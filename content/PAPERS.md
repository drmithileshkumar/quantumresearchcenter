# arXiv papers and news

The site uses an editorial workflow: fetch → review and summarize → choose → approve → build.
The six initial candidates were sourced from arXiv abstract pages on 19 October 2026.
They are recommendations for review, not an objective ranking or a complete latest-paper feed.
Summaries are abstract-based; read the linked version before approving a news article.

- `content/papers.json` holds curated summaries and explicit editorial status.
- `news/papers.html` lets readers filter candidates and select papers. It is published but unlisted: the public news page does not link to it (the **Review & approve** link appears only when the page is served by the local editor), it is left out of `sitemap.xml`, and it carries `noindex`. Anyone with the URL can still open it, so do not put anything confidential in candidate entries. In the local editor, **Approve selected papers** saves approval to the repository and rebuilds both news pages. On a static host, approval is disabled and the page explains how to start the local editor. This page is public if deployed; the approval service only binds to loopback and checks a session token and request origin.
- `news/index.html` lists approved papers compactly (question, result, technique names), grouped by the month they were selected. The sidebar filters by research area (`?topic=computing` links work) and jumps by month.
- Each approved paper gets its own page, `news/<arXiv id>/index.html`, holding the full description, the methods with derivations, and context. MathJax loads only on pages that contain TeX, so the listing stays light as papers accumulate.
- `news/index.json` is a small search index (title, authors, topic, dates, question, result, technique names) used by the listing's search box. It is the basis for later archive pages, which can search papers that are no longer on the main list.
- `news/papers.html` shows only papers still awaiting approval.
- Withdrawing a paper (back to `candidate`) removes its page on the next build; `build.py --check` fails if a withdrawn paper's page is still present.
- `scripts/paper_news.py` renders both pages through the existing build system. Do not edit generated HTML.

Fetch recent metadata with Python's standard library:

```sh
python3 scripts/arxiv_papers.py fetch --days 30 --limit 100 --as-of 2026-10-19
```

This makes one request to the [arXiv API](https://info.arxiv.org/help/api/user-manual.html) and writes `content/arxiv-inbox.json`. Network access is required. Leave at least three seconds between requests. Results are capped and ordered by initial submission date; this is discovery, not automatic quality scoring. The quant-ph feed covers all three areas but needs editorial classification. The inbox is not rendered by the website. Fetching never overwrites curated summaries or approvals.

Review the inbox, check the full paper, and add promising candidates to `papers.json` using the existing schema. Record `problem`, `result`, `significance`, `limitations`, source `version`, `submitted`, `verified_on`, `summary_basis`, and `topic` (`foundations`, `computing`, or `information`). Update the collection's `reviewed_on` after a review. Use `status: "candidate"` until the editor has chosen it. Revised versions require a fresh summary review; the fetcher does not silently replace a cited version.

To approve directly on the page:

```sh
python3 scripts/news_editor.py
```

Open `http://127.0.0.1:8765/news/papers.html`, select papers, and click **Approve selected papers**. The success message links to the updated news page. Approval survives restarting the server because it is stored in `content/papers.json`. The server does not deploy the website; deploy through the usual process when ready. Stop it with Ctrl+C. This is a local editing service, not a production server.

Alternatively, once the editor explicitly chooses paper IDs, approve only those IDs from the command line (example syntax):

```sh
python3 scripts/arxiv_papers.py approve 2609.10508 --date 2026-10-19
python3 scripts/build.py
python3 scripts/build.py --check
```

Approval generates static news summaries on the next build. Deployment continues through the site's usual process. To withdraw an article, set its status back to `candidate`, remove `approved_on`, and rebuild. No paper has been approved in the initial dataset.

## Transferable methods

Every approved paper must have a nonempty `description`: a list of paragraphs
describing the setting, the precise question, the main theorem or measurement,
and what remains open. It renders under **The paper in detail**.

Every approved paper must also have a nonempty `methods` list. Each entry contains
`technique` (a short name), `explanation` (how the paper uses it), `math` (a list
of paragraphs deriving the idea: definitions, the key identity or inequality, and
why it works), and `transfer` (how to reuse it, including relevant assumptions or
limits). Text fields may contain TeX: `\(...\)` inline and `\[...\]` displayed,
rendered by the site's local MathJax bundle (macros such as `\ket`, `\bra`,
`\ketbra`, `\braket` and `\tr` are available). In JSON every backslash is
doubled. Mark derivations that are not in the paper as editorial. Also supply
`methods_source_section` and `methods_basis`. The renderer links the source to
the paper's pinned arXiv HTML version. These sections appear on news articles
and in the shortlist for review before approval. The build and approval service
reject approved papers without methods. Base these explanations on the paper's
body, not just its abstract; distinguish editorial transfer suggestions from
results established by the authors.
