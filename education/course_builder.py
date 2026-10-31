#!/usr/bin/env python3
"""Shared build for the courses that render chapter manuscripts with the computing-course theme.

Each course's build.py holds only what is particular to it, as a Course. Chapters come from chapters.json
and content/<stem>.html, and the page layout from templates/course.html.in.
"""
from dataclasses import dataclass
from html import escape as esc
import json
from pathlib import Path
from typing import Callable

from bs4 import BeautifulSoup

from asset_versions import version_pages
import chapter_exercises
import chapter_summary
from course_map import render_chapter_map, render_course_map
from page_template import fill
from site_logo import COURSE_LOGO
from site_navigation import COURSE_NAV

TEMPLATE = Path(__file__).resolve().parent / 'templates/course.html.in'
FOIL_GUIDE = (('Starting point', 'prerequisites'), ('Anchor example', 'example'), ('Principle at work', 'principle'), ('Foil', 'foil'))
METHOD_GUIDE = (('Starting point', 'prerequisites'), ('Anchor example', 'example'), ('Method', 'method'), ('Watch for', 'pitfall'))
BASIC_GUIDE = (('Starting point', 'prerequisites'), ('Anchor example', 'example'))


@dataclass
class Course:
    root: Path
    title: str
    tagline: str
    subtitle: str
    about: str
    prerequisites: str
    extra: str
    description: str
    resources: str  # The related-links <nav> closing the sidebar.
    search_example: str
    guide: tuple
    credit: str = 'Mithilesh Kumar'
    lesson_note: str = 'This lesson includes explanations, worked examples, and problems with solutions. Advanced results whose proofs are outside the chapter are identified explicitly.'
    draft_note: str = ' contain draft lessons with worked examples and solved problems. These are teaching manuscripts in development; advanced results are stated with their assumptions and sources where a full proof lies beyond the course.'
    styles: tuple = ()
    scripts: tuple = ()
    prepare: Callable = lambda: None  # Runs first; generates or verifies this course's assets.


def navigation(course, current):
 out=COURSE_LOGO+f'<a class="book-home" href="index.html">{esc(course.title)}<span>{esc(course.tagline)}</span></a><a class="nav-introduction" href="index.html">About this course</a>'
 for i,c in enumerate(course.chapters,1):
  stem=c['stem'];active=' open' if stem==current else ''
  out+=f'<details class="nav-chapter"{active}><summary><span>{i:02}</span> {esc(c["title"])}</summary><a class="chapter-start" href="{stem}.html"'+(' aria-current="page"' if stem==current else '')+'>Chapter overview</a>'
  for sec in c['sections']:out+=f'<a href="{stem}.html#{sec["id"]}" data-topic="{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a>'
  out+='</details>'
 return out+course.resources


def shell(course, stem, title, body):
 chapter_stems={c['stem'] for c in course.chapters}
 css=''.join(f'<link rel="stylesheet" href="{s}">' for s in dict.fromkeys(['../computing/assets/source/slides.css','../computing/assets/source/classical.css','../computing/assets/source/math.css',*(['../computing/assets/topic-map.css'] if stem=='index' or stem in chapter_stems else []),'../computing/assets/book.css','../../styles.css','../computing/assets/learning.css','../course.css',*course.styles]))
 js=''.join(f'<script defer src="{s}"></script>' for s in ['../computing/assets/source/mathjax-config.js','../computing/assets/source/vendor/mathjax/tex-svg.js','assets/search-index.js','assets/book.js',*course.scripts])
 return fill(TEMPLATE,dict(DESCRIPTION=course.description,TITLE=esc(title),COURSE=course.title,SLUG=course.root.name,PAGE='' if stem=='index' else stem+'.html',CSS=css,JS=js,STEM=stem,COURSE_NAV=COURSE_NAV,NAVIGATION=navigation(course,stem),CREDIT=course.credit,BODY=body,SEARCH_EXAMPLE=course.search_example))


def build(course):
 course.prepare()
 root=course.root
 chapters=course.chapters=json.loads((root/'chapters.json').read_text())
 exercises=chapter_exercises.load(root)
 summaries=chapter_summary.load(root,{c['stem'] for c in chapters})
 search=[]
 drafts=sum(c.get('status')=='draft' for c in chapters)
 for i,c in enumerate(chapters,1):
  stem=c['stem'];manuscript=(root/'content'/f'{stem}.html').read_text()
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
  notice=course.lesson_note if status=='draft' else 'This chapter is an outline; its lesson remains to be developed.'
  toc=''.join(f'<li><a href="#{sec["id"]}"><span>{sec["number"]}</span> {esc(sec["title"])}</a></li>' for sec in c['sections'])
  guide=''.join(f'<p><strong>{label}:</strong> {esc(c[key])}</p>' for label,key in course.guide)
  body=f'<header class="chapter-header" id="chapter-top"><p class="book-kicker">Chapter {i:02} · {label}</p><h1>{esc(c["title"])}</h1>{render_chapter_map(c["title"],c)}<p class="chapter-subtitle">{esc(c["question"])}</p><details class="chapter-contents"><summary>In this chapter · {len(c["sections"])} sections</summary><ol>{toc}</ol></details></header><details class="learning-guide"><summary>Reading guide · preparation and approach</summary>{guide}<p>{notice}</p></details>'+manuscript
  body+=chapter_summary.render(summaries.get(stem))+chapter_exercises.render(stem,c['title'],exercises.get(stem,[]),{el['id'] for el in soup.select('[id]')},search)
  prev=chapters[i-2] if i>1 else None;nxt=chapters[i] if i<len(chapters) else None
  links=(f'<a rel="prev" href="{prev["stem"]}.html"><small>Previous chapter</small>{esc(prev["title"])} ←</a>' if prev else '<a href="index.html"><small>Course overview</small>← Introduction</a>')+(f'<a rel="next" href="{nxt["stem"]}.html"><small>Next chapter</small>{esc(nxt["title"])} →</a>' if nxt else '<a href="index.html"><small>Return to</small>Course contents →</a>')
  body='<nav class="chapter-pagination chapter-pagination-top" aria-label="Chapter navigation, top of page">'+links+'</nav>'+body+'<nav class="chapter-pagination" aria-label="Chapter navigation">'+links+'</nav>'
  (root/f'{stem}.html').write_text(shell(course,stem,c['title'],body))
  ids=[el['id'] for el in soup.select('[id]')]
  if len(ids)!=len(set(ids)):raise ValueError('Duplicate manuscript IDs: '+stem)
  for sec in c['sections']:
   element=soup.find(id=sec['id'])
   if element is None:raise ValueError('Missing planned section: '+sec['id'])
   search.append(dict(title=sec['title'],chapter=c['title'],url=stem+'.html#'+sec['id'],text=element.get_text(' ',strip=True)))
 body=f'''<header class="chapter-header book-cover" id="chapter-top"><p class="book-kicker">Course manuscript · {course.credit}</p><h1>{course.title}</h1><p class="chapter-subtitle">{course.subtitle}</p><p class="chapter-intro">{course.about}</p><a class="start-reading" href="{chapters[0]["stem"]}.html">Begin reading <span aria-hidden="true">→</span></a><a id="resume-reading" hidden>Continue where you left off →</a></header>
<section class="book-about"><h2>Prerequisites and approach</h2><p>{course.prerequisites}</p><p>{drafts} of {len(chapters)} chapters{course.draft_note}</p>{course.extra}</section>
{render_course_map(course.title,chapters)}'''
 (root/'index.html').write_text(shell(course,'index',course.title,body))
 (root/'assets/search-index.js').write_text('window.BOOK_SEARCH = '+json.dumps(search,ensure_ascii=False)+';\n')
 version_pages(root)
 print(f'Built {course.title}: {drafts} draft lessons, {len(chapters)-drafts} outlines.')
