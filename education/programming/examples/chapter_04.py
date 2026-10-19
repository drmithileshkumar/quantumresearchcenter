"""Runnable companion for Quantum Programming, Chapter 4."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, Operator, SparsePauliOp, partial_trace

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
state = Statevector.from_instruction(qc)
local = partial_trace(DensityMatrix(state), [1])
assert np.allclose(local.data, np.eye(2) / 2)
assert np.isclose(state.expectation_value(SparsePauliOp("XX")), 1)
assert np.isclose(state.expectation_value(SparsePauliOp("ZI")), 0)
assert np.allclose(Operator(qc).data.conj().T @ Operator(qc).data, np.eye(4))
print("Local state:", local.data)
