"""Tweakable hash functions for the SLH-DSA SHAKE instantiations (FIPS 205 §11.1).

For the SHAKE family, F, H and T_l are all SHAKE256(PK.seed ‖ ADRS ‖ M, 8n), so a
single helper covers them. ``base_2b`` (Algorithm 4) converts a byte string to
base-2^b digits and is used for both WOTS+ message encoding and FORS index extraction.
"""
from __future__ import annotations

import hashlib

from .adrs import ADRS


class ShakeHashes:
    def __init__(self, n: int, m: int):
        self.n = n
        self.m = m

    def h_msg(self, r: bytes, pk_seed: bytes, pk_root: bytes, message: bytes) -> bytes:
        return hashlib.shake_256(r + pk_seed + pk_root + message).digest(self.m)

    def prf(self, pk_seed: bytes, sk_seed: bytes, adrs: ADRS) -> bytes:
        return hashlib.shake_256(pk_seed + adrs.bytes() + sk_seed).digest(self.n)

    def prf_msg(self, sk_prf: bytes, opt_rand: bytes, message: bytes) -> bytes:
        return hashlib.shake_256(sk_prf + opt_rand + message).digest(self.n)

    def f(self, pk_seed: bytes, adrs: ADRS, m1: bytes) -> bytes:
        return hashlib.shake_256(pk_seed + adrs.bytes() + m1).digest(self.n)

    # H and T_l are identical to F for the SHAKE variant.
    h = f
    t = f


def base_2b(data: bytes, b: int, out_len: int) -> list[int]:
    """Convert a byte string to ``out_len`` base-2^b digits (Algorithm 4)."""
    pos = 0
    bits = 0
    total = 0
    mask = (1 << b) - 1
    out = []
    for _ in range(out_len):
        while bits < b:
            total = (total << 8) | data[pos]
            pos += 1
            bits += 8
        bits -= b
        out.append((total >> bits) & mask)
    return out
