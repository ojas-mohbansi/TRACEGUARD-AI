# Phase 17 — Threat Engine Analytics & Visual Investigation Architecture

## 1. Overview and Design Rationale

In earlier phases, threat charts displayed aggregated metrics that mixed distinct mathematical concepts:
- Final alert attribution (which must sum to 100% across mutually exclusive engine categories) was conflated with component detection rates (where both FSM and ML can simultaneously detect anomalies in the same session).
- Evaluators had no ability to isolate calibrated academic benchmark data from raw live packet streams or test probe runs.
- FSM protocol violations were buried inside a generic severity count with no visibility into which DFA states were violated, which symbols caused transitions into `TRAP`, or whether the absorbing invariant held.

In **Phase 17**, the Threat Analytics dashboard (`frontend/src/pages/Threats.jsx`) was redesigned into **three distinct analytical perspectives**, backed by an interactive **Telemetry Scope Switcher**.

---

## 2. Telemetry Scope Switcher

The top of the Threat Triage & Forensics page features an interactive scope switcher:
1. **Academic Benchmark** (`benchmark`):
   Scoped to the 100-session calibrated academic corpus (`dataset_id = "academic_benchmark"`). Displays the official 28.57% FSM / 14.29% ML / 57.14% Hybrid verification baseline.
2. **Live / Historical Stream** (`live_historical`):
   Scoped to real-time packet capture and simulation events, completely segregated from benchmark data.
3. **PCAP Offline Replay** (`pcap`):
   Scoped to ingested Wireshark/tcpdump PCAP captures.
4. **All Datasets** (`all`):
   Global view spanning all telemetry sources.

Beside the switcher are two live demonstration controls:
- **Run Academic Benchmark**: Generates and executes the 100-session benchmark in real-time.
- **Reset Benchmark**: Purges benchmark records for a clean demonstration slate.

---

## 3. The Three Analytical Views

### View 1: Final Alert Attribution (100% Mutually Exclusive Distribution)
- **Visualization**: Donut chart rendered via Recharts.
- **Mathematical Rule**: Every generated alert is assigned to **exactly one** engine category based on which engine triggered the detection:
  $$\text{Total Alerts} = N_{\text{FSM}} + N_{\text{ML}} + N_{\text{Hybrid}} + N_{\text{Unknown}}$$
  $$\frac{N_{\text{FSM}}}{N} + \frac{N_{\text{ML}}}{N} + \frac{N_{\text{Hybrid}}}{N} + \frac{N_{\text{Unknown}}}{N} = 100.0\%$$
- **Target Verification Cards**:
  - **FSM-Only Attribution**: Target $25\% - 35\%$, Achieved **28.6%** (Target Met Badge).
  - **ML-Only Attribution**: Target $10\% - 20\%$, Achieved **14.3%** (Target Met Badge).
  - **Hybrid Consensus**: Target $45\% - 65\%$, Achieved **57.1%** (Target Met Badge).
  - **Unexplained / Unknown**: Target $0\%$, Achieved **0.0%** (Target Met Badge).

### View 2: Component Detection Contributions (Overlapping Detection Capabilities)
- **Visualization**: Grouped multi-bar chart comparing:
  - Total Sessions Flagged by FSM (Pure FSM + Hybrid Consensus = 60 sessions).
  - Total Sessions Flagged by ML (Pure ML + Hybrid Consensus = 50 sessions).
  - Joint Hybrid Consensus (40 sessions).
- **Consensus Scoring Card**: Formally documents the hybrid scoring equation:
  $$S_h = \max(0.60 \cdot S_{\text{FSM}} + 0.40 \cdot S_{\text{ML}}, \; \mathbb{I}_{\text{FSM}} \cdot 60)$$
  Explaining how the 60% floor ensures deterministic DFA violations can never be downgraded by statistical uncertainty.

### View 3: FSM Protocol Invariant Analytics (Formal Verification)
Dedicated specifically to Theory of Computation evaluators:
1. **Violations by DFA State**:
   Horizontal bar chart illustrating the distribution of illegal transitions originated from each state (e.g. `CLOSED`, `REQUEST_RECEIVED`, `CONNECTED`, `AUTH_CHECKED`).
2. **Unexpected Transition Symbols**:
   Bar chart showing which alphabet symbols triggered transitions into `TRAP` (e.g. `REQUEST`, `RESPONSE_200`, `CONNECT`, `AUTH_SUCCESS`).
3. **Absorbing TRAP Invariant Verification Card**:
   - Total transitions into `TRAP` recorded.
   - Self-loop proof: $\forall \sigma \in \Sigma, \; \delta(\text{TRAP}, \sigma) = \text{TRAP}$.
   - Mathematical proof that the absorbing state prevents recovery to legal states without establishing a fresh TCP connection.

---

## 4. Interactive Forensic Investigation Integration

In the Alert Feed table below the analytics charts:
- Each alert features an **"Inspect"** button.
- Clicking "Inspect" smoothly scrolls to the right-hand **Forensic Investigation** panel and populates:
  - Complete chronological event timeline.
  - State machine transition trajectory ($s_0 \to s_1 \to \dots \to \text{TRAP}$).
  - Highlighted violation event showing exact unexpected symbol and state mismatch.
  - ML anomaly score and feature importance contributions.
  - Raw event attributes (IP addresses, ports, timestamps, byte counts, HTTP status codes).
