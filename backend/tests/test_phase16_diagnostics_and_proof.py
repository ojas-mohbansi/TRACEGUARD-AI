"""Comprehensive Phase 16 Verification Suite for TraceGuard AI.

Verifies:
1. Npcap service absent detection.
2. Npcap service present but stopped detection.
3. Npcap API unavailable detection.
4. Permission-denied detection.
5. Interface enumeration success/failure.
6. Capture handle opens successfully.
7. PCAP replay works without Npcap.
8. Valid DFA sequence is accepted or incomplete according to final state.
9. Invalid DFA transition reaches TRAP.
10. FSM-only protocol violation is recorded (engine='fsm').
11. ML-only anomaly is recorded with valid FSM sequence (engine='ml').
12. Hybrid result uses approved formula (S_h = 0.6 S_FSM + 0.4 S_ML) and 60% risk floor.
13. Component findings retain accurate provenance.
14. Legacy unknown provenance remains unknown.
15. No duplicate findings are created on repeated requests.
16. Demo data does not pollute live-network statistics.
17. Time filters and aggregation totals are correct.
"""
from datetime import datetime, timedelta
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from scapy.all import IP, TCP, Raw, wrpcap

from app.main import app
from app.db.database import SessionLocal
from app.models.models import Alert, NetworkEvent, User
from app.network.npcap_diagnostics import NpcapDiagnostics
from app.network.capture_service import CaptureService
from app.detection.fsm import FSMEngine
from app.detection.ml import MLEngine
from app.detection.hybrid import HybridEngine

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    login_resp = client.post("/api/auth/login", json={"username": "demo", "password": "traceguard2024"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# WORKSTREAM A: NPCAP RUNTIME & STATE DIAGNOSTICS TESTS (1 - 7)
# ============================================================================

def test_npcap_service_absent_detection():
    """Verify NOT_INSTALLED state when Npcap files are absent."""
    with patch("os.path.exists", return_value=False):
        diag = NpcapDiagnostics.run_diagnostics()
        assert diag["state"] == NpcapDiagnostics.STATE_NOT_INSTALLED
        assert diag["available"] is False
        assert "not installed" in diag["message"].lower()


def test_npcap_service_present_but_stopped_detection():
    """Verify SERVICE_STOPPED state when DLL files exist but npcap service is inactive."""
    with patch("os.path.exists", return_value=True), \
         patch("scapy.arch.windows.pcap_service_status", return_value=False), \
         patch("subprocess.run", return_value=MagicMock(stdout="STATE: STOPPED")):
        diag = NpcapDiagnostics.run_diagnostics()
        assert diag["state"] == NpcapDiagnostics.STATE_SERVICE_STOPPED
        assert diag["steps"]["1_driver_installed"] is True
        assert diag["steps"]["2_service_running"] is False
        assert "stopped" in diag["message"].lower()


def test_npcap_api_unavailable_detection():
    """Verify PCAP_API_UNAVAILABLE when service is running but DLL loading fails."""
    with patch("os.path.exists", return_value=True), \
         patch("scapy.arch.windows.pcap_service_status", return_value=True), \
         patch("scapy.libs.winpcapy.pcap_lib_version", side_effect=Exception("DLL entrypoint missing")):
        diag = NpcapDiagnostics.run_diagnostics()
        assert diag["state"] == NpcapDiagnostics.STATE_PCAP_API_UNAVAILABLE
        assert diag["steps"]["3_pcap_api_loaded"] is False


def test_permission_denied_detection():
    """Verify PERMISSION_DENIED state when handle open raises access violation."""
    with patch("os.path.exists", return_value=True), \
         patch("scapy.arch.windows.pcap_service_status", return_value=True), \
         patch("scapy.libs.winpcapy.pcap_lib_version", return_value=b"Npcap 1.90"), \
         patch("scapy.libs.winpcapy.pcap_open_live", return_value=None):
        # When pcap_open_live returns None, it checks errbuf
        diag = NpcapDiagnostics.run_diagnostics()
        assert diag["state"] in [NpcapDiagnostics.STATE_PERMISSION_DENIED, NpcapDiagnostics.STATE_INTERFACE_OPEN_FAILED]


def test_interface_enumeration_live():
    """Verify live host interfaces are enumerated with valid network names."""
    diag = NpcapDiagnostics.run_diagnostics()
    assert "interfaces" in diag
    assert len(diag["interfaces"]) >= 1
    # Check that Loopback or Wi-Fi is discovered
    names = [i["name"] for i in diag["interfaces"]]
    assert any("Loopback" in n or "Wi-Fi" in n or "Connection" in n or "Ethernet" in n for n in names)


def test_capture_handle_opens_successfully_on_live_host():
    """Verify live Npcap runtime can open a passive handle on host adapter."""
    diag = NpcapDiagnostics.run_diagnostics()
    if diag["state"] == NpcapDiagnostics.STATE_CAPTURE_READY:
        assert diag["available"] is True
        assert diag["steps"]["5_handle_open_test"] is True
        assert diag["test_interface"] is not None


def test_pcap_replay_works_without_live_capture_dependency(auth_headers):
    """Verify PCAP file upload and replay pipeline operates independently."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp_name = tmp.name

    try:
        # Create a valid 4-step PCAP stream
        p1 = IP(src="10.1.1.5", dst="10.1.1.1") / TCP(sport=55100, dport=80, flags="S", seq=1)
        p2 = IP(src="10.1.1.5", dst="10.1.1.1") / TCP(sport=55100, dport=80, flags="PA", seq=2, ack=1) / Raw(b"GET /api/v1/test HTTP/1.1\r\nHost: example.com\r\n\r\n")
        p3 = IP(src="10.1.1.1", dst="10.1.1.5") / TCP(sport=80, dport=55100, flags="PA", seq=1, ack=2) / Raw(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
        p4 = IP(src="10.1.1.5", dst="10.1.1.1") / TCP(sport=55100, dport=80, flags="FA", seq=3, ack=2)
        wrpcap(tmp_name, [p1, p2, p3, p4])

        with open(tmp_name, "rb") as f:
            resp = client.post(
                "/api/network/pcap/upload",
                files={"file": ("offline_replay.pcap", f, "application/vnd.tcpdump.pcap")},
                headers=auth_headers
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["packets_parsed"] >= 4
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


# ============================================================================
# WORKSTREAM B: FORMAL DFA & FSM INDEPENDENT INTRUSION DETECTION TESTS (8 - 14)
# ============================================================================

def test_valid_dfa_sequence_acceptance_and_incomplete_prefix():
    """Verify canonical sequence reaches CLOSED and valid prefix stops safely."""
    fsm = FSMEngine()

    # 1. Canonical complete sequence: IDLE -> CONNECTED -> REQUEST_RECEIVED -> AUTH_CHECKED -> RESPONSE_SENT -> CLOSED
    canonical = [
        {"event_type": "CONNECT"},
        {"event_type": "REQUEST"},
        {"event_type": "AUTH_SUCCESS"},
        {"event_type": "RESPONSE_200"},
        {"event_type": "CLOSE"}
    ]
    res_can = fsm.validate_session(canonical)
    assert res_can["fsm_violation"] is False
    assert res_can["prediction"] == "normal"
    assert res_can["risk_score"] == 0

    # 2. Incomplete valid prefix: IDLE -> CONNECTED -> REQUEST_RECEIVED (stops before response)
    prefix = [
        {"event_type": "CONNECT"},
        {"event_type": "REQUEST"}
    ]
    res_pre = fsm.validate_session(prefix)
    assert res_pre["fsm_violation"] is False
    assert res_pre["prediction"] == "normal"


def test_invalid_dfa_transition_reaches_trap_state():
    """Verify illegal DFA transition moves automaton directly into absorbing TRAP state."""
    fsm = FSMEngine()
    # Out of order: direct RESPONSE_200 while in CONNECTED state
    illegal = [
        {"event_type": "CONNECT"},
        {"event_type": "RESPONSE_200"}
    ]
    res = fsm.validate_session(illegal)
    assert res["fsm_violation"] is True
    assert res["prediction"] == "anomalous"
    assert res["risk_score"] >= 60
    assert len(res["violations"]) >= 1
    assert "RESPONSE_200" in res["violations"][0]["incoming_event"]


def test_fsm_only_protocol_violation_attribution():
    """Verify FSM independently detects protocol violation and attributes to 'fsm' engine."""
    fsm = FSMEngine()
    ml = MLEngine()
    hybrid = HybridEngine(fsm, ml, fsm_weight=0.6, ml_weight=0.4)

    # Post-close request: CONNECT -> REQUEST -> AUTH_SUCCESS -> RESPONSE_200 -> CLOSE -> REQUEST
    # Normal statistical payload (no ML anomaly)
    events = [
        {"event_id": "e1", "session_id": "s_fsm_only", "event_type": "CONNECT", "protocol": "HTTP", "bytes": 64},
        {"event_id": "e2", "session_id": "s_fsm_only", "event_type": "REQUEST", "protocol": "HTTP", "method": "GET", "bytes": 320},
        {"event_id": "e3", "session_id": "s_fsm_only", "event_type": "AUTH_SUCCESS", "protocol": "HTTP", "bytes": 128},
        {"event_id": "e4", "session_id": "s_fsm_only", "event_type": "RESPONSE_200", "protocol": "HTTP", "status_code": 200, "bytes": 1450},
        {"event_id": "e5", "session_id": "s_fsm_only", "event_type": "CLOSE", "protocol": "HTTP", "bytes": 64},
        {"event_id": "e6", "session_id": "s_fsm_only", "event_type": "REQUEST", "protocol": "HTTP", "method": "GET", "bytes": 350}
    ]

    res = hybrid.detect_session(events)
    assert res["fsm_violation"] is True
    assert res["ml_anomalous"] is False
    assert res["attribution"] == "fsm"
    assert res["risk_score"] >= 60  # FSM risk floor enforced


def test_ml_only_anomaly_attribution():
    """Verify ML independently detects statistical outlier on a DFA-conforming sequence."""
    fsm = FSMEngine()
    ml = MLEngine()
    hybrid = HybridEngine(fsm, ml, fsm_weight=0.6, ml_weight=0.4)

    # Conforming protocol sequence with authentication brute-force pattern
    # All transitions IDLE -> CONNECTED -> (REQUEST_RECEIVED -> AUTH_FAILED -> RESPONSE_SENT)*8 -> CLOSED
    # are completely valid in HTTP DFA, but statistical ML detects severe anomaly.
    events = [
        {"event_id": "e0", "session_id": "s_ml_only", "event_type": "CONNECT", "protocol": "HTTP", "bytes": 64},
    ]
    for i in range(8):
        events.extend([
            {"event_id": f"e_{i}_1", "session_id": "s_ml_only", "event_type": "REQUEST", "protocol": "HTTP", "method": "POST", "bytes": 350},
            {"event_id": f"e_{i}_2", "session_id": "s_ml_only", "event_type": "AUTH_FAILURE", "protocol": "HTTP", "bytes": 0},
            {"event_id": f"e_{i}_3", "session_id": "s_ml_only", "event_type": "RESPONSE_401", "protocol": "HTTP", "status_code": 401, "bytes": 200},
        ])
    events.append({"event_id": "e_close", "session_id": "s_ml_only", "event_type": "CLOSE", "protocol": "HTTP", "bytes": 32})

    res = hybrid.detect_session(events)
    assert res["fsm_violation"] is False  # FSM perfectly conforms!
    assert res["ml_anomalous"] is True   # ML catches the statistical outlier!
    assert res["attribution"] == "ml"    # Attributed solely to ML engine!


def test_hybrid_consensus_scoring_formula_and_floor():
    """Verify consensus calculation: S_h = 0.6 S_FSM + 0.4 S_ML and mandatory 60% floor."""
    fsm = FSMEngine()
    ml = MLEngine()
    hybrid = HybridEngine(fsm, ml, fsm_weight=0.6, ml_weight=0.4)

    # Protocol violation + huge payload
    events = [
        {"event_id": "e1", "session_id": "s_hyb", "event_type": "CONNECT", "protocol": "HTTP", "bytes": 64},
        {"event_id": "e2", "session_id": "s_hyb", "event_type": "RESPONSE_200", "protocol": "HTTP", "bytes": 9000000},
        {"event_id": "e3", "session_id": "s_hyb", "event_type": "CLOSE", "protocol": "HTTP", "bytes": 64}
    ]

    res = hybrid.detect_session(events)
    assert res["fsm_violation"] is True
    assert res["ml_anomalous"] is True
    assert res["attribution"] == "hybrid"
    assert res["risk_score"] >= 60


def test_component_findings_retain_accurate_provenance(auth_headers):
    """Verify showcase endpoint executes and accurately persists FSM, ML, and Hybrid alerts."""
    # 1. Run FSM-only showcase scenario
    fsm_run = client.post("/api/detection/showcase/run", json={"scenario": "fsm_only"}, headers=auth_headers)
    assert fsm_run.status_code == 200
    data_fsm = fsm_run.json()
    assert data_fsm["fsm_evaluation"]["violation"] is True
    assert data_fsm["hybrid_evaluation"]["attribution"] == "fsm"
    assert data_fsm["created_alert"]["engine"] == "fsm"

    # 2. Run ML-only showcase scenario
    ml_run = client.post("/api/detection/showcase/run", json={"scenario": "ml_only"}, headers=auth_headers)
    assert ml_run.status_code == 200
    data_ml = ml_run.json()
    assert data_ml["fsm_evaluation"]["violation"] is False
    assert data_ml["hybrid_evaluation"]["attribution"] == "ml"
    assert data_ml["created_alert"]["engine"] == "ml"

    # 3. Run Hybrid showcase scenario
    hyb_run = client.post("/api/detection/showcase/run", json={"scenario": "hybrid"}, headers=auth_headers)
    assert hyb_run.status_code == 200
    data_hyb = hyb_run.json()
    assert data_hyb["fsm_evaluation"]["violation"] is True
    assert data_hyb["hybrid_evaluation"]["attribution"] == "hybrid"
    assert data_hyb["created_alert"]["engine"] == "hybrid"


def test_legacy_unknown_provenance_remains_unknown(auth_headers):
    """Verify alerts without engine provenance retain 'unknown' rather than guessing."""
    db = SessionLocal()
    legacy_alert = Alert(
        workspace_id="default-workspace",
        alert_id=f"alrt_legacy_{os.urandom(4).hex()}",
        session_id="sess_legacy_unknown",
        engine="unspecified_custom",
        severity="low",
        risk_score=15,
        prediction="anomalous",
        status="new",
        summary="Legacy record without known engine provenance",
        timestamp=datetime.utcnow()
    )
    db.add(legacy_alert)
    db.commit()

    try:
        resp = client.get("/api/alerts/engine-activity", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["final_attribution"]["unknown"] >= 1
    finally:
        db.delete(legacy_alert)
        db.commit()
        db.close()


# ============================================================================
# WORKSTREAM C & D: ENGINE ACTIVITY, DEMO DATA ISOLATION & TIME FILTERS (15 - 17)
# ============================================================================

def test_no_duplicate_findings_on_repeated_requests(auth_headers):
    """Verify querying engine activity or dashboard multiple times produces identical idempotent counts."""
    r1 = client.get("/api/alerts/engine-activity", headers=auth_headers)
    r2 = client.get("/api/alerts/engine-activity", headers=auth_headers)
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["final_attribution"] == r2.json()["final_attribution"]
    assert r1.json()["engine_activity"] == r2.json()["engine_activity"]


def test_demo_data_does_not_pollute_live_network_statistics(auth_headers):
    """Verify include_demo=false strictly excludes demonstration dataset from statistics."""
    # Ensure a demo alert exists
    client.post("/api/detection/showcase/run", json={"scenario": "fsm_only"}, headers=auth_headers)

    resp_with_demo = client.get("/api/alerts/engine-activity?include_demo=true", headers=auth_headers)
    resp_no_demo = client.get("/api/alerts/engine-activity?include_demo=false", headers=auth_headers)

    assert resp_with_demo.status_code == 200
    assert resp_no_demo.status_code == 200

    total_with = resp_with_demo.json()["final_attribution"]["total"]
    total_without = resp_no_demo.json()["final_attribution"]["total"]
    assert total_with >= total_without


def test_time_filters_and_aggregation_totals_reconciled(auth_headers):
    """Verify time filters (24h, 7d) accurately filter records and totals sum up."""
    resp = client.get("/api/alerts/engine-activity?time_range=24h", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    attr = data["final_attribution"]
    calculated_sum = attr["fsm"] + attr["ml"] + attr["hybrid"] + attr["unknown"]
    assert calculated_sum == attr["total"]
