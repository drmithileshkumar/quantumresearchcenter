/* Haar-model kernel concentration. A model calculation for teaching, not a hardware claim. */
(() => {
  const box = document.getElementById('kernel-explorer');
  if (!box) return;
  const slider = document.getElementById('kernel-n');
  const curve = document.getElementById('kernel-curve');
  const marker = document.getElementById('kernel-marker');
  const x = n => 54 + (n - 1) / 11 * 440;
  const y = std => 28 + (-Math.log10(std)) / 4 * 210;
  const spreadOf = n => { const d = 2 ** n; return Math.sqrt((d - 1) / d ** 3); };
  function update() {
    const n = Number(slider.value);
    const d = 2 ** n, mean = 1 / d, spread = spreadOf(n), shots = 100 / mean;
    document.getElementById('kernel-n-value').textContent = String(n);
    document.getElementById('kernel-dim').textContent = String(d);
    document.getElementById('kernel-mean').textContent = mean.toExponential(3);
    document.getElementById('kernel-spread').textContent = spread.toExponential(3);
    document.getElementById('kernel-verdict').textContent = shots > 1e6
      ? `Each entry needs about ${shots.toExponential(0)} shots for 10% relative error: the estimator is the bottleneck.`
      : `Each entry needs about ${shots.toExponential(0)} shots for 10% relative error.`;
    const points = Array.from({ length: 12 }, (_, i) => {
      const k = i + 1;
      return (i ? 'L' : 'M') + x(k).toFixed(2) + ',' + y(spreadOf(k)).toFixed(2);
    });
    curve.setAttribute('d', points.join(' '));
    marker.setAttribute('cx', x(n).toFixed(2));
    marker.setAttribute('cy', y(spread).toFixed(2));
  }
  slider.addEventListener('input', update);
  update();
})();
