import { Hono } from 'hono'
import { hasErrors, validateContact, validateEmail } from '../lib/validate'

// The Cloudflare Worker in front of the static site.
type Env = {
  ASSETS: Fetcher
}

const app = new Hono<{ Bindings: Env }>()

const KNOWN_ROUTES = new Set([
  '/',
  '/technology',
  '/automaton',
  '/architecture',
  '/research',
  '/presentation',
  '/about',
  '/styleguide',
])

const SECURITY_HEADERS: Record<string, string> = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Content-Security-Policy':
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self' http: https: ws: wss:; frame-ancestors 'none'; base-uri 'self';",
}

function applySecurityAndCacheHeaders(res: Response, path: string): Response {
  const headers = new Headers(res.headers)

  // Apply standard security headers
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    headers.set(key, value)
  }

  // Smart caching headers
  if (path.startsWith('/assets/')) {
    // Fingerprinted JS and CSS assets: 1 year immutable cache
    headers.set('Cache-Control', 'public, max-age=31536000, immutable')
  } else if (path === '/robots.txt' || path === '/sitemap.xml' || path === '/site.webmanifest') {
    // SEO and manifest assets: 1 hour cache with stale-while-revalidate
    headers.set('Cache-Control', 'public, max-age=3600, stale-while-revalidate=86400')
    if (path === '/robots.txt') {
      headers.set('Content-Type', 'text/plain; charset=utf-8')
    } else if (path === '/sitemap.xml') {
      headers.set('Content-Type', 'application/xml; charset=utf-8')
    } else if (path === '/site.webmanifest') {
      headers.set('Content-Type', 'application/manifest+json; charset=utf-8')
    }
  } else if (headers.get('Content-Type')?.includes('text/html')) {
    // HTML pages: must revalidate to serve latest deployments immediately
    headers.set('Cache-Control', 'public, max-age=0, must-revalidate')
  }

  return new Response(res.status === 304 ? null : res.body, {
    status: res.status,
    statusText: res.statusText,
    headers,
  })
}

async function body<T>(c: { req: { json: <U>() => Promise<U> } }): Promise<Partial<T> | null> {
  try {
    const v = await c.req.json<Partial<T>>()
    return v && typeof v === 'object' ? v : null
  } catch {
    return null
  }
}

// ── API Routes ──────────────────────────────────────────────────
app.get('/api/health', (c) => c.json({ ok: true, project: 'TraceGuard AI', version: '1.0.0' }))

app.post('/api/contact', async (c) => {
  const v = await body<Record<string, string>>(c)
  if (!v) return c.json({ error: 'Send a JSON body.' }, 400)
  const errors = validateContact(v)
  if (hasErrors(errors)) return c.json({ error: 'Check the highlighted fields.', errors }, 422)
  return c.json({ ok: true, reference: `TG-${Date.now().toString(36).toUpperCase()}` })
})

app.post('/api/subscribe', async (c) => {
  const v = await body<{ email: string }>(c)
  if (!v) return c.json({ error: 'Send a JSON body.' }, 400)
  const err = validateEmail(v.email ?? '')
  if (err) return c.json({ error: err, errors: { email: err } }, 422)
  return c.json({ ok: true })
})

app.all('/api/*', (c) => c.json({ error: 'Endpoint not found' }, 404))

// ── Static Assets & SPA Document Routing ───────────────────────
app.all('*', async (c) => {
  const path = c.req.path
  const url = new URL(c.req.raw.url)

  // 1. Attempt to fetch asset directly from static assets binding
  let res = await c.env.ASSETS.fetch(c.req.raw)

  // 2. If the static asset was found (200 OK, 304 Not Modified, etc.), return with security & cache headers
  if (res.status < 400) {
    return applySecurityAndCacheHeaders(res, path)
  }

  // 3. If asset not found (404), determine appropriate response:
  // If it is a file request (has extension, e.g. .js, .css, .png, .map), return genuine 404 text, NEVER HTML
  const hasFileExtension = /\.[a-zA-Z0-9]+$/.test(path)
  if (hasFileExtension) {
    return new Response('404 Not Found', {
      status: 404,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'X-Content-Type-Options': 'nosniff',
      },
    })
  }

  // 4. For page navigation paths:
  // Normalize path (strip trailing slashes, keep '/' for root)
  const normalizedPath = path.replace(/\/+$/, '') || '/'

  // Fetch index.html from static assets
  const indexUrl = new URL('/index.html', url.origin)
  const indexReq = new Request(indexUrl.toString(), {
    method: 'GET',
    headers: c.req.raw.headers,
  })
  const htmlRes = await c.env.ASSETS.fetch(indexReq)

  if (KNOWN_ROUTES.has(normalizedPath)) {
    // Known public SPA route: return index.html with 200 OK
    return applySecurityAndCacheHeaders(htmlRes, path)
  }

  // Unknown route: return index.html with 404 Not Found status!
  // This allows the client-side router to render <NotFound /> while HTTP clients and search crawlers see 404.
  const notFoundHeaders = new Headers(htmlRes.headers)
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    notFoundHeaders.set(key, value)
  }
  notFoundHeaders.set('Cache-Control', 'no-cache, no-store')

  return new Response(htmlRes.body, {
    status: 404,
    statusText: 'Not Found',
    headers: notFoundHeaders,
  })
})

export default app
