#!/usr/bin/env python3
"""Build the independent book manuscripts listed in chapters.json."""
from pathlib import Path
from bs4 import BeautifulSoup
import argparse, html, json, re
import learning
import illustrations
ROOT=Path(__file__).resolve().parent
import sys
sys.path.insert(0,str(ROOT.parent))
from course_map import render_course_map, render_chapter_map
from asset_versions import version_pages
META=json.loads((ROOT/'chapters.json').read_text())
def esc(s):return html.escape(str(s),quote=True)
def chapter_redirect(previous,target):
 """Preserve topic bookmarks when a numbered chapter moves."""
 renumber={'07-amplitude-amplification':(7,9),'08-circuits-universality':(8,8),'05-composite-systems':(5,6),'06-queries-phase-kickback':(6,7),'07-circuits-universality':(7,8),'08-amplitude-amplification':(8,9),'09-complexity-advantage':(9,10)}
 script=''
 if previous in renumber:
  old,new=renumber[previous]
  script=f'<script>location.replace({json.dumps(target+".html")}+location.hash.replace(/^#(topic|section)-{old}-/,"#$1-{new}-"));</script>'
 return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chapter moved</title><link rel="canonical" href="https://quantumresearch.center/education/computing/{target}.html">{script}<meta http-equiv="refresh" content="0;url={target}.html"></head><body><main><h1>Chapter moved</h1><p>The book has been reorganized. <a href="{target}.html">Continue to the revised book</a>.</p></main></body></html>'
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
 pieces.append('<nav class="book-resources" aria-label="Learning resources"><a href="study-guide.html">Study guide</a><a href="glossary.html">Glossary</a><a href="notation.html">Notation</a><a href="revisions.html">Revisions and corrections</a><a href="downloads/quantum-computing.zip" download>Download offline book</a></nav>')
 return ''.join(pieces)
def inline_figures(soup):
 """Inline SVG figures so MathJax can typeset their data-tex labels.

 Ids get a per-page prefix (a page may show one figure twice) and each figure's
 style rules are scoped to that figure, since inline styles apply page-wide.
 """
 for n,img in enumerate(soup.select('img[src^="assets/figures/"][src$=".svg"]'),1):
  svg=(ROOT/img['src']).read_text();prefix=f'figure{n}-'
  for ident in re.findall(r'\bid="([^"]+)"',svg):
   svg=svg.replace(f'id="{ident}"',f'id="{prefix}{ident}"').replace(f'url(#{ident})',f'url(#{prefix}{ident})')
  svg=re.sub(r'aria-labelledby="([^"]*)"',lambda m:'aria-labelledby="'+' '.join(prefix+x for x in m.group(1).split())+'"',svg,count=1)
  scope=lambda css:re.sub(r'([^{}]+)\{',lambda m:','.join(f'#{prefix}svg {x.strip()}' for x in m.group(1).split(','))+'{',css)
  svg=re.sub(r'<style>(.*?)</style>',lambda m:'<style>'+scope(m.group(1))+'</style>',svg,flags=re.S)
  svg=svg.replace('<svg ',f'<svg id="{prefix}svg" class="book-figure" ',1)
  img.replace_with(BeautifulSoup(svg,'html.parser'))
def shell(stem,title,body,data,styles=(),scripts=(),classes=()):
 css=''.join(f'<link rel="stylesheet" href="{s}">' for s in dict.fromkeys(['assets/source/slides.css','assets/source/classical.css','assets/source/math.css',*styles,*(['assets/topic-map.css'] if stem=='index' or stem in {m[0] for m in META} else []),'assets/book.css','../../styles.css','assets/learning.css']))
 js=''.join(f'<script defer src="{s}"></script>' for s in ['assets/source/mathjax-config.js','assets/source/vendor/mathjax/tex-svg.js',*scripts,'assets/experiments.js','assets/search-index.js','assets/book.js','assets/learning.js'])
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="An interactive introduction to quantum computing by Mithilesh Kumar, from classical foundations to quantum algorithms."><title>{esc(title)} · Quantum Computing</title><link rel="icon" href="../../icons/icon.svg"><link rel="canonical" href="https://quantumresearch.center/education/computing/{"" if stem=="index" else stem+".html"}"><script src="assets/theme.js"></script>{css}{js}</head>
<body class="ebook {' '.join(classes)}" data-chapter="{stem}"><a class="skip-link" href="#main">Skip to content</a>
<header class="book-toolbar"><button id="menu-toggle" aria-controls="book-navigation" aria-expanded="false" aria-label="Toggle table of contents">☰ <span>Contents</span></button><a href="../index.html" class="toolbar-title">Education / Quantum Computing</a><div class="reading-tools"><button id="print-chapter" hidden>Print chapter</button><button id="search-open" aria-label="Search the book">Search <kbd>/</kbd></button><button id="text-smaller" aria-label="Decrease reading text size">A−</button><button id="text-larger" aria-label="Increase reading text size">A+</button></div></header>
<aside id="book-navigation" aria-label="Book navigation">{navigation(stem,data)}<p class="nav-credit">Mithilesh Kumar</p></aside><button id="nav-scrim" aria-label="Close contents" hidden></button>
<main id="main" tabindex="-1">{body}<footer class="book-footer">Mithilesh Kumar · Quantum Computing <a href="#chapter-top">Back to top ↑</a></footer></main>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Search this book</h2><button id="search-close" aria-label="Close search">Close ×</button></div><label for="book-search">Find a concept, equation, or section</label><input id="book-search" type="search" autocomplete="off" placeholder="Try interference, NAND, or measurement"><p id="search-status" role="status">Search all chapters and appendices.</p><ol id="search-results"></ol></dialog>
</body></html>'''
def course_map(data):
 chapters=[dict(manifest,stem=meta[0],title=meta[1]) for meta,manifest in zip(META,data)]
 return render_course_map('Quantum Computing',chapters)


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.parse_args()
 illustrations.build()
 data=[json.loads((ROOT/'content'/f'{m[0]}.json').read_text()) for m in META]
 index=[]
 for i,(meta,manifest) in enumerate(zip(META,data)):
  stem,title,subtitle,intro,prompt=meta
  content=(ROOT/'content'/f'{stem}.html').read_text()
  soup=BeautifulSoup(content,'html.parser')
  learning.enrich(soup)
  inline_figures(soup)
  for sec in manifest['sections']:
   section=soup.find(id=sec['id'])
   searchable=BeautifulSoup(str(section),'html.parser') if section else None
   if searchable:
    for hidden in searchable.select('.problem-solution,svg.book-figure'):hidden.decompose()
   txt=searchable.get_text(' ',strip=True) if searchable else ''
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
  continuation=manifest.get('opening_continuation') or []
  for paragraph in ([continuation] if isinstance(continuation,str) else continuation): opening+=f'<p>{esc(paragraph)}</p>'
  intro_continuation=f'<p>{esc(manifest["intro_continuation"])}</p>' if manifest.get('intro_continuation') else ''
  body=f'<header class="chapter-header" id="chapter-top"><p class="book-kicker">{"Appendices" if stem=="appendices" else f"Chapter {i+1:02}"}</p><h1>{title}</h1>{render_chapter_map(title,manifest)}{opening}{f'<p class="chapter-subtitle">{subtitle}</p>' if subtitle else ""}<p class="chapter-intro">{intro}</p>{intro_continuation}{f'<p class="reading-prompt">{prompt}</p>' if prompt else ""}<details class="chapter-contents"><summary>In this chapter · {contents_label}</summary><ol>{toc}</ol></details></header>'+learning.guide(stem)+str(soup)+learning.exercises(stem,index,title)
  prev=META[i-1] if i else None; nxt=META[i+1] if i+1<len(META) else None
  links=(f'<a rel="prev" href="{prev[0]}.html"><small>Previous chapter</small>{prev[1]} ←</a>' if prev else '<a href="index.html"><small>Book overview</small>← Introduction</a>')+(f'<a rel="next" href="{nxt[0]}.html"><small>Next chapter</small>{nxt[1]} →</a>' if nxt else '<a href="index.html"><small>Return to</small>Book contents →</a>')
  body='<nav class="chapter-pagination chapter-pagination-top" aria-label="Chapter navigation, top of page">'+links+'</nav>'+body+'<nav class="chapter-pagination" aria-label="Chapter navigation">'+links+'</nav>'
  (ROOT/f'{stem}.html').write_text(shell(stem,title,body,data,manifest['styles'],manifest['scripts'],manifest['classes']))
 intro='''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">An interactive introduction · Mithilesh Kumar</p><h1>Quantum Computing</h1><p class="chapter-subtitle">From classical to quantum</p><p class="chapter-intro">What changes when computation follows the rules of quantum mechanics? This book builds the answer from the ground up: from mechanical reasoning and classical machines to quantum states, circuits, and algorithms.</p><a class="start-reading" href="01-logic-computability.html">Begin reading <span aria-hidden="true">→</span></a><a id="resume-reading" hidden>Continue where you left off →</a></header>
<section class="book-about"><h2>Prerequisites and approach</h2><p>You do not need a previous course in quantum mechanics, computer science, or linear algebra. The mathematics is introduced as it is used, with examples you can work through by hand.</p><p>We begin with ordinary computation: how a machine follows rules, and what it means to reverse a calculation. From there, we study quantum states and the operations that change them. Small examples carry much of the explanation. Follow each calculation, try the problems, and use the interactive figures to check your predictions.</p></section>
'''+course_map(data)+'''<section class="book-about"><h2>How to use this book</h2><p>Read the chapters in order for a continuous path through the subject, or use the expandable contents to revisit a topic. Search works throughout the book. The text-size controls adjust the reading view, and each section has a permanent link.</p><p>Diagrams, equations, and interactive experiments are included with the book. Use Print chapter for a reading copy, or download the complete offline edition. The <a href="study-guide.html">study guide</a> explains the exercises, reader controls, and sources; the <a href="glossary.html">glossary</a> collects key definitions. Interactive figures print their current state.</p></section>'''
 (ROOT/'index.html').write_text(shell('index','Introduction',intro,data,styles=['assets/topic-map.css']))
 legacy={'00-landscape':'index','01-classical-computation':'01-logic-computability','02-quantum-mechanics':'04-states-measurement','03-quantum-computation':'07-queries-phase-kickback','04-quantum-circuits':'08-circuits-universality','05-amplitude-amplification':'09-amplitude-amplification','06-black-box-model':'07-queries-phase-kickback','07-amplitude-amplification':'09-amplitude-amplification','08-circuits-universality':'08-circuits-universality'}
 legacy.update({'05-composite-systems': '06-composite-systems', '06-queries-phase-kickback': '07-queries-phase-kickback', '07-circuits-universality': '08-circuits-universality', '08-amplitude-amplification': '09-amplitude-amplification', '09-complexity-advantage': '10-complexity-advantage'})
 for previous,target in legacy.items():
  if previous in {m[0] for m in META}:continue
  (ROOT/f'{previous}.html').write_text(chapter_redirect(previous,target))
 for stem,title,body in learning.resources(META,index):
  (ROOT/f'{stem}.html').write_text(shell(stem,title,body,data))
 (ROOT/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(index,ensure_ascii=False).replace('</','<\\/')+';\n')
 version_pages(ROOT)
 learning.package()
 print(f'Built {len(META)-1} chapters, appendices, {len(index)} topics, and the book introduction.')
if __name__=='__main__':main()
