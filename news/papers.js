(() => {
  const cards = [...document.querySelectorAll('[data-paper-id]')];
  const key = 'qrc-paper-selection-v1';
  let selected = new Set();
  const storage = document.getElementById('paper-storage');
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '[]');
    if (Array.isArray(saved)) selected = new Set(saved.filter(id => cards.some(c => c.dataset.paperId === id)));
  } catch { storage.textContent = 'Browser storage is unavailable. Copy your selection before leaving.'; }
  let editorToken = '';
  let approved = new Set();
  let saving = false;
  const approveButton = document.getElementById('paper-approve');
  const approvalStatus = document.getElementById('paper-approval');
  const output = document.getElementById('paper-selection');
  function update() {
    const term = document.getElementById('paper-search').value.trim().toLowerCase();
    const topic = document.getElementById('paper-topic').value;
    let count = 0;
    for (const card of cards) {
      card.hidden = !((topic === 'all' || card.dataset.topic === topic) && card.textContent.toLowerCase().includes(term));
      if (!card.hidden) count++;
      const indexLink = document.querySelector(`.news-index a[href="#${card.id}"]`);
      if (indexLink) indexLink.hidden = card.hidden;
    }
    document.getElementById('paper-count').textContent = `${count} papers shown · ${selected.size} selected across all areas`;
    approveButton.disabled = !editorToken || saving || ![...selected].some(id => !approved.has(id));
    for (const card of cards) card.querySelector('.paper-approval-status').textContent = approved.has(card.dataset.paperId) ? 'Approved · included in news' : '';
    output.value = cards.filter(c => selected.has(c.dataset.paperId)).map(c => `${c.querySelector('h3').textContent}\nhttps://arxiv.org/abs/${c.dataset.paperId}`).join('\n\n');
  }
  for (const card of cards) {
    const box = card.querySelector('input');
    box.checked = selected.has(box.value);
    box.addEventListener('change', () => {
      if (box.checked) selected.add(box.value); else selected.delete(box.value);
      try { localStorage.setItem(key, JSON.stringify([...selected])); }
      catch { storage.textContent = 'Selection is available below, but could not be saved in this browser.'; }
      update();
    });
  }
  document.getElementById('paper-search').addEventListener('input', update);
  document.getElementById('paper-topic').addEventListener('change', update);
  document.getElementById('paper-export').addEventListener('click', () => {
    update(); document.querySelector('.selection-export').open = true; output.focus(); output.select();
    storage.textContent = selected.size ? 'Copy this list and send it to the editor to request publication.' : 'Select at least one paper first.';
  });
  approveButton.addEventListener('click', async () => {
    const ids = [...selected].filter(id => !approved.has(id));
    if (!ids.length || saving || !editorToken) return;
    saving = true; update();
    approvalStatus.textContent = 'Saving approvals and rebuilding news…';
    try {
      const response = await fetch('/api/news-editor/approve', {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-Editor-Token': editorToken},
        body: JSON.stringify({ids})
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Approval failed. Please retry.');
      approved = new Set(result.approved);
      approvalStatus.textContent = `${ids.length} paper(s) approved and saved. `;
      const link = document.createElement('a');
      link.href = 'index.html'; link.textContent = 'View updated news →';
      approvalStatus.append(link);
    } catch (error) {
      approvalStatus.textContent = `Could not approve: ${error.message} Your selection has been kept.`;
    } finally { saving = false; update(); }
  });
  async function connectEditor() {
    try {
      if (!['127.0.0.1', 'localhost'].includes(location.hostname)) throw new Error('Local editor required');
      const response = await fetch('/api/news-editor', {cache: 'no-store'});
      if (!response.ok) throw new Error('Editor unavailable');
      const state = await response.json();
      if (typeof state.token !== 'string' || !Array.isArray(state.approved)) throw new Error('Invalid editor response');
      editorToken = state.token; approved = new Set(state.approved);
      approvalStatus.textContent = 'Local editor connected. Approve selected papers to save them to news.';
    } catch {
      approvalStatus.textContent = 'Approval requires the local editor; this static page cannot save changes.';
      document.getElementById('paper-editor-help').hidden = false;
    }
    update();
  }
  document.getElementById('paper-tools').hidden = false;
  connectEditor();
  update();
})();
