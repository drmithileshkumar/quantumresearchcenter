# Quantum Foundations

Seventeen draft chapters that derive finite-dimensional quantum theory from physical
principles. Each principle is paired with a foil theory that violates it, and each chapter
ends with ten exercises with hints and worked solutions. The course is an initial teaching
manuscript: theorem-level results whose proofs lie beyond it are stated with their
assumptions and sources.

Open `index.html` to navigate. Edit canonical manuscripts in `content/*.html` and
exercises in `content/exercises.json`, not the generated root pages. Chapter order,
headings, principles, and foils live in `chapters.json`. Follow [AGENTS.md](AGENTS.md)
for the teaching approach.

```sh
python3 education/foundations/build.py
python3 education/checks/check_courses.py --course foundations
```

The reader shares CSS and MathJax with the computing course, with independent search and
reading-position storage.
