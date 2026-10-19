"""Runnable companion for Quantum Programming, Chapter 11."""
import argparse
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

def build(backend):
    circuit = QuantumCircuit(2)
    circuit.h(0); circuit.cx(0, 1); circuit.measure_all()
    return generate_preset_pass_manager(backend=backend, optimization_level=1,
                                        seed_transpiler=17).run(circuit)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--submit", action="store_true", help="Explicitly submit a paid/allocated hardware job")
    parser.add_argument("--backend", help="Exact accessible hardware backend name")
    args = parser.parse_args()
    if not args.submit:
        compiled = build(GenericBackendV2(2, seed=3))
        print("Local compilation only; no account accessed and no job submitted.")
        print(compiled.count_ops())
    else:
        if not args.backend:
            parser.error("--backend is required with --submit")
        service = QiskitRuntimeService()  # Uses a separately configured account.
        backend = service.backend(args.backend)
        compiled = build(backend)
        job = SamplerV2(mode=backend).run([compiled], shots=1024)
        print("Submitted job:", job.job_id())
        print(job.result()[0].data.meas.get_counts())
