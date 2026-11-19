#!/usr/bin/env python3
"""Write RUN/self-assessment.json from the model (deliverables.md section 4).

    PRD_DIR=<package-lite> python3 tools/run_self_assessment.py   # also refreshes the PRD story cache
    python3 tools/run_self_assessment.py                          # uses docs/overview/data/prd-stories.json

Status comes from `mxcli report traceability` (docs/overview/data/traceability.json, written by
docs/overview/collect.py): built -> done, partial/changed -> partial, not built -> no. `where` is the
story's screens (from its PRD table, only the table row is read) plus the pages and snippets its
brain anchors resolve to. Stories that no automated test or journey reaches say so in `notes`.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA = os.path.join(ROOT, 'docs', 'overview', 'data')
CACHE = os.path.join(DATA, 'prd-stories.json')
STUDIO_PRO = '11.16.1'
SCREENS = {'SCR-01': 'Home', 'SCR-02': 'Menu', 'SCR-03': 'Pizza configurator', 'SCR-04': 'Item info',
           'SCR-05': 'Cart', 'SCR-06': 'Checkout', 'SCR-07': 'Payment sheet', 'SCR-08': 'Order confirmation',
           'SCR-09': 'Order tracking', 'SCR-10': 'Track order lookup', 'SCR-13': 'Order receipt',
           'SCR-16': 'Customer shell', 'SCR-40': 'Not found', 'SCR-41': 'Unexpected error'}
# Journeys that exercise a story on a page whose data needs no microflow, so traceability cannot link them.
JOURNEY_ONLY = {'US-281': 'J5', 'US-287': 'J6'}
# Deviation ids of RUN/delivery-notes.md section 5 for stories that are not done.
DEV = {'US-097': 'DEV-01', 'US-288': 'DEV-02'}


def stories():
    src = os.environ.get('PRD_DIR')
    if src:
        out = {}
        d = os.path.join(src, '03-user-stories')
        for fn in sorted(os.listdir(d)):
            if not fn.startswith('EP-'):
                continue
            text = open(os.path.join(d, fn), encoding='utf-8').read()
            for m in re.finditer(r'^### (US-\d+) (.+?)\n.*?\n\| (Must|Should|Could)[^|]*\| [^|]*\| ([^|]*)\|', text, re.M | re.S):
                out[m.group(1)] = {'title': m.group(2).strip(), 'priority': m.group(3),
                                   'screens': re.findall(r'SCR-\d+', m.group(4))}
        json.dump(out, open(CACHE, 'w'), indent=1, ensure_ascii=False)
        return out
    return json.load(open(CACHE))


def main():
    prd = stories()
    trace = json.load(open(os.path.join(DATA, 'traceability.json')))['data']['milestones']
    reqs = {r['title'].split()[0]: r for m in trace for r in m['requirements']}
    missing = sorted(set(prd) - set(reqs))
    if missing:
        sys.exit(f'Stories in the PRD without a brain requirement: {missing}')
    entries = []
    for us in sorted(prd, key=lambda s: int(s[3:])):
        r, p = reqs[us], prd[us]
        status = {'built': 'done', 'partial': 'partial', 'changed': 'partial'}.get(r['status'], 'no')
        docs = sorted({a['anchor'][1:] for a in r['anchors'] if a['state'] == 'resolved' and a['kind'] in ('page', 'snippet')})
        screens = ', '.join(f'{s} {SCREENS.get(s, "")}'.strip() for s in p['screens'])
        where = '; '.join(x for x in (screens, ', '.join(docs)) if x) if status != 'no' else ''
        notes = []
        if status != 'done':
            reason = next((re.sub(r'^[0-9a-f]{6}: ', '', d) for d in (r['decisions'] or []) if us in d), None)
            notes.append((reason or 'see delivery-notes.md') + f' ({DEV.get(us, "DEV-?")})')
        if status == 'done' and not (r['tests'] or r['journeys']):
            if us in JOURNEY_ONLY:
                notes.append(f'Exercised by browser journey {JOURNEY_ONLY[us]} (tests/e2e/journeys.js).')
            else:
                notes.append('No automated test or browser journey covers this story yet.')
        entries.append({'id': us, 'status': status, 'where': where or ('n/a' if status != 'no' else ''),
                        'notes': ' '.join(notes)})
    doc = {'studioProVersion': STUDIO_PRO, 'stories': entries}
    path = os.path.join(ROOT, 'RUN', 'self-assessment.json')
    json.dump(doc, open(path, 'w'), indent=2, ensure_ascii=False)
    count = {k: sum(1 for e in entries if e['status'] == k) for k in ('done', 'partial', 'no')}
    print(f'wrote RUN/self-assessment.json: {len(entries)} stories {count}')


if __name__ == '__main__':
    main()
