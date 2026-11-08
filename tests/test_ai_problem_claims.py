"""The claim index must retain attribution and exclude unpublished explainers."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import ai_problem_claims as claims


class ProblemClaimsTests(unittest.TestCase):
    def setUp(self):
        self.articles = [json.loads(p.read_text()) for p in (ROOT / 'content/news-articles').glob('*.json')]
        self.data = json.loads((ROOT / 'content/ai-problem-claims.json').read_text())

    def test_each_claim_has_visible_scope_attribution_and_source(self):
        soup = BeautifulSoup(claims.render_claims(ROOT, self.articles), 'html.parser')
        cards = soup.select('.problem-claim')
        self.assertEqual(len(cards), len(self.data['problems']))
        for card, item in zip(cards, self.data['problems']):
            self.assertIn(item['scope'], card.get_text())
            self.assertIn(item.get('claimant', item.get('source_label')), card.get_text())
            self.assertIsNotNone(card.find('a', href=item['source']))
        self.assertIn('not a list of independently confirmed solutions', soup.get_text())

    def test_categories_are_separate_and_open_entries_do_not_claim_ai_proofs(self):
        soup = BeautifulSoup(claims.render_claims(ROOT, self.articles), 'html.parser')
        for category, ident in [('claimed', 'claimed-by-ai'), ('open', 'still-open')]:
            section = soup.find(id=ident)
            expected = {p['id'] for p in self.data['problems'] if p['category'] == category}
            self.assertEqual({p['id'] for p in section.select('.problem-claim')}, expected)
        self.assertNotIn('Read the claim', soup.find(id='still-open').get_text())
        self.assertIsNotNone(soup.select_one('#claimed-by-ai #yang-mills'))
        self.assertIsNotNone(soup.select_one('#still-open #yang-mills-mass-gap'))

    def test_rejects_draft_explainer(self):
        articles = copy.deepcopy(self.articles)
        target = next(p['article'] for p in self.data['problems'] if p.get('article'))
        next(a for a in articles if a['slug'] == target)['status'] = 'draft'
        with self.assertRaisesRegex(ValueError, 'must be published'):
            claims.load_claims(ROOT, articles)

    def test_home_links_to_page_with_stable_problem_anchors(self):
        home = BeautifulSoup(claims.render_claims_home(ROOT, self.articles), 'html.parser')
        self.assertIsNotNone(home.find('a', href=claims.PAGE))
        self.assertFalse(home.select('.problem-claim'))
        pages = {}
        def shell(path, title, description, body):
            pages[path] = body
        claims.render_claims_page(ROOT, self.articles, shell)
        page = BeautifulSoup(pages[claims.PAGE], 'html.parser')
        self.assertEqual(len(page.select('h1')), 1)
        for item in self.data['problems']:
            self.assertIsNotNone(page.find(id=item['id']))
            if item.get('article'):
                self.assertIsNotNone(page.find('a', href='../news/articles/' + item['article'] + '/index.html'))

    def test_rejects_duplicate_ids_and_unsafe_source(self):
        for mutate in (lambda d: d['problems'].append(d['problems'][0]),
                       lambda d: d['problems'][0].update(source='javascript:alert(1)'),
                       lambda d: d['problems'][0].update(category='unknown')):
            data = copy.deepcopy(self.data)
            mutate(data)
            with patch.object(claims.json, 'loads', return_value=data):
                with self.assertRaises(ValueError):
                    claims.load_claims(ROOT, self.articles)
