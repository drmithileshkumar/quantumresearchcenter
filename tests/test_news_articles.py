"""Publishing boundaries, stable paper URLs, and the two independent news feeds."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build
import news_articles
import news_editor
import paper_news


class NewsPublishingTests(unittest.TestCase):
    def setUp(self):
        self.book = json.loads((ROOT / 'content/research.json').read_text())
        self.articles = news_articles.load_articles(ROOT)
        self.config = json.loads((ROOT / 'content/news.json').read_text())
        self.papers = json.loads((ROOT / 'content/papers.json').read_text())['papers']

    def render(self):
        return build.render(self.book)

    def test_paper_urls_and_feed_remain_stable(self):
        output = self.render()
        build.check_output(output)
        feed = ET.fromstring(output['news/feed.xml'])
        for paper in self.papers:
            path = paper_news.paper_path(paper)
            if paper['status'] == 'approved':
                self.assertIn(path, output)
                self.assertTrue(path.startswith('news/papers/'))
                self.assertIn('<a href="../index.html">Research Papers</a>', output[path])
            else:
                self.assertNotIn(path, output)
        for link in feed.findall('channel/item/link'):
            self.assertIn('/news/papers/', link.text)
        self.assertTrue(feed.findtext('channel/link').endswith('/news/papers/'))
        self.assertIn('<h1>Research Papers</h1>', output['news/papers/index.html'])
        self.assertIn('news/articles/index.html', output['index.html'])

    def test_draft_never_leaks_into_public_outputs(self):
        draft = copy.deepcopy(self.articles[0])
        draft.update(slug='private-draft', title='UNPUBLISHED SENTINEL', status='draft')
        with patch.object(news_articles, 'load_articles', return_value=self.articles + [draft]):
            output = self.render()
        self.assertNotIn('news/articles/private-draft/index.html', output)
        self.assertNotIn('UNPUBLISHED SENTINEL', '\n'.join(output.values()))
        feed = ET.fromstring(output['news/articles/feed.xml'])
        self.assertEqual(len(feed.findall('channel/item')), len(self.articles))

    def test_rejects_invalid_publishing_metadata(self):
        for changes in ({'slug': '../escape'}, {'status': 'live'}, {'updated': '2020-01-01'},
                        {'related_articles': ['missing']}, {'related_papers': ['9999.00000']},
                        {'sources': [{'title': 'Unsafe URL', 'url': 'javascript:alert(1)'}]}):
            with self.subTest(changes=changes):
                articles = copy.deepcopy(self.articles)
                articles[0].update(changes)
                with self.assertRaises(ValueError):
                    news_articles.validate(articles, self.config, self.papers)
        with self.assertRaises(ValueError):
            news_articles.validate(self.articles, {'featured': 'missing'}, self.papers)

    def test_article_figures_are_inlined_and_sanitized(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'content/news-articles/figures/demo'
            folder.mkdir(parents=True)
            figure = {'file': 'plot.svg', 'caption': 'A caption', 'alt': 'A description'}
            (folder / 'plot.svg').write_text('<?xml version="1.0"?>\n<svg viewBox="0 0 10 10"><line class="fig-axis"/></svg>')
            html = news_articles.figure_html(root, 'demo', figure)
            self.assertIn('<svg role="img" aria-label="A description" viewBox', html)
            self.assertIn('<figcaption>A caption</figcaption>', html)
            for unsafe in ('<svg><script>x</script></svg>', '<svg onload="x"></svg>', '<svg><g id="a"/></svg>'):
                (folder / 'plot.svg').write_text(unsafe)
                with self.assertRaises(ValueError):
                    news_articles.figure_html(root, 'demo', figure)
        broken = copy.deepcopy(self.articles)
        broken[0]['sections'][0]['figure'] = {'file': 'plot.svg', 'caption': '', 'alt': 'x'}
        with self.assertRaises(ValueError):
            news_articles.validate(broken, self.config, self.papers)

    def test_cross_stream_links_are_reciprocal(self):
        articles = copy.deepcopy(self.articles)
        paper = next(p for p in self.papers if p['status'] == 'approved')
        articles[0]['related_papers'] = [paper['id']]
        with patch.object(news_articles, 'load_articles', return_value=articles):
            output = self.render()
        self.assertIn('Read the research analysis', output[news_articles.article_path(articles[0])])
        self.assertIn('Read the accessible explanation', output[paper_news.paper_path(paper)])
        build.check_output(output)

    def test_empty_article_collection_has_useful_navigation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'content').mkdir()
            (root / 'content/conferences.json').write_text(json.dumps({'checked': '2026-10-28', 'conferences': []}))
            (root / 'content/companies.json').write_text(json.dumps({'checked': '2026-10-30', 'companies': []}))
            (root / 'content/news.json').write_text('{"featured": null}')
            (root / 'content/papers.json').write_text(json.dumps({'papers': []}))
            (root / 'content/tools.json').write_text(json.dumps({'intro': 'Tools.', 'tools': [], 'planned': []}))
            output = {}
            news_articles.render_editorial(root, output, self.book, build.site_logo, build.social_meta, build.json_ld)
            self.assertIn('Our first stories are on the way', output['index.html'])
            self.assertIn('education/index.html', output['index.html'])
            self.assertEqual(ET.fromstring(output['news/articles/feed.xml']).findall('channel/item'), [])

    def test_withdrawal_cleanup_preserves_unmanaged_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, generated in [('news/articles/withdrawn/index.html', True),
                                    ('news/2610.12345/index.html', True),
                                    ('news/papers/2610.54321/index.html', True),
                                    ('news/articles/manual/index.html', False),
                                    ('news/papers/index.html', True)]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(build.GENERATED_NOTE if generated else 'Hand-authored page')
            with patch.object(build, 'ROOT', root):
                stale = {p.relative_to(root).as_posix() for p in build.orphaned_news_pages({})}
            self.assertEqual(stale, {'news/articles/withdrawn/index.html', 'news/2610.12345/index.html',
                                    'news/papers/2610.54321/index.html'})

    def test_local_paper_approval_refreshes_home_and_both_streams(self):
        # Exercise the write selection on an isolated copy; never approve real candidates.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'content').mkdir()
            (root / 'content/papers.json').write_text(json.dumps({'papers': self.papers}))
            (root / 'content/research.json').write_text(json.dumps(self.book))
            paper = next(p for p in self.papers if p['status'] == 'approved')
            output = {'index.html': 'fresh home', 'news/index.html': 'fresh hub',
                      'news/papers/index.html': 'fresh papers', 'news/articles/index.html': 'fresh articles',
                      'sitemap.xml': 'fresh sitemap', 'research/index.html': 'unchanged'}
            with patch.object(news_editor, 'ROOT', root), patch.object(build, 'render', return_value=output), \
                 patch.object(build, 'check_output'), patch.object(build, 'orphaned_news_pages', return_value=[]), \
                 patch.object(build, 'record_generated') as record:
                news_editor.approve([paper['id']])
            for name in output.keys() - {'research/index.html'}:
                self.assertEqual((root / name).read_text(), output[name])
            self.assertFalse((root / 'research/index.html').exists())
            self.assertIn('index.html', record.call_args.args[1])


if __name__ == '__main__':
    unittest.main()
