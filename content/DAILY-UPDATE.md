# Daily news update

The scheduled cloud routine follows this procedure once a day. It extends
[PAPERS.md](PAPERS.md) and [NEWS.md](NEWS.md); read both first. The routine
approves its own selections and pushes to `main`, so every check below is a
publishing gate, not a suggestion. If a gate fails and cannot be fixed, publish
nothing (or only the parts that pass) and say so in the final report.

## 0. Start clean

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests
```

If either fails before you change anything, stop and report: the repository
is already inconsistent and someone must look at it.

Let `TODAY` be today's date (UTC). If `content/papers.json` already has
papers with `approved_on` equal to `TODAY`, the update has already run; stop.

## 1. Papers: fetch

```sh
cp content/arxiv-inbox.json /tmp/inbox-backup.json
python3 scripts/arxiv_papers.py fetch --days 4 --limit 80 --as-of TODAY
```

- arXiv indexing lags about two days, so `--days 2` often returns nothing;
  use `--days 4` and pick papers not already in `content/papers.json`.
- The API can be slow (about 30 s a request) and rate-limits with HTTP 429.
  `--limit 200` exceeds the script's timeout; 80 works. Wait at least
  3 seconds between requests, and longer after a 429; retry at most three times.
- An empty fetch overwrites the inbox. If it comes back empty, restore
  `/tmp/inbox-backup.json`.

## 2. Papers: choose two per area

Shortlist two papers for each of `foundations`, `computing` and
`information` (six in total). Prefer substantive theorems or experiments
with a clear question and result over incremental or purely numerical work.
Skip any ID already in `papers.json`. If an area has no paper worth covering,
cover fewer rather than padding.

## 3. Papers: write the entries

Read each paper's full arXiv HTML (`https://arxiv.org/html/<id>v<N>`; fall
back to the PDF), not just the abstract. Write the entry in the existing
schema, at the depth of the most recent approved entries (compare two of them
before writing):

- `problem`, `result`, `significance`, `limitations`, `kind`, `version`,
  `submitted`, `verified_on: TODAY`, `summary_basis`, `topic`.
- `description`: paragraphs on the setting, the precise question, the main
  theorem or measurement, and what remains open.
- `methods`: two techniques, each with `explanation`, `math` (paragraphs that
  derive the idea: definitions, the key identity or inequality, why it works)
  and `transfer`. Mark derivations that are not in the paper as editorial.
  Set `methods_source_section` and `methods_basis`.
- Voice: plain, direct prose with no filler, and no bare lists of facts. Say
  what problem forced each idea.

Check claims numerically wherever you can (a short Python script): rederive
special cases from the paper's general theorem and check that the stated
limits and constants agree. Published formulas do contain errors (2610.32923
had a sign error in a special case). If the paper is wrong, say so in the
entry; do not copy the error.

### TeX rules (these broke previous entries)

- Write entries from Python with raw strings. In a plain string, `\t`, `\f`,
  `\n`, `\b` turn `\times`, `\frac`, `\nu`, `\beta` into control characters
  without any error. A prime (`M'`) ends a `r'...'` string, so use
  triple-quoted raw strings or `^\prime`.
- After writing, scan `papers.json` for `[\x00-\x1f]` inside strings. There
  must be none.
- `\boldsymbol` is not loaded; use `\mathbf`. The site's `\braket` takes two
  arguments; write expectation values as `\langle X\rangle`.
- Long inline math (`\(...\)`) overflows on phones, since only display math
  (`\[...\]`) scrolls in its own box. Put any long formula in display math,
  with its punctuation inside.

## 4. Papers: approve and build

Add the entries as `candidate`, update the collection's `reviewed_on`, then:

```sh
python3 scripts/arxiv_papers.py approve <id> <id> ... --date TODAY
python3 scripts/build.py
```

If headless Chrome or Chromium is available, render each new paper page
(`--dump-dom` after MathJax has finished, with an isolated `--user-data-dir`)
and grep for `data-mjx-error`. Fix every error and rebuild. If no browser is
available, check the TeX by eye against the rules above, and note in the report
that the pages were not rendered.

## 5. Article (only when the news justifies one)

Search for quantum-technology news from the past three days: experiments,
companies, government programmes, notable results. Publish an article only
if a story is substantive and covered by at least one primary source (a
paper, an official announcement, a company release) plus a reputable report,
and if it is not already covered in `content/news-articles/`. Most days
there will be nothing; then skip this step and say so in the report.

When writing one, follow the schema in NEWS.md: `status: "published"`,
`published: TODAY`, `author: "Quantum Research Center"`, attributed claims,
explicit announcement dates, a clear line between goals, funding,
demonstrations and products, and `source_refs` on the sections. Link
`related_papers` when an approved paper is relevant. Do not add figures.

## 6. Gate and publish

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests
git status
```

Both must pass. `git status` must show changes only under `content/`,
`news/`, the homepage, `sitemap.xml` and other build outputs; an
unexpected file means something went wrong. Then commit with the message
`news: daily update TODAY` and push to `main`.

## 7. Report

End with a short report: the papers approved (ID, title, area), whether an
article was published and why or why not, any gate that failed or step that
was skipped, and any error found in a paper.
