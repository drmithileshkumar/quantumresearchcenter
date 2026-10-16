#!/usr/bin/env python3
"""Draw Chapter 3's transition diagrams: one bit, one step, applied twice.

Each figure pairs a state diagram (configurations as circles, arrows labelled with
their weights) with its time-expanded diagram from 0 over two steps, so every path is visible.
"""
from pathlib import Path
from html import escape
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svgmath import plain, svg_text
ROOT = Path(__file__).resolve().parents[1] / 'assets/figures'
INK, EDGE, MUTED = '#30343b', '#246593', '#a7bccd'

class Figure:
    def __init__(self, title, description, width=820, height=330):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
                      f'<title id="title">{escape(plain(title))}</title><desc id="desc">{escape(plain(description))}</desc>'
                      f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                      f'<path d="M0 0L10 5L0 10Z" fill="{EDGE}"/></marker></defs>'
                      f'<style>text{{font:16px Georgia,serif;fill:{INK}}}.heading{{font:600 14px system-ui,sans-serif;fill:{EDGE}}}'
                      f'.small{{font:13px system-ui,sans-serif;fill:#4b5864}}.weight{{font:15px Georgia,serif;fill:{EDGE}}}'
                      f'.node{{fill:#fff;stroke:{EDGE};stroke-width:1.6}}.unused{{fill:#fff;stroke:{MUTED};stroke-width:1.2;stroke-dasharray:4 3}}'
                      f'.edge{{fill:none;stroke:{EDGE};stroke-width:1.6;marker-end:url(#arrow)}}.rule{{stroke:#d3dee7;stroke-width:1}}</style>']
    def text(self, x, y, value, cls='', anchor='middle'):
        self.parts.append(svg_text(x, y, value, f' text-anchor="{anchor}" class="{cls}"'))
    def node(self, x, y, label, r=22, used=True):
        self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r}" class="{"node" if used else "unused"}"/>')
        self.text(x, y + 6, label, '' if used else 'small')
    def path(self, d):
        self.parts.append(f'<path d="{d}" class="edge"/>')
    def save(self, name):
        ROOT.mkdir(parents=True, exist_ok=True)
        (ROOT / (name + '.svg')).write_text(''.join(self.parts) + '</svg>\n')

def transition_figure(name, title, description, weights, totals, note):
    """weights maps (from, to) to an arrow label; a missing pair means no arrow."""
    f = Figure(title, description)
    # State diagram: nodes 0 and 1 with arrows between and self-loops outside.
    mid = 180
    f.text(mid, 34, 'State diagram', 'heading')
    a, b, y, r = (mid - 70, 165), (mid + 70, 165), 165, 24
    f.node(a[0], y, r'\(0\)', r); f.node(b[0], y, r'\(1\)', r)
    if (0, 1) in weights:
        f.path(f'M{a[0]+17} {y-17} Q{mid} {y-70} {b[0]-17} {y-17}'); f.text(mid, y - 52, weights[(0, 1)], 'weight')
    if (1, 0) in weights:
        f.path(f'M{b[0]-17} {y+17} Q{mid} {y+70} {a[0]+17} {y+17}'); f.text(mid, y + 66, weights[(1, 0)], 'weight')
    if (0, 0) in weights:
        f.path(f'M{a[0]-14} {y-19} C{a[0]-75} {y-60} {a[0]-75} {y+60} {a[0]-19} {y+14}'); f.text(a[0] - 68, y + 5, weights[(0, 0)], 'weight', 'end')
    if (1, 1) in weights:
        f.path(f'M{b[0]+14} {y-19} C{b[0]+75} {y-60} {b[0]+75} {y+60} {b[0]+19} {y+14}'); f.text(b[0] + 68, y + 5, weights[(1, 1)], 'weight', 'start')
    f.parts.append('<path d="M376 30V300" class="rule"/>')
    # Time-expanded diagram: one copy of the configurations per time, starting from 0.
    f.text(552, 34, 'Time-expanded diagram from \\(0\\)', 'heading')
    xs, rows = (422, 537, 652), {0: 120, 1: 230}
    for x, label in zip(xs, (r'\(t=0\)', r'\(t=1\)', r'\(t=2\)')):
        f.text(x, 76, label, 'small')
    reached = [{0}]
    for _ in range(2):
        reached.append({j for i in reached[-1] for (s, j) in weights if s == i})
    for step in range(2):
        x1, x2 = xs[step] + 16, xs[step + 1] - 16
        for (i, j), w in sorted(weights.items()):
            if i not in reached[step]:
                continue
            y1, y2 = rows[i], rows[j]
            f.path(f'M{x1} {y1}L{x2} {y2}')
            if i == j:
                f.text((x1 + x2) / 2, y1 - 9 if i == 0 else y1 + 24, w, 'weight')
            else:
                tx, ty = x1 + 0.22 * (x2 - x1), y1 + 0.22 * (y2 - y1)
                f.text(tx + 8, ty + (4 if i == 0 else 10), w, 'weight', 'start')
    for col, x in enumerate(xs):
        for state, y in rows.items():
            f.node(x, y, f'\\({state}\\)', 16, state in reached[col])
    for state, y in rows.items():
        f.text(686, y + 5, totals[state], '', 'start')
    f.text(552, 300, note, 'small')
    f.save(name)

def hadamard_weight_figure():
    """Show the unnormalized signed step before fixing its common weight c."""
    c = r'\(c\)'
    transition_figure('transitions-hadamard-c', 'Signed Hadamard transition with weight c',
        'Three arrows carry weight c and the arrow from 1 to 1 carries minus c. '
        'Over two steps from 0, two paths to 0 contribute c squared each, giving 2c squared; '
        'the paths to 1 contribute c squared and minus c squared, giving zero. '
        'Returning the original weight one therefore requires 2c squared equals one.',
        {(0, 0): c, (0, 1): c, (1, 0): c, (1, 1): r'\(-c\)'},
        {0: r'\(c^2+c^2=2c^2\)', 1: r'\(c^2-c^2=0\)'},
        r'Returning to weight one requires \(2c^2=1\).')

def sqrt_not_weight_figure():
    """Show the path sums of a symmetric step whose square is NOT."""
    transition_figure('transitions-sqrt-not-ab', 'Square root of NOT with weights a and b',
        'Each self-loop carries stay-weight a and each arrow between configurations carries switch-weight b. '
        'Over two steps from 0, staying twice contributes a squared and switching twice contributes b squared at 0. '
        'Staying then switching contributes ab and switching then staying contributes ba at 1. '
        'For the combined step to be NOT, a squared plus b squared must be zero and 2ab must be one.',
        {(0, 0): r'\(a\)', (0, 1): r'\(b\)', (1, 0): r'\(b\)', (1, 1): r'\(a\)'},
        {0: r'\(a^2+b^2\)', 1: r'\(ab+ba=2ab\)'},
        r'NOT requires \(a^2+b^2=0\) and \(2ab=1\).')

def main():
    h = r'\(1/\sqrt2\)'
    transition_figure('transitions-deterministic', 'Deterministic transitions: NOT applied twice',
        'The state diagram of NOT has one arrow from 0 to 1 and one from 1 to 0, each with weight 1. In the time-expanded diagram over two steps from 0, there is a single path, 0 to 1 to 0.',
        {(0, 1): r'\(1\)', (1, 0): r'\(1\)'}, {0: r'weight \(1\)', 1: r'weight \(0\)'},
        'One arrow leaves each configuration, so the run has exactly one path.')
    transition_figure('transitions-nondeterministic', 'Nondeterministic transitions: keep or flip, applied twice',
        'The keep-or-flip rule allows all four arrows. In the time-expanded diagram over two steps from 0, four paths are possible: two end at 0 and two end at 1.',
        {(0, 0): 'yes', (0, 1): 'yes', (1, 0): 'yes', (1, 1): 'yes'}, {0: 'reachable', 1: 'reachable'},
        'Every arrow is allowed, so both end configurations are reachable.')
    transition_figure('transitions-probabilistic', 'Probabilistic transitions: a fair coin step, applied twice',
        'Every arrow of the fair coin step has probability one half. In the time-expanded diagram over two steps from 0, each of the four paths has probability one quarter, and each end configuration has probability one half.',
        {(0, 0): r'\(1/2\)', (0, 1): r'\(1/2\)', (1, 0): r'\(1/2\)', (1, 1): r'\(1/2\)'},
        {0: r'\(\tfrac14+\tfrac14=\tfrac12\)', 1: r'\(\tfrac14+\tfrac14=\tfrac12\)'},
        'Each path has probability \\(1/4\\); two paths reach each end.')
    transition_figure('transitions-quantum', 'Quantum transitions: the Hadamard step, applied twice',
        'The Hadamard step has amplitude one over root two on every arrow except the arrow from 1 to 1, which has minus one over root two. In the time-expanded diagram over two steps from 0, the two paths to 0 contribute one half each and add to 1; the two paths to 1 contribute one half and minus one half and cancel.',
        {(0, 0): h, (0, 1): h, (1, 0): h, (1, 1): r'\(-1/\sqrt2\)'},
        {0: r'\(\tfrac12+\tfrac12=1\)', 1: r'\(\tfrac12-\tfrac12=0\)'},
        'The amplitudes of the two paths to \\(1\\) cancel.')
    hadamard_weight_figure()
    sqrt_not_weight_figure()
    print('Drew 6 Chapter 3 transition diagrams.')

if __name__ == '__main__':
    main()
