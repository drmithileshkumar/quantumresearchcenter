/* Interactive, MathJax-formatted visual simulation engines for all QRC courses. */
(() => {
  const NS = 'http://www.w3.org/2000/svg';

  function el(tag, attrs = {}, text = '') {
    const node = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) {
      node.setAttribute(k, String(v));
    }
    if (text) node.textContent = text;
    return node;
  }

  function h2(p) {
    if (p <= 0 || p >= 1) return 0;
    return -p * Math.log2(p) - (1 - p) * Math.log2(1 - p);
  }

  function typesetNode(node) {
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
      window.MathJax.typesetPromise([node]).catch(() => {});
    }
  }

  function renderHelstrom(left, right, readout, pVal, aVal) {
    const theta = pVal * Math.PI;
    const p = aVal;
    const cx = 148, cy = 148, r = 92;
    left.appendChild(el('text', { x: cx, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Bloch X–Z Plane & Helstrom Axis'));
    left.appendChild(el('circle', { cx, cy, r, class: 'qsim-ring' }));
    left.appendChild(el('line', { x1: cx - r - 12, y1: cy, x2: cx + r + 12, y2: cy, class: 'qsim-axis' }));
    left.appendChild(el('line', { x1: cx, y1: cy - r - 12, x2: cx, y2: cy + r + 12, class: 'qsim-axis' }));
    left.appendChild(el('text', { x: cx, y: cy - r - 16, 'text-anchor': 'middle', class: 'qsim-muted' }, '|0⟩'));
    left.appendChild(el('text', { x: cx + r + 18, y: cy + 4, 'text-anchor': 'start', class: 'qsim-muted' }, '|+⟩'));

    // State |psi_0> = |0> (upward along Z)
    left.appendChild(el('line', { x1: cx, y1: cy, x2: cx, y2: cy - r, class: 'qsim-vec-1' }));
    left.appendChild(el('circle', { cx, cy: cy - r, r: 5, class: 'qsim-dot-1' }));

    // State |psi_1> at angle theta from |0>
    const x1 = cx + r * Math.sin(theta);
    const y1 = cy - r * Math.cos(theta);
    left.appendChild(el('line', { x1: cx, y1: cy, x2: x1, y2: y1, class: 'qsim-vec-2' }));
    left.appendChild(el('circle', { cx: x1, cy: y1, r: 5, class: 'qsim-dot-2' }));

    // Helstrom difference Bloch vector D = p*r0 - (1-p)*r1
    const dx = -(1 - p) * Math.sin(theta);
    const dz = p - (1 - p) * Math.cos(theta);
    const normD = Math.sqrt(dx * dx + dz * dz);
    const hAngle = Math.atan2(dx, dz);
    const hx = cx + r * Math.sin(hAngle);
    const hy = cy - r * Math.cos(hAngle);
    left.appendChild(el('line', { x1: cx - r * Math.sin(hAngle), y1: cy + r * Math.cos(hAngle), x2: hx, y2: hy, class: 'qsim-helstrom-axis' }));
    left.appendChild(el('text', { x: hx + (hx >= cx ? 8 : -8), y: hy, 'text-anchor': hx >= cx ? 'start' : 'end', class: 'qsim-label' }, 'M*'));

    // Right panel: p_guess and Trace distance vs theta/pi
    const x0 = 340, y0 = 230, w = 266, h = 176;
    right.appendChild(el('text', { x: x0 + w / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Guessing Probability p_guess & Trace Distance T'));
    right.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: x0, y1: y0 - h, x2: x0, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('text', { x: x0 + w / 2, y: 256, 'text-anchor': 'middle', class: 'qsim-muted' }, 'State angle θ / π'));

    let dGuess = '', dTrace = '';
    for (let i = 0; i <= 50; i++) {
      const u = i / 50;
      const th = u * Math.PI;
      const tDist = Math.sin(th / 2);
      const hel = 0.5 * (1 + Math.sqrt(1 - 4 * p * (1 - p) * Math.cos(th / 2) ** 2));
      const px = x0 + u * w;
      const pyG = y0 - hel * h;
      const pyT = y0 - tDist * h;
      dGuess += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + pyG.toFixed(1) + ' ';
      dTrace += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + pyT.toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dTrace, class: 'qsim-curve-2' }));
    right.appendChild(el('path', { d: dGuess, class: 'qsim-curve-1' }));

    const T = Math.sin(theta / 2);
    const F = Math.cos(theta / 2) ** 2;
    const pGuess = 0.5 * (1 + normD);
    const curX = x0 + pVal * w;
    right.appendChild(el('circle', { cx: curX, cy: y0 - pGuess * h, r: 5, class: 'qsim-dot-1' }));
    right.appendChild(el('circle', { cx: curX, cy: y0 - T * h, r: 5, class: 'qsim-dot-2' }));

    readout.innerHTML = `For \\(\\theta = ${pVal.toFixed(2)}\\pi\\) and prior \\(p = ${p.toFixed(2)}\\): trace distance \\(T(\\rho,\\sigma) = ${T.toFixed(3)}\\), squared fidelity \\(F(\\rho,\\sigma) = ${F.toFixed(3)}\\), and optimal Helstrom success probability \\(p_{\\mathrm{guess}} = ${pGuess.toFixed(4)}\\).`;
    typesetNode(readout);
  }

  function renderChannel(left, right, readout, gamma, thFrac) {
    const cx = 148, cy = 148, r = 90;
    left.appendChild(el('text', { x: cx, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Bloch Ball Contraction under Noise γ'));
    left.appendChild(el('circle', { cx, cy, r, class: 'qsim-ring' }));
    left.appendChild(el('line', { x1: cx - r - 10, y1: cy, x2: cx + r + 10, y2: cy, class: 'qsim-axis' }));
    left.appendChild(el('line', { x1: cx, y1: cy - r - 10, x2: cx, y2: cy + r + 10, class: 'qsim-axis' }));

    // Contracted amplitude-damping / dephasing ellipse
    const rx = r * Math.sqrt(Math.max(0, 1 - gamma));
    const rz = r * (1 - gamma);
    const shiftY = cy - r * gamma;
    left.appendChild(el('ellipse', { cx, cy: shiftY, rx: Math.max(2, rx), ry: Math.max(2, rz), class: 'qsim-contracted' }));

    const th = thFrac * Math.PI;
    const inX = Math.sin(th), inZ = Math.cos(th);
    const outX = Math.sqrt(1 - gamma) * inX;
    const outZ = (1 - gamma) * inZ + gamma;
    left.appendChild(el('line', { x1: cx, y1: cy, x2: cx + r * inX, y2: cy - r * inZ, class: 'qsim-vec-2' }));
    left.appendChild(el('line', { x1: cx, y1: cy, x2: cx + r * outX, y2: cy - r * outZ, class: 'qsim-vec-1' }));
    left.appendChild(el('circle', { cx: cx + r * outX, cy: cy - r * outZ, r: 5, class: 'qsim-dot-1' }));

    // Right panel: Purity Tr(rho^2) and Coherence |rho_01| vs gamma
    const x0 = 340, y0 = 230, w = 266, h = 176;
    right.appendChild(el('text', { x: x0 + w / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Output Purity Tr(ρ′²) & Coherence |ρ′₀₁|'));
    right.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: x0, y1: y0 - h, x2: x0, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('text', { x: x0 + w / 2, y: 256, 'text-anchor': 'middle', class: 'qsim-muted' }, 'Noise parameter γ'));

    let dPur = '', dCoh = '';
    for (let i = 0; i <= 50; i++) {
      const g = i / 50;
      const ox = Math.sqrt(1 - g) * inX;
      const oz = (1 - g) * inZ + g;
      const pur = 0.5 * (1 + ox * ox + oz * oz);
      const coh = 0.5 * Math.abs(ox);
      const px = x0 + g * w;
      dPur += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + (y0 - pur * h).toFixed(1) + ' ';
      dCoh += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + (y0 - coh * 2 * h).toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dPur, class: 'qsim-curve-1' }));
    right.appendChild(el('path', { d: dCoh, class: 'qsim-curve-2' }));

    const purity = 0.5 * (1 + outX * outX + outZ * outZ);
    const rLen = Math.sqrt(outX * outX + outZ * outZ);
    const eigPlus = 0.5 * (1 + rLen);
    const S = h2(Math.min(0.9999, Math.max(0.0001, eigPlus)));
    right.appendChild(el('circle', { cx: x0 + gamma * w, cy: y0 - purity * h, r: 5, class: 'qsim-dot-1' }));

    readout.innerHTML = `At damping \\(\\gamma = ${gamma.toFixed(2)}\\) and input \\(\\theta = ${thFrac.toFixed(2)}\\pi\\): Bloch radius \\(\\|\\mathbf{r}^\\prime\\| = ${rLen.toFixed(3)}\\), output purity \\(\\mathrm{Tr}(\\rho^{\\prime 2}) = ${purity.toFixed(3)}\\), and output entropy \\(S(\\mathcal{E}(\\rho)) = ${S.toFixed(3)}\\text{ bits}\\).`;
    typesetNode(readout);
  }

  function renderEntropy(left, right, readout, p, q) {
    // Left panel: Bar chart of S(rho), Holevo chi, Coherent info I_c
    const xL = 42, yL = 228, wL = 216, hL = 170;
    left.appendChild(el('text', { x: xL + wL / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Information Quantities (bits)'));
    left.appendChild(el('line', { x1: xL, y1: yL, x2: xL + wL, y2: yL, class: 'qsim-axis' }));
    left.appendChild(el('line', { x1: xL, y1: yL - hL, x2: xL, y2: yL, class: 'qsim-axis' }));

    const sOut = h2(q * (1 - p) + (1 - q) * p);
    const sCond = h2(p);
    const chi = Math.max(0, sOut - sCond);
    const ic = Math.max(0, 1 - 2 * h2(Math.min(0.5, p)));

    const bars = [
      { label: 'S(ρ̄)', val: sOut, cls: 'qsim-bar-1' },
      { label: 'S(N(ρ))', val: sCond, cls: 'qsim-bar-muted' },
      { label: 'Holevo χ', val: chi, cls: 'qsim-bar-2' },
      { label: 'Coherent I_c', val: ic, cls: 'qsim-bar-1' },
    ];
    bars.forEach((b, idx) => {
      const bx = xL + 16 + idx * 50;
      const bh = Math.max(2, b.val * hL);
      left.appendChild(el('rect', { x: bx, y: yL - bh, width: 32, height: bh, rx: 3, class: b.cls }));
      left.appendChild(el('text', { x: bx + 16, y: yL + 18, 'text-anchor': 'middle', class: 'qsim-muted' }, b.label));
      left.appendChild(el('text', { x: bx + 16, y: yL - bh - 6, 'text-anchor': 'middle', class: 'qsim-label' }, b.val.toFixed(2)));
    });

    // Right panel: Binary entropy h2(p) and Holevo chi(p) curves
    const x0 = 340, y0 = 228, w = 266, h = 170;
    right.appendChild(el('text', { x: x0 + w / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Entropy h₂(p) & Accessible Rate χ(p)'));
    right.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: x0, y1: y0 - h, x2: x0, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('text', { x: x0 + w / 2, y: 256, 'text-anchor': 'middle', class: 'qsim-muted' }, 'Channel noise parameter p'));

    let dH = '', dChi = '';
    for (let i = 1; i < 50; i++) {
      const u = i / 50;
      const hu = h2(u);
      const chiu = Math.max(0, h2(q * (1 - u) + (1 - q) * u) - hu);
      const px = x0 + u * w;
      dH += (i === 1 ? 'M' : 'L') + px.toFixed(1) + ',' + (y0 - hu * h).toFixed(1) + ' ';
      dChi += (i === 1 ? 'M' : 'L') + px.toFixed(1) + ',' + (y0 - chiu * h).toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dH, class: 'qsim-curve-2' }));
    right.appendChild(el('path', { d: dChi, class: 'qsim-curve-1' }));
    right.appendChild(el('circle', { cx: x0 + p * w, cy: y0 - chi * h, r: 5, class: 'qsim-dot-1' }));
    right.appendChild(el('circle', { cx: x0 + p * w, cy: y0 - sCond * h, r: 5, class: 'qsim-dot-2' }));

    readout.innerHTML = `With noise \\(p = ${p.toFixed(2)}\\) and prior weight \\(q = ${q.toFixed(2)}\\): ensemble entropy \\(S(\\bar{\\rho}) = ${sOut.toFixed(3)}\\text{ bits}\\), conditional noise entropy \\(H_2(p) = ${sCond.toFixed(3)}\\text{ bits}\\), and Holevo quantity \\(\\chi = ${chi.toFixed(3)}\\text{ bits/use}\\).`;
    typesetNode(readout);
  }

  function renderMajorization(left, right, readout, lamPsi, lamPhi) {
    // Left panel: Lorenz curves for Schmidt vectors (lamPsi, 1-lamPsi) vs (lamPhi, 1-lamPhi)
    const x0 = 44, y0 = 228, w = 216, h = 170;
    left.appendChild(el('text', { x: x0 + w / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Majorization Lorenz Curves'));
    left.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0, class: 'qsim-axis' }));
    left.appendChild(el('line', { x1: x0, y1: y0 - h, x2: x0, y2: y0, class: 'qsim-axis' }));
    left.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0 - h, class: 'qsim-helstrom-axis' }));

    const dPsi = `M${x0},${y0} L${x0 + w / 2},${y0 - lamPsi * h} L${x0 + w},${y0 - h}`;
    const dPhi = `M${x0},${y0} L${x0 + w / 2},${y0 - lamPhi * h} L${x0 + w},${y0 - h}`;
    left.appendChild(el('path', { d: dPhi, class: 'qsim-curve-2' }));
    left.appendChild(el('path', { d: dPsi, class: 'qsim-curve-1' }));
    left.appendChild(el('circle', { cx: x0 + w / 2, cy: y0 - lamPsi * h, r: 5, class: 'qsim-dot-1' }));
    left.appendChild(el('circle', { cx: x0 + w / 2, cy: y0 - lamPhi * h, r: 5, class: 'qsim-dot-2' }));
    left.appendChild(el('text', { x: x0 + w / 2, y: y0 + 20, 'text-anchor': 'middle', class: 'qsim-muted' }, 'k = 1 Schmidt sum'));

    // Right panel: Entanglement entropy E(|psi>) = h2(lambda_1) & Vidal max conversion probability
    const rx0 = 340, ry0 = 228, rw = 266, rh = 170;
    right.appendChild(el('text', { x: rx0 + rw / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Entanglement E(|ψ⟩) & Optimal LOCC Probability'));
    right.appendChild(el('line', { x1: rx0, y1: ry0, x2: rx0 + rw, y2: ry0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: rx0, y1: ry0 - rh, x2: rx0, y2: ry0, class: 'qsim-axis' }));

    let dEnt = '';
    for (let i = 0; i <= 48; i++) {
      const l = 0.5 + (i / 48) * 0.49;
      const px = rx0 + ((l - 0.5) / 0.5) * rw;
      const py = ry0 - h2(l) * rh;
      dEnt += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + py.toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dEnt, class: 'qsim-curve-1' }));
    const ePsi = h2(lamPsi), ePhi = h2(lamPhi);
    const pSucc = Math.min(1, (1 - lamPsi) / Math.max(0.001, 1 - lamPhi));
    right.appendChild(el('circle', { cx: rx0 + ((lamPsi - 0.5) / 0.5) * rw, cy: ry0 - ePsi * rh, r: 5, class: 'qsim-dot-1' }));
    right.appendChild(el('circle', { cx: rx0 + ((lamPhi - 0.5) / 0.5) * rw, cy: ry0 - ePhi * rh, r: 5, class: 'qsim-dot-2' }));

    const det = lamPsi <= lamPhi + 1e-9;
    readout.innerHTML = `Schmidt spectra \\(\\lambda(\\psi) = (${lamPsi.toFixed(2)}, ${(1 - lamPsi).toFixed(2)})\\) vs. \\(\\lambda(\\phi) = (${lamPhi.toFixed(2)}, ${(1 - lamPhi).toFixed(2)})\\): \\(E(|\\psi\\rangle) = ${ePsi.toFixed(3)}\\text{ ebits}\\), \\(E(|\\phi\\rangle) = ${ePhi.toFixed(3)}\\text{ ebits}\\). Deterministic single-copy LOCC is <strong>${det ? 'possible (\\(\\lambda(\\psi) \\prec \\lambda(\\phi)\\))' : 'impossible'}</strong>; maximum stochastic LOCC success is \\(P_{\\max} = ${pSucc.toFixed(3)}\\).`;
    typesetNode(readout);
  }

  function renderStabilizer(left, right, readout, p, faultIdx) {
    const q = Math.round(faultIdx);
    left.appendChild(el('text', { x: 152, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, '[[7,1,3]] Steane Plaquette Syndromes'));
    // 3 overlapping syndrome plaquettes S1={1,3,5,7}, S2={2,3,6,7}, S3={4,5,6,7}
    const s1 = [1, 3, 5, 7].includes(q);
    const s2 = [2, 3, 6, 7].includes(q);
    const s3 = [4, 5, 6, 7].includes(q);

    left.appendChild(el('circle', { cx: 122, cy: 118, r: 52, class: s1 ? 'qsim-plaq-active' : 'qsim-plaq' }));
    left.appendChild(el('circle', { cx: 182, cy: 118, r: 52, class: s2 ? 'qsim-plaq-active' : 'qsim-plaq' }));
    left.appendChild(el('circle', { cx: 152, cy: 170, r: 52, class: s3 ? 'qsim-plaq-active' : 'qsim-plaq' }));

    const coords = {
      1: [88, 96], 2: [216, 96], 3: [152, 92],
      4: [152, 208], 5: [112, 158], 6: [192, 158], 7: [152, 134],
    };
    for (let i = 1; i <= 7; i++) {
      const [qx, qy] = coords[i];
      const active = i === q;
      left.appendChild(el('circle', { cx: qx, cy: qy, r: 13, class: active ? 'qsim-dot-2' : 'qsim-node' }));
      left.appendChild(el('text', { x: qx, y: qy + 4, 'text-anchor': 'middle', class: active ? 'qsim-node-inv' : 'qsim-label' }, 'q' + i));
    }
    const synStr = `${s3 ? 1 : 0}${s2 ? 1 : 0}${s1 ? 1 : 0}`;
    left.appendChild(el('text', { x: 152, y: 248, 'text-anchor': 'middle', class: 'qsim-label' }, `Syndrome (s₃s₂s₁) = ${synStr}₂ → identifies q${q}`));

    // Right panel: Logical failure rate p_L(p) vs unencoded p
    const x0 = 340, y0 = 228, w = 266, h = 170;
    right.appendChild(el('text', { x: x0 + w / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Logical Error Rate p_L(p) vs. Physical p'));
    right.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: x0, y1: y0 - h, x2: x0, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0 - h, class: 'qsim-helstrom-axis' }));

    let dSteane = '';
    for (let i = 0; i <= 50; i++) {
      const u = (i / 50) * 0.30;
      const pL = 1 - Math.pow(1 - u, 7) - 7 * u * Math.pow(1 - u, 6);
      const px = x0 + (u / 0.30) * w;
      const py = y0 - Math.min(1, pL / 0.30) * h;
      dSteane += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + py.toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dSteane, class: 'qsim-curve-1' }));
    const curPL = 1 - Math.pow(1 - p, 7) - 7 * p * Math.pow(1 - p, 6);
    right.appendChild(el('circle', { cx: x0 + (p / 0.30) * w, cy: y0 - Math.min(1, curPL / 0.30) * h, r: 5, class: 'qsim-dot-1' }));

    readout.innerHTML = `Fault on qubit \\(q_${q}\\) triggers binary syndrome \\((s_3 s_2 s_1) = ${synStr}_2 = ${q}\\). At physical error probability \\(p = ${p.toFixed(2)}\\), the distance-3 code achieves logical failure probability \\(p_L(p) = 1 - (1-p)^7 - 7p(1-p)^6 = ${curPL.toFixed(4)}\\).`;
    typesetNode(readout);
  }

  function renderSurface(left, right, readout, p, dVal) {
    const d = Math.round(dVal);
    left.appendChild(el('text', { x: 152, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, `Planar Surface Code Lattice (d = ${d})`));
    const size = Math.min(5, d);
    const step = 150 / size;
    const gx0 = 76, gy0 = 62;
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        const x = gx0 + c * step, y = gy0 + r * step;
        if (c + 1 < size) left.appendChild(el('line', { x1: x, y1: y, x2: x + step, y2: y, class: 'qsim-axis' }));
        if (r + 1 < size) left.appendChild(el('line', { x1: x, y1: y, x2: x, y2: y + step, class: 'qsim-axis' }));
        const isDefect = (r === 1 && c === 0) || (r === 1 && c === size - 1);
        left.appendChild(el('circle', { cx: x, cy: y, r: isDefect ? 7 : 4, class: isDefect ? 'qsim-dot-2' : 'qsim-dot-1' }));
      }
    }
    left.appendChild(el('line', { x1: gx0, y1: gy0 + step, x2: gx0 + (size - 1) * step, y2: gy0 + step, class: 'qsim-vec-2' }));
    left.appendChild(el('text', { x: 152, y: 248, 'text-anchor': 'middle', class: 'qsim-muted' }, `Corrects up to t = ⌊(d−1)/2⌋ = ${(d - 1) / 2} errors`));

    // Right panel: Threshold scaling p_L vs p/p_th
    const x0 = 340, y0 = 228, w = 266, h = 170;
    right.appendChild(el('text', { x: x0 + w / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Sub-Threshold Suppression across d'));
    right.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: x0, y1: y0 - h, x2: x0, y2: y0, class: 'qsim-axis' }));
    const pth = 0.01;
    const thX = x0 + (pth / 0.02) * w;
    right.appendChild(el('line', { x1: thX, y1: y0 - h, x2: thX, y2: y0, class: 'qsim-helstrom-axis' }));
    right.appendChild(el('text', { x: thX, y: y0 - h - 6, 'text-anchor': 'middle', class: 'qsim-muted' }, 'p_th = 1%'));

    let dCurve = '';
    for (let i = 1; i <= 50; i++) {
      const u = (i / 50) * 0.02;
      const pL = Math.min(1, 0.1 * Math.pow(u / pth, (d + 1) / 2));
      const px = x0 + (u / 0.02) * w;
      const py = y0 - Math.min(1, pL / 0.35) * h;
      dCurve += (i === 1 ? 'M' : 'L') + px.toFixed(1) + ',' + py.toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dCurve, class: 'qsim-curve-1' }));
    const curPL = Math.min(1, 0.1 * Math.pow(p / pth, (d + 1) / 2));
    right.appendChild(el('circle', { cx: x0 + (p / 0.02) * w, cy: y0 - Math.min(1, curPL / 0.35) * h, r: 5, class: 'qsim-dot-1' }));

    readout.innerHTML = `For code distance \\(d = ${d}\\) (correcting \\(t = ${(d - 1) / 2}\\) faults) at physical error rate \\(p = ${(100 * p).toFixed(2)}\\%\\) vs. threshold \\(p_{\\mathrm{th}} = 1.00\\%\\): scaling law \\(p_L \\approx 0.1(p/p_{\\mathrm{th}})^{(d+1)/2} = ${curPL.toExponential(2)}\\).`;
    typesetNode(readout);
  }

  function renderGpt(left, right, readout, thFrac, gammaT) {
    const cx = 148, cy = 148, r = 86;
    left.appendChild(el('text', { x: cx, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Simplex vs. Bloch Ball vs. Boxworld'));
    // Outer square (Boxworld), middle circle (Quantum Bloch), inner diamond (Classical Simplex)
    left.appendChild(el('rect', { x: cx - r, y: cy - r, width: 2 * r, height: 2 * r, class: 'qsim-plaq' }));
    left.appendChild(el('circle', { cx, cy, r, class: 'qsim-ring' }));
    left.appendChild(el('polygon', { points: `${cx},${cy - r} ${cx + r},${cy} ${cx},${cy + r} ${cx - r},${cy}`, class: 'qsim-contracted' }));

    const vis = Math.exp(-gammaT);
    const th = thFrac * Math.PI;
    const vx = cx + r * vis * Math.sin(th);
    const vy = cy - r * Math.cos(th);
    left.appendChild(el('line', { x1: cx, y1: cy, x2: vx, y2: vy, class: 'qsim-vec-1' }));
    left.appendChild(el('circle', { cx: vx, cy: vy, r: 5, class: 'qsim-dot-1' }));

    // Right panel: Interference fringe with decoherence damping
    const x0 = 340, y0 = 228, w = 266, h = 170;
    right.appendChild(el('text', { x: x0 + w / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Outcome Probability P+(θ) & Visibility V'));
    right.appendChild(el('line', { x1: x0, y1: y0, x2: x0 + w, y2: y0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: x0, y1: y0 - h, x2: x0, y2: y0, class: 'qsim-axis' }));

    let dFringe = '', dPure = '';
    for (let i = 0; i <= 50; i++) {
      const u = i / 50;
      const pPlus = 0.5 * (1 + vis * Math.cos(u * Math.PI));
      const pIdeal = 0.5 * (1 + Math.cos(u * Math.PI));
      const px = x0 + u * w;
      dFringe += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + (y0 - pPlus * h).toFixed(1) + ' ';
      dPure += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + (y0 - pIdeal * h).toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dPure, class: 'qsim-curve-2' }));
    right.appendChild(el('path', { d: dFringe, class: 'qsim-curve-1' }));
    const curP = 0.5 * (1 + vis * Math.cos(th));
    right.appendChild(el('circle', { cx: x0 + thFrac * w, cy: y0 - curP * h, r: 5, class: 'qsim-dot-1' }));

    readout.innerHTML = `At analyzer angle \\(\\theta = ${thFrac.toFixed(2)}\\pi\\) and environmental decoherence \\(\\Gamma t = ${gammaT.toFixed(2)}\\): off-diagonal coherence visibility \\(\\mathcal{V} = e^{-\\Gamma t} = ${vis.toFixed(3)}\\) and Born probability \\(P_+(\\theta) = \\frac{1}{2}(1 + \\mathcal{V}\\cos\\theta) = ${curP.toFixed(3)}\\).`;
    typesetNode(readout);
  }

  function renderHardware(left, right, readout, areaPi, detRatio) {
    // Left panel: Anharmonic 3-level ladder |0>, |1>, |2> and population bars
    left.appendChild(el('text', { x: 152, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Anharmonic Qubit Ladder & Populations'));
    const y0 = 212, y1 = 136, y2 = 72;
    left.appendChild(el('line', { x1: 48, y1: y0, x2: 148, y2: y0, class: 'qsim-vec-1' }));
    left.appendChild(el('line', { x1: 48, y1: y1, x2: 148, y2: y1, class: 'qsim-vec-1' }));
    left.appendChild(el('line', { x1: 48, y1: y2, x2: 148, y2: y2, class: 'qsim-helstrom-axis' }));
    left.appendChild(el('text', { x: 40, y: y0 + 4, 'text-anchor': 'end', class: 'qsim-label' }, '|0⟩'));
    left.appendChild(el('text', { x: 40, y: y1 + 4, 'text-anchor': 'end', class: 'qsim-label' }, '|1⟩'));
    left.appendChild(el('text', { x: 40, y: y2 + 4, 'text-anchor': 'end', class: 'qsim-muted' }, '|2⟩'));

    const eff = Math.sqrt(1 + detRatio * detRatio);
    const p1 = (1 / (1 + detRatio * detRatio)) * Math.pow(Math.sin(0.5 * areaPi * Math.PI * eff), 2);
    const p0 = 1 - p1;
    left.appendChild(el('rect', { x: 176, y: y0 - p0 * 120, width: 34, height: Math.max(2, p0 * 120), rx: 3, class: 'qsim-bar-muted' }));
    left.appendChild(el('rect', { x: 222, y: y0 - p1 * 120, width: 34, height: Math.max(2, p1 * 120), rx: 3, class: 'qsim-bar-1' }));
    left.appendChild(el('text', { x: 193, y: y0 + 18, 'text-anchor': 'middle', class: 'qsim-muted' }, 'P₀'));
    left.appendChild(el('text', { x: 239, y: y0 + 18, 'text-anchor': 'middle', class: 'qsim-muted' }, 'P₁'));

    // Right panel: Driven Rabi oscillation P_1(t)
    const rx0 = 340, ry0 = 228, rw = 266, rh = 170;
    right.appendChild(el('text', { x: rx0 + rw / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Driven Excited-State Population P₁(t)'));
    right.appendChild(el('line', { x1: rx0, y1: ry0, x2: rx0 + rw, y2: ry0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: rx0, y1: ry0 - rh, x2: rx0, y2: ry0, class: 'qsim-axis' }));

    let dRabi = '';
    for (let i = 0; i <= 60; i++) {
      const a = (i / 60) * 2.0;
      const pop = (1 / (1 + detRatio * detRatio)) * Math.pow(Math.sin(0.5 * a * Math.PI * eff), 2);
      const px = rx0 + (a / 2.0) * rw;
      const py = ry0 - pop * rh;
      dRabi += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + py.toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dRabi, class: 'qsim-curve-1' }));
    right.appendChild(el('circle', { cx: rx0 + (areaPi / 2.0) * rw, cy: ry0 - p1 * rh, r: 5, class: 'qsim-dot-1' }));

    readout.innerHTML = `At pulse area \\(\\Omega t_g = ${areaPi.toFixed(2)}\\pi\\) and detuning ratio \\(\\Delta/\\Omega = ${detRatio.toFixed(2)}\\): effective Rabi rate \\(\\Omega_{\\mathrm{eff}}/\\Omega = ${eff.toFixed(3)}\\), excited population \\(P_1 = ${p1.toFixed(4)}\\), and ground population \\(P_0 = ${p0.toFixed(4)}\\).`;
    typesetNode(readout);
  }

  function renderQiskit(left, right, readout, thFrac, logShots) {
    const shots = Math.pow(2, Math.round(logShots));
    const th = thFrac * Math.PI;
    // Left panel: Schematic circuit R_y(theta) + CX -> Bell superposition
    left.appendChild(el('text', { x: 152, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, 'Parameterized Circuit & Sampler'));
    left.appendChild(el('line', { x1: 42, y1: 102, x2: 268, y2: 102, class: 'qsim-axis' }));
    left.appendChild(el('line', { x1: 42, y1: 168, x2: 268, y2: 168, class: 'qsim-axis' }));
    left.appendChild(el('text', { x: 34, y: 106, 'text-anchor': 'end', class: 'qsim-label' }, 'q₀'));
    left.appendChild(el('text', { x: 34, y: 172, 'text-anchor': 'end', class: 'qsim-label' }, 'q₁'));

    left.appendChild(el('rect', { x: 74, y: 82, width: 64, height: 40, rx: 5, class: 'qsim-gate-active' }));
    left.appendChild(el('text', { x: 106, y: 106, 'text-anchor': 'middle', class: 'qsim-label' }, `Ry(${thFrac.toFixed(1)}π)`));

    left.appendChild(el('line', { x1: 184, y1: 102, x2: 184, y2: 168, class: 'qsim-vec-1' }));
    left.appendChild(el('circle', { cx: 184, cy: 102, r: 5, class: 'qsim-dot-1' }));
    left.appendChild(el('circle', { cx: 184, cy: 168, r: 11, class: 'qsim-ring' }));
    left.appendChild(el('line', { x1: 173, y1: 168, x2: 195, y2: 168, class: 'qsim-vec-1' }));
    left.appendChild(el('line', { x1: 184, y1: 157, x2: 184, y2: 179, class: 'qsim-vec-1' }));

    const p00 = Math.pow(Math.cos(th / 2), 2);
    const p11 = Math.pow(Math.sin(th / 2), 2);
    const expZZ = 1.0;
    const expXX = Math.sin(th);
    const sigma = 1 / Math.sqrt(shots);

    // Right panel: Exact probabilities vs finite-shot Estimator curve <X tensor X>
    const rx0 = 340, ry0 = 228, rw = 266, rh = 170;
    right.appendChild(el('text', { x: rx0 + rw / 2, y: 28, 'text-anchor': 'middle', class: 'qsim-title' }, `Populations P(00), P(11) (${shots} shots)`));
    right.appendChild(el('line', { x1: rx0, y1: ry0, x2: rx0 + rw, y2: ry0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: rx0, y1: ry0 - rh, x2: rx0, y2: ry0, class: 'qsim-axis' }));

    let dP11 = '', dP00 = '';
    for (let i = 0; i <= 50; i++) {
      const u = (i / 50) * 2.0;
      const px = rx0 + (u / 2.0) * rw;
      dP11 += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + (ry0 - Math.sin(u * Math.PI / 2) ** 2 * rh).toFixed(1) + ' ';
      dP00 += (i === 0 ? 'M' : 'L') + px.toFixed(1) + ',' + (ry0 - Math.cos(u * Math.PI / 2) ** 2 * rh).toFixed(1) + ' ';
    }
    right.appendChild(el('path', { d: dP00, class: 'qsim-curve-2' }));
    right.appendChild(el('path', { d: dP11, class: 'qsim-curve-1' }));
    right.appendChild(el('circle', { cx: rx0 + (thFrac / 2.0) * rw, cy: ry0 - p11 * rh, r: 5, class: 'qsim-dot-1' }));

    readout.innerHTML = `Statevector \\(|\\psi(\\theta)\\rangle = \\cos(\\theta/2)|00\\rangle + \\sin(\\theta/2)|11\\rangle\\): \\(P(00) = ${p00.toFixed(3)}\\), \\(P(11) = ${p11.toFixed(3)}\\), correlators \\(\\langle Z\\otimes Z\\rangle = ${expZZ.toFixed(2)}\\), \\(\\langle X\\otimes X\\rangle = ${expXX.toFixed(3)}\\), and shot noise \\(\\sigma \\approx 1/\\sqrt{${shots}} = ${sigma.toFixed(4)}\\).`;
    typesetNode(readout);
  }

  function renderAlgoStepper(left, right, readout, phiFrac, stepVal) {
    const step = Math.round(stepVal);
    const phi = phiFrac * Math.PI;
    // Left panel: 5-stage quantum circuit with active column highlight
    left.appendChild(el('text', { x: 165, y: 26, 'text-anchor': 'middle', class: 'qsim-title' }, `Quantum Circuit Stepper — Stage t = ${step} / 4`));
    const stageX = [46, 102, 162, 222, 276];
    const stageNames = ['|0⟩', 'H⊗n', 'O_φ', 'U_int', 'Meas'];
    // Highlight current stage column
    left.appendChild(el('rect', { x: stageX[step] - 22, y: 42, width: 44, height: 176, rx: 5, class: 'qsim-stage-highlight' }));

    [82, 130, 178].forEach((wy, idx) => {
      left.appendChild(el('line', { x1: 30, y1: wy, x2: 300, y2: wy, class: 'qsim-axis' }));
      left.appendChild(el('text', { x: 24, y: wy + 4, 'text-anchor': 'end', class: 'qsim-muted' }, `q${idx}`));
    });
    for (let s = 1; s <= 4; s++) {
      left.appendChild(el('rect', {
        x: stageX[s] - 18, y: 64, width: 36, height: 132, rx: 4,
        class: s <= step ? 'qsim-gate-active' : 'qsim-plaq',
      }));
      left.appendChild(el('text', { x: stageX[s], y: 134, 'text-anchor': 'middle', class: 'qsim-label' }, stageNames[s]));
    }

    // Compute 4-state probabilities at stage `step`
    let probs = [1, 0, 0, 0];
    let ketLatex = '|00\\rangle';
    if (step === 1) {
      probs = [0.25, 0.25, 0.25, 0.25];
      ketLatex = '\\frac{1}{2}\\sum_{x=0}^{3}|x\\rangle';
    } else if (step === 2) {
      probs = [0.25, 0.25, 0.25, 0.25];
      ketLatex = `\\frac{1}{2}\\sum_{x=0}^{3} e^{i x (${phiFrac.toFixed(2)}\\pi)}|x\\rangle`;
    } else if (step >= 3) {
      const p0 = Math.pow(Math.cos(phi / 2), 4);
      const p1 = 2 * Math.pow(Math.cos(phi / 2) * Math.sin(phi / 2), 2);
      const p2 = Math.pow(Math.sin(phi / 2), 4);
      probs = [p0, p1 / 2, p2, p1 / 2];
      ketLatex = step === 3
        ? `\\sum_{y=0}^{3} \\alpha_y(${phiFrac.toFixed(2)}\\pi)|y\\rangle`
        : `\\text{Readout peak } P(y^\\star) = ${Math.max(...probs).toFixed(3)}`;
    }

    // Right panel: Bar chart of measurement probabilities P(00), P(01), P(10), P(11)
    const rx0 = 352, ry0 = 224, rw = 250, rh = 166;
    right.appendChild(el('text', { x: rx0 + rw / 2, y: 26, 'text-anchor': 'middle', class: 'qsim-title' }, `Basis Probabilities P(y) = |⟨y|ψ_${step}⟩|²`));
    right.appendChild(el('line', { x1: rx0, y1: ry0, x2: rx0 + rw, y2: ry0, class: 'qsim-axis' }));
    right.appendChild(el('line', { x1: rx0, y1: ry0 - rh, x2: rx0, y2: ry0, class: 'qsim-axis' }));

    ['|00⟩', '|01⟩', '|10⟩', '|11⟩'].forEach((lbl, idx) => {
      const bx = rx0 + 18 + idx * 58;
      const bh = Math.max(3, probs[idx] * rh);
      right.appendChild(el('rect', { x: bx, y: ry0 - bh, width: 36, height: bh, rx: 3, class: idx === 2 && step >= 3 ? 'qsim-bar-2' : 'qsim-bar-1' }));
      right.appendChild(el('text', { x: bx + 18, y: ry0 + 18, 'text-anchor': 'middle', class: 'qsim-muted' }, lbl));
      right.appendChild(el('text', { x: bx + 18, y: ry0 - bh - 6, 'text-anchor': 'middle', class: 'qsim-label' }, probs[idx].toFixed(2)));
    });

    readout.innerHTML = `<strong>Layer \\(t = ${step}\\):</strong> state \\(|\\psi_${step}\\rangle = ${ketLatex}\\) with phase parameter \\(\\varphi = ${phiFrac.toFixed(2)}\\pi\\).`;
    typesetNode(readout);
  }

  const RENDERERS = {
    helstrom: renderHelstrom,
    channel: renderChannel,
    entropy: renderEntropy,
    majorization: renderMajorization,
    stabilizer: renderStabilizer,
    surface: renderSurface,
    gpt: renderGpt,
    hardware: renderHardware,
    qiskit: renderQiskit,
    algo_stepper: renderAlgoStepper,
  };

  function initSim(figure) {
    const kind = figure.getAttribute('data-sim-kind') || 'helstrom';
    const left = figure.querySelector('.qsim-left-panel');
    const right = figure.querySelector('.qsim-right-panel');
    const readout = figure.querySelector('[data-qsim-readout]');
    const pInput = figure.querySelector('[data-qsim-param]');
    const aInput = figure.querySelector('[data-qsim-aux]');
    const pOut = pInput ? figure.querySelector(`output[for="${pInput.id}"]`) : null;
    const aOut = aInput ? figure.querySelector(`output[for="${aInput.id}"]`) : null;
    const playBtn = figure.querySelector('[data-qsim-action="play"]');
    const stepBtn = figure.querySelector('[data-qsim-action="step"]');
    const resetBtn = figure.querySelector('[data-qsim-action="reset"]');
    if (!left || !right || !pInput || !aInput) return;

    const initP = pInput.getAttribute('value') || pInput.value;
    const initA = aInput.getAttribute('value') || aInput.value;
    let timer = null;

    function draw() {
      const pVal = parseFloat(pInput.value);
      const aVal = parseFloat(aInput.value);
      if (pOut) pOut.textContent = pInput.value;
      if (aOut) aOut.textContent = aInput.value;
      left.replaceChildren();
      right.replaceChildren();
      const fn = RENDERERS[kind] || renderHelstrom;
      fn(left, right, readout, pVal, aVal);
    }

    function stopPlay() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      if (playBtn) {
        playBtn.setAttribute('aria-pressed', 'false');
        playBtn.textContent = 'Animate';
      }
    }

    function advanceOnce() {
      if (kind === 'algo_stepper') {
        const cur = Math.round(parseFloat(aInput.value));
        aInput.value = String((cur + 1) % 5);
      } else {
        const min = parseFloat(pInput.min);
        const max = parseFloat(pInput.max);
        const step = parseFloat(pInput.step) || 0.05;
        let next = parseFloat(pInput.value) + step;
        if (next > max + 1e-9) next = min;
        const decimals = (pInput.step.split('.')[1] || '').length;
        pInput.value = next.toFixed(decimals);
      }
      draw();
    }

    pInput.addEventListener('input', draw);
    aInput.addEventListener('input', draw);

    if (stepBtn) {
      stepBtn.addEventListener('click', () => {
        stopPlay();
        advanceOnce();
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        stopPlay();
        pInput.value = initP;
        aInput.value = initA;
        draw();
      });
    }
    if (playBtn) {
      playBtn.addEventListener('click', () => {
        if (timer) {
          stopPlay();
        } else {
          playBtn.setAttribute('aria-pressed', 'true');
          playBtn.textContent = 'Pause';
          timer = setInterval(advanceOnce, 750);
        }
      });
    }

    draw();
  }

  function boot() {
    document.querySelectorAll('.qcourse-sim').forEach(initSim);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

