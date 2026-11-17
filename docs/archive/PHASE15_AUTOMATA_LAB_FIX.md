# Phase 15: Automata Laboratory Simulation Lifecycle Architecture & Fix

## 1. Executive Summary

The Automata Laboratory allows cybersecurity researchers and students to visualize the state transitions of the formal 9-state HTTP Deterministic Finite Automaton (DFA) in real time. Prior to Phase 15, when executing multi-step simulations, the interface would advance to Stage 2 and permanently stall, failing to process the remaining sequence tokens or produce the final acceptance/rejection verdict.

Phase 15 identifies and resolves the root cause within the simulation lifecycle, restores continuous execution across arbitrary-length sequences, introduces full playback controls (play/pause, step forward, step backward, reset, variable playback speed), and preserves the academic formal model intact.

---

## 2. Formal Automaton Specification

The formal model is defined over the 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$:

### 2.1 State Space $Q$ ($|Q| = 9$)
- $q_0 = \text{IDLE}$ (Initial starting state)
- $q_1 = \text{CONNECTED}$ (TCP handshake established)
- $q_2 = \text{REQUEST\_RECEIVED}$ (HTTP request header parsed)
- $q_3 = \text{AUTH\_CHECKED}$ (Authentication credentials validated)
- $q_4 = \text{AUTH\_FAILED}$ (Unauthorized access attempted)
- $q_5 = \text{RESPONSE\_SENT}$ (HTTP response generated and dispatched)
- $q_6 = \text{ERROR}$ (Server or protocol recovery state)
- $q_7 = \text{CLOSED}$ (Accepting final state; session cleanly torn down)
- $q_8 = \text{TRAP}$ (Absorbing dead state; unrecoverable protocol violation)

### 2.2 Input Alphabet $\Sigma$ ($|\Sigma| = 13$)
$$\Sigma = \{ \text{CONNECT}, \text{REQUEST}, \text{AUTH\_SUCCESS}, \text{AUTH\_FAILURE}, \text{RESPONSE\_200}, \text{RESPONSE\_301}, \text{RESPONSE\_401}, \text{RESPONSE\_403}, \text{RESPONSE\_500}, \text{CLOSE}, \text{TIMEOUT}, \text{MALFORMED}, \text{ERROR\_RESPONSE} \}$$

### 2.3 Acceptance & Invariants
- Total transition matrix size: $|\delta| = 9 \times 13 = 117$ entries.
- Accepting set: $F = \{ \text{CLOSED} \}$.
- Dead state invariant: $\forall \sigma \in \Sigma, \delta(\text{TRAP}, \sigma) = \text{TRAP}$ (absorbing).

---

## 3. Root Cause Analysis: The Stage 2 Stall

### 3.1 Flow Breakdown
Tracing the execution flow revealed:
1. When the user initiated a simulation, the frontend component called `/api/protocols/http/step-execute` with the full sequence of events.
2. The backend returned the full transition path containing all $N$ steps:
   - Step 1: `IDLE --CONNECT--> CONNECTED`
   - Step 2: `CONNECTED --REQUEST--> REQUEST_RECEIVED`
   - Step 3: `REQUEST_RECEIVED --AUTH_SUCCESS--> AUTH_CHECKED`
   - Step 4: `AUTH_CHECKED --RESPONSE_200--> RESPONSE_SENT`
   - Step 5: `RESPONSE_SENT --CLOSE--> CLOSED`
3. In `frontend/src/pages/AutomataLab.jsx`, the animation timer was implemented with a fixed `setTimeout` loop that relied on a stale closure over the React state variable `currentStepIndex`.
4. When `currentStepIndex` incremented from `0` to `1` (displaying Stage 2), a re-render occurred that triggered an effect cleanup cancelling the active timer. The next timeout callback was scheduled with the stale initial index, causing a conditional guard `if (nextIndex >= 2 && !isManual)` to erroneously evaluate to true and break the timer loop.

---

## 4. Implementation: Resilient Simulation Engine

### 4.1 Step Progression Architecture
The simulation state machine in `AutomataLab.jsx` was re-engineered using React `useRef` for timing coordinates, ensuring immutability across re-renders:

```javascript
// Step progression loop driven by ref state
const advanceStep = useCallback(() => {
  setCurrentStepIndex(prev => {
    if (prev < stepsRef.current.length) {
      const next = prev + 1;
      if (next === stepsRef.current.length) {
        setIsPlaying(false);
      }
      return next;
    }
    setIsPlaying(false);
    return prev;
  });
}, []);

useEffect(() => {
  if (!isPlaying) return;
  const intervalMs = Math.round(1000 / playbackSpeed);
  const timer = setInterval(advanceStep, intervalMs);
  return () => clearInterval(timer);
}, [isPlaying, playbackSpeed, advanceStep]);
```

### 4.2 Playback Control Suite
The interface provides complete manual and automated simulation controls:
- **Play / Pause**: Start automated playback or pause mid-stream at any stage.
- **Step Forward ($+1$)**: Manually advance by one symbol.
- **Step Backward ($-1$)**: Rewind to inspect preceding state transitions.
- **Reset**: Return to Stage 0 (`IDLE` state, full input queue intact).
- **Speed Selector**: Multipliers of `0.5x` (2000ms), `1.0x` (1000ms), and `2.0x` (500ms).

### 4.3 Visual Feedback & State Representation
1. **Interactive DFA Graph Canvas**:
   - Active state node glows with cyan accent border and pulsating halo.
   - Active transition edge illuminates with animated dashed directional stroke.
   - TRAP state highlights in red upon violation.
   - CLOSED state highlights in green upon valid acceptance.
2. **Stream Token Pill Array**:
   - **Consumed Tokens**: Grayed out with checkmark badge.
   - **Current Token**: Pulsing cyan border indicating active evaluation.
   - **Remaining Tokens**: Outlined queue waiting to be consumed.
3. **Verdict Banner**:
   - Displays real-time verdict once the stream is exhausted or TRAP is entered:
     - `SEQUENCE ACCEPTED (HTTP Protocol Compliant)`: Final state $\in \{ \text{CLOSED} \}$.
     - `SEQUENCE REJECTED (FSM Protocol Violation)`: Current state $= \text{TRAP}$.
     - `INCOMPLETE SEQUENCE (Valid Prefix)`: Exhausted stream, non-accepting state $\notin \{ \text{TRAP}, \text{CLOSED} \}$.

---

## 5. Formal Verification & Regression Test Matrix

The complete test suite in `backend/tests/test_phase15_full_regression.py` validates:
1. `test_automata_canonical_5_step_sequence`: Advances through Stages 1, 2, 3, 4, 5 to `CLOSED` (PASSED).
2. `test_automata_pipelined_cyclic_8_step_sequence`: Pipelined request cycles (PASSED).
3. `test_automata_valid_incomplete_prefix`: Partial sequence halting gracefully before close (PASSED).
4. `test_automata_out_of_order_violation_rejection`: Unordered symbols immediately entering `TRAP` (PASSED).
5. `test_automata_empty_sequence`: Gracefully handles empty event lists (PASSED).
