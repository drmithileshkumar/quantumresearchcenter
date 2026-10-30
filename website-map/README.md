# Website graph

Visit `website-map/index.html` (also works directly from disk). This is a map of public HTML pages and actual hyperlinks, separate from the curated quantum topic map in `map/`.

Run `python3 scripts/build.py` to refresh the graph after adding or changing pages. `scripts/site_graph.py` combines generated page output with public HTML files, excluding redirects, noindex pages, and build inputs. Edges are undirected and deduplicated; links in navigation, headers, footers, and sidebars are classified as menu links and can be shown with the checkbox. Every public page remains a node, including pages without content connections.

The canvas has a bounded force simulation, section colours, node dragging, pan/zoom, search, and a local-neighbour view. Reduced-motion preferences disable animated layout. Search results and neighbour buttons support keyboard selection; the HTML directory provides ordinary links without JavaScript. No external libraries or runtime network requests are needed.

Click empty canvas space, click the selected node again, or press Escape to clear the selection. Reset also clears search and section filters, restores default links, and fits the complete graph.

The XML sitemap and this graph use the same public-page inventory. Newly added standalone pages and nested directories are discovered on the next main site build. Removed managed pages are excluded before their stale generated files are cleaned up. After changing the page set, run `python3 scripts/build.py` and include both map outputs; `--check` detects stale maps in CI.
