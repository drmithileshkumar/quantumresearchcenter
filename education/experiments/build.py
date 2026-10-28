#!/usr/bin/env python3
"""Render Quantum Experiments from canonical chapter fragments and lab specifications."""
from pathlib import Path
from html import escape as esc
import json,sys
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from site_navigation import COURSE_NAV
from site_logo import COURSE_LOGO
from asset_versions import version_pages
from diagrams import svg
CHAPTERS=json.loads((ROOT/'chapters.json').read_text())
LABS=json.loads((ROOT/'labs.json').read_text())

def nav(current):
 out=COURSE_LOGO+'<a class="book-home" href="index.html">Quantum Experiments<span>Apparatus, arguments, and evidence</span></a><a class="nav-introduction" href="index.html">About this course</a>'
 part=''
 for i,c in enumerate(CHAPTERS,1):
  if part!=c['part']:part=c['part'];out+=f'<p class="nav-group">{esc(part)}</p>'
  out+=f'<details class="nav-chapter"'+(' open' if c['stem']==current else '')+f'><summary><span>{i:02}</span> {esc(c["title"])}</summary><a href="{c["stem"]}.html"'+(' aria-current="page"' if current==c['stem'] else '')+'>Chapter overview</a>'
  for sec in c['sections']+[dict(id='explore',title='Interactive experiment'),dict(id='practice',title='Problems and solutions')]:out+=f'<a href="{c["stem"]}.html#{sec["id"]}" data-topic="{sec["id"]}">{esc(sec["title"])}</a>'
  out+='</details>'
 return out+'<nav aria-label="Related courses"><a href="../foundations/index.html">Quantum Foundations</a><a href="../hardware/index.html">Quantum Hardware</a><a href="../interpretations/index.html">Interpretations of Quantum Mechanics</a></nav>'

def shell(stem,title,body):
 styles=['../computing/assets/book.css','../../styles.css','../computing/assets/learning.css','../course.css','assets/experiments.css']
 scripts=['../computing/assets/source/mathjax-config.js','../computing/assets/source/vendor/mathjax/tex-svg.js','assets/models.js','assets/experiments.js','assets/search-index.js','../computing/assets/book.js']
 description=next((c['question'] for c in CHAPTERS if c['stem']==stem),'Explore laboratory and thought experiments through 24 lessons, interactive models, worked examples, and solved problems.')
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Quantum Experiments</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="https://quantumresearch.center/education/experiments/{'' if stem=='index' else stem+'.html'}"><link rel="icon" href="../../icons/icon.svg"><script src="../computing/assets/theme.js"></script><script src="../../navigation.js"></script>{''.join(f'<link rel="stylesheet" href="{s}">' for s in styles)}{''.join(f'<script defer src="{s}"></script>' for s in scripts)}</head>
<body class="ebook revised-book" data-chapter="{stem}"><a class="skip-link" href="#main">Skip to content</a><header class="book-toolbar"><button id="menu-toggle" aria-controls="book-navigation" aria-expanded="false" aria-label="Toggle table of contents">☰ <span>Contents</span></button><a class="toolbar-title" href="index.html">Quantum Experiments</a>{COURSE_NAV}<div class="reading-tools"><button id="print-chapter" hidden>Print chapter</button><button id="search-open" aria-label="Search the book">Search <kbd>/</kbd></button><button id="text-smaller" aria-label="Decrease reading text size">A−</button><button id="text-larger" aria-label="Increase reading text size">A+</button></div></header><aside id="book-navigation" aria-label="Book navigation">{nav(stem)}<p class="nav-credit">Quantum Research Center</p></aside><button id="nav-scrim" aria-label="Close contents" hidden></button><main id="main" tabindex="-1">{body}<footer class="book-footer">Quantum Experiments · Quantum Research Center <a href="#chapter-top">Back to top ↑</a></footer></main><dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Search Quantum Experiments</h2><button id="search-close" aria-label="Close search">Close ×</button></div><label for="book-search">Find an experiment or concept</label><input id="book-search" type="search" placeholder="Try Wigner, interference, or tomography"><p id="search-status" role="status">Search all 24 chapters.</p><ol id="search-results"></ol></dialog></body></html>'''

def lab(c):
 kind=c['kind'];s=LABS[kind]
 opts='<label for="lab-mode">Configuration<select id="lab-mode">'+''.join(f'<option value="{v}">{esc(t)}</option>' for v,t in s['options'])+'</select></label>' if s['options'] else ''
 return f'''<figure class="qe-lab" data-kind="{kind}"><header><p class="qe-eyebrow">Interactive model · {"Synthetic observations" if kind in ('counts','slits','capstone') else "Idealized predictions"}</p><h3>{esc(s['title'])}</h3></header><div class="qe-scroll" role="region" tabindex="0" aria-label="Apparatus diagram; scroll horizontally on small screens">{svg(kind,s['title'])}</div><p class="qe-scroll-hint">On a small screen, swipe the diagram to inspect its components. Moving marks illustrate the model; they are not measured trajectories.</p><div class="qe-controls" hidden><label for="lab-value">{esc(s['label'])} <output id="lab-value-label" for="lab-value">{s['value']}</output><input id="lab-value" type="range" min="{s['min']}" max="{s['max']}" step="{s['step']}" value="{s['value']}"></label>{opts}<div class="qe-actions"><button type="button" data-action="play" aria-pressed="false">Play</button><button type="button" data-action="step">Step</button><button type="button" data-action="reset">Reset</button>{'<button type="button" data-action="export">Download CSV</button>' if kind=='capstone' else ''}</div></div><p class="qe-live" role="status" aria-live="polite"></p><div class="qe-results" hidden><div class="qe-scroll qe-chart-wrap" role="region" tabindex="0" aria-label="Prediction plot; scroll horizontally on small screens"><svg class="qe-chart" viewBox="0 0 640 310" role="img" aria-label="Model predictions"></svg></div><div class="qe-readout"></div><p class="qe-model-note"></p><details class="qe-data"><summary>Read the values as a table</summary><div class="qe-table-wrap"></div></details></div><figcaption>{esc(c['question'])} The text and worked examples remain available without JavaScript. Animation starts only when requested; Step gives a motion-free way to follow the model.</figcaption><noscript><p>Enable JavaScript for adjustable controls. The static apparatus, derivation, and worked values above and below provide the same conceptual explanation.</p></noscript></figure>'''

def main():
 search=[]
 for i,c in enumerate(CHAPTERS):
  source=(ROOT/'content'/f'{c["stem"]}.html').read_text()
  source=source.replace(f'<div data-lab="{c["kind"]}"></div>',lab(c))
  toc=''.join(f'<li><a href="#{s["id"]}">{esc(s["title"])}</a></li>' for s in c['sections'])+'<li><a href="#explore">Interactive experiment</a></li><li><a href="#practice">Problems and solutions</a></li>'
  body=f'<header class="chapter-header" id="chapter-top"><p class="book-kicker">{esc(c["part"])} · Chapter {i+1:02}</p><h1>{esc(c["title"])}</h1><p class="chapter-subtitle">{esc(c["question"])}</p><details class="chapter-contents"><summary>In this chapter</summary><ol>{toc}</ol></details></header>'+source
  prev=CHAPTERS[i-1] if i else None;nxt=CHAPTERS[i+1] if i+1<len(CHAPTERS) else None
  links=(f'<a rel="prev" href="{prev["stem"]}.html">← {esc(prev["title"])}</a>' if prev else '<a href="index.html">← Course overview</a>')+(f'<a rel="next" href="{nxt["stem"]}.html">{esc(nxt["title"])} →</a>' if nxt else '<a href="index.html">Course overview →</a>')
  body+='<nav class="chapter-pagination" aria-label="Chapter navigation">'+links+'</nav>'
  (ROOT/f'{c["stem"]}.html').write_text(shell(c['stem'],c['title'],body))
  soup=BeautifulSoup(source,'html.parser')
  for section in soup.select('section[id]'):search.append(dict(title=section.h2.get_text(),chapter=c['title'],url=c['stem']+'.html#'+section['id'],text=section.get_text(' ',strip=True)))
 body='''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">Advanced course · 24 chapters</p><h1>Quantum Experiments</h1><p class="chapter-subtitle">See the apparatus. Follow the argument. Question the evidence.</p><p class="chapter-intro">From individual detector clicks to Wigner’s friend, learn how laboratory experiments and thought experiments constrain our explanations of the quantum world.</p><a class="start-reading" href="01-evidence.html">Begin the course →</a><a id="resume-reading" hidden>Continue reading →</a><div class="qe-cover-stat"><span><strong>24</strong> interactive models</span><span><strong>72</strong> solved problems</span><span><strong>1</strong> reproducible capstone</span></div></header><section class="book-section" id="approach"><h2>How to use this course</h2><p>Begin with basic algebra, waves, and probability. Chapters 1–12 introduce amplitudes and experimental reasoning in context; the later chapters use two-component vectors, simple matrices, and tensor products, explained through examples. Optional sensing derivations use elementary differentiation. Quantum Foundations and Interpretations of Quantum Mechanics offer deeper mathematical and philosophical treatments.</p><p>Every chapter develops a question, an apparatus or thought scenario, a quantitative prediction, and the limits of the inference. Each includes an interactive visualization, a worked example, three problems with hints and solutions, and sources. Read sequentially or follow an experiment from the contents below.</p><p>The visualizations are idealized teaching models. Detector clicks and the downloadable capstone scan are labelled synthetic; they are not laboratory measurements. Thought scenarios explicitly separate controlled quantum memories from human observers. No interpretation is presented as experimentally selected by the animation.</p><p>Use Play for a parameter sweep or a sequence of synthetic trials. Pause to inspect a state, Step to advance without continuous motion, and Reset to return to the initial setup. Nothing autoplays. Controls work with a keyboard, values are available in tables, and the static explanations remain readable without JavaScript or a network connection.</p><p>This is a complete first teaching edition, with developed lessons throughout. The capstone asks you to report a reproducible result with uncertainty and limitations. Advanced results are identified by their assumptions and linked sources; the course does not claim full proofs of every general theorem.</p></section>'''
 for part in dict.fromkeys(c['part'] for c in CHAPTERS):
  body+=f'<section class="book-section qe-part"><h2>{esc(part)}</h2><ol class="qe-chapters">'
  for c in CHAPTERS:
   if c['part']!=part:continue
   body+=f'<li><a href="{c["stem"]}.html"><span class="qe-chapter-number">{c["stem"][:2]}</span><span><strong>{esc(c["title"])}</strong><small>{esc(c["question"])}</small></span><span aria-hidden="true">↗</span></a></li>'
  body+='</ol></section>'
 (ROOT/'index.html').write_text(shell('index','Quantum Experiments',body))
 (ROOT/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(search,ensure_ascii=False)+';\n')
 version_pages(ROOT)
 print(f'Built Quantum Experiments: {len(CHAPTERS)} developed chapters, 24 interactive models, 72 solved problems.')
if __name__=='__main__':main()
