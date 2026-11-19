// Visual comparison of the app against the clickable prototype (first viewport,
// desktop 1440×900 and phone 390×844). References in tests/e2e/reference/ are the
// prototype's screens (regenerate with capture-reference.js). Writes app shots and
// red-on-dim diff images to tests/e2e/out/ and fails a screen whose share of
// differing pixels exceeds its budget. Live data (KPIs, clock, order numbers,
// product photos' compression) never matches exactly, so budgets are not zero.
//   node tests/e2e/visual.js            all screens
//   node tests/e2e/visual.js SCR-02     screens whose name contains SCR-02
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium, OUT, DESKTOP, PHONE, guest, leave, open, test, expect, finish, comparePng } = require('./lib');

const REF = path.join(__dirname, 'reference');
const FREEZE = '*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}';

const SCREENS = [
  { name: 'SCR-01-home', route: '/', budget: 0.12 },
  // The filter chips (US-033, BR-MENU-20) are required by the stories but absent from
  // the prototype; they are hidden for the comparison only.
  { name: 'SCR-02-menu', route: '/p/menu', budget: 0.10, hide: ['.filter-chips'] },
  { name: 'SCR-03-pizza-configurator', route: '/p/menu', budget: 0.10, setup: async (page) => {
      await page.locator('.pcard', { hasText: 'Inferno Payload' }).locator('.mx-name-pConfigure').first().click();
      await page.waitForTimeout(2500);
    } },
  { name: 'SCR-10-track-order-lookup', route: '/p/track', budget: 0.10 },
  { name: 'SCR-40-not-found', route: '/p/not-found', budget: 0.10 },
  { name: 'SCR-41-unexpected-error', route: '/p/error', budget: 0.10 },
];

(async () => {
  const filter = process.argv[2] || '';
  const browser = await chromium.launch();
  const summary = [];
  console.log('Visual comparison against the prototype');
  for (const screen of SCREENS.filter((s) => s.name.includes(filter))) {
    for (const [tag, viewport] of [['d', DESKTOP], ['m', PHONE]]) {
      const id = `${screen.name}-${tag}`;
      await test(`${id} within ${Math.round(screen.budget * 100)} % of the prototype`, async () => {
        const g = await guest(browser, viewport);
        try {
          const { page } = g;
          await open(page, screen.route, 3500);
          if (screen.setup) { await screen.setup(page); }
          await page.addStyleTag({ content: FREEZE + (screen.hide || []).map((h) => `${h}{display:none!important}`).join('') });
          await page.mouse.move(0, 0);
          await page.waitForTimeout(300);
          const actual = path.join(OUT, `${id}.png`);
          await page.screenshot({ path: actual });
          const res = await comparePng(browser, actual, path.join(REF, `${id}.png`), path.join(OUT, `${id}-diff.png`));
          summary.push({ id, mismatch: +(res.ratio * 100).toFixed(2), budget: screen.budget * 100 });
          expect(res.ratio <= screen.budget, `${(res.ratio * 100).toFixed(1)} % of pixels differ (budget ${screen.budget * 100} %)`);
        } finally { await leave(g); }
      });
    }
  }
  await browser.close();
  console.log('\nscreen                              mismatch %  budget %');
  for (const s of summary) { console.log(`${s.id.padEnd(36)}${String(s.mismatch).padStart(10)}${String(s.budget).padStart(10)}`); }
  fs.writeFileSync(path.join(OUT, 'visual-summary.json'), JSON.stringify(summary, null, 2));
  finish('visual');
})();
