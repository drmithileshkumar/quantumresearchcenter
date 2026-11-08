// Deterministic scene player for article videos (scripts/videos.py).
// The renderer calls __seek(t) for each frame; nothing moves on its own, so every
// render of the same scene is identical. __seek returns a signature that changes only
// when the picture does, which lets the renderer reuse unchanged frames.
(() => {
  const S = window.SCENE;
  const ease = x => x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.pow(1 - x, 3);
  const NS = 'http://www.w3.org/2000/svg';
  const groups = {};   // chart id -> list of clip rects, one per titled mark group

  // Split each chart into groups: every element with its own <title> starts a group,
  // and untitled marks after it belong to it. Marks before the first group stay visible.
  function prepareChart(chart) {
    const svg = chart.querySelector('svg');
    const [x0, y0, w, h] = svg.getAttribute('viewBox').split(/\s+/).map(Number);
    const defs = document.createElementNS(NS, 'defs');
    svg.prepend(defs);
    const rects = [];
    let current = null;
    for (const el of [...svg.children]) {
      if (el === defs) continue;
      if ([...el.children].some(c => c.tagName === 'title')) {
        const k = rects.length, id = `${chart.id}-clip-${k}`;
        const clip = document.createElementNS(NS, 'clipPath'); clip.id = id;
        const rect = document.createElementNS(NS, 'rect');
        rect.setAttribute('x', x0 - 20); rect.setAttribute('y', y0 - 20);
        rect.setAttribute('height', h + 40); rect.setAttribute('width', 0);
        rect.dataset.full = w + 40;
        clip.append(rect); defs.append(clip); rects.push(rect);
        current = document.createElementNS(NS, 'g'); current.setAttribute('clip-path', `url(#${id})`);
        svg.insertBefore(current, el);
      }
      if (current) current.append(el);
    }
    groups[chart.id] = rects;
  }
  document.querySelectorAll('.chart[id]').forEach(prepareChart);

  const caption = document.querySelector('.caption');
  window.__seek = t => {
    const sig = [];
    for (const cue of S.cues) {
      const p = ease((t - cue.t) / cue.dur);
      sig.push(p === 0 || p === 1 ? p : p.toFixed(3));
      if (cue.kind === 'series') {
        const rects = groups[cue.id] || [];
        for (const k of cue.series) if (rects[k]) rects[k].setAttribute('width', p * rects[k].dataset.full);
      } else {
        const el = document.getElementById(cue.id);
        el.style.opacity = p;
        el.style.transform = p < 1 ? `translateY(${(1 - p) * 14}px)` : '';
      }
    }
    const k = S.captions.findIndex(c => t >= c.t0 && t < c.t1);
    if (caption) {
      caption.textContent = k < 0 ? '' : S.captions[k].text;
      caption.classList.toggle('on', k >= 0);
    }
    sig.push(k);
    return sig.join(',');
  };

  window.__ready = (async () => {
    await document.fonts.ready;
    if (window.MathJax && MathJax.startup) await MathJax.startup.promise;
    window.__seek(0);
    return true;
  })();

  // Layout checks on the fully revealed scene, reported in the review page.
  window.__audit = minFont => {
    window.__seek(S.duration);
    const issues = [];
    const stage = document.querySelector('.stage').getBoundingClientRect();
    const textEls = [...document.querySelectorAll('.stage *')].filter(el =>
      [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) && !el.closest('svg, mjx-container'));
    for (const el of textEls) {
      const r = el.getBoundingClientRect(), size = parseFloat(getComputedStyle(el).fontSize);
      const what = el.textContent.trim().slice(0, 50);
      if (size < minFont) issues.push(`text below ${minFont}px (${size}px): "${what}"`);
      if (r.bottom > stage.bottom + 2 || r.right > stage.right + 2) issues.push(`text outside the content area: "${what}"`);
    }
    for (const t of document.querySelectorAll('.stage svg text')) {
      const px = t.getBoundingClientRect().height;
      if (px && px < minFont * 0.8) issues.push(`chart label about ${Math.round(px)}px high: "${t.textContent.slice(0, 40)}"`);
    }
    for (const el of document.querySelectorAll('.stage svg, .stage mjx-container')) {
      const r = el.getBoundingClientRect();
      if (r.bottom > stage.bottom + 2 || r.right > stage.right + 2) issues.push('figure or formula extends outside the content area');
    }
    for (const el of document.querySelectorAll('[data-mjx-error], mjx-merror'))
      issues.push('MathJax error: ' + (el.getAttribute('data-mjx-error') || el.textContent).slice(0, 80));
    if (caption) {
      const line = parseFloat(getComputedStyle(caption).lineHeight);
      for (const c of S.captions) {
        caption.textContent = c.text; caption.classList.add('on');
        if (caption.getBoundingClientRect().height > 2 * line + 16) issues.push(`caption runs to three lines: "${c.text.slice(0, 50)}"`);
      }
      window.__seek(S.duration);
    }
    return issues;
  };
})();
