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
        broken['scenes'][1]['notes'][0]['on'] = 'a phrase the article never uses'
        broken['scenes'][2]['narration'] = ['Our own words.']
        broken['scenes'][3]['layout'] = 'carousel'
        broken['scenes'][4]['from'] = 'Beyond the qubit count'   # before the previous scene's start
        errors = '\n'.join(videos.validate(broken))
        self.assertIn('"on" 99', errors)
        self.assertIn("'a phrase the article never uses' is in 0", errors)
        self.assertIn('the narration is the article', errors)
        self.assertIn('unknown layout carousel', errors)
        self.assertIn('is not in the article after', errors)

    def test_narration_is_the_whole_article_in_order(self):
        spec = videos.load('beyond-the-qubit-count')
        art = videos.article(spec)
        narrated, errors = videos.plan(spec, art)
        self.assertEqual(errors, [])
        self.assertEqual([x['text'] for said in narrated for x in said], [x['text'] for x in videos.stream(art)])
        spoken = ' '.join(x['text'] for x in videos.stream(art))
        for section in art['sections']:
            for para in section['paragraphs']:
                self.assertIn(' '.join(para.split()), spoken)

    def test_formulas_are_read_aloud_and_shown_plainly(self):
        self.assertEqual(videos.say_tex('2^{n/2}'), '2 to the power n over 2')
        self.assertEqual(videos.say_tex('2d^2'), '2 d squared')
        self.assertEqual(videos.say_tex('\\Lambda\\approx2.1'), 'lambda is about 2.1')
        self.assertEqual(videos.say_tex('H|\\psi\\rangle'), 'H ket psi')
        self.assertEqual(videos.say_tex('(1-p)^N', {'(1-p)^N': 'one minus p, all to the power N'}), 'one minus p, all to the power N')
        with self.assertRaises(ValueError):
            videos.say_tex('\\unknowncommand x')
        self.assertEqual(videos.plain_tex('\\Lambda\\approx12'), 'Λ≈12')
        self.assertEqual(videos.visible('about \\((1-p)^N\\).'), 'about (1-p)ᴺ.')
        self.assertEqual(videos.spoken({'text': 'distance \\(d\\) uses \\(2d^2\\) qubits'}, {}), 'distance d uses 2 d squared qubits')

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
        for chunk in videos.caption_chunks('word ' * 25 + '\\(a + b + c + d\\) ' + 'word ' * 25):
            self.assertEqual(chunk.count('\\('), chunk.count('\\)'))   # never split inside a formula
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

    def test_cues_follow_their_phrases(self):
        spec = videos.load('beyond-the-qubit-count')
        art, settings = videos.article(spec), videos.style()
        index, scene = next((i, s) for i, s in enumerate(spec['scenes']) if s['id'] == 'scaling')
        said = videos.plan(spec, art)[0][index]
        self.assertTrue(said[0]['text'].startswith('The two results below'))
        times = [(1.0 + 5 * k, 5.0 + 5 * k) for k in range(len(said))]
        page = videos.scene_html(spec, art, scene, said, index, times, 5.0 * len(said) + 2, settings, 'light')
        data = json.loads(re.search(r'window\.SCENE = (.*?);</script>', page).group(1))
        series = [c['t'] for c in data['cues'] if c['kind'] == 'series']
        self.assertTrue(times[0][0] < series[0] < times[0][1])   # "use different codes" is mid-sentence
        # a phrase fires inside its sentence, in proportion to where it falls
        k = videos.find('If each trend continued', said)[0]
        self.assertEqual(series[2], times[k][0])
        later = videos.find('but about 21', said)[0]
        self.assertTrue(times[later][0] < series[5] < times[later][1])
        self.assertEqual(series, sorted(series))
        self.assertIn('suppression factor 12', page)   # the figure is inlined, so its marks can be animated
        self.assertIn('<div class="caption" id="c0">', page)   # captions are in the page, so formulas are typeset


class Boundaries(unittest.TestCase):
    def test_generated_video_files_are_never_scanned_or_published(self):
        self.assertIn('_video', site_graph.EXCLUDED)
        self.assertTrue(build_all.private(Path('_video/beyond-the-qubit-count/scenes/open.html')))
        self.assertTrue(build_all.private(Path('requirements-video.txt')))
        self.assertIn('/_video/', (ROOT / '.gitignore').read_text())


if __name__ == '__main__':
    unittest.main()
