"""Samplers for ML-KEM (FIPS 203 §4.2.2).

* :func:`sample_ntt` - Algorithm 7, rejection sampling of a uniform NTT-domain
  polynomial from a SHAKE128 stream seeded by ``rho ‖ j ‖ i``.
* :func:`sample_cbd` - Algorithm 8, a centered binomial distribution from PRF output.
"""
from __future__ import annotations

import numpy as np

from ..common.xof import SHAKEReader
from .params import N, Q


def sample_ntt(rho: bytes, j: int, i: int) -> np.ndarray:
    """Uniform polynomial in the NTT domain (Algorithm 7).

    The XOF seed is ``rho ‖ j ‖ i`` with ``j`` (column) before ``i`` (row), matching
    the construction of matrix entry Â[i][j] in FIPS 203.
    """
    reader = SHAKEReader(rho + bytes([j, i]), bits=128)
    out = np.empty(N, dtype=np.int64)
    count = 0
    while count < N:
        c = reader.read(3)
        d1 = c[0] | ((c[1] & 0x0F) << 8)
        d2 = (c[1] >> 4) | (c[2] << 4)
        if d1 < Q:
            out[count] = d1
            count += 1
        if d2 < Q and count < N:
            out[count] = d2
            count += 1
    return out


def sample_cbd(eta: int, buf: bytes) -> np.ndarray:
    """Sample a polynomial from a centered binomial distribution (Algorithm 8).

    ``buf`` must be 64*eta bytes. Coefficient i is (sum of eta bits) minus
    (sum of the next eta bits), reduced mod q.
    """
    bits = np.unpackbits(np.frombuffer(buf, dtype=np.uint8), bitorder="little")
    bits = bits[: 2 * eta * N].reshape(N, 2 * eta).astype(np.int64)
    x = bits[:, :eta].sum(axis=1)
    y = bits[:, eta:].sum(axis=1)
    return (x - y) % Q
