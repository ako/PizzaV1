#!/usr/bin/env python3
"""Lay out the build-overview deck from the lane JSON that collect.py wrote.

    python3 docs/overview/collect.py && python3 docs/overview/deck.py

A Pen & Marker poster (sketch-deck skill, ako/inkscape-presenter): one swimlane board
whose lanes are lane 0 (crosscutting) and the milestones M1..M4, each lane with the
columns PRD | Decisions | Model | Proof | Status; every lane is also its own zoom frame,
and a summary frame closes the board. Writes build-overview.html (the deck page) and
frames.json (the frame batch for the deck's database). Nothing is typed in here except
layout and labels: every figure and name comes from data/*.json.
"""
import base64
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'kit'))
from pen_marker import *          # noqa: E402,F401,F403  (kit: wline, wbox, mbox, T, MT, MO, wrap, ...)
from pen_marker import E           # noqa: E402

DECK = os.path.join(HERE, 'build-overview.html')
TEMPLATE = os.path.join(HERE, 'kit', 'sketch-deck.template.html')
DATA = os.path.join(HERE, 'data')
TITLE = 'GitPizza Build Overview'
LANES = ('lane0', 'm1', 'm2', 'm3', 'm4')

W = 6600                                   # board width (canvas units); every lane is a zoom frame W wide
X0, LABEL_W = 70, 400                      # lane label column
COLS = [('PRD', 1050), ('Decisions', 1450), ('Model', 1150), ('Proof', 1300), ('Status', 930)]
GAP = 40
HEAD_Y = 0                                 # board header
LANE_TOP = 900
LANE_GAP = 90
PAD = 34
AMBER, RED_, GREEN = YEL, RED, GRN         # status colours: green built/pass, amber partial/accepted, red open/fail
FILL = {'partial': AMBER, 'deviation': AMBER, 'accepted': AMBER, 'open': RED_, 'decision': None}
SIZE = {'h': 66, 'b': 60, 'm': 50, 's': 48}


def load(name):
    return json.load(open(os.path.join(DATA, name + '.json')))


def col_x(i):
    return X0 + LABEL_W + GAP + sum(w for _, w in COLS[:i]) + GAP * i


def chars(w, size, mono=False):
    return max(8, int((w - 2 * PAD) / (size * (0.6 if mono else 0.5))))


def mono_wrap(text, n):
    """Wrap document names and paths: break long tokens after a '/' (or hard) so nothing overflows."""
    toks = []
    for t in text.split():
        while len(t) > n:
            cut = t.rfind('/', 0, n) + 1 or n
            toks.append(t[:cut]); t = t[cut:]
        toks.append(t)
    out, line = [], ''
    for t in toks:
        if line and len(line) + 1 + len(t) > n:
            out.append(line); line = t
        else:
            line = (line + ' ' + t).strip()
    return out + [line] if line else out


def lines_of(kind, text, w):
    size = SIZE[kind]
    n = chars(w, size, kind == 'm')
    return [(kind, size, ln) for ln in (mono_wrap(text, n) if kind == 'm' else wrap(text, n))]


def block(x, y, w, items, fill=None, sw=2.6):
    """A marker card at (x, y), w wide, holding items [(kind, text)]: h heading, b body,
    m mono (document names), s small muted. Returns (svg, height)."""
    rows = [r for kind, text in items if text for r in lines_of(kind, text, w)]
    h = PAD + sum(size * 1.3 for _, size, _ in rows) + PAD * 0.55
    s = mbox(x, y, w, h, fill, sw, d=8)
    yy = y + PAD
    for kind, size, ln in rows:
        yy += size * 1.05
        if kind == 'm':
            s += MO(x + PAD, yy, size, ln, INK)
        else:
            s += T(x + PAD, yy, size, ln, MUT if kind == 's' and not fill else INK, bold=(kind == 'h'))
        yy += size * 0.25
    return s, h


def stack(x, y, w, cards, gap=30):
    """Cards [(items, fill)] one under the other; returns (svg, bottom)."""
    s = ''
    for items, fill in cards:
        c, h = block(x, y, w, items, fill)
        s += c
        y += h + gap
    return s, y


def head_body(text):
    """Split a decision into a short head and its body: the part before the first colon."""
    t = text.rstrip(' …')
    m = re.match(r'^(.{3,60}?):\s+(.*)$', t)
    if m:
        return m.group(1), m.group(2) + (' …' if text.endswith('…') else '')
    words = t.split()
    return ' '.join(words[:6]), ' '.join(words[6:]) + (' …' if text.endswith('…') else '')


def clip(text, n):
    return text if len(text) <= n else text[:n].rsplit(' ', 1)[0] + ' …'


_thumbs = {}


def thumb(file, w=390):
    """A screenshot as a data URI, scaled to w px (the shots are taken at 2x)."""
    if file not in _thumbs:
        from PIL import Image
        im = Image.open(os.path.join(HERE, 'shots', file)).convert('RGB')
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=74, optimize=True)
        _thumbs[file] = ('data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(), im.width, im.height)
    return _thumbs[file]


def shots(x, y, w, items):
    """Phone screenshots side by side with their captions; returns (svg, bottom)."""
    if not items:
        return '', y
    n = len(items)
    tw = min(400, (w - (n - 1) * 34) / n)
    s, bottom = '', y
    for i, sh in enumerate(items):
        uri, iw, ih = thumb(sh['file'])
        th = tw * ih / iw
        xx = x + i * (tw + 34)
        cid = uid('shot')
        s += shadow(xx, y, tw, th, 18, 9)
        s += (f'<clipPath id="{cid}"><rect x="{xx:.1f}" y="{y:.1f}" width="{tw:.1f}" height="{th:.1f}" rx="18"/></clipPath>'
              f'<image href="{uri}" x="{xx:.1f}" y="{y:.1f}" width="{tw:.1f}" height="{th:.1f}" '
              f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>')
        s += wbox(xx, y, tw, th, 3, inner=False)
        yy = y + th + 50
        for ln in mono_wrap(clip(sh['shows'], 64), int(tw / (44 * 0.56))):
            s += T(xx + 4, yy, 44, ln, MUT)
            yy += 54
        bottom = max(bottom, yy)
    return s, bottom + 10


def col_label(i, y):
    name = COLS[i][0]
    x = col_x(i)
    return MT(x + 6, y + 70, 64, name, BRN) + swipe(x, y + 84, len(name) * 40 + 30, 16, YEL, .5)


def lane_frame_svg(lane, cols_svg, h, label_svg):
    s = f'<rect x="0" y="0" width="{W}" height="{h:.0f}" rx="26" fill="{PAPER}"/>'
    s += wbox(14, 14, W - 28, h - 28, 3.4, MUT)
    s += label_svg
    for i in range(len(COLS)):
        s += col_label(i, 40)
        if i:
            xx = col_x(i) - GAP / 2
            s += wline(xx, 70, xx, h - 60, 2, SHADOW, .9, dash='14 14')
    return s + cols_svg


def label_column(d, h, counts, color, letter):
    x, y = X0, 40
    s = mbox(x, y, LABEL_W, h - 80, color, 3, d=10)
    s += MT(x + LABEL_W / 2, y + 190, 150, letter, INK, 'middle')
    name = d['name'].split('—')[-1].strip()
    yy = y + 300
    for ln in wrap(name, 9):
        s += MT(x + LABEL_W / 2, yy, 62, ln, INK, 'middle')
        yy += 78
    yy += 40
    for txt in counts:
        for ln in wrap(txt, 11):
            s += T(x + LABEL_W / 2, yy, 62, ln, INK, 'middle', True)
            yy += 76
        yy += 16
    return s


def counts_bar(x, y, w, built, partial, open_, total, size=46):
    """A stacked bar: built (green), partial (amber), open (red), with counts beside it."""
    s = ''
    xx = x
    for n, col in ((built, GREEN), (partial, AMBER), (open_, RED_)):
        if n and total:
            ww = w * n / total
            s += hatch(xx, y, ww, 56, col, 6, .6)
            xx += ww
    s += wbox(x, y, w, 56, 2.6, inner=False)
    return s


# ------------------------------------------------------------------ lanes
def epic_cards(epics):
    out = []
    for e in epics:
        pr = e.get('priorities') or {}
        mix = ' · '.join(f'{k} {v}' for k, v in pr.items()) if len(pr) > 1 else f"{e['moscow']}"
        out.append(([('h', f"{e['id']} {e['title']}"),
                     ('b', f"{e['range'].replace(' – ', '–')} · {e['stories']} {'story' if e['stories'] == 1 else 'stories'} · {mix}"),
                     ('m', e['file'].replace('package-lite/', ''))], None))
    return out


TAG = {'partial': 'PARTLY MEETS', 'deviation': 'DEVIATION', 'accepted': 'ACCEPTED', 'open': 'OPEN'}


def decision_list(x, y, w, decs, limit):
    """Decisions as one marked list: a dot per entry, amber/red highlight for partial,
    accepted, deviating and open ones; the brain id closes each entry."""
    if not decs:
        return block(x, y, w, [('h', 'No recorded decision'), ('s', 'docs/brain has none for this milestone')])[0], y + 200
    size, lh = SIZE['b'], SIZE['b'] * 1.3
    n = chars(w - 70, size)
    rows = []
    for d in decs:
        head, body = head_body(d['text'])
        tag = TAG.get(d['kind'])
        text = clip(f"{head}: {body}", limit)
        rows.append((d, wrap(text, n), tag))
    h = PAD + sum(len(r[1]) * lh + (lh * .8 if r[2] else 0) + 26 for r in rows) + PAD * .4
    s = mbox(x, y, w, h, None, 2.6, d=8)
    yy = y + PAD
    for d, lines, tag in rows:
        hh = len(lines) * lh + (lh * .8 if tag else 0)
        if FILL[d['kind']]:
            s += hatch(x + 46, yy - 6, w - 64, hh + 6, FILL[d['kind']], 10, .38)
        s += f'<circle cx="{x + 26}" cy="{yy + size * .55:.1f}" r="11" fill="{INK}"/>'
        if tag:
            s += T(x + 60, yy + SIZE['s'] * 1.0, SIZE['s'], f"{tag} · brain {d['id']}", INK, bold=True)
            yy += lh * .8
        for i, ln in enumerate(lines):
            s += T(x + 60, yy + size * 1.0, size, ln, INK, bold=False)
            yy += lh
        if not tag:
            s += T(x + w - 24, yy - lh + size * 1.0, SIZE['s'] * .8, d['id'], MUT, 'end')
        yy += 26
    return s, y + h + 30


def short_test(name):
    return name.split(':')[0]


def short_journey(name):
    m = re.match(r'(J\d+)\s+(.*)', name)
    return f'{m.group(1)} {clip(m.group(2), 34)}' if m else name


def milestone_lane(d, other):
    st, model, proof = d['status'], d['model'], d['proof']
    cols = []
    # PRD
    cols.append(epic_cards(d['prd']['epics']))
    # Decisions
    cols.append(('decisions', d['decisions'], 150))
    # Model
    mods = ' · '.join(f'{k} {v}' for k, v in model['modules'].items())
    mc = [([('h', f"{model['footprintMicroflows']} microflows"), ('b', mods), ('s', 'footprint of the lane\'s requirements, by module')], None)]
    if model['pages']:
        mc.append(([('h', f"{len(model['pages'])} pages"), ('m', ' '.join(model['pages']))], None))
    if model['snippets']:
        mc.append(([('h', f"{len(model['snippets'])} snippets"), ('m', ' '.join(model['snippets']))], None))
    if model['entities']:
        mc.append(([('h', 'Entities used most'), ('m', ' '.join(model['entities'][:8]))], None))
    js = model['jsActions'] + model['nanoflows']
    if js:
        mc.append(([('h', 'Client side'), ('m', ' '.join(js))], None))
    if d['lane'] == 'm3':
        mc.append(([('h', 'Background work'), ('m', ' '.join(other['lane0']['model']['scheduledEvents']
                                                          + other['lane0']['model']['taskQueues'])),
                    ('s', 'scheduled events and the clock\'s task queue')], None))
    cols.append(mc)
    # Proof (screenshots are drawn separately, above these cards)
    pc = []
    by_file = {}
    for t in proof['tests']:
        by_file.setdefault(t['file'], []).append(t)
    for f, ts in by_file.items():
        ok = all(t['passed'] for t in ts)
        pc.append(([('h', f"{len(ts)} microflow tests {'pass' if ok else 'FAIL'}"), ('m', f),
                    ('b', ', '.join(short_test(t['name']) for t in ts))], GREEN if ok else RED_))
    if not proof['tests']:
        pc.append(([('h', 'No microflow test'), ('b', 'proof is by browser journeys only')], AMBER))
    if proof['journeys']:
        passed = sum(1 for j in proof['journeys'] if j['status'] == 'passed')
        pc.append(([('h', f"{passed}/{len(proof['journeys'])} journeys pass"), ('m', 'tests/e2e/journeys.js'),
                    ('b', ' · '.join(short_journey(j['name']) for j in proof['journeys']))],
                   GREEN if passed == len(proof['journeys']) else RED_))
    cols.append(pc)
    # Status
    sc = [([('h', f"{st['built']}/{st['requirements']} built"),
            ('b', f"{st['partial']} partial · {st['changed']} changed · {st['notBuilt']} not built"),
            ('b', f"{st['proven']}/{st['requirements']} reached by a test or journey"),
            ('s', 'derived: mxcli report traceability')], GREEN if st['built'] == st['requirements'] else AMBER)]
    for g in st['gaps']:
        _, body = head_body(g['reason'] or '')
        sc.append(([('h', f"{g['title'].split()[0]} {g['status']}"), ('b', clip(g['title'].split(' ', 1)[1], 60)),
                    ('s', clip(body, 160) if g['reason'] else 'no reason recorded')], AMBER))
    if proof['untested']:
        sc.append(([('h', f"{len(proof['untested'])} not reached by any test"),
                    ('b', ', '.join(t.split()[0] for t in proof['untested'])),
                    ('s', clip('; '.join(t.split(' ', 1)[1] for t in proof['untested']), 170))], AMBER))
    cols.append(sc)
    counts = [f"{st['built']} built", f"{st['partial']} partial", f"{st['notBuilt']} open",
              ' '.join(e['id'] for e in d['prd']['epics'])]
    color = GREEN if st['built'] == st['requirements'] else AMBER
    return cols, proof['screenshots'], counts, color, d['lane'].upper()


def lane0_lane(d):
    m, p = d['model'], d['proof']
    cols = []
    cols.append([([('h', it['ref']), ('b', it['text'])], None) for it in d['prd']['items']]
                + [([('h', 'No milestones in the PRD'), ('b', 'It orders 12 epics (EP-01…EP-15). M1–M4 group them; that grouping is recorded in the brain, not in the PRD.')], AMBER)])
    cols.append(('decisions', d['decisions'], 108))
    layers = ' → '.join(f"{x['name']} L{x['layer']}" for x in m['modules'])
    nav = m['navigation'] or {}
    integ = sum(m['integrations'].values())
    cols.append([
        ([('h', '5 modules, layered'), ('b', layers), ('s', f"{m['cycles']} cycles · {m['clusters']} clusters (report architecture)")], None),
        ([('h', 'Security and roles'), ('b', 'user roles ' + ', '.join(m['userRoles'])), ('m', ' '.join(m['moduleRoles']))], None),
        ([('h', 'Navigation'), ('b', f"profile {nav.get('ProfileName')}"), ('m', f"home {nav.get('HomePage')} notfound {nav.get('NotFoundPage')}")], None),
        ([('h', 'Theme'), ('b', m['theme'])], None),
        ([('h', 'Integrations: none'), ('b', f"{integ} REST/OData services, {m['integrations']['WORKFLOWS']} workflows, {m['viewEntities']} view entities"),
          ('s', 'payment, map and kitchen are simulated in-app')], None),
        ([('h', 'Project brain'), ('b', f"{m['brain']['requirements']} requirements in {m['brain']['slices']} slices · {m['brain']['anchors']} anchors · {m['brain']['decisions']} decisions · {m['brain']['open']} open"),
          ('m', 'docs/brain/')], None),
    ])
    lint, cats, vis, cov = p['lint'], p['categories'], p['visual'], p['coverage']
    mb = p['mxbuild'] or {}
    pc = [
        ([('h', f"mxbuild: {mb.get('errors')} errors"), ('s', f"docker check, {mb.get('checkedAt')}")], GREEN if mb.get('passed') else RED_),
        ([('h', f"{p['tests']['count'] - p['tests']['failed']}/{p['tests']['count']} microflow tests · {p['journeys']['passed']}/{p['journeys']['count']} journeys"),
          ('m', ' '.join(p['tests']['files']) + ' tests/e2e/journeys.js')], GREEN),
        ([('h', f"Coverage {cov['reached']}/{cov['nonStartup']} microflows"),
          ('b', f"{round(100 * cov['reached'] / cov['nonStartup'])} % of non-startup flows reached; only {cov['byTests']} by microflow tests"),
          ('s', 'report tests')], AMBER),
        ([('h', f"Visual: {vis['withinBudget']}/{vis['screens']} within budget"),
          ('b', f"mismatch {vis['minMismatch']}–{vis['maxMismatch']} % against the prototype: not pixel-perfect"),
          ('s', f"tests/e2e/visual.js · {vis['measuredAt']}")], AMBER),
        ([('h', f"lint {lint['errors']} errors · {lint['warnings']} warnings · {lint['infos']} info"),
          ('b', f"report score {p['score']:g}/100 · " + ' · '.join(f'{k} {v}' for k, v in p['categories'].items()))], RED_ if cats.get('Quality') == 0 else AMBER),
        ([('h', f"Security: {len(p['security']['openHighMedium'])} open high/medium"),
          ('s', f"{p['security']['findings']} findings, triaged in docs/reports/security-annotations.yaml")], GREEN if not p['security']['openHighMedium'] else RED_),
    ]
    cols.append(pc)
    gaps = d['status']['gaps']
    sc = [([('h', 'No PRD stories'), ('b', 'crosscutting work: status shown as gates and open points')], None)]
    for g in gaps:
        head, body = head_body(g['text'])
        sc.append(([('h', head), ('s', clip(body, 110))], FILL[g['kind']]))
    if cats.get('Quality') == 0:
        q = p['qualityCategory']
        sc.append(([('h', 'Quality score 0'), ('s', f"{q['warnings']} warnings + {q['infos']} info floor the category; most frequent lint rules: "
                    + ', '.join(f"{r} ×{n}" for r, n in p['topRules'][:4]))], RED_))
    cols.append(sc)
    counts = [f"{len(d['decisions'])} decisions", f"{sum(1 for x in d['decisions'] if x['kind'] == 'open')} open"]
    return cols, p['screenshots'], counts, BLU, '0'


def draw_lane(lane, cols, screenshots, counts, color, letter, d):
    body, bottoms = '', []
    top = 150
    for i, cards in enumerate(cols):
        x, w = col_x(i), COLS[i][1]
        y = top
        if COLS[i][0] == 'Proof':
            sv, y = shots(x, y, w, screenshots)
            body += sv
        if isinstance(cards, tuple):
            sv, y = decision_list(x, y, w, cards[1], cards[2])
        else:
            sv, y = stack(x, y, w, cards)
        body += sv
        bottoms.append(y)
    h = max(bottoms) + 50
    label = label_column(d, h, counts, color, letter)
    return lane_frame_svg(lane, depth(0.5, body), h, label), h


# ------------------------------------------------------------------ poster and summary
def poster_svg(H, lanes_at, summary):
    s = f'<rect x="0" y="0" width="{W}" height="{H:.0f}" fill="{PAPER}"/>'
    title = 'GitPizza: from PRD to app'
    s += depth(1, swipe(X0, 330, len(title) * 118, 70) + MT(X0, 320, 230, title))
    s += T(X0, 470, 76, f"{summary['requirements']} user stories of the PRD (package-lite v1.2), built in Mendix 11.16.1 with mxcli. "
           f"{summary['built']} built, {summary['partial']} partly, {summary['notBuilt']} not built.", INK)
    s += T(X0, 570, 58, 'The PRD has no milestones: M1–M4 group its epics (recorded in docs/brain). The PRD is English, so its English domain terms are kept.', MUT)
    s += T(X0, 650, 58, f"Every figure is derived from the model and this session's runs (collected {summary['collectedAt']}).", MUT)
    xx = X0
    for txt, col in (('built / passing', GREEN), ('partial / accepted / deviation', AMBER), ('open / failing', RED_), ('recorded decision', None)):
        c, w = chip(xx, 720, txt, col or CARD, 50)
        s += c
        xx += w + 40
    for lane, (y, h) in lanes_at.items():
        s += f'<rect x="{-30}" y="{y - 30:.0f}" width="{W + 60}" height="{h + 60:.0f}" rx="40" fill="{SHADOW}" opacity=".25"/>'
    return s


SW = 4125                                 # the summary is drawn in a smaller space, so it reads larger


def summary_svg(S, data):
    H = SW * 9 / 16
    s = f'<rect x="0" y="0" width="{SW}" height="{H:.0f}" rx="20" fill="{CARD}"/>' + wbox(10, 10, SW - 20, H - 20, 3)
    s += tape(SW / 2, 10, 300, 64, -2)
    s += depth(1, swipe(70, 200, 780, 44) + MT(70, 190, 120, 'Summary'))
    s += T(70, 290, 50, f"{S['requirements']} PRD user stories: {S['built']} built, {S['partial']} partly built, "
           f"{S['notBuilt']} not built; {S['proven']} reached by a test or journey.", MUT)
    # table: one row per milestone with a stacked bar
    x, y = 70, 410
    cols = [('Stories', 1240), ('Built', 1440), ('Partial', 1640), ('Open', 1840), ('Proven', 2040)]
    s += T(x, y, 46, 'Milestone', BRN, bold=True)
    for t, dx in cols:
        s += T(x + dx, y, 46, t, BRN, 'middle', True)
    s += wline(x, y + 26, x + 2420, y + 26, 2.4)
    y += 110
    rows = S['milestones'] + [{'name': 'Total', 'requirements': S['requirements'], 'built': S['built'], 'partial': S['partial'],
                                'notBuilt': S['notBuilt'], 'proven': S['proven'], 'open': [], 'epics': []}]
    for r in rows:
        tot = r['name'] == 'Total'
        s += T(x, y, 52, r['name'].replace('—', '·'), INK, bold=True)
        for (t, dx), v in zip(cols, (r['requirements'], r['built'], r['partial'], r['notBuilt'], r['proven'])):
            s += T(x + dx, y, 54, str(v), INK, 'middle', tot)
        s += counts_bar(x + 2160, y - 40, 260,
                        r['built'], r['partial'], r['notBuilt'], r['requirements'])
        if r.get('open'):
            s += T(x + 30, y + 52, 40, 'partly built: ' + ', '.join(r['open']) + '   epics ' + ' '.join(r['epics']), BRN, bold=True)
        elif r.get('epics'):
            s += T(x + 30, y + 52, 40, 'epics ' + ' '.join(r['epics']), MUT)
        y += 140
        if not tot:
            s += wline(x, y - 70, x + 2420, y - 70, 1.4, SHADOW)
    # gates
    g, p = S['gates'], data['lane0']['proof']
    vis = p['visual']
    y += 10
    s += T(x, y, 46, 'Gates, run this session', BRN, bold=True)
    gates = [(f"mxbuild {g['mxbuild']['errors']} errors", GREEN), (f"tests {g['tests']}", GREEN), (f"journeys {g['journeys']}", GREEN),
             (f"security {len(p['security']['openHighMedium'])} open high", GREEN),
             (f"visual {vis['withinBudget']}/{vis['screens']}, ≤{vis['maxMismatch']} % off", AMBER),
             (f"lint {g['lint']['errors']} E · {g['lint']['warnings']} W · {g['lint']['infos']} I", AMBER), (f"score {g['score']:g}/100", RED_)]
    xx, yy = x, y + 30
    for t, col in gates:
        w = len(t) * 42 * .5 + 42 * 1.3
        if xx + w > x + 2420:
            xx, yy = x, yy + 100
        c, w = chip(xx, yy, t, col, 42)
        s += c
        xx += w + 24
    y = yy + 180
    s += T(x, y, 46, 'Open points', BRN, bold=True)
    pts = []
    for q in S['openQuestions']:
        pts.append(clip(q, 92))
    pts.append('Commits grouped stories instead of one "US-xxx: <title>" commit per story')
    for m in S['milestones']:
        for o in m['open']:
            pts.append(f"{o} partly built ({m['name'].split('—')[0].strip()})")
    yy = y + 70
    for ptxt in pts:
        for k, ln in enumerate(wrap(ptxt, 80)):
            if not k:
                s += cross(x + 22, yy - 16, 18, ORA)
            s += T(x + 60, yy, 44, ln, INK)
            yy += 56
        yy += 8
    # lessons
    lx, lw, ly = 2620, 1430, 410
    s += T(lx, ly, 46, 'Three lessons (FINDINGS.md)', BRN, bold=True)
    ly += 40
    for i, l in enumerate(S['lessons'], 1):
        c, h = block(lx, ly, lw, [('h', f"{i}. {l['source'].split(': ', 1)[1]}"), ('b', l['text'])], [BLU, LIL, GRN][i - 1])
        s += depth(0.5, c)
        ly += h + 40
    return s


def main():
    data = {k: load(k) for k in LANES}
    summary = load('summary')
    lanes, y = [], LANE_TOP
    for k in LANES:
        d = data[k]
        cols, sh, counts, color, letter = lane0_lane(d) if k == 'lane0' else milestone_lane(d, data)
        svg, h = draw_lane(k, cols, sh, counts, color, letter, d)
        lanes.append((k, d, svg, y, h))
        y += h + LANE_GAP
    sum_h = W * 9 / 16
    sum_y = y + 40
    H = sum_y + sum_h + 120
    lanes_at = {k: (yy, h) for k, _, _, yy, h in lanes}

    if not os.path.exists(DECK):
        import shutil
        shutil.copy(TEMPLATE, DECK)
    theme_page(DECK, TITLE)
    groups = [group('board', 'Swimlane board', poster_svg(H, lanes_at, summary), (0, 0, W, H), W)]
    frames = [('board', 0, 0, W, round(H), 10)]
    names = {'lane0': 'Lane 0 · Crosscutting'}
    for i, (k, d, svg, yy, h) in enumerate(lanes):
        title = names.get(k, d['name'].replace('—', '·'))
        groups.append(group(k, title, svg, (0, yy, W, h), W))
        frames.append((k, 0, round(yy), W, round(h), 20 + i * 10))
    groups.append(group('summary', 'Summary', summary_svg(summary, data), (0, sum_y, W, sum_h), SW))
    frames.append(('summary', 0, round(sum_y), W, round(sum_h), 80))
    inject(DECK, groups, motion='subtle')
    ops = [{'op': 'set', 'collection': 'frames', 'doc_id': f, 'data': {'x': x, 'y': yv, 'w': w, 'h': hv, 't': t}}
           for f, x, yv, w, hv, t in frames]
    ops.append({'op': 'set', 'collection': 'meta', 'doc_id': 'settings', 'data': {'cols': 4, 'grid': False}})
    json.dump(ops, open(os.path.join(HERE, 'frames.json'), 'w'), indent=1)
    print(f'wrote {os.path.relpath(DECK)} ({os.path.getsize(DECK) // 1024} KB), frames.json:')
    for f in frames:
        print('  ', f)


if __name__ == '__main__':
    main()
