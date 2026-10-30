# Frontier maps

A frontier map shows what is known and unknown in one field. Edit `content/frontiers/<field>.json`, then run:

```sh
python3 frontiers/build.py
```

The builder writes `frontiers/<field>/index.html` and one page per node. `--check` reports stale pages.

Each node carries two separate labels. The field's status lives in the JSON: `established`, `partial`, `conjectured`, `open`, `claimed` (a recent result without independent confirmation), or `refuted` (the statement shown is false). The reader's own coverage, notes, and trail stay in `localStorage` and can be exported as a backup or a Markdown research log.

The build fails if a node has no source, cites an unknown paper, links to a missing node, or sits on the frontier without saying what is unknown. Check each new source against its own text, and update the top-level `checked` date when you recheck the map.

The pilot pages are `noindex`, so they stay out of `sitemap.xml` and the website map. To publish a map, remove the robots tag from `head()` in `build.py`, link it from a public page, then run `python3 scripts/build.py` and include the updated maps, as `AGENTS.md` requires.
