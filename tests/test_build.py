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
        self.book['categories'][0]['papers'].append('missing')
        with self.assertRaises(ValueError):builder.render(self.book)
    def test_duplicate_sibling_rejected(self):
        self.book['categories'].append(copy.deepcopy(self.book['categories'][0]))
        with self.assertRaises(ValueError):builder.render(self.book)
    def test_invalid_path_rejected(self):
        self.book['categories'][0]['id']='../escape'
        with self.assertRaises(ValueError):builder.render(self.book)
    def test_questions_and_references_preserved(self):
        output=builder.render(self.book)
        for item in builder.records(self.book):
            page=output[builder.path(item)]
            for question in item['questions']:self.assertIn(builder.esc(question),page)
            for paper in item['papers']:self.assertIn(self.book['papers'][paper]['url'],page)
    def test_categories_and_keyword_links(self):
        output=builder.render(self.book)
        self.assertIn('href="research/index.html"',output['index.html'])
        for category in self.book['categories']:
            root='research/'+category['id']+'/index.html'
            self.assertIn(root,output)
            self.assertIn('class="research-keywords"',output[root])
            for child in category['children']:
                self.assertIn('href="'+child['id']+'/index.html"',output[root])
        self.assertEqual([c['title'] for c in self.book['categories']],['Quantum Computation','Quantum Information','Quantum Technologies'])
    def test_deeper_topics_and_breadcrumbs(self):
        parent=self.book['categories'][0]['children'][0]['children'][0]
        leaf={'id':'new-subtopic','title':'New subtopic','keyword':'New keyword','summary':'Summary','paragraphs':['Overview'],'papers':[],'questions':[],'children':[]}
        parent['children']=[leaf]
        output=builder.render(self.book);builder.check_output(output)
        target='research/quantum-computation/algorithms/variational-algorithms/new-subtopic/index.html'
        self.assertIn(target,output)
        self.assertIn('href="../index.html"',output[target])
        self.assertIn('href="../../index.html"',output[target])
        self.assertIn('aria-label="Breadcrumb"',output[target])
        self.assertIn('href="../../../../../styles.css"',output[target])
    def test_same_slug_in_different_branches(self):
        child=copy.deepcopy(self.book['categories'][0]['children'][0])
        self.book['categories'][1]['children'].append(child)
        output=builder.render(self.book);builder.check_output(output)
        self.assertIn('research/quantum-information/algorithms/index.html',output)
        self.assertIn('research/quantum-computation/algorithms/index.html',output)
if __name__=='__main__':unittest.main()
