// Optional browser verification. Requires Node with WebSocket and Google Chrome.
// Only opens local course files. Screenshots and browser profile go under /tmp.
import {spawn} from 'node:child_process';
import {readFile, writeFile, mkdtemp} from 'node:fs/promises';
import {resolve, dirname} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {tmpdir} from 'node:os';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const courses=process.argv.slice(2).length?process.argv.slice(2):['algorithms','programming','information','hardware'];
if(courses.some(c=>!['algorithms','programming','information','hardware'].includes(c)))throw Error('Unknown course');
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
 for(const course of courses){
  const chapters=JSON.parse(await readFile(resolve(root,`education/${course}/chapters.json`),'utf8'));
  for(const c of chapters){const result=await open(`education/${course}/${c.stem}.html`);console.log('PASS',course,c.stem,`(${result.math} math expressions)`);}
 }
 await tab('Emulation.setDeviceMetricsOverride',{width:390,height:1000,deviceScaleFactor:1,mobile:true});
 for(const course of courses){
  const chapters=JSON.parse(await readFile(resolve(root,`education/${course}/chapters.json`),'utf8'));
  for(const c of chapters){await open(`education/${course}/${c.stem}.html`);}
  console.log('PASS mobile',course,chapters.length,'chapters');
 }
 for(const [name,file,anchor,width] of [
  ['algorithms','education/algorithms/04-fourier-methods.html','section-4-1',1440],
  ['programming','education/programming/06-sampling-and-estimation.html','section-6-3',1440],
  ['information','education/information/08-state-discrimination.html','section-8-2',1440],
  ['mobile','education/information/10-entanglement-protocols.html','section-10-1',390],
  ['hardware','education/hardware/03-coherent-control.html','section-3-1',1440],
  ['hardware-mobile','education/hardware/18-fault-tolerant-hardware.html','section-18-1',390]]){
  if(!courses.some(c=>file.includes('/'+c+'/')))continue;
  await tab('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width<500});
  await open(file);await evaluate(`document.getElementById(${JSON.stringify(anchor)}).scrollIntoView();true`);
  await evaluate('new Promise(resolve=>setTimeout(resolve,500))');
  const {data}=await tab('Page.captureScreenshot',{format:'png'});
  await writeFile(`${work}/${name}.png`,Buffer.from(data,'base64'));
 }
 console.log('Browser checks passed. Screenshots:',work);
} finally {
 if(socket)socket.close();chrome.kill('SIGTERM');
}
