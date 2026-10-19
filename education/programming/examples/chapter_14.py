"""Runnable companion for Quantum Programming, Chapter 14."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

theta = Parameter("theta")
qc = QuantumCircuit(2)
qc.ry(theta, 0); qc.cx(0, 1)
H = SparsePauliOp.from_list([("ZZ", -1), ("XX", -1)])
angles = np.linspace(0, np.pi, 101)
energies = StatevectorEstimator().run([(qc, H, angles[:, None])]).result()[0].data.evs
assert np.allclose(energies, -1 - np.sin(angles))
best = int(np.argmin(energies))
assert np.isclose(energies[best], -2)
print("Grid minimum:", angles[best], energies[best])
