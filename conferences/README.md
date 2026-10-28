# Conference directory

Visit `/conferences/` or open `index.html`. The collection works without JavaScript; JavaScript adds search, combined filters, date ranges, and sorting. The page shares the site's navigation, typography, and theme controls.

## Maintaining the collection

Edit `content/conferences.json`, then run `python3 scripts/build.py`. Do not hand-edit the generated HTML. The main build includes this page in the sitemap and checks local links and asset versions.

Each conference edition has a unique ID, name, full name, country, city, year, ISO start/end dates, description, quality category and rationale, official URL, source URL, and last checked date. Use `null` for **both** dates when an announced edition has no confirmed dates. Do not infer next year's dates or location from a past edition. Verify changes with organizers and update the checked dates.

Quality categories are editorial descriptions, not official rankings. Explain the supporting evidence per entry and avoid guessed acceptance rates. Keep industry forums distinct from scientific research meetings.

Date ranges select events that overlap the chosen interval. Undated events are excluded when a date boundary is set. Status is calculated in the visitor's local date; static HTML shows status as of the collection's checked date. Default sorting puts ongoing and upcoming events first, undated editions next, and past editions last. Past editions remain searchable.

Verification:

```sh
python3 scripts/build.py --check
python3 -m unittest discover -s tests
node --check conferences/conferences.js
```

## World map

The inline SVG uses local `world-map.json`, derived from Natural Earth’s public-domain 1:110m admin-0 country GeoJSON. Source: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson. License: https://www.naturalearthdata.com/about/terms-of-use/. Coordinates use an equirectangular projection; Antarctica is omitted. Singapore has a point marker because its polygon is absent at this resolution. Markers indicate countries, not conference venues; crowded markers have leader lines.

The map and country buttons share the country filter. Counts reflect all other filters so alternative destinations stay discoverable. Selecting the same country again clears the country selection. The static map remains visible without JavaScript; the country buttons are enabled when filtering is available.

### India boundary view

The map shows India’s claimed extent of Jammu and Kashmir, including Pakistan- and China-administered areas. This is explicitly identified in the map caption as a claim view, not administrative control. The India polygon merges the Natural Earth 1:110m base with the 1:10m disputed-region polygons B03 (Demchok), B05 (Jammu and Kashmir), B06 (Shaksam/Shaksgam Valley), B07 (Aksai Chin), B08 (Gilgit-Baltistan), B09 (Azad Kashmir), and B45 (Siachen Glacier). The merged area is subtracted from the Pakistan and China display polygons to avoid overlapping country hit targets. Source and region identifiers are retained in `world-map.json` under `boundary_view`.
