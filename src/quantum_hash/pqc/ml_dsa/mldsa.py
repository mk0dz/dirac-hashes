"""ML-DSA (FIPS 204): key generation, signing (Fiat-Shamir with aborts), verification.

The ``*_internal`` / ``sign_external_mu`` entry points expose the exact interfaces the
NIST ACVP vectors exercise (internal, external/pure, and externalMu), each taking the
randomness explicitly so signatures reproduce byte-for-byte. The public
:class:`MLDSA` implements the generic signature interface (external, pure, hedged by
default).
"""
from __future__ import annotations

import secrets

import numpy as np

from ..common.base import SignatureScheme, register
from ..common.ntt import DilithiumNTT
from ..common.xof import shake256
from . import encode as enc
from .params import D, N, PARAMS, Q
from .rounding import high_bits, inf_norm, low_bits, make_hint, use_hint
from .sample import expand_a, expand_mask, expand_s, sample_in_ball

_NTT = DilithiumNTT()
_ZERO = lambda: np.zeros(N, dtype=np.int64)  # noqa: E731


def _center(p: np.ndarray) -> np.ndarray:
    c = p % Q
    return np.where(c > (Q - 1) // 2, c - Q, c)


class MLDSA(SignatureScheme):
    def __init__(self, param_set: str):
        self.p = PARAMS[param_set]
        self.name = self.p.name
        self.security_category = self.p.security_category

    @property
    def sizes(self) -> dict[str, int]:
        return {"pk": self.p.pk_bytes, "sk": self.p.sk_bytes, "sig": self.p.sig_bytes}

    # --- helpers ------------------------------------------------------------
    def _matvec(self, a_hat, v_hat):
        """Return NTT^-1(A_hat ∘ v_hat) as a list of k polynomials."""
        k, l = self.p.k, self.p.l
        out = []
        for r in range(k):
            acc = _ZERO()
            for s in range(l):
                acc = (acc + _NTT.basemul(a_hat[r][s], v_hat[s])) % Q
            out.append(_NTT.intt(acc))
        return out

    # --- key generation -----------------------------------------------------
    def keygen_internal(self, xi: bytes) -> tuple[bytes, bytes]:
        p, k, l = self.p, self.p.k, self.p.l
        h = shake256(xi + bytes([k, l]), 128)
        rho, rho_prime, key = h[:32], h[32:96], h[96:128]
        a_hat = expand_a(rho, k, l)
        s1, s2 = expand_s(rho_prime, k, l, p.eta)
        s1_hat = [_NTT.ntt(s) for s in s1]
        t = [(self._matvec(a_hat, s1_hat)[r] + s2[r]) % Q for r in range(k)]
        t1, t0 = enc.power2round_vec(t)
        pk = enc.pk_encode(rho, t1)
        tr = shake256(pk, 64)
        sk = enc.sk_encode(rho, key, tr, s1, s2, t0, p.eta)
        return pk, sk

    def keygen(self) -> tuple[bytes, bytes]:
        return self.keygen_internal(secrets.token_bytes(32))

    # --- signing ------------------------------------------------------------
    def _sign_core(self, sk: bytes, mu: bytes, rnd: bytes) -> bytes:
        p, k, l = self.p, self.p.k, self.p.l
        rho, key, _tr, s1, s2, t0 = enc.sk_decode(sk, k, l, p.eta)
        a_hat = expand_a(rho, k, l)
        s1_hat = [_NTT.ntt(s) for s in s1]
        s2_hat = [_NTT.ntt(s) for s in s2]
        t0_hat = [_NTT.ntt(s) for s in t0]
        rho_pp = shake256(key + rnd + mu, 64)

        kappa = 0
        while True:
            y = expand_mask(rho_pp, kappa, l, p.gamma1)
            kappa += l
            y_hat = [_NTT.ntt(yi) for yi in y]
            w = self._matvec(a_hat, y_hat)
            w1 = [high_bits(wi, p.gamma2) for wi in w]
            c_tilde = shake256(mu + enc.w1_encode(w1, p.w1_max), p.c_tilde_bytes)
            c_hat = _NTT.ntt(sample_in_ball(c_tilde, p.tau))
            cs1 = [_center(_NTT.intt(_NTT.basemul(c_hat, s1_hat[i]))) for i in range(l)]
            cs2 = [_center(_NTT.intt(_NTT.basemul(c_hat, s2_hat[i]))) for i in range(k)]
            z = [y[i] + cs1[i] for i in range(l)]
            r0 = [low_bits(w[i] - cs2[i], p.gamma2) for i in range(k)]
            if max(inf_norm(zi) for zi in z) >= p.gamma1 - p.beta:
                continue
            if max(inf_norm(ri) for ri in r0) >= p.gamma2 - p.beta:
                continue
            ct0 = [_center(_NTT.intt(_NTT.basemul(c_hat, t0_hat[i]))) for i in range(k)]
            if max(inf_norm(ci) for ci in ct0) >= p.gamma2:
                continue
            h = [make_hint(-ct0[i], w[i] - cs2[i] + ct0[i], p.gamma2) for i in range(k)]
            if sum(int(hi.sum()) for hi in h) > p.omega:
                continue
            return enc.sig_encode(c_tilde, [_center(zi) for zi in z], h,
                                  p.gamma1, p.omega)

    def sign_internal(self, sk: bytes, message: bytes, rnd: bytes) -> bytes:
        tr = enc.sk_decode(sk, self.p.k, self.p.l, self.p.eta)[2]
        mu = shake256(tr + message, 64)
        return self._sign_core(sk, mu, rnd)

    def sign_external_mu(self, sk: bytes, mu: bytes, rnd: bytes) -> bytes:
        return self._sign_core(sk, mu, rnd)

    @staticmethod
    def _format(message: bytes, context: bytes) -> bytes:
        if len(context) > 255:
            raise ValueError("context too long (max 255 bytes)")
        return bytes([0, len(context)]) + context + message

    def sign(self, sk: bytes, message: bytes, context: bytes = b"",
             rnd: bytes | None = None, deterministic: bool = False) -> bytes:
        if rnd is None:
            rnd = bytes(32) if deterministic else secrets.token_bytes(32)
        return self.sign_internal(sk, self._format(message, context), rnd)

    # --- verification -------------------------------------------------------
    def verify_internal(self, pk: bytes, message: bytes, sig: bytes) -> bool:
        p, k, l = self.p, self.p.k, self.p.l
        if len(sig) != p.sig_bytes or len(pk) != p.pk_bytes:
            return False
        rho, t1 = enc.pk_decode(pk, k)
        c_tilde, z, h = enc.sig_decode(sig, p)
        if h is None:
            return False
        if max(inf_norm(zi) for zi in z) >= p.gamma1 - p.beta:
            return False
        a_hat = expand_a(rho, k, l)
        tr = shake256(pk, 64)
        mu = shake256(tr + message, 64)
        c_hat = _NTT.ntt(sample_in_ball(c_tilde, p.tau))
        z_hat = [_NTT.ntt(zi) for zi in z]
        t1_hat = [_NTT.ntt((t1[i] * (1 << D)) % Q) for i in range(k)]
        w_approx = []
        for r in range(k):
            acc = _ZERO()
            for s in range(l):
                acc = (acc + _NTT.basemul(a_hat[r][s], z_hat[s])) % Q
            acc = (acc - _NTT.basemul(c_hat, t1_hat[r])) % Q
            w_approx.append(_NTT.intt(acc))
        w1 = [use_hint(h[r], w_approx[r], p.gamma2) for r in range(k)]
        c_tilde2 = shake256(mu + enc.w1_encode(w1, p.w1_max), p.c_tilde_bytes)
        return c_tilde == c_tilde2

    def verify_external_mu(self, pk: bytes, mu: bytes, sig: bytes) -> bool:
        # mu already incorporates tr; reuse the core by substituting mu for tr||M.
        return self._verify_with_mu(pk, mu, sig)

    def _verify_with_mu(self, pk: bytes, mu: bytes, sig: bytes) -> bool:
        p, k, l = self.p, self.p.k, self.p.l
        if len(sig) != p.sig_bytes or len(pk) != p.pk_bytes:
            return False
        rho, t1 = enc.pk_decode(pk, k)
        c_tilde, z, h = enc.sig_decode(sig, p)
        if h is None or max(inf_norm(zi) for zi in z) >= p.gamma1 - p.beta:
            return False
        a_hat = expand_a(rho, k, l)
        c_hat = _NTT.ntt(sample_in_ball(c_tilde, p.tau))
        z_hat = [_NTT.ntt(zi) for zi in z]
        t1_hat = [_NTT.ntt((t1[i] * (1 << D)) % Q) for i in range(k)]
        w_approx = []
        for r in range(k):
            acc = _ZERO()
            for s in range(l):
                acc = (acc + _NTT.basemul(a_hat[r][s], z_hat[s])) % Q
            acc = (acc - _NTT.basemul(c_hat, t1_hat[r])) % Q
            w_approx.append(_NTT.intt(acc))
        w1 = [use_hint(h[r], w_approx[r], p.gamma2) for r in range(k)]
        return c_tilde == shake256(mu + enc.w1_encode(w1, p.w1_max), p.c_tilde_bytes)

    def verify(self, pk: bytes, message: bytes, signature: bytes,
               context: bytes = b"") -> bool:
        try:
            return self.verify_internal(pk, self._format(message, context), signature)
        except ValueError:
            return False


ML_DSA_44 = register(MLDSA("ML-DSA-44"))
ML_DSA_65 = register(MLDSA("ML-DSA-65"))
ML_DSA_87 = register(MLDSA("ML-DSA-87"))
