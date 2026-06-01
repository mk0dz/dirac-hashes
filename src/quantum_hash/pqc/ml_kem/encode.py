"""Byte (de)serialization and compression for ML-KEM (FIPS 203 §4.2).

Polynomials are length-256 numpy ``int64`` arrays. ``byte_encode``/``byte_decode``
implement Algorithms 5/6 (little-endian d-bit packing); ``compress``/``decompress``
implement the rounding maps of equations (4.7)/(4.8).
"""
from __future__ import annotations

import numpy as np

from .params import N, Q


def byte_encode(d: int, poly: np.ndarray) -> bytes:
    """Pack 256 d-bit integers little-endian into 32*d bytes (Algorithm 5)."""
    arr = np.asarray(poly, dtype=np.int64)
    bits = ((arr[:, None] >> np.arange(d, dtype=np.int64)) & 1).astype(np.uint8)
    return np.packbits(bits.reshape(-1), bitorder="little").tobytes()


def byte_decode(d: int, data: bytes, modulus: int | None = None) -> np.ndarray:
    """Unpack 32*d bytes into 256 d-bit integers (Algorithm 6).

    For d == 12 the decoded values are reduced mod q (``modulus`` defaults to q
    there, 2^d otherwise) so malformed inputs fold into range, per the spec.
    """
    if modulus is None:
        modulus = Q if d == 12 else (1 << d)
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="little")
    bits = bits[: N * d].reshape(N, d).astype(np.int64)
    weights = (np.int64(1) << np.arange(d, dtype=np.int64))
    vals = (bits * weights).sum(axis=1)
    return vals % modulus


def compress(d: int, poly: np.ndarray) -> np.ndarray:
    """Compress_d: round(2^d / q * x) mod 2^d (eq. 4.7)."""
    x = np.asarray(poly, dtype=np.int64)
    return (((x << (d + 1)) + Q) // (2 * Q)) & ((1 << d) - 1)


def decompress(d: int, poly: np.ndarray) -> np.ndarray:
    """Decompress_d: round(q / 2^d * y) (eq. 4.8)."""
    y = np.asarray(poly, dtype=np.int64)
    return (Q * y + (1 << (d - 1))) >> d


def encode_vector(d: int, vec: list[np.ndarray]) -> bytes:
    return b"".join(byte_encode(d, p) for p in vec)


def decode_vector(d: int, data: bytes, k: int, modulus: int | None = None) -> list[np.ndarray]:
    step = 32 * d
    return [byte_decode(d, data[i * step:(i + 1) * step], modulus) for i in range(k)]
