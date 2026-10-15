#!/usr/bin/env python3
"""Generate Chapter 1's accessible vector diagrams using the standard library."""
from pathlib import Path
from html import escape
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svgmath import plain, svg_text
ROOT = Path(__file__).resolve().parents[1] / 'assets/figures'

class Diagram:
    def __init__(self, title, description, height):
        self.parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(plain(title))}</title><desc id="desc">{escape(description)}</desc><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10Z" fill="#246593"/></marker></defs><style>text{{font:16px Georgia,serif;fill:#30343b}}.small{{font:13px system-ui,sans-serif;fill:#626c77}}.label{{font:600 13px system-ui,sans-serif;fill:#246593}}.node{{fill:#fff;stroke:#a7bccd;stroke-width:1.5}}.accent{{fill:#eaf1f7;stroke:#246593;stroke-width:1.5}}.edge{{fill:none;stroke:#246593;stroke-width:1.7;marker-end:url(#arrow)}}.frame{{fill:none;stroke:#a7bccd;stroke-width:1.3;stroke-dasharray:5 4}}</style>''']
        self.text(360, 28, title, 'label')
    def text(self, x, y, text, cls='', anchor='middle'):
        self.parts.append(svg_text(x, y, text, f' text-anchor="{anchor}" class="{cls}"'))
    def box(self, x, y, w, h, lines, accent=False):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" class="{"accent" if accent else "node"}"/>')
        lines = lines if isinstance(lines, list) else [lines]
        for i, line in enumerate(lines): self.text(x+w/2, y+h/2+5+(i-(len(lines)-1)/2)*22, line)
    def arrow(self, points, dashed=False):
        d='M'+' L'.join(f'{x} {y}' for x,y in points)
        self.parts.append(f'<path d="{d}" class="edge"'+(' stroke-dasharray="5 4"' if dashed else '')+'/>')
    def frame(self,x,y,w,h):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" class="frame"/>')
    def save(self,name):
        ROOT.mkdir(parents=True,exist_ok=True)
        (ROOT/(name+'.svg')).write_text(''.join(self.parts)+'</svg>\n')

def main():
    d=Diagram('A proof is a network of justified steps','Statements P and P implies Q lead by modus ponens to Q. Q and Q implies R lead to R. Each edge records a dependency, not a passage of time.',320)
    d.box(45,65,170,50,r'\(P\)');d.box(265,65,190,50,r'\(P\) implies \(Q\)')
    d.arrow([(130,115),(130,150),(210,150),(210,180)]);d.arrow([(360,115),(360,150),(290,150),(290,180)])
    d.text(250,137,'modus ponens','small');d.box(165,180,170,50,r'\(Q\)',True)
    d.box(465,180,210,50,r'\(Q\) implies \(R\)');d.arrow([(335,205),(395,205),(395,270)])
    d.arrow([(570,230),(570,270),(475,270)]);d.box(315,270,160,38,r'\(R\)',True)
    d.save('logic-proof-network')

    d=Diagram('Hilbert’s program: study the proof rules','The object theory uses axioms and inference rules to produce formal proofs. Metamathematical reasoning studies these finite proofs, aiming to establish that none proves a contradiction.',340)
    d.frame(30,55,660,125);d.text(60,79,'OBJECT THEORY','label','start')
    d.box(55,100,185,55,['Axioms and','inference rules']);d.arrow([(240,127),(305,127)])
    d.box(305,100,350,55,['Finite formal proofs','and their conclusions'])
    d.box(40,235,255,65,['Finitary reasoning','about proof construction'],True)
    d.arrow([(167,235),(167,200),(480,200),(480,155)])
    d.box(385,235,295,65,['Goal: no permitted proof','derives a contradiction'],True);d.arrow([(295,267),(385,267)])
    d.text(360,326,'A proposed justification, not an assumption that consistency is guaranteed.','small')
    d.save('logic-hilbert-program')

    d=Diagram('Checking, searching, and deciding','Checking accepts or rejects a supplied record. Search enumerates and checks candidates, looping on failure and stopping on a proof. A decision procedure must also halt with no when no proof exists.',390)
    d.text(35,65,'CHECK','label','start');d.box(135,42,145,46,'Candidate');d.arrow([(280,65),(340,65)])
    d.box(340,42,130,46,'Checker');d.arrow([(470,65),(530,65)]);d.box(530,42,155,46,'Valid / invalid')
    d.text(35,150,'SEARCH','label','start');d.box(135,123,145,55,['Next','candidate']);d.arrow([(280,150),(340,150)])
    d.box(340,123,130,55,'Checker');d.arrow([(470,150),(550,150)]);d.text(510,134,r'proves \(P\)','small')
    d.box(550,123,135,55,'Stop: found',True)
    d.arrow([(405,178),(405,222),(207,222),(207,178)]);d.text(305,245,'otherwise: keep searching','small')
    d.text(35,318,'DECIDE','label','start');d.box(135,290,145,55,r'Sentence \(P\)');d.arrow([(280,318),(340,318)])
    d.box(340,290,130,55,'Decider');d.arrow([(470,318),(530,318)]);d.box(530,290,155,55,['Yes / no','always halts'],True)
    d.text(360,378,'Search alone has no stopping condition when no proof exists.','small');d.save('logic-proof-search')

    d=Diagram('Euclid’s algorithm: what stays fixed, what decreases','The pairs 48,18; 18,12; 12,6; and 6,0 have the same greatest common divisor, six. Their second entries decrease from 18 to 12 to 6 to zero, proving termination.',245)
    for i,label in enumerate(['(48, 18)','(18, 12)','(12, 6)','(6, 0)']):
        x=30+i*175;d.box(x,75,135,55,label,i==3)
        if i<3:d.arrow([(x+135,102),(x+175,102)])
    d.text(360,170,r'Invariant: \(\gcd(a,b)=6\) throughout this run','label')
    d.text(360,203,r'Decreasing nonnegative measure: \(18\to12\to6\to0\)','small')
    d.text(360,231,'Preservation gives correctness; decrease gives termination.','small');d.save('logic-euclid-run')

    d=Diagram('Configurations contain what is needed to continue','A configuration consists of stored data, control state, and position in the instructions. A transition produces the next complete configuration, and repeated transitions form a run.',260)
    d.box(30,70,265,130,[r'Configuration \(C_t\)','stored data','control state / next instruction'],True)
    d.arrow([(295,135),(425,135)]);d.text(360,113,'transition','small')
    d.box(425,70,265,130,[r'Configuration \(C_{t+1}\)','updated data','updated control position'],True)
    d.text(360,236,r'A run: \(C_0\to C_1\to C_2\to\cdots\) (until a halting condition is reached)','small');d.save('logic-configurations')

    d=Diagram('A Turing machine: tape, head, and finite control','A tape holds blanks and a finite block of ones. The head reads one cell. In state q, reading 1 leaves 1, moves right and remains in q; reading blank enters halt. A universal machine instead reads an encoded rule table and input and simulates it.',420)
    d.text(360,59,'Tape: no fixed bound on available cells','small')
    for i,symbol in enumerate(['…','□','1','1','1','□','…']):d.box(80+i*80,80,80,52,symbol,i==2)
    d.arrow([(280,185),(280,132)]);d.text(328,168,'read / write head','small','start')
    d.box(180,185,200,52,r'Finite control: \(q\)',True)
    d.box(430,185,250,75,[r'\(q, 1\to\) write 1; right; \(q\)',r'\(q, \square\to\) halt'])
    d.arrow([(380,211),(430,211)]);d.text(555,282,'Example rule table (□ = blank)','small')
    d.text(360,315,'Universal simulation','label')
    d.box(30,339,215,58,[r'Encoded program \(P\)',r'and input \(x\)']);d.arrow([(245,368),(285,368)])
    d.box(285,339,175,58,'Universal machine');d.arrow([(460,368),(500,368)])
    d.box(500,339,190,58,['Simulates the steps',r'of \(P\) on \(x\)']);d.save('logic-turing-machine')

    d=Diagram('Formal model equivalence and the Church–Turing thesis','Turing machines, lambda calculus, and recursive functions compute the same class of functions. Their formal equivalence is proved. Identifying this class with every effective mechanical procedure is the Church–Turing thesis.',320)
    d.box(20,65,195,60,'Turing machines');d.box(260,65,195,60,'Lambda calculus');d.box(500,65,200,60,'Recursive functions')
    d.arrow([(215,84),(260,84)]);d.arrow([(260,106),(215,106)])
    d.arrow([(455,84),(500,84)]);d.arrow([(500,106),(455,106)])
    d.text(360,160,'Same computable functions: equivalence of formal models','label')
    d.box(160,220,400,60,'Informal notion of an effective procedure',True)
    d.arrow([(360,220),(360,176)],True);d.text(575,202,'Church–Turing thesis','small')
    d.text(360,307,'Equivalence concerns computability, not equal running time.','small');d.save('logic-church-turing')

    d=Diagram('The halting contradiction: run D on its own description','Assume H always halts and correctly predicts halting. Program D calls H(p,p) and does the opposite. With p equal to d, the description of D, either prediction about D(d) is contradicted by its prescribed behavior.',440)
    d.text(360,61,r'Assume \(H\) always halts and correctly predicts halting.','small')
    d.frame(25,80,670,285);d.text(50,104,r'PROGRAM \(D(p)\)','label','start')
    d.box(60,137,130,60,r'Input \(p\)');d.arrow([(190,167),(245,167)])
    d.box(245,137,160,60,r'Call \(H(p,p)\)',True)
    d.arrow([(405,153),(460,153),(460,135),(515,135)]);d.text(455,116,'“halts”','small')
    d.box(515,108,145,55,'Loop forever')
    d.arrow([(405,181),(460,181),(460,267),(515,267)]);d.text(460,298,'“does not halt”','small')
    d.box(515,240,145,55,'Halt')
    d.text(360,337,r'\(D\) follows fixed instructions: it opposes the prediction.','small')
    d.text(360,392,r'Now set \(p=d\), the description of \(D\).','label')
    d.text(360,422,r'\(H(d,d)\) predicts this very run; either answer is contradicted.','small');d.save('logic-halting-contradiction')

    d=Diagram('Undecidability and incompleteness concern different objects','Undecidability excludes an always-correct total algorithm for a specified decision problem. Incompleteness says that in a consistent effective theory with enough arithmetic there is a sentence P such that neither P nor not P has a proof.',310)
    d.box(25,65,315,175,['UNDECIDABILITY','Object: a decision problem','No algorithm always halts','with the correct yes/no answer.'],True)
    d.box(380,65,315,175,['INCOMPLETENESS',r'Object: a fixed theory \(T\)',r'For some sentence \(P\),',r'\(T\) proves neither \(P\) nor \(\neg P\).'],True)
    d.text(182,271,'Example: the general halting problem','small')
    d.text(537,271,r'\(T\): consistent, effective,','small');d.text(537,291,'and sufficiently strong for arithmetic','small');d.save('logic-limitations')

    d=Diagram('Deterministic does not imply reversible','Two distinct configurations may each have one successor yet share that successor, preventing unique reversal. A one-to-one transition retains distinct resulting states so each has a unique predecessor.',290)
    d.text(175,65,'Deterministic, many-to-one','label');d.text(540,65,'One-to-one, reversible on its image','label')
    for x,y,label in [(25,100,r'\(A\)'),(25,200,r'\(B\)'),(230,150,r'\(C\)'),(410,100,r'\(A\)'),(410,200,r'\(B\)'),(600,100,r'\(A^\prime\)'),(600,200,r'\(B^\prime\)')]:d.box(x,y,90,45,label)
    d.arrow([(115,122),(175,122),(175,172),(230,172)]);d.arrow([(115,222),(175,222),(175,172),(230,172)])
    d.arrow([(500,122),(600,122)]);d.arrow([(500,222),(600,222)])
    d.text(175,278,r'\(C\) alone does not identify \(A\) or \(B\).','small');d.text(540,278,'Each result identifies its predecessor.','small');d.save('logic-reversible-transitions')

    d=Diagram('Retaining inputs preserves the distinctions AND discards','Ordinary AND maps inputs 00, 01, and 10 to zero and 11 to one. Retaining x and y and placing their AND into a target initially zero gives distinct three-bit outputs. The full reversible update is x,y,t to x,y,t XOR xy.',370)
    d.text(170,62,r'Retain only \(\mathrm{AND}(x,y)\)','label');d.text(545,62,'Retain inputs and update a target','label')
    for y,label in [(90,'00'),(145,'01'),(200,'10'),(255,'11')]:d.box(25,y,65,36,label)
    d.box(240,150,65,40,'0',True);d.box(240,255,65,36,'1',True)
    for y in [108,163,218]:d.arrow([(90,y),(165,y),(165,170),(240,170)])
    d.arrow([(90,273),(240,273)])
    for y,label,out in [(90,'000','000'),(145,'010','010'),(200,'100','100'),(255,'110','111')]:
        d.box(420,y,85,36,label);d.box(615,y,85,36,out,True);d.arrow([(505,y+18),(615,y+18)])
    d.text(545,318,r'Shown: target \(t\) initially 0','small')
    d.text(360,351,r'Full update: \((x,y,t)\to(x,y,t\oplus xy)\); applying it twice restores the input.','small');d.save('logic-information-loss')
    print('Drew 11 Chapter 1 concept diagrams.')

if __name__ == '__main__': main()
