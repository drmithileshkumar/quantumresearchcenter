#!/usr/bin/env python3
"""Build the Quantum Information Theory course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import METHOD_GUIDE, Course, build

COURSE_TITLE = 'Quantum Information Theory'
COURSE_SUBTITLE = 'Distinguishability, communication, and the limits of quantum resources'
COURSE_ABOUT = 'Quantum Foundations explains the structure of the theory. Here we ask what that structure permits: how well can states be distinguished, how much information survives a noisy channel, and when can lost information be recovered? Work from explicit finite-dimensional examples to operational bounds, coding theorems, and small research investigations.'
COURSE_PREREQUISITES = 'Complete <a href="../foundations/index.html">Quantum Foundations</a> and <a href="../information/index.html">Quantum Information</a>, or bring equivalent knowledge of density operators, tensor products, partial traces, measurements, and elementary entropy. You should be comfortable with complex linear algebra and probability. Operator norms, convex optimization, and asymptotic reasoning are developed where needed.'
COURSE_EXTRA = '<p>Chapters 1–3 establish the mathematical tools. Chapters 4–7 study entanglement, compression, and communication. Chapters 8–10 turn to recovery, resource theories, and reproducible research. All logarithms are base two; systems are finite-dimensional unless explicitly stated. Fidelity means the squared fidelity throughout.</p><p>Plan for one or two study sessions per chapter, plus time for proofs and exercises. First attempt the prediction and worked checks, then solve the end-of-chapter problems. The final chapter offers three bounded projects with benchmark answers and clear limits on what a numerical experiment establishes.</p><p>Reference texts: <a href="https://jhwatrous.github.io/books-and-courses.html">John Watrous, The Theory of Quantum Information</a> and <a href="https://arxiv.org/abs/1604.07450">John Preskill, Quantum Shannon Theory</a>. Manuscripts here use original explanations and examples; theorem references appear beside the statements they support.</p>'

COURSE_EXTRA += '<p><strong>Continue the advanced sequence:</strong> <a href="../error-correction/index.html">Quantum Error Correction</a> turns the conditions for recovery into code constructions, protected logical operations, and explicit reliability budgets.</p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='Information, resources, and limits',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='Advanced quantum information theory: distinguishability, channels, entropy, recovery, and communication.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../foundations/index.html">Quantum Foundations</a><a href="../information/index.html">Quantum Information</a></nav>',
    search_example='trace distance, channel capacity, or recovery',
    guide=METHOD_GUIDE,
)

if __name__ == '__main__':
    build(COURSE)
