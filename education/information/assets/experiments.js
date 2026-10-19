/* Exact probabilities, with native controls and static no-JavaScript figures. */
(() => {
  'use strict';
  const deg = Math.PI / 180;
  const fmt = x => x.toFixed(4);
  function bars(lab, entries) {
    const holder = lab.querySelector('[data-bars]');
    holder.replaceChildren();
    entries.forEach(([label, probability]) => {
      const row = document.createElement('div');
      row.className = 'bar-label';
      row.textContent = `${label}: ${fmt(probability)}`;
      const track = document.createElement('div');
      track.className = 'bar-track'; track.setAttribute('aria-hidden', 'true');
      const fill = document.createElement('div');
      fill.className = 'bar-fill'; fill.style.width = `${100 * Math.max(0, Math.min(1, probability))}%`;
      track.append(fill); row.append(track); holder.append(row);
    });
  }
  const setups = {
    phase(lab) {
      const phase = lab.querySelector('[data-phase]');
      function update() {
        const angle = Number(phase.value), p0 = (1 + Math.cos(angle * deg)) / 2;
        lab.dataset.probability = String(p0);
        bars(lab, [['Outcome 0', p0], ['Outcome 1', 1 - p0]]);
        lab.querySelector('[data-state]').textContent = `Phase ${angle}°. Final outcome probabilities sum to one. The original 0/1 probabilities before H remain one half each.`;
      }
      phase.addEventListener('input', update);
      lab.querySelector('[data-reset]').onclick = () => { phase.value = '0'; update(); };
      update();
    },
    noise(lab) {
      const noise = lab.querySelector('[data-noise]');
      function update() {
        const p = Number(noise.value) / 100, coherence = 1 - 2 * p;
        lab.dataset.coherence = String(coherence);
        bars(lab, [['Plus outcome', 1 - p], ['Minus outcome', p]]);
        const state = p === 0 ? 'Pure plus.' : p === 1 ? 'Pure minus: a known phase flip.' : p === .5 ? 'Maximally mixed: I/2.' : 'A mixture of plus and minus.';
        lab.querySelector('[data-state]').textContent = `Flip probability ${p.toFixed(2)}. Off-diagonal entries ${fmt(coherence / 2)}. ${state} Z readout remains fair throughout.`;
      }
      noise.addEventListener('input', update);
      lab.querySelector('[data-reset]').onclick = () => { noise.value = '50'; update(); };
      update();
    },
    decision(lab) {
      const angle = lab.querySelector('[data-angle]'), prior = lab.querySelector('[data-prior]');
      let exactAngle = null;
      function update() {
        const theta = exactAngle === null ? Number(angle.value) * deg : exactAngle;
        const p = Number(prior.value) / 100;
        const success = p * Math.cos(theta) ** 2 + (1 - p) * (1 - Math.sin(2 * theta)) / 2;
        const optimum = (1 + Math.sqrt(p * p + (1 - p) ** 2)) / 2;
        lab.dataset.success = String(success); lab.dataset.optimum = String(optimum);
        bars(lab, [['Correct guess', success], ['Wrong guess', 1 - success]]);
        lab.querySelector('[data-state]').textContent = `Direction ${(theta / deg).toFixed(2)}°. Prior ${p.toFixed(2)}. Best possible success ${fmt(optimum)}. Always guessing the common input succeeds with ${fmt(Math.max(p, 1 - p))}.`;
      }
      angle.addEventListener('input', () => { exactAngle = null; update(); });
      prior.addEventListener('input', () => { exactAngle = null; update(); });
      lab.querySelector('[data-optimal]').onclick = () => {
        const p = Number(prior.value) / 100;
        exactAngle = Math.atan2(-(1 - p), p) / 2;
        angle.value = String(exactAngle / deg); update();
      };
      lab.querySelector('[data-reset]').onclick = () => { angle.value = '0'; prior.value = '50'; exactAngle = null; update(); };
      update();
    }
  };
  document.querySelectorAll('[data-experiment]').forEach(lab => {
    const setup = setups[lab.dataset.experiment];
    if (!setup) return;
    setup(lab);
    lab.querySelectorAll('[data-live]').forEach(el => { el.hidden = false; });
    // Captions and circuit fallbacks remain visible beside the computed probabilities.
  });
})();
