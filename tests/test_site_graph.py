"""The graph describes public pages and resolves links without inventing connections."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from site_graph import collect


class SiteGraphTests(unittest.TestCase):
    def test_public_pages_and_internal_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'content').mkdir()
            (root / 'content/private.html').write_text('<html><title>Private</title></html>')
            outputs = {
                'index.html': '<html><title>Home</title><nav><a href="/tools/">Tools</a></nav><main><a href="tools/index.html#demo">Demo</a><a href="https://other.test/">External</a></main></html>',
                'tools/index.html': '<html><title>Tools</title><a href="../index.html">Home</a><a href="https://example.test/research/">Research</a></html>',
                'research/index.html': '<html><title>Research</title></html>',
                'hidden.html': '<html><meta name="robots" content="noindex"><title>Hidden</title></html>',
                'old.html': '<html><meta http-equiv="refresh" content="0;url=index.html"></html>',
                'fragment.html': '<section>Not a page</section>',
            }
            graph = collect(root, outputs, 'https://example.test')
            self.assertEqual({n['id'] for n in graph['nodes']}, {'index.html', 'tools/index.html', 'research/index.html', 'website-map/index.html'})
            self.assertEqual(len(graph['edges']), 2)
            self.assertTrue(all(not edge['navigation'] for edge in graph['edges']))

    def test_generated_graph_has_valid_unique_nodes_and_edges(self):
        text = (ROOT / 'website-map/index.html').read_text()
        graph = json.loads(text.split('<script id="graph-data" type="application/json">')[1].split('</script>')[0])
        ids = {n['id'] for n in graph['nodes']}
        self.assertEqual(len(ids), len(graph['nodes']))
        self.assertGreater(len(ids), 200)
        for node in graph['nodes']:
            self.assertTrue((ROOT / node['id']).is_file(), node['id'])
        pairs = set()
        for edge in graph['edges']:
            self.assertIn(edge['source'], ids)
            self.assertIn(edge['target'], ids)
            self.assertNotEqual(edge['source'], edge['target'])
            pairs.add((edge['source'], edge['target']))
        self.assertEqual(len(pairs), len(graph['edges']))
        self.assertIn('href="website-map/index.html">Website map</a>', (ROOT / 'index.html').read_text())

    def test_new_nested_pages_are_discovered_and_removed_managed_pages_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'new-section/deep').mkdir(parents=True)
            page = root / 'new-section/deep/index.html'
            page.write_text('<html><title>New public page</title></html>')
            (root / 'scripts').mkdir()
            (root / 'scripts/.generated-manifest.json').write_text(json.dumps({'withdrawn.html': 'old-hash'}))
            (root / 'withdrawn.html').write_text('<html><title>Withdrawn</title></html>')
            ids = {node['id'] for node in collect(root, {}, 'https://example.com')['nodes']}
            self.assertIn('new-section/deep/index.html', ids)
            self.assertNotIn('withdrawn.html', ids)
            page.unlink()
            self.assertNotIn('new-section/deep/index.html', {n['id'] for n in collect(root, {}, 'https://example.com')['nodes']})

    def test_xml_sitemap_matches_graph_page_inventory(self):
        from xml.etree import ElementTree as ET
        import build
        text = (ROOT / 'website-map/index.html').read_text()
        graph = json.loads(text.split('<script id="graph-data" type="application/json">')[1].split('</script>')[0])
        site = json.loads((ROOT / 'content/research.json').read_text())['url']
        expected = {site + '/' + node['id'].removesuffix('index.html') for node in graph['nodes'] if node['id'] not in build.UNLISTED}
        actual = {node.text for node in ET.parse(ROOT / 'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        self.assertEqual(actual, expected)
