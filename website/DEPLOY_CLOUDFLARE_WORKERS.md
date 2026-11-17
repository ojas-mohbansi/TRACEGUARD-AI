# TraceGuard AI — Cloudflare Pages & Workers Production Deployment Guide

**Target Application**: TraceGuard AI Marketing & Research Web Application  
**Runtime Architecture**: Cloudflare Pages (with Advanced Mode Edge Worker `_worker.js` + `_headers` + `_routes.json`)  
**Package Manager**: Bun (`bun` v1.2+)  
**Primary Production URL**: `https://traceguard-ai.pages.dev`  
**Workers Production Trigger**: `https://traceguard-ai.stylish00killer.workers.dev`  
**Account ID**: `a80bbebe00dec24588c0d0cd62a4e02c`  
**Project Name**: `traceguard-ai`  

---

## 1. Architecture Overview

TraceGuard AI deploys to Cloudflare Pages as a high-performance edge application:
1. **Static Client Assets**: Compiled React 19 SPA bundled with Vite and Tailwind CSS v4, served directly from Cloudflare's global edge network.
2. **Edge Worker Router (`_worker.js`)**: Compiled from `src/worker/index.ts` to `dist/client/_worker.js` and driven by `_routes.json`, providing:
   - Full control over dynamic status codes (true HTTP 404 for missing assets and unknown SPA routes).
   - Serverless API endpoints: `/api/health`, `/api/contact`, `/api/subscribe`.
3. **Security Invariants (`_headers` + Edge Worker)**:
   - `Content-Security-Policy`: Strict CSP with frame-ancestors `'none'`
   - `X-Content-Type-Options`: `nosniff`
   - `Referrer-Policy`: `strict-origin-when-cross-origin`
   - `Permissions-Policy`: `camera=(), microphone=(), geolocation=()`
4. **Smart Cache Policies**:
   - Fingerprinted JS/CSS in `/assets/*`: `public, max-age=31536000, immutable` (1 year)
   - SEO Assets (`sitemap.xml`, `robots.txt`, `site.webmanifest`): `public, max-age=3600, stale-while-revalidate=86400`
   - HTML documents: `public, max-age=0, must-revalidate`
   - Missing assets (file extensions): HTTP 404 `text/plain`
   - SPA unknown route: HTTP 404 status serving `<NotFound />` with `Cache-Control: no-cache, no-store`.

---

## 2. Production Environment Configuration

The production domain is configured via `website/.env.production`:
```env
PUBLIC_SITE_URL=https://traceguard-ai.pages.dev
VITE_PUBLIC_SITE_URL=https://traceguard-ai.pages.dev
```

During build (`bun run build`), the prebuild script `scripts/generate_seo_assets.mjs` generates:
- `website/public/sitemap.xml` with canonical `https://traceguard-ai.pages.dev/` URLs.
- `website/public/robots.txt` referencing `Sitemap: https://traceguard-ai.pages.dev/sitemap.xml`.
- `website/public/site.webmanifest`.

---

## 3. Deployment Lifecycle

Execute all commands inside the `website/` directory using Bun:

```bash
# 1. Typecheck
bun run typecheck

# 2. Production build (runs prebuild SEO generator + Vite build + postbuild cleanup)
bun run build

# 3. Technical SEO & Metadata validation
bun run seo:check

# 4. Deploy directly to Cloudflare Pages
bun run deploy
# or:
npx wrangler pages deploy dist/client --project-name traceguard-ai --branch main
```

---

## 4. Automated CI/CD Pipeline (`.github/workflows/deploy-website.yml`)

The website has a dedicated, path-filtered GitHub Actions workflow that executes ONLY when website assets or its workflow definition change.

### Path Filtering Invariant:
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'website/**'
      - '.github/workflows/deploy-website.yml'
  workflow_dispatch:
```

### Trigger Isolation Behavior:
| Modified Path | Backend CI (`ci.yml`) | Website Deployment (`deploy-website.yml`) |
|---|---|---|
| `backend/**` | **Runs** | **Does NOT run** |
| `frontend/**` (SaaS app) | **Runs** | **Does NOT run** |
| `website/**` | Does NOT trigger | **Runs** |
| `docs/**` | Does NOT trigger | **Does NOT run** |
| `presentation/**` | Does NOT trigger | **Does NOT run** |
| Root `README.md` | Does NOT trigger | **Does NOT run** |
| `.github/workflows/deploy-website.yml` | Does NOT trigger | **Runs** |

### Required GitHub Repository Secrets:
Configure the following secrets in GitHub Repository Settings (`Settings` > `Secrets and variables` > `Actions`):
1. `CLOUDFLARE_API_TOKEN`: Cloudflare API token with permissions for Pages and Workers scripts/assets.
2. `CLOUDFLARE_ACCOUNT_ID`: Cloudflare Account ID (`a80bbebe00dec24588c0d0cd62a4e02c`).

---

## 5. Live Verification Matrix

All 15 production route invariants are verified against `https://traceguard-ai.pages.dev`:
- `GET /` -> HTTP 200 `text/html`
- `GET /technology` -> HTTP 200 `text/html`
- `GET /automaton` -> HTTP 200 `text/html`
- `GET /architecture` -> HTTP 200 `text/html`
- `GET /research` -> HTTP 200 `text/html`
- `GET /presentation` -> HTTP 200 `text/html`
- `GET /about` -> HTTP 200 `text/html`
- `GET /sitemap.xml` -> HTTP 200 `application/xml`
- `GET /robots.txt` -> HTTP 200 `text/plain`
- `GET /favicon.svg` -> HTTP 200 `image/svg+xml`
- `GET /site.webmanifest` -> HTTP 200 `application/manifest+json`
- `GET /brand/traceguard-ai-preview.png` -> HTTP 200 `image/png`
- `GET /api/health` -> HTTP 200 `application/json`
- `GET /assets/non-existent-script.js` -> HTTP 404 `text/plain`
- `GET /trap-404-test-route` -> HTTP 404 `text/html`
