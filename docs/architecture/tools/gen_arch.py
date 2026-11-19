#!/usr/bin/env python3
"""Architecture report (HTML) from docs/architecture/arch.json.

    python3 docs/architecture/tools/collect.py && python3 docs/architecture/tools/gen_arch.py

Every number comes from arch.json: mxcli's architecture report (layers, cohesion, edges,
communities, god nodes, bridges, hotspots, unused) plus catalog counts and the module edges
without the generated seed flows. Placement (ROWS), cluster names, module roles and the prose
are written here by hand from that data; an assert stops the build when a module changes layer.
"""
import html
import sys as _sys
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from report_fonts import font_face_css  # noqa: E402
FONT_FACES = font_face_css()
from report_kit import nav as _nav  # noqa: E402
NAV = _nav('architecture')
d = json.load(open(os.path.join(HERE, '..', 'arch.json')))
OUT = os.path.join(HERE, '..', 'report.html')
E = html.escape
R = d['report']['data']
C = d['counts']
M = {m['name']: m for m in R['modules']}
ORDER = ['Simulation', 'Shop', 'Fulfilment', 'Catalog', 'Core']
ROWS = {3: ['Simulation'], 2: ['Shop'], 1: ['Fulfilment'], 0: ['Catalog', 'Core']}
for lay, ms in ROWS.items():
    for m in ms:
        assert M[m]['layer'] == lay, f'{m} moved to layer {M[m]["layer"]}: update ROWS'
assert sorted(ORDER) == sorted(M), 'every app module placed once'
COLOR = {'Simulation': '--s1', 'Shop': '--s2', 'Fulfilment': '--s3', 'Catalog': '--s4', 'Core': '--s5'}


def n(table, m):
    return C[table].get(m, 0)


# cohesion without the generated seed flows (catalog references by source module)
cat = {(e['from'], e['to']): e['refs'] for e in d['catalogEdges']['withoutSeed']}
cat_all = {(e['from'], e['to']): e['refs'] for e in d['catalogEdges']['withSeed']}


def cohesion_noseed(m):
    inside = cat.get((m, m), 0)
    out = sum(v for (a, b), v in cat.items() if a == m and b != m)
    return round(100 * inside / (inside + out)) if inside + out else 100


def band(p):
    return 'low' if p < 40 else 'mid' if p < 70 else 'high'


edges = sorted(R['domainEdges'], key=lambda e: -e['refs'])
edge_noseed = {(a, b): v for (a, b), v in cat.items() if a != b}

# ---------------------------------------------------------------- 1. module map
W, H = 1000, 590
BW, BH = 270, 70
Y = {3: 60, 2: 205, 1: 350, 0: 510}
X = {'Simulation': 500, 'Shop': 290, 'Fulfilment': 710, 'Catalog': 290, 'Core': 710}
# skip-level edges that would cross a box go round the outside: (start dx, control x, end dx)
ROUTE = {('Simulation', 'Catalog'): (-120, 60, -70), ('Simulation', 'Core'): (120, 940, 70)}
mx = max(e['refs'] for e in edges)


def bez(p0, p1, p2, p3, t):
    return tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * dd for a, b, c, dd in zip(p0, p1, p2, p3))


paths, labels = [], []
for e in edges:
    a, b = e['from'], e['to']
    y1, y2 = Y[M[a]['layer']] + BH / 2, Y[M[b]['layer']] - BH / 2
    if (a, b) in ROUTE:
        dx0, cx, dx1 = ROUTE[(a, b)]
        x1, x2 = X[a] + dx0, X[b] + dx1
        c1, c2 = (cx, y1 + 30), (cx, y2 - 70)
    else:
        x1 = X[a] + (X[b] - X[a]) * 0.2
        x2 = X[b] - (X[b] - X[a]) * 0.15
        c1, c2 = (x1, y1 + (y2 - y1) * 0.45), (x2, y1 + (y2 - y1) * 0.55)
    w = 1 + math.log10(e['refs'] + 1) * 1.7
    ns = edge_noseed.get((a, b))
    kinds = ', '.join(e['kinds'][:8])
    tip = f'{a} → {b}: {e["refs"]:,} references' + (f' ({ns:,} without the seed flows)' if ns is not None and ns != e['refs'] else '') + f'\nkinds: {kinds}\ne.g. ' + '\n'.join(e['samples'][:3])
    seedy = ns is not None and ns < e['refs'] * 0.2
    paths.append(f'<path class="e{" seed" if seedy else ""}" d="M{x1:.0f},{y1:.0f} C{c1[0]:.0f},{c1[1]:.0f} {c2[0]:.0f},{c2[1]:.0f} {x2:.0f},{y2:.0f}" '
                 f'stroke-width="{w:.1f}" marker-end="url(#ah)"><title>{E(tip)}</title></path>')
    mxp, myp = bez((x1, y1), c1, c2, (x2, y2), 0.5)
    txt = f'{e["refs"]:,}' + (f' · {ns:,} w/o seed' if seedy else '')
    labels.append(f'<g class="el"><rect x="{mxp - len(txt) * 3.4 - 6:.0f}" y="{myp - 9:.0f}" width="{len(txt) * 6.8 + 12:.0f}" height="18" rx="9"/>'
                  f'<text x="{mxp:.0f}" y="{myp + 4:.0f}">{E(txt)}</text></g>')

nodes = []
for m in ORDER:
    mm = M[m]
    x, y = X[m], Y[mm['layer']]
    p = mm['cohesion']
    mf, seed = n('microflows', m), n('seedMicroflows', m)
    mf_txt = f'{mf - seed} mf + {seed} seed' if seed else f'{mf} mf'
    ui = n('pages', m) + n('snippets', m)
    ns = cohesion_noseed(m)
    coh = f'cohesion {p:.0f}%' + (f' ({ns}% w/o seed)' if seed else '')
    tip = f'{m} · layer {mm["layer"]}\n{mm.get("purpose", "")}\n{mf} microflows ({seed} generated seed), {n("pages", m)} pages, {n("snippets", m)} snippets, {n("entities", m)} entities, {n("viewModels", m)} view models\nuses: {mm["fanOut"]} modules · used by: {mm["fanIn"]}'
    nodes.append(f'<g class="n {band(ns if seed else p)}"><title>{E(tip)}</title>'
                 f'<rect x="{x - BW / 2}" y="{y - BH / 2}" width="{BW}" height="{BH}" rx="7"/>'
                 f'<rect class="sw" x="{x - BW / 2}" y="{y - BH / 2}" width="6" height="{BH}" rx="3" style="fill:var({COLOR[m]})"/>'
                 f'<text x="{x}" y="{y - 12}" class="nm">{E(m)}</text>'
                 f'<text x="{x}" y="{y + 6}" class="sub">{E(mf_txt)}{f" · {ui} pg" if ui else ""} · {n("entities", m)} ent</text>'
                 f'<text x="{x}" y="{y + 22}" class="sub">{E(coh)}</text></g>')
lay = ''.join(f'<text x="14" y="{Y[l] + 4}" class="lay">layer {l}</text><line x1="70" x2="{W - 20}" y1="{Y[l] + BH / 2 + 22}" y2="{Y[l] + BH / 2 + 22}" class="lg"/>' for l in (3, 2, 1))
module_map = (f'<svg class="map" viewBox="0 0 {W} {H}" role="img" aria-label="Layered module map"><defs>'
              f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mk"/></marker></defs>'
              f'{lay}<text x="14" y="{Y[0] + 4}" class="lay">layer 0</text>{"".join(paths)}{"".join(nodes)}{"".join(labels)}</svg>')

# ---------------------------------------------------------------- 2. module health
ROLE = {
    'Simulation': 'Plays everyone the guest never sees: payment gateway, kitchen, ovens, couriers, other customers, and the demo reset. 186 of its 204 microflows are the seed generated from 09-demo-data, which is why it looks like one big outward arrow.',
    'Shop': 'The storefront: pages, guest session, cart and checkout. Also holds three rules the simulator borrows (payment decision, line pricing, order placement) — see recommendations.',
    'Fulfilment': 'The order domain without UI: orders, lines, payments, status history, log, couriers, ovens, zones, coupons, pricing and the order transitions. Almost everything it does stays inside it.',
    'Catalog': 'The menu data: products, sizes, options, recipes, ingredients, allergens. Depends on nothing; read by every module above it.',
    'Core': 'Settings, toasts and the formatting helpers (money, mm:ss, phone, ids). Depends on nothing.',
}
rows = []
for m in ORDER:
    mm = M[m]
    p = mm['cohesion']
    seed = n('seedMicroflows', m)
    ns = cohesion_noseed(m)
    lab = lambda v: f'left:calc({v:.0f}% + 6px)' if v < 30 else 'left:6px'
    bar = f'<div class="bar {band(p)}"><i style="width:{max(p, 1):.0f}%"></i><span style="{lab(p)}">{p:.0f}%</span></div>'
    if seed:
        bar += f'<div class="bar {band(ns)} thin"><i style="width:{ns}%"></i><span style="{lab(ns)}">{ns}% w/o seed</span></div>'
    rows.append(f'<tr><th scope="row"><i class="dot" style="background:var({COLOR[m]})"></i>{E(m)}</th><td class="num">{mm["layer"]}</td><td>{bar}</td>'
                f'<td class="num">{mm["internal"]:,}</td><td class="num">{mm["externalOut"]:,}</td><td class="num">{mm["externalIn"]:,}</td>'
                f'<td class="num">{n("entities", m)} + {n("viewModels", m)}</td><td class="num">{n("microflows", m) - seed}{f" + {seed}" if seed else ""}</td>'
                f'<td class="num">{n("pages", m)} + {n("snippets", m)}</td><td class="num">{mm["fanIn"]}</td><td class="num">{mm["fanOut"]}</td><td class="note">{E(ROLE[m])}</td></tr>')
health = ('<table class="mods"><thead><tr><th>Module</th><th>Layer</th><th>Cohesion</th><th>Internal</th><th>Out</th><th>In</th>'
          '<th>Entities + view models</th><th>Microflows (+ seed)</th><th>Pages + snippets</th><th>Used by</th><th>Uses</th><th>Role</th></tr></thead>'
          f'<tbody>{"".join(rows)}</tbody></table>')

# ---------------------------------------------------------------- 3. coupling matrix
dm = {(e['from'], e['to']): e['refs'] for e in R['domainEdges']}
mxl = math.log(max(dm.values()) + 1)
head = ''.join(f'<th class="vh"><span>{E(m)}</span></th>' for m in ORDER)
body = []
for a in ORDER:
    tds = []
    for b in ORDER:
        if a == b:
            tds.append(f'<td class="self">{M[a]["internal"]:,}</td>')
            continue
        v = dm.get((a, b), 0)
        if not v:
            tds.append('<td></td>')
            continue
        ns = edge_noseed.get((a, b))
        sub = f'<span class="rng">{ns:,} w/o seed</span>' if ns is not None and ns != v and a == 'Simulation' else ''
        tds.append(f'<td class="h" style="--t:{math.log(v + 1) / mxl:.2f}" title="{E(a)} → {E(b)}: {v:,}">{v:,}{sub}</td>')
    body.append(f'<tr><th scope="row">{E(a)}</th>{"".join(tds)}</tr>')
matrix = f'<table class="mx"><thead><tr><th>uses →</th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'

# ---------------------------------------------------------------- 4. clusters
CLUSTER = {
    'Shop · CartLine': ('Configure, cart and checkout', 'The guest\'s order being built: configurator tiles, cart lines, checkout form, pricing and toasts. A real bounded context; it borrows catalog reads and the money helper.'),
    'Simulation · Order': ('The simulator engine', 'Ticks, payments, kitchen, couriers and traffic acting on Fulfilment\'s orders, ovens and zones. Spans Simulation and Fulfilment by design: the simulator stands in for staff and outside systems.'),
    'Simulation · Product': ('Seed: order lines', 'Generated seed flows that create the demo orders\' lines. Not a design decision — one cluster per kind of generated row.'),
    'Shop · TrackView': ('Tracking and lookup', 'Confirmation, live tracking, order lookup and the session grant (OrderAccess). Reads the simulation settings for the ETA.'),
    'Simulation · OrderStatusChange': ('Seed: status history', 'Generated seed flows for the demo orders\' history.'),
    'Shop · Cart': ('Shell, home and menu', 'The guest\'s cart as the page context: menu filters, home carousel and the header. The cart doubles as view state because a microflow-fed list refreshes only on a committed object.'),
    'Simulation · OrderLogEntry': ('Seed: order log', 'Generated seed flows for the demo orders\' log lines.'),
    'Catalog': ('Catalog', 'Products, options, ingredients and allergens, with the storefront\'s menu flows that read them.'),
    'Shop · ErrorView': ('Error pages', 'SCR-41 and its fault probe.'),
}
mod_order = {m: i for i, m in enumerate(ORDER)}
crow = []
for c in R['communities']:
    name, note = CLUSTER.get(c['label'], (c['label'], ''))
    segs = ''.join(f'<i style="flex:{x["count"]};background:var({COLOR.get(x["module"], "--muted")})" title="{E(x["module"])}: {x["count"]}"></i>'
                   for x in sorted(c['modules'], key=lambda x: mod_order.get(x['module'], 9)))
    split = ', '.join(f'{x["module"]} {x["count"]}' for x in c['modules'])
    crow.append(f'<tr><th scope="row">{E(name)}<span class="rng">{E(c["label"])}</span></th><td class="num">{c["size"]}</td>'
                f'<td><div class="stack">{segs}</div><span class="rng">{E(split)}</span></td><td class="note">{E(note)}</td></tr>')
clusters = ('<table class="cl"><thead><tr><th>Cluster</th><th>Size</th><th>Modules</th><th>What it is</th></tr></thead>'
            f'<tbody>{"".join(crow)}</tbody></table>')
legend = ''.join(f'<span><i class="dot" style="background:var({COLOR[m]})"></i>{m}</span>' for m in ORDER)


def tbl(rows, cols):
    return ('<table><thead><tr>' + ''.join(f'<th>{c}</th>' for c in cols) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{v}</td>' for v in r) + '</tr>' for r in rows) + '</tbody></table>')


god = tbl([(f'<code>{E(g["name"])}</code>', g['type'].lower(), f'{g["in"]:,}', f'{g["out"]:,}') for g in R['godNodes'][:8]], ['Element', 'Kind', 'In', 'Out'])
bridges = tbl([(f'<code>{E(g["name"])}</code>', f'{g["betweenness"]:,.0f}', g['in'], g['out']) for g in R['bridges'][:8]], ['Microflow', 'Betweenness', 'Callers', 'Calls'])
hot = tbl([(f'<code>{E(h["entity"])}</code>', h['flows'], E(h['modules'].replace(',', ', '))) for h in R['hotspots'][:8]], ['Entity', 'Flows', 'Modules'])
VERDICT = {
    'Shop.ACT_Track_Token': ('used', 'Entry point of the tracking link <code>/p/track/{token}</code>: a microflow with a URL, which the graph does not count as a caller.'),
    'Shop.FaultProbe': ('used', 'Opened by URL <code>/p/fault</code> for the US-282 acceptance test (opt-in constant <code>Shop.FaultInjection</code>).'),
    'Shop.UnexpectedError': ('used', 'Opened by the client error hook (<code>JS_LivePoller</code>) instead of the platform dialog, and by URL <code>/p/error</code>.'),
    'Shop.DS_Product_Recipe': ('unused', 'No longer used since performance fix F4 stored the toppings on the product; kept because requirement US-026 is anchored on it. Re-anchor, then delete.'),
}
unused = tbl([(f'<code>{E(u["name"])}</code>', u['type'].lower(), f'<b class="{VERDICT.get(u["name"], ("?",))[0]}">{VERDICT.get(u["name"], ("check",))[0]}</b>',
               VERDICT.get(u['name'], ('', 'Not reviewed.'))[1]) for u in R['unused']], ['Document', 'Kind', 'Verdict', 'Why'])
outside = ', '.join(f'{o["from"]} → {o["to"]} ({o["refs"]})' for o in R['outsideEdges'])
sim_shop = d['simulationToShop']
calls = sorted({x['TargetName'] for x in sim_shop if x['RefKind'] == 'call'})
real_unused = sum(1 for u in R['unused'] if VERDICT.get(u['name'], ('',))[0] == 'unused')
seed_total, mf_total = n('seedMicroflows', 'Simulation'), sum(n('microflows', m) for m in ORDER)
layers = len({M[m]['layer'] for m in ORDER})
top_hot = R['hotspots'][0]

kpis = [
    (f'{layers} layers · {len(R["cycles"] or [])} cycles', 'Every dependency between the five app modules points down, Simulation → Shop → Fulfilment → Catalog and Core; no cycle, with or without navigation.'),
    (f'{seed_total} of {mf_total}', f'App microflows are the generated seed (<code>Simulation.SEED_*</code>). They create {d["report"]["data"]["domainEdges"][0]["refs"]:,} of the references into Fulfilment and dominate the graph.'),
    (f'{top_hot["flows"]} flows', f'Touch <code>{E(top_hot["entity"])}</code>, in {len(top_hot["modules"].split(","))} modules: the app\'s centre of gravity, and the one entity whose attributes are expensive to change.'),
    (f'{real_unused} of {len(R["unused"])}', '"Unused" documents really are unused; the others are reached by URL or a client hook, which the graph does not see.'),
]

recs = [
    '<b>Move the payment decision into Fulfilment.</b> <code>Shop.SUB_Payment_Resolve</code> decides an attempt\'s outcome and performs T-02/T-03/T-04 on Fulfilment\'s order and attempt; the simulator calls it from above the storefront. In Fulfilment it sits next to <code>SUB_Payment_Retry</code> and the transitions, and Simulation no longer needs Shop for payments.',
    '<b>Give order placement and line pricing a home below the storefront.</b> The traffic generator builds a <code>Shop.CartLine</code> and calls <code>SUB_Line_ApplyDefaults</code>, <code>SUB_Line_Recalculate</code> and <code>SUB_Order_Place</code> to create a simulated order the same way a guest does. That reuse is right — one pricing path — but it makes the simulator depend on the storefront\'s cart. A Fulfilment-level "place order from lines" with the pricing rules (BR-PRICE-02…04) lets both callers use it; the cart then only collects choices.',
    f'<b>Keep the seed out of the architecture.</b> {seed_total} generated flows turn Simulation into a 2.8 %-cohesion module and fill the god-node list (<code>SEED_Catalog</code> with {R["godNodes"][1]["out"]:,} outgoing references). Moving them to their own module (e.g. <code>DemoData</code>, layer 3) would leave Simulation\'s own 18 flows to be judged on their own and makes the next report readable without the "w/o seed" column.',
    f'<b>Watch the two bridges.</b> <code>Shop.SUB_Line_Recalculate</code> and <code>Shop.SUB_Cart_Recalculate</code> carry most shortest paths in the graph: configurator, cart, checkout and the traffic generator all run through them. They are also the open performance finding F6 (every line recalculated 2–4 times per add); changes there need the pricing tests (<code>tests/pricing.test.mdl</code>) and journeys J2, J9 and J11.',
    f'<b>Treat <code>Fulfilment.Order</code> as a published contract.</b> {top_hot["flows"]} flows in three modules read and write it directly. Additive changes are cheap; renaming or retyping an attribute is not.',
    '<b>Delete <code>Shop.DS_Product_Recipe</code></b> after re-anchoring requirement US-026 on <code>Shop.SUB_Product_Recalculate</code>.',
]

page = f'''<title>GitPizza Architecture</title>
<style>
{FONT_FACES}
:root {{
  --bg: #f6f5f1; --surface: #ffffff; --ink: #1b1b1c; --muted: #5e6066; --line: #dedcd5; --brand: #ff9d00; --code: #131313;
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4;
  --high-bg: #e6f4ec; --high-bd: #1f7a4a; --mid-bg: #fdf3dc; --mid-bd: #b7860b; --low-bg: #fbe7e6; --low-bd: #b3261e;
  --edge: #8d8f96; --edge-seed: #c9c6bd; --heat: 32, 120, 214;
  --f-display: "JetBrains Mono", ui-monospace, monospace; --f-body: "Geist", system-ui, sans-serif; --f-mono: "JetBrains Mono", ui-monospace, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #131313; --surface: #1b1b1c; --ink: #ececec; --muted: #a2a4aa; --line: #2f2f31; color-scheme: dark;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181;
  --high-bg: #15291e; --high-bd: #5cc98e; --mid-bg: #2d2510; --mid-bd: #e0b54a; --low-bg: #321615; --low-bd: #f07575; --edge: #8b8e96; --edge-seed: #44464b; --heat: 57, 135, 229 }} }}
:root[data-theme="dark"] {{
  --bg: #131313; --surface: #1b1b1c; --ink: #ececec; --muted: #a2a4aa; --line: #2f2f31; color-scheme: dark;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181;
  --high-bg: #15291e; --high-bd: #5cc98e; --mid-bg: #2d2510; --mid-bd: #e0b54a; --low-bg: #321615; --low-bd: #f07575; --edge: #8b8e96; --edge-seed: #44464b; --heat: 57, 135, 229 }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); margin: 0; padding: 0 16px 64px; }}
.wrap {{ max-width: 1180px; margin: 0 auto; display: grid; gap: 40px; }}
.wrap > *, .kpis > *, .cols > * {{ min-width: 0; }}
header.top {{ border-bottom: 6px solid var(--brand); padding-block: 36px 24px; display: grid; gap: 10px; }}
nav.reports {{ display: flex; flex-wrap: wrap; gap: 4px 14px; font: 500 13px var(--f-body); }}
nav.reports a {{ color: var(--muted); text-decoration: none; }} nav.reports a[aria-current] {{ color: var(--ink); font-weight: 600; }}
.eyebrow {{ font: 600 12px/1 var(--f-body); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}
h1 {{ font: 700 clamp(30px, 5vw, 44px)/1.1 var(--f-display); margin: 0; letter-spacing: -.02em; }}
h2 {{ font: 700 24px/1.2 var(--f-display); margin: 0 0 12px; letter-spacing: -.01em; }}
h3 {{ font: 600 17px/1.3 var(--f-body); margin: 0 0 6px; }}
p {{ margin: 0 0 10px; max-width: 74ch; }}
.lede {{ font-size: 17px; max-width: 76ch; }}
code {{ font-family: var(--f-mono); font-size: 12.5px; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
.kpi {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px 18px; display: grid; gap: 6px; align-content: start; }}
.kpi .v {{ font: 600 26px/1.1 var(--f-mono); }}
.kpi .l {{ color: var(--muted); font-size: 13.5px; }}
.panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px; overflow-x: auto; }}
svg.map {{ display: block; width: 100%; min-width: 760px; }}
svg.map .lay {{ font: 600 11px var(--f-mono); fill: var(--muted); }}
svg.map .lg {{ stroke: var(--line); stroke-dasharray: 3 5; }}
svg.map .e {{ fill: none; stroke: var(--edge); opacity: .9; }}
svg.map .e.seed {{ stroke: var(--edge-seed); }}
svg.map .e:hover {{ stroke: var(--brand); opacity: 1; }}
svg.map .mk {{ fill: var(--edge); }}
svg.map .n rect {{ stroke-width: 1.5; }}
svg.map .n.high rect:first-of-type {{ fill: var(--high-bg); stroke: var(--high-bd); }}
svg.map .n.mid rect:first-of-type {{ fill: var(--mid-bg); stroke: var(--mid-bd); }}
svg.map .n.low rect:first-of-type {{ fill: var(--low-bg); stroke: var(--low-bd); }}
svg.map .nm {{ font: 600 15px var(--f-body); fill: var(--ink); text-anchor: middle; }}
svg.map .sub {{ font: 11px var(--f-mono); fill: var(--muted); text-anchor: middle; }}
svg.map .el rect {{ fill: var(--surface); stroke: var(--line); }}
svg.map .el text {{ font: 10.5px var(--f-mono); fill: var(--ink); text-anchor: middle; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 13px; color: var(--muted); margin-top: 8px; }}
.legend i {{ display: inline-block; width: 14px; height: 10px; border-radius: 2px; margin-right: 6px; vertical-align: 0; border: 1.5px solid; }}
.legend .l1 {{ background: var(--high-bg); border-color: var(--high-bd); }} .legend .l2 {{ background: var(--mid-bg); border-color: var(--mid-bd); }} .legend .l3 {{ background: var(--low-bg); border-color: var(--low-bd); }}
.legend .ln {{ height: 0; border: 0; border-top: 3px solid var(--edge); width: 18px; }} .legend .ls {{ height: 0; border: 0; border-top: 3px solid var(--edge-seed); width: 18px; }}
i.dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; vertical-align: 0; }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }}
thead th {{ font: 600 12px/1.2 var(--f-body); letter-spacing: .04em; text-transform: uppercase; color: var(--muted); border-bottom: 2px solid var(--ink); }}
td.num {{ font-family: var(--f-mono); font-size: 13px; white-space: nowrap; }}
td.note {{ color: var(--muted); font-size: 13.5px; min-width: 260px; }}
.rng {{ display: block; color: var(--muted); font: 11.5px var(--f-mono); }}
.bar {{ position: relative; width: 150px; height: 18px; background: var(--bg); border-radius: 3px; overflow: hidden; }}
.bar.thin {{ height: 14px; margin-top: 4px; }}
.bar i {{ position: absolute; inset: 0 auto 0 0; border-radius: 3px 0 0 3px; }}
.bar.high i {{ background: var(--high-bd); }} .bar.mid i {{ background: var(--mid-bd); }} .bar.low i {{ background: var(--low-bd); }}
.bar span {{ position: absolute; left: 6px; top: 0; font: 600 11.5px/18px var(--f-mono); color: var(--ink); mix-blend-mode: normal; }}
.bar.thin span {{ line-height: 14px; font-size: 10.5px; }}
table.mx {{ width: auto; }}
table.mx td {{ font: 13px var(--f-mono); text-align: right; min-width: 92px; }}
table.mx td.h {{ background: rgba(var(--heat), calc(.12 + var(--t) * .75)); color: var(--ink); }}
table.mx td.self {{ color: var(--muted); background: repeating-linear-gradient(135deg, transparent 0 6px, var(--line) 6px 7px); }}
.stack {{ display: flex; height: 16px; width: 260px; border-radius: 3px; overflow: hidden; gap: 2px; background: var(--surface); }}
.stack i {{ display: block; height: 100%; }}
b.used {{ color: var(--high-bd); }} b.unused {{ color: var(--low-bd); }}
.cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(330px, 100%), 1fr)); gap: 24px; }}
.cols.wide {{ grid-template-columns: repeat(auto-fit, minmax(min(380px, 100%), 1fr)); }}
.cols.wide td, .cols.wide th {{ font-size: 13px; padding: 6px 8px; }}
ul.recs {{ display: grid; gap: 10px; padding-left: 20px; max-width: 80ch; margin: 0; }}
.scroll {{ overflow-x: auto; }}
</style>
<div class="wrap">
<header class="top">
  {NAV}
  <span class="eyebrow">GitPizza · architecture views from the model graph · 19 November 2026</span>
  <h1>GitPizza Architecture</h1>
  <p class="lede">How the app's five modules depend on one another, where the bounded contexts really lie, which elements everything hangs on, and what to change. Every figure
  comes from <code>mxcli report architecture</code> and the mxcli catalog, read from the model itself; the generated demo-data seed is shown separately because it distorts the picture.</p>
</header>

<section class="kpis">{''.join(f'<div class="kpi"><span class="v">{v}</span><span class="l">{l}</span></div>' for v, l in kpis)}</section>

<section>
  <h2>Module map</h2>
  <p>Each module sits on the layer its domain dependencies put it on. Arrows point from the user to the used module, thicker for more references; the label is the count.
  Pale arrows are carried almost entirely by the generated seed flows, with the count without them next to it. A box gives hand-written microflows (+ generated seed),
  pages and snippets, persistent entities, and cohesion: the share of a module's references that stay inside it. Hover a box or an arrow for details.</p>
  <div class="panel">{module_map}
  <div class="legend"><span><i class="l1"></i>cohesion ≥ 70 %</span><span><i class="l2"></i>40–70 %</span><span><i class="l3"></i>&lt; 40 %</span>
  <span><i class="ln"></i>depends on</span><span><i class="ls"></i>mostly seed flows</span></div></div>
</section>

<section>
  <h2>Module health</h2>
  <p>Fulfilment, Catalog and Core are close to self-contained (95–100 %). Shop's 60 % is a storefront's normal share: it reads the catalog and calls the order domain.
  Simulation is the outlier twice over — its cohesion is {M["Simulation"]["cohesion"]:.1f} % because the seed creates every catalog row and demo order from there, and still
  {cohesion_noseed("Simulation")} % without it, because the simulator's job is to act on Fulfilment's orders.</p>
  <div class="scroll">{health}</div>
</section>

<section class="cols">
  <div><h2>Coupling matrix</h2>
  <p>Rows use columns, highest layer first. A layered design fills only the triangle above the diagonal — as here: nothing below it. The diagonal is each module's internal references.</p>
  <div class="scroll">{matrix}</div></div>
  <div><h2>Outside the app</h2>
  <p>Only the System module is used from the app modules ({E(outside)}): the guest user and session for carts, toasts and the session grant. No Marketplace module is
  called from app code; Atlas provides layouts, DataWidgets the data widgets.</p>
  <h2 style="margin-top:20px">Cycles</h2>
  <p>None between app modules, with or without navigation references. The module split (Simulation → Shop → Fulfilment → Catalog + Core) removed the one
  Fulfilment ↔ Shop cycle the single module had.</p></div>
</section>

<section>
  <h2>Bounded contexts</h2>
  <p>Clusters of elements that reference each other more than the rest (the catalog's community detection), coloured by the module each element lives in.
  Four are real contexts of the shop; three are generated seed, one cluster per kind of generated row; {R["smallCommunities"]} small ones are left out.</p>
  <div class="legend">{legend}</div>
  <div class="scroll">{clusters}</div>
</section>

<section class="cols wide">
  <div><h3>God nodes</h3><p class="note">Most-referenced elements. The order history entities top the list because the seed writes thousands of rows into them; among
  hand-written code, <code>Fulfilment.Order</code> is the centre.</p><div class="scroll">{god}</div></div>
  <div><h3>Bridges</h3><p class="note">Microflows on the most shortest paths between others: pricing and cart recalculation connect configurator, cart, checkout and the
  traffic generator.</p><div class="scroll">{bridges}</div></div>
  <div><h3>Entity hotspots</h3><p class="note">Entities read or written by the most microflows, and from how many modules.</p><div class="scroll">{hot}</div></div>
</section>

<section>
  <h2>Unused documents</h2>
  <p>What the graph finds with no caller, checked by hand.</p>
  <div class="scroll">{unused}</div>
</section>

<section>
  <h2>Recommendations</h2>
  <p>The simulator calls into the storefront in {len(calls)} places ({", ".join(f"<code>{E(c)}</code>" for c in calls)}): that is where the layering bends, and where the first two changes go.</p>
  <ul class="recs">{''.join(f'<li>{r}</li>' for r in recs)}</ul>
</section>

<section class="cols">
  <div><h2>How this was made</h2>
  <p><code>mxcli report architecture --format json</code> (layers, cohesion, domain edges, communities, god nodes, bridges, hotspots, unused) and catalog queries for
  document counts and module edges without <code>Simulation.SEED_*</code>, in <code>docs/architecture/arch.json</code>
  (<code>tools/collect.py</code>); this page is rendered by <code>tools/gen_arch.py</code>. Cluster names, module roles, verdicts and recommendations are written by hand from that data.</p></div>
  <div><h2>Limits</h2>
  <p>References are counted from the model, not weighted by how often they run. Microflows reached only by URL, a JavaScript hook or a Java action count as unused.
  The "without seed" figures count catalog references by source module, which differs slightly from the report's own reference kinds.</p></div>
</section>
</div>
'''
open(OUT, 'w').write(page)
print(f'wrote {os.path.relpath(OUT)} ({os.path.getsize(OUT) // 1024} KB)')
