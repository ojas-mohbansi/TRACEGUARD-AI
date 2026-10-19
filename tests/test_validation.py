"""Tests for row coercion and the strict protocol validation gate."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from modbus_nids import IngestConfig
from modbus_nids.constants import expected_request_length
from modbus_nids.models import RejectReason, WarningCode
from modbus_nids.validation import coerce_timestamp, validate_row

TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def row(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "timestamp": TS,
        "source_ip": "10.0.0.1",
        "dest_ip": "10.0.0.2",
        "tcp_connection": "conn-1",
        "transaction_id": 1,
        "function_code": 3,
        "register_address": 100,
        "data_length": 6,
        "label": 0,
        "source_port": 40000,
        "dest_port": 502,
        "protocol_id": 0,
        "unit_id": 1,
        "quantity": 10,
        "direction": "request",
    }
    base.update(overrides)
    return base


def reasons(outcome) -> set[RejectReason]:
    return {issue.reason for issue in outcome.issues}


# ---------------------------------------------------------------------------
# Timestamp coercion
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-01-01T00:00:00Z", datetime(2026, 1, 1, tzinfo=timezone.utc)),
        ("2026-01-01T05:30:00+05:30", datetime(2026, 1, 1, tzinfo=timezone.utc)),
        ("2026-01-01 00:00:00", datetime(2026, 1, 1, tzinfo=timezone.utc)),
        (datetime(2026, 1, 1), datetime(2026, 1, 1, tzinfo=timezone.utc)),
        (1767225600, datetime(2026, 1, 1, tzinfo=timezone.utc)),
        (1767225600000, datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ],
)
def test_timestamp_forms_normalise_to_utc(value: Any, expected: datetime) -> None:
    parsed = coerce_timestamp(value)

    assert parsed == expected
    assert parsed.tzinfo is not None
    assert parsed.utcoffset().total_seconds() == 0  # type: ignore[union-attr]


@pytest.mark.parametrize("value", ["not-a-date", "", None, 42, 0.5, 1e30])
def test_bad_timestamps_raise(value: Any) -> None:
    with pytest.raises(ValueError):
        coerce_timestamp(value)


def test_out_of_range_year_is_rejected() -> None:
    with pytest.raises(ValueError, match="outside"):
        coerce_timestamp("1901-01-01T00:00:00Z")


def test_naive_timestamp_policy_is_configurable() -> None:
    with pytest.raises(ValueError, match="naive"):
        coerce_timestamp(datetime(2026, 1, 1), assume_naive_utc=False)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_valid_row_becomes_record() -> None:
    outcome = validate_row(row(), raw_index=7)

    assert outcome.ok
    assert outcome.record is not None
    assert outcome.record.raw_index == 7
    assert outcome.record.flow_key == "10.0.0.1|10.0.0.2|conn-1"
    assert outcome.issues == []


def test_nullable_register_and_missing_ports_are_allowed() -> None:
    outcome = validate_row(
        row(register_address=None, source_port=None, dest_port=None), raw_index=0
    )

    assert outcome.ok
    assert outcome.record is not None
    assert outcome.record.register_address is None
    assert outcome.record.source_port is None


# ---------------------------------------------------------------------------
# Hard rejections
# ---------------------------------------------------------------------------


def test_missing_required_values_are_reported_together() -> None:
    outcome = validate_row(row(timestamp="", source_ip="   "), raw_index=3)

    assert not outcome.ok
    missing = {issue.field for issue in outcome.issues if issue.reason is RejectReason.MISSING_FIELD}
    assert missing == {"timestamp", "source_ip"}


def test_bad_ip_is_rejected() -> None:
    outcome = validate_row(row(dest_ip="10.0.0.999"), raw_index=0)

    assert reasons(outcome) == {RejectReason.BAD_IP}


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({"transaction_id": 70000}, RejectReason.TID_OUT_OF_RANGE),
        ({"transaction_id": -1}, RejectReason.TID_OUT_OF_RANGE),
        ({"function_code": 0}, RejectReason.FC_OUT_OF_RANGE),
        ({"function_code": 300}, RejectReason.FC_OUT_OF_RANGE),
        ({"register_address": 70000}, RejectReason.REGISTER_OUT_OF_RANGE),
        ({"data_length": 1}, RejectReason.MBAP_LENGTH_OUT_OF_BOUNDS),
        ({"data_length": 255}, RejectReason.MBAP_LENGTH_OUT_OF_BOUNDS),
        ({"label": 7}, RejectReason.LABEL_NOT_BINARY),
        ({"protocol_id": 1}, RejectReason.PROTOCOL_ID_NONZERO),
        ({"quantity": -1}, RejectReason.QUANTITY_OUT_OF_BOUNDS),
    ],
)
def test_protocol_bounds(overrides: dict[str, Any], expected: RejectReason) -> None:
    outcome = validate_row(row(**overrides), raw_index=0)

    assert expected in reasons(outcome)


def test_tcp_connection_cannot_be_blank() -> None:
    outcome = validate_row(row(tcp_connection="  "), raw_index=0)

    assert RejectReason.BAD_TCP_CONNECTION in reasons(outcome)


@pytest.mark.parametrize("port", [5020, 8080, 0, 70000])
def test_off_scope_ports_are_rejected(port: int) -> None:
    outcome = validate_row(row(dest_port=port, source_port=40000), raw_index=0)

    assert not outcome.ok
    assert RejectReason.BAD_PORT in reasons(outcome)


def test_non_modbus_framing_uses_its_own_reason() -> None:
    outcome = validate_row(row(dest_port=8080, protocol_id=5), raw_index=0)

    assert not outcome.ok
    assert RejectReason.NOT_MODBUS_FRAMED in reasons(outcome)
    assert RejectReason.PROTOCOL_ID_NONZERO in reasons(outcome)


def test_lenient_profile_skips_port_scope() -> None:
    outcome = validate_row(
        row(dest_port=8080, protocol_id=5), config=IngestConfig(strict=False), raw_index=0
    )

    assert outcome.ok


# ---------------------------------------------------------------------------
# Quantity / length semantics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("function_code", "quantity", "valid"),
    [
        (3, 125, True),
        (3, 126, False),
        (4, 0, False),
        (1, 2000, True),
        (1, 2001, False),
        (2, 2000, True),
        (2, 2001, False),
        (16, 123, True),
        (16, 124, False),
        (15, 1968, True),
        (15, 1969, False),
        (23, 125, True),
        (23, 126, False),
    ],
)
def test_function_specific_quantity_bounds(
    function_code: int, quantity: int, valid: bool
) -> None:
    outcome = validate_row(
        row(function_code=function_code, quantity=quantity), raw_index=0
    )

    if valid:
        assert outcome.ok, outcome.issues
    else:
        assert RejectReason.QUANTITY_OUT_OF_BOUNDS in reasons(outcome)


def test_exception_response_is_structurally_valid() -> None:
    outcome = validate_row(
        row(function_code=0x83, data_length=3, direction="response"), raw_index=0
    )

    assert outcome.ok
    assert outcome.record is not None
    assert outcome.record.is_exception_response


def test_length_consistency_warning() -> None:
    outcome = validate_row(row(function_code=3, data_length=7, direction="request"), raw_index=0)

    assert outcome.ok
    assert WarningCode.LENGTH_INCONSISTENT in outcome.warnings


def test_expected_lengths_match_the_function_table() -> None:
    assert expected_request_length(16, 4) == 15
    assert expected_request_length(15, 1) == 9
    assert expected_request_length(3, 50) == 6


def test_unknown_function_code_warns_but_is_kept() -> None:
    outcome = validate_row(row(function_code=9, quantity=None, data_length=2), raw_index=0)

    assert outcome.ok
    assert WarningCode.UNKNOWN_FUNCTION_CODE in outcome.warnings
