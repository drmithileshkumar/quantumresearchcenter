/* Progressive enhancement: static lessons and diagrams do not require this file. */
(() => {
'use strict';
const M=window.QEModels,esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=x=>Number(x).toFixed(4),rad=x=>x*Math.PI/180;
for(const lab of document.querySelectorAll('.qe-lab')){
 const kind=lab.dataset.kind,input=lab.querySelector('input'),select=lab.querySelector('select'),output=lab.querySelector('output'),chart=lab.querySelector('.qe-chart'),readout=lab.querySelector('.qe-readout'),table=lab.querySelector('.qe-table-wrap'),note=lab.querySelector('.qe-model-note'),status=lab.querySelector('.qe-live'),play=lab.querySelector('[data-action=play]'),diagram=lab.querySelector('.qe-apparatus');
 const initial=Number(input.value),initialMode=select?.value||'default',originalDiagram=diagram.innerHTML,reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let random=M.rng(),bins=[],arrivals=[],N=0,running=false,raf=0,last=0,tick=0,seed=2026,scan=null;
 function mode(){return select?.value||'default';}
 function announce(s){status.textContent=s;}
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
   model.values.forEach((v,i)=>{const xx=left+10+i*bw;g+=`<rect class="bar" x="${xx}" y="${Math.min(yy(0),yy(v))}" width="${bw*.65}" height="${Math.abs(yy(v)-yy(0))}"/><text x="${xx+bw*.325}" y="278" text-anchor="middle">${esc(width<450?model.labels[i].replace('D0: inconclusive','D0').replace('D1: certifies','D1').replace('Before: P0','Before P0').replace('Corrected: P0','After P0'):model.labels[i])}</text>`;
    if(kind==='counts'&&N)g+=`<circle class="point" cx="${xx+bw*.325}" cy="${yy(bins[i]/N)}" r="6"/>`;
   });
   g+='<text x="65" y="22">'+(kind==='ghz'?'Predicted product':kind==='counts'?'Probability · dots: samples':'Predicted probability')+'</text>';
  }else{
   for(let i=0;i<=4;i++){let v=ylo+(yhi-ylo)*i/4;g+=`<path class="grid" d="M${left} ${Y(v)}H${right}"/><text x="43" y="${Y(v)+4}" text-anchor="end">${v.toFixed(yhi<=.1?2:1)}</text>`;}
   for(let i=0;i<=4;i++){let v=lo+(hi-lo)*i/4;g+=`<text x="${X(v)}" y="274" text-anchor="middle">${v.toFixed(hi>20?0:1)}</text>`;}
   g+=`<text x="65" y="22">${esc(model.ylabel)}</text><text x="${width/2}" y="302" text-anchor="middle">${esc(model.xlabel)}</text>`;
   function curve(fn,cls='curve'){return poly(Array.from({length:181},(_,i)=>{let t=lo+(hi-lo)*i/180;return[X(t),Y(fn(t))];}),cls);}
   if(model.curve)g+=curve(model.curve);
   if(kind==='eraser'){g+=curve(t=>(1-Math.cos(rad(t)))/2,'curve secondary')+curve(()=>.5,'curve tertiary');}
   if(kind==='bell')g+=`<path class="bound" d="M${left} ${Y(2)}H${right}"/><text x="${right-5}" y="${Y(2)-8}" text-anchor="end">Local bound 2</text>`;
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
   residual.innerHTML=`<title>Fit residuals</title><text x="${left}" y="20">Observed − fitted</text><path class="bound" d="M${left} 80H${right}"/>`+points.map(([phase,res])=>`<circle class="point" cx="${left+phase/360*span}" cy="${80-res/limit*45}" r="4"/>`).join('')+`<text x="55" y="40" text-anchor="end">${limit.toFixed(2)}</text><text x="55" y="84" text-anchor="end">0</text><text x="55" y="130" text-anchor="end">−${limit.toFixed(2)}</text><text x="${width/2}" y="148" text-anchor="middle">Phase (degrees), 0 → 360</text>`;
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
   diagram.innerHTML='<title id="diagram-title">Peres–Mermin square</title><desc id="diagram-desc">Rows have products +1. Columns have products +1, +1, −1.</desc>'+[['XI','IX','XX'],['IY','YI','YY'],['XY','YX','ZZ']].map((row,i)=>row.map((t,j)=>`<g class="node"><rect x="${75+j*155}" y="${35+i*90}" width="135" height="65" rx="8"/><text x="${142+j*155}" y="${74+i*90}" text-anchor="middle">${t}</text></g>`).join('')+`<text x="600" y="${74+i*90}" text-anchor="middle">+1</text>`).join('')+'<text x="142" y="332" text-anchor="middle">+1</text><text x="297" y="332" text-anchor="middle">+1</text><text x="452" y="332" text-anchor="middle">−1</text>';
  }else if(kind==='ghz'&& !diagram.querySelector('.ray'))diagram.innerHTML=originalDiagram;
  if(kind==='slits'){
   let dots=diagram.querySelector('.detections');if(!dots){dots=document.createElementNS('http://www.w3.org/2000/svg','g');dots.setAttribute('class','detections');diagram.append(dots);}
   dots.innerHTML=arrivals.slice(-600).map((bin,i)=>`<circle cx="${645+(i*17%50)}" cy="${30+(bin+.5)/64*285}" r="2" fill="var(--lab-gold)" opacity=".65"/>`).join('');
  }
  if(kind==='extended'&&mode()==='records'){
   diagram.innerHTML='<title id="diagram-title">Friend record probabilities</title><desc id="diagram-desc">Three possible record pairs, each with probability one third; h,u is absent.</desc>'+[['h,d','1/3'],['h,u','0'],['t,d','1/3'],['t,u','1/3']].map(([label,p],i)=>`<g class="node"><rect x="${30+i*175}" y="110" width="140" height="100" rx="10"/><text x="${100+i*175}" y="150" text-anchor="middle">${label}</text><text x="${100+i*175}" y="184" text-anchor="middle">${p}</text></g>`).join('');
  }
  if(kind==='extended'&&mode()!=='records'){
   const n=Math.round(x),nodes=diagram.querySelectorAll('.node');nodes.forEach((el,i)=>el.style.opacity=i<3&&i>=n?'.25':'1');
  }
  if(['bomb','ghz'].includes(kind)){const nodes=[...diagram.querySelectorAll('.node')];nodes.forEach((el,i)=>el.classList.toggle('active-stage',i===Math.round(x)%nodes.length));}
  const traveller=diagram.querySelector('.traveller');if(traveller){const t=(tick%40)/40;let px,py;if(t<.2){px=42+t/.2*133;py=160;}else if(t<.6){const u=(t-.2)/.4;px=175+330*u;py=160-100*Math.sin(Math.PI*u);}else{const u=(t-.6)/.4;px=505+140*u;py=160-65*u;}traveller.setAttribute('cx',px);traveller.setAttribute('cy',py);}
 }
 function render(){
  const x=Number(input.value),model=M.calc(kind,x,mode());output.value=String(x);output.textContent=String(x);draw(model,x);scene(model,x);
  let vals=model.values,labels=model.labels;
  if(kind==='slits'){vals=[N,x];labels=['Synthetic events','Visibility'];}
  if(kind==='counts'){vals=[...vals,N,...bins];labels=[...labels,'Trials','A counts','B counts'];}
  if(kind==='capstone'){vals=[x,scan.estimate,scan.se,scan.seed];labels=['Generating V','Estimated V','Approx. standard error','Seed'];}
  readout.innerHTML=vals.map((v,i)=>`<div class="qe-metric"><small>${esc(labels[i])}</small><strong>${Number.isInteger(v)&&Math.abs(v)>1?v:fmt(v)}</strong></div>`).join('');
  note.textContent=model.note+(kind==='eraser'?' Blue: given +; dashed gold: given −; dotted violet: unsorted.':'')+(kind==='slits'?` ${N} synthetic events; dots show empirical bin fractions.`:'')+(kind==='capstone'?' Blue: generating curve; dashed gold: fitted curve; dots: counts / trials.':'');
  let rows=vals.map((v,i)=>[labels[i],fmt(v)]),heads=['Quantity','Value'];
  if(kind==='slits'){heads=['Screen bin','Predicted probability','Synthetic count'];rows=model.values.map((v,i)=>[i+1,fmt(v),bins[i]]);}
  if(kind==='capstone'){heads=['Phase (°)','Trials','D0','D1','Residual'];rows=scan.rows.map(r=>[r.phase,r.trials,r.a,r.b,fmt(r.a/r.trials-(1+scan.estimate*Math.cos(rad(r.phase)))/2)]);}
  table.innerHTML='<table><thead><tr>'+heads.map(h=>'<th scope="col">'+esc(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map((v,i)=>i?'<td>'+esc(v)+'</td>':'<th scope="row">'+esc(v)+'</th>').join('')+'</tr>').join('')+'</tbody></table>';
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
 lab.querySelector('[data-action=step]').addEventListener('click',()=>{stop();step();announce(kind==='counts'||kind==='slits'?`Recorded ${N} synthetic events.`:'Advanced one step. '+output.textContent);});
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
})();
