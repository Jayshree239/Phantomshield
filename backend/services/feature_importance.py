# Computes per-feature contribution to a scan threat score.

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parents[1] / "ml" / "models"

# Keep this order aligned with URLFeatureExtractor._get_feature_names().
FEATURE_ORDER = [
    "domain_length",
    "subdomain_count",
    "has_ip_address",
    "tld_suspicious",
    "domain_contains_brand",
    "domain_age_score",
    "url_length",
    "has_at_symbol",
    "has_double_slash",
    "special_char_count",
    "digit_ratio",
    "hyphen_count",
    "dot_count",
    "query_param_count",
    "has_homograph_chars",
    "homograph_count",
    "has_unicode",
    "has_https",
    "ssl_valid",
    "ssl_age_score",
    "has_login_keyword",
    "has_secure_keyword",
    "has_verify_keyword",
    "has_update_keyword",
    "has_urgency_keyword",
    "path_depth",
    "has_redirect",
    "subdomain_depth",
]

FEATURE_META = {
    "domain_length": {
        "label": "Domain Name Length",
        "group": "Domain",
        "icon": "ruler",
        "why": "Very long domain names are unusual for legitimate sites and are often generated randomly for phishing.",
    },
    "subdomain_count": {
        "label": "Subdomain Count",
        "group": "Domain",
        "icon": "layers",
        "why": "Multiple nested subdomains can make a fake URL look familiar at first glance.",
    },
    "has_ip_address": {
        "label": "IP Address Used",
        "group": "Domain",
        "icon": "server",
        "why": "Using a raw IP address instead of a domain can hide real ownership and intent.",
    },
    "tld_suspicious": {
        "label": "Suspicious TLD",
        "group": "Domain",
        "icon": "flag",
        "why": "Free or uncommon TLDs are overrepresented in phishing infrastructure.",
    },
    "domain_contains_brand": {
        "label": "Brand Name in Domain",
        "group": "Domain",
        "icon": "tag",
        "why": "Placing a known brand in a different domain is a common impersonation pattern.",
    },
    "domain_age_score": {
        "label": "Domain Age",
        "group": "Domain",
        "icon": "calendar",
        "why": "Newly registered domains are frequently used in short-lived phishing campaigns.",
    },
    "url_length": {
        "label": "URL Total Length",
        "group": "Structure",
        "icon": "maximize",
        "why": "Long URLs can hide malicious path segments and tracking or redirect parameters.",
    },
    "has_at_symbol": {
        "label": "At Symbol Present",
        "group": "Structure",
        "icon": "at-sign",
        "why": "The at symbol can be abused to disguise the destination host shown to users.",
    },
    "has_double_slash": {
        "label": "Double Slash in Path",
        "group": "Structure",
        "icon": "code",
        "why": "Unexpected path syntax can indicate obfuscation or redirect behavior.",
    },
    "special_char_count": {
        "label": "Special Character Count",
        "group": "Structure",
        "icon": "hash",
        "why": "Heavy symbol usage is often used to make malicious URLs harder to parse visually.",
    },
    "digit_ratio": {
        "label": "Digit Ratio",
        "group": "Structure",
        "icon": "percent",
        "why": "Digit-heavy URLs are often algorithmically generated and less human-readable.",
    },
    "hyphen_count": {
        "label": "Hyphen Count",
        "group": "Structure",
        "icon": "minus",
        "why": "Many phishing domains use multiple hyphens to mimic legitimate naming patterns.",
    },
    "dot_count": {
        "label": "Dot Count",
        "group": "Structure",
        "icon": "more-horizontal",
        "why": "Excessive dot usage often correlates with deep subdomain nesting.",
    },
    "query_param_count": {
        "label": "Query Parameters",
        "group": "Structure",
        "icon": "list",
        "why": "High parameter count can indicate redirect chains or token harvesting flows.",
    },
    "has_homograph_chars": {
        "label": "Look-Alike Characters",
        "group": "Homograph",
        "icon": "eye",
        "why": "Character substitutions can make a fake domain appear identical to a trusted one.",
    },
    "homograph_count": {
        "label": "Homograph Character Count",
        "group": "Homograph",
        "icon": "copy",
        "why": "A higher count of substitutions indicates a stronger visual deception attempt.",
    },
    "has_unicode": {
        "label": "Unicode or Punycode",
        "group": "Homograph",
        "icon": "globe",
        "why": "Unicode domain tricks can render as familiar brand-like text while being malicious.",
    },
    "has_https": {
        "label": "HTTPS Present",
        "group": "SSL",
        "icon": "lock",
        "why": "HTTPS is expected, but phishing pages can still use valid certificates.",
    },
    "ssl_valid": {
        "label": "SSL Validity",
        "group": "SSL",
        "icon": "shield",
        "why": "Invalid certificates increase risk and suggest weak or fake hosting setup.",
    },
    "ssl_age_score": {
        "label": "SSL Certificate Age",
        "group": "SSL",
        "icon": "clock",
        "why": "Very recent certificates can indicate newly spun-up malicious infrastructure.",
    },
    "has_login_keyword": {
        "label": "Login Keyword",
        "group": "Keywords",
        "icon": "key",
        "why": "Login-related words are often inserted to trigger trust and urgent action.",
    },
    "has_secure_keyword": {
        "label": "Security Keyword",
        "group": "Keywords",
        "icon": "shield-check",
        "why": "Words like secure or ssl are commonly used to fake legitimacy.",
    },
    "has_verify_keyword": {
        "label": "Verification Keyword",
        "group": "Keywords",
        "icon": "check-circle",
        "why": "Verification language is a common lure for credential capture.",
    },
    "has_update_keyword": {
        "label": "Update Keyword",
        "group": "Keywords",
        "icon": "refresh-cw",
        "why": "Update or restore prompts mimic account maintenance scams.",
    },
    "has_urgency_keyword": {
        "label": "Urgency Keyword",
        "group": "Keywords",
        "icon": "alert-triangle",
        "why": "Urgency wording is a social engineering pressure tactic.",
    },
    "path_depth": {
        "label": "URL Path Depth",
        "group": "Path",
        "icon": "folder",
        "why": "Deep path nesting can hide suspicious segments and fake workflows.",
    },
    "has_redirect": {
        "label": "Redirect Pattern",
        "group": "Path",
        "icon": "external-link",
        "why": "Redirect markers can chain users through multiple destinations.",
    },
    "subdomain_depth": {
        "label": "Subdomain Depth",
        "group": "Path",
        "icon": "git-branch",
        "why": "Very deep subdomains can exploit truncated URL bar visibility.",
    },
}


class FeatureImportanceService:
    """Interpretability helpers based on trained model importances."""

    _rf_model = None
    _xgb_model = None
    _scaler = None
    _loaded = False

    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._loaded:
            return

        try:
            cls._rf_model = joblib.load(MODEL_DIR / "random_forest.pkl")
            cls._xgb_model = joblib.load(MODEL_DIR / "xgboost_model.pkl")
            cls._scaler = joblib.load(MODEL_DIR / "scaler.pkl")
            cls._loaded = True
        except Exception as exc:
            logger.error("Feature importance model load error: %s", exc)

    @classmethod
    def get_global_importances(cls) -> List[Dict]:
        """Returns normalized global importances from RF+XGB weighted ensemble."""
        cls._ensure_loaded()
        if cls._rf_model is None or cls._xgb_model is None:
            return []

        rf_imp = np.array(cls._rf_model.feature_importances_, dtype=float)
        xgb_imp = np.array(cls._xgb_model.feature_importances_, dtype=float)

        n = min(len(FEATURE_ORDER), len(rf_imp), len(xgb_imp))
        if n == 0:
            return []

        ensemble_imp = (rf_imp[:n] * 0.45) + (xgb_imp[:n] * 0.55)
        max_imp = float(np.max(ensemble_imp)) if np.max(ensemble_imp) > 0 else 1.0
        normalized = np.round((ensemble_imp / max_imp) * 100.0, 1)

        results: List[Dict] = []
        for idx, name in enumerate(FEATURE_ORDER[:n]):
            meta = FEATURE_META.get(name, {})
            results.append(
                {
                    "feature": name,
                    "label": meta.get("label", name),
                    "group": meta.get("group", "Other"),
                    "icon": meta.get("icon", "circle"),
                    "why": meta.get("why", ""),
                    "importance": float(normalized[idx]),
                    "rf_importance": float(rf_imp[idx] * 100.0),
                    "xgb_importance": float(xgb_imp[idx] * 100.0),
                }
            )

        results.sort(key=lambda item: item["importance"], reverse=True)
        return results

    @classmethod
    def get_local_contribution(
        cls,
        feature_dict: Dict,
        feature_vector: List[float],
        threat_score: int,
    ) -> List[Dict]:
        """Returns per-scan contribution values for each feature."""
        _ = threat_score  # Reserved for future calibration.

        cls._ensure_loaded()

        n = min(len(FEATURE_ORDER), len(feature_vector))
        if n == 0:
            return []

        global_imp = cls.get_global_importances()
        global_map = {item["feature"]: item["importance"] for item in global_imp}

        values = np.array(feature_vector[:n], dtype=float)

        # Convert transformed values into 0..1 activation scores for local impact.
        try:
            scaled = np.array(cls._scaler.transform([values])[0], dtype=float)
            activation = 1.0 / (1.0 + np.exp(-scaled))
        except Exception:
            max_abs = float(np.max(np.abs(values))) if np.max(np.abs(values)) > 0 else 1.0
            activation = np.clip(np.abs(values) / max_abs, 0.0, 1.0)

        contributions: List[Dict] = []
        for idx, name in enumerate(FEATURE_ORDER[:n]):
            meta = FEATURE_META.get(name, {})
            g_imp = float(global_map.get(name, 0.0))
            local = round(g_imp * float(activation[idx]), 2)

            contributions.append(
                {
                    "feature": name,
                    "label": meta.get("label", name),
                    "group": meta.get("group", "Other"),
                    "icon": meta.get("icon", "circle"),
                    "why": meta.get("why", ""),
                    "global_importance": g_imp,
                    "local_contribution": local,
                    "raw_value": feature_dict.get(name, 0),
                    "normalized_value": round(float(activation[idx]), 3),
                    "is_suspicious": local > 5.0,
                }
            )

        contributions.sort(key=lambda item: item["local_contribution"], reverse=True)
        return contributions

    @classmethod
    def get_top_contributors(
        cls,
        feature_dict: Dict,
        feature_vector: List[float],
        threat_score: int,
        top_n: int = 8,
    ) -> Dict:
        """Returns top contributing features and category summary."""
        all_contributions = cls.get_local_contribution(
            feature_dict=feature_dict,
            feature_vector=feature_vector,
            threat_score=threat_score,
        )

        top = all_contributions[:top_n]

        group_totals: Dict[str, float] = {}
        for item in all_contributions:
            group = item["group"]
            group_totals[group] = round(group_totals.get(group, 0.0) + item["local_contribution"], 2)

        primary_group = max(group_totals, key=group_totals.get) if group_totals else "Unknown"

        return {
            "top_contributors": top,
            "all_contributions": all_contributions,
            "group_totals": group_totals,
            "primary_group": primary_group,
            "suspicious_count": sum(1 for item in all_contributions if item["is_suspicious"]),
        }
