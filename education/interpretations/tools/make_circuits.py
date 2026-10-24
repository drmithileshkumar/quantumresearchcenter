#!/usr/bin/env python3
"""Generate original, accessible SVG circuits used by the course manuscripts."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'circuits'

class Circuit:
    def __init__(self, title, labels, outputs=None, spacing=58):
        self.title=title; self.labels=labels; self.spacing=spacing
        self.height=100+spacing*len(labels); self.items=[]
        self.text(20,30,title,19,weight='600')
        self.text(690,30,'time →',13)
        for row,label in enumerate(labels):
            y=self.y(row); self.text(18,y+5,label,15)
            self.line(155,y,690,y)
            if outputs and outputs[row]:self.text(711,y+5,outputs[row],14)
    def y(self,r): return 76+r*self.spacing
    def text(self,x,y,label,size=16,anchor='start',weight='400',color='#253d50'):
        self.items.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{escape(label)}</text>')
    def line(self,x1,y1,x2,y2,color='#506880',width=1.7):
        self.items.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    def gate(self,x,row,label,width=42,color='#2876ae'):
        y=self.y(row)
        self.items.append(f'<rect x="{x-width/2}" y="{y-19}" width="{width}" height="38" rx="4" fill="#f2f6fc" stroke="{color}" stroke-width="1.8"/>')
        self.text(x,y+5,label,16,anchor='middle',color=color)
    def control(self,x,control,target,label=None):
        a,b=self.y(control),self.y(target)
        self.line(x,a,x,b)
        self.items.append(f'<circle cx="{x}" cy="{a}" r="5" fill="#253d50"/>')
        if label:self.gate(x,target,label)
        else:
            self.items.append(f'<circle cx="{x}" cy="{b}" r="13" fill="white" stroke="#2876ae" stroke-width="1.8"/>')
            self.line(x-13,b,x+13,b,'#2876ae');self.line(x,b-13,x,b+13,'#2876ae')
    def measure(self,x,row,basis='Z',result='s'):
        y=self.y(row)
        self.items.append(f'<rect x="{x-24}" y="{y-20}" width="48" height="40" rx="4" fill="white" stroke="#506880" stroke-width="1.7"/>')
        self.text(x,y+5,'M'+basis,15,anchor='middle')
        self.items.append(f'<rect x="{x+25}" y="{y-5}" width="{690-x-24}" height="10" fill="white"/>')
        self.line(x+24,y-3,690,y-3);self.line(x+24,y+3,690,y+3)
        self.text(711,y+5,result,14)
    def block(self,x,first,last,label,width=78):
        a,b=self.y(first)-22,self.y(last)+22
        self.items.append(f'<rect x="{x-width/2}" y="{a}" width="{width}" height="{b-a}" rx="5" fill="#f2f6fc" stroke="#2876ae" stroke-width="1.8"/>')
        self.text(x,(a+b)/2+5,label,17,anchor='middle')
    def feed(self,x1,row1,x2,row2):
        a,b=self.y(row1),self.y(row2)
        for d in (-3,3):
            self.items.append(f'<path d="M{x1} {a+d} H{x2+d} V{b+23}" stroke="#7956bd" fill="none" stroke-width="1.5"/>')
    def note(self,label):self.text(20,self.height-18,label,13)
    def save(self,name,description):
        OUT.mkdir(parents=True,exist_ok=True)
        source=(f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{self.height}" viewBox="0 0 900 {self.height}" role="img" aria-labelledby="title desc">'
                f'<title id="title">{escape(self.title)}</title><desc id="desc">{escape(description)}</desc>'
                '<rect width="100%" height="100%" fill="white"/><g font-family="DejaVu Sans, sans-serif">'+''.join(self.items)+'</g></svg>\n')
        (OUT/f'{name}.svg').write_text(source)


def main():
    c=Circuit('An ideal premeasurement',['system: |ψ⟩','pointer: |0⟩'])
    c.control(350,0,1)
    c.note('CNOT correlates the pointer: α|00⟩ + β|11⟩. No outcome is selected by this unitary.')
    c.save('premeasurement','The system controls a CNOT into a pointer initially in zero, producing a correlated two-qubit state.')
    c=Circuit('A record can be reversed coherently',['system: |+⟩','memory: |0⟩'])
    c.control(260,0,1);c.control(460,0,1);c.measure(610,0,basis='X',result='+ with certainty')
    c.text(260,178,'record',13,anchor='middle');c.text(460,178,'undo record',13,anchor='middle')
    c.note('The second CNOT erases the memory. Dephasing between gates reduces p(+) to 1/2.')
    c.save('friend-reversal','Two successive CNOTs copy and then erase the memory coherently. An X measurement on the system gives plus with certainty, unless coherence was lost.')
    c=Circuit('A record escapes into the environment',['system: |+⟩','pointer: |0⟩','environment: |0⟩'])
    c.control(250,0,1);c.control(450,1,2)
    c.note('The joint state is (|000⟩ + |111⟩)/√2. Ignoring the environment removes local coherence.')
    c.save('environment-record','A CNOT correlates system and pointer; a second from pointer to environment produces a three-qubit GHZ state.')
    print('Generated 3 measurement diagrams.')

if __name__=='__main__':main()
