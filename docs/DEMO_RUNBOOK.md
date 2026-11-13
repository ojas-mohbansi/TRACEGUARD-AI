# TraceGuard AI: Academic Demonstration Runbook

This runbook provides reproducible Windows PowerShell commands for instructors, professors, and students to run and evaluate TraceGuard AI locally.

---

## 1. Prerequisites & Environment Activation

```powershell
# Navigate to the project root
cd C:\Projects\FSM-NIDS

# Run test suite to verify formal automata and engines
pytest backend/tests/ -v
```
**Expected Result**: `32 passed, 0 failures` (100% test pass rate).

---

## 2. Starting the Backend Server

```powershell
# In PowerShell Terminal 1:
$env:PYTHONPATH="C:\Projects\FSM-NIDS\backend"
cd C:\Projects\FSM-NIDS\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
**Expected Result**: Uvicorn running on `http://0.0.0.0:8000`.

---

## 3. Starting the Frontend Server

```powershell
# In PowerShell Terminal 2:
cd C:\Projects\FSM-NIDS\frontend
npm run dev
```
**Expected Result**: Vite development server running on `http://localhost:5173`.

---

## 4. Live Demonstration Sequence

### Step 1: Open the Automata Laboratory
- Navigate to `http://localhost:5173/automata` in your browser.
- Verify that **Automata Laboratory** loads with the 9-state formal DFA, including `q0` (IDLE), accepting state `F` (CLOSED), and the dead state `TRAP`.

### Step 2: Formal 5-Tuple Verification
- Click the **5-Tuple Definition** tab.
- Inspect the mathematical 5-tuple:
  $$M = (Q, \Sigma, \delta, q_0, F)$$
  where $|Q| = 9$, $|\Sigma| = 13$, $q_0 = \text{IDLE}$, and $F = \{\text{CLOSED}\}$.

### Step 3: Complete Transition Matrix Inspection
- Click the **Transition Matrix** tab.
- Verify the total matrix of $9 \times 13 = 117$ entries.
- Observe that all 13 cells for `TRAP` self-loop on `TRAP`.
- Filter by `CLOSED` and observe that unexpected events after closure transition to `TRAP`.

### Step 4: Step-by-Step Execution of Valid String ($w \in L(M)$)
- Return to **Interactive Automaton**.
- Select preset: `Canonical Valid Transaction`.
- Click **Load & Run**, then use **Step** to advance through:
  `CONNECT` $\to$ `REQUEST` $\to$ `AUTH_SUCCESS` $\to$ `RESPONSE_200` $\to$ `CLOSE`.
- **Expected Result**: Node highlights move across the canvas, terminating in state `CLOSED`.
- **Verdict**: `ACCEPTED` ($w \in L(M)$).

### Step 5: Step-by-Step Execution of Invalid String (Rejection)
- Select preset: `Premature Response Violation` (`CONNECT, RESPONSE_200, REQUEST, CLOSE`).
- Click **Load & Run** and advance to Step 2.
- **Expected Result**: Step 2 evaluates $\delta(\text{CONNECTED}, \text{RESPONSE\_200}) = \text{TRAP}$. Node transitions to `TRAP`, glowing red.
- **Verdict**: `REJECTED`.

### Step 6: Valid Incomplete Prefix
- Select preset: `Valid Incomplete Prefix` (`CONNECT, REQUEST, AUTH_SUCCESS`).
- Click **Load & Run** and advance through all 3 steps.
- **Expected Result**: All 3 transitions are valid ($\delta$ succeeds), but the final state is `AUTH_CHECKED` $\notin F$.
- **Verdict**: `INCOMPLETE_VALID`.

### Step 7: Launch University Presentation Mode
- Click the **Presentation Mode** button in the top navigation bar.
- Walk through the 10 guided slides with embedded interactive execution widgets.
