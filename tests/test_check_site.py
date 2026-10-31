import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_all
import check_site


def page(body, head=''):
    return f'<!doctype html><html lang="en"><head><title>x</title>{head}</head><body><h1>x</h1>{body}</body></html>'


class SiteCheck(unittest.TestCase):
    def problems(self, files):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, text in files.items():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(text)
            return check_site.problems(root)[1]

    def test_the_published_site_passes(self):
        self.assertEqual(check_site.problems(ROOT)[1], [])

    def test_connected_pages_pass(self):
        self.assertEqual(self.problems({'index.html': page('<a href="a/">a</a><a href="a/index.html#x">x</a>'),
                                        'a/index.html': page('<p id="x"></p><a href="../index.html">home</a>')}), [])

    def test_broken_link_is_reported(self):
        self.assertEqual(self.problems({'index.html': page('<a href="nope.html">n</a>')}), ['index.html: broken link nope.html'])

    def test_broken_anchor_is_reported(self):
        self.assertEqual(self.problems({'index.html': page('<a href="#nope">n</a>')}), ['index.html: broken anchor #nope'])

    def test_missing_resource_is_reported(self):
        self.assertEqual(self.problems({'index.html': page('', '<script src="gone.js"></script>')}), ['index.html: broken link gone.js'])

    def test_orphan_page_is_reported(self):
        self.assertEqual(self.problems({'index.html': page(''), 'lost/index.html': page('')}),
                         ['lost/index.html: no links lead here from the home page'])

    def test_redirects_may_be_orphans(self):
        moved = page('', '<meta http-equiv="refresh" content="0;url=index.html">')
        self.assertEqual(self.problems({'index.html': page(''), 'old.html': moved}), [])

    def test_routed_fragments_are_not_element_ids(self):
        routed = page('<a href="#node">n</a>', '<script defer src="map.js"></script>')
        self.assertEqual(self.problems({'index.html': routed, 'map.js': ''}), [])


class Publishing(unittest.TestCase):
    def test_published_copy_is_complete_and_holds_no_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary) / 'site'
            build_all.publish(ROOT, site)
            self.assertEqual(check_site.problems(site)[1], [])
            for public in ('index.html', 'CNAME', 'styles.css', 'website-map/data.js', 'news/index.json'):
                self.assertTrue((site / public).is_file(), public)
            for private in ('scripts', 'tests', 'content', 'AGENTS.md', 'education/foundations/content',
                            'education/foundations/build.py', 'education/course_builder.py', 'education/templates', 'website-map/template.html.in'):
                self.assertFalse((site / private).exists(), private)


class BuildOrder(unittest.TestCase):
    def test_shared_build_runs_last_and_every_section_runs(self):
        order = build_all.builders(ROOT)
        self.assertEqual(order[-1], 'scripts/build.py')
        for builder in ('education/computing/build.py', 'frontiers/build.py', 'map/build.py'):
            self.assertIn(builder, order)
        self.assertEqual(len(order), len(set(order)))


if __name__ == '__main__':
    unittest.main()
