/* Shared appearance preference, applied before styles paint. No network dependencies. */
(() => {
  const navigationURL = new URL('../../../navigation.js', document.currentScript.src).href;
  const diagramURL = new URL('../../../diagrams.js', document.currentScript.src).href;
  const root = document.documentElement;
  root.classList.add('js');
  const preference = matchMedia('(prefers-color-scheme: dark)');
  let saved;
  try { saved = localStorage.getItem('qrc-theme'); } catch {}
  const valid = value => value === 'dark' || value === 'light';
  const apply = value => {
    root.dataset.theme = value;
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.setAttribute('aria-pressed', String(value === 'dark'));
      button.title = value === 'dark' ? 'Switch to light appearance' : 'Switch to dark appearance';
    });
  };
  const refreshPreference = () => {
    try { saved = localStorage.getItem('qrc-theme'); } catch {}
    apply(valid(saved) ? saved : preference.matches ? 'dark' : 'light');
  };
  refreshPreference();
  // Back/Forward can restore a document whose appearance predates another page's choice.
  addEventListener('pageshow', refreshPreference);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) refreshPreference();
  });
  preference.addEventListener('change', () => {
    if (!valid(saved)) apply(preference.matches ? 'dark' : 'light');
  });
  addEventListener('storage', event => {
    if (event.key !== 'qrc-theme') return;
    saved = event.newValue;
    apply(valid(saved) ? saved : preference.matches ? 'dark' : 'light');
  });
  // Put the toggle in the toolbar while the page is still being parsed, so it is there at first paint
  // (adding it at DOMContentLoaded shifted the toolbar on every page load). It is kept as the last item
  // while the parser adds the toolbar's other controls.
  let toggle;
  const placeToggle = () => {
    const tools = document.querySelector('.reading-tools, .toolbar, .news-toolbar');
    if (!tools) return;
    if (!toggle) {
      toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'theme-toggle';
      toggle.dataset.themeToggle = '';
      toggle.innerHTML = '<span aria-hidden="true">◐</span><span class="theme-label">Dark mode</span>';
      toggle.setAttribute('aria-label', 'Dark mode');
      toggle.addEventListener('click', () => {
        saved = root.dataset.theme === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('qrc-theme', saved); } catch {}
        apply(saved);
      });
      tools.append(toggle);
      apply(root.dataset.theme);   // once: re-applying on every mutation would loop with navigation.js
      return;
    }
    if (tools.lastChild !== toggle) tools.append(toggle);
  };
  const watcher = new MutationObserver(placeToggle);
  if (document.readyState === 'loading') watcher.observe(root, {childList: true, subtree: true});
  document.addEventListener('DOMContentLoaded', () => {
    const diagrams = document.createElement('script');
    diagrams.src = diagramURL; document.head.append(diagrams);
    watcher.disconnect();
    placeToggle();
    if (!window.__qrcNavigation) {        // pages that do not load navigation.js from <head>
      const navigation = document.createElement('script');
      navigation.src = navigationURL;
      document.head.append(navigation);
    }
    const hero = document.querySelector('.hero-visual');
    if (!hero) return;
    hero.classList.add('motion-ready');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const motion = hero.querySelector('[data-motion]');
    let paused = false;
    const updateMotion = () => {
      hero.classList.toggle('motion-paused', paused || reduced.matches);
      motion.hidden = reduced.matches;
      motion.textContent = paused ? 'Resume motion' : 'Pause motion';
      motion.setAttribute('aria-pressed', String(paused));
    };
    motion.addEventListener('click', () => { paused = !paused; updateMotion(); });
    reduced.addEventListener('change', updateMotion);
    updateMotion();
    const observer = new IntersectionObserver(entries => {
      hero.classList.toggle('offscreen', !entries[0].isIntersecting);
    });
    observer.observe(hero);
  });
})();
