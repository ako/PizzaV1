// User-journey browser tests against the running app (default http://localhost:8080).
//   ./mxcli run --local --detach -p GitPizza.mpr     (start with a fresh demo reset for stable data)
//   node tests/e2e/journeys.js
// Scenarios follow 12-acceptance/test-scenarios.md; amounts are the worked examples.
'use strict';
const path = require('path');
const { chromium, OUT, PHONE, guest, leave, open, test, expect, expectEqual, finish } = require('./lib');

const shot = (page, name) => page.screenshot({ path: path.join(OUT, `journey-${name}.png`), fullPage: false });
const text = async (page, sel) => (await page.locator(sel).first().innerText()).replace(/\s+/g, ' ').trim();

async function addFromMenu(page, product) {
  await page.locator('.pcard', { hasText: product }).locator('.btn-primary').first().click();
  await page.waitForTimeout(1200);
}

async function fillDelivery(page) {
  await page.locator('.mx-name-tA1 input').fill('500 Howard Street');
  await page.locator('.mx-name-tZip input').fill('94105');
  await page.locator('.mx-name-tName input').click(); await page.waitForTimeout(1200);
  await page.locator('.mx-name-tName input').fill('Taylor Brooks');
  await page.locator('.mx-name-tEmail input').fill('taylor.brooks@example.com');
  await page.locator('.mx-name-tPhone input').fill('415 555 0199');
  await page.locator('.mx-name-tCity input').click(); await page.waitForTimeout(1500);
}

(async () => {
  const browser = await chromium.launch();
  console.log('Journeys');

  await test('J1 order, pay and track (example: Root Pizza + Binary BBQ, delivery, tip 15 %)', async () => {
    const g = await guest(browser);
    try {
      const { page } = g;
      await open(page, '/p/menu', 3000);
      await addFromMenu(page, 'The Root Pizza');
      await addFromMenu(page, 'Binary BBQ');
      expectEqual(await text(page, '.app-header-dv .count-bubble'), '2', 'cart badge');
      await page.locator('.main-nav .nav-checkout').click(); await page.waitForTimeout(3000);
      await fillDelivery(page);
      expectEqual((await text(page, '.co-right .sum-total')).match(/\$[\d,.]+$/)[0], '$47.24', 'checkout total');
      await shot(page, 'checkout');
      await page.locator('.mx-name-exec').click(); await page.waitForTimeout(8000);
      const conf = await text(page, '.scr-08');
      expect(/DEPLOYMENT SUCCESSFUL/.test(conf), 'confirmation shows DEPLOYMENT SUCCESSFUL');
      expect(/MX-\d{4}/.test(conf), 'confirmation shows the order number');
      await shot(page, 'confirmation');
      await page.locator('.mx-name-fMonitor').click(); await page.waitForTimeout(3000);
      const head = await text(page, '.scr-09 .trk-head');
      expect(/DEPLOYMENT_STATUS/.test(head) && /QUEUED|BAKING/.test(head), `tracking header: ${head}`);
      const log = await text(page, '.scr-09 .term-body');
      expect(/Order MX-\d{4} staged/.test(log), 'order log lists the staged line');
      expect(/Payment confirmed/.test(log), 'order log lists the payment');
      expect(!(await page.locator('.mx-dialog-error').count()), 'no platform error dialog');
      await shot(page, 'tracking');
    } finally { await leave(g); }
  });

  await test('J2 coupon GITHUB_STUDENT on example B (Root Pizza M + Garlic Knot Loop) gives $26.58', async () => {
    const g = await guest(browser);
    try {
      const { page } = g;
      await open(page, '/p/menu', 3000);
      await addFromMenu(page, 'The Root Pizza');
      await page.locator('.file-tab', { hasText: 'sides' }).first().click(); await page.waitForTimeout(1500);
      await addFromMenu(page, 'Garlic Knot Loop');
      await page.locator('.app-header-dv .icon-btn').first().click(); await page.waitForTimeout(2000);
      await page.locator('.mx-name-cpInput input').fill('GITHUB_STUDENT');
      await page.locator('.mx-name-cpApply').click(); await page.waitForTimeout(2000);
      const drawer = await text(page, '.mx-window, .scr-05');
      expect(/−\$3\.22/.test(drawer), `drawer shows the discount −$3.22: ${drawer.slice(0, 200)}`);
      await page.goto(page.url().replace(/\/p\/.*$/, '/p/checkout'), { waitUntil: 'load' }); await page.waitForTimeout(3000);
      await fillDelivery(page);
      expectEqual((await text(page, '.co-right .sum-total')).match(/\$[\d,.]+$/)[0], '$26.58', 'checkout total with coupon');
    } finally { await leave(g); }
  });

  await test('J3 declined card VISA_0002, then retry with Apple Pay succeeds (scenario: Example B, G2)', async () => {
    const g = await guest(browser);
    try {
      const { page } = g;
      await open(page, '/p/menu', 3000);
      await addFromMenu(page, 'Binary BBQ');
      await page.locator('.main-nav .nav-checkout').click(); await page.waitForTimeout(3000);
      await fillDelivery(page);
      await page.locator('.mx-name-coc2').click(); await page.waitForTimeout(1500);
      await page.locator('.mx-name-exec').click(); await page.waitForTimeout(8000);
      const sheet = await text(page, '.mx-window');
      expect(/declin|fail/i.test(sheet), `payment sheet reports the failure: ${sheet.slice(0, 160)}`);
      await shot(page, 'payment-failed');
      await page.locator('.mx-window .mx-name-pmApple').click(); await page.waitForTimeout(1500);
      await page.locator('.mx-name-fRetry').click(); await page.waitForTimeout(9000);
      expect(/DEPLOYMENT SUCCESSFUL/.test(await text(page, 'body')), 'retry with Apple Pay reaches the confirmation');
    } finally { await leave(g); }
  });

  await test('J4 order lookup rejects an unknown order without revealing which field was wrong', async () => {
    const g = await guest(browser);
    try {
      const { page } = g;
      await open(page, '/p/track', 3000);
      await page.locator('.mx-name-tNo input').fill('MX-9999');
      await page.locator('.mx-name-tEm input').fill('nobody@example.com');
      await page.locator('.mx-name-lBtn').click(); await page.waitForTimeout(2000);
      const body = await text(page, '.scr-10');
      expect(/no order|not found|doesn't match|does not match/i.test(body), `lookup error shown: ${body.slice(0, 200)}`);
    } finally { await leave(g); }
  });

  await test('J5 unknown URL shows ERROR 404 // CRUST_NOT_FOUND with RETURN_TO_MAIN', async () => {
    const g = await guest(browser);
    try {
      const { page } = g;
      await open(page, '/p/not-found', 2500);
      const body = await text(page, 'body');
      expect(/ERROR 404/.test(body) && /CRUST_NOT_FOUND/.test(body), '404 heading');
      expect(/RETURN_TO_MAIN/.test(body), 'RETURN_TO_MAIN button');
      expect(!/Exception|Microflow|Shop\./.test(body), 'no technical names (US-289)');
    } finally { await leave(g); }
  });

  await test('J6 connection loss shows the CONNECTION_LOST banner and blocks actions with a toast', async () => {
    const g = await guest(browser);
    try {
      const { page, context } = g;
      await open(page, '/p/menu', 3500);
      await context.setOffline(true); await page.waitForTimeout(7000);
      expect(await page.evaluate(() => document.documentElement.classList.contains('gp-offline')), 'banner shown');
      await page.locator('.pcard').first().locator('.btn-primary').click(); await page.waitForTimeout(800);
      expect(/Could not reach the server/.test(await text(page, '.toasts')), 'offline action toast');
      await context.setOffline(false); await page.waitForTimeout(5000);
      expect(!(await page.evaluate(() => document.documentElement.classList.contains('gp-offline'))), 'banner hidden after reconnect');
      expect(!(await page.locator('.app-header-dv .count-bubble').isVisible()), 'blocked action was not sent later');
    } finally { await leave(g); }
  });

  await test('J7 phone: bottom navigation and menu cards render at 390 px', async () => {
    const g = await guest(browser, PHONE);
    try {
      const { page } = g;
      await open(page, '/p/menu', 3500);
      expect(await page.locator('.bottom-nav, .bn-tab').first().isVisible(), 'bottom navigation visible');
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      expect(overflow <= 1, `no horizontal scroll (overflow ${overflow}px)`);
      await shot(page, 'menu-phone');
    } finally { await leave(g); }
  });

  await browser.close();
  finish('journeys');
})();
