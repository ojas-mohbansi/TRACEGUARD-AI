"""Empirical Verification Suite for Hybrid Scoring Engine and Quadrant Analysis.

Verifies:
1. Standard Academic Consensus Formula: S_h = 0.6 * S_FSM + 0.4 * S_ML.
2. Mandatory FSM Protocol Violation Floor: S_h >= 60 whenever fsm_violation is True.
3. Strict Quadrant Analysis:
   - Q1: Valid FSM + Normal ML -> Normal (Low Risk).
   - Q2: Valid FSM + Anomalous ML -> Statistical Anomaly.
   - Q3: Invalid FSM + Normal ML -> Protocol Violation with >= 60% risk floor.
   - Q4: Invalid FSM + Anomalous ML -> Critical Compound Anomaly.
4. Normalization and bounds: 0 <= risk_score <= 100.
"""
import pytest
from app.detection.hybrid import HybridEngine
from app.detection.fsm import FSMEngine
from app.detection.ml import MLEngine


def test_hybrid_engine_default_weights():
    """Verify default engine weights are strictly 0.6 FSM and 0.4 ML."""
    engine = HybridEngine()
    assert engine.fsm_weight == 0.6, f"Expected FSM weight 0.6, got {engine.fsm_weight}"
    assert engine.ml_weight == 0.4, f"Expected ML weight 0.4, got {engine.ml_weight}"
    assert round(engine.fsm_weight + engine.ml_weight, 5) == 1.0


def test_quadrant_1_known_normal():
    """Quadrant 1: Legitimate FSM sequence and normal ML features -> Normal verdict."""
    fsm = FSMEngine()
    ml = MLEngine()
    hybrid = HybridEngine(fsm_engine=fsm, ml_engine=ml, fsm_weight=0.6, ml_weight=0.4)

    events = [
        {"session_id": "sess_q1", "event_id": "e1", "timestamp": "2026-11-17T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "sess_q1", "event_id": "e2", "timestamp": "2026-11-17T12:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 250},
        {"session_id": "sess_q1", "event_id": "e3", "timestamp": "2026-11-17T12:00:02", "event_type": "AUTH_SUCCESS", "method": "GET", "status_code": 0, "bytes": 150},
        {"session_id": "sess_q1", "event_id": "e4", "timestamp": "2026-11-17T12:00:03", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1500},
        {"session_id": "sess_q1", "event_id": "e5", "timestamp": "2026-11-17T12:00:04", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]

    res = hybrid.detect_session(events)
    assert res["fsm_violation"] is False
    assert res["risk_score"] <= 35
    assert res["prediction"] == "normal"
    assert res["severity"] in ["low", "medium"]


def test_quadrant_2_statistical_anomaly_clean_fsm():
    """Quadrant 2: Structurally valid FSM sequence with statistical ML anomaly."""
    # Mocking ML engine to return high anomaly score while FSM is valid
    class MockHighMLEngine:
        def predict_session(self, events):
            return {"anomaly_score": 0.85, "prediction": "anomalous"}

    fsm = FSMEngine()
    mock_ml = MockHighMLEngine()
    hybrid = HybridEngine(fsm_engine=fsm, ml_engine=mock_ml, fsm_weight=0.6, ml_weight=0.4)

    events = [
        {"session_id": "sess_q2", "event_id": "e1", "timestamp": "2026-11-17T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "sess_q2", "event_id": "e2", "timestamp": "2026-11-17T12:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 250},
        {"session_id": "sess_q2", "event_id": "e3", "timestamp": "2026-11-17T12:00:02", "event_type": "AUTH_SUCCESS", "method": "GET", "status_code": 0, "bytes": 150},
        {"session_id": "sess_q2", "event_id": "e4", "timestamp": "2026-11-17T12:00:03", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1500},
        {"session_id": "sess_q2", "event_id": "e5", "timestamp": "2026-11-17T12:00:04", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]

    res = hybrid.detect_session(events)
    assert res["fsm_violation"] is False
    # 0.6 * 0 + 0.4 * 85 = 34
    assert res["risk_score"] == 34
    assert res["ml_anomaly_score"] == 0.85


def test_quadrant_3_fsm_violation_with_60_percent_floor():
    """Quadrant 3: FSM violation occurs with ML score near 0; risk score must clamp to >= 60%."""
    class MockZeroMLEngine:
        def predict_session(self, events):
            return {"anomaly_score": 0.0, "prediction": "normal"}

    fsm = FSMEngine()
    mock_ml = MockZeroMLEngine()
    hybrid = HybridEngine(fsm_engine=fsm, ml_engine=mock_ml, fsm_weight=0.6, ml_weight=0.4)

    # Invalid sequence: skipping auth from REQUEST_RECEIVED straight to RESPONSE_200
    events = [
        {"session_id": "sess_q3", "event_id": "e1", "timestamp": "2026-11-17T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "sess_q3", "event_id": "e2", "timestamp": "2026-11-17T12:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 250},
        {"session_id": "sess_q3", "event_id": "e3", "timestamp": "2026-11-17T12:00:02", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1500},
        {"session_id": "sess_q3", "event_id": "e4", "timestamp": "2026-11-17T12:00:03", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]

    res = hybrid.detect_session(events)
    assert res["fsm_violation"] is True
    assert res["prediction"] == "anomalous"
    # Mandatory academic invariant: risk score must be at least 60%
    assert res["risk_score"] >= 60, f"Expected risk_score >= 60 for FSM violation, got {res['risk_score']}"
    assert res["severity"] in ["high", "critical"]


def test_quadrant_4_compound_violation():
    """Quadrant 4: Both FSM violation and high ML anomaly score."""
    class MockCriticalMLEngine:
        def predict_session(self, events):
            return {"anomaly_score": 0.95, "prediction": "anomalous"}

    fsm = FSMEngine()
    mock_ml = MockCriticalMLEngine()
    hybrid = HybridEngine(fsm_engine=fsm, ml_engine=mock_ml, fsm_weight=0.6, ml_weight=0.4)

    events = [
        {"session_id": "sess_q4", "event_id": "e1", "timestamp": "2026-11-17T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "sess_q4", "event_id": "e2", "timestamp": "2026-11-17T12:00:01", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1500},
    ]

    res = hybrid.detect_session(events)
    assert res["fsm_violation"] is True
    assert res["prediction"] == "anomalous"
    # 0.6 * 60 + 0.4 * 95 = 74 >= 60 floor
    assert res["risk_score"] >= 70
    assert res["severity"] in ["high", "critical"]
