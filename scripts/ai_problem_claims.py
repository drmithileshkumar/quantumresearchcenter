"""An evolving claim register and its compact homepage introduction."""
import html
import json
import re
from datetime import date
from urllib.parse import urlsplit

PAGE = 'ai-problem-claims/index.html'


def load_claims(root, articles):
    data = json.loads((root / 'content/ai-problem-claims.json').read_text())
    reviewed = date.fromisoformat(data['reviewed_on'])
    public = {a['slug'] for a in articles if a['status'] == 'published'}
    seen = set()
    for item in data['problems']:
        ident = item['id']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError('Invalid or duplicate problem ID: ' + ident)
        seen.add(ident)
        category = item.get('category')
        if category not in ('claimed', 'open'):
            raise ValueError('Invalid problem category')
        fields = ('claimant',) if category == 'claimed' else ('source_label',)
        for key in ('field', 'problem', 'question', 'status', 'scope', *fields):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError('Missing problem claim field: ' + key)
        url = urlsplit(item['source'])
        if url.scheme != 'https' or not url.netloc:
            raise ValueError('Problem claims require an HTTPS source')
        if category == 'claimed' and date.fromisoformat(item['announced']) > reviewed:
            raise ValueError('Claim announcement follows review date')
        if item.get('article') and item['article'] not in public:
            raise ValueError('Problem claim article must be published')
    return data


def render_claims(root, articles, prefix='../'):
    if not (root / 'content/ai-problem-claims.json').exists():
        return ''
    data = load_claims(root, articles)
    if not data['problems']:
        return ''
    esc = lambda value: html.escape(value, quote=True)
    cards = {'claimed': [], 'open': []}
    for item in data['problems']:
        claimed = item['category'] == 'claimed'
        attribution = (f'{esc(item["claimant"])} · <time datetime="{item["announced"]}">{date.fromisoformat(item["announced"]).strftime("%d %b %Y")}</time>'
                       if claimed else esc(item['source_label']))
        link_label = 'Read the claim' if claimed else 'Read about the problem'
        explainer = (f'<a href="{prefix}news/articles/{esc(item["article"])}/index.html">Read our explainer</a>'
                     if item.get('article') else '')
        cards[item['category']].append(f'''<li class="problem-claim" id="{esc(item['id'])}">
<p class="problem-field">{esc(item['field'])}</p>
<h3><a href="#{esc(item['id'])}">{esc(item['problem'])}</a></h3><p class="problem-question">{esc(item['question'])}</p>
<p class="problem-status">{esc(item['status'])}</p><p class="problem-scope">{esc(item['scope'])}</p>
<p class="problem-attribution">{attribution}</p>
<div class="problem-links"><a href="{esc(item['source'])}">{link_label}<span class="visually-hidden">: {esc(item['problem'])}</span> ↗</a>{explainer}</div>
</li>''')
    return f'''<div id="ai-problem-claims">
<nav class="problem-links" aria-label="Problem categories"><a href="#claimed-by-ai">Claimed by AI ({len(cards['claimed'])})</a><a href="#still-open">Still open ({len(cards['open'])})</a></nav>
<section class="problem-claims" id="claimed-by-ai" aria-labelledby="claimed-title">
<div class="section-top"><h2 id="claimed-title">Claimed by AI</h2></div>
<p class="problem-intro">AI-assisted proofs, refutations, and partial results reported by the named teams. These are attributed claims, not a list of independently confirmed solutions. A claim here does not by itself establish that a problem is closed.</p>
<ul class="problem-claims-grid">{''.join(cards['claimed'])}</ul>
</section>
<section class="problem-claims" id="still-open" aria-labelledby="open-title">
<div class="section-top"><h2 id="open-title">Still open</h2></div>
<p class="problem-intro">Selected unresolved problems, with links to their statements and research context. This is a curated list, not a claim that no proposed solutions exist. Where only part of a problem has an AI resolution claim, its unresolved part is listed separately.</p>
<ul class="problem-claims-grid">{''.join(cards['open'])}</ul>
</section>
<p class="problem-review">Sources reviewed <time datetime="{data['reviewed_on']}">{date.fromisoformat(data['reviewed_on']).strftime('%d %B %Y')}</time>. Formal verification, expert review, and the scope of a claimed result are distinct; follow the linked sources for updates.</p>
</div>'''


def render_claims_home(root, articles):
    if not (root / 'content/ai-problem-claims.json').exists():
        return ''
    data = load_claims(root, articles)
    if not data['problems']:
        return ''
    return f'''<section class="problem-claims problem-claims-preview" aria-labelledby="claims-preview-title">
<div class="section-top"><div><p class="eyebrow">Major questions / AI research</p><h2 id="claims-preview-title">Famous problems. New claims.</h2></div></div>
<p class="problem-intro">Explore two sections: Claimed by AI and Still open. Follow reported results and unresolved questions in physics, mathematics, computer science, and quantum information, with scope notes and sources.</p>
<p class="problem-links"><a href="{PAGE}">Explore the problems and developments ↗</a></p>
<p class="problem-review">{len(data['problems'])} problems tracked · Sources reviewed <time datetime="{data['reviewed_on']}">{date.fromisoformat(data['reviewed_on']).strftime('%d %B %Y')}</time></p>
</section>'''


def render_claims_page(root, articles, shell):
    register = render_claims(root, articles)
    if not register:
        return
    header = '''<header class="editorial-intro compact"><p class="eyebrow">Research watch</p>
<h1>AI and famous problems</h1><p>An evolving register of AI-assisted resolution claims and problems that remain open. We will update this page as new claims, reviews, corrections, and explanations appear.</p>
<p><a href="../index.html">← Back to the homepage</a></p></header>'''
    shell(PAGE, 'AI and famous problems',
          'Track AI-assisted resolution claims in physics, mathematics, computer science, and quantum information, with sources and scope notes.', header + register)
