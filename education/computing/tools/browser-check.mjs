/* Optional browser smoke checks. Requires Node 22+ and Google Chrome. */
import {spawn} from 'node:child_process';
import {mkdtemp,readFile,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=process.env.BOOK_ROOT||fileURLToPath(new URL('..',import.meta.url));
const sourceRoot=fileURLToPath(new URL('..',import.meta.url));
const profile=await mkdtemp(join(tmpdir(),'qc-book-browser-'));
const chrome=spawn(process.env.CHROME||'google-chrome',['--headless','--no-sandbox','--disable-gpu','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;let serial=0;const pending=new Map();const errors=[];
try {
 let port;for(let i=0;i<100;i++){try{port=(await readFile(join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch{await sleep(100)}}
 if(!port)throw Error('Chrome did not start');
 const pages=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
 ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);if(m.error)p.reject(Error(m.error.message));else p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)};
 function send(method,params={}){return new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))})}
 async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value}
 async function navigate(name){await send('Page.navigate',{url:pathToFileURL(join(root,name+'.html')).href});for(let i=0;i<100;i++){const ready=await evaluate(`document.readyState==='complete' && document.documentElement.dataset.mathReady==='true'`);if(ready){await evaluate('document.fonts.ready.then(()=>true)');return}await sleep(100)}throw Error('Page not ready: '+name+' '+JSON.stringify(await evaluate('({url:location.href,state:document.readyState,math:document.documentElement.dataset.mathReady,hasMath:!!window.MathJax})')))}
 async function screenshot(name,selector){if(selector)await evaluate(`document.querySelector(${JSON.stringify(selector)}).scrollIntoView({behavior:'instant',block:'start'})`);await evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');const shot=await send('Page.captureScreenshot',{format:'png'});await writeFile(join(tmpdir(),name+'.png'),Buffer.from(shot.data,'base64'))}
 async function assert(expression,label){if(!await evaluate(expression))throw Error('Failed: '+label);console.log('PASS '+label)}
 await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1050,deviceScaleFactor:1,mobile:false});
 await navigate('01-logic-computability');
 await assert(`document.querySelectorAll('.book-part').length===4&&document.querySelectorAll('.reading-topic').length===11`,'chapter structure');
 await assert(`document.querySelectorAll('.book-drawing svg.book-figure').length===11&&[...document.querySelectorAll('.book-drawing svg.book-figure')].every(s=>s.getBoundingClientRect().width>0)`,'chapter concept diagrams loaded');
 await assert(`document.querySelectorAll('.problem-solution').length===33&&[...document.querySelectorAll('.problem-solution')].every(d=>!d.open&&!d.querySelector('p').checkVisibility())`, 'subsection solutions are initially hidden');
 await assert(`[...document.querySelectorAll('.probing-question')].every(d=>d.tagName==='DETAILS'&&!d.open&&d.querySelector('summary').textContent==='Problems'&&!d.querySelector('.problem-text').checkVisibility())`, 'problem sets start collapsed');
 await assert(`(()=>{const d=document.querySelector('.probing-question');d.querySelector('summary').click();return d.open&&d.querySelector('.problem-text').checkVisibility()&&[...d.querySelectorAll('.problem-solution')].every(s=>!s.open)})()`, 'opening problems leaves solutions hidden');
 await assert(`(()=>{const d=document.querySelector('.problem-solution');d.querySelector('summary').click();return d.open&&d.querySelector('p').checkVisibility()&&getComputedStyle(d.querySelector('.solution-closed')).display==='none'&&[...document.querySelectorAll('.problem-solution')].filter(x=>x.open).length===1})()`, 'one solution opens independently');
 await screenshot('book-problem-solution','#topic-1-1-1 .probing-question');
 await assert(`(()=>{const d=document.querySelector('.problem-solution');d.querySelector('summary').click();return !d.open})()`, 'solution closes again');
 await assert(`(()=>{const d=document.querySelector('.probing-question');d.querySelector('summary').click();return !d.open&&!d.querySelector('.problem-text').checkVisibility()})()`, 'problem set collapses again');
 await assert(`(()=>{location.hash='topic-1-1-1-problem-2';return new Promise(resolve=>setTimeout(()=>resolve(document.querySelector('.probing-question').open&&document.querySelector('#topic-1-1-1-problem-2 .problem-text').checkVisibility()&&!document.querySelector('#topic-1-1-1-problem-2 .problem-solution').open),100))})()`, 'direct problem link reveals questions without solutions');
 await screenshot('book-probing-question','#topic-1-1-2 .probing-question');
 await screenshot('book-turing-diagram','#figure-logic-turing-machine');
 await screenshot('book-halting-diagram','#figure-logic-halting-contradiction');
 await screenshot('book-rewrite-opening','#section-1-1');
 await navigate('02-boolean-reversible-computation');
 await screenshot('book-rewrite-nand','#topic-2-2-2');
 await navigate('08-circuits-universality');
 await assert(`(()=>{const l=document.querySelector('[data-lab="gates"]');l.querySelector('[data-gate="H"]').click();l.querySelector('[data-gate="H"]').click();const v=JSON.parse(l.dataset.amplitudes);return Math.abs(v[0]-1)<1e-9&&Math.abs(v[1])<1e-9})()`, 'H twice restores the state');
 await navigate('05-composite-systems');
 await screenshot('book-rewrite-teleportation','#topic-5-4-2');
 await assert(`(()=>{const l=document.querySelector('[data-lab="bell"]');l.querySelector('[data-next]').click();l.querySelector('[data-next]').click();const v=JSON.parse(l.dataset.amplitudes);return Math.abs(v[0]**2-.5)<1e-9&&Math.abs(v[3]**2-.5)<1e-9&&v[1]===0&&v[2]===0})()`, 'Bell preparation gives 00/11 amplitudes');
 await navigate('07-amplitude-amplification');
 await assert(`(()=>{const l=document.querySelector('[data-lab="grover"]'),n=l.querySelector('[data-size]');n.value='4';n.dispatchEvent(new Event('change'));l.querySelector('[data-next]').click();return Math.abs(Number(l.dataset.probability)-1)<1e-9})()`, 'Grover N=4 reaches probability one in one iteration');
 await screenshot('book-grover','[data-lab="grover"]');
 await navigate('06-queries-phase-kickback');
 await assert(`(()=>{const l=document.querySelector('[data-lab="phase"]');for(const [f,result] of [['0,0','0'],['1,1','0'],['0,1','1'],['1,0','1']]){const input=l.querySelector('[data-function]');input.value=f;input.dispatchEvent(new Event('change'));l.querySelector('[data-next]').click();l.querySelector('[data-next]').click();if(l.dataset.result!==result)return false}return true})()`, 'phase kickback distinguishes constant and balanced functions');
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await navigate('index');
 await assert(`(()=>{document.querySelector('#menu-toggle').click();return document.body.classList.contains('contents-open')&&!document.querySelector('#book-navigation').inert})()`, 'mobile contents opens');
 await assert(`(()=>{document.querySelector('#nav-scrim').click();return !document.body.classList.contains('contents-open')&&document.querySelector('#book-navigation').inert&&getComputedStyle(document.querySelector('#book-navigation')).visibility==='hidden'})()`, 'mobile contents closes and leaves tab order');
 await assert(`(()=>{document.querySelector('#search-open').click();const i=document.querySelector('#book-search');i.value='amplitude';i.dispatchEvent(new Event('input'));const ok=document.querySelectorAll('#search-results a').length>0;document.querySelector('#search-close').click();return ok})()`, 'book search returns results');
 await assert(`(()=>{const n=parseFloat(getComputedStyle(document.body).fontSize);document.querySelector('#text-larger').click();return parseFloat(getComputedStyle(document.body).fontSize)>n})()`, 'reading font size increases');
 await screenshot('book-mobile');
 for(const chapter of JSON.parse(await readFile(join(sourceRoot,'chapters.json'),'utf8')).map(c=>c[0])){
  await navigate(chapter);
  await evaluate(`Promise.all([...document.querySelectorAll('.reading-topic img')].map(img=>{img.loading='eager';return img.decode()}))`);
  await assert(`document.documentElement.scrollWidth<=innerWidth+2&&!document.querySelector('[data-mml-node="merror"]')`,chapter+' at 390px without page overflow or math errors');
  await assert(`!document.querySelector('svg text[data-tex],svg text[data-math]')&&document.querySelectorAll('svg.book-figure .diagram-math').length>0`,chapter+' typesets every figure label');
  await assert(`[...document.querySelectorAll('.reading-topic')].every(s=>s.querySelector('figure,svg,img')&&s.querySelectorAll('.probing-question > ol > li').length===3)`,chapter+' has illustrations and three questions in every subsection');
 }
 await navigate('notation');
 await assert(`document.documentElement.scrollWidth<=innerWidth+2`,'notation index fits mobile');
 await screenshot('book-mobile-notation');
 await navigate('03-amplitudes-interference');
 await screenshot('book-mobile-phase-illustration','#topic-3-4-2');
 await screenshot('book-mobile-product-path','#topic-3-2-1 figure');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1050,deviceScaleFactor:1,mobile:false});
 await screenshot('book-product-path','#topic-3-2-1 figure');
 for(const topic of ['3-2-2','3-2-3','3-3-1','3-3-2','3-4-1','3-4-2','3-4-3'])await screenshot('book-diagram-'+topic,'#topic-'+topic+' figure');
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});

 await navigate('07-amplitude-amplification');
 await screenshot('book-rewrite-mobile-circuit','#topic-7-1-3');
 await evaluate(`Promise.race([Promise.all(Array.from(document.images).map(i=>{i.loading='eager';return i.decode().catch(()=>{})})),new Promise((_,reject)=>setTimeout(()=>reject(Error('Image loading timed out')),5000))])`);
 await assert(`Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)`,'circuit drawings loaded');
 await navigate('glossary');
 await assert(`(()=>{const q=document.querySelector('#glossary-query');q.value='phase';q.dispatchEvent(new Event('input'));return document.querySelectorAll('.glossary-entry:not([hidden])').length>=3&&document.querySelectorAll('.glossary-entry[hidden]').length>0})()`, 'glossary filters definitions');
 await screenshot('book-glossary');
 await navigate('notation');
 await assert(`document.querySelectorAll('.notation-row:not(.notation-head)').length>=30&&[...document.querySelectorAll('.notation-symbol')].every(e=>e.querySelector('mjx-container'))&&!document.querySelector('[data-mml-node="merror"]')`,'notation index typesets every symbol');
 await screenshot('book-notation');
 await navigate('09-complexity-advantage');
 await assert(`document.querySelectorAll('.exercise').length===3&&document.querySelectorAll('.exercise-hint').length===6`, 'chapter has staged practice');
 await assert(`(()=>{const e=document.querySelector('.exercise-hint');e.querySelector('summary').click();return e.open&&!document.querySelector('.exercise-solution').open})()`, 'hint opens without revealing solution');
 await screenshot('book-practice','#practice');
 await assert(`(()=>{const before=[...document.querySelectorAll('main details')].map(e=>e.open);window.dispatchEvent(new Event('beforeprint'));const expanded=[...document.querySelectorAll('main details')].every(e=>e.open);window.dispatchEvent(new Event('afterprint'));return expanded&&[...document.querySelectorAll('main details')].every((e,i)=>e.open===before[i])})()`, 'printing expands explanations and restores disclosure state');
 await navigate('study-guide');
 await assert(`document.documentElement.scrollWidth<=innerWidth+2`, 'study guide fits mobile');
 await assert(`(()=>{localStorage.setItem('qc-book-position','test');document.querySelector('#clear-reading-data').click();return !localStorage.getItem('qc-book-position')})()`, 'reading preferences can be cleared');
 await navigate('appendices');
 await evaluate(`localStorage.setItem('qc-book-position',JSON.stringify({url:document.body.dataset.chapter+'.html#'+document.querySelector('.book-section').id}))`);
 await navigate('index');
 await assert(`!document.querySelector('#resume-reading').hidden&&document.querySelector('#resume-reading').getAttribute('href').startsWith('appendices.html#')`, 'resume includes appendices');
 await send('Emulation.setScriptExecutionDisabled',{value:true});
 await send('Page.navigate',{url:pathToFileURL(join(root,'01-logic-computability.html')).href});
 await sleep(500);
 await assert(`!document.documentElement.classList.contains('book-js')&&getComputedStyle(document.querySelector('#book-navigation')).transform==='none'&&document.querySelectorAll('.exercise-solution').length===3`, 'mobile navigation and solutions remain available without JavaScript');
 await assert(`(()=>{const d=document.querySelector('.probing-question');if(!d||d.open)return false;d.querySelector('summary').click();return d.open&&d.querySelector('.problem-text').checkVisibility()})()`, 'problem set opens without JavaScript');
 await assert(`(()=>{const d=document.querySelector('.problem-solution');if(!d||d.open)return false;d.querySelector('summary').click();return d.open})()`, 'subsection solution opens without JavaScript');
 await send('Emulation.setScriptExecutionDisabled',{value:false});
 if(errors.length)throw Error(errors.join('; '));console.log('All browser smoke checks passed. Screenshots saved in '+tmpdir());
}finally{ws?.close();chrome.kill();await sleep(400);await rm(profile,{recursive:true,force:true,maxRetries:3}).catch(()=>{})}
