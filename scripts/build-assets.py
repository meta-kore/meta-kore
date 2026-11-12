#!/usr/bin/env python3
"""Generate META-KORE identity assets.

Text is converted to outlines when fontTools and the fonts below are available
(pip install fonttools), so the SVG and GIF look identical everywhere. Without
them it falls back to live <text>, which depends on installed fonts.

Usage: python scripts/build-assets.py
Writes assets/identity/header.svg and assets/identity/mark.svg.
`header(phase)` is reusable for animation frames later.
"""
import math
from pathlib import Path

INK, PAPER, ASH, RULE = "#0A0A0B", "#F2EFE8", "#8B9098", "#2A2C30"
W, H, M = 1600, 500, 40
SANS = "'Space Grotesk','Inter','Helvetica Neue',Arial,sans-serif"
MONO = "'IBM Plex Mono','JetBrains Mono',Consolas,monospace"

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "identity"

FONT_SANS = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
_fonts = {}


def _font(fp):
    if fp not in _fonts:
        try:
            from fontTools.ttLib import TTFont
            _fonts[fp] = TTFont(fp) if Path(fp).exists() else None
        except ImportError:
            _fonts[fp] = None
    return _fonts[fp]


def text_el(txt, x, y, size, fill, fontfile, family, spacing=0.0, anchor="start", weight=None):
    """Outlined text as one <path>; live <text> fallback if the font is unavailable."""
    f = _font(fontfile)
    if f is None:
        w = f' font-weight="{weight}"' if weight else ""
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        return (f'<text x="{x}" y="{y}"{a} fill="{fill}" font-family="{family}" '
                f'font-size="{size}"{w} letter-spacing="{spacing}">{txt}</text>')
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    k = size / f["head"].unitsPerEm
    names = [cmap[ord(c)] for c in txt]
    total = sum(hmtx[n][0] * k + spacing for n in names) - spacing
    cx = x - (total if anchor == "end" else 0)
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}")
    for n in names:
        gs[n].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += hmtx[n][0] * k + spacing
    return f'<path fill="{fill}" d="{pen.getCommands()}"/>'


def path(points):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)


def wave(phase, y0, amp, freq, harmonics, x0=M, x1=W - M, n=400):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        env = math.sin(math.pi * t) ** 0.8  # taper toward the edges
        v = sum(a * math.sin(2 * math.pi * (freq * k * t) + phase * k + k * 0.7)
                for k, a in harmonics)
        pts.append((x, y0 + amp * env * v))
    return pts


def header(phase=0.0):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" aria-labelledby="t d">',
         '<title id="t">META-KORE</title>',
         '<desc id="d">Plotted waveforms on a black field with the wordmark META-KORE.</desc>',
         f'<rect width="{W}" height="{H}" fill="{INK}"/>']

    # fine grid
    for x in range(M, W - M + 1, 80):
        o.append(f'<line x1="{x}" y1="{M}" x2="{x}" y2="{H-M}" stroke="{RULE}" stroke-width="1"/>')
    for y in range(M, H - M + 1, 80):
        o.append(f'<line x1="{M}" y1="{y}" x2="{W-M}" y2="{y}" stroke="{RULE}" stroke-width="1"/>')

    # waveform family: faint ash traces plus one paper emphasis trace
    for i in range(7):
        h = [(1, 1.0), (2, 0.45 - i * 0.03), (3, 0.2 + i * 0.02)]
        pts = wave(phase + i * 0.35, 330, 85, 2.0 + i * 0.12, h)
        o.append(f'<path d="{path(pts)}" fill="none" stroke="{ASH}" stroke-opacity="0.55" stroke-width="1"/>')
    main = wave(phase, 330, 85, 2.0, [(1, 1.0), (2, 0.45), (3, 0.2)])
    o.append(f'<path d="{path(main)}" fill="none" stroke="{PAPER}" stroke-width="3" stroke-linejoin="round"/>')

    # sample markers on the main trace
    for i in range(0, len(main), 40):
        x, y = main[i]
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{INK}" stroke="{PAPER}" stroke-width="2"/>')

    # axis ticks
    for x in range(M, W - M + 1, 40):
        l = 12 if (x - M) % 160 == 0 else 6
        o.append(f'<line x1="{x}" y1="{H-M}" x2="{x}" y2="{H-M-l}" stroke="{PAPER}" stroke-width="1"/>')

    # wordmark (outlined)
    o.append(text_el("META-KORE", M, 190, 140, PAPER, FONT_SANS, SANS, -4, weight=700))

    # annotations
    def lab(t, x, y, anchor="start"):
        return text_el(t, x, y, 20, ASH, FONT_MONO, MONO, 2.4, anchor)
    o.append(lab("00 / INDEX", M, M + 4))
    o.append(lab("SOFTWARE · INTELLIGENCE · SYSTEMS · EXPERIMENTS", W - M, M + 4, "end"))
    o.append(lab(f"PHASE {phase:.2f} RAD", M, H - M + 30))
    o.append(lab("A WORKBENCH IN PUBLIC", W - M, H - M + 30, "end"))
    o.append("</svg>")
    return "\n".join(o)


def mark():
    """MK monogram: two plotted strokes on a 200 square."""
    s = 200
    k = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}" '
         f'role="img" aria-label="MK mark"><rect width="{s}" height="{s}" fill="{INK}"/>'
         f'<path d="M40,150 L40,50 L100,110 L100,50" fill="none" stroke="{PAPER}" stroke-width="6" stroke-linejoin="miter"/>'
         f'<path d="M118,50 L118,150 M118,100 L160,50 M118,100 L160,150" fill="none" stroke="{PAPER}" stroke-width="6"/>'
         f'<circle cx="100" cy="110" r="5" fill="{INK}" stroke="{PAPER}" stroke-width="3"/></svg>')
    return k


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "header.svg").write_text(header(0.0), encoding="utf-8")
    (OUT / "mark.svg").write_text(mark(), encoding="utf-8")
    print("wrote", OUT / "header.svg", OUT / "mark.svg")
