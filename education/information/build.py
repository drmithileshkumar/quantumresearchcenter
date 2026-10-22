#!/usr/bin/env python3
"""Build the Quantum Information course using the shared computing-course theme."""
from pathlib import Path
from html import escape as esc
import json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
import sys
sys.path.insert(0,str(ROOT.parent))
from course_map import render_course_map, render_chapter_map
from asset_versions import version_pages
from site_logo import COURSE_LOGO
import chapter_exercises
import chapter_summary
CHAPTERS=json.loads((ROOT/'chapters.json').read_text())
LEARNING=json.loads((ROOT/'content/learning.json').read_text())
EXERCISES=chapter_exercises.load(ROOT)
SUMMARIES=chapter_summary.load(ROOT,{c['stem'] for c in CHAPTERS})
def navigation(current,data):
 out=COURSE_LOGO+'<a class="book-home" href="index.html">Quantum Information<span>States, resources, and communication</span></a><a class="nav-introduction" href="index.html">About this course</a><a href="index.html#topic-map-heading">Course map</a>'
 for i,c in enumerate(CHAPTERS,1):
  stem=c['stem'];active=' open' if stem==current else ''
  out+=f'<details class="nav-chapter"{active}><summary><span>{i:02}</span> {esc(c["title"])}</summary><a class="chapter-start" href="{stem}.html"'+(' aria-current="page"' if stem==current else '')+'>Chapter overview</a>'
  for sec in c['sections']:
   out+=f'<a href="{stem}.html#{sec["id"]}" data-topic="{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a>'
   for j,title in enumerate(sec['subsections'],1):
    topic=sec['id'].replace('section-','topic-')+f'-{j}'
    out+=f'<a class="nav-topic" href="{stem}.html#{topic}" data-topic="{topic}"><span>{sec["number"]}.{j}</span> {esc(title)}</a>'
  out+='</details>'
 return out+'<nav class="book-resources" aria-label="Related courses"><a href="../computing/index.html">Quantum Computing</a><a href="../algorithms/index.html">Quantum Algorithms</a></nav>'
def shell(stem,title,body,data,styles=(),scripts=(),classes=()):
 css=''.join(f'<link rel="stylesheet" href="{s}">' for s in dict.fromkeys(['../computing/assets/source/slides.css','../computing/assets/source/classical.css','../computing/assets/source/math.css',*styles,*(['../computing/assets/topic-map.css'] if stem=='index' or stem in {c['stem'] for c in CHAPTERS} else []),'../computing/assets/book.css','../../styles.css','../computing/assets/learning.css','../course.css','assets/information.css']))
 js=''.join(f'<script defer src="{s}"></script>' for s in ['../computing/assets/source/mathjax-config.js','../computing/assets/source/vendor/mathjax/tex-svg.js',*scripts,'assets/search-index.js','assets/book.js','assets/experiments.js'])
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="An interactive introduction to quantum information by Mithilesh Kumar."><title>{esc(title)} · Quantum Information</title><link rel="icon" href="../../icons/icon.svg"><link rel="canonical" href="https://quantumresearch.center/education/information/{"" if stem=="index" else stem+".html"}"><script src="../computing/assets/theme.js"></script><script src="../../navigation.js"></script>{css}{js}</head>
<body class="ebook {' '.join(classes)}" data-chapter="{stem}"><a class="skip-link" href="#main">Skip to content</a>
<header class="book-toolbar"><button id="menu-toggle" aria-controls="book-navigation" aria-expanded="false" aria-label="Toggle table of contents">☰ <span>Contents</span></button><a href="../index.html" class="toolbar-title">Education / Quantum Information</a><nav class="site-nav" aria-label="Site navigation"><a href="../../index.html">Home</a><a href="../index.html">Education</a><a href="../../research/index.html">Research</a></nav><div class="reading-tools"><button id="print-chapter" hidden data-print>Print chapter</button><button id="search-open" aria-label="Search the book">Search <kbd>/</kbd></button><button id="text-smaller" aria-label="Decrease reading text size">A−</button><button id="text-larger" aria-label="Increase reading text size">A+</button></div></header>
<aside id="book-navigation" aria-label="Book navigation">{navigation(stem,data)}<p class="nav-credit">Mithilesh Kumar</p></aside><button id="nav-scrim" aria-label="Close contents" hidden></button>
<main id="main" tabindex="-1">{body}<footer class="book-footer">Mithilesh Kumar · Quantum Information <a href="#chapter-top">Back to top ↑</a></footer></main>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Search this book</h2><button id="search-close" aria-label="Close search">Close ×</button></div><label for="book-search">Find a concept, equation, or section</label><input id="book-search" type="search" autocomplete="off" placeholder="Try entanglement, entropy, or teleportation"><p id="search-status" role="status">Search the course.</p><ol id="search-results"></ol></dialog>
</body></html>'''

COURSE_TITLE = 'Quantum Information'
COURSE_SUBTITLE = 'From distinguishable messages to quantum communication'
COURSE_ABOUT = 'What can we learn, preserve, transform, and communicate when information is carried by quantum systems? Develop states, measurements, entanglement, entropy, and communication through concrete tasks, returning to nonorthogonal states, a Bell pair, and a noisy channel.'
COURSE_PREREQUISITES = 'No prior quantum mechanics, information theory, or linear algebra course is assumed. Probability and mathematics are introduced in context. <a href="../computing/index.html">Quantum Computing</a> is a complementary course, not a prerequisite.'
COURSE_EXTRA = '<p>Read in order on your first pass. Pause at each prediction, reproduce the worked calculations, and try the Problems before opening their solutions. Interactive figures compare phase, noise, and measurement choices; every figure also has a static explanation.</p><p>The recurring examples are two nonorthogonal states, a Bell pair, and a noisy qubit. Their purpose changes as the course develops: first predict an observation, then distinguish, preserve, transmit, or protect a state.</p>'

def main():
 search=[]
 drafts=sum(c.get('status')=='draft' for c in CHAPTERS)
 for i,c in enumerate(CHAPTERS,1):
  stem=c['stem'];manuscript=(ROOT/'content'/f'{stem}.html').read_text()
  soup=BeautifulSoup(manuscript,'html.parser')
  guide=LEARNING[stem]
  body=f'<header class="chapter-header" id="chapter-top"><p class="book-kicker">{COURSE_TITLE} · Chapter {i}</p><h1>{esc(c["title"])}</h1>{render_chapter_map(c["title"],c)}<p class="chapter-subtitle">{esc(c["question"])}</p></header><details class="chapter-contents"><summary>In this chapter</summary><ol>'
  for sec in c['sections']:
   body+=f'<li class="contents-part"><a href="#{sec["id"]}">{sec["number"]} {esc(sec["title"])}</a><ol>'
   for j,title in enumerate(sec['subsections'],1):
    topic=sec['id'].replace('section-','topic-')+f'-{j}'
    body+=f'<li><a href="#{topic}"><span>{sec["number"]}.{j}</span> {esc(title)}</a></li>'
   body+='</ol></li>'
  body+='</ol></details>'
  body+=f'<details class="chapter-direction"><summary>Before you begin</summary><p><strong>Starting point:</strong> {esc(c["prerequisites"])}</p><p><strong>Keep in view:</strong> {esc(c["example"])}</p></details><aside class="prediction"><p><strong>Predict first.</strong> {guide["prediction"]}</p><details class="prediction-answer"><summary>Compare your reasoning</summary><p>{guide["explanation"]}</p></details></aside>'+manuscript
  body+=chapter_summary.render(SUMMARIES.get(stem))+chapter_exercises.render(stem,c['title'],EXERCISES.get(stem,[]),{el['id'] for el in soup.select('[id]')},search)
  prev=CHAPTERS[i-2] if i>1 else None;nxt=CHAPTERS[i] if i<len(CHAPTERS) else None
  links=(f'<a rel="prev" href="{prev["stem"]}.html"><small>Previous chapter</small>{esc(prev["title"])} ←</a>' if prev else '<a href="index.html"><small>Course overview</small>← Introduction</a>')+(f'<a rel="next" href="{nxt["stem"]}.html"><small>Next chapter</small>{esc(nxt["title"])} →</a>' if nxt else '<a href="index.html"><small>Return to</small>Course contents →</a>')
  body='<nav class="chapter-pagination chapter-pagination-top" aria-label="Chapter navigation, top of page">'+links+'</nav>'+body+'<nav class="chapter-pagination" aria-label="Chapter navigation">'+links+'</nav>'
  (ROOT/f'{stem}.html').write_text(shell(stem,c['title'],body,[],styles=c.get('styles',()),classes=['revised-book']))
  ids=[el['id'] for el in soup.select('[id]')]
  if len(ids)!=len(set(ids)):raise ValueError('Duplicate manuscript IDs: '+stem)
  for element in soup.select('.book-part, .reading-topic'):
   excerpt=BeautifulSoup(str(element),'html.parser')
   for solution in excerpt.select('.problem-solution'):solution.decompose()
   heading=element.find(['h2','h3'])
   search.append(dict(title=heading.get_text(' ',strip=True).replace('§','').strip(),chapter=c['title'],url=stem+'.html#'+element['id'],text=excerpt.get_text(' ',strip=True)))
  for sec in c['sections']:
   if soup.find(id=sec['id']) is None:raise ValueError('Missing planned section: '+sec['id'])
   for j in range(1,len(sec['subsections'])+1):
    topic=sec['id'].replace('section-','topic-')+f'-{j}'
    if soup.find(id=topic) is None:raise ValueError('Missing subsection anchor: '+topic)
 body=f'''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">Course manuscript · Mithilesh Kumar</p><h1>{COURSE_TITLE}</h1><p class="chapter-subtitle">{COURSE_SUBTITLE}</p><p class="chapter-intro">{COURSE_ABOUT}</p><a class="start-reading" href="{CHAPTERS[0]["stem"]}.html">Begin reading <span aria-hidden="true">→</span></a><a id="resume-reading" hidden>Continue where you left off →</a></header>
<section class="book-about"><h2>Prerequisites and approach</h2><p>{COURSE_PREREQUISITES}</p><p>{drafts} of {len(CHAPTERS)} chapters contain draft lessons with worked examples and solved problems. These are teaching manuscripts in development; advanced results are stated with their assumptions and sources where a full proof lies beyond the course.</p>{COURSE_EXTRA}</section>
{render_course_map(COURSE_TITLE,CHAPTERS)}'''
 (ROOT/'index.html').write_text(shell('index',COURSE_TITLE,body,[],classes=['revised-book']))
 (ROOT/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(search,ensure_ascii=False)+';\n')
 version_pages(ROOT)
 print(f'Built {COURSE_TITLE}: {drafts} draft lessons, {len(CHAPTERS)-drafts} outlines.')
if __name__=='__main__':main()
