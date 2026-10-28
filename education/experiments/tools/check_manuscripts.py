#!/usr/bin/env python3
"""Check chapter manuscripts: heading structure and consistent MathJax math.

Usage: check_manuscripts.py [stem ...]   (default: every chapter)

Every section h2 must read "N.k Title" and its h3 headings "N.k.j Subtitle",
exactly as listed in chapters.json. Mathematical symbols (Greek letters, kets,
roots, superscripts, comparison signs, degree marks) must appear only inside
MathJax delimiters \\( \\) or \\[ \\], never as bare Unicode in prose.
"""
from pathlib import Path
import json
import re
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = json.loads((ROOT / 'chapters.json').read_text())
MATH = re.compile(r'\\\((.*?)\\\)|\\\[(.*?)\\\]', re.S)
FORBIDDEN = re.compile('[⟨⟩√²³¹⁰⁴⁵⁶⁷⁸⁹⁻⁺⁽⁾ᵃᵇθφϕψΨγΓΔδσλκΩωηΦτρπμ±≤≥≈≃×−∝∑∫ℏ°₀₁₂₃ᵢⱼ→←↦⊗†]')


def check(c):
    problems = []
    soup = BeautifulSoup((ROOT / 'content' / f'{c["stem"]}.html').read_text(), 'html.parser')
    for sec in c['sections']:
        el = soup.find('section', id=sec['id'])
        if not el:
            problems.append(f'missing section {sec["id"]}')
            continue
        h2 = el.find('h2').get_text(strip=True)
        if h2 != f'{sec["number"]} {sec["title"]}':
            problems.append(f'{sec["id"]}: h2 "{h2}"')
        expected = [f'{sec["number"]}.{j} {t}' for j, t in enumerate(sec['subsections'], 1)]
        found = [h.get_text(strip=True) for h in el.find_all('h3')]
        if found != expected:
            problems.append(f'{sec["id"]}: h3 {found} != {expected}')
    for sid in ('explore', 'worked', 'practice', 'takeaways', 'sources'):
        if not soup.find('section', id=sid):
            problems.append(f'missing section #{sid}')
    if not soup.select_one(f'#explore div[data-lab="{c["kind"]}"]'):
        problems.append('missing lab placeholder')
    for el in soup.select('section'):
        if el.get('id') == 'sources':
            continue
        for node in el.find_all(string=True):
            if node.parent.name in ('a', 'script', 'style'):
                continue
            prose = MATH.sub(' ', str(node))
            for m in FORBIDDEN.finditer(prose):
                start = max(0, m.start() - 30)
                problems.append(f'bare math symbol {m.group()!r} in: …{prose[start:m.end() + 30].strip()}…')
    whole = soup.get_text()
    if whole.count('\\(') != whole.count('\\)') or whole.count('\\[') != whole.count('\\]'):
        problems.append('unbalanced MathJax delimiters')
    return problems


def main(stems):
    failed = False
    for c in CHAPTERS:
        if stems and c['stem'] not in stems:
            continue
        problems = check(c)
        if problems:
            failed = True
            print(f'{c["stem"]}:')
            for p in problems[:25]:
                print('  ' + p)
    if failed:
        sys.exit(1)
    print('PASS: manuscript headings and MathJax notation.')


if __name__ == '__main__':
    main(sys.argv[1:])

