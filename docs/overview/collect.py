#!/usr/bin/env python3
"""Collect the evidence for the build-overview deck: one JSON per swimlane.

    python3 docs/overview/collect.py              # measure again (traceability, scored report, mxbuild)
    python3 docs/overview/collect.py --no-build   # skip mxbuild (docker check), keep its last result
    PRD_DIR=<package-lite> python3 docs/overview/collect.py   # also refresh the PRD epic table

Writes docs/overview/data/{lane0,m1,m2,m3,m4,summary}.json. Nothing here is typed in by
hand except LESSONS (picked from FINDINGS.md, and checked to still be there) and the
lane-0 rules for decisions that name no user story. Status always comes from the model:
`mxcli report traceability` derives built / partial / changed / not built from the
brain's anchors, and the counts below are taken from that, never from memory.
"""
import collections
import datetime
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DATA = os.path.join(HERE, 'data')
RAW = os.path.join(ROOT, 'docs', 'reports', 'raw')
MPR = 'GitPizza.mpr'
APP_MODULES = ('Simulation', 'Shop', 'Fulfilment', 'Catalog', 'Core')
os.makedirs(DATA, exist_ok=True)

# Three lessons, quoted from FINDINGS.md (the heading text is checked below).
LESSONS = [
    ('Home carousel never moved',
     'A list fed by a microflow refreshes only when a persistent context object is committed '
     'with refresh, so the carousel and the menu filters keep their state on the guest\'s cart.'),
    ('Caller-trusting data sources',
     'The security report found 3 high findings no test caught: data sources that trusted an '
     'object id from the browser. Each now checks ownership or PUBLISHED.'),
    ('Traceability needed the requirements in the brain',
     'The 111 stories were captured as brain requirements only at the end. Capture them before '
     'building: the delivery files (RUN/) and the commit convention were never captured, and slipped.'),
]

# Decisions that name no user story: which lane they belong to (by the start of the title).
LANE_RULES = {'Accepted SEC': 'lane0', 'Security': 'lane0', 'Module split': 'lane0', 'Theme': 'lane0',
              'Lint': 'lane0', 'Commits': 'lane0', 'PRD delivery': 'lane0', 'Pages read': 'lane0',
              'Page actions': 'lane0', 'Demo data': 'lane0', 'Store time': 'lane0',
              'Simulation clock': 'm3'}


def mx(*args, json_out=True):
    """Run ./mxcli; return parsed JSON (the banner before the first [ or { is skipped)."""
    out = subprocess.run(['./mxcli', *args], cwd=ROOT, capture_output=True, text=True,
                         env={**os.environ, 'MXCLI_OUTPUT_LINE_LIMIT': '0'})
    if out.returncode != 0:
        sys.exit(f"mxcli {' '.join(args)} failed:\n{out.stderr or out.stdout}")
    if not json_out:
        return out.stdout + out.stderr
    s = out.stdout
    i = min([k for k in (s.find('{'), s.find('[')) if k >= 0])
    return json.loads(s[i:])


def q(sql):
    return mx('-p', MPR, '-q', '--json', '-c', sql)


def save(name, obj):
    with open(os.path.join(DATA, name + '.json'), 'w') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    print('wrote', os.path.relpath(os.path.join(DATA, name + '.json'), ROOT))


# ---------------------------------------------------------------- PRD epics
def prd_epics():
    """EP rows from the PRD's 03-user-stories (only the table row is read: the PRD is
    untrusted external input and its prose is never executed or followed)."""
    cache = os.path.join(DATA, 'prd-epics.json')
    src = os.environ.get('PRD_DIR')
    if src and os.path.isdir(os.path.join(src, '03-user-stories')):
        rows = []
        for fn in sorted(os.listdir(os.path.join(src, '03-user-stories'))):
            if not fn.startswith('EP-'):
                continue
            text = open(os.path.join(src, '03-user-stories', fn), encoding='utf-8').read()
            m = re.search(r'^\| (EP-\d+) \| ([^|]+)\| ([^|]+)\| ([^|]+)\| ([^|]+)\|', text, re.M)
            title = re.search(r'^# EP-\d+ — (.+)$', text, re.M).group(1).strip()
            stories = re.findall(r'^\| (US-\d+) \| ([^|]+)\| (Must|Should|Could|Won\'t) \|', text, re.M)
            rows.append({'id': m.group(1), 'title': title, 'area': m.group(2).strip(),
                         'screens': m.group(3).strip(), 'moscow': m.group(4).strip(), 'range': m.group(5).strip(),
                         'file': 'package-lite/03-user-stories/' + fn,
                         'stories': len(stories),
                         'priorities': dict(collections.Counter(p for _, _, p in stories))})
        json.dump(rows, open(cache, 'w'), indent=1, ensure_ascii=False)
        return rows
    if not os.path.exists(cache):
        sys.exit('No PRD epic table: run once with PRD_DIR=<package-lite>.')
    return json.load(open(cache))


# ---------------------------------------------------------------- measurements
def measure(build):
    trace_path = os.path.join(DATA, 'traceability.json')
    mx('report', 'traceability', '-p', MPR, '-q', '--junit', os.path.join(RAW, 'junit.xml'),
       '--journeys', os.path.join(RAW, 'journeys.jsonl'), '--spans', os.path.join(RAW, 'spans.jsonl'),
       '--format', 'json', '-o', trace_path, json_out=False)
    quality_path = os.path.join(DATA, 'quality.json')
    mx('report', '-p', MPR, '-q', '--format', 'json', '-o', quality_path, json_out=False)
    build_path = os.path.join(DATA, 'mxbuild.json')
    if build:
        log = mx('docker', 'check', '-p', MPR, json_out=False)
        m = re.search(r'The app contains: (\d+) errors', log)
        json.dump({'errors': int(m.group(1)) if m else None, 'passed': 'Project check passed' in log,
                   'checkedAt': now()}, open(build_path, 'w'), indent=1)
    return (json.load(open(trace_path)), json.load(open(quality_path)),
            json.load(open(build_path)) if os.path.exists(build_path) else None)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')


# ---------------------------------------------------------------- helpers
US = re.compile(r'US-(\d{3})')


def us_range(text):
    """US ids named in a decision title; 'US-121..US-137' is a range."""
    ids = set()
    for a, b in re.findall(r'US-(\d{3})\s*(?:\.\.|–|-)\s*US-(\d{3})', text):
        ids.update(f'US-{n:03d}' for n in range(int(a), int(b) + 1))
    ids.update('US-' + n for n in US.findall(text))
    return ids


def short(title, n=150):
    t = re.sub(r'\s+', ' ', title).strip()
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0] + ' …'


def main():
    build = '--no-build' not in sys.argv
    epics = prd_epics()
    trace, quality, mxbuild = measure(build)
    brain = mx('brain', 'list', '-p', MPR, '-q', '--json')['entries']
    plan = mx('brain', 'plan', '-p', MPR, '--json')
    shots = json.load(open(os.path.join(HERE, 'shots', 'index.json')))
    junit = ET.parse(os.path.join(RAW, 'junit.xml')).getroot()
    test_file = {tc.get('name'): tc.get('file') for tc in junit.iter('testcase')}
    test_fail = {tc.get('name') for tc in junit.iter('testcase') if tc.find('failure') is not None or tc.find('error') is not None}
    journeys = {}
    for line in open(os.path.join(RAW, 'journeys.jsonl')):
        rec = json.loads(line)
        if 'journey' in rec and 'step' not in rec:
            journeys[rec['journey']] = rec.get('status')
    findings = open(os.path.join(ROOT, 'FINDINGS.md'), encoding='utf-8').read()
    for head, _ in LESSONS:
        if head not in findings:
            sys.exit(f'Lesson "{head}" is no longer in FINDINGS.md: update LESSONS.')

    # microflow -> entities it references (catalog), for the Model column
    refs = collections.defaultdict(set)
    for r in q("SELECT SourceName, TargetName FROM CATALOG.REFS WHERE SourceType = 'MICROFLOW' AND TargetType = 'ENTITY'"):
        if r['TargetName'].split('.')[0] in APP_MODULES:
            refs[r['SourceName']].add(r['TargetName'])

    milestones = trace['data']['milestones']
    lane_of_us, lane_ids = {}, {}
    for i, m in enumerate(milestones, 1):
        lane_ids[m['name']] = f'm{i}'
        for r in m['requirements']:
            lane_of_us[r['title'].split()[0]] = f'm{i}'
    slice_ms = {r['slice']: lane_of_us[r['title'].split()[0]] for r in plan['requirements']}
    epic_lane = {}
    for e in epics:
        num = e['id'].split('-')[1]
        for sl, lane in slice_ms.items():
            if sl.startswith(num + '-'):
                epic_lane[e['id']] = lane

    # decisions -> lanes
    decisions = [e for e in brain if e['kind'] == 'decision' and not e.get('open')]
    open_q = [e for e in mx('brain', 'list', '--open', '-p', MPR, '-q', '--json')['entries']]
    dec_lane = {}
    for d in decisions + open_q:
        t = d['title']
        rule = next((lane for p, lane in LANE_RULES.items() if t.startswith(p)), None)
        if rule:
            dec_lane[d['id']] = rule
            continue
        lanes = collections.Counter(lane_of_us[u] for u in us_range(t) if u in lane_of_us)
        if not lanes:   # by anchors: the milestone whose requirements' footprint holds them
            for m in milestones:
                for r in m['requirements']:
                    names = set(r['footprint'] or []) | {a['anchor'][1:] for a in r['anchors']}
                    for a in d.get('anchors') or []:
                        if a[1:] in names:
                            lanes[lane_ids[m['name']]] += 1
        dec_lane[d['id']] = lanes.most_common(1)[0][0] if lanes else 'lane0'

    def dec_card(d):
        t = d['title']
        kind = ('open' if d.get('open') else 'partial' if re.search(r'partly (met|meets)', t, re.I)
                else 'deviation' if re.search(r'deviate|although the prototype|not produced', t)
                else 'accepted' if re.search(r'^Accepted|; accepted ', t) else 'decision')
        return {'id': d['id'], 'kind': kind, 'module': d.get('shard'), 'text': short(t),
                'anchors': d.get('anchors') or []}

    summary_rows = []
    for m in milestones:
        lane = lane_ids[m['name']]
        reqs = m['requirements']
        st = collections.Counter(r['status'] for r in reqs)
        anchors = collections.defaultdict(set)
        foot = set()
        for r in reqs:
            for a in r['anchors']:
                if a['state'] == 'resolved':
                    anchors[a['kind']].add(a['anchor'][1:])
            foot.update(r['footprint'] or [])
        ents = collections.Counter(e for f in foot for e in refs.get(f, ()))
        mods = collections.Counter(n.split('.')[0] for n in foot)
        tests = collections.OrderedDict()
        jset = collections.OrderedDict()
        for r in reqs:
            for t in r['tests'] or []:
                tests[t] = {'name': t, 'file': test_file.get(t), 'passed': t not in test_fail}
            for jn in r['journeys'] or []:
                jset[jn] = {'name': jn, 'status': journeys.get(jn, 'unknown')}
        gaps = []
        for r in reqs:
            if r['status'] != 'built':
                reason = next((x['text'] for x in (dec_card(d) for d in decisions)
                               if r['id'] in x['text'] or r['title'].split()[0] in x['text']), None)
                if not reason:
                    for d in decisions:
                        if r['title'].split()[0] in d['title']:
                            reason = short(d['title'])
                gaps.append({'id': r['id'], 'title': r['title'], 'status': r['status'], 'reason': reason})
        untested = [r['title'] for r in reqs if not (r['tests'] or r['journeys'])]
        lane_epics = [e for e in epics if epic_lane.get(e['id']) == lane]
        doc = {
            'lane': lane, 'name': m['name'], 'collectedAt': now(),
            'prd': {'epics': lane_epics,
                    'note': 'Milestones are the brain\'s grouping of the PRD epics; the PRD itself has none.'},
            'decisions': [dec_card(d) for d in decisions + open_q if dec_lane[d['id']] == lane],
            'model': {
                'modules': dict(mods.most_common()),
                'footprintMicroflows': len(foot),
                'pages': sorted(anchors.get('page', ())), 'snippets': sorted(anchors.get('snippet', ())),
                'entities': [e for e, _ in ents.most_common(10)],
                'jsActions': sorted(anchors.get('javascript_action', ())),
                'nanoflows': sorted(anchors.get('nanoflow', ())),
                'anchorKinds': {k: len(v) for k, v in sorted(anchors.items())},
            },
            'proof': {'tests': list(tests.values()), 'journeys': list(jset.values()),
                      'screenshots': [s for s in shots if s['lane'] == lane],
                      'untested': untested},
            'status': {'requirements': len(reqs), 'built': st.get('built', 0), 'partial': st.get('partial', 0),
                       'changed': st.get('changed', 0), 'notBuilt': st.get('not built', 0) + st.get('not_built', 0),
                       'notTraceable': st.get('not traceable', 0) + st.get('not_traceable', 0),
                       'proven': len(reqs) - len(untested), 'gaps': gaps},
        }
        save(lane, doc)
        summary_rows.append({'lane': lane, 'name': m['name'], **{k: doc['status'][k] for k in
                             ('requirements', 'built', 'partial', 'changed', 'notBuilt', 'proven')},
                             'epics': [e['id'] for e in lane_epics],
                             'open': [g['title'].split()[0] for g in doc['status']['gaps']]})

    # ---------------------------------------------------------------- lane 0
    roles = q("SELECT UserRoleName, ModuleRoleName FROM CATALOG.ROLE_MAPPINGS")
    nav = q("SELECT ProfileName, HomePage, NotFoundPage FROM CATALOG.NAVIGATION_PROFILES")
    ent_types = q("SELECT ModuleName, EntityType, COUNT(*) AS N FROM CATALOG.ENTITIES GROUP BY ModuleName, EntityType")
    counts = {t: int(q(f"SELECT COUNT(*) AS N FROM CATALOG.{t}")[0]['N']) for t in
              ('WORKFLOWS', 'CONSUMED_REST_SERVICES', 'CONSUMED_ODATA_SERVICES', 'PUBLISHED_REST_SERVICES',
               'PUBLISHED_ODATA_SERVICES')}
    sched = [r['QualifiedName'] for r in q("SELECT QualifiedName FROM CATALOG.SCHEDULED_EVENTS")]
    queues = [r['QualifiedName'] for r in q("SELECT QualifiedName FROM CATALOG.TASK_QUEUES")]
    sec = json.load(open(os.path.join(RAW, 'security.json')))['data']
    arch = json.load(open(os.path.join(RAW, 'architecture.json')))['data']
    tests_rep = json.load(open(os.path.join(RAW, 'tests.json')))['data']
    sec_notes = open(os.path.join(ROOT, 'docs', 'reports', 'security-annotations.yaml')).read()
    open_high = [f['id'] for f in sec['findings'] if f.get('severity') in ('high', 'medium')
                 and not re.search(re.escape(f'finding:{f["id"]}') + r'": \{status: (fixed|intended|accepted)', sec_notes)]
    test_files = sorted({f for f in test_file.values() if f})
    cov = tests_rep['totals']
    # visual comparison against the prototype (tests/e2e/visual.js writes out/, which is gitignored)
    vis_src, vis_cache = os.path.join(ROOT, 'tests', 'e2e', 'out', 'visual-summary.json'), os.path.join(DATA, 'visual.json')
    if os.path.exists(vis_src):
        rows = json.load(open(vis_src))
        json.dump({'screens': rows, 'measuredAt': datetime.datetime.fromtimestamp(os.path.getmtime(vis_src), datetime.timezone.utc)
                   .strftime('%Y-%m-%d %H:%M UTC')}, open(vis_cache, 'w'), indent=1)
    vis = json.load(open(vis_cache)) if os.path.exists(vis_cache) else None
    visual_cmp = vis and {'screens': len(vis['screens']), 'withinBudget': sum(1 for r in vis['screens'] if r['mismatch'] <= r['budget']),
                          'minMismatch': min(r['mismatch'] for r in vis['screens']),
                          'maxMismatch': max(r['mismatch'] for r in vis['screens']), 'measuredAt': vis['measuredAt']}
    cats = {c['name']: c['score'] for c in quality['categories']}
    req_all = sum(r['requirements'] for r in summary_rows)
    lane0 = {
        'lane': 'lane0', 'name': 'Crosscutting', 'collectedAt': now(),
        'prd': {'items': [
            {'ref': '00-README §8', 'text': 'Delivery: commit per story "US-xxx: <title>", RUN/ journal, self-assessment, delivery notes, operations, start/stop scripts'},
            {'ref': '00-README / LITE-SES-01', 'text': 'No sign-in: every visitor is an anonymous guest; no demo users'},
            {'ref': '07-design-system', 'text': 'Git Pizza look: dark console theme, design tokens, prototype screens'},
            {'ref': '12-acceptance', 'text': 'Acceptance scenarios and calculated pricing examples'},
            {'ref': '09-demo-data', 'text': 'Demo catalogue, coupons and orders as JSON'},
        ]},
        'decisions': [dec_card(d) for d in decisions + open_q if dec_lane[d['id']] == 'lane0'],
        'model': {
            'modules': [{'name': m['name'], 'layer': m.get('layer')} for m in arch['modules']],
            'cycles': arch.get('cycles') or 0, 'clusters': len(arch.get('communities') or []),
            'userRoles': sorted({r['UserRoleName'] for r in roles}),
            'moduleRoles': sorted({r['ModuleRoleName'] for r in roles if r['ModuleRoleName'].split('.')[0] in APP_MODULES}),
            'navigation': nav[0] if nav else None,
            'entities': {f"{r['ModuleName']}:{r['EntityType']}": int(r['N']) for r in ent_types if r['ModuleName'] in APP_MODULES},
            'viewEntities': sum(int(r['N']) for r in ent_types if r['ModuleName'] in APP_MODULES and 'VIEW' in r['EntityType']),
            'integrations': counts, 'scheduledEvents': sched, 'taskQueues': queues,
            'theme': 'theme/web + themesource/shop (prototype CSS ported, scoped to .gp-app)',
            'brain': {'requirements': sum(1 for e in brain if e['kind'] == 'requirement'),
                      'decisions': len(decisions), 'open': len(open_q),
                      'anchors': sum(len(r['anchors']) for r in plan['requirements']),
                      'slices': len({r['slice'] for r in plan['requirements']})},
        },
        'proof': {
            'mxbuild': mxbuild, 'lint': quality['summary'], 'score': quality['overallScore'], 'categories': cats,
            'security': {'openHighMedium': open_high, 'findings': len(sec['findings'])},
            'qualityCategory': next(c for c in quality['categories'] if c['name'] == 'Quality'),
            'topRules': collections.Counter(v['ruleId'] for v in quality['violations']).most_common(6),
            'tests': {'files': test_files, 'count': len(test_file), 'failed': len(test_fail)},
            'journeys': {'count': len(journeys), 'passed': sum(1 for s in journeys.values() if s == 'passed')},
            'visual': visual_cmp,
            'coverage': {'reached': cov['both'] + cov['testsOnly'] + cov['journeysOnly'],
                         'nonStartup': cov['total'] - cov['startup'], 'byTests': cov['both'] + cov['testsOnly']},
            'screenshots': [s for s in shots if s['lane'] == 'lane0'],
        },
        'status': {'gaps': [dec_card(d) for d in decisions + open_q
                            if dec_lane[d['id']] == 'lane0' and dec_card(d)['kind'] in ('open', 'deviation', 'accepted')]},
    }
    save('lane0', lane0)

    save('summary', {
        'collectedAt': now(), 'requirements': req_all,
        'built': sum(r['built'] for r in summary_rows), 'partial': sum(r['partial'] for r in summary_rows),
        'notBuilt': sum(r['notBuilt'] for r in summary_rows), 'changed': sum(r['changed'] for r in summary_rows),
        'proven': sum(r['proven'] for r in summary_rows),
        'milestones': summary_rows, 'openQuestions': [short(e['title'], 120) for e in open_q],
        'lessons': [{'source': 'FINDINGS.md: ' + h, 'text': t} for h, t in LESSONS],
        'gates': {'mxbuild': mxbuild, 'score': quality['overallScore'], 'lint': quality['summary'],
                  'tests': f"{len(test_file) - len(test_fail)}/{len(test_file)}",
                  'journeys': f"{sum(1 for s in journeys.values() if s == 'passed')}/{len(journeys)}"},
        'mxcli': trace.get('mxcli'),
    })


if __name__ == '__main__':
    main()
