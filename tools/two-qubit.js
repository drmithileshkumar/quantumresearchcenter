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

  const byId = id => document.getElementById(id);
  const parts = {
    heat: byId('ph-heat-disc'),
    status: byId('state-status'), result: byId('measure-result'), tally: byId('measure-tally'),
    desc: byId('phasor-desc'),
    menuState: byId('menu-state'), menuGateA: byId('menu-gate-a'), menuGateB: byId('menu-gate-b'),
    menuGateTwo: byId('menu-gate-two'), menuMeasure: byId('menu-measure'),
    sDesc: byId('schmidt-desc'), sFormula: byId('schmidt-formula'), sTheta: byId('schmidt-theta'),
    sLambda0: byId('schmidt-lambda-0'), sLambda1: byId('schmidt-lambda-1'), sChi: byId('schmidt-chi'),
    sALine: byId('schmidt-a-line'), sAPlus: byId('schmidt-a-plus'), sAMinus: byId('schmidt-a-minus'),
    sAPlusLabel: byId('schmidt-a-plus-label'), sAMinusLabel: byId('schmidt-a-minus-label'),
    sBAxis: byId('schmidt-b-axis'), sBPlusLine: byId('schmidt-b-plus-line'),
    sBMinusLine: byId('schmidt-b-minus-line'), sBPlus: byId('schmidt-b-plus'),
    sBMinus: byId('schmidt-b-minus'), sBPlusLabel: byId('schmidt-b-plus-label'),
    sBMinusLabel: byId('schmidt-b-minus-label'), sQuad: byId('schmidt-parallelogram'),
    norm: byId('state-norm'), normalize: byId('normalize-arrows'),
  };
  if (Object.values(parts).some(element => !element)) return;
  const sphere = byId('schmidt');
  if (!sphere) return;

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

  // Editing a length can leave the arrows scaling to something other than one. Every physical
  // readout then divides by the weight Σ|c|², so normalization is a rescaling rather than a new
  // state, and stretching an arrow cannot fake entanglement.
  const weight = () => state.reduce((sum, c) => sum + abs2(c), 0);
  const scaled = () => {
    const total = weight();
    return total > ZERO ? state.map(c => scale(c, 1 / Math.sqrt(total))) : state.map(() => [0, 0]);
  };
  // The two products the needle is built from, kept inside the unit disc by the same weight.
  const products = () => {
    const total = weight();
    const factor = total > ZERO ? 2 / total : 0;
    return [scale(mul(state[0], state[3]), factor), scale(mul(state[1], state[2]), factor)];
  };
  const concurrence = () => {
    const [first, second] = products();
    return size(sub(first, second));
  };

  // ---- Schmidt form: one unit basis and one scaled one --------------------------------------
  // Mirrors scripts/schmidt.py: c = cos θ |+a⟩⟨+b| + e^{iχ} sin θ |−a⟩⟨−b|.
  const conj = a => [a[0], -a[1]];
  const divide = (a, b) => {
    const d = abs2(b) || 1;
    return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
  };
  const normalisePair = pair => {
    const length = Math.hypot(size(pair[0]), size(pair[1])) || 1;
    return [scale(pair[0], 1 / length), scale(pair[1], 1 / length)];
  };
  const unit3 = v => {
    const length = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0] / length, v[1] / length, v[2] / length];
  };
  const stretch3 = (v, factor) => [v[0] * factor, v[1] * factor, v[2] * factor];
  const blochOf = pair => {
    const product = mul(conj(pair[0]), pair[1]);
    return [2 * product[0], 2 * product[1], abs2(pair[0]) - abs2(pair[1])];
  };
  const eigenstatesOf = axis => {
    const [x, y, z] = unit3(axis);
    const polar = Math.acos(Math.max(-1, Math.min(1, z)));
    const azimuth = Math.hypot(x, y) > ZERO ? Math.atan2(y, x) : 0;
    const turn = [Math.cos(azimuth), Math.sin(azimuth)];
    const half = polar / 2;
    return [[[Math.cos(half), 0], scale(turn, Math.sin(half))],
            [[Math.sin(half), 0], scale(turn, -Math.cos(half))]];
  };
  const overlapPair = (source, first, second) => source.reduce((sum, amplitude, index) => {
    const bra = mul(conj(first[(index >> 1) & 1]), conj(second[index & 1]));
    return add(sum, mul(bra, amplitude));
  }, [0, 0]);

  function schmidtForm() {
    const amplitudes = scaled();
    const [c00, c01, c10, c11] = amplitudes;
    const row0 = abs2(c00) + abs2(c01), row1 = abs2(c10) + abs2(c11);
    const mixing = add(mul(c00, conj(c10)), mul(c01, conj(c11)));
    const mean = (row0 + row1) / 2;
    const spread = Math.hypot((row0 - row1) / 2, size(mixing));
    const first = Math.sqrt(Math.max(0, mean + spread));
    const determinant = Math.max(0, row0 * row1 - abs2(mixing));
    const second = first > ZERO ? Math.sqrt(determinant) / first : 0;
    let lead;
    if (size(mixing) > ZERO) {
      const candidates = [
        [[mixing[0], mixing[1]], [first * first - row0, 0]],
        [[first * first - row1, 0], [mixing[0], -mixing[1]]],
      ];
      const pairWeight = pair => size(pair[0]) ** 2 + size(pair[1]) ** 2;
      lead = normalisePair(pairWeight(candidates[0]) >= pairWeight(candidates[1])
        ? candidates[0] : candidates[1]);
    } else {
      lead = row0 >= row1 ? [[1, 0], [0, 0]] : [[0, 0], [1, 0]];
    }
    const right = [add(mul(conj(c00), lead[0]), mul(conj(c10), lead[1])),
                   add(mul(conj(c01), lead[0]), mul(conj(c11), lead[1]))];
    const partner = normalisePair([conj(right[0]), conj(right[1])]);
    const axisA = blochOf(lead), axisB = blochOf(partner);
    const theta = Math.atan2(second, first) * R2D;
    let chi = 0;
    if (second > ZERO) {
      const plusA = eigenstatesOf(axisA)[0], minusA = eigenstatesOf(axisA)[1];
      const plusB = eigenstatesOf(axisB)[0], minusB = eigenstatesOf(axisB)[1];
      const weightPlus = overlapPair(amplitudes, plusA, plusB);
      const weightMinus = overlapPair(amplitudes, minusA, minusB);
      if (size(weightPlus) > ZERO && size(weightMinus) > ZERO) chi = phaseOf(divide(weightMinus, weightPlus));
    }
    return { theta, axisA, axisB, chi, first, second };
  }

  const S_CENTER = 200, S_RADIUS = 148;
  const sBasis = (sphere.dataset.basis || '').split(',').map(Number);
  const sRight = sBasis.slice(0, 3), sUp = sBasis.slice(3);
  const sProject = v => [S_CENTER + S_RADIUS * (v[0] * sRight[0] + v[1] * sRight[1] + v[2] * sRight[2]),
                         S_CENTER - S_RADIUS * (v[0] * sUp[0] + v[1] * sUp[1] + v[2] * sUp[2])];
  const setSegment = (line, start, end) => {
    line.setAttribute('x1', start[0].toFixed(1));
    line.setAttribute('y1', start[1].toFixed(1));
    line.setAttribute('x2', end[0].toFixed(1));
    line.setAttribute('y2', end[1].toFixed(1));
  };
  const placeTip = (dot, point) => {
    dot.setAttribute('cx', point[0].toFixed(1));
    dot.setAttribute('cy', point[1].toFixed(1));
  };
  // Labels sit just inside a tip and sideways, clear of the shaft and of the rim's basis labels.
  const placeTipLabel = (label, point, side) => {
    const dx = point[0] - S_CENTER, dy = point[1] - S_CENTER, distance = Math.hypot(dx, dy);
    if (distance < 1) { label.classList.add('is-empty'); return; }
    const ux = dx / distance, uy = dy / distance;
    label.setAttribute('x', (point[0] - ux * 18 - uy * side).toFixed(1));
    label.setAttribute('y', (point[1] - uy * 18 + ux * side).toFixed(1));
    label.setAttribute('text-anchor', 'middle');
  };

  function drawSchmidt() {
    const { theta, axisA, axisB, chi, first, second } = schmidtForm();
    const cos = Math.cos(theta * D2R), sin = Math.sin(theta * D2R);
    const origin = sProject([0, 0, 0]);
    const aPlus = sProject(axisA), aMinus = sProject(stretch3(axisA, -1));
    const bPlus = sProject(stretch3(axisB, cos)), bMinus = sProject(stretch3(axisB, -sin));
    const corners = [aPlus, bPlus, aMinus, bMinus];
    const area = Math.abs(corners.reduce((sum, [x, y], index) => {
      const [nextX, nextY] = corners[(index + 1) % corners.length];
      return sum + x * nextY - nextX * y;
    }, 0)) / 2;
    parts.sQuad.setAttribute('points',
      corners.map(point => `${point[0].toFixed(1)},${point[1].toFixed(1)}`).join(' '));
    parts.sQuad.classList.toggle('is-empty', area < 24);
    setSegment(parts.sBAxis, sProject(stretch3(axisB, -1)), sProject(axisB));
    setSegment(parts.sALine, aMinus, aPlus);
    setSegment(parts.sBPlusLine, origin, bPlus);
    setSegment(parts.sBMinusLine, origin, bMinus);
    placeTip(parts.sAPlus, aPlus); placeTip(parts.sAMinus, aMinus);
    placeTip(parts.sBPlus, bPlus); placeTip(parts.sBMinus, bMinus);
    const gone = sin < 1e-3;
    [parts.sBMinusLine, parts.sBMinus, parts.sBMinusLabel]
      .forEach(element => element.classList.toggle('is-empty', gone));
    parts.sAPlusLabel.textContent = '|+a⟩';
    parts.sAMinusLabel.textContent = '|−a⟩';
    parts.sBPlusLabel.textContent = '|+b⟩';
    parts.sBMinusLabel.textContent = '|−b⟩';
    placeTipLabel(parts.sAPlusLabel, aPlus, -20);
    placeTipLabel(parts.sAMinusLabel, aMinus, -20);
    placeTipLabel(parts.sBPlusLabel, bPlus, 20);
    placeTipLabel(parts.sBMinusLabel, bMinus, 20);
    parts.sTheta.textContent = theta.toFixed(0) + '°';
    parts.sLambda0.textContent = (first * first).toFixed(3);
    parts.sLambda1.textContent = (second * second).toFixed(3);
    parts.sChi.textContent = gone ? '—' : chi.toFixed(0) + '°';
    parts.sFormula.textContent = gone
      ? `|ψ⟩ = ${first.toFixed(3)} |+a⟩|+b⟩`
      : `|ψ⟩ = ${first.toFixed(3)} |+a⟩|+b⟩ + e^{i${chi.toFixed(0)}°} ${second.toFixed(3)} |−a⟩|−b⟩`;
    parts.sDesc.textContent = `Schmidt form at θ = ${theta.toFixed(0)} degrees: qubit A's basis has unit`
      + ` length and qubit B's vectors have lengths ${cos.toFixed(3)} and ${sin.toFixed(3)}. A translucent`
      + ' parallelogram joins the four Schmidt endpoints.';
  }

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
    state.forEach((amplitude, index) => {
      const key = KEYS[index];
      const group = byId(`ph-group-${key}`);
      const line = byId(`ph-vec-${key}`);
      const text = byId(`ph-vec-${key}-label`);
      const magnitude = size(amplitude);
      const degrees = phaseOf(amplitude);
      const [x, y] = place(line, magnitude, degrees, [CENTER, CENTER], offsets[index]);
      const hit = group.querySelector('.ph-hit');
      if (hit) for (const name of ['x1', 'y1', 'x2', 'y2']) hit.setAttribute(name, line.getAttribute(name));
      text.textContent = LABELS[index];
      placeLabel(text, x, y, labelOffsets[index]);
      text.setAttribute('text-anchor', x < CENTER - 1 ? 'end' : 'start');
      group.classList.toggle('is-empty', magnitude < ZERO);
      group.setAttribute('tabindex', '0');
      group.setAttribute('role', 'button');
      group.setAttribute('aria-label', `${LABELS[index]}: magnitude ${magnitude.toFixed(3)},`
        + ` phase ${degrees.toFixed(0)} degrees. Use the left and right arrow keys to turn it,`
        + ' and up and down to resize it.');
    });
  }

  function drawNeedle(offset) {
    const [first, second] = products();
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

  function drawDials() {
    // One dial per basis state: the arrow's length is the magnitude and its angle the phase.
    state.forEach((amplitude, index) => {
      const key = KEYS[index];
      const magnitude = size(amplitude);
      const degrees = phaseOf(amplitude);
      const x = 32 + 22 * magnitude * Math.cos(degrees * D2R);
      const y = 32 - 22 * magnitude * Math.sin(degrees * D2R);
      const needle = byId(`amp-needle-${key}`);
      needle.setAttribute('x2', x.toFixed(1));
      needle.setAttribute('y2', y.toFixed(1));
      needle.classList.toggle('is-empty', magnitude < ZERO);
      const dot = byId(`amp-tip-${key}`);
      dot.setAttribute('cx', x.toFixed(1));
      dot.setAttribute('cy', y.toFixed(1));
      dot.classList.toggle('is-empty', magnitude < ZERO);
      byId(`amp-name-${key}`).textContent = LABELS[index];
      byId(`amp-mag-${key}`).textContent = magnitude.toFixed(3);
      byId(`amp-phase-${key}`).textContent = magnitude < ZERO ? '—' : degrees.toFixed(0) + '°';
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
    const total = weight();
    const normalised = Math.abs(total - 1) < 5e-4;
    const c = concurrence();

    // Arrows and the needle share one fan group, so a needle lying on an arrow steps aside too.
    const [firstProduct, secondProduct] = products();
    const needle = sub(firstProduct, secondProduct);
    const vectors = state.map(a => [size(a), phaseOf(a)]).concat([[size(needle), phaseOf(needle)]]);
    const offsets = fanOffsets(vectors, 5);
    drawArrows(offsets, fanOffsets(vectors, 16));
    drawNeedle(offsets[4]);
    drawDials();
    drawSchmidt();
    syncStateMenu();
    // The heat map is a legend for the needle's scale; its strength is the concurrence itself, so the disc
    // cools to plain paper as the state factorises and deepens towards the rim as it entangles.
    parts.heat.style.opacity = c.toFixed(3);

    parts.norm.textContent = normalised
      ? `Σ|c|² = ${total.toFixed(3)} — the arrows are normalized.`
      : `Σ|c|² = ${total.toFixed(3)} — unnormalized, so press Normalize.`;
    parts.norm.classList.toggle('is-unnormalized', !normalised);
    parts.normalize.disabled = total < ZERO;

    parts.desc.textContent = `${ketText()}. The arrows are the four computational-basis amplitudes; the`
      + ` concurrence needle has length ${c.toFixed(3)}, over a background that warms from concurrence 0 at`
      + ` the centre to 1 at the rim and`
      + ` is shown at ${Math.round(c * 100)}% of its strength.`
      + (normalised ? '' : ` The arrows keep the lengths you set, with total weight ${total.toFixed(3)};`
        + ' Normalize rescales all four so that weight returns to one.');
    if (announce) {
      parts.status.textContent = `${ketText()}. Concurrence ${c.toFixed(3)}, ${describeType(c).toLowerCase()}`
        + (normalised ? '.' : `, total weight ${total.toFixed(3)}.`);
    }
  }

  // A drag sets both numbers: the distance from the centre is the length and the bearing the phase.
  // The floor keeps every arrow long enough to grab again.
  const MIN_LENGTH = 0.02;
  const pointerAim = event => {
    const matrix = svg.getScreenCTM();
    if (!matrix) return null;
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const local = point.matrixTransform(matrix.inverse());
    const dx = local.x - CENTER, dy = CENTER - local.y;
    return {
      degrees: ((Math.atan2(dy, dx) * R2D) + 360) % 360,
      magnitude: Math.min(1, Math.max(MIN_LENGTH, Math.hypot(dx, dy) / RADIUS)),
    };
  };

  const reshape = (index, change) => {
    const magnitude = change.magnitude ?? size(state[index]);
    const degrees = change.degrees ?? phaseOf(state[index]);
    state[index] = [magnitude * Math.cos(degrees * D2R), magnitude * Math.sin(degrees * D2R)];
  };

  let dragging = null;
  document.querySelectorAll('.ph-vec').forEach(group => {
    const index = Number(group.dataset.index);
    group.addEventListener('pointerdown', event => {
      if (event.button !== 0) return;
      const aim = pointerAim(event);
      if (!aim) return;
      dragging = index;
      svg.classList.add('is-dragging');
      if (svg.setPointerCapture) svg.setPointerCapture(event.pointerId);
      reshape(index, aim);
      render(false);
      event.preventDefault();
    });
    group.addEventListener('keydown', event => {
      const current = phaseOf(state[index]);
      const magnitude = size(state[index]);
      const turn = event.shiftKey ? 15 : 5;
      const grow = event.shiftKey ? 0.2 : 0.05;
      if (event.key === 'ArrowRight') reshape(index, { degrees: current + turn });
      else if (event.key === 'ArrowLeft') reshape(index, { degrees: current - turn });
      else if (event.key === 'ArrowUp') reshape(index, { magnitude: Math.min(1, magnitude + grow) });
      else if (event.key === 'ArrowDown') reshape(index, { magnitude: Math.max(MIN_LENGTH, magnitude - grow) });
      else if (event.key === 'Home') reshape(index, { degrees: 0 });
      else return;
      event.preventDefault();
      render(true);
    });
  });
  svg.addEventListener('pointermove', event => {
    if (dragging === null) return;
    const aim = pointerAim(event);
    if (!aim) return;
    reshape(dragging, aim);
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

  // ---- normalization --------------------------------------------------------------------------
  parts.normalize.addEventListener('click', () => {
    if (weight() < ZERO) return;
    state = scaled();
    render(false);
    parts.status.textContent = `Normalized every arrow by one factor, so Σ|c|² = 1 and the concurrence`
      + ` is ${concurrence().toFixed(3)}.`;
  });

  // ---- measurement ----------------------------------------------------------------------------
  const tallyText = () => {
    const total = counts.reduce((sum, n) => sum + n, 0);
    if (!total) return 'No joint measurements yet.';
    return `${total} joint measurement${total === 1 ? '' : 's'}: `
      + KEYS.map((key, index) => `${key} × ${counts[index]}`).join(', ') + '.';
  };

  function measure(wire) {
    const total = weight() || 1;
    const probability = [0, 0];
    state.forEach((amplitude, index) => {
      probability[wire === 0 ? (index >> 1) & 1 : index & 1] += abs2(amplitude) / total;
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
    const total = weight() || 1;
    const probability = state.map(amplitude => abs2(amplitude) / total);
    const threshold = Math.random();
    let outcome = 0, running = probability[0];
    while (outcome < 3 && threshold > running) { outcome += 1; running += probability[outcome]; }
    const chance = probability[outcome];
    state = state.map((amplitude, index) => (index === outcome ? [1, 0] : [0, 0]));
    return { outcome, probability: chance };
  }

  function measureQubit(wire, name) {
    const { outcome, probability } = measure(wire);
    render(false);
    parts.result.textContent = `Measured qubit ${name}: outcome ${outcome}`
      + ` (probability ${probability.toFixed(3)}). The pair is now ${ketText()}.`;
    parts.tally.textContent = tallyText();
    parts.status.textContent = `Measured qubit ${name} as ${outcome}; the state is now ${ketText()}.`;
  }

  function measurePair() {
    const { outcome, probability } = measureBoth();
    counts[outcome] += 1;
    render(false);
    parts.result.textContent = `Measured both: outcome |${(outcome >> 1) & 1}⟩|${outcome & 1}⟩`
      + ` (probability ${probability.toFixed(3)}).`;
    parts.tally.textContent = tallyText();
    parts.status.textContent = `Measured both qubits; outcome ${KEYS[outcome]}.`;
  }

  function resetAll() {
    state = PRESETS['00'].map(c => [...c]);
    counts = [0, 0, 0, 0];
    render(false);
    parts.result.textContent = 'Measuring A projects onto |0⟩ or |1⟩ on that qubit. On a Bell state the two'
      + ' outcomes always agree.';
    parts.tally.textContent = tallyText();
    parts.status.textContent = 'Reset to the state |00⟩ with no measurements recorded.';
  }

  // ---- the five menus ------------------------------------------------------------------
  // Action menus apply at once and fall back to "Choose…", so a gate can be used twice. The state
  // menu instead names the preset the current state equals, or "Custom…" once a gate has moved it.
  function syncStateMenu() {
    const match = Object.keys(PRESETS).find(key => PRESETS[key].every((c, index) =>
      Math.abs(c[0] - state[index][0]) < 1e-9 && Math.abs(c[1] - state[index][1]) < 1e-9));
    parts.menuState.value = match || '';
  }

  parts.menuState.addEventListener('change', () => {
    const preset = PRESETS[parts.menuState.value];
    if (!preset) return;
    state = preset.map(c => [...c]);
    render(true);
  });

  const applyLocal = (wire, name) => {
    const matrix = GATES[name];
    if (!matrix) return;
    gateOn(matrix, wire);
    render(true);
  };
  parts.menuGateA.addEventListener('change', () => {
    const name = parts.menuGateA.value;
    parts.menuGateA.value = '';
    applyLocal(0, name);
  });
  parts.menuGateB.addEventListener('change', () => {
    const name = parts.menuGateB.value;
    parts.menuGateB.value = '';
    applyLocal(1, name);
  });
  parts.menuGateTwo.addEventListener('change', () => {
    const name = parts.menuGateTwo.value;
    parts.menuGateTwo.value = '';
    if (!name) return;
    applyTwoQubit(name);
    render(true);
  });

  parts.menuMeasure.addEventListener('change', () => {
    const choice = parts.menuMeasure.value;
    parts.menuMeasure.value = '';
    if (choice === 'measure-a') measureQubit(0, 'A');
    else if (choice === 'measure-b') measureQubit(1, 'B');
    else if (choice === 'measure-both') measurePair();
    else if (choice === 'two-reset') resetAll();
  });

  byId('show-products').addEventListener('change', () => render(false));

  render(false);
})();
