"""Abstract interfaces and a registry shared by every PQC scheme.

All public operations take and return ``bytes`` in the canonical FIPS encodings, so
that schemes are interchangeable, sizes are meaningful, and known-answer tests can be
compared byte-for-byte. A single registry lets the benchmark harness and the wallet
enumerate schemes by their standard names (``"ML-KEM-768"``, ``"ML-DSA-65"``, ...).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class _Scheme(ABC):
    """Common metadata for KEMs and signature schemes."""

    #: Canonical name, e.g. ``"ML-DSA-65"``.
    name: str = ""
    #: NIST security category (1-5).
    security_category: int = 0

    @property
    @abstractmethod
    def sizes(self) -> dict[str, int]:
        """Byte sizes of the scheme's objects (keys, ciphertext/signature)."""

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{type(self).__name__} {self.name}>"


class KEM(_Scheme):
    """Key-encapsulation mechanism (FIPS 203 shape)."""

    @abstractmethod
    def keygen(self) -> tuple[bytes, bytes]:
        """Return ``(ek, dk)`` - encapsulation (public) and decapsulation (secret) keys."""

    @abstractmethod
    def encaps(self, ek: bytes) -> tuple[bytes, bytes]:
        """Return ``(ciphertext, shared_secret)`` for the given encapsulation key."""

    @abstractmethod
    def decaps(self, dk: bytes, ciphertext: bytes) -> bytes:
        """Return the shared secret recovered from ``ciphertext``."""


class SignatureScheme(_Scheme):
    """Digital signature scheme (FIPS 204 / 205 shape)."""

    @abstractmethod
    def keygen(self) -> tuple[bytes, bytes]:
        """Return ``(pk, sk)`` - public and secret keys."""

    @abstractmethod
    def sign(self, sk: bytes, message: bytes, context: bytes = b"") -> bytes:
        """Return a signature over ``message`` (with optional ``context``)."""

    @abstractmethod
    def verify(self, pk: bytes, message: bytes, signature: bytes,
               context: bytes = b"") -> bool:
        """Return whether ``signature`` is valid for ``message`` under ``pk``."""


# --- registry ---------------------------------------------------------------
_REGISTRY: dict[str, _Scheme] = {}


def register(scheme: _Scheme) -> _Scheme:
    """Register a scheme instance under its canonical ``name`` and return it."""
    if not scheme.name:
        raise ValueError("scheme must define a non-empty name")
    _REGISTRY[scheme.name] = scheme
    return scheme


def get_scheme(name: str) -> _Scheme:
    """Look up a registered scheme by canonical name."""
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"unknown scheme {name!r}; registered: {sorted(_REGISTRY)}"
        ) from None


def list_schemes(kind: Callable[[_Scheme], bool] | None = None) -> list[str]:
    """Return registered scheme names, optionally filtered by a predicate."""
    names = sorted(_REGISTRY)
    if kind is None:
        return names
    return [n for n in names if kind(_REGISTRY[n])]
