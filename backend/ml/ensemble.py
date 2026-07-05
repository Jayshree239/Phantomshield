# d:/SPECTER/phantomshield/backend/ml/ensemble.py
from dataclasses import dataclass


@dataclass
class WeightedEnsemble:
    rf_weight: float = 0.45
    xgb_weight: float = 0.55

    def combine(self, rf_probability: float, xgb_probability: float) -> float:
        total = self.rf_weight + self.xgb_weight
        if total <= 0:
            return 0.5
        return ((rf_probability * self.rf_weight) + (xgb_probability * self.xgb_weight)) / total
