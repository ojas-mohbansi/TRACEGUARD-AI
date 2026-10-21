"""Session-isolated sliding windows and incremental Phase 1.3 features.

The parser emits clean, timestamp-sorted :class:`~modbus_nids.models.ModbusRecord`
events. This module turns them into per-session behavioural features without
letting interleaved traffic contaminate a window.

The window key is ``(source_ip, dest_ip, tcp_connection)``. The Modbus
transaction ID is deliberately *not* part of that key: it changes on every
request, so including it would create a fresh window per event and erase all
temporal context. TID continuity is instead exposed as ``tid_delta``. Windows
are directional, matching the directional ``flow_key`` from ingestion; request
and response streams therefore form separate sessions unless the caller
normalises endpoints before ingest.

Sessions are bounded in memory in three independent ways:

* every window retains at most ``window_size`` events;
* an optional ``idle_timeout`` restarts one session when *its own* inter-event
  gap exceeds the timeout (safe under interleaved traffic);
* an optional ``max_sessions`` cap evicts the least-recently-used session when a
  new session would exceed it, and :meth:`SessionWindowManager.prune` performs
  explicit idle sweeps for long-running stream managers.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Final, Iterable

import pandas as pd

from .models import ModbusRecord

DEFAULT_WINDOW_SIZE: Final[int] = 10
"""Number of trailing events retained per TCP session."""

DEFAULT_EPSILON: Final[float] = 1e-6
"""Seconds added inside the log transform to keep zero deltas finite."""

NGRAM_SIZES: Final[tuple[int, ...]] = (2, 3, 5)
"""Symbol n-gram lengths tracked by the baseline extractor."""

WRITE_FUNCTION_CODES: Final[frozenset[int]] = frozenset({0x05, 0x06, 0x0F, 0x10})
"""Control/write function codes used for the W/R ratio."""

READ_FUNCTION_CODES: Final[frozenset[int]] = frozenset({0x01, 0x02, 0x03, 0x04})
"""Telemetry/read function codes used for the W/R ratio."""

TID_MODULUS: Final[int] = 1 << 16

FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    "dt_seconds",
    "log_dt",
    "is_session_start",
    "tid_delta",
    "window_event_count",
    "window_fill_ratio",
    "write_count",
    "read_count",
    "other_count",
    "write_read_ratio",
    "write_fraction",
    "ngram_unique_2",
    "ngram_unique_3",
    "ngram_unique_5",
    "ngram_novelty_2",
    "ngram_novelty_3",
    "ngram_novelty_5",
)
"""Numeric feature columns produced for every event."""

METADATA_COLUMNS: Final[tuple[str, ...]] = (
    "session_id",
    "source_ip",
    "dest_ip",
    "tcp_connection",
    "timestamp",
    "transaction_id",
    "function_code",
    "register_address",
    "quantity",
    "unit_id",
    "direction",
    "label",
    "raw_index",
)
"""Columns carried through from the clean record for alignment and auditing.

``register_address``, ``quantity``, ``unit_id`` and ``direction`` are retained
for the Tier-1 FSM, which needs register scope and request/response semantics in
addition to the numeric window features. Rows stay aligned with clean records by
``label`` and ``raw_index``.
"""

OUTPUT_COLUMNS: Final[tuple[str, ...]] = METADATA_COLUMNS + FEATURE_COLUMNS

_STRING_METADATA: Final[tuple[str, ...]] = (
    "session_id",
    "source_ip",
    "dest_ip",
    "tcp_connection",
    "direction",
)
_INT64_METADATA: Final[tuple[str, ...]] = (
    "transaction_id",
    "function_code",
    "label",
    "raw_index",
)
_NULLABLE_INT_METADATA: Final[tuple[str, ...]] = (
    "register_address",
    "quantity",
    "unit_id",
)


class WindowError(ValueError):
    """Raised when a session's events arrive out of timestamp order."""


@dataclass(frozen=True, slots=True)
class SessionKey:
    """Identity of one directional Modbus/TCP session."""

    source_ip: str
    dest_ip: str
    tcp_connection: str

    @classmethod
    def from_record(cls, record: ModbusRecord) -> "SessionKey":
        return cls(
            source_ip=record.source_ip,
            dest_ip=record.dest_ip,
            tcp_connection=record.tcp_connection,
        )

    @property
    def label(self) -> str:
        """Stable, human-readable key used as ``session_id`` in output."""
        return f"{self.source_ip}|{self.dest_ip}|{self.tcp_connection}"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.label


def _require_positive_int(value: object, name: str) -> int:
    """Validate an integer-valued configuration knob, rejecting bools."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer >= 1")
    if value < 1:
        raise ValueError(f"{name} must be an integer >= 1")
    return value


def _require_optional_positive_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    return _require_positive_int(value, name)


def _require_positive_seconds(value: object, name: str) -> float:
    """Validate a finite, strictly positive number of seconds."""
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


def _cast_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Pin the public output schema and dtypes for any frame shape.

    Both :meth:`SessionWindowManager.transform` and the empty-input path go
    through this helper, so a zero-row result is schema-identical to a populated
    one instead of relying on pandas' dtype inference.
    """
    frame = frame.copy()
    for column in OUTPUT_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.Series(index=frame.index, dtype="object")
    frame = frame.loc[:, list(OUTPUT_COLUMNS)]

    if frame.empty:
        frame["timestamp"] = pd.Series(dtype="datetime64[ns, UTC]")
    else:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    for column in _STRING_METADATA:
        frame[column] = frame[column].astype("string")
    for column in _INT64_METADATA:
        frame[column] = frame[column].astype("int64")
    for column in _NULLABLE_INT_METADATA:
        frame[column] = frame[column].astype("Int64")
    frame[list(FEATURE_COLUMNS)] = frame[list(FEATURE_COLUMNS)].astype("float64")
    return frame


def _empty_feature_frame() -> pd.DataFrame:
    """Schema-stable empty frame, so ``transform([])`` keeps pinned dtypes."""
    frame = pd.DataFrame({column: pd.Series(dtype="object") for column in OUTPUT_COLUMNS})
    return _cast_feature_frame(frame)


def _ngram_stats(symbols: list[int], n: int) -> tuple[int, float]:
    """Return (unique_count, novelty) for the trailing n-gram of ``symbols``.

    ``novelty`` is 1.0 when the most recent n-gram did not occur earlier in the
    window, 0.0 when it is a repeat, and 0.0 when the window is shorter than n.
    """
    if len(symbols) < n:
        return 0, 0.0
    grams = [tuple(symbols[index : index + n]) for index in range(len(symbols) - n + 1)]
    unique = len(set(grams))
    novelty = 0.0 if grams[-1] in grams[:-1] else 1.0
    return unique, novelty


class SessionWindowManager:
    """Maintains one bounded rolling window per TCP session.

    The manager is stateful for streaming use via :meth:`add`; :meth:`transform`
    processes a complete batch and resets state first. It is not thread-safe.

    Args:
        window_size: Trailing events retained per session (``k``).
        epsilon: Seconds added inside ``log(dt + epsilon)``.
        idle_timeout: Optional per-session idle gap, in seconds. When an event
            arrives more than ``idle_timeout`` after that same session's newest
            event, the stale window is evicted and the event starts a fresh
            session. Other sessions are never compared against this clock.
        max_sessions: Optional hard cap on tracked sessions. Adding a new
            session at the cap evicts the least-recently-used session first.
            This bounds memory but intentionally sacrifices that session's
            temporal context.
    """

    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        epsilon: float = DEFAULT_EPSILON,
        *,
        idle_timeout: float | None = None,
        max_sessions: int | None = None,
    ) -> None:
        self.window_size = _require_positive_int(window_size, "window_size")
        self.epsilon = _require_positive_seconds(epsilon, "epsilon")
        self.idle_timeout = _require_optional_positive_seconds(idle_timeout, "idle_timeout")
        self.max_sessions = _require_optional_positive_int(max_sessions, "max_sessions")
        self._windows: dict[SessionKey, deque[ModbusRecord]] = {}
        self._touches: dict[SessionKey, int] = {}
        self._touch_serial = 0
        self._latest_timestamp: datetime | None = None
        self._evicted_sessions = 0

    # -- lifecycle ----------------------------------------------------------
    def reset(self) -> None:
        """Drop every retained window and reset eviction counters/clock state."""
        self._windows.clear()
        self._touches.clear()
        self._touch_serial = 0
        self._latest_timestamp = None
        self._evicted_sessions = 0

    @property
    def session_count(self) -> int:
        return len(self._windows)

    @property
    def active_sessions(self) -> tuple[SessionKey, ...]:
        return tuple(self._windows)

    @property
    def evicted_sessions(self) -> int:
        """Sessions evicted by idle resets, the LRU cap, or :meth:`prune`.

        The count is cumulative since construction or the last :meth:`reset`.
        """
        return self._evicted_sessions

    def last_seen(self, key: SessionKey) -> datetime | None:
        """Timestamp of the newest retained event for ``key``, if any."""
        window = self._windows.get(key)
        return window[-1].timestamp if window else None

    def _evict(self, key: SessionKey) -> bool:
        """Remove one session, returning whether it existed."""
        if key not in self._windows:
            return False
        del self._windows[key]
        self._touches.pop(key, None)
        self._evicted_sessions += 1
        return True

    def prune(
        self,
        reference: datetime | None = None,
        *,
        idle_timeout: float | None = None,
    ) -> int:
        """Evict sessions whose newest event is older than the idle cutoff.

        Args:
            reference: Timezone-aware reference instant. Defaults to the latest
                timestamp observed by this manager, which makes offline pruning
                deterministic. Live callers should pass
                ``datetime.now(timezone.utc)``.
            idle_timeout: Cutoff in seconds. Defaults to the manager's
                configured ``idle_timeout``; if neither is set, this raises
                ``ValueError`` rather than inventing a retention policy.

        Returns:
            The number of sessions evicted by this call. Sessions exactly at the
            cutoff are retained.
        """
        timeout = (
            _require_positive_seconds(idle_timeout, "idle_timeout")
            if idle_timeout is not None
            else self.idle_timeout
        )
        if timeout is None:
            raise ValueError(
                "prune requires idle_timeout=... or a configured idle_timeout policy"
            )
        instant = self._latest_timestamp if reference is None else _require_aware(
            reference, "reference"
        )
        if instant is None:
            return 0

        cutoff = instant - timedelta(seconds=timeout)
        stale = [
            key
            for key, window in self._windows.items()
            if window and window[-1].timestamp < cutoff
        ]
        for key in stale:
            self._evict(key)
        return len(stale)

    # -- feature computation -------------------------------------------------
    def add(self, record: ModbusRecord) -> dict[str, Any]:
        """Append one event and return its metadata plus feature values.

        The returned mapping uses :data:`OUTPUT_COLUMNS` as its schema. The
        current event is included in the window used for counts and n-grams.

        Raises:
            WindowError: If the timestamp regresses within this session. State
                is left untouched in that case.
        """
        if not isinstance(record, ModbusRecord):
            raise TypeError(f"expected ModbusRecord, got {type(record).__name__}")

        key = SessionKey.from_record(record)
        window = self._windows.get(key)
        previous = window[-1] if window else None

        dt_seconds = 0.0
        if previous is not None:
            dt_seconds = (record.timestamp - previous.timestamp).total_seconds()
            if dt_seconds < 0:
                raise WindowError(
                    f"session {key.label}: timestamp regressed from "
                    f"{previous.timestamp.isoformat()} to {record.timestamp.isoformat()}"
                )
            if self.idle_timeout is not None and dt_seconds > self.idle_timeout:
                # The stream went idle: restart it rather than bridging the gap.
                self._evict(key)
                window = None
                previous = None
                dt_seconds = 0.0

        if window is None:
            if self.max_sessions is not None and len(self._windows) >= self.max_sessions:
                oldest = min(
                    self._windows,
                    key=lambda candidate: self._touches.get(candidate, -1),
                )
                self._evict(oldest)
            window = deque(maxlen=self.window_size)
            self._windows[key] = window
            previous = None

        log_dt = math.log(dt_seconds + self.epsilon)
        is_session_start = 1 if previous is None else 0
        tid_delta = (
            0
            if previous is None
            else (record.transaction_id - previous.transaction_id) % TID_MODULUS
        )

        window.append(record)
        self._touch_serial += 1
        self._touches[key] = self._touch_serial
        if self._latest_timestamp is None or record.timestamp > self._latest_timestamp:
            self._latest_timestamp = record.timestamp

        symbols = [event.function_code for event in window]
        write_count = sum(
            1
            for event in window
            if event.request_function_code in WRITE_FUNCTION_CODES
        )
        read_count = sum(
            1 for event in window if event.request_function_code in READ_FUNCTION_CODES
        )
        other_count = len(window) - write_count - read_count

        ngram_values: dict[str, float | int] = {}
        for n in NGRAM_SIZES:
            unique, novelty = _ngram_stats(symbols, n)
            ngram_values[f"ngram_unique_{n}"] = unique
            ngram_values[f"ngram_novelty_{n}"] = novelty

        return {
            "session_id": key.label,
            "source_ip": record.source_ip,
            "dest_ip": record.dest_ip,
            "tcp_connection": record.tcp_connection,
            "timestamp": record.timestamp,
            "transaction_id": record.transaction_id,
            "function_code": record.function_code,
            "register_address": record.register_address,
            "quantity": record.quantity,
            "unit_id": record.unit_id,
            "direction": record.direction,
            "label": record.label,
            "raw_index": record.raw_index,
            "dt_seconds": dt_seconds,
            "log_dt": log_dt,
            "is_session_start": is_session_start,
            "tid_delta": tid_delta,
            "window_event_count": len(window),
            "window_fill_ratio": len(window) / self.window_size,
            "write_count": write_count,
            "read_count": read_count,
            "other_count": other_count,
            "write_read_ratio": write_count / max(read_count, 1),
            "write_fraction": write_count / max(write_count + read_count, 1),
            **ngram_values,
        }

    def transform(self, records: Iterable[ModbusRecord]) -> pd.DataFrame:
        """Build the aligned feature frame for ``records``.

        State is reset first, so repeated calls never share windows.
        """
        self.reset()
        rows = [self.add(record) for record in records]
        if not rows:
            return _empty_feature_frame()
        frame = pd.DataFrame.from_records(rows, columns=list(OUTPUT_COLUMNS))
        return _cast_feature_frame(frame)

    def window_for(self, key: SessionKey) -> tuple[ModbusRecord, ...]:
        """Return a snapshot of the retained events for ``key``."""
        window = self._windows.get(key)
        return tuple(window) if window is not None else ()
