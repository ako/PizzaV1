#!/usr/bin/env python3
"""Build docs/reports/index.html: one overview page over the mxcli reports.

    python3 tools/reports_index.py

Reads the reports' own JSON (docs/reports/raw/*.json, written with --format json)
and the triage annotations, so every number on the page is the report's number.
Charts are inline SVG + a small hover layer: no libraries, no network.
Colours follow the dataviz reference palette (validated: slots 1-2 pass CVD and
normal-vision checks in light and dark mode).
"""
import html
import json
import math
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
REP = os.path.join(ROOT, 'docs', 'reports')
RAW = os.path.join(REP, 'raw')


def load(name):
    return json.load(open(os.path.join(RAW, name + '.json'), encoding='utf-8'))


def annotations(name):
    """Tiny reader for the flat `"key": {status: x, ...}` lines of our YAML files."""
    out = {}
    path = os.path.join(REP, name + '-annotations.yaml')
    if not os.path.exists(path):
        return out
    for m in re.finditer(r'^\s+"([^"]+)":\s*\{status:\s*(\w+)', open(path, encoding='utf-8').read(), re.M):
        out[m.group(1)] = m.group(2)
    return out


E = html.escape
quality, tests, trace, sec, perf, arch = (load(n) for n in ('quality', 'tests', 'traceability', 'security', 'performance', 'architecture'))
T, TR, S, P, A = tests['data'], trace['data'], sec['data'], perf['data'], arch['data']

# ---- headline numbers -------------------------------------------------------------
tests_total = len(T['tests'] or [])
tests_pass = sum(1 for t in (T['tests'] or []) if t.get('status') == 'passed')
j_total = len(T['journeys'] or [])
j_pass = sum(1 for j in (T['journeys'] or []) if j.get('status') == 'passed')
tot = T['totals']
gap_scope = tot['total'] - tot['startup']
reached = tot['both'] + tot['testsOnly'] + tot['journeysOnly']
reqs = [r for m in TR['milestones'] for r in m['requirements']]
built = sum(1 for r in reqs if r['status'] == 'built')
proven = sum(1 for r in reqs if r.get('tests') or r.get('journeys'))
sec_ann = annotations('security')
open_hm = [f for f in S['findings'] if f['severity'] in ('high', 'medium')
           and sec_ann.get('finding:' + f['id'], 'open') not in ('fixed', 'intended', 'accepted')]
mods = A['modules']
layers = max(m['layer'] for m in mods) + 1
steps = P['steps']
gen = max(d['generated'] for d in (tests, trace, sec, perf, arch))

# ---- small SVG helpers ------------------------------------------------------------
def hbars(rows, maxv, unit='', width=520, row_h=30, label_w=190, fmt=lambda v: f'{v:g}'):
    """Single-series horizontal bars. rows: (label, value, tooltip)."""
    plot = width - label_w - 60
    h = row_h * len(rows) + 8
    out = [f'<svg class="viz" viewBox="0 0 {width} {h}" role="img" aria-label="bar chart">']
    for i, (label, v, tip) in enumerate(rows):
        y = 4 + i * row_h
        w = max(2, plot * v / maxv) if maxv else 2
        out.append(f'<text class="lbl" x="{label_w - 10}" y="{y + row_h / 2 + 4}" text-anchor="end">{E(label)}</text>')
        out.append(f'<rect class="track" x="{label_w}" y="{y + 7}" width="{plot}" height="{row_h - 14}" rx="4"/>')
        out.append(f'<rect class="bar s1" x="{label_w}" y="{y + 7}" width="{w:.1f}" height="{row_h - 14}" rx="4" data-tip="{E(tip)}"/>')
        out.append(f'<text class="val" x="{label_w + w + 8:.1f}" y="{y + row_h / 2 + 4}">{fmt(v)}{unit}</text>')
    out.append('</svg>')
    return ''.join(out)


def stacked(rows, series, width=560, row_h=30, label_w=190):
    label_w = max(label_w, 12 + 6.6 * max(len(r[0]) for r in rows))
    """Stacked horizontal bars with a 2px surface gap between segments.
    rows: (label, [values], tooltip); series: [(name, css class)]."""
    plot = width - label_w - 50
    maxv = max(sum(v) for _, v, _ in rows) or 1
    h = row_h * len(rows) + 8
    out = [f'<svg class="viz" viewBox="0 0 {width} {h}" role="img" aria-label="stacked bar chart">']
    for i, (label, vals, tip) in enumerate(rows):
        y = 4 + i * row_h
        x = label_w
        out.append(f'<text class="lbl" x="{label_w - 10}" y="{y + row_h / 2 + 4}" text-anchor="end">{E(label)}</text>')
        for (name, cls), v in zip(series, vals):
            if not v:
                continue
            w = plot * v / maxv
            out.append(f'<rect class="bar {cls}" x="{x:.1f}" y="{y + 7}" width="{max(w - 2, 1):.1f}" height="{row_h - 14}" rx="3" '
                       f'data-tip="{E(label)} · {E(name)}: {v}"/>')
            x += w
        out.append(f'<text class="val" x="{x + 6:.1f}" y="{y + row_h / 2 + 4}">{sum(vals)}</text>')
    out.append('</svg>')
    legend = ''.join(f'<span class="key"><i class="sw {cls}"></i>{E(n)}</span>' for n, cls in series)
    return f'<div class="legend">{legend}</div>' + ''.join(out)


def layer_diagram():
    by_layer = {}
    for m in mods:
        by_layer.setdefault(m['layer'], []).append(m)
    W, box_w, box_h, gap_y = 560, 150, 46, 92
    pos = {}
    order = sorted(by_layer, reverse=True)
    for row, layer in enumerate(order):
        ms = sorted(by_layer[layer], key=lambda m: m['name'])
        span = len(ms) * box_w + (len(ms) - 1) * 40
        x0 = (W - span) / 2 + 40
        for k, m in enumerate(ms):
            pos[m['name']] = (x0 + k * (box_w + 40), 18 + row * gap_y)
    H = 18 + len(order) * gap_y
    maxref = max(e['refs'] for e in A['domainEdges'])
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="module layer diagram">',
           '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker></defs>']
    for row, layer in enumerate(order):
        out.append(f'<text class="axis" x="6" y="{18 + row * gap_y + box_h / 2 + 4}">layer {layer}</text>')
    for e in A['domainEdges']:
        (x1, y1), (x2, y2) = pos[e['from']], pos[e['to']]
        sw = 1 + 3 * math.log10(e['refs']) / math.log10(maxref)
        out.append(f'<line class="edge" x1="{x1 + box_w / 2:.1f}" y1="{y1 + box_h}" x2="{x2 + box_w / 2:.1f}" y2="{y2 - 2}" '
                   f'stroke-width="{sw:.2f}" marker-end="url(#ah)" data-tip="{E(e["from"])} uses {E(e["to"])}: {e["refs"]:,} references"/>')
    for m in mods:
        x, y = pos[m['name']]
        tip = f'{m["name"]}: {m["documents"]} documents, cohesion {m["cohesion"]:.0f}% — {m.get("purpose") or ""}'
        out.append(f'<rect class="node" x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="6" data-tip="{E(tip)}"/>')
        out.append(f'<text class="nodet" x="{x + box_w / 2}" y="{y + 20}" text-anchor="middle">{E(m["name"])}</text>')
        out.append(f'<text class="nodes" x="{x + box_w / 2}" y="{y + 36}" text-anchor="middle">{m["documents"]} docs</text>')
    out.append('</svg>')
    return ''.join(out)


# ---- charts -----------------------------------------------------------------------
cat_rows = [(c['name'], c['score'], f'{c["name"]}: {c["score"]}/100 · {c["errors"]} errors, {c["warnings"]} warnings, {c["infos"]} info')
            for c in quality['categories']]
quality_svg = hbars(cat_rows, 100, fmt=lambda v: f'{v:.0f}')

ms_rows = []
for m in TR['milestones']:
    rs = m['requirements']
    pv = sum(1 for r in rs if r['status'] == 'built' and (r.get('tests') or r.get('journeys')))
    bu = sum(1 for r in rs if r['status'] == 'built') - pv
    nb = len(rs) - pv - bu
    ms_rows.append((m['name'], [pv, bu, nb], ''))
trace_svg = stacked(ms_rows, [('built and proven by a test or journey', 's1'), ('built, no test reaches it', 's2'),
                              ('not fully built', 'crit')])

mod_rows = [(m['module'], [m['both'] + m['testsOnly'] + m['journeysOnly'], m['neither'], m['startup']], '')
            for m in T['modules'] if m['module']]
cov_svg = stacked(mod_rows, [('reached by tests or journeys', 's1'), ('reached by neither', 's2'),
                             ('startup or scheduled (not a gap)', 'neutral')])

step_rows = [(s['step'], s['browserMs'], f'{s["step"]}: browser {s["browserMs"]:.0f} ms · server {s["serverMs"]:.0f} ms · '
              f'database {s["dbMs"]:.0f} ms · {s["queries"]} queries (median of {s["warmRuns"]} warm runs)') for s in steps]
perf_svg = hbars(step_rows, max(s['browserMs'] for s in steps), unit=' ms', label_w=230, fmt=lambda v: f'{v:,.0f}')

arch_svg = layer_diagram()

# ---- page -------------------------------------------------------------------------
def tile(value, label, sub, status=None):
    st = ''
    if status:
        icon = {'good': '✔', 'warn': '!', 'crit': '✖'}[status]
        st = f'<span class="status {status}"><b>{icon}</b> {E({"good": "on target", "warn": "needs attention", "crit": "failing"}[status])}</span>'
    return f'<div class="tile"><div class="big">{E(value)}</div><div class="tl">{E(label)}</div><div class="ts">{E(sub)}</div>{st}</div>'


tiles = ''.join([
    tile(f'{quality["overallScore"]:.0f}/100', 'quality score', f'{quality["summary"]["errors"]} errors · {quality["summary"]["warnings"]} warnings', 'warn'),
    tile(f'{built}/{len(reqs)}', 'requirements built', f'{proven} proven by a test or journey', 'good' if built == len(reqs) else 'warn'),
    tile(f'{tests_pass}/{tests_total} · {j_pass}/{j_total}', 'microflow tests · journeys', 'all passing' if tests_pass == tests_total and j_pass == j_total else 'failures', 'good' if tests_pass == tests_total and j_pass == j_total else 'crit'),
    tile(f'{100 * reached / gap_scope:.0f}%', 'microflows reached', f'{reached} of {gap_scope} (excl. {tot["startup"]} startup/scheduled)'),
    tile(str(len(open_hm)), 'open high/medium security findings', 'after triage', 'good' if not open_hm else 'crit'),
    tile(f'{len(mods)} · {layers} · {len(A["cycles"] or [])}', 'modules · layers · cycles', 'all dependencies point down', 'good' if not A['cycles'] else 'crit'),
])

cards = [
    ('architecture.html', 'Architecture', 'Layered module map, coupling matrix, bounded contexts, god nodes and bridges.', arch_svg,
     'Arrows point from a module to what it uses; thicker means more references. Hover a module or an arrow.'),
    ('traceability.html', 'Traceability', f'All {len(reqs)} user stories per milestone: built, partial, proven — with footprint, tests and journeys.', trace_svg,
     'Status is derived from each requirement’s anchors in the model, never ticked off by hand.'),
    ('tests.html', 'Tests and coverage', f'{tests_total} microflow tests, {j_total} browser journeys, measured microflow reach per module.', cov_svg,
     'Reach = microflows entered by a test (call graph) or a journey (runtime spans).'),
    ('performance.html', 'Performance', 'Per-step flame charts, top microflows, SQL statements and Postgres plans (auto_explain).', perf_svg,
     'Median browser time of 5 warm runs per step. “Place order and pay” includes the simulated gateway’s deliberate delay.'),
    ('quality.html', 'Quality score', 'Scored best-practice report: every lint finding by category.', quality_svg,
     'Scores fall 10 per error, 3 per warning and 1 per info, per category.'),
]
cards_html = ''.join(
    f'<section class="card"><header><h2>{E(t)}</h2><a class="open" href="{h}">Open full report →</a></header>'
    f'<p class="desc">{E(d)}</p><div class="chart">{svg}</div><p class="note">{E(n)}</p></section>' for h, t, d, svg, n in cards)
more = (f'<section class="card wide"><header><h2>Also in this set</h2></header><ul class="links">'
        f'<li><a href="security.html">Security review</a> — access grid per role, client-callable flows, unsafe defaults, lint security verdicts '
        f'({len(S["findings"])} findings, {len(open_hm)} open high/medium after triage).</li>'
        f'<li><a href="map.html">Software map</a> — interactive guide: features per slice, module map, page flows, data across modules, index.</li>'
        f'</ul></section>')

CSS = """
:root{color-scheme:light;--surface:#fcfcfb;--card:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--ink3:#7a7974;--grid:#e1e0d9;--axis:#c3c2b7;
--border:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--neutral:#c3c2b7;--good:#0ca30c;--warn:#fab219;--crit:#d03b3b;--link:#1f5fae}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--surface:#1a1a19;--card:#222220;--ink:#f0efec;
--ink2:#c3c2b7;--ink3:#8f8e88;--grid:#2c2c2a;--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--neutral:#4a4a46;--link:#7fb0ef}}
:root[data-theme="dark"]{color-scheme:dark;--surface:#1a1a19;--card:#222220;--ink:#f0efec;--ink2:#c3c2b7;--ink3:#8f8e88;--grid:#2c2c2a;
--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--neutral:#4a4a46;--link:#7fb0ef}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1240px;margin:0 auto;padding:32px 20px 60px}h1{font-size:28px;margin:0 0 4px}.sub{color:var(--ink2);margin:0 0 24px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:24px}
.tile{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px}.big{font-size:26px;font-weight:650}
.tl{color:var(--ink);font-size:13px}.ts{color:var(--ink3);font-size:12px}.status{display:inline-block;margin-top:6px;font-size:12px;color:var(--ink2)}
.status b{display:inline-block;width:16px;height:16px;border-radius:8px;text-align:center;line-height:16px;color:#fff;font-size:10px;margin-right:4px}
.status.good b{background:var(--good)}.status.warn b{background:var(--warn);color:#0b0b0b}.status.crit b{background:var(--crit)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,560px),1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 20px}.card.wide{grid-column:1/-1}
.card header{display:flex;justify-content:space-between;align-items:baseline;gap:12px}.card h2{font-size:18px;margin:0}
a{color:var(--link)}.open{font-size:14px;white-space:nowrap}.desc{color:var(--ink2);margin:4px 0 12px;font-size:14px}.note{color:var(--ink3);font-size:12px;margin:8px 0 0}
.chart{overflow-x:auto}.viz{width:100%;height:auto;display:block;font-size:12px}
.viz .lbl{fill:var(--ink2)}.viz .val{fill:var(--ink)}.viz .axis{fill:var(--ink3);font-size:11px}.viz .track{fill:var(--grid)}
.viz .bar{cursor:default}.viz .s1{fill:var(--s1)}.viz .s2{fill:var(--s2)}.viz .neutral{fill:var(--neutral)}.viz .crit{fill:var(--crit)}
.viz .bar:hover{opacity:.82}.viz .node{fill:var(--card);stroke:var(--s1);stroke-width:2}.viz .nodet{fill:var(--ink);font-weight:600;font-size:13px}
.viz .nodes{fill:var(--ink3);font-size:11px}.viz .edge{stroke:var(--axis)}.viz .edge:hover{stroke:var(--s1)}.viz .arrowhead{fill:var(--axis)}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--ink2);margin-bottom:6px}.key{display:inline-flex;align-items:center;gap:6px}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px}.sw.s1{background:var(--s1)}.sw.s2{background:var(--s2)}.sw.neutral{background:var(--neutral)}.sw.crit{background:var(--crit)}
.links{margin:8px 0 0;padding-left:18px}.links li{margin:4px 0}
#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--surface);padding:6px 9px;border-radius:6px;font-size:12px;max-width:340px;
display:none;z-index:9}footer{color:var(--ink3);font-size:12px;margin-top:28px}
"""
JS = """const tip=document.getElementById('tip');document.addEventListener('mousemove',e=>{const t=e.target.closest('[data-tip]');
if(!t){tip.style.display='none';return}tip.textContent=t.getAttribute('data-tip');tip.style.display='block';
const x=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8);tip.style.left=x+'px';tip.style.top=(e.clientY+16)+'px'});"""

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GitPizza quality reports</title><style>{CSS}</style></head><body><main>
<h1>GitPizza quality reports</h1>
<p class="sub">Five modules in four layers — Simulation → Shop → Fulfilment → Catalog + Core. Generated {E(gen)} by {E(arch['mxcli'])}; every number below is the linked report's own.</p>
<div class="tiles">{tiles}</div>
<div class="grid">{cards_html}{more}</div>
<footer>Rebuild: run the reports with <code>--format json -o docs/reports/raw/&lt;kind&gt;.json</code>, then <code>python3 tools/reports_index.py</code>.</footer>
</main><div id="tip" role="tooltip"></div><script>{JS}</script></body></html>"""
open(os.path.join(REP, 'index.html'), 'w', encoding='utf-8').write(page)
print('wrote docs/reports/index.html')
