# d:/SPECTER/phantomshield/backend/ml/predictor.py
# Loads trained models and performs ensemble predictions.

import logging
from pathlib import Path
from typing import Dict

import joblib
import numpy as np

from ml.ensemble import WeightedEnsemble

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).resolve().parent / "models"


class PhishingPredictor:
    """
    Singleton predictor: loads models once and reuses for all requests.
    """

    _instance = None
    _models_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.__class__._models_loaded:
            self._load_models()

    def _load_models(self) -> None:
        try:
            rf_path = MODEL_DIR / "random_forest.pkl"
            xgb_path = MODEL_DIR / "xgboost_model.pkl"
            scaler_path = MODEL_DIR / "scaler.pkl"

            if not all(path.exists() for path in (rf_path, xgb_path, scaler_path)):
                logger.warning("Model files not found. Running trainer first.")
                from ml.model_trainer import train_and_save_models

                train_and_save_models()

            self.rf_model = joblib.load(rf_path)
            self.xgb_model = joblib.load(xgb_path)
            self.scaler = joblib.load(scaler_path)
            self.ensemble = WeightedEnsemble(rf_weight=0.45, xgb_weight=0.55)

            self.__class__._models_loaded = True
            logger.info("Models loaded successfully")

        except Exception as exc:
            logger.error("Model loading failed: %s", exc)
            self.__class__._models_loaded = False
            raise

    def predict(self, feature_vector: list[float]) -> Dict:
        """Run weighted ensemble prediction for a feature vector."""
        try:
            X = np.array(feature_vector).reshape(1, -1)
            X_scaled = self.scaler.transform(X)

            rf_proba = float(self.rf_model.predict_proba(X_scaled)[0][1])
            xgb_proba = float(self.xgb_model.predict_proba(X_scaled)[0][1])
            ensemble_proba = float(self.ensemble.combine(rf_proba, xgb_proba))

            threat_score = int(ensemble_proba * 100)

            # Heuristics adjustment layer based on feature vector values
            # Indices mapping in feature_vector:
            # 2: has_ip_address, 3: tld_suspicious, 4: domain_contains_brand
            # 14: has_homograph_chars, 20: has_login_keyword, 21: has_secure_keyword
            # 22: has_verify_keyword, 23: has_update_keyword, 24: has_urgency_keyword
            has_ip_address = len(feature_vector) > 2 and feature_vector[2] > 0.5
            tld_suspicious = len(feature_vector) > 3 and feature_vector[3] > 0.5
            domain_contains_brand = len(feature_vector) > 4 and feature_vector[4] > 0.5
            has_homograph_chars = len(feature_vector) > 14 and feature_vector[14] > 0.5

            has_login_keyword = len(feature_vector) > 20 and feature_vector[20] > 0.5
            has_verify_keyword = len(feature_vector) > 22 and feature_vector[22] > 0.5
            has_update_keyword = len(feature_vector) > 23 and feature_vector[23] > 0.5
            has_urgency_keyword = len(feature_vector) > 24 and feature_vector[24] > 0.5

            heuristics_score = 0
            if has_homograph_chars:
                heuristics_score = max(heuristics_score, 85)
            if has_ip_address:
                heuristics_score = max(heuristics_score, 80)
            if domain_contains_brand:
                heuristics_score = max(heuristics_score, 75)
            if tld_suspicious:
                heuristics_score = max(heuristics_score, 60)

            # Count of active security/urgency keywords
            kw_count = sum([
                int(has_login_keyword),
                int(has_verify_keyword),
                int(has_update_keyword),
                int(has_urgency_keyword),
            ])

            if heuristics_score > 0:
                heuristics_score += kw_count * 5
                heuristics_score = min(heuristics_score, 98)
            else:
                if kw_count >= 2:
                    heuristics_score = 45
                elif kw_count == 1:
                    heuristics_score = 25

            if heuristics_score > 0:
                threat_score = max(threat_score, heuristics_score)
                ensemble_proba = max(ensemble_proba, threat_score / 100.0)

            if threat_score >= 80:
                threat_level = "critical"
            elif threat_score >= 60:
                threat_level = "dangerous"
            elif threat_score >= 40:
                threat_level = "suspicious"
            else:
                threat_level = "safe"

            return {
                "threat_score": threat_score,
                "is_phishing": ensemble_proba > 0.5,
                "confidence": float(max(ensemble_proba, 1 - ensemble_proba)),
                "rf_probability": rf_proba,
                "xgb_probability": xgb_proba,
                "threat_level": threat_level,
            }
        except Exception as exc:
            logger.error("Prediction failed: %s", exc)
            return {
                "threat_score": 50,
                "is_phishing": False,
                "confidence": 0.5,
                "rf_probability": 0.5,
                "xgb_probability": 0.5,
                "threat_level": "suspicious",
            }
