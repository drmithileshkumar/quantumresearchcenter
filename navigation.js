/* Progressive enhancement: links retain readable text without JavaScript. */
(() => {
  if (document.querySelector('link[data-navigation-icons]')) return;
  const css = document.createElement('link');
  css.rel = 'stylesheet'; css.href = new URL('navigation.css', document.currentScript.src).href;
  css.dataset.navigationIcons = ''; document.head.append(css);
  const paths = {
    theme: '<g class="icon-sun"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5"/></g><path class="icon-moon" d="M20 15a9 9 0 0 1-11-11 9 9 0 1 0 11 11Z"/>',
    print: '<path d="M7 8V3h10v5M7 17H4V9h16v8h-3"/><path class="icon-paper" d="M7 14h10v7H7zM10 17h4"/><circle cx="17" cy="11" r=".5" fill="currentColor"/>',
    search: '<g class="icon-lens"><circle cx="10" cy="10" r="6"/><path d="m14.5 14.5 6 6"/></g>',
    close: '<path d="m6 6 12 12M6 18 18 6"/>',

    home: '<path d="m3 11 9-8 9 8M5 10v10h5v-6h4v6h5V10"/>',
    education: '<path d="M12 6c-3-2-6-2-10-1v14c4-1 7-1 10 1 3-2 6-2 10-1V5c-4-1-7-1-10 1Z"/><path class="icon-detail" d="M12 6v14M5 9h4M15 9h4M5 13h4M15 13h4"/>',
    research: '<g class="icon-orbit"><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/></g><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/>',
    news: '<rect x="4" y="3" width="16" height="18" rx="2"/><path class="icon-detail" d="M8 7h8M8 11h8M8 15h4M8 18h6"/>',
    review: '<path d="M8 5H5v16h14V5h-3M9 3h6v4H9z"/><path class="icon-detail" d="m8 14 3 3 5-6"/>',
    menu: '<path class="icon-detail" d="M4 6h16M4 12h16M4 18h16"/>',
    type: '<path d="m3 19 5-14 5 14M5 14h6M15 12h6M18 12v7"/>'
  };
  const names = {Home:'home',Education:'education',Research:'research','Selected papers':'news','Review & approve':'review'};
  function decorate(element, kind, label) {
    element.classList.add('icon-nav', `icon-nav-${kind}`);
    element.setAttribute('aria-label', label);
    element.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${paths[kind]}</svg><span class="nav-tooltip" aria-hidden="true"></span>`;
    const tip = element.querySelector('.nav-tooltip');
    tip.textContent = label;
    new MutationObserver(() => { tip.textContent = element.getAttribute('aria-label'); }).observe(element, {attributes:true,attributeFilter:['aria-label']});
  }
  document.querySelectorAll('.site-nav a, .news-toolbar nav a').forEach(link => {
    const label = link.textContent.trim();
    if (names[label]) decorate(link,names[label],label);
  });
  document.querySelectorAll('[data-theme-toggle], #print-chapter, #search-open, #search-close').forEach(button => {
    const theme = button.hasAttribute('data-theme-toggle');
    const kind = theme ? 'theme' : {'print-chapter':'print','search-open':'search','search-close':'close'}[button.id];
    const label = (theme && button.title) || button.getAttribute('aria-label') || button.textContent.trim();
    decorate(button, kind, label);
    if (theme) new MutationObserver(() => button.setAttribute('aria-label', button.title)).observe(button, {attributes:true, attributeFilter:['title']});
  });
  const menu = document.getElementById('menu-toggle');
  if (menu) decorate(menu,'menu','Toggle contents');
  const type = document.getElementById('font-toggle');
  if (type) decorate(type,'type',type.getAttribute('aria-label') || 'Increase text size');
})();
