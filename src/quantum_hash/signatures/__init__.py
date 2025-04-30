"""
Post-quantum signature schemes module.

This module provides implementations of various post-quantum signature schemes.
"""

# Import and expose the signature classes
from quantum_hash.signatures.lamport import LamportSignature
from quantum_hash.signatures.sphincs import SPHINCSSignature
from quantum_hash.signatures.kyber import KyberKEM
from quantum_hash.signatures.dilithium import DilithiumSignature

__all__ = ['LamportSignature', 'SPHINCSSignature', 'KyberKEM', 'DilithiumSignature'] 