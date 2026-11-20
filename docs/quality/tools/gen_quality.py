#!/usr/bin/env python3
"""Scored quality report (HTML) from mxcli's lint score.

    ./mxcli report -p GitPizza.mpr --format json --output docs/reports/raw/quality.json
    ./mxcli lint -p GitPizza.mpr --list-rules -q > docs/quality/data/lint-rules.txt
    python3 docs/quality/tools/gen_quality.py                    # -> docs/quality/report.html

Every number comes from data: docs/reports/raw/quality.json (the scored report: categories,
246 findings), docs/quality/data/lint-rules.txt (rule descriptions) and
docs/quality/data/score-runs.json (the same report scoped per module, run on a scratch copy of
the project, which pins down how the overall score weighs the categories). The rule-to-category
map, the category weights and the verdicts are written here by hand; asserts stop the build
when the counts or the score no longer follow from them. The prose is by hand, from that data.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools'))
from report_kit import E, page, kpis, section, table, bar, stack, finding, write  # noqa: E402

DOCS = os.path.join(HERE, '..', '..')
Q = json.load(open(os.path.join(DOCS, 'reports', 'raw', 'quality.json')))
RUNS = json.load(open(os.path.join(HERE, '..', 'data', 'score-runs.json')))['runs']
OUT = os.path.join(HERE, '..', 'report.html')
V = Q['violations']

# ---------------------------------------------------------------- rule descriptions (mxcli lint --list-rules)
RULE_DESC = {}
for m in re.finditer(r'^\s+(\S+) \(([^)]*)\) - (.+)$', open(os.path.join(HERE, '..', 'data', 'lint-rules.txt')).read(), re.M):
    RULE_DESC[m.group(1)] = (m.group(2), m.group(3))

# ---------------------------------------------------------------- scoring
PTS = {'error': 10, 'warning': 3, 'info': 1}
# The report puts each rule in one of seven categories; the JSON does not say which, so the map is
# fixed here and checked against the per-category counts below.
RULE_CAT = {
    'SEC007': 'Security', 'SEC001': 'Security', 'SEC004': 'Security', 'SEC006': 'Security', 'SEC010': 'Security',
    'CONV007': 'Security', 'CONV008': 'Security',
    'MPR006': 'Quality', 'CONV009': 'Quality', 'QUAL003': 'Quality', 'QUAL001': 'Quality', 'CONV014': 'Quality',
    'CONV015': 'Quality', 'QUAL004': 'Quality',
    'ARCH003': 'Architecture', 'ARCH001': 'Architecture',
    'CONV011': 'Performance',
    'DESIGN001': 'Design', 'CONV013': 'Design',
    'MPR008': 'Other', 'MPR010': 'Other', 'MDL-FLOW01': 'Other', 'MPR017': 'Other',
}
# Overall = weighted mean of the category scores (weights renormalised over the categories present).
# Reproduced exactly on six runs (whole app + each module, data/score-runs.json); a plain mean gives 54.0.
WEIGHT = {'Security': 25, 'Quality': 20, 'Architecture': 15, 'Performance': 15, 'Naming': 10, 'Design': 10, 'Other': 5}
CAT_ORDER = [c['name'] for c in Q['categories']]
CATS = {c['name']: c for c in Q['categories']}


def cat_score(e, w, i):
    return max(0, 100 - 10 * e - 3 * w - i)


def overall(scores):
    tw = sum(WEIGHT[k] for k in scores)
    return sum(WEIGHT[k] * s for k, s in scores.items()) / tw


for r in RUNS:
    assert abs(round(overall(r['categories']) + 1e-9, 1) - r['overallScore']) < 0.051, f'weights do not reproduce {r["scope"]}'
for v in V:
    assert v['ruleId'] in RULE_CAT, f'new rule {v["ruleId"]}: add it to RULE_CAT'
    v['cat'] = RULE_CAT[v['ruleId']]
for c in Q['categories']:
    cnt = Counter(v['severity'] for v in V if v['cat'] == c['name'])
    assert (cnt['error'], cnt['warning'], cnt['info']) == (c['errors'], c['warnings'], c['infos']), f'rule map wrong for {c["name"]}'
    assert cat_score(c['errors'], c['warnings'], c['infos']) == c['score'], f'scoring rule wrong for {c["name"]}'
SCORES = {c: CATS[c]['score'] for c in CAT_ORDER}
assert abs(overall(SCORES) - Q['overallScore']) < 0.051
PLAIN_MEAN = sum(SCORES.values()) / len(SCORES)

# ---------------------------------------------------------------- normalise locations
for v in V:
    mod, doc = v['module'], v['document']
    if mod and doc.startswith(mod + '.'):
        doc = doc[len(mod) + 1:]
    v['doc'] = doc
    v['where'] = f'{mod}.{doc}' if mod else 'Project security'
    v['kind'] = v['documentType'].lower()
    m = re.search(r"'([^']+)'", v['message'])
    v['widget'] = m.group(1) if m else ''

# ---------------------------------------------------------------- verdicts
# Accepted = covered by a recorded decision (docs/brain or docs/reports/security-annotations.yaml);
# by design = a reason in FINDINGS.md or the brain that is not a decision about this rule;
# tool limit = the finding is about mxcli, not the app; fix = worth changing.
POLL = {'liveHome', 'menuPoll', 'payPoll', 'trkPoll', 'apPoll', 'confPoll', 'shellPoll'}  # class gp-poll (DESCRIBE PAGE)
VIEW_MODELS = {'Cart', 'CartLine', 'CheckoutForm', 'HomeView', 'TrackView', 'Choice', 'SimulationSettings', 'StoreSettings'}
WHY = {
    'sec007': 'Allergen and StoreSettings are public reference data (allergen notice, store name and address). Brain decision <code>3bcac0</code>.',
    'conv007': 'The same two public entities; triaged as accepted in <code>security-annotations.yaml</code>.',
    'sec001': 'Server-only entities: no access rule means no client access (<code>security-annotations.yaml</code>); the guest read on Coupon was removed on purpose (brain <code>968fd2</code>).',
    'sec004': 'The shop has no sign-in: every visitor is the anonymous user role (brain <code>1b8578</code>).',
    'sec006': 'SimCustomer is a simulated person, server-only (<code>security-annotations.yaml</code>).',
    'sec010': 'The list views show only the rows the guest\'s XPath allows, their own cart (<code>security-annotations.yaml</code>).',
    'conv008': 'The built-in Administrator holds the same Guest module roles instead of unconstrained reads (brain <code>1b8578</code>).',
    'arch001': 'A page about one product (ItemInfo) and the toast list, which has no context object to refresh it (brain <code>2d759f</code>).',
    'qual004_url': 'Opened by URL and by the client error hook, which the reference graph does not see (brain <code>5ae203</code>).',
    'qual004_fix': '<code>DS_Product_Recipe</code> is unused since performance fix F4; re-anchor US-026, then delete it (brain <code>da951c</code>).',
    'mpr006_poll': 'Hidden refresh targets the live-update poller clicks every 2 s (brain <code>2be98e</code>).',
    'mpr006_deco': 'CSS-drawn decoration and state cells: the home pixel board, terminal dots, cursors, glows (FINDINGS.md).',
    'size_seed': 'Generated demo-data flows (<code>SEED_*</code>, brain <code>128ecd</code>); the generator, not the flow, is the source.',
    'size_fix': 'Hand-written flows over the limits; <code>SUB_Track_Fill</code> (184 activities) is the named next refactor in FINDINGS.md.',
    'arch003': 'Carts, toasts, settings and view models are per-session or singleton objects; order children are identified through their order (FINDINGS.md).',
    'design_vm': 'View models and settings mirror one screen or one settings form each (FINDINGS.md).',
    'design_dom': 'Domain entities a few attributes over 10; <code>Product</code>\'s width is mostly stored card values (brain <code>da951c</code>).',
    'design_order': '<code>Fulfilment.Order</code> has 51 attributes and is read and written by flows in three modules; splitting it is real work.',
    'conv011_sim': 'Simulator steps commit per courier or order over a handful of objects per tick; FINDINGS.md: "the others are bounded".',
    'conv011_shop': 'Shop flows commit per cart line; <code>SUB_Cart_Recalculate</code> is open performance finding F6.',
    'conv015': 'No decision records why entity validation rules were kept; the rule set prefers <code>VAL_</code> microflows.',
    'conv014': '<code>SIM_Tick</code> and <code>SIM_ClockRun</code> continue past a failing step on purpose, so one broken step cannot stop the simulator, but nothing is logged: keep going, and log the error.',
    'conv013': 'The clock\'s Java action rolls back on error and the minutely watchdog restarts the clock (brain <code>1ee26b</code>).',
    'mpr008': '<code>mxcli layout flows</code> does not move loop boxes (FINDINGS.md); only the diagram is affected.',
    'mpr017': 'Nothing in the app sets <code>IsActive</code> to false on coupons, options or delivery zones, so the branch that checks it never runs. Open decision: add a back-office switch, or record that the switch is only changed in the database.',
    'mpr010': 'Forms are laid out by the prototype\'s CSS ported into the theme (brain <code>e95c42</code>), not by a layout grid.',
    'flow01': 'The flow runs; mxcli\'s DESCRIBE cannot render its branch shape as nested if/else.',
}


def verdict(v):
    r, d = v['ruleId'], v['doc']
    if r == 'SEC007': return 'accepted', 'sec007'
    if r == 'CONV007': return 'accepted', 'conv007'
    if r == 'SEC001': return 'accepted', 'sec001'
    if r == 'SEC004': return 'accepted', 'sec004'
    if r == 'SEC006': return 'accepted', 'sec006'
    if r == 'SEC010': return 'accepted', 'sec010'
    if r == 'CONV008': return 'accepted', 'conv008'
    if r == 'ARCH001': return 'accepted', 'arch001'
    if r == 'QUAL004': return ('fix', 'qual004_fix') if d == 'DS_Product_Recipe' else ('accepted', 'qual004_url')
    if r == 'MPR006': return ('accepted', 'mpr006_poll') if v['widget'] in POLL else ('by design', 'mpr006_deco')
    if r in ('CONV009', 'QUAL003', 'QUAL001'): return ('by design', 'size_seed') if d.startswith('SEED_') else ('fix', 'size_fix')
    if r == 'ARCH003': return 'by design', 'arch003'
    if r == 'DESIGN001':
        if d in VIEW_MODELS: return 'by design', 'design_vm'
        return ('fix', 'design_order') if d == 'Order' else ('by design', 'design_dom')
    if r == 'CONV011': return ('fix', 'conv011_shop') if v['module'] == 'Shop' else ('by design', 'conv011_sim')
    if r == 'CONV015': return 'fix', 'conv015'
    if r == 'CONV014': return 'fix', 'conv014'
    if r == 'CONV013': return 'by design', 'conv013'
    if r == 'MPR008': return 'tool limit', 'mpr008'
    if r == 'MPR010': return 'by design', 'mpr010'
    if r == 'MPR017': return 'fix', 'mpr017'
    if r == 'MDL-FLOW01': return 'tool limit', 'flow01'
    raise KeyError(r)


for v in V:
    v['verdict'], v['why'] = verdict(v)
assert sum(1 for v in V if v['widget'] in POLL and v['ruleId'] == 'MPR006') == len(POLL), 'a poll container moved'
VERDICTS = ['fix', 'accepted', 'by design', 'tool limit']
VCLS = {'fix': 'warn', 'accepted': 'good', 'by design': 'none', 'tool limit': 'ink'}
VC = Counter(v['verdict'] for v in V)


def vtag(name, n=None):
    return f'<span class="tag {VCLS[name]}">{E(name)}{f" {n}" if n is not None else ""}</span>'


SEV = [('error', '--bad', 'error'), ('warning', '--warn', 'warning'), ('info', '--s1', 'info')]


def sev_legend():
    return '<div class="legend">' + ''.join(f'<span><i style="background:var({c})"></i>{E(lab)}</span>' for _, c, lab in SEV) + '</div>'


def pen(vs):
    return sum(PTS[v['severity']] for v in vs)


def score_without(removed_ids):
    """Overall score and category scores if the findings with these ids disappeared."""
    sc = {}
    for c in CAT_ORDER:
        vs = [v for v in V if v['cat'] == c and id(v) not in removed_ids]
        sc[c] = max(0, 100 - pen(vs))
    return overall(sc), sc


TOTAL = Q['summary']['total']
assert TOTAL == len(V)

# ---------------------------------------------------------------- 1. headline
lost = {c: WEIGHT[c] * (100 - SCORES[c]) / sum(WEIGHT.values()) for c in CAT_ORDER}
top_rule, top_n = Counter(v['ruleId'] for v in V).most_common(1)[0]
mpr006 = [v for v in V if v['ruleId'] == 'MPR006']
home_dots = sum(1 for v in mpr006 if v['doc'] == 'Home')
qual = CATS['Quality']
q_pen = 10 * qual['errors'] + 3 * qual['warnings'] + qual['infos']
q_no_mpr006 = q_pen - len(mpr006)
errs = [v for v in V if v['severity'] == 'error']
sec_acc = all(v['verdict'] == 'accepted' for v in V if v['cat'] == 'Security')
acc_overall, _ = score_without({id(v) for v in V if v['verdict'] == 'accepted'})

K = kpis([
    (f'{Q["overallScore"]:.1f}<span class="of">/100</span>',
     f'A weighted mean of seven categories. Of the {100 - Q["overallScore"]:.1f} points lost, Quality at 0 costs {lost["Quality"]:.1f} and Security {lost["Security"]:.1f}; '
     f'a plain mean would read {PLAIN_MEAN:.1f}.', 'warn'),
    (f'{len(errs)} errors',
     f'Both <code>SEC007</code>: <code>{E(errs[0]["where"])}</code> and <code>{E(errs[1]["where"])}</code> are readable by every guest. Public reference data, '
     f'accepted in a recorded decision; still {10 * len(errs)} Security points, {10 * len(errs) * WEIGHT["Security"] / 100:.1f} overall.', 'good'),
    (f'{top_rule} × {top_n}',
     f'The most frequent rule ({top_n * 100 // TOTAL}% of all findings) is an empty container: {home_dots} on Home alone, CSS-drawn dots and pixels, and '
     f'{len(POLL)} live-update targets. Without any of them Quality would still be 0.', None),
    (f'{VC["accepted"]} of {TOTAL}',
     f'Findings covered by a recorded decision; {VC["by design"]} more are by design and {VC["tool limit"]} a tool limit, which leaves {VC["fix"]} worth fixing. '
     f'The score counts them all the same.', None),
])

# ---------------------------------------------------------------- 2. categories
SCALE = 250
cat_rows = []
for c in sorted(CAT_ORDER, key=lambda c: -lost[c]):
    cc = CATS[c]
    p = 10 * cc['errors'] + 3 * cc['warnings'] + cc['infos']
    below = max(0, p - 100)
    segs = ''.join(f'<i style="width:{pts / SCALE * 100:.2f}%;background:var({col})" title="{E(lab)}: {pts} points"></i>'
                   for pts, col, lab in ((10 * cc['errors'], '--bad', f'{cc["errors"]} errors'), (3 * cc['warnings'], '--warn', f'{cc["warnings"]} warnings'),
                                         (cc['infos'], '--s1', f'{cc["infos"]} info')) if pts)
    pen_bar = (f'<div class="pen"><div class="segs">{segs}</div><b class="floor" style="left:{100 / SCALE * 100:.1f}%"></b></div>'
               f'<span class="rng">{p} points{f" · {below} below the floor" if below else (" · none" if not p else f" · {100 - p} above the floor")}</span>')
    st = 'good' if cc['score'] >= 80 else 'warn' if cc['score'] >= 50 else 'bad'
    vs = [v for v in V if v['cat'] == c]
    vsum = ' '.join(vtag(k, n) for k in VERDICTS if (n := sum(1 for v in vs if v['verdict'] == k)))
    cat_rows.append([f'<b>{E(c)}</b>', bar(cc['score'], st, f'{cc["score"]}').replace('<span style="left:6px">', '<span class="in" style="left:6px">'), f'{WEIGHT[c]}%', f'{lost[c]:.1f}',
                     str(cc['errors']), str(cc['warnings']), str(cc['infos']), (pen_bar, 'penc'), vsum or '<span class="muted">—</span>'])
cat_table = table([('Category', ''), ('Score', ''), ('Weight', 'num'), ('Overall lost', 'num'), ('Errors', 'num'), ('Warnings', 'num'), ('Info', 'num'),
                   ('Penalty against the 100-point floor', ''), ('Verdicts', '')], cat_rows, cls='cats')

runs_rows = [[E(r['scope']), str(r['findings']), ' · '.join(f'{k[:4]} {s}' for k, s in r['categories'].items()), f'{r["overallScore"]:.1f}',
              f'{overall(r["categories"]):.2f}', f'{sum(r["categories"].values()) / len(r["categories"]):.1f}'] for r in RUNS]
runs_table = table([('Scope', ''), ('Findings', 'num'), ('Category scores', ''), ('Reported', 'num'), ('Weighted', 'num'), ('Plain mean', 'num')], runs_rows, cls='small')

# ---------------------------------------------------------------- 3. rules
by_rule = defaultdict(list)
for v in V:
    by_rule[v['ruleId']].append(v)
rule_sections = []
for c in sorted(CAT_ORDER, key=lambda c: -lost[c]):
    rules = sorted({r for r, vs in by_rule.items() if vs[0]['cat'] == c}, key=lambda r: (-pen(by_rule[r]), r))
    if not rules:
        continue
    rows = []
    for r in rules:
        vs = by_rule[r]
        name, desc = RULE_DESC.get(r, ('', ''))
        whys = []
        for (vd, w), n in sorted(Counter((v['verdict'], v['why']) for v in vs).items(), key=lambda x: VERDICTS.index(x[0][0])):
            whys.append(f'<div class="why">{vtag(vd, n)} {WHY[w]}</div>')
        docs = Counter(v['where'] for v in vs).most_common(3)
        more = len({v['where'] for v in vs}) - len(docs)
        top = '<br>'.join(f'<code>{E(d).replace(".", ".<wbr>")}</code>{f" ×{n}" if n > 1 else ""}' for d, n in docs) + (f'<span class="rng">+ {more} more</span>' if more > 0 else '')
        rows.append([f'<code class="rid">{E(r)}</code><span class="rng">{E(name)}</span>', E(desc), f'<span class="sev {vs[0]["severity"]}">{vs[0]["severity"]}</span>',
                     str(len(vs)), str(pen(vs)), ''.join(whys), top])
    cc = CATS[c]
    rule_sections.append(f'<h3 class="cath">{E(c)} <span class="muted">· score {cc["score"]} · {cc["total"]} findings</span></h3>'
                         + table([('Rule', ''), ('What it checks', ''), ('Severity', ''), ('Count', 'num'), ('Points', 'num'), ('Verdict and why', ''), ('Top documents', '')],
                                 rows, cls='rules'))
naming = CATS.get('Naming')

# ---------------------------------------------------------------- 4. where
MODS = ['Simulation', 'Shop', 'Fulfilment', 'Catalog', 'Core', '']
by_mod = defaultdict(list)
for v in V:
    by_mod[v['module']].append(v)
assert set(by_mod) <= set(MODS)
mx = max(len(vs) for vs in by_mod.values())
mod_rows = []
for m in sorted(by_mod, key=lambda m: -len(by_mod[m])):
    vs = by_mod[m]
    sc = Counter(v['severity'] for v in vs)
    st = stack([(sc[s], col, lab) for s, col, lab in SEV])
    lab = ' · '.join(f'{sc[s]} {lab}' for s, _, lab in SEV if sc[s])
    vsum = ' '.join(vtag(k, n) for k in VERDICTS if (n := sum(1 for v in vs if v['verdict'] == k)))
    mod_rows.append([f'<b>{E(m or "Project")}</b>', str(len(vs)), (f'<div style="width:{len(vs) / mx * 100:.1f}%" class="sw">{st}</div><span class="rng">{lab}</span>', 'stk'), vsum])
mod_table = table([('Module', ''), ('Findings', 'num'), ('By severity', ''), ('Verdicts', '')], mod_rows, cls='mods')

doc_count = Counter(v['where'] for v in V)
doc_rows = []
for d, n in doc_count.most_common(10):
    vs = [v for v in V if v['where'] == d]
    rules = ', '.join(f'{r} ×{k}' if k > 1 else r for r, k in Counter(v['ruleId'] for v in vs).most_common())
    vsum = ' '.join(vtag(k, c) for k in VERDICTS if (c := sum(1 for v in vs if v['verdict'] == k)))
    doc_rows.append([f'<code>{E(d)}</code><span class="rng">{E(vs[0]["kind"])}</span>', str(n), str(pen(vs)), E(rules), vsum])
doc_table = table([('Document', ''), ('Findings', 'num'), ('Points', 'num'), ('Rules', ''), ('Verdicts', '')], doc_rows, cls='docs')
top10_share = sum(n for _, n in doc_count.most_common(10))

# ---------------------------------------------------------------- 5. recommendations (computed)
base = Q['overallScore']


def gain(pred):
    ids = {id(v) for v in V if pred(v)}
    o, sc = score_without(ids)
    return o - base, sc, len(ids)


def fmt_delta(x):
    return f'+{x:.1f}' if x >= 0.05 else ('±0' if abs(x) < 0.05 else f'{x:.1f}')


recs = []
g, sc, n = gain(lambda v: v['ruleId'] == 'CONV011' and v['verdict'] == 'fix')
g_all, sc_all, n_all = gain(lambda v: v['ruleId'] == 'CONV011')
recs.append(('fix', fmt_delta(g_all), f'Commit once after the loop: {n_all} commits in loops, Performance {SCORES["Performance"]} → {sc_all["Performance"]}',
             f'<p>Every Performance finding is <code>CONV011</code>. The {n} in Shop (<code>SUB_Cart_Recalculate</code>, <code>SUB_Order_Place</code>) are the ones a guest waits for '
             f'and the cheapest to fix: collect the lines in a list and commit it once. That alone gives {fmt_delta(g)} overall (Performance {sc["Performance"]}). '
             f'The other {n_all - n} are in the simulator\'s <code>SIM_Couriers</code>, <code>SIM_Kitchen</code> and <code>SIM_Pickups</code>; bounded, but the same change. '
             f'Each removed warning is 3 Performance points, {3 * WEIGHT["Performance"] / 100:.2f} overall.</p>'))

q_ids = lambda pred: [v for v in V if v['cat'] == 'Quality' and pred(v)]
q_fix = q_ids(lambda v: v['verdict'] == 'fix')
q_deco = q_ids(lambda v: v['ruleId'] == 'MPR006' and v['verdict'] == 'by design')
q_after_fix = q_pen - pen(q_fix)
q_after_both = q_after_fix - pen(q_deco)
g_q, sc_q, _ = gain(lambda v: v['cat'] == 'Quality' and (v['verdict'] == 'fix' or (v['ruleId'] == 'MPR006' and v['verdict'] == 'by design')))
size_docs = Counter(v['where'] for v in q_fix if v['ruleId'] in ('QUAL003', 'QUAL001', 'CONV009'))
recs.append(('fix', fmt_delta(g_q), f'Quality needs two kinds of work before it moves off 0',
             f'<p>Quality carries {q_pen} penalty points against a floor of 100. Fixing every Quality finding marked <i>fix</i> — splitting the {len(size_docs)} long or complex '
             f'hand-written microflows, logging in <code>SIM_Tick</code>, moving the entity validation rules to <code>VAL_</code> flows and deleting <code>DS_Product_Recipe</code>, '
             f'{len(q_fix)} findings and {pen(q_fix)} points — leaves {q_after_fix}: still 0. Removing the {len(q_deco)} decorative containers alone leaves '
             f'{q_pen - pen(q_deco)}: still 0. Both together leave {q_after_both}, Quality {sc_q["Quality"]}, <b>{fmt_delta(g_q)} overall</b>. Decoration can move to CSS '
             f'pseudo-elements on the parent (<code>::before</code>/<code>::after</code>, or a repeating gradient for the {sum(1 for v in q_deco if v["widget"].startswith("px"))}-cell pixel board) '
             f'without changing what the page looks like; the visual comparison with the prototype has to be re-run.</p>'
             f'<p class="note">Splitting is counted as removing the finding. A split flow can itself still exceed 15 activities (<code>CONV009</code>), so this is the upper end.</p>'))

acts = {v['where']: int(re.search(r'has (\d+) activities', v['message']).group(1)) for v in q_fix if v['ruleId'] == 'QUAL003'}
top_split = max(acts, key=acts.get)
cplx = {v['where']: int(re.search(r'complexity (\d+)', v['message']).group(1)) for v in q_fix if v['ruleId'] == 'QUAL001'}
g_s, sc_s, n_s = gain(lambda v: v['where'] == top_split and v['ruleId'] in ('QUAL003', 'QUAL001', 'CONV009'))
recs.append(('fix', fmt_delta(g_s), f'Split <code>{E(top_split)}</code> first anyway',
             f'<p>On its own a split moves nothing while Quality is below its floor ({n_s} findings, {fmt_delta(g_s)} overall). It is still the first refactor FINDINGS.md names: '
             f'{acts[top_split]} activities and complexity {cplx.get(top_split, "—")} that fill one view model.'
             f' Each hand-written long flow typically carries <code>QUAL003</code> + <code>QUAL001</code> + <code>CONV009</code>, '
             f'7 points; the ones with all three are {", ".join(f"<code>{E(d)}</code>" for d, k in size_docs.most_common() if k == 3)}.</p>'))

g_m, sc_m, n_m = gain(lambda v: v['ruleId'] == 'MPR010')
g_8, _, n_8 = gain(lambda v: v['ruleId'] == 'MPR008')
recs.append(('by design', fmt_delta(g_m + g_8), 'Other: five forms and three loop boxes',
             f'<p>Wrapping the {n_m} form data views in a layout grid (<code>MPR010</code>) gives {fmt_delta(g_m)} overall but fights the ported prototype CSS that lays the forms out now; '
             f'only worth it if the visual comparison stays within budget. The {n_8} loop-box overlaps (<code>MPR008</code>, {fmt_delta(g_8)}) need hand-set <code>@position</code> values '
             f'until <code>mxcli layout flows</code> moves loop boxes. Other weighs 5%, so the whole category is worth {lost["Other"]:.1f} points.</p>'))

g_o, sc_o, _ = gain(lambda v: v['ruleId'] == 'DESIGN001' and v['doc'] == 'Order')
recs.append(('by design', fmt_delta(g_o), 'Do not split entities for the score',
             f'<p>Design is {CATS["Design"]["warnings"]} warnings at 3 points and a 10% weight: {3 * WEIGHT["Design"] / 100:.1f} overall per entity. Splitting <code>Fulfilment.Order</code> '
             f'(51 attributes) is the only candidate with a reason beyond the score, and it is a change to the most-used entity in the app (the architecture report\'s published contract).</p>'))

g_a, sc_a, n_a = gain(lambda v: v['ruleId'] == 'ARCH003')
g_sec, sc_sec, n_sec = gain(lambda v: v['cat'] == 'Security')
recs.append(('accepted', f'{fmt_delta(g_a + g_sec)}', 'The two biggest levers are decisions, not defects (together)',
             f'<p>Adding a business key to the {n_a} entities <code>ARCH003</code> lists would raise Architecture to {sc_a["Architecture"]} and the overall by {fmt_delta(g_a)} — the largest '
             f'single rule — but the keys would identify carts, toasts and view models nobody looks up. Security is {SCORES["Security"]} although every one of its {n_sec} findings is covered by a '
             f'recorded decision ({fmt_delta(g_sec)} if they counted). The score does not read <code>security-annotations.yaml</code> or the brain, so it will stay there; '
             f'read it as {acc_overall:.1f} with the recorded decisions honoured.</p>'))

recs.insert(0, recs.pop(1))
rec_html = '<div class="findings">' + ''.join(
    finding(t, VCLS[k] if k != 'by design' else 'none', {'fix': 'Recommended', 'by design': 'Weigh first', 'accepted': 'No change'}[k], title, body)
    for k, t, title, body in recs) + '</div>'

# ---------------------------------------------------------------- page
lede = (f'What <code>mxcli report</code> scores, why it lands at {Q["overallScore"]:.1f}, and which of its {TOTAL} lint findings are worth acting on. '
        f'Each finding is matched against the project\'s recorded decisions and given a verdict; the recommendations say exactly how far each change would move the score.')

cats_sec = section('Categories', (
    f'<p>Each category starts at 100 and loses 10 points per error, 3 per warning and 1 per info, floored at 0. The bar on the right is that penalty on one scale, with the floor '
    f'marked: Quality is {q_pen - 100} points beyond it, so its 0 says nothing about how far it is from moving. The overall score is not the plain mean of the seven ({PLAIN_MEAN:.1f}) '
    f'but a weighted one, with Security at 25% and Other at 5%; "overall lost" is what each category costs the headline.</p>'
    + sev_legend() + f'<div class="panel">{cat_table}</div>'
    + f'<details><summary>How the weights were found</summary><p>The JSON gives the overall score but not its formula. The same report run per module on a scratch copy of the project '
      f'gives six scorings of the same rules; weights of {", ".join(f"{k} {w}" for k, w in WEIGHT.items())}, renormalised over the categories a run has, reproduce all six to the decimal.</p>'
      f'{runs_table}</details>'))

rules_sec = section('Rules', (
    f'<p>{len(by_rule)} rules fired, grouped by the category they score in, heaviest first. "Points" is what the rule costs its category. A verdict says what to do with each finding: '
    f'{vtag("fix")} worth changing, {vtag("accepted")} covered by a recorded decision (brain or security triage), {vtag("by design")} explained in FINDINGS.md or the brain but not '
    f'decided for this rule, {vtag("tool limit")} about mxcli rather than the app. Naming scores {naming["score"] if naming else "—"} with no findings because the project declares its '
    f'own prefixes in <code>.claude/lint-config.yaml</code> and switches off three naming rules (<code>CONV003</code>/<code>004</code>/<code>005</code>: page, enumeration and snippet names), '
    f'each with its reason. It also switches off <code>CONV002</code> (attribute default values), which lint files under <i>quality</i>; the brain\'s "no quality rule was switched off" '
    f'is not quite right, though at Quality 0 it changes nothing.</p>' + ''.join(rule_sections)))

where_sec = section('Where they are', (
    f'<p>Shop has {len(by_mod["Shop"])} of the {TOTAL}, and {sum(1 for v in by_mod["Shop"] if v["ruleId"] == "MPR006")} of those are empty containers on its pages. '
    f'The ten busiest documents hold {top10_share} findings ({top10_share * 100 // TOTAL}%); Home alone has {doc_count["Shop.Home"]}, all decoration and one poll target. '
    f'"Project" is the security settings, which belong to no module.</p>'
    + '<h3>Findings per module</h3>' + sev_legend() + f'<div class="panel">{mod_table}</div>'
    + f'<h3 class="gap">The ten documents with the most findings</h3><div class="panel">{doc_table}</div>'))

rec_sec = section('Recommendations', (
    f'<p>Computed from the scoring rule and the weights above: the number in the tag is the change in the overall score if those findings disappeared and nothing else changed. '
    f'Quality is the trap — at {q_pen} points, no single change moves it.</p>' + rec_html))

how = (f'<p><code>mxcli report --format json</code> for the scored report ({E(Q["date"])}, <code>docs/reports/raw/quality.json</code>) and <code>mxcli lint --list-rules</code> for the '
       f'rule descriptions (<code>docs/quality/data/lint-rules.txt</code>). The per-module runs that pin down the weighting were made on a scratch copy of the project and are kept in '
       f'<code>docs/quality/data/score-runs.json</code>. Which category each rule scores in is fixed in <code>tools/gen_quality.py</code> and checked against the report\'s own counts; '
       f'the verdicts are written there by hand from <code>docs/brain/</code>, <code>docs/reports/security-annotations.yaml</code>, <code>.claude/lint-config.yaml</code> and FINDINGS.md, '
       f'and the poll containers were identified from <code>DESCRIBE PAGE</code> (class <code>gp-poll</code>).</p>')
limits = ('<p>The weighting is inferred, not documented: it fits six runs exactly but could differ for a category mix not seen here. The score counts a finding the same whether or not '
          'it is accepted; the verdicts here are this page\'s reading and change nothing in mxcli. Recommendations assume a finding disappears cleanly; a split microflow can raise '
          'new findings of its own. Lint sees the model only: it does not know how often a flow runs or what a page looks like, so a removed container still needs the visual '
          'comparison, and a commit moved out of a loop still needs the tests.</p>')

body = (K + cats_sec + rules_sec + where_sec + rec_sec
        + f'<section class="cols"><div><h2>How this was made</h2>{how}</div><div><h2>Limits</h2>{limits}</div></section>')

EXTRA = r'''
.legend { margin: 4px 0 10px; }
.pen { position: relative; height: 16px; min-width: 220px; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; }
.pen .segs { position: absolute; inset: 0; display: flex; gap: 1px; overflow: hidden; border-radius: 2px; }
.pen .segs i { display: block; height: 100%; }
.pen .floor { position: absolute; top: -4px; bottom: -4px; width: 2px; background: var(--ink); }
.pen .floor::after { content: "floor"; position: absolute; top: -13px; left: 4px; font: 600 10px/1 var(--f-mono); color: var(--muted); }
table.cats td { vertical-align: middle; }
table.cats td.penc { min-width: 260px; padding-top: 16px; }
table.small td, table.small th { font-size: 13px; padding: 6px 8px; }
h3.cath { margin: 26px 0 8px; font-size: 18px; }
h3.cath .muted { font-weight: 400; font-size: 14px; }
table.rules td { font-size: 13.5px; }
table.rules td:nth-child(2) { color: var(--muted); }
code.rid { font-weight: 700; font-size: 13px; white-space: nowrap; }
.why { margin-bottom: 6px; } .why .tag { margin-right: 4px; }
.sev { font: 700 11px/1 var(--f-mono); text-transform: uppercase; letter-spacing: .03em; }
.sev.error { color: var(--bad); } .sev.warning { color: var(--warn); } .sev.info { color: var(--s1); }
td .tag { margin: 0 2px 3px 0; }
table.mods td.stk { min-width: 200px; width: 50%; }
table.mods .sw .stack { min-width: 0; }
table.docs td:nth-child(4) { font-size: 12.5px; color: var(--muted); }
.cols.wide { grid-template-columns: repeat(auto-fit, minmax(min(460px, 100%), 1fr)); }
.finding > .tag { font-size: 12px; }
.kpi .v .of { color: var(--muted); font-weight: 400; font-size: 19px; margin-left: 2px; }
h3.gap { margin-top: 22px; }
.bar span.in { color: var(--c-label); }
table.rules { table-layout: fixed; min-width: 1000px; }
table.rules th:nth-child(1) { width: 15%; } table.rules th:nth-child(2) { width: 19%; } table.rules th:nth-child(3) { width: 8%; }
table.rules th:nth-child(4) { width: 6%; } table.rules th:nth-child(5) { width: 6%; } table.rules th:nth-child(6) { width: 28%; } table.rules th:nth-child(7) { width: 18%; }
table.rules td:nth-child(7) code { white-space: normal; }
table.cats tr:not(:first-child) .floor::after { content: none; }
table.mods td:nth-child(4) .tag, table.docs td:nth-child(5) .tag { margin-bottom: 3px; }
details summary { margin: 10px 0 4px; }
'''

write(OUT, page('GitPizza Quality Score', eyebrow='GitPizza · quality score · 19 November 2026', lede=lede, body=body, current='quality', extra_css=EXTRA))
print(f'overall {Q["overallScore"]} (plain mean {PLAIN_MEAN:.1f}); verdicts {dict(VC)}; honoured decisions {acc_overall:.1f}')
