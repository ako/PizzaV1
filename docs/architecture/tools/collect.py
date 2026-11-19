#!/usr/bin/env python3
"""Collect docs/architecture/arch.json: the built-in architecture report's data plus per-module
document counts and the module edges with and without the generated seed flows.

    ./mxcli report architecture -p GitPizza.mpr -q --format json -o docs/reports/raw/architecture.json
    python3 docs/architecture/tools/collect.py
"""
import json
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
APP = ('Simulation', 'Shop', 'Fulfilment', 'Catalog', 'Core')


def q(sql):
    out = subprocess.run(['./mxcli', '-p', 'GitPizza.mpr', '-q', '--json', '-c', sql], cwd=ROOT, capture_output=True, text=True,
                         env={**os.environ, 'MXCLI_OUTPUT_LINE_LIMIT': '0'}).stdout
    i = out.find('[')
    return json.loads(out[i:]) if i >= 0 else []


def per_module(table, where=''):
    rows = q(f"SELECT ModuleName, COUNT(*) AS N FROM CATALOG.{table} {where} GROUP BY ModuleName")
    return {r['ModuleName']: int(r['N']) for r in rows}


rep = json.load(open(os.path.join(ROOT, 'docs', 'reports', 'raw', 'architecture.json')))
counts = {
    'microflows': per_module('MICROFLOWS'),
    'seedMicroflows': per_module('MICROFLOWS', "WHERE Name LIKE 'SEED%'"),
    'nanoflows': per_module('NANOFLOWS'),
    'pages': per_module('PAGES'),
    'snippets': per_module('SNIPPETS'),
    'entities': per_module('ENTITIES', "WHERE EntityType = 'PERSISTENT'"),
    'viewModels': per_module('ENTITIES', "WHERE EntityType = 'NON_PERSISTENT'"),
    'jsActions': per_module('JAVASCRIPT_ACTIONS'),
    'javaActions': per_module('JAVA_ACTIONS'),
}
# references between app modules, by the source's module, without the generated seed flows
edges = {}
for seed in (False, True):
    where = "" if seed else "AND SourceName NOT LIKE 'Simulation.SEED%'"
    rows = q("SELECT ModuleName, SUBSTR(TargetName, 1, INSTR(TargetName, '.') - 1) AS T, COUNT(*) AS N FROM CATALOG.REFS "
             f"WHERE ModuleName IN ('Simulation','Shop','Fulfilment','Catalog','Core') {where} GROUP BY ModuleName, T")
    edges['withSeed' if seed else 'withoutSeed'] = [{'from': r['ModuleName'], 'to': r['T'], 'refs': int(r['N'])} for r in rows if r['T'] in APP]
sim_shop = q("SELECT SourceName, TargetName, RefKind FROM CATALOG.REFS WHERE ModuleName = 'Simulation' AND TargetName LIKE 'Shop.%' "
             "AND RefKind IN ('call', 'create')")
json.dump({'report': rep, 'counts': counts, 'catalogEdges': edges, 'simulationToShop': sim_shop},
          open(os.path.join(ROOT, 'docs', 'architecture', 'arch.json'), 'w'), indent=1)
print('wrote docs/architecture/arch.json')
