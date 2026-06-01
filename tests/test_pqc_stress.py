"""Randomized stress tests: properties that must hold beyond the fixed KAT vectors.

KATs prove conformance on NIST's chosen inputs; these check the same operations over
many random keys/messages, plus negative cases (tampered messages, signatures and
ciphertexts) that KATs only partially cover.
"""
import os

import pytest

import quantum_hash.pqc as pqc

# Fast-to-exercise schemes (the slow SLH-DSA 's' variants are covered by KATs only).
SIG_SCHEMES = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87",
               "SLH-DSA-SHAKE-128f", "SLH-DSA-SHAKE-192f"]
KEM_SCHEMES = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]


def _flip_bit(data: bytes, index: int = 0) -> bytes:
    b = bytearray(data)
    b[index % len(b)] ^= 0x01
    return bytes(b)


@pytest.mark.parametrize("name", SIG_SCHEMES)
def test_signature_roundtrip_and_tamper(name):
    scheme = pqc.get_scheme(name)
    iterations = 20 if name.startswith("ML-DSA") else 4  # SLH 'f' signing is slower
    for i in range(iterations):
        pk, sk = scheme.keygen()
        assert len(pk) == scheme.sizes["pk"]
        assert len(sk) == scheme.sizes["sk"]
        msg = os.urandom(1 + (i * 7) % 128)
        ctx = b"" if i % 2 else os.urandom(i % 16)
        sig = scheme.sign(sk, msg, context=ctx)
        assert len(sig) == scheme.sizes["sig"]
        assert scheme.verify(pk, msg, sig, context=ctx)
        # Negative cases.
        assert not scheme.verify(pk, _flip_bit(msg), sig, context=ctx)
        assert not scheme.verify(pk, msg, _flip_bit(sig, len(sig) // 2), context=ctx)
        if ctx:
            assert not scheme.verify(pk, msg, sig, context=b"")


@pytest.mark.parametrize("name", KEM_SCHEMES)
def test_kem_roundtrip_and_implicit_reject(name):
    scheme = pqc.get_scheme(name)
    for _ in range(30):
        ek, dk = scheme.keygen()
        assert len(ek) == scheme.sizes["ek"]
        assert len(dk) == scheme.sizes["dk"]
        ct, ss = scheme.encaps(ek)
        assert len(ct) == scheme.sizes["ct"]
        assert scheme.decaps(dk, ct) == ss
        # Implicit rejection: a corrupted ciphertext yields a different secret, no error.
        ss_bad = scheme.decaps(dk, _flip_bit(ct, 3))
        assert ss_bad != ss


def test_determinism_and_independence():
    mldsa = pqc.get_scheme("ML-DSA-65")
    pk, sk = mldsa.keygen()
    msg = b"deterministic check"
    # Deterministic signing is reproducible and verifies.
    det1 = mldsa.sign(sk, msg, deterministic=True)
    det2 = mldsa.sign(sk, msg, deterministic=True)
    assert det1 == det2
    assert mldsa.verify(pk, msg, det1)
    # Two fresh keypairs are independent.
    pk2, _ = mldsa.keygen()
    assert pk2 != pk


def test_cross_scheme_signature_is_rejected():
    a = pqc.get_scheme("ML-DSA-44")
    b = pqc.get_scheme("ML-DSA-65")
    pk_a, sk_a = a.keygen()
    pk_b, _ = b.keygen()
    sig_a = a.sign(sk_a, b"hello")
    # A ML-DSA-44 signature must not verify under a ML-DSA-65 key (size/scheme mismatch).
    assert not b.verify(pk_b, b"hello", sig_a)
