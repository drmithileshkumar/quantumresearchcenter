(() => {
  const entries = [...document.querySelectorAll('.paper-entry')];
  const months = [...document.querySelectorAll('.news-month')];
  const search = document.getElementById('news-search');
  const topic = document.getElementById('news-topic');
  const links = [...document.querySelectorAll('.news-index a')];
  const newsRoot = document.getElementById('articles').dataset.newsRoot;
  const earlier = document.getElementById('earlier-results');
  const earlierList = document.getElementById('earlier-list');
  const EARLIER_LIMIT = 100;
  let index = null;
  // Search text per paper. The page text is a fallback until index.json loads
  // (or when it cannot, e.g. opened from disk); the index adds technique names
  // and the papers that are not listed on this page.
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
    const others = index && (query || topic.value !== 'all') ? index.papers.filter(paper => !searchText.has(paper.id)
      && (topic.value === 'all' || topic.value === paper.topic) && paperText(paper).includes(query)) : [];
    showEarlier(others);
    const matches = count + others.length;
    const total = index ? index.papers.length : entries.length;
    document.getElementById('news-count').textContent = matches ? `${matches} of ${total} papers` : 'No matching papers. Try another search or research area.';
  }

  function paperText(paper) {
    return [paper.title, paper.authors, paper.problem, paper.result, ...paper.techniques].join(' ').toLowerCase();
  }

  function showEarlier(papers) {
    earlierList.replaceChildren(...papers.slice(0, EARLIER_LIMIT).map(paper => {
      const card = document.createElement('section');
      card.className = 'paper-card paper-entry';
      const heading = document.createElement('h3');
      const link = document.createElement('a');
      link.href = newsRoot + paper.url;
      link.textContent = paper.title;
      heading.append(link);
      const authors = document.createElement('p');
      authors.className = 'paper-authors';
      authors.textContent = paper.authors;
      const problem = document.createElement('p');
      problem.textContent = paper.problem;
      card.append(heading, authors, problem);
      return card;
    }));
    if (papers.length > EARLIER_LIMIT) {
      const note = document.createElement('p');
      note.className = 'paper-meta';
      note.textContent = `Showing the first ${EARLIER_LIMIT} of ${papers.length} earlier matches. Refine the search to narrow them.`;
      earlierList.append(note);
    }
    earlier.hidden = !papers.length;
    if (papers.length && window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([earlierList]).catch(() => {});
  }

  // The index grows with the archive, so fetch it only once a reader searches or filters.
  let loading = false;
  function loadIndex() {
    if (loading) return;
    loading = true;
    fetch(newsRoot + 'index.json').then(response => response.ok ? response.json() : null).then(loaded => {
      if (!loaded) return;
      index = loaded;
      for (const paper of index.papers) if (searchText.has(paper.id)) searchText.set(paper.id, paperText(paper));
      filter();
    }).catch(() => {});
  }

  search.addEventListener('focus', loadIndex);
  search.addEventListener('input', () => { loadIndex(); filter(); });
  topic.addEventListener('change', () => {
    loadIndex();
    const url = new URL(location.href);
    if (topic.value === 'all') url.searchParams.delete('topic'); else url.searchParams.set('topic', topic.value);
    history.replaceState(null, '', url);
    filter();
  });
  document.getElementById('news-filters').hidden = false;
  filter();
  if (topic.value !== 'all') loadIndex();

  // The review page is unlisted; link to it only when served by the local editor.
  if (['127.0.0.1', 'localhost'].includes(location.hostname)) {
    fetch('/api/news-editor', {cache: 'no-store'}).then(response => {
      if (!response.ok) return;
      const link = document.createElement('a');
      link.href = newsRoot + 'papers.html'; link.textContent = 'Review & approve';
      document.querySelector('.news-toolbar nav').append(link);
    }).catch(() => {});
  }
})();
