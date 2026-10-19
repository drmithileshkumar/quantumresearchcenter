"""Runnable companion for Quantum Programming, Chapter 2."""
import sys
from importlib.metadata import version
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

circuit = QuantumCircuit(1)
circuit.h(0)
circuit.measure_all()
counts = StatevectorSampler(seed=7).run([circuit], shots=4096).result()[0].data.meas.get_counts()
assert sum(counts.values()) == 4096
assert abs(counts.get("1", 0) / 4096 - 0.5) < 0.05
print("Python", sys.version.split()[0], "Qiskit", version("qiskit"))
print(counts)
