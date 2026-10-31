"""Build the website graph from public pages and their actual internal links."""
import hashlib
import html
import json
import posixpath
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

EXCLUDED = {'.git', '_site', 'content', 'source', 'vendor', 'templates', 'tests', 'node_modules', '.codex', '.agents'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.title = ''
        self.in_title = False
        self.public = False
        self.excluded = False
        self.chrome = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.public = True
        if tag == 'title': self.in_title = True
        if tag == 'meta' and (a.get('http-equiv', '').lower() == 'refresh' or
                             (a.get('name', '').lower() == 'robots' and 'noindex' in a.get('content', '').lower())):
            self.excluded = True
        if tag in {'nav', 'header', 'footer', 'aside'}: self.chrome.append(tag)
        if tag == 'a' and a.get('href'): self.links.append((a['href'], bool(self.chrome)))

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag in self.chrome:
            self.chrome = self.chrome[:len(self.chrome) - 1 - self.chrome[::-1].index(tag)]

    def handle_data(self, data):
        if self.in_title: self.title += data


def collect(root, outputs, site_url):
    manifest = root / 'scripts/.generated-manifest.json'
    managed = set(json.loads(manifest.read_text())) if manifest.exists() else set()
    sources = {p.relative_to(root).as_posix(): p.read_text() for p in sorted(root.rglob('*.html'))
               if not EXCLUDED.intersection(p.relative_to(root).parts)
               and not (p.relative_to(root).as_posix() in managed and p.relative_to(root).as_posix() not in outputs)}
    sources.update({name: text for name, text in outputs.items() if name.endswith('.html')})
    # Include the graph itself without turning its fallback directory into hundreds of edges.
    sources['website-map/index.html'] = '<html><head><title>Website map</title></head></html>'
    pages = {name: Page(text) for name, text in sorted(sources.items())}
    pages = {name: page for name, page in pages.items() if page.public and not page.excluded}
    nodes = []
    for name, page in pages.items():
        section = name.split('/')[0] if '/' in name else 'home'
        nodes.append({'id': name, 'title': page.title.split(' | Quantum Research Center')[0].strip() or name,
                      'section': section, 'url': '../' + name})
    edges = {}
    for source, page in pages.items():
        for href, navigation in page.links:
            url = urlsplit(href)
            if url.scheme and url.scheme not in {'http', 'https'}: continue
            if url.netloc and url.netloc != urlsplit(site_url).netloc: continue
            path = unquote(url.path)
            if not path: continue
            target = posixpath.normpath(path.lstrip('/') if path.startswith('/') or url.netloc
                                       else posixpath.join(posixpath.dirname(source), path))
            if path.endswith('/') or target == '.': target = (target.rstrip('.') + '/index.html').lstrip('/')
            if target not in pages or target == source: continue
            key = tuple(sorted((source, target)))
            # A substantive link takes precedence over a repeated navigation link.
            edges[key] = edges.get(key, True) and navigation
    return {'nodes': nodes, 'edges': [{'source': a, 'target': b, 'navigation': nav}
                                     for (a, b), nav in sorted(edges.items())]}


def compact(graph):
    """Encode edges by node position; the browser derives each page's section and URL from its path."""
    position = {node['id']: i for i, node in enumerate(graph['nodes'])}
    return {'nodes': [[node['id'], node['title']] for node in graph['nodes']],
            'edges': [[position[edge['source']], position[edge['target']], int(edge['navigation'])] for edge in graph['edges']]}


def render_site_graph(root, outputs, site_url, logo, navigation):
    graph = collect(root, outputs, site_url)
    sections = {}
    for node in graph['nodes']: sections.setdefault(node['section'], []).append(node)
    outputs['website-map/data.js'] = 'window.SITE_GRAPH=' + json.dumps(compact(graph), ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c') + ';\n'
    digest = hashlib.sha256(outputs['website-map/data.js'].encode()).hexdigest()[:10]
    directory = ''.join(f'<li><a href="sections/{html.escape(section)}.html">{html.escape(section)}</a><small>{len(nodes)} pages</small></li>' for section, nodes in sorted(sections.items()))
    values = {'LOGO': logo('editorial-brand', '../index.html'),
              'NAV': navigation('website-map/index.html', 'editorial-nav'),
              'DATA_URL': f'data.js?v={digest}',
              'DIRECTORY': directory, 'COUNT': str(len(graph['nodes'])),
              'CANONICAL': site_url + '/website-map/'}
    template = (root / 'website-map/template.html.in').read_text()
    for key, value in values.items(): template = template.replace('{{' + key + '}}', value)
    outputs['website-map/index.html'] = template
    # Each section lists its pages as ordinary links, so the directory works without JavaScript at any size.
    section_template = (root / 'website-map/section.html.in').read_text()
    for section, nodes in sections.items():
        source = f'website-map/sections/{section}.html'
        values = {'LOGO': logo('editorial-brand', '../../index.html'), 'NAV': navigation(source, 'editorial-nav'),
                  'SECTION': html.escape(section), 'COUNT': str(len(nodes)),
                  'DIRECTORY': ''.join(f'<li><a href="../../{html.escape(n["id"])}">{html.escape(n["title"])}</a></li>' for n in nodes)}
        page = section_template
        for key, value in values.items(): page = page.replace('{{' + key + '}}', value)
        outputs[source] = page
    return graph
