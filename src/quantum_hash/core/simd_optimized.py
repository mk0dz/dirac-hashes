"""
SIMD-optimized quantum-inspired hash functions.

This module provides vectorized implementations of our quantum-inspired hash
functions for improved performance on modern CPUs.
"""

import numpy as np
from typing import List, Tuple, Optional, Union
import hashlib
import os

# Try to import C extensions
try:
    from .optimized_core import optimized_grover_hash_c, optimized_shor_hash_c
    from .hybrid_core import optimized_hybrid_hash_c
    _HAVE_C_EXTENSIONS = True
except ImportError:
    _HAVE_C_EXTENSIONS = False
    print("Warning: C extensions not found. Using slower Python implementations.")

# Try to import numba for JIT compilation
try:
    import numba
    from numba import njit, prange, vectorize
    from numba import uint32, uint64, uint8
    _HAVE_NUMBA = True
except ImportError:
    # Create dummy decorators if numba is not available
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def prange(*args, **kwargs):
        return range(*args, **kwargs)
    
    def vectorize(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    # Dummy type annotations that won't be used without Numba
    uint32 = lambda x: x
    uint64 = lambda x: x
    uint8 = lambda x: x
    _HAVE_NUMBA = False

# Constants for hashing
PRIMES = np.array([
    0x9e3779b9, 0x6a09e667, 0xbb67ae85, 0x3c6ef372,
    0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
    0x5be0cd19, 0xca62c1d6, 0x84caa73b, 0xfe94f82b
], dtype=np.uint32)

ROTATIONS = np.array([7, 11, 13, 17, 19, 23, 29, 31, 5, 3], dtype=np.uint8)

# Additional constants for better quantum resistance
EXTRA_PRIMES = np.array([
    0x243f6a88, 0x85a308d3, 0x13198a2e, 0x03707344,
    0xa4093822, 0x299f31d0, 0x082efa98, 0xec4e6c89,
    0x452821e6, 0x38d01377, 0xbe5466cf, 0x34e90c6c
], dtype=np.uint32)


# Define the rotate left function based on whether Numba is available
if _HAVE_NUMBA:
    @vectorize([uint32(uint32, uint8)], nopython=True)
    def rotate_left(value: np.uint32, shift: np.uint8) -> np.uint32:
        """Vectorized rotate left operation."""
        return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF
else:
    def rotate_left(value: np.uint32, shift: np.uint8) -> np.uint32:
        """Simple rotate left operation."""
        return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


@njit(fastmath=True)
def mix_bits(a: np.uint32, b: np.uint32) -> Tuple[np.uint32, np.uint32]:
    """Mix two values to increase diffusion."""
    a = (a + b) & 0xFFFFFFFF
    b = rotate_left(b, 13) ^ a
    a = (rotate_left(a, 7) + b) & 0xFFFFFFFF
    b = rotate_left(b, 17) ^ a
    a = (a + b) & 0xFFFFFFFF
    
    # Additional mixing for quantum resistance
    b = rotate_left(b, 5) ^ (a * 0x9e3779b9)
    a = rotate_left(a, 11) + rotate_left(b, 19)
    return a, b


@njit(parallel=True, fastmath=True)
def numba_enhanced_grover_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    JIT-compiled implementation of enhanced Grover-inspired hash function
    with better diffusion, avalanche effect, and quantum resistance.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    # If data is empty, add a single byte to ensure consistent behavior
    if not data:
        data = b"\x00"
    
    # Initialize state with prime numbers
    state = np.array([PRIMES[i % len(PRIMES)] for i in range(digest_size)], dtype=np.uint32)
    
    # Split data into 32-bit chunks for processing
    chunk_size = 4  # 4 bytes = 32 bits
    padded_size = ((len(data) + chunk_size - 1) // chunk_size) * chunk_size
    padded_data = bytearray(padded_size)
    padded_data[:len(data)] = data
    
    # Convert to chunks
    chunks = np.empty(padded_size // chunk_size + 1, dtype=np.uint32)
    for i in prange(padded_size // chunk_size):
        chunk = 0
        for j in range(chunk_size):
            if i * chunk_size + j < padded_size:
                chunk |= padded_data[i * chunk_size + j] << (j * 8)
        chunks[i] = chunk
    
    # Add the length as the last chunk to prevent length extension attacks
    chunks[-1] = len(data)
    
    # Process each chunk
    for chunk in chunks:
        # Enhanced state update with better mixing
        for i in prange(len(state)):
            a = state[i]
            b = chunk ^ PRIMES[i % len(PRIMES)] ^ EXTRA_PRIMES[i % len(EXTRA_PRIMES)]
            
            # Apply multiple mixing rounds for better diffusion
            for r in range(4):  # Increased from 3 to 4 rounds
                a, b = mix_bits(a, b)
                b = rotate_left(b, ROTATIONS[r % len(ROTATIONS)])
                # Add non-linearity with multiplication by prime
                a = (a * PRIMES[(i + r) % len(PRIMES)]) & 0xFFFFFFFF
            
            state[i] = a ^ b
        
        # State diffusion after each chunk (improved version)
        temp_state = state.copy()
        for i in prange(len(state)):
            j = (i + 1) % len(state)
            k = (i + len(state)//2) % len(state)
            # Enhanced diffusion using additional rotations and operations
            state[i] = rotate_left(temp_state[i], 5) ^ temp_state[j] ^ rotate_left(temp_state[k], 13)
            state[i] = (state[i] + rotate_left(state[i], 11)) & 0xFFFFFFFF
    
    # Final mixing rounds with additional operations
    for r in range(digest_size * 2):  # More rounds for better security
        i = r % len(state)
        j = (i + 1) % len(state)
        k = (i + len(state)//2) % len(state)
        
        # Mix multiple state elements
        state[i], state[j] = mix_bits(state[i], state[j])
        state[j], state[k] = mix_bits(state[j], state[k])
        state[k], state[i] = mix_bits(state[k], state[i])
    
    # Convert state to bytes
    result = bytearray(digest_size)
    for i in range(min(len(state), digest_size // 4)):
        for j in range(4):
            if i * 4 + j < digest_size:
                result[i * 4 + j] = (state[i] >> (j * 8)) & 0xFF
    
    return bytes(result)


def optimized_grover_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    Optimized Grover-inspired hash function with better diffusion,
    avalanche effect, and quantum resistance.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    if _HAVE_C_EXTENSIONS:
        return optimized_grover_hash_c(data, digest_size)
    else:
        return numba_enhanced_grover_hash(data, digest_size)


@njit(parallel=True, fastmath=True)
def numba_enhanced_shor_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    JIT-compiled implementation of enhanced Shor-inspired hash function
    with better avalanche effect, distribution, and quantum resistance.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    # If data is empty, use a default value
    if not data:
        data = b"\x00"
    
    # Initialize state with prime number seeds
    state_size = (digest_size + 3) // 4  # Number of 32-bit words
    state = np.array([PRIMES[i % len(PRIMES)] for i in range(state_size)], dtype=np.uint32)
    
    # Calculate data length for finalization
    data_length = len(data)
    
    # Process data in blocks
    block_size = 64  # Similar to SHA-256 block size
    padded_size = ((len(data) + block_size - 1) // block_size) * block_size
    padded_data = bytearray(padded_size)
    padded_data[:len(data)] = data
    
    # Process each block with enhanced security
    for block_start in range(0, padded_size, block_size):
        block = padded_data[block_start:block_start+block_size]
        
        # Process the block in 32-bit chunks
        for i in range(0, block_size, 4):
            chunk = 0
            for j in range(4):
                if i + j < len(block):
                    chunk |= block[i + j] << (j * 8)
            
            # Update state with chunk
            idx = (i // 4) % state_size
            state[idx] ^= chunk
            
            # Apply mixing function with quantum resistance enhancements
            for j in prange(state_size):
                k = (j + 1) % state_size
                
                # Enhanced mixing inspired by Shor's period finding
                a = state[j]
                b = state[k]
                
                # Mix values with more rounds
                for r in range(4):  # Increased from 3 to 4 rounds
                    a, b = mix_bits(a, b)
                    a = rotate_left(a, ROTATIONS[r % len(ROTATIONS)])
                    
                    # Additional mixing for quantum resistance
                    b = (b + EXTRA_PRIMES[r % len(EXTRA_PRIMES)]) & 0xFFFFFFFF
                
                state[j] = a
                state[k] = b
        
        # Apply permutation after each block with enhanced complexity
        temp = state.copy()
        for i in prange(state_size):
            j = (i * 7 + 1) % state_size
            k = (i * 5 + 3) % state_size  # Additional mixing point
            state[j] = temp[i] ^ rotate_left(temp[k], 13)
    
    # Finalization with data length and additional operations
    for i in prange(state_size):
        state[i] ^= data_length
        
        # Apply enhanced final diffusion
        for j in range(4):  # Increased from 3 to 4 rounds
            idx1 = (i + j + 1) % state_size
            idx2 = (i + j + 2) % state_size
            idx3 = (i + j + 3) % state_size  # Additional mixing point
            
            # More complex diffusion
            state[i] = rotate_left(state[i], 9) ^ state[idx1] ^ rotate_left(state[idx2], 13) ^ state[idx3]
            state[i] = (state[i] * PRIMES[j % len(PRIMES)]) & 0xFFFFFFFF
    
    # Convert state to bytes
    result = bytearray(digest_size)
    for i in range(min(state_size, digest_size // 4 + 1)):
        for j in range(4):
            if i * 4 + j < digest_size:
                result[i * 4 + j] = (state[i] >> (j * 8)) & 0xFF
    
    return bytes(result)


def optimized_shor_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    Optimized Shor-inspired hash function with better avalanche effect,
    distribution properties, and quantum resistance.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    if _HAVE_C_EXTENSIONS:
        return optimized_shor_hash_c(data, digest_size)
    else:
        return numba_enhanced_shor_hash(data, digest_size)


@njit(parallel=True, fastmath=True)
def numba_enhanced_hybrid_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    JIT-compiled implementation of enhanced hybrid hash function combining 
    Grover and Shor approaches with improved quantum resistance.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    # If empty data, use a default value
    if not data:
        data = b"\x00"
    
    # Use simpler initialization without SHA-256 to improve performance
    # while maintaining security through other means
    
    # Calculate the half and remaining sizes
    half_size = digest_size // 2
    remaining = digest_size - (2 * half_size)
    
    # Split the work between Grover and Shor approaches
    # Create domain separation by using different prefixes
    data1 = bytearray(len(data) + 1)
    data1[0] = 0x01  # Prefix for Grover domain
    data1[1:] = data
    
    data2 = bytearray(len(data) + 1)
    data2[0] = 0x02  # Prefix for Shor domain
    data2[1:] = data
    
    # Process with Grover-inspired approach
    grover_result = numba_enhanced_grover_hash(data1, half_size)
    
    # Process with Shor-inspired approach
    shor_result = numba_enhanced_shor_hash(data2, half_size)
    
    # Combine the results with additional mixing for quantum resistance
    result = bytearray(digest_size)
    
    # Interleave the results for better mixing
    for i in prange(half_size):
        result[i*2] = grover_result[i]
        result[i*2+1] = shor_result[i]
    
    # If digest size is odd, add one more byte
    if remaining:
        # XOR the last bytes of both results for the remaining byte
        result[-1] = grover_result[-1] ^ shor_result[-1]
    
    # Enhance security with a final mixing pass
    # Convert to 32-bit chunks for processing
    state_size = (digest_size + 3) // 4
    state = np.zeros(state_size, dtype=np.uint32)
    
    for i in prange(digest_size):
        byte_val = result[i]
        state_idx = i // 4
        shift = (i % 4) * 8
        state[state_idx] |= byte_val << shift
    
    # Apply multiple rounds of mixing for better diffusion
    for round in range(4):  # Multiple rounds for security
        # Mix each state element with others
        for i in prange(state_size):
            for j in range(1, min(4, state_size)):
                idx = (i + j) % state_size
                a = state[i]
                b = state[idx]
                a, b = mix_bits(a, b)
                state[i] = a
                state[idx] = b
    
    # Convert back to bytes
    for i in prange(state_size):
        for j in range(4):
            idx = i * 4 + j
            if idx < digest_size:
                result[idx] = (state[i] >> (j * 8)) & 0xFF
    
    return bytes(result) 


def optimized_hybrid_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    Optimized hybrid hash combining both Grover and Shor approaches
    with enhanced security properties and quantum resistance.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    if _HAVE_C_EXTENSIONS:
        return optimized_hybrid_hash_c(data, digest_size)
    else:
        return numba_enhanced_hybrid_hash(data, digest_size) 