(() => {
  const entries = [...document.querySelectorAll('.paper-entry')];
  const months = [...document.querySelectorAll('.news-month')];
  const search = document.getElementById('news-search');
  const topic = document.getElementById('news-topic');
  const links = [...document.querySelectorAll('.news-index a')];
  // Search text per paper. The page text is a fallback until index.json loads
  // (or when it cannot, e.g. opened from disk); the index adds technique names.
  const searchText = new Map(entries.map(entry => [entry.dataset.paperId, entry.textContent.toLowerCase()]));

  const requested = new URLSearchParams(location.search).get('topic');
  if ([...topic.options].some(option => option.value === requested)) topic.value = requested;

  function filter() {
    let count = 0;
    const query = search.value.trim().toLowerCase();
    for (const entry of entries) {
      entry.hidden = !(searchText.get(entry.dataset.paperId).includes(query) && (topic.value === 'all' || topic.value === entry.dataset.topic));
      if (!entry.hidden) count++;
    }
    for (const month of months) {
      month.hidden = !month.querySelector('.paper-entry:not([hidden])');
      const link = links.find(link => link.hash === '#' + month.id);
      if (link) link.hidden = month.hidden;
    }
    for (const link of links) {
      const linkTopic = new URLSearchParams(link.search).get('topic') || (link.getAttribute('href') === 'index.html' ? 'all' : null);
      if (linkTopic) { if (linkTopic === topic.value) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current'); }
    }
    document.getElementById('news-count').textContent = count ? `${count} of ${entries.length} papers` : 'No matching papers. Try another search or research area.';
  }

  search.addEventListener('input', filter);
  topic.addEventListener('change', () => {
    const url = new URL(location.href);
    if (topic.value === 'all') url.searchParams.delete('topic'); else url.searchParams.set('topic', topic.value);
    history.replaceState(null, '', url);
    filter();
  });
  document.getElementById('news-filters').hidden = false;
  filter();

  fetch('../index.json', {cache: 'no-store'}).then(response => response.ok ? response.json() : null).then(index => {
    if (!index) return;
    for (const paper of index.papers) {
      const fields = [paper.title, paper.authors, paper.problem, paper.result, ...paper.techniques];
      if (searchText.has(paper.id)) searchText.set(paper.id, fields.join(' ').toLowerCase());
    }
    filter();
  }).catch(() => {});

  // The review page is unlisted; link to it only when served by the local editor.
  if (['127.0.0.1', 'localhost'].includes(location.hostname)) {
    fetch('/api/news-editor', {cache: 'no-store'}).then(response => {
      if (!response.ok) return;
      const link = document.createElement('a');
      link.href = '../papers.html'; link.textContent = 'Review & approve';
      document.querySelector('.news-toolbar nav').append(link);
    }).catch(() => {});
  }
})();
