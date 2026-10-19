"""Runnable companion for Quantum Programming, Chapter 16."""
import io, json, sys
from importlib.metadata import version
from qiskit import QuantumCircuit, qpy
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Operator

secret = "1011"  # Written high bit first.
n = len(secret)
qc = QuantumCircuit(n+1)
qc.x(n); qc.h(range(n+1))
for qubit, bit in enumerate(reversed(secret)):
    if bit == "1":
        qc.cx(qubit, n)
qc.h(range(n))
# Save/load the coherent circuit before appending measurements.
buffer = io.BytesIO()
qpy.dump(qc, buffer); buffer.seek(0)
restored = qpy.load(buffer)[0]
assert Operator(qc).equiv(Operator(restored))
qc.measure_all()
counts = StatevectorSampler(seed=41).run([qc], shots=1024).result()[0].data.meas.get_counts()
assert all(bits[1:] == secret for bits in counts)
record = {"problem": "Bernstein-Vazirani", "secret": secret,
    "python": sys.version.split()[0], "qiskit": version("qiskit"),
    "seed": 41, "shots": 1024, "qubits": qc.num_qubits,
    "gate_counts": dict(qc.count_ops()), "counts": counts,
    "execution": "local ideal StatevectorSampler", "oracle_queries_per_shot": 1}
print(json.dumps(record, indent=2))
