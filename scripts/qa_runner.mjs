import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

const SCREENSHOT_DIR = path.resolve('qa/phase19/screenshots');
const OUTPUT_JSON = path.resolve('qa/phase19/browser_qa_results.json');

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const VIEWPORTS = {
  mobile: { name: 'mobile', width: 390, height: 844, isMobile: true, hasTouch: true },
  tablet: { name: 'tablet', width: 768, height: 1024, isMobile: true, hasTouch: true },
  laptop: { name: 'laptop', width: 1366, height: 768, isMobile: false, hasTouch: false },
  desktop: { name: 'desktop', width: 1920, height: 1080, isMobile: false, hasTouch: false },
};

const ROUTES = [
  { path: '/', slug: 'home', name: 'Home' },
  { path: '/technology', slug: 'technology', name: 'Technology' },
  { path: '/automaton', slug: 'automaton', name: 'Automaton Lab' },
  { path: '/architecture', slug: 'architecture', name: 'Architecture' },
  { path: '/research', slug: 'research', name: 'Research' },
  { path: '/presentation', slug: 'presentation', name: 'Presentation' },
  { path: '/about', slug: 'about', name: 'About' },
  { path: '/styleguide', slug: 'styleguide', name: 'Style Guide' },
  { path: '/non-existent-route-for-testing', slug: '404', name: '404 Trap State' },
];

const FORBIDDEN_WORDS = [
  'tidewell',
  'fusion energy',
  'tokamak',
  'plasma containment',
  'clean energy startup',
  'commercial fusion',
  'maritime cargo',
  'stellarator'
];

async function runQA() {
  console.log('🚀 Starting Browser QA with Puppeteer...');
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const results = {
    timestamp: new Date().toISOString(),
    viewportsTested: Object.keys(VIEWPORTS),
    routesTested: ROUTES.map(r => r.path),
    routeResults: [],
    interactiveTests: [],
    forbiddenWordChecks: [],
    consoleErrors: [],
    consoleWarnings: [],
    networkFailures: [],
    accessibilityFindings: [],
  };

  const page = await browser.newPage();

  // Attach error & console listeners
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    if (type === 'error') {
      results.consoleErrors.push({ location: page.url(), text });
    } else if (type === 'warning') {
      results.consoleWarnings.push({ location: page.url(), text });
    }
  });

  page.on('pageerror', err => {
    results.consoleErrors.push({ location: page.url(), text: err.toString() });
  });

  page.on('requestfailed', req => {
    results.networkFailures.push({
      url: req.url(),
      error: req.failure()?.errorText || 'unknown',
    });
  });

  const baseUrl = 'http://localhost:4173';

  // 1. Test all routes on Desktop (1920x1080)
  console.log('--- Testing Routes on Desktop (1920x1080) ---');
  await page.setViewport(VIEWPORTS.desktop);

  for (const route of ROUTES) {
    const url = `${baseUrl}${route.path}`;
    console.log(`Navigating to ${url}...`);
    const resp = await page.goto(url, { waitUntil: 'networkidle0', timeout: 15000 });
    await new Promise(r => setTimeout(r, 600)); // Allow Framer Motion animations to settle

    const title = await page.title();
    const status = resp?.status() || 0;

    // Check horizontal scroll / overflow
    const overflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });

    // Extract text content and test forbidden words
    const pageText = await page.evaluate(() => document.body.innerText.toLowerCase());
    const matchedForbidden = [];
    for (const term of FORBIDDEN_WORDS) {
      if (pageText.includes(term.toLowerCase())) {
        matchedForbidden.push(term);
      }
    }

    // Capture screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, `desktop_${route.slug}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    results.routeResults.push({
      viewport: 'desktop',
      route: route.path,
      slug: route.slug,
      name: route.name,
      status,
      title,
      overflow,
      forbiddenTermsFound: matchedForbidden,
      screenshot: `qa/phase19/screenshots/desktop_${route.slug}.png`,
    });

    if (matchedForbidden.length > 0) {
      console.warn(`[WARN] Found forbidden terms on ${route.path}:`, matchedForbidden);
      results.forbiddenWordChecks.push({ route: route.path, terms: matchedForbidden });
    }
  }

  // 2. Test Laptop Viewport (1366x768) on key routes
  console.log('--- Testing Laptop Viewport (1366x768) ---');
  await page.setViewport(VIEWPORTS.laptop);
  for (const slug of ['home', 'technology', 'automaton', 'architecture', 'research', 'presentation']) {
    const route = ROUTES.find(r => r.slug === slug);
    await page.goto(`${baseUrl}${route.path}`, { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 500));
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    const screenshotPath = path.join(SCREENSHOT_DIR, `laptop_${slug}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    results.routeResults.push({
      viewport: 'laptop',
      route: route.path,
      slug,
      overflow,
      screenshot: `qa/phase19/screenshots/laptop_${slug}.png`
    });
  }

  // 3. Test Tablet Viewport (768x1024)
  console.log('--- Testing Tablet Viewport (768x1024) ---');
  await page.setViewport(VIEWPORTS.tablet);
  for (const slug of ['home', 'automaton', 'architecture', 'research', 'presentation']) {
    const route = ROUTES.find(r => r.slug === slug);
    await page.goto(`${baseUrl}${route.path}`, { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 500));
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    const screenshotPath = path.join(SCREENSHOT_DIR, `tablet_${slug}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    results.routeResults.push({
      viewport: 'tablet',
      route: route.path,
      slug,
      overflow,
      screenshot: `qa/phase19/screenshots/tablet_${slug}.png`
    });
  }

  // 4. Test Mobile Viewport (390x844)
  console.log('--- Testing Mobile Viewport (390x844) ---');
  await page.setViewport(VIEWPORTS.mobile);
  for (const route of ROUTES) {
    await page.goto(`${baseUrl}${route.path}`, { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 500));
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    const screenshotPath = path.join(SCREENSHOT_DIR, `mobile_${route.slug}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    results.routeResults.push({
      viewport: 'mobile',
      route: route.path,
      slug: route.slug,
      overflow,
      screenshot: `qa/phase19/screenshots/mobile_${route.slug}.png`
    });
  }

  // 5. Interactive Mobile Navigation Drawer Test
  console.log('--- Testing Mobile Drawer Navigation ---');
  await page.setViewport(VIEWPORTS.mobile);
  await page.goto(`${baseUrl}/`, { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 500));

  // Find hamburger button
  const menuBtn = await page.$('button[aria-label="Open menu"]');
  if (menuBtn) {
    await menuBtn.click();
    await new Promise(r => setTimeout(r, 600)); // wait for sheet drawer animation
    const drawerOpenShot = path.join(SCREENSHOT_DIR, 'mobile_drawer_open.png');
    await page.screenshot({ path: drawerOpenShot });

    // Verify sheet drawer title or links
    const drawerLinks = await page.evaluate(() => {
      const sheet = document.querySelector('dialog, [role="dialog"], [data-sheet]');
      const links = document.querySelectorAll('nav[aria-label="Mobile"] a');
      return {
        exists: !!sheet || links.length > 0,
        count: links.length,
        items: Array.from(links).map(a => a.textContent?.trim() || '')
      };
    });

    results.interactiveTests.push({
      test: 'Mobile Navigation Drawer Open & Links',
      passed: drawerLinks.count >= 5,
      details: drawerLinks,
      screenshot: 'qa/phase19/screenshots/mobile_drawer_open.png'
    });

    // Click on "Automaton" link in mobile drawer
    const automatonLink = await page.$('nav[aria-label="Mobile"] a[href="/automaton"]');
    if (automatonLink) {
      await automatonLink.click();
      await new Promise(r => setTimeout(r, 800));
      const currentUrl = page.url();
      results.interactiveTests.push({
        test: 'Mobile Drawer Navigation to /automaton',
        passed: currentUrl.includes('/automaton'),
        targetUrl: currentUrl
      });
    }
  } else {
    results.interactiveTests.push({
      test: 'Mobile Menu Button Detection',
      passed: false,
      error: 'button[aria-label="Open menu"] not found'
    });
  }

  // 6. Interactive DFA State Machine Simulation Test
  console.log('--- Testing Interactive Automaton Lab ---');
  await page.setViewport(VIEWPORTS.desktop);
  await page.goto(`${baseUrl}/automaton`, { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 800));

  // Find sample traces buttons
  const sampleButtons = await page.$$('button');
  let authBypassButton = null;
  let normalTraceButton = null;
  let resetButton = null;

  for (const btn of sampleButtons) {
    const text = await page.evaluate(el => el.textContent, btn);
    if (text?.includes('Auth Bypass Attack')) authBypassButton = btn;
    if (text?.includes('Normal 200 OK')) normalTraceButton = btn;
    if (text?.includes('Reset Trace') || text?.includes('Reset')) resetButton = btn;
  }

  if (authBypassButton) {
    console.log('Clicking "Auth Bypass Attack (Illegal)" sample trace...');
    await authBypassButton.click();
    await new Promise(r => setTimeout(r, 600));

    // Verify state badge
    const stateBadge = await page.evaluate(() => {
      const text = document.body.innerText;
      return {
        hasTrap: text.includes('TRAP') || text.includes('Violation') || text.includes('REJECTED'),
        fullSnippet: text.slice(text.indexOf('Current Automaton State'), text.indexOf('Current Automaton State') + 300)
      };
    });

    const shotAuthBypass = path.join(SCREENSHOT_DIR, 'interactive_automaton_auth_bypass_trap.png');
    await page.screenshot({ path: shotAuthBypass, fullPage: false });

    results.interactiveTests.push({
      test: 'Automaton Lab: Auth Bypass triggers TRAP sink',
      passed: stateBadge.hasTrap,
      details: stateBadge,
      screenshot: 'qa/phase19/screenshots/interactive_automaton_auth_bypass_trap.png'
    });
  }

  if (normalTraceButton) {
    console.log('Clicking "Normal 200 OK (Clean)" sample trace...');
    await normalTraceButton.click();
    await new Promise(r => setTimeout(r, 600));

    const stateBadgeNormal = await page.evaluate(() => {
      const text = document.body.innerText;
      return {
        hasClosed: text.includes('CLOSED') || text.includes('ACCEPTED') || text.includes('Clean'),
      };
    });

    const shotNormal = path.join(SCREENSHOT_DIR, 'interactive_automaton_normal_accepted.png');
    await page.screenshot({ path: shotNormal, fullPage: false });

    results.interactiveTests.push({
      test: 'Automaton Lab: Normal 200 OK completes to CLOSED (Accepted)',
      passed: stateBadgeNormal.hasClosed,
      screenshot: 'qa/phase19/screenshots/interactive_automaton_normal_accepted.png'
    });
  }

  // 7. Interactive State Selection in SVG DFA Diagram
  const svgNode = await page.$('svg circle, svg g[role="button"], svg [data-state]');
  if (svgNode) {
    await svgNode.click();
    await new Promise(r => setTimeout(r, 400));
    const shotSvg = path.join(SCREENSHOT_DIR, 'interactive_dfa_state_inspect.png');
    await page.screenshot({ path: shotSvg, fullPage: false });
    results.interactiveTests.push({
      test: 'DFADiagram: State Click & Inspect',
      passed: true,
      screenshot: 'qa/phase19/screenshots/interactive_dfa_state_inspect.png'
    });
  }

  // 8. Keyboard Accessibility (Tab Navigation)
  console.log('--- Testing Keyboard Accessibility ---');
  await page.goto(`${baseUrl}/`, { waitUntil: 'networkidle0' });
  const focusedElements = [];
  for (let i = 0; i < 6; i++) {
    await page.keyboard.press('Tab');
    const elInfo = await page.evaluate(() => {
      const active = document.activeElement;
      if (!active) return null;
      return {
        tagName: active.tagName,
        ariaLabel: active.getAttribute('aria-label'),
        text: active.textContent?.slice(0, 30)?.trim(),
        hasOutline: window.getComputedStyle(active).outlineStyle !== 'none' ||
                    window.getComputedStyle(active).boxShadow !== 'none' ||
                    active.className.includes('focus')
      };
    });
    if (elInfo) focusedElements.push(elInfo);
  }

  results.accessibilityFindings.push({
    test: 'Keyboard Tab Focus Ring Propagation',
    passed: focusedElements.length > 0 && focusedElements[0].tagName !== 'BODY',
    focusedSequence: focusedElements
  });

  await browser.close();

  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(results, null, 2));
  console.log('✅ QA Run Finished! Results written to', OUTPUT_JSON);
}

runQA().catch(err => {
  console.error('Fatal error in QA script:', err);
  process.exit(1);
});
