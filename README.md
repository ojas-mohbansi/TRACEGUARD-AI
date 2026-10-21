# FSM-NIDS — Hybrid Modbus/TCP NIDS

Local, CPU-only intrusion detection for Modbus/TCP industrial traffic. The
hybrid detector combines an FSM-based protocol model with statistical/ML
features; the pipeline is built phase by phase.

**Current scope: Phase 2.1 — Tier-1 deterministic protocol FSM (complete);
Phase 1.3 session-isolated features remain the input layer for the Tier 2/3
stages.**

## Layout

```
modbus_nids/
├── constants.py   # MBAP bounds, function-code table, canonical schema + aliases
├── models.py      # ModbusRecord, IngestConfig, RejectionReport, IngestResult, ...
├── validation.py  # reason-coded structural + protocol validation
├── parser.py      # CSV / record / DataFrame ingress, typed frame out
├── synthetic.py   # seeded Modbus traffic simulator + defect injector
├── window.py      # per-session sliding windows, pruning, feature math
├── features.py    # batch extraction API over records / frames / IngestResult
├── fsm.py         # Tier-1 protocol state machine, verdicts, conversation keys
└── cli.py         # generate | parse | features | fsm | demo
tests/             # pytest suite (validation, parser, synthetic, window, FSM, CLI)
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

## Session-isolated features (Phase 1.3)

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
`function_code`, `register_address`, `quantity`, `unit_id`, `direction`,
`label`, `raw_index` — is carried on every row, so feature matrices stay aligned
with ground truth and source provenance for the Tier 1 FSM and Tier 2/3 ML
stages. Optional protocol fields use nullable `Int64`; string metadata uses
pandas `string`; the 17 feature columns are always `float64`. The empty result
from `transform([])` has exactly the same columns and dtypes as a populated
frame.

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

### Session lifecycle and pruning

A long-running manager would otherwise retain a window forever for every flow it
has ever seen. Three opt-in controls bound that memory:

```python
from datetime import datetime, timezone
from modbus_nids import SessionWindowManager

manager = SessionWindowManager(
    window_size=10,
    idle_timeout=30.0,   # restart one session if its own gap exceeds 30 s
    max_sessions=50_000, # LRU-evict on overflow of a new session
)

row = manager.add(record)
manager.prune(datetime.now(timezone.utc))  # explicit idle sweep
```

* `idle_timeout` is evaluated **per session** on `add()`: if a flow resumes after
  a longer gap, its stale window is evicted and the new event is a genuine
  session start (`is_session_start=1`, `dt_seconds=0`,
  `log_dt=log(epsilon)`). This is safe under interleaved traffic because one
  session's clock is never compared to another's.
* `max_sessions` is a hard cap. Adding a **new** session at the cap evicts the
  least-recently-used session first. It is off by default and intentionally
  sacrifices that session's temporal context; existing sessions are never split.
* `prune(reference, idle_timeout=...)` evicts every session whose newest event
  is older than the cutoff and returns the number removed. With no `reference`
  it uses the latest timestamp the manager has observed, which keeps offline
  runs deterministic; live callers should pass the current UTC time. Sessions
  exactly at the cutoff are retained. `prune()` with no policy raises
  `ValueError`.
* `last_seen(key)` exposes a session's newest retained timestamp;
  `evicted_sessions` is cumulative since construction or the last `reset()`.

Because pruning removes temporal context, a session that reappears after
pruning is a new session and its first delta is zero. Choose timeouts that match
the plant's polling cadence rather than using pruning as a generic cache squeeze.

On a 200,000-row log spanning 4,000 sessions, extraction runs at roughly 54k
rows/s on a single CPU core (3.7 s), producing a finite `(200000, 17)` matrix.

## Tier-1 protocol FSM (Phase 2.1)

`modbus_nids.fsm.ModbusFSM` is the deterministic, hard-protocol half of the
detector. It consumes the same `ModbusRecord` stream as the feature extractor
and returns one verdict per event: a score, a decision, a stable reason code
and the provenance needed to reconstruct exactly what the engine saw. A
violation short-circuits the pipeline (`score = 1.0`, `bypass_ml = True`); a
clean event scores `0.0` and is forwarded to the Tier 2/3 stages.

The engine is a *protocol* checker, not a behavioural one. "Is this exchange
possible in a well-formed Modbus/TCP conversation?" is Tier 1; "is this traffic
unusual?" — write floods, register sweeps, off-hours bursts — stays in Tier
2/3.

### Conversations are canonicalised, not directional

A request and its response travel in opposite directions, so the directional
`(source_ip, dest_ip, connection)` key used for feature windows would split an
exchange across two sessions. `ConversationKey` stores
`(client_ip, server_ip, tcp_connection)` instead, and its `label`
(`client|server|connection`) is byte-identical to the existing `flow_key` for
request-only captures.

Roles are resolved per event and the evidence is recorded as `role_source`:

| Precedence | Source | Meaning |
|---|---|---|
| 1 | `ports` | exactly one of `source_port`/`dest_port` is an allowed Modbus port: `dest` ⇒ request, `source` ⇒ response |
| 2 | `declared` | the `direction` column, when the ports are absent or ambiguous |
| 3 | `learned` | the roles established by an earlier event on the same connection |
| 4 | `default` | nothing was available; the source end is treated as the client |

Ports outrank the `direction` column on purpose: exporters mislabel direction
often, and the synthetic `exception_response` defect keeps client→server
endpoints while declaring `direction="response"`. Ports-first attributes the
packet to the right conversation, so the engine reports the real fault
(`response_without_request`) instead of a direction artefact. A contradiction
between the ports and the declared direction is recorded as the soft note
`direction_conflict`, never as a violation. The Modbus exception flag (0x80)
outranks everything for the *message* role, because only a server sets it.

`strict_direction` turns an unproven role into a hard violation
(`direction_unresolved`). A role is proven when a Modbus port or the
`direction` column establishes it; a role merely *learned* from an earlier
event does not count, because the earlier event was itself unproven — so
every event of a portless capture is flagged, not just the first.

### States, symbols and the transition table

`SessionState` is `idle`, `request_sent` (exactly one transaction in flight),
`waiting_response` (two or more — legal pipelining) and `error` (the previous
event was a violation). `FSMSymbol` records the provenance of an event
(`request_read_03`, `request_write_single_06`, `request_write_multiple_10`,
`request_other`, the matching `response_*` symbols and `response_exception`)
and folds to a `SymbolClass` of `request` or `response`.

The transition table is a declared, module-level mapping:

| State | REQUEST | RESPONSE |
|---|---|---|
| `idle` | `request_sent` | `forbidden` |
| `request_sent` | `waiting_response` | `derived` |
| `waiting_response` | `waiting_response` | `derived` |
| `error` | `derived` | `derived` |

`derived` recomputes the state from the number of transactions still in flight
(`0 → idle`, `1 → request_sent`, `≥2 → waiting_response`). A pair missing from
the table is an *undefined* transition and is reported as
`undefined_transition` rather than silently accepted. `error` is a one-event
quarantine: the next structurally valid event recovers the conversation, so one
malformed packet cannot cascade across a whole capture.

### Hard rules and soft notes

A request is checked against the open transactions of its conversation before
it is accepted:

* a transaction ID that is still open, or that was closed recently (the
  `tid_history` ring, default 256), is a violation — `transaction_id_reuse`;
* an optional `supported_function_codes` allow-list rejects other request
  codes — `unsupported_function_code`.

A response is matched to its request by transaction ID:

* no open request — `response_without_request`;
* the transaction was already answered — `response_after_close`;
* a function code that contradicts the request — `function_code_mismatch`;
* an exception response with the wrong MBAP length —
  `exception_length_invalid`;
* a unit ID that contradicts the request — `unit_id_mismatch`;
* a response that arrives while the conversation is in error and matches no
  open request — `session_in_error`.

Soft observations are counted for auditing but never scored:
`incomplete_transaction`, `outstanding_evicted`, `transaction_expired`,
`direction_inferred`, `direction_conflict`, `session_evicted`.

**Unanswered requests are legal.** Modbus/TCP allows several requests in
flight on one connection, and many captures only contain one direction, so an
unanswered request stays open and is reported as an incomplete transaction at
`finish()`. It is never a violation.

### Verdicts

```python
from modbus_nids import FSMConfig, ModbusFSM, evaluate_tier1

tier1 = evaluate_tier1(result)      # IngestResult, DataFrame or records
verdict = tier1.verdicts[0]
verdict.score, verdict.decision, verdict.bypass_ml   # 0.0 / "benign" / False
verdict.reason, verdict.detail                       # None / "" when clean

engine = ModbusFSM(FSMConfig(tid_history=512, max_sessions=10_000))
tier1 = engine.evaluate(result)
summary = engine.finish()      # events, sessions, violations, reasons, notes
frame = tier1.to_frame()       # one row per event, 19 pinned columns
```

`Tier1Verdict` carries `raw_index`, `session_id`/`session_key`, `symbol`,
`symbol_class`, `direction`, `role_source`, `transaction_id`, `function_code`,
`state_before`, `state_after`, `outstanding`, `reason`, `detail`, `score`,
`decision`, `bypass_ml` and `notes`. `Tier1Result` adds `scores`,
`decisions`, `anomaly_mask`, `reasons`, `n_violations`, `violation_rate`,
`n_sessions`, `to_frame()`, `to_dict()` and `summary()`.

### Bounds

Memory is bounded on every axis: at most `max_outstanding` open transactions
(default 64) and `tid_history` closed transaction IDs (default 256) per
conversation, and at most `max_sessions` conversations (LRU eviction, off by
default); the learned-role map is bounded by the same cap. `response_timeout`
(seconds, measured on event timestamps rather than the wall clock, so batch
runs stay deterministic) expires transactions that were never answered.
`prune(reference, idle_timeout=...)` evicts idle conversations, mirroring
`SessionWindowManager`.

On a 200,000-row log spanning 4,000 conversations the Tier-1 pass runs at
roughly 72k events/s on a single CPU core (2.7 s).

### Running it from the shell

Every policy knob of `FSMConfig` is reachable from the `fsm` subcommand, so a
plant policy can be applied without writing Python:

```bash
.venv/Scripts/python -m modbus_nids.cli fsm \
    --in data/synthetic.csv --out data/tier1.csv --report data/tier1.json \
    --supported-function-code 3 --supported-function-code 16 \
    --response-timeout 5 --max-sessions 50000 --strict-direction
```

| Flag | Effect |
|---|---|
| `--allowed-port` | repeatable; the Modbus ports that identify the server end (default `502`) |
| `--supported-function-code` | repeatable; request codes the plant may use — anything else is `unsupported_function_code` |
| `--response-timeout` | seconds after which an unanswered transaction expires (measured on event timestamps) |
| `--max-sessions` | cap on tracked conversations; the least recently used is evicted |
| `--max-outstanding` | open transactions kept per conversation |
| `--tid-history` | recently closed transaction IDs remembered per conversation |
| `--strict-direction` | treat an unproven direction as a violation |

An invalid policy (a zero session cap, a negative timeout, a function code
outside 1–127) exits `2` with the reason on stderr, like any other fatal
input error.

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

# 4. Run the Tier-1 protocol state machine over the same log
.venv/Scripts/python -m modbus_nids.cli fsm \
    --in data/synthetic.csv --out data/tier1.csv --report data/tier1.json \
    --supported-function-code 3 --response-timeout 5

# 5. Or run the in-memory demo (generate, parse, featurise and evaluate)
.venv/Scripts/python -m modbus_nids.cli demo
```

`parse`, `features` and `fsm` exit `0` on success, `1` when no row survives
validation (or, for `fsm`, when the log yields no event), and `2` on a fatal
input error (missing file, missing required column, unreadable encoding,
invalid window configuration).
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

```python
from modbus_nids import ModbusFSM

tier1 = ModbusFSM().evaluate(result)
print(tier1.summary())        # events, violations, reasons, notes
verdicts = tier1.to_frame()   # one row per event, aligned with the clean frame
```

CSV ingestion streams `chunk_size` rows at a time, so large captures stay
memory-bounded; on a 200k-row synthetic log it sustains roughly 35k rows/s on a
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

Phase 1.3 adds: explicit idle pruning (deterministic default reference, cutoff
boundary, idempotence), per-session `idle_timeout` restart semantics, the
`max_sessions` LRU cap, `last_seen` / `evicted_sessions` reporting, Tier-1
metadata provenance (including nullable protocol fields), and dtype equality
between empty and populated feature frames.

Phase 2.1 adds: the state table and its undefined-transition guard, the
ports-first role resolution and its `role_source` provenance, canonical
conversation keys shared by a request and its response, transaction
correlation with the open/closed rings, every hard rule (`response_without_
request`, `response_after_close`, `function_code_mismatch`, `unit_id_mismatch`,
`exception_length_invalid`, `transaction_id_reuse`, `undefined_transition`,
`forbidden_transition`, `session_in_error`, `unsupported_function_code`), the
one-event error quarantine and its recovery, the `id → request_sent → derived`
state sequence, pipelining and unanswered requests staying legal, per-event
verdict provenance, the memory bounds (`max_outstanding`, `tid_history`,
`max_sessions`, `response_timeout`, `prune`), and the `fsm` CLI writing a
verdict frame whose row count matches the clean frame.

Phase 2.1 completion adds: the CLI policy knobs (`--supported-function-code`,
`--response-timeout`, `--max-sessions`, `--strict-direction`), the strict
direction gate rejecting an unproven *learned* role as well as a default one,
and the CLI end to end for each of them.
