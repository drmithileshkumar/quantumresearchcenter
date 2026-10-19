# Writing the Quantum Information course

## Scope

These instructions govern `education/information/`. All sixteen chapters contain initial draft lessons, worked examples, and solved
problems. Continue improving mathematical dependencies and distinguish cited
theorems from results derived in the text. Follow current user directions.

The central question is: what can we learn, preserve, transform, and communicate
when information is carried by quantum systems? The course is self-contained:
assume no prior quantum mechanics, information theory, probability, or linear
algebra course. Quantum Computing is complementary, not a prerequisite.

## Teaching philosophy

Use the concrete reasoning and explanatory intimacy associated with Feynman and
the cumulative conceptual discipline associated with Susskind, in an original
voice. Build ideas inside the problems that require them. Begin with a physical
or operational question, work a small example, reveal the obstacle, construct the
needed mathematics, and then generalize. Do not start with a mathematical survey
or send readers to an appendix for prerequisites needed by the main argument.

Return to a few examples: two nonorthogonal states, a Bell pair, a noisy qubit,
and a short message sent through a channel. Each return must answer a stronger
question. Make calculations reproducible by an attentive reader. Use connected
prose and short formal chapter titles. Do not mistake familiarity with terminology
for understanding or use a list of definitions in place of an explanation.

The progression is distinguishability → classical information → quantum states →
composite systems → mixed states → operations → measurement → discrimination →
constraints → protocols → entropy → compression → entanglement transformations →
error correction → communication → cryptography.

For each chapter, maintain its motivating question, starting knowledge, anchor
example, conceptual obstacle, construction, decisive calculation, application,
limits, understanding checks, and handoff. Metadata currently records questions,
prerequisites, examples, and section plans; expand the rest during manuscript work.
Section counts may change to serve the explanation rather than a fixed template.

## Dependency discipline

- Introduce probability, conditioning, logarithms, and classical entropy through
  messages and coding examples. Explain repeated-source assumptions.
- Develop amplitudes, complex numbers, vectors, inner products, and the probability
  rule before using their abstract names as reasoning shortcuts.
- Construct tensor products from paired configurations. Establish entanglement by
  amplitudes, not just correlated counts in one measurement basis.
- Derive density operators from averaged predictions, reduced states from joint
  probabilities, and purification from explicit joint-state constructions.
- Explain channels through ancillas, interaction, and discarding before stating
  operator-sum or complete-positivity conditions. General measurements follow these
  constructions. Basic projective measurement is available in Chapter 3.
- Chapter 8 develops accessible information operationally; entropy-based bounds may
  be stated with clear scope and revisited after Chapter 11, not silently depend on
  quantum entropy before it is defined.
- Introduce spectra, entropy, trace distance, fidelity, typicality, Schmidt
  coefficients, and majorization in the tasks that require them.
- Keep quantum communication introductory in this edition. Mark results whose full
  proof lies beyond the main development, without hiding assumptions or claiming
  that a special example proves a capacity theorem.

## Mathematical and physical standards

- Separate physical postulates, mathematical consequences, interpretations, and
  experimental evidence. Mathematical consistency alone does not establish a
  physical law.
- State subsystem and basis order, normalization, operation order, and conditioning.
  Distinguish amplitudes, outcome probabilities, and recorded classical values.
- Distinguish a pure superposition, a classical ensemble, and a reduced state.
  A density operator generally has many ensemble decompositions.
- Separate measurement probabilities from the state-update instrument. A POVM
  alone does not specify the post-measurement state.
- Specify prior probabilities and error or inconclusive-outcome criteria in
  discrimination tasks. State the resources and assumptions of impossibility claims.
- Account for classical communication, entanglement, transmitted systems, and
  consumed resources in protocols. Teleportation does not clone or signal instantly.
- Explain negative conditional entropy operationally. Distinguish correlations,
  entanglement, and information obtainable by a specified measurement.
- State compression and capacity assumptions: source/channel model, independent
  uses where applicable, asymptotic regime, error criterion, and assistance.
  Do not replace a regularized capacity with a single-use expression without grounds.
- Explain which error set a code corrects. A bit-flip repetition code is not a code
  correcting arbitrary single-qubit errors.
- Distinguish a protocol demonstration from a security proof. State authentication,
  device assumptions, adversary model, finite-data effects, and the security goal.
- Verify worked examples directly and consult primary sources for nontrivial theorem
  statements and attribution. Do not fabricate citations or experimental results.

## Presentation and exercises

Reuse the computing course's reader style. Prefer actual circuits for protocols
and operations; introduce circuit notation before using it. State diagrams and
probability distributions may support state and information arguments. Do not use
generic flowchart boxes as substitutes for physical operations or calculations.
Use the existing SVG and MathJax conventions, accessible captions, clear register
labels, and distinguishable classical records. Visually inspect new diagrams.

Full chapters need prediction prompts, worked examples, and questions with reasoned
solutions. Include misconceptions and limits, not just mechanical substitutions.
Outlines need not contain fabricated exercises, illustrations, or completed proofs.

## Files and build

- `chapters.json`: order, questions, prerequisites, examples, and section plans.
- `content/*.html`: canonical manuscripts; root chapter pages are generated.
- Build with `python3 education/information/build.py`.
- Shared CSS and MathJax come from `../computing/assets/`; deploy the courses together.
- `assets/book.js` uses isolated `qi-book-` reading storage; search data is course-local.
- Keep headings, manifests, navigation, search, catalog, and sitemap consistent.
- Update only necessary site outputs. Preserve manual student and research edits.
- Check local links, anchors, heading IDs, JavaScript syntax, and mathematical examples
  appropriate to the change. Do not commit or publish unless requested.
