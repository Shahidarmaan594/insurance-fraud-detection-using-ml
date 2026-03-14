"""
Machine Learning Fraud Detection Model.
Ensemble of Random Forest + Logistic Regression with feature engineering.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler

# Model version
MODEL_VERSION = "1.0.0"
FEATURE_COLUMNS = [
    "claim_amount_category_encoded",
    "age_group_encoded",
    "claim_frequency_encoded",
    "policy_ratio",
    "normalized_age",
    "normalized_amount",
    "normalized_frequency",
    "claim_type_auto",
    "claim_type_health",
    "claim_type_property",
    "claim_type_liability",
]


def get_claim_amount_category(amount: float) -> str:
    """Categorize claim amount."""
    if amount < 5000:
        return "low"
    if amount < 20000:
        return "medium"
    if amount < 75000:
        return "high"
    return "extreme"


def get_age_group(age: int) -> str:
    """Categorize age."""
    if age < 35:
        return "young"
    if age < 55:
        return "middle"
    return "senior"


def get_claim_frequency(prev_claims: int) -> str:
    """Categorize claim frequency."""
    if prev_claims == 0:
        return "new"
    if prev_claims <= 2:
        return "regular"
    return "frequent"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply feature engineering to claim data.
    """
    df = df.copy()

    # Basic derived features
    df["claim_amount_category"] = df["claim_amount"].apply(get_claim_amount_category)
    df["age_group"] = df["claimant_age"].apply(get_age_group)
    df["claim_frequency"] = df["previous_claims_count"].apply(get_claim_frequency)
    df["policy_ratio"] = df["claim_amount"] / (df["policy_duration_months"] + 1)
    df["policy_ratio"] = np.clip(df["policy_ratio"], 0, 10000)

    # Normalized features (0-1)
    df["normalized_age"] = (df["claimant_age"] - 18) / 62
    df["normalized_amount"] = np.log1p(df["claim_amount"]) / np.log1p(500000)
    df["normalized_frequency"] = df["previous_claims_count"] / 10

    # Encode categoricals
    amount_map = {"low": 0, "medium": 1, "high": 2, "extreme": 3}
    age_map = {"young": 0, "middle": 1, "senior": 2}
    freq_map = {"new": 0, "regular": 1, "frequent": 2}

    df["claim_amount_category_encoded"] = df["claim_amount_category"].map(amount_map)
    df["age_group_encoded"] = df["age_group"].map(age_map)
    df["claim_frequency_encoded"] = df["claim_frequency"].map(freq_map)

    # One-hot claim type
    for ct in ["auto", "health", "property", "liability"]:
        df[f"claim_type_{ct}"] = (df["claim_type"] == ct).astype(int)

    return df


def prepare_claim_for_prediction(claim_data: dict) -> np.ndarray:
    """
    Convert single claim dict to feature array for prediction.
    """
    df = pd.DataFrame([claim_data])
    df = engineer_features(df)
    # Ensure all columns exist
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0
    return df[FEATURE_COLUMNS].values


class FraudDetectionModel:
    """
    Fraud detection model with ensemble (RF + LR) and calibration.
    """

    def __init__(self, model_path: Optional[Path] = None):
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_importance_ = {}
        self.metrics = {}
        self.model_path = model_path
        if model_path and model_path.exists():
            self.load()

    def _build_model(self):
        """Build the ensemble model."""
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            n_jobs=-1,
        )
        lr = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight="balanced",
        )
        return VotingClassifier(
            estimators=[("rf", rf), ("lr", lr)],
            voting="soft",
            weights=[2, 1],
        )

    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Train model with stratified k-fold cross validation.
        """
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = self._build_model()
        self.model.fit(X_scaled, y)

        # Cross-validation predictions
        y_pred_proba = cross_val_predict(
            self.model, X_scaled, y, cv=cv, method="predict_proba"
        )[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)

        # Metrics
        self.metrics = {
            "accuracy": float(accuracy_score(y, y_pred)),
            "precision": float(precision_score(y, y_pred, zero_division=0)),
            "recall": float(recall_score(y, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y, y_pred_proba)),
        }

        cm = confusion_matrix(y, y_pred)
        self.metrics["confusion_matrix"] = cm.tolist()

        # Feature importance from RF
        rf_model = self.model.named_estimators_["rf"]
        importances = dict(zip(FEATURE_COLUMNS, rf_model.feature_importances_.tolist()))
        self.feature_importance_ = dict(
            sorted(importances.items(), key=lambda x: x[1], reverse=True)
        )

        return self.metrics

    def predict_fraud_probability(self, claim_data: dict) -> float:
        """
        Predict fraud probability (0-100).
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Run training or load from file.")
        X = prepare_claim_for_prediction(claim_data)
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)[0, 1]
        return round(float(proba) * 100, 2)

    def get_risk_level(self, probability: float) -> str:
        """
        Get risk level from probability (0-100).
        """
        if probability < 30:
            return "low"
        if probability < 60:
            return "medium"
        if probability < 80:
            return "high"
        return "critical"

    def get_feature_importance(self) -> Dict[str, float]:
        """Return feature importance scores."""
        return self.feature_importance_.copy()

    def explain_prediction(self, claim_data: dict) -> Dict[str, Any]:
        """
        Explain prediction with top factors.
        """
        prob = self.predict_fraud_probability(claim_data)
        importance = self.get_feature_importance()

        # Top factors that increase risk
        claim_df = pd.DataFrame([claim_data])
        claim_df = engineer_features(claim_df)

        factors_increase = []
        factors_decrease = []
        for feat, imp in list(importance.items())[:5]:
            val = 0
            if feat in claim_df.columns:
                val = claim_df[feat].iloc[0]
            readable = feat.replace("_encoded", "").replace("claim_type_", "")
            if imp > 0.05 and val > 0:
                factors_increase.append({"factor": readable, "importance": round(imp, 4)})
            elif imp > 0.05:
                factors_decrease.append({"factor": readable, "importance": round(imp, 4)})

        return {
            "probability": prob,
            "risk_level": self.get_risk_level(prob),
            "factors_increasing_risk": factors_increase[:3],
            "factors_decreasing_risk": factors_decrease[:3],
        }

    def save(self, path: Optional[Path] = None):
        """Save model and metrics."""
        path = path or self.model_path
        if not path:
            raise ValueError("No path provided for saving")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        obj = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_importance": self.feature_importance_,
            "metrics": self.metrics,
            "version": MODEL_VERSION,
        }
        joblib.dump(obj, path)

        # Save metrics to JSON
        metrics_path = path.parent / "model_metrics.json"
        save_metrics = {k: v for k, v in self.metrics.items() if k != "confusion_matrix"}
        save_metrics["confusion_matrix"] = self.metrics.get("confusion_matrix", [])
        save_metrics["feature_importance"] = self.feature_importance_
        save_metrics["version"] = MODEL_VERSION
        with open(metrics_path, "w") as f:
            json.dump(save_metrics, f, indent=2)

    def load(self, path: Optional[Path] = None):
        """Load model from file."""
        path = path or self.model_path
        if not path or not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        obj = joblib.load(path)
        self.model = obj["model"]
        self.scaler = obj["scaler"]
        self.feature_importance_ = obj.get("feature_importance", {})
        self.metrics = obj.get("metrics", {})


# Global model instance
_model_instance: Optional[FraudDetectionModel] = None


def get_model(model_path: Optional[Path] = None) -> FraudDetectionModel:
    """Get or create model singleton."""
    global _model_instance
    if _model_instance is None:
        _model_instance = FraudDetectionModel(model_path)
    return _model_instance


def train_model(csv_path: Path, output_path: Path) -> Dict[str, float]:
    """
    Train model from CSV and save.
    """
    df = pd.read_csv(csv_path)
    if "is_fraud" not in df.columns:
        raise ValueError("CSV must contain 'is_fraud' column")

    df = engineer_features(df)
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0

    X = df[FEATURE_COLUMNS].values
    y = df["is_fraud"].values

    model = FraudDetectionModel()
    metrics = model.train(X, y)
    model.save(output_path)

    print(f"Model trained. Accuracy: {metrics['accuracy']:.4f}, "
          f"F1: {metrics['f1_score']:.4f}, ROC-AUC: {metrics['roc_auc']:.4f}")
    return metrics
