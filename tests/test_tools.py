"""The Tools section: catalogue integrity and the geometry of both state explorers."""
import copy
import cmath
import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import tools
import schmidt

class ControlAudit(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.labels, self.buttons, self.presets, self.inputs = set(), [], [], []
        self.axes, self.axis_line, self.svgs = [], None, []
        self.axis_handle, self.axis_label = None, None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'label' and a.get('for'): self.labels.add(a['for'])
        if tag == 'input': self.inputs.append(a)
        if tag == 'button' and 'data-gate' in a: self.buttons.append(a['data-gate'])
        if tag == 'button' and 'data-preset' in a: self.presets.append((a['data-theta'], a['data-phi']))
        if tag == 'button' and 'data-axis-theta' in a: self.axes.append((a['data-axis-theta'], a['data-axis-phi']))
        if tag == 'line' and a.get('id') == 'bloch-naxis': self.axis_line = a
        if tag == 'circle' and a.get('id') == 'bloch-nhandle': self.axis_handle = a
        if tag == 'text' and a.get('id') == 'bloch-nlabel': self.axis_label = a
        if tag == 'svg' and 'data-basis' in a: self.svgs.append(a)

class TwoQubitAudit(HTMLParser):
    """Collects the vector groups, the five menus and the readout cells of the two-qubit page."""
    def __init__(self, text):
        super().__init__()
        self.svgs, self.groups = [], []
        self.menus = {}
        self.menu = None
        self.lines, self.texts = {}, {}
        self.element = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'svg' and a.get('class') == 'phasor': self.svgs.append(a)
        if tag == 'g' and 'ph-vec' in a.get('class', '').split(): self.groups.append(a)
        if tag == 'select' and a.get('id'): self.menu = a['id']; self.menus[self.menu] = []
        if tag == 'option' and self.menu: self.menus[self.menu].append(a.get('value', ''))
        if tag in ('line', 'text') and a.get('id'): self.lines[a['id']] = (tag, a)
        self.element = a.get('id') if tag == 'text' else None

    def handle_endtag(self, tag):
        if tag == 'select': self.menu = None

    def handle_data(self, text):
        if self.element and text.strip(): self.texts[self.element] = text


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'content/tools.json').read_text())

    def test_every_listed_tool_is_published_and_linked(self):
        tools.validate(ROOT, self.data)
        index = (ROOT / 'tools/index.html').read_text()
        sitemap = (ROOT / 'sitemap.xml').read_text()
        for tool in self.data['tools']:
            self.assertTrue((ROOT / tool['href']).is_file(), tool['href'])
            self.assertIn(tool['href'].split('/')[-1], index)
            self.assertIn(tool['href'].removesuffix('index.html'), sitemap)

    def test_rejects_escaped_or_duplicate_tools(self):
        escaped = copy.deepcopy(self.data)
        escaped['tools'][0]['href'] = '../../index.html'
        with self.assertRaises(ValueError): tools.validate(ROOT, escaped)
        duplicate = copy.deepcopy(self.data)
        duplicate['tools'].append(dict(duplicate['tools'][0]))
        with self.assertRaises(ValueError): tools.validate(ROOT, duplicate)

    def test_bloch_camera_is_orthonormal_and_orients_the_axes(self):
        basis = [*tools.RIGHT, *tools.UP]
        dot = lambda a, b: sum(x * y for x, y in zip(a, b))
        self.assertAlmostEqual(dot(tools.RIGHT, tools.RIGHT), 1)
        self.assertAlmostEqual(dot(tools.UP, tools.UP), 1)
        self.assertAlmostEqual(dot(tools.RIGHT, tools.UP), 0)
        centre = tools.project((0, 0, 0))
        zero, one, plus, minus, plus_i = (tools.project(v) for v in
                                          ((0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0, 1, 0)))
        self.assertAlmostEqual(centre[0], tools.CENTER)
        self.assertAlmostEqual(centre[1], tools.CENTER)
        self.assertLess(zero[1], centre[1])          # |0⟩ above the centre
        self.assertGreater(one[1], centre[1])        # |1⟩ below it
        self.assertGreater(plus[0], centre[0])       # |+⟩ to the right
        self.assertLess(minus[0], centre[0])
        self.assertLess(plus_i[1], plus[1])          # |+i⟩ rises above |+⟩
        self.assertEqual(len(basis), 6)

    def test_explorer_controls_match_the_model(self):
        page = (ROOT / 'tools/single-qubit.html').read_text()
        audit = ControlAudit(page)
        self.assertEqual(sorted(audit.buttons), sorted(name for name, _ in tools.GATES))
        self.assertEqual(audit.presets, [(str(theta), str(phi)) for _, theta, phi in tools.PRESETS])
        for field in audit.inputs:
            self.assertIn(field['id'], audit.labels, field['id'])
        self.assertEqual(len(audit.svgs), 1)
        self.assertEqual(audit.svgs[0]['aria-labelledby'], 'bloch-title bloch-desc')
        basis = [float(value) for value in audit.svgs[0]['data-basis'].split(',')]
        self.assertEqual(len(basis), 6)

    def test_two_qubit_reference_maths(self):
        root2 = 1 / 2 ** 0.5
        bell = [root2, 0, 0, root2]
        table, concurrence, plus, minus = tools.two_qubit_observables(bell)
        self.assertAlmostEqual(concurrence, 1)
        self.assertAlmostEqual(plus, root2)
        self.assertAlmostEqual(minus, root2)
        self.assertEqual([round(table[i][i], 6) for i in (1, 2, 3)],
                         [1, -1, 1])                                  # T = diag(1, -1, 1)
        self.assertEqual([round(value, 6) for value in table[0]], [1, 0, 0, 0])
        for mu in range(1, 4):                                        # every marginal vanishes
            self.assertAlmostEqual(table[mu][0], 0)
        product, c_product, *_ = tools.two_qubit_observables([1, 0, 0, 0])
        self.assertAlmostEqual(c_product, 0)
        self.assertEqual([round(product[i][i], 6) for i in range(4)], [1, 0, 0, 1])

    def test_needle_is_the_concurrence_for_every_bell_state(self):
        root2 = 1 / 2 ** 0.5
        for state, concurrence, direction in (([root2, 0, 0, root2], 1, 0),
                                              ([root2, 0, 0, -root2], 1, 180),
                                              ([0, root2, root2, 0], 1, 180),
                                              ([0, root2, -root2, 0], 1, 0),
                                              ([0.5, 0.5, 0.5, 0.5], 0, None)):
            needle = 2 * (state[0] * state[3] - state[1] * state[2])
            self.assertAlmostEqual(abs(needle), tools.concurrence_of(state), places=9)
            self.assertAlmostEqual(tools.concurrence_of(state), concurrence, places=9)
            if direction is None:
                self.assertAlmostEqual(abs(needle), 0, places=9)
            else:
                self.assertAlmostEqual(cmath.phase(needle) * 180 / math.pi % 360, direction, places=6)

    def test_phasor_geometry_puts_the_unit_circle_at_full_amplitude(self):
        self.assertEqual(tools.phasor_tip(0, 0), (tools.PHASOR_CENTER, tools.PHASOR_CENTER))
        x, y = tools.phasor_tip(1, 0)
        self.assertAlmostEqual(x - tools.PHASOR_CENTER, tools.PHASOR_RADIUS)
        self.assertAlmostEqual(y, tools.PHASOR_CENTER)
        x, y = tools.phasor_tip(0.5, 90)
        self.assertAlmostEqual(x, tools.PHASOR_CENTER)
        self.assertAlmostEqual(tools.PHASOR_CENTER - y, tools.PHASOR_RADIUS / 2)

    def test_two_qubit_page_matches_its_static_state(self):
        page = (ROOT / 'tools/two-qubit.html').read_text()
        audit = TwoQubitAudit(page)
        self.assertEqual(len(audit.svgs), 1)
        self.assertEqual([group['data-index'] for group in audit.groups], ['0', '1', '2', '3'])
        names = [name for name, _ in tools.GATES]
        self.assertEqual(audit.menus['menu-state'], [''] + [key for key, _ in tools.TWO_PRESETS])
        self.assertEqual(audit.menus['menu-gate-a'], [''] + names)
        self.assertEqual(audit.menus['menu-gate-b'], [''] + names)
        self.assertEqual(audit.menus['menu-gate-two'], ['', 'CNOT', 'CZ', 'SWAP'])
        self.assertEqual(audit.menus['menu-measure'],
                         ['', 'measure-a', 'measure-b', 'measure-both', 'two-reset'])
        self.assertEqual(audit.texts.get('ph-vec-00-label'), '|00⟩')
        line = audit.lines['ph-vec-00'][1]
        self.assertEqual(round(float(line['x2']), 1), 376.0)   # full amplitude on the real axis
        self.assertEqual(round(float(line['y2']), 1), 220.0)
        for index in (1, 2, 3):                                 # the other three are empty
            self.assertIn('is-empty', audit.groups[index]['class'])
        # <option> holds text only, so the preset labels must not smuggle markup into the menu
        self.assertNotIn('<sup>', page.split('id="menu-state"')[1].split('</select>')[0])
        self.assertIn('Φ⁺', page.split('id="menu-state"')[1].split('</select>')[0])

    def test_two_qubit_static_readouts_agree_with_the_reference(self):
        page = (ROOT / 'tools/two-qubit.html').read_text()
        _, concurrence, plus, minus = tools.two_qubit_observables([1, 0, 0, 0])
        # The page keeps no summary strip: the needle, the dials and the Schmidt panel carry the readouts.
        for retired in ('state-ket', 'inv-concurrence', 'inv-needle', 'inv-schmidt', 'inv-type', 'bar-c'):
            self.assertNotIn(f'id="{retired}"', page)
        self.assertIn(f'id="schmidt-lambda-0">{(1 + math.sqrt(1 - concurrence ** 2)) / 2:.3f}<', page)
        self.assertIn(f'id="schmidt-lambda-1">{(1 - math.sqrt(1 - concurrence ** 2)) / 2:.3f}<', page)
        for key in ('00', '01', '10', '11'):
            self.assertIn(f'id="amp-mag-{key}"', page)
        self.assertIn('id="ph-needle"', page)
        self.assertIn('id="ph-p1"', page)

    def test_phasor_disc_carries_the_concurrence_heat_map(self):
        page = (ROOT / 'tools/two-qubit.html').read_text()
        self.assertIn('<radialGradient id="ph-heat"', page)
        self.assertIn('class="ph-heat" id="ph-heat-disc" cx="220.0" cy="220.0" r="156.0" opacity="0"', page)
        offsets = re.findall(r'<stop offset="([^"]+)" style="stop-color:var\(--heat-(\d)\)"', page)
        self.assertEqual([offset for offset, _ in offsets], ['0', '.25', '.5', '.75', '1'])
        self.assertEqual([index for _, index in offsets], ['0', '1', '2', '3', '4'])
        # the contours mark the concurrence at a quarter, a half and three quarters of the needle's reach
        self.assertEqual(page.count('class="ph-contour"'), 3)
        self.assertEqual(re.findall(r'class="ph-contour"[^>]*r="([\d.]+)"', page), ['39.0', '78.0', '117.0'])
        css = (ROOT / 'tools/tools.css').read_text()
        self.assertIn('.ph-heat{fill:url(#ph-heat);transition:opacity .35s ease}', css)
        self.assertIn('--heat-4:rgba(147,77,54,.32)', css)
        self.assertIn('html[data-theme=dark] .phasor{', css)
        # the strength follows the current concurrence, so the disc cools to plain paper at C = 0
        script = (ROOT / 'tools/two-qubit.js').read_text()
        self.assertIn('heat: byId(\'ph-heat-disc\')', script)
        self.assertIn('parts.heat.style.opacity = c.toFixed(3);', script)

    def test_two_qubit_page_draws_the_schmidt_bases_statically(self):
        page = (ROOT / 'tools/two-qubit.html').read_text()
        form = schmidt.schmidt_form([1, 0, 0, 0])
        self.assertEqual(form.theta_deg, 0)
        plus, minus = tools.project(form.axis_a), tools.project(tuple(-v for v in form.axis_a))
        line = re.search(r'<line class="schmidt-a-line" id="schmidt-a-line" x1="([-\d.]+)" y1="([-\d.]+)"'
                         r' x2="([-\d.]+)" y2="([-\d.]+)"', page)
        self.assertIsNotNone(line)
        self.assertEqual(line.groups(), (f'{minus[0]:.1f}', f'{minus[1]:.1f}',
                                         f'{plus[0]:.1f}', f'{plus[1]:.1f}'))
        # Qubit B's leading arm is cos θ = 1 here, so it reaches the surface; the trailing arm is gone.
        origin = tools.project((0.0, 0.0, 0.0))
        b_line = re.search(r'<line class="schmidt-b-line" id="schmidt-b-plus-line" x1="([-\d.]+)"'
                           r' y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"', page)
        self.assertIsNotNone(b_line)
        self.assertEqual(b_line.groups(), (f'{origin[0]:.1f}', f'{origin[1]:.1f}',
                                           f'{plus[0]:.1f}', f'{plus[1]:.1f}'))
        self.assertIn('class="schmidt-b-line is-empty" id="schmidt-b-minus-line"', page)
        for readout in ('id="schmidt-theta">0°<', 'id="schmidt-lambda-0">1.000<',
                        'id="schmidt-lambda-1">0.000<', 'id="schmidt-chi">—<',
                        'id="schmidt-formula">|ψ⟩ = 1.000 |+a⟩|+b⟩<'):
            self.assertIn(readout, page)

    def test_three_qubit_page_publishes_eight_arrows_and_two_planes(self):
        page = (ROOT / 'tools/three-qubit.html').read_text()
        for key in tools.THREE_KEYS:
            self.assertIn(f'id="ph3-group-{key}"', page)
            self.assertIn(f'id="amp3-mag-{key}"', page)
        self.assertEqual(page.count('class="plane-branch branch-'), 2)
        self.assertIn('id="planes-quad-0"', page)
        self.assertIn('id="planes-quad-1"', page)
        self.assertIn('id="menu-reference"', page)
        for index, _ in enumerate(tools.THREE_QUBITS):
            self.assertIn(f'<option value="{index}"', page)
        self.assertIn('id="normalize-arrows"', page)
        self.assertIn('src="three-qubit.js', page)

    def test_three_qubit_sphere_can_be_orbited(self):
        page = (ROOT / 'tools/three-qubit.html').read_text()
        self.assertIn('data-azimuth="32.0" data-elevation="17.0"', page)
        self.assertIn('id="planes-grid"', page)
        self.assertIn('id="planes-axes"', page)
        self.assertIn('id="reset-view"', page)
        self.assertIn('to orbit the view', page)
        script = (ROOT / 'tools/three-qubit.js').read_text()
        for token in ('function camera()', 'drawGrid', 'drawAxes', 'renderSphere', 'orbitTo', 'reset-view'):
            self.assertIn(token, script)
        # The camera starts from the angles the static drawing was built with.
        self.assertIn("sphere.dataset.azimuth", script)
        self.assertIn("sphere.dataset.elevation", script)

    def test_three_qubit_branches_match_the_schmidt_decomposition(self):
        state = tools.THREE_STATES['ghz']
        weight, form = tools.branch_form(state, 0, 0)
        self.assertAlmostEqual(weight, 0.5, places=9)
        self.assertAlmostEqual(form.theta_deg, 0.0, places=6)
        weight, form = tools.branch_form(state, 1, 1)
        self.assertAlmostEqual(weight, 0.5, places=9)
        self.assertAlmostEqual(form.theta_deg, 0.0, places=6)
        # A product branch leaves the other branch of |000⟩ empty.
        weight, form = tools.branch_form(tools.THREE_STATES['000'], 0, 1)
        self.assertAlmostEqual(weight, 0.0, places=9)
        self.assertIsNone(form)

    def test_three_qubit_planes_join_the_branch_endpoints(self):
        state = tools.THREE_STATES['planes']
        page = tools.three_planes_svg(state)
        for bit in (0, 1):
            _, form = tools.branch_form(state, 0, bit)
            cos = math.cos(math.radians(form.theta_deg))
            sin = math.sin(math.radians(form.theta_deg))
            corners = (tools.project(form.axis_a), tools.project(tuple(cos * v for v in form.axis_b)),
                       tools.project(tuple(-v for v in form.axis_a)),
                       tools.project(tuple(-sin * v for v in form.axis_b)))
            points = ' '.join(f'{x:.1f},{y:.1f}' for x, y in corners)
            self.assertIn(f'id="planes-quad-{bit}" points="{points}"', page)
        # Every named state has product branches along one axis, so its planes collapse.
        for name in ('ghz', 'w', '000'):
            flat = tools.three_planes_svg(tools.THREE_STATES[name])
            self.assertEqual(flat.count('class="plane-quad is-empty"'), 2)
        script = (ROOT / 'tools/three-qubit.js').read_text()
        for token in ('branchAmplitudes', 'branchForm', 'drawPlanes', 'menu-reference', 'planes-quad'):
            self.assertIn(token, script)

    def test_schmidt_sphere_joins_the_four_endpoints(self):
        # |00⟩ has coincident bases, so the quadrilateral has no area and starts hidden.
        page = (ROOT / 'tools/two-qubit.html').read_text()
        self.assertIn('class="schmidt-parallelogram is-empty" id="schmidt-parallelogram"', page)
        state = schmidt.schmidt_state(45, (0, 0, 1), (1, 0, 0), 0)
        page = tools.schmidt_svg(state)
        form = schmidt.schmidt_form(state)
        cos, sin = math.cos(math.radians(form.theta_deg)), math.sin(math.radians(form.theta_deg))
        corners = (tools.project(form.axis_a), tools.project(tuple(cos * v for v in form.axis_b)),
                   tools.project(tuple(-v for v in form.axis_a)),
                   tools.project(tuple(-sin * v for v in form.axis_b)))
        points = ' '.join(f'{x:.1f},{y:.1f}' for x, y in corners)
        self.assertIn(f'class="schmidt-parallelogram" id="schmidt-parallelogram" points="{points}"/>', page)
        script = (ROOT / 'tools/two-qubit.js').read_text()
        self.assertIn("sQuad: byId('schmidt-parallelogram')", script)
        self.assertIn('parts.sQuad.classList.toggle(\'is-empty\', area < 24)', script)
        css = (ROOT / 'tools/tools.css').read_text()
        self.assertIn('.schmidt-parallelogram{fill:var(--heading);fill-opacity:.06;', css)

    def test_schmidt_sphere_follows_the_model_for_any_state(self):
        state = tools.schmidt.schmidt_state(30, (0, 0, 1), (1, 0, 0), 40)
        page = tools.schmidt_svg(state)
        form = schmidt.schmidt_form(state)
        cos, sin = math.cos(math.radians(form.theta_deg)), math.sin(math.radians(form.theta_deg))
        centre = tools.project((0.0, 0.0, 0.0))
        b_plus = tools.project(tuple(cos * v for v in form.axis_b))
        b_minus = tools.project(tuple(-sin * v for v in form.axis_b))
        for line in (f'id="schmidt-b-plus-line" x1="{centre[0]:.1f}" y1="{centre[1]:.1f}"'
                     f' x2="{b_plus[0]:.1f}" y2="{b_plus[1]:.1f}"',
                     f'id="schmidt-b-minus-line" x1="{centre[0]:.1f}" y1="{centre[1]:.1f}"'
                     f' x2="{b_minus[0]:.1f}" y2="{b_minus[1]:.1f}"'):
            self.assertIn(line, page)
        self.assertIn('|+a⟩', page)
        self.assertIn('|−b⟩', page)

    def test_two_qubit_script_defines_the_same_controls(self):
        script = (ROOT / 'tools/two-qubit.js').read_text()
        for name, _ in tools.GATES:
            self.assertIn(name + ': [[', script)
        for key in ('CNOT', 'CZ', 'SWAP'):
            self.assertIn(key, script)
        for key, _ in tools.TWO_PRESETS:
            self.assertIn(key + ':', script.replace("'", ''))
        self.assertIn('fanOffsets', script)
        self.assertIn('ph-needle', script)
        # The display-basis switch is gone; the panel leads with Normalize instead.
        self.assertNotIn('BELL_LABELS', script)
        self.assertNotIn('basis-bell', script)
        page = (ROOT / 'tools/two-qubit.html').read_text()
        self.assertNotIn('Display basis', page)
        self.assertNotIn('id="basis-hint"', page)
        self.assertLess(page.index('id="normalize-arrows"'), page.index('class="amplitude-strip"'))
        for token in ('schmidtForm', 'drawSchmidt', 'schmidt-b-minus-label', 'schmidt-lambda-0',
                      'schmidt-formula', 'menu-state', 'menu-gate-a', 'menu-gate-two', 'menu-measure',
                      'drawDials'):
            self.assertIn(token, script)
        self.assertNotIn('data-gate-a', script)

    def test_two_qubit_arrows_can_be_resized_and_normalized(self):
        page = (ROOT / 'tools/two-qubit.html').read_text()
        self.assertIn('id="normalize-arrows" aria-describedby="state-norm">Normalize</button>', page)
        self.assertIn('id="state-norm">Σ|c|² = 1.000 — the arrows are normalized.<', page)
        self.assertIn('↑/↓', page)
        script = (ROOT / 'tools/two-qubit.js').read_text()
        for token in ('normalize-arrows', 'state-norm', 'MIN_LENGTH', 'pointerAim', 'reshape',
                      'const weight = () =>', 'const scaled = () =>', 'const products = () =>'):
            self.assertIn(token, script)
        # A stretched arrow must not be rescaled behind the user's back; only the button normalizes.
        self.assertNotIn('if (Math.abs(total - 1) > 1e-9)', script)
        css = (ROOT / 'tools/tools.css').read_text()
        self.assertIn('.ph-normalize{', css)
        self.assertIn('.ph-norm.is-unnormalized{color:var(--warm)}', css)
        # The concurrence arrow sits behind the amplitudes, so it is drawn partly transparent.
        self.assertIn('.ph-needle .ph-arrow{stroke:var(--heading);stroke-width:2.6;stroke-opacity:.5}', css)
        self.assertIn('.ph-head-needle{fill:var(--heading);fill-opacity:.5}', css)

    def test_script_defines_every_gate_and_the_shared_camera(self):
        script = (ROOT / 'tools/single-qubit.js').read_text()
        for name, _ in tools.GATES:
            self.assertIn(name + ': [[', script)
        self.assertIn('dataset.basis', script)
        self.assertIn('pointermove', script)

    def test_rotation_controls_build_the_general_gate(self):
        page = (ROOT / 'tools/single-qubit.html').read_text()
        audit = ControlAudit(page)
        self.assertEqual(audit.axes, [(str(polar), str(azimuth)) for _, polar, azimuth in tools.AXIS_PRESETS])
        self.assertEqual(sorted(field['id'] for field in audit.inputs if field['id'].startswith(('axis-', 'rot-'))),
                         ['axis-phi', 'axis-theta', 'rot-gamma', 'rot-theta'])
        for element in ('apply-rotation', 'axis-vector', 'u-00', 'u-01', 'u-10', 'u-11'):
            self.assertIn(f'id="{element}"', page)
        axis = tools.rotation_axis(*tools.AXIS_ANGLES)
        matrix = tools.rotation_matrix(axis, tools.ROTATION_ANGLE, tools.ROTATION_PHASE)
        self.assertIn('id="axis-vector">n̂ = (', page)
        for row in (0, 1):
            for column in (0, 1):
                self.assertIn(f'id="u-{row}{column}">{tools.complex_text(matrix[row][column])}<', page)

    def test_rotation_axis_presets_are_the_axes_they_name(self):
        root2 = 1 / 2 ** 0.5
        self.assertEqual([round(value, 9) for value in tools.rotation_axis(90, 0)], [1, 0, 0])
        self.assertEqual([round(value, 9) for value in tools.rotation_axis(90, 90)], [0, 1, 0])
        self.assertEqual([round(value, 9) for value in tools.rotation_axis(0, 0)], [0, 0, 1])
        for got, want in zip(tools.rotation_axis(45, 0), (root2, 0, root2)):
            self.assertAlmostEqual(got, want)

    def test_rotation_matrix_reproduces_the_named_gates(self):
        root2 = 1 / 2 ** 0.5
        cases = {'X': ((1, 0, 0), 180, 90, ((0, 1), (1, 0))),
                 'Y': ((0, 1, 0), 180, 90, ((0, -1j), (1j, 0))),
                 'Z': ((0, 0, 1), 180, 90, ((1, 0), (0, -1))),
                 'H': ((root2, 0, root2), 180, 90, ((root2, root2), (root2, -root2))),
                 'S': ((0, 0, 1), 90, 45, ((1, 0), (0, 1j)))}
        for name, (axis, theta, gamma, want) in cases.items():
            got = tools.rotation_matrix(axis, theta, gamma)
            for row in (0, 1):
                for column in (0, 1):
                    self.assertAlmostEqual(got[row][column], want[row][column], places=9, msg=name)

    def test_rotation_matrix_is_unitary_and_the_phase_is_global(self):
        for polar, azimuth in ((0, 0), (37, 123), (90, 250), (180, 45)):
            axis = tools.rotation_axis(polar, azimuth)
            for theta, gamma in ((0, 0), (73, 210), (180, 90), (360, 0)):
                unit = tools.rotation_matrix(axis, theta, gamma)
                square = [[sum(unit[row][k] * unit[column][k].conjugate() for k in (0, 1))
                           for column in (0, 1)] for row in (0, 1)]
                for row in (0, 1):
                    for column in (0, 1):
                        self.assertAlmostEqual(square[row][column], 1 if row == column else 0, places=9)
        bare = tools.rotation_matrix((0.6, 0.8, 0), 140, 0)
        phased = tools.rotation_matrix((0.6, 0.8, 0), 140, 17)
        for row in (0, 1):
            for column in (0, 1):
                self.assertAlmostEqual(phased[row][column] * cmath.exp(-1j * math.radians(17)),
                                       bare[row][column], places=9)

    def test_rotation_axis_is_drawn_where_the_state_plane_projects_it(self):
        audit = ControlAudit((ROOT / 'tools/single-qubit.html').read_text())
        axis = tools.rotation_axis(*tools.AXIS_ANGLES)
        tip, tail = tools.project(axis), tools.project(tuple(-value for value in axis))
        line = audit.axis_line
        self.assertEqual((line['x1'], line['y1']), (f'{tail[0]:.1f}', f'{tail[1]:.1f}'))
        self.assertEqual((line['x2'], line['y2']), (f'{tip[0]:.1f}', f'{tip[1]:.1f}'))

    def test_rotation_axis_has_a_labelled_handle_outside_the_rim(self):
        audit = ControlAudit((ROOT / 'tools/single-qubit.html').read_text())
        tip = tools.project(tools.rotation_axis(*tools.AXIS_ANGLES))
        self.assertEqual((audit.axis_handle['cx'], audit.axis_handle['cy']),
                         (f'{tip[0]:.1f}', f'{tip[1]:.1f}'))
        self.assertGreater(float(audit.axis_handle['r']), 10)
        self.assertEqual(audit.axis_label['text-anchor'], 'middle')
        offset = math.hypot(float(audit.axis_label['x']) - tip[0], float(audit.axis_label['y']) - tip[1])
        self.assertGreater(offset, 15)      # clear of the handle at the tip
        self.assertLess(offset, 40)         # and still read as its label

    def test_script_applies_the_matrix_the_controls_build(self):
        script = (ROOT / 'tools/single-qubit.js').read_text()
        for token in ('rotationMatrix', 'rotationAxis', 'rotationReadout', 'apply-rotation',
                      'data-axis-theta', 'bloch-naxis', 'bloch-npole', 'bloch-nhandle',
                      'bloch-nlabel', 'nearAxis', 'setAxisAngles', 'is-aiming-axis'):
            self.assertIn(token, script)

    def test_applied_rotation_leaves_an_orbit_cone_and_arc(self):
        page = (ROOT / 'tools/single-qubit.html').read_text()
        for element in ('bloch-orbit', 'bloch-cone', 'bloch-arc'):
            self.assertIn(f'id="{element}"', page)
        style = (ROOT / 'tools/tools.css').read_text()
        for rule in ('.bloch-rotation-orbit', '.bloch-rotation-cone', '.bloch-rotation-arc'):
            self.assertIn(rule, style)
        script = (ROOT / 'tools/single-qubit.js').read_text()
        for token in ('rotateVector', 'showRotationOrbit', 'showRotationPath', 'clearRotationPath',
                      'bloch-orbit', 'bloch-cone', 'bloch-arc', 'prefers-reduced-motion'):
            self.assertIn(token, script)

if __name__ == '__main__': unittest.main()
