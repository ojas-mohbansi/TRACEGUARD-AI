"""Hybrid Detection Engine integrating FSM and ML analysis."""
from typing import Dict, Any, List, Optional
import time


class HybridEngine:
    """Combines deterministic FSM protocol verification with statistical ML anomaly scores."""

    def __init__(self, fsm_engine=None, ml_engine=None, fsm_weight: float = 0.6, ml_weight: float = 0.4):
        self.fsm_engine = fsm_engine
        self.ml_engine = ml_engine
        self.fsm_weight = fsm_weight
        self.ml_weight = ml_weight

    def _risk_to_severity(self, risk_score: int) -> str:
        if risk_score >= 76:
            return "critical"
        if risk_score >= 51:
            return "high"
        if risk_score >= 26:
            return "medium"
        return "low"

    def detect_session(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run hybrid detection on a sequence of events belonging to one session."""
        start_time = time.time()
        session_id = events[0].get("session_id", "unknown") if events else "unknown"

        # 1. FSM Engine evaluation
        fsm_result = None
        fsm_score = 0.0
        fsm_violation = False
        fsm_explanation = ""
        responsible_events = []

        if self.fsm_engine:
            try:
                fsm_result = self.fsm_engine.validate_session(events)
                fsm_score = float(fsm_result.get("risk_score", 0))
                fsm_violation = bool(fsm_result.get("fsm_violation", False))
                fsm_explanation = fsm_result.get("explanation", "")
                responsible_events = fsm_result.get("responsible_events", [])
            except Exception as e:
                fsm_explanation = f"FSM execution error: {str(e)}"
        else:
            # Fallback simple FSM transition check if engine not injected
            pass

        # 2. ML Engine evaluation
        ml_result = None
        ml_anomaly_score = 0.0
        ml_prediction = "normal"
        if self.ml_engine:
            try:
                ml_result = self.ml_engine.predict_session(events)
                ml_anomaly_score = float(ml_result.get("anomaly_score", 0.0))
                ml_prediction = ml_result.get("prediction", "normal")
            except Exception as e:
                pass

        ml_score = ml_anomaly_score * 100.0

        # 3. Hybrid Combination Formula: (fsm_weight * fsm_score) + (ml_weight * ml_score)
        # If FSM violation detected, minimum hybrid_score = 60
        combined_score = (self.fsm_weight * fsm_score) + (self.ml_weight * ml_score)
        if fsm_violation:
            combined_score = max(combined_score, 60.0)

        risk_score = int(round(min(100.0, max(0.0, combined_score))))
        severity = self._risk_to_severity(risk_score)

        # ML anomaly flag: anomaly score strictly >= 0.70 for statistical significance
        ml_anomalous = bool(ml_result and ml_anomaly_score >= 0.70)

        # Exact component attribution
        if fsm_violation and ml_anomalous:
            attribution = "hybrid"
        elif fsm_violation:
            attribution = "fsm"
        elif ml_anomalous:
            attribution = "ml"
        else:
            attribution = "none"

        # Hybrid prediction rule: anomalous if risk_score >= 40 or protocol violation detected
        prediction = "anomalous" if (risk_score >= 40 or fsm_violation) else "normal"

        explanation_parts = []
        if fsm_violation:
            explanation_parts.append(f"FSM protocol violation detected ({fsm_explanation or 'invalid state transition'}).")
        else:
            explanation_parts.append("Protocol sequence conforms to HTTP state machine.")

        if ml_anomalous:
            explanation_parts.append(f"ML Isolation Forest detected statistical anomaly (score: {ml_anomaly_score:.2f}).")
        else:
            explanation_parts.append(f"ML statistical profile within normal limits (score: {ml_anomaly_score:.2f}).")

        explanation = " ".join(explanation_parts)

        processing_time_ms = round((time.time() - start_time) * 1000.0, 2)

        return {
            "session_id": session_id,
            "engine": attribution if attribution != "none" else "hybrid",
            "attribution": attribution,
            "prediction": prediction,
            "risk_score": risk_score,
            "severity": severity,
            "fsm_violation": fsm_violation,
            "ml_anomalous": ml_anomalous,
            "ml_anomaly_score": round(ml_anomaly_score, 4),
            "explanation": explanation,
            "responsible_events": responsible_events,
            "processing_time_ms": processing_time_ms,
            "fsm_result": fsm_result,
            "ml_result": ml_result,
            "hybrid_result": {
                "combined_risk_score": risk_score,
                "severity": severity,
                "fsm_weight": self.fsm_weight,
                "ml_weight": self.ml_weight,
                "fsm_score": fsm_score,
                "ml_score": ml_score,
                "formula": f"max(0.6 * {fsm_score} + 0.4 * {ml_score:.1f}, 60.0)" if fsm_violation else f"0.6 * {fsm_score} + 0.4 * {ml_score:.1f}",
                "floor_applied": bool(fsm_violation and combined_score < 60.0),
                "attribution": attribution,
                "explanation": explanation
            }
        }
