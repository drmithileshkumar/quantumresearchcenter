"""Build the frontier maps from content/frontiers/*.json: python3 frontiers/build.py [--check]."""
import json
import shutil
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'education'))
from site_navigation import site_navigation
from site_logo import site_logo
from asset_versions import version_assets

STATUSES = {
    'established': ('Established', 'Proved, with a source.'),
    'partial': ('Partial', 'Settled in some cases only.'),
    'conjectured': ('Conjectured', 'Widely expected, not proved in general.'),
    'open': ('Open', 'Unresolved.'),
    'claimed': ('Claimed', 'A recent result, not yet independently confirmed.'),
    'refuted': ('Refuted', 'The statement shown is false.'),
}
FRONTIER = {'partial', 'conjectured', 'open', 'claimed'}
RELATIONS = {
    'depends': ('Relies on', 'Needed by'),
    'narrows': ('Narrows', 'Narrowed by'),
    'related': ('See also', 'See also'),
}
ROW, GROUP_GAP, ROOT_X, BRANCH_DX, LEAF_DX, WIDTH = 28, 30, 570, 135, 265, 1140
RIGHT, LEFT = ('detection', 'conversion'), ('measures', 'multipartite')


def validate(data):
    """Reject a map whose status lacks evidence or whose links lead nowhere."""
    ids = [n['id'] for n in data['nodes']]
    assert len(ids) == len(set(ids)), 'duplicate node id'
    known = set(ids)
    for n in data['nodes']:
        assert n.get('sources'), f"{n['id']} has no source"
        assert set(n['sources']) <= set(data['papers']), f"{n['id']} cites an unknown paper"
        if n.get('kind') == 'topic':
            assert 'status' not in n, f"{n['id']} is a topic and cannot have a status"
        else:
            assert n.get('status') in STATUSES, f"{n['id']} has an invalid status"
            assert n.get('parent') in known, f"{n['id']} has an unknown parent"
        if n.get('status') in FRONTIER:
            assert n.get('unknown') or n['status'] == 'open', f"{n['id']} does not say what is unknown"
        for link in n.get('links', []):
            assert link['to'] in known and link['rel'] in RELATIONS, f"{n['id']} has an invalid link"
    assert set(data['papers']) <= {s for n in data['nodes'] for s in n['sources']}, 'unused paper'


def layout(data):
    """Place the map deterministically: the root in the middle, branches out to each side."""
    kids = {}
    for n in data['nodes']:
        kids.setdefault(n.get('parent'), []).append(n)
    place, heights = {}, []
    for branches in (RIGHT, LEFT):
        heights.append(sum(len(kids[b]) for b in branches) * ROW + GROUP_GAP)
    height = max(heights) + 2 * ROW
    place['entanglement'] = (ROOT_X, height / 2)
    for side, branches, total in ((1, RIGHT, heights[0]), (-1, LEFT, heights[1])):
        y = (height - total) / 2 + ROW / 2
        for branch in branches:
            first = y
            for leaf in kids[branch]:
                place[leaf['id']] = (ROOT_X + side * LEAF_DX, y)
                y += ROW
            place[branch] = (ROOT_X + side * BRANCH_DX, (first + y - ROW) / 2)
            y += GROUP_GAP
    return place, height


def glyph(status):
    if status == 'established': return '<circle class="g-fill" r="5"/>'
    if status == 'partial': return '<circle class="g-ring" r="6"/><path class="g-half" d="M0-6A6 6 0 0 0 0 6Z"/>'
    if status == 'conjectured': return '<circle class="g-ring g-dash" r="7"/>'
    if status == 'open': return '<circle class="g-ring g-strong" r="8"/>'
    if status == 'claimed': return '<path class="g-ring" d="M0-7 7 0 0 7-7 0Z"/>'
    return '<path class="g-cross" d="M-5-5 5 5M5-5-5 5"/>'


def curve(a, b):
    mid = (a[0] + b[0]) / 2
    return f'M{a[0]} {a[1]}C{mid} {a[1]} {mid} {b[1]} {b[0]} {b[1]}'


def render_svg(data):
    place, height = layout(data)
    edges, nodes = [], []
    for n in data['nodes']:
        if n.get('parent'):
            edges.append(f'<path class="edge" data-to="{n["id"]}" d="{curve(place[n["parent"]], place[n["id"]])}"/>')
        for link in n.get('links', []):
            edges.append(f'<path class="cross-link" hidden data-a="{n["id"]}" data-b="{link["to"]}" d="{curve(place[n["id"]], place[link["to"]])}"/>')
    for n in data['nodes']:
        x, y = place[n['id']]
        topic = n.get('kind') == 'topic'
        right = x > ROOT_X
        anchor = 'middle' if topic else ('start' if right else 'end')
        dx = 0 if topic else (16 if right else -16)
        dy = -16 if topic else 4
        status = n.get('status')
        frontier = ' frontier' if status in FRONTIER else ''
        mark = '<circle class="g-topic" r="9"/>' if topic else glyph(status)
        kind = 'topic' if topic else status
        label = f'{escape(n["title"])}' + (f' ({STATUSES[status][0]})' if status else '')
        nodes.append(f'<a class="node n-{kind}{frontier}" href="{n["id"]}/index.html" data-id="{n["id"]}" transform="translate({x} {y})"><title>{label}</title><circle class="hit" r="13"/>{mark}'
                     f'<text x="{dx}" y="{dy}" text-anchor="{anchor}">{escape(n["label"])}</text><g class="pips" transform="translate({-5 if right or topic else 1} 11)"></g></a>')
    return (f'<svg id="frontier" viewBox="0 0 {WIDTH} {height:g}" data-width="{WIDTH}" data-height="{height:g}" role="group" aria-label="Map of {escape(data["title"])}. Each node links to a page; the directory beside it lists them all.">'
            + ''.join(edges) + ''.join(nodes) + '</svg>')


def head(title, description, prefix, extra=''):
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">'
            f'<title>{escape(title)} | Quantum Research Center</title><meta name="description" content="{escape(description, quote=True)}"><link rel="icon" href="{prefix}icons/icon.svg">'
            f'<script src="{prefix}education/computing/assets/theme.js"></script><script src="{prefix}navigation.js"></script><link rel="stylesheet" href="{prefix}styles.css">{extra}</head>')


def legend():
    return ''.join(f'<li><svg viewBox="-10 -10 20 20" class="n-{key}" aria-hidden="true">{glyph(key)}</svg><span><b>{label}</b> {escape(text)}</span></li>' for key, (label, text) in STATUSES.items())


def directory(data, kids):
    out = ''
    for branch in RIGHT[:1] + LEFT[:1] + RIGHT[1:] + LEFT[1:]:
        title = next(n['title'] for n in data['nodes'] if n['id'] == branch)
        out += f'<details><summary>{escape(title)}</summary><ul>'
        for n in kids[branch]:
            out += f'<li><a href="{n["id"]}/index.html" data-node="{n["id"]}">{escape(n["title"])}</a> <small>{STATUSES[n["status"]][0]}</small></li>'
        out += '</ul></details>'
    return out


def deep_links(data):
    return ''.join(f'<p>Deep map: <a href="{d["id"]}/index.html">{escape(d["title"])}</a></p>' for d in load_deep_maps(data))


def render_map(data):
    kids = {}
    for n in data['nodes']:
        kids.setdefault(n.get('parent'), []).append(n)
    claims = [n for n in data['nodes'] if n.get('status')]
    frontier = sum(n['status'] in FRONTIER for n in claims)
    source = f'frontiers/{data["id"]}/index.html'
    payload = json.dumps({'id': data['id'], 'title': data['title'], 'nodes': data['nodes'], 'papers': data['papers'], 'statuses': {k: v[0] for k, v in STATUSES.items()}, 'frontier': sorted(FRONTIER), 'relations': RELATIONS}, ensure_ascii=False).replace('<', '\\u003c')
    html = (head(f'{data["title"]} frontier map', data['lede'], '../../', '<link rel="stylesheet" href="../frontier.css"><script defer src="../frontier.js"></script>')
            + f'<body><a class="skip-link" href="#main">Skip to content</a><header class="news-toolbar">{site_logo("news-brand", "../../index.html")}{site_navigation(source)}</header>'
            + f'<main id="main" tabindex="-1"><header class="frontier-intro"><div><p class="kicker">Frontier map</p><h1>{escape(data["title"])}</h1><p>{escape(data["lede"])}</p>{deep_links(data)}</div><p class="frontier-count">{len(claims)} claims and questions · {frontier} on the frontier · checked {data["checked"]}</p></header>'
            + '<div class="frontier-workspace"><aside class="frontier-tools" aria-label="Explore the map">'
            + '<label for="search">Find a node</label><input id="search" type="search" placeholder="Try distillable, PPT, AME…" autocomplete="off">'
            + '<label for="view">Show</label><select id="view"><option value="all">Everything</option><option value="frontier">Only the frontier</option><option value="unexplored">Only what I haven’t explored</option></select><p id="view-status" role="status"></p>'
            + f'<h2>What the field knows</h2><ul class="frontier-legend">{legend()}</ul>'
            + '<h2>My trail</h2><ol id="trail" class="trail" reversed></ol><p id="trail-empty" class="tool-note">Your path appears here as you jump between nodes.</p>'
            + '<details class="log-tools"><summary>Save or restore my notes</summary><div><p class="tool-note">Notes and trail are kept only in this browser. Back them up to keep them safe.</p><button id="log" type="button">Download research log</button><button id="backup" type="button">Download backup</button><label class="restore" for="restore">Restore from backup</label><input id="restore" type="file" accept="application/json"><p id="log-status" class="tool-note" role="status"></p></div></details>'
            + f'<details class="frontier-directory"><summary>Browse every node</summary><div>{directory(data, kids)}</div></details></aside>'
            + f'<section class="frontier-canvas" aria-label="Frontier map">{render_svg(data)}<div class="frontier-controls"><button id="zoom-in" type="button" aria-label="Zoom in">+</button><button id="zoom-out" type="button" aria-label="Zoom out">−</button><button id="fit" type="button">Fit map</button></div></section>'
            + '<aside id="detail" class="frontier-detail" aria-label="Selected node" aria-live="polite"><p class="kicker">Start anywhere</p><h2>Pick a node</h2><p>Hollow and diamond marks are the frontier. Selecting a node shows what is known, what is not, and what it connects to.</p></aside></div>'
            + '<p class="frontier-note">Statuses were checked against each source’s abstract or introduction, not by re-deriving the proofs. The map is a growing selection, so a missing topic means it has not been mapped yet, not that nothing is known about it.</p><noscript><p class="frontier-note">Without JavaScript, every node still opens as its own page. Notes and the trail need JavaScript.</p></noscript></main>'
            + f'<script id="frontier-data" type="application/json">{payload}</script></body></html>')
    return version_assets(html, ROOT / 'frontiers' / data['id'])


def render_node(data, n, incoming):
    source = f'frontiers/{data["id"]}/{n["id"]}/index.html'
    by_id = {x['id']: x for x in data['nodes']}
    status = n.get('status')
    kicker = STATUSES[status][0] if status else 'Topic'
    meaning = f'<p class="tool-note">{escape(STATUSES[status][1])}</p>' if status else ''
    unknown = f'<h2>Still unknown</h2><p>{escape(n["unknown"])}</p>' if n.get('unknown') else ''
    rows = [(RELATIONS[l['rel']][0], l['to']) for l in n.get('links', [])] + [(RELATIONS[l['rel']][1], other) for other, l in incoming]
    if n.get('parent'): rows.insert(0, ('Part of', n['parent']))
    rows += [('Includes', x['id']) for x in data['nodes'] if x.get('parent') == n['id']]
    links = ''.join(f'<li>{word}: <a href="../{to}/index.html">{escape(by_id[to]["title"])}</a></li>' for word, to in rows)
    papers = ''.join(f'<li><a href="{escape(data["papers"][k]["url"], quote=True)}">{escape(data["papers"][k]["title"])}</a>. {escape(data["papers"][k]["authors"])}, {data["papers"][k]["year"]}.</li>' for k in n['sources'])
    html = (head(n['title'], n['statement'], '../../../', '<link rel="stylesheet" href="../../frontier.css">')
            + f'<body><a class="skip-link" href="#main">Skip to content</a><header class="news-toolbar">{site_logo("news-brand", "../../../index.html")}{site_navigation(source)}</header>'
            + f'<main id="main" tabindex="-1" class="frontier-page"><p class="kicker"><a href="../index.html#{n["id"]}">{escape(data["title"])} map</a> · {kicker}</p><h1>{escape(n["title"])}</h1>{meaning}<p>{escape(n["statement"])}</p>{unknown}'
            + f'<h2>Connections</h2><ul>{links}</ul><h2>Sources</h2><ul>{papers}</ul><p class="tool-note">Checked {data["checked"]}.</p></main></body></html>')
    return version_assets(html, ROOT / 'frontiers' / data['id'] / n['id'])


def load_deep_maps(data):
    return [json.loads(p.read_text()) for p in sorted((ROOT / 'content/frontiers' / data['id']).glob('*.json'))]


def resolve_deep_map(parent, deep):
    """Return a deep map whose papers include those it reuses from the parent map, after checking it."""
    used = {s for n in deep['nodes'] for s in n.get('sources', [])}
    data = {**deep, 'papers': {**{k: v for k, v in parent['papers'].items() if k in used}, **deep['papers']}}
    validate(data)
    parents = {n['id']: n.get('parent') for n in deep['nodes']}
    roots = [i for i, p in parents.items() if p is None]
    assert roots == [deep['id']], 'a deep map needs one root, named after the map'
    for start in parents:
        seen, at = set(), start
        while at:
            assert at in parents and at not in seen, f'{start} does not reach the root'
            seen.add(at)
            at = parents[at]
    targets = {n['id'] for n in parent['nodes']}
    assert deep['id'] not in targets, 'a deep map cannot share a folder with a node'
    for n in deep['nodes']:
        assert set(n.get('map', [])) <= targets, f"{n['id']} links to a missing frontier node"
    return data


def outline(data, kids, by_id, parent):
    out = ''
    for n in kids.get(parent, []):
        status = STATUSES[n['status']][0] if n.get('status') else 'Topic'
        unknown = f'<p class="outline-unknown"><b>Still unknown:</b> {escape(n["unknown"])}</p>' if n.get('unknown') else ''
        sources = ' · '.join(f'<a href="{escape(data["papers"][k]["url"], quote=True)}">{escape(data["papers"][k]["authors"].split(",")[0])} {data["papers"][k]["year"]}</a>' for k in n['sources'])
        nested = outline(data, kids, by_id, n['id'])
        out += (f'<li id="outline-{n["id"]}"><h3><a href="#{n["id"]}">{escape(n["title"])}</a> <small>{status}</small></h3><p>{escape(n["statement"])}</p>{unknown}'
                f'<p class="outline-sources">{sources}</p>' + (f'<ul>{nested}</ul>' if nested else '') + '</li>')
    return out


def render_deep_map(parent, deep):
    """A single page holding a collapsible map, which deep-map.js lays out, and the same content as an outline."""
    data = resolve_deep_map(parent, deep)
    kids = {}
    for n in data['nodes']:
        kids.setdefault(n.get('parent'), []).append(n)
    by_id = {n['id']: n for n in data['nodes']}
    source = f'frontiers/{parent["id"]}/{data["id"]}/index.html'
    claims = [n for n in data['nodes'] if n.get('status')]
    frontier = sum(n['status'] in FRONTIER for n in claims)
    root = by_id[data['id']]
    payload = json.dumps({'id': data['id'], 'title': data['title'], 'nodes': data['nodes'], 'papers': data['papers'], 'statuses': {k: v[0] for k, v in STATUSES.items()}, 'frontier': sorted(FRONTIER), 'relations': RELATIONS, 'glyphs': {k: glyph(k) for k in STATUSES}, 'mapTitles': {n['id']: n['title'] for n in parent['nodes']}}, ensure_ascii=False).replace('<', '\\u003c')
    html = (head(data['title'], data['lede'], '../../../', '<link rel="stylesheet" href="../../frontier.css"><link rel="stylesheet" href="../../deep-map.css"><script defer src="../../deep-map.js"></script>')
            + f'<body><a class="skip-link" href="#main">Skip to content</a><header class="news-toolbar">{site_logo("news-brand", "../../../index.html")}{site_navigation(source)}</header>'
            + f'<main id="main" tabindex="-1"><header class="frontier-intro"><div><p class="kicker"><a href="../index.html">{escape(parent["title"])} frontier map</a> · Deep map</p><h1>{escape(data["title"])}</h1><p>{escape(data["lede"])}</p></div><p class="frontier-count">{len(claims)} ideas and questions · {frontier} on the frontier · checked {data["checked"]}</p></header>'
            + '<div class="frontier-workspace deep-workspace"><aside class="frontier-tools" aria-label="Explore the map">'
            + '<label for="search">Find an idea</label><input id="search" type="search" placeholder="Try Schmidt, Werner, steering…" autocomplete="off">'
            + '<label for="view">Show</label><select id="view"><option value="all">Everything</option><option value="frontier">Only the frontier</option></select><p id="view-status" role="status"></p>'
            + '<div class="deep-actions"><button id="expand-all" type="button">Expand all</button><button id="collapse-all" type="button">Collapse</button></div>'
            + f'<h2>What the field knows</h2><ul class="frontier-legend">{legend()}</ul>'
            + '<p class="tool-note">A ring with a number is a folded topic, and the number counts the ideas inside. Select it to open or fold it.</p></aside>'
            + '<section class="frontier-canvas" aria-label="Map of ideas"><svg id="frontier" role="group" aria-label="Map of the ideas used to classify bipartite entanglement. The outline below the map lists them all."></svg><div class="frontier-controls"><button id="zoom-in" type="button" aria-label="Zoom in">+</button><button id="zoom-out" type="button" aria-label="Zoom out">−</button><button id="fit" type="button">Fit map</button></div></section>'
            + f'<aside id="detail" class="frontier-detail" aria-label="Selected idea" aria-live="polite"><p class="kicker">Start anywhere</p><h2>{escape(root["title"])}</h2><p>{escape(root["statement"])}</p></aside></div>'
            + f'<section class="deep-outline" aria-labelledby="outline-title"><h2 id="outline-title">Every idea, in outline</h2><ul>{outline(data, kids, by_id, data["id"])}</ul></section>'
            + '<p class="frontier-note">Sources were checked against arXiv or Crossref records, and most statements against the source’s abstract. Standard results were written from the wider literature, so treat the cited paper as the place to confirm them. The map is a growing selection, so a missing idea means it has not been mapped yet.</p><noscript><p class="frontier-note">The interactive map needs JavaScript. The outline above holds the same content.</p></noscript></main>'
            + f'<script id="frontier-data" type="application/json">{payload}</script></body></html>')
    return version_assets(html, ROOT / 'frontiers' / parent['id'] / data['id'])


def render(data):
    """Return every page of one map as {path relative to the repository: html}."""
    validate(data)
    incoming = {}
    for n in data['nodes']:
        for link in n.get('links', []):
            incoming.setdefault(link['to'], []).append((n['id'], link))
    pages = {f'frontiers/{data["id"]}/index.html': render_map(data)}
    for n in data['nodes']:
        pages[f'frontiers/{data["id"]}/{n["id"]}/index.html'] = render_node(data, n, incoming.get(n['id'], []))
    for deep in load_deep_maps(data):
        pages[f'frontiers/{data["id"]}/{deep["id"]}/index.html'] = render_deep_map(data, deep)
    return pages


def load():
    return [json.loads(p.read_text()) for p in sorted((ROOT / 'content/frontiers').glob('*.json'))]


def main():
    check = '--check' in sys.argv[1:]
    stale = []
    for data in load():
        folder = ROOT / 'frontiers' / data['id']
        # Asset stamps resolve relative to each page, so its folder must exist before rendering.
        if not check:
            for n in data['nodes']:
                (folder / n['id']).mkdir(parents=True, exist_ok=True)
            for deep in load_deep_maps(data):
                (folder / deep['id']).mkdir(parents=True, exist_ok=True)
        pages = render(data)
        wanted = {str(Path(p).parent.name) for p in pages}
        for old in (folder.iterdir() if folder.exists() else []):
            if old.is_dir() and old.name not in wanted:
                stale.append(old.relative_to(ROOT).as_posix())
                if not check: shutil.rmtree(old)
        for path, html in pages.items():
            target = ROOT / path
            if not target.exists() or target.read_text() != html:
                stale.append(path)
                if not check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(html)
        print(f'{data["id"]}: {len(pages) - 1} nodes')
    if check and stale:
        sys.exit('Stale frontier pages: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
