"""
Dirac Hashes - Main interface module.

This module provides easy access to all quantum-inspired hash and key functions.
"""

from typing import Tuple, Dict, Union, Optional

from src.quantum_hash.core.grover import grover_hash
from src.quantum_hash.core.shor import shor_hash, shor_inspired_key_generation
from src.quantum_hash.core.improved_hash import (
    improved_grover_hash, improved_shor_hash, improved_hybrid_hash
)
# Import SIMD-optimized implementations
try:
    from src.quantum_hash.core.simd_optimized import (
        optimized_grover_hash, optimized_shor_hash, optimized_hybrid_hash
    )
    _HAVE_OPTIMIZED = True
except ImportError:
    _HAVE_OPTIMIZED = False

from src.quantum_hash.utils.hash import quantum_hash, quantum_hmac
from src.quantum_hash.utils.keys import (generate_quantum_seed, generate_keypair,
                                    derive_key, format_key, parse_key)


class DiracHash:
    """
    Main interface class for quantum-inspired hash functions.
    
    This class provides an easy-to-use interface for all quantum-inspired
    hash and key generation functions.
    """
    
    @staticmethod
    def hash(data: Union[bytes, str], algorithm: str = 'improved', 
             digest_size: int = 32, optimized: bool = True) -> bytes:
        """
        Generate a hash using quantum-inspired algorithms.
        
        Args:
            data: Input data to hash
            algorithm: Algorithm to use ('grover', 'shor', 'hybrid', 
                      'improved_grover', 'improved_shor', or 'improved')
            digest_size: Size of the output hash in bytes
            optimized: Whether to use SIMD-optimized implementations when available
        
        Returns:
            Hash value as bytes
        """
        # Convert string input to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use optimized implementations if available and requested
        if optimized and _HAVE_OPTIMIZED:
            if algorithm.lower() == 'improved_grover' or algorithm.lower() == 'optimized_grover':
                return optimized_grover_hash(data, digest_size)
            elif algorithm.lower() == 'improved_shor' or algorithm.lower() == 'optimized_shor':
                return optimized_shor_hash(data, digest_size)
            elif algorithm.lower() == 'improved' or algorithm.lower() == 'optimized':
                return optimized_hybrid_hash(data, digest_size)
        
        # Fall back to non-optimized implementations
        return quantum_hash(data, algorithm, digest_size)
    
    @staticmethod
    def hmac(key: Union[bytes, str], data: Union[bytes, str],
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
        return quantum_hmac(key, data, algorithm, digest_size, optimized)
    
    @staticmethod
    def generate_seed(entropy_bytes: int = 32) -> bytes:
        """
        Generate a high-entropy seed.
        
        Args:
            entropy_bytes: Number of bytes of entropy to generate
        
        Returns:
            Entropy bytes
        """
        return generate_quantum_seed(entropy_bytes)
    
    @staticmethod
    def generate_keypair(key_size: int = 32, 
                         algorithm: str = 'improved',
                         optimized: bool = True) -> Tuple[bytes, bytes]:
        """
        Generate a keypair using quantum-inspired algorithms.
        
        Args:
            key_size: Size of the key in bytes
            algorithm: Algorithm to use for key derivation
            optimized: Whether to use SIMD-optimized implementations when available
        
        Returns:
            Tuple of (private_key, public_key)
        """
        return generate_keypair(key_size, algorithm, optimized)
    
    @staticmethod
    def derive_key(master_key: bytes, purpose: str, 
                  key_size: int = 32, algorithm: str = 'improved',
                  optimized: bool = True) -> bytes:
        """
        Derive a subkey from a master key for a specific purpose.
        
        Args:
            master_key: The master key to derive from
            purpose: A string describing the purpose of this key
            key_size: Size of the derived key in bytes
            algorithm: Hash algorithm to use for key derivation
            optimized: Whether to use SIMD-optimized implementations when available
        
        Returns:
            Derived key
        """
        return derive_key(master_key, purpose, key_size, algorithm, optimized)
    
    @staticmethod
    def format_key(key: bytes, format_type: str = 'hex') -> str:
        """
        Format a key for output or storage.
        
        Args:
            key: Key bytes
            format_type: Format type ('hex', 'base64', or 'base58')
        
        Returns:
            Formatted key as a string
        """
        return format_key(key, format_type)
    
    @staticmethod
    def parse_key(key_str: str, format_type: str = 'hex') -> bytes:
        """
        Parse a formatted key.
        
        Args:
            key_str: Formatted key string
            format_type: Format type ('hex', 'base64', or 'base58')
        
        Returns:
            Key bytes
        """
        return parse_key(key_str, format_type)
    
    @staticmethod
    def optimized_available() -> bool:
        """
        Check if optimized implementations are available.
        
        Returns:
            True if optimized implementations are available, False otherwise
        """
        return _HAVE_OPTIMIZED 