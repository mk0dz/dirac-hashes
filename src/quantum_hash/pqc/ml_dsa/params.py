"""ML-DSA parameter sets (FIPS 204, Table 1)."""
from __future__ import annotations

from dataclasses import dataclass

Q = 8380417
N = 256
D = 13  # number of dropped bits in t


@dataclass(frozen=True)
class MLDSAParams:
    name: str
    k: int
    l: int
    eta: int
    tau: int
    gamma1: int
    gamma2: int
    omega: int
    c_tilde_bytes: int       # = lambda/4
    security_category: int

    @property
    def beta(self) -> int:
        return self.tau * self.eta

    @property
    def eta_bits(self) -> int:
        return (2 * self.eta).bit_length()

    @property
    def z_bits(self) -> int:
        return (2 * self.gamma1 - 1).bit_length()

    @property
    def w1_max(self) -> int:
        return (Q - 1) // (2 * self.gamma2) - 1

    @property
    def w1_bits(self) -> int:
        return self.w1_max.bit_length()

    @property
    def pk_bytes(self) -> int:
        return 32 + 32 * 10 * self.k

    @property
    def sk_bytes(self) -> int:
        return (128
                + 32 * self.eta_bits * (self.k + self.l)
                + 32 * D * self.k)

    @property
    def sig_bytes(self) -> int:
        return (self.c_tilde_bytes
                + 32 * self.z_bits * self.l
                + self.omega + self.k)


PARAMS = {
    "ML-DSA-44": MLDSAParams("ML-DSA-44", k=4, l=4, eta=2, tau=39,
                             gamma1=1 << 17, gamma2=(Q - 1) // 88, omega=80,
                             c_tilde_bytes=32, security_category=2),
    "ML-DSA-65": MLDSAParams("ML-DSA-65", k=6, l=5, eta=4, tau=49,
                             gamma1=1 << 19, gamma2=(Q - 1) // 32, omega=55,
                             c_tilde_bytes=48, security_category=3),
    "ML-DSA-87": MLDSAParams("ML-DSA-87", k=8, l=7, eta=2, tau=60,
                             gamma1=1 << 19, gamma2=(Q - 1) // 32, omega=75,
                             c_tilde_bytes=64, security_category=5),
}
