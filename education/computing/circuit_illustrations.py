"""Render circuit specifications with quantum wires and classical readout."""
from html import escape
from svgmath import svg_text, plain

class CircuitDrawing:
 def __init__(self,spec):
  panels=spec['circuits']; heights=[120+70*len(p['inputs'])+28*len(p.get('notes',[])) for p in panels]
  self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {52+sum(heights)}" role="img" aria-labelledby="title desc"><title id="title">{escape(plain(spec["title"]))}</title><desc id="desc">{escape(plain(spec["caption"]))} Read each circuit left to right.</desc><style>text{{font:17px Georgia,serif;fill:#26434b}}.small{{font:15px Arial,sans-serif}}.wire{{stroke:#476b70;stroke-width:2;fill:none}}.gate{{fill:#f8fbf9;stroke:#476b70;stroke-width:2}}</style>']
  self.text(480,28,spec['title'],'small')
  top=52
  for p,height in zip(panels,heights):
   n=len(p['inputs']);ys=[top+58+70*i for i in range(n)];cols=p['steps'];count=max(1,len(cols));xs=[240+i*480/max(1,count-1) for i in range(count)] if count>1 else [480]
   self.text(480,top+17,p.get('label',''),'small')
   measured={}
   for j,col in enumerate(cols):
    for gate in col:
     if gate.get('kind')=='measure':measured[gate['wires'][0]]=xs[j]
   for i,(label,y) in enumerate(zip(p['inputs'],ys)):
    self.text(150,y+5,label,anchor='end',width=145)
    end=measured.get(i,810);self.line(170,y,end,y)
    if i in measured:
     self.line(end,y-3,810,y-3);self.line(end,y+3,810,y+3)
    if i in p.get('bundles',[]):self.line(189,y+7,199,y-7)
    self.text(830,y+5,p.get('outputs',['']*n)[i],anchor='start',width=120)
   for j,col in enumerate(cols):
    x=xs[j]
    for gate in col:
     wires=gate['wires'];kind=gate.get('kind','gate');y=ys[wires[0]]
     assert all(0<=w<n for w in wires)
     if kind in ('cx','cz','swap'):
      y2=ys[wires[-1]];self.line(x,y,x,y2)
      if kind=='swap':
       for yy in (y,y2):self.line(x-8,yy-8,x+8,yy+8);self.line(x-8,yy+8,x+8,yy-8)
      else:
       self.parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#476b70"/>')
       if kind=='cz':self.parts.append(f'<circle cx="{x}" cy="{y2}" r="5" fill="#476b70"/>')
       else:
        self.parts.append(f'<circle class="gate" cx="{x}" cy="{y2}" r="14"/>');self.line(x-14,y2,x+14,y2);self.line(x,y2-14,x,y2+14)
     else:
      width=gate.get('width',min(100,430/count));h=ys[wires[-1]]-y+40
      self.parts.append(f'<rect class="gate" x="{x-width/2}" y="{y-20}" width="{width}" height="{h}" rx="3"/>')
      self.text(x,y-20+h/2+6,'M' if kind=='measure' else gate['label'],width=width-8)
   for i,note in enumerate(p.get('notes',[])):self.text(480,ys[-1]+52+28*i,note,'small',width=880)
   top+=height
  self.parts.append('</svg>\n')
 def text(self,x,y,value,cls='',anchor='middle',width=700):
  self.parts.append(svg_text(x,y,value,f' text-anchor="{anchor}" class="{cls}" data-max-width="{width}"'))
 def line(self,x,y,x2,y2):self.parts.append(f'<path class="wire" d="M{x} {y}L{x2} {y2}"/>')
 def save(self,path):path.write_text(''.join(self.parts))
