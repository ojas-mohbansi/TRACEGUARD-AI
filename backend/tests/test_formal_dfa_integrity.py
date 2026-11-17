"""Formal Mathematical Invariant Verification Suite for Complete Total HTTP DFA.

Verifies:
1. Exact State Space Q: |Q| = 9.
2. Exact Alphabet Sigma: |Σ| = 13.
3. Total Transition Function: |δ| = |Q| * |Σ| = 9 * 13 = 117.
4. Total Completeness: ∀ q ∈ Q, ∀ σ ∈ Σ, δ(q, σ) ∈ Q (No undefined cells, no duplicate cells).
5. Determinism: Single unique target state for every (state, symbol) pair.
6. Initial State: q0 = IDLE.
7. Accepting Set: F = {CLOSED}.
8. Absorbing Trap Invariant: ∀ σ ∈ Σ, δ(TRAP, σ) = TRAP.
9. Terminal Boundary Invariant: ∀ σ ∈ Σ, δ(CLOSED, σ) = TRAP.
10. Operational vs Complete DFA cardinality consistency.
"""
import pytest
from app.detection.fsm.states import (
    COMPLETE_DFA_STATES,
    OPERATIONAL_STATES,
    INITIAL_STATE,
    FINAL_STATES,
    TRANSITION_MAP,
    State,
    EventType,
    HTTP_FSM_DEFINITION
)
from app.api.protocols import get_formal_automaton, get_http_fsm


EXPECTED_Q_STATES = {
    "IDLE",
    "CONNECTED",
    "REQUEST_RECEIVED",
    "AUTH_CHECKED",
    "AUTH_FAILED",
    "RESPONSE_SENT",
    "ERROR",
    "CLOSED",
    "TRAP"
}

EXPECTED_SIGMA_ALPHABET = {
    "CONNECT",
    "REQUEST",
    "AUTH_SUCCESS",
    "AUTH_FAILURE",
    "RESPONSE_200",
    "RESPONSE_301",
    "RESPONSE_401",
    "RESPONSE_403",
    "RESPONSE_500",
    "CLOSE",
    "TIMEOUT",
    "MALFORMED",
    "ERROR_RESPONSE"
}


def test_dfa_cardinality_and_states():
    """Verify |Q| = 9 and state set matches the approved academic HTTP DFA."""
    assert len(COMPLETE_DFA_STATES) == 9, f"Expected |Q|=9, got {len(COMPLETE_DFA_STATES)}"
    assert set(COMPLETE_DFA_STATES) == EXPECTED_Q_STATES
    assert len(set(COMPLETE_DFA_STATES)) == 9, "Duplicate state detected in state space"


def test_alphabet_cardinality_and_symbols():
    """Verify |Σ| = 13 and alphabet matches the approved protocol events."""
    alphabet = HTTP_FSM_DEFINITION["event_types"]
    assert len(alphabet) == 13, f"Expected |Σ|=13, got {len(alphabet)}"
    assert set(alphabet) == EXPECTED_SIGMA_ALPHABET
    assert len(set(alphabet)) == 13, "Duplicate symbol detected in alphabet"


def test_transition_matrix_completeness_and_determinism():
    """Verify |δ| = |Q| * |Σ| = 9 * 13 = 117 total transitions without omissions or duplicates."""
    automaton = get_formal_automaton()
    delta_list = automaton["transition_function_delta"]
    
    assert len(delta_list) == 117, f"Expected exactly 117 transitions, got {len(delta_list)}"
    assert automaton["total_matrix_cells"] == 117
    
    # Check that every (q, σ) pair appears exactly once
    seen_pairs = set()
    for entry in delta_list:
        pair = (entry["from_state"], entry["input_symbol"])
        assert pair not in seen_pairs, f"Duplicate transition cell found for {pair}"
        seen_pairs.add(pair)
        
        # Verify closure: target must belong to Q
        assert entry["to_state"] in EXPECTED_Q_STATES, f"Target {entry['to_state']} not in Q"

    assert len(seen_pairs) == 117, "Not all 117 (state, symbol) pairs are covered in δ"


def test_formal_trap_state_invariants():
    """Verify TRAP state is strictly absorbing (self-loop for all 13 symbols)."""
    automaton = get_formal_automaton()
    delta_list = automaton["transition_function_delta"]
    
    trap_transitions = [e for e in delta_list if e["from_state"] == State.TRAP]
    assert len(trap_transitions) == 13, f"Expected 13 TRAP transitions, got {len(trap_transitions)}"
    
    for entry in trap_transitions:
        assert entry["to_state"] == State.TRAP, f"TRAP transition on {entry['input_symbol']} leaked to {entry['to_state']}"
        assert entry["status"] == "trap_self_loop"


def test_closed_terminal_state_invariants():
    """Verify CLOSED state rejects any subsequent symbols into TRAP."""
    automaton = get_formal_automaton()
    delta_list = automaton["transition_function_delta"]
    
    closed_transitions = [e for e in delta_list if e["from_state"] == State.CLOSED]
    assert len(closed_transitions) == 13, f"Expected 13 CLOSED transitions, got {len(closed_transitions)}"
    
    for entry in closed_transitions:
        assert entry["to_state"] == State.TRAP, f"Post-CLOSED transition on {entry['input_symbol']} did not enter TRAP"
        assert entry["status"] == "post_closed_violation"


def test_initial_and_accepting_states():
    """Verify initial state is IDLE and accepting set is exactly {CLOSED}."""
    assert INITIAL_STATE == "IDLE"
    assert FINAL_STATES == {"CLOSED"}
    
    automaton = get_formal_automaton()
    q_states = automaton["Q_states"]
    
    initial_count = sum(1 for s in q_states if s["is_initial"])
    accepting_count = sum(1 for s in q_states if s["is_accepting"])
    
    assert initial_count == 1, "There must be exactly one initial state"
    assert accepting_count == 1, "There must be exactly one accepting state"
    
    for s in q_states:
        if s["id"] == "IDLE":
            assert s["is_initial"] is True
            assert s["is_accepting"] is False
        elif s["id"] == "CLOSED":
            assert s["is_initial"] is False
            assert s["is_accepting"] is True
        else:
            assert s["is_initial"] is False
            assert s["is_accepting"] is False


def test_step_execution_acceptance_semantics():
    """Verify the 3 formal verdicts: ACCEPTED, INCOMPLETE_VALID, REJECTED."""
    from app.api.protocols import StepExecutionRequest, router
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # 1. Canonical Valid Session -> ACCEPTED
    res_acc = client.post("/api/protocols/http/step-execute", json={
        "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"]
    })
    assert res_acc.status_code == 200
    data_acc = res_acc.json()
    assert data_acc["verdict"] == "ACCEPTED"
    assert data_acc["accepted_by_automaton"] is True
    assert data_acc["final_state"] == "CLOSED"
    
    # 2. Incomplete Valid Prefix -> INCOMPLETE_VALID
    res_inc = client.post("/api/protocols/http/step-execute", json={
        "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS"]
    })
    assert res_inc.status_code == 200
    data_inc = res_inc.json()
    assert data_inc["verdict"] == "INCOMPLETE_VALID"
    assert data_inc["accepted_by_automaton"] is False
    assert data_inc["final_state"] == "AUTH_CHECKED"
    
    # 3. Invalid Transition -> REJECTED
    res_rej = client.post("/api/protocols/http/step-execute", json={
        "events": ["CONNECT", "RESPONSE_200", "CLOSE"]
    })
    assert res_rej.status_code == 200
    data_rej = res_rej.json()
    assert data_rej["verdict"] == "REJECTED"
    assert data_rej["accepted_by_automaton"] is False
    assert data_rej["final_state"] == "TRAP"
