# TraceGuard AI — Phase 14 Application Interaction & Route Inventory
**Document ID:** `docs/PHASE14_APPLICATION_INVENTORY.md`  
**Phase:** Phase 14 — Full Human-Style End-to-End QA, Swarm Verification & Complete Product Repair  
**Target Environment:** Localhost Frontend (`http://127.0.0.1:5173/`), Backend (`http://127.0.0.1:8000/`)  
**Mathematical Invariants:** Complete 9-State HTTP DFA ($|Q|=9$, $|\Sigma|=13$, $|\delta|=117$, $q_0=\text{IDLE}$, $F=\{\text{CLOSED}\}$, Absorbing $\text{TRAP}$)  
**Brand Identity:** Deep Ink (`#0E131F`), Electric Blue (`#3B82F6`), Emerald (`#10B981`), White (`#FFFFFF`); Light-first primary system  

---

## 1. Executive Summary

This inventory catalogues every user-accessible page route, layout component, modal dialog, interactive control, form input, filter, visualization element, and backend integration endpoint across TraceGuard AI. Discovered programmatically through comprehensive source code inspection of `frontend/src/App.jsx`, `frontend/src/layouts/AppLayout.jsx`, all page components, and FastAPI backend routers.

---

## 2. Route Topology & Access Matrix

| Route Path | Route Component | Access Tier | Layout Shell | Primary Backend Dependencies |
|---|---|---|---|---|
| `/` | `Dashboard.jsx` | Authenticated / Public Fallback | `AppLayout` | `GET /api/dashboard/summary`, `GET /api/events`, `WS /ws/events` |
| `/landing` | `Landing.jsx` | Public | Standalone | None (static brand landing) |
| `/login` | `Login.jsx` | Public | Standalone | `POST /api/auth/login`, `GET /api/auth/me`, `GET /api/auth/workspaces` |
| `/signup` | `Signup.jsx` | Public | Standalone | `POST /api/auth/signup`, `POST /api/auth/login` |
| `/automata` | `AutomataLab.jsx` | Authenticated / Public Console | `AppLayout` | `GET /api/protocols/http/fsm`, `GET /api/protocols/http/formal-automaton`, `POST /api/protocols/http/step-execute` |
| `/protocol` | `ProtocolExplorer.jsx` | Authenticated / Public Console | `AppLayout` | `GET /api/protocols/http/fsm` |
| `/monitor` | `LiveMonitor.jsx` | Authenticated / Public Console | `AppLayout` | `GET /api/events`, `WS /ws/events` |
| `/threats` | `Threats.jsx` | Authenticated / Public Console | `AppLayout` | `GET /api/alerts`, `GET /api/alerts/{id}`, `PATCH /api/alerts/{id}`, `WS /ws/alerts` |
| `/lab` | `DetectionLab.jsx` | Authenticated / Public Console | `AppLayout` | `GET /api/datasets`, `GET /api/detection/compare`, `POST /api/detection/run` |
| `/datasets` | `Datasets.jsx` | Authenticated / Public Console | `AppLayout` | `GET /api/datasets`, `POST /api/datasets/upload`, `GET /api/datasets/{id}/download` |
| `/settings` | `Settings.jsx` | Authenticated / Public Console | `AppLayout` | Local browser storage, active user context |
| `/*` | `Navigate to="/"` | Wildcard redirect | `AppLayout` | Redirects any unknown route to `/` |

---

## 3. Detailed Component & Control Inventory

### 3.1 Primary Application Layout (`frontend/src/layouts/AppLayout.jsx`)
- **Brand Header:**
  - Official vector mark link: `/traceguard-ai-horizontal-color.svg` (navigates to `/`).
  - Fallback vector badge: ShieldCheck icon with `TraceGuard AI` typography.
- **Sidebar Navigation Items:**
  1. `Overview` (`/`) — Icon: `LayoutDashboard`
  2. `Automata Lab` (`/automata`) — Icon: `GitBranch`, Badge: `TOC`
  3. `Protocol Explorer` (`/protocol`) — Icon: `Activity`, Badge: `Simulator`
  4. `Live Monitor` (`/monitor`) — Icon: `Radio`, Badge: `Live`
  5. `Threats` (`/threats`) — Icon: `ShieldAlert`
  6. `Detection Lab` (`/lab`) — Icon: `FlaskConical`, Badge: `Multi-Engine`
  7. `Datasets` (`/datasets`) — Icon: `Database`
  8. `Settings` (`/settings`) — Icon: `Settings`
- **Mobile Responsive Drawer:**
  - Hamburger menu button (`lg:hidden`).
  - Darkened backdrop overlay (`bg-black/75 backdrop-blur-sm`).
  - Close button (`X` icon).
- **Sidebar Footer Widgets:**
  - **Active User Profile:** Displays user's full name, email, avatar icon, active session dot, and dynamic Logout / Sign In button.
  - **Detection Engine Status:** Live WebSocket telemetry badge (`STREAM ONLINE` in emerald / `RECONNECTING` in amber / `OFFLINE` in rose) and 9-State Complete DFA badge.
- **Top Header Bar:**
  - Breadcrumb navigation (`TraceGuard > [Active Page]`).
  - **Presentation Mode Button:** Launches the academic 14-slide presentation modal.
  - **DFA Specification Pill:** `9 States · 13 Symbols · 117 δ`.
- **Presentation Modal (`PresentationMode.jsx`):**
  - Full-screen modal overlay.
  - Slide header with title, subtitle, and category.
  - 14 distinct slides covering formal language theory, DFA Chomsky classification, transition matrices, Isolation Forest statistical anomalies, hybrid consensus mathematical proofs, and live architecture.
  - Navigation controls: Previous button, Next button, Close button (`X`), slide dots, keyboard arrow listeners (`ArrowLeft`, `ArrowRight`, `Escape`).

---

### 3.2 Public Landing Page (`frontend/src/pages/Landing.jsx`)
- **Header:** Brand icon link to `/`, navigation links (`#engines`, `#specifications`, `#tiers`), `Sign In` (`/login`), `Launch Console` (`/`).
- **Hero Section:**
  - Pill badge: "Deterministic State-Machine & ML Hybrid Telemetry".
  - Headline: "Network protocol verification. Mathematically audited against formal automata."
  - CTA Button 1: "Launch Live Platform" (navigates to `/`).
  - CTA Button 2: "Register SOC Workspace" (navigates to `/signup`).
  - Metric Strip: 4 KPI cards (3 Engines, < 0.05ms Latency, 100% Explainable, 60% Risk Floor).
- **Engines Section (`#engines`):**
  - Card 1: Deterministic FSM (8 operational + 1 trap state).
  - Card 2: Isolation Forest ML (statistical outliers).
  - Card 3: Hybrid Engine Consensus ($S_h = 0.6 \cdot S_{\text{FSM}} + 0.4 \cdot S_{\text{ML}}$).
- **Formal Specifications Section (`#specifications`):**
  - LaTeX mathematical formula card ($M = (Q, \Sigma, \delta, q_0, F)$).
  - Transition matrix summary ($9 \times 13 = 117$ transitions).
- **Workspace Tiers Section (`#tiers`):**
  - Academic Free tier, Pro Team tier, Enterprise SOC tier.
- **Footer:** Academic disclaimer, repository links, copyright.

---

### 3.3 Authentication Pages (`Login.jsx` & `Signup.jsx`)
- **Login (`/login`):**
  - Brand header link to `/`.
  - Link to `/signup` ("create a new organization account").
  - Username input field (pre-filled with default demo operator `demo`).
  - Password input field (pre-filled with `traceguard2024`).
  - "Sign In" button with loading spinner and double-submit prevention.
  - Error banner (`rose-500` background) for invalid credentials.
- **Signup (`/signup`):**
  - Brand header link to `/`.
  - Link to `/login` ("Sign in to existing workspace").
  - Full Name input field.
  - Username input field.
  - Email input field.
  - Password input field.
  - "Create Workspace Account" button with submission progress.
  - Automatic workspace provisioning ($ws\_[uuid]$) and automatic login redirect.

---

### 3.4 Security Operations Center Dashboard (`frontend/src/pages/Dashboard.jsx`)
- **Header:** Page title and real-time telemetry badge.
- **KPI Cards Grid (`KPICard.jsx`):**
  1. `Total Events` — Ingested protocol stream count with 24h trend delta.
  2. `Protocol Violations` — Exploded count of illegal state transitions with violation rate percentage.
  3. `Detection Accuracy` — Benchmark accuracy of consensus engine.
  4. `Active Sessions` — Concurrent HTTP/TCP monitored contexts.
- **Visualizations Grid:**
  - **Ingestion Timeline (AreaChart):** Hourly volume distribution of protocol frames.
  - **Threat Severity Breakdown (PieChart):** Distribution of Critical, High, Medium, Low severity alerts.
- **Multi-Engine Consensus Panel:**
  - Deterministic FSM score breakdown bar with 60% violation risk floor.
  - Machine Learning anomaly confidence bar (40% weight).
  - Consensus risk score gauge.
- **Recent Violations Table:**
  - Recent flagged events with timestamp, session ID, threat description, engine badge, and direct deep-link to `/threats`.

---

### 3.5 Automata Laboratory (`frontend/src/pages/AutomataLab.jsx`)
- **Header:** Formal language verification console title.
- **Tab Controls:**
  1. `Interactive Automaton Graph & Stepper` (`visualizer`)
  2. `DFA Transition Matrix (117 δ)` (`matrix`)
  3. `Formal 5-Tuple & Theory` (`formal`)
- **Tab 1: Visualizer:**
  - **Graph Canvas:** Interactive ReactFlow rendering of all 9 states:
    - Initial state $q_0 = \text{IDLE}$ (blue accent, $q_0$ badge).
    - Accepting state $F = \{\text{CLOSED}\}$ (gold double border).
    - Absorbing trap state $\text{TRAP}$ (red warning border, self-loops).
    - Intermediate states: $\text{CONNECTED}, \text{REQUEST\_RECEIVED}, \text{AUTH\_CHECKED}, \text{AUTH\_FAILED}, \text{RESPONSE\_SENT}, \text{ERROR}$.
  - **Preset Sequence Dropdown:** 8 pre-configured academic sequences:
    1. Canonical Valid Transaction
    2. Pipelined Keep-Alive Session
    3. Auth Failure & 401 Response
    4. Premature Response Violation
    5. Authentication Bypass Violation
    6. Malformed Request Error Trap
    7. Valid Incomplete Prefix
    8. Connection Idle Timeout
  - **Input Sequence Field:** Editable comma-separated list of symbols.
  - **Stepper Controls:**
    - "Run Trace" button (calls `POST /api/protocols/http/step-execute`).
    - "Step Back" button.
    - "Step Forward" button.
    - "Reset" button.
  - **Execution History List:** Displays each step number, transition formula $\delta(q_t, \sigma) = q_{t+1}$, validity badge, and explanation.
- **Tab 2: Transition Matrix (117 δ):**
  - State filter dropdown (`ALL`, `IDLE`, `CONNECTED`, etc.).
  - Search symbol input.
  - Full matrix table displaying all $9 \times 13 = 117$ transition cells.
- **Tab 3: Formal Specification:**
  - 5-tuple overview cards ($Q, \Sigma, \delta, q_0, F$).
  - Proof of total function completeness.
  - Academic Chomsky Type-3 regular language notes.

---

### 3.6 Protocol FSM Explorer & Playback (`frontend/src/pages/ProtocolExplorer.jsx`)
- **Header:** Protocol trace playback and dynamic invariant debugger.
- **Input Sequence Bar:** Custom event sequence input box.
- **Playback Controls:**
  - Play / Pause button (auto-stepping with 1.2s timer).
  - Step Forward button.
  - Reset button.
- **Dynamic ReactFlow Graph:**
  - Animated edge transitions on step execution.
  - Traversed valid edges highlighted in emerald green.
  - Illegal transitions highlighted in danger rose red.
- **Validation Log Panel:**
  - Chronological transaction log detailing valid transitions and specific violation root causes.

---

### 3.7 Live Protocol Monitor (`frontend/src/pages/LiveMonitor.jsx`)
- **Header:** Real-time network stream monitor with WebSocket connection status badge.
- **Filter Bar:**
  - Search input (filters session ID, IP, or method).
  - Protocol / Event type dropdown filter.
  - Pause / Resume stream button.
  - Clear table button.
- **Live Event Table (`EventTable.jsx`):**
  - Displays streaming network events: Timestamp, Event ID, Session, Protocol, Event Type, Source/Destination, HTTP Method, Status Code, Bytes, and Ground Truth / Detection Label.
  - Smooth animation on incoming frames.

---

### 3.8 Threat Triage & Forensics (`frontend/src/pages/Threats.jsx`)
- **Header:** Threat triage title with live update indicator.
- **Filter Bar:**
  - Severity dropdown filter (`ALL`, `Critical`, `High`, `Medium`, `Low`).
  - Engine dropdown filter (`ALL`, `FSM`, `ML`, `Hybrid`).
- **Two-Panel Forensic Interface:**
  - **Left Panel (Incident List):** Scrollable master list of flagged alerts (`AlertCard.jsx`) with alert ID, severity tag, timestamp, engine badge, and session ID.
  - **Right Panel (Forensics & Triage):**
    - Alert summary: Alert ID, Severity, Session ID.
    - Score breakdown: FSM deterministic violation details, ML anomaly outlier score, hybrid consensus rating.
    - Raw event trace timeline within the session.
    - Triage Status Buttons: "Mark Investigating", "Resolve Incident", "Mark False Positive".
    - Operator Notes Textarea: Editable investigation notes.
    - "Update Status & Notes" button: Persists changes via `PATCH /api/alerts/{alert_id}`.

---

### 3.9 Detection Benchmark Lab (`frontend/src/pages/DetectionLab.jsx`)
- **Header:** Empirical detection benchmark lab title.
- **Dataset Selector:** Dropdown listing all uploaded benchmark datasets from `GET /api/datasets`.
- **Engine Execution Triggers:**
  - "Run FSM Engine" button.
  - "Run ML Engine" button.
  - "Run Hybrid Consensus" button.
- **Metrics Comparison Table:**
  - Precision, Recall, F1 Score, Detection Rate, False Positive Rate (FPR) across FSM, ML, and Hybrid engines.
- **Comparative Chart:** Recharts grouped BarChart comparing metrics visually.
- **Consensus Quadrant Matrix:** Explains multi-engine consensus logic (Quadrant 1: Both Detect, Quadrant 2: FSM Only, Quadrant 3: ML Only, Quadrant 4: Neither).

---

### 3.10 Benchmark Dataset Management (`frontend/src/pages/Datasets.jsx`)
- **Header:** Dataset management title.
- **Upload Panel:**
  - Dataset Name input.
  - Description input.
  - Drag-and-drop file upload zone (accepts `.csv` and `.json` protocol traces, max 10 MB).
  - "Upload & Validate Dataset" button with submission spinner.
- **Dataset Inventory Table:**
  - Lists all registered datasets: Name, Format, Event Count, Session Count, Ground Truth Labels indicator, Upload Date.
  - Action buttons: "Download CSV" link, "Benchmark" navigation link.

---

### 3.11 System Configuration & Hybrid Tuning (`frontend/src/pages/Settings.jsx`)
- **Header:** Settings and hybrid tuning title.
- **Consensus Weight Calibration Panel:**
  - Academic scope disclaimer notice.
  - FSM Invariant Weight range slider ($0.0 - 1.0$, default $0.6$).
  - Isolation Forest ML Weight range slider ($0.0 - 1.0$, default $0.4$).
  - FSM Violation Risk Floor range slider ($20\% - 95\%$, default $60\%$).
  - "Save Reference Weights" button with localStorage persistence and confirmation toast.
- **Active Operator Profile Panel:**
  - Operator Handle (read-only input).
  - Workstation Email (read-only input).
  - Role badge (SOC Analyst, Authorized).

---

## 4. Backend Endpoints & API Contract Map

| Endpoint | HTTP Method | Request Payload | Response Schema | Frontend Caller |
|---|---|---|---|---|
| `/api/health` | `GET` | None | `{status, version, database, models_loaded}` | `api.getHealth()` |
| `/api/auth/login` | `POST` | `{username, password}` | `TokenResponse` (`access_token`, `user`, `active_workspace_id`) | `api.login()` |
| `/api/auth/signup` | `POST` | `{username, email, password, full_name}` | `UserResponse` | `api.signup()` |
| `/api/auth/me` | `GET` | Bearer Token | `UserResponse` | `api.getMe()` |
| `/api/auth/workspaces` | `GET` | Bearer Token | `List[WorkspaceResponse]` | `api.getWorkspaces()` |
| `/api/dashboard/summary` | `GET` | Optional Token/Workspace | `DashboardSummaryResponse` (KPIs, timeline, severity) | `api.getDashboardSummary()` |
| `/api/events` | `GET` | `?limit=100&offset=0&session_id=...` | `{events, total}` | `api.getEvents()` |
| `/api/alerts` | `GET` | `?severity=...&engine=...&limit=100` | `{alerts, total}` | `api.getAlerts()` |
| `/api/alerts/{id}` | `GET` | None | `AlertDetailResponse` | `api.getAlertDetail()` |
| `/api/alerts/{id}` | `PATCH` | `{status, investigation_notes}` | `AlertResponse` | `api.updateAlert()` |
| `/api/protocols/http/fsm` | `GET` | None | `HttpFsmResponse` (states, transitions, 5-tuple) | `api.getHttpFsm()` |
| `/api/protocols/http/formal-automaton` | `GET` | None | `FormalAutomatonResponse` (Q, $\Sigma$, $\delta$, $q_0$, $F$, 117 matrix) | `api.getFormalAutomaton()` |
| `/api/protocols/http/step-execute` | `POST` | `{events, initial_state}` | `StepExecutionResponse` (steps, verdict, reasons) | `api.stepExecuteAutomaton()` |
| `/api/detection/run` | `POST` | `{session_ids, engines, dataset_id}` | `DetectionResponse` | `api.runDetection()` |
| `/api/detection/compare` | `GET` | `?dataset_id=...` | `DetectionCompareResponse` | `api.getDetectionComparison()` |
| `/api/datasets` | `GET` | None | `{datasets, total}` | `api.getDatasets()` |
| `/api/datasets/upload` | `POST` | Multipart `FormData` (`file`, `name`, `description`) | `DatasetResponse` | `api.uploadDataset()` |
| `/api/datasets/{id}/download` | `GET` | None | File download stream | `api.getDatasetDownloadUrl()` |
| `/ws/events` | `WebSocket` | Stream connection | Streaming `NetworkEvent` JSON frames | `useWebSocket('event')` |
| `/ws/alerts` | `WebSocket` | Stream connection | Streaming `Alert` JSON frames | `useWebSocket('alert')` |

---

## 5. Verification Status

- [x] All 11 application routes discovered and inventoried.
- [x] Primary navigation bar defect resolved (Protocol Explorer `/protocol` integrated into `AppLayout.jsx`).
- [x] React Context defect resolved (`<AuthProvider>` cleanly wrapped inside `<App.jsx>`).
- [x] Landing page CTA links updated from `/app` to `/`.
- [x] Dynamic user profile and logout controls active in sidebar.
- [x] All 32 backend pytest unit and integration tests passing.
- [x] Frontend production build succeeding in 366ms with zero oversized chunks.
