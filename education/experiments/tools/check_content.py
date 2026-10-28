#!/usr/bin/env python3
"""Check the complete course, generated readers, navigation, and local references."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
chapters=json.loads((ROOT/'chapters.json').read_text());labs=json.loads((ROOT/'labs.json').read_text())
assert len(chapters)==24 and len(labs)==24
cache={}
def parse(p):
 p=p.resolve()
 if p not in cache:cache[p]=BeautifulSoup(p.read_text(),'html.parser')
 return cache[p]
words=0
for c in chapters:
 manuscript=parse(ROOT/'content'/f'{c["stem"]}.html')
 wc=len(manuscript.get_text(' ',strip=True).split());words+=wc
 assert wc>500,(c['stem'],wc)
 assert c['status']=='developed' and c['kind'] in labs
 assert len(manuscript.select('#practice .exercise'))==3
 assert len(manuscript.select('.exercise-hint'))==3 and len(manuscript.select('.exercise-solution'))==3
 assert manuscript.select('#sources a[href^="https://"]')
for p in ROOT.glob('*.html'):
 doc=parse(p);ids=[el['id'] for el in doc.select('[id]')]
 assert len(ids)==len(set(ids)),p
 assert doc.h1 and doc.main and doc.title
 nav=doc.select_one('nav[aria-label="Site navigation"]')
 assert [a.get_text() for a in nav.find_all('a')]==['Home','News','Education','Research']
 if p.name!='index.html':
  assert len(doc.select('.qe-lab'))==1 and doc.select_one('svg title') and doc.select_one('svg desc')
  assert doc.select_one('input[type=range]') and doc.select_one('noscript')
  assert doc.select_one('.qe-controls').has_attr('hidden')
 for el in doc.select('[href],[src]'):
  u=urlsplit(el.get('href') or el.get('src'))
  if u.scheme or u.netloc:continue
  target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve()
  assert target.exists(),(p,target)
  if u.fragment and target.suffix=='.html':assert parse(target).find(id=unquote(u.fragment)),(p,target,u.fragment)
 for el in doc.select('[aria-labelledby],[aria-controls]'):
  for ident in (el.get('aria-labelledby') or el.get('aria-controls')).split():assert ident in ids,(p,ident)
print(f'PASS: 24 chapters, {words:,} words, 72 solved problems; 25 pages, IDs, navigation, local links, accessible static diagrams.')
