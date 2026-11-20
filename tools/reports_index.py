#!/usr/bin/env python3
"""Overview of all report pages: docs/reports/index.html, in the shared house style.

    python3 tools/reports_index.py

Reads the reports' own data: docs/reports/raw/*.json (mxcli report … --format json), the
performance before/after (docs/perf/data/*.json) and docs/reports/security-annotations.yaml.
Each card links the report page (docs/<kind>/report.html) and mxcli's built-in rendering.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from report_kit import E, MODULE_COLOR, bar, kpis, page, stack, write  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..'))
REP = os.path.join(ROOT, 'docs', 'reports')
RAW = os.path.join(REP, 'raw')


def load(name):
    return json.load(open(os.path.join(RAW, name + '.json'), encoding='utf-8'))


def triage(name):
    path = os.path.join(REP, name + '-annotations.yaml')
    out = {}
    if os.path.exists(path):
        for m in re.finditer(r'^\s+"([^"]+)":\s*\{status:\s*(\w+)', open(path, encoding='utf-8').read(), re.M):
            out[m.group(1)] = m.group(2)
    return out


quality, tests, trace, sec, arch = (load(n) for n in ('quality', 'tests', 'traceability', 'security', 'architecture'))
T, TR, S, A = tests['data'], trace['data'], sec['data'], arch['data']
pb = {(s['journey'], s['step']): s for s in json.load(open(os.path.join(ROOT, 'docs', 'perf', 'data', 'before.json')))['steps']}
pa = {(s['journey'], s['step']): s for s in json.load(open(os.path.join(ROOT, 'docs', 'perf', 'data', 'after.json')))['steps']}
vis = json.load(open(os.path.join(ROOT, 'docs', 'overview', 'data', 'visual.json')))

# ---------------------------------------------------------------- numbers
t_total = len(T['tests'] or [])
t_pass = sum(1 for t in (T['tests'] or []) if t.get('status') == 'passed')
j_total = len(T['journeys'] or [])
j_pass = sum(1 for j in (T['journeys'] or []) if j.get('status') == 'passed')
tot = T['totals']
scope = tot['total'] - tot['startup']
reached = tot['both'] + tot['testsOnly'] + tot['journeysOnly']
reqs = [r for m in TR['milestones'] for r in m['requirements']]
built = sum(1 for r in reqs if r['status'] == 'built')
partial = [r['title'].split()[0] for r in reqs if r['status'] != 'built']
proven = sum(1 for r in reqs if r.get('tests') or r.get('journeys'))
st = triage('security')
open_hm = [f for f in S['findings'] if f['severity'] in ('high', 'medium')
           and st.get('finding:' + f['id'], 'open') not in ('fixed', 'intended', 'accepted')]
mods = A['modules']
layers = len({m['layer'] for m in mods})
cycles = len(A.get('cycles') or [])
cats = quality['categories']
gen = max(d['generated'] for d in (tests, trace, sec, arch))

# ---------------------------------------------------------------- cards
def card(href, builtin, title, desc, viz, facts):
    links = f'<a class="open" href="{href}">Open report →</a>' + (f'<a class="alt" href="{builtin}">built-in rendering</a>' if builtin else '')
    return (f'<article class="card"><header><h2>{E(title)}</h2><div class="links">{links}</div></header><p class="desc">{desc}</p>'
            f'<div class="viz">{viz}</div><ul class="facts">{"".join(f"<li>{x}</li>" for x in facts)}</ul></article>')


def row(label, inner, value=''):
    return f'<div class="row"><span class="lab">{E(label)}</span><span class="cell">{inner}</span><span class="val">{value}</span></div>'


# traceability: per milestone built+proven / built, not reached / partial
tr_rows = ''
for m in TR['milestones']:
    rs = m['requirements']
    pv = sum(1 for r in rs if r['status'] == 'built' and (r.get('tests') or r.get('journeys')))
    bu = sum(1 for r in rs if r['status'] == 'built') - pv
    pa_ = len(rs) - pv - bu
    tr_rows += row(m['name'].split('—')[0].strip() + ' ' + m['name'].split('—')[-1].strip()[:22],
                   stack([(pv, '--good', 'built, reached by a test or journey'), (bu, '--s1', 'built, no test reaches it'), (pa_, '--warn', 'partly built')]),
                   f'{pv + bu}/{len(rs)}')
tr_leg = '<div class="legend"><span><i style="background:var(--good)"></i>built, tested</span><span><i style="background:var(--s1)"></i>built, untested</span><span><i style="background:var(--warn)"></i>partly built</span></div>'

# tests: per module coverage
te_rows = ''
for m in sorted([m for m in T['modules'] if m['module']], key=lambda m: ['Simulation', 'Shop', 'Fulfilment', 'Catalog', 'Core'].index(m['module']) if m['module'] in MODULE_COLOR else 9):
    r = m['both'] + m['testsOnly'] + m['journeysOnly']
    te_rows += row(m['module'], stack([(m['both'] + m['testsOnly'], '--good', 'reached by microflow tests'), (m['journeysOnly'], '--s1', 'reached by journeys only'),
                                       (m['neither'], '--bad', 'reached by neither'), (m['startup'], '--none-bg', 'startup or scheduled')]),
                   f'{r}/{r + m["neither"]}')
te_leg = '<div class="legend"><span><i style="background:var(--good)"></i>microflow tests</span><span><i style="background:var(--s1)"></i>journeys only</span><span><i style="background:var(--bad)"></i>neither</span><span><i style="background:var(--none-bg)"></i>startup / scheduled</span></div>'

# performance: steps that changed
pf_rows = ''
for k in [('Guest orders a pizza', '2 open menu'), ('Guest orders a pizza', '5 add to cart'), ('Guest orders a pizza', '1 open home'), ('Guest orders a pizza', '3 open configurator')]:
    b, a = pb[k], pa[k]
    pf_rows += row(k[1].split(' ', 1)[1], bar(100 * a['dbMs'] / max(b['dbMs'], 1), 'brand', f'{a["dbMs"]:.0f} of {b["dbMs"]:.0f} ms'), f'{b["queries"]:.0f}→{a["queries"]:.0f} q')

# architecture: modules per layer with cohesion
ar_rows = ''
for m in sorted(mods, key=lambda m: -m['layer']):
    p = m['cohesion']
    ar_rows += row(f'L{m["layer"]} {m["name"]}', bar(p, 'good' if p >= 70 else 'warn' if p >= 40 else 'bad'), f'{m["fanOut"]} uses')

# security
sev = {}
for f in S['findings']:
    sev.setdefault(f['severity'], []).append(st.get('finding:' + f['id'], 'open'))
se_rows = ''.join(row(s, ' '.join(f'<span class="tag {"good" if v in ("fixed", "intended", "accepted") else "bad"}">{E(v)}</span>' for v in sev[s]), str(len(sev[s])))
                  for s in ('high', 'medium', 'low', 'info') if s in sev)

# quality
qu_rows = ''.join(row(c['name'], bar(c['score'], 'good' if c['score'] >= 80 else 'warn' if c['score'] >= 50 else 'bad'),
                      f'{c["errors"]}E {c["warnings"]}W {c["infos"]}I') for c in cats)

menu_b, menu_a = pb[('Guest orders a pizza', '2 open menu')], pa[('Guest orders a pizza', '2 open menu')]
RD = json.load(open(os.path.join(REP, 'raw', 'readiness.json')))['data']
CF = json.load(open(os.path.join(REP, 'raw', 'configuration.json')))['data']
DP = json.load(open(os.path.join(REP, 'raw', 'dependencies.json')))['data']
cards = [
    card('../traceability/report.html', 'traceability.html', 'Traceability',
         f'All {len(reqs)} PRD user stories per milestone: derived status, the microflows behind each, and the tests and journeys that reach them.',
         tr_rows + tr_leg, [f'{built} of {len(reqs)} built; partly: {", ".join(partial) or "none"}', f'{proven} reached by a test or journey']),
    card('../testing/report.html', 'tests.html', 'Tests and coverage',
         'Microflow tests, browser journeys and the visual comparison with the prototype, and which microflows they reach per module.',
         te_rows + te_leg, [f'{t_pass}/{t_total} microflow tests · {j_pass}/{j_total} journeys pass',
                            f'{reached} of {scope} non-startup microflows reached · visual {sum(1 for r in vis["screens"] if r["mismatch"] <= r["budget"])}/{len(vis["screens"])} within budget']),
    card('../perf/report.html', 'performance.html', 'Performance under load',
         'Two guest journeys on 400,000 orders, before and after the fixes: findings grouped by improvement, flame-chart pairs, statements.',
         pf_rows + '<p class="note">Database time after the fixes, as a share of before.</p>',
         [f'menu {menu_b["browserMs"]:.0f} → {menu_a["browserMs"]:.0f} ms', 'housekeeping backlog no longer blocks checkout (F1)']),
    card('../architecture/report.html', 'architecture.html', 'Architecture',
         'Module map with counts and cohesion, with and without the generated seed; coupling, bounded contexts, bridges and recommendations.',
         ar_rows + '<p class="note">Cohesion per module (share of references that stay inside).</p>',
         [f'{len(mods)} modules · {layers} layers · {cycles} cycles', 'Simulation is mostly generated seed; see the report']),
    card('../security/report.html', 'security.html', 'Security',
         'Who can read what, client-callable flows that trust the caller, unsafe defaults, and a verdict per security rule.',
         se_rows, [f'{len(open_hm)} open high/medium findings after triage', 'every visitor is an anonymous guest; data is row-scoped']),
    card('../quality/report.html', 'quality.html', 'Quality score',
         'Every lint finding by category and rule, with a verdict per rule and the changes that would move the score most.',
         qu_rows, [f'score {quality["overallScore"]:g}/100', f'{quality["summary"]["errors"]} errors · {quality["summary"]["warnings"]} warnings · {quality["summary"]["infos"]} info']),
    card('readiness.html', None, 'Production readiness',
         'One go/no-go page rolled up from the other reports: blocking items, risks, what is accepted, the administrator checklist and what was not assessed.',
         '', [f'verdict: {RD["verdict"]} · {len(RD["blocking"])} blocking · {len(RD["risks"])} risks · {len(RD["accepted"])} accepted',
              'not assessed: ' + (', '.join(s['kind'] for s in RD['sources'] if not s['assessed']) or 'none')]),
    card('configuration.html', None, 'Configuration',
         'What each environment must supply: constants to set, scheduled events to switch, startup work, read from the model.',
         '', [f'{sum(1 for c in CF["constants"] if c["need"] != "default applies")} of {len(CF["constants"])} constants must be set (' + ', '.join(c['name'] for c in CF['constants'] if c['need'] != 'default applies') + ')',
              f'{len(CF["scheduled"])} scheduled events to switch on or off']),
    card('dependencies.html', None, 'Dependencies',
         'Mendix release line, Marketplace modules and widgets against their newest versions, and known vulnerabilities (OSV).',
         '', [f'{sum(1 for m in DP["modules"] if m["status"] == "newer available")} of {len(DP["modules"])} Marketplace modules and {sum(1 for w in DP["widgets"] if w["status"] == "newer available")} of {len(DP["widgets"])} widgets have a newer version',
              'vulnerabilities checked against OSV: none found' if DP.get('vulnChecked') else 'vulnerabilities not checked']),
    card('map.html', None, 'Software map',
         'Interactive guide for a newcomer: features per slice, module map, page flows per role, data across modules, conventions, background work and an index.',
         '', ['self-contained: diagrams drawn in the browser']),
]

head_tiles = kpis([
    (f'{built}/{len(reqs)}', f'PRD stories built ({len(partial)} partly), {proven} reached by a test or journey', 'good' if not partial else 'warn'),
    (f'{t_pass}/{t_total} · {j_pass}/{j_total}', 'Microflow tests · browser journeys passing', 'good' if t_pass == t_total and j_pass == j_total else 'bad'),
    (f'{len(open_hm)}', 'Open high or medium security findings after triage', 'good' if not open_hm else 'bad'),
    (f'{quality["overallScore"]:g}/100', 'Scored quality report: ' + ', '.join(c['name'] for c in sorted(cats, key=lambda c: c['score'])[:3]) + ' score lowest (see the quality report)', 'warn'),
])

CSS = '''
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(520px, 100%), 1fr)); gap: 20px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 18px 20px; display: grid; gap: 10px; align-content: start; min-width: 0; }
.card header { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 6px 14px; }
.card h2 { margin: 0; font-size: 21px; }
.card .links { display: flex; gap: 14px; font-size: 13.5px; }
.card .links .open { font-weight: 600; color: var(--ink); text-decoration-color: var(--brand); text-decoration-thickness: 2px; }
.card .links .alt { color: var(--muted); }
.card .desc { color: var(--muted); margin: 0; }
.viz { display: grid; gap: 6px; }
.row { display: grid; grid-template-columns: minmax(90px, 160px) 1fr auto; gap: 10px; align-items: center; font-size: 13px; }
.row .lab { color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row .val { font: 12px var(--f-mono); color: var(--muted); white-space: nowrap; }
.row .bar { width: 100%; }
.facts { margin: 0; padding-left: 18px; font-size: 13.5px; }
.also { color: var(--muted); font-size: 14px; }
'''
body = head_tiles + f'<section class="cards">{"".join(cards)}</section>' + (
    '<section class="also"><h2>Also</h2><ul class="tight">'
    '<li><a href="../../RUN/delivery-notes.md">Delivery notes</a>, <a href="../../RUN/operations.md">operations</a>, '
    '<a href="../../RUN/journal.md">journal</a> and <a href="../../RUN/self-assessment.json">self-assessment</a> (RUN/).</li>'
    '<li>Narrated journey videos: <a href="../../demo/films/order-desktop.mp4">ordering</a> and <a href="../../demo/films/declined-desktop.mp4">declined card</a> (desktop; phone versions next to them).</li>'
    '<li>Build overview sketch deck: <code>docs/overview/</code> (published privately as a Claude artifact).</li>'
    f'<li>Generated from each report\'s own data; latest data {E(gen)}. Rebuild: see <code>docs/reports/README.md</code>.</li></ul></section>')
html = page('GitPizza Reports', 'GitPizza · quality reports · 19 November 2026',
            'Every report on how the app was built and how it holds up: traceability to the PRD, tests, performance under load, architecture, security, '
            'quality score and a software map. All pages work offline and share one look; each also has mxcli\'s built-in rendering of the same data.',
            body, current='index', extra_css=CSS)
write(os.path.join(REP, 'index.html'), html)
