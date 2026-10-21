#!/usr/bin/env python3
"""Draw transition diagrams for path composition and matrix representation.

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

def transition_matrix_figure():
    """Map each directed transition to its destination row and source column."""
    f = Figure('Transition amplitudes and matrix entries',
        'Two input nodes and two output nodes show one step. From input 0, the arrows to outputs 0 and 1 have weights a and b; these form matrix column 0. From input 1, the arrows to outputs 0 and 1 have weights c and d; these form column 1. Output 0 selects row 0, containing a and c. Output 1 selects row 1, containing b and d. Thus U equals the matrix with rows a,c and b,d, and U ji is the weight of i to j.',
        width=960, height=410)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    blue, orange = '#246593', '#a64d26'
    f.text(205, 30, 'One-step transition graph', 'heading')
    f.text(710, 30, 'Matrix of the same transition', 'heading')
    f.text(80, 72, r'Input \(i\)', 'small')
    f.text(330, 72, r'Output \(j\)', 'small')
    # Repeated configuration nodes separate the source and destination of a step.
    edges = [
        ('M104 120H306', blue, 205, 108, r'\(a\)'),
        ('M99 135L311 265', blue, 160, 201, r'\(b\)'),
        ('M99 265L311 135', orange, 250, 201, r'\(c\)'),
        ('M104 280H306', orange, 205, 309, r'\(d\)')]
    for path, color, x, y, label in edges:
        f.parts.append(f'<path class="edge" d="{path}" style="stroke:{color}"/>')
        f.parts.append(svg_text(x, y, label, f' text-anchor="middle" class="weight" style="fill:{color}"'))
    for x in (80, 330):
        f.node(x, 120, r'\(0\)', r=24)
        f.node(x, 280, r'\(1\)', r=24)
    f.parts.append('<path class="rule" d="M430 55V330"/>')
    # Column colors match the arrows leaving the corresponding source node.
    f.parts.append('<rect x="596" y="120" width="100" height="160" rx="4" fill="#eaf1f7"/><rect x="726" y="120" width="100" height="160" rx="4" fill="#fbefe8"/>')
    f.text(646, 85, r'from \(0\)', 'small')
    f.text(776, 85, r'from \(1\)', 'small')
    f.text(528, 160, r'to \(0\)', 'small')
    f.text(528, 245, r'to \(1\)', 'small')
    f.text(552, 205, r'\(U=\)')
    f.parts.append('<path d="M590 125H580V275H590 M832 125H842V275H832" fill="none" stroke="#30343b" stroke-width="1.6"/>')
    for x, y, value, color in [(646,160,'a',blue),(646,245,'b',blue),(776,160,'c',orange),(776,245,'d',orange)]:
        f.parts.append(svg_text(x, y, r'\('+value+r'\)', f' text-anchor="middle" style="fill:{color};font-size:22px"'))
    f.text(710, 320, 'Rows: destinations. Columns: sources.', 'small')
    f.text(480, 382, r'\(U_{ji}=\bra jU\ket i,\qquad U=\begin{pmatrix}a&c\\b&d\end{pmatrix}\)')
    f.save('transitions-to-matrix')

def adjoint_transition_figure():
    """Show the adjoint as reversed arrows with conjugated amplitudes."""
    f = Figure('Adjoint: reverse transitions and conjugate amplitudes',
        'The arrows of the preceding U graph are reversed. The original transition i to j with amplitude U ji becomes a transition j to i with conjugate amplitude U ji star. The reversed arrows have weights a star from 0 to 0, b star from 1 to 0, c star from 0 to 1, and d star from 1 to 1. Thus U dagger has rows a star,b star and c star,d star. The original columns become conjugated rows. For a unitary U this is the inverse transition; the adjoint is defined for any matrix.',
        width=960, height=440)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    blue, orange = '#246593', '#a64d26'
    f.text(205, 30, 'Reversed transition graph', 'heading')
    f.text(710, 30, r'Matrix \(U^\dagger\)', 'heading')
    f.text(80, 72, r'Output \(i\)', 'small')
    f.text(330, 72, r'Input \(j\)', 'small')
    edges = [
        ('M306 120H104', blue, 205, 108, r'\(a^*\)'),
        ('M311 265L99 135', blue, 160, 201, r'\(b^*\)'),
        ('M311 135L99 265', orange, 250, 201, r'\(c^*\)'),
        ('M306 280H104', orange, 205, 309, r'\(d^*\)')]
    for path, color, x, y, label in edges:
        f.parts.append(f'<path class="edge" d="{path}" style="stroke:{color}"/>')
        f.parts.append(svg_text(x, y, label, f' text-anchor="middle" class="weight" style="fill:{color}"'))
    for x in (80, 330):
        f.node(x, 120, r'\(0\)', r=24)
        f.node(x, 280, r'\(1\)', r=24)
    f.parts.append('<path class="rule" d="M430 55V330"/>')
    # Original columns become conjugated rows, retaining their colors.
    f.parts.append('<rect x="596" y="125" width="230" height="65" rx="4" fill="#eaf1f7"/><rect x="596" y="210" width="230" height="65" rx="4" fill="#fbefe8"/>')
    f.text(646, 85, r'from \(0\)', 'small')
    f.text(776, 85, r'from \(1\)', 'small')
    f.text(520, 160, r'to \(0\)', 'small')
    f.text(520, 245, r'to \(1\)', 'small')
    f.text(548, 205, r'\(U^\dagger=\)')
    f.parts.append('<path d="M590 125H580V275H590 M832 125H842V275H832" fill="none" stroke="#30343b" stroke-width="1.6"/>')
    for x, y, value, color in [(646,160,'a^*',blue),(776,160,'b^*',blue),(646,245,'c^*',orange),(776,245,'d^*',orange)]:
        f.parts.append(svg_text(x, y, r'\('+value+r'\)', f' text-anchor="middle" style="fill:{color};font-size:22px"'))
    f.text(710, 320, 'Original columns become conjugated rows.', 'small')
    f.text(480, 370, r'\(U=\begin{pmatrix}a&c\\b&d\end{pmatrix}\quad\longmapsto\quad U^\dagger=\begin{pmatrix}a^*&b^*\\c^*&d^*\end{pmatrix}\)')
    f.text(480, 415, r'\((U^\dagger)_{ij}=U_{ji}^*=\bigl(\bra jU\ket i\bigr)^*\)')
    f.save('transitions-adjoint')

def unitarity_transition_figure():
    """Compose U with its adjoint and sum paths to every endpoint."""
    f = Figure('Composition of U and its adjoint',
        'A three-layer graph shows inputs k, intermediate configurations j, and outputs i. The first step U has matrix rows a,c and b,d. The second step U dagger reverses the original arrows and conjugates their weights. Each entry of U dagger U is the sum of the two path products to that output. Normalized columns give diagonal entries one; orthogonal columns give off-diagonal entries zero. Under these conditions the composite is the identity.',
        width=960, height=430)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    blue, orange = '#246593', '#a64d26'
    f.text(245, 30, 'One step, then its adjoint', 'heading')
    f.text(720, 30, 'Sum products along the two-step paths', 'heading')
    f.text(80, 72, r'Input \(k\)', 'small')
    f.text(245, 72, r'Intermediate \(j\)', 'small')
    f.text(410, 72, r'Output \(i\)', 'small')
    f.text(162, 100, r'\(U\)', 'heading')
    f.text(327, 100, r'\(U^\dagger\)', 'heading')
    for left, labels in [(80, ('a','b','c','d')), (245, ('a^*','c^*','b^*','d^*'))]:
        # U colors identify its source columns; U dagger colors identify the
        # corresponding conjugated rows, as in the preceding illustrations.
        colors = (blue,blue,orange,orange) if left==80 else (blue,orange,blue,orange)
        routes = [
            (f'M{left+24} 140H{left+141}', left+82, 129),
            (f'M{left+19} 154L{left+146} 286', left+57, 218),
            (f'M{left+19} 286L{left+146} 154', left+110, 205),
            (f'M{left+24} 300H{left+141}', left+82, 329)]
        for (path,x,y),label,color in zip(routes,labels,colors):
            f.parts.append(f'<path class="edge" d="{path}" style="stroke:{color}"/>')
            f.parts.append(svg_text(x,y,r'\('+label+r'\)',f' text-anchor="middle" class="weight" style="fill:{color}"'))
    for x in (80,245,410):
        f.node(x,140,r'\(0\)',r=24)
        f.node(x,300,r'\(1\)',r=24)
    f.parts.append('<path class="rule" d="M475 55V350"/>')
    equation=r'\(U^\dagger U=\begin{pmatrix}a^*a+b^*b&a^*c+b^*d\\c^*a+d^*b&c^*c+d^*d\end{pmatrix}\)'
    f.parts.append(svg_text(720,180,equation,' text-anchor="middle" data-max-width="425" style="font-size:18px"'))
    f.text(720,245,r'\(=\begin{pmatrix}1&0\\0&1\end{pmatrix}=I\)')
    f.text(720,305,'Unit output vectors give the diagonal ones.', 'small')
    f.text(720,330,'Orthogonal outputs give the off-diagonal zeros.', 'small')
    f.text(480,395,r'\((U^\dagger U)_{ik}=\sum_j U_{ji}^*U_{jk}=\begin{cases}1&i=k\\0&i\ne k\end{cases}\)')
    f.save('transitions-unitarity')

def inner_product_geometry_figure():
    """Show a transition amplitude as a component along a final direction."""
    f = Figure('Inner product: amplitude along the final direction',
        'A real state-vector plane shows the final unit vector phi equals ket zero and the initial unit vector psi equals square root three over two ket zero plus one half ket one. Their angle is pi over six. The component of psi along phi has coefficient bra phi ket psi equals square root three over two, so the probability of the final-state outcome is three quarters. The dashed line selects the projection. These are state-vector directions, not directions in physical space.',
        width=760, height=430)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    f.text(380,30,'Amplitude as a component of the initial vector','heading')
    # Both vectors have length 300; their angle is pi/6.
    f.parts.append('<path d="M115 300V85" stroke="#a7bccd" stroke-width="1.2" fill="none"/>')
    f.text(95,85,r'\(\ket1\)','small')
    f.parts.append('<path class="edge" d="M115 300H415" style="stroke:#a64d26"/>')
    f.parts.append('<path class="edge" d="M115 300L374.808 150"/>')
    f.parts.append('<path d="M374.808 150V300" stroke="#a7bccd" stroke-width="1.4" stroke-dasharray="5 4" fill="none"/>')
    f.parts.append('<circle cx="374.808" cy="300" r="4" fill="#246593"/>')
    f.parts.append('<path d="M165 300A50 50 0 0 0 158.301 275" fill="none" stroke="#a64d26" stroke-width="1.4"/>')
    f.text(178,286,r'\(\theta\)')
    f.text(98,321,r'\(0\)','small')
    f.text(375,128,r'initial \(\ket\psi\)')
    f.text(495,306,r'final \(\ket\phi=\ket0\)')
    f.text(245,337,r'\(\braket\phi\psi=\sqrt3/2\)')
    f.text(575,125,r'\(\braket\phi\phi=\braket\psi\psi=1\)')
    f.text(575,177,r'\(\theta=\pi/6\)')
    f.text(575,230,r'\(|\braket\phi\psi|^2=3/4\)')
    f.text(380,395,r'For real unit vectors: \(\braket\phi\psi=\cos\theta\).')
    f.save('inner-product-geometry')

def component_split_figure():
    """Split a unit vector into its component along a direction and an orthogonal remainder."""
    import math
    f = Figure('Splitting a state along a direction',
        'In a real state-vector plane, the unit vector phi points at 15 degrees and the unit vector psi at 75 degrees, '
        'so the angle between them is 60 degrees. The component of psi along phi, the inner product of phi and psi times phi, '
        'has length one half and lies along phi. The remainder psi perp runs from the end of that component to the tip of psi, '
        'at a right angle to phi, with length root three over two. The squared lengths one quarter and three quarters add to one.',
        width=760, height=390)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    f.text(380, 30, 'Splitting a state along a direction', 'heading')
    O = (110, 340); R = 260; a_phi, a_psi = math.radians(15), math.radians(75)
    pt = lambda r, a: (O[0] + r * math.cos(a), O[1] - r * math.sin(a))
    up, un = (math.cos(a_phi), -math.sin(a_phi)), (-math.sin(a_phi), -math.cos(a_phi))   # along phi, perpendicular to it
    phi_tip, psi_tip = pt(R, a_phi), pt(R, a_psi)
    c = R * math.cos(a_psi - a_phi); foot = (O[0] + c * up[0], O[1] + c * up[1])
    fmt = lambda q: f'{q[0]:.1f} {q[1]:.1f}'
    far, back = pt(1.22 * R, a_phi), pt(-0.12 * R, a_phi)
    f.parts.append(f'<path d="M{fmt(back)}L{fmt(far)}" stroke="#d3dee7" stroke-width="1.2" fill="none"/>')       # the line of phi
    f.parts.append(f'<path class="edge" d="M{fmt(O)}L{fmt(phi_tip)}" style="stroke:#a64d26"/>')                     # |phi>
    f.parts.append(f'<path class="edge" d="M{fmt(O)}L{fmt(psi_tip)}"/>')                                            # |psi>
    # A thick line would scale the shared arrowhead with it, so the component gets a fixed-size head.
    f.parts.append('<defs><marker id="arrow-fixed" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="13" markerHeight="13" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#c2410c"/></marker></defs>')
    f.parts.append(f'<path d="M{fmt(O)}L{fmt(foot)}" fill="none" stroke="#c2410c" stroke-width="4" marker-end="url(#arrow-fixed)"/>')          # component
    f.parts.append(f'<path class="edge" d="M{fmt(foot)}L{fmt(psi_tip)}" style="stroke:#347449;stroke-width:2.2;stroke-dasharray:7 5"/>')  # remainder
    m = 14; corner = [(foot[0] + m * un[0], foot[1] + m * un[1]), (foot[0] + m * (un[0] - up[0]), foot[1] + m * (un[1] - up[1])), (foot[0] - m * up[0], foot[1] - m * up[1])]
    f.parts.append(f'<path d="M{fmt(corner[0])}L{fmt(corner[1])}L{fmt(corner[2])}" stroke="#347449" stroke-width="1.4" fill="none"/>')
    a0, a1 = pt(52, a_phi), pt(52, a_psi)
    f.parts.append(f'<path d="M{fmt(a0)}A52 52 0 0 0 {fmt(a1)}" stroke="#4b5864" stroke-width="1.3" fill="none"/>')
    f.parts.append(f'<circle cx="{O[0]}" cy="{O[1]}" r="3.5" fill="{INK}"/>')
    lab = lambda q, d, k: (q[0] + d * k[0], q[1] + d * k[1])
    f.text(*lab(phi_tip, 30, up), r'\(\ket\phi\)')
    f.text(*lab(psi_tip, -16, (0, 1)), r'\(\ket\psi\)')
    th = pt(72, (a_phi + a_psi) / 2); f.text(th[0], th[1] + 5, r'\(\theta\)')
    mid = ((O[0] + foot[0]) / 2, (O[1] + foot[1]) / 2); f.text(*lab(mid, -30, un), r'\(\braket\phi\psi\,\ket\phi\)')
    mr = ((foot[0] + psi_tip[0]) / 2, (foot[1] + psi_tip[1]) / 2); f.text(*lab(mr, 38, up), r'\(\ket{\psi_\perp}\)')
    f.text(565, 120, r'\(\ket\psi=\braket\phi\psi\,\ket\phi+\ket{\psi_\perp}\)')
    f.text(565, 172, r'\(\braket\phi{\psi_\perp}=0\)')
    f.text(565, 224, r'\(1=|\braket\phi\psi|^2+\|\psi_\perp\|^2\)')
    f.text(565, 276, r'Here \(\theta=60^\circ\): \(\braket\phi\psi=\tfrac12\)', 'small')
    f.text(565, 304, r'\(1=\tfrac14+\tfrac34\)', 'small')
    f.save('component-split')

def standard_basis_ket_figure():
    """Draw a real-amplitude ket and its standard-basis coordinates."""
    f = Figure('A ket as a vector in the standard basis',
        'The standard basis vectors ket zero and ket one are perpendicular unit vectors. A blue arrow represents ket psi equals three fifths ket zero plus four fifths ket one. Dashed lines mark its coordinates v zero equals three fifths horizontally and v one equals four fifths vertically. The same ket is the column vector with entries three fifths and four fifths. This real-amplitude drawing represents state space, not physical space.',
        width=760, height=430)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    f.text(380,30,'A ket and its standard-basis coordinates','heading')
    # Unit basis vectors have length 250. Psi has coordinates (3/5,4/5).
    f.parts.append('<path class="edge" d="M110 330H360" style="stroke:#a64d26"/>')
    f.parts.append('<path class="edge" d="M110 330V80" style="stroke:#347449"/>')
    f.parts.append('<path d="M110 130H260V330" stroke="#a7bccd" stroke-width="1.3" stroke-dasharray="5 4" fill="none"/>')
    f.parts.append('<path class="edge" d="M110 330L260 130"/>')
    f.text(110,60,r'\(\ket1\)')
    f.text(385,335,r'\(\ket0\)')
    f.text(280,117,r'\(\ket\psi\)')
    f.text(75,136,r'\(v_1=4/5\)')
    f.text(260,355,r'\(v_0=3/5\)')
    f.text(93,352,r'\(0\)','small')
    f.text(550,75,'Standard basis','heading')
    f.text(485,130,r'\(\ket0=\begin{pmatrix}1\\0\end{pmatrix}\)')
    f.text(650,130,r'\(\ket1=\begin{pmatrix}0\\1\end{pmatrix}\)')
    f.text(550,215,r'\(\ket\psi=\frac35\ket0+\frac45\ket1\)')
    f.text(550,280,r'\(\ket\psi=\begin{pmatrix}3/5\\4/5\end{pmatrix}\)')
    f.text(550,335,'A real-amplitude example.','small')
    f.text(380,400,r'\(\ket\psi=v_0\ket0+v_1\ket1\): the coefficients are coordinates.')
    f.save('ket-standard-basis')

def transition_matrix_geometry_figure():
    """Show a real unitary acting on a state and both basis directions."""
    f = Figure('Geometric action of a transition matrix',
        'Left: the initial ket psi has coordinates three fifths and four fifths in the standard basis. Right: U equals one fifth times the matrix with rows four,minus three and three,four. It rotates ket zero to coordinates four fifths,three fifths and ket one to minus three fifths,four fifths. The transformed components three fifths U ket zero and four fifths U ket one add to U ket psi equals ket one. The coordinate axes stay fixed. This is a real state-vector plane.',
        width=960, height=530)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    orange,green='#a64d26','#347449'
    f.text(240,30,'Initial vector','heading')
    f.text(720,30,'Transformed vector and basis directions','heading')
    # Left: unit basis vectors and psi=(3/5,4/5).
    for path,color in [('M135 340H345',orange),('M135 340V130',green),('M135 340L261 172',EDGE)]:
        f.parts.append(f'<path class="edge" d="{path}" style="stroke:{color}"/>')
    f.parts.append('<path d="M135 172H261V340" stroke="#a7bccd" stroke-width="1.3" stroke-dasharray="5 4" fill="none"/>')
    f.text(365,345,r'\(\ket0\)')
    f.text(135,110,r'\(\ket1\)')
    f.text(276,154,r'\(\ket\psi\)')
    f.text(104,181,r'\(4/5\)')
    f.text(261,365,r'\(3/5\)')
    # Right: the fixed coordinate axes and the rotated unit basis.
    f.parts.append('<path d="M535 340H915 M700 365V95" stroke="#d3dee7" stroke-width="1.2" fill="none"/>')
    f.text(920,360,r'\(\ket0\)','small')
    f.text(700,78,r'\(\ket1\)','small')
    for path,color in [('M700 340L868 214',orange),('M700 340L574 172',green),('M700 340V130',EDGE)]:
        f.parts.append(f'<path class="edge" d="{path}" style="stroke:{color}"/>')
    f.text(880,198,r'\(U\ket0\)')
    f.text(565,150,r'\(U\ket1\)')
    f.text(739,120,r'\(U\ket\psi\)')
    # A parallelogram adds the weighted transformed basis vectors.
    f.parts.append(f'<path d="M800.8 264.4L700 130" fill="none" stroke="{green}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    f.parts.append(f'<path d="M599.2 205.6L700 130" fill="none" stroke="{orange}" stroke-width="1.4" stroke-dasharray="5 4"/>')
    f.parts.append(f'<circle cx="800.8" cy="264.4" r="3.5" fill="{orange}"/><circle cx="599.2" cy="205.6" r="3.5" fill="{green}"/>')
    f.text(830,291,r'\(\frac35U\ket0\)','small')
    f.text(777,184,r'\(\frac45U\ket1\)','small')
    f.parts.append('<path class="rule" d="M465 55V385"/>')
    f.text(480,425,'The state changes; the coordinate axes stay fixed.','small')
    f.text(480,470,r'\(U=\frac15\begin{pmatrix}4&-3\\3&4\end{pmatrix},\qquad \ket\psi=\begin{pmatrix}3/5\\4/5\end{pmatrix},\qquad U\ket\psi=\begin{pmatrix}0\\1\end{pmatrix}\)')
    f.text(480,515,r'\(U\ket\psi=\frac35U\ket0+\frac45U\ket1=\ket1\)')
    f.save('transition-matrix-geometry')

def adjoint_geometry_figure():
    """Compare both images with the initial vector on common axes."""
    import math
    f = Figure('A matrix and its adjoint acting on the same vector',
        'One set of axes shows the initial vector psi in blue at coordinates three fifths,four fifths, A psi in orange at seven fifths,four fifths, and A dagger psi in green at three fifths,seven fifths. A is the horizontal shear with rows one,one and zero,one; its adjoint is the vertical shear with rows one,zero and one,one. An orange arc alpha measures the angle from A psi to psi, about 23.4 degrees. A green arc beta measures the angle from psi to A dagger psi, about 13.7 degrees. The arcs compare directions, not lengths. The adjoint does not undo A.',
        width=800, height=520)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    orange,green='#a64d26','#347449'
    f.text(400,30,'Same initial vector, two different images','heading')
    ox,oy,scale=145,370,180
    f.parts.append('<path d="M110 370H480 M145 395V65" stroke="#d3dee7" stroke-width="1.3" fill="none"/>')
    f.text(500,378,r'\(\ket0\)','small')
    f.text(124,70,r'\(\ket1\)','small')
    for x,y,color in [(.6,.8,EDGE),(1.4,.8,orange),(.6,1.4,green)]:
        f.parts.append(f'<path class="edge" d="M{ox} {oy}L{ox+scale*x:g} {oy-scale*y:g}" style="stroke:{color}"/>')
    f.parts.append('<path d="M253 118V226H397" stroke="#a7bccd" stroke-width="1.2" stroke-dasharray="4 4" fill="none"/>')
    for x,y,label,color in [(275,248,r'\(\ket\psi\)',EDGE),(432,224,r'\(A\ket\psi\)',orange),(287,102,r'\(A^\dagger\ket\psi\)',green)]:
        f.parts.append(svg_text(x,y,label,f' text-anchor="middle" style="fill:{color}"'))
    initial=math.atan2(4,3)
    image=math.atan2(4,7)
    adjoint=math.atan2(7,3)
    def arc(radius,a,b,label,color):
        x1,y1=ox+radius*math.cos(a),oy-radius*math.sin(a)
        x2,y2=ox+radius*math.cos(b),oy-radius*math.sin(b)
        f.parts.append(f'<path class="angle-arc" d="M{x1:g} {y1:g}A{radius} {radius} 0 0 0 {x2:g} {y2:g}" fill="none" stroke="{color}" stroke-width="1.7"/>')
        mid=(a+b)/2
        x,y=ox+(radius+19)*math.cos(mid),oy-(radius+19)*math.sin(mid)
        f.parts.append(svg_text(x,y,label,f' text-anchor="middle" style="fill:{color}"'))
    arc(84,image,initial,r'\(\alpha\)',orange)
    arc(112,initial,adjoint,r'\(\beta\)',green)
    f.text(625,85,r'\(A=\begin{pmatrix}1&1\\0&1\end{pmatrix}\)')
    f.text(625,165,r'\(A^\dagger=\begin{pmatrix}1&0\\1&1\end{pmatrix}\)')
    for y,label,color in [(250,r'\(\alpha\approx23.4^\circ\)',orange),(292,r'\(\beta\approx13.7^\circ\)',green)]:
        f.parts.append(svg_text(625,y,label,f' text-anchor="middle" style="fill:{color}"'))
    f.text(625,342,'Angles measured from the initial vector.','small')
    f.text(400,435,r'\(\ket\psi=\begin{pmatrix}3/5\\4/5\end{pmatrix},\quad A\ket\psi=\begin{pmatrix}7/5\\4/5\end{pmatrix},\quad A^\dagger\ket\psi=\begin{pmatrix}3/5\\7/5\end{pmatrix}\)')
    f.text(400,492,r'\(A^\dagger A=\begin{pmatrix}1&1\\1&2\end{pmatrix}\ne I\)')
    f.save('adjoint-geometry')

def adjoint_composition_geometry_figure():
    """Compare both orders of a nonunitary matrix and its adjoint."""
    import math
    f = Figure('Geometric action of AA dagger and A dagger A',
        'Common axes show initial psi at three fifths,four fifths in blue. Orange AA dagger first sends psi through A dagger to three fifths,seven fifths, then through A to two,seven fifths. Green A dagger A first sends psi through A to seven fifths,four fifths, then through A dagger to seven fifths,eleven fifths. Faint dashed rays show the intermediate vectors. Angle alpha compares AA dagger psi with psi, about 18.1 degrees; beta compares A dagger A psi with psi, about 4.4 degrees. The blue direction extends as a faint guide for the angle arc. The two products are different and neither returns psi.',
        width=850, height=570)
    f.parts[0] = f.parts[0].replace(f'fill="{EDGE}"/></marker>', 'fill="context-stroke"/></marker>')
    orange,green='#a64d26','#347449'
    f.text(425,30,'Two orders of composition on the same vector','heading')
    ox,oy,scale=120,390,125
    f.parts.append('<path d="M85 390H450 M120 420V65" stroke="#d3dee7" stroke-width="1.3" fill="none"/>')
    f.text(468,400,r'\(\ket0\)','small')
    f.text(100,75,r'\(\ket1\)','small')
    # Intermediate images retain the color of their two-step sequence.
    for x,y,color in [(.6,1.4,orange),(1.4,.8,green)]:
        f.parts.append(f'<path class="edge" d="M{ox} {oy}L{ox+scale*x:g} {oy-scale*y:g}" style="stroke:{color};opacity:.4;stroke-dasharray:5 4"/>')
    # Guides connect the endpoints after each discrete matrix application.
    f.parts.append(f'<path d="M195 290V215H370" fill="none" stroke="{orange}" stroke-width="1.1" stroke-dasharray="3 4" opacity=".5"/>')
    f.parts.append(f'<path d="M195 290H295V115" fill="none" stroke="{green}" stroke-width="1.1" stroke-dasharray="3 4" opacity=".5"/>')
    f.parts.append('<path d="M195 290L246 222" stroke="#a7bccd" stroke-width="1.1" stroke-dasharray="3 4" fill="none"/>')
    for x,y,color in [(.6,.8,EDGE),(2,1.4,orange),(1.4,2.2,green)]:
        f.parts.append(f'<path class="edge" d="M{ox} {oy}L{ox+scale*x:g} {oy-scale*y:g}" style="stroke:{color}"/>')
    for x,y,label,color in [(173,310,r'\(\ket\psi\)',EDGE),(410,213,r'\(AA^\dagger\ket\psi\)',orange),(335,97,r'\(A^\dagger A\ket\psi\)',green),(172,197,r'\(A^\dagger\ket\psi\)',orange),(337,310,r'\(A\ket\psi\)',green)]:
        f.parts.append(svg_text(x,y,label,f' text-anchor="middle" style="fill:{color}"'))
    initial=math.atan2(4,3)
    def arc(radius,a,b,label,color):
        x1,y1=ox+radius*math.cos(a),oy-radius*math.sin(a)
        x2,y2=ox+radius*math.cos(b),oy-radius*math.sin(b)
        f.parts.append(f'<path class="angle-arc" d="M{x1:g} {y1:g}A{radius} {radius} 0 0 0 {x2:g} {y2:g}" fill="none" stroke="{color}" stroke-width="1.7"/>')
        mid=(a+b)/2
        f.parts.append(svg_text(ox+(radius+18)*math.cos(mid),oy-(radius+18)*math.sin(mid),label,f' text-anchor="middle" style="fill:{color}"'))
    arc(84,math.atan2(7,10),initial,r'\(\alpha\)',orange)
    arc(160,initial,math.atan2(11,7),r'\(\beta\)',green)
    f.text(655,95,r'\(AA^\dagger=\begin{pmatrix}2&1\\1&1\end{pmatrix}\)')
    f.text(655,175,r'\(A^\dagger A=\begin{pmatrix}1&1\\1&2\end{pmatrix}\)')
    f.text(655,235,'The rightmost matrix acts first.','small')
    for y,label,color in [(287,r'\(\alpha\approx18.1^\circ\)',orange),(330,r'\(\beta\approx4.4^\circ\)',green)]:
        f.parts.append(svg_text(655,y,label,f' text-anchor="middle" style="fill:{color}"'))
    f.text(655,375,'Angles measured from the initial vector.','small')
    f.text(425,465,r'\(\ket\psi\xrightarrow{A^\dagger}\begin{pmatrix}3/5\\7/5\end{pmatrix}\xrightarrow{A}AA^\dagger\ket\psi=\begin{pmatrix}2\\7/5\end{pmatrix}\)')
    f.text(425,535,r'\(\ket\psi\xrightarrow{A}\begin{pmatrix}7/5\\4/5\end{pmatrix}\xrightarrow{A^\dagger}A^\dagger A\ket\psi=\begin{pmatrix}7/5\\11/5\end{pmatrix}\)')
    f.save('adjoint-composition-geometry')

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
    transition_matrix_figure()
    adjoint_transition_figure()
    unitarity_transition_figure()
    inner_product_geometry_figure()
    component_split_figure()
    standard_basis_ket_figure()
    transition_matrix_geometry_figure()
    adjoint_geometry_figure()
    adjoint_composition_geometry_figure()
    print('Drew 14 transition and state-geometry diagrams.')

if __name__ == '__main__':
    main()
