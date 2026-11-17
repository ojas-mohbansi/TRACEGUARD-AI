// Postbuild script for Cloudflare Workers & Pages.
// Ensures dist/client is clean and generates Pages compatibility artifacts (_headers, _routes.json, _worker.js).
import { readdirSync, rmSync, statSync, copyFileSync, writeFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

function clean(dir) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    if (name === '.DS_Store' || name === 'Thumbs.db') {
      rmSync(path, { recursive: true, force: true })
      continue
    }
    if (statSync(path).isDirectory()) clean(path)
  }
}

const clientDir = fileURLToPath(new URL('../dist/client', import.meta.url))
const workerFile = fileURLToPath(new URL('../dist/traceguard_ai/index.js', import.meta.url))

try {
  clean(clientDir)

  // 1. Pages Advanced Mode Worker: copy compiled Hono worker to _worker.js
  if (existsSync(workerFile)) {
    copyFileSync(workerFile, join(clientDir, '_worker.js'))
  }

  // 2. Pages _headers configuration for edge security and cache headers
  const headersContent = `/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self' http: https: ws: wss:; frame-ancestors 'none'; base-uri 'self';

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/robots.txt
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400
  Content-Type: text/plain; charset=utf-8

/sitemap.xml
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400
  Content-Type: application/xml; charset=utf-8

/site.webmanifest
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400
  Content-Type: application/manifest+json; charset=utf-8
`
  writeFileSync(join(clientDir, '_headers'), headersContent, 'utf-8')

  // 3. Pages _routes.json: route all paths to _worker.js so it controls 404s and cache policies
  const routesContent = JSON.stringify({
    version: 1,
    include: ["/*"],
    exclude: []
  }, null, 2)
  writeFileSync(join(clientDir, '_routes.json'), routesContent, 'utf-8')

  // 4. Cloudflare Pages true 404 support: generate 404.html so Pages serves genuine 404 HTTP status
  if (existsSync(join(clientDir, 'index.html'))) {
    copyFileSync(join(clientDir, 'index.html'), join(clientDir, '404.html'))
  }
} catch (e) {
  console.error('Postbuild notice:', e.message)
}
