# Quantum Research

Educational and Research resource for Quantum computing and Quantum information

## Research hierarchy

Research pages are generated from `content/research.json`:

- `research/quantum-computation/`
- `research/quantum-information/`
- `research/quantum-technologies/`

Every category and topic has an `index.html`. Each node's `children` list defines
its keyword links and subfolders, recursively. Add further levels by adding
children to a topic; no renderer changes are required. IDs are URL slugs, unique
among siblings. `keyword` is the short link label; `title`, `summary`,
`paragraphs`, `questions`, and `papers` supply the topic page. Paper IDs refer to
the shared `papers` catalog. Preserve existing slugs when possible, since moving
a node changes its URL.

Run `python3 scripts/build.py` to regenerate the site and sitemap, then
`python3 scripts/build.py --check` and `python3 -m unittest discover -s tests`.
The builder checks local links and page reachability. When moving a topic,
remove its obsolete generated page after checking that its content and links
have moved; the builder does not delete arbitrary folders.
