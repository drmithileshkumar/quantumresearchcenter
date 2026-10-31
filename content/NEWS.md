# Quantum News and the news-led homepage

The homepage leads with accessible coverage. `/news/` is the shared hub;
`/news/articles/` lists general-audience stories and `/news/papers/` lists
technical research summaries; each paper page is `/news/papers/<arxiv-id>/`. The paper
search index and `/news/feed.xml` remain intact. `/news/papers.html` is still
the separate, unlisted local paper-review interface.

## Publish an article

Create one JSON file in `content/news-articles/`; its filename must match its
`slug`. Copy an existing article as a starting point. Text is plain text, escaped
by the renderer; HTML and Markdown are not interpreted.

Required fields:

- `slug`: lowercase words separated by hyphens; becomes `/news/articles/<slug>/`.
- `title`, `summary`, `author`: headline, short introduction, and credited author.
- `published`: publication date in `YYYY-MM-DD` format. This is the article's
  date, not the date of a historical announcement discussed in the article.
- `status`: `draft` or `published`. Only published articles appear anywhere public.
- `topic`: `discoveries`, `companies`, `government`, or `projects`.
- `format`: `News`, `Explainer`, `Interview`, or `Opinion`.
- `sections`: a nonempty list of objects with `heading` and `paragraphs` (a list
  of plain-text paragraphs).
- `sources`: a nonempty list of objects with `title` and an HTTP(S) `url`.

Optional fields:

- `updated`: date of a substantive update, no earlier than `published`.
- `related_articles`: other published article slugs.
- Within a section, `source_refs`: optional 1-based source numbers for linked citations
  immediately after that section. The build rejects missing/out-of-range references.
- `related_papers`: approved arXiv IDs from `content/papers/`. These create
  links in both directions between the explanation and the technical page.
- Within a section, `figure`: `{"file": "name.svg", "caption": "...", "alt": "..."}`.
  The SVG lives in `content/news-articles/figures/<slug>/` and is inlined after the
  section's paragraphs. Draw marks with the `.fig-*` classes in `news/editorial.css`
  so they follow the light/dark theme; scripts, event handlers and `id` attributes
  are rejected. Keep a generator script beside the figures (see the ETH article's
  `draw.py`) so they can be redrawn.
- Mathematics: write TeX in paragraphs and captions, `\(...\)` inline and `\[...\]`
  displayed. MathJax loads only on article pages that contain TeX. Keep titles and
  summaries plain text, since cards and RSS readers do not typeset.

The starter collection contains three source-linked background explainers,
not a feed of breaking announcements. Keep announcement dates explicit in
stories. Attribute claims to their sources and distinguish goals, funding,
experimental demonstrations, and deployed products. Add company and project
coverage through the same schema as reporting becomes available.

Choose the homepage feature using `featured` in `content/news.json`. It must
name a published article, or be `null` to use the newest published article.
The remaining stories and the latest three approved papers are populated
automatically. Equal publication dates are sorted by slug for stable builds.

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/` to preview. Edit source files, not generated HTML.
Publishing is explicit: there is no scheduler. A future `published` date does
not delay a story whose status is already `published`; keep it `draft` until
ready. Source files live in the repository and may be accessible on static
hosting, so draft status excludes content from generated pages and feeds but
does not provide confidentiality.

To withdraw an article, set it to `draft`, clear any explicit feature selection,
and remove links to it from other published articles. Rebuilding removes the
managed article page and its entries from the homepage, article feed, RSS,
and sitemap. Unmanaged pages are never removed by this cleanup.

## Feeds, filters, and maintenance

- `/news/articles/feed.xml`: the 30 newest general-audience articles.
- `/news/feed.xml`: the existing feed of selected technical papers.
- Article filters support bookmarkable `?topic=government`, `?format=Explainer`,
  and `?q=security` queries. All articles remain readable without JavaScript.
- Old `/news/?topic=computing` and `/news/#paper-…` bookmarks forward to the new
  paper list when JavaScript is enabled. Without it, the hub links to both feeds.
- The builder validates metadata, dates, sources, related links, local links,
  reachability, and sitemap inclusion. Tests cover draft exclusion, withdrawals,
  stable paper links, cross-stream links, and homepage refresh during approval.
- The article renderer is `scripts/news_articles.py`; styles and filtering are
  in `news/editorial.css` and `news/articles.js`. Research/course styles retain
  their existing reader layout.
