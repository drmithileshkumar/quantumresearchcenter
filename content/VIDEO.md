# Article videos

`scripts/videos.py` turns a news article into a narrated 1080p video. The
narration is the article itself, read in full and in order: the headline, the
standfirst, then each section's kicker and heading and its paragraphs. The
script adds only the pictures: scenes drawn as HTML in the site's style,
recorded frame by frame in headless Chrome and encoded with ffmpeg. Everything it makes goes to
`_video/<slug>/`, which git ignores and the site never publishes. Videos are not
yet linked from the site; that waits for a hosting decision (see the end).

The pipeline is built to be improved by repetition: every run measures the video
against fixed targets, writes a review page, and records the result, so each
change to a script or to the pipeline can be judged against the last run.

## Setup (once)

```sh
python3 -m venv _video/venv
_video/venv/bin/pip install -r requirements-video.txt
```

Chrome or Chromium must be installed (set `CHROME` if it is not on `PATH`).
The first run with a Piper voice downloads it (60 to 115 MB) into `_video/voices/`.

## Commands

```sh
python3 scripts/videos.py check                      # validate every script; no dependencies
_video/venv/bin/python scripts/videos.py stills <slug>               # speech + one still per scene + review page
_video/venv/bin/python scripts/videos.py stills <slug> --voice silent # layout only, in seconds
_video/venv/bin/python scripts/videos.py build <slug>                # the video, captions and transcript
```

Options: `--voice silent | piper:<voice> | recorded`, `--fps`, `--theme light|dark`,
and `--scenes id,id` (stills only). Speech is cached per sentence and video per
scene, so after the first build only the scenes you changed are spoken and
rendered again.

Outputs in `_video/<slug>/`: `<slug>.mp4`, `<slug>.vtt` (captions),
`<slug>.txt` (transcript), `review/index.html` (the review page), and
`history.jsonl` (one line per run).

## Writing a script

A script is `content/news-videos/<slug>.json`; shared settings (voice, pace,
pauses, targets, pronunciation lexicon) are in `content/news-videos/_style.json`.
`beyond-the-qubit-count.json` is the worked example.

The words are the article's, so accuracy and sourcing are settled there: to
change what is said, edit the article. The script decides what is on screen
while each part is read, and the pictures follow the article's rules: every
number shown is in the article or its sources, attributed through the scene's
`source` line, and our own calculations or extrapolations say so. Prefer the
article's own figures, stats, tables and questions to new material.

- `from`: a phrase from the sentence where the scene starts. Each scene runs
  until the next one starts, so the scenes always cover the whole article once,
  in order; `check` reports a phrase that is missing or out of order, and an
  article whose opening is not narrated. A scene without `from` is silent and
  needs `hold` (the sources card at the end).
- `"on"` on any visual element makes it appear when a phrase of the scene's
  narration is spoken, for example `"on": "suppression factor"`. The time is
  placed by the phrase's position in its sentence (there are no word timings
  yet); a number `k` means the start of sentence `k` of the scene, and
  `"delay"` adds seconds. The phrase must occur in exactly one sentence of the
  scene. Every sentence should change the picture or deliberately hold it; the
  review flags long holds.
- Every scene takes `id`, `layout`, `from`, and optionally `section`
  (top-right label), `heading`, `source`, `pause` (between sentences), `hold`
  (seconds of reading time at the end, not counted as a stalled picture) and
  `rate` (speaking speed for the scene, for example 0.92 to slow down; the
  words cannot change, so this is how a dense passage gets more time).
- Formulas in the article (`\(...\)`) are read aloud by a small TeX reader
  (`2^{n/2}` becomes "2 to the power n over 2") and typeset in the captions.
  When a reading is wrong or the reader does not know a command, `check` says
  so; add the formula to `tex` in `_style.json` with how it should be said.
  Words the voice mispronounces go in `lexicon` (or the script's own
  `lexicon`, for one article).

| Layout | Fields |
|---|---|
| `title` | `headline`, `kicker`, `deck` (text or `{"text","on"}`), `banner` (`true` or `{"on"}`: the article banner) |
| `statement` | `text`, `sub` |
| `points` | `items`: text, `{"text","on"}` or `{"tex","on"}`; inline maths as `\(..\)` |
| `stats` | `stats`: `{"value","label","on"}` |
| `figure` | `figure` (an SVG in the article's figures folder), `steps`, `notes` |
| `equation` | `lines`: `{"tex","note","on"}` |
| `table` | `columns`, `rows` (`{"cells","on"}`; a cell may be `{"text","on"}`), `column_on` (one cue per column), `footer`, `small` |
| `columns` | `columns`: `{"title","items"}` (for shown / claimed / open) |
| `sources` | `items` (defaults to the article's sources), `url` |

Figures animate by mark groups: in the SVG, every top-level element with its own
`<title>` starts a group, and the untitled marks after it belong to it. A step
`{"series": [0, 2], "on": 3}` draws groups 0 and 2 from left to right when
sentence 3 starts. Give each mark you want to reveal separately a title in the
figure's `draw.py`; titles also make the article figure more accessible.

## The improvement loop

1. Run `stills` and open `review/index.html`. Fix every automatic flag, or
   decide it is acceptable.
2. Run `build` and watch the whole video once, scoring it against the rubric
   below. Note the weakest item.
3. Change the script (or the pipeline, if the problem is general), add a line
   to the script's `revisions` saying what changed and why, and run again.
   The command prints how flags and length moved since the last run.
4. When the video scores at least 4 on every rubric item, set `status` to `ready`.

Fix problems where they start: a mispronounced word goes in the lexicon, a
passage that listens badly is rewritten in the article, and a layout that overflows for every article is a CSS fix,
not a shorter sentence in one script.

### Automatic checks (targets in `_style.json`)

| Check | Target | Why |
|---|---|---|
| Pace | 140 to 175 words a minute per scene | Slower than news reading; dense content needs time |
| Caption speed | at most 20 characters a second | Readable while watching the picture |
| Longest hold | at most 12 s without a visual change | Keeps the picture tied to the narration |
| Scene length | at most 60 s | Longer scenes should be split |
| Text size | at least 26 px at 1080p; chart labels about the same | Legible on a phone held sideways |
| Layout | nothing outside the content area, no three-line captions, no MathJax errors | Checked on the fully revealed scene |
| Loudness | −16 LUFS integrated, within 1.5 | Platform standard for speech |

### Human rubric (score 1 to 5)

1. **Accuracy**: everything shown matches the article and its sources;
   estimates and extrapolations are labelled. (The spoken words are the article.)
2. **Sourcing**: the source of each claim is on screen while it is made.
3. **Explanation**: at least one idea is shown being derived or built, not
   just stated; a newcomer could follow it.
4. **Picture and words agree**: each element appears as it is read; nothing
   on screen is unexplained. Watch for article wording that points at the page
   ("the table below", "the numbers above"): the thing it names must be on screen.
5. **Voice**: names, numbers and terms pronounced correctly; natural pauses.
6. **Pace and length**: no stretch drags or rushes; tables and charts stay up
   long enough to read.
7. **Legibility**: readable on a phone; captions never cover content.
8. **Status is clear**: shown, claimed and still open are distinguishable.

## Pipeline backlog (in order of expected gain)

- **Voice quality.** Piper (`en_US-lessac-high`) is local and free but flat.
  The `Silent`/`Piper` classes in `videos.py` show the interface (`key`,
  `synth`); a cloud voice or a recorded human voice (`--voice recorded`, one
  file per scene in `content/news-videos/<slug>/<scene>.wav`) is the biggest
  single improvement.
- **Word-level timing.** Phrase cues and caption chunks are placed by their
  position in the sentence; a forced aligner (or Piper's phoneme timings) would
  put them on the spoken word.
- **Writing for the ear.** The narration is the article, so a passage that
  reads well but listens badly is fixed in the article; note such passages
  while reviewing.
- **Richer motion.** Equations built term by term; highlighting a table cell or
  chart point as it is discussed; transitions between scenes.
- **Vertical cut.** A 1080×1920 layout set for social platforms from the same script.
- **Publishing.** An optional `video` field on articles (hosted URL and
  transcript), shown on the article page with the transcript below it.
