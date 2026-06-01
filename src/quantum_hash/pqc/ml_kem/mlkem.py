"""ML-KEM (FIPS 203): K-PKE + the ML-KEM Fujisaki-Okamoto transform.

The public :class:`MLKEM` implements the :class:`~quantum_hash.pqc.common.base.KEM`
interface with fresh randomness. The ``*_internal`` methods take the randomness
explicitly so they can be checked byte-for-byte against the NIST ACVP vectors.
"""
from __future__ import annotations

import secrets

import numpy as np

from ..common.base import KEM, register
from ..common.ntt import KyberNTT
from ..common.xof import G, H, J, prf
from . import encode as enc
from .params import N, PARAMS, Q
from .sample import sample_cbd, sample_ntt

_NTT = KyberNTT()


def _add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a + b) % Q


class MLKEM(KEM):
    def __init__(self, param_set: str):
        self.p = PARAMS[param_set]
        self.name = self.p.name
        self.security_category = self.p.security_category

    @property
    def sizes(self) -> dict[str, int]:
        return {"ek": self.p.ek_bytes, "dk": self.p.dk_bytes, "ct": self.p.ct_bytes}

    # --- matrix expansion ---------------------------------------------------
    def _expand_a(self, rho: bytes) -> list[list[np.ndarray]]:
        k = self.p.k
        return [[sample_ntt(rho, j, i) for j in range(k)] for i in range(k)]

    # --- K-PKE --------------------------------------------------------------
    def _kpke_keygen(self, d: bytes) -> tuple[bytes, bytes]:
        k, p = self.p.k, self.p
        rho, sigma = G(d + bytes([k]))
        a_hat = self._expand_a(rho)
        nonce = 0
        s = []
        for _ in range(k):
            s.append(sample_cbd(p.eta1, prf(p.eta1, sigma, nonce)))
            nonce += 1
        e = []
        for _ in range(k):
            e.append(sample_cbd(p.eta1, prf(p.eta1, sigma, nonce)))
            nonce += 1
        s_hat = [_NTT.ntt(si) for si in s]
        e_hat = [_NTT.ntt(ei) for ei in e]
        t_hat = []
        for i in range(k):
            acc = np.zeros(N, dtype=np.int64)
            for j in range(k):
                acc = _add(acc, _NTT.basemul(a_hat[i][j], s_hat[j]))
            t_hat.append(_add(acc, e_hat[i]))
        ek = enc.encode_vector(12, t_hat) + rho
        dk = enc.encode_vector(12, s_hat)
        return ek, dk

    def _kpke_encrypt(self, ek: bytes, m: bytes, r: bytes) -> bytes:
        k, p = self.p.k, self.p
        t_hat = enc.decode_vector(12, ek[: 384 * k], k, modulus=Q)
        rho = ek[384 * k: 384 * k + 32]
        a_hat = self._expand_a(rho)
        nonce = 0
        rvec = []
        for _ in range(k):
            rvec.append(sample_cbd(p.eta1, prf(p.eta1, r, nonce)))
            nonce += 1
        e1 = []
        for _ in range(k):
            e1.append(sample_cbd(p.eta2, prf(p.eta2, r, nonce)))
            nonce += 1
        e2 = sample_cbd(p.eta2, prf(p.eta2, r, nonce))
        r_hat = [_NTT.ntt(ri) for ri in rvec]
        # u = NTT^-1(A^T ∘ r_hat) + e1
        u = []
        for i in range(k):
            acc = np.zeros(N, dtype=np.int64)
            for j in range(k):
                acc = _add(acc, _NTT.basemul(a_hat[j][i], r_hat[j]))
            u.append(_add(_NTT.intt(acc), e1[i]))
        # v = NTT^-1(t_hat^T ∘ r_hat) + e2 + Decompress1(Decode1(m))
        acc = np.zeros(N, dtype=np.int64)
        for i in range(k):
            acc = _add(acc, _NTT.basemul(t_hat[i], r_hat[i]))
        mu = enc.decompress(1, enc.byte_decode(1, m))
        v = _add(_add(_NTT.intt(acc), e2), mu)
        c1 = b"".join(enc.byte_encode(p.du, enc.compress(p.du, ui)) for ui in u)
        c2 = enc.byte_encode(p.dv, enc.compress(p.dv, v))
        return c1 + c2

    def _kpke_decrypt(self, dk: bytes, c: bytes) -> bytes:
        k, p = self.p.k, self.p
        c1_len = 32 * p.du * k
        u = [enc.decompress(p.du, ui)
             for ui in enc.decode_vector(p.du, c[:c1_len], k)]
        v = enc.decompress(p.dv, enc.byte_decode(p.dv, c[c1_len:]))
        s_hat = enc.decode_vector(12, dk, k, modulus=Q)
        acc = np.zeros(N, dtype=np.int64)
        for i in range(k):
            acc = _add(acc, _NTT.basemul(s_hat[i], _NTT.ntt(u[i])))
        w = (v - _NTT.intt(acc)) % Q
        return enc.byte_encode(1, enc.compress(1, w))

    # --- ML-KEM internals (derandomized; used by KATs) ----------------------
    def keygen_internal(self, d: bytes, z: bytes) -> tuple[bytes, bytes]:
        ek, dk_pke = self._kpke_keygen(d)
        dk = dk_pke + ek + H(ek) + z
        return ek, dk

    def encaps_internal(self, ek: bytes, m: bytes) -> tuple[bytes, bytes]:
        """Derandomized encapsulation. Returns ``(ciphertext, shared_secret)``."""
        shared, r = G(m + H(ek))
        c = self._kpke_encrypt(ek, m, r)
        return c, shared

    def decaps_internal(self, dk: bytes, c: bytes) -> bytes:
        k = self.p.k
        dk_pke = dk[: 384 * k]
        ek = dk[384 * k: 768 * k + 32]
        h = dk[768 * k + 32: 768 * k + 64]
        z = dk[768 * k + 64: 768 * k + 96]
        m2 = self._kpke_decrypt(dk_pke, c)
        shared2, r2 = G(m2 + h)
        c2 = self._kpke_encrypt(ek, m2, r2)
        # Implicit rejection: constant in spirit (compare full ciphertexts).
        if c != c2:
            shared2 = J(z + c)
        return shared2

    # --- KEM interface (fresh randomness) -----------------------------------
    def keygen(self) -> tuple[bytes, bytes]:
        return self.keygen_internal(secrets.token_bytes(32), secrets.token_bytes(32))

    def encaps(self, ek: bytes) -> tuple[bytes, bytes]:
        if len(ek) != self.p.ek_bytes:
            raise ValueError(f"bad ek length {len(ek)} for {self.name}")
        return self.encaps_internal(ek, secrets.token_bytes(32))

    def decaps(self, dk: bytes, ciphertext: bytes) -> bytes:
        if len(dk) != self.p.dk_bytes:
            raise ValueError(f"bad dk length {len(dk)} for {self.name}")
        if len(ciphertext) != self.p.ct_bytes:
            raise ValueError(f"bad ciphertext length {len(ciphertext)} for {self.name}")
        return self.decaps_internal(dk, ciphertext)


ML_KEM_512 = register(MLKEM("ML-KEM-512"))
ML_KEM_768 = register(MLKEM("ML-KEM-768"))
ML_KEM_1024 = register(MLKEM("ML-KEM-1024"))
