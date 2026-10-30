(() => {
  const data = JSON.parse(document.getElementById('frontier-data').textContent);
  const byId = Object.fromEntries(data.nodes.map(n => [n.id, n]));
  const svg = document.getElementById('frontier');
  const detail = document.getElementById('detail');
  const key = `qrc-frontier-${data.id}`;
  const levels = {skimmed: 1, studied: 2, documented: 3};
  const nodeEls = Object.fromEntries([...svg.querySelectorAll('.node')].map(el => [el.dataset.id, el]));
  const emptyState = () => ({trail: [], coverage: {}, notes: {}});
  let store = emptyState();
  let current = null;
  try { store = {...store, ...JSON.parse(localStorage.getItem(key) || '{}')}; } catch {}
  const save = () => { try { localStorage.setItem(key, JSON.stringify(store)); } catch {} };

  const element = (tag, props = {}, ...children) => {
    const el = Object.assign(document.createElement(tag), props);
    el.append(...children);
    return el;
  };

  const connections = id => {
    const n = byId[id], rows = [];
    if (n.parent) rows.push(['Part of', n.parent]);
    for (const link of n.links || []) rows.push([data.relations[link.rel][0], link.to]);
    for (const other of data.nodes) {
      if (other.parent === id) rows.push(['Includes', other.id]);
      for (const link of other.links || []) if (link.to === id) rows.push([data.relations[link.rel][1], other.id]);
    }
    return rows;
  };

  function renderPips(id) {
    const group = nodeEls[id].querySelector('.pips');
    group.replaceChildren();
    for (let i = 0; i < (levels[store.coverage[id]] || 0); i++) {
      const pip = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      pip.setAttribute('x', i * 4);
      pip.setAttribute('width', 3);
      pip.setAttribute('height', 3);
      group.append(pip);
    }
  }

  function renderDetail(id) {
    const n = byId[id];
    const parts = [element('p', {className: 'kicker', textContent: n.status ? data.statuses[n.status] : 'Topic'}), element('h2', {textContent: n.title}), element('p', {textContent: n.statement})];
    if (n.unknown) parts.push(element('h3', {textContent: 'Still unknown'}), element('p', {className: 'unknown', textContent: n.unknown}));
    parts.push(element('h3', {textContent: 'Connections'}));
    const list = element('ul');
    for (const [word, to] of connections(id)) {
      const jump = element('button', {type: 'button', className: 'jump', textContent: byId[to].title});
      jump.addEventListener('click', () => { location.hash = to; });
      list.append(element('li', {}, element('small', {textContent: word}), jump));
    }
    parts.push(list, element('h3', {textContent: 'Sources'}));
    const papers = element('ul');
    for (const source of n.sources) {
      const p = data.papers[source];
      papers.append(element('li', {}, element('a', {href: p.url, textContent: p.title}), element('small', {textContent: `${p.authors}, ${p.year}`})));
    }
    parts.push(papers, element('h3', {textContent: 'My progress'}));
    const coverage = element('select', {id: 'coverage'});
    for (const [value, label] of [['', 'Unexplored'], ['skimmed', 'Skimmed'], ['studied', 'Studied'], ['documented', 'Documented']]) coverage.append(element('option', {value, textContent: label}));
    coverage.value = store.coverage[id] || '';
    coverage.addEventListener('change', () => {
      if (coverage.value) store.coverage[id] = coverage.value; else delete store.coverage[id];
      save(); renderPips(id); applyView();
    });
    const notes = element('textarea', {id: 'notes', value: store.notes[id] || '', placeholder: 'What did you find? What should you read next?'});
    notes.addEventListener('input', () => {
      if (notes.value) store.notes[id] = notes.value; else delete store.notes[id];
      save();
    });
    parts.push(element('label', {htmlFor: 'coverage', textContent: 'How far I’ve got'}), coverage, element('label', {htmlFor: 'notes', textContent: 'My notes, saved in this browser', style: 'margin-top:10px'}), notes);
    parts.push(element('p', {className: 'tool-note'}, element('a', {href: `${id}/index.html`, textContent: 'Open as a page'})));
    detail.replaceChildren(...parts);
    detail.scrollTop = 0;
  }

  function renderTrail() {
    const list = document.getElementById('trail');
    list.replaceChildren(...store.trail.slice(-60).reverse().filter(id => byId[id]).map(id => {
      const button = element('button', {type: 'button', textContent: byId[id].label});
      button.addEventListener('click', () => { location.hash = id; });
      return element('li', {}, button);
    }));
    document.getElementById('trail-empty').hidden = store.trail.length > 0;
  }

  function select(id) {
    current = id;
    const linked = new Set(connections(id).map(row => row[1]));
    for (const [nodeId, el] of Object.entries(nodeEls)) {
      el.classList.toggle('selected', nodeId === id);
      el.classList.toggle('connected', linked.has(nodeId));
    }
    for (const path of svg.querySelectorAll('.cross-link')) path.toggleAttribute('hidden', path.dataset.a !== id && path.dataset.b !== id);
    renderDetail(id);
    reveal(id);
    if (store.trail[store.trail.length - 1] !== id) {
      store.trail.push(id);
      store.trail = store.trail.slice(-500);
      save();
      renderTrail();
    }
  }

  function applyView() {
    const view = document.getElementById('view').value;
    const query = document.getElementById('search').value.trim().toLowerCase();
    let shown = 0;
    for (const n of data.nodes) {
      const visible = (n.kind === 'topic' && !query)
        || (n.kind !== 'topic'
            && (view === 'all' || (view === 'frontier' && data.frontier.includes(n.status)) || (view === 'unexplored' && !store.coverage[n.id]))
            && (!query || `${n.title} ${n.label} ${n.statement}`.toLowerCase().includes(query)));
      nodeEls[n.id].classList.toggle('dim', !visible);
      if (n.kind !== 'topic' && visible) shown++;
    }
    for (const edge of svg.querySelectorAll('.edge')) edge.classList.toggle('dim', nodeEls[edge.dataset.to].classList.contains('dim'));
    document.getElementById('view-status').textContent = view === 'all' && !query ? '' : `${shown} shown`;
  }

  // Pan and zoom move the viewBox, so the map stays sharp at every scale.
  const full = {w: +svg.dataset.width, h: +svg.dataset.height};
  let box = {x: 0, y: 0, ...full};
  const paint = () => svg.setAttribute('viewBox', `${box.x} ${box.y} ${box.w} ${box.h}`);
  const position = id => { const m = nodeEls[id].transform.baseVal.getItem(0).matrix; return [m.e, m.f]; };
  const reveal = id => {
    const [x, y] = position(id);
    if (x > box.x + box.w * .1 && x < box.x + box.w * .9 && y > box.y + box.h * .1 && y < box.y + box.h * .9) return;
    box.x = x - box.w / 2;
    box.y = y - box.h / 2;
    paint();
  };
  // A narrow screen cannot show the whole map legibly, so it opens zoomed in on one area.
  const closeUp = id => {
    const [x, y] = position(id), w = 520, h = w * svg.clientHeight / svg.clientWidth;
    box = {x: x - w / 2, y: y - h / 2, w, h};
    paint();
  };
  const zoom = (factor, cx = box.x + box.w / 2, cy = box.y + box.h / 2) => {
    const w = Math.min(full.w * 2, Math.max(full.w / 8, box.w * factor)), scale = w / box.w;
    box = {x: cx - (cx - box.x) * scale, y: cy - (cy - box.y) * scale, w, h: box.h * scale};
    paint();
  };
  const toMap = e => {
    const point = new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse());
    return [point.x, point.y];
  };
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
    if (location.hash === `#${node.dataset.id}`) select(node.dataset.id); else location.hash = node.dataset.id;
  });
  document.getElementById('zoom-in').addEventListener('click', () => zoom(1 / 1.3));
  document.getElementById('zoom-out').addEventListener('click', () => zoom(1.3));
  document.getElementById('fit').addEventListener('click', () => { box = {x: 0, y: 0, ...full}; paint(); });

  for (const link of document.querySelectorAll('[data-node]')) link.addEventListener('click', e => { e.preventDefault(); location.hash = link.dataset.node; });
  document.getElementById('view').addEventListener('change', applyView);
  document.getElementById('search').addEventListener('input', applyView);
  document.getElementById('search').addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const first = data.nodes.find(n => !nodeEls[n.id].classList.contains('dim') && n.kind !== 'topic');
    if (first) location.hash = first.id;
  });
  const fromHash = () => { const id = decodeURIComponent(location.hash.slice(1)); if (byId[id] && id !== current) select(id); };
  addEventListener('hashchange', fromHash);

  const download = (name, type, text) => {
    const url = URL.createObjectURL(new Blob([text], {type}));
    const link = element('a', {href: url, download: name});
    link.click();
    URL.revokeObjectURL(url);
  };
  document.getElementById('backup').addEventListener('click', () => download(`${data.id}-frontier-notes.json`, 'application/json', JSON.stringify(store, null, 2)));
  document.getElementById('log').addEventListener('click', () => {
    const lines = [`# ${data.title} research log`, '', '## Trail', ''];
    store.trail.forEach((id, i) => { if (byId[id]) lines.push(`${i + 1}. ${byId[id].title}`); });
    lines.push('', '## Notes', '');
    for (const id of Object.keys(store.notes)) {
      if (!byId[id]) continue;
      const n = byId[id];
      lines.push(`### ${n.title}`, '', `Field: ${n.status ? data.statuses[n.status] : 'Topic'}. Me: ${store.coverage[id] || 'unexplored'}.`, '', store.notes[id], '');
    }
    download(`${data.id}-research-log.md`, 'text/markdown', lines.join('\n'));
  });
  document.getElementById('restore').addEventListener('change', async e => {
    const status = document.getElementById('log-status');
    try {
      const parsed = JSON.parse(await e.target.files[0].text());
      if (!Array.isArray(parsed.trail) || !parsed.coverage || !parsed.notes || typeof parsed.coverage !== 'object' || typeof parsed.notes !== 'object') throw new Error();
      store = {...emptyState(), ...parsed};
      save();
      Object.keys(byId).forEach(renderPips);
      renderTrail();
      applyView();
      if (current) renderDetail(current);
      status.textContent = 'Notes restored.';
    } catch {
      status.textContent = 'That file is not a frontier backup. Nothing changed.';
    }
  });

  Object.keys(byId).forEach(renderPips);
  renderTrail();
  applyView();
  if (svg.clientWidth < 620) closeUp(byId[location.hash.slice(1)] ? location.hash.slice(1) : data.nodes[0].id);
  fromHash();
})();
