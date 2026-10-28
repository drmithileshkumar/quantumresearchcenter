(() => {
  'use strict';
  const nodes = JSON.parse(document.getElementById('topic-data').textContent);
  const byId = new Map(nodes.map(n => [n.id, n]));
  const root = nodes[0];
  nodes.forEach(n => { n.children = []; n.depth = n.parent ? byId.get(n.parent).depth + 1 : 0; });
  nodes.forEach(n => { if (n.parent) byId.get(n.parent).children.push(n); });
  const fields = root.children;
  const tokens = ['--violet', '--blue', '--topic-information', '--warm', '--subsection-heading', '--section-heading'];
  const search = document.getElementById('search'), branch = document.getElementById('branch'), depth = document.getElementById('depth');
  const canvas = document.getElementById('graph'), ctx = canvas.getContext('2d');
  let selected = root, visible = nodes, visibleIds = new Set(nodes.map(n => n.id));
  let width = 1, height = 1, scale = 1, offsetX = 0, offsetY = 0, pointer = null, hovered = null;
  let colors, ink, line, paper;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function palette() {
    const css = getComputedStyle(document.documentElement);
    colors = fields.map((_, i) => css.getPropertyValue(tokens[i]).trim());
    ink = css.getPropertyValue('--ink').trim(); line = css.getPropertyValue('--line-strong').trim(); paper = css.getPropertyValue('--paper').trim();
  }
  function color(n) { return n === root ? ink : colors[fields.findIndex(f => f.label === n.branch)]; }
  function weight(n) { return n.children.length ? n.children.reduce((sum, child) => sum + weight(child), 0) : 1; }
  function place(n, start, end) {
    const angle = (start + end) / 2;
    const radius = [0, 260, 550, 850][n.depth] + (n.depth === 3 ? (nodes.indexOf(n) % 3) * 70 : 0);
    n.x = Math.cos(angle) * radius; n.y = Math.sin(angle) * radius;
    n.ax = n.x; n.ay = n.y;
    let cursor = start;
    n.children.forEach(child => { const span = (end - start) * weight(child) / weight(n); place(child, cursor, cursor + span); cursor += span; });
  }
  place(root, -Math.PI, Math.PI);
  // Relax the radial seed into a network while keeping each field near its sector.
  for (let step = 0; step < 100; step++) {
    nodes.forEach(n => { n.fx = (n.ax - n.x) * .012; n.fy = (n.ay - n.y) * .012; });
    for (let i = 1; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j], dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + 1;
        if (d2 > 60000) continue;
        const force = Math.min(1.5, 420 / d2), d = Math.sqrt(d2);
        a.fx += dx / d * force; a.fy += dy / d * force; b.fx -= dx / d * force; b.fy -= dy / d * force;
      }
    }
    nodes.slice(1).forEach(n => { const p = byId.get(n.parent), dx = p.x - n.x, dy = p.y - n.y, d = Math.hypot(dx, dy) || 1;
      const force = (d - (n.depth === 3 ? 95 : 235)) * .025;
      n.fx += dx / d * force; n.fy += dy / d * force;
      if (p !== root) { p.fx -= dx / d * force; p.fy -= dy / d * force; }
    });
    nodes.slice(1).forEach(n => { n.x += n.fx; n.y += n.fy; });
  }
  function topicButton(n) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'topic-link'; button.textContent = n.label;
    button.addEventListener('click', () => reveal(n)); return button;
  }
  function select(n, updateHash = true) {
    selected = n;
    if (updateHash) history.replaceState(null, '', '#' + n.id);
    const detail = document.getElementById('detail'); detail.replaceChildren();
    const tag = document.createElement('div'); tag.className = 'selected-label'; tag.textContent = n.depth ? 'Selected topic' : 'Start exploring'; detail.append(tag);
    const title = document.createElement('h2'); title.textContent = n.label; detail.append(title);
    const description = document.createElement('p'); description.textContent = n.description; detail.append(description);
    if (n.parent) {
      const ancestors = []; let p = byId.get(n.parent);
      while (p) { ancestors.unshift(p.label); p = byId.get(p.parent); }
      const crumb = document.createElement('p'); crumb.className = 'crumb'; crumb.textContent = ancestors.join(' / '); detail.append(crumb);
      const heading = document.createElement('h3'); heading.textContent = 'Parent topic'; detail.append(heading, topicButton(byId.get(n.parent)));
    }
    const heading = document.createElement('h3'); heading.textContent = `Child topics · ${n.children.length}`; detail.append(heading);
    if (n.children.length) n.children.forEach(child => detail.append(topicButton(child)));
    else { const note = document.createElement('p'); note.textContent = 'This keyword is a leaf in the current map. Explore its parent for neighboring ideas.'; detail.append(note); }
    const course = {'Quantum mechanics': 'foundations', 'Quantum computing': 'computing', 'Quantum information': 'information', 'Quantum communication': 'cryptography', 'Quantum technology': 'hardware'}[n.branch];
    if (course) { const link = document.createElement('a'); link.href = `../education/${course}/index.html`; link.textContent = 'Explore the related course ↗'; detail.append(link); }
    draw();
  }
  function reveal(n) {
    if (branch.value && n.branch !== branch.value) branch.value = '';
    if (Number(depth.value) < n.depth) depth.value = String(n.depth);
    update(false); select(n); scale = Math.max(scale, .9); offsetX = width / 2 - n.x * scale; offsetY = height / 2 - n.y * scale; draw();
  }
  fields.forEach((n, i) => {
    const option = document.createElement('option'); option.value = n.label; option.textContent = n.label; branch.append(option);
    const button = document.createElement('button'); button.type = 'button';
    const dot = document.createElement('span'); dot.className = 'swatch'; dot.style.setProperty('--dot', `var(${tokens[i]})`); button.append(dot, document.createTextNode(n.label));
    button.addEventListener('click', () => { branch.value = n.label; update(); select(n); }); document.getElementById('legend').append(button);
  });
  function update(refit = true) {
    visible = nodes.filter(n => n.depth <= Number(depth.value) && (!branch.value || n === root || n.branch === branch.value));
    visibleIds = new Set(visible.map(n => n.id));
    const query = search.value.trim().toLocaleLowerCase();
    const matches = visible.filter(n => n.label.toLocaleLowerCase().includes(query));
    const results = document.getElementById('results'); results.replaceChildren();
    if (query) matches.forEach(n => results.append(topicButton(n)));
    document.getElementById('results-status').textContent = query ? `${matches.length} matching topics` : `${visible.length} topics in view`;
    document.getElementById('map-count').textContent = `${nodes.length} topics / ${nodes.length - 1} connections`;
    if (!visibleIds.has(selected.id)) select(branch.value ? fields.find(n => n.label === branch.value) : root);
    if (refit) fit(); else draw();
  }
  function fit() {
    const xs = visible.map(n => n.x), ys = visible.map(n => n.y);
    const left = Math.min(...xs) - 100, right = Math.max(...xs) + 100, top = Math.min(...ys) - 100, bottom = Math.max(...ys) + 100;
    scale = Math.min((width - 40) / (right - left), (height - 110) / (bottom - top), 2);
    offsetX = width / 2 - (left + right) / 2 * scale; offsetY = height / 2 - (top + bottom) / 2 * scale; draw();
  }
  function draw() {
    if (!colors) return;
    ctx.clearRect(0, 0, width, height);
    const query = search.value.trim().toLocaleLowerCase();
    const related = n => n === selected || n.parent === selected.id || selected.parent === n.id;
    const point = n => [n.x * scale + offsetX, n.y * scale + offsetY];
    visible.forEach(n => {
      if (!n.parent || !visibleIds.has(n.parent)) return;
      const p = byId.get(n.parent), [x, y] = point(n), [px, py] = point(p), active = n === selected || p === selected;
      ctx.globalAlpha = active ? .8 : .35; ctx.strokeStyle = active ? color(n) : line; ctx.lineWidth = active ? 1.5 : .8;
      ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(x, y); ctx.stroke();
      if (active) { const a = Math.atan2(y - py, x - px), mx = px + (x - px) * .65, my = py + (y - py) * .65;
        ctx.beginPath(); ctx.moveTo(mx - Math.cos(a - .5) * 6, my - Math.sin(a - .5) * 6); ctx.lineTo(mx, my); ctx.lineTo(mx - Math.cos(a + .5) * 6, my - Math.sin(a + .5) * 6); ctx.stroke(); }
    });
    visible.forEach(n => {
      const [x, y] = point(n), match = query && n.label.toLocaleLowerCase().includes(query), active = related(n) || n === hovered || match;
      const radius = n.depth === 0 ? 8 : n.depth === 1 ? 6 : n.depth === 2 ? 4 : 2.7;
      ctx.globalAlpha = query && !match && !related(n) ? .18 : .9;
      ctx.fillStyle = color(n); ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
      if (n === selected || n === hovered) { ctx.strokeStyle = color(n); ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(x, y, radius + 5, 0, Math.PI * 2); ctx.stroke(); }
      if (n.depth < 2 || active || (scale > .65 && n.depth < 3) || scale > 1.35) {
        ctx.font = `${n.depth < 2 ? '600 ' : ''}${n.depth < 2 ? 12 : 10}px system-ui`;
        ctx.lineWidth = 4; ctx.strokeStyle = paper; ctx.strokeText(n.label, x + radius + 7, y + 4);
        ctx.fillStyle = active || n.depth < 2 ? ink : color(n); ctx.fillText(n.label, x + radius + 7, y + 4);
      }
    }); ctx.globalAlpha = 1;
  }
  function zoom(factor, x = width / 2, y = height / 2) {
    const next = Math.max(.08, Math.min(4, scale * factor));
    offsetX = x - (x - offsetX) * next / scale; offsetY = y - (y - offsetY) * next / scale; scale = next; draw();
  }
  function coordinates(event) { const rect = canvas.getBoundingClientRect(); return {x: event.clientX - rect.left, y: event.clientY - rect.top}; }
  function hit(p) { return [...visible].reverse().find(n => Math.hypot(n.x * scale + offsetX - p.x, n.y * scale + offsetY - p.y) < 12); }
  canvas.addEventListener('pointerdown', e => { const p = coordinates(e); pointer = {...p, startX: p.x, startY: p.y, node: hit(p), moved: false, id: e.pointerId}; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', e => {
    const p = coordinates(e);
    if (pointer && pointer.id === e.pointerId) {
      if (Math.hypot(p.x - pointer.startX, p.y - pointer.startY) > 4) pointer.moved = true;
      if (pointer.moved) {
        if (pointer.node) { pointer.node.x += (p.x - pointer.x) / scale; pointer.node.y += (p.y - pointer.y) / scale; }
        else { offsetX += p.x - pointer.x; offsetY += p.y - pointer.y; }
      } pointer.x = p.x; pointer.y = p.y;
    } else { hovered = hit(p); canvas.style.cursor = hovered ? 'pointer' : 'grab'; }
    draw();
  });
  canvas.addEventListener('pointerup', e => { if (pointer && pointer.id === e.pointerId && !pointer.moved && pointer.node) select(pointer.node); pointer = null; });
  canvas.addEventListener('pointercancel', () => { pointer = null; });
  canvas.addEventListener('pointerleave', () => { hovered = null; draw(); });
  canvas.addEventListener('wheel', e => { e.preventDefault(); const p = coordinates(e); zoom(Math.exp(-e.deltaY * .001), p.x, p.y); }, {passive: false});
  canvas.addEventListener('keydown', e => {
    if (e.key === '+' || e.key === '=') zoom(1.25); else if (e.key === '-') zoom(.8);
    else if (e.key === 'ArrowLeft') offsetX += 40; else if (e.key === 'ArrowRight') offsetX -= 40;
    else if (e.key === 'ArrowUp') offsetY += 40; else if (e.key === 'ArrowDown') offsetY -= 40;
    else if (e.key === 'Home') fit(); else return;
    e.preventDefault(); draw();
  });
  document.getElementById('zoom-in').addEventListener('click', () => zoom(1.25));
  document.getElementById('zoom-out').addEventListener('click', () => zoom(.8));
  document.getElementById('fit').addEventListener('click', fit);
  search.addEventListener('input', () => update(false)); branch.addEventListener('change', () => update()); depth.addEventListener('change', () => update());
  document.querySelectorAll('[data-topic]').forEach(link => link.addEventListener('click', e => { e.preventDefault(); reveal(byId.get(link.dataset.topic)); canvas.scrollIntoView({block: 'center', behavior: reduced ? 'instant' : 'smooth'}); }));
  new MutationObserver(() => { palette(); draw(); }).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
  new ResizeObserver(() => { const rect = canvas.getBoundingClientRect(); width = rect.width; height = rect.height;
    const dpr = Math.min(devicePixelRatio || 1, 2); canvas.width = width * dpr; canvas.height = height * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); fit();
  }).observe(canvas);
  document.querySelector('[data-theme-toggle]').addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('qrc-theme', theme); } catch {}
    const button = document.querySelector('[data-theme-toggle]');
    button.setAttribute('aria-pressed', String(theme === 'dark'));
    button.title = theme === 'dark' ? 'Switch to light appearance' : 'Switch to dark appearance';
  });
  palette(); update(); select(byId.get(location.hash.slice(1)) || root, false);
  window.addEventListener('hashchange', () => { const n = byId.get(location.hash.slice(1)); if (n) reveal(n); });
})();
