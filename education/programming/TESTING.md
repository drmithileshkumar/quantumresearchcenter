# Tested examples

All sixteen chapter scripts were executed locally with Python 3.14.4 on Linux
x86_64, using Qiskit 2.6.0, Aer 0.17.2, IBM Runtime 0.50.0, NumPy 2.5.4, and
SciPy 1.18.1. Direct dependencies are pinned in `requirements.txt`; the full
resolved environment is recorded in `requirements-lock.txt`.

From the repository root:

```sh
python3 -m venv .venv-quantum
source .venv-quantum/bin/activate
python -m pip install -r education/programming/requirements.txt
python education/programming/checks/run_examples.py
```

The runner launches each script in a fresh process. It checks state preparation,
bit order, coherent oracle signs, Fourier matrices, search success, controlled
phases, compilation with layout, all observed teleportation branches, a noisy
channel's analytic prediction, variational energies, product-formula error,
operator blocks, and circuit serialization. Finite examples do not prove
asymptotic algorithmic or hardware performance.

## Linux Aer loading

The tested Linux process reported `cannot allocate memory in static TLS block`
when importing Aer after dynamically loading scientific libraries. The runner
preloads the OpenMP library bundled with the installed Aer distribution into its
child processes. It does not modify shell settings or system libraries. If a
standalone Aer script encounters the same error, use the runner or set
`LD_PRELOAD` to the installed distribution's `qiskit_aer.libs/libgomp*.so*` file
for that invocation only. This is an environment workaround, not a quantum
programming requirement.

## Execution boundaries

Chapter 11 was checked only in its default local compilation mode using a
synthetic backend. Its explicitly guarded `--submit --backend NAME` branch was
reviewed against the Runtime API but was **not run on hardware**. It requires a
separately configured account, compatible backend, and an execution budget.
No credentials are included and no hardware results are claimed.

Chapters 12 and 13 used Aer simulation. Other examples use local SDK primitives
or mathematical state/operator calculations. Seeds support reproduction within
the pinned implementation; exact random count strings are not a portable API
contract. The examples assert predictions using exact checks or stated tolerances.
