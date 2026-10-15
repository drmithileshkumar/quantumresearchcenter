#!/usr/bin/env python3
"""Check the built book's local links, anchors, assets, and chapter structure."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
errors=[];pages={p.name:BeautifulSoup(p.read_text(),'html.parser') for p in ROOT.glob('*.html')}
for name,s in pages.items():
 counts=Counter(x['id'] for x in s.select('[id]'))
 errors.extend(f'{name}: duplicate id {key}' for key,count in counts.items() if count>1)
 for el in s.select('[href],[src]'):
  value=el.get('href') or el.get('src');u=urlsplit(value)
  if u.scheme or u.netloc:continue
  target=ROOT/unquote(u.path) if u.path else ROOT/name
  if not target.exists():errors.append(f'{name}: missing {value}');continue
  if u.fragment and target.suffix=='.html':
   doc=pages.get(target.name)
   if doc and not doc.find(id=unquote(u.fragment)):errors.append(f'{name}: missing anchor {value}')
 for section in s.select('.reading-topic'):
  if not section.select('figure,svg,img'):errors.append(f'{name}: missing illustration for {section["id"]}')
  questions=section.select('.probing-question')
  if len(questions)!=1 or len(questions[0].select(':scope > ol > li'))!=3:
   errors.append(f'{name}: expected three questions for {section["id"]}')
  for group in questions:
   if group.name!='details' or group.has_attr('open') or not group.select_one(':scope > summary.question-label'):
    errors.append(f'{name}: problems must be a closed disclosure in {section["id"]}')
  for problem in section.select('.probing-question > ol > li'):
   answers=problem.select('details.problem-solution')
   if len(answers)!=1 or answers[0].has_attr('open') or not answers[0].select_one('p'):
    errors.append(f'{name}: missing or initially exposed solution in {problem.get("id")}')
  for img in section.select('img'):
   if not img.get('alt','').strip():errors.append(f'{name}: missing figure description for {section["id"]}')
 if not s.select_one('main h1'):errors.append(f'{name}: no page heading')
 if s.select_one('script[src$="/slides.js"]'):errors.append(f'{name}: presentation navigation loaded')
print(f'Checked {len(pages)} pages and their local links/assets.')
if errors:
 print('\n'.join(errors));raise SystemExit(1)
print('All static checks passed.')
