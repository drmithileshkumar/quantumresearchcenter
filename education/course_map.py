"""Shared, metadata-driven mind map for course overview pages."""
from html import escape


def render_course_map(title, chapters):
    branches = []
    for i, chapter in enumerate(chapters, 1):
        stem = chapter['stem']
        sections = chapter.get('parts') or chapter['sections']
        topics = ''.join(
            f'<li><a href="{escape(stem)}.html#{escape(section["id"])}">'
            f'{escape(section["title"])}</a></li>'
            for section in sections
        )
        number = f'{i:02}' if stem != 'appendices' else 'A–E'
        branches.append(
            f'<li class="topic-map-branch"><a class="topic-map-section" '
            f'href="{escape(stem)}.html"><span>{number}</span>'
            f'{escape(chapter["title"])}</a><ul>{topics}</ul></li>'
        )
    return (
        '<nav class="chapter-topic-map" aria-labelledby="topic-map-heading">'
        '<h2 id="topic-map-heading">Course map</h2>'
        '<p class="topic-map-hint">Select a chapter or topic to start reading.</p>'
        f'<div class="topic-map-root">{escape(title)}</div>'
        '<ul class="topic-map-branches">' + ''.join(branches) + '</ul></nav>'
    )


def render_chapter_map(title, chapter):
    """Normalize the course manifests into linked section and topic branches."""
    branches = []
    for section in chapter.get('parts') or chapter['sections']:
        if chapter.get('parts'):
            topics = [topic for topic in chapter['sections']
                      if topic.get('part_id') == section['id']]
        elif 'topics' in section:
            topics = section['topics']
        else:
            topics = [dict(id=section['id'].replace('section-', 'topic-') + f'-{i}',
                           title=label)
                      for i, label in enumerate(section.get('subsections', []), 1)]
        links = ''.join(
            f'<li><a href="#{escape(topic["id"])}">{escape(topic["title"])}</a></li>'
            for topic in topics
        )
        branches.append(
            f'<li class="topic-map-branch"><a class="topic-map-section" '
            f'href="#{escape(section["id"])}"><span>{escape(section.get("number", ""))}</span>'
            f'{escape(section["title"])}</a>' + (f'<ul>{links}</ul>' if links else '') + '</li>'
        )
    return (
        '<nav class="chapter-topic-map" aria-labelledby="topic-map-heading">'
        '<h2 id="topic-map-heading">Chapter map</h2>'
        '<p class="topic-map-hint">Select a topic to jump to its explanation.</p>'
        f'<div class="topic-map-root">{escape(title)}</div>'
        '<ul class="topic-map-branches">' + ''.join(branches) + '</ul></nav>'
    )
