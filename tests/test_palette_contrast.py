"""The shared palette must keep readable contrast in both themes (WCAG 2.2 AA)."""
from pathlib import Path
import re
import unittest

STYLES = (Path(__file__).resolve().parents[1] / 'styles.css').read_text()

def tokens(selector):
    block = re.search(re.escape(selector) + r'\{([^}]*)\}', STYLES).group(1)
    return dict(re.findall(r'(--[\w-]+):\s*(#[0-9a-fA-F]{6})\b', block))

def luminance(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

TEXT = ['ink', 'heading', 'ink-soft', 'muted', 'blue', 'blue-strong']
SURFACES = ['card', 'sidebar', 'surface', 'hover', 'blue-soft', 'blue-wash']

class PaletteContrast(unittest.TestCase):
    def check(self, palette, page_background):
        surfaces = {name: palette[f'--{name}'] for name in SURFACES} | {'page': page_background}
        for text in TEXT:
            for name, background in surfaces.items():
                with self.subTest(text=text, background=name):
                    self.assertGreaterEqual(ratio(palette[f'--{text}'], background), 4.5)
        for name in ('field-border', 'focus'):          # UI components and focus indicators: 3:1
            for surface, background in surfaces.items():
                with self.subTest(component=name, background=surface):
                    self.assertGreaterEqual(ratio(palette[f'--{name}'], background), 3)
        self.assertGreaterEqual(ratio(palette['--on-blue'], palette['--blue']), 4.5)

    def test_light_theme(self):
        self.check(tokens(':root'), '#ffffff')

    def test_dark_theme(self):
        light = tokens(':root')
        dark = light | tokens('html[data-theme=dark]')
        self.check(dark, '#0a0a10')

if __name__ == '__main__':
    unittest.main()
