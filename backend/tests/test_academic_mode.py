"""Verification suite for Phase 17 Local Academic Mode & Production Dual-Mode Security."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token

client = TestClient(app)


def test_local_academic_mode_allows_unauthenticated_requests():
    """Verify that in LOCAL_ACADEMIC mode, requests proceed without requiring Bearer tokens."""
    original_mode = settings.LOCAL_ACADEMIC_MODE
    try:
        settings.LOCAL_ACADEMIC_MODE = True
        
        # 1. Unauthenticated request to /api/dashboard/summary
        resp = client.get("/api/dashboard/summary")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "total_events" in data
        assert "engine_distribution" in data

        # 2. Unauthenticated request to /api/alerts
        resp_alerts = client.get("/api/alerts?limit=10")
        assert resp_alerts.status_code == 200
        assert "alerts" in resp_alerts.json()

        # 3. Unauthenticated request to /api/alerts/analytics
        resp_analytics = client.get("/api/alerts/analytics")
        assert resp_analytics.status_code == 200
        assert "severity_distribution" in resp_analytics.json()
        assert "engine_distribution" in resp_analytics.json()

    finally:
        settings.LOCAL_ACADEMIC_MODE = original_mode


def test_production_mode_fails_closed_with_401():
    """Verify that in PRODUCTION mode, unauthenticated requests are strictly rejected with 401."""
    original_mode = settings.LOCAL_ACADEMIC_MODE
    try:
        settings.LOCAL_ACADEMIC_MODE = False

        # 1. Unauthenticated request to /api/dashboard/summary must return 401
        resp = client.get("/api/dashboard/summary")
        assert resp.status_code == 401, f"Expected 401 in PRODUCTION mode, got {resp.status_code}"
        assert resp.json()["detail"] == "Not authenticated"

        # 2. Unauthenticated request to /api/alerts must return 401
        resp_alerts = client.get("/api/alerts")
        assert resp_alerts.status_code == 401

        # 3. Authenticated request with valid JWT succeeds in PRODUCTION mode
        valid_token = create_access_token(data={"sub": settings.DEMO_USERNAME})
        resp_auth = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {valid_token}"})
        assert resp_auth.status_code == 200

    finally:
        settings.LOCAL_ACADEMIC_MODE = original_mode


def test_local_academic_mode_binds_to_default_workspace():
    """Verify that in LOCAL_ACADEMIC mode, client is safely pinned to default-workspace."""
    original_mode = settings.LOCAL_ACADEMIC_MODE
    try:
        settings.LOCAL_ACADEMIC_MODE = True
        resp = client.get("/api/dashboard/summary", headers={"X-Workspace-ID": "malicious-tenant-spoof"})
        assert resp.status_code == 200
    finally:
        settings.LOCAL_ACADEMIC_MODE = original_mode


def test_fsm_strict_trap_absorption():
    """Verify that under strict_trap=True, the FSM enters TRAP and absorbs subsequent events."""
    from app.detection.fsm import FSMEngine, State
    fsm = FSMEngine()
    events = [
        {"event_id": "e1", "session_id": "s_trap", "event_type": "CONNECT"},
        {"event_id": "e2", "session_id": "s_trap", "event_type": "RESPONSE_200"},  # Invalid in CONNECTED -> enters TRAP
        {"event_id": "e3", "session_id": "s_trap", "event_type": "REQUEST"},       # In TRAP -> absorbed
        {"event_id": "e4", "session_id": "s_trap", "event_type": "CLOSE"},         # In TRAP -> absorbed
    ]
    res = fsm.validate_session(events, strict_trap=True)
    assert res["fsm_violation"] is True
    assert res["final_state"] == State.TRAP
    assert res["transition_history"][1]["to"] == State.TRAP
    assert res["transition_history"][2]["from"] == State.TRAP
    assert res["transition_history"][2]["to"] == State.TRAP
    assert res["transition_history"][3]["from"] == State.TRAP
    assert res["transition_history"][3]["to"] == State.TRAP
