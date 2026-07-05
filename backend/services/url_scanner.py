# d:/SPECTER/phantomshield/backend/services/url_scanner.py
# URL scanning pipeline helpers.

from typing import List

from ml.feature_extractor import URLFeatureExtractor
from ml.predictor import PhishingPredictor
from models.scan_models import AttackType

extractor = URLFeatureExtractor()
predictor = PhishingPredictor()


def determine_attack_types(feature_dict: dict) -> List[AttackType]:
    attacks: List[AttackType] = []

    if feature_dict.get("has_homograph_chars"):
        attacks.append(AttackType.HOMOGRAPH)
    if feature_dict.get("domain_contains_brand"):
        attacks.append(AttackType.BRAND_IMPERSONATION)
    if feature_dict.get("has_ip_address"):
        attacks.append(AttackType.CREDENTIAL_HARVESTING)
    if feature_dict.get("has_urgency_keyword"):
        attacks.append(AttackType.URGENCY_MANIPULATION)
    if not feature_dict.get("ssl_valid") and feature_dict.get("has_secure_keyword"):
        attacks.append(AttackType.FAKE_SSL)
    if feature_dict.get("domain_age_score", 0) > 0.7 and not attacks:
        attacks.append(AttackType.TYPOSQUATTING)

    return attacks or [AttackType.UNKNOWN]


def scan_url_features(url: str) -> dict:
    feature_vector, feature_dict = extractor.extract(url)
    prediction = predictor.predict(feature_vector)
    attack_types = determine_attack_types(feature_dict)
    return {
        "feature_vector": feature_vector,
        "feature_dict": feature_dict,
        "prediction": prediction,
        "attack_types": attack_types,
    }
