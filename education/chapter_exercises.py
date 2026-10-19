"""End-of-chapter exercises shared by the information, hardware, and programming courses.

Each course keeps its exercises in content/exercises.json, keyed by chapter stem.
An exercise has a kind, a question, hints, a worked answer, and a review anchor
that must exist in the chapter, and may carry Python in optional "code" (shown
with the question) and "answer_code" (shown in the solution). Text is escaped;
write TeX as \\( ... \\).
"""
from html import escape
import json

KINDS = ('Quick check', 'Worked problem', 'Misconception', 'Extension')


def esc(value):
    return escape(str(value), quote=True)


def code(source):
    return f'<pre><code class="language-python">{esc(source)}</code></pre>' if source else ''


def load(root):
    path = root / 'content' / 'exercises.json'
    return json.loads(path.read_text()) if path.exists() else {}


def render(stem, title, items, anchors, search):
    """Return the practice section for one chapter and add its search entries."""
    if not items:
        return ''
    out = ['<section class="chapter-practice" id="practice"><h2>Questions and worked problems</h2>'
           '<p>These exercises draw on the whole chapter. Attempt each question before opening a hint, '
           'explain your reasoning, then compare it with the worked solution.</p>']
    for i, e in enumerate(items, 1):
        if e['kind'] not in KINDS:
            raise ValueError(f'Unknown exercise kind in {stem}: {e["kind"]}')
        if e['review'] not in anchors:
            raise ValueError(f'Exercise review link {e["review"]} missing in {stem}')
        if not e['hints']:
            raise ValueError(f'Exercise {i} in {stem} needs a hint')
        ident = f'exercise-{i}'
        hints = ''.join(f'<details class="exercise-hint"><summary>Hint {n}</summary><p>{esc(h)}</p></details>'
                        for n, h in enumerate(e['hints'], 1))
        out.append(f'<article class="exercise" id="{ident}"><h3>{i}. {esc(e["kind"])} '
                   f'<a class="heading-link" href="#{ident}" aria-label="Link to exercise {i}">§</a></h3>'
                   f'<p>{esc(e["question"])}</p>{code(e.get("code"))}{hints}'
                   f'<details class="exercise-solution"><summary>Worked solution</summary><p>{esc(e["answer"])}</p>'
                   f'{code(e.get("answer_code"))}</details>'
                   f'<p><a href="#{esc(e["review"])}">Revisit the relevant explanation</a></p></article>')
        search.append(dict(title=f'{title} — Exercise {i}', chapter=title, url=f'{stem}.html#{ident}',
                           text=e['question'] + ' ' + e['answer']))
    out.append('</section>')
    return ''.join(out)
