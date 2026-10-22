# Quantum Information Theory

Ten advanced draft lessons following Quantum Foundations and introductory Quantum
Information. Each chapter develops an operational question, mathematical arguments,
three worked checks, and ten exercises with hints and reasoned solutions. Deep
coding and recovery theorems are identified as statements rather than full proofs.
The final chapter supplies three bounded research projects.

Edit `content/*.html`, `content/exercises.json`, `content/summary.json`, and
`chapters.json`; the root HTML pages and search index are generated. The reader
reuses the site's theme, MathJax, course maps, and accessible search interface.
Its reading-position storage uses the independent `qit-book-` prefix.

```sh
python3 education/information-theory/build.py
python3 education/checks/check_courses.py --course information-theory
python3 education/information-theory/tools/check_examples.py
python3 scripts/build.py
```

The build and structural checker require Beautiful Soup (`beautifulsoup4`), as do
existing course builds. The numerical verifier requires NumPy. To install these
in a development environment: `python3 -m pip install beautifulsoup4 numpy`.

Conventions: finite-dimensional systems; base-two logarithms; squared fidelity;
unnormalized Choi matrices ordered reference then output. Keep support conditions,
source models, capacity assistance, and exact versus asymptotic criteria explicit.
Do not turn a numerical example into a claim of a general proof. Sources appear
beside nontrivial theorem statements; prose and exercises are original.
