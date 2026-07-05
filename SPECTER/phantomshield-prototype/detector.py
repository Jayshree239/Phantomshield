# specter-prototype/detector.py
# SPECTER - AI-Based Phishing Detection Prototype
# Core detection engine for Round 2 demo.
#
# Run: python detector.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

from datetime import datetime
import hashlib
import re
import time
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ------------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------------

app = FastAPI(
    title="SPECTER API",
    description="AI-Based Phishing Detection - Round 2 Prototype",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# FEATURE 1: REAL-TIME MONITORING
# ------------------------------------------------------------

scan_history = []
alert_queue = []
session_stats = {
    "total_scans": 0,
    "phishing_caught": 0,
    "safe_confirmed": 0,
    "start_time": datetime.now().isoformat(),
}

# ------------------------------------------------------------
# FEATURE 4: FAULT CLASSIFICATION TAXONOMY
# ------------------------------------------------------------

ATTACK_TYPES = {
    "HOMOGRAPH": "Character substitution attack (o->0, l->1)",
    "TYPOSQUATTING": "Domain typo impersonation",
    "BRAND_IMPERSONATION": "Legitimate brand name in fake domain",
    "URGENCY_ATTACK": "Psychological pressure manipulation",
    "FAKE_SSL": "False security signal (HTTPS without trust)",
    "IP_MASKING": "IP address used instead of domain",
    "SUBDOMAIN_ABUSE": "Trusted brand as subdomain of fake domain",
    "FREE_TLD": "Disposable free top-level domain",
    "CLEAN": "No attack pattern detected",
}

# ------------------------------------------------------------
# CORE FEATURE EXTRACTION ENGINE (28 FEATURES)
# ------------------------------------------------------------

HOMOGRAPH_MAP = {
    "0": "o",
    "1": "l",
    "3": "e",
    "4": "a",
    "5": "s",
    "@": "a",
    "$": "s",
    "vv": "w",
}

KNOWN_BRANDS = {
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
}

PHISHING_TLDS = {
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".xyz",
    ".top",
    ".click",
    ".work",
    ".loan",
    ".party",
    ".win",
    ".online",
}

URGENCY_WORDS = [
    "urgent",
    "immediately",
    "expire",
    "suspended",
    "verify",
    "confirm",
    "alert",
    "warning",
    "action",
    "update",
    "required",
    "limited",
    "unusual",
    "suspicious",
]

TRUST_WORDS = ["secure", "login", "account", "bank", "payment", "official"]


def extract_features(url: str) -> dict:
    """
    Extract 28 numeric features from a URL.
    These features are used to calculate threat score and Health Index.
    """
    url_lower = url.lower()

    domain_match = re.search(r"https?://([^/]+)", url)
    full_domain = domain_match.group(1) if domain_match else url

    domain_clean = re.sub(r":\d+", "", full_domain)

    tld_match = re.search(r"\.[a-z]{2,6}$", domain_clean)
    tld = tld_match.group(0) if tld_match else ""

    parts = domain_clean.split(".")
    domain_name = parts[-2] if len(parts) >= 2 else domain_clean
    subdomain = ".".join(parts[:-2]) if len(parts) > 2 else ""

    path_match = re.search(r"https?://[^/]+(/.+)?", url)
    path = path_match.group(1) or "" if path_match else ""
    query = re.search(r"\?(.+)", url)
    query_str = query.group(1) if query else ""

    features = {}

    # F1-F5
    features["url_length"] = len(url)
    features["domain_length"] = len(domain_name)
    features["subdomain_count"] = len(subdomain.split(".")) if subdomain else 0
    features["has_ip_address"] = int(bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain_clean)))
    features["suspicious_tld"] = int(tld in PHISHING_TLDS)

    # F6-F10
    features["brand_impersonation"] = int(
        any(brand in domain_name.lower() for brand in KNOWN_BRANDS)
        and domain_name.lower() not in KNOWN_BRANDS
    )
    features["has_https"] = int(url.startswith("https"))
    features["has_at_symbol"] = int("@" in url)
    features["has_double_slash"] = int("//" in path)
    features["special_char_count"] = len(re.findall(r"[!@#$%^&*(){}|\[\]<>]", url))

    # F11-F14
    digit_count = sum(1 for c in url if c.isdigit())
    features["digit_ratio"] = round(digit_count / max(len(url), 1), 3)
    features["hyphen_count"] = domain_clean.count("-")
    features["dot_count"] = url.count(".")
    features["query_param_count"] = len(query_str.split("&")) if query_str else 0

    # F15-F16
    homograph_found = []
    for fake_char in HOMOGRAPH_MAP:
        if fake_char in domain_name:
            homograph_found.append(fake_char)
    features["homograph_count"] = len(homograph_found)
    features["homograph_chars"] = homograph_found

    try:
        url.encode("ascii")
        features["has_unicode"] = 0
    except UnicodeEncodeError:
        features["has_unicode"] = 1

    # F17-F21
    features["has_login_keyword"] = int(any(w in url_lower for w in ["login", "signin", "auth", "logon"]))
    features["has_secure_keyword"] = int(any(w in url_lower for w in ["secure", "security", "ssl", "safe"]))
    features["has_verify_keyword"] = int(any(w in url_lower for w in ["verify", "verification", "confirm", "validate"]))
    features["has_urgency_keyword"] = int(any(w in url_lower for w in URGENCY_WORDS))
    features["has_update_keyword"] = int(any(w in url_lower for w in ["update", "upgrade", "renew", "restore"]))

    # F22-F28
    features["path_depth"] = len([p for p in path.split("/") if p])
    features["has_redirect"] = int("redirect" in url_lower or "url=" in url_lower or "return=" in url_lower)
    features["brand_in_subdomain"] = int(any(brand in subdomain.lower() for brand in KNOWN_BRANDS) if subdomain else False)
    features["url_too_long"] = int(len(url) > 100)

    trust_count = sum(1 for w in TRUST_WORDS if w in url_lower)
    features["trust_word_overload"] = int(trust_count >= 2)

    features["has_php_extension"] = int(".php" in path or ".asp" in path or ".aspx" in path)
    features["long_query"] = int(len(query_str) > 100)

    return features


# ------------------------------------------------------------
# FEATURE 2: HEALTH INDEX GENERATION
# ------------------------------------------------------------

FEATURE_WEIGHTS = {
    "has_ip_address": 15,
    "brand_impersonation": 14,
    "homograph_count": 12,
    "brand_in_subdomain": 12,
    "suspicious_tld": 10,
    "has_at_symbol": 10,
    "has_redirect": 8,
    "trust_word_overload": 8,
    "has_urgency_keyword": 7,
    "digit_ratio": 6,
    "subdomain_count": 5,
    "dot_count": 4,
    "url_too_long": 4,
    "hyphen_count": 3,
    "has_double_slash": 3,
    "has_php_extension": 3,
    "has_unicode": 3,
    "special_char_count": 2,
    "has_verify_keyword": 2,
    "has_update_keyword": 2,
    "has_login_keyword": 1,
    "has_secure_keyword": 1,
    "long_query": 1,
    "query_param_count": 1,
    "path_depth": 1,
    "url_length": 0,
    "domain_length": 0,
    "has_https": -5,
}

MAX_POSSIBLE_SCORE = sum(weight for weight in FEATURE_WEIGHTS.values() if weight > 0)


def calculate_health_index(features: dict) -> dict:
    """
    FEATURE 2: Health Index Generation.

    Converts features into a Threat Score (0-100), then:
    Health Index = 100 - Threat Score.
    """
    raw_score = 0
    score_breakdown = {}

    for feature_name, weight in FEATURE_WEIGHTS.items():
        if weight == 0:
            continue

        value = features.get(feature_name, 0)

        if feature_name == "homograph_count":
            contribution = min(value / 3, 1.0) * weight
        elif feature_name == "special_char_count":
            contribution = min(value / 5, 1.0) * weight
        elif feature_name == "subdomain_count":
            contribution = min(value / 4, 1.0) * weight
        elif feature_name == "dot_count":
            contribution = min(value / 6, 1.0) * weight
        elif feature_name == "digit_ratio":
            contribution = min(value * 3, 1.0) * weight
        elif feature_name == "query_param_count":
            contribution = min(value / 5, 1.0) * weight
        elif feature_name == "path_depth":
            contribution = min(value / 5, 1.0) * weight
        else:
            contribution = int(bool(value)) * weight

        raw_score += contribution
        if abs(contribution) > 0:
            score_breakdown[feature_name] = round(contribution, 2)

    threat_score = min(int((raw_score / MAX_POSSIBLE_SCORE) * 100), 100)
    threat_score = max(threat_score, 0)
    health_index = 100 - threat_score

    if threat_score >= 80:
        threat_level = "CRITICAL"
        level_color = "#FF3B3B"
    elif threat_score >= 60:
        threat_level = "DANGEROUS"
        level_color = "#FF6B35"
    elif threat_score >= 40:
        threat_level = "SUSPICIOUS"
        level_color = "#FFB800"
    else:
        threat_level = "SAFE"
        level_color = "#00FF88"

    return {
        "threat_score": threat_score,
        "health_index": health_index,
        "threat_level": threat_level,
        "level_color": level_color,
        "score_breakdown": score_breakdown,
        "is_phishing": threat_score >= 50,
    }


# ------------------------------------------------------------
# FEATURE 3: RUL PREDICTION
# ------------------------------------------------------------

def calculate_rul(features: dict, threat_score: int) -> dict:
    """
    FEATURE 3: RUL (Remaining Useful Life), adapted for phishing.

    Here, RUL means estimated time before an average user may fall for the attack.
    Lower RUL implies a more convincing attack.
    """
    base_rul_hours = 72
    sophistication_score = threat_score / 100
    rul_reduction = sophistication_score * 60

    if features.get("has_https"):
        rul_reduction += 8
    if features.get("brand_impersonation"):
        rul_reduction += 10
    if features.get("has_urgency_keyword"):
        rul_reduction += 7
    if features.get("trust_word_overload"):
        rul_reduction += 5

    rul_hours = max(base_rul_hours - rul_reduction, 0.5)
    rul_hours = round(rul_hours, 1)

    if rul_hours < 5:
        risk_assessment = "EXTREME - Highly convincing, can fool most users within hours"
        urgency = "IMMEDIATE"
    elif rul_hours < 20:
        risk_assessment = "HIGH - Sophisticated enough to fool untrained users quickly"
        urgency = "URGENT"
    elif rul_hours < 48:
        risk_assessment = "MODERATE - Can fool some users under pressure"
        urgency = "MONITOR"
    else:
        risk_assessment = "LOW - Trained users will likely detect this"
        urgency = "ROUTINE"

    victim_rate = max(0, int((1 - rul_hours / 72) * 35))

    return {
        "rul_hours": rul_hours,
        "rul_days": round(rul_hours / 24, 1),
        "urgency_level": urgency,
        "risk_assessment": risk_assessment,
        "estimated_victims_per_100": victim_rate,
        "recommended_action": _get_recommended_action(urgency),
    }


def _get_recommended_action(urgency: str) -> str:
    actions = {
        "IMMEDIATE": "Block immediately. Alert all users. Report to security team.",
        "URGENT": "Block within 1 hour. Send user warning. Log for analysis.",
        "MONITOR": "Flag for review. Educate user. Add to watch list.",
        "ROUTINE": "Log and monitor. Show education tip to user.",
    }
    return actions.get(urgency, "Monitor and log.")


# ------------------------------------------------------------
# FEATURE 4: ATTACK TYPE CLASSIFICATION
# ------------------------------------------------------------

def classify_attack(features: dict, url: str) -> dict:
    """
    FEATURE 4: Fault classification for phishing attack techniques.
    """
    del url

    detected = []

    if features.get("homograph_count", 0) > 0:
        detected.append(
            {
                "type": "HOMOGRAPH",
                "name": "Homograph Attack",
                "desc": ATTACK_TYPES["HOMOGRAPH"],
                "evidence": f"Found substituted characters: {features.get('homograph_chars', [])}",
                "severity": "HIGH",
            }
        )

    if features.get("brand_in_subdomain"):
        detected.append(
            {
                "type": "SUBDOMAIN_ABUSE",
                "name": "Subdomain Brand Abuse",
                "desc": ATTACK_TYPES["SUBDOMAIN_ABUSE"],
                "evidence": "Trusted brand name used inside subdomain of another domain",
                "severity": "HIGH",
            }
        )

    if features.get("brand_impersonation"):
        detected.append(
            {
                "type": "BRAND_IMPERSONATION",
                "name": "Brand Impersonation",
                "desc": ATTACK_TYPES["BRAND_IMPERSONATION"],
                "evidence": "Domain contains known brand term but is not official",
                "severity": "CRITICAL",
            }
        )

    if features.get("has_ip_address"):
        detected.append(
            {
                "type": "IP_MASKING",
                "name": "IP Address Masking",
                "desc": ATTACK_TYPES["IP_MASKING"],
                "evidence": "URL uses raw IP address instead of domain name",
                "severity": "CRITICAL",
            }
        )

    if features.get("has_urgency_keyword") and features.get("trust_word_overload"):
        detected.append(
            {
                "type": "URGENCY_ATTACK",
                "name": "Urgency + Trust Manipulation",
                "desc": ATTACK_TYPES["URGENCY_ATTACK"],
                "evidence": "Urgency language combined with trust-building keywords",
                "severity": "MEDIUM",
            }
        )
    elif features.get("has_urgency_keyword"):
        detected.append(
            {
                "type": "URGENCY_ATTACK",
                "name": "Urgency Manipulation",
                "desc": ATTACK_TYPES["URGENCY_ATTACK"],
                "evidence": "Contains pressure language to rush user action",
                "severity": "MEDIUM",
            }
        )

    if features.get("suspicious_tld"):
        detected.append(
            {
                "type": "FREE_TLD",
                "name": "Disposable Domain",
                "desc": ATTACK_TYPES["FREE_TLD"],
                "evidence": "Using free/disposable TLD often seen in phishing",
                "severity": "MEDIUM",
            }
        )

    if features.get("has_at_symbol"):
        detected.append(
            {
                "type": "TYPOSQUATTING",
                "name": "URL Misdirection (@)",
                "desc": "@ symbol can hide final destination",
                "evidence": "Everything before @ can mislead users about destination",
                "severity": "HIGH",
            }
        )

    if not detected:
        detected.append(
            {
                "type": "CLEAN",
                "name": "No Known Attack Pattern",
                "desc": ATTACK_TYPES["CLEAN"],
                "evidence": "URL passed all attack-type checks",
                "severity": "NONE",
            }
        )

    return {
        "primary_attack": detected[0] if detected else None,
        "all_attacks": detected,
        "attack_count": len([entry for entry in detected if entry["type"] != "CLEAN"]),
        "is_compound": len(detected) > 1 and detected[0]["type"] != "CLEAN",
    }


# ------------------------------------------------------------
# FEATURE 5: ALERT SYSTEM
# ------------------------------------------------------------

def generate_alert(url: str, threat_score: int, threat_level: str, rul: dict, attack_types: list) -> Optional[dict]:
    """
    FEATURE 5: Structured alert generation based on threat and urgency.
    """
    if threat_score < 40:
        return None

    alert_id = hashlib.md5(f"{url}{datetime.now().isoformat()}".encode()).hexdigest()[:8].upper()
    primary_attack = attack_types[0] if attack_types else {}

    alert = {
        "alert_id": f"PS-{alert_id}",
        "timestamp": datetime.now().isoformat(),
        "severity": rul.get("urgency_level", "MONITOR"),
        "threat_score": threat_score,
        "threat_level": threat_level,
        "url": url,
        "primary_attack": primary_attack.get("name", "Unknown"),
        "rul_hours": rul.get("rul_hours", 0),
        "action_required": rul.get("recommended_action", "Monitor"),
        "status": "ACTIVE",
        "auto_block": threat_score >= 80,
    }

    alert_queue.insert(0, alert)
    if len(alert_queue) > 50:
        alert_queue.pop()

    return alert


# ------------------------------------------------------------
# REQUEST/RESPONSE MODELS
# ------------------------------------------------------------

class ScanRequest(BaseModel):
    url: str
    user_id: Optional[str] = "demo_user"


class ScanResponse(BaseModel):
    scan_id: str
    url: str
    timestamp: str
    scan_time_ms: int
    health_index: dict
    rul: dict
    attack_types: dict
    alert: Optional[dict]
    features: dict
    explanation: str


# ------------------------------------------------------------
# API ENDPOINTS
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "SPECTER",
        "version": "2.0.0 - Round 2 Prototype",
        "features": [
            "Real-time monitoring",
            "Health Index generation",
            "RUL prediction",
            "Attack classification",
            "Alert system",
        ],
        "endpoints": {
            "scan": "POST /scan",
            "alerts": "GET /alerts",
            "stats": "GET /stats",
            "history": "GET /history",
            "demo": "GET /demo",
        },
    }


@app.post("/scan", response_model=ScanResponse)
def scan_url(request: ScanRequest):
    """
    Main endpoint that runs all 5 features in sequence:
    1) feature extraction
    2) Health Index generation
    3) RUL prediction
    4) attack classification
    5) alert generation
    """
    start_time = time.time()
    url = request.url.strip()

    features = extract_features(url)
    health = calculate_health_index(features)
    rul = calculate_rul(features, health["threat_score"])
    attacks = classify_attack(features, url)

    alert = generate_alert(
        url=url,
        threat_score=health["threat_score"],
        threat_level=health["threat_level"],
        rul=rul,
        attack_types=attacks["all_attacks"],
    )

    session_stats["total_scans"] += 1
    if health["is_phishing"]:
        session_stats["phishing_caught"] += 1
    else:
        session_stats["safe_confirmed"] += 1

    scan_record = {
        "url": url[:60] + "..." if len(url) > 60 else url,
        "score": health["threat_score"],
        "level": health["threat_level"],
        "primary_attack": attacks["primary_attack"]["name"] if attacks["primary_attack"] else "Clean",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    scan_history.insert(0, scan_record)
    if len(scan_history) > 20:
        scan_history.pop()

    explanation = _build_explanation(features, health, attacks)
    scan_time = int((time.time() - start_time) * 1000)
    clean_features = {key: value for key, value in features.items() if key != "homograph_chars"}

    return {
        "scan_id": f"SCAN-{int(time.time())}",
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "scan_time_ms": scan_time,
        "health_index": health,
        "rul": rul,
        "attack_types": attacks,
        "alert": alert,
        "features": clean_features,
        "explanation": explanation,
    }


def _build_explanation(features: dict, health: dict, attacks: dict) -> str:
    """Generate a plain-language explanation of findings."""
    if not health["is_phishing"]:
        return "This URL passed SPECTER checks. No phishing pattern detected."

    parts = []
    primary = attacks.get("primary_attack", {})

    if primary:
        parts.append(f"PRIMARY THREAT: {primary.get('name')} - {primary.get('evidence')}")

    if features.get("homograph_count", 0) > 0:
        chars = features.get("homograph_chars", [])
        parts.append(f"HOMOGRAPH SIGNAL: Substituted characters detected: {chars}")

    if features.get("has_urgency_keyword"):
        parts.append("URGENCY SIGNAL: Pressure language can force rushed decisions.")

    if not features.get("has_https"):
        parts.append("NO HTTPS: Missing SSL encryption is a risk signal.")

    if features.get("brand_impersonation"):
        parts.append("BRAND IMPERSONATION: URL appears to mimic a known brand.")

    score = health["threat_score"]
    parts.append(f"THREAT SCORE: {score}/100 ({health['threat_level']}). Avoid entering sensitive data.")

    return " | ".join(parts)


@app.get("/alerts")
def get_alerts():
    """FEATURE 5: Real-time alert feed for dashboard consumption."""
    return {
        "total_active": len(alert_queue),
        "alerts": alert_queue[:10],
        "last_updated": datetime.now().isoformat(),
    }


@app.get("/stats")
def get_stats():
    """FEATURE 1: Real-time monitoring statistics."""
    detection_rate = 0
    if session_stats["total_scans"] > 0:
        detection_rate = round(session_stats["phishing_caught"] / session_stats["total_scans"] * 100, 1)

    return {
        **session_stats,
        "detection_rate_pct": detection_rate,
        "active_alerts": len(alert_queue),
        "current_time": datetime.now().isoformat(),
    }


@app.get("/history")
def get_history():
    """FEATURE 1: Recent scan history for live monitoring."""
    return {"scans": scan_history, "total": len(scan_history)}


@app.get("/demo")
def run_demo():
    """
    Demo endpoint for judges.
    Runs 5 URLs through the full pipeline to demonstrate all features quickly.
    """
    demo_urls = [
        "http://paypa0.com/secure/login?verify=true&urgent=1",
        "https://www.google.com/search?q=weather",
        "http://192.168.1.1/bank/login.php",
        "https://amazon-secure-login.tk/verify/account",
        "https://github.com/torvalds/linux",
    ]

    results = []
    for url in demo_urls:
        result = scan_url(ScanRequest(url=url))
        results.append(
            {
                "url": url,
                "threat_score": result["health_index"]["threat_score"],
                "health_index": result["health_index"]["health_index"],
                "level": result["health_index"]["threat_level"],
                "primary_attack": result["attack_types"]["primary_attack"]["name"]
                if result["attack_types"]["primary_attack"]
                else "None",
                "rul_hours": result["rul"]["rul_hours"],
            }
        )

    return {
        "demo_results": results,
        "summary": "5 URLs scanned. All SPECTER core capabilities demonstrated.",
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 52)
    print("  SPECTER - Round 2 Prototype")
    print("  AI-Based Phishing Detection System")
    print("=" * 52)
    print("\n  API:   http://localhost:8000")
    print("  Docs:  http://localhost:8000/docs")
    print("  Demo:  http://localhost:8000/demo")
    print("\n  All 5 features active:")
    print("  - Real-time monitoring")
    print("  - Health Index generation")
    print("  - RUL prediction")
    print("  - Fault classification")
    print("  - Alert system")
    print("\n" + "=" * 52 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
