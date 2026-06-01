"""Unit tests for ML-DSA rounding/hint arithmetic (independent of KAT)."""
import numpy as np
import pytest

from quantum_hash.pqc.ml_dsa.params import D, PARAMS, Q
from quantum_hash.pqc.ml_dsa import rounding as r

GAMMA2 = sorted({p.gamma2 for p in PARAMS.values()})


def test_power2round_reconstructs():
    rng = np.random.default_rng(0)
    x = rng.integers(0, Q, size=256, dtype=np.int64)
    r1, r0 = r.power2round(x)
    assert np.array_equal((r1 * (1 << D) + r0) % Q, x)
    assert int(np.abs(r0).max()) <= (1 << (D - 1))


@pytest.mark.parametrize("gamma2", GAMMA2)
def test_decompose_reconstructs(gamma2):
    rng = np.random.default_rng(1)
    x = rng.integers(0, Q, size=256, dtype=np.int64)
    r1, r0 = r.decompose(x, gamma2)
    assert np.array_equal((r1 * (2 * gamma2) + r0) % Q, x)
    assert int(np.abs(r0).max()) <= gamma2


@pytest.mark.parametrize("gamma2", GAMMA2)
def test_hint_recovers_highbits(gamma2):
    """UseHint(MakeHint(z, r), r) == HighBits(r + z) for ||z||_inf <= gamma2."""
    rng = np.random.default_rng(2)
    for _ in range(50):
        x = rng.integers(0, Q, size=256, dtype=np.int64)
        z = rng.integers(-gamma2, gamma2 + 1, size=256, dtype=np.int64)
        h = r.make_hint(z, x, gamma2)
        recovered = r.use_hint(h, x, gamma2)
        assert np.array_equal(recovered, r.high_bits(x + z, gamma2))
