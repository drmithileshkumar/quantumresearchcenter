#!/usr/bin/env python3
"""Report broken external links on the site: python3 scripts/check_links.py [--host arxiv.org]."""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', 'vendor', 'source', 'templates'}
# The site's own canonical URLs are checked locally by build.py; loopback links belong to the local editor.
SKIP_HOSTS = {'quantumresearch.center', '127.0.0.1:8765', 'localhost'}
AGENT = 'QRC-LinkCheck/1.0 (mailto:mail.qrc@gmail.com)'
# Servers that refuse automated requests but are known to work in a browser.
BLOCKS_BOTS = {401, 403, 405, 429}

def site_links():
    found = defaultdict(set)
    for page in ROOT.rglob('*.html'):
        if SKIP_DIRS & set(page.relative_to(ROOT).parts):
            continue
        for url in re.findall(r'href="(https?://[^"#]+)', page.read_text(errors='ignore')):
            if urlsplit(url).netloc not in SKIP_HOSTS:
                found[url].add(str(page.relative_to(ROOT)))
    return found

def status(url):
    for method in ('HEAD', 'GET'):
        try:
            with urlopen(Request(url, method=method, headers={'User-Agent': AGENT}), timeout=25) as response:
                return response.status
        except HTTPError as error:
            if method == 'HEAD' and error.code in (403, 405, 501):
                continue
            return error.code
        except (URLError, TimeoutError, OSError) as error:
            return f'unreachable ({getattr(error, "reason", error)})'
    return 'unreachable'

def check_host(urls):
    # One request per second per host keeps the check polite (arXiv asks for restraint).
    results = {}
    for url in urls:
        results[url] = status(url)
        time.sleep(1)
    return results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', help='only check links to this host')
    args = parser.parse_args()
    links = site_links()
    by_host = defaultdict(list)
    for url in sorted(links):
        host = urlsplit(url).netloc
        if not args.host or host == args.host:
            by_host[host].append(url)
    results = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for part in pool.map(check_host, by_host.values()):
            results.update(part)
    broken = {u: s for u, s in results.items() if not (isinstance(s, int) and (s < 400 or s in BLOCKS_BOTS))}
    blocked = {u: s for u, s in results.items() if s in BLOCKS_BOTS}
    print(f'{len(results)} external links checked; {len(broken)} broken; {len(blocked)} refused automated requests (not counted).')
    for url, code in sorted(broken.items()):
        pages = sorted(links[url])
        print(f'  {code}  {url}\n        on {pages[0]}' + (f' and {len(pages) - 1} more' if len(pages) > 1 else ''))
    return 1 if broken else 0

if __name__ == '__main__':
    sys.exit(main())
