#!/usr/bin/env python3
"""Requirements traceability report (HTML): PRD user stories -> brain requirements -> model -> proof.

    ./mxcli report traceability -p GitPizza.mpr --format json > docs/reports/raw/traceability.json
    python3 docs/traceability/tools/gen_traceability.py          # -> docs/traceability/report.html

Every number comes from data: docs/reports/raw/traceability.json (status, anchors, footprint,
tests, journeys, decisions, method, limits), docs/reports/raw/journeys.jsonl (journey names and
results), docs/reports/raw/tests.json (all microflow tests), RUN/self-assessment.json (screens per
story), docs/overview/data/prd-epics.json (epics) and RUN/delivery-notes.md (the deviation table).
Reasons for partial requirements are read from the brain decisions ("Partly meets requirement
`<id>`: ..."). The prose is written here by hand from that data.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools'))
from report_kit import E, page, kpis, section, table, bar, finding, write  # noqa: E402

OUT = os.path.join(HERE, '..', 'report.html')


def path(*p):
    return os.path.join(REPO, *p)


def load(*p):
    with open(path(*p)) as f:
        return json.load(f)


TR = load('docs', 'reports', 'raw', 'traceability.json')
D = TR['data']
SELF = {s['id']: s for s in load('RUN', 'self-assessment.json')['stories']}
EPICS = load('docs', 'overview', 'data', 'prd-epics.json')
TESTS_ALL = [t['name'] for t in load('docs', 'reports', 'raw', 'tests.json')['data']['tests']]
with open(path('docs', 'reports', 'raw', 'journeys.jsonl')) as f:
    JOURNEYS = [json.loads(line) for line in f if line.strip()]
JNAME = {j['journey'].split()[0]: j['journey'] for j in JOURNEYS}
JIDS = sorted(JNAME, key=lambda j: int(j[1:]))
SPAN_NAMES = set()
with open(path('docs', 'reports', 'raw', 'spans.jsonl')) as f:
    for line in f:
        for m in re.finditer(r'"([A-Z][A-Za-z]+\.[A-Za-z0-9_]+)"', line):
            SPAN_NAMES.add(m.group(1))


def md(t):
    """escape, then render `code` spans"""
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', E(t))


# hand-written notes, checked against tests/e2e/journeys.js: a journey whose name suggests it covers a story it does not
JOURNEY_NOTE = {'US-064': 'J9\'s name says "remove and clear", but it lowers the quantity and clears the cart; it never removes a single line, '
                          'so neither footprint microflow runs. The report is right; the journey name overpromises.'}

gen = datetime.datetime.strptime(TR['generated'][:10], '%Y-%m-%d')
DATE = f'{gen.day} {gen.strftime("%B %Y")}'

# ---------------------------------------------------------------- brain: partial/changed reasons
REASON = {}       # requirement id -> (decision heading, short reason, decision id, kind)
for fn in sorted(os.listdir(path('docs', 'brain', 'modules'))):
    text = open(path('docs', 'brain', 'modules', fn)).read()
    for block in re.split(r'\n(?=## )', text):
        if not block.startswith('## '):
            continue
        head = block[3:].split('\n', 1)[0].strip()
        did = re.search(r'id `([0-9a-f]{6})`', block)
        for kind, rid, why in re.findall(r'(Partly meets|Changes) requirement `([0-9a-f]{6})`:\s*(.+)', block):
            REASON[rid] = (head, why.strip(), did.group(1) if did else '', kind)

# ---------------------------------------------------------------- delivery notes: deviation table
DEVS = []
for line in open(path('RUN', 'delivery-notes.md')):
    if re.match(r'\|\s*DEV-\d+\s*\|', line):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        DEVS.append({'id': c[0], 'type': c[1], 'ref': c[2], 'says': c[3], 'does': c[4], 'why': c[5]})

# ---------------------------------------------------------------- requirements
def usnum(title):
    m = re.match(r'US-(\d+)', title)
    return int(m.group(1)) if m else 0


def epic_of(n):
    for e in EPICS:
        nums = [int(x) for x in re.findall(r'US-(\d+)', e['range'])]
        if nums and nums[0] <= n <= nums[-1]:
            return e['id']
    return None


REQS, MS = [], []
for m in D['milestones']:
    MS.append(m['name'])
    for r in m['requirements']:
        r = dict(r)
        for k in ('anchors', 'footprint', 'tests', 'journeys', 'decisions', 'questions'):
            r[k] = r.get(k) or []
        r['milestone'] = m['name']
        r['us'] = r['title'].split()[0]
        r['name'] = r['title'].split(' ', 1)[1] if ' ' in r['title'] else r['title']
        r['n'] = usnum(r['title'])
        r['epic'] = epic_of(r['n'])
        r['jids'] = sorted({j.split()[0] for j in r['journeys']}, key=lambda j: int(j[1:]))
        r['reached'] = bool(r['tests'] or r['journeys'])
        REQS.append(r)

TOTAL = len(REQS)
ST = lambda s: [r for r in REQS if r['status'] == s]  # noqa: E731
built, partial, changed, notbuilt, untrace = ST('built'), ST('partial'), ST('changed'), ST('not built'), ST('not traceable')
reached = [r for r in REQS if r['reached']]
by_test = [r for r in REQS if r['tests']]
unreached = [r for r in REQS if not r['reached']]
linked_tests = sorted({t for r in REQS for t in r['tests']})
QUESTIONS = D.get('questions') or []
all_j = [r for r in REQS if len(r['jids']) == len(JIDS)]


def ms_short(name):
    return name.split(' ')[0]


def ms_stats(name):
    rs = [r for r in REQS if r['milestone'] == name]
    return {'name': name, 'n': len(rs), 'built': sum(r['status'] == 'built' for r in rs),
            'partial': sum(r['status'] in ('partial', 'changed') for r in rs),
            'notbuilt': sum(r['status'] in ('not built', 'not traceable') for r in rs),
            'test': sum(bool(r['tests']) for r in rs), 'journey': sum(bool(r['journeys']) and not r['tests'] for r in rs),
            'reached': sum(r['reached'] for r in rs), 'unreached': [r for r in rs if not r['reached']]}


MSTATS = [ms_stats(m) for m in MS]
weak = min(MSTATS, key=lambda s: s['reached'] / s['n'])


def ep_stats(e):
    rs = [r for r in REQS if r['epic'] == e['id']]
    return {'e': e, 'rs': rs, 'n': len(rs), 'built': sum(r['status'] == 'built' for r in rs),
            'partial': sum(r['status'] in ('partial', 'changed') for r in rs), 'reached': sum(r['reached'] for r in rs)}


ESTATS = [ep_stats(e) for e in EPICS]
assert sum(s['n'] for s in ESTATS) == TOTAL, 'every requirement belongs to one epic'
weak_ep = min(ESTATS, key=lambda s: (s['reached'] / s['n'], -s['n']))

# self-assessment agreement (done <-> built, partial <-> partial)
SA_MAP = {'done': 'built', 'partial': 'partial'}
disagree = [r for r in REQS if SA_MAP.get(SELF.get(r['us'], {}).get('status')) != r['status']]
sa_journey_note = {k: v['notes'] for k, v in SELF.items() if re.search(r'journey J\d+', v.get('notes') or '')}


# ---------------------------------------------------------------- helpers
STATUS_TAG = {'built': ('good', 'BUILT'), 'partial': ('warn', 'PARTIAL'), 'changed': ('warn', 'CHANGED'),
              'not built': ('bad', 'NOT BUILT'), 'not traceable': ('none', 'NO ANCHORS')}


def tag(status):
    c, t = STATUS_TAG.get(status, ('none', status.upper()))
    return f'<span class="tag {c}">{t}</span>'


def screens(us):
    w = (SELF.get(us) or {}).get('where', '')
    w = w.split(';')[0].strip()
    if not w or w == 'n/a':
        return '<span class="muted">—</span>'
    if not w.startswith('SCR'):
        return f'<span class="muted">{E(w)}</span>'
    return ', '.join(f'<span class="scr">{E(s.strip())}</span>' for s in w.split(','))


def plural(n, word):
    return f'{n} {word}{"" if n == 1 else "s"}'


def listing(items, unit, empty):
    if not items:
        return f'<span class="muted">{empty}</span>'
    return (f'<details class="mini"><summary>{plural(len(items), unit)}</summary><ul>'
            + ''.join(f'<li><code>{E(x)}</code></li>' if unit == 'microflow' else f'<li>{E(x)}</li>' for x in items) + '</ul></details>')


def journeys_cell(r):
    if not r['jids']:
        return '<span class="muted">none</span>'
    tip = E('\n'.join(r['journeys']))
    if len(r['jids']) == len(JIDS):
        return f'<span class="jt" title="{tip}">all {len(JIDS)}</span>'
    return ' '.join(f'<span class="jt" title="{E(JNAME.get(j, j))}">{j}</span>' for j in r['jids'])


def ids(rs):
    return ', '.join(r['us'] for r in rs)


# ---------------------------------------------------------------- KPIs
pct = lambda a, b: 100 * a / b if b else 0  # noqa: E731
partial_all = partial + changed
K = kpis([
    (f'{len(built)} <small class="of">of </small>{TOTAL}',
     f'requirements built: every anchor resolves in the model ({pct(len(built), TOTAL):.0f} %). {len(notbuilt)} not built, {len(untrace)} without anchors.',
     'good' if not notbuilt else 'warn'),
    (f'{len(partial_all)}',
     'partly met by a recorded decision: ' + '; '.join(f'<b>{E(r["us"])}</b> {E(r["name"])}' for r in partial_all) if partial_all else 'requirements partly met or changed by a decision',
     'warn' if partial_all else 'good'),
    (f'{len(reached)} <small class="of">of </small>{TOTAL}',
     f'reached by a microflow test or a browser journey ({pct(len(reached), TOTAL):.0f} %). Only {len(by_test)} by a microflow test; {len(unreached)} by nothing.',
     'warn' if unreached else 'good'),
    (f'{weak["reached"]} <small class="of">of </small>{weak["n"]}',
     f'reached in <b>{E(weak["name"])}</b>, the milestone with the weakest proof; by epic, {E(weak_ep["e"]["id"])} {E(weak_ep["e"]["title"])} '
     f'({weak_ep["reached"]} of {weak_ep["n"]}).',
     'bad' if pct(weak['reached'], weak['n']) < 50 else 'warn'),
])

# ---------------------------------------------------------------- milestone chart (CSS bars, counts as text)
MAXN = max(s['n'] for s in MSTATS)


def seg(n, var, label):
    cls = ' class="nr"' if var == '--none-bg' else ''
    return f'<i{cls} style="flex:{n};background:var({var})" title="{E(label)}: {n}"></i>' if n else ''


rows = []
for s in MSTATS:
    w = 100 * s['n'] / MAXN
    unr = s['n'] - s['reached']
    rows.append(
        f'<div class="msname"><b>{E(s["name"])}</b><span class="muted">{plural(s["n"], "requirement")}</span></div>'
        f'<div class="msbars">'
        f'<div class="row"><span class="k">Built</span><div class="track"><div class="fill" style="width:{w:.1f}%">'
        f'{seg(s["built"], "--good", "built")}{seg(s["partial"], "--warn", "partial")}{seg(s["notbuilt"], "--bad", "not built")}</div></div>'
        f'<span class="cnt">{s["built"]} built · {s["partial"]} partial · {s["notbuilt"]} not built</span></div>'
        f'<div class="row"><span class="k">Proven</span><div class="track"><div class="fill" style="width:{w:.1f}%">'
        f'{seg(s["test"], "--s7", "microflow test")}{seg(s["journey"], "--s1", "journey only")}{seg(unr, "--none-bg", "not reached")}</div></div>'
        f'<span class="cnt">{s["test"]} test · {s["journey"]} journey only · <b class="{"bad" if unr else ""}">{unr} not reached</b></span></div>'
        f'</div>')
chart = (f'<div class="panel"><div class="legend">'
         f'<span><i style="background:var(--good)"></i>built</span><span><i style="background:var(--warn)"></i>partial</span>'
         f'<span><i style="background:var(--bad)"></i>not built</span>'
         f'<span><i style="background:var(--s7)"></i>reached by a microflow test</span><span><i style="background:var(--s1)"></i>reached by a journey only</span>'
         f'<span><i class="nr"></i>not reached</span></div>'
         f'<div class="ms">{"".join(rows)}</div></div>')

# ---------------------------------------------------------------- epic table
erows = []
for s in ESTATS:
    e = s['e']
    pri = ', '.join(f'{v} {k}' for k, v in e['priorities'].items())
    p = pct(s['reached'], s['n'])
    unr = [r for r in s['rs'] if not r['reached']]
    erows.append([f'<code>{E(e["id"])}</code>', f'{E(e["title"])}<span class="rng">{E(e["range"])} · {E(pri)}</span>',
                  str(s['n']), str(s['built']), (str(s['partial']) if s['partial'] else '<span class="muted">0</span>'),
                  bar(p, 'good' if p == 100 else 'warn' if p >= 50 else 'bad', f'{s["reached"]} of {s["n"]}'),
                  (ids(unr) if unr else '<span class="muted">—</span>', 'note')])
epic_table = table([('Epic', ''), ('Title · stories · priority', ''), ('Stories', 'num'), ('Built', 'num'), ('Partial', 'num'),
                    ('Reached', ''), ('Not reached', '')], erows)

# ---------------------------------------------------------------- gaps
gap_a = []
for r in partial_all:
    head, why, did, kind = REASON.get(r['id'], ('', '', '', ''))
    dev = next((d for d in DEVS if r['us'] in d['ref']), None)
    pri = re.search(r'\((Must|Should|Could)\)', dev['ref']).group(1) if dev and re.search(r'\((Must|Should|Could)\)', dev['ref']) else None
    built_txt = re.sub(r'^US-\d+ (is )?partly met:\s*', '', head)
    body = (f'<p><b>Asked:</b> {md(dev["says"]) if dev else "see the story"}. '
            f'<b>Built:</b> {md(built_txt[:1].upper() + built_txt[1:])}</p>'
            f'<p class="muted">Decision <code>{E(did)}</code> — "{E(kind)} requirement <code>{E(r["id"])}</code>: {E(why)}"'
            f'{f"; delivery notes {E(dev["id"])}: {E(dev['why'])}" if dev else ""}.'
            f' Proof: {plural(len(r["tests"]), "test")}, journeys {", ".join(r["jids"]) or "none"}.</p>')
    gap_a.append(finding(r['us'][3:], 'warn', f'{r["status"]}{f" · {pri} story" if pri else ""}', f'{E(r["us"])} {E(r["name"])}', body))
interp = [d for d in DEVS if d['type'] == 'INTERPRETATION' and re.search(r'US-\d+', d['ref'])]
for d in interp:
    us = re.search(r'US-\d+', d['ref']).group(0)
    r = next((x for x in REQS if x['us'] == us), None)
    if not r:
        continue
    dec = next((x for x in r['decisions'] if 'although' in x or 'prototype' in x), '')
    gap_a.append(finding(us[3:], 'good', f'{r["status"]} · interpretation', f'{E(us)} {E(r["name"])} — built as the story asks, not as the prototype shows',
                         f'<p>{E(d["says"])}. {E(d["does"])}. Reason: {E(d["why"])} ({E(d["id"])}).</p>'
                         + (f'<p class="muted">Decision <code>{E(dec.split(":")[0])}</code> records it; traceability counts it as built, which is right — '
                            f'journey J10 exercises the filter.</p>' if dec else ''), tag_cls='none'))

ur_rows = []
for r in unreached:
    note = sa_journey_note.get(r['us'], '')
    jm = re.search(r'journey (J\d+)', note)
    if jm:
        seen = [x for x in r['footprint'] if x in SPAN_NAMES]
        why = (f'<b>{jm.group(1)}</b> exercises it ({E(JNAME.get(jm.group(1), ""))}), but '
               + (f'none of its footprint microflows ({", ".join(r["footprint"])}) runs in that journey' if not seen else 'its footprint microflows run elsewhere, not in that journey')
               + ' and the journey log does not name the anchored page, so traceability cannot link them.')
    elif not r['footprint']:
        why = 'No microflow in its footprint (a snippet or page only), so no span can show it.'
    else:
        seen = [x for x in r['footprint'] if x in SPAN_NAMES]
        why = (JOURNEY_NOTE.get(r['us']) or
               (f'None of its {plural(len(r["footprint"]), "footprint microflow")} appears in any recorded span.' if not seen else
                f'{", ".join(seen)} ran, but not inside a journey\'s window.'))
    ur_rows.append({'cls': 'hit' if jm else '', 'cells': [f'<code>{E(r["us"])}</code>', E(r['name']), ms_short(r['milestone']),
                    str(len(r['footprint'])), screens(r['us']), (why, 'note')]})
ur_table = table([('ID', ''), ('Requirement', ''), ('Milestone', ''), ('Footprint', 'num'), ('Screens', ''), ('Why no proof', '')], ur_rows)
j_linked = [m.group(1) for m in (re.search(r'journey (J\d+)', sa_journey_note.get(r['us'], '')) for r in unreached) if m]

# proof quality
tests_by_req = {r['us']: r['tests'] for r in by_test}
groups = {}
for r in by_test:
    groups.setdefault(tuple(sorted(r['tests'])), []).append(r)
odd = []
for g in groups.values():
    eps = [r['epic'] for r in g]
    if len(set(eps)) > 1:
        main = max(set(eps), key=eps.count)
        odd += [r for r in g if r['epic'] != main]
proof = [
    finding('T', 'warn', 'Thin', f'Microflow tests reach {len(by_test)} of {TOTAL} requirements',
            f'<p>The project has {len(TESTS_ALL)} microflow tests; {len(linked_tests)} of them touch a requirement\'s footprint, the other {len(TESTS_ALL) - len(linked_tests)} '
            f'test shared helpers (money and timer formatting) that no requirement anchors. They concentrate on pricing and the configurator: '
            + '; '.join(f'{E(r["us"])} {E(r["name"])} ({len(r["tests"])})' for r in by_test) + '. '
            f'Everything else rests on browser journeys alone.</p>'
            + (f'<p>A test proves a requirement when its call closure <em>touches</em> the footprint, not when it asserts the requirement: '
               + ', '.join(f'{E(r["us"])} {E(r["name"])}' for r in odd)
               + ' is credited with the configurator\'s allergen and price tests because they share the line recalculation, not because a test makes an item unavailable at checkout.</p>' if odd else '')),
    finding('J', 'warn', 'Inflated', f'{len(all_j)} requirements are "reached" by every journey',
            f'<p>{ids(all_j)} are each linked to all {len(JIDS)} journeys — including J5, which only opens an unknown URL. Most are the simulator\'s background work '
            f'(kitchen, dispatch, traffic generator, housekeeping, simulated payments) and the shell around every page: their microflows run on the clock or on every page '
            f'load, so they appear in every journey\'s spans. For the simulator rows that shows the work happens, not that a journey checks it.</p>'),
]

# ---------------------------------------------------------------- deviations table
dev_rows = []
traced_us = {r['us'] for r in REQS}
for d in DEVS:
    us = re.findall(r'US-\d+', d['ref'])
    inb = [u for u in us if u in traced_us]
    t = {'PARTIAL': 'warn', 'CHANGED': 'none', 'INTERPRETATION': 'none'}.get(d['type'], 'none')
    dev_rows.append({'cls': 'hit' if d['type'] == 'PARTIAL' and not inb else '',
                     'cells': [f'<code>{E(d["id"])}</code>', f'<span class="tag {t}">{E(d["type"])}</span>',
                               re.sub(r'`([^`]+)`', r'<code>\1</code>', E(d['ref'])),
                               (f'yes — {", ".join(inb)}' if inb else '<b>no</b>' if d['type'] == 'PARTIAL' else '<span class="muted">no (not a story)</span>')]})
dev_table = table([('Deviation', ''), ('Type', ''), ('Package reference', ''), ('In this report', '')], dev_rows)
dev_outside = [d for d in DEVS if d['type'] == 'PARTIAL' and not any(u in traced_us for u in re.findall(r'US-\d+', d['ref']))]

# ---------------------------------------------------------------- full table, grouped by milestone and epic
COLS = [('ID', ''), ('Requirement', ''), ('Status', ''), ('Footprint', ''), ('Tests', ''), ('Journeys', ''), ('Screens', '')]
full = []
for m in MS:
    s = next(x for x in MSTATS if x['name'] == m)
    full.append(f'<h3 class="msh">{E(m)} <span class="muted">· {s["built"]} built, {s["partial"]} partial, {s["reached"]} of {s["n"]} reached</span></h3>')
    for e in EPICS:
        rs = sorted([r for r in REQS if r['milestone'] == m and r['epic'] == e['id']], key=lambda r: r['n'])
        if not rs:
            continue
        rows = []
        for r in rs:
            dec = ''
            if r['decisions']:
                dec = f'<span class="rng" title="{E(chr(10).join(r["decisions"]))}">{plural(len(r["decisions"]), "decision")}</span>'
            rows.append({'cls': '' if r['reached'] and r['status'] == 'built' else 'hit',
                         'cells': [f'<code>{E(r["us"])}</code>', f'{E(r["name"])}{dec}', tag(r['status']),
                                   listing(r['footprint'], 'microflow', 'none'), listing(r['tests'], 'test', 'none'),
                                   journeys_cell(r), (screens(r['us']), 'note')]})
        nb = sum(r['status'] == 'built' for r in rs)
        nr = sum(r['reached'] for r in rs)
        flags = []
        if nb < len(rs):
            flags.append(f'<span class="tag warn">{len(rs) - nb} partial</span>')
        if nr < len(rs):
            flags.append(f'<span class="tag bad">{len(rs) - nr} not reached</span>')
        full.append(f'<details class="ep"><summary><code>{E(e["id"])}</code> {E(e["title"])} '
                    f'<span class="muted">· {plural(len(rs), "requirement")} · {nb} built · {nr} reached</span> {" ".join(flags)}</summary>'
                    f'{table(COLS, rows, "req")}</details>')

# ---------------------------------------------------------------- method / limits (rephrased by hand, sourced from the JSON's arrays)
assert len(TR['method']) == 6 and len(TR['limits']) == 4, 'method/limits changed: re-read them and update the prose below'
how = f'''<ul class="tight">
<li><b>Requirements</b> are the {TOTAL} user stories captured in the project brain (<code>docs/brain/plan/</code>), each with anchors to model elements.
Milestones come from each slice's <code>milestone:</code> frontmatter; epics from the PRD's story ranges (<code>prd-epics.json</code>).</li>
<li><b>Status is derived, never ticked off:</b> built when every anchor resolves in the model; partial or changed only when a decision says
"Partly meets requirement …" or "Changes requirement …".</li>
<li><b>Footprint</b> is the microflows that implement a requirement: anchored microflows and their same-module callees, microflows its pages or snippets call,
and microflows that write its entities or use its attributes. Helpers with more than three callers are left out.</li>
<li><b>Proof:</b> a microflow test counts when its call closure touches the footprint; a journey counts when a footprint microflow appears in its OpenTelemetry spans
or its log names an anchored page. {len(JOURNEYS)} journeys ran ({sum(j["status"] == "passed" for j in JOURNEYS)} passed) and {len(TESTS_ALL)} microflow tests.</li>
<li>Data: <code>mxcli report traceability --format json</code> ({E(TR["mxcli"])}, {E(TR["generated"])}); screens from <code>RUN/self-assessment.json</code>;
deviations from <code>RUN/delivery-notes.md</code>. Rendered by <code>docs/traceability/tools/gen_traceability.py</code>.</li>
<li>Cross-check: the self-assessment marks {sum(1 for v in SELF.values() if v["status"] == "done")} stories done and
{sum(1 for v in SELF.values() if v["status"] == "partial")} partial; {"it agrees with every derived status" if not disagree else f"it disagrees on {ids(disagree)}"}.</li>
</ul>'''
limits = f'''<ul class="tight">
<li>Only captured requirements appear. A PRD item nobody captured in the brain is invisible — including non-story requirements such as A-91 (DEV-03, under Gaps).</li>
<li>"Built" means the anchors exist, not that they do what was asked; the proof columns and decisions are what say more.</li>
<li>Pages fed only by database data sources run no microflow, so a journey reaching them is invisible unless its log names the page (US-281/J5, US-287/J6).</li>
<li>"Reached" is not "asserted": a test or journey that merely runs a footprint microflow counts, and background simulator work runs during every journey.</li>
<li>Footprints miss microflows reached only from Java actions, and nanoflows.</li>
</ul>'''

# ---------------------------------------------------------------- page
lede = (f'Which of the PRD\'s user stories the app implements, where in the model, and what evidence says they work. {TOTAL} stories in {len(EPICS)} epics are captured as '
        f'requirements in the project brain; status comes from whether their anchors exist in the model and from recorded decisions, proof from {len(TESTS_ALL)} microflow tests '
        f'and {len(JOURNEYS)} browser journeys. Nothing on this page was ticked off by hand.')

q_html = ('<p>None. No open question is filed in the brain on any slice.</p>' if not QUESTIONS else
          '<ul class="tight">' + ''.join(f'<li>{E(str(q))}</li>' for q in QUESTIONS) + '</ul>')

body = K + section('Milestones at a glance', (
    f'<p>Each milestone is drawn to scale: the upper bar is build status, the lower one the strongest proof each requirement has. Everything is built, so the story is in the '
    f'proof bars: M2 is reached throughout, M1 and M3 have a few gaps, and {E(ms_short(weak["name"]))} — error pages and session messages — is reached for only '
    f'{weak["reached"]} of {weak["n"]}. Microflow tests (purple) are a sliver everywhere.</p>' + chart)) \
    + section('By epic', '<p>The same, per PRD epic. The bar is the share of stories reached by a test or journey.</p>' + epic_table) \
    + section('Gaps', (
        f'<h3>Not built as asked</h3><p>{len(partial_all)} requirements are partly met, each by a recorded decision; one more is built to the story where the prototype disagreed. '
        f'Nothing is not built or untraceable.</p>'
        f'<div class="findings">{"".join(gap_a)}</div>'
        f'<h3 class="gh">Built, but reached by no test or journey</h3>'
        f'<p>{len(unreached)} requirements have no proof at all. {len(j_linked)} of them ({", ".join(j_linked)}, highlighted) are in fact exercised by a journey that '
        f'traceability cannot see; the self-assessment says so for each. The rest are the demo banner and footer, three cart states, the demo reset and three error and session messages.</p>'
        + ur_table +
        f'<h3 class="gh">How strong the proof is</h3><div class="findings">{"".join(proof)}</div>'
        f'<h3 class="gh">Open questions</h3>{q_html}'
        f'<h3 class="gh">Deviations in the delivery notes</h3>'
        f'<p>The delivery notes list {len(DEVS)} deviations from the package. Three concern a captured story and appear above; the others concern the information model, '
        f'conventions or tooling and are not requirements here. '
        + (f'<b>{", ".join(d["id"] for d in dev_outside)}</b> is a partial deviation with no requirement in the brain ({E(dev_outside[0]["ref"].split(",")[0])}: '
           f'{E(dev_outside[0]["does"])}), so this report cannot show it.' if dev_outside else '')
        + '</p>' + dev_table)) \
    + section('Every requirement', (
        '<p>Grouped by milestone and epic; open an epic to see its stories. Footprint and tests expand to their names; hover a journey id for its name. '
        '"All 11" means every journey reached it. Highlighted rows are partial or without proof.</p>' + ''.join(full))) \
    + f'<section class="cols"><div><h2>How this was made</h2>{how}</div><div><h2>Limits</h2>{limits}</div></section>'

EXTRA = '''
.ms { display: grid; grid-template-columns: minmax(170px, 250px) 1fr; gap: 18px 20px; margin-top: 14px; align-items: center; }
.msname { display: grid; gap: 2px; font-size: 14px; }
.msbars { display: grid; gap: 6px; min-width: 0; }
.msbars .row { display: grid; grid-template-columns: 56px minmax(120px, 1fr) minmax(0, 300px); gap: 10px; align-items: center; }
.msbars .k { font: 600 11px/1 var(--f-body); letter-spacing: .05em; text-transform: uppercase; color: var(--muted); }
.track { height: 16px; }
.fill { display: flex; gap: 2px; height: 100%; min-width: 4px; border-radius: 3px; overflow: hidden; }
.fill i { display: block; height: 100%; min-width: 3px; }
.cnt { font: 12px/1.3 var(--f-mono); color: var(--muted); }
.cnt b.bad { color: var(--bad); }
.legend i { vertical-align: -1px; }
h3.gh { margin-top: 30px; }
h3.msh { margin: 26px 0 8px; font-size: 18px; }
h3.msh .muted { font-weight: 400; font-size: 14px; }
details.ep > summary { padding: 6px 0; }
details.ep > summary .tag { margin-left: 4px; }
details.ep[open] > summary { margin-bottom: 6px; }
table.req td { font-size: 13.5px; }
table.req td:nth-child(7) { min-width: 180px; }
details.mini { border: 0; padding: 0; }
details.mini > summary { font-weight: 400; font-family: var(--f-mono); font-size: 12.5px; white-space: nowrap; }
details.mini ul { margin: 4px 0 0; padding-left: 16px; font-size: 12px; }
details.mini code { font-size: 11.5px; }
.jt { display: inline-block; font: 600 11px/1 var(--f-mono); background: var(--code); color: var(--brand); padding: 3px 5px; border-radius: 3px; margin: 0 2px 3px 0; cursor: help; }
.scr { white-space: nowrap; }
.eyebrow { line-height: 1.4; }
td.note { min-width: 240px; }
table.req td:nth-child(2) { min-width: 180px; }
.kpi .v small.of { color: var(--muted); font-weight: 400; font-size: 17px; }
td:first-child code { white-space: nowrap; }
.bar.good i { background: var(--good-bg); border-right: 3px solid var(--good); }
.bar.warn i { background: var(--warn-bg); border-right: 3px solid var(--warn); }
.bar.bad i { background: var(--bad-bg); border-right: 3px solid var(--bad); }
.bar span { line-height: 16px; }
i.nr { background: repeating-linear-gradient(135deg, var(--none-bg) 0 4px, var(--line) 4px 6px) !important; }
.bar span { white-space: nowrap; }
@media (max-width: 720px) {
  .ms { grid-template-columns: 1fr; gap: 8px; }
  .msbars { margin-bottom: 10px; }
  .msbars .row { grid-template-columns: 52px 1fr; }
  .msbars .row .cnt { grid-column: 2; }
}
'''

write(OUT, page(title='GitPizza Traceability', eyebrow=f'GitPizza · requirements traceability · {DATE}',
                lede=lede, body=body, current='traceability', extra_css=EXTRA))
