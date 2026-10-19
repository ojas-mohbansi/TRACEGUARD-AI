"""Deterministic synthetic Modbus/TCP traffic for testing the pipeline.

The generator models a small plant: several clients poll one of a few PLCs over
persistent TCP connections, with realistic transaction-ID progression, poll
periods, coil/register reads, and the occasional write. Behavioural anomalies
(write floods, register sweeps, TID reuse, exception responses, off-hours
bursts) are injected and labelled ``1``.

Separately, ``defect_rate`` injects structurally malformed rows (bad timestamp,
address, port, length, ...) that are *not* labelled anomalous: they exist to
exercise the ingestion gate, which must drop them and account for them.

All randomness flows from ``numpy.random.default_rng(seed)``, so a given set of
arguments always yields identical bytes.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .constants import expected_request_length

DISPLAY_COLUMNS: dict[str, str] = {
    "timestamp": "Timestamp",
    "source_ip": "SourceIP",
    "dest_ip": "DestIP",
    "tcp_connection": "TCPConnection",
    "transaction_id": "TransactionID",
    "function_code": "FunctionCode",
    "register_address": "RegisterAddress",
    "data_length": "DataLength",
    "label": "Label",
    "source_port": "SourcePort",
    "dest_port": "DestPort",
    "protocol_id": "ProtocolID",
    "unit_id": "UnitID",
    "quantity": "Quantity",
    "direction": "Direction",
}
"""Canonical -> header spelling used in generated CSV logs."""

_DEFAULT_START = datetime(2026, 1, 1, 6, 0, 0, tzinfo=timezone.utc)
_POLL_PERIODS = (0.2, 0.5, 1.0, 2.0)

# Ephemeral source ports stay inside the IANA dynamic range. The offset is
# wrapped because a linear assignment overflows 65535 after ~3600 sessions.
_SOURCE_PORT_BASE = 40_000
_SOURCE_PORT_SPAN = 20_000


def _event(
    timestamp: datetime,
    *,
    source_ip: str,
    dest_ip: str,
    connection: str,
    transaction_id: int,
    function_code: int,
    register_address: int,
    label: int = 0,
    source_port: int = 51234,
    unit_id: int = 1,
    quantity: int | None = None,
    direction: str = "request",
) -> dict[str, Any]:
    """One canonical event dict with a protocol-consistent MBAP length."""
    if direction == "response" and function_code >= 0x80:
        data_length = 3
    else:
        data_length = expected_request_length(function_code, quantity) or 6
    return {
        "timestamp": timestamp,
        "source_ip": source_ip,
        "dest_ip": dest_ip,
        "tcp_connection": connection,
        "transaction_id": transaction_id,
        "function_code": function_code,
        "register_address": register_address,
        "data_length": data_length,
        "label": label,
        "source_port": source_port,
        "dest_port": 502,
        "protocol_id": 0,
        "unit_id": unit_id,
        "quantity": quantity,
        "direction": direction,
    }


def _benign_events(
    rng: np.random.Generator,
    *,
    n_sessions: int,
    events_per_session: int,
    start: datetime,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build per-session polling behaviour plus the session profiles."""
    events: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []

    for session in range(n_sessions):
        client_ip = f"10.0.{(session // 250) % 250}.{session % 250 + 1}"
        server_ip = f"192.168.10.{10 + (session % 6)}"
        connection = f"conn-{1000 + session}"
        source_port = _SOURCE_PORT_BASE + (session * 7) % _SOURCE_PORT_SPAN
        unit_id = 1 + (session % 4)
        base_register = int(rng.integers(100, 6000))
        span = int(rng.integers(20, 200))
        period = float(_POLL_PERIODS[int(rng.integers(0, len(_POLL_PERIODS)))])
        tid = int(rng.integers(0, 60000))

        profiles.append(
            {
                "connection": connection,
                "source_ip": client_ip,
                "dest_ip": server_ip,
                "source_port": source_port,
                "unit_id": unit_id,
                "base_register": base_register,
                "span": span,
                "period": period,
            }
        )

        for step in range(events_per_session):
            tid = (tid + 1) & 0xFFFF
            timestamp = start + timedelta(
                seconds=step * period + float(rng.uniform(0.0, 0.05))
            )
            roll = float(rng.random())
            if roll < 0.70:
                quantity = int(rng.integers(1, min(span, 100) + 1))
                function_code = 3
                register = base_register + int(rng.integers(0, span - quantity + 1))
            elif roll < 0.80:
                quantity = int(rng.integers(1, min(span, 64) + 1))
                function_code = 1
                register = base_register
            elif roll < 0.88:
                quantity = int(rng.integers(1, min(span, 100) + 1))
                function_code = 4
                register = base_register + int(rng.integers(0, span - quantity + 1))
            elif roll < 0.96:
                quantity = None
                function_code = 6
                register = base_register + int(rng.integers(0, span))
            else:
                quantity = int(rng.integers(1, 7))
                function_code = 16
                register = base_register + int(rng.integers(0, max(span - quantity, 1)))

            events.append(
                _event(
                    timestamp,
                    source_ip=client_ip,
                    dest_ip=server_ip,
                    connection=connection,
                    transaction_id=tid,
                    function_code=function_code,
                    register_address=register,
                    source_port=source_port,
                    unit_id=unit_id,
                    quantity=quantity,
                )
            )

    return events, profiles


def _mutate_anomaly(
    events: list[dict[str, Any]],
    profiles: list[dict[str, Any]],
    rng: np.random.Generator,
    *,
    session: int,
    base: int,
    run: int,
    kind: str,
    events_per_session: int,
) -> None:
    """Rewrite a contiguous run of one session's events as an anomaly."""
    profile = profiles[session]
    anchor = events[base]["timestamp"]

    if kind == "write_flood":
        for offset in range(run):
            quantity = int(rng.integers(1, 5))
            events[base + offset].update(
                function_code=16,
                register_address=40100 + int(rng.integers(0, 40)),
                quantity=quantity,
                data_length=expected_request_length(16, quantity) or 15,
                label=1,
                direction="request",
                timestamp=anchor + timedelta(milliseconds=15 * offset),
            )
    elif kind == "register_sweep":
        sweep_start = int(rng.integers(0, 60000))
        for offset in range(run):
            events[base + offset].update(
                function_code=3,
                register_address=(sweep_start + offset * 1) & 0xFFFF,
                quantity=1,
                data_length=6,
                label=1,
                direction="request",
                timestamp=anchor + timedelta(milliseconds=80 * offset),
            )
    elif kind == "exception_response":
        events[base].update(
            function_code=0x83,
            data_length=3,
            label=1,
            direction="response",
            timestamp=anchor + timedelta(milliseconds=40),
        )
    elif kind == "tid_reuse":
        shared_tid = int(events[max(base - 1, 0)]["transaction_id"])
        for offset in range(run):
            events[base + offset].update(
                transaction_id=shared_tid,
                label=1,
            )
    elif kind == "off_hours_burst":
        night = anchor.replace(hour=2, minute=13, second=0, microsecond=0)
        for offset in range(run):
            events[base + offset].update(
                function_code=3,
                register_address=profile["base_register"] + offset,
                quantity=1,
                data_length=6,
                label=1,
                direction="request",
                timestamp=night + timedelta(seconds=offset),
            )
    else:  # pragma: no cover - guarded by the caller
        raise ValueError(f"unknown anomaly kind: {kind}")


_ANOMALY_KINDS = ("write_flood", "register_sweep", "exception_response", "tid_reuse", "off_hours_burst")
_ANOMALY_WEIGHTS = (0.30, 0.25, 0.15, 0.15, 0.15)
_ANOMALY_RUNS = {"write_flood": (5, 9), "register_sweep": (6, 10), "exception_response": (1, 1), "tid_reuse": (2, 3), "off_hours_burst": (4, 6)}


def _inject_anomalies(
    events: list[dict[str, Any]],
    profiles: list[dict[str, Any]],
    rng: np.random.Generator,
    *,
    target: int,
    events_per_session: int,
) -> int:
    if target <= 0:
        return 0
    injected = 0
    attempts = 0
    kinds = np.array(_ANOMALY_KINDS, dtype=object)
    while injected < target and attempts < target * 50:
        attempts += 1
        kind = str(rng.choice(kinds, p=_ANOMALY_WEIGHTS))
        session = int(rng.integers(0, len(profiles)))
        low, high = _ANOMALY_RUNS[kind]
        run = min(int(rng.integers(low, high + 1)), events_per_session)
        step = int(rng.integers(0, events_per_session - run + 1))
        base = session * events_per_session + step
        if any(events[base + offset]["label"] for offset in range(run)):
            continue
        _mutate_anomaly(
            events,
            profiles,
            rng,
            session=session,
            base=base,
            run=run,
            kind=kind,
            events_per_session=events_per_session,
        )
        injected += run
    return injected


def _inject_defects(
    events: list[dict[str, Any]], rng: np.random.Generator, *, count: int
) -> int:
    """Append malformed rows that the validation gate must reject."""
    if count <= 0:
        return 0
    defects: list[dict[str, Any]] = []
    for index in range(count):
        template = dict(events[int(rng.integers(0, len(events)))])
        template["label"] = 0
        kind = index % 7
        if kind == 0:
            template["timestamp"] = ""
        elif kind == 1:
            template["source_ip"] = "10.0.0.999"
        elif kind == 2:
            template["label"] = 7
        elif kind == 3:
            template["transaction_id"] = 70000
        elif kind == 4:
            template["data_length"] = 300
        elif kind == 5:
            template["dest_port"] = 5020
            template["source_port"] = 40000
        else:
            template["function_code"] = 0
        defects.append(template)
    events.extend(defects)
    return len(defects)


def generate_synthetic_logs(
    n_sessions: int = 40,
    events_per_session: int = 60,
    anomaly_rate: float = 0.03,
    defect_rate: float = 0.0,
    seed: int = 42,
    start: datetime | None = None,
) -> pd.DataFrame:
    """Generate a CSV-shaped frame of Modbus/TCP events.

    Args:
        n_sessions: number of distinct TCP connections / clients.
        events_per_session: polling events produced per connection.
        anomaly_rate: fraction of rows rewritten into labelled anomalies.
        defect_rate: fraction of extra malformed (unlabelled) rows to append.
        seed: RNG seed; identical arguments produce identical output.
        start: session start time (naive values are treated as UTC).

    Returns:
        A frame with the mandatory schema columns plus optional enrichment
        columns, ready to write to CSV and feed through :func:`parse_csv`.
    """
    if n_sessions < 1:
        raise ValueError("n_sessions must be >= 1")
    if events_per_session < 1:
        raise ValueError("events_per_session must be >= 1")
    if not 0.0 <= anomaly_rate <= 1.0:
        raise ValueError("anomaly_rate must be between 0 and 1")
    if not 0.0 <= defect_rate <= 1.0:
        raise ValueError("defect_rate must be between 0 and 1")

    rng = np.random.default_rng(seed)
    if start is None:
        start_dt = _DEFAULT_START
    elif start.tzinfo is None or start.utcoffset() is None:
        start_dt = start.replace(tzinfo=timezone.utc)
    else:
        start_dt = start.astimezone(timezone.utc)

    events, profiles = _benign_events(
        rng, n_sessions=n_sessions, events_per_session=events_per_session, start=start_dt
    )
    total = len(events)
    target = int(round(anomaly_rate * total))
    _inject_anomalies(
        events, profiles, rng, target=target, events_per_session=events_per_session
    )
    _inject_defects(events, rng, count=int(round(defect_rate * total)))

    events.sort(
        key=lambda event: event["timestamp"]
        if isinstance(event["timestamp"], datetime)
        else _DEFAULT_START
    )
    frame = pd.DataFrame.from_records(events)
    for canonical in DISPLAY_COLUMNS:
        if canonical not in frame.columns:
            frame[canonical] = None
    return frame[list(DISPLAY_COLUMNS)].rename(columns=DISPLAY_COLUMNS)


def write_synthetic_csv(path: str | Path, **kwargs: Any) -> Path:
    """Generate a log and write it to ``path`` (creating parents)."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_synthetic_logs(**kwargs)
    frame.to_csv(output, index=False, date_format="%Y-%m-%dT%H:%M:%S.%f%z")
    return output


if __name__ == "__main__":  # pragma: no cover - manual smoke entry point
    sample = generate_synthetic_logs(n_sessions=3, events_per_session=5, seed=7)
    print(sample.head(10).to_string(index=False))
