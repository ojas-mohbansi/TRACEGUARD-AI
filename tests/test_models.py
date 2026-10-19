"""Contract tests for the typed ingestion models and protocol constants."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from modbus_nids import IngestConfig, IngestMeta, IngestResult, ModbusRecord, RejectReason
from modbus_nids.constants import (
    ALIAS_TO_CANONICAL,
    CANONICAL_COLUMNS,
    COLUMN_DTYPES,
    MBAP_MAX_LENGTH,
    MBAP_MIN_LENGTH,
    base_function_code,
    expected_request_length,
    is_exception_response,
    normalize_column_name,
)
from modbus_nids.models import (
    RejectionReport,
    ValidationIssue,
    WarningCode,
)

TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def make_record(**overrides: object) -> ModbusRecord:
    defaults: dict[str, object] = {
        "timestamp": TS,
        "source_ip": "192.168.1.10",
        "dest_ip": "192.168.1.20",
        "tcp_connection": "conn-1",
        "transaction_id": 1,
        "function_code": 3,
        "register_address": 100,
        "data_length": 6,
        "label": 0,
        "source_port": 51234,
        "dest_port": 502,
        "quantity": 10,
    }
    defaults.update(overrides)
    return ModbusRecord(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Record invariants
# ---------------------------------------------------------------------------


def test_record_round_trip_and_derived_fields() -> None:
    record = make_record()

    assert record.flow_key == "192.168.1.10|192.168.1.20|conn-1"
    assert record.is_exception_response is False
    assert record.request_function_code == 3
    assert set(record.as_row()) == set(CANONICAL_COLUMNS)
    assert record.as_row()["timestamp"] is TS


def test_exception_response_keeps_flag_and_base_code() -> None:
    record = make_record(function_code=0x83, data_length=3)

    assert record.is_exception_response is True
    assert record.request_function_code == 3
    assert base_function_code(0x83) == 3
    assert is_exception_response(3) is False


def test_optional_fields_default_safely() -> None:
    record = ModbusRecord(
        timestamp=TS,
        source_ip="10.0.0.1",
        dest_ip="10.0.0.2",
        tcp_connection="7",
        transaction_id=0,
        function_code=16,
        register_address=None,
        data_length=MBAP_MIN_LENGTH,
        label=1,
    )

    assert record.source_port is None
    assert record.dest_port is None
    assert record.protocol_id == 0
    assert record.unit_id is None
    assert record.quantity is None
    assert record.direction == "unknown"
    assert record.raw_index == -1


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"timestamp": datetime(2026, 1, 1)}, "timezone-aware"),
        ({"transaction_id": 70000}, "transaction_id"),
        ({"function_code": 0}, "function_code"),
        ({"function_code": -1}, "function_code"),
        ({"function_code": 300}, "function_code"),
        ({"register_address": 70000}, "register_address"),
        ({"data_length": MBAP_MAX_LENGTH + 1}, "data_length"),
        ({"data_length": 1}, "data_length"),
        ({"label": 7}, "binary"),
        ({"source_port": 70000}, "source_port"),
        ({"protocol_id": -1}, "protocol_id"),
        ({"unit_id": 300}, "unit_id"),
        ({"direction": "sideways"}, "direction"),
        ({"source_ip": "  "}, "source_ip"),
    ],
)
def test_record_rejects_invalid_invariants(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        make_record(**overrides)


# ---------------------------------------------------------------------------
# Function-code metadata
# ---------------------------------------------------------------------------


def test_request_lengths_follow_the_pdu_shape() -> None:
    assert expected_request_length(3) == 6
    assert expected_request_length(0x03) == 6
    assert expected_request_length(16, quantity=2) == 11  # 7 + 2 * 2
    assert expected_request_length(15, quantity=1) == 9
    assert expected_request_length(16) is None  # quantity required
    assert expected_request_length(43) == 5  # fixed request, variable response


def test_unknown_but_in_range_function_code_has_no_spec() -> None:
    from modbus_nids.constants import function_code_spec

    assert function_code_spec(9) is None
    assert function_code_spec(0x89) is None


# ---------------------------------------------------------------------------
# Column aliases and dtypes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("SourceIP", "source_ip"),
        ("src_ip", "source_ip"),
        ("TransactionID", "transaction_id"),
        (" tid ", "transaction_id"),
        ("FunctionCode", "function_code"),
        ("RegisterAddress", "register_address"),
        ("MBAP_Length", "data_length"),
        ("Label", "label"),
        ("tcp_conn", "tcp_connection"),
        ("dst_port", "dest_port"),
        ("Qty", "quantity"),
    ],
)
def test_header_alias_folding(header: str, expected: str) -> None:
    assert ALIAS_TO_CANONICAL[normalize_column_name(header)] == expected


def test_every_canonical_column_has_a_dtype() -> None:
    for column in CANONICAL_COLUMNS:
        assert column in COLUMN_DTYPES, column


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def test_config_defaults_are_the_strict_profile() -> None:
    config = IngestConfig()

    assert config.strict is True
    assert config.allowed_ports == frozenset({502})
    assert config.chunk_size == 200_000
    assert config.max_reject_samples == 5
    assert config.drop_exact_duplicates is False
    assert config.sort is True
    assert config.new_report().max_samples == 5


def test_config_coerces_and_validates_ports() -> None:
    config = IngestConfig(allowed_ports={502, 1502})  # type: ignore[arg-type]

    assert config.allowed_ports == frozenset({502, 1502})
    with pytest.raises(ValueError, match="at least one port"):
        IngestConfig(allowed_ports=frozenset())
    with pytest.raises(ValueError, match="invalid port"):
        IngestConfig(allowed_ports=frozenset({70000}))
    with pytest.raises(ValueError, match="chunk_size"):
        IngestConfig(chunk_size=0)


def test_meta_rejects_inconsistent_counts() -> None:
    meta = IngestMeta(source="mem", rows_in=10, rows_clean=7, rows_rejected=3, elapsed_ms=1.5)

    assert meta.to_dict()["rows_rejected"] == 3
    with pytest.raises(ValueError, match="inconsistent"):
        IngestMeta(source="mem", rows_in=10, rows_clean=7, rows_rejected=2, elapsed_ms=1.0)


# ---------------------------------------------------------------------------
# Rejection report
# ---------------------------------------------------------------------------


def build_report() -> RejectionReport:
    report = RejectionReport(max_samples=2)
    report.record_seen(10)
    report.record_clean(6)
    for index in range(3):
        report.add(
            ValidationIssue(
                RejectReason.BAD_IP,
                raw_index=index,
                field="source_ip",
                value=f"10.0.0.{index}",
                detail="not an IP",
            )
        )
    report.add(ValidationIssue(RejectReason.LABEL_NOT_BINARY, raw_index=9, field="label", value=7))
    report.note_warning(WarningCode.LENGTH_INCONSISTENT, 2)
    return report


def test_report_accounts_for_every_row() -> None:
    report = build_report()

    assert report.rows_seen == 10
    assert report.rows_clean == 6
    assert report.rows_rejected == 4
    assert report.rejection_rate == pytest.approx(0.4)
    assert report.counts[RejectReason.BAD_IP] == 3
    assert len(report.samples[RejectReason.BAD_IP]) == 2  # capped
    assert report.warnings[WarningCode.LENGTH_INCONSISTENT] == 2


def test_report_renders_summary_frame_and_json() -> None:
    report = build_report()

    summary = report.summary()
    assert "seen=10 clean=6 rejected=4" in summary
    assert RejectReason.BAD_IP.value in summary
    assert "length_inconsistent" in summary

    frame = report.to_frame()
    assert list(frame.columns) == [
        "count",
        "share_of_rejections",
        "share_of_rows",
        "example",
    ]
    assert frame.loc[RejectReason.BAD_IP.value, "count"] == 3
    assert frame.loc[RejectReason.BAD_IP.value, "share_of_rejections"] == pytest.approx(0.75)

    payload = json.loads(report.to_json())
    assert payload["rows_rejected"] == 4
    assert payload["rejections"][RejectReason.BAD_IP.value] == 3
    assert payload["samples"][RejectReason.BAD_IP.value][0]["field"] == "source_ip"


def test_empty_report_frame_keeps_the_reason_index_contract() -> None:
    frame = RejectionReport().to_frame()

    assert frame.empty
    assert frame.index.name == "reason"
    assert list(frame.columns) == [
        "count",
        "share_of_rejections",
        "share_of_rows",
        "example",
    ]


def test_report_merge_preserves_samples_and_counts() -> None:
    left = RejectionReport(max_samples=2)
    left.record_seen(3)
    left.record_clean(2)
    left.add(ValidationIssue(RejectReason.BAD_PORT, raw_index=1, detail="port 5020"))

    right = RejectionReport(max_samples=2)
    right.record_seen(2)
    right.record_clean(2)

    left.merge(right)
    assert (left.rows_seen, left.rows_clean, left.rows_rejected) == (5, 4, 1)
    assert left.counts[RejectReason.BAD_PORT] == 1


def test_result_requires_frame_record_parity() -> None:
    report = build_report()
    meta = IngestMeta(source="mem", rows_in=10, rows_clean=6, rows_rejected=4, elapsed_ms=2.0)

    import pandas as pd

    with pytest.raises(ValueError, match="length mismatch"):
        IngestResult(frame=pd.DataFrame(), records=[make_record()], report=report, meta=meta)
