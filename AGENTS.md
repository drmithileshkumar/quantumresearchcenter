# Site maps

Whenever adding, renaming, or removing a public page, run its relevant content builder first, then run `python3 scripts/build.py`. Include the resulting `website-map/index.html` and `sitemap.xml` updates with the page change. Run `python3 scripts/build.py --check` to ensure both maps are current. The shared inventory automatically discovers public HTML pages, including standalone pages and nested directories; redirects, noindex pages, and build inputs are excluded.
