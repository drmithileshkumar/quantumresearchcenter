"""Runnable companion for Quantum Programming, Chapter 10."""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit.quantum_info import Operator

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 2)
compiled = transpile(qc, basis_gates=["rz", "sx", "x", "cx"],
    coupling_map=CouplingMap.from_line(3), initial_layout=[0, 1, 2],
    optimization_level=1, seed_transpiler=19)
logical = Operator.from_circuit(compiled)
assert logical.equiv(Operator(qc))
print("Logical", qc.count_ops(), "compiled", compiled.count_ops())
print("Layout:", compiled.layout)
