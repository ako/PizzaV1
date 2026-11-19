#!/usr/bin/env python3
"""Tests and coverage report (HTML) from the raw test data.

    python3 docs/testing/tools/gen_tests.py          # -> docs/testing/report.html

Every number comes from data:
  docs/reports/raw/tests.json      mxcli report tests --format json (tests, journeys, reach per microflow)
  docs/reports/raw/junit.xml       mxcli test --junit (24 microflow tests, assertions, time)
  docs/reports/raw/journeys.jsonl  tests/e2e/journeys.js (start, end, status per journey)
  docs/overview/data/visual.json   tests/e2e/visual.js (12 screens vs the prototype)
  tests/*.test.mdl                 the @expect lines each microflow test pins
  docs/reports/tests-annotations.yaml  earlier human triage of the gaps
The grouping of the gaps, the judgements and the prose are written here by hand from that data;
asserts stop the build when a gap is not placed in exactly one group or the sources disagree.
"""
import collections
import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools'))
from report_kit import E, MODULE_COLOR, MODULE_ORDER, bar, finding, kpis, page, section, stack, table, write  # noqa: E402

OUT = os.path.join(REPO, 'docs', 'testing', 'report.html')
RAW = os.path.join(REPO, 'docs', 'reports', 'raw')

T = json.load(open(os.path.join(RAW, 'tests.json')))
D = T['data']
VIS = json.load(open(os.path.join(REPO, 'docs', 'overview', 'data', 'visual.json')))
JL = [json.loads(l) for l in open(os.path.join(RAW, 'journeys.jsonl')) if l.strip()]
JUNIT = ET.parse(os.path.join(RAW, 'junit.xml')).getroot()


def annotations():
    """The yaml is one flat map of `"key": {status: …, note: "…"}`; read it without a yaml dependency."""
    out = {}
    for line in open(os.path.join(REPO, 'docs', 'reports', 'tests-annotations.yaml')):
        m = re.match(r'\s*"([^"]+)":\s*\{status:\s*(\w+),\s*note:\s*"(.*)"\}\s*$', line)
        if m:
            out[m.group(1)] = {'status': m.group(2), 'note': m.group(3)}
    return out


ANN = annotations()

# ---------------------------------------------------------------- microflow tests (+ junit + sources)
tests = D['tests']
jcases = {c.get('name'): c for c in JUNIT.iter('testcase')}
suite = next(JUNIT.iter('testsuite'))
assert len(jcases) == len(tests) == int(suite.get('tests')), 'tests.json and junit.xml list the same tests'
for t in tests:
    c = jcases[t['name']]
    a = int(next(p.get('value') for p in c.iter('property') if p.get('name') == 'assertions'))
    assert a == t['assertions'], f'assertions differ for {t["name"]}'
    t['time'] = float(c.get('time'))
    t['failed'] = c.find('failure') is not None or c.find('error') is not None


def parse_test_file(rel):
    """@test name -> (expects, called microflows) from a .test.mdl file."""
    src = open(os.path.join(REPO, rel)).read()
    out = {}
    for chunk in re.split(r'^/\s*$', src, flags=re.M):
        docs = re.findall(r'/\*\*(.*?)\*/', chunk, re.S)
        doc = docs[-1] if docs else ''
        name = re.search(r'@test\s+(.+)', doc)
        if not name:
            continue
        exp = [e.strip() for e in re.findall(r'@expect\s+(.+)', doc)]
        out[name.group(1).strip()] = exp
    return out


EXPECTS = {}
for f in sorted({t['file'] for t in tests}):
    EXPECTS.update(parse_test_file(f))
for t in tests:
    assert len(EXPECTS[t['name']]) == t['assertions'], f'@expect lines and assertions differ: {t["name"]}'

FILE_ABOUT = {
    'tests/pricing.test.mdl': ('Pricing', 'Pricing rules BR-PRICE-05 … BR-PRICE-13 against the calculated examples of the acceptance test scenarios '
                               '(section 2.3): the order total with tax, delivery fee, tip and coupon (<code>Fulfilment.SUB_Price_Compute</code>), and a '
                               'configured line\'s unit price, allergens and vegan/vegetarian flags (<code>Shop.SUB_Line_ApplyDefaults</code> + '
                               '<code>SUB_Line_Recalculate</code>). "Example" tests are the worked examples; "P" tests are the rounding, cap, minimum and '
                               'waiver edge cases.'),
    'tests/helpers.test.mdl': ('Formatting helpers', 'Money text (BR-PRICE-14), the mm:ss timer and phone normalisation (BR-DATA-06) in Core: what every '
                               'price, countdown and phone number on screen goes through.'),
}


def ms(s):
    return '&lt;1' if s < 0.0005 else f'{s * 1000:.0f}'


def expect_html(e):
    e = re.sub(r'^\$\w+/', '', e)
    return f'<code>{E(e)}</code>'


test_sections = []
for f in sorted({t['file'] for t in tests}, key=lambda f: 0 if 'pricing' in f else 1):
    ts = [t for t in tests if t['file'] == f]
    title, about = FILE_ABOUT.get(f, (f, ''))
    rows = []
    for t in ts:
        tag = '<span class="tag bad">FAIL</span>' if t['failed'] or t['status'] != 'passed' else '<span class="tag good">PASS</span>'
        calls = ', '.join(f'<code>{E(c)}</code>' for c in t['calls'])
        rows.append([f'{E(t["name"])}<span class="rng">{calls}</span>', tag,
                     '<span class="pins">' + ' '.join(expect_html(e) for e in EXPECTS[t['name']]) + '</span>',
                     str(t['assertions']), ms(t['time'])])
    total_a = sum(t['assertions'] for t in ts)
    total_s = sum(t['time'] for t in ts)
    test_sections.append(
        f'<h3>{E(title)} <span class="muted">· <code>{E(f)}</code> · {len(ts)} tests, {total_a} assertions, {total_s * 1000:.0f} ms</span></h3>'
        f'<p class="note">{about}</p>'
        + table([('Test · microflow called', ''), ('Result', ''), ('What it pins', ''), ('Assertions', 'num'), ('ms', 'num')], rows, cls='tests'))

n_tests = len(tests)
n_pass = sum(1 for t in tests if t['status'] == 'passed' and not t['failed'])
n_assert = sum(t['assertions'] for t in tests)
direct = sorted({c for t in tests for c in t['calls']})
reached_by_tests = sorted({r for t in tests for r in t['reached']})

# ---------------------------------------------------------------- journeys
JS = {j['journey']: j for j in JL}


def jid(name):
    return name.split(' ', 1)[0]


def jnum(name):
    return int(jid(name)[1:])


def secs(j):
    f = lambda s: datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
    return (f(j['end']) - f(j['start'])).total_seconds()


journeys = D['journeys']
assert {j['name'] for j in journeys} == set(JS), 'tests.json and journeys.jsonl name the same journeys'
cnt = collections.Counter(m for j in journeys for m in j['executed'])
n_j = len(journeys)
n_j_pass = sum(1 for j in journeys if j['status'] == 'passed' and JS[j['name']]['status'] == 'passed')
j_total_s = sum(secs(JS[j['name']]) for j in journeys)
sim_bg = sorted(m for m in cnt if m.startswith('Simulation.'))
sim_everywhere = [m for m in sim_bg if cnt[m] == n_j]
run_order = [jid(j['journey']) for j in JL]
max_s = max(secs(JS[j['name']]) for j in journeys)

jrows = []
for j in sorted(journeys, key=lambda j: jnum(j['name'])):
    name = j['name']
    jj = JS[name]
    ok = j['status'] == 'passed' and jj['status'] == 'passed'
    app = [m for m in j['executed'] if not m.startswith('Simulation.')]
    bym = collections.Counter(m.split('.')[0] for m in app)
    split = ' · '.join(f'{m} {bym[m]}' for m in MODULE_ORDER if bym.get(m))
    uniq = [m for m in app if cnt[m] == 1]
    uniq_html = (', '.join(f'<code>{E(m.split(".", 1)[1])}</code>' for m in uniq if '.ACT_' in m or '.DS_' in m or 'Fulfilment.' in m)
                 or '<span class="muted">none — every microflow it runs is also run by another journey</span>')
    s = secs(jj)
    jrows.append([f'<span class="tag ink">{E(jid(name))}</span>', f'{E(name.split(" ", 1)[1])}<span class="rng">{E(split)}</span>',
                  '<span class="tag good">PASS</span>' if ok else '<span class="tag bad">FAIL</span>',
                  f'<div class="vrow">{bar(s / max_s * 100, "brand", "")}<span>{s:.1f} s</span></div>',
                  f'{len(app)}', f'{len(uniq)}', uniq_html])
journey_table = table([('', ''), ('Journey', ''), ('Result', ''), ('Duration', ''), ('Microflows', 'num'), ('Only here', 'num'),
                       ('Only this journey runs', '')], jrows, cls='journeys')

# ---------------------------------------------------------------- coverage per module
CATS = [('both', 'tests and journeys', '--c-both', 'Both'), ('testsOnly', 'tests only', '--c-tests', 'Tests only'),
        ('journeysOnly', 'journeys only', '--c-journeys', 'Journeys only'), ('startup', 'startup or scheduled', '--c-startup', 'Startup'),
        ('neither', 'neither', '--c-neither', 'Neither')]
mods = {m['module']: m for m in D['modules']}
tot = D['totals']
assert sum(m['total'] for m in D['modules']) == tot['total'] == D['microflows'] == len(D['reach'])
for k, *_ in CATS:
    assert sum(m[k] for m in D['modules']) == tot[k], k
non_startup = tot['total'] - tot['startup']
reached = tot['both'] + tot['testsOnly'] + tot['journeysOnly']
by_tests = tot['both'] + tot['testsOnly']
assert reached + tot['neither'] == non_startup
assert sorted(reached_by_tests) == sorted(m for m, v in D['reach'].items() if v in ('both', 'tests only'))


def cov_row(name, m, dot=True):
    ns = m['total'] - m['startup']
    r = m['both'] + m['testsOnly'] + m['journeysOnly']
    label = (f'<i class="dot" style="background:var({MODULE_COLOR[name]})"></i>' if dot else '') + E(name or 'All app modules')
    st = stack([(m[k], c, lab) for k, lab, c, _ in CATS])
    pct = f'{r / ns * 100:.0f}%' if ns else '—'
    return [label, str(m['total'])] + [str(m[k]) if m[k] else '<span class="muted">0</span>' for k, *_ in CATS] + [
        f'{r} of {ns}<span class="rng">{pct}</span>' if ns else '<span class="muted">all startup</span>', st]


cov_rows = [cov_row(m, mods[m]) for m in MODULE_ORDER]
cov_rows.append({'cls': 'total', 'cells': cov_row('', tot, dot=False)})
cov_table = table([('Module', ''), ('Microflows', 'num')] + [(short, 'num') for *_, short in CATS] + [('Reached', 'num'), ('Mix', '')],
                  cov_rows, cls='cov')
cov_legend = '<div class="legend">' + ''.join(f'<span><i style="background:var({c})"></i>{E(lab)}</span>' for _, lab, c, _ in CATS) + '</div>'
shop = mods['Shop']
shop_ns = shop['total'] - shop['startup']
sim = mods['Simulation']

# ---------------------------------------------------------------- visual comparison
screens = VIS['screens']
vmax = max(s['budget'] for s in screens)
vrows = []
for s in screens:
    mm, b = s['mismatch'], s['budget']
    ratio = mm / b
    st = 'bad' if mm > b else 'warn' if ratio >= 0.75 else 'good'
    scr, rest = s['id'].split('-', 2)[:2], s['id'].split('-', 2)[2]
    view = 'phone 390×844' if rest.endswith('-m') else 'desktop 1440×900'
    label = f'{mm:.2f} % of {b:g} %'
    vbar = (f'<div class="vrow"><div class="vbar {st}" role="img" aria-label="{E(label)}"><i style="width:{mm / vmax * 100:.1f}%"></i>'
            f'<b style="left:{b / vmax * 100:.1f}%" title="budget {b:g} %"></b></div><span>{E(label)}</span></div>')
    vrows.append([f'<code>{E("-".join(scr))}</code> {E(rest[:-2].replace("-", " "))}', E(view), vbar,
                  f'{ratio * 100:.0f}%', f'<span class="tag {st}">{"over" if st == "bad" else "near" if st == "warn" else "within"}</span>'])
vis_table = table([('Screen', ''), ('Viewport', ''), ('Differing pixels vs budget', ''), ('Of budget', 'num'), ('', '')], vrows, cls='vis')
v_ok = sum(1 for s in screens if s['mismatch'] <= s['budget'])
v_worst = max(screens, key=lambda s: s['mismatch'])
v_tight = max(screens, key=lambda s: s['mismatch'] / s['budget'])
v_near = [s for s in screens if s['mismatch'] / s['budget'] >= 0.75]
v_phone = [s for s in screens if s['id'].endswith('-m')]
v_desk = [s for s in screens if s['id'].endswith('-d')]
avg = lambda xs: sum(s['mismatch'] for s in xs) / len(xs)

# ---------------------------------------------------------------- gaps: grouped by hand, every gap exactly once
GROUPS = [
    ('G1', 'bad', 'Add a test', 'Cancelling a payment', [
        'Shop.ACT_Pay_Cancel', 'Shop.ACT_Pay_CancelAndCart', 'Shop.ACT_Pay_ToCart', 'Shop.SUB_Pay_Cancel'],
     'The payment sheet\'s cancel paths change an order that is already placed: cancel, cancel and back to the cart, back to the cart. J3 covers a '
     'declined card and a retry, but no journey walks away from a payment. A state change on an order with money attached is exactly what a test is for: '
     'one journey step (cancel on the payment sheet, then check the order status and that the cart is back) covers all four.'),
    ('G2', 'bad', 'Add a test', 'Opening an order by its tracking link', [
        'Shop.ACT_Track_Token', 'Shop.SUB_Track_Token', 'Shop.ACT_Track_OpenView', 'Shop.SUB_Track_OpenView', 'Shop.ACT_Track_RetryOpen'],
     '<code>ACT_Track_Token</code> is the entry point of the personal tracking link <code>/p/track/{token}</code> (US-121, NFR-11): a valid token of a '
     'guest order grants the browser session access to that order; an unknown, short or simulated-order token shows the invalid-link page (US-134, '
     'LITE-SEC-05). The journeys reach tracking only right after paying or through the lookup form, so neither branch has ever run. Access to someone '
     'else\'s order is the one gap with a security edge: a journey that opens a known token and an altered one would cover it.'),
    ('G3', 'warn', 'Worth a journey step', 'Editing what is already in the cart', [
        'Shop.ACT_Cart_Edit', 'Shop.ACT_Configure_Edit', 'Shop.SUB_Configure_Edit', 'Shop.ACT_Line_Remove', 'Shop.SUB_Line_Remove',
        'Shop.ACT_Config_Qty', 'Shop.SUB_Config_Qty', 'Shop.ACT_Config_Back', 'Shop.SUB_Config_Back', 'Shop.ACT_Cart_Checkout', 'Shop.ACT_Cart_ToMenu'],
     'Re-opening a line in the configurator, the configurator\'s own quantity stepper, removing one line, and the cart\'s checkout and back-to-menu buttons. '
     'The pricing underneath (<code>SUB_Line_Recalculate</code>, <code>SUB_Cart_Recalculate</code>) is covered, so the risk is the wiring, not the sums. '
     'J9\'s name says "remove", but it changes the quantity and clears the cart: <code>SUB_Line_Remove</code> never runs. Adding "edit line, change size, '
     'remove it" to J9 would close most of this group.'),
    ('G4', 'warn', 'Worth a journey step', 'Removing a coupon and switching to pickup', [
        'Shop.ACT_Coupon_Remove', 'Shop.SUB_Coupon_Remove', 'Shop.ACT_Checkout_Pickup', 'Shop.SUB_Checkout_Pickup'],
     'Both change the total: removing a coupon must restore the discount, and the "Switch to pickup" button (shown when the address is outside the delivery zone) must drop '
     'fee and tip. The rules themselves are pinned by the pricing tests (P2-pickup, Example D) and J11 switches to pickup through the order-type tile, '
     'so these are second paths to covered logic. One step each in J2 and J11.'),
    ('G5', 'warn', 'Worth a journey step', 'Product info and the order\'s details', [
        'Shop.ACT_Product_Info', 'Shop.DS_Info_Line', 'Shop.ACT_Info_Add', 'Shop.SUB_Info_Add',
        'Shop.ACT_Receipt_Open', 'Shop.DS_Order_History', 'Shop.DS_Order_Payments', 'Shop.DS_OrderLine_Modifiers'],
     'The product info dialog has its own add-to-cart (<code>SUB_Info_Add</code>), a third way into the cart next to quick add and the configurator. '
     'The receipt, status history, payment list and line modifiers on the tracking page are read-only data sources: J1 and J3 open tracking, '
     'but these parts are behind a click no journey makes. Low risk; the info dialog\'s add is the one worth a check.'),
    ('G6', 'good', 'Accepted', 'Secondary navigation and UI state', [
        'Shop.ACT_Nav_Home', 'Shop.ACT_Nav_Menu', 'Shop.SUB_Nav_Menu', 'Shop.ACT_Nav_Search', 'Shop.SUB_Nav_Search', 'Shop.ACT_Nav_Track',
        'Shop.SUB_Nav_Track', 'Shop.ACT_Menu_ClearSearch', 'Shop.SUB_Menu_ClearSearch', 'Shop.ACT_Menu_ShowAll', 'Shop.SUB_Menu_ShowAll',
        'Shop.ACT_Toast_Close', 'Shop.ACT_Toast_Copied', 'Core.SUB_Toast_Close'],
     'Header links, clearing a search, "show all", closing a toast and the "copied" toast. The earlier triage accepted these and nothing has changed: '
     'each is one page open or one attribute set, and a broken one is visible at once.'),
    ('G7', 'good', 'Accepted', 'Error page and fault probe', ['Shop.DS_Error', 'Shop.DS_FaultProbe'],
     '<code>DS_Error</code> feeds SCR-41, shown only when something has already gone wrong; the visual comparison opens <code>/p/error</code> and finds it within '
     'budget, but that run is outside the journeys\' span windows. <code>DS_FaultProbe</code> runs only with the opt-in constant <code>Shop.FaultInjection</code> '
     'for the US-282 acceptance test.'),
    ('G8', 'none', 'Delete', 'Unused since the performance fix', ['Shop.DS_Product_Recipe'],
     'No page uses it since performance fix F4 stored the toppings line on the product. It is not a test gap but dead code: re-anchor requirement US-026 on '
     '<code>Shop.SUB_Product_Recalculate</code>, then delete it.'),
]
gap_set = {m for g in D['gaps'] for m in g['microflows']}
grouped = [m for g in GROUPS for m in g[4]]
assert len(grouped) == len(set(grouped)), 'a gap is in two groups'
assert set(grouped) == gap_set, f'ungrouped: {gap_set - set(grouped)}; not a gap: {set(grouped) - gap_set}'
assert len(gap_set) == tot['neither']
want_test = sum(len(g[4]) for g in GROUPS if g[1] == 'bad')
want_step = sum(len(g[4]) for g in GROUPS if g[1] == 'warn')
accepted = sum(len(g[4]) for g in GROUPS if g[1] == 'good')
gap_mod = collections.Counter(m.split('.')[0] for m in gap_set)

gap_findings = []
for tag, cls, status, title, mfs, body in GROUPS:
    by = collections.Counter(m.split('.')[0] for m in mfs)
    names = ' '.join(f'<code>{E(m)}</code>' for m in mfs)
    gap_findings.append(finding(tag, cls, f'{status} · {len(mfs)} microflow{"s" if len(mfs) != 1 else ""}', E(title),
                                f'<p>{body}</p><p class="mfs">{names}</p>', tag_cls='bad' if cls == 'bad' else 'warn' if cls == 'warn' else 'none'))
shop_note = ANN.get('gap:Shop', {}).get('note', '')

# ---------------------------------------------------------------- page
heads = kpis([
    (f'{n_pass} of {n_tests}', f'Microflow tests passed, with {n_assert} assertions in {float(suite.get("time")) * 1000:.0f} ms: '
                               f'the pricing worked examples and the formatting helpers', 'good' if n_pass == n_tests else 'bad'),
    (f'{n_j_pass} of {n_j}', f'Browser journeys passed against the running app, {j_total_s / 60:.1f} minutes end to end: order, pay, coupon, '
                             f'declined card, lookup, errors, connection loss, phone layout', 'good' if n_j_pass == n_j else 'bad'),
    (f'{reached} of {non_startup}', f'Microflows reached by a test or journey ({reached / non_startup * 100:.0f}%), not counting the {tot["startup"]} that run '
                                    f'at startup or on a schedule. Only {by_tests} are reached by a microflow test', 'warn'),
    (f'{v_ok} of {len(screens)}', f'Screens within their visual budget against the prototype; the largest difference is {v_worst["mismatch"]:.2f} % of pixels '
                                  f'({E(v_worst["id"])}, budget {v_worst["budget"]:g} %)', 'good' if v_ok == len(screens) else 'bad'),
])

lede = (f'Three layers of tests on GitPizza: {n_tests} microflow tests that pin the pricing and formatting rules, {n_j} browser journeys that drive the '
        f'running app the way a guest does, and a pixel comparison of {len(screens)} screens with the prototype. Which microflows they reach is '
        f'measured — statically for the microflow tests, from runtime spans for the journeys — and what neither reaches is triaged below.')

coverage = (
    f'<p>Every app microflow falls in one of five groups: reached by a microflow test and a journey, by tests only, by journeys only, run at startup '
    f'or on a schedule (not a gap), or by neither. Counts are in the columns; the bar shows each module\'s mix.</p>'
    f'{cov_legend}<div class="panel">{cov_table}</div>'
    f'<ul class="tight reading">'
    f'<li><b>The journeys carry the coverage.</b> {tot["journeysOnly"]} of the {reached} reached microflows are reached by journeys only; '
    f'microflow tests reach {by_tests}, and every one of those is also run by a journey ({tot["testsOnly"]} "tests only"). The tests call {len(direct)} '
    f'microflows directly ({", ".join(f"<code>{E(m)}</code>" for m in direct)}); the rest of their {by_tests} is what those call.</li>'
    f'<li><b>Catalog, Core and Fulfilment are nearly closed.</b> Catalog {mods["Catalog"]["both"]} of {mods["Catalog"]["total"]} by both layers; '
    f'Fulfilment {mods["Fulfilment"]["both"] + mods["Fulfilment"]["journeysOnly"]} of {mods["Fulfilment"]["total"]}, but only '
    f'{mods["Fulfilment"]["both"]} of them (pricing and coupons) by a microflow test — the order transitions, refund and cancel are proved only end to end. '
    f'Core\'s one gap is closing a toast.</li>'
    f'<li><b>Shop holds {gap_mod["Shop"]} of the {tot["neither"]} gaps.</b> {shop["both"] + shop["journeysOnly"]} of its {shop_ns} non-startup microflows '
    f'are reached ({(shop["both"] + shop["journeysOnly"]) / shop_ns * 100:.0f}%). Its gaps are the storefront\'s side doors, sorted in "Gaps" below.</li>'
    f'<li><b>Simulation is {sim["startup"]} startup microflows</b> — the generated seed and the reset — and {sim["journeysOnly"]} "journeys only". Those '
    f'{sim["journeysOnly"]} are the simulator\'s clock: {len(sim_everywhere)} of them (<code>SIM_Tick</code> among them) ran inside all {n_j} journey windows, '
    f'because a span counts for whichever journey is running. They are reached by the scheduler, not by what a guest does.</li></ul>')

tests_sec = (f'<p>{n_tests} tests in {len(FILE_ABOUT)} files, {n_assert} assertions, all on the logic that decides a number a guest sees. Each test calls one '
             f'microflow with fixed input and checks the result against values worked out by hand in the acceptance scenarios. '
             f'"What it pins" is the test\'s <code>@expect</code> lines.</p>' + ''.join(test_sections))

journeys_sec = (f'<p>Playwright scripts in <code>tests/e2e/journeys.js</code>, each in a fresh guest session against the running app. They ran one after another '
                f'in the order {", ".join(run_order)}, {j_total_s:.0f} s in all. "Microflows" counts the app microflows whose spans started inside the journey\'s '
                f'time window, without the simulator\'s background clock, split by module under the name; "only here" is how many no other journey runs — what each one adds. '
                f'The last column lists those actions, data sources and order logic.</p>'
                f'<div class="panel">{journey_table}</div>'
                f'<p class="note">J5 (404), J6 (connection loss) and J7 (phone layout) add no microflow of their own: they test what the guest sees, which coverage by '
                f'microflow does not measure. J1 adds nothing either — J3 and J11 between them run everything it runs — but it is the happy path the others vary.</p>')

vis_sec = (f'<p>The third layer: <code>tests/e2e/visual.js</code> screenshots the first viewport of {len(screens) // 2} screens on desktop and phone and counts the '
           f'share of pixels that differ from the prototype by more than 32 in any colour channel. Live data (KPIs, clocks, order numbers) never matches, so '
           f'each screen has a budget. The bar is the difference, the tick the budget; measured {E(VIS["measuredAt"])}.</p>'
           f'<div class="panel">{vis_table}</div>'
           f'<p>All {len(screens)} are within budget. Phone screens differ more than desktop (average {avg(v_phone):.1f} % against {avg(v_desk):.1f} %), and '
           f'{len(v_near)} sit at three quarters of their budget or more: {", ".join(f"<code>{E(s["id"])}</code> {s["mismatch"]:.2f} %" for s in v_near)}. '
           f'Those are the ones a small layout change would push over.</p>')

gaps_sec = (f'<p>The {tot["neither"]} microflows no test or journey reaches, grouped by what they do. The earlier triage accepted Shop\'s gaps as a whole '
            f'("{E(shop_note)}"). That still holds for the logic — pricing, coupons and line configuration are pinned — but not for every group: '
            f'{want_test} microflows change an order or grant access to one and deserve a test, {want_step} are second paths to covered logic worth a journey '
            f'step, {accepted} are accepted, and 1 is dead code.</p>'
            f'<div class="findings">{"".join(gap_findings)}</div>')

how = ('<ul class="tight">'
       f'<li><code>mxcli report tests --format json</code> (mxcli {E(T["mxcli"])}, generated {E(T["generated"])}) → <code>docs/reports/raw/tests.json</code>: '
       'per-test results, static reach of each microflow test through the call graph, and runtime reach of each journey from the '
       '<code>Microflow</code> spans of the app running with <code>run --local --trace-otlp</code>.</li>'
       '<li><code>mxcli test tests/ --junit</code> → <code>junit.xml</code> (result, assertions, time); the <code>@expect</code> lines are read from '
       '<code>tests/*.test.mdl</code> and checked against the assertion count.</li>'
       '<li><code>node tests/e2e/journeys.js</code> → <code>journeys.jsonl</code> (start, end, status); <code>node tests/e2e/visual.js</code> → '
       '<code>docs/overview/data/visual.json</code>.</li>'
       '<li>This page: <code>docs/testing/tools/gen_tests.py</code>. Gap groups, judgements and prose are written there by hand from the data, reusing '
       '<code>docs/reports/tests-annotations.yaml</code>; asserts stop the build when a gap is ungrouped or the sources disagree.</li></ul>')
limits = '<ul class="tight">' + ''.join(f'<li>{E(l.replace("the database state is stated above when the journey log records it", "this run\'s journey log records no database state, and all eleven passed")).replace("`", "")}</li>' for l in T['limits']) + (
    '<li>Runtime reach counts every microflow span inside a journey\'s window, so the simulator\'s clock is credited to every journey (see Coverage).</li>'
    '<li>The visual comparison was measured separately from the journeys, earlier the same day, and covers the first viewport of six screens only.</li></ul>')

body = (heads
        + section('Coverage per module', coverage)
        + section('The microflow tests', tests_sec)
        + section('The journeys', journeys_sec)
        + section('Visual comparison with the prototype', vis_sec)
        + section('Gaps', gaps_sec)
        + f'<section class="cols"><div><h2>How this was made</h2>{how}</div><div><h2>Limits</h2>{limits}</div></section>')

EXTRA = r'''
:root { --c-both: var(--good); --c-tests: var(--s7); --c-journeys: var(--s1); --c-startup: #c9c6bd; --c-neither: var(--bad); }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --c-startup: #4a4b50; } }
:root[data-theme="dark"] { --c-startup: #4a4b50; }
table.cov td:last-child { min-width: 220px; }
table.cov tr.total td { border-top: 2px solid var(--ink); font-weight: 600; }
table.cov td:first-child { white-space: nowrap; }
ul.reading { margin-top: 14px; }
table.tests td:first-child { min-width: 260px; }
.pins { display: flex; flex-wrap: wrap; gap: 4px; }
.pins code { background: var(--bg); border: 1px solid var(--line); border-radius: 3px; padding: 1px 5px; font-size: 11.5px; white-space: nowrap; }
section h3 { margin-top: 18px; }
section h3 .muted { font-weight: 400; font-size: 14px; }
table.journeys td:nth-child(2) { min-width: 240px; }
table.journeys td:last-child { font-size: 13px; min-width: 200px; width: 30%; }
table.journeys .bar { width: 110px; flex: none; }
table.tests td:first-child { width: 36%; } table.tests td:nth-child(2) { width: 70px; }
.vbar { position: relative; flex: 1; min-width: 120px; max-width: 360px; height: 20px; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; }
.vbar i { position: absolute; inset: 0 auto 0 0; border-radius: 2px 0 0 2px; }
.vbar.good i { background: var(--good-bg); border-right: 2px solid var(--good); }
.vbar.warn i { background: var(--warn-bg); border-right: 2px solid var(--warn); }
.vbar.bad i { background: var(--bad-bg); border-right: 2px solid var(--bad); }
.vbar b { position: absolute; top: -3px; bottom: -3px; width: 2px; background: var(--ink); }
.vrow { display: flex; align-items: center; gap: 10px; }
.vrow > span { font: 600 12px var(--f-mono); white-space: nowrap; }
table.vis td:first-child { min-width: 200px; }
table.vis td:nth-child(3) { width: 45%; }
p.mfs { display: flex; flex-wrap: wrap; gap: 4px 10px; font-size: 12px; color: var(--muted); }
p.mfs code { font-size: 11.5px; }
.finding h3 { margin-top: 4px; }
@media (max-width: 600px) { .finding { grid-template-columns: 44px 1fr; gap: 10px; } }
'''

html = page('GitPizza Tests and Coverage', eyebrow='GitPizza · tests and coverage · 19 November 2026',
            lede=lede, body=body, current='tests', extra_css=EXTRA)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
write(OUT, html)
