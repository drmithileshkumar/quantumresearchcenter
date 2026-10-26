# Quantum Cryptography

Six developed draft chapters with 54 subsections, 41 expandable worked examples,
seventeen inline figures, and 60 exercises with hints and reasoned solutions. The
course has about 21,300 words of chapter text before the end-of-chapter exercises.
Preparation: introductory Quantum Information, linear algebra, and probability. A
suggested twelve-session schedule and chapter learning objectives appear in the reader.

The course derives one-time-pad secrecy, real/ideal key comparisons, BB84
measurement and attack statistics, exact finite-population sampling, source
replacement, Bell error labels, syndrome decoding, Toeplitz collision probabilities,
decoy-state bounds, CHSH correlations, Pauli encryption, and a commitment attack.
The general quantum uncertainty and leftover-hash results are stated with sources;
their full proofs are not claimed. The final protocol dossier has explicit
deliverables and an assessment rubric.

## Authoring and building

Edit `content/*.html`, `chapters.json`, `content/exercises.json`, and
`content/summary.json`; reader HTML and search data are generated. The reader
shares the existing course theme and uses isolated `cryptography-book-` storage.
Course-specific table, explorer, and SVG figure styles are in `assets/course.css`.

```sh
python3 education/cryptography/build.py
python3 education/checks/check_courses.py --course cryptography
python3 education/cryptography/tools/check_examples.py
node education/checks/check_render.mjs cryptography
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests
```

The builder/checker requires Beautiful Soup. The browser check requires Google
Chrome and Node with WebSocket support. It checks MathJax, local images, desktop
and mobile overflow, the rate controls, course search, and the overview; screenshots
are written to a temporary directory. Canonical subsection titles and metadata must
agree; the shared validator enforces ten exercises per chapter.

## Reproducible laboratory

`examples/bb84_lab.py` uses the Python standard library and accepts `--signals`,
`--attack`, `--seed`, and `--test-fraction`. For example:

```sh
python3 education/cryptography/examples/bb84_lab.py --signals 20000 --attack 0.2 --seed 7
```

It exposes emitted, detected, sifted, public-test, and unrevealed counts separately.
Hidden raw errors are labelled simulator-only. Its finite-population Hoeffding
bound concerns a classical error string; it is not a quantum phase-error bound.
A separate exact hypergeometric inversion is intended for small examples.
The module also supplies binary entropy, seven-bit syndrome decoding, Toeplitz
hashing, an assumed-entropy key budget, and an asymptotic decoy-yield bound.
No key is certified or emitted; the PRNG is for reproducibility, not security.

`tools/check_examples.py` verifies all 896 one-error cases of the short decoder,
all collisions of the 2×4 Toeplitz family, confidence coverage for every error
population in small blocks, Born-rule attack probabilities, extraction arithmetic,
decoy bounds, and seeded simulations. These checks do not replace general
security proofs or certify physical devices.

The interactive Chapter 3 rate explorer uses the ideal single-photon asymptotic
expression `1 - (1 + f) h2(q)`. It clips the guaranteed displayed fraction at zero
while retaining the signed expression. Static text and a fallback plot remain
available without JavaScript.
