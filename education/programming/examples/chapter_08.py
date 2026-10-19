"""Runnable companion for Quantum Programming, Chapter 8."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

# Positive-sign QFT on integer labels |q1 q0>.
qft = QuantumCircuit(2)
qft.h(1)
qft.cp(np.pi / 2, 0, 1)
qft.h(0)
qft.swap(0, 1)
expected = np.array([[np.exp(2j*np.pi*x*y/4)/2 for x in range(4)] for y in range(4)])
assert np.allclose(Operator(qft).data, expected)
# One Grover step for marked state |11> in four items.
search = QuantumCircuit(2)
search.h([0, 1])
search.cz(0, 1)
search.h([0, 1]); search.x([0, 1]); search.cz(0, 1)
search.x([0, 1]); search.h([0, 1])
assert np.isclose(Statevector.from_instruction(search).probabilities()[3], 1)
print(qft.draw(output="text"))
