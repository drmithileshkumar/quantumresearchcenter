# Quantum Algorithms

Eleven chapters organized by technique, presented with the same reader design as
the Quantum Computing course: numbered sections and subsections, keywords linked
to a glossary, circuit diagrams and plots, three problems with worked solutions
after every subsection, a reading guide and exercises with hints for every
chapter, a glossary, and a study guide. The course is a teaching manuscript; the
text identifies theorem-level results and links to their sources.

Open `index.html` to navigate. Do not edit the generated root pages.

## Sources

- `content/NN-*.html` — chapter manuscripts in a compact authoring form
  (`section.book-part` for numbered sections, `article.reading-topic` for
  subsections, `figure[data-figure]`, `aside.predict`, and `ol.problems` with
  three `li` items each containing a `div.solution`). `build.py` expands them
  into the shared book markup. Write `&lt;` for `<` inside TeX.
- `chapters.json` — chapter order, titles, opening paragraphs, driving question,
  and the section/subsection outline (kept identical to the manuscripts; the
  build fails if they differ).
- `content/learning.json` — reading guide and end-of-chapter exercises.
- `content/glossary.json` — definitions; a term must appear as a subsection
  keyword (`data-keywords`) so the glossary can link to its explanation.
- `content/figures.json` — figure specifications rendered by `figures.py`
  (circuits with controlled boxes and classical feed-forward, tables, plots,
  planes). Rendered SVGs go to `assets/figures/` and are inlined so MathJax
  typesets their labels.

## Build and check

```sh
python3 education/algorithms/build.py            # ONLY=03,04 builds selected chapters while drafting
python3 education/checks/check_courses.py
python3 education/algorithms/checks/worked_examples.py
python3 education/algorithms/checks/chapter_examples.py   # requires NumPy
python3 education/checks/check_mathematics.py
```

The reader shares CSS, MathJax, and learning scripts with the computing course
(`../computing/assets/`) and keeps independent search and reading-position
storage. Follow [AGENTS.md](AGENTS.md) for the teaching philosophy.
