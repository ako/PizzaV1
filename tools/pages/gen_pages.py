#!/usr/bin/env python3
"""Expand %%NAME%% placeholders of tools/pages/*.mdl.tpl with tools/pages/<name>.txt
fragments into mdlsource/. Usage: python3 tools/pages/gen_pages.py <tpl> <out> NAME=file ..."""
import sys
tpl = open(sys.argv[1]).read()
for kv in sys.argv[3:]:
    k, f = kv.split('=', 1)
    tpl = tpl.replace(f'%%{k}%%', open(f).read())
open(sys.argv[2], 'w').write(tpl)
