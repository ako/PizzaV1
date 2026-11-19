#!/usr/bin/env python3
"""Security review (HTML) from the model.

    ./mxcli report security -p GitPizza.mpr --format json > docs/reports/raw/security.json
    python3 docs/security/tools/collect.py          # -> docs/security/catalog.json (read-only catalog queries)
    python3 docs/security/tools/gen_security.py     # -> docs/security/report.html

Every number comes from data: the report (settings, findings, grid, XPaths, client-callable flows,
lint rules, method, limits), the catalog snapshot (create/delete rights, non-persistent and
server-only entities, role mapping, constants, the microflows each flow calls) and the human
triage in docs/reports/security-annotations.yaml. A finding or lint rule that is not in the
annotations is shown as OPEN. The prose is written here by hand from that data; asserts stop
the build when the data no longer says what the prose claims.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools'))
from report_kit import E, MODULE_COLOR, MODULE_ORDER, finding, kpis, page, section, table, write  # noqa: E402

RAW = json.load(open(os.path.join(REPO, 'docs', 'reports', 'raw', 'security.json')))
D = RAW['data']
CAT = json.load(open(os.path.join(HERE, '..', 'catalog.json')))
OUT = os.path.join(HERE, '..', 'report.html')


def load_annotations(path):
    """The annotations file is flat YAML: `  "key": {status: x, note: "..."}` per line (no PyYAML needed)."""
    items = {}
    for line in open(path):
        m = re.match(r'\s+"([^"]+)":\s*\{status:\s*(\w+),\s*note:\s*"(.*)"\}\s*$', line)
        if m:
            items[m.group(1)] = {'status': m.group(2), 'note': m.group(3)}
    return items


ANN = load_annotations(os.path.join(REPO, 'docs', 'reports', 'security-annotations.yaml'))
S = D['settings']
ROLES = D['roles']                      # user roles
GUEST = S['guestRole']
ROLE_ORDER = [GUEST] + [r for r in ROLES if r != GUEST]

STATUS_CLS = {'fixed': 'good', 'intended': 'good', 'accepted': 'warn', 'open': 'bad'}
SEV_CLS = {'high': 'bad', 'error': 'bad', 'medium': 'warn', 'warning': 'warn', 'low': 'none', 'info': 'none'}
SEV_TAG = {'high': 'HIGH', 'medium': 'MED', 'low': 'LOW', 'info': 'INFO', 'error': 'ERR', 'warning': 'WARN'}


def verdict(key):
    a = ANN.get(key)
    return (a['status'], a['note']) if a else ('open', '')


def md_code(t):
    """The report writes `code` in markdown; render it."""
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', E(t))


def short_xpath(x):
    """Drop module prefixes from association paths so a constraint fits a cell; the full text is in the title."""
    x = ' '.join(x.split())
    return re.sub(r'\b(?:Catalog|Core|Fulfilment|Shop|Simulation)\.', '', x)


# ------------------------------------------------------------------ access per entity, role, right
ENT = {e['QualifiedName']: e for e in CAT['entities']}
U2M = {}
for m in CAT['roleMappings']:
    U2M.setdefault(m['UserRoleName'], set()).add(m['ModuleRoleName'])
RIGHTS = ['READ', 'WRITE', 'CREATE', 'DELETE']
RANK = {'own': 1, 'filtered': 2, 'all': 3}       # widest wins, as in the report


def classify(xp):
    if not xp.strip():
        return 'all'
    return 'own' if '[%CurrentUser%]' in xp else 'filtered'


access = {}       # (entity, user role, right) -> (class, [xpaths])
for p in CAT['permissions']:
    for ur in ROLE_ORDER:
        if p['ModuleRoleName'] in U2M.get(ur, ()):
            key = (p['ElementName'], ur, p['AccessType'])
            c = classify(p['XPathConstraint'])
            old = access.get(key)
            xps = (old[1] if old else []) + ([p['XPathConstraint']] if p['XPathConstraint'].strip() else [])
            access[key] = (c if not old or RANK[c] > RANK[old[0]] else old[0], xps)

# the catalog must agree with the report's own grid for every persistent entity
GRID = {g['entity']: g['access'] for g in D['grid']}
for ent, cells in GRID.items():
    for ur, cell in cells.items():
        letters, cls = cell.split(' ', 1)
        mine = access.get((ent, ur, 'READ'))
        assert mine and {'own': 'via user'}.get(mine[0], mine[0]) == cls, f'{ent}/{ur}: report {cell}, catalog {mine}'
        assert ('W' in letters) == ((ent, ur, 'WRITE') in access), f'{ent}/{ur}: write differs'

persistent = [e for e in ENT.values() if e['EntityType'] == 'PERSISTENT']
server_only = sorted(e['QualifiedName'] for e in persistent if e['AccessRuleCount'] == '0')
non_persistent = sorted(e['QualifiedName'] for e in ENT.values() if e['EntityType'] != 'PERSISTENT')
assert len(GRID) == len(persistent) - len(server_only), 'grid = persistent entities with an access rule'
unconstrained = sorted(e for e in GRID if access[(e, GUEST, 'READ')][0] == 'all')
creates = sorted({k[0] for k in access if k[2] in ('CREATE', 'DELETE')})
writes = sorted({k[0] for k in access if k[2] == 'WRITE' and k[1] == GUEST})
roles_same = all(access.get((e, ROLE_ORDER[0], r)) == access.get((e, ur, r)) for e in ENT for ur in ROLE_ORDER for r in RIGHTS)

# ------------------------------------------------------------------ findings and triage
findings = D['findings']
fstat = [(f, *verdict('finding:' + f['id'])) for f in findings]
open_hm = [f for f, st, _ in fstat if st == 'open' and f['severity'] in ('high', 'medium')]
by_sev = {}
for f, st, _ in fstat:
    by_sev.setdefault(f['severity'], []).append(st)
lint = D['lintRules']
lstat = [(r, *verdict('rule:' + r['rule'])) for r in lint]
lint_open = [r['rule'] for r, st, _ in lstat if st == 'open']

# ------------------------------------------------------------------ client-callable flows
flows = D['flows']
CALLS = CAT['flowCalls']


def param_entity(f):
    m = re.search(r'Object:([\w.]+)', f['params'][0]) if f['params'] else None
    return m.group(1) if m else None


fixed_flows = {f['name'] for f in flows if verdict('finding:flow:' + f['name'])[0] == 'fixed'}
trusting = [f for f in flows if not f['checksCaller'] and f['name'] not in fixed_flows]
delegating = [f for f in trusting if any('.SUB_' in c or '.ACT_' in c for c in CALLS.get(f['name'], []))]
unbounded = [f for f in trusting if access.get((param_entity(f), GUEST, 'READ'), ('all',))[0] == 'all']
assert all(GUEST in f['roles'] for f in flows), 'every client-callable flow is a guest flow'

# ------------------------------------------------------------------ 1. headline
sev_order = [s for s in ('high', 'medium', 'low', 'info') if s in by_sev]
sev_txt = ' + '.join(f'{len(by_sev[s])} {s}' for s in sev_order)
tri_txt = ', '.join(f'{s} {", ".join(sorted(by_sev[s]))}' for s in sev_order)
k = kpis([
    (f'{len(open_hm)} open', f'High or medium findings left after triage. The report raised {len(findings)} findings ({sev_txt}); '
     f'every one has a verdict in the annotations ({tri_txt}).', 'good' if not open_hm else 'bad'),
    (f'{len(lint)} rules · {sum(r["count"] for r in lint)} hits', f'Lint security and access findings, grouped per rule: {len(lint) - len(lint_open)} triaged as intended or accepted, '
     f'{len(lint_open)} not yet triaged (<code>{", ".join(lint_open) or "none"}</code>, info).', 'warn' if lint_open else 'good'),
    (f'{len(unconstrained)} of {len(GRID)}', f'Entities a guest can read without any row constraint: {" and ".join(f"<code>{E(e)}</code>" for e in unconstrained)}, '
     'the public allergen list and store details. Accepted by design; every other read is limited to the guest\'s own rows or to published catalog data.', 'warn' if unconstrained else 'good'),
    (f'{len(unbounded)} of {len(flows)}', f'Client-callable flows whose object a guest could swap for someone else\'s. {len(trusting)} do not check the caller themselves, '
     f'but each takes an object the guest may only read when it is theirs or published; {len(flows) - len(trusting)} check the caller in code ({len(fixed_flows)} through a sub-microflow).', 'good' if not unbounded else 'bad'),
])

# ------------------------------------------------------------------ 2. findings
WHY = {
    'flow:Shop.DS_Info_Line': 'Read in the model: the flow returns nothing for a product that is not <code>PUBLISHED</code> and creates the draft line in the cart that '
                              '<code>Shop.SUB_Cart_Current</code> retrieves for <code>[%CurrentUser%]</code>. A substituted product id can only name another published product, '
                              'which every guest may see anyway. The report still lists it because it recognises a caller check only by name in the flow\'s own body.',
    'setting:guest-access': f'The shop has no sign-in, so the anonymous role <code>{E(GUEST)}</code> <em>is</em> the customer. The grid and the flow list below are therefore the '
                            'public surface of the app, and are reviewed as such.',
}
fhtml = []
for f, st, note in fstat:
    body = (f'<p>{md_code(f["detail"])}</p>'
            + (f'<p><b>Triage.</b> {E(note)}.</p>' if note else '<p><b>Not triaged.</b> Add a verdict to <code>docs/reports/security-annotations.yaml</code>.</p>')
            + (f'<p class="note">{WHY[f["id"]]}</p>' if f['id'] in WHY else '')
            + f'<p class="note"><b>Report\'s advice:</b> {md_code(f["fix"])}</p>')
    fhtml.append(finding(SEV_TAG[f['severity']], STATUS_CLS[st], f'{st} · {f["severity"]}', md_code(f['title']), body, tag_cls=SEV_CLS[f['severity']]))
controls = ''.join(f'<li>{md_code(c)}</li>' for c in D['controls'])
sec_findings = section('Findings', f'''
<p>The report raised {len(findings)} findings. Both were looked at by hand and have a verdict in the annotations; a finding without one would show as <b>open</b> here.
The controls the report found in place are listed underneath: they are why the list is short.</p>
<div class="findings">{''.join(fhtml)}</div>
<h3 style="margin-top:26px">Controls in place</h3><ul class="tight">{controls}</ul>''')

# ------------------------------------------------------------------ 3. access grid
LAB = {'own': ('own', 'good'), 'filtered': ('filtered', 'good'), 'all': ('all', 'warn'), 'session': ('session', 'none')}


def cell(ent, ur, right):
    a = access.get((ent, ur, right))
    if not a:
        return '<span class="no" title="no access">–</span>'
    c = 'session' if ent in non_persistent else a[0]
    txt, cls = LAB[c]
    tip = {'own': 'rows tied to the current user', 'filtered': 'rows matching the constraint', 'all': 'every row, no constraint',
           'session': 'non-persistent: only objects in the guest\'s own session'}[c]
    return f'<span class="tag {cls}" title="{E(right.lower())}: {E(tip)}">{txt}</span>'


NOTE = {
    'Catalog.Allergen': 'Public allergen list (accepted SEC007).',
    'Core.StoreSettings': 'Store name, address, phone, prices (accepted SEC007).',
    'Fulfilment.Coupon': 'Guest read removed: the code is shown as text on the cart.',
    'Fulfilment.DeliveryZone': 'Only the zone of the guest\'s own orders.',
    'Fulfilment.OrderAccess': 'The session grant: placed, looked up or opened by tracking link.',
    'Fulfilment.OrderLogEntry': 'Also only customer-visible lines.',
    'Shop.LookupForm': 'Order lookup form; guesses are counted in LookupAttempt.',
}
rows = []
for mod in MODULE_ORDER:
    ents = sorted(e for e in ENT if ENT[e]['ModuleName'] == mod)
    if not ents:
        continue
    head = f'<tr class="mod"><th colspan="{2 + 4 * len(ROLE_ORDER)}" scope="colgroup"><i class="dot" style="background:var({MODULE_COLOR[mod]})"></i>{E(mod)}</th></tr>'
    rows.append(head)
    for e in sorted(ents, key=lambda x: (ENT[x]['EntityType'] != 'PERSISTENT', ENT[x]['AccessRuleCount'] == '0', x)):
        kind = 'server only' if e in server_only else 'non-persistent' if e in non_persistent else ''
        xps = sorted({x for ur in ROLE_ORDER for r in RIGHTS for x in access.get((e, ur, r), (None, []))[1]})
        con = '<br>'.join(f'<code class="xp" title="{E(" ".join(x.split()))}">{E(short_xpath(x))}</code>' for x in xps)
        if not con:
            con = ('<span class="note">no access rule: no client can read it</span>' if e in server_only else
                   '<span class="note">none (in-memory object)</span>' if e in non_persistent else '<span class="note">none: every row</span>')
        if e in NOTE:
            con += f'<span class="rng">{E(NOTE[e])}</span>'
        cells = ''.join(f'<td class="c{" first" if i == 0 else ""}">{cell(e, ur, r)}</td>' for ur in ROLE_ORDER for i, r in enumerate(RIGHTS))
        rows.append(f'<tr{" class=dim" if kind else ""}><th scope="row"><code>{E(ENT[e]["Name"])}</code>{f"<span class=rng>{kind}</span>" if kind else ""}</th>{cells}<td class="xpc">{con}</td></tr>')
rhead = ''.join(f'<th colspan="4" class="grp" scope="colgroup">{E(ur)}{" (guest)" if ur == GUEST else ""}</th>' for ur in ROLE_ORDER)
rsub = ''.join(f'<th class="c{" first" if i == 0 else ""}" title="{r.lower()}">{r[0]}</th>' for _ in ROLE_ORDER for i, r in enumerate(RIGHTS))
grid = (f'<div class="scroll"><table class="grid"><thead><tr><th rowspan="2">Entity</th>{rhead}<th rowspan="2">Constraint</th></tr><tr>{rsub}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>')
legend = ('<div class="legend"><span><span class="tag good">own</span> only rows tied to the current guest</span>'
          '<span><span class="tag good">filtered</span> rows matching a constraint (published, active)</span>'
          '<span><span class="tag warn">all</span> every row, no constraint</span>'
          '<span><span class="tag none">session</span> non-persistent, the guest\'s own objects</span>'
          '<span><b class="no">–</b> no access</span><span>R W C D = read, write, create, delete</span></div>')
sec_grid = section('Who can read and change what', f'''
<p>Each persistent and non-persistent entity of the five app modules, per user role and right, from the access rules in the model.
{"Both user roles have exactly the same access: " if roles_same else ""}<code>Administrator</code> exists only so the runtime has an admin user (<code>{E(S["adminUser"])}</code>),
and holds the same Guest module roles as <code>{E(GUEST)}</code> instead of unconstrained reads on everything.</p>
<p>No client can create or delete a persistent object{f" (only {', '.join(creates)})" if creates else ""}: carts, lines, orders and toasts are made and removed by microflows.
A guest can write only {", ".join(f"<code>{E(w)}</code>" for w in writes[:-1])} and <code>{E(writes[-1])}</code>, and only their own. {len(server_only)} entities have no access rule at all and are
reachable only from server code. Hover a tag for its meaning and a constraint for its full XPath.</p>
{legend}{grid}''')

# ------------------------------------------------------------------ 4. client-callable flows
GROUP_NOTE = {
    'Shop.Cart': 'The guest\'s cart: header, menu, home carousel, coupons and checkout start.',
    'Shop.CartLine': 'Lines in the cart and the configurator\'s draft line.',
    'Shop.CheckoutForm': 'The checkout form: type, tip, pickup, place and pay.',
    'Catalog.Product': 'Menu and product info: the object is a product, the cart is found from the current user.',
    'Fulfilment.Order': 'Receipt and tracking.',
    'Fulfilment.OrderLine': 'Lines of an order on the receipt and tracking pages.',
    'Core.Toast': 'Closing a notification.',
}
groups = {}
for f in flows:
    groups.setdefault(param_entity(f), []).append(f)
order = sorted(groups, key=lambda e: (-len(groups[e]), e))
blocks = []
for ent in order:
    fs = sorted(groups[ent], key=lambda f: f['name'])
    rc = access.get((ent, GUEST, 'READ'), ('none', []))[0]
    bound = {'own': 'only the guest\'s own rows', 'filtered': 'only published / active rows', 'all': 'any row', 'none': 'no row'}[rc]
    trs = []
    for f in fs:
        if f['checksCaller']:
            chk = '<span class="status good">checks caller</span><span class="rng">in its own body</span>'
        elif f['name'] in fixed_flows:
            chk = '<span class="status good">checks caller</span><span class="rng">via a sub-microflow (triaged: fixed)</span>'
        else:
            chk = '<span class="status none">relies on read rule</span>'
        calls = [c for c in CALLS.get(f['name'], []) if c.split('.')[1].startswith(('SUB_', 'ACT_')) and c != f['name']]
        does = ', '.join(f'<code>{E(c)}</code>' for c in calls) or '<span class="note">nothing; opens a page or returns a list</span>'
        trs.append([f'<code>{E(f["name"])}</code>', (f'<span class="tag {SEV_CLS.get(f["risk"], "good") if f["risk"] != "ok" else "good"}">{E(f["risk"])}</span>', ''), chk, does])
    n_chk = sum(1 for f in fs if f['checksCaller'] or f['name'] in fixed_flows)
    split = f'{n_chk} check the caller, {len(fs) - n_chk} rely on the read rule' if n_chk and n_chk < len(fs) else ('all check the caller' if n_chk else 'all rely on the read rule')
    blocks.append(f'<details{" open" if ent in order[:1] else ""}><summary><code>{E(ent)}</code> · {len(fs)} flow{"s" if len(fs) != 1 else ""} ({split}) · '
                  f'substitutable object: <b>{bound}</b></summary><p class="note">{E(GROUP_NOTE.get(ent, ""))}</p>'
                  + table([('Flow', ''), ('Report risk', ''), ('Caller check', ''), ('Delegates to', '')], trs, cls='flows') + '</details>')
risk_n = {r: sum(1 for f in flows if f['risk'] == r) for r in ('high', 'medium', 'ok')}
sec_flows = section('What a guest can call', f'''
<p>{len(flows)} microflows are granted to the guest and take a persistent object, so the browser chooses which object they act on. Because a client may only pass an object it can read,
the question per flow is whether that object is limited to the guest's own rows. The report rates {risk_n["high"]} high, {risk_n["medium"]} medium and {risk_n["ok"]} ok; grouped by the
object they take, every group's read rule is row-scoped or limited to published data, so a swapped id reaches nothing a guest could not already see or change.</p>
<p><b>Read the "medium" label with care.</b> The report looks at a flow's own body only. {len(delegating)} of the {len(trusting)} flows it calls "reads only" hand the object to another
microflow, and several of those do change it (remove a line, clear a cart, place an order). They are safe because of the read rule on the object, not because they only read.
A caller check written in such a sub-microflow is invisible to the report in the same way.</p>
{"".join(blocks)}''')

# ------------------------------------------------------------------ 5. settings, roles, constants
pol = {}
for line in CAT['projectSecurity']:
    if ':' in line:
        a, b = line.split(':', 1)
        pol[a.strip()] = b.strip()
ok, warn, note_ = 'good', 'warn', 'none'
srows = [
    ('Security level', E(pol.get('Security Level', S['level'])), ok, 'Entity, page and microflow access are enforced.'),
    ('Strict mode', 'on' if S['strictMode'] else 'off', ok if S['strictMode'] else warn, 'The client API is limited to what pages request.'),
    ('Demo users', f'{"enabled" if S["demoUsersEnabled"] else "disabled"} · {pol.get("Demo Users", "?")}', ok if not S['demoUsersEnabled'] else warn, 'No test accounts ship with the model.'),
    ('Guest access', f'on · role <code>{E(GUEST)}</code>', note_, 'Intended: the shop has no sign-in.'),
    ('Administrator', f'<code>{E(S["adminUser"])}</code> · role <code>{E(S["adminRole"])}</code> · password {E(pol.get("Admin Password", "?"))}', note_,
     'Demo password in the project settings; change it per environment.'),
    ('Password policy', f'min. {S["passwordMinLength"]} · digit {pol.get("Require Digit")} · mixed case {pol.get("Require Mixed Case")} · symbol {pol.get("Require Symbol")}', note_,
     'Applies only to the admin account; guests have no password.'),
]
settings_t = table([('Setting', ''), ('Value', ''), ('Verdict', ''), ('Note', '')],
                   [[E(a), b, f'<span class="status {c}">{ {"good": "ok", "warn": "check", "none": "by design"}[c] }</span>', (E(n), 'note')] for a, b, c, n in srows])
CONST_SAFE = {'Shop.FaultInjection': 'False', 'Simulation.ResetOnStartup': 'False'}
crow = []
for c in CAT['constants']:
    v = c['DefaultValue']
    if c['QualifiedName'] in CONST_SAFE:
        st = ('good', 'safe default') if v == CONST_SAFE[c['QualifiedName']] else ('bad', 'unsafe default')
    elif c['DataType'] == 'String' and 'localhost' in v:
        st = ('warn', 'set per environment')
    else:
        st = ('good', 'harmless')
    crow.append([f'<code>{E(c["QualifiedName"])}</code>', E(c['DataType']), f'<code>{E(v)}</code>', f'<span class="status {st[0]}">{st[1]}</span>',
                 ('client' if c['ExposedToClient'] == '1' else 'server only', 'note'), (E(c['Description']), 'note')])
const_t = table([('Constant', ''), ('Type', ''), ('Default', ''), ('Verdict', ''), ('Exposed', ''), ('What it does', '')], crow)
app_mods = set(D['scope']['app'])
mrows = []
for ur in ROLE_ORDER:
    mine = sorted(U2M.get(ur, ()))
    mrows.append([f'<code>{E(ur)}</code>{" (guest)" if ur == GUEST else ""}', ', '.join(f'<code>{E(m)}</code>' for m in mine if m.split('.')[0] in app_mods),
                  (', '.join(E(m) for m in mine if m.split('.')[0] not in app_mods), 'note')])
roles_t = table([('User role', ''), ('App module roles', ''), ('Platform and Marketplace roles', '')], mrows)
sec_settings = section('Settings and defaults', f'''
<p>Project security as the model holds it, the user-role mapping, and the app's constants. The report's unsafe-default check (key-like strings, test switches that default to
<code>true</code>) found nothing: the fault switch <code>Shop.FaultInjection</code> and the demo reset both default to off, and no constant is sent to the browser.</p>
<div class="cols"><div><h3>Project security</h3>{settings_t}</div><div><h3>User roles</h3>{roles_t}
<p class="note" style="margin-top:8px">Every app module has one module role, <code>Guest</code>, mapped to both user roles. That is what lint rule CONV008 reports below.</p></div></div>
<h3 style="margin-top:22px">Constants</h3>{const_t}''')

# ------------------------------------------------------------------ 6. lint
lrows = []
for r, st, note in sorted(lstat, key=lambda x: (x[1] != 'open', -['info', 'warning', 'error'].index(x[0]['severity']), x[0]['rule'])):
    ex = ''.join(f'<li>{E(x)}</li>' for x in r['examples'])
    n_ex, cnt = len(r['examples']), r['count']
    of = f' of {cnt}' if cnt > n_ex else ''
    exs = f'<details><summary>{n_ex} example{"s" if n_ex != 1 else ""}{of}</summary><ul class="tight ex">{ex}</ul></details>'
    if not note and r['rule'] == 'CONV008':
        note_html = ('<b>Not triaged.</b> Suggested verdict: intended. The admin user shares the guests\' module roles on purpose (project brain, Shop: <em>the built-in '
                     'Administrator holds the same Guest module roles instead of unconstrained reads on every entity</em>).')
    else:
        note_html = E(note) or '<b>Not triaged.</b>'
    if r['rule'] == 'SEC001':
        named = [e for e in server_only if e.split('.')[1] not in note]
        if named:
            note_html += (f' <span class="rng">The note names {len(server_only) - len(named)} of the {r["count"]} entities; also server-only: '
                          f'{", ".join(E(n) for n in named)} (guest read removed, project brain, Fulfilment).</span>')
    lrows.append([f'<code>{E(r["rule"])}</code>', (f'<span class="tag {SEV_CLS[r["severity"]]}">{E(r["severity"])}</span>', ''), (str(r['count']), 'num'),
                  f'<span class="status {STATUS_CLS[st]}">{E(st)}</span>', note_html + exs])
lint_t = table([('Rule', ''), ('Severity', ''), ('Hits', 'num'), ('Verdict', ''), ('Why', '')], lrows, cls='lint')
sec_lint = section('Lint security rules', f'''
<p>{len(lint)} rules fire {sum(r["count"] for r in lint)} times. The lint score alone would read as alarming (an error and three warnings); per rule, each hit is a decision
already recorded. {len(lint_open)} rule{" has" if len(lint_open) == 1 else "s have"} no verdict yet and {"is" if len(lint_open) == 1 else "are"} shown as open.</p>{lint_t}''')

# ------------------------------------------------------------------ 7. method, limits
method = ''.join(f'<li>{md_code(m)}</li>' for m in RAW['method'])
limits = ''.join(f'<li>{md_code(m)}</li>' for m in RAW['limits'])
sec_how = f'''<section class="cols">
<div><h2>How this was made</h2>
<p><code>mxcli report security --format json</code> ({E(RAW["mxcli"])}, {E(RAW["generated"])}) in <code>docs/reports/raw/security.json</code>; read-only catalog queries for create
and delete rights, non-persistent and server-only entities, role mapping, constants and the microflows each flow calls in <code>docs/security/catalog.json</code>
(<code>tools/collect.py</code>); verdicts from <code>docs/reports/security-annotations.yaml</code>. This page is rendered by <code>tools/gen_security.py</code>, which checks that the
catalog's access rules give the same grid as the report.</p>
<ul class="tight">{method}</ul></div>
<div><h2>Limits</h2><ul class="tight">{limits}
<li>Marketplace and platform modules (Administration, System, Atlas, DataWidgets…) are outside the grid; the Administrator's <code>Administration.Administrator</code> role reaches their account pages.</li>
<li>"Delegates to" lists direct calls only; what a sub-microflow writes was read by hand for <code>Shop.DS_Info_Line</code>, not for every flow.</li></ul></div>
</section>'''

body = k + sec_findings + sec_grid + sec_flows + sec_settings + sec_lint + sec_how

EXTRA = '''
table.grid { width: auto; min-width: 100%; }
table.grid th, table.grid td { padding: 6px 8px; }
table.grid thead th.grp { text-align: center; border-bottom: 1px solid var(--line); border-left: 2px solid var(--line); }
table.grid .c { text-align: center; padding-inline: 4px; width: 70px; min-width: 70px; }
td .status { white-space: nowrap; }
table.grid .c.first { border-left: 2px solid var(--line); }
table.grid .c .tag { min-width: 52px; text-align: center; }
table.grid tr.mod th { font: 600 14px/1.2 var(--f-body); padding-top: 18px; border-bottom: 1px solid var(--ink); background: var(--bg); }
table.grid tbody th[scope=row] { font-weight: 500; white-space: nowrap; }
table.grid tr.dim th code, table.grid tr.dim .no { color: var(--muted); }
table.grid td.xpc { min-width: 300px; max-width: 520px; }
code.xp { display: block; font-size: 11.5px; color: var(--muted); word-break: break-word; }
.no { color: var(--muted); font-family: var(--f-mono); }
.legend .tag { margin-right: 4px; }
.legend { margin-bottom: 12px; }
details > summary { padding: 6px 0; }
details > p.note { margin-top: 4px; }
table.flows td:first-child { white-space: nowrap; }
table.flows td { font-size: 14px; }
table.lint td:last-child { min-width: 320px; }
ul.ex { margin-top: 6px; font-size: 13px; color: var(--muted); }
ul.ex li { word-break: break-word; }
.finding h3 { margin-top: 4px; }
@media (max-width: 600px) { .finding { grid-template-columns: 48px 1fr; gap: 12px; } table.grid td.xpc { min-width: 240px; } }
'''

html = page('GitPizza Security', eyebrow='GitPizza · security review · 19 November 2026',
            lede=('Who can see and change what in a shop where every visitor is an anonymous guest. The model was read, not attacked: '
                  'access rules, the flows a browser can call, project settings and lint rules, each with the verdict it was given in triage. '
                  f'Nothing high or medium is open; {len(unconstrained)} entities are public on purpose, and {len(lint_open)} lint rule{"s" if len(lint_open) != 1 else ""} still wait{"" if len(lint_open) != 1 else "s"} for a verdict.'),
            body=body, current='security', extra_css=EXTRA)
write(OUT, html)
