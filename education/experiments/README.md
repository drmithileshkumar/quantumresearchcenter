# Quantum Experiments

An advanced course with 24 developed lessons (~16,000 words), 24 interactive
models, 24 worked examples, 72 problems with hints and solutions, and a
reproducible synthetic-data investigation. Laboratory and thought experiments
are taught together. All chapters are implemented; the edition is a teaching
manuscript, not an independently peer-reviewed textbook.

## Authoring

- `content/*.html`: canonical chapter manuscripts; edit these, not the readers.
- `chapters.json`: sequence, parts, titles, and section metadata.
- `labs.json`: lab titles, controls, ranges, defaults, and configuration choices.
- `diagrams.py`: accessible static SVG apparatus drawings.
- `assets/models.js`: pure numerical models; usable in the browser and Node.
- `assets/experiments.js`: progressive enhancement, plots, animation, CSV export.
- `assets/experiments.css`: course-specific visuals using the shared reader theme.
- `build.py`: shell, shared navigation, search index, and generated HTML.

```sh
python3 education/experiments/build.py
python3 education/experiments/tools/check_content.py
node education/experiments/tools/check_models.cjs
node education/experiments/tools/check_browser.mjs
python3 -m unittest discover -s tests
```

The course build needs Python and Beautiful Soup, as the other developed courses
do. Numerical checks use Node's standard library. Browser checks need Google
Chrome and Node with WebSocket support (Node 22 tested), and permission for a
local debugging socket. They open local files and save screenshots under `/tmp`.
No external package installation, backend, API key, or quantum hardware is needed.
The MathJax bundle and shared reader assets are local repository assets.

The site catalog entry is `content/courses.json` (`level: advanced`). The main
site builder regenerates the catalog and sitemap. Preserve unrelated user edits
when selecting outputs from `scripts.build.render`; do not force an entire site
rebuild over manually edited generated pages.

## Model scope

The diagrams are schematics, not measured trajectories. Every lab names its
simplifications. The evidence and slit labs sample seeded distributions. The
capstone exports 16 phase settings with 200 binomial trials per setting and
metadata identifying the data as synthetic. Reset restores the seed; Step/Play
on the capstone selects another seed. No real experimental dataset is bundled.

Specific restrictions include a Gaussian double-slit envelope, equal-width
pure recoil-pointer states, ideal single-mode photon-correlation profiles,
E/V0=1/2 rectangular-barrier scattering, resonant two-level Rabi rotation,
phenomenological Ramsey damping, perfectly refocusable static-noise echo,
xz-plane tomography, Gaussian pure-mode HOM overlap, and singlet-spin CHSH
angles (not photon-polarizer angles). The sensing optimum assumes a fixed-shot
budget. Wigner's friend is explicitly a reversible memory model; extended-friend
amplitudes and cross-agent inference assumptions are distinguished.

No visualization runs automatically. Play/Pause, Step, Reset, labelled sliders,
configuration selectors, numeric tables, keyboard operation, offscreen/tab
pausing, reduced-motion awareness, static SVGs, and no-JavaScript text are provided.
The capstone includes fit residuals and a downloadable CSV. Complex apparatus
plots intentionally scroll within their frame on narrow screens.

## Verification

`check_content.py` validates 25 pages, source completeness, exercises, local
links/anchors, shared navigation, accessible diagram references, and fallback
markup. `check_models.cjs` checks every mode/range, normalization, independent
beam-splitter amplitudes, local CHSH assignments, GHZ and Peres–Mermin operator
products, complex-input teleportation, the extended-friend basis change,
seeded sampling, and the visibility estimator's sampling variance.

`check_browser.mjs` exercises every slider endpoint and select option, Step and
Reset, Play/Pause/offscreen behavior, search, keyboard controls, reduced-motion
initial state, CSV contents, and JavaScript-disabled fallback. It checks math
rendering and page overflow on desktop, 390 px, and 320 px screens and captures
representative light/dark screenshots for inspection. These checks validate the
implemented examples and interface; they do not prove general no-go theorems,
certify physical equipment, or establish an interpretation of quantum mechanics.
