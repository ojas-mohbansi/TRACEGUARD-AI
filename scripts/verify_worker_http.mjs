import fs from 'node:fs';
import path from 'node:path';

const BASE_URL = 'http://127.0.0.1:8787';

const CHECKS = [
  { path: '/', expectedStatus: 200, expectedContentType: 'text/html', desc: 'Homepage' },
  { path: '/technology', expectedStatus: 200, expectedContentType: 'text/html', desc: 'Technology Page' },
  { path: '/automaton', expectedStatus: 200, expectedContentType: 'text/html', desc: 'Automaton Lab' },
  { path: '/architecture', expectedStatus: 200, expectedContentType: 'text/html', desc: 'Architecture Page' },
  { path: '/research', expectedStatus: 200, expectedContentType: 'text/html', desc: 'Research Page' },
  { path: '/presentation', expectedStatus: 200, expectedContentType: 'text/html', desc: 'Presentation Page' },
  { path: '/about', expectedStatus: 200, expectedContentType: 'text/html', desc: 'About Academic Page' },
  { path: '/styleguide', expectedStatus: 200, expectedContentType: 'text/html', desc: 'StyleGuide Page' },
  { path: '/robots.txt', expectedStatus: 200, expectedContentType: 'text/plain', desc: 'Robots Policy' },
  { path: '/sitemap.xml', expectedStatus: 200, expectedContentType: 'application/xml', desc: 'Sitemap Index' },
  { path: '/site.webmanifest', expectedStatus: 200, expectedContentType: 'application/manifest+json', desc: 'Web App Manifest' },
  { path: '/favicon.svg', expectedStatus: 200, expectedContentType: 'image/svg+xml', desc: 'Vector Favicon' },
  { path: '/api/health', expectedStatus: 200, expectedContentType: 'application/json', desc: 'Worker API Health' },
  { path: '/assets/non-existent-script.js', expectedStatus: 404, expectedContentType: 'text/plain', desc: 'Missing Asset File Handling' },
  { path: '/trap-404-test-route', expectedStatus: 404, expectedContentType: 'text/html', desc: 'Unknown Route 404 Handling' },
];

async function runHttpChecks() {
  console.log(`Starting HTTP route verification against Cloudflare Workers preview: ${BASE_URL}...`);
  const results = {
    timestamp: new Date().toISOString(),
    workerUrl: BASE_URL,
    totalChecks: CHECKS.length,
    passed: 0,
    failed: 0,
    checks: [],
  };

  for (const check of CHECKS) {
    const url = `${BASE_URL}${check.path}`;
    try {
      const res = await fetch(url, { redirect: 'manual' });
      const contentType = res.headers.get('content-type') || '';
      const cacheControl = res.headers.get('cache-control') || '';
      const xContentTypeOptions = res.headers.get('x-content-type-options') || '';
      const referrerPolicy = res.headers.get('referrer-policy') || '';
      const csp = res.headers.get('content-security-policy') || '';

      const statusMatch = res.status === check.expectedStatus;
      const typeMatch = check.expectedContentType ? contentType.includes(check.expectedContentType) : true;
      const passed = statusMatch && typeMatch;

      if (passed) {
        results.passed++;
        console.log(`  ✓ [${res.status}] ${check.path} (${check.desc}) - Content-Type: ${contentType.split(';')[0]}`);
      } else {
        results.failed++;
        console.error(`  ❌ [${res.status} vs ${check.expectedStatus}] ${check.path} (${check.desc}) - Content-Type: ${contentType}`);
      }

      results.checks.push({
        path: check.path,
        description: check.desc,
        expectedStatus: check.expectedStatus,
        actualStatus: res.status,
        expectedContentType: check.expectedContentType,
        actualContentType: contentType,
        cacheControl,
        headers: {
          'x-content-type-options': xContentTypeOptions,
          'referrer-policy': referrerPolicy,
          'content-security-policy': csp ? 'PRESENT' : 'NONE',
        },
        passed,
      });
    } catch (err) {
      results.failed++;
      console.error(`  ❌ Failed fetch on ${url}:`, err.message);
      results.checks.push({
        path: check.path,
        description: check.desc,
        error: err.message,
        passed: false,
      });
    }
  }

  const outPath = path.resolve('qa/phase20/http_route_checks.json');
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(results, null, 2), 'utf-8');
  console.log(`\nCompleted HTTP Route Verification: ${results.passed}/${results.totalChecks} passed.`);
  console.log(`Saved report to ${outPath}`);

  if (results.failed > 0) {
    process.exit(1);
  }
}

runHttpChecks().catch((err) => {
  console.error('Fatal HTTP check runner error:', err);
  process.exit(1);
});
