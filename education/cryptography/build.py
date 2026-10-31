#!/usr/bin/env python3
"""Build the Quantum Cryptography course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import METHOD_GUIDE, Course, build

COURSE_TITLE = 'Quantum Cryptography'
COURSE_SUBTITLE = 'From quantum signals to secret keys'
COURSE_ABOUT = 'Alice and Bob want a shared secret even when Eve controls their communication channel. Learn what quantum mechanics contributes, how a protocol turns observations into a security bound, and where implementation assumptions enter.'
COURSE_PREREQUISITES = 'Complete <a href="../information/index.html">Quantum Information</a> or bring equivalent knowledge of qubits, measurement, tensor products, and elementary probability. Density operators and binary entropy are reviewed as needed. No prior cryptography course is required.'
COURSE_EXTRA = '<p>This six-chapter course develops security definitions, quantum attacks, entanglement-based proof ideas, reconciliation, extraction, optical implementations, and cryptographic limitations through 54 linked subsections. Each chapter includes learning objectives, mathematical derivations, worked calculations, and ten exercises with hints and reasoned solutions.</p><p><strong>Suggested pace:</strong> twelve study sessions, two per chapter. In the first session, derive the equations and work through the examples. In the second, solve the problems and reproduce the numerical calculations. Chapters 1–2 build the protocol; Chapters 3–4 build the security argument; Chapters 5–6 test its physical assumptions and extend the cryptographic tasks.</p><p>All logarithms are base two unless marked ln. Bits are column vectors over the binary field when used with parity matrices. Quantum systems are ordered Alice, Bob, then Eve unless stated otherwise. Trace distance includes the factor one half. Examples specify whether a result is derived, a theorem is invoked, or a numerical model is assumed.</p><p><a href="examples/bb84_lab.py">Download the Python laboratory</a> to simulate BB84 attacks, inspect sampling bounds, reconcile short strings, apply Toeplitz hashes, and calculate decoy yields and key budgets. It runs with the Python standard library. The <a href="tools/check_examples.py">verification companion</a> exhaustively checks small codes and hash families and reproduces the numerical examples.</p><p>The <a href="03-entanglement.html#rate-explorer">interactive rate explorer</a> shows how error and reconciliation overhead change the ideal asymptotic key fraction. The <a href="06-beyond-qkd.html#section-6-3">final project</a> specifies deliverables and an assessment rubric. Simulations and illustrative budgets are clearly separated from general quantum security proofs.</p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='From quantum signals to secret keys',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='Quantum cryptography: BB84, entanglement, security definitions, privacy amplification, practical devices, and cryptographic limits.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../information-theory/index.html">Quantum Information Theory</a><a href="../foundations/index.html">Quantum Foundations</a></nav>',
    search_example='BB84, entropy, or decoy states',
    guide=METHOD_GUIDE,
    credit='Quantum Research Center',
    styles=('assets/course.css',),
    scripts=('assets/explorer.js',),
)

if __name__ == '__main__':
    build(COURSE)
