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
  elif spec['kind']=='unitary-rotation':description+='Two unit circles show two states before and after a common rotation of '+str(spec['rotation'])+' degrees. Both radii remain one and the angle between the states is unchanged.'
  elif spec['kind']=='phasor':description+='A vector from the origin, its phase angle, and its projections onto the real and imaginary axes.'
  elif spec['kind']=='bars':description+='; '.join(f'{label}: {value:g}' for label,value in zip(spec['labels'],spec['values']))
  elif spec['kind']=='decision':description+='; '.join(spec['nodes'])
  elif spec['kind']=='diagram':description+=spec.get('summary') or '; '.join(plain(edge.get('label') and f"{edge['from']} → {edge['to']} ({edge['label']})" or f"{edge['from']} → {edge['to']}") for edge in spec.get('edges',[]))
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
# Tones shared by diagram nodes, edges, regions and shapes: (fill, stroke, ink).
TONES={'plain':('#fff','#a7bccd','#246593'),'accent':('#eaf1f7','#8fb0c8','#246593'),'quantum':('#f1ecf7','#b39dd0','#765391'),
 'classical':('#eef4f8','#a7bccd','#246593'),'good':('#edf5ef','#9fc4aa','#347449'),'bad':('#fbf0ea','#d9ad97','#a64d26'),'muted':('#f5f7f9','#c6d0d9','#6b7885')}
def diagram(spec):
 """A laid-out diagram: nodes at explicit centres, routed edges, tinted regions and raw shapes.

 nodes: {id,x,y,w,h,label,shape: box|diamond|pill|circle|text,tone}; edges: {from,to,label,via:[[x,y]],
 from_side/to_side: l|r|t|b, bend, dashed, arrow, tone, lx, ly}; regions: {x,y,w,h,label,tone};
 shapes: {type: rect|line, ...}; notes: {x,y,text,cls,anchor,tone}. Coordinates use the 760-wide canvas.
 """
 d=Drawing(spec,spec['height']);nodes={n['id']:n for n in spec.get('nodes',[])}
 for r in spec.get('regions',[]):
  fill,stroke,ink=TONES[r.get('tone','classical')]
  d.parts.append(f'<rect x="{r["x"]:g}" y="{r["y"]:g}" width="{r["w"]:g}" height="{r["h"]:g}" rx="12" fill="{fill}" fill-opacity=".55" stroke="{stroke}" stroke-dasharray="4 4"/>')
  if r.get('label'):d.parts.append(svg_text(r['x']+14,r['y']+22,r['label'],f' text-anchor="start" class="small" style="font-weight:600;fill:{ink};letter-spacing:.04em"'))
 for sh in spec.get('shapes',[]):
  fill,stroke,ink=TONES[sh.get('tone','plain')]
  if sh['type']=='rect':
   d.parts.append(f'<rect x="{sh["x"]:g}" y="{sh["y"]:g}" width="{sh["w"]:g}" height="{sh["h"]:g}" rx="{sh.get("rx",2):g}" fill="{sh.get("fill",ink)}" fill-opacity="{sh.get("opacity",.85):g}"'+(f' stroke="{stroke}"' if sh.get('outline') else '')+'/>')
  elif sh['type']=='line':
   pts=' '.join(f'{x:g},{y:g}' for x,y in sh['points'])
   d.parts.append(f'<polyline points="{pts}" fill="none" stroke="{sh.get("color",ink)}" stroke-width="{sh.get("width",1.6):g}"'+(' stroke-dasharray="5 4"' if sh.get('dashed') else '')+(' marker-end="url(#arrow)"' if sh.get('arrow') else '')+'/>')
 def anchor(n,side):
  return {'l':(n['x']-n['w']/2,n['y']),'r':(n['x']+n['w']/2,n['y']),'t':(n['x'],n['y']-n['h']/2),'b':(n['x'],n['y']+n['h']/2)}[side]
 def auto(n,toward):
  dx,dy=toward[0]-n['x'],toward[1]-n['y']
  return ('r' if dx>0 else 'l') if abs(dx)*n['h']>=abs(dy)*n['w'] else ('b' if dy>0 else 't')
 for e in spec.get('edges',[]):
  a,b=nodes[e['from']],nodes[e['to']];via=[tuple(p) for p in e.get('via',[])]
  start=anchor(a,e.get('from_side') or auto(a,via[0] if via else (b['x'],b['y'])))
  end=anchor(b,e.get('to_side') or auto(b,via[-1] if via else (a['x'],a['y'])))
  fill,stroke,ink=TONES[e.get('tone','plain')]
  if e.get('bend'):
   mx,my=(start[0]+end[0])/2,(start[1]+end[1])/2;dx,dy=end[0]-start[0],end[1]-start[1];L=math.hypot(dx,dy) or 1
   cx,cy=mx-dy/L*e['bend'],my+dx/L*e['bend'];path=f'M{start[0]:g} {start[1]:g}Q{cx:g} {cy:g} {end[0]:g} {end[1]:g}';mid=(mx-dy/L*e['bend']/2,my+dx/L*e['bend']/2)
  else:
   pts=[start,*via,end];path='M'+'L'.join(f'{x:g} {y:g}' for x,y in pts);k=(len(pts)-1)//2;mid=((pts[k][0]+pts[k+1][0])/2,(pts[k][1]+pts[k+1][1])/2)
  d.parts.append(f'<path d="{path}" fill="none" stroke="{ink}" stroke-width="{e.get("width",1.7):g}"'+(' stroke-dasharray="5 4"' if e.get('dashed') else '')+('' if e.get('arrow') is False else ' marker-end="url(#arrow)"')+'/>')
  if e.get('label'):d.parts.append(svg_text(e.get('lx',mid[0]),e.get('ly',mid[1]-8),e['label'],f' text-anchor="{e.get("anchor","middle")}" class="small" style="fill:{ink}" data-max-width="{e.get("maxwidth",200):g}"'))
 for n in spec.get('nodes',[]):
  fill,stroke,ink=TONES[n.get('tone','plain')];x,y,w,h=n['x'],n['y'],n.get('w',0),n.get('h',0);shape=n.get('shape','box')
  if shape=='box':d.parts.append(f'<rect x="{x-w/2:g}" y="{y-h/2:g}" width="{w:g}" height="{h:g}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
  elif shape=='pill':d.parts.append(f'<rect x="{x-w/2:g}" y="{y-h/2:g}" width="{w:g}" height="{h:g}" rx="{h/2:g}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
  elif shape=='diamond':d.parts.append(f'<path d="M{x:g} {y-h/2:g}L{x+w/2:g} {y:g}L{x:g} {y+h/2:g}L{x-w/2:g} {y:g}Z" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
  elif shape=='circle':d.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="{w/2:g}" fill="{fill}" stroke="{ink}" stroke-width="1.7"/>')
  ls=lines(n['label'],(w*.62 if shape=='diamond' else w-18) if w else 400);cls=n.get('cls','')
  for i,line in enumerate(ls):d.parts.append(svg_text(x,y+5+(i-(len(ls)-1)/2)*20,line,f' text-anchor="middle" class="{cls}" data-max-width="{(w-12 if w else 400):g}"'+(f' style="fill:{ink}"' if n.get('ink') else '')))
 for t in spec.get('notes',[]):
  fill,stroke,ink=TONES[t.get('tone','muted')]
  d.parts.append(svg_text(t['x'],t['y'],t['text'],f' text-anchor="{t.get("anchor","middle")}" class="{t.get("cls","small")}"'+(f' style="fill:{ink}"' if t.get('tone') else '')+f' data-max-width="{t.get("maxwidth",700):g}"'))
 return d
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
 elif kind=='diagram':d=diagram(spec)
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
      w=7.2*len(plain(rest[0]))+8
      if spec.get('label_plates',True):
       f=(0.3 if uy>0 else 0.7)*length;lx=x1+ux*f;ly=y1+uy*f
       d.parts.append(f'<rect x="{lx-w/2:g}" y="{ly-10:g}" width="{w:g}" height="20" rx="3" fill="#fff"/>')
       d.text(lx,ly+5,rest[0],'small',maxwidth=120)
      else:
       # No plate: set the label beside the arrow, on the side away from the panel's middle row,
       # far enough that its box (half-width w/2, half-height 10) clears the line.
       mx,my=x1+ux*length/2,y1+uy*length/2;side=-1 if my<top+(rows-1)*gap/2 else 1
       nx,ny=side*-uy,side*ux;off=w/2*abs(uy)+10*abs(ux)+4
       d.text(mx+nx*off,my+ny*off+5,rest[0],'small',maxwidth=120)
   for (c,label),(x,y) in pos.items():
    hw,hh=size(label)
    fill='#fff' if spec.get('label_plates',True) else 'none'
    if hw==22:d.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="22" fill="{fill}" stroke="#246593" stroke-width="1.7"/>')
    else:d.parts.append(f'<rect x="{x-hw:g}" y="{y-hh:g}" width="{2*hw:g}" height="{2*hh:g}" rx="{hh:g}" fill="{fill}" stroke="#246593" stroke-width="1.7"/>')
    d.text(x,y+5,label,maxwidth=2*hw-6)
   for c,weights in enumerate(panel.get('weights',[])):
    for label,w in weights.items():
     x,y=pos[c,label];hw,hh=size(label)
     if c==0 and len(cols)>1:d.text(x-hw-10,y+5,w,'',anchor='end',maxwidth=120)
     elif c==len(cols)-1:d.text(x+hw+10,y+5,w,'',anchor='start',maxwidth=120)
     else:d.text(x,y-hh-10,w,'',maxwidth=120)
 elif kind=='unitary-rotation':
  d=Drawing(spec,440);r=114;cy=230
  for panel,cx in enumerate((190,570)):
   d.text(cx,68,'Before' if panel==0 else 'After the same unitary U','heading',maxwidth=330)
   d.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#f7fafc" stroke="#a7bccd" stroke-width="1.5"/>')
   d.edge(cx-r-24,cy,cx+r+26,cy,'#a7bccd');d.edge(cx,cy+r+20,cx,cy-r-22,'#a7bccd')
   d.text(cx+r+27,cy+22,r'\(v_0\)','small',maxwidth=35)
   d.text(cx+19,cy-r-21,r'\(v_1\)','small',maxwidth=35)
   offset=panel*spec['rotation']
   for i,angle in enumerate(spec['angles']):
    a=math.radians(angle+offset);x=cx+r*math.cos(a);y=cy-r*math.sin(a)
    d.edge(cx,cy,x,y,COLORS[i],dashed=i==1)
    d.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="3.5" fill="{COLORS[i]}"/>')
    label=(r'\(\ket\psi\)' if i==0 else r'\(\ket\chi\)') if not panel else (r'\(U\ket\psi\)' if i==0 else r'\(U\ket\chi\)')
    d.text(cx+(r+24)*math.cos(a),cy-(r+24)*math.sin(a)+5,label,maxwidth=68)
   a,b=(math.radians(v+offset) for v in spec['angles']);ar=42
   d.parts.append(f'<path d="M{cx+ar*math.cos(a):g} {cy-ar*math.sin(a):g} A{ar} {ar} 0 0 0 {cx+ar*math.cos(b):g} {cy-ar*math.sin(b):g}" fill="none" stroke="#6b7885" stroke-width="1.5"/>')
   mid=(a+b)/2;d.text(cx+66*math.cos(mid),cy-66*math.sin(mid)+4,r'\(\gamma\)',maxwidth=28)
   d.text(cx,380,'Unit radius · same angle γ','small',maxwidth=330)
  d.edge(347,230,413,230);d.text(380,210,'U','heading',maxwidth=40)
  d.text(380,420,r'\(\|U\psi\|=\|\psi\|=1,\qquad \braket{U\chi}{U\psi}=\braket\chi\psi\)',maxwidth=700)
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
