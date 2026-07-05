# d:/SPECTER/phantomshield/backend/services/explainer_service.py
# Uses Gemini to generate user-friendly phishing explanations.

import json
import logging
import re
from typing import Optional
from urllib.parse import urlparse

import google.generativeai as genai

from config import settings

logger = logging.getLogger(__name__)

model: Optional[genai.GenerativeModel] = None
_active_model_name: Optional[str] = None

_VALID_ATTACK_TYPES = {
    "homograph",
    "typosquatting",
    "subdomain_attack",
    "brand_impersonation",
    "fake_ssl",
    "urgency_manipulation",
    "credential_harvesting",
    "malware_distribution",
    "spear_phishing",
    "unknown",
}
_VALID_SEVERITY = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
_KNOWN_BRANDS = [
    "paypal",
    "google",
    "facebook",
    "microsoft",
    "apple",
    "amazon",
    "netflix",
    "instagram",
    "whatsapp",
    "twitter",
    "linkedin",
    "hdfc",
    "icici",
    "sbi",
    "paytm",
    "phonepe",
]


def _normalize_model_name(name: str) -> str:
    return name.removeprefix("models/").strip()


def _model_candidates() -> list[str]:
    candidates: list[str] = []

    if _active_model_name:
        candidates.append(_active_model_name)

    configured = _normalize_model_name(settings.GEMINI_MODEL)
    if configured:
        candidates.append(configured)

    # Fallbacks kept in stable->newest order for availability and continuity.
    candidates.extend(
        [
            "gemini-flash-latest",
            "gemini-2.5-flash",
            "gemini-2.0-flash-lite",
        ]
    )

    unique: list[str] = []
    for name in candidates:
        if name and name not in unique:
            unique.append(name)
    return unique


if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


def _normalize_attack_type(value: object) -> str:
    text = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text if text in _VALID_ATTACK_TYPES else "unknown"


def _normalize_severity(value: object) -> str:
    text = str(value or "").strip().upper()
    return text if text in _VALID_SEVERITY else "MEDIUM"


def _sanitize_explanation_text(text: str) -> str:
    cleaned = (text or "").strip()

    # Remove common greeting/self-introduction starts if model ignores style rules.
    cleaned = re.sub(
        r"^(hello|hi|hey)\b[^\n.!?]*[.!?]\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^(i\s*(am|'m)\s*from\b[^\n.!?]*[.!?]\s*)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    return cleaned.strip() or (text or "").strip()


def _extract_json_payload(text: str) -> Optional[dict]:
    raw = (text or "").strip()
    if not raw:
        return None

    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        raw = fenced.group(1).strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        return None

    try:
        payload = json.loads(raw[start : end + 1])
    except Exception:
        return None

    return payload if isinstance(payload, dict) else None


def _infer_safe_alternative(url: str, feature_dict: dict) -> Optional[str]:
    if feature_dict.get("has_ip_address"):
        return None

    host = (urlparse(url).hostname or "").lower()
    for brand in _KNOWN_BRANDS:
        if brand in host:
            return f"https://www.{brand}.com"
    return None


def _heuristic_suspicious_elements(feature_dict: dict) -> list[dict]:
    elements: list[dict] = []

    if feature_dict.get("has_homograph_chars"):
        chars = feature_dict.get("_homograph_chars_found", [])
        elements.append(
            {
                "element": ", ".join(chars) if chars else "look-alike characters",
                "reason": "Look-alike characters can imitate trusted domains.",
                "severity": "HIGH",
                "attack_type": "homograph",
                "position": "domain",
            }
        )

    if feature_dict.get("domain_contains_brand"):
        elements.append(
            {
                "element": "brand-like domain text",
                "reason": "The domain appears to impersonate a known brand.",
                "severity": "CRITICAL",
                "attack_type": "brand_impersonation",
                "position": "domain",
            }
        )

    if feature_dict.get("has_ip_address"):
        elements.append(
            {
                "element": "raw IP address",
                "reason": "IP-only URLs hide identity and are often used in phishing.",
                "severity": "HIGH",
                "attack_type": "credential_harvesting",
                "position": "host",
            }
        )

    if feature_dict.get("has_at_symbol"):
        elements.append(
            {
                "element": "@",
                "reason": "@ can hide the true destination in some URL patterns.",
                "severity": "HIGH",
                "attack_type": "typosquatting",
                "position": "url",
            }
        )

    if feature_dict.get("tld_suspicious"):
        elements.append(
            {
                "element": "suspicious top-level domain",
                "reason": "The TLD is frequently observed in abuse campaigns.",
                "severity": "MEDIUM",
                "attack_type": "unknown",
                "position": "domain",
            }
        )

    if feature_dict.get("has_urgency_keyword"):
        elements.append(
            {
                "element": "urgency language",
                "reason": "Urgency words are used to force impulsive user actions.",
                "severity": "MEDIUM",
                "attack_type": "urgency_manipulation",
                "position": "path_or_query",
            }
        )

    return elements[:6]


def _default_confidence_rationale(threat_score: int, feature_dict: dict) -> str:
    signals = []
    if feature_dict.get("domain_contains_brand"):
        signals.append("brand impersonation signal")
    if feature_dict.get("has_homograph_chars"):
        signals.append("homograph character signal")
    if feature_dict.get("has_ip_address"):
        signals.append("IP-host signal")
    if feature_dict.get("has_urgency_keyword"):
        signals.append("urgency-language signal")
    if feature_dict.get("tld_suspicious"):
        signals.append("suspicious-TLD signal")

    if not signals:
        return f"Confidence is primarily based on aggregate feature scoring at {threat_score}/100."

    preview = ", ".join(signals[:3])
    return (
        f"Confidence is supported by {preview}. "
        f"Combined indicator strength aligns with a threat score of {threat_score}/100."
    )


def _default_immediate_actions(threat_score: int) -> list[str]:
    if threat_score >= 80:
        return [
            "Do not open the URL again.",
            "Block the domain on gateway or DNS filters.",
            "Notify security team immediately with screenshot and URL.",
            "Reset credentials if any data was entered.",
        ]
    if threat_score >= 60:
        return [
            "Avoid logging in through this link.",
            "Verify account alerts directly from the official app.",
            "Report this URL to your security channel.",
        ]
    return [
        "Proceed with caution and verify destination manually.",
        "Type official domain directly in browser instead of clicking links.",
    ]


def _default_attacker_thinking(feature_dict: dict) -> str:
    if feature_dict.get("has_urgency_keyword"):
        return "The attacker is trying to create urgency so the victim acts before validating the link."
    if feature_dict.get("domain_contains_brand") or feature_dict.get("has_homograph_chars"):
        return "The attacker is banking on visual trust by mimicking a known brand and domain pattern."
    return "The attacker is exploiting trust signals and URL complexity to reduce careful inspection."


def build_explanation_prompt(
    url: str,
    feature_dict: dict,
    threat_score: int,
    threat_level: str,
) -> str:
    suspicious_features = []

    if feature_dict.get("has_homograph_chars"):
        chars = feature_dict.get("_homograph_chars_found", [])
        suspicious_features.append(
            "Contains homograph characters: "
            f"{', '.join(chars)} (characters that look like letters but are different)"
        )

    if feature_dict.get("domain_contains_brand"):
        suspicious_features.append(
            "The domain tries to impersonate a well-known brand "
            "(contains brand name but is a different domain)"
        )

    if feature_dict.get("domain_age_score", 0) > 0.6:
        suspicious_features.append(
            "The domain was registered very recently (less than 90 days ago), "
            "a strong phishing indicator"
        )

    if not feature_dict.get("ssl_valid", True):
        suspicious_features.append("The SSL certificate is invalid or missing.")

    if feature_dict.get("has_ip_address"):
        suspicious_features.append("The URL uses an IP address instead of a domain name.")

    if feature_dict.get("has_at_symbol"):
        suspicious_features.append("Contains '@' symbol in URL, which can hide the real destination.")

    if feature_dict.get("has_urgency_keyword"):
        suspicious_features.append("Contains urgency keywords designed to trigger panic-click behavior.")

    if feature_dict.get("tld_suspicious"):
        suspicious_features.append("Uses a suspicious top-level domain commonly abused for phishing.")

    if feature_dict.get("has_verify_keyword") and feature_dict.get("has_secure_keyword"):
        suspicious_features.append(
            "Combines 'verify' and 'secure' keywords, a common social engineering pattern."
        )

    features_text = "\n".join(f"- {item}" for item in suspicious_features)
    allowed_types = ", ".join(sorted(_VALID_ATTACK_TYPES))

    return f"""You are a cybersecurity expert explaining a phishing attack to a regular user.

STYLE RULES:
- Do NOT greet the user.
- Do NOT introduce yourself.
- Do NOT mention team or organization names.
- Start immediately with the threat explanation.
- Use plain language for non-technical users.

SCAN RESULT:
URL: {url}
Threat Score: {threat_score}/100
Threat Level: {threat_level.upper()}

DETECTED SUSPICIOUS INDICATORS:
{features_text if features_text else '- General suspicious patterns detected'}

OUTPUT FORMAT:
Return ONLY one JSON object (no markdown, no code fences) with this schema:
{{
  "summary": "one concise sentence",
  "attack_technique": "short label",
  "how_attacker_thinks": "1-2 sentence psychology explanation",
  "ai_explanation": "detailed explanation up to 220 words",
  "confidence_rationale": "why this score is reliable",
  "immediate_actions": ["action 1", "action 2", "action 3"],
  "safe_alternative": "https://official-site.example" or null,
  "suspicious_elements": [
    {{
      "element": "token/value",
      "reason": "why suspicious",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "attack_type": "one of: {allowed_types}",
      "position": "domain|path|query|host|url|path_or_query" or null
    }}
  ]
}}

Limit suspicious_elements to 6 items max.
"""


def _build_fallback_bundle(
    url: str,
    feature_dict: dict,
    threat_score: int,
    threat_level: str,
) -> dict:
    suspicious = _heuristic_suspicious_elements(feature_dict)
    first_type = suspicious[0]["attack_type"] if suspicious else "unknown"

    return {
        "summary": f"Threat score: {threat_score}/100 ({str(threat_level).upper()}).",
        "suspicious_elements": suspicious,
        "attack_technique": first_type.replace("_", " "),
        "how_attacker_thinks": _default_attacker_thinking(feature_dict),
        "safe_alternative": _infer_safe_alternative(url, feature_dict),
        "ai_explanation": _generate_fallback_explanation(feature_dict, threat_score),
        "confidence_rationale": _default_confidence_rationale(threat_score, feature_dict),
        "immediate_actions": _default_immediate_actions(threat_score),
    }


def _parse_bundle_response(
    text: str,
    url: str,
    feature_dict: dict,
    threat_score: int,
    threat_level: str,
) -> Optional[dict]:
    payload = _extract_json_payload(text)
    if payload is None:
        return None

    suspicious = []
    raw_elements = payload.get("suspicious_elements")
    if isinstance(raw_elements, list):
        for item in raw_elements[:8]:
            if not isinstance(item, dict):
                continue

            element = str(item.get("element") or "").strip()
            reason = str(item.get("reason") or "").strip()
            if not element or not reason:
                continue

            suspicious.append(
                {
                    "element": element,
                    "reason": reason,
                    "severity": _normalize_severity(item.get("severity")),
                    "attack_type": _normalize_attack_type(item.get("attack_type")),
                    "position": str(item.get("position") or "").strip() or None,
                }
            )

    if not suspicious:
        suspicious = _heuristic_suspicious_elements(feature_dict)

    summary = str(payload.get("summary") or "").strip()
    attack_technique = str(payload.get("attack_technique") or "").strip()
    how_attacker_thinks = str(payload.get("how_attacker_thinks") or "").strip()
    ai_explanation = _sanitize_explanation_text(str(payload.get("ai_explanation") or ""))
    confidence_rationale = str(payload.get("confidence_rationale") or "").strip()

    safe_alt_raw = payload.get("safe_alternative")
    safe_alternative = str(safe_alt_raw).strip() if isinstance(safe_alt_raw, str) else None

    immediate_actions: list[str] = []
    raw_actions = payload.get("immediate_actions")
    if isinstance(raw_actions, list):
        for action in raw_actions:
            text_action = str(action or "").strip()
            if text_action:
                immediate_actions.append(text_action)
    immediate_actions = immediate_actions[:6]

    if not summary:
        summary = f"Threat score: {threat_score}/100 ({str(threat_level).upper()})."
    if not attack_technique:
        attack_technique = suspicious[0]["attack_type"].replace("_", " ") if suspicious else "unknown"
    if not how_attacker_thinks:
        how_attacker_thinks = _default_attacker_thinking(feature_dict)
    if not ai_explanation:
        ai_explanation = _generate_fallback_explanation(feature_dict, threat_score)
    if not confidence_rationale:
        confidence_rationale = _default_confidence_rationale(threat_score, feature_dict)
    if not immediate_actions:
        immediate_actions = _default_immediate_actions(threat_score)
    if not safe_alternative:
        safe_alternative = _infer_safe_alternative(url, feature_dict)

    return {
        "summary": summary,
        "suspicious_elements": suspicious,
        "attack_technique": attack_technique,
        "how_attacker_thinks": how_attacker_thinks,
        "safe_alternative": safe_alternative,
        "ai_explanation": ai_explanation,
        "confidence_rationale": confidence_rationale,
        "immediate_actions": immediate_actions,
    }


async def generate_explanation_bundle(
    url: str,
    feature_dict: dict,
    threat_score: int,
    threat_level: str,
) -> dict:
    global model, _active_model_name

    fallback_bundle = _build_fallback_bundle(url, feature_dict, threat_score, threat_level)
    if not settings.GEMINI_API_KEY:
        return fallback_bundle

    prompt = build_explanation_prompt(url, feature_dict, threat_score, threat_level)
    last_exc: Optional[Exception] = None

    for model_name in _model_candidates():
        try:
            if model is None or _active_model_name != model_name:
                model = genai.GenerativeModel(model_name)
                _active_model_name = model_name

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 700,
                    "top_p": 0.9,
                },
            )

            text = response.text or ""
            parsed = _parse_bundle_response(text, url, feature_dict, threat_score, threat_level)
            if parsed is not None:
                return parsed

            cleaned = _sanitize_explanation_text(text)
            if cleaned:
                fallback_bundle["ai_explanation"] = cleaned
                return fallback_bundle
        except Exception as exc:
            last_exc = exc
            logger.warning("Gemini model '%s' failed: %s", model_name, exc)
            model = None
            _active_model_name = None

    if last_exc is not None:
        logger.warning("Gemini explanation failed on all models. Using fallback.")
    return fallback_bundle


async def generate_explanation(
    url: str,
    feature_dict: dict,
    threat_score: int,
    threat_level: str,
) -> str:
    bundle = await generate_explanation_bundle(url, feature_dict, threat_score, threat_level)
    return bundle.get("ai_explanation") or _generate_fallback_explanation(feature_dict, threat_score)


def _generate_fallback_explanation(feature_dict: dict, threat_score: int) -> str:
    parts = []

    if feature_dict.get("has_homograph_chars"):
        parts.append("This URL uses look-alike characters to imitate a trusted website.")

    if feature_dict.get("domain_contains_brand"):
        parts.append("The domain includes a brand-like name but is not the real brand domain.")

    if feature_dict.get("domain_age_score", 0) > 0.6:
        parts.append("The website appears newly registered, which is common in phishing campaigns.")

    if feature_dict.get("has_urgency_keyword"):
        parts.append("Urgency wording is used to pressure fast decisions without verification.")

    if not parts:
        parts.append("Multiple suspicious patterns were detected that are often linked to phishing.")

    parts.append(f"Threat Score: {threat_score}/100. Avoid submitting personal data on this site.")
    return " ".join(parts)
