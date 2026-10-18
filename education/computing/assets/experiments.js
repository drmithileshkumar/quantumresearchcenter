/* Small book-native simulations. Every display is derived from the state. */
(() => {
 const clean=n=>Math.abs(n)<1e-10?0:n;
 const fmt=n=>clean(n).toFixed(3);
 const percent=p=>(100*p).toFixed(2)+'%';
 // Set text containing TeX, then typeset it once MathJax has started.
 const math=(el,text)=>{el.textContent=text;const mj=window.MathJax;if(mj?.startup?.promise&&mj.typesetPromise)mj.startup.promise=mj.startup.promise.then(()=>{mj.typesetClear([el]);return mj.typesetPromise([el])}).catch(()=>{})};
 function chart(lab,labels){const box=lab.querySelector('[data-bars]');labels.forEach(label=>{const row=document.createElement('div');row.className='lab-bar-row';const name=document.createElement('span');math(name,`\\(\\ket{${label}}\\)`);const track=document.createElement('div');track.className='lab-track';const fill=document.createElement('div');fill.className='lab-fill';track.append(fill);const out=document.createElement('output');row.append(name,track,out);box.append(row)});return values=>{[...box.children].forEach((row,i)=>{const a=clean(values[i]);row.querySelector('.lab-fill').style.width=percent(a*a);row.querySelector('.lab-fill').classList.toggle('negative',a<0);row.querySelector('output').textContent=percent(a*a);row.setAttribute('aria-label',`${labels[i]}: amplitude ${fmt(a)}, probability ${percent(a*a)}`)})}}
 document.querySelectorAll('[data-lab="gates"]').forEach(lab=>{let v=[1,0],history=[];const bars=chart(lab,['0','1']);function draw(){bars(v);math(lab.querySelector('[data-state]'),`State: \\(${fmt(v[0])}\\ket0 ${v[1]<0?'-':'+'} ${fmt(Math.abs(v[1]))}\\ket1\\)`);lab.querySelector('[data-status]').textContent=history.length?'Operations, in order: '+history.join(' → '):'Choose a gate to change the state.';lab.dataset.amplitudes=JSON.stringify(v)}lab.querySelectorAll('[data-gate]').forEach(b=>b.onclick=()=>{const [a,c]=v,g=b.dataset.gate;v=g==='H'?[(a+c)/Math.SQRT2,(a-c)/Math.SQRT2]:g==='X'?[c,a]:[a,-c];history.push(g);draw()});lab.querySelector('[data-reset]').onclick=()=>{v=[1,0];history=[];draw()};draw()});
 document.querySelectorAll('[data-lab="bell"]').forEach(lab=>{let step=0;const bars=chart(lab,['00','01','10','11']),next=lab.querySelector('[data-next]');function draw(){const v=step===0?[1,0,0,0]:step===1?[1/Math.SQRT2,0,1/Math.SQRT2,0]:[1/Math.SQRT2,0,0,1/Math.SQRT2];bars(v);math(lab.querySelector('[data-state]'),['State: \\(\\ket{00}\\)','State: \\((\\ket{00}+\\ket{10})/\\sqrt2\\)','State: \\((\\ket{00}+\\ket{11})/\\sqrt2\\)'][step]);lab.querySelector('[data-status]').textContent=['Both qubits start in 0.','The first qubit is in a superposition; the second is still 0. This state is a product.','CNOT changes the 10 component into 11. This pure state is entangled; a Z-basis measurement gives 00 or 11 with equal probability.'][step];next.textContent=['Apply H to the first qubit','Apply CNOT','Bell state prepared'][step];next.disabled=step===2;lab.dataset.amplitudes=JSON.stringify(v)}next.onclick=()=>{step=Math.min(2,step+1);draw()};lab.querySelector('[data-reset]').onclick=()=>{step=0;draw()};draw()});
 document.querySelectorAll('[data-lab="grover"]').forEach(lab=>{let k=0,timer=null;const n=lab.querySelector('[data-size]'),slider=lab.querySelector('[data-slider]'),play=lab.querySelector('[data-play]');function pause(){clearInterval(timer);timer=null;play.textContent='Play';play.setAttribute('aria-pressed','false')}function draw(){const theta=Math.asin(1/Math.sqrt(Number(n.value))),angle=(2*k+1)*theta,p=Math.sin(angle)**2;slider.value=k;lab.querySelector('[data-iteration]').value=k;lab.querySelector('[data-repetitions]').textContent=`(D O_f) × ${k}`;lab.querySelector('[data-state]').textContent=`Probability of finding the marked item: ${percent(p)}.`;lab.querySelector('[data-status]').textContent=`Iteration ${k}. The marked amplitude is ${fmt(Math.sin(angle))}; its squared magnitude gives the success probability.`;lab.dataset.probability=p;lab.querySelector('[data-next]').disabled=k===30;if(k===30)pause()}lab.querySelector('[data-next]').onclick=()=>{pause();k=Math.min(30,k+1);draw()};play.onclick=()=>{if(timer){pause();return}if(k===30)k=0;play.textContent='Pause';play.setAttribute('aria-pressed','true');timer=setInterval(()=>{k=Math.min(30,k+1);draw()},matchMedia('(prefers-reduced-motion: reduce)').matches?1800:900)};slider.oninput=()=>{pause();k=Number(slider.value);draw()};n.onchange=lab.querySelector('[data-reset]').onclick=()=>{pause();k=0;draw()};lab.closest('.book-section')?.addEventListener('slideleave',pause);document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});draw()});
 document.querySelectorAll('[data-lab="phase"]').forEach(lab=>{let stage=0;const select=lab.querySelector('[data-function]'),next=lab.querySelector('[data-next]');function draw(){const f=select.value.split(',').map(Number),signs=stage===0?[1,1]:f.map(v=>v?-1:1),out=[(signs[0]+signs[1])/2,(signs[0]-signs[1])/2];signs.forEach((s,i)=>{lab.querySelector(`[data-path="${i}"]`).classList.toggle('negative',s<0);lab.querySelector(`[data-sign="${i}"]`).textContent=(s<0?'−':'+')+'1/√2'});math(lab.querySelector('[data-state]'),stage<2?(stage===0?'Before oracle: both amplitudes are \\(+1/\\sqrt2\\).':`After oracle: \\(${signs[0]<0?'-':'+'}\\ket0/\\sqrt2 ${signs[1]<0?'-':'+'}\\ket1/\\sqrt2\\).`):`After \\(H\\): probability of 0 is ${percent(out[0]**2)}; probability of 1 is ${percent(out[1]**2)}.`);lab.querySelector('[data-status]').textContent=['Choose a function, then apply its oracle.','The branches show the phase after the oracle. Apply H to combine them.','Equal signs interfere into 0; opposite signs interfere into 1. The paths above show the oracle stage.'][stage];next.textContent=['Apply oracle','Apply final H','Experiment complete'][stage];next.disabled=stage===2;lab.dataset.result=stage===2?String(out[1]**2):''}next.onclick=()=>{stage=Math.min(2,stage+1);draw()};select.onchange=lab.querySelector('[data-reset]').onclick=()=>{stage=0;draw()};draw()});
 /* Animated figures. Each replaces a static drawing that stays in the page, hidden,
    for readers without scripting. Every frame is redrawn from the figure's state. */
 const NS='http://www.w3.org/2000/svg',DEG=Math.PI/180;
 const gcd=(a,b)=>b?gcd(b,a%b):a;
 const still=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
 function node(parent,tag,attrs={},text){const e=document.createElementNS(NS,tag);for(const k in attrs)e.setAttribute(k,attrs[k]);if(text!=null)e.textContent=text;parent.append(e);return e}
 function label(parent,x,y,text,attrs={}){return node(parent,'text',{x,y,'text-anchor':'middle',...attrs},text)}
 function arrow(parent,x1,y1,x2,y2,tint,width=2.5){const g=node(parent,'g',{class:tint}),dx=x2-x1,dy=y2-y1,l=Math.hypot(dx,dy);if(l<1)return g;const ux=dx/l,uy=dy/l,h=Math.min(11,l*.5);node(g,'path',{d:`M${x1} ${y1}L${x2-ux*h*.7} ${y2-uy*h*.7}`,class:'lf-line',style:`stroke-width:${width}`});node(g,'path',{d:`M${x2} ${y2}L${x2-h*ux+h*.42*uy} ${y2-h*uy-h*.42*ux}L${x2-h*ux-h*.42*uy} ${y2-h*uy+h*.42*ux}Z`,class:'lf-head'});return g}
 // Ease from 0 to 1 over ms, calling step(t); jump to the end when motion is reduced.
 function tween(ms,step,done){if(still()){step(1);done?.();return()=>{}}let start,id;const frame=now=>{start??=now;const t=Math.min(1,(now-start)/ms);step(t*t*(3-2*t));if(t<1)id=requestAnimationFrame(frame);else done?.()};id=requestAnimationFrame(frame);return()=>cancelAnimationFrame(id)}
 // Show the live controls and drawing in place of the static fallback.
 function stage(lab,width,height,name){lab.querySelector('.lab-fallback').hidden=true;lab.querySelectorAll('[data-live]').forEach(e=>e.hidden=false);return node(lab.querySelector('[data-stage]'),'svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':name})}
 // A Run button that calls tick() at a steady pace until tick() returns false.
 function runner(button,tick,ms){let timer=null;const stop=()=>{clearInterval(timer);timer=null;button.textContent='Run';button.setAttribute('aria-pressed','false')};button.onclick=()=>{if(timer)return stop();if(!tick())return;button.textContent='Pause';button.setAttribute('aria-pressed','true');timer=setInterval(()=>{if(!tick())stop()},still()?2*ms:ms)};document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});return stop}
 // Exact fractions for the dyadic weights used in the path figures.
 const frac=x=>{if(Math.abs(x)<1e-12)return'0';for(const d of [1,2,4,8,16,32]){const n=Math.round(x*d);if(Math.abs(n/d-x)<1e-9)return d===1?String(n):`${n}/${d}`}return fmt(x)};
 const minus=s=>s.replace(/-/g,'−');
 function bar(parent,x,y,width,p){node(parent,'rect',{x,y,width,height:14,rx:2,class:'lf-track'});node(parent,'rect',{x,y,width:width*p,height:14,rx:2,class:'lf-bar'})}

 document.querySelectorAll('[data-lab="euclid"]').forEach(lab=>{
  const [first,second]=lab.querySelectorAll('[data-entry]'),next=lab.querySelector('[data-next]'),row=46,top=58;
  const svg=stage(lab,530,top+row,'Euclid’s algorithm as a sequence of pairs');
  const read=input=>Math.max(0,Math.min(9999,Math.floor(Number(input.value)||0)));
  let pairs=[],shown=0;
  function draw(){
   const g=pairs.at(-1)[0],b0=Math.max(1,pairs[0][1]),last=pairs.length-1,[a,b]=pairs[shown];
   svg.setAttribute('viewBox',`0 0 530 ${top+pairs.length*row-14}`);svg.replaceChildren();
   [['pair (a, b)',80],['a = q·b + r',235],['gcd',360],['second entry',445]].forEach(([t,x])=>label(svg,x,22,t,{class:'lf-caption'}));
   pairs.slice(0,shown+1).forEach(([a,b],t)=>{
    const y=top+t*row,g2=node(svg,'g',t&&t===shown?{class:'lf-new'}:{});
    if(t)arrow(g2,80,y-row+16,80,y-16,'c-axis',1.6);
    node(g2,'rect',{x:20,y:y-15,width:120,height:30,rx:15,class:'lf-node'+(t===shown?' current':'')});
    label(g2,80,y+5,`(${a}, ${b})`);
    label(g2,235,y+5,b?`${a} = ${Math.floor(a/b)}·${b} + ${a%b}`:`b = 0: return ${a}`);
    label(g2,360,y+5,String(g),{class:'tint c-teal'});
    node(g2,'rect',{x:395,y:y-7,width:100*b/b0,height:14,rx:2,class:'lf-bar'});
    node(g2,'text',{x:401+100*b/b0,y:y+5},String(b));
   });
   lab.querySelector('[data-state]').textContent=!g?'gcd(0, 0) is not defined. Choose at least one positive entry.':shown===last?`Halted at (${g}, 0) after ${last} step${last===1?'':'s'}. The algorithm returns ${g}.`:`Step ${shown}: the pair is (${a}, ${b}). The gcd is still ${g}; the second entry has fallen from ${pairs[0][1]} to ${b}.`;
   next.disabled=shown===last;lab.dataset.result=shown===last&&g?String(g):'';lab.dataset.steps=String(shown);
  }
  const stop=runner(lab.querySelector('[data-run]'),()=>{const last=pairs.length-1;if(shown>=last){shown=0;draw();return true}shown++;draw();return shown<last},800);
  function reset(){stop();pairs=[[read(first),read(second)]];while(pairs.at(-1)[1]>0){const [a,b]=pairs.at(-1);pairs.push([b,a%b])}shown=0;draw()}
  next.onclick=()=>{stop();shown=Math.min(shown+1,pairs.length-1);draw()};
  first.onchange=second.onchange=lab.querySelector('[data-reset]').onclick=reset;reset();
 });

 document.querySelectorAll('[data-lab="turing"]').forEach(lab=>{
  const next=lab.querySelector('[data-next]'),W=600,R=28,svg=stage(lab,W,360,'A Turing machine: its tape and its control drawn as a state diagram');
  const int=(lo,hi)=>lo+Math.floor(Math.random()*(hi-lo+1)),pick=xs=>xs[int(0,xs.length-1)],word=(n,abc)=>Array.from({length:n},()=>pick(abc)).join(''),yes=ok=>ok?'accept':'reject',rev=w=>[...w].reverse().join('');
  const sym=s=>s==='_'?'□':s;
  // Problem families. Each call draws fresh parameters and input; rules are [state, read, write, move, next].
  const example=()=>({name:'Scan a block of ones',question:'Move right over the block of ones and halt at the first blank.',input:'111',halts:['halt'],rules:[['scan','1','1','R','scan'],['scan','_','_','S','halt']],check:(w,out)=>out===w});
  const families=[
   ()=>{const m=int(2,3),p=word(m,'01'),ids=[...Array(m).keys()].map(i=>i?'saw '+p.slice(0,i):'start'),rules=[];
    const fit=s=>{for(let k=Math.min(s.length,m);k>0;k--)if(s.endsWith(p.slice(0,k)))return k;return 0};
    ids.forEach((q,i)=>{for(const c of '01'){const k=fit(p.slice(0,i)+c);rules.push([q,c,c,'R',k===m?'accept':ids[k]])}rules.push([q,'_','_','S','reject'])});
    let w=word(int(5,8),'01');if(Math.random()<.5&&!w.includes(p)){const i=int(0,w.length-m);w=w.slice(0,i)+p+w.slice(i+m)}
    return{name:'Pattern search',question:`Does ${w} contain ${p}? The state “saw x” means the last symbols read match the beginning x of the pattern.`,input:w,halts:['accept','reject'],rules,check:(w,out,s)=>s===yes(w.includes(p))}},
   ()=>{const k=int(3,4),ids=[...Array(k).keys()].map(i=>'rem '+i),rules=[];
    ids.forEach((q,i)=>{for(const b of '01')rules.push([q,b,b,'R',ids[(2*i+Number(b))%k]]);rules.push([q,'_','_','S',i?'reject':'accept'])});
    const w=Math.random()<.5?(k*int(2,40)).toString(2):'1'+word(int(2,6),'01');
    return{name:`Divisibility by ${k}`,question:`Is ${w} (${parseInt(w,2)} in decimal) divisible by ${k}? The state “rem r” holds the remainder of the digits read so far: reading digit d turns r into 2r + d, reduced modulo ${k}.`,input:w,halts:['accept','reject'],rules,check:(w,out,s)=>s===yes(parseInt(w,2)%k===0)}},
   ()=>{const half=word(int(1,3),'ab'),w=Math.random()<.5?half+(Math.random()<.5?word(1,'ab'):'')+rev(half):word(int(2,6),'ab');
    const rules=[['start','a','_','R','have a'],['start','b','_','R','have b'],['start','_','_','S','accept']];
    for(const [c,d] of [['a','b'],['b','a']])rules.push([`have ${c}`,'a','a','R',`have ${c}`],[`have ${c}`,'b','b','R',`have ${c}`],[`have ${c}`,'_','_','L',`check ${c}`],[`check ${c}`,c,'_','L','back'],[`check ${c}`,d,d,'S','reject'],[`check ${c}`,'_','_','S','accept']);
    rules.push(['back','a','a','L','back'],['back','b','b','L','back'],['back','_','_','R','start']);
    return{name:'Palindromes',question:`Is ${w} a palindrome? The machine erases the first symbol, remembers it in its state, runs to the end, and compares it with the last symbol.`,input:w,halts:['accept','reject'],rules,check:(w,out,s)=>s===yes(w===rev(w))}},
   ()=>{const n=int(1,3),w=pick(['a'.repeat(n)+'b'.repeat(n),'a'.repeat(n)+'b'.repeat(n),'a'.repeat(n)+'b'.repeat(n+1),'a'.repeat(n+1)+'b'.repeat(n),'ab'.repeat(n+1),'b'+'a'.repeat(n)+'b']);
    const rules=[['mark a','a','X','R','find b'],['mark a','Y','Y','R','verify'],['mark a','b','b','S','reject'],['mark a','_','_','S','reject'],
     ['find b','a','a','R','find b'],['find b','Y','Y','R','find b'],['find b','b','Y','L','return'],['find b','_','_','S','reject'],
     ['return','a','a','L','return'],['return','Y','Y','L','return'],['return','X','X','R','mark a'],
     ['verify','Y','Y','R','verify'],['verify','_','_','S','accept'],['verify','a','a','S','reject'],['verify','b','b','S','reject']];
    return{name:'Matching counts',question:`Is ${w} a block of a’s followed by equally many b’s? Each round marks one a as X and one b as Y.`,input:w,halts:['accept','reject'],rules,check:(w,out,s)=>s===yes(/^a+b+$/.test(w)&&2*w.indexOf('b')===w.length)}},
   ()=>{let w='';if(Math.random()<.5){const n=int(1,3);let open=0,opened=0;while(w.length<2*n){if(opened<n&&(!open||Math.random()<.5)){w+='(';open++;opened++}else{w+=')';open--}}}else w=word(pick([2,3,4,5,6]),'()');
    const rules=[['right','(','(','R','right'],['right','X','X','R','right'],['right',')','X','L','left'],['right','_','_','L','check'],
     ['left','(','X','R','right'],['left','X','X','L','left'],['left','_','_','S','reject'],
     ['check','X','X','L','check'],['check','(','(','S','reject'],['check','_','_','S','accept']];
    const balanced=w=>{let d=0;for(const c of w){d+=c==='('?1:-1;if(d<0)return false}return d===0};
    return{name:'Balanced parentheses',question:`Are the parentheses in ${w} balanced? Each ) is crossed out together with the nearest uncrossed ( to its left.`,input:w,halts:['accept','reject'],rules,check:(w,out,s)=>s===yes(balanced(w))}},
   ()=>{const n=int(1,3),w='1'.repeat(n)+'#';
    const rules=[['mark','1','X','R','skip'],['mark','#','#','L','restore'],['skip','1','1','R','skip'],['skip','#','#','R','to end'],
     ['to end','1','1','R','to end'],['to end','_','1','L','back'],['back','1','1','L','back'],['back','#','#','L','seek X'],
     ['seek X','1','1','L','seek X'],['seek X','X','X','R','mark'],['restore','X','1','L','restore'],['restore','_','_','R','halt']];
    return{name:'Copying',question:`Copy the block of ${n} one${n>1?'s':''} to the right of #. Each 1 is marked X while its copy is written, then the marks are restored.`,input:w,halts:['halt'],rules,check:(w,out)=>out===w+'1'.repeat(n)}},
   ()=>{const w='1'+word(int(1,4),'01')+(Math.random()<.5?'11':'');
    const rules=[['right','0','0','R','right'],['right','1','1','R','right'],['right','_','_','L','carry'],['carry','1','0','L','carry'],['carry','0','1','S','halt'],['carry','_','1','S','halt']];
    return{name:'Binary increment',question:`What is ${w} + 1 in binary? (${w} is ${parseInt(w,2)} in decimal.) The machine finds the last digit, then carries to the left.`,input:w,halts:['halt'],rules,check:(w,out)=>parseInt(out,2)===parseInt(w,2)+1}},
   ()=>{const a=int(1,3),b=int(1,3),w='1'.repeat(a)+'+'+'1'.repeat(b);
    const rules=[['first','1','1','R','first'],['first','+','1','R','second'],['second','1','1','R','second'],['second','_','_','L','last'],['last','1','_','S','halt']];
    return{name:'Unary addition',question:`Compute ${a} + ${b}, written in unary as ${w}. The machine replaces + by 1 and erases the last 1.`,input:w,halts:['halt'],rules,check:(w,out)=>out==='1'.repeat(a+b)}},
  ];
  const lines=rules=>rules.length>1&&rules.every(r=>r[1]===r[2]&&r[3]===rules[0][3])?[`${rules.map(r=>sym(r[1])).join(', ')} → same, ${rules[0][3]}`]:rules.map(r=>`${sym(r[1])} → ${sym(r[2])}, ${r[3]}`);
  // Geometry of every arrow and its label for given state positions. Labels sit on their arrows.
  function geometry(m,at){
   const groups=new Map;m.rules.forEach(r=>{const k=r[0]+'|'+r[4];groups.set(k,[...(groups.get(k)||[]),r])});
   return[...groups].map(([k,rules])=>{
    const [from,to]=k.split('|'),[x1,y1,side]=at[from],[x2,y2]=at[to],texts=lines(rules),w=Math.max(...texts.map(t=>t.length))*7+10,h=texts.length*16;
    if(from===to)return{from,to,rules,texts,loop:side,label:{x:x1,y:y1+side*(R+54+h/2),w,h}};
    const dx=x2-x1,dy=y2-y1,l=Math.hypot(dx,dy),ux=dx/l,uy=dy/l,nx=uy,ny=-ux,bend=groups.has(to+'|'+from)?24:0;
    return{from,to,rules,texts,ux,uy,nx,ny,bend,l,label:{x:(x1+x2)/2+nx*bend*1.2,y:(y1+y2)/2+ny*bend*1.2,w,h}};
   });
  }
  // Place states on a grid, searching for positions where arrows avoid other states and labels do not collide.
  function arrange(m){
   const ids=[...new Set(m.rules.flatMap(r=>[r[0],r[4]]))],start=m.rules[0][0],loops=new Set(m.rules.filter(r=>r[0]===r[4]).map(r=>r[0]));
   const cols=5,rows=3,X=c=>70+c*115,Y=r=>190+r*125;
   const gap=([x,y],[x1,y1],[x2,y2])=>{const dx=x2-x1,dy=y2-y1,t=Math.max(0,Math.min(1,((x-x1)*dx+(y-y1)*dy)/(dx*dx+dy*dy)));return Math.hypot(x-x1-t*dx,y-y1-t*dy)};
   const cross=(a,b,c,d)=>{const o=(p,q,r)=>Math.sign((q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]));return o(a,b,c)*o(a,b,d)<0&&o(c,d,a)*o(c,d,b)<0};
   const overlap=(a,b,pad=4)=>Math.abs(a.x-b.x)<(a.w+b.w)/2+pad&&Math.abs(a.y-b.y)<(a.h+b.h)/2+pad;
   const place=pos=>{const bottom=Math.max(...ids.map(q=>pos[q][1]));return Object.fromEntries(ids.map(q=>[q,[X(pos[q][0]),Y(pos[q][1]),pos[q][1]===0?-1:1]]))};
   function cost(pos){
    const bottom=Math.max(...ids.map(q=>pos[q][1])),at=place(pos),edges=geometry(m,at);let c=bottom*40+(pos[start][0]?400:0)+(ids.some(q=>q!==start&&pos[q][0]===0&&pos[q][1]===pos[start][1])?400:0);
    ids.forEach(q=>{if(loops.has(q)&&pos[q][1]&&pos[q][1]!==bottom)c+=600;if(m.halts.includes(q))c+=(cols-1-pos[q][0])*3});
    const straight=edges.filter(e=>!e.loop);
    straight.forEach(e=>{const p=at[e.from],q=at[e.to];c+=e.l/25+(e.l>260?150:0);ids.forEach(o=>{if(o!==e.from&&o!==e.to&&gap(at[o],p,q)<R+18)c+=500})});
    straight.forEach((s,i)=>straight.slice(i+1).forEach(t=>{if(![t.from,t.to].some(x=>x===s.from||x===s.to)&&cross(at[s.from],at[s.to],at[t.from],at[t.to]))c+=40}));
    const boxes=edges.map(e=>e.label),nodes=ids.map(q=>({x:at[q][0],y:at[q][1],w:2*R,h:2*R}));
    boxes.forEach((b,i)=>{boxes.slice(i+1).forEach(o=>{if(overlap(b,o))c+=120});nodes.forEach(n=>{if(overlap(b,n,2))c+=250})});
    return c}
   let best,bestCost=Infinity;
   for(let restart=0;restart<(ids.length>6?16:8);restart++){
    const free=[...Array(cols*rows).keys()].sort(()=>Math.random()-.5);let pos=Object.fromEntries(ids.map((q,i)=>[q,[free[i]%cols,Math.floor(free[i]/cols)]])),c=cost(pos);
    for(let it=0;it<1200;it++){const q=pick(ids),slot=[int(0,cols-1),int(0,rows-1)],other=ids.find(o=>pos[o][0]===slot[0]&&pos[o][1]===slot[1]),trial={...pos,[q]:slot};if(other)trial[other]=pos[q];const tc=cost(trial);if(tc<=c){pos=trial;c=tc}}
    if(c<bestCost){best=pos;bestCost=c}
   }
   const at=place(best),xs=ids.map(q=>at[q][0]),shift=(W-Math.max(...xs)-Math.min(...xs))/2;ids.forEach(q=>at[q][0]+=shift);
   const edges=geometry(m,at),height=Math.max(...ids.map(q=>at[q][1]+R),...edges.map(e=>e.label.y+e.label.h/2))+16;
   return{at,edges,height};
  }
  let machine,layout,input,tape,head,at,state,steps,rule,visited,offset,cancel=()=>{};
  function curve(x0,y0,x1,y1,x2,y2,x3,y3,tint,width){const g=node(svg,'g',{class:tint});node(g,'path',{d:`M${x0} ${y0}C${x1} ${y1} ${x2} ${y2} ${x3} ${y3}`,class:'lf-line',style:`stroke-width:${width}`});const dx=x3-x2,dy=y3-y2,l=Math.hypot(dx,dy),ux=dx/l,uy=dy/l,h=10;node(g,'path',{d:`M${x3} ${y3}L${x3-h*ux+h*.42*uy} ${y3-h*uy-h*.42*ux}L${x3-h*ux-h*.42*uy} ${y3-h*uy+h*.42*ux}Z`,class:'lf-head'})}
  function diagram(){
   const pos=layout.at,[sx,sy]=pos[machine.rules[0][0]];arrow(svg,sx-R-34,sy,sx-R-2,sy,'c-axis',1.6);
   layout.edges.forEach(e=>{
    const [x1,y1]=pos[e.from],[x2,y2]=pos[e.to],used=e.rules.includes(rule),tint=used?'c-neg':'c-state',w=used?2.8:1.5,s=e.loop;
    if(s)curve(x1-14,y1+s*(R-4),x1-46,y1+s*(R+60),x1+46,y1+s*(R+60),x1+14,y1+s*(R-4),tint,w);
    else if(e.bend){const {ux,uy,nx,ny,bend,l}=e,mx=(x1+x2)/2+nx*bend*1.6,my=(y1+y2)/2+ny*bend*1.6;curve(x1+ux*R+nx*10,y1+uy*R+ny*10,mx-ux*l/4,my-uy*l/4,mx+ux*l/4,my+uy*l/4,x2-ux*R+nx*10,y2-uy*R+ny*10,tint,w)}
    else arrow(svg,x1+e.ux*R,y1+e.uy*R,x2-e.ux*(R+2),y2-e.uy*(R+2),tint,w);
   });
   layout.edges.forEach(e=>{const {x,y,w,h}=e.label,used=e.rules.includes(rule);node(svg,'rect',{x:x-w/2,y:y-h/2,width:w,height:h,rx:3,class:'lf-tag'+(used?' used':'')});e.texts.forEach((t,i)=>label(svg,x,y-h/2+12+i*16,t,{class:'lf-caption'+(used?' tint c-neg':'')}))});
   Object.entries(pos).forEach(([q,[x,y]])=>{node(svg,'circle',{cx:x,cy:y,r:R,class:'lf-node'+(q===state?' current':'')});if(machine.halts.includes(q))node(svg,'circle',{cx:x,cy:y,r:R-5,class:'lf-node'+(q===state?' current':'')});label(svg,x,y+4,q,{style:'font-size:12px'})});
  }
  function draw(){
   const w=40,x0=(W-tape.length*w)/2,hx=x0+at*w+w/2;svg.replaceChildren();svg.setAttribute('viewBox',`0 0 ${W} ${layout.height}`);
   tape.forEach((s,i)=>{node(svg,'rect',{x:x0+i*w,y:14,width:w,height:w,class:'lf-cell'+(visited.has(i-offset)?' visited':'')});label(svg,x0+i*w+w/2,40,s==='_'?'':s)});
   node(svg,'path',{d:`M${hx} 60l-8 13h16z`,class:'lf-pointer'});
   diagram();
   const halted=machine.halts.includes(state),out=tape.join('').replace(/^_+|_+$/g,''),config=tape.map((s,i)=>i===head?`[${sym(s)}]`:sym(s)).join(' '),decides=machine.halts.includes('accept');
   lab.querySelector('[data-encoding]').textContent='The same rules as data: '+machine.rules.map(r=>r.join(',')).join(';');
   lab.querySelector('[data-status]').textContent=`${machine.name}. ${machine.question}`;
   lab.querySelector('[data-state]').textContent=halted?`Halted in state ${state} after ${steps} step${steps===1?'':'s'}. `+(decides?`The answer is ${state==='accept'?'yes':'no'}.`:`The tape now reads ${out||'(blank)'}.`):`Step ${steps}. State ${state}, reading ${sym(tape[head])}. Tape: ${config}`;
   next.disabled=halted;lab.dataset.steps=String(steps);lab.dataset.halted=String(halted);lab.dataset.correct=halted?String(machine.check(input,out,state)):'';
  }
  function step(){
   if(machine.halts.includes(state))return false;
   rule=machine.rules.find(r=>r[0]===state&&r[1]===tape[head]);tape[head]=rule[2];state=rule[4];steps++;
   const move=rule[3]==='R'?1:rule[3]==='L'?-1:0;
   if(head+move<0){tape.unshift('_');head++;offset++}if(head+move>=tape.length)tape.push('_');
   const from=head;head+=move;visited.add(head-offset);at=from;
   cancel=move?tween(300,t=>{at=from+move*t;draw()}):()=>{};if(!move)at=head;draw();
   return !machine.halts.includes(state);
  }
  function restart(){stop();cancel();input=machine.input;tape=['_',...input,'_'];head=at=1;offset=0;state=machine.rules[0][0];steps=0;rule=null;visited=new Set([1]);draw()}
  function load(m){machine=m;layout=arrange(m);restart()}
  const stop=runner(lab.querySelector('[data-run]'),()=>{if(machine.halts.includes(state)){restart();return true}return step()},550);
  let last=-1;
  next.onclick=()=>{stop();step()};
  lab.querySelector('[data-reset]').onclick=restart;
  lab.querySelector('[data-new]').onclick=()=>{let i;do i=int(0,families.length-1);while(i===last);last=i;load(families[i]())};
  lab.querySelector('[data-example]').onclick=()=>{last=-1;load(example())};
  load(example());
 });

 document.querySelectorAll('[data-lab="cancel"]').forEach(lab=>{
  const slider=lab.querySelector('[data-weight]'),both=lab.querySelector('[data-second]'),svg=stage(lab,520,352,'Two paths from i to k and their signed contributions');
  const at={i:[50,115],j1:[230,45],j2:[230,185],k:[410,115]},X=v=>40+(v+.5)/1.5*440;
  function edge(u,v,text,amount,tint,dashed,dim){const [x1,y1]=at[u],[x2,y2]=at[v],l=Math.hypot(x2-x1,y2-y1),ux=(x2-x1)/l,uy=(y2-y1)/l,g=arrow(svg,x1+24*ux,y1+24*uy,x2-26*ux,y2-26*uy,tint,1.5+14*Math.abs(amount));if(dashed)g.classList.add('lf-dash');if(dim)g.classList.add('lf-dim');const mx=(x1+x2)/2-230,my=(y1+y2)/2-115,m=Math.hypot(mx,my);label(svg,230+mx*(1+30/m),115+my*(1+30/m)+5,text,{class:dim?'lf-dim':''})}
  function draw(){
   const a=.5,b=.5,c=.5,d=Number(slider.value)/8,on=both.checked,p1=c*a,p2=on?d*b:0,total=p1+p2,tint=d<0?'c-neg':'c-teal';
   svg.replaceChildren();
   edge('i','j1','a = 1/2',p1,'c-teal');edge('j1','k','c = 1/2',p1,'c-teal');
   edge('i','j2','b = 1/2',on?d*b:0,tint,d<0,!on);edge('j2','k',minus(`d = ${frac(d)}`),on?d*b:0,tint,d<0,!on);
   [['i','i'],['j1','j₁'],['j2','j₂'],['k','k']].forEach(([id,name])=>{node(svg,'circle',{cx:at[id][0],cy:at[id][1],r:23,class:'lf-node'+(id==='j2'&&!on?' lf-dim':'')});label(svg,at[id][0],at[id][1]+6,name)});
   node(svg,'path',{d:`M${X(-.5)} 310H${X(1)}`,class:'lf-thin c-axis'});
   [-.5,-.25,0,.25,.5,.75,1].forEach(v=>{node(svg,'path',{d:`M${X(v)} 304V316`,class:'lf-thin c-axis'});label(svg,X(v),336,minus(frac(v)),{class:'lf-caption'})});
   arrow(svg,X(0),262,X(p1),262,'c-teal',4);label(svg,(X(0)+X(p1))/2,252,'ca',{class:'tint c-teal'});
   if(p2){arrow(svg,X(p1),282,X(total),282,tint,4);label(svg,(X(p1)+X(total))/2,300,'db',{class:`tint ${tint}`})}
   node(svg,'path',{d:`M${X(total)} 308l-7 -14h14z`,class:'lf-pointer'});
   math(lab.querySelector('[data-state]'),`\\(ca=${frac(p1)}\\), \\(db=${frac(p2)}\\), \\(W(i\\to k)=${frac(total)}\\).`);
   lab.querySelector('[data-d]').textContent=minus(frac(d));
   lab.querySelector('[data-status]').textContent=!on?'With the second path removed, only ca remains.'+(d<0?' Removing a negative contribution increased the total.':''):!d?'The second path contributes nothing.':!total?'Complete cancellation: both paths have nonzero weight, yet their contributions sum to zero.':p2<0?(total<0?'The negative contribution outweighs ca, so the total is negative.':'Partial cancellation: the negative contribution lowers the total below ca.'):'Both contributions are positive, so they reinforce.';
   lab.dataset.total=String(total);
  }
  slider.oninput=both.onchange=draw;lab.querySelector('[data-reset]').onclick=()=>{slider.value=-4;both.checked=true;draw()};draw();
 });

 document.querySelectorAll('[data-lab="interference"]').forEach(lab=>{
  const rel=lab.querySelector('[data-relative]'),glob=lab.querySelector('[data-global]'),svg=stage(lab,520,318,'Amplitudes arriving at 0 and at 1 after a Hadamard step');
  const piText=k=>{k=(k%24+24)%24;if(!k)return'0';const g=gcd(k,12),n=k/g,d=12/g;return`${n===1?'':n}\\pi${d===1?'':'/'+d}`};
  let phi=0,cancel=()=>{};
  function plane(cx,name,sign,theta){
   const R=96,cy=142,pt=([x,y])=>[cx+R*x,cy-R*y],u=[Math.cos(theta)/2,Math.sin(theta)/2],w=[sign*Math.cos(theta+phi)/2,sign*Math.sin(theta+phi)/2],s=[u[0]+w[0],u[1]+w[1]],p=s[0]**2+s[1]**2;
   label(svg,cx,22,name,{class:'lf-caption'});
   node(svg,'circle',{cx,cy,r:R,class:'lf-ring'});node(svg,'path',{d:`M${cx-R-8} ${cy}H${cx+R+8}M${cx} ${cy-R-8}V${cy+R+8}`,class:'lf-thin c-axis'});
   arrow(svg,cx,cy,...pt(s),'c-state',4.5);arrow(svg,cx,cy,...pt(u),'c-teal');arrow(svg,...pt(u),...pt(s),'c-neg');
   bar(svg,cx-R,262,2*R,p);label(svg,cx,298,`probability ${fmt(p)}`);return p}
  function draw(){
   const theta=Number(glob.value)*Math.PI/12;svg.replaceChildren();
   const p0=plane(130,'Arriving at 0',1,theta),p1=plane(390,'Arriving at 1',-1,theta),k=Number(rel.value);
   math(lab.querySelector('[data-state]'),`\\(\\phi=${piText(k)}\\): \\(p(0)=\\tfrac{1+\\cos\\phi}{2}=${fmt(p0)}\\) and \\(p(1)=${fmt(p1)}\\). Before \\(H\\), both were \\(1/2\\).`);
   math(lab.querySelector('[data-phi-out]'),`\\(${piText(k)}\\)`);math(lab.querySelector('[data-theta-out]'),`\\(${piText(Number(glob.value))}\\)`);
   lab.querySelector('[data-status]').textContent=(Math.abs(p0-p1)<1e-9?'Neither endpoint is favored: the probabilities are equal.':p0>p1?'Constructive at 0, destructive at 1.':'Destructive at 0, constructive at 1.')+(Number(glob.value)%24?' The global phase turns every arrow together, so the lengths of the sums, and the probabilities, do not change.':'');
   lab.dataset.p0=String(p0);
  }
  rel.oninput=glob.oninput=()=>{cancel();phi=Number(rel.value)*Math.PI/12;draw()};
  lab.querySelector('[data-z]').onclick=()=>{cancel();const from=Number(rel.value)*Math.PI/12;rel.value=(Number(rel.value)+12)%24;cancel=tween(700,t=>{phi=from+t*Math.PI;draw()},()=>{phi=Number(rel.value)*Math.PI/12;draw()})};
  lab.querySelector('[data-reset]').onclick=()=>{rel.value=0;glob.value=0;rel.oninput()};rel.oninput();
 });

 document.querySelectorAll('[data-lab="inner"]').forEach(lab=>{
  const psiIn=lab.querySelector('[data-psi]'),phiIn=lab.querySelector('[data-phi]'),svg=stage(lab,520,312,'The component of the initial state along the final state');
  function draw(){
   const a=psiIn.value*DEG,b=phiIn.value*DEG,amp=Math.cos(a-b),cx=160,cy=156,R=118,pt=(x,y)=>[cx+R*x,cy-R*y],foot=[amp*Math.cos(b),amp*Math.sin(b)];
   let theta=((psiIn.value-phiIn.value)%360+360)%360;if(theta>180)theta=360-theta;
   svg.replaceChildren();
   node(svg,'circle',{cx,cy,r:R,class:'lf-ring'});
   node(svg,'path',{d:`M${pt(-1.25*Math.cos(b),-1.25*Math.sin(b))}L${pt(1.25*Math.cos(b),1.25*Math.sin(b))}`,class:'lf-thin lf-dash c-teal'});
   node(svg,'path',{d:`M${pt(Math.cos(a),Math.sin(a))}L${pt(...foot)}`,class:'lf-thin lf-dash c-axis'});
   arrow(svg,cx,cy,...pt(Math.cos(b),Math.sin(b)),'c-teal');arrow(svg,cx,cy,...pt(Math.cos(a),Math.sin(a)),'c-state',3);arrow(svg,cx,cy,...pt(...foot),'c-neg',5);
   label(svg,...pt(1.17*Math.cos(a),1.17*Math.sin(a)+.04),'|ψ⟩',{class:'tint c-state'});label(svg,...pt(1.17*Math.cos(b),1.17*Math.sin(b)+.04),'|φ⟩',{class:'tint c-teal'});
   [[`angle between: ${theta}°`,60],[`⟨φ|ψ⟩ = cos θ = ${minus(fmt(amp))}`,100],[`|⟨φ|ψ⟩|² = ${fmt(amp*amp)}`,140]].forEach(([t,y])=>node(svg,'text',{x:320,y},t));
   bar(svg,320,156,180,amp*amp);node(svg,'text',{x:320,y:200,class:'lf-caption'},'probability of the outcome φ');
   math(lab.querySelector('[data-state]'),`\\(\\braket\\phi\\psi=${fmt(amp)}\\) and \\(|\\braket\\phi\\psi|^2=${fmt(amp*amp)}\\).`);
   lab.querySelector('[data-status]').textContent=Math.abs(amp)<1e-9?'The states are orthogonal: the component along |φ⟩ is zero, and so is the probability.':amp<0?'The amplitude is negative: the component points against |φ⟩, but its square is still a probability.':Math.abs(amp-1)<1e-9?'The states coincide: the component is the whole vector.':'The orange component is the part of |ψ⟩ along |φ⟩; the dashed segment is the orthogonal remainder.';
   lab.dataset.amplitude=String(amp);
  }
  psiIn.oninput=phiIn.oninput=draw;lab.querySelector('[data-reset]').onclick=()=>{psiIn.value=30;phiIn.value=0;draw()};draw();
 });

 document.querySelectorAll('[data-lab="measure"]').forEach(lab=>{
  const angle=lab.querySelector('[data-angle]'),svg=stage(lab,520,300,'A state, its projections onto the basis directions, and outcome counts');
  let psi,state,shown,outcome,counts,cancel=()=>{};
  const sample=v=>Math.random()<v[0]**2?0:1;
  function draw(){
   const R=190,ox=58,oy=258,pt=(x,y)=>[ox+R*x,oy-R*y],[x,y]=shown,total=counts[0]+counts[1];svg.replaceChildren();
   node(svg,'path',{d:`M${pt(1,0)}A${R} ${R} 0 0 0 ${pt(0,1)}`,class:'lf-ring'});
   arrow(svg,ox,oy,...pt(1.12,0),'c-axis',1.5);arrow(svg,ox,oy,...pt(0,1.12),'c-axis',1.5);
   label(svg,...pt(1.12,-.1),'|0⟩');label(svg,ox-24,oy-R*1.06,'|1⟩');
   node(svg,'path',{d:`M${pt(x,y)}L${pt(x,0)}M${pt(x,y)}L${pt(0,y)}`,class:'lf-thin lf-dash c-axis'});
   arrow(svg,ox,oy,...pt(x,0),'c-teal',5);arrow(svg,ox,oy,...pt(0,y),'c-neg',5);arrow(svg,ox,oy,...pt(x,y),'c-state',3);
   if(x>.08)label(svg,...pt(x/2,-.09),fmt(x),{class:'tint c-teal'});if(y>.08)node(svg,'text',{x:ox+8,y:oy-R*y/2+5,class:'tint c-neg'},fmt(y));
   node(svg,'text',{x:330,y:26,class:'lf-caption'},`Fresh copies measured: ${total}`);
   [0,1].forEach(j=>{const bx=345+j*90,p=psi[j]**2,f=total?counts[j]/total:0;node(svg,'rect',{x:bx,y:70,width:56,height:170,class:'lf-track'});node(svg,'rect',{x:bx,y:240-170*f,width:56,height:170*f,class:j?'lf-bar c-neg':'lf-bar c-teal',style:'fill:currentColor'});node(svg,'path',{d:`M${bx-6} ${240-170*p}H${bx+62}`,class:'lf-thin lf-dash c-state'});label(svg,bx+28,262,`outcome ${j}`);label(svg,bx+28,284,total?`${counts[j]}`:'—',{class:'lf-caption'})});
   math(lab.querySelector('[data-state]'),outcome===null?`\\(\\ket\\psi=${fmt(psi[0])}\\ket0+${fmt(psi[1])}\\ket1\\): \\(p(0)=${fmt(psi[0]**2)}\\), \\(p(1)=${fmt(psi[1]**2)}\\).`:`Last outcome ${outcome}; the system is now in \\(\\ket{${outcome}}\\).`);
   lab.dataset.counts=JSON.stringify(counts);lab.dataset.outcome=outcome??'';
  }
  function animate(to){cancel();const from=[...shown],proj=to[0]?[from[0],0]:[0,from[1]];state=to;cancel=tween(800,t=>{shown=t<.5?from.map((v,i)=>v+(proj[i]-v)*2*t):proj.map((v,i)=>v+(to[i]-v)*(2*t-1));draw()},()=>{shown=to;draw()})}
  function prepare(clear){cancel();psi=[Math.cos(angle.value*DEG),Math.sin(angle.value*DEG)];state=[...psi];shown=[...psi];outcome=null;if(clear)counts=[0,0];draw()}
  lab.querySelector('[data-measure]').onclick=()=>{const fresh=outcome===null,j=sample(state),repeat=!fresh;outcome=j;if(fresh)counts[j]++;lab.dataset.outcome=j;lab.dataset.counts=JSON.stringify(counts);animate(j?[0,1]:[1,0]);lab.querySelector('[data-status]').textContent=repeat?`Outcome ${j} again. The system was already in |${j}⟩, so the result is certain; this run is not counted as a fresh copy.`:`Outcome ${j}. Only the ${j?'orange':'teal'} component is kept and normalized. Measure again to test the same system, or prepare a fresh copy.`};
  lab.querySelector('[data-batch]').onclick=()=>{for(let n=0;n<100;n++)counts[sample(psi)]++;draw();const total=counts[0]+counts[1];lab.querySelector('[data-status]').textContent=`${total} fresh copies: ${counts[0]} gave 0 (${percent(counts[0]/total)}) and ${counts[1]} gave 1 (${percent(counts[1]/total)}). The dashed lines mark the predicted fractions.`};
  lab.querySelector('[data-fresh]').onclick=()=>{prepare(false);lab.querySelector('[data-status]').textContent='A fresh copy of the state is ready. Its outcome is not yet determined.'};
  angle.oninput=lab.querySelector('[data-reset]').onclick=()=>{prepare(true);lab.querySelector('[data-status]').textContent='Measure the system, then measure it again, or measure many fresh copies.'};
  angle.oninput();
 });

 document.querySelectorAll('[data-lab="reflect"]').forEach(lab=>{
  const size=lab.querySelector('[data-size]'),svg=stage(lab,520,330,'A Grover iteration as two reflections in the plane of the bad and good directions');
  let theta,state,shown,trail,ops,mirror,cancel=()=>{};
  const angleOf=v=>Math.atan2(v[1],v[0])/DEG;
  function draw(){
   const cx=260,cy=170,R=128,pt=(x,y)=>[cx+R*x,cy-R*y],[x,y]=shown,s=[Math.cos(theta),Math.sin(theta)];svg.replaceChildren();
   node(svg,'circle',{cx,cy,r:R,class:'lf-ring'});
   node(svg,'path',{d:`M${pt(-1.2,0)}L${pt(1.2,0)}`,class:'lf-thin '+(mirror===0?'lf-mirror c-neg':'c-axis')});node(svg,'path',{d:`M${pt(0,-1.2)}L${pt(0,1.2)}`,class:'lf-thin c-axis'});
   node(svg,'path',{d:`M${pt(-1.2*s[0],-1.2*s[1])}L${pt(1.2*s[0],1.2*s[1])}`,class:'lf-thin lf-dash '+(mirror===theta?'lf-mirror c-neg':'c-teal')});
   label(svg,...pt(1.3,-.03),'|B⟩');label(svg,...pt(0,1.26),'|G⟩');label(svg,...pt(1.3*s[0],1.3*s[1]-.03),'|s⟩',{class:'tint c-teal'});
   trail.forEach(v=>arrow(svg,cx,cy,...pt(...v),'c-faint',2));
   arrow(svg,cx,cy,...pt(x,y),'c-state',3.5);
   const a=angleOf(state),p=state[1]**2;
   math(lab.querySelector('[data-state]'),`Angle from \\(\\ket B\\): \\(${a.toFixed(1)}^\\circ\\). Success probability \\(\\sin^2=${fmt(p)}\\).`);
   lab.dataset.angle=String(a);
  }
  function status(){const n=ops.length,last=ops.slice(-2).join(' ');math(lab.querySelector('[data-status]'),!n?`The state starts at \\(\\theta=${(theta/DEG).toFixed(1)}^\\circ\\) from the bad axis.`:(n>1&&ops[n-1]===ops[n-2]?'Reflecting twice across the same mirror undoes the first reflection. ':last==='O_f D'?`The pair \\(O_f\\) then \\(D\\) has turned the state by \\(2\\theta=${(2*theta/DEG).toFixed(1)}^\\circ\\) toward \\(\\ket G\\). `:'')+'Applied: \\('+ops.join('\\to ')+'\\).')}
  function reflect(axis,name,done){cancel();const c=Math.cos(2*axis),s=Math.sin(2*axis),from=[...shown],to=[c*state[0]+s*state[1],s*state[0]-c*state[1]];trail.push([...state]);if(trail.length>6)trail.shift();state=to;ops.push(name);mirror=axis;status();lab.dataset.angle=String(angleOf(to));cancel=tween(650,t=>{shown=from.map((v,i)=>v+(to[i]-v)*t);draw()},()=>{shown=to;draw();done?.()})}
  function reset(){cancel();theta=Math.asin(1/Math.sqrt(Number(size.value)));state=[Math.cos(theta),Math.sin(theta)];shown=[...state];trail=[];ops=[];mirror=null;status();draw()}
  lab.querySelector('[data-oracle]').onclick=()=>reflect(0,'O_f');lab.querySelector('[data-diffuse]').onclick=()=>reflect(theta,'D');
  lab.querySelector('[data-iterate]').onclick=()=>reflect(0,'O_f',()=>reflect(theta,'D'));
  size.onchange=lab.querySelector('[data-reset]').onclick=reset;reset();
 });
 document.querySelectorAll('[data-lab="proofs"]').forEach(lab=>{
  const svg=stage(lab,720,320,'A proof drawn as a network of justified steps'),list=lab.querySelector('[data-steps]'),check=lab.querySelector('[data-check]');
  // A formula is a letter or an implication {a, b}, read "a implies b".
  const text=(f,top=true)=>typeof f==='string'?f:(top?'':'(')+`${text(f.a,false)} implies ${text(f.b,false)}`+(top?'':')');
  const pick=xs=>xs[Math.floor(Math.random()*xs.length)];
  const example=[{f:'P',rule:'axiom'},{f:{a:'P',b:'Q'},rule:'axiom'},{f:'Q',rule:'mp',from:[0,1]},{f:{a:'Q',b:'R'},rule:'axiom'},{f:'R',rule:'mp',from:[2,3]}];
  let steps,layout,checking=-1,timer=null;
  // The checker trusts only axioms; every other line must follow from two earlier lines by modus ponens.
  function verify(steps){return steps.every((s,i)=>s.rule==='axiom'||s.from.every(j=>j<i)&&(([x,imp])=>typeof imp!=='string'&&text(imp.a)===text(x)&&text(imp.b)===text(s.f))(s.from.map(j=>steps[j].f)))}
  function generate(){
   const letters=['P','Q','R','S','T','U','V','W'],out=[],facts=[];let used=0;
   const add=(f,rule,from)=>{const i=out.findIndex(s=>text(s.f)===text(f));if(i>=0)return i;out.push(from?{f,rule,from}:{f,rule});return out.length-1};
   facts.push(add(letters[used++],'axiom'));if(Math.random()<.6)facts.push(add(letters[used++],'axiom'));
   for(let inferences=0,goal=3+Math.floor(Math.random()*3);inferences<goal&&used<letters.length;){
    const recent=facts.slice(-3),x=pick(recent),others=facts.filter(i=>i!==x);
    if(others.length&&Math.random()<.45){const z=pick(others),w=letters[used++],imp=add({a:out[x].f,b:{a:out[z].f,b:w}},'axiom'),mid=add({a:out[z].f,b:w},'mp',[x,imp]);facts.push(add(w,'mp',[z,mid]));inferences+=2}
    else{const y=letters[used++],imp=add({a:out[x].f,b:y},'axiom');facts.push(add(y,'mp',[x,imp]));inferences++}
   }
   // Keep only the lines the final conclusion depends on, in their original order.
   const keep=new Set,visit=i=>{if(keep.has(i))return;keep.add(i);out[i].from?.forEach(visit)};visit(out.length-1);
   const order=[...keep].sort((a,b)=>a-b),renumber=new Map(order.map((i,n)=>[i,n]));
   // Rename the surviving letters P, Q, R, ... in order of first appearance.
   const names=new Map,rename=f=>typeof f==='string'?(names.has(f)||names.set(f,letters[names.size]),names.get(f)):{a:rename(f.a),b:rename(f.b)};
   return order.map(i=>({...out[i],f:rename(out[i].f),...(out[i].from?{from:out[i].from.map(j=>renumber.get(j))}:{})}));
  }
  // Layers: a derived line sits one row below its deepest derived premise; an axiom sits just above its first use.
  function arrange(steps){
   const users=steps.map((_,i)=>steps.flatMap((s,j)=>s.from?.includes(i)?[j]:[])),level=[];
   steps.forEach((s,i)=>{if(s.rule==='mp')level[i]=1+Math.max(0,...s.from.filter(j=>steps[j].rule==='mp').map(j=>level[j]))});
   steps.forEach((s,i)=>{if(s.rule==='axiom')level[i]=Math.min(...users[i].map(j=>level[j]))-1});
   const rows=[];steps.forEach((s,i)=>(rows[level[i]]??=[]).push(i));
   const width=i=>text(steps[i].f).length*8.6+34,x=[];
   const place=row=>{let total=row.reduce((t,i)=>t+width(i),0)+28*(row.length-1),left=360-total/2;row.forEach(i=>{x[i]=left+width(i)/2;left+=width(i)+28});return total};
   if(rows.some(row=>!row||place(row)>700))return null;
   const near=i=>[...(steps[i].from||[]),...users[i]];
   for(let sweep=0;sweep<8;sweep++)rows.forEach(row=>{row.sort((a,b)=>near(a).reduce((t,j)=>t+x[j],0)/near(a).length-near(b).reduce((t,j)=>t+x[j],0)/near(b).length);place(row)});
   const y=i=>58+level[i]*78,edges=[];
   steps.forEach((s,i)=>s.from?.slice().sort((a,b)=>x[a]-x[b]).forEach((j,n)=>edges.push({from:j,to:i,x1:x[j],y1:y(j)+19,x2:x[i]+(n-.5)*26,y2:y(i)-21})));
   // Reject drawings in which an arrow passes through a box it does not join.
   const hits=edges.some(e=>steps.some((_,k)=>k!==e.from&&k!==e.to&&[...Array(21)].some((_,t)=>{const px=e.x1+(e.x2-e.x1)*t/20,py=e.y1+(e.y2-e.y1)*t/20;return Math.abs(px-x[k])<width(k)/2+6&&Math.abs(py-y(k))<26})));
   return hits?null:{x,y,width,edges,height:Math.max(...steps.map((_,i)=>y(i)))+40};
  }
  function draw(){
   svg.setAttribute('viewBox',`0 0 720 ${layout.height}`);svg.replaceChildren();
   const now=steps[checking],last=steps.length-1;
   layout.edges.forEach(e=>arrow(svg,e.x1,e.y1,e.x2,e.y2,e.to===checking?'c-neg':'c-state',e.to===checking?2.6:1.6));
   steps.forEach((s,i)=>{const w=layout.width(i),cx=layout.x[i],cy=layout.y(i);
    node(svg,'rect',{x:cx-w/2,y:cy-19,width:w,height:38,rx:5,class:'lf-node'+(s.rule==='mp'?' derived':'')+(i===last?' conclusion':'')+(i===checking?' checking':'')+(now?.from?.includes(i)?' premise':'')});
    label(svg,cx,cy+6,text(s.f));node(svg,'text',{x:cx-w/2-4,y:cy+5,'text-anchor':'end',class:'lf-caption'},String(i+1))});
   list.replaceChildren(...steps.map((s,i)=>{const li=document.createElement('li');li.textContent=`${text(s.f)} — `+(s.rule==='axiom'?'axiom':`from lines ${s.from[0]+1} and ${s.from[1]+1} by modus ponens`)+(checking>=0&&i<=checking?' ✓':'');if(i===checking)li.className='checking';return li}));
   lab.dataset.steps=String(steps.length);
  }
  function stop(){clearInterval(timer);timer=null;check.textContent='Check it step by step';check.setAttribute('aria-pressed','false')}
  function show(next){stop();steps=next;layout=arrange(steps);checking=-1;lab.dataset.valid=String(verify(steps));lab.dataset.checked='false';draw();
   const inferred=steps.filter(s=>s.rule==='mp').length;lab.querySelector('[data-status]').textContent=`${steps.length} lines: ${steps.length-inferred} axioms and ${inferred} applications of modus ponens. The shaded box with a dark border is the conclusion.`}
  function tick(){checking++;draw();const s=steps[checking],status=lab.querySelector('[data-status]');
   if(s.rule==='axiom')status.textContent=`Line ${checking+1} is an axiom: the checker accepts it without justification.`;
   else{const [x,imp]=s.from;status.textContent=`Line ${checking+1}: line ${imp+1} has the form “X implies Y” with X = ${text(steps[x].f)}, which is line ${x+1}, and Y = ${text(s.f)}, which is this line. Modus ponens applies.`}
   if(checking===steps.length-1){stop();lab.dataset.checked='true';status.textContent+=' Every line is an axiom or follows from earlier lines, so the proof checks.'}}
  check.onclick=()=>{if(timer)return stop();if(checking>=steps.length-1)checking=-1;check.textContent='Pause';check.setAttribute('aria-pressed','true');tick();if(checking<steps.length-1)timer=setInterval(tick,still()?1800:900)};
  lab.querySelector('[data-new]').onclick=()=>{for(let tries=0;tries<300;tries++){const next=generate();if(next.filter(s=>s.rule==='mp').length>=3&&arrange(next))return show(next)}show(example)};
  lab.querySelector('[data-reset]').onclick=()=>show(example);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
  show(example);
 });
 document.querySelectorAll('[data-lab="reversible"]').forEach(lab=>{
  const svg=stage(lab,600,200,'A Boolean function drawn as arrows from inputs to outputs'),next=lab.querySelector('[data-next]'),keep=lab.querySelector('[data-keep]');
  const int=(lo,hi)=>lo+Math.floor(Math.random()*(hi-lo+1)),pick=xs=>xs[int(0,xs.length-1)],bits=(v,n)=>v.toString(2).padStart(n,'0'),ones=v=>v.toString(2).split('1').length-1;
  const gate=(name,n,m,f)=>({name,n,m,table:[...Array(2**n).keys()].map(f)});
  const named=[gate('AND',2,1,x=>x===3?1:0),gate('OR',2,1,x=>x?1:0),gate('XOR',2,1,x=>ones(x)%2),gate('NAND',2,1,x=>x===3?0:1),gate('NOT',1,1,x=>1-x),gate('RESET',1,1,()=>0),
   gate('majority',3,1,x=>ones(x)>=2?1:0),gate('copy',1,2,x=>3*x),gate('swap',2,2,x=>(x&1)<<1|x>>1),gate('CNOT',2,2,x=>x^x>>1&1),gate('Toffoli',3,3,x=>x^(x>>2&x>>1&1))];
  function random(){
   if(Math.random()<.4)return pick(named.slice(1));
   const n=int(1,3),m=int(1,3),N=2**n;
   const table=m===n&&Math.random()<.5?[...Array(N).keys()].sort(()=>Math.random()-.5):Array.from({length:N},()=>int(0,2**m-1));
   return{name:'a random function',n,m,table};
  }
  let fn,k,seen,clash,cancelRun=()=>{};
  // With "keep the input", the output of x is the pair (x, f(x)).
  const outputs=()=>fn.table.map((y,x)=>keep.checked?x*2**fn.m+y:y),width=()=>keep.checked?fn.n+fn.m:fn.m;
  const name=v=>keep.checked?`${bits(v>>fn.m,fn.n)}, ${bits(v&2**fn.m-1,fn.m)}`:bits(v,fn.m);
  function verdict(){const out=outputs(),distinct=new Set(out).size;return distinct<out.length?'irreversible':distinct===2**width()?'bijection':'one-to-one'}
  function draw(){
   const out=outputs(),N=out.length,targets=keep.checked?out:[...Array(2**fn.m).keys()],rows=Math.max(N,targets.length),top=58,gap=36,H=top+rows*gap+10,done=clash||k===N;
   const yIn=i=>top+(rows-N)*gap/2+i*gap+gap/2,yOut=v=>top+(rows-targets.length)*gap/2+targets.indexOf(v)*gap+gap/2;
   svg.setAttribute('viewBox',`0 0 600 ${H}`);svg.replaceChildren();
   label(svg,150,30,`input x (${fn.n} bit${fn.n>1?'s':''})`,{class:'lf-caption'});label(svg,450,30,keep.checked?'output (x, f(x))':`output f(x) (${fn.m} bit${fn.m>1?'s':''})`,{class:'lf-caption'});
   const pill=v=>v.length*9+26,inW=pill(bits(0,fn.n)),outW=pill(name(0));
   out.forEach((y,x)=>{const hit=clash&&(x===clash[0]||x===clash[1]),now=!clash&&x===k-1,tint=hit?'c-neg':x<k||hit?'c-state':'c-faint';arrow(svg,150+inW/2,yIn(x),450-outW/2-2,yOut(y),tint,hit?3:now?2.6:1.5)});
   out.forEach((y,x)=>{node(svg,'rect',{x:150-inW/2,y:yIn(x)-14,width:inW,height:28,rx:14,class:'lf-node'+(clash&&clash.includes(x)?' checking':x===k-1&&!clash?' current':'')});label(svg,150,yIn(x)+5,bits(x,fn.n))});
   targets.forEach(v=>{const into=out.slice(0,k+(clash?1:0)).filter(y=>y===v).length,unused=done&&!out.includes(v);
    node(svg,'rect',{x:450-outW/2,y:yOut(v)-14,width:outW,height:28,rx:14,class:'lf-node'+(clash&&out[clash[1]]===v?' checking':'')+(unused?' lf-dim':'')});label(svg,450,yOut(v)+5,name(v),unused?{class:'lf-dim'}:{});
    if(into)node(svg,'text',{x:450+outW/2+10,y:yOut(v)+5,class:'lf-caption'+(into>1?' tint c-neg':'')},into>1?`${into} arrows`:'1 arrow')});
   const N2=2**fn.n,M2=2**width();
   lab.querySelector('[data-about]').textContent=`Function: ${fn.name}, from ${fn.n} bit${fn.n>1?'s':''} to ${keep.checked?`${fn.n+fn.m} bits (the input kept beside f(x))`:`${fn.m} bit${fn.m>1?'s':''}`}. `+(N2>M2?`There are ${N2} inputs but only ${M2} possible outputs, so some output must be shared before we look at any arrow.`:`There are ${N2} inputs and ${M2} possible outputs.`);
   const status=lab.querySelector('[data-status]');
   if(clash){const [a,b]=clash,y=name(out[b]);status.textContent=`Irreversible: inputs ${bits(a,fn.n)} and ${bits(b,fn.n)} both give ${y}. Seeing ${y}, we cannot tell which input occurred.`}
   else if(k===N)status.textContent=verdict()==='bijection'?`Reversible: every one of the ${M2} possible outputs has exactly one arrow arriving. The function is a bijection; its inverse follows each arrow backward.`:`One-to-one: every output that occurs identifies its input, so the step can be undone. `+(keep.checked?`Only ${N} of the ${M2} possible ${width()}-bit outputs occur, so this is not a bijection of one fixed state space. Chapter 2 adds a target bit and XOR to obtain one.`:`Some ${width()}-bit outputs never occur (shown faint), so this is not a bijection of one fixed state space.`);
   else status.textContent=k?`Input ${bits(k-1,fn.n)} gives ${name(out[k-1])}, which no earlier input gave. ${N-k} input${N-k===1?'':'s'} left to check.`:'Check the inputs in order. The first time two arrows reach the same output, the function is irreversible.';
   next.disabled=done;lab.dataset.result=done?(clash?'irreversible':verdict()):'';lab.dataset.table=JSON.stringify(fn.table);
  }
  function step(){if(clash||k===outputs().length)return false;const y=outputs()[k];if(seen.has(y))clash=[seen.get(y),k];else{seen.set(y,k);k++}draw();return !clash&&k<outputs().length}
  function reset(){stop();k=0;seen=new Map;clash=null;draw()}
  function load(f){fn=f;reset()}
  const stop=runner(lab.querySelector('[data-run]'),()=>{if(clash||k===outputs().length){reset();return true}return step()},700);
  next.onclick=()=>{stop();step()};keep.onchange=reset;lab.querySelector('[data-reset]').onclick=reset;
  lab.querySelector('[data-new]').onclick=()=>{let f;do f=random();while(fn&&JSON.stringify(f.table)===JSON.stringify(fn.table)&&f.n===fn.n);keep.checked=false;load(f)};
  lab.querySelector('[data-example]').onclick=()=>{keep.checked=false;load(named[0])};
  load(named[0]);
 });
 document.querySelectorAll('[data-lab="nand-toffoli"]').forEach(lab=>{
  const svg=stage(lab,600,400,'A NAND circuit and the Toffoli circuit obtained from it'),next=lab.querySelector('[data-next]'),inputsBox=lab.querySelector('[data-inputs]');
  const int=(lo,hi)=>lo+Math.floor(Math.random()*(hi-lo+1)),names='abc';
  // A circuit is a list of NAND gates; each reads two distinct earlier signals (inputs first, then gates).
  function random(){
   for(;;){const n=int(2,3),g=int(2,4),gates=[];
    for(let k=0;k<g;k++){const pool=[...Array(n+k).keys()],recent=k?[n+k-1]:[];let a=Math.random()<.6&&recent.length?recent[0]:pool[int(0,pool.length-1)],b;do b=pool[int(0,pool.length-1)];while(b===a);gates.push([a,b].sort((x,y)=>x-y))}
    const used=new Set,visit=s=>{if(used.has(s))return;used.add(s);if(s>=n)gates[s-n].forEach(visit)};visit(n+g-1);
    if(used.size===n+g)return{n,gates}}
  }
  const example={n:2,gates:[[0,1],[0,2],[1,2],[3,4]]};
  let circuit,bits,shown,ops;
  const label2=(s,c=circuit)=>s<c.n?names[s]:`g${s-c.n+1}`;
  const classical=(c,x)=>{const v=[...x];c.gates.forEach(([a,b])=>v.push(1-(v[a]&v[b])));return v};
  // Reversible wires: inputs, one target per gate (starts at 1), and an answer bit (starts at 0).
  function reversible(c,x,count){const v=[...x,...c.gates.map(()=>1),0],ops=plan(c);ops.slice(0,count).forEach(o=>{if(o.cnot)v[v.length-1]^=v[c.n+c.gates.length-1];else{const [a,b]=c.gates[o.gate];v[c.n+o.gate]^=v[a]&v[b]}});return v}
  const plan=c=>[...c.gates.map((_,k)=>({gate:k})),{cnot:true},...c.gates.map((_,k)=>({gate:c.gates.length-1-k,undo:true}))];
  function verify(c,count){let agree=true,clean=true;for(let m=0;m<2**c.n;m++){const x=[...Array(c.n)].map((_,i)=>m>>(c.n-1-i)&1),f=classical(c,x).at(-1),v=reversible(c,x,count),g=c.gates.length;
    if(count>=g&&(count===g?v[c.n+g-1]:v.at(-1))!==f)agree=false;if(count===2*g+1&&(v.at(-1)!==f||v.slice(c.n,c.n+g).some(b=>b!==1)))clean=false}return{agree,clean}}
  function draw(){
   const {n,gates}=circuit,g=gates.length,values=classical(circuit,bits),top=40,lane=44,H1=top+(n+g)*lane-10;
   // Every signal has its own lane; gate k sits on lane n+k, so no wire passes behind a gate.
   const pos=[...Array(n+g).keys()].map(s=>[s<n?40:130+(s-n)*105,top+s*lane]),out=s=>s<n?pos[s][0]+14:pos[s][0]+43;
   const current=shown>0&&shown<=g?shown-1:-1,converted=Math.min(shown,g);
   svg.replaceChildren();node(svg,'text',{x:12,y:22,class:'lf-caption'},'NAND circuit');
   const wire=v=>v?'lf-wire one':'lf-wire';
   gates.forEach(([a,b],k)=>{const [gx,gy]=pos[n+k];[a,b].forEach((src,i)=>{const [,sy]=pos[src],iy=gy-10+20*i,mx=gx-16-10*i;node(svg,'path',{d:`M${out(src)} ${sy}H${mx}V${iy}H${gx}`,class:wire(values[src])})})});
   const [ox,oy]=pos[n+g-1];node(svg,'path',{d:`M${ox+44} ${oy}H${ox+70}`,class:wire(values.at(-1))});label(svg,ox+86,oy+5,values.at(-1),{class:'tint c-state'});
   for(let s=0;s<n;s++){const [x,y]=pos[s];node(svg,'circle',{cx:x,cy:y,r:13,class:'lf-node'});label(svg,x,y+5,names[s]);label(svg,x-26,y+5,bits[s],{class:'tint c-state'})}
   gates.forEach((_,k)=>{const [x,y]=pos[n+k];node(svg,'path',{d:`M${x} ${y-18}h16a18 18 0 0 1 0 36h-16z`,class:'lf-node'+(k===current?' checking':k<converted?' derived':'')});node(svg,'circle',{cx:x+39,cy:y,r:4,class:'lf-node'+(k===current?' checking':'')});label(svg,x+16,y-24,`g${k+1}`,{class:'lf-caption'})});
   // Reversible circuit below: one wire per input, per converted gate's target, and the answer bit once it is used.
   const list=plan(circuit).slice(0,shown),answer=shown>g,wires=[...Array(n).keys()].map(i=>({name:names[i],start:bits[i],index:i})).concat(gates.slice(0,converted).map((_,k)=>({name:`g${k+1}`,start:1,index:n+k}))).concat(answer?[{name:'answer',start:0,index:n+g}]:[]);
   const t0=H1+46,row=34,X=i=>150+i*(400/Math.max(1,2*g+1)),H=t0+wires.length*row+16,y=w=>t0+wires.indexOf(w)*row;
   svg.setAttribute('viewBox',`0 0 600 ${H}`);node(svg,'text',{x:12,y:t0-22,class:'lf-caption'},'Toffoli circuit (time runs left to right)');
   let state=reversible(circuit,bits,0);const segments=[state];list.forEach((_,i)=>segments.push(state=reversible(circuit,bits,i+1)));
   wires.forEach(w=>{const yy=y(w);node(svg,'text',{x:12,y:yy+5},`${w.name}`);node(svg,'text',{x:96,y:yy+5,'text-anchor':'end',class:'tint c-state'},String(w.start));
    segments.forEach((v,i)=>node(svg,'path',{d:`M${i?X(i-1)+0:104} ${yy}H${i<list.length?X(i):570}`,class:wire(v[w.index])}));node(svg,'text',{x:578,y:yy+5,class:'tint c-state'},String(segments.at(-1)[w.index]))});
   list.forEach((o,i)=>{const x=X(i),g2=node(svg,'g',i===shown-1?{class:'lf-new'}:{}),targetWire=o.cnot?wires.at(-1):wires.find(w=>w.index===n+o.gate),controls=o.cnot?[wires.find(w=>w.index===n+g-1)]:circuit.gates[o.gate].map(s=>wires.find(w=>w.index===s));
    const ys=[...controls.map(y),y(targetWire)];node(g2,'path',{d:`M${x} ${Math.min(...ys)}V${Math.max(...ys)}`,class:'lf-thin c-state',style:'stroke-width:1.8'});
    controls.forEach(w=>node(g2,'circle',{cx:x,cy:y(w),r:5,class:'lf-dot'}));node(g2,'circle',{cx:x,cy:y(targetWire),r:10,class:'lf-node'+(i===shown-1?' checking':'')});node(g2,'path',{d:`M${x-10} ${y(targetWire)}H${x+10}M${x} ${y(targetWire)-10}V${y(targetWire)+10}`,class:'lf-thin c-state',style:'stroke-width:1.6'});
    if(o.undo)label(g2,x,t0-6,'undo',{class:'lf-caption'})});
   inputsBox.replaceChildren(...bits.map((b,i)=>{const button=document.createElement('button');button.textContent=`${names[i]} = ${b}`;button.onclick=()=>{bits[i]^=1;draw()};return button}));
   const status=lab.querySelector('[data-status]'),o=list.at(-1),f=values.at(-1);
   if(!shown)status.textContent=`A random circuit of ${g} NAND gates on ${n} inputs. Its output is ${f} for the inputs chosen above. Convert it one gate at a time.`;
   else if(!o.cnot&&!o.undo){const [a,b]=gates[o.gate].map(s=>label2(s));status.textContent=`g${o.gate+1} = NAND(${a}, ${b}) becomes a Toffoli gate with controls ${a} and ${b} and a fresh target set to 1. The target becomes 1 ⊕ ${a}·${b}, which is NAND(${a}, ${b}). The controls are unchanged, so later gates can read ${a} and ${b} again without a copying gate.`+(o.gate===g-1?` The circuit is converted: target g${g} holds the answer ${f}, but the other targets still hold intermediate values.`:'')}
   else if(o.cnot)status.textContent=`A CNOT copies the answer from g${g} into a fresh bit set to 0. Next, the Toffoli gates are applied again in reverse order.`;
   else status.textContent=shown===2*g+1?`Uncomputed: every target is back to 1, and only the copied answer ${f} remains. The workspace is clean: this is uncomputation.`:`Applying the Toffoli gate for g${o.gate+1} again restores its target to 1, because each Toffoli gate is its own inverse.`;
   next.disabled=shown===2*g+1;const check=verify(circuit,shown);lab.dataset.agree=String(check.agree);lab.dataset.clean=shown===2*g+1?String(check.clean):'';lab.dataset.steps=String(shown);
  }
  function load(c){stop();circuit=c;bits=Array(c.n).fill(1);shown=0;draw()}
  const stop=runner(lab.querySelector('[data-run]'),()=>{if(shown===2*circuit.gates.length+1){shown=0;draw();return true}shown++;draw();return shown<2*circuit.gates.length+1},900);
  next.onclick=()=>{stop();shown++;draw()};
  lab.querySelector('[data-reset]').onclick=()=>{stop();shown=0;draw()};
  lab.querySelector('[data-new]').onclick=()=>load(random());
  lab.querySelector('[data-check]').onclick=()=>{const g=circuit.gates.length,{agree,clean}=verify(circuit,2*g+1),rows=2**circuit.n;lab.querySelector('[data-status]').textContent=agree&&clean?`Checked all ${rows} input combinations: the Toffoli circuit gives the same answer as the NAND circuit every time, and uncomputation returns every target to 1.`:'The circuits disagree on some input.';lab.dataset.agree=String(agree);lab.dataset.clean=String(clean)};
  load(example);
 });
 document.querySelectorAll('[data-lab="square-root"]').forEach(lab=>{
  const svg=stage(lab,680,330,'A step with weights a, b, c, d and its two-step paths'),sliders=['switch','stay-phase','switch-phase','one-phase'].map(k=>lab.querySelector(`[data-${k}]`));
  // Complex numbers are pairs [re, im]; a step is a 2×2 array w[i][k] = w(i→k).
  const add=(a,b)=>[a[0]+b[0],a[1]+b[1]],mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]],scale=(a,s)=>[a[0]*s,a[1]*s],abs2=a=>a[0]**2+a[1]**2,conj=a=>[a[0],-a[1]],cis=t=>[Math.cos(t),Math.sin(t)];
  const div=(a,b)=>{const d=abs2(b);return[(a[0]*b[0]+a[1]*b[1])/d,(a[1]*b[0]-a[0]*b[1])/d]},root=([x,y])=>{const r=Math.hypot(x,y);return[Math.sqrt((r+x)/2),(y<0?-1:1)*Math.sqrt(Math.max(0,(r-x)/2))]};
  const two=A=>[0,1].map(i=>[0,1].map(k=>add(mul(A[i][0],A[0][k]),mul(A[i][1],A[1][k])))),gap=(A,B)=>[0,1].reduce((t,i)=>t+[0,1].reduce((u,k)=>u+abs2(add(A[i][k],scale(B[i][k],-1))),0),0);
  const num=v=>{const r=Math.round(v*1000)/1000;return Math.abs(r)<5e-4?0:r},show=z=>{const [x,y]=z.map(num),m=v=>String(Math.abs(v));if(!y)return(x<0?'−':'')+m(x);const im=(Math.abs(y)===1?'':m(y))+'i';return x?`${x<0?'−':''}${m(x)} ${y<0?'−':'+'} ${im}`:(y<0?'−':'')+im};
  // Target: from 0, stay √(1−p)·e^{iβ} and switch √p·e^{iγ}; from 1, switch √p·e^{i(φ−γ)} and stay −√(1−p)·e^{i(φ−β)}. Every slider setting is a valid step.
  function target(){const [p,b,g,f]=sliders.map(s=>Number(s.value)),st=Math.sqrt(1-p),sw=Math.sqrt(p),r=Math.PI/180;
   return[[scale(cis(b*r),st),scale(cis(g*r),sw)],[scale(cis((f-g)*r),sw),scale(cis((f-b)*r),-st)]]}
  // A = (B + sI)/t with s² = B(0→0)B(1→1) − B(0→1)B(1→0) and t² = B(0→0) + B(1→1) + 2s.
  function roots(B){const det=add(mul(B[0][0],B[1][1]),scale(mul(B[0][1],B[1][0]),-1)),tr=add(B[0][0],B[1][1]),s0=root(det),found=[];
   for(const s of [s0,scale(s0,-1)]){const t2=add(tr,scale(s,2));if(abs2(t2)<1e-12)continue;const t=root(t2),A=[0,1].map(i=>[0,1].map(k=>div(i===k?add(B[i][k],s):B[i][k],t)));
    for(const sign of [1,-1]){const R=A.map(r=>r.map(z=>scale(z,sign)));if(!found.some(F=>gap(F,R)<1e-12))found.push(R)}}
   return found}
  let B,list,A=null,start=0;
  // Follow the root nearest the previous one, so a, b, c, d change smoothly as the sliders move.
  function solve(jump){B=target();list=roots(B);const order=A?list.map((R,i)=>[gap(R,A),i]).sort((x,y)=>x[0]-y[0]):[[0,0]];A=list[jump?(order[0][1]+1)%list.length:order[0][1]];draw()}
  const sym=['a','b','c','d'],w=(i,k)=>A[i][k],name=(i,k)=>sym[2*i+k];
  function draw(){
   svg.replaceChildren();
   // State diagram, as in the figure above: loops carry the stay weights, arcs the switch weights.
   label(svg,160,26,'State diagram',{class:'lf-caption'});
   const n0=[95,165],n1=[225,165],mid=(n0[0]+n1[0])/2,tint=k=>k?'c-neg':'c-state';
   curve2(n0[0]-16,n0[1]-18,n0[0]-60,n0[1]-95,n0[0]+30,n0[1]-95,n0[0]+6,n0[1]-24,'c-state');
   curve2(n1[0]+16,n1[1]+18,n1[0]+60,n1[1]+95,n1[0]-30,n1[1]+95,n1[0]-6,n1[1]+24,'c-state');
   curve2(n0[0]+20,n0[1]-14,n0[0]+45,n0[1]-60,n1[0]-45,n1[1]-60,n1[0]-20,n1[1]-14,'c-neg');
   curve2(n1[0]-20,n1[1]+14,n1[0]-45,n1[1]+60,n0[0]+45,n0[1]+60,n0[0]+20,n0[1]+14,'c-neg');
   [[n0[0]-15,n0[1]-100,0,0,17],[mid,n0[1]-76,0,1,18],[mid,n1[1]+84,1,0,-18],[n1[0]+15,n1[1]+97,1,1,17]].forEach(([x,y,i,k,dy])=>{label(svg,x,y,name(i,k),{class:'tint '+tint(i!==k),style:'font-style:italic;font-size:17px'});label(svg,x,y+dy,show(w(i,k)),{class:'lf-caption'})});
   [[n0,'0'],[n1,'1']].forEach(([[x,y],t])=>{node(svg,'circle',{cx:x,cy:y,r:22,class:'lf-node'});label(svg,x,y+5,t)});
   node(svg,'path',{d:'M300 20V310',class:'lf-thin c-faint'});
   // Time-expanded diagram from the chosen start, with the two-step path sums at the end.
   const X=[340,445,550],Y=[110,230];label(svg,445,26,`Time-expanded diagram from ${start}`,{class:'lf-caption'});X.forEach((x,t)=>label(svg,x,70,`t = ${t}`,{class:'lf-caption'}));
   for(let s=0;s<2;s++)for(let a=0;a<2;a++)for(let b=0;b<2;b++){if(s===0&&a!==start)continue;const x1=X[s]+18,y1=Y[a],x2=X[s+1]-20,y2=Y[b];arrow(svg,x1,y1,x2,y2,tint(a!==b),1.6);
    const f=a===b?.5:.28,mx=x1+(x2-x1)*f,my=y1+(y2-y1)*f;label(svg,a===b?mx:mx+(b>a?12:12),a===b?my+(a?20:-8):my+(b>a?-2:12),name(a,b),{class:'tint '+tint(a!==b),style:'font-style:italic'})}
   X.forEach((x,t)=>Y.forEach((y,j)=>{const unused=t===0&&j!==start;node(svg,'circle',{cx:x,cy:y,r:16,class:'lf-node'+(unused?' lf-dim':'')});label(svg,x,y+5,String(j),unused?{class:'lf-dim'}:{})}));
   const formula=[['a² + bc','ab + bd'],['ca + dc','cb + d²']],T=two(A);
   [0,1].forEach(k=>{label(svg,584,Y[k]-4,formula[start][k],{'text-anchor':'start'});label(svg,584,Y[k]+15,`= ${show(T[start][k])}`,{'text-anchor':'start',class:'lf-caption'})});
   label(svg,445,300,`target B: ${show(B[start][0])} at 0, ${show(B[start][1])} at 1`,{class:'lf-caption'});
   // Equations and validity checks.
   const eq=[['a² + bc',0,0],['ab + bd',0,1],['ca + dc',1,0],['cb + d²',1,1]].map(([f,i,k])=>`${f} = ${show(T[i][k])}   (B from ${i} to ${k}: ${show(B[i][k])})`);
   const p0=abs2(w(0,0))+abs2(w(0,1)),p1=abs2(w(1,0))+abs2(w(1,1)),cross=add(mul(conj(w(0,0)),w(1,0)),mul(conj(w(0,1)),w(1,1)));
   lab.querySelector('[data-equations]').textContent=eq.join('\n');
   lab.querySelector('[data-status]').textContent=`Square root ${list.indexOf(A)+1} of ${list.length}. All four two-step sums equal the weights of B, so A² = B. A is a valid step: |a|² + |b|² = ${num(p0)}, |c|² + |d|² = ${num(p1)}, and the cross-sum a*c + b*d = ${show(cross)}.`+(list.length<4?' This B does nothing up to a common phase, so it has infinitely many square roots; for example, NOT, Hadamard, and the sign flip all square to doing nothing. The construction finds only two.':'');
   const [p,b,g,f]=sliders.map(s=>Number(s.value));lab.querySelector('[data-switch-out]').textContent=p.toFixed(2);['stay-phase','switch-phase','one-phase'].forEach((k,i)=>lab.querySelector(`[data-${k}-out]`).textContent=`${[b,g,f][i]}°`);
   lab.dataset.ok=String(list.every(R=>gap(two(R),B)<1e-12&&[0,1].every(r=>Math.abs(abs2(R[r][0])+abs2(R[r][1])-1)<1e-9)));lab.dataset.roots=String(list.length);lab.dataset.weights=JSON.stringify(A.flat().flat().map(num));
  }
  function curve2(x0,y0,x1,y1,x2,y2,x3,y3,tint){const g=node(svg,'g',{class:tint});node(g,'path',{d:`M${x0} ${y0}C${x1} ${y1} ${x2} ${y2} ${x3} ${y3}`,class:'lf-line',style:'stroke-width:1.6'});const dx=x3-x2,dy=y3-y2,l=Math.hypot(dx,dy),ux=dx/l,uy=dy/l,h=9;node(g,'path',{d:`M${x3} ${y3}L${x3-h*ux+h*.42*uy} ${y3-h*uy-h*.42*ux}L${x3-h*ux-h*.42*uy} ${y3-h*uy+h*.42*ux}Z`,class:'lf-head'})}
  sliders.forEach(s=>s.oninput=()=>solve(false));
  const presets={not:[1,0,0,0],hadamard:[.5,0,0,0],none:[0,0,0,180],sign:[0,0,0,0]};
  lab.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>{presets[b.dataset.preset].forEach((v,i)=>sliders[i].value=v);A=null;solve(false)});
  lab.querySelector('[data-another]').onclick=()=>solve(true);
  lab.querySelectorAll('[data-start]').forEach(b=>b.onclick=()=>{start=Number(b.dataset.start);draw()});
  solve(false);
 });
 document.querySelectorAll('[data-lab="adjoint"]').forEach(lab=>{
  const svg=stage(lab,600,440,'A vector, its images under A dagger then A, and under A then A dagger'),entries=[...lab.querySelectorAll('[data-entry]')],angle=lab.querySelector('[data-psi]');
  // Real 2×2 matrices act on column vectors; for real entries the adjoint is the transpose.
  const apply=(M,v)=>[M[0][0]*v[0]+M[0][1]*v[1],M[1][0]*v[0]+M[1][1]*v[1]],mm=(P,Q)=>[0,1].map(i=>[0,1].map(k=>P[i][0]*Q[0][k]+P[i][1]*Q[1][k])),T=M=>[[M[0][0],M[1][0]],[M[0][1],M[1][1]]];
  const r=v=>{const x=Math.round(v*100)/100;return Object.is(x,-0)||Math.abs(x)<.005?'0':String(x)},tex=M=>`\\begin{pmatrix}${r(M[0][0])}&${r(M[0][1])}\\\\${r(M[1][0])}&${r(M[1][1])}\\end{pmatrix}`,col=v=>`\\begin{pmatrix}${r(v[0])}\\\\${r(v[1])}\\end{pmatrix}`;
  const dir=v=>Math.atan2(v[1],v[0]),between=(u,v)=>{let d=dir(v)-dir(u);while(d>Math.PI)d-=2*Math.PI;while(d<-Math.PI)d+=2*Math.PI;return d};
  let t=2,cancel=()=>{};
  const matrix=()=>[[Number(entries[0].value),Number(entries[1].value)],[Number(entries[2].value),Number(entries[3].value)]];
  function draw(){
   const A=matrix(),D=T(A),psi=[Math.cos(angle.value*Math.PI/180),Math.sin(angle.value*Math.PI/180)];
   const orange=[psi,apply(D,psi),apply(A,apply(D,psi))],green=[psi,apply(A,psi),apply(D,apply(A,psi))];
   // Within each stage the vector slides from one image to the next.
   const at=(path,t)=>{const s=Math.min(1,Math.floor(t)),f=t-s;if(t>=2)return path[2];const [u,v]=[path[s],path[s+1]];return[u[0]+(v[0]-u[0])*f,u[1]+(v[1]-u[1])*f]};
   const all=[...orange,...green],reach=Math.max(1,...all.map(v=>Math.hypot(...v))),cx=300,cy=220,unit=190/reach,P=v=>[cx+unit*v[0],cy-unit*v[1]];
   svg.replaceChildren();
   node(svg,'path',{d:`M${cx-210} ${cy}H${cx+210}M${cx} ${cy+200}V${cy-200}`,class:'lf-thin c-axis'});label(svg,cx+226,cy+5,'|0⟩');label(svg,cx,cy-206,'|1⟩');
   node(svg,'circle',{cx,cy,r:unit,class:'lf-ring'});
   const ray=v=>{const l=Math.hypot(...v)||1;return[v[0]/l*reach*1.05,v[1]/l*reach*1.05]};node(svg,'path',{d:`M${cx} ${cy}L${P(ray(psi))}`,class:'lf-thin lf-dash c-faint'});
   if(t>=1){[[orange[1],'c-orange'],[green[1],'c-green']].forEach(([v,c])=>{const g=arrow(svg,cx,cy,...P(v),c,1.6);g.classList.add('lf-dash');g.style.opacity=.55})}
   const arc=(v,radius,c,name)=>{const a=dir(psi),d=between(psi,v);if(Math.abs(d)<.005)return;const b=a+d,[x1,y1]=[cx+radius*Math.cos(a),cy-radius*Math.sin(a)],[x2,y2]=[cx+radius*Math.cos(b),cy-radius*Math.sin(b)];
    node(svg,'path',{d:`M${x1} ${y1}A${radius} ${radius} 0 0 ${d>0?0:1} ${x2} ${y2}`,class:'lf-thin '+c,style:'stroke-width:1.8'});const m=a+d/2;label(svg,cx+(radius+16)*Math.cos(m),cy-(radius+16)*Math.sin(m)+5,name,{class:'tint '+c})};
   if(t>=2){arc(orange[2],Math.min(unit+44,170),'c-orange','α');arc(green[2],Math.min(unit+80,200),'c-green','β')}
   const o=at(orange,t),g=at(green,t);arrow(svg,cx,cy,...P(o),'c-orange',3);arrow(svg,cx,cy,...P(g),'c-green',3);arrow(svg,cx,cy,...P(psi),'c-state',3);
   const tag=(v,text,c)=>{const [x,y]=P(v),l=Math.hypot(x-cx,y-cy)||1;label(svg,x+(x-cx)/l*28,y+(y-cy)/l*20+5,text,{class:'tint '+c})};
   tag(psi,'ψ','c-state');const same=Math.hypot(orange[2][0]-green[2][0],orange[2][1]-green[2][1])<1e-6;if(t>=2){if(same)tag(orange[2],'AA†ψ = A†Aψ','c-state');else{tag(orange[2],'AA†ψ','c-orange');tag(green[2],'A†Aψ','c-green')}}else if(t>=1){tag(orange[1],'A†ψ','c-orange');tag(green[1],'Aψ','c-green')}
   const AD=mm(A,D),DA=mm(D,A),alpha=between(psi,orange[2])*180/Math.PI,beta=between(psi,green[2])*180/Math.PI,unitary=[0,1].every(i=>[0,1].every(k=>Math.abs(DA[i][k]-(i===k))<1e-9));
   math(lab.querySelector('[data-state]'),`\\(A=${tex(A)}\\), \\(A^\\dagger=${tex(D)}\\), \\(AA^\\dagger=${tex(AD)}\\), \\(A^\\dagger A=${tex(DA)}\\). The rightmost matrix acts first.`);
   math(lab.querySelector('[data-chains]'),`\\(\\ket\\psi=${col(psi)}\\xrightarrow{A^\\dagger}${col(orange[1])}\\xrightarrow{A}AA^\\dagger\\ket\\psi=${col(orange[2])}\\), and \\(\\ket\\psi\\xrightarrow{A}${col(green[1])}\\xrightarrow{A^\\dagger}A^\\dagger A\\ket\\psi=${col(green[2])}\\).`);
   lab.querySelector('[data-status]').textContent=unitary?'A is unitary: A†A = AA† = I, so both orders return ψ exactly. The adjoint undoes A.':`Angles from ψ: α ≈ ${Math.abs(alpha).toFixed(1)}° for AA†ψ, β ≈ ${Math.abs(beta).toFixed(1)}° for A†Aψ. `+([0,1].every(i=>[0,1].every(k=>Math.abs(AD[i][k]-DA[i][k])<1e-9))?'Here AA† = A†A, so both orders agree, but neither is the identity: the adjoint does not undo A.':'The two orders give different results, and neither restores ψ: A is not unitary, so A† is not its inverse.');
   entries.forEach(e=>e.previousElementSibling&&(e.previousElementSibling.textContent=r(Number(e.value))));lab.querySelector('[data-psi-out]').textContent=`${Number(angle.value).toFixed(1)}°`;
   lab.dataset.alpha=String(Math.abs(alpha));lab.dataset.beta=String(Math.abs(beta));lab.dataset.unitary=String(unitary);
  }
  const presets={shear:[1,1,0,1],rotation:[.8,-.6,.6,.8],stretch:[2,0,0,.5],squeeze:[1.5,.5,.5,.5]};
  lab.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>{cancel();const p=b.dataset.preset==='random'?[0,0,0,0].map(()=>Math.round((Math.random()*4-2)*10)/10):presets[b.dataset.preset];entries.forEach((e,i)=>e.value=p[i]);t=2;draw()});
  lab.querySelector('[data-play]').onclick=()=>{cancel();t=0;cancel=tween(2400,s=>{t=2*s;draw()},()=>{t=2;draw()})};
  [...entries,angle].forEach(e=>e.oninput=()=>{cancel();t=2;draw()});
  draw();
 });
 document.querySelectorAll('[data-lab="parallel"]').forEach(lab=>{
  const svg=stage(lab,600,300,'Amplitudes of input and target configurations during a parallel evaluation'),choice=lab.querySelector('[data-function]'),next=lab.querySelector('[data-next]');
  const bits=(v,n)=>v.toString(2).padStart(n,'0'),int=(lo,hi)=>lo+Math.floor(Math.random()*(hi-lo+1));
  const tables={and:[0,0,0,1],xor:[0,1,1,0],zero:[0,0,0,0],first:[0,0,1,1]};
  let f,n,stage2,amp,known,runs,note='',last=null;
  // amp[x][y] is the amplitude of |x>|y>; stages: 0 start, 1 after H on the inputs, 2 after U_f.
  function prepare(s){const N=2**n;amp=[...Array(N)].map((_,x)=>[s===0?(x===0?1:0):s===1?1/Math.sqrt(N):(f[x]?0:1/Math.sqrt(N)),s===2&&f[x]?1/Math.sqrt(N):0]);stage2=s;last=null}
  function sample(){let r=Math.random();for(let x=0;x<amp.length;x++)for(const y of [0,1]){r-=amp[x][y]**2;if(r<=0)return[x,y]}return[amp.length-1,f[amp.length-1]]}
  function draw(){
   const N=2**n,row=30,top=56,H=top+N*row+20;svg.setAttribute('viewBox',`0 0 600 ${H}`);svg.replaceChildren();
   label(svg,70,top-24,'input x',{class:'lf-caption'});label(svg,175,top-24,'target 0',{class:'lf-caption'});label(svg,295,top-24,'target 1',{class:'lf-caption'});
   label(svg,470,top-38,'values learned from runs',{class:'lf-caption'});label(svg,430,top-18,'x',{class:'lf-caption'});label(svg,510,top-18,'f(x)',{class:'lf-caption'});
   for(let x=0;x<N;x++){const y=top+x*row;label(svg,70,y+19,`|${bits(x,n)}⟩`);
    [0,1].forEach(t=>{const a=amp[x][t],p=a*a,cx=120+t*120,hit=last&&last[0]===x&&last[1]===t;node(svg,'rect',{x:cx,y:y+3,width:110,height:row-6,rx:3,class:'lf-track'});node(svg,'rect',{x:cx,y:y+3,width:110*p**.5*(p>0?1:0),height:row-6,rx:3,class:'lf-bar'+(hit?' c-neg':''),style:hit?'fill:currentColor':''});if(a)label(svg,cx+55,y+20,(Math.round(a*1000)/1000).toString(),{style:'font-size:12px'+(Math.abs(a)>.6?';fill:white':'')})});
    label(svg,430,y+19,bits(x,n),{class:'lf-caption'});label(svg,510,y+19,known[x]==null?'?':String(known[x]),known[x]==null?{class:'lf-caption'}:{class:'tint c-state'})}
   const learned=known.filter(v=>v!=null).length,status=lab.querySelector('[data-status]');
   lab.querySelector('[data-state]').textContent=`Runs so far: ${runs}. Values learned: ${learned} of ${N}. Evaluating f one input at a time would take exactly ${N} evaluations.`;
   status.textContent=note||['All qubits start in 0. Apply H to each input qubit.',`Every input string now has amplitude 1/√${N}; the target is still 0. Apply U_f.`,'Each input now sits beside its own value. Measure every qubit, or only the target.'][stage2];
   next.disabled=stage2===2;next.textContent=['Apply H to the inputs','Apply U_f','Applied'][stage2];
   lab.dataset.runs=String(runs);lab.dataset.learned=String(learned);lab.dataset.table=JSON.stringify(f);lab.dataset.amps=JSON.stringify(amp);
  }
  function measureAll(){if(stage2<2)prepare(2);const [x,y]=sample();runs++;known[x]=y;amp=amp.map((r,i)=>r.map((_,t)=>i===x&&t===y?1:0));last=[x,y];note=`This run returned the input ${bits(x,n)} with value ${y}. The other pairs are gone; learning another value needs a fresh preparation.`;draw();return[x,y]}
  function measureTarget(){if(stage2<2)prepare(2);const p1=amp.reduce((s,r)=>s+r[1]**2,0),y=Math.random()<p1?1:0,p=y?p1:1-p1,keep=amp.map(r=>r[y]).map(a=>a/Math.sqrt(p));runs++;amp=keep.map(a=>y?[0,a]:[a,0]);last=null;
   const inputs=keep.map((a,x)=>a?bits(x,n):null).filter(Boolean);note=`The target gave ${y}, with probability ${(Math.round(p*1000)/1000)}. The inputs left are exactly the strings with value ${y}: ${inputs.join(', ')}. We learn that f takes the value ${y}, but not at which input unless only one remains.`;
   if(inputs.length===1)known[parseInt(inputs[0],2)]=y;draw()}
  function load(table){f=table;n=Math.log2(table.length);known=Array(table.length).fill(null);runs=0;note='';prepare(0);draw()}
  next.onclick=()=>{note='';prepare(stage2+1);draw()};
  lab.querySelector('[data-all]').onclick=measureAll;lab.querySelector('[data-target]').onclick=measureTarget;
  lab.querySelector('[data-again]').onclick=()=>{note='A fresh preparation: the same parallel state as before the last measurement.';prepare(2);draw()};
  lab.querySelector('[data-collect]').onclick=()=>{const start=runs;while(known.some(v=>v==null)){prepare(2);measureAll()}note=`Every value is now known after ${runs-start} more runs, ${runs} in all, compared with ${f.length} one-at-a-time evaluations. Random sampling repeats inputs, so it usually needs more runs than there are values.`;draw()};
  choice.onchange=()=>load(choice.value==='random'?Array.from({length:2**int(2,3)},()=>int(0,1)):tables[choice.value]);
  load(tables.and);
 });
})();
