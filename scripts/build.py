#!/usr/bin/env python3
"""Build the research handbook using only the Python standard library."""
import argparse
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
from paper_news import load_papers, paper_path, render_news
# Editorial pages and legacy redirects stay out of the public sitemap.
RESEARCH_REDIRECTS = json.loads((Path(__file__).resolve().parents[1]/'content/research-redirects.json').read_text())
UNLISTED = {'news/papers.html', *RESEARCH_REDIRECTS}

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'education'))
from site_navigation import site_navigation
from news_articles import render_editorial, stream_nav
from site_graph import render_site_graph
from site_logo import site_logo  # noqa: E402  (shared with the course builds)
from page_template import fill
TEMPLATES=ROOT/'scripts/templates'
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
    ASSET_DIGESTS.clear()
    papers_by_path={paper_path(paper):paper for paper in load_papers(ROOT)['papers']}
    courses=json.loads((ROOT/'content/courses.json').read_text())
    course_levels=(('basics','Basics'),('advanced','Advanced'))
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
            description=description or 'Selected quantum research papers: problems, results, and transferable methods.'
            canonical=book['url']+'/'+source.removesuffix('index.html')
            kind='article' if re.fullmatch(r'news/papers/(?:[0-9]{4}\.[0-9]+|quant-ph-[0-9]+)/index\.html',source) else 'website'
            review='<a href="papers.html" aria-current="page">Review &amp; approve</a>' if source=='news/papers.html' else ''
            stream='papers' if source=='news/papers/index.html' or source.startswith('news/papers/archive/') else ''
            outputs[source]=fill(TEMPLATES/'news-reader.html.in',dict(TITLE=esc(title),DESCRIPTION=esc(description),CANONICAL=canonical,
                SOCIAL=social_meta(title,description,canonical,kind),ARTICLE_DATA=article_data(book['url'],papers_by_path.get(source),source,title,description),
                ROBOTS='<meta name="robots" content="noindex">' if source in UNLISTED else '',UP=up,MATHJAX=mathjax,LOGO=site_logo('news-brand',up+'index.html'),
                NAVIGATION=site_navigation(source,extra=review),SECTIONS=navigation,STREAM_NAV=stream_nav(source,stream),BODY=body,EMAIL=book['email']))
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
        site_nav=site_navigation(source)
        sidebar_contents = ('<ul class="contents-list">'+''.join(f'<li class="part-label">{label}</li>'+''.join(f'<li class="chapter"><a href="{esc(relative(course["path"], source))}">{esc(course["title"])}</a></li>' for course in courses if course['level']==level) for level,label in course_levels)+'</ul>' if source=='education/index.html' else toc(source,current))
        if source=='index.html':
            sidebar_contents='<ul class="contents-list"><li class="part-label">Explore the site</li><li class="chapter"><a href="education/index.html">Education</a></li><li class="chapter"><a href="research/index.html">Research</a></li></ul>'
        if source.startswith('research/') or source=='references/index.html':
            sidebar_contents+=f'<a class="intro-link" '+('aria-current="page" ' if source=='research/students/index.html' else '')+f'href="{relative("research/students/index.html",source)}">Students and Contributions</a>'
        intro_target='index.html'  if source=='index.html' else ('education/index.html' if source=='education/index.html' else 'research/index.html')
        intro_label='Home' if source=='index.html' else ('Course catalog' if source=='education/index.html' else 'Research introduction')
        toolbar_title='Quantum Research Center' if source=='index.html' else ('Education' if source=='education/index.html' else 'Quantum Research')
        toolbar_link=site_logo('toolbar-logo','index.html') if source=='index.html' else f'<a href="{prefix}{intro_target}">{toolbar_title}</a>'
        landing_nav=site_nav  # Home / Education / Research sit in the top bar on every page
        font_toggle = '' if source in {'education/index.html', 'research/index.html'} else '<button id="font-toggle" type="button" aria-label="Increase text size" aria-pressed="false" hidden>Aa</button>'
        section_home = source in {'education/index.html', 'research/index.html'}
        mathjax=(f'<script defer src="{prefix}education/computing/assets/source/mathjax-config.js"></script><script defer src="{prefix}education/computing/assets/source/vendor/mathjax/tex-svg.js"></script>' if '\\(' in body or '\\[' in body else '')
        outputs[source]=fill(TEMPLATES/'reader.html.in',dict(
            TITLE='Quantum Research Center: quantum science courses, research questions and papers' if source=='index.html' else esc(title)+' | Quantum Research Center',
            DESCRIPTION=esc(description),CANONICAL=canonical,SOCIAL=social_meta(title,description,canonical,'website'),SITE_DATA=site_data(book['url']) if source=='index.html' else '',
            PREFIX=prefix,MATHJAX=mathjax,LOGO=site_logo('book-brand',prefix+'index.html'),EMAIL=book['email'],
            BODY_CLASS=('landing' if source=='index.html' else 'reader')+(' section-home' if section_home else '')+(' research-question' if current and current.get('manuscript') else ''),
            INTRO_CURRENT='aria-current="page"' if source==intro_target else '',INTRO_TARGET=intro_target,INTRO_LABEL=intro_label,SIDEBAR=sidebar_contents,
            OUTER_BODY='' if section_home else '<div class="book-body">',INNER_BODY='<div class="book-body">' if section_home else '',
            TOOLBAR_LINK=toolbar_link,NAVIGATION=landing_nav,FONT_TOGGLE=font_toggle,BODY=body,PAGER=pager,LOCAL=local))
    intro='<header class="title-page research-opening"><p class="kicker">Research</p><h1>Questions at the edge of quantum science</h1><p class="subtitle">Explore the foundations, possibilities, and limits of quantum theory through questions we can make precise.</p></header><section id="introduction"><h2>From understanding to investigation</h2><p>Each question begins with a physical or computational problem, develops a mathematical model, and separates established results from unresolved issues. Follow a worked starting investigation before attempting the proposed extension.</p><p>Start by reproducing a small calculation. Then change an assumption, compare with the literature, and identify what a new result would establish. The proposed extensions describe starting directions for investigation.</p></section><section id="contents-overview"><h2>Explore the four fields</h2><div class="research-categories">'
    for number,category in enumerate(children[None],1):
        intro+='<section class="research-category"><p class="kicker">'+f'{number:02} · {len(children.get(path(category),[]))} questions'+'</p><h3>'+link(category,'research/index.html')+'</h3><p>'+esc(category['summary'])+'</p>'+keywords(children.get(path(category),[]),'research/index.html')+'</section>'
    intro+='</div></section><section id="literature"><h2>Read the argument, then the source</h2><p>Known results link to papers near the claims they support. Each question also has an annotated reading list. Model assumptions and theorem scope matter as much as the equation itself.</p><a href="../references/index.html">Browse the bibliography →</a></section><section id="students"><h2>People and contributions</h2><p>Explore the projects and documented contributions of students working with the Center.</p><a href="students/index.html">Students and contributions →</a></section>'
    page('research/index.html','Quantum Research',intro,[('introduction','How to explore'),('contents-overview','Research questions'),('literature','Sources'),('students','People')])
    render_news(ROOT, page, outputs, book['url'])
    article_dates = render_editorial(ROOT, outputs, book, site_logo, social_meta, json_ld)
    course_icons=['<circle cx="16" cy="16" r="11"/><ellipse cx="16" cy="16" rx="11" ry="4"/><path d="M16 16L23 7M16 3V29"/>', '<path d="M2 17C7 1 9 1 16 17S25 33 30 17M2 17H30"/>', '<path d="M2 9H30M2 23H30M16 9V23"/><circle cx="16" cy="9" r="2"/><rect x="12" y="19" width="8" height="8"/>', '<path d="M7 7L25 16L7 25Z"/><circle cx="7" cy="7" r="3"/><circle cx="25" cy="16" r="3"/><circle cx="7" cy="25" r="3"/>', '<rect x="8" y="8" width="16" height="16" rx="3"/><path d="M12 2V8M20 2V8M12 24V30M20 24V30M2 12H8M2 20H8M24 12H30M24 20H30"/>']
    course_icons=dict(zip(('education/computing/index.html','education/algorithms/index.html','education/programming/index.html','education/information/index.html','education/hardware/index.html'),course_icons))
    course_icons['education/foundations/index.html']='<circle cx="16" cy="16" r="3"/><ellipse cx="16" cy="16" rx="13" ry="5"/><ellipse cx="16" cy="16" rx="13" ry="5" transform="rotate(60 16 16)"/><ellipse cx="16" cy="16" rx="13" ry="5" transform="rotate(120 16 16)"/>'
    course_list=''
    offset=0
    for level,label in course_levels:
        group=[course for course in courses if course['level']==level]
        cards=''.join(f'<li class="course-card"><a class="course-link" href="{esc(relative(course["path"], "education/index.html"))}"><span class="course-index" aria-hidden="true"><svg class="course-symbol" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.3">{course_icons.get(course["path"], course_icons["education/foundations/index.html"])}</svg>{i:02}</span><div class="course-copy"><h3>{esc(course["title"])}</h3><p>{esc(course.get("summary",course["description"]))}</p></div><span class="course-arrow" aria-hidden="true">↗</span></a><details class="course-requirements"><summary>Prerequisites</summary><p>{esc(course["prerequisite"])}</p></details></li>' for i,course in enumerate(group,offset+1))
        course_list+=f'<section class="catalog-group" id="{level}" aria-labelledby="{level}-heading"><div class="catalog-separator"><h2 id="{level}-heading">{label}</h2><span>{len(group)} course{"" if len(group)==1 else "s"}</span></div><ul class="course-list">'+cards+'</ul></section>'
        offset+=len(group)
    education='<div class="course-catalog"><header class="title-page"><p class="kicker">Learn at your own pace</p><h1>Courses in quantum science.</h1><p class="subtitle">Explore quantum science through clear explanations, worked examples, and interactive experiments.</p></header><section id="courses" aria-labelledby="courses-heading"><div class="catalog-heading"><h2 id="courses-heading">The courses</h2><span>'+f'{len(courses):02} courses'+'</span></div>'+course_list+'<p class="catalog-note">Self-paced textbooks by Mithilesh Kumar. Courses are being developed; each course describes its current scope.</p></section><section class="catalog-learning" id="learning"><p class="kicker">Find your starting point</p><h2>Start with the foundations.<br>Follow what interests you.</h2><p>The Basics courses cover quantum computing, algorithms, programming, information, and hardware. The advanced sequence begins with Quantum Foundations, continues with Quantum Information Theory, and develops reliable computation in Quantum Error Correction. Interpretations of Quantum Mechanics offers a parallel advanced path from Quantum Foundations into measurement, reality, and quantum observers. Quantum Experiments is another advanced course, connecting laboratory and thought experiments through interactive models and evidence. Open the prerequisites above to find the right fit.</p><a href="../research/index.html">Explore the research handbook <span aria-hidden="true">↗</span></a></section></div>'
    page('education/index.html','Education',education,[('basics','Basics'),('advanced','Advanced'),('learning','Learning approach')])
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
            body+='<p class="research-reading-note">A worked entry into an open research direction · Sources checked '+item.get('reviewed','20 October 2026')+'</p>'+manuscript.read_text()
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
    # One public-page inventory drives both maps, including standalone and nested pages.
    graph = render_site_graph(ROOT, outputs, book['url'], site_logo, site_navigation)
    listed = [node['id'] for node in graph['nodes'] if node['id'] not in UNLISTED]
    approved={name:paper['approved_on'] for name,paper in papers_by_path.items() if paper.get('approved_on')}
    approved.update(article_dates)
    outputs['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+book['url']+'/'+p.removesuffix('index.html')+'</loc>'+(f'<lastmod>{approved[p]}</lastmod>' if p in approved else '')+'</url>' for p in dict.fromkeys(listed))+'</urlset>\n'
    # Chapter fragments under content/ are build inputs, not pages.
    outputs['robots.txt']='User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /education/*/content/\nSitemap: '+book['url']+'/sitemap.xml\n'
    for old,target in RESEARCH_REDIRECTS.items():
        if old in outputs or target not in outputs:
            raise ValueError('Invalid research redirect: '+old+' → '+target)
        href=esc(relative(target,old))
        canonical=esc(book['url']+'/'+target.removesuffix('index.html'))
        outputs[old]=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Research page moved | Quantum Research Center</title><meta name="robots" content="noindex"><link rel="canonical" href="{canonical}"><meta http-equiv="refresh" content="0;url={href}"></head><body><main><h1>Research has been reorganized</h1><p>This overview now leads to a related research question. <a href="{href}">Continue to the research page →</a></p></main></body></html>'
    return {name:(mark_generated(version_assets(name,source)) if name.endswith('.html') else source) for name,source in outputs.items()}

def interference_hero(phi=0.4):
    # The landing figure: two-path interference drawn as a transition diagram, as in the book.
    # 0 --H--> (0,1) --phase on 1--> --H--> outputs. hero.js redraws the dynamic parts as phi moves;
    # this static drawing (phi in units of pi) is what readers without JavaScript see.
    import math
    X,Y,R=(44,102,160,218),(96,204),13
    a=math.pi*phi
    def arrow(x1,y1,x2,y2,cls,amp):
        dx,dy=x2-x1,y2-y1;n=math.hypot(dx,dy);ux,uy=dx/n,dy/n
        return f'<line class="{cls}" x1="{x1+ux*(R+3):.1f}" y1="{y1+uy*(R+3):.1f}" x2="{x2-ux*(R+5):.1f}" y2="{y2-uy*(R+5):.1f}" stroke-width="{1+3.2*amp:.2f}" marker-end="url(#hx-head-{cls[3:]})"/>'
    def node(x,y,prob,ident=''):
        return f'<circle class="hx-node" cx="{x}" cy="{y}" r="{R}"/><circle class="hx-fill"{ident} cx="{x}" cy="{y}" r="{R*math.sqrt(prob):.2f}"/>'
    def dial(k):
        cx,cy=304,Y[k];theta=a+math.pi*k
        bx,by=cx+19,cy;vx,vy=bx+19*math.cos(theta),by-19*math.sin(theta);prob=((vx-cx)**2+(vy-cy)**2)/1444
        return (f'<circle class="hx-unit" cx="{cx}" cy="{cy}" r="38"/><line class="hx-blue" id="hx-b{k}" x1="{cx}" y1="{cy}" x2="{bx}" y2="{by}"/>'
                f'<line class="hx-violet" id="hx-v{k}" x1="{bx}" y1="{by}" x2="{vx:.2f}" y2="{vy:.2f}"/><line class="hx-sum" id="hx-r{k}" x1="{cx}" y1="{cy}" x2="{vx:.2f}" y2="{vy:.2f}"/>'
                f'<circle class="hx-tip" id="hx-t{k}" cx="{vx:.2f}" cy="{vy:.2f}" r="3"/><text class="hx-prob" id="hx-p{k}" x="{cx}" y="{cy+54}">P = {prob:.2f}</text>')
    p0=math.cos(a/2)**2
    s=1/math.sqrt(2)
    svg=('<svg viewBox="0 0 360 276" role="img" aria-labelledby="hx-title hx-desc"><title id="hx-title">Two paths interfering</title>'
         f'<desc id="hx-desc">The computation starts in configuration 0. A Hadamard step splits it into 0 and 1, the path through 1 gains a phase, and a second Hadamard step recombines them. Each outcome receives one arrow from each path; its probability is the squared length of their sum. At phase {phi:.2f} pi the probability of 0 is {p0:.2f}.</desc>'
         '<defs>'+''.join(f'<marker id="hx-head-{c}" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto"><path class="hx-{c}-head" d="M0 0L8 4L0 8z"/></marker>' for c in ('blue','violet'))+'</defs>'
         '<g class="hx-labels"><text x="8" y="'+str(Y[0]+5)+'">|0⟩</text><text x="8" y="'+str(Y[1]+5)+'">|1⟩</text>'
         f'<text class="hx-step" x="{(X[0]+X[1])/2:.0f}" y="262">H</text><text class="hx-step" x="{(X[1]+X[2])/2:.0f}" y="262">phase φ</text><text class="hx-step" x="{(X[2]+X[3])/2:.0f}" y="262">H</text><text class="hx-step" x="304" y="44">sum of paths</text></g>'
         +arrow(X[0],Y[0],X[1],Y[0],'hx-blue',s)+arrow(X[0],Y[0],X[1],Y[1],'hx-violet',s)
         +arrow(X[1],Y[0],X[2],Y[0],'hx-blue',s)+arrow(X[1],Y[1],X[2],Y[1],'hx-violet',s)
         +arrow(X[2],Y[0],X[3],Y[0],'hx-blue',.5)+arrow(X[2],Y[0],X[3],Y[1],'hx-blue',.5)+arrow(X[2],Y[1],X[3],Y[0],'hx-violet',.5)+arrow(X[2],Y[1],X[3],Y[1],'hx-violet',.5)
         +f'<g class="hx-phase"><circle cx="{(X[1]+X[2])/2}" cy="{Y[1]-22}" r="9"/><line id="hx-hand" x1="{(X[1]+X[2])/2}" y1="{Y[1]-22}" x2="{(X[1]+X[2])/2+8*math.cos(a):.2f}" y2="{Y[1]-22-8*math.sin(a):.2f}"/></g>'
         +node(X[0],Y[0],1)+node(X[0],Y[1],0)+node(X[1],Y[0],.5)+node(X[1],Y[1],.5)+node(X[2],Y[0],.5)+node(X[2],Y[1],.5)
         +node(X[3],Y[0],p0,' id="hx-o0"')+node(X[3],Y[1],1-p0,' id="hx-o1"')+dial(0)+dial(1)+'</svg>')
    return (f'<figure class="hero-visual interference-hero">{svg}<div class="hx-control"><label for="hx-phase">Phase φ</label>'
            f'<input id="hx-phase" type="range" min="0" max="200" step="1" value="{round(phi*100)}"><output id="hx-value" for="hx-phase">{phi:.2f}π</output></div>'
            '<figcaption>Two paths, one outcome</figcaption><button type="button" data-motion hidden>Pause motion</button></figure><script defer src="hero.js"></script>')

def json_ld(data):
    # Structured data for search engines; '</' is escaped so the JSON cannot close the script element.
    return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'</script>'

def site_data(url):
    return json_ld({'@context':'https://schema.org','@type':'WebSite','name':'Quantum Research Center','url':url+'/',
        'description':'Courses, research questions and selected papers in quantum science and quantum computing.',
        'publisher':{'@type':'Organization','name':'Quantum Research Center','url':url+'/','logo':url+'/icons/icon.svg'}})

def article_data(url,paper,source,title,description):
    # A news page summarizes one arXiv paper; the paper itself is cited, not claimed.
    if not paper: return ''
    data={'@context':'https://schema.org','@type':'Article','headline':title[:110],'description':re.sub(r'\\[()\[\]]','',description or ''),
        'url':url+'/'+source.removesuffix('index.html'),'datePublished':paper.get('approved_on'),'inLanguage':'en',
        'publisher':{'@type':'Organization','name':'Quantum Research Center','url':url+'/'},
        'citation':{'@type':'ScholarlyArticle','name':paper['title'],'url':'https://arxiv.org/abs/'+paper['id'],
            'author':[{'@type':'Person','name':name.strip()} for name in paper['authors'].split(';')]}}
    return json_ld({k:v for k,v in data.items() if v})

def social_meta(title,description,url,kind):
    # Link previews (Open Graph / Twitter); TeX delimiters read badly in a preview card.
    text=re.sub(r'\\[()\[\]]','',description)
    return (f'<meta property="og:type" content="{kind}"><meta property="og:site_name" content="Quantum Research Center">'
        f'<meta property="og:title" content="{esc('Quantum Research Center' if title=='Home' else title+' | Quantum Research Center')}"><meta property="og:description" content="{esc(text)}">'
        f'<meta property="og:url" content="{esc(url)}"><meta name="twitter:card" content="summary">')

GENERATED_NOTE='<!-- Generated by scripts/build.py from content/*.json. Edit those sources and rebuild; changes made here are overwritten. -->'
def mark_generated(source):
    head,sep,rest=source.partition('>')
    return head+sep+GENERATED_NOTE+rest if head.lower().startswith('<!doctype') else GENERATED_NOTE+source

ASSET_DIGESTS={}
def asset_digest(target):
    if target not in ASSET_DIGESTS:ASSET_DIGESTS[target]=hashlib.sha256(target.read_bytes()).hexdigest()[:10]
    return ASSET_DIGESTS[target]

def version_assets(name,source):
    # Stylesheets and scripts are cached for hours by the CDN and browsers; a content
    # hash in the URL makes each deploy fetch exactly the files its HTML expects.
    def stamp(match):
        attribute,url=match.group(1),match.group(2)
        target=ROOT/os.path.normpath(str(Path(name).parent/url))
        if not target.is_file():return match.group(0)
        return f'{attribute}="{url}?v={asset_digest(target)}"'
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

# Fingerprints of the files this build last wrote, so hand edits to generated pages are noticed
# instead of silently overwritten. Local only (gitignored); a missing manifest disables the guard once.
MANIFEST=ROOT/'scripts/.generated-manifest.json'
def fingerprint(text):return hashlib.sha256(text.encode()).hexdigest()
def hand_edited(output):
    known=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    edited=[]
    for name,source in output.items():
        target=ROOT/name
        if name in known and target.exists():
            current=target.read_text()
            if current!=source and fingerprint(current)!=known[name]:edited.append(name)
    return edited
def record_generated(output,names=None):
    known=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    known.update({name:fingerprint(output[name]) for name in (names or output)})
    known={name:value for name,value in known.items() if name in output}
    MANIFEST.write_text(json.dumps(known,indent=0,sort_keys=True)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true')
    parser.add_argument('--force',action='store_true',help='overwrite generated pages even if they were edited by hand')
    args=parser.parse_args()
    output=render(json.loads((ROOT/'content/research.json').read_text()));check_output(output)
    if not args.check and not args.force:
        edited=hand_edited(output)
        if edited:
            raise SystemExit('These generated pages were edited by hand since the last build:\n  '+'\n  '.join(edited)+
                '\nMove the changes into content/*.json (or scripts/build.py), then rebuild; or rerun with --force to discard them.')
    for name,source in output.items():
        target=ROOT/name
        if args.check:
            if not target.exists() or target.read_text()!=source:raise ValueError('Stale output: '+name)
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
    if not args.check:record_generated(output)
    for target in orphaned_news_pages(output):
        if args.check:raise ValueError('Withdrawn paper page still present: '+str(target.relative_to(ROOT)))
        remove_page(target)
    print(f"{sum(name.endswith('.html') for name in output)} HTML pages validated; all local links and page reachability pass.")

def orphaned_news_pages(output):
    # Only managed article/paper pages can be withdrawn; never remove hand-authored sections.
    candidates = [p for pattern in ('*/index.html', 'papers/*/index.html') for p in (ROOT/'news').glob(pattern)
                  if re.fullmatch(r'(?:[0-9]{4}\.[0-9]{4,5}|quant-ph-[0-9]{7})', p.parent.name)]
    candidates.extend((ROOT/'news/articles').glob('*/index.html'))
    candidates.extend((ROOT/'news/papers/archive').glob('*/index.html'))
    return [p for p in candidates if str(p.relative_to(ROOT)) not in output
            and GENERATED_NOTE in p.read_text()]

def remove_page(target):
    target.unlink()
    if not any(target.parent.iterdir()):target.parent.rmdir()
if __name__=='__main__':main()
