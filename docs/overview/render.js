// Render the overview and each frame of build-overview.html to PNGs (for checking the layout).
//   node docs/overview/render.js [outdir]
const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
const here = __dirname; const out = process.argv[2] || path.join(here, 'render');
fs.mkdirSync(out, { recursive: true });
const frames = JSON.parse(fs.readFileSync(path.join(here, 'frames.json'))).filter((o) => o.collection === 'frames');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
  await p.goto('file://' + path.join(here, 'build-overview.html')); await p.waitForTimeout(2500);
  await p.evaluate(() => { const h = document.getElementById('hint'); if (h) h.style.display = 'none'; });
  for (const f of frames) {
    const d = f.data; const s = Math.min(1600 / d.w, 1000 / d.h) * 0.98;
    await p.evaluate(([cx, cy, s]) => document.getElementById('camera').setAttribute('transform', `translate(800 500) scale(${s}) translate(${-cx} ${-cy})`), [d.x + d.w / 2, d.y + d.h / 2, s]);
    await p.waitForTimeout(400);
    await p.screenshot({ path: path.join(out, f.doc_id + '.png') }); console.log('rendered', f.doc_id);
  }
  await b.close();
})();
