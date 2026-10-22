/* Lecture deck controls. Space and → reveal the next step, then advance; ← steps back.
   N opens the presenter's notes, F toggles fullscreen. Without JavaScript every slide stays readable. */
window.addEventListener('load', async () => {
  try { await window.MathJax?.startup?.promise; } catch (_) { /* Navigation still works. */ }
  const slides = [...document.querySelectorAll('#deck > .slide')];
  const select = document.querySelector('#slide-select');
  const previous = document.querySelector('#deck-prev');
  const next = document.querySelector('#deck-next');
  const notes = document.querySelector('#deck-notes');
  let current = 0;
  const steps = slide => [...slide.querySelectorAll('.fragment')];
  const shownCount = slide => steps(slide).filter(f => f.classList.contains('shown')).length;

  function show(index, {revealAll = false, updateHash = true} = {}) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    steps(slides[current]).forEach(f => f.classList.toggle('shown', revealAll));
    select.value = String(current);
    previous.disabled = current === 0;
    next.disabled = current === slides.length - 1 && shownCount(slides[current]) === steps(slides[current]).length;
    document.querySelector('#counter').textContent = `${current + 1} / ${slides.length}`;
    document.querySelector('#progress-fill').style.width = `${100 * (current + 1) / slides.length}%`;
    if (updateHash) history.replaceState(null, '', `#slide-${current + 1}`);
  }
  function forward() {
    const hidden = steps(slides[current]).find(f => !f.classList.contains('shown'));
    if (hidden) {
      hidden.classList.add('shown');
      next.disabled = current === slides.length - 1 && !steps(slides[current]).some(f => !f.classList.contains('shown'));
    } else if (current < slides.length - 1) show(current + 1);
  }
  function backward() {
    const shown = steps(slides[current]).filter(f => f.classList.contains('shown'));
    if (shown.length) { shown.at(-1).classList.remove('shown'); next.disabled = false; }
    else if (current > 0) show(current - 1, {revealAll: true});
  }
  async function openNotes() {
    const body = document.querySelector('#deck-notes-content');
    window.MathJax?.typesetClear?.([body]);
    body.replaceChildren(document.querySelector(`#notes-${current + 1}`).content.cloneNode(true));
    if (!body.childElementCount) body.innerHTML = '<p>No further notes for this slide.</p>';
    document.querySelector('#deck-notes-title').textContent = slides[current].getAttribute('aria-label').replace(/^Slide \d+: /, '');
    notes.showModal();
    try { await window.MathJax?.typesetPromise?.([body]); } catch (_) { /* Prose stays readable. */ }
  }
  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch (_) { /* Not available here. */ }
  }

  document.body.classList.add('js-ready');
  document.querySelector('.deck-controls').hidden = false;
  const notesButton = document.querySelector('#deck-notes-open');
  notesButton.hidden = false;
  notesButton.addEventListener('click', openNotes);
  document.querySelector('#deck-notes-close').addEventListener('click', () => notes.close());
  const print = document.querySelector('#deck-print');
  print.hidden = false;
  print.addEventListener('click', () => window.print());
  const fullscreen = document.querySelector('#deck-fullscreen');
  if (document.fullscreenEnabled) {
    fullscreen.hidden = false;
    fullscreen.addEventListener('click', toggleFullscreen);
  }
  previous.addEventListener('click', backward);
  next.addEventListener('click', forward);
  select.addEventListener('change', () => show(Number(select.value)));
  document.querySelector('#deck').addEventListener('click', event => {
    if (!(event.target instanceof Element && event.target.closest('a,button,select,summary'))) forward();
  });
  const indexFromHash = () => { const m = location.hash.match(/^#slide-(\d+)$/); return m ? Number(m[1]) - 1 : 0; };
  window.addEventListener('hashchange', () => show(indexFromHash(), {updateHash: false}));
  window.addEventListener('beforeprint', () => slides.forEach(s => steps(s).forEach(f => f.classList.add('shown'))));
  window.addEventListener('afterprint', () => show(current, {updateHash: false}));
  let idle;
  document.addEventListener('mousemove', () => {
    document.body.classList.add('chrome');
    clearTimeout(idle);
    idle = setTimeout(() => document.body.classList.remove('chrome'), 1800);
  });
  document.addEventListener('keydown', event => {
    if (notes.open || event.altKey || event.ctrlKey || event.metaKey) return;
    const target = event.target instanceof Element ? event.target : null;
    if (target?.closest('select,input,textarea,[contenteditable]')) return;
    const key = event.key;
    if (key === 'ArrowRight' || key === 'PageDown' || key === ' ') { event.preventDefault(); forward(); }
    else if (key === 'ArrowLeft' || key === 'PageUp') { event.preventDefault(); backward(); }
    else if (key === 'Home') { event.preventDefault(); show(0); }
    else if (key === 'End') { event.preventDefault(); show(slides.length - 1, {revealAll: true}); }
    else if (key === 'n' || key === 'N') { event.preventDefault(); openNotes(); }
    else if (key === 'f' || key === 'F') { event.preventDefault(); toggleFullscreen(); }
  });
  show(indexFromHash(), {updateHash: false});
});
