"""Draw the article banners. Run: python3 draw_banners.py (writes <slug>/banner.svg beside it).

Banners are original, text-free illustrations of each story's subject, 1200x400.
Marks use the .fig-* classes from news/editorial.css, so the inlined SVG follows the
site theme; no ids, scripts or event handlers (the build rejects them).
"""
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 1200, 400


def svg(body):
    return (f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" class="fig-bg"/>{body}</svg>\n')


def line(x1, y1, x2, y2, cls='fig-link'):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"/>'


def circle(x, y, r, cls):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}"/>'


def rect(x, y, w, h, cls, rx=0):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" class="{cls}"/>'


def path(points, cls, close=False):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points) + (' Z' if close else '')
    return f'<path d="{d}" class="{cls}"/>'


def grid(x0, y0, x1, y1, step, cls='fig-grid'):
    out = [line(x, y0, x, y1, cls) for x in range(int(x0), int(x1) + 1, step)]
    out += [line(x0, y, x1, y, cls) for y in range(int(y0), int(y1) + 1, step)]
    return ''.join(out)


def arrow(x1, y1, x2, y2, cls='fig-link', head=12):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.45), y2 - head * math.sin(a - 0.45))
    p2 = (x2 - head * math.cos(a + 0.45), y2 - head * math.sin(a + 0.45))
    return line(x1, y1, x2, y2, cls) + path([p1, (x2, y2), p2], cls)


# ---------------------------------------------------------------- banners

def cat_qubits():
    """Two coherent-state lobes with interference fringes, beside a field of qubits."""
    out = [grid(0, 0, W, H, 40)]
    cx, cy = 300, 200
    for dx in (-130, 130):
        for r, cls in ((96, 'fig-wash-1'), (64, 'fig-wash-1'), (34, 'fig-fill-1')):
            out.append(circle(cx + dx, cy, r, cls))
    for k in range(-5, 6):
        x = cx + k * 11
        h = 70 * math.cos(k * math.pi / 5.5) ** 2 + 18
        out.append(line(x, cy - h, x, cy + h, 'fig-line-2' if k % 2 == 0 else 'fig-grid'))
    rnd = random.Random(2048)
    for i in range(26):
        for j in range(11):
            x, y = 640 + i * 21, 60 + j * 28
            cls = 'fig-fill-1' if rnd.random() < 0.82 else 'fig-fill-muted'
            out.append(circle(x + (j % 2) * 10, y, 5, cls))
    return svg(''.join(out))


def qubit_count():
    """Two chips: a large noisy array and a small reliable one, with error bars beneath."""
    out = [grid(0, 0, W, H, 40)]
    rnd = random.Random(7)
    out.append(rect(80, 50, 560, 300, 'fig-box', 10))
    for i in range(16):
        for j in range(8):
            bad = rnd.random() < 0.35
            out.append(circle(115 + i * 33, 85 + j * 33, 8, 'fig-hollow' if bad else 'fig-fill-muted'))
    out.append(rect(760, 110, 210, 180, 'fig-box-claimed', 10))
    for i in range(4):
        for j in range(3):
            out.append(circle(800 + i * 44, 150 + j * 50, 11, 'fig-fill-1'))
    for k, h in enumerate((150, 120, 95, 60, 38, 22)):
        out.append(rect(1010 + k * 26, 330 - h, 16, h, 'fig-fill-2' if k < 3 else 'fig-fill-1'))
    out.append(line(1000, 330, 1170, 330, 'fig-axis'))
    return svg(''.join(out))


def qec_platform():
    """A square-lattice processor and a GPU rack joined by a fast feedback loop."""
    out = [grid(0, 0, W, H, 40)]
    x0, y0, s = 110, 80, 40
    for i in range(7):
        for j in range(7):
            x, y = x0 + i * s, y0 + j * s
            if i < 6: out.append(line(x, y, x + s, y, 'fig-link'))
            if j < 6: out.append(line(x, y, x, y + s, 'fig-link'))
    for i in range(7):
        for j in range(7):
            out.append(circle(x0 + i * s, y0 + j * s, 9, 'fig-fill-1' if (i + j) % 2 else 'fig-node'))
    out.append(rect(860, 70, 240, 260, 'fig-box', 8))
    for k in range(6):
        y = 92 + k * 39
        out.append(rect(882, y, 196, 28, 'fig-wash-2', 4))
        for m in range(8):
            out.append(rect(894 + m * 22, y + 8, 14, 12, 'fig-fill-2', 2))
    # feedback loop: measurements out (top), corrections back (bottom)
    out.append(path([(400, 140), (520, 90), (720, 90), (850, 140)], 'fig-line-1'))
    out.append(arrow(820, 125, 852, 140, 'fig-line-1', 16))
    out.append(path([(850, 260), (720, 310), (520, 310), (400, 260)], 'fig-line-2'))
    out.append(arrow(430, 275, 398, 260, 'fig-line-2', 16))
    for x in range(470, 790, 60):
        out.append(circle(x, 90, 5, 'fig-fill-1'))
        out.append(circle(x + 30, 310, 5, 'fig-fill-2'))
    return svg(''.join(out))


def india_mission():
    """Four connected hubs: computing, communication, sensing and materials."""
    out = [grid(0, 0, W, H, 40)]
    hubs = [(210, 200), (480, 110), (720, 290), (990, 200)]
    for a in range(4):
        for b in range(a + 1, 4):
            out.append(line(*hubs[a], *hubs[b], 'fig-grid'))
    for x, y in hubs:
        out.append(circle(x, y, 92, 'fig-wash-1'))
    x, y = hubs[0]  # computing: a small qubit lattice
    for i in range(4):
        for j in range(4):
            out.append(circle(x - 45 + i * 30, y - 45 + j * 30, 7, 'fig-fill-1'))
    x, y = hubs[1]  # communication: a fibre carrying a wave
    out.append(line(x - 70, y, x + 70, y, 'fig-axis'))
    out.append(path([(x - 70 + t, y - 26 * math.sin(t / 9)) for t in range(0, 141, 3)], 'fig-line-2'))
    x, y = hubs[2]  # sensing: concentric field rings around a probe
    for r in (18, 36, 54, 72):
        out.append(circle(x, y, r, 'fig-measure'))
    out.append(circle(x, y, 8, 'fig-fill-2'))
    x, y = hubs[3]  # materials: a hexagonal crystal
    for i in range(-1, 2):
        for j in range(-1, 2):
            cx, cy = x + i * 46 + (j % 2) * 23, y + j * 40
            hexa = [(cx + 24 * math.cos(math.pi / 3 * k + math.pi / 6), cy + 24 * math.sin(math.pi / 3 * k + math.pi / 6)) for k in range(6)]
            out.append(path(hexa, 'fig-link', True))
            out.append(circle(cx, cy, 4, 'fig-fill-1'))
    return svg(''.join(out))


def intel_classiq():
    """A software stack descending onto a spin-qubit chip."""
    out = [grid(0, 0, W, H, 40)]
    for k, w in enumerate((560, 470, 380)):
        x, y = 600 - w / 2, 30 + k * 52
        out.append(rect(x, y, w, 40, 'fig-wash-1', 6))
        out.append(rect(x, y, w, 40, 'fig-box-claimed' if k == 0 else 'fig-box', 6))
        rnd = random.Random(k)
        cx = x + 18
        while cx < x + w - 40:
            seg = rnd.choice((22, 34, 48))
            out.append(rect(cx, y + 15, seg, 10, 'fig-fill-1' if k == 0 else 'fig-fill-muted', 3))
            cx += seg + 12
    out.append(arrow(600, 190, 600, 226, 'fig-line-1', 14))
    out.append(rect(330, 232, 540, 140, 'fig-box', 10))
    for m in range(13):
        x = 360 + m * 40
        out.append(line(x, 232, x, 218, 'fig-axis'))
        out.append(line(x, 372, x, 386, 'fig-axis'))
    for row in range(2):
        y = 276 + row * 52
        out.append(line(370, y, 830, y, 'fig-grid'))
        for m in range(12):
            out.append(circle(390 + m * 38, y, 10, 'fig-fill-1' if (m + row) % 3 else 'fig-fill-2'))
    return svg(''.join(out))


def mbqc():
    """A cluster state measured column by column; outcomes feed forward."""
    out = [grid(0, 0, W, H, 40)]
    cols, rows, x0, y0, s = 13, 5, 120, 80, 80
    for i in range(cols):
        for j in range(rows):
            x, y = x0 + i * s, y0 + j * s
            if i < cols - 1: out.append(line(x, y, x + s, y, 'fig-grid' if i < 5 else 'fig-link'))
            if j < rows - 1: out.append(line(x, y, x, y + s, 'fig-grid' if i < 5 else 'fig-link'))
    for i in range(cols):
        for j in range(rows):
            x, y = x0 + i * s, y0 + j * s
            if i < 5:
                out.append(circle(x, y, 10, 'fig-fill-muted'))
            elif i == 5:
                out.append(circle(x, y, 12, 'fig-fill-2'))
                out.append(line(x - 10, y + 10, x + 10, y - 10, 'fig-cross'))
            else:
                out.append(circle(x, y, 10, 'fig-node'))
    out.append(path([(x0 + 5 * s, 30), (x0 + 6.5 * s, 30)], 'fig-line-2'))
    out.append(arrow(x0 + 6.3 * s, 30, x0 + 7 * s, 30, 'fig-line-2', 12))
    return svg(''.join(out))


def new_york():
    """A central research hub linked to regional hubs, over a faint street grid."""
    out = [grid(0, 0, W, H, 40)]
    hub = (600, 210)
    regions = [(200, 120), (330, 300), (470, 90), (760, 320), (900, 110), (1030, 260)]
    rnd = random.Random(23)
    for x, y in regions:
        out.append(line(*hub, x, y, 'fig-link'))
        for _ in range(5):
            a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(28, 56)
            out.append(line(x, y, x + r * math.cos(a), y + r * math.sin(a), 'fig-grid'))
            out.append(circle(x + r * math.cos(a), y + r * math.sin(a), 4, 'fig-fill-muted'))
        out.append(circle(x, y, 22, 'fig-wash-2'))
        out.append(circle(x, y, 10, 'fig-fill-2'))
    for r, cls in ((88, 'fig-wash-1'), (56, 'fig-wash-1'), (30, 'fig-fill-1')):
        out.append(circle(*hub, r, cls))
    return svg(''.join(out))


def eth():
    """Exponential curves that only change their base, and one that bends away."""
    out = [grid(0, 0, W, H, 40)]
    x0, y0, x1, y1 = 80, 360, 1140, 40
    out.append(path([(x0, y1), (x0, y0), (x1, y0)], 'fig-axis'))
    def curve(f, cls):
        pts = []
        for k in range(0, 401):
            t = k / 400
            v = f(t)
            pts.append((x0 + t * (x1 - x0), y0 - min(v, 1.0) * (y0 - y1)))
            if v >= 1.0: break
        return path(pts, cls)
    # c^n family: same shape, the base only moves where each curve leaves the panel
    for exit_t in (0.28, 0.4, 0.52, 0.64):
        a = 6.0 / exit_t
        out.append(curve(lambda t, a=a: (math.exp(a * t) - 1) / (math.exp(6.0) - 1), 'fig-ref'))
    out.append(curve(lambda t: (math.exp(6.0 / 0.76 * t) - 1) / (math.exp(6.0) - 1), 'fig-line-1'))
    # subexponential: exponent grows like n / sqrt(log n), so the curve keeps bending away
    out.append(curve(lambda t: (math.exp(5.2 * t / math.sqrt(0.35 + t)) - 1) / (math.exp(6.0) - 1) * 0.9, 'fig-line-2'))
    return svg(''.join(out))


def yang_mills():
    """A gauge lattice with link variables, one highlighted plaquette and a flux tube."""
    out = []
    x0, y0, s = 60, 40, 80
    for i in range(15):
        for j in range(5):
            x, y = x0 + i * s, y0 + j * s
            if i < 14: out.append(arrow(x + 12, y, x + s - 12, y, 'fig-link', 8))
            if j < 4: out.append(arrow(x, y + 12, x, y + s - 12, 'fig-link', 8))
    for a, b in ((2, 1), (3, 1), (3, 2), (2, 2)):
        out.append(rect(x0 + a * s + 4, y0 + b * s + 4, s - 8, s - 8, 'fig-wash-1', 4))
    out.append(rect(x0 + 3 * s + 4, y0 + 1 * s + 4, s - 8, s - 8, 'fig-wash-1', 4))
    for (a, b, c, d) in ((3, 1, 4, 1), (4, 1, 4, 2), (4, 2, 3, 2), (3, 2, 3, 1)):
        out.append(arrow(x0 + a * s, y0 + b * s, x0 + c * s, y0 + d * s, 'fig-line-1', 14))
    qa, qb = (x0 + 8 * s, y0 + 2 * s), (x0 + 12 * s, y0 + 2 * s)
    out.append(rect(qa[0], qa[1] - 26, qb[0] - qa[0], 52, 'fig-wash-2', 26))
    for k in range(-1, 2):
        out.append(line(qa[0] + 20, qa[1] + 11 * k, qb[0] - 20, qb[1] + 11 * k, 'fig-line-2'))
    for i in range(15):
        for j in range(5):
            out.append(circle(x0 + i * s, y0 + j * s, 5, 'fig-node'))
    for x, y in (qa, qb):
        out.append(circle(x, y, 16, 'fig-fill-2'))
    return svg(''.join(out))


def pentagon():
    """An evaluation staircase: many entrants, fewer at each stage, a few at the top."""
    out = [grid(0, 0, W, H, 40)]
    steps = [(80, 330, 340), (420, 250, 320), (740, 170, 380)]
    for x, y, w in steps:
        out.append(rect(x, y, w, H - y, 'fig-box', 0))
    rnd = random.Random(350)
    for k in range(20):
        out.append(circle(110 + (k % 10) * 30, 300 - (k // 10) * 26, 9, 'fig-fill-muted'))
    for k in range(10):
        out.append(circle(450 + (k % 5) * 50, 222 - (k // 5) * 26, 9, 'fig-node'))
    for k in range(6):
        out.append(circle(790 + k * 52, 142, 11, 'fig-fill-1'))
    out.append(arrow(330, 290, 440, 230, 'fig-line-2', 14))
    out.append(arrow(680, 210, 780, 150, 'fig-line-2', 14))
    return svg(''.join(out))


def color_code():
    """Triangular colour codes at distances 3, 5 and 7, built from three-coloured faces."""
    out = [grid(0, 0, W, H, 40)]
    def triangle(cx, base, d, size):
        rows = d
        h = size * math.sqrt(3) / 2
        cls = ['fig-wash-1', 'fig-wash-2', 'fig-fill-muted-soft']
        for r in range(rows):
            for c in range(r + 1):
                x = cx + (c - r / 2) * size
                y = base - (rows - 1 - r) * h
                up = [(x, y - h * 0.62), (x - size / 2, y + h * 0.38), (x + size / 2, y + h * 0.38)]
                out.append(path(up, cls[(r + 2 * c) % 3], True))
                out.append(path(up, 'fig-link', True))
                out.append(circle(x, y - h * 0.62, 4, 'fig-fill-1'))
        return h
    triangle(200, 300, 3, 70)
    triangle(520, 320, 5, 56)
    triangle(930, 340, 7, 46)
    return svg(''.join(out))


def quantum_safe():
    """A two-dimensional lattice with a skewed basis, a hidden closest point, and a padlock."""
    out = []
    a, b = (70, -16), (24, -56)
    for i in range(-12, 22):
        for j in range(-8, 14):
            x, y = 40 + i * a[0] + j * b[0], 380 + i * a[1] + j * b[1]
            if -10 < x < W + 10 and -10 < y < H + 10:
                out.append(circle(x, y, 5, 'fig-fill-muted'))
    ox, oy = 40 + 4 * a[0] + 2 * b[0], 380 + 4 * a[1] + 2 * b[1]
    out.append(arrow(ox, oy, ox + 2 * a[0], oy + 2 * a[1], 'fig-line-1', 14))
    out.append(arrow(ox, oy, ox + 2 * b[0], oy + 2 * b[1], 'fig-line-1', 14))
    out.append(circle(ox, oy, 8, 'fig-fill-1'))
    tx, ty = ox + 4.4 * a[0] + 1.45 * b[0], oy + 4.4 * a[1] + 1.45 * b[1]
    out.append(circle(tx, ty, 46, 'fig-measure'))
    out.append(circle(tx, ty, 9, 'fig-fill-2'))
    lx, ly = 900, 90
    out.append(rect(lx - 30, ly - 20, 240, 270, 'fig-bg', 12))
    out.append(f'<path d="M{lx+30},{ly+80} V{ly+40} A60,60 0 0 1 {lx+150},{ly+40} V{ly+80}" class="fig-line-1"/>')
    out.append(rect(lx, ly + 80, 180, 140, 'fig-box-claimed', 14))
    out.append(circle(lx + 90, ly + 140, 14, 'fig-fill-1'))
    out.append(rect(lx + 84, ly + 146, 12, 40, 'fig-fill-1', 3))
    return svg(''.join(out))


def aaronson_ambainis():
    """A cube of inputs with one influential direction, and the classical query tree it allows."""
    out = [grid(0, 0, W, H, 40)]
    # four-dimensional cube drawn as two offset three-dimensional cubes
    base = [(0, 0), (150, 0), (0, 150), (150, 150)]
    def cube(ox, oy):
        front = [(ox + x, oy + y) for x, y in base]
        back = [(x + 60, y - 45) for x, y in front]
        return front + back
    a, b = cube(90, 150), cube(330, 190)
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    for (i, j) in edges:
        out.append(line(*a[i], *a[j], 'fig-link'))
        out.append(line(*b[i], *b[j], 'fig-link'))
    for k in range(8):  # the influential coordinate: edges joining the two cubes
        out.append(line(*a[k], *b[k], 'fig-line-1'))
    rnd = random.Random(2008)
    for p in a + b:
        out.append(circle(*p, 9, 'fig-fill-1' if rnd.random() < .5 else 'fig-node'))
    out.append(arrow(700, 220, 780, 220, 'fig-line-2', 14))
    # classical decision tree: query the influential bit, fix it, repeat
    def tree(x, y, depth, spread):
        if depth == 0:
            out.append(rect(x - 9, y - 9, 18, 18, 'fig-fill-muted', 3))
            return
        for sgn in (-1, 1):
            nx, ny = x + sgn * spread, y + 80
            out.append(line(x, y, nx, ny, 'fig-link'))
            tree(nx, ny, depth - 1, spread / 2)
        out.append(circle(x, y, 13, 'fig-fill-2' if depth == 3 else 'fig-fill-1'))
    tree(980, 70, 3, 112)
    return svg(''.join(out))


def mip_re():
    """A verifier questioning two entangled provers, and a chain of ever smaller games feeding back on itself."""
    out = [grid(0, 0, W, H, 40)]
    out.append(rect(40, 40, 460, 320, 'fig-wash-1', 18))
    pa, pb, v = (130, 110), (130, 290), (390, 200)
    # entanglement between the provers: a wave joining them, no line to the verifier
    wave = [(pa[0] - 30 + 14 * math.sin(k / 3), pa[1] + 24 + k * (pb[1] - pa[1] - 48) / 24) for k in range(25)]
    out.append(path(wave, 'fig-line-2'))
    for p in (pa, pb):
        out.append(arrow(v[0] - 46, v[1] + (p[1] - v[1]) * .25 - 8, p[0] + 34, p[1] - 8, 'fig-link', 12))
        out.append(arrow(p[0] + 34, p[1] + 8, v[0] - 46, v[1] + (p[1] - v[1]) * .25 + 8, 'fig-line-1', 12))
        out.append(circle(*p, 26, 'fig-fill-1'))
    out.append(rect(v[0] - 40, v[1] - 40, 80, 80, 'fig-box', 8))
    # compression: each game simulated by an exponentially smaller one
    x, size, boxes = 560, 210, []
    while size > 14:
        boxes.append((x, 200, size))
        x += size + 40
        size *= .55
    for i, (bx, by, s) in enumerate(boxes):
        out.append(rect(bx, by - s / 2, s, s, 'fig-wash-2' if i else 'fig-box', 6))
        out.append(grid(bx + s / 4, by - s / 4, bx + 3 * s / 4, by + s / 4, max(4, int(s / 6)), 'fig-grid'))
        if i + 1 < len(boxes):
            nx = boxes[i + 1][0]
            out.append(arrow(bx + s + 6, by, nx - 8, by, 'fig-line-1', 10))
    # self-reference: the smallest game hands back to the first
    lx, _, ls = boxes[-1]
    fx = boxes[0][0] + boxes[0][2] / 2
    out.append(path([(lx + ls / 2, 200 + ls / 2 + 6), (lx + ls / 2, 345), (fx, 345)], 'fig-line-2'))
    out.append(arrow(fx, 345, fx, 200 + boxes[0][2] / 2 + 6, 'fig-line-2', 12))
    return svg(''.join(out))


def verified_programs():
    """Quantum circuit wires with gates on the left, feeding a proof tree whose root is checked."""
    out = [grid(0, 0, W, H, 40)]
    out.append(rect(40, 60, 560, 280, 'fig-wash-1', 18))
    rnd = random.Random(2611)
    ys = [100 + 50 * k for k in range(5)]
    for y in ys:
        out.append(line(70, y, 570, y, 'fig-link'))
    for x in range(110, 560, 62):
        a = rnd.randrange(5)
        if rnd.random() < .45 and a < 4:  # two-qubit gate: control dot and target box
            b = a + 1 + rnd.randrange(4 - a)
            out.append(line(x, ys[a], x, ys[b], 'fig-line-1'))
            out.append(circle(x, ys[a], 6, 'fig-fill-1'))
            out.append(rect(x - 13, ys[b] - 13, 26, 26, 'fig-box', 4))
        else:
            out.append(rect(x - 14, ys[a] - 14, 28, 28, 'fig-fill-2' if rnd.random() < .3 else 'fig-box', 4))
    out.append(arrow(615, 200, 690, 200, 'fig-line-2', 14))
    # proof tree: leaves at the bottom, root at the top right
    leaves = [(740 + 60 * k, 320) for k in range(8)]
    level = leaves
    for p in leaves:
        out.append(rect(p[0] - 10, p[1] - 10, 20, 20, 'fig-fill-muted', 3))
    while len(level) > 1:
        nxt = []
        for k in range(0, len(level), 2):
            (x1, y1), (x2, y2) = level[k], level[k + 1]
            px, py = (x1 + x2) / 2, y1 - 70
            out.append(line(x1, y1 - 10, px, py + 10, 'fig-link'))
            out.append(line(x2, y2 - 10, px, py + 10, 'fig-link'))
            nxt.append((px, py))
        for q in nxt:
            out.append(circle(*q, 11 if len(nxt) > 1 else 22, 'fig-node' if len(nxt) > 1 else 'fig-fill-1'))
        level = nxt
    rx, ry = level[0]
    out.append(path([(rx - 10, ry), (rx - 3, ry + 8), (rx + 11, ry - 9)], 'fig-line-2'))
    return svg(''.join(out))


BANNERS = {
    'google-ai-formally-verified-quantum-programs': verified_programs,
    'mip-star-equals-re-verified': mip_re,
    'alice-bob-rsa-2048-cat-qubits': cat_qubits,
    'psi-aaronson-ambainis-conjecture': aaronson_ambainis,
    'beyond-the-qubit-count': qubit_count,
    'ibm-ornl-amd-error-correction-platform': qec_platform,
    'indias-quantum-mission': india_mission,
    'intel-to-acquire-classiq': intel_classiq,
    'measurement-based-quantum-computing-introduction': mbqc,
    'new-york-quantum-study': new_york,
    'openai-exponential-time-hypothesis': eth,
    'openai-yang-mills-existence': yang_mills,
    'pentagon-quantum-350-million': pentagon,
    'quantinuum-color-code-error-record': color_code,
    'quantum-safe-security': quantum_safe,
}

if __name__ == '__main__':
    for slug, draw in BANNERS.items():
        folder = HERE / slug
        folder.mkdir(exist_ok=True)
        (folder / 'banner.svg').write_text(draw())
        print('wrote', slug + '/banner.svg')
