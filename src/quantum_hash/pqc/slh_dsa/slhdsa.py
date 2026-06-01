"""SLH-DSA (FIPS 205): the full stateless hash-based signature scheme.

Layers, bottom to top: WOTS+ one-time signatures -> XMSS Merkle trees -> the
hypertree (HT) of d stacked XMSS trees -> FORS few-time signatures over the message
digest -> SLH-DSA. Everything is kept in one class so the shared parameters and
tweakable hashes don't have to be threaded through dozens of free functions.

Pure Python and intentionally the simple (recompute-the-subtree) variant: the 's'
parameter sets are slow to sign. Correct, not fast - optimization is a later phase.
"""
from __future__ import annotations

import secrets
from math import ceil

from ..common.base import SignatureScheme, register
from .adrs import (ADRS, FORS_PRF, FORS_ROOTS, FORS_TREE, TREE, WOTS_HASH,
                   WOTS_PK, WOTS_PRF)
from .hashes import ShakeHashes, base_2b
from .params import PARAMS


class SLHDSA(SignatureScheme):
    def __init__(self, param_set: str):
        self.p = PARAMS[param_set]
        self.name = self.p.name
        self.security_category = self.p.security_category
        self.H = ShakeHashes(self.p.n, self.p.m)

    @property
    def sizes(self) -> dict[str, int]:
        return {"pk": self.p.pk_bytes, "sk": self.p.sk_bytes, "sig": self.p.sig_bytes}

    # --- WOTS+ --------------------------------------------------------------
    def _chain(self, x: bytes, start: int, steps: int, pk_seed: bytes, adrs: ADRS) -> bytes:
        tmp = x
        for j in range(start, start + steps):
            adrs.set_hash_address(j)
            tmp = self.H.f(pk_seed, adrs, tmp)
        return tmp

    def _wots_msg(self, m: bytes) -> list[int]:
        p = self.p
        msg = base_2b(m, p.lg_w, p.len1)
        csum = sum(p.w - 1 - x for x in msg)
        csum <<= (8 - (p.len2 * p.lg_w) % 8) % 8
        csum_bytes = csum.to_bytes(ceil(p.len2 * p.lg_w / 8), "big")
        return msg + base_2b(csum_bytes, p.lg_w, p.len2)

    def _wots_pkgen(self, sk_seed: bytes, pk_seed: bytes, adrs: ADRS) -> bytes:
        sk_adrs = adrs.copy()
        sk_adrs.set_type_and_clear(WOTS_PRF)
        sk_adrs.set_key_pair_address(adrs.get_key_pair_address())
        tmp = []
        for i in range(self.p.length):
            sk_adrs.set_chain_address(i)
            sk = self.H.prf(pk_seed, sk_seed, sk_adrs)
            adrs.set_chain_address(i)
            adrs.set_hash_address(0)
            tmp.append(self._chain(sk, 0, self.p.w - 1, pk_seed, adrs))
        wotspk_adrs = adrs.copy()
        wotspk_adrs.set_type_and_clear(WOTS_PK)
        wotspk_adrs.set_key_pair_address(adrs.get_key_pair_address())
        return self.H.t(pk_seed, wotspk_adrs, b"".join(tmp))

    def _wots_sign(self, m: bytes, sk_seed: bytes, pk_seed: bytes, adrs: ADRS) -> bytes:
        msg = self._wots_msg(m)
        sk_adrs = adrs.copy()
        sk_adrs.set_type_and_clear(WOTS_PRF)
        sk_adrs.set_key_pair_address(adrs.get_key_pair_address())
        sig = []
        for i in range(self.p.length):
            sk_adrs.set_chain_address(i)
            sk = self.H.prf(pk_seed, sk_seed, sk_adrs)
            adrs.set_chain_address(i)
            adrs.set_hash_address(0)
            sig.append(self._chain(sk, 0, msg[i], pk_seed, adrs))
        return b"".join(sig)

    def _wots_pk_from_sig(self, sig: bytes, m: bytes, pk_seed: bytes, adrs: ADRS) -> bytes:
        n = self.p.n
        msg = self._wots_msg(m)
        tmp = []
        for i in range(self.p.length):
            adrs.set_chain_address(i)
            si = sig[i * n:(i + 1) * n]
            tmp.append(self._chain(si, msg[i], self.p.w - 1 - msg[i], pk_seed, adrs))
        wotspk_adrs = adrs.copy()
        wotspk_adrs.set_type_and_clear(WOTS_PK)
        wotspk_adrs.set_key_pair_address(adrs.get_key_pair_address())
        return self.H.t(pk_seed, wotspk_adrs, b"".join(tmp))

    # --- XMSS / hypertree ---------------------------------------------------
    def _xmss_node(self, sk_seed: bytes, i: int, z: int, pk_seed: bytes, adrs: ADRS) -> bytes:
        if z == 0:
            adrs.set_type_and_clear(WOTS_HASH)
            adrs.set_key_pair_address(i)
            return self._wots_pkgen(sk_seed, pk_seed, adrs)
        lnode = self._xmss_node(sk_seed, 2 * i, z - 1, pk_seed, adrs)
        rnode = self._xmss_node(sk_seed, 2 * i + 1, z - 1, pk_seed, adrs)
        adrs.set_type_and_clear(TREE)
        adrs.set_tree_height(z)
        adrs.set_tree_index(i)
        return self.H.h(pk_seed, adrs, lnode + rnode)

    def _xmss_sign(self, m: bytes, sk_seed: bytes, idx: int, pk_seed: bytes, adrs: ADRS) -> bytes:
        auth = []
        for j in range(self.p.hp):
            k = (idx >> j) ^ 1
            auth.append(self._xmss_node(sk_seed, k, j, pk_seed, adrs))
        adrs.set_type_and_clear(WOTS_HASH)
        adrs.set_key_pair_address(idx)
        sig = self._wots_sign(m, sk_seed, pk_seed, adrs)
        return sig + b"".join(auth)

    def _xmss_pk_from_sig(self, idx: int, sig: bytes, m: bytes, pk_seed: bytes, adrs: ADRS) -> bytes:
        n = self.p.n
        adrs.set_type_and_clear(WOTS_HASH)
        adrs.set_key_pair_address(idx)
        wlen = self.p.length * n
        node = self._wots_pk_from_sig(sig[:wlen], m, pk_seed, adrs)
        auth = sig[wlen:]
        adrs.set_type_and_clear(TREE)
        adrs.set_tree_index(idx)
        for j in range(self.p.hp):
            adrs.set_tree_height(j + 1)
            authj = auth[j * n:(j + 1) * n]
            if (idx >> j) & 1 == 0:
                adrs.set_tree_index(adrs.get_tree_index() // 2)
                node = self.H.h(pk_seed, adrs, node + authj)
            else:
                adrs.set_tree_index((adrs.get_tree_index() - 1) // 2)
                node = self.H.h(pk_seed, adrs, authj + node)
        return node

    def _ht_sign(self, m: bytes, sk_seed: bytes, pk_seed: bytes,
                 idx_tree: int, idx_leaf: int) -> bytes:
        hp = self.p.hp
        adrs = ADRS()
        adrs.set_tree_address(idx_tree)
        sig_tmp = self._xmss_sign(m, sk_seed, idx_leaf, pk_seed, adrs)
        out = sig_tmp
        root = self._xmss_pk_from_sig(idx_leaf, sig_tmp, m, pk_seed, adrs)
        for j in range(1, self.p.d):
            idx_leaf = idx_tree & ((1 << hp) - 1)
            idx_tree >>= hp
            adrs.set_layer_address(j)
            adrs.set_tree_address(idx_tree)
            sig_tmp = self._xmss_sign(root, sk_seed, idx_leaf, pk_seed, adrs)
            out += sig_tmp
            if j < self.p.d - 1:
                root = self._xmss_pk_from_sig(idx_leaf, sig_tmp, root, pk_seed, adrs)
        return out

    def _ht_verify(self, m: bytes, sig_ht: bytes, pk_seed: bytes,
                   idx_tree: int, idx_leaf: int, pk_root: bytes) -> bool:
        hp, n = self.p.hp, self.p.n
        xmss_len = (self.p.hp + self.p.length) * n
        adrs = ADRS()
        adrs.set_tree_address(idx_tree)
        sig0 = sig_ht[:xmss_len]
        node = self._xmss_pk_from_sig(idx_leaf, sig0, m, pk_seed, adrs)
        for j in range(1, self.p.d):
            idx_leaf = idx_tree & ((1 << hp) - 1)
            idx_tree >>= hp
            adrs.set_layer_address(j)
            adrs.set_tree_address(idx_tree)
            sigj = sig_ht[j * xmss_len:(j + 1) * xmss_len]
            node = self._xmss_pk_from_sig(idx_leaf, sigj, node, pk_seed, adrs)
        return node == pk_root

    # --- FORS ---------------------------------------------------------------
    def _fors_skgen(self, sk_seed: bytes, pk_seed: bytes, adrs: ADRS, idx: int) -> bytes:
        sk_adrs = adrs.copy()
        sk_adrs.set_type_and_clear(FORS_PRF)
        sk_adrs.set_key_pair_address(adrs.get_key_pair_address())
        sk_adrs.set_tree_index(idx)
        return self.H.prf(pk_seed, sk_seed, sk_adrs)

    def _fors_node(self, sk_seed: bytes, i: int, z: int, pk_seed: bytes, adrs: ADRS) -> bytes:
        if z == 0:
            sk = self._fors_skgen(sk_seed, pk_seed, adrs, i)
            adrs.set_tree_height(0)
            adrs.set_tree_index(i)
            return self.H.f(pk_seed, adrs, sk)
        lnode = self._fors_node(sk_seed, 2 * i, z - 1, pk_seed, adrs)
        rnode = self._fors_node(sk_seed, 2 * i + 1, z - 1, pk_seed, adrs)
        adrs.set_tree_height(z)
        adrs.set_tree_index(i)
        return self.H.h(pk_seed, adrs, lnode + rnode)

    def _fors_sign(self, md: bytes, sk_seed: bytes, pk_seed: bytes, adrs: ADRS) -> bytes:
        p = self.p
        indices = base_2b(md, p.a, p.k)
        out = []
        for i in range(p.k):
            idx = indices[i]
            out.append(self._fors_skgen(sk_seed, pk_seed, adrs, (i << p.a) + idx))
            for j in range(p.a):
                s = (idx >> j) ^ 1
                out.append(self._fors_node(sk_seed, (i << (p.a - j)) + s, j, pk_seed, adrs))
        return b"".join(out)

    def _fors_pk_from_sig(self, sig: bytes, md: bytes, pk_seed: bytes, adrs: ADRS) -> bytes:
        p, n = self.p, self.p.n
        indices = base_2b(md, p.a, p.k)
        roots = []
        off = 0
        for i in range(p.k):
            idx = indices[i]
            sk = sig[off:off + n]
            off += n
            adrs.set_tree_height(0)
            adrs.set_tree_index((i << p.a) + idx)
            node = self.H.f(pk_seed, adrs, sk)
            for j in range(p.a):
                authj = sig[off:off + n]
                off += n
                adrs.set_tree_height(j + 1)
                if (idx >> j) & 1 == 0:
                    adrs.set_tree_index(adrs.get_tree_index() // 2)
                    node = self.H.h(pk_seed, adrs, node + authj)
                else:
                    adrs.set_tree_index((adrs.get_tree_index() - 1) // 2)
                    node = self.H.h(pk_seed, adrs, authj + node)
            roots.append(node)
        forspk_adrs = adrs.copy()
        forspk_adrs.set_type_and_clear(FORS_ROOTS)
        forspk_adrs.set_key_pair_address(adrs.get_key_pair_address())
        return self.H.t(pk_seed, forspk_adrs, b"".join(roots))

    # --- top level ----------------------------------------------------------
    def keygen_internal(self, sk_seed: bytes, sk_prf: bytes, pk_seed: bytes) -> tuple[bytes, bytes]:
        adrs = ADRS()
        adrs.set_layer_address(self.p.d - 1)
        pk_root = self._xmss_node(sk_seed, 0, self.p.hp, pk_seed, adrs)
        pk = pk_seed + pk_root
        sk = sk_seed + sk_prf + pk_seed + pk_root
        return pk, sk

    def keygen(self) -> tuple[bytes, bytes]:
        n = self.p.n
        return self.keygen_internal(secrets.token_bytes(n), secrets.token_bytes(n),
                                    secrets.token_bytes(n))

    def _digest_indices(self, digest: bytes) -> tuple[bytes, int, int]:
        p = self.p
        ka, tb, lb = p.ka_bytes, p.tree_bytes, p.leaf_bytes
        md = digest[:ka]
        idx_tree = int.from_bytes(digest[ka:ka + tb], "big") % (1 << (p.h - p.hp))
        idx_leaf = int.from_bytes(digest[ka + tb:ka + tb + lb], "big") % (1 << p.hp)
        return md, idx_tree, idx_leaf

    def sign_internal(self, message: bytes, sk: bytes, addrnd: bytes) -> bytes:
        n = self.p.n
        sk_seed, sk_prf, pk_seed, pk_root = sk[:n], sk[n:2 * n], sk[2 * n:3 * n], sk[3 * n:4 * n]
        r = self.H.prf_msg(sk_prf, addrnd, message)
        digest = self.H.h_msg(r, pk_seed, pk_root, message)
        md, idx_tree, idx_leaf = self._digest_indices(digest)
        adrs = ADRS()
        adrs.set_tree_address(idx_tree)
        adrs.set_type_and_clear(FORS_TREE)
        adrs.set_key_pair_address(idx_leaf)
        sig_fors = self._fors_sign(md, sk_seed, pk_seed, adrs)
        pk_fors = self._fors_pk_from_sig(sig_fors, md, pk_seed, adrs)
        sig_ht = self._ht_sign(pk_fors, sk_seed, pk_seed, idx_tree, idx_leaf)
        return r + sig_fors + sig_ht

    def verify_internal(self, message: bytes, sig: bytes, pk: bytes) -> bool:
        p, n = self.p, self.p.n
        if len(sig) != p.sig_bytes or len(pk) != p.pk_bytes:
            return False
        pk_seed, pk_root = pk[:n], pk[n:2 * n]
        r = sig[:n]
        sig_fors = sig[n:n + p.fors_bytes]
        sig_ht = sig[n + p.fors_bytes:]
        digest = self.H.h_msg(r, pk_seed, pk_root, message)
        md, idx_tree, idx_leaf = self._digest_indices(digest)
        adrs = ADRS()
        adrs.set_tree_address(idx_tree)
        adrs.set_type_and_clear(FORS_TREE)
        adrs.set_key_pair_address(idx_leaf)
        pk_fors = self._fors_pk_from_sig(sig_fors, md, pk_seed, adrs)
        return self._ht_verify(pk_fors, sig_ht, pk_seed, idx_tree, idx_leaf, pk_root)

    @staticmethod
    def _format(message: bytes, context: bytes) -> bytes:
        if len(context) > 255:
            raise ValueError("context too long (max 255 bytes)")
        return bytes([0, len(context)]) + context + message

    def sign(self, sk: bytes, message: bytes, context: bytes = b"",
             addrnd: bytes | None = None, deterministic: bool = False) -> bytes:
        pk_seed = sk[2 * self.p.n:3 * self.p.n]
        if addrnd is None:
            addrnd = pk_seed if deterministic else secrets.token_bytes(self.p.n)
        return self.sign_internal(self._format(message, context), sk, addrnd)

    def verify(self, pk: bytes, message: bytes, signature: bytes,
               context: bytes = b"") -> bool:
        try:
            return self.verify_internal(self._format(message, context), signature, pk)
        except ValueError:
            return False


_SCHEMES = [register(SLHDSA(name)) for name in PARAMS]
