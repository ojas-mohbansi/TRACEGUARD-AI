"""
Machine Learning Engine for TraceGuard AI.
Uses Isolation Forest to detect anomalous sessions based on extracted features.
"""
import os
import time
from typing import Dict, Any, List, Union, Optional
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

from ..features.extractor import FEATURE_COLUMNS, FeatureExtractor


def risk_to_severity(risk_score: int) -> str:
    """Map risk score (0-100) to severity category."""
    if risk_score >= 76:
        return "critical"
    if risk_score >= 51:
        return "high"
    if risk_score >= 26:
        return "medium"
    return "low"


class MLEngine:
    """
    ML detection engine using Isolation Forest.
    Outputs:
    - anomaly_score: 0.0 (normal) to 1.0 (anomalous)
    - risk_score: 0 to 100
    - prediction: "normal" | "anomalous"
    """

    def __init__(
        self,
        contamination: float = 0.1,
        random_state: int = 42,
        model_version: str = "1.0.0",
        model_path: Optional[str] = None,
    ):
        self.contamination = contamination
        self.random_state = random_state
        self.model_version = model_version
        self.feature_columns = FEATURE_COLUMNS
        self.extractor = FeatureExtractor()
        self.model_path = model_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models", "isolation_forest.joblib")
        )

        self.model: Optional[IsolationForest] = None
        self._score_min: float = -0.5
        self._score_max: float = 0.5

        # Try to load existing model if path exists
        if os.path.exists(self.model_path):
            try:
                self.load_model(self.model_path)
            except Exception:
                pass

    def train(self, features_df: pd.DataFrame, seed: int = 42) -> Dict[str, Any]:
        """
        Train Isolation Forest on extracted features dataframe.
        """
        self.random_state = seed
        X = features_df[self.feature_columns].copy().fillna(0.0)

        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            n_jobs=-1,
        )
        self.model.fit(X)

        # In sklearn Isolation Forest: decision_function yields raw anomaly score.
        # Lower score = more abnormal (e.g. -0.2 to -0.4 is outlier, 0.1 to 0.2 is inlier).
        # We invert so higher = more anomalous.
        raw_scores = self.model.decision_function(X)
        self._score_min = float(np.min(raw_scores))
        self._score_max = float(np.max(raw_scores))

        return {
            "status": "trained",
            "samples": len(X),
            "features": len(self.feature_columns),
            "score_min": self._score_min,
            "score_max": self._score_max,
        }

    def _normalize_anomaly_score(self, raw_decision: float) -> float:
        """
        Convert decision_function score (where lower is more anomalous)
        to anomaly_score in [0.0, 1.0], where 0.0=normal, 1.0=anomalous.
        """
        # decision_function: typically between -0.5 (very anomalous) and +0.3 (very normal)
        # Using min-max normalization inverted:
        if self._score_max > self._score_min:
            norm = (self._score_max - raw_decision) / (self._score_max - self._score_min)
        else:
            norm = 0.5 - raw_decision
        
        # Clip to [0.0, 1.0]
        return float(np.clip(norm, 0.0, 1.0))

    def _compute_pseudo_feature_importances(self, x_row: pd.Series) -> Dict[str, float]:
        """
        Approximate feature importances for Isolation Forest using normalized variance or z-scores.
        Provides interpretable feature contribution weights in [0.0, 1.0].
        """
        importances = {}
        for col in self.feature_columns:
            val = float(x_row.get(col, 0.0))
            if col in ("invalid_transition_count", "auth_failure_count", "error_count"):
                weight = min(1.0, val * 0.3)
            elif col in ("response_4xx_ratio", "response_5xx_ratio"):
                weight = min(1.0, val)
            elif col == "has_close":
                weight = 0.2 if val == 0.0 else 0.05
            elif col == "request_rate":
                weight = min(1.0, val / 10.0)
            else:
                weight = min(1.0, abs(val) / 100.0) if val > 0 else 0.02
            importances[col] = round(float(weight), 4)

        # Normalize so sum = 1.0 if not empty
        tot = sum(importances.values())
        if tot > 0:
            importances = {k: round(v / tot, 4) for k, v in importances.items()}
        return importances

    def predict(self, features_df: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Predict on session features.
        Accepts:
        - DataFrame containing feature columns and optional 'session_id'
        - Dict of single session features
        - List of session feature dicts
        Returns list of detection dicts:
        {
            "session_id": str,
            "engine": "ml",
            "prediction": "normal" | "anomalous",
            "risk_score": int(0-100),
            "severity": "low" | "medium" | "high" | "critical",
            "ml_anomaly_score": float(0.0-1.0),
            "feature_importances": dict,
            "model_version": str,
            "processing_time_ms": float
        }
        """
        start_time = time.perf_counter()

        if isinstance(features_df, dict):
            df = pd.DataFrame([features_df])
        elif isinstance(features_df, list):
            df = pd.DataFrame(features_df)
        elif isinstance(features_df, pd.DataFrame):
            df = features_df.copy()
        else:
            raise ValueError(f"Unsupported features type: {type(features_df)}")

        # Ensure feature columns exist
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0.0

        if "session_id" not in df.columns:
            df["session_id"] = [f"session_{i}" for i in range(len(df))]

        results = []
        X = df[self.feature_columns].fillna(0.0)

        if self.model is None:
            # Fallback heuristic if model is not yet loaded
            for _, row in df.iterrows():
                sid = str(row["session_id"])
                results.append({
                    "session_id": sid,
                    "engine": "ml",
                    "prediction": "normal",
                    "risk_score": 0,
                    "severity": "low",
                    "ml_anomaly_score": 0.0,
                    "feature_importances": {col: round(1.0 / len(self.feature_columns), 4) for col in self.feature_columns},
                    "model_version": self.model_version,
                    "processing_time_ms": round((time.perf_counter() - start_time) * 1000, 2),
                })
            return results

        raw_scores = self.model.decision_function(X)
        preds = self.model.predict(X)  # 1: inlier (normal), -1: outlier (anomalous)

        proc_time_ms = round((time.perf_counter() - start_time) * 1000 / max(1, len(df)), 3)

        for i, (_, row) in enumerate(df.iterrows()):
            sid = str(row["session_id"])
            raw_dec = float(raw_scores[i])
            is_outlier = (preds[i] == -1)

            anomaly_score = self._normalize_anomaly_score(raw_dec)

            # High risk score if outlier or high anomaly score
            risk_score = int(round(anomaly_score * 100))
            risk_score = max(0, min(100, risk_score))
            
            # Predict anomalous if outlier or anomaly_score > 0.55
            prediction = "anomalous" if (is_outlier or anomaly_score >= 0.55) else "normal"
            severity = risk_to_severity(risk_score)
            feat_imp = self._compute_pseudo_feature_importances(row)

            results.append({
                "session_id": sid,
                "engine": "ml",
                "prediction": prediction,
                "risk_score": risk_score,
                "severity": severity,
                "ml_anomaly_score": round(anomaly_score, 4),
                "feature_importances": feat_imp,
                "model_version": self.model_version,
                "processing_time_ms": proc_time_ms,
            })

        return results

    def predict_session(self, events: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convenience method to extract features from a session event list and predict.
        Returns a single detection dict matching API expectations:
        {
            "session_id": str,
            "engine": "ml",
            "prediction": "normal" | "anomalous",
            "anomaly_score": float,  # alias for ml_anomaly_score
            "ml_anomaly_score": float,
            "risk_score": int,
            "severity": str,
            "feature_importances": dict,
            "processing_time_ms": float
        }
        """
        if isinstance(events, dict):
            event_list = [events]
        else:
            event_list = events or []

        if not event_list:
            return {
                "session_id": "unknown",
                "engine": "ml",
                "prediction": "normal",
                "anomaly_score": 0.0,
                "ml_anomaly_score": 0.0,
                "risk_score": 0,
                "severity": "low",
                "feature_importances": {col: round(1.0 / len(self.feature_columns), 4) for col in self.feature_columns},
                "model_version": self.model_version,
                "processing_time_ms": 0.0
            }

        session_id = "unknown"
        if event_list and isinstance(event_list[0], dict):
            session_id = str(event_list[0].get("session_id", "unknown"))

        features = self.extractor.extract_session_features(event_list)
        features["session_id"] = session_id
        res_list = self.predict([features])
        if res_list:
            res = res_list[0].copy()
            res["anomaly_score"] = res.get("ml_anomaly_score", 0.0)
            return res

        return {
            "session_id": session_id,
            "engine": "ml",
            "prediction": "normal",
            "anomaly_score": 0.0,
            "ml_anomaly_score": 0.0,
            "risk_score": 0,
            "severity": "low",
            "feature_importances": {},
            "processing_time_ms": 0.0
        }

    def save_model(self, file_path: Optional[str] = None):
        """Save trained Isolation Forest model bundle."""
        target_path = file_path or self.model_path
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        bundle = {
            "model": self.model,
            "feature_columns": self.feature_columns,
            "score_min": self._score_min,
            "score_max": self._score_max,
            "contamination": self.contamination,
            "random_state": self.random_state,
            "model_version": self.model_version,
        }
        joblib.dump(bundle, target_path)

    def load_model(self, file_path: Optional[str] = None):
        """Load trained Isolation Forest model bundle."""
        target_path = file_path or self.model_path
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Model file not found at: {target_path}")

        bundle = joblib.load(target_path)
        if isinstance(bundle, dict):
            self.model = bundle.get("model")
            self.feature_columns = bundle.get("feature_columns", FEATURE_COLUMNS)
            self._score_min = bundle.get("score_min", -0.5)
            self._score_max = bundle.get("score_max", 0.5)
            self.contamination = bundle.get("contamination", 0.1)
            self.random_state = bundle.get("random_state", 42)
            self.model_version = bundle.get("model_version", "1.0.0")
        else:
            # Direct estimator
            self.model = bundle
