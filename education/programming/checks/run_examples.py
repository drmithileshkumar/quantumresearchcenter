#!/usr/bin/env python3
"""Run every companion locally. Never adds the hardware --submit option."""
from pathlib import Path
import importlib.metadata
import os
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
env=os.environ.copy()
# Some Linux Python 3.14 processes exhaust static TLS before Aer loads OpenMP.
# Preload only the library shipped in the installed Aer distribution, in child
# processes. This has no effect on the user's shell or global configuration.
if sys.platform.startswith('linux'):
    bundled=Path(importlib.metadata.distribution('qiskit-aer').locate_file('qiskit_aer.libs'))
    candidates=sorted(bundled.glob('libgomp*.so*'))
    if candidates:
        existing=env.get('LD_PRELOAD','')
        env['LD_PRELOAD']=str(candidates[0]) + (':'+existing if existing else '')
for path in sorted((root/'examples').glob('chapter_*.py')):
    result=subprocess.run([sys.executable,str(path)],env=env,text=True,capture_output=True,timeout=90)
    if result.returncode:
        print(result.stdout+result.stderr)
        raise SystemExit(f'FAIL: {path.name}')
    print(f'PASS: {path.name}',flush=True)
print('All 16 companion examples passed locally; no hardware jobs submitted.')
