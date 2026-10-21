"""Tier-1 deterministic FSM engine for Modbus/TCP protocol validation.

This module is the hard-protocol half of the hybrid detector. It consumes the
same :class:`~modbus_nids.models.ModbusRecord` stream as the Phase 1.3 window
extractor and returns a per-event verdict: a score, a decision, a stable reason
code and enough provenance (conversation, transaction, states) for an operator to
reconstruct exactly what the engine saw.

The engine is a *protocol* checker, not a behavioural one. It answers "is this
event possible in a well-formed Modbus/TCP conversation?" and deliberately
ignores "is this traffic unusual?". Write floods, register sweeps and off-hours
bursts are Tier 2/3 material; a response with no matching request, a reused
transaction ID, or a function-code mismatch are Tier-1 material.

Two decisions shape the design:

*Conversations are canonicalised, not directional.* A request and its response
travel in opposite directions, so the directional ``(source_ip, dest_ip,
connection)`` key used for feature windows would put them in different
sessions. :class:`ConversationKey` stores ``(client_ip, server_ip,
tcp_connection)`` so both halves of an exchange live together. For a
request-only capture the label is byte-identical to the existing ``flow_key``.

*Unanswered requests are legal.* Modbus/TCP permits several requests in flight
on one connection, and many captures only contain one direction. An unanswered
request therefore stays open and is reported as an incomplete transaction at
``finish()`` -- it is never scored as a violation. Hard violations are
reserved for the faults that are unambiguous: a response that cannot be
correlated, a function code or unit ID that contradicts the request, a reused
transaction ID, and a transition the state machine does not define.

*Roles come from the wire, not from labels.* The endpoint that carries a
Modbus port is the server, so a request and its response land in one
conversation even when the exporter mislabels the direction. The message role
(request or response) is decided by the ports first, then by the declared
``direction`` column, then by roles learned from an earlier event on the same
connection. The one thing that outranks all of them is the Modbus exception
flag (0x80): only a server ever sets it, so it always marks a response.
"""

from __future__ import annotations

import math
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from types import MappingProxyType
from typing import Any, Final, Iterable, Literal, Mapping, Union

import numpy as np
import pandas as pd

from .constants import (
    DEFAULT_ALLOWED_PORTS,
    EXCEPTION_FLAG,
    EXCEPTION_RESPONSE_LENGTH,
    PORT_MAX,
    PORT_MIN,
    base_function_code,
    is_exception_response,
)
from .models import Direction, IngestResult, ModbusRecord
from .parser import resolve_records

__all__ = [
    "ConversationKey",
    "DEFAULT_MAX_OUTSTANDING",
    "DEFAULT_TID_HISTORY",
    "FSMConfig",
    "FSMNote",
    "FSMReason",
    "FSMSummary",
    "FSMSymbol",
    "ModbusFSM",
    "RoleSource",
    "SessionState",
    "SymbolClass",
    "Tier1Result",
    "Tier1Verdict",
    "TransitionTarget",
    "TRANSITIONS",
    "VERDICT_COLUMNS",
    "evaluate_tier1",
]

FSMInput = Union[IngestResult, pd.DataFrame, Iterable[ModbusRecord]]
"""Accepted inputs for :func:`evaluate_tier1`."""

DEFAULT_MAX_OUTSTANDING: Final[int] = 64
"""Open transactions retained per conversation before the oldest is evicted."""

DEFAULT_TID_HISTORY: Final[int] = 256
"""Recently closed transaction IDs remembered per conversation."""


# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------


class SessionState(str, Enum):
    """State of one Modbus/TCP conversation."""

    IDLE = "idle"
    """No transaction is in flight."""

    REQUEST_SENT = "request_sent"
    """Exactly one transaction is in flight."""

    WAITING_RESPONSE = "waiting_response"
    """Two or more transactions are in flight (pipelined)."""

    ERROR = "error"
    """The previous event violated a rule; the conversation is quarantined."""


class SymbolClass(str, Enum):
    """Coarse class of an input symbol."""

    REQUEST = "request"
    RESPONSE = "response"


class FSMSymbol(str, Enum):
    """Input symbol derived from the direction and function code of an event."""

    REQUEST_READ_03 = "request_read_03"
    REQUEST_WRITE_SINGLE_06 = "request_write_single_06"
    REQUEST_WRITE_MULTIPLE_10 = "request_write_multiple_10"
    REQUEST_OTHER = "request_other"
    RESPONSE_READ_03 = "response_read_03"
    RESPONSE_WRITE_SINGLE_06 = "response_write_single_06"
    RESPONSE_WRITE_MULTIPLE_10 = "response_write_multiple_10"
    RESPONSE_OTHER = "response_other"
    RESPONSE_EXCEPTION = "response_exception"


SYMBOL_CLASSES: Final[Mapping[FSMSymbol, SymbolClass]] = MappingProxyType(
    {
        FSMSymbol.REQUEST_READ_03: SymbolClass.REQUEST,
        FSMSymbol.REQUEST_WRITE_SINGLE_06: SymbolClass.REQUEST,
        FSMSymbol.REQUEST_WRITE_MULTIPLE_10: SymbolClass.REQUEST,
        FSMSymbol.REQUEST_OTHER: SymbolClass.REQUEST,
        FSMSymbol.RESPONSE_READ_03: SymbolClass.RESPONSE,
        FSMSymbol.RESPONSE_WRITE_SINGLE_06: SymbolClass.RESPONSE,
        FSMSymbol.RESPONSE_WRITE_MULTIPLE_10: SymbolClass.RESPONSE,
        FSMSymbol.RESPONSE_OTHER: SymbolClass.RESPONSE,
        FSMSymbol.RESPONSE_EXCEPTION: SymbolClass.RESPONSE,
    }
)
"""Symbol -> symbol class, used to look up a transition rule."""


class TransitionTarget(str, Enum):
    """Result of a state transition rule."""

    IDLE = "idle"
    REQUEST_SENT = "request_sent"
    WAITING_RESPONSE = "waiting_response"
    DERIVED = "derived"
    """Recompute the state from the number of transactions still in flight."""

    FORBIDDEN = "forbidden"
    """The symbol class cannot occur in this state."""


TRANSITIONS: Final[Mapping[tuple[SessionState, SymbolClass], TransitionTarget]] = (
    MappingProxyType(
        {
            (SessionState.IDLE, SymbolClass.REQUEST): TransitionTarget.REQUEST_SENT,
            (SessionState.IDLE, SymbolClass.RESPONSE): TransitionTarget.FORBIDDEN,
            (SessionState.REQUEST_SENT, SymbolClass.REQUEST): TransitionTarget.WAITING_RESPONSE,
            (SessionState.REQUEST_SENT, SymbolClass.RESPONSE): TransitionTarget.DERIVED,
            (SessionState.WAITING_RESPONSE, SymbolClass.REQUEST): TransitionTarget.WAITING_RESPONSE,
            (SessionState.WAITING_RESPONSE, SymbolClass.RESPONSE): TransitionTarget.DERIVED,
            (SessionState.ERROR, SymbolClass.REQUEST): TransitionTarget.DERIVED,
            (SessionState.ERROR, SymbolClass.RESPONSE): TransitionTarget.DERIVED,
        }
    )
)
"""Declared state machine: ``(state, symbol class) -> target``.

A pair that is absent from this table is an *undefined transition* and is
reported as :attr:`FSMReason.UNDEFINED_TRANSITION` rather than silently
accepted. The concrete targets for request symbols agree with the state
derived from the number of in-flight transactions; ``tests/test_fsm.py``
asserts that agreement so the table cannot drift away from the engine.
"""


class FSMReason(str, Enum):
    """Stable reason codes for hard violations."""

    RESPONSE_WITHOUT_REQUEST = "response_without_request"
    RESPONSE_AFTER_CLOSE = "response_after_close"
    FUNCTION_CODE_MISMATCH = "function_code_mismatch"
    UNIT_ID_MISMATCH = "unit_id_mismatch"
    EXCEPTION_LENGTH_INVALID = "exception_length_invalid"
    TRANSACTION_ID_REUSE = "transaction_id_reuse"
    UNDEFINED_TRANSITION = "undefined_transition"
    FORBIDDEN_TRANSITION = "forbidden_transition"
    SESSION_IN_ERROR = "session_in_error"
    UNSUPPORTED_FUNCTION_CODE = "unsupported_function_code"
    DIRECTION_UNRESOLVED = "direction_unresolved"


class FSMNote(str, Enum):
    """Soft observations: counted for auditing, never scored as violations."""

    INCOMPLETE_TRANSACTION = "incomplete_transaction"
    OUTSTANDING_EVICTED = "outstanding_evicted"
    TRANSACTION_EXPIRED = "transaction_expired"
    DIRECTION_INFERRED = "direction_inferred"
    DIRECTION_CONFLICT = "direction_conflict"
    SESSION_EVICTED = "session_evicted"


class RoleSource(str, Enum):
    """Evidence used to decide whether an event is a request or a response."""

    PORTS = "ports"
    """The Modbus port identifies the server end of the flow."""

    DECLARED = "declared"
    """The ``direction`` column named the role."""

    LEARNED = "learned"
    """An earlier event on the same connection established the roles."""

    DEFAULT = "default"
    """Nothing was available; the event is treated as a request."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _require_positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be an integer >= 1")
    return int(value)


def _require_optional_positive_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    return _require_positive_int(value, name)


def _require_positive_seconds(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive finite number")
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return seconds


def _require_optional_positive_seconds(value: object, name: str) -> float | None:
    if value is None:
        return None
    return _require_positive_seconds(value, name)


def _require_aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a timezone-aware datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


@dataclass(frozen=True, slots=True)
class FSMConfig:
    """Policy knobs for the Tier-1 engine.

    Defaults are permissive enough to run on request-only captures without
    producing false positives: any function code is accepted, unanswered
    requests are legal, and an unresolvable direction is a note rather than a
    violation. Tighten them per plant.
    """

    allowed_ports: frozenset[int] = DEFAULT_ALLOWED_PORTS
    """Ports that identify the Modbus server end of a flow."""

    supported_function_codes: frozenset[int] | None = None
    """Request function codes the plant is allowed to use.

    ``None`` accepts every in-range request code. When set, a request with any
    other base function code is a hard violation.
    """

    max_outstanding: int = DEFAULT_MAX_OUTSTANDING
    """Open transactions kept per conversation before the oldest is evicted.

    At least two are required: a conversation has to be able to hold a
    request and its successor so the pipelined state is reachable and the
    declared transition table stays consistent with the engine.
    """

    tid_history: int = DEFAULT_TID_HISTORY
    """Recently closed transaction IDs remembered per conversation.

    Reuse of a transaction ID inside this window is a hard violation; reuse
    beyond it is legitimate wrap-around of the 16-bit transaction ID space.
    """

    max_sessions: int | None = None
    """Hard cap on tracked conversations; the least recently used is evicted."""

    response_timeout: float | None = None
    """Seconds after which an unanswered transaction is considered expired.

    Expiry is measured on event timestamps, never on the wall clock, so batch
    runs stay deterministic. It is off by default.
    """

    strict_direction: bool = False
    """Treat an unresolvable direction as a hard violation.

    A direction is resolved when the Modbus port identifies the server
    endpoint, or when the ``direction`` column states it. A role merely
    *learned* from an earlier event counts as unresolved here, because the
    earlier event was itself unproven.
    """

    def __post_init__(self) -> None:
        if not isinstance(self.allowed_ports, frozenset):
            object.__setattr__(self, "allowed_ports", frozenset(self.allowed_ports))
        if not self.allowed_ports:
            raise ValueError("allowed_ports must contain at least one port")
        for port in self.allowed_ports:
            if not PORT_MIN <= int(port) <= PORT_MAX:
                raise ValueError(f"allowed_ports contains invalid port: {port}")
        outstanding = _require_positive_int(self.max_outstanding, "max_outstanding")
        if outstanding < 2:
            raise ValueError(
                "max_outstanding must be at least 2 so a conversation can hold a "
                "request and its successor"
            )
        object.__setattr__(self, "max_outstanding", outstanding)
        object.__setattr__(self, "tid_history", _require_positive_int(self.tid_history, "tid_history"))
        object.__setattr__(
            self, "max_sessions", _require_optional_positive_int(self.max_sessions, "max_sessions")
        )
        object.__setattr__(
            self,
            "response_timeout",
            _require_optional_positive_seconds(self.response_timeout, "response_timeout"),
        )
        if self.supported_function_codes is not None:
            codes = frozenset(int(code) for code in self.supported_function_codes)
            for code in codes:
                if not 1 <= code <= 0x7F:
                    raise ValueError(f"supported_function_codes contains invalid code: {code}")
            object.__setattr__(self, "supported_function_codes", codes)


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConversationKey:
    """Identity of one Modbus/TCP conversation, independent of direction.

    ``client_ip`` is the initiator and ``server_ip`` the responder, so a
    request and its response share one key. For a request-only capture the
    label is identical to the record's directional ``flow_key``.
    """

    client_ip: str
    server_ip: str
    tcp_connection: str

    @property
    def label(self) -> str:
        """Stable, human-readable key, matching the ``flow_key`` spelling."""
        return f"{self.client_ip}|{self.server_ip}|{self.tcp_connection}"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.label


@dataclass(frozen=True, slots=True)
class Transaction:
    """One request awaiting its response."""

    transaction_id: int
    function_code: int
    unit_id: int | None
    timestamp: datetime


@dataclass(slots=True)
class _Conversation:
    """Mutable per-conversation state held by the engine."""

    key: ConversationKey
    state: SessionState = SessionState.IDLE
    outstanding: "OrderedDict[int, Transaction]" = field(default_factory=OrderedDict)
    closed: "OrderedDict[int, None]" = field(default_factory=OrderedDict)
    last_seen: datetime | None = None

    def remember_closed(self, transaction_id: int, limit: int) -> None:
        """Record a finished transaction ID, keeping the ring at ``limit``."""
        self.closed[transaction_id] = None
        self.closed.move_to_end(transaction_id)
        while len(self.closed) > limit:
            self.closed.popitem(last=False)


@dataclass(frozen=True, slots=True)
class Tier1Verdict:
    """Outcome of the Tier-1 evaluation of one event."""

    raw_index: int
    """Row index of the event in the ingested log."""

    session_id: str
    """Conversation label (``client|server|connection``)."""

    session_key: ConversationKey
    """Structured form of :attr:`session_id`."""

    symbol: FSMSymbol
    """Input symbol derived from direction and function code."""

    symbol_class: SymbolClass
    """Coarse class of :attr:`symbol`."""

    direction: Direction
    """Resolved direction of the event."""

    role_source: RoleSource
    """Evidence used to resolve the direction."""

    transaction_id: int
    function_code: int
    state_before: SessionState
    """Conversation state before the event was evaluated."""

    state_after: SessionState
    """Conversation state after the event was evaluated."""

    outstanding: int
    """Transactions still in flight after the event."""

    reason: FSMReason | None
    """Violation reason, or ``None`` when the event is clean."""

    detail: str
    """Human-readable explanation of the verdict."""

    score: float
    """``1.0`` for a violation, ``0.0`` otherwise."""

    decision: Literal["anomaly", "benign"]
    """Tier-1 decision; ``anomaly`` short-circuits the ML tier."""

    bypass_ml: bool
    """True when the event must not be forwarded to Tier 2/3."""

    notes: tuple[FSMNote, ...] = ()
    """Soft observations attached to the event."""

    @property
    def is_violation(self) -> bool:
        return self.reason is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_index": self.raw_index,
            "session_id": self.session_id,
            "symbol": self.symbol.value,
            "symbol_class": self.symbol_class.value,
            "direction": self.direction,
            "role_source": self.role_source.value,
            "transaction_id": self.transaction_id,
            "function_code": self.function_code,
            "state_before": self.state_before.value,
            "state_after": self.state_after.value,
            "outstanding": self.outstanding,
            "reason": self.reason.value if self.reason is not None else "",
            "detail": self.detail,
            "score": self.score,
            "decision": self.decision,
            "bypass_ml": self.bypass_ml,
            "notes": [note.value for note in self.notes],
        }


@dataclass(frozen=True, slots=True)
class FSMSummary:
    """Aggregate view of one engine run."""

    events: int
    sessions: int
    violations: int
    violation_rate: float
    incomplete_transactions: int
    reasons: Mapping[str, int]
    notes: Mapping[str, int]
    final_states: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "events": self.events,
            "sessions": self.sessions,
            "violations": self.violations,
            "violation_rate": self.violation_rate,
            "incomplete_transactions": self.incomplete_transactions,
            "reasons": dict(self.reasons),
            "notes": dict(self.notes),
            "final_states": dict(self.final_states),
        }

    def summary(self) -> str:
        lines = [
            (
                f"events={self.events} sessions={self.sessions} "
                f"violations={self.violations} ({self.violation_rate:.2%}) "
                f"incomplete={self.incomplete_transactions}"
            )
        ]
        if self.reasons:
            lines.append("violations by reason:")
            for reason, count in sorted(self.reasons.items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  {reason:<30} {count:>8}")
        else:
            lines.append("violations by reason: none")
        if self.notes:
            lines.append("notes:")
            for note, count in sorted(self.notes.items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"  {note:<30} {count:>8}")
        return "\n".join(lines)


VERDICT_COLUMNS: Final[tuple[str, ...]] = (
    "raw_index",
    "fsm_session_id",
    "fsm_client_ip",
    "fsm_server_ip",
    "fsm_state_before",
    "fsm_state_after",
    "fsm_symbol",
    "fsm_symbol_class",
    "fsm_direction",
    "fsm_role_source",
    "fsm_transaction_id",
    "fsm_function_code",
    "fsm_outstanding",
    "fsm_score",
    "fsm_decision",
    "fsm_bypass_ml",
    "fsm_reason",
    "fsm_detail",
    "fsm_notes",
)
"""Columns of the frame produced by :meth:`Tier1Result.to_frame`."""

_VERDICT_DTYPES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "raw_index": "int64",
        "fsm_session_id": "string",
        "fsm_client_ip": "string",
        "fsm_server_ip": "string",
        "fsm_state_before": "string",
        "fsm_state_after": "string",
        "fsm_symbol": "string",
        "fsm_symbol_class": "string",
        "fsm_direction": "string",
        "fsm_role_source": "string",
        "fsm_transaction_id": "int64",
        "fsm_function_code": "int64",
        "fsm_outstanding": "int64",
        "fsm_score": "float64",
        "fsm_decision": "string",
        "fsm_bypass_ml": "bool",
        "fsm_reason": "string",
        "fsm_detail": "string",
        "fsm_notes": "string",
    }
)


@dataclass(slots=True)
class Tier1Result:
    """Verdicts for a batch of events, in input order."""

    verdicts: tuple[Tier1Verdict, ...]

    def __len__(self) -> int:
        return len(self.verdicts)

    def __iter__(self):
        return iter(self.verdicts)

    @property
    def scores(self) -> np.ndarray:
        """Tier-1 score per event as float64 (``1.0`` = violation)."""
        return np.array([verdict.score for verdict in self.verdicts], dtype=np.float64)

    @property
    def decisions(self) -> np.ndarray:
        """Tier-1 decision per event."""
        return np.array([verdict.decision for verdict in self.verdicts], dtype=object).astype("U7")

    @property
    def anomaly_mask(self) -> np.ndarray:
        """Boolean mask of the events that violated a rule."""
        return np.array([verdict.is_violation for verdict in self.verdicts], dtype=bool)

    @property
    def reasons(self) -> Counter[FSMReason]:
        """Histogram of violation reasons."""
        counter: Counter[FSMReason] = Counter()
        for verdict in self.verdicts:
            if verdict.reason is not None:
                counter[verdict.reason] += 1
        return counter

    @property
    def n_violations(self) -> int:
        return sum(1 for verdict in self.verdicts if verdict.is_violation)

    @property
    def violation_rate(self) -> float:
        return self.n_violations / len(self.verdicts) if self.verdicts else 0.0

    @property
    def n_sessions(self) -> int:
        return len({verdict.session_id for verdict in self.verdicts})

    def to_frame(self) -> pd.DataFrame:
        """Tabular verdicts with pinned columns and dtypes.

        The empty result has exactly the same schema as a populated one, so
        downstream code never has to special-case an empty capture.
        """
        rows = []
        for verdict in self.verdicts:
            rows.append(
                {
                    "raw_index": verdict.raw_index,
                    "fsm_session_id": verdict.session_id,
                    "fsm_client_ip": verdict.session_key.client_ip,
                    "fsm_server_ip": verdict.session_key.server_ip,
                    "fsm_state_before": verdict.state_before.value,
                    "fsm_state_after": verdict.state_after.value,
                    "fsm_symbol": verdict.symbol.value,
                    "fsm_symbol_class": verdict.symbol_class.value,
                    "fsm_direction": verdict.direction,
                    "fsm_role_source": verdict.role_source.value,
                    "fsm_transaction_id": verdict.transaction_id,
                    "fsm_function_code": verdict.function_code,
                    "fsm_outstanding": verdict.outstanding,
                    "fsm_score": verdict.score,
                    "fsm_decision": verdict.decision,
                    "fsm_bypass_ml": verdict.bypass_ml,
                    "fsm_reason": verdict.reason.value if verdict.reason is not None else "",
                    "fsm_detail": verdict.detail,
                    "fsm_notes": ";".join(note.value for note in verdict.notes),
                }
            )
        frame = pd.DataFrame.from_records(rows, columns=list(VERDICT_COLUMNS))
        for column, dtype in _VERDICT_DTYPES.items():
            if dtype == "string":
                frame[column] = frame[column].astype("string")
            elif dtype == "bool":
                frame[column] = frame[column].astype("bool")
            else:
                frame[column] = frame[column].astype(dtype)
        return frame

    def to_dict(self) -> dict[str, Any]:
        return {
            "events": len(self.verdicts),
            "sessions": self.n_sessions,
            "violations": self.n_violations,
            "violation_rate": self.violation_rate,
            "reasons": {reason.value: count for reason, count in self.reasons.items()},
            "verdicts": [verdict.to_dict() for verdict in self.verdicts],
        }

    def summary(self) -> str:
        lines = [
            (
                f"tier1: events={len(self.verdicts)} sessions={self.n_sessions} "
                f"violations={self.n_violations} ({self.violation_rate:.2%})"
            )
        ]
        reasons = self.reasons
        if reasons:
            for reason, count in reasons.most_common():
                lines.append(f"  {reason.value:<30} {count:>8}")
        else:
            lines.append("  no violations")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


def _derive_state(outstanding: int) -> SessionState:
    """Session state implied by the number of transactions in flight."""
    if outstanding <= 0:
        return SessionState.IDLE
    if outstanding == 1:
        return SessionState.REQUEST_SENT
    return SessionState.WAITING_RESPONSE


def _symbol_for(record: ModbusRecord, direction: Direction) -> FSMSymbol:
    """Classify an event into an input symbol."""
    base = base_function_code(record.function_code)
    if direction == "request":
        if base == 0x03:
            return FSMSymbol.REQUEST_READ_03
        if base == 0x06:
            return FSMSymbol.REQUEST_WRITE_SINGLE_06
        if base == 0x10:
            return FSMSymbol.REQUEST_WRITE_MULTIPLE_10
        return FSMSymbol.REQUEST_OTHER
    if is_exception_response(record.function_code):
        return FSMSymbol.RESPONSE_EXCEPTION
    if base == 0x03:
        return FSMSymbol.RESPONSE_READ_03
    if base == 0x06:
        return FSMSymbol.RESPONSE_WRITE_SINGLE_06
    if base == 0x10:
        return FSMSymbol.RESPONSE_WRITE_MULTIPLE_10
    return FSMSymbol.RESPONSE_OTHER


@dataclass(frozen=True, slots=True)
class _Resolution:
    """Direction and conversation roles resolved for one event."""

    direction: Direction
    role_source: RoleSource
    client_ip: str
    server_ip: str
    notes: tuple[FSMNote, ...]
    proven: bool = True
    """Whether the endpoint roles rest on evidence rather than on a guess."""


class ModbusFSM:
    """Stateful Tier-1 protocol validator for Modbus/TCP conversations.

    The engine is stateful for streaming use via :meth:`observe`;
    :meth:`evaluate` processes a complete batch and resets first. It is not
    thread-safe: use one instance per stream.

    Args:
        config: Policy knobs; the defaults are permissive enough for
            request-only captures.
    """

    def __init__(self, config: FSMConfig | None = None) -> None:
        self.config = config or FSMConfig()
        self._conversations: dict[ConversationKey, _Conversation] = {}
        self._touches: dict[ConversationKey, int] = {}
        self._touch_serial = 0
        self._roles: "OrderedDict[tuple[str, str, str], tuple[str, str, bool]]" = OrderedDict()
        self._reasons: Counter[FSMReason] = Counter()
        self._notes: Counter[FSMNote] = Counter()
        self._events = 0
        self._violations = 0
        self._latest_timestamp: datetime | None = None
        self._evicted_sessions = 0

    # -- lifecycle ----------------------------------------------------------
    def reset(self) -> None:
        """Drop every conversation, learned role and counter."""
        self._conversations.clear()
        self._touches.clear()
        self._touch_serial = 0
        self._roles.clear()
        self._reasons.clear()
        self._notes.clear()
        self._events = 0
        self._violations = 0
        self._latest_timestamp = None
        self._evicted_sessions = 0

    @property
    def session_count(self) -> int:
        return len(self._conversations)

    @property
    def active_sessions(self) -> tuple[ConversationKey, ...]:
        return tuple(self._conversations)

    @property
    def conversation_states(self) -> dict[ConversationKey, SessionState]:
        """Current state of every tracked conversation."""
        return {key: conversation.state for key, conversation in self._conversations.items()}

    @property
    def evicted_sessions(self) -> int:
        """Conversations evicted by the LRU cap or by :meth:`prune`."""
        return self._evicted_sessions

    @property
    def outstanding_count(self) -> int:
        """Transactions still awaiting a response across all conversations."""
        return sum(len(item.outstanding) for item in self._conversations.values())

    def prune(self, reference: datetime | None = None, *, idle_timeout: float | None = None) -> int:
        """Evict conversations whose newest event is older than the cutoff.

        Args:
            reference: Timezone-aware reference instant. Defaults to the
                latest timestamp this engine observed, which keeps offline runs
                deterministic; live callers should pass
                ``datetime.now(timezone.utc)``.
            idle_timeout: Cutoff in seconds. Required, so no retention policy
                is ever invented silently.

        Returns:
            The number of conversations evicted by this call. Conversations
            exactly at the cutoff are retained.
        """
        if idle_timeout is None:
            raise ValueError("idle_timeout is required: no retention policy is invented")
        timeout = _require_positive_seconds(idle_timeout, "idle_timeout")
        instant = (
            self._latest_timestamp
            if reference is None
            else _require_aware(reference, "reference")
        )
        if instant is None:
            return 0
        cutoff = instant - timedelta(seconds=timeout)
        stale = [
            key
            for key, conversation in self._conversations.items()
            if conversation.last_seen is not None and conversation.last_seen < cutoff
        ]
        for key in stale:
            self._evict(key)
        return len(stale)

    def _evict(self, key: ConversationKey) -> bool:
        if key not in self._conversations:
            return False
        del self._conversations[key]
        self._touches.pop(key, None)
        self._evicted_sessions += 1
        return True

    def _trim_roles(self) -> None:
        """Keep the learned-role map within the conversation cap.

        A role belongs to a connection, so the map grows with the number of
        connections seen. The LRU cap that bounds the conversations bounds it
        too, and the roles of the most recently active connections survive.
        """
        limit = self.config.max_sessions
        if limit is None:
            return
        while len(self._roles) > limit:
            self._roles.popitem(last=False)

    def _conversation_for(self, key: ConversationKey) -> tuple[_Conversation, list[FSMNote]]:
        """Fetch or create the conversation, honouring the LRU cap."""
        notes: list[FSMNote] = []
        conversation = self._conversations.get(key)
        if conversation is None:
            if (
                self.config.max_sessions is not None
                and len(self._conversations) >= self.config.max_sessions
            ):
                oldest = min(
                    self._conversations,
                    key=lambda candidate: self._touches.get(candidate, -1),
                )
                self._evict(oldest)
                notes.append(FSMNote.SESSION_EVICTED)
            conversation = _Conversation(key)
            self._conversations[key] = conversation
        self._touch_serial += 1
        self._touches[key] = self._touch_serial
        return conversation, notes

    # -- direction resolution -----------------------------------------------
    def _port_direction(self, record: ModbusRecord) -> Direction | None:
        """Direction implied by which end of the flow carries the Modbus port."""
        allowed = self.config.allowed_ports
        source_is_server = (
            record.source_port is not None
            and record.source_port in allowed
            and not (record.dest_port is not None and record.dest_port in allowed)
        )
        dest_is_server = (
            record.dest_port is not None
            and record.dest_port in allowed
            and not (record.source_port is not None and record.source_port in allowed)
        )
        if dest_is_server:
            return "request"
        if source_is_server:
            return "response"
        return None

    def _roles_key(self, record: ModbusRecord) -> tuple[str, str, str]:
        first, second = sorted((record.source_ip, record.dest_ip))
        return (record.tcp_connection, first, second)

    def _resolve(self, record: ModbusRecord) -> _Resolution:
        """Resolve the message role and the endpoint roles of one event.

        Two independent questions are answered here.

        *Which endpoint is the server?* The endpoint that carries a Modbus
        port is the server, so a request and its response share one
        conversation key. Ports win over the declared ``direction`` column
        because they are objective evidence of the shape of the flow; an
        exporter that mislabels direction still produces one conversation.

        *Is this packet a request or a response?* The Modbus exception flag
        (0x80) settles it on the wire -- only a server ever sets it -- so it
        outranks the exporter's ``direction`` column. Otherwise the ports
        decide, then the declared column, then roles learned from an earlier
        event on the same connection, and finally the request default.
        """
        notes: list[FSMNote] = []
        port_direction = self._port_direction(record)
        declared = record.direction if record.direction in ("request", "response") else None
        exception = is_exception_response(record.function_code)

        # -- endpoint roles: the end carrying the Modbus port is the server ---
        if port_direction is not None:
            if port_direction == "request":
                client_ip, server_ip = record.source_ip, record.dest_ip
            else:
                client_ip, server_ip = record.dest_ip, record.source_ip
            role_source = RoleSource.PORTS
        elif declared is not None:
            if declared == "request":
                client_ip, server_ip = record.source_ip, record.dest_ip
            else:
                client_ip, server_ip = record.dest_ip, record.source_ip
            role_source = RoleSource.DECLARED
        else:
            learned_roles = self._roles.get(self._roles_key(record))
            if learned_roles is not None:
                client_ip, server_ip, proven = learned_roles
                role_source = RoleSource.LEARNED
                self._roles.move_to_end(self._roles_key(record))
            else:
                client_ip, server_ip = record.source_ip, record.dest_ip
                role_source = RoleSource.DEFAULT
                proven = False
        if role_source in (RoleSource.PORTS, RoleSource.DECLARED):
            proven = True
        self._roles[self._roles_key(record)] = (client_ip, server_ip, proven)
        self._roles.move_to_end(self._roles_key(record))
        self._trim_roles()

        # -- message role -----------------------------------------------------
        if exception:
            direction: Direction = "response"
            if port_direction == "request" or (
                port_direction is None and declared == "request"
            ):
                notes.append(FSMNote.DIRECTION_CONFLICT)
        elif port_direction is not None:
            direction = port_direction
            if declared is not None and declared != port_direction:
                notes.append(FSMNote.DIRECTION_CONFLICT)
        elif declared is not None:
            direction = declared
        else:
            direction = "request" if record.source_ip == client_ip else "response"
            notes.append(FSMNote.DIRECTION_INFERRED)

        return _Resolution(
            direction=direction,
            role_source=role_source,
            client_ip=client_ip,
            server_ip=server_ip,
            notes=tuple(notes),
            proven=proven,
        )

    # -- rule evaluation ----------------------------------------------------
    def _expire(self, conversation: _Conversation, now: datetime) -> list[FSMNote]:
        """Expire transactions that outlived the configured response timeout."""
        timeout = self.config.response_timeout
        if timeout is None:
            return []
        cutoff = now - timedelta(seconds=timeout)
        expired = [
            transaction_id
            for transaction_id, transaction in conversation.outstanding.items()
            if transaction.timestamp < cutoff
        ]
        if not expired:
            return []
        for transaction_id in expired:
            del conversation.outstanding[transaction_id]
            conversation.remember_closed(transaction_id, self.config.tid_history)
        return [FSMNote.TRANSACTION_EXPIRED] * len(expired)

    def _apply_request(
        self, conversation: _Conversation, record: ModbusRecord
    ) -> tuple[FSMReason | None, str, list[FSMNote]]:
        """Evaluate a request against the open transactions of a conversation."""
        notes: list[FSMNote] = []
        transaction_id = record.transaction_id

        supported = self.config.supported_function_codes
        if supported is not None and base_function_code(record.function_code) not in supported:
            return (
                FSMReason.UNSUPPORTED_FUNCTION_CODE,
                f"function code 0x{record.function_code:02X} is not in the supported set",
                notes,
            )

        if transaction_id in conversation.outstanding:
            return (
                FSMReason.TRANSACTION_ID_REUSE,
                f"transaction {transaction_id} is still awaiting a response",
                notes,
            )
        if transaction_id in conversation.closed:
            return (
                FSMReason.TRANSACTION_ID_REUSE,
                f"transaction {transaction_id} was already completed recently",
                notes,
            )

        if len(conversation.outstanding) >= self.config.max_outstanding:
            conversation.outstanding.popitem(last=False)
            notes.append(FSMNote.OUTSTANDING_EVICTED)

        conversation.outstanding[transaction_id] = Transaction(
            transaction_id=transaction_id,
            function_code=record.function_code,
            unit_id=record.unit_id,
            timestamp=record.timestamp,
        )
        return None, "", notes

    def _apply_response(
        self, conversation: _Conversation, record: ModbusRecord, *, quarantined: bool
    ) -> tuple[FSMReason | None, str, list[FSMNote]]:
        """Evaluate a response against the open transactions of a conversation."""
        notes: list[FSMNote] = []
        transaction_id = record.transaction_id
        transaction = conversation.outstanding.get(transaction_id)

        if transaction is None:
            if quarantined:
                return (
                    FSMReason.SESSION_IN_ERROR,
                    f"conversation is in error and transaction {transaction_id} has no open request",
                    notes,
                )
            if transaction_id in conversation.closed:
                return (
                    FSMReason.RESPONSE_AFTER_CLOSE,
                    f"transaction {transaction_id} was already answered",
                    notes,
                )
            return (
                FSMReason.RESPONSE_WITHOUT_REQUEST,
                f"no open request for transaction {transaction_id}",
                notes,
            )

        expected = transaction.function_code
        if record.function_code not in (expected, expected | EXCEPTION_FLAG):
            return (
                FSMReason.FUNCTION_CODE_MISMATCH,
                (
                    f"response function code 0x{record.function_code:02X} does not match "
                    f"request 0x{expected:02X} for transaction {transaction_id}"
                ),
                notes,
            )

        if (
            is_exception_response(record.function_code)
            and record.data_length != EXCEPTION_RESPONSE_LENGTH
        ):
            return (
                FSMReason.EXCEPTION_LENGTH_INVALID,
                (
                    f"exception response for transaction {transaction_id} has length "
                    f"{record.data_length}, expected {EXCEPTION_RESPONSE_LENGTH}"
                ),
                notes,
            )

        if (
            transaction.unit_id is not None
            and record.unit_id is not None
            and transaction.unit_id != record.unit_id
        ):
            return (
                FSMReason.UNIT_ID_MISMATCH,
                (
                    f"response unit id {record.unit_id} does not match request unit id "
                    f"{transaction.unit_id} for transaction {transaction_id}"
                ),
                notes,
            )

        del conversation.outstanding[transaction_id]
        conversation.remember_closed(transaction_id, self.config.tid_history)
        return None, "", notes

    # -- public API ---------------------------------------------------------
    def observe(self, record: ModbusRecord) -> Tier1Verdict:
        """Evaluate one event and return its verdict.

        The event is folded into the state of its conversation. A violation
        leaves the open transactions untouched -- so a well-formed response can
        still complete the request -- but moves the conversation to
        :attr:`SessionState.ERROR` until the next valid event recovers it.

        Raises:
            TypeError: If ``record`` is not a :class:`ModbusRecord`.
        """
        if not isinstance(record, ModbusRecord):
            raise TypeError(f"expected ModbusRecord, got {type(record).__name__}")

        self._events += 1
        resolution = self._resolve(record)
        key = ConversationKey(
            client_ip=resolution.client_ip,
            server_ip=resolution.server_ip,
            tcp_connection=record.tcp_connection,
        )
        conversation, eviction_notes = self._conversation_for(key)
        state_before = conversation.state
        symbol = _symbol_for(record, resolution.direction)
        symbol_class = SYMBOL_CLASSES[symbol]
        notes = list(resolution.notes)
        notes.extend(eviction_notes)
        notes.extend(self._expire(conversation, record.timestamp))

        reason: FSMReason | None = None
        detail = ""
        state_after = state_before

        if self.config.strict_direction and not resolution.proven:
            reason = FSMReason.DIRECTION_UNRESOLVED
            detail = (
                "direction could not be resolved from a Modbus port or the "
                "direction column"
            )
        else:
            target = TRANSITIONS.get((state_before, symbol_class))
            if target is None:
                reason = FSMReason.UNDEFINED_TRANSITION
                detail = (
                    f"no transition is defined for {state_before.value} + "
                    f"{symbol_class.value}"
                )
            else:
                if symbol_class is SymbolClass.REQUEST:
                    reason, detail, extra = self._apply_request(conversation, record)
                else:
                    reason, detail, extra = self._apply_response(
                        conversation,
                        record,
                        quarantined=state_before is SessionState.ERROR,
                    )
                notes.extend(extra)
                if reason is None:
                    if target is TransitionTarget.FORBIDDEN:
                        reason = FSMReason.FORBIDDEN_TRANSITION
                        detail = (
                            f"{symbol_class.value} is not allowed in "
                            f"{state_before.value}"
                        )
                    elif target is TransitionTarget.DERIVED:
                        state_after = _derive_state(len(conversation.outstanding))
                    else:
                        state_after = SessionState(target.value)

        if reason is None:
            conversation.state = state_after
            verdict = Tier1Verdict(
                raw_index=record.raw_index,
                session_id=key.label,
                session_key=key,
                symbol=symbol,
                symbol_class=symbol_class,
                direction=resolution.direction,
                role_source=resolution.role_source,
                transaction_id=record.transaction_id,
                function_code=record.function_code,
                state_before=state_before,
                state_after=state_after,
                outstanding=len(conversation.outstanding),
                reason=None,
                detail=detail,
                score=0.0,
                decision="benign",
                bypass_ml=False,
                notes=tuple(notes),
            )
        else:
            conversation.state = SessionState.ERROR
            self._reasons[reason] += 1
            self._violations += 1
            verdict = Tier1Verdict(
                raw_index=record.raw_index,
                session_id=key.label,
                session_key=key,
                symbol=symbol,
                symbol_class=symbol_class,
                direction=resolution.direction,
                role_source=resolution.role_source,
                transaction_id=record.transaction_id,
                function_code=record.function_code,
                state_before=state_before,
                state_after=SessionState.ERROR,
                outstanding=len(conversation.outstanding),
                reason=reason,
                detail=detail,
                score=1.0,
                decision="anomaly",
                bypass_ml=True,
                notes=tuple(notes),
            )

        conversation.last_seen = record.timestamp
        if self._latest_timestamp is None or record.timestamp > self._latest_timestamp:
            self._latest_timestamp = record.timestamp
        for note in verdict.notes:
            self._notes[note] += 1
        return verdict

    def evaluate(self, source: FSMInput) -> Tier1Result:
        """Evaluate a batch of events.

        State is reset first, so repeated calls never share conversations.
        """
        records = resolve_records(source)
        self.reset()
        verdicts = tuple(self.observe(record) for record in records)
        return Tier1Result(verdicts=verdicts)

    def finish(self) -> FSMSummary:
        """Summarise the run without disturbing the engine state."""
        incomplete = sum(
            len(conversation.outstanding) for conversation in self._conversations.values()
        )
        notes = Counter(self._notes)
        notes[FSMNote.INCOMPLETE_TRANSACTION] = incomplete
        final_states = Counter(
            conversation.state for conversation in self._conversations.values()
        )
        return FSMSummary(
            events=self._events,
            sessions=len(self._conversations),
            violations=self._violations,
            violation_rate=self._violations / self._events if self._events else 0.0,
            incomplete_transactions=incomplete,
            reasons={reason.value: count for reason, count in self._reasons.items()},
            notes={note.value: count for note, count in notes.items()},
            final_states={state.value: count for state, count in final_states.items()},
        )


def evaluate_tier1(source: FSMInput, config: FSMConfig | None = None) -> Tier1Result:
    """Evaluate a batch of events with the Tier-1 FSM engine.

    Args:
        source: An ingestion result, a clean frame, or an iterable of records.
        config: Optional policy overrides.

    Returns:
        A :class:`Tier1Result` aligned row-for-row with the input records.
    """
    return ModbusFSM(config).evaluate(source)
