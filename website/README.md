# Tidewell Fusion

A deep-tech company site for a (fictional) maritime fusion reactor company:
pure black, lit by fire (orange light streaks, a thermal-camera team photo)
and ocean (a reactor render, holographic ships, a blue mission panel).
Eight screens plus a 404 and a live [style guide](#style-guide). All copy and
seed data live in one file; forms post to validated Worker routes; visitor
state is kept in localStorage.

## Pages (`src/pages`, routed in `src/App.tsx`)

| Path | What it is |
|---|---|
| `/` | Hero with the reactor, "Who we're building for", "Why Maritime Fusion?" cards over fire streaks, the road to sea trials, "Be part of the mission" |
| `/technology` | Reactor explorer (hotspots + tab list with arrow keys), principles, plant specs, milestones |
| `/applications` | Shipping, defense and offshore markets, and a voyage fuel/CO₂ calculator (`#calculator`, inputs remembered) |
| `/company` | Story, numbers, leadership, values, timeline, backers |
| `/careers`, `/careers/:slug` | Roles with search, team filter and saved roles; role page with an application form whose draft autosaves |
| `/news`, `/news/:slug` | Posts with a category filter and newsletter; article page with copy link |
| `/early-access` | Three-step partner request (who, fleet, review) with `?segment=` preselect and a saved receipt |
| `/contact` | Topic, name, email, message (`?topic=investors` preselects); offices and press email |
| `/styleguide` | The living style guide |
| anything else | 404 |

## Run it

```sh
bun install
bun run dev        # http://localhost:5303 (Vite + the Worker in workerd)
bun run typecheck
bun run build      # dist/client (assets) + dist/fusion_energy/index.js (Worker)
```

## Edit it

- `src/content.ts` holds every string, number, role, post and link. Start there.
- Photos and renders: every image goes through `photos` in `src/content.ts`.
  The eleven `.webp` files in `public/images` (about 1 MB in all) are
  generated stand-ins, not real photography: the crew portrait, a cut-out
  reactor render (home hero and prototype card), two cut-out holographic ships
  (home and the Applications hero), one sea photo per market, three news
  covers (`posts[].image`) and the careers header. Drop your own files into
  `public/images` and change the paths there; keep the reactor and ship
  renders as transparent cut-outs. People in the crew and careers images are
  fictional. The team card shows the crew photo through a thermal-camera SVG
  filter (`ThermalImage`): dark tones read hot, so a backlit portrait with
  faces in shadow keeps the look.
- The reactor explorer, the ships on the 404, early-access and style-guide
  pages, the skyline and the fire streaks are drawn in code
  (`src/components/Reactor.tsx`, `Ship.tsx`, `Skyline.tsx`, `FireStreaks.tsx`).
- The pedigree strip on the team card uses placeholder institution names set
  as type (`why.pedigree`); swap in your own.
- Tokens (colours, radii, shadows, keyframes) are in `src/styles.css` under
  `@theme`; `src/lib/tokens.ts` mirrors them for the style guide.
- Components live in `src/components`, home sections in `src/sections`.

## Forms and state

The Worker (`src/worker/index.ts`) validates with the same rules as the
browser (`src/lib/validate.ts`) and returns 400 for a malformed body, 422 with
field errors for bad input, 200 otherwise. Nothing is stored server-side:
connect each route to your CRM, inbox or a D1 table.

| Route | Form |
|---|---|
| `POST /api/early-access` | Early access request |
| `POST /api/contact` | Contact |
| `POST /api/apply` | Job application |
| `POST /api/subscribe` | Newsletter |
| `GET /api/health` | `{ ok: true }`; unknown `/api/*` is a JSON 404 |

Kept in localStorage (`tidewell:*` keys, `src/lib/store.ts`): saved roles,
applied roles, application drafts per role, the early-access draft and
receipt, the newsletter address and the calculator inputs.

## Style guide

`/styleguide` (linked from the footer) renders the real components: colour
swatches with hex values, the type scale, spacing, radii, shadows, motion
tokens with a replay button, and every component in its states (default,
hover, focus-visible, pressed, disabled, loading, error, empty). States are
pinned with `data-force="hover|focus|pressed"`. The site is dark only.

## Accessibility and motion

Skip link, focus moved to `<main>` on navigation, visible focus rings, a
focus-trapped mobile menu (Esc closes, focus returns), labelled fields with
errors wired via `aria-describedby`. With `prefers-reduced-motion` the
streaks, float and plasma pulse stop and reveals only fade.
