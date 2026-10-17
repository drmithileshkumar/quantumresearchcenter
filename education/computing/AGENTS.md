# Writing and maintaining the quantum computing book

## Scope and authority

These instructions apply to the book and its supporting files in `education/computing/`. Follow the user's current directions when they change the scope or teaching approach. This file defines the intended pedagogy and progression; `README.md` also documents the existing manuscript and build workflow. Where its older outline or prerequisite statements conflict with this file, use this file. Do not reorganize unrelated chapters merely because the intended progression differs from the current contents.

The book begins with the origins of computability and ends with the optimality of quantum search and the limits of the black-box model of computation. Its central thread is the evolution of configurations: what transitions a model permits, how transitions compose, what information survives, and what a computation can reveal.

## Current phase: design the blueprint

We are presently designing the blueprint of the book, not treating the existing manuscript or chapter list as a finished structure. The ambition is a coherent, deeply understandable book on quantum computing with the explanatory intimacy associated with Feynman and the cumulative conceptual discipline associated with Susskind. These are teaching aspirations, not instructions to reproduce either author's prose, persona, or organization.

- When the user asks to refine the blueprint or these instructions, edit this file only unless they explicitly request other artifacts. Do not rebuild the site, revise chapters, or update the README as a side effect.
- Design the blueprint independently of the current book. Do not use its contents, chapter groupings, section titles, examples, or allocation of space as the starting point for proposals. Do not inspect the existing manuscript to decide what the new structure should be.
- Give the Feynman–Susskind teaching aspirations defined below priority over continuity with the current edition: concrete reasoning, conceptual discovery, revealing calculations, and a carefully accumulated mathematical framework. Follow the user's intended conceptual journey, but derive chapter boundaries from the reasoning needed to teach it.
- Establish the motivating problems, anchor examples, conceptual obstacles, and dependencies before proposing chapter divisions or a chapter count. Do not begin with a conventional syllabus and attach intuitive introductions afterward.
- Consult the existing manuscript for possible reuse only after the independent blueprint is established and the user requests comparison or implementation. At that stage, judge existing material against the blueprint rather than adapting the blueprint to preserve it. Until then, leave the manuscript unchanged.
- Evaluate proposed structure by the reader's growing understanding, not by resemblance to a conventional quantum computing syllabus. A contents list alone is not a blueprint.
- Aim for completeness of the explanatory journey rather than encyclopedic coverage. A topic belongs on the main route when it advances the central question or supplies a necessary tool for a later argument.
- Keep unresolved design choices explicit. Do not call the blueprint complete merely because every standard topic has a heading.

## Desired reading experience

The reader should feel that a thoughtful teacher is working through a consequential question with them. Each new idea should answer a difficulty they have already encountered, and each calculation should help them see something they could not see before.

- Use concrete experiments, machine configurations, and small computations to make alternatives tangible. Invite the reader to predict a result, then calculate it and explain any surprise.
- Combine exploratory reasoning with careful accumulation: an intuitive picture creates a need, a calculation makes it precise, and a reusable principle captures what was learned.
- Give the reader enough mathematical control to reconstruct the result. An explanation that feels plausible but cannot be used to calculate the next example is incomplete.
- Introduce abstraction when it compresses familiar reasoning or enables a needed extension. Explain what work the abstraction saves; do not introduce it for prestige or apparent rigor.
- Use plain, direct, conversational prose with intellectual seriousness. Avoid a lecture-note outline masquerading as a chapter, theatrical mystery, breathless claims about quantum power, and appeals to authority in place of reasoning.
- Allow difficult ideas room to develop. Slow down at the transition from probabilities to amplitudes, the role of conjugation, joint states, measurement, and lower bounds. Do not flatten these conceptual turns into a glossary of definitions.
- Return to an earlier example with a stronger question rather than repeat its original explanation. The reader should experience continuity and increasing power.
- Preserve the distinction between understanding why a rule is useful, accepting a physical postulate, proving a mathematical consequence, and establishing an experimental fact.
- Do not eliminate mathematics to achieve accessibility. Build the mathematics in context so that no prior course is required. The objective is independent reasoning, not familiarity with terminology.

## What the blueprint must specify

For each proposed chapter or substantial conceptual unit, identify the following in the planning material. These are design requirements, not a template to print mechanically in the eventual book.

1. **Driving question:** What specific problem motivates this unit, and why does it arise now?
2. **Reader's starting point:** Which ideas and operations are already available? Identify the earlier explanations that supply them.
3. **Anchor example:** Which small machine, experiment, state, graph, or circuit carries the argument?
4. **Conceptual obstacle:** What fails, remains unexplained, or cannot yet be calculated using the reader's existing tools?
5. **Construction:** What new rule or mathematical idea resolves that obstacle, and how will it be developed without a prerequisite detour?
6. **Decisive calculation:** What calculation demonstrates the new idea and makes the result reproducible by the reader?
7. **Representative illustration:** What actual states, transitions, or circuit will be shown, and what reasoning does the picture make easier?
8. **Transfer and limits:** What fresh example can the reader now solve, and what tempting inference does the result not justify?
9. **Understanding checks:** Which predictions, calculations, or explanations distinguish understanding from memorizing the presentation?
10. **Handoff:** What unresolved question now naturally leads to the next unit?

Maintain the dependencies between units, including when notation first becomes meaningful and when it is first needed. Audit the route for circular explanations, hidden prerequisites, disconnected examples, redundant chapters, and jumps from a special example to an unjustified general claim. Mark optional extensions clearly so they do not interrupt the main argument.

Before accepting a blueprint revision, check that an attentive newcomer could follow the proposed reasoning using only earlier material, that every major technique has a worked use, and that the final discussion of black-box limits draws on tools the book actually develops. Make chapter boundaries and topic coverage serve these tests.

## Reader and teaching contract

- Keep chapter titles short and formal, preferably two to five words. Name the subject directly, for example: “Computability,” “Reversible Computation,” “Quantum States,” “Quantum Circuits,” “Phase Kickback,” or “Search Optimality.” Avoid questions, slogans, metaphors, promotional language, and long lists of topics in titles. Put the motivating question and explanatory framing in the chapter opening, not the title.
- Assume no subject prerequisites: no linear algebra, complex numbers, probability theory, formal logic, computer science, calculus, or quantum mechanics. Introduce any mathematical operation or notation when it becomes necessary, including elementary ones when their meaning is essential to the argument.
- Write for a curious reader willing to reason through examples. Do not confuse lack of prerequisites with lack of ability.
- Build concepts within the problem that needs them. Follow a concrete question with an example, a calculation, a pattern, and only then the general rule and its name.
- Use the pedagogical qualities sought from Feynman and Susskind: concrete situations, explicit alternatives, revealing calculations, and a carefully accumulated mathematical framework. Retain an original voice and let quantum computation supply the questions and examples.
- Do not begin with a survey of mathematical machinery. Do not send readers to an appendix to acquire a prerequisite needed for the main argument. Appendices may consolidate or extend material already made usable in context.
- Keep the main route self-contained. A reader following it in order must not need an unexplained concept from a later chapter.
- Depth follows the explanation, not a fixed number of subsections, examples, or pages. Avoid padding to satisfy a template.

## How to develop an explanation

1. State a question the reader can understand with what has already been established.
2. Give the smallest concrete instance that contains the difficulty.
3. Draw its configurations, weighted transitions, state geometry, or circuit when that makes the reasoning visible.
4. Work through what happens. Show the contributions and their combination rather than jumping to a formula.
5. Compare a useful alternative or counterexample to identify what matters.
6. State the general rule, explain each symbol, and introduce the technical name.
7. Reuse the rule in a slightly different situation and identify its limits.

This is a reasoning sequence, not a mandatory set of visible headings. Write connected prose. Let questions motivate the discussion without turning every paragraph into a question-and-answer script.

Use a few recurring examples: a small configuration machine, reversible function evaluation, a two-configuration transition, a two-path cancellation, a pair of qubits, and a four-item search. Extend these examples as the reader acquires new tools.

## Intended conceptual progression

The stages below specify dependencies, not immutable chapter numbers. Chapter divisions should serve the development.

### 1. Origins of computability and machine models

- Begin with the ambition to make reasoning and calculation mechanical. Explain rules, finite descriptions, proof checking, proof search, and decision through examples before introducing formal terminology.
- Distinguish finding an answer from checking a proposed answer, and eventual termination from efficient termination.
- Describe a machine by its configurations and allowed transitions. A configuration must include the information needed to determine its future behavior, such as memory, control state, and head position.
- Develop representative machine models sufficiently to make their operation tangible. Explain why a change of representation need not change what is computable.
- Introduce limits of computability with a worked argument, not a list of named theorems. Keep computability separate from resource bounds.

### 2. Reversible computation and transition models

- Show information loss using explicit truth tables and configuration graphs. Explain reversibility as the ability to recover the previous configuration uniquely.
- Develop NOT, controlled operations, retained inputs, workspace, and uncomputation as responses to that requirement.
- Explain reversible evaluation as preserving the input while combining the answer into a target, for example `(x, y) -> (x, y XOR f(x))`. Define XOR before using it.
- Compare deterministic, nondeterministic, and probabilistic transition rules using the same small configuration space where possible.
- Deterministic transitions select one successor. Nondeterminism concerns allowed branches and an acceptance condition; it is neither a random choice nor access to all branch answers. Probabilistic transitions assign nonnegative probabilities whose outgoing sum is one.
- Show composition explicitly: multiply weights along a path and add the contributions of alternatives reaching the same final configuration. Explain which interpretation of weights makes this appropriate.
- Do not treat arbitrary reversible probability distributions as if they were quantum amplitudes. Explain what changes when the weight rule changes.

### 3. Signed weights, cancellation, and reversible amplitude transitions

- Ask what changes if transition weights may be negative. Work through two paths that cancel before naming interference.
- Explain why signed weights cannot themselves be probabilities. Motivate a separate rule connecting weights to observed frequencies.
- Introduce the squared-weight probability rule for real amplitudes and its normalization requirement. Distinguish the experimental/postulated rule from consequences derived from it.
- Develop the simplest normalization-preserving reversible transitions on two configurations. Start with lists of weights and sums of products, not an assertion about orthogonal matrices.
- Explain why requiring the squares in each outgoing list to add to one is insufficient: arbitrary combinations of inputs must also retain their total squared weight. Show how the cross-sum must vanish.
- Use a concrete rotation or Hadamard-like example to demonstrate cancellation and recovery of the input by a reverse step.
- Distinguish an invertible transformation from one that preserves the probability interpretation. Many invertible transformations change lengths and are not valid closed-system quantum transitions.

### 4. Complex amplitudes through a square root of NOT

- Pose a concrete demand: find a transition which, performed twice, gives NOT. Show why the desired two-state reversible amplitude operation cannot be obtained with real weights under the stated constraints.
- Introduce complex numbers as the additional directions needed for these weights. Explain `i`, addition, multiplication, conjugation, and squared magnitude through their use and simple plane geometry.
- Exhibit a working square root of NOT and multiply the transitions explicitly. One usable choice has stay weight `(1+i)/2` and flip weight `(1-i)/2`: the two paths to stay cancel, while the paths to flip sum to one.
- Check both normalization and the composition. Do not present a complex matrix without explaining its entries as transition amplitudes.
- Generalize the real cross-sum to products with conjugates. Explain why conjugation appears, and only then identify the rule as unitarity.
- Explain relative phase through interference. Distinguish it from a common phase that leaves all measurement probabilities unchanged.

### 5. Quantum postulates developed in context

- Assemble the state, evolution, measurement, and composite-state postulates from the problems already considered.
- Be explicit that a mathematically consistent extension of transition rules does not by itself prove that nature uses it. Separate physical postulates from mathematical deductions and illustrative motivation.
- A state specifies amplitudes for a complete set of distinguishable configurations. Explain normalization and the physical equivalence of states differing only by a common phase.
- An isolated system evolves by transformations preserving the probability interpretation for every input. Introduce the adjoint as reversing transition arrows and conjugating weights; show why it is the inverse for a unitary operation, and not for every matrix.
- Measurement specifies both outcome probabilities and the state conditional on the observed outcome. Show projection and normalization geometrically when appropriate. Never portray the components as simultaneous fractional outcomes.
- Illustrate smooth evolution interrupted by measurement updates. Label such a history schematic; a vertical drop does not represent loss of normalization or necessarily a decrease in energy.
- Construct composite configurations by pairing labels. Introduce the tensor product as the bookkeeping for these joint possibilities and explain why dimensions multiply.
- Independent pure preparations give products of local amplitudes. General joint amplitudes need not factor; develop entanglement from this failure with a small example.
- Correlated measurement outcomes alone do not establish entanglement. Distinguish a coherent pure state from a classical mixture when the distinction becomes necessary.

### 6. Quantum computation, circuits, parallelism, and limitations

- Turn the postulates into a computational model: input preparation, a register, elementary local gates, workspace, measurements, classical control, and an output criterion.
- Introduce circuit wires and symbols before expecting readers to read them. Explain left-to-right time, rightmost-first matrix composition, identity wires, quantum controls, measurement, and classical records.
- Show complete small computations, tracking amplitudes at meaningful intermediate points.
- Explain quantum parallelism through linearity of reversible function evaluation on a superposition. Immediately establish what measurement reveals and why this does not provide all function values as accessible classical answers.
- Develop the relevant impossibilities through short arguments: no arbitrary-state copying, no perfect discrimination of nonorthogonal states, and no signaling through local operations on an entangled pair. Introduce any mathematics needed inside those arguments.
- Build teleportation as a circuit with explicit branches and corrections. Account for the shared entangled pair, two classical bits, the consumed input state, and the absence of faster-than-light communication. Explain the protocol before compressing it into an identity.
- Count preparation, gates, qubits, depth, repetitions, and classical processing where relevant. Do not count an arbitrary global unitary as a free elementary gate.

### 7. Phase kickback as a reusable technique

- Begin with a target state whose response to a reversible query is a sign or phase. Calculate how that phase becomes attached to the controlling alternatives.
- Derive the effect from the action on basis configurations before introducing eigenstate language.
- Distinguish recording an answer in a target from encoding a relation in relative phase. Show how a later interference step makes the phase observable.
- Use small promise problems to demonstrate the technique. State the promise, oracle access, number of queries, output task, and classical comparison precisely.
- Track workspace and explain why it must be restored when it would otherwise retain information that prevents the intended interference.

### 8. Constructing universal quantum gates

- Motivate universality by asking how the transformations used so far can be built from a restricted repertoire of elementary gates.
- Develop single-qubit rotations and phase operations geometrically, controlled operations through their action on joint configurations, and entangling operations through worked circuits.
- Explain what “universal” means for the chosen gate set: exact construction when applicable, or approximation to arbitrary accuracy.
- Distinguish continuous families of allowed gates from a finite gate alphabet. Never imply that a finite alphabet exactly realizes every unitary.
- Explain approximation error and construction cost before making an efficiency claim. Separate existence of a decomposition from an efficient synthesis.
- Connect gate constructions back to queries, phase kickback, controlled operations, and the reflections needed next.

### 9. Amplification as a technique

- Begin with an easy-to-check marked answer and a small search space. Show that phase marking alone does not change the immediate probabilities.
- Derive reflection about a known prepared state through a circuit. Explain the effect of each reflection before composing them.
- Use a real two-dimensional state diagram to expose rotation between marked and unmarked components. Construct those two directions in words and amplitude lists before naming a subspace.
- Work through a four-item example numerically, then derive the general scaling. Explain overshooting and why repeated iterations do not improve success indefinitely.
- Generalize from uniform search to amplitude amplification of a preparation procedure, making access to that procedure, its inverse, and the success test explicit.

### 10. Search optimality and the limits of black-box computation

- Define precisely what the oracle hides, what constitutes one query, what output is required, and what probability of success is promised.
- Separate query complexity from the total work of implementing the oracle and the rest of the circuit.
- Establish an upper bound by an actual algorithm, and a lower bound by reasoning about all algorithms in the stated model. Do not infer optimality from failure to find a faster circuit.
- Develop an accessible lower-bound argument for unstructured search, showing why too few queries cannot make the possible oracle cases sufficiently distinguishable. Supply needed estimates in context.
- State the dependence on the number of items, the number of marked items, and any promises. Explain which regime a claimed bound covers.
- End by identifying what the black-box model can and cannot establish. A query lower bound does not rule out exploiting an explicit problem's additional structure; a query speedup does not automatically imply an end-to-end speedup.
- Do not present unstructured search as a general efficient solution to NP-complete problems, or an oracle separation as an unconditional separation of ordinary complexity classes.

## Mathematical language and correctness

- Begin with configurations, arrows, amplitude lists, and path sums. Introduce vectors as a name for lists with established combination rules; matrices as tables of transition weights; inner products as overlap calculations; and tensor products as joint-state construction.
- Introduce ket notation only after the configuration or state it denotes is understood. Explain bras and conjugation before using a bra-ket expression as an argument.
- Use technical terms after their meaning has been established. Avoid unexplained phrases such as “Hilbert space,” “linear operator,” “eigenbasis,” or “spectral decomposition.” If needed, construct the idea locally and then name it.
- State basis order, subsystem order, input/output indexing, and gate order consistently. Distinguish probabilities, amplitudes, and measured values.
- State assumptions with claims: finite dimension, pure state, closed evolution, ideal projective measurement, independence, oracle promises, or approximation tolerance as appropriate.
- Do not sacrifice correctness for an intuitive story. Identify schematic pictures, special cases, and analogies explicitly, then explain their reach.
- Verify worked examples by direct calculation. For small gates, check normalization, interference signs, and the claimed composed action. Keep global and relative phase distinct.
- Use reliable primary sources when verifying historical claims, attributing results, or checking nontrivial theorem statements. Do not invent references or imply that an illustrative argument proves more than it does.

## Illustrations

- From Chapter 5 onward, use circuit diagrams for illustrations. Introduce their notation before use, show actual quantum wires and gates, and distinguish classical records. Abstract algorithm and oracle boxes must be labelled as composite operations; a drawing alone does not establish their cost or prove a lower bound. Keep geometric reasoning in the text where needed.

- Use representative state diagrams, weighted transition graphs, geometric projections or rotations, and actual circuit diagrams. Do not use generic block diagrams or process-flow boxes as substitutes for explaining quantum states or operations.
- Gate boxes on circuit wires are valid circuit notation; the prohibition concerns generic explanatory flowcharts.
- A two-qubit amplitude picture may use a complete bipartite graph: one node for each local basis label on either side, with an edge for each joint amplitude. Explain that these edges label joint configurations, not time transitions. Label general weights separately from their product-state specialization.
- Place edge labels beside the edges without white rectangles that break the lines. Crossing edges are not additional vertices unless explicitly marked.
- Label amplitudes, directions, basis states, measurement outcomes, and conditional branches where they matter. Use color consistently, but never as the sole carrier of meaning.
- Distinguish quantum wires from classical records and coherent control from classical conditional gates.
- Supply meaningful captions and accessible descriptions. Explain what the picture shows, how to read it, and any limitation necessary to prevent a false inference.
- Use the existing SVG and MathJax conventions. Keep labels legible and clear of edges; visually inspect new or materially changed diagrams.

## Exercises and continuity

- Problems should check understanding, apply the idea, and expose a limit or misconception. They must be solvable with the preceding material.
- Provide worked reasoning rather than answer-only solutions. Avoid exercises whose solution silently imports later mathematics.
- Keep subsection questions, solutions, keywords, notation references, illustrations, chapter aims, and navigation consistent with the manuscript.
- When removing material, remove or repair dependent references and exercises. When adding or moving chapters, update numbering, links, reading guides, search data, and the offline edition.
- Introduce the next problem at a chapter boundary without promising content that is no longer present.

## Repository workflow

These implementation rules apply when manuscript or site work is requested. During blueprint-only work, follow the narrower file scope above and do not regenerate artifacts.

- Edit canonical manuscripts in `content/*.html`, navigation manifests in `content/*.json`, and chapter ordering in `chapters.json`. Do not treat generated root chapter pages as the source of truth.
- Keep figure sources or specifications consistent with the generated illustrations. Do not change only an inlined SVG in a generated chapter.
- Use `content/learning.json`, `probing-questions.json`, `problem-solutions.json`, `keywords.json`, `notation.json`, `glossary.json`, and `illustrations.json` as appropriate. Follow the existing schemas; a chapter-specific figure in its manuscript can replace an automatic illustration.
- Rebuild with `python3 education/computing/build.py` from the repository root and validate with `python3 education/computing/tools/validate.py`.
- Check for broken links, duplicate IDs, stale numbering, notation introduced before its explanation, and unintended generated changes. Visually inspect diagrams separately; static validation does not establish visual quality or mathematical correctness.
- Preserve unrelated user edits. Do not commit or publish unless requested. Report what changed and what was actually checked.
