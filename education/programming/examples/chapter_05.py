"""Runnable companion for Quantum Programming, Chapter 5."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Operator

angle = Parameter("theta")
def rotation(theta):
    qc = QuantumCircuit(1, name="rotation")
    qc.ry(theta, 0)
    return qc

component = rotation(angle)
bound = component.assign_parameters({angle: 0.7})
identity = bound.compose(bound.inverse())
assert np.allclose(Operator(identity).data, np.eye(2))
controlled = bound.to_gate().control(1)
qc = QuantumCircuit(2)
qc.append(controlled, [0, 1])
print(qc.draw(output="text"))
