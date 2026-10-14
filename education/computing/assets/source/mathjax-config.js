// Pinned local MathJax bundle: no CDN is needed when presenting.
window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    packages: ['base', 'ams', 'newcommand', 'configmacros'],
    macros: {
      ket: ['\\lvert #1\\rangle', 1],
      bra: ['\\langle #1\\rvert', 1],
      NP: '\\mathsf{NP}', BPP: '\\mathsf{BPP}', BQP: '\\mathsf{BQP}',
      braket: ['\\langle #1\\vert #2\\rangle', 2],
      ketbra: ['\\lvert #1\\rangle\\!\\langle #2\\rvert', 2],
      tr: '\\operatorname{tr}'
    }
  },
  svg: { fontCache: 'local' },
  options: { enableMenu: false },
  startup: {
    pageReady: async () => {
      await MathJax.startup.defaultPageReady();
      // SVG text cannot contain HTML math containers. Convert its TeX to native
      // MathJax SVG and retain the existing label's position and baseline.
      const namespace = 'http://www.w3.org/2000/svg';
      for (const label of document.querySelectorAll('svg text[data-tex]')) {
        const rendered = await MathJax.tex2svgPromise(label.dataset.tex, { display: false });
        const equation = rendered.querySelector('svg');
        const [, , width] = equation.getAttribute('viewBox').split(/\s+/).map(Number);
        const scale = parseFloat(getComputedStyle(label).fontSize) / 1000;
        const x = Number(label.getAttribute('x'));
        const y = Number(label.getAttribute('y'));
        const anchor = label.getAttribute('text-anchor');
        const offset = anchor === 'middle' ? width * scale / 2 : anchor === 'end' ? width * scale : 0;
        const group = document.createElementNS(namespace, 'g');
        group.setAttribute('class', 'diagram-math');
        group.setAttribute('transform', `translate(${x - offset} ${y}) scale(${scale})`);
        group.setAttribute('role', 'img');
        group.setAttribute('aria-label', label.textContent);
        group.dataset.tex = label.dataset.tex;
        const title = document.createElementNS(namespace, 'title');
        title.textContent = label.textContent;
        group.append(title, ...equation.childNodes);
        label.replaceWith(group);
      }
      document.documentElement.dataset.mathReady = 'true';
    }
  }
};
