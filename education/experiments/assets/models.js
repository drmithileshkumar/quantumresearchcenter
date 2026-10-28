/* Pure teaching models. Angles passed by the interface are in degrees. */
(function(root){
'use strict';
const rad=x=>x*Math.PI/180, clamp=x=>Math.max(0,Math.min(1,x));
const cos=x=>Math.cos(rad(x)), sin=x=>Math.sin(rad(x));
function rng(seed=2026){let s=seed>>>0;return()=>{s=(Math.imul(1664525,s)+1013904223)>>>0;return s/4294967296;};}
function slitWeights(v){const w=Array.from({length:64},(_,i)=>{const x=-3+6*(i+.5)/64;return Math.exp(-x*x/2)*(1+v*Math.cos(8*x));});const z=w.reduce((a,b)=>a+b,0);return w.map(x=>x/z);}
function scan(v,seed=2026){const random=rng(seed),N=200,M=16;const rows=Array.from({length:M},(_,j)=>{const phase=j*360/M,p=(1+v*cos(phase))/2;let a=0;for(let k=0;k<N;k++)a+=random()<p?1:0;return {phase,trials:N,a,b:N-a};});const estimate=2/M*rows.reduce((s,r)=>s+(2*r.a/N-1)*cos(r.phase),0);const variance=16/(M*M*N)*rows.reduce((s,r)=>{const p=clamp((1+estimate*cos(r.phase))/2);return s+p*(1-p)*cos(r.phase)**2;},0);return {rows,estimate,se:Math.sqrt(variance),seed};}
function calc(kind,x,mode='default'){
 let values=[],labels=[],curve=null,domain=[0,360],range=[0,1],xlabel='Angle (degrees)',ylabel='Probability',note='',vector=null;
 const p=(1+cos(x))/2;
 switch(kind){
 case 'counts': values=[x,1-x];labels=['A','B'];domain=[0,1];xlabel='Chosen probability of A';curve=t=>t;note='Independent Bernoulli trials; synthetic counts.';break;
 case 'energy':values=[Math.max(0,x-2)];labels=['Kmax (eV)'];domain=[0,5];range=[0,3];xlabel='Photon energy (eV)';ylabel='Maximum energy (eV)';curve=t=>Math.max(0,t-2);note=x<2?'Below threshold: no emission in this model.':`Stopping voltage: ${(x-2).toFixed(2)} V. Work function: 2 eV.`;break;
 case 'slits':values=slitWeights(x);labels=['Screen bins'];domain=[-3,3];xlabel='Screen coordinate (model units)';ylabel='Normalized bin probability';range=[0,.08];curve=t=>{const i=Math.max(0,Math.min(63,Math.floor((t+3)*64/6)));return values[i];};note='Gaussian envelope; visibility '+x.toFixed(2)+'. Each dot is a synthetic detection.';break;
 case 'spin':values=[cos(x/2)**2,sin(x/2)**2];labels=['+ axis','− axis'];curve=t=>cos(t/2)**2;domain=[0,180];vector=[sin(x),0,cos(x)];note='Input is +z. Analyzer direction rotates; state vector shown is the analyzer axis.';break;
 case 'polarization':values=[cos(x)**2,cos(x)**2*sin(x)**2];labels=['After middle','After final'];domain=[0,90];curve=t=>cos(t)**2*sin(t)**2;note='Probabilities are relative to the H-prepared input.';break;
 case 'photons':domain=[-4,4];range=[0,2.1];xlabel='Delay τ / τc';ylabel='g⁽²⁾(τ)';curve=t=>1+(mode==='thermal'?1:mode==='coherent'?0:-1)*Math.exp(-Math.abs(t));values=[curve(0),curve(x)];labels=['g⁽²⁾(0)','g⁽²⁾(τ)'];note='Idealized correlation shape, not generated laboratory time tags.';break;
 case 'mzi':case 'delayed':{let closed=kind==='mzi'||mode!=='open';values=closed?[p,1-p]:[.5,.5];labels=['D0','D1'];curve=t=>closed?(1+cos(t))/2:.5;note=closed?'Closed: the final splitter converts phase to populations.':'Open: phase does not change the path populations.';break;}
 case 'recoil':{const v=Math.exp(-x*x/8);values=[v,Math.sqrt(1-v*v)];labels=['Visibility V','Distinguishability D'];domain=[0,6];xlabel='Pointer separation Δ / σ';curve=t=>Math.exp(-t*t/8);note='Pure equal-width Gaussian records: V² + D² = 1.';break;}
 case 'eraser':values=[p,1-p,.5];labels=['D0 given +','D0 given −','D0 unsorted'];curve=t=>(1+cos(t))/2;note='The two subsets have equal weight. The unsorted probability stays 0.5.';break;
 case 'bomb':values=mode==='absent'?[0,1,0]:[.5,.25,.25];labels=['Absorbed','D0: inconclusive','D1: certifies'];domain=[0,1];xlabel='Object status';curve=null;note='Single-pass model; all incident trials are counted.';break;
 case 'tunnel':{const t=1/Math.cosh(x)**2;values=[t,1-t];labels=['Transmitted','Reflected'];domain=[0,4];xlabel='Barrier width κa';curve=t=>1/Math.cosh(t)**2;note='Exact rectangular-barrier transmission for E / V₀ = 1/2. Envelope is schematic.';break;}
 case 'rabi':values=[sin(x/2)**2];labels=['Excited P1'];curve=t=>sin(t/2)**2;domain=[0,720];xlabel='Pulse area (degrees)';vector=[0,-sin(x),cos(x)];note='Resonant drive, no relaxation or leakage.';break;
 case 'ramsey':{const v=mode==='echo'?1:Math.exp(-x);values=[(1+v*Math.cos(2*Math.PI*x))/2,v];labels=['P0','Contrast'];domain=[0,4];xlabel='Delay t / T₂';curve=t=>(1+(mode==='echo'?1:Math.exp(-t))*Math.cos(2*Math.PI*t))/2;vector=[v*cos(360*x),v*sin(360*x),0];note=mode==='echo'?'Ideal refocusing of static offsets; all other decoherence omitted.':'Exponential contrast loss; one phase cycle per T₂.';break;}
 case 'tomography':{const length=mode==='mixed'?.4:mode==='maxmixed'?0:1;vector=[length*sin(x),0,length*cos(x)];values=vector.map(v=>(1+v)/2);labels=['P(+X)','P(+Y)','P(+Z)'];curve=t=>(1+length*cos(t))/2;domain=[0,180];note=`Bloch length ${length.toFixed(1)}; purity ${((1+length*length)/2).toFixed(2)}. Exact probabilities.`;break;}
 case 'hom':values=[(1-Math.exp(-x*x))/2];labels=['Coincidence'];domain=[-4,4];xlabel='Relative delay (model units)';curve=t=>(1-Math.exp(-t*t))/2;note='Pure Gaussian modes: squared overlap exp(−δ²).';break;
 case 'bell':{const correlations=[-cos(x),-cos(x),-sin(x),sin(x)];values=correlations;labels=['E00','E01','E10','E11'];domain=[0,90];range=[0,3];xlabel='Bob angle θ (degrees)';ylabel='|CHSH S|';curve=t=>2*(cos(t)+sin(t));note=`|S| = ${Math.abs(correlations[0]+correlations[1]+correlations[2]-correlations[3]).toFixed(4)}. Local bound 2; singlet-spin convention.`;break;}
 case 'ghz':values=mode==='square'?[1,1,1,1,1,-1]:[1,-1,-1,-1];labels=mode==='square'?['Row 1','Row 2','Row 3','Col 1','Col 2','Col 3']:['XXX','XYY','YXY','YYX'];note=mode==='square'?'Five + products and one − product; each assigned value would appear twice.':'Multiplying the last three predictions conflicts with the first under local predetermined values.';break;
 case 'teleport':{const branch=Number(mode)||0,a=Math.floor(branch/2),b=branch%2;vector=[sin(x),0,cos(x)];const before=[(a?-1:1)*vector[0],0,(b?-1:1)*vector[2]];values=[(1+before[2])/2,(1+vector[2])/2];labels=['Before: P0','Corrected: P0'];curve=t=>(1+cos(t))/2;domain=[0,180];note=`Message ab = ${a}${b}; Bob before: (${before[0].toFixed(2)}, 0, ${before[2].toFixed(2)}). After: input restored. Branch probability 1/4.`;break;}
 case 'cat':case 'friend':values=kind==='friend'&&mode==='record'?[.5,.5]:[(1+x)/2,(1-x)/2];labels=kind==='friend'&&mode==='record'?['Record 0','Record 1']:['Joint +','Joint −'];domain=[0,1];xlabel='Surviving coherence γ';curve=t=>kind==='friend'&&mode==='record'?.5:(1+t)/2;note='Pointer records are always equally likely. Joint interference probes the off-diagonal terms.';break;
 case 'extended':values=mode==='records'?[1/3,0,1/3,1/3]:[1/12,1/12,1/12,3/4];labels=mode==='records'?['h,d','h,u','t,d','t,u']:['ok,ok','ok,fail','fail,ok','fail,fail'];note='Fully specified quantum prediction; cross-agent reasoning assumptions are separate.';break;
 case 'sensing':domain=[.1,4];range=[0,1.5];xlabel='Interrogation t / T₂';ylabel='Frequency uncertainty × T₂';curve=t=>Math.exp(t)/(10*t);values=[Math.exp(-x),curve(x)];labels=['Contrast','δω × T₂'];note='100 independent shots, exponential envelope, local quadrature estimate.';break;
 case 'capstone':values=[x];labels=['Generating V'];curve=t=>(1+x*cos(t))/2;note='Synthetic phase scan: 16 settings × 200 trials. CSV includes seed and model.';break;
 default:throw Error('Unknown model: '+kind);
 }
 return {values,labels,curve,domain,range,xlabel,ylabel,note,vector};
}
const api={calc,rng,scan,slitWeights};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.QEModels=api;
})(typeof window!=='undefined'?window:globalThis);
