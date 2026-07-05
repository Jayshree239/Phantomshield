# Extended Gemini analyst capabilities for scan deep analysis.

from __future__ import annotations

import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import parse_qsl, urlparse

import google.generativeai as genai
import tldextract

from config import settings

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


def _model_candidates() -> List[str]:
    names = [
        settings.GEMINI_MODEL,
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
    ]

    unique: List[str] = []
    seen = set()
    for name in names:
        if name and name not in seen:
            unique.append(name)
            seen.add(name)
    return unique


def _generate_with_fallback(prompt: str, max_output_tokens: int) -> Optional[str]:
    for model_name in _model_candidates():
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": max_output_tokens,
                    "top_p": 0.85,
                },
            )
            response = model.generate_content(prompt)
            text = getattr(response, "text", None)
            if text and text.strip():
                return text.strip()
        except Exception as exc:
            logger.warning("Gemini model '%s' failed: %s", model_name, exc)
            continue
    return None


def _safe_json_extract(text: str) -> Optional[Dict]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    candidate = _extract_json_payload(cleaned)
    if not candidate:
        return None

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _extract_json_payload(text: str) -> Optional[str]:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    for idx in range(start, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return None


def _cleanup_answer(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^(hi|hello|hey|sure|of course|great)[,!\s]+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def generate_threat_narrative(
    url: str,
    threat_score: int,
    threat_level: str,
    attack_types: List[str],
    top_features: List[Dict],
    is_phishing: bool,
) -> Dict:
    """Creates deep threat narrative content for a scan result."""
    top_feature_text = "\n".join(
        [
            f"- {item.get('label', 'Feature')}: {item.get('local_contribution', 0)} contribution, raw={item.get('raw_value', 0)}"
            for item in top_features[:6]
        ]
    )

    prompt = f"""You are a cybersecurity analyst writing a concise threat narrative.

SCAN DATA:
URL: {url}
Threat Score: {threat_score}/100
Threat Level: {str(threat_level).upper()}
Is Phishing: {is_phishing}
Attack Types: {', '.join(attack_types) if attack_types else 'None detected'}

Top Feature Contributors:
{top_feature_text if top_feature_text else '- Not available'}

Return ONLY valid JSON with this exact structure:
{{
  "attacker_profile": "...",
  "industry_context": "...",
  "risk_comparison": "...",
  "one_liner": "...",
  "severity_justification": "...",
  "victim_profile": "...",
  "red_flags_plain": ["...", "...", "..."]
}}

Rules:
- Specific to this scan
- Plain English
- red_flags_plain must contain exactly 3 short points
- No markdown
"""

    content = _generate_with_fallback(prompt, max_output_tokens=1200)
    if not content:
        return _narrative_fallback(threat_score, attack_types)

    data = _safe_json_extract(content)
    if not isinstance(data, dict):
        return _narrative_fallback(threat_score, attack_types)

    required = {
        "attacker_profile",
        "industry_context",
        "risk_comparison",
        "one_liner",
        "severity_justification",
        "victim_profile",
        "red_flags_plain",
    }
    if not required.issubset(data.keys()):
        return _narrative_fallback(threat_score, attack_types)

    red_flags = data.get("red_flags_plain")
    if not isinstance(red_flags, list):
        red_flags = [str(red_flags)] if red_flags else []
    red_flags = [str(item).strip() for item in red_flags if str(item).strip()][:3]
    while len(red_flags) < 3:
        red_flags.append("Review the URL structure carefully before interacting with it.")

    return {
        "attacker_profile": str(data.get("attacker_profile", "")).strip(),
        "industry_context": str(data.get("industry_context", "")).strip(),
        "risk_comparison": str(data.get("risk_comparison", "")).strip(),
        "one_liner": str(data.get("one_liner", "")).strip(),
        "severity_justification": str(data.get("severity_justification", "")).strip(),
        "victim_profile": str(data.get("victim_profile", "")).strip(),
        "red_flags_plain": red_flags,
    }


def _narrative_fallback(threat_score: int, attack_types: List[str]) -> Dict:
    primary_attack = attack_types[0] if attack_types else "unknown"
    return {
        "attacker_profile": "This pattern matches broad phishing campaigns run by credential-focused threat actors.",
        "industry_context": "Similar URL patterns are common in active impersonation attacks across consumer services.",
        "risk_comparison": f"A score of {threat_score}/100 indicates {'above-average' if threat_score >= 60 else 'moderate'} phishing risk.",
        "one_liner": "This URL shows deception patterns designed to capture sensitive user input.",
        "severity_justification": f"The score is driven by multiple suspicious indicators, especially {primary_attack} behavior.",
        "victim_profile": "Targets are typically users who trust familiar-looking domains and urgency prompts.",
        "red_flags_plain": [
            "The URL structure is crafted to look trustworthy.",
            "Language in the URL suggests urgency or verification pressure.",
            "Infrastructure signals indicate possible short-term malicious hosting.",
        ],
    }


def answer_scan_question(
    question: str,
    url: str,
    threat_score: int,
    threat_level: str,
    attack_types: List[str],
    explanation_summary: str,
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    """Answers follow-up user questions while grounding response in scan context."""
    history_lines: List[str] = []
    for turn in (conversation_history or [])[-4:]:
        role = "User" if turn.get("role") == "user" else "PhantomShield"
        content = str(turn.get("content", "")).strip()
        if content:
            history_lines.append(f"{role}: {content}")

    history_text = "\n".join(history_lines)

    prompt = f"""You are PhantomShield, answering questions about one specific scan.

Scan context:
URL: {url}
Threat score: {threat_score}/100
Threat level: {threat_level}
Attack types: {', '.join(attack_types) if attack_types else 'None'}
Summary: {explanation_summary or 'N/A'}

Conversation history:
{history_text if history_text else 'No prior turns.'}

User question: {question}

Rules:
- Focus only on this scan context
- Be direct and specific
- Max 3 concise sentences unless extra detail is necessary
- No markdown
- No greeting or introduction
"""

    content = _generate_with_fallback(prompt, max_output_tokens=700)
    if not content:
        return _qa_fallback(question)

    cleaned = _cleanup_answer(content)
    return cleaned if cleaned else _qa_fallback(question)


def _qa_fallback(question: str) -> str:
    _ = question
    return (
        "I could not generate a detailed follow-up right now. Based on this scan, "
        "the URL contains suspicious indicators that align with phishing behavior. "
        "Use the feature and explanation sections to review the strongest signals."
    )


def analyze_url_anatomy(
    url: str,
    feature_dict: Dict,
    attack_types: List[str],
) -> Dict:
    """Breaks URL into components and labels each component with safety status."""
    suspicious_signals: List[str] = []
    if feature_dict.get("has_homograph_chars"):
        suspicious_signals.append(f"homograph_chars={feature_dict.get('_homograph_chars_found', [])}")
    if feature_dict.get("has_ip_address"):
        suspicious_signals.append("ip_address_used")
    if feature_dict.get("tld_suspicious"):
        suspicious_signals.append(f"suspicious_tld={feature_dict.get('_suffix', '')}")
    if feature_dict.get("domain_contains_brand"):
        suspicious_signals.append("brand_impersonation_pattern")
    if feature_dict.get("has_at_symbol"):
        suspicious_signals.append("at_symbol_present")
    if feature_dict.get("has_urgency_keyword"):
        suspicious_signals.append("urgency_keywords_present")
    if feature_dict.get("has_redirect"):
        suspicious_signals.append("redirect_pattern_present")

    prompt = f"""You are a URL security analyst.

URL: {url}
Detected attack types: {', '.join(attack_types) if attack_types else 'None'}
Suspicious signals: {', '.join(suspicious_signals) if suspicious_signals else 'none'}

Return ONLY valid JSON:
{{
  "components": [
    {{
      "text": "exact substring from URL",
      "type": "scheme|subdomain|domain|tld|path|query|fragment|separator",
      "status": "safe|suspicious|critical|neutral",
      "note": "max 10 words"
    }}
  ],
  "summary": "X of Y components are suspicious"
}}

Rules:
- Use exact URL substrings in text
- Split into meaningful components
- critical = strong phishing indicator
- suspicious = moderate concern
- neutral = not inherently risky
- safe = clearly legitimate component
"""

    content = _generate_with_fallback(prompt, max_output_tokens=1200)
    if not content:
        return _anatomy_fallback(url, feature_dict)

    data = _safe_json_extract(content)
    if not isinstance(data, dict) or not isinstance(data.get("components"), list):
        return _anatomy_fallback(url, feature_dict)

    valid_components: List[Dict] = []
    for component in data.get("components", []):
        if not isinstance(component, dict):
            continue

        text = str(component.get("text", ""))
        if not text:
            continue

        # Keep only components that map to the URL string for reliable highlighting.
        if text not in url and text.replace("://", "") not in url:
            continue

        status = str(component.get("status", "neutral")).lower()
        if status not in {"safe", "suspicious", "critical", "neutral"}:
            status = "neutral"

        valid_components.append(
            {
                "text": text,
                "type": str(component.get("type", "other")).lower(),
                "status": status,
                "note": str(component.get("note", "")).strip(),
            }
        )

    if not valid_components:
        return _anatomy_fallback(url, feature_dict)

    bad_count = sum(1 for item in valid_components if item["status"] in {"suspicious", "critical"})
    total = len(valid_components)
    summary = f"{bad_count} of {total} components {'are' if bad_count != 1 else 'is'} suspicious"

    return {"components": valid_components, "summary": summary}


def _anatomy_fallback(url: str, feature_dict: Dict) -> Dict:
    parsed = urlparse(url)
    extracted = tldextract.extract(url)

    components: List[Dict] = []

    if parsed.scheme:
        components.append(
            {
                "text": f"{parsed.scheme}://",
                "type": "scheme",
                "status": "safe" if parsed.scheme == "https" else "suspicious",
                "note": "Encrypted scheme" if parsed.scheme == "https" else "No TLS scheme",
            }
        )

    if extracted.subdomain:
        components.append(
            {
                "text": f"{extracted.subdomain}.",
                "type": "subdomain",
                "status": "suspicious" if int(feature_dict.get("subdomain_count", 0)) > 1 else "neutral",
                "note": "Nested subdomain structure",
            }
        )

    domain_status = "critical" if feature_dict.get("domain_contains_brand") or feature_dict.get("has_homograph_chars") else "neutral"
    components.append(
        {
            "text": extracted.domain or parsed.hostname or "",
            "type": "domain",
            "status": domain_status,
            "note": "Potential impersonation" if domain_status == "critical" else "Domain label",
        }
    )

    if extracted.suffix:
        tld_status = "critical" if feature_dict.get("tld_suspicious") else "safe"
        components.append(
            {
                "text": f".{extracted.suffix}",
                "type": "tld",
                "status": tld_status,
                "note": "Suspicious TLD" if tld_status == "critical" else "Common TLD",
            }
        )

    if parsed.path and parsed.path != "/":
        components.append(
            {
                "text": parsed.path,
                "type": "path",
                "status": "suspicious" if feature_dict.get("has_urgency_keyword") else "neutral",
                "note": "Path includes suspicious terms" if feature_dict.get("has_urgency_keyword") else "Path segment",
            }
        )

    if parsed.query:
        query_parts = [f"{k}={v}" if v else k for k, v in parse_qsl(parsed.query)]
        for part in query_parts or [parsed.query]:
            components.append(
                {
                    "text": part,
                    "type": "query",
                    "status": "suspicious" if feature_dict.get("has_redirect") else "neutral",
                    "note": "Redirect-like query" if feature_dict.get("has_redirect") else "Query parameter",
                }
            )

    bad_count = sum(1 for item in components if item["status"] in {"suspicious", "critical"})
    total = len(components)

    return {
        "components": components,
        "summary": f"{bad_count} of {total} components {'are' if bad_count != 1 else 'is'} suspicious",
    }
