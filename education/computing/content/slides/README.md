# Chapter lecture slides

Each `NN-*.json` file is a list of slides for one chapter. `presentations.py` turns it into
`NN-*-slides.html`; never edit the generated HTML. Every slide has a `kind`:

| kind | fields | use it for |
|---|---|---|
| `section` | `number`, `title`, `question` | a divider that poses the section's driving question |
| `figure` | `title`, `figure`, `lead`?, `takeaway`? | one chapter figure, shown large |
| `steps` | `title`, `lead`?, `steps`, `takeaway`? | a derivation revealed one line at a time |
| `predict` | `title`, `question`, `answer`, `hint`? | the question first, the answer on the next key press |
| `compare` | `title`, `left`, `right`, `takeaway`? | two columns, each `{label, items}` |
| `statement` | `title`, `label`, `statement`, `note`? | a postulate, definition, or quoted theorem in a box |
| `table` | `title`, `headers`, `rows`, `takeaway`? | a small comparison table |
| `takeaways` | `title`, `items` | the chapter's conclusions |
| `content` | `title`, `blocks` or `columns`, `figure`?, `figure_side`?, `caption`? | a full lecture slide (the default) |

A `content` slide holds `blocks` (or `columns`: two lists of blocks). A block is one of
`{"p": text}`, `{"math": "\\[...\\]"}`, `{"ul": [...]}`, `{"ol": [...]}`, `{"note": text}`,
`{"box": {"label", "text"}}` (a definition, postulate, or theorem) or `{"table": {"headers", "rows"}}`;
any block may set `"reveal": true`. A `figure` is drawn to the right of the text, or `"figure_side": "below"`.

Content slides name the subsection they teach in `topic` (or `topics`). The build fails
if a chapter subsection has no slide, if a topic is unknown, or if a figure is not used
in the chapter (figures live under `assets/figures/`; subsection illustrations are also allowed).
`notes` holds the presenter's fuller explanation: the Notes button (or N) shows it; it is never projected or printed.

Write slides as lecture slides, not as a quiz. Titles are short topic names; section dividers state
what the section does. Each content slide teaches one subsection, or one step of its argument: the
claim, the reasoning or calculation that establishes it, and a worked example, with definitions and
postulates in boxes. Put asides and longer explanations in `notes`. Prefer `content` slides; the older
kinds remain for special cases. The build does not measure text, so render the deck and check that
nothing reaches the footer or runs under a figure.

Presenting: → or Space reveals the next step, then advances; ← steps back; Home/End jump;
N opens notes; F toggles fullscreen; Print / PDF prints one slide per landscape page with every step shown.
Slides are 16:9 and scale with the window, so they look the same on a laptop, a projector, and a PDF.

Build with `python3 education/computing/build.py`, then `python3 education/computing/tools/validate.py`.
