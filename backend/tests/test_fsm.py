"""Test suite for TraceGuard AI FSM Engine."""

import pytest
from backend.app.detection.fsm import FSMEngine, State, EventType, HTTP_FSM_DEFINITION


@pytest.fixture
def fsm():
    return FSMEngine()


def test_normal_session(fsm):
    """1. Normal session produces prediction='normal', risk_score=0."""
    events = [
        {"event_id": "evt_1", "session_id": "sess_norm", "event_type": "CONNECT"},
        {"event_id": "evt_2", "session_id": "sess_norm", "event_type": "REQUEST"},
        {"event_id": "evt_3", "session_id": "sess_norm", "event_type": "AUTH_SUCCESS"},
        {"event_id": "evt_4", "session_id": "sess_norm", "event_type": "RESPONSE_200"},
        {"event_id": "evt_5", "session_id": "sess_norm", "event_type": "CLOSE"},
    ]
    result = fsm.validate_session(events)
    assert result["session_id"] == "sess_norm"
    assert result["engine"] == "fsm"
    assert result["prediction"] == "normal"
    assert result["risk_score"] == 0
    assert result["fsm_violation"] is False
    assert len(result["violations"]) == 0
    assert result["severity"] == "low"
    assert len(result["transition_history"]) == 5
    assert all(t["valid"] for t in result["transition_history"])


def test_invalid_transition(fsm):
    """2. Session with invalid transition produces prediction='anomalous' and risk_score=60."""
    events = [
        {"event_id": "evt_1", "session_id": "sess_inv", "event_type": "CONNECT"},
        {"event_id": "evt_2", "session_id": "sess_inv", "event_type": "RESPONSE_200"},  # Invalid in CONNECTED state
        {"event_id": "evt_3", "session_id": "sess_inv", "event_type": "REQUEST"},
        {"event_id": "evt_4", "session_id": "sess_inv", "event_type": "AUTH_SUCCESS"},
        {"event_id": "evt_5", "session_id": "sess_inv", "event_type": "RESPONSE_200"},
        {"event_id": "evt_6", "session_id": "sess_inv", "event_type": "CLOSE"},
    ]
    result = fsm.validate_session(events)
    assert result["session_id"] == "sess_inv"
    assert result["prediction"] == "anomalous"
    assert result["risk_score"] == 60
    assert result["fsm_violation"] is True
    assert len(result["violations"]) == 1
    assert result["violations"][0]["incoming_event"] == "RESPONSE_200"
    assert "evt_2" in result["responsible_events"]


def test_incomplete_session(fsm):
    """3. Incomplete session (no CLOSE) gets lower severity / risk_score=30."""
    events = [
        {"event_id": "evt_1", "session_id": "sess_inc", "event_type": "CONNECT"},
        {"event_id": "evt_2", "session_id": "sess_inc", "event_type": "REQUEST"},
        {"event_id": "evt_3", "session_id": "sess_inc", "event_type": "AUTH_SUCCESS"},
        {"event_id": "evt_4", "session_id": "sess_inc", "event_type": "RESPONSE_200"},
        # No CLOSE event
    ]
    result = fsm.validate_session(events)
    assert result["session_id"] == "sess_inc"
    assert result["fsm_violation"] is False  # No sequence invariant broken, but incomplete
    assert result["risk_score"] == 30
    assert result["severity"] == "medium"
    assert result["prediction"] == "normal"  # Risk score 30 < 50 threshold


def test_multiple_violations(fsm):
    """4. Multiple violations increase risk score (80+)."""
    events = [
        {"event_id": "evt_1", "session_id": "sess_mult", "event_type": "CONNECT"},
        {"event_id": "evt_2", "session_id": "sess_mult", "event_type": "RESPONSE_200"},  # Viol 1
        {"event_id": "evt_3", "session_id": "sess_mult", "event_type": "AUTH_SUCCESS"},  # Viol 2 (still CONNECTED)
        {"event_id": "evt_4", "session_id": "sess_mult", "event_type": "REQUEST"},
        {"event_id": "evt_5", "session_id": "sess_mult", "event_type": "CLOSE"},  # Viol 3 in REQUEST_RECEIVED
    ]
    result = fsm.validate_session(events)
    assert result["session_id"] == "sess_mult"
    assert result["prediction"] == "anomalous"
    assert result["fsm_violation"] is True
    assert len(result["violations"]) == 3
    assert result["risk_score"] >= 80
    assert result["severity"] == "critical"
    assert len(result["responsible_events"]) == 3


def test_impossible_transition(fsm):
    """5. Impossible transition (e.g. unknown event or event from terminal CLOSED) gets risk_score near 100."""
    # Test case A: Unknown event type in protocol
    events = [
        {"event_id": "evt_1", "session_id": "sess_impos", "event_type": "CONNECT"},
        {"event_id": "evt_2", "session_id": "sess_impos", "event_type": "NON_EXISTENT_OPCODE"},
        {"event_id": "evt_3", "session_id": "sess_impos", "event_type": "CLOSE"},
    ]
    result = fsm.validate_session(events)
    assert result["session_id"] == "sess_impos"
    assert result["prediction"] == "anomalous"
    assert result["risk_score"] == 100
    assert result["severity"] == "critical"
    assert result["fsm_violation"] is True

    # Test case B: Event after terminal CLOSED state
    events_closed = [
        {"event_id": "evt_1", "session_id": "sess_closed", "event_type": "CONNECT"},
        {"event_id": "evt_2", "session_id": "sess_closed", "event_type": "TIMEOUT"},  # Reaches CLOSED
        {"event_id": "evt_3", "session_id": "sess_closed", "event_type": "REQUEST"},  # Impossible from CLOSED
    ]
    result_closed = fsm.validate_session(events_closed)
    assert result_closed["risk_score"] == 100
    assert result_closed["prediction"] == "anomalous"


def test_get_definition(fsm):
    """6. get_definition() returns correct number of states and transitions."""
    definition = fsm.get_definition()
    assert definition["protocol"] == "HTTP"
    assert len(definition["states"]) == 9
    assert len(definition["transitions"]) == 15
    assert len(definition["event_types"]) == 13

    # Check state IDs
    state_ids = {s["id"] for s in definition["states"]}
    expected_states = {
        "IDLE", "CONNECTED", "REQUEST_RECEIVED", "AUTH_CHECKED",
        "AUTH_FAILED", "RESPONSE_SENT", "ERROR", "CLOSED", "TRAP"
    }
    assert state_ids == expected_states

    # Check initial and final flags
    initial_states = [s["id"] for s in definition["states"] if s.get("is_initial")]
    final_states = [s["id"] for s in definition["states"] if s.get("is_final")]
    assert initial_states == ["IDLE"]
    assert final_states == ["CLOSED"]


def test_session_isolation_and_resets(fsm):
    """7. Test session isolation: concurrent/sequential sessions do not leak state."""
    # Session 1 ends in ERROR
    sess1 = [
        {"event_id": "e1", "session_id": "sess_1", "event_type": "CONNECT"},
        {"event_id": "e2", "session_id": "sess_1", "event_type": "REQUEST"},
        {"event_id": "e3", "session_id": "sess_1", "event_type": "MALFORMED"},
    ]
    res1 = fsm.validate_session(sess1)
    assert res1["session_id"] == "sess_1"
    assert res1["transition_history"][-1]["to"] == "ERROR"

    # Session 2 is completely clean
    sess2 = [
        {"event_id": "e4", "session_id": "sess_2", "event_type": "CONNECT"},
        {"event_id": "e5", "session_id": "sess_2", "event_type": "TIMEOUT"},
    ]
    res2 = fsm.validate_session(sess2)
    assert res2["session_id"] == "sess_2"
    assert res2["prediction"] == "normal"
    assert res2["risk_score"] == 0
    assert len(res2["violations"]) == 0
    assert res2["transition_history"][0]["from"] == "IDLE"


def test_all_15_valid_transitions_individually(fsm):
    """8. Test every single one of the 15 documented transitions executes validly."""
    def_data = fsm.get_definition()
    assert len(def_data["transitions"]) == 15

    # Path 1: IDLE -> CONNECTED -> REQUEST_RECEIVED -> AUTH_CHECKED -> RESPONSE_SENT (200) -> REQUEST_RECEIVED -> AUTH_CHECKED -> RESPONSE_SENT (301) -> CLOSED
    path1 = [
        {"event_id": "1", "event_type": "CONNECT"},          # 1. IDLE -> CONNECTED
        {"event_id": "2", "event_type": "REQUEST"},          # 2. CONNECTED -> REQUEST_RECEIVED
        {"event_id": "3", "event_type": "AUTH_SUCCESS"},      # 3. REQUEST_RECEIVED -> AUTH_CHECKED
        {"event_id": "4", "event_type": "RESPONSE_200"},      # 4. AUTH_CHECKED -> RESPONSE_SENT
        {"event_id": "5", "event_type": "REQUEST"},          # 5. RESPONSE_SENT -> REQUEST_RECEIVED (Keep-alive)
        {"event_id": "6", "event_type": "AUTH_SUCCESS"},      # REQUEST_RECEIVED -> AUTH_CHECKED
        {"event_id": "7", "event_type": "RESPONSE_301"},      # 6. AUTH_CHECKED -> RESPONSE_SENT (Redirect)
        {"event_id": "8", "event_type": "CLOSE"},             # 7. RESPONSE_SENT -> CLOSED
    ]
    r1 = fsm.validate_session(path1)
    assert r1["fsm_violation"] is False
    assert r1["risk_score"] == 0

    # Path 2: IDLE -> CONNECTED -> TIMEOUT -> CLOSED
    path2 = [
        {"event_id": "1", "event_type": "CONNECT"},
        {"event_id": "2", "event_type": "TIMEOUT"},          # 8. CONNECTED -> CLOSED
    ]
    r2 = fsm.validate_session(path2)
    assert r2["fsm_violation"] is False
    assert r2["risk_score"] == 0

    # Path 3: REQUEST_RECEIVED -> AUTH_FAILURE -> RESPONSE_401 -> CLOSE
    path3 = [
        {"event_id": "1", "event_type": "CONNECT"},
        {"event_id": "2", "event_type": "REQUEST"},
        {"event_id": "3", "event_type": "AUTH_FAILURE"},      # 9. REQUEST_RECEIVED -> AUTH_FAILED
        {"event_id": "4", "event_type": "RESPONSE_401"},      # 10. AUTH_FAILED -> RESPONSE_SENT
        {"event_id": "5", "event_type": "CLOSE"},
    ]
    r3 = fsm.validate_session(path3)
    assert r3["fsm_violation"] is False

    # Path 4: AUTH_FAILED -> RESPONSE_403
    path4 = [
        {"event_id": "1", "event_type": "CONNECT"},
        {"event_id": "2", "event_type": "REQUEST"},
        {"event_id": "3", "event_type": "AUTH_FAILURE"},
        {"event_id": "4", "event_type": "RESPONSE_403"},      # 11. AUTH_FAILED -> RESPONSE_SENT
        {"event_id": "5", "event_type": "CLOSE"},
    ]
    r4 = fsm.validate_session(path4)
    assert r4["fsm_violation"] is False

    # Path 5: AUTH_CHECKED -> RESPONSE_500 -> ERROR -> ERROR_RESPONSE -> RESPONSE_SENT -> CLOSE
    path5 = [
        {"event_id": "1", "event_type": "CONNECT"},
        {"event_id": "2", "event_type": "REQUEST"},
        {"event_id": "3", "event_type": "AUTH_SUCCESS"},
        {"event_id": "4", "event_type": "RESPONSE_500"},      # 12. AUTH_CHECKED -> ERROR
        {"event_id": "5", "event_type": "ERROR_RESPONSE"},    # 13. ERROR -> RESPONSE_SENT
        {"event_id": "6", "event_type": "CLOSE"},
    ]
    r5 = fsm.validate_session(path5)
    assert r5["fsm_violation"] is False

    # Path 6: REQUEST_RECEIVED -> MALFORMED -> ERROR -> CLOSE
    path6 = [
        {"event_id": "1", "event_type": "CONNECT"},
        {"event_id": "2", "event_type": "REQUEST"},
        {"event_id": "3", "event_type": "MALFORMED"},         # 14. REQUEST_RECEIVED -> ERROR
        {"event_id": "4", "event_type": "CLOSE"},             # 15. ERROR -> CLOSED
    ]
    r6 = fsm.validate_session(path6)
    assert r6["fsm_violation"] is False

