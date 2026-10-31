#!/usr/bin/env python3
"""Build the Quantum Programming course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import BASIC_GUIDE, Course, build

COURSE_TITLE = 'Quantum Programming'
COURSE_SUBTITLE = 'From circuit specifications to reproducible programs'
COURSE_ABOUT = 'Turn quantum computations into executable programs with Qiskit. Each chapter has a runnable companion, explicit mathematical predictions, and checks. The sequence progresses from language design and local simulation to compilation, dynamic circuits, noise, and a reproducible project.'
COURSE_PREREQUISITES = 'Quantum Computing and Quantum Algorithms, or equivalent knowledge. Python concepts are introduced through the examples.'
COURSE_EXTRA = '<p><a href="TESTING.md">Tested environment and verification</a> · <a href="requirements.txt">Pinned dependencies</a></p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='Programs, circuits, and execution',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='An interactive introduction to quantum programming with Qiskit by Mithilesh Kumar.',
    resources='<nav class="book-resources" aria-label="Prerequisite courses"><a href="../computing/index.html">Quantum Computing</a><a href="../algorithms/index.html">Quantum Algorithms</a></nav>',
    search_example='Qiskit, measurement, or transpilation',
    guide=BASIC_GUIDE,
)

if __name__ == '__main__':
    build(COURSE)
