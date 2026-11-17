# TraceGuard AI — Brand Audit
**Phase 19 Website Rebrand** · Generated 2026-11-17

---

## 1. Brand Identity Overview

| Field | Value |
|-------|-------|
| **Product name** | TraceGuard AI |
| **Category** | Network security software |
| **Tagline** | Network protocol state machine verification and hybrid intrusion detection platform that mathematically audits network traffic against formal automata. |
| **Style** | Quiet Sans Identities |
| **Symbol idea** | A Trace-line T whose crossbar loops back once into a clean state transition node |
| **Target audience** | Security and network engineering teams |
| **Deployment contexts** | App, Web |

---

## 2. Official Logo Asset Inventory

All logos live in `brand/logo/`. Every file is SVG (vector-first per brand rules).

| File | Dimensions | Use case |
|------|-----------|----------|
| `traceguard-ai-color.svg` | 4358 × 4358 (square) | Full icon mark — app icon, favicon, large standalone symbol |
| `traceguard-ai-horizontal-color.svg` | 733 × 229 | Nav bar, header, email header — icon left + wordmark right |
| `traceguard-ai-icon-color.svg` | 320 × 320 | Small icon contexts: 32–64 px favicon, app icon, mobile nav |
| `traceguard-ai-stacked-color.svg` | 733 × 229* | Stacked layout — icon above wordmark for square marketing lockups |
| `traceguard-ai-wordmark-color.svg` | Wordmark only | Text-heavy contexts where the mark would be too small to read |
| `traceguard-ai-mono.svg` | 4358 × 4358 | Single-color dark backgrounds (#111111 paths) |
| `traceguard-ai-inverse.svg` | 4358 × 4358 | Light or white backgrounds (paths inverted) |
| `traceguard-ai-reversed.svg` | 4358 × 4358 | Reversed-out placement (white on dark fill) |

> [!NOTE]
> `traceguard-ai-stacked-color.svg` shares the same `733 × 229` viewport as horizontal but routes the layout vertically — verify rendering in browser before final use.

### Mockups
`brand/mockups/` — browser tab and app icon mockups for reference sizing. Use `traceguard-ai-icon-color.svg` as the production source.

---

## 3. Logo Structure (from SVG analysis)

### Icon mark (the "T-state" symbol)
- **Shape**: Two-lobed form — a vertical column (the T-stem) and a horizontal arm with a notch forming a state-transition node
- **Fill**: Rich linear gradient `#081710 → #103A29 → #156244 → #168C62 → #10B981` (dark forest to emerald)
- **Overlay radial glows**: Three layered radial gradients add atmospheric depth:
  - Dark vignette (near-black `#030510`, 90% → 0% opacity)
  - Mid green (`#006342`, 80% → 0%)
  - Bright emerald highlight (`#34C58E`, 95% → 0%)
- **Effect**: The mark reads as a deep, luminous green — almost dimensional

### Wordmark "TraceGuard AI"
- **Font style**: Geometric sans-serif, weight ~500, wide letter-spacing
- **Color**: Solid `#3B82F6` (brand ink blue) on all color variants
- **Mono variant**: `#111111` (near-black) — for single-color print, emboss, cutout use

### Combined lockup (horizontal)
Icon mark (left) + wordmark (right), baseline-aligned. Generous clear space around both.

---

## 4. Color Palette (from brand.json)

### Official palette

| Token name | Hex | Role |
|-----------|-----|------|
| `primary` | `#0E131F` | Deep navy-black background, the product's "dark matter" |
| `ink` | `#3B82F6` | Blue — UI accent, wordmark, interactive elements, signal/protocol |
| `paper` | `#FFFFFF` | White — text on dark, inverse marks |
| `accent[0]` | `#10B981` | Emerald — ML/anomaly, trace paths, secondary CTA |

### Logo gradient stops (reference)
| Stop | Hex | Position |
|------|-----|----------|
| Darkest | `#081710` | 0% |
| Forest | `#103A29` | 25% |
| Mid green | `#156244` | 50% |
| Bright forest | `#168C62` | 75% |
| Emerald | `#10B981` | 100% |

### Semantic color extensions (design system)
Derived from the brand palette for website use:

| Semantic name | Hex | Meaning |
|--------------|-----|---------|
| `signal` | `#3B82F6` | FSM protocol states, network flow, primary action |
| `trace` | `#10B981` | ML anomaly paths, detection results, secondary |
| `threat` | `#ef4444` | Alerts, intrusion events, destructive actions |
| `warn` | `#f59e0b` | Warnings, rate limits, elevated risk |
| `success` | `#22c55e` | Clean states, baseline normal, resolved alerts |

---

## 5. Typography Specification

### Typeface
- **Primary**: Inter (variable, loaded via Google Fonts CDN)
- **System fallback stack**: `ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif`
- **OpenType features**: `cv11` (alternate digit 1), `ss03`
- **Global tracking**: `letter-spacing: -0.011em` on body
- **Rendering**: `-webkit-font-smoothing: antialiased`

### Type scale

| Level | Size | Line-height | Weight | Tracking | Notes |
|-------|------|-------------|--------|----------|-------|
| Display XL | 76px | 1.02 | 500 | −0.035em | Hero headlines, one-word impact |
| Display L | 56px | 1.02 | 500 | −0.035em | Section headers |
| Display M | 40px | 1.02 | 500 | −0.035em | Sub-section, card large |
| Title | 24px | 1.3 | 500 | −0.02em | Card titles, modal headings |
| Card title | 16px | 1.4 | 500 | 0 | In-card headings |
| Lede | 18px | 1.55 | 400 | 0 | Intro paragraphs, section descriptions |
| Body | 16px | 1.5 | 400 | 0 | Main reading text |
| Small | 14px | 1.4 | 400 | 0 | Labels, captions, metadata |
| Caption | 13px | 1.3 | 400 | 0 | Fine print, timestamps |

### Display utility
Tight tracking and compressed leading for large type — applied with the `.display` CSS class.

---

## 6. Icon Style Rules

From `brand.json → rules` and `brand.json → icons`:

1. **Line icons only** — `look: "line"`, default size 24 px. Lucide Icons (already in codebase) fits this spec exactly.
2. **Single color** — icons take `currentColor` from the page; never hard-code a fill inside an icon.
3. **No text inside icons or marks** — the symbol must read without labels.
4. **Vector first** — SVG for every mark, icon, and illustration. No icon fonts, no PNG fallbacks at display sizes.
5. **Illustration style**: `vector_illustration` — clean geometric vector, no photorealism inside icons/marks.

---

## 7. Brand Voice Guidelines

### Tone
TraceGuard AI operates in the **network security / formal verification** space. The brand voice is:

- **Precise, not verbose** — write as engineers write: direct sentences, no filler. If a word doesn't add information, cut it.
- **Confident, not arrogant** — the product makes strong guarantees (mathematical verification). State them plainly.
- **Technical without being impenetrable** — security engineers and network architects are the audience. Use correct terminology (FSM, automata, state machine, anomaly, heuristic). Do not dumb it down, but always define on first use.
- **Calm under pressure** — threat detection is high-stakes. The UI copy should feel composed, not alarming.

### Writing rules
1. Lead with the outcome, not the mechanism: "Catch protocol anomalies before they escalate" not "Uses finite state machines to detect…"
2. Use active voice for all CTAs: "Deploy" not "Deployment can be initiated."
3. Numbers over adjectives in security copy: "Inspect 40,000 packets/s" beats "ultra-fast inspection."
4. Avoid: "enterprise-grade", "next-generation", "cutting-edge", "best-in-class", "AI-powered" (the name already says AI).
5. Headline convention: Title Case for Display XL/L, Sentence case for everything else.
6. CTA hierarchy: Primary = action verb ("Deploy", "Explore docs", "Start free trial"); Secondary = exploratory ("See how it works", "View architecture").

### Naming conventions
- Product: **TraceGuard AI** (always two words + AI, never "TraceGuard", never "Traceguard")
- Module names: FSM Engine, ML Detector, Packet Inspector, Threat Console
- Avoid: "platform" as the leading noun; prefer "system", "tool", or the product name directly

---

## 8. Brand Anti-patterns (Do Not)

| ❌ Avoid | ✅ Instead |
|---------|----------|
| Orange/fire color scheme | Deep navy-black + blue + emerald |
| Light backgrounds on the main site | Dark theme throughout (`#000` / `#060810`) |
| Compressed or distorted logo | Use SVG at any scale; never rasterize below 32px |
| Icon mark without clear space | Min 16px clear space on all sides |
| Hard-coded icon colors | `currentColor` only |
| Text inside the icon mark | The symbol stands alone |
| "Tidewell Fusion" or fusion-energy references | TraceGuard AI — network security |
| Plasma/fire gradient themes | Signal (blue) / Trace (emerald) / Threat (red) |
