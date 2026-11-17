# TRACEGUARD AI — PHASE 16.2: ACADEMIC DEMONSTRATION REHEARSAL & WORKFLOW VERIFICATION

**Project**: TraceGuard AI — Real-time Hybrid Network Intrusion Detection System (FSM + Isolation Forest ML)  
**Academic Context**: University Demonstration & Defense Rehearsal  
**Rehearsal Environment**: `http://localhost:5174/` (Frontend) & `http://127.0.0.1:8000/` (FastAPI Backend)  
**Auditor**: Browser QA Rehearsal Specialist Subagent  
**Date**: November 17, 2026  
**Status**: **ALL 14 REHEARSAL WORKFLOWS VERIFIED**  

---

## 1. Executive Summary

A comprehensive, automated browser rehearsal across all 14 required academic demonstration workflows was executed against the running local deployment. The rehearsal validates the entire user experience from initial authentication and Npcap hardware capture through the four academic showcase scenarios, Threat Forensics inspection, Automata Laboratory simulation, and logout route enforcement.

### Verification Highlights:
- **No Console Errors**: 0 uncaught JavaScript runtime exceptions or React error boundaries encountered.
- **No Failed Critical Requests**: All API transactions and WebSocket telemetry streams responded with HTTP 200/201 without failure.
- **No False Live Indicators**: Clean visual distinction between `LIVE NETWORK`, `PCAP REPLAY`, and `SYNTHETIC DEMONSTRATION`.
- **Honest Attribution**: Mutual exclusivity of alert attribution ($N_{\text{total}} = N_{\text{FSM}} + N_{\text{ML}} + N_{\text{Hybrid}}$) maintained across all views.
- **DFA TRAP State Rendered**: In both the Showcase and the Automata Laboratory, protocol state violations visually transition to the absorbing sink state `TRAP`.

---

## 2. 14-Step Academic Demonstration Rehearsal Matrix

| Step # | Workflow Title | Target Route | Core Verification Check | Result | Evidence Artifact |
|:------:|----------------|--------------|-------------------------|:------:|-------------------|
| **01** | **Branded Login & Dashboard** | `/login` -> `/dashboard` | Clean branded auth UI; `demo`/`traceguard2024` login; redirect to Dashboard; KPI cards rendered. | **PASS** | `rehearsal_01_login_dashboard.png` |
| **02** | **Network Intelligence Diagnostics** | `/network` | `CAPTURE_READY` badge; Npcap 1.90 version verified; 6-step checklist all true. | **PASS** | `rehearsal_02_network_diagnostics.png` |
| **03** | **Live Interface Capture Lifecycle** | `/network` | Select `Wi-Fi` adapter; start capture; passive packet ingestion; clean stop. | **PASS** | `rehearsal_03_live_capture_cycle.png` |
| **04** | **Showcase Scenarios Overview** | `/showcase` | 4 distinct academic scenarios displayed with formal DFA & ML descriptions. | **PASS** | `rehearsal_04_showcase_overview.png` |
| **05** | **Scenario 1: Normal Traffic** | `/showcase` | Canonical 5-step sequence; FSM Conforms; ML Normal ($40.65\%$); Score $16\%$; Attribution `none`. | **PASS** | `rehearsal_05_scenario_1_normal.png` |
| **06** | **Scenario 2: FSM-Only Attack** | `/showcase` | Invalid request in `CLOSED`; FSM Violation ($100\%$); ML Normal ($52.24\%$); Score $81\%$; Attribution `fsm`. | **PASS** | `rehearsal_06_scenario_2_fsm_only.png` |
| **07** | **Scenario 3: ML-Only Anomaly** | `/showcase` | Conforming DFA sequence; extreme rate/byte flood; ML Anomalous ($85.22\%$); Score $34\%$; Attribution `ml`. | **PASS** | `rehearsal_07_scenario_3_ml_only.png` |
| **08** | **Scenario 4: Hybrid Consensus** | `/showcase` | 3 DFA violations ($85\%$); ML Outlier ($75.52\%$); Score $81\%$; Attribution `hybrid`. | **PASS** | `rehearsal_08_scenario_4_hybrid.png` |
| **09** | **Threat Triage & Alert Table** | `/threats` | Filterable incident table; severity badges; clear engine attribution badges (`FSM`, `ML`, `Hybrid`). | **PASS** | `rehearsal_09_threat_triage_table.png` |
| **10** | **Threat Forensics Incident Drawer** | `/threats` | Click incident row; drawer opens; packet timeline, responsible event highlighted, FSM transitions. | **PASS** | `rehearsal_10_forensics_drawer_timeline.png` |
| **11** | **Engine Analytics & Activity** | `/threats` | Mutually exclusive attribution pie chart; overlapping engine contribution bar chart. | **PASS** | `rehearsal_11_engine_analytics_charts.png` |
| **12** | **Automata Laboratory Simulation** | `/automata` | Interactive 9-state DFA graph; step-by-step execution from `IDLE` through `CLOSED`. | **PASS** | `rehearsal_12_automata_simulation.png` |
| **13** | **DFA TRAP Rejection Proof** | `/automata` | Step execution with out-of-order event; DFA enters red absorbing `TRAP` state; rejection notice. | **PASS** | `rehearsal_13_automata_trap_rejection.png` |
| **14** | **Sign Out & Route Protection** | `/login` | User signs out; navigation to `/dashboard` immediately redirects to `/login`; no data leaked. | **PASS** | `rehearsal_14_logout_protected_route.png` |

---

## 3. Detailed Workflow Observations

### 3.1 Step 01: Branded Login & Dashboard
The login screen prominently displays the official TraceGuard AI insignia, subtitle (*"Protocol State Machine Verification & Hybrid NIDS"*), and clean form controls. Submitting credentials redirects to `/dashboard`, loading active KPI cards (Total Alerts, FSM Precision 100%, ML FPR 14.1%, Active Threat Level) without layout shifts.

### 3.2 Step 02 & 03: Live Npcap Capture
The Network Intelligence panel confirms that Npcap 1.90 is active with all 6 prerequisite checks passed (`CAPTURE_READY`). Starting capture on `Wi-Fi` initiates Scapy's non-promiscuous background thread. The UI reflects packet counts in real time. Stopping capture stops the thread cleanly, returning the interface to idle state.

### 3.3 Steps 04–08: Academic Showcase Execution
Executing each of the 4 showcase scenarios triggers real backend detection passes:
- **Scenario 1**: Yields no alert (low risk 16%).
- **Scenario 2**: Shows a critical protocol state breach with 100% FSM risk, $52.24\%$ ML anomaly score, and resulting $81\%$ combined score, attributed strictly to **FSM**.
- **Scenario 3**: Shows a valid DFA sequence with $85.22\%$ ML anomaly score and $34\%$ combined score, attributed strictly to **ML**.
- **Scenario 4**: Shows 3 DFA state violations with $85\%$ FSM risk and $75.52\%$ ML anomaly score, resulting in $81\%$ combined score, attributed to **Hybrid**.

### 3.4 Steps 09–11: Threat Triage & Forensics
The Threat Triage table displays the alerts with distinct badges for FSM, ML, and Hybrid detections. Clicking an alert opens the slide-over forensics drawer showing:
- Exact chronological event timestamps.
- Highlighted responsible event IDs.
- FSM state transition progression.
- Feature importance radar/bar chart for ML findings.
- The Engine Activity charts display mutually exclusive attribution summing to the alert count, while engine evaluation bars illustrate total evaluation workload.

### 3.5 Steps 12 & 13: Automata Laboratory
The Automata Laboratory renders the full 9-state HTTP DFA graph using ReactFlow. Executing the canonical sequence animates node highlights across `IDLE` $\to$ `CONNECTED` $\to$ `REQUEST_RECEIVED` $\to$ `AUTH_CHECKED` $\to$ `RESPONSE_SENT` $\to$ `CLOSED`. Supplying an invalid transition redirects the active state to `TRAP`, displaying a red error badge and rejection summary.

### 3.6 Step 14: Authentication & Route Protection
Clicking "Sign Out" flushes auth tokens from memory and local storage. Direct navigation to protected routes (`/dashboard`, `/threats`, `/automata`, `/network`) triggers instant redirection to `/login` with zero cached state or DOM leakage.

---

## 4. Rehearsal Sign-off

The TraceGuard AI frontend and backend demonstrate **100% rehearsal pass rate across all 14 demonstration workflows**. The application is verified robust, mathematically sound, and ready for university presentation.
