#!/usr/bin/env python3
"""Build the Quantum Machine Learning course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import METHOD_GUIDE, Course, build

COURSE_TITLE = 'Quantum Machine Learning'
COURSE_SUBTITLE = 'Models, kernels, and honest advantage claims'
COURSE_ABOUT = 'Quantum machine learning asks whether quantum devices can learn from data better than classical learners. Answering it requires three separate arguments: what the model can express, whether it can be trained, and whether it generalises. This course builds all three, and keeps classical baselines in view throughout.'
COURSE_PREREQUISITES = 'Complete <a href="../information/index.html">Quantum Information</a> or bring equivalent knowledge of qubits, measurement, density operators, and tensor products, plus undergraduate linear algebra and probability. Familiarity with supervised learning and gradient descent is assumed; kernel methods are developed from scratch in Chapter 3.'
COURSE_EXTRA = '<p>This nine-chapter course develops the modelling language of quantum machine learning, the cost of encoding classical data, kernel methods and their quantum versions, variational models and their gradients, trainability limits, generalisation evidence, the classical algorithms that compete with quantum models, and a closing audit project. Each chapter includes learning objectives, derivations, worked examples, figures, and ten exercises with hints and reasoned solutions.</p><p><strong>Suggested pace:</strong> eighteen study sessions, two per chapter. In the first session, reproduce the derivations and work the examples. In the second, solve the problems and run the laboratory.</p><p><strong>Reading discipline.</strong> Every claim in this course is labelled as one of three things: a calculation you can check, an assumption that could fail, or a theorem quoted with its hypotheses. Where the field disagrees or where a result is numerical rather than general, the text says so.</p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='Models, kernels, and honest advantage claims',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='Quantum machine learning: data encoding, quantum kernels, variational models, trainability, generalisation, and honest claims about advantage.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../information/index.html">Quantum Information</a><a href="../algorithms/index.html">Quantum Algorithms</a></nav>',
    search_example='kernel, plateau, or encoding',
    guide=METHOD_GUIDE,
    credit='Quantum Research Center',
    lesson_note='This lesson includes explanations, worked examples, and problems with solutions. Results quoted from the literature are identified as theorems with their hypotheses.',
    draft_note=' contain draft lessons with worked examples and solved problems. These are teaching manuscripts in development; results quoted from the literature are stated with their hypotheses and sources.',
    styles=('assets/course.css',),
    scripts=('assets/explorer.js',),
)

if __name__ == '__main__':
    build(COURSE)
