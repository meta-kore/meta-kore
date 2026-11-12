// Rasterize SVG files to PNG with Chromium (Playwright).
// Usage: node scripts/rasterize.js <width> <out-dir> <a.svg> [b.svg ...]
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const [width, outDir, ...files] = process.argv.slice(2);
  const w = +width, h = Math.round(w * 500 / 1600);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  for (const f of files) {
    const wrap = path.join(outDir, path.basename(f, '.svg') + '.html');
    fs.writeFileSync(wrap, `<body style="margin:0;background:#0A0A0B"><img src="${path.resolve(f)}" width="${w}"></body>`);
    await page.goto('file://' + wrap);
    await page.screenshot({ path: path.join(outDir, path.basename(f, '.svg') + '.png') });
  }
  await browser.close();
})();
