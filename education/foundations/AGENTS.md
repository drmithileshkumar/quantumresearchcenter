# Writing the Quantum Foundations course

## Scope

These instructions govern `education/foundations/`. The course derives finite-dimensional
quantum theory from a small number of stated principles instead of postulating Hilbert
space, the Born rule, unitary dynamics, the tensor product, and the update rule. All
seventeen chapters contain initial draft lessons. Follow current user directions.

The central question is: why is the world described by quantum theory and not by some
other theory that agrees with the same experiments? The course assumes vectors, matrices,
and elementary probability, but no quantum mechanics.

## The principles-first stance

Experimental outcomes do not justify a framework. A finite table of results is consistent
with many theories, and describing an experiment already uses theoretical concepts. The
course therefore follows the model of a principle theory (as thermodynamics and special
relativity are principle theories):

1. **The arena.** The operational framework describes every theory that could be tested:
   preparations, transformations, measurements, and the statistics of repeated trials.
   It is justified as the precondition of testing, not by any experiment. It does not
   assume indeterminism; deterministic classical theory is a valid theory in the arena.
2. **The principles.** Finiteness, local tomography, equivalence of subspaces,
   continuous reversibility, and the availability of all measurements consistent with the
   state space (after Masanes and Müller, and Hardy). Purification is presented as an
   alternative route in Chapter 15. Each principle is introduced in the chapter where it
   does work, with an argument for why it is reasonable in general.
3. **The foils.** Every principle is paired with a consistent theory that violates it:
   classical probability theory, real and quaternionic quantum theory, boxworld and the
   square bit, restricted-measurement theories, labelled particles. The foil shows what
   the principle excludes. Never introduce a principle without its foil.
4. **The theorems.** Derive the formalism from the principles. Prove what can be proved
   at the course level (notably the qubit case and the consequences in Chapters 9–15).
   Where a step rests on a deep theorem (the general-N reconstruction, Gleason's theorem,
   Wigner's theorem in full, Stone's theorem), state it precisely, list its assumptions,
   and cite the primary source. Do not present a plausibility argument as a proof.
5. **Experiments as illustrations and tests.** Stern–Gerlach, polarization, beam
   splitters, and Bell tests illustrate principles and test them. They never justify a
   principle. Say which principle an experiment tests and what a contrary result would
   mean.

Intrinsic randomness is derived (Chapter 6), not assumed. The Born rule is derived for
the qubit from the shape of the state space (Chapter 7) and in general (Chapters 8 and 12).

## Dependency discipline

- Chapters 1–4 contain no quantum formalism. Use the gallery of state spaces (segment,
  triangle, square, disc, ball) to make convexity, effects, distinguishability, and
  composition concrete.
- Introduce complex numbers, matrices of amplitudes, and Hilbert space only when the
  derivation produces them (Chapters 7 and 8). Do not use bra–ket notation before
  Chapter 7.
- Write K for the number of real parameters that fix an unnormalized state (equivalently,
  the number of fiducial probabilities, including normalization) and N for the maximal
  number of perfectly distinguishable states. Keep this convention throughout.
- Keep finite dimensions until Chapter 16. If a step fails in infinite dimensions, say so
  where it occurs and defer the repair to Chapter 16.
- Separate the framework, principles, mathematical consequences, interpretations, and
  experimental evidence. Do not claim that the principles settle the measurement problem.

## Presentation

Use connected prose in an original voice: begin with a question, work a small case,
reveal the obstacle, construct the mathematics, then generalize. Each chapter has a
prediction prompt, worked examples, problems with reasoned solutions, and ten end-of-
chapter exercises in `content/exercises.json`. Verify every numerical example. Do not
fabricate citations or experimental results.

## Files and build

- `chapters.json`: order, questions, prerequisites, examples, principle, foil, sections.
- `content/*.html`: canonical manuscripts (h2 per section, h3 per subsection; the build
  assigns subsection anchors `topic-X-Y-Z`). Root chapter pages are generated.
- `content/exercises.json`: ten exercises per chapter, rendered by `../chapter_exercises.py`.
- Build with `python3 education/foundations/build.py`; check with
  `python3 education/checks/check_courses.py --course foundations`.
- Shared CSS and MathJax come from `../computing/assets/`. Do not commit or publish
  unless requested.
