#!/usr/bin/env python3
"""Check every public page: local links and anchors resolve, and each page can be reached from the home page."""
import argparse
import posixpath
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from site_graph import EXCLUDED

ROOT = Path(__file__).resolve().parents[1]
# These scripts read the URL fragment to select a node, so their fragments are routes rather than element ids.
HASH_ROUTERS = {'map.js', 'frontier.js', 'deep-map.js'}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.document = False
        self.hidden = False
        self.routed = False
        self.ids = set()
        self.links = []
        self.resources = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.document = True
        if tag == 'meta' and (a.get('http-equiv', '').lower() == 'refresh' or
                             (a.get('name', '').lower() == 'robots' and 'noindex' in a.get('content', '').lower())):
            self.hidden = True
        for key in ('id', 'name'):
            if a.get(key) and (key == 'id' or tag == 'a'): self.ids.add(a[key])
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        elif a.get('href') and tag != 'base': self.resources.append(a['href'])
        if a.get('src'):
            self.resources.append(a['src'])
            if posixpath.basename(urlsplit(a['src']).path) in HASH_ROUTERS: self.routed = True


def target_of(source, reference):
    """Resolve a reference to (site path, fragment), or None if it leaves the site."""
    url = urlsplit(reference)
    if url.scheme or url.netloc: return None
    path = unquote(url.path)
    if not path: return source, url.fragment
    target = posixpath.normpath(path.lstrip('/') if path.startswith('/') else posixpath.join(posixpath.dirname(source), path))
    if path.endswith('/') or target == '.': target = posixpath.normpath(posixpath.join(target, 'index.html'))
    return target, url.fragment


def load_pages(root):
    pages = {}
    for path in sorted(Path(root).rglob('*.html')):
        name = path.relative_to(root).as_posix()
        if EXCLUDED.intersection(name.split('/')): continue
        page = Page(path.read_text(errors='ignore'))
        if page.document: pages[name] = page
    return pages


def problems(root):
    root = Path(root)
    pages = load_pages(root)
    found = []
    def exists(target):
        return target in pages or (root / target).is_file() or (root / target / 'index.html').is_file()
    for name, page in pages.items():
        for reference in dict.fromkeys(page.links + page.resources):
            resolved = target_of(name, reference)
            if not resolved: continue
            target, fragment = resolved
            if not exists(target):
                found.append(f'{name}: broken link {reference}')
            elif fragment and target in pages and not pages[target].routed and fragment not in pages[target].ids:
                found.append(f'{name}: broken anchor {reference}')
    reached = set()
    pending = ['index.html']
    while pending:
        name = pending.pop()
        if name in reached or name not in pages: continue
        reached.add(name)
        for reference in pages[name].links:
            resolved = target_of(name, reference)
            if resolved: pending.append(resolved[0])
    for name, page in pages.items():
        if name not in reached and not page.hidden:
            found.append(f'{name}: no links lead here from the home page')
    return len(pages), found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=ROOT, help='site directory (default: the repository)')
    args = parser.parse_args()
    count, found = problems(args.root)
    for problem in found: print(problem)
    if found: sys.exit(f'{len(found)} problems across {count} pages.')
    print(f'{count} pages checked: all local links resolve and every page is reachable.')


if __name__ == '__main__':
    main()
