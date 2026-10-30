# Quantum companies by country

Edit `content/companies.json`, then run `python3 scripts/build.py`. The page is linked beside Conferences in the editorial footer and from the conference directory; it is included in the sitemap and website graph.

Each entry includes a stable ID, company name, documented country and city base, focus areas, short description, official website, official supporting sources, and a review date. Group by the documented base of the listed company, not every office, customer location, or its parent company's nationality. This is a curated selection of specialist companies, not an exhaustive ranking or a list of every corporate quantum programme. Avoid unsupported performance claims; distinguish quantum communication from classical post-quantum cryptography.

Sources should support both the location and the activity. Update entry dates after reviewing them, and keep the directory date at least as recent as every entry. All entries work without JavaScript. JavaScript adds combined text/country/focus filtering, visible counts, reset, and no-results feedback. Country shortcuts clear restrictive filters before jumping.

Checks: `python3 scripts/build.py --check`, `python3 -m unittest discover -s tests`, and `node --check companies/companies.js`.

## Country map

The directory shares the Conferences Natural Earth basemap, including its documented boundary view. Country buttons and SVG countries/markers filter the company list. Selecting the same country again, or choosing “Show all countries”, clears that filter. Counts follow search and focus filters independently of the selected country. The map represents company country bases, not precise offices. The HTML country directory remains usable without JavaScript.
