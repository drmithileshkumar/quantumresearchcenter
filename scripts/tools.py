"""Render the Tools section: the catalogue of interactive models and the single-qubit Bloch sphere.

The geometry of the sphere is computed here so the page is a complete drawing without JavaScript;
`tools/single-qubit.js` re-projects the state vector with the camera basis emitted on the <svg>.
"""
from html import escape
import cmath
import json
import math
import os
import re
from pathlib import Path

CENTER = 200.0
RADIUS = 148.0
# Camera azimuth and elevation in degrees; the same basis drives the static drawing and the drag
# mapping in single-qubit.js, which reads it from the svg's data-basis attribute.
AZIMUTH, ELEVATION = 32.0, 17.0

AXES = (((1.0, 0.0, 0.0), '|+⟩'), ((-1.0, 0.0, 0.0), '|−⟩'), ((0.0, 1.0, 0.0), '|+i⟩'),
        ((0.0, -1.0, 0.0), '|−i⟩'), ((0.0, 0.0, 1.0), '|0⟩'), ((0.0, 0.0, -1.0), '|1⟩'))

PRESETS = (('|0⟩', 0, 0), ('|1⟩', 180, 0), ('|+⟩', 90, 0), ('|−⟩', 90, 180),
           ('|+i⟩', 90, 90), ('|−i⟩', 90, 270))

GATES = (('X', 'Bit flip'), ('Y', 'Bit and phase flip'), ('Z', 'Phase flip'),
         ('H', 'Hadamard'), ('S', 'Phase by π/2'), ('T', 'Phase by π/4'))

# The arbitrary gate U = e^{iγ}(cos(θ/2) I − i sin(θ/2) n·σ). The axis is given by its polar and
# azimuth angles so it is always a unit vector, and γ is the global phase the sphere cannot see.
AXIS_PRESETS = (('x', 90, 0), ('y', 90, 90), ('z', 0, 0), ('x+z', 45, 0))
AXIS_ANGLES = (90, 0)
ROTATION_ANGLE, ROTATION_PHASE = 90, 0
ZERO = 5e-4


def rotation_axis(polar_deg, azimuth_deg):
    """The unit vector n̂ at a polar angle and azimuth, both in degrees."""
    polar, azimuth = math.radians(polar_deg), math.radians(azimuth_deg)
    return (math.sin(polar) * math.cos(azimuth), math.sin(polar) * math.sin(azimuth), math.cos(polar))


def rotation_matrix(axis, theta_deg, gamma_deg):
    """U = e^{iγ}(cos(θ/2) I − i sin(θ/2)(n_x X + n_y Y + n_z Z)) for the unit axis n̂ = axis."""
    half, phase = math.radians(theta_deg) / 2, cmath.exp(1j * math.radians(gamma_deg))
    cos, sin = math.cos(half) * phase, math.sin(half) * phase
    nx, ny, nz = axis
    return ((cos - 1j * nz * sin, -ny * sin - 1j * nx * sin),
            (ny * sin - 1j * nx * sin, cos + 1j * nz * sin))


def complex_text(value, digits=3):
    """A complex number the way single-qubit.js writes it, so static and live readouts agree."""
    def fixed(part):
        part = 0.0 if abs(part) < ZERO else part
        return ('−' if part < 0 else '') + f'{abs(part):.{digits}f}'
    real, imag = value.real, value.imag
    if abs(imag) < ZERO:
        return fixed(real)
    if abs(real) < ZERO:
        return fixed(imag) + 'i'
    return fixed(real) + (' − ' if imag < 0 else ' + ') + fixed(abs(imag)) + 'i'


def camera_basis():
    """Right, up and forward unit vectors for an orthographic camera looking down at the sphere."""
    azimuth, elevation = math.radians(AZIMUTH), math.radians(ELEVATION)
    forward = (-math.cos(elevation) * math.sin(azimuth),
               math.cos(elevation) * math.cos(azimuth),
               -math.sin(elevation))
    length = math.hypot(forward[1], -forward[0])
    right = (forward[1] / length, -forward[0] / length, 0.0)
    up = (right[1] * forward[2] - right[2] * forward[1],
          right[2] * forward[0] - right[0] * forward[2],
          right[0] * forward[1] - right[1] * forward[0])
    return right, up, forward


RIGHT, UP, FORWARD = camera_basis()


ORIGIN = (CENTER, CENTER)


def project(point, center=ORIGIN, radius=RADIUS):
    x, y, z = point
    return (center[0] + radius * (x * RIGHT[0] + y * RIGHT[1] + z * RIGHT[2]),
            center[1] - radius * (x * UP[0] + y * UP[1] + z * UP[2]))


def facing(point):
    """True when a point on the sphere is on the hemisphere turned towards the camera."""
    return sum(a * b for a, b in zip(point, FORWARD)) < 0


def arcs(point_at, steps=180, center=ORIGIN, radius=RADIUS):
    """Split a closed 3D curve into the runs that are in front of, or behind, the sphere."""
    samples = []
    for index in range(steps):
        point = point_at(2 * math.pi * index / steps)
        samples.append((project(point, center, radius), facing(point)))
    start = next((index for index in range(steps) if samples[index][1] != samples[index - 1][1]), 0)
    ordered = samples[start:] + samples[:start]
    runs = []
    for index, sample in enumerate(ordered):
        if runs and runs[-1][0] == sample[1]:
            runs[-1][1].append(index)
        else:
            runs.append([sample[1], [index]])
    total = len(ordered)
    paths = []
    for visible, indices in runs:
        points = [ordered[index % total][0] for index in range(indices[0] - 1, indices[-1] + 2)]
        paths.append((visible, 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in points)))
    return paths


def axis_label(point, text, center=ORIGIN, radius=RADIUS):
    px, py = project(point, center, radius)
    dx, dy = px - center[0], py - center[1]
    distance = math.hypot(dx, dy) or 1.0
    anchor = 'middle'
    if dx / distance > 0.35:
        anchor = 'start'
    elif dx / distance < -0.35:
        anchor = 'end'
    return (f'<text class="bloch-axis-label" x="{center[0] + dx * 1.15:.1f}"'
            f' y="{center[1] + dy * 1.15:.1f}" text-anchor="{anchor}" dy="4">{text}</text>')


def rotation_axis_geometry(point, center=ORIGIN, radius=RADIUS, prefix='bloch'):
    """The diameter through n̂, drawn under the state vector so the arrow always stays legible."""
    tip = project(point, center, radius)
    tail = project((-point[0], -point[1], -point[2]), center, radius)
    return (f'<line class="bloch-rotation-axis" id="{prefix}-naxis" x1="{tail[0]:.1f}" y1="{tail[1]:.1f}"'
            f' x2="{tip[0]:.1f}" y2="{tip[1]:.1f}"/>')


def rotation_axis_marker(point, center=ORIGIN, radius=RADIUS, prefix='bloch', angles=AXIS_ANGLES):
    """The ring, label and grab target at the tip of n̂, drawn above the state vector."""
    tip = project(point, center, radius)
    return (f'<circle class="bloch-rotation-pole" id="{prefix}-npole" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="5"/>'
            f'{rotation_axis_label(tip, center, prefix)}'
            + angle_label(point, f'θₙ {angles[0]}° · φₙ {angles[1]}°', center, radius, prefix,
                          'axis-angles', 'bloch-axis-angle', -20, 29)
            + f'{rotation_axis_handle(point, center, radius, prefix)}')


def rotation_axis_label(tip, center=ORIGIN, prefix='bloch'):
    """The n̂ label, set just beyond the tip and to one side so it never lands on a basis-state label.

    The projection of n̂ is foreshortened: an axis pointing at the camera projects close to the
    centre, so the offset is measured from the tip rather than from the centre.
    """
    dx, dy = tip[0] - center[0], tip[1] - center[1]
    distance = math.hypot(dx, dy)
    ux, uy = (dx / distance, dy / distance) if distance > 1 else (0.0, -1.0)
    x = tip[0] + ux * 12 + uy * 20
    y = tip[1] + uy * 12 - ux * 20
    return (f'<text class="bloch-rotation-label" id="{prefix}-nlabel" x="{x:.1f}" y="{y:.1f}"'
            f' text-anchor="middle" dy="4">n̂</text>')


def angle_label(point, text, center=ORIGIN, radius=RADIUS, prefix='bloch', ident='state-angles',
                cls='bloch-angle', offset=16, half=26):
    """A faint θ and φ label beside a vector's tip, clear of its shaft and inside the drawing.

    `offset` is the sideways distance from the tip; its sign picks the side. `half` is half the
    estimated text width, used to keep the label inside the 400 × 400 view box.
    """
    x, y = project(point, center, radius)
    dx, dy = x - center[0], y - center[1]
    distance = math.hypot(dx, dy)
    if distance < 12:
        # The vector points at the camera: it projects onto the centre and has no screen direction.
        lx, ly, anchor = center[0] - 16, center[1] + 18, 'end'
    else:
        side = dy * offset / distance
        lx = x + side
        ly = y - dx * offset / distance
        anchor = 'middle' if abs(side) < 2 else ('start' if side > 0 else 'end')
    if anchor == 'start':
        lx = min(lx, 396 - 2 * half)
    elif anchor == 'end':
        lx = max(lx, 4 + 2 * half)
    else:
        lx = min(max(lx, 4 + half), 396 - half)
    return (f'<text class="{cls}" id="{prefix}-{ident}" x="{lx:.1f}" y="{ly:.1f}"'
            f' text-anchor="{anchor}" dy="4">{text}</text>')


def rotation_axis_handle(point, center=ORIGIN, radius=RADIUS, prefix='bloch'):
    """A wider invisible target over the tip of n̂, drawn last so the pointer finds it first."""
    tip = project(point, center, radius)
    return (f'<circle class="bloch-rotation-handle" id="{prefix}-nhandle" cx="{tip[0]:.1f}"'
            f' cy="{tip[1]:.1f}" r="18"/>')


def state_geometry(theta_deg, phi_deg, center=ORIGIN, radius=RADIUS, prefix='bloch'):
    """The state vector and its two dashed guides, as static SVG for the no-JavaScript drawing."""
    theta, phi = math.radians(theta_deg), math.radians(phi_deg)
    tip_3d = (math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta))
    tip = project(tip_3d, center, radius)
    foot = project((tip_3d[0], tip_3d[1], 0.0), center, radius)
    origin = project((0.0, 0.0, 0.0), center, radius)
    return (f'<line class="bloch-guide" id="{prefix}-radial" x1="{origin[0]:.1f}" y1="{origin[1]:.1f}"'
            f' x2="{foot[0]:.1f}" y2="{foot[1]:.1f}"/>'
            f'<line class="bloch-guide" id="{prefix}-drop" x1="{tip[0]:.1f}" y1="{tip[1]:.1f}"'
            f' x2="{foot[0]:.1f}" y2="{foot[1]:.1f}"/>'
            f'<line class="bloch-vector" id="{prefix}-arrow" x1="{origin[0]:.1f}" y1="{origin[1]:.1f}"'
            f' x2="{tip[0]:.1f}" y2="{tip[1]:.1f}"/>'
            f'<circle class="bloch-tip" id="{prefix}-tip" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="6"/>'
            + angle_label(tip_3d, f'θ {theta_deg:.0f}° · φ {phi_deg:.0f}°', center, radius, prefix))


def sphere_grid(center=ORIGIN, radius=RADIUS):
    grid = []
    for visible, path in arcs(lambda t: (math.cos(t), math.sin(t), 0.0), center=center, radius=radius):
        grid.append(f'<path class="bloch-equator" d="{path}"/>' if visible
                    else f'<path class="bloch-equator is-behind" d="{path}"/>')
    for longitude in (0.0, math.pi / 2):
        for visible, path in arcs(lambda t, p=longitude: (math.sin(t) * math.cos(p),
                                                          math.sin(t) * math.sin(p), math.cos(t)),
                                  center=center, radius=radius):
            grid.append(f'<path class="bloch-meridian" d="{path}"/>' if visible
                        else f'<path class="bloch-meridian is-behind" d="{path}"/>')
    return grid


def sphere_axes(center=ORIGIN, radius=RADIUS, labels=AXES):
    axes = ''.join(f'<line class="bloch-axis" x1="{center[0]:.1f}" y1="{center[1]:.1f}"'
                   f' x2="{project(axis, center, radius)[0]:.1f}"'
                   f' y2="{project(axis, center, radius)[1]:.1f}"/>' for axis, _ in labels)
    return axes + ''.join(axis_label(axis, label, center, radius) for axis, label in labels)


def sphere_svg(title, desc, prefix='bloch', center=ORIGIN, radius=RADIUS,
               view_box='0 0 400 400', cls='bloch', extra='', labels=AXES):
    """One Bloch sphere. The camera basis is emitted on the element so the script reuses it."""
    basis = ','.join(f'{value:.6f}' for value in (*RIGHT, *UP))
    return (f'<svg class="{cls}" id="{prefix}" viewBox="{view_box}" role="img"'
            f' aria-labelledby="{prefix}-title {prefix}-desc" data-basis="{basis}"{extra}>'
            f'<title id="{prefix}-title">{title}</title>'
            f'<desc id="{prefix}-desc">{desc}</desc>'
            f'<circle class="bloch-surface" cx="{center[0]:.1f}" cy="{center[1]:.1f}" r="{radius:.1f}"/>'
            f'<g class="bloch-grid">{"".join(sphere_grid(center, radius))}</g>'
            f'<path class="bloch-rotation-orbit" id="{prefix}-orbit" d=""/>'
            f'<path class="bloch-rotation-cone" id="{prefix}-cone" d=""/>'
            f'<path class="bloch-rotation-arc" id="{prefix}-arc" d=""/>'
            f'<g class="bloch-axes">{sphere_axes(center, radius, labels)}</g>'
            f'{rotation_axis_geometry(rotation_axis(*AXIS_ANGLES), center, radius, prefix)}'
            f'{state_geometry(0, 0, center, radius, prefix)}'
            f'<circle class="bloch-origin" cx="{center[0]:.1f}" cy="{center[1]:.1f}" r="2.5"/>'
            f'{rotation_axis_marker(rotation_axis(*AXIS_ANGLES), center, radius, prefix)}'
            '</svg>')


def bloch_svg():
    axis = rotation_axis(*AXIS_ANGLES)
    return sphere_svg('Bloch sphere for the current qubit state',
                      'The Bloch sphere with the state vector pointing at the north pole, θ = 0°, φ = 0°.'
                      ' The probability of outcome 0 is 1.000 and of outcome 1 is 0.000. Faint labels beside'
                      ' the arrows give their θ and φ. The green dashed diameter marks the rotation axis n̂, now at ('
                      + ', '.join(f'{value:.3f}' for value in axis) + '); drag its handle to aim it.')


# Two-qubit explorer: every vector of the state in one complex plane. The four amplitudes are the
# arrows; the concurrence needle is their paired product difference, so the phases stay visible.

PHASOR_CENTER = 220.0
PHASOR_RADIUS = 156.0
PHASOR_LABELS = (('00', '|00⟩', 'Φ⁺'), ('01', '|01⟩', 'Φ⁻'),
                 ('10', '|10⟩', 'Ψ⁺'), ('11', '|11⟩', 'Ψ⁻'))

PAULI = {'I': ((1, 0), (0, 1)), 'X': ((0, 1), (1, 0)),
         'Y': ((0, -1j), (1j, 0)), 'Z': ((1, 0), (0, -1))}

TWO_PRESETS = (('00', '|00⟩'), ('11', '|11⟩'), ('++', '|++⟩'), ('phi+', 'Φ<sup>+</sup>'),
               ('phi-', 'Φ<sup>−</sup>'), ('psi+', 'Ψ<sup>+</sup>'), ('psi-', 'Ψ<sup>−</sup>'),
               ('partial', 'Partly entangled'))


def two_qubit_observables(state):
    """The 4x4 Pauli table <σ_μ ⊗ σ_ν> and the pure-state invariants of a two-qubit state."""
    table = [[sum((state[2 * a + b].conjugate() * PAULI[mu][a][a2] * PAULI[nu][b][b2]
                   * state[2 * a2 + b2]).real
                  for a in (0, 1) for b in (0, 1) for a2 in (0, 1) for b2 in (0, 1))
              for nu in 'IXYZ'] for mu in 'IXYZ']
    concurrence = concurrence_of(state)
    spread = math.sqrt(max(0.0, 1 - concurrence ** 2))
    return table, concurrence, math.sqrt((1 + spread) / 2), math.sqrt((1 - spread) / 2)


def concurrence_of(state):
    return 2 * abs(state[0] * state[3] - state[1] * state[2])


def signed(value):
    """Three decimals with a true minus sign; a zero never carries a sign."""
    if abs(value) < 5e-4:
        return '0.000'
    return ('−' if value < 0 else '+') + f'{abs(value):.3f}'


def phasor_tip(magnitude, phase_deg):
    rad = math.radians(phase_deg)
    return (PHASOR_CENTER + PHASOR_RADIUS * magnitude * math.cos(rad),
            PHASOR_CENTER - PHASOR_RADIUS * magnitude * math.sin(rad))


def phasor_arrow(prefix, magnitude, phase_deg, label, marker, cls='ph-arrow'):
    """One arrow from the origin; its label sits on a fixed ring outside the rim so labels never
    land on another arrow's shaft."""
    x, y = phasor_tip(magnitude, phase_deg)
    lx, ly = phasor_tip((PHASOR_RADIUS + 20) / PHASOR_RADIUS, phase_deg)
    dx = math.cos(math.radians(phase_deg))
    anchor = ' text-anchor="end"' if dx < -0.01 else ''
    text = (f'<text id="{prefix}-label" class="ph-label" x="{lx:.1f}" y="{ly:.1f}" dy="4"{anchor}>'
            f'{label}</text>' if label else '')
    return (f'<line id="{prefix}" class="{cls}" x1="{PHASOR_CENTER:.1f}" y1="{PHASOR_CENTER:.1f}"'
            f' x2="{x:.1f}" y2="{y:.1f}" marker-end="url(#{marker})"/>' + text)


def phasor_svg(state, basis_labels=PHASOR_LABELS):
    """The static drawing of the complex plane holding every vector of the state."""
    rings = ''.join(
        f'<circle class="{"ph-ring is-inner" if factor < 1 else "ph-ring"}" cx="{PHASOR_CENTER:.1f}"'
        f' cy="{PHASOR_CENTER:.1f}" r="{PHASOR_RADIUS * factor:.1f}"/>' for factor in (1.0, 0.5))
    rim = PHASOR_RADIUS * 0.82
    ticks = (f'<text class="ph-tick" x="{PHASOR_CENTER + rim:.0f}" y="{PHASOR_CENTER + 16:.0f}"'
             ' text-anchor="middle">0°</text>'
             f'<text class="ph-tick" x="{PHASOR_CENTER + 12:.0f}" y="{PHASOR_CENTER - rim + 4:.0f}">90°</text>'
             f'<text class="ph-tick" x="{PHASOR_CENTER - rim:.0f}" y="{PHASOR_CENTER + 16:.0f}"'
             ' text-anchor="middle">180°</text>'
             f'<text class="ph-tick" x="{PHASOR_CENTER + 12:.0f}" y="{PHASOR_CENTER + rim + 4:.0f}">270°</text>')
    vectors = ''
    for index, (key, label, _) in enumerate(basis_labels):
        amplitude = state[index]
        magnitude = abs(amplitude)
        phase = math.degrees(cmath.phase(amplitude)) % 360 if magnitude > 1e-9 else 0.0
        hidden = ' is-empty' if magnitude <= 1e-9 else ''
        x0, y0 = phasor_tip(magnitude, phase)
        vectors += (f'<g class="ph-vec{hidden}" data-index="{index}" id="ph-group-{key}">'
                    f'<line class="ph-hit" x1="{PHASOR_CENTER:.1f}" y1="{PHASOR_CENTER:.1f}"'
                    f' x2="{x0:.1f}" y2="{y0:.1f}"/>'
                    + phasor_arrow(f'ph-vec-{key}', magnitude, phase, label, f'ph-head-{index}')
                    + '</g>')
    needle = 2 * (state[0] * state[3] - state[1] * state[2])
    needle_magnitude = abs(needle)
    needle_phase = math.degrees(cmath.phase(needle)) % 360 if needle_magnitude > 1e-9 else 0.0
    needle_hidden = ' is-empty' if needle_magnitude <= 1e-9 else ''
    pairing = ''
    products = (2 * state[0] * state[3], 2 * state[1] * state[2])
    for key, product in zip(('p1', 'p2'), products):
        magnitude = abs(product)
        phase = math.degrees(cmath.phase(product)) % 360 if magnitude > 1e-9 else 0.0
        pairing += phasor_arrow(f'ph-{key}', magnitude, phase, '', f'ph-head-{key}',
                                cls='ph-arrow is-pairing')
    markers = ''.join(
        f'<marker id="ph-head-{name}" viewBox="0 0 10 10" refX="7.5" refY="5" markerWidth="4.6"'
        f' markerHeight="4.6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ph-head-{name}"/>'
        f'</marker>' for name in ('0', '1', '2', '3', 'p1', 'p2', 'needle'))
    return (f'<svg class="phasor" id="phasor" viewBox="0 0 440 440" role="group"'
            f' aria-labelledby="phasor-title phasor-desc">'
            '<title id="phasor-title">Every vector of the two-qubit state in one complex plane</title>'
            '<desc id="phasor-desc">Four arrows, one per basis amplitude: length is the magnitude and the'
            ' angle is the phase. Only |00⟩ is present, with magnitude 1.000 at phase 0°, so the concurrence'
            ' needle has zero length.</desc>'
            f'<defs>{markers}</defs>'
            f'<g class="ph-grid">{rings}'
            f'<line class="ph-axis" x1="48" y1="{PHASOR_CENTER:.1f}" x2="392" y2="{PHASOR_CENTER:.1f}"/>'
            f'<line class="ph-axis" x1="{PHASOR_CENTER:.1f}" y1="48" x2="{PHASOR_CENTER:.1f}" y2="392"/>'
            f'{ticks}</g>'
            f'<g class="ph-pairing is-empty" id="ph-pairing">{pairing}</g>'
            f'<g class="ph-needle" id="ph-needle-group"{needle_hidden}>'
            f'<line class="ph-arrow is-halo" id="ph-needle-halo" x1="{PHASOR_CENTER:.1f}"'
            f' y1="{PHASOR_CENTER:.1f}" x2="{PHASOR_CENTER:.1f}" y2="{PHASOR_CENTER:.1f}"/>'
            + phasor_arrow('ph-needle', needle_magnitude, needle_phase, 'C', 'ph-head-needle')
            + '</g>'
            '<g class="ph-vectors">' + vectors + '</g>'
            f'<circle class="ph-origin" cx="{PHASOR_CENTER:.1f}" cy="{PHASOR_CENTER:.1f}" r="3"/>'
            '</svg>')


def render_two_qubit(root, shell):
    e = escape
    table, concurrence, lam_plus, lam_minus = two_qubit_observables([1, 0, 0, 0])
    rows = ''
    for index, (key, label, _) in enumerate(PHASOR_LABELS):
        rows += (f'<tr data-index="{index}"><th scope="row" id="amp-name-{key}">{label}</th>'
                 f'<td id="amp-mag-{key}">1.000</td><td id="amp-phase-{key}">0°</td>'
                 f'<td id="amp-prob-{key}">1.000</td></tr>')
    gates = ''.join(f'<button type="button" data-gate-a="{name}" title="{hint} on qubit A">{name}</button>'
                    for name, hint in GATES)
    gates_b = ''.join(f'<button type="button" data-gate-b="{name}" title="{hint} on qubit B">{name}</button>'
                      for name, hint in GATES)

    body = (
        '<header class="editorial-intro compact qubit-intro"><p class="eyebrow">Tools / Two-qubit state</p>'
        '<h1>The state is<br><span>four arrows.</span></h1>'
        '<p>A two-qubit state is four complex numbers, and a complex number is a vector. So the whole state fits'
        ' in one ordinary plane: four arrows whose lengths are the magnitudes and whose angles are the phases.'
        ' Gates turn and add those arrows; the fifth, heavy arrow measures how entangled the pair is.</p>'
        '</header>'

        '<div class="two-summary"><div class="two-ket-block"><p class="qubit-kicker">Current state</p>'
        '<p class="qubit-ket" id="state-ket">|00⟩</p></div><dl class="two-invariants">'
        f'<div><dt>Concurrence C</dt><dd id="inv-concurrence">{concurrence:.3f}</dd></div>'
        f'<div><dt>Needle angle</dt><dd id="inv-needle">—</dd></div>'
        f'<div><dt>Schmidt λ₊, λ₋</dt><dd id="inv-schmidt">{lam_plus:.3f}, {lam_minus:.3f}</dd></div>'
        f'<div><dt>Type</dt><dd id="inv-type">Product</dd></div></dl>'
        '<div class="two-scale"><p class="meter-label"><span>Product</span>'
        f'<span class="meter-track"><span class="meter-fill" id="bar-c" style="width:{concurrence * 100:.1f}%">'
        '</span></span><span>Maximally entangled</span></p>'
        '<p class="slider-hint">The needle\'s length is the concurrence. Its direction is the local frame, which'
        ' is a choice of basis — local gates turn the needle but never change its length.</p></div></div>'

        '<section class="two-lab" aria-labelledby="lab-heading"><h2 class="sr-only" id="lab-heading">'
        'Two-qubit vector explorer</h2><div class="phasor-layout">'
        '<figure class="phasor-figure">' + phasor_svg([1, 0, 0, 0]) +
        '<figcaption>One plane, every vector. Pick an arrow and use the arrow keys to turn it, or drag its tip.'
        ' Turning an arrow changes one phase and nothing else.</figcaption></figure>'
        '<div class="phasor-panel">'
        '<fieldset class="qubit-group"><legend>Display basis</legend><div class="qubit-buttons">'
        '<button type="button" id="basis-computational" aria-pressed="true">|00⟩ |01⟩ |10⟩ |11⟩</button>'
        '<button type="button" id="basis-bell" aria-pressed="false">Bell</button>'
        '</div><p class="slider-hint" id="basis-hint">Computational basis. The Bell view re-expresses the same'
        ' state in Φ⁺, Φ⁻, Ψ⁺, Ψ⁻, where each Bell state is a single arrow.</p></fieldset>'
        '<table class="phasor-table"><caption>Amplitude, phase and probability per basis state</caption>'
        '<thead><tr><th scope="col">State</th><th scope="col">Magnitude</th><th scope="col">Phase</th>'
        f'<th scope="col">P</th></tr></thead><tbody>{rows}</tbody></table>'
        '<label class="ph-toggle"><input type="checkbox" id="show-products">'
        '<span>Show the two products 2c<sub>00</sub>c<sub>11</sub> and 2c<sub>01</sub>c<sub>10</sub></span>'
        '</label>'
        '<p class="measure-result" id="needle-note">The highlighted arrow is 2·(c<sub>00</sub>c<sub>11</sub> −'
        ' c<sub>01</sub>c<sub>10</sub>): the first product, then the second one subtracted. Its length is the'
        ' concurrence — zero for a product state, one for a Bell state.</p>'
        '<p class="sr-only" id="state-status" role="status" aria-live="polite"></p>'
        '</div></div></section>'

        '<section class="two-controls" aria-labelledby="controls-heading"><h2 class="sr-only"'
        ' id="controls-heading">Controls</h2>'
        '<fieldset class="qubit-group"><legend>Prepare a state</legend><div class="qubit-buttons">'
        + ''.join(f'<button type="button" data-preset="{key}">{label}</button>'
                  for key, label in TWO_PRESETS)
        + '</div></fieldset>'
        '<fieldset class="qubit-group"><legend>Gates on qubit A</legend><div class="qubit-buttons">'
        + gates + '</div></fieldset>'
        '<fieldset class="qubit-group"><legend>Gates on qubit B</legend><div class="qubit-buttons">'
        + gates_b + '</div></fieldset>'
        '<fieldset class="qubit-group"><legend>Two-qubit gates</legend><div class="qubit-buttons">'
        '<button type="button" data-gate="CNOT" title="Flip B when A is 1">CNOT</button>'
        '<button type="button" data-gate="CZ" title="Flip the sign of |11⟩">CZ</button>'
        '<button type="button" data-gate="SWAP" title="Exchange the two qubits">SWAP</button>'
        '</div><p class="slider-hint">X, Y, Z and S turn arrows in this plane; H replaces two arrows by their sum'
        ' and difference. CNOT and CZ turn a superposition into entanglement: on |+0⟩ or |++⟩ they create the'
        ' needle, on |00⟩ they cannot.</p></fieldset>'
        '<fieldset class="qubit-group"><legend>Measurement</legend><div class="qubit-buttons">'
        '<button type="button" id="measure-a">Measure A</button>'
        '<button type="button" id="measure-b">Measure B</button>'
        '<button type="button" id="measure-both">Measure both</button>'
        '<button type="button" id="two-reset" title="Return to |00⟩ and clear the counts">Reset</button>'
        '</div><p class="measure-result" id="measure-result">Measuring A projects onto |0⟩ or |1⟩ on that qubit.'
        ' On a Bell state the two outcomes always agree.</p>'
        '<p class="measure-tally" id="measure-tally">No joint measurements yet.</p></fieldset>'
        '<noscript><p class="qubit-noscript">The page shows the state |00⟩: one arrow of length 1 along the'
        ' real axis. Enable JavaScript to turn the arrows, apply gates, and measure.</p></noscript></section>'

        '<section class="qubit-reading" id="explanation"><h2>Why one plane is enough</h2>'
        '<p>A pure two-qubit state is four complex numbers, so it is four vectors in the plane — no projection,'
        ' no loss. Two of the eight real numbers are not physical: the total length is fixed to one by'
        ' normalization, and multiplying all four arrows by the same phase only rotates the whole figure, which'
        ' no measurement can see. That leaves six, exactly the state\'s six parameters. This is the one common'
        ' plot that holds everything, phases included.</p>'
        '<p>Arrows that land on the same point are drawn side by side so that both stay visible; lengths and'
        ' angles are untouched.</p>'
        '<p>Gates act on these arrows in ways you can watch. Z and S turn the arrows whose qubit is |1⟩ and leave'
        ' the others alone; H replaces a pair by their sum and difference (divided by √2), which is why it can'
        ' move weight between arrows; X swaps pairs. A relative phase shows up as one arrow turning against the'
        ' others, and that is the information a pair of ordinary Bloch spheres throws away: |Φ⁺⟩ and |Φ⁻⟩ have'
        ' identical reduced states, but here one arrow is flipped through 180°.</p>'
        '<h2>The needle</h2>'
        '<p>Multiply the amplitudes that sit at opposite corners: c<sub>00</sub>c<sub>11</sub> and'
        ' c<sub>01</sub>c<sub>10</sub>. Each product is again a vector, with the phases added and the lengths'
        ' multiplied. A state is a product of two single-qubit states exactly when those two vectors coincide.'
        ' So draw the second from the tip of the first, and close the triangle: the closing arrow is'
        ' 2·(c<sub>00</sub>c<sub>11</sub> − c<sub>01</sub>c<sub>10</sub>). Its length is the concurrence, and it'
        ' vanishes precisely when the state factorizes.</p>'
        '<p>That gives entanglement a single number you can measure with a ruler, and a direction that records'
        ' the relative phase. The length is basis-independent; the direction is a frame, and local gates rotate'
        ' it without changing its length — which is the whole reason a local picture cannot see entanglement.</p>'
        '<h2>Things to try</h2><ol class="qubit-try">'
        '<li>Press <strong>H on A</strong> from |00⟩. Two arrows appear along the real axis, each of length'
        ' 0.707 — |00⟩ and |10⟩ — and the needle stays at zero: still a product state.</li>'
        '<li>Now press <strong>S on A</strong>. The |10⟩ arrow turns by 90° while |00⟩ stays put: a relative'
        ' phase you can see, with the needle still at zero. Press T instead and it turns by 45°.</li>'
        '<li>Load Φ<sup>+</sup> and Φ<sup>−</sup>. Both have the needle at full length 1.000; only its direction'
        ' flips by 180°, and the |11⟩ arrow flips with it. This is the difference the Bloch spheres cannot'
        ' show.</li>'
        '<li>Switch to the <strong>Bell</strong> basis. Each of the four Bell presets becomes a single arrow of'
        ' length 1, while no product state can be: |00⟩ needs two arrows and |+0⟩ needs four. That is the'
        ' sharpest way to see that Bell states are a different kind of object.</li>'
        '<li>Load <strong>|++⟩</strong> and drag one arrow round the circle. Its length never changes, only its'
        ' angle, and the needle grows from zero towards 0.707: a product state becoming entangled as the two'
        ' products stop agreeing. Drag it back to 0° and the needle vanishes again.</li>'
        '<li>Load <strong>Partly entangled</strong>: the needle is 0.707 long, and the two starting arrows are'
        ' 0.924 and 0.383 at the same angle.</li></ol>'
        '<p class="qubit-note">This model follows pure states only, because unitary gates and projective'
        ' measurements keep the state pure. A noisy two-qubit state needs a 4 × 4 density matrix and a'
        ' mixed-state concurrence, and its arrows would need magnitudes that no longer add to one. Measurements'
        ' use your browser\'s random number generator.</p></section>')
    shell('tools/two-qubit.html', 'Two-qubit state visualizer',
          'Every vector of a two-qubit state in one complex plane: four amplitude arrows plus the concurrence'
          ' needle, so phases and entanglement are visible at the same time.',
          body, assets='<link rel="stylesheet" href="tools.css"><script defer src="two-qubit.js"></script>')


def validate(root, data):
    ids = set()
    for tool in data['tools']:
        if tool['id'] in ids:
            raise ValueError('Duplicate tool ID: ' + tool['id'])
        ids.add(tool['id'])
        if not re.fullmatch(r'tools/[a-z0-9]+(?:-[a-z0-9]+)*\.html', tool['href']):
            raise ValueError('Tool links must be pages inside tools/: ' + tool['href'])
        if not all(tool[field].strip() for field in ('kind', 'title', 'summary')):
            raise ValueError('Every tool needs a kind, title and summary')


def relative(target, source):
    return os.path.relpath(target, Path(source).parent).replace(os.sep, '/')


def tool_card(index, tool, source):
    e = escape
    features = ''.join(f'<li>{e(feature)}</li>' for feature in tool['features'])
    return (f'<li class="tool-card"><p class="tool-index" aria-hidden="true">{index:02}</p>'
            f'<div class="tool-body"><p class="tool-status">{e(tool["kind"])}</p>'
            f'<h3><a href="{e(relative(tool["href"], source))}">{e(tool["title"])}</a></h3>'
            f'<p class="tool-summary">{e(tool["summary"])}</p>'
            f'<ul class="tool-features">{features}</ul></div></li>')


def rotation_controls():
    """The arbitrary-gate controls: axis angles, rotation angle, global phase and the matrix they build."""
    axis = rotation_axis(*AXIS_ANGLES)
    matrix = rotation_matrix(axis, ROTATION_ANGLE, ROTATION_PHASE)
    entries = ''.join(f'<div><dt>U{"₀₁"[row]}{"₀₁"[column]}</dt>'
                      f'<dd id="u-{row}{column}">{complex_text(matrix[row][column])}</dd></div>'
                      for row in (0, 1) for column in (0, 1))
    return ('<fieldset class="qubit-group"><legend>Apply any unitary</legend>'
            '<p class="rotation-formula">'
            r'\(U=e^{i\gamma}\bigl(\cos\tfrac{\theta}{2}I-i\sin\tfrac{\theta}{2}\,n\!\cdot\!\sigma\bigr)\)</p>'
            '<div class="slider-row"><label for="axis-theta">θₙ <span class="slider-note">axis polar</span></label>'
            f'<input id="axis-theta" type="range" min="0" max="180" step="1" value="{AXIS_ANGLES[0]}">'
            f'<output id="axis-theta-value" for="axis-theta">{AXIS_ANGLES[0]}°</output></div>'
            '<div class="slider-row"><label for="axis-phi">φₙ <span class="slider-note">axis azimuth</span></label>'
            f'<input id="axis-phi" type="range" min="0" max="360" step="1" value="{AXIS_ANGLES[1]}">'
            f'<output id="axis-phi-value" for="axis-phi">{AXIS_ANGLES[1]}°</output></div>'
            '<div class="slider-row"><label for="rot-theta">θ <span class="slider-note">rotation angle</span></label>'
            f'<input id="rot-theta" type="range" min="0" max="360" step="1" value="{ROTATION_ANGLE}">'
            f'<output id="rot-theta-value" for="rot-theta">{ROTATION_ANGLE}°</output></div>'
            '<div class="slider-row"><label for="rot-gamma">γ <span class="slider-note">global phase</span></label>'
            f'<input id="rot-gamma" type="range" min="0" max="360" step="1" value="{ROTATION_PHASE}">'
            f'<output id="rot-gamma-value" for="rot-gamma">{ROTATION_PHASE}°</output></div>'
            '<div class="qubit-buttons rotation-presets">'
            + ''.join(f'<button type="button" data-axis-theta="{polar}" data-axis-phi="{azimuth}"'
                      f' title="Point n̂ at the {label} axis">{label}</button>'
                      for label, polar, azimuth in AXIS_PRESETS)
            + '<button type="button" id="apply-rotation">Apply U</button></div>'
            '<p class="rotation-readout" id="axis-vector">n̂ = ('
            + ', '.join(complex_text(complex(value)) for value in axis) + ')</p>'
            '<dl class="qubit-values rotation-matrix">' + entries + '</dl></fieldset>')


def render_tools(root, shell):
    data = json.loads((root / 'content/tools.json').read_text())
    validate(root, data)
    e = escape
    count = len(data['tools'])
    index_body = ('<header class="editorial-intro"><p class="eyebrow">Tools / Interactive models</p>'
                  '<h1>Quantum states<br><span>you can move.</span></h1>'
                  f'<p>{e(data["intro"])}</p></header>'
                  '<section class="tool-catalog" id="tools" aria-labelledby="tools-heading"><div class="section-top"><div>'
                  '<p class="eyebrow">Available now</p><h2 id="tools-heading">The tools</h2></div>'
                  f'<span class="tool-count">{count:02} tool{"" if count == 1 else "s"}</span></div>'
                  f'<ol class="tool-list">{"".join(tool_card(n, tool, "tools/index.html") for n, tool in enumerate(data["tools"], 1))}</ol>'
                  '</section><section class="tool-planned" id="planned" aria-labelledby="planned-heading">'
                  '<p class="eyebrow">In development</p><h2 id="planned-heading">Next on the bench</h2>'
                  '<p class="tool-planned-intro">These follow the same rule as the single-qubit sphere: one idea,'
                  ' every control exposed, and the mathematics visible next to the picture.</p><ul>'
                  + ''.join(f'<li><h3>{e(item["title"])}</h3><p>{e(item["summary"])}</p></li>'
                            for item in data['planned'])
                  + '</ul></section>'
                  '<section class="tool-reading" id="about"><h2>How these tools are built</h2>'
                  '<p>Each model is a small programme that runs in the page: no account, no server, and no'
                  ' tracking. Where a drawing depends on a physical parameter, the static page still shows a'
                  ' meaningful state, and the controls always have a keyboard path — sliders for continuous'
                  ' values, buttons for everything else.</p>'
                  '<p>They are companions to the <a href="../education/index.html">courses</a> and the'
                  ' <a href="../research/index.html">research handbook</a>. If a model contradicts your'
                  ' calculation, the calculation is the arbiter.</p></section>')
    shell('tools/index.html', 'Quantum tools',
          'Interactive models for quantum states, starting with a draggable Bloch sphere for a single qubit.',
          index_body, assets='<link rel="stylesheet" href="tools.css">')

    sliders = ('<fieldset class="qubit-group"><legend>Angles</legend>'
               '<div class="slider-row"><label for="theta">θ <span class="slider-note">polar angle</span></label>'
               '<input id="theta" type="range" min="0" max="180" step="1" value="0">'
               '<output id="theta-value" for="theta">0°</output></div>'
               '<div class="slider-row"><label for="phi">φ <span class="slider-note">azimuth</span></label>'
               '<input id="phi" type="range" min="0" max="360" step="1" value="0">'
               '<output id="phi-value" for="phi">0° (0.00π)</output></div></fieldset>')
    presets = ('<fieldset class="qubit-group"><legend>Prepare a state</legend><div class="qubit-buttons">'
               + ''.join(f'<button type="button" data-preset data-theta="{theta}" data-phi="{phi}">{label}</button>'
                         for label, theta, phi in PRESETS)
               + '</div></fieldset>')
    gates = ('<fieldset class="qubit-group"><legend>Apply a gate</legend><div class="qubit-buttons">'
             + ''.join(f'<button type="button" data-gate="{name}" title="{hint}">{name}</button>'
                       for name, hint in GATES)
             + '</div></fieldset>')
    measurement = ('<fieldset class="qubit-group"><legend>Measurement</legend><div class="qubit-buttons">'
                   '<button type="button" id="measure">Measure qubit</button>'
                   '<button type="button" id="reset" title="Return to |0⟩ and clear the counts">Reset</button>'
                   '</div><p class="measure-result" id="measure-result">Measure in the computational basis.'
                   '</p><p class="measure-tally" id="measure-tally">No measurements yet.</p>'
                   '<p class="sr-only" id="state-status" role="status" aria-live="polite"></p></fieldset>')
    tool_body = ('<header class="editorial-intro compact qubit-intro"><p class="eyebrow">Tools / Single-qubit state</p>'
                 '<h1>One qubit, one sphere.</h1>'
                 '<p>A pure state of a single qubit has two physical angles. Drag the arrow on the Bloch sphere, or'
                 ' set θ and φ directly. The green n̂ handle chooses the axis any unitary turns about: drag it, or'
                 ' set its two angles. Then apply a gate — a fixed one, or one you build from that axis, angle and'
                 ' phase — measure the qubit, and watch the amplitudes follow.</p>'
                 '</header>'
                 '<section class="qubit-lab" aria-labelledby="lab-heading">'
                 '<h2 class="sr-only" id="lab-heading">Single-qubit state explorer</h2>'
                 f'<figure class="bloch-figure">{bloch_svg()}'
                 '<figcaption>Drag anywhere on the sphere to point the state vector, or drag the green n̂ handle'
                 ' to aim the rotation axis; Apply U turns the arrow slowly about n̂, leaving the full orbit as a'
                 ' light dotted circle and the part it swept as a darker arc. Keyboard users can set every angle'
                 ' with the sliders.</figcaption></figure>'
                 '<div class="qubit-panel"><div class="qubit-state"><p class="qubit-kicker">Current state</p>'
                 '<p class="qubit-ket" id="state-ket">|0⟩</p><dl class="qubit-values">'
                 '<div><dt>α</dt><dd id="state-alpha">1.000</dd></div>'
                 '<div><dt>β</dt><dd id="state-beta">0.000</dd></div>'
                 '<div><dt>P(0)</dt><dd id="prob-0">1.000</dd></div>'
                 '<div><dt>P(1)</dt><dd id="prob-1">0.000</dd></div></dl>'
                 '<div class="qubit-meters">'
                 '<p class="meter-label"><span>Outcome 0</span><span class="meter-track">'
                 '<span class="meter-fill" id="bar-0" style="width:100%"></span></span></p>'
                 '<p class="meter-label"><span>Outcome 1</span><span class="meter-track">'
                 '<span class="meter-fill" id="bar-1" style="width:0%"></span></span></p>'
                 '</div></div>'
                 + sliders + presets + gates + rotation_controls() + measurement +
                 '<noscript><p class="qubit-noscript">The drawing shows the state |0⟩. Enable JavaScript to drag'
                 ' the arrow, apply gates, and measure the qubit.</p></noscript>'
                 '</div></section>'
                 '<section class="qubit-reading" id="explanation"><h2>What the sphere shows</h2>'
                 '<p>A pure state of one qubit is a pair of complex numbers α and β with |α|² + |β|² = 1. An'
                 ' overall phase and an overall scale have no physical meaning, which leaves exactly two real'
                 ' parameters. This tool writes them as α = cos(θ/2) and β = e<sup>iφ</sup> sin(θ/2), and draws the'
                 ' arrow at (sin θ cos φ, sin θ sin φ, cos θ).</p>'
                 '<p>Because the arrow has length one, every pure state sits on the surface. Opposite points are'
                 ' orthogonal states: |0⟩ and |1⟩ on the vertical axis, |+⟩ and |−⟩ on x, |+i⟩ and |−i⟩ on y. A'
                 ' measurement along z returns 0 with probability |α|² and 1 with probability |β|², which is why'
                 ' moving the arrow around the equator leaves the probabilities alone: phase appears in'
                 ' interference, not in a single computational-basis readout.</p>'
                 '<p>The half angles are not decoration. Turning the qubit through 2π sends α and β to their'
                 ' negatives — a global phase, and the same point on the sphere. The arrow returns to its starting'
                 ' direction only after a 4π turn, and that sign has been measured with neutrons, not just'
                 ' argued.</p>'
                 '<h2 id="general-gate">The most general single-qubit gate</h2>'
                 r'<p>A gate must keep the total probability equal to one, so it is a 2 × 2 unitary matrix,'
                 r' \(U^\dagger U=I\). Every such matrix can be written with four real numbers, an overall phase'
                 r' \(\gamma\) and three angles \(a\), \(b\), \(c\):</p>'
                 r'<p>\[U=e^{i\gamma}\begin{pmatrix}e^{-i(a+c)/2}\cos\frac{b}{2} & -e^{-i(a-c)/2}\sin\frac{b}{2}\\'
                 r' e^{i(a-c)/2}\sin\frac{b}{2} & e^{i(a+c)/2}\cos\frac{b}{2}\end{pmatrix}=e^{i\gamma}R_z(a)\,R_y(b)\,R_z(c),\]</p>'
                 r'<p>where \(R_z(a)=e^{-iaZ/2}\) and \(R_y(b)=e^{-ibY/2}\) are rotations of the arrow about the'
                 r' \(z\) and \(y\) axes. So every gate is a turn about \(z\), a turn about \(y\) and another turn'
                 r' about \(z\). Equivalently, every gate is one rotation by an angle \(\theta\) about a single unit'
                 r' axis \(\hat n=(n_x,n_y,n_z)\):</p>'
                 r'<p>\[U=e^{i\gamma}\Bigl(\cos\tfrac{\theta}{2}\,I-i\sin\tfrac{\theta}{2}\,(n_xX+n_yY+n_zZ)\Bigr),\]</p>'
                 r'<p>and its effect on the sphere is exactly that: the arrow turns by \(\theta\) about'
                 r' \(\hat n\). The phase \(e^{i\gamma}\) multiplies \(\alpha\) and \(\beta\) together and never'
                 r' moves the arrow, which is why the sphere needs only three of the four numbers. The half angles'
                 r' are the same ones as in the amplitudes: a full turn, \(\theta=2\pi\), gives \(-I\).</p>'
                 r'<p>The <em>Apply any unitary</em> controls build this matrix directly. Set the axis with two'
                 r' angles — \(\theta_n\) from the \(z\) axis and \(\phi_n\) around it — then the rotation angle'
                 r' \(\theta\) and the global phase \(\gamma\). The four entries of \(U\) appear beside the'
                 r' sliders, and the dashed diameter on the sphere is \(\hat n\). Apply U turns the arrow by'
                 r' \(\theta\) about that diameter, while \(\alpha\) and \(\beta\) also pick up \(e^{i\gamma}\):'
                 r' set \(\gamma=180^\circ\) and both amplitudes change sign with the arrow untouched. The light'
                 r' dotted circle is the full orbit about \(\hat n\); the darker arc and the translucent cone'
                 r' under it show how far the rotation actually went, and they stay visible until the state'
                 r' moves again. The turn itself is animated so it can be followed; with reduced motion it lands'
                 r' at once.</p>'
                 r'<p>The six gate buttons above are special cases. X, Y and Z are half-turns, \(\theta=\pi\), about the'
                 r' \(x\), \(y\) and \(z\) axes, each times a phase \(-i\), so \(\gamma=90^\circ\) in the controls above'
                 r' rebuilds them. H is \(-i\) times a half-turn about the'
                 r' axis \((1,0,1)/\sqrt2\), halfway between \(x\) and \(z\), which is why it swaps |0⟩ and |+⟩. S'
                 r' and T are quarter- and eighth-turns about \(z\): \(S=e^{i\pi/4}R_z(\pi/2)\) and'
                 r' \(T=e^{i\pi/8}R_z(\pi/4)\).</p>'
                 '<h2>Things to try</h2><ol class="qubit-try">'
                 '<li>Set the state angle θ = 30° and compare α with cos 15° = 0.966 and β with sin 15° = 0.259.</li>'
                 '<li>From |0⟩ press H: the arrow lands on |+⟩ with probabilities 0.500 and 0.500. Press S: the'
                 ' arrow moves to |+i⟩ and P(0) does not move.</li>'
                 '<li>From |0⟩ press X to reach |1⟩, then H to reach |−⟩. Both |+⟩ and |−⟩ measure 0 half the'
                 ' time, so the probabilities alone cannot tell them apart.</li>'
                 '<li>Prepare |+⟩ and press Measure: the arrow jumps to |0⟩ or |1⟩ — the collapse — and the'
                 ' probabilities become certain. Press |+⟩ and Measure again a few times to watch the counts'
                 ' approach 50 / 50.</li>'
                 '<li>Set n̂ to x, θ = 180° and γ = 90°, then Apply U: the matrix equals X and the arrow moves'
                 ' exactly as it does with the X button.</li>'
                 '<li>Leave the axis on z, set θ = 90° and γ = 45°: the matrix is S. Set γ = 0° instead and the'
                 ' same turn leaves every probability alone, because a phase about z is invisible on |0⟩.</li>'
                 '<li>Drag slowly near the north pole and quickly near the equator: the half angle compresses the'
                 ' whole sphere into the amplitudes.</li></ol>'
                 '<p class="qubit-note">This model shows pure states only. A noisy qubit sits inside the sphere,'
                 ' where the arrow is shorter, and needs a density-matrix view that this tool does not yet'
                 ' provide. Measurements here use your browser\'s random number generator, so a short run of'
                 ' outcomes can look surprising: that is statistics, not a bias.</p></section>')
    shell('tools/single-qubit.html', 'Single-qubit state visualizer',
          'Explore a single qubit on the Bloch sphere: drag the state vector, apply gates, and measure the resulting probabilities.',
          tool_body, assets='<link rel="stylesheet" href="tools.css"><script defer src="single-qubit.js"></script>')
    render_two_qubit(root, shell)
