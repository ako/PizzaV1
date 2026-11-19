#!/usr/bin/env python3
"""Render docs/perf/report.html from the measured data in docs/perf/data/.

    python3 docs/perf/tools/analyse.py docs/perf/data/before      # per run: guest-only figures + flame
    python3 docs/perf/tools/analyse.py docs/perf/data/after
    python3 docs/perf/tools/analyse.py docs/perf/data/drain
    python3 docs/perf/tools/gen_report.py                           # -> docs/perf/report.html

Every figure on the page comes from data/: before.json / after.json / drain.json (analyse.py),
before-/after-statements.psv (pg_stat_statements), f1-incident.json (runtime log of the first
volume run) and volume.json. The findings' prose is written here, by hand, from that data.
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
OUT = os.path.join(HERE, '..', 'report.html')
E = html.escape


def load(n):
    return json.load(open(os.path.join(DATA, n)))


before, after, drain = load('before.json'), load('after.json'), load('drain.json')
f1, volume = load('f1-incident.json'), load('volume.json')
B = {(s['journey'], s['step']): s for s in before['steps']}
A = {(s['journey'], s['step']): s for s in after['steps']}
ORDER = [(s['journey'], s['step']) for s in after['steps']]
J = {'Guest orders a pizza': 'J1 Order', 'Guest finds a past order': 'J2 Lookup'}
CHANGED = {('Guest orders a pizza', s) for s in ('1 open home', '2 open menu', '3 open configurator', '4 choose extra', '5 add to cart')}


def step(j, s):
    return A[(j, s)], B[(j, s)]


def statements(name):
    rows = []
    for line in open(os.path.join(DATA, name)):
        calls, total, mean, nrows, q = line.rstrip('\n').split('|', 4)
        rows.append({'calls': int(calls), 'total': float(total), 'mean': float(mean), 'rows': int(nrows), 'sql': q})
    return rows


def find_stmt(rows, pattern):
    for r in rows:
        if re.search(pattern, r['sql']):
            return r
    return None


SB, SA = statements('before-statements.psv'), statements('after-statements.psv')
KPI = r'completedat" >= '
kpi_b, kpi_a = find_stmt(SB, KPI), find_stmt(SA, KPI)


def fmt(v, unit=''):
    if v is None:
        return '—'
    v = float(v)
    s = f'{v:,.0f}' if abs(v) >= 10 else f'{v:,.1f}'
    return s + unit


def pct(b, a):
    if not b:
        return ''
    d = (a - b) / b * 100
    return f'{d:+.0f}%'


# ---------------------------------------------------------------- flame chart
def flame(st, title, width=1100, row=18):
    fl = st['flame']
    spans = fl['spans']
    if not spans:
        return '<p class="muted">No guest requests in this window.</p>'
    total = max(fl['windowMs'], max(s['start'] + s['dur'] for s in spans))
    bands = {}
    for s in spans:
        bands[s['band']] = max(bands.get(s['band'], 0), s['depth'] + 1)
    offs, y = {}, 0
    for b in sorted(bands):
        offs[b] = y
        y += bands[b]
    h = y * row + 26
    plot = width - 40
    px = lambda ms: ms / total * plot
    parts = [f'<svg class="flame" viewBox="0 0 {width} {h}" width="100%" role="img" aria-label="{E(title)}">']
    stepms = next(s for s in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000) if total / s <= 10)
    t = 0
    while t <= total:
        x = px(t)
        parts.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{h - 14}" class="grid"/>'
                     f'<text x="{x + 2:.1f}" y="{h - 3}" class="tick">{t:g} ms</text>')
        t += stepms
    for s in sorted(spans, key=lambda s: (s['band'], s['depth'], s['start'])):
        x0 = px(max(s['start'], 0))
        w = max(px(s['dur']), 0.8)
        yy = (offs[s['band']] + s['depth']) * row
        lab = s['name']
        tip = E(f"{lab}\n{s['dur']:.2f} ms")
        parts.append(f'<g class="sp {s["kind"]}"><title>{tip}</title><rect x="{x0:.1f}" y="{yy}" width="{w:.1f}" height="{row - 2}" rx="2"/>')
        if w > 40:
            chars = int(w / 6.2)
            txt = lab if len(lab) <= chars else lab[:max(chars - 1, 1)] + '…'
            parts.append(f'<text x="{x0 + 3:.1f}" y="{yy + row - 6}">{E(txt)}</text>')
        parts.append('</g>')
    parts.append('</svg>')
    return ''.join(parts)


def figure(st, label):
    return (f'<figure class="fc"><figcaption><b>{E(label)}</b>'
            f'<span>browser {fmt(st["browserMs"])} ms · {round(st["requests"])} requests · server {fmt(st["serverMs"])} ms · '
            f'database {fmt(st["dbMs"])} ms in {round(st["queries"])} queries · run {st["flame"]["run"]}</span></figcaption>'
            f'<div class="scroll">{flame(st, label)}</div></figure>')


# ---------------------------------------------------------------- figures used in the prose
menu_a, menu_b = step('Guest orders a pizza', '2 open menu')
cart_a, cart_b = step('Guest orders a pizza', '5 add to cart')
conf_a, conf_b = step('Guest orders a pizza', '3 open configurator')
ext_a, ext_b = step('Guest orders a pizza', '4 choose extra')
home_a, home_b = step('Guest orders a pizza', '1 open home')
pay_a, pay_b = step('Guest orders a pizza', '8 place order and pay')
trk_a, trk_b = step('Guest orders a pizza', '9 open tracking')
lk_a, _ = step('Guest finds a past order', '2 find order by number and email')
tl_a, _ = step('Guest finds a past order', '3 open tracking link')
dr_pay = next(s for s in drain['steps'] if s['step'] == '8 place order and pay')
orders = volume['rows'][0][1]

kpis = [
    (f'<s>{f1["blockedMinutes"]} min</s> {f1["after"]["housekeepingMedianMs"]} ms',
     f'Housekeeping with a backlog of {f1["backlogEvents"]:,} events: one transaction that blocked every checkout until it was aborted, now batches of {f1["after"]["housekeepingMedianMs"]} ms (max {f1["after"]["housekeepingMaxMs"]}) per tick'),
    (f'<s>{fmt(menu_b["browserMs"])}</s> {fmt(menu_a["browserMs"])} ms',
     f'Opening the menu ({fmt(menu_b["queries"])} → {fmt(menu_a["queries"])} database queries; one data source per product card is gone)'),
    (f'<s>{fmt(cart_b["dbMs"])}</s> {fmt(cart_a["dbMs"])} ms',
     f'Database time to add a configured pizza to the cart ({fmt(cart_b["queries"])} → {fmt(cart_a["queries"])} queries)'),
    (f'<s>{kpi_b["mean"]:.0f}</s> {kpi_a["mean"]:.0f} ms',
     f'The home page\'s "deployed today" query over {orders:,} orders: a full table scan became an index range scan'),
]

# ---------------------------------------------------------------- step table
rows = []
for k in ORDER:
    a, b = A[k], B[k]
    hit = ' class="hit"' if k in CHANGED else ''
    rows.append(f'<tr{hit}><th scope="row"><span class="j">{E(J[k[0]])}</span>{E(k[1].split(" ", 1)[1])}</th>'
                f'<td>{fmt(b["browserMs"])}<span class="rng">{fmt(b["range"]["browserMs"][0])}–{fmt(b["range"]["browserMs"][1])}</span></td>'
                f'<td>{fmt(a["browserMs"])}<span class="rng">{fmt(a["range"]["browserMs"][0])}–{fmt(a["range"]["browserMs"][1])}</span></td>'
                f'<td class="d">{pct(b["browserMs"], a["browserMs"])}</td>'
                f'<td>{fmt(b["serverMs"])} → {fmt(a["serverMs"])}</td><td>{fmt(b["dbMs"])} → {fmt(a["dbMs"])}</td>'
                f'<td>{fmt(b["queries"])} → {fmt(a["queries"])}</td></tr>')
table = ''.join(rows)

# ---------------------------------------------------------------- findings (prose by hand, figures from data)
def F(tag, cls, status, title, body):
    return (f'<article class="finding"><span class="tag {cls}">{tag}</span><div><span class="status {cls}">{status}</span>'
            f'<h3>{title}</h3>{body}</div></article>')


findings = [
    F('F1', 'fixed', 'Fixed · locking', 'Housekeeping held a 10-minute transaction and blocked every checkout',
      f'<p>Every 15 minutes the simulator\'s tick runs housekeeping (SIM-08): it removes simulated orders and simulation events older than 24 hours. '
      f'It loaded <em>all</em> of them and deleted them in one transaction. With a backlog of {f1["backlogEvents"]:,} events — what housekeeping that was off or failing leaves behind — '
      f'that transaction ran from {f1["blockedFrom"]} until the runtime aborted it at {f1["abortedAt"]}. It held the store-settings row it had locked to number a new order, '
      f'so every guest\'s <code>Execute Order --force</code> waited on that lock and the step timed out; the watchdog restarted the clock every minute, and the abort rolled back '
      f'the "last run" time too, so the next tick started the same delete again. In this state the shop takes no orders at all.</p>'
      f'<p>Fix: <code>Simulation.SIM_Housekeeping</code> deletes oldest-first in batches of {f1["after"]["eventsPerTick"]:,} events and {f1["after"]["ordersPerTick"]} orders per tick, '
      f'and marks the run done only when a batch comes back short; an index on <code>SimulationEvent.OccurredAt</code> finds the batch. Measured on the same backlog: housekeeping '
      f'{f1["after"]["housekeepingMedianMs"]} ms per tick (max {f1["after"]["housekeepingMaxMs"]}), the whole tick {f1["after"]["tickMedianMs"]} ms (max {f1["after"]["tickMaxMs"]}), and all twelve steps ran '
      f'during the drain — "place order and pay" in {fmt(dr_pay["browserMs"])} ms, as without a backlog.</p>'),
    F('F2', 'fixed', 'Fixed · index', 'The home KPIs scanned every order ever placed',
      f'<p><code>Shop.SUB_Home_Refresh</code> counts the orders completed today: <code>[(OrderStatus = DELIVERED or PICKED_UP) and CompletedAt &gt;= today]</code>. '
      f'Without an index on <code>CompletedAt</code> Postgres read all {orders:,} orders on every home page: {kpi_b["mean"]:.1f} ms per call. '
      f'Fix: index on <code>Order.CompletedAt</code>: {kpi_a["mean"]:.1f} ms, reading only today\'s rows. Database time of the home step {fmt(home_b["dbMs"])} → {fmt(home_a["dbMs"])} ms.</p>'),
    F('F3', 'fixed', 'Fixed · index', 'The traffic generator and housekeeping scanned every order too',
      '<p>The traffic generator counts open simulated orders before it spawns one (<code>[Source = SIMULATOR and IsOpen]</code>, 54 ms) and housekeeping looks for finished '
      'simulated orders past their retention (<code>… and StatusChangedAt &lt; cutoff</code>, 48 ms). Both were sequential scans, because guest orders — the whole history — '
      'match neither. Fix: one index on <code>Order(Source, IsOpen, StatusChangedAt)</code> serves both; the housekeeping query now reads the index only (0.07 ms in '
      '<code>EXPLAIN ANALYZE</code>). These run in the background, so no guest step shows them, but they ran every few seconds against the full table.</p>'),
    F('F4', 'fixed', 'Fixed · query', 'The menu ran a data source for every product card',
      f'<p>Each card\'s code block listed the toppings through a nested list fed by <code>Shop.DS_Product_Recipe</code>: twelve microflow calls and their association reads per menu render, '
      f'and again whenever the menu refreshed after an add. Fix: the toppings line is stored on the product (<code>CodeToppings</code>) by <code>Shop.SUB_Product_Recalculate</code>, '
      f'like the card\'s other derived values, and recalculated at every start. Menu: {fmt(menu_b["queries"])} → {fmt(menu_a["queries"])} queries, browser {fmt(menu_b["browserMs"])} → {fmt(menu_a["browserMs"])} ms.</p>'),
    F('F5', 'fixed', 'Fixed · query', 'Configuring a pizza cost two queries per option and per ingredient',
      f'<p><code>Shop.DS_Config_Choices</code> read each option\'s ingredient twice to decide stock (once in <code>Catalog.SUB_Option_AvailableFor</code>), and '
      f'<code>Shop.SUB_Line_Recalculate</code> read each recipe item\'s ingredient and its allergens one by one. Fix: one query for the options whose ingredient is out of stock, '
      f'one for the recipe\'s ingredients (found in memory per item) and, without removed toppings, one for their allergens; a new <code>Catalog.SUB_Option_Selectable</code> decides '
      f'availability without database access. Queries: configurator {fmt(conf_b["queries"])} → {fmt(conf_a["queries"])}, choose extra {fmt(ext_b["queries"])} → {fmt(ext_a["queries"])}, '
      f'add to cart {fmt(cart_b["queries"])} → {fmt(cart_a["queries"])} (database {fmt(cart_b["dbMs"])} → {fmt(cart_a["dbMs"])} ms). The configurator\'s browser time did not improve: '
      f'its server work fell ({fmt(conf_b["serverMs"])} → {fmt(conf_a["serverMs"])} ms), but the median after-run caught one 2-second live-poll request inside its window (see "How it was measured").</p>'),
    F('F6', 'open', 'Open · recommendation', 'Adding to the cart still recalculates every line several times',
      f'<p>An add runs <code>SUB_Line_Recalculate</code> for the new line in <code>SUB_Config_Commit</code> and twice in <code>SUB_Cart_AddLine</code>, then once per cart line in '
      f'<code>SUB_Cart_Recalculate</code>, so its cost grows with the cart (up to 30 items). The configurator also calls <code>DS_Config_Choices</code> once per tile group (seven times), '
      f'each re-checking cart ownership and re-reading product and size: still {fmt(conf_a["queries"])} queries. Recommended: recalculate only the changed line and refresh the cart totals '
      f'from stored line values; build all tile groups in one data source.</p>'),
    F('F7', 'open', 'Open · recommendation', 'The home KPIs still load the day\'s orders to count them',
      f'<p>With the index the query is fast, but <code>SUB_Home_Refresh</code> still retrieves every order completed today (about 1,100 a day at this volume) to count them and average '
      f'their pipeline time in a loop. A view entity (OQL <code>COUNT</code>/<code>AVG</code>, Mendix 10.18+) lets the database return the two numbers — the project\'s own convention for aggregates.</p>'),
    F('F8', 'open', 'By design', '"Place order and pay" takes 3.8 or 5.8 seconds',
      f'<p>The simulated gateway takes 3 seconds (lite-configuration: <code>paymentProcessing</code>), and the payment sheet advances when the simulator\'s next tick and the next 2-second poll '
      f'have both happened, so the step lands on one of two plateaus: before {fmt(pay_b["range"]["browserMs"][0])}–{fmt(pay_b["range"]["browserMs"][1])} ms, after '
      f'{fmt(pay_a["range"]["browserMs"][0])}–{fmt(pay_a["range"]["browserMs"][1])} ms. Its server and database work did not change ({fmt(pay_b["dbMs"])} → {fmt(pay_a["dbMs"])} ms). "Open tracking" '
      f'right after it shows the same two-plateau spread. Neither is a regression.</p>'),
    F('OK', 'ok', 'No change needed', 'Finding a past order stays fast at 400,000 orders',
      f'<p>The lookup by order number and email ({fmt(lk_a["dbMs"])} ms database) and opening an old order\'s tracking link ({fmt(tl_a["dbMs"])} ms) use the unique indexes on '
      f'<code>OrderNumber</code> and <code>TrackingToken</code> that were there from the start; their times are the same as on the 59-order demo data.</p>'),
]

# ---------------------------------------------------------------- statements table
def stmt_rows(rows, n=8):
    out = []
    for r in rows[:n]:
        sql = r['sql']
        where = sql[sql.find(' WHERE '):][:150] if ' WHERE ' in sql else sql[:150]
        table_m = re.search(r'FROM "([^"]+)"', sql) or re.search(r'(?:INTO|UPDATE) "([^"]+)"', sql)
        out.append(f'<tr><td><code>{E(table_m.group(1) if table_m else "")}</code></td><td>{r["calls"]:,}</td><td>{r["total"]:,.1f}</td>'
                   f'<td>{r["mean"]:.2f}</td><td><code class="sql">{E(where)}</code></td></tr>')
    return ''.join(out)


changed = [k for k in ORDER if k in CHANGED]
pairs = ''.join(f'<div class="pair">{figure(B[k], J[k[0]] + " · " + k[1].split(" ", 1)[1] + " (before)")}'
                f'{figure(A[k], J[k[0]] + " · " + k[1].split(" ", 1)[1] + " (after)")}</div>' for k in changed if k[1] in ('2 open menu', '5 add to cart', '3 open configurator'))
alls = ''.join(figure(A[k], J[k[0]] + ' · ' + k[1].split(' ', 1)[1]) for k in ORDER)
vol = ''.join(f'<tr><td>{E(n)}</td><td>{c:,}</td></tr>' for n, c in volume['rows'])

page = f'''<title>GitPizza Load Test</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@700;800&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f6f5f1; --surface: #ffffff; --ink: #1b1b1c; --muted: #5e6066; --line: #dedcd5;
  --brand: #ff9d00; --brand-ink: #2c1700; --code: #131313; --hit: #fff1d9; --good: #127a3a; --bad: #b3261e;
  --c-request: #1b1b1c; --c-microflow: #ff9d00; --c-action: #ffc485; --c-db: #c4373a; --c-label: #ffffff; --c-label-dark: #1b1b1c;
  --f-display: "JetBrains Mono", ui-monospace, monospace; --f-body: "IBM Plex Sans", system-ui, sans-serif; --f-mono: "IBM Plex Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #131313; --surface: #1b1b1c; --ink: #ececec; --muted: #a2a4aa; --line: #2f2f31; --hit: #2c2210; --good: #72ff70; --bad: #ff7a6e;
  --c-request: #9aa0aa; --c-microflow: #ff9d00; --c-action: #b88a4a; --c-db: #e05a5d; --c-label: #131313; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #131313; --surface: #1b1b1c; --ink: #ececec; --muted: #a2a4aa; --line: #2f2f31; --hit: #2c2210; --good: #72ff70; --bad: #ff7a6e;
  --c-request: #9aa0aa; --c-microflow: #ff9d00; --c-action: #b88a4a; --c-db: #e05a5d; --c-label: #131313; color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); margin: 0; padding: 0 16px 64px; }}
.wrap {{ max-width: 1180px; margin: 0 auto; display: grid; gap: 40px; }}
.wrap > *, .findings > *, .pair > *, .kpis > * {{ min-width: 0; }}
header.top {{ border-bottom: 6px solid var(--brand); padding-block: 36px 24px; display: grid; gap: 10px; }}
.eyebrow {{ font: 600 12px/1 var(--f-body); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}
h1 {{ font: 800 clamp(30px, 5vw, 44px)/1.1 var(--f-display); margin: 0; letter-spacing: -.02em; }}
h2 {{ font: 700 24px/1.2 var(--f-display); margin: 0 0 12px; letter-spacing: -.01em; }}
h3 {{ font: 600 18px/1.3 var(--f-body); margin: 0 0 6px; }}
p {{ margin: 0 0 10px; max-width: 72ch; }}
.lede {{ font-size: 17px; max-width: 74ch; }}
code {{ font-family: var(--f-mono); font-size: 12.5px; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
.kpi {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px 18px; display: grid; gap: 6px; align-content: start; }}
.kpi .v {{ font: 600 26px/1.1 var(--f-mono); font-variant-numeric: tabular-nums; }}
.kpi .v s {{ color: var(--muted); font-weight: 400; font-size: 19px; margin-right: 6px; }}
.kpi .l {{ color: var(--muted); font-size: 13.5px; }}
.scroll {{ overflow-x: auto; min-width: 0; }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
thead th {{ font: 600 12px/1.2 var(--f-body); letter-spacing: .04em; text-transform: uppercase; color: var(--muted); border-bottom: 2px solid var(--ink); white-space: nowrap; }}
table.steps td {{ font-family: var(--f-mono); font-size: 13px; white-space: nowrap; }}
table.steps th[scope=row] {{ font-weight: 500; min-width: 240px; }}
.j {{ display: inline-block; font: 600 11px/1 var(--f-mono); background: var(--code); color: var(--brand); padding: 3px 5px; border-radius: 3px; margin-right: 8px; }}
.rng {{ display: block; color: var(--muted); font-size: 11.5px; }}
tr.hit {{ background: var(--hit); }}
td.d {{ font-weight: 600; }}
.findings {{ display: grid; gap: 24px; }}
.finding {{ display: grid; grid-template-columns: 56px 1fr; gap: 16px; }}
.finding .tag {{ font: 700 13px/1 var(--f-mono); padding: 8px 0; text-align: center; border-radius: 4px; height: fit-content; }}
.tag.fixed {{ background: var(--brand); color: var(--brand-ink); }}
.tag.open {{ background: var(--surface); border: 1px solid var(--line); color: var(--muted); }}
.tag.ok {{ background: var(--surface); border: 1px solid var(--good); color: var(--good); }}
.status {{ font: 600 12px/1 var(--f-body); letter-spacing: .05em; text-transform: uppercase; }}
.status.fixed {{ color: var(--good); }} .status.open {{ color: var(--muted); }} .status.ok {{ color: var(--good); }}
.pair {{ display: grid; gap: 14px; }}
.charts {{ display: grid; gap: 18px; }}
figure.fc {{ margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; display: grid; gap: 8px; min-width: 0; }}
figure.fc figcaption {{ display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: baseline; font-size: 13px; }}
figure.fc figcaption span {{ color: var(--muted); font-family: var(--f-mono); font-size: 12px; }}
svg.flame {{ display: block; min-width: 760px; }}
svg.flame text {{ font: 11px var(--f-mono); fill: var(--c-label); pointer-events: none; }}
svg.flame .tick {{ fill: var(--muted); font-size: 10px; }}
svg.flame .grid {{ stroke: var(--line); stroke-width: 1; }}
svg.flame .sp rect {{ stroke: var(--surface); stroke-width: .5; }}
svg.flame .request rect {{ fill: var(--c-request); }}
svg.flame .microflow rect {{ fill: var(--c-microflow); }} svg.flame .microflow text {{ fill: var(--c-label-dark); }}
svg.flame .action rect {{ fill: var(--c-action); }} svg.flame .action text {{ fill: var(--c-label-dark); }}
svg.flame .db rect {{ fill: var(--c-db); }}
svg.flame .sp:hover rect {{ opacity: .8; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 13px; color: var(--muted); }}
.legend i {{ display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; }}
code.sql {{ white-space: normal; word-break: break-all; color: var(--muted); }}
.cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }}
ul {{ margin: 0; padding-left: 20px; max-width: 72ch; }} li {{ margin-bottom: 6px; }}
.muted {{ color: var(--muted); }}
</style>
<div class="wrap">
<header class="top">
  <span class="eyebrow">GitPizza · performance under load · 19 November 2026</span>
  <h1>GitPizza Load Test</h1>
  <p class="lede">Two guest journeys measured against a year of a busy store: {orders:,} orders and about ten million rows. Each step ran six times; figures are medians of the five
  warm runs, before and after the fixes this test led to, counting only the guest's own requests (the simulator's background clock is left out).</p>
</header>

<section class="kpis">{''.join(f'<div class="kpi"><span class="v">{v}</span><span class="l">{l}</span></div>' for v, l in kpis)}</section>

<section>
  <h2>Every step, before and after</h2>
  <p>Browser time runs from the click until the last request it set off has answered (with the median's min–max underneath). Server time is the sum of the guest's request spans,
  database time the sum of their JDBC spans. Highlighted rows are the steps the fixes target. The others did not change: their Δ is run-to-run spread on this
  machine — "place order and pay" and "open tracking" land on one of two plateaus set by the simulator's tick (F8), and the 2-second live poller can fall inside a short
  step's window. Server and database time are the steadier measure there.</p>
  <div class="scroll"><table class="steps"><thead><tr><th>Journey · step</th><th>Before, ms</th><th>After, ms</th><th>Δ</th><th>Server ms</th><th>Database ms</th><th>Queries</th></tr></thead>
  <tbody>{table}</tbody></table></div>
</section>

<section>
  <h2>Findings</h2>
  <div class="findings">{''.join(findings)}</div>
</section>

<section class="charts">
  <h2>Flame charts</h2>
  <p>Time runs left to right from the click; each guest request is its own band, with its microflows, activities and database statements stacked underneath. Hover a bar for the
  full name or SQL. A comb of thin red bars is a query per row.</p>
  <div class="legend"><span><i style="background:var(--c-request)"></i>request</span><span><i style="background:var(--c-microflow)"></i>microflow</span>
  <span><i style="background:var(--c-action)"></i>activity</span><span><i style="background:var(--c-db)"></i>database</span></div>
  <h3>The steps that changed</h3>
  {pairs}
  <h3 style="margin-top:12px">All steps, after</h3>
  {alls}
</section>

<section class="cols">
  <div><h2>Database statements</h2>
  <p>The most expensive statements over each whole run (pg_stat_statements: the journeys plus the simulator in the background).</p>
  <h3>Before</h3><div class="scroll"><table><thead><tr><th>Table</th><th>Calls</th><th>Total ms</th><th>Mean ms</th><th>Filter</th></tr></thead><tbody>{stmt_rows(SB)}</tbody></table></div>
  <h3 style="margin-top:16px">After</h3><div class="scroll"><table><thead><tr><th>Table</th><th>Calls</th><th>Total ms</th><th>Mean ms</th><th>Filter</th></tr></thead><tbody>{stmt_rows(SA)}</tbody></table></div></div>
</section>

<section class="cols">
  <div><h2>Data volume</h2><p>{E(volume["note"])}</p>
  <table><thead><tr><th>Table</th><th>Rows</th></tr></thead><tbody>{vol}</tbody></table></div>
  <div><h2>How it was measured</h2>
  <ul>
   <li>Seed: <code>docs/perf/tools/seed.sql</code> (direct SQL with the runtime's id formula, dates relative to now); backup taken first and restored afterwards.</li>
   <li>Postgres 16 with <code>pg_stat_statements</code> and <code>auto_explain</code> (20 ms) for the runs, then reset; the app on the local runtime with OpenTelemetry to an OTLP collector.</li>
   <li><code>tests/perf/journeys.js</code>: "Guest orders a pizza" (9 steps) and "Guest finds a past order" (3 steps on seeded order MX-200000), six runs each, run 0 is warm-up.
   A step ends when no request has started for 0.6 s.</li>
   <li>"Before" is the committed model on the seed, "after" the fixed model on the same seed, both from a fresh start. <code>docs/perf/tools/analyse.py</code> keeps only traces
   rooted in a guest request on the app port; <code>mxcli report performance</code>'s own JSON is kept next to it (<code>*-raw.json</code>).</li>
   <li>F1 was observed on the first run of the committed model with a year of simulation events; the "after" drain ran the journeys while the same backlog was being removed.</li>
  </ul>
  <h3 style="margin-top:16px">Limits</h3>
  <ul>
   <li>One machine, one guest at a time: no concurrency or contention beyond the simulator.</li>
   <li>The page's 2-second live poller can land inside a step window and add up to ~200 ms of browser time; compare server and database time for small steps.</li>
   <li>The seed is uniform: every order is a finished guest order, ~1,100 a day. Real traffic has peaks and more open orders.</li>
   <li>Payment is simulated (3 s by design), so "place order and pay" says little about real gateway latency.</li>
  </ul></div>
</section>
</div>
'''

open(OUT, 'w').write(page)
print(f'wrote {os.path.relpath(OUT)} ({os.path.getsize(OUT) // 1024} KB)')
