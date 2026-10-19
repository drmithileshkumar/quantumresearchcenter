/* Navigation and experiment lifecycle for a continuously scrolling book. */
(() => {
  document.documentElement.classList.add('book-js');
  const storage={get(k){try{return localStorage.getItem(k)}catch{return null}},set(k,v){try{localStorage.setItem(k,v)}catch{}}};
  let size=Number(storage.get('qi-book-size'))||parseFloat(getComputedStyle(document.body).fontSize)||17;
  function setSize(n){size=Math.max(16,Math.min(26,n));document.documentElement.style.setProperty('--book-text-size',size+'px');storage.set('qi-book-size',size);document.querySelector('#text-smaller').disabled=size===16;document.querySelector('#text-larger').disabled=size===26;}
  if(storage.get('qi-book-size'))setSize(size);
  document.querySelector('#text-smaller').onclick=()=>setSize(size-1);
  document.querySelector('#text-larger').onclick=()=>setSize(size+1);
  const menu=document.querySelector('#menu-toggle'),scrim=document.querySelector('#nav-scrim'),sidebar=document.querySelector('#book-navigation');
  const narrow=matchMedia('(max-width:800px)');
  function syncNav(){sidebar.inert=narrow.matches&&!document.body.classList.contains('contents-open')}
  narrow.addEventListener('change',syncNav);syncNav();
  function toggle(open){document.body.classList.toggle('contents-open',open);menu.setAttribute('aria-expanded',String(open));scrim.hidden=!open;syncNav();if(open)sidebar.querySelector('a').focus();}
  menu.onclick=()=>toggle(!document.body.classList.contains('contents-open'));scrim.onclick=()=>{toggle(false);menu.focus()};
  sidebar.addEventListener('click',e=>{if(e.target.closest('a')&&innerWidth<=800)toggle(false)});
  const dialog=document.querySelector('#search-dialog'),input=document.querySelector('#book-search'),results=document.querySelector('#search-results'),status=document.querySelector('#search-status');
  function openSearch(){dialog.showModal();input.focus()}
  document.querySelector('#search-open').onclick=openSearch;document.querySelector('#search-close').onclick=()=>dialog.close();
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){toggle(false)}if(e.key==='/'&&!e.target.closest('input,textarea,select,[contenteditable]')){e.preventDefault();if(!dialog.open)openSearch()}});
  input.addEventListener('input',()=>{
    const query=input.value.trim().toLowerCase(),words=query.split(/\s+/);results.replaceChildren();
    if(!query){status.textContent='Search the course.';return}
    const hits=(window.BOOK_SEARCH||[]).filter(x=>words.every(w=>(x.title+' '+x.text).toLowerCase().includes(w))).sort((a,b)=>Number(b.title.toLowerCase().includes(query))-Number(a.title.toLowerCase().includes(query)));
    status.textContent=hits.length?`${hits.length} matching sections${hits.length>30?' · showing the first 30':''}.`:'No matching sections. Try a shorter phrase.';
    hits.slice(0,30).forEach(hit=>{const li=document.createElement('li'),a=document.createElement('a'),small=document.createElement('small'),p=document.createElement('p');a.href=hit.url;a.textContent=hit.title;a.onclick=()=>dialog.close();small.textContent=hit.chapter;const pos=hit.text.toLowerCase().indexOf(words[0]);p.textContent=(pos>70?'…':'')+hit.text.slice(Math.max(0,pos-60),Math.max(0,pos-60)+170)+'…';li.append(a,small,p);results.append(li)});
  });
  const chapter=document.body.dataset.chapter,sections=[...document.querySelectorAll('.book-section')];
  const resume=document.querySelector('#resume-reading');
  if(resume){try{const saved=JSON.parse(storage.get('qi-book-position'));if(saved&&[...sidebar.querySelectorAll('a[data-topic]')].some(a=>a.getAttribute('href')===saved.url)){resume.href=saved.url;resume.hidden=false}}catch{}}
  const links=[...sidebar.querySelectorAll(`a[href^="${chapter}.html#"]`)];let selected=null,scheduled=false;
  function track(){scheduled=false;if(!sections.length)return;let current=sections[0];for(const s of sections){if(s.getBoundingClientRect().top<=150)current=s;else break}if(current===selected)return;selected=current;links.forEach(a=>{const active=a.dataset.topic===current.id;if(active){a.setAttribute('aria-current','location');const r=a.getBoundingClientRect(),nr=sidebar.getBoundingClientRect();if(r.bottom>nr.bottom-30)sidebar.scrollTop+=r.bottom-nr.bottom+45;else if(r.top<nr.top+15)sidebar.scrollTop+=r.top-nr.top-30;}else a.removeAttribute('aria-current')});storage.set('qi-book-position',JSON.stringify({url:chapter+'.html#'+current.id}));}
  addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(track)}},{passive:true});track();
  // Reuse the demos' pause-on-exit hooks without hiding any reading content.
  if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{entries.forEach(({target,isIntersecting})=>target.dispatchEvent(new CustomEvent(isIntersecting?'slideenter':'slideleave',{bubbles:true})))},{rootMargin:'0px',threshold:0});sections.filter(s=>s.querySelector('button,input,select')).forEach(s=>observer.observe(s));}
  function followHash(){if(!location.hash)return;let id;try{id=decodeURIComponent(location.hash.slice(1))}catch{return}const el=document.getElementById(id);if(el){for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;el.scrollIntoView({behavior:'instant',block:'start'});}track()}
  addEventListener('hashchange',followHash);
  if(window.MathJax?.startup?.promise)MathJax.startup.promise.then(followHash);else addEventListener('load',followHash);
  const printButton=document.querySelector('#print-chapter');
  if(printButton){printButton.hidden=false;printButton.onclick=()=>window.print()}
  let printDetails=null;
  function expandForPrint(){
    if(printDetails)return;
    printDetails=[...document.querySelectorAll('main details')].map(el=>[el,el.open]);
    printDetails.forEach(([el])=>{el.open=true});
  }
  function restoreAfterPrint(){
    if(!printDetails)return;
    printDetails.forEach(([el,open])=>{el.open=open});printDetails=null;
  }
  addEventListener('beforeprint',expandForPrint);
  addEventListener('afterprint',restoreAfterPrint);
})();
