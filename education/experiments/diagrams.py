"""Accessible, static SVG apparatus drawings, enhanced by the lab controller."""
from html import escape as e


def text(x, y, label, cls='', anchor='middle', w=360):
    if '\\(' in label or '<span' in label:
        left = x if anchor == 'start' else (x - w if anchor == 'end' else x - w / 2)
        align = 'left' if anchor == 'start' else ('right' if anchor == 'end' else 'center')
        return (
            f'<foreignObject x="{left}" y="{y - 18}" width="{w}" height="30" class="svg-fo">'
            f'<div xmlns="http://www.w3.org/1999/xhtml" class="svg-math {cls}" style="text-align:{align}">{label}</div>'
            f'</foreignObject>'
        )
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{e(label)}</text>'


def line(x1, y1, x2, y2, cls='ray'):
    return f'<path d="M{x1} {y1} L{x2} {y2}" class="{cls}"/>'


def box(x, y, w, label, sub='', cls=''):
    return (
        f'<g class="node {cls}"><rect x="{x}" y="{y}" width="{w}" height="64" rx="10"/>'
        f'{text(x + w / 2, y + 27, label, w=w - 8)}'
        f'{text(x + w / 2, y + 48, sub, "small", w=w - 8)}</g>'
    )


def circle(x, y, r, cls=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>'


def detector(x, y, label, sub=''):
    return (
        f'<g class="node"><rect x="{x}" y="{y}" width="92" height="58" rx="8"/>'
        f'<path d="M{x} {y + 12} A18 18 0 0 1 {x} {y + 46}" class="splitter"/>'
        f'{text(x + 48, y + 26, label, w=84)}'
        f'{text(x + 48, y + 45, sub, "small", w=84)}</g>'
    )


def mirror(x, y, tilt=1):
    dx, dy = (22, 14 * tilt)
    return (
        f'<path d="M{x - dx} {y - dy} L{x + dx} {y + dy}" class="barrier"/>'
        f'<path d="M{x - dx + 4} {y - dy - 6 * tilt} L{x + dx + 4} {y + dy - 6 * tilt}" class="axis"/>'
    )


def splitter_cube(x, y, label=''):
    out = (
        f'<rect x="{x - 20}" y="{y - 20}" width="40" height="40" rx="4" class="potential" style="opacity:.45"/>'
        f'<path d="M{x - 18} {y + 18} L{x + 18} {y - 18}" class="splitter"/>'
    )
    if label:
        out += text(x, y + 38, label, 'small')
    return out


def bloch_backdrop():
    s = f'<ellipse cx="205" cy="165" rx="105" ry="37" class="sphere-ring"/>{circle(205, 165, 105, "sphere-ring")}'
    s += '<ellipse cx="205" cy="165" rx="37" ry="105" class="sphere-ring" style="stroke-dasharray:4 4"/>'
    s += line(205, 285, 205, 45, 'axis') + line(80, 165, 330, 165, 'axis') + line(130, 225, 280, 105, 'axis')
    s += (
        text(205, 36, r'\(|0\rangle\)', w=80)
        + text(205, 304, r'\(|1\rangle\)', w=80)
        + text(346, 170, r'\(+x\)', 'small', w=60)
        + text(292, 96, r'\(+y\)', 'small', w=60)
    )
    s += '<path d="M205 165 L205 60" class="state-vector"/><circle class="state-tip" cx="205" cy="60" r="6"/>'
    return s


def svg(kind, title):
    s = ''
    desc = 'Schematic apparatus; geometry and moving indicators are explanatory, not measured trajectories.'
    if kind in ('mzi', 'delayed', 'eraser', 'bomb'):
        s += (
            line(35, 160, 175, 160)
            + line(175, 160, 340, 60)
            + line(340, 60, 505, 160)
            + line(175, 160, 340, 260)
            + line(340, 260, 505, 160)
            + line(505, 160, 610, 95)
            + line(505, 160, 610, 235)
        )
        s += mirror(340, 60, 1) + mirror(340, 260, -1)
        s += splitter_cube(175, 160, r'\(\mathrm{BS}_1\)') + splitter_cube(505, 160, r'\(\mathrm{BS}_2\)')
        s += circle(42, 160, 11, 'source') + text(45, 195, 'Source', 'small')
        s += text(235, 92, 'upper arm', 'small') + text(235, 240, 'lower arm', 'small')
        s += detector(605, 48, r'\(D_0\)', 'port 0') + detector(605, 226, r'\(D_1\)', 'port 1')
        s += '<g class="node"><rect x="288" y="14" width="104" height="36" rx="6"/>' + text(340, 37, r'Phase \(\phi\)', 'small', w=100) + '</g>'
        if kind == 'bomb':
            s += box(278, 223, 125, 'Absorber', 'opaque arm', 'absorber')
        if kind == 'eraser':
            s += box(258, 218, 164, 'Path marker', r'\(|H\rangle / |V\rangle \to |\pm\rangle\)')
        if kind == 'delayed':
            s += text(505, 314, r'Late switch: keep or remove \(\mathrm{BS}_2\)', 'small')
        s += '<circle class="traveller" cx="42" cy="160" r="7"/>'
    elif kind in ('rabi', 'ramsey', 'tomography', 'teleport', 'sensing'):
        s += bloch_backdrop()
        if kind == 'teleport':
            s += (
                box(392, 26, 290, r'Alice: \(\mathrm{CNOT} + H\) + measure', r'two classical bits \((a, b)\)')
                + line(537, 90, 537, 134, 'axis')
                + box(392, 136, 290, 'Bob: pre-correction branch', r'conditional state \(X^b Z^a |\psi\rangle\)')
                + line(537, 200, 537, 242, 'axis')
                + box(392, 244, 290, 'Feed-forward recovery', r'apply \(Z^a X^b \to |\psi\rangle\)')
            )
        elif kind == 'tomography':
            for y, label, sub in [
                (38, r'\(X\)-basis analyzer', r'measure \(P(+X) \to r_x\)'),
                (136, r'\(Y\)-basis analyzer', r'measure \(P(+Y) \to r_y\)'),
                (234, r'\(Z\)-basis analyzer', r'measure \(P(+Z) \to r_z\)'),
            ]:
                s += box(412, y, 265, label, sub)
        elif kind == 'ramsey':
            s += (
                box(402, 28, 275, r'\(\pi/2\) pulse \(\to\) free delay \(\tau\)', r'accumulate phase \(\Delta\tau\)')
                + line(539, 92, 539, 134, 'axis')
                + box(402, 136, 275, r'Optional midpoint \(\pi\) echo', 'refocus static detuning')
                + line(539, 200, 539, 242, 'axis')
                + box(402, 244, 275, r'Second \(\pi/2\) + readout', r'envelope \(W(\tau) = \exp(-\tau/T_2)\)')
            )
        elif kind == 'sensing':
            s += (
                box(402, 28, 275, 'Quadrature Ramsey probe', r'slope \(\partial p/\partial\Delta = W\tau / 2\)')
                + line(539, 92, 539, 134, 'axis')
                + box(402, 136, 275, r'\(N\) repeated interrogations', r'shot noise \(1/(2\sqrt{N})\)')
                + line(539, 200, 539, 242, 'axis')
                + box(402, 244, 275, 'Frequency estimator', r'\(\delta\Delta \approx 1 / (W\tau\sqrt{N})\)')
            )
        else:
            s += (
                box(402, 28, 275, r'Prepare \(|0\rangle\) state', 'calibrated initial population')
                + line(539, 92, 539, 134, 'axis')
                + box(402, 136, 275, r'Resonant drive pulse \(\Omega t\)', r'unitary rotation \(\exp(-i\Omega t X/2)\)')
                + line(539, 200, 539, 242, 'axis')
                + box(402, 244, 275, 'Projective population readout', r'\(P_1 = \sin^2(\Omega t/2)\)')
            )
    elif kind in ('cat', 'friend'):
        s += box(15, 130, 135, r'Prepare \(|+\rangle\)', 'trigger qubit') + line(150, 162, 275, 92) + line(150, 162, 275, 246)
        s += '<rect x="248" y="18" width="276" height="292" rx="16" class="lab-boundary"/>'
        s += (
            text(386, 45, 'Isolated laboratory (unitary coupling)', 'small')
            + box(272, 60, 228, r'\(|0, R_0\rangle\)', r'branch weight \(1/2\)')
            + box(272, 214, 228, r'\(|1, R_1\rangle\)', r'branch weight \(1/2\)')
        )
        s += '<path d="M386 124 V214" class="coherence-link"/>' + text(448, 173, r'coherence \(\gamma\)', 'accent', w=120)
        s += line(524, 162, 568, 162) + box(570, 130, 135, 'Superobserver', 'record / interfere')
        if kind == 'cat':
            s += text(386, 335, 'Macroscopic pointer branches with controllable decoherence.', 'small')
        else:
            s += text(386, 335, 'Friend memory register probed in record or interference basis.', 'small')
    elif kind == 'extended':
        for y, label, sign in [(28, r'\(|0, 0\rangle\)', '+'), (128, r'\(|1, 0\rangle\)', '-'), (228, r'\(|1, 1\rangle\)', '+')]:
            s += (
                box(22, y, 152, label, r'state weight \(1/\sqrt{3}\)')
                + line(174, y + 32, 338, y + 32)
                + text(256, y + 20, rf'\({sign}1/\sqrt{{12}}\)', 'accent', w=120)
                + line(338, y + 32, 456, 162)
            )
        s += (
            box(456, 128, 240, r'Outside \(|\mathrm{ok}, \mathrm{ok}\rangle\)', 'sum amplitudes, then square')
            + text(576, 236, r'\((+1 - 1 + 1)^2 / 12 = 1/12\)', 'accent', w=260)
            + text(576, 266, 'Destructive cancellation of two of three branches', 'small')
        )
    elif kind == 'ghz':
        s += box(255, 18, 210, '3-Qubit GHZ Source', r'\((|000\rangle + |111\rangle)/\sqrt{2}\)')
        for x, label, sub in [
            (20, 'Alice (qubit 1)', r'measure \(X_1\) or \(Y_1\)'),
            (265, 'Bob (qubit 2)', r'measure \(X_2\) or \(Y_2\)'),
            (510, 'Charlie (qubit 3)', r'measure \(X_3\) or \(Y_3\)'),
        ]:
            s += line(360, 82, x + 95, 162) + box(x, 162, 190, label, sub)
        s += (
            text(360, 282, r'\(X_1 X_2 X_3 = +1 \quad X_1 Y_2 Y_3 = -1 \quad Y_1 X_2 Y_3 = -1 \quad Y_1 Y_2 X_3 = -1\)', 'accent', w=640)
            + text(360, 316, r'Product of the last three parity constraints contradicts \(X_1 X_2 X_3 = +1\).', 'small', w=640)
        )
    elif kind == 'bell':
        s += (
            box(262, 126, 196, 'Entangled Singlet Source', r'\((|01\rangle - |10\rangle)/\sqrt{2}\)')
            + line(262, 158, 175, 158)
            + line(458, 158, 545, 158)
        )
        s += (
            box(18, 126, 157, 'Alice Station', r'\(a_0=0^\circ,\; a_1=90^\circ\)')
            + box(545, 126, 157, 'Bob Station', r'\(b_0=\theta,\; b_1=-\theta\)')
            + text(360, 52, r'Spacelike separated setting choices · outcomes \(\pm 1\)', 'accent', w=520)
            + text(360, 268, r'CHSH combination: \(S = E_{00} + E_{01} + E_{10} - E_{11}\) (\(|S| \le 2\) locally)', 'small', w=620)
        )
    elif kind == 'hom':
        s += (
            line(65, 60, 360, 170)
            + line(65, 280, 360, 170)
            + line(360, 170, 565, 62)
            + line(360, 170, 565, 278)
        )
        s += (
            splitter_cube(360, 170, '50:50 BS')
            + box(15, 25, 172, r'Input Photon \(A\)', r'mode \(a\) (reference)')
            + box(15, 245, 172, r'Input Photon \(B\)', r'mode \(b\) (delay \(\Delta\tau\))')
            + detector(565, 30, r'\(D_c\)', 'port c')
            + detector(565, 246, r'\(D_d\)', 'port d')
        )
        s += (
            '<g class="packet-a"><ellipse cx="245" cy="127" rx="38" ry="12" class="packet"/></g>'
            '<g class="packet-b"><ellipse cx="245" cy="213" rx="38" ry="12" class="packet secondary"/></g>'
            + text(360, 326, r'Both-reflect and both-transmit amplitudes cancel at \(\Delta\tau = 0\).', 'small', w=560)
        )
    elif kind == 'slits':
        s += (
            circle(52, 170, 13, 'source')
            + text(52, 208, 'Collimated', 'small')
            + text(52, 225, 'source', 'small')
            + line(65, 170, 235, 125)
            + line(65, 170, 235, 215)
        )
        s += '<path d="M240 28V114 M240 136V204 M240 226V312" class="barrier"/>'
        for sy in [125, 215]:
            for y in [40, 95, 155, 215, 275, 315]:
                s += line(245, sy, 630, y, 'alternative')
        s += (
            line(635, 28, 635, 315, 'barrier')
            + text(240, 336, r'Double slit (spacing \(d\))', 'small', w=220)
            + text(630, 336, 'Detector screen', 'small')
            + text(435, 22, r'Superposed path amplitudes \(\psi_1(x) + \psi_2(x)\)', 'small', w=360)
        )
    elif kind == 'recoil':
        s += (
            box(22, 135, 152, 'Path superpos.', r'\((|1\rangle + |2\rangle)/\sqrt{2}\)')
            + line(174, 167, 298, 167)
            + box(298, 135, 184, 'Movable slit pointer', r'states \(|\chi_1\rangle, |\chi_2\rangle\)')
            + line(482, 167, 580, 167)
            + box(580, 135, 118, 'Screen', r'\(V = |\langle\chi_1|\chi_2\rangle|\)')
        )
        s += (
            '<g class="pointer-waves"></g>'
            + text(390, 36, r'Pointer wavepackets overlap \(V = \exp(-\Delta^2 / 8\sigma^2)\)', 'accent', w=480)
            + text(390, 318, r'Duality relation for pure balanced states: \(D^2 + V^2 = 1\)', 'small', w=480)
        )
    elif kind == 'tunnel':
        s += (
            '<path d="M35 250H680" class="axis"/>'
            '<rect x="300" y="60" width="120" height="190" class="potential"/>'
            '<path d="M35 155H680" class="energy-line"/>'
        )
        s += (
            text(360, 44, r'Barrier height \(V_0\)', w=200)
            + text(52, 144, r'Particle energy \(E = V_0/2\)', 'small', 'start', w=220)
            + text(360, 278, r'Barrier width \(a\) (decay \(\kappa\))', 'small', w=240)
            + text(145, 314, 'Incident + reflected wave', 'small')
            + text(575, 314, r'Transmitted wave (energy \(E\))', 'small', w=240)
            + '<path class="tunnel-wave" d="M40 200H680"/>'
        )
    elif kind == 'polarization':
        s += line(35, 167, 680, 167)
        for x, angle, label, sub in [
            (150, 0, r'Filter 1: \(H\) (\(0^\circ\))', r'prepares \(|H\rangle\)'),
            (360, 45, r'Filter 2: \(\theta\)', r'projects onto \(|\theta\rangle\)'),
            (565, 90, r'Filter 3: \(V\) (\(90^\circ\))', r'\(P = \frac{1}{4}\sin^2(2\theta)\)'),
        ]:
            s += (
                f'<ellipse cx="{x}" cy="167" rx="43" ry="86" class="filter"/>'
                f'<g transform="rotate({angle} {x} 167)"'
                + (' class="middle-axis"' if x == 360 else '')
                + f'><path d="M{x} 96V238" class="filter-axis"/></g>'
                + text(x, 280, label, 'small', w=180)
                + text(x, 300, sub, 'small', w=180)
            )
    elif kind == 'spin':
        s += (
            box(18, 138, 145, 'Oven + Slit', r'prepares \(|+z\rangle\)')
            + line(163, 170, 278, 170)
            + box(278, 138, 152, r'SG Magnet (\(\theta\))', r'gradient \(\partial B/\partial n\)')
            + line(430, 152, 575, 72)
            + line(430, 188, 575, 268)
            + detector(575, 38, r'\(+\theta\) port', r'\(\cos^2(\theta/2)\)')
            + detector(575, 236, r'\(-\theta\) port', r'\(\sin^2(\theta/2)\)')
            + text(355, 314, 'Quantized deflection into two orthogonal spin channels.', 'small')
        )
    elif kind == 'energy':
        s += (
            box(18, 135, 158, 'Monochromatic', r'photons \(E = h\nu\)')
            + line(176, 167, 318, 167)
            + '<rect x="320" y="58" width="76" height="224" rx="6" class="potential"/>'
            + text(358, 40, 'Photocathode', 'small')
            + text(358, 308, r'Work function \(\Phi = 2\,\mathrm{eV}\)', 'small', w=220)
            + line(396, 167, 542, 167)
            + box(542, 135, 160, 'Retarding grid', r'stopping bias \(V_s\)')
            + text(530, 82, r'\(K_{\max} = h\nu - \Phi = eV_s\)', 'accent', w=260)
        )
    elif kind == 'photons':
        s += (
            box(15, 137, 160, 'Light Source', r'select \(g^{(2)}(\tau)\) model')
            + line(175, 169, 345, 169)
            + line(345, 169, 555, 65)
            + line(345, 169, 555, 262)
            + splitter_cube(345, 169, '50:50 BS')
            + detector(555, 32, r'\(D_A\)', r'start \(t\)')
            + detector(555, 232, r'\(D_B\)', r'stop \(t+\tau\)')
            + '<path d="M647 61 H688 V261 H647" class="axis"/>'
            + text(360, 324, r'Hanbury Brown–Twiss coincidence timer: \(g^{(2)}(\tau)\) across delay \(\tau\)', 'accent', w=600)
        )
    elif kind == 'capstone':
        for x, l, sub in [
            (15, '1. Phase Scan', r'\(16\text{ phases} \times 200\text{ trials}\)'),
            (255, '2. Moment Fit', r'estimate \(\hat{V} \pm \mathrm{SE}\)'),
            (495, '3. Audit Report', 'residuals & scope'),
        ]:
            s += box(x, 120, 205, l, sub)
        s += (
            line(220, 152, 255, 152)
            + line(460, 152, 495, 152)
            + text(360, 55, 'Reproducible interference audit workflow', 'accent')
            + text(360, 272, r'Export seeded CSV \(\to\) verify estimator \(\to\) inspect phase residuals.', 'small', w=560)
        )
    else:
        s += (
            '<rect x="16" y="20" width="168" height="240" rx="12" class="lab-boundary"/>'
            + text(100, 44, '1. Preparation', 'small')
            + circle(72, 150, 14, 'source')
            + '<circle cx="72" cy="150" r="22" class="sphere-ring"/>'
            + text(72, 192, 'Triggered source', 'small')
            + '<path d="M136 112V138 M136 162V188" class="barrier"/>'
            + text(136, 212, 'Collimator', 'small')
            + line(86, 150, 290, 150)
            + '<rect x="210" y="20" width="180" height="240" rx="12" class="lab-boundary"/>'
            + text(300, 44, '2. Transformation', 'small')
            + splitter_cube(300, 150, 'Two-channel analyzer')
            + line(300, 150, 495, 78)
            + line(300, 150, 495, 222)
            + text(395, 92, r'Channel \(A\) (\(\text{prob } p\))', 'small', w=180)
            + text(395, 236, r'Channel \(B\) (\(\text{prob } 1-p\))', 'small', w=180)
            + '<rect x="420" y="20" width="284" height="240" rx="12" class="lab-boundary"/>'
            + text(562, 44, '3. Measurement & Ledger', 'small')
            + detector(495, 48, r'\(D_A\)', r'\(\eta_A\)')
            + detector(495, 192, r'\(D_B\)', r'\(\eta_B\)')
            + '<circle class="det-flash-a" cx="495" cy="77" r="16" fill="var(--lab-blue)" opacity="0"/>'
            + '<circle class="det-flash-b" cx="495" cy="221" r="16" fill="var(--lab-gold)" opacity="0"/>'
            + '<g class="node"><rect x="602" y="64" width="90" height="168" rx="8"/>'
            + text(647, 92, 'Ledger', 'small')
            + text(647, 124, r'\(k_A = \) <span class="counts-ka">0</span>', 'accent', w=86)
            + text(647, 156, r'\(k_B = \) <span class="counts-kb">0</span>', '', w=86)
            + text(647, 188, r'\(N = \) <span class="counts-n">0</span>', 'small', w=86)
            + text(647, 214, r'\(\hat{p} = \) <span class="counts-phat">—</span>', 'small', w=86)
            + '</g>'
            + '<circle class="counts-traveller" cx="72" cy="150" r="8" fill="var(--accent)" opacity="0"/>'
            + '<g class="counts-tape" transform="translate(24, 282)">'
            + '<rect x="0" y="0" width="672" height="48" rx="8" fill="var(--sidebar)" stroke="var(--line)"/>'
            + text(14, 29, 'Recent trials:', 'small', 'start')
            + '<g class="counts-tape-cells" transform="translate(115, 9)"></g>'
            + '</g>'
        )
    return f'<svg class="qe-apparatus" viewBox="0 0 720 350" role="img" aria-labelledby="diagram-title diagram-desc"><title id="diagram-title">{e(title)}</title><desc id="diagram-desc">{e(desc)}</desc>{s}</svg>'


# Formula badges for Section N.2 (quantitative law) and Section N.3 (experimental threshold)
SECTION_FORMULAS = {
    'counts': (
        r'\(P(k_A\mid N,p) = \binom{N}{k_A}p^{k_A}(1-p)^{N-k_A}, \quad \mathrm{SE}(\hat{p}) = \sqrt{p(1-p)/N}\)',
        r'\(\hat{p}_{\mathrm{cal}} = \frac{\sqrt{R_1 R_2}}{1 + \sqrt{R_1 R_2}}, \quad f_A = \frac{p\,\eta_A}{p\,\eta_A + (1-p)\,\eta_B}\)',
    ),
    'energy': (
        r'\(K_{\max} = h\nu - \Phi = eV_s \quad (\text{for } h\nu \ge \Phi)\)',
        r'\(I_{\mathrm{photo}} = \eta\,\frac{P_{\mathrm{opt}}}{h\nu}\,\Theta(h\nu - \Phi - eV)\)',
    ),
    'slits': (
        r'\(I(x) = I_0(x)\big[1 + V\cos(2\pi d\,x / \lambda L)\big]\)',
        r'\(V_{\mathrm{obs}} = \eta\,|\gamma_{12}|, \quad \mathrm{SE}(\hat{p}_m) = \sqrt{p_m(1-p_m)/N}\)',
    ),
    'spin': (
        r'\(P(+\theta) = \cos^2(\theta/2), \quad P(-\theta) = \sin^2(\theta/2)\)',
        r'\(\langle\sigma_\theta\rangle_{\mathrm{obs}} = \eta\cos\theta, \quad P_{\mathrm{obs}}(\pm\theta) = \frac{1 \pm \eta\cos\theta}{2}\)',
    ),
    'polarization': (
        r'\(P_{\mathrm{3-pol}}(\theta) = \cos^2\theta\,\sin^2\theta = \frac{1}{4}\sin^2(2\theta)\)',
        r'\(P_{\mathrm{obs}}(\theta) = \frac{\eta}{4}\sin^2(2\theta) + (1-\eta)\epsilon_{\mathrm{leak}}\)',
    ),
    'photons': (
        r'\(g^{(2)}(\tau) = \frac{\langle : \hat{I}(t)\hat{I}(t+\tau) : \rangle}{\langle\hat{I}(t)\rangle^2}\)',
        r'\(g^{(2)}_{\mathrm{obs}}(0) = 1 - \eta < 1 \;\Longleftrightarrow\; \text{nonclassical anti-bunching}\)',
    ),
    'mzi': (
        r'\(P(D_0) = \frac{1}{2}(1 + V\cos\phi), \quad P(D_1) = \frac{1}{2}(1 - V\cos\phi)\)',
        r'\(V = \frac{P_{\max} - P_{\min}}{P_{\max} + P_{\min}} = 2\sqrt{p_u(1-p_u)}\,|\langle e_u|e_\ell\rangle|\)',
    ),
    'recoil': (
        r'\(V = |\langle\chi_1|\chi_2\rangle| = \exp\!\big(-\Delta^2/(8\sigma^2)\big), \quad D = \sqrt{1 - V^2}\)',
        r'\(D^2 + V_{\mathrm{obs}}^2 = \eta^2 \le 1 \quad (\text{Englert–Greenberger duality})\)',
    ),
    'delayed': (
        r'\(P_{\mathrm{closed}}(D_0) = \cos^2(\phi/2), \quad P_{\mathrm{open}}(D_0) = \frac{1}{2}\)',
        r'\(P_{\mathrm{obs}}(D_0) = \frac{1}{2}\big(1 + \eta\,s_{\mathrm{BS2}}\cos\phi\big)\)',
    ),
    'eraser': (
        r'\(P(D_0\mid \pm) = \frac{1}{2}(1 \pm \cos\phi), \quad P_{\mathrm{unsorted}}(D_0) = \frac{1}{2}\)',
        r'\(V_{\mathrm{cond}} = \eta, \quad P(D_0) = \frac{1}{2}P(D_0\mid +) + \frac{1}{2}P(D_0\mid -) = \frac{1}{2}\)',
    ),
    'bomb': (
        r'\(P_{\mathrm{abs}} = \frac{1}{2}, \quad P(D_0) = \frac{1}{4}, \quad P(D_1) = \frac{1}{4}\)',
        r'\(\eta_{\mathrm{IFM}} = \frac{P(D_1)}{P(D_1) + P_{\mathrm{abs}}} \to \frac{1}{3} \quad (\text{single-pass})\)',
    ),
    'tunnel': (
        r'\(T(\kappa a) = \frac{1}{1 + \sinh^2(\kappa a)} = \mathrm{sech}^2(\kappa a) \quad (E = V_0/2)\)',
        r'\(\ln T(\kappa a) \approx \ln 4 - 2\kappa a, \quad \kappa = \sqrt{2m(V_0 - E)}/\hbar\)',
    ),
    'rabi': (
        r'\(P_1(t) = \frac{\Omega^2}{\Omega_{\mathrm{eff}}^2}\sin^2\!\left(\frac{\Omega_{\mathrm{eff}}\,t}{2}\right), \quad \Theta = \Omega t\)',
        r'\(P_{1,\mathrm{obs}}(t) = \frac{1}{2}\big[1 - \eta\cos(\Omega t)\big]\)',
    ),
    'ramsey': (
        r'\(P_0(\tau) = \frac{1}{2}\big[1 + W(\tau)\cos(\Delta\tau)\big], \quad W(\tau) = e^{-\tau/T_2}\)',
        r'\(\frac{1}{T_2} = \frac{1}{2T_1} + \frac{1}{T_\phi} \;\Longrightarrow\; T_2 \le 2T_1\)',
    ),
    'tomography': (
        r'\(\rho = \frac{1}{2}(I + r_x X + r_y Y + r_z Z), \quad \mathrm{Tr}(\rho^2) = \frac{1 + \|\vec{r}\|^2}{2}\)',
        r'\(\|\hat{\vec{r}}\| \le 1 \;\Longleftrightarrow\; \hat{\lambda}_{\pm} = \frac{1 \pm \|\hat{\vec{r}}\|}{2} \ge 0\)',
    ),
    'hom': (
        r'\(P_{cd}(\Delta\tau) = \frac{1}{2}\big[1 - J(\Delta\tau)\big], \quad J(\Delta\tau) = e^{-\Delta\tau^2/\tau_c^2}\)',
        r'\(V_{\mathrm{HOM}} = \frac{C(\infty) - C(0)}{C(\infty)} = \eta > 0.50 \;\;(\text{nonclassical threshold})\)',
    ),
    'bell': (
        r'\(E_Q(\theta_a,\theta_b) = -\cos(\theta_a - \theta_b), \quad |S_Q(\theta)| = 2(\cos\theta + \sin\theta)\)',
        r'\(|S_{\mathrm{obs}}| = 2\sqrt{2}\,\eta > 2 \;\Longleftrightarrow\; \eta > 1/\sqrt{2} \approx 0.7071\)',
    ),
    'ghz': (
        r'\(\langle X_1 X_2 X_3\rangle = +1, \quad \langle X_1 Y_2 Y_3\rangle = \langle Y_1 X_2 Y_3\rangle = \langle Y_1 Y_2 X_3\rangle = -1\)',
        r'\(\langle\hat{\mathcal{M}}\rangle = 4\eta > 2 \;\Longleftrightarrow\; \eta > 0.50 \quad (\text{Mermin witness})\)',
    ),
    'teleport': (
        r'\(|\psi\rangle_S|\Phi^+\rangle_{AB} = \frac{1}{2}\sum_{a,b\in\{0,1\}} |\Phi_{ab}\rangle_{SA}\otimes(X^b Z^a|\psi\rangle_B)\)',
        r'\(\bar{F}_{\mathrm{tele}}(\eta) = \frac{1 + \eta}{2} > \frac{2}{3} \;\Longleftrightarrow\; \eta > \frac{1}{3}\)',
    ),
    'cat': (
        r'\(\rho_{SM}(W) = \frac{1}{2}\big(|\Phi_0\rangle\langle\Phi_0| + |\Phi_1\rangle\langle\Phi_1| + W|\Phi_0\rangle\langle\Phi_1| + \text{h.c.}\big)\)',
        r'\(W(t) = |\langle E_0|E_1\rangle| = \exp(-2\kappa\bar{n}\,t), \quad \mathrm{Tr}(\rho_{SM}^2) = \frac{1 + W^2}{2}\)',
    ),
    'friend': (
        r'\(|\Psi_{SF}\rangle = \mathrm{CNOT}_{S\to F}(|+\rangle_S|0\rangle_F) = \frac{|00\rangle_{SF} + |11\rangle_{SF}}{\sqrt{2}}\)',
        r'\(P_+(\phi) = \frac{1}{2}(1 + \gamma\cos\phi), \quad [Z_F,\, X_S\otimes X_F] = 2i(X_S\otimes Y_F) \neq 0\)',
    ),
    'extended': (
        r'\(\langle\mathrm{ok},\mathrm{ok}|\Psi_{L_1 L_2}\rangle = \frac{1}{2\sqrt{3}}(1 - 0 - 1 + 1) = \frac{1}{2\sqrt{3}} \;\Rightarrow\; P = \frac{1}{12}\)',
        r'\(P(\mathrm{ok}_1,\mathrm{ok}_2) = \frac{3 - 4\eta + 2\eta^2}{12} \in \left[\frac{1}{12},\, \frac{1}{4}\right]\)',
    ),
    'sensing': (
        r'\(\delta\Delta(\tau) = \frac{1}{\sqrt{N}\,\tau\,W(\tau)}, \quad \tau_{\mathrm{opt}}^{\mathrm{fixed}\,N} = T_2, \quad \tau_{\mathrm{opt}}^{\mathrm{fixed}\,T} = \frac{T_2}{2}\)',
        r'\(\delta\Delta_{\mathrm{obs}}(\tau) = \frac{e^{\tau/T_2}}{\eta\sqrt{N}\,\tau}\)',
    ),
    'capstone': (
        r'\(\hat{V}_c = \frac{4}{M}\sum_{m=0}^{M-1}\hat{p}_m\cos\phi_m, \quad \widehat{\mathrm{SE}}(\hat{V}_c) = \frac{4}{M}\sqrt{\sum_m \frac{\hat{p}_m(1-\hat{p}_m)}{N_m}\cos^2\phi_m}\)',
        r'\(r_m = \frac{\hat{p}_m - \hat{p}_{\mathrm{fit}}(\phi_m)}{\sqrt{\hat{p}_{\mathrm{fit}}(1-\hat{p}_{\mathrm{fit}})/N_m}}, \quad \chi^2 = \sum_{m=0}^{M-1} r_m^2\)',
    ),
}


def scene_svg(name, chapter=None):
    """Render an inline section visual animation apparatus SVG with MathJax notation."""
    if name == 'section-1-1':
        s = (
            '<title id="scene-1-1-title">Animated two-outcome quantum experiment: preparation, transformation, and measurement</title>'
            '<desc id="scene-1-1-desc">Interactive schematic of a triggered single-quantum source, two-channel analyzer, detectors with efficiencies eta_A and eta_B, digital counter ledger, and trial-by-trial event tape.</desc>'
            '<g class="scene-stage stage-prep" data-stage="prep">'
            '<rect x="16" y="18" width="196" height="252" rx="12" class="lab-boundary stage-box"/>'
            + text(114, 42, '1. PREPARATION', 'accent')
            + text(114, 61, 'Heralded trigger window', 'small')
            + '<g class="node"><rect x="32" y="82" width="102" height="62" rx="8"/>'
            + text(83, 108, 'Source')
            + text(83, 129, '1 pulse / gate', 'small')
            + '</g>'
            + '<circle class="trigger-led" cx="46" cy="96" r="5" fill="var(--lab-blue)" opacity="0.35"/>'
            + '<path d="M40 174 H62 V156 H82 V174 H104 V156 H124 V174 H146" class="axis"/>'
            + text(93, 193, r'Trigger clock \(t_1, t_2, \dots, t_N\)', 'small', w=180)
            + '<path d="M168 80 V128 M168 152 V204" class="barrier"/>'
            + text(168, 224, 'Collimator', 'small')
            + '<text x="114" y="252" text-anchor="middle" class="small prep-status">Gate ready</text>'
            + '</g>'
            + '<g class="scene-stage stage-trans" data-stage="trans">'
            + '<rect x="226" y="18" width="214" height="252" rx="12" class="lab-boundary stage-box"/>'
            + text(333, 42, '2. TRANSFORMATION', 'accent')
            + text(333, 61, r'Two-channel analyzer \(U(p)\)', 'small', w=200)
            + line(134, 140, 326, 140)
            + splitter_cube(326, 140, 'Analyzer BS')
            + line(326, 140, 502, 76, 'ray branch-a')
            + line(326, 140, 502, 204, 'ray branch-b')
            + text(412, 88, r'Channel \(A\): \(p = \) <span class="val-pa">0.50</span>', 'small', w=176)
            + text(412, 222, r'Channel \(B\): \(1-p = \) <span class="val-pb">0.50</span>', 'small', w=176)
            + text(333, 252, r'Superposition \(\sqrt{p}\,|A\rangle + \sqrt{1-p}\,|B\rangle\)', 'small', w=210)
            + '</g>'
            + '<g class="scene-stage stage-meas" data-stage="meas">'
            + '<rect x="454" y="18" width="290" height="252" rx="12" class="lab-boundary stage-box"/>'
            + text(599, 42, '3. MEASUREMENT', 'accent')
            + text(599, 61, 'Detectors & event counter', 'small')
            + detector(502, 47, r'\(D_A\)', r'\(\eta_A = \) <span class="val-eta-a">1.00</span>')
            + detector(502, 175, r'\(D_B\)', r'\(\eta_B = \) <span class="val-eta-b">1.00</span>')
            + '<circle class="scene-flash-a" cx="502" cy="76" r="18" fill="var(--lab-blue)" opacity="0"/>'
            + '<circle class="scene-flash-b" cx="502" cy="204" r="18" fill="var(--lab-gold)" opacity="0"/>'
            + '<path d="M594 76 H616 M594 204 H616" class="axis"/>'
            + '<g class="node"><rect x="616" y="47" width="114" height="186" rx="8"/>'
            + text(673, 71, 'Counter', 'small')
            + text(673, 99, r'\(k_A = \) <span class="scene-ka">0</span>', 'accent', w=108)
            + text(673, 125, r'\(k_B = \) <span class="scene-kb">0</span>', '', w=108)
            + text(673, 151, r'\(k_{\mathrm{miss}} = \) <span class="scene-kmiss">0</span>', 'small', w=108)
            + text(673, 177, r'\(N = \) <span class="scene-ntrials">0</span>', 'small', w=108)
            + text(673, 204, r'\(f_A = \) <span class="scene-fa">—</span>', 'small', w=108)
            + text(673, 223, r'\(\mathrm{SE} = \) <span class="scene-se">—</span>', 'small', w=108)
            + '</g>'
            + '<text x="599" y="252" text-anchor="middle" class="small meas-status">Waiting for first trigger window</text>'
            + '</g>'
            + '<circle class="scene-packet-in" cx="134" cy="140" r="8" fill="var(--accent)" opacity="0"/>'
            + '<circle class="scene-packet-a" cx="326" cy="140" r="7" fill="var(--lab-blue)" opacity="0"/>'
            + '<circle class="scene-packet-b" cx="326" cy="140" r="7" fill="var(--lab-gold)" opacity="0"/>'
            + '<g class="scene-tape" transform="translate(16, 282)">'
            + '<rect x="0" y="0" width="728" height="72" rx="10" fill="var(--sidebar)" stroke="var(--line)"/>'
            + '<text x="14" y="23" text-anchor="start" class="small">Trial log (seeded sequence):</text>'
            + '<text x="714" y="23" text-anchor="end" class="small scene-seed-label">Seed 2026 · deterministic replay</text>'
            + '<g class="scene-tape-cells" transform="translate(14, 32)"></g>'
            + '</g>'
        )
        return f'<svg class="qe-apparatus qe-scene-svg" viewBox="0 0 760 366" role="img" aria-labelledby="scene-1-1-title scene-1-1-desc">{s}</svg>'

    if name == 'section-1-2':
        s = (
            '<title id="scene-1-2-title">Binomial distribution, standard-error scaling, and detector efficiency bias</title>'
            '<desc id="scene-1-2-desc">Left panel shows the binomial distribution P(k_A | N, p) and one-sigma band; right panel shows the 1/sqrt(N) standard-error funnel and efficiency-postselected fraction f_A.</desc>'
            '<rect x="16" y="16" width="354" height="318" rx="12" class="lab-boundary"/>'
            + text(193, 40, r'1. Binomial Distribution \(P(k_A\mid N, p)\)', 'accent', w=330)
            + text(193, 62, r'\(\langle k_A\rangle = Np = \) <span class="s12-mean">50.0</span> \(\;\pm\; \sigma_k = \) <span class="s12-sigma">5.00</span>', 'small', w=330)
            + '<g class="s12-hist" transform="translate(36, 78)"></g>'
            + text(193, 316, r'Sample draw: \(k_A = \) <span class="s12-ka">53</span> (\(|z| = \) <span class="s12-z">0.60</span>\(\sigma_k\))', 'small', w=330)
            + '<rect x="386" y="16" width="358" height="318" rx="12" class="lab-boundary"/>'
            + text(565, 40, r'2. Convergence \(\mathrm{SE}(\hat{p}) \propto 1/\sqrt{N}\) & Bias \(f_A\)', 'accent', w=340)
            + text(565, 62, r'True \(p = \) <span class="s12-p">0.50</span> \(\;\to\;\) Postselected \(f_A = \) <span class="s12-fa">0.500</span>', 'small', w=340)
            + '<g class="s12-funnel" transform="translate(406, 78)"></g>'
            + text(565, 316, r'\(f_A = \frac{p\,\eta_A}{p\,\eta_A + (1-p)\,\eta_B}, \quad \mathrm{SE}(\hat{p}) = \) <span class="s12-se">0.050</span>', 'small', w=340)
        )
        return f'<svg class="qe-apparatus qe-scene-svg" viewBox="0 0 760 348" role="img" aria-labelledby="scene-1-2-title scene-1-2-desc">{s}</svg>'

    if name == 'section-1-3':
        s = (
            '<title id="scene-1-3-title">Detector-swap calibration protocol and explicit assumption ledger</title>'
            '<desc id="scene-1-3-desc">Animates swapping detectors D1 and D2 between ports A and B to cancel efficiency asymmetry and displays the four-item assumption ledger.</desc>'
            '<rect x="16" y="16" width="404" height="318" rx="12" class="lab-boundary"/>'
            + text(218, 40, '1. Port-Swap Calibration Protocol', 'accent', w=380)
            + text(218, 62, r'Cancels \(\eta_1 \neq \eta_2\) via \(\hat{p}_{\mathrm{cal}} = \frac{\sqrt{R_1 R_2}}{1 + \sqrt{R_1 R_2}}\)', 'small', w=380)
            + box(30, 126, 108, 'Source', r'true \(p\)')
            + line(138, 158, 206, 158)
            + splitter_cube(206, 158, 'Analyzer')
            + line(206, 158, 304, 104, 'ray')
            + line(206, 158, 304, 212, 'ray')
            + '<g class="s13-det-top">' + detector(304, 75, r'\(D_1\)', r'\(\eta_1 = \) <span class="s13-eta1">1.00</span>') + '</g>'
            + '<g class="s13-det-bot">' + detector(304, 183, r'\(D_2\)', r'\(\eta_2 = \) <span class="s13-eta2">0.60</span>') + '</g>'
            + '<circle class="s13-pulse" cx="138" cy="158" r="7" fill="var(--accent)" opacity="0"/>'
            + text(218, 272, r'Direct \(f_A^{(1)} = \) <span class="s13-f1">0.625</span> \(\;\mid\;\) Swapped \(f_A^{(2)} = \) <span class="s13-f2">0.375</span>', 'small', w=380)
            + text(218, 304, r'Calibrated \(\hat{p}_{\mathrm{cal}} = \) <span class="s13-pcal">0.500</span> (True \(p = \) <span class="s13-ptrue">0.500</span>)', 'accent', w=380)
            + '<rect x="434" y="16" width="310" height="318" rx="12" class="lab-boundary"/>'
            + text(589, 40, '2. Explicit Assumption Ledger', 'accent', w=290)
            + text(589, 62, 'Operational status of inference', 'small', w=290)
            + '<g class="s13-ledger" transform="translate(450, 78)">'
            + '<g class="node"><rect x="0" y="0" width="278" height="48" rx="8"/>' + text(139, 20, r'A1. Stationary preparation \(p\)', 'small', w=260) + text(139, 39, 'Verified across blocks', 'accent', w=260) + '</g>'
            + '<g class="node s13-card-eff"><rect x="0" y="58" width="278" height="48" rx="8"/>' + text(139, 78, r'A2. Efficiency balance \(\eta_1 / \eta_2\)', 'small', w=260) + '<text x="139" y="97" text-anchor="middle" class="small s13-status-eff">Uncalibrated asymmetry</text></g>'
            + '<g class="node"><rect x="0" y="116" width="278" height="48" rx="8"/>' + text(139, 136, r'A3. Fair sampling of misses', 'small', w=260) + text(139, 155, r'Raw bias \(\Delta p = \) <span class="s13-status-bias">+0.125</span>', 'small', w=260) + '</g>'
            + '<g class="node"><rect x="0" y="174" width="278" height="54" rx="8"/>' + text(139, 195, r'A4. Swap-calibrated estimator \(\hat{p}_{\mathrm{cal}}\)', 'small', w=260) + '<text x="139" y="216" text-anchor="middle" class="accent s13-status-cal">Recovers true p within SE</text></g>'
            + '</g>'
        )
        return f'<svg class="qe-apparatus qe-scene-svg" viewBox="0 0 760 348" role="img" aria-labelledby="scene-1-3-title scene-1-3-desc">{s}</svg>'

    # General section-N-k visual animation for Chapters 2..24
    parts = name.split('-')
    ch_num = int(parts[1])
    sec_idx = int(parts[2])
    kind = chapter['kind'] if chapter else 'mzi'
    sec = chapter['sections'][sec_idx - 1] if chapter else {'number': f'{ch_num}.{sec_idx}', 'title': name, 'subsections': ['', '', '']}
    f_law, f_audit = SECTION_FORMULAS.get(kind, (r'\(P(\theta)\)', r'\(V_{\mathrm{obs}} = \eta\,V\)'))

    if sec_idx == 1:
        # Section N.1: Animated Apparatus Stage with Live Sub-Stage Progression & Particle/Wave Propagation
        base = svg(kind, sec['title'])
        inner = base.split('>', 1)[1].rsplit('</svg>', 1)[0]
        # Replace diagram-title / diagram-desc IDs so they never collide with #explore
        inner = inner.replace('id="diagram-title"', f'id="{name}-title"').replace('id="diagram-desc"', f'id="{name}-desc"')
        sub1, sub2, sub3 = (sec.get('subsections') + ['', '', ''])[:3]
        overlay = (
            f'<g class="s-n1-overlay">'
            f'<circle class="s-n1-pulse-a" cx="60" cy="160" r="8" fill="var(--accent)" opacity="0"/>'
            f'<circle class="s-n1-pulse-b" cx="60" cy="160" r="7" fill="var(--lab-gold)" opacity="0"/>'
            f'<g transform="translate(16, 352)">'
            f'<rect x="0" y="0" width="688" height="54" rx="8" fill="var(--sidebar)" stroke="var(--line)"/>'
            + text(14, 21, rf'Section {sec["number"]} Live State:', 'accent', 'start', w=220)
            + f'<foreignObject x="195" y="3" width="480" height="26" class="svg-fo"><div xmlns="http://www.w3.org/1999/xhtml" class="svg-math small s-n1-formula" style="text-align:right">{f_law}</div></foreignObject>'
            + f'<text x="14" y="42" text-anchor="start" class="small s-n1-stage-text">Stage 1 ({sec["number"]}.1): {e(sub1[:58])}</text>'
            + f'<text x="674" y="42" text-anchor="end" class="small s-n1-readout">Ready</text>'
            f'</g></g>'
        )
        return f'<svg class="qe-apparatus qe-scene-svg" viewBox="0 0 720 416" role="img" aria-labelledby="{name}-title {name}-desc">{inner}{overlay}</svg>'

    if sec_idx == 2:
        # Section N.2: Dual-Panel Quantitative Mechanism (Phasor / Bloch / Wave Dial + Live Curve/Bar Sweep)
        s = (
            f'<title id="{name}-title">{e(sec["number"] + " " + sec["title"])}</title>'
            f'<desc id="{name}-desc">Interactive geometric state/phasor dial and quantitative prediction curve for {e(sec["title"])}.</desc>'
            '<rect x="16" y="16" width="304" height="318" rx="12" class="lab-boundary"/>'
            + text(168, 40, '1. State / Amplitude Geometry', 'accent', w=284)
            + '<g class="s-n2-dial" transform="translate(168, 178)">'
            + '<circle cx="0" cy="0" r="86" class="sphere-ring"/>'
            + '<ellipse cx="0" cy="0" rx="86" ry="28" class="sphere-ring"/>'
            + '<path d="M-96 0 H96 M0 -96 V96" class="axis"/>'
            + '<path class="s-n2-vec-a" d="M0 0 L60 0" stroke="var(--lab-blue)" stroke-width="3" fill="none"/>'
            + '<path class="s-n2-vec-b" d="M60 0 L60 -50" stroke="var(--lab-gold)" stroke-width="3" stroke-dasharray="5 3" fill="none"/>'
            + '<path class="s-n2-vec-tot" d="M0 0 L60 -50" stroke="var(--accent)" stroke-width="4" fill="none"/>'
            + '<circle class="s-n2-tip" cx="60" cy="-50" r="6" fill="var(--accent)"/>'
            + '</g>'
            + '<text x="168" y="292" text-anchor="middle" class="small s-n2-dial-label">Amplitude / Bloch projection</text>'
            + text(168, 318, r'Value \(= \) <span class="s-n2-val">0.500</span>', 'accent', w=280)
            + '<rect x="334" y="16" width="410" height="318" rx="12" class="lab-boundary"/>'
            + text(539, 40, f'2. Quantitative Law ({sec["number"]})', 'accent', w=390)
            + text(539, 64, f_law, 'small', w=395)
            + '<g class="s-n2-plot" transform="translate(354, 78)"></g>'
        )
        return f'<svg class="qe-apparatus qe-scene-svg" viewBox="0 0 760 348" role="img" aria-labelledby="{name}-title {name}-desc">{s}</svg>'

    # Section N.3: Experimental Audit (Ideal vs. Noisy/Imperfect Prediction + Section N.3 Assumption Ledger)
    sub1, sub2, sub3 = (sec.get('subsections') + ['', '', ''])[:3]
    s = (
        f'<title id="{name}-title">{e(sec["number"] + " " + sec["title"])}</title>'
        f'<desc id="{name}-desc">Compares ideal prediction against finite efficiency/coherence and audits the experimental assumptions for {e(sec["title"])}.</desc>'
        '<rect x="16" y="16" width="414" height="318" rx="12" class="lab-boundary"/>'
        + text(223, 40, '1. Ideal Model vs. Imperfect Apparatus', 'accent', w=394)
        + text(223, 64, f_audit, 'small', w=398)
        + '<g class="s-n3-plot" transform="translate(36, 78)"></g>'
        + '<rect x="444" y="16" width="300" height="318" rx="12" class="lab-boundary"/>'
        + text(594, 40, f'2. Audit Ledger ({sec["number"]})', 'accent', w=280)
        + text(594, 62, r'Fidelity / efficiency \(\eta = \) <span class="s-n3-eta">0.85</span>', 'small', w=280)
        + '<g transform="translate(458, 78)">'
        + f'<g class="node"><rect x="0" y="0" width="272" height="54" rx="8"/><text x="136" y="22" text-anchor="middle" class="small">{e(sec["number"])}.1 Check</text><text x="136" y="42" text-anchor="middle" class="small">{e(sub1[:38])}</text></g>'
        + f'<g class="node"><rect x="0" y="64" width="272" height="54" rx="8"/><text x="136" y="86" text-anchor="middle" class="small">{e(sec["number"])}.2 Check</text><text x="136" y="106" text-anchor="middle" class="small">{e(sub2[:38])}</text></g>'
        + f'<g class="node"><rect x="0" y="128" width="272" height="54" rx="8"/><text x="136" y="150" text-anchor="middle" class="small">{e(sec["number"])}.3 Scope</text><text x="136" y="170" text-anchor="middle" class="small">{e(sub3[:38])}</text></g>'
        + '<g class="node"><rect x="0" y="192" width="272" height="52" rx="8"/>'
        + text(136, 212, r'Ideal \(= \) <span class="s-n3-ideal">1.00</span> \(\;\mid\;\) Obs. \(= \) <span class="s-n3-obs">0.85</span>', 'small', w=260)
        + '<text x="136" y="234" text-anchor="middle" class="accent s-n3-verdict">Audit status: calibrated</text></g>'
        + '</g>'
    )
    return f'<svg class="qe-apparatus qe-scene-svg" viewBox="0 0 760 348" role="img" aria-labelledby="{name}-title {name}-desc">{s}</svg>'
