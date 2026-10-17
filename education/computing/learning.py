"""Render book-wide learning aids from reviewed, chapter-specific content."""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import html, json, re, zipfile
from illustrations import SPECS as ILLUSTRATIONS, plain
ROOT=Path(__file__).resolve().parent
LEARNING=json.loads((ROOT/'content/learning.json').read_text())
GLOSSARY=json.loads((ROOT/'content/glossary.json').read_text())
PROBING=json.loads((ROOT/'content/probing-questions.json').read_text())
SOLUTIONS=json.loads((ROOT/'content/problem-solutions.json').read_text())
KEYWORDS=json.loads((ROOT/'content/keywords.json').read_text())
NOTATION=json.loads((ROOT/'content/notation.json').read_text())
def esc(value): return html.escape(str(value),quote=True)
def guide(stem):
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
 'bell':(r'Reset to \(\ket{00}\). After \(H\) on the first qubit, which two outcomes are possible? Which outcomes remain after CNOT?', r'After \(H\), \(00\) and \(10\) each have probability \(1/2\). CNOT changes \(10\) to \(11\), so the final outcomes are \(00\) and \(11\), each with probability \(1/2\). The bars alone do not establish entanglement.'),
 'phase':('Compare a constant function with a balanced function. Before running the circuit, predict whether the final input bit is 0 or 1. Would complementing every function value change that bit?', 'A constant function gives 0; a balanced function gives 1. Complementing the function multiplies the state after the phase oracle by a common minus sign, so it does not change the final measurement.'),
 'grover':('Set Search space to 4 and reset. There is one marked item; start from equal amplitudes. Predict the success probability after one iteration and after a second. Does another iteration always help?', r'One iteration gives success probability 1. A second gives \(1/4\): continued rotation can move the state away from the marked direction. Compare this with the initial probability \(1/4\).'),
 'proofs':('Generate a new proof. Before checking it, decide which lines the checker must accept without justification, and what it must confirm about each of the others.', 'Only the axioms are accepted as given. For every other line, the checker finds two earlier lines of the forms X and “X implies Y” and confirms that the line is Y. It compares symbols; it never has to discover the proof.'),
 'reversible':('Before checking a new function, look at its sizes. If it maps 2 bits to 1 bit, must it be irreversible? Then try to name two inputs that share an output, and predict what Keep the input too does to them.', 'A function from 2 bits to 1 bit has 4 inputs but only 2 possible outputs, so two inputs must share one: it is irreversible whatever its table. With equal numbers of input and output bits, it is reversible exactly when no two arrows meet. Keeping the input gives each x the output (x, f(x)), whose first part already differs between different inputs, so no two arrows can meet.'),
 'nand-toffoli':('A circuit has g NAND gates. How many extra bits does its Toffoli version need, and what do they hold after the conversion? What do they hold after the answer is copied and the gates are run backward?', 'One fresh target set to 1 for each NAND gate, so g extra bits, plus one bit set to 0 for the copied answer. After the conversion the targets hold every intermediate NAND value, which is garbage. Because each Toffoli gate is its own inverse, running them backward returns every target to 1, so only the inputs and the copied answer remain.'),
 'square-root':(r'The text found one square root \(S\) of NOT. Is it the only one? Does \(-S\) work? Name a step other than doing nothing whose square does nothing.', r'\(-S\) works, because each path product has two factors and the signs cancel. NOT has four square roots: \(S\), \(-S\), the step with the stay and switch weights of \(S\) exchanged, and its negative. Doing nothing has infinitely many: NOT, Hadamard, and the sign flip each square to doing nothing. The construction in the figure finds only two of them.'),
 'adjoint':(r'For the shear, which order turns \(\ket\psi\) further from its starting direction? Switch to the rotation: what do \(AA^\dagger\ket\psi\) and \(A^\dagger A\ket\psi\) become?', r'For the shear, \(AA^\dagger\) turns \(\ket\psi\) by about \(18.1^\circ\) and \(A^\dagger A\) by about \(4.4^\circ\), and both change its length. For a rotation, \(A^\dagger A=AA^\dagger=I\), so both orders return \(\ket\psi\) exactly: a rotation is unitary, and its adjoint is its inverse.'),
 'euclid':('Before stepping, predict how many steps the run from (48, 18) takes and which quantity stays fixed. Then try (89, 55): will it need more steps or fewer?', 'The run reaches (6, 0) after three steps, and the greatest common divisor 6 is the same in every row. Consecutive Fibonacci numbers such as (89, 55) need nine steps: every quotient is 1, so the second entry falls as slowly as possible.'),
 'turing':('Generate a new problem. Before running it, answer the question yourself, then predict how the machine will reach the answer: which arrow does each step use, and in which state does it halt? For the opening example, how many steps does a block of n ones take?', 'Each step uses exactly one arrow: the one leaving the current state whose label begins with the symbol under the head. The opening example takes n + 1 steps: n moves right over the ones and one step that reads the blank and halts. Machines that mark symbols, such as the palindrome or parenthesis checkers, sweep back and forth, so their step counts grow much faster than the input length. Tracing the diagram this way is what a universal machine does with the encoded rules.'),
 'cancel':(r'With \(a=b=c=1/2\), predict \(W(i\to k)\) for \(d=-1/2\), \(d=-1/4\), and \(d=1/2\). For which values of \(d\) does removing the second path increase the total?', r'The totals are \(0\), \(1/8\), and \(1/2\). Removing the second path leaves \(ca=1/4\), which exceeds the total exactly when \(d\) is negative, because then \(db<0\).'),
 'interference':(r'Predict \(p(0)\) after \(H\) for \(\phi=0\), \(\pi/2\), and \(\pi\). Then change only the global phase \(\theta\): what happens to the arrows, and what happens to the probabilities?', r'\((1+\cos\phi)/2\) gives \(1\), \(1/2\), and \(0\). A global phase turns both contributions, and so their sum, by the same angle. The lengths of the sums, and therefore the probabilities, do not change.'),
 'inner':(r'Keep \(\ket\phi\) fixed and turn \(\ket\psi\). At what angle between them is the probability \(3/4\)? \(1/2\)? \(0\)? What happens at \(180^\circ\)?', r'The probability is \(\cos^2\theta\): \(3/4\) at \(30^\circ\), \(1/2\) at \(45^\circ\), and \(0\) at \(90^\circ\), where the states are orthogonal and the component vanishes. At \(180^\circ\) the amplitude is \(-1\), but the probability is \(1\).'),
 'measure':(r'For \((\sqrt3/2)\ket0+(1/2)\ket1\), about how many of 100 fresh copies give 1? If one measurement gives 1, what does measuring the same system again give?', r'About 25, varying from run to run by roughly 4. Measuring the same system again gives 1 every time, because its state is now \(\ket1\). Only fresh copies reproduce the frequencies \(3/4\) and \(1/4\).'),
 'reflect':(r'For \(N=4\) the state starts at \(30^\circ\). Predict its angle after \(O_f\), then after \(D\). Where is it after a second full iteration?', r'\(O_f\) sends \(30^\circ\) to \(-30^\circ\), and \(D\) sends \(-30^\circ\) to \(90^\circ\), the good direction, so success is certain. A second iteration turns it another \(60^\circ\), to \(150^\circ\), where the success probability is \(\sin^2 150^\circ=1/4\).'),
 'gates':(r'Starting from \(\ket0\), compare applying \(H\) twice with applying \(H\), then \(Z\), then \(H\). Predict both final measurement distributions before trying the gates.', r'\(H\) followed by \(H\) returns \(\ket0\), so 0 is certain. \(H\), \(Z\), \(H\) produces \(\ket1\), so 1 is certain. \(Z\) changes a relative sign that the final \(H\) converts into a different outcome.')}
def enrich(soup):
 for section in soup.select('.reading-topic'):
  ident=section['id']
  if ident not in PROBING:
   raise ValueError(f'Missing probing question for {ident}')
  if not section.select('figure,svg,img'):
   if ident not in ILLUSTRATIONS:raise ValueError(f'Missing illustration for {ident}')
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
   prompt=BeautifulSoup(f'<div class="prediction"><p><strong>Predict first.</strong> {esc(q)}</p></div>','html.parser')
   lab.insert_before(prompt)
   lab.insert_after(BeautifulSoup(f'<details class="prediction-answer"><summary>After trying it: compare your explanation</summary><p>{esc(a)}</p></details>','html.parser'))
 optional=soup.select_one('#topic-10-3-3 .book-exposition')
 if optional:
  details=soup.new_tag('details',attrs={'class':'optional-note'});summary=soup.new_tag('summary');summary.string='Optional derivation · polynomial lower bounds';details.append(summary);optional.wrap(details)
  for sibling in list(details.next_siblings):details.append(sibling.extract())
  question=soup.select_one('#topic-10-3-3 .probing-question')
  if question:details.append(question.extract())
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
 revisions='''<header class="chapter-header" id="chapter-top"><p class="book-kicker">Editorial record</p><h1>Revisions and corrections</h1></header><section class="book-about"><h2>15 October 2026</h2><p>Revised explanations across all nine chapters to shorten repetition, introduce formulas through their purpose, and state the scope of claims clearly. Updated problems and hidden solutions to test changed assumptions and common mistakes. Aligned the amplitude illustrations and reading guides with the distinction between physical postulates and their mathematical consequences. Refined reading width, postulate styling, tables, and solution controls.</p><p>Added individually expandable solutions to all 336 subsection problems. Solutions are closed initially and expand for printing.</p><p>Completed illustration coverage across all 112 subsections and appendices. Added 86 schematics, comparison tables, and probability or state-space diagrams alongside the existing figures. Each subsection pairs its illustration with three questions progressing from a concept check to application and further reasoning.</p><p>Added three levels of practice after all 107 chapter subsections and five appendices: a foundation question, a concrete application, and an optional deeper challenge. The challenges ask readers to examine assumptions, construct counterexamples, and connect formal statements to their computational meaning.</p><p>Added chapter reading guides with prerequisites, learning aims, examples, and scope; 27 exercises with hints and worked solutions; a linked glossary; prediction prompts for the four experiments; a study guide; and an offline archive. Optional polynomial material is expandable. Printing includes hidden explanations and solutions.</p><h2>Suggest a correction</h2><p><a href="mailto:mail.qrc@gmail.com?subject=Quantum%20Computing%20correction">Email a correction</a> with the chapter, a section or exercise link, the passage in question, and your proposed correction or reasoning. Section and exercise headings have permanent § links.</p><p>This record describes editorial changes. It is not a claim that every argument has undergone independent peer review.</p></section>'''
 return [('glossary','Glossary',glossary),('notation','Notation',notation(meta,index)),('study-guide','Study guide',study),('revisions','Revisions and corrections',revisions)]
def package():
 """Create a deterministic, self-contained extracted-file edition."""
 output=ROOT/'downloads/quantum-computing.zip';output.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  def add(name,content):
   info=zipfile.ZipInfo(name,date_time=(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;archive.writestr(info,content)
  add('index.html','<!doctype html><html lang="en"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=education/computing/index.html"><title>Quantum Computing</title><a href="education/computing/index.html">Open Quantum Computing</a></html>')
  add('styles.css',(ROOT.parents[1]/'styles.css').read_bytes())
  for file in sorted((ROOT.parents[1]/'icons').rglob('*')):
   if file.is_file() and file.suffix!='.html':add(file.relative_to(ROOT.parents[1]).as_posix(),file.read_bytes())
  for file in sorted([*ROOT.glob('*.html'),*(ROOT/'assets').rglob('*')]):
   if not file.is_file():continue
   content=file.read_bytes()
   if file.suffix=='.html':
    text=content.decode()
    for src,dest in [('../../index.html','https://quantumresearch.center/'),('../index.html','https://quantumresearch.center/education/'),('../../research/index.html','https://quantumresearch.center/research/')]:text=text.replace(f'href="{src}"',f'href="{dest}"')
    text=re.sub(r'<a[^>]*href="downloads/quantum-computing.zip"[^>]*>.*?</a>','<span>Offline edition (already downloaded)</span>',text)
    content=text.encode()
   add('education/computing/'+file.relative_to(ROOT).as_posix(),content)
  add('README.txt','Extract the entire archive, then open index.html. Local equations, figures, search and experiments require no network. External references and main-site links require internet. See the included asset license files for third-party notices.\n')
