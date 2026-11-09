# Structural principles for website content

The following principles guide all future content creation and revision across the website, including courses, research explanations, news, and interactive learning material. Apply them at a depth appropriate to the page's purpose; they are quality standards, not a mandatory six-part page template. Existing content will be updated in subsequent work.

## What makes a book “best-written”?

1. **Clarity of exposition** – Concepts are introduced gradually, with each new idea building on previously established intuition.
2. **Narrative flow** – The author treats the subject as a story, using analogies, real-world motivations, and purposeful examples rather than isolated definitions.
3. **Pedagogical design** – Thoughtful exercises, summaries, and “what-if” explorations encourage active learning and deeper comprehension.
4. **Concise, precise language** – No superfluous jargon; terminology is defined the first time it appears and reused consistently.
5. **Balanced rigor and accessibility** – Formal proofs are presented with intuition-boosting explanations, so readers can follow the logical structure without feeling lost.
6. **Aesthetic presentation** – Clean typography, well-chosen diagrams, and consistent formatting let the reader focus on the content rather than on visual clutter.

# Site maps

Public pages, `website-map/` and `sitemap.xml` are build output and are not committed. Whenever adding, renaming, or removing a public page, run `python3 scripts/build_all.py`, then `python3 scripts/check_site.py` to ensure every link resolves and every page is reachable. The shared inventory automatically discovers public HTML pages, including standalone pages and nested directories; redirects, noindex pages, and build inputs are excluded.

# Math on pages

Set every mathematical expression with the local MathJax bundle rather than a unicode or HTML approximation: `\(n\)`, `\(2^n\)`, `\(\ket{n,k}\)`, `\(z^n+1\)`, `\(E_G\)` in place of `2<sup>n</sup>`, `|n,k⟩`, `zⁿ + 1`, `E<sub>G</sub>`. Inline math is `\(...\)` and display math is `\[...\]`; `scripts/build.py` adds the MathJax script tags whenever a page body contains either delimiter. The macros `\ket`, `\bra`, `\braket`, `\ketbra` and `\tr` come from `education/computing/assets/source/mathjax-config.js`.

Inside an SVG, HTML math cannot be nested in `<text>`, so put the TeX on the label as `data-tex` (math only) or `data-math` (prose around `\(...\)`) and let the config typeset it into the figure.

Measured numbers and script-written readouts stay plain monospace text unless the script typesets them again with `MathJax.tex2svgPromise`; `tools/majorana.js` shows that pattern, including coalescing while a drag updates the value.

# Course clarity and restraint

Prioritize conceptual clarity over volume. Every paragraph, worked example, and SVG schematic must earn its place by making a concept easier to grasp than prose or equations alone. Do not add boilerplate diagrams, decorative widgets, or long-winded explanations to fill a quota; place a schematic or interactive figure only at the exact point where geometry, circuit structure, or a parameter trade-off directly clarifies the argument.
