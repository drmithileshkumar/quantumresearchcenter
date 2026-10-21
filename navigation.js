/* Progressive enhancement: links keep readable text without JavaScript. Loaded from <head> on every page,
   it decorates each toolbar control as soon as the parser has finished it, so icons are in place before the
   first paint instead of swapping in afterwards (which made every page load flicker). Styles live in styles.css. */
(() => {
  if (window.__qrcNavigation) return;
  window.__qrcNavigation = true;
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
  // An element is finished once the parser has moved past it (some later node exists) or the document is parsed.
  const finished = element => {
    if (document.readyState !== 'loading' || element.hasAttribute('data-theme-toggle')) return true;
    for (let node = element; node; node = node.parentNode) if (node.nextSibling) return true;
    return false;
  };
  const buttons = {'print-chapter': 'print', 'search-open': 'search', 'search-close': 'close'};
  function scan() {
    // Pages whose scripts enable printing mark the button with data-print; show it now so it does not
    // appear (and shift the toolbar) when those deferred scripts run. They still attach the click handler.
    const print = document.querySelector('#print-chapter[data-print][hidden]');
    if (print) print.hidden = false;
    document.querySelectorAll('.site-nav a:not(.icon-nav), .news-toolbar nav a:not(.icon-nav)').forEach(link => {
      const label = link.textContent.trim();
      if (names[label] && finished(link)) decorate(link, names[label], label);
    });
    document.querySelectorAll('[data-theme-toggle]:not(.icon-nav), #print-chapter:not(.icon-nav), #search-open:not(.icon-nav), #search-close:not(.icon-nav)').forEach(button => {
      if (!finished(button)) return;
      const theme = button.hasAttribute('data-theme-toggle');
      const label = (theme && button.title) || button.getAttribute('aria-label') || button.textContent.trim();
      decorate(button, theme ? 'theme' : buttons[button.id], label);
      if (theme) new MutationObserver(() => button.setAttribute('aria-label', button.title)).observe(button, {attributes: true, attributeFilter: ['title']});
    });
    const menu = document.getElementById('menu-toggle');
    if (menu && !menu.classList.contains('icon-nav') && finished(menu)) decorate(menu, 'menu', 'Toggle contents');
    const type = document.getElementById('font-toggle');
    if (type && !type.classList.contains('icon-nav') && finished(type)) decorate(type, 'type', type.getAttribute('aria-label') || 'Increase text size');
  }
  if (document.readyState === 'loading') {
    const observer = new MutationObserver(scan);
    observer.observe(document.documentElement, {childList: true, subtree: true});
    document.addEventListener('DOMContentLoaded', () => { observer.disconnect(); scan(); });
  }
  scan();
})();
