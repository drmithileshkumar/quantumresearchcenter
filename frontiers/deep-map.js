(() => {
  const data = JSON.parse(document.getElementById('frontier-data').textContent);
  const byId = Object.fromEntries(data.nodes.map(n => [n.id, n]));
  const kids = {};
  for (const n of data.nodes) if (n.parent) (kids[n.parent] ||= []).push(n);
  const svg = document.getElementById('frontier');
  const detail = document.getElementById('detail');
  const search = document.getElementById('search');
  const view = document.getElementById('view');
  const ROW = 27, GROUP_GAP = 8, COLUMN = 215, PADDING = 24, SVG = 'http://www.w3.org/2000/svg';
  const hasKids = id => (kids[id] || []).length > 0;
  const expanded = new Set([data.id, ...kids[data.id].map(n => n.id)]);
  let current = null, place = {}, full = {x: 0, y: 0, w: 1, h: 1}, box = null;

  const element = (tag, props = {}, ...children) => {
    const el = Object.assign(document.createElement(tag), props);
    el.append(...children);
    return el;
  };
  const ancestors = id => {
    const chain = [];
    for (let at = byId[id].parent; at; at = byId[at].parent) chain.push(at);
    return chain;
  };
  const descendants = id => (kids[id] || []).flatMap(n => [n, ...descendants(n.id)]);

  function matches() {
    const query = search.value.trim().toLowerCase();
    if (!query && view.value === 'all') return null;
    return new Set(data.nodes.filter(n => (view.value === 'all' || data.frontier.includes(n.status))
      && (!query || `${n.title} ${n.label} ${n.statement}`.toLowerCase().includes(query))).map(n => n.id));
  }

  // The root sits at the origin and each top-level branch alternates sides, so a node keeps its side when others open.
  function layout() {
    place = {};
    const rows = id => expanded.has(id) && hasKids(id) ? kids[id].reduce((sum, n) => sum + rows(n.id), 0) + (kids[id].length - 1) * GROUP_GAP / ROW : 1;
    const put = (id, depth, side, top) => {
      const height = rows(id) * ROW;
      place[id] = {x: side * depth * COLUMN, y: top + height / 2, side};
      if (!expanded.has(id) || !hasKids(id)) return;
      let y = top;
      for (const n of kids[id]) {
        put(n.id, depth + 1, side, y);
        y += rows(n.id) * ROW + GROUP_GAP;
      }
    };
    const branches = kids[data.id];
    for (const side of [1, -1]) {
      const group = branches.filter((_, i) => (i % 2 === 0) === (side === 1));
      const total = group.reduce((sum, n) => sum + rows(n.id) * ROW + GROUP_GAP * 2, 0);
      let y = -total / 2;
      for (const n of group) {
        put(n.id, 1, side, y);
        y += rows(n.id) * ROW + GROUP_GAP * 2;
      }
    }
    place[data.id] = {x: 0, y: 0, side: 0};
  }

  const curve = (a, b) => {
    const mid = (a.x + b.x) / 2;
    return `M${a.x} ${a.y}C${mid} ${a.y} ${mid} ${b.y} ${b.x} ${b.y}`;
  };
  const svgNode = (tag, attrs = {}) => {
    const el = document.createElementNS(SVG, tag);
    for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
    return el;
  };

  function draw() {
    layout();
    const shown = matches();
    const focused = document.activeElement?.closest?.('.node')?.dataset.id;
    const parts = [];
    const isDim = id => shown && !shown.has(id) && !(shown.size && [...shown].some(m => ancestors(m).includes(id)));
    for (const id of Object.keys(place)) {
      const n = byId[id];
      if (n.parent) parts.push(svgNode('path', {class: `edge${isDim(id) ? ' dim' : ''}`, d: curve(place[n.parent], place[id])}));
    }
    const selectedLinks = current ? [...(byId[current].links || []).map(l => l.to), ...data.nodes.filter(n => (n.links || []).some(l => l.to === current)).map(n => n.id)] : [];
    for (const to of selectedLinks) if (place[to] && place[current]) parts.push(svgNode('path', {class: 'cross-link', d: curve(place[current], place[to])}));
    for (const [id, p] of Object.entries(place)) {
      const n = byId[id];
      const topic = n.kind === 'topic';
      const open = expanded.has(id);
      const above = id === data.id || (hasKids(id) && open);
      const kind = id === data.id ? 'root n-topic' : topic ? 'topic' : n.status;
      const classes = ['node', `n-${kind}`];
      if (data.frontier.includes(n.status)) classes.push('frontier');
      if (id === current) classes.push('selected');
      if (selectedLinks.includes(id)) classes.push('connected');
      if (isDim(id)) classes.push('dim');
      const a = svgNode('a', {class: classes.join(' '), href: `#${id}`, 'data-id': id, transform: `translate(${p.x} ${p.y})`});
      const title = svgNode('title');
      title.textContent = n.title + (n.status ? ` (${data.statuses[n.status]})` : '') + (hasKids(id) ? (open ? '. Open: select to fold.' : '. Folded: select to open.') : '');
      a.append(title, svgNode('circle', {class: 'hit', r: 13}));
      const mark = svgNode('g');
      if (topic) mark.append(svgNode('circle', {class: open || id === data.id ? 'g-topic' : 'g-branch', r: id === data.id ? 10 : 7}));
      else mark.innerHTML = data.glyphs[n.status];
      a.append(mark);
      const right = p.side >= 0;
      const text = svgNode('text', above ? {x: 0, y: id === data.id ? -18 : -13, 'text-anchor': 'middle'} : {x: right ? 15 : -15, y: 4, 'text-anchor': right ? 'start' : 'end'});
      text.textContent = n.label;
      if (hasKids(id) && !open) {
        const inside = descendants(id);
        const count = svgNode('tspan', {class: 'count', dx: 6});
        count.textContent = `${inside.length}`;
        text.append(count);
        const openCount = inside.filter(x => data.frontier.includes(x.status)).length;
        if (openCount) {
          const flag = svgNode('tspan', {class: 'count count-frontier', dx: 4});
          flag.textContent = `· ${openCount} frontier`;
          text.append(flag);
        }
      }
      a.append(text);
      parts.push(a);
    }
    svg.replaceChildren(...parts);
    // Labels vary in length, so measure the drawing instead of estimating its margins.
    const bounds = svg.getBBox();
    full = {x: bounds.x - PADDING, y: bounds.y - PADDING, w: bounds.width + PADDING * 2, h: bounds.height + PADDING * 2};
    if (focused) svg.querySelector(`[data-id="${CSS.escape(focused)}"]`)?.focus({preventScroll: true});
    const status = document.getElementById('view-status');
    status.textContent = shown ? `${[...shown].filter(id => byId[id].kind !== 'topic').length} shown` : '';
  }

  // Pan and zoom move the viewBox, so the map stays sharp at every scale.
  const paint = () => svg.setAttribute('viewBox', `${box.x} ${box.y} ${box.w} ${box.h}`);
  const fit = () => { box = {...full}; paint(); };
  const reveal = id => {
    const {x, y} = place[id];
    if (x > box.x + box.w * .1 && x < box.x + box.w * .9 && y > box.y + box.h * .1 && y < box.y + box.h * .9) return;
    box.x = x - box.w / 2;
    box.y = y - box.h / 2;
    paint();
  };
  const closeUp = id => {
    const {x, y} = place[id], w = 520, h = w * svg.clientHeight / svg.clientWidth;
    box = {x: x - w / 2, y: y - h / 2, w, h};
    paint();
  };
  const zoom = (factor, cx = box.x + box.w / 2, cy = box.y + box.h / 2) => {
    const w = Math.min(full.w * 2, Math.max(120, box.w * factor)), scale = w / box.w;
    box = {x: cx - (cx - box.x) * scale, y: cy - (cy - box.y) * scale, w, h: box.h * scale};
    paint();
  };
  const toMap = e => {
    const point = new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse());
    return [point.x, point.y];
  };
  // Opening a branch moves its siblings, so hold the chosen node still on screen.
  const redrawHolding = id => {
    const before = place[id];
    draw();
    const after = place[id];
    if (before && after) { box.x += after.x - before.x; box.y += after.y - before.y; paint(); }
  };

  function renderDetail(id) {
    const n = byId[id];
    const jump = to => {
      const button = element('button', {type: 'button', className: 'jump', textContent: byId[to].title});
      button.addEventListener('click', () => { location.hash = to; });
      return button;
    };
    const parts = [element('p', {className: 'kicker', textContent: n.status ? data.statuses[n.status] : 'Topic'}), element('h2', {textContent: n.title}), element('p', {textContent: n.statement})];
    if (n.unknown) parts.push(element('h3', {textContent: 'Still unknown'}), element('p', {className: 'unknown', textContent: n.unknown}));
    const rows = [];
    if (n.parent) rows.push(['Part of', n.parent]);
    for (const link of n.links || []) rows.push([data.relations[link.rel][0], link.to]);
    for (const other of data.nodes) {
      if (other.parent === id) rows.push(['Includes', other.id]);
      for (const link of other.links || []) if (link.to === id) rows.push([data.relations[link.rel][1], other.id]);
    }
    if (rows.length) parts.push(element('h3', {textContent: 'Connections'}), element('ul', {}, ...rows.map(([word, to]) => element('li', {}, element('small', {textContent: word}), jump(to)))));
    if (n.map?.length) parts.push(element('h3', {textContent: 'On the frontier map'}), element('ul', {}, ...n.map.map(to => element('li', {}, element('a', {href: `../${to}/index.html`, textContent: data.mapTitles[to]})))));
    parts.push(element('h3', {textContent: 'Sources'}), element('ul', {}, ...n.sources.map(key => {
      const p = data.papers[key];
      return element('li', {}, element('a', {href: p.url, textContent: p.title}), element('small', {textContent: `${p.authors}, ${p.year}`}));
    })));
    detail.replaceChildren(...parts);
    detail.scrollTop = 0;
  }

  function select(id) {
    current = id;
    ancestors(id).forEach(a => expanded.add(a));
    redrawHolding(id);
    renderDetail(id);
    reveal(id);
  }

  function applyFilter() {
    const shown = matches();
    if (shown) for (const id of shown) ancestors(id).forEach(a => expanded.add(a));
    draw();
    fit();
  }

  svg.addEventListener('wheel', e => { e.preventDefault(); zoom(e.deltaY > 0 ? 1.12 : 1 / 1.12, ...toMap(e)); }, {passive: false});
  let drag = null, moved = false;
  svg.addEventListener('pointerdown', e => { if (e.button === 0) { drag = {start: toMap(e), id: e.pointerId, x: e.clientX, y: e.clientY}; moved = false; } });
  svg.addEventListener('pointermove', e => {
    if (!drag) return;
    if (!moved && Math.hypot(e.clientX - drag.x, e.clientY - drag.y) < 5) return;
    if (!moved) { moved = true; svg.setPointerCapture(drag.id); svg.classList.add('dragging'); }
    const [x, y] = toMap(e);
    box.x -= x - drag.start[0];
    box.y -= y - drag.start[1];
    paint();
  });
  const endDrag = () => { drag = null; svg.classList.remove('dragging'); };
  svg.addEventListener('pointerup', endDrag);
  svg.addEventListener('pointercancel', endDrag);
  svg.addEventListener('click', e => {
    const node = e.target.closest('.node');
    if (!node) return;
    e.preventDefault();
    if (moved) { moved = false; return; }
    const id = node.dataset.id;
    if (hasKids(id) && id !== data.id) {
      if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
      redrawHolding(id);
    }
    if (location.hash === `#${id}`) select(id); else location.hash = id;
  });
  document.getElementById('zoom-in').addEventListener('click', () => zoom(1 / 1.3));
  document.getElementById('zoom-out').addEventListener('click', () => zoom(1.3));
  document.getElementById('fit').addEventListener('click', fit);
  document.getElementById('expand-all').addEventListener('click', () => { data.nodes.forEach(n => expanded.add(n.id)); draw(); fit(); });
  document.getElementById('collapse-all').addEventListener('click', () => {
    expanded.clear();
    expanded.add(data.id);
    if (current) ancestors(current).forEach(a => expanded.add(a));
    draw();
    fit();
  });
  search.addEventListener('input', applyFilter);
  view.addEventListener('change', applyFilter);
  search.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const shown = matches();
    const first = shown && data.nodes.find(n => shown.has(n.id) && n.kind !== 'topic');
    if (first) location.hash = first.id;
  });
  const fromHash = () => { const id = decodeURIComponent(location.hash.slice(1)); if (byId[id] && id !== current) select(id); };
  addEventListener('hashchange', fromHash);

  const start = decodeURIComponent(location.hash.slice(1));
  if (byId[start]) ancestors(start).forEach(a => expanded.add(a));
  draw();
  fit();
  if (svg.clientWidth < 620) closeUp(byId[start] ? start : data.id);
  fromHash();
})();
