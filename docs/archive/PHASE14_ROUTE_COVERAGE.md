# TraceGuard AI — Phase 14 Route Coverage Report
**Document ID:** `docs/PHASE14_ROUTE_COVERAGE.md`  
**Phase:** Phase 14 — Full Human-Style End-to-End QA, Swarm Verification & Complete Product Repair  
**Target Environment:** Localhost Frontend (`http://127.0.0.1:5173/`), Backend (`http://127.0.0.1:8000/`)  
**Testing Methodology:** Live Human-Style Webview Browser Interaction, API Contract Tracing, Viewport Testing  

---

## 1. Overview & Verification Summary

TraceGuard AI's frontend architecture provides 11 distinct accessible routes: 3 public standalone entrypoints (`/landing`, `/login`, `/signup`) and 8 primary Security Operations Center console routes managed under `AppLayout` (`/`, `/automata`, `/protocol`, `/monitor`, `/threats`, `/lab`, `/datasets`, `/settings`), plus wildcard redirect routing (`/*`).

Every route has been loaded, visually inspected, interacted with via real browser events (clicking buttons, typing into form fields, toggling filters, adjusting sliders, and running live simulations), and verified against its underlying FastAPI backend API and WebSocket endpoints.

---

## 2. Route-by-Route Coverage Matrix

### 2.1 Route: `/landing` (Public Landing Page)
- **Path:** `/landing`
- **Authentication Requirement:** Public (Unauthenticated)
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`, `1440x900`, `1920x1080`), Tablet (`768x1024`), Mobile (`390x844`, `413x791`)
- **Interactive Controls Exercised:**
  - Header brand link: Clicked, navigates to `/`.
  - Navigation anchors: `#engines`, `#specifications`, `#tiers`.
  - "Sign In" button: Clicked, navigates to `/login`.
  - "Launch Console" CTA: Clicked, navigates to `/`.
  - "Launch Live Platform" Hero CTA: Clicked, navigates to `/`.
  - "Register SOC Workspace" Hero CTA: Clicked, navigates to `/signup`.
  - Tier cards "Get Started" / "Start Pro Trial" / "Contact Sales" buttons: All link to `/signup`.
- **Backend Connections Checked:** Static assets verified, brand SVGs loaded from root public directory.
- **Persistence Verified:** N/A (Static informational page).
- **Result:** **PASS**
- **Known Defects & Remediation:**
  - *Previous Defect (P2):* Hero CTA links pointed to `/app` which required a wildcard redirect hop to `/`.
  - *Remediation:* Updated links in `frontend/src/pages/Landing.jsx` to direct target `/`.

---

### 2.2 Route: `/login` (User Authentication)
- **Path:** `/login`
- **Authentication Requirement:** Public (Unauthenticated)
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`), Mobile (`390x844`)
- **Interactive Controls Exercised:**
  - Brand header link: Clicked, navigates to `/`.
  - Link to `/signup` ("create a new organization account"): Clicked, navigates to `/signup`.
  - Username input field: Checked default `demo`, typed custom username.
  - Password input field: Checked default `traceguard2024`, masked text verified.
  - "Sign In" submit button: Clicked, transitions to "Authenticating..." spinner, prevents duplicate submission.
- **Backend Connections Checked:**
  - `POST /api/auth/login` — Authenticates user, seeds demo operator if non-existent, returns JWT bearer token and active workspace ID.
  - `GET /api/auth/me` — Loads user profile (`id`, `username`, `email`, `full_name`).
  - `GET /api/auth/workspaces` — Loads authorized workspaces list.
- **Persistence Verified:**
  - `localStorage.setItem('traceguard_token', token)`
  - `localStorage.setItem('traceguard_user', JSON.stringify(profile))`
  - `localStorage.setItem('traceguard_workspace_id', workspace_id)`
  - On page refresh or navigation to `/`, session remains active; sidebar renders user name `demo` and `demo@traceguard.ai` with active session indicator.
- **Result:** **PASS**
- **Known Defects & Remediation:**
  - *Previous Defect (P0/P1):* `useAuth()` in `Login.jsx` failed with `Error: useAuth must be used within an AuthProvider` because `<AuthProvider>` was not wrapped around `<App />`.
  - *Remediation:* Integrated `<AuthProvider>` into `frontend/src/App.jsx` inside `<BrowserRouter>` and `<ErrorBoundary>`.

---

### 2.3 Route: `/signup` (Workspace Registration)
- **Path:** `/signup`
- **Authentication Requirement:** Public (Unauthenticated)
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`), Mobile (`390x844`)
- **Interactive Controls Exercised:**
  - Brand header link: Navigates to `/`.
  - Link to `/login` ("Sign in to existing workspace"): Navigates to `/login`.
  - Form fields: Full Name, Username, Email, Password.
  - "Create Workspace Account" submit button: Verified submission and validation.
- **Backend Connections Checked:**
  - `POST /api/auth/signup` — Creates user, creates personal workspace with slug `$username-personal-[uuid]`, assigns `RoleEnum.OWNER`.
  - Auto-login via `POST /api/auth/login`.
- **Persistence Verified:** Database transaction creates `users`, `workspaces`, and `workspace_members` rows; JWT token stored in `localStorage`.
- **Result:** **PASS**
- **Known Defects & Remediation:**
  - *Previous Defect (P0/P1):* `Signup.jsx` crashed on mount with unhandled `AuthProvider` context missing error.
  - *Remediation:* Fixed via `<AuthProvider>` root wrapping in `App.jsx`.

---

### 2.4 Route: `/` (Security Operations Center Dashboard)
- **Path:** `/`
- **Authentication Requirement:** Public Fallback / Authenticated
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`, `1440x900`), Mobile (`390x844`)
- **Interactive Controls Exercised:**
  - "Sync Telemetry" refresh button: Clicked, refetches summary metrics.
  - KPI Cards (Total Events, Active Sessions, Critical Alerts, Detection Accuracy, Latency): Dynamic live counters.
  - Charts: Ingestion timeline AreaChart, Detection consensus breakdown Donut chart, Recharts tooltips hover states.
  - "View All Alerts" table link: Navigates to `/threats`.
  - "Investigate" incident buttons in Recent Threats table: Navigates to `/threats` with alert focus.
  - Sidebar Navigation Links: Tested navigation to all 8 core modules.
  - User Badge Logout Button: Clears JWT token and resets user state to unauthenticated.
- **Backend Connections Checked:**
  - `GET /api/dashboard/summary` — Returns 200 OK with total events, alert counts, and timeline telemetry.
  - `GET /api/events` — Loads recent streaming events.
  - `WS /ws/events` — Connects live telemetry stream ("STREAM ONLINE" badge).
- **Persistence Verified:** Telemetry poll persists across tab switches; theme tokens apply cleanly.
- **Result:** **PASS**

---

### 2.5 Route: `/automata` (Automata Laboratory)
- **Path:** `/automata`
- **Authentication Requirement:** Console Route
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`, `1440x900`), Tablet (`768x1024`)
- **Interactive Controls Exercised:**
  - Tab Switcher:
    - Tab 1: `Interactive Automaton Graph & Stepper`
    - Tab 2: `DFA Transition Matrix (117 δ)`
    - Tab 3: `Formal 5-Tuple & Theory`
  - Preset Sequence Dropdown: Selected "Canonical Valid Transaction".
  - "Load & Run" Button: Clicked, transitions start state to `CONNECTED`, executes full DFA evaluation.
  - Stepper Controls:
    - "Step Forward" button: Increments step index, advances active node highlight.
    - "Step Backward" button: Decrements step index.
    - "Reset" button: Restores automaton to $q_0 = \text{IDLE}$.
  - Custom Input Sequence: Modified comma-separated input string.
  - Matrix Filter Controls: State filter dropdown, symbol search input.
- **Backend Connections Checked:**
  - `GET /api/protocols/http/fsm` — Retrieves formal state machine definitions.
  - `GET /api/protocols/http/formal-automaton` — Retrieves 117-cell transition matrix and 5-tuple proof.
  - `POST /api/protocols/http/step-execute` — Dispatches event symbols and returns step-by-step verdicts.
- **Persistence Verified:** Execution logs update reactively; DFA mathematical invariants maintained ($|Q|=9$, $|\Sigma|=13$, 117 cells, accepting $\{CLOSED\}$, absorbing $TRAP$).
- **Result:** **PASS**

---

### 2.6 Route: `/protocol` (Protocol FSM Explorer & Playback)
- **Path:** `/protocol`
- **Authentication Requirement:** Console Route
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`), Mobile (`390x844`)
- **Interactive Controls Exercised:**
  - Event sequence text box: Custom string input.
  - "Step Forward" button: Step-by-step traversal with live edge animations.
  - "Play / Pause" button: Automatic 1.2s playback cycle.
  - "Reset" button: Restores initial state `IDLE`.
  - Edge Traversal Visualizer: Emerald green for valid transitions, Rose red for illegal transitions.
  - Validation Log List: Chronological transition history with error diagnosis.
- **Backend Connections Checked:** `GET /api/protocols/http/fsm`.
- **Persistence Verified:** In-memory stepper state reacts dynamically to input events.
- **Result:** **PASS**
- **Known Defects & Remediation:**
  - *Previous Defect (P1):* Route existed in `App.jsx` but was missing from `NAV_ITEMS` in `AppLayout.jsx`, making it unreachable from the sidebar.
  - *Remediation:* Added `Protocol Explorer` (`/protocol`) with `Activity` icon and `Simulator` badge to `NAV_ITEMS`.

---

### 2.7 Route: `/monitor` (Live Protocol Monitor)
- **Path:** `/monitor`
- **Authentication Requirement:** Console Route
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`), Tablet (`768x1024`)
- **Interactive Controls Exercised:**
  - Telemetry Stream Badge: Verifies WebSocket connection ("STREAM ONLINE").
  - Search filter input: Filters by session ID or IP.
  - Protocol type dropdown: Toggles event classification.
  - "Pause / Resume" stream button: Toggles live ingestion queue.
  - "Clear Feed" button: Clears local event buffer.
- **Backend Connections Checked:**
  - `GET /api/events` — Initial event history load.
  - `WS /ws/events` — Live bi-directional frame broadcast.
- **Persistence Verified:** WebSocket reconnects automatically upon connection drop; event queue maintains max buffer limit without memory leaks.
- **Result:** **PASS**

---

### 2.8 Route: `/threats` (Threat Triage & Forensics)
- **Path:** `/threats`
- **Authentication Requirement:** Console Route
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`), Mobile (`390x844`)
- **Interactive Controls Exercised:**
  - Severity dropdown filter: Filtered by Critical, High, Medium, Low.
  - Engine dropdown filter: Filtered by FSM, ML, Hybrid.
  - Incident triage cards (`AlertCard.jsx`): Clicked alert item in master list to select.
  - Forensic details panel: Inspected anomaly breakdown and raw event trace.
  - Triage Action Buttons: "Mark Investigating", "Resolve Incident", "Mark False Positive".
  - Operator Notes Textarea: Entered forensic notes and clicked "Update Status & Notes".
- **Backend Connections Checked:**
  - `GET /api/alerts` — Alert list with filtering.
  - `GET /api/alerts/{id}` — Incident forensic details payload.
  - `PATCH /api/alerts/{id}` — Mutation endpoint for status and notes persistence.
- **Persistence Verified:** Database updates confirmed on `alerts` table; UI refetches and displays updated status badges.
- **Result:** **PASS**

---

### 2.9 Route: `/lab` (Detection Benchmark Lab)
- **Path:** `/lab`
- **Authentication Requirement:** Console Route
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`, `1440x900`)
- **Interactive Controls Exercised:**
  - Target Dataset Dropdown: Selected benchmark dataset (`verify_upload_15def3`).
  - "Run FSM Engine" button: Executed FSM detector.
  - "Run ML Engine" button: Executed Isolation Forest outlier detector.
  - "Run Hybrid Consensus" button: Executed hybrid scoring algorithm ($0.6 \cdot S_{\text{FSM}} + 0.4 \cdot S_{\text{ML}}$).
  - Metrics Comparison Table: Precision, Recall, F1 Score, Detection Rate, FPR.
  - Recharts Grouped BarChart: Multi-engine visual comparison across all metrics.
- **Backend Connections Checked:**
  - `GET /api/datasets` — Populates dataset dropdown.
  - `POST /api/detection/run` — Executes detector models over target session traces.
  - `GET /api/detection/compare` — Retrieves empirical benchmark metrics.
- **Persistence Verified:** Metric values calculate deterministically from dataset sessions; no mock data fabrication.
- **Result:** **PASS**

---

### 2.10 Route: `/datasets` (Benchmark Dataset Management)
- **Path:** `/datasets`
- **Authentication Requirement:** Console Route
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`), Tablet (`768x1024`)
- **Interactive Controls Exercised:**
  - Dataset Name & Description text inputs.
  - File Dropzone: Uploaded `.csv` synthetic protocol trace file.
  - "Upload & Validate Dataset" button: Clicked, verified validation and upload progress.
  - Dataset Table: Verified registered datasets list (39 datasets registered).
  - Download Link: Tested CSV download endpoint.
- **Backend Connections Checked:**
  - `GET /api/datasets` — Fetches registered dataset inventory.
  - `POST /api/datasets/upload` — Multipart form upload, CSV parsing, row validation.
  - `GET /api/datasets/{id}/download` — Binary stream download.
- **Persistence Verified:** Uploaded datasets stored in `datasets` table and file storage; rows immediately appear in the inventory.
- **Result:** **PASS**

---

### 2.11 Route: `/settings` (System Configuration & Hybrid Tuning)
- **Path:** `/settings`
- **Authentication Requirement:** Console Route
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`), Mobile (`390x844`)
- **Interactive Controls Exercised:**
  - FSM Weight Slider: Adjusted range between 0.0 and 1.0 (auto-balances ML weight).
  - ML Weight Slider: Adjusted range between 0.0 and 1.0.
  - FSM Violation Risk Floor Slider: Adjusted percentage threshold between 20% and 95%.
  - "Save Reference Weights" Submit Button: Clicked, verified confirmation alert banner ("Reference weights saved to browser").
  - Operator Profile card: Verified read-only operator handle and workstation email.
- **Backend Connections Checked:** Active user session profile loaded via AuthContext.
- **Persistence Verified:** Reference weights persisted in `localStorage` under `traceguard_hybrid_config`.
- **Result:** **PASS**

---

### 2.12 Header Component: Presentation Mode (`PresentationMode.jsx`)
- **Entrypoint:** Top Header CTA Button ("Presentation Mode" with `PlaySquare` icon).
- **Browser Test Completed:** YES
- **Viewports Tested:** Desktop (`1280x800`, `1920x1080`), Mobile (`390x844`)
- **Interactive Controls Exercised:**
  - "Presentation Mode" Header Button: Opens full-screen academic modal.
  - "Next Slide" Button: Advances slide index.
  - "Previous Slide" Button: Returns to previous slide.
  - Slide Dots: Direct navigation to specific slides.
  - Keyboard Navigation: `ArrowRight` (next), `ArrowLeft` (previous), `Escape` (exit).
  - Close Button (`X`): Closes modal cleanly and returns to host page.
  - Content Verified: All 14 slides present with formal mathematical formulas, state tables, and architecture diagrams.
- **Result:** **PASS**
