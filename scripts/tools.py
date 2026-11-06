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

import schmidt

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
# The amplitude strip's dials are drawn in a 64-unit square with this ring radius.
AMP_RADIUS = 22.0
PHASOR_LABELS = (('00', '|00⟩', 'Φ⁺'), ('01', '|01⟩', 'Φ⁻'),
                 ('10', '|10⟩', 'Ψ⁺'), ('11', '|11⟩', 'Ψ⁻'))

PAULI = {'I': ((1, 0), (0, 1)), 'X': ((0, 1), (1, 0)),
         'Y': ((0, -1j), (1j, 0)), 'Z': ((1, 0), (0, -1))}

TWO_PRESETS = (('00', '|00⟩'), ('11', '|11⟩'), ('++', '|++⟩'), ('phi+', 'Φ<sup>+</sup>'),
               ('phi-', 'Φ<sup>−</sup>'), ('psi+', 'Ψ<sup>+</sup>'), ('psi-', 'Ψ<sup>−</sup>'),
               ('partial', 'Partly entangled'))
SUPERSCRIPT = {'+': '⁺', '-': '⁻', '−': '⁻'}
# <option> holds text only, so menu labels carry real superscript characters.
TWO_PRESET_MENU = tuple((key, re.sub(r'<sup>(.)</sup>', lambda m: SUPERSCRIPT[m.group(1)], label))
                        for key, label in TWO_PRESETS)


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
    # The disc is painted with the concurrence: 0 at the centre, 1 at the rim, which is the scale the
    # needle already uses, so a warm ring is where a long needle would end.
    heat = (f'<radialGradient id="ph-heat" gradientUnits="userSpaceOnUse" cx="{PHASOR_CENTER:.1f}"'
            f' cy="{PHASOR_CENTER:.1f}" r="{PHASOR_RADIUS:.1f}">'
            + ''.join(f'<stop offset="{offset}" style="stop-color:var(--heat-{index})"/>'
                      for index, offset in enumerate(('0', '.25', '.5', '.75', '1')))
            + '</radialGradient>')
    rings = (f'<circle class="ph-ring" cx="{PHASOR_CENTER:.1f}" cy="{PHASOR_CENTER:.1f}"'
             f' r="{PHASOR_RADIUS:.1f}"/>'
             + ''.join(f'<circle class="ph-contour" cx="{PHASOR_CENTER:.1f}" cy="{PHASOR_CENTER:.1f}"'
                       f' r="{PHASOR_RADIUS * factor:.1f}"/>' for factor in (0.25, 0.5, 0.75)))
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
            ' angle is the phase. The background is the concurrence, cold at the centre and warm at the rim,'
            ' where 0 means a product state and 1 maximal entanglement. Only |00⟩ is present, with magnitude'
            ' 1.000 at phase 0°, so the concurrence needle has zero length at the cold centre.</desc>'
            f'<defs>{markers}{heat}</defs>'
            f'<circle class="ph-heat" id="ph-heat-disc" cx="{PHASOR_CENTER:.1f}" cy="{PHASOR_CENTER:.1f}"'
            f' r="{PHASOR_RADIUS:.1f}" opacity="0"/>'
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


def schmidt_label(tip, text, ident, cls, side, empty=False, center=ORIGIN, radius=RADIUS):
    """A small label just beyond a tip, pushed sideways so the two bases never fall on each other."""
    x, y = tip
    if empty:
        # The text is kept so the script can reveal it when the arm grows; the class hides it now.
        return (f'<text class="{cls} is-empty" id="{ident}" x="{x:.1f}" y="{y:.1f}"'
                f' text-anchor="middle">{text}</text>')
    dx, dy = x - center[0], y - center[1]
    distance = math.hypot(dx, dy) or 1.0
    ux, uy = dx / distance, dy / distance
    # Step just inside the tip and sideways, which keeps the label off both the shaft and the
    # basis-state labels that sit outside the rim.
    x, y = x - ux * 18 - uy * side, y - uy * 18 + ux * side
    return (f'<text class="{cls}" id="{ident}" x="{x:.1f}" y="{y:.1f}" text-anchor="middle"'
            f' dy="4">{text}</text>')


def schmidt_svg(state, prefix='schmidt', center=ORIGIN, radius=RADIUS):
    """One Bloch sphere carrying both Schmidt bases.

    The drawing is a faithful picture of |ψ⟩ = cos θ|+a⟩|+b⟩ + e^{iχ} sin θ|−a⟩|−b⟩: qubit A's two
    basis vectors are always unit length, while qubit B's carry the branch amplitudes cos θ and sin θ
    as their lengths. The two lengths therefore always satisfy cos²θ + sin²θ = 1.
    """
    form = schmidt.schmidt_form(state)
    angle = math.radians(form.theta_deg)
    cos, sin = math.cos(angle), math.sin(angle)
    axis_a, axis_b = form.axis_a, form.axis_b
    flip = lambda v: (-v[0], -v[1], -v[2])
    stretch = lambda v, factor: (v[0] * factor, v[1] * factor, v[2] * factor)
    origin = project((0.0, 0.0, 0.0), center, radius)
    a_plus, a_minus = project(axis_a, center, radius), project(flip(axis_a), center, radius)
    b_plus = project(stretch(axis_b, cos), center, radius)
    b_minus = project(stretch(axis_b, -sin), center, radius)
    corners = (a_plus, b_plus, a_minus, b_minus)
    quad = ' '.join(f'{x:.1f},{y:.1f}' for x, y in corners)
    # The four endpoints share a plane, but that plane can be seen edge-on or collapse to a line
    # when both Schmidt bases line up; a flat quad with no area has no shape to show.
    area = abs(sum(corners[i][0] * corners[(i + 1) % 4][1] - corners[(i + 1) % 4][0] * corners[i][1]
                   for i in range(4))) / 2
    flat = ' is-empty' if area < 24 else ''
    faded = ' is-empty' if sin < ZERO else ''
    line = lambda cls, ident, start, end: (f'<line class="{cls}" id="{ident}" x1="{start[0]:.1f}"'
                                           f' y1="{start[1]:.1f}" x2="{end[0]:.1f}" y2="{end[1]:.1f}"/>')
    dot = lambda cls, ident, point, r=4: (f'<circle class="{cls}" id="{ident}" cx="{point[0]:.1f}"'
                                          f' cy="{point[1]:.1f}" r="{r}"/>')
    basis = ','.join(f'{value:.6f}' for value in (*RIGHT, *UP))
    return (f'<svg class="schmidt" id="{prefix}" viewBox="0 0 400 400" role="img"'
            f' aria-labelledby="{prefix}-title {prefix}-desc" data-basis="{basis}">'
            f'<title id="{prefix}-title">Schmidt bases of the current two-qubit state</title>'
            f'<desc id="{prefix}-desc">Schmidt form at θ = {form.theta_deg:.0f}°: qubit A\'s basis has unit'
            f' length and qubit B\'s vectors have lengths {cos:.3f} and {sin:.3f}. A translucent'
            f' parallelogram joins the four Schmidt endpoints.</desc>'
            f'<circle class="bloch-surface" cx="{center[0]:.1f}" cy="{center[1]:.1f}" r="{radius:.1f}"/>'
            f'<polygon class="schmidt-parallelogram{flat}" id="{prefix}-parallelogram" points="{quad}"/>'
            f'<g class="bloch-grid">{"".join(sphere_grid(center, radius))}</g>'
            f'<g class="bloch-axes">{sphere_axes(center, radius)}</g>'
            + line('schmidt-b-axis', f'{prefix}-b-axis', project(flip(axis_b), center, radius),
                   project(axis_b, center, radius))
            + line('schmidt-a-line', f'{prefix}-a-line', a_minus, a_plus)
            + line('schmidt-b-line', f'{prefix}-b-plus-line', origin, b_plus)
            + line('schmidt-b-line' + faded, f'{prefix}-b-minus-line', origin, b_minus)
            + dot('schmidt-a-tip', f'{prefix}-a-plus', a_plus)
            + dot('schmidt-a-tip', f'{prefix}-a-minus', a_minus)
            + dot('schmidt-b-tip', f'{prefix}-b-plus', b_plus)
            + dot('schmidt-b-tip' + faded, f'{prefix}-b-minus', b_minus)
            + schmidt_label(a_plus, '|+a⟩', f'{prefix}-a-plus-label', 'schmidt-a-label', -20)
            + schmidt_label(a_minus, '|−a⟩', f'{prefix}-a-minus-label', 'schmidt-a-label', -20)
            + schmidt_label(b_plus, '|+b⟩', f'{prefix}-b-plus-label', 'schmidt-b-label', 20)
            + schmidt_label(b_minus, '|−b⟩', f'{prefix}-b-minus-label', 'schmidt-b-label', 20,
                            empty=sin < ZERO)
            + f'<circle class="bloch-origin" cx="{center[0]:.1f}" cy="{center[1]:.1f}" r="2.5"/>'
            '</svg>')


# Three-qubit explorer: eight amplitudes in one plane, plus the relative-state view on one sphere.
# One qubit is the reference, so the state splits into |0⟩|φ₀⟩ + |1⟩|φ₁⟩; each branch is a
# two-qubit state with its own Schmidt bases, and those two bases span one plane in the sphere.

THREE_KEYS = ('000', '001', '010', '011', '100', '101', '110', '111')
THREE_LABELS = tuple('|' + key + '⟩' for key in THREE_KEYS)
THREE_QUBITS = ('A', 'B', 'C')
THREE_SUBSCRIPTS = ('₀', '₁')
THREE_PRESETS = (('planes', 'Two planes'), ('000', '|000⟩'), ('+++', '|+++⟩'),
                 ('ghz', 'GHZ'), ('w', 'W'))
THREE_STATES = {
    '000': (1, 0, 0, 0, 0, 0, 0, 0),
    '+++': (math.sqrt(1 / 8),) * 8,
    'ghz': (math.sqrt(1 / 2), 0, 0, 0, 0, 0, 0, math.sqrt(1 / 2)),
    'w': (0, math.sqrt(1 / 3), math.sqrt(1 / 3), 0, math.sqrt(1 / 3), 0, 0, 0),
    # Chosen so that every choice of reference qubit shows two planes that are clearly apart; the
    # named states (GHZ, W, |000⟩) instead have branches whose Schmidt axes line up.
    'planes': (-0.28393134960506705 + 0.45168829364378027j, 0.26625299315248008 + 0.082071697093509213j,
               0.07089425323024845 + 0.1938563742430385j, -0.13168687249243721 - 0.26948978880487245j,
               -0.15907888253636024 + 0.04783143732863885j, 0.40033177289152511 + 0.059187702119268173j,
               0.29722942580113965 - 0.068721791063861934j, 0.14988116610591448 - 0.44527155402130247j),
}
THREE_TWO_QUBIT = (
    ('cnot-ab', 'CNOT A→B'), ('cnot-ba', 'CNOT B→A'), ('cnot-ac', 'CNOT A→C'),
    ('cnot-ca', 'CNOT C→A'), ('cnot-bc', 'CNOT B→C'), ('cnot-cb', 'CNOT C→B'),
    ('cz-ab', 'CZ A,B'), ('cz-ac', 'CZ A,C'), ('cz-bc', 'CZ B,C'),
    ('swap-ab', 'SWAP A,B'), ('swap-ac', 'SWAP A,C'), ('swap-bc', 'SWAP B,C'),
)


def branch_amplitudes(state, reference, bit):
    """The four amplitudes of the other two qubits, in the branch where the reference reads `bit`."""
    others = [wire for wire in range(3) if wire != reference]
    amplitudes = []
    for row in (0, 1):
        for col in (0, 1):
            bits = [0, 0, 0]
            bits[reference] = bit
            bits[others[0]] = row
            bits[others[1]] = col
            amplitudes.append(state[4 * bits[0] + 2 * bits[1] + bits[2]])
    return amplitudes


def branch_form(state, reference, bit):
    """The branch probability and the Schmidt form of that branch's normalised two-qubit state."""
    amplitudes = branch_amplitudes(state, reference, bit)
    weight = sum(abs(amplitude) ** 2 for amplitude in amplitudes)
    if weight < 1e-9:
        return weight, None
    return weight, schmidt.schmidt_form([amplitude / math.sqrt(weight) for amplitude in amplitudes])


def three_phasor_svg(state, prefix='ph3'):
    """Eight amplitude arrows in one plane. There is no needle: three-qubit entanglement is not one
    number, so the sphere's two Schmidt planes carry that information instead."""
    rings = (f'<circle class="ph-ring" cx="{PHASOR_CENTER:.1f}" cy="{PHASOR_CENTER:.1f}"'
             f' r="{PHASOR_RADIUS:.1f}"/>'
             + ''.join(f'<circle class="ph-contour" cx="{PHASOR_CENTER:.1f}" cy="{PHASOR_CENTER:.1f}"'
                       f' r="{PHASOR_RADIUS * factor:.1f}"/>' for factor in (0.25, 0.5, 0.75)))
    rim = PHASOR_RADIUS * 0.82
    ticks = (f'<text class="ph-tick" x="{PHASOR_CENTER + rim:.0f}" y="{PHASOR_CENTER + 16:.0f}"'
             ' text-anchor="middle">0°</text>'
             f'<text class="ph-tick" x="{PHASOR_CENTER + 12:.0f}" y="{PHASOR_CENTER - rim + 4:.0f}">90°</text>'
             f'<text class="ph-tick" x="{PHASOR_CENTER - rim:.0f}" y="{PHASOR_CENTER + 16:.0f}"'
             ' text-anchor="middle">180°</text>'
             f'<text class="ph-tick" x="{PHASOR_CENTER + 12:.0f}" y="{PHASOR_CENTER + rim + 4:.0f}">270°</text>')
    markers = ''.join(
        f'<marker id="{prefix}-head-{index}" viewBox="0 0 10 10" refX="7.5" refY="5" markerWidth="4.6"'
        f' markerHeight="4.6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z"'
        f' class="{prefix}-head-{index // 2}"/></marker>' for index in range(8))
    vectors = ''
    for index, key in enumerate(THREE_KEYS):
        amplitude = state[index]
        magnitude = abs(amplitude)
        phase = math.degrees(cmath.phase(amplitude)) % 360 if magnitude > 1e-9 else 0.0
        hidden = ' is-empty' if magnitude <= 1e-9 else ''
        x0, y0 = phasor_tip(magnitude, phase)
        vectors += (f'<g class="{prefix}-vec{hidden}" data-index="{index}" id="{prefix}-group-{key}">'
                    f'<line class="{prefix}-hit" x1="{PHASOR_CENTER:.1f}" y1="{PHASOR_CENTER:.1f}"'
                    f' x2="{x0:.1f}" y2="{y0:.1f}"/>'
                    + phasor_arrow(f'{prefix}-vec-{key}', magnitude, phase, THREE_LABELS[index],
                                   f'{prefix}-head-{index}', cls=f'{prefix}-arrow')
                    + '</g>')
    return (f'<svg class="phasor phasor8" id="{prefix}" viewBox="0 0 440 440" role="group"'
            f' aria-labelledby="{prefix}-title {prefix}-desc">'
            f'<title id="{prefix}-title">Eight vectors of the three-qubit state in one complex plane</title>'
            f'<desc id="{prefix}-desc">Eight arrows, one per computational basis amplitude: the length is the'
            f' magnitude and the angle is the phase. Drag an arrow to set both, or use the arrow keys to turn'
            f' and resize it.</desc>'
            f'<defs>{markers}</defs>'
            f'<g class="ph-grid">{rings}'
            f'<line class="ph-axis" x1="48" y1="{PHASOR_CENTER:.1f}" x2="392" y2="{PHASOR_CENTER:.1f}"/>'
            f'<line class="ph-axis" x1="{PHASOR_CENTER:.1f}" y1="48" x2="{PHASOR_CENTER:.1f}" y2="392"/>'
            f'{ticks}</g>'
            f'<g class="{prefix}-vectors">' + vectors + '</g>'
            f'<circle class="ph-origin" cx="{PHASOR_CENTER:.1f}" cy="{PHASOR_CENTER:.1f}" r="3"/>'
            '</svg>')


def _vec_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _vec_norm(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def plane_normal(form):
    """The unit normal of a branch's Schmidt plane, or None when the branch is empty."""
    if form is None:
        return None
    normal = _vec_cross(form.axis_a, form.axis_b)
    length = _vec_norm(normal)
    return tuple(value / length for value in normal) if length > 1e-9 else None


def _signed(value):
    return ('−' if value < 0 else '') + f'{abs(value):.2f}'


PLANE_RING_STEPS = 48
# |n0 × n1| below which the two planes are too nearly twins for a front/back split to mean anything.
PLANE_SPLIT_MIN = 0.06
# |n_other · forward| below which the camera sits in the other plane, so the depth there is a tie.
PLANE_VIEW_FLAT = 0.05


def _vec_dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _vec_unit(a):
    length = _vec_norm(a)
    return tuple(value / length for value in a) if length > 1e-9 else None


def plane_ring(axis_p, axis_q):
    """t -> a point on the circle where the plane of two Schmidt axes meets the sphere."""
    e1 = _vec_unit(axis_p)
    q = _vec_unit(axis_q)
    if e1 is None or q is None:
        return None
    e2 = _vec_unit(tuple(value - _vec_dot(q, e1) * base for value, base in zip(q, e1)))
    if e2 is None:
        return None
    return lambda t: tuple(math.cos(t) * a + math.sin(t) * b for a, b in zip(e1, e2))


def clip_half(polygon, normal, sign):
    """The part of a convex polygon where sign·normal·x >= 0, with the cut edges added in."""
    kept = []
    for index, current in enumerate(polygon):
        previous = polygon[index - 1]
        current_side = sign * _vec_dot(normal, current)
        previous_side = sign * _vec_dot(normal, previous)
        if (current_side >= 0) != (previous_side >= 0):
            t = previous_side / (previous_side - current_side)
            kept.append(tuple(p + t * (c - p) for p, c in zip(previous, current)))
        if current_side >= 0:
            kept.append(current)
    return kept


def polygon_points(polygon):
    """The projected polygon as an SVG points attribute, or '' when it has no area."""
    return ' '.join(f'{x:.1f},{y:.1f}' for x, y in (project(point) for point in polygon))


def plane_meeting(branches):
    """The direction of the two planes' intersection and their dihedral angle, or None."""
    normals = [plane_normal(form) for _, form in branches]
    if any(normal is None for normal in normals):
        return None
    axis = _vec_cross(normals[0], normals[1])
    length = _vec_norm(axis)
    if length < 1e-6:
        return None
    cosine = sum(first * second for first, second in zip(normals[0], normals[1]))
    return (tuple(value / length for value in axis),
            math.degrees(math.acos(min(1.0, abs(cosine)))))


def basis_label(point, text, name, center=ORIGIN, spread=1.16):
    """One end of the shared basis, tagged just outside the sphere."""
    x = center[0] + (point[0] - center[0]) * spread
    y = center[1] + (point[1] - center[1]) * spread + 4
    return (f'<text class="plane-u-label" id="{name}" x="{x:.1f}" y="{y:.1f}"'
            f' text-anchor="middle">{text}</text>')


def meeting_svg(prefix, branches, center=ORIGIN, radius=RADIUS):
    """The diameter where the two Schmidt planes meet; hidden when the planes coincide."""
    meeting = plane_meeting(branches)
    hidden = '' if meeting else ' is-empty'
    axis = meeting[0] if meeting else (0.0, 0.0, 1.0)
    plus = project(axis, center, radius)
    minus = project(tuple(-value for value in axis), center, radius)
    return (f'<g class="plane-meet{hidden}" id="{prefix}-meet">'
            f'<line class="plane-meet-line" id="{prefix}-meet-line" x1="{minus[0]:.1f}"'
            f' y1="{minus[1]:.1f}" x2="{plus[0]:.1f}" y2="{plus[1]:.1f}"/>'
            f'<circle class="plane-meet-tip" id="{prefix}-meet-plus" cx="{plus[0]:.1f}"'
            f' cy="{plus[1]:.1f}" r="2.8"/>'
            f'<circle class="plane-meet-tip" id="{prefix}-meet-minus" cx="{minus[0]:.1f}"'
            f' cy="{minus[1]:.1f}" r="2.8"/>'
            + basis_label(plus, '|+û⟩', f'{prefix}-meet-plus-label', center)
            + basis_label(minus, '|−û⟩', f'{prefix}-meet-minus-label', center)
            + '</g>')


def axis_tilt(axis, direction):
    """How far a Schmidt axis leans away from the shared basis axis, in degrees."""
    cosine = abs(sum(first * second for first, second in zip(axis, direction)))
    return math.degrees(math.acos(min(1.0, cosine)))


def basis_report(branches):
    """The shared basis of the two planes as two lines of text: where it points, and the leans and twist."""
    meeting = plane_meeting(branches)
    if meeting is None:
        return ('The two planes coincide, so every diameter of their common plane is a shared basis.',
                'No single shared axis, so no leans to report.')
    axis, dihedral = meeting
    polar, azimuth = schmidt.angles_from_axis(axis)
    line = (f'The planes meet at {dihedral:.1f}° along û = ('
            + ', '.join(_signed(value) for value in axis)
            + f'); that diameter is the basis |+û⟩, |−û⟩, at polar {polar:.0f}° and azimuth {azimuth:.0f}°.')
    leans = []
    for bit, (_, form) in enumerate(branches):
        sub = THREE_SUBSCRIPTS[bit]
        leans.append(f'λ{sub} = {axis_tilt(axis, form.axis_a):.0f}°, '
                     f'μ{sub} = {axis_tilt(axis, form.axis_b):.0f}°')
    detail = ('In the shared û basis all four amplitudes survive in each branch; the frame data left is '
              + ', '.join(leans)
              + f', and the twist α = {dihedral:.1f}° between the two meridians.')
    return line, detail


def three_planes_svg(state, reference=0, prefix='planes'):
    """One Bloch sphere carrying both branches' Schmidt planes.

    The reference qubit stays the pair of kets |0⟩ and |1⟩; for each value, the other two qubits
    form a two-qubit state with its own Schmidt bases. Those bases span a plane, so the sphere
    holds one plane per branch. Each plane is filled where it meets the sphere, so the shared
    diameter visibly lies inside both, and the half nearer the camera is drawn stronger so the two
    planes read as crossing rather than stacked. A plane needs two independent axes: when they
    line up there is no plane, and it is hidden rather than drawn as a stray line.
    """
    origin = project((0.0, 0.0, 0.0), ORIGIN, RADIUS)
    names = [THREE_QUBITS[wire].lower() for wire in range(3) if wire != reference]
    branches = [branch_form(state, reference, bit) for bit in (0, 1)]
    normals = [plane_normal(form) for _, form in branches]
    basis = ','.join(f'{value:.6f}' for value in (*RIGHT, *UP))
    rings = [plane_ring(form.axis_a, form.axis_b) if form else None for _, form in branches]
    splittable = (None not in normals
                  and _vec_norm(_vec_cross(normals[0], normals[1])) > PLANE_SPLIT_MIN)
    # Which side of the other plane faces the camera: the half on that side is the half in front.
    sides = [None, None]
    if splittable:
        for bit in (0, 1):
            other = normals[1 - bit]
            if abs(_vec_dot(other, FORWARD)) >= PLANE_VIEW_FLAT:
                sides[bit] = 1.0 if _vec_dot(other, FORWARD) < 0 else -1.0
    sampled = [[ring(2 * math.pi * index / PLANE_RING_STEPS) for index in range(PLANE_RING_STEPS)]
               if ring else [] for ring in rings]
    fills = ''
    # Back halves first, then front halves: along any line of sight at most one of the two planes
    # is the far one, so this order paints every overlap correctly.
    for half, bit in ((half, bit) for half in ('far', 'near') for bit in (0, 1)):
        weight = branches[bit][0]
        opacity = 0.11 + 0.18 * weight if half == 'near' else 0.03 + 0.04 * weight
        if not sampled[bit]:
            points, empty = '', ' is-empty'
        elif sides[bit] is None:
            points = polygon_points(sampled[bit])
            empty = '' if half == 'near' else ' is-empty'
        else:
            sign = sides[bit] if half == 'near' else -sides[bit]
            piece = clip_half(sampled[bit], normals[1 - bit], sign)
            points = polygon_points(piece)
            empty = '' if len(piece) > 2 else ' is-empty'
        fills += (f'<polygon class="plane-fill plane-{half} branch-{bit}{empty}"'
                  f' id="{prefix}-fill-{bit}-{half}" points="{points}"'
                  f' style="fill-opacity:{opacity:.3f}"/>')
    edges = ''
    for bit, ring in enumerate(rings):
        if ring is None:
            continue
        for visible, path in arcs(ring):
            edges += (f'<path class="plane-edge branch-{bit}" d="{path}"/>' if visible
                      else f'<path class="plane-edge branch-{bit} is-behind" d="{path}"/>')
    groups = ''
    for bit, (weight, form) in enumerate(branches):
        theta = form.theta_deg if form else 0.0
        axis_p = form.axis_a if form else (0.0, 0.0, 1.0)
        axis_q = form.axis_b if form else (0.0, 0.0, 1.0)
        cos, sin = math.cos(math.radians(theta)), math.sin(math.radians(theta))
        p_plus, p_minus = project(axis_p), project(tuple(-value for value in axis_p))
        q_plus = project(tuple(cos * value for value in axis_q))
        q_minus = project(tuple(-sin * value for value in axis_q))
        hidden = ' is-empty' if weight < 1e-9 else ''
        sub = THREE_SUBSCRIPTS[bit]
        # The two branches can share an axis, so their labels sit on opposite sides of it.
        p_side, q_side = (-20, 20) if bit == 0 else (20, -20)
        groups += (
            f'<g class="plane-branch branch-{bit}{hidden}" id="{prefix}-branch-{bit}"'
            f' style="opacity:{0.3 + 0.7 * weight:.2f}">'
            f'<line class="plane-axis" id="{prefix}-p-axis-{bit}" x1="{p_minus[0]:.1f}" y1="{p_minus[1]:.1f}"'
            f' x2="{p_plus[0]:.1f}" y2="{p_plus[1]:.1f}"/>'
            f'<line class="plane-arm" id="{prefix}-q-plus-{bit}" x1="{origin[0]:.1f}" y1="{origin[1]:.1f}"'
            f' x2="{q_plus[0]:.1f}" y2="{q_plus[1]:.1f}"/>'
            f'<line class="plane-arm" id="{prefix}-q-minus-{bit}" x1="{origin[0]:.1f}" y1="{origin[1]:.1f}"'
            f' x2="{q_minus[0]:.1f}" y2="{q_minus[1]:.1f}"/>'
            f'<circle class="plane-p-tip" id="{prefix}-p-plus-tip-{bit}" cx="{p_plus[0]:.1f}"'
            f' cy="{p_plus[1]:.1f}" r="3.4"/>'
            f'<circle class="plane-p-tip" id="{prefix}-p-minus-tip-{bit}" cx="{p_minus[0]:.1f}"'
            f' cy="{p_minus[1]:.1f}" r="3.4"/>'
            f'<circle class="plane-q-tip" id="{prefix}-q-plus-tip-{bit}" cx="{q_plus[0]:.1f}"'
            f' cy="{q_plus[1]:.1f}" r="3.4"/>'
            f'<circle class="plane-q-tip" id="{prefix}-q-minus-tip-{bit}" cx="{q_minus[0]:.1f}"'
            f' cy="{q_minus[1]:.1f}" r="3.4"/>'
            + schmidt_label(p_plus, f'|+{names[0]}⟩{sub}', f'{prefix}-p-plus-label-{bit}',
                            'plane-p-label', p_side)
            + schmidt_label(p_minus, f'|−{names[0]}⟩{sub}', f'{prefix}-p-minus-label-{bit}',
                            'plane-p-label', p_side)
            + schmidt_label(q_plus, f'|+{names[1]}⟩{sub}', f'{prefix}-q-plus-label-{bit}',
                            'plane-q-label', q_side)
            + schmidt_label(q_minus, f'|−{names[1]}⟩{sub}', f'{prefix}-q-minus-label-{bit}',
                            'plane-q-label', q_side, empty=sin < ZERO)
            + '</g>')
    description = ('Two Schmidt planes, one for each value of the reference qubit. Each plane is drawn'
                   ' as the disc where it cuts the sphere, its half nearer the camera stronger, so the two'
                   ' planes read as crossing; the branch probability sets its opacity. The violet diameter'
                   ' where the planes cross is the basis the two branches share.')
    return (f'<svg class="planes" id="{prefix}" viewBox="0 0 400 400" role="img" tabindex="0"'
            f' aria-labelledby="{prefix}-title {prefix}-desc" data-basis="{basis}"'
            f' data-azimuth="{AZIMUTH:.1f}" data-elevation="{ELEVATION:.1f}">'
            f'<title id="{prefix}-title">The two Schmidt planes of the relative-state view</title>'
            f'<desc id="{prefix}-desc">{description} Drag the sphere, or use the arrow keys while it has'
            f' focus, to orbit the view.</desc>'
            f'<circle class="bloch-surface" cx="{ORIGIN[0]:.1f}" cy="{ORIGIN[1]:.1f}" r="{RADIUS:.1f}"/>'
            f'<g class="bloch-grid" id="{prefix}-grid">{"".join(sphere_grid())}</g>'
            f'<g class="bloch-axes" id="{prefix}-axes">{sphere_axes()}</g>'
            f'<g class="plane-fills" id="{prefix}-fills">{fills}</g>'
            f'<g class="plane-edges" id="{prefix}-edges">{edges}</g>'
            + groups
            + meeting_svg(prefix, branches) +
            f'<circle class="bloch-origin" cx="{ORIGIN[0]:.1f}" cy="{ORIGIN[1]:.1f}" r="2.5"/>'
            '</svg>')


def render_two_qubit(root, shell):
    e = escape
    # A dial per basis state: arrow length is the magnitude, arrow angle the phase.
    dials = ''
    for index, (key, label, _) in enumerate(PHASOR_LABELS):
        empty = index != 0
        x = 32 + (0 if empty else AMP_RADIUS)
        tip = ' is-empty' if empty else ''
        dials += (f'<div class="amp-cell" data-index="{index}">'
                  '<svg class="amp-dial" viewBox="0 0 64 64" aria-hidden="true">'
                  f'<circle class="amp-ring" cx="32" cy="32" r="{AMP_RADIUS}"/>'
                  '<line class="amp-axis" x1="8" y1="32" x2="56" y2="32"/>'
                  '<line class="amp-axis" x1="32" y1="8" x2="32" y2="56"/>'
                  f'<line class="amp-needle" id="amp-needle-{key}" x1="32" y1="32" x2="{x}" y2="32"/>'
                  f'<circle class="amp-tip{tip}" id="amp-tip-{key}" cx="{x}" cy="32" r="2.6"/>'
                  '</svg>'
                  f'<p class="amp-name" id="amp-name-{key}">{label}</p>'
                  f'<p class="amp-numbers"><span id="amp-mag-{key}">{"0.000" if empty else "1.000"}</span>'
                  f'<span id="amp-phase-{key}">{"—" if empty else "0°"}</span></p>'
                  '</div>')
    body = (
        '<header class="editorial-intro compact qubit-intro"><p class="eyebrow">Tools / Two-qubit state</p>'
        '<h1>The state is<br><span>four arrows.</span></h1>'
        '<p>A two-qubit state is four complex numbers, and a complex number is a vector. So the whole state fits'
        ' in one ordinary plane: four arrows whose lengths are the magnitudes and whose angles are the phases.'
        ' Gates turn and add those arrows; the fifth, heavy arrow measures how entangled the pair is. Below the'
        ' plane, the same state is redrawn in Schmidt form: one sphere, the first qubit\'s basis at unit'
        ' length, the second qubit\'s vectors scaled by the two branch amplitudes.</p>'
        '</header>'

        '<section class="two-controls" aria-labelledby="controls-heading"><h2 class="sr-only"'
        ' id="controls-heading">Controls</h2>'
        '<div class="menu-row">'
        '<div class="menu"><label for="menu-state">State</label><select id="menu-state">'
        '<option value="">Custom…</option>'
        + ''.join(f'<option value="{key}">{label}</option>' for key, label in TWO_PRESET_MENU)
        + '</select></div>'
        '<div class="menu"><label for="menu-gate-a">Gate on A</label><select id="menu-gate-a">'
        '<option value="" selected>Choose…</option>'
        + ''.join(f'<option value="{name}" title="{hint} on qubit A">{name}</option>' for name, hint in GATES)
        + '</select></div>'
        '<div class="menu"><label for="menu-gate-b">Gate on B</label><select id="menu-gate-b">'
        '<option value="" selected>Choose…</option>'
        + ''.join(f'<option value="{name}" title="{hint} on qubit B">{name}</option>' for name, hint in GATES)
        + '</select></div>'
        '<div class="menu"><label for="menu-gate-two">Two-qubit gate</label><select id="menu-gate-two">'
        '<option value="" selected>Choose…</option>'
        '<option value="CNOT" title="Flip B when A is 1">CNOT</option>'
        '<option value="CZ" title="Flip the sign of |11⟩">CZ</option>'
        '<option value="SWAP" title="Exchange the two qubits">SWAP</option>'
        '</select></div>'
        '<div class="menu"><label for="menu-measure">Measurement</label><select id="menu-measure">'
        '<option value="" selected>Choose…</option>'
        '<option value="measure-a">Measure A</option>'
        '<option value="measure-b">Measure B</option>'
        '<option value="measure-both">Measure both</option>'
        '<option value="two-reset">Reset</option>'
        '</select></div>'
        '</div>'
        '<div class="control-readouts"><p class="control-line">'
        '<span class="measure-result" id="measure-result">Measure A, B or both: the outcome appears here.</span>'
        '<span class="measure-tally" id="measure-tally">No joint measurements yet.</span></p></div>'
        '<noscript><p class="qubit-noscript">The page shows the state |00⟩: one arrow of length 1 along the'
        ' real axis. Enable JavaScript to turn and resize the arrows, apply gates, and measure.</p></noscript>'
        '</section>'

        '<section class="two-views" aria-labelledby="views-heading">'
        '<h2 class="sr-only" id="views-heading">The same state in two pictures</h2>'
        '<div class="view-grid">'
        '<section class="view-column" aria-labelledby="phasor-heading">'
        '<p class="eyebrow">Amplitudes</p>'
        '<h3 class="view-heading" id="phasor-heading">Four arrows in one plane</h3>'
        '<figure class="phasor-figure">' + phasor_svg([1, 0, 0, 0]) +
        '<figcaption>Drag an arrow to set both its length and its angle, or use ←/→ to turn it and ↑/↓ to'
        ' resize it. Edits may leave the arrows unnormalized; Normalize rescales all four so that'
        ' Σ|c|² = 1. The background is the concurrence: it deepens from 0 at the centre to 1 at the rim, and'
        ' its colour rises and fades with the current value. Every change updates the Schmidt sphere too.'
        '</figcaption></figure>'
        '<div class="phasor-panel">'
        '<div class="phasor-actions">'
        '<button type="button" class="ph-normalize" id="normalize-arrows" aria-describedby="state-norm">'
        'Normalize</button>'
        '<p class="ph-norm" id="state-norm">Σ|c|² = 1.000 — the arrows are normalized.</p>'
        '</div>'
        '<div class="amplitude-strip" role="group" aria-label="Magnitude and phase per basis state">'
        + dials + '</div>'
        '<p class="amp-caption">Arrow length is the magnitude, its angle the phase. A drag sets both;'
        ' ←/→ turns an arrow and ↑/↓ resizes it.</p>'
        '<label class="ph-toggle"><input type="checkbox" id="show-products">'
        '<span>Show the two products 2c<sub>00</sub>c<sub>11</sub> and 2c<sub>01</sub>c<sub>10</sub></span>'
        '</label>'
        '<p class="measure-result" id="needle-note">The highlighted arrow is 2·(c<sub>00</sub>c<sub>11</sub> −'
        ' c<sub>01</sub>c<sub>10</sub>) divided by the total weight Σ|c|², which is one while the arrows are'
        ' normalized: the first product, then the second one subtracted. Its length is the concurrence — zero'
        ' for a product state, one for a Bell state — and a rescaling leaves it unchanged.</p>'
        '<p class="sr-only" id="state-status" role="status" aria-live="polite"></p>'
        '</div></section>'

        '<section class="view-column" aria-labelledby="schmidt-heading">'
        '<p class="eyebrow">Schmidt form</p>'
        '<h3 class="view-heading" id="schmidt-heading">One basis unit, one scaled</h3>'
        '<figure class="schmidt-figure">' + schmidt_svg([1, 0, 0, 0]) +
        '<figcaption>Qubit A\'s Schmidt basis stays at unit length; qubit B\'s two vectors carry the branch'
        ' amplitudes cos θ and sin θ as their lengths, so the pair always obeys cos²θ + sin²θ = 1. The dashed'
        ' diameter marks B\'s axis even when an arm has shrunk to nothing, and the translucent parallelogram'
        ' joins the four endpoints, flattening out of sight when the two Schmidt bases line up.'
        '</figcaption></figure>'
        '<div class="schmidt-panel">'
        '<p class="schmidt-formula" id="schmidt-formula">|ψ⟩ = 1.000 |+a⟩|+b⟩</p>'
        '<dl class="two-invariants schmidt-values">'
        '<div><dt>Schmidt angle θ</dt><dd id="schmidt-theta">0°</dd></div>'
        '<div><dt>λ₀ = cos²θ</dt><dd id="schmidt-lambda-0">1.000</dd></div>'
        '<div><dt>λ₁ = sin²θ</dt><dd id="schmidt-lambda-1">0.000</dd></div>'
        '<div><dt>Relative phase χ</dt><dd id="schmidt-chi">—</dd></div>'
        '</dl>'
        '<p class="slider-hint">θ = 0 is a product state and θ = 45° is maximal entanglement. Gates move the'
        ' bases and the weights together; χ is the phase between the two branches, and no Bloch sphere shows'
        ' it.</p>'
        '</div></section>'
        '</div></section>'

        '<section class="qubit-reading" id="explanation"><h2>Why one plane is enough</h2>'
        '<p>A pure two-qubit state is four complex numbers, so it is four vectors in the plane — no projection,'
        ' no loss. Two of the eight real numbers are not physical: the total length is fixed to one by'
        ' normalization, and multiplying all four arrows by the same phase only rotates the whole figure, which'
        ' no measurement can see. That leaves six, exactly the state\'s six parameters. This is the one common'
        ' plot that holds everything, phases included.</p>'
        '<p>Here you can stretch the arrows yourself, which makes the first constraint visible. While the lengths'
        ' are free the drawing is unnormalized; the <strong>Normalize</strong> button divides all four arrows by'
        ' √(Σ|c|²), so the weights add up to one again. Every readout on the page already divides by that'
        ' weight, so stretching an arrow changes the picture but never invents entanglement.</p>'
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
        ' vanishes precisely when the state factorizes. Both products are divided by the total weight, which is'
        ' one for normalized arrows, so the needle stays inside the rim even while the arrows are stretched.</p>'
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
        '<li>Load <strong>|++⟩</strong> and turn one arrow with ←/→, or drag it round at a steady radius. Its'
        ' length never changes, only its angle, and the needle grows from zero towards 0.707: a product state'
        ' becoming entangled as the two products stop agreeing. Turn it back to 0° and the needle vanishes'
        ' again.</li>'
        '<li>Load <strong>Partly entangled</strong>: the needle is 0.707 long, and the two starting arrows are'
        ' 0.924 and 0.383 at the same angle.</li>'
        '<li>Load Φ<sup>+</sup> and drag the |11⟩ arrow outwards. Its length passes 0.707, the weight readout'
        ' climbs past 1, and the needle shortens to 0.943: two long arrows in step are less entangled once the'
        ' extra weight is divided out. Press <strong>Normalize</strong>: the arrows shrink so the weight is'
        ' 1.000 again, while the needle stays at 0.943. Normalization moves the arrows, not the physics.</li>'
        '<li>Load Φ<sup>+</sup> and press <strong>H on A</strong>. The two Schmidt bases swing apart and a'
        ' translucent parallelogram joins the four endpoints; at θ = 45° its diagonals bisect each other, so'
        ' it really is a parallelogram. Press H again and it flattens as the bases line up once more.</li>'
        '</ol>'
        '<p class="qubit-note">This model follows pure states only, because unitary gates and projective'
        ' measurements keep the state pure. A noisy two-qubit state needs a 4 × 4 density matrix and a'
        ' mixed-state concurrence, and its arrows would need magnitudes that no longer add to one. Measurements'
        ' use your browser\'s random number generator.</p></section>')
    shell('tools/two-qubit.html', 'Two-qubit state visualizer',
          'Every vector of a two-qubit state in one complex plane: four amplitude arrows plus the concurrence'
          ' needle, so phases and entanglement are visible at the same time.',
          body, assets='<link rel="stylesheet" href="tools.css"><script defer src="two-qubit.js"></script>')


def render_three_qubit(root, shell):
    e = escape
    state = THREE_STATES['planes']
    dials = ''
    for index, key in enumerate(THREE_KEYS):
        magnitude = abs(state[index])
        phase = math.degrees(cmath.phase(state[index])) % 360 if magnitude > 1e-9 else 0.0
        empty = magnitude <= 1e-9
        x = 32 if empty else 32 + AMP_RADIUS * magnitude * math.cos(math.radians(phase))
        y = 32 if empty else 32 - AMP_RADIUS * magnitude * math.sin(math.radians(phase))
        tip = ' is-empty' if empty else ''
        phase_text = '—' if empty else f'{phase:.0f}°'
        dials += (f'<div class="amp-cell" data-index="{index}">'
                  '<svg class="amp-dial" viewBox="0 0 64 64" aria-hidden="true">'
                  f'<circle class="amp-ring" cx="32" cy="32" r="{AMP_RADIUS}"/>'
                  '<line class="amp-axis" x1="8" y1="32" x2="56" y2="32"/>'
                  '<line class="amp-axis" x1="32" y1="8" x2="32" y2="56"/>'
                  f'<line class="amp-needle{tip}" id="amp3-needle-{key}" x1="32" y1="32"'
                  f' x2="{x:.1f}" y2="{y:.1f}"/>'
                  f'<circle class="amp-tip{tip}" id="amp3-tip-{key}" cx="{x:.1f}" cy="{y:.1f}" r="2.6"/>'
                  '</svg>'
                  f'<p class="amp-name" id="amp3-name-{key}">{THREE_LABELS[index]}</p>'
                  f'<p class="amp-numbers"><span id="amp3-mag-{key}">{magnitude:.3f}</span>'
                  f'<span id="amp3-phase-{key}">{phase_text}</span></p>'
                  '</div>')
    branches = [branch_form(state, 0, bit) for bit in (0, 1)]
    names = [THREE_QUBITS[wire].lower() for wire in range(3) if wire != 0]
    angle_text, basis_text = basis_report(branches)
    expansion = (f'|ψ⟩ = {math.sqrt(branches[0][0]):.3f} |0⟩<sub>A</sub>|φ₀⟩'
                 f' + {math.sqrt(branches[1][0]):.3f} |1⟩<sub>A</sub>|φ₁⟩')
    formulas = ''
    probabilities, angles, weights, phases = [], [], [], []
    for bit, (weight, form) in enumerate(branches):
        sub = THREE_SUBSCRIPTS[bit]
        cos = math.cos(math.radians(form.theta_deg))
        sin = math.sin(math.radians(form.theta_deg))
        probabilities.append(f'{weight:.3f}')
        angles.append(f'{form.theta_deg:.0f}°')
        weights.append(f'{cos * cos:.3f} / {sin * sin:.3f}')
        phases.append(f'{form.chi_deg:.0f}°')
        formulas += (f'<p class="schmidt-formula" id="branch-formula-{bit}">|φ{sub}⟩ = {cos:.3f}'
                     f' |+{names[0]}⟩{sub}|+{names[1]}⟩{sub} + e^{{i{form.chi_deg:.0f}°}} {sin:.3f}'
                     f' |−{names[0]}⟩{sub}|−{names[1]}⟩{sub}</p>')
    rows = ''.join(
        f'<tr><th scope="row">{label}</th><td id="branch-{key}-0">{values[0]}</td>'
        f'<td id="branch-{key}-1">{values[1]}</td></tr>'
        for label, key, values in (('Probability', 'prob', probabilities),
                                   ('Schmidt angle θ', 'theta', angles),
                                   ('cos²θ / sin²θ', 'weights', weights),
                                   ('Relative phase χ', 'chi', phases)))
    gate_options = ''.join(f'<option value="{name}" title="{hint}">{name}</option>' for name, hint in GATES)
    presets = ''.join(f'<option value="{key}">{e(label)}</option>' for key, label in THREE_PRESETS)
    references = ''.join(f'<option value="{index}"{" selected" if index == 0 else ""}>{name}</option>'
                         for index, name in enumerate(THREE_QUBITS))
    pairs = ''.join(f'<option value="{key}">{label}</option>' for key, label in THREE_TWO_QUBIT)
    body = (
        '<header class="editorial-intro compact qubit-intro"><p class="eyebrow">Tools / Three-qubit state</p>'
        '<h1>One qubit as<br><span>the reference.</span></h1>'
        '<p>A three-qubit pure state is eight complex numbers, so it is eight arrows in one plane. Choose'
        ' one qubit as the reference and the same state reads |0⟩|φ₀⟩ + |1⟩|φ₁⟩: two two-qubit states, one'
        ' for each value of that qubit. Each branch has its own Schmidt bases and contributes four endpoints;'
        ' two Schmidt axes span a plane, so a single Bloch sphere carries two planes — one per branch — and'
        ' you can turn it to see them from any side.</p></header>'

        '<section class="two-controls" aria-labelledby="controls-heading"><h2 class="sr-only"'
        ' id="controls-heading">Controls</h2>'
        '<div class="menu-row">'
        '<div class="menu"><label for="menu-state3">State</label><select id="menu-state3">'
        '<option value="">Custom…</option>' + presets + '</select></div>'
        '<div class="menu"><label for="menu-reference">Reference qubit</label><select id="menu-reference">'
        + references + '</select></div>'
        '<div class="menu"><label for="menu-gate-0">Gate on A</label><select id="menu-gate-0">'
        '<option value="" selected>Choose…</option>' + gate_options + '</select></div>'
        '<div class="menu"><label for="menu-gate-1">Gate on B</label><select id="menu-gate-1">'
        '<option value="" selected>Choose…</option>' + gate_options + '</select></div>'
        '<div class="menu"><label for="menu-gate-2">Gate on C</label><select id="menu-gate-2">'
        '<option value="" selected>Choose…</option>' + gate_options + '</select></div>'
        '<div class="menu"><label for="menu-gate-pair">Two-qubit gate</label>'
        '<select id="menu-gate-pair"><option value="" selected>Choose…</option>' + pairs + '</select></div>'
        '<div class="menu"><label for="menu-measure3">Measurement</label><select id="menu-measure3">'
        '<option value="" selected>Choose…</option>'
        '<option value="measure-0">Measure A</option><option value="measure-1">Measure B</option>'
        '<option value="measure-2">Measure C</option><option value="measure-all">Measure all three</option>'
        '<option value="three-reset">Reset</option></select></div>'
        '</div>'
        '<div class="control-readouts"><p class="control-line">'
        '<span class="measure-result" id="measure-result">Measure A, B, C or all three: the outcome appears'
        ' here.</span><span class="measure-tally" id="measure-tally">No measurements yet.</span></p></div>'
        '<noscript><p class="qubit-noscript">The page opens on the state with two visible planes. Enable'
        ' JavaScript to turn and resize the eight arrows, choose the reference qubit, apply gates, and'
        ' measure.</p></noscript></section>'

        '<section class="two-views" aria-labelledby="views-heading">'
        '<h2 class="sr-only" id="views-heading">The same state in two pictures</h2>'
        '<div class="view-grid">'
        '<section class="view-column" aria-labelledby="phasor-heading">'
        '<p class="eyebrow">Amplitudes</p>'
        '<h3 class="view-heading" id="phasor-heading">Eight arrows in one plane</h3>'
        '<figure class="phasor-figure">' + three_phasor_svg(state) +
        '<figcaption>Eight arrows, one per computational amplitude: length is the magnitude and the angle'
        ' is the phase. Drag an arrow to set both, or use ←/→ to turn it and ↑/↓ to resize it. Edits can'
        ' leave the arrows unnormalized; Normalize divides all eight by √(Σ|c|²).</figcaption></figure>'
        '<div class="phasor-panel">'
        '<div class="phasor-actions">'
        '<button type="button" class="ph-normalize" id="normalize-arrows" aria-describedby="state-norm">'
        'Normalize</button>'
        '<p class="ph-norm" id="state-norm">Σ|c|² = 1.000 — the arrows are normalized.</p>'
        '</div>'
        '<div class="amplitude-strip" role="group" aria-label="Magnitude and phase per basis state">'
        + dials + '</div>'
        '<p class="amp-caption">Arrow length is the magnitude, its angle the phase. A drag sets both;'
        ' ←/→ turns an arrow and ↑/↓ resizes it.</p>'
        '<p class="sr-only" id="state-status" role="status" aria-live="polite"></p>'
        '</div></section>'

        '<section class="view-column" aria-labelledby="planes-heading">'
        '<p class="eyebrow">Relative state</p>'
        '<h3 class="view-heading" id="planes-heading">Two planes in one sphere</h3>'
        '<figure class="schmidt-figure planes-figure">' + three_planes_svg(state) +
        '<figcaption>The reference qubit stays the pair of kets |0⟩ and |1⟩. For each value, the other two'
        ' qubits form a two-qubit state, drawn here in its own Schmidt bases: one axis at unit length and'
        ' the other carrying the branch amplitudes cos θ and sin θ, and the two axes span that branch\'s'
        ' plane. Each plane is filled where it cuts the sphere, and its half nearer the camera is drawn'
        ' stronger, so the two discs read as crossing rather than stacked and the overlap comes out lighter'
        ' where the far plane shows through; the fill also fades with the branch probability. When a'
        ' branch\'s axes line up — as they do in GHZ and W — the plane collapses and is hidden. The violet'
        ' diameter is where the two planes cross; its ends are |+û⟩ and |−û⟩, so the diameter names one'
        ' basis of a single qubit. Drag the sphere, or focus it and use the arrow keys, to look from'
        ' another side.'
        '</figcaption></figure>'
        '<div class="schmidt-panel">'
        '<div class="plane-view">'
        '<button type="button" class="ph-normalize" id="reset-view">Reset view</button>'
        '<button type="button" class="ph-normalize" id="look-along-u">Look along û</button>'
        '<p class="plane-hint">Drag the sphere to orbit it; with the sphere focused, ←/→ turns the view and'
        ' ↑/↓ raises or lowers it. Each plane is filled where it cuts the sphere, and the stronger half is'
        ' the half in front of the other plane.</p>'
        '</div>'
        '<div class="plane-legend" aria-hidden="true">'
        '<p class="plane-key"><span class="plane-swatch branch-0"></span>'
        '<span id="plane-legend-0">|0⟩<sub>A</sub> branch</span></p>'
        '<p class="plane-key"><span class="plane-swatch branch-1"></span>'
        '<span id="plane-legend-1">|1⟩<sub>A</sub> branch</span></p>'
        '<p class="plane-key"><span class="plane-swatch is-shared"></span>'
        '<span>shared basis |+û⟩, |−û⟩</span></p>'
        '</div>'
        '<p class="schmidt-formula" id="plane-expansion">' + expansion + '</p>'
        '<table class="plane-table"><caption class="sr-only">The two reference branches</caption>'
        '<thead><tr><th scope="col">Quantity</th><th scope="col" id="plane-head-0">|0⟩<sub>A</sub></th>'
        '<th scope="col" id="plane-head-1">|1⟩<sub>A</sub></th></tr></thead><tbody>'
        + rows +
        '</tbody></table>'
        + formulas +
        f'<p class="plane-angle" id="plane-angle">{angle_text}</p>'
        f'<p class="plane-angle" id="plane-basis">{basis_text}</p>'
        '<p class="slider-hint">The two planes are alternatives, not a simultaneous picture: measuring the'
        ' reference realizes one branch with probability w₀ or w₁. Changing the reference qubit re-cuts the'
        ' same state and gives two different planes. Drag the sphere to see them from another side — edge on,'
        ' a plane shows as a line.</p>'
        '<p class="sr-only" id="plane-summary">Two Schmidt planes, one per reference branch.</p>'
        '</div></section>'
        '</div></section>'

        '<section class="qubit-reading" id="explanation"><h2>Why one qubit is the reference</h2>'
        '<p>Group the eight amplitudes by the value of one qubit and the state separates into two pieces:</p>'
        r'<p>\[|\psi\rangle = |0\rangle|\phi_0\rangle + |1\rangle|\phi_1\rangle .\]</p>'
        r'<p>Nothing is approximated — \(|\phi_0\rangle\) and \(|\phi_1\rangle\) are ordinary, unnormalised'
        ' two-qubit states, and their lengths are the probabilities of the two values:'
        r' \(w_0 = \langle\phi_0|\phi_0\rangle\) and \(w_1 = \langle\phi_1|\phi_1\rangle\), with'
        r' \(w_0 + w_1 = 1\). The reference qubit contributes only its two kets; everything else lives in the'
        ' other two qubits.</p>'
        r'<p>Each branch is then a problem this toolkit already solves. Divide \(|\phi_r\rangle\) by'
        r' \(\sqrt{w_r}\) to normalise it, and it has a Schmidt form</p>'
        r'<p>\[|\phi_r\rangle = \sqrt{w_r}\left(\cos\theta_r\,|{+}p_r\rangle|{+}q_r\rangle'
        r' + e^{i\chi_r}\sin\theta_r\,|{-}p_r\rangle|{-}q_r\rangle\right),\]</p>'
        '<p>with its own axes for the two remaining qubits. Those axes are different in the two branches in'
        ' general, which is the point of the picture: the same pair of qubits is described by a different'
        ' pair of local bases depending on what the reference reads.</p>'
        '<h2>The two planes</h2>'
        '<p>Two axes through the origin span a plane, so each branch contributes one plane to the sphere.'
        ' The plane is filled where it cuts the sphere — a disc seen at an angle — so the whole shared'
        ' diameter lies visibly inside both planes rather than running off their edges. The disc is split'
        r' along that diameter into the half nearer the camera and the half beyond it, and the nearer half'
        ' is drawn stronger: where the two discs overlap, the stronger piece is the plane in front. Filling'
        ' strength also tracks the branch probability, so the branch that is less likely fades.</p>'
        '<p>The two planes generally differ, and that is the point of the picture: the same pair of qubits'
        ' is described by a different pair of local bases depending on what the reference reads. A plane'
        ' needs two independent directions, so when a branch\'s axes line up — GHZ, W, and any product'
        ' branch — there is no plane to fill, and it is hidden rather than drawn as a stray line.</p>'
        '<h2>The intersection line</h2>'
        '<p>Both planes pass through the centre of the sphere, and two distinct planes through one point'
        r' always meet in a line. With unit normals \(\hat n_r = \hat p_r \times \hat q_r\), the line runs'
        r' along \(\hat u = \hat n_0 \times \hat n_1\), and the planes open at the dihedral angle'
        r' \(\alpha = \arccos\lvert \hat n_0 \cdot \hat n_1\rvert\).</p>'
        '<h2>The basis the line defines</h2>'
        r'<p>Every diameter of the Bloch sphere is a basis: its two ends are the \(\pm 1\) eigenstates of'
        r' \(\hat u \cdot \vec{\sigma}\), so \(\hat u\) names the orthonormal pair'
        r' \(\{|{+}\hat u\rangle, |{-}\hat u\rangle\}\). This one sphere carries both non-reference qubits,'
        ' so that is a single basis read on either of them — the one basis the picture adapts to both'
        ' branches at once. Lying in both planes is what buys it:</p>'
        r'<p>\[\hat u \in \Pi_0 \cap \Pi_1 \quad\Longleftrightarrow\quad'
        r' \hat p_r, \hat q_r \in \operatorname{span}(\hat u, \hat m_r) \quad (r = 0, 1).\]</p>'
        r'<p>Read it in the frame whose \(z\) axis is \(\hat u\). No Schmidt axis then winds around'
        r" \(\hat u\): each branch's two axes lie on one meridian, and inside a branch they differ only"
        r' in how far they lean away from \(\hat u\). All the azimuthal disagreement in the picture'
        r' therefore collapses into a single meridian angle per branch, and the gap between those two'
        r' meridian angles is exactly the dihedral angle. The readout under the sphere names the two lean'
        r' angles \(\lambda_r\) and \(\mu_r\) for each branch, and the twist \(\alpha\).</p>'
        r"<p>That is the line's significance for the three-qubit state. The reference cut produces two"
        ' branches with two Schmidt frames, and those frames disagree in exactly two ways: by their lean'
        r' along a common axis, and by a twist around it. The line is that common axis — the only direction'
        r' on which both branches agree — and \(\alpha\) is the residue of the twist, the part no change of'
        r' frame removes. Rotating about \(\hat u\) by \(\alpha\) carries one Schmidt plane exactly onto'
        r' the other, so \(\hat u\) is the axis that relates them. The two frames coincide only when'
        r' \(\alpha = 0\) — the product, GHZ and W cases, where the planes already lie on top of'
        ' each other.</p>'
        r'<p>The line also ignores which of the two non-reference qubits you call the first: exchanging'
        r' them swaps \(\hat p_r\) with \(\hat q_r\) and so flips both normals, and flipping both vectors'
        r' leaves a cross product unchanged. The axes and the normals move under that exchange;'
        r' \(\hat u\), and with it \(\alpha\), does not.</p>'
        '<p><em>Look along û</em> turns the camera down the shared axis. Seen end on, the two planes'
        ' flatten into two straight lines through the centre, crossing at the dihedral angle: the meridians'
        ' themselves.</p>'
        '<p>Three qualifications. When the planes coincide, the intersection is the whole shared plane, so'
        ' no single diameter is distinguished and every basis inside that plane qualifies. A maximally'
        r' entangled branch \((\theta_r = 45^\circ)\) has no unique Schmidt bases, so its plane, and the'
        ' line through it, inherit that freedom of convention. And the line belongs to this picture, which'
        ' identifies the Bloch spheres of the two non-reference qubits: a local unitary on either qubit'
        ' turns the planes and the line, while the branch weights and the Schmidt angles stay put.</p>'
        '<h2>Both branches in the shared basis</h2>'
        r'<p>Write both branches in the basis the diameter names, \(\{|{+}\hat u\rangle,'
        r' |{-}\hat u\rangle\}\) on each of the two remaining qubits. Neither branch keeps two terms:'
        r' all four amplitudes survive, because \(\hat u\) is not a Schmidt axis of either qubit unless the'
        r' leans vanish. Nothing physical is lost — a change of local basis is a local unitary, so the'
        r' Schmidt values and every entanglement measure stay exactly where they were — but the Schmidt'
        r' coefficients no longer sit on the diagonal.</p>'
        r'<p>What the shared basis does remove is azimuthal freedom. In the frame whose \(z\) axis is'
        r" \(\hat u\), a branch's two Schmidt axes lie on one great circle through \(\hat u\) — the same"
        r' meridian, up to relabelling \(|{\pm}\hat q\rangle\), which swaps those two basis vectors and'
        r' nothing more. So each local frame is a rotation about the single axis'
        r' \(\hat k_r = \hat u \times \hat m_r\), by the lean \(\lambda_r\) on the first qubit and'
        r' \(\mu_r\) on the second, and between branches that axis turns by \(\alpha\) about'
        r' \(\hat u\). Two branches that started with four axis angles each are left with four leans and'
        ' one twist.</p>'
        r'<p>This is also why the line is a basis and not a Schmidt basis. A plane needs two independent'
        r' axes, so \(\hat u\) could be the Schmidt axis of both qubits at once only when both axes'
        r' collapse onto it — a product branch, with no plane left to draw. A product basis in which both'
        r' branches are Schmidt-diagonal therefore exists only where the planes coincide, and there the'
        ' diameter stops being distinguished in the first place.</p>'
        '<h2>What this cut does not show</h2>'
        '<p>Three qubits have more than one way to be entangled, and a single reference sees only one cut.'
        ' Choose A and the branches are states of B and C; choose B and the same amplitudes regroup into'
        ' states of A and C. The three cuts carry different information — GHZ is entangled across every'
        ' cut, while W concentrates its entanglement differently — so switching the reference is not a'
        ' cosmetic change but a different question asked of the same state.</p>'
        '<h2>Things to try</h2><ol class="qubit-try">'
        '<li>Start on <strong>Two planes</strong>: the two branches carry different Schmidt frames, so the'
        ' two planes sit at an angle. Drag the sphere and the view turns with it.</li>'
        '<li>Switch the <strong>Reference qubit</strong> to B without touching the state: the same eight'
        ' amplitudes are regrouped, the branch probabilities change, and both planes move.</li>'
        '<li>Load <strong>GHZ</strong>: each branch is a product state along the same axis, so the four'
        ' endpoints are collinear and the planes vanish. The reference qubit is perfectly correlated with'
        ' the other two, which is what a plane with no area means here.</li>'
        '<li>Load <strong>W</strong>: the branches have probabilities 1/3 and 2/3, so the legend and the'
        ' table show unequal weights even before any plane appears.</li>'
        '<li>Press <strong>Look along û</strong>: the camera turns down the shared axis, and both planes'
        ' flatten into straight lines crossing at the dihedral angle.</li>'
        '<li>Rotate until a plane is edge on: it thins to a line, then widens again on the far side.</li>'
        '<li>Drag one of the eight arrows, then Normalize: the branch probabilities and both planes follow'
        ' the amplitudes you set.</li>'
        '</ol>'
        '<p class="qubit-note">This model follows pure states only, and measurement uses your browser\'s'
        ' random number generator. A mixed three-qubit state needs a density matrix and a different notion'
        ' of Schmidt form, which this tool does not attempt.</p></section>')
    shell('tools/three-qubit.html', 'Three-qubit state visualizer',
          'A three-qubit state as eight arrows in one plane, and the same state cut by a reference qubit'
          ' into two two-qubit branches, each drawn as a Schmidt plane on one Bloch sphere.',
          body, assets='<link rel="stylesheet" href="tools.css"><script defer src="three-qubit.js"></script>')


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
    render_three_qubit(root, shell)
