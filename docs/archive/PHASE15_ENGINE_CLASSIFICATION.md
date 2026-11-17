# Phase 15: Engine Classification & Provenance Architecture

## 1. Problem Statement & Root Cause Analysis

### 1.1 The Single-Engine Defect
In earlier iterations of TraceGuard AI, the "Engine Classification" chart on the main SecOps Dashboard displayed 100% of alerts under the single label `Hybrid`. Even when alerts were triggered exclusively by an FSM protocol violation or by an Isolation Forest statistical outlier, they were recorded and grouped generically under `Hybrid`.

### 1.2 Root Cause Discovery
Investigation revealed two contributing root causes:
1. **Simulation Generator Defaulting**: In `backend/app/simulator/generator.py`, synthetic alerts were constructed with `engine="hybrid"` hardcoded across all scenarios, ignoring whether the alert arose from a deterministic FSM state violation or an ML metric spike.
2. **Dashboard Query Aggregation**: The dashboard summary endpoint (`/api/dashboard/summary`) only queried for `hybrid` counts, failing to provide categories for `fsm`, `ml`, or unclassified legacy alerts (`unknown`).
3. **Frontend Pie Chart Assumptions**: The dashboard frontend only expected `data.engine_distribution.hybrid`, rendering a single monochrome slice and hiding other engines.

---

## 2. Solution Architecture

### 2.1 Provenance Attribution Rules
TraceGuard AI Phase 15 establishes strict classification provenance rules across both real and simulated traffic:

| Engine Key | Condition | Description | Severity Range |
|---|---|---|---|
| `fsm` | $S_{FSM} = 1.0 \land S_{ML} < 0.5$ | Deterministic state machine protocol violation (e.g. out-of-order token, unauthorized method). | High to Critical (Min 60%) |
| `ml` | $S_{FSM} = 0.0 \land S_{ML} \ge 0.5$ | Statistical anomaly detected by Isolation Forest (e.g. abnormal payload ratio, burst frequency). | Medium to High |
| `hybrid` | $S_{FSM} = 1.0 \land S_{ML} \ge 0.5$ | Consensus detection where both FSM and ML flagged the event simultaneously. | Critical (80% - 100%) |
| `unknown` | Missing / legacy provenance | Legacy records prior to Phase 15 without provenance data. Displayed honestly without fabricating history. | Variable |

### 2.2 Database Schema & Model Support
The `Alert` model in `backend/app/models/models.py` already supported an `engine = Column(String(50), default="hybrid")` field.
The backend pipeline and simulator were updated to guarantee that every alert generated assigns `engine` strictly according to the rules above.

### 2.3 SQL Aggregation & Time Filtering
In `backend/app/api/dashboard.py`, the `get_dashboard_summary` endpoint supports a `time_range` query parameter (`all`, `24h`, `7d`, `30d`):

```python
# Compute engine distribution with provenance
engine_counts = {"fsm": 0, "ml": 0, "hybrid": 0, "unknown": 0}
engine_rows = db.query(Alert.engine, func.count(Alert.id)).filter(
    Alert.workspace_id == ws_ctx.workspace_id,
    Alert.timestamp >= start_time
).group_by(Alert.engine).all()

for eng, count in engine_rows:
    eng_lower = (eng or "").lower()
    if eng_lower in engine_counts:
        engine_counts[eng_lower] += count
    else:
        engine_counts["unknown"] += count
```

### 2.4 Recharts Multi-Engine Visualization
In `frontend/src/pages/Dashboard.jsx`:
- The donut chart maps distinct cyber-defense color tokens:
  - **FSM Engine**: Cyan (`#06b6d4`)
  - **ML Isolation Forest**: Purple (`#a855f7`)
  - **Hybrid Consensus**: Emerald / Green (`#10b981`)
  - **Unknown / Legacy**: Slate / Gray (`#64748b`)
- Tooltips display exact alert counts, percentage share of total, and engine description.
- Legend displays category labels with respective percentages ($X\%$).
- When no alerts exist in the selected time range, an honest empty state is shown: `"No alert records found for the selected time window"`.

---

## 3. Reconciled Total Verification

To prevent visual inconsistencies, the frontend reconciles chart totals:
$$\text{Total Engine Classifications} = N_{FSM} + N_{ML} + N_{Hybrid} + N_{Unknown}$$
The sum strictly matches the total filtered alert count displayed in the dashboard metrics summary.

---

## 4. Test Verification

1. **Automated Backend Regression**:
   - `test_engine_classification_provenance` in [test_phase15_full_regression.py](file:///c:/Projects/FSM-NIDS/backend/tests/test_phase15_full_regression.py) verifies distinct `fsm`, `ml`, and `hybrid` alerts are persisted and correctly aggregated.
   - `test_dashboard_summary_with_time_range` in [test_network_intelligence.py](file:///c:/Projects/FSM-NIDS/backend/tests/test_network_intelligence.py) validates time filtering.
2. **Interactive Browser Verification**:
   - Verified on live dashboard with time filter toggles (`all`, `24h`, `7d`, `30d`).
