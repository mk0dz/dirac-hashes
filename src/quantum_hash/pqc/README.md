# `quantum_hash.pqc` — post-quantum cryptography

From-scratch, **spec-correct** implementations of the NIST post-quantum standards,
each validated byte-for-byte against the official **NIST ACVP** known-answer tests.

| Module | Standard | Type | Parameter sets | KAT status |
|---|---|---|---|---|
| `ml_kem`  | FIPS 203 (ML-KEM, ex-Kyber)     | KEM       | 512 / 768 / 1024 | ✅ keyGen, encaps, decaps |
| `ml_dsa`  | FIPS 204 (ML-DSA, ex-Dilithium) | Signature | 44 / 65 / 87     | ✅ keyGen, sigGen, sigVer (all interfaces, incl. HashML-DSA) |
| `slh_dsa` | FIPS 205 (SLH-DSA, ex-SPHINCS+) | Signature | SHAKE 128/192/256 s & f | ✅ keyGen, sigVer, sigGen |

> **Research-grade, not production-hardened.** These are pure-Python and therefore
> **not constant-time** — they are correct and standards-conformant, suitable for
> research, testing, benchmarking and integration prototyping, but they are not
> side-channel resistant. Do not use them to protect real funds without an audited,
> constant-time backend. All symmetric primitives are SHAKE/SHA3 from the standard
> library, as the standards require; the library's `DiracHash` is unrelated and is
> never used inside these schemes.

## Usage

```python
import quantum_hash.pqc as pqc

# Signatures (FIPS 204)
mldsa = pqc.get_scheme("ML-DSA-65")
pk, sk = mldsa.keygen()
sig = mldsa.sign(sk, b"transfer 1 SOL", context=b"dirac-wallet")
assert mldsa.verify(pk, b"transfer 1 SOL", sig, context=b"dirac-wallet")

# Key encapsulation (FIPS 203)
kem = pqc.get_scheme("ML-KEM-768")
ek, dk = kem.keygen()
ciphertext, shared = kem.encaps(ek)
assert kem.decaps(dk, ciphertext) == shared

pqc.signature_schemes()   # -> ['ML-DSA-44', 'ML-DSA-65', ...]
pqc.kem_schemes()         # -> ['ML-KEM-512', 'ML-KEM-768', 'ML-KEM-1024']
```

Keys, ciphertexts and signatures are canonical `bytes` in the exact FIPS encodings, so
sizes are meaningful and objects interoperate with other conformant implementations.

## Layout

```
common/   shared primitives: ntt.py (Kyber + Dilithium NTTs), xof.py (SHAKE/SHA3),
          base.py (SignatureScheme / KEM ABCs + registry)
ml_kem/   params, encode/compress, samplers, K-PKE + ML-KEM (FO transform)
ml_dsa/   params, rounding/hints, bit-packing, samplers, keygen/sign/verify
slh_dsa/  params, ADRS, tweakable hashes, WOTS+/FORS/XMSS/HT, SLH-DSA
```

## Validation & benchmarking

```bash
python kat/fetch_acvp.py --all     # vendor NIST ACVP vectors (once)
pytest tests/ -m "not slow"        # all KATs except the slow SLH-DSA 's' sigGen
pytest tests/ -m slow              # the slow ones

python bench/run.py                # measure timings + sizes -> JSON
python bench/report.py             # comparison tables + wallet pick + charts
```
