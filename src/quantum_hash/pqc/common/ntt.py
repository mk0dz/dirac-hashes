"""Number-Theoretic Transforms for the lattice schemes.

Both ML-KEM and ML-DSA work in the ring Z_q[X]/(X^256 + 1), but with different moduli
and transform structure:

* **ML-KEM** (q = 3329): q ≡ 1 (mod 256) but not (mod 512), so X^256+1 only factors
  into 128 quadratics. The NTT is *incomplete* - it runs 7 layers down to length-2
  blocks and pointwise multiplication is a degree-1 product modulo X^2 - ζ^(2·br(i)+1).

* **ML-DSA** (q = 8380417): q ≡ 1 (mod 512), so X^256+1 splits completely into 256
  linear factors. The NTT is *complete* - 8 layers down to length-1 and pointwise
  multiplication is coordinatewise.

Both share the same Cooley-Tukey (forward) / Gentleman-Sande (inverse) butterfly
network with a single positive ``zeta`` power table, exactly as FIPS 203 Algorithms
9/10 and FIPS 204 Algorithms 41/42 specify. The only differences are the modulus,
the bit-reversal width, where the layers stop, and the basecase multiply.

Arithmetic uses numpy ``int64``: the largest intermediate is ζ·v < q² < 2^46, well
within int64, so a single ``% q`` after each butterfly is exact. (Montgomery/Barrett
reduction is a Phase-6 optimization; correctness here does not depend on it.)
"""
from __future__ import annotations

import numpy as np

N = 256


def _bitrev(x: int, bits: int) -> int:
    r = 0
    for _ in range(bits):
        r = (r << 1) | (x & 1)
        x >>= 1
    return r


class _NegacyclicNTT:
    """Shared CT/GS butterfly engine over Z_q[X]/(X^256+1)."""

    def __init__(self, q: int, zeta: int, bits: int, stop_len: int):
        self.q = q
        self.stop_len = stop_len
        # zetas[i] = zeta^BitRev_bits(i) mod q, the table used by both CT and GS.
        self.zetas = np.array(
            [pow(zeta, _bitrev(i, bits), q) for i in range(N // 2 if bits == 7 else N)],
            dtype=np.int64,
        )
        self.n_zetas = len(self.zetas)
        self.n_inv = pow(N // stop_len, q - 2, q)  # 128^-1 (KEM) or 256^-1 (DSA)

    def ntt(self, poly: np.ndarray) -> np.ndarray:
        """Forward NTT (Cooley-Tukey). Returns a new array; input untouched."""
        q = self.q
        f = np.asarray(poly, dtype=np.int64).copy()
        i = 1
        length = 128
        while length >= self.stop_len:
            for start in range(0, N, 2 * length):
                z = int(self.zetas[i])
                i += 1
                u = f[start:start + length].copy()
                v = f[start + length:start + 2 * length].copy()
                t = (z * v) % q
                f[start:start + length] = (u + t) % q
                f[start + length:start + 2 * length] = (u - t) % q
            length //= 2
        return f

    def intt(self, poly: np.ndarray) -> np.ndarray:
        """Inverse NTT (Gentleman-Sande) including the 1/n scaling."""
        q = self.q
        f = np.asarray(poly, dtype=np.int64).copy()
        i = self.n_zetas - 1
        length = self.stop_len
        while length <= 128:
            for start in range(0, N, 2 * length):
                z = int(self.zetas[i])
                i -= 1
                u = f[start:start + length].copy()
                v = f[start + length:start + 2 * length].copy()
                f[start:start + length] = (u + v) % q
                f[start + length:start + 2 * length] = (z * (v - u)) % q
            length *= 2
        return (f * self.n_inv) % q


class KyberNTT(_NegacyclicNTT):
    """Incomplete NTT for ML-KEM (FIPS 203), q = 3329, zeta = 17."""

    Q = 3329
    ZETA = 17

    def __init__(self):
        super().__init__(self.Q, self.ZETA, bits=7, stop_len=2)
        # gammas[i] = zeta^(2*BitRev7(i)+1) for the degree-2 basecase products.
        self.gammas = np.array(
            [pow(self.ZETA, 2 * _bitrev(i, 7) + 1, self.Q) for i in range(N // 2)],
            dtype=np.int64,
        )

    def basemul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Pointwise multiply two NTT-domain polynomials (128 degree-1 products)."""
        q = self.Q
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        a0, a1 = a[0::2], a[1::2]
        b0, b1 = b[0::2], b[1::2]
        c0 = (a0 * b0 + (a1 * b1) % q * self.gammas) % q
        c1 = (a0 * b1 + a1 * b0) % q
        out = np.empty(N, dtype=np.int64)
        out[0::2] = c0
        out[1::2] = c1
        return out


class DilithiumNTT(_NegacyclicNTT):
    """Complete NTT for ML-DSA (FIPS 204), q = 8380417, zeta = 1753."""

    Q = 8380417
    ZETA = 1753

    def __init__(self):
        super().__init__(self.Q, self.ZETA, bits=8, stop_len=1)

    def basemul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Pointwise multiply (coordinatewise, since the NTT is complete)."""
        a = np.asarray(a, dtype=np.int64)
        b = np.asarray(b, dtype=np.int64)
        return (a * b) % self.Q
