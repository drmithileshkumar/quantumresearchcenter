#!/usr/bin/env python3
"""Render the course figures in content/figures.json as accessible SVG.

Circuits use the computing course's visual conventions, extended with controlled
boxes, open controls, multi-controlled X, classical feed-forward, and slice
markers. Other kinds (table, plane, bars, network, transitions, flow, paths,
phasor) are drawn by the computing course's renderer, so both books share one
figure style.
"""
from pathlib import Path
from html import escape
import json, math, sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'computing'))
from svgmath import svg_text, plain  # noqa: E402
import illustrations as shared  # noqa: E402
SPECS=json.loads((ROOT/'content/figures.json').read_text())
INK='#26434b';WIRE='#476b70'

class Circuit:
 """One or more circuit panels stacked vertically.

 Each panel has inputs (wire labels), optional outputs, and steps: a list of
 columns, each a list of operations. Operations:
  {"label":"H","wires":[0]}                       box on one or more adjacent wires
  {"kind":"ctrl","controls":[0],"label":"U","wires":[2]}   controlled box
  {"kind":"x","controls":[0,1],"target":2}        (multi-)controlled X; no controls gives X as a circle
  {"kind":"cz","wires":[0,1]}                     controlled phase dots, optional "label"
  {"kind":"swap","wires":[0,1]}
  {"kind":"measure","wires":[0]}                  measurement; the wire becomes classical
  {"kind":"cbox","from":0,"label":"X","wires":[1]} classically controlled box fed by a measured wire
 "open" lists controls drawn hollow (control on 0). Optional panel keys: label,
 notes, bundles (wires carrying registers), slices (list of [position,label]
 where position is a column index plus a fraction), headers (column labels).
 """
 def __init__(self,spec):
  panels=spec['circuits'];self.W=W=spec.get('width',780)
  heights=[60+(30 if p.get('headers') else 0)+64*(len(p['inputs'])-1)+(76 if p.get('slices') else 44)+28*len(p.get('notes',[]))+(10 if p.get('notes') else 0)+18 for p in panels]
  self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {40+sum(heights)}" role="img" aria-labelledby="title desc"><title id="title">{escape(plain(spec["title"]))}</title><desc id="desc">{escape(plain(spec["caption"]))} Read each circuit left to right; double lines carry classical measurement records.</desc><style>text{{font:17px Georgia,serif;fill:{INK}}}.small{{font:15px Arial,sans-serif}}.head{{font:600 14px Arial,sans-serif;fill:#246593}}.wire{{stroke:{WIRE};stroke-width:2;fill:none}}.gate{{fill:#f8fbf9;stroke:{WIRE};stroke-width:2}}.big{{fill:#e9f0ed;stroke:{WIRE};stroke-width:2}}.slice{{stroke:#a64d26;stroke-width:1.4;stroke-dasharray:5 4}}</style>']
  self.text(W/2,26,spec['title'],'small')
  top=40
  for p,height in zip(panels,heights):
   self.panel(p,top);top+=height
  self.parts.append('</svg>\n')
 def panel(self,p,top):
  n=len(p['inputs']);cols=p['steps'];count=max(1,len(cols))
  head=30 if p.get('headers') else 0
  ys=[top+60+head+64*i for i in range(n)]
  W=self.W;left,right=p.get('span',(205+(40 if p.get('bundles') else 0),W-185))
  xs=[left+i*(right-left)/max(1,count-1) for i in range(count)] if count>1 else [(left+right)/2]
  self.text(W/2,top+14,p.get('label',''),'small')
  for j,label in enumerate(p.get('headers',[])):
   if label:self.text(xs[j],top+44,label,'head',width=(right-left)/count+40)
  measured={}
  for j,col in enumerate(cols):
   for g in col:
    if g.get('kind')=='measure':measured[g['wires'][0]]=xs[j]
  for i,(label,y) in enumerate(zip(p['inputs'],ys)):
   self.text(122,y+6,label,anchor='end',width=115)
   end=measured.get(i,W-130)
   self.line(135,y,end,y)
   if i in measured:
    self.line(end+23,y-3,W-130,y-3);self.line(end+23,y+3,W-130,y+3)
   if i in p.get('bundles',[]):
    self.line(151,y+8,163,y-8);self.text(165,y-10,p.get('bundle_sizes',{}).get(str(i),''),'small',anchor='start',width=40)
   self.text(W-116,y+6,(p.get('outputs') or ['']*n)[i],anchor='start',width=112)
  for position,label in p.get('slices',[]):
   j=int(position);frac=position-j
   x=xs[j]+frac*((xs[j+1]-xs[j]) if j+1<count else 60)
   self.parts.append(f'<path class="slice" d="M{x:g} {ys[0]-34}V{ys[-1]+30}"/>')
   self.text(x,ys[-1]+50,label,'small',width=150)
  width_default=min(92,(right-left)/count*.72)
  for j,col in enumerate(cols):
   x=xs[j]
   for g in col:self.gate(g,x,ys,measured,width_default)
  base=ys[-1]+(76 if p.get('slices') else 52)
  for i,note in enumerate(p.get('notes',[])):self.text(W/2,base+28*i,note,'small',width=W-40)
 def gate(self,g,x,ys,measured,wd):
  kind=g.get('kind','box')
  if kind in ('box','ctrl','cbox','measure'):
   wires=g['wires'];lo,hi=min(wires),max(wires)
   w=g.get('width',46 if kind=='measure' else min(wd,max(46,11*len(plain(g['label']))+24)) if hi==lo else wd)
   y0=ys[lo]-21;h=ys[hi]-ys[lo]+42
   if kind=='ctrl':
    ctrls=g['controls'];ally=[ys[c] for c in ctrls]
    for c in ctrls:
     yy=ys[c];self.line(x,yy,x,y0 if yy<y0 else y0+h)
    for c in ctrls:self.dot(x,ys[c],c in g.get('open',[]))
   if kind=='cbox':
    yy=ys[g['from']];edge=y0 if yy<y0 else y0+h
    self.line(x-3,yy,x-3,edge);self.line(x+3,yy,x+3,edge)
    self.parts.append(f'<circle cx="{x}" cy="{yy}" r="4" fill="{WIRE}"/>')
   cls='big' if hi>lo or g.get('composite') else 'gate'
   self.parts.append(f'<rect class="{cls}" x="{x-w/2:g}" y="{y0:g}" width="{w:g}" height="{h:g}" rx="3"/>')
   if kind=='measure':
    cy=y0+h/2+6
    self.parts.append(f'<path d="M{x-14:g} {cy:g}A14 14 0 0 1 {x+14:g} {cy:g}" fill="none" stroke="{WIRE}" stroke-width="1.8"/><path d="M{x:g} {cy:g}L{x+10:g} {cy-16:g}" stroke="{WIRE}" stroke-width="1.8"/>')
   else:self.text(x,y0+h/2+6,g['label'],width=w-6)
  elif kind=='x':
   ctrls=g.get('controls',[]);t=ys[g['target']]
   if ctrls:
    ally=[ys[c] for c in ctrls]+[t];self.line(x,min(ally),x,max(ally))
    for c in ctrls:self.dot(x,ys[c],c in g.get('open',[]))
   self.parts.append(f'<circle class="gate" cx="{x}" cy="{t}" r="14"/>');self.line(x-14,t,x+14,t);self.line(x,t-14,x,t+14)
  elif kind=='cz':
   yy=[ys[w] for w in g['wires']];self.line(x,min(yy),x,max(yy))
   for w in g['wires']:self.dot(x,ys[w],w in g.get('open',[]))
   if g.get('label'):self.text(x+12,max(yy)+28,g['label'],'small',anchor='middle',width=120)
  elif kind=='swap':
   y1,y2=ys[g['wires'][0]],ys[g['wires'][1]];self.line(x,y1,x,y2)
   for yy in (y1,y2):self.line(x-9,yy-9,x+9,yy+9);self.line(x-9,yy+9,x+9,yy-9)
  else:raise ValueError('Unknown gate kind '+kind)
 def dot(self,x,y,hollow=False):
  self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="6" fill="{"#fff" if hollow else WIRE}" stroke="{WIRE}" stroke-width="2"/>')
 def text(self,x,y,value,cls='',anchor='middle',width=700):
  self.parts.append(svg_text(x,y,value,f' text-anchor="{anchor}" class="{cls}" data-max-width="{width:g}"'))
 def line(self,x,y,x2,y2):self.parts.append(f'<path class="wire" d="M{x:g} {y:g}L{x2:g} {y2:g}"/>')
 def save(self,path):path.write_text(''.join(self.parts))

def curve(spec):
 """Plot one or more sampled functions; points are [x, y] pairs."""
 d=shared.Drawing({**spec,'kind':'table','rows':[],'headers':None,'caption':spec['caption']+' Horizontal axis: '+spec.get('xlabel','')+'; vertical axis: '+spec.get('ylabel','')+'.'},400);L,R,T,B=95,700,70,320
 if spec.get('legend')=='out':R=500
 (x0,x1),(y0,y1)=spec['xrange'],spec['yrange']
 X=lambda v:L+(v-x0)/(x1-x0)*(R-L);Y=lambda v:B-(v-y0)/(y1-y0)*(B-T)
 for v in spec.get('yticks',[]):
  v,lab=(v if isinstance(v,list) else (v,str(v)))
  d.parts.append(f'<path d="M{L} {Y(v):g}H{R}" class="grid"/>');d.text(L-12,Y(v)+5,lab,'small','end')
 for v in spec.get('xticks',[]):
  label=v if isinstance(v,str) else None
  if isinstance(v,list):v,label=v
  d.parts.append(f'<path d="M{X(v):g} {B}V{B+6}" stroke="#6b7885"/>');d.text(X(v),B+24,label if label is not None else f'{v:g}','small')
 d.parts.append(f'<path d="M{L} {B}H{R}M{L} {B}V{T}" stroke="#6b7885" fill="none"/>')
 d.text((L+R)/2,B+52,spec.get('xlabel',''),'small',maxwidth=560);d.text(L-4,T-16,spec.get('ylabel',''),'small','start',maxwidth=400)
 for i,s in enumerate(spec['series']):
  color=shared.COLORS[i%len(shared.COLORS)]
  if s.get('style')=='bars':
   w=s.get('width',12)
   for x,y in s['points']:d.parts.append(f'<rect x="{X(x)-w/2:g}" y="{min(Y(y),Y(0)):g}" width="{w}" height="{abs(Y(y)-Y(0)):g}" fill="{color}"/>')
  else:
   path='M'+'L'.join(f'{X(x):.1f} {Y(y):.1f}' for x,y in s['points'])
   d.parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.4"'+(' stroke-dasharray="6 5"' if s.get('style')=='dashed' else '')+'/>')
  if s.get('label'):
   pos=spec.get('legend','lr');lx=R-170 if pos[1]=='r' else L+20
   if pos=='out':pos,lx='ur',R+30
   ly=B-20-26*(len(spec['series'])-1-i) if pos[0]=='l' else T+8+26*i;d.parts.append(f'<path d="M{lx} {ly-5}H{lx+30}" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="6 5"' if s.get('style')=='dashed' else '')+'/>');d.text(lx+38,ly,s['label'],'small','start',maxwidth=170)
 for note in spec.get('notes',[]):d.text(note['x'],note['y'],note['text'],'small',maxwidth=note.get('width',300))
 return d

def generate(spec):
 """Fill sampled points for curves defined by a Python expression in x."""
 for s in spec.get('series',[]):
  if 'expr' in s and 'points' not in s:
   a,b=s.get('domain',spec['xrange']);n=s.get('samples',200)
   env={k:getattr(math,k) for k in dir(math) if not k.startswith('_')};env.update(range=range,sum=sum,abs=abs,min=min,max=max)
   pts=[]
   for k in range(n+1):
    x=a+(b-a)*k/n
    try:pts.append([x,eval(s['expr'],{'__builtins__':{},**env,'x':x})])
    except ZeroDivisionError:pass
   s['points']=pts
 return spec

def roots(spec):
 """The N-th roots of unity, optionally with the arrows of one power highlighted."""
 d=shared.Drawing({**spec,'kind':'table','rows':[],'headers':None},400);cx,cy,r=230,215,140;N=spec['n']
 d.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#c4d1dc"/>')
 d.parts.append(f'<path d="M{cx-r-10} {cy}H{cx+r+10}M{cx} {cy-r-10}V{cy+r+10}" stroke="#d3dee7"/>')
 for k in range(N):
  a=2*math.pi*k/N;x=cx+r*math.cos(a);y=cy-r*math.sin(a)
  d.edge(cx,cy,x,y,shared.COLORS[0])
  d.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="4" fill="{shared.COLORS[0]}"/>')
  d.text(cx+(r+30)*math.cos(a),cy-(r+26)*math.sin(a)+5,spec['labels'][k] if spec.get('labels') else (r'\(1\)' if k==0 else (r'\(\omega\)' if k==1 else r'\(\omega^{%d}\)'%k)),'small')
 for i,line in enumerate(spec.get('notes',[])):d.text(560,150+34*i,line,'',maxwidth=330)
 return d

def plane(spec):
 """Unit vectors in a real plane, with the horizontal-axis label at the axis tip."""
 d=shared.Drawing(spec,430);cx,cy,r=215,230,115
 d.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#c4d1dc"/>')
 d.edge(cx-r-25,cy,cx+r+30,cy,'#6b7885');d.edge(cx,cy+r+25,cx,cy-r-30,'#6b7885')
 d.text(cx+r+36,cy+6,spec['axes'][0],'small','start',maxwidth=120);d.text(cx,cy-r-42,spec['axes'][1],'small',maxwidth=300)
 for i,(angle,label) in enumerate(zip(spec['angles'],spec['labels'])):
  a=math.radians(angle);color=shared.COLORS[i%len(shared.COLORS)];x=cx+r*math.cos(a);y=cy-r*math.sin(a)
  d.edge(cx,cy,x,y,color,dashed=i==1)
  d.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="4" fill="{color}"/>')
  ly=120+i*70;d.parts.append(f'<path d="M430 {ly}H460" stroke="{color}" stroke-width="3"'+(' stroke-dasharray="5 4"' if i==1 else '')+'/>')
  d.text(472,ly+5,label,'small','start',maxwidth=270)
 return d

def render(spec):
 if spec['kind']=='plane':return plane(spec)
 if spec['kind']=='roots':return roots(spec)
 if spec['kind']=='circuit':return Circuit(spec)
 if spec['kind']=='curve':return curve(generate(dict(spec)))
 return shared.render(spec)

def build():
 out=ROOT/'assets/figures';out.mkdir(exist_ok=True)
 for name,spec in SPECS.items():render(spec).save(out/f'{name}.svg')
 for stale in out.glob('*.svg'):
  if stale.stem not in SPECS:stale.unlink()
 return len(SPECS)

if __name__=='__main__':print(f'Rendered {build()} figures.')
