# TraceGuard AI — Phase 12 Visual QA & Brand Audit Screenshot Index

This document catalogues all 26 verification screenshots captured via headless browser automation across all 11 application routes and 6 standard device viewports.

---

## 1. Viewport Matrix Specifications

| Identifier | Dimensions | Device Category | Purpose |
|---|---|---|---|
| `desktop_1920x1080` | 1920 × 1080 | Wide Desktop / SOC Wall | Max-width containment, grid expansion, chart readability |
| `desktop_1440x900` | 1440 × 900 | Standard Workstation | Primary desktop layout baseline, sidebar + topbar alignment |
| `tablet_1024x768` | 1024 × 768 | Landscape Tablet | Layout collapse threshold, navigation visibility |
| `tablet_768x1024` | 768 × 1024 | Portrait Tablet | Responsive breakpoint transition, table scrolling |
| `mobile_390x844` | 390 × 844 | iPhone 12/13/14/15 | Standard modern mobile viewport, mobile drawer navigation |
| `mobile_360x800` | 360 × 800 | Compact Android | Minimum supported mobile width, zero horizontal overflow |

---

## 2. Screenshot Catalogue

All screenshots are stored under `qa/screenshots/`.

| File Path | Route | Viewport | Validation Targets | Visual Quality Verdict |
|---|---|---|---|---|
| `qa/screenshots/dashboard_desktop_1440x900.png` | `/` | 1440 × 900 | Paper-white canvas (`#F8FAFC`), Deep Ink text (`#0E131F`), KPI cards, Recharts timeline & donut | **PASS** — Crisp, high-contrast, clean 8pt rhythm |
| `qa/screenshots/dashboard_desktop_1920x1080.png` | `/` | 1920 × 1080 | Max-width 7xl container alignment, header bar elevation | **PASS** — Clean centered layout, no stretching |
| `qa/screenshots/dashboard_tablet_1024x768.png` | `/` | 1024 × 768 | Desktop sidebar collapse, 2-column KPI grid | **PASS** — Flawless flex adaptation |
| `qa/screenshots/dashboard_tablet_768x1024.png` | `/` | 768 × 1024 | Single-column chart layout, hamburger drawer toggle | **PASS** — Smooth vertical rhythm |
| `qa/screenshots/dashboard_mobile_390x844.png` | `/` | 390 × 844 | Full mobile navigation, KPI card vertical stack, touch targets | **PASS** — No horizontal overflow, touch targets $\ge 44\text{px}$ |
| `qa/screenshots/dashboard_mobile_360x800.png` | `/` | 360 × 800 | Narrowest supported viewport, typography wrapping | **PASS** — Zero truncation, legible labels |
| `qa/screenshots/automata_lab_desktop_1440x900.png` | `/automata` | 1440 × 900 | ReactFlow 9-state DFA rendering, transition table, symbol chips | **PASS** — State nodes clean, edge labels high contrast |
| `qa/screenshots/automata_lab_mobile_390x844.png` | `/automata` | 390 × 844 | Mobile ReactFlow container, sequence player touch controls | **PASS** — Graph zoom/pan responsive, controls stack vertically |
| `qa/screenshots/protocol_explorer_desktop_1440x900.png` | `/protocol` | 1440 × 900 | Modbus/HTTP protocol session inspector, live trace execution | **PASS** — Tokenized edge styles, clean execution timeline |
| `qa/screenshots/protocol_explorer_mobile_390x844.png` | `/protocol` | 390 × 844 | Protocol trace cards, single-column validation logs | **PASS** — No overflow, responsive panels |
| `qa/screenshots/live_monitor_desktop_1440x900.png` | `/monitor` | 1440 × 900 | Live telemetry stream, event feed table, streaming status pill | **PASS** — High-density monospace table, clean headers |
| `qa/screenshots/live_monitor_mobile_390x844.png` | `/monitor` | 390 × 844 | Event feed mobile scroll, status indicators | **PASS** — Horizontal table scroll container intact |
| `qa/screenshots/threats_desktop_1440x900.png` | `/threats` | 1440 × 900 | Threat investigation table, severity filter pills, alert drawer | **PASS** — Restrained status colors, accessible contrast |
| `qa/screenshots/threats_mobile_390x844.png` | `/threats` | 390 × 844 | Filter chip wrap, mobile threat card listing | **PASS** — Touch-friendly filters, readable summaries |
| `qa/screenshots/detection_lab_desktop_1440x900.png` | `/lab` | 1440 × 900 | 3-engine benchmark comparison (FSM, ML, Hybrid), Recharts bar chart | **PASS** — Recharts tooltip tokenized, benchmark table clear |
| `qa/screenshots/detection_lab_mobile_390x844.png` | `/lab` | 390 × 844 | Multi-engine selector tabs, stacked benchmark metrics | **PASS** — Adaptive tabs, clean chart scaling |
| `qa/screenshots/datasets_desktop_1440x900.png` | `/datasets` | 1440 × 900 | Dataset management table, CSV upload dropzone, partition pills | **PASS** — Crisp borders, accessible action buttons |
| `qa/screenshots/datasets_mobile_390x844.png` | `/datasets` | 390 × 844 | Mobile dropzone, dataset cards stack | **PASS** — Form controls responsive, no layout shifts |
| `qa/screenshots/settings_desktop_1440x900.png` | `/settings` | 1440 × 900 | Hybrid weight sliders, violation floor inputs, account profile | **PASS** — Focus rings, Emil motion feedback, clear typography |
| `qa/screenshots/settings_mobile_390x844.png` | `/settings` | 390 × 844 | Mobile form controls, slider touch areas | **PASS** — Full-width inputs, clean spacing |
| `qa/screenshots/landing_desktop_1440x900.png` | `/landing` | 1440 × 900 | Public landing page, official SVG logo, hero section, CTA buttons | **PASS** — Premium typography, Quiet Sans identity |
| `qa/screenshots/landing_mobile_390x844.png` | `/landing` | 390 × 844 | Mobile hero presentation, feature cards stack, sticky mobile nav | **PASS** — Mobile menu accessible, clean hero typography |
| `qa/screenshots/login_desktop_1440x900.png` | `/login` | 1440 × 900 | SOC sign-in form, official brand icon, input states | **PASS** — Centered card, crisp inputs, accessible links |
| `qa/screenshots/login_mobile_390x844.png` | `/login` | 390 × 844 | Mobile authentication form, full-width button | **PASS** — Mobile keyboard friendly, no clipping |
| `qa/screenshots/signup_desktop_1440x900.png` | `/signup` | 1440 × 900 | Workspace registration, organization input, password rules | **PASS** — High-contrast labels, clear validation text |
| `qa/screenshots/signup_mobile_390x844.png` | `/signup` | 390 × 844 | Mobile registration form | **PASS** — Clean vertical flow, accessible inputs |

---

## 3. Visual Defect Resolution Summary

- **Identified Defect 1**: Default root was dark obsidian (`#0A0D14`), contradicting official brand specification of 60% white paper background.
  - **Resolution**: Refactored `:root` in `design-system.css` to light-first (`--tg-bg-base: #FFFFFF`, `--tg-bg-root: #F8FAFC`). Dark mode preserved under `[data-theme="dark"]`.
- **Identified Defect 2**: Recharts tooltips contained hardcoded dark backgrounds (`#141B2B`) and white borders (`rgba(255,255,255,0.12)`).
  - **Resolution**: Replaced with dynamic CSS tokens (`var(--tg-bg-surface)` and `var(--tg-border-default)`).
- **Identified Defect 3**: ReactFlow edges and background in `AutomataLab.jsx` and `ProtocolExplorer.jsx` used hardcoded dark alpha lines.
  - **Resolution**: Bound to `var(--tg-border-strong)` and `var(--tg-border-subtle)` for crisp contrast in light mode.
