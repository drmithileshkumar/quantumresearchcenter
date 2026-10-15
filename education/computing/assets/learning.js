/* Progressive enhancements; definitions and solutions remain native HTML. */
(() => {
 const print=document.querySelector('#print-chapter');
 if(print){print.hidden=false;print.addEventListener('click',()=>window.print());}
 let printState=null;
 addEventListener('beforeprint',()=>{
  if(printState)return;
  printState=[...document.querySelectorAll('main details')].map(el=>[el,el.open]);
  printState.forEach(([el])=>el.open=true);
 });
 addEventListener('afterprint',()=>{printState?.forEach(([el,open])=>el.open=open);printState=null;});
 const query=document.querySelector('#glossary-query'),entries=[...document.querySelectorAll('.glossary-entry')];
 if(query){
  query.closest('.glossary-filter').hidden=false;
  const filter=()=>{const words=query.value.toLowerCase().trim().split(/\s+/);let count=0;entries.forEach(el=>{el.hidden=!words.every(w=>el.textContent.toLowerCase().includes(w));if(!el.hidden)count++});document.querySelector('#glossary-status').textContent=`${count} of ${entries.length} terms`;};
  query.addEventListener('input',filter);filter();
  addEventListener('hashchange',()=>{query.value='';filter();let id;try{id=decodeURIComponent(location.hash.slice(1))}catch{return}document.getElementById(id)?.scrollIntoView();});
 }
 const clear=document.querySelector('#clear-reading-data');
 if(clear){clear.hidden=false;clear.addEventListener('click',()=>{try{localStorage.removeItem('qc-book-size');localStorage.removeItem('qc-book-position');document.querySelector('#reading-data-status').textContent='Saved preferences cleared. Reload to use the default text size.';}catch{document.querySelector('#reading-data-status').textContent='This browser does not allow access to saved preferences.';}});}
})();
