/* Mach–Zehnder Single-Photon Interferometer Simulation */
(() => {
  'use strict';

  const svg = document.getElementById('mzi-svg');
  if (!svg) return;

  const phaseInput = document.getElementById('home-phase');
  const phaseValue = document.getElementById('home-phase-value');
  const phaseSvgDisplay = document.getElementById('mzi-phase-display');
  const statusDesc = document.getElementById('mzi-status-desc');

  const p0Val = document.getElementById('mzi-p0-val');
  const p1Val = document.getElementById('mzi-p1-val');
  const p0Fill = document.getElementById('mzi-p0-fill');
  const p1Fill = document.getElementById('mzi-p1-fill');
  const p0Bar = document.getElementById('mzi-p0-bar');
  const p1Bar = document.getElementById('mzi-p1-bar');
  const d0Count = document.getElementById('mzi-d0-count');
  const d1Count = document.getElementById('mzi-d1-count');

  const flash0 = document.getElementById('mzi-d0-flash');
  const flash1 = document.getElementById('mzi-d1-flash');
  const blocker = document.getElementById('mzi-blocker');
  const blockToggle = document.getElementById('mzi-block-toggle');
  const fireBtn = document.getElementById('mzi-fire-btn');
  const pauseBtn = document.getElementById('mzi-pause-btn');
  const photonsGroup = document.getElementById('mzi-photons');

  let phaseDeg = Number(phaseInput.value) || 0;
  let isBlocked = false;
  let isPlaying = true;
  let counts = [0, 0];
  let photons = [];
  let lastSpawn = 0;
  let lastTime = 0;
  let animId = 0;

  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    isPlaying = false;
    if (pauseBtn) {
      pauseBtn.textContent = 'Play';
      pauseBtn.setAttribute('aria-pressed', 'true');
    }
  }

  // Geometry coordinates
  const POS = {
    source: { x: 58, y: 180 },
    bs1: { x: 110, y: 180 },
    m2: { x: 110, y: 70 },
    shifterMid: { x: 195, y: 70 },
    m1: { x: 280, y: 180 },
    barrier: { x: 195, y: 180 },
    bs2: { x: 280, y: 70 },
    d0: { x: 365, y: 70 },
    d1: { x: 280, y: 25 }
  };

  // Path lengths:
  // L0: source -> bs1 = 52px
  // L_upper: bs1 -> m2 (110) + m2 -> bs2 (170) = 280px
  // L_lower: bs1 -> m1 (170) + m1 -> bs2 (110) = 280px
  // L_d0: bs2 -> d0 = 85px
  // L_d1: bs2 -> d1 = 45px
  const SPEED = 150; // pixels per second
  const TOTAL_PATH = 52 + 280 + 85; // 417px

  function updateMeters() {
    const rad = phaseDeg * Math.PI / 180;
    let prob0, prob1;
    if (isBlocked) {
      prob0 = 0.5;
      prob1 = 0.5;
    } else {
      prob0 = Math.cos(rad / 2) ** 2;
      prob1 = Math.sin(rad / 2) ** 2;
    }

    const pct0 = Math.round(prob0 * 100);
    const pct1 = Math.round(prob1 * 100);

    p0Val.textContent = `${pct0}%`;
    p1Val.textContent = `${pct1}%`;
    p0Fill.style.width = `${pct0}%`;
    p1Fill.style.width = `${pct1}%`;
    p0Bar.setAttribute('aria-valuenow', pct0);
    p1Bar.setAttribute('aria-valuenow', pct1);

    phaseValue.value = `${phaseDeg}°`;
    phaseSvgDisplay.textContent = `φ = ${phaseDeg}°`;

    let desc;
    if (isBlocked) {
      desc = 'Lower arm is blocked. The path superposition is destroyed: each transmitted photon reaches D₀ or D₁ with an unbiased 50% probability regardless of φ.';
    } else if (phaseDeg === 0) {
      desc = 'At φ = 0°, complete destructive interference cancels detector D₁: 100% of photons emerge at D₀.';
    } else if (phaseDeg === 180) {
      desc = 'At φ = 180°, complete destructive interference cancels detector D₀: 100% of photons emerge at D₁.';
    } else if (phaseDeg === 90 || phaseDeg === 270) {
      desc = `At φ = ${phaseDeg}°, interference produces a balanced 50% / 50% split between D₀ and D₁.`;
    } else {
      desc = `At φ = ${phaseDeg}°, quantum interference allocates P(D₀) = ${pct0}% and P(D₁) = ${pct1}%.`;
    }
    statusDesc.textContent = desc;
  }

  function flashDetector(idx) {
    const el = idx === 0 ? flash0 : flash1;
    const box = idx === 0 ? document.getElementById('mzi-d0-box') : document.getElementById('mzi-d1-box');
    if (!el) return;
    el.setAttribute('opacity', '1');
    el.setAttribute('r', '8');
    if (box) box.classList.add('mzi-det-active');

    setTimeout(() => {
      el.setAttribute('opacity', '0');
      el.setAttribute('r', '14');
      if (box) box.classList.remove('mzi-det-active');
    }, 280);

    counts[idx]++;
    d0Count.textContent = `${counts[0]} click${counts[0] === 1 ? '' : 's'}`;
    d1Count.textContent = `${counts[1]} click${counts[1] === 1 ? '' : 's'}`;
  }

  function spawnPhoton() {
    const rad = phaseDeg * Math.PI / 180;
    const prob0 = isBlocked ? 0.5 : (Math.cos(rad / 2) ** 2);
    const chosenDetector = Math.random() < prob0 ? 0 : 1;
    const lowerBlocked = isBlocked;

    photons.push({
      dist: 0,
      chosenDetector,
      lowerBlocked,
      absorbed: false,
      elUpper: null,
      elLower: null,
      elInit: null
    });
  }

  function getPointOnPath(dist, branch, chosenDetector) {
    // Initial segment: 0 -> 52 (Source to BS1)
    if (dist <= 52) {
      return { x: POS.source.x + dist, y: POS.source.y };
    }

    const dArm = dist - 52;
    // Inside arms: 0 -> 280
    if (dArm <= 280) {
      if (branch === 'upper') {
        // bs1 (110, 180) -> m2 (110, 70) [110px]
        if (dArm <= 110) {
          return { x: POS.bs1.x, y: POS.bs1.y - dArm };
        }
        // m2 (110, 70) -> bs2 (280, 70) [170px]
        const dHoriz = dArm - 110;
        return { x: POS.m2.x + dHoriz, y: POS.m2.y };
      } else {
        // lower arm
        // bs1 (110, 180) -> m1 (280, 180) [170px]
        if (dArm <= 170) {
          return { x: POS.bs1.x + dArm, y: POS.bs1.y };
        }
        // m1 (280, 180) -> bs2 (280, 70) [110px]
        const dVert = dArm - 170;
        return { x: POS.m1.x, y: POS.m1.y - dVert };
      }
    }

    // Beyond BS2: 280 -> 280 + (85 for d0, 45 for d1)
    const dOut = dArm - 280;
    if (chosenDetector === 0) {
      // bs2 (280, 70) -> d0 (365, 70) [85px]
      return { x: Math.min(POS.d0.x, POS.bs2.x + dOut), y: POS.bs2.y };
    } else {
      // bs2 (280, 70) -> d1 (280, 25) [45px]
      return { x: POS.bs2.x, y: Math.max(POS.d1.y, POS.bs2.y - dOut) };
    }
  }

  function makePulseElement(className) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', className);
    const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    core.setAttribute('r', '3.5');
    core.setAttribute('class', 'mzi-pulse-core');
    const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    ring.setAttribute('r', '7.5');
    ring.setAttribute('class', 'mzi-pulse-halo');
    g.appendChild(ring);
    g.appendChild(core);
    photonsGroup.appendChild(g);
    return g;
  }

  function loop(timestamp) {
    if (!lastTime) lastTime = timestamp;
    const dt = Math.min((timestamp - lastTime) / 1000, 0.1);
    lastTime = timestamp;

    if (isPlaying && timestamp - lastSpawn > 1750) {
      spawnPhoton();
      lastSpawn = timestamp;
    }

    for (let i = photons.length - 1; i >= 0; i--) {
      const p = photons[i];
      p.dist += SPEED * dt;

      // 1. Initial segment before BS1
      if (p.dist <= 52) {
        if (!p.elInit) p.elInit = makePulseElement('mzi-pulse-packet');
        const pt = getPointOnPath(p.dist, 'init');
        p.elInit.setAttribute('transform', `translate(${pt.x}, ${pt.y})`);
      } else {
        if (p.elInit) {
          p.elInit.remove();
          p.elInit = null;
        }

        // Inside or beyond arms
        const dArm = p.dist - 52;
        if (dArm <= 280) {
          // Upper arm
          if (!p.elUpper) p.elUpper = makePulseElement('mzi-pulse-packet mzi-pulse-upper');
          const ptU = getPointOnPath(p.dist, 'upper');
          p.elUpper.setAttribute('transform', `translate(${ptU.x}, ${ptU.y})`);

          // Lower arm
          if (p.lowerBlocked && dArm >= 85) {
            // Lower arm is blocked at x = 195 (85px from BS1)
            if (p.elLower) {
              p.elLower.remove();
              p.elLower = null;
            }
          } else {
            if (!p.elLower) p.elLower = makePulseElement('mzi-pulse-packet mzi-pulse-lower');
            const ptL = getPointOnPath(p.dist, 'lower');
            p.elLower.setAttribute('transform', `translate(${ptL.x}, ${ptL.y})`);
          }
        } else {
          // Beyond BS2: interference has occurred!
          if (p.elUpper) {
            p.elUpper.remove();
            p.elUpper = null;
          }
          if (p.elLower) {
            p.elLower.remove();
            p.elLower = null;
          }

          const dOut = dArm - 280;
          const maxOut = p.chosenDetector === 0 ? 85 : 45;

          if (dOut <= maxOut) {
            if (!p.elOut) p.elOut = makePulseElement('mzi-pulse-packet mzi-pulse-combined');
            const ptOut = getPointOnPath(p.dist, 'out', p.chosenDetector);
            p.elOut.setAttribute('transform', `translate(${ptOut.x}, ${ptOut.y})`);
          } else {
            // Arrived at detector!
            if (p.elOut) {
              p.elOut.remove();
              p.elOut = null;
            }
            flashDetector(p.chosenDetector);
            photons.splice(i, 1);
          }
        }
      }
    }

    animId = requestAnimationFrame(loop);
  }

  // Event handlers
  phaseInput.addEventListener('input', () => {
    phaseDeg = Number(phaseInput.value);
    updateMeters();
  });

  document.querySelectorAll('.mzi-chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetPhase = Number(btn.dataset.phase);
      phaseInput.value = targetPhase;
      phaseDeg = targetPhase;
      updateMeters();
    });
  });

  blockToggle.addEventListener('change', () => {
    isBlocked = blockToggle.checked;
    blocker.style.display = isBlocked ? 'block' : 'none';
    updateMeters();
  });

  fireBtn.addEventListener('click', () => {
    spawnPhoton();
    if (!isPlaying) {
      // Run for 3 seconds then stop
      isPlaying = true;
      setTimeout(() => { isPlaying = false; }, 3200);
    }
  });

  pauseBtn.addEventListener('click', () => {
    isPlaying = !isPlaying;
    pauseBtn.textContent = isPlaying ? 'Pause' : 'Resume';
    pauseBtn.setAttribute('aria-pressed', (!isPlaying).toString());
  });

  updateMeters();
  animId = requestAnimationFrame(loop);
})();
