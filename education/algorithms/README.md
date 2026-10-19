# Quantum Algorithms

11 developed draft chapters, with explanations, worked examples,
solved problems, and circuit illustrations where they clarify the construction.
The course is an initial teaching manuscript, not a claim that every advanced
result receives a full proof. The text identifies theorem-level results and
links to their sources.

Open `index.html` to navigate. Edit canonical manuscripts in `content/*.html`,
not the generated root pages. Chapter order, headings, and planning notes live
in `chapters.json`. Follow [AGENTS.md](AGENTS.md) for the teaching philosophy.

```sh
python3 education/algorithms/build.py
python3 education/checks/check_courses.py
```

The reader shares CSS and MathJax with the computing course, with independent
search and reading-position storage. Preserve manual research/student pages
when updating the site catalog.

Numerical small-instance checks: `python3 education/checks/check_mathematics.py`
(requires NumPy). They validate examples, not the general cited theorems.
