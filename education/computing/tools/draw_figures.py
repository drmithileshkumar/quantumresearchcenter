#!/usr/bin/env python3
"""Draw the book's original, accessible SVG circuits. No rendering dependencies."""
from pathlib import Path
from html import escape as e
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from svgmath import plain, svg_text
ROOT=Path(__file__).resolve().parents[1]/'assets/figures'
class Drawing:
 def __init__(self,title,desc,w=700,h=260):
  self.w,self.h=w,h;self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{e(plain(title))}</title><desc id="desc">{e(plain(desc))}</desc><style>text{{font:16px Georgia,serif;fill:#26434b}}.small{{font:13px Arial,sans-serif}}line,path{{stroke:#476b70;stroke-width:2;fill:none}}rect{{fill:#f8fbf9;stroke:#476b70;stroke-width:2}}circle{{stroke:#476b70;stroke-width:2;fill:#f8fbf9}}</style>']
 def line(self,x1,y1,x2,y2,dash=False):self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'+(' stroke-dasharray="5 4"' if dash else '')+'/>')
 def text(self,x,y,t,small=False):self.parts.append(svg_text(x,y,t,' text-anchor="middle"'+(' class="small"' if small else '')))
 def wire(self,y,label,end=None):self.text(40,y+5,label);self.line(85,y,end or self.w-40,y)
 def box(self,x,y,t,w=48,h=40):self.parts.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="4"/>');self.text(x,y+6,t)
 def dot(self,x,y):self.parts.append(f'<circle cx="{x}" cy="{y}" r="5" style="fill:#476b70"/>')
 def target(self,x,y):self.parts.append(f'<circle cx="{x}" cy="{y}" r="14"/>');self.line(x-14,y,x+14,y);self.line(x,y-14,x,y+14)
 def cx(self,x,controls,target):
  self.line(x,min(*controls,target),x,max(*controls,target))
  for y in controls:self.dot(x,y)
  self.target(x,target)
 def swap(self,x,control,a,b):
  self.line(x,control,x,b);self.dot(x,control)
  for y in [a,b]:self.line(x-9,y-9,x+9,y+9);self.line(x-9,y+9,x+9,y-9)
 def measure(self,x,y):
  self.box(x,y,'',44);self.parts.append(f'<path d="M{x-13} {y+8} A14 14 0 0 1 {x+13} {y+8} M{x} {y+7} l8 -18"/>')
 def save(self,name):
  ROOT.mkdir(parents=True,exist_ok=True);(ROOT/(name+'.svg')).write_text(''.join(self.parts)+'</svg>')

def main():
 d=Drawing('Controlled reversible gates','CNOT has one control and an XOR target. Toffoli has two controls. Fredkin has a control and two swap targets.',700,270)
 for offset,name in [(0,'CNOT'),(225,'Toffoli'),(450,'Fredkin')]:
  d.text(offset+120,32,name)
  for y,label in [(85,r'\(a\)'),(145,r'\(b\)'),(205,r'\(c\)')]:
   if name=='CNOT' and y==205:continue
   d.text(offset+30,y+5,label);d.line(offset+55,y,offset+205,y)
 d.cx(120,[85],145);d.cx(345,[85,145],205);d.swap(570,85,145,205)
 d.text(350,252,'Filled dot: control = 1. Circled plus: XOR target. Crosses: swap.',True);d.save('reversible-gates')
 d=Drawing('Compute, copy a basis label, and uncompute','A computes an answer in workspace. CNOT records the answer in a clean output. A dagger restores the workspace.',700,270)
 for y,label in [(65,r'\(x\)'),(130,'0'),(205,'0')]:d.wire(y,label)
 d.box(205,97,r'\(A\)',70,112);d.cx(350,[130],205);d.box(485,97,r'\(A^\dagger\)',70,112)
 for y,label in [(65,r'\(x\)'),(130,'0'),(205,r'\(f(x)\)')]:d.text(670,y-16,label)
 d.text(205,252,'compute',True);d.text(350,252,'copy label',True);d.text(485,252,'uncompute',True);d.save('uncomputation')
 d=Drawing('Two Hadamards','Two consecutive Hadamard gates restore the input. No intermediate measurement is performed.',620,170)
 d.wire(75,r'\(\ket0\)');d.box(195,75,r'\(H\)');d.box(390,75,r'\(H\)');d.text(580,60,r'\(\ket0\)');d.text(290,140,r'Intermediate amplitudes: \(+1/\sqrt2\) and \(+1/\sqrt2\)',True);d.save('two-hadamards')
 d=Drawing('Coherent computation paths','Each path amplitude is a product. Contributions to final zero add; contributions to final one cancel.',700,310)
 for x,y,label in [(60,145,'0'),(300,65,'0'),(300,230,'1'),(620,65,'0'),(620,230,'1')]:
  d.parts.append(f'<circle cx="{x}" cy="{y}" r="20"/>');d.text(x,y+5,label)
 for x1,y1,x2,y2 in [(80,140,280,65),(80,150,280,230),(320,65,600,65),(320,65,600,230),(320,230,600,65),(320,230,600,230)]:d.line(x1,y1,x2,y2)
 d.text(175,80,r'\(+1/\sqrt2\)');d.text(175,230,r'\(+1/\sqrt2\)');d.text(450,44,r'\(+1/\sqrt2\)');d.text(450,255,r'\(-1/\sqrt2\)');d.text(405,105,r'\(+1/\sqrt2\)');d.text(520,105,r'\(+1/\sqrt2\)')
 d.text(350,294,r'Final amplitudes: \(0\to 1/2+1/2=1\); \(1\to 1/2-1/2=0\)',True);d.save('interference-paths')
 d=Drawing('Measurement as projection','A real unit vector projects onto two orthogonal measurement axes. Squared projected lengths give probabilities.',600,300)
 d.line(100,240,480,240);d.line(100,240,100,30);d.line(100,240,360,90);d.line(360,90,360,240,True);d.line(360,90,100,90,True)
 d.text(390,83,r'\(\psi\)');d.text(475,265,r'\(\ket0\)');d.text(75,35,r'\(\ket1\)');d.text(240,265,r'\(\sqrt3/2\)');d.text(70,160,r'\(1/2\)');d.text(355,35,r'\(p(0)=3/4\), \(p(1)=1/4\)');d.save('projection')
 d=Drawing('Bell-state preparation','Hadamard on the first qubit followed by CNOT prepares the Bell state from two zeros.',620,235)
 d.wire(75,r'\(\ket0\)');d.wire(155,r'\(\ket0\)');d.box(195,75,r'\(H\)');d.cx(375,[75],155);d.text(345,215,r'Output: \((\ket{00}+\ket{11})/\sqrt2\)',True);d.save('bell')
 d=Drawing('Quantum teleportation','The Bell pair is prepared on the last two wires. Alice performs CNOT, Hadamard, and two measurements. Their classical bits control X then Z on Bob.',930,330)
 for y,label in [(65,r'\(\ket\psi\)'),(150,r'\(\ket0\)'),(245,r'\(\ket0\)')]:d.wire(y,label,end=535 if y!=245 else 890)
 d.box(155,150,r'\(H\)');d.cx(240,[150],245);d.cx(355,[65],150);d.box(445,65,r'\(H\)');d.measure(520,65);d.measure(520,150)
 d.line(542,65,785,65,True);d.line(785,65,785,223,True);d.line(542,150,665,150,True);d.line(665,150,665,223,True)
 d.box(665,245,r'\(X^n\)');d.box(785,245,r'\(Z^m\)');d.text(580,49,r'\(m\)',True);d.text(580,135,r'\(n\)',True);d.text(875,223,r'\(\ket\psi\)');d.text(200,298,'shared Bell pair',True);d.text(443,298,'Alice',True);d.text(735,298,r'Bob: \(X\) first, then \(Z\)',True);d.save('teleportation')
 d=Drawing('Deutsch algorithm','Prepare zero and one, apply Hadamards, query the joint oracle, and apply Hadamard and measurement to the first wire.',720,235)
 d.wire(70,r'\(\ket0\)');d.wire(155,r'\(\ket1\)');d.box(170,70,r'\(H\)');d.box(170,155,r'\(H\)');d.box(330,112,r'\(U_f\)',70,135);d.box(490,70,r'\(H\)');d.measure(610,70)
 d.text(385,218,'Measured bit: 0 = constant; 1 = balanced',True);d.save('deutsch')
 d=Drawing('Phase kickback','A joint function oracle acts on input x and target minus. The target remains minus while the input acquires the function-dependent sign.',700,240)
 d.wire(75,r'\(\ket{x}\)');d.wire(160,r'\(\ket-\)');d.box(300,117,r'\(U_f\)',80,135);d.text(515,50,r'\((-1)^{f(x)}\ket{x}\)');d.text(580,145,r'\(\ket-\)');d.text(350,220,'No input-dependent record remains in the target.',True);d.save('kickback')
 d=Drawing('Four-item search circuit','Prepare two plus states, mark eleven using controlled Z, then apply H X controlled Z X H on both wires. The reflection differs from diffusion only by global phase.',860,230)
 for y in [70,150]:d.wire(y,r'\(\ket0\)');d.box(140,y,r'\(H\)')
 d.line(235,70,235,150);d.dot(235,70);d.dot(235,150)
 for x,g in [(340,r'\(H\)'),(415,r'\(X\)'),(590,r'\(X\)'),(665,r'\(H\)')]:
  for y in [70,150]:d.box(x,y,g)
 d.line(505,70,505,150);d.dot(505,70);d.dot(505,150)
 d.measure(765,70);d.measure(765,150);d.text(235,207,'mark 11',True);d.text(505,207,'reflection (up to global phase)',True);d.save('grover-four')
 d=Drawing('Controlled Z from CNOT','Hadamard on the target, then CNOT, then Hadamard implements controlled Z.',660,225)
 d.wire(65,r'\(a\)');d.wire(150,r'\(b\)');d.box(180,150,r'\(H\)');d.cx(330,[65],150);d.box(480,150,r'\(H\)');d.text(350,210,r'Only \(\ket{11}\) changes sign.',True);d.save('cz-construction')
 d=Drawing('Reflection about a prepared state','Apply A dagger, reflect about the all-zero state, then apply A. Operations act from left to right.',750,180)
 d.wire(75,r'\(\ket{v}\)');d.box(185,75,r'\(A^\dagger\)',60);d.box(380,75,r'\(2\ketbra00-I\)',180);d.box(595,75,r'\(A\)',60);d.text(375,145,r'Result: \((2\ketbra\psi\psi-I)\ket{v}\), where \(\ket\psi=A\ket0\)',True);d.save('reflection')
 # A genuine NAND symbol: AND body with an inversion bubble.
 d=Drawing('XOR from four NAND gates',r'First compute \(t=\mathrm{NAND}(a,b)\). Then \(u=\mathrm{NAND}(a,t)\) and \(v=\mathrm{NAND}(b,t)\). The last NAND of \(u\) and \(v\) yields XOR.',790,330)
 def nand(x,y):
  d.parts.append(f'<path d="M{x-28} {y-28} H{x} A28 28 0 0 1 {x} {y+28} H{x-28} Z" style="fill:#f8fbf9"/><circle cx="{x+34}" cy="{y}" r="6"/>')
 d.text(30,65,r'\(a\)');d.text(30,260,r'\(b\)');d.line(50,60,330,60);d.line(50,255,330,255)
 d.line(90,60,90,145);d.line(90,145,162,145);d.dot(90,60);d.line(115,255,115,175);d.line(115,175,162,175);d.dot(115,255);nand(190,160)
 d.line(230,160,285,160);d.text(265,143,r'\(t\)');d.dot(285,160);d.line(285,160,285,110);d.line(285,110,352,110);d.line(285,160,285,210);d.line(285,210,352,210)
 d.line(330,60,330,80);d.line(330,80,352,80);d.line(330,255,330,240);d.line(330,240,352,240);nand(380,95);nand(380,225)
 d.line(420,95,530,95);d.line(530,95,530,145);d.line(530,145,572,145);d.text(470,78,r'\(u\)');d.line(420,225,530,225);d.line(530,225,530,175);d.line(530,175,572,175);d.text(470,250,r'\(v\)');nand(600,160);d.line(640,160,725,160);d.text(720,143,r'\(a\oplus b\)');d.text(395,310,'The small output circle denotes negation; filled dots denote branches.',True);d.save('nand-xor')
 print('Drew 13 SVG circuit figures.')
 from draw_logic_figures import main as draw_logic
 draw_logic()
 from draw_transition_figures import main as draw_transitions
 draw_transitions()
if __name__=='__main__':main()
