#!/usr/bin/env python3
"""Per-step figures that count only the guest's own work, from a journey log and its spans.

    python3 docs/perf/tools/analyse.py docs/perf/data/before   # reads before-journeys.jsonl, before-spans.jsonl.gz
    -> docs/perf/data/before.json

Why not the built-in step figures: `mxcli report performance` sums every span inside a step's
time window, so the simulator's background clock (a queued task that sleeps 1.5 s, then ticks)
lands in whichever step it overlaps and adds up to 1.5 s of "server time" and its queries to
random steps. Here a step's work is the traces whose root is an HTTP request on the app port
(8080) starting inside the step window; queued tasks and scheduled events are reported apart.

Per step: browser ms (from the journey log), server ms (sum of the guest requests), database ms
and queries (the JDBC spans under them); median of the warm runs (run 0 is warm-up) with min-max.
The median run's spans are kept as a flame chart: each request in its own band, depth by parent.
"""
import gzip
import json
import statistics
import sys
from collections import defaultdict

APP_PORT = '8080'


def is_db(s):
    a = s['attrs']
    return 'db.statement' in a or 'db.query.text' in a or ('db.system' in a and s.get('kind') == 3)


def load(prefix):
    steps, meta = [], {}
    for line in open(prefix + '-journeys.jsonl'):
        r = json.loads(line)
        if r.get('meta'):
            meta = r
        elif 'step' in r:
            steps.append(r)
    spans = [json.loads(l) for l in gzip.open(prefix + '-spans.jsonl.gz', 'rt')]
    return meta, steps, spans


def iso_ns(t):
    from datetime import datetime, timezone
    return int(datetime.fromisoformat(t.replace('Z', '+00:00')).astimezone(timezone.utc).timestamp() * 1e9)


def main(prefix):
    meta, steps, spans = load(prefix)
    by_trace = defaultdict(list)
    for s in spans:
        by_trace[s['traceId']].append(s)
    roots = []
    for tid, ss in by_trace.items():
        ids = {s['spanId'] for s in ss}
        for s in ss:
            if not s.get('parentId') or s['parentId'] not in ids:
                roots.append(s)
    guest = sorted([r for r in roots if r['attrs'].get('server.port') == APP_PORT], key=lambda r: r['start'])
    background = [r for r in roots if r['attrs'].get('server.port') != APP_PORT]

    def trace_spans(root):
        return by_trace[root['traceId']]

    out = defaultdict(lambda: {'runs': []})
    for st in steps:
        a, b = iso_ns(st['start']), iso_ns(st['end'])
        mine = [r for r in guest if a <= r['start'] <= b]
        server = sum((r['end'] - r['start']) for r in mine) / 1e6
        dbs = [s for r in mine for s in trace_spans(r) if is_db(s)]
        bg = [r for r in background if a <= r['start'] <= b]
        key = (st['journey'], st['step'])
        out[key]['runs'].append({'run': st['run'], 'browserMs': st['browserMs'], 'serverMs': round(server, 1),
                                 'dbMs': round(sum(s['end'] - s['start'] for s in dbs) / 1e6, 1), 'queries': len(dbs),
                                 'requests': len(mine), 'backgroundTasks': len(bg),
                                 'window': (a, b), 'roots': [r['spanId'] for r in mine]})
    result = []
    for (journey, step), v in out.items():
        warm = [r for r in v['runs'] if r['run'] > 0] or v['runs']
        def med(k):
            return statistics.median([r[k] for r in warm])
        rep = sorted(warm, key=lambda r: r['browserMs'])[len(warm) // 2]
        result.append({'journey': journey, 'step': step, 'warmRuns': len(warm),
                       **{k: med(k) for k in ('browserMs', 'serverMs', 'dbMs', 'queries', 'requests')},
                       'range': {k: [min(r[k] for r in warm), max(r[k] for r in warm)] for k in ('browserMs', 'queries')},
                       'flame': flame(rep, {s['spanId']: s for r in guest if r['spanId'] in rep['roots'] for s in trace_spans(r)},
                                      [r for r in guest if r['spanId'] in rep['roots']])})
    # background work over the whole measurement: the simulator's ticks
    ticks = [r for r in background if 'SIM_ClockRun' in r['name']]
    bg_summary = {'clockTicks': len(ticks),
                  'tickMs': round(statistics.median([(r['end'] - r['start']) / 1e6 for r in ticks]), 1) if ticks else None,
                  'note': 'Each tick includes a 1.5 s wait (Simulation.JA_Sleep); excluded from every step.'}
    json.dump({'meta': meta, 'steps': result, 'background': bg_summary}, open(prefix + '.json', 'w'), indent=1)
    print(f'wrote {prefix}.json: {len(result)} steps, {len(guest)} guest requests, {len(ticks)} clock ticks')


def flame(rep, spans, roots):
    """Spans of the representative run: x from the step start (ms), a band per concurrent request."""
    a = rep['window'][0]
    kids = defaultdict(list)
    for s in spans.values():
        kids[s.get('parentId')].append(s)
    bands, items = [], []
    for r in sorted(roots, key=lambda r: r['start']):
        # first band whose last request ended before this one starts
        for i, end in enumerate(bands):
            if end <= r['start']:
                band = i
                bands[i] = r['end']
                break
        else:
            band = len(bands)
            bands.append(r['end'])
        stack = [(r, 0)]
        while stack:
            s, d = stack.pop()
            kind = 'db' if is_db(s) else 'request' if s is r else 'microflow' if s['name'].startswith('Microflow') else 'action'
            items.append({'name': s['attrs'].get('db.statement', s['name'])[:160] if kind == 'db' else s['name'][:120],
                          'start': round((s['start'] - a) / 1e6, 2), 'dur': round((s['end'] - s['start']) / 1e6, 2),
                          'depth': d, 'band': band, 'kind': kind})
            for c in kids.get(s['spanId'], []):
                stack.append((c, d + 1))
    return {'run': rep['run'], 'windowMs': round((rep['window'][1] - a) / 1e6, 1), 'bands': len(bands), 'spans': items}


if __name__ == '__main__':
    main(sys.argv[1])
