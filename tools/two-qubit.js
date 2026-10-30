/* Two-qubit explorer: the four amplitudes and the concurrence needle, all in one complex plane.
   Pure states only — unitary gates and projective measurement never leave the pure-state space. */
(() => {
  'use strict';
  const svg = document.getElementById('phasor');
  if (!svg) return;
  const CENTER = 220, RADIUS = 156, ZERO = 5e-4;
  const R2D = 180 / Math.PI, D2R = Math.PI / 180;
  const KEYS = ['00', '01', '10', '11'];
  const LABELS = ['|00⟩', '|01⟩', '|10⟩', '|11⟩'];
  const BELL_LABELS = ['Φ⁺', 'Φ⁻', 'Ψ⁺', 'Ψ⁻'];

  const byId = id => document.getElementById(id);
  const parts = {
    ket: byId('state-ket'), concurrence: byId('inv-concurrence'), needle: byId('inv-needle'),
    schmidt: byId('inv-schmidt'), type: byId('inv-type'), barC: byId('bar-c'),
    status: byId('state-status'), result: byId('measure-result'), tally: byId('measure-tally'),
    desc: byId('phasor-desc'), basisHint: byId('basis-hint'),
    computational: byId('basis-computational'), bell: byId('basis-bell'),
  };
  if (Object.values(parts).some(element => !element)) return;

  // ---- complex arithmetic on [re, im] pairs ------------------------------------------------
  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1]];
  const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  const abs2 = a => a[0] * a[0] + a[1] * a[1];
  const size = a => Math.sqrt(abs2(a));
  const scale = (a, s) => [a[0] * s, a[1] * s];
  const phaseOf = a => (size(a) < ZERO ? 0 : (Math.atan2(a[1], a[0]) * R2D + 360) % 360);

  const fixed = (value, digits = 3) => {
    const rounded = Math.abs(value) < ZERO ? 0 : value;
    return (rounded < 0 ? '−' : '') + Math.abs(rounded).toFixed(digits);
  };

  function complexText(c) {
    if (Math.abs(c[1]) < ZERO) return fixed(c[0]);
    if (Math.abs(c[0]) < ZERO) return fixed(c[1]) + 'i';
    return fixed(c[0]) + (c[1] < 0 ? ' − ' : ' + ') + fixed(Math.abs(c[1])) + 'i';
  }

  // ---- gates ------------------------------------------------------------------------------
  const SQ = Math.SQRT1_2;
  const GATES = {
    X: [[[0, 0], [1, 0]], [[1, 0], [0, 0]]],
    Y: [[[0, 0], [0, -1]], [[0, 1], [0, 0]]],
    Z: [[[1, 0], [0, 0]], [[0, 0], [-1, 0]]],
    H: [[[SQ, 0], [SQ, 0]], [[SQ, 0], [-SQ, 0]]],
    S: [[[1, 0], [0, 0]], [[0, 0], [0, 1]]],
    T: [[[1, 0], [0, 0]], [[0, 0], [SQ, SQ]]],
  };
  const PRESETS = {
    '00': [[1, 0], [0, 0], [0, 0], [0, 0]],
    '11': [[0, 0], [0, 0], [0, 0], [1, 0]],
    '++': [[0.5, 0], [0.5, 0], [0.5, 0], [0.5, 0]],
    'phi+': [[SQ, 0], [0, 0], [0, 0], [SQ, 0]],
    'phi-': [[SQ, 0], [0, 0], [0, 0], [-SQ, 0]],
    'psi+': [[0, 0], [SQ, 0], [SQ, 0], [0, 0]],
    'psi-': [[0, 0], [SQ, 0], [-SQ, 0], [0, 0]],
    partial: [[Math.cos(Math.PI / 8), 0], [0, 0], [0, 0], [Math.sin(Math.PI / 8), 0]],
  };

  let state = PRESETS['00'].map(c => [...c]);
  let basis = 'computational';
  let counts = [0, 0, 0, 0];

  const gateOn = (matrix, wire) => {
    // Index 2a+b: wire 0 is the first (left) qubit of the ket.
    const next = state.map(() => [0, 0]);
    for (let a = 0; a < 2; a++) {
      for (let b = 0; b < 2; b++) {
        let total = [0, 0];
        for (let other = 0; other < 2; other++) {
          const source = wire === 0 ? 2 * other + b : 2 * a + other;
          total = add(total, mul(matrix[wire === 0 ? a : b][other], state[source]));
        }
        next[2 * a + b] = total;
      }
    }
    state = next;
  };

  const TWO_QUBIT_GATES = { CNOT: [0, 1, 3, 2], SWAP: [0, 2, 1, 3] };
  const applyTwoQubit = name => {
    if (name === 'CZ') {
      state = state.map((c, index) => (index === 3 ? scale(c, -1) : c));
    } else if (TWO_QUBIT_GATES[name]) {
      state = TWO_QUBIT_GATES[name].map(source => state[source]);
    }
  };

  // ---- the two views of the same state -----------------------------------------------------
  const displayState = () => {
    if (basis === 'computational') return state;
    // Φ⁺ = (|00⟩+|11⟩)/√2, Φ⁻ = (|00⟩−|11⟩)/√2, Ψ⁺ = (|01⟩+|10⟩)/√2, Ψ⁻ = (|01⟩−|10⟩)/√2.
    return [scale(add(state[0], state[3]), SQ), scale(sub(state[0], state[3]), SQ),
            scale(add(state[1], state[2]), SQ), scale(sub(state[1], state[2]), SQ)];
  };

  const concurrence = () => 2 * size(sub(mul(state[0], state[3]), mul(state[1], state[2])));

  // ---- drawing ------------------------------------------------------------------------------
  const tip = (magnitude, degrees) => [
    CENTER + RADIUS * magnitude * Math.cos(degrees * D2R),
    CENTER - RADIUS * magnitude * Math.sin(degrees * D2R),
  ];

  function place(line, magnitude, degrees, from, offset = 0) {
    // A lateral offset keeps coincident arrows visible side by side; it never changes a length.
    const shift = [offset * Math.sin(degrees * D2R), offset * Math.cos(degrees * D2R)];
    const [x, y] = tip(magnitude, degrees);
    line.setAttribute('x1', (from[0] + shift[0]).toFixed(1));
    line.setAttribute('y1', (from[1] + shift[1]).toFixed(1));
    line.setAttribute('x2', (x + shift[0]).toFixed(1));
    line.setAttribute('y2', (y + shift[1]).toFixed(1));
    return [x + shift[0], y + shift[1]];
  }

  // Arrows that land on top of each other would hide one another, so give each a small fan-out.
  // Each entry is [magnitude, degrees]; the offsets returned line up with the input.
  function fanOffsets(vectors, spacing) {
    const groups = [];
    const offsets = vectors.map(() => 0);
    vectors.forEach(([magnitude, degrees], index) => {
      if (magnitude < ZERO) return;
      const near = groups.find(group => Math.abs(group.magnitude - magnitude) < 0.04
        && Math.abs(group.degrees - degrees) < 6);
      if (near) near.members.push(index);
      else groups.push({ magnitude, degrees, members: [index] });
    });
    groups.forEach(group => {
      const count = group.members.length;
      group.members.forEach((index, position) => {
        offsets[index] = (position - (count - 1) / 2) * spacing;
      });
    });
    return offsets;
  }

  function placeLabel(text, x, y, lateral = 0) {
    // Labels ride a fixed ring outside the rim, fanned sideways when arrows coincide, so a label
    // never lands on another arrow's shaft.
    const radius = Math.hypot(x - CENTER, y - CENTER) || 1;
    const nx = (x - CENTER) / radius, ny = (y - CENTER) / radius;
    const ring = RADIUS + 20;
    text.setAttribute('x', (CENTER + ring * nx - lateral * ny).toFixed(1));
    text.setAttribute('y', (CENTER + ring * ny + lateral * nx).toFixed(1));
  }

  function drawArrows(offsets, labelOffsets) {
    const amplitudes = displayState();
    const labels = basis === 'computational' ? LABELS : BELL_LABELS;
    amplitudes.forEach((amplitude, index) => {
      const key = KEYS[index];
      const group = byId(`ph-group-${key}`);
      const line = byId(`ph-vec-${key}`);
      const text = byId(`ph-vec-${key}-label`);
      const magnitude = size(amplitude);
      const degrees = phaseOf(amplitude);
      const [x, y] = place(line, magnitude, degrees, [CENTER, CENTER], offsets[index]);
      const hit = group.querySelector('.ph-hit');
      if (hit) for (const name of ['x1', 'y1', 'x2', 'y2']) hit.setAttribute(name, line.getAttribute(name));
      text.textContent = labels[index];
      placeLabel(text, x, y, labelOffsets[index]);
      text.setAttribute('text-anchor', x < CENTER - 1 ? 'end' : 'start');
      group.classList.toggle('is-empty', magnitude < ZERO);
      const interactive = basis === 'computational';
      group.setAttribute('tabindex', interactive ? '0' : '-1');
      group.setAttribute('role', interactive ? 'button' : 'img');
      group.setAttribute('aria-label', interactive
        ? `${labels[index]}: magnitude ${magnitude.toFixed(3)}, phase ${degrees.toFixed(0)} degrees.`
          + ' Use the left and right arrow keys to turn it.'
        : `${labels[index]}: magnitude ${magnitude.toFixed(3)}, phase ${degrees.toFixed(0)} degrees.`);
    });
  }

  function drawNeedle(offset) {
    const first = scale(mul(state[0], state[3]), 2);
    const second = scale(mul(state[1], state[2]), 2);
    const needle = sub(first, second);
    const magnitude = size(needle);
    const degrees = phaseOf(needle);

    const pairing = byId('ph-pairing');
    pairing.classList.toggle('is-empty',
      !byId('show-products').checked || Math.max(size(first), size(second)) < ZERO);
    const firstTip = place(byId('ph-p1'), size(first), phaseOf(first), [CENTER, CENTER]);
    // Drawn head to tail, so the gap between them is the subtraction.
    place(byId('ph-p2'), size(second), (phaseOf(second) + 180) % 360, firstTip);

    const group = byId('ph-needle-group');
    group.classList.toggle('is-empty', magnitude < ZERO);
    place(byId('ph-needle-halo'), magnitude, degrees, [CENTER, CENTER], offset);
    place(byId('ph-needle'), magnitude, degrees, [CENTER, CENTER], offset);

    // The label rides partway along the arrow, clear of both the tip and the rim.
    const label = byId('ph-needle-label');
    label.textContent = magnitude < ZERO ? '' : `C = ${magnitude.toFixed(3)}`;
    const [x, y] = tip(magnitude * 0.35, degrees);
    const nx = (x - CENTER) / Math.max(1, Math.hypot(x - CENTER, y - CENTER));
    const ny = (y - CENTER) / Math.max(1, Math.hypot(x - CENTER, y - CENTER));
    label.setAttribute('x', (x - 14 * ny).toFixed(1));
    label.setAttribute('y', (y + 14 * nx + 4).toFixed(1));
  }

  function drawTable() {
    const amplitudes = displayState();
    const labels = basis === 'computational' ? LABELS : BELL_LABELS;
    amplitudes.forEach((amplitude, index) => {
      const key = KEYS[index];
      byId(`amp-name-${key}`).textContent = labels[index];
      byId(`amp-mag-${key}`).textContent = size(amplitude).toFixed(3);
      byId(`amp-phase-${key}`).textContent = size(amplitude) < ZERO ? '—' : phaseOf(amplitude).toFixed(0) + '°';
      byId(`amp-prob-${key}`).textContent = abs2(amplitude).toFixed(3);
    });
  }

  function ketText() {
    const terms = [];
    state.forEach((amplitude, index) => {
      if (size(amplitude) < ZERO) return;
      const negative = (Math.abs(amplitude[0]) < ZERO && amplitude[1] < 0)
        || (Math.abs(amplitude[1]) < ZERO && amplitude[0] < 0);
      let coefficient = complexText(negative ? scale(amplitude, -1) : amplitude);
      if (coefficient.includes(' ')) coefficient = '(' + coefficient + ')';
      const exact = Math.abs(amplitude[0] - 1) < 1e-9 && Math.abs(amplitude[1]) < 1e-9;
      terms.push({ negative, coefficient, label: LABELS[index], exact });
    });
    if (!terms.length) return '0';
    return terms.map((item, index) => {
      const sign = index === 0 ? (item.negative ? '−' : '') : (item.negative ? ' − ' : ' + ');
      const coefficient = terms.length === 1 && item.exact ? '' : item.coefficient;
      return sign + coefficient + item.label;
    }).join('');
  }

  const describeType = c => (c < ZERO ? 'Product' : c > 1 - ZERO ? 'Maximally entangled' : 'Entangled');

  function render(announce) {
    const total = state.reduce((sum, c) => sum + abs2(c), 0);
    if (Math.abs(total - 1) > 1e-9) state = state.map(c => scale(c, 1 / Math.sqrt(total)));

    const c = concurrence();
    const spread = Math.sqrt(Math.max(0, 1 - c * c));
    parts.ket.textContent = ketText();
    parts.concurrence.textContent = c.toFixed(3);
    const needlePhase = phaseOf(sub(scale(mul(state[0], state[3]), 2), scale(mul(state[1], state[2]), 2)));
    parts.needle.textContent = c < ZERO ? '—' : needlePhase.toFixed(0) + '°';
    parts.schmidt.textContent = `${Math.sqrt((1 + spread) / 2).toFixed(3)}, `
      + `${Math.sqrt((1 - spread) / 2).toFixed(3)}`;
    parts.type.textContent = describeType(c);
    parts.barC.style.width = (c * 100).toFixed(1) + '%';

    // Arrows and the needle share one fan group, so a needle lying on an arrow steps aside too.
    const shown = displayState();
    const needle = sub(scale(mul(state[0], state[3]), 2), scale(mul(state[1], state[2]), 2));
    const vectors = shown.map(a => [size(a), phaseOf(a)]).concat([[size(needle), phaseOf(needle)]]);
    const offsets = fanOffsets(vectors, 5);
    drawArrows(offsets, fanOffsets(vectors, 16));
    drawNeedle(offsets[4]);
    drawTable();

    parts.desc.textContent = `${ketText()}. The arrows show the state in the `
      + `${basis === 'computational' ? 'computational' : 'Bell'} basis; the concurrence needle has length `
      + `${c.toFixed(3)}.`;
    if (announce) {
      parts.status.textContent = `${ketText()}. Concurrence ${c.toFixed(3)}, ${describeType(c).toLowerCase()}.`;
    }
  }

  // ---- direct manipulation of one phase -----------------------------------------------------
  const angleFromPointer = event => {
    const matrix = svg.getScreenCTM();
    if (!matrix) return null;
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const local = point.matrixTransform(matrix.inverse());
    return ((Math.atan2(CENTER - local.y, local.x - CENTER) * R2D) + 360) % 360;
  };

  const turnTo = (index, degrees) => {
    const magnitude = size(state[index]);
    state[index] = [magnitude * Math.cos(degrees * D2R), magnitude * Math.sin(degrees * D2R)];
  };

  let dragging = null;
  document.querySelectorAll('.ph-vec').forEach(group => {
    const index = Number(group.dataset.index);
    group.addEventListener('pointerdown', event => {
      if (basis !== 'computational' || event.button !== 0) return;
      const degrees = angleFromPointer(event);
      if (degrees === null) return;
      dragging = index;
      svg.classList.add('is-dragging');
      if (svg.setPointerCapture) svg.setPointerCapture(event.pointerId);
      turnTo(index, degrees);
      render(false);
      event.preventDefault();
    });
    group.addEventListener('keydown', event => {
      if (basis !== 'computational') return;
      const current = phaseOf(state[index]);
      const step = event.shiftKey ? 15 : 5;
      if (event.key === 'ArrowRight') turnTo(index, current + step);
      else if (event.key === 'ArrowLeft') turnTo(index, current - step);
      else if (event.key === 'Home') turnTo(index, 0);
      else return;
      event.preventDefault();
      render(true);
    });
  });
  svg.addEventListener('pointermove', event => {
    if (dragging === null) return;
    const degrees = angleFromPointer(event);
    if (degrees === null) return;
    turnTo(dragging, degrees);
    render(false);
  });
  const stopDrag = () => {
    if (dragging === null) return;
    dragging = null;
    svg.classList.remove('is-dragging');
    render(true);
  };
  svg.addEventListener('pointerup', stopDrag);
  svg.addEventListener('pointercancel', stopDrag);

  // ---- basis switch ---------------------------------------------------------------------------
  const setBasis = (next, announce = true) => {
    basis = next;
    const computational = basis === 'computational';
    parts.computational.setAttribute('aria-pressed', String(computational));
    parts.bell.setAttribute('aria-pressed', String(!computational));
    parts.basisHint.textContent = computational
      ? 'Computational basis. Drag or arrow-key an arrow to turn that phase; its length stays fixed.'
      : 'Bell basis. Each Bell state is a single arrow here; no product state can be one — |00⟩ needs two'
        + ' arrows and |+0⟩ needs four. A Bell-basis phase would mean a different state, so the arrows are'
        + ' read-only.';
    render(announce);
  };
  parts.computational.addEventListener('click', () => setBasis('computational'));
  parts.bell.addEventListener('click', () => setBasis('bell'));

  // ---- measurement ----------------------------------------------------------------------------
  const tallyText = () => {
    const total = counts.reduce((sum, n) => sum + n, 0);
    if (!total) return 'No joint measurements yet.';
    return `${total} joint measurement${total === 1 ? '' : 's'}: `
      + KEYS.map((key, index) => `${key} × ${counts[index]}`).join(', ') + '.';
  };

  function measure(wire) {
    const probability = [0, 0];
    state.forEach((amplitude, index) => {
      probability[wire === 0 ? (index >> 1) & 1 : index & 1] += abs2(amplitude);
    });
    const outcome = Math.random() < probability[1] ? 1 : 0;
    state = state.map((amplitude, index) => {
      const bit = wire === 0 ? (index >> 1) & 1 : index & 1;
      return bit === outcome ? amplitude : [0, 0];
    });
    const norm = Math.sqrt(state.reduce((sum, c) => sum + abs2(c), 0)) || 1;
    state = state.map(c => scale(c, 1 / norm));
    return { outcome, probability: probability[outcome] };
  }

  function measureBoth() {
    const probability = state.map(abs2);
    const threshold = Math.random();
    let outcome = 0, running = probability[0];
    while (outcome < 3 && threshold > running) { outcome += 1; running += probability[outcome]; }
    const chance = probability[outcome];
    state = state.map((amplitude, index) => (index === outcome ? [1, 0] : [0, 0]));
    return { outcome, probability: chance };
  }

  for (const [id, wire, name] of [['measure-a', 0, 'A'], ['measure-b', 1, 'B']]) {
    byId(id).addEventListener('click', () => {
      const { outcome, probability } = measure(wire);
      render(false);
      parts.result.textContent = `Measured qubit ${name}: outcome ${outcome}`
        + ` (probability ${probability.toFixed(3)}). The pair is now ${ketText()}.`;
      parts.tally.textContent = tallyText();
      parts.status.textContent = `Measured qubit ${name} as ${outcome}; the state is now ${ketText()}.`;
    });
  }

  byId('measure-both').addEventListener('click', () => {
    const { outcome, probability } = measureBoth();
    counts[outcome] += 1;
    render(false);
    parts.result.textContent = `Measured both: outcome |${(outcome >> 1) & 1}⟩|${outcome & 1}⟩`
      + ` (probability ${probability.toFixed(3)}).`;
    parts.tally.textContent = tallyText();
    parts.status.textContent = `Measured both qubits; outcome ${KEYS[outcome]}.`;
  });

  byId('two-reset').addEventListener('click', () => {
    state = PRESETS['00'].map(c => [...c]);
    counts = [0, 0, 0, 0];
    setBasis('computational', false);
    parts.result.textContent = 'Measuring A projects onto |0⟩ or |1⟩ on that qubit. On a Bell state the two'
      + ' outcomes always agree.';
    parts.tally.textContent = tallyText();
    parts.status.textContent = 'Reset to the state |00⟩ with no measurements recorded.';
  });

  document.querySelectorAll('[data-preset]').forEach(button => {
    button.addEventListener('click', () => {
      const preset = PRESETS[button.dataset.preset];
      if (!preset) return;
      state = preset.map(c => [...c]);
      render(true);
    });
  });

  document.querySelectorAll('[data-gate-a]').forEach(button => {
    button.addEventListener('click', () => {
      const matrix = GATES[button.dataset.gateA];
      if (!matrix) return;
      gateOn(matrix, 0);
      render(true);
    });
  });

  document.querySelectorAll('[data-gate-b]').forEach(button => {
    button.addEventListener('click', () => {
      const matrix = GATES[button.dataset.gateB];
      if (!matrix) return;
      gateOn(matrix, 1);
      render(true);
    });
  });

  document.querySelectorAll('[data-gate]').forEach(button => {
    button.addEventListener('click', () => {
      applyTwoQubit(button.dataset.gate);
      render(true);
    });
  });

  byId('show-products').addEventListener('change', () => render(false));

  render(false);
})();
