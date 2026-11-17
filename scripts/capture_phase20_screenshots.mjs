import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

const targetDirArg = process.argv[2] || 'before';
const baseUrlArg = process.argv[3] || 'http://localhost:5303';
const SCREENSHOT_DIR = path.resolve(`qa/phase20/screenshots/${targetDirArg}`);

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const VIEWPORTS = [
  { name: 'mobile_390x844', width: 390, height: 844, isMobile: true, hasTouch: true },
  { name: 'tablet_768x1024', width: 768, height: 1024, isMobile: true, hasTouch: true },
  { name: 'laptop_1366x768', width: 1366, height: 768, isMobile: false, hasTouch: false },
  { name: 'desktop_1920x1080', width: 1920, height: 1080, isMobile: false, hasTouch: false },
];

const ROUTES = [
  { path: '/', slug: 'home', title: 'Home' },
  { path: '/technology', slug: 'technology', title: 'Technology' },
  { path: '/automaton', slug: 'automaton', title: 'Automaton' },
  { path: '/architecture', slug: 'architecture', title: 'Architecture' },
  { path: '/research', slug: 'research', title: 'Research' },
  { path: '/presentation', slug: 'presentation', title: 'Presentation' },
  { path: '/about', slug: 'about', title: 'About' },
  { path: '/styleguide', slug: 'styleguide', title: 'StyleGuide' },
  { path: '/trap-404-test', slug: '404', title: '404 Trap State' },
];

async function captureAll() {
  console.log(`Starting Phase 20 Screenshot Capture into ${SCREENSHOT_DIR} against ${baseUrlArg}...`);
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const report = {
    targetDir: targetDirArg,
    baseUrl: baseUrlArg,
    timestamp: new Date().toISOString(),
    routesChecked: [],
    consoleErrors: [],
    layoutIssues: [],
  };

  const page = await browser.newPage();

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      report.consoleErrors.push({ text: msg.text(), location: msg.location() });
    }
  });

  for (const vp of VIEWPORTS) {
    console.log(`\n--- Viewport: ${vp.name} (${vp.width}x${vp.height}) ---`);
    await page.setViewport(vp);

    for (const r of ROUTES) {
      const url = `${baseUrlArg}${r.path}`;
      try {
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 15000 });
        await new Promise((resolve) => setTimeout(resolve, 250));

        // Smooth scroll through entire page to trigger lazy loading and IntersectionObserver animations
        await page.evaluate(async () => {
          await new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 400;
            const timer = setInterval(() => {
              const scrollHeight = document.documentElement.scrollHeight;
              window.scrollBy(0, distance);
              totalHeight += distance;
              if (totalHeight >= scrollHeight) {
                clearInterval(timer);
                window.scrollTo(0, 0);
                setTimeout(resolve, 150);
              }
            }, 40);
          });
        });
        await new Promise((resolve) => setTimeout(resolve, 350));

        // Check for horizontal overflow
        const overflow = await page.evaluate(() => {
          return {
            scrollWidth: document.documentElement.scrollWidth,
            clientWidth: document.documentElement.clientWidth,
            hasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
          };
        });

        if (overflow.hasHorizontalOverflow) {
          report.layoutIssues.push({
            route: r.path,
            viewport: vp.name,
            issue: `Horizontal overflow detected: scrollWidth (${overflow.scrollWidth}) > clientWidth (${overflow.clientWidth})`,
          });
          console.warn(`  [OVERFLOW] ${r.slug} on ${vp.name}: ${overflow.scrollWidth} > ${overflow.clientWidth}`);
        }

        // Capture full page screenshot
        const filename = `${vp.name}_${r.slug}.png`;
        const filePath = path.join(SCREENSHOT_DIR, filename);
        await page.screenshot({ path: filePath, fullPage: true });
        console.log(`  Saved ${filename}`);

        report.routesChecked.push({
          route: r.path,
          slug: r.slug,
          viewport: vp.name,
          overflow,
          file: filename,
        });

        // Special: If on mobile and home page, capture mobile menu opened
        if (vp.name === 'mobile_390x844' && r.slug === 'home') {
          const menuBtn = await page.$('button[aria-label="Open menu"], header button[aria-expanded]');
          if (menuBtn) {
            await menuBtn.click();
            await new Promise((res) => setTimeout(res, 300));
            const menuFile = `${vp.name}_home_mobile_menu.png`;
            await page.screenshot({ path: path.join(SCREENSHOT_DIR, menuFile) });
            console.log(`  Saved ${menuFile}`);
            // Close it
            const closeBtn = await page.$('button[aria-label="Close menu"], button[aria-label="Close"]');
            if (closeBtn) await closeBtn.click();
            else await menuBtn.click();
            await new Promise((res) => setTimeout(res, 200));
          }
        }
      } catch (err) {
        console.error(`  Error on ${url} (${vp.name}):`, err.message);
        report.layoutIssues.push({ route: r.path, viewport: vp.name, error: err.message });
      }
    }
  }

  // Also capture interactive components on Automaton Lab (e.g. desktop view)
  console.log('\n--- Capturing Interactive Components ---');
  await page.setViewport({ width: 1366, height: 768, isMobile: false, hasTouch: false });
  await page.goto(`${baseUrlArg}/automaton`, { waitUntil: 'networkidle0' });
  await new Promise((resolve) => setTimeout(resolve, 500));
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'automaton_interactive_overview.png') });

  // Test interactive trace simulator button if present
  const stepped = await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const btn = buttons.find((b) => /step|run|next|verify|test/i.test(b.textContent || ''));
    if (btn) {
      btn.click();
      return true;
    }
    return false;
  });

  if (stepped) {
    await new Promise((resolve) => setTimeout(resolve, 400));
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'automaton_interactive_stepped.png') });
  }

  await browser.close();

  fs.writeFileSync(
    path.join(SCREENSHOT_DIR, `capture_summary_${targetDirArg}.json`),
    JSON.stringify(report, null, 2),
    'utf-8'
  );
  console.log(`Done. Saved summary to capture_summary_${targetDirArg}.json.`);
}

captureAll().catch((err) => {
  console.error('Fatal screenshot runner error:', err);
  process.exit(1);
});
