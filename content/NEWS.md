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

- `key_points`: up to five short plain-text sentences shown under the summary
  as "Key points". Use them for news stories: state what happened, the key
  number, and what it does not show, so readers get the takeaway even if
  they stop there.
- `banner`: `{"file": "banner.svg", "alt": "..."}`, a representative 1200x400
  illustration of the story's subject, shown under the summary and reused,
  cropped, as the card thumbnail and lead-story image. Draw it in
  `content/news-articles/figures/draw_banners.py` (add a function and a
  `BANNERS` entry, then run the script): original, text-free line art with the
  `.fig-*` classes, including `.fig-bg` and `.fig-wash-1`/`-2`. Never use company
  logos, photographs or other people's images. The alt text starts with
  "Illustration:" and says what is drawn.
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
- Within a section, optional structure for explainers and checklists, rendered in
  the site's plain style (rules and type, no boxes):
  `kicker` (a short label above the heading, such as "Question 1"; it also
  appears in the contents list, so the heading itself can stay short);
  `stats` (one to four `{"value", "label"}` key numbers, shown large after the
  section's first paragraph); `table` (`{"columns", "rows", "caption"}`, every
  row as long as `columns`; the first cell of a row is its header); `asks` (a
  list of questions shown as "What to ask"). Order within a section:
  paragraphs (with stats after the first), table, figure, asks.
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

## Article page layout

- Articles with five or more sections get an "In this article" contents list.
  On screens at least 1280 px wide it is open and stays in view in the left
  margin; on narrower screens it is a closed disclosure under the header.
- `source_refs` render as small bracketed superscript links after the
  section's last paragraph.
- The breadcrumb links to the topic's filtered list. The label above the
  headline shows the format, so label long beginner's guides `Explainer`.
- Reading time is shown only from two minutes up.
- Cards and the lead story reuse an article's first figure as a thumbnail;
  the lead story falls back to the house illustration.
- Body text uses the self-hosted Source Serif 4 (`fonts/`), with Georgia as
  the fallback.

## AI problem claims register

`content/ai-problem-claims.json` maintains the curated list at
`/ai-problem-claims/`. The main homepage shows a compact introduction and link;
the full list lives on the dedicated page. Each problem has a stable anchor
based on its `id`, so links to individual problems survive future additions.
Each entry records the problem, field, claimant, announcement date, primary-source
URL, claim status, and scope. An optional `article` slug links to a published local
explainer. Keep partial results and consequences explicit; do not label a claim
an accepted solution solely because its authors report a formal proof. Update
`reviewed_on` when checking the sources. The renderer validates dates, unique IDs,
source URLs, and published explainer links.

For new developments, update the relevant entry's status, scope, and source link
and refresh `reviewed_on` after checking the sources. Keep its `id` and original
`announced` date stable. Add new problems as new entries. Rebuild with
`python3 scripts/build_all.py`, then run `python3 scripts/check_site.py`.

Set `category` to `claimed` for the “Claimed by AI” section, or `open` for
“Still open”. Claimed entries require `claimant` and `announced`; open entries
require `source_label` and a source supporting the unresolved problem. Retain
the stable `id` when moving an entry between sections. A partial claim and an
unresolved remainder may have distinct entries, as with Yang–Mills existence
and the mass gap; state the difference explicitly in their scope notes.
