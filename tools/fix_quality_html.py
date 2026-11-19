#!/usr/bin/env python3
"""mxcli's scored report (report --format html) gives the score bars widths but no CSS
for the fill, so every bar renders as an empty grey track. Add the three rules."""
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
css = ('<style>.score-fill{display:block;height:100%;border-radius:4px}'
       '.score-good{background:#2e9e5b}.score-ok{background:#e0a400}.score-bad{background:#d9534f}</style>')
if '.score-fill{' not in s:
    s = s.replace('</head>', css + '</head>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('score-bar CSS added')
