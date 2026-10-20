"""Theme assets must stay fresh on every generated reader, including course pages."""
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import tempfile
import zipfile
import posixpath
import unittest
from urllib.parse import urlsplit, parse_qs

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'education'))
from asset_versions import version_assets, version_pages

class Assets(HTMLParser):
    def __init__(self,source):
        super().__init__();self.assets=[];self.redirect=False;self.feed(source)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='meta' and attrs.get('http-equiv','').lower()=='refresh':self.redirect=True
        if tag=='script' and 'src' in attrs:self.assets.append(attrs['src'])
        if tag=='link' and attrs.get('rel')=='stylesheet':self.assets.append(attrs['href'])

class AppearanceAssets(unittest.TestCase):
    def test_changed_local_asset_gets_a_new_url(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'theme.js';p.write_text('first')
            source='<script src="theme.js"></script><script src="https://example.org/remote.js"></script>'
            first=version_assets(source,directory)
            self.assertEqual(version_assets(first,directory),first)
            self.assertIn('https://example.org/remote.js',first)
            p.write_text('second')
            self.assertNotEqual(version_assets(source,directory),first)
            (Path(directory)/'index.html').write_text(first)
            version_pages(directory)
            self.assertEqual((Path(directory)/'index.html').read_text(),version_assets(source,directory))
    def test_offline_reader_versions_match_the_packaged_assets(self):
        with zipfile.ZipFile(ROOT/'education/computing/downloads/quantum-computing.zip') as archive:
            for name in archive.namelist():
                if not name.endswith('.html'):continue
                for asset in Assets(archive.read(name).decode()).assets:
                    url=urlsplit(asset)
                    if url.scheme or not url.query:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(name),url.path))
                    self.assertEqual(parse_qs(url.query).get('v'),[sha256(archive.read(target)).hexdigest()[:10]],(name,asset))
    def test_all_site_and_course_readers_load_fresh_theme_assets(self):
        pages=[]
        for p in ROOT.rglob('*.html'):
            if any(part in p.relative_to(ROOT).parts for part in ('content','source','vendor','templates')):continue
            doc=Assets(p.read_text())
            if doc.redirect or not any(urlsplit(a).path.endswith('styles.css') for a in doc.assets):continue
            pages.append(p)
            self.assertTrue(any(urlsplit(a).path.endswith('/theme.js') for a in doc.assets),str(p))
            for asset in doc.assets:
                url=urlsplit(asset)
                if url.scheme or url.netloc or not re.search(r'\.(css|js)$',url.path):continue
                target=(p.parent/url.path).resolve()
                self.assertTrue(target.is_file(),str(target))
                self.assertEqual(parse_qs(url.query).get('v'),[sha256(target.read_bytes()).hexdigest()[:10]],(str(p),asset))
        self.assertGreaterEqual(len(pages),100)

if __name__=='__main__':unittest.main()
