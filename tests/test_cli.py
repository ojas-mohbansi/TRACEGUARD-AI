"""End-to-end CLI tests through the same entry point a user invokes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from modbus_nids import FEATURE_COLUMNS

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "modbus_nids.cli", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_demo_runs_clean() -> None:
    completed = run_cli("demo", "--sessions", "3", "--events", "10", "--seed", "5")

    assert completed.returncode == 0, completed.stderr
    assert "rows seen=" in completed.stdout


def test_generate_then_parse_round_trip(tmp_path: Path) -> None:
    log = tmp_path / "synthetic.csv"
    clean = tmp_path / "clean.csv"
    rejects = tmp_path / "rejects.csv"
    report = tmp_path / "report.json"

    generated = run_cli(
        "generate",
        "--out",
        str(log),
        "--sessions",
        "4",
        "--events",
        "15",
        "--defect-rate",
        "0.1",
        "--seed",
        "13",
    )
    assert generated.returncode == 0, generated.stderr
    assert log.exists()

    parsed = run_cli(
        "parse",
        "--in",
        str(log),
        "--out",
        str(clean),
        "--rejects",
        str(rejects),
        "--report",
        str(report),
    )
    assert parsed.returncode == 0, parsed.stderr
    assert clean.exists() and rejects.exists() and report.exists()

    payload = json.loads(report.read_text(encoding="utf-8"))
    meta = payload["meta"]
    assert meta["rows_in"] == meta["rows_clean"] + meta["rows_rejected"]
    assert meta["rows_rejected"] > 0
    assert meta["rows_in"] == payload["report"]["rows_seen"]
    assert len(clean.read_text(encoding="utf-8").strip().splitlines()) == (
        meta["rows_clean"] + 1
    )


def test_features_command_writes_an_aligned_matrix(tmp_path: Path) -> None:
    log = tmp_path / "synthetic.csv"
    clean = tmp_path / "clean.csv"
    features = tmp_path / "features.csv"

    assert run_cli(
        "generate", "--out", str(log), "--sessions", "3", "--events", "12", "--seed", "21"
    ).returncode == 0
    assert run_cli("parse", "--in", str(log), "--out", str(clean)).returncode == 0

    completed = run_cli(
        "features", "--in", str(log), "--out", str(features), "--window-size", "4"
    )
    assert completed.returncode == 0, completed.stderr
    assert "features: rows=" in completed.stdout

    frame = pd.read_csv(features)
    parsed = pd.read_csv(clean)
    assert len(frame) == len(parsed)
    for column in FEATURE_COLUMNS:
        assert column in frame.columns, column
        assert not frame[column].isna().any(), column
    assert frame["window_event_count"].max() == 4
    assert frame["session_id"].nunique() == parsed["flow_key"].nunique()
    assert list(frame["raw_index"]) == list(parsed["raw_index"])
    assert list(frame["label"]) == list(parsed["label"])
    for column in ("transaction_id", "function_code", "register_address", "quantity", "unit_id"):
        assert column in frame.columns, column
        assert frame[column].astype("Float64").equals(parsed[column].astype("Float64")), column
    assert list(frame["direction"]) == list(parsed["direction"])


def test_missing_input_is_a_fatal_error(tmp_path: Path) -> None:
    completed = run_cli("parse", "--in", str(tmp_path / "absent.csv"))

    assert completed.returncode == 2
    assert "does not exist" in completed.stderr


def test_no_arguments_runs_demo() -> None:
    completed = run_cli()

    assert completed.returncode == 0, completed.stderr
    assert "source=<demo>" in completed.stdout
