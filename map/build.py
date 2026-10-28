"""Build the accessible topic directory and graph data: python3 map/build.py."""
import json
from pathlib import Path
from html import escape
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'education'))
from site_navigation import site_navigation
from site_logo import site_logo
from asset_versions import version_assets
# Each branch contains subfields and their child keywords. IDs are stable slugs.
BRANCHES = {
'Quantum mechanics': {
'Mathematical foundations': 'Hilbert space|State vectors|Dirac notation|Inner product|Tensor product|Linear operators|Eigenvalues and eigenvectors|Spectral theorem|Commutators|Unitary operators|Hermitian operators|Projectors',
'Quantum states': 'Wavefunction|Superposition|Probability amplitudes|Born rule|Pure states|Mixed states|Density operator|Bloch sphere|Coherence|State preparation',
'Dynamics': 'Schrödinger equation|Time evolution|Hamiltonian|Heisenberg picture|Schrödinger picture|Interaction picture|Propagators|Path integrals|Adiabatic theorem|Berry phase|Quantum speed limits',
'Measurement': 'Observables|Projective measurement|POVMs|Measurement backaction|Weak measurement|Continuous measurement|Uncertainty relations|Compatible observables|Quantum instruments',
'Canonical systems': 'Particle in a box|Quantum harmonic oscillator|Hydrogen atom|Potential barriers|Quantum tunneling|Angular momentum|Spin|Addition of angular momenta|Identical particles|Bosons|Fermions|Pauli exclusion principle',
'Approximation methods': 'Perturbation theory|Variational principle|WKB approximation|Scattering theory|Born approximation|Fermi’s golden rule',
'Foundations and interpretations': 'Measurement problem|EPR paradox|Bell inequalities|Contextuality|Kochen–Specker theorem|Copenhagen interpretation|Many-worlds interpretation|Bohmian mechanics|Objective collapse|Quantum Bayesianism|Decoherence|Classical limit'
},
'Quantum computing': {
'Computational models': 'Qubits|Qudits|Quantum circuits|Universal gate sets|Reversible computation|Measurement-based computation|Adiabatic quantum computing|Topological quantum computing|Analog quantum computing',
'Quantum gates': 'Pauli gates|Hadamard gate|Phase gate|T gate|Rotation gates|Controlled-NOT gate|Controlled-Z gate|SWAP gate|Toffoli gate|Controlled unitaries',
'Quantum algorithms': 'Quantum Fourier transform|Phase estimation|Shor’s algorithm|Grover’s algorithm|Amplitude amplification|Amplitude estimation|Quantum walks|Hamiltonian simulation|Quantum signal processing|Quantum singular value transformation|HHL algorithm|Deutsch–Jozsa algorithm|Simon’s algorithm',
'Hybrid algorithms': 'Variational quantum eigensolver|Quantum approximate optimization algorithm|Variational quantum circuits|Parameter-shift rule|Barren plateaus|Quantum machine learning|Quantum kernels|Quantum neural networks',
'Complexity theory': 'BQP|QMA|Quantum query complexity|Quantum communication complexity|Quantum advantage|Quantum supremacy|Classical simulation|Stabilizer simulation|Tensor-network simulation',
'Error correction': 'Quantum error-correcting codes|Stabilizer codes|CSS codes|Surface codes|Toric code|Color codes|Quantum LDPC codes|Subsystem codes|Bosonic codes|GKP codes|Cat codes|Syndrome measurement|Logical qubits|Decoding',
'Fault tolerance': 'Threshold theorem|Fault-tolerant gates|Transversal gates|Magic-state distillation|Lattice surgery|Code switching|Quantum error mitigation|Zero-noise extrapolation|Probabilistic error cancellation',
'Programming and compilation': 'Quantum programming languages|Circuit synthesis|Gate decomposition|Qubit routing|Circuit optimization|Resource estimation|Dynamic circuits|Quantum intermediate representations|Quantum verification'
},
'Quantum information': {
'Information measures': 'Von Neumann entropy|Quantum relative entropy|Quantum mutual information|Conditional quantum entropy|Rényi entropies|Min-entropy|Max-entropy|Fidelity|Trace distance|Purity',
'Entanglement': 'Bipartite entanglement|Multipartite entanglement|Bell states|GHZ states|W states|Schmidt decomposition|Entanglement entropy|Entanglement witnesses|Entanglement measures|Entanglement distillation|Entanglement dilution|Bound entanglement|Monogamy of entanglement',
'Quantum channels': 'Completely positive maps|Trace-preserving maps|Kraus operators|Stinespring dilation|Choi–Jamiołkowski isomorphism|Depolarizing channel|Dephasing channel|Amplitude damping|Quantum channel capacity|Coherent information|Entanglement-breaking channels',
'Information protocols': 'Quantum teleportation|Superdense coding|Entanglement swapping|State merging|Quantum state discrimination|Quantum compression|No-cloning theorem|No-broadcasting theorem|No-signalling principle',
'Resource theories': 'Local operations and classical communication|Entanglement as a resource|Coherence as a resource|Magic states|Asymmetry|Quantum thermodynamic resources',
'Characterization': 'Quantum state tomography|Quantum process tomography|Gate-set tomography|Randomized benchmarking|Classical shadows|Quantum certification|Device-independent certification'
},
'Quantum communication': {
'Quantum cryptography': 'Quantum key distribution|BB84 protocol|E91 protocol|Decoy-state protocols|Device-independent QKD|Measurement-device-independent QKD|Continuous-variable QKD|Quantum randomness|Quantum digital signatures|Quantum secret sharing|Blind quantum computing',
'Quantum networks': 'Quantum internet|Quantum repeaters|Entanglement distribution|Quantum memories|Quantum transduction|Photonic interconnects|Network routing|Distributed quantum computing',
'Communication platforms': 'Optical fiber links|Free-space quantum links|Satellite quantum communication|Single-photon sources|Single-photon detectors|Quantum frequency conversion'
},
'Quantum matter and fields': {
'Many-body physics': 'Second quantization|Fock space|Creation and annihilation operators|Bose–Einstein condensation|Fermi gases|Hubbard model|Ising model|Heisenberg model|Quantum phase transitions|Quantum criticality|Many-body localization|Eigenstate thermalization',
'Condensed matter': 'Band theory|Bloch theorem|Superconductivity|Cooper pairs|BCS theory|Josephson effect|Quantum Hall effect|Topological insulators|Topological order|Anyons|Majorana zero modes|Spin liquids',
'Quantum field theory': 'Quantum fields|Canonical quantization|Path-integral quantization|Feynman diagrams|Renormalization|Gauge symmetry|Quantum electrodynamics|Quantum chromodynamics|Standard Model|Vacuum fluctuations|Casimir effect',
'Quantum gravity': 'Semiclassical gravity|Hawking radiation|Black-hole information problem|Holographic principle|AdS/CFT correspondence|Loop quantum gravity|String theory',
'Quantum chemistry': 'Electronic structure|Molecular orbitals|Hartree–Fock method|Density functional theory|Configuration interaction|Coupled cluster|Born–Oppenheimer approximation'
},
'Quantum technology': {
'Hardware platforms': 'Superconducting qubits|Trapped-ion qubits|Neutral-atom qubits|Rydberg atoms|Photonic qubits|Semiconductor spin qubits|Quantum dots|Diamond NV centers|Topological qubits',
'Quantum optics': 'Photons|Coherent states|Squeezed states|Fock states|Beam splitters|Optical interferometry|Hong–Ou–Mandel effect|Spontaneous parametric down-conversion|Cavity QED|Circuit QED|Optomechanics',
'Quantum sensing': 'Quantum metrology|Quantum Fisher information|Quantum Cramér–Rao bound|Standard quantum limit|Heisenberg limit|Atomic clocks|Quantum magnetometry|Quantum gravimetry|Spin squeezing|Quantum imaging',
'Open quantum systems': 'System–environment coupling|Master equations|Lindblad equation|Markovian dynamics|Non-Markovian dynamics|Quantum trajectories|Dissipation|Dephasing|Relaxation|Dynamical decoupling',
'Quantum control': 'Coherent control|Optimal control|Pulse shaping|Feedback control|Laser cooling|Sideband cooling|Reservoir engineering',
'Quantum thermodynamics': 'Quantum heat engines|Quantum work|Fluctuation theorems|Thermal states|Thermalization|Landauer principle|Quantum batteries'
}}
DESCRIPTIONS = {
'Quantum world': 'Explore the language of quantum science, from its mathematical foundations to the technologies built on them.',
'Quantum mechanics': 'The framework for describing physical states, measurement, and dynamics at quantum scales.',
'Quantum computing': 'Processing information using quantum states, gates, algorithms, and error-corrected hardware.',
'Quantum information': 'The structure, quantification, and transformation of information carried by quantum systems.',
'Quantum communication': 'Transmitting quantum states and using quantum correlations for communication and cryptography.',
'Quantum matter and fields': 'Quantum descriptions of particles, materials, molecules, fields, and gravity.',
'Quantum technology': 'Platforms and methods for controlling quantum systems and using them to compute, communicate, and sense.'}
COURSES = {'Quantum mechanics': 'foundations', 'Quantum computing': 'computing', 'Quantum information': 'information', 'Quantum communication': 'cryptography', 'Quantum technology': 'hardware'}
import re

def slug(label):
    return re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')

nodes = []
def add(label, parent, branch):
    nodes.append(dict(id=slug(label), label=label, parent=slug(parent) if parent else None, branch=branch, description=DESCRIPTIONS.get(label, f'{label} is included under {parent} in this topic hierarchy.')))
add('Quantum world', None, 'Quantum world')
for branch, groups in BRANCHES.items():
    add(branch, 'Quantum world', branch)
    for group, terms in groups.items():
        add(group, branch, branch)
        for term in terms.split('|'):
            add(term, group, branch)
assert len({n['id'] for n in nodes}) == len(nodes)
(ROOT / 'map/topics.json').write_text(json.dumps(nodes, ensure_ascii=False, indent=2) + '\n')
directory = ''
for branch, groups in BRANCHES.items():
    directory += f'<details><summary>{escape(branch)}</summary>'
    for group, terms in groups.items():
        directory += f'<details><summary>{escape(group)}</summary><ul>'
        for term in terms.split('|'):
            directory += f'<li><a href="#{slug(term)}" data-topic="{slug(term)}">{escape(term)}</a></li>'
        directory += '</ul></details>'
    directory += '</details>'
html = (ROOT / 'map/template.html.in').read_text().replace('<!-- NAV -->', site_logo('news-brand', '../index.html') + site_navigation('map/index.html')).replace('<!-- DIRECTORY -->', directory).replace('<!-- DATA -->', '<script id="topic-data" type="application/json">' + json.dumps(nodes, ensure_ascii=False) + '</script>')
(ROOT / 'map/index.html').write_text('<!-- Generated by map/build.py; edit template.html and build.py. -->\n' + version_assets(html, ROOT / 'map'))
print(f'Built map with {len(nodes)} topics and {len(nodes)-1} parent–child links.')
