"""Phase 1: the SHAKE/SHA3 wrappers and the incremental squeeze reader behave."""
import hashlib

from quantum_hash.pqc.common import xof

# NIST SHAKE known answers for the empty message, first 32 bytes.
SHAKE128_EMPTY = bytes.fromhex(
    "7f9c2ba4e88f827d616045507605853ed73b8093f6efbc88eb1a6eacfa66ef26"
)
SHAKE256_EMPTY = bytes.fromhex(
    "46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f"
)


def test_shake_known_answers():
    assert xof.shake128(b"", 32) == SHAKE128_EMPTY
    assert xof.shake256(b"", 32) == SHAKE256_EMPTY


def test_g_splits_sha3_512():
    a, b = xof.G(b"dirac")
    full = hashlib.sha3_512(b"dirac").digest()
    assert a == full[:32] and b == full[32:]
    assert xof.H(b"dirac") == hashlib.sha3_256(b"dirac").digest()


def test_prf_shape():
    out = xof.prf(3, b"\x00" * 32, 7)
    assert out == hashlib.shake_256(b"\x00" * 32 + bytes([7])).digest(64 * 3)


def test_shake_reader_matches_oneshot_in_arbitrary_chunks():
    data = b"the quantum brown fox"
    for bits in (128, 256):
        reader = xof.SHAKEReader(data, bits=bits)
        # Read 200 bytes in awkward chunk sizes spanning multiple sponge blocks.
        chunks = b"".join(reader.read(n) for n in (1, 2, 3, 5, 50, 139, 0))
        oneshot = (hashlib.shake_128 if bits == 128 else hashlib.shake_256)(data)
        assert chunks == oneshot.digest(len(chunks))
