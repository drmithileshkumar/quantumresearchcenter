#!/usr/bin/env python3
"""Build the Interpretations of Quantum Mechanics course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import METHOD_GUIDE, Course, build
sys.path.insert(0, str(ROOT / "tools"))
from make_circuits import main as make_circuits

COURSE_TITLE = 'Interpretations of Quantum Mechanics'
COURSE_SUBTITLE = 'What the quantum formalism says, what it leaves open, and how to compare physical accounts'
COURSE_ABOUT = 'A detector records one result. A unitary calculation produces a correlated state. How should we connect those two descriptions? This advanced course follows that question through concrete experiments, mathematical constraints, and competing accounts of states, events, and probability.'
COURSE_PREREQUISITES = 'Complete <a href="../foundations/index.html">Quantum Foundations</a>, or bring equivalent knowledge of state vectors, density operators, tensor products, projective measurement, and probability. <a href="../information-theory/index.html">Quantum Information Theory</a> is useful preparation for channels and distinguishability, but is not required throughout. Chapter 6 also uses elementary gradients and continuity equations.'
COURSE_EXTRA = '<p>Ten draft chapters develop a common measurement model before comparing operational accounts, consistent histories, Everett, Bohmian mechanics, objective collapse, relational quantum mechanics, and QBism. Bell and contextuality constraints, quantum-state ontology, and quantum observers supply tests of what each account can claim. This is a parallel advanced path after Quantum Foundations; Quantum Error Correction is not a prerequisite.</p><p>Each chapter has three worked checks, ten exercises with hints and reasoned solutions, a summary, and linked primary-source or research-review readings. Explanations are conversational, but claims are tied to equations and explicit assumptions. No interpretation is presented as an experimentally selected winner. Modified collapse dynamics is distinguished from empirically equivalent readings of the usual formalism.</p><p>Conventions: finite-dimensional examples use normalized kets and left-to-right tensor order; |±⟩=(|0⟩±|1⟩)/√2; X, Y, and Z are the usual Pauli matrices; logarithms are natural unless specified. Conditional states require nonzero conditioning probability. Ideal coherent-control thought experiments are distinguished from practical macroscopic experiments. Continuous-variable models state their restricted physical scope.</p><p>Read with an assumption ledger: identify the calculation, the physical postulates, the theorem assumptions, and the interpretive conclusion. The final chapter offers a comparative research practicum.</p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='States, outcomes, and physical reality',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='Advanced interpretations of quantum mechanics: measurement, decoherence, Bell, Everett, Bohmian mechanics, collapse, relational accounts, QBism, and quantum observers.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../information-theory/index.html">Quantum Information Theory</a><a href="../foundations/index.html">Quantum Foundations</a></nav>',
    search_example='decoherence, Everett, or contextuality',
    guide=METHOD_GUIDE,
    prepare=make_circuits,
)

if __name__ == '__main__':
    build(COURSE)
