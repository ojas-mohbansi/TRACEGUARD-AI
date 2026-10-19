# FSM-NIDS — Hybrid Modbus/TCP NIDS

Local, CPU-only intrusion detection for Modbus/TCP industrial traffic. The
hybrid detector combines an FSM-based protocol model with statistical/ML
features; the pipeline is built phase by phase.

**Current scope: Phase 1.2 — session-isolated windows and feature extraction
(complete); Phase 1.1 ingestion is its input layer.**

## Layout

```
modbus_nids/
├── constants.py   # MBAP bounds, function-code table, canonical schema + aliases
├── models.py      # ModbusRecord, IngestConfig, RejectionReport, IngestResult, ...
├── validation.py  # reason-coded structural + protocol validation
├── parser.py      # CSV / record / DataFrame ingress, typed frame out
├── synthetic.py   # seeded Modbus traffic simulator + defect injector
├── window.py      # per-session sliding windows + incremental feature math
├── features.py    # batch extraction API over records / frames / IngestResult
└── cli.py         # generate | parse | demo
tests/             # pytest suite (validation, parser, synthetic, window, CLI)
```

## Input contract

Each row describes one Modbus/TCP event and must carry the following fields
(header matching is case-, space- and underscore-insensitive; common aliases
such as `src_ip`, `tid`, `fc`, `addr`, `length`, `attack` are accepted):

| Canonical | Type | Meaning |
|---|---|---|
| `timestamp` | ISO-8601 or epoch | event time, normalised to UTC |
| `source_ip` / `dest_ip` | string | endpoint addresses |
| `tcp_connection` | string / int | socket or stream identifier |
| `transaction_id` | 0–65535 | MBAP transaction ID |
| `function_code` | 1–127, 128–255 | Modbus FC, exception bit preserved |
| `register_address` | 0–65535, nullable | target register |
| `data_length` | 2–254 | MBAP length (unit ID + PDU) |
| `label` | 0 / 1 | 0 normal, 1 anomalous |

Optional enrichment columns: `source_port`, `dest_port`, `protocol_id`,
`unit_id`, `quantity`, `direction`. Epoch timestamps are auto-scaled across
seconds/milliseconds/microseconds/nanoseconds.

## Validation gate (strict profile)

Rows that fail a hard rule are dropped and counted under a stable reason code
(`missing_field`, `bad_timestamp`, `bad_ip`, `bad_tcp_connection`,
`tid_out_of_range`, `bad_port`, `protocol_id_nonzero`,
`mbap_length_out_of_bounds`, `fc_out_of_range`, `register_out_of_range`,
`quantity_out_of_bounds`, `label_not_binary`, `not_modbus_framed`,
`duplicate_record`, `csv_parse_error`, `invalid_record`).

* Ports, when present, must include an allowed Modbus port (default 502);
  otherwise the row must prove explicit Modbus framing (valid function code,
  protocol ID 0, MBAP length in bounds).
* Per-function-code quantity bounds are enforced when `quantity` is present:
  FC1/2 1–2000, FC3/4 1–125, FC15 1–1968, FC16 1–123, FC23 read 1–125.
* Soft anomalies (`length_inconsistent`, `non_monotonic_timestamp`,
  `unknown_function_code`) are counted as warnings on retained rows, not
  dropped. Request-length consistency is checked only when `direction` is
  known, since responses carry a byte count rather than a quantity.
* Duplicate (retransmitted) rows are kept by default; `IngestConfig` can drop
  exact duplicates, which is deliberately opt-in because retransmission is
  itself NIDS signal.

Rejected rows never silence the run: the parser returns a `RejectionReport`
with per-reason counts, rejection rate, and up to `max_reject_samples` examples
per reason, serialisable via `summary()`, `to_frame()`, and `to_json()`.

## Output contract

`IngestResult.frame` carries canonical snake_case columns with pinned dtypes:

* `timestamp` → `datetime64[ns, UTC]`
* `source_ip`, `dest_ip`, `tcp_connection`, `direction` → `string`
* `transaction_id`, `function_code`, `data_length`, `label` → `int64`
* `register_address`, `quantity`, ports, `protocol_id`, `unit_id` → `Int64`
* derived `flow_key` (`src|dst|connection`) and `raw_index` (source row)

Rows are sorted by timestamp (stable, with `raw_index` as tiebreaker), and
`IngestResult.records` contains the same rows as typed `ModbusRecord` objects.
`records_to_frame` / `frame_to_records` round-trip between the two.

## Session-isolated features (Phase 1.2)

`window.SessionWindowManager` keeps an independent bounded window of the last
`k = 10` events (configurable) per session. The key is the directional tuple
`(source_ip, dest_ip, tcp_connection)` — the same tuple as the derived
`flow_key`, exposed as `session_id`. The Modbus transaction ID is deliberately
*not* part of the key: it changes every request, so keying on it would produce a
fresh window per event and destroy all temporal context. TID continuity is
instead a feature (`tid_delta`). Because the key is directional, request and
response streams are separate sessions unless the caller normalises endpoints
before ingest.

Events for a session must arrive in non-decreasing timestamp order; a regression
raises `WindowError` rather than silently corrupting deltas. Batch parsing sorts
globally, so per-session order is guaranteed for `parse_csv`/`parse_dataframe`
inputs.

Per event, the extractor emits (current event included in the window):

| Feature | Definition |
|---|---|
| `dt_seconds` | `t_i - t_{i-1}` in seconds, `0` at session start |
| `log_dt` | `log(dt_seconds + epsilon)`, `epsilon = 1e-6` s; a session start therefore scores `log(epsilon)` (finite, not NaN) |
| `is_session_start` | `1` for the first event of a session |
| `tid_delta` | `(TID_i - TID_{i-1}) mod 65536`, `0` at session start |
| `window_event_count`, `window_fill_ratio` | occupancy of the trailing window |
| `write_count`, `read_count`, `other_count` | FC classes in the window (writes 0x05/0x06/0x0F/0x10, reads 0x01–0x04; exception bit folded to the base FC) |
| `write_read_ratio` | `write_count / max(read_count, 1)` |
| `write_fraction` | `write_count / max(write + read, 1)` |
| `ngram_unique_{2,3,5}` | distinct symbol n-grams in the window |
| `ngram_novelty_{2,3,5}` | `1` if the newest n-gram is new within the window, else `0` |

Metadata — `session_id`, endpoints, `timestamp`, `transaction_id`,
`function_code`, `label`, `raw_index` — is carried on every row, so feature
matrices stay aligned with ground truth and source provenance for the Tier 1
FSM and Tier 2/3 ML stages.

```python
from modbus_nids import extract_features, parse_csv

result = parse_csv("data/synthetic.csv")
batch = extract_features(result, window_size=10)

batch.X             # float64 (n_events, 17)
batch.y             # int64 labels, aligned
batch.raw_index     # source row ids, aligned
batch.session_ids   # session id per row
batch.frame         # metadata + features as one DataFrame
```

`extract_features` accepts an `IngestResult`, a clean `DataFrame`, or any
iterable of `ModbusRecord`. For streaming use, drive
`SessionWindowManager.add(record)` directly and call `reset()` between captures.
The manager is stateful and not thread-safe; use one instance per stream.

On a 200,000-row log spanning 4,000 sessions, extraction runs at roughly 80k
rows/s on a single CPU core (2.4 s), producing a finite `(200000, 17)` matrix.

## Setup

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
.venv/bin/python -m pip install -r requirements.txt       # POSIX
```

## Usage

```bash
# 1. Generate a synthetic log (deterministic per seed)
.venv/Scripts/python -m modbus_nids.cli generate \
    --out data/synthetic.csv --sessions 60 --events 60 \
    --anomaly-rate 0.05 --defect-rate 0.02 --seed 2026

# 2. Parse it, exporting clean rows, rejects and an audit report
.venv/Scripts/python -m modbus_nids.cli parse \
    --in data/synthetic.csv --out data/clean.csv \
    --rejects data/rejects.csv --report data/report.json

# 3. Compute session-isolated window features for the clean rows
.venv/Scripts/python -m modbus_nids.cli features \
    --in data/synthetic.csv --out data/features.csv --window-size 10

# 4. Or run the in-memory demo (generate, parse and featurise)
.venv/Scripts/python -m modbus_nids.cli demo
```

`parse` and `features` exit `0` on success, `1` when no row survives validation,
and `2` on a fatal input error (missing file, missing required column, unreadable
encoding, invalid window configuration).
The JSON report contains `meta` (provenance, counts, timing) and `report`
(reason-code counts and samples).

Python API:

```python
from modbus_nids import IngestConfig, parse_csv

result = parse_csv("data/synthetic.csv", IngestConfig(chunk_size=100_000))
print(result.summary())
clean = result.frame          # typed, sorted, session-ready
records = result.records      # list[ModbusRecord]
```

CSV ingestion streams `chunk_size` rows at a time, so large captures stay
memory-bounded; on a 200k-row synthetic log it sustains roughly 40k rows/s on a
single CPU core.

## Tests

```bash
.venv/Scripts/python -m pytest -q
```

Covers timestamp forms and epoch scaling (seconds through nanoseconds), MBAP
length bounds (2 and 254), port scope with the default and a custom allow-list,
function-code quantity bounds (FC1/2/3/4/15/16/23) and request-length checks
(FC3/7/15/16/22/23/24/43), sorting and `sort=False` ordering, report
accounting/serialisation, CSV streaming (chunk boundaries, BOM, bad-line file
numbers, rejects export), generator determinism and defect accounting, and the
CLI end to end.

Phase 1.2 adds: session isolation under interleaved traffic, per-session window
bounding and reset, log-delta stability, TID wrap continuity, write/read ratio
and fraction, n-gram novelty for n = 2/3/5, label/`raw_index` alignment, batch
extraction from all three input shapes, empty input, timestamp-regression
rejection, and the `features` CLI writing a matrix whose row count, session
count and `raw_index` order match the clean frame.
