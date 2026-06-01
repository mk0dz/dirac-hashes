"""SLH-DSA parameter sets (FIPS 205, Table 2) - SHAKE instantiations.

Only the SHAKE family is implemented; for it the tweakable hashes F, H and T_l all
reduce to a single SHAKE256 call, which keeps the code small and uniform.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2


@dataclass(frozen=True)
class SLHParams:
    name: str
    n: int       # security parameter / hash output bytes
    h: int       # total hypertree height
    d: int       # number of hypertree layers
    a: int       # FORS tree height (each tree has 2^a leaves)
    k: int       # number of FORS trees
    lg_w: int    # log2 of Winternitz parameter (always 4 here)
    security_category: int

    @property
    def w(self) -> int:
        return 1 << self.lg_w

    @property
    def hp(self) -> int:               # height of one XMSS tree
        return self.h // self.d

    @property
    def len1(self) -> int:
        return ceil(8 * self.n / self.lg_w)

    @property
    def len2(self) -> int:
        return int(log2(self.len1 * (self.w - 1)) // self.lg_w) + 1

    @property
    def length(self) -> int:           # WOTS+ chains per key
        return self.len1 + self.len2

    @property
    def ka_bytes(self) -> int:
        return ceil(self.k * self.a / 8)

    @property
    def tree_bytes(self) -> int:
        return ceil((self.h - self.hp) / 8)

    @property
    def leaf_bytes(self) -> int:
        return ceil(self.hp / 8)

    @property
    def m(self) -> int:                # H_msg digest length
        return self.ka_bytes + self.tree_bytes + self.leaf_bytes

    @property
    def pk_bytes(self) -> int:
        return 2 * self.n

    @property
    def sk_bytes(self) -> int:
        return 4 * self.n

    @property
    def fors_bytes(self) -> int:
        return self.k * (1 + self.a) * self.n

    @property
    def ht_bytes(self) -> int:
        return (self.h + self.d * self.length) * self.n

    @property
    def sig_bytes(self) -> int:
        return self.n + self.fors_bytes + self.ht_bytes


def _p(name, n, h, d, a, k, cat):
    return SLHParams(name, n=n, h=h, d=d, a=a, k=k, lg_w=4, security_category=cat)


PARAMS = {
    "SLH-DSA-SHAKE-128s": _p("SLH-DSA-SHAKE-128s", 16, 63, 7, 12, 14, 1),
    "SLH-DSA-SHAKE-128f": _p("SLH-DSA-SHAKE-128f", 16, 66, 22, 6, 33, 1),
    "SLH-DSA-SHAKE-192s": _p("SLH-DSA-SHAKE-192s", 24, 63, 7, 14, 17, 3),
    "SLH-DSA-SHAKE-192f": _p("SLH-DSA-SHAKE-192f", 24, 66, 22, 8, 33, 3),
    "SLH-DSA-SHAKE-256s": _p("SLH-DSA-SHAKE-256s", 32, 64, 8, 14, 22, 5),
    "SLH-DSA-SHAKE-256f": _p("SLH-DSA-SHAKE-256f", 32, 68, 17, 9, 35, 5),
}
