"""Accessible, static SVG apparatus drawings, enhanced by the lab controller."""
from html import escape as e


def text(x, y, label, cls='', anchor='middle'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{e(label)}</text>'


def line(x1, y1, x2, y2, cls='ray'):
    return f'<path d="M{x1} {y1} L{x2} {y2}" class="{cls}"/>'


def box(x, y, w, label, sub='', cls=''):
    return f'<g class="node {cls}"><rect x="{x}" y="{y}" width="{w}" height="64" rx="10"/>{text(x + w / 2, y + 27, label)}{text(x + w / 2, y + 48, sub, "small")}</g>'


def circle(x, y, r, cls=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>'


def detector(x, y, label, sub=''):
    return (
        f'<g class="node"><rect x="{x}" y="{y}" width="92" height="58" rx="8"/>'
        f'<path d="M{x} {y + 12} A18 18 0 0 1 {x} {y + 46}" class="splitter"/>'
        f'{text(x + 48, y + 26, label)}{text(x + 48, y + 45, sub, "small")}</g>'
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
    s += text(205, 36, '|0⟩') + text(205, 304, '|1⟩') + text(346, 170, '+x', 'small') + text(292, 96, '+y', 'small')
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
        s += splitter_cube(175, 160, 'BS1') + splitter_cube(505, 160, 'BS2')
        s += circle(42, 160, 11, 'source') + text(45, 195, 'Source', 'small')
        s += text(235, 92, 'upper arm', 'small') + text(235, 240, 'lower arm', 'small')
        s += detector(605, 48, 'D0', 'port 0') + detector(605, 226, 'D1', 'port 1')
        s += '<g class="node"><rect x="288" y="14" width="104" height="36" rx="6"/>' + text(340, 37, 'Phase φ', 'small') + '</g>'
        if kind == 'bomb':
            s += box(278, 223, 125, 'Absorber', 'opaque arm', 'absorber')
        if kind == 'eraser':
            s += box(258, 218, 164, 'Path marker', '|H⟩ / |V⟩ → |±⟩')
        if kind == 'delayed':
            s += text(505, 314, 'Late switch: keep or remove BS2', 'small')
        s += '<circle class="traveller" cx="42" cy="160" r="7"/>'
    elif kind in ('rabi', 'ramsey', 'tomography', 'teleport', 'sensing'):
        s += bloch_backdrop()
        if kind == 'teleport':
            s += (
                box(392, 26, 290, 'Alice: CNOT + H + measure', 'two classical bits (a, b)')
                + line(537, 90, 537, 134, 'axis')
                + box(392, 136, 290, 'Bob: pre-correction branch', 'conditional state X^b Z^a |ψ⟩')
                + line(537, 200, 537, 242, 'axis')
                + box(392, 244, 290, 'Feed-forward recovery', 'apply Z^a X^b → |ψ⟩')
            )
        elif kind == 'tomography':
            for y, label, sub in [
                (38, 'X-basis analyzer', 'measure P(+x) → rx'),
                (136, 'Y-basis analyzer', 'measure P(+y) → ry'),
                (234, 'Z-basis analyzer', 'measure P(+z) → rz'),
            ]:
                s += box(412, y, 265, label, sub)
        elif kind == 'ramsey':
            s += (
                box(402, 28, 275, 'π/2 pulse → free delay t', 'accumulate phase Δ·t')
                + line(539, 92, 539, 134, 'axis')
                + box(402, 136, 275, 'Optional midpoint π echo', 'refocus static detuning')
                + line(539, 200, 539, 242, 'axis')
                + box(402, 244, 275, 'Second π/2 + readout', 'envelope V(t) = exp(−t/T₂)')
            )
        elif kind == 'sensing':
            s += (
                box(402, 28, 275, 'Quadrature Ramsey probe', 'slope ∂P₀/∂δω = V t / 2')
                + line(539, 92, 539, 134, 'axis')
                + box(402, 136, 275, 'N repeated interrogations', 'shot noise 1/(2√N)')
                + line(539, 200, 539, 242, 'axis')
                + box(402, 244, 275, 'Frequency estimator', 'δω ≈ 1 / (V t √N)')
            )
        else:
            s += (
                box(402, 28, 275, 'Prepare |0⟩ state', 'calibrated initial population')
                + line(539, 92, 539, 134, 'axis')
                + box(402, 136, 275, 'Resonant drive pulse Ωt', 'unitary rotation exp(−iΩtX/2)')
                + line(539, 200, 539, 242, 'axis')
                + box(402, 244, 275, 'Projective population readout', 'P₁ = sin²(Ωt/2)')
            )
    elif kind in ('cat', 'friend'):
        s += box(15, 130, 135, 'Prepare |+⟩', 'trigger qubit') + line(150, 162, 275, 92) + line(150, 162, 275, 246)
        s += '<rect x="248" y="18" width="276" height="292" rx="16" class="lab-boundary"/>'
        s += (
            text(386, 45, 'Isolated laboratory (unitary coupling)', 'small')
            + box(272, 60, 228, '|0, record 0⟩', 'branch weight 1/2')
            + box(272, 214, 228, '|1, record 1⟩', 'branch weight 1/2')
        )
        s += '<path d="M386 124 V214" class="coherence-link"/>' + text(448, 173, 'coherence γ', 'accent')
        s += line(524, 162, 568, 162) + box(570, 130, 135, 'Superobserver', 'record / interfere')
        if kind == 'cat':
            s += text(386, 335, 'Macroscopic pointer branches with controllable decoherence.', 'small')
        else:
            s += text(386, 335, 'Friend memory register probed in record or interference basis.', 'small')
    elif kind == 'extended':
        for y, label, sign in [(28, '|h, d⟩', '+'), (128, '|t, d⟩', '−'), (228, '|t, u⟩', '+')]:
            s += (
                box(22, y, 152, label, 'state weight 1/√3')
                + line(174, y + 32, 338, y + 32)
                + text(256, y + 20, f'{sign}1/√12', 'accent')
                + line(338, y + 32, 456, 162)
            )
        s += (
            box(456, 128, 240, 'Outside |ok, ok⟩', 'sum amplitudes, then square')
            + text(576, 236, '(+1 − 1 + 1)² / 12 = 1/12', 'accent')
            + text(576, 266, 'Destructive cancellation of two of three branches', 'small')
        )
    elif kind == 'ghz':
        s += box(255, 18, 210, '3-Qubit GHZ Source', '(|000⟩ + |111⟩)/√2')
        for x, label, sub in [
            (20, 'Alice (qubit 1)', 'measure X₁ or Y₁'),
            (265, 'Bob (qubit 2)', 'measure X₂ or Y₂'),
            (510, 'Charlie (qubit 3)', 'measure X₃ or Y₃'),
        ]:
            s += line(360, 82, x + 95, 162) + box(x, 162, 190, label, sub)
        s += (
            text(360, 282, 'XXX = +1    XYY = −1    YXY = −1    YYX = −1', 'accent')
            + text(360, 316, 'Product of the last three parity constraints contradicts XXX = +1.', 'small')
        )
    elif kind == 'bell':
        s += (
            box(262, 126, 196, 'Entangled Singlet Source', '(|01⟩ − |10⟩)/√2')
            + line(262, 158, 175, 158)
            + line(458, 158, 545, 158)
        )
        s += (
            box(18, 126, 157, 'Alice Station', 'settings a₀=0°, a₁=90°')
            + box(545, 126, 157, 'Bob Station', 'settings b₀=θ, b₁=−θ')
            + text(360, 52, 'Spacelike separated setting choices · outcomes ±1', 'accent')
            + text(360, 268, 'CHSH combination: S = E₀₀ + E₀₁ + E₁₀ − E₁₁  (|S| ≤ 2 locally)', 'small')
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
            + box(15, 25, 172, 'Input Photon A', 'mode f (reference)')
            + box(15, 245, 172, 'Input Photon B', 'mode g (delay δ)')
            + detector(565, 30, 'Det 0', 'port c')
            + detector(565, 246, 'Det 1', 'port d')
        )
        s += (
            '<g class="packet-a"><ellipse cx="245" cy="127" rx="38" ry="12" class="packet"/></g>'
            '<g class="packet-b"><ellipse cx="245" cy="213" rx="38" ry="12" class="packet secondary"/></g>'
            + text(360, 326, 'Both-reflect and both-transmit amplitudes cancel at δ = 0.', 'small')
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
            + text(240, 336, 'Double slit (spacing d)', 'small')
            + text(630, 336, 'Detector screen', 'small')
            + text(435, 22, 'Superposed path amplitudes ψ_L(x) + ψ_R(x)', 'small')
        )
    elif kind == 'recoil':
        s += (
            box(22, 135, 152, 'Path superpos.', '(|L⟩ + |R⟩)/√2')
            + line(174, 167, 298, 167)
            + box(298, 135, 184, 'Movable slit pointer', 'states |d_L⟩, |d_R⟩')
            + line(482, 167, 580, 167)
            + box(580, 135, 118, 'Screen', 'V = |⟨d_R|d_L⟩|')
        )
        s += (
            '<g class="pointer-waves"></g>'
            + text(390, 36, 'Pointer wave packets overlap γ = exp(−Δ² / 8σ²)', 'accent')
            + text(390, 318, 'Duality relation for pure balanced states: D² + V² = 1', 'small')
        )
    elif kind == 'tunnel':
        s += (
            '<path d="M35 250H680" class="axis"/>'
            '<rect x="300" y="60" width="120" height="190" class="potential"/>'
            '<path d="M35 155H680" class="energy-line"/>'
        )
        s += (
            text(360, 44, 'Barrier height V₀')
            + text(52, 144, 'Particle energy E = V₀/2', 'small', 'start')
            + text(360, 278, 'Barrier width a (decay κ)', 'small')
            + text(145, 314, 'Incident + reflected wave', 'small')
            + text(575, 314, 'Transmitted wave (energy E)', 'small')
            + '<path class="tunnel-wave" d="M40 200H680"/>'
        )
    elif kind == 'polarization':
        s += line(35, 167, 680, 167)
        for x, angle, label, sub in [
            (150, 0, 'Filter 1: H (0°)', 'prepares |H⟩'),
            (360, 45, 'Filter 2: θ', 'projects onto |θ⟩'),
            (565, 90, 'Filter 3: V (90°)', 'P = ¼ sin²(2θ)'),
        ]:
            s += (
                f'<ellipse cx="{x}" cy="167" rx="43" ry="86" class="filter"/>'
                f'<g transform="rotate({angle} {x} 167)"'
                + (' class="middle-axis"' if x == 360 else '')
                + f'><path d="M{x} 96V238" class="filter-axis"/></g>'
                + text(x, 280, label, 'small')
                + text(x, 300, sub, 'small')
            )
    elif kind == 'spin':
        s += (
            box(18, 138, 145, 'Oven + Slit', 'prepares |+z⟩')
            + line(163, 170, 278, 170)
            + box(278, 138, 152, 'SG Magnet (θ)', 'gradient ∂B/∂n')
            + line(430, 152, 575, 72)
            + line(430, 188, 575, 268)
            + detector(575, 38, '+θ port', 'cos²(θ/2)')
            + detector(575, 236, '−θ port', 'sin²(θ/2)')
            + text(355, 314, 'Quantized deflection into two orthogonal spin channels.', 'small')
        )
    elif kind == 'energy':
        s += (
            box(18, 135, 158, 'Monochromatic', 'photons E = hf')
            + line(176, 167, 318, 167)
            + '<rect x="320" y="58" width="76" height="224" rx="6" class="potential"/>'
            + text(358, 40, 'Photocathode', 'small')
            + text(358, 308, 'Work function Φ = 2 eV', 'small')
            + line(396, 167, 542, 167)
            + box(542, 135, 160, 'Retarding grid', 'stopping bias Vs')
            + text(530, 82, 'K_max = hf − Φ = e V_s', 'accent')
        )
    elif kind == 'photons':
        s += (
            box(15, 137, 160, 'Light Source', 'select g⁽²⁾(τ) model')
            + line(175, 169, 345, 169)
            + line(345, 169, 555, 65)
            + line(345, 169, 555, 262)
            + splitter_cube(345, 169, '50:50 BS')
            + detector(555, 32, 'Det A', 'start t')
            + detector(555, 232, 'Det B', 'stop t+τ')
            + '<path d="M647 61 H688 V261 H647" class="axis"/>'
            + text(360, 324, 'Hanbury Brown–Twiss coincidence timer: g⁽²⁾(τ) across delay τ', 'accent')
        )
    elif kind == 'capstone':
        for x, l, sub in [
            (15, '1. Phase Scan', '16 phases × 200 trials'),
            (255, '2. Moment Fit', 'estimate V ± SE'),
            (495, '3. Audit Report', 'residuals & scope'),
        ]:
            s += box(x, 120, 205, l, sub)
        s += (
            line(220, 152, 255, 152)
            + line(460, 152, 495, 152)
            + text(360, 55, 'Reproducible interference audit workflow', 'accent')
            + text(360, 272, 'Export seeded CSV → verify estimator → inspect phase residuals.', 'small')
        )
    else:
        s += (
            box(18, 135, 155, 'Source', 'probability p of A')
            + line(173, 167, 285, 167)
            + box(285, 135, 155, '2-Outcome Det.', 'efficiencies η_A, η_B')
            + line(440, 167, 552, 167)
            + box(552, 135, 150, 'Counter Ledger', 'k_A, k_B in N trials')
            + text(360, 62, 'p̂ = k_A / N   with   SE ≈ √(p̂(1 − p̂) / N)', 'accent')
        )
    return f'<svg class="qe-apparatus" viewBox="0 0 720 350" role="img" aria-labelledby="diagram-title diagram-desc"><title id="diagram-title">{e(title)}</title><desc id="diagram-desc">{e(desc)}</desc>{s}</svg>'
