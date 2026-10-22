"""Build lecture decks from the slide manuscripts in content/slides/.

Each manuscript is a list of slides. Every slide has a `kind`:

  section    number, title, question            divider that poses a section's driving question
  figure     title, figure, lead?, takeaway?    one chapter figure, shown large
  steps      title, lead?, steps, takeaway?     a derivation revealed one line at a time
  predict    title, question, answer, hint?     the question first; the answer on the next key press
  compare    title, left, right, takeaway?      two columns, each {label, items}
  statement  title, label, statement, note?     a postulate, definition, or theorem in a box
  table      title, headers, rows, takeaway?    a small comparison table
  takeaways  title, items                       the chapter's conclusions
  content    title, blocks | columns, figure?    a full lecture slide: argument, worked example, figure

A `content` slide holds `blocks` (or `columns`, a list of two block lists). Each block is one of
  {"p": text}  {"math": "\\[...\\]"}  {"ul": [..]}  {"ol": [..]}  {"note": text}
  {"box": {"label", "text"}}  {"table": {"headers", "rows"}}
and may set "reveal": true to appear on the next key press. An optional `figure` is drawn beside
the blocks (`figure_side`: "right", the default) or under them ("below"), with an optional `caption`.

Content slides name the chapter subsection(s) they teach in `topic` (or `topics`);
the build checks that every subsection of the chapter is taught. `notes` holds the
presenter's fuller explanation, shown by the Notes button and never projected.
Strings use the book's TeX delimiters and macros.
"""
import html
import json
from bs4 import BeautifulSoup

e = html.escape


def fragments(items, cls='step'):
    return ''.join(f'<li class="{cls} fragment">{e(x)}</li>' for x in items)


def block(b):
    cls = ' fragment' if b.get('reveal') else ''
    if 'p' in b:
        return f'<p class="para{cls}">{e(b["p"])}</p>'
    if 'math' in b:
        return f'<div class="display{cls}">{e(b["math"])}</div>'
    if 'note' in b:
        return f'<p class="remark{cls}">{e(b["note"])}</p>'
    if 'ul' in b or 'ol' in b:
        tag = 'ul' if 'ul' in b else 'ol'
        return f'<{tag} class="points{cls}">' + ''.join(f'<li>{e(x)}</li>' for x in b[tag]) + f'</{tag}>'
    if 'box' in b:
        return (f'<div class="box{cls}"><p class="box-label">{e(b["box"]["label"])}</p>'
                f'<p>{e(b["box"]["text"])}</p></div>')
    if 'table' in b:
        t = b['table']
        head = ''.join(f'<th scope="col">{e(x)}</th>' for x in t['headers'])
        for row in t['rows']:
            if len(row) != len(t['headers']):
                raise ValueError('Mismatched table row in a content block')
        rows = ''.join('<tr>' + ''.join(f'<td>{e(x)}</td>' for x in row) + '</tr>' for row in t['rows'])
        return f'<table class="deck-table compact{cls}"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'
    raise ValueError(f'Unknown content block: {sorted(b)}')


def render(item, figure_alt):
    kind = item['kind']
    lead = f'<p class="lead">{e(item["lead"])}</p>' if item.get('lead') else ''
    takeaway = f'<p class="takeaway fragment">{e(item["takeaway"])}</p>' if item.get('takeaway') else ''
    if kind == 'section':
        return (f'<p class="section-number">{e(item["number"])}</p><h2>{e(item["title"])}</h2>'
                f'<p class="section-question">{e(item["question"])}</p>')
    if kind == 'figure':
        path = 'assets/figures/' + item['figure']
        return (f'<h2>{e(item["title"])}</h2>{lead}<figure class="stage"><img src="{e(path)}" alt="{e(figure_alt(path))}"></figure>{takeaway}')
    if kind == 'steps':
        return f'<h2>{e(item["title"])}</h2>{lead}<ol class="steps">{fragments(item["steps"])}</ol>{takeaway}'
    if kind == 'predict':
        hint = f'<p class="hint">{e(item["hint"])}</p>' if item.get('hint') else ''
        return (f'<p class="predict-label">Predict</p><h2>{e(item["title"])}</h2><p class="predict-question">{e(item["question"])}</p>{hint}'
                f'<div class="answer fragment"><p class="answer-label">Answer</p><p>{e(item["answer"])}</p></div>')
    if kind == 'compare':
        col = lambda side, cls: (f'<div class="column {cls}"><p class="column-label">{e(side["label"])}</p>'
                                 f'<ul>{"".join(f"<li>{e(x)}</li>" for x in side["items"])}</ul></div>')
        return f'<h2>{e(item["title"])}</h2>{lead}<div class="compare">{col(item["left"], "left")}{col(item["right"], "right fragment")}</div>{takeaway}'
    if kind == 'statement':
        note = f'<p class="statement-note fragment">{e(item["note"])}</p>' if item.get('note') else ''
        return (f'<h2>{e(item["title"])}</h2>{lead}<div class="statement"><p class="statement-label">{e(item["label"])}</p>'
                f'<p class="statement-body">{e(item["statement"])}</p></div>{note}')
    if kind == 'table':
        head = ''.join(f'<th scope="col">{e(x)}</th>' for x in item['headers'])
        rows = ''
        for row in item['rows']:
            if len(row) != len(item['headers']):
                raise ValueError(f'Mismatched table row in slide "{item["title"]}"')
            rows += '<tr>' + ''.join(f'<td>{e(x)}</td>' for x in row) + '</tr>'
        return f'<h2>{e(item["title"])}</h2>{lead}<table class="deck-table"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>{takeaway}'
    if kind == 'content':
        if 'columns' in item:
            text = '<div class="cols">' + ''.join('<div class="col">' + ''.join(block(b) for b in c) + '</div>' for c in item['columns']) + '</div>'
        else:
            text = '<div class="flow">' + ''.join(block(b) for b in item.get('blocks', [])) + '</div>'
        if item.get('figure'):
            path = 'assets/figures/' + item['figure']
            cap = f'<figcaption>{e(item["caption"])}</figcaption>' if item.get('caption') else ''
            fig = f'<figure class="stage"><img src="{e(path)}" alt="{e(figure_alt(path))}">{cap}</figure>'
            side = item.get('figure_side', 'right')
            return f'<h2>{e(item["title"])}</h2><div class="with-figure {side}">{text}{fig}</div>'
        return f'<h2>{e(item["title"])}</h2>{text}'
    if kind == 'takeaways':
        return f'<h2>{e(item["title"])}</h2><ol class="takeaway-list">{fragments(item["items"], "point")}</ol>'
    raise ValueError(f'Unknown slide kind: {kind}')


def build(root, metadata, inline_figures):
    counts = {}
    for number, (stem, title, subtitle, *_) in enumerate(metadata, 1):
        source = root / 'content' / 'slides' / f'{stem}.json'
        if not source.exists():
            continue
        manuscript = BeautifulSoup((root / 'content' / f'{stem}.html').read_text(), 'html.parser')
        illustrations = json.loads((root / 'content/illustrations.json').read_text())
        expected = {x['id'].removeprefix('topic-').replace('-', '.') for x in manuscript.select('.reading-topic')}

        def figure_alt(path):
            if not (root / path).is_file():
                raise ValueError(f'{source.name}: missing figure {path}')
            original = manuscript.find('img', src=path)
            if original is not None:
                return original.get('alt', '')
            name = path.removeprefix('assets/figures/subsections/').removesuffix('.svg')
            if name in illustrations:
                return illustrations[name]['caption']
            raise ValueError(f'{source.name}: figure is not used in the chapter: {path}')

        slides, notes, taught = [], [], set()
        cover = (f'<p class="cover-kicker">Quantum Computing · Chapter {number:02}</p><h1>{e(title)}</h1>'
                 f'<p class="cover-question">{e(subtitle or "")}</p><p class="cover-author">Mithilesh Kumar</p>'
                 '<p class="cover-hint">→ or Space to advance · N for notes · F for fullscreen</p>')
        slides.append((title, 'cover', cover, None))
        notes.append([])
        for item in json.loads(source.read_text()):
            topics = item.get('topics') or ([item['topic']] if item.get('topic') else [])
            for topic in topics:
                if topic not in expected:
                    raise ValueError(f'{source.name}: unknown topic {topic}')
            taught.update(topics)
            heading = item.get('title', '')
            slides.append((heading, item['kind'], render(item, figure_alt), topics[0] if topics else None))
            notes.append(item.get('notes', []))
        if taught != expected:
            raise ValueError(f'{source.name}: subsections without a slide: {sorted(expected - taught)}')

        sections, templates = [], []
        for index, (heading, kind, body, topic) in enumerate(slides, 1):
            link = (f'<a class="book-link" href="{stem}.html#topic-{topic.replace(".", "-")}">§{e(topic)} in the book</a>'
                    if topic else f'<a class="book-link" href="{stem}.html">Read the chapter</a>')
            sections.append(f'<section class="slide kind-{kind}" id="slide-{index}" aria-label="Slide {index}: {e(heading)}">'
                            f'<div class="slide-body">{body}</div><footer class="slide-foot">{link}<span class="slide-no">{index} / {len(slides)}</span></footer></section>')
            templates.append(f'<template id="notes-{index}">' + ''.join(f'<p>{e(p)}</p>' for p in notes[index - 1]) + '</template>')
        options = ''.join(f'<option value="{i}">{i + 1}. {e(h)}</option>' for i, (h, *_) in enumerate(slides))
        page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · Lecture slides</title><meta name="description" content="Lecture slides for Chapter {number} of Quantum Computing: {e(title)}."><link rel="icon" href="../../icons/icon.svg"><link rel="stylesheet" href="assets/presentations.css"><script defer src="assets/source/mathjax-config.js"></script><script defer src="assets/source/vendor/mathjax/tex-svg.js"></script><script defer src="assets/presentations.js"></script></head>
<body class="deck"><a class="skip-link" href="#main">Skip to the slides</a><header class="deck-bar"><a class="deck-back" href="{stem}.html">← Chapter {number:02}: {e(title)}</a><div class="deck-tools"><button id="deck-notes-open" hidden>Notes <kbd>N</kbd></button><button id="deck-fullscreen" hidden>Fullscreen <kbd>F</kbd></button><button id="deck-print" hidden>Print / PDF</button></div></header>
<main id="main" tabindex="-1"><div id="deck">{''.join(sections)}</div></main>{''.join(templates)}
<dialog id="deck-notes" aria-labelledby="deck-notes-title"><button id="deck-notes-close" autofocus>Close</button><h2 id="deck-notes-title">Notes</h2><div id="deck-notes-content"></div></dialog>
<footer class="deck-controls" hidden><select id="slide-select" aria-label="Go to slide">{options}</select><button id="deck-prev" aria-label="Previous">←</button><span id="counter" class="visually-hidden" role="status" aria-live="polite"></span><button id="deck-next" aria-label="Next">→</button></footer><div class="deck-progress" aria-hidden="true"><div id="progress-fill"></div></div></body></html>'''
        document = BeautifulSoup(page, 'html.parser')
        inline_figures(document)
        for control in document.select('svg [role="button"]'):
            for attribute in ('role', 'tabindex', 'aria-pressed'):
                control.attrs.pop(attribute, None)
        (root / f'{stem}-slides.html').write_text(str(document))
        counts[stem] = len(slides)
    return counts
