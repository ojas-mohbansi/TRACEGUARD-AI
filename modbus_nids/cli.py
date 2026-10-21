"""Command-line interface for Phase 1.1 ingestion, Phase 1.3 features and Phase 2.1 Tier-1 FSM.

Commands:
    generate   write a synthetic Modbus/TCP CSV log
    parse      validate a CSV log into a clean frame and rejection report
    features   compute session-isolated window features from a log
    fsm        run the Tier-1 protocol state machine over a log
    demo       generate + parse + featurise + evaluate in memory and print a digest

Exit codes: 0 success, 1 nothing survived validation, 2 fatal input error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .constants import DEFAULT_ALLOWED_PORTS
from .features import extract_features
from .fsm import DEFAULT_MAX_OUTSTANDING, DEFAULT_TID_HISTORY, FSMConfig, ModbusFSM
from .models import IngestConfig, IngestionError
from .parser import parse_csv, parse_dataframe
from .synthetic import generate_synthetic_logs, write_synthetic_csv
from .window import DEFAULT_EPSILON, DEFAULT_WINDOW_SIZE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="modbus-nids",
        description=(
            "Modbus/TCP pipeline: synthetic logs, strict parsing, rejection "
            "reports, session-isolated features, Tier-1 protocol FSM."
        ),
    )
    sub = parser.add_subparsers(dest="command")

    generate = sub.add_parser("generate", help="write a synthetic CSV log")
    generate.add_argument("--out", required=True, type=Path, help="destination CSV path")
    generate.add_argument("--sessions", type=int, default=40, help="number of TCP sessions")
    generate.add_argument(
        "--events", type=int, default=60, help="events generated per session"
    )
    generate.add_argument(
        "--anomaly-rate", type=float, default=0.03, help="fraction of rows labelled anomalous"
    )
    generate.add_argument(
        "--defect-rate", type=float, default=0.02, help="fraction of malformed rows to inject"
    )
    generate.add_argument("--seed", type=int, default=42, help="RNG seed")
    generate.set_defaults(handler=_cmd_generate)

    parse = sub.add_parser("parse", help="validate a CSV log")
    parse.add_argument("--in", dest="input", required=True, type=Path, help="input CSV path")
    parse.add_argument("--out", type=Path, help="write the clean frame to this CSV")
    parse.add_argument("--report", type=Path, help="write the rejection report as JSON")
    parse.add_argument("--rejects", type=Path, help="write rejected raw rows with reasons")
    parse.add_argument(
        "--lenient",
        action="store_true",
        help="skip port/protocol-id scope checks (structural rules still apply)",
    )
    parse.add_argument(
        "--chunk-size", type=int, default=200_000, help="rows per streaming chunk"
    )
    parse.add_argument(
        "--allowed-port",
        dest="allowed_ports",
        type=int,
        action="append",
        help="allowed Modbus port (repeatable; defaults to 502)",
    )
    parse.set_defaults(handler=_cmd_parse)

    features = sub.add_parser("features", help="compute session-isolated window features")
    features.add_argument(
        "--in", dest="input", required=True, type=Path, help="input CSV path"
    )
    features.add_argument(
        "--out", type=Path, help="write the per-event feature matrix to this CSV"
    )
    features.add_argument(
        "--window-size",
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        help="trailing events retained per TCP session",
    )
    features.add_argument(
        "--epsilon",
        type=float,
        default=DEFAULT_EPSILON,
        help="seconds added inside log(dt + epsilon)",
    )
    features.add_argument(
        "--lenient",
        action="store_true",
        help="skip port/protocol-id scope checks (structural rules still apply)",
    )
    features.add_argument(
        "--chunk-size", type=int, default=200_000, help="rows per streaming chunk"
    )
    features.add_argument(
        "--allowed-port",
        dest="allowed_ports",
        type=int,
        action="append",
        help="allowed Modbus port (repeatable; defaults to 502)",
    )
    features.set_defaults(handler=_cmd_features)

    fsm = sub.add_parser("fsm", help="run the Tier-1 protocol state machine over a log")
    fsm.add_argument(
        "--in", dest="input", required=True, type=Path, help="input CSV path"
    )
    fsm.add_argument(
        "--out", type=Path, help="write the per-event Tier-1 verdicts to this CSV"
    )
    fsm.add_argument(
        "--report", type=Path, help="write the Tier-1 summary as JSON"
    )
    fsm.add_argument(
        "--max-outstanding",
        type=int,
        default=DEFAULT_MAX_OUTSTANDING,
        help="open transactions kept per conversation",
    )
    fsm.add_argument(
        "--tid-history",
        type=int,
        default=DEFAULT_TID_HISTORY,
        help="recently closed transaction ids remembered per conversation",
    )
    fsm.add_argument(
        "--lenient",
        action="store_true",
        help="skip port/protocol-id scope checks (structural rules still apply)",
    )
    fsm.add_argument(
        "--allowed-port",
        dest="allowed_ports",
        type=int,
        action="append",
        help="allowed Modbus port (repeatable; defaults to 502)",
    )
    fsm.set_defaults(handler=_cmd_fsm)

    demo = sub.add_parser(
        "demo", help="generate, parse, featurise and evaluate in memory"
    )
    demo.add_argument("--sessions", type=int, default=8)
    demo.add_argument("--events", type=int, default=25)
    demo.add_argument("--anomaly-rate", type=float, default=0.05)
    demo.add_argument("--defect-rate", type=float, default=0.02)
    demo.add_argument("--seed", type=int, default=42)
    demo.set_defaults(handler=_cmd_demo)

    return parser


def _allowed_ports(args: argparse.Namespace) -> frozenset[int]:
    ports = getattr(args, "allowed_ports", None)
    return frozenset(ports) if ports else DEFAULT_ALLOWED_PORTS


def _config_from(args: argparse.Namespace) -> IngestConfig:
    return IngestConfig(
        strict=not getattr(args, "lenient", False),
        allowed_ports=_allowed_ports(args),
        chunk_size=getattr(args, "chunk_size", 200_000),
    )


def _write_clean(frame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def _cmd_generate(args: argparse.Namespace) -> int:
    path = write_synthetic_csv(
        args.out,
        n_sessions=args.sessions,
        events_per_session=args.events,
        anomaly_rate=args.anomaly_rate,
        defect_rate=args.defect_rate,
        seed=args.seed,
    )
    print(f"wrote {path}")
    return 0


def _cmd_parse(args: argparse.Namespace) -> int:
    config = _config_from(args)
    result = parse_csv(args.input, config, rejects_out=args.rejects)
    if args.out is not None:
        _write_clean(result.frame, args.out)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {"meta": result.meta.to_dict(), "report": result.report.to_dict()},
            indent=2,
            sort_keys=True,
        )
        args.report.write_text(payload, encoding="utf-8")
    print(result.summary())
    return 0 if result.rows_clean else 1


def _cmd_features(args: argparse.Namespace) -> int:
    result = parse_csv(args.input, _config_from(args))
    batch = extract_features(
        result, window_size=args.window_size, epsilon=args.epsilon
    )
    if args.out is not None:
        _write_clean(batch.frame, args.out)
    print(result.summary())
    print(
        f"features: rows={len(batch)} sessions={batch.n_sessions} "
        f"columns={len(batch.feature_names)} window={args.window_size} "
        f"anomalies={int(batch.y.sum())}"
    )
    return 0 if len(batch) else 1


def _cmd_fsm(args: argparse.Namespace) -> int:
    result = parse_csv(args.input, _config_from(args))
    engine = ModbusFSM(
        FSMConfig(
            allowed_ports=_allowed_ports(args),
            max_outstanding=args.max_outstanding,
            tid_history=args.tid_history,
        )
    )
    tier1 = engine.evaluate(result)
    if args.out is not None:
        _write_clean(tier1.to_frame(), args.out)
    summary = engine.finish()
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(summary.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
        )
    print(result.summary())
    print(summary.summary())
    return 0 if len(tier1) else 1


def _cmd_demo(args: argparse.Namespace) -> int:
    raw = generate_synthetic_logs(
        n_sessions=args.sessions,
        events_per_session=args.events,
        anomaly_rate=args.anomaly_rate,
        defect_rate=args.defect_rate,
        seed=args.seed,
    )
    result = parse_dataframe(raw, IngestConfig(), source="<demo>")
    batch = extract_features(result)
    tier1 = ModbusFSM().evaluate(result)
    print(result.summary())
    print(
        f"features: rows={len(batch)} sessions={batch.n_sessions} "
        f"columns={len(batch.feature_names)} X={batch.X.shape}"
    )
    print(
        f"tier1: events={len(tier1)} violations={tier1.n_violations} "
        f"rate={tier1.violation_rate:.2%}"
    )
    print()
    print(batch.frame.head(8).to_string(index=False))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        args = parser.parse_args([*list(argv or []), "demo"])
    try:
        return int(args.handler(args))
    except (IngestionError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
