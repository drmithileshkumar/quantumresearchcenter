# Research questions

`../research.json` defines the four categories, question titles, summaries, bibliography keys, and manuscript paths. Each HTML file here is a canonical manuscript; the corresponding page under `research/` is generated.

A question manuscript develops five sections:

- `perspective`: the physical or computational question and why it matters.
- `mathematics`: a specified model, explained notation, and a worked calculation.
- `known`: established results, theorem scope, and links to the supporting papers.
- `frontier`: the unresolved issue and the assumptions that make it precise.
- `investigation`: a reproducible baseline, an explicit check, and a proposed extension. Distinguish the baseline from a possible new contribution.

Keep citations beside the relevant claims and include each cited source in the question's `papers` list. Verify an open-problem claim against primary literature when revising it. A proposal, a disputed calculation, and an experimentally established result require different wording. Update the source-review date in the reader when performing a new review.

Build and validate from the repository root:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests
```

`scripts/research_figures.py` rebuilds the six original plots using NumPy and Matplotlib. These are authoring dependencies; the deployed site uses only the generated SVGs and the existing local MathJax bundle. Preserve captions, alternative descriptions, and narrow-screen scrolling when changing a plot.

`../research-redirects.json` maps earlier research URLs to related current pages. Redirects have canonical links and are excluded from the sitemap. Keep those mappings when changing the taxonomy, and preserve student contributions in `../student.json`.
