/* Single-qubit Bloch sphere: state vector, gates, and projective measurement, all local to the page. */
(() => {
  'use strict';
  const svg = document.getElementById('bloch');
  if (!svg) return;
  const CENTER = 200, RADIUS = 148, ZERO = 5e-4;
  // The camera basis is written into the markup by scripts/tools.py, so the static drawing and the
  // pointer mapping cannot drift apart.
  const basis = (svg.dataset.basis || '').split(',').map(Number);
  if (basis.length !== 6 || basis.some(value => !Number.isFinite(value))) return;
  const right = basis.slice(0, 3), up = basis.slice(3);
  const cross = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
  const forward = cross(up, right);   // points into the screen

  const byId = id => document.getElementById(id);
  const parts = {
    arrow: byId('bloch-arrow'), tip: byId('bloch-tip'), drop: byId('bloch-drop'),
    radial: byId('bloch-radial'), desc: byId('bloch-desc'),
    theta: byId('theta'), phi: byId('phi'), thetaValue: byId('theta-value'), phiValue: byId('phi-value'),
    ket: byId('state-ket'), alpha: byId('state-alpha'), beta: byId('state-beta'),
    p0: byId('prob-0'), p1: byId('prob-1'), bar0: byId('bar-0'), bar1: byId('bar-1'),
    status: byId('state-status'), measure: byId('measure'), reset: byId('reset'),
    result: byId('measure-result'), tally: byId('measure-tally'),
  };
  if (Object.values(parts).some(element => !element)) return;

  const SQRT1_2 = Math.SQRT1_2;
  const gates = {
    X: [[[0, 0], [1, 0]], [[1, 0], [0, 0]]],
    Y: [[[0, 0], [0, -1]], [[0, 1], [0, 0]]],
    Z: [[[1, 0], [0, 0]], [[0, 0], [-1, 0]]],
    H: [[[SQRT1_2, 0], [SQRT1_2, 0]], [[SQRT1_2, 0], [-SQRT1_2, 0]]],
    S: [[[1, 0], [0, 0]], [[0, 0], [0, 1]]],
    T: [[[1, 0], [0, 0]], [[0, 0], [SQRT1_2, SQRT1_2]]],
  };

  let alpha = [1, 0], beta = [0, 0];
  let counts = [0, 0];

  const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
  const mul = (a, b) => [a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]];
  const size = c => Math.hypot(c[0], c[1]);
  const abs2 = c => c[0]*c[0] + c[1]*c[1];

  function blochVector() {
    const p0 = abs2(alpha), p1 = abs2(beta);
    // α*β gives ⟨X⟩/2 and ⟨Y⟩/2 once the state is normalized.
    const product = [alpha[0]*beta[0] + alpha[1]*beta[1], alpha[0]*beta[1] - alpha[1]*beta[0]];
    return [2*product[0], 2*product[1], p0 - p1];
  }

  function angles() {
    const [x, y, z] = blochVector();
    const theta = Math.acos(Math.max(-1, Math.min(1, z))) * 180/Math.PI;
    const phi = (Math.atan2(y, x) * 180/Math.PI + 360) % 360;
    return [theta, phi];
  }

  function setAngles(thetaDeg, phiDeg) {
    // Quantize to the slider steps so the readouts, sliders and amplitudes always agree.
    const theta = Math.min(180, Math.max(0, Math.round(thetaDeg)));
    const phi = ((Math.round(phiDeg) % 360) + 360) % 360;
    const half = theta * Math.PI/360, turn = phi * Math.PI/180;
    alpha = [Math.cos(half), 0];
    beta = [Math.sin(half) * Math.cos(turn), Math.sin(half) * Math.sin(turn)];
  }

  const project = v => [CENTER + RADIUS*(v[0]*right[0] + v[1]*right[1] + v[2]*right[2]),
                        CENTER - RADIUS*(v[0]*up[0] + v[1]*up[1] + v[2]*up[2])];

  function moveLine(line, from, to) {
    const a = project(from), b = project(to);
    line.setAttribute('x1', a[0].toFixed(1));
    line.setAttribute('y1', a[1].toFixed(1));
    line.setAttribute('x2', b[0].toFixed(1));
    line.setAttribute('y2', b[1].toFixed(1));
  }

  const fixed = (value, digits = 3) => {
    const rounded = Math.abs(value) < ZERO ? 0 : value;
    return (rounded < 0 ? '−' : '') + Math.abs(rounded).toFixed(digits);
  };

  function complexText(c) {
    if (Math.abs(c[1]) < ZERO) return fixed(c[0]);
    if (Math.abs(c[0]) < ZERO) return fixed(c[1]) + 'i';
    return fixed(c[0]) + (c[1] < 0 ? ' − ' : ' + ') + fixed(Math.abs(c[1])) + 'i';
  }

  function ketText(a, b) {
    const terms = [];
    const term = (c, label) => {
      if (size(c) <= ZERO) return;
      // A negative real or negative pure-imaginary coefficient lets its sign sit between terms.
      const negative = (Math.abs(c[1]) < ZERO && c[0] < 0) || (Math.abs(c[0]) < ZERO && c[1] < 0);
      let coefficient = complexText(negative ? [-c[0], -c[1]] : c);
      if (coefficient.includes(' ')) coefficient = '(' + coefficient + ')';
      const exact = Math.abs(c[0] - 1) < 1e-9 && Math.abs(c[1]) < 1e-9;
      terms.push({ negative, coefficient, label, exact });
    };
    term(a, '|0⟩');
    term(b, '|1⟩');
    if (!terms.length) return '0';
    return terms.map((item, index) => {
      const sign = index === 0 ? (item.negative ? '−' : '') : (item.negative ? ' − ' : ' + ');
      // A lone basis state reads as |0⟩ or |1⟩; a global phase keeps its coefficient, as α and β show it.
      const coefficient = terms.length === 1 && item.exact ? '' : item.coefficient;
      return sign + coefficient + item.label;
    }).join('');
  }

  function render(announce) {
    const [theta, phi] = angles();
    const vector = blochVector();
    const tip = project(vector);
    moveLine(parts.arrow, [0, 0, 0], vector);
    moveLine(parts.drop, vector, [vector[0], vector[1], 0]);
    moveLine(parts.radial, [0, 0, 0], [vector[0], vector[1], 0]);
    parts.tip.setAttribute('cx', tip[0].toFixed(1));
    parts.tip.setAttribute('cy', tip[1].toFixed(1));

    parts.theta.value = String(Math.round(theta));
    parts.phi.value = String(Math.round(phi));
    parts.thetaValue.textContent = theta.toFixed(0) + '°';
    parts.phiValue.textContent = phi.toFixed(0) + '° (' + (phi/180).toFixed(2) + 'π)';

    const p0 = abs2(alpha), p1 = abs2(beta);
    parts.alpha.textContent = complexText(alpha);
    parts.beta.textContent = complexText(beta);
    parts.ket.textContent = ketText(alpha, beta);
    parts.p0.textContent = p0.toFixed(3);
    parts.p1.textContent = p1.toFixed(3);
    parts.bar0.style.width = (p0*100).toFixed(1) + '%';
    parts.bar1.style.width = (p1*100).toFixed(1) + '%';

    parts.desc.textContent = `The Bloch sphere with the state vector pointing at θ = ${theta.toFixed(0)}°, φ = ${phi.toFixed(0)}°. The probability of outcome 0 is ${p0.toFixed(3)} and of outcome 1 is ${p1.toFixed(3)}.`;
    if (announce) parts.status.textContent = `θ = ${theta.toFixed(0)}°, φ = ${phi.toFixed(0)}°. Probability of 0 is ${p0.toFixed(3)}, of 1 is ${p1.toFixed(3)}.`;
  }

  function anglesFromPointer(event) {
    const matrix = svg.getScreenCTM();
    if (!matrix) return null;
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const local = point.matrixTransform(matrix.inverse());
    let px = (local.x - CENTER) / RADIUS, py = (CENTER - local.y) / RADIUS;
    const length = Math.hypot(px, py);
    if (length > 1) { px /= length; py /= length; }
    // The visible hemisphere is the part of the sphere facing the camera.
    const depth = -Math.sqrt(Math.max(0, 1 - px*px - py*py));
    const x = px*right[0] + py*up[0] + depth*forward[0];
    const y = px*right[1] + py*up[1] + depth*forward[1];
    const z = px*right[2] + py*up[2] + depth*forward[2];
    return [Math.acos(Math.max(-1, Math.min(1, z))) * 180/Math.PI,
            (Math.atan2(y, x) * 180/Math.PI + 360) % 360];
  }

  let dragging = false;
  svg.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    const next = anglesFromPointer(event);
    if (!next) return;
    dragging = true;
    svg.classList.add('is-dragging');
    if (svg.setPointerCapture) svg.setPointerCapture(event.pointerId);
    setAngles(next[0], next[1]);
    render(false);
    event.preventDefault();
  });
  svg.addEventListener('pointermove', event => {
    if (!dragging) return;
    const next = anglesFromPointer(event);
    if (!next) return;
    setAngles(next[0], next[1]);
    render(false);
  });
  const stopDrag = () => {
    if (!dragging) return;
    dragging = false;
    svg.classList.remove('is-dragging');
    render(true);
  };
  svg.addEventListener('pointerup', stopDrag);
  svg.addEventListener('pointercancel', stopDrag);

  const fromSliders = () => {
    setAngles(Number(parts.theta.value), Number(parts.phi.value));
    render(false);
  };
  parts.theta.addEventListener('input', fromSliders);
  parts.phi.addEventListener('input', fromSliders);
  parts.theta.addEventListener('change', () => render(true));
  parts.phi.addEventListener('change', () => render(true));

  document.querySelectorAll('[data-preset]').forEach(button => {
    button.addEventListener('click', () => {
      setAngles(Number(button.dataset.theta), Number(button.dataset.phi));
      render(true);
    });
  });

  document.querySelectorAll('[data-gate]').forEach(button => {
    button.addEventListener('click', () => {
      const matrix = gates[button.dataset.gate];
      if (!matrix) return;
      const nextAlpha = add(mul(matrix[0][0], alpha), mul(matrix[0][1], beta));
      const nextBeta = add(mul(matrix[1][0], alpha), mul(matrix[1][1], beta));
      alpha = nextAlpha;
      beta = nextBeta;
      render(true);
    });
  });

  parts.measure.addEventListener('click', () => {
    const p1 = abs2(beta), p0 = abs2(alpha);
    const outcome = Math.random() < p1 ? 1 : 0;
    counts[outcome] += 1;
    setAngles(outcome ? 180 : 0, 0);
    render(false);
    parts.result.textContent = `Last measurement: |${outcome}⟩, which had probability ${(outcome ? p1 : p0).toFixed(3)}. The qubit is now in |${outcome}⟩.`;
    parts.tally.textContent = `${counts[0] + counts[1]} measurement${counts[0] + counts[1] === 1 ? '' : 's'}: ${counts[0]} zero${counts[0] === 1 ? '' : 's'}, ${counts[1]} one${counts[1] === 1 ? '' : 's'}.`;
    parts.status.textContent = `Measured ${outcome}. The state collapsed to |${outcome}⟩.`;
  });

  parts.reset.addEventListener('click', () => {
    counts = [0, 0];
    setAngles(0, 0);
    render(false);
    parts.result.textContent = 'A measurement in the computational basis returns 0 or 1 with probabilities |α|² and |β|², and leaves the qubit in the state it found.';
    parts.tally.textContent = 'No measurements yet.';
    parts.status.textContent = 'Reset to the state |0⟩ with no measurements recorded.';
  });

  render(false);
})();
