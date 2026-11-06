"""Chapter banners for the Quantum Algorithms course. Run: python3 banners.py

Writes assets/banners/<chapter>.svg. Each banner is an original, text-free drawing of the
chapter's anchor example (chapters.json "example"), 1200x400, using the .cb-* classes in
education/computing/assets/book.css and the drawing helpers of the Quantum Computing banners.
"""
import importlib.util
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('computing_banners', HERE.parent / 'computing' / 'banners.py')
_cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cb)
W, H = _cb.W, _cb.H
svg, line, circle, rect, path, curve, arrow, grid = _cb.svg, _cb.line, _cb.circle, _cb.rect, _cb.path, _cb.curve, _cb.arrow, _cb.grid
oplus, gate, meter, split = _cb.oplus, _cb.gate, _cb.meter, _cb.split
OUT = HERE / 'assets' / 'banners'


def bars(x0, base, values, width=34, gap=14, scale=1.0, colours=None):
    out = []
    for k, v in enumerate(values):
        cls = (colours or {}).get(k, 'cb-f1')
        h = abs(v) * scale
        out.append(rect(x0 + k * (width + gap), base - h if v >= 0 else base, width, max(h, 3), cls, 3))
    return ''.join(out)


# ---------------------------------------------------------------- chapters

def algorithmic_thinking():
    """The design chain on Deutsch's problem: access, interference, readout."""
    out = [grid()]
    ya, yb = 150, 270
    for y in (ya, yb):
        out.append(line(70, y, 980, y, 'cb-line'))
    out.append(circle(70, ya, 11, 'cb-f1'))
    out.append(circle(70, yb, 11, 'cb-f2'))
    out.append(gate(190, ya, 56, 56) + split(190, ya, 18))
    out.append(gate(190, yb, 56, 56) + split(190, yb, 18))
    out.append(rect(330, ya - 46, 150, yb - ya + 92, 'cb-box2', 10))
    for k, v in enumerate((0, 1)):  # the hidden function f(0), f(1)
        out.append(rect(370 + k * 46, ya + 30, 26, 26, 'cb-f2' if v else 'cb-fm', 4))
    # interference: the two branches recombine into one certain answer
    out.append(curve(520, ya - 40, 640, ya, 'cb-1') + curve(520, ya + 40, 640, ya, 'cb-1'))
    out.append(gate(680, ya, 56, 56) + split(680, ya, 18, merge=True))
    out.append(meter(820, ya))
    out.append(line(850, ya + 4, 980, ya + 4, 'cb-line') + line(850, ya - 4, 980, ya - 4, 'cb-line'))
    out.append(rect(1040, 330 - 230, 50, 230, 'cb-f1', 4) + rect(1110, 326, 50, 4, 'cb-fm'))
    out.append(line(1020, 330, 1180, 330, 'cb-axis'))
    return svg(''.join(out))


def coherent_computation():
    """Compute, copy, uncompute: the workspace returns clean."""
    out = [grid()]
    ys = [100, 200, 300]  # input, workspace, output
    for y in ys:
        out.append(line(70, y, 1130, y, 'cb-line'))
    out.append(rect(330, 175, 460, 50, 'cb-w2', 6))  # workspace in use
    out.append(rect(250, 70, 140, 160, 'cb-box', 10))
    out.append(rect(730, 70, 140, 160, 'cb-box', 10))
    out.append(path([(285, 175), (320, 120), (355, 175)], 'cb-1'))
    out.append(path([(765, 120), (800, 175), (835, 120)], 'cb-1'))
    out.append(line(560, 200, 560, 314, 'cb-1') + circle(560, 200, 9, 'cb-f1') + oplus(560, 300, 14))
    out.append(circle(70, 100, 11, 'cb-f1'))
    out.append(circle(70, 200, 11, 'cb-hollow1'))
    out.append(circle(70, 300, 11, 'cb-hollow1'))
    out.append(circle(1130, 100, 11, 'cb-f1'))
    out.append(circle(1130, 200, 11, 'cb-hollow1'))
    out.append(circle(1130, 300, 11, 'cb-f2'))
    return svg(''.join(out))


def phase_encoding():
    """A predicate written as signs on amplitudes, then read through Hadamards."""
    out = [grid()]
    base = 210
    out.append(line(60, base, 520, base, 'cb-axis'))
    signs = [(-1) ** bin(5 & x).count('1') for x in range(8)]  # (-1)^(a.x) with a = 101
    out.append(bars(80, base, [s * 90 for s in signs], 40, 16, colours={k: 'cb-f2' for k, s in enumerate(signs) if s < 0}))
    out.append(arrow(560, base, 660, base, 'cb-1', 14))
    out.append(gate(610, base - 70, 50, 50) + split(610, base - 70, 16))
    out.append(line(700, 330, 1150, 330, 'cb-axis'))
    # after the Hadamard readout: weight concentrated on the labels the pattern selects
    after = [4, 4, 4, 4, 4, 200, 4, 4]  # H on every qubit sends the whole state to label a = 5
    out.append(bars(720, 330, after, 40, 16, colours={k: 'cb-fm' for k in range(8) if k != 5}))
    return svg(''.join(out))


def fourier_methods():
    """A periodic pattern on eight labels, the eighth roots of unity, and the frequency peaks."""
    out = [grid()]
    base = 300
    out.append(line(60, base, 470, base, 'cb-axis'))
    pattern = [150 if k % 4 == 1 else 4 for k in range(8)]
    out.append(bars(80, base, pattern, 34, 16))
    cx, cy, r = 600, 200, 110
    out.append(circle(cx, cy, r, 'cb-thin'))
    for k in range(8):
        a = 2 * math.pi * k / 8
        out.append(line(cx, cy, cx + r * math.cos(a), cy - r * math.sin(a), 'cb-thin'))
        out.append(circle(cx + r * math.cos(a), cy - r * math.sin(a), 8, 'cb-f2' if k % 2 == 0 else 'cb-fm'))
    out.append(arrow(cx, cy, cx + r * math.cos(math.pi / 2), cy - r * math.sin(math.pi / 2), 'cb-2', 12))
    out.append(line(760, base, 1160, base, 'cb-axis'))
    freq = [150 if k % 2 == 0 else 4 for k in range(8)]
    out.append(bars(780, base, freq, 34, 16, colours={k: 'cb-f1' for k in range(8)}))
    return svg(''.join(out))


def amplitude_manipulation():
    """A nonuniform preparation; two reflections rotate the state toward the good outcome."""
    out = [grid()]
    base = 320
    out.append(line(60, base, 470, base, 'cb-axis'))
    prep = [120, 160, 90, 30, 140, 110]
    out.append(bars(80, base, prep, 44, 20, colours={3: 'cb-f2'}))
    cx, cy, r = 540, 330, 260
    out.append(arrow(cx - 10, cy, cx + r + 30, cy, 'cb-axis', 12))
    out.append(arrow(cx, cy + 10, cx, cy - r - 20, 'cb-axis', 12))
    th = math.radians(11)
    for k, cls in ((0, 'cb-1t'), (1, 'cb-1t'), (2, 'cb-1')):
        a = (2 * k + 1) * th
        out.append(arrow(cx, cy, cx + r * math.cos(a), cy - r * math.sin(a), cls, 13))
    out.append(line(cx, cy, cx + .6 * r * math.cos(-th), cy - .6 * r * math.sin(-th), 'cb-2d'))
    out.append(line(900, base, 1160, base, 'cb-axis'))
    after = [30, 40, 22, 200, 35, 28]
    out.append(bars(915, base, after, 30, 12, colours={3: 'cb-f1', 0: 'cb-fm', 1: 'cb-fm', 2: 'cb-fm', 4: 'cb-fm', 5: 'cb-fm'}))
    return svg(''.join(out))


def quantum_walks():
    """A walk on an eight-vertex cycle with a marked vertex; quantum and classical spreads compared."""
    out = [grid()]
    cx, cy, r = 260, 200, 140
    pts = [(cx + r * math.cos(2 * math.pi * k / 8), cy + r * math.sin(2 * math.pi * k / 8)) for k in range(8)]
    for k in range(8):
        out.append(line(*pts[k], *pts[(k + 1) % 8], 'cb-line'))
    weights = [0.9, 0.5, 0.3, 0.2, 0.15, 0.2, 0.3, 0.5]
    for k, (x, y) in enumerate(pts):
        if k == 4:
            out.append(circle(x, y, 26, 'cb-w2') + circle(x, y, 13, 'cb-f2'))
        else:
            out.append(circle(x, y, 8 + 18 * weights[k], 'cb-w1') + circle(x, y, 7, 'cb-f1'))
    out.append(f'<path d="M{cx+r+30},{cy-50} A{r+30},{r+30} 0 0 1 {cx+r-10},{cy+90}" class="cb-2d"/>')
    # spread on a line after t steps: classical bell vs quantum two-peaked
    x0, x1, base = 560, 1160, 330
    out.append(line(x0, base, x1, base, 'cb-axis'))
    mid = (x0 + x1) / 2
    out.append(path([(x, base - 200 * math.exp(-((x - mid) / 60) ** 2)) for x in range(x0, x1 + 1, 6)], 'cb-2'))
    q = lambda x: 230 * (math.exp(-((x - mid + 220) / 28) ** 2) + math.exp(-((x - mid - 220) / 28) ** 2)) + 40 * abs(math.sin((x - mid) / 14)) * (abs(x - mid) < 200)
    out.append(path([(x, base - q(x)) for x in range(x0, x1 + 1, 4)], 'cb-1'))
    return svg(''.join(out))


def operator_embedding():
    """A scaled two-by-two matrix in the corner of a unitary, selected by an auxiliary qubit."""
    out = [grid()]
    x0, y0, s = 120, 50, 75
    for i in range(4):
        for j in range(4):
            corner = i < 2 and j < 2
            out.append(rect(x0 + j * s, y0 + i * s, s - 8, s - 8, 'cb-w1' if corner else 'cb-box', 6))
            out.append(circle(x0 + j * s + (s - 8) / 2, y0 + i * s + (s - 8) / 2, 14 if corner else 6, 'cb-f1' if corner else 'cb-fm'))
    out.append(rect(x0 - 10, y0 - 10, 2 * s + 12, 2 * s + 12, 'cb-1', 10))
    ya, yb = 140, 270
    out.append(line(560, ya, 1100, ya, 'cb-line') + line(560, yb, 1100, yb, 'cb-line'))
    out.append(circle(560, ya, 11, 'cb-hollow2'))
    out.append(circle(560, yb, 11, 'cb-f1'))
    out.append(rect(720, ya - 46, 180, yb - ya + 92, 'cb-box', 10))
    out.append(rect(752, yb - 22, 116, 44, 'cb-w1', 6))
    out.append(meter(1000, ya, 'cb-2'))
    out.append(circle(1100, ya, 11, 'cb-hollow2'))
    out.append(circle(1100, yb, 11, 'cb-f1'))
    return svg(''.join(out))


def polynomial_transformations():
    """Alternating signal and phase steps on one wire, and the low-degree filter they build."""
    out = [grid()]
    y = 110
    out.append(line(60, y, 1140, y, 'cb-line'))
    for k in range(9):
        x = 110 + k * 120
        if k % 2 == 0:
            out.append(gate(x, y, 48, 48, 'cb-box2'))
            out.append(f'<path d="M{x-14},{y+8} A16,16 0 0 1 {x+14},{y-4}" class="cb-2"/>')
        else:
            out.append(gate(x, y, 48, 48))
            out.append(line(x - 14, y, x + 14, y, 'cb-1') + circle(x, y, 5, 'cb-f1'))
    # filter: spectrum on [-1, 1] mapped through a smooth step polynomial
    x0, x1, base, top = 160, 1040, 350, 200
    out.append(line(x0, base, x1, base, 'cb-axis'))
    def poly(t):  # odd smooth step on [-1, 1], degree-limited look
        return 0.5 + 0.5 * math.tanh(4.2 * t) * (1 - 0.06 * math.cos(9 * t))
    out.append(path([(x0 + (t + 1) / 2 * (x1 - x0), base - (base - top) * poly(t)) for t in [i / 100 - 1 for i in range(201)]], 'cb-1'))
    rnd = random.Random(8)
    for t in sorted(rnd.uniform(-0.95, 0.95) for _ in range(11)):
        x = x0 + (t + 1) / 2 * (x1 - x0)
        out.append(circle(x, base, 6, 'cb-f2'))
        out.append(line(x, base - 8, x, base - (base - top) * poly(t) + 8, 'cb-2d'))
    return svg(''.join(out))


def evolution_engineering():
    """Alternating X and Z evolutions; finer steps track the target path more closely."""
    out = [grid()]
    y = 90
    out.append(line(60, y, 1140, y, 'cb-line'))
    for k in range(12):
        out.append(rect(90 + k * 88, y - 22, 76, 44, 'cb-w1' if k % 2 == 0 else 'cb-w2', 6))
        out.append(rect(90 + k * 88, y - 22, 76, 44, 'cb-box2' if k % 2 else 'cb-hollow1', 6))
    # target trajectory and its product-formula approximations
    x0, x1 = 80, 1120
    target = lambda t: 300 - 110 * math.sin(math.pi * t) - 30 * t
    out.append(path([(x0 + t * (x1 - x0), target(t)) for t in [i / 200 for i in range(201)]], 'cb-1'))
    for steps, cls in ((4, 'cb-thin'), (12, 'cb-2')):
        pts = [(x0, target(0))]
        for k in range(steps):
            t0, t1 = k / steps, (k + 1) / steps
            pts.append((x0 + t1 * (x1 - x0), pts[-1][1]))
            pts.append((x0 + t1 * (x1 - x0), target(t1)))
        out.append(path(pts, cls))
    return svg(''.join(out))


def variational_methods():
    """A parameterized two-qubit circuit in a loop with an optimizer descending an energy curve."""
    out = [grid()]
    ya, yb = 130, 240
    for yy in (ya, yb):
        out.append(line(70, yy, 600, yy, 'cb-line'))
        out.append(circle(70, yy, 10, 'cb-f1'))
    for x in (170, 400):
        for yy in (ya, yb):
            out.append(gate(x, yy, 52, 52))
            out.append(circle(x, yy, 15, 'cb-thin') + line(x, yy, x + 11, yy - 11, 'cb-2'))
    out.append(line(285, ya, 285, yb + 14, 'cb-1') + circle(285, ya, 9, 'cb-f1') + oplus(285, yb, 14))
    out.append(meter(520, ya) + meter(520, yb))
    out.append(f'<path d="M560,{yb+40} C560,370 170,370 170,{yb+40}" class="cb-2d"/>')
    out.append(arrow(176, yb + 60, 170, yb + 32, 'cb-2', 12))
    # energy landscape and descent
    x0, x1 = 680, 1160
    # screen y grows downward, so the valley (minimum energy) is the largest y
    E = lambda t: 130 + 190 * math.exp(-((t - .62) / .2) ** 2) - 60 * (t - .5) ** 2 + 40 * math.exp(-((t - .18) / .08) ** 2)
    out.append(path([(x0 + t * (x1 - x0), E(t)) for t in [i / 200 for i in range(201)]], 'cb-line'))
    ts = [.3, .4, .48, .55, .6, .62]
    for k, t in enumerate(ts):
        out.append(circle(x0 + t * (x1 - x0), E(t), 6 + k, 'cb-f2' if k < len(ts) - 1 else 'cb-f1'))
    return svg(''.join(out))


def adaptive_measurement():
    """Iterative phase estimation: one reused auxiliary qubit, each round corrected by earlier bits."""
    out = [grid()]
    ya, yb = 130, 260
    out.append(line(60, yb, 1140, yb, 'cb-line'))
    out.append(rect(60, yb - 16, 1080, 32, 'cb-w1', 6))
    for k in range(3):
        x = 110 + k * 340
        out.append(line(x - 30, ya, x + 230, ya, 'cb-line'))
        out.append(circle(x - 30, ya, 9, 'cb-hollow1'))
        out.append(gate(x + 20, ya, 44, 44) + split(x + 20, ya, 14))
        out.append(line(x + 90, ya, x + 90, yb - 16, 'cb-1') + circle(x + 90, ya, 8, 'cb-f1'))
        out.append(rect(x + 60, yb - 24, 60 + 18 * k, 48, 'cb-box', 6))
        if k:
            out.append(gate(x + 150, ya, 44, 44, 'cb-box2'))
            out.append(f'<path d="M{x-150},{ya-40} C{x-60},{ya-80} {x+100},{ya-80} {x+150},{ya-24}" class="cb-2d"/>')
        out.append(meter(x + 200, ya))
        out.append(circle(x + 200, ya - 60, 10, 'cb-f2' if k != 1 else 'cb-fm'))
    return svg(''.join(out))


BANNERS = {
    '01-quantum-algorithmic-thinking': (algorithmic_thinking, "Illustration: Deutsch's problem as a design: two prepared wires pass a query box holding the hidden function, their branches recombine, and a measurement gives one certain answer."),
    '02-coherent-computation': (coherent_computation, 'Illustration: compute, copy and uncompute on three wires; the workspace wire is in use between the two mirrored blocks and returns clean at the end.'),
    '03-phase-encoding': (phase_encoding, 'Illustration: eight amplitudes whose signs follow a hidden bit pattern, then a Hadamard readout that sends all the weight to the label naming that pattern.'),
    '04-fourier-methods': (fourier_methods, 'Illustration: a periodic amplitude pattern on eight labels, the eight phases on a circle, and the frequency peaks the Fourier transform produces.'),
    '05-amplitude-manipulation': (amplitude_manipulation, 'Illustration: a nonuniform preparation with a small good outcome, two reflections rotating the state toward it, and the amplified result.'),
    '06-quantum-walks': (quantum_walks, 'Illustration: a walk on an eight-vertex cycle with one marked vertex, beside the spread after many steps: a single classical bell against two fast quantum peaks.'),
    '07-operator-embedding': (operator_embedding, 'Illustration: a four-by-four unitary whose top-left two-by-two block holds the scaled matrix, and the circuit that selects it with an auxiliary qubit returned to zero.'),
    '08-polynomial-transformations': (polynomial_transformations, 'Illustration: alternating signal and phase steps on one wire, and the smooth low-degree filter they apply to every eigenvalue of an encoded operator.'),
    '09-evolution-engineering': (evolution_engineering, 'Illustration: alternating evolution blocks on a wire, and a target trajectory approximated by coarse and fine staircases of alternating steps.'),
    '10-variational-methods': (variational_methods, 'Illustration: a parameterized two-qubit circuit with rotation dials and a measurement loop back to its parameters, beside an energy curve the optimizer descends.'),
    '11-adaptive-measurement': (adaptive_measurement, 'Illustration: one reused auxiliary qubit measured in three rounds, each controlling a growing power of the evolution and corrected by the bits already read.'),
}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, (draw, _) in BANNERS.items():
        (OUT / f'{stem}.svg').write_text(draw())
        print('wrote', stem)
