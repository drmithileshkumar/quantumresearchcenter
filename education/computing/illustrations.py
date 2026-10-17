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
  elif spec['kind']=='paths':description+='; '.join(path['label']+': '+' → '.join(path['states'])+'; weights '+', '.join(path['weights'])+'; '+path['result'] for path in spec['paths'])
  elif spec['kind']=='network':description+='; '.join(edge['start']+' → '+edge['end']+': '+edge['label'] for edge in spec['edges'])
  elif spec['kind']=='phasor':description+='A vector from the origin, its phase angle, and its projections onto the real and imaginary axes.'
  elif spec['kind']=='bars':description+='; '.join(f'{label}: {value:g}' for label,value in zip(spec['labels'],spec['values']))
  elif spec['kind']=='decision':description+='; '.join(spec['nodes'])
  elif spec['kind']=='transitions':description+=' '.join('; '.join(f'{a} → {b}'+(f' (weight {w})' if w else '') for _,a,b,*rest in panel['edges'] for w in [rest[0] if rest else ''])+'.' for panel in spec['panels'])
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
 if kind=='circuit':
  from circuit_illustrations import CircuitDrawing
  return CircuitDrawing(spec)
 if kind=='flow':
  heights=[max(70,22*max(len(lines(cell,(696-(len(row)-1)*28)/len(row)-22)) for cell in row)+24) for row in spec['rows']]
  d=Drawing(spec,70+sum(heights)+24*(len(heights)-1));y=54
  for row,h in zip(spec['rows'],heights):
   w=(696-(len(row)-1)*28)/len(row)
   for i,cell in enumerate(row):
    x=32+i*(w+28);d.box(x,y,w,h,cell,i==len(row)-1)
    if i<len(row)-1:d.edge(x+w,y+h/2,x+w+28,y+h/2)
   y+=h+24
 elif kind=='paths':
  d=Drawing(spec,76+140*len(spec['paths']))
  for x,time in zip((180,380,580),(0,1,2)):
   d.text(x,59,f'Time {time}','small')
  for n,path in enumerate(spec['paths']):
   y=126+140*n
   d.text(38,y-37,path['label'],'heading','start',maxwidth=680)
   for x,state in zip((180,380,580),path['states']):
    d.parts.append(f'<circle cx="{x}" cy="{y}" r="23" fill="#fff" stroke="#246593" stroke-width="1.7"/>')
    d.text(x,y+5,state,maxwidth=40)
   for x,weight in zip((180,380),path['weights']):
    d.edge(x+23,y,x+177,y)
    d.text(x+100,y-14,weight,maxwidth=130)
   d.text(380,y+51,path['result'],'small',maxwidth=680)
 elif kind=='network':
  d=Drawing(spec,spec['height']);nodes={node['id']:node for node in spec['nodes']};radius=28
  for edge in spec['edges']:
   a=nodes[edge['start']];b=nodes[edge['end']];dx=b['x']-a['x'];dy=b['y']-a['y'];length=math.hypot(dx,dy)
   d.edge(a['x']+radius*dx/length,a['y']+radius*dy/length,b['x']-radius*dx/length,b['y']-radius*dy/length)
   d.text(edge['x'],edge['y'],edge['label'],maxwidth=190)
  for node in spec['nodes']:
   d.parts.append(f'<circle cx="{node["x"]}" cy="{node["y"]}" r="{radius}" fill="#fff" stroke="#246593" stroke-width="1.7"/>')
   d.text(node['x'],node['y']+5,node['label'],maxwidth=48)
  for note in spec['notes']:d.text(note['x'],note['y'],note['text'],'small',maxwidth=700)
 elif kind=='phasor':
  d=Drawing(spec,390)
  d.edge(125,280,650,280,'#6b7885');d.edge(180,310,180,70,'#6b7885')
  d.parts.append('<path d="M430 280V110H180" fill="none" stroke="#a7bccd" stroke-dasharray="5 4"/>')
  d.edge(180,280,430,110)
  d.parts.append('<path d="M235 280A55 55 0 0 0 225.5 249.1" fill="none" stroke="#a64d26" stroke-width="1.7"/>')
  d.text(180,58,'Imaginary','small');d.text(685,285,'Real','small',maxwidth=70)
  d.text(160,303,r'\(0\)');d.text(430,310,r'\(r\cos\phi\)');d.text(115,116,r'\(r\sin\phi\)',maxwidth=100)
  d.text(250,265,r'\(\phi\)');d.text(285,174,r'\(r\)');d.text(520,102,r'\(z=re^{i\phi}\)',maxwidth=200)
  d.text(380,365,r'\(|z|^2=(r\cos\phi)^2+(r\sin\phi)^2=r^2\)','small')
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
 elif kind=='transitions':
  panels=spec['panels'];rows=max(len(col) for panel in panels for col in panel['columns']);gap=84;top=118 if any(panel.get('weights') for panel in panels) else 104
  d=Drawing(spec,top+(rows-1)*gap+(70 if any(panel.get('weights') for panel in panels) else 50));width=700/len(panels)
  def size(label):
   n=len(plain(label));return (22,22) if n<=2 else (8+4.6*n,20)
  for p,panel in enumerate(panels):
   cols=panel['columns'];x0=30+p*width;m=112 if panel.get('weights') else (36 if len(panels)>1 else 62);xs=[x0+width/2] if len(cols)==1 else [x0+m+c*(width-2*m)/(len(cols)-1) for c in range(len(cols))]
   pos={}
   for c,col in enumerate(cols):
    for i,label in enumerate(col):pos[c,label]=(xs[c],top+(rows-len(col))*gap/2+i*gap)
   for c,label in enumerate(panel.get('times',[])):d.text(xs[c],top-48,label,'small',maxwidth=width/len(cols))
   for c,label in enumerate(panel.get('steps',[])):d.text((xs[c]+xs[c+1])/2,top-48,label,maxwidth=width/len(cols))
   for c,a,b,*rest in panel['edges']:
    (x1,y1),(x2,y2)=pos[c,a],pos[c+1,b];dx,dy=x2-x1,y2-y1;length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
    (a1,b1),(a2,b2)=size(a),size(b)
    t1=1/math.hypot(ux/a1,uy/b1);t2=1/math.hypot(ux/a2,uy/b2)
    d.edge(x1+ux*(t1+2),y1+uy*(t1+2),x2-ux*(t2+3),y2-uy*(t2+3))
    if rest and rest[0]:
     if abs(uy)<.2:
      f=t1+0.5*(length-t1-t2);below=pos[c,a][1]>top+(rows-1)*gap/2+1 and any(e[0]==c and e[1]==a and e[2]!=b for e in panel['edges'])
      d.text(x1+ux*f,y1+uy*f+(19 if below else -9),rest[0],'small',maxwidth=120)
     else:
      f=(0.3 if uy>0 else 0.7)*length;lx=x1+ux*f;ly=y1+uy*f;w=7.2*len(plain(rest[0]))+8
      d.parts.append(f'<rect x="{lx-w/2:g}" y="{ly-10:g}" width="{w:g}" height="20" rx="3" fill="#fff"/>')
      d.text(lx,ly+5,rest[0],'small',maxwidth=120)
   for (c,label),(x,y) in pos.items():
    hw,hh=size(label)
    if hw==22:d.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="22" fill="#fff" stroke="#246593" stroke-width="1.7"/>')
    else:d.parts.append(f'<rect x="{x-hw:g}" y="{y-hh:g}" width="{2*hw:g}" height="{2*hh:g}" rx="{hh:g}" fill="#fff" stroke="#246593" stroke-width="1.7"/>')
    d.text(x,y+5,label,maxwidth=2*hw-6)
   for c,weights in enumerate(panel.get('weights',[])):
    for label,w in weights.items():
     x,y=pos[c,label];hw,hh=size(label)
     if c==0 and len(cols)>1:d.text(x-hw-10,y+5,w,'',anchor='end',maxwidth=120)
     elif c==len(cols)-1:d.text(x+hw+10,y+5,w,'',anchor='start',maxwidth=120)
     else:d.text(x,y-hh-10,w,'',maxwidth=120)
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
