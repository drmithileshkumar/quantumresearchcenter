"""Draw the figures for the Yang–Mills article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
"""
import math
from pathlib import Path
from html import escape

HERE = Path(__file__).resolve().parent


def svg(width, height, body):
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{body}</svg>\n'


def text(x, y, s, cls='fig-text', anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def path(points, cls, title=None):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)
    tip = f'<title>{escape(title)}</title>' if title else ''
    return f'<path d="{d}" class="{cls}">{tip}</path>'


def ladder():
    """The steps from a lattice model to the Clay problem, marked by what is publicly claimed."""
    W, H = 400, 404
    steps = [
        ('1  Lattice in a finite box', 'Wilson 1974: well defined, computable', 'known'),
        ('2  Continuum limit, spacing → 0', 'short distances; asymptotic freedom', 'claimed'),
        ('3  Infinite volume, box → all space', 'long distances; no method was known', 'claimed'),
        ('4  Axioms of a quantum field theory', 'reflection positivity → Minkowski QFT', 'unclear'),
        ('5  Mass gap Δ > 0', 'every excitation costs energy', 'not'),
    ]
    style = {
        'known': ('fig-box', 'established before 2026'),
        'claimed': ('fig-box-claimed', 'claimed by OpenAI, per the review committee'),
        'unclear': ('fig-box', 'not stated in public documents'),
        'not': ('fig-box-open', 'not claimed: still open'),
    }
    out = []
    top, h, gap = 12, 58, 14
    for i, (title, sub, kind) in enumerate(steps):
        y = top + i * (h + gap)
        cls, tip = style[kind]
        out.append(f'<rect x="20" y="{y}" width="248" height="{h}" rx="6" class="{cls}"><title>{escape(tip)}</title></rect>')
        out.append(text(32, y + 24, title, 'fig-label'))
        out.append(text(32, y + 44, sub, 'fig-muted'))
        if i < len(steps) - 1:
            out.append(f'<path d="M144,{y + h + 2} V{y + h + gap - 2}" class="fig-axis"/>')
    # Brackets on the right.
    def bracket(a, b, label1, label2, cls):
        ya, yb = top + a * (h + gap) + 4, top + b * (h + gap) + h - 4
        out.append(f'<path d="M280,{ya} H290 V{yb} H280" class="{cls}"/>')
        mid = (ya + yb) / 2
        out.append(text(298, mid - 3, label1, 'fig-label'))
        out.append(text(298, mid + 14, label2, 'fig-muted'))
    bracket(1, 2, 'claimed', 'not yet public', 'fig-line-1')
    bracket(3, 3, 'not stated', 'publicly', 'fig-axis')
    bracket(4, 4, 'open', 'not claimed', 'fig-line-2')
    out.append(text(20, H - 8, 'The Clay problem asks for steps 2–5 on ℝ⁴, for every gauge group', 'fig-muted'))
    return svg(W, H, ''.join(out))


def running():
    """One-loop strong coupling against energy scale: weak at short distances."""
    W, H = 400, 280
    x0, x1, y0, y1 = 52, 380, 226, 22
    lo, hi = math.log10(1.2), math.log10(1000)
    amax = 0.5
    nf, lam = 5, 0.09                       # illustrative one-loop parameters (GeV)
    b0 = (33 - 2 * nf) / (12 * math.pi)
    alpha = lambda q: 1 / (b0 * math.log(q * q / (lam * lam)))
    X = lambda e: x0 + (e - lo) / (hi - lo) * (x1 - x0)
    Y = lambda a: y0 - a / amax * (y0 - y1)
    out = []
    for a in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(a):.1f}" y2="{Y(a):.1f}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(a) + 4, f'{a:g}', 'fig-muted', 'end'))
    for q in (2, 10, 100, 1000):
        out.append(text(X(math.log10(q)), y0 + 18, f'{q:g} GeV', 'fig-muted', 'end' if q == 1000 else 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    out.append(text((x0 + x1) / 2, H - 14, 'energy scale (log scale): higher energy = shorter distance', 'fig-muted', 'middle'))
    out.append(text(14, (y0 + y1) / 2, 'strength of the strong force', 'fig-muted', 'middle', f' transform="rotate(-90 14 {(y0 + y1) / 2:.1f})"'))
    es = [lo + i * (hi - lo) / 200 for i in range(201)]
    out.append(path([(X(e), Y(alpha(10 ** e))) for e in es], 'fig-line-1', 'One-loop running coupling, five quark flavours, illustrative'))
    mz = 91.19
    a_mz = alpha(mz)
    out.append(f'<circle cx="{X(math.log10(mz)):.1f}" cy="{Y(a_mz):.1f}" r="4.5" class="fig-fill-1"><title>About 0.118 at the Z boson mass, 91 GeV</title></circle>')
    out.append(text(X(math.log10(mz)) - 6, Y(a_mz) + 24, f'≈ {a_mz:.3f} at 91 GeV', 'fig-label', 'end'))
    out.append(text(X(lo) + 10, Y(0.46), 'strong at long distances:', 'fig-label'))
    out.append(text(X(lo) + 10, Y(0.46) + 16, 'quarks bound into protons', 'fig-muted'))
    out.append(text(X(hi) - 4, Y(0.29), 'weak at short distances:', 'fig-label', 'end'))
    out.append(text(X(hi) - 4, Y(0.29) + 16, 'asymptotic freedom', 'fig-muted', 'end'))
    return svg(W, H, ''.join(out)), a_mz


def blocking():
    """Block-spin renormalization: average 2×2 blocks, three times."""
    W, H = 400, 176
    out = []
    panels = [(8, 20), (4, 40), (2, 80)]
    size = 100
    for p, (n, cell) in enumerate(panels):
        x = 20 + p * 136
        y = 30
        out.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" class="fig-box"/>')
        step = size / n
        for i in range(1, n):
            out.append(f'<line x1="{x + i * step:.1f}" x2="{x + i * step:.1f}" y1="{y}" y2="{y + size}" class="fig-grid"/>')
            out.append(f'<line x1="{x}" x2="{x + size}" y1="{y + i * step:.1f}" y2="{y + i * step:.1f}" class="fig-grid"/>')
        for i in range(n + 1):
            for j in range(n + 1):
                r = 2.2 if n == 8 else 3.2 if n == 4 else 4.5
                out.append(f'<circle cx="{x + i * step:.1f}" cy="{y + j * step:.1f}" r="{r}" class="fig-node"/>')
        if n > 2:
            out.append(f'<rect x="{x}" y="{y}" width="{2 * step:.1f}" height="{2 * step:.1f}" class="fig-measure"><title>One block: its average becomes a single variable on the next lattice</title></rect>')
        out.append(text(x + size / 2, y + size + 20, f'{n} × {n} cells', 'fig-muted', 'middle'))
        if p < 2:
            out.append(text(x + size + 18, y + size / 2 + 5, '→', 'fig-label', 'middle'))
    out.append(text(20, 16, 'average 2 × 2 blocks, then repeat', 'fig-label'))
    return svg(W, H + 4, ''.join(out))


if __name__ == '__main__':
    (HERE / 'ladder.svg').write_text(ladder())
    r, a_mz = running()
    (HERE / 'running.svg').write_text(r)
    (HERE / 'blocking.svg').write_text(blocking())
    print(f'alpha_s(M_Z) one-loop illustrative: {a_mz:.4f}')
