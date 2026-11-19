#!/usr/bin/env python3
"""Rebuild flows deliberately: `python3 tools/mdl_rebuild.py <script.mdl> [Module.Name ...]`.

mxcli's `create or modify` splices changes into the stored flow and refuses
structural changes it cannot splice (MDL-V1-REBUILD). For flows authored only
in MDL (no Studio Pro drawing to preserve) a drop + create in one run is the
documented way to rebuild. With no names, every microflow/nanoflow that the
plain exec refuses is rebuilt. Afterwards the script's own `create or modify`
runs unchanged.
"""
import re, subprocess, sys, tempfile

path, names = sys.argv[1], sys.argv[2:]
src = open(path, encoding='utf-8').read()
header = 'mdl 1;\n'
blocks = re.findall(r'((?:/\*\*.*?\*/\s*)?create or modify (microflow|nanoflow) ([\w."]+)\s*\(.*?\nend;)', src, re.S)
if not names:
    r0 = subprocess.run(['./mxcli', 'exec', path, '-p', 'GitPizza.mpr'], capture_output=True, text=True)
    out = re.sub(r'\x1b\[[0-9;]*m', '', r0.stdout + r0.stderr)
    names = sorted(set(re.findall(r'create or modify (?:microflow|nanoflow) ([\w.]+): this change cannot be spliced', out)))
todo = []
for block, kind, name in blocks:
    if name.replace('"', '') in names:
        todo.append(f'drop {kind} {name};\n' + block.replace('create or modify ' + kind, 'create ' + kind, 1))
if not todo:
    print('nothing to rebuild'); sys.exit(0)
with tempfile.NamedTemporaryFile('w', suffix='.mdl', delete=False, dir='.mxcli') as f:
    f.write(header + '\n'.join(todo) + '\n')
print('rebuilding:', ', '.join(names))
r = subprocess.run(['./mxcli', 'exec', f.name, '-p', 'GitPizza.mpr'], capture_output=True, text=True)
print((r.stdout + r.stderr)[-1500:])
