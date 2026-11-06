"""Chapter banners for the quantum computing book. Run: python3 banners.py

Writes assets/banners/<chapter>.svg. Each banner is an original, text-free drawing of the
chapter's anchor example, 1200x400. Marks use the .cb-* classes in assets/book.css, so the
SVG (inlined by build.py) follows the light and dark themes. No ids or scripts.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'assets' / 'banners'
W, H = 1200, 400


def svg(body):
    return (f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" class="cb-bg"/>{body}</svg>\n')


def line(x1, y1, x2, y2, cls='cb-line'):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"/>'


def circle(x, y, r, cls):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" class="{cls}"/>'


def rect(x, y, w, h, cls, rx=0):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" class="{cls}"/>'


def path(points, cls, close=False):
    return f'<path d="M{" L".join(f"{x:.1f},{y:.1f}" for x, y in points)}{" Z" if close else ""}" class="{cls}"/>'


def curve(x1, y1, x2, y2, cls, bend=0.5):
    mx = x1 + (x2 - x1) * bend
    return f'<path d="M{x1:.1f},{y1:.1f} C{mx:.1f},{y1:.1f} {mx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" class="{cls}"/>'


def arrow(x1, y1, x2, y2, cls='cb-line', head=11):
    a = math.atan2(y2 - y1, x2 - x1)
    tip = [(x2 - head * math.cos(a - .45), y2 - head * math.sin(a - .45)), (x2, y2),
           (x2 - head * math.cos(a + .45), y2 - head * math.sin(a + .45))]
    return line(x1, y1, x2, y2, cls) + path(tip, cls)


def grid(step=40):
    return ''.join([line(x, 0, x, H, 'cb-grid') for x in range(0, W + 1, step)] +
                   [line(0, y, W, y, 'cb-grid') for y in range(0, H + 1, step)])


def oplus(x, y, r=13, cls='cb-1'):
    return circle(x, y, r, cls + ' cb-hollow') + line(x - r, y, x + r, y, cls) + line(x, y - r, x, y + r, cls)


def gate(x, y, w=44, h=44, cls='cb-box'):
    return rect(x - w / 2, y - h / 2, w, h, cls, 6)


def split(x, y, half=22, cls='cb-1', merge=False):
    """Two paths leaving one point (or, with merge, joining at one): the action of a Hadamard step."""
    a, b = (x + half, x - half) if merge else (x - half, x + half)
    out = path([(a, y), (b, y - half * .8)], cls) + path([(a, y), (b, y + half * .8)], cls)
    return out + circle(a, y, 4, 'cb-f1') + circle(b, y - half * .8, 4, 'cb-f1') + circle(b, y + half * .8, 4, 'cb-f1')


def meter(x, y, cls='cb-1'):
    return (gate(x, y, 54, 44) + f'<path d="M{x-17},{y+8} A18,18 0 0 1 {x+17},{y+8}" class="{cls}"/>'
            + line(x, y + 8, x + 11, y - 9, cls))


# ---------------------------------------------------------------- chapters

def logic_computability():
    """A machine head on a tape, its finite control, and a proof tree that may never close."""
    out = [grid()]
    states = [(150, 120), (110, 270), (270, 200)]
    for (a, b) in ((0, 2), (2, 1), (1, 0)):
        out.append(curve(*states[a], *states[b], 'cb-line', 0.5))
    out.append(f'<path d="M290,175 A26,26 0 1 1 300,215" class="cb-line"/>')
    for k, (x, y) in enumerate(states):
        out.append(circle(x, y, 26, 'cb-f1' if k == 2 else 'cb-node'))
    out.append(arrow(320, 200, 405, 250, 'cb-1', 12))
    rnd = random.Random(1936)
    for k in range(8):
        x = 360 + k * 62
        out.append(rect(x, 270, 56, 56, 'cb-box', 4))
        mark = rnd.random()
        if mark < .45: out.append(rect(x + 18, 288, 20, 20, 'cb-f1', 3))
        elif mark < .7: out.append(circle(x + 28, 298, 10, 'cb-f2'))
    out.append(path([(424, 236), (444, 262), (464, 236)], 'cb-f2', True))
    # proof tree growing upward from axioms
    def tree(x, y, depth, spread):
        if depth == 0:
            out.append(circle(x, y, 5, 'cb-fm'))
            return
        for s in (-1, 1):
            nx, ny = x + s * spread, y - 46
            out.append(line(x, y, nx, ny, 'cb-thin'))
            tree(nx, ny, depth - 1, spread * .55)
        out.append(circle(x, y, 6, 'cb-f1'))
    tree(1035, 330, 4, 80)
    return svg(''.join(out))


def boolean_reversible():
    """An irreversible gate merges inputs; a reversible one permutes them."""
    out = [grid()]
    ys = [80, 160, 240, 320]
    for y in ys:
        out.append(circle(120, y, 14, 'cb-node'))
    out.append(circle(380, 140, 16, 'cb-f2'))
    out.append(circle(380, 290, 16, 'cb-f1'))
    for y in ys[:3]:
        out.append(curve(134, y, 364, 140, 'cb-2'))
    out.append(curve(134, ys[3], 364, 290, 'cb-1'))
    # reversible: eight configurations, a permutation that swaps the last two (Toffoli)
    x0, x1 = 640, 940
    yy = [40 + k * 46 for k in range(8)]
    for k, y in enumerate(yy):
        out.append(circle(x0, y, 11, 'cb-node'))
        out.append(circle(x1, y, 11, 'cb-f1' if k >= 6 else 'cb-node'))
        j = {6: 7, 7: 6}.get(k, k)
        out.append(curve(x0 + 11, y, x1 - 11, yy[j], 'cb-1' if k >= 6 else 'cb-thin'))
    # the circuit that implements it
    for k, y in enumerate((130, 200, 270)):
        out.append(line(1010, y, 1170, y, 'cb-line'))
    out.append(line(1090, 130, 1090, 283, 'cb-1'))
    out.append(circle(1090, 130, 8, 'cb-f1'))
    out.append(circle(1090, 200, 8, 'cb-f1'))
    out.append(oplus(1090, 270))
    return svg(''.join(out))


def amplitudes_interference():
    """Two steps through two configurations: paths to 1 cancel, paths to 0 add."""
    out = [grid()]
    cols = [140, 520, 900]
    rows = {0: 120, 1: 280}
    for c in cols:
        out.append(line(c, 70, c, 330, 'cb-grid-strong'))
    out.append(curve(cols[0], rows[0], cols[1], rows[0], 'cb-1'))
    out.append(curve(cols[0], rows[0], cols[1], rows[1], 'cb-1'))
    out.append(curve(cols[1], rows[0], cols[2], rows[0], 'cb-1'))
    out.append(curve(cols[1], rows[1], cols[2], rows[0], 'cb-1'))
    out.append(curve(cols[1], rows[0], cols[2], rows[1], 'cb-1'))
    out.append(curve(cols[1], rows[1], cols[2], rows[1], 'cb-2d'))
    out.append(circle(cols[0], rows[0], 22, 'cb-f1'))
    out.append(circle(cols[0], rows[1], 18, 'cb-node'))
    out.append(circle(cols[1], rows[0], 17, 'cb-w1s'))
    out.append(circle(cols[1], rows[1], 17, 'cb-w1s'))
    out.append(circle(cols[2], rows[0], 30, 'cb-w1'))
    out.append(circle(cols[2], rows[0], 22, 'cb-f1'))
    out.append(circle(cols[2], rows[1], 18, 'cb-hollow2'))
    out.append(line(cols[2] - 12, rows[1] - 12, cols[2] + 12, rows[1] + 12, 'cb-2'))
    out.append(line(cols[2] - 12, rows[1] + 12, cols[2] + 12, rows[1] - 12, 'cb-2'))
    # amplitude bars: before and after
    for k, (h, cls) in enumerate(((110, 'cb-f1'), (0, 'cb-f1'))):
        out.append(rect(1010 + k * 60, 330 - h, 40, h, cls, 3))
    out.append(line(995, 330, 1130, 330, 'cb-axis'))
    return svg(''.join(out))


def states_measurement():
    """A state vector on the unit circle, its projections, and the outcome probabilities."""
    out = [grid()]
    cx, cy, r = 330, 330, 260
    out.append(f'<path d="M{cx+r},{cy} A{r},{r} 0 0 0 {cx},{cy-r}" class="cb-thin"/>')
    out.append(arrow(cx - 20, cy, cx + r + 50, cy, 'cb-axis', 12))
    out.append(arrow(cx, cy + 20, cx, cy - r - 30, 'cb-axis', 12))
    th = math.radians(58)
    px, py = cx + r * math.cos(th), cy - r * math.sin(th)
    out.append(f'<path d="M{cx},{cy} L{cx+r},{cy} A{r},{r} 0 0 0 {px:.1f},{py:.1f} Z" class="cb-w1"/>')
    out.append(line(px, py, px, cy, 'cb-2d'))
    out.append(line(px, py, cx, py, 'cb-2d'))
    out.append(arrow(cx, cy, px, py, 'cb-1', 16))
    out.append(circle(px, cy, 7, 'cb-f2'))
    out.append(circle(cx, py, 7, 'cb-f2'))
    # Born rule: squared lengths as outcome bars
    for k, p in enumerate((math.cos(th) ** 2, math.sin(th) ** 2)):
        out.append(rect(800 + k * 120, 330 - 260 * p, 70, 260 * p, 'cb-f1' if k else 'cb-f2', 4))
    out.append(line(770, 330, 1040, 330, 'cb-axis'))
    return svg(''.join(out))


def quantum_model():
    """Prepare, evolve, measure: one qubit through H, Z, H, read out as a histogram."""
    out = [grid()]
    y = 200
    out.append(line(80, y, 900, y, 'cb-line'))
    out.append(circle(80, y, 12, 'cb-f1'))
    for x, cls in ((260, 'cb-box'), (450, 'cb-box2'), (640, 'cb-box')):
        out.append(gate(x, y, 76, 76, cls))
    # inside the gates: H as a split, Z as a sign flip, H as a recombination
    out.append(split(260, y, 24))
    out.append(arrow(450, y + 24, 450, y - 24, 'cb-2', 10))
    out.append(split(640, y, 24, merge=True))
    out.append(meter(820, y))
    out.append(line(850, y + 4, 900, y + 4, 'cb-line') + line(850, y - 4, 900, y - 4, 'cb-line'))
    for k, h in enumerate((4, 220)):
        out.append(rect(960 + k * 90, 320 - h, 60, h, 'cb-f1' if k else 'cb-fm', 4))
    out.append(line(940, 320, 1130, 320, 'cb-axis'))
    return svg(''.join(out))


def composite_systems():
    """A Bell circuit on two wires, and the four joint amplitudes it produces."""
    out = [grid()]
    ya, yb = 140, 270
    for y in (ya, yb):
        out.append(line(80, y, 640, y, 'cb-line'))
        out.append(circle(80, y, 11, 'cb-f1'))
    out.append(gate(220, ya, 64, 64))
    out.append(split(220, ya, 20))
    out.append(line(400, ya, 400, yb + 14, 'cb-1'))
    out.append(circle(400, ya, 10, 'cb-f1'))
    out.append(oplus(400, yb, 15))
    out.append(curve(560, ya, 640, ya, 'cb-2d'))
    # 2x2 grid of joint configurations 00 01 / 10 11 ; correlated ones filled
    x0, y0, s = 760, 70, 130
    for i in range(2):
        for j in range(2):
            on = i == j
            out.append(rect(x0 + j * s, y0 + i * s, s - 16, s - 16, 'cb-box', 8))
            if on:
                out.append(circle(x0 + j * s + (s - 16) / 2, y0 + i * s + (s - 16) / 2, 38, 'cb-f1'))
            else:
                out.append(circle(x0 + j * s + (s - 16) / 2, y0 + i * s + (s - 16) / 2, 6, 'cb-fm'))
    out.append(curve(x0 + 57, y0 + 57, x0 + s + 57, y0 + s + 57, 'cb-2d', 0.5))
    return svg(''.join(out))


def queries_phase_kickback():
    """A query box on two wires; the target's phase kicks back onto the control."""
    out = [grid()]
    ya, yb = 130, 280
    for y in (ya, yb):
        out.append(line(80, y, 1000, y, 'cb-line'))
    out.append(circle(80, ya, 11, 'cb-f1'))
    out.append(circle(80, yb, 11, 'cb-f2'))
    out.append(gate(220, ya, 60, 60))
    out.append(gate(220, yb, 60, 60))
    out.append(rect(420, ya - 50, 200, yb - ya + 100, 'cb-box2', 10))
    for k in range(5):
        out.append(rect(450 + k * 30, ya - 12 + (k % 2) * 8, 18, 18, 'cb-f1' if k % 2 else 'cb-fm', 3))
    # the target state |-> drawn as a wave with a sign flip
    out.append(path([(660 + t, yb - 26 * math.sin(t / 12)) for t in range(0, 241, 4)], 'cb-2'))
    # phase kickback arrow from target up to control
    out.append(f'<path d="M700,{yb-40} C760,{yb-110} 760,{ya+70} 700,{ya+18}" class="cb-2d"/>')
    out.append(arrow(712, ya + 32, 700, ya + 16, 'cb-2', 12))
    out.append(gate(850, ya, 60, 60))
    out.append(meter(960, ya))
    out.append(circle(1060, ya, 26, 'cb-f1'))
    out.append(circle(1140, ya, 26, 'cb-hollow1'))
    return svg(''.join(out))


def circuits_universality():
    """A small gate set on the left composes into a deep circuit on the right."""
    out = [grid()]
    # the gate set
    out.append(rect(60, 70, 230, 260, 'cb-w1', 12))
    out.append(gate(120, 140, 56, 56))
    out.append(split(120, 140, 18))
    out.append(gate(230, 140, 56, 56, 'cb-box2'))
    out.append(f'<path d="M212,152 A20,20 0 0 1 248,140" class="cb-2"/>')
    out.append(line(175, 220, 175, 290, 'cb-1'))
    out.append(circle(175, 220, 9, 'cb-f1'))
    out.append(oplus(175, 290, 14))
    out.append(arrow(310, 200, 380, 200, 'cb-1', 14))
    # composed circuit
    wires = [70, 135, 200, 265, 330]
    for y in wires:
        out.append(line(400, y, 1160, y, 'cb-line'))
    rnd = random.Random(8)
    x = 430
    while x < 1140:
        kind = rnd.random()
        if kind < .4:
            a, b = rnd.sample(range(5), 2)
            out.append(line(x, wires[a], x, wires[b], 'cb-1'))
            out.append(circle(x, wires[a], 7, 'cb-f1'))
            out.append(oplus(x, wires[b], 11))
        else:
            for wi in rnd.sample(range(5), rnd.randint(1, 3)):
                out.append(gate(x, wires[wi], 34, 34, 'cb-box2' if rnd.random() < .4 else 'cb-box'))
        x += 46
    return svg(''.join(out))


def amplitude_amplification():
    """Grover rotations in the plane of the marked and unmarked states, and four-item search."""
    out = [grid()]
    cx, cy, r = 120, 300, 260
    out.append(arrow(cx - 10, cy, cx + r + 40, cy, 'cb-axis', 12))
    out.append(arrow(cx, cy + 10, cx, cy - r - 10, 'cb-axis', 12))
    out.append(f'<path d="M{cx+r},{cy} A{r},{r} 0 0 0 {cx},{cy-r}" class="cb-thin"/>')
    th = math.asin(0.5)  # four items: sin(theta) = 1/2
    for k, cls in ((0, 'cb-thin'), (1, 'cb-1')):
        a = (2 * k + 1) * th
        out.append(arrow(cx, cy, cx + r * math.cos(a) + (8 if k else 0), cy - r * math.sin(a), cls if k else 'cb-1t', 14))
        if k: out.append(circle(cx + r * math.cos(a) + 8, cy - r * math.sin(a) + 10, 9, 'cb-f1'))
    a0, a1 = th, 3 * th
    out.append(f'<path d="M{cx+170*math.cos(a0):.1f},{cy-170*math.sin(a0):.1f} A170,170 0 0 0 {cx+170*math.cos(a1):.1f},{cy-170*math.sin(a1):.1f}" class="cb-2"/>')
    # reflection about the unmarked axis, dashed
    out.append(line(cx, cy, cx + .55 * r * math.cos(-th), cy - .55 * r * math.sin(-th), 'cb-2d'))
    # four items: before and after one iteration
    for k in range(4):
        out.append(rect(620 + k * 56, 330 - 70, 40, 70, 'cb-fm' if k != 2 else 'cb-f2', 3))
        out.append(rect(900 + k * 56, 330 - (240 if k == 2 else 4), 40, 240 if k == 2 else 4, 'cb-f1' if k == 2 else 'cb-fm', 3))
    out.append(line(600, 330, 1140, 330, 'cb-axis'))
    out.append(arrow(840, 200, 880, 200, 'cb-1', 12))
    return svg(''.join(out))


def complexity_advantage():
    """Nested resource classes, and query costs N against the square root of N."""
    out = [grid()]
    cx, cy = 330, 210
    for (rx, ry, cls) in ((260, 170, 'cb-w2'), (200, 130, 'cb-w1'), (130, 86, 'cb-w1'), (70, 48, 'cb-f1o')):
        out.append(f'<ellipse cx="{cx - (260 - rx) * .35:.1f}" cy="{cy:.1f}" rx="{rx}" ry="{ry}" class="{cls}"/>')
        out.append(f'<ellipse cx="{cx - (260 - rx) * .35:.1f}" cy="{cy:.1f}" rx="{rx}" ry="{ry}" class="cb-thin"/>')
    rnd = random.Random(10)
    for _ in range(26):
        a, t = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random())
        out.append(circle(cx + 240 * t * math.cos(a), cy + 150 * t * math.sin(a), 4, 'cb-fm'))
    # query lower bound: N vs sqrt N
    x0, y0, x1, y1 = 720, 340, 1150, 60
    out.append(path([(x0, y1), (x0, y0), (x1, y0)], 'cb-axis'))
    out.append(path([(x0, y0), (x1, y1)], 'cb-2'))
    out.append(path([(x0 + t, y0 - (y0 - y1) * math.sqrt(t / (x1 - x0)) * 0.55) for t in range(0, x1 - x0 + 1, 6)], 'cb-1'))
    for t in (0.25, 0.5, 0.75, 1.0):
        x = x0 + t * (x1 - x0)
        out.append(circle(x, y0 - (y0 - y1) * math.sqrt(t) * 0.55, 6, 'cb-f1'))
        out.append(circle(x, y0 - (y0 - y1) * t, 6, 'cb-f2'))
    return svg(''.join(out))


BANNERS = {
    '01-logic-computability': (logic_computability, 'Illustration: a machine reading a tape of symbols under the control of three states, beside a tree of deductions branching upward from axioms.'),
    '02-boolean-reversible-computation': (boolean_reversible, 'Illustration: an irreversible gate sending three of four inputs to one output, beside a reversible gate that permutes eight configurations, swapping the last two, and the Toffoli circuit that does it.'),
    '03-amplitudes-interference': (amplitudes_interference, 'Illustration: a configuration that splits into two paths and recombines over two steps; the paths into one outcome cancel and the paths into the other add.'),
    '04-states-measurement': (states_measurement, 'Illustration: a state vector on the unit circle with its projections onto the two axes, and bars showing the squared lengths as measurement probabilities.'),
    '05-quantum-model': (quantum_model, 'Illustration: one qubit prepared, passed through three gates that split, flip the sign of and recombine its paths, then measured, with the outcomes shown as a histogram.'),
    '06-composite-systems': (composite_systems, 'Illustration: a two-wire circuit with a Hadamard gate and a controlled-NOT, beside a two-by-two grid of joint configurations in which only the matching pairs carry amplitude.'),
    '07-queries-phase-kickback': (queries_phase_kickback, 'Illustration: a query box acting on a control wire and a target wire, with an arrow showing the target phase kicked back onto the control before it is measured.'),
    '08-circuits-universality': (circuits_universality, 'Illustration: a small set of gates on the left composed into a deep five-wire circuit on the right.'),
    '09-amplitude-amplification': (amplitude_amplification, 'Illustration: a state vector rotating toward the marked axis in the plane of marked and unmarked states, and four bars in which one iteration moves all the weight to the marked item.'),
    '10-complexity-advantage': (complexity_advantage, 'Illustration: nested regions for complexity classes, beside two growth curves comparing a cost proportional to N with one proportional to the square root of N.'),
}

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for stem, (draw, _) in BANNERS.items():
        (OUT / f'{stem}.svg').write_text(draw())
        print('wrote', stem)
