# d:/SPECTER/phantomshield/backend/ml/feature_extractor.py
# Extracts 28 features from URLs for ML classification.

import logging
import socket
import ssl
from datetime import datetime
from typing import List, Tuple
from urllib.parse import parse_qs, urlparse

import tldextract

tld_extractor = tldextract.TLDExtract(suffix_list_urls=None)
from utils.domain_utils import get_domain_age_days

logger = logging.getLogger(__name__)

# Common character substitutions used in homograph attacks.
HOMOGRAPH_MAP = {
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",
    "с": "c",
    "0": "o",
    "1": "l",
    "3": "e",
    "4": "a",
    "5": "s",
    "@": "a",
    "$": "s",
    "!": "i",
    "vv": "w",
    "rn": "m",
    "ı": "i",
    "ο": "o",
    "ρ": "p",
    "α": "a",
    "ν": "v",
}

SUSPICIOUS_TLDS = {
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".xyz",
    ".top",
    ".click",
    ".download",
    ".loan",
    ".work",
    ".party",
    ".win",
    ".club",
    ".online",
    ".site",
    ".tech",
}

TRUSTED_BRANDS = {
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
    "dropbox",
    "github",
    "steam",
    "ebay",
    "hdfc",
    "icici",
    "sbi",
    "axis",
    "kotak",
    "paytm",
    "phonepe",
    "gpay",
    "razorpay",
    "airtel",
}

LOGIN_KEYWORDS = ["login", "signin", "sign-in", "logon", "auth", "authenticate"]
SECURE_KEYWORDS = ["secure", "security", "ssl", "safe", "protected"]
VERIFY_KEYWORDS = ["verify", "verification", "confirm", "validate", "activate"]
UPDATE_KEYWORDS = ["update", "upgrade", "renew", "reactivate", "restore"]
URGENCY_KEYWORDS = ["urgent", "immediately", "expire", "suspend", "alert", "warning", "critical"]


class URLFeatureExtractor:
    """Extracts 28 numerical/boolean features from a URL."""

    def __init__(self):
        self.features_names = self._get_feature_names()

    def extract(self, url: str) -> Tuple[List[float], dict]:
        """
        Returns: (feature_vector, feature_dict)
        feature_vector: list of 28 values for ML model
        feature_dict:   human-readable dict for explanation
        """
        try:
            normalized_url = self._normalize_url(url)
            parsed = urlparse(normalized_url)
            extracted = tld_extractor(normalized_url)
            domain = extracted.domain or ""
            suffix = extracted.suffix or ""
            subdomain = extracted.subdomain or ""
            full_domain = f"{domain}.{suffix}" if suffix else domain

            feature_dict: dict[str, float | int | str | list[str]] = {}

            # GROUP 1: DOMAIN FEATURES (6)
            feature_dict["domain_length"] = len(domain)
            feature_dict["subdomain_count"] = len(subdomain.split(".")) if subdomain else 0
            feature_dict["has_ip_address"] = int(self._is_ip_address(parsed.netloc))
            feature_dict["tld_suspicious"] = int(f".{suffix}" in SUSPICIOUS_TLDS if suffix else 0)
            feature_dict["domain_contains_brand"] = int(self._check_brand_impersonation(domain))
            feature_dict["domain_age_score"] = 0.5

            # GROUP 2: URL STRUCTURE FEATURES (8)
            feature_dict["url_length"] = min(len(normalized_url), 200)
            feature_dict["has_at_symbol"] = int("@" in normalized_url)
            feature_dict["has_double_slash"] = int("//" in parsed.path)
            feature_dict["special_char_count"] = self._count_special_chars(normalized_url)
            feature_dict["digit_ratio"] = self._digit_ratio(normalized_url)
            feature_dict["hyphen_count"] = normalized_url.count("-")
            feature_dict["dot_count"] = normalized_url.count(".")
            feature_dict["query_param_count"] = len(parse_qs(parsed.query))

            # GROUP 3: HOMOGRAPH FEATURES (3)
            homograph_chars = self._find_homograph_chars(normalized_url)
            feature_dict["has_homograph_chars"] = int(len(homograph_chars) > 0)
            feature_dict["homograph_count"] = len(homograph_chars)
            feature_dict["has_unicode"] = int(self._has_unicode(normalized_url))

            # GROUP 4: SSL FEATURES (3)
            ssl_info = self._check_ssl(parsed.netloc)
            feature_dict["has_https"] = int(parsed.scheme == "https")
            feature_dict["ssl_valid"] = int(ssl_info.get("valid", False))
            feature_dict["ssl_age_score"] = float(ssl_info.get("age_score", 0.0))

            # GROUP 5: KEYWORD FEATURES (5)
            url_lower = normalized_url.lower()
            feature_dict["has_login_keyword"] = int(any(kw in url_lower for kw in LOGIN_KEYWORDS))
            feature_dict["has_secure_keyword"] = int(any(kw in url_lower for kw in SECURE_KEYWORDS))
            feature_dict["has_verify_keyword"] = int(any(kw in url_lower for kw in VERIFY_KEYWORDS))
            feature_dict["has_update_keyword"] = int(any(kw in url_lower for kw in UPDATE_KEYWORDS))
            feature_dict["has_urgency_keyword"] = int(any(kw in url_lower for kw in URGENCY_KEYWORDS))

            # GROUP 6: REDIRECT/PATH FEATURES (3)
            feature_dict["path_depth"] = len([part for part in parsed.path.split("/") if part])
            feature_dict["has_redirect"] = int("redirect" in url_lower or "url=" in url_lower)
            feature_dict["subdomain_depth"] = len(subdomain.split(".")) if subdomain else 0

            feature_vector = [float(feature_dict[name]) for name in self.features_names]

            # Metadata used by explainer (not in model vector)
            feature_dict["_homograph_chars_found"] = homograph_chars
            feature_dict["_domain"] = domain
            feature_dict["_suffix"] = suffix
            feature_dict["_subdomain"] = subdomain
            feature_dict["_scheme"] = parsed.scheme

            return feature_vector, feature_dict

        except Exception as exc:
            logger.error("Feature extraction failed for %s: %s", url, exc)
            return [0.0] * 28, {}

    def _normalize_url(self, url: str) -> str:
        cleaned = (url or "").strip()
        if not cleaned:
            return ""
        if not cleaned.startswith(("http://", "https://")):
            return f"http://{cleaned}"
        return cleaned

    def _get_feature_names(self) -> List[str]:
        return [
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

    def _is_ip_address(self, netloc: str) -> bool:
        try:
            host = netloc.split(":")[0]
            socket.inet_aton(host)
            return True
        except (socket.error, OSError):
            return False

    def _check_brand_impersonation(self, domain: str) -> bool:
        domain_lower = (domain or "").lower()
        for brand in TRUSTED_BRANDS:
            if brand in domain_lower and domain_lower != brand:
                return True
            normalized = domain_lower
            for fake, real in HOMOGRAPH_MAP.items():
                normalized = normalized.replace(fake, real)
            if brand in normalized and normalized != brand:
                return True
        return False

    def _get_domain_age_score(self, domain: str) -> float:
        if not domain:
            return 0.5

        age_days = get_domain_age_days(domain)
        if age_days is not None:
            if age_days < 30:
                return 1.0
            if age_days < 90:
                return 0.8
            if age_days < 180:
                return 0.6
            if age_days < 365:
                return 0.4
            if age_days < 730:
                return 0.2
            return 0.0

        return 0.5

    def _count_special_chars(self, url: str) -> int:
        special = set("!@#$%^&*(){}[]|\\<>?=+~`")
        return sum(1 for char in url if char in special)

    def _digit_ratio(self, url: str) -> float:
        if not url:
            return 0.0
        return sum(1 for char in url if char.isdigit()) / len(url)

    def _find_homograph_chars(self, url: str) -> List[str]:
        found = []
        for fake_char in HOMOGRAPH_MAP:
            if fake_char in url:
                found.append(fake_char)
        return list(set(found))

    def _has_unicode(self, url: str) -> bool:
        try:
            url.encode("ascii")
            return False
        except UnicodeEncodeError:
            return True

    def _check_ssl(self, netloc: str) -> dict:
        try:
            host = netloc.split(":")[0]
            if not host:
                return {"valid": False, "age_score": 0.5}

            context = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=1.5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as secure_sock:
                    cert = secure_sock.getpeercert()
                    not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
                    cert_age_days = (datetime.now() - not_before).days
                    age_score = 1.0 if cert_age_days < 30 else 0.0
                    return {"valid": True, "age_score": age_score}
        except ssl.SSLError:
            return {"valid": False, "age_score": 0.5}
        except Exception:
            return {"valid": False, "age_score": 0.5}
