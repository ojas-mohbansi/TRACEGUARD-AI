"""Protocol FSM specification and formal automata endpoints."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.detection.fsm.states import (
    HTTP_FSM_DEFINITION,
    INITIAL_STATE,
    FINAL_STATES,
    TRANSITION_MAP,
    VALID_EVENTS_PER_STATE,
    EventType,
    State,
)

router = APIRouter()


class StepExecutionRequest(BaseModel):
    events: List[str] = Field(..., description="Ordered list of event symbols/types")
    initial_state: Optional[str] = Field(None, description="Optional custom start state, defaults to q0 (IDLE)")


class StepDetail(BaseModel):
    step_number: int
    current_state: str
    symbol: str
    valid: bool
    next_state: Optional[str]
    delta_lookup: str
    explanation: str
    accepted_so_far: bool


class StepExecutionResponse(BaseModel):
    protocol: str
    formal_5_tuple: Dict[str, Any]
    input_symbols: List[str]
    steps: List[StepDetail]
    initial_state: str
    final_state: str
    all_transitions_valid: bool
    is_in_accepting_state: bool
    accepted_by_automaton: bool
    verdict: str  # ACCEPTED, REJECTED, INCOMPLETE_VALID
    rejection_reason: Optional[str] = None


@router.get("/http/fsm")
def get_http_fsm():
    """Return the HTTP FSM definition, states, transitions, event types, and formal 5-tuple."""
    five_tuple = {
        "formal_definition": "M = (Q, Σ, δ, q₀, F)",
        "Q": [s["id"] for s in HTTP_FSM_DEFINITION["states"]],
        "Sigma": HTTP_FSM_DEFINITION["event_types"],
        "q0": INITIAL_STATE,
        "F": list(FINAL_STATES),
        "transition_count": len(HTTP_FSM_DEFINITION["transitions"]),
        "states_count": len(HTTP_FSM_DEFINITION["states"]),
        "alphabet_size": len(HTTP_FSM_DEFINITION["event_types"]),
        "deterministic": True,
    }
    
    # Enrich states with formal metadata
    enriched_states = []
    for s in HTTP_FSM_DEFINITION["states"]:
        s_id = s["id"]
        valid_out = [
            {"event": event, "to": next_s}
            for (curr, event), next_s in TRANSITION_MAP.items()
            if curr == s_id
        ]
        valid_in = [
            {"event": event, "from": from_s}
            for (from_s, event), next_s in TRANSITION_MAP.items()
            if next_s == s_id
        ]
        enriched_states.append({
            **s,
            "is_initial": s_id == INITIAL_STATE,
            "is_final": s_id in FINAL_STATES,
            "outgoing_transitions": valid_out,
            "incoming_transitions": valid_in,
            "outgoing_count": len(valid_out),
            "incoming_count": len(valid_in),
        })

    enriched_transitions = []
    for t in HTTP_FSM_DEFINITION["transitions"]:
        enriched_transitions.append({
            **t,
            "delta_notation": f"δ({t['from']}, {t['event']}) = {t['to']}",
            "status": "deterministic_valid"
        })

    return {
        **HTTP_FSM_DEFINITION,
        "states": enriched_states,
        "transitions": enriched_transitions,
        "five_tuple": five_tuple,
    }


@router.get("/http/formal-automaton")
def get_formal_automaton():
    """Return formal Theory of Computation complete DFA mathematical representation (9 states, 117 total transitions)."""
    alphabet = HTTP_FSM_DEFINITION["event_types"]
    all_states_formal = [
        "IDLE", "CONNECTED", "REQUEST_RECEIVED", "AUTH_CHECKED",
        "AUTH_FAILED", "RESPONSE_SENT", "ERROR", "CLOSED", "TRAP"
    ]

    transition_table = []
    total_delta_list = []

    for state in all_states_formal:
        is_initial = (state == INITIAL_STATE)
        is_accepting = (state in FINAL_STATES)
        row_entries = {}

        for sym in alphabet:
            if state == State.TRAP:
                # TRAP self-loops for all symbols
                target = State.TRAP
                status = "trap_self_loop"
            elif state == State.CLOSED:
                # Any event after CLOSED enters TRAP
                target = State.TRAP
                status = "post_closed_violation"
            else:
                target = TRANSITION_MAP.get((state, sym))
                if target:
                    status = "valid_protocol_transition"
                else:
                    target = State.TRAP
                    status = "undefined_to_trap"

            row_entries[sym] = target
            total_delta_list.append({
                "from_state": state,
                "input_symbol": sym,
                "to_state": target,
                "delta": f"δ({state}, {sym}) = {target}",
                "status": status,
            })

        transition_table.append({
            "state": state,
            "is_initial": is_initial,
            "is_accepting": is_accepting,
            "is_trap": (state == State.TRAP),
            "entries": row_entries,
        })

    return {
        "tuple_notation": "M = (Q, Σ, δ, q₀, F)",
        "model_type": "Complete Total Deterministic Finite Automaton (Complete DFA)",
        "completeness_proof": "Total function: ∀ q ∈ Q, ∀ σ ∈ Σ, δ(q, σ) ∈ Q",
        "total_matrix_cells": len(all_states_formal) * len(alphabet),
        "valid_protocol_transitions_count": len(TRANSITION_MAP),
        "Q_states": [
            {
                "id": "IDLE",
                "meaning": "Initial quiescent state; socket listener initialized, waiting for incoming TCP SYN.",
                "is_initial": True,
                "is_accepting": False,
                "is_trap": False
            },
            {
                "id": "CONNECTED",
                "meaning": "3-way TCP handshake complete; session context allocated, waiting for HTTP request payload.",
                "is_initial": False,
                "is_accepting": False,
                "is_trap": False
            },
            {
                "id": "REQUEST_RECEIVED",
                "meaning": "HTTP request headers and path parsed; requires credential evaluation or error check.",
                "is_initial": False,
                "is_accepting": False,
                "is_trap": False
            },
            {
                "id": "AUTH_CHECKED",
                "meaning": "Credential verification succeeded or resource is public; ready to emit status response.",
                "is_initial": False,
                "is_accepting": False,
                "is_trap": False
            },
            {
                "id": "AUTH_FAILED",
                "meaning": "Credential verification failed; must emit 401 Unauthorized or 403 Forbidden.",
                "is_initial": False,
                "is_accepting": False,
                "is_trap": False
            },
            {
                "id": "RESPONSE_SENT",
                "meaning": "HTTP response flushed to socket; eligible for HTTP Keep-Alive pipelining or TCP CLOSE.",
                "is_initial": False,
                "is_accepting": False,
                "is_trap": False
            },
            {
                "id": "ERROR",
                "meaning": "Syntax error, internal failure, or timeout handled; can transmit error frame or close.",
                "is_initial": False,
                "is_accepting": False,
                "is_trap": False
            },
            {
                "id": "CLOSED",
                "meaning": "TCP FIN/RST or timeout received. Terminal accepting state (w ∈ L(M)).",
                "is_initial": False,
                "is_accepting": True,
                "is_trap": False
            },
            {
                "id": "TRAP",
                "meaning": "Dead/Trap non-accepting absorbing state. Entered upon any illegal protocol transition. Non-escapable.",
                "is_initial": False,
                "is_accepting": False,
                "is_trap": True
            }
        ],
        "Sigma_alphabet": [
            {"symbol": "CONNECT", "category": "Transport Handshake", "meaning": "TCP connection established"},
            {"symbol": "REQUEST", "category": "Client Action", "meaning": "HTTP request line & headers received"},
            {"symbol": "AUTH_SUCCESS", "category": "Security Verification", "meaning": "Authentication check passed"},
            {"symbol": "AUTH_FAILURE", "category": "Security Verification", "meaning": "Authentication check failed"},
            {"symbol": "RESPONSE_200", "category": "Server Response", "meaning": "HTTP 200 OK sent"},
            {"symbol": "RESPONSE_301", "category": "Server Response", "meaning": "HTTP 301 Moved Permanently sent"},
            {"symbol": "RESPONSE_401", "category": "Server Response", "meaning": "HTTP 401 Unauthorized sent"},
            {"symbol": "RESPONSE_403", "category": "Server Response", "meaning": "HTTP 403 Forbidden sent"},
            {"symbol": "RESPONSE_500", "category": "Server Response", "meaning": "HTTP 500 Internal Server Error sent"},
            {"symbol": "CLOSE", "category": "Session Teardown", "meaning": "Connection termination initiated"},
            {"symbol": "TIMEOUT", "category": "Session Teardown", "meaning": "Session inactivity limit reached"},
            {"symbol": "MALFORMED", "category": "Protocol Anomaly", "meaning": "Malformed request structure parsed"},
            {"symbol": "ERROR_RESPONSE", "category": "Server Response", "meaning": "Generic error response dispatched"}
        ],
        "q0": INITIAL_STATE,
        "F_accepting": list(FINAL_STATES),
        "transition_function_delta": total_delta_list,
        "full_matrix": transition_table
    }


@router.post("/http/step-execute", response_model=StepExecutionResponse)
def step_execute_automaton(payload: StepExecutionRequest):
    """Execute an event sequence step-by-step through the formal complete DFA transition function δ."""
    curr_state = payload.initial_state or INITIAL_STATE
    steps: List[StepDetail] = []
    all_valid = True
    rejection_reason = None
    entered_trap_at = None

    for idx, sym in enumerate(payload.events, start=1):
        clean_sym = sym.strip().upper()
        prev_state = curr_state

        if prev_state == State.TRAP:
            # Already in TRAP state: self-loop
            curr_state = State.TRAP
            valid_transition = False
            delta_str = f"δ(TRAP, {clean_sym}) = TRAP"
            expl = f"Step {idx}: Automaton remains trapped in dead state 'TRAP' upon input '{clean_sym}'."
        elif prev_state == State.CLOSED:
            # Event arriving after socket is already closed
            curr_state = State.TRAP
            valid_transition = False
            all_valid = False
            delta_str = f"δ(CLOSED, {clean_sym}) = TRAP"
            expl = f"REJECTION at Step {idx}: Connection already in terminal state 'CLOSED'. Unexpected event '{clean_sym}' transitions to TRAP."
            if rejection_reason is None:
                rejection_reason = expl
                entered_trap_at = idx
        else:
            # Normal lookup
            lookup_key = (prev_state, clean_sym)
            next_s = TRANSITION_MAP.get(lookup_key)

            if next_s is not None and all_valid:
                curr_state = next_s
                valid_transition = True
                delta_str = f"δ({prev_state}, {clean_sym}) = {next_s}"
                expl = f"Valid transition from {prev_state} to {next_s} upon receiving input symbol '{clean_sym}'."
            else:
                curr_state = State.TRAP
                valid_transition = False
                all_valid = False
                delta_str = f"δ({prev_state}, {clean_sym}) = TRAP"
                allowed = VALID_EVENTS_PER_STATE.get(prev_state, [])
                allowed_fmt = ", ".join(allowed) if allowed else "none (terminal)"
                expl = f"REJECTION at Step {idx}: No valid transition defined in protocol specification for state '{prev_state}' with symbol '{clean_sym}'. Transitioning to dead state 'TRAP'. Allowed symbols: [{allowed_fmt}]."
                if rejection_reason is None:
                    rejection_reason = expl
                    entered_trap_at = idx

        is_accepting = (curr_state in FINAL_STATES) and all_valid

        steps.append(StepDetail(
            step_number=idx,
            current_state=prev_state,
            symbol=clean_sym,
            valid=valid_transition,
            next_state=curr_state,
            delta_lookup=delta_str,
            explanation=expl,
            accepted_so_far=is_accepting
        ))

    is_accepting_final = (curr_state in FINAL_STATES)
    accepted_by_automaton = all_valid and is_accepting_final

    if accepted_by_automaton:
        verdict = "ACCEPTED"
    elif curr_state == State.TRAP or not all_valid:
        verdict = "REJECTED"
        if not rejection_reason:
            rejection_reason = "Sequence was rejected and entered dead state TRAP."
    else:
        # All transitions were valid, but did not end in accepting state F (e.g. valid prefix)
        verdict = "INCOMPLETE_VALID"
        rejection_reason = f"Sequence is a valid protocol prefix, but terminal state '{curr_state}' ∉ F ({list(FINAL_STATES)})."

    return StepExecutionResponse(
        protocol="HTTP",
        formal_5_tuple={
            "Q_cardinality": 9,
            "Sigma_size": len(HTTP_FSM_DEFINITION["event_types"]),
            "q0": INITIAL_STATE,
            "F": list(FINAL_STATES),
            "trap_state": State.TRAP,
            "total_transitions": 9 * len(HTTP_FSM_DEFINITION["event_types"]),
        },
        input_symbols=[s.strip().upper() for s in payload.events],
        steps=steps,
        initial_state=payload.initial_state or INITIAL_STATE,
        final_state=curr_state,
        all_transitions_valid=all_valid,
        is_in_accepting_state=is_accepting_final,
        accepted_by_automaton=accepted_by_automaton,
        verdict=verdict,
        rejection_reason=rejection_reason
    )

