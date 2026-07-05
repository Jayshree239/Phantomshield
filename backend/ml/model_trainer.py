# d:/SPECTER/phantomshield/backend/ml/model_trainer.py
# Trains Random Forest + XGBoost on phishing feature datasets.

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset() -> pd.DataFrame:
    """
    Load and prepare the phishing dataset.
    Expected local path: backend/data/phishing_dataset.csv
    If not found, synthetic training data is generated.
    """
    dataset_path = Path(__file__).resolve().parents[1] / "data" / "phishing_dataset.csv"

    try:
        df = pd.read_csv(dataset_path)
        if "Result" in df.columns and -1 in set(df["Result"].values):
            df["Result"] = df["Result"].map({-1: 0, 1: 1})
        return df
    except FileNotFoundError:
        return _generate_synthetic_data()


def _generate_synthetic_data(n_samples: int = 10000) -> pd.DataFrame:
    """Generate realistic synthetic data for local bootstrapping."""
    np.random.seed(42)
    n_phishing = n_samples // 2
    n_legit = n_samples - n_phishing

    legit_data = {
        "domain_length": np.random.randint(4, 15, n_legit),
        "subdomain_count": np.random.randint(0, 2, n_legit),
        "has_ip_address": np.zeros(n_legit, dtype=int),
        "tld_suspicious": np.zeros(n_legit, dtype=int),
        "domain_contains_brand": np.zeros(n_legit, dtype=int),
        "domain_age_score": np.full(n_legit, 0.5),
        "url_length": np.random.randint(15, 60, n_legit),
        "has_at_symbol": np.zeros(n_legit, dtype=int),
        "has_double_slash": np.zeros(n_legit, dtype=int),
        "special_char_count": np.random.randint(0, 3, n_legit),
        "digit_ratio": np.random.uniform(0.0, 0.08, n_legit),
        "hyphen_count": np.random.randint(0, 2, n_legit),
        "dot_count": np.random.randint(1, 3, n_legit),
        "query_param_count": np.random.randint(0, 2, n_legit),
        "has_homograph_chars": np.zeros(n_legit, dtype=int),
        "homograph_count": np.zeros(n_legit, dtype=int),
        "has_unicode": np.zeros(n_legit, dtype=int),
        "has_https": np.random.choice([0, 1], n_legit, p=[0.1, 0.9]),
        "ssl_valid": np.random.choice([0, 1], n_legit, p=[0.1, 0.9]),
        "ssl_age_score": np.random.choice([0.0, 0.5, 1.0], n_legit, p=[0.6, 0.1, 0.3]),
        "has_login_keyword": np.random.choice([0, 1], n_legit, p=[0.95, 0.05]),
        "has_secure_keyword": np.random.choice([0, 1], n_legit, p=[0.97, 0.03]),
        "has_verify_keyword": np.random.choice([0, 1], n_legit, p=[0.98, 0.02]),
        "has_update_keyword": np.random.choice([0, 1], n_legit, p=[0.98, 0.02]),
        "has_urgency_keyword": np.random.choice([0, 1], n_legit, p=[0.99, 0.01]),
        "path_depth": np.random.randint(0, 3, n_legit),
        "has_redirect": np.zeros(n_legit, dtype=int),
        "subdomain_depth": np.random.randint(0, 2, n_legit),
        "label": np.zeros(n_legit, dtype=int),
    }

    phishing_data = {
        "domain_length": np.random.randint(8, 25, n_phishing),
        "subdomain_count": np.random.randint(0, 3, n_phishing),
        "has_ip_address": np.zeros(n_phishing, dtype=int),
        "tld_suspicious": np.zeros(n_phishing, dtype=int),
        "domain_contains_brand": np.zeros(n_phishing, dtype=int),
        "domain_age_score": np.full(n_phishing, 0.5),
        "url_length": np.random.randint(25, 90, n_phishing),
        "has_at_symbol": np.zeros(n_phishing, dtype=int),
        "has_double_slash": np.zeros(n_phishing, dtype=int),
        "special_char_count": np.random.randint(0, 5, n_phishing),
        "digit_ratio": np.random.uniform(0.0, 0.15, n_phishing),
        "hyphen_count": np.random.randint(0, 3, n_phishing),
        "dot_count": np.random.randint(1, 4, n_phishing),
        "query_param_count": np.random.randint(0, 3, n_phishing),
        "has_homograph_chars": np.zeros(n_phishing, dtype=int),
        "homograph_count": np.zeros(n_phishing, dtype=int),
        "has_unicode": np.zeros(n_phishing, dtype=int),
        "has_https": np.random.choice([0, 1], n_phishing, p=[0.1, 0.9]),
        "ssl_valid": np.random.choice([0, 1], n_phishing, p=[0.1, 0.9]),
        "ssl_age_score": np.random.choice([0.0, 0.5, 1.0], n_phishing, p=[0.6, 0.1, 0.3]),
        "has_login_keyword": np.random.choice([0, 1], n_phishing, p=[0.75, 0.25]),
        "has_secure_keyword": np.random.choice([0, 1], n_phishing, p=[0.85, 0.15]),
        "has_verify_keyword": np.random.choice([0, 1], n_phishing, p=[0.75, 0.25]),
        "has_update_keyword": np.random.choice([0, 1], n_phishing, p=[0.8, 0.2]),
        "has_urgency_keyword": np.random.choice([0, 1], n_phishing, p=[0.75, 0.25]),
        "path_depth": np.random.randint(0, 3, n_phishing),
        "has_redirect": np.zeros(n_phishing, dtype=int),
        "subdomain_depth": np.random.randint(0, 2, n_phishing),
        "label": np.ones(n_phishing, dtype=int),
    }

    # Inject realistic phishing indicators so that phishing samples have 1 to 4 flags
    for i in range(n_phishing):
        n_indicators = np.random.randint(1, 3)
        indicators = np.random.choice(6, n_indicators, replace=False)

        if 0 in indicators:
            phishing_data["domain_contains_brand"][i] = 1
            phishing_data["domain_length"][i] = np.random.randint(15, 30)
            if np.random.rand() > 0.5:
                phishing_data["has_login_keyword"][i] = 1
            else:
                phishing_data["has_update_keyword"][i] = 1
        if 1 in indicators:
            phishing_data["has_homograph_chars"][i] = 1
            phishing_data["homograph_count"][i] = np.random.randint(1, 3)
            phishing_data["has_unicode"][i] = 1
        if 2 in indicators:
            phishing_data["has_ip_address"][i] = 1
            phishing_data["dot_count"][i] = np.random.randint(3, 5)
        if 3 in indicators:
            phishing_data["tld_suspicious"][i] = 1
        if 4 in indicators:
            phishing_data["has_urgency_keyword"][i] = 1
            phishing_data["has_verify_keyword"][i] = 1
            if np.random.rand() > 0.5:
                phishing_data["has_login_keyword"][i] = 1
        if 5 in indicators:
            phishing_data["has_redirect"][i] = 1
            phishing_data["has_at_symbol"][i] = 1
            if np.random.rand() > 0.5:
                phishing_data["has_double_slash"][i] = 1

    df_phishing = pd.DataFrame(phishing_data)
    df_legit = pd.DataFrame(legit_data)
    df = pd.concat([df_phishing, df_legit], ignore_index=True)
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def train_and_save_models() -> dict:
    """Train Random Forest + XGBoost and persist model artifacts."""
    print("Loading dataset...")
    df = load_dataset()

    feature_cols = [col for col in df.columns if col not in {"label", "Result"}]
    target_col = "label" if "label" in df.columns else "Result"

    X = df[feature_cols].values
    y = df[target_col].values

    print(f"Dataset: {len(X)} samples, {X.shape[1]} features")
    print(f"Phishing: {int(y.sum())} ({y.mean() * 100:.1f}%)")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("\nTraining Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf_model.fit(X_train_scaled, y_train)
    rf_pred = rf_model.predict(X_test_scaled)
    rf_proba = rf_model.predict_proba(X_test_scaled)[:, 1]

    print("Random Forest Results:")
    print(f"  Accuracy:  {accuracy_score(y_test, rf_pred) * 100:.2f}%")
    print(f"  Precision: {precision_score(y_test, rf_pred) * 100:.2f}%")
    print(f"  Recall:    {recall_score(y_test, rf_pred) * 100:.2f}%")
    print(f"  F1 Score:  {f1_score(y_test, rf_pred) * 100:.2f}%")
    print(f"  AUC-ROC:   {roc_auc_score(y_test, rf_proba) * 100:.2f}%")

    print("\nTraining XGBoost...")
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=1,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )
    xgb_model.fit(
        X_train_scaled,
        y_train,
        eval_set=[(X_test_scaled, y_test)],
        verbose=False,
    )
    xgb_pred = xgb_model.predict(X_test_scaled)
    xgb_proba = xgb_model.predict_proba(X_test_scaled)[:, 1]

    print("XGBoost Results:")
    print(f"  Accuracy:  {accuracy_score(y_test, xgb_pred) * 100:.2f}%")
    print(f"  Precision: {precision_score(y_test, xgb_pred) * 100:.2f}%")
    print(f"  Recall:    {recall_score(y_test, xgb_pred) * 100:.2f}%")
    print(f"  F1 Score:  {f1_score(y_test, xgb_pred) * 100:.2f}%")
    print(f"  AUC-ROC:   {roc_auc_score(y_test, xgb_proba) * 100:.2f}%")

    ensemble_proba = (rf_proba + xgb_proba) / 2
    ensemble_pred = (ensemble_proba > 0.5).astype(int)
    print("\nEnsemble Results:")
    print(f"  Accuracy:  {accuracy_score(y_test, ensemble_pred) * 100:.2f}%")
    print(f"  AUC-ROC:   {roc_auc_score(y_test, ensemble_proba) * 100:.2f}%")

    print("\nSaving models...")
    joblib.dump(rf_model, MODEL_DIR / "random_forest.pkl")
    joblib.dump(xgb_model, MODEL_DIR / "xgboost_model.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")

    importance_df = pd.DataFrame(
        {
            "feature": feature_cols,
            "rf_importance": rf_model.feature_importances_,
            "xgb_importance": xgb_model.feature_importances_,
        }
    ).sort_values("rf_importance", ascending=False)
    importance_df.to_csv(MODEL_DIR / "feature_importance.csv", index=False)

    print(f"\nModels saved to {MODEL_DIR}/")
    print("Top 5 most important features:")
    print(importance_df.head())

    return {
        "rf_accuracy": float(accuracy_score(y_test, rf_pred)),
        "xgb_accuracy": float(accuracy_score(y_test, xgb_pred)),
        "ensemble_accuracy": float(accuracy_score(y_test, ensemble_pred)),
    }


if __name__ == "__main__":
    train_and_save_models()
