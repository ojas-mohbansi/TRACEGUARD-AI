# TraceGuard AI — Master Documentation Index & Catalog

This document is the authoritative catalog of all documentation within the TraceGuard AI project repository. It details file paths, subject domains, target audiences, academic invariants, and lifecycle statuses across all active and archived documentation.

---

## 1. Documentation Overview Matrix

| Category | Active Files | Archived Files | Primary Focus | Primary Audience |
| :--- | :---: | :---: | :--- | :--- |
| **Academic & Automata Theory** | 5 | — | Formal DFA, 5-Tuple, 117-transition matrix, Chomsky hierarchy, Viva preparation | Course Faculty, TOC Examiners |
| **System Architecture & Design** | 9 | — | FastAPI backend, React frontend, REST/WebSocket APIs, security model, database schema | Software Architects, Developers |
| **Operations, Demos & Delivery** | 11 | — | Evaluator demo scripts, runbooks, GitHub packaging, release readiness, limitations | Evaluators, Operators, SOC Team |
| **Benchmark & Engine Analytics** | 5 | — | Phase 17 evaluation benchmark, synthetic workloads, detection performance analysis | Data Scientists, Evaluators |
| **Presentation & Oral Defense** | 6 | — | Word-for-word spoken scripts for 5 presenters, team handoff cues, defense rehearsal matrix | Defense Speakers, Faculty Panel |
| **Historical Milestone Archive** | — | 36 | Archived Phase 12 brand audits, Phase 14-16 intermediate milestone and verification reports | Project Provenance, QA Auditors |
| **Index & Cleanup Governance** | 3 | — | Documentation suite overview, master index catalog, repository cleanup report | All Stakeholders |
| **Total** | **39** | **36** | **Comprehensive Full-Spectrum Academic & Engineering Coverage** | **All Project Roles** |

---

## 2. Directory Structure Tree

```text
docs/
├── README.md                            # Documentation Suite Overview & Reading Roadmap
├── DOCUMENTATION_INDEX.md               # [This Document] Master Catalog & Invariants Matrix
├── REPOSITORY_CLEANUP_REPORT.md         # Safe Repository Cleanup & Archival Sign-Off Report
│
├── [Academic & Theoretical Foundations]
│   ├── FORMAL_AUTOMATON.md              # Formal 5-tuple M = (Q, Σ, δ, q0, F) definition & theorems
│   ├── TRANSITION_TABLE.md              # 117-cell transition matrix (9 states × 13 alphabet symbols)
│   ├── TOC_THEORY.md                    # Regular languages, Pumping Lemma, Chomsky classification, TRAP sink
│   ├── ALGORITHM_EXPLANATION.md         # FSM verification, Isolation Forest ML & hybrid consensus formula
│   └── VIVA_PREPARATION.md              # 60 viva voce defense questions, equations & counterarguments
│
├── [System Architecture & Engineering]
│   ├── ARCHITECTURE.md                  # System component topology, packet ingestion & data flow
│   ├── API_CONTRACTS.md                 # REST API endpoints, JSON schemas & WebSocket telemetry
│   ├── DATA_SCHEMA.md                   # Database models, event telemetry schemas & relational entities
│   ├── SECURITY_MODEL.md                # Threat model, token authentication, packet privacy & tenant isolation
│   ├── CI_CD.md                         # Continuous integration, automated test execution & linting
│   ├── DEPLOYMENT.md                    # Docker, local development, and enterprise deployment setups
│   ├── SAAS_ARCHITECTURE.md             # Multi-tenant scaling, cloud ingestion & worker architecture
│   ├── SAAS_ROADMAP.md                  # Future roadmap for enterprise cloud migration
│   └── BRAND_SYSTEM.md                  # Visual identity tokens, typography, dark/light themes & CSS mapping
│
├── [Operations, Demonstrations & Submission]
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
│   ├── PHASE17_BENCHMARK_METHODOLOGY.md # Evaluation methodology, synthetic attack suites & baseline metrics
│   ├── PHASE17_ENGINE_ANALYTICS.md      # Analytical throughput, latency, and false positive metrics
│   ├── PHASE17_FINAL_REPORT.md          # Phase 17 benchmark and local academic mode completion report
│   ├── PHASE17_FSM_DETECTION_ANALYSIS.md# In-depth analysis of FSM vs ML detection rates across scenarios
│   └── PHASE17_LOCAL_ACADEMIC_MODE.md   # Deterministic local academic evaluation mode specification
│
├── presentation/                        # Presenter guides & team oral defense coordination
│   ├── PRESENTATION_TEAM_OVERVIEW.md    # Master speaking order, timing budgets, handoffs & defense checklist
│   ├── presenter_1.md                   # Presenter 1: Intro, Problem Statement & Scope (Slides 1-3, 2.5 min)
│   ├── presenter_2.md                   # Presenter 2: Formal HTTP DFA, 5-Tuple, Transitions & TRAP (Slides 4-8, 3.5 min)
│   ├── presenter_3.md                   # Presenter 3: ML Isolation Forest, Consensus Formula & Benchmark (Slides 9-11, 2.5 min)
│   ├── presenter_4.md                   # Presenter 4: Architecture, Pipeline & Threats Forensics (Slide 12, 2.5 min)
│   └── presenter_5.md                   # Presenter 5: Live Workflow, Evidence, Limitations & Defense Q&A (Slides 13-14, 2.5 min)
│
└── archive/                             # Safely preserved historical milestone reports (36 files)
    ├── BRAND_REBRAND_AUDIT.md           # Phase 12 initial component-by-component brand audit
    ├── BRAND_REBRAND_FINAL_AUDIT.md     # Phase 12 brand fidelity and contrast audit report
    ├── BRAND_REBRAND_FINAL_QA.md        # Phase 12 quality assurance signoff for brand migration
    ├── BRAND_REBRAND_IMPLEMENTATION.md  # Phase 12 CSS design tokens and component implementation log
    ├── BRAND_REBRAND_QA.md              # Phase 12 intermediate brand QA report
    ├── BRAND_REBRAND_SCREENSHOT_INDEX.md# Phase 12 screenshot catalog for design verification
    ├── PHASE14_2_FINAL_SIGNOFF.md       # Phase 14.2 multi-agent sign-off report
    ├── PHASE14_2_FORMAL_VERIFICATION.md # Phase 14.2 verification logs and proofs
    ├── PHASE14_2_HYBRID_SCORING_VERIFICATION.md # Phase 14.2 hybrid consensus formula testing record
    ├── PHASE14_2_SWARM_COMPLETION.md    # Phase 14.2 multi-agent swarm task execution log
    ├── PHASE14_APPLICATION_INVENTORY.md # Phase 14 interim component inventory
    ├── PHASE14_DEFECT_REGISTER.md       # Phase 14 defect triage and bug resolution log
    ├── PHASE14_FINAL_REPORT.md          # Phase 14 milestone summary report
    ├── PHASE14_ROUTE_COVERAGE.md        # Phase 14 frontend route testing matrix
    ├── PHASE14_WORKFLOW_COVERAGE.md     # Phase 14 user journey and workflow test execution
    ├── PHASE15_AUTH_AND_NAVIGATION.md   # Phase 15 JWT auth and route guard hardening record
    ├── PHASE15_AUTOMATA_LAB_FIX.md      # Phase 15 Automata Lab state visualizer bugfix record
    ├── PHASE15_ENGINE_CLASSIFICATION.md # Phase 15 classification engine tuning log
    ├── PHASE15_FINAL_REPORT.md          # Phase 15 milestone summary report
    ├── PHASE15_LIVE_NETWORK_ARCHITECTURE.md # Phase 15 live packet capture pipeline design notes
    ├── PHASE15_THREAT_FORENSICS.md      # Phase 15 forensic incident investigation log
    ├── PHASE16_1_EVIDENCE_RECONCILIATION.md # Phase 16.1 forensic evidence and capture audit record
    ├── PHASE16_1_FINAL_SIGNOFF.md       # Phase 16.1 quality gate signoff
    ├── PHASE16_1_ML_CALIBRATION.md      # Phase 16.1 Isolation Forest threshold tuning log
    ├── PHASE16_1_PRIVACY_AND_CAPTURE_AUDIT.md # Phase 16.1 payload privacy and PII scrubbing verification
    ├── PHASE16_2_ALERT_PROVENANCE_AUDIT.md # Phase 16.2 alert lineage and signature trace verification
    ├── PHASE16_2_DEMO_REHEARSAL.md      # Phase 16.2 rehearsal walk-through notes
    ├── PHASE16_2_FINAL_SIGNOFF.md       # Phase 16.2 final signoff audit
    ├── PHASE16_2_FINAL_TEST_REPORT.md   # Phase 16.2 backend and frontend test run output
    ├── PHASE16_2_FORMAL_FSM_VALIDATION.md # Phase 16.2 formal FSM validation report
    ├── PHASE16_2_ML_EVALUATION.md       # Phase 16.2 ML precision, recall, and ROC analysis record
    ├── PHASE16_DEMONSTRATION_GUIDE.md   # Phase 16 demonstration instructions
    ├── PHASE16_ENGINE_ANALYTICS.md      # Phase 16 performance metrics
    ├── PHASE16_FINAL_REPORT.md          # Phase 16 milestone summary report
    ├── PHASE16_FSM_DETECTION_PROOF.md   # Phase 16 mathematical detection proof
    └── PHASE16_NPCAP_DIAGNOSTICS.md     # Phase 16 Windows Npcap driver setup and troubleshooting
```

---

## 3. Active Documentation Catalog

### 3.1 Academic & Theoretical Foundations

| File | Title & Core Subject | Target Audience | Key Mathematical Invariants |
| :--- | :--- | :--- | :--- |
| [`FORMAL_AUTOMATON.md`](FORMAL_AUTOMATON.md) | **Formal Automaton Specification**<br>Comprehensive mathematical definition of $\mathcal{M} = (Q, \Sigma, \delta, q_0, F)$ | Theory Faculty, Evaluators | $|Q|=9$, $|\Sigma|=13$, $|\delta|=117$, $F = \{ \text{RES\_HDRS} \}$, deterministic polynomial time $O(n)$ |
| [`TRANSITION_TABLE.md`](TRANSITION_TABLE.md) | **117-Cell Transition Matrix**<br>Exhaustive mapping for every state-symbol pair | Theory Faculty, Evaluators | Complete $9 \times 13$ matrix, explicit absorbing `TRAP` state transitions |
| [`TOC_THEORY.md`](TOC_THEORY.md) | **Theory of Computation Foundations**<br>Regular languages, Chomsky hierarchy, Pumping Lemma | Theory Faculty, Students | Type-3 regular grammar, memoryless state transitions, trap sink proof |
| [`ALGORITHM_EXPLANATION.md`](ALGORITHM_EXPLANATION.md) | **Detection Algorithm & Consensus Logic**<br>FSM parser, Isolation Forest ML, hybrid score | Evaluators, ML Engineers | $S_h = 0.6 \cdot S_{FSM} + 0.4 \cdot S_{ML}$, $S_{FSM}=1.0 \implies S_h \ge 0.6$ |
| [`VIVA_PREPARATION.md`](VIVA_PREPARATION.md) | **Viva Voce Defense Preparation**<br>60 faculty examination questions with model answers | Presenters, Defense Team | Mathematical proofs, complexity derivations, counter-arguments |

### 3.2 System Architecture & Engineering

| File | Title & Core Subject | Target Audience | Key Content & Specifications |
| :--- | :--- | :--- | :--- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | **System Architecture Blueprint**<br>Packet pipeline, async engine, frontend design | Software Engineers | FastAPI, Scapy/Npcap, asyncio event loop, Vite React UI |
| [`API_CONTRACTS.md`](API_CONTRACTS.md) | **REST & WebSocket API Contracts**<br>Endpoints, schemas, payloads, status codes | Frontend/Backend Developers | `/api/fsm/verify`, `/api/detection/scan`, `/ws/telemetry` |
| [`DATA_SCHEMA.md`](DATA_SCHEMA.md) | **Database & Event Telemetry Schema**<br>Relational entities, telemetry records, alerts | Database Administrators | SQLite/PostgreSQL schemas, Alembic migrations, event models |
| [`SECURITY_MODEL.md`](SECURITY_MODEL.md) | **Security, Privacy & Threat Model**<br>Authentication, token encryption, payload sanitization | Security Engineers | JWT auth, AES token handling, PII redaction, tenant isolation |
| [`CI_CD.md`](CI_CD.md) | **Continuous Integration & Delivery**<br>Automated test workflows and linting | DevOps Engineers | GitHub Actions, pytest, ESLint, automated quality gates |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | **Deployment Runbook**<br>Docker Compose, standalone, and enterprise setups | Systems Administrators | Dockerfile, docker-compose.yml, environment configuration |
| [`SAAS_ARCHITECTURE.md`](SAAS_ARCHITECTURE.md) | **Enterprise Multi-Tenant SaaS Topology**<br>Horizontal scaling, Celery workers, Redis queues | Cloud Architects | Distributed packet broker, tenant isolation, Redis buffer |
| [`SAAS_ROADMAP.md`](SAAS_ROADMAP.md) | **SaaS Product Roadmap**<br>Phase progression from single-node to cloud scale | Product Managers | Milestone tracking, feature roadmap, enterprise readiness |
| [`BRAND_SYSTEM.md`](BRAND_SYSTEM.md) | **Brand & Design System Specification**<br>Design tokens, typography, dark/light themes | Frontend Engineers, Designers | Obsidian `#0E131F`, Emerald `#10B981`, Blue `#3B82F6` |

### 3.3 Operations, Demonstrations & Submission Delivery

| File | Title & Core Subject | Target Audience | Key Content & Specifications |
| :--- | :--- | :--- | :--- |
| [`ACADEMIC_DEMONSTRATION.md`](ACADEMIC_DEMONSTRATION.md) | **Evaluator Walkthrough Guide**<br>Guided execution of live academic showcase | Course Evaluators | 5-minute showcase, sample injections, verdict checks |
| [`DEMO_RUNBOOK.md`](DEMO_RUNBOOK.md) | **Operator Demonstration Runbook**<br>Step-by-step console setup and service startup | Presenters, Lab Demonstrators | Startup commands, port bindings, health checks |
| [`FINAL_PRESENTATION_SCRIPT.md`](FINAL_PRESENTATION_SCRIPT.md) | **Live Demonstration Script**<br>Timed interface walkthrough synchronized with UI | Demonstration Speakers | 5-7 minute walkthrough script for Automata Lab & Live Monitor |
| [`PROJECT_REPORT.md`](PROJECT_REPORT.md) | **Formal University Project Report**<br>Problem statement, related work, methodology, results | Academic Evaluators | Full formal academic project report write-up |
| [`RELEASE_READINESS.md`](RELEASE_READINESS.md) | **Release Readiness Review**<br>Quality gates, test pass criteria, benchmark targets | QA Lead, Release Manager | 100% test pass guarantee, memory profiling, clean exit |
| [`GITHUB_RELEASE_READINESS.md`](GITHUB_RELEASE_READINESS.md) | **GitHub Packaging & Release Guide**<br>Repository structuring, release tags, release notes | Release Engineer | Release checklists, git tag conventions, artifact assets |
| [`FINAL_RELEASE_VERIFICATION.md`](FINAL_RELEASE_VERIFICATION.md) | **Final Release Verification Sign-Off**<br>Multi-agent swarm quality audit record | Project Leads | Verified test pass reports, zero-regression guarantee |
| [`FINAL_SUBMISSION_MANIFEST.md`](FINAL_SUBMISSION_MANIFEST.md) | **Submission Deliverables Manifest**<br>Index of submitted artifacts, hashes, and files | Course Coordinators | Code, documentation, presentation, datasets inventory |
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | **Official Submission Checklist**<br>Academic rubric compliance verification | Faculty Evaluators | Complete compliance audit against university rubric |
| [`IMPLEMENTATION_LOG.md`](IMPLEMENTATION_LOG.md) | **Chronological Engineering Log**<br>Historical development log across all phases | Engineering Team | Milestone records, bug fixes, refactoring history |
| [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) | **Documented Academic Limitations**<br>Theoretical and architectural system boundaries | Faculty Examiners, Researchers | Regular language boundary, Pushdown Automata future scope |

### 3.4 Benchmark & Engine Analytics (Phase 17)

| File | Title & Core Subject | Target Audience | Key Content & Specifications |
| :--- | :--- | :--- | :--- |
| [`PHASE17_BENCHMARK_METHODOLOGY.md`](PHASE17_BENCHMARK_METHODOLOGY.md) | **Benchmark Evaluation Methodology**<br>Synthetic evaluation datasets and attack suites | Data Scientists, Evaluators | RFC 7231 conformant streams, injected state violations |
| [`PHASE17_ENGINE_ANALYTICS.md`](PHASE17_ENGINE_ANALYTICS.md) | **Throughput & Latency Engine Analytics**<br>Verification performance and packet processing rates | Performance Engineers | Packet/sec processing metrics, memory footprints |
| [`PHASE17_FINAL_REPORT.md`](PHASE17_FINAL_REPORT.md) | **Phase 17 Milestone Final Report**<br>Summary of benchmark and academic mode milestones | Academic Evaluators | 149 passing unit/integration tests, zero regressions |
| [`PHASE17_FSM_DETECTION_ANALYSIS.md`](PHASE17_FSM_DETECTION_ANALYSIS.md) | **FSM vs ML Comparative Detection Analysis**<br>Evaluation across attack scenarios | ML & Security Researchers | Precision, recall, F1-score, consensus behavior |
| [`PHASE17_LOCAL_ACADEMIC_MODE.md`](PHASE17_LOCAL_ACADEMIC_MODE.md) | **Deterministic Local Academic Mode**<br>Standalone deterministic evaluation harness | Evaluators, Students | Zero-dependency offline evaluation harness |

### 3.5 Presentation & Oral Defense Suite (`docs/presentation/`)

| File | Presenter / Document | Slide Scope | Duration | Key Spoken Topics |
| :--- | :--- | :---: | :---: | :--- |
| [`PRESENTATION_TEAM_OVERVIEW.md`](presentation/PRESENTATION_TEAM_OVERVIEW.md) | **Team Presentation Master Coordination** | Slides 1–14 | 13.5 min | Speaker allocations, time limits, handoff cues, defense matrix |
| [`presenter_1.md`](presentation/presenter_1.md) | **Presenter 1: Foundation & Scope** | Slides 1–3 | 2.5 min | Title, NIDS challenge, state exhaustion, protocol scope |
| [`presenter_2.md`](presentation/presenter_2.md) | **Presenter 2: Formal HTTP DFA Theory** | Slides 4–8 | 3.5 min | 5-tuple, 9 states, 13 alphabet symbols, 117 matrix, absorbing TRAP |
| [`presenter_3.md`](presentation/presenter_3.md) | **Presenter 3: ML Anomaly & Hybrid Consensus** | Slides 9–11 | 2.5 min | Isolation Forest, $S_h = 0.6 \cdot S_{FSM} + 0.4 \cdot S_{ML}$, 60% floor |
| [`presenter_4.md`](presentation/presenter_4.md) | **Presenter 4: Architecture & Forensics** | Slide 12 | 2.5 min | Ingestion pipeline, forensics drawer, payload privacy redaction |
| [`presenter_5.md`](presentation/presenter_5.md) | **Presenter 5: Demonstration, Proof & Viva Q&A** | Slides 13–14 | 2.5 min | Live demo evidence, 149 passing tests, PDA scope, defense Q&A |

---

## 4. Historical Archive Registry (`docs/archive/`)

The 36 files moved to [`docs/archive/`](archive/) represent interim sprint audits and earlier phase verification records that are preserved for auditability and provenance:

| Category | Archived File | Original Purpose | Reason for Archival & Superseded-By Reference |
| :--- | :--- | :--- | :--- |
| **Brand Rebrand** | `BRAND_REBRAND_AUDIT.md` | Initial Phase 12 UI audit | Superseded by canonical [`docs/BRAND_SYSTEM.md`](BRAND_SYSTEM.md) |
| **Brand Rebrand** | `BRAND_REBRAND_FINAL_AUDIT.md` | Phase 12 brand fidelity audit | Preserved as historical design verification record |
| **Brand Rebrand** | `BRAND_REBRAND_FINAL_QA.md` | Phase 12 QA test report | Preserved as historical test pass evidence |
| **Brand Rebrand** | `BRAND_REBRAND_IMPLEMENTATION.md` | Phase 12 CSS implementation log | Superseded by active CSS in `frontend/src/styles/` |
| **Brand Rebrand** | `BRAND_REBRAND_QA.md` | Phase 12 intermediate QA audit | Superseded by FINAL_QA report |
| **Brand Rebrand** | `BRAND_REBRAND_SCREENSHOT_INDEX.md` | Phase 12 visual verification index | Historical screenshot catalog |
| **Phase 14** | `PHASE14_2_FINAL_SIGNOFF.md` | Phase 14.2 multi-agent signoff | Superseded by [`FINAL_RELEASE_VERIFICATION.md`](FINAL_RELEASE_VERIFICATION.md) |
| **Phase 14** | `PHASE14_2_FORMAL_VERIFICATION.md` | Phase 14.2 verification logs | Superseded by [`docs/FORMAL_AUTOMATON.md`](FORMAL_AUTOMATON.md) & tests |
| **Phase 14** | `PHASE14_2_HYBRID_SCORING_VERIFICATION.md`| Phase 14.2 consensus test log | Superseded by [`ALGORITHM_EXPLANATION.md`](ALGORITHM_EXPLANATION.md) |
| **Phase 14** | `PHASE14_2_SWARM_COMPLETION.md` | Phase 14.2 swarm execution log | Preserved for swarm execution provenance |
| **Phase 14** | `PHASE14_APPLICATION_INVENTORY.md` | Phase 14 component inventory | Superseded by [`qa/phase18/repository_inventory.json`](../qa/phase18/repository_inventory.json) |
| **Phase 14** | `PHASE14_DEFECT_REGISTER.md` | Phase 14 bug triage register | All defects resolved in codebase |
| **Phase 14** | `PHASE14_FINAL_REPORT.md` | Phase 14 milestone final report | Archived for project lifecycle history |
| **Phase 14** | `PHASE14_ROUTE_COVERAGE.md` | Phase 14 route test matrix | Superseded by current route test suites |
| **Phase 14** | `PHASE14_WORKFLOW_COVERAGE.md` | Phase 14 user journey matrix | Superseded by current E2E browser tests |
| **Phase 15** | `PHASE15_AUTH_AND_NAVIGATION.md` | Phase 15 JWT auth hardening | Superseded by [`docs/SECURITY_MODEL.md`](SECURITY_MODEL.md) |
| **Phase 15** | `PHASE15_AUTOMATA_LAB_FIX.md` | Phase 15 Automata Lab visualizer fix | Bug resolved; visualizer verified active in UI |
| **Phase 15** | `PHASE15_ENGINE_CLASSIFICATION.md` | Phase 15 engine tuning log | Superseded by [`PHASE17_ENGINE_ANALYTICS.md`](PHASE17_ENGINE_ANALYTICS.md) |
| **Phase 15** | `PHASE15_FINAL_REPORT.md` | Phase 15 milestone final report | Archived for project lifecycle history |
| **Phase 15** | `PHASE15_LIVE_NETWORK_ARCHITECTURE.md`| Phase 15 live packet capture notes | Superseded by [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) |
| **Phase 15** | `PHASE15_THREAT_FORENSICS.md` | Phase 15 forensic incident triage | Preserved as test evidence in `qa/phase15/` |
| **Phase 16** | `PHASE16_1_EVIDENCE_RECONCILIATION.md` | Phase 16.1 evidence reconciliation | Superseded by Phase 18 reconciliation |
| **Phase 16** | `PHASE16_1_FINAL_SIGNOFF.md` | Phase 16.1 quality gate signoff | Superseded by [`FINAL_RELEASE_VERIFICATION.md`](FINAL_RELEASE_VERIFICATION.md) |
| **Phase 16** | `PHASE16_1_ML_CALIBRATION.md` | Phase 16.1 Isolation Forest tuning | Consolidated in [`ALGORITHM_EXPLANATION.md`](ALGORITHM_EXPLANATION.md) |
| **Phase 16** | `PHASE16_1_PRIVACY_AND_CAPTURE_AUDIT.md`| Phase 16.1 privacy sanitization | Consolidated in [`docs/SECURITY_MODEL.md`](SECURITY_MODEL.md) |
| **Phase 16** | `PHASE16_2_ALERT_PROVENANCE_AUDIT.md`| Phase 16.2 alert lineage verify | Preserved as test evidence in `qa/phase16_2/` |
| **Phase 16** | `PHASE16_2_DEMO_REHEARSAL.md` | Phase 16.2 rehearsal notes | Superseded by [`presentation/`](presentation/) guides |
| **Phase 16** | `PHASE16_2_FINAL_SIGNOFF.md` | Phase 16.2 final signoff audit | Superseded by Phase 18 final sign-off |
| **Phase 16** | `PHASE16_2_FINAL_TEST_REPORT.md` | Phase 16.2 test run output | Preserved in `qa/phase16_2/` |
| **Phase 16** | `PHASE16_2_FORMAL_FSM_VALIDATION.md` | Phase 16.2 formal FSM validation | Consolidated in [`docs/FORMAL_AUTOMATON.md`](FORMAL_AUTOMATON.md) |
| **Phase 16** | `PHASE16_2_ML_EVALUATION.md` | Phase 16.2 ML precision/recall | Consolidated in [`PHASE17_FSM_DETECTION_ANALYSIS.md`](PHASE17_FSM_DETECTION_ANALYSIS.md) |
| **Phase 16** | `PHASE16_DEMONSTRATION_GUIDE.md` | Phase 16 demo instructions | Superseded by [`docs/DEMO_RUNBOOK.md`](DEMO_RUNBOOK.md) |
| **Phase 16** | `PHASE16_ENGINE_ANALYTICS.md` | Phase 16 performance metrics | Superseded by [`PHASE17_ENGINE_ANALYTICS.md`](PHASE17_ENGINE_ANALYTICS.md) |
| **Phase 16** | `PHASE16_FINAL_REPORT.md` | Phase 16 milestone final report | Archived for project lifecycle history |
| **Phase 16** | `PHASE16_FSM_DETECTION_PROOF.md` | Phase 16 mathematical proof | Consolidated in [`docs/TOC_THEORY.md`](TOC_THEORY.md) |
| **Phase 16** | `PHASE16_NPCAP_DIAGNOSTICS.md` | Phase 16 Npcap troubleshooting | Technical reference for Windows capture driver |
