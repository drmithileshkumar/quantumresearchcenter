"""Runnable companion for Quantum Programming, Chapter 13."""
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, transpile
from qiskit_aer.noise import NoiseModel, depolarizing_error

qc = QuantumCircuit(1)
qc.x(0); qc.measure_all()
noise = NoiseModel()
noise.add_all_qubit_quantum_error(depolarizing_error(0.1, 1), ["x"])
sim = AerSimulator(noise_model=noise, seed_simulator=31, max_parallel_threads=1)
counts = sim.run(transpile(qc, sim, optimization_level=0), shots=8192).result().get_counts()
p1 = counts.get("1", 0) / 8192
# E(rho) = .9 rho + .1 I/2, so expected P(1) = .95.
assert abs(p1 - 0.95) < 0.03
print("Simulated P(1):", p1, "analytic prediction: 0.95")
