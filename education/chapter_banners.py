"""Chapter banners shared by the course builders.

A course keeps a ``banners.py`` with a ``BANNERS`` dict (stem -> (draw function, alt text))
and writes ``assets/banners/<stem>.svg``. ``render`` inlines the SVG so its ``.cb-*``
classes (education/computing/assets/book.css) follow the light and dark themes.
"""
import html
import importlib.util
import re
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def _module(course_root):
    spec = importlib.util.spec_from_file_location(f'banners_{Path(course_root).name}', Path(course_root) / 'banners.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render(course_root, stem):
    """The chapter's banner figure, or '' when the course or chapter has none."""
    course_root = Path(course_root)
    path = course_root / 'assets' / 'banners' / f'{stem}.svg'
    if not (course_root / 'banners.py').exists() or not path.exists():
        return ''
    entry = _module(str(course_root)).BANNERS.get(stem)
    if not entry:
        return ''
    svg = path.read_text()
    if re.search(r'<script|\son\w+=|\sid=', svg):
        raise ValueError('Chapter banner must be a plain SVG without scripts, handlers or ids: ' + path.name)
    svg = svg.replace('<svg', f'<svg role="img" aria-label="{html.escape(entry[1], quote=True)}"', 1)
    return f'<figure class="chapter-banner">{svg}</figure>'
