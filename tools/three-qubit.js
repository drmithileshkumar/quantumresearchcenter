/* Three-qubit explorer: eight amplitudes in one complex plane, plus the relative-state view.
   One qubit is the reference, so the state splits into two two-qubit branches; each branch has its
   own Schmidt bases, and those two bases span one plane inside the same Bloch sphere. */
(() => {
  'use strict';
  const svg = document.getElementById('ph3');
  if (!svg) return;
  const CENTER = 220, RADIUS = 156, ZERO = 5e-4;
  const R2D = 180 / Math.PI, D2R = Math.PI / 180;
  const KEYS = ['000', '001', '010', '011', '100', '101', '110', '111'];
  const LABELS = KEYS.map(key => '|' + key + '⟩');
  const QUBITS = ['A', 'B', 'C'];
  const SUBSCRIPTS = ['₀', '₁'];

  const byId = id => document.getElementById(id);
  const parts = {
    status: byId('state-status'), result: byId('measure-result'), tally: byId('measure-tally'),
    desc: byId('ph3-desc'),
    menuState: byId('menu-state3'), menuReference: byId('menu-reference'), menuPair: byId('menu-gate-pair'),
    menuMeasure: byId('menu-measure3'),
    gates: [byId('menu-gate-0'), byId('menu-gate-1'), byId('menu-gate-2')],
    norm: byId('state-norm'), normalize: byId('normalize-arrows'),
    expansion: byId('plane-expansion'),
    legend: [byId('plane-legend-0'), byId('plane-legend-1')],
    heads: [byId('plane-head-0'), byId('plane-head-1')],
    prob: [byId('branch-prob-0'), byId('branch-prob-1')],
    theta: [byId('branch-theta-0'), byId('branch-theta-1')],
    weights: [byId('branch-weights-0'), byId('branch-weights-1')],
    chi: [byId('branch-chi-0'), byId('branch-chi-1')],
    formula: [byId('branch-formula-0'), byId('branch-formula-1')],
    planesDesc: byId('plane-summary'),
  };
  const flatten = value => (Array.isArray(value) ? value.flatMap(flatten) : [value]);
  if (flatten(Object.values(parts)).some(element => !element)) return;

  const sphere = byId('planes');
  if (!sphere) return;
  const planes = [0, 1].map(bit => ({
    group: byId(`planes-branch-${bit}`), quad: byId(`planes-quad-${bit}`),
    pAxis: byId(`planes-p-axis-${bit}`), qPlus: byId(`planes-q-plus-${bit}`),
    qMinus: byId(`planes-q-minus-${bit}`), pPlusTip: byId(`planes-p-plus-tip-${bit}`),
    pMinusTip: byId(`planes-p-minus-tip-${bit}`), qPlusTip: byId(`planes-q-plus-tip-${bit}`),
    qMinusTip: byId(`planes-q-minus-tip-${bit}`), pPlusLabel: byId(`planes-p-plus-label-${bit}`),
    pMinusLabel: byId(`planes-p-minus-label-${bit}`), qPlusLabel: byId(`planes-q-plus-label-${bit}`),
    qMinusLabel: byId(`planes-q-minus-label-${bit}`),
  }));
  if (flatten(planes.map(part => Object.values(part))).some(element => !element)) return;

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
  const S8 = Math.sqrt(1 / 8), S3 = Math.sqrt(1 / 3);
  const PRESETS = {
    // Every reference qubit shows two planes that are clearly apart for this state.
    planes: [[-0.28393134960506705, 0.45168829364378027], [0.26625299315248008, 0.082071697093509213],
             [0.07089425323024845, 0.1938563742430385], [-0.13168687249243721, -0.26948978880487245],
             [-0.15907888253636024, 0.04783143732863885], [0.40033177289152511, 0.059187702119268173],
             [0.29722942580113965, -0.068721791063861934], [0.14988116610591448, -0.44527155402130247]],
    '000': [[1, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
    '+++': Array.from({ length: 8 }, () => [S8, 0]),
    ghz: [[SQ, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [SQ, 0]],
    w: [[0, 0], [S3, 0], [S3, 0], [0, 0], [S3, 0], [0, 0], [0, 0], [0, 0]],
  };

  let state = PRESETS.planes.map(c => [...c]);
  let reference = 0;
  let counts = Array.from({ length: 8 }, () => 0);

  // Index 4a + 2b + c: wire 0 is the most significant bit.
  const bitOf = (index, wire) => (index >> (2 - wire)) & 1;
  const withBit = (index, wire, value) => {
    const shift = 2 - wire;
    return (index & ~(1 << shift)) | ((value & 1) << shift);
  };

  const gateOn = (matrix, wire) => {
    const next = state.map(() => [0, 0]);
    for (let index = 0; index < 8; index++) {
      const row = bitOf(index, wire);
      for (let source = 0; source < 2; source++) {
        next[index] = add(next[index], mul(matrix[row][source], state[withBit(index, wire, source)]));
      }
    }
    state = next;
  };

  const applyPair = (name, first, second) => {
    const next = state.map(() => [0, 0]);
    state.forEach((amplitude, index) => {
      const bits = [0, 1, 2].map(wire => bitOf(index, wire));
      let factor = [1, 0];
      let target = index;
      if (name === 'cnot') {
        if (bits[first] === 1) target = withBit(index, second, bits[second] ^ 1);
      } else if (name === 'cz') {
        if (bits[first] === 1 && bits[second] === 1) factor = [-1, 0];
      } else if (name === 'swap') {
        target = withBit(withBit(index, first, bits[second]), second, bits[first]);
      }
      next[target] = add(next[target], mul(factor, amplitude));
    });
    state = next;
  };

  // ---- scale and the two reference branches -------------------------------------------------
  const weight = () => state.reduce((sum, c) => sum + abs2(c), 0);
  const scaled = () => {
    const total = weight();
    return total > ZERO ? state.map(c => scale(c, 1 / Math.sqrt(total))) : state.map(() => [0, 0]);
  };

  const branchAmplitudes = bit => {
    const others = [0, 1, 2].filter(wire => wire !== reference);
    const amplitudes = [];
    for (let row = 0; row < 2; row++) {
      for (let col = 0; col < 2; col++) {
        let index = withBit(0, reference, bit);
        index = withBit(index, others[0], row);
        index = withBit(index, others[1], col);
        amplitudes.push(state[index]);
      }
    }
    return amplitudes;
  };

  const branchForm = bit => {
    const amplitudes = branchAmplitudes(bit);
    const total = amplitudes.reduce((sum, c) => sum + abs2(c), 0);
    if (total < ZERO) return { weight: total, form: null };
    return { weight: total, form: schmidtForm(amplitudes.map(c => scale(c, 1 / Math.sqrt(total)))) };
  };

  // ---- Schmidt form of a two-qubit state (same model as the two-qubit page) -------------------
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

  function schmidtForm(source) {
    const [c00, c01, c10, c11] = source;
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
      const weightPlus = overlapPair(source, plusA, plusB);
      const weightMinus = overlapPair(source, minusA, minusB);
      if (size(weightPlus) > ZERO && size(weightMinus) > ZERO) {
        chi = phaseOf(divide(weightMinus, weightPlus));
      }
    }
    return { theta, axisA, axisB, chi, first, second };
  }

  // ---- the plane: eight arrows -----------------------------------------------------------------
  const tip = (magnitude, degrees) => [
    CENTER + RADIUS * magnitude * Math.cos(degrees * D2R),
    CENTER - RADIUS * magnitude * Math.sin(degrees * D2R),
  ];

  function place(line, magnitude, degrees, from, offset = 0) {
    const shift = [offset * Math.sin(degrees * D2R), offset * Math.cos(degrees * D2R)];
    const [x, y] = tip(magnitude, degrees);
    line.setAttribute('x1', (from[0] + shift[0]).toFixed(1));
    line.setAttribute('y1', (from[1] + shift[1]).toFixed(1));
    line.setAttribute('x2', (x + shift[0]).toFixed(1));
    line.setAttribute('y2', (y + shift[1]).toFixed(1));
    return [x + shift[0], y + shift[1]];
  }

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
    const radius = Math.hypot(x - CENTER, y - CENTER) || 1;
    const nx = (x - CENTER) / radius, ny = (y - CENTER) / radius;
    const ring = RADIUS + 20;
    text.setAttribute('x', (CENTER + ring * nx - lateral * ny).toFixed(1));
    text.setAttribute('y', (CENTER + ring * ny + lateral * nx).toFixed(1));
  }

  function drawArrows(offsets, labelOffsets) {
    state.forEach((amplitude, index) => {
      const key = KEYS[index];
      const group = byId(`ph3-group-${key}`);
      const line = byId(`ph3-vec-${key}`);
      const text = byId(`ph3-vec-${key}-label`);
      const magnitude = size(amplitude);
      const degrees = phaseOf(amplitude);
      const [x, y] = place(line, magnitude, degrees, [CENTER, CENTER], offsets[index]);
      const hit = group.querySelector('.ph3-hit');
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

  function drawDials() {
    state.forEach((amplitude, index) => {
      const key = KEYS[index];
      const magnitude = size(amplitude);
      const degrees = phaseOf(amplitude);
      const x = 32 + 22 * magnitude * Math.cos(degrees * D2R);
      const y = 32 - 22 * magnitude * Math.sin(degrees * D2R);
      const needle = byId(`amp3-needle-${key}`);
      needle.setAttribute('x2', x.toFixed(1));
      needle.setAttribute('y2', y.toFixed(1));
      needle.classList.toggle('is-empty', magnitude < ZERO);
      const dot = byId(`amp3-tip-${key}`);
      dot.setAttribute('cx', x.toFixed(1));
      dot.setAttribute('cy', y.toFixed(1));
      dot.classList.toggle('is-empty', magnitude < ZERO);
      byId(`amp3-name-${key}`).textContent = LABELS[index];
      byId(`amp3-mag-${key}`).textContent = magnitude.toFixed(3);
      byId(`amp3-phase-${key}`).textContent = magnitude < ZERO ? '—' : degrees.toFixed(0) + '°';
    });
  }

  // ---- the sphere: an orbit camera, one plane per branch ---------------------------------------
  const S_CENTER = 200, S_RADIUS = 148;
  const GRID_STEPS = 180;
  const HOME = { azimuth: Number(sphere.dataset.azimuth || 32), elevation: Number(sphere.dataset.elevation || 17) };
  let azimuth = HOME.azimuth, elevation = HOME.elevation;
  let sRight = [1, 0, 0], sUp = [0, 1, 0], sForward = [0, 0, -1];

  function camera() {
    const a = azimuth * D2R, e = elevation * D2R;
    sForward = [-Math.cos(e) * Math.sin(a), Math.cos(e) * Math.cos(a), -Math.sin(e)];
    const length = Math.hypot(sForward[1], -sForward[0]) || 1;
    sRight = [sForward[1] / length, -sForward[0] / length, 0];
    sUp = [sRight[1] * sForward[2] - sRight[2] * sForward[1],
           sRight[2] * sForward[0] - sRight[0] * sForward[2],
           sRight[0] * sForward[1] - sRight[1] * sForward[0]];
  }

  const sProject = v => [S_CENTER + S_RADIUS * (v[0] * sRight[0] + v[1] * sRight[1] + v[2] * sRight[2]),
                         S_CENTER - S_RADIUS * (v[0] * sUp[0] + v[1] * sUp[1] + v[2] * sUp[2])];
  const sFacing = v => v[0] * sForward[0] + v[1] * sForward[1] + v[2] * sForward[2] < 0;
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
  const placeTipLabel = (label, point, side) => {
    const dx = point[0] - S_CENTER, dy = point[1] - S_CENTER, distance = Math.hypot(dx, dy);
    if (distance < 1) { label.classList.add('is-empty'); return; }
    const ux = dx / distance, uy = dy / distance;
    label.setAttribute('x', (point[0] - ux * 18 - uy * side).toFixed(1));
    label.setAttribute('y', (point[1] - uy * 18 + ux * side).toFixed(1));
    label.setAttribute('text-anchor', 'middle');
  };

  // ---- drawing the sphere at the current camera ------------------------------------------------
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const sCross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const sNorm = a => Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]);
  const AXES = [[[1, 0, 0], '|+⟩'], [[-1, 0, 0], '|−⟩'], [[0, 1, 0], '|+i⟩'],
                [[0, -1, 0], '|−i⟩'], [[0, 0, 1], '|0⟩'], [[0, 0, -1], '|1⟩']];

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
      samples.push([sProject(point), sFacing(point)]);
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
      return {
        visible: run.visible,
        path: 'M' + points.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L'),
      };
    });
  }

  function drawGrid() {
    const grid = byId('planes-grid');
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

  function drawAxes() {
    const axes = byId('planes-axes');
    axes.replaceChildren();
    AXES.forEach(([vector, label]) => {
      const tip = sProject(vector);
      axes.appendChild(svgElement('line', {
        class: 'bloch-axis', x1: S_CENTER, y1: S_CENTER,
        x2: tip[0].toFixed(1), y2: tip[1].toFixed(1),
      }));
      const dx = tip[0] - S_CENTER, dy = tip[1] - S_CENTER;
      const distance = Math.hypot(dx, dy) || 1;
      axes.appendChild(svgElement('text', {
        class: 'bloch-axis-label', x: (S_CENTER + dx * 1.15).toFixed(1),
        y: (S_CENTER + dy * 1.15).toFixed(1), dy: '4',
        'text-anchor': dx / distance > 0.35 ? 'start' : dx / distance < -0.35 ? 'end' : 'middle',
      }, label));
    });
  }

  function drawPlanes() {
    const others = [0, 1, 2].filter(wire => wire !== reference);
    const names = others.map(wire => QUBITS[wire].toLowerCase());
    const branches = [branchForm(0), branchForm(1)];
    const origin = sProject([0, 0, 0]);
    branches.forEach(({ weight: branchWeight, form }, bit) => {
      const part = planes[bit];
      const theta = form ? form.theta : 0;
      const axisP = form ? form.axisA : [0, 0, 1];
      const axisQ = form ? form.axisB : [0, 0, 1];
      const cos = Math.cos(theta * D2R), sin = Math.sin(theta * D2R);
      const pPlus = sProject(axisP), pMinus = sProject(stretch3(axisP, -1));
      const qPlus = sProject(stretch3(axisQ, cos)), qMinus = sProject(stretch3(axisQ, -sin));
      part.quad.setAttribute('points',
        [pPlus, qPlus, pMinus, qMinus].map(point => `${point[0].toFixed(1)},${point[1].toFixed(1)}`).join(' '));
      // A plane needs two independent axes; with them collinear the four endpoints are one line.
      part.quad.classList.toggle('is-empty', !form || sNorm(sCross(axisP, axisQ)) < 1e-6);
      setSegment(part.pAxis, pMinus, pPlus);
      setSegment(part.qPlus, origin, qPlus);
      setSegment(part.qMinus, origin, qMinus);
      placeTip(part.pPlusTip, pPlus); placeTip(part.pMinusTip, pMinus);
      placeTip(part.qPlusTip, qPlus); placeTip(part.qMinusTip, qMinus);
      const sub = SUBSCRIPTS[bit];
      part.pPlusLabel.textContent = `|+${names[0]}⟩${sub}`;
      part.pMinusLabel.textContent = `|−${names[0]}⟩${sub}`;
      part.qPlusLabel.textContent = `|+${names[1]}⟩${sub}`;
      part.qMinusLabel.textContent = `|−${names[1]}⟩${sub}`;
      const pSide = bit === 0 ? -20 : 20, qSide = bit === 0 ? 20 : -20;
      placeTipLabel(part.pPlusLabel, pPlus, pSide);
      placeTipLabel(part.pMinusLabel, pMinus, pSide);
      placeTipLabel(part.qPlusLabel, qPlus, qSide);
      placeTipLabel(part.qMinusLabel, qMinus, qSide);
      part.qMinusLabel.classList.toggle('is-empty', sin < 1e-3 || branchWeight < ZERO);
      part.group.classList.toggle('is-empty', branchWeight < ZERO);
      part.group.style.opacity = (0.3 + 0.7 * branchWeight).toFixed(2);
    });
    return { branches, names };
  }

  let drawnAzimuth = null, drawnElevation = null;
  function renderSphere() {
    camera();
    if (azimuth !== drawnAzimuth || elevation !== drawnElevation) {
      drawGrid();
      drawAxes();
      drawnAzimuth = azimuth;
      drawnElevation = elevation;
    }
    return drawPlanes();
  }

  function drawReadouts(branches, names) {
    const letter = QUBITS[reference];
    [0, 1].forEach(bit => {
      const { weight: branchWeight, form } = branches[bit];
      parts.prob[bit].textContent = branchWeight.toFixed(3);
      const theta = form ? form.theta : 0;
      const cos = Math.cos(theta * D2R), sin = Math.sin(theta * D2R);
      parts.theta[bit].textContent = form ? theta.toFixed(0) + '°' : '—';
      parts.weights[bit].textContent = form
        ? `${(cos * cos).toFixed(3)} / ${(sin * sin).toFixed(3)}` : '—';
      parts.chi[bit].textContent = form && sin > 1e-3 ? form.chi.toFixed(0) + '°' : '—';
      const sub = SUBSCRIPTS[bit];
      parts.formula[bit].textContent = form
        ? `|φ${sub}⟩ = ${cos.toFixed(3)} |+${names[0]}⟩${sub}|+${names[1]}⟩${sub}`
          + ` + e^{i${form.chi.toFixed(0)}°} ${sin.toFixed(3)} |−${names[0]}⟩${sub}|−${names[1]}⟩${sub}`
        : `|φ${sub}⟩ = 0`;
    });
    const [first, second] = branches;
    parts.expansion.innerHTML = `|ψ⟩ = ${Math.sqrt(first.weight).toFixed(3)} |0⟩<sub>${letter}</sub>|φ₀⟩`
      + ` + ${Math.sqrt(second.weight).toFixed(3)} |1⟩<sub>${letter}</sub>|φ₁⟩`;
    [0, 1].forEach(bit => {
      parts.heads[bit].innerHTML = `|${bit}⟩<sub>${letter}</sub>`;
      parts.legend[bit].innerHTML = `|${bit}⟩<sub>${letter}</sub> branch`;
    });
    parts.planesDesc.textContent = `Reference qubit ${letter}: branch 0 has weight`
      + ` ${first.weight.toFixed(3)} and branch 1 has weight ${second.weight.toFixed(3)}.`
      + (first.form ? ' Branch 0 is drawn with Schmidt angle ' + first.form.theta.toFixed(0) + ' degrees.'
        : ' Branch 0 is empty.')
      + (second.form ? ' Branch 1 is drawn with Schmidt angle ' + second.form.theta.toFixed(0) + ' degrees.'
        : ' Branch 1 is empty.');
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

  function render(announce) {
    const total = weight();
    const normalised = Math.abs(total - 1) < 5e-4;
    const vectors = state.map(a => [size(a), phaseOf(a)]);
    const offsets = fanOffsets(vectors, 5);
    drawArrows(offsets, fanOffsets(vectors, 16));
    drawDials();
    const { branches, names } = renderSphere();
    drawReadouts(branches, names);
    syncStateMenu();
    parts.norm.textContent = normalised
      ? `Σ|c|² = ${total.toFixed(3)} — the arrows are normalized.`
      : `Σ|c|² = ${total.toFixed(3)} — unnormalized, so press Normalize.`;
    parts.norm.classList.toggle('is-unnormalized', !normalised);
    parts.normalize.disabled = total < ZERO;
    const letter = QUBITS[reference];
    parts.desc.textContent = `${ketText()}. Reference qubit ${letter}: branch 0 has weight`
      + ` ${branches[0].weight.toFixed(3)} and branch 1 has weight ${branches[1].weight.toFixed(3)}.`
      + (normalised ? '' : ` The arrows keep the lengths you set, with total weight ${total.toFixed(3)};`
        + ' Normalize rescales all eight so that weight returns to one.');
    if (announce) {
      parts.status.textContent = `${ketText()}. Reference ${letter}, branch weights`
        + ` ${branches[0].weight.toFixed(3)} and ${branches[1].weight.toFixed(3)}`
        + (normalised ? '.' : `, total weight ${total.toFixed(3)}.`);
    }
  }

  function syncStateMenu() {
    const match = Object.keys(PRESETS).find(key => PRESETS[key].every((c, index) =>
      Math.abs(c[0] - state[index][0]) < 1e-9 && Math.abs(c[1] - state[index][1]) < 1e-9));
    parts.menuState.value = match || '';
  }

  // ---- orbiting the sphere --------------------------------------------------------------------
  let orbit = null;
  const orbitTo = (nextAzimuth, nextElevation) => {
    azimuth = ((nextAzimuth % 360) + 360) % 360;
    elevation = Math.max(-85, Math.min(85, nextElevation));
    renderSphere();
  };
  sphere.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    orbit = { x: event.clientX, y: event.clientY };
    sphere.classList.add('is-orbiting');
    if (sphere.setPointerCapture) sphere.setPointerCapture(event.pointerId);
    event.preventDefault();
  });
  sphere.addEventListener('pointermove', event => {
    if (!orbit) return;
    orbitTo(azimuth - (event.clientX - orbit.x) * 0.4, elevation + (event.clientY - orbit.y) * 0.4);
    orbit = { x: event.clientX, y: event.clientY };
  });
  const stopOrbit = () => {
    orbit = null;
    sphere.classList.remove('is-orbiting');
  };
  sphere.addEventListener('pointerup', stopOrbit);
  sphere.addEventListener('pointercancel', stopOrbit);
  sphere.addEventListener('keydown', event => {
    const step = event.shiftKey ? 15 : 5;
    if (event.key === 'ArrowLeft') orbitTo(azimuth - step, elevation);
    else if (event.key === 'ArrowRight') orbitTo(azimuth + step, elevation);
    else if (event.key === 'ArrowUp') orbitTo(azimuth, elevation + step);
    else if (event.key === 'ArrowDown') orbitTo(azimuth, elevation - step);
    else return;
    event.preventDefault();
  });
  byId('reset-view').addEventListener('click', () => {
    orbitTo(HOME.azimuth, HOME.elevation);
    sphere.focus();
  });

  // ---- direct manipulation of one amplitude ---------------------------------------------------
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
  document.querySelectorAll('.ph3-vec').forEach(group => {
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
    const [first, second] = [branchForm(0), branchForm(1)];
    parts.status.textContent = 'Normalized every arrow by one factor, so Σ|c|² = 1. Reference'
      + ` ${QUBITS[reference]}, branch weights ${first.weight.toFixed(3)} and ${second.weight.toFixed(3)}.`;
  });

  // ---- measurement ----------------------------------------------------------------------------
  const tallyText = () => {
    const total = counts.reduce((sum, n) => sum + n, 0);
    if (!total) return 'No full measurements yet.';
    return `${total} full measurement${total === 1 ? '' : 's'}: `
      + KEYS.map((key, index) => `${key} × ${counts[index]}`).join(', ') + '.';
  };

  function measure(wire) {
    const total = weight() || 1;
    const probability = [0, 0];
    state.forEach((amplitude, index) => {
      probability[bitOf(index, wire)] += abs2(amplitude) / total;
    });
    const outcome = Math.random() < probability[1] ? 1 : 0;
    state = state.map((amplitude, index) => (bitOf(index, wire) === outcome ? amplitude : [0, 0]));
    const norm = Math.sqrt(state.reduce((sum, c) => sum + abs2(c), 0)) || 1;
    state = state.map(c => scale(c, 1 / norm));
    return { outcome, probability: probability[outcome] };
  }

  function measureAll() {
    const total = weight() || 1;
    const probability = state.map(amplitude => abs2(amplitude) / total);
    const threshold = Math.random();
    let outcome = 0, running = probability[0];
    while (outcome < 7 && threshold > running) { outcome += 1; running += probability[outcome]; }
    const chance = probability[outcome];
    state = state.map((amplitude, index) => (index === outcome ? [1, 0] : [0, 0]));
    counts[outcome] += 1;
    return { outcome, probability: chance };
  }

  const measureQubit = wire => {
    const { outcome, probability } = measure(wire);
    render(false);
    parts.result.textContent = `Measured qubit ${QUBITS[wire]}: outcome ${outcome}`
      + ` (probability ${probability.toFixed(3)}). The state is now ${ketText()}.`;
    parts.status.textContent = `Measured qubit ${QUBITS[wire]} as ${outcome}; the state is now ${ketText()}.`;
  };

  const measureEverything = () => {
    const { outcome, probability } = measureAll();
    render(false);
    parts.result.textContent = `Measured all three: outcome ${KEYS[outcome]}`
      + ` (probability ${probability.toFixed(3)}).`;
    parts.tally.textContent = tallyText();
    parts.status.textContent = `Measured all three qubits; outcome ${KEYS[outcome]}.`;
  };

  function resetAll() {
    state = PRESETS['000'].map(c => [...c]);
    counts = Array.from({ length: 8 }, () => 0);
    reference = 0;
    parts.menuReference.value = '0';
    render(false);
    parts.result.textContent = 'Measuring a qubit projects it onto |0⟩ or |1⟩. On GHZ the three outcomes'
      + ' always agree.';
    parts.tally.textContent = tallyText();
    parts.status.textContent = 'Reset to the state |000⟩ with no measurements recorded.';
  }

  // ---- menus ---------------------------------------------------------------------------------
  parts.menuState.addEventListener('change', () => {
    const preset = PRESETS[parts.menuState.value];
    if (!preset) return;
    state = preset.map(c => [...c]);
    render(true);
  });
  parts.menuReference.addEventListener('change', () => {
    reference = Number(parts.menuReference.value);
    render(true);
  });
  parts.gates.forEach((menu, wire) => {
    menu.addEventListener('change', () => {
      const name = menu.value;
      menu.value = '';
      const matrix = GATES[name];
      if (!matrix) return;
      gateOn(matrix, wire);
      render(true);
    });
  });
  parts.menuPair.addEventListener('change', () => {
    const choice = parts.menuPair.value;
    parts.menuPair.value = '';
    const [name, first, second] = choice.split('-');
    const wires = { a: 0, b: 1, c: 2 };
    if (name && wires[first] !== undefined && wires[second] !== undefined) {
      applyPair(name, wires[first], wires[second]);
      render(true);
    }
  });
  parts.menuMeasure.addEventListener('change', () => {
    const choice = parts.menuMeasure.value;
    parts.menuMeasure.value = '';
    if (choice === 'measure-0') measureQubit(0);
    else if (choice === 'measure-1') measureQubit(1);
    else if (choice === 'measure-2') measureQubit(2);
    else if (choice === 'measure-all') measureEverything();
    else if (choice === 'three-reset') resetAll();
  });

  render(false);
})();
