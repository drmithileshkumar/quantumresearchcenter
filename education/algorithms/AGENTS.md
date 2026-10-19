# Writing the Quantum Algorithms course

## Scope

These instructions govern `education/algorithms/`. This is a continuation of
Quantum Computing. Assume the knowledge developed in that course, but no further
mathematics or physics courses. Follow the user's current instructions when the
scope changes. All eleven chapters now contain initial draft lessons. Keep development status
and chapter metadata current as explanations and validation improve.
Do not present outline pages as completed instruction.

## Teaching philosophy

Use the explanatory intimacy and concrete reasoning associated with Feynman and
the cumulative conceptual discipline associated with Susskind, in an original
voice. Begin with a problem the reader can understand; work through a small
example, expose the obstacle, construct a solution, then name and generalize it.
Build mathematics inside the argument that needs it. Do not substitute jargon,
an appendix prerequisite, or an appeal to authority for an explanation.

Carry the recurring examples from small circuits to general input sizes. Show
amplitude calculations, phase conventions, measurement outcomes, and resource
counts. Small examples motivate general results; they do not prove scalability.
Use connected prose and short formal headings. Let explanatory dependencies
determine the amount of space and number of sections, not a fixed template.

## Organization by techniques

Chapter 1, **Quantum Algorithmic Thinking**, introduces the design process:
formulate the problem, specify access, encode the useful property, engineer
interference, choose the readout, prove correctness, and account for resources.
Use Deutsch’s problem as a recurring design case, rather than repeating the
introductory course as a survey. Distinguish a small illustration from an algorithm
for a family of inputs.

The technique chapters follow:
2. Coherent Computation
3. Phase Encoding
4. Fourier Methods
5. Amplitude Manipulation
6. Quantum Walks
7. Operator Embedding
8. Polynomial Transformations
9. Evolution Engineering
10. Variational Methods
11. Adaptive Measurement

These are overlapping toolkits. Named algorithms are applications or compositions,
not additional technique categories. Standard phase estimation combines controlled
powers, kickback, and inverse QFT; standard amplitude estimation combines amplification
and phase estimation. Explain these dependencies rather than teach each from scratch.

Revisit material from Quantum Computing with a stronger question; do not duplicate
its introductory derivations wholesale. Basic measurement and classical feedback
are already available before the final chapter. That chapter develops their
systematic use, rather than introducing prerequisites needed by earlier algorithms.
Define simple generator-based evolution in Quantum Walks when needed; the later
Evolution Engineering chapter develops its construction and error analysis.

For each chapter, maintain a driving question, explicit prerequisites, an anchor
example, a conceptual obstacle, a decisive calculation, an application, limits,
and a handoff to the next chapter. The chapter metadata records the first three;
expand the remaining planning details as each manuscript is developed.

## Correctness and resource accounting

- Specify the input, output, success criterion, access model, and promises before
  claiming an advantage. Distinguish state preparation from classical data access.
- Controlled oracle access and inverse access must be provided or constructed;
  they are not free consequences of an unknown black box.
- Separate query count, elementary gates, depth, qubits, precision, repetitions,
  postselection probability, classical processing, and output extraction costs.
- Explain norms, spectra, Hamiltonians, singular values, polynomials, and calculus
  through needed examples before general formulas use them.
- Track normalization, register order, gate order, workspace restoration, and
  global versus relative phase. State approximation and error assumptions.
- Distinguish proofs, stated theorems, heuristic strategies, empirical evidence,
  and open questions. Do not imply that variational or adiabatic methods give a
  general efficient solution to hard optimization problems.
- Compare algorithms under compatible input and output models. A quantum state
  encoding a vector is not a classical list of that vector's entries.
- Verify worked small instances directly. Use primary sources for theorem
  attribution and nontrivial claims; include qualifications and provenance.

## Presentation

Use the same reader layout and shared visual assets as the computing course.
Use actual circuit diagrams, not generic flowcharts. Label registers, controls,
measurement records, and composite subroutines. Explain that a box can represent
many elementary gates. Use SVG and the existing MathJax conventions, accessible
descriptions, and legible labels. Inspect any new diagrams visually.

When expanding a chapter, include predictions, complete worked calculations,
and problems with worked solutions. Include questions that expose limitations
or incorrect implementations. Do not fabricate exercises or solutions merely
to make an unfinished outline look complete.

## Files and build

- `chapters.json`: chapter order, titles, questions, prerequisite notes, examples,
  and section/subsection plans.
- `content/*.html`: canonical chapter manuscripts. Edit these, not generated pages.
- `build.py`: reader generation; references shared CSS and MathJax from
  `../computing/assets/` and generates local search data.
- `assets/book.js`: reader controls with an independent `qa-book-` storage namespace.
- Build using `python3 education/algorithms/build.py`.
- Keep chapter metadata, headings, links, navigation, and search in sync.
- The course is listed in `content/courses.json`; `scripts/build.py` includes its
  pages in the site sitemap. Preserve manually edited student pages when updating
  site-level outputs; do not blindly regenerate unrelated pages.
- Check local links, duplicate IDs, chapter order, and JavaScript syntax. Preserve
  unrelated user edits. Do not commit or publish unless asked.
