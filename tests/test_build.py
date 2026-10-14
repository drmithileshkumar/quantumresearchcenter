import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class HandbookTests(unittest.TestCase):
    def setUp(self):self.book=json.loads((ROOT/'content/research.json').read_text())
    def test_all_pages_have_valid_links_and_are_reachable(self):builder.check_output(builder.render(self.book))
    def test_reading_sequence(self):
        output=builder.render(self.book);items=builder.records(self.book)
        for n,item in enumerate(items):
            page=output[builder.path(item)]
            self.assertIn('aria-current="page"',page)
            if n+1<len(items):self.assertIn('rel="next" href="'+builder.relative(builder.path(items[n+1]),builder.path(item))+'"',page)
            if n:self.assertIn('rel="prev" href="'+builder.relative(builder.path(items[n-1]),builder.path(item))+'"',page)
    def test_missing_reference_rejected(self):
        self.book['parts'][0]['chapters'][0]['papers'].append('missing')
        with self.assertRaises(ValueError):builder.render(self.book)
    def test_duplicate_topic_rejected(self):
        self.book['parts'][0]['chapters'].append(copy.deepcopy(self.book['parts'][0]['chapters'][0]))
        with self.assertRaises(ValueError):builder.render(self.book)
    def test_questions_and_references_preserved(self):
        output=builder.render(self.book)
        for item in builder.records(self.book):
            page=output[builder.path(item)]
            for question in item['questions']:self.assertIn(builder.esc(question),page)
            for paper in item['papers']:self.assertIn(self.book['papers'][paper]['url'],page)
    def test_home_and_research_have_separate_entry_points(self):
        output=builder.render(self.book)
        self.assertIn('class="landing-hero"',output['index.html'])
        self.assertIn('href="research/index.html"',output['index.html'])
        research=output['research/index.html']
        self.assertNotIn('http-equiv="refresh"',research)
        self.assertIn('id="contents-overview"',research)
        self.assertIn('href="foundations/index.html"',research)
        self.assertIn('rel="prev" href="../../research/index.html"',output['research/foundations/index.html'])
if __name__=='__main__':unittest.main()
