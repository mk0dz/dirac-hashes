"""Make the src-layout package and the repo root importable during tests.

Putting ``src`` first means the in-tree ``quantum_hash`` is used even if an older
build is installed in site-packages, and the repo root lets tests import ``kat``.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for p in (ROOT / "src", ROOT):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
