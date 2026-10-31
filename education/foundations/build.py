#!/usr/bin/env python3
"""Build the Foundations of Quantum Mechanics course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import FOIL_GUIDE, Course, build

COURSE_TITLE = 'Quantum Foundations'
COURSE_SUBTITLE = 'Quantum theory derived from physical principles'
COURSE_ABOUT = 'Quantum mechanics is usually taught from postulates: Hilbert space, the Born rule, unitary evolution, and the tensor product, each stated and then used. This course derives them. It begins with the least a testable theory must say, adds a few general principles one at a time, and proves that quantum theory is the only theory satisfying them. Each principle is paired with a foil, a consistent theory that violates it, so you can see what the principle rules out.'
COURSE_PREREQUISITES = 'Comfort with vectors, matrices, and probability at the level of a first university course. No prior quantum mechanics is assumed; complex numbers, density matrices, and Hilbert space are constructed when the argument needs them. <a href="../information/index.html">Quantum Information</a> and <a href="../computing/index.html">Quantum Computing</a> are complementary courses.'
COURSE_EXTRA = '<p>The course works in finite dimensions, where every step can be stated precisely. Chapter 16 explains what changes for position and momentum, which need infinite-dimensional spaces. Chapters 1–4 set up the space of possible theories, Chapters 5–9 introduce the principles and derive the formalism, Chapters 10–15 develop its consequences, and Chapters 16–17 treat infinite dimensions and review what was assumed.</p><p>Experiments such as Stern–Gerlach appear as illustrations and tests of principles, never as their justification: a finite table of outcomes is consistent with many theories. Where a derivation rests on a theorem whose full proof lies beyond the course, the text states it, says what it assumes, and cites the source.</p>'

COURSE_EXTRA += '<p><strong>Continue the advanced sequence:</strong> <a href="../information-theory/index.html">Quantum Information Theory</a> develops distinguishability, entropy inequalities, communication limits, and recovery. Take the introductory Quantum Information course first if entropy and information-processing protocols are new to you.</p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='Quantum theory from principles',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='Foundations of quantum mechanics: quantum theory derived from physical principles, by Mithilesh Kumar.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../information/index.html">Quantum Information</a><a href="../computing/index.html">Quantum Computing</a></nav>',
    search_example='local tomography, Bloch ball, or Gleason',
    guide=FOIL_GUIDE,
)

if __name__ == '__main__':
    build(COURSE)
