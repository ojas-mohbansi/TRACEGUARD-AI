# TraceGuard AI — Documentation Suite

Welcome to the comprehensive technical, theoretical, and operational documentation suite for **TraceGuard AI** — a high-performance, mathematically rigorous Network Protocol Finite State Machine (FSM) Verification and Hybrid Machine Learning Intrusion Detection System.

This directory contains the complete theoretical proofs, architectural blueprints, deployment guides, examiner viva preparation registers, presentation guides, and historical phase artifacts.

---

## 1. Documentation Map & Directory Tree

```text
docs/
├── README.md                            # You are here: Documentation suite overview & navigation guide
├── DOCUMENTATION_INDEX.md               # Master catalog, metadata index, and cross-reference matrix
├── REPOSITORY_CLEANUP_REPORT.md         # Safe cleanup audit, archival rationale, and preservation sign-off
│
├── [Academic & Theoretical Foundations]
│   ├── FORMAL_AUTOMATON.md              # Mathematical specification: M = (Q, Σ, δ, q0, F), decidability, proofs
│   ├── TRANSITION_TABLE.md              # Exhaustive 117-cell deterministic transition matrix (9 states × 13 symbols)
│   ├── TOC_THEORY.md                    # Regular languages, Chomsky Hierarchy, Pumping Lemma, Trap absorbing state
│   ├── ALGORITHM_EXPLANATION.md         # FSM verification, Isolation Forest ML, and hybrid consensus logic
│   └── VIVA_PREPARATION.md              # 60 viva voce defense questions, mathematical derivations & proofs
│
├── [System Architecture & Engineering]
│   ├── ARCHITECTURE.md                  # High-level component topology, packet ingestion, and dataflow
│   ├── API_CONTRACTS.md                 # REST API endpoints, schemas, and WebSocket telemetry contracts
│   ├── DATA_SCHEMA.md                   # Database models, event telemetry schemas, and relational entities
│   ├── SECURITY_MODEL.md                # Threat model, token authentication, capture privacy, and tenant isolation
│   ├── CI_CD.md                         # Continuous integration, automated test runners, and linting
│   ├── DEPLOYMENT.md                    # Docker, local development, and enterprise deployment topologies
│   ├── SAAS_ARCHITECTURE.md             # Multi-tenant scaling, cloud telemetry ingestion, and worker queues
│   ├── SAAS_ROADMAP.md                  # Future roadmap for enterprise cloud deployment
│   └── BRAND_SYSTEM.md                  # Visual identity tokens, typography, dark/light themes, and CSS mapping
│
├── [Demonstrations & Operations]
│   ├── ACADEMIC_DEMONSTRATION.md        # Step-by-step evaluator demonstration walkthrough
│   ├── DEMO_RUNBOOK.md                  # Quick-start operator guide for running local demo workflows
│   ├── FINAL_PRESENTATION_SCRIPT.md     # Timed live web demonstration script for browser showcase
│   ├── PROJECT_REPORT.md                # Comprehensive university assignment project report
│   ├── RELEASE_READINESS.md             # Production readiness checklist, benchmark criteria & sign-off
│   ├── GITHUB_RELEASE_READINESS.md      # GitHub repository submission & packaging guide
│   ├── FINAL_RELEASE_VERIFICATION.md    # Multi-agent verification logs and test pass guarantees
│   ├── FINAL_SUBMISSION_MANIFEST.md     # Official project submission deliverables manifest
│   ├── SUBMISSION_CHECKLIST.md          # Comprehensive submission criteria audit
│   ├── IMPLEMENTATION_LOG.md            # Chronological engineering log across all phases
│   └── KNOWN_LIMITATIONS.md             # Formal automata boundaries, protocol scope & packet limitations
│
├── [Benchmark & Analytics (Phase 17)]
│   ├── PHASE17_BENCHMARK_METHODOLOGY.md # Evaluation methodology, synthetic attack suites, and baseline metrics
│   ├── PHASE17_ENGINE_ANALYTICS.md      # Analytical throughput, latency, and false positive metrics
│   ├── PHASE17_FINAL_REPORT.md          # Phase 17 benchmark and local academic mode completion report
│   ├── PHASE17_FSM_DETECTION_ANALYSIS.md# In-depth analysis of FSM vs ML detection rates across scenarios
│   └── PHASE17_LOCAL_ACADEMIC_MODE.md   # Deterministic local academic evaluation mode specification
│
├── presentation/                        # Presenter guides & team oral defense coordination
│   ├── PRESENTATION_TEAM_OVERVIEW.md    # Presenter team assignments, speaking order, time limits & handoffs
│   ├── presenter_1.md                   # Presenter 1: Intro, Problem Statement & Scope (Slides 1-3, 2.5 min)
│   ├── presenter_2.md                   # Presenter 2: Formal HTTP DFA, 5-Tuple, Transitions & TRAP (Slides 4-8, 3.5 min)
│   ├── presenter_3.md                   # Presenter 3: ML Isolation Forest, Consensus Formula & Benchmark (Slides 9-11, 2.5 min)
│   ├── presenter_4.md                   # Presenter 4: Architecture, Pipeline & Threats Forensics (Slide 12, 2.5 min)
│   └── presenter_5.md                   # Presenter 5: Live Workflow, Evidence, Limitations & Defense Q&A (Slides 13-14, 2.5 min)
│
└── archive/                             # Historical milestone reports & earlier phase audits
    ├── BRAND_REBRAND_*.md               # Phase 12 brand rebrand audits, QA reports, and screenshot indices (6 files)
    ├── PHASE14_*.md                     # Phase 14 application inventory, defect register, coverage & signoff (9 files)
    ├── PHASE15_*.md                     # Phase 15 auth, navigation, threat forensics, and network architecture (6 files)
    └── PHASE16_*.md                     # Phase 16 evidence, ML calibration, privacy, FSM proofs & diagnostics (15 files)
```

---

## 2. Reading Roadmap by Role

### A. For University Evaluators & Theory of Computation Examiners
If evaluating mathematical rigor, formal language properties, and academic depth:
1. Start with [`FORMAL_AUTOMATON.md`](FORMAL_AUTOMATON.md) for the 5-tuple definition $\mathcal{M} = (Q, \Sigma, \delta, q_0, F)$, state specifications, and decidability proofs.
2. Review [`TRANSITION_TABLE.md`](TRANSITION_TABLE.md) for the complete $9 \times 13 = 117$ transition matrix showing the absorbing $\text{TRAP}$ state behavior.
3. Consult [`TOC_THEORY.md`](TOC_THEORY.md) for regular language classification, Chomsky hierarchy placement, and Pumping Lemma derivations.
4. Read [`ALGORITHM_EXPLANATION.md`](ALGORITHM_EXPLANATION.md) for the hybrid consensus formula $S_h = 0.6 \cdot S_{FSM} + 0.4 \cdot S_{ML}$ and mathematical threshold guarantees.
5. Review [`VIVA_PREPARATION.md`](VIVA_PREPARATION.md) for the 60-question viva defense register.

### B. For Software Engineers & System Architects
If reviewing codebase structure, APIs, models, and deployment:
1. Start with [`ARCHITECTURE.md`](ARCHITECTURE.md) to understand the FastAPI backend, asyncio pipeline, and React frontend.
2. Review [`API_CONTRACTS.md`](API_CONTRACTS.md) and [`DATA_SCHEMA.md`](DATA_SCHEMA.md) for data exchange contracts.
3. Review [`SECURITY_MODEL.md`](SECURITY_MODEL.md) for cryptographic tokens, packet privacy, and tenant isolation.
4. Consult [`DEPLOYMENT.md`](DEPLOYMENT.md) and [`CI_CD.md`](CI_CD.md) for development workflows and Docker containers.

### C. For Presentation Team & Oral Defense Speakers
If rehearsing the defense presentation:
1. Review [`presentation/PRESENTATION_TEAM_OVERVIEW.md`](presentation/PRESENTATION_TEAM_OVERVIEW.md) for master speaker allocations, timing budgets, and handoff protocols.
2. Read your individual presenter script in [`presentation/`](presentation/):
   - [`presenter_1.md`](presentation/presenter_1.md) (Slides 1-3)
   - [`presenter_2.md`](presentation/presenter_2.md) (Slides 4-8)
   - [`presenter_3.md`](presentation/presenter_3.md) (Slides 9-11)
   - [`presenter_4.md`](presentation/presenter_4.md) (Slide 12)
   - [`presenter_5.md`](presentation/presenter_5.md) (Slides 13-14)
3. For live system demonstrations during the viva, follow [`FINAL_PRESENTATION_SCRIPT.md`](FINAL_PRESENTATION_SCRIPT.md) and [`DEMO_RUNBOOK.md`](DEMO_RUNBOOK.md).

### D. For Quality Assurance & Audit Reviewers
1. Read [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) for the complete catalog of all 78 documentation assets.
2. Review [`REPOSITORY_CLEANUP_REPORT.md`](REPOSITORY_CLEANUP_REPORT.md) and [`qa/phase18/documentation_reconciliation.md`](../qa/phase18/documentation_reconciliation.md) for archival records and preservation verification.

---

## 3. Core Academic Invariants Summary

All documentation adheres strictly to the canonical project invariants:

| Invariant | Value / Formula | Governing Document |
| :--- | :--- | :--- |
| **States ($Q$)** | 9 discrete states: `START`, `REQ_METHOD`, `REQ_URI`, `REQ_VER`, `REQ_HDRS`, `REQ_BODY`, `RES_STATUS`, `RES_HDRS`, `TRAP` | [`FORMAL_AUTOMATON.md`](FORMAL_AUTOMATON.md) |
| **Alphabet ($\Sigma$)** | 13 symbols: `EV_TCP_SYN`, `EV_REQ_METHOD`, `EV_REQ_URI`, `EV_REQ_HTTP11`, `EV_HDR_HOST`, `EV_HDR_CONTENT_LEN`, `EV_HDR_TRANSFER_ENC`, `EV_HDR_MISC`, `EV_BODY_CHUNK`, `EV_RES_STATUS_200`, `EV_RES_HDR_MISC`, `EV_TCP_FIN`, `EV_INVALID_TOKEN` | [`FORMAL_AUTOMATON.md`](FORMAL_AUTOMATON.md) |
| **Transition Matrix ($\delta$)** | $9 \times 13 = 117$ deterministic cells; non-standard or malformed transitions lead irrevocably to `TRAP` | [`TRANSITION_TABLE.md`](TRANSITION_TABLE.md) |
| **Accepting States ($F$)** | $F = \{ \text{RES\_HDRS} \}$ | [`FORMAL_AUTOMATON.md`](FORMAL_AUTOMATON.md) |
| **Trap Property** | $\forall \sigma \in \Sigma: \delta(\text{TRAP}, \sigma) = \text{TRAP}$ (Absorbing State, Sink) | [`TOC_THEORY.md`](TOC_THEORY.md) |
| **Hybrid Consensus Formula** | $S_h = 0.60 \cdot S_{FSM} + 0.40 \cdot S_{ML}$ | [`ALGORITHM_EXPLANATION.md`](ALGORITHM_EXPLANATION.md) |
| **FSM Violation Floor** | When $S_{FSM} = 1.0$, $S_h \ge 0.60$ (guaranteed malicious triage regardless of ML score) | [`ALGORITHM_EXPLANATION.md`](ALGORITHM_EXPLANATION.md) |

---

## 4. Archive Documentation Policy

Historical milestone reports that served specific sprint verification needs in previous phases (Phases 12, 14, 15, 16) are safely preserved in [`docs/archive/`](archive/). 

- **Preservation Principle**: No technical data or historical proof is deleted; older phase-specific audit files are archived to maintain clarity in the active documentation root.
- **Detailed Rationale**: A complete registry of all 36 archived files with the explicit rationale for each is documented in [`REPOSITORY_CLEANUP_REPORT.md`](REPOSITORY_CLEANUP_REPORT.md).
