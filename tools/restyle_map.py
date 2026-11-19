#!/usr/bin/env python3
"""Give mxcli's interactive software map the reports' house style, after rendering it.

    ./mxcli report map -p GitPizza.mpr -q -o docs/reports/map.html
    python3 tools/restyle_map.py docs/reports/map.html

The map draws itself in the browser from its own CSS variables; this script appends the
house tokens (light and dark), the embedded fonts, the brand bar and the shared report
navigation. Its content and behaviour are untouched. Safe to run twice.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report_fonts import font_face_css  # noqa: E402
from report_kit import nav  # noqa: E402

MARK = '<!-- house-style -->'
LIGHT = ('--bg:#f6f5f1;--fg:#1b1b1c;--muted:#5e6066;--line:#dedcd5;--card:#ffffff;--accent:#2a78d6;--heat:#2a78d6;'
         '--ok:#127a3a;--okbg:#e6f4ec;--warn:#9a6b00;--warnbg:#fdf3dc;--bad:#b3261e;--badbg:#fbe7e6;--info:#2a78d6;--infobg:#e3eefb')
DARK = ('--bg:#131313;--fg:#ececec;--muted:#a2a4aa;--line:#2f2f31;--card:#1b1b1c;--accent:#6da7ec;--heat:#3987e5;'
        '--ok:#5cc98e;--okbg:#15291e;--warn:#e0b54a;--warnbg:#2d2510;--bad:#f07575;--badbg:#321615;--info:#86b6ef;--infobg:#16253a')
CSS = f'''
:root{{{LIGHT}}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{{DARK};color-scheme:dark}}}}
:root[data-theme="dark"]{{{DARK};color-scheme:dark}}
body{{font:15px/1.55 "Geist",system-ui,sans-serif}}
code,pre,svg text{{font-family:"JetBrains Mono",ui-monospace,monospace}}
main > header{{border-bottom:6px solid #ff9d00;padding:12px 0 22px;margin-bottom:22px;display:grid;gap:10px}}
main > header h1{{font:700 clamp(28px,5vw,40px)/1.1 "JetBrains Mono",ui-monospace,monospace;letter-spacing:-.02em}}
h2{{font:700 21px/1.25 "JetBrains Mono",ui-monospace,monospace;letter-spacing:-.01em}}
nav.reports{{display:flex;flex-wrap:wrap;gap:4px 14px;font:500 13px "Geist",system-ui,sans-serif}}
nav.reports a{{color:var(--muted);text-decoration:none}} nav.reports a[aria-current]{{color:var(--fg);font-weight:600}}
.eyebrow{{font:600 12px/1 "Geist",system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
'''


def main(path):
    s = open(path).read()
    if MARK in s:
        s = s[:s.index(MARK)] + s[s.index('</style>', s.index(MARK)) + len('</style>'):]
        s = s.replace('<span class="eyebrow">GitPizza · software map</span>', '')
        s = s.replace(nav('map'), '')
    style = f'{MARK}<style>{font_face_css()}{CSS}</style>'
    i = s.index('</head>')
    s = s[:i] + style + s[i:]
    s = s.replace('<main id="app"><header>', f'<main id="app"><header>{nav("map")}<span class="eyebrow">GitPizza · software map</span>', 1)
    open(path, 'w').write(s)
    print(f'restyled {path}')


if __name__ == '__main__':
    main(sys.argv[1])
