"""Article video scripts and the timing logic of scripts/videos.py (no browser, voice or ffmpeg needed)."""
import copy
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_all
import site_graph
import videos


class VideoScripts(unittest.TestCase):
    def test_every_script_is_valid(self):
        for path in sorted(videos.SPECS.glob('*.json')):
            if path.name.startswith('_'):
                continue
            with self.subTest(path.name):
                spec = json.loads(path.read_text())
                self.assertEqual(spec['slug'], path.stem)
                self.assertEqual(videos.validate(spec), [])

    def test_validation_catches_common_mistakes(self):
        spec = videos.load('beyond-the-qubit-count')
        broken = copy.deepcopy(spec)
        broken['scenes'][1]['steps'][0]['on'] = 99
        broken['scenes'][2]['narration'] = ['Write \\(p\\) as maths.']
        broken['scenes'][3]['layout'] = 'carousel'
        errors = '\n'.join(videos.validate(broken))
        self.assertIn('"on" 99', errors)
        self.assertIn('write maths in words', errors)
        self.assertIn('unknown layout carousel', errors)

    def test_style_has_every_setting_the_pipeline_reads(self):
        style = videos.style()
        for key in ('voice', 'fps', 'theme', 'captions', 'lead_in', 'tail', 'sentence_pause', 'fade', 'lexicon'):
            self.assertIn(key, style)
        for key in ('wpm', 'caption_cps_max', 'hold_max_s', 'scene_max_s', 'min_font_px', 'lufs'):
            self.assertIn(key, style['targets'])


class Timing(unittest.TestCase):
    def test_sentences_split_on_full_stops_but_not_abbreviations(self):
        said = videos.sentences('Errors compound, e.g. in long circuits. Distance 7 lasted 2.4 times longer. See Fig. 3 here.')
        self.assertEqual([s['text'] for s in said],
                         ['Errors compound, e.g. in long circuits.', 'Distance 7 lasted 2.4 times longer.', 'See Fig. 3 here.'])
        self.assertEqual(videos.sentences(['One.', {'text': 'Λ ≈ 12', 'say': 'lambda is about twelve'}])[1]['say'],
                         'lambda is about twelve')

    def test_lexicon_changes_speech_only_at_word_boundaries(self):
        lexicon = {'RSA': 'R S A', 'Λ': 'lambda'}
        self.assertEqual(videos.spoken({'text': 'RSA keys, not RSAX; Λ ≈ 2'}, lexicon), 'R S A keys, not RSAX; lambda ≈ 2')
        self.assertEqual(videos.spoken({'text': 'shown', 'say': 'said'}, lexicon), 'said')

    def test_captions_are_short_balanced_and_cover_the_sentence(self):
        text = ('And check whether the logical qubit beats its own parts: in Google\'s 2024 experiment, the '
                'distance-seven logical memory outlived the best physical qubit by a factor of about 2.4.')
        chunks = videos.caption_chunks(text)
        self.assertEqual(' '.join(chunks), text)
        self.assertTrue(all(len(c) <= 84 for c in chunks))
        self.assertGreater(min(map(len, chunks)), 30)
        cues = videos.captions([{'text': text}], [(1.0, 9.0)])
        self.assertEqual((cues[0]['t0'], cues[-1]['t1']), (1.0, 9.0))
        for a, b in zip(cues, cues[1:]):
            self.assertEqual(a['t1'], b['t0'])
        speeds = [len(c['text']) / (c['t1'] - c['t0']) for c in cues]
        self.assertLess(max(speeds) - min(speeds), 0.5)

    def test_cues_follow_their_sentences(self):
        spec = videos.load('beyond-the-qubit-count')
        art, settings = videos.article(spec), videos.style()
        scene = next(s for s in spec['scenes'] if s['id'] == 'scaling')
        n = len(videos.sentences(scene['narration']))
        times = [(1.0 + 5 * k, 5.0 + 5 * k) for k in range(n)]
        page = videos.scene_html(spec, art, scene, 5, times, 5.0 * n + 2, settings, 'light')
        data = json.loads(re.search(r'window\.SCENE = (.*?);</script>', page).group(1))
        series = [c for c in data['cues'] if c['kind'] == 'series']
        self.assertEqual([c['t'] for c in series], [16.0, 21.0, 31.0, 33.5])
        self.assertEqual(len(data['captions']) >= n, True)
        self.assertIn('suppression factor 12', page)   # the figure is inlined, so its marks can be animated


class Boundaries(unittest.TestCase):
    def test_generated_video_files_are_never_scanned_or_published(self):
        self.assertIn('_video', site_graph.EXCLUDED)
        self.assertTrue(build_all.private(Path('_video/beyond-the-qubit-count/scenes/open.html')))
        self.assertTrue(build_all.private(Path('requirements-video.txt')))
        self.assertIn('/_video/', (ROOT / '.gitignore').read_text())


if __name__ == '__main__':
    unittest.main()
