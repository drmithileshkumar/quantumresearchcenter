#!/usr/bin/env python3
"""Build the Interpretations of Quantum Mechanics course using the shared computing-course theme."""
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
sys.path.insert(0,str(ROOT / "tools"))
from make_circuits import main as make_circuits
CHAPTERS=json.loads((ROOT/'chapters.json').read_text())
EXERCISES=chapter_exercises.load(ROOT)
SUMMARIES=chapter_summary.load(ROOT,{c['stem'] for c in CHAPTERS})
def navigation(current,data):
 out=COURSE_LOGO+'<a class="book-home" href="index.html">Interpretations of Quantum Mechanics<span>States, outcomes, and physical reality</span></a><a class="nav-introduction" href="index.html">About this course</a>'
 for i,c in enumerate(CHAPTERS,1):
  stem=c['stem'];active=' open' if stem==current else ''
  out+=f'<details class="nav-chapter"{active}><summary><span>{i:02}</span> {esc(c["title"])}</summary><a class="chapter-start" href="{stem}.html"'+(' aria-current="page"' if stem==current else '')+'>Chapter overview</a>'
  for sec in c['sections']:out+=f'<a href="{stem}.html#{sec["id"]}" data-topic="{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a>'
  out+='</details>'
 return out+'<nav class="book-resources" aria-label="Related courses"><a href="../information-theory/index.html">Quantum Information Theory</a><a href="../foundations/index.html">Quantum Foundations</a></nav>'
def shell(stem,title,body,data,styles=(),scripts=(),classes=()):
 css=''.join(f'<link rel="stylesheet" href="{s}">' for s in dict.fromkeys(['../computing/assets/source/slides.css','../computing/assets/source/classical.css','../computing/assets/source/math.css',*styles,*(['../computing/assets/topic-map.css'] if stem=='index' or stem in {c['stem'] for c in CHAPTERS} else []),'../computing/assets/book.css','../../styles.css','../computing/assets/learning.css','../course.css']))
 js=''.join(f'<script defer src="{s}"></script>' for s in ['../computing/assets/source/mathjax-config.js','../computing/assets/source/vendor/mathjax/tex-svg.js',*scripts,'assets/search-index.js','assets/book.js'])
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Advanced interpretations of quantum mechanics: measurement, decoherence, Bell, Everett, Bohmian mechanics, collapse, relational accounts, QBism, and quantum observers."><title>{esc(title)} · Interpretations of Quantum Mechanics</title><link rel="icon" href="../../icons/icon.svg"><link rel="canonical" href="https://quantumresearch.center/education/interpretations/{"" if stem=="index" else stem+".html"}"><script src="../computing/assets/theme.js"></script><script src="../../navigation.js"></script>{css}{js}</head>
<body class="ebook {' '.join(classes)}" data-chapter="{stem}"><a class="skip-link" href="#main">Skip to content</a>
<header class="book-toolbar"><button id="menu-toggle" aria-controls="book-navigation" aria-expanded="false" aria-label="Toggle table of contents">☰ <span>Contents</span></button><a href="../index.html" class="toolbar-title">Education / Interpretations of Quantum Mechanics</a><nav class="site-nav" aria-label="Site navigation"><a href="../../index.html">Home</a><a href="../index.html">Education</a><a href="../../research/index.html">Research</a></nav><div class="reading-tools"><button id="print-chapter" hidden>Print chapter</button><button id="search-open" aria-label="Search the book">Search <kbd>/</kbd></button><button id="text-smaller" aria-label="Decrease reading text size">A−</button><button id="text-larger" aria-label="Increase reading text size">A+</button></div></header>
<aside id="book-navigation" aria-label="Book navigation">{navigation(stem,data)}<p class="nav-credit">Mithilesh Kumar</p></aside><button id="nav-scrim" aria-label="Close contents" hidden></button>
<main id="main" tabindex="-1">{body}<footer class="book-footer">Mithilesh Kumar · Interpretations of Quantum Mechanics <a href="#chapter-top">Back to top ↑</a></footer></main>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Search this book</h2><button id="search-close" aria-label="Close search">Close ×</button></div><label for="book-search">Find a concept, equation, or section</label><input id="book-search" type="search" autocomplete="off" placeholder="Try decoherence, Everett, or contextuality"><p id="search-status" role="status">Search the course.</p><ol id="search-results"></ol></dialog>
</body></html>'''

COURSE_TITLE = 'Interpretations of Quantum Mechanics'
COURSE_SUBTITLE = 'What the quantum formalism says, what it leaves open, and how to compare physical accounts'
COURSE_ABOUT = 'A detector records one result. A unitary calculation produces a correlated state. How should we connect those two descriptions? This advanced course follows that question through concrete experiments, mathematical constraints, and competing accounts of states, events, and probability.'
COURSE_PREREQUISITES = 'Complete <a href="../foundations/index.html">Quantum Foundations</a>, or bring equivalent knowledge of state vectors, density operators, tensor products, projective measurement, and probability. <a href="../information-theory/index.html">Quantum Information Theory</a> is useful preparation for channels and distinguishability, but is not required throughout. Chapter 6 also uses elementary gradients and continuity equations.'
COURSE_EXTRA = '<p>Ten draft chapters develop a common measurement model before comparing operational accounts, consistent histories, Everett, Bohmian mechanics, objective collapse, relational quantum mechanics, and QBism. Bell and contextuality constraints, quantum-state ontology, and quantum observers supply tests of what each account can claim. This is a parallel advanced path after Quantum Foundations; Quantum Error Correction is not a prerequisite.</p><p>Each chapter has three worked checks, ten exercises with hints and reasoned solutions, a summary, and linked primary-source or research-review readings. Explanations are conversational, but claims are tied to equations and explicit assumptions. No interpretation is presented as an experimentally selected winner. Modified collapse dynamics is distinguished from empirically equivalent readings of the usual formalism.</p><p>Conventions: finite-dimensional examples use normalized kets and left-to-right tensor order; |±⟩=(|0⟩±|1⟩)/√2; X, Y, and Z are the usual Pauli matrices; logarithms are natural unless specified. Conditional states require nonzero conditioning probability. Ideal coherent-control thought experiments are distinguished from practical macroscopic experiments. Continuous-variable models state their restricted physical scope.</p><p>Read with an assumption ledger: identify the calculation, the physical postulates, the theorem assumptions, and the interpretive conclusion. The final chapter offers a comparative research practicum. A <a href="tools/check_examples.py">reproducible numerical companion</a> verifies the finite examples; it does not prove the general no-go theorems or select an interpretation.</p>'

def main():
 make_circuits()
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
  notice='This lesson includes explanations, worked examples, and problems with solutions. Advanced results whose proofs are outside the chapter are identified explicitly.' if status=='draft' else 'This chapter is an outline; its lesson remains to be developed.'
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
 body=f'''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">Course manuscript · Mithilesh Kumar</p><h1>{COURSE_TITLE}</h1><p class="chapter-subtitle">{COURSE_SUBTITLE}</p><p class="chapter-intro">{COURSE_ABOUT}</p><a class="start-reading" href="{CHAPTERS[0]["stem"]}.html">Begin reading <span aria-hidden="true">→</span></a><a id="resume-reading" hidden>Continue where you left off →</a></header>
<section class="book-about"><h2>Prerequisites and approach</h2><p>{COURSE_PREREQUISITES}</p><p>{drafts} of {len(CHAPTERS)} chapters contain draft lessons with worked examples and solved problems. These are teaching manuscripts in development; advanced results are stated with their assumptions and sources where a full proof lies beyond the course.</p>{COURSE_EXTRA}</section>
{render_course_map(COURSE_TITLE,CHAPTERS)}'''
 (ROOT/'index.html').write_text(shell('index',COURSE_TITLE,body,[],classes=['revised-book']))
 (ROOT/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(search,ensure_ascii=False)+';\n')
 version_pages(ROOT)
 print(f'Built {COURSE_TITLE}: {drafts} draft lessons, {len(CHAPTERS)-drafts} outlines.')
if __name__=='__main__':main()
