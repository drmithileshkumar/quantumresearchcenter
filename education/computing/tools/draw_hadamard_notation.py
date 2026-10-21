#!/usr/bin/env python3
"""Draw the Chapter 4 bridge from Hadamard arrows to ket notation."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svgmath import svg_text

parts=['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 470" role="img" aria-labelledby="title desc">
<title id="title">Hadamard transitions and their ket notation</title>
<desc id="desc">Two rows show each possible input separately. From input zero, arrows to zero and one both have amplitude one over square root two, giving H ket zero equals ket zero plus ket one, divided by square root two. From input one, the arrow to zero has positive amplitude and the dashed arrow to one has negative amplitude, giving H ket one equals ket zero minus ket one, divided by square root two.</desc>
<defs><marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#256a91"/></marker><marker id="arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#a3542e"/></marker></defs>
<style>text{font:19px Georgia,serif;fill:#263d4b}.label{font:14px Arial,sans-serif;fill:#596b78}.node{fill:#f5f8fb;stroke:#6e8796;stroke-width:1.5}.rule{stroke:#d4dfe6;stroke-width:1}</style>
<line class="rule" x1="28" y1="240" x2="872" y2="240"/>
''']
def text(x,y,label,attrs=''):parts.append(svg_text(x,y,label,attrs))
text(65,30,'Input',' class="label" text-anchor="middle"')
text(295,30,'After one H step',' class="label" text-anchor="middle"')
text(590,30,'The same transition in ket notation',' class="label" text-anchor="middle"')
for inp,cy in [(0,130),(1,355)]:
 for target,dy,color in [(0,-55,'blue'),(1,55,'orange')]:
  end=cy+dy;negative=inp==1 and target==1
  parts.append(f'<path d="M86 {cy+dy*.1}L272 {end-dy*.08}" fill="none" stroke="'+('#256a91' if color=='blue' else '#a3542e')+f'" stroke-width="2.4" marker-end="url(#arrow-{color})"'+(' stroke-dasharray="7 4"' if negative else '')+'/>')
  text(169,cy+dy*.6+(-14 if dy<0 else 25),r'\(-1/\sqrt2\)' if negative else r'\(1/\sqrt2\)',' text-anchor="middle"')
  parts.append(f'<circle class="node" cx="295" cy="{end}" r="21"/>');text(295,end+6,str(target),' text-anchor="middle"')
 parts.append(f'<circle class="node" cx="65" cy="{cy}" r="21"/>');text(65,cy+6,str(inp),' text-anchor="middle"')
 text(590,cy+3,r'\(H\ket0=\frac{1}{\sqrt2}\ket0+\frac{1}{\sqrt2}\ket1\)' if inp==0 else r'\(H\ket1=\frac{1}{\sqrt2}\ket0-\frac{1}{\sqrt2}\ket1\)',' text-anchor="middle"')
 text(590,cy+45,'Both outgoing amplitudes are positive.' if inp==0 else 'The minus sign belongs to the arrow ending at 1.',' class="label" text-anchor="middle"')
parts.append('</svg>')
(Path(__file__).resolve().parents[1]/'assets/figures/hadamard-ket-notation.svg').write_text(''.join(parts))
