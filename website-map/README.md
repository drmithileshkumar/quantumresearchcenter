# Website graph

Visit `website-map/index.html` (also works directly from disk). This is a map of public HTML pages and actual hyperlinks, separate from the curated quantum topic map in `map/`.

Run `python3 scripts/build_all.py` to refresh the graph after adding or changing pages. `scripts/site_graph.py` combines generated page output with public HTML files, excluding redirects, noindex pages, and build inputs. Edges are undirected and deduplicated; links in navigation, headers, footers, and sidebars are classified as menu links and can be shown with the checkbox. Every public page remains a node, including pages without content connections.

The canvas has a bounded force simulation, section colours, node dragging, pan/zoom, search, and a local-neighbour view. Reduced-motion preferences disable animated layout. Search results and neighbour buttons support keyboard selection; the section pages in `website-map/sections/` provide ordinary links without JavaScript. The graph data lives in `website-map/data.js`, loaded with a script tag so the map still works from disk; edges refer to nodes by position to keep it small. No external libraries are needed, and repulsion uses a grid so that layout stays fast with thousands of pages.

Click empty canvas space, click the selected node again, or press Escape to clear the selection. Reset also clears search and section filters, restores default links, and fits the complete graph.

The XML sitemap and this graph use the same public-page inventory. Newly added standalone pages and nested directories are discovered on the next main site build. Removed managed pages are excluded before their stale generated files are cleaned up. Both are build output, so they are always current in a deployment and are not committed.
