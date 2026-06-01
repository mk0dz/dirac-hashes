"""Samplers for ML-DSA (FIPS 204 §7.3).

* :func:`expand_a`     - Algorithm 32, uniform NTT-domain matrix from rho.
* :func:`expand_s`     - Algorithm 33, short secret vectors via rejection (CBD-like).
* :func:`expand_mask`  - Algorithm 34, the per-iteration masking vector y.
* :func:`sample_in_ball` - Algorithm 29, the sparse +/-1 challenge polynomial.
"""
from __future__ import annotations

import numpy as np

from ..common.xof import SHAKEReader, shake256
from .encode import bit_unpack
from .params import N, Q


def _rej_ntt_poly(seed: bytes) -> np.ndarray:
    """Uniform polynomial in NTT domain via rejection (Algorithm 30)."""
    reader = SHAKEReader(seed, bits=128)
    out = np.empty(N, dtype=np.int64)
    count = 0
    while count < N:
        b = reader.read(3)
        z = b[0] | (b[1] << 8) | ((b[2] & 0x7F) << 16)
        if z < Q:
            out[count] = z
            count += 1
    return out


def expand_a(rho: bytes, k: int, l: int) -> list[list[np.ndarray]]:
    """Â[r][s] = RejNTTPoly(rho ‖ s ‖ r) for r in [0,k), s in [0,l)."""
    return [[_rej_ntt_poly(rho + bytes([s, r])) for s in range(l)] for r in range(k)]


def _coeff_from_half_byte(b: int, eta: int) -> int | None:
    if eta == 2:
        return 2 - (b % 5) if b < 15 else None
    if eta == 4:
        return 4 - b if b < 9 else None
    raise ValueError(f"unsupported eta {eta}")  # pragma: no cover


def _rej_bounded_poly(seed: bytes, eta: int) -> np.ndarray:
    """Short polynomial with coefficients in [-eta, eta] (Algorithm 31)."""
    reader = SHAKEReader(seed, bits=256)
    out = np.empty(N, dtype=np.int64)
    count = 0
    while count < N:
        byte = reader.read(1)[0]
        for nibble in (byte & 0x0F, byte >> 4):
            if count >= N:
                break
            c = _coeff_from_half_byte(nibble, eta)
            if c is not None:
                out[count] = c
                count += 1
    return out


def expand_s(rho_prime: bytes, k: int, l: int, eta: int):
    """Sample (s1, s2) with coefficients in [-eta, eta] (Algorithm 33)."""
    s1 = [_rej_bounded_poly(rho_prime + bytes([i & 0xFF, i >> 8]), eta)
          for i in range(l)]
    s2 = [_rej_bounded_poly(rho_prime + bytes([(l + i) & 0xFF, (l + i) >> 8]), eta)
          for i in range(k)]
    return s1, s2


def expand_mask(rho_pp: bytes, mu: int, l: int, gamma1: int) -> list[np.ndarray]:
    """Mask vector y with coefficients in (-gamma1, gamma1] (Algorithm 34)."""
    c = 1 + (gamma1 - 1).bit_length()  # bytes per coefficient block: 32*c total
    out = []
    for r in range(l):
        idx = mu + r
        v = shake256(rho_pp + bytes([idx & 0xFF, idx >> 8]), 32 * c)
        out.append(bit_unpack(v, gamma1 - 1, gamma1))
    return out


def sample_in_ball(rho: bytes, tau: int) -> np.ndarray:
    """Sparse challenge polynomial with tau nonzero +/-1 coefficients (Algorithm 29)."""
    reader = SHAKEReader(rho, bits=256)
    signs = int.from_bytes(reader.read(8), "little")
    c = np.zeros(N, dtype=np.int64)
    for i in range(N - tau, N):
        while True:
            j = reader.read(1)[0]
            if j <= i:
                break
        c[i] = c[j]
        c[j] = 1 - 2 * (signs & 1)
        signs >>= 1
    return c
