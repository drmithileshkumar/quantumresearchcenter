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


def scene_svg(name):
    """Render an inline section visual animation apparatus SVG with MathJax notation."""
    if name != 'section-1-1':
        raise ValueError(f'Unknown scene: {name}')
    s = (
        '<title id="scene-1-1-title">Animated two-outcome quantum experiment: preparation, transformation, and measurement</title>'
        '<desc id="scene-1-1-desc">Interactive schematic of a triggered single-quantum source, two-channel analyzer, detectors with efficiencies eta_A and eta_B, digital counter ledger, and trial-by-trial event tape.</desc>'
        # Stage 1: Preparation
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
        # Stage 2: Transformation
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
        # Stage 3: Measurement & Ledger
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
        # Animated wavepacket pulses
        + '<circle class="scene-packet-in" cx="134" cy="140" r="8" fill="var(--accent)" opacity="0"/>'
        + '<circle class="scene-packet-a" cx="326" cy="140" r="7" fill="var(--lab-blue)" opacity="0"/>'
        + '<circle class="scene-packet-b" cx="326" cy="140" r="7" fill="var(--lab-gold)" opacity="0"/>'
        # Bottom strip: Trial-by-trial event tape & convergence bar
        + '<g class="scene-tape" transform="translate(16, 282)">'
        + '<rect x="0" y="0" width="728" height="72" rx="10" fill="var(--sidebar)" stroke="var(--line)"/>'
        + '<text x="14" y="23" text-anchor="start" class="small">Trial log (seeded sequence):</text>'
        + '<text x="714" y="23" text-anchor="end" class="small scene-seed-label">Seed 2026 · deterministic replay</text>'
        + '<g class="scene-tape-cells" transform="translate(14, 32)"></g>'
        + '</g>'
    )
    return f'<svg class="qe-apparatus qe-scene-svg" viewBox="0 0 760 366" role="img" aria-labelledby="scene-1-1-title scene-1-1-desc">{s}</svg>'
