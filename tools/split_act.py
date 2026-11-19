#!/usr/bin/env python3
"""Split page-action microflows into an ACT_ entry point and a SUB_ with the logic (lint CONV010).

    python3 tools/split_act.py <file.mdl|file.tpl> ACT_Name [ACT_Name ...]

ACT_X keeps its signature, documentation and grants (it is what pages call and
what the module roles may execute) and only delegates:

    create or modify microflow Shop.ACT_X ($A: T) ... begin
      call microflow Shop.SUB_X(A = $A);
    end;

The original body moves unchanged into a new SUB_X placed just before it (SUB_X_Do when a
SUB_X already exists). The SUB_ needs no grant: it is called from the server only.
"""
import re, sys

def split_params(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out

def split_one(src, name, existing):
    start = src.find(f'create or modify microflow Shop.{name} (')
    if start < 0:
        raise SystemExit(f'{name}: not found')
    doc_start = src.rfind('/**', 0, start)
    doc = ''
    if doc_start >= 0 and src[src.find('*/', doc_start) + 2:start].strip() == '':
        doc = src[doc_start:start]
    else:
        doc_start = start
    end = src.index('\nend;', start) + len('\nend;')
    block = src[start:end]
    # header: name + balanced parameter list
    i = block.index('(')
    depth = 0
    for j in range(i, len(block)):
        if block[j] == '(':
            depth += 1
        elif block[j] == ')':
            depth -= 1
            if depth == 0:
                break
    params = split_params(block[i + 1:j])
    head_rest, body = block[j + 1:].split('\nbegin\n', 1)
    body = body[:-len('end;')]
    m = re.search(r'returns (.+?) as \$(\w+)', head_rest)
    sub = 'SUB_' + name[len('ACT_'):]
    if sub in existing:
        sub += '_Do'
    args = ', '.join(f"{p.split(':')[0].strip()[1:]} = {p.split(':')[0].strip()}" for p in params)
    call = f'call microflow Shop.{sub}({args});'
    if m:
        new_body = f'  ${m.group(2)} = {call}\n  return ${m.group(2)};\n'
    else:
        new_body = f'  {call}\n'
    sub_doc = doc or '/** Logic of the page action. */\n'
    one = re.fullmatch(r'/\*\*\s*(.*?)\s*\*/\s*', doc, re.S) if doc and '\n' not in doc.strip() else None
    lines = ['/**', f' * {one.group(1)}', ' */'] if one else (doc.rstrip().split('\n') if doc else [])
    if lines:
        # append to the first paragraph (before the first ' *' blank line or the closing ' */')
        k = next((i for i, l in enumerate(lines) if i > 0 and l.strip() in ('*', '*/')), len(lines) - 1)
        act_doc = '\n'.join(lines[:k] + [f' * Page entry point; the logic is in {sub}.'] + lines[k:]) + '\n'
    else:
        act_doc = f'/** Page entry point; the logic is in {sub}. */\n'
    sub_head = re.sub(r"\nurl '[^']*'", '', head_rest)  # the deep link stays on the ACT_
    sub_block = sub_doc + f'create or modify microflow Shop.{sub} ' + block[block.index('('):j + 1] + sub_head + '\nbegin\n' + body + 'end;\n\n'
    act_block = act_doc + block[:j + 1] + head_rest + '\nbegin\n' + new_body + 'end;'
    return src[:doc_start] + sub_block + act_block + src[end:], sub

if __name__ == '__main__':
    path, names = sys.argv[1], sys.argv[2:]
    import glob
    existing = set(re.findall(r'microflow Shop\.(SUB_\w+) ', ''.join(open(f, encoding='utf-8').read() for f in glob.glob('mdlsource/*.mdl'))))
    src = open(path, encoding='utf-8').read()
    for n in names:
        src, sub = split_one(src, n, existing)
        existing.add(sub)
        print(f'{n} -> {sub}')
    open(path, 'w', encoding='utf-8').write(src)
