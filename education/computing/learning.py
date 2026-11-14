"""Render book-wide learning aids from reviewed, chapter-specific content."""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import html, json, re, sys, zipfile
from illustrations import SPECS as ILLUSTRATIONS, plain
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from concept_asides import inject_concept_asides
LEARNING=json.loads((ROOT/'content/learning.json').read_text())
GLOSSARY=json.loads((ROOT/'content/glossary.json').read_text())
PROBING=json.loads((ROOT/'content/probing-questions.json').read_text())
SOLUTIONS=json.loads((ROOT/'content/problem-solutions.json').read_text())
KEYWORDS=json.loads((ROOT/'content/keywords.json').read_text())
NOTATION=json.loads((ROOT/'content/notation.json').read_text())
def esc(value): return html.escape(str(value),quote=True)
def guide(stem):
 if stem == 'assignments':
  return '<aside class="learning-guide"><h2>Using the assignments</h2><p>These comprehensive problem sets bring together concepts across multiple chapters. Work through each problem by hand before reviewing the complete worked solutions.</p></aside>'
 if stem == 'exams':
  return '<aside class="learning-guide"><h2>Oral Examination Guide</h2><p>These conceptual problems probe understanding, intuition, and architectural vision rather than rote symbolic calculation. Designed for a 30-minute oral defense covering Chapters 1 through 6.</p></aside>'
 if stem not in LEARNING:
  return '<aside class="learning-guide"><h2>Using the appendices</h2><p>These are supporting references. Read them when a chapter points here; completing them in advance is not required.</p></aside>'
 d=LEARNING[stem]
 return '<details class="learning-guide"><summary>Reading guide · preparation, aims, and assumptions</summary>'+f'<p>{esc(d["purpose"])}</p><h3>Before you begin</h3><p>{esc(d["before"])}</p><h3>What you should be able to do</h3><ul>'+''.join(f'<li>{esc(x)}</li>' for x in d['outcomes'])+f'</ul><h3>The example to follow</h3><p>{esc(d["example"])}</p><h3>Scope and assumptions</h3><p>{esc(d["limits"])}</p></details>'
def exercises(stem,index,title):
 if stem not in LEARNING:return ''
 d=LEARNING[stem];pieces=['<section class="chapter-practice" id="practice"><h2>Questions and worked problems</h2><p>Attempt each question before opening a hint. Explain your reasoning, then compare it with the solution.</p>']
 for i,e in enumerate(d['exercises'],1):
  ident=f'exercise-{i}'
  hints=''.join(f'<details class="exercise-hint"><summary>Hint {n}</summary><p>{esc(h)}</p></details>' for n,h in enumerate(e['hints'],1))
  pieces.append(f'<article class="exercise" id="{ident}"><h3>{i}. {esc(e["kind"])} <a class="heading-link" href="#{ident}" aria-label="Link to exercise {i}">§</a></h3><p>{esc(e["question"])}</p>{hints}<details class="exercise-solution"><summary>Worked solution</summary><p>{esc(e["answer"])}</p></details><p><a href="#{esc(e["review"])}">Revisit the relevant explanation</a></p></article>')
  index.append(dict(title=title+' — '+e['kind'],chapter='Exercises',url=stem+'.html#'+ident,text=e['question']+' '+e['answer']))
 pieces.append(f'<p class="chapter-bridge"><strong>Where this leads.</strong> {esc(d["next"])}</p></section>')
 return ''.join(pieces)
PREDICTIONS={
 'no-signalling':(r'This figure tracks the joint amplitudes and Bob’s marginal readout probabilities for \((\ket{00}+\ket{01}+\ket{11})/\sqrt{3}\). Apply local gates such as \(H\) on Alice’s qubit and compare Bob’s marginal distribution before and after.', r'Bob’s probability of observing \(0\) stays fixed at \(1/3\). Alice’s local gate redistributes amplitude among her own basis labels while preserving the squared norm accompanying each of Bob’s outcomes, so Bob’s local statistics remain invariant without classical communication.'),
 'teleportation':(r'This interactive teleportation circuit steps through Bell-pair sharing, Alice’s CNOT and Hadamard gates, her two-bit measurement \((m_1,m_2)\), and Bob’s conditional Pauli corrections \(X^{m_2}Z^{m_1}\). Step through all four measurement branches to compare Bob’s state before and after the classical correction.', r'Each of Alice’s four outcomes \(00,01,10,11\) occurs with probability \(1/4\) regardless of \(\alpha\) and \(\beta\). Before Bob applies \(X^{m_2}Z^{m_1}\), his four branch states average to \(I/2\); applying the two-bit-controlled Pauli correction restores \(\alpha\ket{0}+\beta\ket{1}\) on every branch.'),
 'bell':(r'This circuit stepper prepares a two-qubit state from \(\ket{00}\) using a Hadamard gate \(H\) on the first qubit followed by a CNOT gate. Step through the two gates to compare the intermediate product state with the final correlated outcome probabilities.', r'After \(H\), outcomes \(00\) and \(10\) each have probability \(1/2\). The CNOT gate flips the target when the control is \(1\), turning \(10\) into \(11\) and leaving \(00\) and \(11\) with probability \(1/2\) each.'),
 'phase':(r'This circuit compares Deutsch’s parity test on constant and balanced Boolean functions. Select each oracle type, step through the phase kickback and final Hadamard gate, and test whether complementing every output flips the measured bit.', r'A constant function yields \(0\) and a balanced function yields \(1\). Complementing every function value multiplies the state after the phase oracle by a global sign \(-1\), leaving the final measurement outcome unchanged.'),
 'grover':(r'This simulator runs Grover’s search iteration from a uniform superposition and plots the marked-state probability after each step. Set the search space size to 4, step through one and two iterations, and observe how over-rotation affects the success probability.', r'On a 4-item search space, one iteration rotates the state directly onto the marked item with probability \(1\), whereas a second iteration over-rotates the state and drops the success probability back to \(1/4\).'),
 'proofs':(r'This proof checker steps line by line through a formal derivation from stated axioms. Generate a candidate proof and run the checker to see how it verifies each line by matching earlier formulas against modus ponens.', r'Only axiom lines are accepted outright. For every subsequent line, the checker locates two earlier lines of the form \(X\) and \(X\Rightarrow Y\) and verifies symbol by symbol that the new line is \(Y\).'),
 'reversible':(r'This diagram maps inputs to outputs for finite Boolean functions and shows the effect of retaining the input register. Compare a 2-bit-to-1-bit map with an equal-width map, then toggle Keep the input too to see how colliding arrows separate.', r'A map from 2 bits to 1 bit sends 4 inputs into 2 outputs, so collisions are unavoidable. Retaining the input embeds each \(x\) into \((x,f(x))\), whose first coordinate distinguishes distinct inputs and makes the map one-to-one.'),
 'nand-toffoli':(r'This circuit converter translates irreversible NAND gates into reversible Toffoli gates with initialized ancilla wires. Step forward through the computation, copy the output, and run the Toffoli stages in reverse to observe workspace uncomputation.', r'Each NAND gate uses a fresh target wire initialized to \(1\). Running the Toffoli stage in reverse after copying the result restores every workspace ancilla to \(1\), leaving only the original inputs and the target answer.'),
 'square-root':(r'This transition diagram composes two identical single-bit steps to build a square root \(S\) of NOT. Step through the two stages to see how complex or signed path weights cancel on the diagonal and reinforce on the off-diagonal.', r'Both \(S\) and \(-S\) square to NOT because each two-step path multiplies two weights whose signs cancel. The identity operation likewise admits multiple square roots—including NOT, \(H\), and \(Z\)—via destructive interference on off-diagonal paths.'),
 'adjoint':(r'This geometric viewer compares a linear transformation \(A\) and its conjugate transpose \(A^\dagger\) acting on \(\ket{\psi}\). Switch between the non-unitary shear and the unitary rotation to compare \(AA^\dagger\ket{\psi}\) and \(A^\dagger A\ket{\psi}\).', r'For the non-unitary shear, \(AA^\dagger\) and \(A^\dagger A\) rotate \(\ket{\psi}\) by different angles and alter its norm. For the unitary rotation, \(A^\dagger A=AA^\dagger=I\), so \(A^\dagger\) acts as the exact inverse of \(A\).'),
 'parallel':(r'This simulator applies the reversible evaluation unitary \(U_f\) for AND to an equal superposition of all four 2-bit inputs and then measures the register. Run repeated single-shot measurements to see how many queries are needed to observe all four truth-table rows.', r'Each measurement collapses the superposition to a single random pair \((x,f(x))\) with probability \(1/4\). Because outcomes repeat at random, collecting all four rows requires \(25/3\approx 8.3\) runs on average without interference.'),
 'euclid':(r'This table traces Euclid’s greatest-common-divisor algorithm step by step on a pair \((a,b)\). Run the division steps on \((48,18)\) and on the Fibonacci pair \((89,55)\) to observe the preserved divisor invariant and the rate of remainder descent.', r'From \((48,18)\), three remainder steps reach \((6,0)\) while keeping \(\gcd(a,b)=6\) invariant on every row. Consecutive Fibonacci inputs such as \((89,55)\) produce quotients of \(1\) at every step, yielding the slowest possible descent.'),
 'turing':(r'This state-and-tape simulator executes a Turing machine one transition at a time. Select a problem, step the tape head through the state diagram, and compare single-pass acceptance on \(1^n\) with back-and-forth marking on palindromes.', r'At each step, the current state and scanned tape symbol select a single outgoing transition arrow. Reading \(n\) ones takes \(n+1\) steps, whereas marking symbols from both ends sweeps across the tape repeatedly and takes \(O(n^2)\) steps.'),
 'cancel':(r'This two-path amplitude diagram sums the transition weights \(ca+db\) from initial state \(i\) to final state \(k\). Vary the second-path weight \(d\) across negative and positive values to see when adding a path lowers the total transition weight.', r'With \(a=b=c=1/2\), setting \(d=-1/2\), \(-1/4\), and \(1/2\) yields total weights \(0\), \(1/8\), and \(1/2\). Whenever \(d<0\), the two paths interfere destructively and the two-path sum falls below the single-path weight \(ca=1/4\).'),
 'interference':(r'This phasor diagram shows how a Hadamard gate recombines the amplitudes of \(\ket{0}+e^{i\phi}\ket{1}\). Sweep the relative phase \(\phi\) from \(0\) to \(\pi\) to track \(p(0)\), then vary the global phase \(\theta\) to compare the arrows and readout probabilities.', r'The outcome probability \(p(0)=(1+\cos\phi)/2\) shifts from \(1\) at \(\phi=0\) to \(1/2\) at \(\phi=\pi/2\) and \(0\) at \(\phi=\pi\). Changing the global phase \(\theta\) rotates both amplitude arrows together without altering the resultant length or probabilities.'),
 'inner':(r'This state-plane viewer projects \(\ket{\psi}\) onto \(\ket{\phi}\) and computes the transition probability \(|\braket{\phi|\psi}|^2\). Drag \(\ket{\psi}\) through \(30^\circ\), \(45^\circ\), \(90^\circ\), and \(180^\circ\) relative to \(\ket{\phi}\) to observe how projection length sets the Born probability.', r'At separation angle \(\theta\), the transition probability is \(\cos^2\theta\): \(3/4\) at \(30^\circ\), \(1/2\) at \(45^\circ\), and \(0\) at \(90^\circ\) where the states are orthogonal. At \(180^\circ\), the inner product is \(-1\) and the probability returns to \(1\).'),
 'measure':(r'This measurement simulator compares repeated projective measurements on fresh copies of \((\sqrt{3}/2)\ket{0}+(1/2)\ket{1}\) against repeated measurements on the same post-measurement qubit. Draw 100 fresh samples, then re-measure a single collapsed state.', r'Across 100 fresh copies, outcome \(1\) appears about \(25\pm 4\) times in accordance with \(|1/2|^2=1/4\). Re-measuring the same qubit after outcome \(1\) yields \(1\) deterministically because the first measurement projected the state onto \(\ket{1}\).'),
 'reflect':(r'This two-dimensional plane traces Grover’s iteration as a reflection \(O_f\) across the unmarked axis followed by a reflection \(D\) across the initial superposition \(\ket{s}\). Step through \(O_f\) and \(D\) for \(N=4\) to follow the state angle across two iterations.', r'Starting at \(30^\circ\) for \(N=4\), \(O_f\) reflects the state to \(-30^\circ\) and \(D\) reflects it to \(90^\circ\) (the marked axis, probability \(1\)). A second iteration adds another \(60^\circ\) rotation to \(150^\circ\), reducing the success probability to \(\sin^2 150^\circ=1/4\).'),
 'parallelism':(r'This interactive animation visualizes how the evaluation unitary \(U_f\) acts on a superposition of two-qubit inputs. Select a Boolean function and step through the calculation to watch each basis configuration pass through \(U_f\) and transform into \(\ket{x}\ket{y \oplus f(x)}\).', r'When the inputs start in an equal superposition \(\frac{1}{2}\sum_x \ket{x}\), a single application of \(U_f\) acts on every basis branch in parallel. The output register becomes \(\frac{1}{2}\sum_x \ket{x}\ket{f(x)}\), holding the complete function behavior in a single three-qubit state.'),
 'gates':(r'This single-qubit circuit tester applies sequences of \(X\), \(Z\), and \(H\) gates to \(\ket{0}\) and displays the resulting state vector and measurement bars. Compare the sequence \(H\to H\) with \(H\to Z\to H\) to see how \(H\) converts phase flips into bit flips.', r'Applying \(H\) twice cancels the off-diagonal phases and returns \(\ket{0}\) with certainty. Inserting \(Z\) between the two Hadamard gates flips the relative phase of \(\ket{1}\), so the second \(H\) interferes constructively on \(\ket{1}\) instead (\(HZH=X\)).')}
def enrich(soup):
 for section in soup.select('.reading-topic'):
  ident=section['id']
  if ident not in PROBING:
   raise ValueError(f'Missing probing question for {ident}')
  if not section.select('figure,svg,img') and ident in ILLUSTRATIONS:
   spec=ILLUSTRATIONS[ident]
   section.append(BeautifulSoup(f'<figure class="book-drawing subsection-illustration"><div class="drawing-scroll" tabindex="0" role="region" aria-label="{esc(plain(spec["title"]))}; scroll horizontally on small screens"><img src="assets/figures/subsections/{ident}.svg" alt="{esc(plain(spec["caption"]))}" loading="lazy"/></div><figcaption>{esc(spec["caption"])}</figcaption></figure>','html.parser'))
  if KEYWORDS.get(ident):
   source=re.sub(r'\s+',' ',section.get_text(' ')).lower().replace('’',"'");source=re.sub(r' ([,.;:)])',r'\1',source)
   items=[]
   for term in KEYWORDS[ident]:
    key=term.lower().replace('’',"'")
    if key.startswith('\\(') and key.endswith('\\)'):key=key[2:-2]
    if key not in source and key.rstrip('s') not in source:print(f'Keyword check: "{term}" does not occur in {ident}')
    entry=next((g for g in GLOSSARY if g['term'].lower()==term.lower()),None)
    items.append(f'<a class="glossary-term" href="glossary.html#{entry["slug"]}">{esc(term)}</a>' if entry else f'<span>{esc(term)}</span>')
   (section.find(['h2','h3']) or section).insert_after(BeautifulSoup(f'<p class="keywords" aria-label="Keywords defined in this subsection">{'<span class="keyword-sep" aria-hidden="true"> · </span>'.join(items)}</p>','html.parser'))
  questions=PROBING[ident]
  if set(questions)!={'foundation','application','challenge'} or not all(isinstance(q,str) and q.strip() for q in questions.values()):
   raise ValueError(f'Expected three question levels for {ident}')
  if ident not in SOLUTIONS or set(SOLUTIONS[ident])!=set(questions) or not all(isinstance(a,str) and a.strip() for a in SOLUTIONS[ident].values()):
   raise ValueError(f'Missing problem solution for {ident}')
  items=''.join(f'<li id="{ident}-problem-{n}"><p class="problem-text">{esc(questions[key])}</p><details class="problem-solution"><summary><span class="solution-closed">Show solution</span><span class="solution-open">Hide solution</span></summary><p>{esc(SOLUTIONS[ident][key])}</p></details></li>' for n,key in enumerate(('foundation','application','challenge'),1))
  prompt=BeautifulSoup(f'<details class="probing-question"><summary class="question-label">Problems</summary><ol>{items}</ol></details>','html.parser')
  section.append(prompt)
 # Link one prose occurrence per term per chapter; never modify equations or links.
 for term in GLOSSARY:
  pattern=re.compile(r'(?<![\w-])'+re.escape(term['term'])+r'(?![\w-])',re.I)
  found=False
  for p in soup.select('.book-exposition p'):
   for node in list(p.find_all(string=True)):
    if node.parent.name in ('a','script','style') or node.find_parent('a'):continue
    # Split TeX delimiters before matching prose so notation stays intact.
    parts=re.split(r'(\\\(.*?\\\)|\\\[.*?\\\])',str(node),flags=re.S)
    offset=0
    for part in parts:
     match=None if part.startswith(('\\(','\\[')) else pattern.search(part)
     if match:
      start,end=offset+match.start(),offset+match.end();text=str(node)
      a=soup.new_tag('a',href='glossary.html#'+term['slug']);a['class']='glossary-term';a['title']=plain(term['definition']);a.string=text[start:end]
      node.replace_with(NavigableString(text[:start]),a,NavigableString(text[end:]));found=True;break
     offset+=len(part)
    if found:break
   if found:break
 for lab in soup.select('[data-lab]'):
  key=lab['data-lab']
  if key in PREDICTIONS:
   q,a=PREDICTIONS[key]
   prompt=BeautifulSoup(f'<div class="prediction"><p><strong>Interactive figure.</strong> {esc(q)}</p></div>','html.parser')
   lab.insert_before(prompt)
   lab.insert_after(BeautifulSoup(f'<details class="prediction-answer"><summary>What to observe</summary><p>{esc(a)}</p></details>','html.parser'))
 optional=soup.select_one('#topic-10-3-3 .book-exposition')
 if optional:
  details=soup.new_tag('details',attrs={'class':'optional-note'});summary=soup.new_tag('summary');summary.string='Optional derivation · polynomial lower bounds';details.append(summary);optional.wrap(details)
  for sibling in list(details.next_siblings):details.append(sibling.extract())
  question=soup.select_one('#topic-10-3-3 .probing-question')
  if question:details.append(question.extract())
 inject_concept_asides(soup)
def notation(meta,index):
 """Render the notation index and report symbols used before their explanation."""
 sections,order,tex={},[],{}
 for stem,*_ in meta:
  for sec in json.loads((ROOT/'content'/f'{stem}.json').read_text())['sections']:sections[sec['id']]=(stem,sec['number'],sec['title'])
  soup=BeautifulSoup((ROOT/'content'/f'{stem}.html').read_text(),'html.parser')
  for sec in soup.select('[id^="topic-"],[id^="appendix-"]'):
   order.append(sec['id']);tex[sec['id']]=[a or b for a,b in re.findall(r'\\\((.*?)\\\)|\\\[(.*?)\\\]',sec.get_text(' '),re.S)]
 def link(ident):
  stem,number,title=sections[ident];label='Appendix '+number if ident.startswith('appendix-') else '§'+number
  return f'<a href="{stem}.html#{ident}">{esc(label)} {esc(title)}</a>'
 body='<header class="chapter-header" id="chapter-top"><p class="book-kicker">Reference</p><h1>Notation</h1><p>Each symbol the book uses, how to read it aloud, what it means, and where it is explained. Symbols marked as prerequisites are reviewed in Appendix C.</p></header>'
 for group in NOTATION:
  body+=f'<section class="notation-group"><h2>{esc(group["group"])}</h2><div class="notation-list" role="table" aria-label="{esc(group["group"])}"><div class="notation-row notation-head" role="row"><span role="columnheader">Symbol</span><span role="columnheader">Read as</span><span role="columnheader">Meaning</span><span role="columnheader">Explained in</span></div>'
  for e in group['entries']:
   slug='symbol-'+re.sub(r'[^a-z0-9]+','-',e['read'].lower()).strip('-')
   where=('Prerequisite; reviewed in ' if e.get('prerequisite') else '')+link(e['section'])
   if e.get('intro'):where=f'Introduced in {link(e["intro"])}; developed in {link(e["section"])}'
   body+=f'<div class="notation-row" role="row" id="{slug}"><span role="cell" class="notation-symbol">\\({esc(e["tex"])}\\)</span><span role="cell">{esc(e["read"])}</span><span role="cell">{esc(e["meaning"])}</span><span role="cell">{where}</span></div>'
   index.append(dict(title='Notation: '+e['read'],chapter='Notation',url='notation.html#'+slug,text=plain('\\('+e['tex']+'\\)')+' '+e['meaning']))
   pattern=e.get('pattern')
   if pattern and not e.get('prerequisite'):
    first=next((ident for ident in order if any(re.search(pattern,m) for m in tex[ident])),None)
    explained=min(order.index(x) for x in (e.get('intro'),e['section']) if x)
    if first is None:print(f'Notation check: {e["read"]} is not used in the prose.')
    elif order.index(first)<explained:print(f'Notation check: {e["read"]} is used in {sections[first][1]} before its explanation in {sections[e.get("intro") or e["section"]][1]}.')
  body+='</div></section>'
 return body
def resources(meta,index):
 glossary='<header class="chapter-header" id="chapter-top"><p class="book-kicker">Reference</p><h1>Glossary</h1><p>Short definitions with links to the full explanations. A definition depends on the setting stated here.</p></header><div class="glossary-filter" hidden><label for="glossary-query">Find a term or idea</label><input type="search" id="glossary-query" autocomplete="off"><p id="glossary-status" role="status"></p></div><dl class="glossary-list">'
 for t in sorted(GLOSSARY,key=lambda x:x['term'].lower()):
  glossary+=f'<div id="{t["slug"]}" class="glossary-entry"><dt>{esc(t["term"])}</dt><dd><p>{esc(t["definition"])}</p><a href="{t["url"]}">Read the explanation →</a></dd></div>'
  index.append(dict(title=t['term'],chapter='Glossary',url='glossary.html#'+t['slug'],text=t['definition']))
 glossary+='</dl>'
 study='''<header class="chapter-header" id="chapter-top"><p class="book-kicker">Reading and review</p><h1>Study guide</h1><p>Follow the ten chapters in order on a first reading. Use the appendices when an explanation calls for them.</p></header><section class="book-about"><h2>A route through the book</h2><ol>'''
 for m in meta:
  if m[0] in LEARNING:study+=f'<li><a href="{m[0]}.html">{esc(m[1])}</a>: {esc(LEARNING[m[0]]["purpose"])}</li>'
 study+='''</ol><h2>Follow one calculation across chapters</h2><p>Begin with Boolean function evaluation in Chapter 2. Preserve its inputs and clear its workspace. Chapter 7 uses that reversible evaluation to place a function value in a phase. Chapter 8 constructs the operations from elementary gates. Chapter 9 uses phase marking and reflections to find successful candidates, and Chapter 10 compares their costs and limits. At each step, ask what information changed and what a measurement can reveal.</p><h2>Working through a section</h2><p>Read the explanation and reconstruct its diagram without looking. Calculate one small example. Before using an experiment, write down your prediction and the reason for it. If the result differs, identify the first step where your calculation and the experiment disagree.</p><p>Each subsection has an illustration and three questions, and a subsection that introduces new terms lists them under Keywords. Read the figure with its caption, then use the questions to check the idea and work through a concrete use of it. The questions move from checking the central idea to using it in an example and exploring its implications. Work through them in order, and return to a harder question after further reading if needed. Each problem has a hidden solution: select “Show solution” after attempting it. The responses to open-ended questions give a model argument; other sound examples and explanations may also work. Each chapter ends with a quick check, a worked problem, and an extension. Open hints one at a time. After checking a solution, try the problem again with different inputs. Explaining why a tempting answer fails is useful practice too.</p><h2>Assumptions to keep visible</h2><p>The core circuit model uses ideal gates and states. Query counts treat access to an oracle as a resource in its own right; they do not automatically include building that oracle. A claim about probabilities must identify the measurement. A claim about efficiency must identify input size, allowed error, and the resources counted.</p><h2>Offline reading and printing</h2><p><a href="downloads/quantum-computing.zip" download>Download the complete offline book (ZIP)</a>. Extract the archive and open its index.html in a browser. Equations, figures, search, and experiments are included. External references and links to the main website need an internet connection.</p><p>Use “Print chapter” on any page, or your browser’s print command, to print or save a PDF. Hints, solutions, and optional explanations expand for printing. Interactive figures print their current state; the accompanying prediction and explanation also describe the result.</p><h2>Reader controls and accessibility</h2><p>Use Contents to move between topics, Search (or the / key) to find an idea, and A− or A+ to adjust the text. Tab moves through controls; Enter activates links and buttons. The glossary and expandable explanations also work without JavaScript. Equations have MathJax accessibility support and figures have text descriptions.</p><p>Your text size and last reading location are stored in this browser when local storage is available. They are not sent to a server. Private browsing and some browsers’ local-file settings may prevent persistence. <button type="button" id="clear-reading-data" hidden>Clear saved reading preferences</button> <span id="reading-data-status" role="status"></span></p><h2>Sources and further reading</h2><p>Original sources complement the explanations; they are not prerequisites.</p><ul><li><a href="https://doi.org/10.1112/plms/s2-42.1.230">Turing, On Computable Numbers (1936)</a> — the machine model and limits of decision procedures.</li><li><a href="https://www.feynmanlectures.caltech.edu/III_01.html">The Feynman Lectures, Quantum Behavior</a> — amplitudes and interference.</li><li><a href="https://arxiv.org/abs/quant-ph/9605034">Grover, A fast quantum mechanical algorithm for database search</a> — quantum search.</li><li><a href="https://arxiv.org/abs/quant-ph/9503016">Barenco et al., Elementary gates for quantum computation</a> — gate constructions.</li><li><a href="https://arxiv.org/abs/quant-ph/9802049">Beals et al., Quantum lower bounds by polynomials</a> — an optional continuation of Chapter 10.</li></ul></section>'''
 revisions='''<header class="chapter-header" id="chapter-top"><p class="book-kicker">Editorial record</p><h1>Revisions and corrections</h1></header><section class="book-about"><h2>19 October 2026</h2><p>Expanded the end-of-chapter practice to ten exercises in every chapter, 100 in all, each with hints, a worked solution, and a link to the explanation it draws on. Each set moves from quick checks through worked calculations to a common misconception and extensions that probe limits of the chapter’s results. Chapter 4 received its first end-of-chapter exercises.</p><h2>15 October 2026</h2><p>Revised explanations across all nine chapters to shorten repetition, introduce formulas through their purpose, and state the scope of claims clearly. Updated problems and hidden solutions to test changed assumptions and common mistakes. Aligned the amplitude illustrations and reading guides with the distinction between physical postulates and their mathematical consequences. Refined reading width, postulate styling, tables, and solution controls.</p><p>Added individually expandable solutions to all 336 subsection problems. Solutions are closed initially and expand for printing.</p><p>Completed illustration coverage across all 112 subsections and appendices. Added 86 schematics, comparison tables, and probability or state-space diagrams alongside the existing figures. Each subsection pairs its illustration with three questions progressing from a concept check to application and further reasoning.</p><p>Added three levels of practice after all 107 chapter subsections and five appendices: a foundation question, a concrete application, and an optional deeper challenge. The challenges ask readers to examine assumptions, construct counterexamples, and connect formal statements to their computational meaning.</p><p>Added chapter reading guides with prerequisites, learning aims, examples, and scope; 27 exercises with hints and worked solutions; a linked glossary; prediction prompts for the four experiments; a study guide; and an offline archive. Optional polynomial material is expandable. Printing includes hidden explanations and solutions.</p><h2>Suggest a correction</h2><p><a href="mailto:mail.qrc@gmail.com?subject=Quantum%20Computing%20correction">Email a correction</a> with the chapter, a section or exercise link, the passage in question, and your proposed correction or reasoning. Section and exercise headings have permanent § links.</p><p>This record describes editorial changes. It is not a claim that every argument has undergone independent peer review.</p></section>'''
 return [('glossary','Glossary',glossary),('notation','Notation',notation(meta,index)),('study-guide','Study guide',study),('revisions','Revisions and corrections',revisions)]
def package():
 """Create a deterministic, self-contained extracted-file edition."""
 output=ROOT/'downloads/quantum-computing.zip';output.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  def add(name,content):
   info=zipfile.ZipInfo(name,date_time=(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;archive.writestr(info,content)
  add('index.html','<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=education/computing/index.html"><title>Quantum Computing</title><a href="education/computing/index.html">Open Quantum Computing</a></html>')
  add('styles.css',(ROOT.parents[1]/'styles.css').read_bytes())
  add('navigation.js',(ROOT.parents[1]/'navigation.js').read_bytes())
  add('diagrams.js',(ROOT.parents[1]/'diagrams.js').read_bytes())
  for folder in ('icons','fonts'):
   for file in sorted((ROOT.parents[1]/folder).rglob('*')):
    if file.is_file() and file.suffix!='.html':add(file.relative_to(ROOT.parents[1]).as_posix(),file.read_bytes())
  for file in sorted([*ROOT.glob('*.html'),*(ROOT/'assets').rglob('*')]):
   if not file.is_file():continue
   content=file.read_bytes()
   if file.suffix=='.html':
    text=content.decode()
    for src,dest in [('../../index.html','https://quantumresearch.center/'),('../index.html','https://quantumresearch.center/education/')]:text=text.replace(f'href="{src}"',f'href="{dest}"')
    text=re.sub(r'href="\.\./\.\./([a-z0-9_/-]+?)/index\.html"',r'href="https://quantumresearch.center/\1/"',text)
    text=re.sub(r'<a[^>]*href="downloads/quantum-computing.zip"[^>]*>.*?</a>','<span>Offline edition (already downloaded)</span>',text)
    content=text.encode()
   add('education/computing/'+file.relative_to(ROOT).as_posix(),content)
  add('README.txt','Extract the entire archive, then open index.html. Local equations, figures, search and experiments require no network. External references and main-site links require internet. See the included asset license files for third-party notices.\n')
