"""Public-facing articles and the news-led home. Standard-library-only static publishing."""
import html
import json
import os
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from paper_news import long_date, paper_path, plain
from site_navigation import site_navigation

TOPICS = {'discoveries': 'Discoveries', 'companies': 'Companies',
          'government': 'Government & Policy', 'projects': 'Projects & Infrastructure'}
FORMATS = ('News', 'Explainer', 'Interview', 'Opinion')
SLUG = r'[a-z0-9]+(?:-[a-z0-9]+)*'


def esc(value):
    return html.escape(str(value), quote=True)


def relative(target, source):
    return os.path.relpath(target, Path(source).parent).replace(os.sep, '/')


def article_path(article):
    return 'news/articles/' + article['slug'] + '/index.html'


def load_articles(root):
    articles = []
    for file in sorted((root / 'content/news-articles').glob('*.json')):
        article = json.loads(file.read_text())
        if article.get('slug') != file.stem:
            raise ValueError('Article slug must match filename: ' + file.name)
        articles.append(article)
    return articles


def validate(articles, config, papers):
    seen = set()
    for article in articles:
        slug = article.get('slug', '')
        if not re.fullmatch(SLUG, slug) or slug in seen:
            raise ValueError('Invalid or duplicate article slug: ' + slug)
        seen.add(slug)
        if article.get('status') not in ('draft', 'published'):
            raise ValueError('Invalid article status: ' + slug)
        for key in ('title', 'summary', 'author'):
            if not isinstance(article.get(key), str) or not article[key].strip():
                raise ValueError('Missing article field: ' + key)
        if article.get('topic') not in TOPICS or article.get('format') not in FORMATS:
            raise ValueError('Invalid article topic/format: ' + slug)
        published = date.fromisoformat(article['published'])
        if date.fromisoformat(article.get('updated', article['published'])) < published:
            raise ValueError('Article update precedes publication: ' + slug)
        sections = article.get('sections')
        if not isinstance(sections, list) or not sections:
            raise ValueError('Article needs sections: ' + slug)
        for section in sections:
            if not section.get('heading') or not isinstance(section.get('paragraphs'), list) or not section['paragraphs'] or any(not isinstance(p, str) or not p.strip() for p in section['paragraphs']):
                raise ValueError('Article sections need headings and paragraphs: ' + slug)
        sources = article.get('sources')
        if not isinstance(sources, list) or not sources:
            raise ValueError('Article needs sources: ' + slug)
        for source in sources:
            url = urlsplit(source.get('url', ''))
            if not source.get('title') or url.scheme not in ('https', 'http') or not url.netloc:
                raise ValueError('Invalid article source: ' + slug)
        for section in sections:
            figure = section.get('figure')
            if figure is not None and (not isinstance(figure, dict) or not re.fullmatch(r'[a-z0-9-]+\.svg', figure.get('file', ''))
                                       or any(not isinstance(figure.get(k), str) or not figure[k].strip() for k in ('caption', 'alt'))):
                raise ValueError('Article figures need an SVG file name, caption and alt text: ' + slug)
        for section in sections:
            refs = section.get('source_refs', [])
            if not isinstance(refs, list) or any(type(ref) is not int or not 1 <= ref <= len(sources) for ref in refs):
                raise ValueError('Invalid section source reference: ' + slug)
        for field in ('related_articles', 'related_papers'):
            if not isinstance(article.get(field, []), list) or any(not isinstance(x, str) for x in article.get(field, [])):
                raise ValueError('Invalid related links: ' + slug)
    public = {a['slug'] for a in articles if a['status'] == 'published'}
    approved = {p['id'] for p in papers if p['status'] == 'approved'}
    if config.get('featured') and config['featured'] not in public:
        raise ValueError('Featured article must be published')
    for article in articles:
        if article['status'] != 'published':
            continue
        if set(article.get('related_articles', [])) - public:
            raise ValueError('Related article is missing or unpublished: ' + article['slug'])
        if set(article.get('related_papers', [])) - approved:
            raise ValueError('Related paper is missing or unapproved: ' + article['slug'])


def figure_html(root, slug, figure):
    # Figures are inlined so their marks can use the page's theme variables.
    svg = (root / 'content/news-articles/figures' / slug / figure['file']).read_text()
    svg = re.sub(r'^\s*<\?xml[^>]*>\s*', '', svg)
    if not svg.startswith('<svg') or re.search(r'<script|\son\w+=|\sid=', svg):
        raise ValueError('Article figure must be a plain SVG without scripts, handlers or ids: ' + figure['file'])
    svg = svg.replace('<svg', f'<svg role="img" aria-label="{esc(figure["alt"])}"', 1)
    return f'<figure class="article-figure"><div class="figure-scroll">{svg}</div><figcaption>{esc(figure["caption"])}</figcaption></figure>'


def metadata(article):
    words = sum(len(p.split()) for s in article['sections'] for p in s['paragraphs'])
    minutes = max(1, (words + 199) // 200)
    return f'<time datetime="{article["published"]}">{long_date(article["published"])}</time><span>{minutes} min read</span>'


def card(article, source, featured=False):
    url = relative(article_path(article), source)
    cls = 'lead-story' if featured else 'story-card'
    heading = 'h2' if featured else 'h3'
    return (f'<article class="{cls}" data-article data-topic="{article["topic"]}" data-format="{article["format"]}">'
            f'<p class="story-label">{esc(TOPICS[article["topic"]])}<span> / </span>{esc(article["format"])}</p>'
            f'<{heading}><a href="{url}">{esc(article["title"])}</a></{heading}>'
            f'<p class="story-summary">{esc(article["summary"])}</p>'
            f'<p class="story-meta">{metadata(article)}</p>'
            + (f'<a class="story-read" href="{url}">Read the story <span aria-hidden="true">↗</span></a>' if featured else '') + '</article>')


def signal_art():
    # Original, decorative SVG: a quiet visual echo of the interference-bar identity.
    bars = ''.join(f'<line x1="{x}" y1="{180-h}" x2="{x}" y2="{180+h}" stroke-width="{3 if i % 2 else 5}" opacity="{.25 + .7*(1-abs(i-12)/12):.2f}"/>'
                   for i in range(25) for x, h in [(36 + i * 12, 18 + 105 * (1 - abs(i - 12) / 12) ** 2)])
    return '<div class="signal-art" aria-hidden="true"><svg viewBox="0 0 360 360" fill="none"><circle cx="180" cy="180" r="154"/><circle cx="180" cy="180" r="115"/><path d="M0 180h360M180 0v360"/><g class="signal-bars">'+bars+'</g></svg><span>QUANTUM / IN PERSPECTIVE</span></div>'


def stream_nav(source, active=''):
    return '<nav class="stream-nav" aria-label="News streams">' + ''.join(
        f'<a href="{relative(path, source)}"'+(' aria-current="page"' if key == active else '')+f'>{label}</a>'
        for key, path, label in [('all', 'news/index.html', 'Overview'), ('articles', 'news/articles/index.html', 'Quantum News'), ('papers', 'news/papers/index.html', 'Research Papers')]) + '</nav>'


def paper_preview(papers, source):
    items = ''.join(f'<li><p class="story-label">Research paper · Selected {long_date(p["approved_on"])}</p><h3><a href="{relative(paper_path(p), source)}">{esc(p["title"])}</a></h3><p>{esc(plain(p["problem"]))}</p></li>' for p in papers[:3])
    return '<section class="paper-digest" aria-labelledby="papers-heading"><div class="section-top"><div><p class="eyebrow">Go deeper</p><h2 id="papers-heading">Latest research papers</h2></div><a href="'+relative('news/papers/index.html', source)+'">Browse research papers ↗</a></div><p class="section-intro">Technical summaries, methods, and limitations for researchers and advanced readers.</p><ol>'+items+'</ol>'+('' if items else '<p>No research papers have been selected yet.</p>')+'</section>'


def render_editorial(root, outputs, book, site_logo, social_meta, json_ld):
    articles = load_articles(root)
    config = json.loads((root / 'content/news.json').read_text())
    papers = json.loads((root / 'content/papers.json').read_text())['papers']
    validate(articles, config, papers)
    published = sorted((a for a in articles if a['status'] == 'published'), key=lambda a: (a['published'], a['slug']), reverse=True)
    approved = sorted((p for p in papers if p['status'] == 'approved'), key=lambda p: (p['approved_on'], p['submitted']), reverse=True)
    featured = next((a for a in published if a['slug'] == config.get('featured')), published[0] if published else None)
    site_url = book['url']

    def shell(source, title, description, body, article=None):
        up = '../' * source.count('/')
        canonical = site_url + '/' + source.removesuffix('index.html')
        structured = {'@context': 'https://schema.org', '@type': 'WebSite' if source == 'index.html' else 'CollectionPage', 'name': title, 'url': canonical, 'description': description}
        if article:
            structured.update({'@type': 'NewsArticle' if article['format'] == 'News' else 'Article', 'headline': title, 'datePublished': article['published'], 'dateModified': article.get('updated', article['published']), 'author': {'@type': 'Organization' if article['author'] == 'Quantum Research Center' else 'Person', 'name': article['author']}, 'publisher': {'@type': 'Organization', 'name': 'Quantum Research Center'}, 'citation': [s['url'] for s in article['sources']]})
        nav = site_navigation(source, 'editorial-nav')
        # Article text may contain TeX (\(...\) inline, \[...\] displayed); load MathJax only where it is used.
        mathjax = (f'<script defer src="{up}education/computing/assets/source/mathjax-config.js"></script>'
                   f'<script defer src="{up}education/computing/assets/source/vendor/mathjax/tex-svg.js"></script>') if '\\(' in body or '\\[' in body else ''
        outputs[source] = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Quantum Research Center</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}">{social_meta(title, description, canonical, 'article' if article else 'website')}{json_ld(structured)}<link rel="icon" href="{up}icons/icon.svg"><link rel="alternate" type="application/rss+xml" title="Quantum News" href="{up}news/articles/feed.xml"><link rel="alternate" type="application/rss+xml" title="Research Papers" href="{up}news/feed.xml"><script src="{up}education/computing/assets/theme.js"></script><script src="{up}navigation.js"></script><link rel="stylesheet" href="{up}styles.css"><link rel="stylesheet" href="{up}news/editorial.css"><script defer src="{up}news/articles.js"></script>{mathjax}</head>
<body class="editorial"><a class="skip-link" href="#main">Skip to content</a><header class="toolbar editorial-header">{site_logo('editorial-brand',up+'index.html')}{nav}</header><main id="main" tabindex="-1" class="editorial-main">{body}</main><footer class="editorial-footer"><div><strong>Quantum Research Center</strong><p>News, learning, and inquiry into quantum science.</p></div><nav aria-label="Footer"><a href="{up}news/articles/feed.xml">Quantum News RSS</a><a href="{up}news/feed.xml">Research Papers RSS</a><a href="{up}references/index.html">Bibliography</a><a href="mailto:{book['email']}">Contact</a></nav></footer></body></html>'''

    for source in ('index.html', 'news/index.html'):
        home = source == 'index.html'
        body = '<header class="editorial-intro"><p class="eyebrow">Quantum Research Center / '+('The wider picture' if home else 'News desk')+'</p><h1>'+('Quantum science.<br><span>In perspective.</span>' if home else 'Follow the quantum world.')+'</h1><p>Discoveries, people, and projects shaping quantum technology. Clear explanations, with a path to the research behind them.</p></header>'
        body += stream_nav(source, '' if home else 'all')
        if featured:
            body += '<section class="feature" aria-label="Featured story">'+card(featured, source, True)+signal_art()+'</section>'
        else:
            body += '<section class="empty-news"><h2>Quantum News</h2><p>Our first stories are on the way. Explore the research papers and courses below.</p></section>'
        recent = [a for a in published if a != featured][:6]
        body += '<section class="latest-stories"><div class="section-top"><div><p class="eyebrow">For curious minds</p><h2>News &amp; explainers</h2></div><a href="'+relative('news/articles/index.html', source)+'">All Quantum News ↗</a></div><div class="story-grid">'+''.join(card(a, source) for a in recent)+'</div></section>'
        body += '<section class="explore-paths" aria-label="Explore quantum science"><div><p class="eyebrow">Build your understanding</p><h2>Start with a question.<br>Follow it further.</h2></div><a href="'+relative('education/index.html', source)+'"><span>01 / Education</span><strong>Learn the foundations ↗</strong><p>Courses, worked examples, and interactive experiments.</p></a><a href="'+relative('research/index.html', source)+'"><span>02 / Research</span><strong>Explore open questions ↗</strong><p>Follow the ideas and mathematics behind our research.</p></a></section>'
        body += paper_preview(approved, source)
        shell(source, 'Quantum science, news & ideas' if home else 'News', 'Accessible quantum news and explainers, alongside technical research papers, courses, and open questions.', body)

    source = 'news/articles/index.html'
    body = '<header class="editorial-intro compact"><p class="eyebrow">For curious minds</p><h1>Quantum News</h1><p>Progress in quantum science, explained. Explore discoveries, companies, public programmes, and the ideas behind the headlines.</p></header>'+stream_nav(source, 'articles')
    body += '<section class="article-filters" aria-label="Filter articles" hidden><label>Search articles<input id="article-search" type="search" placeholder="Search headlines and summaries…"></label><label>Topic<select id="article-topic"><option value="all">All topics</option>'+''.join(f'<option value="{key}">{esc(label)}</option>' for key, label in TOPICS.items())+'</select></label><label>Format<select id="article-format"><option value="all">All formats</option>'+''.join(f'<option>{label}</option>' for label in FORMATS)+'</select></label><p id="article-count" role="status"></p></section>'
    body += '<section aria-label="Articles" class="story-grid article-list">'+''.join(card(a, source) for a in published)+'</section>'
    if not published:
        body += '<p>Our first stories are on the way. <a href="../papers/index.html">Explore research papers →</a></p>'
    shell(source, 'Quantum News', 'Quantum discoveries, companies, government programmes, and explainers for curious readers.', body)

    by_slug = {a['slug']: a for a in published}
    by_id = {p['id']: p for p in approved}
    for article in published:
        source = article_path(article)
        body = '<article class="general-article"><nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../../index.html">News</a></li><li><a href="../index.html">Quantum News</a></li></ol></nav>'
        body += f'<header><p class="story-label">{esc(TOPICS[article["topic"]])} / {article["format"]}</p><h1>{esc(article["title"])}</h1><p class="article-deck">{esc(article["summary"])}</p><p class="story-meta"><span>By {esc(article["author"])}</span>{metadata(article)}</p>'
        if article.get('updated') and article['updated'] != article['published']:
            body += f'<p class="story-meta">Updated <time datetime="{article["updated"]}">{long_date(article["updated"])}</time></p>'
        if article['format'] == 'Explainer':
            body += '<p class="article-context">Background reading · An introduction to the ideas behind the news.</p>'
        body += '</header><div class="article-prose">'
        for i, section in enumerate(article['sections'], 1):
            body += f'<section id="section-{i}"><h2>{esc(section["heading"])}</h2>'+''.join('<p>'+esc(p)+'</p>' for p in section['paragraphs'])
            if section.get('figure'):
                body += figure_html(root, article['slug'], section['figure'])
            if section.get('source_refs'):
                body += '<p class="section-sources">Sources: '+', '.join(f'<a href="#source-{ref}" aria-label="Source {ref}: {esc(article["sources"][ref-1]["title"])}">[{ref}]</a>' for ref in section['source_refs'])+'</p>'
            body += '</section>'
        body += '<section class="article-sources"><h2>Sources &amp; further reading</h2><ol>'+''.join(f'<li id="source-{ref}"><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></li>' for ref, s in enumerate(article['sources'], 1))+'</ol></section>'
        if article.get('related_papers'):
            body += '<section><h2>Read the research analysis</h2><ul>'+''.join(f'<li><a href="{relative(paper_path(by_id[pid]), source)}">{esc(by_id[pid]["title"])}</a></li>' for pid in article['related_papers'])+'</ul></section>'
        body += '</div></article>'
        if article.get('related_articles'):
            body += '<section class="related-stories"><h2>Keep exploring</h2><div class="story-grid">'+''.join(card(by_slug[slug], source) for slug in article['related_articles'])+'</div></section>'
        shell(source, article['title'], article['summary'], body, article)

    # Reciprocal links appear only for deliberately associated, published articles.
    for paper in approved:
        related = [a for a in published if paper['id'] in a.get('related_papers', [])]
        source = paper_path(paper)
        if related:
            links = '<section class="editorial-note"><h2>Read the accessible explanation</h2>'+''.join(f'<p><a href="{relative(article_path(a), source)}">{esc(a["title"])}</a></p>' for a in related)+'</section>'
            outputs[source] = outputs[source].replace('<nav class="paper-pager"', links+'<nav class="paper-pager"', 1)

    items = ''
    for article in published[:30]:
        url = site_url + '/' + article_path(article).removesuffix('index.html')
        stamp = date.fromisoformat(article['published'])
        items += f'<item><title>{esc(article["title"])}</title><link>{url}</link><guid isPermaLink="true">{url}</guid><pubDate>{stamp:%a, %d %b %Y} 00:00:00 +0530</pubDate><category>{esc(TOPICS[article["topic"]])}</category><description>{esc(article["summary"])}</description></item>'
    outputs['news/articles/feed.xml'] = f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Quantum News | Quantum Research Center</title><link>{site_url}/news/articles/</link><description>Quantum news and explainers for curious readers.</description><language>en</language><atom:link href="{site_url}/news/articles/feed.xml" rel="self" type="application/rss+xml"/>{items}</channel></rss>\n'
    return {article_path(a): a.get('updated', a['published']) for a in published}
