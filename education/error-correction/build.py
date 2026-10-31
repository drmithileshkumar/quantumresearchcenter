#!/usr/bin/env python3
"""Build the Quantum Error Correction course."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from course_builder import METHOD_GUIDE, Course, build
sys.path.insert(0, str(ROOT / "tools"))
from make_circuits import main as make_circuits

COURSE_TITLE = 'Quantum Error Correction'
COURSE_SUBTITLE = 'How to protect an unknown state and compute when operations can fail'
COURSE_ABOUT = 'You have stored an unknown qubit. An interaction with its environment may have changed it. How could you discover what went wrong without discovering the state you wanted to preserve? Starting with this question, we construct quantum codes, extract error syndromes, build logical operations, and account for the resources needed to make a computation reliable.'
COURSE_PREREQUISITES = 'Complete <a href="../information-theory/index.html">Quantum Information Theory</a> and the basic <a href="../computing/index.html">Quantum Computing</a> course, or bring equivalent knowledge of states, channels, reference systems, Pauli operators, and elementary circuits. Binary linear algebra and classical codes are developed as needed. Hardware knowledge is helpful but not required.'
COURSE_EXTRA = '<p>The ten chapters form a cumulative argument. Chapters 1–2 establish what recovery must preserve. Chapters 3–5 construct and analyze codes. Chapters 6–7 turn syndromes into decoding decisions and local geometric codes. Chapters 8–10 confront faulty recovery, universal gates, and the cost of a reliable computation.</p><p>Work through the small cases before reading the general statement. Each chapter includes three worked checks and ten exercises with hints and reasoned solutions. Deep no-go and threshold theorems are stated with scope and references; numerical models are labeled as models. The course is an initial draft textbook, not a hardware performance forecast.</p><p>Conventions: qubits are ordered left to right; Pauli subscripts label physical positions; binary arithmetic is modulo two; stabilizer syndromes use 0 for eigenvalue +1 and 1 for −1. Code parameters are [[n,k,d]]. Gate conjugations use UPU†, and fidelity means squared fidelity. Unless specified otherwise, syndrome measurements and recovery are ideal through Chapter 7.</p><p>Reference reading: <a href="https://arxiv.org/abs/0904.2557">Daniel Gottesman, An Introduction to Quantum Error Correction and Fault-Tolerant Quantum Computation</a>, and <a href="https://arxiv.org/abs/1302.3428">Barbara Terhal, Quantum Error Correction for Quantum Memories</a>. The final chapter links a reproducible numerical verifier and proposes a resource-estimation project.</p>'

COURSE = Course(
    root=ROOT,
    title=COURSE_TITLE,
    tagline='Protecting information and computation',
    subtitle=COURSE_SUBTITLE,
    about=COURSE_ABOUT,
    prerequisites=COURSE_PREREQUISITES,
    extra=COURSE_EXTRA,
    description='Quantum error correction and fault-tolerant computing: codes, syndromes, decoding, logical gates, and resource estimates.',
    resources='<nav class="book-resources" aria-label="Related courses"><a href="../information-theory/index.html">Quantum Information Theory</a><a href="../computing/index.html">Quantum Computing</a></nav>',
    search_example='stabilizer, syndrome, or threshold',
    guide=METHOD_GUIDE,
    prepare=make_circuits,
)

if __name__ == '__main__':
    build(COURSE)
