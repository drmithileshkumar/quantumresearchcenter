"""The homepage opening: an authentic quantum mechanical Mach–Zehnder interferometer experiment."""


def opening():
    return '''<section class="home-opening" aria-labelledby="home-title">
<header class="home-intro">
<p class="eyebrow">Learn · Explore · Research</p>
<h1 id="home-title">Quantum science.<br><em>One idea at a time.</em></h1>
<p>Understand the principles, explore the mathematics, and see what changes when you try an idea for yourself.</p>
<p class="home-description">Courses, interactive experiments, and research explained with care.</p>
<a class="home-primary" href="education/index.html">Explore the courses <span aria-hidden="true">→</span></a>
<a class="home-secondary" href="#latest-news">Read the latest news ↓</a>
</header>
<figure class="home-interference" aria-labelledby="interference-title">
<div class="home-figure-heading"><p class="eyebrow">Experiment · Single-Photon Interference</p><span aria-hidden="true">01</span></div>
<h2 id="interference-title">Mach–Zehnder Interferometer</h2>
<p class="home-figure-intro">Single photons split into a superposition across two arms, acquire an optical phase shift \(\\phi\), and interfere at the second beam splitter. A photon interferes only with itself.</p>

<div class="mzi-stage">
<svg id="mzi-svg" viewBox="0 0 440 250" role="img" aria-labelledby="mzi-svg-title mzi-svg-desc">
<title id="mzi-svg-title">Single-photon Mach–Zehnder interferometer</title>
<desc id="mzi-svg-desc">A single-photon source emits wavepackets through a 50:50 beam splitter BS1, splitting into an upper path with an adjustable phase shifter and a lower path with mirrors. Both paths recombine at beam splitter BS2 and are recorded at detectors D0 and D1.</desc>

<g class="mzi-grid-guides" aria-hidden="true">
<path class="mzi-beam-guide" d="M35 180 H110 V70 H280 M110 180 H280 V70 M280 70 H365 M280 70 V15"/>
</g>

<!-- Optical components -->
<!-- Source -->
<g class="mzi-comp" id="mzi-source-group" transform="translate(14, 168)">
<rect x="0" y="0" width="44" height="24" rx="3" class="mzi-box-housing"/>
<circle cx="44" cy="12" r="3" class="mzi-aperture"/>
<text x="20" y="16" class="mzi-text-label">Source</text>
</g>

<!-- Beam Splitter 1 (BS1) -->
<g class="mzi-comp" id="mzi-bs1-group" transform="translate(110, 180)">
<rect x="-14" y="-14" width="28" height="28" class="mzi-bs-cube"/>
<line x1="-12" y1="-12" x2="12" y2="12" class="mzi-bs-diag"/>
<text x="0" y="27" class="mzi-comp-name">BS₁</text>
</g>

<!-- Mirror 2 (Upper left) -->
<g class="mzi-comp" id="mzi-m2-group" transform="translate(110, 70)">
<line x1="-14" y1="14" x2="14" y2="-14" class="mzi-mirror-line"/>
<text x="-16" y="-8" class="mzi-comp-name">M₂</text>
</g>

<!-- Mirror 1 (Lower right) -->
<g class="mzi-comp" id="mzi-m1-group" transform="translate(280, 180)">
<line x1="-14" y1="14" x2="14" y2="-14" class="mzi-mirror-line"/>
<text x="18" y="16" class="mzi-comp-name">M₁</text>
</g>

<!-- Phase Shifter -->
<g class="mzi-comp" id="mzi-phase-group" transform="translate(170, 57)">
<rect x="0" y="0" width="50" height="26" rx="4" class="mzi-phase-cell"/>
<text x="25" y="17" class="mzi-phase-text" id="mzi-phase-display">φ = 0°</text>
</g>

<!-- Lower path blocker / absorber (toggled) -->
<g class="mzi-comp mzi-blocker" id="mzi-blocker" transform="translate(190, 168)" style="display:none">
<rect x="0" y="0" width="10" height="24" rx="2" class="mzi-blocker-slab"/>
<text x="5" y="34" class="mzi-blocker-label">Blocked</text>
</g>

<!-- Beam Splitter 2 (BS2) -->
<g class="mzi-comp" id="mzi-bs2-group" transform="translate(280, 70)">
<rect x="-14" y="-14" width="28" height="28" class="mzi-bs-cube"/>
<line x1="-12" y1="-12" x2="12" y2="12" class="mzi-bs-diag"/>
<text x="18" y="27" class="mzi-comp-name">BS₂</text>
</g>

<!-- Detector 0 (Output port 0, horizontal) -->
<g class="mzi-comp" id="mzi-d0-group" transform="translate(365, 58)">
<rect x="0" y="0" width="42" height="24" rx="3" class="mzi-det-box" id="mzi-d0-box"/>
<circle cx="0" cy="12" r="3" class="mzi-aperture"/>
<text x="21" y="16" class="mzi-text-label">D₀</text>
<circle cx="0" cy="12" r="14" class="mzi-det-flash" id="mzi-d0-flash" opacity="0"/>
</g>

<!-- Detector 1 (Output port 1, vertical) -->
<g class="mzi-comp" id="mzi-d1-group" transform="translate(268, 0)">
<rect x="0" y="0" width="24" height="25" rx="3" class="mzi-det-box" id="mzi-d1-box"/>
<circle cx="12" cy="25" r="3" class="mzi-aperture"/>
<text x="12" y="16" class="mzi-text-label">D₁</text>
<circle cx="12" cy="25" r="14" class="mzi-det-flash" id="mzi-d1-flash" opacity="0"/>
</g>

<!-- Path annotations -->
<text x="195" y="47" class="mzi-path-annotation">Upper arm · |0⟩</text>
<text x="195" y="202" class="mzi-path-annotation">Lower arm · |1⟩</text>

<!-- Traveling quantum wavepackets / photons -->
<g id="mzi-photons" aria-hidden="true"></g>
</svg>

<div class="mzi-meters" aria-label="Detector probabilities">
<div class="mzi-meter-row">
<div class="mzi-meter-meta">
<span class="mzi-meter-name">Detector D₀ <em>(P = cos²(φ/2))</em></span>
<span class="mzi-meter-val" id="mzi-p0-val">100%</span>
</div>
<div class="mzi-meter-track" role="progressbar" id="mzi-p0-bar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" aria-label="Probability of detection at D0">
<div class="mzi-meter-fill mzi-fill-d0" id="mzi-p0-fill" style="width:100%"></div>
</div>
<span class="mzi-count-tag" id="mzi-d0-count">0 clicks</span>
</div>

<div class="mzi-meter-row">
<div class="mzi-meter-meta">
<span class="mzi-meter-name">Detector D₁ <em>(P = sin²(φ/2))</em></span>
<span class="mzi-meter-val" id="mzi-p1-val">0%</span>
</div>
<div class="mzi-meter-track" role="progressbar" id="mzi-p1-bar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" aria-label="Probability of detection at D1">
<div class="mzi-meter-fill mzi-fill-d1" id="mzi-p1-fill" style="width:0%"></div>
</div>
<span class="mzi-count-tag" id="mzi-d1-count">0 clicks</span>
</div>
</div>
</div>

<div class="mzi-controls">
<div class="mzi-control-row">
<label for="home-phase" class="mzi-slider-label">Phase shift φ: <output id="home-phase-value" for="home-phase">0°</output></label>
<input id="home-phase" type="range" min="0" max="360" step="1" value="0" aria-describedby="mzi-status-desc">
</div>

<div class="mzi-btn-row">
<div class="mzi-presets" aria-label="Phase presets">
<button type="button" class="mzi-chip-btn" data-phase="0">0° (100% D₀)</button>
<button type="button" class="mzi-chip-btn" data-phase="90">90° (Balanced)</button>
<button type="button" class="mzi-chip-btn" data-phase="180">180° (100% D₁)</button>
</div>
<div class="mzi-actions">
<button type="button" id="mzi-fire-btn" class="mzi-btn mzi-btn-subtle">Emit single photon</button>
<button type="button" id="mzi-pause-btn" class="mzi-btn mzi-btn-subtle" aria-pressed="false">Pause</button>
<label class="mzi-check-label"><input type="checkbox" id="mzi-block-toggle"> Block lower arm</label>
</div>
</div>
</div>

<figcaption>
<p id="mzi-status-desc">At <strong>φ = 0°</strong>, destructive interference completely extinguishes detection at D₁: every single photon emerges at D₀.</p>
<p>Each photon enters in superposition, travels both arms simultaneously, and interferes with itself at the second beam splitter. Blocking an arm destroys the superposition, yielding an equal 50 / 50 distribution at both detectors regardless of φ.</p>
<div class="mzi-fig-links">
<a href="tools/single-qubit.html">Single-qubit state visualizer →</a>
<a href="research/foundations-of-quantum-mechanics/composite-quantum-systems/index.html">Why composite systems use tensor products →</a>
</div>
</figcaption>
</figure></section>
<section class="home-learning" aria-labelledby="home-learning-title">
<div class="home-section-heading"><p class="eyebrow">Choose a direction</p><h2 id="home-learning-title">A place to begin.<br>A way to go deeper.</h2></div>
<div class="home-paths">
<a href="education/computing/index.html"><span class="home-path-number">01</span><div><h3>Learn the foundations</h3><p>A guided course from classical computation to quantum algorithms, with worked examples along the way.</p></div><span aria-hidden="true">↗</span></a>
<a href="tools/index.html"><span class="home-path-number">02</span><div><h3>Put an idea to the test</h3><p>Change a quantum state, apply an operation, and connect the picture to the calculation.</p></div><span aria-hidden="true">↗</span></a>
<a href="research/index.html"><span class="home-path-number">03</span><div><h3>Follow an open question</h3><p>Explore research through its assumptions, mathematical models, and unanswered questions.</p></div><span aria-hidden="true">↗</span></a>
</div></section>
<div class="section-top home-current"><div><p class="eyebrow">From the field</p><h2>Discoveries &amp; perspectives</h2></div><a href="news/index.html">Visit the news desk ↗</a></div>'''
