"""ML-KEM parameter sets (FIPS 203, Table 2)."""
from __future__ import annotations

from dataclasses import dataclass

Q = 3329
N = 256


@dataclass(frozen=True)
class MLKEMParams:
    name: str
    k: int          # module rank (number of polynomials per vector)
    eta1: int       # CBD parameter for the secret/randomness vectors
    eta2: int       # CBD parameter for the error terms
    du: int         # compression bits for u
    dv: int         # compression bits for v
    security_category: int

    @property
    def ek_bytes(self) -> int:
        return 384 * self.k + 32

    @property
    def dk_bytes(self) -> int:
        return 768 * self.k + 96

    @property
    def ct_bytes(self) -> int:
        return 32 * (self.du * self.k + self.dv)


PARAMS = {
    "ML-KEM-512": MLKEMParams("ML-KEM-512", k=2, eta1=3, eta2=2, du=10, dv=4,
                              security_category=1),
    "ML-KEM-768": MLKEMParams("ML-KEM-768", k=3, eta1=2, eta2=2, du=10, dv=4,
                              security_category=3),
    "ML-KEM-1024": MLKEMParams("ML-KEM-1024", k=4, eta1=2, eta2=2, du=11, dv=5,
                               security_category=5),
}
