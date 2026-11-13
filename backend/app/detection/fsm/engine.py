"""FSM Detection Engine for TraceGuard AI.

Validates sequences of protocol events against deterministic FSM rules,
identifies invalid transitions, assigns risk scores, and generates detailed explanations.
"""

import time
from typing import Any, Dict, List, Optional

from .states import (
    HTTP_FSM_DEFINITION,
    INITIAL_STATE,
    FINAL_STATES,
    State,
    TRANSITION_MAP,
    VALID_EVENTS_PER_STATE,
)


def risk_to_severity(risk_score: int) -> str:
    """Map risk score (0-100) to severity category.

    Low (0-25), Medium (26-50), High (51-75), Critical (76-100).
    """
    if risk_score >= 76:
        return "critical"
    if risk_score >= 51:
        return "high"
    if risk_score >= 26:
        return "medium"
    return "low"


class FSMEngine:
    """Finite State Machine verification engine for protocol sessions."""

    def __init__(self, definition: Optional[Dict[str, Any]] = None):
        self.definition = definition or HTTP_FSM_DEFINITION
        self.initial_state = INITIAL_STATE
        self.final_states = FINAL_STATES
        self.transition_map = TRANSITION_MAP
        self.valid_events = VALID_EVENTS_PER_STATE

    @classmethod
    def get_definition(cls) -> Dict[str, Any]:
        """Return the FSM definition conforming to GET /api/protocols/http/fsm."""
        return HTTP_FSM_DEFINITION

    def validate_session(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate an event stream for a single session against the FSM.

        Args:
            events: List of event dicts belonging to a single session. Each event
                    typically contains event_id, session_id, event_type, timestamp.

        Returns:
            Dict containing session_id, prediction, risk_score, severity,
            fsm_violation flag, violations, transition_history, explanation,
            responsible_events, and processing_time_ms.
        """
        start_time = time.perf_counter()

        if not events:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "session_id": "unknown",
                "engine": "fsm",
                "prediction": "normal",
                "risk_score": 0,
                "severity": "low",
                "fsm_violation": False,
                "violations": [],
                "transition_history": [],
                "explanation": "No events provided for session.",
                "responsible_events": [],
                "processing_time_ms": round(elapsed_ms, 3),
            }

        session_id = str(events[0].get("session_id", "unknown"))

        current_state: str = self.initial_state
        transition_history: List[Dict[str, Any]] = []
        violations: List[Dict[str, Any]] = []
        responsible_events: List[str] = []
        has_impossible_transition = False

        for event in events:
            event_id = str(event.get("event_id", ""))
            event_type = str(event.get("event_type", ""))
            prev_state = current_state

            lookup_key = (current_state, event_type)
            next_state = self.transition_map.get(lookup_key)

            if next_state is not None:
                # Valid transition
                transition_history.append({
                    "from": prev_state,
                    "to": next_state,
                    "event": event_type,
                    "valid": True,
                })
                current_state = next_state
            else:
                # Invalid / Unexpected transition
                expected_events = self.valid_events.get(current_state, [])
                
                # Check if this event type exists anywhere in the protocol
                all_events = self.definition.get("event_types", [])
                if event_type not in all_events:
                    violation_reason = f"Unknown protocol event '{event_type}' received in state '{current_state}'."
                    has_impossible_transition = True
                else:
                    violation_reason = (
                        f"Unexpected event '{event_type}' in state '{current_state}'. "
                        f"Expected one of: {expected_events if expected_events else 'None'}."
                    )
                    # Impossible transitions: e.g. event from terminal CLOSED state or illegal protocol bypass
                    if current_state == State.CLOSED:
                        has_impossible_transition = True

                violation_entry = {
                    "current_state": current_state,
                    "previous_state": prev_state,
                    "incoming_event": event_type,
                    "expected_transitions": expected_events,
                    "actual_transition": f"{current_state} -> ? via {event_type}",
                    "violation_reason": violation_reason,
                }
                violations.append(violation_entry)
                if event_id:
                    responsible_events.append(event_id)

                transition_history.append({
                    "from": prev_state,
                    "to": current_state,  # State does not advance or is stuck
                    "event": event_type,
                    "valid": False,
                })

        # Check completeness: Did the session terminate in a valid final state?
        is_incomplete = (current_state not in self.final_states)

        # Risk scoring rules:
        # 0 = clean
        # 30 = incomplete (no CLOSE / terminated early without violation)
        # 60 = single violation
        # 80+ = multiple violations (e.g. 80 for 2, +5 for each subsequent up to 95)
        # 100 = impossible transitions
        num_violations = len(violations)
        if has_impossible_transition:
            risk_score = 100
        elif num_violations >= 2:
            risk_score = min(95, 80 + (num_violations - 2) * 5)
        elif num_violations == 1:
            risk_score = 60
        elif is_incomplete:
            risk_score = 30
        else:
            risk_score = 0

        severity = risk_to_severity(risk_score)
        fsm_violation = (num_violations > 0)
        # A session is anomalous if it has violations or severe incompleteness (risk_score >= 50 or fsm_violation)
        prediction = "anomalous" if (fsm_violation or risk_score >= 50) else "normal"

        # Build human-readable explanation
        if has_impossible_transition:
            explanation = (
                f"Critical protocol violation: Session executed impossible transition(s) ({num_violations} total). "
                f"First violation: {violations[0]['violation_reason']}"
            )
        elif num_violations > 1:
            explanation = (
                f"Multiple protocol sequence violations detected ({num_violations} violations). "
                f"First violation at state '{violations[0]['previous_state']}' with event '{violations[0]['incoming_event']}'."
            )
        elif num_violations == 1:
            explanation = (
                f"Protocol violation detected: {violations[0]['violation_reason']}"
            )
        elif is_incomplete:
            explanation = (
                f"Session incomplete: Stream terminated in non-final state '{current_state}' without a clean CLOSE/TIMEOUT."
            )
        else:
            explanation = "Session followed valid protocol state sequence from IDLE to CLOSED."

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "session_id": session_id,
            "engine": "fsm",
            "prediction": prediction,
            "risk_score": risk_score,
            "severity": severity,
            "fsm_violation": fsm_violation,
            "violations": violations,
            "transition_history": transition_history,
            "explanation": explanation,
            "responsible_events": responsible_events,
            "processing_time_ms": round(elapsed_ms, 3),
        }
