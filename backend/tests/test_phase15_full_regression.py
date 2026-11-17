"""Comprehensive Phase 15 Regression Suite for TraceGuard AI."""
from datetime import datetime, timedelta
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from scapy.all import IP, TCP, Raw, wrpcap

from app.main import app
from app.core.config import settings
from app.db.database import SessionLocal
from app.models.models import Alert, NetworkEvent, User
from app.network.pcap_parser import PacketParser
from app.network.pipeline import IngestionPipeline
from app.network.capture_service import CaptureService

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    login_resp = client.post("/api/auth/login", json={"username": "demo", "password": "traceguard2024"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# 1. AUTOMATA LABORATORY DFA SIMULATION LIFECYCLE TESTS (ADVANCING BEYOND STAGE 2)
# ============================================================================

def test_automata_canonical_5_step_sequence():
    """Verify sequence of 5 symbols executes completely beyond stage 2 to acceptance."""
    payload = {
        "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"]
    }
    resp = client.post("/api/protocols/http/step-execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["steps"]) == 5
    # Stage 1: IDLE --CONNECT--> CONNECTED
    assert data["steps"][0]["step_number"] == 1
    assert data["steps"][0]["current_state"] == "IDLE"
    assert data["steps"][0]["symbol"] == "CONNECT"
    assert data["steps"][0]["next_state"] == "CONNECTED"
    assert data["steps"][0]["valid"] is True

    # Stage 2: CONNECTED --REQUEST--> REQUEST_RECEIVED
    assert data["steps"][1]["step_number"] == 2
    assert data["steps"][1]["current_state"] == "CONNECTED"
    assert data["steps"][1]["symbol"] == "REQUEST"
    assert data["steps"][1]["next_state"] == "REQUEST_RECEIVED"
    assert data["steps"][1]["valid"] is True

    # Stage 3: REQUEST_RECEIVED --AUTH_SUCCESS--> AUTH_CHECKED (Advances past Stage 2!)
    assert data["steps"][2]["step_number"] == 3
    assert data["steps"][2]["current_state"] == "REQUEST_RECEIVED"
    assert data["steps"][2]["symbol"] == "AUTH_SUCCESS"
    assert data["steps"][2]["next_state"] == "AUTH_CHECKED"
    assert data["steps"][2]["valid"] is True

    # Stage 4: AUTH_CHECKED --RESPONSE_200--> RESPONSE_SENT
    assert data["steps"][3]["step_number"] == 4
    assert data["steps"][3]["current_state"] == "AUTH_CHECKED"
    assert data["steps"][3]["symbol"] == "RESPONSE_200"
    assert data["steps"][3]["next_state"] == "RESPONSE_SENT"
    assert data["steps"][3]["valid"] is True

    # Stage 5: RESPONSE_SENT --CLOSE--> CLOSED
    assert data["steps"][4]["step_number"] == 5
    assert data["steps"][4]["current_state"] == "RESPONSE_SENT"
    assert data["steps"][4]["symbol"] == "CLOSE"
    assert data["steps"][4]["next_state"] == "CLOSED"
    assert data["steps"][4]["valid"] is True

    assert data["final_state"] == "CLOSED"
    assert data["verdict"] == "ACCEPTED"
    assert data["all_transitions_valid"] is True


def test_automata_pipelined_cyclic_8_step_sequence():
    """Verify cyclic keep-alive session advances through all 8 stages."""
    payload = {
        "events": [
            "CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200",
            "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"
        ]
    }
    resp = client.post("/api/protocols/http/step-execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["steps"]) == 8
    # Step 5 is cyclic pipelined request from RESPONSE_SENT back to REQUEST_RECEIVED
    assert data["steps"][4]["current_state"] == "RESPONSE_SENT"
    assert data["steps"][4]["symbol"] == "REQUEST"
    assert data["steps"][4]["next_state"] == "REQUEST_RECEIVED"
    assert data["steps"][4]["valid"] is True

    assert data["final_state"] == "CLOSED"
    assert data["verdict"] == "ACCEPTED"


def test_automata_valid_incomplete_prefix():
    """Verify valid incomplete prefix ends in INCOMPLETE_VALID with non-accepting terminal state."""
    payload = {
        "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS"]
    }
    resp = client.post("/api/protocols/http/step-execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["steps"]) == 3
    assert data["final_state"] == "AUTH_CHECKED"
    assert data["verdict"] == "INCOMPLETE_VALID"
    assert data["all_transitions_valid"] is True


def test_automata_out_of_order_violation_rejection():
    """Verify out-of-order response symbol is immediately rejected and enters TRAP."""
    payload = {
        "events": ["CONNECT", "RESPONSE_200", "REQUEST", "CLOSE"]
    }
    resp = client.post("/api/protocols/http/step-execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["steps"]) == 4
    # Step 2: Premature response in CONNECTED state transitions to TRAP
    assert data["steps"][1]["symbol"] == "RESPONSE_200"
    assert data["steps"][1]["valid"] is False
    assert data["steps"][1]["next_state"] == "TRAP"
    assert data["verdict"] == "REJECTED"


def test_automata_empty_sequence():
    """Verify empty sequence returns zero steps cleanly with IDLE state."""
    payload = {"events": []}
    resp = client.post("/api/protocols/http/step-execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["steps"]) == 0
    assert data["final_state"] == "IDLE"
    assert data["verdict"] == "INCOMPLETE_VALID"


# ============================================================================
# 2. ENGINE CLASSIFICATION & AGGREGATION PROVENANCE TESTS
# ============================================================================

def test_engine_classification_provenance(auth_headers):
    """Verify FSM, ML, and Hybrid engines are individually tracked and aggregated."""
    db = SessionLocal()
    workspace_id = "default-workspace"

    # Insert test alerts for each engine
    fsm_alert = Alert(
        workspace_id=workspace_id,
        alert_id=f"alrt_test_fsm_{os.urandom(4).hex()}",
        session_id="sess_fsm_1",
        engine="fsm",
        severity="high",
        risk_score=75,
        prediction="anomalous",
        status="new",
        summary="Deterministic FSM protocol violation",
        fsm_result={"fsm_violation": True},
        timestamp=datetime.utcnow()
    )
    ml_alert = Alert(
        workspace_id=workspace_id,
        alert_id=f"alrt_test_ml_{os.urandom(4).hex()}",
        session_id="sess_ml_1",
        engine="ml",
        severity="medium",
        risk_score=45,
        prediction="anomalous",
        status="new",
        summary="Statistical Isolation Forest outlier",
        ml_result={"prediction": "anomalous", "anomaly_score": 0.65},
        timestamp=datetime.utcnow()
    )
    hybrid_alert = Alert(
        workspace_id=workspace_id,
        alert_id=f"alrt_test_hyb_{os.urandom(4).hex()}",
        session_id="sess_hyb_1",
        engine="hybrid",
        severity="critical",
        risk_score=92,
        prediction="anomalous",
        status="new",
        summary="Hybrid consensus detected dual deviation",
        fsm_result={"fsm_violation": True},
        ml_result={"prediction": "anomalous", "anomaly_score": 0.8},
        timestamp=datetime.utcnow()
    )
    db.add_all([fsm_alert, ml_alert, hybrid_alert])
    db.commit()

    try:
        # Check dashboard summary
        resp = client.get("/api/dashboard/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()

        dist = data["engine_distribution"]
        assert dist["fsm"] >= 1
        assert dist["ml"] >= 1
        assert dist["hybrid"] >= 1
        assert "unknown" in dist

        # Verify time range filtering works
        resp_24h = client.get("/api/dashboard/summary?time_range=24h", headers=auth_headers)
        assert resp_24h.status_code == 200
        dist_24h = resp_24h.json()["engine_distribution"]
        assert dist_24h["fsm"] >= 1

    finally:
        db.delete(fsm_alert)
        db.delete(ml_alert)
        db.delete(hybrid_alert)
        db.commit()
        db.close()


# ============================================================================
# 3. THREAT FORENSICS ANALYTICS & TIMELINE INTEGRITY TESTS
# ============================================================================

def test_threat_forensics_analytics_endpoint(auth_headers):
    """Verify forensic analytics distributions reconcile and provide protocol & risk breakdown."""
    resp = client.get("/api/alerts/analytics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert "total_alerts" in data
    assert "avg_risk_score" in data
    assert "severity_distribution" in data
    assert "engine_distribution" in data
    assert "risk_distribution" in data
    assert "engine_correlation" in data
    assert "time_series" in data
    assert "protocol_distribution" in data

    # Verify risk bands cover complete distribution
    assert "0-25 (Low)" in data["risk_distribution"]
    assert "26-50 (Med)" in data["risk_distribution"]
    assert "51-75 (High)" in data["risk_distribution"]
    assert "76-100 (Crit)" in data["risk_distribution"]


def test_alert_detail_chronological_timeline(auth_headers):
    """Verify alert detail returns chronological session events for forensic reconstruction."""
    db = SessionLocal()
    test_session = f"sess_timeline_{os.urandom(4).hex()}"

    ev1 = NetworkEvent(
        workspace_id="default-workspace",
        event_id=f"evt_1_{os.urandom(3).hex()}",
        session_id=test_session,
        timestamp=datetime.utcnow() - timedelta(seconds=10),
        protocol="HTTP",
        event_type="CONNECT",
        source="192.168.1.100:54321",
        destination="192.168.1.1:80",
        bytes=54
    )
    ev2 = NetworkEvent(
        workspace_id="default-workspace",
        event_id=f"evt_2_{os.urandom(3).hex()}",
        session_id=test_session,
        timestamp=datetime.utcnow() - timedelta(seconds=5),
        protocol="HTTP",
        event_type="REQUEST",
        source="192.168.1.100:54321",
        destination="192.168.1.1:80",
        method="GET",
        path_category="api",
        bytes=312
    )
    alrt = Alert(
        workspace_id="default-workspace",
        alert_id=f"alrt_timeline_{os.urandom(4).hex()}",
        session_id=test_session,
        engine="hybrid",
        severity="medium",
        risk_score=40,
        prediction="anomalous",
        status="new",
        responsible_events=[ev2.event_id],
        timestamp=datetime.utcnow()
    )
    db.add_all([ev1, ev2, alrt])
    db.commit()

    try:
        resp = client.get(f"/api/alerts/{alrt.alert_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()

        assert data["alert_id"] == alrt.alert_id
        assert data["session_id"] == test_session
        assert len(data["events"]) == 2
        # Events must be chronologically ordered
        assert data["events"][0]["event_type"] == "CONNECT"
        assert data["events"][1]["event_type"] == "REQUEST"
        assert ev2.event_id in data["responsible_events"]

    finally:
        db.delete(ev1)
        db.delete(ev2)
        db.delete(alrt)
        db.commit()
        db.close()


# ============================================================================
# 4. AUTHENTICATION & SESSION INVALIDATION TESTS
# ============================================================================

def test_auth_login_and_logout_flow():
    """Verify login provisions token and logout endpoint invalidates session cleanly."""
    login_resp = client.post("/api/auth/login", json={"username": "demo", "password": "traceguard2024"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token is not None

    # Access protected profile
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "demo"

    # Invalidate session via logout endpoint
    logout_resp = client.post("/api/auth/logout", headers=headers)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "logged_out"

    # Attempting to access without token fails when auth enforced (PRODUCTION mode)
    original_mode = settings.LOCAL_ACADEMIC_MODE
    try:
        settings.LOCAL_ACADEMIC_MODE = False
        unauth_resp = client.get("/api/auth/me")
        assert unauth_resp.status_code == 401
    finally:
        settings.LOCAL_ACADEMIC_MODE = original_mode


# ============================================================================
# 5. LIVE NETWORK & PCAP PARSING TESTS
# ============================================================================

def test_pcap_safe_ingestion_and_privacy():
    """Verify PCAP parser respects privacy, redacting credentials and generating valid sessions."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        # Create a packet with sensitive authorization header
        auth_req = "GET /api/v1/keys HTTP/1.1\r\nHost: traceguard\r\nAuthorization: Bearer supersecrettoken123\r\nCookie: sessionid=secretcookie\r\n\r\n"
        pkt1 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=60000, dport=80, flags="S", seq=1)
        pkt2 = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=60000, dport=80, flags="PA", seq=2, ack=1) / Raw(load=auth_req.encode())
        wrpcap(tmp_name, [pkt1, pkt2])

        events = PacketParser.parse_pcap_file(tmp_name)
        assert len(events) >= 1

        # Confirm sensitive strings are nowhere in event records
        events_str = str(events)
        assert "supersecrettoken123" not in events_str
        assert "secretcookie" not in events_str
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
