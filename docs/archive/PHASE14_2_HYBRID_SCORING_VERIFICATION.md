# Phase 14.2: Hybrid Scoring Architecture & Quadrant Verification

**Document Version**: 1.0.0  
**Status**: VERIFIED & AUDITED  
**Date**: 2026-11-17  
**Author**: Antigravity Detection & ML Verification Swarm  

---

## 1. Hybrid Detection Formula & Mathematical Properties

TraceGuard AI combines deterministic formal automata protocol verification with probabilistic machine learning anomaly detection into a unified risk scoring function:

$$S_h = f(S_{\text{FSM}}, S_{\text{ML}})$$

### 1.1 The Mathematical Model
In standard operational conditions, the base hybrid score is the weighted convex combination:

$$S_{\text{base}} = w_{\text{FSM}} \cdot S_{\text{FSM}} + w_{\text{ML}} \cdot S_{\text{ML}}$$

where:
- $w_{\text{FSM}} = 0.6$ (60% weight allocated to protocol state conformance).
- $w_{\text{ML}} = 0.4$ (40% weight allocated to Isolation Forest statistical anomaly scoring).
- $w_{\text{FSM}} + w_{\text{ML}} = 1.0$.

### 1.2 The Deterministic Violation Floor
A fundamental security axiom of TraceGuard AI is that **formal protocol violations cannot be suppressed or smoothed out by machine learning statistics**. Even if an attacker's packet payload exhibits statistical normalcy according to the Isolation Forest model, an out-of-order protocol transition represents an unambiguous structural attack.

Therefore, the engine enforces a **60% Risk Floor**:

$$S_h = \begin{cases} 
\max(0.6 \cdot S_{\text{FSM}} + 0.4 \cdot S_{\text{ML}}, 60.0) & \text{if FSM Violation} = \text{True} \\
0.6 \cdot S_{\text{FSM}} + 0.4 \cdot S_{\text{ML}} & \text{if FSM Violation} = \text{False}
\end{cases}$$

---

## 2. The Four Operational Detection Quadrants

The dual-engine architecture produces a 2x2 detection matrix that addresses every combination of protocol validity and payload statistical distribution:

```
                  FSM VALID (Conforming)       FSM INVALID (Violation)
               +----------------------------+----------------------------+
               | Quadrant 1: KNOWN NORMAL   | Quadrant 3: KNOWN ATTACK   |
  ML NORMAL    | S_h in [0, 35]             | S_h >= 60.0 (Floor Applied)|
               | Low Risk                   | High Risk                  |
               +----------------------------+----------------------------+
               | Quadrant 2: NOVEL NORMAL   | Quadrant 4: COMPOUND ATTACK|
  ML ANOMALOUS | S_h in [25, 55]            | S_h >= 70.0                |
               | Medium Risk (Flagged)      | Critical / High Risk       |
               +----------------------------+----------------------------+
```

### 2.1 Quadrant 1: Known Normal Traffic
- **Characteristics**: Protocol sequence strictly follows valid transitions; payload features (packet size, inter-arrival time, header length) align with baseline distribution.
- **Example**: Standard GET request returning HTTP 200 with normal headers.
- **Engine Output**: FSM score = 0, ML score $\approx 0.05 \rightarrow S_h \approx 2 \rightarrow$ **LOW severity**.

### 2.2 Quadrant 2: Novel Normal / Zero-Day Statistical Anomaly
- **Characteristics**: Protocol transitions are valid, but payload features deviate significantly from historical training data (e.g. unusually large payloads, bursty request patterns).
- **Example**: File upload or API batch request executing valid HTTP sequence.
- **Engine Output**: FSM score = 0, ML score $\approx 0.75 \rightarrow S_h \approx 30 \rightarrow$ **MEDIUM severity** (queued for inspection without false-positive blocking).

### 2.3 Quadrant 3: Known Protocol Exploit (Statistical Stealth)
- **Characteristics**: Attacker crafts packets whose statistical properties mimic normal traffic, but performs an out-of-sequence request (e.g. state evasion, unauthenticated endpoint access, out-of-order response injection).
- **Example**: `AUTH_CHECKED` followed directly by `REQUEST` without completing transaction.
- **Engine Output**: FSM score = 60, ML score = 0. Base score = 36, but **60% Floor activates** $\rightarrow S_h = 60.0 \rightarrow$ **HIGH severity**.

### 2.4 Quadrant 4: Compound / High-Volume Attack
- **Characteristics**: Attacker executes invalid protocol transitions accompanied by highly anomalous traffic volumes, malformed byte streams, or port scans.
- **Example**: Malformed HTTP fuzzing flood.
- **Engine Output**: FSM score = 60-100, ML score $\ge 0.90 \rightarrow S_h \ge 74.0 \rightarrow$ **CRITICAL / HIGH severity**.

---

## 3. UI Slider Reconciliation Audit

### 3.1 Observed State
In `Settings.jsx`, users observed a slider showing a 75% FSM weight position in some browser sessions.

### 3.2 Audit Determination
1. **Frontend Role**:
   - `Settings.jsx` manages local user display preferences persisted to browser `localStorage` under `traceguard_fsm_weight`.
   - The UI includes an explicit **Academic Scope Banner** explaining:
     > *"Backend hybrid detection enforces the mathematically verified 0.6 FSM / 0.4 ML ratio with the 60% FSM risk floor to maintain academic reproducibility. Sliders in this panel configure client-side threshold views."*
2. **Backend Engine Invariant**:
   - In `backend/app/detection/hybrid/engine.py`, the weights $w_{\text{FSM}} = 0.6$ and $w_{\text{ML}} = 0.4$ and the 60.0 risk floor are strictly hardcoded constants in the mathematical evaluation pipeline.
   - Client display adjustments do not perturb backend engine decisions.

---

## 4. Verification Evidence

- Test Suite: [backend/tests/test_hybrid_scoring_integrity.py](file:///c:/Projects/FSM-NIDS/backend/tests/test_hybrid_scoring_integrity.py) (5/5 Passed)
- JSON Export: [qa/phase14_2/hybrid-scoring-verification.json](file:///c:/Projects/FSM-NIDS/qa/phase14_2/hybrid-scoring-verification.json)
- Pytest Log: [qa/phase14_2/backend-pytest.log](file:///c:/Projects/FSM-NIDS/qa/phase14_2/backend-pytest.log)
