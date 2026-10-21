"""Ingestion entry points: raw logs in, validated records and frames out.

Three ingress paths share one validation gate:

* :func:`parse_csv` -- chunked streaming from disk, with optional reject export.
* :func:`parse_records` -- an iterable of mappings (e.g. JSON lines).
* :func:`parse_dataframe` -- an already-tabular frame.

The clean output is a pandas frame with canonical snake_case columns and pinned
dtypes, plus the same rows as :class:`ModbusRecord` objects. Every dropped row
is accounted for in the :class:`RejectionReport`.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable, Mapping, Sequence, Union

import pandas as pd

from .constants import (
    ALIAS_TO_CANONICAL,
    CANONICAL_COLUMNS,
    COLUMN_DTYPES,
    REQUIRED_COLUMNS,
    normalize_column_name,
)
from .models import (
    IngestConfig,
    IngestMeta,
    IngestResult,
    ModbusRecord,
    RejectReason,
    RejectionReport,
    SchemaError,
    SourceError,
    ValidationIssue,
    WarningCode,
)
from .validation import is_blank, validate_row

_DATETIME_DTYPE = "datetime64[ns, UTC]"


# ---------------------------------------------------------------------------
# Frame helpers
# ---------------------------------------------------------------------------


def map_columns(columns: Iterable[Any]) -> dict[str, str]:
    """Map canonical column names to the actual headers in ``columns``.

    Unknown headers are ignored and the first spelling of a duplicated canonical
    field wins, so exports that carry both ``time`` and ``timestamp`` remain
    deterministic instead of creating duplicate columns.
    """
    mapping: dict[str, str] = {}
    for column in columns:
        canonical = ALIAS_TO_CANONICAL.get(normalize_column_name(str(column)))
        if canonical is not None and canonical not in mapping:
            mapping[canonical] = str(column)
    return mapping


def empty_frame() -> pd.DataFrame:
    """A zero-row frame with the full canonical schema and pinned dtypes."""
    return pd.DataFrame(
        {column: pd.Series(dtype=dtype) for column, dtype in COLUMN_DTYPES.items()}
    )[list(CANONICAL_COLUMNS)]


def _cast_frame(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    for column in CANONICAL_COLUMNS:
        if column not in frame.columns:
            frame[column] = None
    for column, dtype in COLUMN_DTYPES.items():
        if dtype == _DATETIME_DTYPE:
            frame[column] = pd.to_datetime(frame[column], utc=True)
        elif dtype == "int64":
            frame[column] = frame[column].astype("int64")
        elif dtype == "Int64":
            frame[column] = frame[column].astype("Int64")
        else:
            frame[column] = frame[column].astype("string")
    return frame[list(CANONICAL_COLUMNS)].reset_index(drop=True)


def records_to_frame(records: Sequence[ModbusRecord]) -> pd.DataFrame:
    """Build the clean frame from typed records."""
    if not records:
        return empty_frame()
    return _cast_frame(pd.DataFrame.from_records([record.as_row() for record in records]))


def frame_to_records(
    frame: pd.DataFrame, *, config: IngestConfig | None = None
) -> list[ModbusRecord]:
    """Inverse of :func:`records_to_frame`; rejects rows that break invariants."""
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise SchemaError(missing, list(map(str, frame.columns)))
    records: list[ModbusRecord] = []
    failures: list[str] = []
    for row in frame.to_dict("records"):
        raw_index = row.get("raw_index")
        outcome = validate_row(
            row,
            config=config,
            raw_index=-1 if is_blank(raw_index) else int(raw_index),
        )
        if outcome.record is None:
            failures.append("; ".join(str(issue) for issue in outcome.issues))
        else:
            records.append(outcome.record)
    if failures:
        raise ValueError(
            f"{len(failures)} row(s) in the frame failed validation: {failures[0]}"
        )
    return records


def resolve_records(
    source: Union[IngestResult, pd.DataFrame, Iterable[ModbusRecord]],
) -> list[ModbusRecord]:
    """Resolve the three accepted input shapes into typed records.

    Shared by the Phase 1.3 feature extractor and the Phase 2.1 FSM engine so
    both tiers accept exactly the same inputs and fail the same way.
    """
    if isinstance(source, IngestResult):
        return list(source.records)
    if isinstance(source, pd.DataFrame):
        return frame_to_records(source)
    records = list(source)
    invalid = [type(item).__name__ for item in records if not isinstance(item, ModbusRecord)]
    if invalid:
        raise TypeError(
            "expected ModbusRecord items; got " + ", ".join(sorted(set(invalid)))
        )
    return records


# ---------------------------------------------------------------------------
# Shared ingestion core
# ---------------------------------------------------------------------------


def _duplicate_key(record: ModbusRecord) -> tuple[Any, ...]:
    return (
        record.source_ip,
        record.dest_ip,
        record.tcp_connection,
        record.transaction_id,
        record.timestamp,
    )


def _ingest_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    config: IngestConfig,
    report: RejectionReport,
    base_index: int = 0,
    seen_keys: set[tuple[Any, ...]] | None = None,
    reject_sink: "_RejectWriter | None" = None,
    last_timestamps: dict[str, datetime] | None = None,
) -> list[ModbusRecord]:
    records: list[ModbusRecord] = []
    if last_timestamps is None:
        last_timestamps = {}
    for offset, row in enumerate(rows):
        raw_index = base_index + offset
        report.record_seen()
        outcome = validate_row(row, raw_index=raw_index, config=config)
        if outcome.record is None:
            for issue in outcome.issues:
                report.add(issue)
            if reject_sink is not None:
                reject_sink(row, outcome.issues)
            continue

        record = outcome.record
        if config.drop_exact_duplicates:
            if seen_keys is None:
                seen_keys = set()
            key = _duplicate_key(record)
            if key in seen_keys:
                report.add(
                    ValidationIssue(
                        RejectReason.DUPLICATE_RECORD,
                        raw_index,
                        "transaction_id",
                        record.transaction_id,
                        "duplicate of an earlier record in this ingest",
                    )
                )
                if reject_sink is not None:
                    reject_sink(row, [ValidationIssue(RejectReason.DUPLICATE_RECORD, raw_index)])
                continue
            seen_keys.add(key)

        previous = last_timestamps.get(record.tcp_connection)
        if previous is not None and record.timestamp < previous:
            report.note_warning(WarningCode.NON_MONOTONIC_TIMESTAMP)
        last_timestamps[record.tcp_connection] = record.timestamp

        for warning in outcome.warnings:
            report.note_warning(warning)
        records.append(record)
        report.record_clean()
    return records


def _finalize(
    records: list[ModbusRecord],
    *,
    config: IngestConfig,
    report: RejectionReport,
    source: str,
    started: float,
    encoding: str | None,
    chunks: int,
) -> IngestResult:
    if config.sort:
        records = sorted(records, key=lambda record: (record.timestamp, record.raw_index))
    frame = records_to_frame(records)
    meta = IngestMeta(
        source=source,
        rows_in=report.rows_seen,
        rows_clean=report.rows_clean,
        rows_rejected=report.rows_rejected,
        elapsed_ms=(perf_counter() - started) * 1000.0,
        encoding=encoding,
        chunks=chunks,
    )
    return IngestResult(frame=frame, records=records, report=report, meta=meta)


def _empty_result(
    *, source: str, config: IngestConfig, started: float, encoding: str | None
) -> IngestResult:
    return IngestResult(
        frame=empty_frame(),
        records=[],
        report=config.new_report(),
        meta=IngestMeta(
            source=source,
            rows_in=0,
            rows_clean=0,
            rows_rejected=0,
            elapsed_ms=(perf_counter() - started) * 1000.0,
            encoding=encoding,
            chunks=0,
        ),
    )


def _validated_subset(frame: pd.DataFrame, mapping: Mapping[str, str]) -> pd.DataFrame:
    subset = frame[list(mapping.values())].rename(
        columns={header: canonical for canonical, header in mapping.items()}
    )
    return subset


# ---------------------------------------------------------------------------
# Public ingress
# ---------------------------------------------------------------------------


def parse_dataframe(
    frame: pd.DataFrame,
    config: IngestConfig | None = None,
    *,
    source: str = "<dataframe>",
) -> IngestResult:
    """Validate an in-memory frame and return the clean frame plus report."""
    config = config or IngestConfig()
    started = perf_counter()
    mapping = map_columns(frame.columns)
    missing = [column for column in REQUIRED_COLUMNS if column not in mapping]
    if missing:
        raise SchemaError(missing, list(map(str, frame.columns)))

    report = config.new_report()
    rows = _validated_subset(frame, mapping).to_dict("records")
    records = _ingest_rows(rows, config=config, report=report)
    return _finalize(
        records,
        config=config,
        report=report,
        source=source,
        started=started,
        encoding=None,
        chunks=1,
    )


def parse_records(
    records: Iterable[Mapping[str, Any]],
    config: IngestConfig | None = None,
    *,
    source: str = "<records>",
) -> IngestResult:
    """Validate an iterable of mapping rows (JSON lines, dicts, ...)."""
    buffered = list(records)
    frame = pd.DataFrame.from_records(buffered) if buffered else empty_frame()
    return parse_dataframe(frame, config, source=source)


def detect_encoding(path: Path) -> str:
    """Choose a decoding for ``path``: UTF-8 (BOM tolerated) else Latin-1."""
    sample = path.read_bytes()[:65536]
    if not sample:
        return "utf-8"
    probe = sample[:-4] if len(sample) > 8 else sample
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            probe.decode(encoding)
        except UnicodeDecodeError:
            continue
        return encoding
    return "latin-1"


class _RejectWriter:
    """Streams rejected raw rows to CSV with their reason codes."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("w", newline="", encoding="utf-8")
        self._writer: csv.DictWriter | None = None

    def __call__(self, row: Mapping[str, Any], issues: Sequence[ValidationIssue]) -> None:
        payload = {
            str(key): "" if is_blank(value) else value for key, value in row.items()
        }
        payload["_reason"] = ";".join(sorted({issue.reason.value for issue in issues}))
        payload["_detail"] = " | ".join(issue.detail for issue in issues if issue.detail)[:500]
        if self._writer is None:
            self._writer = csv.DictWriter(self._handle, fieldnames=list(payload))
            self._writer.writeheader()
        self._writer.writerow(payload)

    def close(self) -> None:
        self._handle.close()

    def __enter__(self) -> "_RejectWriter":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def parse_csv(
    path: str | Path,
    config: IngestConfig | None = None,
    *,
    rejects_out: str | Path | None = None,
) -> IngestResult:
    """Stream a CSV log through the validation gate.

    Rows are processed ``config.chunk_size`` at a time so multi-million-row
    captures stay memory-bounded. Rows with the wrong number of fields are
    reported as ``csv_parse_error`` with their physical line number instead of
    aborting the run.
    """
    config = config or IngestConfig()
    started = perf_counter()
    csv_path = Path(path)
    if not csv_path.exists():
        raise SourceError(f"input file does not exist: {csv_path}")
    if not csv_path.is_file():
        raise SourceError(f"input path is not a file: {csv_path}")
    if csv_path.stat().st_size == 0:
        return _empty_result(
            source=str(csv_path), config=config, started=started, encoding=None
        )
    if rejects_out is not None and Path(rejects_out).resolve() == csv_path.resolve():
        raise SourceError("rejects_out must not overwrite the input log")

    encoding = detect_encoding(csv_path)
    report = config.new_report()
    records: list[ModbusRecord] = []
    seen_keys: set[tuple[Any, ...]] = set()
    last_timestamps: dict[str, datetime] = {}
    chunks = 0
    offset = 0
    buffer_rows: list[dict[str, Any]] = []
    reject_writer: _RejectWriter | None = None

    try:
        with csv_path.open("r", encoding=encoding, newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader, [])
            except csv.Error as exc:
                raise SourceError(f"could not read {csv_path}: {exc}") from exc
            if not header:
                return _empty_result(
                    source=str(csv_path),
                    config=config,
                    started=started,
                    encoding=encoding,
                )

            mapping = map_columns(header)
            missing = [column for column in REQUIRED_COLUMNS if column not in mapping]
            if missing:
                raise SchemaError(missing, header)
            indices = {
                canonical: header.index(header_name)
                for canonical, header_name in mapping.items()
            }
            if rejects_out is not None:
                reject_writer = _RejectWriter(rejects_out)

            def flush() -> None:
                nonlocal chunks, offset
                if not buffer_rows:
                    return
                records.extend(
                    _ingest_rows(
                        buffer_rows,
                        config=config,
                        report=report,
                        base_index=offset,
                        seen_keys=seen_keys,
                        reject_sink=reject_writer,
                        last_timestamps=last_timestamps,
                    )
                )
                offset += len(buffer_rows)
                buffer_rows.clear()
                chunks += 1

            for row in reader:
                if not row:
                    continue
                line_number = reader.line_num
                if len(row) != len(header):
                    flush()
                    report.record_seen()
                    issue = ValidationIssue(
                        RejectReason.CSV_PARSE_ERROR,
                        raw_index=line_number,
                        detail=(
                            f"line {line_number}: expected {len(header)} fields, "
                            f"got {len(row)}"
                        ),
                    )
                    report.add(issue)
                    continue
                buffer_rows.append(
                    {canonical: row[index] for canonical, index in indices.items()}
                )
                if len(buffer_rows) >= config.chunk_size:
                    flush()
            flush()
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise SourceError(f"could not read {csv_path}: {exc}") from exc
    finally:
        if reject_writer is not None:
            reject_writer.close()

    return _finalize(
        records,
        config=config,
        report=report,
        source=str(csv_path),
        started=started,
        encoding=encoding,
        chunks=chunks,
    )


if __name__ == "__main__":  # pragma: no cover - manual smoke entry point
    import sys

    result = parse_csv(sys.argv[1]) if len(sys.argv) > 1 else parse_records([])
    print(result.summary())
