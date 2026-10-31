# Quantum Research

Educational and Research resource for Quantum computing and Quantum information

## Editing and building

The repository holds sources only. Every public page is generated from them, is ignored by git, and has to be
built once after cloning. Edit the sources, then rebuild and check:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build_all.py        # build everything; discovers every <section>/build.py
python3 scripts/check_site.py       # every local link and anchor resolves and every page is reachable
python3 -m unittest discover -s tests
```

`python3 scripts/build.py` alone rebuilds the shared pages and maps, once the other builders have run.
It refuses to overwrite generated pages that were edited by hand.

Paper entries live in `content/papers/`, one file each. The paper list shows the latest 40; every paper also
appears in a monthly archive at `news/papers/archive/<YYYY-MM>/`, and the list's search covers all of them.

The Tools section is rendered by `scripts/tools.py` from `content/tools.json`; its interactive
models live beside the pages in `tools/` (`single-qubit.js` and `two-qubit.js`, both styled by
`tools.css`). Each model reuses the Bloch-sphere geometry that `tools.py` computes, so the drawing
without JavaScript matches the one the script then maintains. Course chapters under `education/<course>/` have their own `build.py`; most of those only describe the course and call `education/course_builder.py`, while `algorithms`, `computing`, `experiments` and `information` have layouts of their own. News curation is
described in `content/PAPERS.md`. General-audience articles and homepage selection are described in
`content/NEWS.md`.

GitHub Actions builds the site and runs the checks and tests on every push (`.github/workflows/checks.yml`).
A passing push to `main` publishes a fresh build to GitHub Pages, which must have **GitHub Actions** as its
source. Sources such as `content/` and `scripts/` are not published. It also checks external links weekly (`.github/workflows/links.yml`; run locally with `python3 scripts/check_links.py`).

## Styles and accessibility

`styles.css` is loaded by every page and owns the design tokens (`:root`, with dark-mode values under
`html[data-theme=dark]`). Use `var(--ink)`, `var(--muted)`, `var(--line)`, `var(--blue)` and the other tokens
instead of hex colours, including in course stylesheets, so both themes and the high-contrast settings keep
working. Its last section holds the shared accessibility rules (focus ring, underlined prose links, reduced
motion, `prefers-contrast`, Windows high-contrast mode).

`tests/test_accessibility.py` checks every page's markup (language, title, one `<h1>`, skip link, alt text,
named links and buttons, labelled form fields, unique ids, zoom allowed), and
`tests/test_palette_contrast.py` checks the token palette against WCAG AA contrast in both themes.

## Shared templates

Content is separate from presentation: `scripts/build.py` renders research pages,
`scripts/news_articles.py` renders the homepage and public articles, and the course
builders render their reader layouts, from the templates in `scripts/templates/` and `education/templates/`. All three use `education/site_navigation.py`
for **Home · News · Education · Research · Tools**, including relative links and the active
section. `navigation.js` decorates utility buttons only; primary links retain their
visible labels with or without JavaScript.

After changing shared navigation or styles, rebuild everything (the Computing build also refreshes its
offline download):

```sh
python3 scripts/build_all.py
python3 -m unittest discover -s tests
```

## Adding pages and keeping maps current

Add a page by adding its source and, for a new section, a `<section>/build.py`, which `scripts/build_all.py` discovers. A new kind of output also needs a rule in `.gitignore`; CI fails if a build leaves anything uncommitted. Both the interactive website graph (`website-map/`) and the search-engine sitemap (`sitemap.xml`) are built from one shared inventory of the public HTML pages, including new standalone sections and nested pages; redirects, noindex pages, and build inputs are excluded. Run `python3 scripts/check_site.py` before finishing, since a page that nothing links to fails it.
