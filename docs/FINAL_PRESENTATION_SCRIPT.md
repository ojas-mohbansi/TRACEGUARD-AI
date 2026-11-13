# TraceGuard AI: Live Academic Demonstration Script

**Target Duration**: 5 to 7 Minutes  
**Audience**: Course Evaluators, Faculty Examiners, University Viva Panel  
**Primary Interface**: Browser at `http://localhost:5173/automata`  
**Backend API**: FastAPI running on `http://127.0.0.1:8000`  

---

## Pre-Demonstration Checklist (T-minus 2 Minutes)

Before the professor sits down:
1. Ensure the backend server is running in PowerShell Terminal 1:
   ```powershell
   $env:PYTHONPATH="C:\Projects\FSM-NIDS\backend"
   cd C:\Projects\FSM-NIDS\backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2. Ensure the frontend Vite dev server is running in PowerShell Terminal 2:
   ```powershell
   cd C:\Projects\FSM-NIDS\frontend
   npm run dev
   ```
3. Open Google Chrome or Microsoft Edge to: `http://localhost:5173/automata`.
4. Keep the browser zoomed to 100% or 110% for crisp diagram rendering.

---

## Timed Demonstration Script

### Minute 0:00 – 1:00 | Architecture & The Automata Centerpiece
- **Action**: Open the dashboard at `http://localhost:5173/`. Point out the navigation sidebar and click directly on **Automata Lab** (`/automata`).
- **What to Say**:
  > *"Respected examiners, TraceGuard AI demonstrates the practical application of Theory of Computation concepts to network intrusion detection. Rather than relying on black-box heuristics, we model the protocol as a formal Deterministic Finite Automaton. Here at the Automata Laboratory, you can see the complete 9-state DFA representing the HTTP protocol lifecycle."*
- **Visual Highlight**: Point to the initial state `IDLE` (indicated by $q_0$ and dashed border), accepting state `CLOSED` (indicated by $F$ and gold border), and the explicit `TRAP` state at the bottom.

---

### Minute 1:00 – 2:00 | Mathematical 5-Tuple & Total Transition Completeness
- **Action**: Click on the **5-Tuple Definition** tab at the top of the Automata Lab.
- **What to Say**:
  > *"In classical automata theory, a true DFA requires a total transition function. On this screen, we present the formal 5-tuple: $M = (Q, \Sigma, \delta, q_0, F)$.*  
  > *• $Q$ contains 9 states, including our absorbing dead state TRAP.*  
  > *• $\Sigma$ contains 13 discrete protocol event symbols.*  
  > *• Total completeness is mathematically guaranteed: for all 9 states and all 13 symbols, $\delta(q, \sigma) \in Q$, yielding exactly 117 defined transitions.*  
  > *• $q_0$ is IDLE, and $F$ contains only CLOSED."*
- **Action**: Switch to the **Transition Matrix** tab. Type `CLOSED` into the search box to show that events after connection teardown transition into `TRAP`.

---

### Minute 2:00 – 3:30 | Step-by-Step Execution of Valid Sequence ($w \in L(M)$)
- **Action**: Switch back to the **Interactive Automaton** tab.
- **Action**: Click the preset button: **Canonical Valid Transaction**.  
  Sequence: `CONNECT, REQUEST, AUTH_SUCCESS, RESPONSE_200, CLOSE`
- **Action**: Click **Load & Run**. The execution inspector loads Step 1.
- **Action**: Click **Step** button 4 times, advancing one symbol at a time.
- **What to Say**:
  > *"Now let us execute a canonical HTTP sequence step-by-step. As I click Step, the active state updates in real time on the ReactFlow canvas:*  
  > *• Step 1: $\delta(\text{IDLE}, \text{CONNECT}) = \text{CONNECTED}$.*  
  > *• Step 2: $\delta(\text{CONNECTED}, \text{REQUEST}) = \text{REQUEST\_RECEIVED}$.*  
  > *• Step 3: $\delta(\text{REQUEST\_RECEIVED}, \text{AUTH\_SUCCESS}) = \text{AUTH\_CHECKED}$.*  
  > *• Step 4: $\delta(\text{AUTH\_CHECKED}, \text{RESPONSE\_200}) = \text{RESPONSE\_SENT}$.*  
  > *• Step 5: $\delta(\text{RESPONSE\_SENT}, \text{CLOSE}) = \text{CLOSED}$.*  
  > *Notice the final verdict: ACCEPTED. Because every transition was valid and the terminal state belongs to $F$, the string belongs to the language $L(M)$."*

---

### Minute 3:30 – 4:45 | Immediate Rejection & The Absorbing TRAP State
- **Action**: Click the preset button: **Premature Response Violation**.  
  Sequence: `CONNECT, RESPONSE_200, REQUEST, CLOSE`
- **Action**: Click **Load & Run**.
- **Action**: Click **Step** to advance to Step 2.
- **Expected Output**: The active node jumps down to `TRAP`, glowing in red alert styling. The audit log flags `VIOLATION / REJECTED`.
- **What to Say**:
  > *"Here an attacker attempts an out-of-order exploit, transmitting a response status before the client ever sent a request.*  
  > *At Step 2, state is CONNECTED and symbol is RESPONSE_200. In our complete DFA, $\delta(\text{CONNECTED}, \text{RESPONSE\_200}) = \text{TRAP}$.*  
  > *Notice that as I step forward through the remaining symbols (REQUEST, CLOSE), the automaton self-loops on TRAP. It is an absorbing sink state from which an attacker can never escape. The string is decisively REJECTED with an exact causal explanation."*

---

### Minute 4:45 – 5:45 | Incomplete Valid Prefix vs. Acceptance
- **Action**: Click the preset button: **Valid Incomplete Prefix**.  
  Sequence: `CONNECT, REQUEST, AUTH_SUCCESS`
- **Action**: Click **Load & Run** and step through to the end.
- **Expected Output**: Verdict shows `INCOMPLETE_VALID` in amber/yellow styling.
- **What to Say**:
  > *"A critical theoretical distinction we emphasize is between valid transitions and language acceptance. Here, all 3 transitions are completely legal according to protocol rules. However, execution halted in AUTH_CHECKED, which is not in $F$.*  
  > *The system correctly classifies this as INCOMPLETE_VALID. It is a legitimate in-progress session, not an attack. An empty sequence $\epsilon$ is treated identically."*

---

### Minute 5:45 – 6:45 | Multi-Engine Comparison & Hybrid Risk Floor
- **Action**: Navigate to **Detection Lab** in the left sidebar (`/lab`).
- **What to Say**:
  > *"To evaluate the boundaries of automata theory, we built a comparative triad:*  
  > *• The Deterministic FSM catches structural sequence violations in $\mathcal{O}(1)$ step time with zero false positives.*  
  > *• The Isolation Forest ML extracts 15 statistical session features (rates, durations, variances) to detect volumetric floods that follow legal transitions.*  
  > *• The Hybrid Arbiter combines both: $\text{Score} = 0.6 \cdot \text{FSM} + 0.4 \cdot \text{ML}$.*  
  > *Crucially, if any FSM violation occurs, a mathematical risk floor of 60 is enforced, guaranteeing that proven structural violations can never be dismissed by a statistical model."*

---

### Minute 6:45 – 7:00 | Conclusion & Handoff
- **Action**: Return to the **Automata Lab** or click **Presentation Mode** in the top bar.
- **What to Say**:
  > *"In conclusion, TraceGuard AI proves that Theory of Computation principles provide mathematical guarantees of safety that machine learning cannot achieve alone. The project is verified by 32 automated tests with 100% pass rate. Thank you, and I look forward to your questions."*

---

## Contingency & Fallback Plans

| Scenario | Immediate Fix / What to Say |
|:---|:---|
| **Backend connection drops** | Keep Terminal 1 visible. Restart with: `$env:PYTHONPATH="C:\Projects\FSM-NIDS\backend"; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`. Say: *"Uvicorn process reloaded; our stateless architecture restores all sessions immediately."* |
| **Examiner asks for custom sequence** | Type into the input box on `/automata`: `CONNECT, REQUEST, AUTH_FAILURE, RESPONSE_200, CLOSE`. Click **Load & Run**. Show that attempting to emit 200 OK after `AUTH_FAILURE` immediately enters `TRAP`. |
| **Examiner asks to see tests** | Open PowerShell and run: `pytest backend/tests/ -v`. Point to `test_complete_dfa_formal_specification` and all 32 passing tests. |
