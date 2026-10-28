/* Boundary checks and independent finite-dimensional calculations for teaching claims. */
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const M=require('../assets/models.js'),specs=JSON.parse(fs.readFileSync(path.join(__dirname,'../labs.json'),'utf8'));
const close=(a,b,eps=1e-10)=>assert.ok(Math.abs(a-b)<eps,`${a} != ${b}`);
for(const [kind,s]of Object.entries(specs))for(const mode of s.options.length?s.options.map(x=>x[0]):['default'])for(let j=0;j<=20;j++){
 const x=s.min+(s.max-s.min)*j/20,m=M.calc(kind,x,mode);m.values.forEach(v=>assert.ok(Number.isFinite(v),kind));if(m.curve)for(let k=0;k<=20;k++)assert.ok(Number.isFinite(m.curve(m.domain[0]+(m.domain[1]-m.domain[0])*k/20)),kind);
}
close(M.calc('spin',90).values[0],.5);close(M.calc('polarization',45).values[1],.25);close(M.calc('hom',0).values[0],0);close(M.calc('tunnel',0).values[0],1);
for(let x=0;x<=6;x+=.1){const [v,d]=M.calc('recoil',x).values;close(v*v+d*d,1);}
// Direct complex beam-splitter amplitudes, independent of the probability formula.
for(let phi=0;phi<=360;phi+=15){const re=Math.cos(phi*Math.PI/180),im=Math.sin(phi*Math.PI/180);const p=((1+re)**2+im*im)/4;close(p,M.calc('mzi',phi).values[0]);const e=M.calc('eraser',phi).values;close((e[0]+e[1])/2,e[2]);}
close(M.calc('bell',45).curve(45),2*Math.SQRT2);
// Enumerate all deterministic local CHSH assignments.
for(let bits=0;bits<16;bits++){const [a,b,c,d]=[0,1,2,3].map(i=>(bits>>i&1)?1:-1);assert.ok(Math.abs(a*c+a*d+b*c-b*d)<=2);}
// Small complex matrix helper verifies GHZ and Peres–Mermin products independently.
const z=(r,i=0)=>[r,i],add=(a,b)=>z(a[0]+b[0],a[1]+b[1]),mul=(a,b)=>z(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]);
const I=[[z(1),z(0)],[z(0),z(1)]],X=[[z(0),z(1)],[z(1),z(0)]],Y=[[z(0),z(0,-1)],[z(0,1),z(0)]],Z=[[z(1),z(0)],[z(0),z(-1)]];
const kron=(a,b)=>Array.from({length:a.length*b.length},(_,i)=>Array.from({length:a.length*b.length},(_,j)=>mul(a[Math.floor(i/b.length)][Math.floor(j/b.length)],b[i%b.length][j%b.length])));
const mm=(a,b)=>a.map(row=>b[0].map((_,j)=>row.reduce((s,v,k)=>add(s,mul(v,b[k][j])),z(0))));
const square=[[kron(X,I),kron(I,X),kron(X,X)],[kron(I,Y),kron(Y,I),kron(Y,Y)],[kron(X,Y),kron(Y,X),kron(Z,Z)]];
const contexts=[...square,...[0,1,2].map(i=>square.map(r=>r[i]))];
contexts.forEach((arr,k)=>{const prod=mm(mm(arr[0],arr[1]),arr[2]);prod.forEach((r,i)=>r.forEach((v,j)=>{close(v[0],i===j?(k===5?-1:1):0);close(v[1],0);}));});
[[X,X,X],[X,Y,Y],[Y,X,Y],[Y,Y,X]].forEach((arr,k)=>{const op=kron(kron(arr[0],arr[1]),arr[2]);const ev=(op[0][0][0]+op[0][7][0]+op[7][0][0]+op[7][7][0])/2;close(ev,k===0?1:-1);});
// Extended-friend basis change: H ⊗ H on [hd,hu,td,tu], ordered fail before ok.
const H=I.map((r,i)=>r.map((_,j)=>z((i&&j?-1:1)/Math.sqrt(2))));const U=kron(H,H),state=[1,0,1,1].map(x=>x/Math.sqrt(3));const probs=U.map(row=>row.reduce((s,c,j)=>s+c[0]*state[j],0)**2);const shown=M.calc('extended',3,'outside').values;[probs[3],probs[2],probs[1],probs[0]].forEach((v,i)=>close(v,shown[i]));
// Teleportation for complex input: direct 3-qubit gates followed by conditional correction.
const input=[z(Math.sqrt(.3)),z(0,Math.sqrt(.7))],v=Array.from({length:8},()=>z(0));
for(let q=0;q<2;q++)for(let b=0;b<2;b++)v[q*4+b*3]=input[q].map(x=>x/Math.sqrt(2));
const afterC=Array.from({length:8},()=>z(0));v.forEach((a,i)=>afterC[i^(i&4?2:0)]=a);
const afterH=Array.from({length:8},(_,i)=>add(afterC[i&3],afterC[(i&3)|4].map(x=>(i&4?-1:1)*x)).map(x=>x/Math.sqrt(2)));
for(let a=0;a<2;a++)for(let b=0;b<2;b++){
 let bob=[afterH[a*4+b*2],afterH[a*4+b*2+1]].map(v=>v.map(x=>x*2));if(b)bob.reverse();if(a)bob[1]=bob[1].map(x=>-x);bob.forEach((v,i)=>v.forEach((x,j)=>close(x,input[i][j])));
}
for(const vis of [0,.4,.8,1]){const weights=M.slitWeights(vis);close(weights.reduce((a,b)=>a+b,0),1);assert.ok(weights.every(x=>x>=0));const a=M.scan(vis),b=M.scan(vis);assert.deepEqual(a,b);assert.ok(a.rows.every(r=>r.a+r.b===200));assert.ok(Math.abs(a.estimate-vis)<.12);}
const estimates=Array.from({length:400},(_,i)=>M.scan(.6,5000+i));const mean=estimates.reduce((s,x)=>s+x.estimate,0)/estimates.length;assert.ok(Math.abs(mean-.6)<.01);const empirical=estimates.reduce((s,x)=>s+(x.estimate-mean)**2,0)/estimates.length,reported=estimates.reduce((s,x)=>s+x.se**2,0)/estimates.length;assert.ok(Math.abs(empirical/reported-1)<.2);
console.log('PASS: all 24 model ranges and modes; interference, Bell, GHZ, contextuality, teleportation, observer basis change, reproducible sampling, and estimator uncertainty.');
