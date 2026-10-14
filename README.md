# Quantum Research

A research handbook published at https://quantumresearch.center, organized into four parts and eleven chapters. The reading interface is inspired by the chapter-based structure of [qubit.guide](https://qubit.guide). The implementation and research descriptions are maintained independently.

## Editing and building

Edit `content/research.json` to update chapter titles, topic descriptions, open questions, and bibliography entries. Chapters have numbered sections. Every entry requires a unique ID, a description, and valid paper references. IDs determine URLs; retain them when changing titles.

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m unittest discover -s tests
python3 -m http.server 8000
```

Generated HTML is committed for GitHub Pages. `styles.css` and `script.js` control the responsive reading layout, contents search, and text-size control. No JavaScript framework or build dependencies are required. Navigation and all research content remain available without JavaScript.

The home page provides a site overview with links to Education, Research, and the bibliography. `/education/` lists available courses from `content/courses.json`; add entries there as new courses become available. The Quantum Computing course lives in `/education/computing/` and shares `styles.css` with the handbook. Rebuild it with `python3 education/computing/build.py` (Python 3.12+ and BeautifulSoup required), and validate with `python3 education/computing/tools/validate.py`. Its manuscript sources, interactive labs, and reader controls remain in the course folder. Topic pages contain scope and methods, research subsections, open problems where specified, and annotated references. `/references/` lists the bibliography. `/research/` contains the research introduction and full handbook contents.

## Publication

`CNAME` configures `quantumresearch.center`. Preserve it and `.nojekyll` when publishing. The build generates the sitemap and robots file. The site contains no registration service or consulting catalog.

Reference years indicate first arXiv submission. These entries are concise research overviews, not comprehensive literature surveys.
