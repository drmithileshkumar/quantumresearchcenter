"""Accessible, static SVG apparatus drawings, enhanced by the lab controller."""
from html import escape as e

def text(x,y,label,cls='',anchor='middle'):
 return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{e(label)}</text>'
def line(x1,y1,x2,y2,cls='ray'):
 return f'<path d="M{x1} {y1} L{x2} {y2}" class="{cls}"/>'
def box(x,y,w,label,sub='',cls=''):
 return f'<g class="node {cls}"><rect x="{x}" y="{y}" width="{w}" height="64" rx="10"/>{text(x+w/2,y+27,label)}{text(x+w/2,y+48,sub,"small")}</g>'
def circle(x,y,r,cls=''):
 return f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>'
def svg(kind,title):
 s='';desc='Schematic apparatus; geometry and moving indicators are explanatory, not measured trajectories.'
 if kind in ('mzi','delayed','eraser','bomb'):
  s+=line(35,160,175,160)+line(175,160,340,60)+line(340,60,505,160)+line(175,160,340,260)+line(340,260,505,160)+line(505,160,650,95)+line(505,160,650,230)
  for x,y in [(175,160),(505,160)]:s+=f'<path d="M{x-16} {y+24}l32 -48" class="splitter"/>'
  s+=circle(42,160,10,'source')+text(45,195,'Input')+text(175,200,'BS1')+text(505,200,'BS2')
  s+=box(605,45,90,'D0')+box(605,230,90,'D1')+box(285,20,110,'Phase φ')
  if kind=='bomb':s+=box(278,223,125,'Absorber','one arm','absorber')
  if kind=='eraser':s+=box(258,218,160,'Path marker','H / V → ±')
  if kind=='delayed':s+=text(500,302,'Choice: keep / remove BS2','small')
  s+='<circle class="traveller" cx="42" cy="160" r="7"/>'
 elif kind in ('rabi','ramsey','tomography','teleport','sensing'):
  s+=f'<ellipse cx="205" cy="165" rx="105" ry="37" class="sphere-ring"/>{circle(205,165,105,"sphere-ring")}'
  s+=line(205,285,205,45,'axis')+line(80,165,330,165,'axis')+line(130,225,280,105,'axis')
  s+=text(205,38,'|0⟩')+text(205,302,'|1⟩')+text(345,170,'x')+text(282,94,'y')
  s+='<path d="M205 165 L205 60" class="state-vector"/><circle class="state-tip" cx="205" cy="60" r="6"/>'
  if kind=='teleport':
   s+=box(392,30,280,'Alice: Bell measurement','two classical bits')+line(532,94,532,135,'axis')+box(392,138,280,'Bob: conditional state','Xᵇ Zᵃ |ψ⟩')+line(532,202,532,240,'axis')+box(392,244,280,'Apply the correction','Zᵃ Xᵇ → |ψ⟩')
  elif kind=='tomography':
   for y,label in [(45,'X copies'),(138,'Y copies'),(231,'Z copies')]:s+=box(420,y,235,label,'separate fresh preparations')
  else:
   s+=box(410,35,235,'Prepare |0⟩','calibrate readout')+line(527,99,527,135,'axis')+box(410,138,235,'Controlled evolution','pulse / delay')+line(527,202,527,240,'axis')+box(410,244,235,'Measure populations','repeat on fresh systems')
 elif kind in ('cat','friend'):
  s+=box(15,130,130,'Prepare +','system')+line(145,162,290,80)+line(145,162,290,245)
  s+='<rect x="252" y="18" width="270" height="292" rx="16" class="lab-boundary"/>'
  s+=text(387,47,'Isolated laboratory','small')+box(275,60,225,'|0, record 0⟩','weight 1/2')+box(275,214,225,'|1, record 1⟩','weight 1/2')
  s+='<path d="M387 124 V214" class="coherence-link"/>'+text(450,171,'γ','accent')
  s+=line(522,162,573,162)+box(575,130,130,'Outside','read / interfere')
  if kind=='cat':s+=text(387,335,'The two records are schematic macroscopic alternatives.','small')
 elif kind=='extended':
  for y,label,sign in [(30,'|h,d⟩','+'),(130,'|t,d⟩','−'),(230,'|t,u⟩','+')]:
   s+=box(25,y,145,label,'amplitude 1/√3')+line(170,y+32,340,y+32)+text(255,y+19,sign+'1/√12','accent')+line(340,y+32,460,165)
  s+=box(460,130,230,'ok, ok','sum, then square')+text(572,238,'(+1 − 1 + 1)² / 12','accent')+text(572,269,'Probability = 1/12','small')
 elif kind=='ghz':
  s+=box(270,20,180,'GHZ source','|000⟩ + |111⟩')
  for x,label in [(20,'Alice'),(265,'Bob'),(510,'Charlie')]:
   s+=line(360,84,x+95,165)+box(x,165,190,label,'choose X or Y')
  s+=text(360,283,'XXX: +1     XYY: −1     YXY: −1     YYX: −1','accent')+text(360,317,'Multiply the last three constraints.','small')
 elif kind=='bell':
  s+=box(272,132,176,'Singlet source','local marginals 1/2')+line(272,164,145,164)+line(448,164,575,164)
  s+=box(20,132,155,'Alice','a₀=0°, a₁=90°')+box(545,132,155,'Bob','b₀=θ, b₁=−θ')+text(360,55,'Independent settings · outcomes ±1','accent')+text(360,280,'Compare records to estimate four correlations.','small')
 elif kind=='hom':
  s+=line(65,60,360,170)+line(65,280,360,170)+line(360,170,635,60)+line(360,170,635,280)
  s+=f'<path d="M337 203 L383 137" class="splitter"/>'+box(15,25,170,'Photon A','mode f')+box(15,245,170,'Photon B','mode g, delay δ')+box(565,25,140,'Detector 0')+box(565,245,140,'Detector 1')
  s+='<g class="packet-a"><ellipse cx="245" cy="127" rx="40" ry="12" class="packet"/></g><g class="packet-b"><ellipse cx="245" cy="213" rx="40" ry="12" class="packet secondary"/></g>'+text(400,325,'Coincidences test mode overlap.','small')
 elif kind=='slits':
  s+=circle(55,170,12,'source')+text(55,210,'Source')+line(70,170,235,125)+line(70,170,235,215)
  s+='<path d="M240 30V115 M240 135V205 M240 225V310" class="barrier"/>'
  for sy in [125,215]:
   for y in [40,95,155,215,275,315]:s+=line(245,sy,630,y,'alternative')
  s+=line(635,30,635,315,'barrier')+text(240,337,'Slits','small')+text(630,337,'Screen','small')+text(440,22,'Amplitude alternatives','small')
 elif kind=='recoil':
  s+=box(25,135,150,'Two paths','L / R')+line(175,167,305,167)+box(305,125,180,'Movable record','pointer coordinate')+line(485,167,585,167)+box(585,135,110,'Readout')
  s+='<g class="pointer-waves"></g>'+text(390,40,'Pointer states overlap or separate','accent')+text(390,315,'Greater distinguishability → less local interference','small')
 elif kind=='tunnel':
  s+='<path d="M35 250H680" class="axis"/><rect x="300" y="60" width="120" height="190" class="potential"/><path d="M35 155H680" class="energy-line"/>'
  s+=text(360,43,'V₀')+text(55,145,'E = V₀/2','small','start')+text(360,283,'Width a','small')+text(140,315,'Incoming + reflected','small')+text(575,315,'Transmitted','small')+'<path class="tunnel-wave" d="M40 200H680"/>'
 elif kind=='polarization':
  s+=line(35,167,680,167)
  for x,angle,label in [(150,0,'H preparation'),(360,45,'θ analyzer'),(565,90,'V analyzer')]:
   s+=f'<ellipse cx="{x}" cy="167" rx="43" ry="86" class="filter"/><g transform="rotate({angle} {x} 167)"'+(' class="middle-axis"' if x==360 else '')+f'><path d="M{x} 100V234" class="filter-axis"/></g>'+text(x,285,label,'small')
 elif kind=='spin':
  s+=box(20,138,145,'Prepare +z')+line(165,170,290,170)+box(290,120,130,'Magnet','angle θ')+line(420,150,600,70)+line(420,190,600,270)+box(580,32,115,'+ axis')+box(580,240,115,'− axis')+text(355,302,'Spatial outputs encode measurement results.','small')
 elif kind=='energy':
  s+=box(20,135,155,'Light hf','variable frequency')+line(175,167,320,167)
  s+='<rect x="325" y="60" width="70" height="240" class="potential"/>'+text(360,40,'Metal surface','small')+text(360,325,'Φ = 2 eV','small')
  s+=line(400,167,550,167)+box(550,135,155,'Collector','retarding voltage')+text(535,80,'Kmax = hf − Φ','accent')
 elif kind=='photons':
  s+=box(15,137,155,'Light source','choose statistics')+line(170,169,345,169)+line(345,169,560,65)+line(345,169,560,260)
  s+='<path d="M325 194L365 144" class="splitter"/>'+box(555,32,140,'Detector A')+box(555,230,140,'Detector B')+text(360,322,'Compare detection times: delay τ','accent')
 elif kind=='capstone':
  for x,l,sub in [(15,'Generate','seed + model'),(255,'Estimate','visibility ± error'),(495,'Audit','residuals + limits')]:s+=box(x,120,200,l,sub)
  s+=line(215,152,255,152)+line(455,152,495,152)+text(360,55,'A reproducible investigation','accent')+text(360,270,'16 phases × 200 trials · synthetic data','small')
 else:
  s+=box(20,135,150,'Prepare','repeatable source')+line(170,167,290,167)+box(290,135,150,'Measure','two outcomes')+line(440,167,560,167)+box(560,135,140,'Count','A / B')+text(360,65,'One trial → one recorded outcome','accent')
 return f'<svg class="qe-apparatus" viewBox="0 0 720 350" role="img" aria-labelledby="diagram-title diagram-desc"><title id="diagram-title">{e(title)}</title><desc id="diagram-desc">{e(desc)}</desc>{s}</svg>'
