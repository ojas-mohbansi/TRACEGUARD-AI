"""Tests for the synthetic Modbus/TCP log generator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from modbus_nids import IngestConfig, generate_synthetic_logs, parse_dataframe, write_synthetic_csv
from modbus_nids.models import RejectReason
from modbus_nids.synthetic import DISPLAY_COLUMNS


def test_output_schema_is_the_declared_header_set() -> None:
    frame = generate_synthetic_logs(n_sessions=2, events_per_session=3, seed=1)

    assert list(frame.columns) == list(DISPLAY_COLUMNS.values())
    assert len(frame) == 6


def test_generation_is_deterministic() -> None:
    first = generate_synthetic_logs(n_sessions=4, events_per_session=10, seed=99)
    second = generate_synthetic_logs(n_sessions=4, events_per_session=10, seed=99)

    assert_frame_equal(first, second)


def test_seed_changes_the_data() -> None:
    first = generate_synthetic_logs(n_sessions=3, events_per_session=5, seed=1)
    second = generate_synthetic_logs(n_sessions=3, events_per_session=5, seed=2)

    assert not first.equals(second)


def test_anomaly_labels_are_binary_and_roughly_on_rate() -> None:
    frame = generate_synthetic_logs(
        n_sessions=10,
        events_per_session=30,
        anomaly_rate=0.05,
        seed=7,
    )

    labels = frame["Label"]
    assert set(labels.unique()) <= {0, 1}
    assert 0.03 <= labels.mean() <= 0.08


def test_fully_valid_log_is_retained() -> None:
    frame = generate_synthetic_logs(
        n_sessions=8, events_per_session=25, anomaly_rate=0.05, defect_rate=0.0, seed=11
    )

    result = parse_dataframe(frame)

    assert result.report.rows_rejected == 0
    assert result.meta.rows_in == len(frame)
    assert result.report.rows_clean == len(frame)
    assert int(result.frame["label"].sum()) > 0  # anomalies survive the gate


def test_injected_defects_are_dropped_exactly_once() -> None:
    frame = generate_synthetic_logs(
        n_sessions=5,
        events_per_session=20,
        anomaly_rate=0.0,
        defect_rate=0.1,
        seed=3,
    )
    defects = round(0.1 * 100)

    result = parse_dataframe(frame, IngestConfig())

    assert len(frame) == 100 + defects
    assert result.report.rows_rejected == defects
    assert result.report.rows_clean == 100
    assert result.report.counts[RejectReason.LABEL_NOT_BINARY] >= 1


def test_large_session_counts_keep_ports_and_ips_valid() -> None:
    frame = generate_synthetic_logs(
        n_sessions=4000, events_per_session=1, anomaly_rate=0.0, defect_rate=0.0, seed=5
    )

    ports = frame["SourcePort"]
    assert ports.between(1, 65535).all()

    result = parse_dataframe(frame)
    assert result.report.rows_rejected == 0
    assert result.report.rows_clean == len(frame)
    assert result.frame["source_ip"].str.match(r"^10\.0\.\d{1,3}\.\d{1,3}$").all()


def test_write_synthetic_csv_creates_parents(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "log.csv"

    written = write_synthetic_csv(
        target, n_sessions=2, events_per_session=5, seed=4, defect_rate=0.0
    )

    assert written == target
    assert pd.read_csv(target).shape[0] == 10


@pytest.mark.parametrize(
    "kwargs",
    [
        {"n_sessions": 0},
        {"events_per_session": 0},
        {"anomaly_rate": -0.1},
        {"defect_rate": 1.5},
    ],
)
def test_invalid_arguments_raise(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        generate_synthetic_logs(**kwargs)  # type: ignore[arg-type]
