"""Inject concise 1-5 word concept asides beside chapter paragraphs and refine illustration guides."""
import re
from bs4 import BeautifulSoup

MATH_RE = re.compile(r'\\\((.*?)\\\)|\\\[(.*?)\\\]', re.S)

# Replace specific TeX commands with readable concept tokens when matching paragraph topics.
TEX_HINTS = (
    (r'\\ketbra\{0\}\{0\}', ' computational basis projector '),
    (r'\\ketbra\{\+\}\{\+\}', ' superposition projector '),
    (r'\\tr\b|\\operatorname\{tr\}', ' matrix trace '),
    (r'\\\|[^\\]+\\\|_1', ' trace norm '),
    (r'\\\|[^\\]+\\\|_\\infty', ' operator norm '),
    (r'\\\|[^\\]+\\\|_\\diamond', ' diamond norm '),
    (r'\\mathcal\s*N|\\Phi\b|\\Lambda\b', ' quantum channel '),
    (r'\\prec\b', ' majorization '),
    (r'\\otimes\b', ' tensor product '),
    (r'\\dagger\b', ' Hermitian adjoint '),
)

# Prioritized domain lexicon: (regex pattern in normalized text, 2-4 word formal concept label).
DOMAIN_CONCEPTS = [
    (r'\baxioms?\b.*\brules of inference\b|\brules of inference\b', 'Axioms & inference rules'),
    (r'\bcreative exploration\b.*\bchecking an existing proof\b|\bchecking an existing proof\b', 'Proof search vs. checking'),
    (r'\bfoundational bridge to computation\b|\binspect symbol by symbol\b', 'Mechanical proof verification'),
    (r'\bcontradiction\b.*\bconsistent\b|\bprove both\b.*\bconsistent\b', 'Formal consistency'),
    (r'\bfinitary methods?\b', 'Hilbert finitary methods'),
    (r'\bhilbert.?s program\b', 'Hilbert’s program'),
    (r'\brejects the argument\b|\bsupplied argument is valid\b', 'Validity vs. provability'),
    (r'\bproof search\b', 'Exhaustive proof search'),
    (r'\bdecision procedure\b.*\bdecision problem\b|\bdecision procedure\b', 'Decision procedures'),
    (r'\bdefinition of what an .?algorithm.? actually is\b|\bmodels of computation\b', 'Formalizing algorithms'),
    (r'\beuclid.?s algorithm\b.*\bgreatest common divisor\b', 'Euclid’s division algorithm'),
    (r'\bwhy is the final answer correct\b.*\bwhy must the procedure eventually stop\b', 'Correctness & termination'),
    (r'\binvariant\b.*\bcommon divisors\b|\bgreatest common divisor is an invariant\b', 'Loop invariant correctness'),
    (r'\bstrictly decreasing sequence of non-?negative integers\b', 'Termination via descent'),
    (r'\bseparate arguments\b.*\bcorrectness\b.*\btermination\b', 'Correctness vs. termination'),
    (r'\bpausing a computation\b|\bminimum information you would need to record\b', 'State needed to resume'),
    (r'\bsnapshot of a computational process is called its configuration\b|\bconfiguration\b.*\binstruction counter\b', 'Machine configuration'),
    (r'\bupdates one configuration into the next is called a transition\b', 'Configuration transitions'),
    (r'\bentire sequence is called a run\b', 'Deterministic execution run'),
    (r'\bforward step is deterministic, but it is not reversible\b|\bwhere you came from\b', 'Irreversible state merging'),
    (r'\birreducible physical operations\b|\bhigh-level commands\b', 'Atomic computation steps'),
    (r'\bturing formalized\b|\bturing machine strips computing\b', 'Turing machine components'),
    (r'\bhalting state\b.*\bconfiguration of a turing machine\b', 'Turing halting configuration'),
    (r'\buniversal machine\b|\bimitate its behavior step by step\b', 'Universal Turing machine'),
    (r'\bunifies hardware and software\b|\bcode is simply data\b', 'Programs as data'),
    (r'\blambda calculus\b.*\brecursive functions\b', 'Lambda & recursive models'),
    (r'\bevery one of these formal models turns out to compute\b|\bsimulated step by step on a turing machine\b', 'Equivalence of formal models'),
    (r'\bchurch.?turing thesis\b.*\beffective mechanical method\b', 'Church–Turing thesis'),
    (r'\bstatement about computability\b.*\befficiency\b', 'Computability vs. efficiency'),
    (r'\bnot halted yet\b|\bdetermine in advance whether the run will eventually stop\b', 'Predicting program termination'),
    (r'\buniversal halting decider\b|\bcall it h\(p,\s*x\)\b', 'Assumed halting decider'),
    (r'\badversarial program\b.*\bexact opposite\b', 'Adversarial diagonal program'),
    (r'\bfeed d as the input to d\b|\bvalid program with its own finite text description\b', 'Self-referential input'),
    (r'\bundecidability of the halting problem\b', 'Halting undecidability'),
    (r'\bscope of this theorem\b|\bautomated verification tools\b', 'Scope of undecidability'),
    (r'\bundecidable problem\b.*\bincomplete theory\b', 'Undecidability vs. incompleteness'),
    (r'\benumerating candidate proofs\b.*\bcomplete and consistent axiom system\b', 'Completeness implies decidability'),
    (r'\bgödel.?rosser theorem\b', 'Gödel–Rosser theorem'),
    (r'\badding the undecided sentence\b.*\bnew axiom\b', 'Inexhaustible incompleteness'),
    (r'\bsecond incompleteness theorem\b', 'Second incompleteness theorem'),
    (r'\bone-to-one\b.*\blogical reversibility\b|\blogical reversibility\b', 'Logical reversibility'),
    (r'\bbijection\b.*\bunique predecessor\b', 'Bijective state transitions'),
    (r'\bmany-to-one\b.*\band operation\b', 'Many-to-one information loss'),
    (r'\bretain the input alongside the output\b|\bforming the pair\b', 'Reversible input embedding'),
    (r'\blandauer.?s principle\b|\bk_b\s*t\s*\\ln\s*2\b', 'Landauer erasure bound'),
    (r'\btoffoli gate\b|\bcontrolled-controlled-not\b', 'Toffoli gate universality'),
    (r'\bfredkin gate\b|\bcontrolled-swap\b', 'Fredkin controlled-SWAP'),
    (r'\buncomput(?:e|ing|ation)\b|\bgarbage bits?\b', 'Workspace uncomputation'),
    (r'\bboolean polynomial\b|\bfinite field\b|\bmodulo\s*2\b.*\bpolynomial\b', 'Algebraic normal form'),
    (r'\btruth table\b.*\bboolean function\b', 'Boolean truth tables'),
    (r'\bnand\b.*\buniversal\b|\buniversal gate\b', 'Universal gate sets'),
    (r'\bstochastic matrix\b|\bcolumn-stochastic\b|\bmarkov\b', 'Stochastic transition matrix'),
    (r'\bprobability amplitudes?\b', 'Probability amplitudes'),
    (r'\bdestructive interference\b|\bcancel(?:s|ling|lation)?\b.*\bpath', 'Destructive path interference'),
    (r'\bconstructive interference\b', 'Constructive interference'),
    (r'\bborn(?:\'s|s)? (?:probability )?rule\b|\bsquared magnitude\b', 'Born probability rule'),
    (r'\bglobal phase\b.*\brelative phase\b|\brelative phase\b', 'Relative vs. global phase'),
    (r'\binner product\b|\borthonormal basis\b', 'Inner product & orthogonality'),
    (r'\bunitary(?: matrix| operator| evolution)?\b', 'Unitary state evolution'),
    (r'\bhermitian adjoint\b|\bconjugate transpose\b', 'Hermitian adjoint'),
    (r'\bprojective measurement\b|\bpost-measurement\b', 'Projective state update'),
    (r'\bhadamard gate\b', 'Hadamard superposition gate'),
    (r'\bpauli\b.*\b(?:matrices|operators|gates)\b', 'Pauli operator algebra'),
    (r'\bbloch sphere\b|\bbloch vector\b|\bbloch ball\b', 'Bloch sphere geometry'),
    (r'\btensor product\b|\bcomposite system\b', 'Composite tensor product'),
    (r'\bbell state\b|\bbell pair\b|\bmaximally entangled\b', 'Bell-pair entanglement'),
    (r'\bproduct state\b.*\bentangled\b|\bfactor(?:ize|ed|able)?\b.*\bproduct\b', 'Separability vs. entanglement'),
    (r'\bno-cloning theorem\b|\bclone an unknown\b', 'No-cloning theorem'),
    (r'\bno-signalling\b|\bmarginal distribution\b.*\blocal\b', 'No-signalling principle'),
    (r'\bquantum teleportation\b|\bclassical two-bit\b.*\bteleport', 'Quantum teleportation'),
    (r'\bsuperdense coding\b|\bdense coding\b', 'Superdense coding'),
    (r'\bphase kickback\b', 'Phase kickback mechanism'),
    (r'\bphase oracle\b|\bstandard bit oracle\b', 'Quantum query oracles'),
    (r'\bdeutsch.?s algorithm\b', 'Deutsch’s parity test'),
    (r'\bdeutsch.?jozsa\b', 'Deutsch–Jozsa algorithm'),
    (r'\bbernstein.?vazirani\b', 'Bernstein–Vazirani hidden string'),
    (r'\bsimon.?s (?:algorithm|problem|period)\b', 'Simon’s period finding'),
    (r'\bquantum fourier transform\b|\bqft\b', 'Quantum Fourier transform'),
    (r'\bphase estimation\b', 'Quantum phase estimation'),
    (r'\bshor.?s (?:algorithm|factoring)\b|\border-finding\b', 'Order finding & factoring'),
    (r'\bgrover(?:\'s)? (?:iteration|search|diffusion|algorithm)\b', 'Grover search iteration'),
    (r'\bamplitude amplification\b', 'Amplitude amplification'),
    (r'\bamplitude estimation\b', 'Quantum amplitude estimation'),
    (r'\bquantum walk\b|\bcoined walk\b|\bszegedy\b', 'Quantum walk dynamics'),
    (r'\bblock encoding\b|\blinear combination of unitaries\b|\blcu\b', 'Block encoding & LCU'),
    (r'\bquantum signal processing\b|\bqsp\b|\bqubitization\b', 'Quantum signal processing'),
    (r'\bqsvt\b|\bsingular value transformation\b', 'Singular value transformation'),
    (r'\btrotter\b|\blie.?trotter\b|\bproduct formula\b', 'Trotter Hamiltonian simulation'),
    (r'\bvariational quantum eigensolver\b|\bvqe\b|\bvariational ansatz\b', 'Variational ansatz optimization'),
    (r'\bqaoa\b|\bapproximate optimization\b', 'Quantum approximate optimization'),
    (r'\bbarren plateau\b|\bvanishing gradient\b', 'Barren plateau gradients'),
    (r'\bparameter-shift rule\b', 'Parameter-shift gradient'),
    (r'\bquantum kernel\b|\bfeature map\b|\breproducing kernel\b', 'Quantum kernel mapping'),
    (r'\bdata encoding\b|\bamplitude encoding\b|\bangle encoding\b', 'Quantum data encoding'),
    (r'\brademacher\b|\bcovering number\b|\bgeneralization bound\b', 'Generalization error bounds'),
    (r'\bdequantiz(?:ed|ation)\b|\bsample-based classical\b', 'Classical dequantization baseline'),
    (r'\bquery complexity\b|\badversary bound\b|\bpolynomial method\b', 'Query complexity bounds'),
    (r'\bbqp\b.*\bbpp\b|\bcomplexity class(?:es)?\b', 'Computational complexity classes'),
    (r'\bcomputational basis\b.*\bambiguity\b', 'Computational-basis test'),
    (r'\bconditional on outcome\b|\bdecision rule should therefore guess\b', 'Maximum-posterior guessing'),
    (r'\boptimize over every allowed quantum decision\b|\bnothing in the calculation shows that it is optimal\b', 'Optimality vs. single strategy'),
    (r'\bprior probabilities\b', 'Prior hypothesis probabilities'),
    (r'\bmeasurement effect\b.*\bi-m\b|\bgrouping all outcomes\b.*\beffect\b', 'Two-outcome measurement effects'),
    (r'\boperator inequalities\b|\bpositive semidefinite\b.*\beigenvalue\b', 'POVM positivity constraints'),
    (r'\bblindly guessing\b|\badvantage added by the measurement\b', 'Linear trace objective'),
    (r'\borthonormal eigenbasis\b.*\bexpanding the trace\b', 'Spectral trace expansion'),
    (r'\bdiagonal expectation value obeys\b|\bmaximize the sum by setting\b', 'Eigenvalue upper bound'),
    (r'\borthogonal projector onto the positive-eigenvalue subspace\b', 'Positive-eigenspace projector'),
    (r'\bdiagonal entries in the eigenbasis\b.*\bglobal optimum\b', 'Attaining the spectral bound'),
    (r'\bhelstrom bound\b', 'Helstrom minimum-error bound'),
    (r'\bsum of its singular values\b.*\boperator norm\b', 'Trace vs. operator norm'),
    (r'\btrace distance\b', 'Trace distance definition'),
    (r'\bnormalizes\b.*\badvantage over random guessing\b', 'Operational meaning of T'),
    (r'\bsquaring d\b|\bresolve our opening qubit question\b', 'Qubit difference spectrum'),
    (r'\bhelstrom basis straddles\b|\bpositive eigenvector of d\b', 'Optimal tilted eigenbasis'),
    (r'\bresidual error\b|\bsacrifices certainty\b', 'Fundamental non-orthogonality limit'),
    (r'\bpass the supplied state through a noisy device\b', 'Processing before measurement'),
    (r'\bcomposite procedure\b.*\bcontractivity\b', 'Channel contractivity'),
    (r'\bhilbert.?schmidt adjoint\b|\bunital\b', 'Heisenberg adjoint pullback'),
    (r'\bpostselect\b|\bheralding outcome\b', 'Postselection vs. trace preservation'),
    (r'\buhlmann fidelity\b|\bextending this overlap test\b', 'Uhlmann state fidelity'),
    (r'\bunique positive semidefinite square root\b', 'Operator square root'),
    (r'\bsquared fidelity\b', 'Squared fidelity convention'),
    (r'\b2\\times 2\b.*\btrace\b.*\bdeterminant\b|\bpure-state\b.*\btrace distance\b', 'Pure-state distance identity'),
    (r'\bfuchs.?van de graaf\b', 'Fuchs–van de Graaf bounds'),
    (r'\bworst-case distinguishability guarantees\b|\brange between t and\b', 'Error-budget square root'),
    (r'\bmaximally mixed qubit\b|\bpure-state equality fails\b', 'Mixed-state fidelity gap'),
    (r'\bfidelity obeys a data-processing inequality\b', 'Monotonicity of fidelity'),
    (r'\bmissed signal\b.*\bfalse alarm\b|\btype i\b.*\btype ii\b', 'Type I & II errors'),
    (r'\bexternally specified tolerance\b|\bminimizes the false-alarm probability\b', 'Constrained error optimization'),
    (r'\btwo-outcome commuting example\b|\bshared eigenbasis\b', 'Commuting test reduction'),
    (r'\bat tolerance\b.*\bfalse-alarm rate\b', 'Threshold acceptance rule'),
    (r'\bneyman.?pearson\b|\bfalse-alarm cost per unit\b|\bprice of signal acceptance\b', 'Neyman–Pearson cost ratio'),
    (r'\bordering outcomes by\b.*\blikelihood ratio\b', 'Likelihood-ratio ordering'),
    (r'\boptimal effect\b.*\bis not a projector\b', 'Randomized boundary effects'),
    (r'\bsemidefinite program\b|\bsdp\b', 'Semidefinite programming (SDP)'),
    (r'\bconvex combination\b.*\bduality\b', 'Randomized tests & SDP duality'),
    (r'\bquantum relative entropy\b', 'Quantum relative entropy'),
    (r'\bcomplete positivity\b|\bcompletely positive\b', 'Complete positivity'),
    (r'\bchoi (?:matrix|state|isomorphism|jamio)\b', 'Choi–Jamiołkowski matrix'),
    (r'\bkraus (?:operators?|representation)\b', 'Kraus operator sum'),
    (r'\bstinespring dilation\b|\bisometric extension\b', 'Stinespring dilation'),
    (r'\bcomplementary channel\b', 'Complementary channel'),
    (r'\bdiamond norm\b|\bcompletely bounded\b', 'Diamond norm distance'),
    (r'\bvon neumann entropy\b', 'Von Neumann entropy'),
    (r'\bshannon entropy\b|\bbinary entropy\b', 'Shannon information entropy'),
    (r'\bstrong subadditivity\b|\bssa\b', 'Strong subadditivity'),
    (r'\bmutual information\b', 'Quantum mutual information'),
    (r'\bconditional entropy\b', 'Conditional quantum entropy'),
    (r'\bquantum stein.?s lemma\b|\bchernoff\b', 'Asymptotic error exponents'),
    (r'\blocc\b|\blocal operations and classical communication\b', 'LOCC protocol class'),
    (r'\bnielsen.?s theorem\b|\bmajorization\b', 'Majorization & LOCC conversion'),
    (r'\bentanglement distillation\b|\bentanglement dilution\b', 'Entanglement distillation'),
    (r'\bschumacher compression\b|\btypical subspace\b|\btypicality\b', 'Typical subspace compression'),
    (r'\bholevo (?:bound|quantity|information|chi)\b', 'Holevo capacity bound'),
    (r'\bcoherent information\b|\blloyd.?shor.?devetak\b', 'Coherent information capacity'),
    (r'\berasure channel\b|\bdegradable channel\b', 'Erasure channel capacity'),
    (r'\bpetz recovery\b|\brecovery map\b', 'Petz recovery channel'),
    (r'\bresource theory\b|\bfree states?\b.*\bfree operations?\b', 'Quantum resource monotones'),
    (r'\bknill.?laflamme\b|\bcorrectable errors?\b', 'Knill–Laflamme conditions'),
    (r'\bstabilizer (?:code|group|formalism|generator)\b', 'Stabilizer code formalism'),
    (r'\bcss code\b|\bcalderbank.?shor.?steane\b|\bsteane code\b|\bshor code\b', 'CSS code construction'),
    (r'\blogical (?:operator|pauli|qubit)\b|\bnormalizer\b|\bcentralizer\b', 'Logical Pauli operators'),
    (r'\bsyndrome (?:extraction|measurement|decoding)\b|\berror syndrome\b', 'Syndrome extraction & decoding'),
    (r'\bsurface code\b|\btoric code\b|\bplaquette\b|\bstar operator\b', 'Surface code topology'),
    (r'\btransversal gate\b|\beastin.?knill\b', 'Transversal fault-tolerant gates'),
    (r'\bmagic state distillation\b', 'Magic state distillation'),
    (r'\bthreshold theorem\b|\bfault-tolerant threshold\b', 'Fault-tolerance threshold'),
    (r'\bbb84\b|\bsifted key\b|\bbasis sifting\b', 'BB84 basis sifting'),
    (r'\berror reconciliation\b|\binformation reconciliation\b', 'Information reconciliation'),
    (r'\bprivacy amplification\b|\btwo-universal hash\b|\btoeplitz\b|\bleftover hash\b', 'Privacy amplification hashing'),
    (r'\bmin-entropy\b|\bsmooth min-entropy\b', 'Conditional min-entropy'),
    (r'\bdecoy-?state\b|\bphoton-number splitting\b', 'Decoy-state security'),
    (r'\bdevice-independent\b|\bchsh\b|\bbell inequality\b', 'Bell inequality violation'),
    (r'\bbit commitment\b|\bmayers.?lo.?chau\b', 'No-go for bit commitment'),
    (r'\banharmonicity\b|\btransmon\b|\bjosephson junction\b', 'Transmon anharmonicity'),
    (r'\brabi oscillation\b|\brabi frequency\b|\bdetuning\b', 'Driven Rabi oscillations'),
    (r'\bt_1\b|\brelaxation time\b|\bamplitude damping\b', 'Energy relaxation (T₁)'),
    (r'\bt_2\b|\bdephasing\b|\bhahn echo\b|\bramsey\b', 'Phase coherence & echo (T₂)'),
    (r'\bdispersive readout\b|\bquantum nondemolition\b|\bqnd\b', 'Dispersive QND readout'),
    (r'\blamb.?dicke\b|\bmotional sideband\b|\bmølmer.?sørensen\b', 'Ion motional sidebands'),
    (r'\brydberg blockade\b|\boptical tweezer\b', 'Rydberg dipole blockade'),
    (r'\bpauli spin blockade\b|\bexchange interaction\b|\bdouble quantum dot\b', 'Spin exchange blockade'),
    (r'\bnitrogen-vacancy\b|\bnv center\b|\bzero-phonon line\b', 'Defect-center spin optics'),
    (r'\bhong.?ou.?mandel\b|\bdual-rail\b|\blinear optical\b', 'Photonic mode interference'),
    (r'\bcat code\b|\bgkp\b|\bbinomial code\b|\bbosonic\b', 'Bosonic cavity encoding'),
    (r'\bmajorana zero mode\b|\bnon-abelian braiding\b', 'Topological Majorana braiding'),
    (r'\bcryogenic\b|\bdilution refrigerator\b|\bthermal load\b', 'Cryogenic wiring budget'),
    (r'\brandomized benchmarking\b|\bgate-set tomography\b', 'Randomized benchmarking'),
    (r'\bqiskit\b|\bquantumcircuit\b|\btranspil(?:e|er|ation)\b', 'Circuit compilation & layout'),
    (r'\bshot noise\b|\bstandard error\b|\bbinomial fluctuation\b', 'Finite-sample shot noise'),
    (r'\bcontextuality\b|\bkochen.?specker\b|\bperes.?mermin\b', 'Quantum contextuality'),
    (r'\bdecoherence\b|\bpointer basis\b|\beinselection\b', 'Environment-induced decoherence'),
    (r'\beverett\b|\bmany-worlds\b|\brelative state\b', 'Everett relative-state branches'),
    (r'\bbohmian\b|\bpilot-wave\b|\bguidance equation\b', 'Bohmian guidance dynamics'),
    (r'\bgrw\b|\bobjective collapse\b|\bcsl\b', 'Objective collapse models'),
    (r'\bqbism\b|\brelational quantum mechanics\b', 'Observer-relative states'),
    (r'\bwigner.?s friend\b|\bfrauchiger.?renner\b', 'Extended Wigner’s friend'),
    (r'\bpusey.?barrett.?rudolph\b|\bpbr theorem\b|\bontic\b.*\bepistemic\b', 'Ontic vs. epistemic states'),
    (r'\bgleason.?s theorem\b|\bframe function\b', 'Gleason probability theorem'),
    (r'\blocal tomography\b|\btomographic locality\b', 'Tomographic locality'),
    (r'\bpurification principle\b|\bpurification\b', 'State purification'),
    (r'\bleakage\b.*\bencoding\b|\bencoding\b.*\bleakage\b', 'Qubit encoding & leakage'),
    (r'\bmatrix exponential\b|\bschrödinger evolution\b', 'Unitary Hamiltonian generator'),
]

STOPWORDS = {
    'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from',
    'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'can', 'cannot', 'could', 'will', 'would', 'shall', 'should', 'may',
    'might', 'must', 'that', 'this', 'these', 'those', 'it', 'its', 'they', 'them',
    'their', 'we', 'us', 'our', 'you', 'your', 'he', 'she', 'his', 'her', 'who',
    'whom', 'which', 'what', 'where', 'when', 'why', 'how', 'if', 'then', 'else',
    'than', 'so', 'such', 'no', 'not', 'nor', 'only', 'also', 'very', 'too', 'just',
    'now', 'here', 'there', 'up', 'down', 'out', 'into', 'over', 'under', 'again',
    'further', 'once', 'each', 'every', 'all', 'any', 'both', 'few', 'more', 'most',
    'other', 'some', 'many', 'much', 'own', 'same', 'another', 'one', 'two', 'three',
    'first', 'second', 'third', 'new', 'old', 'good', 'bad', 'great', 'small',
    'large', 'long', 'short', 'high', 'low', 'next', 'last', 'early', 'late',
    'let', 'suppose', 'consider', 'imagine', 'take', 'write', 'choose', 'define',
    'replace', 'notice', 'recall', 'compare', 'look', 'ask', 'begin', 'start',
    'continue', 'think', 'see', 'show', 'prove', 'check', 'find', 'use', 'make',
    'give', 'gives', 'given', 'called', 'known', 'means', 'mean', 'way', 'task',
    'example', 'problem', 'question', 'answer', 'result', 'case', 'step', 'steps',
    'part', 'form', 'value', 'values', 'number', 'numbers', 'set', 'sets', 'line',
    'lines', 'point', 'points', 'side', 'sides', 'hand', 'time', 'times', 'order',
    'fact', 'reason', 'idea', 'view', 'sense', 'kind', 'sort', 'type', 'types',
    'and', 'or', 'but', 'yet', 'because', 'since', 'while', 'although', 'though',
    'however', 'therefore', 'thus', 'hence', 'consequently', 'instead', 'otherwise',
    'moreover', 'furthermore', 'nevertheless', 'nonetheless', 'meanwhile', 'firstly',
    'whether', 'either', 'neither', 'between', 'among', 'within', 'without', 'across',
    'through', 'during', 'before', 'after', 'above', 'below', 'under', 'over',
    'turn', 'turns', 'turned', 'keep', 'keeps', 'kept', 'hold', 'holds', 'held',
    'need', 'needs', 'needed', 'want', 'wants', 'wanted', 'allow', 'allows', 'allowed',
    'requires', 'require', 'required', 'gives', 'gave', 'taken', 'takes', 'took',
    'like', 'unlike', 'even', 'still', 'already', 'always', 'never', 'often',
}

TECHNICAL_HEAD_NOUNS = {
    'state', 'states', 'operator', 'operators', 'matrix', 'matrices', 'norm', 'norms',
    'distance', 'fidelity', 'entropy', 'channel', 'channels', 'measurement',
    'measurements', 'effect', 'effects', 'projector', 'projectors', 'basis', 'bases',
    'subspace', 'eigenvalue', 'eigenvalues', 'eigenvector', 'eigenvectors', 'spectrum',
    'amplitude', 'amplitudes', 'phase', 'phases', 'interference', 'probability',
    'probabilities', 'distribution', 'distributions', 'bound', 'bounds', 'inequality',
    'inequalities', 'theorem', 'lemma', 'postulate', 'principle', 'rule', 'rules',
    'axiom', 'axioms', 'proof', 'proofs', 'consistency', 'completeness',
    'incompleteness', 'decidability', 'undecidability', 'computability', 'complexity',
    'algorithm', 'algorithms', 'procedure', 'procedures', 'machine', 'machines',
    'configuration', 'configurations', 'transition', 'transitions', 'reversibility',
    'erasure', 'gate', 'gates', 'circuit', 'circuits', 'oracle', 'oracles', 'query',
    'queries', 'walk', 'walks', 'transform', 'transforms', 'estimation',
    'amplification', 'simulation', 'encoding', 'encodings', 'code', 'codes',
    'syndrome', 'syndromes', 'stabilizer', 'stabilizers', 'decoder', 'decoding',
    'threshold', 'thresholds', 'leakage', 'relaxation', 'dephasing', 'decoherence',
    'coherence', 'resonance', 'detuning', 'blockade', 'coupling', 'hamiltonian',
    'unitary', 'adjoint', 'commutator', 'observable', 'observables', 'contextuality',
    'nonlocality', 'entanglement', 'correlation', 'correlations', 'teleportation',
    'purification', 'dilation', 'isometry', 'positivity', 'program', 'programs',
    'duality', 'convexity', 'invariant', 'invariants', 'termination', 'correctness',
    'bijection', 'polynomial', 'polynomials', 'kernel', 'kernels', 'gradient',
    'gradients', 'ansatz', 'generalization', 'reconciliation', 'hashing', 'key',
    'keys', 'protocol', 'protocols', 'calibration', 'tomography', 'benchmarking',
    'efficiency', 'fluctuation', 'fluctuations', 'variance', 'estimator', 'test',
    'tests', 'hypothesis', 'hypotheses', 'ratio', 'ratios', 'budget', 'overhead',
    'latency', 'throughput', 'routing', 'topology', 'braiding', 'mode', 'modes',
    'photon', 'photons', 'spin', 'spins', 'ion', 'ions', 'transmon', 'junction',
    'cavity', 'resonator', 'oscillator', 'register', 'registers', 'ancilla',
    'workspace', 'garbage', 'reduction', 'reductions', 'capacity', 'capacities',
    'rate', 'rates', 'exponent', 'exponents', 'recovery', 'monotone', 'monotones',
    'resource', 'resources', 'Check', 'checks', 'parity', 'parities', 'lattice',
}

BAD_SINGLE_WORDS = {
    'complete', 'consistent', 'squared', 'optimal', 'halted', 'halting', 'machine',
    'algorithm', 'algorithms', 'undecidable', 'incomplete', 'deterministic',
    'reversible', 'irreversible', 'fidelity', 'entropy', 'channel', 'channels',
    'state', 'states', 'qubit', 'qubits', 'matrix', 'matrices', 'operator',
    'operators', 'vector', 'vectors', 'measurement', 'measurements', 'circuit',
    'circuits', 'function', 'functions', 'system', 'systems', 'process', 'model',
    'models', 'theorem', 'theorems', 'lemma', 'bound', 'bounds', 'rule', 'rules',
    'method', 'methods', 'proof', 'proofs', 'input', 'inputs', 'output', 'outputs',
    'error', 'errors', 'noise', 'signal', 'signals', 'test', 'tests', 'code', 'codes',
}

TECHNICAL_MODIFIERS = {
    'quantum', 'classical', 'unitary', 'hermitian', 'projective', 'computational',
    'orthonormal', 'orthogonal', 'nonorthogonal', 'non-orthogonal', 'reversible',
    'irreversible', 'deterministic', 'stochastic', 'probabilistic', 'coherent',
    'incoherent', 'entangled', 'separable', 'product', 'composite', 'marginal',
    'conditional', 'joint', 'relative', 'global', 'local', 'nonlocal', 'non-local',
    'diagonal', 'spectral', 'eigenvalue', 'eigenvector', 'singular', 'trace',
    'operator', 'matrix', 'vector', 'state', 'channel', 'diamond', 'hilbert',
    'fock', 'bloch', 'pauli', 'hadamard', 'clifford', 'toffoli', 'fredkin',
    'stabilizer', 'syndrome', 'logical', 'physical', 'ancilla', 'ancillary',
    'workspace', 'garbage', 'fault-tolerant', 'transversal', 'topological',
    'surface', 'toric', 'planar', 'concatenated', 'bosonic', 'dispersive',
    'motional', 'sideband', 'cryogenic', 'thermal', 'shot', 'readout', 'control',
    'microwave', 'optical', 'photonic', 'neutral-atom', 'trapped-ion', 'superconducting',
    'transmon', 'josephson', 'rydberg', 'spin', 'exchange', 'majorana', 'cavity',
    'resonator', 'phase', 'amplitude', 'frequency', 'detuning', 'rabi', 'ramsey',
    'hahn', 'relaxation', 'dephasing', 'decoherence', 'damping', 'depolarizing',
    'erasure', 'leakage', 'crosstalk', 'calibration', 'randomized', 'tomographic',
    'interferometric', 'homodyne', 'heterodyne', 'coincidence', 'heralded',
    'postselected', 'post-measurement', 'pre-measurement', 'weak', 'continuous',
    'discrete', 'binary', 'boolean', 'axiomatic', 'formal', 'finitary',
    'mechanical', 'universal', 'halting', 'undecidable', 'decidable', 'computable',
    'uncomputable', 'incompleteness', 'completeness', 'consistency', 'diagonalization',
    'self-referential', 'bijective', 'injective', 'surjective', 'many-to-one',
    'one-to-one', 'polynomial', 'exponential', 'quadratic', 'asymptotic',
    'finite', 'infinite', 'bounded', 'unbounded', 'worst-case', 'average-case',
    'query', 'oracle', 'black-box', 'adversary', 'adversarial', 'parity',
    'period', 'periodic', 'fourier', 'modular', 'hidden', 'subgroup', 'reflection',
    'diffusion', 'walk', 'coined', 'szegedy', 'block', 'linear', 'nonlinear',
    'chebyshev', 'trotter', 'hamiltonian', 'adiabatic', 'variational', 'parameterized',
    'parametrized', 'ansatz', 'cost', 'objective', 'gradient', 'barren', 'kernel',
    'feature', 'generalization', 'empirical', 'rademacher', 'dequantized',
    'pure', 'mixed', 'pure-state', 'mixed-state', 'reduced', 'purified',
    'isometric', 'complete', 'completely', 'positive', 'semidefinite', 'unital',
    'trace-preserving', 'contractivity', 'contractive', 'monotonic', 'data-processing',
    'helstrom', 'uhlmann', 'bures', 'chernoff', 'hoeffding', 'stein', 'neyman-pearson',
    'hypothesis', 'likelihood', 'posterior', 'prior', 'bayesian', 'symmetric',
    'asymmetric', 'commuting', 'noncommuting', 'non-commuting', 'incompatible',
    'compatible', 'contextual', 'noncontextual', 'epistemic', 'ontic', 'ontological',
    'operational', 'relational', 'everettian', 'bohmian', 'pilot-wave', 'pointer',
    'einselected', 'gleason', 'kochen-specker', 'bell', 'chsh', 'ghz', 'werner',
    'teleportation', 'superdense', 'entanglement-assisted', 'one-shot', 'smoothed',
    'min-entropy', 'max-entropy', 'von-neumann', 'shannon', 'renyi', 'rényi',
    'typical', 'schumacher', 'holevo', 'coherent-information', 'degradable',
    'antidegradable', 'complementary', 'petz', 'recovery', 'resource', 'free',
    'monotone', 'catalytic', 'majorization', 'locc', 'distillable', 'bound-entangled',
    'knill-laflamme', 'correctable', 'detectable', 'degenerate', 'nondegenerate',
    'css', 'steane', 'shor', 'gottesman-knill', 'eastin-knill', 'magic', 'magic-state',
    'clifford-hierarchy', 'minimum-weight', 'union-find', 'belief-propagation',
    'threshold', 'sub-threshold', 'logical-error', 'sifted', 'reconciled',
    'privacy-amplified', 'decoy-state', 'device-independent', 'composable',
    'trace-distance', 'epsilon-secure', 'two-universal', 'toeplitz', 'syndrome-based',
    'circuit-level', 'phenomenological', 'code-capacity', 'spacetime', 'lattice-surgery',
    'braiding', 'non-abelian', 'anyonic', 'fermionic', 'gaussian',
    'non-gaussian', 'squeezed', 'cat', 'gkp', 'binomial', 'dual-rail', 'single-photon',
    'spontaneous', 'parametric', 'down-conversion', 'hong-ou-mandel', 'mach-zehnder',
    'stern-gerlach', 'ramsey-zone', 'rydberg-blockade', 'pauli-blockade',
    'turing', 'church-turing', 'gödel', 'euclid', 'landauer', 'deutsch', 'simon',
    'grover', 'markov', 'poisson', 'sub-poissonian', 'super-poissonian', 'antibunching',
    'bunching', 'squeezing', 'quadrature', 'wigner', 'husimi', 'glauber', 'jaynes-cummings',
}


def _clean_tex(text: str) -> str:
    out = text
    for pat, repl in TEX_HINTS:
        out = re.sub(pat, repl, out)
    out = MATH_RE.sub(' ', out)
    return re.sub(r'\s+', ' ', out).strip()


def _valid_concept_phrase(phrase: str, require_head_noun: bool = False, strict_modifiers: bool = False) -> str | None:
    """Validate and normalize a candidate 2-4 word (or specific 1-word) concept phrase."""
    if '?' in phrase or '!' in phrase:
        return None
    cleaned = MATH_RE.sub('', phrase)
    cleaned = re.sub(r'[^\w\s\-–—/’\'₁₂₃₀₊₋]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' -–—/,.')
    if not cleaned:
        return None
    words = cleaned.split()
    while words and words[0].lower().strip("’'") in STOPWORDS:
        words.pop(0)
    while words and words[-1].lower().strip("’'") in STOPWORDS:
        words.pop()
    if not (1 <= len(words) <= 4):
        return None
    if len(words) == 1:
        w = words[0].lower().strip("’'")
        if len(w) < 6 or w in STOPWORDS or w in BAD_SINGLE_WORDS:
            return None
        if strict_modifiers and w not in TECHNICAL_MODIFIERS and w not in TECHNICAL_HEAD_NOUNS:
            return None
    if require_head_noun and words[-1].lower().strip("’'") not in TECHNICAL_HEAD_NOUNS:
        return None
    if strict_modifiers:
        for w in words[:-1]:
            wl = w.lower().strip("’'")
            if wl not in TECHNICAL_MODIFIERS and wl not in TECHNICAL_HEAD_NOUNS:
                return None
        if len(words) >= 2 and words[0].lower() == words[-1].lower():
            return None
    else:
        allowed_mid = {'of', 'and', 'or', 'vs', 'to', 'in', 'for', 'on', 'by'}
        for w in words:
            wl = w.lower().strip("’'")
            if wl in STOPWORDS and wl not in allowed_mid:
                return None
    result = ' '.join(words)
    if len(result) < 5 or len(result) > 36:
        return None
    return result[0].upper() + result[1:]


def extract_paragraph_concept(p_tag, heading_text: str, used_in_section: set) -> str | None:
    """Return a concise 1-4 word (<=5 words) concept label for a paragraph, or None if transitional."""
    if p_tag.get('data-concept'):
        return p_tag['data-concept'].strip()

    raw_text = p_tag.get_text(' ', strip=True)
    # Skip equation continuation fragments starting with a lowercase letter ("where ...", "and ...")
    if raw_text and raw_text[0].islower():
        return None

    norm_text = _clean_tex(raw_text).lower()

    # 1. Check prioritized domain lexicon first (high-precision multi-word technical terms)
    for pattern, label in DOMAIN_CONCEPTS:
        if re.search(pattern, norm_text):
            if label.lower() not in used_in_section:
                used_in_section.add(label.lower())
                return label

    # 2. Check explicitly defined terms in <dfn>, <em>, or <a class="glossary-term">
    em_candidates = []
    for tag in p_tag.select('dfn, em, a.glossary-term'):
        t_raw = tag.get_text(' ', strip=True)
        if '?' in t_raw or len(t_raw.split()) > 4:
            continue
        is_glossary = 'glossary-term' in (tag.get('class') or []) or tag.name == 'dfn'
        cand = _valid_concept_phrase(
            t_raw,
            require_head_noun=not is_glossary and len(t_raw.split()) == 1,
            strict_modifiers=not is_glossary,
        )
        if cand:
            em_candidates.append(cand)
    if len(em_candidates) >= 2 and len(em_candidates[0].split()) <= 2 and len(em_candidates[1].split()) <= 2:
        if em_candidates[0].lower() != em_candidates[1].lower():
            combined = f'{em_candidates[0]} & {em_candidates[1].lower()}'
            if len(combined.split()) <= 5 and combined.lower() not in used_in_section:
                used_in_section.add(combined.lower())
                return combined
    for cand in em_candidates:
        if cand.lower() not in used_in_section:
            used_in_section.add(cand.lower())
            return cand

    # 3. Extract contiguous technical noun phrases ending in a TECHNICAL_HEAD_NOUN
    clean_prose = _clean_tex(raw_text)
    for m in re.finditer(r'\b([A-Za-z\w\-]{3,}(?:\s+[A-Za-z\w\-]{3,}){1,2})\b', clean_prose):
        cand = _valid_concept_phrase(m.group(1), require_head_noun=True, strict_modifiers=True)
        if cand and 2 <= len(cand.split()) <= 3 and cand.lower() not in used_in_section:
            used_in_section.add(cand.lower())
            return cand

    # 4. Fallback to cleaned subsection heading (<= 4 words) if not yet used in this subsection
    h_clean = re.sub(r'^\d+(?:\.\d+)*\s*', '', heading_text.replace('§', '')).strip()
    h_cand = _valid_concept_phrase(' '.join(h_clean.split()[:4]))
    if h_cand and h_cand.lower() not in used_in_section:
        used_in_section.add(h_cand.lower())
        return h_cand
    return None


SKIP_P_CLASSES = {
    'part-label', 'keywords', 'source-note', 'chapter-intro', 'chapter-subtitle',
    'reading-prompt', 'lab-title', 'lab-status', 'lab-caption', 'qe-eyebrow',
    'qe-scene-heading', 'qe-live', 'qe-scroll-hint', 'qe-model-note',
    'chapter-slides', 'chapter-bridge', 'topic-map-hint', 'problem-text',
}
SKIP_SECTION_IDS = {'explore', 'worked', 'practice', 'takeaways', 'sources', 'approach'}


def inject_concept_asides(soup: BeautifulSoup) -> int:
    """Insert <aside class="concept-aside"> before substantive prose paragraphs in chapter sections."""
    inserted = 0
    for sec in soup.select('section.book-section, section.reading-topic'):
        if sec.get('id') in SKIP_SECTION_IDS or 'qe-part' in (sec.get('class') or []):
            continue
        used_in_section = set()
        current_heading = ''
        for h in sec.find_all(['h2', 'h3'], limit=1):
            current_heading = h.get_text(' ', strip=True)
        for el in list(sec.descendants):
            if getattr(el, 'name', None) in ('h2', 'h3'):
                current_heading = el.get_text(' ', strip=True)
                used_in_section.clear()
            elif getattr(el, 'name', None) == 'p':
                if el.find_parent(['aside', 'details', 'figure', 'li', 'blockquote', 'table', 'header']):
                    continue
                parent_classes = set(el.parent.get('class') or []) if el.parent else set()
                if parent_classes & {'exercise', 'worked-answer', 'prediction', 'chapter-opening'}:
                    continue
                p_classes = set(el.get('class') or [])
                if p_classes & SKIP_P_CLASSES:
                    continue
                prev = el.find_previous_sibling()
                if prev and prev.name == 'aside' and 'concept-aside' in (prev.get('class') or []):
                    continue
                prose_only = MATH_RE.sub('', el.get_text(' ', strip=True)).strip()
                if len(prose_only) < 75:
                    continue
                label = extract_paragraph_concept(el, current_heading, used_in_section)
                if not label:
                    continue
                aside = soup.new_tag('aside', attrs={'class': 'concept-aside', 'aria-label': 'Concept'})
                aside.string = label
                el.insert_before(aside)
                inserted += 1
    return inserted


def upgrade_predictions(soup: BeautifulSoup) -> int:
    """Replace 'Predict first' / 'Predict before calculating' headers with concise illustration/setup guides."""
    updated = 0
    for pred in soup.select('.prediction'):
        first_p = pred.find('p')
        if not first_p:
            continue
        strong = first_p.find('strong')
        nxt = pred.find_next_sibling()
        sec = pred.find_parent('section') or soup
        fig = nxt if (nxt and nxt.name == 'figure') else sec.find('figure')
        if strong:
            old_label = strong.get_text(strip=True).lower()
            if any(k in old_label for k in ('predict', 'before calculating', 'think before')):
                strong.string = 'Figure guide.' if fig else 'Scenario to verify.'
                updated += 1
        details = pred.find('details', class_='prediction-answer')
        if details and details.find('summary'):
            details.find('summary').string = 'What to observe' if fig else 'Key mechanism'
    return updated
