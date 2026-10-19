# Quantum Hardware

Nineteen teaching drafts on physical implementation, following Quantum Computing.
The existing chapter and subsection order is preserved. The chapters now develop
explicit small-device models, worked calculations, one additional model-check
problem per chapter, and two original figures per chapter (38 total).

Energy levels, pulse-driven evolution, interactions, readout, and noise are
introduced before the platform chapters reuse them. Circuit energy, ion motion,
Rydberg shifts, spin exchange, photon interference, and encoded error syndromes
are connected to their mathematical descriptions. Standard physical laws are
stated as inputs; simplified models are derived from those inputs. Microscopic
materials models, full topological protection proofs, and universal fault-tolerance
constructions are not asserted to follow from the small examples.

Edit `content/*.html`, not generated root pages. `chapters.json` defines the
headings and reader maps. Primary-paper links are provided in each chapter.
Build the pages with:

```sh
python3 education/hardware/build.py
```

## Figures

`figures.py` is the source for the original circuit, energy-level, physical-state,
phase-space, timing, and connectivity drawings, and for the analytical plots.
It generates `assets/figures/*.svg` and the figure manifest in
`content/figures.json`. The committed SVGs make ordinary HTML builds independent
of Matplotlib. To regenerate them in an isolated environment:

```sh
python3 -m venv /tmp/hardware-figures
/tmp/hardware-figures/bin/pip install -r education/hardware/requirements-figures.txt
/tmp/hardware-figures/bin/python education/hardware/figures.py
```

All curves are analytical or illustrative model predictions, not measured device
data. Plot axes and captions state their parameters and conventions. Figure
captions explain the approximation and the inference it supports. Legacy assets
remain available for existing external links.

## Verification

```sh
python3 education/hardware/checks/worked_examples.py
python3 education/checks/check_courses.py --course hardware
python3 -m unittest discover -s tests
```

The numerical checks require NumPy. They compare driven dynamics with a direct
matrix exponential, check phase corrections and exchange conventions, compare
transmon perturbation with a charge-basis spectrum, test Raman elimination and
full nine-state blockade phases, and verify binomial-code loss syndromes,
Majorana algebra, parity extraction, and probability/resource calculations.
These checks validate small instances and approximations, not general theorems
or experimental performance. The optional browser checker documented in
`education/checks/README.md` checks MathJax, image loading, and page overflow.
Visually inspect regenerated figures separately.

No current commercial device specification, hardware ranking, hardware execution
result, or unqualified protection claim is implied by the examples.
