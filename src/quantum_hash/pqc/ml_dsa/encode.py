"""Bit-packing and key/signature (de)serialization for ML-DSA (FIPS 204 §7.1-7.2).

Polynomials are length-256 numpy ``int64`` arrays. ``simple_bit_pack`` handles
non-negative coefficients; ``bit_pack`` handles signed coefficients in ``[-a, b]`` by
storing ``b - w``. The hint encoders implement Algorithms 20/21 with the validation
that makes malformed signatures fail closed.
"""
from __future__ import annotations

import numpy as np

from .params import D, N
from .rounding import power2round


def _pack_bits(arr: np.ndarray, width: int) -> bytes:
    arr = np.asarray(arr, dtype=np.int64)
    bits = ((arr[:, None] >> np.arange(width, dtype=np.int64)) & 1).astype(np.uint8)
    return np.packbits(bits.reshape(-1), bitorder="little").tobytes()


def _unpack_bits(data: bytes, width: int) -> np.ndarray:
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="little")
    bits = bits[: N * width].reshape(N, width).astype(np.int64)
    weights = np.int64(1) << np.arange(width, dtype=np.int64)
    return (bits * weights).sum(axis=1)


def simple_bit_pack(w: np.ndarray, b: int) -> bytes:
    """Pack coefficients in [0, b] (Algorithm 16)."""
    return _pack_bits(w, b.bit_length())


def simple_bit_unpack(data: bytes, b: int) -> np.ndarray:
    """Inverse of :func:`simple_bit_pack` (Algorithm 18)."""
    return _unpack_bits(data, b.bit_length())


def bit_pack(w: np.ndarray, a: int, b: int) -> bytes:
    """Pack coefficients in [-a, b] as (b - w) (Algorithm 17)."""
    return _pack_bits(b - np.asarray(w, dtype=np.int64), (a + b).bit_length())


def bit_unpack(data: bytes, a: int, b: int) -> np.ndarray:
    """Inverse of :func:`bit_pack`: returns b - z (Algorithm 19)."""
    return b - _unpack_bits(data, (a + b).bit_length())


# --- public key -------------------------------------------------------------
def pk_encode(rho: bytes, t1: list[np.ndarray]) -> bytes:
    return rho + b"".join(simple_bit_pack(p, (1 << 10) - 1) for p in t1)


def pk_decode(pk: bytes, k: int) -> tuple[bytes, list[np.ndarray]]:
    rho = pk[:32]
    step = 32 * 10
    t1 = [simple_bit_unpack(pk[32 + i * step:32 + (i + 1) * step], (1 << 10) - 1)
          for i in range(k)]
    return rho, t1


# --- secret key -------------------------------------------------------------
def sk_encode(rho: bytes, key: bytes, tr: bytes,
              s1: list[np.ndarray], s2: list[np.ndarray], t0: list[np.ndarray],
              eta: int) -> bytes:
    out = [rho, key, tr]
    out += [bit_pack(p, eta, eta) for p in s1]
    out += [bit_pack(p, eta, eta) for p in s2]
    out += [bit_pack(p, (1 << (D - 1)) - 1, 1 << (D - 1)) for p in t0]
    return b"".join(out)


def sk_decode(sk: bytes, k: int, l: int, eta: int):
    rho, key, tr = sk[:32], sk[32:64], sk[64:128]
    off = 128
    es = 32 * (2 * eta).bit_length()
    s1 = [bit_unpack(sk[off + i * es:off + (i + 1) * es], eta, eta) for i in range(l)]
    off += l * es
    s2 = [bit_unpack(sk[off + i * es:off + (i + 1) * es], eta, eta) for i in range(k)]
    off += k * es
    ts = 32 * D
    a = (1 << (D - 1)) - 1
    b = 1 << (D - 1)
    t0 = [bit_unpack(sk[off + i * ts:off + (i + 1) * ts], a, b) for i in range(k)]
    return rho, key, tr, s1, s2, t0


def power2round_vec(t: list[np.ndarray]) -> tuple[list[np.ndarray], list[np.ndarray]]:
    t1, t0 = [], []
    for ti in t:
        a, b = power2round(ti)
        t1.append(a)
        t0.append(b)
    return t1, t0


# --- signature --------------------------------------------------------------
def sig_encode(c_tilde: bytes, z: list[np.ndarray], h: list[np.ndarray],
               gamma1: int, omega: int) -> bytes:
    out = [c_tilde]
    out += [bit_pack(p, gamma1 - 1, gamma1) for p in z]
    out.append(hint_bit_pack(h, omega))
    return b"".join(out)


def sig_decode(sig: bytes, params):
    k, l, gamma1, omega = params.k, params.l, params.gamma1, params.omega
    ct = params.c_tilde_bytes
    c_tilde = sig[:ct]
    off = ct
    zs = 32 * (2 * gamma1 - 1).bit_length()
    z = [bit_unpack(sig[off + i * zs:off + (i + 1) * zs], gamma1 - 1, gamma1)
         for i in range(l)]
    off += l * zs
    h = hint_bit_unpack(sig[off:off + omega + k], k, omega)
    return c_tilde, z, h


def hint_bit_pack(h: list[np.ndarray], omega: int) -> bytes:
    k = len(h)
    y = bytearray(omega + k)
    index = 0
    for i in range(k):
        for j in range(N):
            if h[i][j] != 0:
                y[index] = j
                index += 1
        y[omega + i] = index
    return bytes(y)


def hint_bit_unpack(data: bytes, k: int, omega: int) -> list[np.ndarray] | None:
    h = [np.zeros(N, dtype=np.int64) for _ in range(k)]
    index = 0
    for i in range(k):
        end = data[omega + i]
        if end < index or end > omega:
            return None
        first = index
        while index < end:
            if index > first and data[index - 1] >= data[index]:
                return None  # indices must be strictly increasing
            h[i][data[index]] = 1
            index += 1
    for j in range(index, omega):
        if data[j] != 0:
            return None  # padding must be zero
    return h


def w1_encode(w1: list[np.ndarray], w1_max: int) -> bytes:
    return b"".join(simple_bit_pack(p, w1_max) for p in w1)
