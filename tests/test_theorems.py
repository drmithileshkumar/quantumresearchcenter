"""Theorem of the Day: page structure, sources, and the mathematics of each entry."""
import importlib.util
import json
import math
import random
from pathlib import Path
import sys
import unittest
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('theorem_builder',ROOT/'scripts/build.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class Sections(HTMLParser):
    def __init__(self,text):
        super().__init__();self.sections=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        if tag=='section':self.sections.append(dict(attrs).get('id'))

class TheoremPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'content/theorems.json').read_text())
        cls.entries=builder.theorem_entries(cls.data)
        cls.output=builder.render(json.loads((ROOT/'content/research.json').read_text()))
    def test_each_entry_states_proves_and_extends(self):
        for item in self.entries:
            text=(ROOT/item['manuscript']).read_text()
            self.assertEqual(Sections(text).sections,['statement','proof','discovery','check'],item['id'])
            self.assertIn('theorem-new',text)
            self.assertIn('theorem-status',text,'a new result must say what is already known')
            self.assertIn('\\square',text)
            self.assertIn('Reproduce:',text)
            self.assertGreaterEqual(len(item['references']),2)
            page=self.output[item['_path']]
            self.assertIn('mathjax-config.js',page)
            for ref in item['references']:
                if ref.get('url'):self.assertIn(ref['url'],page)
    def test_pages_are_linked_from_research(self):
        builder.check_output(self.output)
        home=self.output[builder.THEOREM_HOME]
        self.assertIn('theorem-of-the-day/index.html',self.output['research/index.html'])
        for item in self.entries:
            self.assertIn(builder.relative(item['_path'],builder.THEOREM_HOME),home)
    def test_newest_theorem_comes_first(self):
        dates=[item['date'] for item in self.entries]
        self.assertEqual(dates,sorted(dates,reverse=True))

def gap(s,n,m):return math.acos(s**m)-math.acos(s**n)

class CloningTradeoff(unittest.TestCase):
    def test_worked_example(self):
        s=3/4
        self.assertAlmostEqual(math.cos(gap(s,1,2)),31/32)
        self.assertAlmostEqual(math.cos(gap(s,1,2))**2,961/1024)
        self.assertAlmostEqual(math.cos(gap(s,1,2)/2)**2,63/64)
        self.assertAlmostEqual(math.cos(gap(s,1,2)-math.acos(math.sqrt(.99)))**2,.97752,places=5)
    def test_symmetric_point_matches_chefles_barnett(self):
        for s in (.1,.5,.75,.95):
            for n,m in ((1,2),(1,3),(2,3),(2,5)):
                known=(1+s**(m+n)+math.sqrt((1-s**(2*m))*(1-s**(2*n))))/2
                self.assertAlmostEqual(math.cos(gap(s,n,m)/2)**2,known)
    def test_great_circle_cloner_has_the_input_overlap(self):
        # The optimal outputs must have the same overlap as the inputs, so a unitary maps one pair to the other.
        for s in (.2,.6,.9):
            for n,m in ((1,2),(2,3)):
                g,d=math.acos(s**m),gap(s,n,m)
                for x in (0,d/3,d/2,d):
                    y=d-x
                    self.assertAlmostEqual(math.cos(x)*math.cos(g-y)+math.sin(x)*math.sin(g-y),s**n)
                    self.assertAlmostEqual(math.cos(g)*math.cos(g-y)+math.sin(g)*math.sin(g-y),math.cos(y))
    def test_random_qubit_cloners_respect_the_bound(self):
        # 1 -> 2 qubit cloners: a random 4x4 unitary acting on |input>|0>, no environment.
        rng=random.Random(7)
        def unit(n):
            v=[complex(rng.gauss(0,1),rng.gauss(0,1)) for _ in range(n)];r=math.sqrt(sum(abs(z)**2 for z in v));return [z/r for z in v]
        def unitary(n):
            cols=[]
            for _ in range(n):
                v=unit(n)
                for c in cols:
                    p=sum(a.conjugate()*b for a,b in zip(c,v));v=[b-p*a for a,b in zip(c,v)]
                r=math.sqrt(sum(abs(z)**2 for z in v));cols.append([z/r for z in v])
            return lambda w:[sum(cols[j][i]*w[j] for j in range(n)) for i in range(n)]
        dot=lambda u,v:sum(a.conjugate()*b for a,b in zip(u,v))
        kron=lambda u,v:[a*b for a in u for b in v]
        for _ in range(300):
            psi,phi=unit(2),unit(2);s=abs(dot(psi,phi));U=unitary(4)
            angles=[math.acos(min(1,abs(dot(kron(x,x),U(kron(x,[1,0]))))))for x in (psi,phi)]
            self.assertGreaterEqual(sum(angles),gap(s,1,2)-1e-9)
    def test_perfect_cloning_needs_orthogonal_or_equal_states(self):
        self.assertAlmostEqual(gap(0,1,2),0);self.assertAlmostEqual(gap(1,1,2),0)
        for s in (.01,.3,.99):self.assertGreater(gap(s,1,2),0)

if __name__=='__main__':unittest.main()
