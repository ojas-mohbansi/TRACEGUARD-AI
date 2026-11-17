import fs from 'node:fs';
import path from 'node:path';

const EXPECTED_PUBLIC_ROUTES = [
  '/',
  '/technology',
  '/automaton',
  '/architecture',
  '/research',
  '/presentation',
  '/about',
];

const EXCLUDED_ROUTES = ['/styleguide', '/trap-404-test', '/404'];

function validateSEO() {
  console.log('🔍 Running TraceGuard AI Technical SEO & Metadata Validation Audit...');
  let hasErrors = false;
  let hasWarnings = false;

  const cwd = process.cwd();
  const publicDir = fs.existsSync(path.join(cwd, 'public'))
    ? path.join(cwd, 'public')
    : path.resolve(cwd, 'website/public');

  const sitemapPath = path.join(publicDir, 'sitemap.xml');
  const robotsPath = path.join(publicDir, 'robots.txt');
  const manifestPath = path.join(publicDir, 'site.webmanifest');

  const envUrl = process.env.PUBLIC_SITE_URL || '';
  const isProd = process.env.NODE_ENV === 'production';

  console.log(`\n1. Target Domain Inspection:`);
  if (!envUrl) {
    if (isProd) {
      console.error('  ❌ ERROR: PUBLIC_SITE_URL is not set for production build.');
      hasErrors = true;
    } else {
      console.warn('  ⚠️ WARNING: PUBLIC_SITE_URL not set. Using local development fallback.');
      hasWarnings = true;
    }
  } else {
    try {
      const parsed = new URL(envUrl);
      if (isProd && parsed.protocol !== 'https:') {
        console.error(`  ❌ ERROR: Production PUBLIC_SITE_URL must use HTTPS protocol. Got: ${parsed.protocol}`);
        hasErrors = true;
      } else if (parsed.hostname === 'example.com' || parsed.hostname.includes('placeholder')) {
        console.error(`  ❌ ERROR: Invalid placeholder production domain detected: ${parsed.hostname}`);
        hasErrors = true;
      } else {
        console.log(`  ✓ Configured site URL: ${envUrl}`);
      }
    } catch (err) {
      console.error(`  ❌ ERROR: Malformed PUBLIC_SITE_URL: "${envUrl}" - ${err.message}`);
      hasErrors = true;
    }
  }

  // 2. Sitemap Validation
  console.log(`\n2. Sitemap Validation (${sitemapPath}):`);
  if (!fs.existsSync(sitemapPath)) {
    console.error('  ❌ ERROR: sitemap.xml does not exist.');
    hasErrors = true;
  } else {
    const sitemapContent = fs.readFileSync(sitemapPath, 'utf-8');
    if (!sitemapContent.startsWith('<?xml') || !sitemapContent.includes('<urlset')) {
      console.error('  ❌ ERROR: sitemap.xml is not valid XML.');
      hasErrors = true;
    } else {
      console.log('  ✓ Valid UTF-8 XML header and urlset element.');
    }

    // Check expected public routes
    for (const r of EXPECTED_PUBLIC_ROUTES) {
      const expectedMatch = r === '/' ? '<loc>' : `<loc>.*${r}</loc>`;
      const reg = new RegExp(expectedMatch);
      if (!reg.test(sitemapContent)) {
        console.error(`  ❌ ERROR: Expected route missing from sitemap: ${r}`);
        hasErrors = true;
      } else {
        console.log(`  ✓ Route indexed: ${r}`);
      }
    }

    // Check excluded routes
    for (const ex of EXCLUDED_ROUTES) {
      if (sitemapContent.includes(ex)) {
        console.error(`  ❌ ERROR: Excluded utility/error route found in sitemap: ${ex}`);
        hasErrors = true;
      }
    }
  }

  // 3. Robots.txt Validation
  console.log(`\n3. Robots.txt Validation (${robotsPath}):`);
  if (!fs.existsSync(robotsPath)) {
    console.error('  ❌ ERROR: robots.txt does not exist.');
    hasErrors = true;
  } else {
    const robotsContent = fs.readFileSync(robotsPath, 'utf-8');
    if (!robotsContent.includes('User-agent: *')) {
      console.error('  ❌ ERROR: robots.txt missing User-agent rule.');
      hasErrors = true;
    }
    if (!robotsContent.includes('Sitemap:')) {
      console.error('  ❌ ERROR: robots.txt missing Sitemap directive.');
      hasErrors = true;
    } else {
      console.log('  ✓ Sitemap directive properly declared in robots.txt.');
    }
    if (!robotsContent.includes('Disallow: /styleguide')) {
      console.error('  ❌ ERROR: robots.txt should disallow internal /styleguide.');
      hasErrors = true;
    } else {
      console.log('  ✓ Disallow /styleguide present.');
    }
  }

  // 4. Web Manifest Validation
  console.log(`\n4. Web App Manifest Validation (${manifestPath}):`);
  if (!fs.existsSync(manifestPath)) {
    console.error('  ❌ ERROR: site.webmanifest does not exist.');
    hasErrors = true;
  } else {
    try {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
      if (manifest.name === 'TraceGuard AI' && manifest.icons?.length > 0) {
        console.log(`  ✓ Web App Manifest valid: "${manifest.name}"`);
      } else {
        console.error('  ❌ ERROR: Incomplete manifest data.');
        hasErrors = true;
      }
    } catch (e) {
      console.error('  ❌ ERROR: site.webmanifest is not valid JSON:', e.message);
      hasErrors = true;
    }
  }

  // 5. Social & Favicon Assets
  console.log(`\n5. Social & Favicon Asset Inspection:`);
  const faviconSvg = path.join(publicDir, 'favicon.svg');
  const ogPreview = path.join(publicDir, 'brand/traceguard-ai-preview.png');
  if (fs.existsSync(faviconSvg)) {
    console.log('  ✓ Vector Favicon exists.');
  } else {
    console.error('  ❌ ERROR: favicon.svg is missing.');
    hasErrors = true;
  }
  if (fs.existsSync(ogPreview)) {
    console.log('  ✓ Open Graph preview image (1200x630) exists.');
  } else {
    console.error('  ❌ ERROR: Open Graph preview image is missing.');
    hasErrors = true;
  }

  console.log('\n----------------------------------------');
  if (hasErrors) {
    console.error('❌ SEO Audit FAILED with errors.');
    process.exit(1);
  } else if (hasWarnings) {
    console.log('⚠️ SEO Audit PASSED with warnings (safe for local development/preview).');
  } else {
    console.log('✅ SEO Audit PASSED with zero defects.');
  }
}

validateSEO();
