"""Research structure, migration, source provenance, and worked mathematical checks."""
import cmath
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import unittest
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('research_builder',ROOT/'scripts/build.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)

class Source(HTMLParser):
    def __init__(self,text):
        super().__init__();self.sections=[];self.links=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='section':self.sections.append(attrs.get('id'))
        if tag=='a':self.links.append(attrs.get('href'))

class ResearchPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book=json.loads((ROOT/'content/research.json').read_text())
        cls.output=builder.render(cls.book)
    def test_every_question_has_an_argument_and_sources(self):
        questions=[i for i in builder.records(self.book) if i.get('manuscript')]
        self.assertEqual(len(questions),13)
        for item in questions:
            manuscript=(ROOT/item['manuscript']).read_text();doc=Source(manuscript)
            self.assertEqual(doc.sections,['perspective','mathematics','known','frontier','investigation'])
            self.assertGreaterEqual(len(item['papers']),2)
            self.assertIn('\\[',manuscript)
            self.assertIn('Reproduce:',manuscript)
            self.assertIn('Extend:',manuscript)
            allowed={self.book['papers'][p]['url'] for p in item['papers']}
            self.assertTrue(allowed.issubset(set(doc.links)),item['id'])
            self.assertIn('mathjax-config.js',self.output[builder.path(item)])
    def test_legacy_urls_redirect_to_live_pages_and_stay_out_of_sitemap(self):
        for old,target in builder.RESEARCH_REDIRECTS.items():
            self.assertIn(target,self.output)
            self.assertIn('http-equiv="refresh"',self.output[old])
            self.assertNotIn(self.book['url']+'/'+old.removesuffix('index.html')+'</loc>',self.output['sitemap.xml'])
        self.assertEqual(builder.RESEARCH_REDIRECTS['research/quantum-information/channel-capacities/index.html'],'research/quantum-information/channel-capacity/index.html')
    def test_navigation_has_all_four_categories_and_questions(self):
        builder.check_output(self.output)
        landing=self.output['research/index.html']
        for item in builder.records(self.book):
            self.assertIn(builder.relative(builder.path(item),'research/index.html'),landing)

class WorkedMathematics(unittest.TestCase):
    def test_decoherence_purity(self):
        # Form the reduced state by tracing an explicit two-record pure state.
        for s in (0,.2,.9,1):
            v=[1/math.sqrt(2),0,s/math.sqrt(2),math.sqrt(1-s*s)/math.sqrt(2)]
            rho=[[sum(v[2*i+e]*v[2*j+e] for e in range(2)) for j in range(2)] for i in range(2)]
            purity=sum(rho[i][j]*rho[j][i] for i in range(2) for j in range(2))
            self.assertAlmostEqual(purity,(1+s*s)/2)
    def test_chsh_box_marginals(self):
        for visibility in (0,.5,1/math.sqrt(2),1):
            correlators={}
            for x,y in itertools.product(range(2),repeat=2):
                p={(a,b):visibility*(.5 if a^b==x*y else 0)+(1-visibility)/4 for a,b in itertools.product(range(2),repeat=2)}
                for a in range(2):self.assertAlmostEqual(sum(p[a,b] for b in range(2)),.5)
                correlators[x,y]=sum((-1)**(a+b)*v for (a,b),v in p.items())
            self.assertAlmostEqual(correlators[0,0]+correlators[0,1]+correlators[1,0]-correlators[1,1],4*visibility)
    def test_gravity_phase_invariant(self):
        for phases in ((0,0,0,0),(.1,.3,-.2,math.pi),(.1,1.2,.4,.9)):
            delta=phases[0]+phases[3]-phases[1]-phases[2]
            m=[cmath.exp(1j*p)/2 for p in phases]
            determinant=m[0]*m[3]-m[1]*m[2]
            self.assertAlmostEqual(abs(determinant),abs(math.sin(delta/2))/2)
            local_a=(.7,-.4);local_b=(.2,1.3)
            transformed=[m[2*i+j]*cmath.exp(1j*(local_a[i]+local_b[j])) for i,j in itertools.product(range(2),repeat=2)]
            self.assertAlmostEqual(abs(transformed[0]*transformed[3]-transformed[1]*transformed[2]),abs(determinant))
    def test_search_rotation_against_full_amplitude_updates(self):
        for n in (4,16,64):
            v=[1/math.sqrt(n)]*n;theta=math.asin(1/math.sqrt(n))
            for k in range(12):
                self.assertAlmostEqual(v[0]**2,math.sin((2*k+1)*theta)**2)
                v[0]*=-1;mean=sum(v)/n;v=[2*mean-x for x in v]
    def test_repetition_code_probability_and_distance_budget(self):
        for p in (.001,.01,.2):
            fail=sum(p**sum(bits)*(1-p)**(3-sum(bits)) for bits in itertools.product((0,1),repeat=3) if sum(bits)>=2)
            self.assertAlmostEqual(fail,3*p*p-2*p**3)
        self.assertAlmostEqual(3*.01**2-2*.01**3,.000298)
        self.assertLessEqual(10**6*.1*.1**((13+1)/2),.01+1e-12)
    def test_single_copy_filter(self):
        a=.5*math.sqrt(.8);b=math.sqrt(.2);success=a*a+b*b
        self.assertAlmostEqual(success,.4)
        self.assertAlmostEqual(a/math.sqrt(success),1/math.sqrt(2))
        self.assertAlmostEqual(b/math.sqrt(success),1/math.sqrt(2))
    def test_erasure_entropy_cancellation(self):
        entropy=lambda p: -sum(x*math.log2(x) for x in (p,1-p) if x)
        for p in (0,.25,.5,.9,1):
            out=entropy(p)+1-p;joint=entropy(p)+p
            self.assertAlmostEqual(out-joint,1-2*p)
    def test_correctable_error_spaces_and_phase_counterexample(self):
        images={(error,logical):((0 if logical==0 else 7)^error) for error in (0,1,2,4) for logical in (0,1)}
        self.assertEqual(len(set(images.values())),8)
        # Z on the most significant qubit distinguishes the code basis states.
        self.assertNotEqual((-1)**((0>>2)&1),(-1)**((7>>2)&1))
        # A classical copy A=B=C has H(AB)=H(BC)=H(B)=H(ABC)=1.
        self.assertEqual(1+1-1-1,0)
    def test_product_formula_bound_for_x_plus_z(self):
        def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
        t=.7;c=math.cos(math.sqrt(2)*t);z=-1j*math.sin(math.sqrt(2)*t)/math.sqrt(2)
        exact=[[c+z,z],[z,c-z]]
        for r in (1,2,8,32):
            h=t/r
            rx=[[math.cos(h),-1j*math.sin(h)],[-1j*math.sin(h),math.cos(h)]]
            rz=[[cmath.exp(-1j*h),0],[0,cmath.exp(1j*h)]]
            step=mul(rx,rz);approx=[[1,0],[0,1]]
            for _ in range(r):approx=mul(approx,step)
            diff=[[approx[i][j]-exact[i][j] for j in range(2)] for i in range(2)]
            gram=[[sum(diff[k][i].conjugate()*diff[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
            trace=(gram[0][0]+gram[1][1]).real;det=(gram[0][0]*gram[1][1]-gram[0][1]*gram[1][0]).real
            norm=math.sqrt((trace+math.sqrt(max(0,trace*trace-4*det)))/2)
            self.assertLessEqual(norm,t*t/r+1e-12)
    def test_two_segment_geometric_wait(self):
        p=.1
        # Independent calculation from the survival-probability sum.
        expectation=sum(1-(1-(1-p)**k)**2 for k in range(1000))
        self.assertAlmostEqual(expectation,2/p-1/(2*p-p*p))
    def test_coherent_control_and_noisy_sensing(self):
        epsilon=.01;m=100;q=math.sin(epsilon/2)**2
        self.assertAlmostEqual(math.sin(m*epsilon/2)**2,.22984884706593015)
        odd_flips=sum(math.comb(m,k)*q**k*(1-q)**(m-k) for k in range(1,m+1,2))
        self.assertAlmostEqual((1-(1-2*q)**m)/2,odd_flips)
        for n in (1,10,100):
            gamma=.4;total=1000
            ent=lambda t:n*n*total*t*math.exp(-2*n*gamma*t)
            prod=lambda t:n*total*t*math.exp(-2*gamma*t)
            self.assertAlmostEqual(ent(1/(2*n*gamma)),prod(1/(2*gamma)))
            self.assertGreater(ent(1/(2*n*gamma)),ent(.8/(2*n*gamma)))

if __name__=='__main__':unittest.main()
