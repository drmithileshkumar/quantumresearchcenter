// The Majorana constellation page. Every number below mirrors the build in scripts/tools.py:
// stars are roots of the Majorana polynomial, the state is rebuilt from the stars, and the
// geometric measure of entanglement uses the same fixed grid, so the page never jumps on load.
(() => {
  'use strict';

  const sphere = document.getElementById('majorana');
  if (!sphere) return;

  const byId = id => document.getElementById(id);
  const R2D = 180 / Math.PI, D2R = Math.PI / 180;
  const ZERO = 5e-4;
  const MAX_N = 8;
  const RINGS = 48;
  const LIGHT = Math.hypot;

  // ---- complex numbers, as [re, im] -------------------------------------------------------------
  const cAdd = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const cMul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const cDiv = (a, b) => {
    const size = b[0] * b[0] + b[1] * b[1] || 1;
    return [(a[0] * b[0] + a[1] * b[1]) / size, (a[1] * b[0] - a[0] * b[1]) / size];
  };
  const cAbs = a => Math.hypot(a[0], a[1]);
  const cConj = a => [a[0], -a[1]];
  const cScale = (a, factor) => [a[0] * factor, a[1] * factor];
  const cExp = angle => [Math.cos(angle), Math.sin(angle)];
  const cPow = (a, power) => {
    let out = [1, 0];
    for (let step = 0; step < power; step++) out = cMul(out, a);
    return out;
  };
  const comb = (n, k) => {
    let out = 1;
    for (let step = 1; step <= k; step++) out = (out * (n - k + step)) / step;
    return Math.round(out);
  };

  // ---- the text formatters the static page also uses --------------------------------------------
  const fixed = (value, digits) => {
    const rounded = Math.abs(value) < ZERO ? 0 : value;
    return (rounded < 0 ? '−' : '') + Math.abs(rounded).toFixed(digits);
  };
  const complexText = (value, digits = 3) => {
    if (Math.abs(value[1]) < ZERO) return fixed(value[0], digits);
    if (Math.abs(value[0]) < ZERO) return fixed(value[1], digits) + 'i';
    return fixed(value[0], digits) + (value[1] < 0 ? ' − ' : ' + ')
      + fixed(Math.abs(value[1]), digits) + 'i';
  };
  const phaseText = value => {
    if (cAbs(value) < 1e-9) return '—';
    // A real amplitude computed from stars carries rounding noise in its imaginary part; without
    // this it can land on 360° instead of 0° and the readout would disagree with the build.
    let degrees = Math.abs(value[1]) < ZERO && value[0] > 0 ? 0 : Math.atan2(value[1], value[0]) * R2D;
    return `${((degrees + 360) % 360).toFixed(0)}°`;
  };

  // ---- stars and states -------------------------------------------------------------------------
  const clamp = value => Math.max(-1, Math.min(1, value));
  const unit = point => {
    const size = LIGHT(point[0], point[1], point[2]) || 1;
    return [point[0] / size, point[1] / size, point[2] / size];
  };

  // The one-spin state pointing along a star: (u, v) with |u|² + |v|² = 1.
  function spinor(point) {
    const theta = Math.acos(clamp(point[2]));
    return [[Math.cos(theta / 2), 0], cMul(cExp(Math.atan2(point[1], point[0])), [Math.sin(theta / 2), 0])];
  }

  // Bloch vector of a root z = −u/v; z = ∞ is the north pole.
  function starOfRoot(root) {
    if (!root) return [0, 0, 1];
    const scale = 1 / Math.sqrt(1 + cAbs(root) ** 2);
    const u = cScale(root, -scale), v = [scale, 0];
    const product = cMul(cConj(u), v);
    return [2 * product[0], 2 * product[1], Math.abs(u[0]) ** 2 + u[1] ** 2 - Math.abs(v[0]) ** 2];
  }

  // Durand–Kerner on c₀ + c₁z + … The roots above the degree stay at infinity, i.e. the north pole.
  function rootsOf(coefficients, iterations = 400) {
    const values = coefficients.slice();
    while (values.length && cAbs(values[values.length - 1]) < 1e-13) values.pop();
    const degree = values.length - 1;
    if (degree < 1) return [];
    const lead = values[degree];
    const lower = values.slice(0, degree).map(value => cDiv(value, lead));
    const radius = 1 + lower.reduce((most, value) => Math.max(most, cAbs(value)), 0);
    let found = Array.from({ length: degree },
      (_, index) => cScale(cExp(2 * Math.PI * (index + 0.25) / degree), radius));
    const evaluate = point => {
      let total = [1, 0];
      for (let index = lower.length - 1; index >= 0; index--) total = cAdd(cMul(total, point), lower[index]);
      return total;
    };
    for (let round = 0; round < iterations; round++) {
      let moved = 0;
      found = found.map((root, index) => {
        let divisor = [1, 0];
        found.forEach((other, otherIndex) => {
          if (otherIndex !== index) divisor = cMul(divisor, [root[0] - other[0], root[1] - other[1]]);
        });
        const step = cDiv(evaluate(root), divisor);
        moved = Math.max(moved, cAbs(step));
        return [root[0] - step[0], root[1] - step[1]];
      });
      if (moved < 1e-15) break;
    }
    return found;
  }

  // Σ_k √C(n,k) c_k z^k, the polynomial whose roots are the stars.
  const polynomialCoefficients = state =>
    state.map((value, index) => cScale(value, Math.sqrt(comb(state.length - 1, index))));

  function starsOf(coefficients) {
    const count = coefficients.length - 1;
    const stars = rootsOf(polynomialCoefficients(coefficients)).map(starOfRoot);
    while (stars.length < count) stars.push([0, 0, 1]);
    return stars;
  }

  // Dicke amplitudes of the symmetrization of the given spin directions.
  function stateOf(stars) {
    const count = stars.length;
    let poly = [[1, 0]];
    stars.forEach(point => {
      const [u, v] = spinor(point);
      const grown = Array.from({ length: poly.length + 1 }, () => [0, 0]);
      poly.forEach((coefficient, index) => {
        grown[index] = cAdd(grown[index], cMul(coefficient, u));
        grown[index + 1] = cAdd(grown[index + 1], cMul(coefficient, v));
      });
      poly = grown;
    });
    const amplitudes = poly.map((value, index) => cScale(value, 1 / Math.sqrt(comb(count, index))));
    const norm = LIGHT(...amplitudes.map(cAbs)) || 1;
    return amplitudes.map(value => cScale(value, 1 / norm));
  }

  // |⟨n̂| ψ⟩|² for the spin-coherent state pointing along direction.
  function overlap2(coefficients, direction) {
    const count = coefficients.length - 1;
    const [u, v] = spinor(direction);
    let total = [0, 0];
    coefficients.forEach((value, index) => {
      const weight = cMul(cPow(cConj(u), count - index), cPow(cConj(v), index));
      total = cAdd(total, cMul(weight, cScale(value, Math.sqrt(comb(count, index)))));
    });
    return total[0] ** 2 + total[1] ** 2;
  }

  // The same rings and the same pattern search as majorana_coherent_overlap in the build.
  function coherentOverlap(coefficients) {
    let best = -1, arg = [0, 0, 1];
    for (let ring = 0; ring < RINGS; ring++) {
      const theta = (Math.PI * (ring + 0.5)) / RINGS;
      const steps = Math.max(1, Math.round(2 * RINGS * Math.sin(theta)));
      for (let step = 0; step < steps; step++) {
        const phi = (2 * Math.PI * step) / steps;
        const candidate = [Math.sin(theta) * Math.cos(phi), Math.sin(theta) * Math.sin(phi), Math.cos(theta)];
        const value = overlap2(coefficients, candidate);
        if (value > best) { best = value; arg = candidate; }
      }
    }
    let side = Math.PI / RINGS;
    for (let round = 0; round < 200; round++) {
      let improved = false;
      for (let axis = 0; axis < 3; axis++) {
        for (const sign of [1, -1]) {
          const moved = unit(arg.map((value, index) => value + (index === axis ? sign * side : 0)));
          const value = overlap2(coefficients, moved);
          if (value > best) { best = value; arg = moved; improved = true; }
        }
      }
      if (!improved) side *= 0.5;
      else if (side < 1e-9) break;
    }
    return Math.min(1, best);
  }

  function spinLength(stars) {
    const total = [0, 1, 2].map(axis => stars.reduce((sum, point) => sum + point[axis], 0));
    return LIGHT(total[0], total[1], total[2]) / (stars.length || 1);
  }

  // A coefficient as (sign, TeX body), so a negative term can be joined with a minus sign.
  function termTex(value) {
    // The sign is decided once, from whichever part is actually displayed: a coefficient whose
    // real part is negligible is signed by its imaginary part, or the two would cancel the
    // wrong way. Negating a real-negative coefficient cannot oscillate.
    if (Math.abs(value[0]) < ZERO) {
      if (Math.abs(value[1]) < ZERO) return ['+', '0.00'];
      return [value[1] < 0 ? '-' : '+', Math.abs(value[1]).toFixed(2) + 'i'];
    }
    if (value[0] < 0) {
      const [sign, body] = termTex([-value[0], -value[1]]);
      return [sign === '+' ? '-' : '+', body];
    }
    if (Math.abs(value[1]) < ZERO) return ['+', value[0].toFixed(2)];
    const inner = value[1] >= 0 ? '+' : '-';
    return ['+', `(${value[0].toFixed(2)}${inner}${Math.abs(value[1]).toFixed(2)}i)`];
  }

  function polynomialTex(coefficients) {
    const terms = polynomialCoefficients(coefficients).map((value, index) => [index, value])
      .filter(([, value]) => cAbs(value) > 1e-9);
    if (!terms.length) return 'P(z)=0';
    const pieces = terms.slice().reverse().map(([index, value]) => {
      const [sign, body] = termTex(value);
      return [sign, body + (index === 0 ? '' : (index === 1 ? 'z' : `z^{${index}}`))];
    });
    return 'P(z)=' + pieces.map(([sign, body], index) =>
      (index === 0 ? (sign === '-' ? '-' : '') : sign) + body).join('');
  }

  // MathJax typesets in the page's own style, so the readout is set with the same engine as the prose.
  // Updates coalesce: a drag asks for new TeX faster than MathJax can set it, so only the latest wins.
  let polynomial = '', typesetting = false;
  function showPolynomial(tex) {
    polynomial = tex;
    if (typesetting) return;
    const host = byId('majorana-polynomial');
    if (!window.MathJax || !MathJax.tex2svgPromise) { host.textContent = `\\(${tex}\\)`; return; }
    typesetting = true;
    const ready = MathJax.startup && MathJax.startup.promise ? MathJax.startup.promise : Promise.resolve();
    ready.then(async () => {
      try {
        for (let current = polynomial; ; current = polynomial) {
          const rendered = await MathJax.tex2svgPromise(current, { display: false });
          host.replaceChildren(rendered);
          host.dataset.tex = current;
          if (current === polynomial) break;
        }
      } finally {
        typesetting = false;
        if (host.dataset.tex !== polynomial) showPolynomial(polynomial);
      }
    });
  }

  // ---- the sphere: an orbit camera ----------------------------------------------------------------
  const S_CENTER = 200, S_RADIUS = 148;
  const GRID_STEPS = 180;
  const HOME = { azimuth: Number(sphere.dataset.azimuth || 32), elevation: Number(sphere.dataset.elevation || 17) };
  let azimuth = HOME.azimuth, elevation = HOME.elevation;
  let right = [1, 0, 0], up = [0, 1, 0], forward = [0, 0, -1];

  function camera() {
    const a = azimuth * D2R, e = elevation * D2R;
    forward = [-Math.cos(e) * Math.sin(a), Math.cos(e) * Math.cos(a), -Math.sin(e)];
    const length = Math.hypot(forward[1], -forward[0]) || 1;
    right = [forward[1] / length, -forward[0] / length, 0];
    up = [right[1] * forward[2] - right[2] * forward[1],
          right[2] * forward[0] - right[0] * forward[2],
          right[0] * forward[1] - right[1] * forward[0]];
  }

  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const project = point => [S_CENTER + S_RADIUS * dot(point, right), S_CENTER - S_RADIUS * dot(point, up)];
  const facing = point => dot(point, forward) < 0;

  const SVG_NS = 'http://www.w3.org/2000/svg';
  const svgElement = (name, attributes, text) => {
    const element = document.createElementNS(SVG_NS, name);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    if (text !== undefined) element.textContent = text;
    return element;
  };

  function curveRuns(pointAt) {
    const samples = [];
    for (let index = 0; index < GRID_STEPS; index++) {
      const point = pointAt((2 * Math.PI * index) / GRID_STEPS);
      samples.push([project(point), facing(point)]);
    }
    const wrap = index => ((index % GRID_STEPS) + GRID_STEPS) % GRID_STEPS;
    let start = 0;
    for (let index = 0; index < GRID_STEPS; index++) {
      if (samples[index][1] !== samples[wrap(index - 1)][1]) { start = index; break; }
    }
    const ordered = samples.slice(start).concat(samples.slice(0, start));
    const runs = [];
    ordered.forEach((sample, index) => {
      const last = runs[runs.length - 1];
      if (last && last.visible === sample[1]) last.last = index;
      else runs.push({ visible: sample[1], first: index, last: index });
    });
    return runs.map(run => {
      const points = [ordered[wrap(run.first - 1)][0]];
      for (let index = run.first; index <= run.last; index++) points.push(ordered[index][0]);
      points.push(ordered[wrap(run.last + 1)][0]);
      return { visible: run.visible, path: 'M' + points.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L') };
    });
  }

  function drawGrid() {
    const grid = byId('majorana-grid');
    grid.replaceChildren();
    curveRuns(t => [Math.cos(t), Math.sin(t), 0]).forEach(run => {
      grid.appendChild(svgElement('path', {
        class: run.visible ? 'bloch-equator' : 'bloch-equator is-behind', d: run.path,
      }));
    });
    [0, Math.PI / 2].forEach(longitude => {
      curveRuns(t => [Math.sin(t) * Math.cos(longitude), Math.sin(t) * Math.sin(longitude), Math.cos(t)])
        .forEach(run => {
          grid.appendChild(svgElement('path', {
            class: run.visible ? 'bloch-meridian' : 'bloch-meridian is-behind', d: run.path,
          }));
        });
    });
  }

  const AXES = [[[1, 0, 0], '|+⟩'], [[-1, 0, 0], '|−⟩'], [[0, 1, 0], '|+i⟩'],
                [[0, -1, 0], '|−i⟩'], [[0, 0, 1], '|0⟩'], [[0, 0, -1], '|1⟩']];

  function drawAxes() {
    const axes = byId('majorana-axes');
    axes.replaceChildren();
    AXES.forEach(([vector, label]) => {
      const tip = project(vector);
      axes.appendChild(svgElement('line', {
        class: 'bloch-axis', x1: S_CENTER, y1: S_CENTER,
        x2: tip[0].toFixed(1), y2: tip[1].toFixed(1),
      }));
      const dx = tip[0] - S_CENTER, dy = tip[1] - S_CENTER;
      axes.appendChild(svgElement('text', {
        class: 'bloch-axis-label', x: (S_CENTER + dx * 1.15).toFixed(1),
        y: (S_CENTER + dy * 1.15).toFixed(1), dy: '4',
        'text-anchor': dx / S_RADIUS > 0.35 ? 'start' : dx / S_RADIUS < -0.35 ? 'end' : 'middle',
      }, label));
    });
  }

  // ---- the stars ------------------------------------------------------------------------------------
  const starGroup = byId('majorana-stars');
  let stars = [];
  let selected = 0;
  let label = '';
  let preset = 'cat';

  function buildStars(count) {
    starGroup.replaceChildren();
    Array.from({ length: count }, (_, index) => {
      starGroup.appendChild(svgElement('circle', { class: 'majorana-star', id: `majorana-star-${index}`, r: '6.5' }));
      starGroup.appendChild(svgElement('text', {
        class: 'majorana-index', id: `majorana-index-${index}`, 'text-anchor': 'middle',
      }, String(index + 1)));
    });
    menu.replaceChildren(...Array.from({ length: count }, (_, index) => {
      const option = document.createElement('option');
      option.value = String(index);
      option.textContent = String(index + 1);
      return option;
    }));
    if (selected > count - 1) selected = count - 1;
    menu.value = String(selected);
  }

  function placeStars() {
    // Stars on the same point share one marker and one label listing every index.
    const groups = [];
    stars.forEach((point, index) => {
      const group = groups.find(entry => Math.hypot(entry.point[0] - point[0], entry.point[1] - point[1],
        entry.point[2] - point[2]) < 1e-6);
      if (group) group.indices.push(index);
      else groups.push({ point, indices: [index] });
    });
    groups.forEach(group => {
      group.first = group.indices[0];
      group.label = group.indices.map(index => index + 1).join('·');
    });
    stars.forEach((point, index) => {
      const dot = byId(`majorana-star-${index}`);
      const number = byId(`majorana-index-${index}`);
      if (!dot || !number) return;
      const [x, y] = project(point);
      const behind = !facing(point);
      dot.setAttribute('cx', x.toFixed(1));
      dot.setAttribute('cy', y.toFixed(1));
      dot.classList.toggle('is-behind', behind);
      dot.classList.toggle('is-selected', index === selected);
      number.classList.toggle('is-behind', behind);
      const group = groups.find(entry => entry.indices.includes(index));
      if (group.first !== index) {
        number.classList.add('is-empty');
        return;
      }
      number.classList.remove('is-empty');
      number.textContent = group.label;
      // A star on the north pole would print its number over the |0⟩ axis tag.
      number.setAttribute('x', x.toFixed(1));
      number.setAttribute('y', (y < S_CENTER - S_RADIUS + 14 ? y + 19 : y - 11).toFixed(1));
    });
  }

  // ---- the readouts ---------------------------------------------------------------------------------
  const menu = byId('majorana-star');
  const rows = Array.from({ length: MAX_N + 1 }, (_, index) => byId(`majorana-row-${index}`));

  // The ket column only changes with n, so it is typeset once per size rather than once per frame.
  let ketCount = Number(byId('majorana-count').textContent);

  async function showKets(count) {
    const typeset = Boolean(window.MathJax && MathJax.startup && MathJax.tex2svgPromise);
    if (typeset) await MathJax.startup.promise;
    for (let index = 0; index <= count; index++) {
      const cell = byId(`majorana-ket-${index}`);
      if (!cell) continue;
      if (!typeset) { cell.textContent = `|${count},${index}⟩`; continue; }
      cell.replaceChildren(await MathJax.tex2svgPromise(`\\ket{${count},${index}}`, { display: false }));
    }
  }

  function showState() {
    const count = stars.length;
    const coefficients = stateOf(stars);
    const fidelity = coherentOverlap(coefficients);
    const entanglement = fidelity > 1e-12 ? -Math.log2(fidelity) : 0;
    byId('majorana-title').textContent = `${label}, n = ${count}`;
    byId('majorana-count').textContent = String(count);
    byId('majorana-spin').textContent = spinLength(stars).toFixed(3);
    byId('majorana-fidelity').textContent = fidelity.toFixed(3);
    byId('majorana-entanglement').textContent = entanglement.toFixed(3);
    showPolynomial(polynomialTex(coefficients));
    if (count !== ketCount) {
      ketCount = count;
      showKets(count);
    }
    rows.forEach((row, index) => {
      if (!row) return;
      const value = coefficients[index] || [0, 0];
      row.classList.toggle('is-empty', index > count);
      byId(`majorana-amp-${index}`).textContent = complexText(value, 3);
      byId(`majorana-mag-${index}`).textContent = cAbs(value).toFixed(3);
      byId(`majorana-phase-${index}`).textContent = phaseText(value);
    });
    return coefficients;
  }

  // ---- controls --------------------------------------------------------------------------------------
  const numberSlider = byId('majorana-n');
  const kSlider = byId('majorana-k');
  const thetaSlider = byId('majorana-theta');
  const phiSlider = byId('majorana-phi');

  function syncStarSliders() {
    const point = stars[selected] || [0, 0, 1];
    const theta = Math.acos(clamp(point[2])) * R2D;
    const phi = ((Math.atan2(point[1], point[0]) * R2D) + 360) % 360;
    thetaSlider.value = String(Math.round(theta));
    phiSlider.value = String(Math.round(phi));
    byId('majorana-theta-value').textContent = `${Math.round(theta)}°`;
    byId('majorana-phi-value').textContent = `${Math.round(phi)}°`;
    byId('majorana-star-value').textContent = String(selected + 1);
    menu.value = String(selected);
  }

  function syncKSlider() {
    kSlider.max = String(Math.max(1, stars.length - 1));
    const value = Math.min(Number(kSlider.value), Number(kSlider.max));
    kSlider.value = String(value);
    byId('majorana-k-value').textContent = String(value);
  }

  function draw() {
    camera();
    drawGrid();
    drawAxes();
    placeStars();
    showState();
    syncKSlider();
    syncStarSliders();
  }

  function setStars(next, name, source) {
    stars = next.map(unit);
    label = name;
    preset = source;
    if (selected > stars.length - 1) selected = stars.length - 1;
    draw();
  }

  function presetStates(name) {
    const count = stars.length;
    if (name === 'cat') {
      const amplitudes = Array.from({ length: count + 1 }, (_, index) =>
        (index === 0 || index === count ? [1 / Math.SQRT2, 0] : [0, 0]));
      return [starsOf(amplitudes), 'Cat'];
    }
    if (name === 'coherent') {
      const direction = stars[0] || [0, 0, 1];
      return [Array.from({ length: count }, () => direction), 'Coherent'];
    }
    if (name === 'dicke' || name === 'w') {
      const excited = name === 'w' ? 1 : Math.min(Number(kSlider.value), count - 1);
      const amplitudes = Array.from({ length: count + 1 }, (_, index) => (index === excited ? [1, 0] : [0, 0]));
      return [starsOf(amplitudes), name === 'w' ? 'One excitation' : `Dicke |${count},${excited}⟩`];
    }
    const amplitudes = Array.from({ length: count + 1 }, () =>
      cScale(cExp(2 * Math.PI * Math.random()), Math.sqrt(-2 * Math.log(1 - Math.random()))));
    return [starsOf(amplitudes), 'Random'];
  }

  numberSlider.addEventListener('input', () => {
    const count = Number(numberSlider.value);
    byId('majorana-n-value').textContent = String(count);
    stars = stars.slice(0, count).map(unit);
    while (stars.length < count) stars.push([0, 0, 1]);
    if (selected > count - 1) selected = count - 1;
    buildStars(count);
    // A prepared state is rebuilt at the new size, so raising n keeps a cat a cat.
    const [next, name] = preset ? presetStates(preset) : [stars, 'Custom'];
    setStars(next, name, preset);
  });

  kSlider.addEventListener('input', () => {
    syncKSlider();
    const [next, name] = presetStates('dicke');
    setStars(next, name, 'dicke');
  });

  Array.from(document.querySelectorAll('[data-majorana-preset]')).forEach(button => {
    button.addEventListener('click', () => {
      const [next, name] = presetStates(button.dataset.majoranaPreset);
      // A random draw is a one-off: raising n enlarges it rather than drawing again.
      setStars(next, name, button.dataset.majoranaPreset === 'random' ? null : button.dataset.majoranaPreset);
    });
  });

  menu.addEventListener('change', () => {
    selected = Number(menu.value);
    draw();
  });

  const readAngles = () => {
    const theta = Number(thetaSlider.value) * D2R, phi = Number(phiSlider.value) * D2R;
    byId('majorana-theta-value').textContent = `${thetaSlider.value}°`;
    byId('majorana-phi-value').textContent = `${phiSlider.value}°`;
    stars[selected] = [Math.sin(theta) * Math.cos(phi), Math.sin(theta) * Math.sin(phi), Math.cos(theta)];
    label = 'Custom';
    preset = null;
    draw();
  };
  thetaSlider.addEventListener('input', readAngles);
  phiSlider.addEventListener('input', readAngles);

  // ---- orbiting, and dragging a star along the sphere -------------------------------------------------
  let orbit = null, drag = null;

  const orbitTo = (nextAzimuth, nextElevation) => {
    azimuth = ((nextAzimuth % 360) + 360) % 360;
    elevation = Math.max(-85, Math.min(85, nextElevation));
    camera();
    drawGrid();
    drawAxes();
    placeStars();
  };

  // Screen point to the sphere point in front of the camera; the limb is the equator seen edge on.
  const pointAt = (x, y) => {
    const a = (x - S_CENTER) / S_RADIUS, b = (S_CENTER - y) / S_RADIUS;
    const flat = a * a + b * b;
    const shrink = flat > 1 ? 1 / Math.sqrt(flat) : 1;
    const depth = -Math.sqrt(Math.max(0, 1 - flat));
    return unit([0, 1, 2].map(axis => a * shrink * right[axis] + b * shrink * up[axis] + depth * forward[axis]));
  };

  const localPoint = event => {
    const box = sphere.getBoundingClientRect();
    return [(event.clientX - box.left) * (400 / box.width), (event.clientY - box.top) * (400 / box.height)];
  };

  const nearestStar = ([x, y]) => {
    let best = -1, closest = 16;
    stars.forEach((point, index) => {
      const [sx, sy] = project(point);
      const distance = Math.hypot(sx - x, sy - y);
      if (distance < closest) { best = index; closest = distance; }
    });
    return best;
  };

  sphere.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    const local = localPoint(event);
    const hit = nearestStar(local);
    if (hit >= 0) {
      selected = hit;
      drag = { pointer: event.pointerId };
      sphere.classList.add('is-dragging');
      placeStars();
      syncStarSliders();
    } else {
      orbit = { x: event.clientX, y: event.clientY };
      sphere.classList.add('is-orbiting');
    }
    if (sphere.setPointerCapture) sphere.setPointerCapture(event.pointerId);
    // preventDefault() cancels the implicit focus, so take it explicitly for the arrow keys.
    sphere.focus({ preventScroll: true });
    event.preventDefault();
  });

  sphere.addEventListener('pointermove', event => {
    if (drag) {
      const [x, y] = localPoint(event);
      stars[selected] = pointAt(x, y);
      label = 'Custom';
      preset = null;
      placeStars();
      showState();
      syncStarSliders();
      return;
    }
    if (!orbit) return;
    orbitTo(azimuth - (event.clientX - orbit.x) * 0.4, elevation + (event.clientY - orbit.y) * 0.4);
    orbit = { x: event.clientX, y: event.clientY };
  });

  const stop = () => {
    orbit = null;
    drag = null;
    sphere.classList.remove('is-orbiting', 'is-dragging');
  };
  sphere.addEventListener('pointerup', stop);
  sphere.addEventListener('pointercancel', stop);

  sphere.addEventListener('keydown', event => {
    const step = event.shiftKey ? 15 : 5;
    if (event.key === 'ArrowLeft') orbitTo(azimuth - step, elevation);
    else if (event.key === 'ArrowRight') orbitTo(azimuth + step, elevation);
    else if (event.key === 'ArrowUp') orbitTo(azimuth, elevation + step);
    else if (event.key === 'ArrowDown') orbitTo(azimuth, elevation - step);
    else return;
    event.preventDefault();
  });

  byId('majorana-reset-view').addEventListener('click', () => {
    orbitTo(HOME.azimuth, HOME.elevation);
    byId('majorana-status').textContent = 'View reset.';
  });

  // ---- start from the constellation the build drew, at full precision ----------------------------------
  stars = (sphere.dataset.stars || '').split(' ').filter(Boolean)
    .map(pair => unit(pair.split(',').map(Number)));
  label = 'Cat';
  preset = 'cat';
  selected = 0;
  buildStars(stars.length);
  draw();
})();
