"""Static accessibility checks for every published page (WCAG basics that markup alone can show)."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {'.git', 'content', 'source', 'vendor', 'templates', 'tests'}

class Audit(HTMLParser):
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
    def __init__(self, text):
        super().__init__()
        self.problems, self.ids, self.labels = [], [], set()
        self.lang = self.title = self.redirect = self.skip_link = self.stylesheet = False
        self.h1 = 0
        self.stack = []        # open elements: [tag, attrs, text]
        self.controls = []     # (description, id, labelled)
        self.title_text = ''
        self.feed(text)
        for description, ident, labelled in self.controls:
            if not labelled and ident not in self.labels:
                self.problems.append(f'form control without a label: {description}')

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'html': self.lang = bool(a.get('lang', '').strip())
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh': self.redirect = True
        if tag == 'meta' and a.get('name') == 'viewport' and re.search(r'user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b', a.get('content', '')):
            self.problems.append('viewport blocks zooming')
        if tag == 'link' and a.get('rel') == 'stylesheet': self.stylesheet = True
        if tag == 'a' and a.get('href') in ('#main', '#content') and 'skip-link' in a.get('class', ''): self.skip_link = True
        if tag == 'h1': self.h1 += 1
        if tag == 'img' and 'alt' not in a: self.problems.append(f'image without alt: {a.get("src", "?")}')
        if a.get('tabindex', '0').lstrip('-').isdigit() and int(a.get('tabindex', '0')) > 0:
            self.problems.append(f'positive tabindex on <{tag}>')
        if tag == 'label' and a.get('for'): self.labels.add(a['for'])
        inside_label = any(t == 'label' for t, _, _ in self.stack)
        named = bool(a.get('aria-label') or a.get('aria-labelledby') or a.get('title'))
        if tag in ('input', 'select', 'textarea') and a.get('type') not in ('hidden', 'submit', 'button', 'reset', 'image'):
            self.controls.append((f'<{tag} id={a.get("id")} name={a.get("name")}>', a.get('id'), inside_label or named))
        if tag not in self.VOID: self.stack.append([tag, a, ''])

    def handle_endtag(self, tag):
        while self.stack:
            t, a, text = self.stack.pop()
            if self.stack: self.stack[-1][2] += text
            if t == tag:
                named = text.strip() or a.get('aria-label') or a.get('aria-labelledby') or a.get('title')
                if t == 'title': self.title = bool(text.strip())
                if t in ('a', 'button') and not named and a.get('aria-hidden') != 'true' and 'hidden' not in a:
                    self.problems.append(f'<{t}> without an accessible name: {a.get("href") or a.get("id") or a.get("class")}')
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID: self.handle_endtag(tag)

    def handle_data(self, data):
        if self.stack: self.stack[-1][2] += data

def published_pages():
    for page in sorted(ROOT.rglob('*.html')):
        if SKIP_PARTS & set(page.relative_to(ROOT).parts): continue
        yield page

def audit(page):
    text = page.read_text(errors='ignore')
    if not re.search(r'<html\b', text, re.I): return []   # HTML snippets, not pages
    # An image's alt text names the link or button around it.
    text = re.sub(r'<img\b[^>]*\balt="([^"]+)"[^>]*>', lambda m: m.group(0) + m.group(1), text)
    doc = Audit(text)
    problems = list(doc.problems)
    if doc.redirect: return problems
    if not doc.lang: problems.append('<html> without lang')
    if not doc.title: problems.append('missing or empty <title>')
    duplicates = sorted({i for i in doc.ids if doc.ids.count(i) > 1})
    if duplicates: problems.append(f'duplicate ids: {duplicates[:5]}')
    if doc.stylesheet and doc.h1 != 1: problems.append(f'{doc.h1} <h1> elements (expected 1)')
    if doc.stylesheet and not doc.skip_link: problems.append('no skip link to #main')
    return problems

class Accessibility(unittest.TestCase):
    def test_every_published_page_passes_static_checks(self):
        failures = {str(p.relative_to(ROOT)): problems for p in published_pages() if (problems := audit(p))}
        report = '\n'.join(f'{page}: ' + '; '.join(problems[:4]) for page, problems in sorted(failures.items()))
        self.assertFalse(failures, f'{len(failures)} pages with accessibility problems:\n{report}')

if __name__ == '__main__':
    for page in published_pages():
        for problem in audit(page): print(f'{page.relative_to(ROOT)}: {problem}')
