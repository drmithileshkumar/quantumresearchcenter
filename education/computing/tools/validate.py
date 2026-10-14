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
 if not s.select_one('main h1'):errors.append(f'{name}: no page heading')
 if s.select_one('script[src$="/slides.js"]'):errors.append(f'{name}: presentation navigation loaded')
print(f'Checked {len(pages)} pages and their local links/assets.')
if errors:
 print('\n'.join(errors));raise SystemExit(1)
print('All static checks passed.')
