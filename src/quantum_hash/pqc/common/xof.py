"""SHAKE / SHA3 primitives shared by the lattice and hash-based schemes.

These are thin wrappers over the standard library ``hashlib`` SHA-3 family, which is
exactly what FIPS 203/204/205 mandate. Two things the standards need that
``hashlib`` does not offer directly are provided here:

* :class:`SHAKEReader` - an incremental squeeze interface, required by rejection
  sampling (``SampleNTT`` etc.) where the number of output bytes is not known ahead
  of time.
* Named helpers (:func:`H`, :func:`G`, :func:`J`, :func:`prf`) matching the FIPS 203
  notation so the scheme code reads like the spec.
"""
from __future__ import annotations

import hashlib

# SHA-3 sponge rates (bytes) = (1600 - 2*capacity)/8. Used as the squeeze block size.
SHAKE128_RATE = 168
SHAKE256_RATE = 136


def shake128(data: bytes, length: int) -> bytes:
    """SHAKE128(data) truncated to ``length`` bytes."""
    return hashlib.shake_128(data).digest(length)


def shake256(data: bytes, length: int) -> bytes:
    """SHAKE256(data) truncated to ``length`` bytes."""
    return hashlib.shake_256(data).digest(length)


def sha3_256(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def sha3_512(data: bytes) -> bytes:
    return hashlib.sha3_512(data).digest()


# --- FIPS 203 named functions ------------------------------------------------
def H(data: bytes) -> bytes:
    """ML-KEM H := SHA3-256."""
    return hashlib.sha3_256(data).digest()


def J(data: bytes) -> bytes:
    """ML-KEM J := SHAKE256(., 32) (implicit-rejection shared secret)."""
    return hashlib.shake_256(data).digest(32)


def G(data: bytes) -> tuple[bytes, bytes]:
    """ML-KEM G := SHA3-512, split into two 32-byte halves."""
    digest = hashlib.sha3_512(data).digest()
    return digest[:32], digest[32:]


def prf(eta: int, data: bytes, nonce: int) -> bytes:
    """ML-KEM PRF_eta(s, b) := SHAKE256(s || b, 64*eta)."""
    return hashlib.shake_256(data + bytes([nonce])).digest(64 * eta)


class SHAKEReader:
    """Incremental SHAKE squeeze.

    ``hashlib`` only exposes a one-shot ``digest(n)``. Since SHAKE is a stream
    (``digest(n)`` returns the first ``n`` bytes and ``digest(m>n)`` extends it), we
    lazily re-squeeze in rate-sized blocks as more bytes are requested. The amounts
    involved (a few hundred bytes during rejection sampling) make the recompute cost
    negligible.
    """

    def __init__(self, data: bytes, bits: int = 128):
        if bits == 128:
            self._x = hashlib.shake_128(data)
            self._block = SHAKE128_RATE
        elif bits == 256:
            self._x = hashlib.shake_256(data)
            self._block = SHAKE256_RATE
        else:  # pragma: no cover - guards programmer error
            raise ValueError("SHAKE width must be 128 or 256")
        self._buf = b""
        self._pos = 0

    def read(self, n: int) -> bytes:
        """Return the next ``n`` bytes of the squeezed stream."""
        while self._pos + n > len(self._buf):
            new_len = len(self._buf) + self._block
            self._buf = self._x.digest(new_len)
        out = self._buf[self._pos:self._pos + n]
        self._pos += n
        return out
