"""Runnable companion for Quantum Programming, Chapter 12."""
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, transpile

# q0=input, q1=Alice's half, q2=Bob's half; c0,c1 are correction records.
qc = QuantumCircuit(3, 3)
qc.ry(0.7, 0); qc.rz(0.4, 0)
qc.h(1); qc.cx(1, 2)
qc.cx(0, 1); qc.h(0)
qc.measure(0, 0); qc.measure(1, 1)
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
with qc.if_test((qc.clbits[0], 1)):
    qc.z(2)
# Inverse of the known test preparation verifies the recovered state.
qc.rz(-0.4, 2); qc.ry(-0.7, 2)
qc.measure(2, 2)
sim = AerSimulator(seed_simulator=23, max_parallel_threads=1)
counts = sim.run(transpile(qc, sim), shots=1024).result().get_counts()
assert all(key[0] == "0" for key in counts)
print("c2 c1 c0:", counts)
