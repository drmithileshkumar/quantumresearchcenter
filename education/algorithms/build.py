#!/usr/bin/env python3
"""Build the Quantum Algorithms course with the computing course's reader design.

Manuscripts in content/*.html use a compact authoring form that this script
expands into the shared book markup:

  <section class="book-part" id="section-N-M" data-title="..."> intro </section>
  <article class="reading-topic" id="topic-N-M-K" data-title="..." data-keywords="a; b">
    prose, <figure data-figure="name"></figure>, <p class="principle">,
    <aside class="predict"><p>question</p><div class="answer">...</div></aside>,
    <ol class="problems"><li><p>question</p><div class="solution">...</div></li> ×3</ol>
  </article>

Chapter metadata is in chapters.json; reading guides and end-of-chapter
exercises in content/learning.json; glossary definitions in content/glossary.json;
figure specifications in content/figures.json (rendered by figures.py).
"""
from pathlib import Path
from html import escape
import json, re
from bs4 import BeautifulSoup, NavigableString
import figures
from figures import plain
ROOT=Path(__file__).resolve().parent
import sys
sys.path.insert(0,str(ROOT.parent))
from course_map import render_course_map, render_chapter_map
import chapter_summary
from asset_versions import version_pages
from site_logo import COURSE_LOGO
from site_navigation import COURSE_NAV
CHAPTERS=json.loads((ROOT/'chapters.json').read_text())
SUMMARIES=chapter_summary.load(ROOT,{c['stem'] for c in CHAPTERS})
LEARNING=json.loads((ROOT/'content/learning.json').read_text())
GLOSSARY=json.loads((ROOT/'content/glossary.json').read_text())
COURSE='Quantum Algorithms'
def esc(s):return escape(str(s),quote=True)
def slug(term):return re.sub(r'[^a-z0-9]+','-',plain(term).lower()).strip('-')

def navigation(current):
 out=[COURSE_LOGO+'<a class="book-home" href="index.html">Quantum Algorithms<span>Techniques and constructions</span></a><a class="nav-introduction" href="index.html">About this course</a>']
 for i,c in enumerate(CHAPTERS,1):
  stem=c['stem']
  out.append(f'<details class="nav-chapter" {"open" if stem==current else ""}><summary><span>{i:02}</span> {esc(c["title"])}</summary><a class="chapter-start" href="{stem}.html">Chapter overview</a>')
  for sec in c['sections']:
   out.append(f'<a class="nav-group" href="{stem}.html#{sec["id"]}">{sec["number"]} · {esc(sec["title"])}</a>')
   for t in sec.get('topics',[]):out.append(f'<a href="{stem}.html#{t["id"]}" data-topic="{t["id"]}"><span>{t["number"]}</span> {esc(t["title"])}</a>')
  out.append('</details>')
 out.append('<nav class="book-resources" aria-label="Learning resources"><a href="study-guide.html">Study guide</a><a href="glossary.html">Glossary</a><a href="../computing/index.html">Quantum Computing (prerequisite)</a></nav>')
 return ''.join(out)

def shell(stem,title,body):
 css=''.join(f'<link rel="stylesheet" href="{s}">' for s in ['../computing/assets/source/slides.css','../computing/assets/source/classical.css','../computing/assets/source/math.css',*(['../computing/assets/topic-map.css'] if stem=='index' or stem in {c['stem'] for c in CHAPTERS} else []),'../computing/assets/book.css','../../styles.css','../computing/assets/learning.css','../course.css'])
 js=''.join(f'<script defer src="{s}"></script>' for s in ['../computing/assets/source/mathjax-config.js','../computing/assets/source/vendor/mathjax/tex-svg.js','assets/search-index.js','assets/book.js','../computing/assets/learning.js'])
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="An interactive course on quantum algorithms by Mithilesh Kumar, organized around reusable computational techniques."><title>{esc(title)} · {COURSE}</title><link rel="icon" href="../../icons/icon.svg"><link rel="canonical" href="https://quantumresearch.center/education/algorithms/{"" if stem=="index" else stem+".html"}"><script src="../computing/assets/theme.js"></script><script src="../../navigation.js"></script>{css}{js}</head>
<body class="ebook revised-book" data-chapter="{stem}"><a class="skip-link" href="#main">Skip to content</a>
<header class="book-toolbar"><button id="menu-toggle" aria-controls="book-navigation" aria-expanded="false" aria-label="Toggle table of contents">☰ <span>Contents</span></button><a href="../index.html" class="toolbar-title">Education / {COURSE}</a>{COURSE_NAV}<div class="reading-tools"><button id="print-chapter" hidden data-print>Print chapter</button><button id="search-open" aria-label="Search the book">Search <kbd>/</kbd></button><button id="text-smaller" aria-label="Decrease reading text size">A−</button><button id="text-larger" aria-label="Increase reading text size">A+</button></div></header>
<aside id="book-navigation" aria-label="Book navigation">{navigation(stem)}<p class="nav-credit">Mithilesh Kumar</p></aside><button id="nav-scrim" aria-label="Close contents" hidden></button>
<main id="main" tabindex="-1">{body}<footer class="book-footer">Mithilesh Kumar · {COURSE} <a href="#chapter-top">Back to top ↑</a></footer></main>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Search this book</h2><button id="search-close" aria-label="Close search">Close ×</button></div><label for="book-search">Find a concept, equation, or section</label><input id="book-search" type="search" autocomplete="off" placeholder="Try Fourier, walks, or block encoding"><p id="search-status" role="status">Search the course.</p><ol id="search-results"></ol></dialog>
</body></html>'''

def frag(html):return BeautifulSoup(html,'html.parser')

def figure_markup(name):
 spec=figures.SPECS[name]
 return f'<figure class="book-drawing subsection-illustration" id="figure-{name}"><div class="drawing-scroll" tabindex="0" role="region" aria-label="{esc(plain(spec["title"]))}; scroll horizontally on small screens"><img src="assets/figures/{name}.svg" alt="{esc(plain(spec["caption"]))}" loading="lazy"/></div><figcaption>{esc(spec["caption"])}</figcaption></figure>'

def inline_figures(soup):
 """Inline SVGs so MathJax can typeset their labels; scope ids and styles per figure."""
 for n,img in enumerate(soup.select('img[src^="assets/figures/"]'),1):
  svg=(ROOT/img['src']).read_text();prefix=f'figure{n}-'
  for ident in re.findall(r'\bid="([^"]+)"',svg):
   svg=svg.replace(f'id="{ident}"',f'id="{prefix}{ident}"').replace(f'url(#{ident})',f'url(#{prefix}{ident})')
  svg=re.sub(r'aria-labelledby="([^"]*)"',lambda m:'aria-labelledby="'+' '.join(prefix+x for x in m.group(1).split())+'"',svg,count=1)
  scope=lambda css:re.sub(r'([^{}]+)\{',lambda m:','.join(f'#{prefix}svg {x.strip()}' for x in m.group(1).split(','))+'{',css)
  svg=re.sub(r'<style>(.*?)</style>',lambda m:'<style>'+scope(m.group(1))+'</style>',svg,flags=re.S)
  svg=svg.replace('<svg ',f'<svg id="{prefix}svg" class="book-figure" ',1)
  img.replace_with(frag(svg))

def expand(stem,chapter,soup,glossary_urls):
 """Turn authored parts and topics into book markup; return the outline found."""
 outline=[]
 for part in soup.select('section.book-part'):
  ident=part['id'];number=ident.split('-',1)[1].replace('-','.');title=part['data-title']
  del part['data-title'];part['aria-labelledby']=ident+'-heading'
  part.insert(0,frag(f'<p class="part-label">{number}</p><h2 id="{ident}-heading">{esc(title)}</h2>'))
  outline.append(dict(id=ident,number=number,title=title,topics=[]))
 for art in soup.select('article.reading-topic'):
  ident=art['id'];number=ident.split('-',1)[1].replace('-','.');title=art['data-title']
  part_id='section-'+'-'.join(ident.split('-')[1:3])
  sec=next(s for s in outline if s['id']==part_id)
  sec['topics'].append(dict(id=ident,number=number,title=title))
  keywords=[k.strip() for k in art.get('data-keywords','').split(';') if k.strip()]
  problems=art.find('ol',class_='problems')
  if problems is None:raise ValueError('Missing problems: '+ident)
  problems.extract()
  items=problems.find_all('li',recursive=False)
  if len(items)!=3:raise ValueError(f'Expected three problems in {ident}')
  # Prose: everything except the problems, wrapped like the computing book.
  exposition=soup.new_tag('div',attrs={'class':'book-exposition'})
  for child in list(art.contents):exposition.append(child.extract())
  for fig in exposition.select('figure[data-figure]'):
   name=fig['data-figure']
   if name not in figures.SPECS:raise ValueError(f'Unknown figure {name} in {ident}')
   fig.replace_with(frag(figure_markup(name)))
  for aside in exposition.select('aside.predict'):
   answer=aside.find('div',class_='answer');answer.extract()
   question=aside.decode_contents().strip()
   question=re.sub(r'^<p>','<p><strong>Predict first.</strong> ',question,count=1)
   aside.replace_with(frag(f'<div class="prediction">{question}</div><details class="prediction-answer"><summary>Check your prediction</summary>{answer.decode_contents()}</details>'))
  # Figures sit after the prose block in the computing book; keep authored order here.
  section=soup.new_tag('section',attrs={'class':'book-section reading-topic','id':ident,'aria-labelledby':ident+'-heading'})
  section.append(frag(f'<h3 class="topic-heading" id="{ident}-heading"><span class="topic-number">{number}</span> {esc(title)}<a aria-label="Link to {esc(plain(title))}" class="heading-link" href="#{ident}">§</a></h3>'))
  if keywords:
   text=re.sub(r'\s+',' ',exposition.get_text(' ')).lower().replace('-',' ');text=re.sub(r'(\w)s\b',r'\1',text)
   links=[]
   for k in keywords:
    if re.sub(r'(\w)s\b',r'\1',k.lower().replace('-',' ')) not in text:print(f'Keyword check: "{k}" does not occur in {ident}')
    s=slug(k)
    glossary_urls.setdefault(s,f'{stem}.html#{ident}')
    links.append(f'<a class="glossary-term" href="glossary.html#{s}">{esc(k)}</a>' if s in GLOSSARY_SLUGS else f'<span>{esc(k)}</span>')
   section.append(frag(f'<p class="keywords" aria-label="Keywords defined in this subsection">{"<span class=\"keyword-sep\" aria-hidden=\"true\"> · </span>".join(links)}</p>'))
  section.append(exposition)
  lis=[]
  for n,li in enumerate(items,1):
   sol=li.find('div',class_='solution');sol.extract()
   lis.append(f'<li id="{ident}-problem-{n}"><div class="problem-text">{li.decode_contents().strip()}</div><details class="problem-solution"><summary><span class="solution-closed">Show solution</span><span class="solution-open">Hide solution</span></summary>{sol.decode_contents().strip()}</details></li>')
  section.append(frag(f'<details class="probing-question"><summary class="question-label">Problems</summary><ol>{"".join(lis)}</ol></details>'))
  art.replace_with(section)
 return outline

def link_glossary(soup):
 """Link the first prose occurrence of each glossary term in a chapter."""
 for term,entry in GLOSSARY.items():
  # Single ordinary words (order, period, reflection) are linked only from keyword lines.
  acronym=term.isupper()
  if ' ' not in term and not acronym:continue
  pattern=re.compile(r'(?<![\w-])'+re.escape(term)+r'(?![\w-])',0 if acronym else re.I);done=False
  for p in soup.select('.book-exposition > p'):
   if 'principle' in (p.get('class') or []):continue
   for node in list(p.find_all(string=True)):
    if node.find_parent(['a','script','style','em','strong']):continue
    pieces=re.split(r'(\\\(.*?\\\)|\\\[.*?\\\])',str(node),flags=re.S);offset=0
    for piece in pieces:
     m=None if piece.startswith(('\\(','\\[')) else pattern.search(piece)
     if m:
      a,b=offset+m.start(),offset+m.end();text=str(node)
      tag=soup.new_tag('a',href='glossary.html#'+slug(term));tag['class']='glossary-term';tag['title']=plain(entry);tag.string=text[a:b]
      node.replace_with(NavigableString(text[:a]),tag,NavigableString(text[b:]));done=True;break
     offset+=len(piece)
    if done:break
   if done:break

def guide(stem):
 d=LEARNING[stem]
 return '<details class="learning-guide"><summary>Reading guide · preparation, aims, and assumptions</summary>'+f'<p>{esc(d["purpose"])}</p><h3>Before you begin</h3><p>{esc(d["before"])}</p><h3>What you should be able to do</h3><ul>'+''.join(f'<li>{esc(x)}</li>' for x in d['outcomes'])+f'</ul><h3>The example to follow</h3><p>{esc(d["example"])}</p><h3>Scope and assumptions</h3><p>{esc(d["limits"])}</p></details>'

def exercises(stem,title,index):
 d=LEARNING[stem];out=['<section class="chapter-practice" id="practice"><h2>Questions and worked problems</h2><p>Attempt each question before opening a hint. Explain your reasoning, then compare it with the solution.</p>']
 for i,e in enumerate(d['exercises'],1):
  ident=f'exercise-{i}'
  hints=''.join(f'<details class="exercise-hint"><summary>Hint {n}</summary><p>{esc(h)}</p></details>' for n,h in enumerate(e['hints'],1))
  out.append(f'<article class="exercise" id="{ident}"><h3>{i}. {esc(e["kind"])} <a class="heading-link" href="#{ident}" aria-label="Link to exercise {i}">§</a></h3><p>{esc(e["question"])}</p>{hints}<details class="exercise-solution"><summary>Worked solution</summary><p>{esc(e["answer"])}</p></details><p><a href="#{esc(e["review"])}">Revisit the relevant explanation</a></p></article>')
  index.append(dict(title=title+' — '+e['kind'],chapter='Exercises',url=f'{stem}.html#{ident}',text=plain(e['question']+' '+e['answer'])))
 out.append(f'<p class="chapter-bridge"><strong>Where this leads.</strong> {esc(d["next"])}</p></section>')
 return ''.join(out)

GLOSSARY_SLUGS={slug(t) for t in GLOSSARY}

def main():
 count=figures.build()
 index=[];glossary_urls={};problems=0
 import os;only=os.environ.get('ONLY','').split(',') if os.environ.get('ONLY') else None
 for i,c in enumerate(CHAPTERS,1):
  if only and c['stem'][:2] not in only:continue
  stem=c['stem'];raw=(ROOT/'content'/f'{stem}.html').read_text()
  bad=[m.group(0)[:60] for m in re.finditer(r'\\\((.*?)\\\)|\\\[(.*?)\\\]',raw,re.S) if '<' in m.group(0)]
  if bad:raise ValueError(f'Write &lt; inside TeX in {stem}: {bad}')
  soup=BeautifulSoup(raw,'html.parser')
  outline=expand(stem,c,soup,glossary_urls)
  planned=[(s['id'],s['title'],[t['title'] for t in s['topics']]) for s in c['sections']]
  found=[(s['id'],s['title'],[t['title'] for t in s['topics']]) for s in outline]
  if planned!=found:raise ValueError(f'chapters.json does not match the manuscript for {stem}:\n{planned}\n{found}')
  for s,f in zip(c['sections'],outline):
   if [t['id'] for t in s['topics']]!=[t['id'] for t in f['topics']]:raise ValueError('Topic ids differ in '+stem)
  if stem not in LEARNING:raise ValueError('Missing reading guide: '+stem)
  for e in LEARNING[stem]['exercises']:
   if not soup.find(id=e['review']):raise ValueError(f'Exercise review link {e["review"]} missing in {stem}')
  link_glossary(soup)
  for sec in soup.select('.reading-topic'):
   searchable=frag(str(sec))
   for hidden in searchable.select('.problem-solution,figure,.prediction-answer'):hidden.decompose()
   heading=searchable.select_one('.topic-heading')
   index.append(dict(title=heading.get_text(' ',strip=True).replace('§','').strip(),chapter=c['title'],url=f'{stem}.html#{sec["id"]}',text=searchable.get_text(' ',strip=True)))
  problems+=len(soup.select('.probing-question li'))
  inline_figures(soup)
  ids=[el['id'] for el in soup.select('[id]')]
  dup={x for x in ids if ids.count(x)>1}
  if dup:raise ValueError(f'Duplicate ids in {stem}: {dup}')
  toc=''.join(f'<li class="contents-part"><a href="#{s["id"]}"><span>{s["number"]}</span> {esc(s["title"])}</a><details><summary>Topics in this section</summary><ol>'+''.join(f'<li><a href="#{t["id"]}"><span>{t["number"]}</span> {esc(t["title"])}</a></li>' for t in s['topics'])+'</ol></details></li>' for s in c['sections'])
  ntopics=sum(len(s['topics']) for s in c['sections'])
  opening=''.join(f'<p{" class=\"chapter-intro\"" if n==0 else ""}>{esc(p)}</p>' for n,p in enumerate(c['opening']))
  header=f'<header class="chapter-header" id="chapter-top"><p class="book-kicker">Chapter {i:02}</p><h1>{esc(c["title"])}</h1>{render_chapter_map(c["title"],c)}{opening}<p class="chapter-subtitle">{esc(c["question"])}</p><p class="chapter-intro">{esc(c["intro"])}</p><details class="chapter-contents"><summary>In this chapter · {len(c["sections"])} sections · {ntopics} topics</summary><ol>{toc}</ol></details></header>'
  prev=CHAPTERS[i-2] if i>1 else None;nxt=CHAPTERS[i] if i<len(CHAPTERS) else None
  links=(f'<a rel="prev" href="{prev["stem"]}.html"><small>Previous chapter</small>{esc(prev["title"])} ←</a>' if prev else '<a href="index.html"><small>Course overview</small>← Introduction</a>')+(f'<a rel="next" href="{nxt["stem"]}.html"><small>Next chapter</small>{esc(nxt["title"])} →</a>' if nxt else '<a href="index.html"><small>Return to</small>Course contents →</a>')
  body='<nav class="chapter-pagination chapter-pagination-top" aria-label="Chapter navigation, top of page">'+links+'</nav>'+header+guide(stem)+str(soup)+chapter_summary.render(SUMMARIES.get(stem))+exercises(stem,c['title'],index)+'<nav class="chapter-pagination" aria-label="Chapter navigation">'+links+'</nav>'
  (ROOT/f'{stem}.html').write_text(shell(stem,c['title'],body))
 intro=f'''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">A course in techniques · Mithilesh Kumar</p><h1>{COURSE}</h1><p class="chapter-subtitle">From computational techniques to complete algorithms</p><p class="chapter-intro">A quantum algorithm is not a superposition followed by hope. It is a construction: specify what the input gives you, encode the property you need into amplitudes or phases, arrange interference so that the property becomes a measurement outcome, and account for every resource. This course builds that craft one technique at a time.</p><a class="start-reading" href="{CHAPTERS[0]["stem"]}.html">Begin reading <span aria-hidden="true">→</span></a><a id="resume-reading" hidden>Continue where you left off →</a></header>
<section class="book-about"><h2>Prerequisites and approach</h2><p>The course continues <a href="../computing/index.html">Quantum Computing</a>. It assumes amplitudes, unitary circuits, measurement, reversible oracles, phase kickback, and amplitude amplification as developed there, but no further mathematics or physics. Norms, spectra, Hamiltonians, singular values, and polynomial approximation are built from worked examples at the point where an algorithm needs them.</p><p>The chapters are organized by technique rather than by famous algorithm. Named algorithms such as Bernstein–Vazirani, phase estimation, Shor’s factoring, amplitude estimation, element distinctness, quantum signal processing, Trotter simulation, the variational eigensolver, QAOA, and measurement-based computation appear as applications or compositions of those techniques. Each technique is carried from a small circuit you can verify by hand to a statement about general input sizes, with its assumptions, costs, and limits.</p></section>
{render_course_map(COURSE,CHAPTERS)}<section class="book-about"><h2>How to use this course</h2><p>Each subsection develops one step of an argument, lists the terms it defines, often includes a circuit or plot, and ends with three problems: a check of the central idea, a calculation applying it, and a challenge that probes a limit or a tempting mistake. Every problem has a worked solution behind “Show solution”. Each chapter opens with a reading guide and closes with exercises that have hints.</p><p>Small examples motivate general results; they do not prove them. When a chapter relies on a theorem whose proof lies beyond it, the text says so and links to the source. The <a href="study-guide.html">study guide</a> suggests routes through the material and the <a href="glossary.html">glossary</a> collects definitions.</p></section>'''
 (ROOT/'index.html').write_text(shell('index','Introduction',intro))
 # Glossary
 entries=''
 for term in sorted(GLOSSARY,key=str.lower):
  s=slug(term);url=glossary_urls.get(s)
  if url is None and only:continue
  if url is None:raise ValueError(f'Glossary term "{term}" is not listed as a keyword in any subsection')
  entries+=f'<div id="{s}" class="glossary-entry"><dt>{esc(term)}</dt><dd><p>{esc(GLOSSARY[term])}</p><a href="{url}">Read the explanation →</a></dd></div>'
  index.append(dict(title=term,chapter='Glossary',url='glossary.html#'+s,text=plain(GLOSSARY[term])))
 glossary='<header class="chapter-header" id="chapter-top"><p class="book-kicker">Reference</p><h1>Glossary</h1><p>Short definitions with links to the full explanations. A definition depends on the assumptions stated in its subsection.</p></header><div class="glossary-filter" hidden><label for="glossary-query">Find a term or idea</label><input type="search" id="glossary-query" autocomplete="off"><p id="glossary-status" role="status"></p></div><dl class="glossary-list">'+entries+'</dl>'
 (ROOT/'glossary.html').write_text(shell('glossary','Glossary',glossary))
 route=''.join(f'<li><a href="{c["stem"]}.html">{esc(c["title"])}</a>: {esc(LEARNING.get(c["stem"],{}).get("purpose",""))}</li>' for c in CHAPTERS)
 study=f'''<header class="chapter-header" id="chapter-top"><p class="book-kicker">Reading and review</p><h1>Study guide</h1><p>Read Chapter 1 first: it sets out the design questions every later chapter answers. The technique chapters then build on one another, with the dependencies described below.</p></header><section class="book-about"><h2>A route through the course</h2><ol>{route}</ol><h2>Dependencies between techniques</h2><p>Coherent computation (Chapter 2) supplies the clean subroutines that every later oracle assumes. Phase encoding (Chapter 3) and the Fourier transform (Chapter 4) combine into phase estimation, which Chapter 5 reuses for amplitude estimation and Chapter 11 rebuilds with one control qubit and feedback. Reflections from Chapter 5 reappear as the steps of quantum walks in Chapter 6 and as the walk operators of qubitization in Chapter 8. Block encodings (Chapter 7) are the input to polynomial transformations (Chapter 8), which give one of the two simulation strategies compared in Chapter 9. Variational methods (Chapter 10) trade the guarantees of the earlier chapters for shallow circuits and classical optimization, and say so.</p><h2>Working through a subsection</h2><p>Read the explanation once, then redo its central calculation without looking. When a subsection asks you to predict, write the prediction and your reason before opening the answer. The three problems at the end of each subsection move from checking the idea, to applying it in a new instance, to exposing a limit or a common incorrect implementation. Attempt them in order. The chapter exercises at the end combine several subsections; open hints one at a time.</p><h2>Assumptions to keep visible</h2><p>A claimed advantage must state the input model, the output required, the allowed error, and the resources counted. Queries, gates, depth, qubits, precision, repetitions, postselection, and classical processing are different resources. Access to a unitary does not automatically include its inverse or a controlled version, and a quantum state encoding a vector is not a classical list of its entries. Small worked circuits check the mathematics of an example; they do not establish scaling.</p><h2>Checking the worked examples</h2><p>The repository includes numerical checks of the small instances used in the text (<code>education/algorithms/checks/worked_examples.py</code> and <code>education/checks/check_mathematics.py</code>). They confirm amplitudes, probabilities, and identities for the stated examples; they do not prove the general theorems the text cites.</p><h2>Reader controls</h2><p>Use Contents to move between topics, Search (or the / key) to find an idea, and A− or A+ to adjust the text. Print chapter expands hidden hints and solutions for a printed copy. Your text size and last reading position are kept only in this browser.</p></section>'''
 (ROOT/'study-guide.html').write_text(shell('study-guide','Study guide',study))
 (ROOT/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(index,ensure_ascii=False).replace('</','<\\/')+';\n')
 version_pages(ROOT)
 topics=sum(len(s.get('topics',[])) for c in CHAPTERS for s in c['sections'])
 print(f'Built {COURSE}: {len(CHAPTERS)} chapters, {topics} topics, {problems} subsection problems, {count} figures, {len(GLOSSARY)} glossary terms.')
if __name__=='__main__':main()
