#!/usr/bin/env python3
"""Build the Quantum Hardware course."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import BASIC_GUIDE, Course, build

COURSE_TITLE = 'Quantum Hardware'
COURSE_SUBTITLE = 'From physical qubits to reliable quantum processors'
COURSE_ABOUT = 'How does a physical device realize the states, gates, and measurements used by a quantum algorithm? Develop energy levels, control, coupling, readout, and noise through concrete examples, then examine the principal hardware platforms, their infrastructure, and their scaling constraints.'
COURSE_PREREQUISITES = 'The <a href="../computing/index.html">Quantum Computing course</a> or equivalent familiarity with qubits, gates, and measurement. Atomic, optical, and circuit physics are introduced through the devices that require them.'
COURSE_EXTRA = '<p>Each platform is examined through the same questions: what stores a qubit, how is it prepared, controlled, coupled, and measured, what causes errors, and what limits scaling? Numerical examples are illustrative models, not claims about a current commercial processor.</p>'

def check_figures():
    for figure in json.loads((ROOT / 'content/figures.json').read_text()):
        if not (ROOT / 'assets/figures' / f'{figure["name"]}.svg').is_file():
            raise ValueError('Missing figure; regenerate using figures.py: ' + figure['name'])

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='Devices, control, and architecture',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='An interactive introduction to quantum hardware by Mithilesh Kumar.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../computing/index.html">Quantum Computing</a><a href="../algorithms/index.html">Quantum Algorithms</a><a href="../programming/index.html">Quantum Programming</a><a href="../information/index.html">Quantum Information</a></nav>',
    search_example='transmon, Rabi, or readout',
    guide=BASIC_GUIDE,
    styles=('assets/hardware.css',),
    prepare=check_figures,
)

if __name__ == '__main__':
    build(COURSE)
