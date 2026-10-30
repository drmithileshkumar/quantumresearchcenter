"""Render the source-backed conference directory into the shared editorial shell."""
from datetime import date
from html import escape
import json
from urllib.parse import urlsplit
from conference_map import render_map

QUALITY = {
    'Flagship research': 'Editorial selection of long-running, field-defining research meetings with a dedicated international scientific community.',
    'Established research': 'Recurring scientific meetings with a documented academic programme, committees, or institutional backing.',
    'Emerging / regional': 'Institution-hosted or regional meetings with a relevant scientific programme; a shorter or more local track record.',
    'Industry forum': 'Business and ecosystem meetings. Evaluate these for partnerships and applications, separately from research prestige.',
}

def validate(data):
    date.fromisoformat(data['checked'])
    ids = set()
    for event in data['conferences']:
        assert event['id'] not in ids, 'Duplicate conference ID'
        ids.add(event['id'])
        assert event['quality'] in QUALITY, 'Unknown quality category'
        assert bool(event['start']) == bool(event['end']), 'Provide both dates or neither'
        assert isinstance(event['year'], int)
        if event['start']:
            start, end = date.fromisoformat(event['start']), date.fromisoformat(event['end'])
            assert start <= end, 'End precedes start'
            assert start.year == event['year']
        date.fromisoformat(event['checked'])
        for field in ('url', 'source'):
            parsed = urlsplit(event[field])
            assert parsed.scheme == 'https' and parsed.netloc, 'Use HTTPS sources'
        for field in ('name', 'full_name', 'country', 'city', 'description', 'quality_reason'):
            assert event[field].strip(), f'Missing {field}'


def status(event, today):
    if not event['start']:
        return 'Dates pending'
    if event['end'] < today:
        return 'Past edition'
    if event['start'] <= today:
        return 'In progress'
    return 'Upcoming'


def render_conferences(root, shell):
    data = json.loads((root / 'content/conferences.json').read_text())
    validate(data)
    events = data['conferences']
    checked = data['checked']
    e = escape
    countries = sorted({c['country'] for c in events})
    upcoming = sum(status(c, checked) in ('Upcoming', 'In progress') for c in events)
    def options(values):
        return ''.join(f'<option value="{e(str(v))}">{e(str(v))}</option>' for v in values)
    body = f'''
<header class="editorial-intro conference-intro"><p class="eyebrow">The quantum community / Conferences</p><h1>Where quantum<br><span>ideas meet.</span></h1><p>A curated collection of quantum computing and quantum information conferences. Find your field, choose a destination, and plan your next conversation.</p></header>
<p class="directory-note">Explore the wider community: <a href="../companies/index.html">Quantum companies by country ↗</a></p>
<div class="conference-stats" aria-label="Collection summary"><p><strong>{len(events):02}</strong> conferences</p><p><strong>{len(countries):02}</strong> countries</p><p><strong id="upcoming-count">{upcoming:02}</strong> upcoming / in progress</p><p class="verified">Sources checked<br><time datetime="{checked}">{date.fromisoformat(checked):%d %B %Y}</time></p></div>
{render_map(root, events)}
<form id="conference-filters" class="conference-filters" hidden aria-label="Filter conferences">
<label class="search-field" for="conference-search">Search the collection<input id="conference-search" type="search" placeholder="Conference, topic, or city…"></label>
<label for="country">Country<select id="country"><option value="">All countries</option>{options(countries)}</select></label>
<label for="period">Date / status<select id="period"><option value="">All dates</option><option value="future">Upcoming &amp; in progress</option><option value="past">Past editions</option><option value="pending">Dates pending</option></select></label>
<label for="year">Year<select id="year"><option value="">All years</option>{options(sorted({c['year'] for c in events}))}</select></label>
<label for="quality">Quality category<select id="quality"><option value="">All categories</option>{options(QUALITY)}</select></label>
<label for="from-date">From date<input id="from-date" type="date"></label><label for="to-date">To date<input id="to-date" type="date"></label>
<label for="sort">Sort by<select id="sort"><option value="date">Date: upcoming first</option><option value="country">Country: A–Z</option><option value="quality">Quality category</option><option value="name">Conference: A–Z</option></select></label><button type="reset">Reset filters</button></form>
<div class="collection-heading"><h2>The collection</h2><p id="conference-count" role="status">{len(events)} conferences</p></div>
<p class="directory-note">Dates refer to the listed edition, including tutorials where the organizer includes them. Past editions remain useful for discovering recurring series. Confirm changes on the official website before making plans.</p>
<div id="conference-list" class="conference-list">'''
    order = {'In progress': 0, 'Upcoming': 1, 'Dates pending': 2, 'Past edition': 3}
    for c in sorted(events, key=lambda c: (order[status(c, checked)], c['start'] or '9999', c['name'])):
        attrs = ' '.join(f'data-{k}="{e(str(c[k] or ""))}"' for k in ('id','country','quality','start','end','year','name'))
        state = status(c, checked)
        if c['start']:
            first, last = date.fromisoformat(c['start']), date.fromisoformat(c['end'])
            date_html = f'<time datetime="{c["start"]}">{first:%d %b %Y}</time><span aria-hidden="true"> – </span><span class="sr-only"> to </span><time datetime="{c["end"]}">{last:%d %b %Y}</time>'
            date_badge = f'<span>{first:%b}</span><strong>{first:%d}</strong><span>{first:%Y}</span>'
        else:
            date_html = f'{c["year"]} · Exact dates to be announced'
            date_badge = f'<span>Dates</span><strong>—</strong><span>{c["year"]}</span>'
        body += f'''<article id="{e(c['id'])}" class="conference-card" {attrs}>
<div class="date-badge" aria-hidden="true">{date_badge}</div><div class="conference-content">
<div class="conference-meta"><span class="event-status">{state}</span><span>{e(c['city'])}, {e(c['country'])}</span></div>
<h3><a href="{e(c['url'])}">{e(c['name'])} <span aria-hidden="true">↗</span></a></h3><p class="full-name">{e(c['full_name'])}</p>
<p class="event-dates">{date_html}</p><p class="event-description">{e(c['description'])}</p>
<div class="event-footer"><span class="quality-tag">{e(c['quality'])}</span><a href="{e(c['source'])}">Official source ↗</a><span>Checked {c['checked']}</span></div>
<details class="quality-detail"><summary>Why this category?</summary><p>{e(c['quality_reason'])}</p></details></div></article>'''
    body += '''</div><div id="no-results" class="no-results" hidden><h3>No conferences match these filters.</h3><p>Try another country, broaden your dates, or reset the filters.</p><button id="clear-empty" type="button">Reset filters</button></div>
<section class="quality-guide" aria-labelledby="quality-heading"><p class="eyebrow">A guide, not a league table</p><h2 id="quality-heading">How we describe quality</h2><p>Categories are editorial judgments based on the series’ track record, scientific focus, programme, and organizers. They are not official rankings, acceptance-rate estimates, or guarantees of an individual talk’s quality. Industry forums serve a different purpose from research conferences.</p><dl>'''
    body += ''.join(f'<div><dt>{e(label)}</dt><dd>{e(description)}</dd></div>' for label, description in QUALITY.items())
    body += '</dl><p>This is a selective directory, not a complete global calendar. Each entry links to its organizer or institutional source. Dates pending means that an edition is announced but exact dates were not confirmed in the cited source.</p></section><noscript><p>All conferences are shown. Enable JavaScript to filter and sort the collection.</p></noscript>'
    shell('conferences/index.html', 'Quantum conferences', 'Explore quantum computing and information conferences by country, date, quality category, and research focus.', body, assets='<link rel="stylesheet" href="conferences.css"><script defer src="conferences.js"></script>')
