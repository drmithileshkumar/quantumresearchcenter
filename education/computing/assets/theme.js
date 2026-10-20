/* Shared appearance preference, applied before styles paint. No network dependencies. */
(() => {
  const root = document.documentElement;
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
  document.addEventListener('DOMContentLoaded', () => {
    const tools = document.querySelector('.reading-tools, .toolbar, .news-toolbar');
    if (tools) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'theme-toggle';
      button.dataset.themeToggle = '';
      button.innerHTML = '<span aria-hidden="true">◐</span><span class="theme-label">Dark mode</span>';
      button.setAttribute('aria-label', 'Dark mode');
      button.addEventListener('click', () => {
        saved = root.dataset.theme === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('qrc-theme', saved); } catch {}
        apply(saved);
      });
      tools.append(button);
      apply(root.dataset.theme);
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
    hero.addEventListener('pointermove', event => {
      if (reduced.matches || paused || event.pointerType === 'touch') return;
      const box = hero.getBoundingClientRect();
      hero.style.setProperty('--tilt', `${(event.clientX - box.left - box.width / 2) / 30}deg`);
    });
    hero.addEventListener('pointerleave', () => hero.style.setProperty('--tilt', '0deg'));
  });
})();
