"""Fill {{NAME}} slots in a page template; filled values are never rescanned, so TeX braces stay intact."""
from pathlib import Path
import re


def fill(template, values):
    return re.sub(r'\{\{([A-Z_]+)\}\}', lambda match: str(values[match.group(1)]), Path(template).read_text())
