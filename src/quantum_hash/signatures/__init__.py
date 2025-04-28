"""
Quantum-inspired signature schemes module.

This module contains implementations of post-quantum signature algorithms
based on quantum-inspired hashing techniques.
"""

from src.quantum_hash.signatures.lamport import LamportSignature

__all__ = ["LamportSignature"] 