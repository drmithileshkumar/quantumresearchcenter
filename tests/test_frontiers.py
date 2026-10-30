"""Frontier maps: evidence rules, generated pages, and the unlisted pilot."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
# Loaded by path: other tests import scripts/build.py as the module named "build".
spec = importlib.util.spec_from_file_location('frontier_build', ROOT / 'frontiers/build.py')
frontiers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontiers)


class FrontierMapTest(unittest.TestCase):
    def setUp(self):
        self.data = frontiers.load()[0]

    def rejected(self, change):
        data = copy.deepcopy(self.data)
        change({n['id']: n for n in data['nodes']}, data)
        with self.assertRaises(AssertionError):
            frontiers.validate(data)

    def test_map_is_valid(self):
        frontiers.validate(self.data)

    def test_status_needs_a_source(self):
        self.rejected(lambda nodes, _: nodes['npt-bound'].update(sources=[]))

    def test_source_must_exist(self):
        self.rejected(lambda nodes, _: nodes['npt-bound'].update(sources=['0000.00000']))

    def test_link_must_resolve(self):
        self.rejected(lambda nodes, _: nodes['npt-bound'].update(links=[{'to': 'missing', 'rel': 'related'}]))

    def test_claim_must_say_what_is_unknown(self):
        self.rejected(lambda nodes, _: nodes['two-copy-werner'].pop('unknown'))

    def test_committed_pages_are_current(self):
        for path, html in frontiers.render(self.data).items():
            self.assertEqual((ROOT / path).read_text(), html, path)

    def test_pilot_is_unlisted(self):
        pages = frontiers.render(self.data)
        for html in pages.values():
            self.assertIn('<meta name="robots" content="noindex">', html)
        self.assertNotIn('frontiers/', (ROOT / 'sitemap.xml').read_text())

    def test_every_node_links_to_its_page(self):
        html = frontiers.render(self.data)['frontiers/entanglement/index.html']
        for node in self.data['nodes']:
            self.assertIn(f'href="{node["id"]}/index.html"', html)


if __name__ == '__main__':
    unittest.main()
