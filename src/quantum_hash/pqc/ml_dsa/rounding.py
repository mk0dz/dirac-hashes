"""Rounding and hint arithmetic for ML-DSA (FIPS 204 §7.4).

All functions are vectorized over length-256 numpy ``int64`` polynomials. Centered
representatives use the convention ``r mod± a ∈ (-a/2, a/2]``.
"""
from __future__ import annotations

import numpy as np

from .params import D, Q


def _centered(r: np.ndarray, a: int) -> np.ndarray:
    """r mod± a in (-a/2, a/2]."""
    r0 = r % a
    return np.where(r0 > a // 2, r0 - a, r0)


def inf_norm(poly: np.ndarray) -> int:
    """max |coeff| using centered representatives mod q."""
    c = poly % Q
    c = np.where(c > (Q - 1) // 2, c - Q, c)
    return int(np.abs(c).max(initial=0))


def power2round(r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Split r = r1*2^d + r0 with r0 = r mod± 2^d (Algorithm 35)."""
    r = r % Q
    r0 = r & ((1 << D) - 1)
    r0 = np.where(r0 > (1 << (D - 1)), r0 - (1 << D), r0)
    r1 = (r - r0) >> D
    return r1, r0


def decompose(r: np.ndarray, gamma2: int) -> tuple[np.ndarray, np.ndarray]:
    """Decompose r into (r1, r0) with r = r1*(2*gamma2) + r0 (Algorithm 36)."""
    a = 2 * gamma2
    r = r % Q
    r0 = _centered(r, a)
    rmr0 = r - r0
    boundary = rmr0 == (Q - 1)
    r1 = np.where(boundary, 0, rmr0 // a)
    r0 = np.where(boundary, r0 - 1, r0)
    return r1, r0


def high_bits(r: np.ndarray, gamma2: int) -> np.ndarray:
    return decompose(r, gamma2)[0]


def low_bits(r: np.ndarray, gamma2: int) -> np.ndarray:
    return decompose(r, gamma2)[1]


def make_hint(z: np.ndarray, r: np.ndarray, gamma2: int) -> np.ndarray:
    """1 where HighBits(r) != HighBits(r+z), else 0 (Algorithm 39)."""
    return (high_bits(r, gamma2) != high_bits(r + z, gamma2)).astype(np.int64)


def use_hint(h: np.ndarray, r: np.ndarray, gamma2: int) -> np.ndarray:
    """Recover the corrected high bits using the hint (Algorithm 40)."""
    m = (Q - 1) // (2 * gamma2)
    r1, r0 = decompose(r, gamma2)
    up = (r1 + 1) % m
    down = (r1 - 1) % m
    return np.where(h == 1, np.where(r0 > 0, up, down), r1)
