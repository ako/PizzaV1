#!/usr/bin/env python3
"""Stage the model unit files of named documents: `python3 tools/stage_units.py Name1 Name2 ...`.

Mendix MPR v2 stores every document as its own BSON file under mprcontents/.
A document's own name is stored as a BSON string (int32 length + bytes + NUL),
so we look for exactly that encoding; references from other documents are
qualified (Module.Name) and do not match. Prints the files it staged.
"""
import glob, struct, subprocess, sys

list_only = '--list' in sys.argv
names = [a for a in sys.argv[1:] if a != '--list']
pats = {n: struct.pack('<i', len(n.encode()) + 1) + n.encode() + b'\x00' for n in names}
hits = {}
for f in glob.glob('mprcontents/**/*.mxunit', recursive=True):
    data = open(f, 'rb').read()
    for n, p in pats.items():
        if b'Name\x00' + p in data:
            hits.setdefault(n, []).append(f)
missing = [n for n in names if n not in hits]
files = sorted({f for fs in hits.values() for f in fs})
if list_only:
    print('\n'.join(files)); sys.exit(0)
if files:
    subprocess.run(['git', 'add', '--'] + files, check=True)
for n in names:
    print(f'{n}: {", ".join(hits.get(n, ["NOT FOUND"]))}')
if missing:
    sys.exit(1)
