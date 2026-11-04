"""Editorial approval and publishing boundaries; no paid APIs or posts."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import editorial_pipeline as ep
import build_all


def package():
    return {
        'article': {'slug': 'test-quantum-story', 'title': 'A quantum example',
                    'summary': 'An illustrative test story.', 'author': 'QRC',
                    'published': '2026-11-02', 'status': 'draft', 'topic': 'discoveries',
                    'format': 'Explainer', 'sections': [{'heading': 'Evidence',
                        'paragraphs': ['An example with a source.'], 'source_refs': [1]}],
                    'sources': [{'title': 'Source', 'url': 'https://example.org/paper'}]},
        'scenes': [{'title': 'An example', 'points': ['First observation', 'A limitation'],
                    'narration': 'This is a test of an educational video.'} for _ in range(3)],
        'youtube_title': 'A quantum example', 'x_text': 'Read our explanation.'}


class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.config = ep.read(ep.CONFIG)
        ep.save(self.folder / 'package.json', package())
        initial = ep.read(self.folder / 'package.json')
        initial['storyboard_article_hash'] = ep.article_hash(self.folder)
        ep.save(self.folder / 'package.json', initial)
        ep.save(self.folder / 'research.json', {'text': 'Evidence'})
        self.refresh()
        ep.approve_article(self.folder, 'Editor')
        (self.folder / 'slides.mp4').write_bytes(b'slides-preview')
        ep.save(self.folder / 'slides-render.json', {'package_hash': ep.file_hash(self.folder / 'package.json'),
            'video_hash': ep.file_hash(self.folder / 'slides.mp4'), 'silent': True})
        ep.approve_slides(self.folder, 'Editor')

    def refresh(self, blocking=None, silent=False):
        ep.save(self.folder / 'review.json', {'article_hash': ep.article_hash(self.folder),
                                            'blocking_issues': blocking or []})
        (self.folder / 'video.mp4').write_bytes(b'test-video')
        ep.save(self.folder / 'render.json', {'package_hash': ep.file_hash(self.folder / 'package.json'),
            'video_hash': ep.file_hash(self.folder / 'video.mp4'), 'silent': silent})

    def test_valid_package_matches_site_schema(self):
        ep.validate(package())

    def test_unsafe_slug_rejected(self):
        p = package()
        p['article']['slug'] = '../../bad'
        with self.assertRaises(ValueError): ep.validate(p)

    def test_generated_public_status_rejected(self):
        p = package()
        p['article']['status'] = 'published'
        with self.assertRaises(ValueError): ep.validate(p)

    def test_missing_and_invalid_section_citations_rejected(self):
        for refs in ([], [2], [True]):
            p = package()
            p['article']['sections'][0]['source_refs'] = refs
            with self.assertRaises(ValueError): ep.validate(p)

    def test_script_or_social_limits_rejected(self):
        for key, value in [('x_text', 'https://example.org'), ('youtube_title', 'x'*101), ('scenes', [])]:
            p = package()
            p[key] = value
            with self.assertRaises(ValueError): ep.validate(p)

    def test_html_preview_escapes_text(self):
        p = package()
        p['article']['title'] = '<script>alert(1)</script>'
        ep.save(self.folder / 'package.json', p)
        ep.preview(self.folder)
        text = (self.folder / 'preview.html').read_text()
        self.assertNotIn('<script>', text)
        self.assertIn('&lt;script&gt;', text)

    def test_approval_detects_every_changed_artifact(self):
        for name in ('package.json', 'research.json', 'review.json', 'render.json', 'video.mp4'):
            with self.subTest(name=name):
                ep.approve(self.folder, 'Editor', self.config)
                path = self.folder / name
                before = path.read_bytes()
                path.write_bytes(before + b' ')
                with self.assertRaises(ValueError): ep.check_approval(self.folder, self.config)
                path.write_bytes(before)

    def test_config_changes_invalidate_approval(self):
        ep.approve(self.folder, 'Editor', self.config)
        other = dict(self.config, site_url='https://other.example')
        with self.assertRaises(ValueError): ep.check_approval(self.folder, other)

    def test_blocked_and_silent_packages_cannot_be_approved(self):
        self.refresh(blocking=['Unsupported claim'])
        with self.assertRaises(ValueError): ep.approve(self.folder, 'Editor', self.config)
        self.refresh(silent=True)
        with self.assertRaises(ValueError): ep.approve(self.folder, 'Editor', self.config)

    def test_stale_review_or_render_cannot_be_approved(self):
        p = package()
        p['x_text'] = 'Changed social copy'
        ep.save(self.folder / 'package.json', p)
        with self.assertRaises(ValueError): ep.approve(self.folder, 'Editor', self.config)

    def test_delivery_does_not_repeat_success(self):
        action = Mock(return_value={'id': 'video123'})
        self.assertEqual(ep.once(self.folder, 'youtube', action), {'id': 'video123'})
        ep.once(self.folder, 'youtube', action)
        action.assert_called_once()

    def test_uncertain_delivery_is_not_retried(self):
        action = Mock(side_effect=RuntimeError('network timeout after posting'))
        with self.assertRaises(RuntimeError): ep.once(self.folder, 'x', action)
        with self.assertRaises(ValueError): ep.once(self.folder, 'x', action)
        action.assert_called_once()

    def test_package_lock_rejects_concurrency_and_cleans_up(self):
        with ep.locked(self.folder):
            with self.assertRaises(ValueError):
                with ep.locked(self.folder): pass
        self.assertFalse((self.folder / '.lock').exists())

    def test_production_artifacts_excluded_from_site(self):
        self.assertTrue(build_all.private(Path('content/.production/2026-11-02/preview.html')))
        self.assertTrue(build_all.private(Path('scripts/editorial/.env')))

    def test_incomplete_model_response_rejected(self):
        with self.assertRaises(ValueError): ep.response_text({'status': 'incomplete'})
        with self.assertRaises(ValueError): ep.response_text({'status': 'completed', 'output': []})

    def test_existing_package_resumes_missing_review_only(self):
        (self.folder / 'review.json').unlink()
        with patch.object(ep, 'review') as review, patch.object(ep, 'model') as model:
            ep.prepare(self.folder, '2026-11-02', self.config)
            review.assert_called_once_with(self.folder)
            model.assert_not_called()

    def test_scheduler_waits_for_approval_without_rerendering(self):
        (self.folder / 'article-approval.json').unlink()
        with patch.object(ep, 'prepare'), patch.object(ep, 'render') as render, patch.object(ep, 'publish') as publish:
            ep.run_daily(self.folder, '2026-11-02', self.config)
            render.assert_not_called()
            publish.assert_not_called()

    def test_scheduler_does_not_generate_video_when_review_blocked(self):
        self.refresh(blocking=['Evidence unavailable'])
        (self.folder / 'article-approval.json').unlink()
        with patch.object(ep, 'prepare'), patch.object(ep, 'render') as render:
            ep.run_daily(self.folder, '2026-11-02', self.config)
            render.assert_not_called()

    def test_publish_requires_approval_before_any_network(self):
        with patch.object(ep, 'request') as request:
            with self.assertRaises(FileNotFoundError): ep.publish(self.folder, self.config)
            request.assert_not_called()

    def test_article_only_package_can_be_previewed(self):
        ep.save(self.folder / 'package.json', {'article': package()['article']})
        ep.preview(self.folder)
        self.assertNotIn('<video', (self.folder / 'preview.html').read_text())

    def test_slides_require_article_approval_before_model_call(self):
        (self.folder / 'article-approval.json').unlink()
        with patch.object(ep, 'model') as model:
            with self.assertRaises(FileNotFoundError): ep.slides(self.folder, self.config)
            model.assert_not_called()

    def test_voice_requires_slide_approval_before_network(self):
        (self.folder / 'slides-approval.json').unlink()
        with patch.object(ep, 'request') as request:
            with self.assertRaises(FileNotFoundError): ep.render(self.folder, self.config)
            request.assert_not_called()

    def test_article_edit_invalidates_downstream(self):
        p = package()
        p['article']['summary'] = 'Updated article'
        ep.save(self.folder / 'package.json', p)
        with self.assertRaises(ValueError): ep.check_article(self.folder)
        with self.assertRaises(ValueError): ep.check_slides(self.folder)

    def test_narration_edit_preserves_article_but_invalidates_slides(self):
        p = package()
        p['scenes'][0]['narration'] = 'Updated narration.'
        ep.save(self.folder / 'package.json', p)
        ep.check_article(self.folder)
        with self.assertRaises(ValueError): ep.check_slides(self.folder)

    def test_dirty_checkout_never_written(self):
        with patch.object(ep.subprocess, 'check_output', return_value=' M existing.json\n'), patch.object(ep, 'save') as save:
            with self.assertRaises(ValueError): ep.publish_site(package())
            save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
