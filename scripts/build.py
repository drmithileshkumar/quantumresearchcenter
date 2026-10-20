#!/usr/bin/env python3
"""Build the research handbook using only the Python standard library."""
import argparse
import hashlib
import html
import json
import os
import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
from paper_news import render_news
# Editorial pages and legacy redirects stay out of the public sitemap.
RESEARCH_REDIRECTS = json.loads((Path(__file__).resolve().parents[1]/'content/research-redirects.json').read_text())
UNLISTED = {'news/papers.html', *RESEARCH_REDIRECTS}

ROOT = Path(__file__).resolve().parents[1]
def esc(value): return html.escape(str(value), quote=True)
def path(item): return item['_path']
def relative(target, source): return os.path.relpath(target, Path(source).parent).replace(os.sep, '/')
def records(book):
    """Flatten a recursive topic tree while retaining its URL and ancestors."""
    result=[]
    def walk(nodes, parents=()):
        siblings=set()
        for node in nodes:
            slug=node['id']
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):
                raise ValueError('Invalid topic slug: '+slug)
            if slug in siblings: raise ValueError('Duplicate sibling topic: '+slug)
            siblings.add(slug)
            item=dict(node)
            item['_path']='research/'+'/'.join([p['id'] for p in parents]+[slug])+'/index.html'
            item['_parents']=parents
            result.append(item)
            walk(node.get('children',[]), (*parents,item))
    walk(book['categories'])
    return result

def render(book):
    courses=json.loads((ROOT/'content/courses.json').read_text())
    entries = records(book)
    ids = [path(i) for i in entries]
    if len(ids) != len(set(ids)): raise ValueError('Duplicate topic ID')
    for item in entries:
        if not item['paragraphs']: raise ValueError('Empty topic: ' + item['id'])
        for ref in item['papers']:
            if ref not in book['papers']: raise ValueError('Unknown paper: ' + ref)
    outputs = {}
    def link(item, source):
        return f'<a href="{relative(path(item), source)}">{esc(item["title"])}</a>'
    def bibliography(refs):
        out = '<ol class="references">'
        for ref in refs:
            paper = book['papers'][ref]
            out += f'<li><a href="{esc(paper["url"])}">{esc(paper["title"])}</a><p>{esc(paper["authors"])}. {paper["year"]}. <span class="reference-type">{esc(paper["kind"])}</span></p><p class="annotation">{esc(paper["note"])}</p></li>'
        return out + '</ol>'
    children={None:[]}
    for item in entries:
        parent=path(item['_parents'][-1]) if item['_parents'] else None
        children.setdefault(parent,[]).append(item)
    def toc(source, current='', full=False):
        def branch(parent=None):
            out='<ul class="contents-list">' if parent is None else '<ul>'
            for item in children.get(parent,[]):
                anchor=link(item,source)
                if current and path(item)==path(current):
                    anchor=anchor.replace('<a ', '<a aria-current="page" ',1)
                out+='<li class="chapter research-node">'+anchor
                if path(item) in children:out+=branch(path(item))
                out+='</li>'
            return out+'</ul>'
        return branch()
    def keywords(items,source):
        return '<ol class="research-question-list">'+''.join(
            '<li><a href="'+relative(path(item),source)+'">'+esc(item['title'])+'<span aria-hidden="true"> ↗</span></a><p>'+esc(item['summary'])+'</p></li>'
            for item in items)+'</ol>'
    def breadcrumbs(item):
        source=path(item)
        return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="'+relative('research/index.html',source)+'">Research</a></li>'+''.join(
            '<li>'+link(parent,source)+'</li>' for parent in item['_parents'])+'<li><span aria-current="page">'+esc(item['title'])+'</span></li></ol></nav>'
    def page(source,title,body,sections,current=None,previous=None,next_item=None,description=None):
        if source.startswith('news/'):
            # News sections are (href, label) links; a None href starts a labelled group.
            up='../'*source.count('/')
            navigation=''.join(f'<p class="kicker">{esc(label)}</p>' if href is None else f'<a href="{esc(href)}">{esc(label)}</a>' for href,label in sections)
            mathjax=f'<script defer src="{up}education/computing/assets/source/mathjax-config.js"></script><script defer src="{up}education/computing/assets/source/vendor/mathjax/tex-svg.js"></script>' if '\\(' in body or '\\[' in body else ''
            outputs[source]=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Quantum Research Center</title><meta name="description" content="{esc(description or 'Selected quantum research papers: problems, results, and transferable methods.')}"><link rel="canonical" href="{book['url']}/{source.removesuffix('index.html')}">{'<meta name="robots" content="noindex">' if source in UNLISTED else ''}<link rel="icon" href="{up}icons/icon.svg"><script src="{up}education/computing/assets/theme.js"></script><link rel="stylesheet" href="{up}styles.css">{mathjax}</head>
<body class="news-reader"><a class="skip-link" href="#main">Skip to content</a><header class="news-toolbar"><a class="news-brand" href="{up}index.html">Quantum Research Center</a><nav aria-label="News navigation"><a href="{up}news/index.html" {'aria-current="page"' if source=='news/index.html' else ''}>Selected papers</a>{'<a href="papers.html" aria-current="page">Review &amp; approve</a>' if source=='news/papers.html' else ''}</nav></header><div class="news-layout"><aside class="news-index"><details open><summary>Browse</summary><nav aria-label="Section navigation">{navigation}</nav></details><script>if(matchMedia("(max-width:900px)").matches)document.currentScript.previousElementSibling.open=false</script></aside><main id="main" tabindex="-1">{body}<footer>Quantum Research Center · <a href="mailto:{book['email']}">Contact</a></footer></main></div></body></html>'''
            return
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
        if source.startswith('research/') or source=='references/index.html':
            sidebar_contents+=f'<a class="intro-link" '+('aria-current="page" ' if source=='research/students/index.html' else '')+f'href="{relative("research/students/index.html",source)}">Students and Contributions</a>'
        intro_target='index.html'  if source=='index.html' else ('education/index.html' if source=='education/index.html' else 'research/index.html')
        intro_label='Home' if source=='index.html' else ('Course catalog' if source=='education/index.html' else 'Research introduction')
        toolbar_title='Quantum Research Center' if source=='index.html' else ('Education' if source=='education/index.html' else 'Quantum Research')
        landing_nav=site_nav if source=='index.html' else ''
        mathjax=(f'<script defer src="{prefix}education/computing/assets/source/mathjax-config.js"></script><script defer src="{prefix}education/computing/assets/source/vendor/mathjax/tex-svg.js"></script>' if '\\(' in body or '\\[' in body else '')
        outputs[source]=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Quantum Research Center</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}"><link rel="icon" href="{prefix}icons/icon.svg"><script src="{prefix}education/computing/assets/theme.js"></script><link rel="stylesheet" href="{prefix}styles.css"><script defer src="{prefix}script.js"></script>{mathjax}</head>
<body class="{'landing' if source=='index.html' else 'reader'}{' research-question' if current and current.get('manuscript') else ''}"><a class="skip-link" href="#main">Skip to content</a>
<aside class="sidebar" id="contents"><a class="book-brand" href="{prefix}index.html">Quantum Research Center<span>Education &amp; Research</span></a>{site_nav}<label class="search-label" for="topic-search">Search topics</label><input id="topic-search" type="search" placeholder="Search topics…" autocomplete="off"><p id="search-status" role="status" class="search-status"></p><nav aria-label="Table of contents"><a class="intro-link" {'aria-current="page"' if source==intro_target else ''} href="{prefix}{intro_target}">{intro_label}</a>{sidebar_contents}<a class="intro-link" href="{prefix}references/index.html">Bibliography</a></nav><a class="sidebar-contact" href="mailto:{book['email']}">Contact the editors ↗</a></aside>
<div class="book-body"><header class="toolbar"><button id="menu-toggle" type="button" aria-controls="contents" aria-expanded="false" hidden>☰ <span>Contents</span></button><a href="{prefix}{intro_target}">{toolbar_title}</a>{landing_nav}<button id="font-toggle" type="button" aria-label="Increase text size" aria-pressed="false" hidden>Aa</button></header><div class="reading-layout"><main id="main" tabindex="-1"><article>{body}</article>{pager}<footer>Quantum Research Center · <a href="mailto:{book['email']}">Contact</a></footer></main>{local}</div></div></body></html>'''
    intro='<header class="title-page research-opening"><p class="kicker">Research</p><h1>Questions at the edge of quantum science</h1><p class="subtitle">Explore the foundations, possibilities, and limits of quantum theory through questions we can make precise.</p></header><section id="introduction"><h2>From understanding to investigation</h2><p>Each question begins with a physical or computational problem, develops a mathematical model, and separates established results from unresolved issues. Follow a worked starting investigation before attempting the proposed extension.</p><p>These are selected research directions, not an exhaustive list of open problems or a claim that the Center has solved them. A reproducible exercise builds the tools; a research contribution must add a justified result beyond that baseline.</p></section><section id="contents-overview"><h2>Explore the four fields</h2><div class="research-categories">'
    for number,category in enumerate(children[None],1):
        intro+='<section class="research-category"><p class="kicker">'+f'{number:02} · {len(children.get(path(category),[]))} questions'+'</p><h3>'+link(category,'research/index.html')+'</h3><p>'+esc(category['summary'])+'</p>'+keywords(children.get(path(category),[]),'research/index.html')+'</section>'
    intro+='</div></section><section id="literature"><h2>Read the argument, then the source</h2><p>Known results link to papers near the claims they support. Each question also has an annotated reading list. Model assumptions and theorem scope matter as much as the equation itself.</p><a href="../references/index.html">Browse the bibliography →</a></section><section id="students"><h2>People and contributions</h2><p>Explore the projects and documented contributions of students working with the Center.</p><a href="students/index.html">Students and contributions →</a></section>'
    page('research/index.html','Quantum Research',intro,[('introduction','How to explore'),('contents-overview','Research questions'),('literature','Sources'),('students','People')])
    home='''<header class="landing-hero" id="welcome"><p class="kicker">Quantum Research Center</p><h1>The study of quantum science</h1><p class="subtitle">A place for learning and inquiry into quantum theory, computation, and information. Courses and research notes connect foundational ideas, mathematical reasoning, and open questions.</p><figure class="hero-visual"><svg viewBox="0 0 360 360" role="img" aria-labelledby="hero-sphere-title"><title id="hero-sphere-title">A qubit state on a Bloch sphere</title><defs><radialGradient id="sphere-glow"><stop stop-color="currentColor" stop-opacity=".12"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></radialGradient></defs><circle cx="180" cy="180" r="178" fill="url(#sphere-glow)"/><g class="sphere-grid" fill="none" stroke="currentColor"><circle cx="180" cy="180" r="120"/><ellipse cx="180" cy="180" rx="120" ry="38"/><ellipse cx="180" cy="180" rx="44" ry="120"/><path d="M35 180H325M180 35V325M88 268L272 92"/></g><g class="sphere-state"><path d="M180 180L250 101"/><path d="M239 104L250 101L248 113"/><circle cx="250" cy="101" r="5"/></g><g class="sphere-labels"><text x="177" y="25">z</text><text x="331" y="185">y</text><text x="75" y="285">x</text><text x="262" y="98">|ψ⟩</text></g></svg><figcaption>The geometry of a qubit</figcaption><button type="button" data-motion hidden>Pause motion</button></figure><div class="landing-actions"><a class="primary-link" href="education/index.html">Explore courses →</a><a href="research/index.html">Read research notes →</a></div></header><div class="landing-paths"><section id="education"><p class="kicker">Education</p><h2>Courses in quantum science</h2><p>The courses develop concepts through explanations, mathematical examples, and interactive experiments. Quantum Computing begins with classical logic and proceeds through quantum states, circuits, and algorithms.</p><a href="education/index.html">Browse courses →</a></section><section id="research"><p class="kicker">Research</p><h2>Topics and open questions</h2><p>Explore questions in the foundations of quantum mechanics, quantum computation, quantum information, and quantum technology. Follow the mathematics from known results to a next investigation.</p><a href="research/index.html">Explore research →</a></section></div><section class="landing-literature" id="references"><div><p class="kicker">References</p><h2>Papers and further reading</h2><p>The bibliography collects papers and reviews cited in the research notes, with brief annotations on their relevance.</p></div><a href="references/index.html">Browse the bibliography →</a></section>'''
    home+='<section class="landing-literature" id="news"><div><p class="kicker">Research updates</p><h2>News &amp; articles</h2><p>Explore recent arXiv papers and editor-selected research summaries.</p></div><a href="news/index.html">Browse news &amp; papers →</a></section>'
    render_news(ROOT, page, outputs)
    page('index.html','Home',home,[('welcome','Welcome'),('education','Education'),('research','Research'),('references','References'),('news','News & articles')])
    course_icons=['<circle cx="16" cy="16" r="11"/><ellipse cx="16" cy="16" rx="11" ry="4"/><path d="M16 16L23 7M16 3V29"/>', '<path d="M2 17C7 1 9 1 16 17S25 33 30 17M2 17H30"/>', '<path d="M2 9H30M2 23H30M16 9V23"/><circle cx="16" cy="9" r="2"/><rect x="12" y="19" width="8" height="8"/>', '<path d="M7 7L25 16L7 25Z"/><circle cx="7" cy="7" r="3"/><circle cx="25" cy="16" r="3"/><circle cx="7" cy="25" r="3"/>', '<rect x="8" y="8" width="16" height="16" rx="3"/><path d="M12 2V8M20 2V8M12 24V30M20 24V30M2 12H8M2 20H8M24 12H30M24 20H30"/>']
    course_list=''.join(f'<li class="course-card"><a class="course-link" href="{esc(relative(course["path"], "education/index.html"))}"><span class="course-index" aria-hidden="true"><svg class="course-symbol" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.3">{course_icons[i-1]}</svg>{i:02}</span><div class="course-copy"><h3>{esc(course["title"])}</h3><p>{esc(course.get("summary",course["description"]))}</p></div><span class="course-arrow" aria-hidden="true">↗</span></a><details class="course-requirements"><summary>Prerequisites</summary><p>{esc(course["prerequisite"])}</p></details></li>' for i,course in enumerate(courses,1))
    education='<div class="course-catalog"><header class="title-page"><p class="kicker">Learn at your own pace</p><h1>Courses in quantum science.</h1><p class="subtitle">Explore quantum science through clear explanations, worked examples, and interactive experiments.</p></header><section id="courses" aria-labelledby="courses-heading"><div class="catalog-heading"><h2 id="courses-heading">The courses</h2><span>'+f'{len(courses):02} courses'+'</span></div><ul class="course-list">'+course_list+'</ul><p class="catalog-note">Self-paced textbooks by Mithilesh Kumar. Courses are being developed; each course describes its current scope.</p></section><section class="catalog-learning" id="learning"><p class="kicker">Find your starting point</p><h2>Start with the foundations.<br>Follow what interests you.</h2><p>Begin with Quantum Computing, then explore algorithms, programming, or hardware. Quantum Information offers a self-contained path into states and communication. Open the prerequisites above to find the right fit.</p><a href="../research/index.html">Explore the research handbook <span aria-hidden="true">↗</span></a></section></div>'
    page('education/index.html','Education',education,[('courses','Courses'),('learning','Learning approach')])
    for index,item in enumerate(entries):
        source=path(item)
        is_question=bool(item.get('manuscript'))
        body=breadcrumbs(item)+f'<header class="research-heading"><p class="kicker">{"Research question" if is_question else "Research category"}</p><h1>{esc(item["title"])}</h1><p class="lead">{esc(item["summary"])}</p></header>'
        sections=[]
        descendants=children.get(source,[])
        if is_question:
            manuscript=ROOT/item['manuscript']
            if not manuscript.resolve().is_relative_to((ROOT/'content/research').resolve()):
                raise ValueError('Research manuscript outside content/research')
            body+='<p class="research-reading-note">A worked entry into an open research direction · Sources checked 20 October 2026</p>'+manuscript.read_text()
            sections=[('perspective','The question'),('mathematics','The mathematics'),('known','Known results'),('frontier','The frontier'),('investigation','Next investigation')]
        else:
            body+='<section id="overview"><h2>The field in perspective</h2>'+''.join('<p>'+esc(p)+'</p>' for p in item['paragraphs'])+'</section>'
            sections.append(('overview','Perspective'))
            if descendants:
                body+='<section id="topics"><h2>Fundamental questions</h2>'+keywords(descendants,source)+'</section>'
                sections.append(('topics','Research questions'))
            if item['questions']:
                body+='<section id="questions"><h2>Open problems</h2><ul>'+''.join('<li>'+esc(q)+'</li>' for q in item['questions'])+'</ul></section>'
                sections.append(('questions','Open problems'))
        if item['papers']:
            body+='<section id="references"><h2>Selected references</h2>'+bibliography(item['papers'])+'<p class="reference-note">Years refer to first arXiv submission. Publication details are available in the linked records.</p></section>'
            sections.append(('references','Selected references'))
        parent=item['_parents'][-1] if item['_parents'] else None
        parent_url=path(parent) if parent else 'research/index.html'
        body+='<p class="research-parent"><a href="'+relative(parent_url,source)+'">← Back to '+esc(parent['title'] if parent else 'Research')+'</a></p>'
        page(source,item['title'],body,sections,item,entries[index-1] if index else None,entries[index+1] if index+1<len(entries) else None)
    student_source='research/students/index.html'
    student_body='<nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../index.html">Research</a></li><li><span aria-current="page">Students and Contributions</span></li></ol></nav><header class="title-page"><p class="kicker">Research community</p><h1>Students and Contributions</h1><p class="subtitle">Student projects and contributions across our research areas.</p></header><section id="contributions"><h2>Student contributions</h2>'
    students=json.loads((ROOT/'content/student.json').read_text())['students']
    if not students:
        student_body+='<p>Student profiles and contributions will be added here as projects are documented.</p>'
    def student_url(value):
        url=urlsplit(value)
        if url.scheme not in ('','https','http') or url.netloc and not url.scheme:
            raise ValueError('Unsupported student link: '+value)
        if url.scheme:return esc(value)
        return esc(relative(value,student_source))
    for student in students:
        student_body+='<section class="student-profile"><h3>'+esc(student['name'])+'</h3>'
        if student.get('affiliation'):student_body+='<p class="student-affiliation">'+esc(student['affiliation'])+'</p>'
        student_body+='<ul class="student-contributions">'
        for contribution in student['contributions']:
            title=esc(contribution['title'])
            if contribution.get('topic'):title='<a href="'+student_url(contribution['topic'])+'">'+title+'</a>'
            student_body+='<li><h4>'+title+'</h4>'
            if contribution.get('problem'):
                student_body+='<p><strong>Problem:</strong> '+esc(contribution['problem'])+'</p>'
            student_body+='<p>'+('<strong>Contribution:</strong> ' if contribution.get('problem') else '')+esc(contribution['description'])+'</p>'
            metadata=[contribution.get('period'),contribution.get('status')]
            if any(metadata):student_body+='<p class="contribution-meta">'+esc(' · '.join(x for x in metadata if x))+'</p>'
            if contribution.get('outputs'):
                student_body+='<ul class="contribution-outputs">'+''.join('<li><a href="'+student_url(output['url'])+'">'+esc(output['label'])+'</a></li>' for output in contribution['outputs'])+'</ul>'
            student_body+='</li>'
        student_body+='</ul></section>'
    student_body+='</section><p class="research-parent"><a href="../index.html">← Back to Research</a></p>'
    page(student_source,'Students and Contributions',student_body,[('contributions','Student contributions')])
    used=list(dict.fromkeys(ref for item in entries for ref in item['papers']))
    page('references/index.html','Bibliography','<p class="kicker">Reference material</p><h1>Bibliography</h1><p class="lead">Papers cited in the research handbook.</p><section id="papers"><h2>Research papers and reviews</h2>'+bibliography(used)+'</section>',[('papers','Papers and reviews')])
    followup_pages=[]
    for course in ('algorithms','programming','information','hardware'):
        followup_pages.append(f'education/{course}/index.html')
        followup_pages.extend(f'education/{course}/'+chapter['stem']+'.html' for chapter in json.loads((ROOT/f'education/{course}/chapters.json').read_text()))
    outputs['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+book['url']+'/'+p.removesuffix('index.html')+'</loc></url>' for p in [*[name for name in outputs if name.endswith('.html') and name not in UNLISTED], *followup_pages, 'education/computing/index.html', 'education/computing/glossary.html', 'education/computing/study-guide.html', 'education/computing/revisions.html', *['education/computing/'+chapter[0]+'.html' for chapter in json.loads((ROOT/'education/computing/chapters.json').read_text())]])+'</urlset>\n'
    outputs['robots.txt']='User-agent: *\nAllow: /\nSitemap: '+book['url']+'/sitemap.xml\n'
    for old,target in RESEARCH_REDIRECTS.items():
        if old in outputs or target not in outputs:
            raise ValueError('Invalid research redirect: '+old+' → '+target)
        href=esc(relative(target,old))
        canonical=esc(book['url']+'/'+target.removesuffix('index.html'))
        outputs[old]=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Research page moved | Quantum Research Center</title><meta name="robots" content="noindex"><link rel="canonical" href="{canonical}"><meta http-equiv="refresh" content="0;url={href}"></head><body><main><h1>Research has been reorganized</h1><p>This overview now leads to a related research question. <a href="{href}">Continue to the research page →</a></p></main></body></html>'
    return {name:(version_assets(name,source) if name.endswith('.html') else source) for name,source in outputs.items()}

def version_assets(name,source):
    # Stylesheets and scripts are cached for hours by the CDN and browsers; a content
    # hash in the URL makes each deploy fetch exactly the files its HTML expects.
    def stamp(match):
        attribute,url=match.group(1),match.group(2)
        target=ROOT/os.path.normpath(str(Path(name).parent/url))
        if not target.is_file():return match.group(0)
        return f'{attribute}="{url}?v={hashlib.sha256(target.read_bytes()).hexdigest()[:10]}"'
    return re.sub(r'(href|src)="((?![a-z]+:)[^"?#]+\.(?:css|js))"',stamp,source)

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
    if set(pages)-reached-UNLISTED:raise ValueError('Unreachable pages')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    output=render(json.loads((ROOT/'content/research.json').read_text()));check_output(output)
    for name,source in output.items():
        target=ROOT/name
        if args.check:
            if not target.exists() or target.read_text()!=source:raise ValueError('Stale output: '+name)
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
    for target in orphaned_news_pages(output):
        if args.check:raise ValueError('Withdrawn paper page still present: '+str(target.relative_to(ROOT)))
        remove_page(target)
    print(f"{sum(name.endswith('.html') for name in output)} HTML pages validated; all local links and page reachability pass.")

def orphaned_news_pages(output):
    # Per-paper pages whose paper is no longer approved.
    return [p for p in (ROOT/'news').glob('*/index.html') if str(p.relative_to(ROOT)) not in output]

def remove_page(target):
    target.unlink()
    if not any(target.parent.iterdir()):target.parent.rmdir()
if __name__=='__main__':main()
