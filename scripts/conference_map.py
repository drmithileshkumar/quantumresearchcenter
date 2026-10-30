"""Render the local Natural Earth basemap with accessible country controls."""
from collections import Counter
from html import escape
import json


def render_map(root, events, *, collection="conferences"):
    assert collection in {"conferences", "companies"}
    company_map = collection == "companies"
    heading = "A world of quantum companies" if company_map else "A world of quantum conferences"
    instructions = "Counts show listed companies by their documented base, not every office or customer location." if company_map else "Counts include upcoming, past, and undated editions unless filtered."
    filter_note = "Country counts reflect search and focus filters." if company_map else "Country counts reflect search, date, year, and quality filters."
    country_label = "company" if company_map else "conference"
    counts = Counter(event['country'] for event in events)
    if not counts:
        return ''
    data = json.loads((root / 'conferences/world-map.json').read_text())
    positions = {f['name']: f['point'] for f in data['features']}
    # Singapore is smaller than the 1:110m dataset's minimum polygon size.
    positions['Singapore'] = [(103.82 + 180) * 1000 / 360, (85 - 1.35) * 1000 / 360]
    # Move crowded markers out into the sea, with leader lines to the country.
    offsets = {'Ireland': (-33, -12), 'Netherlands': (-5, 27), 'Denmark': (18, -18), 'South Korea': (-9, -17), 'Japan': (17, 8)}
    if company_map:
        offsets.update({'United Kingdom': (-32, -28), 'France': (-38, 4), 'Netherlands': (-8, -35),
                        'Germany': (18, -20), 'Switzerland': (-22, 32), 'Austria': (19, 23),
                        'Finland': (12, -20), 'Israel': (14, 17)})
    paths = []
    for feature in data['features']:
        name = feature['name']
        attrs = f' class="map-land map-host" data-map-country="{escape(name)}"' if name in counts else ' class="map-land"'
        paths.append(f'<path{attrs} d="{feature["path"]}"><title>{escape(name)}</title></path>')
    markers = []
    for name, count in sorted(counts.items()):
        if name not in positions:
            continue  # The text controls still expose any country absent from this basemap.
        x, y = positions[name]
        dx, dy = offsets.get(name, (0, 0))
        mx, my = x + dx, y + dy
        markers.append(f'<g class="map-marker" data-map-country="{escape(name)}"><title>{escape(name)}: {count} {collection}</title><line x1="{x:.1f}" y1="{y:.1f}" x2="{mx:.1f}" y2="{my:.1f}"/><circle class="map-anchor" cx="{x:.1f}" cy="{y:.1f}" r="2.5"/><circle class="map-bubble" cx="{mx:.1f}" cy="{my:.1f}" r="12"/><text x="{mx:.1f}" y="{my:.1f}" dy=".35em" text-anchor="middle">{count}</text></g>')
    controls = ''.join(f'<button type="button" data-map-country="{escape(name)}" aria-pressed="false" disabled>{escape(name)} <span class="map-country-count">{count}</span></button>' for name, count in sorted(counts.items()))
    return f'''<section class="conference-map" aria-labelledby="world-map-heading"><div class="map-section-heading"><div><p class="eyebrow">Explore by country</p><h2 id="world-map-heading">{heading}</h2></div><button type="button" id="map-clear" hidden>Show all countries</button></div><p class="map-instructions">Select a highlighted country or use the country buttons below. {instructions}</p>
<div class="world-map-frame"><svg class="conference-world-map" viewBox="0 0 1000 435" aria-hidden="true" focusable="false"><g class="map-grid" fill="none">{''.join(f'<path d="M0 {y}H1000"/>' for y in (97,180,263,347))}</g>{''.join(paths)}{''.join(markers)}</svg></div>
<div class="map-caption"><p id="map-status" role="status">{len(events)} {collection} across {len(counts)} countries.</p><p>Map: <a href="https://www.naturalearthdata.com/about/terms-of-use/">Natural Earth</a> · Country-level locations</p></div><p class="map-count-note">Boundary view: India’s claimed extent of Jammu and Kashmir, including areas administered by Pakistan and China; not administrative control.</p><div class="map-country-buttons" aria-label="Choose a {country_label} country">{controls}</div><p class="map-count-note">{filter_note} Selecting a country narrows the list below.</p></section>'''
