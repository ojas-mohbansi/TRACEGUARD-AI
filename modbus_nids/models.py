"""Typed domain models shared by every stage of the Modbus/TCP NIDS.

The ingestion pipeline converts untrusted log rows into :class:`ModbusRecord`
objects and a strictly typed pandas frame, while accounting for every row it
drops via :class:`RejectionReport`. Later phases (session-isolated sliding
windows, the FSM engine, and the hybrid detector) consume these types directly,
so their invariants are enforced at construction time rather than assumed.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal

import pandas as pd

from .constants import (
    BASE_FC_MAX,
    BASE_FC_MIN,
    DEFAULT_ALLOWED_PORTS,
    DIRECTIONS,
    MBAP_MAX_LENGTH,
    MBAP_MIN_LENGTH,
    PORT_MAX,
    PORT_MIN,
    REGISTER_ADDRESS_MAX,
    TRANSACTION_ID_MAX,
    UNIT_ID_MAX,
    base_function_code,
    is_exception_response,
)

Direction = Literal["request", "response", "unknown"]


class IngestionError(Exception):
    """Base class for fatal ingestion failures (as opposed to rejected rows)."""


class SchemaError(IngestionError):
    """Raised when the input lacks required columns and cannot be parsed at all."""

    def __init__(self, missing: list[str] | tuple[str, ...], observed: list[str] | tuple[str, ...]):
        self.missing = tuple(missing)
        self.observed = tuple(observed)
        super().__init__(
            "input is missing required column(s): "
            + ", ".join(self.missing)
            + " | observed headers: "
            + (", ".join(self.observed) if self.observed else "<none>")
        )


class SourceError(IngestionError):
    """Raised when the data source cannot be read (missing file, bad encoding)."""


class RejectReason(str, Enum):
    """Stable reason codes attached to every dropped row."""

    MISSING_FIELD = "missing_field"
    BAD_TIMESTAMP = "bad_timestamp"
    BAD_IP = "bad_ip"
    BAD_TCP_CONNECTION = "bad_tcp_connection"
    TID_OUT_OF_RANGE = "tid_out_of_range"
    BAD_PORT = "bad_port"
    PROTOCOL_ID_NONZERO = "protocol_id_nonzero"
    MBAP_LENGTH_OUT_OF_BOUNDS = "mbap_length_out_of_bounds"
    FC_OUT_OF_RANGE = "fc_out_of_range"
    REGISTER_OUT_OF_RANGE = "register_out_of_range"
    QUANTITY_OUT_OF_BOUNDS = "quantity_out_of_bounds"
    LABEL_NOT_BINARY = "label_not_binary"
    NOT_MODBUS_FRAMED = "not_modbus_framed"
    DUPLICATE_RECORD = "duplicate_record"
    CSV_PARSE_ERROR = "csv_parse_error"
    INVALID_RECORD = "invalid_record"


class WarningCode(str, Enum):
    """Non-fatal anomalies counted for auditing but kept in the clean frame."""

    LENGTH_INCONSISTENT = "length_inconsistent"
    NON_MONOTONIC_TIMESTAMP = "non_monotonic_timestamp"
    UNKNOWN_FUNCTION_CODE = "unknown_function_code"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A single rejection reason with enough context to triage the raw row."""

    reason: RejectReason
    raw_index: int = -1
    field: str | None = None
    value: Any = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason": self.reason.value,
            "raw_index": self.raw_index,
            "field": self.field,
            "value": None if self.value is None else str(self.value),
            "detail": self.detail,
        }

    def __str__(self) -> str:
        location = f"row {self.raw_index}" if self.raw_index >= 0 else "row ?"
        where = f" field={self.field}" if self.field else ""
        return f"{location}{where}: {self.reason.value} ({self.detail or 'invalid'})"


@dataclass(slots=True)
class RejectionReport:
    """Aggregated, reason-coded accounting of every row the gate rejected.

    ``rows_seen`` and ``rows_clean`` are maintained by the parser; the rejected
    count is derived so the three numbers can never drift apart.
    """

    max_samples: int = 5
    counts: Counter[RejectReason] = field(default_factory=Counter)
    warnings: Counter[WarningCode] = field(default_factory=Counter)
    samples: dict[RejectReason, list[ValidationIssue]] = field(default_factory=dict)
    rows_seen: int = 0
    rows_clean: int = 0

    # -- accounting ---------------------------------------------------------
    @property
    def rows_rejected(self) -> int:
        return self.rows_seen - self.rows_clean

    @property
    def rejection_rate(self) -> float:
        return self.rows_rejected / self.rows_seen if self.rows_seen else 0.0

    def record_seen(self, count: int = 1) -> None:
        self.rows_seen += count

    def record_clean(self, count: int = 1) -> None:
        self.rows_clean += count

    def add(self, issue: ValidationIssue) -> None:
        """Count a rejection and retain up to ``max_samples`` examples."""
        self.counts[issue.reason] += 1
        bucket = self.samples.setdefault(issue.reason, [])
        if len(bucket) < self.max_samples:
            bucket.append(issue)

    def note_warning(self, code: WarningCode, count: int = 1) -> None:
        self.warnings[code] += count

    def merge(self, other: "RejectionReport") -> None:
        """Fold another report (e.g. a chunk) into this one."""
        self.counts.update(other.counts)
        self.warnings.update(other.warnings)
        for reason, issues in other.samples.items():
            bucket = self.samples.setdefault(reason, [])
            for issue in issues:
                if len(bucket) >= self.max_samples:
                    break
                bucket.append(issue)
        self.rows_seen += other.rows_seen
        self.rows_clean += other.rows_clean

    # -- reporting ----------------------------------------------------------
    def summary(self) -> str:
        lines = [
            f"rows seen={self.rows_seen} clean={self.rows_clean} "
            f"rejected={self.rows_rejected} ({self.rejection_rate:.2%})"
        ]
        if self.counts:
            lines.append("rejections by reason:")
            for reason, count in self.counts.most_common():
                example = self.samples.get(reason)
                suffix = f" | e.g. {example[0]}" if example else ""
                lines.append(f"  {reason.value:<26} {count:>8}{suffix}")
        else:
            lines.append("rejections by reason: none")
        if self.warnings:
            lines.append("warnings:")
            for code, count in self.warnings.most_common():
                lines.append(f"  {code.value:<26} {count:>8}")
        return "\n".join(lines)

    def to_frame(self) -> pd.DataFrame:
        """Tabular view: one row per reason code, with share and example."""
        total = self.rows_rejected or 1
        records = [
            {
                "reason": reason.value,
                "count": count,
                "share_of_rejections": count / total,
                "share_of_rows": count / self.rows_seen if self.rows_seen else 0.0,
                "example": str(self.samples[reason][0]) if reason in self.samples else "",
            }
            for reason, count in self.counts.most_common()
        ]
        frame = pd.DataFrame.from_records(
            records, columns=["reason", "count", "share_of_rejections", "share_of_rows", "example"]
        )
        return frame.set_index("reason")

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows_seen": self.rows_seen,
            "rows_clean": self.rows_clean,
            "rows_rejected": self.rows_rejected,
            "rejection_rate": self.rejection_rate,
            "rejections": {reason.value: count for reason, count in self.counts.items()},
            "warnings": {code.value: count for code, count in self.warnings.items()},
            "samples": {
                reason.value: [issue.to_dict() for issue in issues]
                for reason, issues in self.samples.items()
            },
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


@dataclass(frozen=True, slots=True)
class ModbusRecord:
    """One validated Modbus/TCP event, normalized to UTC and canonical fields.

    Construction enforces the structural invariants that later phases rely on,
    so anything that violates the protocol bounds must be rejected before it
    reaches this type.
    """

    timestamp: datetime
    source_ip: str
    dest_ip: str
    tcp_connection: str
    transaction_id: int
    function_code: int
    register_address: int | None
    data_length: int
    label: int
    source_port: int | None = None
    dest_port: int | None = None
    protocol_id: int = 0
    unit_id: int | None = None
    quantity: int | None = None
    direction: Direction = "unknown"
    raw_index: int = -1

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime instance")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        for name in ("source_ip", "dest_ip", "tcp_connection"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not 0 <= self.transaction_id <= TRANSACTION_ID_MAX:
            raise ValueError(f"transaction_id out of range: {self.transaction_id}")
        if not 0 <= self.function_code <= 0xFF:
            raise ValueError(f"function_code must fit one byte: {self.function_code}")
        if not BASE_FC_MIN <= base_function_code(self.function_code) <= BASE_FC_MAX:
            raise ValueError(f"function_code out of range: {self.function_code}")
        if self.register_address is not None and not (
            0 <= self.register_address <= REGISTER_ADDRESS_MAX
        ):
            raise ValueError(f"register_address out of range: {self.register_address}")
        if not MBAP_MIN_LENGTH <= self.data_length <= MBAP_MAX_LENGTH:
            raise ValueError(f"data_length outside MBAP bounds: {self.data_length}")
        if self.label not in (0, 1):
            raise ValueError(f"label must be binary, got {self.label}")
        for name in ("source_port", "dest_port"):
            port = getattr(self, name)
            if port is not None and not PORT_MIN <= port <= PORT_MAX:
                raise ValueError(f"{name} out of range: {port}")
        if not 0 <= self.protocol_id <= 0xFFFF:
            raise ValueError(f"protocol_id out of range: {self.protocol_id}")
        if self.unit_id is not None and not 0 <= self.unit_id <= UNIT_ID_MAX:
            raise ValueError(f"unit_id out of range: {self.unit_id}")
        if self.quantity is not None and self.quantity < 0:
            raise ValueError(f"quantity must be non-negative, got {self.quantity}")
        if self.direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, got {self.direction!r}")

    # -- derived views ------------------------------------------------------
    @property
    def flow_key(self) -> str:
        """Directional flow identifier used to isolate sessions."""
        return f"{self.source_ip}|{self.dest_ip}|{self.tcp_connection}"

    @property
    def is_exception_response(self) -> bool:
        return is_exception_response(self.function_code)

    @property
    def request_function_code(self) -> int:
        return base_function_code(self.function_code)

    def as_row(self) -> dict[str, Any]:
        """Canonical scalar mapping, matching the clean-frame columns."""
        return {
            "timestamp": self.timestamp,
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "tcp_connection": self.tcp_connection,
            "transaction_id": self.transaction_id,
            "function_code": self.function_code,
            "register_address": self.register_address,
            "data_length": self.data_length,
            "label": self.label,
            "source_port": self.source_port,
            "dest_port": self.dest_port,
            "protocol_id": self.protocol_id,
            "unit_id": self.unit_id,
            "quantity": self.quantity,
            "direction": self.direction,
            "flow_key": self.flow_key,
            "raw_index": self.raw_index,
        }


@dataclass(frozen=True, slots=True)
class IngestConfig:
    """Knobs for the validation gate and the parser.

    Defaults implement the strict profile: only Modbus/TCP port traffic or
    explicitly Modbus-framed rows are admitted, and no row is dropped for being
    a retransmission unless ``drop_exact_duplicates`` is enabled.
    """

    strict: bool = True
    allowed_ports: frozenset[int] = DEFAULT_ALLOWED_PORTS
    assume_naive_utc: bool = True
    max_reject_samples: int = 5
    chunk_size: int = 200_000
    drop_exact_duplicates: bool = False
    sort: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.allowed_ports, frozenset):
            object.__setattr__(self, "allowed_ports", frozenset(self.allowed_ports))
        if not self.allowed_ports:
            raise ValueError("allowed_ports must contain at least one port")
        for port in self.allowed_ports:
            if not PORT_MIN <= int(port) <= PORT_MAX:
                raise ValueError(f"allowed_ports contains invalid port: {port}")
        if self.max_reject_samples < 0:
            raise ValueError("max_reject_samples must be non-negative")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

    def new_report(self) -> RejectionReport:
        """Create a report honouring this config's sample cap."""
        return RejectionReport(max_samples=self.max_reject_samples)


@dataclass(frozen=True, slots=True)
class IngestMeta:
    """Provenance and timing for one ingest run."""

    source: str
    rows_in: int
    rows_clean: int
    rows_rejected: int
    elapsed_ms: float
    encoding: str | None = None
    chunks: int = 1

    def __post_init__(self) -> None:
        if self.rows_in < 0 or self.rows_clean < 0 or self.rows_rejected < 0:
            raise ValueError("row counts must be non-negative")
        if self.rows_in != self.rows_clean + self.rows_rejected:
            raise ValueError(
                "row counts are inconsistent: "
                f"{self.rows_in} != {self.rows_clean} + {self.rows_rejected}"
            )
        if self.chunks < 0:
            raise ValueError("chunks must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "rows_in": self.rows_in,
            "rows_clean": self.rows_clean,
            "rows_rejected": self.rows_rejected,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "encoding": self.encoding,
            "chunks": self.chunks,
        }


@dataclass(slots=True)
class IngestResult:
    """The clean frame plus the same rows as typed records and an audit report."""

    frame: pd.DataFrame
    records: list[ModbusRecord]
    report: RejectionReport
    meta: IngestMeta

    def __post_init__(self) -> None:
        if len(self.frame) != len(self.records):
            raise ValueError(
                f"frame/record length mismatch: {len(self.frame)} != {len(self.records)}"
            )

    @property
    def rows_clean(self) -> int:
        return len(self.records)

    def summary(self) -> str:
        """Human-readable run digest, including provenance."""
        meta = self.meta
        return (
            f"source={meta.source} rows_in={meta.rows_in} clean={meta.rows_clean} "
            f"rejected={meta.rows_rejected} elapsed={meta.elapsed_ms:.1f}ms\n"
            + self.report.summary()
        )
