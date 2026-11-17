import fs from 'node:fs';
import path from 'node:path';

// Public indexable routes according to Phase 20 specification.
// /styleguide is excluded as an internal developer styleguide.
const PUBLIC_ROUTES = [
  { path: '', changefreq: 'weekly', priority: '1.0' },
  { path: '/technology', changefreq: 'monthly', priority: '0.8' },
  { path: '/automaton', changefreq: 'monthly', priority: '0.9' },
  { path: '/architecture', changefreq: 'monthly', priority: '0.8' },
  { path: '/research', changefreq: 'monthly', priority: '0.8' },
  { path: '/presentation', changefreq: 'monthly', priority: '0.7' },
  { path: '/about', changefreq: 'monthly', priority: '0.6' },
];

function resolveSiteUrl() {
  const envUrl = process.env.PUBLIC_SITE_URL || '';
  if (envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  // Safe default for local development and preview builds
  return 'http://localhost:5303';
}

function generateSitemap(baseUrl) {
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';

  for (const r of PUBLIC_ROUTES) {
    const loc = `${baseUrl}${r.path || '/'}`;
    xml += '  <url>\n';
    xml += `    <loc>${loc}</loc>\n`;
    xml += `    <changefreq>${r.changefreq}</changefreq>\n`;
    xml += `    <priority>${r.priority}</priority>\n`;
    xml += '  </url>\n';
  }

  xml += '</urlset>\n';
  return xml;
}

function generateRobots(baseUrl) {
  const sitemapUrl = `${baseUrl}/sitemap.xml`;
  return `# TraceGuard AI — Search Engine Robots Policy
# https://github.com/ojas-mohbansi/TRACEGUARD-AI

User-agent: *
Allow: /
Allow: /technology
Allow: /automaton
Allow: /architecture
Allow: /research
Allow: /presentation
Allow: /about
Allow: /brand/
Allow: /docs/
Allow: /assets/
Disallow: /styleguide
Disallow: /api/

Sitemap: ${sitemapUrl}
`;
}

function generateWebManifest() {
  return JSON.stringify(
    {
      name: 'TraceGuard AI',
      short_name: 'TraceGuard',
      description: 'Formal Protocol Verification & Network Intrusion Detection',
      start_url: '/',
      display: 'standalone',
      background_color: '#060810',
      theme_color: '#060810',
      icons: [
        {
          src: '/brand/traceguard-ai-icon-color.svg',
          sizes: 'any',
          type: 'image/svg+xml',
          purpose: 'any maskable',
        },
      ],
    },
    null,
    2
  );
}

function run() {
  const baseUrl = resolveSiteUrl();
  console.log(`Generating SEO discovery assets with base URL: ${baseUrl}...`);

  const cwd = process.cwd();
  const publicDir = fs.existsSync(path.join(cwd, 'public'))
    ? path.join(cwd, 'public')
    : path.resolve(cwd, 'website/public');

  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true });
  }

  // 1. sitemap.xml
  const sitemapContent = generateSitemap(baseUrl);
  const sitemapPath = path.join(publicDir, 'sitemap.xml');
  fs.writeFileSync(sitemapPath, sitemapContent, 'utf-8');
  console.log(`  ✓ Generated ${sitemapPath}`);

  // 2. robots.txt
  const robotsContent = generateRobots(baseUrl);
  const robotsPath = path.join(publicDir, 'robots.txt');
  fs.writeFileSync(robotsPath, robotsContent, 'utf-8');
  console.log(`  ✓ Generated ${robotsPath}`);

  // 3. site.webmanifest
  const manifestContent = generateWebManifest();
  const manifestPath = path.join(publicDir, 'site.webmanifest');
  fs.writeFileSync(manifestPath, manifestContent, 'utf-8');
  console.log(`  ✓ Generated ${manifestPath}`);
}

run();
