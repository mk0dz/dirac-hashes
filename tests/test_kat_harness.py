"""Phase 0 smoke test: the vendored KAT vectors load and are structurally sane.

This does not exercise any cryptography yet — it only proves the known-answer-test
harness (loader + vendored ACVP vectors) is wired up, so later scheme suites can
rely on it. Per-scheme KAT suites live in ``test_kat_ml_kem.py`` etc.
"""
import pytest

from kat import iter_tests, load, unhex

# Expected canonical key sizes (bytes) from FIPS 203, used as a structural check
# that we vendored the real vectors and the loader decodes hex correctly.
ML_KEM_SIZES = {
    "ML-KEM-512": {"ek": 800, "dk": 1632},
    "ML-KEM-768": {"ek": 1184, "dk": 2400},
    "ML-KEM-1024": {"ek": 1568, "dk": 3168},
}


def test_loader_missing_file_is_explicit():
    with pytest.raises(FileNotFoundError):
        load("does_not_exist")


@pytest.mark.parametrize("param_set,sizes", ML_KEM_SIZES.items())
def test_ml_kem_keygen_vectors_present_and_sized(param_set, sizes):
    cases = list(iter_tests("ml_kem_keygen", param_set))
    assert cases, f"no vectors for {param_set}"
    for group, test in cases:
        assert len(unhex(test["d"])) == 32
        assert len(unhex(test["z"])) == 32
        assert len(unhex(test["ek"])) == sizes["ek"]
        assert len(unhex(test["dk"])) == sizes["dk"]


def test_ml_dsa_siggen_groups_expose_interface_fields():
    # Phase 3 depends on these fields existing in the vectors.
    seen_param_sets = set()
    for group, test in iter_tests("ml_dsa_siggen"):
        seen_param_sets.add(group["parameterSet"])
        assert "deterministic" in group
        assert group["signatureInterface"] in ("internal", "external")
        assert {"pk", "sk", "signature"} <= set(test)
        # Pure/preHash groups carry `message`; externalMu groups carry `mu`.
        assert ("message" in test) or ("mu" in test)
    assert {"ML-DSA-44", "ML-DSA-65", "ML-DSA-87"} <= seen_param_sets
