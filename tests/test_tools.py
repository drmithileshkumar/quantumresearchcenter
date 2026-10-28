"""The Tools section: catalogue integrity and the single-qubit explorer's geometry."""
import copy
import json
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

    def test_script_defines_every_gate_and_the_shared_camera(self):
        script = (ROOT / 'tools/single-qubit.js').read_text()
        for name, _ in tools.GATES:
            self.assertIn(name + ': [[', script)
        self.assertIn('dataset.basis', script)
        self.assertIn('pointermove', script)

if __name__ == '__main__': unittest.main()
