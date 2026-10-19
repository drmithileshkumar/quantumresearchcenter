# Quantum Programming course

## Scope and teaching approach

This course completes the progression Quantum Computing → Quantum Algorithms →
Quantum Programming. Qiskit is the primary implementation environment. Assume
knowledge from the first two courses, but introduce Python and software concepts
through examples rather than requiring an additional programming course.

All sixteen chapters contain initial draft lessons with runnable companions.
Keep code, tested dependency versions, and validation records synchronized.
Follow the user's current instructions over earlier plans.

Preserve the concrete, cumulative teaching philosophy of the computing course:
start with an understandable problem, predict the mathematical result, construct
its circuit, write the program, test it, and explain discrepancies. Develop
concepts inside the problem that needs them, using an original voice inspired by
Feynman's explanatory intimacy and Susskind's conceptual discipline. Do not turn
chapters into API catalogs or unexplained collections of code snippets.

Use short formal titles. Chapter 1 compares language families and design principles,
including imperative and functional approaches, embedded frameworks, type and
ownership rules, no-cloning, reversibility, measurement, intermediate languages,
and hardware independence. Explain that Qiskit is a Python SDK, not a standalone
quantum programming language. The following chapters develop Qiskit programming.

## Software and scientific standards

- Verify APIs against current official Qiskit documentation when writing lessons.
  Record and pin the versions actually tested. Do not invent version requirements
  for outlines, and do not copy legacy execution APIs into new examples unchecked.
- Distinguish the SDK, Aer, and IBM Runtime. Begin with local simulation; distinguish
  simulator access to amplitudes from information obtainable by physical measurement.
- Use V2 primitive interfaces where applicable. Explain Sampler and Estimator input
  and result structures through complete examples, not names alone.
- Make register order, bit-string order, tensor-product order, and gate order explicit.
- Specify ancilla initialization and cleanup. Test superpositions as well as basis
  inputs; probability agreement alone does not establish coherent equivalence.
- Separate programming errors, approximation error, sampling uncertainty, and noise.
  State numerical tolerances and statistical reasoning.
- Distinguish ideal circuits from compiled circuits. Account for layout, observable
  mapping, routing, native operations, and resource changes.
- Hardware capabilities differ from abstract circuit support. Verify dynamic-circuit
  support for the selected backend. Never promise free hardware access or fixed quotas.
- Never embed credentials. Keep hardware submission explicit and separate from local
  examples; do not automatically spend execution credits or submit student jobs.
- Provide runnable code, expected mathematical behaviour, and genuine tests. Do not
  fabricate hardware results. State when an example was only simulated.
- Use named algorithms from the earlier courses as applications; do not repeat their
  entire theory. Explain the implementation choices and costs that the code adds.
- Treat variational performance and error mitigation as conditional claims. Distinguish
  empirical results from general guarantees.

## Presentation and exercises

Use the established course reader and circuit diagrams. Draw quantum wires, gates,
controls, measurements, and classical records rather than generic flowcharts.
Explain composite boxes and their implementation costs. Use accessible captions
and the existing SVG/MathJax conventions; visually inspect new illustrations.

Full lessons should include prediction prompts, working examples, debugging tasks,
and exercises with reasoned solutions. Test from the first program; the testing
chapter consolidates that practice. Increase project complexity gradually and
finish with a reproducible implementation and an honest evaluation.

## Repository workflow

- `chapters.json` defines order, questions, prerequisites, examples, and section plans.
- `content/*.html` holds canonical manuscripts; root HTML pages are generated.
- Build with `python3 education/programming/build.py`.
- Shared styles and MathJax come from `../computing/assets/`. Reader storage uses
  its own `qp-book-` namespace and the search index contains only this course.
- Keep metadata, manuscript headings, navigation, catalog, and sitemap synchronized.
- Update only necessary site-level outputs. Preserve manual edits to student and
  research pages rather than blindly rebuilding unrelated HTML.
- Check local links, anchors, duplicate IDs, JavaScript syntax, and relevant code
  examples. Do not commit or publish unless requested.
