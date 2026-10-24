# Quantum Error Correction

Ten advanced draft chapters following Quantum Information Theory and basic
Quantum Computing. Original conversational explanations develop calculations from
concrete tasks, with 30 worked checks and 100 end-of-chapter exercises, hints,
and reasoned solutions. Coverage progresses through exact correction, stabilizers,
CSS codes, logical distance, syndromes, surface codes, fault containment, universal
logical gates, and resource estimation.

Edit `content/*.html`, `chapters.json`, `content/exercises.json`, and
`content/summary.json`. Root HTML and the search index are generated. The course
uses the existing site reader and MathJax, with isolated `qec-book-` reading storage.

```sh
python3 education/error-correction/build.py
python3 education/checks/check_courses.py --course error-correction
python3 education/error-correction/tools/check_examples.py
python3 scripts/build.py
```

Build/check dependencies are `beautifulsoup4`; the numerical verifier uses `numpy`.
The verifier exhaustively checks distances of the small five-qubit, Steane, and
L=3 toric codes and directly tests parity circuits and gate-injection branches.
It does not certify a real hardware threshold or a complete fault-tolerant gadget.

Keep physical qubit order, generator order, syndrome signs, Pauli phases, and
noise assumptions explicit. Initial syndrome extraction is ideal; noisy gadgets
enter in Chapter 8. Distillation and threshold results have stated assumptions and
references. Resource numbers are hypothetical planning examples, not measurements.
Preserve the distinction between a demonstrated circuit identity, a stated theorem,
a finite computational certificate, and a model-based estimate.

## Circuit diagrams

Fourteen original SVG circuits illustrate the relevant operations in Chapters 1–9.
The build regenerates them from `tools/make_circuits.py`; captions and alternative
text live beside each figure in the canonical manuscripts. The numerical verifier
checks the encoding, complete repetition recovery, X and Z parity instruments,
five-qubit XZZXI readout, hook propagation, and both T-injection branches.
SVGs use a light drawing surface, while the surrounding reader follows the site theme.
