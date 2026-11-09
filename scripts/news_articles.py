"""Public-facing articles and the news-led home. Standard-library-only static publishing."""
import html
import json
import os
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from homepage import opening as homepage_opening
from conferences import render_conferences
from companies import render_companies
from paper_news import load_papers, long_date, paper_path, plain
from site_navigation import site_navigation
from tools import render_tools
from ai_problem_claims import render_claims_home, render_claims_page

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
        strings = lambda xs: isinstance(xs, list) and all(isinstance(x, str) and x.strip() for x in xs)
        for section in sections:
            if 'kicker' in section and (not isinstance(section['kicker'], str) or not section['kicker'].strip()):
                raise ValueError('Section kicker must be plain text: ' + slug)
            if 'card' in section and section['card'] is not True:
                raise ValueError('Section card must be true when present: ' + slug)
            if 'asks' in section and (not strings(section['asks']) or not section['asks']):
                raise ValueError('Section asks must be a nonempty list of strings: ' + slug)
            stats = section.get('stats')
            if stats is not None and (not isinstance(stats, list) or not 1 <= len(stats) <= 4
                                      or any(not isinstance(x, dict) or not strings([x.get('value'), x.get('label')]) for x in stats)):
                raise ValueError('Section stats need one to four items with a value and a label: ' + slug)
            table = section.get('table')
            if table is not None and (not isinstance(table, dict) or not strings(table.get('columns')) or not table.get('rows')
                                      or any(not strings(r) or len(r) != len(table['columns']) for r in table['rows'])
                                      or ('caption' in table and not strings([table['caption']]))):
                raise ValueError('Section tables need columns and rows of matching length: ' + slug)
        for section in sections:
            refs = section.get('source_refs', [])
            if not isinstance(refs, list) or any(type(ref) is not int or not 1 <= ref <= len(sources) for ref in refs):
                raise ValueError('Invalid section source reference: ' + slug)
        banner = article.get('banner')
        if banner is not None and (not isinstance(banner, dict) or not re.fullmatch(r'[a-z0-9-]+\.svg', banner.get('file', ''))
                                   or not isinstance(banner.get('alt'), str) or not banner['alt'].strip()):
            raise ValueError('Article banners need an SVG file name and alt text: ' + slug)
        points = article.get('key_points', [])
        if not isinstance(points, list) or len(points) > 5 or any(not isinstance(p, str) or not p.strip() for p in points):
            raise ValueError('Key points must be a list of at most five plain-text strings: ' + slug)
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


def banner_svg(root, article):
    """The article's banner as inline SVG with its alt text, or ''."""
    banner = article.get('banner')
    if not banner:
        return ''
    return figure_html(root, article['slug'], {**banner, 'caption': '-'}).split('<div class="figure-scroll">', 1)[1].split('</div><figcaption>', 1)[0]


def first_figure(root, article):
    """A decorative thumbnail (no caption): the banner, else the first figure, else ''."""
    if article.get('banner'):
        svg = banner_svg(root, article)
        return '<div class="article-figure card-figure card-banner" aria-hidden="true">' + re.sub(r'\srole="img" aria-label="[^"]*"', '', svg, count=1) + '</div>'
    figure = next((s['figure'] for s in article['sections'] if s.get('figure')), None)
    if not figure:
        return ''
    svg = figure_html(root, article['slug'], figure).split('<div class="figure-scroll">', 1)[1].split('</div><figcaption>', 1)[0]
    return '<div class="article-figure card-figure" aria-hidden="true">' + re.sub(r'\srole="img" aria-label="[^"]*"', '', svg, count=1) + '</div>'


def metadata(article):
    words = sum(len(p.split()) for s in article['sections'] for p in s['paragraphs'])
    minutes = (words + 199) // 200
    # A one-minute estimate says more about brevity than about reading time; show it only from two minutes.
    reading = f'<span>{minutes} min read</span>' if minutes >= 2 else ''
    return f'<time datetime="{article["published"]}">{long_date(article["published"])}</time>{reading}'


def card(article, source, featured=False, thumbnail=''):
    url = relative(article_path(article), source)
    cls = 'lead-story' if featured else 'story-card'
    heading = 'h2' if featured else 'h3'
    return (f'<article class="{cls}" data-article data-topic="{article["topic"]}" data-format="{article["format"]}">' + ('' if featured else thumbnail) +
            f'<p class="story-label">{esc(TOPICS[article["topic"]])}<span> / </span>{esc(article["format"])}</p>'
            f'<{heading}><a href="{url}">{esc(article["title"])}</a></{heading}>'
            f'<p class="story-summary">{esc(article["summary"])}</p>'
            f'<p class="story-meta">{metadata(article)}</p>'
            + (f'<a class="story-read" href="{url}">Read the article <span aria-hidden="true">↗</span></a>' if featured else '') + '</article>')


def lead_feature(root, article, source):
    # The lead story is shown beside its own first figure when it has one, else the house illustration.
    return '<section class="feature" aria-label="Featured story">' + card(article, source, True) + (first_figure(root, article) or signal_art()) + '</section>'


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
    return '<section class="paper-digest" aria-labelledby="papers-heading"><div class="section-top"><div><p class="eyebrow">Papers</p><h2 id="papers-heading">Recently selected papers</h2></div><a href="'+relative('news/papers/index.html', source)+'">All selected papers ↗</a></div><p class="section-intro">Technical summaries, methods, and limitations for researchers and advanced readers.</p><ol>'+items+'</ol>'+('' if items else '<p>No research papers have been selected yet.</p>')+'</section>'


def render_editorial(root, outputs, book, site_logo, social_meta, json_ld):
    articles = load_articles(root)
    config = json.loads((root / 'content/news.json').read_text())
    papers = load_papers(root)['papers']
    validate(articles, config, papers)
    published = sorted((a for a in articles if a['status'] == 'published'), key=lambda a: (a['published'], a['slug']), reverse=True)
    approved = sorted((p for p in papers if p['status'] == 'approved'), key=lambda p: (p['approved_on'], p['submitted']), reverse=True)
    featured = next((a for a in published if a['slug'] == config.get('featured')), published[0] if published else None)
    site_url = book['url']

    def shell(source, title, description, body, article=None, assets=''):
        up = '../' * source.count('/')
        canonical = site_url + '/' + source.removesuffix('index.html')
        structured = {'@context': 'https://schema.org', '@type': 'WebSite' if source == 'index.html' else 'CollectionPage', 'name': title, 'url': canonical, 'description': description}
        if article:
            structured.update({'@type': 'NewsArticle' if article['format'] == 'News' else 'Article', 'headline': title, 'datePublished': article['published'], 'dateModified': article.get('updated', article['published']), 'author': {'@type': 'Organization' if article['author'] == 'Quantum Research Center' else 'Person', 'name': article['author']}, 'publisher': {'@type': 'Organization', 'name': 'Quantum Research Center'}, 'citation': [s['url'] for s in article['sources']]})
        nav = site_navigation(source, 'editorial-nav')
        website_map = '<a href="website-map/index.html">Website map</a><a href="frontiers/entanglement/index.html">Entanglement frontier map</a>' if source == 'index.html' else ''
        # Article text may contain TeX (\(...\) inline, \[...\] displayed); load MathJax only where it is used.
        mathjax = (f'<script defer src="{up}education/computing/assets/source/mathjax-config.js"></script>'
                   f'<script defer src="{up}education/computing/assets/source/vendor/mathjax/tex-svg.js"></script>') if '\\(' in body or '\\[' in body else ''
        rss_news = '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="19" r="1.5" fill="currentColor" stroke="none"/><path d="M4 11a9 9 0 0 1 9 9M4 4a16 16 0 0 1 16 16"/></svg>'
        rss_papers = '<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h4M14 3l4 4v4M14 3v4h4"/><circle cx="14.5" cy="19.5" r="1.2" fill="currentColor" stroke="none"/><path d="M14 15.5a4.5 4.5 0 0 1 4.5 4.5M14 12a8 8 0 0 1 8 8"/></svg>'
        assets += f'<link rel="stylesheet" href="{up}news/refinements.css">'
        if source == "index.html":
            assets += '<link rel="stylesheet" href="news/homepage.css"><script defer src="news/homepage.js"></script>'
        outputs[source] = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Quantum Research Center</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}">{social_meta(title, description, canonical, 'article' if article else 'website')}{json_ld(structured)}<link rel="icon" href="{up}icons/icon.svg"><link rel="alternate" type="application/rss+xml" title="Quantum News" href="{up}news/articles/feed.xml"><link rel="alternate" type="application/rss+xml" title="Research Papers" href="{up}news/feed.xml"><script src="{up}education/computing/assets/theme.js"></script><script src="{up}navigation.js"></script><link rel="stylesheet" href="{up}styles.css"><link rel="stylesheet" href="{up}news/editorial.css"><script defer src="{up}news/articles.js"></script>{mathjax}{assets}</head>
<body class="editorial"><a class="skip-link" href="#main">Skip to content</a><header class="toolbar editorial-header">{site_logo('editorial-brand',up+'index.html')}{nav}</header><main id="main" tabindex="-1" class="editorial-main">{body}</main><footer class="editorial-footer"><div><strong>Quantum Research Center</strong><p>News, learning, and inquiry into quantum science.</p></div><nav aria-label="Footer">{website_map}<a href="{up}conferences/index.html">Conferences</a><a href="{up}companies/index.html">Companies</a><a href="{up}references/index.html">Bibliography</a><a href="mailto:{book['email']}">Contact</a><a class="footer-icon" href="{up}news/articles/feed.xml" aria-label="Quantum News RSS" title="Quantum News RSS">{rss_news}</a><a class="footer-icon" href="{up}news/feed.xml" aria-label="Research Papers RSS" title="Research Papers RSS">{rss_papers}</a></nav></footer></body></html>'''

    render_conferences(root, shell)
    render_companies(root, shell)
    render_tools(root, shell)
    render_claims_page(root, articles, shell)

    for source in ('index.html', 'news/index.html'):
        home = source == 'index.html'
        if home:
            body = homepage_opening()
        else:
            body = ('<header class="editorial-intro"><p class="eyebrow">Quantum Research Center / News</p>'
                    '<h1>Quantum News</h1><p>Summaries of reported results in quantum science, each with the source '
                    'it rests on and the scope the source states.</p></header>')
        if not home:
            body += stream_nav(source, 'all')
        if featured:
            body += lead_feature(root, featured, source)
        else:
            body += '<section class="empty-news"><h2>Quantum News</h2><p>Our first stories are on the way. Explore the research papers and courses below.</p></section>'
        for article_format, section_id, title, kicker in (
            ('News', 'latest-news', 'News', 'Latest'),
            ('Explainer', 'latest-explainers', 'Explainers', 'Background'),
        ):
            selection = [a for a in published if a != featured and a['format'] == article_format][:3]
            if not selection:
                continue
            body += (f'<section class="latest-stories" id="{section_id}" aria-labelledby="{section_id}-title">'
                     f'<div class="section-top"><div><p class="eyebrow">{kicker}</p><h2 id="{section_id}-title">{title}</h2></div>'
                     f'<a href="{relative("news/articles/index.html", source)}?format={article_format}">All {title.lower()} ↗</a></div>'
                     + (('<p class="home-section-intro">Reported developments, with links to the sources and a clear account of what was found.</p>' if article_format == 'News' else '<p class="home-section-intro">Take time with the ideas behind the headlines, one explanation at a time.</p>') if home else '')
                     + '<div class="story-grid">' + ''.join(card(a, source, thumbnail=first_figure(root, a)) for a in selection) + '</div></section>')
        if home:
            body += render_claims_home(root, articles)
        if home:
            body += ('<nav class="home-reference" aria-label="Reference and community"><span>Keep exploring</span>'
                     '<a href="map/index.html">Topic maps ↗</a><a href="references/index.html">Bibliography ↗</a>'
                     '<a href="conferences/index.html">Conferences ↗</a></nav>')
        else:
            body += '<section class="explore-paths" aria-label="Sections of the site"><div><p class="eyebrow">Sections</p><h2>Education, research, and topic maps</h2><p><a href="'+relative('conferences/index.html', source)+'">Quantum conferences ↗</a></p></div><a href="'+relative('education/index.html', source)+'"><span>01 / Education</span><strong>Courses and experiments ↗</strong><p>Course texts, worked examples, and interactive experiments.</p></a><a href="'+relative('research/index.html', source)+'"><span>02 / Research</span><strong>Research questions ↗</strong><p>Questions developed as models, calculations, and open problems.</p></a><a href="'+relative('map/index.html', source)+'"><span>03 / Maps</span><strong>Topic maps ↗</strong><p>Quantum topics arranged from broad areas to narrower ones.</p></a></section>'
        body += paper_preview(approved, source)
        shell(source, 'Quantum science: news, courses, and reference' if home else 'News',
              'Reported results in quantum science with their sources, alongside research papers, courses, and reference material.', body)

    source = 'news/articles/index.html'
    body = '<header class="editorial-intro compact"><p class="eyebrow">News</p><h1>Quantum News</h1><p>Summaries of reported results, appointments, and public programmes in quantum science, with the paper or announcement each one rests on.</p></header>'+stream_nav(source, 'articles')
    body += '<section class="article-filters" aria-label="Filter articles" hidden><label>Search articles<input id="article-search" type="search" placeholder="Search headlines and summaries…"></label><label>Topic<select id="article-topic"><option value="all">All topics</option>'+''.join(f'<option value="{key}">{esc(label)}</option>' for key, label in TOPICS.items())+'</select></label><label>Format<select id="article-format"><option value="all">All formats</option>'+''.join(f'<option>{label}</option>' for label in FORMATS)+'</select></label><p id="article-count" role="status"></p></section>'
    if featured:
        body += lead_feature(root, featured, source)
    body += '<section aria-label="Articles" class="story-grid article-list">'+''.join(card(a, source, thumbnail=first_figure(root, a)) for a in published if a != featured)+'</section>'
    if not published:
        body += '<p>Our first stories are on the way. <a href="../papers/index.html">Explore research papers →</a></p>'
    shell(source, 'Quantum News', 'Reported results, companies, public programmes, and background articles in quantum science, each with its source.', body)

    by_slug = {a['slug']: a for a in published}
    by_id = {p['id']: p for p in approved}
    for article in published:
        source = article_path(article)
        sections = article['sections']
        long_read = len(sections) >= 5
        body = f'<article class="general-article{" has-toc" if long_read else ""}"><nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../index.html">Quantum News</a></li><li><a href="../index.html?topic={article["topic"]}">{esc(TOPICS[article["topic"]])}</a></li></ol></nav>'
        body += f'<header><p class="story-label">{esc(article["format"])}</p><h1>{esc(article["title"])}</h1><p class="article-deck">{esc(article["summary"])}</p>'
        if article.get('banner'):
            body += '<figure class="article-figure article-banner">' + banner_svg(root, article) + '</figure>'
        if article.get('key_points'):
            body += '<section class="key-points" aria-labelledby="key-points-heading"><h2 id="key-points-heading" class="eyebrow">Key points</h2><ul>'+''.join('<li>'+esc(p)+'</li>' for p in article['key_points'])+'</ul></section>'
        meta = f'<span>By {esc(article["author"])}</span>{metadata(article)}'
        if article.get('updated') and article['updated'] != article['published']:
            meta += f'<span>Updated <time datetime="{article["updated"]}">{long_date(article["updated"])}</time></span>'
        papers_here = article.get('related_papers', [])
        if papers_here:
            target = '#research-analysis' if len(papers_here) > 1 else relative(paper_path(by_id[papers_here[0]]), source)
            meta += f'<a href="{target}">Technical summary →</a>'
        body += f'<p class="story-meta">{meta}</p></header><div class="article-layout">'
        if long_read:
            # A plain disclosure (the site's standard toggle); articles.js opens it where it fits in the margin.
            body += '<details class="article-toc"><summary>In this article</summary><ol>'+''.join(f'<li><a href="#section-{i}">'+(f'<span class="toc-kicker">{esc(s["kicker"])}</span> ' if s.get('kicker') else '')+f'{esc(s["heading"])}</a></li>' for i, s in enumerate(sections, 1))+'</ol></details>'
        body += '<div class="article-prose">'
        for i, section in enumerate(sections, 1):
            paragraphs = ['<p>'+esc(p) for p in section['paragraphs']]
            if section.get('source_refs'):
                # Section-level citations sit quietly after the section's last paragraph.
                # Bind the citation to the paragraph's last word so it never wraps onto a line of its own.
                last = paragraphs[-1]
                head, _, word = last.rpartition(' ')
                if (' ' in last and '\\' not in word and head.count('\\(') == head.count('\\)') and head.count('\\[') == head.count('\\]')):
                    paragraphs[-1] = head + ' <span class="cite-tail">' + word
                    closing = '</span>'
                else:
                    closing = ''
                paragraphs[-1] += '<sup class="cite">'+'<span aria-hidden="true">[</span>'+','.join(f'<a href="#source-{ref}" aria-label="Source {ref}: {esc(article["sources"][ref-1]["title"])}">{ref}</a>' for ref in section['source_refs'])+'<span aria-hidden="true">]</span></sup>'+closing
            kicker = f'<p class="section-kicker">{esc(section["kicker"])}</p>' if section.get('kicker') else ''
            stats = ''
            if section.get('stats'):
                # Key numbers, set large, follow the first paragraph that introduces them.
                stats = '<dl class="article-stats">'+''.join(f'<div><dt>{esc(x["label"])}</dt><dd>{esc(x["value"])}</dd></div>' for x in section['stats'])+'</dl>'
            parts = [p+'</p>' for p in paragraphs]
            # A run of "card" sections is a tutorial: one self-contained idea per card.
            classes = ' '.join(c for c, on in (('has-kicker', kicker), ('concept-card', section.get('card'))) if on)
            body += f'<section id="section-{i}"{f" class=\"{classes}\"" if classes else ""}>{kicker}<h2>{esc(section["heading"])}</h2>'+parts[0]+stats+''.join(parts[1:])
            table = section.get('table')
            if table:
                head = ''.join(f'<th scope="col">{esc(c)}</th>' for c in table['columns'])
                rows = ''.join('<tr>'+''.join((f'<th scope="row">{esc(c)}</th>' if k == 0 else f'<td>{esc(c)}</td>') for k, c in enumerate(r))+'</tr>' for r in table['rows'])
                caption = f'<caption>{esc(table["caption"])}</caption>' if table.get('caption') else ''
                body += f'<div class="article-table" role="region" aria-label="{esc(table.get("caption", section["heading"]))}" tabindex="0"><table>{caption}<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
            if section.get('figure'):
                body += figure_html(root, article['slug'], section['figure'])
            if section.get('asks'):
                body += '<div class="article-asks"><p class="asks-label">What to ask</p><ul>'+''.join(f'<li>{esc(q)}</li>' for q in section['asks'])+'</ul></div>'
            body += '</section>'
        body += '<section class="article-sources"><h2>Sources &amp; further reading</h2><ol>'+''.join(f'<li id="source-{ref}"><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a></li>' for ref, s in enumerate(article['sources'], 1))+'</ol></section>'
        if article.get('related_papers'):
            body += '<section id="research-analysis"><h2>Read the research analysis</h2><ul>'+''.join(f'<li><a href="{relative(paper_path(by_id[pid]), source)}">{esc(by_id[pid]["title"])}</a></li>' for pid in article['related_papers'])+'</ul></section>'
        body += '</div></div></article>'
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
