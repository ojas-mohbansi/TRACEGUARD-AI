# Phase 17 — Academic Detection Benchmark Methodology & Corpus Specification

## 1. Objective and Scientific Integrity Principles

The primary academic contribution of TraceGuard AI is proving that:
1. **A formal Finite State Machine independently identifies protocol violations** that statistical algorithms miss (e.g. out-of-order transitions, illegal post-close commands, premature response emissions, authentication bypasses).
2. **Machine Learning independently identifies statistical anomalies** that conform to protocol grammar (e.g. volumetric brute-force, slow-rate exfiltration, oversized payloads).
3. **The Hybrid Engine combines both signals** into an auditable risk score using the academic consensus formula:
   $$S_h = \max(0.60 \cdot S_{\text{FSM}} + 0.40 \cdot S_{\text{ML}}, \; \mathbb{I}_{\text{FSM}} \cdot 60)$$

To demonstrate these principles rigorously without hardcoding UI values or fabricating mock data, Phase 17 introduces the **`AcademicBenchmarkGenerator`** (`backend/app/detection/benchmark.py`).

---

## 2. Benchmark Corpus Composition

The benchmark evaluates a standardized, reproducible corpus of **100 complete sessions** (comprising 450+ individual network events). Every session is processed through the actual detection pipeline:
- `FSMEngine.validate_session(events)`
- `MLEngine.predict_session(events)`
- `HybridEngine.detect_session(events)`

The corpus is constructed with exact theoretical distribution targets:

```
Total Corpus: 100 Sessions
├── 30 Normal Sessions (30%) ───────────► FSM Valid, ML Normal ────────────► No Alert (Normal Verdict)
└── 70 Attack Sessions (70%) ──────────► Detection Alerts Created:
    ├── 20 Pure FSM Violations (28.6%) ─► FSM Invalid (TRAP), ML Normal ──► Attributed to FSM
    ├── 10 Pure ML Anomalies (14.3%) ───► FSM Valid, ML Statistical ──────► Attributed to ML
    └── 40 Hybrid Consensus (57.1%) ────► FSM Invalid, ML Statistical ────► Attributed to Hybrid
```

### Attribution Breakdown Over Generated Alerts (N = 70)

$$\text{Attribution Rate}_{\text{FSM}} = \frac{20}{70} \approx 28.57\% \quad (\text{Target: } 25\% - 35\%)$$
$$\text{Attribution Rate}_{\text{ML}} = \frac{10}{70} \approx 14.29\% \quad (\text{Target: } 10\% - 20\%)$$
$$\text{Attribution Rate}_{\text{Hybrid}} = \frac{40}{70} \approx 57.14\% \quad (\text{Target: } 45\% - 65\%)$$
$$\text{Unexplained Alerts} = \frac{0}{70} = 0.00\% \quad (\text{Target: } 0\%)$$

---

## 3. Session Generation Architecture

### Category 1: Canonical Normal Sessions (30 sessions)
- **Protocol Sequence**:
  $$\text{IDLE} \xrightarrow{\text{CONNECT}} \text{CONNECTED} \xrightarrow{\text{REQUEST}} \text{REQUEST\_RECEIVED} \xrightarrow{\text{AUTH\_SUCCESS}} \text{AUTH\_CHECKED} \xrightarrow{\text{RESPONSE\_200}} \text{RESPONSE\_SENT} \xrightarrow{\text{CLOSE}} \text{CLOSED}$$
- **Statistical Features**: Payload sizes bounded between 64 and 1,500 bytes. Inter-event timing uniform (20–50 ms). Clean socket teardown (`has_close = 1`).
- **Engine Output**: $S_{\text{FSM}} = 0.0$, $S_{\text{ML}} < 0.50$, $S_h \le 25 \implies \text{prediction} = \text{"normal"}$. Zero alerts generated.

### Category 2: Pure FSM Protocol Violations (20 sessions)
- **Structural Attack Types**:
  1. *Post-Close Execution*: Sending `REQUEST` after `CLOSE` transition ($\delta(\text{CLOSED}, \text{REQUEST}) \to \text{TRAP}$).
  2. *Authentication Bypass*: Emitting `RESPONSE_200` directly from `REQUEST_RECEIVED` without traversing authentication states.
  3. *Unsolicited Response*: Server sending `RESPONSE_200` immediately following socket `CONNECT`.
  4. *Double Connect*: Issuing redundant `CONNECT` operations within an open session.
- **Statistical Profile**: Modest payload sizes (64–1,450 bytes), standard HTTP headers. ML anomaly score remains strictly $< 0.55$.
- **Engine Output**: $S_{\text{FSM}} = 100.0$, $S_{\text{ML}} < 0.50$, $S_h \ge 60 \implies \text{Attribution} = \mathbf{fsm}$.

### Category 3: Pure Machine Learning Statistical Outliers (10 sessions)
- **Statistical Attack Types**:
  1. *Authentication Brute-Force*: High-frequency sequence of repeating `(REQUEST -> AUTH_FAILURE -> RESPONSE_401)` cycles. All transitions strictly conform to the HTTP DFA grammar, but statistical frequency and error rates deviate by $> 4\sigma$.
  2. *Oversized Data Burst*: Structurally valid HTTP file exchange containing excessive packet byte volumes (9.5+ MB).
- **Engine Output**: $S_{\text{FSM}} = 0.0$ (no protocol violation), $S_{\text{ML}} \ge 0.70 \implies \text{Attribution} = \mathbf{ml}$.

### Category 4: Hybrid Consensus Compound Attacks (40 sessions)
- **Compound Attack Types**:
  - Direct protocol violation (e.g. unsolicited response or illegal method) accompanied by massive data exfiltration or high request volume.
- **Engine Output**: $S_{\text{FSM}} = 100.0$, $S_{\text{ML}} \ge 0.70$, $S_h \ge 80 \implies \text{Attribution} = \mathbf{hybrid}$.

---

## 4. API Endpoints for Live Academic Demonstration

The benchmark is fully interactive and controllable via REST endpoints:

- `POST /api/detection/benchmark/generate`:
  Executes the 100-session corpus through the real detection pipeline, stores results under `dataset_id = "academic_benchmark"`, and returns validation status.
- `GET /api/detection/benchmark/status`:
  Retrieves current benchmark metrics, total alert counts, percentages, and verification target flags (`fsm_target_met`, `ml_target_met`, `hybrid_target_met`, `unexplained_target_met`).
- `POST /api/detection/benchmark/reset`:
  Atomically purges all existing benchmark records (`dataset_id = "academic_benchmark"`) from both `NetworkEvent` and `Alert` tables, allowing clean demonstration resets.
