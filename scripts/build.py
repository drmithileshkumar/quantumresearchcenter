#!/usr/bin/env python3
"""Build the research handbook using only the Python standard library."""
import argparse
import html
import json
import os
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
def esc(value): return html.escape(str(value), quote=True)
def path(item): return 'research/' + item['id'] + '/index.html'
def relative(target, source): return os.path.relpath(target, Path(source).parent).replace(os.sep, '/')
def records(book):
    return [item for part in book['parts'] for chapter in part['chapters'] for item in [chapter, *chapter['sections']]]

def render(book):
    courses=json.loads((ROOT/'content/courses.json').read_text())
    entries = records(book)
    ids = [i['id'] for i in entries]
    if len(ids) != len(set(ids)): raise ValueError('Duplicate topic ID')
    for item in entries:
        if not item['paragraphs']: raise ValueError('Empty topic: ' + item['id'])
        for ref in item['papers']:
            if ref not in book['papers']: raise ValueError('Unknown paper: ' + ref)
    outputs = {}
    def link(item, source):
        return f'<a href="{relative(path(item), source)}"><span class="number">{esc(item["number"])}</span> {esc(item["title"])}</a>'
    def bibliography(refs):
        out = '<ol class="references">'
        for ref in refs:
            paper = book['papers'][ref]
            out += f'<li><a href="{esc(paper["url"])}">{esc(paper["title"])}</a><p>{esc(paper["authors"])}. {paper["year"]}. <span class="reference-type">{esc(paper["kind"])}</span></p><p class="annotation">{esc(paper["note"])}</p></li>'
        return out + '</ol>'
    def toc(source, current='', full=False):
        out=''
        for part in book['parts']:
            out+=f'<li class="part-label">{part["number"]} &nbsp; {esc(part["title"])}</li>'
            for chapter in part['chapters']:
                out+='<li class="chapter">'+link(chapter,source)+'<ul>'
                for section in chapter['sections']: out+='<li>'+link(section,source)+'</li>'
                out+='</ul></li>'
        if current:
            out=out.replace(f'href="{relative(path(current),source)}"', f'aria-current="page" href="{relative(path(current),source)}"')
        return '<ul class="contents-list">'+out+'</ul>'
    def page(source,title,body,sections,current=None,previous=None,next_item=None):
        prefix=relative('index.html',source).removesuffix('index.html')
        pager='<nav class="page-navigation" aria-label="Reading navigation">'
        if previous: pager+=f'<a rel="prev" href="{relative(path(previous),source)}"><small>← Previous</small>{esc(previous["title"])}</a>'
        elif current: pager+=f'<a rel="prev" href="{prefix}research/index.html"><small>← Previous</small>Introduction</a>'
        else: pager+='<span></span>'
        if next_item:pager+=f'<a rel="next" href="{relative(path(next_item),source)}"><small>Next →</small>{esc(next_item["title"])}</a>'
        pager+='</nav>'
        if not current and not next_item: pager=''
        local='<nav class="on-page" aria-label="On this page"><p>On this page</p>'+''.join(f'<a href="#{anchor}">{esc(label)}</a>' for anchor,label in sections)+'</nav>'
        description = 'Courses in quantum science and computing, with interactive lessons and structured reading.' if source=='education/index.html' else (current['summary'] if current else book['subtitle'])
        if source=='index.html': description='Explore quantum science through courses, interactive lessons, research overviews, and selected literature.'
        canonical=book['url']+'/'+source.removesuffix('index.html')
        site_nav=f'<nav class="site-nav" aria-label="Site navigation"><a href="{prefix}index.html"'+(' aria-current="page"' if source=='index.html' else '')+f'>Home</a><a href="{prefix}education/index.html"'+(' aria-current="page"' if source=='education/index.html' else '')+f'>Education</a><a href="{prefix}research/index.html"'+(' aria-current="page"' if source=='research/index.html' else '')+'>Research</a></nav>'
        sidebar_contents = ('<ul class="contents-list"><li class="part-label">Courses</li>'+''.join(f'<li class="chapter"><a href="{esc(relative(course["path"], source))}">{esc(course["title"])}</a></li>' for course in courses)+'</ul>' if source=='education/index.html' else toc(source,current))
        if source=='index.html':
            sidebar_contents='<ul class="contents-list"><li class="part-label">Explore the site</li><li class="chapter"><a href="education/index.html">Education</a></li><li class="chapter"><a href="research/index.html">Research</a></li></ul>'
        intro_target='index.html' if source=='index.html' else ('education/index.html' if source=='education/index.html' else 'research/index.html')
        intro_label='Home' if source=='index.html' else ('Course catalog' if source=='education/index.html' else 'Research introduction')
        toolbar_title='Quantum Research Center' if source=='index.html' else ('Education' if source=='education/index.html' else 'Quantum Research')
        landing_nav=site_nav if source=='index.html' else ''
        outputs[source]=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Quantum Research Center</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}"><link rel="icon" href="{prefix}icons/icon.svg"><link rel="stylesheet" href="{prefix}styles.css"><script defer src="{prefix}script.js"></script></head>
<body class="{'landing' if source=='index.html' else 'reader'}"><a class="skip-link" href="#main">Skip to content</a>
<aside class="sidebar" id="contents"><a class="book-brand" href="{prefix}index.html">Quantum Research Center<span>Education &amp; Research</span></a>{site_nav}<label class="search-label" for="topic-search">Search topics</label><input id="topic-search" type="search" placeholder="Search topics…" autocomplete="off"><p id="search-status" role="status" class="search-status"></p><nav aria-label="Table of contents"><a class="intro-link" {'aria-current="page"' if source==intro_target else ''} href="{prefix}{intro_target}">{intro_label}</a>{sidebar_contents}<a class="intro-link" href="{prefix}references/index.html">Bibliography</a></nav><a class="sidebar-contact" href="mailto:{book['email']}">Contact the editors ↗</a></aside>
<div class="book-body"><header class="toolbar"><button id="menu-toggle" type="button" aria-controls="contents" aria-expanded="false" hidden>☰ <span>Contents</span></button><a href="{prefix}{intro_target}">{toolbar_title}</a>{landing_nav}<button id="font-toggle" type="button" aria-label="Increase text size" aria-pressed="false" hidden>Aa</button></header><div class="reading-layout"><main id="main" tabindex="-1"><article>{body}</article>{pager}<footer>Quantum Research Center · <a href="mailto:{book['email']}">Contact</a></footer></main>{local}</div></div></body></html>'''
    intro='''<header class="title-page"><p class="kicker">Research reference</p><h1>Quantum Research</h1><p class="subtitle">Theory, experiments, programming, and technologies</p><p class="byline">Quantum Research Center</p></header><section id="introduction"><h2>Introduction</h2><p>This handbook organizes research topics in quantum science around their theoretical basis, methods, and open problems. It covers quantum foundations and information, computation and error correction, experimental systems, programming, and physical technologies.</p><p>The chapters provide concise research overviews and annotated references. They are intended for readers with a background in quantum mechanics and linear algebra who need an entry point into a topic or its literature.</p><aside class="editorial-note"><strong>Scope of this reference</strong><p>The current entries are research overviews, not exhaustive surveys. Open questions identify directions of investigation; cited papers should be consulted for precise assumptions, proofs, and experimental results.</p></aside></section><section id="organization"><h2>Organization</h2><p>The four parts separate theoretical questions, experimental methods, programming systems, and device architectures. Numbered sections treat more specific problems within each chapter. These divisions are organizational: methods and results frequently apply across them.</p></section><section id="contents-overview"><h2>Contents</h2>'''+toc('research/index.html',full=True)+'''</section><section id="literature"><h2>Literature and references</h2><p>Each topic includes selected papers with brief descriptions of their relevance. Reference dates indicate the first arXiv submission; the linked records provide publication and revision details.</p><p><a href="../references/index.html">Complete bibliography →</a></p></section>'''
    page('research/index.html','Quantum Research',intro,[('introduction','Introduction'),('organization','Organization'),('contents-overview','Contents'),('literature','References')],next_item=entries[0])
    home='''<header class="landing-hero" id="welcome"><p class="kicker">Quantum Research Center</p><h1>The study of quantum science</h1><p class="subtitle">A place for learning and inquiry into quantum theory, computation, and information. Courses and research notes connect foundational ideas, mathematical reasoning, and open questions.</p><div class="landing-actions"><a class="primary-link" href="education/index.html">Explore courses →</a><a href="research/index.html">Read research notes →</a></div></header><div class="landing-paths"><section id="education"><p class="kicker">Education</p><h2>Courses in quantum science</h2><p>The courses develop concepts through explanations, mathematical examples, and interactive experiments. Quantum Computing begins with classical logic and proceeds through quantum states, circuits, and algorithms.</p><a href="education/index.html">Browse courses →</a></section><section id="research"><p class="kicker">Research</p><h2>Topics and open questions</h2><p>The research notes introduce topics in quantum theory, experiments, programming, and technologies, with descriptions of methods, open problems, and references to the literature.</p><a href="research/index.html">Explore research →</a></section></div><section class="landing-literature" id="references"><div><p class="kicker">References</p><h2>Papers and further reading</h2><p>The bibliography collects papers and reviews cited in the research notes, with brief annotations on their relevance.</p></div><a href="references/index.html">Browse the bibliography →</a></section>'''
    page('index.html','Home',home,[('welcome','Welcome'),('education','Education'),('research','Research'),('references','References')])
    course_list=''.join(f'<li class="course-card"><p class="kicker">{esc(course["format"])}</p><h3><a href="{esc(relative(course["path"], "education/index.html"))}">{esc(course["title"])}</a></h3><p>{esc(course["description"])}</p><p class="course-meta">{esc(course["details"])}</p><p><strong>Prerequisite:</strong> {esc(course["prerequisite"])}</p><a href="{esc(relative(course["path"], "education/index.html"))}">View course →</a></li>' for course in courses)
    education='<header class="title-page"><p class="kicker">Quantum Research Center</p><h1>Education</h1><p class="subtitle">Courses in quantum science and computing</p></header><section id="courses"><h2>Courses</h2><p>Build your understanding through structured reading, mathematical examples, and interactive experiments. Choose a course below to explore its chapters.</p><ul class="course-list">'+course_list+'</ul></section><section id="learning"><h2>Learning at your own pace</h2><p>Read chapters in order or return to individual topics using the course contents and search. Each course lists its prerequisites so you can choose a starting point that suits your background.</p><p>For topic overviews and selected literature, explore the <a href="../research/index.html">research handbook</a>.</p></section>'
    page('education/index.html','Education',education,[('courses','Courses'),('learning','Learning approach')])
    for index,item in enumerate(entries):
        body=f'<p class="kicker">{"Chapter" if "sections" in item else "Section"} {item["number"]}</p><h1><span class="heading-number">{item["number"]}</span> {esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p><section id="overview"><h2>Scope and methods</h2>'+''.join('<p>'+esc(p)+'</p>' for p in item['paragraphs'])+'</section>'
        sections=[('overview','Scope and methods')]
        if item.get('sections'):
            body+='<section id="topics"><h2>Research topics</h2><ol class="topic-list">'+''.join('<li>'+link(s,path(item))+'<p>'+esc(s['summary'])+'</p></li>' for s in item['sections'])+'</ol></section>'
            sections.append(('topics','Research topics'))
        if item['questions']:
            body+='<section id="questions"><h2>Open problems</h2><ul>'+''.join('<li>'+esc(q)+'</li>' for q in item['questions'])+'</ul></section>'
            sections.append(('questions','Open problems'))
        body+='<section id="references"><h2>Selected references</h2>'+bibliography(item['papers'])+'<p class="reference-note">Years refer to first arXiv submission. Publication details are available in the linked records.</p></section>'
        sections.append(('references','Selected references'))
        page(path(item),item['title'],body,sections,item,entries[index-1] if index else None,entries[index+1] if index+1<len(entries) else None)
    used=list(dict.fromkeys(ref for item in entries for ref in item['papers']))
    page('references/index.html','Bibliography','<p class="kicker">Reference material</p><h1>Bibliography</h1><p class="lead">Papers cited in the research handbook.</p><section id="papers"><h2>Research papers and reviews</h2>'+bibliography(used)+'</section>',[('papers','Papers and reviews')])
    outputs['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+book['url']+'/'+p.removesuffix('index.html')+'</loc></url>' for p in [*[name for name in outputs if name.endswith('.html')], 'education/computing/index.html', 'education/computing/glossary.html', 'education/computing/study-guide.html', 'education/computing/revisions.html', *['education/computing/'+chapter[0]+'.html' for chapter in json.loads((ROOT/'education/computing/chapters.json').read_text())]])+'</urlset>\n'
    outputs['robots.txt']='User-agent: *\nAllow: /\nSitemap: '+book['url']+'/sitemap.xml\n'
    return outputs

class Page(HTMLParser):
    def __init__(self,source):
        super().__init__();self.ids=[];self.refs=[];self.headings=0;self.feed(source)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='h1':self.headings+=1
        for key in ['href','src']:
            if key in attrs:self.refs.append(attrs[key])
        for key in ['aria-controls','aria-labelledby']:
            self.refs.extend('#'+v for v in attrs.get(key,'').split())
def check_output(output):
    pages={p:Page(s) for p,s in output.items() if p.endswith('.html')}
    for name,page in pages.items():
        if page.headings!=1 or len(page.ids)!=len(set(page.ids)):raise ValueError('Invalid headings or IDs: '+name)
        for ref in page.refs:
            url=urlsplit(ref)
            if url.scheme or url.netloc:continue
            target=os.path.normpath(str(Path(name).parent/url.path)) if url.path else name
            if target not in output and not (ROOT/target).is_file():raise ValueError(f'Broken link: {name} → {ref}')
            if url.fragment and target in pages and url.fragment not in pages[target].ids:raise ValueError('Broken anchor: '+ref)
    reached=set();pending=['index.html']
    while pending:
        p=pending.pop()
        if p in reached:continue
        reached.add(p)
        for ref in pages[p].refs:
            u=urlsplit(ref)
            if u.scheme or u.netloc:continue
            target=os.path.normpath(str(Path(p).parent/u.path)) if u.path else p
            if target in pages:pending.append(target)
    if set(pages)-reached:raise ValueError('Unreachable pages')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    output=render(json.loads((ROOT/'content/research.json').read_text()));check_output(output)
    for name,source in output.items():
        target=ROOT/name
        if args.check:
            if not target.exists() or target.read_text()!=source:raise ValueError('Stale output: '+name)
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
    print(f'{len(output)-2} HTML pages validated; all local links and page reachability pass.')
if __name__=='__main__':main()
