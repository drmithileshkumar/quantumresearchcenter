"""Conference data integrity and date boundary behavior."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from conferences import validate, status
from conference_map import render_map

class ConferenceTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'content/conferences.json').read_text())

    def test_source_backed_collection_and_rendered_coverage(self):
        validate(self.data)
        page = (ROOT / 'conferences/index.html').read_text()
        for event in self.data['conferences']:
            self.assertIn(f'id="{event["id"]}"', page)
            self.assertIn(event['source'], page)
        self.assertIn('conferences/', (ROOT / 'sitemap.xml').read_text())

    def test_status_includes_entire_end_date(self):
        event = {'start': '2027-02-20', 'end': '2027-02-26'}
        for day, expected in [('2027-02-19', 'Upcoming'), ('2027-02-20', 'In progress'), ('2027-02-26', 'In progress'), ('2027-02-27', 'Past edition')]:
            self.assertEqual(status(event, day), expected)
        self.assertEqual(status({'start': None, 'end': None}, '2027-02-20'), 'Dates pending')

    def test_rejects_duplicate_ids_partial_dates_and_reverse_ranges(self):
        duplicate = copy.deepcopy(self.data)
        duplicate['conferences'].append(duplicate['conferences'][0])
        with self.assertRaises(AssertionError): validate(duplicate)
        for start, end in [('2027-02-20', None), ('2027-02-26', '2027-02-20')]:
            broken = copy.deepcopy(self.data)
            broken['conferences'][0].update(start=start, end=end)
            with self.assertRaises(AssertionError): validate(broken)

    def test_map_has_controls_and_markers_for_every_country(self):
        from html.parser import HTMLParser
        class MapAudit(HTMLParser):
            def __init__(self):
                super().__init__()
                self.buttons, self.markers = set(), set()
            def handle_starttag(self, tag, attributes):
                attributes = dict(attributes)
                if 'data-map-country' in attributes:
                    if tag == 'button': self.buttons.add(attributes['data-map-country'])
                    if tag == 'g': self.markers.add(attributes['data-map-country'])
        audit = MapAudit()
        audit.feed(render_map(ROOT, self.data['conferences']))
        countries = {event['country'] for event in self.data['conferences']}
        self.assertEqual(audit.buttons, countries)
        self.assertEqual(audit.markers, countries)
        self.assertIn('Singapore', audit.markers)
