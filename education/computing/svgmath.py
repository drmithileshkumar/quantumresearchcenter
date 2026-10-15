"""TeX in SVG figures: labels carry TeX for MathJax and a Unicode fallback.

Labels use the book's inline delimiters, for example 'Apply \\(H\\) to \\(\\ket0\\)'.
MathJax typesets inline SVG text carrying data-tex or data-math (assets/source/mathjax-config.js);
plain() supplies the readable fallback for alt text, descriptions, and standalone files.
"""
from html import escape
import re
MATH=re.compile(r'\\\((.*?)\\\)|\\\[(.*?)\\\]',re.S)
# Readable Unicode for TeX where MathJax cannot run: alt text and SVG descriptions.
SYMBOLS={'theta':'θ','pi':'π','psi':'ψ','phi':'φ','Phi':'Φ','alpha':'α','beta':'β','gamma':'γ','lambda':'λ','rho':'ρ','mu':'μ','epsilon':'ε','varepsilon':'ε','Omega':'Ω','Theta':'Θ','otimes':'⊗','oplus':'⊕','to':'→','mapsto':'↦','leftarrow':'←','Rightarrow':'⇒','le':'≤','leq':'≤','ge':'≥','geq':'≥','ne':'≠','neq':'≠','approx':'≈','cdot':'·','times':'×','pm':'±','mp':'∓','circ':'∘','dagger':'†','in':'∈','notin':'∉','neg':'¬','land':'∧','lor':'∨','sum':'Σ','infty':'∞','ldots':'…','cdots':'⋯','langle':'⟨','rangle':'⟩','lvert':'|','rvert':'|','mid':'|','lceil':'⌈','rceil':'⌉','lfloor':'⌊','rfloor':'⌋','subseteq':'⊆','emptyset':'∅','sin':'sin','cos':'cos','log':'log','tr':'tr','BQP':'BQP','BPP':'BPP','NP':'NP','bmod':' mod ','ln':'ln ','prime':'′','square':'□','gcd':'gcd'}
SUPER=dict(zip('0123456789+-−n()kTij†*′','⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻ⁿ⁽⁾ᵏᵀⁱʲ†*′'));SUB=dict(zip('0123456789+-−ijknt','₀₁₂₃₄₅₆₇₈₉₊₋₋ᵢⱼₖₙₜ'))
def _group(tex,i):
 """Return the argument starting at tex[i] (a braced group, command, or character) and the next index."""
 while i<len(tex) and tex[i]==' ':i+=1
 if i>=len(tex):return '',i
 if tex[i]=='{':
  depth=0
  for j in range(i,len(tex)):
   depth+=tex[j]=='{';depth-=tex[j]=='}'
   if not depth:return tex[i+1:j],j+1
 if tex[i]=='\\':
  m=re.match(r'\\[a-zA-Z]+|\\.',tex[i:]);return m.group(),i+len(m.group())
 return tex[i],i+1
def _math(tex):
 out='';i=0
 while i<len(tex):
  c=tex[i]
  if c=='\\':
   m=re.match(r'\\([a-zA-Z]+)|\\(.)',tex[i:]);name=m.group(1) or m.group(2);i+=len(m.group())
   if name in ('ket','bra'):
    a,i=_group(tex,i);a=_math(a);out+=f'|{a}⟩' if name=='ket' else f'⟨{a}|'
   elif name in ('braket','ketbra'):
    a,i=_group(tex,i);b,i=_group(tex,i);a,b=_math(a),_math(b);out+=f'⟨{a}|{b}⟩' if name=='braket' else f'|{a}⟩⟨{b}|'
   elif name in ('sqrt',):
    a,i=_group(tex,i);a=_math(a);out+='√'+(a if re.fullmatch(r'[\w.]+',a) else f'({a})')
   elif name in ('frac','tfrac','dfrac'):
    a,i=_group(tex,i);b,i=_group(tex,i);a,b=_math(a),_math(b)
    out+=(a if re.fullmatch(r'[\w.√]+',a) else f'({a})')+'/'+(b if re.fullmatch(r'[\w.√]+',b) else f'({b})')
   elif name in ('mathrm','operatorname','text','mathsf','mathbf','mathit'):
    a,i=_group(tex,i);out+=_math(a)
   elif name in ('left','right','big','Big',',',';','!','quad','qquad'):
    out+=' ' if name in (',',';','quad','qquad') else ''
   elif name in '{}|%#&_ ':out+=name
   else:out+=SYMBOLS.get(name,name)
  elif c in '^_':
   a,i=_group(tex,i+1);a=_math(a);table=SUPER if c=='^' else SUB
   if a=='∘':out+='°'
   elif a and all(x in table for x in a):out+=''.join(table[x] for x in a)
   else:out+=c+(a if len(a)==1 else f'({a})')
  elif c in '{}':i+=1
  elif c=='-':out+='−';i+=1
  else:out+=c;i+=1
 return out
def plain(value):
 """Replace each \\(...\\) or \\[...\\] span with a Unicode rendering."""
 return MATH.sub(lambda m:_math(m.group(1) if m.group(1) is not None else m.group(2)),str(value))
def svg_text(x,y,value,attrs=''):
 """An SVG text element whose content stays readable Unicode.

 A label that is one TeX span gains data-tex; a label mixing prose and TeX gains
 data-math, which MathJax lays out piecewise so the prose keeps the figure's font.
 """
 value=str(value);whole=MATH.fullmatch(value.strip())
 if whole and value.count('\\(')+value.count('\\[')==1:extra=f' data-tex="{escape(whole.group(1) if whole.group(1) is not None else whole.group(2))}"'
 elif MATH.search(value):extra=f' data-math="{escape(value)}"'
 else:extra=''
 return f'<text x="{x:g}" y="{y:g}"{attrs}{extra}>{escape(plain(value))}</text>'
def wrap(value,width):
 """Wrap prose by its rendered length without splitting a TeX span."""
 result=[]
 for paragraph in str(value).split('\n'):
  words=re.findall(r'(?:\\\(.*?\\\)|\S)+',paragraph);line=''
  for word in words:
   trial=line+' '+word if line else word
   if line and len(plain(trial))>width:result.append(line);line=word
   else:line=trial
  result.append(line)
 return result
