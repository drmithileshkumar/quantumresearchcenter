/* Primary navigation is rendered as text by the shared Python template.
   Only utility controls receive icons here, while the document is being parsed. */
(() => {
  if (window.__qrcNavigation) return;
  window.__qrcNavigation = true;
  const paths = {
    theme: '<g class="icon-sun"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5"/></g><path class="icon-moon" d="M20 15a9 9 0 0 1-11-11 9 9 0 1 0 11 11Z"/>',
    print: '<path d="M7 8V3h10v5M7 17H4V9h16v8h-3"/><path class="icon-paper" d="M7 14h10v7H7zM10 17h4"/><circle cx="17" cy="11" r=".5" fill="currentColor"/>',
    search: '<g class="icon-lens"><circle cx="10" cy="10" r="6"/><path d="m14.5 14.5 6 6"/></g>',
    close: '<path d="m6 6 12 12M6 18 18 6"/>',

    menu: '<path class="icon-detail" d="M4 6h16M4 12h16M4 18h16"/>',
    type: '<path d="m3 19 5-14 5 14M5 14h6M15 12h6M18 12v7"/>'
  };
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
    document.querySelectorAll('[data-theme-toggle]:not(.icon-nav), #print-chapter:not(.icon-nav), #search-open:not(.icon-nav), #search-close:not(.icon-nav)').forEach(button => {
      if (!finished(button)) return;
      const theme = button.hasAttribute('data-theme-toggle');
      const label = (theme && button.title) || button.getAttribute('aria-label') || button.textContent.trim();
      decorate(button, theme ? 'theme' : buttons[button.id], label);
      if (theme) new MutationObserver(() => button.setAttribute('aria-label', button.title)).observe(button, {attributes: true, attributeFilter: ['title']});
    });
    // Reserve reader controls before deferred handlers run, avoiding a late header shift.
    document.querySelectorAll('.reader #menu-toggle[hidden], .reader #font-toggle[hidden]').forEach(button => {
      if (finished(button)) button.hidden = false;
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
  // Warm only explicitly indicated navigation destinations; never intercept clicks.
  const warmed = new Set();
  function warmDestination(event) {
    if (event.type === 'pointerover' && event.pointerType !== 'mouse') return;
    const connection = navigator.connection;
    if (connection?.saveData || /(^|-)2g$/.test(connection?.effectiveType || '')) return;
    const link = event.target.closest?.('nav.primary-nav a, .page-navigation a');
    if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
    const url = new URL(link.href, location.href);
    if (!/^https?:$/.test(url.protocol) || url.origin !== location.origin || url.search ||
        !(/\.html$/.test(url.pathname) || url.pathname.endsWith('/'))) return;
    url.hash = '';
    if (url.href === location.href.split('#')[0] || warmed.has(url.href) || warmed.size >= 6) return;
    const hint = document.createElement('link');
    if (!hint.relList?.supports('prefetch')) return;
    hint.rel = 'prefetch';
    hint.href = url.href;
    warmed.add(url.href);
    document.head.append(hint);
  }
  document.addEventListener('pointerover', warmDestination, {passive: true});
  document.addEventListener('focusin', warmDestination);
})();
