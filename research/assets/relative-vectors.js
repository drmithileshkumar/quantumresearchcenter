// One frame for both qubits: the state maps each observer vector o to the observed vector v = Cᵀo.
(() => {
  const root = document.getElementById('relative-vectors');
  if (!root) return;
  root.hidden = false;
  const $ = id => document.getElementById(id);
  const sliders = {weight: $('rv-weight'), gap: $('rv-gap'), observer: $('rv-observer'), observed: $('rv-observed')};
  const presets = {product: [.6, 0], partial: [.6, 60], bell: [.5, 90]};
  const NS = 'http://www.w3.org/2000/svg';
  const SCALE = 118;
  const rad = d => d * Math.PI / 180, deg = r => r * 180 / Math.PI;
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
  const cross = (a, b) => a[0] * b[1] - a[1] * b[0];
  const OFFSET = 15; // The first vector starts off-axis, so the initial basis is visibly not the Schmidt basis.
  let frame = null;

  const unrotated = () => {
    const w = +sliders.weight.value, gap = rad(+sliders.gap.value), start = rad(OFFSET);
    return [[Math.sqrt(w) * Math.cos(start), Math.sqrt(w) * Math.sin(start)],
            [Math.sqrt(1 - w) * Math.cos(start + gap), Math.sqrt(1 - w) * Math.sin(start + gap)]];
  };
  const turned = ([a, b], phi) => {
    const c = Math.cos(phi), s = Math.sin(phi);
    return [[c * a[0] + s * b[0], c * a[1] + s * b[1]], [-s * a[0] + c * b[0], -s * a[1] + c * b[1]]];
  };
  const observerAngle = ([a, b]) => deg(Math.atan2(2 * dot(a, b), dot(a, a) - dot(b, b))) / 2;
  const observedAngle = ([a, b]) => dot(a, a) > 1e-9 ? deg(Math.atan2(a[1], a[0])) : deg(Math.atan2(b[1], b[0])) - 90;
  const fixed3 = x => { const t = x.toFixed(3); return /^-0\.0+$/.test(t) ? t.slice(1) : t.replace('-', '−'); };
  const wrap = d => ((d + 180) % 360 + 360) % 360 - 180;
  const wrapHalf = d => ((d + 90) % 180 + 180) % 180 - 90;
  // Relative states are rays, so v and −v count as the same state. Null if either has no weight.
  const rayAngle = (a, b) => {
    const size = Math.hypot(...a) * Math.hypot(...b);
    return size < 1e-6 ? null : deg(Math.acos(Math.min(1, Math.abs(dot(a, b)) / size)));
  };
  // The angle is 90° on the principal axes and smallest halfway between them.
  const rayRange = base => {
    const [a, b] = turned(base, rad(observerAngle(base) + 45));
    return [rayAngle(a, b), 90];
  };

  function make(parent, tag, attrs, text) {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    if (text) el.textContent = text;
    parent.append(el);
    return el;
  }
  function arrow(parent, x, y, cls, label, gap = 14) {
    const len = Math.hypot(x, y);
    if (len < 1) return;
    const ux = x / len, uy = y / len, size = Math.min(9, len);
    make(parent, 'line', {x1: 0, y1: 0, x2: x - ux * size, y2: y - uy * size, class: cls});
    make(parent, 'path', {d: `M${x} ${y}L${x - ux * size - uy * 4} ${y - uy * size + ux * 4}L${x - ux * size + uy * 4} ${y - uy * size - ux * 4}Z`, class: `${cls} rv-head`});
    if (label) make(parent, 'text', {x: x - ux * 16 + uy * gap, y: y - uy * 16 - ux * gap + 4, 'text-anchor': 'middle', class: cls}, label);
  }
  const point = (x, y) => [x * SCALE, -y * SCALE];

  function draw() {
    const phi = +sliders.observer.value, theta = +sliders.observed.value;
    const base = unrotated(), [v0, v1] = turned(base, rad(phi));
    const [m0, m1] = turned(base, rad(observerAngle(base)));
    const a = Math.hypot(...m0), b = Math.hypot(...m1), tilt = deg(Math.atan2(m0[1], m0[0]));
    const o0 = [Math.cos(rad(phi)), Math.sin(rad(phi))], o1 = [-Math.sin(rad(phi)), Math.cos(rad(phi))];

    const plot = $('rv-plot');
    plot.replaceChildren();
    make(plot, 'circle', {r: SCALE, class: 'rv-guide'});
    for (const [angle, label] of [[theta, 's₀'], [theta + 90, 's₁']]) {
      const x = Math.cos(rad(angle)) * (SCALE + 26), y = -Math.sin(rad(angle)) * (SCALE + 26);
      make(plot, 'line', {x1: -x, y1: -y, x2: x, y2: y, class: 'rv-axis'});
      make(plot, 'text', {x: x * 1.08, y: y * 1.08 + 4, 'text-anchor': 'middle', class: 'rv-axis-label'}, label);
    }
    const [ox0, oy0] = point(...o0), [ox1, oy1] = point(...o1);
    make(plot, 'line', {x1: 0, y1: 0, x2: ox0, y2: oy0, class: 'rv-zero rv-basis-line'});
    make(plot, 'line', {x1: 0, y1: 0, x2: ox1, y2: oy1, class: 'rv-one rv-basis-line'});
    const mark = 10 / SCALE;
    make(plot, 'path', {d: `M${ox0 * mark} ${oy0 * mark}L${(ox0 + ox1) * mark} ${(oy0 + oy1) * mark}L${ox1 * mark} ${oy1 * mark}`, class: 'rv-right-angle'});
    make(plot, 'ellipse', {rx: Math.max(a * SCALE, .01), ry: Math.max(b * SCALE, .01), transform: `rotate(${-tilt})`, class: 'rv-ellipse'});
    for (const [v, cls] of [[v0, 'rv-zero'], [v1, 'rv-one']]) {
      const len = Math.hypot(...v);
      if (len < 1e-6) continue;
      const [x, y] = point(v[0] / len, v[1] / len);
      make(plot, 'line', {x1: -x, y1: -y, x2: x, y2: y, class: `${cls} rv-ray`});
    }
    for (const [o, v, cls] of [[o0, v0, 'rv-zero'], [o1, v1, 'rv-one']]) {
      const [x1, y1] = point(...o), [x2, y2] = point(...v);
      make(plot, 'line', {x1, y1, x2, y2, class: `${cls} rv-link`});
      make(plot, 'circle', {cx: x1, cy: y1, r: 5, class: `${cls} rv-basis`});
    }
    for (const [o, label, cls] of [[o0, 'o₀', 'rv-zero'], [o1, 'o₁', 'rv-one']]) {
      const [x, y] = point(...o);
      make(plot, 'text', {x: x * 1.13, y: y * 1.13 + 4, 'text-anchor': 'middle', class: cls}, label);
    }
    arrow(plot, ...point(...v0), 'rv-zero', 'v₀');
    arrow(plot, ...point(...v1), 'rv-one', 'v₁');

    const c = Math.cos(rad(theta)), s = Math.sin(rad(theta));
    const amps = [[c * v0[0] + s * v0[1], -s * v0[0] + c * v0[1]], [c * v1[0] + s * v1[1], -s * v1[0] + c * v1[1]]];
    ['00', '01', '10', '11'].forEach(k => { $(`rv-c${k}`).textContent = fixed3(amps[+k[0]][+k[1]]); });
    for (const [prefix, angle] of [['rv-uo', phi], ['rv-us', theta]]) {
      const cos = Math.cos(rad(angle)), sin = Math.sin(rad(angle));
      [[`${prefix}00`, cos], [`${prefix}01`, sin], [`${prefix}10`, -sin], [`${prefix}11`, cos]].forEach(([id, value]) => { $(id).textContent = fixed3(value); });
    }
    [[0, 0], [0, 1], [1, 0], [1, 1]].forEach(([i, j]) => { $(`rv-r${i}${j}`).textContent = fixed3(o0[i] * v0[j] + o1[i] * v1[j]); });
    const grams = [dot(o0, o0), dot(o1, o1), dot(o0, o1)];
    const orthonormal = Math.abs(grams[0] - 1) < 1e-9 && Math.abs(grams[1] - 1) < 1e-9 && Math.abs(grams[2]) < 1e-9;
    $('rv-orthonormal').textContent = orthonormal ? 'Yes' : 'No';
    $('rv-grams').textContent = grams.map(fixed3).join(', ');
    const drift = Math.max(...[0, 1].flatMap(i => [0, 1].map(j => Math.abs(o0[i] * v0[j] + o1[i] * v1[j] - base[i][j]))));
    $('rv-same').textContent = drift < 1e-9 ? 'Yes' : `No, off by ${drift.toFixed(3)}`;
    const diagonal = Math.abs(amps[0][1]) < .002 && Math.abs(amps[1][0]) < .002;
    const round = Math.abs(a - b) < 1e-6, flat = b < 1e-6;
    const now = rayAngle(v0, v1), [low, high] = flat ? [0, 0] : rayRange(base);
    $('rv-angle').textContent = now === null ? 'one arrow has no weight' : `${now.toFixed(1)}°`;
    $('rv-range').textContent = flat ? '0.0° always' : `${low.toFixed(1)}° to ${high.toFixed(1)}°`;
    $('rv-schmidt').textContent = `${(a * a).toFixed(3)} and ${(b * b).toFixed(3)}`;
    $('rv-concurrence').textContent = (2 * Math.abs(cross(v0, v1))).toFixed(3);
    $('rv-weights').textContent = `${dot(v0, v0).toFixed(3)} and ${dot(v1, v1).toFixed(3)}`;
    $('rv-weight-out').textContent = (+sliders.weight.value).toFixed(2);
    $('rv-gap-out').textContent = `${sliders.gap.value}°`;
    $('rv-observer-out').textContent = `${phi.toFixed(1)}°`.replace('-', '−');
    $('rv-observed-out').textContent = `${theta.toFixed(1)}°`.replace('-', '−');
    let status;
    if (flat) status = 'Separable: every observer basis lands on the same line. Only the arrow lengths change, so the observer finds the same observed state whichever basis it uses.';
    else if (round) status = diagonal ? 'Maximally entangled, in a Schmidt basis. Any observer basis has orthogonal arrows here, so this choice is one of many.' : 'Maximally entangled: the arrows are orthogonal in every observer basis, but their direction depends on the basis.';
    else if (diagonal) status = 'Schmidt basis: the arrows lie on the ellipse’s axes, and the amplitude table is diagonal.';
    else if (Math.abs(dot(v0, v1)) < .001) status = 'Observer basis chosen: the arrows are orthogonal. Now choose the observed basis along them.';
    else status = 'Entangled: the observed state depends on the observer’s basis. Choose another observer basis and the arrows change, but the ellipse, which belongs to the state, stays put.';
    $('rv-status').textContent = status;
    $('rv-svg').setAttribute('aria-label', `Common frame. Observer basis at ${phi.toFixed(0)} degrees. Arrow v0 at (${v0[0].toFixed(2)}, ${v0[1].toFixed(2)}), arrow v1 at (${v1[0].toFixed(2)}, ${v1[1].toFixed(2)}), on an ellipse with semi-axes ${a.toFixed(2)} and ${b.toFixed(2)}.`);
  }

  const stop = () => { if (frame) { cancelAnimationFrame(frame); frame = null; } };
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  function run(duration, update, finish) {
    stop();
    if (reduced()) { finish(); draw(); return; }
    const began = performance.now();
    const step = now => {
      const t = Math.min(1, (now - began) / duration);
      if (t === 1) { frame = null; finish(); draw(); return; }
      update(t);
      draw();
      frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
  }
  function animate(targets) {
    const starts = targets.map(([slider]) => +slider.value);
    run(700, t => {
      const eased = t * t * (3 - 2 * t);
      targets.forEach(([slider, end], i) => { slider.value = starts[i] + (end - starts[i]) * eased; });
    }, () => targets.forEach(([slider, end]) => { slider.value = end; }));
  }

  const toObserver = () => animate([[sliders.observer, observerAngle(unrotated())]]);
  const toObserved = () => animate([[sliders.observed, wrap(observedAngle(turned(unrotated(), rad(+sliders.observer.value))))]]);
  const toSchmidt = () => {
    const phi = observerAngle(unrotated());
    animate([[sliders.observer, phi], [sliders.observed, wrap(observedAngle(turned(unrotated(), rad(phi))))]]);
  };
  // One half-turn covers every observer basis, because φ + 180° only flips the signs of both vectors.
  const sweep = () => {
    const start = +sliders.observer.value;
    run(4000, t => { sliders.observer.value = wrapHalf(start + 180 * t); }, () => { sliders.observer.value = start; });
  };
  $('rv-rotate-observer').addEventListener('click', toObserver);
  $('rv-rotate-observed').addEventListener('click', toObserved);
  $('rv-go-schmidt').addEventListener('click', toSchmidt);
  $('rv-sweep').addEventListener('click', sweep);
  $('rv-reset').addEventListener('click', () => animate([[sliders.observer, 0], [sliders.observed, 0]]));
  for (const slider of Object.values(sliders)) slider.addEventListener('input', () => { stop(); draw(); });
  for (const button of root.querySelectorAll('[data-preset]')) button.addEventListener('click', () => {
    stop();
    [sliders.weight.value, sliders.gap.value] = presets[button.dataset.preset];
    sliders.observer.value = 0;
    sliders.observed.value = 0;
    draw();
  });
  draw();
})();
