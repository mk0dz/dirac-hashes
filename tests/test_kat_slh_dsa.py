"""SLH-DSA (FIPS 205, SHAKE instantiations) validated against NIST ACVP.

The ACVP files also contain SHA2 parameter sets, which this library does not
implement; those are filtered out. sigGen for the 's' parameter sets is slow in pure
Python, so it is split out and marked ``slow`` (run with ``-m slow``).
"""
import hashlib

import pytest

import quantum_hash.pqc.slh_dsa  # noqa: F401  (registers the schemes)
from kat import iter_tests, unhex
from quantum_hash.pqc.common.base import get_scheme

SHAKE_SETS = [
    "SLH-DSA-SHAKE-128f", "SLH-DSA-SHAKE-128s",
    "SLH-DSA-SHAKE-192f", "SLH-DSA-SHAKE-192s",
    "SLH-DSA-SHAKE-256f", "SLH-DSA-SHAKE-256s",
]
FAST_SETS = [s for s in SHAKE_SETS if s.endswith("f")]
SLOW_SETS = [s for s in SHAKE_SETS if s.endswith("s")]

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


def _prehash(alg, m):
    if alg == "SHAKE-128":
        return hashlib.shake_128(m).digest(32)
    if alg == "SHAKE-256":
        return hashlib.shake_256(m).digest(64)
    return hashlib.new(_HASHLIB_NAME[alg], m).digest()


def _m_prime(group, test):
    ctx = unhex(test.get("context") or "")
    msg = unhex(test["message"])
    if group.get("preHash") == "preHash":
        alg = test["hashAlg"]
        oid = bytes([0x06, 0x09, 0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02,
                     _OID_LAST[alg]])
        return bytes([1, len(ctx)]) + ctx + oid + _prehash(alg, msg)
    return bytes([0, len(ctx)]) + ctx + msg


def _message_for(scheme, group, test):
    if group["signatureInterface"] == "internal":
        return unhex(test["message"])
    return _m_prime(group, test)


@pytest.mark.parametrize("param_set", SHAKE_SETS)
def test_keygen(param_set):
    d = get_scheme(param_set)
    count = 0
    for _g, t in iter_tests("slh_dsa_keygen", param_set):
        pk, sk = d.keygen_internal(unhex(t["skSeed"]), unhex(t["skPrf"]),
                                   unhex(t["pkSeed"]))
        assert pk == unhex(t["pk"]), f"pk mismatch tc {t['tcId']}"
        assert sk == unhex(t["sk"]), f"sk mismatch tc {t['tcId']}"
        count += 1
    assert count, f"no keygen vectors for {param_set}"


@pytest.mark.parametrize("param_set", SHAKE_SETS)
def test_sigver(param_set):
    d = get_scheme(param_set)
    count = 0
    for g, t in iter_tests("slh_dsa_sigver", param_set):
        ok = d.verify_internal(_message_for(d, g, t), unhex(t["signature"]),
                               unhex(t["pk"]))
        assert ok == bool(t["testPassed"]), f"{param_set} tc {t['tcId']}"
        count += 1
    assert count, f"no sigver vectors for {param_set}"


def _run_siggen(param_set):
    d = get_scheme(param_set)
    n = d.p.n
    count = 0
    for g, t in iter_tests("slh_dsa_siggen", param_set):
        sk = unhex(t["sk"])
        addrnd = sk[2 * n:3 * n] if g["deterministic"] else unhex(t["additionalRandomness"])
        sig = d.sign_internal(_message_for(d, g, t), sk, addrnd)
        assert sig == unhex(t["signature"]), f"{param_set} tc {t['tcId']}"
        count += 1
    assert count, f"no siggen vectors for {param_set}"


@pytest.mark.parametrize("param_set", FAST_SETS)
def test_siggen_fast(param_set):
    _run_siggen(param_set)


@pytest.mark.slow
@pytest.mark.parametrize("param_set", SLOW_SETS)
def test_siggen_slow(param_set):
    _run_siggen(param_set)
