#!/usr/bin/env python3
"""Local editorial server: python3 scripts/news_editor.py, then /news/papers.html."""
import argparse
from datetime import datetime
import hmac
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import threading
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import build
from paper_news import validate

ROOT = Path(__file__).resolve().parents[1]
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.Lock()

def approve(ids):
    if not isinstance(ids, list) or not ids or any(not isinstance(i, str) for i in ids):
        raise ValueError('Select at least one paper.')
    path = ROOT / 'content/papers.json'
    original = path.read_text()
    data = json.loads(original)
    validate(data)
    if set(ids) - {p['id'] for p in data['papers']}:
        raise ValueError('The selection includes unknown papers. Reload the page.')
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
    for paper in data['papers']:
        if paper['id'] in ids and paper['status'] != 'approved':
            paper.update(status='approved', approved_on=today)
    validate(data)
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        output = build.render(json.loads((ROOT / 'content/research.json').read_text()))
        build.check_output(output)
        # Approval changes the news pages, the search index, and the sitemap.
        for name in [n for n in output if n.startswith('news/') or n == 'sitemap.xml']:
            target = ROOT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.tmp')
            temporary.write_text(output[name])
            os.replace(temporary, target)
        for target in build.orphaned_news_pages(output):
            build.remove_page(target)
    except Exception:
        path.write_text(original)
        raise
    return [p['id'] for p in data['papers'] if p['status'] == 'approved']

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def trusted_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def json_response(self, status, data):
        payload = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if not self.trusted_host():
            self.json_response(403, {'error': 'Use the localhost editor address.'}); return
        if urlsplit(self.path).path == '/api/news-editor':
            data = json.loads((ROOT / 'content/papers.json').read_text())
            self.json_response(200, {'token': TOKEN, 'approved': [p['id'] for p in data['papers'] if p['status'] == 'approved']})
            return
        if urlsplit(self.path).path.startswith('/api/'):
            self.json_response(404, {'error': 'Unknown endpoint.'}); return
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != '/api/news-editor/approve':
            self.json_response(404, {'error': 'Unknown endpoint.'}); return
        origin = self.headers.get('Origin')
        if not self.trusted_host() or (origin and origin != 'http://' + self.headers.get('Host', '')) or not hmac.compare_digest(self.headers.get('X-Editor-Token', ''), TOKEN):
            self.json_response(403, {'error': 'Reload the local editor before approving.'}); return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 16384: raise ValueError('Invalid request size.')
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict): raise ValueError('Invalid request.')
            with LOCK:
                approved = approve(body.get('ids'))
            self.json_response(200, {'approved': approved, 'news_url': '/news/index.html'})
        except (ValueError, KeyError) as exc:
            self.json_response(400, {'error': str(exc)})
        except Exception:
            self.json_response(500, {'error': 'Could not rebuild news. Check the editor terminal and retry.'})
            raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Local editor: http://127.0.0.1:{server.server_port}/news/papers.html', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
