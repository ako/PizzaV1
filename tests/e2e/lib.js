// Shared helpers for the browser tests. Only the `playwright` library is needed
// (no test runner): node tests/e2e/journeys.js / node tests/e2e/visual.js.
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const APP = (process.env.APP_URL || 'http://localhost:8080').replace(/\/$/, '');
const OUT = path.join(__dirname, 'out');
const DESKTOP = { width: 1440, height: 900 };
const PHONE = { width: 390, height: 844 };

fs.mkdirSync(OUT, { recursive: true });

/** Opens a fresh guest (new browser context = new anonymous session). */
async function guest(browser, viewport = DESKTOP) {
  const context = await browser.newContext({ viewport, timezoneId: 'America/Los_Angeles' });
  const page = await context.newPage();
  page.on('pageerror', (e) => { page.__errors = (page.__errors || []).concat(String(e)); });
  return { context, page };
}

/**
 * Ends the guest session. The trial runtime caps concurrent sessions, so every
 * test logs out instead of leaving its session to time out.
 */
async function leave({ context, page }, name) {
  if (name) { try { await page.screenshot({ path: path.join(OUT, `fail-${name}.png`) }); } catch (e) { /* closed */ } }
  try { await page.evaluate(() => window.mx && mx.logout && mx.logout()); } catch (e) { /* page gone */ }
  await context.close();
}

/** Waits for the Mendix client to render (load event, then a short settle). */
async function open(page, route, settle = 2500) {
  await page.goto(APP + route, { waitUntil: 'load' });
  await page.waitForTimeout(settle);
}

const results = [];
/** Runs one named test and records PASS/FAIL with the message. */
// With MXCLI_JOURNEY_LOG set (mxcli report tests / performance --journeys-cmd), every
// test appends {journey, start, end, status} so the report can match server spans to it.
function logJourney(name, started, ok) {
  if (!process.env.MXCLI_JOURNEY_LOG) { return; }
  fs.appendFileSync(process.env.MXCLI_JOURNEY_LOG, JSON.stringify({
    journey: name, start: new Date(started).toISOString(), end: new Date().toISOString(), status: ok ? 'passed' : 'failed',
  }) + '\n');
}

async function test(name, fn) {
  const started = Date.now();
  try {
    await fn();
    results.push({ name, ok: true, ms: Date.now() - started });
    logJourney(name, started, true);
    console.log(`  PASS  ${name} (${Date.now() - started} ms)`);
  } catch (e) {
    results.push({ name, ok: false, ms: Date.now() - started, error: String(e && e.message || e) });
    logJourney(name, started, false);
    console.log(`  FAIL  ${name}\n        ${String(e && e.message || e).split('\n')[0]}`);
  }
}

function expect(cond, message) { if (!cond) { throw new Error(message); } }
function expectEqual(actual, expected, what) {
  if (actual !== expected) { throw new Error(`${what}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`); }
}

/** Prints the summary, writes JUnit-style JSON and sets the exit code. */
function finish(suite) {
  const failed = results.filter((r) => !r.ok);
  fs.writeFileSync(path.join(OUT, `${suite}.json`), JSON.stringify(results, null, 2));
  console.log(`\n${suite}: ${results.length - failed.length}/${results.length} passed`);
  process.exitCode = failed.length ? 1 : 0;
}

/**
 * Pixel comparison of two PNG files, done in a browser canvas so no image
 * library is needed. Compares the overlapping area (top-left aligned); a pixel
 * differs when any channel differs by more than `tolerance`. Writes a diff PNG
 * (differences in red over a dimmed copy of the app screenshot).
 */
async function comparePng(browser, actualFile, referenceFile, diffFile, tolerance = 32) {
  const page = await browser.newPage();
  const a = 'data:image/png;base64,' + fs.readFileSync(actualFile).toString('base64');
  const r = 'data:image/png;base64,' + fs.readFileSync(referenceFile).toString('base64');
  const res = await page.evaluate(async ({ a, r, tolerance }) => {
    const load = (src) => new Promise((ok, ko) => { const i = new Image(); i.onload = () => ok(i); i.onerror = ko; i.src = src; });
    const [ia, ir] = await Promise.all([load(a), load(r)]);
    const w = Math.min(ia.width, ir.width); const h = Math.min(ia.height, ir.height);
    const ca = document.createElement('canvas'); ca.width = w; ca.height = h;
    const cr = document.createElement('canvas'); cr.width = w; cr.height = h;
    const xa = ca.getContext('2d'); const xr = cr.getContext('2d');
    xa.drawImage(ia, 0, 0); xr.drawImage(ir, 0, 0);
    const da = xa.getImageData(0, 0, w, h); const dr = xr.getImageData(0, 0, w, h);
    const out = xa.createImageData(w, h);
    let diff = 0;
    for (let i = 0; i < da.data.length; i += 4) {
      const d = Math.max(Math.abs(da.data[i] - dr.data[i]), Math.abs(da.data[i + 1] - dr.data[i + 1]), Math.abs(da.data[i + 2] - dr.data[i + 2]));
      if (d > tolerance) { diff++; out.data[i] = 255; out.data[i + 1] = 0; out.data[i + 2] = 0; out.data[i + 3] = 255; }
      else { out.data[i] = da.data[i] * 0.3; out.data[i + 1] = da.data[i + 1] * 0.3; out.data[i + 2] = da.data[i + 2] * 0.3; out.data[i + 3] = 255; }
    }
    xa.putImageData(out, 0, 0);
    return { ratio: diff / (w * h), width: w, height: h, sizeA: [ia.width, ia.height], sizeR: [ir.width, ir.height], png: ca.toDataURL('image/png') };
  }, { a, r, tolerance });
  fs.writeFileSync(diffFile, Buffer.from(res.png.split(',')[1], 'base64'));
  await page.close();
  delete res.png;
  return res;
}

module.exports = { chromium, APP, OUT, DESKTOP, PHONE, guest, leave, open, test, expect, expectEqual, finish, comparePng };
