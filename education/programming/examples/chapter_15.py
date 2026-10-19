"""Runnable companion for Quantum Programming, Chapter 15."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from scipy.linalg import expm

X = np.array([[0, 1], [1, 0]])
Z = np.diag([1, -1])
errors = []
for steps in (10, 20, 40):
    qc = QuantumCircuit(1)
    for _ in range(steps):
        qc.rz(2/steps, 0)
        qc.rx(2/steps, 0)
    error = np.linalg.norm(Operator(qc).data - expm(-1j*(X+Z)), 2)
    assert error <= 1/steps + 1e-12
    errors.append(error)
# An LCU encoding of (I+X)/2: ancilla q1, system q0.
lcu = QuantumCircuit(2)
lcu.h(1); lcu.cx(1, 0); lcu.h(1)
assert np.allclose(Operator(lcu).data[:2, :2], (np.eye(2)+X)/2)
print("Product-formula errors:", errors)

# Verify the low-degree signal response independently of a synthesis package.
for x in np.linspace(-1, 1, 21):
    W = x*np.eye(2) + 1j*np.sqrt(max(0, 1-x*x))*X
    assert np.allclose(W.conj().T @ W, np.eye(2))
    assert np.isclose((W @ W)[0, 0], 2*x*x-1)
