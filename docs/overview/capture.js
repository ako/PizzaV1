// Fresh phone screenshots of the running app for the build-overview deck.
//   node docs/overview/capture.js            (app on APP_URL, default http://127.0.0.1:8080)
// iPhone profile (Mendix picks its navigation profile from the user agent), 390 px wide.
// Every visitor is an anonymous guest (the PRD has no sign-in and no demo users), so each
// shot is taken as a fresh guest. Writes docs/overview/shots/<lane>-<name>.jpg and
// shots/index.json with what each shot shows and when it was taken.
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const APP = (process.env.APP_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');
const OUT = path.join(__dirname, 'shots');
fs.mkdirSync(OUT, { recursive: true });
const index = [];
const PHONE = {
  viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  timezoneId: 'America/Los_Angeles',
};

async function guest(browser) { const c = await browser.newContext(PHONE); const p = await c.newPage(); return { c, p }; }
async function leave({ c, p }) { try { await p.evaluate(() => window.mx && mx.logout && mx.logout()); } catch (e) { /* gone */ } await c.close(); }
async function shot(p, lane, name, shows, scrollSel) {
  if (scrollSel) await p.locator(scrollSel).first().evaluate((el) => el.scrollIntoView({ block: 'start' }));
  await p.waitForTimeout(600);
  const file = `${lane}-${name}.jpg`;
  await p.screenshot({ path: path.join(OUT, file), type: 'jpeg', quality: 72 });
  index.push({ lane, file, shows, takenAt: new Date().toISOString() });
  console.log('  shot', file);
}
const open = async (p, route) => { await p.goto(APP + route, { waitUntil: 'load' }); await p.waitForTimeout(3000); };
const tap = async (p, sel) => { await p.locator(sel).first().click(); await p.waitForTimeout(1500); };

async function order(p) {          // a delivery order paid with the default test card
  await open(p, '/p/menu');
  await p.locator('.pcard', { hasText: 'Inferno Payload' }).first().waitFor();
  await tap(p, '.pcard:has-text("Inferno Payload") .mx-name-pConfigure');
  await tap(p, '.scr-03 .opt:has-text("LARGE")');
  await tap(p, '.scr-03 .xopt:has-text("cherry_tomatoes")');
}

(async () => {
  const browser = await chromium.launch();
  let g = await guest(browser);
  try {
    // lane 0: the shell (header, bottom tabs, theme) on the home page
    await open(g.p, '/');
    await shot(g.p, 'lane0', 'home-shell', 'SCR-01 home: header, DEMO MODE banner, bottom tabs, Git Pizza theme');
    // M1: menu and configurator
    await order(g.p);
    await shot(g.p, 'm1', 'configurator', 'SCR-03 configurator: Inferno Payload Large + cherry tomatoes, line total $25.00', '.scr-03 .mx-name-deploy');
    await open(g.p, '/p/menu');
    await shot(g.p, 'm1', 'menu', 'SCR-02 menu: category tabs, grep search, dietary filter chips, product cards');
  } finally { await leave(g); }

  g = await guest(browser);
  try {
    // M2: payment sheet and tracking
    await order(g.p);
    await tap(g.p, '.scr-03 .mx-name-deploy');
    await tap(g.p, '.bn-tab.nav-cart');
    await tap(g.p, '.mx-window .mx-name-proceed');
    await g.p.locator('.mx-name-tA1 input').waitFor();
    for (const [s, v] of [['tA1', '500 Howard Street'], ['tZip', '94105'], ['tName', 'Sam Rivera'], ['tEmail', 'sam.rivera@example.com'], ['tPhone', '415 555 0142']]) {
      await g.p.locator(`.mx-name-${s} input`).fill(v); await g.p.locator('.mx-name-tCity input').click(); await g.p.waitForTimeout(400);
    }
    await shot(g.p, 'm1', 'checkout', 'SCR-06 checkout summary: Inferno Payload Large $25.00, fee, tax, tip, total $34.90', '.co-right .sum-total');
    await g.p.locator('.mx-name-exec').click();
    await g.p.locator('.mx-window').first().waitFor();
    await g.p.waitForTimeout(800);
    await shot(g.p, 'm2', 'payment', 'SCR-07 payment sheet: simulated gateway processing the card');
    await g.p.locator('.scr-08').waitFor({ timeout: 30000 });
    await tap(g.p, '.mx-name-fMonitor');
    await g.p.locator('.scr-09').waitFor();
    await g.p.waitForTimeout(2500);
    await shot(g.p, 'm2', 'tracking', 'SCR-09 tracking: pipeline stepper, ETA, order log');
    // M3: wait until the simulated kitchen has moved the order on
    await g.p.waitForTimeout(25000);
    await shot(g.p, 'm3', 'kitchen-log', 'SCR-09 ~25 s later: still queued (all ovens busy), live map, ETA 05:27, 2.8 mi', '.scr-09 .term-body');
  } finally { await leave(g); }

  g = await guest(browser);
  try {
    await open(g.p, '/');
    await shot(g.p, 'm3', 'home-kpis', 'SCR-01 live kitchen KPIs: deployed today 10, kitchen load 6/6 ovens (HEAVY), 4 couriers on duty', '.scr-01 .kpis, .scr-01 .kpi-grid, .scr-01 [class*="kpi"]');
    // M4: errors and system messages
    await open(g.p, '/p/not-found');
    await shot(g.p, 'm4', 'not-found', 'SCR-40 ERROR 404 // CRUST_NOT_FOUND');
    await open(g.p, '/p/menu');
    await g.c.setOffline(true); await g.p.waitForTimeout(7000);
    await shot(g.p, 'm4', 'offline', 'CONNECTION_LOST banner after two failed refreshes (US-287)');
    await g.c.setOffline(false); await g.p.waitForTimeout(4000);
  } finally { await leave(g); }

  await browser.close();
  fs.writeFileSync(path.join(OUT, 'index.json'), JSON.stringify(index, null, 1));
  console.log(`${index.length} shots -> ${OUT}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
