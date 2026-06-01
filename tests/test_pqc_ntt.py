"""Phase 1 gate: the NTTs are provably correct.

We do not need KAT vectors for this - an NTT is correct iff it round-trips and iff
multiplication in the NTT domain matches a schoolbook negacyclic multiply in
Z_q[X]/(X^256+1). Every later lattice scheme depends on this holding.
"""
import numpy as np
import pytest

from quantum_hash.pqc.common.ntt import DilithiumNTT, KyberNTT, N


def schoolbook_negacyclic(f: np.ndarray, g: np.ndarray, q: int) -> np.ndarray:
    """Reference multiply in Z_q[X]/(X^n + 1) (X^n = -1)."""
    f = [int(x) for x in f]
    g = [int(x) for x in g]
    res = [0] * N
    for i in range(N):
        for j in range(N):
            k = i + j
            prod = f[i] * g[j]
            if k < N:
                res[k] += prod
            else:
                res[k - N] -= prod
    return np.array([x % q for x in res], dtype=np.int64)


def _rng(seed):
    return np.random.default_rng(seed)


@pytest.mark.parametrize("engine_cls", [KyberNTT, DilithiumNTT])
def test_ntt_roundtrip(engine_cls):
    eng = engine_cls()
    rng = _rng(1)
    for _ in range(20):
        f = rng.integers(0, eng.q, size=N, dtype=np.int64)
        back = eng.intt(eng.ntt(f))
        assert np.array_equal(back % eng.q, f % eng.q)


@pytest.mark.parametrize("engine_cls", [KyberNTT, DilithiumNTT])
def test_ntt_multiply_matches_schoolbook(engine_cls):
    eng = engine_cls()
    rng = _rng(2)
    for _ in range(20):
        f = rng.integers(0, eng.q, size=N, dtype=np.int64)
        g = rng.integers(0, eng.q, size=N, dtype=np.int64)
        got = eng.intt(eng.basemul(eng.ntt(f), eng.ntt(g)))
        want = schoolbook_negacyclic(f, g, eng.q)
        assert np.array_equal(got, want)


@pytest.mark.parametrize("engine_cls", [KyberNTT, DilithiumNTT])
def test_ntt_multiplicative_identity(engine_cls):
    """Multiplying by the constant polynomial 1 is the identity in the NTT domain."""
    eng = engine_cls()
    one = np.zeros(N, dtype=np.int64)
    one[0] = 1
    rng = _rng(3)
    f = rng.integers(0, eng.q, size=N, dtype=np.int64)
    prod = eng.intt(eng.basemul(eng.ntt(f), eng.ntt(one)))
    assert np.array_equal(prod, f % eng.q)
