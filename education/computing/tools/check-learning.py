#!/usr/bin/env python3
"""Check learning-content coverage and the extracted offline edition's links."""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, unquote
import json, tempfile, zipfile, re
ROOT=Path(__file__).resolve().parents[1]
meta=json.loads((ROOT/'chapters.json').read_text())
for stem,*_ in meta:
 soup=BeautifulSoup((ROOT/(stem+'.html')).read_text(),'html.parser')
 assert soup.select_one('.learning-guide'),stem
 if stem!='appendices':
  assert len(soup.select('.exercise'))==3,stem
  assert len(soup.select('.exercise-hint'))==6,stem
  assert len(soup.select('.exercise-solution'))==3,stem
  assert soup.select_one('.glossary-term'),stem
 for lab in soup.select('[data-lab]'):
  assert lab.find_previous_sibling().get('class')==['prediction'],stem
  assert lab.find_next_sibling().get('class')==['prediction-answer'],stem
with tempfile.TemporaryDirectory() as tmp:
 base=Path(tmp)
 with zipfile.ZipFile(ROOT/'downloads/quantum-computing.zip') as z:z.extractall(base)
 assert not list(base.rglob('*.zip')),'Archive includes itself'
 for page in base.rglob('*.html'):
  soup=BeautifulSoup(page.read_text(),'html.parser')
  for el in soup.select('[href],[src]'):
   raw=el.get('href',el.get('src'));url=urlsplit(raw)
   if url.scheme or url.netloc:continue
   target=(page.parent/unquote(url.path)).resolve() if url.path else page
   assert target.is_file(),f'{page}: missing {raw}'
   if url.fragment and target.suffix=='.html':
    dest=soup if target==page else BeautifulSoup(target.read_text(),'html.parser')
    assert dest.find(id=unquote(url.fragment)),f'{page}: missing anchor {raw}'
 for css in base.rglob('*.css'):
  for raw in re.findall(r'url\([\'"]?([^\)\'\"]+)',css.read_text()):
   u=urlsplit(raw)
   if not u.scheme and not u.netloc and u.path:assert (css.parent/unquote(u.path)).is_file(),f'{css}: {raw}'
print('All chapters have guides, exercises, and definition links. Offline links and CSS assets resolve.')
