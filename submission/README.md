# TraceGuard AI: Academic Submission Package

**Course**: Theory of Computation / Formal Languages and Automata Theory  
**Project**: TraceGuard AI — Formal Protocol Automata & Hybrid Intrusion Detection  

---

## 1. Quickstart Guide (Local Windows Execution)

### Prerequisites:
- Python 3.11+
- Node.js 18+ & npm

### Step 1: Run the Backend Test Suite
```powershell
# Navigate to the project root
cd TraceGuard_AI

# Run the 32 automated verification tests
pytest backend/tests/ -v
```
*Expected Result*: 32 passed, 0 failures.

### Step 2: Start the FastAPI Backend Server
```powershell
# Terminal 1:
$env:PYTHONPATH="backend"
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*Backend URL*: `http://localhost:8000` (API docs at `http://localhost:8000/docs`).

### Step 3: Start the React Frontend Server
```powershell
# Terminal 2:
cd frontend
npm install
npm run dev
```
*Frontend URL*: `http://localhost:5173`.

### Step 4: Open the Automata Laboratory
Open your browser to: `http://localhost:5173/automata` to interact with the 9-state Complete DFA visualizer, transition debugger, and 117-cell matrix explorer.

---

## 2. Submission Materials Directory Guide

- **PowerPoint Presentation**: `presentation/TraceGuard_AI_TOC_Presentation.pptx`  
  (14 widescreen slides with complete speaker notes on every slide).
- **Viva Voce Defense Guide**: `docs/VIVA_PREPARATION.md`  
  (60 technical questions and answers with detailed explanations and examiner challenges).
- **Live Demonstration Script**: `docs/FINAL_PRESENTATION_SCRIPT.md`  
  (5–7 minute timed evaluation walkthrough).
- **Academic Project Report**: `docs/PROJECT_REPORT.md`  
  (Comprehensive formal university project report).
- **Formal 5-Tuple Specification**: `docs/FORMAL_AUTOMATON.md`  
  (Mathematical specification $M = (Q, \Sigma, \delta, q_0, F)$).
- **Complete Transition Table**: `docs/TRANSITION_TABLE.md`  
  (117-cell total transition function).
- **Submission Checklist**: `docs/SUBMISSION_CHECKLIST.md`  
  (Full submission inventory and verification evidence).
