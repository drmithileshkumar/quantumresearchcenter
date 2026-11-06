/* Progressive enhancement: static lessons and diagrams do not require this file. */
(() => {
'use strict';
const M=window.QEModels,esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=x=>Number(x).toFixed(4),rad=x=>x*Math.PI/180;
const mjxCache=new Map();
function typeset(rootEl){
 if(!rootEl)return;
 const nodes=rootEl.querySelectorAll('.svg-math, .qe-metric small, .qe-model-note, th, .qe-live');
 const pending=[];
 for(const n of nodes){
  const raw=n.dataset.raw||n.innerHTML;
  if(!raw.includes('\\(')&&!raw.includes('\\['))continue;
  n.dataset.raw=raw;
  if(mjxCache.has(raw)){
   if(n.innerHTML!==mjxCache.get(raw))n.innerHTML=mjxCache.get(raw);
  }else{
   pending.push(n);
  }
 }
 if(pending.length&&window.MathJax?.typesetPromise){
  window.MathJax.typesetPromise(pending).then(()=>{
   for(const n of pending){if(n.dataset.raw)mjxCache.set(n.dataset.raw,n.innerHTML);}
  }).catch(()=>{});
 }
}
function svgText(x,y,label,anchor='middle',cls='',w=260){
 if(String(label).includes('\\(')){
  const left=anchor==='start'?x:anchor==='end'?x-w:x-w/2;
  const align=anchor==='start'?'left':anchor==='end'?'right':'center';
  return `<foreignObject x="${left}" y="${y-16}" width="${w}" height="28" class="svg-fo"><div xmlns="http://www.w3.org/1999/xhtml" class="svg-math ${cls}" style="text-align:${align}">${label}</div></foreignObject>`;
 }
 return `<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}">${esc(label)}</text>`;
}
for(const lab of document.querySelectorAll('.qe-lab')){
 const kind=lab.dataset.kind,input=lab.querySelector('input'),select=lab.querySelector('select'),output=lab.querySelector('output'),chart=lab.querySelector('.qe-chart'),readout=lab.querySelector('.qe-readout'),table=lab.querySelector('.qe-table-wrap'),note=lab.querySelector('.qe-model-note'),status=lab.querySelector('.qe-live'),play=lab.querySelector('[data-action=play]'),diagram=lab.querySelector('.qe-apparatus');
 const initial=Number(input.value),initialMode=select?.value||'default',originalDiagram=diagram.innerHTML,reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let random=M.rng(),bins=[],arrivals=[],N=0,running=false,raf=0,last=0,tick=0,seed=2026,scan=null;
 function mode(){return select?.value||'default';}
 function announce(s){delete status.dataset.raw;status.innerHTML=esc(s);typeset(lab);}
 function stop(message){running=false;cancelAnimationFrame(raf);play.textContent='Play';play.setAttribute('aria-pressed','false');if(message)announce(message);}
 function resetData(){random=M.rng();N=0;arrivals=[];bins=Array(kind==='slits'?64:2).fill(0);scan=null;}
 resetData();
 function sample(count=1){const probs=M.calc(kind,Number(input.value),mode()).values;for(let j=0;j<count;j++){let u=random(),sum=0,k=probs.length-1;for(let i=0;i<probs.length;i++){sum+=probs[i];if(u<sum){k=i;break;}}bins[k]++;arrivals.push(k);N++;}}
 function poly(points,cls='curve'){return `<path class="${cls}" d="${points.map(([x,y],i)=>`${i?'L':'M'}${x.toFixed(2)} ${y.toFixed(2)}`).join(' ')}"/>`;}
 function draw(model,x){
  const width=Math.max(300,Math.min(640,Math.round(chart.parentElement.clientWidth))),left=55,right=width-20,span=right-left;chart.setAttribute('viewBox',`0 0 ${width} 310`);
  const [lo,hi]=model.domain; const [ylo,yhi]=kind==='slits'&&N?[0,Math.max(.08,...bins.map(b=>b/N))]:model.range;
  const X=v=>left+(v-lo)/(hi-lo)*span,Y=v=>250-(v-ylo)/(yhi-ylo)*205;
  let g='<title>Model prediction and current setting</title><desc>'+esc(model.note)+'</desc>';
  const bars=['counts','bomb','ghz','extended','teleport','tomography','cat','friend'].includes(kind);
  if(bars){
   const min=model.values.some(v=>v<0)?-1:0,max=1,yy=v=>250-(v-min)/(max-min)*205;
   for(const v of min<0?[-1,0,1]:[0,.5,1])g+=`<path class="grid" d="M${left} ${yy(v)}H${right}"/><text x="45" y="${yy(v)+4}" text-anchor="end">${v}</text>`;
   const bw=(span-10)/model.values.length;
   model.values.forEach((v,i)=>{const xx=left+10+i*bw;const lbl=width<450?model.labels[i].replace('\\(D_0\\): inconclusive','\\(D_0\\)').replace('\\(D_1\\): certifies','\\(D_1\\)').replace('Before: \\(P_0\\)','Before \\(P_0\\)').replace('Corrected: \\(P_0\\)','After \\(P_0\\)'):model.labels[i];g+=`<rect class="bar" x="${xx}" y="${Math.min(yy(0),yy(v))}" width="${bw*.65}" height="${Math.abs(yy(v)-yy(0))}"/>${svgText(xx+bw*.325,278,lbl,'middle','',bw)}`;
    if(kind==='counts'&&N)g+=`<circle class="point" cx="${xx+bw*.325}" cy="${yy(bins[i]/N)}" r="6"/>`;
   });
   g+='<text x="65" y="22">'+(kind==='ghz'?'Predicted product':kind==='counts'?'Probability · dots: empirical samples':'Predicted probability')+'</text>';
  }else{
   for(let i=0;i<=4;i++){let v=ylo+(yhi-ylo)*i/4;g+=`<path class="grid" d="M${left} ${Y(v)}H${right}"/><text x="43" y="${Y(v)+4}" text-anchor="end">${v.toFixed(yhi<=.1?2:1)}</text>`;}
   for(let i=0;i<=4;i++){let v=lo+(hi-lo)*i/4;g+=`<text x="${X(v)}" y="274" text-anchor="middle">${v.toFixed(hi>20?0:1)}</text>`;}
   g+=svgText(65,22,model.ylabel,'start','',260)+svgText(width/2,302,model.xlabel,'middle','',320);
   function curve(fn,cls='curve'){return poly(Array.from({length:181},(_,i)=>{let t=lo+(hi-lo)*i/180;return[X(t),Y(fn(t))];}),cls);}
   if(model.curve)g+=curve(model.curve);
   if(kind==='eraser'){g+=curve(t=>(1-Math.cos(rad(t)))/2,'curve secondary')+curve(()=>.5,'curve tertiary');}
   if(kind==='bell')g+=`<path class="bound" d="M${left} ${Y(2)}H${right}"/>${svgText(right-5,Y(2)-8,'Local bound \\(|S| \\le 2\\)','end','',180)}`;
   if(kind==='slits'&&N){bins.forEach((b,i)=>{const pos=-3+6*(i+.5)/64;g+=`<circle class="point" cx="${X(pos)}" cy="${Y(b/N)}" r="2.8"/>`;});}
   else if(kind==='capstone'){
    if(!scan)scan=M.scan(x,seed);
    g+=curve(t=>(1+scan.estimate*Math.cos(rad(t)))/2,'curve secondary');
    for(const r of scan.rows)g+=`<circle class="point" cx="${X(r.phase)}" cy="${Y(r.a/r.trials)}" r="4"/>`;
   }else if(model.curve)g+=`<circle class="point" cx="${X(x)}" cy="${Y(model.curve(x))}" r="6"/>`;
  }
  chart.innerHTML=g;
  if(kind==='capstone'){
   let residual=lab.querySelector('.qe-residual');if(!residual){residual=document.createElementNS('http://www.w3.org/2000/svg','svg');residual.setAttribute('viewBox',`0 0 ${width} 150`);residual.setAttribute('class','qe-chart qe-residual');residual.setAttribute('role','img');residual.setAttribute('aria-label','Fit residuals by phase');chart.after(residual);}
   residual.setAttribute('viewBox',`0 0 ${width} 150`);
   const points=scan.rows.map(r=>[r.phase,r.a/r.trials-(1+scan.estimate*Math.cos(rad(r.phase)))/2]);const limit=Math.max(.05,...points.map(p=>Math.abs(p[1])))*1.15;
   residual.innerHTML=`<title>Fit residuals</title>${svgText(left,20,'Observed \\(-\\) fitted','start','',200)}<path class="bound" d="M${left} 80H${right}"/>`+points.map(([phase,res])=>`<circle class="point" cx="${left+phase/360*span}" cy="${80-res/limit*45}" r="4"/>`).join('')+`<text x="55" y="40" text-anchor="end">${limit.toFixed(2)}</text><text x="55" y="84" text-anchor="end">0</text>${svgText(55,130,`\\(-${limit.toFixed(2)}\\)`,'end','',80)}${svgText(width/2,148,'Phase \\(\\phi\\) (degrees), \\(0^\\circ \\to 360^\\circ\\)','middle','',300)}`;
  }
 }
 function scene(model,x){
  if(model.vector){const [a,b,c]=model.vector;const px=205+105*a+48*b,py=165-105*c-37*b;diagram.querySelector('.state-vector')?.setAttribute('d',`M205 165L${px} ${py}`);const tip=diagram.querySelector('.state-tip');tip?.setAttribute('cx',px);tip?.setAttribute('cy',py);}
  diagram.querySelector('.middle-axis')?.setAttribute('transform',`rotate(${x} 360 167)`);
  const coherence=diagram.querySelector('.coherence-link');if(coherence)coherence.style.opacity=String(x);
  if(kind==='tunnel'){const t=model.values[0],pts=Array.from({length:200},(_,i)=>{const xx=40+i*640/199,amp=xx<300?45:xx<420?45*Math.exp(-x*(xx-300)/120):45*Math.sqrt(t);return[xx,215-amp*Math.sin(xx/12)];});diagram.querySelector('.tunnel-wave').setAttribute('d',pts.map(([a,b],i)=>`${i?'L':'M'}${a} ${b}`).join(' '));}
  if(kind==='hom')diagram.querySelector('.packet-b').setAttribute('transform',`translate(${x*25} ${-x*9})`);
  if(kind==='recoil'){const w=diagram.querySelector('.pointer-waves');w.innerHTML=[-1,1].map((sign,i)=>poly(Array.from({length:100},(_,j)=>{let q=-5+j*10/99;return[390+q*30,110-45*Math.exp(-((q-sign*x/2)**2)/4)];}),i?'curve secondary':'curve')).join('');w.querySelectorAll('path').forEach((p,i)=>{p.style.fill='none';p.style.stroke=i?'var(--lab-gold)':'var(--lab-blue)';p.style.strokeWidth='2';});}
  if(kind==='delayed'){const splitters=diagram.querySelectorAll('.splitter');splitters[1].style.opacity=mode()==='open'?'0.12':'1';}
  if(kind==='bomb'){diagram.querySelector('.absorber').style.opacity=mode()==='absent'?'0.15':'1';}
  if(kind==='ghz'&&mode()==='square'){
   diagram.innerHTML='<title id="diagram-title">Peres–Mermin square</title><desc id="diagram-desc">Rows have products +1. Columns have products +1, +1, -1.</desc>'+[['\\(X\\otimes I\\)','\\(I\\otimes X\\)','\\(X\\otimes X\\)'],['\\(I\\otimes Y\\)','\\(Y\\otimes I\\)','\\(Y\\otimes Y\\)'],['\\(X\\otimes Y\\)','\\(Y\\otimes X\\)','\\(Z\\otimes Z\\)']].map((row,i)=>row.map((t,j)=>`<g class="node"><rect x="${75+j*155}" y="${35+i*90}" width="135" height="65" rx="8"/>${svgText(142+j*155,74+i*90,t,'middle','',130)}</g>`).join('')+svgText(600,74+i*90,'\\(+I\\)','middle','accent',80)).join('')+svgText(142,332,'\\(+I\\)','middle','accent',80)+svgText(297,332,'\\(+I\\)','middle','accent',80)+svgText(452,332,'\\(-I\\)','middle','accent',80);
  }else if(kind==='ghz'&& !diagram.querySelector('.ray'))diagram.innerHTML=originalDiagram;
  if(kind==='slits'){
   let dots=diagram.querySelector('.detections');if(!dots){dots=document.createElementNS('http://www.w3.org/2000/svg','g');dots.setAttribute('class','detections');diagram.append(dots);}
   dots.innerHTML=arrivals.slice(-600).map((bin,i)=>`<circle cx="${645+(i*17%50)}" cy="${30+(bin+.5)/64*285}" r="2" fill="var(--lab-gold)" opacity=".65"/>`).join('');
  }
  if(kind==='extended'&&mode()==='records'){
   diagram.innerHTML='<title id="diagram-title">Friend record probabilities</title><desc id="diagram-desc">Three possible record pairs, each with probability one third; 0,1 is absent.</desc>'+[['\\(|0,0\\rangle\\)','\\(1/3\\)'],['\\(|0,1\\rangle\\)','\\(0\\)'],['\\(|1,0\\rangle\\)','\\(1/3\\)'],['\\(|1,1\\rangle\\)','\\(1/3\\)']].map(([label,p],i)=>`<g class="node"><rect x="${30+i*175}" y="110" width="140" height="100" rx="10"/>${svgText(100+i*175,150,label,'middle','',130)}${svgText(100+i*175,184,p,'middle','accent',130)}</g>`).join('');
  }
  if(kind==='extended'&&mode()!=='records'){
   const n=Math.round(x),nodes=diagram.querySelectorAll('.node');nodes.forEach((el,i)=>el.style.opacity=i<3&&i>=n?'.25':'1');
  }
  if(['bomb','ghz'].includes(kind)){const nodes=[...diagram.querySelectorAll('.node')];nodes.forEach((el,i)=>el.classList.toggle('active-stage',i===Math.round(x)%nodes.length));}
  if(kind==='counts'){
   const ka=bins[0]||0,kb=bins[1]||0,lastOut=arrivals.length?arrivals[arrivals.length-1]:null;
   const elKa=diagram.querySelector('.counts-ka'),elKb=diagram.querySelector('.counts-kb'),elN=diagram.querySelector('.counts-n'),elPhat=diagram.querySelector('.counts-phat');
   if(elKa)elKa.textContent=String(ka);
   if(elKb)elKb.textContent=String(kb);
   if(elN)elN.textContent=String(N);
   if(elPhat)elPhat.textContent=N?(ka/N).toFixed(3):'—';
   const fa=diagram.querySelector('.det-flash-a'),fb=diagram.querySelector('.det-flash-b'),tr=diagram.querySelector('.counts-traveller');
   if(fa)fa.setAttribute('opacity',lastOut===0?'0.45':'0');
   if(fb)fb.setAttribute('opacity',lastOut===1?'0.45':'0');
   if(tr){
    if(lastOut===null){tr.setAttribute('opacity','0');}
    else{tr.setAttribute('opacity','1');tr.setAttribute('cx',495);tr.setAttribute('cy',lastOut===0?77:221);tr.setAttribute('fill',lastOut===0?'var(--lab-blue)':'var(--lab-gold)');}
   }
   const tape=diagram.querySelector('.counts-tape-cells');
   if(tape){
    const recent=arrivals.slice(-18);
    tape.innerHTML=recent.map((out,idx)=>{
     const xx=idx*30,isA=out===0,col=isA?'var(--lab-blue)':'var(--lab-gold)';
     return `<g transform="translate(${xx},0)"><rect x="0" y="0" width="26" height="30" rx="5" fill="${col}" opacity="0.88"/><text x="13" y="20" text-anchor="middle" style="font:600 13px var(--sans);fill:#fff">${isA?'A':'B'}</text></g>`;
    }).join('');
   }
  }
  const traveller=diagram.querySelector('.traveller');if(traveller){const t=(tick%40)/40;let px,py;if(t<.2){px=42+t/.2*133;py=160;}else if(t<.6){const u=(t-.2)/.4;px=175+330*u;py=160-100*Math.sin(Math.PI*u);}else{const u=(t-.6)/.4;px=505+140*u;py=160-65*u;}traveller.setAttribute('cx',px);traveller.setAttribute('cy',py);}
 }
 function render(){
  const x=Number(input.value),model=M.calc(kind,x,mode());output.value=String(x);output.textContent=String(x);draw(model,x);scene(model,x);
  let vals=model.values,labels=model.labels;
  if(kind==='slits'){vals=[N,x];labels=['Synthetic events \\(N\\)','Visibility \\(V\\)'];}
  if(kind==='counts'){vals=[...vals,N,...bins];labels=[...labels,'Trials \\(N\\)','\\(k_A\\) counts','\\(k_B\\) counts'];}
  if(kind==='capstone'){vals=[x,scan.estimate,scan.se,scan.seed];labels=['Generating \\(V\\)','Estimated \\(\\hat{V}_c\\)','Standard error \\(\\mathrm{SE}\\)','Seed'];}
  readout.innerHTML=vals.map((v,i)=>`<div class="qe-metric"><small>${esc(labels[i])}</small><strong>${Number.isInteger(v)&&Math.abs(v)>1?v:fmt(v)}</strong></div>`).join('');
  delete note.dataset.raw;
  note.innerHTML=esc(model.note+(kind==='eraser'?' Blue: given \\(|+\\rangle\\); dashed gold: given \\(|-\\rangle\\); dotted violet: unsorted.':'')+(kind==='slits'?` \\(N = ${N}\\) synthetic events; dots show empirical bin fractions.`:'')+(kind==='capstone'?' Blue: generating curve; dashed gold: fitted curve; dots: \\(k_m / N_m\\).':''));
  let rows=vals.map((v,i)=>[labels[i],fmt(v)]),heads=['Quantity','Value'];
  if(kind==='slits'){heads=['Screen bin','Predicted probability','Synthetic count'];rows=model.values.map((v,i)=>[i+1,fmt(v),bins[i]]);}
  if(kind==='capstone'){heads=['Phase (\\(^\\circ\\))','Trials \\(N_m\\)','\\(D_0\\)','\\(D_1\\)','Residual'];rows=scan.rows.map(r=>[r.phase,r.trials,r.a,r.b,fmt(r.a/r.trials-(1+scan.estimate*Math.cos(rad(r.phase)))/2)]);}
  table.innerHTML='<table><thead><tr>'+heads.map(h=>'<th scope="col">'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map((v,i)=>i?'<td>'+esc(v)+'</td>':'<th scope="row">'+esc(v)+'</th>').join('')+'</tr>').join('')+'</tbody></table>';
  typeset(lab);
  lab.dataset.ready='true';lab.dataset.events=String(N);
 }
 function step(){
  tick++;
  if(kind==='counts'||kind==='slits')sample(running?4:1);
  else if(kind==='capstone'){seed++;scan=null;}
  else{const min=Number(input.min),max=Number(input.max),s=Number(input.step),delta=['bomb','ghz','extended'].includes(kind)?1:Math.max(s,(max-min)/100);let v=Number(input.value)+delta;input.value=String(v>max+1e-8?min:v);}
  render();
 }
 function frame(time){if(!running)return;if(!last||time-last>85){step();last=time;}raf=requestAnimationFrame(frame);}
 lab.querySelector('[data-action=play]').addEventListener('click',()=>{if(running){stop('Paused.');return;}running=true;last=0;play.textContent='Pause';play.setAttribute('aria-pressed','true');announce('Running. Use Pause to inspect the current values.');raf=requestAnimationFrame(frame);});
 lab.querySelector('[data-action=step]').addEventListener('click',()=>{stop();step();announce(kind==='counts'||kind==='slits'?`Recorded \\(N = ${N}\\) synthetic events.`:'Advanced one step. '+output.textContent);});
 lab.querySelector('[data-action=reset]').addEventListener('click',()=>{stop();input.value=initial;if(select)select.value=initialMode;seed=2026;tick=0;resetData();render();announce('Reset to the initial settings and random seed.');});
 input.addEventListener('input',()=>{stop();resetData();render();announce('Setting updated. '+input.value);});
 select?.addEventListener('change',()=>{stop();diagram.innerHTML=originalDiagram;resetData();render();announce('Configuration updated. '+select.selectedOptions[0].textContent);});
 lab.querySelector('[data-action=export]')?.addEventListener('click',()=>{
  const csv='# Synthetic educational data; not laboratory measurements\n# model: P0=(1+V*cos(phase))/2; independent binomial trials\n# visibility='+input.value+'; seed='+seed+'\nphase_degrees,trials,d0,d1\n'+scan.rows.map(r=>[r.phase,r.trials,r.a,r.b].join(',')).join('\n')+'\n';
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='quantum-experiments-synthetic-scan.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);announce('Downloaded synthetic counts with model and seed metadata.');
 });
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
 new IntersectionObserver(entries=>{if(!entries[0].isIntersecting&&running)stop('Paused while the experiment is off screen.');},{threshold:0}).observe(lab);
 reduced.addEventListener('change',()=>{if(reduced.matches)stop('Reduced motion enabled. Use Step for individual updates.');});
 new ResizeObserver(()=>render()).observe(lab.querySelector('.qe-chart-wrap'));
 lab.querySelector('.qe-controls').hidden=false;lab.querySelector('.qe-results').hidden=false;render();announce(reduced.matches?'Reduced motion is enabled. Use Step for individual updates.':'Ready. Change a setting, step through the model, or press Play.');
}
for(const sceneEl of document.querySelectorAll('.qe-scene[data-scene="section-1-1"]')){
 const svgEl=sceneEl.querySelector('svg'),controlsEl=sceneEl.querySelector('.qe-scene-controls'),liveEl=sceneEl.querySelector('.qe-scene-live');
 const pIn=sceneEl.querySelector('[data-scene-p]'),etaAIn=sceneEl.querySelector('[data-scene-eta-a]'),etaBIn=sceneEl.querySelector('[data-scene-eta-b]');
 const pOut=sceneEl.querySelector('#scene-1-1-p-out'),etaAOut=sceneEl.querySelector('#scene-1-1-eta-a-out'),etaBOut=sceneEl.querySelector('#scene-1-1-eta-b-out');
 const playBtn=sceneEl.querySelector('[data-scene-action="play"]'),stepBtn=sceneEl.querySelector('[data-scene-action="step"]'),batchBtn=sceneEl.querySelector('[data-scene-action="batch"]'),resetBtn=sceneEl.querySelector('[data-scene-action="reset"]'),reseedBtn=sceneEl.querySelector('[data-scene-action="reseed"]');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let seed=2026,rng=M.rng(seed),kA=0,kB=0,kMiss=0,N=0,log=[],running=false,raf=0,animStart=0,currentTrial=null;
 function nextOutcome(){
  const p=Number(pIn.value),etaA=Number(etaAIn.value),etaB=Number(etaBIn.value);
  const uPath=rng(),uDet=rng(),ch=uPath<p?'A':'B',eff=ch==='A'?etaA:etaB,clicked=uDet<=eff;
  return {index:N+1,ch,clicked,p,etaA,etaB};
 }
 function commitOutcome(tr){
  N=tr.index;
  if(tr.clicked){if(tr.ch==='A')kA++;else kB++;}else{kMiss++;}
  log.push(tr);
 }
 function setStageHighlight(active){
  for(const st of svgEl.querySelectorAll('.scene-stage'))st.classList.toggle('stage-active',st.dataset.stage===active);
 }
 function updateStaticTexts(stageMsg){
  const p=Number(pIn.value),etaA=Number(etaAIn.value),etaB=Number(etaBIn.value);
  pOut.value=p.toFixed(2);pOut.textContent=p.toFixed(2);
  etaAOut.value=etaA.toFixed(2);etaAOut.textContent=etaA.toFixed(2);
  etaBOut.value=etaB.toFixed(2);etaBOut.textContent=etaB.toFixed(2);
  const valPa=svgEl.querySelector('.val-pa'),valPb=svgEl.querySelector('.val-pb');
  if(valPa)valPa.textContent=p.toFixed(2);
  if(valPb)valPb.textContent=(1-p).toFixed(2);
  const valEtaA=svgEl.querySelector('.val-eta-a'),valEtaB=svgEl.querySelector('.val-eta-b');
  if(valEtaA)valEtaA.textContent=etaA.toFixed(2);
  if(valEtaB)valEtaB.textContent=etaB.toFixed(2);
  svgEl.querySelector('.scene-ka').textContent=String(kA);
  svgEl.querySelector('.scene-kb').textContent=String(kB);
  svgEl.querySelector('.scene-kmiss').textContent=String(kMiss);
  svgEl.querySelector('.scene-ntrials').textContent=String(N);
  const detTotal=kA+kB,fA=detTotal?kA/detTotal:null,se=detTotal?Math.sqrt((fA*(1-fA))/detTotal):null;
  svgEl.querySelector('.scene-fa').textContent=fA!==null?fA.toFixed(3):'—';
  svgEl.querySelector('.scene-se').textContent=se!==null?se.toFixed(3):'—';
  svgEl.querySelector('.scene-seed-label').textContent=`Seed ${seed} · deterministic replay`;
  if(stageMsg){delete liveEl.dataset.raw;liveEl.innerHTML=esc(stageMsg);typeset(sceneEl);}
  const tape=svgEl.querySelector('.scene-tape-cells');
  const recent=log.slice(-22);
  tape.innerHTML=recent.map((item,idx)=>{
   const xx=idx*32,col=!item.clicked?'transparent':item.ch==='A'?'var(--lab-blue)':'var(--lab-gold)';
   const stroke=!item.clicked?'var(--muted)':col,txt=!item.clicked?'–':item.ch,tcol=!item.clicked?'var(--muted)':'#fff';
   return `<g transform="translate(${xx},0)"><rect x="0" y="0" width="28" height="28" rx="5" fill="${col}" stroke="${stroke}" stroke-dasharray="${!item.clicked?'3 2':'none'}" opacity="0.9"/><text x="14" y="19" text-anchor="middle" style="font:600 13px var(--sans);fill:${tcol}">${txt}</text></g>`;
  }).join('');
 }
 function renderVisualPhase(tr,phase){
  const pktIn=svgEl.querySelector('.scene-packet-in'),pktA=svgEl.querySelector('.scene-packet-a'),pktB=svgEl.querySelector('.scene-packet-b');
  const flashA=svgEl.querySelector('.scene-flash-a'),flashB=svgEl.querySelector('.scene-flash-b'),led=svgEl.querySelector('.trigger-led');
  const prepSt=svgEl.querySelector('.prep-status'),measSt=svgEl.querySelector('.meas-status');
  if(!tr){
   setStageHighlight('');pktIn.setAttribute('opacity','0');pktA.setAttribute('opacity','0');pktB.setAttribute('opacity','0');
   flashA.setAttribute('opacity','0');flashB.setAttribute('opacity','0');led.setAttribute('opacity','0.35');
   prepSt.textContent='Gate ready';
   measSt.textContent=N?`Recorded ${kA+kB} clicks in ${N} trigger windows`:'Waiting for first trigger window';
   return;
  }
  if(phase<0.35){
   const u=phase/0.35;
   setStageHighlight('prep');led.setAttribute('opacity','1');
   pktIn.setAttribute('opacity','1');pktIn.setAttribute('cx',(134+(326-134)*u).toFixed(1));pktIn.setAttribute('cy','140');
   pktA.setAttribute('opacity','0');pktB.setAttribute('opacity','0');flashA.setAttribute('opacity','0');flashB.setAttribute('opacity','0');
   prepSt.textContent=`Window #${tr.index}: pulse emitted`;
   measSt.textContent='Detectors gated open';
  }else if(phase<0.74){
   const u=(phase-0.35)/0.39;
   setStageHighlight('trans');led.setAttribute('opacity','0.5');pktIn.setAttribute('opacity','0');
   pktA.setAttribute('opacity',String(Math.max(0.25,Math.sqrt(tr.p))));
   pktB.setAttribute('opacity',String(Math.max(0.25,Math.sqrt(1-tr.p))));
   pktA.setAttribute('cx',(326+(502-326)*u).toFixed(1));pktA.setAttribute('cy',(140+(76-140)*u).toFixed(1));
   pktB.setAttribute('cx',(326+(502-326)*u).toFixed(1));pktB.setAttribute('cy',(140+(204-140)*u).toFixed(1));
   flashA.setAttribute('opacity','0');flashB.setAttribute('opacity','0');
   prepSt.textContent=`Window #${tr.index}: gate active`;
   measSt.textContent='Awaiting detector click…';
  }else{
   const u=(phase-0.74)/0.26;
   setStageHighlight('meas');pktIn.setAttribute('opacity','0');pktA.setAttribute('opacity','0');pktB.setAttribute('opacity','0');
   const glow=String((1-u*0.6)*0.7);
   flashA.setAttribute('opacity',tr.clicked&&tr.ch==='A'?glow:'0');
   flashB.setAttribute('opacity',tr.clicked&&tr.ch==='B'?glow:'0');
   prepSt.textContent=`Window #${tr.index}: complete`;
   measSt.textContent=tr.clicked?`Click registered in Det ${tr.ch}!`:`Channel ${tr.ch} missed (efficiency < 1)`;
  }
 }
 function stopScene(msg){
  running=false;cancelAnimationFrame(raf);currentTrial=null;
  playBtn.textContent='Run trials';playBtn.setAttribute('aria-pressed','false');
  renderVisualPhase(null,1);updateStaticTexts(msg);
 }
 function animateFrame(now){
  if(!currentTrial)currentTrial=nextOutcome();
  if(!animStart)animStart=now;
  const duration=reduced.matches?10:480,elapsed=now-animStart,phase=Math.min(1,elapsed/duration);
  renderVisualPhase(currentTrial,phase);
  if(phase>=1){
   commitOutcome(currentTrial);
   const done=currentTrial;currentTrial=null;animStart=0;
   updateStaticTexts(`Trial #${done.index}: ${done.clicked?`click in \\(D_${done.ch}\\)`:`missed in \\(D_${done.ch}\\)`} (\\(k_A=${kA},\\; k_B=${kB},\\; N=${N}\\)).`);
   renderVisualPhase(done,0.85);
   if(running){raf=requestAnimationFrame(animateFrame);}
  }else{
   raf=requestAnimationFrame(animateFrame);
  }
 }
 function resetScene(newSeed){
  running=false;cancelAnimationFrame(raf);currentTrial=null;animStart=0;
  if(newSeed)seed++;
  rng=M.rng(seed);kA=0;kB=0;kMiss=0;N=0;log=[];
  playBtn.textContent='Run trials';playBtn.setAttribute('aria-pressed','false');
  renderVisualPhase(null,0);
  updateStaticTexts(newSeed?`Switched to new seed ${seed}. Ready to run trials.`:`Reset to seed ${seed}. Stepping or running replays the identical sequence.`);
 }
 playBtn.addEventListener('click',()=>{
  if(running){stopScene('Paused trial sequence.');return;}
  running=true;animStart=0;playBtn.textContent='Pause';playBtn.setAttribute('aria-pressed','true');
  raf=requestAnimationFrame(animateFrame);
 });
 stepBtn.addEventListener('click',()=>{
  running=false;cancelAnimationFrame(raf);playBtn.textContent='Run trials';playBtn.setAttribute('aria-pressed','false');
  currentTrial=nextOutcome();animStart=0;raf=requestAnimationFrame(animateFrame);
 });
 batchBtn.addEventListener('click',()=>{
  running=false;cancelAnimationFrame(raf);playBtn.textContent='Run trials';playBtn.setAttribute('aria-pressed','false');
  let lastTr=null;for(let i=0;i<25;i++){lastTr=nextOutcome();commitOutcome(lastTr);}
  renderVisualPhase(lastTr,0.85);
  updateStaticTexts(`Added 25 trials (\\(N=${N}:\\; k_A=${kA},\\; k_B=${kB},\\; k_{\\mathrm{miss}}=${kMiss}\\)).`);
 });
 resetBtn.addEventListener('click',()=>resetScene(false));
 reseedBtn.addEventListener('click',()=>resetScene(true));
 for(const inp of [pIn,etaAIn,etaBIn])inp.addEventListener('input',()=>resetScene(false));
 controlsEl.hidden=false;typeset(sceneEl);resetScene(false);
}
for(const sceneEl of document.querySelectorAll('.qe-scene[data-scene="section-1-2"]')){
 const svgEl=sceneEl.querySelector('svg'),controlsEl=sceneEl.querySelector('.qe-scene-controls'),liveEl=sceneEl.querySelector('.qe-scene-live');
 const pIn=sceneEl.querySelector('[data-s12-p]'),nIn=sceneEl.querySelector('[data-s12-n]'),etaIn=sceneEl.querySelector('[data-s12-eta]');
 const pOut=sceneEl.querySelector('#scene-1-2-p-out'),nOut=sceneEl.querySelector('#scene-1-2-n-out'),etaOut=sceneEl.querySelector('#scene-1-2-eta-out');
 const playBtn=sceneEl.querySelector('[data-s12-action="play"]'),stepBtn=sceneEl.querySelector('[data-s12-action="step"]'),resetBtn=sceneEl.querySelector('[data-s12-action="reset"]');
 let seed=3026,rng=M.rng(seed),running=false,raf=0,last=0,sampleKa=53;
 function drawS12(newSample){
  const p=Number(pIn.value),N=Number(nIn.value),ratio=Number(etaIn.value);
  pOut.value=p.toFixed(2);pOut.textContent=p.toFixed(2);
  nOut.value=String(N);nOut.textContent=String(N);
  etaOut.value=ratio.toFixed(2);etaOut.textContent=ratio.toFixed(2);
  const fA=(p*ratio)/(p*ratio+(1-p)),mean=N*p,sigma=Math.sqrt(N*p*(1-p)),se=Math.sqrt(p*(1-p)/N);
  if(newSample){
   let k=0;for(let i=0;i<N;i++)if(rng()<fA)k++;
   sampleKa=k;
  }else{
   sampleKa=Math.min(N,Math.max(0,Math.round(N*fA+0.6*sigma)));
  }
  const zScore=sigma>0?Math.abs(sampleKa-mean)/sigma:0;
  svgEl.querySelector('.s12-mean').textContent=mean.toFixed(1);
  svgEl.querySelector('.s12-sigma').textContent=sigma.toFixed(2);
  svgEl.querySelector('.s12-ka').textContent=String(sampleKa);
  svgEl.querySelector('.s12-z').textContent=zScore.toFixed(2);
  svgEl.querySelector('.s12-p').textContent=p.toFixed(2);
  svgEl.querySelector('.s12-fa').textContent=fA.toFixed(3);
  svgEl.querySelector('.s12-se').textContent=se.toFixed(3);
  // Left panel: Gaussian/Binomial histogram around mean
  const histG=svgEl.querySelector('.s12-hist');
  const kMin=Math.max(0,Math.floor(mean-3.5*sigma)),kMax=Math.min(N,Math.ceil(mean+3.5*sigma)),binsCount=Math.max(7,Math.min(25,kMax-kMin+1));
  const stepK=Math.max(1,Math.round((kMax-kMin)/binsCount));
  let barsHtml=`<path class="grid" d="M0 195 H310"/>`;
  const bandL=Math.max(0,Math.min(310,((mean-sigma-kMin)/Math.max(1,kMax-kMin))*310));
  const bandR=Math.max(0,Math.min(310,((mean+sigma-kMin)/Math.max(1,kMax-kMin))*310));
  barsHtml+=`<rect x="${bandL.toFixed(1)}" y="10" width="${Math.max(4,bandR-bandL).toFixed(1)}" height="185" fill="var(--lab-blue)" opacity="0.13"/>`;
  const peakP=1/Math.sqrt(2*Math.PI*sigma*sigma);
  for(let k=kMin;k<=kMax;k+=stepK){
   const prob=Math.exp(-((k-mean)**2)/(2*sigma*sigma))*peakP;
   const h=Math.min(175,(prob/peakP)*165);
   const xx=((k-kMin)/Math.max(1,kMax-kMin))*290+6;
   const bw=Math.max(4,260/binsCount);
   barsHtml+=`<rect x="${(xx-bw/2).toFixed(1)}" y="${(195-h).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" fill="var(--lab-blue)" opacity="0.72" rx="2"/>`;
  }
  const sampleX=Math.max(8,Math.min(302,((sampleKa-kMin)/Math.max(1,kMax-kMin))*290+6));
  barsHtml+=`<path d="M${sampleX.toFixed(1)} 12 V195" stroke="var(--lab-gold)" stroke-width="2.5" stroke-dasharray="4 3"/><circle cx="${sampleX.toFixed(1)}" cy="28" r="6" fill="var(--lab-gold)"/>`;
  barsHtml+=`<text x="6" y="212" class="small">${kMin}</text><text x="155" y="212" text-anchor="middle" class="small">${Math.round(mean)}</text><text x="304" y="212" text-anchor="end" class="small">${kMax}</text>`;
  histG.innerHTML=barsHtml;
  // Right panel: 1/sqrt(N) funnel + trajectory
  const funG=svgEl.querySelector('.s12-funnel');
  const Y=v=>195-Math.max(0,Math.min(1,v))*180,X=n=>((n-1)/Math.max(1,N-1))*310;
  let upper=[],lower=[],traj=[];
  const trajRng=M.rng(seed);let runA=0;
  for(let n=1;n<=N;n++){
   if(trajRng()<fA)runA++;
   if(n===1||n%Math.max(1,Math.floor(N/45))===0||n===N){
    const s=Math.sqrt(p*(1-p)/n);
    upper.push([X(n),Y(Math.min(1,p+s))]);
    lower.push([X(n),Y(Math.max(0,p-s))]);
    traj.push([X(n),Y(runA/n)]);
   }
  }
  const pathStr=pts=>pts.map(([x,y],i)=>`${i?'L':'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  let funHtml=`<path class="grid" d="M0 ${Y(p).toFixed(1)} H310"/>`;
  if(Math.abs(fA-p)>0.005)funHtml+=`<path class="bound" d="M0 ${Y(fA).toFixed(1)} H310"/>`;
  funHtml+=`<path d="${pathStr(upper)}" fill="none" stroke="var(--lab-blue)" stroke-width="1.5" stroke-dasharray="4 3"/>`;
  funHtml+=`<path d="${pathStr(lower)}" fill="none" stroke="var(--lab-blue)" stroke-width="1.5" stroke-dasharray="4 3"/>`;
  funHtml+=`<path d="${pathStr(traj)}" fill="none" stroke="var(--lab-gold)" stroke-width="2.4"/>`;
  funHtml+=`<text x="4" y="212" class="small">n = 1</text><text x="306" y="212" text-anchor="end" class="small">N = ${N}</text>`;
  funG.innerHTML=funHtml;
  delete liveEl.dataset.raw;
  liveEl.innerHTML=esc(`Draw: \\(k_A = ${sampleKa} / ${N}\\) (\\(\\hat{p} = ${(sampleKa/N).toFixed(3)}\\), \\(\\mathrm{SE} = ${se.toFixed(3)}\\), efficiency-shifted \\(f_A = ${fA.toFixed(3)}\\)).`);
  typeset(sceneEl);
 }
 function frame12(now){
  if(!running)return;
  if(!last||now-last>320){seed++;rng=M.rng(seed);drawS12(true);last=now;}
  raf=requestAnimationFrame(frame12);
 }
 playBtn.addEventListener('click',()=>{
  if(running){running=false;cancelAnimationFrame(raf);playBtn.textContent='Animate draws';playBtn.setAttribute('aria-pressed','false');return;}
  running=true;last=0;playBtn.textContent='Pause';playBtn.setAttribute('aria-pressed','true');raf=requestAnimationFrame(frame12);
 });
 stepBtn.addEventListener('click',()=>{running=false;cancelAnimationFrame(raf);playBtn.textContent='Animate draws';playBtn.setAttribute('aria-pressed','false');seed++;rng=M.rng(seed);drawS12(true);});
 resetBtn.addEventListener('click',()=>{running=false;cancelAnimationFrame(raf);playBtn.textContent='Animate draws';playBtn.setAttribute('aria-pressed','false');pIn.value='0.50';nIn.value='100';etaIn.value='1.00';seed=3026;rng=M.rng(seed);drawS12(false);});
 for(const inp of [pIn,nIn,etaIn])inp.addEventListener('input',()=>drawS12(true));
 controlsEl.hidden=false;drawS12(false);
}
for(const sceneEl of document.querySelectorAll('.qe-scene[data-scene="section-1-3"]')){
 const svgEl=sceneEl.querySelector('svg'),controlsEl=sceneEl.querySelector('.qe-scene-controls'),liveEl=sceneEl.querySelector('.qe-scene-live');
 const pIn=sceneEl.querySelector('[data-s13-p]'),eta2In=sceneEl.querySelector('[data-s13-eta2]');
 const pOut=sceneEl.querySelector('#scene-1-3-p-out'),eta2Out=sceneEl.querySelector('#scene-1-3-eta2-out');
 const playBtn=sceneEl.querySelector('[data-s13-action="play"]'),swapBtn=sceneEl.querySelector('[data-s13-action="swap"]'),resetBtn=sceneEl.querySelector('[data-s13-action="reset"]');
 let swapped=false,running=false,raf=0,t0=0;
 function updateS13(phase=0){
  const p=Number(pIn.value),eta1=1.0,eta2=Number(eta2In.value);
  pOut.value=p.toFixed(2);pOut.textContent=p.toFixed(2);
  eta2Out.value=eta2.toFixed(2);eta2Out.textContent=eta2.toFixed(2);
  const f1=(p*eta1)/(p*eta1+(1-p)*eta2),f2=(p*eta2)/(p*eta2+(1-p)*eta1);
  const r1=f1/(1-f1),r2=f2/(1-f2),g=Math.sqrt(r1*r2),pCal=g/(1+g),bias=f1-p;
  svgEl.querySelector('.s13-eta1').textContent=eta1.toFixed(2);
  svgEl.querySelector('.s13-eta2').textContent=eta2.toFixed(2);
  svgEl.querySelector('.s13-f1').textContent=f1.toFixed(3);
  svgEl.querySelector('.s13-f2').textContent=f2.toFixed(3);
  svgEl.querySelector('.s13-pcal').textContent=pCal.toFixed(3);
  svgEl.querySelector('.s13-ptrue').textContent=p.toFixed(3);
  svgEl.querySelector('.s13-det-top').setAttribute('transform',swapped?'translate(0, 108)':'translate(0, 0)');
  svgEl.querySelector('.s13-det-bot').setAttribute('transform',swapped?'translate(0, -108)':'translate(0, 0)');
  svgEl.querySelector('.s13-status-eff').textContent=Math.abs(eta1-eta2)<0.01?'Matched detector efficiencies':(swapped?'Config 2: swapped ports':'Config 1: direct ports');
  svgEl.querySelector('.s13-status-bias').textContent=`${bias>=0?'+':''}${bias.toFixed(3)}`;
  const pulse=svgEl.querySelector('.s13-pulse');
  if(running){
   pulse.setAttribute('opacity','1');
   const u=(phase%1);
   if(u<0.4){pulse.setAttribute('cx',(138+(206-138)*(u/0.4)).toFixed(1));pulse.setAttribute('cy','158');}
   else{const v=(u-0.4)/0.6;pulse.setAttribute('cx',(206+(304-206)*v).toFixed(1));pulse.setAttribute('cy',(158+((swapped?212:104)-158)*v).toFixed(1));}
  }else{
   pulse.setAttribute('opacity','0');
  }
  delete liveEl.dataset.raw;
  liveEl.innerHTML=esc(`Configuration: ${swapped?'Swapped (\\(D_2\\) on \\(A\\))':'Direct (\\(D_1\\) on \\(A\\))'} · \\(f_A^{(1)}=${f1.toFixed(3)},\\; f_A^{(2)}=${f2.toFixed(3)},\\; \\hat{p}_{\\mathrm{cal}}=${pCal.toFixed(3)}\\).`);
  typeset(sceneEl);
 }
 function loop13(now){
  if(!running)return;
  if(!t0)t0=now;
  const elapsed=(now-t0)/900;
  swapped=Math.floor(elapsed)%2===1;
  updateS13(elapsed);
  raf=requestAnimationFrame(loop13);
 }
 playBtn.addEventListener('click',()=>{
  if(running){running=false;cancelAnimationFrame(raf);playBtn.textContent='Run swap cycle';playBtn.setAttribute('aria-pressed','false');updateS13(0);return;}
  running=true;t0=0;playBtn.textContent='Pause';playBtn.setAttribute('aria-pressed','true');raf=requestAnimationFrame(loop13);
 });
 swapBtn.addEventListener('click',()=>{running=false;cancelAnimationFrame(raf);playBtn.textContent='Run swap cycle';playBtn.setAttribute('aria-pressed','false');swapped=!swapped;updateS13(0);});
 resetBtn.addEventListener('click',()=>{running=false;cancelAnimationFrame(raf);playBtn.textContent='Run swap cycle';playBtn.setAttribute('aria-pressed','false');swapped=false;pIn.value='0.50';eta2In.value='0.60';updateS13(0);});
 for(const inp of [pIn,eta2In])inp.addEventListener('input',()=>updateS13(0));
 controlsEl.hidden=false;updateS13(0);
}
for(const sceneEl of document.querySelectorAll('.qe-scene[data-kind]')){
 const kind=sceneEl.dataset.kind,secIdx=Number(sceneEl.dataset.sec),svgEl=sceneEl.querySelector('svg'),controlsEl=sceneEl.querySelector('.qe-scene-controls'),liveEl=sceneEl.querySelector('.qe-scene-live');
 const valIn=sceneEl.querySelector('[data-scene-val]'),valOut=sceneEl.querySelector(`#${sceneEl.dataset.scene}-val-out`);
 const modeSel=sceneEl.querySelector('[data-scene-mode]'),etaIn=sceneEl.querySelector('[data-scene-eta]'),etaOut=sceneEl.querySelector(`#${sceneEl.dataset.scene}-eta-out`);
 const playBtn=sceneEl.querySelector('[data-gen-action="play"]'),stepBtn=sceneEl.querySelector('[data-gen-action="step"]'),resetBtn=sceneEl.querySelector('[data-gen-action="reset"]');
 const initVal=Number(valIn.value),initMode=modeSel?.value||'default';
 let running=false,raf=0,last=0,tick=0;
 function curMode(){return modeSel?.value||'default';}
 function poly(points,cls='curve'){return `<path class="${cls}" d="${points.map(([x,y],i)=>`${i?'L':'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ')}"/>`;}
 function renderGen(){
  const x=Number(valIn.value),eta=etaIn?Number(etaIn.value):1.0,model=M.calc(kind,x,curMode());
  valOut.value=String(x);valOut.textContent=String(x);
  if(etaOut){etaOut.value=eta.toFixed(2);etaOut.textContent=eta.toFixed(2);}
  const primary=model.values[0]??0.5;
  if(secIdx===1){
   // Animate apparatus elements in Section N.1
   if(model.vector){const [a,b,c]=model.vector;const px=205+105*a+48*b,py=165-105*c-37*b;svgEl.querySelector('.state-vector')?.setAttribute('d',`M205 165L${px} ${py}`);const tip=svgEl.querySelector('.state-tip');tip?.setAttribute('cx',px);tip?.setAttribute('cy',py);}
   svgEl.querySelector('.middle-axis')?.setAttribute('transform',`rotate(${x} 360 167)`);
   const coh=svgEl.querySelector('.coherence-link');if(coh)coh.style.opacity=String(x);
   if(kind==='tunnel'){const t=model.values[0],pts=Array.from({length:160},(_,i)=>{const xx=40+i*640/159,amp=xx<300?42:xx<420?42*Math.exp(-x*(xx-300)/120):42*Math.sqrt(t);return[xx,215-amp*Math.sin(xx/12+tick*0.2)];});svgEl.querySelector('.tunnel-wave')?.setAttribute('d',pts.map(([a,b],i)=>`${i?'L':'M'}${a.toFixed(1)} ${b.toFixed(1)}`).join(' '));}
   if(kind==='hom')svgEl.querySelector('.packet-b')?.setAttribute('transform',`translate(${x*25} ${-x*9})`);
   if(kind==='recoil'){const w=svgEl.querySelector('.pointer-waves');if(w){w.innerHTML=[-1,1].map((sign,i)=>poly(Array.from({length:80},(_,j)=>{let q=-5+j*10/79;return[390+q*30,110-45*Math.exp(-((q-sign*x/2)**2)/4)];}),i?'curve secondary':'curve')).join('');w.querySelectorAll('path').forEach((p,i)=>{p.style.fill='none';p.style.stroke=i?'var(--lab-gold)':'var(--lab-blue)';p.style.strokeWidth='2';});}}
   if(kind==='delayed'){const sp=svgEl.querySelectorAll('.splitter');if(sp[1])sp[1].style.opacity=curMode()==='open'?'0.12':'1';}
   if(kind==='bomb'){const ab=svgEl.querySelector('.absorber');if(ab)ab.style.opacity=curMode()==='absent'?'0.15':'1';}
   const pa=svgEl.querySelector('.s-n1-pulse-a'),pb=svgEl.querySelector('.s-n1-pulse-b');
   const u=(tick%36)/36;
   if(pa&&pb){
    pa.setAttribute('opacity','0.9');
    pa.setAttribute('cx',(55+u*560).toFixed(1));
    pa.setAttribute('cy',(160-48*Math.sin(Math.PI*u)).toFixed(1));
    pb.setAttribute('opacity','0.75');
    pb.setAttribute('cx',(55+u*560).toFixed(1));
    pb.setAttribute('cy',(160+48*Math.sin(Math.PI*u)).toFixed(1));
   }
   const stageIdx=u<0.34?1:u<0.67?2:3;
   const subTitle=sceneEl.dataset[`sub${stageIdx}`]||'';
   const stText=svgEl.querySelector('.s-n1-stage-text'),rdText=svgEl.querySelector('.s-n1-readout');
   if(stText)stText.textContent=`Stage ${stageIdx}: ${subTitle.slice(0,56)}`;
   if(rdText)rdText.textContent=`Setting = ${x} · Output = ${primary.toFixed(3)}`;
  }else if(secIdx===2){
   // Animate Left Dial + Right Quantitative Plot in Section N.2
   const ang=model.domain[1]>10?rad(x):x*Math.PI/2;
   const vx=model.vector?model.vector[0]*75:Math.cos(ang)*72;
   const vy=model.vector?-model.vector[2]*75:-Math.sin(ang)*72;
   svgEl.querySelector('.s-n2-vec-a')?.setAttribute('d',`M0 0 L${(vx*0.55).toFixed(1)} 0`);
   svgEl.querySelector('.s-n2-vec-b')?.setAttribute('d',`M${(vx*0.55).toFixed(1)} 0 L${vx.toFixed(1)} ${vy.toFixed(1)}`);
   svgEl.querySelector('.s-n2-vec-tot')?.setAttribute('d',`M0 0 L${vx.toFixed(1)} ${vy.toFixed(1)}`);
   const tip=svgEl.querySelector('.s-n2-tip');if(tip){tip.setAttribute('cx',vx.toFixed(1));tip.setAttribute('cy',vy.toFixed(1));}
   const valSpan=svgEl.querySelector('.s-n2-val');if(valSpan)valSpan.textContent=primary.toFixed(4);
   const plotG=svgEl.querySelector('.s-n2-plot');
   if(plotG){
    const [lo,hi]=model.domain,[ylo,yhi]=model.range,W=370,H=200;
    const X=v=>((v-lo)/Math.max(1e-6,hi-lo))*W,Y=v=>H-((v-ylo)/Math.max(1e-6,yhi-ylo))*170;
    let h=`<path class="grid" d="M0 ${H} H${W}"/><path class="grid" d="M0 ${Y((ylo+yhi)/2).toFixed(1)} H${W}"/>`;
    if(model.curve){
     const pts=Array.from({length:121},(_,i)=>{const t=lo+(hi-lo)*i/120;return[X(t),Y(model.curve(t))];});
     h+=poly(pts,'curve')+`<circle class="point" cx="${X(x).toFixed(1)}" cy="${Y(model.curve(x)).toFixed(1)}" r="6"/>`;
    }else{
     const bw=W/Math.max(1,model.values.length);
     model.values.forEach((v,i)=>{
      const y0=Y(0),yv=Y(v);
      h+=`<rect class="bar" x="${(i*bw+10).toFixed(1)}" y="${Math.min(y0,yv).toFixed(1)}" width="${(bw*0.65).toFixed(1)}" height="${Math.abs(yv-y0).toFixed(1)}"/>`;
     });
    }
    h+=`<text x="0" y="222" class="small">${lo}</text><text x="${W}" y="222" text-anchor="end" class="small">${hi}</text>`;
    plotG.innerHTML=h;
   }
  }else if(secIdx===3){
   // Animate Ideal vs Imperfect Apparatus Comparison + Audit Ledger in Section N.3
   const plotG=svgEl.querySelector('.s-n3-plot');
   const [lo,hi]=model.domain,[ylo,yhi]=model.range,W=370,H=200;
   const X=v=>((v-lo)/Math.max(1e-6,hi-lo))*W,Y=v=>H-((v-ylo)/Math.max(1e-6,yhi-ylo))*170;
   const degrade=v=>kind==='sensing'?v/Math.max(0.2,eta):kind==='photons'?1+(v-1)*eta:kind==='bell'||kind==='ghz'?v*eta:0.5+(v-0.5)*eta;
   if(plotG){
    let h=`<path class="grid" d="M0 ${H} H${W}"/><path class="grid" d="M0 ${Y((ylo+yhi)/2).toFixed(1)} H${W}"/>`;
    if(model.curve){
     const ptsIdeal=Array.from({length:121},(_,i)=>{const t=lo+(hi-lo)*i/120;return[X(t),Y(model.curve(t))];});
     const ptsObs=Array.from({length:121},(_,i)=>{const t=lo+(hi-lo)*i/120;return[X(t),Y(degrade(model.curve(t)))];});
     h+=poly(ptsIdeal,'curve')+poly(ptsObs,'curve secondary');
     h+=`<circle class="point" cx="${X(x).toFixed(1)}" cy="${Y(degrade(model.curve(x))).toFixed(1)}" r="6"/>`;
    }else{
     const bw=W/Math.max(1,model.values.length);
     model.values.forEach((v,i)=>{
      const y0=Y(0),yi=Y(v),yo=Y(degrade(v));
      h+=`<rect class="bar" x="${(i*bw+8).toFixed(1)}" y="${Math.min(y0,yi).toFixed(1)}" width="${(bw*0.32).toFixed(1)}" height="${Math.abs(yi-y0).toFixed(1)}"/>`;
      h+=`<rect x="${(i*bw+8+bw*0.35).toFixed(1)}" y="${Math.min(y0,yo).toFixed(1)}" width="${(bw*0.32).toFixed(1)}" height="${Math.abs(yo-y0).toFixed(1)}" fill="var(--lab-gold)" opacity="0.8"/>`;
     });
    }
    h+=`${svgText(0,222,'Blue: ideal (\\(\\eta = 1\\))','start','small',180)}${svgText(W,222,`Gold: observed (\\(\\eta = ${eta.toFixed(2)}\\))`,'end','small',210)}`;
    plotG.innerHTML=h;
   }
   const idealVal=model.curve?model.curve(x):primary,obsVal=degrade(idealVal);
   const elEta=svgEl.querySelector('.s-n3-eta'),elId=svgEl.querySelector('.s-n3-ideal'),elOb=svgEl.querySelector('.s-n3-obs'),elVer=svgEl.querySelector('.s-n3-verdict');
   if(elEta)elEta.textContent=eta.toFixed(2);
   if(elId)elId.textContent=idealVal.toFixed(3);
   if(elOb)elOb.textContent=obsVal.toFixed(3);
   if(elVer){
    const pass=kind==='bell'?obsVal>2:kind==='hom'?eta>0.5:kind==='teleport'?(1+eta)/2>2/3:eta>=0.7;
    elVer.textContent=pass?'Threshold certified (passes audit)':'Below certification threshold';
   }
  }
  delete liveEl.dataset.raw;
  liveEl.innerHTML=esc(`${ model.note }`);
  typeset(sceneEl);
 }
 function stepGen(){
  tick++;
  const min=Number(valIn.min),max=Number(valIn.max),step=Number(valIn.step);
  const delta=['bomb','ghz','extended'].includes(kind)?1:Math.max(step,(max-min)/80);
  let nxt=Number(valIn.value)+delta;
  if(nxt>max+1e-8)nxt=min;
  valIn.value=String(Number(nxt.toFixed(4)));
  renderGen();
 }
 function loopGen(now){
  if(!running)return;
  if(!last||now-last>90){stepGen();last=now;}
  raf=requestAnimationFrame(loopGen);
 }
 playBtn.addEventListener('click',()=>{
  if(running){running=false;cancelAnimationFrame(raf);playBtn.textContent='Animate';playBtn.setAttribute('aria-pressed','false');return;}
  running=true;last=0;playBtn.textContent='Pause';playBtn.setAttribute('aria-pressed','true');raf=requestAnimationFrame(loopGen);
 });
 stepBtn.addEventListener('click',()=>{running=false;cancelAnimationFrame(raf);playBtn.textContent='Animate';playBtn.setAttribute('aria-pressed','false');stepGen();});
 resetBtn.addEventListener('click',()=>{running=false;cancelAnimationFrame(raf);playBtn.textContent='Animate';playBtn.setAttribute('aria-pressed','false');valIn.value=String(initVal);if(modeSel)modeSel.value=initMode;if(etaIn)etaIn.value='0.85';tick=0;renderGen();});
 valIn.addEventListener('input',()=>renderGen());
 modeSel?.addEventListener('change',()=>renderGen());
 etaIn?.addEventListener('input',()=>renderGen());
 controlsEl.hidden=false;renderGen();
}
window.addEventListener('load',()=>{for(const el of document.querySelectorAll('.qe-lab, .qe-scene'))typeset(el);});
})();
