# Quantum Computing — HTML book

The book-writing instructions are in [AGENTS.md](AGENTS.md). They define the intended teaching approach and conceptual progression; the historical outline below describes earlier organization and must be reconciled with those instructions as chapters are revised.

## Objective and Prerequisites

The book develops the foundations of quantum computing, from computability and reversible computation to quantum states, interference, and algorithms. It explains how an algorithm encodes a problem, transforms information, and produces a measurable answer, then examines the resources required to do so.

**No subject prerequisites are assumed.** Mathematical ideas and notation are developed in the context that needs them. Configurations, weighted transitions, and explicit path calculations precede vectors, matrices, inner products, complex numbers, and tensor products; these are introduced as useful descriptions of ideas the reader has already encountered.

No prior knowledge of quantum mechanics, formal logic, automata theory, computational complexity, or probability theory is assumed. Discrete probability, Boolean algebra, proof techniques, and algorithmic concepts are introduced before use. Calculus, differential equations, and thermodynamics are not prerequisites; the physical context of information erasure is explained without requiring a thermodynamic derivation.

The exposition should be intuitive without sacrificing precision. Motivation belongs in the examples and explanatory prose. Chapter, section, and subsection titles should identify their subject directly, using concise technical terms. Each new term must be explained when it enters the argument.

The HTML book now follows a ten-chapter structure. Old chapter URLs redirect to the corresponding chapters in the current book.

## Book Structure

Chapter 5, **Quantum Model of Computation**, introduces the global input–evolution–measurement model and single-qubit computation, with H–Z–H and variable-phase examples. Multi-qubit registers and controlled gates are introduced in Chapter 6. Composite Systems is now Chapter 6; Queries is Chapter 7; Circuits and Universality is Chapter 8; Search is Chapter 9; Complexity is Chapter 10. Earlier chapter URLs redirect to the new pages.


| Part | Chapters | Development |
| --- | --- | --- |
| I. Classical Foundations | 1–2 | Why we need procedures, and what information a procedure preserves or discards. |
| II. Quantum Foundations | 3–5 | Why amplitudes are needed, what measurement reveals, and what changes when systems are combined. |
| III. Algorithms and Resources | 6–9 | Design an observable distinction, amplify it, construct its operations, and assess the claimed advantage. |

The main route uses a small set of examples repeatedly. The question of reliable mathematical foundations motivates formal proof and models of computation. A reversible function evaluation connects classical calculation to quantum processing. A two-path experiment carries the transition from probability to amplitude. A four-item search grows into a complete algorithm. Readers should recognize these examples as the questions deepen.

## Detailed Contents

Numbers have the form `chapter.section.subsection`. Sections and subsections identify the mathematical and computational content. Their extent will follow the explanation required, rather than a fixed number of pages or examples.

## Chapter 1 — Logic and Computability

**Motivation:** Formal reasoning leads to questions about proof checking, search, and decision. Models of computation make these questions precise; their limits distinguish computability from efficiency. The chapter ends by introducing reversibility as a constraint on computational steps.

### 1.1 Formal Reasoning and Decision Problems

- **1.1.1** Axioms, inference rules, and proofs
- **1.1.2** Hilbert’s program and consistency
- **1.1.3** Proof checking, proof search, and decision

### 1.2 Models of Computation

- **1.2.1** Algorithms and termination
- **1.2.2** Configurations and transitions
- **1.2.3** Turing machines and universal computation

### 1.3 Computability and Its Limits

- **1.3.1** The Church–Turing thesis
- **1.3.2** The halting problem
- **1.3.3** Undecidability and incompleteness

### 1.4 From Computability to Reversibility

- **1.4.1** Deterministic and reversible transitions
- **1.4.2** Information loss in computation

**Outcome and transition:** Distinguish proof procedures, computability, and efficiency; explain deterministic and reversible transitions; motivate the Boolean and reversible constructions in Chapter 2.

## Chapter 2 — Boolean and Reversible Computation

**Motivation:** An AND gate outputs zero. Which input did it receive? A useful calculation can destroy the information needed to reconstruct its past.

### 2.1 Boolean Functions

- **2.1.1** Binary encodings
- **2.1.2** Boolean functions and truth tables
- **2.1.3** Polynomial representation over the binary field

### 2.2 Boolean Circuits

- **2.2.1** Polynomial evaluation by circuits
- **2.2.2** NAND universality
- **2.2.3** Irreversible Boolean operations

### 2.3 Information Erasure

- **2.3.1** Landauer’s principle
- **2.3.2** Logical reversibility and dissipation
- **2.3.3** Reversible function embeddings

### 2.4 Reversible Gates

- **2.4.1** Controlled reversible operations
- **2.4.2** CNOT, Toffoli, and Fredkin gates
- **2.4.3** Workspace and uncomputation

**Outcome and transition:** Reversible evaluation gives us a way to compute without merging distinct inputs. It remains classical. We now ask whether classical probabilities describe every physical way such a process can unfold.

## Chapter 3 — Probability Amplitudes and Interference

**Motivation:** Two devices give the same probabilities after one use, yet different outcomes after two uses. What did the one-step probabilities fail to describe?

### 3.1 Three Kinds of Transition

- **3.1.1** Deterministic transitions
- **3.1.2** Nondeterministic transitions
- **3.1.3** Probabilistic transitions

### 3.2 Sum and Product Rules

- **3.2.1** The product rule along a path
- **3.2.2** The sum rule across paths
- **3.2.3** States and steps

### 3.3 Signed Weights

- **3.3.1** Negative weights
- **3.3.2** Cancellation across paths
- **3.3.3** The Hadamard step

### 3.4 Complex Amplitudes and Interference

- **3.4.1** Complex weights
- **3.4.2** Interference and phase
- **3.4.3** Kets, measurement, and path information

**Outcome and transition:** Amplitudes provide a predictive description that probabilities alone cannot supply. This is an introduction through examples, not a derivation of quantum mechanics from classical uncertainty. We next make its state and measurement rules precise.

## Chapter 4 — Quantum States and Measurement

**Motivation:** The same prepared state can give a certain answer to one measurement and a random answer to another. How does the question asked determine what can be learned?

### 4.1 Vectors and Matrices

- **4.1.1** State vectors and ket notation
- **4.1.2** Inner products and transition amplitudes
- **4.1.3** Transition matrices
- **4.1.4** Adjoints and unitary operations

### 4.2 Postulates

- **4.2.1** State and evolution postulates
- **4.2.2** The measurement postulate
- **4.2.3** Repeated measurements on independently prepared states

### 4.3 Measurement in Other Bases

- **4.3.1** Changes of basis
- **4.3.2** Measurement in an orthonormal basis
- **4.3.3** Overlaps under unitary evolution

### 4.4 Observables and Distinguishability

- **4.4.1** Eigenvectors and eigenspaces
- **4.4.2** Hermitian operators and spectral projections
- **4.4.3** Nonorthogonal state discrimination

**Outcome and transition:** States, operators, and measurements now form one predictive framework. Before using it to compute, we must learn how the description changes when a system has several parts.

## Chapter 6 — Multi-Qubit Computation

**Motivation:** How do local gates, controlled gates, and measurements turn a joint register into a computation?

### 6.1 Registers and Operations

- **6.1.1** Tensor products and product bases
- **6.1.2** Product states
- **6.1.3** Joint amplitudes
- **6.1.4** Local and controlled gates

### 6.2 Entangled States

- **6.2.1** Bell-state preparation
- **6.2.2** Nonfactorization of amplitudes
- **6.2.3** Joint, marginal, and conditional probabilities

### 6.3 Quantum Information Constraints

- **6.3.1** Basis-state copying
- **6.3.2** The no-cloning theorem
- **6.3.3** Local states and no-signalling

### 6.4 Quantum Teleportation

- **6.4.1** Entanglement resources
- **6.4.2** Measurement and conditional corrections
- **6.4.3** State transfer and classical communication

**Outcome and transition:** The state of a register must be tracked as a whole, including any workspace. This sets up the central algorithmic question: how can a joint evolution reveal a desired property rather than merely produce a complicated state?

## Chapter 7 — Quantum Queries and Phase Kickback

**Motivation:** We can evaluate a function on a superposition, but measuring the result does not hand us all its values. What should a quantum algorithm try to reveal instead?

### 6.1 Function Queries

- **6.1.1** Constant and balanced Boolean functions
- **6.1.2** Classical query access
- **6.1.3** Reversible quantum oracles

### 6.2 Coherent Function Evaluation

- **6.2.1** Oracle action on superpositions
- **6.2.2** Register measurement
- **6.2.3** Workspace entanglement

### 6.3 Phase Kickback

- **6.3.1** Bit-flip eigenstates
- **6.3.2** Phase-oracle construction
- **6.3.3** Coherent uncomputation

### 6.4 Deutsch’s Algorithm

- **6.4.1** Interference and readout
- **6.4.2** Quantum and classical query counts
- **6.4.3** Preparation, oracle evaluation, and measurement

**Outcome and transition:** The first algorithm reveals a global property through interference. Its oracle assumptions are explicit. Next we construct such operations from elementary gates before using them for search.

## Chapter 8 — Quantum Circuits and Universality

**Motivation:** Writing down a transformation does not show that it is cheap to implement. How are the operations needed for queries and search built from elementary gates?

### 7.1 Circuit Representation

- **7.1.1** Wires and gate ordering
- **7.1.2** Circuits for query and search algorithms
- **7.1.3** Measurement and classical control

### 7.2 Gate Constructions

- **7.2.1** Pauli, Hadamard, and rotation gates
- **7.2.2** Controlled and entangling gates
- **7.2.3** Oracle and reflection circuits

### 7.3 Universal Gate Sets

- **7.3.1** Limits of local operations
- **7.3.2** Entangling gates and universality
- **7.3.3** Exact synthesis and approximation

### 7.4 Implementation Resources

- **7.4.1** Gate count, depth, and workspace
- **7.4.2** Connectivity and data preparation
- **7.4.3** Error accumulation and reliability

**Outcome and transition:** The gate constructions provide the operations for search and expose costs that a query count may hide.

## Chapter 9 — Quantum Search and Amplitude Amplification

**Motivation:** An oracle can change the sign of a marked amplitude without changing its probability. Which next operation turns that invisible mark into an advantage?

### 8.1 Four-Item Search

- **8.1.1** Search predicates and classical queries
- **8.1.2** State preparation and phase marking
- **8.1.3** Reflection and final amplitudes

### 8.2 Search Geometry

- **8.2.1** Good and bad subspaces
- **8.2.2** Initial success amplitude
- **8.2.3** Reflections and rotations

### 8.3 Grover Iteration

- **8.3.1** Amplitude evolution
- **8.3.2** Iteration count and overshooting
- **8.3.3** Unknown marked fraction and verification

### 8.4 General Amplitude Amplification

- **8.4.1** Arbitrary state preparation
- **8.4.2** Reflection using preparation and its inverse
- **8.4.3** Success probability and resource cost

**Outcome and transition:** Search combines the constructed oracles and reflections into an algorithm. Its query savings and gate costs can now be compared with the limits on any algorithm for the same problem.

## Chapter 10 — Computational Complexity and Quantum Advantage

**Motivation:** A reduction in oracle queries, a shorter circuit, and a faster physical computation are different claims. Which one has an algorithm established?

### 9.1 Resource Bounds

- **9.1.1** Input size and success criteria
- **9.1.2** Asymptotic notation
- **9.1.3** Query, gate, and space complexity

### 9.2 Complexity Classes

- **9.2.1** P, NP, and reductions
- **9.2.2** BPP and BQP
- **9.2.3** Factoring and search

### 9.3 Query Lower Bounds

- **9.3.1** Upper and lower bounds
- **9.3.2** Unstructured search optimality
- **9.3.3** Acceptance polynomials and approximate degree (optional)

### 9.4 Scope of Quantum Advantage

- **9.4.1** Algorithmic mechanisms and assumptions
- **9.4.2** Computability and readout limitations
- **9.4.3** Period finding and error correction: further topics

**Outcome and transition:** The reader can explain an algorithm’s mechanism, identify its assumptions, and distinguish an established advantage from an expectation. The book ends with questions that its foundations now make possible to study.

## Appendices

These topics remain available as supporting essays or appendices, with links from the point where their purpose is clear:

- **A. Automata and Memory:** finite automata, stacks, bounded tapes, and examples that distinguish their capabilities.
- **B. Grammars and Lambda Calculus:** grammars, the Chomsky hierarchy, lambda calculus, and connections between formalisms.
- **C. Linear Algebra Reference:** complex arithmetic, vector and matrix identities, tensor products, and notation used in the text.
- **D. Mixed States and General Measurements:** mixed states, general measurements, and inconclusive discrimination.
- **E. Polynomial Lower Bounds:** polynomial representations, approximate degree, and the OR/search connection.

These are not prerequisites to be completed before the main story can proceed. Each extension answers a specific question raised on that route.

## Exposition Guidelines

1. Start each chapter with a situation the reader can inspect, not a vocabulary list or a survey.
2. Let the failure or limitation of an existing explanation create the need for the next idea.
3. Use basic linear algebra directly, with brief reminders as needed. Develop additional mathematics and notation at their first substantive use.
4. Keep one primary argument per section. Subsections should advance that argument, not simply collect related facts.
5. Distinguish a motivating example from a general proof, a physical postulate from its consequences, and an abstract operation from its implementation.
6. Carry the same examples across chapter boundaries. Revisit them for a new purpose rather than restart their definitions.
7. Use a figure or animation only if it shows the step in the reasoning that the prose is asking the reader to understand.
8. Use concise subject titles at every level. Put motivating questions and conceptual connections in the prose.
9. Keep the manuscript, chapter metadata, and this outline aligned when changing the progression.

---

## Working with the current HTML book

Open **index.html** to read the book. This is a standalone static site: upload the extracted offline archive to any directory on your website. It does not require a server-side application, a CDN, or a package build on the host. Relative links work under a subdirectory as well as at the domain root.

For local HTTP preview, from the repository root:

```sh
python3 -m http.server 8000 --directory education/computing
```

Then open `http://localhost:8000/`. Opening `index.html` directly also works.

## Reading experience

- Nine rewritten chapters, 36 sections, 107 subsections, and five supporting appendices.
- Basic linear algebra is the only subject prerequisite; the text develops computational concepts and quantum notation as needed.
- Continuous serif prose with adjustable size, a linked hierarchical contents panel, local search, and chapter navigation.
- Twenty-four original SVG drawings: eleven Chapter 1 concept diagrams plus circuit and geometric figures, including NAND, reversible gates, uncomputation, Bell preparation, teleportation, Deutsch, and Grover circuits. Wide drawings scroll within the page on small screens.
- Local MathJax and four interactive examples: elementary gates, Bell preparation, phase kickback, and amplitude amplification.
- Chapter understanding checks with expandable answers; primary-source links for selected advanced results.
- No server application or remote math service is required. Print layout preserves the current experimental state.

Illustrations should use representative quantum states, weighted state graphs, or circuits. Avoid generic block or flow diagrams for new material.

## Edit and rebuild

`chapters.json` defines the chapter order, titles, and introductions. The matching files in `content/` are the canonical HTML manuscripts and JSON navigation manifests. `content/appendices.html` contains the supporting material. Edit manuscripts rather than generated root pages.

```sh
python3 build.py
python3 tools/validate.py
```

The builder requires Python 3 and Beautiful Soup. It generates chapter pages, contents, search data, and compatibility redirects for the previous chapter URLs. All builds are independent of `../html/`; the slide-import command has been removed to protect the rewritten manuscripts.

`assets/book.css` controls reading layout; `assets/book.js` controls navigation and search; `assets/experiments.js` powers the four interactive examples. Their markup is included in the chapter manuscripts.

The original vector diagrams are generated by:

```sh
python3 tools/draw_figures.py
```

Their SVG files live in `assets/figures/`. The Chapter 1 diagrams are generated by `tools/draw_logic_figures.py`, which is also called by the main figure generator. The generator uses only Python’s standard library. Font and MathJax files remain bundled under `assets/source/`, with their licenses.

All mathematics is typeset by MathJax, including figure labels. Write math in the book's TeX delimiters, `\(...\)`, in prose, JSON content, and figure labels alike. `svgmath.py` turns figure labels into SVG text carrying `data-tex` (pure math) or `data-math` (prose with math), with a Unicode fallback. `build.py` inlines every figure into its page so `assets/source/mathjax-config.js` can typeset those labels. Alt text and SVG descriptions use `svgmath.plain()`, a Unicode rendering of the same TeX.

The notation index (`notation.html`) is generated from `content/notation.json`. Each entry gives a symbol's TeX, how to read it aloud, its meaning, and the section that explains it (`section`). It may also give an earlier informal introduction (`intro`). When an entry has a `pattern`, `build.py` finds the symbol's first use in the chapter prose and prints a `Notation check` line if that comes before its explanation. Entries marked `prerequisite` are exempt.

## Design references

The reading typography is inspired by the [Feynman Lectures online edition](https://www.feynmanlectures.caltech.edu/III_01.html): serif prose, comfortable line spacing, and restrained presentation. The expandable contents and chapter navigation are inspired by [qubit.guide](https://qubit.guide/index). This book uses original styles and the user's own course content, not copied chapter text or assets from either reference.

## Browser checks

The optional interaction suite requires Node.js 22 or newer and Google Chrome:

```sh
node tools/browser-check.mjs
```

It checks the four interactive examples, navigation, search, font sizing, chapter structure, equations, drawing loads, and mobile layout. Screenshots are saved in the system temporary directory. Set `CHROME` to choose another Chrome executable.

Worked calculations can also be verified independently (requires NumPy):

```sh
python3 tools/check-mathematics.py
```

This checks the NAND construction, Bell preparation, the explicit Grover circuit, all Deutsch oracle cases, all teleportation corrections, and the general amplification probability formula.

## Learning aids and offline edition

`content/learning.json` supplies the nine chapter guides and 27 exercises. Keep the
`review` anchor for each exercise pointed at its explanation. `content/glossary.json`
contains short definitions and source links. `learning.py` renders these additions
at build time; edit these sources instead of the generated pages. The chapter
manuscripts and the author's introduction remain the source of the main narrative.

Run `python3 education/computing/build.py` from the repository root to rebuild all
pages, search data, learning resources, and `downloads/quantum-computing.zip`.
The archive includes local scripts, MathJax, fonts, figures, and license notices.
Extract the whole archive and open its `index.html`. Main-site and source-reference
links point online; no network is needed for the book itself. Fixed ZIP timestamps
keep identical builds reproducible. No build tools or manuscript files are bundled.

The reader progressively enhances native links and disclosure controls. JavaScript
adds search, glossary filtering, experiments, print expansion, and reading settings.
Text size and reading position use only browser local storage. The study guide has
a control to clear those values. Printing expands hints and solutions temporarily
and restores their state afterwards. Reduced-motion settings suppress transitions.

Validation: `python3 education/computing/tools/validate.py`,
`python3 education/computing/tools/check-learning.py`, and
`node education/computing/tools/browser-check.mjs` (requires Chrome and Node 22+).

`content/probing-questions.json` maps each subsection ID to three subject-specific
questions: `foundation`, `application`, and `challenge`. All three appear in a numbered list under “Problems,” without difficulty labels. The builder places these after the subsection’s explanation
and figures; the optional polynomial prompt remains inside its disclosure.
Missing prompts fail the build so newly added subsections cannot be overlooked.
Questions are also included in the book search index and offline edition.


## Subsection illustrations

From Chapter 5 onward, illustrations use circuit diagrams. Circuit specifications in `content/illustrations.json` are rendered by `circuit_illustrations.py`; detailed authored circuit SVGs are retained. `content/illustrations.json` describes the
86 supplemental figures; `illustrations.py` generates their SVGs automatically
when the book is built. The available layouts cover transformations, tables,
probability bars, state-space directions, and a branching verification procedure.
Each figure includes a caption, alternative text, and SVG title/description.

For states, transitions, and path composition, use state-transition or connection
diagrams: configurations are nodes, transitions are directed arrows, and weights
label the arrows. Show path products and endpoint sums beside the diagram.
Do not represent these concepts as a sequence of rectangular flowchart blocks.

Edit the specification rather than the generated SVG. Keep examples consistent
with the manuscript's basis ordering and assumptions. The builder fails if an
unillustrated subsection has no specification; validation checks figure and
question coverage. Browser checks decode every subsection image and check the
mobile page width. Diagrams scroll within their own regions on narrow screens.


`content/problem-solutions.json` supplies one solution for each question, keyed by
subsection ID and the same `foundation`, `application`, and `challenge` fields.
The builder fails if a solution is absent. Each numbered problem has its own
native `<details>` control, closed by default and usable without JavaScript.
The global print handler temporarily expands solutions and restores their state.
Subsection search entries include questions but omit solution text, so search
previews do not disclose these answers. The offline edition includes all solutions.

## Editorial revision — 15 October 2026

The book-wide pass tightens 43 subsection explanations across all nine chapters,
with additional corrections to transitions, scope, exercises, and learning guides.
Physical postulates are distinguished from consequences of the model; pure states
from general local states; and query savings from implementation costs.
Exercises include incorrect implementations to diagnose, altered assumptions, and
comparisons that connect calculations to their use. Keep their hidden solutions
aligned when changing the exposition. The original Chapter 1 introduction is preserved.

Reading layout uses a bounded text measure, restrained postulate emphasis, and
compact disclosure controls. Diagrams retain horizontal scrolling on small screens
rather than shrinking mathematical labels below a readable size.

Subsection problem sets use native `<details>` disclosures, closed initially. Only
“Problems” is visible until selected; each solution remains independently hidden.
Direct problem links expand the enclosing set, and printing expands both questions
and solutions before restoring the reader’s previous state.
