# Quantum Machine Learning

An advanced course manuscript on what quantum models actually compute, what they cost,
and when a claimed advantage survives scrutiny. Nine chapters are planned; four are
written and marked `draft`, with 12 sections, 36 subsections, 29 expandable worked
examples, six inline figures, seven tables, and ten exercises with hints and reasoned
solutions per chapter. The written chapters contain about 10,600 words of lesson text
before the summaries and exercises.

Preparation: linear algebra, probability, and the material of Chapters 1–3 in this
course. The reader states chapter learning objectives, a reading guide, and a
two-session pace per chapter.

The written chapters derive the hypothesis-class framing of a quantum model, the
geometry and cost of three data encodings, the representer theorem and kernel
concentration, and the measurement budget of a variational circuit. Quoted results
(geometric difference, cost-function-dependent barren plateaus, concentration bounds)
are stated with their hypotheses and sources; their full proofs are not claimed.

## Status

| Chapter | Stem | State |
|---|---|---|
| 01 What a Quantum Model Is | `01-quantum-models` | draft |
| 02 Encoding Data into Quantum States | `02-data-encoding` | draft |
| 03 Quantum Kernels and Kernel Methods | `03-kernels` | draft |
| 04 Variational Quantum Models | `04-variational` | draft |
| 05 Training and Gradients | — | planned |
| 06 Barren Plateaus and Trainability | — | planned |
| 07 Generalisation and Evaluation | — | planned |
| 08 The Classical Frontier and Advantage Claims | — | planned |
| 09 Capstone: Auditing an Advantage Claim | — | planned |

The course is deliberately **not** registered in `content/courses.json`,
`education/checks/check_courses.py`, or the default course list of
`education/checks/check_render.mjs` until all nine chapters exist, so the shared
validators stay green. `check_render.mjs qml` already works when named explicitly.

## Authoring and building

Edit `content/*.html`, `chapters.json`, `content/exercises.json`, and
`content/summary.json`; reader HTML and search data are generated. The reader shares
the existing computing-course theme and uses isolated `qml-book-` storage keys.
Course-specific table, explorer, and SVG figure styles live in `assets/course.css`;
`assets/explorer.js` drives the kernel-concentration explorer of Chapter 3.

```sh
python3 education/qml/build.py
python3 -c "import sys; sys.path.insert(0,'education/checks'); import check_courses; check_courses.main(['qml'])"
node education/checks/check_render.mjs qml
```

## Conventions that the validator enforces

- Chapter `status` is `draft`; each `chapters.json` section id, number, title, and
  subsection list must match the manuscript exactly.
- Every chapter carries at least three `details.problem-solution` worked examples.
- `content/exercises.json` holds exactly ten exercises per chapter, each with a `kind`
  from Quick check, Worked problem, Misconception, Extension, at least one hint, and a
  `review` anchor (`section-s-t`) that exists in the manuscript.
- Local links, fragments, and image alternatives must resolve.
- Inline SVG figures use `role="img"` with `aria-labelledby` on the `<svg>`, plus
  `<title>` and `<desc>`; the wrapper is `<figure class="qml-figure">`, and figure
  styling is scoped to `.qml-figure > svg` so MathJax output inside a `<figcaption>`
  is never stretched.
- Write TeX inside `\( … \)` and `\[ … \]`. The configured MathJax build defines the
  base package only: `\mathbf` is available, `\boldsymbol` is not.
