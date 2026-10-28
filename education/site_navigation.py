"""Primary site navigation shared by the site, editorial, and course templates."""
from html import escape
import posixpath

SECTIONS = (('index.html', 'Home'), ('news/index.html', 'News'),
            ('education/index.html', 'Education'), ('research/index.html', 'Research'),
            ('tools/index.html', 'Tools'))


def site_navigation(source, cls='site-nav', extra=''):
    """Render visible labels and a current section, using paths relative to this page."""
    active = 'index.html' if source == 'index.html' else source.split('/')[0] + '/index.html'
    links = []
    for target, label in SECTIONS:
        href = posixpath.relpath(target, posixpath.dirname(source) or '.')
        current = ''
        if target == active:
            current = ' aria-current="' + ('page' if source == target else 'location') + '"'
        links.append(f'<a href="{escape(href, quote=True)}"{current}>{label}</a>')
    return f'<nav class="primary-nav {escape(cls, quote=True)}" aria-label="Site navigation">'+''.join(links)+extra+'</nav>'


COURSE_NAV = site_navigation('education/course/index.html')
