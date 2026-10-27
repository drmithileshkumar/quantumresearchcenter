#!/usr/bin/env python3
"""Build the Quantum Machine Learning course using the shared computing-course theme."""
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
from site_navigation import COURSE_NAV
import chapter_exercises
import chapter_summary

CHAPTERS=json.loads((ROOT/'chapters.json').read_text())
EXERCISES=chapter_exercises.load(ROOT)
SUMMARIES=chapter_summary.load(ROOT,{c['stem'] for c in CHAPTERS})

def navigation(current,data):
 out=COURSE_LOGO+'<a class="book-home" href="index.html">Quantum Machine Learning<span>Models, kernels, and honest advantage claims</span></a><a class="nav-introduction" href="index.html">About this course</a>'
 for i,c in enumerate(CHAPTERS,1):
  stem=c['stem'];active=' open' if stem==current else ''
  out+=f'<details class="nav-chapter"{active}><summary><span>{i:02}</span> {esc(c["title"])}</summary><a class="chapter-start" href="{stem}.html"'+(' aria-current="page"' if stem==current else '')+'>Chapter overview</a>'
  for sec in c['sections']:out+=f'<a href="{stem}.html#{sec["id"]}" data-topic="{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a>'
  out+='</details>'
 return out+'<nav class="book-resources" aria-label="Related courses"><a href="../information/index.html">Quantum Information</a><a href="../algorithms/index.html">Quantum Algorithms</a></nav>'

def shell(stem,title,body,data,styles=(),scripts=(),classes=()):
 css=''.join(f'<link rel="stylesheet" href="{s}">' for s in dict.fromkeys(['../computing/assets/source/slides.css','../computing/assets/source/classical.css','../computing/assets/source/math.css',*styles,*(['../computing/assets/topic-map.css'] if stem=='index' or stem in {c['stem'] for c in CHAPTERS} else []),'../computing/assets/book.css','../../styles.css','../computing/assets/learning.css','../course.css','assets/course.css']))
 js=''.join(f'<script defer src="{s}"></script>' for s in ['../computing/assets/source/mathjax-config.js','../computing/assets/source/vendor/mathjax/tex-svg.js',*scripts,'assets/search-index.js','assets/book.js','assets/explorer.js'])
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Quantum machine learning: data encoding, quantum kernels, variational models, trainability, generalisation, and honest claims about advantage."><title>{esc(title)} · Quantum Machine Learning</title><link rel="icon" href="../../icons/icon.svg"><link rel="canonical" href="https://quantumresearch.center/education/qml/{"" if stem=="index" else stem+".html"}"><script src="../computing/assets/theme.js"></script><script src="../../navigation.js"></script>{css}{js}</head>
<body class="ebook {' '.join(classes)}" data-chapter="{stem}"><a class="skip-link" href="#main">Skip to content</a>
<header class="book-toolbar"><button id="menu-toggle" aria-controls="book-navigation" aria-expanded="false" aria-label="Toggle table of contents">☰ <span>Contents</span></button><a href="../index.html" class="toolbar-title">Education / Quantum Machine Learning</a>{COURSE_NAV}<div class="reading-tools"><button id="print-chapter" hidden>Print chapter</button><button id="search-open" aria-label="Search the book">Search <kbd>/</kbd></button><button id="text-smaller" aria-label="Decrease reading text size">A−</button><button id="text-larger" aria-label="Increase reading text size">A+</button></div></header>
<aside id="book-navigation" aria-label="Book navigation">{navigation(stem,data)}<p class="nav-credit">Quantum Research Center</p></aside><button id="nav-scrim" aria-label="Close contents" hidden></button>
<main id="main" tabindex="-1">{body}<footer class="book-footer">Quantum Research Center · Quantum Machine Learning <a href="#chapter-top">Back to top ↑</a></footer></main>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Search this book</h2><button id="search-close" aria-label="Close search">Close ×</button></div><label for="book-search">Find a concept, equation, or section</label><input id="book-search" type="search" autocomplete="off" placeholder="Try kernel, plateau, or encoding"><p id="search-status" role="status">Search the course.</p><ol id="search-results"></ol></dialog>
</body></html>'''

COURSE_TITLE = 'Quantum Machine Learning'
COURSE_SUBTITLE = 'Models, kernels, and honest advantage claims'
COURSE_ABOUT = 'Quantum machine learning asks whether quantum devices can learn from data better than classical learners. Answering it requires three separate arguments: what the model can express, whether it can be trained, and whether it generalises. This course builds all three, and keeps classical baselines in view throughout.'
COURSE_PREREQUISITES = 'Complete <a href="../information/index.html">Quantum Information</a> or bring equivalent knowledge of qubits, measurement, density operators, and tensor products, plus undergraduate linear algebra and probability. Familiarity with supervised learning and gradient descent is assumed; kernel methods are developed from scratch in Chapter 3.'
COURSE_EXTRA = '<p>This nine-chapter course develops the modelling language of quantum machine learning, the cost of encoding classical data, kernel methods and their quantum versions, variational models and their gradients, trainability limits, generalisation evidence, the classical algorithms that compete with quantum models, and a closing audit project. Each chapter includes learning objectives, derivations, worked examples, figures, and ten exercises with hints and reasoned solutions.</p><p><strong>Suggested pace:</strong> eighteen study sessions, two per chapter. In the first session, reproduce the derivations and work the examples. In the second, solve the problems and run the laboratory.</p><p><strong>Reading discipline.</strong> Every claim in this course is labelled as one of three things: a calculation you can check, an assumption that could fail, or a theorem quoted with its hypotheses. Where the field disagrees or where a result is numerical rather than general, the text says so.</p>'

def main():
 search=[]
 drafts=sum(c.get('status')=='draft' for c in CHAPTERS)
 for i,c in enumerate(CHAPTERS,1):
  stem=c['stem'];manuscript=(ROOT/'content'/f'{stem}.html').read_text()
  soup=BeautifulSoup(manuscript,'html.parser')
  # Stable subsection destinations for the chapter mind map.
  for section in c['sections']:
   headings=soup.find(id=section['id']).find_all('h3')
   if len(headings)!=len(section['subsections']):raise ValueError('Subsection count differs: '+section['id'])
   for j,heading in enumerate(headings,1):
    heading['id']=section['id'].replace('section-','topic-')+f'-{j}'
  manuscript=str(soup)
  status=c.get('status','outline')
  label='Draft lesson' if status=='draft' else 'Outline'
  notice='This lesson includes explanations, worked examples, and problems with solutions. Results quoted from the literature are identified as theorems with their hypotheses.' if status=='draft' else 'This chapter is an outline; its lesson remains to be developed.'
  toc=''.join(f'<li><a href="#{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a></li>' for sec in c['sections'])
  body=f'<header class="chapter-header" id="chapter-top"><p class="book-kicker">Chapter {i:02} · {label}</p><h1>{esc(c["title"])}</h1>{render_chapter_map(c["title"],c)}<p class="chapter-subtitle">{esc(c["question"])}</p><details class="chapter-contents"><summary>In this chapter · {len(c["sections"])} sections</summary><ol>{toc}</ol></details></header><details class="learning-guide"><summary>Reading guide · preparation and approach</summary><p><strong>Starting point:</strong> {esc(c["prerequisites"])}</p><p><strong>Anchor example:</strong> {esc(c["example"])}</p><p><strong>Method:</strong> {esc(c["method"])}</p><p><strong>Watch for:</strong> {esc(c["pitfall"])}</p><p>{notice}</p></details>'+manuscript
  body+=chapter_summary.render(SUMMARIES.get(stem))+chapter_exercises.render(stem,c['title'],EXERCISES.get(stem,[]),{el['id'] for el in soup.select('[id]')},search)
  prev=CHAPTERS[i-2] if i>1 else None;nxt=CHAPTERS[i] if i<len(CHAPTERS) else None
  links=(f'<a rel="prev" href="{prev["stem"]}.html"><small>Previous chapter</small>{esc(prev["title"])} ←</a>' if prev else '<a href="index.html"><small>Course overview</small>← Introduction</a>')+(f'<a rel="next" href="{nxt["stem"]}.html"><small>Next chapter</small>{esc(nxt["title"])} →</a>' if nxt else '<a href="index.html"><small>Return to</small>Course contents →</a>')
  body='<nav class="chapter-pagination chapter-pagination-top" aria-label="Chapter navigation, top of page">'+links+'</nav>'+body+'<nav class="chapter-pagination" aria-label="Chapter navigation">'+links+'</nav>'
  (ROOT/f'{stem}.html').write_text(shell(stem,c['title'],body,[],classes=['revised-book']))
  ids=[el['id'] for el in soup.select('[id]')]
  if len(ids)!=len(set(ids)):raise ValueError('Duplicate manuscript IDs: '+stem)
  for sec in c['sections']:
   element=soup.find(id=sec['id'])
   if element is None:raise ValueError('Missing planned section: '+sec['id'])
   search.append(dict(title=sec['title'],chapter=c['title'],url=stem+'.html#'+sec['id'],text=element.get_text(' ',strip=True)))
 body=f'''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">Course manuscript · Quantum Research Center</p><h1>{COURSE_TITLE}</h1><p class="chapter-subtitle">{COURSE_SUBTITLE}</p><p class="chapter-intro">{COURSE_ABOUT}</p><a class="start-reading" href="{CHAPTERS[0]["stem"]}.html">Begin reading <span aria-hidden="true">→</span></a><a id="resume-reading" hidden>Continue where you left off →</a></header>
<section class="book-about"><h2>Prerequisites and approach</h2><p>{COURSE_PREREQUISITES}</p><p>{drafts} of {len(CHAPTERS)} chapters contain draft lessons with worked examples and solved problems. These are teaching manuscripts in development; results quoted from the literature are stated with their hypotheses and sources.</p>{COURSE_EXTRA}</section>
{render_course_map(COURSE_TITLE,CHAPTERS)}'''
 (ROOT/'index.html').write_text(shell('index',COURSE_TITLE,body,[],classes=['revised-book']))
 (ROOT/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(search,ensure_ascii=False)+';\n')
 version_pages(ROOT)
 print(f'Built {COURSE_TITLE}: {drafts} draft lessons, {len(CHAPTERS)-drafts} outlines.')

if __name__=='__main__':main()
