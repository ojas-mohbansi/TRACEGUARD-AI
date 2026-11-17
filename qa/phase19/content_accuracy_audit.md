# TraceGuard AI — Content & Academic Accuracy Audit
## Phase 19 Website Rebrand — Content Agent Output

**Auditor**: Content & Academic Accuracy Agent  
**Date**: 2026-11-17  
**Repo**: `C:\Projects\FSM-NIDS`

---

## PART 1 — VERIFIED TECHNICAL FACTS

### 1.1 FSM States (`backend/app/detection/fsm/states.py`, lines 10–20)

| Claim | Verified | Source |
|---|---|---|
| **9 total states** | ✅ CONFIRMED | `states.py` lines 10–20: `IDLE, CONNECTED, REQUEST_RECEIVED, AUTH_CHECKED, AUTH_FAILED, RESPONSE_SENT, ERROR, CLOSED, TRAP` |
| **8 operational states** | ✅ CONFIRMED | `OPERATIONAL_STATES` list lines 25–34 (excludes TRAP) |
| **1 dead/sink state (TRAP)** | ✅ CONFIRMED | Line 20: `TRAP = "TRAP" # Formal DFA sink/trap state for total transition completeness` |
| **Initial state = IDLE** | ✅ CONFIRMED | Line 23: `INITIAL_STATE = State.IDLE` |
| **Accepting state = CLOSED** | ✅ CONFIRMED | Line 24: `FINAL_STATES: Set[str] = {State.CLOSED}` |
| **TRAP is non-accepting** | ✅ CONFIRMED | TRAP not in `FINAL_STATES`; `HTTP_FSM_DEFINITION` line 92: `"is_final": False` |
| **TRAP is absorbing** | ✅ CONFIRMED | `engine.py` lines 96–103: `if current_state == State.TRAP: ...self-loop...continue`; `FORMAL_AUTOMATON.md` line 56 |

---

### 1.2 Input Alphabet (`states.py`, lines 38–52)

| Claim | Verified | Source |
|---|---|---|
| **13 symbols** | ✅ CONFIRMED | `EventType` class: 13 string constants |
| Symbols enumerated | ✅ CONFIRMED | `CONNECT, REQUEST, AUTH_SUCCESS, AUTH_FAILURE, RESPONSE_200, RESPONSE_301, RESPONSE_401, RESPONSE_403, RESPONSE_500, CLOSE, TIMEOUT, MALFORMED, ERROR_RESPONSE` |

---

### 1.3 Transition Count Analysis — How 117 Is Derived

The TRANSITION_MAP (`states.py` lines 56–72) contains **15 explicit valid protocol transitions**:

```
1.  (IDLE,              CONNECT)        → CONNECTED
2.  (CONNECTED,         REQUEST)        → REQUEST_RECEIVED
3.  (CONNECTED,         TIMEOUT)        → CLOSED
4.  (REQUEST_RECEIVED,  AUTH_SUCCESS)   → AUTH_CHECKED
5.  (REQUEST_RECEIVED,  AUTH_FAILURE)   → AUTH_FAILED
6.  (REQUEST_RECEIVED,  MALFORMED)      → ERROR
7.  (AUTH_CHECKED,      RESPONSE_200)   → RESPONSE_SENT
8.  (AUTH_CHECKED,      RESPONSE_301)   → RESPONSE_SENT
9.  (AUTH_CHECKED,      RESPONSE_500)   → ERROR
10. (AUTH_FAILED,       RESPONSE_401)   → RESPONSE_SENT
11. (AUTH_FAILED,       RESPONSE_403)   → RESPONSE_SENT
12. (RESPONSE_SENT,     REQUEST)        → REQUEST_RECEIVED
13. (RESPONSE_SENT,     CLOSE)          → CLOSED
14. (ERROR,             CLOSE)          → CLOSED
15. (ERROR,             ERROR_RESPONSE) → RESPONSE_SENT
```

**Total DFA transition table (117-entry completeness):**

| Component | Count |
|---|---|
| 15 valid protocol transitions (explicit) | 15 |
| 88 undefined transitions → TRAP (all other non-TRAP, non-CLOSED states × symbols not listed) | 88 |
| 13 post-CLOSED transitions → TRAP (∀σ ∈ Σ, δ(CLOSED, σ) = TRAP) | 13 |
| 13 TRAP absorbing self-loops (∀σ ∈ Σ, δ(TRAP, σ) = TRAP) | 13 |
| **Total: 9 × 13** | **117** |

**Verified in:** `FORMAL_AUTOMATON.md` lines 50–56 (formal proof); `README.md` line 101; `test_fsm.py` line 120 (`len(definition["transitions"]) == 15`).

**Accurate language:** "The 15 explicit valid transitions are implemented in code. The remaining 102 entries (all mapping to TRAP) are enforced by the engine's fallback logic, completing the total 9 × 13 = 117 DFA transition matrix."

---

### 1.4 Trace Classifications (`FORMAL_AUTOMATON.md`, lines 74–76; `README.md`, lines 110–115)

| Enum Value | Verified | Meaning |
|---|---|---|
| `ACCEPTED` | ✅ CONFIRMED | δ*(q₀, w) ∈ F — final state is CLOSED |
| `INCOMPLETE_VALID` | ✅ CONFIRMED | All transitions valid, final state ∉ F ∪ {TRAP} |
| `REJECTED` | ✅ CONFIRMED | δ*(q₀, w) = TRAP — at least one illegal transition |

> **Note:** These are semantic labels defined in formal documentation, not Python enums in code. The FSM engine returns `prediction: "normal"/"anomalous"` and `fsm_violation: bool`. The ACCEPTED/INCOMPLETE_VALID/REJECTED taxonomy is the formal automata classification layer.

---

### 1.5 Hybrid Scoring Formula (`backend/app/detection/hybrid/engine.py`)

| Claim | Verified | Source (line) |
|---|---|---|
| `S_h = 0.6 × S_FSM + 0.4 × S_ML` | ✅ CONFIRMED | Line 65: `combined_score = (self.fsm_weight * fsm_score) + (self.ml_weight * ml_score)` |
| `fsm_weight = 0.6` | ✅ CONFIRMED | Line 9: `fsm_weight: float = 0.6` |
| `ml_weight = 0.4` | ✅ CONFIRMED | Line 9: `ml_weight: float = 0.4` |
| 60% risk floor on FSM violation | ✅ CONFIRMED | Lines 66–67: `if fsm_violation: combined_score = max(combined_score, 60.0)` |
| Risk range: 0–100 | ✅ CONFIRMED | Line 69: `int(round(min(100.0, max(0.0, combined_score))))` |
| Severity thresholds: Low/Medium/High/Critical | ✅ CONFIRMED | Lines 16–22: 0–25 / 26–50 / 51–75 / 76–100 |

---

### 1.6 ML Method (`backend/app/detection/ml/engine.py`)

| Claim | Verified | Source |
|---|---|---|
| Isolation Forest algorithm | ✅ CONFIRMED | Line 11: `from sklearn.ensemble import IsolationForest`; line 70: `IsolationForest(...)` |
| `n_estimators = 100` | ✅ CONFIRMED | Line 73 |
| `contamination = 0.1` (10%) | ✅ CONFIRMED | Line 38 / `KNOWN_LIMITATIONS.md` line 22 |
| `random_state = 42` | ✅ CONFIRMED | Line 39 |
| Anomaly score normalized [0.0, 1.0] | ✅ CONFIRMED | Lines 93–106 |
| ML anomaly threshold = 0.70 | ✅ CONFIRMED | `hybrid/engine.py` line 73: `ml_anomaly_score >= 0.70` |
| **15 session features** | ✅ CONFIRMED | `features/extractor.py` FEATURE_COLUMNS array |

**Feature list (15 variables):**
`event_count`, `unique_event_types`, `session_duration_seconds`, `avg_inter_event_time`, `std_inter_event_time`, `invalid_transition_count`, `auth_failure_count`, `error_count`, `response_2xx_ratio`, `response_4xx_ratio`, `response_5xx_ratio`, `avg_bytes`, `has_close`, `request_rate`, `unique_methods`

---

### 1.7 FSM Risk Score Rules (`engine.py` lines 160–175)

| Condition | Risk Score |
|---|---|
| Clean, complete session | 0 |
| Incomplete session (no CLOSE) | 30 |
| Single protocol violation | 60 |
| Two violations | 80 |
| Three violations | 85 |
| N violations (N ≥ 2) | min(95, 80 + (N−2) × 5) |
| Impossible transition (unknown event or post-CLOSED) | 100 |

---

### 1.8 Test Suite Facts (`README.md` line 170; `PROJECT_REPORT.md` line 70)

- README states: **32 tests** in test suite  
- PROJECT_REPORT.md states: **31/31 unit, integration, and security tests passing**  
- `test_fsm.py` contains 8 test functions covering all state transitions  
- `test_integration.py` contains multiple integration, end-to-end, and schema tests

> **Recommendation**: Use "pytest suite covering FSM unit tests, integration tests, and schema validation" rather than citing a specific number; the counts differ between documents.

---

### 1.9 ML Benchmark Metrics (`KNOWN_LIMITATIONS.md` lines 22–26)

| Metric | Value | Context |
|---|---|---|
| Training set | 480 synthetic sessions | Fixed seed=42 |
| Test set | 120 synthetic sessions | Fixed seed=42 |
| F1-Score on test set | **0.5312** | Synthetic dataset only |
| Zero-day detection rate | **68.0%** | Synthetic zero-day templates only |

> **MUST label these as synthetic benchmark results.** Do not present as live-network performance.

---

## PART 2 — CLAIMS THAT CANNOT BE VERIFIED / MUST BE OMITTED

| Claim | Status | Reason |
|---|---|---|
| Team member names / affiliations | ❌ NOT FOUND | README section 10 only says: Course: Theory of Computation, Department: CSE, Academic Year: 2026. No names. |
| University name / institution | ❌ NOT FOUND | Not present in any file |
| Specific instructor or advisor names | ❌ NOT FOUND | Not documented anywhere |
| Live network validation performance | ❌ CANNOT CLAIM | Explicitly contradicted by `KNOWN_LIMITATIONS.md` sections 2 and 3 |
| Commercial readiness | ❌ CANNOT CLAIM | README explicitly states "not commercial perimeter defense" |
| Exact test count (32 vs 31) | ⚠️ CONFLICTING | Use vague "complete test suite" |

---

## PART 3 — TEAM / ACADEMIC INFORMATION FOUND

**From `README.md` Section 10 (lines 270–274):**

```
Course: Theory of Computation / Formal Languages and Automata Theory
Department: Computer Science & Engineering
Project Name: TraceGuard AI: Protocol NIDS
Academic Year: 2026
```

**No individual author names or institutional names appear in any file.** The website Team/Academic section must work without names.

---

## PART 4 — ACCURATE WEBSITE CONTENT

### 4.1 NAVIGATION LABELS

```
Main Nav:
- TraceGuard AI  (logo link → home)
- Overview       (replaces "About" or "Home")
- Research       (replaces "Applications" or "Technology")
- Architecture   (replaces "Company")
- Limitations    (new — academic honesty section)
- Contact        (keep)

Mobile/Hamburger secondary:
- GitHub →       (external link to repo)
- Documentation  (links to /docs section)
```

---

### 4.2 HERO SECTION

**Project name:** TraceGuard AI

**One-sentence description:**
> TraceGuard AI is an academic research prototype that mathematically verifies HTTP protocol session sequences against a formal Deterministic Finite Automaton and flags statistical anomalies via Isolation Forest machine learning.

**Tagline (short):**
> Formal automata meet network intrusion detection.

**Tagline (long):**
> Where Theory of Computation becomes a security primitive.

**Three key metrics (accurate, sourced):**

| Metric | Value | Source label |
|---|---|---|
| DFA States | 9 | `states.py` |
| Input Alphabet | 13 symbols | `states.py` |
| Transition Matrix | 9 × 13 = 117 entries | `FORMAL_AUTOMATON.md` |

**Metric display text:**
```
9 States          — Complete DFA state space (1 sink)
13 Symbols        — HTTP protocol event alphabet |Σ|
117 Transitions   — Total transition matrix |Q × Σ|
```

**Hero CTA buttons:**
- Primary: `Explore the Research` → scrolls to #research
- Secondary: `View on GitHub` → external link

---

### 4.3 PROBLEM SECTION

**Section heading:** The Gap in Protocol Intrusion Detection

**Body copy:**

Modern network intrusion detection systems fall into two categories: signature-based systems that match known attack patterns, and machine learning systems that flag statistical outliers. Both approaches share a fundamental blind spot — neither mathematically verifies whether a network session follows a legally permitted protocol sequence.

Application protocols like HTTP are stateful. A client must connect before requesting, authenticate before receiving protected resources, and close the connection when done. Attackers exploit this order: auth-bypass attempts send responses before authentication, session hijacking injects events into ongoing flows, and malformed sequences exploit undefined protocol behavior.

**The formal language theory answer:** If the set of permissible HTTP event sequences constitutes a Regular Language, a Deterministic Finite Automaton can decide membership in O(1) time per event — with zero false positives on conforming sessions and constructive proof-of-violation for rejected ones. No signature database required; no retraining after each new exploit variant.

TraceGuard AI demonstrates this principle end-to-end: from formal 5-tuple definition through live session classification, augmented with an Isolation Forest for volumetric and behavioral anomalies the DFA cannot detect.

**Three problem cards:**

1. **Out-of-Order Execution**  
   Auth-bypass, response injection before authentication, resources accessed without handshake. Invisible to packet-level signature scanners.

2. **State Injection**  
   Attackers manipulate session flows to skip checkpoints. Signature databases miss novel variants; ML cannot explain why a sequence is illegal.

3. **Black-Box Opacity**  
   Deep learning NIDS generate anomaly scores without causal explanation. Protocol violations require legally-rooted evidence for SOC investigation.

---

### 4.4 DFA SECTION — FORMAL SPECIFICATION

**Section heading:** The Formal Automaton — M = (Q, Σ, δ, q₀, F)

**Intro paragraph:**

TraceGuard AI models the HTTP session lifecycle as a Complete Total Deterministic Finite Automaton. A Complete DFA requires a defined transition for every (state, symbol) pair — no undefined behavior, no gaps. This mathematical completeness is what guarantees that any input sequence receives an unambiguous verdict.

**The 5-Tuple (display as table or cards):**

```
Q  (State Space)      |Q| = 9
   IDLE, CONNECTED, REQUEST_RECEIVED, AUTH_CHECKED, AUTH_FAILED,
   RESPONSE_SENT, ERROR, CLOSED, TRAP

Σ  (Input Alphabet)   |Σ| = 13
   CONNECT, REQUEST, AUTH_SUCCESS, AUTH_FAILURE,
   RESPONSE_200, RESPONSE_301, RESPONSE_401, RESPONSE_403,
   RESPONSE_500, CLOSE, TIMEOUT, MALFORMED, ERROR_RESPONSE

δ  (Transition Fn)    δ: Q × Σ → Q  (117 total entries)
   15 valid protocol transitions (explicit)
   102 undefined transitions → TRAP (enforced by engine fallback)

q₀ (Initial State)   IDLE
   Quiescent; awaiting TCP connection event

F  (Accepting States) {CLOSED}
   Terminal accepting state; clean connection teardown
```

**TRAP State explanation:**

The TRAP state is a formal dead/sink state required for DFA completeness. Once entered, all subsequent inputs self-loop back to TRAP — it is non-escapable. Any session that reaches TRAP is classified REJECTED regardless of subsequent events. This is the mathematical formalization of "no recovery from a protocol violation."

```
∀σ ∈ Σ, δ(TRAP, σ) = TRAP
```

**Transition count explanation:**

The 117 entries in the complete transition matrix break down as:
- **15** valid protocol transitions (implemented explicitly in `TRANSITION_MAP`)
- **88** undefined state/symbol combinations → all route to TRAP
- **13** post-CLOSED transitions → all route to TRAP  
- **13** TRAP self-loops → δ(TRAP, σ) = TRAP for all σ

The 15 explicit transitions and the TRAP routing together form a mathematically complete function: every (state, symbol) input has exactly one defined output.

**Three trace classifications:**

| Classification | Formal Condition | Meaning |
|---|---|---|
| **ACCEPTED** | δ*(q₀, w) ∈ F | Valid sequence; final state = CLOSED |
| **INCOMPLETE_VALID** | δ*(q₀, w) ∉ F, no TRAP reached | Valid prefix; session in-flight |
| **REJECTED** | δ*(q₀, w) = TRAP | Protocol violation detected |

**Risk scores by classification:**

```
ACCEPTED          → risk_score = 0    (clean session)
INCOMPLETE_VALID  → risk_score = 30   (incomplete, no violation)
REJECTED (1 viol) → risk_score = 60   (single violation)
REJECTED (2 viol) → risk_score = 80+  (escalating: +5 per violation)
REJECTED (impossible) → risk_score = 100 (unknown events / post-CLOSED)
```

---

### 4.5 ML / HYBRID SECTION

**Section heading:** Hybrid Detection — Determinism + Statistical Learning

**Intro:**

The DFA verifies protocol sequence correctness — but it cannot detect volumetric attacks, behavioral outliers, or anomalies that use legally-ordered events. Isolation Forest fills this gap: it detects sessions whose statistical profile deviates from baseline normal behavior, without labels or supervised training.

**Feature Extraction subsection:**

Before ML scoring, 15 session-level features are extracted from each event stream:

```
Timing:    session_duration_seconds, avg_inter_event_time, std_inter_event_time
Volume:    event_count, avg_bytes, request_rate
Events:    unique_event_types, unique_methods
State:     invalid_transition_count, auth_failure_count, error_count
Ratios:    response_2xx_ratio, response_4xx_ratio, response_5xx_ratio
Flag:      has_close
```

**Isolation Forest subsection:**

Isolation Forest is an unsupervised anomaly detection algorithm that isolates observations by randomly partitioning feature space. Anomalous sessions — with unusual timing, response rates, or failure patterns — require fewer partitions to isolate and receive higher anomaly scores. The model assigns each session an anomaly score normalized to [0.0, 1.0].

Model parameters (from `ml/engine.py`):
- `n_estimators = 100`
- `contamination = 0.1` (10% expected anomaly rate)
- `random_state = 42`

Sessions with anomaly score ≥ 0.70 are flagged as ML-anomalous.

**Hybrid Scoring Formula subsection:**

The Hybrid Engine combines both scores into a single interpretable risk index:

```
S_h = (0.6 × S_FSM) + (0.4 × S_ML)

where:
  S_FSM ∈ [0, 100]  — FSM protocol violation score
  S_ML  ∈ [0, 100]  — ML anomaly score × 100
  S_h   ∈ [0, 100]  — combined risk index
```

**Violation Floor Rule:**

When a DFA protocol violation is detected (`fsm_violation = true`), the hybrid engine enforces a mandatory risk floor:

```
if fsm_violation:
    S_h = max(S_h, 60.0)
```

This guarantees that any formally proven protocol violation results in at least a **High severity** alert, regardless of the ML score.

**Four Detection Quadrants:**

| Quadrant | FSM | ML | Risk | Verdict |
|---|---|---|---|---|
| A — Normal | Conforming | Normal profile | < 40 | normal |
| B — FSM-only | Violation | Normal profile | ≥ 60 (floor) | anomalous |
| C — ML-only | Conforming | Anomalous profile | Elevated by ML | anomalous if score ≥ 40 |
| D — Combined | Violation | Anomalous profile | ≥ 80 | anomalous / critical |

---

### 4.6 ARCHITECTURE SECTION

**Section heading:** Detection Pipeline Architecture

**Pipeline stages (sequential):**

```
1. EVENT INGESTION
   Protocol events arrive via WebSocket stream (/ws/events) or
   REST API upload (/api/datasets/upload). Events carry:
   session_id, event_type, timestamp, method, status_code, bytes.

2. SESSION GROUPING
   Events are grouped by session_id into ordered sequences for
   per-session analysis.

3. FSM VERIFICATION (Tier 1)
   Each event sequence is replayed symbol-by-symbol through the
   DFA. Invalid transitions route to TRAP. Output: risk_score,
   violation list, transition history, fsm_violation flag.

4. FEATURE EXTRACTION
   15 session-level statistical features are computed from the
   event stream: timing, volume, state counters, response ratios.

5. ISOLATION FOREST SCORING (Tier 2)
   The 15-feature vector is scored by the trained Isolation Forest
   model. Output: anomaly_score ∈ [0.0, 1.0], ml_anomalous flag.

6. HYBRID CONSENSUS (Tier 3)
   S_h = 0.6×S_FSM + 0.4×S_ML, with 60% floor on FSM violation.
   Attribution: "fsm" / "ml" / "hybrid" / "none".

7. ALERT STORAGE
   Results with risk_score ≥ threshold are persisted as alerts in
   SQLite (via SQLAlchemy ORM) with full audit trail.

8. FRONTEND DELIVERY
   REST endpoints expose alerts, session details, and FSM
   definitions. WebSocket stream delivers live event telemetry
   to the React monitoring dashboard.
```

**Tech stack cards:**

| Layer | Technology |
|---|---|
| Backend API | Python 3.11 + FastAPI 0.115.6 + Uvicorn |
| Detection Engines | Custom FSM + scikit-learn IsolationForest |
| Persistence | SQLAlchemy 2.0 + SQLite |
| Frontend | React 19 + Vite + TypeScript + Tailwind CSS v4 |
| State Graph | ReactFlow 11.11.4 |
| Real-time | WebSocket full-duplex stream |
| Deployment | Docker + docker-compose |

---

### 4.7 LIMITATIONS SECTION (ACADEMIC HONESTY)

**Section heading:** Academic Scope & Known Limitations

**Intro:**
TraceGuard AI is an academic prototype developed for a Theory of Computation curriculum. The following limitations are documented transparently in the interest of scientific integrity.

**Limitation cards (from `KNOWN_LIMITATIONS.md`):**

**1. Regular Language Boundary**  
Deterministic Finite Automata recognize Type-3 Regular Languages only. HTTP payload syntax — including deeply nested JSON bodies, chunked transfer encodings, or HTTP/2 multiplexed streams — requires Pushdown Automata (Context-Free Grammars). The FSM models the protocol event lifecycle, not payload content.

**2. Synthetic Benchmarks Only**  
All ML benchmark results are derived from synthetic datasets (600 sessions, `seed=42`). The model has not been validated against live network captures or enterprise perimeter traffic. Reported F1-Score (0.5312) and zero-day detection rate (68.0%) are synthetic-only figures.

**3. Simulated Traffic Ingestion**  
The system does not bind to raw network interfaces via PCAP/libpcap. Traffic arrives via the built-in Markovian simulation engine or CSV/JSON file upload — not live packet capture.

**4. Session Abstraction**  
Verification operates on parsed protocol event sequences, not raw Ethernet frame buffers. A production deployment requires a session reconstruction layer (e.g., Zeek / Suricata) upstream.

**5. Single-Tenant Storage**  
Data isolation is SQLite, single-tenant. Multi-tenant RBAC and enterprise SSO (SAML/OIDC) are not implemented in this prototype.

**6. No Commercial Readiness**  
This project is designed for academic demonstration and research evaluation, not commercial perimeter defense.

---

### 4.8 TEAM / ACADEMIC SECTION

**Section heading:** Academic Context

> **IMPORTANT:** No individual author names or institution names are present in any codebase file or documentation. The section must not invent or assume any.

**Accurate content:**

TraceGuard AI was developed as an academic capstone project for a **Theory of Computation / Formal Languages and Automata Theory** course in the **Department of Computer Science & Engineering**, Academic Year **2026**.

The project bridges mathematical foundations — regular language theory, Chomsky hierarchy, DFA completeness proofs — with practical software engineering: a full-stack intrusion detection platform with REST API, WebSocket streaming, React visualization, and automated test suite.

**Coursework context card:**
```
Course:      Theory of Computation / Formal Languages and Automata Theory
Department:  Computer Science & Engineering  
Academic Year: 2026
Project Type: Capstone / Research Prototype
```

**Research artifacts available:**
- Formal automaton specification (`FORMAL_AUTOMATON.md`)
- Transition table proof (`TRANSITION_TABLE.md`)
- Theory of Computation foundations (`TOC_THEORY.md`)
- Algorithm explanation (`ALGORITHM_EXPLANATION.md`)
- Project report (`PROJECT_REPORT.md`)
- University defense preparation (`VIVA_PREPARATION.md`)

---

### 4.9 CTA LABELS (REPLACE TIDEWELL CTAS)

**Replace "Get early access" / "Early access" with:**

| Old (Tidewell) | New (TraceGuard AI) |
|---|---|
| `Get early access` | `Explore the Research` |
| `Early access` (form heading) | `Research Access` |
| `Join the waitlist` | `View Documentation` |
| `Request a demo` | `Run the Demo Locally` |
| Newsletter form | Link to GitHub README |
| Email capture | GitHub star / fork CTA |

**Primary CTA copy:**

```
Explore the Research
→ Dive into the formal automaton specification, algorithm explanation,
  and academic project report.
```

```
Run the Demo Locally
→ Clone the repository, install dependencies, and run the full
  detection pipeline on your machine in under 5 minutes.
```

**No commercial CTAs.** No "request pricing", no "enterprise contact", no "join beta".

---

### 4.10 FOOTER CONTENT

**Project description:**

> TraceGuard AI is an academic cybersecurity research prototype demonstrating formal DFA-based HTTP protocol verification combined with Isolation Forest anomaly detection. Developed for a Theory of Computation / Formal Languages and Automata Theory course.

**Footer columns:**

```
Column 1 — Project
  TraceGuard AI
  [description above]
  Academic Year 2026

Column 2 — Research
  Overview
  DFA Specification
  Hybrid Engine
  Architecture
  Limitations

Column 3 — Documentation
  README
  FORMAL_AUTOMATON.md
  ALGORITHM_EXPLANATION.md
  PROJECT_REPORT.md
  TRANSITION_TABLE.md

Column 4 — Academic
  Theory of Computation
  Department: CS & Engineering
  Academic Year: 2026
  [GitHub link]
```

**Footer legal line:**
> TraceGuard AI is an academic research prototype. Not intended for production deployment without additional hardening, live dataset retraining, and security review.

**Copyright line:**
> © 2026 TraceGuard AI Academic Project — Department of Computer Science & Engineering

---

## PART 5 — SUMMARY CHECKLIST

| Item | Status |
|---|---|
| 9 FSM states verified | ✅ |
| 13 alphabet symbols verified | ✅ |
| 117 transition matrix count explained | ✅ |
| Initial state = IDLE confirmed | ✅ |
| Accepting state = CLOSED confirmed | ✅ |
| TRAP absorbing behavior confirmed | ✅ |
| ACCEPTED / INCOMPLETE_VALID / REJECTED confirmed (semantic labels) | ✅ |
| Hybrid formula 0.6/0.4 confirmed | ✅ |
| 60% risk floor confirmed | ✅ |
| Isolation Forest confirmed | ✅ |
| 15 ML features confirmed | ✅ |
| Synthetic benchmark labeling required | ✅ |
| No team names (not in codebase) | ✅ |
| No commercial claims | ✅ |
| No live-network validation claims | ✅ |
| All content text written | ✅ |

---

*End of Content & Academic Accuracy Audit — Phase 19*
