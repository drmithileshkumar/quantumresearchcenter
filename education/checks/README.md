# Course validation

The developed manuscript set comprises 11 Quantum Algorithms chapters,
16 Quantum Programming chapters, 16 Quantum Information chapters, 19 Quantum Hardware chapters,
and 17 Quantum Foundations chapters.
Canonical text is in each course's `content/`; rebuild before checking readers.

```sh
python3 education/algorithms/build.py
python3 education/programming/build.py
python3 education/information/build.py
python3 education/hardware/build.py
python3 education/hardware/checks/worked_examples.py
python3 education/foundations/build.py
python3 education/checks/check_courses.py
python3 education/checks/check_mathematics.py
python3 education/algorithms/checks/worked_examples.py
python3 education/algorithms/checks/chapter_examples.py
python3 -m unittest discover -s tests
```

`check_courses.py` requires Beautiful Soup and checks all 86 reader pages,
section/subsection agreement with metadata, developed sections, solutions,
embedded/downloadable code agreement, local references, fragments, IDs, and image
alternatives. `check_mathematics.py` requires NumPy and verifies small instances
independently of the reader: phases, Fourier transforms, amplification, walks,
operator embeddings, polynomial response, evolution, variational objectives,
measurement feedback, mixed states, discrimination, entanglement filters,
error correction, and teleportation. It does not prove the general theorems.

Programming has a separate pinned environment and local runner documented in
[its testing record](../programming/TESTING.md). All 16 companions pass locally;
the explicitly guarded hardware submission branch has not been executed.

Optional browser validation requires Google Chrome and a Node version providing
WebSocket:

```sh
node education/checks/check_render.mjs
# Or check only the hardware course:
node education/checks/check_render.mjs hardware
```

This opens only local course files, checks MathJax completion and errors, missing
images, and page overflow across every chapter at desktop and 390-pixel widths.
It writes representative screenshots and its browser profile to a temporary
folder, not the repository. The desktop and mobile passes succeeded; circuit
renders and representative page screenshots were also visually inspected.

Shared site tests passed. Site catalog regeneration was limited to the education
index, preserving the manually maintained research/student page. No commit,
publish action, or quantum hardware job is part of validation.
