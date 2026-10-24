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
    c=Circuit('Encode one unknown qubit',['q₁: |ψ⟩','q₂: |0⟩','q₃: |0⟩'])
    c.control(280,0,1);c.control(450,0,2)
    c.note('Joint output: α|000⟩ + β|111⟩. The two ancillas do not become independent copies.')
    c.save('repetition-encoding','Two CNOTs from q1 to q2 and q3 encode alpha|0>+beta|1> into alpha|000>+beta|111>.')
    c=Circuit('Read two parities, then correct',['data q₁','data q₂','data q₃','a₁: |0⟩','a₂: |0⟩'])
    for x,a,b in [(210,0,3),(280,1,3),(350,1,4),(420,2,4)]:c.control(x,a,b)
    c.measure(490,3,result='s₁');c.measure(490,4,result='s₂')
    c.feed(550,3,620,2);c.feed(570,4,630,2);c.block(625,0,2,'R(s)',84)
    c.note('s = s₁s₂: 00 → I; 10 → X₁; 11 → X₂; 01 → X₃. Ideal single-bit-flip recovery.')
    c.save('repetition-recovery','Ancillas measure Z1Z2 and Z2Z3; both classical results control a recovery on the data. R is I, X1, X2, or X3 according to the two-bit syndrome.')
    c=Circuit('Noise and recovery must preserve the reference',['reference R','encoded data','environment |0⟩'],['R','recovered data','discard E'])
    c.block(300,1,2,'V');c.gate(550,1,'ℛ',60)
    c.note('V is the noise isometry. The environment is inaccessible; recovery acts only on the data.')
    c.save('noise-recovery','An untouched reference wire, an encoded data wire interacting with an environment via the noise isometry V, followed by recovery R on data only. The environment is discarded.')
    c=Circuit('Measure the five-qubit check XZZXI',['q₁','q₂','q₃','q₄','q₅','a: |0⟩'])
    c.gate(190,5,'H')
    for x,row,label in [(280,0,'X'),(370,1,'Z'),(460,2,'Z'),(550,3,'X')]:c.control(x,5,row,label)
    c.gate(610,5,'H');c.measure(660,5,result='s: 0 → +1')
    c.note('The fifth data qubit is untouched. Ideal check measurement; not a certified fault-tolerant gadget.')
    c.save('five-qubit-check','Ancilla prepared in zero, Hadamard, controlled X on q1, Z on q2, Z on q3, X on q4, Hadamard and Z measurement. The ancilla is control for each gate.')
    for name,title,labels,kind in [
        ('css-x-check','Measure a Steane X-type check',['q₁','q₃','q₅','q₇','a: |0⟩'],'X'),
        ('surface-z-check','Measure one four-edge surface-code check',['edge q₁','edge q₂','edge q₃','edge q₄','a: |0⟩'],'Z')]:
        c=Circuit(title,labels)
        if kind=='X':c.gate(190,4,'H')
        for i,x in enumerate([260,350,440,530]):
            if kind=='X':c.control(x,4,i)
            else:c.control(x,i,4)
        if kind=='X':c.gate(610,4,'H')
        c.measure(660,4,result='s: 0 → +1')
        c.note('Measure only the ancilla. Gate order shown is illustrative; fault tolerance requires a schedule audit.')
        c.save(name,'Ideal '+kind+' parity check on the four named data qubits. '+('Ancilla is prepared in plus and controls each CNOT; a final Hadamard implements X readout.' if kind=='X' else 'Data control CNOTs into a zero ancilla, followed by Z measurement.'))
    c=Circuit('Logical X for the repetition code',['q₁','q₂','q₃'])
    for r in range(3):c.gate(400,r,'X')
    c.note('X₁X₂X₃ exchanges |0L⟩ = |000⟩ and |1L⟩ = |111⟩ without changing either parity.')
    c.save('logical-x','Apply X independently to all three physical qubits to implement logical X on the repetition code.')
    for kind in 'ZX':
        c=Circuit('Measure '+kind+'₁'+kind+'₂ without reading individual values',['data q₁','data q₂','a: |0⟩'])
        if kind=='X':c.gate(220,2,'H')
        for x,row in [(330,0),(450,1)]:
            if kind=='Z':c.control(x,row,2)
            else:c.control(x,2,row)
        if kind=='X':c.gate(550,2,'H')
        c.measure(640,2,result='s: 0 even; 1 odd')
        c.note('Single lines carry qubits. Double lines carry the classical measurement result s.')
        c.save('parity-'+kind.lower(),'Two CNOTs implement a '+kind+' parity measurement. '+('The data control a zero ancilla measured in Z.' if kind=='Z' else 'A plus ancilla controls each data target and is measured in X using a final Hadamard.'))
    c=Circuit('Repeat a check with fresh ancillas',['data q₁','data q₂','aₜ: |0⟩','aₜ₊₁: |0⟩'])
    for x,a,b in [(230,0,2),(300,1,2),(480,0,3),(550,1,3)]:c.control(x,a,b)
    c.measure(360,2,result='sₜ');c.measure(640,3,result='sₜ₊₁')
    c.note('Compare the two classical results: dₜ₊₁ = sₜ₊₁ XOR sₜ. Fresh ancillas avoid retaining old parity.')
    c.save('repeated-check','Measure Z1Z2 twice using separate zero ancillas and compare the resulting classical syndrome bits.')
    c=Circuit('A single ancilla Z fault can spread',['data q₁','data q₂','data q₃','data q₄','a: |0⟩'])
    for x,row in [(230,0),(310,1),(480,2),(560,3)]:c.control(x,row,4)
    c.gate(395,4,'Z',42,color='#a7373d');c.measure(650,4,result='s')
    c.note('Red Z is an injected fault after the first two gates. It propagates to q₃ and q₄ through later CNOTs.')
    c.save('hook-error','Four data controls interact in sequence with a target ancilla. A Z fault is inserted on the ancilla between the second and third CNOTs, causing Z components on data qubits three and four.')
    labels=[v for i in range(1,8) for v in [f'block A: q{i}',f'block B: q{i}']]
    c=Circuit('Transversal CNOT between two Steane blocks',labels,spacing=38)
    for i in range(7):c.control(400,2*i,2*i+1)
    c.note('Wires are interleaved for clarity. Each gate connects corresponding positions in different blocks.')
    c.save('transversal-cnot','Seven disjoint CNOT gates from qubit i in block A to qubit i in block B, implementing encoded CNOT. Wires are displayed in A1 B1 A2 B2 order through A7 B7.')
    c=Circuit('Logical Hadamard on the Steane code',[f'q{i}' for i in range(1,8)],spacing=46)
    for i in range(7):c.gate(400,i,'H')
    c.note('H on every physical qubit exchanges the paired X and Z stabilizers and logical X and Z.')
    c.save('transversal-h','Apply Hadamard independently to all seven Steane-code qubits to implement logical Hadamard.')
    c=Circuit('Inject T using a resource state',['data: |ψ⟩','ancilla: |A⟩'],['T|ψ⟩ (up to phase)',''])
    c.control(280,0,1);c.measure(420,1,result='m')
    c.feed(480,1,570,0);c.gate(570,0,'S if m=1',112)
    c.note('|A⟩ = (|0⟩ + exp(iπ/4)|1⟩)/√2. Outcome 0 needs no correction; outcome 1 needs S.')
    c.save('t-injection','Data controls a CNOT into a magic-state ancilla. Measure the ancilla in Z, and use the classical result to apply S to data only when the result is one. Both branches yield T on the data up to global phase.')
    print(f'Generated {len(list(OUT.glob("*.svg")))} circuit diagrams.')

if __name__=='__main__':main()
