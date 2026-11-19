#!/usr/bin/env python3
"""Fold `create`/`change` followed by `commit` of the same object into one activity (lint CONV021).

    python3 tools/fold_commits.py mdlsource/*.mdl

    $X = create M.E (...);            ->   $X = create M.E (...) commit without events;
    commit $X without events;

Only folds when the commit is the very next statement and names the same variable;
`refresh` is carried over. Files are rewritten in place; prints the count per file.
"""
import re, sys

PAT = re.compile(
    r'(?P<stmt>(?P<ind>^[ \t]*)(?:\$(?P<v1>\w+) = create [\w.]+ \((?:[^;\'"]|\'(?:[^\']|\'\')*\')*?\)'
    r'|change \$(?P<v2>\w+) \((?:[^;\'"]|\'(?:[^\']|\'\')*\')*?\)'
    r'|add \$\w+ to \$(?P<v4>\w+)/[\w.]+));\n'
    r'[ \t]*commit \$(?P<v3>\w+)(?P<we> without events)?(?P<rf> refresh)?;[ \t]*(?=\n)',
    re.M)

# consecutive `change $X (a);` `change $X (b)...` -> `change $X (a, b)...`
MERGE = re.compile(
    r'^(?P<ind>[ \t]*)change \$(?P<v>\w+) \((?P<a>(?:[^;\'"]|\'(?:[^\']|\'\')*\')*?)\);\n'
    r'[ \t]*change \$(?P=v) \(', re.M)

def merge_changes(src):
    total = 0
    while True:
        src, n = MERGE.subn(lambda m: f"{m.group('ind')}change ${m.group('v')} ({m.group('a')}, ", src)
        total += n
        if not n:
            return src, total

def fold(src):
    src, merged = merge_changes(src)
    def rep(m):
        var = m.group('v1') or m.group('v2') or m.group('v4')
        if var != m.group('v3'):
            return m.group(0)
        return f"{m.group('stmt')} commit{m.group('we') or ''}{m.group('rf') or ''};"
    out, n = PAT.subn(rep, src)
    return out, n + merged

if __name__ == '__main__':
    for path in sys.argv[1:]:
        src = open(path, encoding='utf-8').read()
        out, n = fold(src)
        changed = sum(1 for a, b in [(src, out)] if a != b)
        if out != src:
            open(path, 'w', encoding='utf-8').write(out)
        print(f'{path}: {src.count(chr(10)) - out.count(chr(10))} folded')
