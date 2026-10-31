"""Company directory coverage and source-data validation."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from companies import validate
from conference_map import render_map

class CompanyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'content/companies.json').read_text())

    def test_every_company_and_source_is_rendered(self):
        validate(self.data)
        page = (ROOT / 'companies/index.html').read_text()
        for company in self.data['companies']:
            self.assertIn(f'id="{company["id"]}"', page)
            self.assertIn(company['url'], page)
            for source in company['sources']: self.assertIn(source, page)
        self.assertIn('companies/', (ROOT / 'sitemap.xml').read_text())
        self.assertIn('companies/index.html', (ROOT / 'index.html').read_text())
        self.assertIn('../companies/index.html', (ROOT / 'conferences/index.html').read_text())
        self.assertIn('companies/index.html', (ROOT / 'website-map/data.js').read_text())

    def test_invalid_entries_are_rejected(self):
        duplicate = copy.deepcopy(self.data)
        duplicate['companies'].append(duplicate['companies'][0])
        with self.assertRaises(AssertionError): validate(duplicate)
        for changes in ({'sources': []}, {'focus': ['unknown']}, {'country': ''}, {'url': 'javascript:alert(1)'}, {'checked': '2099-01-01'}):
            broken = copy.deepcopy(self.data)
            broken['companies'][0].update(changes)
            with self.assertRaises(AssertionError): validate(broken)

    def test_map_covers_every_company_country(self):
        from html.parser import HTMLParser
        class MapAudit(HTMLParser):
            def __init__(self):
                super().__init__()
                self.buttons, self.markers = set(), set()
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if 'data-map-country' in attrs:
                    if tag == 'button': self.buttons.add(attrs['data-map-country'])
                    if tag == 'g': self.markers.add(attrs['data-map-country'])
        markup = render_map(ROOT, self.data['companies'], collection='companies')
        audit = MapAudit()
        audit.feed(markup)
        countries = {c['country'] for c in self.data['companies']}
        self.assertEqual(audit.buttons, countries)
        self.assertEqual(audit.markers, countries)
        self.assertIn('A world of quantum companies', markup)
        self.assertNotIn('conferences across', markup)
