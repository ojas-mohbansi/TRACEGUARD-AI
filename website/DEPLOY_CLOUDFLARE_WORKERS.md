# TraceGuard AI — Cloudflare Workers Deployment Guide

**Target Application**: TraceGuard AI Marketing & Research Web Application  
**Runtime Architecture**: Cloudflare Workers with Static Assets (`@cloudflare/vite-plugin` + `wrangler`)  
**Package Manager**: Bun (`bun`)

---

## 1. Prerequisites

Before deploying TraceGuard AI to Cloudflare Workers, ensure the following are installed and configured:

1. **Bun Runtime** (v1.2+):
   ```bash
   bun --version
   ```
2. **Node.js** (v20+ or v22+ LTS recommended for toolchain compatibility):
   ```bash
   node --version
   ```
3. **Cloudflare Account**:
   - Free or Paid Cloudflare plan.
   - Account ID and zone privileges if attaching a custom apex or subdomain.

---

## 2. Required Domain & Environment Configuration

TraceGuard AI includes a strict Technical SEO engine that resolves canonical links, sitemaps, and Open Graph previews from `PUBLIC_SITE_URL`.

1. Copy the example configuration to a local environment file:
   ```bash
   cp .env.example .env.production
   ```
2. Set your verified production HTTPS domain:
   ```env
   PUBLIC_SITE_URL=https://traceguard.ai
   VITE_PUBLIC_SITE_URL=https://traceguard.ai
   ```
   > **Note**: Never use `http://` or placeholder domains in production. The SEO validation tool (`bun run seo:check`) will enforce HTTPS and reject placeholders.

---

## 3. Cloudflare Authentication

Authenticate Wrangler with your Cloudflare account:

```bash
bun run wrangler login
```

Verify your active profile and account:
```bash
bun run wrangler whoami
```

---

## 4. Local Workers Preview (`wrangler dev`)

Test the application against Cloudflare's exact local Workers runtime (Workerd) before building for production:

```bash
# 1. Run production build
bun run build

# 2. Start local Cloudflare Workers preview
bun run preview:cf
```

This starts `wrangler dev` on `http://localhost:8787` (or next available port). Verify:
- Direct route visits: `http://localhost:8787/technology`, `http://localhost:8787/automaton`
- Technical SEO endpoints: `http://localhost:8787/robots.txt`, `http://localhost:8787/sitemap.xml`
- Missing asset handling: `http://localhost:8787/assets/missing.js` returns genuine 404 (not HTML)
- Unknown path handling: `http://localhost:8787/unknown-route` returns HTTP 404 with the `<NotFound />` state

---

## 5. Production Build

Build the dual client bundle and Worker entrypoint:

```bash
bun run build
```

This runs:
1. `prebuild`: Generates `public/sitemap.xml`, `public/robots.txt`, and `public/site.webmanifest` using `PUBLIC_SITE_URL`.
2. `vite build`: Compiles:
   - Worker environment into `dist/traceguard_ai/`
   - Static client assets into `dist/client/`
3. `postbuild`: Cleans OS artifacts without stripping sourcemaps or asset ignore rules.

---

## 6. Typecheck & SEO Validation

Run automated pre-flight checks:

```bash
# 1. TypeScript validation
bun run typecheck

# 2. Technical SEO validation
bun run seo:check
```

Both commands must exit with code `0`.

---

## 7. Deployment Dry-Run (No Upload)

Simulate deployment packaging and verify asset manifests without uploading code to Cloudflare:

```bash
bun run deploy:dry
```

Expected output:
```text
⛅️ wrangler 4.x
Using redirected Wrangler configuration.
✨ Read 57+ files from the assets directory dist/client
Total Upload: ~62 KiB
Your Worker has access to the following bindings:
Binding env.ASSETS (Assets)
--dry-run: exiting now.
```

---

## 8. Actual Deployment Command

When you are ready to publish TraceGuard AI to Cloudflare Workers, execute:

```bash
bun run deploy
```

Wrangler will upload your compiled static assets to Cloudflare Workers KV/Asset storage, deploy the routing Worker, and output your live deployment URL:

```text
Uploaded traceguard-ai (x.xx sec)
Deployed traceguard-ai triggers:
  https://traceguard-ai.<your-subdomain>.workers.dev
Current Version ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 9. Custom Domain Configuration

To connect a custom domain (e.g. `traceguard.ai` or `fsm.traceguard.ai`):

### Option A: Via Cloudflare Dashboard
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to **Workers & Pages** > **traceguard-ai**.
3. Go to **Settings** > **Domains & Routes**.
4. Click **Add** > **Custom Domain**.
5. Enter your domain (e.g., `traceguard.ai`) and confirm. Cloudflare will automatically provision SSL certificates and configure DNS records.

### Option B: Via `wrangler.jsonc`
Add a `routes` definition in `wrangler.jsonc`:
```jsonc
{
  "name": "traceguard-ai",
  "routes": [
    { "pattern": "traceguard.ai/*", "zone_name": "traceguard.ai" },
    { "pattern": "www.traceguard.ai/*", "zone_name": "traceguard.ai" }
  ]
}
```
Then run:
```bash
bun run deploy
```

---

## 10. Post-Deployment Verification Checklist

Verify your live production deployment:

1. **HTTP Status Codes**:
   - `curl -I https://traceguard.ai/` -> `HTTP/2 200`
   - `curl -I https://traceguard.ai/technology` -> `HTTP/2 200`
   - `curl -I https://traceguard.ai/sitemap.xml` -> `HTTP/2 200` (`Content-Type: application/xml`)
   - `curl -I https://traceguard.ai/robots.txt` -> `HTTP/2 200` (`Content-Type: text/plain`)
   - `curl -I https://traceguard.ai/non-existent-trap` -> `HTTP/2 404`
2. **Security Headers**:
   - `X-Content-Type-Options: nosniff`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Content-Security-Policy` active
3. **Cache Invariants**:
   - Fingerprinted JS/CSS in `/assets/*` return `Cache-Control: public, max-age=31536000, immutable`
   - HTML documents return `Cache-Control: public, max-age=0, must-revalidate`

---

## 11. Search Engine Discovery (User-Performed Step)

Once the production domain is live:

1. **Google Search Console**:
   - Add property for `https://traceguard.ai`.
   - Submit Sitemap: `https://traceguard.ai/sitemap.xml`.
2. **Bing Webmaster Tools**:
   - Add site or import from Google Search Console.
   - Submit Sitemap: `https://traceguard.ai/sitemap.xml`.
