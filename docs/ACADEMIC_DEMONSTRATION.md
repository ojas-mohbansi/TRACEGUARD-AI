# University Academic Demonstration Guide

This guide is designed for university course evaluators, professors, and students to conduct a live evaluation of TraceGuard AI's Theory of Computation capabilities.

---

## 10-Step Interactive Evaluation Script

### Step 1: Theoretical Overview & Formal Model
- **Action**: Open the **Automata Laboratory** tab.
- **Concept**: Present the formal 5-tuple: $\mathcal{M} = (Q, \Sigma, \delta, q_0, F)$.
- **Demonstration**:
  - Show $|Q| = 8$ states.
  - Show $|\Sigma| = 13$ alphabet symbols.
  - Point out initial state $q_0 = \text{IDLE}$ and accepting state set $F = \{\text{CLOSED}\}$.

### Step 2: Transition Function ($\delta$) Inspection
- **Action**: Switch to the **Transition Table & δ Matrix** tab in Automata Laboratory.
- **Concept**: Explain that the table has $|Q| \times |\Sigma| = 104$ coordinate cells, with exactly 15 defined valid transitions and 89 undefined $\emptyset$ trap cells.
- **Demonstration**: Filter by state `AUTH_CHECKED` to show valid outgoing transitions: `RESPONSE_200`, `RESPONSE_301`, `RESPONSE_500`.

### Step 3: Interactive Step-by-Step Execution of Valid String
- **Action**: In the **Interactive Automaton** panel, select the preset:
  `CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE`
- **Execution**: Click **Step $\to$** one event at a time.
- **Observation**:
  - Watch the active node highlight move from $\text{IDLE} \to \text{CONNECTED} \to \text{REQUEST\_RECEIVED} \to \text{AUTH\_CHECKED} \to \text{RESPONSE\_SENT} \to \text{CLOSED}$.
  - Note the Delta transition lookup: $\delta(\text{IDLE}, \text{CONNECT}) = \text{CONNECTED}$.
  - On reaching `CLOSE`, the final state is `CLOSED` $\in F$.
  - **Verdict**: `ACCEPTED` ($w \in L(\mathcal{M})$).

### Step 4: Step-by-Step Execution of Invalid String (Rejection)
- **Action**: Select the preset:
  `CONNECT, RESPONSE_200, REQUEST, CLOSE`
- **Execution**: Click **Step $\to$** twice.
- **Observation**:
  - At Step 2 (`RESPONSE_200`), state is `CONNECTED`.
  - Lookup $\delta(\text{CONNECTED}, \text{RESPONSE\_200}) = \emptyset$ (Undefined).
  - Node turns red. Audit log displays exact rejection reason:
    *"No valid transition defined in δ for state 'CONNECTED' with symbol 'RESPONSE_200'. Allowed symbols: [REQUEST, TIMEOUT]."*
  - **Verdict**: `REJECTED`.

### Step 5: Valid Incomplete Prefix vs. Acceptance
- **Action**: Enter the sequence:
  `CONNECT, REQUEST, AUTH_SUCCESS`
- **Execution**: Execute all 3 steps.
- **Observation**:
  - All transitions executed were completely valid according to $\delta$.
  - However, final state is $\text{AUTH\_CHECKED} \notin F$.
  - **Verdict**: `INCOMPLETE_VALID`. Demonstrates the formal distinction between language acceptance and transition validity.

### Step 6: Edge Case Testing Suite
- **Action**: Switch to the **Automata Testing Lab** tab.
- **Demonstration**: Run the automated edge-case test battery:
  - Empty string $\epsilon$ $\implies$ Incomplete ($q_0 \notin F$).
  - Valid keep-alive loop $\implies$ Cyclic transition validation.
  - Invalid first symbol $\implies$ Immediate rejection at Step 1.
  - Authentication bypass $\implies$ Invariant protection verified.

### Step 7: Language Recognition & Regular Languages
- **Action**: Switch to the **Regular Languages** tab.
- **Concept**: Explain how $\mathcal{M}$ recognizes a regular language denoted by Kleene star expression.
- **Demonstration**: Inspect prefix processing trees and string acceptance criteria.

### Step 8: Multi-Engine Comparison (FSM vs. ML vs. Hybrid)
- **Action**: Open the **Engine Comparison** tab.
- **Execution**: Feed the same anomalous trace (`CONNECT, RESPONSE_200, CLOSE`) to all three engines.
- **Observation**:
  - **FSM**: 100/100 risk, flags exact invalid transition $\delta(\text{CONNECTED}, \text{RESPONSE\_200})$.
  - **ML**: Flags statistical anomaly score based on path lengths in Isolation Forest.
  - **Hybrid**: Synthesizes scores, enforcing the mandatory 85+ risk floor due to FSM violation.

### Step 9: Live Traffic Simulation & Real-Time Automata
- **Action**: Switch to **Live Monitor** or **Live Traffic Simulator**.
- **Execution**: Start simulation in "Anomalous Traffic" mode.
- **Observation**: Live WebSocket feed streams synthetic sessions, displaying real-time FSM invariant checking against continuous network traffic.

### Step 10: Presentation Mode
- **Action**: Click the **Presentation Mode** button in the top navigation bar.
- **Demonstration**: A fullscreen guided slideshow walking through slides 1 through 10 with embedded live interactive execution widgets.
