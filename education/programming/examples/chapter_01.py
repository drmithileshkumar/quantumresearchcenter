"""Runnable companion for Quantum Programming, Chapter 1."""
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# A Python function builds a circuit; it does not execute a quantum device.
def bell():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return circuit

circuit = bell()
assert Statevector.from_instruction(circuit).equiv(
    Statevector([2**-0.5, 0, 0, 2**-0.5]))
print(circuit.draw(output="text"))
