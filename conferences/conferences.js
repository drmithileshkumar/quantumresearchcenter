(() => {
  'use strict';
  const form = document.getElementById('conference-filters');
  if (!form) return;
  const list = document.getElementById('conference-list');
  const cards = [...list.querySelectorAll('.conference-card')];
  const controls = Object.fromEntries([...form.querySelectorAll('input, select')].map(el => [el.id, el]));
  const mapControls = [...document.querySelectorAll('[data-map-country]')];
  const mapButtons = mapControls.filter(el => el.tagName.toLowerCase() === 'button');
  const categories = ['Flagship research', 'Established research', 'Emerging / regional', 'Industry forum'];
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const searchable = new Map(cards.map(card => [card, normalize(card.textContent)]));
  // Date-only comparisons use the visitor's local calendar, avoiding UTC day shifts.
  function today() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  }
  function state(card, now) {
    const {start, end} = card.dataset;
    return !start ? 'pending' : end < now ? 'past' : start <= now ? 'ongoing' : 'upcoming';
  }
  function update() {
    const now = today(), values = Object.fromEntries(Object.entries(controls).map(([id, el]) => [id, el.value]));
    const from = values['from-date'], to = values['to-date'];
    const invalid = Boolean(from && to && from > to);
    controls['to-date'].setCustomValidity(invalid ? 'End date must be on or after the start date.' : '');
    const words = normalize(values['conference-search']).trim().split(/\s+/).filter(Boolean);
    const statuses = {pending: 'Dates pending', past: 'Past edition', ongoing: 'In progress', upcoming: 'Upcoming'};
    let count = 0;
    const countryCounts = new Map();
    cards.forEach(card => {
      const c = card.dataset;
      c.state = state(card, now);
      card.querySelector('.event-status').textContent = statuses[c.state];
      const periodMatch = !values.period || (values.period === 'future' ? ['ongoing','upcoming'].includes(c.state) : c.state === values.period);
      const dateMatch = (!from && !to) || (c.start && (!from || c.end >= from) && (!to || c.start <= to));
      const matches = !invalid && periodMatch && dateMatch && (!values.year || values.year === c.year) && (!values.quality || values.quality === c.quality) && words.every(word => searchable.get(card).includes(word));
      if (matches) countryCounts.set(c.country, (countryCounts.get(c.country) || 0) + 1);
      card.hidden = !matches || Boolean(values.country && values.country !== c.country);
      if (!card.hidden) count++;
    });
    mapControls.forEach(el => {
      const country = el.dataset.mapCountry, total = countryCounts.get(country) || 0;
      const selected = country === values.country;
      el.classList.toggle('is-selected', selected);
      el.classList.toggle('is-empty', total === 0);
      if (el.tagName.toLowerCase() === 'button') {
        el.setAttribute('aria-pressed', String(selected));
        el.setAttribute('aria-label', `${country}: ${total} matching ${total === 1 ? 'conference' : 'conferences'}`);
        el.querySelector('.map-country-count').textContent = total;
      } else if (el.classList.contains('map-marker')) {
        el.querySelector('text').textContent = total;
        el.querySelector('title').textContent = `${country}: ${total} matching conferences`;
      }
    });
    document.getElementById('map-status').textContent = invalid ? 'Choose a valid date range to update the map.' : values.country ? `${values.country} selected · ${count} matching conferences` : `${count} matching conferences across ${countryCounts.size} countries`;
    const clearCountry = document.getElementById('map-clear');
    clearCountry.hidden = !values.country;
    const rank = {ongoing: 0, upcoming: 1, pending: 2, past: 3};
    const dateCompare = (a, b) => rank[a.dataset.state] - rank[b.dataset.state] || (a.dataset.state === 'past' ? b.dataset.start.localeCompare(a.dataset.start) : a.dataset.start.localeCompare(b.dataset.start)) || a.dataset.name.localeCompare(b.dataset.name);
    cards.sort((a, b) => {
      if (values.sort === 'country') return a.dataset.country.localeCompare(b.dataset.country) || dateCompare(a,b);
      if (values.sort === 'quality') return categories.indexOf(a.dataset.quality) - categories.indexOf(b.dataset.quality) || dateCompare(a,b);
      if (values.sort === 'name') return a.dataset.name.localeCompare(b.dataset.name);
      return dateCompare(a,b);
    });
    cards.forEach(card => list.append(card));
    document.getElementById('conference-count').textContent = invalid ? 'Choose an end date on or after the start date.' : `${count} of ${cards.length} conferences`;
    document.getElementById('no-results').hidden = count !== 0 || invalid;
    document.getElementById('upcoming-count').textContent = String(cards.filter(card => ['ongoing','upcoming'].includes(card.dataset.state)).length).padStart(2,'0');
  }
  mapControls.forEach(el => el.addEventListener('click', () => {
    controls.country.value = controls.country.value === el.dataset.mapCountry ? '' : el.dataset.mapCountry;
    update();
  }));
  mapButtons.forEach(button => { button.disabled = false; });
  document.getElementById('map-clear').addEventListener('click', () => { controls.country.value = ''; update(); });
  form.hidden = false;
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => setTimeout(update, 0));
  document.getElementById('clear-empty').addEventListener('click', () => { form.reset(); controls['conference-search'].focus(); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) update(); });
  update();
})();
