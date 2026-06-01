"""Vendored NIST ACVP known-answer test vectors and a small loader.

The JSON files under ``kat/vectors`` are trimmed copies of NIST's ACVP
``internalProjection.json`` files (see ``fetch_acvp.py``). They drive the KAT
suites in ``tests/`` and are the bar for calling an implementation "real".
"""
from .loader import iter_tests, load, unhex

__all__ = ["load", "iter_tests", "unhex"]
