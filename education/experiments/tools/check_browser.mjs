// Optional browser verification. Requires Node with WebSocket and Google Chrome.
// Only opens local course files. Screenshots and browser profile go under /tmp.
import {spawn} from 'node:child_process';
import {readFile, writeFile, mkdtemp} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {tmpdir} from 'node:os';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const work=await mkdtemp(resolve(tmpdir(),'quantum-course-render-'));
const chrome=spawn('google-chrome',['--headless','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--disable-component-update','--no-first-run','--remote-debugging-port=0',`--user-data-dir=${work}/profile`],{stdio:['ignore','ignore','pipe']});
let socket;
try {
 const endpoint=await new Promise((ok,fail)=>{
  let log='';const timer=setTimeout(()=>fail(Error('Chrome startup timeout')),20000);
  chrome.on('error',fail);chrome.stderr.on('data',b=>{log+=b;const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m){clearTimeout(timer);ok(m[1]);}});
 });
 socket=new WebSocket(endpoint);
 await new Promise((ok,fail)=>{socket.addEventListener('open',ok,{once:true});socket.addEventListener('error',fail,{once:true});});
 let id=0;const pending=new Map();
 socket.addEventListener('message',e=>{const msg=JSON.parse(e.data);if(msg.id&&pending.has(msg.id)){const {ok,fail,timer}=pending.get(msg.id);clearTimeout(timer);pending.delete(msg.id);if(msg.error)fail(Error(JSON.stringify(msg.error)));else ok(msg.result);}});
 function call(method,params={},sessionId){return new Promise((ok,fail)=>{const number=++id;const timer=setTimeout(()=>{pending.delete(number);fail(Error(method+' timed out'));},30000);pending.set(number,{ok,fail,timer});socket.send(JSON.stringify({id:number,method,params,...(sessionId?{sessionId}:{})}));});}
 const {targetId}=await call('Target.createTarget',{url:'about:blank'});
 const {sessionId}=await call('Target.attachToTarget',{targetId,flatten:true});
 const tab=(method,params={})=>call(method,params,sessionId);
 await tab('Page.enable');await tab('Runtime.enable');
 await tab('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 async function evaluate(expression){const out=await tab('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(out.exceptionDetails)throw Error(JSON.stringify(out.exceptionDetails));return out.result.value;}
 async function open(file){
  await tab('Page.navigate',{url:pathToFileURL(resolve(root,file)).href});
  await evaluate(`new Promise((resolve,reject)=>{let n=0;const timer=setInterval(()=>{if(document.documentElement.dataset.mathReady==='true'){clearInterval(timer);resolve(true);}else if(++n>200){clearInterval(timer);reject(new Error('MathJax did not finish'));}},50);})`);
  const result=await evaluate(`({errors:[...document.querySelectorAll('[data-mjx-error],mjx-merror,.mjx-merror')].map(e=>e.getAttribute('data-mjx-error')||e.textContent),math:document.querySelectorAll('mjx-container').length,overflow:document.documentElement.scrollWidth>innerWidth+2,images:[...document.querySelectorAll('main img')].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)})`);
  if(result.errors.length||result.images.length||result.overflow)throw Error(file+' '+JSON.stringify(result));
  return result;
 }
 const chapters=JSON.parse(await readFile(resolve(root,'education/experiments/chapters.json'),'utf8'));
 const errors=[];socket.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);});
 for(const c of chapters){
  await open(`education/experiments/${c.stem}.html`);
  const r=await evaluate(`(() => {
   const lab=document.querySelector('.qe-lab'),q=document.getElementById('lab-value'),sel=document.getElementById('lab-mode'),reset=lab.querySelector('[data-action=reset]');
   if(lab.dataset.ready!=='true')throw Error('Lab did not initialize');
   const initial=q.value;let states=0;
   for(const value of [q.min,q.max,initial]){q.value=value;q.dispatchEvent(new Event('input'));for(const option of sel?[...sel.options]:[null]){if(option){sel.value=option.value;sel.dispatchEvent(new Event('change'));}if(/NaN|Infinity/.test(lab.innerHTML))throw Error('Nonfinite visual');states++;}}
   reset.click();lab.querySelector('[data-action=step]').click();const changed=q.value!==initial||Number(lab.dataset.events)>0||lab.dataset.kind==='capstone';
   if(!changed)throw Error('Step did not change state');reset.click();
   if(q.value!==initial||Number(lab.dataset.events)!==0)throw Error('Reset failed');
   for(const e of lab.querySelectorAll('[aria-labelledby]'))for(const id of e.getAttribute('aria-labelledby').split(' '))if(!document.getElementById(id))throw Error('Broken accessible label');
   return {states,kind:lab.dataset.kind};
  })()`);
  console.log('PASS controls',c.stem,r.states,'configurations');
 }
 for(const width of [390,320]){
  await tab('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:true});
  for(const c of chapters)await open(`education/experiments/${c.stem}.html`);
  await open('education/experiments/index.html');console.log('PASS mobile',width,'25 pages');
 }
 await tab('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await open('education/experiments/03-matter-waves.html');
 await evaluate(`document.querySelector('.qe-lab').scrollIntoView({behavior:'instant',block:'start'});true`);
 await evaluate(`document.querySelector('[data-action=play]').click();new Promise(r=>setTimeout(r,450))`);
 const played=await evaluate(`({n:Number(document.querySelector('.qe-lab').dataset.events),playing:document.querySelector('[data-action=play]').getAttribute('aria-pressed')})`);
 if(!played.n||played.playing!=='true')throw Error('Play failed '+JSON.stringify(played));
 await evaluate(`document.querySelector('[data-action=play]').click();true`);
 const n=await evaluate(`Number(document.querySelector('.qe-lab').dataset.events)`);
 await evaluate('new Promise(r=>setTimeout(r,250))');
 if(n!==await evaluate(`Number(document.querySelector('.qe-lab').dataset.events)`))throw Error('Pause failed');
 await evaluate(`document.querySelector('[data-action=play]').click();document.getElementById('chapter-top').scrollIntoView({behavior:'instant',block:'start'});new Promise(r=>setTimeout(r,600))`);
 if(await evaluate(`document.querySelector('[data-action=play]').getAttribute('aria-pressed')`)!=='false')throw Error('Offscreen pause failed');
 console.log('PASS animation play, pause, and offscreen lifecycle');
 await tab('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
 await open('education/experiments/21-wigners-friend.html');
 const accessible=await evaluate(`(() => {document.getElementById('search-open').click();const q=document.getElementById('book-search');q.value='Wigner';q.dispatchEvent(new Event('input'));const hits=document.querySelectorAll('#search-results li').length;document.getElementById('search-close').click();return {hits,playing:document.querySelector('[data-action=play]').getAttribute('aria-pressed'),message:document.querySelector('.qe-live').textContent};})()`);
 if(!accessible.hits||accessible.playing!=='false'||!accessible.message.includes('Reduced motion'))throw Error(JSON.stringify(accessible));
 await tab('Emulation.setEmulatedMedia',{features:[]});
 // Keyboard arrow input, without mouse-only interactions.
 await evaluate(`document.getElementById('lab-value').focus();true`);
 await tab('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowLeft',code:'ArrowLeft',windowsVirtualKeyCode:37});await tab('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowLeft',code:'ArrowLeft',windowsVirtualKeyCode:37});
 if(await evaluate(`Number(document.getElementById('lab-value').value)`)!==.99)throw Error('Keyboard slider failed');
 console.log('PASS search, reduced-motion default, keyboard controls');
 // Inspect export contents without leaving the local page or submitting data.
 await open('education/experiments/24-investigation.html');
 const csv=await evaluate(`(async()=>{let saved;const old=URL.createObjectURL;URL.createObjectURL=b=>{saved=b;return old(b)};document.querySelector('[data-action=export]').click();return await saved.text();})()`);
 if(!csv.includes('Synthetic educational data')||!csv.includes('phase_degrees,trials,d0,d1')||csv.trim().split('\n').length!==20)throw Error('CSV content failed');
 await writeFile(work+'/synthetic-scan.csv',csv);console.log('PASS CSV download, metadata, and 16 rows');
 for(const [slug,width,theme]of [['index',1440,'light'],['07-interferometer',1440,'light'],['21-wigners-friend',390,'dark'],['18-ghz-contextuality',1440,'dark'],['24-investigation',1440,'light'],['03-matter-waves',390,'light']]){
  await tab('Emulation.setDeviceMetricsOverride',{width,height:1100,deviceScaleFactor:1,mobile:width<500});await open(`education/experiments/${slug}.html`);
  await evaluate(`document.documentElement.dataset.theme=${JSON.stringify(theme)};${slug==='index'?'window.scrollTo(0,0)':'document.querySelector(".qe-lab").scrollIntoView({behavior:"instant",block:"start"})'};true`);
  if(slug==='03-matter-waves')await evaluate(`document.querySelector('[data-action=play]').click();new Promise(r=>setTimeout(r,650))`);
  await evaluate('new Promise(r=>setTimeout(r,150))');
  const {data}=await tab('Page.captureScreenshot',{format:'png'});await writeFile(`${work}/${slug}-${width}-${theme}.png`,Buffer.from(data,'base64'));
 }
 // No-JavaScript fallback: diagrams and text must still be present, dead controls hidden.
 await tab('Emulation.setScriptExecutionDisabled',{value:true});await tab('Page.navigate',{url:pathToFileURL(resolve(root,'education/experiments/21-wigners-friend.html')).href});
 await new Promise(r=>setTimeout(r,300));
 const fallback=await evaluate(`({diagram:!!document.querySelector('svg title'),text:document.querySelector('main').textContent.length,hidden:document.querySelector('.qe-controls').hidden})`);
 if(!fallback.diagram||fallback.text<4000||!fallback.hidden)throw Error('Fallback failed '+JSON.stringify(fallback));
 if(errors.length)throw Error('Browser exceptions: '+JSON.stringify(errors));
 console.log('PASS no-JavaScript fallback. Screenshots:',work);
} finally {if(socket)socket.close();chrome.kill('SIGTERM');}
