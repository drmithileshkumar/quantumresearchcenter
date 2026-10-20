"""Stamp course styles and scripts so readers do not reuse stale theme assets."""
from hashlib import sha256
from pathlib import Path
import re


def version_assets(source, directory):
    directory = Path(directory)

    def stamp(match):
        attribute, url = match.groups()
        target = directory / url
        if not target.is_file():
            return match.group(0)
        digest = sha256(target.read_bytes()).hexdigest()[:10]
        return f'{attribute}="{url}?v={digest}"'

    return re.sub(r'(href|src)="((?![a-z]+:|//)[^"?#]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"', stamp, source)


def version_pages(directory):
    """Run after generated scripts are written so every digest matches its final bytes."""
    directory = Path(directory)
    for page in directory.glob('*.html'):
        source = page.read_text()
        stamped = version_assets(source, directory)
        if stamped != source:
            page.write_text(stamped)
