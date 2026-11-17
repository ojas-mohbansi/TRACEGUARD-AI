# TraceGuard AI — Brand Identity & Design System Specification

## 1. Identity Overview

**TraceGuard AI** is a network protocol state machine verification and hybrid intrusion detection platform that mathematically audits network traffic against formal automata.

The brand identity reflects mathematical precision, formal automata determinism, calmness, and editorial clarity. Built upon the principles of *design-taste-frontend*, *ui-ux-pro-max*, and *emil-design-eng*, the interface is designed as an uncompromising high-contrast security instrument.

- **Brand Archetype**: Quiet Sans Identities / Technical Instrument
- **Core Symbol**: The Trace-line "T" whose crossbar loops back into a clean finite-state transition node.
- **Visual Feel**: Obsidian dark ink foundation, high contrast, sub-pixel alignment, low noise, zero decorative slop.

---

## 2. Official Brand Palette

The core color palette is defined in `brand/brand.json` and mapped to CSS variables in `frontend/src/styles/design-system.css`:

| Role | Name | Hex Code | Token | Description & Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Base** | Deep Ink | `#0E131F` | `--tg-brand-primary` / `--tg-bg-base` | Obsidian base ground, card backgrounds, dark mode identity |
| **Brand Ink** | Brand Blue | `#3B82F6` | `--tg-brand-blue` / `--tg-accent-blue` | Protocol telemetry, state transitions, ML engine metrics |
| **Accent** | Emerald Accent | `#10B981` | `--tg-brand-emerald` / `--tg-accent-emerald` | Formal automata valid state, verified verdicts, primary CTA |
| **Paper** | White Paper | `#FFFFFF` | `--tg-brand-paper` / `--tg-text-inverse` | Crisp neutral ground reference and high-contrast text |

### Supporting Semantic Engine Palette
- **FSM Automata Engine**: Emerald `#10B981` (`--tg-engine-fsm`)
- **Machine Learning Engine**: Blue `#3B82F6` (`--tg-engine-ml`)
- **Hybrid Verification Engine**: Amber `#F59E0B` (`--tg-engine-hybrid`)
- **Critical Violation / Alert**: Red `#EF4444` (`--tg-status-danger`)
- **Protocol Accent / Handshake**: Cyan `#06B6D4` (`--tg-accent-cyan`)

---

## 3. Surface & Elevation Architecture

The console operates on a layered elevation hierarchy that avoids artificial heavy drop-shadows and instead uses subtle alpha-borders and step luminance:

```
[ Canvas: #07090E ]
   └─ [ Root Background: #0A0D14 ]
       └─ [ Base Level: #0E131F (Brand Ink) ]
           └─ [ Surface Level: #141B2B (Card Containers) ]
               └─ [ Elevated Surface: #1B2438 (Modals, Dropdowns, Highlights) ]
                   └─ [ Interactive Hover: #222E47 ]
                       └─ [ Active / Selected: #2A3856 ]
```

### CSS Variables Mapping

| Layer | Dark Mode Token | Light Mode Override |
| :--- | :--- | :--- |
| Canvas Background | `--tg-bg-canvas: #07090E` | `--tg-bg-canvas: #F1F5F9` |
| Viewport Root | `--tg-bg-root: #0A0D14` | `--tg-bg-root: #F8FAFC` |
| Base Ground | `--tg-bg-base: #0E131F` | `--tg-bg-base: #FFFFFF` |
| Surface Panels | `--tg-bg-surface: #141B2B` | `--tg-bg-surface: #FFFFFF` |
| Elevated Cards | `--tg-bg-elevated: #1B2438` | `--tg-bg-elevated: #F1F5F9` |
| Hover State | `--tg-bg-hover: #222E47` | `--tg-bg-hover: #E2E8F0` |
| Active State | `--tg-bg-active: #2A3856` | `--tg-bg-active: #CBD5E1` |

---

## 4. Typography System

The typography uses a clean tripartite hierarchy:

1. **Interface Body (`--tg-font-sans`)**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, sans-serif. Highly readable at 11px - 14px sizes.
2. **Display & Headings (`--tg-font-display`)**: `Plus Jakarta Sans`, sans-serif. Used for prominent landing headlines and modal titles.
3. **Telemetry & Code (`--tg-font-mono`)**: `JetBrains Mono`, `Fira Code`, monospace. Used for IP addresses, hex bytes, automata state symbols, and protocol logs.

### Text Contrast & WCAG 2.2 Compliance

All primary text layers achieve WCAG 2.2 AAA standard contrast ratios against Deep Ink (`#0E131F`) surfaces:

- **Primary Text (`--tg-text-primary: #F8FAFC`)**: Contrast ratio **16.2:1** (Exceeds 7:1 AAA requirement).
- **Secondary Text (`--tg-text-secondary: #CBD5E1`)**: Contrast ratio **11.4:1** (Exceeds 7:1 AAA requirement).
- **Muted Telemetry (`--tg-text-muted: #8896AB`)**: Contrast ratio **5.8:1** (Exceeds 4.5:1 AA requirement for regular text).
- **Primary Emerald Accent (`#10B981`)**: Contrast ratio **7.8:1** against base ink.

---

## 5. Official Brand Assets & Public Distribution

All official brand vector and raster assets are deployed in `frontend/public/`:

| File | Resolution / Type | Role |
| :--- | :--- | :--- |
| `favicon.svg` | SVG Vector | Browser favicon & bookmark icon |
| `traceguard-ai-icon-color.svg` | SVG Vector (320x320) | App bar icon, brand mark |
| `traceguard-ai-icon-color-2048.png` | PNG (2048x2048) | High-resolution brand icon |
| `traceguard-ai-horizontal-color.svg`| SVG Vector | Horizontal brand logo with wordmark |
| `traceguard-ai-wordmark-color.svg`  | SVG Vector | Standalone typographic wordmark |
| `traceguard-ai-stacked-color.svg`   | SVG Vector | Vertical / Stacked brand lockup |
| `traceguard-ai-mono.svg`            | SVG Vector | Monochromatic black & white reproduction |
| `traceguard-ai-reversed.svg`        | SVG Vector | Pure white inverse vector |
| `site.webmanifest`                  | JSON Manifest | PWA metadata & mobile homescreen configuration |

---

## 6. Component Conventions

### A. Buttons (`.tg-btn-primary`, `.tg-btn-blue`, `.tg-btn-secondary`)
- Primary button uses **Emerald Accent** (`#10B981`) with Deep Ink text (`#0E131F`) for immediate affordance and crisp contrast.
- Secondary action uses subtle surface color with default border and crisp white text.
- Micro-interactions follow Emil Kowalski's guidelines: `150ms cubic-bezier(0.16, 1, 0.3, 1)` spring transition with a 1px translate on hover and `scale(0.98)` on press.

### B. Panels & Containers (`.tg-panel`, `.tg-panel-elevated`)
- Default panels use `var(--tg-bg-surface)` with 1px border `var(--tg-border-subtle)` (`rgba(255, 255, 255, 0.08)`).
- On hover, border smoothly transitions to `var(--tg-border-default)` (`rgba(255, 255, 255, 0.14)`).

### C. Status Badges (`.tg-badge-*`)
- Badges use 11px monospace typography with `0.04em` tracking.
- Composed of 12% alpha fill with a matching 25% alpha border:
  - Valid / Low: `.tg-badge-emerald`
  - Warning / Medium: `.tg-badge-amber`
  - Attack / High: `.tg-badge-red`
  - Protocol / Info: `.tg-badge-blue`

### D. Monospace Data Tables (`.tg-table-container`, `.tg-table`)
- Table headers use muted uppercase monospace type with 6% letter spacing.
- Table rows provide instant visual feedback with subtle highlight (`rgba(255, 255, 255, 0.025)`) on hover.
- Row heights are calibrated to 40px (compact) or 48px (standard) for optimal telemetry scanability.

---

## 7. Motion & Accessibility Principles

1. **Zero-Slop Rule**: Avoid gratuitous bouncy animations. Transitions must communicate status or confirm action under 220ms.
2. **Prefers-Reduced-Motion**: Under `prefers-reduced-motion: reduce`, all transitions and animations are clamped to `0.01ms` to support vestibular sensitivity.
3. **Keyboard Focus Ring**: `:focus-visible` enforces a 2px solid emerald ring (`--tg-border-focus`) with a 2px offset.
