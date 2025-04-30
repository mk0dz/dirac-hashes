"""
Hash utility functions for quantum-inspired hash algorithms.
"""

import hashlib
import hmac
import os
from typing import Callable, Optional, Union

from ..core.grover import grover_hash
from ..core.shor import shor_hash
from ..core.improved_hash import (
    improved_grover_hash, improved_shor_hash, improved_hybrid_hash
)

# Import SIMD-optimized implementations if available
try:
    from ..core.simd_optimized import (
        optimized_grover_hash, optimized_shor_hash, optimized_hybrid_hash
    )
    _HAVE_OPTIMIZED = True
except ImportError:
    _HAVE_OPTIMIZED = False


def quantum_hash(data: Union[bytes, str], algorithm: str = 'hybrid', 
                 digest_size: int = 32, optimized: bool = True) -> bytes:
    """
    Generate a hash using quantum-inspired algorithms.
    
    Args:
        data: Input data to hash
        algorithm: Algorithm to use ('grover', 'shor', 'hybrid', 
                  'improved_grover', 'improved_shor', or 'improved',
                  'optimized_grover', 'optimized_shor', 'optimized')
        digest_size: Size of the output hash in bytes
        optimized: Whether to use SIMD-optimized implementations when available
    
    Returns:
        Hash value as bytes
    
    Raises:
        ValueError: If an invalid algorithm is specified
    """
    # Convert string input to bytes if needed
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Use optimized implementations if available and requested
    if optimized and _HAVE_OPTIMIZED:
        if algorithm.lower() in ('optimized_grover', 'opt_grover', 'improved_grover'):
            return optimized_grover_hash(data, digest_size)
        elif algorithm.lower() in ('optimized_shor', 'opt_shor', 'improved_shor'):
            return optimized_shor_hash(data, digest_size)
        elif algorithm.lower() in ('optimized', 'opt', 'improved'):
            return optimized_hybrid_hash(data, digest_size)
    
    # Non-optimized implementations
    algorithm = algorithm.lower()
    if algorithm == 'grover':
        return grover_hash(data, digest_size)
    elif algorithm == 'shor':
        return shor_hash(data, digest_size)
    elif algorithm == 'hybrid':
        # Hybrid approach: combine both algorithms
        # Use deterministic versions by seeding with the data
        
        # Generate a seed from the data for consistent hashing
        seed_hash = hashlib.sha256(data).digest()
        
        # Generate both hashes with the same digest size
        hash1 = grover_hash(data, digest_size)
        hash2 = shor_hash(data, digest_size)
        
        # XOR the results
        result = bytearray(digest_size)
        for i in range(digest_size):
            result[i] = hash1[i] ^ hash2[i]
        
        return bytes(result)
    elif algorithm == 'improved_grover':
        return improved_grover_hash(data, digest_size)
    elif algorithm == 'improved_shor':
        return improved_shor_hash(data, digest_size)
    elif algorithm == 'improved':
        return improved_hybrid_hash(data, digest_size)
    elif algorithm in ('optimized_grover', 'opt_grover', 
                     'optimized_shor', 'opt_shor',
                     'optimized', 'opt'):
        raise ValueError(f"Optimized algorithm {algorithm} requested but not available")
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def quantum_hmac(key: Union[bytes, str], data: Union[bytes, str], 
                algorithm: str = 'improved', digest_size: int = 32,
                optimized: bool = True) -> bytes:
    """
    Generate an HMAC using quantum-inspired hash functions.
    
    Args:
        key: The key for HMAC
        data: Input data
        algorithm: Hash algorithm to use
        digest_size: Size of the output digest in bytes
        optimized: Whether to use SIMD-optimized implementations when available
    
    Returns:
        HMAC digest as bytes
    """
    # Convert string inputs to bytes if needed
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Define the hash function to use with HMAC
    def hash_func(msg: bytes) -> bytes:
        return quantum_hash(msg, algorithm, digest_size, optimized)
    
    # Use Python's built-in HMAC module with our quantum hash
    return hmac.new(key, data, digestmod=lambda d=b'': DigestWrapper(hash_func, d)).digest()


class DigestWrapper:
    """Wrapper to make quantum hash functions compatible with hmac module."""
    
    def __init__(self, hash_func: Callable[[bytes], bytes], data: bytes = b''):
        self.hash_func = hash_func
        self.data = bytearray(data)
        self.digest_size = 32  # Default digest size
        self.block_size = 64   # Default block size (similar to SHA-256)
    
    def update(self, data: bytes) -> None:
        """Update the hash object with data."""
        self.data.extend(data)
    
    def digest(self) -> bytes:
        """Return the digest of all data passed to the update method."""
        return self.hash_func(self.data)
    
    def hexdigest(self) -> str:
        """Return the digest as a string of hexadecimal digits."""
        return self.digest().hex()
    
    def copy(self) -> 'DigestWrapper':
        """Return a copy of the hash object."""
        return DigestWrapper(self.hash_func, self.data) 