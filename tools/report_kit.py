"""Shared look for the generated report pages (docs/<kind>/report.html).

One design for every report: a reading column for prose, full-width bands for tables and
charts, headline tiles, findings with status tags, cohesion/status bars, light and dark
themes from the GitPizza tokens, and the app's own fonts embedded (works offline).

    import sys, os; sys.path.insert(0, '<repo>/tools'); from report_kit import *
    html = page('GitPizza Tests', eyebrow='GitPizza · tests · 19 November 2026', title='GitPizza Tests',
                lede='…', body=section('Heading', '<p>…</p>'))
"""
import html as _html
import os

from report_fonts import font_face_css

E = _html.escape
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# categorical slots (dataviz reference palette, validated): use in this fixed order, never cycled
MODULE_COLOR = {'Simulation': '--s1', 'Shop': '--s2', 'Fulfilment': '--s3', 'Catalog': '--s4', 'Core': '--s5'}
MODULE_ORDER = ['Simulation', 'Shop', 'Fulfilment', 'Catalog', 'Core']

CSS = r'''
:root {
  --bg: #f6f5f1; --surface: #ffffff; --ink: #1b1b1c; --muted: #5e6066; --line: #dedcd5; --brand: #ff9d00; --brand-ink: #2c1700; --code: #131313; --hit: #fff1d9;
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4; --s6: #008300; --s7: #6250d6; --s8: #e34948;
  --good: #127a3a; --good-bg: #e6f4ec; --warn: #9a6b00; --warn-bg: #fdf3dc; --bad: #b3261e; --bad-bg: #fbe7e6; --none-bg: #eeede8;
  --c-request: #1b1b1c; --c-microflow: #ff9d00; --c-action: #ffc485; --c-db: #c4373a; --c-label: #ffffff; --c-label-dark: #1b1b1c;
  --heat: 42, 120, 214;
  --f-display: "JetBrains Mono", ui-monospace, monospace; --f-body: "Geist", system-ui, sans-serif; --f-mono: "JetBrains Mono", ui-monospace, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #131313; --surface: #1b1b1c; --ink: #ececec; --muted: #a2a4aa; --line: #2f2f31; --hit: #2c2210; color-scheme: dark;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #0ca30c; --s7: #9085e9; --s8: #e66767;
  --good: #5cc98e; --good-bg: #15291e; --warn: #e0b54a; --warn-bg: #2d2510; --bad: #f07575; --bad-bg: #321615; --none-bg: #242426;
  --c-request: #9aa0aa; --c-action: #b88a4a; --c-db: #e05a5d; --c-label: #131313; --heat: 57, 135, 229 } }
:root[data-theme="dark"] {
  --bg: #131313; --surface: #1b1b1c; --ink: #ececec; --muted: #a2a4aa; --line: #2f2f31; --hit: #2c2210; color-scheme: dark;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #0ca30c; --s7: #9085e9; --s8: #e66767;
  --good: #5cc98e; --good-bg: #15291e; --warn: #e0b54a; --warn-bg: #2d2510; --bad: #f07575; --bad-bg: #321615; --none-bg: #242426;
  --c-request: #9aa0aa; --c-action: #b88a4a; --c-db: #e05a5d; --c-label: #131313; --heat: 57, 135, 229 }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); margin: 0; padding: 0 16px 64px; }
.wrap { max-width: 1180px; margin: 0 auto; display: grid; gap: 40px; }
.wrap > *, .kpis > *, .cols > *, .findings > * { min-width: 0; }
header.top { border-bottom: 6px solid var(--brand); padding-block: 36px 24px; display: grid; gap: 10px; }
.eyebrow { font: 600 12px/1 var(--f-body); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.eyebrow a { color: inherit; }
h1 { font: 700 clamp(30px, 5vw, 44px)/1.1 var(--f-display); margin: 0; letter-spacing: -.02em; }
h2 { font: 700 24px/1.2 var(--f-display); margin: 0 0 12px; letter-spacing: -.01em; }
h3 { font: 600 17px/1.3 var(--f-body); margin: 0 0 6px; }
p { margin: 0 0 10px; max-width: 74ch; }
.lede { font-size: 17px; max-width: 76ch; }
.muted, .note { color: var(--muted); }
code { font-family: var(--f-mono); font-size: 12.5px; }
a { color: var(--s1); }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(240px, 100%), 1fr)); gap: 16px; }
.kpi { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px 18px; display: grid; gap: 6px; align-content: start; }
.kpi .v { font: 600 26px/1.1 var(--f-mono); font-variant-numeric: tabular-nums; }
.kpi .v s { color: var(--muted); font-weight: 400; font-size: 19px; margin-right: 6px; }
.kpi .l { color: var(--muted); font-size: 13.5px; }
.kpi.good { border-left: 4px solid var(--good); } .kpi.warn { border-left: 4px solid var(--warn); } .kpi.bad { border-left: 4px solid var(--bad); }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px; overflow-x: auto; }
.scroll { overflow-x: auto; min-width: 0; }
table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
thead th { font: 600 12px/1.2 var(--f-body); letter-spacing: .04em; text-transform: uppercase; color: var(--muted); border-bottom: 2px solid var(--ink); white-space: nowrap; }
td.num, th.num { font-family: var(--f-mono); font-size: 13px; white-space: nowrap; text-align: right; }
td.note { color: var(--muted); font-size: 13.5px; }
tr.hit { background: var(--hit); }
.rng { display: block; color: var(--muted); font: 11.5px var(--f-mono); }
.tag { display: inline-block; font: 700 11px/1 var(--f-mono); padding: 4px 6px; border-radius: 3px; white-space: nowrap; }
.tag.good { background: var(--good-bg); color: var(--good); } .tag.warn { background: var(--warn-bg); color: var(--warn); }
.tag.bad { background: var(--bad-bg); color: var(--bad); } .tag.none { background: var(--none-bg); color: var(--muted); }
.tag.brand { background: var(--brand); color: var(--brand-ink); } .tag.ink { background: var(--code); color: var(--brand); }
.findings { display: grid; gap: 22px; }
.finding { display: grid; grid-template-columns: 56px 1fr; gap: 16px; }
.finding > .tag { font-size: 13px; padding: 8px 0; text-align: center; height: fit-content; }
.status { font: 600 12px/1 var(--f-body); letter-spacing: .05em; text-transform: uppercase; }
.status.good { color: var(--good); } .status.warn { color: var(--warn); } .status.bad { color: var(--bad); } .status.none { color: var(--muted); }
.bar { position: relative; width: 150px; height: 18px; background: var(--bg); border: 1px solid var(--line); border-radius: 3px; overflow: hidden; }
.bar i { position: absolute; inset: 0 auto 0 0; }
.bar.good i { background: var(--good); } .bar.warn i { background: var(--warn); } .bar.bad i { background: var(--bad); } .bar.brand i { background: var(--brand); }
.bar span { position: absolute; top: 0; font: 600 11.5px/16px var(--f-mono); color: var(--ink); }
.stack { display: flex; height: 16px; width: 100%; min-width: 180px; border-radius: 3px; overflow: hidden; gap: 2px; }
.stack i { display: block; height: 100%; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 13px; color: var(--muted); }
.legend i { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; }
i.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; vertical-align: 0; }
.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(340px, 100%), 1fr)); gap: 24px; }
ul.tight { margin: 0; padding-left: 20px; max-width: 76ch; } ul.tight li { margin-bottom: 6px; }
details { border-top: 1px solid var(--line); padding: 6px 0; }
details > summary { cursor: pointer; font-weight: 500; }
details > summary::marker { color: var(--muted); }
nav.reports { display: flex; flex-wrap: wrap; gap: 4px 14px; font: 500 13px var(--f-body); }
nav.reports a { color: var(--muted); text-decoration: none; } nav.reports a[aria-current] { color: var(--ink); font-weight: 600; }
svg text { font-family: var(--f-mono); }
'''

NAV = [('index', 'Overview', 'reports/index.html'), ('traceability', 'Traceability', 'traceability/report.html'),
       ('tests', 'Tests', 'testing/report.html'), ('performance', 'Performance', 'perf/report.html'),
       ('architecture', 'Architecture', 'architecture/report.html'), ('security', 'Security', 'security/report.html'),
       ('quality', 'Quality', 'quality/report.html'), ('map', 'Software map', 'reports/map.html')]


def nav(current, depth=1):
    """Links between the report pages; depth = directories below docs/ of the page."""
    up = '../' * depth
    return '<nav class="reports">' + ''.join(
        f'<a href="{up}{href}"{" aria-current=page" if key == current else ""}>{E(label)}</a>' for key, label, href in NAV) + '</nav>'


def page(title, eyebrow, lede, body, current=None, extra_css=''):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><style>{font_face_css()}\n{CSS}\n{extra_css}</style></head><body><div class="wrap">'
            f'<header class="top">{nav(current) if current else ""}<span class="eyebrow">{eyebrow}</span><h1>{E(title)}</h1>'
            f'<p class="lede">{lede}</p></header>{body}</div></body></html>')


def kpis(items):
    """items: (value_html, label_html, status or None)"""
    return '<section class="kpis">' + ''.join(
        f'<div class="kpi{" " + st if st else ""}"><span class="v">{v}</span><span class="l">{l}</span></div>' for v, l, st in items) + '</section>'


def section(heading, inner, cls=''):
    return f'<section{f" class={cls!r}" if cls else ""}><h2>{E(heading)}</h2>{inner}</section>'


def table(cols, rows, cls=''):
    """cols: list of (label, 'num'|''); rows: list of lists of cell html (or (html, cls) tuples)."""
    head = ''.join(f'<th{" class=num" if k == "num" else ""}>{E(c)}</th>' for c, k in cols)
    body = []
    for r in rows:
        tr_cls = ''
        if isinstance(r, dict):
            tr_cls, r = r.get('cls', ''), r['cells']
        cells = []
        for (c, k), v in zip(cols, r):
            if isinstance(v, tuple):
                v, extra = v
            else:
                extra = ''
            klass = ' '.join(x for x in (('num' if k == 'num' else ''), extra) if x)
            cells.append(f'<td{f" class={klass!r}" if klass else ""}>{v}</td>')
        body.append(f'<tr{f" class={tr_cls!r}" if tr_cls else ""}>{"".join(cells)}</tr>')
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def bar(pct, status='brand', label=None):
    pct = max(0, min(100, pct))
    lab = label if label is not None else f'{pct:.0f}%'
    pos = f'left:calc({pct:.0f}% + 6px)' if pct < 30 else 'left:6px'
    return f'<div class="bar {status}"><i style="width:{pct:.1f}%"></i><span style="{pos}">{E(lab)}</span></div>'


def stack(parts, title_suffix=''):
    """parts: (count, css color var, label)"""
    return '<div class="stack">' + ''.join(
        f'<i style="flex:{n};background:var({c})" title="{E(l)}: {n}{title_suffix}"></i>' for n, c, l in parts if n) + '</div>'


def finding(tag, status_cls, status, title, body_html, tag_cls=None):
    return (f'<article class="finding"><span class="tag {tag_cls or status_cls}">{E(tag)}</span><div><span class="status {status_cls}">{E(status)}</span>'
            f'<h3>{title}</h3>{body_html}</div></article>')


def write(path, html_text):
    with open(path, 'w') as f:
        f.write(html_text)
    print(f'wrote {os.path.relpath(path, ROOT)} ({os.path.getsize(path) // 1024} KB)')
