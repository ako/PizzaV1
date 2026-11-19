// Narrated walkthroughs of the Git Pizza guest journeys (Stage 2 of the
// record-narrated-demo skill). This script EXPLAINS; it does not gate anything.
// The verdicts live in tests/e2e/journeys.js (J1, J3, J9), which walk the same paths.
//
//   node demo/walkthrough.js <film> <desktop|phone>      film: order | declined
//
// Needs the app on APP_URL (default http://127.0.0.1:8080), ideally just after a
// demo reset so the home KPIs and kitchen are populated:
//   ./mxcli run --local --detach -p GitPizza.mpr --constant Simulation.ResetOnStartup=true
//
// Beats are held for the narration's measured length (demo/voice/<film>/durations.json,
// from demo/synth.py) plus a reading tail; without a voice track the hold is estimated
// at 135 words per minute. Every beat with a payoff is asserted: take.finish() throws
// if one did not hold, so a dead beat is re-recorded, never cut into the film.
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const SKILL = path.join(__dirname, '..', '.claude', 'skills', 'record-narrated-demo');
const { openTake } = require(path.join(SKILL, 'take.js'));
const narrate = require(path.join(SKILL, 'narrate.js'));

const APP = (process.env.APP_URL || 'http://127.0.0.1:8080').replace(/\/$/, '');
const [film, device] = process.argv.slice(2);
const FILMS = JSON.parse(fs.readFileSync(path.join(__dirname, 'films.json'), 'utf8'));
if (!FILMS[film] || !['desktop', 'phone'].includes(device)) {
  console.error('usage: node demo/walkthrough.js <order|declined> <desktop|phone>');
  process.exit(2);
}
const LINES = FILMS[film].lines;
const durFile = path.join(__dirname, 'voice', film, 'durations.json');
const DUR = fs.existsSync(durFile) ? JSON.parse(fs.readFileSync(durFile, 'utf8')) : {};
const TAIL_MS = 1400;            // reading time after the voice ends
const OUT = path.join(__dirname, 'out', `${film}-${device}`);
const PHONE = device === 'phone';

// Desktop: a 1920x1080 frame, zoomed so the app lays out at the prototype's 1440 px.
// Phone: a real device profile (Mendix routes on the user agent, not the window size).
const DESKTOP_ZOOM = 1920 / 1440;
const takeOpts = PHONE
  ? {
    size: { width: 430, height: 932 },
    zoom: 1,
    contextOptions: {
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 ' +
        '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
      isMobile: true, hasTouch: true, deviceScaleFactor: 3, timezoneId: 'America/Los_Angeles',
    },
  }
  : { size: { width: 1920, height: 1080 }, zoom: DESKTOP_ZOOM, contextOptions: { timezoneId: 'America/Los_Angeles' } };

// The overlay's band geometry is defined for the 1920x1080 film frame. A phone take
// is not that frame: the plate is sized for the phone instead (same flat plate, same
// ground, hairline and font; only the size changes) and the frame check is not strict.
const PHONE_PLATE = `
  #demo-narration { height: 150px !important; padding: 0 20px !important; font-size: 17px !important; gap: 12px !important; }
  #demo-narration .step { display: none !important; }
  :root { --demo-plate-height: 150px !important; }
  /* the phone's fixed bottom tab bar would sit under the plate: lift it above, so
     every tab the walk taps is visible to the viewer */
  .gp-app .bottom-nav { bottom: 150px !important; }`;

(async () => {
  fs.rmSync(OUT, { recursive: true, force: true });
  const browser = await chromium.launch();
  const take = await openTake(browser, {
    ...takeOpts,
    url: APP + (film === 'order' ? '/' : '/p/menu'),
    videoDir: path.join(OUT, 'raw'),
    beatsFile: path.join(OUT, 'beats.json'),
    minGap: 600,
  });
  narrate.configure({ zoom: takeOpts.zoom, strict: !PHONE });
  const { page } = take;

  const install = async () => {
    await narrate.install(page);
    if (PHONE) await page.addStyleTag({ content: PHONE_PLATE });
  };
  const holdMs = (beat) => {
    const voice = DUR[beat] ? DUR[beat] * 1000 : (LINES[beat].split(/\s+/).length / 2.25) * 1000;
    return Math.max(2500, Math.round(voice + TAIL_MS));
  };
  // A beat: caption up and voice cue marked, the action runs while the line plays,
  // then the rest of voice + tail is held so nothing is cut off.
  const beat = async (name, action) => {
    const started = Date.now();
    take.mark(`say:${name}`);
    await install();
    await narrate.say(page, LINES[name], name.toUpperCase(), { holdMs: 300 });
    if (action) await action();
    const left = holdMs(name) - (Date.now() - started);
    if (left > 0) await page.waitForTimeout(left);
  };
  // Give an element found by text a plain CSS handle (narrate.js uses querySelector).
  const tag = async (locator, name) => {
    await locator.first().waitFor({ state: 'visible', timeout: 30000 });
    await locator.first().evaluate((el, n) => el.setAttribute('data-demo', n), name);
    return `[data-demo="${name}"]`;
  };
  // Paced + dialog-guarded, and visible to the viewer: scroll in, point, beat, click.
  // Under html{zoom} Playwright's own scroll-into-view can leave a control just past
  // the fold ("element is outside of the viewport"); the element was already scrolled
  // into view for the viewer, so the fallback clicks that same element in the DOM.
  const act = async (selector) => {
    await take.pace();
    await take.clearDialog();
    const el = page.locator(selector).first();
    await el.waitFor({ state: 'visible', timeout: 30000 });
    await narrate.bringIntoView(page, selector);
    await narrate.point(page, selector);
    await page.waitForTimeout(900);
    try {
      await el.click({ timeout: 4000 });
    } catch (e) {
      await el.evaluate((node) => node.click());
    }
    await narrate.unpoint(page);
  };
  const type = async (selector, value) => {
    await take.pace();
    await narrate.typeSlowly(page, selector, value, 70);
  };
  const waitFor = (selector, timeout = 30000) => page.locator(selector).first().waitFor({ state: 'visible', timeout });
  const textOf = async (selector) => (await page.locator(selector).first().innerText()).replace(/\s+/g, ' ');
  const badge = PHONE ? '.bottom-nav .count-bubble, .bn-tab .count-bubble' : '.app-header-dv .count-bubble';

  const toCheckout = async () => {
    if (PHONE) {
      await act('.bn-tab.nav-cart');
      await waitFor('.mx-window .mx-name-proceed');
      await act('.mx-window .mx-name-proceed');
    } else {
      await act('.main-nav .nav-checkout');
    }
    await waitFor('.mx-name-tA1 input');
  };
  const fillAddress = async (name, email) => {
    await type('.mx-name-tA1 input', '500 Howard Street');
    await type('.mx-name-tZip input', '94105');
    await type('.mx-name-tName input', name);
    await type('.mx-name-tEmail input', email);
    await type('.mx-name-tPhone input', '415 555 0142');
    await page.waitForTimeout(800);
  };

  await take.goto();
  await install();

  if (film === 'order') {
    await waitFor('.scr-01');
    await beat('home', async () => { await narrate.point(page, '.scr-01'); await page.waitForTimeout(1500); await narrate.unpoint(page); });
    await act(PHONE ? '.bn-tab.nav-menu' : '.main-nav .nav-menu');
    await waitFor('.pcard');
    await beat('menu', async () => {
      await narrate.point(page, await tag(page.locator('.pcard'), 'first-card'));
      await page.waitForTimeout(2500);
      await narrate.unpoint(page);
    });
    const configure = await tag(page.locator('.pcard', { hasText: 'Inferno Payload' }).locator('.mx-name-pConfigure'), 'inferno-configure');
    await beat('open', async () => { await act(configure); await waitFor('.scr-03'); });
    await take.assertBeat('open', (p) => p.locator('.scr-03').count(), 'the configurator must be open on Inferno Payload');
    await beat('size', async () => {
      await act(await tag(page.locator('.scr-03 .opt', { hasText: 'LARGE' }), 'size-large'));
      await page.waitForTimeout(1200);
    });
    await take.assertBeat('size', async (p) => /\$22\.50/.test(await p.locator('.scr-03').innerText()), 'Large must price at $22.50');
    await beat('extra', async () => {
      await act(await tag(page.locator('.scr-03 .xopt', { hasText: 'cherry_tomatoes' }), 'extra-tomatoes'));
      await page.waitForTimeout(1200);
      await narrate.bringIntoView(page, '.scr-03 .mx-name-deploy');
    });
    await take.assertBeat('extra', async (p) => /\$25\.00/.test(await p.locator('.scr-03').innerText()), 'the line must come to $25.00');
    await beat('deploy', async () => { await act('.scr-03 .mx-name-deploy'); await waitFor(badge); });
    await take.assertBeat('deploy', async (p) => (await p.locator(badge).first().innerText()).trim() === '1', 'the cart must hold one pizza');
    await toCheckout();
    await beat('checkout', async () => { await fillAddress('Sam Rivera', 'sam.rivera@example.com'); await narrate.bringIntoView(page, '.co-right .sum-total, .sum-total'); });
    await take.assertBeat('checkout', async (p) => /\$\d+\.\d\d/.test(await textOf('.sum-total')), 'the order total must be shown');
    await beat('pay', async () => { await act('.mx-name-exec'); });
    await waitFor('.scr-08', 30000);
    await beat('confirmed');
    await take.assertBeat('confirmed', async (p) => /DEPLOYMENT SUCCESSFUL/.test(await textOf('.scr-08')), 'the confirmation must show the paid order');
    await act('.mx-name-fMonitor');
    await waitFor('.scr-09');
    await beat('tracking', async () => { await page.waitForTimeout(2000); });
    await take.assertBeat('tracking', async (p) => /QUEUED|BAKING|QA_CHECK/.test(await textOf('.scr-09')), 'tracking must show the order in the kitchen');
  } else {
    await waitFor('.pcard');
    const bbq = await tag(page.locator('.pcard', { hasText: 'Binary BBQ' }), 'bbq-card');
    await beat('menu', async () => { await narrate.bringIntoView(page, bbq); await narrate.point(page, bbq); await page.waitForTimeout(1500); await narrate.unpoint(page); });
    const add = await tag(page.locator('.pcard', { hasText: 'Binary BBQ' }).locator('.btn-primary'), 'bbq-add');
    await beat('added', async () => { await act(add); await waitFor(badge); });
    await take.assertBeat('added', async (p) => (await p.locator(badge).first().innerText()).trim() === '1', 'the cart must hold one pizza');
    await toCheckout();
    await beat('checkout', async () => {
      await fillAddress('Alex Chen', 'alex.chen@example.com');
      await act('.mx-name-coc2');                       // Visa ending 0002: the simulated bank declines it
    });
    await take.assertBeat('checkout', (p) => p.locator('.mx-name-coc2.selected').first().waitFor({ state: 'visible', timeout: 5000 }).then(() => true),
      'the declining test card must be selected');
    await act('.mx-name-exec');
    await page.locator('.mx-window', { hasText: /declin/i }).first().waitFor({ state: 'visible', timeout: 30000 });
    await beat('declined');
    await take.assertBeat('declined', async (p) => /declin/i.test(await textOf('.mx-window')), 'the payment sheet must report the decline');
    await beat('switch', async () => { await act('.mx-window .mx-name-pmApple'); await act('.mx-window .mx-name-fRetry'); });
    await waitFor('.scr-08', 30000);
    await beat('confirmed');
    await take.assertBeat('confirmed', async (p) => /DEPLOYMENT SUCCESSFUL/.test(await textOf('.scr-08')), 'the retry must reach the confirmation');
    await act('.mx-name-fMonitor');
    await waitFor('.scr-09');
    await beat('tracking', async () => { await narrate.bringIntoView(page, '.scr-09 .term-body'); await narrate.point(page, '.scr-09 .term-body'); await page.waitForTimeout(2500); await narrate.unpoint(page); });
    await take.assertBeat('tracking', async (p) => /declin/i.test(await textOf('.scr-09 .term-body')), 'the order log must keep the declined attempt');
  }

  try { await page.evaluate(() => window.mx && mx.logout && mx.logout()); } catch (e) { /* session cap: always log out */ }
  const meta = await take.finish();
  await browser.close();
  console.log(`\n${film}/${device}: ${meta.beats.length} marks, ${meta.assertions.length} beats asserted, video ${meta.video}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
