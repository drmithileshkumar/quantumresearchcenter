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
        const style = getComputedStyle(label);
        // Labels may declare the room they have; shrink wide equations to fit it.
        const limit = Number(label.dataset.maxWidth);
        const scale = Math.min(parseFloat(style.fontSize) / 1000, limit ? limit / width : Infinity);
        const x = Number(label.getAttribute('x'));
        const y = Number(label.getAttribute('y'));
        const anchor = label.getAttribute('text-anchor');
        const offset = anchor === 'middle' ? width * scale / 2 : anchor === 'end' ? width * scale : 0;
        const group = document.createElementNS(namespace, 'g');
        group.setAttribute('class', 'diagram-math');
        group.style.color = style.fill;
        group.setAttribute('transform', `translate(${x - offset} ${y}) scale(${scale})`);
        group.setAttribute('role', 'img');
        group.setAttribute('aria-label', label.textContent);
        group.dataset.tex = label.dataset.tex;
        const title = document.createElementNS(namespace, 'title');
        title.textContent = label.textContent;
        group.append(title, ...equation.childNodes);
        label.replaceWith(group);
      }
      // Labels mixing prose and \(...\) keep the prose as SVG text in the label's
      // own font, typeset only the math, and set the pieces side by side.
      for (const label of document.querySelectorAll('svg text[data-math]')) {
        const style = getComputedStyle(label);
        const size = parseFloat(style.fontSize) / 1000;
        const line = document.createElementNS(namespace, 'g');
        line.setAttribute('role', 'img');
        line.setAttribute('aria-label', label.textContent);
        const title = document.createElementNS(namespace, 'title');
        title.textContent = label.textContent;
        line.append(title);
        label.before(line);
        let advance = 0;
        for (const part of label.dataset.math.split(/(\\\(.*?\\\))/s).filter(Boolean)) {
          if (part.startsWith('\\(')) {
            const rendered = await MathJax.tex2svgPromise(part.slice(2, -2), { display: false });
            const equation = rendered.querySelector('svg');
            const [, , width] = equation.getAttribute('viewBox').split(/\s+/).map(Number);
            const math = document.createElementNS(namespace, 'g');
            math.setAttribute('class', 'diagram-math');
            math.style.color = style.fill;
            math.setAttribute('transform', `translate(${advance} 0) scale(${size})`);
            math.append(...equation.childNodes);
            line.append(math);
            advance += width * size;
          } else {
            const prose = document.createElementNS(namespace, 'text');
            if (label.getAttribute('class')) prose.setAttribute('class', label.getAttribute('class'));
            if (label.getAttribute('style')) prose.setAttribute('style', label.getAttribute('style'));
            prose.setAttribute('x', advance);
            prose.setAttribute('y', 0);
            prose.style.whiteSpace = 'pre';
            prose.setAttribute('aria-hidden', 'true');
            prose.textContent = part;
            line.append(prose);
            advance += prose.getComputedTextLength();
          }
        }
        const limit = Number(label.dataset.maxWidth);
        const scale = limit && advance > limit ? limit / advance : 1;
        const anchor = label.getAttribute('text-anchor');
        const offset = anchor === 'middle' ? advance * scale / 2 : anchor === 'end' ? advance * scale : 0;
        line.setAttribute('transform', `translate(${Number(label.getAttribute('x')) - offset} ${Number(label.getAttribute('y'))}) scale(${scale})`);
        line.dataset.math = label.dataset.math;
        label.remove();
      }
      document.documentElement.dataset.mathReady = 'true';
    }
  }
};
