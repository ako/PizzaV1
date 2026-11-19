#!/usr/bin/env python3
"""Insert a `grant execute` line right after every guest-facing flow (ACT_*/DS_*)
of a script, so no snippet or page ever references a flow without an allowed
role (CE0106 at production level). Idempotent."""
import re, sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
s = re.sub(r'\ngrant execute on (?:microflow|nanoflow) Shop\.(?:ACT|DS)_\w+ to Shop\.Guest; -- auto\n', '\n', s)
s = re.sub(r'\n-- grants \(tools/add_grants.py\)\n(?:grant execute[^\n]*\n)*', '\n', s)
def add(m):
    return m.group(0) + f'\ngrant execute on {m.group(1)} {m.group(2)} to Shop.Guest; -- auto'
s = re.sub(r'create or modify (microflow|nanoflow) (Shop\.(?:ACT|DS)_\w+)\b.*?\nend;', add, s, flags=re.S)
open(p, 'w', encoding='utf-8').write(s)
