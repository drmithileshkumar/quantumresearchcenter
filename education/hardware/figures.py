#!/usr/bin/env python3
"""Generate the hardware course's original diagrams and analytical model plots.

Run in the environment described by requirements-figures.txt. Build.py checks
that the committed SVG files exist but does not require plotting dependencies.
All numerical curves are model predictions, not experimental data.
"""
from pathlib import Path
from html import escape
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'assets/figures'
INK='#283f50';BLUE='#286e94';TEAL='#26796e';ORANGE='#ad663c';PLUM='#865879'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
 'axes.spines.right':False,'axes.edgecolor':'#a7b8c2','axes.labelcolor':INK,
 'xtick.color':INK,'ytick.color':INK,'text.color':INK,'svg.fonttype':'none',
 'svg.hashsalt':'quantum-hardware-models','figure.facecolor':'white','axes.facecolor':'white'})
SPECS=[]

def record(n,section,name,title,caption):
    SPECS.append(dict(chapter=n,section=section,name=name,title=title,caption=caption))

def plot(n,section,name,title,xlabel,ylabel,series,caption,*,logx=False,logy=False,ylim=None):
    fig,ax=plt.subplots(figsize=(7.6,3.8),layout='constrained')
    for i,(x,y,label) in enumerate(series):
        ax.plot(x,y,color=[BLUE,ORANGE,TEAL,PLUM][i%4],lw=2,
                ls=['-','--','-.',':'][i%4],label=label)
    ax.set(title=title,xlabel=xlabel,ylabel=ylabel)
    ax.grid(alpha=.23,lw=.7)
    if logx:ax.set_xscale('log')
    if logy:ax.set_yscale('log')
    if ylim:ax.set_ylim(*ylim)
    if len(series)>1:ax.legend(frameon=False,fontsize=9)
    fig.savefig(OUT/(name+'.svg'),metadata={'Date':None,'Title':title,'Description':caption})
    plt.close(fig)
    record(n,section,name,title,caption)

class Drawing:
    def __init__(self,title,description,height=340):
        self.title=title;self.description=description
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc><style>text{{font:16px system-ui,sans-serif;fill:{INK}}}.small{{font-size:13px}}.heading{{font-weight:600;fill:{BLUE}}}.wire{{stroke:{INK};stroke-width:2;fill:none}}.guide{{stroke:#b7c8d2;stroke-width:1;fill:none}}.gate{{fill:#f0f6f8;stroke:{BLUE};stroke-width:1.6}}</style>']
        self.parts.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>')
        self.text(380,27,title,'heading')
    def text(self,x,y,s,cls='',anchor='middle'):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{escape(str(s))}</text>')
    def line(self,x1,y1,x2,y2,cls='wire',color=None):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"'+(f' style="stroke:{color}"' if color else '')+'/>')
    def path(self,d,color=BLUE,width=2,dash='',arrow=False):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
    def rect(self,x,y,w,h,label=None):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" class="gate"/>')
        if label:self.text(x+w/2,y+h/2+6,label)
    def circle(self,x,y,r=5,fill=INK):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"'+(f' stroke="{INK}" stroke-width="1.6"' if fill=='white' else '')+'/>')
    def level(self,x,y,w,label):
        self.line(x,y,x+w,y);self.text(x+w+14,y+5,label,anchor='start')
    def gate(self,x,y,label):self.rect(x-23,y-20,46,40,label)
    def control(self,x,y1,y2):
        self.line(x,y1,x,y2);self.circle(x,y1);self.circle(x,y2,11,'white')
        self.line(x-11,y2,x+11,y2);self.line(x,y2-11,x,y2+11)
    def save(self,n,section,name,caption):
        (OUT/(name+'.svg')).write_text(''.join(self.parts)+'</svg>\n')
        record(n,section,name,self.title,caption)


def diagrams():
    d=Drawing('A Bell-pair circuit becomes timed physical operations','Two initialized data wires pass through H and controlled NOT, followed by measurement. Pulses are schematic, not a hardware waveform.')
    for y,label in [(100,'q₀ : |0⟩'),(190,'q₁ : |0⟩')]:d.text(105,y+5,label);d.line(170,y,675,y)
    d.gate(245,100,'H');d.control(385,100,190)
    for y in [100,190]:d.gate(585,y,'M')
    d.text(245,245,'one-qubit drive','small');d.text(400,275,'interaction + local corrections','small');d.text(585,307,'record outcomes','small')
    d.save(1,1,'bell-operations','The circuit is an ideal interface. A physical implementation must specify the encoded levels, reset, drive, interaction, and measurement. Time runs left to right.')
    d=Drawing('Energy spacing determines spectral selectivity','Harmonic levels have equal gaps, while an illustrative anharmonic ladder has a smaller second gap.')
    for x,label,ys in [(80,'Harmonic oscillator',[260,180,100]),(420,'Anharmonic device',[260,160,85])]:
        d.text(x+100,65,label,'heading')
        for i,y in enumerate(ys):d.level(x,y,150,f'|{i}⟩')
        d.line(x+35,ys[0]-5,x+35,ys[1]+5,color=BLUE)
        d.line(x+80,ys[1]-5,x+80,ys[2]+5,color=ORANGE)
    d.text(180,310,'ω₁₂ = ω₀₁','small');d.text(530,310,'α = ω₁₂ − ω₀₁ ≠ 0','small')
    d.save(2,1,'level-selectivity','The spacings, not just the existence of two selected states, determine whether a drive can address the qubit without exciting higher levels. Level positions are schematic.')
    d=Drawing('Echo reverses the sign of a static frequency error','A π pulse between equal waiting periods reverses the toggling-frame sign of a static Z offset.')
    d.line(90,100,685,100);d.gate(130,100,'π/2');d.gate(380,100,'π');d.gate(640,100,'π/2')
    d.text(245,72,'wait t/2','small');d.text(510,72,'wait t/2','small')
    d.line(100,225,670,225,'guide');d.path('M155 225V165H380V285H620V225',TEAL)
    d.text(245,153,'y(t) = +1','small');d.text(510,307,'y(t) = −1','small');d.text(380,325,'static phase: δωt/2 − δωt/2 = 0','small')
    d.save(6,2,'echo-sign','The sign refers to the frequency term in a toggling frame. Echo refocuses a constant offset; it neither reverses relaxation nor cancels arbitrary rapidly varying noise.')
    d=Drawing('A nonlinear circuit and its selected levels','A capacitor and Josephson junction form a parallel circuit. The junction supplies a nonlinear energy instead of an ordinary quadratic inductive energy.')
    d.path('M150 85H430V255H150Z',INK)
    d.line(136,145,164,145);d.line(136,163,164,163)
    d.parts.append('<rect x="139" y="146" width="22" height="16" fill="white"/>')
    d.line(132,147,168,147);d.line(132,163,168,163);d.text(100,160,'C')
    d.rect(416,145,28,32);d.line(418,147,442,175);d.line(418,175,442,147);d.text(480,166,'JJ')
    d.text(290,303,'H = 4E꜀(n − nɡ)² − Eⱼ cos φ','small')
    for i,y in enumerate([255,175,105]):d.level(555,y,95,f'|{i}⟩')
    d.save(8,1,'josephson-circuit','The capacitor stores charge energy and the Josephson junction supplies −EJ cos φ. The small ladder is schematic; the chapter derives its approximate transition spacings.')
    d=Drawing('Internal transitions can change shared motion','Two internal-state ladders have equally spaced motional levels. A carrier preserves n, and the red sideband lowers n by one.')
    for x,label in [(100,'internal |0⟩'),(440,'internal |1⟩')]:
        d.text(x+80,65,label,'heading')
        for n,y in enumerate([265,195,125]):d.level(x,y,110,f'n={n}')
    d.path('M270 195L430 195',BLUE,arrow=True);d.text(340,180,'carrier','small')
    d.path('M270 195L430 265',ORANGE,arrow=True);d.text(340,262,'red sideband','small')
    d.text(380,322,'The internal energy gap is removed in this schematic.','small')
    d.save(9,2,'ion-sidebands','The carrier connects equal motional occupation; the red sideband changes |0,n⟩ to |1,n−1⟩ in the stated drive convention. The separated ladders suppress the large internal energy offset for readability.')
    d=Drawing('Blockade shifts the double excitation','Two resonantly driven atoms have a double-Rydberg state shifted by interaction V. The shift makes the second excitation off resonant.')
    d.level(65,265,135,'|11⟩');d.level(270,190,140,'|1r⟩, |r1⟩');d.level(525,105,130,'|rr⟩')
    d.line(525,165,655,165,'guide');d.text(600,188,'unshifted rr','small')
    d.line(695,105,695,165,color=ORANGE);d.text(702,141,'V','small',anchor='start')
    d.path('M145 245L305 200',BLUE);d.path('M410 182L545 115',ORANGE)
    d.text(210,215,'drive Ω','small');d.text(420,90,'detuning B = V/ℏ','small')
    d.text(380,318,'Strong blockade: |B| much larger than Ω.','small')
    d.save(10,2,'rydberg-pair','The added energy of |rr⟩ changes the resonance condition for the second excitation. The levels and arrows are schematic; a full gate also needs pulse phases and local corrections.')
    d=Drawing('Two confined spins and a tunable barrier','Two electrostatic potential wells each hold an electron. Changing the inter-dot barrier changes tunneling and exchange.')
    d.path('M65 120Q115 120 145 230Q175 280 205 230Q250 75 295 230Q325 280 355 230Q385 120 430 120',BLUE)
    d.circle(175,235,10,TEAL);d.circle(325,235,10,ORANGE)
    d.text(175,285,'spin 1','small');d.text(325,285,'spin 2','small');d.text(250,85,'tunable barrier','small')
    d.level(510,225,125,'|0⟩');d.level(510,130,125,'|1⟩');d.text(575,180,'ΔE = |g|μʙB','small')
    d.save(11,1,'double-dot','The orbital confinement and spin splitting are different energy scales. Exchange depends on wavefunction overlap across the barrier; physical dot positions alone do not specify the gate.')
    d=Drawing('A selected transition in a spin-one defect','An axial spin-one model has m=0 and m=±1 ground-manifold levels. A magnetic field splits the two microwave transitions.')
    d.level(75,265,140,'m = 0');d.level(355,130,120,'m = −1');d.level(535,85,120,'m = +1')
    d.path('M180 250L375 145',BLUE,arrow=True);d.path('M215 250Q690 245 600 100',ORANGE,arrow=True)
    d.text(245,170,'D − γₑB','small');d.text(490,210,'D + γₑB','small')
    d.text(380,318,'Axial model only; optical excited levels are omitted.','small')
    d.save(12,1,'defect-levels','Selecting two levels does not remove the third. The displayed frequencies follow from D Sz² + γe B Sz; strain, transverse fields, and optical levels require a fuller model.')
    d=Drawing('Path phase becomes an output probability','Two paths pass through a balanced beam splitter, a relative phase plate, and another balanced splitter before detection.')
    for y in [120,215]:d.line(80,y,680,y)
    for x in [210,500]:
        d.rect(x-20,92,40,151);d.text(x,273,'balanced BS','small')
    d.rect(320,102,68,36,'φ');d.text(83,83,'one photon','small',anchor='start')
    d.gate(650,120,'D₀');d.gate(650,215,'D₁')
    d.text(380,310,'P(D₀) = cos²(φ/2),  P(D₁) = sin²(φ/2)','small')
    d.save(13,1,'photonic-interferometer','The two horizontal lines are optical modes, not two photons. A single photon occupies a coherent superposition of paths. The probability formulas use the real beam-splitter convention stated in the text.')
    d=Drawing('One loss changes parity without reading this code','The binomial code uses even-number states. One photon loss maps both logical states into distinct odd-number states with the same amplitude factor.')
    for n,x in enumerate([85,220,355,490,625]):
        d.level(x,240,65,f'{n}');d.text(x+30,275,f'|{n}⟩','small')
    d.text(200,90,'|0L⟩ = (|0⟩ + |4⟩)/√2','heading');d.text(530,90,'|1L⟩ = |2⟩','heading')
    d.path('M650 215Q600 130 525 215',BLUE,arrow=True);d.text(610,143,'√2 |3⟩','small')
    d.path('M380 215Q335 130 250 215',ORANGE,arrow=True);d.text(320,143,'√2 |1⟩','small')
    d.text(380,321,'Both codewords start even; both loss states are odd.','small')
    d.save(14,2,'binomial-loss','The drawn arrows describe the lowering operator acting on the codewords, not deterministic recovery. Both logical alternatives have mean occupation two. No-jump evolution and higher-order errors still require analysis.')
    d=Drawing('An ideal exchange is a path through configuration space','Two mode trajectories exchange horizontal positions as time advances downward. A crossing in this projected drawing is not a physical collision.')
    d.text(70,85,'start','small');d.text(70,265,'finish','small')
    for x,label in [(190,'γ₁'),(380,'γ₂'),(600,'γ₃')]:d.circle(x,85,8);d.text(x,65,label)
    d.path('M190 85C190 150 380 190 380 265',BLUE,3)
    d.path('M380 85C380 140 190 205 190 265',ORANGE,3,'7 5')
    d.path('M600 85V265',TEAL,3)
    for x in [190,380,600]:d.circle(x,265,8)
    d.text(380,318,'Ideal algebra: U₁₂ = (I + γ₁γ₂)/√2','small')
    d.save(15,2,'majorana-exchange','Time runs downward. Dashed and solid trajectories distinguish the two exchanged modes; the stationary third mode shows why a subsequent neighboring exchange can have order-dependent action. This is an ideal braid diagram, not evidence for a device.')
    d=Drawing('Feedback latency and throughput are different','Three measurement rounds on a common time axis. Each round passes through acquire, classify, and decode; a new round starts every interval Δ, before the previous result is ready. Latency is the time from the start of a round to its result; throughput is set by the start interval.',360)
    stage=[('acquire','#e1edf3'),('classify','#eae4f3'),('decode','#e3f0e6')];w=112;starts=[150,230,310]
    for x in range(150,711,80):d.line(x,94,x,262,'guide')
    for i,(start,y) in enumerate(zip(starts,[110,170,230])):
        d.text(80,y+5,f'round {i+1}','small')
        for j,(label,fill) in enumerate(stage):
            x=start+j*w;d.parts.append(f'<rect x="{x}" y="{y-17}" width="{w-4}" height="34" rx="4" fill="{fill}" stroke="#8fb0c8"/>');d.text(x+w/2-2,y+5,label,'small')
        end=start+3*w-4;d.circle(end+8,y,6,ORANGE)
    d.text(start+3*w+20,235,'result 3 ready','small','start')
    d.path(f'M150 82H{150+3*w+4}',BLUE,1.6,arrow=True);d.path(f'M{150+3*w+4} 82H150',BLUE,1.6,arrow=True)
    d.text(150+1.5*w,74,'latency: start of a round → its result','small')
    d.path('M150 296H230',ORANGE,1.6,arrow=True);d.path('M230 296H150',ORANGE,1.6,arrow=True)
    d.line(150,262,150,302,'guide');d.line(230,262,230,302,'guide')
    d.text(242,301,'Δ: a new round every interval sets the throughput','small','start')
    d.line(130,262,720,262,'wire');d.text(720,282,'time →','small','end')
    d.text(380,338,'A dependent operation must wait for the latency, even though rounds overlap.','small')
    d.save(16,2,'feedback-pipeline','Rectangles represent classical acquisition and processing intervals. Overlap shows pipelining, not instantaneous feedback. The times are schematic; a dependent gate must still wait for its result.')
    d=Drawing('A physical interaction graph constrains routing','Four sites form a line. The desired operation connects end sites that have no direct native edge.')
    for x in [140,300,460]:d.line(x,165,x+160,165)
    for i,x in enumerate([140,300,460,620]):d.circle(x,165,20,'#e1edf3');d.text(x,171,str(i))
    d.path('M140 125Q380 25 620 125',ORANGE,2,'7 5');d.text(380,60,'requested nonlocal gate','small')
    d.text(380,235,'native edges: 0—1, 1—2, 2—3','small')
    d.text(380,280,'move-and-restore: 2 outward + 2 return SWAPs','small')
    d.save(17,1,'routing-graph','The dashed curve is the requested operation, not a native interaction. For endpoints at distance three, the explicit move-and-restore strategy uses four SWAPs. Other compilers may retain a changed placement.')
    d=Drawing('Measure joint parity using one auxiliary','Two data-controlled CNOTs write x XOR y to a zero-initialized auxiliary; only the auxiliary is measured.')
    for y,label in [(100,'data x'),(180,'data y'),(260,'aux |0⟩')]:d.text(100,y+5,label);d.line(170,y,685,y)
    d.control(300,100,260);d.control(445,180,260);d.gate(605,260,'M')
    d.text(380,325,'outcome 0 → even parity; outcome 1 → odd parity','small')
    d.save(18,1,'parity-extraction','The ideal circuit preserves coherence within each parity sector. Two data wires and one auxiliary wire are shown; gate faults and repeated noisy measurements require a separate analysis.')


def plots():
    x=np.linspace(0,.12,240)
    plot(1,2,'repetition-error','Redundancy helps only for a specified noise model','Independent physical flip probability p','Decoded bit failure probability',[(x,x,'one physical bit'),(x,3*x*x-2*x**3,'three-bit majority')],'Perfect majority decoding gives 3p²−2p³ under independent bit flips. This encoding does not protect arbitrary phase errors.')
    x=np.linspace(0,12,240)
    plot(2,2,'detuning-bound','A detuning suppresses an isolated unwanted transition','|Δ| / Ω','Maximum transition probability',[(x,1/(1+x*x),'two-state bound')],'The isolated constant-drive bound is 1/[1+(Δ/Ω)²]. It is not a complete multilevel leakage prediction.')
    x=np.linspace(0,2,401)
    series=[]
    for ratio in [0,1,2]:series.append((x,np.sin(np.pi*x*np.sqrt(1+ratio*ratio))**2/(1+ratio*ratio),f'Δ/Ω = {ratio}'))
    plot(3,1,'rabi-detuning','Detuning changes both frequency and oscillation height','Time Ωt / (2π)','Excited-state probability',series,'All traces start in zero under the constant-drive two-state model. Resonance reaches full inversion; detuning imposes a ceiling that changing duration cannot remove.',ylim=(-.03,1.06))
    x=np.linspace(-5,5,401)
    plot(3,2,'pulse-spectrum','A rectangular pulse has spectral sidelobes','Detuning × duration / (2π)','Normalized weak-excitation spectral weight',[(x,np.sinc(x)**2,'rectangular envelope')],'The curve is sinc²(ΔT/2), normalized to its zero-detuning value. It describes a Fourier-weight estimate in weak excitation, not an exact resonant π-pulse probability.')
    x=np.linspace(0,1,241)
    plot(4,1,'exchange-populations','Exchange transfers one excitation coherently','Time gt / π','Population',[(x,np.cos(np.pi*x)**2,'01'),(x,np.sin(np.pi*x)**2,'10')],'Under H/ℏ = g(XX+YY)/2, the 01 and 10 populations follow cos²(gt) and sin²(gt). Equal populations at gt=π/4 accompany the relative phase −i stated in the text.',ylim=(-.03,1.06))
    x=np.linspace(0,3,241)
    plot(4,3,'mediator-overlap','A residual mediator record lowers data coherence','Coherent-state displacement difference |Δα|','Retained coherence magnitude',[(x,np.exp(-x*x/2),'overlap magnitude')],'The curve exp(−|Δα|²/2) is the magnitude of the coherent-state overlap. Correct data populations can coexist with this loss of phase-sensitive contrast.')
    x=np.linspace(-4,5,400)
    normal=lambda m:np.exp(-(x-m)**2/2)/np.sqrt(2*np.pi)
    plot(5,2,'readout-signals','Overlapping signals require a decision rule','Integrated signal (noise standard-deviation units)','Probability density',[(x,normal(0),'prepared 0: mean 0'),(x,normal(2),'prepared 1: mean 2')],'Equal-variance Gaussian models are centered two standard deviations apart. Their overlap causes assignment errors. A midpoint threshold is optimal here only for equally likely preparations and symmetric decision costs.')
    x=np.linspace(0,5,240)
    plot(5,1,'thermal-preparation','The energy-to-temperature ratio controls thermal excitation','Energy splitting / (kB T)','Equilibrium excited population',[(x,1/(1+np.exp(x)),'two-level Boltzmann model')],'The normalized two-level Boltzmann population is 1/(1+exp[ℏω/kBT]). This assumes equilibrium of the qubit, not simply a stated refrigerator temperature.')
    x=np.linspace(0,300,300)
    plot(6,1,'relaxation-coherence','Population and coherence have different decay rates','Time (μs)','Normalized population or coherence',[(x,np.exp(-x/100),'excited population, T₁ = 100 μs'),(x,np.exp(-x/200),'coherence from relaxation only'),(x,np.exp(-x/(200/3)),'coherence with Tφ = 100 μs')],'The relaxation-only coherence envelope is exp(−t/2T₁). Adding independent exponential pure dephasing at Tφ = 100 μs gives T₂ = 66.7 μs. These are model curves, not measured traces.')
    x=np.linspace(0,10,600)
    plot(7,1,'ramsey-fringes','A Ramsey trace separates fringe frequency from contrast','Wait time (μs)','Ground-state probability',[(x,.5*(1+.9*np.exp(-x/5)*np.cos(np.pi*x)),'T₂* = 5 μs, |Δ|/2π = 0.5 MHz')],'The illustrative trace has period 2 μs, visibility 0.9, and an assumed exponential envelope. A cosine-only period gives detuning magnitude, not its sign.')
    x=np.arange(0,1001)
    plot(7,2,'benchmark-decay','A sequence-length decay is a model-dependent inference','Fitted sequence length m','Survival probability',[(x,.45*.998**x+.5,'α = 0.998'),(x,.45*.996**x+.5,'α = 0.996')],'Both curves use A = 0.45 and B = 0.5. Under the effective single-qubit depolarizing model, infidelity per fitted element is (1−α)/2; it is not automatically per native pulse.')
    x=np.arange(0,5)
    # Use an energy spectrum rather than a smooth device cartoon.
    fig,ax=plt.subplots(figsize=(7.6,3.8),layout='constrained')
    ec=.25;ej=20
    E=np.sqrt(8*ec*ej)*(x+.5)-ec*(6*x*x+6*x+3)/12
    E=E-E[0]
    for i,y in enumerate(E):ax.hlines(y,.25,.8,color=BLUE,lw=2);ax.text(.84,y,f'|{i}⟩',va='center')
    ax.set(xlim=(0,1.3),ylim=(-1,E[-1]+2),ylabel='Approximate E / h relative to ground (GHz)',title='A weakly anharmonic transmon ladder',xticks=[])
    ax.grid(axis='y',alpha=.2);fig.savefig(OUT/'transmon-spectrum.svg',metadata={'Date':None});plt.close(fig)
    record(8,2,'transmon-spectrum','A weakly anharmonic transmon ladder','Quartic-approximation levels use EJ/h = 20 GHz and EC/h = 0.25 GHz. Neighboring gaps decrease by about 0.25 GHz. The plot is a low-level approximation, not an exact or measured spectrum.')
    x=np.linspace(0,2*np.pi,241)
    fig,ax=plt.subplots(figsize=(7.6,3.8),layout='constrained')
    alpha=.25*(1-np.exp(1j*x))
    ax.plot(alpha.real,alpha.imag,color=BLUE,lw=2);ax.scatter([0,.5],[0,0],color=[TEAL,ORANGE]);ax.annotate('start and closure',(0,0),xytext=(-.12,.14));ax.annotate('halfway',(.5,0),xytext=(.34,.16))
    ax.set(xlabel='Re α',ylabel='Im α',title='A single-mode force closes its displacement',aspect='equal');ax.grid(alpha=.2)
    fig.savefig(OUT/'motion-closure.svg',metadata={'Date':None});plt.close(fig)
    record(9,2,'motion-closure','A single-mode force closes its displacement','For g/δ = 0.25, α = (g/δ)(1−exp[iδt]) returns to zero at δt = 2π. This closure removes the ideal mediator displacement while an S² phase remains. Other modes and heating are omitted.')
    x=np.linspace(0,30,300)
    plot(10,3,'blockade-suppression','An isolated blockade estimate improves with |B|/Ω','Blockade shift |B| / Ω','Maximum unwanted transfer',[(x,1/(1+x*x),'isolated two-state model')],'At |B|/Ω = 20 the bound is 1/401. It excludes Rydberg decay, pulse phase error, motion, and multilevel structure; it is not a total gate infidelity.',logy=True)
    x=np.linspace(0,100,300)
    plot(11,2,'spin-exchange','A Heisenberg exchange pulse sets the SWAP time','Time (ns), J/h = 10 MHz','Probability of 10 from initial 01',[(x,np.sin(np.pi*.01*x)**2,'sin²[Jt/(2ℏ)]')],'The stated exchange-energy convention gives SWAP at 50 ns and an equal-weight entangling state at 25 ns. This differs from the angular-frequency g convention in Chapter 4.',ylim=(-.03,1.06))
    x=np.linspace(0,1,241)
    plot(12,3,'collection-rate','Two required photons make efficiency a quadratic resource','Per-photon delivery and detection probability η','Per-attempt success contribution',[(x,.5*x*x,'q η² with q = 1/2')],'This two-photon toy rate assumes independent detection and accepted-pattern factor q = 1/2. Conditional state quality also depends on mode overlap and false detections.')
    x=np.linspace(-4,4,401)
    plot(13,2,'hong-ou-mandel','Wavepacket overlap suppresses coincidences','Delay / wavepacket time scale','Coincidence probability',[(x,.5*(1-np.exp(-x*x)),'Gaussian overlap model'),(x,np.full_like(x,.5),'fully distinguishable baseline')],'For the assumed squared overlap |μ|² = exp[−(delay/τ)²], the ideal probability is (1−|μ|²)/2. This is an analytical overlap model, not a fitted experimental dip.',ylim=(-.02,.57))
    x=np.linspace(-8,8,1200)
    y=sum(np.exp(-((x-k*np.sqrt(np.pi))/.13)**2)*np.exp(-(k*np.sqrt(np.pi)/6)**2) for k in range(-4,5,2))
    plot(14,2,'finite-grid','Finite-width peaks illustrate a grid encoding','Dimensionless position q','Illustrative position density (arbitrary scale)',[(x,y,'even-lattice peaks with finite envelope')],'The schematic density uses even multiples of √π, finite peak width, and a finite envelope. It is not an ideal infinite-energy codeword and does not by itself show the required momentum protection.')
    x=np.linspace(0,10,240)
    plot(15,3,'finite-size-splitting','A conditional finite-size model suppresses splitting','Mode separation L / ξ','Residual splitting ε / ε₀',[(x,np.exp(-x),'exp(−L/ξ)')],'The exponential is an illustrative finite-size model; real systems can include oscillations and other terms. Reduced splitting alone does not establish protected operations or suppress nonequilibrium parity changes.',logy=True)
    x=np.arange(0,601)
    plot(16,3,'cold-stage-budget','Other heat loads reduce the line-count budget','Number of lines','Cold-stage heat (μW)',[(x,x*.02,'20 nW per line'),(x,4+x*.02,'same lines + 4 μW fixed load'),(x,np.full_like(x,10,dtype=float),'hypothetical 10 μW budget')],'All quantities refer to the same hypothetical temperature stage. The line-only bound is 500; a 4 μW fixed load reduces it to 300. This is accounting, not a refrigerator specification.')
    x=np.arange(1,501)
    plot(17,2,'link-wait','Retries convert per-attempt success into waiting probability','Number of independent attempts N','Probability of at least one success',[(x,1-.99**x,'s = 0.01'),(x,1-.98**x,'s = 0.02')],'The curves are 1−(1−s)^N. Mean attempts are 1/s, while the distribution has a long tail that affects memory waiting and multi-link scheduling.',ylim=(-.02,1.05))
    x=np.arange(3,16,2)
    plot(18,3,'logical-fit','A logical-error fit must name its physical regime','Odd code distance d','Illustrative logical failure per cycle',[(x,.1*.1**((x+1)/2),'p/pth = 0.1'),(x,.1*.5**((x+1)/2),'p/pth = 0.5'),(x,.1*1.2**((x+1)/2),'p/pth = 1.2')],'The illustrative fit A(p/pth)^((d+1)/2), with A = 0.1, improves with distance only below its assumed threshold. It is not a universal theorem or a prediction from one average gate fidelity.',logy=True)
    x=np.logspace(1,5,300)
    plot(19,2,'zero-failure-bound','Zero observed failures still leaves statistical uncertainty','Number of independent trials N','One-sided 95% upper failure bound',[(x,1-.05**(1/x),'exact: 1−0.05^(1/N)'),(x,3/x,'approximation: 3/N')],'The bound follows by solving (1−q)^N = 0.05 for q when no failures are seen. Independent identical trials are assumed; drift and systematic bias are not included.',logx=True,logy=True)
    x=np.linspace(0,1,241)
    plot(19,3,'accepted-rate','Compare useful output rates with acceptance included','Acceptance probability s','Accepted outputs per second',[(x,x/1e-4,'100 μs attempts'),(x,x/1e-3,'1 ms attempts')],'The illustrative rate is s/τ before calibration overhead. Faster accepted output does not establish adequate state quality; the output error target must also be met.')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    diagrams();plots()
    for spec in SPECS:
        target=OUT/(spec['name']+'.svg')
        source=target.read_text()
        if 'role="img"' not in source:
            source=source.replace('<svg ', '<svg role="img" ',1)
        target.write_text(source)
    (ROOT/'content/figures.json').write_text(json.dumps(SPECS,ensure_ascii=False,indent=2)+'\n')
    print(f'Generated {len(SPECS)} original hardware diagrams and model plots.')
if __name__=='__main__':main()
