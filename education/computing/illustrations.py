"""Build accessible SVG schematics for subsections without manuscript figures."""
from pathlib import Path
from html import escape
import json, math
from svgmath import plain, svg_text, wrap
ROOT=Path(__file__).resolve().parent
SPECS=json.loads((ROOT/'content/illustrations.json').read_text())
COLORS=['#246593','#a64d26','#347449','#765391']
def lines(value,width):
 return wrap(value,max(8,int(width/8.5)))
class Drawing:
 def __init__(self,spec,height):
  description=plain(spec['caption'])+' '
  if spec['kind'] in ('table','flow'):
   if spec.get('headers'):description+='Columns: '+', '.join(spec['headers'])+'. '
   description+='; '.join(' → '.join(row) if spec['kind']=='flow' else ', '.join(row) for row in spec['rows'])
  elif spec['kind']=='bars':description+='; '.join(f'{label}: {value:g}' for label,value in zip(spec['labels'],spec['values']))
  elif spec['kind']=='decision':description+='; '.join(spec['nodes'])
  else:description+='; '.join(f'{label}: {angle} degrees' for label,angle in zip(spec['labels'],spec['angles']))
  description=plain(description)
  self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(plain(spec["title"]))}</title><desc id="desc">{escape(description)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs><style>text{{font:16px Georgia,serif;fill:#30343b}}.heading{{font:600 15px system-ui,sans-serif;fill:#246593}}.small{{font:14px system-ui,sans-serif;fill:#4b5864}}.grid{{stroke:#d3dee7;stroke-width:1}}.edge{{fill:none;stroke:#246593;stroke-width:1.7;marker-end:url(#arrow)}}</style>']
  self.text(380,30,spec['title'],'heading',maxwidth=700)
 def text(self,x,y,value,cls='',anchor='middle',maxwidth=700):
  self.parts.append(svg_text(x,y,value,f' text-anchor="{anchor}" class="{cls}" data-max-width="{maxwidth:g}"'))
 def multiline(self,x,y,value,width,cls=''):
  ls=lines(value,width)
  for i,line in enumerate(ls):self.text(x,y+(i-(len(ls)-1)/2)*22,line,cls,maxwidth=width)
 def box(self,x,y,w,h,value,accent=False):
  self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="5" fill="{"#eaf1f7" if accent else "#fff"}" stroke="#a7bccd"/>')
  self.multiline(x+w/2,y+h/2+5,value,w-22)
 def edge(self,x,y,x2,y2,color=None,dashed=False):
  self.parts.append(f'<path d="M{x:g} {y:g}L{x2:g} {y2:g}" class="edge"'+(f' style="stroke:{color}"' if color else '')+(' stroke-dasharray="5 4"' if dashed else '')+'/>')
 def save(self,path):path.write_text(''.join(self.parts)+'</svg>\n')
def render(spec):
 kind=spec['kind']
 if kind=='flow':
  heights=[max(70,22*max(len(lines(cell,(696-(len(row)-1)*28)/len(row)-22)) for cell in row)+24) for row in spec['rows']]
  d=Drawing(spec,70+sum(heights)+24*(len(heights)-1));y=54
  for row,h in zip(spec['rows'],heights):
   w=(696-(len(row)-1)*28)/len(row)
   for i,cell in enumerate(row):
    x=32+i*(w+28);d.box(x,y,w,h,cell,i==len(row)-1)
    if i<len(row)-1:d.edge(x+w,y+h/2,x+w+28,y+h/2)
   y+=h+24
 elif kind=='table':
  rows=[spec['headers'],*spec['rows']];w=696/len(rows[0]);heights=[max(48,22*max(len(lines(cell,w-22)) for cell in row)+18) for row in rows]
  d=Drawing(spec,70+sum(heights));y=54
  for n,(row,h) in enumerate(zip(rows,heights)):
   for i,cell in enumerate(row):
    x=32+i*w;d.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{"#eaf1f7" if n==0 else "#fff" if n%2 else "#f5f8fa"}" class="grid"/>')
    d.multiline(x+w/2,y+h/2+5,cell,w-22,'small' if n==0 else '')
   y+=h
 elif kind=='decision':
  d=Drawing(spec,330)
  d.box(35,75,230,80,spec['nodes'][0]);d.edge(265,115,325,115)
  d.box(325,75,190,80,spec['nodes'][1],True)
  d.edge(515,100,565,100);d.box(565,65,160,70,spec['nodes'][2],True)
  d.edge(420,155,420,215);d.box(310,215,250,80,spec['nodes'][3])
  d.parts.append('<path d="M310 255H150V155" class="edge"/>')
 elif kind=='bars':
  d=Drawing(spec,330);baseline=266;scale=180
  for v in [0,.25,.5,.75,1]:
   y=baseline-v*scale;d.parts.append(f'<path d="M85 {y:g}H715" class="grid"/>');d.text(68,y+5,f'{v:g}','small')
  d.text(88,60,'Probability','small','start')
  step=600/len(spec['labels']);w=min(74,step*.55)
  for i,(label,value) in enumerate(zip(spec['labels'],spec['values'])):
   x=105+(i+.5)*step;top=baseline-value*scale
   d.parts.append(f'<rect x="{x-w/2:g}" y="{top:g}" width="{w:g}" height="{value*scale:g}" fill="#246593"/>')
   d.text(x,top-12,f'{value:g}','small');d.text(x,298,label,'small',maxwidth=step-10)
 elif kind=='plane':
  d=Drawing(spec,430);cx=225;cy=230;r=115
  d.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#c4d1dc"/>')
  d.edge(70,cy,390,cy,'#6b7885');d.edge(cx,380,cx,75,'#6b7885')
  d.text(cx,409,spec['axes'][0],'small',maxwidth=350);d.text(cx,60,spec['axes'][1],'small',maxwidth=350)
  for i,(angle,label) in enumerate(zip(spec['angles'],spec['labels'])):
   a=math.radians(angle);color=COLORS[i%len(COLORS)];x=cx+r*math.cos(a);y=cy-r*math.sin(a)
   d.edge(cx,cy,x,y,color,dashed=i==1)
   d.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="4" fill="{color}"/>')
   ly=115+i*74;d.parts.append(f'<path d="M425 {ly}H455" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="5 4"' if i==1 else '')+'/>')
   d.multiline(600,ly+5,label,260,'small')
 else:raise ValueError(f'Unknown illustration kind: {kind}')
 return d

def build():
 directory=ROOT/'assets/figures/subsections';directory.mkdir(exist_ok=True)
 for ident,spec in SPECS.items():render(spec).save(directory/(ident+'.svg'))
if __name__=='__main__':
 build();print(f'Built {len(SPECS)} subsection illustrations.')
