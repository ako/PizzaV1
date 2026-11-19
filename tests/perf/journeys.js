// Performance journeys for `mxcli report performance` (report-performance skill).
// One guest walk split into steps; each step runs RUNS times (run 0 is warm-up and not
// counted by the report). A step lasts from its action until the last /xas/ request has
// answered and nothing new starts for 0.6 s. One JSONL line per step and run goes to
// $MXCLI_JOURNEY_LOG:  {"journey","step","run","start","end","browserMs"}
//   mxcli report performance -p GitPizza.mpr --journeys-cmd "node tests/perf/journeys.js" ...
'use strict';
const fs = require('fs');
const { chromium } = require('playwright');

const APP = (process.env.APP_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');
const RUNS = Number(process.env.PERF_RUNS || 6);            // run 0 = warm-up
const LOG = process.env.MXCLI_JOURNEY_LOG;
const JOURNEY = 'Guest orders a pizza';

function log(rec) { if (LOG) fs.appendFileSync(LOG, JSON.stringify(rec) + '\n'); }

// Wait until no /xas/ request is in flight and none has started for `quiet` ms.
function settle(page, quiet = 600, timeout = 30000) {
  return new Promise((resolve) => {
    let inflight = 0; let last = Date.now();
    const on = (r) => { if (r.url().includes('/xas/')) { inflight++; last = Date.now(); } };
    const off = (r) => { if (r.url().includes('/xas/')) { inflight = Math.max(0, inflight - 1); last = Date.now(); } };
    page.on('request', on); page.on('requestfinished', off); page.on('requestfailed', off);
    const t0 = Date.now();
    const tick = setInterval(() => {
      if ((inflight === 0 && Date.now() - last >= quiet) || Date.now() - t0 > timeout) {
        clearInterval(tick); page.off('request', on); page.off('requestfinished', off); page.off('requestfailed', off); resolve();
      }
    }, 50);
  });
}

async function step(page, name, run, action) {
  const start = new Date();
  const t = Date.now();
  await action();
  await settle(page);
  const end = new Date(Date.now() - 600);                  // the quiet tail is not part of the step
  log({ journey: JOURNEY, step: name, run, start: start.toISOString(), end: end.toISOString(), browserMs: Date.now() - 600 - t });
}

(async () => {
  if (LOG) fs.appendFileSync(LOG, JSON.stringify({ meta: true, database: 'fresh demo reset (46 seed orders, 25 products) + live simulation traffic',
    notes: ['auto_explain on for the run (session_preload_libraries, log_min_duration 20ms; restored afterwards)', `${RUNS} runs per step, run 0 warm-up`, 'live poller on (2 s refresh is part of every step)'] }) + '\n');
  const browser = await chromium.launch();
  for (let run = 0; run < RUNS; run++) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, timezoneId: 'America/Los_Angeles' });
    const page = await context.newPage();
    // The 2 s live poller stays on: the payment sheet advances through it. Its short
    // requests leave the 0.6 s quiet gaps the step detection needs, and its share of
    // server time is visible in each step's flame chart.
    try {
      await step(page, '1 open home', run, () => page.goto(APP + '/', { waitUntil: 'load' }));
      await step(page, '2 open menu', run, () => page.locator('.main-nav .nav-menu').click());
      await page.locator('.pcard', { hasText: 'Inferno Payload' }).first().waitFor({ timeout: 30000 });
      await step(page, '3 open configurator', run, () => page.locator('.pcard', { hasText: 'Inferno Payload' }).locator('.mx-name-pConfigure').first().click());
      await page.locator('.scr-03 .xopt', { hasText: 'cherry_tomatoes' }).first().waitFor({ timeout: 30000 });
      await step(page, '4 choose extra', run, () => page.locator('.scr-03 .xopt', { hasText: 'cherry_tomatoes' }).first().click());
      await step(page, '5 add to cart', run, () => page.locator('.scr-03 .mx-name-deploy').click());
      await step(page, '6 open checkout', run, () => page.locator('.main-nav .nav-checkout').click());
      await page.locator('.mx-name-tA1 input').waitFor({ timeout: 30000 });
      for (const [s, v] of [['tA1', '500 Howard Street'], ['tName', 'Sam Rivera'], ['tEmail', 'sam@example.com'], ['tPhone', '415 555 0142']]) {
        await page.locator(`.mx-name-${s} input`).fill(v);
      }
      await step(page, '7 address -> zone and totals', run, async () => { await page.locator('.mx-name-tZip input').fill('94105'); await page.locator('.mx-name-tCity input').click(); });
      await step(page, '8 place order and pay', run, async () => { await page.locator('.mx-name-exec').click(); await page.locator('.scr-08').waitFor({ timeout: 30000 }); });
      await step(page, '9 open tracking', run, async () => { await page.locator('.mx-name-fMonitor').click(); await page.locator('.scr-09').waitFor({ timeout: 30000 }); });
      console.log(`run ${run}: ok`);
    } catch (e) {
      console.log(`run ${run}: ${e.message.split('\n')[0]}`);
      if (process.env.PERF_DEBUG) await page.screenshot({ path: process.env.PERF_DEBUG }).catch(() => {});
    } finally {
      try { await page.evaluate(() => window.mx && mx.logout && mx.logout()); } catch (e) { /* gone */ }
      await context.close();
    }
  }
  await browser.close();
})();
