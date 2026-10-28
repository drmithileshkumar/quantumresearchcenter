"""Every generated reading surface uses the same primary navigation, even without JS."""
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'education'))
from site_navigation import site_navigation


class PrimaryNavigation(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.navs = []
        self.current = None
        self.link = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav' and attrs.get('aria-label') == 'Site navigation':
            self.current = {'attrs': attrs, 'links': []}
            self.navs.append(self.current)
        elif self.current is not None and tag == 'a':
            self.link = {**attrs, 'text': ''}
            self.current['links'].append(self.link)

    def handle_endtag(self, tag):
        if tag == 'a': self.link = None
        if tag == 'nav': self.current = None

    def handle_data(self, text):
        if self.link is not None: self.link['text'] += text


class NavigationTests(unittest.TestCase):
    def test_nested_pages_highlight_the_section_and_resolve_links(self):
        for source, active in [('index.html', 'Home'), ('news/articles/example/index.html', 'News'),
                               ('education/computing/01-example.html', 'Education'),
                               ('research/students/index.html', 'Research'),
                               ('tools/single-qubit.html', 'Tools')]:
            with self.subTest(source=source):
                nav = PrimaryNavigation(site_navigation(source)).navs[0]
                self.assertEqual([a['text'] for a in nav['links']], ['Home', 'News', 'Education', 'Research', 'Tools'])
                self.assertEqual([a['text'] for a in nav['links'] if 'aria-current' in a], [active])
                for a in nav['links']:
                    self.assertTrue((ROOT / posixpath.normpath(posixpath.join(posixpath.dirname(source), a['href']))).is_file())

    def test_all_published_primary_menus_use_the_shared_component(self):
        checked = 0
        for path in ROOT.rglob('*.html'):
            if {'.git', 'content', 'source', 'vendor', 'templates', 'tests'} & set(path.relative_to(ROOT).parts):
                continue
            for nav in PrimaryNavigation(path.read_text()).navs:
                checked += 1
                with self.subTest(page=str(path.relative_to(ROOT))):
                    self.assertIn('primary-nav', nav['attrs'].get('class', '').split())
                    self.assertEqual([a['text'] for a in nav['links'][:5]], ['Home', 'News', 'Education', 'Research', 'Tools'])
                    for a in nav['links'][:5]:
                        self.assertNotIn('icon-nav', a.get('class', ''))
                        self.assertTrue((path.parent / a['href']).is_file())
        self.assertGreater(checked, 100)


if __name__ == '__main__': unittest.main()
