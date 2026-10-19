"""Row-level coercion and protocol validation for Modbus/TCP logs.

The validator is deliberately strict: a row is either fully well-formed and
protocol-plausible, or it is rejected with one or more stable reason codes. It
never repairs a value silently -- coercion helpers raise ``ValueError`` and the
caller turns those into :class:`ValidationIssue` entries, so the rejection
report explains exactly which field failed and why.
"""

from __future__ import annotations

import ipaddress
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

import pandas as pd

from .constants import (
    BASE_FC_MAX,
    BASE_FC_MIN,
    DIRECTIONS,
    EPOCH_UNIT_BOUNDS,
    EXCEPTION_RESPONSE_LENGTH,
    MAX_VALID_TIMESTAMP_YEAR,
    MBAP_MAX_LENGTH,
    MBAP_MIN_LENGTH,
    MIN_VALID_TIMESTAMP_YEAR,
    MODBUS_PROTOCOL_ID,
    NULLABLE_REQUIRED_COLUMNS,
    PORT_MAX,
    PORT_MIN,
    REGISTER_ADDRESS_MAX,
    REQUIRED_COLUMNS,
    TRANSACTION_ID_MAX,
    UNIT_ID_MAX,
    base_function_code,
    expected_request_length,
    function_code_spec,
    is_exception_response,
)
from .models import (
    Direction,
    IngestConfig,
    ModbusRecord,
    RejectReason,
    ValidationIssue,
    WarningCode,
)


@dataclass(slots=True)
class RowValidation:
    """Outcome of validating one raw row."""

    record: ModbusRecord | None
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[WarningCode] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.record is not None


# ---------------------------------------------------------------------------
# Scalar coercion
# ---------------------------------------------------------------------------


def is_blank(value: Any) -> bool:
    """True for ``None``, NaN/NA, and whitespace-only strings."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def coerce_int(value: Any) -> int:
    """Parse an integer from ints, integral floats, or numeric strings."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value) or not value.is_integer():
            raise ValueError(f"not an integer: {value!r}")
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("empty value, expected an integer")
        try:
            return int(text, 10)
        except ValueError:
            number = _maybe_float(text)
            if number is None or not number.is_integer():
                raise ValueError(f"not an integer: {value!r}") from None
            return int(number)
    if hasattr(value, "item"):  # numpy scalar
        return coerce_int(value.item())
    raise ValueError(f"not an integer: {value!r}")


def coerce_optional_int(value: Any) -> int | None:
    """Like :func:`coerce_int` but blank values become ``None``."""
    return None if is_blank(value) else coerce_int(value)


def coerce_ip(value: Any) -> str:
    """Validate and canonicalise an IPv4/IPv6 address."""
    text = str(value).strip()
    if not text:
        raise ValueError("empty IP address")
    try:
        return str(ipaddress.ip_address(text))
    except ValueError:
        raise ValueError(f"invalid IP address: {text!r}") from None


def _maybe_float(text: str) -> float | None:
    try:
        number = float(text)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def _from_epoch(value: float) -> datetime:
    for bound, unit in EPOCH_UNIT_BOUNDS:
        if abs(value) < bound:
            scale = {"s": 1.0, "ms": 1e3, "us": 1e6, "ns": 1e9}[unit]
            try:
                return datetime.fromtimestamp(value / scale, tz=timezone.utc)
            except (OverflowError, OSError, ValueError):
                raise ValueError(f"epoch timestamp out of range: {value!r}") from None
    raise ValueError(f"epoch timestamp out of range: {value!r}")


_EXTRA_TIMESTAMP_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%b %d %Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
)


def coerce_timestamp(value: Any, *, assume_naive_utc: bool = True) -> datetime:
    """Parse ISO-8601 text, epoch numbers, or datetimes into aware UTC.

    Naive values are assumed UTC when ``assume_naive_utc`` is set; otherwise
    they are rejected so a misconfigured export cannot silently shift time.
    """
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if not text:
            raise ValueError("empty timestamp")
        parsed = None
        number = _maybe_float(text)
        if number is not None:
            parsed = _from_epoch(number)
        else:
            iso_text = text[:-1] + "+00:00" if text[-1:] in ("Z", "z") else text
            try:
                parsed = datetime.fromisoformat(iso_text)
            except ValueError:
                parsed = None
            if parsed is None:
                for fmt in _EXTRA_TIMESTAMP_FORMATS:
                    try:
                        parsed = datetime.strptime(text, fmt)
                        break
                    except ValueError:
                        continue
            if parsed is None:
                try:
                    fallback = pd.to_datetime(text, utc=True, errors="coerce")
                except (ValueError, TypeError):
                    fallback = pd.NaT
                if not isinstance(fallback, pd.Timestamp) or pd.isna(fallback):
                    raise ValueError(f"unparseable timestamp: {text!r}")
                parsed = fallback.to_pydatetime()

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        if not assume_naive_utc:
            raise ValueError(f"naive timestamp without timezone: {value!r}")
        parsed = parsed.replace(tzinfo=timezone.utc)
    parsed = parsed.astimezone(timezone.utc)
    if not MIN_VALID_TIMESTAMP_YEAR <= parsed.year <= MAX_VALID_TIMESTAMP_YEAR:
        raise ValueError(
            f"timestamp year {parsed.year} outside "
            f"{MIN_VALID_TIMESTAMP_YEAR}..{MAX_VALID_TIMESTAMP_YEAR}"
        )
    return parsed


# ---------------------------------------------------------------------------
# Row validation
# ---------------------------------------------------------------------------


def _directional(value: Any) -> Direction:
    text = "unknown" if is_blank(value) else str(value).strip().lower()
    return text if text in DIRECTIONS else "unknown"  # type: ignore[return-value]


def validate_row(
    row: Mapping[str, Any],
    *,
    raw_index: int = -1,
    config: IngestConfig | None = None,
) -> RowValidation:
    """Validate one canonical row and build a :class:`ModbusRecord` when clean.

    Every failing check contributes its own issue, so a row that is missing an
    IP *and* has a bad length reports both instead of stopping at the first.
    """
    config = config or IngestConfig()
    issues: list[ValidationIssue] = []
    warnings: list[WarningCode] = []

    def check(field_name: str, reason: RejectReason, parser: Callable[[Any], Any]) -> Any:
        try:
            return parser(row.get(field_name))
        except (TypeError, ValueError) as exc:
            issues.append(
                ValidationIssue(reason, raw_index, field_name, row.get(field_name), str(exc))
            )
            return None

    def flag(field_name: str, reason: RejectReason, detail: str) -> None:
        issues.append(ValidationIssue(reason, raw_index, field_name, row.get(field_name), detail))

    # 1. Presence of required values (register_address may be null by contract).
    for column in REQUIRED_COLUMNS:
        if column in NULLABLE_REQUIRED_COLUMNS:
            continue
        if is_blank(row.get(column)):
            flag(column, RejectReason.MISSING_FIELD, "required field is blank")

    # 2. Per-field structural parsing.
    timestamp = None if is_blank(row.get("timestamp")) else check(
        "timestamp", RejectReason.BAD_TIMESTAMP,
        lambda value: coerce_timestamp(value, assume_naive_utc=config.assume_naive_utc),
    )
    source_ip = None if is_blank(row.get("source_ip")) else check(
        "source_ip", RejectReason.BAD_IP, coerce_ip
    )
    dest_ip = None if is_blank(row.get("dest_ip")) else check(
        "dest_ip", RejectReason.BAD_IP, coerce_ip
    )

    tcp_connection = "" if is_blank(row.get("tcp_connection")) else str(row["tcp_connection"]).strip()
    if not tcp_connection:
        flag("tcp_connection", RejectReason.BAD_TCP_CONNECTION, "missing connection identifier")

    transaction_id = None if is_blank(row.get("transaction_id")) else check(
        "transaction_id", RejectReason.TID_OUT_OF_RANGE, coerce_int
    )
    if transaction_id is not None and not 0 <= transaction_id <= TRANSACTION_ID_MAX:
        flag(
            "transaction_id",
            RejectReason.TID_OUT_OF_RANGE,
            f"expected 0..{TRANSACTION_ID_MAX}, got {transaction_id}",
        )

    function_code = None if is_blank(row.get("function_code")) else check(
        "function_code", RejectReason.FC_OUT_OF_RANGE, coerce_int
    )
    if function_code is not None and not 0 <= function_code <= 0xFF:
        flag(
            "function_code",
            RejectReason.FC_OUT_OF_RANGE,
            f"function code must fit one byte, got {function_code}",
        )
        function_code = None
    elif function_code is not None and not (
        BASE_FC_MIN <= base_function_code(function_code) <= BASE_FC_MAX
    ):
        flag(
            "function_code",
            RejectReason.FC_OUT_OF_RANGE,
            f"function code {function_code} has no valid request code",
        )
        function_code = None

    register_address = check(
        "register_address", RejectReason.REGISTER_OUT_OF_RANGE, coerce_optional_int
    )
    if register_address is not None and not 0 <= register_address <= REGISTER_ADDRESS_MAX:
        flag(
            "register_address",
            RejectReason.REGISTER_OUT_OF_RANGE,
            f"expected 0..{REGISTER_ADDRESS_MAX}, got {register_address}",
        )

    data_length = None if is_blank(row.get("data_length")) else check(
        "data_length", RejectReason.MBAP_LENGTH_OUT_OF_BOUNDS, coerce_int
    )
    if data_length is not None and not MBAP_MIN_LENGTH <= data_length <= MBAP_MAX_LENGTH:
        flag(
            "data_length",
            RejectReason.MBAP_LENGTH_OUT_OF_BOUNDS,
            f"expected {MBAP_MIN_LENGTH}..{MBAP_MAX_LENGTH}, got {data_length}",
        )

    label = None if is_blank(row.get("label")) else check(
        "label", RejectReason.LABEL_NOT_BINARY, coerce_int
    )
    if label is not None and label not in (0, 1):
        flag("label", RejectReason.LABEL_NOT_BINARY, f"expected 0 or 1, got {label}")

    # 3. Optional enrichment fields.
    source_port = check("source_port", RejectReason.BAD_PORT, coerce_optional_int)
    dest_port = check("dest_port", RejectReason.BAD_PORT, coerce_optional_int)
    for name, port in (("source_port", source_port), ("dest_port", dest_port)):
        if port is not None and not PORT_MIN <= port <= PORT_MAX:
            flag(name, RejectReason.BAD_PORT, f"port outside {PORT_MIN}..{PORT_MAX}: {port}")
    if is_blank(row.get("source_port")):
        source_port = None
    if is_blank(row.get("dest_port")):
        dest_port = None

    protocol_id = 0 if is_blank(row.get("protocol_id")) else check(
        "protocol_id", RejectReason.PROTOCOL_ID_NONZERO, coerce_int
    )
    if protocol_id is not None and not 0 <= protocol_id <= 0xFFFF:
        flag("protocol_id", RejectReason.PROTOCOL_ID_NONZERO, f"protocol id out of range: {protocol_id}")
    unit_id = check("unit_id", RejectReason.INVALID_RECORD, coerce_optional_int)
    if unit_id is not None and not 0 <= unit_id <= UNIT_ID_MAX:
        flag("unit_id", RejectReason.INVALID_RECORD, f"expected 0..{UNIT_ID_MAX}, got {unit_id}")
    quantity = check("quantity", RejectReason.QUANTITY_OUT_OF_BOUNDS, coerce_optional_int)
    if quantity is not None and quantity < 0:
        flag("quantity", RejectReason.QUANTITY_OUT_OF_BOUNDS, f"quantity must be non-negative: {quantity}")
    direction = _directional(row.get("direction"))

    # 4. Modbus framing / port scope.
    ports_present = source_port is not None or dest_port is not None
    if config.strict:
        if protocol_id is not None and protocol_id != MODBUS_PROTOCOL_ID:
            flag(
                "protocol_id",
                RejectReason.PROTOCOL_ID_NONZERO,
                f"Modbus requires protocol id {MODBUS_PROTOCOL_ID}, got {protocol_id}",
            )
        if ports_present:
            allowed = [
                port
                for port in (source_port, dest_port)
                if port is not None and port in config.allowed_ports
            ]
            if not allowed:
                reason = (
                    RejectReason.NOT_MODBUS_FRAMED
                    if protocol_id not in (None, MODBUS_PROTOCOL_ID)
                    else RejectReason.BAD_PORT
                )
                flag(
                    "dest_port",
                    reason,
                    f"neither port in {sorted(config.allowed_ports)}",
                )

    # 5. Function-code specific quantity bounds.
    if function_code is not None and quantity is not None:
        spec = function_code_spec(function_code)
        if spec is not None and spec.min_quantity is not None and spec.max_quantity is not None:
            if not spec.min_quantity <= quantity <= spec.max_quantity:
                flag(
                    "quantity",
                    RejectReason.QUANTITY_OUT_OF_BOUNDS,
                    f"FC{base_function_code(function_code)} allows "
                    f"{spec.min_quantity}..{spec.max_quantity}, got {quantity}",
                )

    # 6. Soft anomalies: counted, never dropped.
    if function_code is not None:
        if function_code_spec(function_code) is None:
            warnings.append(WarningCode.UNKNOWN_FUNCTION_CODE)
        expected = None
        if is_exception_response(function_code):
            if direction == "response":
                expected = EXCEPTION_RESPONSE_LENGTH
        elif direction == "request":
            expected = expected_request_length(function_code, quantity)
        if expected is not None and data_length is not None and data_length != expected:
            warnings.append(WarningCode.LENGTH_INCONSISTENT)

    if issues:
        return RowValidation(None, issues, warnings)

    record = ModbusRecord(
        timestamp=timestamp,
        source_ip=source_ip,
        dest_ip=dest_ip,
        tcp_connection=tcp_connection,
        transaction_id=transaction_id,
        function_code=function_code,
        register_address=register_address,
        data_length=data_length,
        label=label,
        source_port=source_port,
        dest_port=dest_port,
        protocol_id=protocol_id if protocol_id is not None else 0,
        unit_id=unit_id,
        quantity=quantity,
        direction=direction,
        raw_index=raw_index,
    )
    return RowValidation(record, issues, warnings)
