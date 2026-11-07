"""Draw the figures for the "Beyond the qubit count" explainer. Run: python3 draw.py

Marks use the .fig-* classes in news/editorial.css so the inlined SVG follows the site theme.
"""
import math
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUP = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')


def svg(w, h, body):
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{body}</svg>\n'


def text(x, y, s, cls='fig-text', anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def path(points, cls, title=None):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points)
    tip = f'<title>{escape(title)}</title>' if title else ''
    return f'<path d="{d}" class="{cls}">{tip}</path>'


def compounding():
    """Probability that every operation succeeds, (1 - p)^N, against the number of operations N."""
    W, H = 400, 290
    x0, x1, y0, y1 = 52, 384, 236, 20
    lo, hi = 1, 10                                   # log10 N from 10 to 10^10
    X = lambda e: x0 + (e - lo) / (hi - lo) * (x1 - x0)
    Y = lambda v: y0 - v * (y0 - y1)
    out = []
    for v in (0, .25, .5, .75, 1):
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(v) + 4, f'{v:g}', 'fig-muted', 'end'))
    for e in range(1, 11, 3):
        out.append(text(X(e), y0 + 18, '10' + str(e).translate(SUP), 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    out.append(text((x0 + x1) / 2, H - 8, 'number of operations N (logarithmic scale)', 'fig-muted', 'middle'))
    out.append(text(14, (y0 + y1) / 2, 'chance no error occurs', 'fig-muted', 'middle', f' transform="rotate(-90 14 {(y0 + y1) / 2:.1f})"'))
    es = [lo + i * (hi - lo) / 300 for i in range(301)]
    # each label sits where its curve crosses a chosen height, staggered so labels do not collide
    series = [(1e-2, 'fig-line-2', '1 in 100', .2), (1e-3, 'fig-line-2', '1 in 1,000', .5),
              (1e-4, 'fig-ref', '1 in 10,000', .8), (1e-6, 'fig-line-1', '1 in a million', .2),
              (1e-9, 'fig-line-1', '1 in a billion', .5)]
    for p, cls, label, v in series:
        f = lambda e: math.exp(10 ** e * math.log1p(-p))
        out.append(path([(X(e), Y(f(e))) for e in es], cls, f'error {label} per operation'))
        at = math.log10(-math.log(v) / p)
        right = p > 1e-8  # the last curve sits at the right edge, so label it on its left
        out.append(text(X(at) + (7 if right else -7), Y(v) + 4, label, 'fig-label', 'start' if right else 'end'))
    return svg(W, H, ''.join(out))


def suppression():
    """Relative logical error against code distance for two suppression factors (editorial extrapolation)."""
    W, H = 400, 290
    x0, x1, y0, y1 = 58, 384, 236, 20
    dlo, dhi, elo = 3, 59, -10                       # distances, log10 relative error range [elo, 0]
    X = lambda d: x0 + (d - dlo) / (dhi - dlo) * (x1 - x0)
    Y = lambda e: y1 + (0 - e) / (0 - elo) * (y0 - y1)
    out = []
    for e in (0, -3, -6, -9):
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(e):.1f}" y2="{Y(e):.1f}" class="fig-grid"/>')
        out.append(text(x0 - 8, Y(e) + 4, '1' if e == 0 else '10' + str(e).translate(SUP), 'fig-muted', 'end'))
    for d in (3, 15, 27, 39, 51):
        out.append(text(X(d), y0 + 18, str(d), 'fig-muted', 'middle'))
    out.append(f'<path d="M{x0},{y1} V{y0} H{x1}" class="fig-axis"/>')
    out.append(text((x0 + x1) / 2, H - 8, 'code distance d', 'fig-muted', 'middle'))
    out.append(text(14, (y0 + y1) / 2, 'logical error, relative to d = 3', 'fig-muted', 'middle', f' transform="rotate(-90 14 {(y0 + y1) / 2:.1f})"'))
    out.append(path([(x0, Y(-9)), (x1, Y(-9))], 'fig-ref', 'a billionfold reduction'))
    for lam, cls, label in ((2.14, 'fig-line-1', 'Λ ≈ 2.1 per step'), (12, 'fig-line-2', 'Λ ≈ 12 per step')):
        e = lambda d: -(d - 3) / 2 * math.log10(lam)
        dmax = min(dhi, 3 + 2 * 10 / math.log10(lam))
        measured = [(X(d), Y(e(d))) for d in (3, 5, 7)]
        out.append(path(measured, cls, f'measured range, suppression factor {lam}'))
        out.append(path([(X(d), Y(e(d))) for d in [7 + k * 0.5 for k in range(int((dmax - 7) * 2) + 1)]], 'fig-ref'))
        for x, y in measured:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" class="{cls.replace("line", "fill")}"/>')
        need = 3 + 2 * math.ceil(9 / math.log10(lam))
        out.append(f'<circle cx="{X(need):.1f}" cy="{Y(e(need)):.1f}" r="4.5" class="fig-hollow"><title>about d = {need} for a billionfold reduction</title></circle>')
        out.append(text(X(need) + (10 if lam > 3 else -10), Y(-9) + (24 if lam > 3 else -12), f'{label}: d ≈ {need}', 'fig-label', 'start' if lam > 3 else 'end'))
    return svg(W, H, ''.join(out))


if __name__ == '__main__':
    (HERE / 'compounding.svg').write_text(compounding())
    (HERE / 'suppression.svg').write_text(suppression())
    for lam in (2.14, 12):
        print(lam, 'distance for 1e-9 relative:', 3 + 2 * math.ceil(9 / math.log10(lam)))
    for p in (1e-2, 1e-3, 1e-4, 1e-6):
        print(p, 'chance all of 10^4 ops succeed:', math.exp(1e4 * math.log1p(-p)))
