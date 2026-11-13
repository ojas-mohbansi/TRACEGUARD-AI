"""Formal Automata Verification Test Suite.

Verifies:
1. Total transition function: ∀ q ∈ Q, ∀ σ ∈ Σ, δ(q, σ) ∈ Q (No undefined transitions).
2. Exactly 9 states in complete DFA (|Q| = 9).
3. Exactly 13 input symbols in alphabet (|Σ| = 13).
4. Exactly 9 * 13 = 117 transition entries in complete matrix.
5. TRAP state self-loops for all 13 symbols.
6. Post-CLOSED events transition to TRAP.
7. Acceptance semantics: ACCEPTED, INCOMPLETE_VALID, REJECTED.
8. Empty sequence handling.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.detection.fsm.states import (
    COMPLETE_DFA_STATES,
    FINAL_STATES,
    INITIAL_STATE,
    HTTP_FSM_DEFINITION,
    State,
)

client = TestClient(app)


def test_complete_dfa_formal_specification():
    """Verify the formal complete DFA endpoint adheres to total transition requirements."""
    response = client.get("/api/protocols/http/formal-automaton")
    assert response.status_code == 200
    data = response.json()

    assert data["tuple_notation"] == "M = (Q, Σ, δ, q₀, F)"
    assert data["model_type"] == "Complete Total Deterministic Finite Automaton (Complete DFA)"
    
    # 1. State space Q cardinality
    states = data["Q_states"]
    state_ids = [s["id"] for s in states]
    assert len(states) == 9
    assert set(state_ids) == set(COMPLETE_DFA_STATES)
    assert "TRAP" in state_ids

    # 2. Alphabet Sigma cardinality
    alphabet = [s["symbol"] for s in data["Sigma_alphabet"]]
    assert len(alphabet) == 13

    # 3. Total transitions = 9 * 13 = 117
    assert data["total_matrix_cells"] == 117
    assert len(data["transition_function_delta"]) == 117
    assert len(data["full_matrix"]) == 9

    # 4. Total transition function property: δ(q, σ) ∈ Q for EVERY (q, σ)
    for row in data["full_matrix"]:
        current_q = row["state"]
        for sym in alphabet:
            target_q = row["entries"][sym]
            assert target_q in state_ids, f"δ({current_q}, {sym}) = {target_q} is not in Q!"
            assert target_q != "∅", f"Found undefined transition for ({current_q}, {sym})"


def test_trap_state_self_loops_for_all_symbols():
    """Verify TRAP state is an absorbing sink: δ(TRAP, σ) = TRAP for all σ ∈ Σ."""
    response = client.get("/api/protocols/http/formal-automaton")
    assert response.status_code == 200
    data = response.json()

    trap_row = next(r for r in data["full_matrix"] if r["state"] == "TRAP")
    assert trap_row["is_trap"] is True
    assert trap_row["is_accepting"] is False

    alphabet = [s["symbol"] for s in data["Sigma_alphabet"]]
    for sym in alphabet:
        assert trap_row["entries"][sym] == "TRAP", f"TRAP failed to self-loop on {sym}"


def test_events_after_closed_transition_to_trap():
    """Verify event received after connection is already CLOSED transitions to TRAP."""
    # Attempting to send REQUEST after CLOSE
    payload = {
        "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE", "REQUEST"]
    }
    response = client.post("/api/protocols/http/step-execute", json=payload)
    assert response.status_code == 200
    res = response.json()

    assert res["verdict"] == "REJECTED"
    assert res["all_transitions_valid"] is False
    assert res["final_state"] == "TRAP"
    
    # Step 5 is CLOSE -> CLOSED
    assert res["steps"][4]["next_state"] == "CLOSED"
    assert res["steps"][4]["valid"] is True

    # Step 6 is REQUEST from CLOSED -> TRAP
    assert res["steps"][5]["current_state"] == "CLOSED"
    assert res["steps"][5]["next_state"] == "TRAP"
    assert res["steps"][5]["valid"] is False
    assert "TRAP" in res["steps"][5]["delta_lookup"]


def test_unrecoverable_trap_behavior():
    """Verify once in TRAP, subsequent events remain in TRAP (absorbing sink)."""
    payload = {
        "events": ["REQUEST", "CONNECT", "CLOSE"]
    }
    response = client.post("/api/protocols/http/step-execute", json=payload)
    assert response.status_code == 200
    res = response.json()

    assert res["verdict"] == "REJECTED"
    assert res["final_state"] == "TRAP"
    # Step 1: IDLE + REQUEST -> TRAP
    assert res["steps"][0]["current_state"] == "IDLE"
    assert res["steps"][0]["next_state"] == "TRAP"
    # Step 2: TRAP + CONNECT -> TRAP
    assert res["steps"][1]["current_state"] == "TRAP"
    assert res["steps"][1]["next_state"] == "TRAP"
    # Step 3: TRAP + CLOSE -> TRAP
    assert res["steps"][2]["current_state"] == "TRAP"
    assert res["steps"][2]["next_state"] == "TRAP"


def test_acceptance_semantics_distinction():
    """Verify clean discrimination between ACCEPTED, INCOMPLETE_VALID, and REJECTED."""
    # A. Accepted (w ∈ L(M))
    res_acc = client.post("/api/protocols/http/step-execute", json={
        "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS", "RESPONSE_200", "CLOSE"]
    }).json()
    assert res_acc["verdict"] == "ACCEPTED"
    assert res_acc["is_in_accepting_state"] is True
    assert res_acc["all_transitions_valid"] is True

    # B. Incomplete Valid Prefix (w ∉ L(M), but valid prefix)
    res_inc = client.post("/api/protocols/http/step-execute", json={
        "events": ["CONNECT", "REQUEST", "AUTH_SUCCESS"]
    }).json()
    assert res_inc["verdict"] == "INCOMPLETE_VALID"
    assert res_inc["is_in_accepting_state"] is False
    assert res_inc["all_transitions_valid"] is True
    assert res_inc["final_state"] == "AUTH_CHECKED"

    # C. Rejected (w ∉ L(M), invalid transition)
    res_rej = client.post("/api/protocols/http/step-execute", json={
        "events": ["CONNECT", "RESPONSE_200"]
    }).json()
    assert res_rej["verdict"] == "REJECTED"
    assert res_rej["all_transitions_valid"] is False
    assert res_rej["final_state"] == "TRAP"


def test_empty_string_epsilon_classification():
    """Verify empty string ε is classified as INCOMPLETE_VALID (not accepted, but no violation)."""
    res = client.post("/api/protocols/http/step-execute", json={"events": []}).json()
    assert res["verdict"] == "INCOMPLETE_VALID"
    assert res["final_state"] == "IDLE"
    assert res["all_transitions_valid"] is True
    assert res["is_in_accepting_state"] is False
    assert len(res["steps"]) == 0
