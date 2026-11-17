# TraceGuard AI — Deployment, Operations & Academic Runbook

**Document:** `05_DEPLOYMENT_OPERATIONS_AND_RUNBOOK.md`  
**Classification:** Operational Runbook, Demonstration Guide & Infrastructure Reference  
**Version:** 2.0.0 (Authoritative)  
**Repository:** `C:\Projects\FSM-NIDS`  

---

## 1. System Requirements & Prerequisites

| Component | Minimum Specification | Recommended Specification |
|---|---|---|
| **Operating System** | Windows 10/11 x64, Ubuntu 22.04 LTS, macOS Sonoma | Windows 11 x64 (Native Npcap Support) |
| **Node.js Runtime** | Node.js v18.0.0+ / Bun 1.1+ | Bun 1.2+ (Ultra-fast package execution) |
| **Python Runtime** | Python 3.10+ | Python 3.11.x (CPython 64-bit) |
| **Packet Capture Driver** | Optional for simulation / Required for live NIC sniffing | **Npcap 1.79+** (Installed in WinPcap API-compatible mode) |
| **RAM & CPU** | 4 GB RAM, 2 vCPU cores | 8 GB RAM, 4 vCPU cores |

---

## 2. Local Environment Setup & Startup Sequence

To run the complete TraceGuard AI platform locally, launch the services in separate terminals:

```powershell
# 1. Clone repository and navigate to root
cd C:\Projects\FSM-NIDS

# 2. Setup Python Virtual Environment and Backend Dependencies
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt

# 3. Start SaaS FastAPI Backend (Port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload

# 4. In a new terminal: Install Frontend dependencies and start SaaS SPA (Port 5174)
bun install --cwd frontend
bun run --cwd frontend dev

# 5. In a new terminal: Start Public Academic Website (Port 5303)
bun install --cwd website
bun run --cwd website dev

# 6. In a new terminal: Start Cloudflare Workers Local Preview (Port 8787)
bun run --cwd website wrangler dev --port 8787 --ip 127.0.0.1
```

### 2.1 Verifying Active Local Ports
```powershell
# Verify that all 4 daemons are listening
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 # SaaS Backend API
Test-NetConnection -ComputerName 127.0.0.1 -Port 5174 # SaaS Frontend UI
Test-NetConnection -ComputerName 127.0.0.1 -Port 5303 # Website Dev
Test-NetConnection -ComputerName 127.0.0.1 -Port 8787 # Cloudflare Workers Preview
```

---

## 3. Windows Npcap Driver Diagnostics

When utilizing passive live interface monitoring on Windows:
1. **Download Npcap**: Obtain the official installer from [npcap.com](https://npcap.com).
2. **Installation Invariant**: During setup, ensure **"Install Npcap in WinPcap API-compatible Mode"** is checked.
3. **Loopback Adapter**: Enable the **"Support loopback traffic (Npcap Loopback Adapter)"** option.
4. **Verifying Driver in PowerShell**:
   ```powershell
   Get-Service -Name npcap
   # Expected Status: Running
   ```
5. **Graceful Fallback**: If Npcap is not detected or permissions are restricted, TraceGuard AI automatically falls back to the internal event generator (`AcademicBenchmarkGenerator`) without crashing or degrading UI features.

---

## 4. 10-Step Interactive University Demonstration Script

Follow this step-by-step walkthrough during viva voce or live faculty evaluation:

| Step | Action & Navigation | Concept Demonstrated | Evaluator Observation |
|:---:|---|---|---|
| **01** | Open `http://localhost:5174/` | **SecOps Dashboard** | KPI overview, active session counters, and live tri-engine threat distribution. |
| **02** | Click **Automata Lab** in sidebar | **Formal DFA State Space** | Interactive React Flow canvas rendering the 9 states, 13 symbols, and 117 transitions. |
| **03** | Click **"Load Canonical Trace"** | **Compliant Protocol Run** | Sequence `CONNECT -> REQUEST -> RESP_200 -> CLOSE`. Canvas animates transitions to `CLOSED` (Accepted). |
| **04** | Click **"Inject Out-of-Order Attack"** | **Hostile Protocol Trap** | Sequence `CONNECT -> RESP_200`. Automaton instantly transitions to `TRAP`. |
| **05** | Step forward through tokens | **Trap Sink Invariant** | Additional symbols keep the state pinned in `TRAP`. Demonstrates $\delta(\text{TRAP}, \sigma) = \text{TRAP}$. |
| **06** | Navigate to **Detection Lab** | **Hybrid Scoring Engine** | Slide the ML Score and FSM Violation toggles. Observe the 60% FSM risk floor in real time. |
| **07** | Open **Threats & Forensics** | **Forensic Investigation** | Click on any flagged session. Forensic drawer slides out showing exact timestamped symbol history. |
| **08** | Click **"Run Academic Benchmark"** | **Corpus Validation** | Runs 120-session benchmark. Confirms 100% FSM accuracy and 98.8% hybrid recall. |
| **09** | Open **Live Monitor** tab | **Real-Time Packet Stream** | View live packet telemetry streaming via WebSocket at `<50ms` latency. |
| **10** | Press `P` key or click **"Presentation"** | **22-Slide Monograph Mode** | 22-slide editorial presentation mode with full presenter speaking notes mapped to team members. |

---

## 5. Cloudflare Workers Edge Deployment

The public project website (`website/`) is engineered for production deployment on **Cloudflare Workers**.

### 5.1 Deployment Configuration (`wrangler.jsonc`)
```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "traceguard-ai",
  "main": "dist/traceguard_ai/index.js",
  "compatibility_date": "2024-09-23",
  "compatibility_flags": ["nodejs_compat"],
  "assets": {
    "directory": "dist/client",
    "binding": "ASSETS",
    "html_handling": "auto-trailing-slash",
    "not_found_handling": "single-page-application"
  }
}
```

### 5.2 Build & Deployment Commands
```bash
# Typecheck TypeScript source
bun run --cwd website typecheck

# Build both Worker bundle and static client SPA
bun run --cwd website build

# Run local deployment dry-run (verifies assets & bindings)
bun run --cwd website wrangler deploy --dry-run

# Production Deploy (requires CLOUDFLARE_API_TOKEN)
bun run --cwd website wrangler deploy
```

---

## 6. Continuous Integration & Quality Gates (`.github/workflows/ci.yml`)

The repository enforces automated CI testing on all branches:
1. **Python Quality Gate**: Runs `pytest backend/tests/ -q` (149/149 test assertions).
2. **Frontend Quality Gate**: Executes `bun run --cwd frontend build` to verify zero build warnings or chunk errors.
3. **Website Quality Gate**: Executes `bun run --cwd website typecheck`, `bun run --cwd website build`, and `bun run --cwd website seo:check`.
