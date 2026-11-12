#!/usr/bin/env python3
"""META-KORE project plates: one animated figure per project, same visual system as the header.

Each plate is a pure function of loop position u in [0, 1), so frames loop seamlessly.
`PLATES` maps a name to (frame_count, draw(u) -> list of SVG elements, metadata).
Render with scripts/render-plates.py. Text is outlined via build-assets.text_el.
"""
import math
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ba", ROOT / "scripts" / "build-assets.py")
ba = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ba)

INK, PAPER, ASH, RULE = ba.INK, ba.PAPER, ba.ASH, ba.RULE
W, H, M = 1600, 400, 40


# ---------------------------------------------------------------- helpers
def T(txt, x, y, size=20, fill=ASH, anchor="start", sp=2.4):
    return ba.text_el(txt, x, y, size, fill, ba.FONT_MONO, ba.MONO, sp, anchor)


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def line(x1, y1, x2, y2, stroke=PAPER, w=1.5, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{op:.2f}"' if op < 1 else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}{o}/>'


def rect(x, y, w, h, stroke=PAPER, fill="none", sw=2, op=1.0, rx=0):
    o = f' opacity="{op:.2f}"' if op < 1 else ""
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{r}{o}/>')


def circle(cx, cy, r, stroke=PAPER, fill="none", sw=2, op=1.0):
    o = f' opacity="{op:.2f}"' if op < 1 else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{o}/>')


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
                 for a, b, c, d in zip(p0, p1, p2, p3))


def fade(el, a):
    """Apply opacity to an outlined-text element."""
    if a >= 1:
        return el
    return el.replace("<path ", f'<path opacity="{a:.2f}" ', 1).replace("<text ", f'<text opacity="{a:.2f}" ', 1)


def frame(num, name, right, u, body):
    """Plate chrome: ink field, grid, axis ticks, corner labels, phase readout."""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="{INK}"/>']
    for x in range(M, W - M + 1, 80):
        o.append(line(x, M, x, H - M, RULE, 1))
    for y in range(M, H - M + 1, 80):
        o.append(line(M, y, W - M, y, RULE, 1))
    for x in range(M, W - M + 1, 40):
        ln = 10 if (x - M) % 160 == 0 else 5
        o.append(line(x, H - M, x, H - M - ln, PAPER, 1))
    o += body
    o.append(T(f"PLATE {num:02d} / {name}", M, 30))
    o.append(T(right, W - M, 30, anchor="end"))
    o.append(T(f"PHASE {u * 2 * math.pi:.2f} RAD", M, H - M + 30))
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- 01 allowance
def allowance(u):
    o = []
    y0, gx = 205, 700
    lanes = [(115, "PAY"), (205, "HOLD"), (295, "BLOCK")]
    o.append(line(140, y0, gx, y0, ASH, 1.5))
    for i, (ly, _) in enumerate(lanes):
        d = [None, "8 8", "2 10"][i]
        o.append(f'<path d="M{gx},{y0} C900,{y0} 980,{ly} 1180,{ly}" fill="none" stroke="{ASH}" '
                 f'stroke-width="1.5"' + (f' stroke-dasharray="{d}"' if d else "") + "/>")
    o.append(line(gx, 140, gx, 270, PAPER, 4))
    o.append(T("RULES", gx, 122, anchor="middle"))
    o.append(T("REQUEST", 140, y0 - 22))
    # end markers
    o.append(circle(1180, 115, 9, PAPER, PAPER))
    o.append(line(1172, 193, 1172, 217, PAPER, 4))
    o.append(line(1188, 193, 1188, 217, PAPER, 4))
    o.append(line(1170, 283, 1190, 307, PAPER, 3))
    o.append(line(1190, 283, 1170, 307, PAPER, 3))
    for ly, lab in lanes:
        o.append(T(lab, 1230, ly + 7, 22, PAPER))
    for k in range(3):
        s = (u + k / 3) % 1
        if s < 0.5:
            x, y = lerp(140, gx, s / 0.5), y0
        else:
            ly = lanes[k][0]
            x, y = bez((gx, y0), (900, y0), (980, ly), (1180, ly), (s - 0.5) / 0.5)
        fade = clamp((1 - s) / 0.12) if s > 0.88 else clamp(s / 0.06)
        o.append(circle(x, y, 8, PAPER, PAPER, 1, fade))
        if k == 1 and s > 0.85:  # hold: the owner decides
            o.append(circle(1180, 205, 14 + 10 * ease((s - 0.85) / 0.15), ASH, "none", 1.5,
                            1 - ease((s - 0.85) / 0.15)))
    return frame(1, "ALLOWANCE", "PAY / HOLD / BLOCK", u, o)


# ---------------------------------------------------------------- 02 kitty
def kitty(u):
    o = []
    cx, cy, R, N = 800, 205, 115, 8
    pos = [(cx + R * math.cos(-math.pi / 2 + 2 * math.pi * i / N),
            cy + R * math.sin(-math.pi / 2 + 2 * math.pi * i / N)) for i in range(N)]
    h = int(u * N) % N
    p = (u * N) % 1
    o.append(circle(cx, cy, R, RULE, "none", 1))
    o.append(T("COLLECT", 140, 190))
    o.append(line(140, 205, 660, 205, ASH, 1.5))
    o.append(f'<polygon points="672,205 660,199 660,211" fill="{ASH}"/>')
    o.append(T("PAY OUT", 1460, 190, anchor="end"))
    o.append(line(940, 205, 1460, 205, ASH, 1.5))
    o.append(f'<polygon points="1472,205 1460,199 1460,211" fill="{ASH}"/>')
    for i, (x, y) in enumerate(pos):
        got = (i == h and p > 0.88)
        o.append(circle(x, y, 11, PAPER, PAPER if got else INK, 2))
        if i == h:
            o.append(circle(x, y, 19, ASH, "none", 1.5))
    c = clamp(p / 0.55)
    for i, (x, y) in enumerate(pos):
        if i != h and p < 0.55:
            e = ease(c)
            o.append(circle(lerp(x, cx, e), lerp(y, cy, e), 5, PAPER, PAPER, 1))
    if p < 0.55:
        o.append(circle(cx, cy, 5 + 11 * ease(c), PAPER, "none", 2))
    elif p < 0.88:
        e = ease((p - 0.55) / 0.33)
        o.append(circle(lerp(cx, pos[h][0], e), lerp(cy, pos[h][1], e), 16 - 5 * e, PAPER, PAPER, 1))
    o.append(T(f"CYCLE {h + 1} / {N}", 1460, 330, anchor="end"))
    return frame(2, "KITTY", "ROTATING POT", u, o)


# ---------------------------------------------------------------- 03 tab-shelf
def tab_shelf(u):
    o = []
    rows, x0, w = 6, 360, 720
    ys = [70 + i * 42 for i in range(rows)]
    widths = [300, 220, 360, 260, 330, 200]
    k = int(u * rows) % rows
    p = (u * rows) % 1
    lift = math.sin(math.pi * p)
    for i, y in enumerate(ys):
        ghost = (i == k)
        o.append(rect(x0, y, w, 34, ASH, "none", 1.5, 0.45 if ghost else 1))
        o.append(rect(x0 + 12, y + 10, 14, 14, ASH, "none", 1.5, 0.45 if ghost else 1))
        o.append(line(x0 + 42, y + 17, x0 + 42 + widths[i], y + 17, ASH, 6, None, 0.45 if ghost else 1))
    y = ys[k]
    dx = 150 * lift
    o.append(rect(x0 + dx, y, w, 34, PAPER, INK, 3))
    o.append(rect(x0 + dx + 12, y + 10, 14, 14, PAPER, PAPER, 1.5))
    o.append(line(x0 + dx + 42, y + 17, x0 + dx + 42 + widths[k], y + 17, PAPER, 6))
    o.append(T("SAVED", 140, 100))
    o.append(T("SEARCHABLE", 140, 130))
    o.append(T("KEPT", 140, 160))
    o.append(T("OPENED", 1460, 100, anchor="end"))
    o.append(T("ONE AT A TIME", 1460, 130, anchor="end"))
    return frame(3, "TAB-SHELF", "SHELF", u, o)


# ---------------------------------------------------------------- 04 simple_shell
def simple_shell(u):
    o = []
    labels = ["READ", "TOKENIZE", "PATH", "FORK", "EXECVE"]
    under = ["$ ls -l", "ls | -l", "/bin/ls", "parent+child", "child runs"]
    bw, bh, gap, x0, cy = 200, 70, 70, 160, 170
    a = int(u * 5) % 5
    p = (u * 5) % 1
    for i, lab in enumerate(labels):
        x = x0 + i * (bw + gap)
        active = i == a
        o.append(rect(x, cy - bh / 2, bw, bh, PAPER if i <= a else ASH, PAPER if active else "none", 2))
        o.append(T(lab, x + bw / 2, cy + 8, 22, INK if active else (PAPER if i < a else ASH), "middle", 2))
        o.append(T(under[i], x + bw / 2, cy + 78, 20, PAPER if i <= a else ASH, "middle", 1))
        if i < 4:
            gx1, gx2 = x + bw, x + bw + gap
            o.append(line(gx1, cy, gx2 - 8, cy, ASH, 1.5))
            o.append(f'<polygon points="{gx2},{cy} {gx2 - 10},{cy - 6} {gx2 - 10},{cy + 6}" fill="{ASH}"/>')
    if a < 4 and p > 0.6:
        x = x0 + a * (bw + gap) + bw
        o.append(circle(x + gap * ease((p - 0.6) / 0.4), cy, 7, PAPER, PAPER, 1))
    o.append(T("STDIN", 160, 90))
    o.append(T("STDOUT", 1440, 90, anchor="end"))
    return frame(4, "SIMPLE_SHELL", "COMMAND INTERPRETER", u, o)


# ---------------------------------------------------------------- 05 monty
_MONTY = [("push 1", [], [1]), ("push 2", [1], [1, 2]), ("push 3", [1, 2], [1, 2, 3]),
          ("pall", [1, 2, 3], [1, 2, 3]), ("add", [1, 2, 3], [1, 5]), ("add", [1, 5], [6]),
          ("pop", [6], [])]


def monty(u):
    o = []
    n = len(_MONTY)
    i = int(u * n) % n
    p = (u * n) % 1
    t = ease(p / 0.45)
    o.append(T("BYTECODE", 140, 70))
    for j, (ins, _, _) in enumerate(_MONTY):
        y = 104 + j * 36
        if j == i:
            o.append(rect(128, y - 25, 250, 33, PAPER, PAPER, 1))
        o.append(T(ins, 144, y, 24, INK if j == i else ASH, "start", 1))
    bx, bw, bh, by = 730, 140, 44, 318
    o.append(line(bx - 40, by + 8, bx + bw + 40, by + 8, PAPER, 2))
    o.append(T("STACK", bx + bw / 2, 70, anchor="middle"))
    _, before, after = _MONTY[i]
    op = _MONTY[i][0].split()[0]

    def box(idx, val, dy=0.0, a=1.0):
        y = by - (idx + 1) * (bh + 8) + dy
        o.append(rect(bx, y, bw, bh, PAPER, "none", 2, a))
        o.append(fade(T(str(val), bx + bw / 2, y + 31, 28, PAPER, "middle", 0), a))

    if op == "push":
        for idx, v in enumerate(before):
            box(idx, v)
        box(len(before), after[-1], -70 * (1 - t), t)
    elif op == "add":
        for idx, v in enumerate(before[:-2]):
            box(idx, v)
        box(len(before) - 2, before[-2], 0, 1 - t)
        box(len(before) - 1, before[-1], 0, 1 - t)
        box(len(after) - 1, after[-1], 0, t)
    elif op == "pop":
        box(0, before[0], -70 * t, 1 - t)
    else:  # pall: the stack is unchanged, the output appears
        for idx, v in enumerate(before):
            box(idx, v)
    # output panel: pall prints the stack, top first; it clears when the loop restarts
    o.append(T("STDOUT", 1100, 70))
    a_out = 0.0 if i < 3 else (t if i == 3 else 1.0)
    for r, v in enumerate([3, 2, 1]):
        o.append(fade(T(str(v), 1100, 104 + r * 36, 24, PAPER, "start", 0), a_out))
    o.append(T("LIFO", 1460, 330, anchor="end"))
    return frame(5, "MONTY", "BYTECODE", u, o)


# ---------------------------------------------------------------- 06 sorting_algorithms
def _quick_states(vals):
    a = list(vals)
    states = [(list(a), ())]

    def qs(lo, hi):
        if lo >= hi:
            return
        piv, i = a[hi], lo
        for j in range(lo, hi):
            if a[j] < piv:
                a[i], a[j] = a[j], a[i]
                states.append((list(a), (i, j)))
                i += 1
        a[i], a[hi] = a[hi], a[i]
        states.append((list(a), (i, hi)))
        qs(lo, i - 1)
        qs(i + 1, hi)
    qs(0, len(a) - 1)
    return states


_N = 24
_VALS = [((i * 11 + 5) % _N) + 1 for i in range(_N)]
_STATES = _quick_states(_VALS)
_SORT_FRAMES = 56


def sorting(u):
    o = []
    total = _SORT_FRAMES
    f = int(u * total) % total
    play, hold = 42, 6  # then the last frames reshuffle back to the start
    if f < play:
        si = round(f / (play - 1) * (len(_STATES) - 1))
        arr, act = _STATES[si]
        heights = list(arr)
    elif f < play + hold:
        arr, act = _STATES[-1][0], ()
        heights = list(arr)
    else:
        e = ease((f - play - hold + 1) / (total - play - hold))
        end, start = _STATES[-1][0], _VALS
        heights = [lerp(end[i], start[i], e) for i in range(_N)]
        arr, act = heights, ()
    x0, step, bw, base = 150, (1300 / _N), 34, 330
    done = f >= play - 1 and f < play + hold
    for i, v in enumerate(heights):
        h = 10 + (v / _N) * 235
        x = x0 + i * step
        fill = PAPER if i in act else "none"
        o.append(rect(x, base - h, bw, h, PAPER if (i in act or done) else ASH, fill, 1.5 if i not in act else 2))
    o.append(line(x0 - 10, base + 2, x0 + 1300, base + 2, PAPER, 2))
    return frame(6, "SORTING_ALGORITHMS", "QUICK SORT, STEP BY STEP", u, o)


# ---------------------------------------------------------------- 07 binary_trees
def _tree():
    order = [8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15]
    pos = {}
    for v in range(1, 16):
        depth = 0
        lo, hi, node = 1, 15, 8
        while node != v:
            if v < node:
                hi = node - 1
            else:
                lo = node + 1
            node = (lo + hi) // 2
            depth += 1
        pos[v] = (160 + (v - 1) * (1280 / 14), 88 + depth * 68, depth)
    return order, pos


_ORDER, _POS = _tree()


def _parent(v):
    lo, hi, node = 1, 15, 8
    while node != v:
        par = node
        if v < node:
            hi = node - 1
        else:
            lo = node + 1
        node = (lo + hi) // 2
    return par if v != 8 else None


def binary_trees(u):
    o = []
    build, trav = 0.5, 0.4
    if u < build:
        shown = u / build * len(_ORDER)
        cur = -1
    else:
        shown, cur = len(_ORDER), int((u - build) / trav * 15)
    master = clamp((1 - u) / 0.1) if u > 0.9 else 1.0
    for idx, v in enumerate(_ORDER):
        if idx >= shown:
            continue
        a = clamp(shown - idx) * master
        par = _parent(v)
        if par:
            x1, y1, _ = _POS[par]
            x2, y2, _ = _POS[v]
            o.append(line(x1, y1, x2, y2, ASH, 1.5, None, a))
    for idx, v in enumerate(_ORDER):
        if idx >= shown:
            continue
        a = clamp(shown - idx) * master
        x, y, _ = _POS[v]
        lit = cur >= 0 and (v - 1) <= cur
        o.append(circle(x, y, 19, PAPER, PAPER if lit else INK, 2, a))
        if cur >= 0 and v - 1 == cur:
            o.append(circle(x, y, 27, ASH, "none", 1.5, a))
        o.append(fade(T(str(v), x, y + 7, 20, INK if lit else PAPER, "middle", 0), a))
    o.append(T("INSERT" if u < build else "IN-ORDER WALK", 140, 92))
    return frame(7, "BINARY_TREES", "BST / AVL / HEAP", u, o)


# ---------------------------------------------------------------- 08 daily haiku (private)
def haiku(u):
    o = []
    rows = [(5, 120), (7, 205), (5, 290)]
    total = 17
    n = int(clamp(u / 0.65) * (total + 0.999)) if u < 0.65 else total
    master = clamp((1 - u) / 0.1) if u > 0.9 else 1.0
    c = 0
    for r, (cnt, y) in enumerate(rows):
        span = (cnt - 1) * 64
        xs = 800 - span / 2
        o.append(T(str(cnt), 360, y + 7, 22, ASH, "middle"))
        for k in range(cnt):
            x = xs + k * 64
            filled = c < n
            o.append(circle(x, y, 13, ASH if not filled else PAPER, PAPER if filled else "none", 2, master if filled else 1))
            c += 1
    o.append(T("17 SYLLABLES", 1460, 330, anchor="end"))
    return frame(8, "DAILY HAIKU", "PRIVATE / IN DEVELOPMENT", u, o)


# ---------------------------------------------------------------- 09 actionextract (private)
_TLEN = [380, 300, 420, 260, 340, 400, 280, 360, 320, 390, 250]
_MARK = {2: ("DECISION", 0), 5: ("ACTION", 1), 8: ("ACTION", 2)}


def actionextract(u):
    o = []
    top, step = 84, 24
    scan = clamp(u / 0.75)
    sy = top + scan * (step * len(_TLEN))
    master = clamp((1 - u) / 0.1) if u > 0.9 else 1.0
    o.append(T("TRANSCRIPT", 140, 62))
    o.append(T("DECISIONS + ACTIONS", 900, 62))
    for i, ln in enumerate(_TLEN):
        y = top + i * step + 10
        seen = sy > y
        marked = i in _MARK and seen
        o.append(line(140, y, 140 + ln, y, PAPER if marked else ASH, 6 if marked else 4, None,
                      1 if (marked or not seen) else 0.55))
    if scan < 1:
        o.append(line(128, sy, 600, sy, PAPER, 1.5))
    for i, (lab, slot) in _MARK.items():
        y = top + i * step + 10
        when = (y - top) / (step * len(_TLEN)) * 0.75
        a = ease((u - when - 0.02) / 0.08) * master
        if a <= 0:
            continue
        cy = 96 + slot * 84
        o.append(line(140 + _TLEN[i] + 14, y, 900, cy + 28, ASH, 1, "3 6", a))
        o.append(rect(900, cy, 540, 56, PAPER, "none", 2, a))
        o.append(fade(T(lab, 920, cy + 35, 20, PAPER, "start", 2), a))
        if lab == "ACTION":
            o.append(circle(1130, cy + 28, 11, PAPER, "none", 2, a))
            o.append(line(1158, cy + 28, 1280, cy + 28, ASH, 6, None, a))
            o.append(rect(1340, cy + 12, 70, 32, PAPER, "none", 1.5, a))
            o.append(line(1340, cy + 22, 1410, cy + 22, PAPER, 1.5, None, a))
        else:
            o.append(line(1100, cy + 28, 1400, cy + 28, ASH, 6, None, a))
    return frame(9, "ACTIONEXTRACT", "PRIVATE / TRANSCRIPT TO ACTIONS", u, o)


# name -> (frames, draw, file stem)
PLATES = {
    "allowance": (36, allowance),
    "kitty": (48, kitty),
    "tab-shelf": (48, tab_shelf),
    "simple-shell": (40, simple_shell),
    "monty": (48, monty),
    "sorting": (_SORT_FRAMES, sorting),
    "binary-trees": (60, binary_trees),
    "daily-haiku": (48, haiku),
    "actionextract": (48, actionextract),
}
