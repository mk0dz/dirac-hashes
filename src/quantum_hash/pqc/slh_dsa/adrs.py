"""32-byte hash addresses for SLH-DSA (FIPS 205 §4.2).

The SHAKE instantiations use the full (uncompressed) 32-byte address. Each address is
eight 4-byte big-endian words; the meaning of the last three words depends on the type.
"""
from __future__ import annotations

# ADRS type constants.
WOTS_HASH = 0
WOTS_PK = 1
TREE = 2
FORS_TREE = 3
FORS_ROOTS = 4
WOTS_PRF = 5
FORS_PRF = 6


class ADRS:
    __slots__ = ("a",)

    def __init__(self, data: bytes | None = None):
        self.a = bytearray(data) if data is not None else bytearray(32)

    def copy(self) -> "ADRS":
        return ADRS(self.a)

    def bytes(self) -> bytes:
        return bytes(self.a)

    @staticmethod
    def _w(value: int) -> bytes:
        return int(value).to_bytes(4, "big")

    def set_layer_address(self, value: int) -> None:
        self.a[0:4] = self._w(value)

    def set_tree_address(self, value: int) -> None:
        self.a[4:16] = int(value).to_bytes(12, "big")

    def set_type_and_clear(self, type_: int) -> None:
        self.a[16:20] = self._w(type_)
        self.a[20:32] = bytes(12)

    def set_key_pair_address(self, value: int) -> None:
        self.a[20:24] = self._w(value)

    def get_key_pair_address(self) -> int:
        return int.from_bytes(self.a[20:24], "big")

    def set_chain_address(self, value: int) -> None:
        self.a[24:28] = self._w(value)

    def set_hash_address(self, value: int) -> None:
        self.a[28:32] = self._w(value)

    # Tree height/index alias the same words as chain/hash for TREE/FORS types.
    def set_tree_height(self, value: int) -> None:
        self.a[24:28] = self._w(value)

    def get_tree_height(self) -> int:
        return int.from_bytes(self.a[24:28], "big")

    def set_tree_index(self, value: int) -> None:
        self.a[28:32] = self._w(value)

    def get_tree_index(self) -> int:
        return int.from_bytes(self.a[28:32], "big")
