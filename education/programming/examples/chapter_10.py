"""Runnable companion for Quantum Programming, Chapter 10."""
from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap, generate_preset_pass_manager
from qiskit.quantum_info import Operator

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 2)

def compile_for(coupling_map):
    # The same preset pipeline that transpile() builds internally.
    pass_manager = generate_preset_pass_manager(
        optimization_level=1, basis_gates=["rz", "sx", "x", "cx"],
        coupling_map=coupling_map, initial_layout=[0, 1, 2], seed_transpiler=19)
    return pass_manager.run(qc)

line = compile_for(CouplingMap.from_line(3))
full = compile_for(CouplingMap.from_full(3))
for compiled in (line, full):
    assert Operator.from_circuit(compiled).equiv(Operator(qc))
assert full.count_ops()["cx"] == 1 and line.count_ops()["cx"] > 1
print("Logical", qc.count_ops())
print("Line", line.count_ops(), "full", full.count_ops())
print("Line final layout:", line.layout.final_index_layout())
