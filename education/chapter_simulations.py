"""Interactive, MathJax-formatted visual simulations for course chapters.

Provides a tailored interactive simulation figure (`<section class="chapter-sim-section" id="interactive-lab">`)
for each chapter across `course_builder.py`, `information/build.py`, and `algorithms/build.py`.
Every control has an explicit `<label for="...">` and accessible button text, and every visualization
displays live MathJax equations updated by `course_sims.js`.
"""
from html import escape as esc


SIM_CONFIGS = {
    'helstrom': {
        'eyebrow': 'Interactive quantum distinguishability lab',
        'param_label': r'State separation angle \(\theta/\pi\)',
        'min': '0.05', 'max': '1.00', 'step': '0.05', 'val': '0.50',
        'aux_label': r'Prior probability \(p = \Pr(\rho)\)',
        'aux_min': '0.10', 'aux_max': '0.90', 'aux_step': '0.05', 'aux_val': '0.50',
        'formula': r'\[T(\rho,\sigma) = \frac{1}{2}\|\rho-\sigma\|_1 = \sin\!\left(\frac{\theta}{2}\right),\qquad p_{\mathrm{guess}} = \frac{1 + \|p\rho - (1-p)\sigma\|_1}{2}\]',
    },
    'channel': {
        'eyebrow': 'Interactive quantum channel & decoherence lab',
        'param_label': r'Channel noise strength \(\gamma\)',
        'min': '0.00', 'max': '1.00', 'step': '0.05', 'val': '0.30',
        'aux_label': r'Input Bloch polar angle \(\theta/\pi\)',
        'aux_min': '0.00', 'aux_max': '1.00', 'aux_step': '0.05', 'aux_val': '0.50',
        'formula': r'\[\mathcal{E}(\rho) = \sum_{k} K_k \rho K_k^\dagger,\qquad \mathrm{Tr}\!\left[\mathcal{E}(\rho)^2\right] = \frac{1 + \|\mathbf{r}^\prime\|^2}{2}\]',
    },
    'entropy': {
        'eyebrow': 'Interactive quantum entropy & capacity explorer',
        'param_label': r'Channel noise / mixing parameter \(p\)',
        'min': '0.01', 'max': '0.99', 'step': '0.02', 'val': '0.20',
        'aux_label': r'Input ensemble weight \(q\)',
        'aux_min': '0.10', 'aux_max': '0.90', 'aux_step': '0.05', 'aux_val': '0.50',
        'formula': r'\[S(\rho) = -\mathrm{Tr}(\rho\log_2\rho),\qquad \chi = S\!\left(\sum_x q_x \rho_x\right) - \sum_x q_x S(\rho_x)\]',
    },
    'majorization': {
        'eyebrow': 'Interactive entanglement & majorization lab',
        'param_label': r'Source Schmidt weight \(\lambda_1^{(\psi)}\)',
        'min': '0.50', 'max': '0.98', 'step': '0.02', 'val': '0.70',
        'aux_label': r'Target Schmidt weight \(\lambda_1^{(\phi)}\)',
        'aux_min': '0.50', 'aux_max': '0.98', 'aux_step': '0.02', 'aux_val': '0.84',
        'formula': r'\[|\psi\rangle \xrightarrow{\mathrm{LOCC}} |\phi\rangle \iff \sum_{j=1}^{k}\lambda_j^{\downarrow}(\psi) \le \sum_{j=1}^{k}\lambda_j^{\downarrow}(\phi),\qquad E(|\psi\rangle) = H_2(\lambda_1)\]',
    },
    'stabilizer': {
        'eyebrow': 'Interactive stabilizer syndrome & threshold decoder',
        'param_label': r'Physical Pauli error rate \(p\)',
        'min': '0.01', 'max': '0.30', 'step': '0.01', 'val': '0.08',
        'aux_label': r'Injected fault location \(q_j\)',
        'aux_min': '1', 'aux_max': '7', 'aux_step': '1', 'aux_val': '3',
        'formula': r'\[S_k E |\psi_L\rangle = (-1)^{s_k} E |\psi_L\rangle,\qquad p_L(p) = \sum_{w = t+1}^{n} \binom{n}{w} p^w (1-p)^{n-w}\]',
    },
    'surface': {
        'eyebrow': 'Interactive planar surface-code syndrome lattice',
        'param_label': r'Physical error rate \(p\) vs. threshold \(p_{\mathrm{th}}\)',
        'min': '0.002', 'max': '0.020', 'step': '0.001', 'val': '0.007',
        'aux_label': r'Code distance \(d = 2t + 1\)',
        'aux_min': '3', 'aux_max': '9', 'aux_step': '2', 'aux_val': '5',
        'formula': r'\[S_p^{(Z)} = \prod_{e\in\partial p} Z_e,\quad S_v^{(X)} = \prod_{e\ni v} X_e,\qquad p_L(d) \propto \left(\frac{p}{p_{\mathrm{th}}}\right)^{(d+1)/2}\]',
    },
    'gpt': {
        'eyebrow': 'Interactive operational state space & decoherence lab',
        'param_label': r'Analyzer / context angle \(\theta/\pi\)',
        'min': '0.00', 'max': '1.00', 'step': '0.05', 'val': '0.25',
        'aux_label': r'Environmental decoherence \(\Gamma t\)',
        'aux_min': '0.00', 'aux_max': '3.00', 'aux_step': '0.10', 'aux_val': '0.40',
        'formula': r'\[\rho(t) = \begin{pmatrix} p & c\,e^{-\Gamma t}e^{-i\omega t} \\ c^*\,e^{-\Gamma t}e^{i\omega t} & 1-p \end{pmatrix},\qquad \mathcal{V}(t) = \mathcal{V}_0 e^{-\Gamma t}\]',
    },
    'hardware': {
        'eyebrow': 'Interactive physical qubit pulse & coherence simulator',
        'param_label': r'Drive pulse area \(\Omega t_g / \pi\)',
        'min': '0.05', 'max': '2.00', 'step': '0.05', 'val': '1.00',
        'aux_label': r'Normalized detuning \(\Delta / \Omega\)',
        'aux_min': '-1.50', 'aux_max': '1.50', 'aux_step': '0.10', 'aux_val': '0.00',
        'formula': r'\[P_1(t) = \frac{\Omega^2}{\Omega^2+\Delta^2}\sin^2\!\left(\frac{\sqrt{\Omega^2+\Delta^2}\,t}{2}\right)e^{-t/T_2},\qquad \Omega_{\mathrm{eff}} = \sqrt{\Omega^2+\Delta^2}\]',
    },
    'qiskit': {
        'eyebrow': 'Interactive circuit statevector & shot-sampling simulator',
        'param_label': r'Parameterized gate angle \(\theta/\pi\)',
        'min': '0.00', 'max': '2.00', 'step': '0.05', 'val': '0.50',
        'aux_label': r'Measurement budget \(\log_2(N_{\mathrm{shots}})\)',
        'aux_min': '4', 'aux_max': '12', 'aux_step': '1', 'aux_val': '8',
        'formula': r'\[|\psi(\theta)\rangle = U(\theta)|0\rangle^{\otimes n},\qquad \langle H\rangle = \langle\psi(\theta)|H|\psi(\theta)\rangle,\qquad \sigma_{\hat{\mu}} \propto \frac{1}{\sqrt{N_{\mathrm{shots}}}}\]',
    },
    'algo_stepper': {
        'eyebrow': 'Interactive step-by-step quantum circuit & statevector stepper',
        'param_label': r'Algorithmic phase / parameter \(\varphi/\pi\)',
        'min': '0.05', 'max': '1.00', 'step': '0.05', 'val': '0.50',
        'aux_label': r'Active circuit layer \(t\)',
        'aux_min': '0', 'aux_max': '4', 'aux_step': '1', 'aux_val': '2',
        'formula': r'\[|\psi_t\rangle = U_t O_x \cdots U_1 O_x U_0 |0\rangle^{\otimes n},\qquad P(y) = |\langle y|\psi_t\rangle|^2\]',
    },
}


def pick_kind(course_slug, stem):
    """Select the most fitting simulation engine for a given course and chapter stem."""
    num = int(stem[:2]) if stem[:2].isdigit() else 1
    if course_slug == 'algorithms':
        return 'algo_stepper'
    if course_slug == 'information-theory':
        if num == 1:
            return 'helstrom'
        if num in (2, 8):
            return 'channel'
        if num == 4:
            return 'majorization'
        return 'entropy'
    if course_slug == 'error-correction':
        return 'surface' if num == 7 else 'stabilizer'
    if course_slug in ('foundations', 'interpretations'):
        if course_slug == 'foundations' and num in (2, 3, 7, 8):
            return 'helstrom'
        if course_slug == 'foundations' and num in (4, 13):
            return 'majorization'
        if course_slug == 'foundations' and num == 15:
            return 'channel'
        return 'gpt'
    if course_slug == 'hardware':
        if num in (6, 14):
            return 'channel'
        if num in (15, 18):
            return 'stabilizer'
        return 'hardware'
    if course_slug in ('programming', 'qml', 'cryptography'):
        if course_slug == 'cryptography' and num in (3, 4):
            return 'entropy'
        if course_slug == 'programming' and num == 13:
            return 'channel'
        return 'qiskit'
    if course_slug == 'information':
        if num in (1, 3, 7, 8):
            return 'helstrom'
        if num in (4, 10, 13):
            return 'majorization'
        if num in (5, 6, 9):
            return 'channel'
        if num == 14:
            return 'stabilizer'
        return 'entropy'
    return 'helstrom'


def render(course_slug, stem, chapter_title, question=''):
    """Return the HTML section for a chapter's interactive visual simulation."""
    kind = pick_kind(course_slug, stem)
    cfg = SIM_CONFIGS[kind]
    uid = f'sim-{course_slug}-{stem}'
    p_id = f'{uid}-param'
    a_id = f'{uid}-aux'
    return f'''<section class="chapter-sim-section" id="interactive-lab" aria-labelledby="interactive-lab-heading">
<h2 id="interactive-lab-heading">Interactive visual simulation · {esc(chapter_title)}</h2>
<figure class="qcourse-sim" data-sim-kind="{kind}" data-sim-course="{esc(course_slug)}" data-sim-stem="{esc(stem)}" data-sim-title="{esc(chapter_title)}">
  <header class="qcourse-sim-header">
    <p class="qcourse-sim-eyebrow">{esc(cfg['eyebrow'])}</p>
    <p class="qcourse-sim-subtitle">{esc(question)}</p>
  </header>
  <div class="qcourse-sim-scroll" role="region" tabindex="0" aria-label="Interactive diagram for {esc(chapter_title)}; scroll horizontally on small screens">
    <svg class="qcourse-sim-svg" viewBox="0 0 640 280" role="img" aria-label="Interactive mathematical visualization for {esc(chapter_title)}">
      <title>{esc(chapter_title)} — Interactive Simulation</title>
      <desc>Left panel displays the state, circuit, or code geometry; right panel plots quantitative response curves as parameters vary.</desc>
      <rect x="0" y="0" width="640" height="280" rx="8" class="qsim-bg"/>
      <g class="qsim-left-panel"></g>
      <g class="qsim-right-panel"></g>
    </svg>
  </div>
  <div class="qcourse-sim-controls">
    <div class="qcourse-sim-sliders">
      <label for="{p_id}">{cfg['param_label']}: <output id="{p_id}-out" for="{p_id}">{cfg['val']}</output>
        <input id="{p_id}" type="range" min="{cfg['min']}" max="{cfg['max']}" step="{cfg['step']}" value="{cfg['val']}" data-qsim-param>
      </label>
      <label for="{a_id}">{cfg['aux_label']}: <output id="{a_id}-out" for="{a_id}">{cfg['aux_val']}</output>
        <input id="{a_id}" type="range" min="{cfg['aux_min']}" max="{cfg['aux_max']}" step="{cfg['aux_step']}" value="{cfg['aux_val']}" data-qsim-aux>
      </label>
    </div>
    <div class="qcourse-sim-actions">
      <button type="button" data-qsim-action="play" aria-pressed="false">Animate</button>
      <button type="button" data-qsim-action="step">Next step</button>
      <button type="button" data-qsim-action="reset">Reset</button>
    </div>
  </div>
  <div class="qcourse-sim-math" aria-live="polite">
    <div class="qcourse-sim-StaticFormula">{cfg['formula']}</div>
    <p class="qcourse-sim-readout" data-qsim-readout>Adjust the controls or press <strong>Next step</strong> to inspect the live state and quantitative predictions.</p>
  </div>
  <figcaption>Interactive model for <strong>{esc(chapter_title)}</strong>. All mathematical quantities are rendered with MathJax and update synchronously with the schematic and response plot.</figcaption>
  <noscript><p>Enable JavaScript to interact with the parameter sliders and step-by-step animation. The static equations and chapter derivations remain complete without JavaScript.</p></noscript>
</figure>
</section>'''

