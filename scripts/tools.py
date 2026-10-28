"""Render the Tools section: the catalogue of interactive models and the single-qubit Bloch sphere.

The geometry of the sphere is computed here so the page is a complete drawing without JavaScript;
`tools/single-qubit.js` re-projects the state vector with the camera basis emitted on the <svg>.
"""
from html import escape
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


def project(point):
    x, y, z = point
    return (CENTER + RADIUS * (x * RIGHT[0] + y * RIGHT[1] + z * RIGHT[2]),
            CENTER - RADIUS * (x * UP[0] + y * UP[1] + z * UP[2]))


def facing(point):
    """True when a point on the sphere is on the hemisphere turned towards the camera."""
    return sum(a * b for a, b in zip(point, FORWARD)) < 0


def arcs(point_at, steps=180):
    """Split a closed 3D curve into the runs that are in front of, or behind, the sphere."""
    samples = []
    for index in range(steps):
        point = point_at(2 * math.pi * index / steps)
        samples.append((project(point), facing(point)))
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


def axis_label(point, text):
    x, y, z = point
    px, py = project((x, y, z))
    dx, dy = px - CENTER, py - CENTER
    distance = math.hypot(dx, dy) or 1.0
    anchor = 'middle'
    if dx / distance > 0.35:
        anchor = 'start'
    elif dx / distance < -0.35:
        anchor = 'end'
    return (f'<text class="bloch-axis-label" x="{CENTER + dx * 1.15:.1f}" y="{CENTER + dy * 1.15:.1f}"'
            f' text-anchor="{anchor}" dy="4">{text}</text>')


def state_geometry(theta_deg, phi_deg):
    """The state vector and its two dashed guides, as static SVG for the no-JavaScript drawing."""
    theta, phi = math.radians(theta_deg), math.radians(phi_deg)
    tip_3d = (math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta))
    tip, foot, origin = project(tip_3d), project((tip_3d[0], tip_3d[1], 0.0)), project((0.0, 0.0, 0.0))
    return (f'<line class="bloch-guide" id="bloch-radial" x1="{origin[0]:.1f}" y1="{origin[1]:.1f}"'
            f' x2="{foot[0]:.1f}" y2="{foot[1]:.1f}"/>'
            f'<line class="bloch-guide" id="bloch-drop" x1="{tip[0]:.1f}" y1="{tip[1]:.1f}"'
            f' x2="{foot[0]:.1f}" y2="{foot[1]:.1f}"/>'
            f'<line class="bloch-vector" id="bloch-arrow" x1="{origin[0]:.1f}" y1="{origin[1]:.1f}"'
            f' x2="{tip[0]:.1f}" y2="{tip[1]:.1f}"/>'
            f'<circle class="bloch-tip" id="bloch-tip" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="6"/>')


def bloch_svg():
    grid = []
    for visible, path in arcs(lambda t: (math.cos(t), math.sin(t), 0.0)):
        grid.append(f'<path class="bloch-equator" d="{path}"/>' if visible
                    else f'<path class="bloch-equator is-behind" d="{path}"/>')
    for longitude in (0.0, math.pi / 2):
        for visible, path in arcs(lambda t, p=longitude: (math.sin(t) * math.cos(p),
                                                          math.sin(t) * math.sin(p), math.cos(t))):
            grid.append(f'<path class="bloch-meridian" d="{path}"/>' if visible
                        else f'<path class="bloch-meridian is-behind" d="{path}"/>')
    axes = ''.join(f'<line class="bloch-axis" x1="{CENTER:.1f}" y1="{CENTER:.1f}"'
                   f' x2="{project(axis)[0]:.1f}" y2="{project(axis)[1]:.1f}"/>' for axis, _ in AXES)
    labels = ''.join(axis_label(axis, label) for axis, label in AXES)
    basis = ','.join(f'{value:.6f}' for value in (*RIGHT, *UP))
    return (f'<svg class="bloch" id="bloch" viewBox="0 0 400 400" role="img"'
            f' aria-labelledby="bloch-title bloch-desc" data-basis="{basis}">'
            '<title id="bloch-title">Bloch sphere for the current qubit state</title>'
            '<desc id="bloch-desc">The Bloch sphere with the state vector pointing at the north pole,'
            ' θ = 0°, φ = 0°. The probability of outcome 0 is 1.000 and of outcome 1 is 0.000.</desc>'
            f'<circle class="bloch-surface" cx="{CENTER:.1f}" cy="{CENTER:.1f}" r="{RADIUS:.1f}"/>'
            f'<g class="bloch-grid">{"".join(grid)}</g>'
            f'<g class="bloch-axes">{axes}{labels}</g>'
            f'{state_geometry(0, 0)}'
            f'<circle class="bloch-origin" cx="{CENTER:.1f}" cy="{CENTER:.1f}" r="2.5"/>'
            '</svg>')


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
               '<input id="theta" type="range" min="0" max="180" step="1" value="0" aria-describedby="theta-hint">'
               '<output id="theta-value" for="theta">0°</output></div>'
               '<p class="slider-hint" id="theta-hint">0° points at |0⟩, 180° at |1⟩, and 90° puts the state on'
               ' the equator.</p>'
               '<div class="slider-row"><label for="phi">φ <span class="slider-note">azimuth</span></label>'
               '<input id="phi" type="range" min="0" max="360" step="1" value="0">'
               '<output id="phi-value" for="phi">0° (0.00π)</output></div>'
               '<p class="slider-hint">φ turns the state around the vertical axis; on its own it never changes'
               ' P(0).</p></fieldset>')
    presets = ('<fieldset class="qubit-group"><legend>Prepare a state</legend><div class="qubit-buttons">'
               + ''.join(f'<button type="button" data-preset data-theta="{theta}" data-phi="{phi}">{label}</button>'
                         for label, theta, phi in PRESETS)
               + '</div></fieldset>')
    gates = ('<fieldset class="qubit-group"><legend>Apply a gate</legend><div class="qubit-buttons">'
             + ''.join(f'<button type="button" data-gate="{name}" title="{hint}">{name}</button>'
                       for name, hint in GATES)
             + '</div><p class="slider-hint">Gates act on the current state, so the same button has a different'
             ' effect at different points. The default order is X, Y, Z, H, S, T; H twice returns the state to'
             ' where it started.</p></fieldset>')
    measurement = ('<fieldset class="qubit-group"><legend>Measurement</legend><div class="qubit-buttons">'
                   '<button type="button" id="measure">Measure qubit</button>'
                   '<button type="button" id="reset" title="Return to |0⟩ and clear the counts">Reset</button>'
                   '</div><p class="measure-result" id="measure-result">A measurement in the computational basis'
                   ' returns 0 or 1 with probabilities |α|² and |β|², and leaves the qubit in the state it'
                   ' found.</p><p class="measure-tally" id="measure-tally">No measurements yet.</p>'
                   '<p class="sr-only" id="state-status" role="status" aria-live="polite"></p></fieldset>')
    tool_body = ('<header class="editorial-intro compact qubit-intro"><p class="eyebrow">Tools / Single-qubit state</p>'
                 '<h1>One qubit, one sphere.</h1>'
                 '<p>A pure state of a single qubit has two physical angles. Drag the arrow on the Bloch sphere, or'
                 ' set θ and φ directly, then apply a gate or measure the qubit and watch the amplitudes follow.</p>'
                 '</header>'
                 '<section class="qubit-lab" aria-labelledby="lab-heading">'
                 '<h2 class="sr-only" id="lab-heading">Single-qubit state explorer</h2>'
                 f'<figure class="bloch-figure">{bloch_svg()}'
                 '<figcaption>Drag anywhere on the sphere to point the state vector. Keyboard users can set both'
                 ' angles with the sliders.</figcaption></figure>'
                 '<div class="qubit-panel"><div class="qubit-state"><p class="qubit-kicker">Current state</p>'
                 '<p class="qubit-ket" id="state-ket">1.000|0⟩</p><dl class="qubit-values">'
                 '<div><dt>α</dt><dd id="state-alpha">1.000 + 0.000i</dd></div>'
                 '<div><dt>β</dt><dd id="state-beta">0.000 + 0.000i</dd></div>'
                 '<div><dt>P(0)</dt><dd id="prob-0">1.000</dd></div>'
                 '<div><dt>P(1)</dt><dd id="prob-1">0.000</dd></div></dl>'
                 '<div class="qubit-meters">'
                 '<p class="meter-label"><span>Outcome 0</span><span class="meter-track">'
                 '<span class="meter-fill" id="bar-0" style="width:100%"></span></span></p>'
                 '<p class="meter-label"><span>Outcome 1</span><span class="meter-track">'
                 '<span class="meter-fill" id="bar-1" style="width:0%"></span></span></p>'
                 '</div></div>'
                 + sliders + presets + gates + measurement +
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
                 r' \(\chi\) and three angles \(a\), \(b\), \(c\):</p>'
                 r'<p>\[U=e^{i\chi}\begin{pmatrix}e^{-i(a+c)/2}\cos\frac{b}{2} & -e^{-i(a-c)/2}\sin\frac{b}{2}\\'
                 r' e^{i(a-c)/2}\sin\frac{b}{2} & e^{i(a+c)/2}\cos\frac{b}{2}\end{pmatrix}=e^{i\chi}R_z(a)\,R_y(b)\,R_z(c),\]</p>'
                 r'<p>where \(R_z(a)=e^{-iaZ/2}\) and \(R_y(b)=e^{-ibY/2}\) are rotations of the arrow about the'
                 r' \(z\) and \(y\) axes. So every gate is a turn about \(z\), a turn about \(y\) and another turn'
                 r' about \(z\). Equivalently, every gate is one rotation by an angle \(\omega\) about a single unit'
                 r' axis \(\hat n=(n_x,n_y,n_z)\):</p>'
                 r'<p>\[U=e^{i\chi}\Bigl(\cos\tfrac{\omega}{2}\,I-i\sin\tfrac{\omega}{2}\,(n_xX+n_yY+n_zZ)\Bigr),\]</p>'
                 r'<p>and its effect on the sphere is exactly that: the arrow turns by \(\omega\) about'
                 r' \(\hat n\). The phase \(e^{i\chi}\) multiplies \(\alpha\) and \(\beta\) together and never'
                 r' moves the arrow, which is why the sphere needs only three of the four numbers. The half angles'
                 r' are the same ones as in the amplitudes: a full turn, \(\omega=2\pi\), gives \(-I\).</p>'
                 r'<p>The six buttons above are special cases. X, Y and Z are half-turns, \(\omega=\pi\), about the'
                 r' \(x\), \(y\) and \(z\) axes, each times a phase \(i\). H is \(i\) times a half-turn about the'
                 r' axis \((1,0,1)/\sqrt2\), halfway between \(x\) and \(z\), which is why it swaps |0⟩ and |+⟩. S'
                 r' and T are quarter- and eighth-turns about \(z\): \(S=e^{i\pi/4}R_z(\pi/2)\) and'
                 r' \(T=e^{i\pi/8}R_z(\pi/4)\).</p>'
                 '<h2>Things to try</h2><ol class="qubit-try">'
                 '<li>Set θ = 30° and compare α with cos 15° = 0.966 and β with sin 15° = 0.259.</li>'
                 '<li>From |0⟩ press H: the arrow lands on |+⟩ with probabilities 0.500 and 0.500. Press S: the'
                 ' arrow moves to |+i⟩ and P(0) does not move.</li>'
                 '<li>From |0⟩ press X to reach |1⟩, then H to reach |−⟩. Both |+⟩ and |−⟩ measure 0 half the'
                 ' time, so the probabilities alone cannot tell them apart.</li>'
                 '<li>Prepare |+⟩ and press Measure: the arrow jumps to |0⟩ or |1⟩ — the collapse — and the'
                 ' probabilities become certain. Press |+⟩ and Measure again a few times to watch the counts'
                 ' approach 50 / 50.</li>'
                 '<li>Drag slowly near the north pole and quickly near the equator: the half angle compresses the'
                 ' whole sphere into the amplitudes.</li></ol>'
                 '<p class="qubit-note">This model shows pure states only. A noisy qubit sits inside the sphere,'
                 ' where the arrow is shorter, and needs a density-matrix view that this tool does not yet'
                 ' provide. Measurements here use your browser\'s random number generator, so a short run of'
                 ' outcomes can look surprising: that is statistics, not a bias.</p></section>')
    shell('tools/single-qubit.html', 'Single-qubit state visualizer',
          'Explore a single qubit on the Bloch sphere: drag the state vector, apply gates, and measure the resulting probabilities.',
          tool_body, assets='<link rel="stylesheet" href="tools.css"><script defer src="single-qubit.js"></script>')
