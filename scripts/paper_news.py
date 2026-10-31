"""Render reviewed arXiv candidates and editor-approved news using the site shell."""
import html
import json
import re
from datetime import date

# The main list stays this long however many papers accumulate; every paper stays in a monthly archive.
LATEST_PAPERS = 40
TOPICS = {'foundations': 'Foundations of quantum mechanics', 'computing': 'Quantum computing', 'information': 'Quantum information'}
def esc(s): return html.escape(str(s), quote=True)
def long_date(s):
    d = date.fromisoformat(s)
    return f'{d.day} {d:%B %Y}'
COLLECTION = '_collection.json'

def load_papers(root):
    """Each paper is one file in content/papers/; _collection.json holds the shared fields."""
    directory = root/'content/papers'
    data = json.loads((directory/COLLECTION).read_text())
    data['papers'] = [json.loads(path.read_text()) for path in sorted(directory.glob('*.json')) if path.name != COLLECTION]
    return data

def save_papers(root, data):
    directory = root/'content/papers'
    directory.mkdir(parents=True, exist_ok=True)
    (directory/COLLECTION).write_text(json.dumps({k: v for k, v in data.items() if k != 'papers'}, ensure_ascii=False, indent=2)+'\n')
    files = {pid_of(p)+'.json': p for p in data['papers']}
    for name, paper in files.items():
        (directory/name).write_text(json.dumps(paper, ensure_ascii=False, indent=2)+'\n')
    for path in directory.glob('*.json'):
        if path.name != COLLECTION and path.name not in files: path.unlink()

def validate(data):
    seen = set()
    for p in data['papers']:
        if not re.fullmatch(r'(?:\d{4}\.\d{4,5}|quant-ph/\d{7})', p['id']) or p['id'] in seen:
            raise ValueError('Invalid or duplicate arXiv ID: '+p['id'])
        seen.add(p['id'])
        if p['topic'] not in TOPICS or p['status'] not in ('candidate', 'approved'):
            raise ValueError('Invalid paper topic/status')
        date.fromisoformat(p['submitted'])
        if not re.fullmatch(r'v\d+', p['version']): raise ValueError('Invalid version')
        for key in ('title','authors','problem','result','significance','limitations','summary_basis'):
            if not p.get(key, '').strip(): raise ValueError('Missing paper field: '+key)
        if 'description' in p and (not isinstance(p['description'], list) or any(not isinstance(x, str) or not x.strip() for x in p['description'])):
            raise ValueError('Description must be a list of paragraphs: '+p['id'])
        if p['status']=='approved':
            date.fromisoformat(p['approved_on'])
            if not p.get('description'): raise ValueError('Approved paper needs a description: '+p['id'])
            if not isinstance(p.get('methods'), list) or not p['methods']:
                raise ValueError('Approved paper needs transferable methods: '+p['id'])
        if p.get('methods'):
            if not isinstance(p['methods'], list): raise ValueError('Methods must be a list')
            for method in p['methods']:
                if not isinstance(method, dict) or any(not isinstance(method.get(k), str) or not method[k].strip() for k in ('technique','explanation','transfer')):
                    raise ValueError('Each method needs technique, explanation, and transfer: '+p['id'])
                math = method.get('math')
                if (math is None and p['status']=='approved') or (math is not None and (not isinstance(math, list) or not math or any(not isinstance(x, str) or not x.strip() for x in math))):
                    raise ValueError('Each approved method needs a mathematical explanation (math: list of paragraphs): '+p['id'])
            for key in ('methods_source_section','methods_basis'):
                if not isinstance(p.get(key), str) or not p[key].strip(): raise ValueError('Missing '+key+': '+p['id'])

def pid_of(p): return p['id'].replace('/', '-')
def paper_path(p): return 'news/papers/'+pid_of(p)+'/index.html'
def plural(n, word): return f'{n} {word}{"" if n == 1 else "s"}'
def month_label(s): return f'{date.fromisoformat(s):%B %Y}'

def source_line(p):
    ref = esc(p['id']+p['version'])
    return f'<p class="paper-source"><a href="https://arxiv.org/abs/{ref}">arXiv:{ref} ↗</a><a href="https://arxiv.org/pdf/{ref}">PDF ↗</a><span>Submitted {esc(long_date(p["submitted"]))}</span></p>'

def summary_html(p):
    return '<dl class="paper-summary">'+''.join(f'<div><dt>{label}</dt><dd>{esc(p[key])}</dd></div>' for key, label in [('problem', 'Question'), ('result', 'Result')])+'</dl>'

def description_html(p):
    return ''.join(f'<p>{esc(x)}</p>' for x in p.get('description', []))

def methods_html(p, heading='h5'):
    out = '<ol class="method-list">'
    for method in p['methods']:
        out += f'<li><{heading}>{esc(method["technique"])}</{heading}><p>{esc(method["explanation"])}</p>'+''.join(f'<p class="paper-math">{esc(x)}</p>' for x in method.get('math', []))
        out += f'<div class="paper-reuse"><p class="paper-reuse-label">How to reuse it</p><p>{esc(method["transfer"])}</p></div></li>'
    return out+f'</ol><p class="paper-meta">Source: <a href="https://arxiv.org/html/{esc(p["id"]+p["version"])}">{esc(p["methods_source_section"])}</a>. {esc(p["methods_basis"])}</p>'

def context_html(p):
    return f'<p><strong>Why it matters.</strong> {esc(p["significance"])}</p><p><strong>Limitations.</strong> {esc(p["limitations"])}</p><p class="paper-meta">{esc(p["summary_basis"])}</p>'

def candidate_card(p):
    """Full review card: everything an editor needs before approving."""
    pid = pid_of(p)
    out = f'<section class="paper-card" id="paper-{pid}" data-topic="{p["topic"]}" data-paper-id="{esc(p["id"])}"><p class="kicker paper-kicker">{esc(TOPICS[p["topic"]])} · {esc(p["kind"])}</p><h3>{esc(p["title"])}</h3><p class="paper-authors">{esc(p["authors"])}</p>'
    out += source_line(p)+summary_html(p)+'<div class="paper-sections">'
    if p.get('description'):
        out += '<details class="paper-section"><summary>The paper in detail<span>Setting, main result, and open questions</span></summary><div class="paper-section-body">'+description_html(p)+'</div></details>'
    if p.get('methods'):
        out += f'<details class="paper-section"><summary>Transferable methods<span>{plural(len(p["methods"]), "technique")}, with derivations</span></summary><div class="paper-section-body">'+methods_html(p)+'</div></details>'
    out += '<details class="paper-section"><summary>Context &amp; limitations<span>Why it matters and what it does not show</span></summary><div class="paper-section-body">'+context_html(p)+'</div></details></div>'
    out += f'<label class="paper-choice"><input type="checkbox" value="{esc(p["id"])}"> Select for approval</label><p class="paper-approval-status" aria-live="polite"></p>'
    return out+'<a class="paper-back" href="#main">Back to top ↑</a></section>'

def archive_path(month): return f'news/papers/archive/{month}/index.html'

def entry(p, papers=''):
    """Compact listing entry; the full write-up lives on the paper's own page."""
    pid = pid_of(p)
    techniques = '; '.join(esc(m['technique']) for m in p['methods'])
    return (f'<section class="paper-card paper-entry" id="paper-{pid}" data-topic="{p["topic"]}" data-paper-id="{esc(p["id"])}">'
        f'<p class="kicker paper-kicker">{esc(TOPICS[p["topic"]])} · {esc(p["kind"])}</p><h3><a href="{papers}{pid}/index.html">{esc(p["title"])}</a></h3>'
        f'<p class="paper-authors">{esc(p["authors"])}</p>{source_line(p)}{summary_html(p)}'
        f'<p class="paper-entry-methods"><span>Methods</span> {techniques}</p><a class="paper-read" href="{papers}{pid}/index.html">Read the full entry →</a></section>')

def paper_page(p, newer, older):
    pid = pid_of(p)
    def pager(q, label, rel):
        return f'<a rel="{rel}" href="../{pid_of(q)}/index.html"><small>{label}</small>{esc(q["title"])}</a>' if q else '<span></span>'
    return (f'<article class="paper-page" data-topic="{p["topic"]}"><nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../index.html">Research Papers</a></li><li><a href="../index.html?topic={p["topic"]}">{esc(TOPICS[p["topic"]])}</a></li></ol></nav>'
        f'<header class="paper-page-header"><p class="kicker paper-kicker">{esc(TOPICS[p["topic"]])} · {esc(p["kind"])}</p><h1>{esc(p["title"])}</h1><p class="paper-authors">{esc(p["authors"])}</p>{source_line(p)}</header>'
        f'{summary_html(p)}<section id="detail" class="paper-page-section"><h2>The paper in detail</h2>{description_html(p)}</section>'
        f'<section id="methods" class="paper-page-section"><h2>Transferable methods</h2>{methods_html(p, "h3")}</section>'
        f'<section id="context" class="paper-page-section"><h2>Context &amp; limitations</h2>{context_html(p)}</section>'
        f'<nav class="paper-pager" aria-label="More selected papers">{pager(newer, "← Newer", "prev")}{pager(older, "Older →", "next")}</nav></article>')

def plain(text):
    # Feed readers do not typeset TeX; drop the delimiters and keep the expressions readable.
    return re.sub(r'\\[()\[\]]', '', text)

def rss(papers, site_url):
    def item(p):
        url = f'{site_url}/'+paper_path(p).removesuffix('index.html')
        published = date.fromisoformat(p['approved_on'])
        return (f'<item><title>{esc(p["title"])}</title><link>{url}</link><guid isPermaLink="true">{url}</guid>'
            f'<pubDate>{published:%a, %d %b %Y} 00:00:00 +0000</pubDate><category>{esc(TOPICS[p["topic"]])}</category>'
            f'<description>{esc(plain(p["problem"]+" "+p["result"]))}</description></item>')
    updated = max((date.fromisoformat(p['approved_on']) for p in papers), default=date(2026, 1, 1))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f'<title>Selected papers | Quantum Research Center</title><link>{site_url}/news/papers/</link>'
        f'<atom:link href="{site_url}/news/feed.xml" rel="self" type="application/rss+xml"/>'
        '<description>Recent arXiv papers in quantum foundations, computing, and information, with explanations of their transferable methods.</description>'
        f'<language>en</language><lastBuildDate>{updated:%a, %d %b %Y} 00:00:00 +0000</lastBuildDate>'
        + ''.join(item(p) for p in papers) + '</channel></rss>\n')

def render_news(root, page, outputs, site_url):
    data = load_papers(root)
    validate(data)
    papers = sorted(data['papers'], key=lambda p: p['submitted'], reverse=True)
    approved = sorted((p for p in papers if p['status'] == 'approved'), key=lambda p: (p['approved_on'], p['submitted']), reverse=True)
    candidates = [p for p in papers if p['status'] == 'candidate']

    # Review page: only papers still awaiting approval.
    body='<header class="title-page"><p class="kicker">Literature desk</p><h1>Paper review</h1><p class="subtitle">Questions, results, and context from quantum research on arXiv.</p><details class="news-about"><summary>About this shortlist</summary><p>Recent recommendations checked on '+esc(data['reviewed_on'])+'. Chosen for relevance, a clear research question, and potential significance; this is an editorial shortlist, not a citation ranking or an exhaustive feed.</p></details></header>'
    body+='<section id="selection" class="editorial-note"><h2>Find &amp; select papers</h2><div id="paper-tools" hidden><label for="paper-search">Search titles, authors, and summaries</label><input id="paper-search" type="search" placeholder="Search papers…"><label for="paper-topic">Research area</label><select id="paper-topic"><option value="all">All areas</option>'+''.join(f'<option value="{k}">{v}</option>' for k,v in TOPICS.items())+'</select><p id="paper-count" role="status"></p><div class="paper-actions"><button type="button" id="paper-approve" disabled>Approve selected papers</button><button type="button" id="paper-export">Copy selection</button></div><p id="paper-approval" role="status">Connecting to the local editor…</p><p id="paper-editor-help" hidden>To enable approval, run <code>python3 scripts/news_editor.py</code> in the project folder, then open <a href="http://127.0.0.1:8765/news/papers.html">the local editor</a>.</p><details class="selection-export"><summary>Selected paper list &amp; export</summary><label for="paper-selection">Selected paper list</label><textarea id="paper-selection" rows="5" readonly placeholder="Your selected papers will appear here."></textarea><p id="paper-storage" role="status"></p></details></div><noscript><p>To select without JavaScript, send the editor the arXiv IDs from the paper links.</p></noscript></section>'
    body+='<section id="candidates"><h2>Awaiting approval</h2>'+(''.join(candidate_card(p) for p in candidates) or '<p>No papers are awaiting approval. Add candidates to <code>content/papers/</code> with <code>status: "candidate"</code>.</p>')
    body+=f'<p class="paper-meta">{plural(len(approved), "approved paper")} appear on the <a href="papers/index.html">research paper feed</a>.</p></section><script defer src="papers.js"></script>'
    page('news/papers.html','Recent paper shortlist',body,[(None,'On this page'),('#selection','Find & select'),*[(f'#paper-{pid_of(p)}',p['title']) for p in candidates]])

    # One page per approved paper, ordered newest selection first.
    for i, p in enumerate(approved):
        newer = approved[i-1] if i else None
        older = approved[i+1] if i+1 < len(approved) else None
        page(paper_path(p), p['title'], paper_page(p, newer, older),
            [(None,'On this page'),('#detail','The paper in detail'),('#methods','Transferable methods'),('#context','Context & limitations'),(None,'Selected papers'),(f'../archive/{p["approved_on"][:7]}/index.html#paper-{pid_of(p)}','Back to the list'),(f'../index.html?topic={p["topic"]}','More in '+TOPICS[p['topic']])],
            description=p['problem'])

    # Compact listing of the latest papers, one archive page per selection month, and a search index.
    months = list(dict.fromkeys(p['approved_on'][:7] for p in approved))
    filters='<section class="news-filters" id="news-filters" hidden><label for="news-search">Search all papers<input id="news-search" type="search" placeholder="Title, author, or technique…"></label><label for="news-topic">Research area<select id="news-topic"><option value="all">All areas</option>'+''.join(f'<option value="{key}">{label}</option>' for key,label in TOPICS.items())+'</select></label><p id="news-count" role="status"></p></section>'
    def by_month(month, papers, prefix=''):
        return f'<section class="news-month" id="month-{month}"><h2 class="news-list-heading">Selected in {month_label(month+"-01")}</h2>'+''.join(entry(p, prefix) for p in papers if p['approved_on'].startswith(month))+'</section>'
    def listing(news_root, content):
        return f'<div id="articles" data-news-root="{news_root}">{content}</div><section id="earlier-results" hidden><h2 class="news-list-heading">Earlier papers</h2><div id="earlier-list"></div></section><script defer src="{news_root}browse.js"></script>'
    def areas(home):
        return [(None,'Research areas'),(home,'All areas'),*[(f'{home}?topic={k}',v) for k,v in TOPICS.items()]]
    latest = approved[:LATEST_PAPERS]
    news='<header class="title-page"><p class="kicker">Research updates</p><h1>Research Papers</h1><p class="subtitle">Recent arXiv papers in quantum foundations, computing, and information. Each entry states the question and result; its full page explains the paper in detail and the methods worth reusing, with derivations.</p><p class="news-stamp">'+f'{plural(len(approved), "paper")} · reviewed {esc(long_date(data["reviewed_on"]))}'+'</p></header>'+filters
    content=''.join(by_month(m, latest) for m in dict.fromkeys(p['approved_on'][:7] for p in latest)) or '<p>No articles have been approved yet.</p>'
    if len(approved) > len(latest): content+=f'<p class="paper-meta">Showing the {len(latest)} latest of {plural(len(approved), "paper")}. Search above covers all of them, or browse earlier months in the section menu.</p>'
    page('news/papers/index.html','Research Papers',news+listing('../',content),[*areas('index.html'),(None,'By month'),*[(f'archive/{m}/index.html',month_label(m+'-01')) for m in months]])
    for i, m in enumerate(months):
        selected = [p for p in approved if p['approved_on'].startswith(m)]
        header=f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../../index.html">Research Papers</a></li></ol></nav><header class="title-page"><p class="kicker">Research paper archive</p><h1>{month_label(m+"-01")}</h1><p class="news-stamp">{plural(len(selected), "paper")}</p></header>'
        pager=''.join(f'<a rel="{rel}" href="../{other}/index.html"><small>{label}</small>{month_label(other+"-01")}</a>' if other else '<span></span>' for other,label,rel in ((months[i-1] if i else None,'← Newer','prev'),(months[i+1] if i+1<len(months) else None,'Older →','next')))
        page(archive_path(m),f'Research papers: {month_label(m+"-01")}',header+filters+listing('../../../',by_month(m, approved, '../../'))+f'<nav class="paper-pager" aria-label="More months">{pager}</nav>',
            [*areas('../../index.html'),(None,'By month'),*[(f'../{other}/index.html',month_label(other+'-01')) for other in months]],
            description=f'Quantum research papers selected in {month_label(m+"-01")}, with their questions, results, and transferable methods.')
    outputs['news/feed.xml'] = rss(approved[:30], site_url)
    outputs['news/index.json'] = json.dumps({'reviewed_on': data['reviewed_on'], 'papers': [
        {'id': p['id'], 'url': paper_path(p).removeprefix('news/'), 'title': p['title'], 'authors': p['authors'], 'topic': p['topic'],
         'submitted': p['submitted'], 'approved_on': p['approved_on'], 'problem': p['problem'], 'result': p['result'],
         'techniques': [m['technique'] for m in p['methods']]} for p in approved]}, ensure_ascii=False, indent=1)+'\n'
