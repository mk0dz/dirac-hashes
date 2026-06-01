"""Loader for the vendored NIST ACVP test vectors."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

VEC = Path(__file__).resolve().parent / "vectors"


def load(name: str) -> dict:
    """Load a vendored vector document by short name, e.g. ``"ml_kem_keygen"``."""
    path = VEC / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"KAT file not found: {path}\n"
            f"Run `python kat/fetch_acvp.py` (add --all for SLH-DSA) to vendor vectors."
        )
    return json.loads(path.read_text())


def iter_tests(name: str, parameter_set: str | None = None) -> Iterator[tuple[dict, dict]]:
    """Yield ``(group, test)`` pairs, optionally filtered by ``parameterSet``.

    The group dict carries shared fields (parameterSet, testType, function,
    deterministic, ...); the test dict carries per-case inputs/outputs.
    """
    doc = load(name)
    for group in doc.get("testGroups", []):
        if parameter_set is not None and group.get("parameterSet") != parameter_set:
            continue
        for test in group.get("tests", []):
            yield group, test


def unhex(value: str | None) -> bytes:
    """Decode an ACVP hex string (``None``/empty -> ``b""``)."""
    return bytes.fromhex(value) if value else b""
