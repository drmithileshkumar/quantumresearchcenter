"""Runnable companion for Quantum Programming, Chapter 6."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import StatevectorSampler, StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp

theta = Parameter("theta")
qc = QuantumCircuit(1)
qc.ry(theta, 0)
values = [[0], [np.pi / 2], [np.pi]]
result = StatevectorEstimator().run([(qc, SparsePauliOp("Z"), values)]).result()
assert np.allclose(result[0].data.evs, [1, 0, -1])
measured = qc.assign_parameters({theta: np.pi / 2})
measured.measure_all()
counts = StatevectorSampler(seed=9).run([measured], shots=4096).result()[0].data.meas.get_counts()
print("Exact means:", result[0].data.evs, "sampled counts:", counts)
