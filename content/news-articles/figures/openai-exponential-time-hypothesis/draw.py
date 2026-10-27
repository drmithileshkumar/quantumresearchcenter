"""Draw the figures for the ETH article. Run: python3 draw.py (writes the .svg files beside it).

Marks use classes from news/editorial.css (.fig-*) so the inlined SVG follows the site theme.
"""
import math
from pathlib import Path
from html import escape

HERE = Path(__file__).resolve().parent
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')


def svg(width, height, body):
    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{body}</svg>\n'


def text(x, y, s, cls='fig-text', anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def path(points, cls, title=None):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)
    tip = f'<title>{escape(title)}</title>' if title else ''
    return f'<path d="{d}" class="{cls}">{tip}</path>'


def growth():
    """Per-variable exponent log2(steps)/n against the number of variables (log scale)."""
    W, H = 400, 300
    x0, x1, y0, y1 = 52, 372, 252, 22          # plot box (y0 bottom)
    lo, hi, ymax = 3, 100, 2.2                  # log10 n range, exponent range
    X = lambda e: x0 + (e - lo) / (hi - lo) * (x1 - x0)
    Y = lambda v: y0 - v / ymax * (y0 - y1)
    manuscript = lambda e: math.log(e * math.log(10)) / math.sqrt(e * math.log(10))
    lean = lambda e: math.log(e * math.log(10)) ** 2 / math.sqrt(e * math.log(10))
    best = math.log2(1.307)
    out = []
    for v in (0, 0.5, 1, 1.5, 2):
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(v) + 4, f'{v:g}', 'fig-muted', 'end'))
    for e in (20, 40, 60, 80, 100):
        out.append(text(X(e), y0 + 18, '10' + str(e).translate(SUP), 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    out.append(text((x0 + x1) / 2, H - 6, 'number of variables n (logarithmic scale)', 'fig-muted', 'middle'))
    out.append(text(14, (y0 + y1) / 2, 'exponent per variable', 'fig-muted', 'middle', f' transform="rotate(-90 14 {(y0 + y1) / 2:.1f})"'))
    # Exponential references: flat lines.
    out.append(path([(X(lo), Y(1)), (X(hi), Y(1))], 'fig-ref', 'Exhaustive search 2^n: exponent per variable 1'))
    out.append(text(X(lo) + 6, Y(1) - 7, 'exhaustive search, 2ⁿ', 'fig-text'))
    out.append(path([(X(lo), Y(best)), (X(hi), Y(best))], 'fig-ref', f'Best known 1.307^n: exponent per variable {best:.3f}'))
    out.append(text(X(lo) + 6, Y(best) + 16, 'best known algorithm, 1.307ⁿ', 'fig-text'))
    # Subexponential bounds (hidden constant set to 1).
    es = [lo + i * (hi - lo) / 200 for i in range(201)]
    out.append(path([(X(e), Y(lean(e))) for e in es], 'fig-line-2', 'Lean-checked bound, hidden constant 1'))
    out.append(text(X(hi), Y(lean(hi)) - 16, 'Lean-checked bound', 'fig-label', 'end'))
    out.append(path([(X(e), Y(manuscript(e))) for e in es], 'fig-line-1', 'Manuscript bound, hidden constant 1'))
    out.append(text(X(30), Y(manuscript(30)) - 18, 'manuscript bound', 'fig-label', 'middle'))
    cross = next(e for e in es if manuscript(e) < best)
    out.append(f'<circle cx="{X(cross):.1f}" cy="{Y(best):.1f}" r="4.5" class="fig-fill-1"><title>Manuscript bound drops below the best known exponential near n = 10^{cross:.0f}</title></circle>')
    out.append(text(X(cross), Y(best) + 34, 'crosses near 10' + f'{cross:.0f}'.translate(SUP), 'fig-muted', 'middle'))
    return svg(W, H, ''.join(out)), cross


def split():
    """Groups tied by clauses, then separated once shared summaries are fixed."""
    W, H = 400, 340
    out = []
    xs = (18, 146, 274)
    def groups(top, cross):
        nodes = {}
        for g, x in enumerate(xs):
            out.append(f'<rect x="{x}" y="{top}" width="108" height="78" rx="6" class="fig-box"/>')
            out.append(text(x + 54, top + 94, f'group {g + 1}', 'fig-muted', 'middle'))
            for i, (dx, dy) in enumerate(((26, 22), (82, 22), (26, 56), (82, 56))):
                nodes[g, i] = (x + dx, top + dy)
        inner = [(0, 1), (0, 2), (1, 3), (2, 3)]
        for g in range(3):
            for a, b in inner[g % 2::2] + [inner[2]]:
                (ax, ay), (bx, by) = nodes[g, a], nodes[g, b]
                out.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" class="fig-link"/>')
        if cross:
            for (ga, a), (gb, b) in (((0, 1), (1, 0)), ((0, 3), (1, 2)), ((1, 1), (2, 2)), ((1, 3), (2, 0)), ((0, 3), (2, 2))):
                (ax, ay), (bx, by) = nodes[ga, a], nodes[gb, b]
                mid = (ax + bx) / 2, min(ay, by) - (28 if (ga, gb) == (0, 2) else 10)
                out.append(f'<path d="M{ax},{ay} Q{mid[0]:.1f},{mid[1]:.1f} {bx},{by}" class="fig-cross"><title>A clause linking two groups</title></path>')
        for (x, y) in nodes.values():
            out.append(f'<circle cx="{x}" cy="{y}" r="6" class="fig-node"/>')
    out.append(text(18, 20, '1  Clauses (orange) tie the groups together', 'fig-label'))
    groups(42, True)
    out.append(text(18, 182, '2  Fix a few shared summaries: groups separate', 'fig-label'))
    groups(204, False)
    bar_y = 326
    out.append(f'<line x1="18" x2="382" y1="{bar_y - 8}" y2="{bar_y - 8}" class="fig-measure"/>')
    for x in xs:
        out.append(f'<line x1="{x + 54}" x2="{x + 54}" y1="{306}" y2="{bar_y - 8}" class="fig-measure"><title>Group summary, held fixed</title></line>')
    out.append(text(200, bar_y + 8, 'shared summaries such as x₃ − x₇ + x₁₂, each held at a fixed value', 'fig-muted', 'middle'))
    return svg(W, H + 12, ''.join(out))


def interpolation():
    """H(T): unknown at T = 0, values and slopes computed at T = 1..4."""
    W, H = 400, 260
    x0, x1, y0, y1 = 30, 386, 214, 40
    tmin, tmax, vmin, vmax = -0.35, 4.25, 2.2, 8.2
    X = lambda t: x0 + (t - tmin) / (tmax - tmin) * (x1 - x0)
    Y = lambda v: y0 - (v - vmin) / (vmax - vmin) * (y0 - y1)
    h = lambda t: 3 + 1.2 * t - 1.1 * t * t + 0.25 * t ** 3
    dh = lambda t: 1.2 - 2.2 * t + 0.75 * t * t
    out = [f'<path d="M{x0},{y0} H{x1}" class="fig-axis"/>']
    for t in range(5):
        out.append(text(X(t), y0 + 18, f'T = {t}', 'fig-muted', 'middle'))
    ts = [tmin + i * (tmax - tmin) / 200 for i in range(201)]
    out.append(path([(X(t), Y(h(t))) for t in ts], 'fig-ref', 'The polynomial H(T), reconstructed'))
    for t in range(1, 5):
        d = 0.32
        out.append(path([(X(t - d), Y(h(t) - d * dh(t))), (X(t + d), Y(h(t) + d * dh(t)))], 'fig-line-1', f'At T = {t}: value and slope are computed quickly'))
        out.append(f'<circle cx="{X(t):.1f}" cy="{Y(h(t)):.1f}" r="5" class="fig-fill-1"><title>H({t}) and its derivatives: computed group by group</title></circle>')
    out.append(f'<circle cx="{X(0):.1f}" cy="{Y(h(0)):.1f}" r="6.5" class="fig-hollow"><title>H(0) is the number of solutions: recovered by interpolation</title></circle>')
    out.append(text(X(0) + 2, Y(h(0)) - 54, 'H(0) = number of solutions', 'fig-label'))
    out.append(text(X(0) + 2, Y(h(0)) - 37, 'too costly to compute directly,', 'fig-muted'))
    out.append(text(X(0) + 2, Y(h(0)) - 22, 'recovered from the other points', 'fig-muted'))
    out.append(text(X(1.0), Y(7.7), 'easy points T = 1, …, 4:', 'fig-label'))
    out.append(text(X(1.0), Y(7.7) + 16, 'value and slopes computed cheaply', 'fig-muted'))
    return svg(W, H, ''.join(out))


def coins():
    """Heads in Q = 100 fair tosses; the polynomial must be right only on a central band."""
    W, H = 400, 250
    Q, lo, hi, band = 100, 26, 74, (41, 60)
    x0, x1, y0, y1 = 20, 384, 200, 34
    pmf = [math.comb(Q, k) / 2 ** Q for k in range(Q + 1)]
    top = max(pmf)
    bw = (x1 - x0) / (hi - lo + 1)
    outside = sum(p for k, p in enumerate(pmf) if not band[0] <= k <= band[1])
    out = [f'<path d="M{x0},{y0} H{x1}" class="fig-axis"/>']
    for k in range(lo, hi + 1):
        hgt = pmf[k] / top * (y0 - y1)
        cls = 'fig-fill-1' if band[0] <= k <= band[1] else 'fig-fill-muted'
        x = x0 + (k - lo) * bw
        out.append(f'<rect x="{x + 1:.1f}" y="{y0 - hgt:.1f}" width="{bw - 2:.1f}" height="{max(hgt, 0.5):.1f}" rx="1" class="{cls}"><title>{k} heads: probability {pmf[k]:.4f}</title></rect>')
    for k in (30, 40, 50, 60, 70):
        out.append(text(x0 + (k - lo + 0.5) * bw, y0 + 18, str(k), 'fig-muted', 'middle'))
    out.append(text((x0 + x1) / 2, y0 + 38, 'number of heads in 100 coin tosses', 'fig-muted', 'middle'))
    out.append(text(x0 + (50 - lo + 0.5) * bw, 18, f'polynomial exact on {band[1] - band[0] + 1} values ({band[0]}–{band[1]})', 'fig-label', 'middle'))
    out.append(text(x0 + 2, 70, f'rare tails: {100 * outside:.1f}%,', 'fig-muted'))
    out.append(text(x0 + 2, 86, 'handled by', 'fig-muted'))
    out.append(text(x0 + 2, 102, 'measurements', 'fig-muted'))
    return svg(W, H, ''.join(out)), outside


if __name__ == '__main__':
    g, cross = growth()
    (HERE / 'growth.svg').write_text(g)
    (HERE / 'split.svg').write_text(split())
    (HERE / 'interpolation.svg').write_text(interpolation())
    c, outside = coins()
    (HERE / 'coins.svg').write_text(c)
    print(f'crossing near 10^{cross:.0f}; tail mass outside band {outside:.4f}')
