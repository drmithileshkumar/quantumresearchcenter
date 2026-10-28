# Quantum topic map

Open `index.html` directly or serve the repository and visit `/map/`. No external libraries, network requests, or build dependencies are needed at runtime.

The map contains 379 topics arranged as a parent–child tree. This is a curated starting taxonomy, not an exhaustive vocabulary or prerequisite graph. Fields overlap scientifically; each topic currently has one organizational parent.

Edit `BRANCHES` and `DESCRIPTIONS` in `build.py` to extend the taxonomy. Edit `template.html.in`, `map.css`, and `map.js` for the interface, then run:

```sh
python3 map/build.py
```

The builder generates `index.html` (including the accessible, JavaScript-free directory and embedded graph data) and `topics.json` (for reuse). Rebuild after asset changes to update cache versions.

Search matches the currently selected field and detail level. Select results, graph nodes, or directory links to view parents and children. Drag the background to pan or nodes to reposition them. Scroll or use the buttons to zoom. With the canvas focused, arrow keys pan, +/- zoom, and Home fits the graph. Topic URLs use stable hash IDs.
