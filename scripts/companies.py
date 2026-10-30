"""Source-backed country directory, rendered through the shared editorial shell."""
from datetime import date
from html import escape
import json
import re
from urllib.parse import urlsplit
from conference_map import render_map

FOCUS = ('Computing hardware', 'Software & applications', 'Control & infrastructure', 'Communication & security')


def validate(data):
    checked = date.fromisoformat(data['checked'])
    ids = set()
    for company in data['companies']:
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', company['id']), 'Invalid company ID'
        assert company['id'] not in ids, 'Duplicate company ID'
        ids.add(company['id'])
        for field in ('name', 'country', 'city', 'description'):
            assert company[field].strip(), f'Missing {field}'
        assert company['focus'] and set(company['focus']) <= set(FOCUS), 'Unknown focus area'
        assert company['sources'], 'Official sources required'
        assert date.fromisoformat(company['checked']) <= checked, 'Entry checked after directory date'
        for url in [company['url'], *company['sources']]:
            parsed = urlsplit(url)
            assert parsed.scheme == 'https' and parsed.netloc, 'Use HTTPS sources'


def render_companies(root, shell):
    data = json.loads((root / 'content/companies.json').read_text())
    validate(data)
    companies = sorted(data['companies'], key=lambda c: (c['country'], c['name'].casefold()))
    countries = sorted({c['country'] for c in companies})
    e = escape
    def slug(country): return country.lower().replace(' ', '-')
    body = f'''<header class="editorial-intro"><p class="eyebrow">The quantum community / Companies</p><h1>Who is building<br><span>the quantum world?</span></h1><p>Discover companies working in quantum computing and quantum information. Explore by country, follow a technology, and go directly to the source.</p></header>
<nav class="community-nav" aria-label="Community directories"><a href="../conferences/index.html">Conferences ↗</a><a href="index.html" aria-current="page">Companies by country</a></nav>
<div class="company-stats"><p><strong>{len(companies):02}</strong> companies</p><p><strong>{len(countries):02}</strong> countries</p><p><strong>{len(FOCUS):02}</strong> focus areas</p><p class="company-checked">Sources checked<br><time datetime="{data['checked']}">{date.fromisoformat(data['checked']):%d %B %Y}</time></p></div>
<p class="company-scope">A curated starting point, grouped by a documented company base. Companies may have offices, customers, and parent organizations in other countries. Inclusion is not a ranking or endorsement; countries absent here are not necessarily without quantum companies.</p>
{render_map(root, companies, collection="companies")}
<form id="company-filters" hidden aria-label="Filter companies"><label for="company-search">Search companies<input id="company-search" type="search" placeholder="Company, city, or technology…"></label><label for="company-country">Country<select id="company-country"><option value="">All countries</option>'''
    body += ''.join(f'<option>{e(c)}</option>' for c in countries)
    body += '</select></label><label for="company-focus">Focus area<select id="company-focus"><option value="">All focus areas</option>'
    body += ''.join(f'<option>{e(f)}</option>' for f in FOCUS)
    body += '</select></label><button type="reset">Reset filters</button></form>'
    body += '<nav class="country-index" aria-label="Jump to country">'
    body += ''.join(f'<a href="#country-{slug(c)}">{e(c)} <span>{sum(x["country"]==c for x in companies)}</span></a>' for c in countries)
    body += f'</nav><div class="company-collection-heading"><h2>Explore by country</h2><p id="company-count" role="status">{len(companies)} companies across {len(countries)} countries</p></div><div id="company-collection">'
    for country in countries:
        members = [c for c in companies if c['country'] == country]
        body += f'<section class="company-country-group" id="country-{slug(country)}" data-country="{e(country)}" aria-labelledby="heading-{slug(country)}"><header class="country-heading"><h3 id="heading-{slug(country)}">{e(country)}</h3><span class="country-count">{len(members)} {"company" if len(members)==1 else "companies"}</span></header><div class="company-cards">'
        for c in members:
            search = ' '.join([c['name'], c['country'], c['city'], c['description'], *c['focus']])
            body += f'<article class="company-card" id="{c["id"]}" data-search="{e(search)}" data-focus="{e(json.dumps(c["focus"]))}"><div class="company-card-top"><h4><a href="{e(c["url"])}">{e(c["name"])} ↗</a></h4><p>{e(c["city"])}</p></div><p class="company-description">{e(c["description"])}</p><ul class="company-tags" aria-label="Focus areas">'
            body += ''.join(f'<li>{e(f)}</li>' for f in c['focus'])
            body += f'</ul><div class="company-card-bottom"><a href="{e(c["url"])}">Official website ↗</a><details><summary>Sources &amp; review</summary><ul>'
            body += ''.join(f'<li><a href="{e(url)}">Official source {i+1} ↗</a></li>' for i,url in enumerate(c['sources']))
            body += f'</ul><p>Checked <time datetime="{c["checked"]}">{c["checked"]}</time></p></details></div></article>'
        body += '</div></section>'
    body += '''</div><div id="company-empty" hidden><h3>No companies match these filters.</h3><p>Try another country, technology, or company name.</p><button id="company-clear" type="button">Reset filters</button></div>
<section class="company-guide"><p class="eyebrow">Find your field</p><h2>Different roles in the quantum ecosystem</h2><dl><div><dt>Computing hardware</dt><dd>Companies building quantum processors and complete computing systems.</dd></div><div><dt>Software &amp; applications</dt><dd>Tools for programming quantum computers, developing algorithms, and exploring applications.</dd></div><div><dt>Control &amp; infrastructure</dt><dd>The electronics and software that operate, calibrate, and read out quantum devices.</dd></div><div><dt>Communication &amp; security</dt><dd>Quantum networks, quantum key distribution, and quantum randomness. Post-quantum cryptography is a distinct, classical approach; a security offering alone does not imply a quantum computer.</dd></div></dl><p>Descriptions summarize the cited companies’ stated activities, not independent performance verification. This first edition focuses on specialist companies and is not a complete list of corporate quantum programmes.</p><a href="../conferences/index.html">Find conferences in the quantum community ↗</a></section><noscript><p>All companies are shown, grouped by country. Use the country links above to browse.</p></noscript>'''
    shell('companies/index.html', 'Quantum companies by country', 'A country-wise directory of companies working in quantum computing, software, control systems, and quantum communication.', body, assets='<link rel="stylesheet" href="../conferences/conferences.css"><link rel="stylesheet" href="companies.css"><script defer src="companies.js"></script>')
