/* Progressive enhancement: all articles and navigation remain available without JS. */
(() => {
  // Preserve bookmarks to the old paper listing after introducing the news hub.
  if (/\/news\/(?:index\.html)?$/.test(location.pathname) &&
      (new URLSearchParams(location.search).has('topic') || /^#(?:paper-|month-)/.test(location.hash))) {
    location.replace('papers/index.html' + location.search + location.hash);
    return;
  }
  const filters = document.querySelector('.article-filters');
  if (!filters) return;
  const search = document.getElementById('article-search');
  const topic = document.getElementById('article-topic');
  const format = document.getElementById('article-format');
  const cards = [...document.querySelectorAll('[data-article]')];
  const count = document.getElementById('article-count');
  function restore() {
    const params = new URLSearchParams(location.search);
    search.value = params.get('q') || '';
    for (const [key, select] of [['topic', topic], ['format', format]]) {
      const value = params.get(key);
      select.value = [...select.options].some(o => o.value === value) ? value : 'all';
    }
  }
  function filter(updateURL = true) {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      card.hidden = !((topic.value === 'all' || card.dataset.topic === topic.value) &&
        (format.value === 'all' || card.dataset.format === format.value) &&
        card.textContent.toLocaleLowerCase().includes(query));
      if (!card.hidden) visible++;
    }
    count.textContent = visible ? `${visible} of ${cards.length} articles` : 'No matching articles. Try another topic, format, or search.';
    if (updateURL) {
      const url = new URL(location.href);
      for (const [key, value] of [['q', search.value.trim()], ['topic', topic.value], ['format', format.value]]) {
        if (!value || value === 'all') url.searchParams.delete(key); else url.searchParams.set(key, value);
      }
      history.replaceState(null, '', url);
    }
  }
  restore(); filter(false); filters.hidden = false;
  search.addEventListener('input', () => filter());
  topic.addEventListener('change', () => filter());
  format.addEventListener('change', () => filter());
  addEventListener('popstate', () => { restore(); filter(false); });
})();
