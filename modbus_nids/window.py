"""Session-isolated sliding windows and incremental Phase 1.2 features.

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
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
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
    "label",
    "raw_index",
)
"""Columns carried through from the clean record for alignment and auditing."""

OUTPUT_COLUMNS: Final[tuple[str, ...]] = METADATA_COLUMNS + FEATURE_COLUMNS


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


def _empty_feature_frame() -> pd.DataFrame:
    """Schema-stable empty frame, so ``transform([])`` keeps pinned dtypes."""
    frame = pd.DataFrame(columns=list(OUTPUT_COLUMNS))
    frame["timestamp"] = pd.Series(dtype="datetime64[ns, UTC]")
    for column in ("transaction_id", "function_code", "label", "raw_index"):
        frame[column] = pd.Series(dtype="int64")
    for column in FEATURE_COLUMNS:
        frame[column] = pd.Series(dtype="float64")
    return frame[list(OUTPUT_COLUMNS)]


class SessionWindowManager:
    """Maintains one bounded rolling window per TCP session.

    The manager is stateful for streaming use via :meth:`add`; :meth:`transform`
    processes a complete batch and resets state first. It is not thread-safe.
    """

    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        epsilon: float = DEFAULT_EPSILON,
    ) -> None:
        if window_size < 1:
            raise ValueError("window_size must be >= 1")
        if not math.isfinite(epsilon) or epsilon <= 0:
            raise ValueError("epsilon must be a positive finite number")
        self.window_size = window_size
        self.epsilon = epsilon
        self._windows: dict[SessionKey, deque[ModbusRecord]] = {}

    # -- lifecycle ----------------------------------------------------------
    def reset(self) -> None:
        """Drop every retained window; the next event starts a new session."""
        self._windows.clear()

    @property
    def session_count(self) -> int:
        return len(self._windows)

    @property
    def active_sessions(self) -> tuple[SessionKey, ...]:
        return tuple(self._windows)

    # -- feature computation -------------------------------------------------
    def add(self, record: ModbusRecord) -> dict[str, Any]:
        """Append one event and return its metadata plus feature values.

        The returned mapping uses :data:`OUTPUT_COLUMNS` as its schema. The
        current event is included in the window used for counts and n-grams.
        """
        if not isinstance(record, ModbusRecord):
            raise TypeError(f"expected ModbusRecord, got {type(record).__name__}")

        key = SessionKey.from_record(record)
        window = self._windows.setdefault(key, deque(maxlen=self.window_size))
        previous = window[-1] if window else None

        dt_seconds = 0.0
        if previous is not None:
            dt_seconds = (record.timestamp - previous.timestamp).total_seconds()
            if dt_seconds < 0:
                raise WindowError(
                    f"session {key.label}: timestamp regressed from "
                    f"{previous.timestamp.isoformat()} to {record.timestamp.isoformat()}"
                )

        log_dt = math.log(dt_seconds + self.epsilon)
        is_session_start = 1 if previous is None else 0
        tid_delta = (
            0
            if previous is None
            else (record.transaction_id - previous.transaction_id) % TID_MODULUS
        )

        window.append(record)
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
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        # Pin a single numeric dtype so downstream estimators see a stable
        # matrix regardless of which window positions happen to be integral.
        frame[list(FEATURE_COLUMNS)] = frame[list(FEATURE_COLUMNS)].astype("float64")
        return frame

    def window_for(self, key: SessionKey) -> tuple[ModbusRecord, ...]:
        """Return a snapshot of the retained events for ``key``."""
        window = self._windows.get(key)
        return tuple(window) if window is not None else ()
