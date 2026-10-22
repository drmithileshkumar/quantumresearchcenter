"""Render a recursive, progressively enhanced topic graph for the home page."""
import html
import json

def render_quantum_map(root):
    data = json.loads((root / 'content/quantum-map.json').read_text())
    def node(item, depth=0):
        title = html.escape(item['title'])
        if 'children' not in item:
            return '<li><a class="qm-node qm-leaf" href="'+html.escape(item['href'], quote=True)+'">'+title+'<span aria-hidden="true"> ↗</span></a></li>'
        children = ''.join(node(child, depth + 1) for child in item['children'])
        return (f'<li><details class="qm-branch" data-depth="{depth}"'+(' open' if depth == 0 else '')+'>'
                f'<summary class="qm-node">{title}<span class="qm-count" aria-hidden="true">{len(item["children"])}</span></summary>'
                '<ul>'+children+'</ul></details></li>')
    return '''<section class="quantum-map" id="quantum-world" aria-labelledby="qm-title">
<link rel="stylesheet" href="quantum-map.css">
<div class="qm-heading"><div><p class="kicker">One connected field</p><h2 id="qm-title">Map of the quantum world</h2></div>
<div class="qm-controls" hidden><button type="button" data-qm-expand>Expand next level</button><button type="button" data-qm-reset>Reset map</button></div></div>
<p id="qm-help">Click a node to expand or collapse its branches. Follow the arrows at the tips to explore a lesson or research question. Scroll within the map to follow wider branches.</p>
<div class="qm-viewport" tabindex="0" role="region" aria-label="Quantum world topic graph" aria-describedby="qm-help"><ul class="qm-tree">'''+node(data)+'''</ul></div>
<p class="qm-note">A guide to connected ideas, not rigid boundaries: entanglement, measurement, noise, and control run across all four fields.</p>
<p class="visually-hidden" role="status" data-qm-status></p><script defer src="quantum-map.js"></script></section>'''
