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

# Phase estimation: counting qubits 0 and 1, eigenstate |1> of P(2*pi*phi) on qubit 2.
phi = 1 / 4
qpe = QuantumCircuit(3)
qpe.x(2)
qpe.h([0, 1])
for j in range(2):
    qpe.cp(2 * np.pi * phi * 2**j, j, 2)  # controlled U^(2^j)
qpe.compose(qft.inverse(), qubits=[0, 1], inplace=True)
counting = Statevector.from_instruction(qpe).probabilities([0, 1])
assert np.isclose(counting[1], 1)  # integer 1 = phi * 4

# One Grover step for marked state |11> in four items.
search = QuantumCircuit(2)
search.h([0, 1])
search.cz(0, 1)
search.h([0, 1]); search.x([0, 1]); search.cz(0, 1)
search.x([0, 1]); search.h([0, 1])
assert np.isclose(Statevector.from_instruction(search).probabilities()[3], 1)

# One coined-walk step on a 4-cycle: coin q0, position q1 + 2*q2.
walk = QuantumCircuit(3)
walk.h(0)
walk.cx(0, 1); walk.ccx(0, 1, 2)                 # coin 1: position - 1
walk.x(0); walk.ccx(0, 1, 2); walk.cx(0, 1); walk.x(0)  # coin 0: position + 1
shift = np.zeros((8, 8))
for coin in range(2):
    for position in range(4):
        moved = (position + (1 if coin == 0 else -1)) % 4
        shift[coin + 2 * moved, coin + 2 * position] = 1
coin_flip = np.kron(np.eye(4), np.array([[1, 1], [1, -1]]) / np.sqrt(2))
assert np.allclose(Operator(walk).data, shift @ coin_flip)
print(qft.draw(output="text"))
