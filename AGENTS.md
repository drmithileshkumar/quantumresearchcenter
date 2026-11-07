# Site maps

Public pages, `website-map/` and `sitemap.xml` are build output and are not committed. Whenever adding, renaming, or removing a public page, run `python3 scripts/build_all.py`, then `python3 scripts/check_site.py` to ensure every link resolves and every page is reachable. The shared inventory automatically discovers public HTML pages, including standalone pages and nested directories; redirects, noindex pages, and build inputs are excluded.

# Math on pages

Set every mathematical expression with the local MathJax bundle rather than a unicode or HTML approximation: `\(n\)`, `\(2^n\)`, `\(\ket{n,k}\)`, `\(z^n+1\)`, `\(E_G\)` in place of `2<sup>n</sup>`, `|n,k⟩`, `zⁿ + 1`, `E<sub>G</sub>`. Inline math is `\(...\)` and display math is `\[...\]`; `scripts/build.py` adds the MathJax script tags whenever a page body contains either delimiter. The macros `\ket`, `\bra`, `\braket`, `\ketbra` and `\tr` come from `education/computing/assets/source/mathjax-config.js`.

Inside an SVG, HTML math cannot be nested in `<text>`, so put the TeX on the label as `data-tex` (math only) or `data-math` (prose around `\(...\)`) and let the config typeset it into the figure.

Measured numbers and script-written readouts stay plain monospace text unless the script typesets them again with `MathJax.tex2svgPromise`; `tools/majorana.js` shows that pattern, including coalescing while a drag updates the value.
