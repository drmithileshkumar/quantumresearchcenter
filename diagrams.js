/* Link scientific representations without changing the calculation. */
(() => {
  function connect() {
    document.querySelectorAll('[data-linked-diagram]').forEach(svg => {
      if (svg.dataset.connected) return;
      svg.dataset.connected = 'true';
      const parts = [...svg.querySelectorAll('[data-link]')];
      let pinned = null;
      const show = key => {
        svg.classList.toggle('diagram-comparing', Boolean(key));
        parts.forEach(part => {
          part.classList.toggle('diagram-selected', part.dataset.link === key);
          part.setAttribute('aria-pressed', String(part.dataset.link === pinned));
        });
      };
      parts.forEach(part => {
        part.addEventListener('pointerenter', () => show(part.dataset.link));
        part.addEventListener('pointerleave', () => show(pinned));
        part.addEventListener('focus', () => show(part.dataset.link));
        part.addEventListener('blur', () => show(pinned));
        const select = () => { pinned = pinned === part.dataset.link ? null : part.dataset.link; show(pinned); };
        part.addEventListener('click', select);
        part.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(); }
          if (event.key === 'Escape') { pinned = null; show(null); }
        });
      });
      const figure = svg.closest('figure');
      if (figure) {
        const help = document.createElement('p');
        help.className = 'diagram-guide';
        help.textContent = 'Explore the connection: hover or focus an arrow or term. Tap to keep it highlighted; tap again or press Escape to clear.';
        figure.append(help);
      }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', connect);
  else connect();
})();
