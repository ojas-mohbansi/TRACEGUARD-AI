import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

async function generateOgImage() {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 630 });

  const wordmarkSvg = fs.readFileSync('website/public/brand/traceguard-ai-wordmark-color.svg', 'utf-8');
  const iconSvg = fs.readFileSync('website/public/brand/traceguard-ai-icon-color.svg', 'utf-8');

  const html = `
<!DOCTYPE html>
<html>
<head>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      width: 1200px;
      height: 630px;
      background: #060810;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 70px 80px;
      position: relative;
      overflow: hidden;
    }
    .glow-blue {
      position: absolute;
      top: -100px;
      right: 100px;
      width: 600px;
      height: 600px;
      border-radius: 50%;
      background: rgba(59, 130, 246, 0.22);
      filter: blur(120px);
      pointer-events: none;
    }
    .glow-emerald {
      position: absolute;
      bottom: -100px;
      left: 100px;
      width: 500px;
      height: 500px;
      border-radius: 50%;
      background: rgba(16, 185, 129, 0.16);
      filter: blur(120px);
      pointer-events: none;
    }
    .grid-bg {
      position: absolute;
      inset: 0;
      background-image: linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
    }
    .header {
      display: flex;
      align-items: center;
      gap: 20px;
      z-index: 10;
    }
    .icon {
      width: 54px;
      height: 54px;
    }
    .wordmark {
      height: 38px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      padding: 6px 14px;
      border-radius: 9999px;
      border: 1px solid rgba(59, 130, 246, 0.4);
      background: rgba(59, 130, 246, 0.12);
      color: #60a5fa;
      font-family: monospace;
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 18px;
    }
    .content {
      z-index: 10;
      max-width: 950px;
    }
    h1 {
      font-size: 52px;
      font-weight: 700;
      line-height: 1.15;
      letter-spacing: -0.02em;
      color: #ffffff;
      margin-bottom: 18px;
    }
    .gradient-text {
      background: linear-gradient(90deg, #60a5fa, #34d399);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p {
      font-size: 22px;
      line-height: 1.5;
      color: #9ca3af;
    }
    .footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-top: 1px solid rgba(255,255,255,0.1);
      padding-top: 24px;
      font-family: monospace;
      font-size: 14px;
      color: #6b7280;
      z-index: 10;
    }
    .stats {
      display: flex;
      gap: 30px;
    }
    .stats span {
      color: #d1d5db;
    }
  </style>
</head>
<body>
  <div class="glow-blue"></div>
  <div class="glow-emerald"></div>
  <div class="grid-bg"></div>

  <div class="header">
    <div class="icon">${iconSvg}</div>
    <div class="wordmark">${wordmarkSvg}</div>
  </div>

  <div class="content">
    <div class="badge">Theory of Computation · Capstone 2026</div>
    <h1>Formal Protocol Verification meets <span class="gradient-text">Statistical ML</span></h1>
    <p>Complete 9-State HTTP protocol automaton paired with an Isolation Forest to eliminate sequence manipulation and volumetric intrusion.</p>
  </div>

  <div class="footer">
    <div>Dept. of Computer Science & Engineering · Academic Research</div>
    <div class="stats">
      <div><span>9</span> States</div>
      <div><span>117</span> Transitions</div>
      <div><span>149/149</span> Passed Tests</div>
    </div>
  </div>
</body>
</html>
  `;

  await page.setContent(html, { waitUntil: 'networkidle0' });
  const outPath = path.resolve('website/public/brand/traceguard-ai-preview.png');
  await page.screenshot({ path: outPath, type: 'png' });
  console.log(`Generated Open Graph image at ${outPath}`);
  await browser.close();
}

generateOgImage().catch((err) => {
  console.error('OG image generation error:', err);
  process.exit(1);
});
