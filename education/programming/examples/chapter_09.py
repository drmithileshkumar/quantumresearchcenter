"""Runnable companion for Quantum Programming, Chapter 9."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

identity = QuantumCircuit(1)
wrong = QuantumCircuit(1)
wrong.z(0)
# Basis output probabilities match, but relative phase differs.
for label in ("0", "1"):
    state = Statevector.from_label(label)
    assert np.allclose(state.evolve(identity).probabilities(), state.evolve(wrong).probabilities())
assert not Statevector.from_label("+").evolve(identity).equiv(Statevector.from_label("+").evolve(wrong))
assert not Operator(identity).equiv(Operator(wrong))
phase = QuantumCircuit(1)
phase.global_phase = 0.3
assert Operator(identity).equiv(Operator(phase))
assert not Operator(identity.to_gate().control()).equiv(Operator(phase.to_gate().control()))
print("Relative-phase bug detected; controlled global phase also checked")
