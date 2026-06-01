"""Spec-correct post-quantum cryptography for dirac-hashes.

This package contains from-scratch, **research-grade** implementations of the NIST
post-quantum standards, validated against the official NIST ACVP known-answer tests:

* ``ml_kem``  - ML-KEM  (FIPS 203, formerly CRYSTALS-Kyber)     key encapsulation
* ``ml_dsa``  - ML-DSA  (FIPS 204, formerly CRYSTALS-Dilithium) signatures
* ``slh_dsa`` - SLH-DSA (FIPS 205, formerly SPHINCS+)           signatures
* ``falcon``  - Falcon  (FN-DSA, draft FIPS 206)                signatures  [stretch]

Design notes
------------
* Keys, ciphertexts and signatures are **canonical byte strings** matching the FIPS
  encodings (not the ad-hoc dicts of the legacy ``quantum_hash.signatures`` module).
* All symmetric primitives are SHAKE/SHA3 from the standard library, exactly as the
  standards require. The library's ``DiracHash`` is unrelated and is never used here.
* Pure Python ⇒ correct but **not constant-time**. Suitable for research, testing and
  benchmarking; not hardened against side-channel attacks. Do not use to protect
  real funds without an audited, constant-time backend.

The unified scheme registry lives in :mod:`quantum_hash.pqc.common.base`. Importing
this package registers every scheme, so ``from quantum_hash.pqc import get_scheme``
followed by ``get_scheme("ML-DSA-65")`` is all a caller needs.
"""

from .common.base import KEM, SignatureScheme, get_scheme, list_schemes, register

# Import the scheme packages for their registration side effects.
from . import ml_kem as ml_kem  # noqa: E402,F401
from . import ml_dsa as ml_dsa  # noqa: E402,F401
from . import slh_dsa as slh_dsa  # noqa: E402,F401


def signature_schemes() -> list[str]:
    """Names of all registered signature schemes."""
    return list_schemes(lambda s: isinstance(s, SignatureScheme))


def kem_schemes() -> list[str]:
    """Names of all registered KEM schemes."""
    return list_schemes(lambda s: isinstance(s, KEM))


__all__ = [
    "SignatureScheme", "KEM", "register", "get_scheme", "list_schemes",
    "signature_schemes", "kem_schemes",
]
