"""End-of-chapter summaries: a short list of key takeaways shown before the practice section.

Each course keeps its takeaways in content/summary.json as {"<chapter stem>": ["takeaway", ...]}.
Items are trusted course content and may contain inline HTML and TeX (\\( … \\)). A chapter with no
entry gets no summary section, so courses can adopt summaries one chapter at a time.
"""
import json
from pathlib import Path


def load(root, stems=None):
    """Read and validate a course's summaries; stems, if given, are the chapters that exist."""
    path = Path(root) / 'content/summary.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    for stem, items in data.items():
        if stems is not None and stem not in stems:
            raise ValueError(f'Summary for unknown chapter: {stem}')
        if not isinstance(items, list) or not items or any(not isinstance(x, str) or not x.strip() for x in items):
            raise ValueError(f'Summary for {stem} must be a non-empty list of takeaways')
    return data


def render(items):
    """Return the summary section for one chapter, or '' when it has no takeaways."""
    if not items:
        return ''
    takeaways = ''.join(f'<li>{item}</li>' for item in items)
    return ('<section class="chapter-summary" id="chapter-summary" aria-labelledby="chapter-summary-heading">'
            '<h2 id="chapter-summary-heading">Summary</h2>'
            f'<ul class="takeaway-list" aria-label="Key takeaways">{takeaways}</ul></section>')
