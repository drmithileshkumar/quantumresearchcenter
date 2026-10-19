"""Runnable companion for Quantum Programming, Chapter 3."""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector

bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
bell.measure_all()
counts = StatevectorSampler(seed=8).run([bell], shots=1024).result()[0].data.meas.get_counts()
assert set(counts) <= {"00", "11"}
# An asymmetric check is essential: a Bell state hides reversed bit order.
asymmetric = QuantumCircuit(2)
asymmetric.x(0)
assert Statevector.from_instruction(asymmetric).probabilities_dict() == {"01": 1.0}
print(bell.draw(output="text"))
print(counts)
