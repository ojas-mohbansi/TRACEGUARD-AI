import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

const SCREENSHOT_DIR = path.resolve('qa/phase21/screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const BASE_URL = 'http://localhost:5174';

async function runPresentationQA() {
  console.log(`Starting Phase 21 Presentation Mode QA against ${BASE_URL}...`);
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  const testReport = {
    timestamp: new Date().toISOString(),
    baseUrl: BASE_URL,
    checks: [],
    errors: [],
  };

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      testReport.errors.push(msg.text());
    }
  });

  try {
    // 1. Navigate to SaaS app with presentation mode query param
    console.log('Navigating to http://localhost:5174/?presentation=true...');
    await page.goto(`${BASE_URL}/?presentation=true`, { waitUntil: 'networkidle0', timeout: 15000 });
    await new Promise((r) => setTimeout(r, 2000));

    // Verify modal is open
    const modalExists = await page.$('div[role="dialog"][aria-label*="Presentation Mode"]');
    console.log('Presentation Mode modal open:', Boolean(modalExists));

    // Helper to jump to slide index (0-based) using keyboard or thumbnails
    async function jumpToSlide(slideNum) {
      // Find thumbnail button with aria-label containing slide number
      const targetAria = `Jump to slide ${slideNum}:`;
      const clicked = await page.evaluate((target) => {
        const buttons = Array.from(document.querySelectorAll('button[aria-label*="Jump to slide"]'));
        const btn = buttons.find((b) => b.getAttribute('aria-label')?.startsWith(target));
        if (btn) {
          btn.click();
          return true;
        }
        return false;
      }, targetAria);

      if (!clicked) {
        // Fallback: use Home then press ArrowRight (slideNum - 1) times
        await page.keyboard.press('Home');
        await new Promise((r) => setTimeout(r, 100));
        for (let i = 1; i < slideNum; i++) {
          await page.keyboard.press('ArrowRight');
          await new Promise((r) => setTimeout(r, 80));
        }
      }
      await new Promise((r) => setTimeout(r, 600));
    }

    // Helper to extract displayed slide and presenter info
    async function getSlideState() {
      return await page.evaluate(() => {
        const headerText = document.querySelector('header')?.innerText || '';
        const presenterHeading = document.querySelector('aside h3')?.innerText || '';
        const topic = document.querySelector('aside span.text-white')?.innerText || '';
        const scriptText = document.querySelector('aside .whitespace-pre-line')?.innerText || '';
        const slideIndex = document.querySelector('header span.text-white')?.innerText || '';
        return { headerText, presenterHeading, topic, scriptText, slideIndex };
      });
    }

    // Capture 1: Slide 1 - Tanmay (Presenter View)
    console.log('Testing Slide 1 (Presenter 1: Tanmay)...');
    await jumpToSlide(1);
    const s1 = await getSlideState();
    console.log(`  Slide 1: Presenter = ${s1.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_01_tanmay_presenter_view.png') });

    // Capture 2: Slide 1 - Audience View
    console.log('Switching to Audience View on Slide 1...');
    await page.keyboard.press('p');
    await new Promise((r) => setTimeout(r, 600));
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_01_audience_view.png') });
    // Switch back to Presenter View
    await page.keyboard.press('p');
    await new Promise((r) => setTimeout(r, 600));

    // Capture 3: Slide 4 - Tanmay before handoff
    console.log('Testing Slide 4 (Tanmay before handoff)...');
    await jumpToSlide(4);
    const s4 = await getSlideState();
    console.log(`  Slide 4: Presenter = ${s4.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_04_tanmay_before_handoff.png') });

    // Boundary 1: Slide 4 -> Slide 5 (Tanmay -> Karthik Sai)
    console.log('Testing Boundary 1: Slide 4 -> Slide 5 (Tanmay -> Karthik Sai)...');
    await page.keyboard.press('ArrowRight');
    await new Promise((r) => setTimeout(r, 600));
    const s5 = await getSlideState();
    console.log(`  Slide 5: Presenter = ${s5.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_05_karthik_sai_presenter_view.png') });

    // Capture 5: Slide 9 - Karthik Sai before handoff
    console.log('Testing Slide 9 (Karthik Sai before handoff)...');
    await jumpToSlide(9);
    const s9 = await getSlideState();
    console.log(`  Slide 9: Presenter = ${s9.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_09_karthik_sai_before_handoff.png') });

    // Boundary 2: Slide 9 -> Slide 10 (Karthik Sai -> Ojas Mohbansi)
    console.log('Testing Boundary 2: Slide 9 -> Slide 10 (Karthik Sai -> Ojas Mohbansi)...');
    await page.keyboard.press('ArrowRight');
    await new Promise((r) => setTimeout(r, 600));
    const s10 = await getSlideState();
    console.log(`  Slide 10: Presenter = ${s10.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_10_ojas_mohbansi_presenter_view.png') });

    // Capture 7: Slide 14 - Ojas Mohbansi before handoff
    console.log('Testing Slide 14 (Ojas Mohbansi before handoff)...');
    await jumpToSlide(14);
    const s14 = await getSlideState();
    console.log(`  Slide 14: Presenter = ${s14.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_14_ojas_mohbansi_before_handoff.png') });

    // Boundary 3: Slide 14 -> Slide 15 (Ojas Mohbansi -> Darpan Jain)
    console.log('Testing Boundary 3: Slide 14 -> Slide 15 (Ojas Mohbansi -> Darpan Jain)...');
    await page.keyboard.press('ArrowRight');
    await new Promise((r) => setTimeout(r, 600));
    const s15 = await getSlideState();
    console.log(`  Slide 15: Presenter = ${s15.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_15_darpan_jain_presenter_view.png') });

    // Capture 9: Slide 18 - Darpan Jain before handoff
    console.log('Testing Slide 18 (Darpan Jain before handoff)...');
    await jumpToSlide(18);
    const s18 = await getSlideState();
    console.log(`  Slide 18: Presenter = ${s18.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_18_darpan_jain_before_handoff.png') });

    // Boundary 4: Slide 18 -> Slide 19 (Darpan Jain -> Panda)
    console.log('Testing Boundary 4: Slide 18 -> Slide 19 (Darpan Jain -> Panda)...');
    await page.keyboard.press('ArrowRight');
    await new Promise((r) => setTimeout(r, 600));
    const s19 = await getSlideState();
    console.log(`  Slide 19: Presenter = ${s19.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_19_panda_presenter_view.png') });

    // Capture 11: Slide 22 - Panda Q.E.D.
    console.log('Testing Slide 22 (Panda Q.E.D.)...');
    await jumpToSlide(22);
    const s22 = await getSlideState();
    console.log(`  Slide 22: Presenter = ${s22.presenterHeading}`);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_22_panda_qed_conclusion.png') });

    // Capture 12: Slide 20 in Audience View
    console.log('Testing Slide 20 in Audience View...');
    await jumpToSlide(20);
    await page.keyboard.press('p');
    await new Promise((r) => setTimeout(r, 600));
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'slide_20_live_lab_audience_view.png') });
    await page.keyboard.press('p');
    await new Promise((r) => setTimeout(r, 600));

    // Capture 13: Tab switching - Defense Q&A Tab on Slide 19
    console.log('Testing Defense Q&A Tab on Slide 19...');
    await jumpToSlide(19);
    await page.evaluate(() => {
      const tabs = Array.from(document.querySelectorAll('aside button'));
      const qaTab = tabs.find((t) => t.innerText.includes('Defense Q&A'));
      if (qaTab) qaTab.click();
    });
    await new Promise((r) => setTimeout(r, 600));
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'defense_qa_tab_expanded.png') });

    // Capture 14: Tab switching - Invariants Tab on Slide 7
    console.log('Testing Invariants Tab on Slide 7...');
    await jumpToSlide(7);
    await page.evaluate(() => {
      const tabs = Array.from(document.querySelectorAll('aside button'));
      const pointsTab = tabs.find((t) => t.innerText.includes('Invariants'));
      if (pointsTab) pointsTab.click();
    });
    await new Promise((r) => setTimeout(r, 600));
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'invariants_tab_view.png') });

    // Capture 15: Thumbnail Navigation focused on Slide 11
    console.log('Testing Thumbnail Strip with Slide 11...');
    await jumpToSlide(11);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'thumbnail_strip_navigation.png') });

    testReport.checks.push({ name: 'Slide 1 Presenter', expected: 'Tanmay', actual: s1.presenterHeading, pass: s1.presenterHeading === 'Tanmay' });
    testReport.checks.push({ name: 'Boundary 4->5 Presenter Change', from: s4.presenterHeading, to: s5.presenterHeading, pass: s4.presenterHeading === 'Tanmay' && s5.presenterHeading === 'Karthik Sai' });
    testReport.checks.push({ name: 'Boundary 9->10 Presenter Change', from: s9.presenterHeading, to: s10.presenterHeading, pass: s9.presenterHeading === 'Karthik Sai' && s10.presenterHeading === 'Ojas Mohbansi' });
    testReport.checks.push({ name: 'Boundary 14->15 Presenter Change', from: s14.presenterHeading, to: s15.presenterHeading, pass: s14.presenterHeading === 'Ojas Mohbansi' && s15.presenterHeading === 'Darpan Jain' });
    testReport.checks.push({ name: 'Boundary 18->19 Presenter Change', from: s18.presenterHeading, to: s19.presenterHeading, pass: s18.presenterHeading === 'Darpan Jain' && s19.presenterHeading === 'Panda' });
    testReport.checks.push({ name: 'Slide 22 Presenter', expected: 'Panda', actual: s22.presenterHeading, pass: s22.presenterHeading === 'Panda' });

    fs.writeFileSync('qa/phase21/browser_test_summary.json', JSON.stringify(testReport, null, 2));
    console.log('\nAll browser QA steps completed successfully!');
  } catch (err) {
    console.error('Error during Presentation QA:', err);
  } finally {
    await browser.close();
  }
}

runPresentationQA();
