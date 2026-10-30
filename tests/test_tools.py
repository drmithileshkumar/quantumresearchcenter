"""The Tools section: catalogue integrity and the geometry of both state explorers."""
import copy
import cmath
import json
import math
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import tools

class ControlAudit(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.labels, self.buttons, self.presets, self.inputs = set(), [], [], []
        self.svgs = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'label' and a.get('for'): self.labels.add(a['for'])
        if tag == 'input': self.inputs.append(a)
        if tag == 'button' and 'data-gate' in a: self.buttons.append(a['data-gate'])
        if tag == 'button' and 'data-preset' in a: self.presets.append((a['data-theta'], a['data-phi']))
        if tag == 'svg' and 'data-basis' in a: self.svgs.append(a)

class TwoQubitAudit(HTMLParser):
    """Collects the vector groups, controls and table cells of the two-qubit page."""
    def __init__(self, text):
        super().__init__()
        self.svgs, self.groups, self.gate_a, self.gate_b, self.two_qubit_gates, self.presets = [], [], [], [], [], []
        self.lines, self.texts = {}, {}
        self.element = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'svg' and a.get('class') == 'phasor': self.svgs.append(a)
        if tag == 'g' and 'ph-vec' in a.get('class', '').split(): self.groups.append(a)
        if tag == 'button' and 'data-gate-a' in a: self.gate_a.append(a['data-gate-a'])
        if tag == 'button' and 'data-gate-b' in a: self.gate_b.append(a['data-gate-b'])
        if tag == 'button' and 'data-gate' in a: self.two_qubit_gates.append(a['data-gate'])
        if tag == 'button' and 'data-preset' in a: self.presets.append(a['data-preset'])
        if tag in ('line', 'text') and a.get('id'): self.lines[a['id']] = (tag, a)
        self.element = a.get('id') if tag == 'text' else None

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
        self.assertEqual(sorted(audit.gate_a), sorted(name for name, _ in tools.GATES))
        self.assertEqual(sorted(audit.gate_b), sorted(name for name, _ in tools.GATES))
        self.assertEqual(sorted(audit.two_qubit_gates), ['CNOT', 'CZ', 'SWAP'])
        self.assertEqual(audit.presets, [key for key, _ in tools.TWO_PRESETS])
        self.assertEqual(audit.texts.get('ph-vec-00-label'), '|00⟩')
        line = audit.lines['ph-vec-00'][1]
        self.assertEqual(round(float(line['x2']), 1), 376.0)   # full amplitude on the real axis
        self.assertEqual(round(float(line['y2']), 1), 220.0)
        for index in (1, 2, 3):                                 # the other three are empty
            self.assertIn('is-empty', audit.groups[index]['class'])

    def test_two_qubit_static_readouts_agree_with_the_reference(self):
        page = (ROOT / 'tools/two-qubit.html').read_text()
        _, concurrence, plus, minus = tools.two_qubit_observables([1, 0, 0, 0])
        for needle in (f'id="inv-concurrence">{concurrence:.3f}<', f'{plus:.3f}, {minus:.3f}'):
            self.assertIn(needle, page)
        for key in ('00', '01', '10', '11'):
            self.assertIn(f'id="amp-mag-{key}"', page)
        self.assertIn('id="ph-needle"', page)
        self.assertIn('id="ph-p1"', page)

    def test_two_qubit_script_defines_the_same_controls(self):
        script = (ROOT / 'tools/two-qubit.js').read_text()
        for name, _ in tools.GATES:
            self.assertIn(name + ': [[', script)
        for key in ('CNOT', 'CZ', 'SWAP'):
            self.assertIn(key, script)
        for key, _ in tools.TWO_PRESETS:
            self.assertIn(key + ':', script.replace("'", ''))
        self.assertIn('BELL_LABELS', script)
        self.assertIn('fanOffsets', script)
        self.assertIn('displayState', script)
        self.assertIn('ph-needle', script)

    def test_script_defines_every_gate_and_the_shared_camera(self):
        script = (ROOT / 'tools/single-qubit.js').read_text()
        for name, _ in tools.GATES:
            self.assertIn(name + ': [[', script)
        self.assertIn('dataset.basis', script)
        self.assertIn('pointermove', script)

if __name__ == '__main__': unittest.main()
