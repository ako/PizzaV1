#!/usr/bin/env python3
"""Read-only catalog queries the security page needs beyond `mxcli report security`.

    python3 docs/security/tools/collect.py     # -> docs/security/catalog.json

The report's grid gives one summary cell per entity and role ("R filtered", "RW via user").
The page also shows the microflows each client-callable flow calls, create/delete, the non-persistent entities, the server-only entities
(no access rule), the user-role -> module-role mapping and the app's constants; those come
from the mxcli catalog here. Nothing is written to the model.
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(HERE, '..', 'catalog.json')
APP = "('Catalog','Core','Fulfilment','Shop','Simulation')"


def q(sql):
    r = subprocess.run(['./mxcli', '-p', 'GitPizza.mpr', '-q', '--json', '-c', sql], cwd=REPO, capture_output=True, text=True, check=True)
    out = r.stdout
    return json.loads(out[out.index('['):]) if '[' in out else []


def flow_calls():
    """Microflows each client-callable flow calls: the report sees writes and caller checks in a flow's own body only."""
    rep = json.load(open(os.path.join(REPO, 'docs', 'reports', 'raw', 'security.json')))['data']
    out = {}
    for f in rep['flows']:
        src = subprocess.run(['./mxcli', '-p', 'GitPizza.mpr', '-q', '-c', f"DESCRIBE MICROFLOW {f['name']}"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout
        out[f['name']] = sorted(set(re.findall(r'call microflow ([\w.]+)', src[src.find('begin'):])))
    return out


data = {
    'entities': q(f"SELECT QualifiedName, ModuleName, Name, EntityType, AccessRuleCount, AttributeCount FROM CATALOG.ENTITIES "
                  f"WHERE ModuleName IN {APP} ORDER BY QualifiedName"),
    'permissions': q(f"SELECT ModuleRoleName, ElementName, AccessType, XPathConstraint FROM CATALOG.PERMISSIONS "
                     f"WHERE ElementType = 'ENTITY' AND ModuleName IN {APP} AND (MemberName IS NULL OR MemberName = '') "
                     f"ORDER BY ElementName, ModuleRoleName, AccessType"),
    'roleMappings': q("SELECT UserRoleName, ModuleRoleName, ModuleName FROM CATALOG.ROLE_MAPPINGS ORDER BY UserRoleName, ModuleRoleName"),
    'constants': q(f"SELECT QualifiedName, DataType, DefaultValue, ExposedToClient, Description FROM CATALOG.CONSTANTS "
                   f"WHERE ModuleName IN {APP} ORDER BY QualifiedName"),
    'flowCalls': flow_calls(),
    'projectSecurity': subprocess.run(['./mxcli', '-p', 'GitPizza.mpr', '-q', '-c', 'SHOW PROJECT SECURITY'], cwd=REPO,
                                      capture_output=True, text=True, check=True).stdout.strip().splitlines(),
}
with open(OUT, 'w') as f:
    json.dump(data, f, indent=1)
print(f'wrote {os.path.relpath(OUT, REPO)}: ' + ', '.join(f'{k} {len(v)}' for k, v in data.items()))
