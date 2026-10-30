(() => {
  const form = document.getElementById('company-filters');
  if (!form) return;
  const search = document.getElementById('company-search');
  const country = document.getElementById('company-country');
  const focus = document.getElementById('company-focus');
  const groups = [...document.querySelectorAll('.company-country-group')];
  const cards = [...document.querySelectorAll('.company-card')].map(element => ({element, text:element.dataset.search.toLocaleLowerCase(), focus:JSON.parse(element.dataset.focus)}));
  const mapControls = [...document.querySelectorAll('[data-map-country]')];
  const mapClear = document.getElementById('map-clear');
  const normalize = text => text.normalize('NFKD').replace(/\p{Diacritic}/gu, '').toLocaleLowerCase();
  function update() {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    const countryCounts = new Map();
    cards.forEach(card => {
      const group = card.element.closest('.company-country-group');
      const matches = (!focus.value || card.focus.includes(focus.value)) && terms.every(term => normalize(card.text).includes(term));
      if (matches) countryCounts.set(group.dataset.country, (countryCounts.get(group.dataset.country) || 0) + 1);
      card.element.hidden = !matches || Boolean(country.value && group.dataset.country !== country.value);
    });
    let count = 0, countryCount = 0;
    groups.forEach(group => {
      const visible = group.querySelectorAll('.company-card:not([hidden])').length;
      group.hidden = visible === 0;
      group.querySelector('.country-count').textContent = `${visible} ${visible===1?'company':'companies'}`;
      if(visible){count+=visible;countryCount++;}
    });
    document.getElementById('company-count').textContent = `${count} ${count===1?'company':'companies'} across ${countryCount} ${countryCount===1?'country':'countries'}`;
    document.getElementById('company-empty').hidden = count !== 0;
    mapControls.forEach(element => {
      const name = element.dataset.mapCountry, total = countryCounts.get(name) || 0;
      const selected = country.value === name;
      element.classList.toggle('is-selected', selected);
      element.classList.toggle('is-empty', total === 0);
      if (element.tagName.toLowerCase() === 'button') {
        element.setAttribute('aria-pressed', String(selected));
        element.setAttribute('aria-label', `${name}: ${total} matching ${total===1?'company':'companies'}`);
        element.querySelector('.map-country-count').textContent = total;
      } else if (element.classList.contains('map-marker')) {
        element.querySelector('text').textContent = total;
        element.querySelector('title').textContent = `${name}: ${total} matching companies`;
      }
    });
    document.getElementById('map-status').textContent = country.value ? `${country.value} selected · ${count} matching companies` : `${count} matching companies across ${countryCounts.size} countries`;
    mapClear.hidden = !country.value;
  }
  mapControls.forEach(element => {
    if (element.tagName.toLowerCase() === 'button') element.disabled = false;
    element.addEventListener('click', () => {
      country.value = country.value === element.dataset.mapCountry ? '' : element.dataset.mapCountry;
      update();
    });
  });
  mapClear.addEventListener('click', () => {country.value='';update();});
  form.hidden = false;
  form.addEventListener('submit',event=>event.preventDefault());
  search.addEventListener('input',update);country.addEventListener('change',update);focus.addEventListener('change',update);
  form.addEventListener('reset',()=>setTimeout(update,0));
  document.getElementById('company-clear').addEventListener('click',()=>{form.reset();search.focus();});
  document.querySelectorAll('.country-index a').forEach(link=>link.addEventListener('click',()=>{
    // Country shortcuts always reveal their destination, including after a restrictive search.
    search.value='';focus.value='';country.value='';update();
  }));
  update();
})();
