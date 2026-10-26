/* Ideal asymptotic BB84 model. No finite-key or device-security claim. */
(() => {
  const explorer = document.getElementById('rate-explorer');
  if (!explorer) return;
  const error = document.getElementById('rate-q');
  const overhead = document.getElementById('rate-overhead');
  const entropy = q => q === 0 || q === 1 ? 0 : -q*Math.log2(q)-(1-q)*Math.log2(1-q);
  const x = q => 54 + q/0.2*440;
  const y = r => 28 + (1-r)/1.7*210;
  function update() {
    const q = Number(error.value)/100, f = Number(overhead.value);
    const rate = 1-(1+f)*entropy(q);
    document.getElementById('rate-q-value').textContent = (100*q).toFixed(1)+'%';
    document.getElementById('rate-overhead-value').textContent = f.toFixed(2);
    document.getElementById('rate-expression').textContent = rate.toFixed(4);
    document.getElementById('rate-key').textContent = Math.max(0,rate).toFixed(4);
    document.getElementById('rate-verdict').textContent = rate > 0
      ? 'Positive asymptotic bound under these assumptions.'
      : 'This expression supplies no positive key guarantee.';
    const points = Array.from({length:101}, (_, i) => {
      const p=i/500;
      return (i ? 'L' : 'M')+x(p).toFixed(2)+','+y(1-(1+f)*entropy(p)).toFixed(2);
    });
    document.getElementById('rate-curve').setAttribute('d', points.join(' '));
    const marker=document.getElementById('rate-marker');
    marker.setAttribute('cx',x(q)); marker.setAttribute('cy',y(rate));
  }
  error.addEventListener('input',update);
  overhead.addEventListener('input',update);
  update();
})();
