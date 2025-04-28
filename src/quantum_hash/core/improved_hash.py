"""
Improved quantum-inspired hash functions based on benchmark results.

This module provides enhanced versions of our quantum-inspired hash functions
with better security properties and performance.
"""

import numpy as np
import hashlib
from typing import List, Tuple, Optional

# Constants for improved hashing
# Large prime numbers for diffusion
PRIMES = [
    0x9e3779b9, 0x6a09e667, 0xbb67ae85, 0x3c6ef372,
    0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
    0x5be0cd19, 0xca62c1d6, 0x84caa73b, 0xfe94f82b
]

# Rotation constants
ROTATIONS = [
    7, 11, 13, 17, 19, 23, 29, 31, 5, 3
]


def rotate_left(value: int, shift: int, bits: int = 32) -> int:
    """Rotate left (circular shift) for the given value."""
    mask = (1 << bits) - 1
    value &= mask
    return ((value << shift) | (value >> (bits - shift))) & mask


def mix_bits(a: int, b: int, bits: int = 32) -> Tuple[int, int]:
    """Mix two values to increase diffusion."""
    mask = (1 << bits) - 1
    a = (a + b) & mask
    b = rotate_left(b, 13, bits) ^ a
    a = (rotate_left(a, 7, bits) + b) & mask
    b = rotate_left(b, 17, bits) ^ a
    a = (a + b) & mask
    return a, b


def improved_grover_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    Improved Grover-inspired hash function with better diffusion and
    avalanche effect.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    # Convert input to numeric array
    data_array = np.frombuffer(data, dtype=np.uint8)
    
    # If data is empty, add a single byte to ensure consistent behavior
    if len(data_array) == 0:
        data_array = np.array([0], dtype=np.uint8)
    
    # Initialize state with prime numbers (use Python ints, not numpy)
    state = [int(p) for p in PRIMES[:digest_size]]
    if len(state) < digest_size:
        # If we need more state elements than primes, repeat them
        state.extend(PRIMES[:digest_size-len(state)])
    
    # Split data into 32-bit chunks for processing
    chunk_size = 4  # 4 bytes = 32 bits
    chunks = []
    
    # Pad data to multiple of chunk_size
    padded_size = ((len(data_array) + chunk_size - 1) // chunk_size) * chunk_size
    padded_data = np.zeros(padded_size, dtype=np.uint8)
    padded_data[:len(data_array)] = data_array
    
    # Convert to chunks
    for i in range(0, padded_size, chunk_size):
        chunk = int.from_bytes(padded_data[i:i+chunk_size].tobytes(), byteorder='little')
        chunks.append(chunk)
    
    # If no chunks, add a zero chunk
    if not chunks:
        chunks = [0]
    
    # Add the length as the last chunk to prevent length extension attacks
    chunks.append(len(data_array))
    
    # Process each chunk
    for chunk in chunks:
        for i in range(len(state)):
            # Enhanced bit mixing with chunk data
            a = state[i]
            b = chunk ^ PRIMES[i % len(PRIMES)]
            
            # Apply multiple mixing rounds
            for r in range(3):  # More rounds for better diffusion
                a, b = mix_bits(a, b)
                b = rotate_left(b, ROTATIONS[r % len(ROTATIONS)])
            
            state[i] = a ^ b
        
        # State diffusion after each chunk
        temp_state = state.copy()
        for i in range(len(state)):
            j = (i + 1) % len(state)
            k = (i + len(state)//2) % len(state)
            state[i] = rotate_left(temp_state[i], 5) ^ temp_state[j] ^ rotate_left(temp_state[k], 13)
    
    # Final mixing rounds
    for r in range(digest_size):
        i = r % len(state)
        j = (i + 1) % len(state)
        state[i], state[j] = mix_bits(state[i], state[j])
    
    # Convert state to bytes
    result = bytearray()
    for val in state:
        result.extend(val.to_bytes(4, byteorder='little'))
    
    # Truncate to desired digest size
    return bytes(result[:digest_size])


def improved_shor_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    Improved Shor-inspired hash function with better avalanche effect
    and distribution properties.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    # If data is empty, use a default value
    if not data:
        data = b"\x00"
    
    # Initialize state with prime number seeds (using Python ints)
    state_size = (digest_size + 3) // 4  # Number of 32-bit words
    state = [int(p) for p in PRIMES[:state_size]]
    if len(state) < state_size:
        state.extend(PRIMES[:state_size-len(state)])
    
    # Calculate data length for finalization
    data_length = len(data)
    
    # Process data in blocks
    block_size = 64  # Similar to SHA-256 block size
    
    # Pad data to multiple of block_size
    padded_size = ((len(data) + block_size - 1) // block_size) * block_size
    padded_data = bytearray(padded_size)
    padded_data[:len(data)] = data
    
    # Process each block
    for block_start in range(0, padded_size, block_size):
        block = padded_data[block_start:block_start+block_size]
        
        # Process the block in 32-bit chunks
        for i in range(0, block_size, 4):
            chunk = int.from_bytes(block[i:i+4], byteorder='little')
            
            # Update state with chunk
            idx = (i // 4) % state_size
            state[idx] ^= chunk
            
            # Apply mixing function
            for j in range(state_size):
                k = (j + 1) % state_size
                
                # Enhanced mixing inspired by Shor's period finding
                a = state[j]
                b = state[k]
                
                # Mix values
                for r in range(3):
                    a, b = mix_bits(a, b)
                    a = rotate_left(a, ROTATIONS[r % len(ROTATIONS)])
                
                state[j] = a
                state[k] = b
        
        # Apply permutation after each block
        temp = state.copy()
        for i in range(state_size):
            j = (i * 7 + 1) % state_size
            state[j] = temp[i]
    
    # Finalization - include data length to prevent length extension
    for i in range(state_size):
        state[i] ^= data_length
        
        # Apply final diffusion
        for j in range(3):
            idx1 = (i + j + 1) % state_size
            idx2 = (i + j + 2) % state_size
            state[i] = rotate_left(state[i], 9) ^ state[idx1] ^ rotate_left(state[idx2], 13)
    
    # Convert state to bytes
    result = bytearray()
    for val in state:
        result.extend(val.to_bytes(4, byteorder='little'))
    
    # Truncate to desired digest size
    return bytes(result[:digest_size])


def improved_hybrid_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    Improved hybrid hash combining Grover and Shor approaches with
    enhanced security properties.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    # If empty data, use a default value
    if not data:
        data = b"\x00"
    
    # Use SHA-256 for initial mixing to improve entropy
    sha_digest = hashlib.sha256(data).digest()
    
    # Split the work - hash half with Grover and half with Shor
    half_size = digest_size // 2
    remaining = digest_size - (2 * half_size)
    
    # Create separate data streams by mixing with SHA digest
    data1 = bytearray(data)
    data2 = bytearray(data)
    
    # XOR with different parts of SHA digest for domain separation
    for i in range(min(len(data1), 32)):
        data1[i] ^= sha_digest[i]
    
    for i in range(min(len(data2), 32)):
        data2[i] ^= sha_digest[31 - (i % 32)]
    
    # Apply improved Grover hash
    hash1 = improved_grover_hash(bytes(data1), half_size)
    
    # Apply improved Shor hash
    hash2 = improved_shor_hash(bytes(data2), half_size)
    
    # Final combination
    result = bytearray()
    
    # Interleave the bytes from both hashes
    for i in range(half_size):
        result.append(hash1[i])
        result.append(hash2[i])
    
    # If digest_size is odd, add one more byte from SHA-256
    if remaining > 0:
        result.extend(sha_digest[:remaining])
    
    # Final diffusion pass
    for i in range(digest_size):
        j = (i + 1) % digest_size
        k = (i + 7) % digest_size
        result[i] = (result[i] + result[j] * result[k]) % 256
    
    return bytes(result) 