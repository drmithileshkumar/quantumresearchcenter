#!/usr/bin/env python3
"""Turn news articles into narrated videos: script -> speech -> scenes -> frames -> MP4, plus a review report.

    python3 scripts/videos.py check [slug ...]          validate video scripts (no dependencies)
    python3 scripts/videos.py stills <slug>             speech, one still per scene and the review page (fast)
    python3 scripts/videos.py build <slug>              the full video, captions, transcript and review page

Options: --voice silent|piper:<voice>|recorded, --fps N, --scenes id,id (stills only), --theme light|dark.
Scripts live in content/news-videos/<slug>.json; shared settings in content/news-videos/_style.json.
Everything generated goes to _video/<slug>/ (ignored by git and never published). See content/VIDEO.md.
"""
import argparse
import base64
import functools
import hashlib
import html
import http.server
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / 'content/news-videos'
ARTICLES = ROOT / 'content/news-articles'
TEMPLATE = ROOT / 'scripts/templates/video'
OUT = ROOT / '_video'
W, H, RATE = 1920, 1080, 22050
SLUG = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
# Layout -> fields it requires. Every layout also takes heading, section, source and narration.
LAYOUTS = {'title': {'headline'}, 'statement': {'text'}, 'points': {'items'}, 'stats': {'stats'},
           'figure': {'figure'}, 'equation': {'lines'}, 'table': {'columns', 'rows'}, 'columns': {'columns'},
           'sources': set()}
ABBREVIATIONS = ('e.g.', 'i.e.', 'et al.', 'Dr.', 'Prof.', 'vs.', 'Fig.', 'Eq.', 'No.', 'U.S.', 'St.')


# ---------------------------------------------------------------- script

def style():
    return json.loads((SPECS / '_style.json').read_text())


def load(slug):
    return json.loads((SPECS / f'{slug}.json').read_text())


def article(spec):
    return json.loads((ARTICLES / f"{spec['article']}.json").read_text())


def sentences(narration):
    """Split narration into the units that are spoken, captioned and cued. A list is taken as given;
    each entry is a string or {"text": shown, "say": spoken}."""
    if isinstance(narration, list):
        return [s if isinstance(s, dict) else {'text': s} for s in narration if (s.get('text') if isinstance(s, dict) else s.strip())]
    text, parts, start = ' '.join(narration.split()), [], 0
    for m in re.finditer(r'[.!?]["”’)]?\s+(?=[A-Z0-9"“‘(])', text):
        if text[start:m.end()].strip().endswith(ABBREVIATIONS):
            continue
        parts.append(text[start:m.end()].strip())
        start = m.end()
    parts.append(text[start:].strip())
    return [{'text': p} for p in parts if p]


def spoken(sentence, lexicon):
    """The text sent to the voice: an explicit "say", else the shown text with the lexicon applied."""
    if 'say' in sentence:
        return sentence['say']
    text = sentence['text']
    for written, said in sorted(lexicon.items(), key=lambda kv: -len(kv[0])):
        if re.fullmatch(r'\w[\w\s.-]*\w|\w', written):
            text = re.sub(rf'(?<![\w-]){re.escape(written)}(?![\w-])', said, text)
        else:
            text = text.replace(written, said)
    return text


def caption_chunks(text, limit=84):
    """Break a sentence into captions of at most two short lines, preferring breaks after punctuation."""
    spaces = [m.start() for m in re.finditer(' ', text)]
    n = math.ceil(len(text) / limit)
    while True:
        cuts, prev = [], -1
        for k in range(1, n):   # the space nearest each equal share, with a pull towards punctuation
            ideal = k * len(text) / n
            options = [s for s in spaces if s > prev] or [prev]
            prev = min(options, key=lambda s: abs(s - ideal) - (12 if text[s - 1] in ',;:—' else 0))
            cuts.append(prev)
        edges = [-1] + cuts + [len(text)]
        chunks = [text[a + 1:b].strip() for a, b in zip(edges, edges[1:])]
        if all(len(c) <= limit for c in chunks) or n > len(spaces):
            return [c for c in chunks if c]
        n += 1


def chart_groups(svg_text):
    """Number of revealable mark groups: top-level elements with their own <title> (see video.js)."""
    root = ET.fromstring(svg_text)
    return sum(1 for el in root if any(c.tag.endswith('title') for c in el))


def figure_path(spec, name):
    return ARTICLES / 'figures' / spec['article'] / name


def cue_refs(node):
    """Every "on" value in a scene, wherever it is nested."""
    if isinstance(node, dict):
        if 'on' in node:
            yield node['on']
        for key, value in node.items():
            if key not in ('on', 'narration'):
                yield from cue_refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from cue_refs(value)


def validate(spec):
    errors = []
    for key in ('slug', 'article', 'status', 'scenes'):
        if key not in spec:
            errors.append(f'missing {key}')
    if errors:
        return errors
    if not (ARTICLES / f"{spec['article']}.json").exists():
        return [f"no article {spec['article']}"]
    if spec['status'] not in ('draft', 'ready'):
        errors.append('status must be draft or ready')
    ids = [s.get('id') for s in spec['scenes']]
    if len(set(ids)) != len(ids):
        errors.append('scene ids repeat')
    for scene in spec['scenes']:
        where = f"scene {scene.get('id')}"
        if not SLUG.match(str(scene.get('id', ''))):
            errors.append(f'{where}: id must be lowercase words joined by hyphens')
        layout = scene.get('layout')
        if layout not in LAYOUTS:
            errors.append(f'{where}: unknown layout {layout}')
            continue
        for key in LAYOUTS[layout] - set(scene):
            errors.append(f'{where}: {layout} needs {key}')
        said = sentences(scene.get('narration') or [])
        if not said:
            errors.append(f'{where}: no narration')
        for s in said:
            if '\\' in s['text'] or '$' in s['text']:
                errors.append(f'{where}: narration is spoken and captioned, so write maths in words: {s["text"][:40]}')
        for on in cue_refs({k: v for k, v in scene.items() if k != 'narration'}):
            if not (isinstance(on, int) and 0 <= on < len(said)):
                errors.append(f'{where}: "on" {on!r} is not a sentence number 0 to {len(said) - 1}')
        if layout == 'figure':
            path = figure_path(spec, scene['figure'])
            if not path.exists():
                errors.append(f'{where}: no figure {path.relative_to(ROOT)}')
                continue
            groups = chart_groups(path.read_text())
            for step in scene.get('steps', []):
                if any(not 0 <= k < groups for k in step['series']):
                    errors.append(f'{where}: figure has {groups} mark groups, step asks for {step["series"]}')
        if layout == 'table':
            width = len(scene['columns'])
            for row in scene['rows']:
                cells = row['cells'] if isinstance(row, dict) else row
                if len(cells) != width:
                    errors.append(f'{where}: a row has {len(cells)} cells for {width} columns')
            if 'column_on' in scene and len(scene['column_on']) != width:
                errors.append(f'{where}: column_on needs one entry per column')
    return errors


# ---------------------------------------------------------------- tools

def ffmpeg():
    exe = shutil.which('ffmpeg')
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit('ffmpeg not found: install it, or pip install -r requirements-video.txt')


def chrome_exe():
    for name in (os.environ.get('CHROME'), 'google-chrome', 'chromium', 'chromium-browser', 'google-chrome-stable'):
        if name and shutil.which(name):
            return shutil.which(name)
    sys.exit('Chrome or Chromium not found; set CHROME to its path')


def sha(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else str(p).encode())
        h.update(b'\0')
    return h.hexdigest()[:20]


def read_pcm(path):
    with wave.open(str(path)) as w:
        assert w.getframerate() == RATE and w.getnchannels() == 1 and w.getsampwidth() == 2, path
        return w.readframes(w.getnframes())


def write_wav(path, pcm):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm)


def silence(seconds):
    return b'\0\0' * int(round(seconds * RATE))


def conform(src, dst):
    """Convert any audio file to the pipeline's format: mono, 16-bit, 22.05 kHz."""
    subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-i', str(src), '-ac', '1', '-ar', str(RATE),
                    '-sample_fmt', 's16', str(dst)], check=True)


# ---------------------------------------------------------------- voices

class Silent:
    """Silence at a set reading pace: fast, for checking layout and timing without a voice."""
    def __init__(self, settings):
        self.wpm = settings.get('silent_wpm', 160)
        self.key = f'silent:{self.wpm}'

    def synth(self, text, path):
        write_wav(path, silence(max(0.6, len(text.split()) * 60 / self.wpm)))


class Piper:
    """Local neural voice (pip install piper-tts). Voices download once into _video/voices/."""
    def __init__(self, name, settings):
        self.name, self.length_scale = name, settings.get('length_scale', 1.0)
        self.key = f'piper:{name}:{self.length_scale}'
        self.voice = None

    def synth(self, text, path):
        from piper import PiperVoice, SynthesisConfig
        if self.voice is None:
            model = OUT / 'voices' / f'{self.name}.onnx'
            if not model.exists():
                model.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run([sys.executable, '-m', 'piper.download_voices', '--data-dir', str(model.parent), self.name], check=True)
            self.voice = PiperVoice.load(str(model))
        raw = path.with_suffix('.raw.wav')
        with wave.open(str(raw), 'wb') as w:
            self.voice.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=self.length_scale))
        conform(raw, path)
        raw.unlink()


def voice(name, settings):
    if name == 'silent':
        return Silent(settings)
    if name.startswith('piper:'):
        return Piper(name.split(':', 1)[1], settings)
    if name == 'recorded':
        return None
    sys.exit(f'unknown voice {name}')


def scene_audio(spec, scene, backend, settings, fps):
    """Speech for one scene: (pcm, sentence times, duration). The duration is a whole number of frames."""
    said = sentences(scene['narration'])
    lead, pause = settings['lead_in'], scene.get('pause', settings['sentence_pause'])
    tail = settings['tail'] + scene.get('hold', 0)
    cache = OUT / 'cache' / 'speech'
    cache.mkdir(parents=True, exist_ok=True)
    if backend is None:   # recorded: one file per scene, sentence times shared out by length
        found = sorted((SPECS / spec['slug']).glob(f"{scene['id']}.*"))
        if not found:
            sys.exit(f"recorded voice: no {SPECS.relative_to(ROOT)}/{spec['slug']}/{scene['id']}.wav (or .mp3, .m4a)")
        wav = cache / f"rec-{sha(found[0].read_bytes())}.wav"
        if not wav.exists():
            conform(found[0], wav)
        speech = read_pcm(wav)
        total, weights = len(speech) / 2 / RATE, [len(s['text']) for s in said]
        times, t = [], lead
        for w_ in weights:
            times.append((t, t + total * w_ / sum(weights)))
            t = times[-1][1]
        pcm, end = silence(lead) + speech, lead + total
    else:
        pieces, times, t = [silence(lead)], [], lead
        for i, s in enumerate(said):
            text = spoken(s, settings.get('lexicon', {}))
            wav = cache / f'{sha(backend.key, text)}.wav'
            if not wav.exists():
                backend.synth(text, wav)
            clip = read_pcm(wav)
            times.append((t, t + len(clip) / 2 / RATE))
            pieces.append(clip)
            t = times[-1][1]
            if i < len(said) - 1:
                pieces.append(silence(pause))
                t += pause
        pcm, end = b''.join(pieces), t
    frames = math.ceil((end + tail) * fps)
    duration = frames / fps
    samples = int(round(duration * RATE))
    pcm = (pcm + silence(duration))[:2 * samples]
    return pcm, times, duration


def captions(said, times):
    cues = []
    """Caption cues for spoken sentences: each sentence's time is shared among its chunks by length."""
    for s, (start, end) in zip(said, times):
        chunks = caption_chunks(s['text'])
        total, done = sum(len(c) for c in chunks), 0
        for c in chunks:
            t0 = start + (end - start) * done / total
            done += len(c)
            cues.append({'t0': round(t0, 3), 't1': round(start + (end - start) * done / total, 3), 'text': c})
    return cues


# ---------------------------------------------------------------- scenes

def esc(text):
    return html.escape(str(text), quote=False)


def rich(item):
    """A text item: plain text (inline \\(..\\) maths allowed) or {"tex": display formula}."""
    if isinstance(item, dict) and 'tex' in item:
        return f'<span class="math">\\({esc(item["tex"])}\\)</span>'
    return esc(item['text'] if isinstance(item, dict) else item)


class Page:
    """Collects revealable elements and their cue times while a layout is written."""
    def __init__(self, times, settings):
        self.times, self.cues, self.n, self.fade = times, [], 0, settings['fade']

    def time(self, item, default):
        on = item.get('on', default) if isinstance(item, dict) else default
        if on is None:
            return 0.0
        return self.times[on][0] + (item.get('delay', 0) if isinstance(item, dict) else 0)

    def spread(self, i, n):
        return min(len(self.times) - 1, (i + 1) * len(self.times) // (n + 1))

    def el(self, tag, cls, inner, t, attrs=''):
        name = f'e{self.n}'
        self.n += 1
        self.cues.append({'id': name, 't': round(t, 3), 'dur': self.fade, 'kind': 'fade'})
        return f'<{tag} id="{name}" class="reveal {cls}"{attrs}>{inner}</{tag}>'

    def heading(self, scene):
        return self.el('h2', '', esc(scene['heading']), 0.0) if scene.get('heading') else ''


def layout_title(p, scene, spec, art):
    out = p.el('div', 'kicker', esc(scene.get('kicker', art.get('format', ''))), 0.0)
    out += p.el('h1', '', esc(scene['headline']), 0.25)
    # deck and banner appear early unless given {"on": sentence}
    if scene.get('deck'):
        out += p.el('div', 'deck', rich(scene['deck']), p.time(scene['deck'], None) or 0.7)
    if scene.get('banner'):
        svg = figure_path(spec, art['banner']['file']).read_text()
        out += p.el('div', 'banner', svg, p.time(scene['banner'], None) or 1.1)
    return out


def layout_statement(p, scene, spec, art):
    out = p.el('div', 'text', rich(scene['text']), p.time(scene['text'], 0))
    if scene.get('sub'):
        out += p.el('div', 'sub', rich(scene['sub']), p.time(scene['sub'], len(p.times) - 1))
    return p.heading(scene) + out


def layout_points(p, scene, spec, art):
    items = scene['items']
    lis = ''.join(p.el('li', '', rich(it), p.time(it, p.spread(i, len(items)))) for i, it in enumerate(items))
    return p.heading(scene) + f'<ul>{lis}</ul>'


def layout_stats(p, scene, spec, art):
    stats = scene['stats']
    row = ''.join(p.el('div', 'stat', f'<div class="value">{esc(s["value"])}</div><div class="label">{rich(s["label"])}</div>',
                       p.time(s, p.spread(i, len(stats)))) for i, s in enumerate(stats))
    return p.heading(scene) + f'<div class="row">{row}</div>'


def layout_figure(p, scene, spec, art):
    svg = re.sub(r'^<\?xml[^>]*>\s*', '', figure_path(spec, scene['figure']).read_text())
    chart = f'chart{p.n}'
    p.cues.append({'id': f'{chart}-box', 't': 0.2, 'dur': p.fade, 'kind': 'fade'})
    steps = scene.get('steps') or [{'series': list(range(chart_groups(svg))), 'on': scene.get('on', 0)}]
    for step in steps:
        p.cues.append({'id': chart, 't': round(p.time(step, 0), 3), 'dur': step.get('dur', 1.8),
                       'kind': 'series', 'series': step['series']})
    notes = ''
    for i, note in enumerate(scene.get('notes', [])):
        key = f'<span class="key" style="background:var(--{note["key"]})"></span>' if isinstance(note, dict) and note.get('key') else ''
        cls = 'note math' if isinstance(note, dict) and 'tex' in note else 'note'
        notes += p.el('div', cls, key + rich(note), p.time(note, p.spread(i, len(scene['notes']))))
    body = (f'<div class="body"><div class="chart" id="{chart}"><div id="{chart}-box" class="reveal">{svg}</div></div>'
            f'<div class="notes">{notes}</div></div>')
    return p.heading(scene) + body


def layout_equation(p, scene, spec, art):
    lines = ''
    for i, line in enumerate(scene['lines']):
        note = f'<div class="note">{rich(line["note"])}</div>' if line.get('note') else ''
        lines += p.el('div', 'line', f'<div class="tex">\\[{esc(line["tex"])}\\]</div>{note}',
                      p.time(line, p.spread(i, len(scene['lines']))))
    return p.heading(scene) + f'<div class="lines">{lines}</div>'


def layout_table(p, scene, spec, art):
    col_t = [0.0 if on is None else p.times[on][0] for on in scene.get('column_on', [None] * len(scene['columns']))]
    head = ''.join(p.el('th', '', esc(c), col_t[j]) for j, c in enumerate(scene['columns']))
    rows = ''
    for i, row in enumerate(scene['rows']):
        cells = row['cells'] if isinstance(row, dict) else row
        rt = p.time(row if isinstance(row, dict) else {}, p.spread(i, len(scene['rows'])))
        # a cell given as {"text", "on"} keeps its own time; others wait for their row and column
        rows += '<tr>' + ''.join(p.el('td', '', rich(c), p.time(c, None) if isinstance(c, dict) and 'on' in c else max(rt, col_t[j]))
                                 for j, c in enumerate(cells)) + '</tr>'
    foot = ''.join(p.el('p', 'foot', rich(it), p.time(it, len(p.times) - 1)) for it in scene.get('footer', []))
    size = 'small' if scene.get('small') else ''
    return p.heading(scene) + f'<div class="{size}"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>{foot}</div>'


def layout_columns(p, scene, spec, art):
    cols = ''
    for j, col in enumerate(scene['columns']):
        items = ''.join(p.el('p', '', rich(it), p.time(it, 0)) for it in col['items'])
        cols += f'<div class="col c{j}"><h3>{esc(col["title"])}</h3>{items}</div>'
    return p.heading(scene) + f'<div class="cols">{cols}</div>'


def layout_sources(p, scene, spec, art):
    items = scene.get('items') or [s['title'] for s in art.get('sources', [])]
    lis = ''.join(f'<li>{esc(s)}</li>' for s in items)
    url = scene.get('url', f"quantumresearch.center/news/articles/{art['slug']}/")
    return (p.heading(scene) + p.el('ol', '', lis, 0.3)
            + p.el('div', 'url', esc(url), p.time(scene, len(p.times) - 1)))


def scene_html(spec, art, scene, index, times, duration, settings, theme):
    p = Page(times, settings)
    stage = globals()[f"layout_{scene['layout']}"](p, scene, spec, art)
    said = sentences(scene['narration'])
    data = {'duration': duration, 'cues': p.cues, 'captions': captions(said, times) if settings['captions'] else []}
    progress = ''.join(f'<i class="{"now" if k == index else "done" if k < index else ""}"></i>'
                       for k in range(len(spec['scenes'])))
    source = f'<div class="source"><b>Source</b> · {esc(scene["source"])}</div>' if scene.get('source') else ''
    return f'''<!doctype html><html lang="en" data-theme="{theme}"><head><meta charset="utf-8"><title>{esc(scene['id'])}</title>
<link rel="stylesheet" href="/scripts/templates/video/video.css">
<script src="/education/computing/assets/source/mathjax-config.js"></script>
<script src="/education/computing/assets/source/vendor/mathjax/tex-svg.js"></script></head>
<body class="{scene['layout']}"><div class="frame-top"><span>Quantum Research Center</span><span class="section">{esc(scene.get('section', ''))}</span></div>
<div class="stage">{stage}</div><div class="caption"></div>{source}<div class="progress">{progress}</div>
<script>window.SCENE = {json.dumps(data)};</script><script src="/scripts/templates/video/video.js"></script></body></html>'''


# ---------------------------------------------------------------- browser

class Chrome:
    """Headless Chrome over the DevTools pipe, serving the repository on a local port."""
    def __init__(self):
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        handler = functools.partial(Quiet, directory=str(ROOT))
        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        r1, w1 = os.pipe()
        r2, w2 = os.pipe()

        def fds():   # Chrome reads commands on fd 3 and writes replies on fd 4
            a, b = os.dup(r1), os.dup(w2)
            os.dup2(a, 3)
            os.dup2(b, 4)
        self.profile = tempfile.mkdtemp(prefix='video-chrome-')
        self.proc = subprocess.Popen([chrome_exe(), '--headless=new', '--remote-debugging-pipe', f'--user-data-dir={self.profile}',
                                      '--no-first-run', '--hide-scrollbars', '--force-color-profile=srgb',
                                      '--font-render-hinting=none', '--disable-gpu', 'about:blank'],
                                     preexec_fn=fds, close_fds=False,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(r1)
        os.close(w2)
        self.w, self.r, self.buf, self.mid = os.fdopen(w1, 'wb'), os.fdopen(r2, 'rb'), b'', 0
        target = self.send('Target.createTarget', {'url': 'about:blank'})['targetId']
        self.session = self.send('Target.attachToTarget', {'targetId': target, 'flatten': True})['sessionId']
        self.send('Emulation.setDeviceMetricsOverride', {'width': W, 'height': H, 'deviceScaleFactor': 1, 'mobile': False})
        self.send('Page.enable')

    def send(self, method, params=None):
        self.mid += 1
        msg = {'id': self.mid, 'method': method, 'params': params or {}}
        if getattr(self, 'session', None):
            msg['sessionId'] = self.session
        self.w.write(json.dumps(msg).encode() + b'\0')
        self.w.flush()
        while True:
            while b'\0' not in self.buf:
                chunk = os.read(self.r.fileno(), 1 << 20)
                if not chunk:
                    sys.exit('Chrome closed unexpectedly')
                self.buf += chunk
            line, self.buf = self.buf.split(b'\0', 1)
            m = json.loads(line)
            if m.get('id') == self.mid:
                if 'error' in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get('result', {})

    def eval(self, expression):
        r = self.send('Runtime.evaluate', {'expression': expression, 'awaitPromise': True, 'returnByValue': True})
        if 'exceptionDetails' in r:
            raise RuntimeError(f"{expression[:40]}: {r['exceptionDetails'].get('exception', {}).get('description')}")
        return r['result'].get('value')

    def open(self, path):
        url = f'http://127.0.0.1:{self.server.server_address[1]}/{path.relative_to(ROOT).as_posix()}'
        self.send('Page.navigate', {'url': url})
        for _ in range(300):
            if self.eval("document.readyState === 'complete' && !!window.__ready"):
                return self.eval('window.__ready')
            time.sleep(0.1)
        sys.exit(f'scene did not load: {url}')

    def shot(self):
        return base64.b64decode(self.send('Page.captureScreenshot', {'format': 'png', 'optimizeForSpeed': True})['data'])

    def close(self):
        self.proc.kill()
        self.server.shutdown()
        shutil.rmtree(self.profile, ignore_errors=True)


def render(chrome, page, duration, fps, out):
    """Encode one scene: seek every frame, screenshot only when the picture changes."""
    proc = subprocess.Popen([ffmpeg(), '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'png',
                             '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                             '-r', str(fps), str(out)], stdin=subprocess.PIPE)
    chrome.open(page)
    last_sig, frame, shots = None, None, 0
    for k in range(round(duration * fps)):
        sig = chrome.eval(f'__seek({k / fps})')
        if sig != last_sig:
            frame, last_sig, shots = chrome.shot(), sig, shots + 1
        proc.stdin.write(frame)
    proc.stdin.close()
    if proc.wait():
        sys.exit(f'ffmpeg failed on {page.name}')
    return shots


# ---------------------------------------------------------------- pipeline

def prepare(slug, voice_name, fps, theme, only=None):
    """Speech, timings and scene pages for every scene (cached), as a list of per-scene records."""
    settings, spec = style(), load(slug)
    errors = validate(spec)
    if errors:
        sys.exit('\n'.join([f'{slug}: script errors'] + errors))
    art, backend = article(spec), voice(voice_name or spec.get('voice') or settings['voice'], settings)
    folder = OUT / slug
    (folder / 'scenes').mkdir(parents=True, exist_ok=True)
    records = []
    for index, scene in enumerate(spec['scenes']):
        if only and scene['id'] not in only:
            continue
        print(f"  speech  {scene['id']}", flush=True)
        pcm, times, duration = scene_audio(spec, scene, backend, settings, fps)
        page = folder / 'scenes' / f"{scene['id']}.html"
        page.write_text(scene_html(spec, art, scene, index, times, duration, settings, theme))
        records.append({'scene': scene, 'pcm': pcm, 'times': times, 'duration': duration, 'page': page,
                        'sentences': sentences(scene['narration'])})
    return spec, settings, records


def stills(chrome, folder, records, settings):
    (folder / 'review').mkdir(exist_ok=True)
    for r in records:
        chrome.open(r['page'])
        r['issues'] = chrome.eval(f"__audit({settings['targets']['min_font_px']})")
        chrome.eval(f"__seek({r['duration']})")
        (folder / 'review' / f"{r['scene']['id']}.png").write_bytes(chrome.shot())
        print(f"  still   {r['scene']['id']}: {len(r['issues'])} layout issue(s)", flush=True)


def metrics(records, settings):
    """Per-scene measurements against the targets in _style.json; returns (rows, flag count)."""
    t, rows, flags = settings['targets'], [], 0
    for r in records:
        said, times = r['sentences'], r['times']
        words = sum(len(s['text'].split()) for s in said)
        speech = times[-1][1] - times[0][0]
        caps = captions(said, times)
        cps = max(len(c['text']) / max(c['t1'] - c['t0'], 0.01) for c in caps)
        events = sorted({0.0, r['duration']} | {c['t'] for c in json.loads(
            re.search(r'window\.SCENE = (.*?);</script>', r['page'].read_text()).group(1))['cues']})
        hold = max(b - a for a, b in zip(events, events[1:]))
        row = {'id': r['scene']['id'], 'duration': round(r['duration'], 1), 'words': words,
               'wpm': round(words / speech * 60), 'max_cps': round(cps, 1), 'longest_hold': round(hold, 1),
               'issues': list(r.get('issues', []))}
        lo, hi = t['wpm']
        if not lo <= row['wpm'] <= hi:
            row['issues'].append(f"pace {row['wpm']} words a minute (target {lo} to {hi})")
        if cps > t['caption_cps_max']:
            row['issues'].append(f"captions reach {cps:.0f} characters a second (target at most {t['caption_cps_max']})")
        if hold > t['hold_max_s']:
            row['issues'].append(f"picture unchanged for {hold:.0f} s (target at most {t['hold_max_s']})")
        if r['duration'] > t['scene_max_s']:
            row['issues'].append(f"scene lasts {r['duration']:.0f} s (target at most {t['scene_max_s']})")
        flags += len(row['issues'])
        rows.append(row)
    return rows, flags


def loudness(path):
    out = subprocess.run([ffmpeg(), '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    summary = out[out.rfind('Summary:'):]
    lufs = re.search(r'I:\s+(-?[\d.]+) LUFS', summary)
    peak = re.search(r'Peak:\s+(-?[\d.]+) dBFS', summary)
    return (float(lufs.group(1)) if lufs else None, float(peak.group(1)) if peak else None)


def review(folder, slug, spec, settings, records, rows, flags, voice_name, fps, video=None):
    """Write review/index.html and append a line to history.jsonl, then compare with the previous run."""
    total = sum(r['duration'] for r in records)
    entry = {'when': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'voice': voice_name, 'fps': fps,
             'scenes': len(records), 'duration': round(total, 1), 'flags': flags, 'video': bool(video),
             'per_scene': {row['id']: len(row['issues']) for row in rows}}
    if video:
        entry['lufs'], entry['peak_db'] = loudness(video)
        target = settings['targets']['lufs']
        if entry['lufs'] is not None and abs(entry['lufs'] - target) > 1.5:
            entry['flags'] += 1
            entry['loudness_issue'] = f"loudness {entry['lufs']} LUFS (target {target})"
    history = folder / 'history.jsonl'
    previous = [json.loads(l) for l in history.read_text().splitlines()] if history.exists() else []
    with history.open('a') as f:
        f.write(json.dumps(entry) + '\n')
    trs = ''
    for r, row in zip(records, rows):
        lines = ''.join(f'<li><span class="t">{t0:.1f}s</span> {esc(s["text"])}</li>' for s, (t0, _) in zip(r['sentences'], r['times']))
        issues = ''.join(f'<li>{esc(i)}</li>' for i in row['issues']) or '<li class="ok">No automatic issues</li>'
        trs += (f'<tr><td><img src="{row["id"]}.png" alt=""><div class="id">{esc(row["id"])} · {row["duration"]} s · '
                f'{row["wpm"]} wpm · captions ≤ {row["max_cps"]} cps · longest hold {row["longest_hold"]} s</div></td>'
                f'<td><ol>{lines}</ol><ul class="issues">{issues}</ul></td></tr>')
    player = f'<video controls src="../{slug}.mp4" poster="{records[0]["scene"]["id"]}.png"></video>' if video else ''
    past = ''.join(f'<tr><td>{esc(h["when"])}</td><td>{esc(h["voice"])}</td><td>{h["duration"]} s</td><td>{h["flags"]}</td></tr>'
                   for h in (previous + [entry])[-12:])
    loud = f" · loudness {entry.get('lufs')} LUFS, peak {entry.get('peak_db')} dB" if video else ''
    (folder / 'review' / 'index.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Review: {esc(slug)}</title><style>
body{{font:16px/1.5 Inter,system-ui,sans-serif;margin:32px auto;max-width:1500px;padding:0 24px;color:#30343b;background:#fcfcfb}}
img{{width:640px;display:block;border:1px solid #dce3ea}} video{{width:100%;max-width:1280px;display:block;margin:20px 0}}
table{{border-collapse:collapse;width:100%}} td,th{{vertical-align:top;padding:12px;border-bottom:1px solid #e6e8eb;text-align:left}}
.id{{font-size:13px;color:#646a71;margin-top:6px}} .t{{color:#646a71;font-variant-numeric:tabular-nums;margin-right:6px}}
.issues li{{color:#934d36}} .issues li.ok{{color:#2f7a5b}} ol{{padding-left:20px;margin:0 0 10px}} h2{{margin-top:36px}}
</style></head><body><h1>Review: {esc(spec['article'])}</h1>
<p>{len(records)} scenes · {total / 60:.1f} min · voice {esc(voice_name)} · {fps} fps · <b>{entry['flags']} automatic flag(s)</b>{loud}.
{esc(entry.get('loudness_issue', ''))} Score the video against the human rubric in content/VIDEO.md and record what you change in the script's "revisions".</p>
{player}<table>{trs}</table><h2>Runs</h2><table><tr><th>When</th><th>Voice</th><th>Length</th><th>Flags</th></tr>{past}</table></body></html>''')
    if previous:
        before = previous[-1]
        print(f"  flags {before['flags']} -> {entry['flags']}, length {before['duration']} s -> {entry['duration']} s")
    return entry


def vtt(records):
    def stamp(s):
        return f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{s % 60:06.3f}'
    out, offset = ['WEBVTT', ''], 0.0
    for r in records:
        for c in captions(r['sentences'], r['times']):
            out += [f"{stamp(offset + c['t0'])} --> {stamp(offset + c['t1'])}", c['text'], '']
        offset += r['duration']
    return '\n'.join(out)


def transcript(spec, records):
    return '\n\n'.join(f"[{r['scene'].get('section') or r['scene']['id']}]\n" + ' '.join(s['text'] for s in r['sentences'])
                       for r in records) + '\n'


def run(args):
    settings = style()
    fps = args.fps or settings['fps']
    theme = args.theme or settings['theme']
    voice_name = args.voice or load(args.slug).get('voice') or settings['voice']
    only = set(args.scenes.split(',')) if getattr(args, 'scenes', None) else None
    spec, settings, records = prepare(args.slug, voice_name, fps, theme, only)
    folder = OUT / args.slug
    chrome = Chrome()
    try:
        stills(chrome, folder, records, settings)
        video = None
        if args.command == 'build':
            segments = folder / 'segments'
            segments.mkdir(exist_ok=True)
            assets = b''.join(p.read_bytes() for p in sorted(TEMPLATE.iterdir()))
            parts = []
            for r in records:
                seg = segments / f"{sha(r['page'].read_text(), assets, fps)}.mp4"
                if not seg.exists():
                    started = time.time()
                    shots = render(chrome, r['page'], r['duration'], fps, seg)
                    print(f"  render  {r['scene']['id']}: {shots} distinct frames, {time.time() - started:.0f} s", flush=True)
                parts.append(seg)
            (folder / 'segments.txt').write_text(''.join(f"file '{p}'\n" for p in parts))
            write_wav(folder / 'speech.wav', b''.join(r['pcm'] for r in records))
            video = folder / f'{args.slug}.mp4'
            subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(folder / 'segments.txt'),
                            '-i', str(folder / 'speech.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                            '-af', f"loudnorm=I={settings['targets']['lufs']}:TP=-1.5:LRA=11", '-ar', '48000',
                            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(video)], check=True)
            (folder / f'{args.slug}.vtt').write_text(vtt(records))
            (folder / f'{args.slug}.txt').write_text(transcript(spec, records))
    finally:
        chrome.close()
    rows, flags = metrics(records, settings)
    entry = review(folder, args.slug, spec, settings, records, rows, flags, voice_name, fps, video)
    print(f"{args.slug}: {len(records)} scenes, {entry['duration'] / 60:.1f} min, {entry['flags']} flag(s)")
    if video:
        print(f'  video   {video.relative_to(ROOT)}')
    print(f"  review  {(folder / 'review/index.html').relative_to(ROOT)}")


def check(slugs):
    slugs = slugs or sorted(p.stem for p in SPECS.glob('*.json') if not p.name.startswith('_'))
    bad = 0
    for slug in slugs:
        errors = validate(load(slug))
        bad += bool(errors)
        print(f'{slug}: ' + ('ok' if not errors else '\n  ' + '\n  '.join(errors)))
    return 1 if bad else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check').add_argument('slugs', nargs='*')
    for name in ('stills', 'build'):
        p = sub.add_parser(name)
        p.add_argument('slug')
        p.add_argument('--voice')
        p.add_argument('--fps', type=int)
        p.add_argument('--theme', choices=('light', 'dark'))
        if name == 'stills':
            p.add_argument('--scenes', help='comma-separated scene ids')
    args = parser.parse_args()
    if args.command == 'check':
        sys.exit(check(args.slugs))
    run(args)


if __name__ == '__main__':
    main()
