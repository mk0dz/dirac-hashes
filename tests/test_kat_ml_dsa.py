"""ML-DSA (FIPS 204) validated against NIST ACVP known-answer tests.

Covers all four ACVP interfaces: internal, external/pure, external/preHash
(HashML-DSA) and externalMu - across keyGen, sigGen and sigVer.
"""
import hashlib

import pytest

import quantum_hash.pqc.ml_dsa  # noqa: F401  (registers the schemes)
from kat import iter_tests, unhex
from quantum_hash.pqc.common.base import get_scheme

PARAM_SETS = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]

# DER object identifiers for the pre-hash functions (NIST CSOR 2.16.840.1.101.3.4.2.x).
_OID_LAST = {
    "SHA2-256": 0x01, "SHA2-384": 0x02, "SHA2-512": 0x03, "SHA2-224": 0x04,
    "SHA2-512/224": 0x05, "SHA2-512/256": 0x06, "SHA3-224": 0x07, "SHA3-256": 0x08,
    "SHA3-384": 0x09, "SHA3-512": 0x0A, "SHAKE-128": 0x0B, "SHAKE-256": 0x0C,
}
_HASHLIB_NAME = {
    "SHA2-224": "sha224", "SHA2-256": "sha256", "SHA2-384": "sha384",
    "SHA2-512": "sha512", "SHA2-512/224": "sha512_224", "SHA2-512/256": "sha512_256",
    "SHA3-224": "sha3_224", "SHA3-256": "sha3_256", "SHA3-384": "sha3_384",
    "SHA3-512": "sha3_512",
}


def _oid(alg: str) -> bytes:
    return bytes([0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02,
                  _OID_LAST[alg]])


def _prehash(alg: str, m: bytes) -> bytes:
    if alg == "SHAKE-128":
        return hashlib.shake_128(m).digest(32)
    if alg == "SHAKE-256":
        return hashlib.shake_256(m).digest(64)
    return hashlib.new(_HASHLIB_NAME[alg], m).digest()


def _m_prime(group, test) -> bytes:
    """Reconstruct the internal message representative M' for an external test."""
    ctx = unhex(test.get("context") or "")
    msg = unhex(test["message"])
    if group.get("preHash") == "preHash":
        alg = test["hashAlg"]
        return bytes([1, len(ctx)]) + ctx + _oid(alg) + _prehash(alg, msg)
    return bytes([0, len(ctx)]) + ctx + msg


@pytest.mark.parametrize("param_set", PARAM_SETS)
def test_keygen(param_set):
    d = get_scheme(param_set)
    count = 0
    for _g, t in iter_tests("ml_dsa_keygen", param_set):
        pk, sk = d.keygen_internal(unhex(t["seed"]))
        assert pk == unhex(t["pk"]), f"pk mismatch tc {t['tcId']}"
        assert sk == unhex(t["sk"]), f"sk mismatch tc {t['tcId']}"
        count += 1
    assert count, f"no keygen vectors for {param_set}"


@pytest.mark.parametrize("param_set", PARAM_SETS)
def test_siggen(param_set):
    d = get_scheme(param_set)
    count = 0
    for g, t in iter_tests("ml_dsa_siggen", param_set):
        rnd = bytes(32) if g["deterministic"] else unhex(t["rnd"])
        sk = unhex(t["sk"])
        if g["externalMu"]:
            sig = d.sign_external_mu(sk, unhex(t["mu"]), rnd)
        elif g["signatureInterface"] == "internal":
            sig = d.sign_internal(sk, unhex(t["message"]), rnd)
        else:
            sig = d.sign_internal(sk, _m_prime(g, t), rnd)
        assert sig == unhex(t["signature"]), \
            f"{param_set} tc {t['tcId']} ({g.get('preHash')}/{g['signatureInterface']})"
        count += 1
    assert count, f"no siggen vectors for {param_set}"


@pytest.mark.parametrize("param_set", PARAM_SETS)
def test_sigver(param_set):
    d = get_scheme(param_set)
    count = 0
    for g, t in iter_tests("ml_dsa_sigver", param_set):
        pk = unhex(t["pk"])
        sig = unhex(t["signature"])
        if g["externalMu"]:
            ok = d.verify_external_mu(pk, unhex(t["mu"]), sig)
        elif g["signatureInterface"] == "internal":
            ok = d.verify_internal(pk, unhex(t["message"]), sig)
        else:
            ok = d.verify_internal(pk, _m_prime(g, t), sig)
        assert ok == bool(t["testPassed"]), f"{param_set} tc {t['tcId']}"
        count += 1
    assert count, f"no sigver vectors for {param_set}"
