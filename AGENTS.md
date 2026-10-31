# Site maps

Public pages, `website-map/` and `sitemap.xml` are build output and are not committed. Whenever adding, renaming, or removing a public page, run `python3 scripts/build_all.py`, then `python3 scripts/check_site.py` to ensure every link resolves and every page is reachable. The shared inventory automatically discovers public HTML pages, including standalone pages and nested directories; redirects, noindex pages, and build inputs are excluded.
