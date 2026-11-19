"""@font-face rules with the app's own fonts embedded as data URIs, so generated report
pages render the same offline (no Google Fonts request). Fonts: theme/web/mxcli-fonts/
(JetBrains Mono and Geist, both under the SIL Open Font License, see the OFL files there)."""
import base64
import os

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'theme', 'web', 'mxcli-fonts')
FACES = [('JetBrains Mono', 400, 'jetbrains-mono-latin-400-normal.woff2'), ('JetBrains Mono', 600, 'jetbrains-mono-latin-600-normal.woff2'),
         ('JetBrains Mono', 700, 'jetbrains-mono-latin-700-normal.woff2'), ('Geist', 400, 'geist-latin-400-normal.woff2'),
         ('Geist', 500, 'geist-latin-500-normal.woff2'), ('Geist', 600, 'geist-latin-600-normal.woff2')]


def font_face_css():
    out = []
    for family, weight, fn in FACES:
        data = base64.b64encode(open(os.path.join(FONTS, fn), 'rb').read()).decode()
        out.append(f'@font-face {{ font-family: "{family}"; font-style: normal; font-weight: {weight}; font-display: swap; '
                   f'src: url(data:font/woff2;base64,{data}) format("woff2"); }}')
    return '\n'.join(out)
