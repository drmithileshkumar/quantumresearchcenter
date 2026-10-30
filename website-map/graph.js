/* A dependency-free force graph. The HTML directory remains usable without canvas. */
(() => {
  const data = JSON.parse(document.getElementById('graph-data').textContent);
  const canvas = document.getElementById('graph-canvas'), ctx = canvas.getContext('2d');
  if (!ctx) return;
  const $ = id => document.getElementById(id);
  const sections = [...new Set(data.nodes.map(n => n.section))].sort();
  const palette = ['#628fd5','#bd7a55','#8b80cd','#479a83','#bf759b','#b69b46','#659faf','#9a876d'];
  const colours = Object.fromEntries(sections.map((s,i) => [s,palette[i % palette.length]]));
  const labels = {home:'Home',education:'Education',research:'Research',news:'News',tools:'Tools',map:'Topic map','website-map':'Website map',references:'References',conferences:'Conferences'};
  sections.forEach(section => {
    const option = new Option(labels[section] || section, section); $('graph-section').append(option);
    const key = document.createElement('span'); key.className = 'graph-key';
    const dot = document.createElement('i'); dot.style.background = colours[section];
    key.append(dot, document.createTextNode(labels[section] || section)); $('graph-legend').append(key);
  });
  const counts = {};
  const nodes = data.nodes.map((node,i) => {
    const group = sections.indexOf(node.section), angle = group / sections.length * Math.PI * 2;
    const k = counts[node.section] = (counts[node.section] || 0) + 1;
    const spiral = k * 2.39996, r = 14 * Math.sqrt(k);
    return {...node, x:Math.cos(angle)*300+Math.cos(spiral)*r, y:Math.sin(angle)*300+Math.sin(spiral)*r, vx:0,vy:0,index:i};
  });
  const byId = new Map(nodes.map(n => [n.id,n]));
  const edges = data.edges.map(e => ({...e,a:byId.get(e.source),b:byId.get(e.target)}));
  let selected = null, hovered = null, visible = nodes, activeEdges = [], neighbours = new Set();
  let width = 1, height = 1, zoom = .65, panX = 0, panY = 0, drag = null, frame = 0;
  let steps = 0, running = true, userView = false;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const theme = () => {
    const s = getComputedStyle(document.body);
    return {ink:s.getPropertyValue('--ink').trim(),muted:s.getPropertyValue('--muted').trim(),line:s.getPropertyValue('--line-strong').trim(),paper:s.getPropertyValue('--paper').trim()};
  };
  let paint = theme();
  function matches(n) {
    const query = $('graph-search').value.trim().toLowerCase();
    return (!$('graph-section').value || n.section === $('graph-section').value) &&
      (!query || `${n.title} ${n.id}`.toLowerCase().includes(query));
  }
  function update() {
    const links = edges.filter(e => $('graph-menus').checked || !e.navigation);
    neighbours = new Set(selected ? [selected.id] : []);
    if (selected) links.forEach(e => {if (e.a===selected) neighbours.add(e.b.id); if(e.b===selected) neighbours.add(e.a.id);});
    visible = nodes.filter(n => matches(n) && (!$('graph-local').checked || !selected || neighbours.has(n.id)));
    const ids = new Set(visible.map(n=>n.id));
    activeEdges = links.filter(e=>ids.has(e.source)&&ids.has(e.target));
    $('graph-status').textContent = `${visible.length} of ${nodes.length} pages · ${activeEdges.length} connections`;
    $('graph-results').replaceChildren();
    if ($('graph-search').value.trim()) {
      visible.slice(0,30).forEach(n=>$('graph-results').append(pageButton(n)));
      if (!visible.length) $('graph-results').textContent='No pages match. Try a different term or section.';
    }
    requestDraw();
  }
  function pageButton(n) {
    const b = document.createElement('button'); b.type='button'; b.textContent=n.title;
    b.addEventListener('click',()=>choose(n,true)); return b;
  }
  function clearSelection() {
    selected=null; hovered=null;
    $('graph-local').checked=false;
    $('detail-title').textContent='Choose a page';
    $('detail-description').textContent='Select a dot to see its connections, or find a page above.';
    $('graph-open').hidden=true; $('graph-open').removeAttribute('href');
    $('graph-neighbours').replaceChildren(); $('graph-tooltip').hidden=true;
    update();
  }
  function resetGraph() {
    $('graph-search').value=''; $('graph-section').value=''; $('graph-menus').checked=false;
    clearSelection(); userView=true; fit();
  }
  function choose(n, center=false) {
    selected=n; update();
    $('detail-title').textContent=n.title;
    $('detail-description').textContent=`${labels[n.section]||n.section} · ${neighbours.size-1} connected pages`;
    $('graph-open').href=n.url; $('graph-open').hidden=false;
    $('graph-neighbours').replaceChildren();
    [...neighbours].filter(id=>id!==n.id).map(id=>byId.get(id)).sort((a,b)=>a.title.localeCompare(b.title)).forEach(other=>{
      const li=document.createElement('li');li.append(pageButton(other));$('graph-neighbours').append(li);
    });
    if (center) {panX=-n.x*zoom;panY=-n.y*zoom;userView=true;}
    requestDraw();
  }
  function fit() {
    if(!visible.length) return;
    const xs=visible.map(n=>n.x),ys=visible.map(n=>n.y);
    const minX=Math.min(...xs)-35,maxX=Math.max(...xs)+35,minY=Math.min(...ys)-35,maxY=Math.max(...ys)+35;
    zoom=Math.max(.15,Math.min(1.8,(width-64)/(maxX-minX),(height-100)/(maxY-minY)));
    panX=-(minX+maxX)/2*zoom;panY=-(minY+maxY)/2*zoom;requestDraw();
  }
  function resize() {
    const rect=canvas.getBoundingClientRect();width=rect.width;height=rect.height;
    const dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);if(!userView)fit();requestDraw();
  }
  function simulate() {
    const cooling=Math.max(.08,1-steps/180);
    // Pairwise repulsion keeps pages distinct; springs use substantive links only.
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
      const a=nodes[i],b=nodes[j],dx=a.x-b.x,dy=a.y-b.y,d2=Math.max(100,dx*dx+dy*dy);
      const f=100*cooling/d2;a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f;
    }
    for(const e of edges){if(e.navigation)continue;const dx=e.b.x-e.a.x,dy=e.b.y-e.a.y,d=Math.hypot(dx,dy)||1,f=(d-65)*.0025*cooling;
      e.a.vx+=dx/d*f;e.a.vy+=dy/d*f;e.b.vx-=dx/d*f;e.b.vy-=dy/d*f;}
    nodes.forEach(n=>{const angle=sections.indexOf(n.section)/sections.length*Math.PI*2;
      n.vx+=(Math.cos(angle)*300-n.x)*.0015;n.vy+=(Math.sin(angle)*300-n.y)*.0015;
      n.vx*=.72;n.vy*=.72;if(!drag||drag.node!==n){n.x+=Math.max(-8,Math.min(8,n.vx));n.y+=Math.max(-8,Math.min(8,n.vy));}
    });steps++;
  }
  function draw() {
    frame=0;
    if(running && !reduced.matches && steps<180){simulate();if(!userView)fit();}
    ctx.clearRect(0,0,width,height);ctx.save();ctx.translate(width/2+panX,height/2+panY);ctx.scale(zoom,zoom);
    ctx.lineWidth=.7/zoom;
    activeEdges.forEach(e=>{const connected=selected&&(e.a===selected||e.b===selected);ctx.strokeStyle=connected?colours[selected.section]:paint.line;ctx.globalAlpha=selected?(connected?.9:.3):.5;ctx.beginPath();ctx.moveTo(e.a.x,e.a.y);ctx.lineTo(e.b.x,e.b.y);ctx.stroke();});
    visible.forEach(n=>{const focus=n===selected||n===hovered;ctx.globalAlpha=selected&&!neighbours.has(n.id)?.6:1;
      const radius=focus?7: n.id.endsWith('/index.html')||n.id==='index.html'?4.5:3;
      ctx.beginPath();ctx.arc(n.x,n.y,radius,0,Math.PI*2);ctx.fillStyle=colours[n.section];ctx.fill();
      if(focus){ctx.strokeStyle=paint.ink;ctx.lineWidth=1.5/zoom;ctx.beginPath();ctx.arc(n.x,n.y,10,0,Math.PI*2);ctx.stroke();}
      if(focus||zoom>1.7||(!selected&&n.id.split('/').length<=2)){
        ctx.font=`${11/zoom}px system-ui`;ctx.fillStyle=paint.ink;const title=n.title.length>44?n.title.slice(0,43)+'…':n.title;ctx.fillText(title,n.x+10,n.y+3/zoom);
      }
    });ctx.restore();ctx.globalAlpha=1;
    if(running&&!reduced.matches&&steps<180)requestDraw();
  }
  function requestDraw(){if(!frame)frame=requestAnimationFrame(draw);}
  function point(e){const r=canvas.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top};}
  function hit(p){const x=(p.x-width/2-panX)/zoom,y=(p.y-height/2-panY)/zoom;let best=null,distance=12/zoom;
    visible.forEach(n=>{const d=Math.hypot(n.x-x,n.y-y);if(d<distance){best=n;distance=d;}});return best;}
  canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;canvas.focus();const p=point(e);drag={...p,startX:p.x,startY:p.y,node:hit(p),moved:false};canvas.setPointerCapture(e.pointerId);userView=true;});
  canvas.addEventListener('pointermove',e=>{const p=point(e);if(drag){const dx=p.x-drag.x,dy=p.y-drag.y;drag.moved ||=Math.hypot(p.x-drag.startX,p.y-drag.startY)>4;
    if(drag.node){drag.node.x+=dx/zoom;drag.node.y+=dy/zoom;}else{panX+=dx;panY+=dy;}drag.x=p.x;drag.y=p.y;
  }else{hovered=hit(p);$('graph-tooltip').hidden=!hovered;if(hovered)$('graph-tooltip').textContent=hovered.title;canvas.style.cursor=hovered?'pointer':'grab';}requestDraw();});
  canvas.addEventListener('pointerup',()=>{if(drag&&!drag.moved){if(drag.node && drag.node!==selected)choose(drag.node);else clearSelection();}drag=null;});
  canvas.addEventListener('pointercancel',()=>{drag=null;});
  canvas.addEventListener('lostpointercapture',()=>{drag=null;});
  canvas.addEventListener('pointerleave',()=>{hovered=null;$('graph-tooltip').hidden=true;requestDraw();});
  function scale(f,p={x:width/2,y:height/2}){const next=Math.max(.12,Math.min(6,zoom*f)),ratio=next/zoom;panX=(panX+width/2-p.x)*ratio+p.x-width/2;panY=(panY+height/2-p.y)*ratio+p.y-height/2;zoom=next;userView=true;requestDraw();}
  canvas.addEventListener('wheel',e=>{e.preventDefault();scale(Math.exp(-e.deltaY*.001),point(e));},{passive:false});
  canvas.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'].includes(e.key))e.preventDefault();else return;
    userView=true;if(e.key==='Home')fit();else if(e.key==='+'||e.key==='=')scale(1.2);else if(e.key==='-')scale(1/1.2);else{panX+=e.key==='ArrowLeft'?40:e.key==='ArrowRight'?-40:0;panY+=e.key==='ArrowUp'?40:e.key==='ArrowDown'?-40:0;requestDraw();}});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){clearSelection();}});
  $('graph-reset').addEventListener('click',resetGraph);
  $('graph-zoom-in').addEventListener('click',()=>scale(1.25));$('graph-zoom-out').addEventListener('click',()=>scale(.8));$('graph-fit').addEventListener('click',()=>{userView=true;fit();});
  ['graph-search','graph-section','graph-menus','graph-local'].forEach(id=>$(id).addEventListener(id==='graph-search'?'input':'change',()=>{update();if(selected)choose(selected);userView=true;fit();}));
  new MutationObserver(()=>{paint=theme();requestDraw();}).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
  reduced.addEventListener('change',requestDraw);
  document.addEventListener('visibilitychange',()=>{running=!document.hidden;if(running)requestDraw();});
  new ResizeObserver(resize).observe(canvas);
  update();resize();
})();
