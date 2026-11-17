# TraceGuard AI — Comprehensive Documentation Suite & Academic Monograph

**Repository:** `C:\Projects\FSM-NIDS`  
**Official Repository:** `https://github.com/ojas-mohbansi/TRACEGUARD-AI`  
**Academic Focus:** Theory of Computation, Formal Languages & Automata Theory, Hybrid Network Intrusion Detection  
**Status:** **100% PRODUCTION READY & CONSOLIDATED**  

---

## 1. Executive Summary

**TraceGuard AI** is an academic and enterprise-grade cybersecurity platform that validates network protocol event sequences against a formal **Deterministic Finite Automaton (Complete DFA)** and correlates deterministic state violations with an **Isolation Forest** statistical machine learning model.

### Theoretical Foundation:
$$\mathcal{M} = (Q, \Sigma, \delta, q_0, F)$$
$$|Q| = 9 \text{ States}, \quad |\Sigma| = 13 \text{ Input Symbols}, \quad |Q \times \Sigma| = 117 \text{ Total Transitions}$$
$$q_0 = \text{IDLE}, \quad F = \{ \text{CLOSED} \}, \quad \text{Sink} = \text{TRAP}$$

### Hybrid Consensus Formula:
$$S_h = \max(0.60 \cdot S_{\text{FSM}} + 0.40 \cdot S_{\text{ML}}, \; \mathbb{I}_{\text{FSM}} \cdot 60)$$
*(Guarantees an unbreakable 60% risk floor upon any deterministic protocol violation into $\text{TRAP}$).*

---

## 2. Essential Documentation Catalog

The documentation in `docs/` has been consolidated into **8 essential, comprehensive documents** that cover the entire technical, theoretical, operational, and academic surface of the project:

| Document | Primary Domain | Core Contents & Key Deliverables |
|---|---|---|
| **[01_SYSTEM_ARCHITECTURE.md](file:///C:/Projects/FSM-NIDS/docs/01_SYSTEM_ARCHITECTURE.md)** | System Architecture | End-to-end multi-tier architecture, FastAPI backend, React SPA frontend, Cloudflare Workers website, SQLite/SQLAlchemy schema, multi-tenancy, Local Academic Mode, and packet privacy safeguards. |
| **[02_THEORY_OF_COMPUTATION_AND_AUTOMATA.md](file:///C:/Projects/FSM-NIDS/docs/02_THEORY_OF_COMPUTATION_AND_AUTOMATA.md)** | Automata Theory | Formal 5-tuple specification, complete 117-entry transition matrix, language recognition $L(M)$, absorbing trap proofs, $O(1)$ step complexity proofs, and formal detection proofs against out-of-order attacks. |
| **[03_HYBRID_DETECTION_AND_ML_ENGINE.md](file:///C:/Projects/FSM-NIDS/docs/03_HYBRID_DETECTION_AND_ML_ENGINE.md)** | Hybrid ML Detection | Authoritative hybrid scoring formula, 60% FSM risk floor proof, 11-D feature vector, Isolation Forest calibration ($\tau = 0.55$), 4 detection quadrants, tri-engine attribution, and benchmark corpus validation. |
| **[04_API_CONTRACTS_AND_PROTOCOLS.md](file:///C:/Projects/FSM-NIDS/docs/04_API_CONTRACTS_AND_PROTOCOLS.md)** | API & Protocol Reference | Complete RESTful API contracts (`/auth`, `/fsm`, `/threats`, `/dashboard`, `/network`, `/benchmark`), request/response JSON schemas, and real-time WebSocket telemetry protocol (`/ws/telemetry`). |
| **[05_DEPLOYMENT_OPERATIONS_AND_RUNBOOK.md](file:///C:/Projects/FSM-NIDS/docs/05_DEPLOYMENT_OPERATIONS_AND_RUNBOOK.md)** | Operations & Runbook | Local multi-service startup, Windows Npcap driver setup, 10-step interactive live viva demonstration walkthrough, Cloudflare Workers edge deployment, and CI/CD quality gates. |
| **[06_ACADEMIC_VIVA_AND_MONOGRAPH.md](file:///C:/Projects/FSM-NIDS/docs/06_ACADEMIC_VIVA_AND_MONOGRAPH.md)** | Viva Voce Defense Guide | Complete 60-question oral examination bank across 7 categories with spoken answers and technical justifications, project report summary, author roster, and submission checklist. |
| **[07_PROJECT_HISTORY_AUDIT_AND_BRAND.md](file:///C:/Projects/FSM-NIDS/docs/07_PROJECT_HISTORY_AUDIT_AND_BRAND.md)** | History, Brand & Audits | Chronological engineering evolution across Phases 1–22, official brand identity system, color tokens, typography, release readiness matrix, and final verification sign-off. |
| **[README.md](file:///C:/Projects/FSM-NIDS/docs/README.md)** | Master Gateway | This authoritative gateway index, quickstart instructions, and academic team overview. |

---

## 3. Presentation Guides & Student Author Allocations

Individual speaker rehearsal guides for the authoritative 22-slide Theory of Computation presentation deck are located in the [docs/presentation/](file:///C:/Projects/FSM-NIDS/docs/presentation/) subfolder:

- **Presenter 1: Tanmay** (Slides 1–4) — [presenter_1.md](file:///C:/Projects/FSM-NIDS/docs/presentation/presenter_1.md)
  *Project Overview, Problem Statement, Paradigm Shift & Research Scope.*
- **Presenter 2: Karthik Sai** (Slides 5–9) — [presenter_2.md](file:///C:/Projects/FSM-NIDS/docs/presentation/presenter_2.md)
  *Formal 5-Tuple, State Space Analysis, 13-Symbol Alphabet, Transition Matrix.*
- **Presenter 3: Ojas Mohbansi** (Slides 10–14) — [presenter_3.md](file:///C:/Projects/FSM-NIDS/docs/presentation/presenter_3.md)
  *DFA Equivalence & Proofs, Language Acceptance $L(M)$, Trap Sink Irreversibility.*
- **Presenter 4: Darpan Jain** (Slides 15–18) — [presenter_4.md](file:///C:/Projects/FSM-NIDS/docs/presentation/presenter_4.md)
  *Dual-Engine Pipeline, Isolation Forest ML Calibration, 60% FSM Risk Floor.*
- **Presenter 5: Panda** (Slides 19–22) — [presenter_5.md](file:///C:/Projects/FSM-NIDS/docs/presentation/presenter_5.md)
  *Performance Benchmarks, Live Attack Scenarios, SOC Dashboard, Final Conclusions.*
- **Team Overview** — [PRESENTATION_TEAM_OVERVIEW.md](file:///C:/Projects/FSM-NIDS/docs/presentation/PRESENTATION_TEAM_OVERVIEW.md)

---

## 4. Quickstart: Running TraceGuard AI

Launch the three core development services:

```powershell
# Terminal 1: Backend API Gateway (Port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

# Terminal 2: SaaS Frontend SPA (Port 5174)
bun run --cwd frontend dev

# Terminal 3: Public Academic Portal (Port 5303)
bun run --cwd website dev
```

- **SaaS Application**: `http://localhost:5174/`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Public Academic Website**: `http://localhost:5303/`
- **Workers Local Preview**: `http://127.0.0.1:8787/`
- **Automated Tests**: Run `pytest backend/tests/ -q` (149/149 pass).

---

## 5. Historical Archive

All pre-consolidation intermediate phase reports and audit notes are preserved in [docs/archive/](file:///C:/Projects/FSM-NIDS/docs/archive/) for complete historical continuity and provenance tracking.
