# Quantum Information

Sixteen teaching chapters develop distinguishability, states, measurement,
entanglement, entropy, compression, correction, communication, and cryptography.
The course assumes no prior information theory, quantum mechanics, or linear
algebra course. Mathematics is constructed through the task that needs it.
Quantum Computing is complementary, not a prerequisite.

The reader uses the Computing course’s serif typography, bounded text width,
section hierarchy, linked subsection navigation, expandable problems, and local
MathJax. Each chapter begins with a prediction and contains reproducible worked
calculations and four solved problems, including a transfer problem with changed
assumptions. The three interactive figures explore relative phase, phase-flip
noise, and minimum-error discrimination with adjustable priors. They show exact
probabilities rather than simulated sample frequencies.

This remains a teaching manuscript in development. Advanced coding, conversion,
capacity, and security theorems are distinguished from the small examples derived
in the text, with assumptions and primary-source references. The examples are not
presented as proofs of general theorems.

Open `index.html` to navigate. Edit canonical manuscripts in `content/*.html`,
not generated root pages. `chapters.json` records the order, headings, questions,
and dependencies; `content/learning.json` supplies chapter prediction prompts and
hidden explanations. Problems and their solutions live beside their chapter’s
exposition. The About page includes a linked mind map with an expandable index of seven domains,
with topic links covering all sixteen chapters; edit `content/landscape.html`
to maintain its topic index. `landscape.py` renders the branches and the standalone
`topic-map.svg` from those links. Every chapter also opens with a linked map of
its sections and subsections, generated from `chapters.json`. Both maps fit the
reader width and stack their branches on narrow screens. Follow [AGENTS.md](AGENTS.md) for the teaching philosophy.

```sh
python3 education/information/build.py
python3 education/checks/check_courses.py --course information
python3 education/information/tools/check-mathematics.py
```

The numerical checks require NumPy and validate finite worked examples, not the
cited general theorems. The existing cross-course checks remain available through
`python3 education/checks/check_mathematics.py`.

Optional browser checks require Google Chrome and the Python `websocket-client`
package:

```sh
python3 education/information/tools/browser-check.py
```

These check all sixteen chapters on desktop and mobile, equation rendering,
drawings, interactive probabilities, search, direct problem links, printing, and
the static fallback when JavaScript is disabled. `CHROME` can select another
Chrome executable. Screenshots are written to the system temporary directory.

Shared CSS and MathJax come from `../computing/assets/`; deploy the courses
together. Course-specific styles and experiments live in `assets/information.css`
and `assets/experiments.js`. Search excludes hidden problem solutions. Reading
position and text size use isolated `qi-book-` browser storage. Native problem
and solution disclosures work without JavaScript. Printing with JavaScript
expands them temporarily and restores their previous states afterwards.
