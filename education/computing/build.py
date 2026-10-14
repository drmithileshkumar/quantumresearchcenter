#!/usr/bin/env python3
"""Build the independent book manuscripts listed in chapters.json."""
from pathlib import Path
from bs4 import BeautifulSoup
import argparse, html, json, re
ROOT=Path(__file__).resolve().parent
META=json.loads((ROOT/'chapters.json').read_text())
def esc(s):return html.escape(str(s),quote=True)
def navigation(current,data):
 pieces=['<nav class="site-nav" aria-label="Site navigation"><a href="../../index.html">Home</a><a href="../index.html">Education</a><a href="../../research/index.html">Research</a></nav><a class="book-home" href="index.html">Quantum Computing<span>From classical to quantum</span></a><a class="nav-introduction" href="index.html">About this book</a>']
 for i,(meta,m) in enumerate(zip(META,data)):
  stem,title,*_=meta
  pieces.append(f'<details class="nav-chapter" {"open" if current==stem else ""}><summary><span>{str(i+1).zfill(2) if stem!="appendices" else "A–E"}</span> {esc(title)}</summary><a class="chapter-start" href="{stem}.html">Chapter overview</a>')
  group=None
  for sec in m['sections']:
   if sec['group'] and sec['group']!=group:
    group=sec['group'];label=re.sub(r'^\d+\s*[·.]\s*','',group)
    part=next((p for p in m.get('parts',[]) if p['id']==sec.get('part_id')),None)
    pieces.append(f'<a class="nav-group" href="{stem}.html#{part["id"]}">{esc(part["number"])} · {esc(part["title"])}</a>' if part else f'<p class="nav-group">{esc(label)}</p>')
   pieces.append(f'<a href="{stem}.html#{sec["id"]}" data-topic="{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a>')
  pieces.append('</details>')
 return ''.join(pieces)
def shell(stem,title,body,data,styles=(),scripts=(),classes=()):
 css=''.join(f'<link rel="stylesheet" href="{s}">' for s in dict.fromkeys(['assets/source/slides.css','assets/source/classical.css','assets/source/math.css',*styles,'assets/book.css','../../styles.css']))
 js=''.join(f'<script defer src="{s}"></script>' for s in ['assets/source/mathjax-config.js','assets/source/vendor/mathjax/tex-svg.js',*scripts,'assets/experiments.js','assets/search-index.js','assets/book.js'])
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="An interactive introduction to quantum computing by Mithilesh Kumar, from classical foundations to quantum algorithms."><title>{esc(title)} · Quantum Computing</title><link rel="icon" href="../../icons/icon.svg"><link rel="canonical" href="https://quantumresearch.center/education/computing/{"" if stem=="index" else stem+".html"}">{css}{js}</head>
<body class="ebook {' '.join(classes)}" data-chapter="{stem}"><a class="skip-link" href="#main">Skip to content</a>
<header class="book-toolbar"><button id="menu-toggle" aria-controls="book-navigation" aria-expanded="false" aria-label="Toggle table of contents">☰ <span>Contents</span></button><a href="../index.html" class="toolbar-title">Education / Quantum Computing</a><div class="reading-tools"><button id="search-open" aria-label="Search the book">Search <kbd>/</kbd></button><button id="text-smaller" aria-label="Decrease reading text size">A−</button><button id="text-larger" aria-label="Increase reading text size">A+</button></div></header>
<aside id="book-navigation" aria-label="Book navigation">{navigation(stem,data)}<p class="nav-credit">Mithilesh Kumar</p></aside><button id="nav-scrim" aria-label="Close contents" hidden></button>
<main id="main" tabindex="-1">{body}<footer class="book-footer">Mithilesh Kumar · Quantum Computing <a href="#chapter-top">Back to top ↑</a></footer></main>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Search this book</h2><button id="search-close" aria-label="Close search">Close ×</button></div><label for="book-search">Find a concept, equation, or section</label><input id="book-search" type="search" autocomplete="off" placeholder="Try interference, NAND, or measurement"><p id="search-status" role="status">Search all chapters and appendices.</p><ol id="search-results"></ol></dialog>
</body></html>'''
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.parse_args()
 data=[json.loads((ROOT/'content'/f'{m[0]}.json').read_text()) for m in META]
 index=[]
 for i,(meta,manifest) in enumerate(zip(META,data)):
  stem,title,subtitle,intro,prompt=meta
  content=(ROOT/'content'/f'{stem}.html').read_text()
  soup=BeautifulSoup(content,'html.parser')
  for sec in manifest['sections']:
   section=soup.find(id=sec['id']);txt=section.get_text(' ',strip=True) if section else ''
   index.append({'title':sec['title'],'chapter':title,'url':f'{stem}.html#{sec["id"]}','text':txt})
  toc=''.join(f'<li><a href="#{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a></li>' for sec in manifest['sections'])
  contents_label=f'{len(manifest["sections"])} sections'
  if manifest.get('parts'):
   groups=[]
   for part in manifest['parts']:
    topics=''.join(f'<li><a href="#{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a></li>' for sec in manifest['sections'] if sec.get('part_id')==part['id'])
    groups.append(f'<li class="contents-part"><a href="#{part["id"]}"><span>{part["number"]}</span> {esc(part["title"])}</a><details><summary>Topics in this section</summary><ol>{topics}</ol></details></li>')
   toc=''.join(groups)
   contents_label=f'{len(manifest["parts"])} sections · {len(manifest["sections"])} topics'
  opening=f'<p class="chapter-intro">{esc(manifest["opening"])}</p>' if manifest.get('opening') else ''
  if manifest.get('opening_continuation'): opening+=f'<p>{esc(manifest["opening_continuation"])}</p>'
  intro_continuation=f'<p>{esc(manifest["intro_continuation"])}</p>' if manifest.get('intro_continuation') else ''
  body=f'<header class="chapter-header" id="chapter-top"><p class="book-kicker">{"Appendices" if stem=="appendices" else f"Chapter {i+1:02}"}</p><h1>{title}</h1>{opening}{f'<p class="chapter-subtitle">{subtitle}</p>' if subtitle else ""}<p class="chapter-intro">{intro}</p>{intro_continuation}{f'<p class="reading-prompt">{prompt}</p>' if prompt else ""}<details class="chapter-contents"><summary>In this chapter · {contents_label}</summary><ol>{toc}</ol></details></header>'+str(soup)
  prev=META[i-1] if i else None; nxt=META[i+1] if i+1<len(META) else None
  body+='<nav class="chapter-pagination" aria-label="Chapter navigation">'+(f'<a rel="prev" href="{prev[0]}.html"><small>Previous chapter</small>{prev[1]} ←</a>' if prev else '<a href="index.html"><small>Book overview</small>← Introduction</a>')+(f'<a rel="next" href="{nxt[0]}.html"><small>Next chapter</small>{nxt[1]} →</a>' if nxt else '<a href="index.html"><small>Return to</small>Book contents →</a>')+'</nav>'
  (ROOT/f'{stem}.html').write_text(shell(stem,title,body,data,manifest['styles'],manifest['scripts'],manifest['classes']))
 cards=''.join(f'<li><a href="{m[0]}.html"><span class="chapter-number">{str(i+1).zfill(2) if m[0]!="appendices" else "A–E"}</span><div><h3>{m[1]}</h3><p>{m[3]}</p></div><span aria-hidden="true">→</span></a></li>' for i,m in enumerate(META))
 intro='''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">An interactive introduction · Mithilesh Kumar</p><h1>Quantum Computing</h1><p class="chapter-subtitle">From classical to quantum</p><p class="chapter-intro">What changes when computation follows the rules of quantum mechanics? This book builds the answer from the ground up: from mechanical reasoning and classical machines to quantum states, circuits, and algorithms.</p><a class="start-reading" href="01-logic-computability.html">Begin reading <span aria-hidden="true">→</span></a><a id="resume-reading" hidden>Continue where you left off →</a></header>
<section class="book-about"><h2>Prerequisites and approach</h2><p>The exposition begins with motivation, develops a mathematical language, and connects it to examples. You do not need prior experience with models of computation. Basic linear algebra is the only subject prerequisite: vectors, matrices, bases, and linear transformations. Complex inner products, tensor products, discrete probability, and computational concepts are developed where they are needed.</p><p>Circuit drawings show how operations are assembled. Interactive figures let you prepare a Bell state, compare phase oracles, and watch how search redistributes amplitudes. Try predicting a result before moving a control, then explain what changed. Animations wait for you to start them.</p></section>
<section class="book-chapters"><h2>Contents</h2><ol>'''+cards+'''</ol></section><section class="book-about"><h2>How to use this book</h2><p>Read the chapters in order for a continuous path through the subject, or use the expandable contents to revisit a topic. Search works throughout the book. The text-size controls adjust the reading view, and each section has a permanent link.</p><p>Diagrams, equations, and interactive experiments are included with the book. Use your browser’s print command for a reading copy; interactive figures print their current state.</p></section>'''
 (ROOT/'index.html').write_text(shell('index','Introduction',intro,data))
 legacy={'00-landscape':'index','01-classical-computation':'01-logic-computability','02-quantum-mechanics':'04-states-measurement','03-quantum-computation':'06-queries-phase-kickback','04-quantum-circuits':'08-circuits-universality','05-amplitude-amplification':'07-amplitude-amplification','06-black-box-model':'06-queries-phase-kickback'}
 for previous,target in legacy.items():
  (ROOT/f'{previous}.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chapter moved</title><meta http-equiv="refresh" content="0;url={target}.html"></head><body><main><h1>Chapter moved</h1><p>The book has been reorganized. <a href="{target}.html">Continue to the revised book</a>.</p></main></body></html>')
 (ROOT/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(index,ensure_ascii=False).replace('</','<\\/')+';\n')
 print(f'Built {len(META)-1} chapters, appendices, {len(index)} topics, and the book introduction.')
if __name__=='__main__':main()
