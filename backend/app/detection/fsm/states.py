"""HTTP Protocol FSM State Definitions and Transition Table.

Defines the states, valid transitions, event types, and metadata
for the HTTP protocol state machine according to TraceGuard AI specifications.
"""

from typing import Any, Dict, List, Set, Tuple


class State:
    """FSM States for the HTTP Protocol as string constants."""
    IDLE = "IDLE"
    CONNECTED = "CONNECTED"
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    AUTH_CHECKED = "AUTH_CHECKED"
    AUTH_FAILED = "AUTH_FAILED"
    RESPONSE_SENT = "RESPONSE_SENT"
    ERROR = "ERROR"
    CLOSED = "CLOSED"
    TRAP = "TRAP"  # Formal DFA sink/trap state for total transition completeness


INITIAL_STATE = State.IDLE
FINAL_STATES: Set[str] = {State.CLOSED}
OPERATIONAL_STATES: List[str] = [
    State.IDLE,
    State.CONNECTED,
    State.REQUEST_RECEIVED,
    State.AUTH_CHECKED,
    State.AUTH_FAILED,
    State.RESPONSE_SENT,
    State.ERROR,
    State.CLOSED,
]
COMPLETE_DFA_STATES: List[str] = OPERATIONAL_STATES + [State.TRAP]


class EventType:
    """Valid event types recognized by the HTTP FSM."""
    CONNECT = "CONNECT"
    REQUEST = "REQUEST"
    AUTH_SUCCESS = "AUTH_SUCCESS"
    AUTH_FAILURE = "AUTH_FAILURE"
    RESPONSE_200 = "RESPONSE_200"
    RESPONSE_301 = "RESPONSE_301"
    RESPONSE_401 = "RESPONSE_401"
    RESPONSE_403 = "RESPONSE_403"
    RESPONSE_500 = "RESPONSE_500"
    CLOSE = "CLOSE"
    TIMEOUT = "TIMEOUT"
    MALFORMED = "MALFORMED"
    ERROR_RESPONSE = "ERROR_RESPONSE"


# Transition Table: (current_state, event) -> next_state
TRANSITION_MAP: Dict[Tuple[str, str], str] = {
    (State.IDLE, EventType.CONNECT): State.CONNECTED,
    (State.CONNECTED, EventType.REQUEST): State.REQUEST_RECEIVED,
    (State.CONNECTED, EventType.TIMEOUT): State.CLOSED,
    (State.REQUEST_RECEIVED, EventType.AUTH_SUCCESS): State.AUTH_CHECKED,
    (State.REQUEST_RECEIVED, EventType.AUTH_FAILURE): State.AUTH_FAILED,
    (State.REQUEST_RECEIVED, EventType.MALFORMED): State.ERROR,
    (State.AUTH_CHECKED, EventType.RESPONSE_200): State.RESPONSE_SENT,
    (State.AUTH_CHECKED, EventType.RESPONSE_301): State.RESPONSE_SENT,
    (State.AUTH_CHECKED, EventType.RESPONSE_500): State.ERROR,
    (State.AUTH_FAILED, EventType.RESPONSE_401): State.RESPONSE_SENT,
    (State.AUTH_FAILED, EventType.RESPONSE_403): State.RESPONSE_SENT,
    (State.RESPONSE_SENT, EventType.REQUEST): State.REQUEST_RECEIVED,
    (State.RESPONSE_SENT, EventType.CLOSE): State.CLOSED,
    (State.ERROR, EventType.CLOSE): State.CLOSED,
    (State.ERROR, EventType.ERROR_RESPONSE): State.RESPONSE_SENT,
}

# Outgoing valid events per state
VALID_EVENTS_PER_STATE: Dict[str, List[str]] = {}
for (state, event) in TRANSITION_MAP.keys():
    VALID_EVENTS_PER_STATE.setdefault(state, []).append(event)


# Exact FSM definition matching GET /api/protocols/http/fsm in API_CONTRACTS.md
HTTP_FSM_DEFINITION: Dict[str, Any] = {
    "protocol": "HTTP",
    "states": [
        {"id": "IDLE", "label": "Idle", "description": "No active connection", "is_initial": True, "is_final": False},
        {"id": "CONNECTED", "label": "Connected", "description": "TCP connection established", "is_initial": False, "is_final": False},
        {"id": "REQUEST_RECEIVED", "label": "Request Received", "description": "HTTP request received", "is_initial": False, "is_final": False},
        {"id": "AUTH_CHECKED", "label": "Auth Checked", "description": "Authentication verified", "is_initial": False, "is_final": False},
        {"id": "AUTH_FAILED", "label": "Auth Failed", "description": "Authentication failed", "is_initial": False, "is_final": False},
        {"id": "RESPONSE_SENT", "label": "Response Sent", "description": "HTTP response sent", "is_initial": False, "is_final": False},
        {"id": "ERROR", "label": "Error", "description": "Error state", "is_initial": False, "is_final": False},
        {"id": "CLOSED", "label": "Closed", "description": "Connection closed", "is_initial": False, "is_final": True}
    ],
    "transitions": [
        {"from": "IDLE", "to": "CONNECTED", "event": "CONNECT", "description": "Client connects"},
        {"from": "CONNECTED", "to": "REQUEST_RECEIVED", "event": "REQUEST", "description": "HTTP request received"},
        {"from": "REQUEST_RECEIVED", "to": "AUTH_CHECKED", "event": "AUTH_SUCCESS", "description": "Auth passed"},
        {"from": "REQUEST_RECEIVED", "to": "AUTH_FAILED", "event": "AUTH_FAILURE", "description": "Auth failed"},
        {"from": "AUTH_CHECKED", "to": "RESPONSE_SENT", "event": "RESPONSE_200", "description": "Success response"},
        {"from": "AUTH_CHECKED", "to": "RESPONSE_SENT", "event": "RESPONSE_301", "description": "Redirect response"},
        {"from": "AUTH_CHECKED", "to": "ERROR", "event": "RESPONSE_500", "description": "Server error"},
        {"from": "AUTH_FAILED", "to": "RESPONSE_SENT", "event": "RESPONSE_401", "description": "Unauthorized response"},
        {"from": "AUTH_FAILED", "to": "RESPONSE_SENT", "event": "RESPONSE_403", "description": "Forbidden response"},
        {"from": "RESPONSE_SENT", "to": "REQUEST_RECEIVED", "event": "REQUEST", "description": "Keep-alive request"},
        {"from": "RESPONSE_SENT", "to": "CLOSED", "event": "CLOSE", "description": "Connection closed"},
        {"from": "ERROR", "to": "CLOSED", "event": "CLOSE", "description": "Close after error"},
        {"from": "ERROR", "to": "RESPONSE_SENT", "event": "ERROR_RESPONSE", "description": "Error response sent"},
        {"from": "CONNECTED", "to": "CLOSED", "event": "TIMEOUT", "description": "Connection timeout"},
        {"from": "REQUEST_RECEIVED", "to": "ERROR", "event": "MALFORMED", "description": "Malformed request"}
    ],
    "event_types": [
        "CONNECT", "REQUEST", "AUTH_SUCCESS", "AUTH_FAILURE",
        "RESPONSE_200", "RESPONSE_301", "RESPONSE_401", "RESPONSE_403",
        "RESPONSE_500", "CLOSE", "TIMEOUT", "MALFORMED", "ERROR_RESPONSE"
    ]
}
