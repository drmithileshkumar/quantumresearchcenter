"""Runnable companion for Quantum Programming, Chapter 7."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

# f(a,b,c) = ab XOR c; q0=a, q1=b, q2=c, q3=target.
qc = QuantumCircuit(4)
qc.ccx(0, 1, 3)
qc.cx(2, 3)
matrix = Operator(qc).data
for index in range(16):
    a, b, c = index & 1, (index >> 1) & 1, (index >> 2) & 1
    expected = index ^ (((a & b) ^ c) << 3)
    assert np.allclose(matrix[:, index], np.eye(16)[:, expected])
# Target minus makes the same oracle a phase oracle.
prep = QuantumCircuit(4)
prep.h([0, 1, 2])
prep.x(3)
prep.h(3)
state = Statevector.from_instruction(prep.compose(qc))
expected = []
for index in range(16):
    a, b, c, target = [(index >> k) & 1 for k in range(4)]
    expected.append((-1)**((a & b) ^ c ^ target) / 4)
assert np.allclose(state.data, expected)
print("All basis columns and coherent signs verified")
