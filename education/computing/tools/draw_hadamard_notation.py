#!/usr/bin/env python3
"""Draw the Chapter 4 bridge from Hadamard arrows to ket notation."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svgmath import svg_text

parts=['''<svg data-linked-diagram="hadamard" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 470" role="group" aria-labelledby="title desc">
<title id="title">Hadamard transitions and their ket notation</title>
<desc id="desc">Two rows show each possible input separately. From input zero, arrows to zero and one both have amplitude one over square root two, giving H ket zero equals ket zero plus ket one, divided by square root two. From input one, the arrow to zero has positive amplitude and the dashed arrow to one has negative amplitude, giving H ket one equals ket zero minus ket one, divided by square root two.</desc>
<defs><marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#256a91"/></marker><marker id="arrow-violet" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#7757b8"/></marker></defs>
<style>text{font:19px Georgia,serif;fill:#263d4b}.label{font:14px Arial,sans-serif;fill:#596b78}.node{fill:#f5f8fb;stroke:#6e8796;stroke-width:1.5}.rule{stroke:#d4dfe6;stroke-width:1}</style>
<line class="rule" x1="28" y1="240" x2="872" y2="240"/>
''']
def text(x,y,label,attrs=''):parts.append(svg_text(x,y,label,attrs))
text(65,30,'Input',' class="label" text-anchor="middle"')
text(295,30,'After one H step',' class="label" text-anchor="middle"')
text(590,30,'The same transition in ket notation',' class="label" text-anchor="middle"')
for inp,cy in [(0,130),(1,355)]:
 for target,dy,color in [(0,-55,'blue'),(1,55,'violet')]:
  end=cy+dy;negative=inp==1 and target==1
  label=f'Input {inp} to output {target}: '+('minus ' if negative else '')+'one over square root two'
  parts.append(f'<g data-link="{inp}-{target}" class="diagram-link diagram-arrow" tabindex="0" role="button" aria-pressed="false" aria-label="{label}">')
  parts.append(f'<path class="diagram-hit" d="M86 {cy+dy*.1}L272 {end-dy*.08}" fill="none" stroke="transparent" stroke-width="22"/>')
  parts.append(f'<path d="M86 {cy+dy*.1}L272 {end-dy*.08}" fill="none" stroke="'+('#256a91' if color=='blue' else '#7757b8')+f'" stroke-width="2.4" marker-end="url(#arrow-{color})"'+(' stroke-dasharray="7 4"' if negative else '')+'/>')
  text(169,cy+dy*.6+(-14 if dy<0 else 25),r'\(-1/\sqrt2\)' if negative else r'\(1/\sqrt2\)',' text-anchor="middle"')
  parts.append('</g>')
  parts.append(f'<circle class="node" cx="295" cy="{end}" r="21"/>');text(295,end+6,str(target),' text-anchor="middle"')
 parts.append(f'<circle class="node" cx="65" cy="{cy}" r="21"/>');text(65,cy+6,str(inp),' text-anchor="middle"')
 text(440,cy+3,rf'\(H\ket{inp}=\)',' text-anchor="middle"')
 for target,x in [(0,555),(1,715)]:
  sign='-' if inp==1 and target==1 else '+'
  label=f'Term for input {inp} to output {target}'
  parts.append(f'<g data-link="{inp}-{target}" class="diagram-link diagram-term" tabindex="0" role="button" aria-pressed="false" aria-label="{label}">')
  parts.append(f'<rect class="term-halo" x="{x-58}" y="{cy-30}" width="116" height="55" rx="10" fill="transparent"/>')
  if target: text(635,cy+3,rf'\({sign}\)',' text-anchor="middle"')
  text(x,cy+3,rf'\(\frac{{1}}{{\sqrt2}}\ket{target}\)',' text-anchor="middle"')
  parts.append('</g>')
 text(590,cy+45,'Both outgoing amplitudes are positive.' if inp==0 else 'The minus sign belongs to the arrow ending at 1.',' class="label" text-anchor="middle"')
parts.append('</svg>')
(Path(__file__).resolve().parents[1]/'assets/figures/hadamard-ket-notation.svg').write_text(''.join(parts))
