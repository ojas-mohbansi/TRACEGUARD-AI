# TraceGuard AI — Design System
**Phase 19 Website Rebrand** · Generated 2026-11-17

> [!IMPORTANT]
> This document is the source of truth for the new CSS token specification. When updating `website/src/styles.css`, replace the existing `@theme` block with the one in §1 and update `website/src/lib/tokens.ts` to match §2.

---

## 1. Complete CSS Token Specification

### New `@theme` block for `website/src/styles.css`

```css
@import 'tailwindcss';

/*
  TraceGuard AI design tokens.
  Dark-first software/security tool. Two semantic light sources:
    signal (blue #3B82F6)  — protocol state machines, network flow, primary action
    trace  (emerald #10B981) — ML anomaly paths, detection results, secondary
  Plus threat (red) and warn (amber) for status.

  Text is always AA-compliant on its surface.
  Every rounded rectangle is a squircle (corner-shape: squircle in base layer).
*/
@theme {
  /* ── Typography ──────────────────────────────────────────── */
  --font-sans: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif;

  /* ── Surfaces ────────────────────────────────────────────── */
  --color-bg:        #000000;    /* Page root — absolute black */
  --color-bg-deep:   #030508;    /* Behind hero gradients */
  --color-surface:   #0a0d16;    /* Cards, panels on bg */
  --color-surface-2: #0e1420;    /* Elevated cards, nested panels */
  --color-raised:    #141928;    /* Tooltips, popovers, modals */
  --color-overlay:   #1a2033;    /* Highest elevation surface */

  /* ── Borders ─────────────────────────────────────────────── */
  --color-line:        rgb(255 255 255 / 0.08);   /* Default card/panel border */
  --color-line-mid:    rgb(255 255 255 / 0.11);   /* Slightly visible dividers */
  --color-line-strong: rgb(255 255 255 / 0.16);   /* Hover/focus borders */

  /* ── Text hierarchy ──────────────────────────────────────── */
  --color-fg:    #ffffff;   /* Primary — headlines, strong labels */
  --color-soft:  #d6dae2;   /* Body copy, secondary labels */
  --color-muted: #9ca3af;   /* Supporting text, placeholders */
  --color-faint: #6b7280;   /* Timestamps, captions, disabled */

  /* ── Signal (blue) — FSM / protocol / primary action ─────── */
  --color-signal:        #3B82F6;   /* Brand ink — primary CTA, links, protocol */
  --color-signal-soft:   #60a5fa;   /* Hover state, text on dark for AA */
  --color-signal-dim:    #1d4ed8;   /* Pressed state, deep accent */
  --color-signal-wash:   rgb(59 130 246 / 0.12);  /* Subtle tinted bg */
  --color-signal-glow:   rgb(59 130 246 / 0.35);  /* Box-shadow glow */
  --color-signal-border: rgb(59 130 246 / 0.30);  /* Tinted card borders */

  /* ── Trace (emerald) — ML / anomaly / secondary ──────────── */
  --color-trace:        #10B981;   /* Brand accent — anomaly, ML, secondary CTA */
  --color-trace-soft:   #34d399;   /* Hover, text on dark */
  --color-trace-dim:    #059669;   /* Pressed, deep accent */
  --color-trace-wash:   rgb(16 185 129 / 0.10);
  --color-trace-glow:   rgb(16 185 129 / 0.30);
  --color-trace-border: rgb(16 185 129 / 0.25);

  /* ── Threat (red) — alerts / intrusion events ────────────── */
  --color-threat:        #ef4444;
  --color-threat-soft:   #f87171;
  --color-threat-dim:    #b91c1c;
  --color-threat-wash:   rgb(239 68 68 / 0.10);
  --color-threat-glow:   rgb(239 68 68 / 0.30);
  --color-threat-border: rgb(239 68 68 / 0.25);

  /* ── Warn (amber) — warnings / rate limits ───────────────── */
  --color-warn:        #f59e0b;
  --color-warn-soft:   #fbbf24;
  --color-warn-dim:    #b45309;
  --color-warn-wash:   rgb(245 158 11 / 0.10);
  --color-warn-border: rgb(245 158 11 / 0.25);

  /* ── Success (green) — clean state / resolved ────────────── */
  --color-ok:        #22c55e;
  --color-ok-soft:   #4ade80;
  --color-ok-wash:   rgb(34 197 94 / 0.10);
  --color-ok-border: rgb(34 197 94 / 0.25);

  /* ── Border radius (squircle scale) ──────────────────────── */
  --radius-control: 999px;   /* Pill buttons, chips, badges */
  --radius-field:   14px;    /* Inputs, selects, small cards */
  --radius-card-sm: 20px;    /* Compact cards */
  --radius-card:    28px;    /* Standard cards */
  --radius-panel:   32px;    /* Section panels, modals */
  --radius-xl:      40px;    /* Hero panels, feature spotlights */

  /* ── Shadows ─────────────────────────────────────────────── */
  --shadow-card:          0 40px 80px -30px rgb(0 0 0 / 0.85);
  --shadow-panel:         0 60px 120px -40px rgb(0 0 0 / 0.9);
  --shadow-glow-signal:   0 0 120px -10px var(--color-signal-glow);
  --shadow-glow-trace:    0 0 120px -10px var(--color-trace-glow);
  --shadow-glow-threat:   0 0 80px -10px var(--color-threat-glow);

  /* ── Motion easing ───────────────────────────────────────── */
  --ease-out:    cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Overshoot spring */

  /* ── Named animations ────────────────────────────────────── */
  --animate-pulse-signal: pulse-signal 4.8s ease-in-out infinite;
  --animate-pulse-trace:  pulse-trace  6s   ease-in-out infinite;
  --animate-float:        float        8s   ease-in-out infinite;
  --animate-shimmer:      shimmer      1.6s linear      infinite;
  --animate-spin-slow:    spin         1s   linear      infinite;
  --animate-scan:         scan         6s   ease-in-out infinite;
  --animate-flicker:      flicker      3s   ease-in-out infinite;

  @keyframes pulse-signal {
    0%, 100% { opacity: 0.80; transform: scale(1);    }
    50%       { opacity: 1;    transform: scale(1.04); }
  }
  @keyframes pulse-trace {
    0%, 100% { opacity: 0.75; transform: scale(1);    }
    50%       { opacity: 1;    transform: scale(1.03); }
  }
  @keyframes float {
    0%, 100% { transform: translateY(0);   }
    50%       { transform: translateY(-6px); }
  }
  @keyframes shimmer {
    from { background-position: -200% 0; }
    to   { background-position:  200% 0; }
  }
  @keyframes scan {
    0%, 100% { transform: translateX(-30%); opacity: 0.4; }
    50%       { transform: translateX( 30%); opacity: 0.9; }
  }
  @keyframes flicker {
    0%, 100% { opacity: 1;    }
    92%       { opacity: 1;    }
    93%       { opacity: 0.6;  }
    94%       { opacity: 1;    }
    96%       { opacity: 0.75; }
    97%       { opacity: 1;    }
  }
}
```

---

## 2. Updated `tokens.ts` Color Groups

```typescript
export const colorGroups = [
  {
    name: 'Surfaces',
    colors: [
      { name: 'bg',        hex: '#000000' },
      { name: 'bg-deep',   hex: '#030508' },
      { name: 'surface',   hex: '#0a0d16' },
      { name: 'surface-2', hex: '#0e1420' },
      { name: 'raised',    hex: '#141928' },
      { name: 'overlay',   hex: '#1a2033' },
    ],
  },
  {
    name: 'Text',
    colors: [
      { name: 'fg',    hex: '#ffffff' },
      { name: 'soft',  hex: '#d6dae2' },
      { name: 'muted', hex: '#9ca3af' },
      { name: 'faint', hex: '#6b7280' },
    ],
  },
  {
    name: 'Signal (Blue / FSM)',
    colors: [
      { name: 'signal',        hex: '#3B82F6' },
      { name: 'signal-soft',   hex: '#60a5fa' },
      { name: 'signal-dim',    hex: '#1d4ed8' },
      { name: 'signal-wash',   hex: 'rgb(59 130 246 / 0.12)' },
    ],
  },
  {
    name: 'Trace (Emerald / ML)',
    colors: [
      { name: 'trace',        hex: '#10B981' },
      { name: 'trace-soft',   hex: '#34d399' },
      { name: 'trace-dim',    hex: '#059669' },
      { name: 'trace-wash',   hex: 'rgb(16 185 129 / 0.10)' },
    ],
  },
  {
    name: 'Status',
    colors: [
      { name: 'threat',    hex: '#ef4444' },
      { name: 'warn',      hex: '#f59e0b' },
      { name: 'ok',        hex: '#22c55e' },
    ],
  },
]
```

---

## 3. Color Semantic Groups & Meaning

```
SURFACES          Used for             Token(s)
─────────────────────────────────────────────────
Page root         Body background      --color-bg
Behind hero       Gradient base        --color-bg-deep
Cards / panels    Surface 1            --color-surface
Nested cards      Surface 2            --color-surface-2
Tooltips          Elevated             --color-raised
Modals            Highest elevation    --color-overlay

SIGNAL BLUE  (#3B82F6 family)
─────────────────────────────────────────────────
Primary CTA buttons                   --color-signal
Hover / active state                  --color-signal-soft
Pressed / deep accent                 --color-signal-dim
Tinted card backgrounds               --color-signal-wash
Glow effects around signal elements   --color-signal-glow
Tinted card borders                   --color-signal-border

TRACE EMERALD  (#10B981 family)
─────────────────────────────────────────────────
Secondary CTAs, ML/anomaly results    --color-trace
Hover                                 --color-trace-soft
Pressed                               --color-trace-dim
Tinted backgrounds                    --color-trace-wash

THREAT RED  (#ef4444 family)
─────────────────────────────────────────────────
Intrusion events, alerts, errors      --color-threat
Text / icon on dark for readability   --color-threat-soft
Serious/critical state highlight      --color-threat-dim

WARN AMBER  (#f59e0b family)
─────────────────────────────────────────────────
Elevated risk, rate limiting          --color-warn
Softer warning badge text             --color-warn-soft

OK GREEN  (#22c55e family)
─────────────────────────────────────────────────
Clean baseline, resolved alerts       --color-ok
Badge text on dark                    --color-ok-soft
```

---

## 4. Typography Scale

```
CLASS          SIZE   LH     WEIGHT   TRACKING    UTILITY CLASS
──────────────────────────────────────────────────────────────
Display XL     76px   1.02   500      −0.035em    display text-[76px]
Display L      56px   1.02   500      −0.035em    display text-[56px]
Display M      40px   1.02   500      −0.035em    display text-[40px]
Title          24px   1.3    500      −0.02em     text-[24px] font-medium tracking-[-0.02em]
Card title     16px   1.4    500      0           text-[16px] font-medium
Lede           18px   1.55   400      0           text-[18px] leading-[1.55] text-muted
Body           16px   1.5    400      0           text-[16px] leading-[1.5] text-soft
Small          14px   1.4    400      0           text-[14px] text-muted
Caption        13px   1.3    400      0           text-[13px] text-faint
```

The `.display` utility (defined in `@layer utilities`) applies:
```css
font-weight: 500;
letter-spacing: -0.035em;
line-height: 1.02;
```

---

## 5. Spacing Scale

| px | Tailwind equiv | Use |
|----|---------------|-----|
| 4  | `p-1`  | Icon inner padding |
| 8  | `p-2`  | Tight spacing, inline |
| 12 | `p-3`  | Label padding |
| 16 | `p-4`  | Standard component padding |
| 20 | `p-5`  | Card inner padding (narrow) |
| 24 | `p-6`  | Card inner padding (standard) |
| 32 | `p-8`  | Section sub-spacing |
| 40 | `p-10` | Card outer margin |
| 56 | `p-14` | Section vertical padding (tight) |
| 80 | `p-20` | Section vertical padding (standard) |
| 128 | `p-32` | Hero padding |

---

## 6. Component Specifications

### 6.1 Buttons

```
VARIANT        BG                TEXT          BORDER               HOVER
──────────────────────────────────────────────────────────────────────────
Primary        --color-signal    white         none                 signal-dim bg + slight scale(0.98) on active
Secondary      transparent       signal-soft   signal-border (1px)  signal-wash bg
Ghost          transparent       muted         none                 surface bg
Danger         threat-wash       threat-soft   threat-border (1px)  threat / 15% bg
Trace          trace-wash        trace-soft    trace-border (1px)   trace / 15% bg
```

- **Border radius**: `--radius-control` (pill) for primary/secondary CTAs; `--radius-field` for inline actions
- **Padding**: `12px 24px` (standard), `8px 16px` (small), `16px 32px` (large)
- **Press animation**: `transform: scale(0.97)` at 200ms `--ease-out`
- **Font**: 15px, weight 500, slight tracking (−0.01em)
- **Focus ring**: `2px solid --color-signal-soft`, `outline-offset: 3px`

### 6.2 Cards

```
VARIANT        SURFACE             BORDER          SHADOW         RADIUS
────────────────────────────────────────────────────────────────────────
Default        surface             line            shadow-card    radius-card
Elevated       surface-2           line-mid        shadow-panel   radius-card
Signal-tinted  signal-wash bg      signal-border   shadow-card    radius-card
Trace-tinted   trace-wash bg       trace-border    shadow-card    radius-card
Threat         threat-wash bg      threat-border   none           radius-card-sm
```

- Use `position: relative` + `.depth` utility (inset edge highlight) on all cards
- Inner padding: `24px` standard, `32px` for feature cards

### 6.3 Badges / Status chips

```
BADGE     BG             TEXT           Border
────────────────────────────────────────────────
Signal    signal-wash    signal-soft    signal-border
Trace     trace-wash     trace-soft     trace-border
Threat    threat-wash    threat-soft    threat-border
Warn      warn-wash      warn-soft      warn-border
Ok        ok-wash        ok-soft        ok-border
Neutral   line           muted          line-mid
```

- **Shape**: `radius-control` (pill)
- **Padding**: `4px 10px`
- **Font**: 12px, weight 500, `letter-spacing: 0.02em`, uppercase for single-word labels

### 6.4 Navigation (top bar)

```css
/* Nav bar spec */
position: fixed;
top: 0; left: 0; right: 0;
height: 60px;
background: rgb(0 0 0 / 0.80);
backdrop-filter: blur(16px) saturate(180%);
border-bottom: 1px solid var(--color-line);
z-index: 100;
```

- **Logo**: `traceguard-ai-horizontal-color.svg`, max-height 28px, left-aligned
- **Nav links**: 15px, weight 450, `--color-muted` default → `--color-fg` hover, 150ms transition
- **Active link**: `--color-signal-soft` with a 2px signal-colored underline
- **CTA button**: Primary (signal) or outline variant, right-aligned
- **Mobile**: Collapse to hamburger at < 768px; sheet/drawer from right

### 6.5 Footer

```
Layout: 4-column grid (desktop), 2-col (tablet), 1-col (mobile)
Background: --color-bg (matches page root — seamless)
Top border: 1px solid --color-line
Padding: 80px top, 48px bottom
```

- **Logo**: Icon mark only (`traceguard-ai-icon-color.svg`) at 32px + wordmark at 15px
- **Column heads**: 12px, weight 600, `--color-muted`, uppercase, `letter-spacing: 0.08em`
- **Links**: 14px, `--color-faint` default → `--color-soft` hover
- **Social icons**: Lucide, 18px, `--color-muted` → `--color-soft`
- **Bottom row**: legal links + copyright in 13px `--color-faint`; inline with legal links left, copyright right

### 6.6 Diagram / Protocol state machine visualization

Diagrams visualize FSM states and packet flows. Style guide:

```
Node type        Fill              Border          Text
────────────────────────────────────────────────────────────
FSM state        surface-2         signal-border   fg
Active state     signal-wash       signal (2px)    signal-soft
Anomaly state    trace-wash        trace-border    trace-soft
Threat state     threat-wash       threat (2px)    threat-soft
Entry/exit       overlay           line-strong     muted
```

- **Edges/arcs**: 1px solid `--color-line-mid`; active/trace path uses `--color-trace` at 60% opacity
- **Labels**: 12px, weight 500, `--color-muted`
- **Background**: `--color-surface` with optional `.grain` texture overlay at 6% opacity
- **Radius**: `--radius-field` for state nodes (rounded rectangle)

### 6.7 Code blocks / Terminal output

```css
background: var(--color-surface);
border: 1px solid var(--color-line-mid);
border-radius: var(--radius-field);
font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
font-size: 13px;
line-height: 1.65;
color: var(--color-soft);
padding: 20px 24px;
```

- **Keyword highlight**: `--color-signal-soft`
- **String highlight**: `--color-trace-soft`
- **Comment**: `--color-faint`
- **Alert/warning in terminal**: `--color-threat-soft` / `--color-warn-soft`

---

## 7. Motion System

| Name | Duration | Easing | Usage |
|------|----------|--------|-------|
| reveal | 0.8s | `--ease-out` | Section/card scroll entrance, rise 18px |
| press | 200ms | `--ease-out` | Button active state, scale 0.97 |
| hover | 150ms | `--ease-out` | Link/icon hover transitions |
| pulse-signal | 4.8s ∞ | ease-in-out | Hero glow core (blue) |
| pulse-trace | 6s ∞ | ease-in-out | Secondary glow (emerald) |
| float | 8s ∞ | ease-in-out | Floating diagram elements |
| shimmer | 1.6s ∞ | linear | Skeleton loading states |
| scan | 6s ∞ | ease-in-out | Background packet-scan FX |
| flicker | 3s ∞ | ease-in-out | Terminal cursor, subtle cyber aesthetic |

### Reduced motion
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 8. Utility Classes

```css
/* Depth: inset edge highlight drawn over children (applied to cards/panels) */
@utility depth {
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    pointer-events: none;
    box-shadow:
      inset 0 0 0 1px var(--depth-edge, rgb(255 255 255 / 0.10)),
      inset 0 1px 0   var(--depth-highlight, rgb(255 255 255 / 0.14));
  }
}

/* Display type: tight tracking + compressed leading */
@utility display {
  font-weight: 500;
  letter-spacing: -0.035em;
  line-height: 1.02;
}

/* Skeleton shimmer for loading states */
@utility skeleton {
  background: linear-gradient(
    90deg,
    rgb(255 255 255 / 0.04) 25%,
    rgb(255 255 255 / 0.09) 50%,
    rgb(255 255 255 / 0.04) 75%
  );
  background-size: 200% 100%;
  animation: var(--animate-shimmer);
}

/* Soft film grain over gradient hero sections */
@utility grain {
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
  opacity: 0.06;
  mix-blend-mode: overlay;
}

/* Signal (blue) gradient page wash — behind hero sections */
@utility signal-wash-bg {
  background: linear-gradient(180deg,
    #000 0%,
    #03061a 40%,
    #071233 75%,
    #0e2060 100%
  );
}

/* Trace (emerald) gradient wash — behind ML/anomaly sections */
@utility trace-wash-bg {
  background: linear-gradient(180deg,
    #000 0%,
    #030f0a 40%,
    #061f14 75%,
    #0b3d26 100%
  );
}

/* Text utility classes */
@utility text-balance { text-wrap: balance; }
@utility text-pretty  { text-wrap: pretty;  }
```

---

## 9. Responsive Breakpoints

```
Breakpoint    px       Tailwind prefix    Notes
──────────────────────────────────────────────────────
xs            < 480    (default)          Single-column, stacked nav
sm            480+     sm:                Two-column grids begin
md            768+     md:                Desktop nav, 2–3 col grids
lg            1024+    lg:                Full 3–4 col layouts
xl            1280+    xl:                Max-width content areas
2xl           1536+    2xl:               Wide monitors, centered content
```

**Max content width**: `1280px` (`max-w-5xl` / `max-w-screen-xl`), centered with `mx-auto`.
**Side padding**: `px-4` (mobile) → `px-6` (sm) → `px-8` (md) → `px-12` (lg).

---

## 10. `@layer base` Rules

```css
@layer base {
  /* Every rounded rectangle is a squircle */
  *, *::before, *::after {
    corner-shape: squircle;
    border-color: var(--color-line);
  }
  .round, .round::before, .round::after {
    corner-shape: round;  /* Opt-out for true circles */
  }

  html {
    background-color: var(--color-bg);
    color-scheme: dark;
    scroll-behavior: smooth;
    -webkit-text-size-adjust: 100%;
  }

  body {
    background-color: var(--color-bg);
    color: var(--color-fg);
    font-family: var(--font-sans);
    font-feature-settings: 'cv11', 'ss03';
    letter-spacing: -0.011em;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: clip;
  }

  ::selection {
    background: rgb(59 130 246 / 0.35);
    color: #fff;
  }

  button, input, textarea, select {
    font: inherit;
    letter-spacing: inherit;
    color: inherit;
  }

  :focus-visible {
    outline: 2px solid var(--color-signal-soft);
    outline-offset: 3px;
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
}
```

---

## 11. Range Slider (updated)

```css
.range { appearance: none; height: 40px; background: transparent; cursor: pointer; }

.range::-webkit-slider-runnable-track {
  height: 6px;
  border-radius: 999px;
  background: linear-gradient(
    to right,
    var(--color-signal) var(--fill, 50%),
    rgb(255 255 255 / 0.12) var(--fill, 50%)
  );
}
.range::-moz-range-track {
  height: 6px;
  border-radius: 999px;
  background: linear-gradient(
    to right,
    var(--color-signal) var(--fill, 50%),
    rgb(255 255 255 / 0.12) var(--fill, 50%)
  );
}
.range::-webkit-slider-thumb {
  appearance: none;
  width: 22px; height: 22px;
  margin-top: -8px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 0 5px var(--color-signal-glow), 0 2px 8px rgb(0 0 0 / 0.4);
  transition: transform 0.15s;
}
.range:active::-webkit-slider-thumb { transform: scale(1.15); }
.range::-moz-range-thumb {
  width: 22px; height: 22px;
  border: 0;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 0 5px var(--color-signal-glow);
}
```

---

## 12. Token → Old Token Migration Map

| **Old token (Tidewell)** | **New token (TraceGuard AI)** | Notes |
|--------------------------|-------------------------------|-------|
| `--color-fire-1` | `--color-threat` | Red replaces orange |
| `--color-fire-2` | `--color-warn` | Amber for warnings |
| `--color-fire-3` | `--color-warn-soft` | Lighter amber |
| `--color-ember` | `--color-threat-dim` | Deep red |
| `--color-ocean-1` | `--color-surface` | Same dark navy |
| `--color-ocean-2` | `--color-surface-2` | Elevated surface |
| `--color-ocean-3` | `--color-signal-dim` | Blue deep tone |
| `--color-sky` | `--color-signal-soft` | Light blue |
| `--color-ice` | `--color-fg` / `--color-soft` | White/near-white text |
| `--color-plasma` | `--color-signal` | Signal blue replaces plasma |
| `--color-plasma-text` | `--color-signal-soft` | Readable blue text |
| `--color-danger` | `--color-threat-soft` | Readable red |
| `--color-success` | `--color-trace-soft` | Emerald success |
| `--shadow-glow-fire` | `--shadow-glow-threat` | Red glow |
| `--shadow-glow-plasma` | `--shadow-glow-signal` | Blue glow |
| `ocean-wash` utility | `signal-wash-bg` utility | Blue gradient wash |

> [!WARNING]
> Do a global find-and-replace across all `.tsx`/`.css` files for Tailwind class names like `text-plasma`, `bg-fire-1`, `shadow-glow-fire`, `border-ocean-2`, etc. Each maps to the new token above. The surface/radius/shadow/motion architecture is compatible — only color names change.


---

# Part II: Information Architecture & Component Design Direction
*Authored by Design Director for `@implementer`*

---

## 13. Route Structure & Navigation Architecture

### Route Migration Map

| Old Route | Old Page | New Route | New Page / Action | Purpose |
|---|---|---|---|---|
| `/` | Home | `/` | **Home** (`pages/Home.tsx`) | Full redesign: Hero DFA, Problem, Pipeline, Engines, CTA |
| `/technology` | Technology | `/technology` | **Technology** (`pages/Technology.tsx`) | Formal Automaton 5-tuple, Isolation Forest ML, Hybrid consensus |
| `/applications` | Applications | `/automaton` | **Automaton** (`pages/Automaton.tsx`) | Dedicated 9-state HTTP DFA laboratory, tables, string classifications |
| `/company` | Company | `/about` | **About** (`pages/About.tsx`) | Academic context, University lab pedigree, 5 defense presenters |
| `/careers` | Careers | `/presentation` | **Presentation** (`pages/Presentation.tsx`) | TOC Defense deck (22 slides, 13m 30s), 5 presenter guides, slide strip |
| `/news` | News | `/research` | **Research** (`pages/Research.tsx`) | Benchmark methodology (100 sessions), test suite (149/149), limitations |
| `/contact` | Contact | `/contact` | **Contact** (`pages/Contact.tsx`) | Academic contact & repository links |
| `/early-access` | EarlyAccess | — | *Remove* | Commercial early access is irrelevant to academic open-source |
| `/styleguide` | StyleGuide | `/styleguide` | **StyleGuide** (`pages/StyleGuide.tsx`) | Keep for visual regression testing & token inspection |
| — | — | `/architecture` | **Architecture** (`pages/Architecture.tsx`) | 4-stage pipeline, engine arbiter, and tech stack |

### Router Event Renaming
In `website/src/lib/router.tsx`:
- Rename `const EVENT = 'tidewell:navigate'` to `const EVENT = 'traceguard:navigate'`

### Global Navigation Array (`content.ts`)

```typescript
export const nav = [
  { label: 'Technology',   href: '/technology' },
  { label: 'Automaton',    href: '/automaton' },
  { label: 'Architecture', href: '/architecture' },
  { label: 'Research',     href: '/research' },
  { label: 'Presentation', href: '/presentation' },
]

export const cta = { label: 'Explore Architecture', href: '/architecture' }
```

---

## 14. Page-by-Page Section Composition & Order

### 14.1 Homepage (`/`)
1. **Hero**: Split layout (Left: Editorial copy + 3 verified metric pills + dual CTAs; Right: Animated SVG 9-state HTTP DFA diagram).
2. **Problem Section (`sections/Problem.tsx`)**: The duality between formal protocol verification ($\mathcal{O}(1)$ deterministic invariant check) vs. statistical heuristics (ML anomaly detection).
3. **Pipeline Section (`sections/Pipeline.tsx`)**: 4-stage horizontal stream processing (Raw Packet Capture $\to$ Protocol Event Tokenizer $\to$ Dual FSM/ML Engines $\to$ Hybrid Risk Arbiter).
4. **Engines Section (`sections/Engines.tsx`)**: 3 comparative engine cards (Deterministic FSM, Isolation Forest ML, Hybrid Consensus Engine).
5. **HomeCTA Section (`sections/HomeCTA.tsx`)**: Minimal academic action strip ("Explore Formal Automaton" & "View Defense Presentation").

### 14.2 Technology Page (`/technology`)
1. **PageHeader**: Eyebrow `Technology`, H1 `Formal Automata Meets Machine Learning`, lede copy.
2. **Formal Automaton Specification**: Complete 5-tuple $\mathcal{M} = (Q, \Sigma, \delta, q_0, F)$, completeness proof theorem ($9 \times 13 = 117$ entries).
3. **Machine Learning Anomaly Engine**: Isolation Forest formulation, recursive feature space partitioning, 15 engineered telemetry features.
4. **Hybrid Risk Arbiter**: Composite scoring formula $S_h = 0.6 S_{FSM} + 0.4 S_{ML}$ with deterministic safety floor $\max(S_h, 60.0)$ on any FSM violation.
5. **Comparative Engine Matrix**: Theoretical complexity, false positive guarantees, and zero-day protocol resilience.

### 14.3 Automaton Page (`/automaton`) — *New Dedicated Interactive Page*
1. **PageHeader**: Eyebrow `Automata Laboratory`, H1 `Complete Total HTTP DFA`, lede copy.
2. **Interactive DFA Diagram Canvas**: Full-width SVG visualization with interactive node tooltips, active path highlights, and edge transition tags.
3. **State Space Table ($Q$)**: All 9 states with formal mathematical semantics, start state ($q_0 = \text{IDLE}$), accepting state ($F = \{\text{CLOSED}\}$), and absorbing sink state ($\text{TRAP}$).
4. **Alphabet Table ($\Sigma$)**: All 13 protocol event symbols.
5. **Language Recognition & Trace Classification**: 3 canonical trace walkthroughs:
   - **ACCEPTED**: $w = \langle\text{CONNECT}, \text{REQUEST}, \text{AUTH\_SUCCESS}, \text{RESPONSE\_200}, \text{CLOSE}\rangle \implies \delta^*(q_0, w) = \text{CLOSED} \in F$.
   - **INCOMPLETE VALID**: Clean pipelined session still open.
   - **REJECTED**: Illegal sequence diverting into absorbing $\text{TRAP}$.
6. **Total Transition Completeness Proof**: Explanation of 15 valid, 88 unauthorized, 13 post-close, and 13 trap self-loops ($117$ total transitions).

### 14.4 Architecture Page (`/architecture`) — *New Page*
1. **PageHeader**: Eyebrow `Architecture`, H1 `Detection Pipeline & Data Flow`.
2. **Pipeline Architecture Diagram**: Detailed 4-stage processing SVG diagram.
3. **Core Engine Breakdown**: Deep-dive cards into packet parsing, state tracking, and vector generation.
4. **Technology Stack Table**: Python 3.11, FastAPI, React 19, Tailwind CSS v4, SQLite/Alembic, Docker, Scapy.

### 14.5 Presentation Page (`/presentation`) — *Replaces Careers*
1. **PageHeader**: Eyebrow `Presentation`, H1 `Theory of Computation Defense`, lede explaining university capstone defense.
2. **Canonical Deck Banner**: Direct download / link to `TraceGuard AI — Editorial Theory of Computation Deck.pptx` (22 slides, 13m 30s defense time).
3. **Presenter Defense Matrix (5 Presenters)**:
   - **Presenter 1**: Intro, Motivation, Scope (Slides 1–3, 2m 30s)
   - **Presenter 2**: Automata Theory & HTTP DFA (Slides 4–8, 3m 30s)
   - **Presenter 3**: Machine Learning & Hybrid Consensus (Slides 9–11, 2m 30s)
   - **Presenter 4**: Architecture & Forensics Telemetry (Slide 12, 2m 30s)
   - **Presenter 5**: Empirical Verification & Defense Q&A (Slides 13–14, 2m 30s)
4. **Slide Strip Carousel**: Interactive thumbnail strip previewing defense slides.

### 14.6 Research Page (`/research`) — *Replaces News*
1. **PageHeader**: Eyebrow `Research & Verification`, H1 `Academic Benchmark & Methodology`.
2. **Calibrated Benchmark Telemetry**: 100-session corpus: **28.57% FSM attribution**, **14.29% ML attribution**, **57.14% Hybrid consensus**, **0% unexplained alerts**.
3. **Test Suite Verification**: 149 of 149 test nodes passing (`pytest -v`, 11.5s), adversarial probe coverage (56 probes).
4. **Academic Limitations**: Transparent discussion of pushdown automata (PDA) necessity for chunked HTTP/2 framing, Npcap kernel latency, and offline dataset boundaries.
5. **Canonical Documentation Index**: Direct links to `FORMAL_AUTOMATON.md`, `ALGORITHM_EXPLANATION.md`, and `PHASE17_FINAL_REPORT.md`.

### 14.7 About Page (`/about`) — *Replaces Company*
1. **PageHeader**: Eyebrow `About TraceGuard AI`, H1 `Theory of Computation Laboratory Project`.
2. **Research Context**: University computer science research initiative exploring automata theory in cybersecurity.
3. **Student Presentation Team**: 5 researcher profiles aligned with the defense presenters.

---

## 15. Component Lifecycle Plan (Keep, Remove, Create)

### Components to KEEP (Update styling/tokens)
- `website/src/components/Container.tsx`: Standard responsive container wrapper.
- `website/src/components/Reveal.tsx`: Smooth scroll-entrance motion component.
- `website/src/components/Button.tsx`: Button and ButtonLink primitives (re-point focus rings and variant colors).
- `website/src/components/Card.tsx`: Update `tones` mapping (remove `fire`/`ocean`/`stripes`/`steel`, add `signal`/`trace`/`threat`/`grid`/`plain`).
- `website/src/components/PageHeader.tsx`: Update `tone` prop (`signal` wash instead of `ocean`/`fire`).
- `website/src/components/Typography.tsx`: `Eyebrow` and `SectionHeading` (update eyebrow tones to `signal`/`trace`/`muted`).
- `website/src/components/Sheet.tsx`: Mobile navigation sliding drawer.
- `website/src/sections/Nav.tsx`: Navigation header (update logo and links).
- `website/src/sections/Footer.tsx`: Clean academic footer.

### Components to REMOVE (Dead Tidewell Fusion Artifacts)
- `website/src/components/FireStreaks.tsx` (Plasma fire canvas effect)
- `website/src/components/Reactor.tsx` (Nuclear stellarator reactor cutaway)
- `website/src/components/Ship.tsx` (Cargo frigate 3D vessel render)
- `website/src/components/ThermalImage.tsx` (Thermal color filter)
- `website/src/components/Skyline.tsx` (Maritime shipyard silhouette)
- `website/src/components/Pedigree.tsx` (Corporate investor marks)
- `website/src/components/Newsletter.tsx` (Marketing newsletter signup)
- `website/src/components/PostCard.tsx` (Blog post teaser cards)
- `website/src/sections/Audiences.tsx` (Commercial shipping/defense markets)
- `website/src/sections/Milestones.tsx` (Corporate venture timeline)
- `website/src/sections/Why.tsx` (Maritime fusion marketing cards)
- `website/src/sections/Mission.tsx` (Recruitment / investor callouts)

### New Components to CREATE
1. `website/src/components/Logo.tsx`: Official TraceGuard AI vector SVG logo from `brand/brand.json` (horizontal full logo & standalone icon).
2. `website/src/components/DFADiagram.tsx`: Interactive SVG state machine rendering the 9 states, 15 valid edges, and pulse animations.
3. `website/src/components/PipelineDiagram.tsx`: 4-stage pipeline visualization showing data ingestion and parallel analysis.
4. `website/src/components/FormulaBlock.tsx`: Polished mathematical block for $S_h = 0.6 S_{FSM} + 0.4 S_{ML}$ and DFA 5-tuple.
5. `website/src/components/MetricPill.tsx`: Clean stat pill for hero metrics.
6. `website/src/sections/Problem.tsx`: Formal verification vs. machine learning problem framing.
7. `website/src/sections/Pipeline.tsx`: Flow visualization section on homepage.
8. `website/src/sections/Engines.tsx`: 3-card engine comparative section.
9. `website/src/sections/HomeCTA.tsx`: Clean 2-action closing section for homepage.

---

## 16. Hero Visual Specification & DFA Diagram Blueprint

### Hero Visual Layout
- **Desktop Grid (1440px)**: 2-column layout (`grid lg:grid-cols-[1.1fr_1fr]`, gap: 40px).
- **Left Column**:
  - `Badge`: Tone `signal` with pulse dot: `Theory of Computation Project`
  - `H1 Display`:
    ```
    Network protocol verification,
    mathematically.
    ```
  - `Lede Copy`: "TraceGuard AI audits HTTP session traces against a formal Deterministic Finite Automaton, flagging protocol violations instantly. A hybrid Isolation Forest layer catches volumetric anomalies statistical rules miss."
  - `CTAs`:
    - Primary: `Explore Architecture` $\to$ `/architecture`
    - Secondary: `View Presentation` $\to$ `/presentation`
  - `Metric Pills Grid`:
    - **9**: DFA states ($Q$)
    - **13**: Alphabet symbols ($\Sigma$)
    - **117**: Total transitions ($\delta$)
- **Right Column (DFA Visualization)**:
  - Container: Glass card with `--color-surface` and subtle `--color-signal-wash` radial glow behind it.
  - Active SVG DFA diagram displaying the 9 states and transition paths with flowing packet animations.

### DFA SVG Node Coordinates & Visual Semantics (`DFADiagram.tsx`)

ViewBox: `0 0 800 520`

| State ($q$) | cx | cy | Visual Style | Border / Accent | Label |
|---|---|---|---|---|---|
| `IDLE` ($q_0$) | 70 | 220 | Start State (Double Ring) | `--color-signal` | `IDLE (q₀)` |
| `CONNECTED` | 210 | 220 | Standard State | `--color-signal-soft` | `CONNECTED` |
| `REQUEST_RECEIVED` | 360 | 220 | Branching Hub | `--color-signal-soft` | `REQ_RCVD` |
| `AUTH_CHECKED` | 510 | 140 | Verification State | `--color-signal-soft` | `AUTH_OK` |
| `AUTH_FAILED` | 510 | 300 | Failure Branch | `--color-threat` | `AUTH_FAIL` |
| `RESPONSE_SENT` | 650 | 220 | Flush State | `--color-signal-soft` | `RESP_SENT` |
| `ERROR` | 510 | 420 | Syntax Fault State | `--color-threat` | `ERROR` |
| `CLOSED` ($F$) | 750 | 360 | Accepting State (Double Ring) | `--color-trace` (Emerald) | `CLOSED (F)` |
| `TRAP` | 360 | 450 | Absorbing Dead Sink (Dashed) | `--color-muted` / Threat | `TRAP (Sink)` |

### Key Transitions & Edges
1. `IDLE` $\to$ `CONNECTED` on `CONNECT`
2. `CONNECTED` $\to$ `REQUEST_RECEIVED` on `REQUEST`
3. `REQUEST_RECEIVED` $\to$ `AUTH_CHECKED` on `AUTH_SUCCESS`
4. `REQUEST_RECEIVED` $\to$ `AUTH_FAILED` on `AUTH_FAILURE`
5. `REQUEST_RECEIVED` $\to$ `ERROR` on `MALFORMED`
6. `AUTH_CHECKED` $\to$ `RESPONSE_SENT` on `RESPONSE_200` / `RESPONSE_301`
7. `AUTH_CHECKED` $\to$ `ERROR` on `RESPONSE_500`
8. `AUTH_FAILED` $\to$ `RESPONSE_SENT` on `RESPONSE_401` / `RESPONSE_403`
9. `RESPONSE_SENT` $\to$ `REQUEST_RECEIVED` on pipelined `REQUEST` (Loopback curve)
10. `RESPONSE_SENT` $\to$ `CLOSED` on `CLOSE` (Accepting path)
11. `ERROR` $\to$ `RESPONSE_SENT` on `ERROR_RESPONSE`
12. `ERROR` $\to$ `CLOSED` on `CLOSE`
13. Any violation $\to$ `TRAP` (Illustrated via representative dashed path)

### Pulse & Flow Animation Spec
- Animate active trace path: A continuous SVG dashed stroke animation (`stroke-dashoffset`) cycling through the canonical accepted sequence `IDLE` $\to$ `CONNECTED` $\to$ `REQUEST_RECEIVED` $\to$ `AUTH_CHECKED` $\to$ `RESPONSE_SENT` $\to$ `CLOSED`.
- `CLOSED` state node features an ambient glow pulse (`filter: drop-shadow(0 0 10px rgba(16, 185, 129, 0.5))`).
- `TRAP` state node features subtle dashed stroke styling to emphasize its absorbing mathematical property.

---

## 17. Verified Academic Statistics (Zero Hallucination Mandate)

| Metric | Ground Truth Value | Academic Source Reference |
|---|---|---|
| **DFA States ($|Q|$)** | **9** | `docs/FORMAL_AUTOMATON.md` §2 |
| **Alphabet Symbols ($|\Sigma|$)** | **13** | `docs/FORMAL_AUTOMATON.md` §3 |
| **Total Transitions ($|Q \times \Sigma|$)** | **117** | `docs/FORMAL_AUTOMATON.md` §4 |
| **Valid Protocol Transitions** | **15** | `docs/FORMAL_AUTOMATON.md` §4 |
| **TRAP Transitions** | **102** ($88 + 13 + 13$) | `docs/FORMAL_AUTOMATON.md` §4 |
| **Test Suite Pass Rate** | **149 / 149 (100%)** | `docs/PHASE17_FINAL_REPORT.md` §3 |
| **Adversarial Test Probes** | **56 probes** | `tests/test_adversarial_probes_56.py` |
| **Benchmark Dataset Size** | **100 sessions** | `docs/PHASE17_FINAL_REPORT.md` §2 |
| **FSM Attribution Share** | **28.57%** | `docs/PHASE17_FINAL_REPORT.md` §2 |
| **ML Attribution Share** | **14.29%** | `docs/PHASE17_FINAL_REPORT.md` §2 |
| **Hybrid Consensus Share** | **57.14%** | `docs/PHASE17_FINAL_REPORT.md` §2 |
| **Unexplained Alert Ratio** | **0.00%** | `docs/PHASE17_FINAL_REPORT.md` §2 |
| **Hybrid Formula** | $S_h = 0.6 S_{FSM} + 0.4 S_{ML}$ | `docs/ALGORITHM_EXPLANATION.md` §4 |
| **Deterministic Risk Floor** | $\max(S_h, 60.0)$ on FSM violation | `docs/ALGORITHM_EXPLANATION.md` §4 |
| **ML Feature Space** | **15 engineered features** | `docs/ALGORITHM_EXPLANATION.md` §3 |
| **Defense Slide Count** | **22 slides** | `docs/PHASE18_FINAL_REPORT.md` §3 |
| **Defense Presentation Time** | **13m 30s** | `docs/PHASE18_FINAL_REPORT.md` §2 |
| **Presenter Team Count** | **5 presenters** | `docs/PHASE18_FINAL_REPORT.md` §2 |

---

## 18. Logo Implementation Guide (`Logo.tsx`)

The vector assets are located in `brand/brand.json` and `brand/logo/`.
`website/src/components/Logo.tsx` must be implemented as:
```tsx
export function Logo({ variant = 'horizontal', className = 'h-8 w-auto' }: { variant?: 'horizontal' | 'icon'; className?: string }) {
  // Renders the official SVG with emerald gradient mark (#081710 -> #10B981)
  // and electric blue wordmark text (#3B82F6).
}
```
In `website/src/sections/Nav.tsx`:
```tsx
<Link href="/" aria-label="TraceGuard AI home" className="-m-2 inline-flex items-center rounded-[12px] p-2">
  <Logo variant="horizontal" className="h-7 w-auto" />
</Link>
```

---

## 19. Summary Checklist for `@implementer`
- [ ] Update `website/src/styles.css` with `@theme` block from §1.
- [ ] Update `website/src/lib/tokens.ts` with color groups from §2.
- [ ] Rename navigate event to `traceguard:navigate` in `lib/router.tsx`.
- [ ] Replace `website/src/content.ts` with authentic TraceGuard AI content matching §13 & §17.
- [ ] Create `website/src/components/Logo.tsx`.
- [ ] Create `website/src/components/DFADiagram.tsx` with animated state flow.
- [ ] Update `website/src/components/Card.tsx` with new tone palette (`signal`, `trace`, `threat`, `grid`, `plain`).
- [ ] Build new pages: `Automaton.tsx`, `Architecture.tsx`, `Presentation.tsx`, `Research.tsx`, `About.tsx`.
- [ ] Redesign `Home.tsx` and `Technology.tsx`.
- [ ] Update route matching in `App.tsx` (or root page router).
- [ ] Remove obsolete Tidewell files listed in §15.
- [ ] Run `bun run build` in `website/` to verify zero TypeScript or bundler errors.
