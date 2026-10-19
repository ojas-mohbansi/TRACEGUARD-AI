"""Tests for session-isolated windows and the Phase 1.2 feature extractor."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from modbus_nids import (
    FEATURE_COLUMNS,
    OUTPUT_COLUMNS,
    FeatureBatch,
    ModbusRecord,
    SessionKey,
    SessionWindowManager,
    WindowError,
    extract_features,
    parse_dataframe,
)
from modbus_nids.parser import records_to_frame
from modbus_nids.window import (
    DEFAULT_EPSILON,
    NGRAM_SIZES,
    TID_MODULUS,
    READ_FUNCTION_CODES,
    WRITE_FUNCTION_CODES,
)

TS = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def make_record(**overrides: object) -> ModbusRecord:
    defaults: dict[str, object] = {
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
        "quantity": 10,
        "direction": "request",
    }
    defaults.update(overrides)
    return ModbusRecord(**defaults)  # type: ignore[arg-type]


def series(count: int, *, seconds: float = 1.0, **overrides: object) -> list[ModbusRecord]:
    """Sequential single-session records, one second apart by default."""
    return [
        make_record(
            timestamp=TS + timedelta(seconds=index * seconds),
            transaction_id=index,
            raw_index=index,
            **overrides,
        )
        for index in range(count)
    ]


def assert_output_schema(frame: pd.DataFrame) -> None:
    assert list(frame.columns) == list(OUTPUT_COLUMNS)


# ---------------------------------------------------------------------------
# Configuration and keying
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"window_size": 0}, "window_size"),
        ({"window_size": -3}, "window_size"),
        ({"epsilon": 0.0}, "epsilon"),
        ({"epsilon": -1e-9}, "epsilon"),
        ({"epsilon": float("nan")}, "epsilon"),
        ({"epsilon": float("inf")}, "epsilon"),
    ],
)
def test_invalid_configuration_is_rejected(kwargs: dict[str, float], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        SessionWindowManager(**kwargs)


def test_session_key_ignores_transaction_id() -> None:
    key = SessionKey.from_record(make_record(transaction_id=7))
    other = SessionKey.from_record(make_record(transaction_id=9999))

    assert key == other
    assert key.label == "10.0.0.1|10.0.0.2|conn-1"
    assert str(key) == key.label
    assert SessionKey.from_record(make_record(dest_ip="10.0.0.3")) != key


def test_manager_rejects_non_records() -> None:
    manager = SessionWindowManager()

    with pytest.raises(TypeError, match="ModbusRecord"):
        manager.add({"timestamp": TS})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Session isolation and window bounding
# ---------------------------------------------------------------------------


def test_interleaved_sessions_do_not_contaminate_each_other() -> None:
    manager = SessionWindowManager(window_size=10)
    events = [
        make_record(timestamp=TS, tcp_connection="A", transaction_id=0),
        make_record(timestamp=TS + timedelta(seconds=5), tcp_connection="B", transaction_id=100),
        make_record(timestamp=TS + timedelta(seconds=1), tcp_connection="A", transaction_id=1),
        make_record(timestamp=TS + timedelta(seconds=9), tcp_connection="B", transaction_id=101),
    ]
    rows = [manager.add(event) for event in events]

    assert [row["session_id"] for row in rows] == [
        "10.0.0.1|10.0.0.2|A",
        "10.0.0.1|10.0.0.2|B",
        "10.0.0.1|10.0.0.2|A",
        "10.0.0.1|10.0.0.2|B",
    ]
    assert [row["dt_seconds"] for row in rows] == [0.0, 0.0, 1.0, 4.0]
    assert [row["tid_delta"] for row in rows] == [0, 0, 1, 1]
    assert [row["window_event_count"] for row in rows] == [1, 1, 2, 2]
    assert [row["is_session_start"] for row in rows] == [1, 1, 0, 0]
    assert manager.session_count == 2


def test_window_is_bounded_per_session() -> None:
    manager = SessionWindowManager(window_size=3)
    rows = [manager.add(event) for event in series(7)]

    assert [row["window_event_count"] for row in rows] == [1, 2, 3, 3, 3, 3, 3]
    assert [row["window_fill_ratio"] for row in rows] == pytest.approx(
        [1 / 3, 2 / 3, 1.0, 1.0, 1.0, 1.0, 1.0]
    )
    key = SessionKey.from_record(make_record())
    assert len(manager.window_for(key)) == 3
    stranger = SessionKey.from_record(make_record(tcp_connection="nope"))
    assert manager.window_for(stranger) == ()


def test_window_counts_only_retained_events() -> None:
    manager = SessionWindowManager(window_size=2)
    events = [
        make_record(timestamp=TS + timedelta(seconds=index), function_code=code)
        for index, code in enumerate([6, 6, 3])
    ]
    rows = [manager.add(event) for event in events]

    assert rows[0]["write_count"] == 1
    assert rows[2]["write_count"] == 1  # the first write aged out
    assert rows[2]["read_count"] == 1
    assert rows[2]["write_read_ratio"] == pytest.approx(1.0)
    assert rows[2]["write_fraction"] == pytest.approx(0.5)


def test_timestamp_regression_raises_and_preserves_state() -> None:
    manager = SessionWindowManager()
    first = make_record(timestamp=TS, transaction_id=0)
    manager.add(first)

    with pytest.raises(WindowError, match="timestamp regressed"):
        manager.add(make_record(timestamp=TS - timedelta(milliseconds=1), transaction_id=1))

    assert manager.window_for(SessionKey.from_record(first)) == (first,)


def test_earlier_timestamp_is_fine_in_a_different_session() -> None:
    manager = SessionWindowManager()
    manager.add(make_record(timestamp=TS, tcp_connection="A"))
    row = manager.add(make_record(timestamp=TS - timedelta(seconds=30), tcp_connection="B"))

    assert row["is_session_start"] == 1
    assert row["dt_seconds"] == 0.0


def test_transform_resets_between_batches() -> None:
    manager = SessionWindowManager(window_size=2)
    manager.add(make_record())
    frame = manager.transform(series(2))

    assert list(frame["is_session_start"]) == [1, 0]
    assert list(frame["window_event_count"]) == [1, 2]
    assert manager.session_count == 1


def test_reset_clears_windows() -> None:
    manager = SessionWindowManager()
    manager.add(make_record())
    manager.reset()

    assert manager.session_count == 0
    assert manager.active_sessions == ()


# ---------------------------------------------------------------------------
# Temporal features
# ---------------------------------------------------------------------------


def test_log_delta_is_stable_for_zero_and_sub_epsilon_gaps() -> None:
    manager = SessionWindowManager(epsilon=DEFAULT_EPSILON)
    rows = [
        manager.add(make_record(timestamp=TS)),
        manager.add(make_record(timestamp=TS)),
        manager.add(make_record(timestamp=TS + timedelta(microseconds=1))),
        manager.add(make_record(timestamp=TS + timedelta(seconds=1))),
    ]

    assert [row["dt_seconds"] for row in rows] == pytest.approx([0.0, 0.0, 1e-6, 0.999999])
    assert [row["log_dt"] for row in rows] == pytest.approx(
        [
            math.log(DEFAULT_EPSILON),
            math.log(DEFAULT_EPSILON),
            math.log(2 * DEFAULT_EPSILON),
            math.log(0.999999 + DEFAULT_EPSILON),
        ]
    )
    assert all(math.isfinite(row["log_dt"]) for row in rows)


def test_custom_epsilon_scales_the_log_delta() -> None:
    manager = SessionWindowManager(epsilon=0.5)
    manager.add(make_record(timestamp=TS))
    row = manager.add(make_record(timestamp=TS + timedelta(seconds=0.5)))

    assert row["log_dt"] == pytest.approx(math.log(1.0))


@pytest.mark.parametrize(
    ("previous_tid", "current_tid", "expected"),
    [(0, 1, 1), (65535, 0, 1), (65535, 5, 6), (1, 1, 0), (0, 65535, 65535), (65534, 2, 4)],
)
def test_tid_delta_wraps_modulo_65536(previous_tid: int, current_tid: int, expected: int) -> None:
    manager = SessionWindowManager()
    manager.add(make_record(timestamp=TS, transaction_id=previous_tid))
    row = manager.add(make_record(timestamp=TS + timedelta(seconds=1), transaction_id=current_tid))

    assert row["tid_delta"] == expected
    assert 0 <= row["tid_delta"] < TID_MODULUS


# ---------------------------------------------------------------------------
# Command mix and n-grams
# ---------------------------------------------------------------------------


def test_write_and_read_ratio_over_the_window() -> None:
    manager = SessionWindowManager(window_size=5)
    events = [
        make_record(timestamp=TS + timedelta(seconds=index), function_code=code)
        for index, code in enumerate([3, 4, 6, 16, 1])
    ]
    rows = [manager.add(event) for event in events]

    last = rows[-1]
    assert (last["write_count"], last["read_count"], last["other_count"]) == (2, 3, 0)
    assert last["write_read_ratio"] == pytest.approx(2 / 3)
    assert last["write_fraction"] == pytest.approx(2 / 5)


def test_all_declared_function_code_classes_are_counted() -> None:
    manager = SessionWindowManager(window_size=20)
    codes = sorted(WRITE_FUNCTION_CODES | READ_FUNCTION_CODES)
    row: dict[str, object] = {}
    for index, code in enumerate(codes):
        row = manager.add(
            make_record(timestamp=TS + timedelta(seconds=index), function_code=code)
        )

    assert row["write_count"] == len(WRITE_FUNCTION_CODES)
    assert row["read_count"] == len(READ_FUNCTION_CODES)
    assert row["other_count"] == 0


def test_exception_responses_use_the_base_function_code() -> None:
    manager = SessionWindowManager(window_size=3)
    manager.add(make_record(timestamp=TS, function_code=0x83))
    manager.add(make_record(timestamp=TS + timedelta(seconds=1), function_code=0x90))
    row = manager.add(make_record(timestamp=TS + timedelta(seconds=2), function_code=0x45))

    assert (row["read_count"], row["write_count"], row["other_count"]) == (1, 1, 1)


def test_unknown_function_code_counts_as_other() -> None:
    manager = SessionWindowManager()
    row = manager.add(make_record(function_code=9))

    assert (row["write_count"], row["read_count"], row["other_count"]) == (0, 0, 1)
    assert row["write_read_ratio"] == 0.0
    assert row["write_fraction"] == 0.0


def test_no_reads_yields_finite_ratio() -> None:
    manager = SessionWindowManager()
    row = manager.add(make_record(function_code=6))

    assert row["write_read_ratio"] == 1.0
    assert np.isfinite(row["write_read_ratio"])


def test_ngram_counts_and_novelty() -> None:
    manager = SessionWindowManager(window_size=5)
    codes = [3, 3, 3, 16]
    rows = [
        manager.add(make_record(timestamp=TS + timedelta(seconds=index), function_code=code))
        for index, code in enumerate(codes)
    ]

    assert rows[0]["ngram_unique_2"] == 0  # window shorter than n
    assert rows[0]["ngram_novelty_2"] == 0.0
    assert rows[1]["ngram_unique_2"] == 1  # (3, 3)
    assert rows[2]["ngram_unique_2"] == 1  # repeated bigram, not novel
    assert rows[2]["ngram_novelty_2"] == 0.0
    assert rows[3]["ngram_unique_2"] == 2  # {(3, 3), (3, 16)}
    assert rows[3]["ngram_novelty_2"] == 1.0
    assert rows[3]["ngram_unique_3"] == 2  # {(3, 3, 3), (3, 3, 16)}
    assert rows[3]["ngram_unique_5"] == 0  # still too short


def test_full_window_ngram_novelty_flags_repeats() -> None:
    manager = SessionWindowManager(window_size=4)
    codes = [1, 2, 1, 2]
    rows = [
        manager.add(make_record(timestamp=TS + timedelta(seconds=index), function_code=code))
        for index, code in enumerate(codes)
    ]

    assert rows[3]["ngram_unique_2"] == 2
    assert rows[3]["ngram_novelty_2"] == 0.0
    assert rows[3]["ngram_novelty_3"] == 1.0


def test_ngram_sizes_are_exposed() -> None:
    assert NGRAM_SIZES == (2, 3, 5)
    for n in NGRAM_SIZES:
        assert f"ngram_unique_{n}" in FEATURE_COLUMNS
        assert f"ngram_novelty_{n}" in FEATURE_COLUMNS


# ---------------------------------------------------------------------------
# Frame contract and alignment
# ---------------------------------------------------------------------------


def test_transform_frame_has_pinned_schema_and_dtypes() -> None:
    frame = SessionWindowManager().transform(series(4))

    assert_output_schema(frame)
    assert frame["timestamp"].dtype == pd.DatetimeTZDtype(tz="UTC")
    for column in FEATURE_COLUMNS:
        assert frame[column].dtype == np.float64, column
    for column in ("label", "raw_index", "transaction_id", "function_code"):
        assert frame[column].dtype == np.int64, column


def test_feature_rows_stay_aligned_with_labels_and_raw_index() -> None:
    records = series(6)
    records[3] = make_record(
        timestamp=records[3].timestamp,
        transaction_id=records[3].transaction_id,
        label=1,
        raw_index=99,
    )
    frame = SessionWindowManager().transform(records)

    assert list(frame["label"]) == [0, 0, 0, 1, 0, 0]
    assert list(frame["raw_index"]) == [0, 1, 2, 99, 4, 5]


def test_empty_transform_returns_empty_typed_frame() -> None:
    frame = SessionWindowManager().transform([])

    assert_output_schema(frame)
    assert frame.empty
    assert frame["timestamp"].dtype == pd.DatetimeTZDtype(tz="UTC")
    for column in FEATURE_COLUMNS:
        assert frame[column].dtype == np.float64, column
    for column in ("label", "raw_index"):
        assert frame[column].dtype == np.int64, column


def test_feature_columns_are_complete_for_every_row() -> None:
    frame = SessionWindowManager().transform(series(2))

    assert not frame[list(FEATURE_COLUMNS)].isna().to_numpy().any()


# ---------------------------------------------------------------------------
# Batch extraction API
# ---------------------------------------------------------------------------


def test_extract_features_accepts_records() -> None:
    batch = extract_features(series(5))

    assert isinstance(batch, FeatureBatch)
    assert len(batch) == 5
    assert batch.X.shape == (5, len(FEATURE_COLUMNS))
    assert batch.X.dtype == np.float64
    assert batch.y.dtype == np.int64
    assert list(batch.raw_index) == [0, 1, 2, 3, 4]
    assert set(batch.session_ids) == {"10.0.0.1|10.0.0.2|conn-1"}
    assert list(batch.features.columns) == list(FEATURE_COLUMNS)


def test_extract_features_accepts_dataframe_and_result() -> None:
    result = parse_dataframe(records_to_frame(series(3)))

    from_frame = extract_features(result.frame)
    from_result = extract_features(result)

    assert_frame_equal(from_frame.frame, from_result.frame)
    assert len(from_result) == len(result.records)
    assert list(from_result.raw_index) == [record.raw_index for record in result.records]


def test_extract_features_honours_configuration() -> None:
    batch = extract_features(series(5), window_size=2, epsilon=0.25)

    assert batch.frame["window_event_count"].max() == 2
    assert batch.frame.loc[1, "log_dt"] == pytest.approx(math.log(1.25))


def test_extract_features_rejects_bad_items() -> None:
    with pytest.raises(TypeError, match="ModbusRecord"):
        extract_features([make_record(), "not-a-record"])  # type: ignore[list-item]


def test_extract_features_empty_input() -> None:
    batch = extract_features([])

    assert len(batch) == 0
    assert batch.X.shape == (0, len(FEATURE_COLUMNS))
    assert batch.y.shape == (0,)
    assert batch.raw_index.shape == (0,)


def test_feature_batch_validates_required_columns() -> None:
    with pytest.raises(ValueError, match="missing column"):
        FeatureBatch(frame=pd.DataFrame({"label": [0]}))


def test_dest_ip_is_part_of_the_session_identity() -> None:
    records = [
        make_record(timestamp=TS, dest_ip="10.0.0.2", tcp_connection="c1"),
        make_record(timestamp=TS, dest_ip="10.0.0.3", tcp_connection="c1"),
        make_record(timestamp=TS + timedelta(seconds=2), dest_ip="10.0.0.2", tcp_connection="c1"),
    ]
    frame = SessionWindowManager().transform(records)

    assert frame["session_id"].nunique() == 2
    assert list(frame["window_event_count"]) == [1, 1, 2]
    assert list(frame["dt_seconds"]) == [0.0, 0.0, 2.0]
