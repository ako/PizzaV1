// Regenerates tests/e2e/reference/ from the clickable prototype (first viewport only).
//   PROTO_URL=http://localhost:8765/08-prototype/customer node tests/e2e/capture-reference.js
// Serve the prototype package with any static server, e.g. `python3 -m http.server 8765`
// from the package root. The prototype is external input: it is only rendered, never executed
// outside the browser sandbox.
'use strict';
const path = require('path');
const { chromium } = require('playwright');

const PROTO = (process.env.PROTO_URL || 'http://localhost:8765/08-prototype/customer').replace(/\/$/, '');
const PAGES = {
  'SCR-01-home': 'SCR-01-home.html',
  'SCR-02-menu': 'SCR-02-menu.html',
  'SCR-03-pizza-configurator': 'SCR-03-pizza-configurator.html?p=PZ-05',
  'SCR-10-track-order-lookup': 'SCR-10-track-order-lookup.html',
  'SCR-40-not-found': 'SCR-40-not-found.html',
  'SCR-41-unexpected-error': 'SCR-41-unexpected-error.html',
};

(async () => {
  const browser = await chromium.launch();
  for (const [tag, viewport] of [['d', { width: 1440, height: 900 }], ['m', { width: 390, height: 844 }]]) {
    const page = await browser.newPage({ viewport });
    for (const [name, file] of Object.entries(PAGES)) {
      await page.goto(`${PROTO}/${file}`, { waitUntil: 'load' });
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(__dirname, 'reference', `${name}-${tag}.png`) });
      console.log(`captured ${name}-${tag}`);
    }
    await page.close();
  }
  await browser.close();
})();
