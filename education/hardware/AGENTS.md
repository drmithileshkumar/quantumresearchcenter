# Writing Quantum Hardware

This course follows Quantum Computing and explains physical implementation.
Develop the needed physics within concrete experiments; do not begin with a
prerequisite survey. Use short formal titles, explicit calculations, prediction
questions, worked solutions, and connected explanations.

Each platform must explain encoding, initialization, single-qubit control,
entangling interactions, readout, dominant error mechanisms, and scaling limits.
Distinguish physical devices from logical encodings. Treat topological protection
as a conditional design principle, not an established universal hardware capability.

State units, basis order, Hamiltonian signs, angular versus ordinary frequency,
rotating-frame conventions, approximation regimes, and measured versus inferred
quantities. Numerical examples are illustrative unless a primary source supports
a specific experimental claim. Avoid current hardware rankings and marketing
metrics. Check niche claims against primary papers and source theorem statements.

Use actual circuits, energy-level diagrams, pulse plots, and physical state
representations. Explain abstract composite gates when used. Inspect diagrams
visually and test worked numerical examples. Label unproved general results.

Edit canonical content/*.html and keep chapters.json synchronized. Build with
python3 education/hardware/build.py. Reuse the established reader and shared
styles. Use the independent qh-book- storage namespace. Check links, math
rendering, and mobile layout. Update catalog and sitemap selectively, preserving
manual student and research pages. Do not submit hardware jobs, commit, or publish.
