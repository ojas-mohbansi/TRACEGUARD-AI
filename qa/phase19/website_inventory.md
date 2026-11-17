# TraceGuard AI — Phase 19 Website Inventory

> **Auditor:** @auditor | **Date:** 2026-11-17 | **Repo:** `C:\Projects\FSM-NIDS`

---

## 1. Stack & Framework Summary

| Layer | Current value |
|---|---|
| Framework | React 19.2 + TypeScript 5.9 |
| Build tool | Vite 8.3 (`@vitejs/plugin-react` 6.1) |
| CSS | Tailwind CSS v4.3 (`@tailwindcss/vite` plugin) — `@theme` block in `styles.css`, no config file |
| Animation | Motion (Framer) v14.4 — `motion/react` |
| Icons | Lucide React v1.60 |
| API layer | Hono v4.13 (Cloudflare Worker) |
| Deployment | Cloudflare Workers + Cloudflare Vite Plugin v1.64 |
| Package manager | Bun (`bun.lock` present) |
| Package name | `fusion-energy` (must be renamed to `traceguard-ai` or similar) |
| Worker name | `fusion-energy` in `wrangler.jsonc` (must be renamed) |
| Dev port | `5303` |

### Dependencies to retain (all brand-agnostic)
- `hono`, `lucide-react`, `motion`, `react`, `react-dom`
- All devDependencies

---

## 2. Git History (last 10 commits)

```
5a05408 fix(tests): auto-seed alert and dataset in integration tests for clean CI runners
9f00f10 fix(ci): add email-validator required by pydantic EmailStr
b6fc858 fix(ci): add httpx dependency required by starlette/fastapi TestClient
248754b chore: prepare TraceGuard AI for GitHub publication
8999124 feat(cli): expose the Tier-1 policy knobs and tighten the strict direction gate (#3)
01aac12 feat(fsm): add the Tier-1 deterministic protocol state machine
52c5a5e Merge branch 'main'
1fac58f phase 1.3
f315032 feat(window): expire idle sessions and carry FSM metadata (#1)
741a592 Add Modbus/TCP ingestion and feature pipeline
```

> [!NOTE]
> Commit `248754b` ("prepare TraceGuard AI for GitHub publication") preceded the website template being added with its Tidewell branding still intact. The website was dropped in as a template and never rebranded.

---

## 3. Complete File Inventory

### Root files

| File | Size | Purpose |
|---|---|---|
| `index.html` | — | SPA shell. Title: "Tidewell Fusion" ❌. Meta description: Tidewell ❌. Inter font loaded from Google Fonts. Favicon: `/favicon.svg` |
| `vite.config.ts` | — | Vite config with `react()`, `tailwindcss()`, `cloudflare()` plugins. Port 5303. Clean. |
| `wrangler.jsonc` | — | Worker name: `fusion-energy` ❌. SPA mode: `single-page-application`. `run_worker_first: true`. Observability enabled. |
| `package.json` | — | Package name: `fusion-energy` ❌. All deps listed above. |
| `scripts/postbuild.mjs` | — | Strips hidden files and `.map` files from `dist/` for Cloudflare Sites upload. **BUG**: path resolution produces `C:\C:\...` on Windows (double drive letter) — `bun run build` exits code 1. Vite build itself succeeds. |

### `src/` — Top-level

| File | Size | Purpose |
|---|---|---|
| `main.tsx` | 487 B | React root mount. Clean, no brand content. ✅ Reusable as-is |
| `App.tsx` | 4.6 KB | Route resolver, Suspense wrapper, `<Nav>/<Footer>`, scroll-to-hash, skip link, `document.title` setter. References `brand.name` ❌ |
| `content.ts` | 20 KB | **Master content file** — every string on the site. 100% Tidewell Fusion content. Must be fully rewritten for TraceGuard AI ❌ |
| `styles.css` | 6.3 KB | Tailwind v4 `@theme` block + base layers + utilities. Brand colours named `fire-*`, `plasma`, `ocean-*`. Comment header says "Tidewell Fusion design tokens" ❌. Colour palette itself (dark, blue/amber) may remain or be adapted. |

### `src/lib/`

| File | Size | Purpose | Reusable? |
|---|---|---|---|
| `router.tsx` | 3.9 KB | Tiny History API SPA router: `useLocation`, `navigate`, `Link`, `match`, `isCurrent`. Event name `tidewell:navigate` ❌ (cosmetic only) | ✅ Fully reusable after renaming the event strings |
| `store.ts` | 3.0 KB | `localStorage`-backed state: `useStored`, `postJson`. localStorage prefix `tidewell:` ❌ | ✅ Reusable after renaming the prefix |
| `validate.ts` | 3.8 KB | Shared browser+Worker form validation for EarlyAccess, Contact, Application, Newsletter. Domain-agnostic logic. | ✅ Reusable; field names (name, email, segment, topic) need updating for TraceGuard's forms |
| `cx.ts` | 124 B | `clsx`-lite class combiner. | ✅ Fully reusable |
| `tokens.ts` | 3.3 KB | Design token data for StyleGuide. Mirrors CSS `@theme`. Comment references "Tidewell" ❌ | ✅ Reusable after updating values and removing comment |
| `useReducedMotion.ts` | 499 B | `prefers-reduced-motion` hook. | ✅ Fully reusable |

### `src/components/`

| Component | Size | Purpose | Reuse verdict |
|---|---|---|---|
| `Button.tsx` | 4.9 KB | `Button`, `ButtonLink`, `TextLink`, `IconButton`. Pill buttons, 3 variants, 3 sizes. Brand-neutral. | ✅ Fully reusable |
| `Card.tsx` | 2.0 KB | `Card` + `CardText`. Tones: `plain`, `fire`, `ocean`, `stripes`, `steel`. Container surface. | ✅ Reusable; tone names may be renamed to TraceGuard vocabulary |
| `Container.tsx` | 405 B | Max-width wrapper with sizes `sm/md/lg/xl`. | ✅ Fully reusable |
| `Controls.tsx` | 11.8 KB | `Badge`, `Chip`, `SaveToggle`, `Notice`, `EmptyState`, `LinkRow`, `ChoiceGroup`, `Stepper`, `Slider`, `Skeleton`, `CheckList`, `SuccessMark`. | ✅ Fully reusable |
| `Field.tsx` | 6.1 KB | `Field`, `Input`, `Textarea`, `Select`, `Checkbox` form primitives. | ✅ Fully reusable |
| `FireStreaks.tsx` | 3.6 KB | Canvas animation of orange fire-streak lines. Used in Hero (home) and EarlyAccess backgrounds. | ⚠️ Thematically wrong for a network IDS. Replace with a network-graph or packet-flow canvas animation, OR repurpose with green/cyan tones. |
| `Logo.tsx` | 1.1 KB | `Logo` and `LogoMark`. SVG of a "plasma ring around a bright core" (orbital ellipses). Renders `brand.short` as text. | ❌ Must be replaced with TraceGuard AI logo/mark. SVG needs redesign. |
| `Newsletter.tsx` | 2.3 KB | Email subscription form posting to `/api/subscribe`. | ✅ Reusable with updated copy |
| `PageHeader.tsx` | 1.9 KB | Reusable inner-page header: eyebrow, h1, lede, optional aside. | ✅ Fully reusable |
| `Pedigree.tsx` | 1.1 KB | Typographic wordmark strip (placeholder employer names). | ✅ Reusable; replace marks in content.ts |
| `PostCard.tsx` | 2.7 KB | News/blog post card (not read yet — see note). | ✅ Likely reusable |
| `Reactor.tsx` | 5.5 KB | SVG reactor cutaway: plasma vessel, magnets, flanges. Used in Technology page interactive explorer and Hero aside. | ❌ Replace with TraceGuard-relevant SVG: e.g. a network topology diagram, FSM state graph, or packet-flow diagram |
| `Reveal.tsx` | 743 B | Scroll-triggered fade+rise animation wrapper. | ✅ Fully reusable |
| `Sheet.tsx` | 3.8 KB | Accessible modal side sheet (mobile nav). Focus trap, Esc close, scroll lock. | ✅ Fully reusable |
| `Ship.tsx` | 5.2 KB | SVG holographic vessel illustrations: `cargo`, `frigate`, `platform`. Thematically maritime. | ❌ Replace with TraceGuard-relevant SVG assets (e.g. network nodes, server racks, industrial control panels) |
| `Skyline.tsx` | 2.3 KB | SVG port skyline with cranes and a moored ship. Used in Mission panel. | ❌ Replace with a network/cyber-relevant SVG (e.g. data-centre skyline, protocol diagram, globe with nodes) |
| `ThermalImage.tsx` | 1.4 KB | SVG filter that maps any photo to a thermal-camera colour gradient. | ⚠️ Interesting visual effect. Could be repurposed as a "threat heat-map" scan effect. |
| `Typography.tsx` | 1.8 KB | `Eyebrow`, `SectionHeading`. Brand-neutral. | ✅ Fully reusable |

### `src/sections/`

| Section | Size | Purpose | Reuse verdict |
|---|---|---|---|
| `Nav.tsx` | 3.6 KB | Fixed top nav with logo, links from `content.nav`, CTA button, mobile Sheet drawer. | ✅ Structure reusable; all content from `content.ts` ❌ |
| `Footer.tsx` | 1.9 KB | 4-column footer: logo, address, link columns, Newsletter widget, legal line. | ✅ Structure reusable; all content from `content.ts` ❌ |
| `Hero.tsx` | 3.9 KB | Home hero: eyebrow badge, two-line h1, lede, two CTAs, stats bar, reactor image with plasma glow. | ✅ Structure reusable; content from `content.ts` ❌; reactor image → replace with TraceGuard hero asset |
| `Audiences.tsx` | 1.4 KB | "Who we're building for" section: ship images, two audience cards. | ✅ Structure (two audience columns) reusable; images → replace with TraceGuard audience visuals ❌ |
| `Why.tsx` | 3.3 KB | Three tall proof-cards with FireStreaks background band: team (ThermalImage), prototype (reactor image), volume (stat). | ⚠️ Structure reusable; card imagery (reactor, thermal crew) must be replaced. FireStreaks background may need replacement. |
| `Mission.tsx` | 1.6 KB | Blue gradient panel with Skyline SVG + three LinkRows. | ✅ Structure reusable; Skyline SVG → replace; content ❌ |
| `Milestones.tsx` | 1.8 KB | Horizontal/vertical timeline of milestones. Current item glows. | ✅ Fully reusable structure; content ❌ |

### `src/pages/`

| Page | Size | Route | Purpose | Reuse verdict |
|---|---|---|---|---|
| `Home.tsx` | 372 B | `/` | Composes: Hero → Audiences → Why → Milestones → Mission. | ✅ Structure reusable; all sections need content replacement |
| `Technology.tsx` | 7.6 KB | `/technology` | Interactive reactor explorer (SVG click-targets + tabpanel), principles cards, specs table, Milestones, Mission. | ⚠️ Interactive part reusable as a pattern (e.g. FSM state explorer); reactor SVG and all copy must go |
| `Applications.tsx` | 6.1 KB | `/applications` | Segment cards with photos, fuel-savings calculator (Slider + Chips). | ⚠️ Structure reusable; calculator concept adaptable (e.g. "alert reduction" calculator); all content ❌ |
| `Company.tsx` | 5.1 KB | `/company` | Stats bar, team cards (Avatar initials), values cards, Milestones, backers list. | ✅ Fully reusable structure; content ❌ |
| `Careers.tsx` | 5.9 KB | `/careers` | Searchable, filterable, saveable job list. | ✅ Excellent reusable pattern; content (jobs, teams) ❌ |
| `Job.tsx` | 7.2 KB | `/careers/:slug` | Job detail with responsibilities/requirements, application form (3 fields + file link). | ✅ Reusable; job data ❌ |
| `News.tsx` | 3.2 KB | `/news` | Filterable news feed with post cards. | ✅ Reusable; posts ❌ |
| `Article.tsx` | 3.3 KB | `/news/:slug` | Article detail: cover (fire/ocean/steel tone), body paragraphs, related posts. | ✅ Reusable; content ❌ |
| `EarlyAccess.tsx` | 13.1 KB | `/early-access` | Multi-step form (3 steps): identity → fleet details → review. localStorage draft persistence. | ✅ Excellent reusable form shell; "fleet" vocabulary → replace with TraceGuard's onboarding flow vocabulary (e.g. organisation type, deployment size, use case) |
| `Contact.tsx` | 5.8 KB | `/contact` | Contact form + office address cards + press email. | ✅ Reusable; office addresses and press email ❌ |
| `NotFound.tsx` | 1.5 KB | `*` (404) | "Lost at sea" with Ship SVG, back-to-home CTA, three shortcut links. | ✅ Structure reusable; "Lost at sea" copy + Ship SVG ❌ |
| `StyleGuide.tsx` | 21.5 KB | `/styleguide` | Complete design system preview: colours, type scale, spacing, radii, shadows, motion, all components. | ✅ Invaluable for the new brand — update token values and re-verify |

### `src/worker/`

| File | Size | Purpose |
|---|---|---|
| `index.ts` | 2.2 KB | Hono Worker: `/api/health`, `/api/early-access`, `/api/contact`, `/api/apply`, `/api/subscribe`. Stubs (no actual storage/email). `favicon.svg` served from public. |

---

## 4. Route Map

### Current routes → TraceGuard AI replacement

| Current route | Current title | Suggested TraceGuard route | Suggested title |
|---|---|---|---|
| `/` | Tidewell Fusion | `/` | TraceGuard AI |
| `/technology` | Technology | `/platform` or `/how-it-works` | Platform |
| `/applications` | Applications | `/use-cases` or `/solutions` | Solutions |
| `/company` | Company | `/company` | Company |
| `/careers` | Careers | `/careers` | Careers |
| `/careers/:slug` | (job title) | `/careers/:slug` | (job title) |
| `/news` | News | `/news` or `/blog` | News |
| `/news/:slug` | (article title) | `/news/:slug` or `/blog/:slug` | (article title) |
| `/early-access` | Early access | `/request-access` or `/get-started` | Request access |
| `/contact` | Contact | `/contact` | Contact |
| `/styleguide` | Style guide | `/styleguide` | Style guide |

---

## 5. Template Content Inventory — Everything "Tidewell Fusion" to Replace

> [!CAUTION]
> Every piece of content below is a **hard-coded Tidewell Fusion fiction**. Nothing carries over to TraceGuard AI.

### `content.ts` — Full replacement required

| Export | Tidewell content | Notes |
|---|---|---|
| `brand.name` | `'Tidewell Fusion'` | → `'TraceGuard AI'` |
| `brand.short` | `'Tidewell'` | → `'TraceGuard'` |
| `brand.tagline` | `'Fusion power for ships that never refuel.'` | → TraceGuard tagline |
| `brand.email` | `'hello@tidewell.example'` | → real email |
| `brand.pressEmail` | `'press@tidewell.example'` | → real email |
| `brand.address` | `['Pier 70, Building 12', 'San Francisco, CA 94107']` | → real address(es) |
| `photos.*` | 13 maritime/reactor images | All 13 must be replaced with TraceGuard assets |
| `nav` | Technology, Applications, Company, Careers, News | Rename to TraceGuard nav |
| `cta` | `'Get early access'` | → e.g. `'Request access'` or `'Get a demo'` |
| `hero.*` | "Fusion power for the open ocean", reactor stats | Entirely new: TraceGuard hero |
| `audiences` | Commercial Shipping, Defense | → TraceGuard audiences (OT/ICS, enterprise, government?) |
| `why.*` | "Why Maritime Fusion?" + team/prototype/volume cards | → "Why TraceGuard?" |
| `why.pedigree` | Arclight, Meridian Orbital, Northgate University, Halden | → real or placeholder institutions |
| `milestones` | 2024–2031 fusion milestones | → TraceGuard's actual or planned milestones |
| `mission.*` | "Be part of the mission" for engineers/shippers/investors | → TraceGuard mission rows |
| `footer.*` | "Compact fusion reactors for commercial shipping" | → TraceGuard footer copy |
| `footer.legal` | "© 2026 Tidewell Fusion, Inc." | → TraceGuard legal |
| `technology.*` | Stellarator, HTS coils, plasma, lithium blanket, CO₂ turbine | Entire technology content |
| `applications.*` | Commercial Shipping, Defense, Offshore; fuel calculator | → TraceGuard use-cases; calculator → alert/threat calculator or ROI calculator |
| `company.*` | "We build hard things at sea level"; 38 people, $62M, Mara Lindqvist et al | → TraceGuard team, stats, values, backers |
| `teams` | Engineering, Physics, Marine, Operations | → TraceGuard teams (e.g. Engineering, Research, Security, Operations) |
| `jobs[]` | 6 fusion/marine jobs | → TraceGuard open roles |
| `newsCategories` | Milestones, Press, Research | → adapt or keep |
| `posts[]` | 4 Tidewell news articles | → TraceGuard news/blog posts |
| `earlyAccess.*` | "Reserve a reactor slot"; fleet size, timeline | → "Request access" form; organisation type, deployment scale, timeline |
| `contact.*` | "Talk to Tidewell"; SF + Rotterdam offices | → TraceGuard contact info |
| `notFound.*` | "Lost at sea" | → TraceGuard 404 copy (can be playful/on-brand) |

### `index.html` — Partial replacement

| Element | Current | Replace with |
|---|---|---|
| `<title>` | `Tidewell Fusion` | `TraceGuard AI` |
| `<meta name="description">` | "Compact fusion reactors for ships…" | TraceGuard description |
| `<link rel="icon">` | `/favicon.svg` (plasma ring) | TraceGuard favicon |

### `wrangler.jsonc` — Rename

| Field | Current | Replace with |
|---|---|---|
| `name` | `fusion-energy` | `traceguard-ai` (or similar) |

### `package.json` — Rename

| Field | Current | Replace with |
|---|---|---|
| `name` | `fusion-energy` | `traceguard-ai` |

### `src/lib/router.tsx` — Cosmetic rename

| Symbol | Current | Replace with |
|---|---|---|
| `EVENT` const | `'tidewell:navigate'` | `'traceguard:navigate'` |

### `src/lib/store.ts` — Cosmetic rename

| Symbol | Current | Replace with |
|---|---|---|
| `PREFIX` const | `'tidewell:'` | `'traceguard:'` |
| `EVENT` const | `'tidewell:store'` | `'traceguard:store'` |

### `styles.css` — Comment update

| Item | Current | Action |
|---|---|---|
| Comment header | "Tidewell Fusion design tokens. A pure-black site lit by two light sources: fire…and ocean…" | Update comment to describe TraceGuard's palette intent |
| Token names (`fire-*`, `plasma`, `ocean-*`) | Fusion-themed names | Rename or keep — see recommendations below |

### SVG components to replace

| Component | Current content | TraceGuard replacement |
|---|---|---|
| `Logo.tsx / LogoMark` | Plasma orbital ring + "Tidewell" text | TraceGuard logo/wordmark |
| `Reactor.tsx` | Fusion reactor cutaway SVG | Network topology, FSM state graph, or packet-flow diagram |
| `Ship.tsx` | Cargo ship, frigate, offshore platform SVGs | Network nodes, server racks, industrial sensor diagrams |
| `Skyline.tsx` | Port cranes and skyline | Data-centre skyline, globe with network edges, or abstract cyber graphic |

---

## 6. Public Assets

| File | Size | Status |
|---|---|---|
| `public/favicon.svg` | 520 B | ❌ Plasma-ring icon — replace with TraceGuard favicon |
| `public/images/careers.webp` | 89 KB | ❌ Engineers around vacuum vessel — replace |
| `public/images/crew.webp` | 28 KB | ❌ Used via ThermalImage filter — replace |
| `public/images/news-coil.webp` | 149 KB | ❌ Superconducting coil — replace |
| `public/images/news-rotterdam.webp` | 101 KB | ❌ Rotterdam office — replace |
| `public/images/news-stellarator.webp` | 110 KB | ❌ Stellarator physics — replace |
| `public/images/reactor.webp` | 166 KB | ❌ Reactor render — replace |
| `public/images/sea-cargo.webp` | 71 KB | ❌ Container ship — replace |
| `public/images/sea-frigate.webp` | 56 KB | ❌ Naval frigate — replace |
| `public/images/sea-offshore.webp` | 42 KB | ❌ Offshore platform — replace |
| `public/images/ship-cargo.webp` | 98 KB | ❌ Container ship cutout — replace |
| `public/images/ship-frigate.webp` | 88 KB | ❌ Frigate cutout — replace |

**All 12 images must be replaced.** The `photos` map in `content.ts` is the single point of control — swap paths there, then drop new files into `public/images/`.

---

## 7. Build Status

**Vite build: ✅ succeeds** — all chunks compile cleanly.

**Post-build script: ❌ fails on Windows** with path error:
```
Error: ENOENT: no such file or directory, scandir 'C:\C:\Projects\FSM-NIDS\website\dist'
```

The `postbuild.mjs` script uses `new URL('../dist', import.meta.url).pathname` which produces a double drive letter on Windows (`C:\C:\...`). Fix:

```js
// scripts/postbuild.mjs — fix for Windows
import { fileURLToPath } from 'node:url'
import { join, dirname } from 'node:path'
// Replace:
// clean(new URL('../dist', import.meta.url).pathname)
// With:
const __dir = dirname(fileURLToPath(import.meta.url))
clean(join(__dir, '..', 'dist'))
```

**Build output chunks (before post-build):**

| Chunk | Size (gzip) |
|---|---|
| `index-*.js` | 252 KB (79 KB gz) — motion + react |
| `Card-*.js` | 169 KB (58 KB gz) — largest lazy chunk |
| `StyleGuide-*.js` | 19 KB (5.5 KB gz) |
| `EarlyAccess-*.js` | 7.8 KB (2.8 KB gz) |
| `Controls-*.js` | 9.3 KB (3.1 KB gz) |

---

## 8. Reusable Components (Full List)

These components require **zero** content changes and can be used directly:

| Component/module | What it provides |
|---|---|
| `Button`, `ButtonLink`, `TextLink`, `IconButton` | All button variants |
| `Card`, `CardText` | Surface containers |
| `Container` | Max-width wrapper |
| `Controls` — `Badge`, `Chip`, `SaveToggle`, `Notice`, `EmptyState`, `LinkRow`, `ChoiceGroup`, `Stepper`, `Slider`, `Skeleton`, `CheckList`, `SuccessMark` | All UI controls |
| `Field`, `Input`, `Textarea`, `Select`, `Checkbox` | Form primitives |
| `Reveal` | Scroll animation wrapper |
| `Sheet` | Accessible modal side sheet |
| `PageHeader` | Inner-page header with aside |
| `Typography` — `Eyebrow`, `SectionHeading` | Type components |
| `Newsletter` | Email capture widget |
| `Pedigree` | Typographic wordmark strip |
| `lib/router.tsx` | SPA router |
| `lib/store.ts` | localStorage state + `postJson` |
| `lib/validate.ts` | Form validation |
| `lib/cx.ts`, `lib/useReducedMotion.ts` | Utilities |
| `styles.css` | Design token system (palette to be updated) |
| `App.tsx` | Route shell |
| `main.tsx` | React entry point |
| `worker/index.ts` | Hono API (stubs, wire to real backend) |

Components that need **replacement or significant rework**:

| Component | Action |
|---|---|
| `Logo.tsx` / `LogoMark` | Redesign for TraceGuard |
| `Reactor.tsx` | Replace with TraceGuard primary SVG illustration |
| `Ship.tsx` | Replace with TraceGuard audience visuals |
| `Skyline.tsx` | Replace with TraceGuard decorative SVG |
| `FireStreaks.tsx` | Repurpose (new colour scheme) or replace with network-graph animation |
| `ThermalImage.tsx` | Repurpose as "threat scan" / "anomaly heatmap" effect, or drop |

---

## 9. Functionality That Works Well (Retain)

1. **SPA router** (`lib/router.tsx`) — custom, no dependencies, handles hash scrolling, focus management, popstate.
2. **Scroll-triggered animations** (`Reveal.tsx`) — clean `whileInView` with stagger support and reduced-motion respect.
3. **Motion system** (hero entrance, page transitions via `AnimatePresence`) — smooth and accessible.
4. **Sheet / mobile nav** (`Sheet.tsx`) — full ARIA dialog, focus trap, Esc close, scroll lock.
5. **Form system** — `Field.tsx` wires IDs/ARIA automatically; `Controls.tsx` has `ChoiceGroup`, `Stepper`, `Slider`; shared validation in `validate.ts`; `postJson` in `store.ts`.
6. **Multi-step EarlyAccess form** — draft persistence, step navigation, server-error routing, success receipt.
7. **Job board** (`Careers.tsx`) — live search, team filter, saved roles via localStorage, applied-role badges.
8. **Interactive diagram pattern** (`Technology.tsx`) — click-target overlays on SVG + keyboard-accessible tab list + animated panel swap. Reuse as "FSM state explorer" or "protocol diagram".
9. **Hono Worker API** — 4 validated endpoints; stub only, but the patterns are solid.
10. **StyleGuide page** — full component and token showcase; invaluable for QA of the new brand.
11. **`corner-shape: squircle`** global — distinctive, modern, Tailwind v4 compatible.
12. **Accessibility baseline** — skip link, ARIA labels throughout, focus management on navigation.

---

## 10. Broken / Placeholder Elements

| Issue | Location | Severity |
|---|---|---|
| `bun run build` exits code 1 | `scripts/postbuild.mjs` Windows path bug | Medium — Vite build itself passes; deploy step affected |
| Form API endpoints are stubs | `worker/index.ts` | Medium — forms submit successfully but data goes nowhere |
| Pedigree names are placeholders | `content.ts` → `why.pedigree` | Low — replace with real institutions |
| Fake team bios | `content.ts` → `company.team` | Content |
| Fake funding round ($50M Series A) | `content.ts` → `posts[1]` | Content |
| Fake stats (38 people, $62M, 14 patents) | `content.ts` → `company.stats` | Content |
| Fake news articles | `content.ts` → `posts[]` | Content |
| Fake job listings | `content.ts` → `jobs[]` | Content |

---

## 11. Recommendations for the Redesign

### Immediate (before any new content)
1. **Fix `postbuild.mjs`** Windows path bug (see §7).
2. **Rename** `package.json` name, `wrangler.jsonc` worker name, router/store event string prefixes.
3. **Replace `index.html`** title, description, favicon.

### Content file (`content.ts`)
4. **Rewrite in one pass** — the file is the single source of truth; all pages pull from it. Brand specialist should draft all copy here first, then the pages will render correctly with zero layout changes.
5. **TraceGuard nav structure** suggestion: `Platform | Solutions | Company | Careers | News`. CTA: `Get a demo` or `Request access`.

### Visual identity
6. **Logo** — design a new `LogoMark` SVG. The current plasma-ring is thematically fitting for a network/state-machine tool (rings → nodes/edges). Consider adapting the concept with green/cyan tones.
7. **Colour palette** — the current dark palette (black surface, blue accent) works well for a security product. Consider:
   - Rename `fire-*` → `alert-*` or `threat-*` (orange/red = threat/alert)
   - Rename `ocean-*` / `plasma` → keep or rename to `signal-*` / `network-*`
   - Add a green `--color-safe` for healthy/normal state
8. **Replace three SVGs**: Reactor → FSM/network diagram, Ship → target-system illustration, Skyline → data-centre or globe.
9. **FireStreaks** → adapt as "packet-flow streaks" (green/cyan) or replace with a network-graph canvas animation.

### Page-level
10. **Technology/Platform page** — reuse the interactive tab-panel pattern from `Technology.tsx` as an "FSM State Explorer": show TraceGuard's protocol states as an interactive diagram.
11. **Applications/Solutions page** — reuse segment cards + calculator pattern. Calculator: "Alert fatigue calculator" (compare current false-positive rate vs. TraceGuard).
12. **EarlyAccess → Request Access** — keep the multi-step form; replace "fleet size / timeline" with "organisation type / deployment scale / primary protocol".
13. **Careers** — the job-board is production-quality. Just replace `jobs[]`, `teams`, and the page-header copy.

### Infrastructure
14. **Wire the Worker API** — connect `/api/early-access`, `/api/contact`, `/api/apply`, `/api/subscribe` to real storage (D1, KV, or external CRM) before launch.
15. **Rename Wrangler worker** from `fusion-energy` to `traceguard-ai` (or use Cloudflare account name as prefix).

---

*End of audit. Total files audited: 54. Brand strings requiring replacement: ~200+ across content.ts, index.html, wrangler.jsonc, package.json, router.tsx, store.ts, styles.css comments.*
