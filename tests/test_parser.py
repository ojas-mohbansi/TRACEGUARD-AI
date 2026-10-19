"""Tests for the ingestion entry points and clean-frame contract."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from modbus_nids import (
    IngestConfig,
    RejectReason,
    SchemaError,
    SourceError,
    WarningCode,
    frame_to_records,
    parse_csv,
    parse_dataframe,
    parse_records,
    records_to_frame,
)
from modbus_nids.constants import CANONICAL_COLUMNS, COLUMN_DTYPES

TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def sample_rows(count: int = 3) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(count):
        rows.append(
            {
                "timestamp": TS + timedelta(seconds=index),
                "source_ip": "10.0.0.1",
                "dest_ip": "10.0.0.2",
                "tcp_connection": "conn-1",
                "transaction_id": index,
                "function_code": 3,
                "register_address": 100 + index,
                "data_length": 6,
                "label": 0,
                "source_port": 40000,
                "dest_port": 502,
                "protocol_id": 0,
                "unit_id": 1,
                "quantity": 10,
                "direction": "request",
            }
        )
    return rows


# ---------------------------------------------------------------------------
# DataFrame ingress
# ---------------------------------------------------------------------------


def test_parse_dataframe_produces_typed_clean_frame() -> None:
    result = parse_dataframe(pd.DataFrame(sample_rows()))

    frame = result.frame
    assert list(frame.columns) == list(CANONICAL_COLUMNS)
    assert str(frame["timestamp"].dtype) == COLUMN_DTYPES["timestamp"]
    assert str(frame["register_address"].dtype) == "Int64"
    assert str(frame["source_ip"].dtype) == "string"
    assert str(frame["label"].dtype) == "int64"
    assert len(frame) == len(result.records) == 3
    assert frame["flow_key"].iloc[0] == "10.0.0.1|10.0.0.2|conn-1"
    assert result.report.rows_rejected == 0


def test_alias_headers_are_mapped() -> None:
    source = pd.DataFrame(
        {
            "Timestamp": [TS],
            "SourceIP": ["10.0.0.1"],
            "DestIP": ["10.0.0.2"],
            "TCPConnection": ["conn-9"],
            "TransactionID": [5],
            "FunctionCode": [6],
            "RegisterAddress": [400],
            "DataLength": [6],
            "Label": [1],
        }
    )

    result = parse_dataframe(source)

    assert len(result.frame) == 1
    row = result.records[0]
    assert row.tcp_connection == "conn-9"
    assert row.register_address == 400
    assert row.label == 1


def test_missing_required_column_raises_schema_error() -> None:
    frame = pd.DataFrame(sample_rows()).drop(columns=["transaction_id"])

    with pytest.raises(SchemaError, match="transaction_id"):
        parse_dataframe(frame)


def test_rejected_rows_are_counted_and_do_not_block_good_rows() -> None:
    rows = sample_rows()
    rows[1]["label"] = 7
    rows[1]["dest_ip"] = "10.0.0.999"
    rows[2]["data_length"] = 300

    result = parse_dataframe(pd.DataFrame(rows))

    assert len(result.frame) == 1
    assert result.report.rows_seen == 3
    assert result.report.rows_clean == 1
    assert result.report.rows_rejected == 2
    assert result.report.counts[RejectReason.LABEL_NOT_BINARY] == 1
    assert result.report.counts[RejectReason.BAD_IP] == 1
    assert result.report.counts[RejectReason.MBAP_LENGTH_OUT_OF_BOUNDS] == 1
    assert "rejected=2" in result.summary()


def test_duplicates_are_kept_unless_requested() -> None:
    rows = sample_rows(2)
    rows[1] = dict(rows[0])

    default = parse_dataframe(pd.DataFrame(rows))
    deduped = parse_dataframe(
        pd.DataFrame(rows), IngestConfig(drop_exact_duplicates=True)
    )

    assert len(default.frame) == 2
    assert default.report.counts[RejectReason.DUPLICATE_RECORD] == 0
    assert len(deduped.frame) == 1
    assert deduped.report.counts[RejectReason.DUPLICATE_RECORD] == 1


def test_output_is_sorted_by_timestamp_and_records_stay_aligned() -> None:
    rows = sample_rows(4)
    rows[0]["timestamp"] = TS + timedelta(seconds=5)
    rows[1]["timestamp"] = TS + timedelta(seconds=2)
    rows[2]["timestamp"] = TS + timedelta(seconds=4)
    rows[3]["timestamp"] = TS + timedelta(seconds=1)

    result = parse_dataframe(pd.DataFrame(rows))

    stamps = result.frame["timestamp"].tolist()
    assert stamps == sorted(stamps)
    assert [record.raw_index for record in result.records][0] == 3
    assert result.frame["raw_index"].tolist() == [record.raw_index for record in result.records]


def test_out_of_order_timestamps_are_warned_per_connection() -> None:
    rows = sample_rows(4)
    rows[1]["tcp_connection"] = "conn-2"
    rows[0]["timestamp"] = TS + timedelta(seconds=10)
    rows[1]["timestamp"] = TS + timedelta(seconds=1)
    rows[2]["timestamp"] = TS + timedelta(seconds=2)
    rows[3]["timestamp"] = TS + timedelta(seconds=3)

    result = parse_dataframe(pd.DataFrame(rows))

    assert result.report.warnings[WarningCode.NON_MONOTONIC_TIMESTAMP] == 1
    assert result.report.rows_clean == 4


def test_out_of_order_warning_carries_across_chunks(tmp_path: Path) -> None:
    rows = sample_rows(3)
    rows[0]["timestamp"] = TS + timedelta(seconds=5)
    rows[1]["timestamp"] = TS
    rows[2]["timestamp"] = TS + timedelta(seconds=1)
    path = write_csv(tmp_path / "out_of_order.csv", rows)

    result = parse_csv(path, IngestConfig(chunk_size=1))

    assert result.meta.chunks == 3
    assert result.report.warnings[WarningCode.NON_MONOTONIC_TIMESTAMP] == 1


def test_records_frame_round_trip() -> None:
    result = parse_dataframe(pd.DataFrame(sample_rows(5)))

    rebuilt = records_to_frame(result.records)
    recovered = frame_to_records(rebuilt)

    assert_frame_equal(rebuilt, result.frame)
    assert [record.as_row() for record in recovered] == [
        record.as_row() for record in result.records
    ]


def test_parse_records_accepts_iterables() -> None:
    result = parse_records(iter(sample_rows(2)))

    assert len(result.frame) == 2
    assert result.meta.source == "<records>"


# ---------------------------------------------------------------------------
# CSV ingress
# ---------------------------------------------------------------------------


def write_csv(path: Path, rows: list[dict[str, object]]) -> Path:
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


@pytest.mark.parametrize(
    ("function_code", "quantity", "length"),
    [
        (7, None, 2),
        (15, 2, 11),
        (16, 2, 11),
        (22, None, 8),
        (23, 2, 15),
        (24, None, 4),
        (43, None, 5),
    ],
)
def test_request_length_paths(
    function_code: int, quantity: int | None, length: int
) -> None:
    row = sample_rows(1)[0]
    row.update(
        function_code=function_code,
        quantity=quantity,
        data_length=length,
        direction="request",
    )

    accepted = parse_dataframe(pd.DataFrame([row]))
    assert accepted.report.rows_clean == 1
    assert accepted.report.warnings.get(WarningCode.LENGTH_INCONSISTENT, 0) == 0

    row["data_length"] = length + 1
    mismatched = parse_dataframe(pd.DataFrame([row]))
    assert mismatched.report.warnings[WarningCode.LENGTH_INCONSISTENT] == 1


@pytest.mark.parametrize(
    ("function_code", "quantity", "length"),
    [
        (22, None, 8),
        (23, 2, 7),
        (24, 2, 9),
        (43, None, 32),
    ],
)
def test_response_direction_is_not_checked_as_a_request(
    function_code: int, quantity: int | None, length: int
) -> None:
    row = sample_rows(1)[0]
    row.update(
        function_code=function_code,
        quantity=quantity,
        data_length=length,
        direction="response",
    )

    result = parse_dataframe(pd.DataFrame([row]))

    assert result.report.rows_clean == 1
    assert result.report.warnings.get(WarningCode.LENGTH_INCONSISTENT, 0) == 0


def test_mbap_length_field_accepts_both_bounds() -> None:
    rows = sample_rows(2)
    rows[0].update(
        function_code=7,
        quantity=None,
        register_address=None,
        data_length=2,
        direction="request",
    )
    rows[1].update(
        function_code=43,
        quantity=None,
        register_address=None,
        data_length=254,
        direction="response",
    )

    result = parse_dataframe(pd.DataFrame(rows))

    assert result.report.rows_clean == 2
    assert result.frame["data_length"].tolist() == [2, 254]


def test_custom_allowed_ports_control_scope() -> None:
    rows = sample_rows(2)
    rows[0]["dest_port"] = 1502

    result = parse_dataframe(
        pd.DataFrame(rows), IngestConfig(allowed_ports=frozenset({1502}))
    )

    assert len(result.frame) == 1
    assert result.records[0].dest_port == 1502
    assert result.report.counts[RejectReason.BAD_PORT] == 1


def test_sort_false_preserves_input_order() -> None:
    rows = sample_rows(3)
    rows[0]["timestamp"] = TS + timedelta(seconds=5)
    rows[1]["timestamp"] = TS
    rows[2]["timestamp"] = TS + timedelta(seconds=2)

    result = parse_dataframe(pd.DataFrame(rows), IngestConfig(sort=False))

    assert result.frame["transaction_id"].tolist() == [0, 1, 2]
    assert [record.raw_index for record in result.records] == [0, 1, 2]


def test_epoch_units_resolve_to_the_same_instant() -> None:
    rows = sample_rows(4)
    for row, value in zip(
        rows,
        [1767225600, 1767225600000, 1767225600000000, 1767225600000000000],
    ):
        row["timestamp"] = value

    result = parse_dataframe(pd.DataFrame(rows))

    assert result.report.rows_clean == 4
    assert result.frame["timestamp"].nunique() == 1
    assert result.frame["timestamp"].iloc[0] == pd.Timestamp("2026-01-01T00:00:00Z")


def test_parse_csv_matches_dataframe_path(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "log.csv", sample_rows(5))

    result = parse_csv(path)

    assert len(result.frame) == 5
    assert result.meta.rows_in == 5
    assert result.meta.chunks == 1
    assert result.meta.encoding == "utf-8-sig"


def test_parse_csv_chunks_preserve_global_raw_indices(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "log.csv", sample_rows(7))

    result = parse_csv(path, IngestConfig(chunk_size=3))

    assert result.meta.chunks == 3
    assert result.frame["raw_index"].tolist() == list(range(7))


def test_parse_csv_writes_rejected_rows(tmp_path: Path) -> None:
    rows = sample_rows(4)
    rows[0]["dest_ip"] = "10.0.0.999"
    path = write_csv(tmp_path / "log.csv", rows)
    rejects = tmp_path / "rejects.csv"

    result = parse_csv(path, rejects_out=rejects)

    assert rejects.exists()
    rejected = pd.read_csv(rejects)
    assert len(rejected) == 1
    assert rejected.loc[0, "_reason"] == "bad_ip"
    assert "10.0.0.999" in str(rejected.loc[0, "dest_ip"])
    assert result.report.counts[RejectReason.BAD_IP] == 1


def test_parse_csv_handles_unparseable_lines(tmp_path: Path) -> None:
    path = tmp_path / "broken.csv"
    path.write_text(
        "Timestamp,SourceIP,DestIP,TCPConnection,TransactionID,FunctionCode,"
        "RegisterAddress,DataLength,Label\n"
        "2026-01-01T00:00:00+00:00,10.0.0.1,10.0.0.2,conn-1,1,3,100,6,0\n"
        "2026-01-01T00:00:01+00:00,10.0.0.1,10.0.0.2,conn-1,2,3,101,6,0,extra,fields\n",
        encoding="utf-8",
    )

    result = parse_csv(path)

    assert len(result.frame) == 1
    assert result.report.counts[RejectReason.CSV_PARSE_ERROR] == 1
    assert result.report.rows_seen == 2
    issue = result.report.samples[RejectReason.CSV_PARSE_ERROR][0]
    assert issue.raw_index == 3
    assert "line 3" in issue.detail


def test_bad_csv_line_in_the_middle_reports_its_file_line(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "middle.csv", sample_rows(5))
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[3] = "broken,line"  # header is line 1, so this corrupts line 4
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = parse_csv(path)

    assert result.report.rows_seen == 5
    assert len(result.frame) == 4
    assert result.report.counts[RejectReason.CSV_PARSE_ERROR] == 1
    issue = result.report.samples[RejectReason.CSV_PARSE_ERROR][0]
    assert issue.raw_index == 4
    assert "line 4" in issue.detail


def test_rejects_out_cannot_overwrite_the_input(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "log.csv", sample_rows(2))
    original = path.read_text(encoding="utf-8")

    with pytest.raises(SourceError, match="must not overwrite"):
        parse_csv(path, rejects_out=path)

    assert path.read_text(encoding="utf-8") == original


def test_parse_csv_handles_bom(tmp_path: Path) -> None:
    path = tmp_path / "bom.csv"
    frame = pd.DataFrame(sample_rows(2))
    frame.to_csv(path, index=False, encoding="utf-8-sig")

    result = parse_csv(path)

    assert len(result.frame) == 2


def test_parse_csv_empty_and_header_only(tmp_path: Path) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    header = tmp_path / "header.csv"
    header.write_text(
        "Timestamp,SourceIP,DestIP,TCPConnection,TransactionID,FunctionCode,"
        "RegisterAddress,DataLength,Label\n",
        encoding="utf-8",
    )

    empty_result = parse_csv(empty)
    header_result = parse_csv(header)

    for result in (empty_result, header_result):
        assert result.frame.empty
        assert list(result.frame.columns) == list(CANONICAL_COLUMNS)
        assert result.meta.rows_in == 0


def test_parse_csv_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SourceError, match="does not exist"):
        parse_csv(tmp_path / "nope.csv")


def test_parse_csv_missing_column_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad_schema.csv"
    path.write_text("Timestamp,SourceIP\n2026-01-01T00:00:00Z,10.0.0.1\n", encoding="utf-8")

    with pytest.raises(SchemaError, match="dest_ip"):
        parse_csv(path)
