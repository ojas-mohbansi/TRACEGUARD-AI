"""Integration tests for TraceGuard AI."""

import io
import json
import pytest
import requests
from uuid import uuid4
from pathlib import Path
import pandas as pd

from backend.app.detection.fsm import FSMEngine
from backend.app.detection.ml import MLEngine
from backend.app.detection.hybrid import HybridEngine
from backend.app.detection.features.extractor import FeatureExtractor


BASE_URL = "http://127.0.0.1:8000"


def get_auth_context():
    """Obtain valid JWT and workspace headers for integration testing."""
    try:
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "demo", "password": "traceguard2024"},
            timeout=5.0
        )
        if login_res.status_code == 200:
            token = login_res.json()["access_token"]
            return {"Authorization": f"Bearer {token}", "X-Workspace-ID": "default-workspace"}
    except Exception:
        pass
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": "demo"})
    return {"Authorization": f"Bearer {token}", "X-Workspace-ID": "default-workspace"}


def test_three_engines_detection_on_session():
    """1. Run detection on a session through all three engines."""
    fsm = FSMEngine()
    ml = MLEngine()
    hybrid = HybridEngine(fsm_engine=fsm, ml_engine=ml, fsm_weight=0.6, ml_weight=0.4)

    events = [
        {"session_id": "sess_int_1", "timestamp": "2026-11-13T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "sess_int_1", "timestamp": "2026-11-13T12:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 200},
        {"session_id": "sess_int_1", "timestamp": "2026-11-13T12:00:02", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1000},  # Invalid FSM transition: skips auth!
        {"session_id": "sess_int_1", "timestamp": "2026-11-13T12:00:03", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]

    # 1. FSM Engine
    fsm_res = fsm.validate_session(events)
    assert fsm_res["engine"] == "fsm"
    assert fsm_res["prediction"] == "anomalous"
    assert fsm_res["fsm_violation"] is True

    # 2. ML Engine (via feature extraction & predict)
    extractor = FeatureExtractor()
    feat = extractor.extract_session_features(events)
    feat["session_id"] = "sess_int_1"
    ml_res_list = ml.predict([feat])
    assert len(ml_res_list) == 1
    ml_res = ml_res_list[0]
    assert ml_res["engine"] == "ml"
    assert "ml_anomaly_score" in ml_res
    assert 0.0 <= ml_res["ml_anomaly_score"] <= 1.0

    # 3. Hybrid Engine
    hybrid_res = hybrid.detect_session(events)
    assert hybrid_res["engine"] == "hybrid"
    assert hybrid_res["fsm_violation"] is True
    assert hybrid_res["prediction"] == "anomalous"
    assert hybrid_res["risk_score"] >= 60


def test_hybrid_score_combines_fsm_and_ml():
    """2. Verify hybrid score combines FSM and ML correctly."""
    fsm = FSMEngine()
    ml = MLEngine()
    hybrid = HybridEngine(fsm_engine=fsm, ml_engine=ml, fsm_weight=0.6, ml_weight=0.4)

    # Valid session
    valid_events = [
        {"session_id": "sess_valid", "timestamp": "2026-11-13T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "sess_valid", "timestamp": "2026-11-13T12:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 200},
        {"session_id": "sess_valid", "timestamp": "2026-11-13T12:00:02", "event_type": "AUTH_SUCCESS", "method": "GET", "status_code": 0, "bytes": 50},
        {"session_id": "sess_valid", "timestamp": "2026-11-13T12:00:03", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1000},
        {"session_id": "sess_valid", "timestamp": "2026-11-13T12:00:04", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]

    res = hybrid.detect_session(valid_events)
    assert res["fsm_violation"] is False
    assert res["prediction"] == "normal"
    assert res["risk_score"] < 40


def test_alerts_created_and_stored_in_db():
    """3. Verify alerts are created and stored in database."""
    # 3a. Unauthenticated access check (200 in LOCAL_ACADEMIC mode, 401 in PRODUCTION mode)
    r_unauth = requests.get(f"{BASE_URL}/api/alerts?limit=10")
    assert r_unauth.status_code in (200, 401), f"Unexpected status code: {r_unauth.status_code}"

    # 3b. Authenticated request with valid JWT and workspace headers
    headers = get_auth_context()
    r_alerts = requests.get(f"{BASE_URL}/api/alerts?limit=10", headers=headers)
    assert r_alerts.status_code == 200
    data = r_alerts.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)

    if len(data["alerts"]) == 0:
        # Populate an alert by triggering simulation or running detection
        requests.post(
            f"{BASE_URL}/api/simulation/start",
            json={"duration": 2, "mode": "anomalous", "event_count": 20, "speed": 0.01},
            headers=headers
        )
        import time
        for _ in range(20):
            time.sleep(0.5)
            r_check = requests.get(f"{BASE_URL}/api/alerts?limit=10", headers=headers)
            if r_check.status_code == 200 and len(r_check.json().get("alerts", [])) > 0:
                data = r_check.json()
                break

    assert len(data["alerts"]) > 0, "Expected at least one alert in database"

    alert = data["alerts"][0]
    assert "alert_id" in alert
    assert "session_id" in alert
    assert "severity" in alert
    assert "engine" in alert
    assert "risk_score" in alert

    # Check alert detail
    alert_id = alert["alert_id"]
    r_detail = requests.get(f"{BASE_URL}/api/alerts/{alert_id}", headers=headers)
    assert r_detail.status_code == 200
    detail = r_detail.json()
    assert detail["alert_id"] == alert_id
    assert "events" in detail



def test_websocket_receives_events_on_simulation():
    """4. Verify WebSocket receives events when simulation runs."""
    import asyncio
    import websockets

    # 4a. Unauthenticated access check (200 in LOCAL_ACADEMIC mode, 401 in PRODUCTION mode)
    r_unauth = requests.post(f"{BASE_URL}/api/simulation/start", json={"duration": 2, "mode": "mixed"})
    assert r_unauth.status_code in (200, 401), f"Unexpected status code: {r_unauth.status_code}"

    # 4b. Authenticated simulation trigger
    headers = get_auth_context()

    async def check_ws():
        uri = f"ws://127.0.0.1:8000/ws/events"
        async with websockets.connect(uri) as ws:
            # Trigger simulation run with authenticated headers
            requests.post(
                f"{BASE_URL}/api/simulation/start",
                json={"duration": 2, "mode": "mixed", "event_count": 50, "speed": 0.05},
                headers=headers
            )
            msg = await asyncio.wait_for(ws.recv(), timeout=15.0)
            data = json.loads(msg)
            assert data is not None
            assert "type" in data or "event_type" in data

    asyncio.run(check_ws())


def test_csv_upload_works():
    """5. Verify CSV upload works."""
    # 5a. Unauthenticated access check (200 in LOCAL_ACADEMIC mode, 401 in PRODUCTION mode)
    r_unauth = requests.post(f"{BASE_URL}/api/datasets/upload", data={"name": "test"})
    assert r_unauth.status_code in (200, 401, 422), f"Unexpected status code: {r_unauth.status_code}"

    # 5b. Authenticated upload
    headers = get_auth_context()
    root_dir = Path(__file__).resolve().parent.parent.parent
    csv_path = root_dir / "datasets" / "synthetic" / "test_data.csv"
    assert csv_path.exists()

    df = pd.read_csv(csv_path)
    prefix = uuid4().hex[:6]
    df["event_id"] = [f"evt_verify_{prefix}_{i}" for i in range(len(df))]
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    r_up = requests.post(
        f"{BASE_URL}/api/datasets/upload",
        data={"name": f"verify_upload_{prefix}", "description": "Verification test upload"},
        files={"file": (f"test_data_{prefix}.csv", io.BytesIO(csv_bytes), "text/csv")},
        headers=headers
    )
    assert r_up.status_code in [200, 201]
    res = r_up.json()
    assert "dataset_id" in res
    assert res["event_count"] > 0
    assert res["session_count"] > 0


def test_detection_comparison_produces_valid_metrics():
    """6. Verify detection comparison produces valid metrics."""
    # 6a. Unauthenticated access check (200 in LOCAL_ACADEMIC mode, 401 in PRODUCTION mode)
    r_unauth = requests.get(f"{BASE_URL}/api/datasets")
    assert r_unauth.status_code in (200, 401), f"Unexpected status code: {r_unauth.status_code}"

    # 6b. Authenticated access
    headers = get_auth_context()
    r_ds = requests.get(f"{BASE_URL}/api/datasets", headers=headers)
    assert r_ds.status_code == 200
    datasets = r_ds.json().get("datasets", [])

    if len(datasets) == 0:
        # Upload a dataset first if empty in clean runner
        root_dir = Path(__file__).resolve().parent.parent.parent
        csv_path = root_dir / "datasets" / "synthetic" / "test_data.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            prefix = uuid4().hex[:6]
            df["event_id"] = [f"evt_init_{prefix}_{i}" for i in range(len(df))]
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            r_seed = requests.post(
                f"{BASE_URL}/api/datasets/upload",
                data={"name": f"seed_data_{prefix}", "description": "Seed dataset for comparison"},
                files={"file": (f"seed_{prefix}.csv", io.BytesIO(buf.getvalue().encode("utf-8")), "text/csv")},
                headers=headers
            )
            if r_seed.status_code in [200, 201]:
                datasets = [r_seed.json()]

    assert len(datasets) > 0, "Expected at least one dataset available for comparison"

    ds_id = datasets[0]["dataset_id"]
    r_comp = requests.get(f"{BASE_URL}/api/detection/compare?dataset_id={ds_id}", headers=headers)
    assert r_comp.status_code == 200
    comp = r_comp.json()
    assert comp["dataset_id"] == ds_id
    assert "engines" in comp

    assert "fsm" in comp["engines"]
    assert "ml" in comp["engines"]
    assert "hybrid" in comp["engines"]

    for eng in ["fsm", "ml", "hybrid"]:
        metrics = comp["engines"][eng]
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "detection_rate" in metrics
        assert "false_positive_rate" in metrics
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
        assert 0.0 <= metrics["f1_score"] <= 1.0


def test_hybrid_engine_four_detection_quadrants():
    """7. Verify Hybrid Engine across 4 distinct quadrants:
    A. Normal traffic (clean sequence, normal ML profile) -> normal, low risk
    B. FSM-only violation (skipping auth, but benign-looking bytes/timing) -> anomalous, risk >= 60 floor
    C. ML-only anomaly (conforming sequence, but anomalous rate/bytes/failures) -> elevated risk from ML
    D. Combined violation (invalid transitions + extreme anomaly) -> critical risk >= 80
    """
    fsm = FSMEngine()
    ml = MLEngine()
    hybrid = HybridEngine(fsm_engine=fsm, ml_engine=ml, fsm_weight=0.6, ml_weight=0.4)

    # Quadrant A: Normal traffic
    quad_a = [
        {"session_id": "quad_a", "timestamp": "2026-11-13T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "quad_a", "timestamp": "2026-11-13T12:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 200},
        {"session_id": "quad_a", "timestamp": "2026-11-13T12:00:02", "event_type": "AUTH_SUCCESS", "method": "GET", "status_code": 0, "bytes": 50},
        {"session_id": "quad_a", "timestamp": "2026-11-13T12:00:03", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 1000},
        {"session_id": "quad_a", "timestamp": "2026-11-13T12:00:04", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]
    res_a = hybrid.detect_session(quad_a)
    assert res_a["fsm_violation"] is False
    assert res_a["prediction"] == "normal"
    assert res_a["risk_score"] < 40

    # Quadrant B: FSM-only violation
    quad_b = [
        {"session_id": "quad_b", "timestamp": "2026-11-13T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "quad_b", "timestamp": "2026-11-13T12:00:01", "event_type": "RESPONSE_200", "method": "GET", "status_code": 200, "bytes": 500}, # Auth skipped!
        {"session_id": "quad_b", "timestamp": "2026-11-13T12:00:02", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]
    res_b = hybrid.detect_session(quad_b)
    assert res_b["fsm_violation"] is True
    assert res_b["prediction"] == "anomalous"
    assert res_b["risk_score"] >= 60  # Minimum floor enforced

    # Quadrant C: ML anomaly independent influence
    # Conforms to FSM transitions, but has unusual attributes
    quad_c = [
        {"session_id": "quad_c", "timestamp": "2026-11-13T12:00:00", "event_type": "CONNECT", "method": "CONNECT", "status_code": 0, "bytes": 100},
        {"session_id": "quad_c", "timestamp": "2026-11-13T12:00:01", "event_type": "REQUEST", "method": "GET", "status_code": 0, "bytes": 200},
        {"session_id": "quad_c", "timestamp": "2026-11-13T12:00:02", "event_type": "AUTH_SUCCESS", "method": "GET", "status_code": 0, "bytes": 50},
        {"session_id": "quad_c", "timestamp": "2026-11-13T12:00:03", "event_type": "RESPONSE_500", "method": "GET", "status_code": 500, "bytes": 5000000}, # Heavy 500
        {"session_id": "quad_c", "timestamp": "2026-11-13T12:00:04", "event_type": "ERROR_RESPONSE", "method": "GET", "status_code": 500, "bytes": 5000000},
        {"session_id": "quad_c", "timestamp": "2026-11-13T12:00:05", "event_type": "CLOSE", "method": "CLOSE", "status_code": 0, "bytes": 50},
    ]
    res_c = hybrid.detect_session(quad_c)
    assert res_c["fsm_violation"] is False  # Sequence is valid in FSM
    assert res_c["ml_anomaly_score"] > 0.5   # Flagged by ML
    assert res_c["risk_score"] > res_a["risk_score"]  # ML elevated the risk

    # Quadrant D: Combined violation
    quad_d = [
        {"session_id": "quad_d", "timestamp": "2026-11-13T12:00:00", "event_type": "RESPONSE_500", "method": "POST", "status_code": 500, "bytes": 9999999},
        {"session_id": "quad_d", "timestamp": "2026-11-13T12:00:01", "event_type": "AUTH_FAILURE", "method": "POST", "status_code": 401, "bytes": 9999999},
    ]
    res_d = hybrid.detect_session(quad_d)
    assert res_d["fsm_violation"] is True
    assert res_d["risk_score"] >= 80
    assert res_d["severity"] in ["high", "critical"]


def test_run_detection_with_dataset_id_and_empty_sessions():
    """Verify run_detection resolves distinct session IDs when dataset_id is supplied without session_ids."""
    from app.db.database import SessionLocal
    from app.api.detection import run_detection
    from app.schemas.detection import DetectionRequest
    from app.models.models import Dataset, NetworkEvent
    from datetime import datetime

    db = SessionLocal()
    try:
        # Create a test dataset with 2 sessions
        ds_id = f"ds_test_{uuid4().hex[:8]}"
        ev1 = NetworkEvent(
            workspace_id="default-workspace",
            event_id=f"evt_{uuid4().hex[:8]}",
            session_id=f"sess_t1_{uuid4().hex[:6]}",
            dataset_id=ds_id,
            timestamp=datetime.utcnow(),
            event_type="CONNECT",
            source="192.168.1.1",
            destination="10.0.0.1",
            label="normal"
        )
        ev2 = NetworkEvent(
            workspace_id="default-workspace",
            event_id=f"evt_{uuid4().hex[:8]}",
            session_id=f"sess_t2_{uuid4().hex[:6]}",
            dataset_id=ds_id,
            timestamp=datetime.utcnow(),
            event_type="CONNECT",
            source="192.168.1.2",
            destination="10.0.0.1",
            label="normal"
        )
        db.add(ev1)
        db.add(ev2)
        db.commit()

        req = DetectionRequest(session_ids=[], engines=["fsm"], dataset_id=ds_id)
        res = run_detection(req, db)
        assert len(res.results) >= 2
        returned_sessions = {r.session_id for r in res.results}
        assert ev1.session_id in returned_sessions
        assert ev2.session_id in returned_sessions
    finally:
        db.query(NetworkEvent).filter(NetworkEvent.dataset_id == ds_id).delete()
        db.commit()
        db.close()


def test_alert_detail_response_schema_fields():
    """Verify AlertDetailResponse includes summary, fsm_violation, ml_anomaly_score, responsible_events."""
    from app.schemas.alerts import AlertDetailResponse
    from datetime import datetime

    detail = AlertDetailResponse(
        alert_id="alrt_test_123",
        session_id="sess_test_123",
        timestamp=datetime.utcnow(),
        engine="hybrid",
        severity="high",
        risk_score=75,
        prediction="anomalous",
        status="new",
        summary="DFA sequence rejected",
        fsm_violation=True,
        ml_anomaly_score=0.85,
        responsible_events=["evt_1", "evt_2"],
        processing_time_ms=12.5
    )
    dumped = detail.model_dump()
    assert dumped["summary"] == "DFA sequence rejected"
    assert dumped["fsm_violation"] is True
    assert dumped["ml_anomaly_score"] == 0.85
    assert dumped["responsible_events"] == ["evt_1", "evt_2"]
    assert dumped["processing_time_ms"] == 12.5


