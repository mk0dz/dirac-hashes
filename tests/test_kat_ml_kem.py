"""ML-KEM (FIPS 203) validated against NIST ACVP known-answer tests.

This is the bar for calling the implementation real: every vendored vector for every
parameter set must reproduce NIST's expected keys, ciphertexts and shared secrets
byte-for-byte.
"""
import pytest

import quantum_hash.pqc.ml_kem  # noqa: F401  (registers the schemes)
from kat import iter_tests, unhex
from quantum_hash.pqc.common.base import get_scheme

PARAM_SETS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]


@pytest.mark.parametrize("param_set", PARAM_SETS)
def test_keygen(param_set):
    kem = get_scheme(param_set)
    count = 0
    for _group, t in iter_tests("ml_kem_keygen", param_set):
        ek, dk = kem.keygen_internal(unhex(t["d"]), unhex(t["z"]))
        assert ek == unhex(t["ek"]), f"ek mismatch tc {t['tcId']}"
        assert dk == unhex(t["dk"]), f"dk mismatch tc {t['tcId']}"
        count += 1
    assert count, f"no keygen vectors for {param_set}"


@pytest.mark.parametrize("param_set", PARAM_SETS)
def test_encaps(param_set):
    kem = get_scheme(param_set)
    count = 0
    for group, t in iter_tests("ml_kem_encapdecap", param_set):
        if group.get("function") != "encapsulation":
            continue
        c, k = kem.encaps_internal(unhex(t["ek"]), unhex(t["m"]))
        assert c == unhex(t["c"]), f"ciphertext mismatch tc {t['tcId']}"
        assert k == unhex(t["k"]), f"shared-secret mismatch tc {t['tcId']}"
        count += 1
    assert count, f"no encaps vectors for {param_set}"


@pytest.mark.parametrize("param_set", PARAM_SETS)
def test_decaps(param_set):
    kem = get_scheme(param_set)
    count = 0
    for group, t in iter_tests("ml_kem_encapdecap", param_set):
        if group.get("function") != "decapsulation":
            continue
        k = kem.decaps_internal(unhex(t["dk"]), unhex(t["c"]))
        assert k == unhex(t["k"]), f"decaps shared-secret mismatch tc {t['tcId']}"
        count += 1
    assert count, f"no decaps vectors for {param_set}"
