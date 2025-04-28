#!/usr/bin/env python3
"""
Dirac Hashes - Command-line demonstration.

This script demonstrates the functionality of the quantum-inspired
hash functions and key generation algorithms.
"""

import sys
import time
import argparse
from src.quantum_hash.dirac import DiracHash


def demo_hash_functions():
    """Demonstrate hash function capabilities."""
    print("\n=== Hash Function Demonstration ===")
    
    test_data = [
        b"Hello, quantum world!",
        b"The quick brown fox jumps over the lazy dog",
        b"",  # Empty string
        b"a" * 1000,  # Repeating pattern
    ]
    
    # Include both original and improved algorithms
    algorithms = [
        'grover', 'shor', 'hybrid', 
        'improved_grover', 'improved_shor', 'improved'
    ]
    
    for algorithm in algorithms:
        print(f"\n## {algorithm.capitalize()} Algorithm ##")
        
        for i, data in enumerate(test_data):
            start_time = time.time()
            digest = DiracHash.hash(data, algorithm=algorithm)
            elapsed = time.time() - start_time
            
            print(f"Test {i+1}: {data[:30]}{'...' if len(data) > 30 else ''}")
            print(f"  Digest: {DiracHash.format_key(digest)}")
            print(f"  Length: {len(digest)} bytes")
            print(f"  Time: {elapsed:.6f} seconds")
    
    # Demonstrate avalanche effect
    print("\n## Avalanche Effect Demonstration ##")
    
    # Compare original vs improved algorithms for avalanche effect
    algorithms_to_compare = ['hybrid', 'improved']
    
    for algorithm in algorithms_to_compare:
        print(f"\n### {algorithm.capitalize()} Algorithm ###")
        data1 = b"Quantum computing will revolutionize cryptography"
        data2 = b"Quantum computing will revolutionize cryptography."  # Added period
        
        hash1 = DiracHash.hash(data1, algorithm=algorithm)
        hash2 = DiracHash.hash(data2, algorithm=algorithm)
        
        xor_result = bytes(a ^ b for a, b in zip(hash1, hash2))
        diff_bits = bin(int.from_bytes(xor_result, byteorder='big')).count('1')
        
        print(f"Input 1: {data1}")
        print(f"Input 2: {data2}")
        print(f"Hash 1: {DiracHash.format_key(hash1)}")
        print(f"Hash 2: {DiracHash.format_key(hash2)}")
        print(f"Bit difference: {diff_bits} out of {len(hash1) * 8} ({diff_bits/(len(hash1)*8)*100:.2f}%)")


def demo_key_generation():
    """Demonstrate key generation capabilities."""
    print("\n=== Key Generation Demonstration ===")
    
    # Generate high-entropy seed
    print("\n## Quantum-Inspired Seed Generation ##")
    start_time = time.time()
    seed = DiracHash.generate_seed()
    elapsed = time.time() - start_time
    
    print(f"Generated seed: {DiracHash.format_key(seed)}")
    print(f"Length: {len(seed)} bytes")
    print(f"Time: {elapsed:.6f} seconds")
    
    # Generate keypair
    print("\n## Keypair Generation (using improved algorithm) ##")
    start_time = time.time()
    private_key, public_key = DiracHash.generate_keypair()
    elapsed = time.time() - start_time
    
    print(f"Private key: {DiracHash.format_key(private_key)}")
    print(f"Public key: {DiracHash.format_key(public_key)}")
    print(f"Time: {elapsed:.6f} seconds")
    
    # Demonstrate different key formats
    print("\n## Key Formatting ##")
    formats = ['hex', 'base64', 'base58']
    for fmt in formats:
        formatted = DiracHash.format_key(private_key, format_type=fmt)
        print(f"{fmt.upper()}: {formatted}")
    
    # Demonstrate key derivation
    print("\n## Key Derivation (using improved algorithm) ##")
    master_key = DiracHash.generate_seed()
    purposes = ["encryption", "signing", "authentication"]
    
    print(f"Master key: {DiracHash.format_key(master_key)}")
    
    for purpose in purposes:
        derived_key = DiracHash.derive_key(master_key, purpose)
        print(f"Derived key for '{purpose}': {DiracHash.format_key(derived_key)}")


def demo_hmac():
    """Demonstrate HMAC functionality."""
    print("\n=== HMAC Demonstration (using improved algorithm) ===")
    
    key = DiracHash.generate_seed(16)  # 16-byte key
    messages = [
        b"Authentication message",
        b"Sign this document",
        b"Verify integrity"
    ]
    
    print(f"Key: {DiracHash.format_key(key)}")
    
    for msg in messages:
        hmac = DiracHash.hmac(key, msg)
        print(f"\nMessage: {msg}")
        print(f"HMAC: {DiracHash.format_key(hmac)}")


def main():
    """Main function to run the demonstration."""
    parser = argparse.ArgumentParser(description="Dirac Hashes Demonstration")
    parser.add_argument("--hash", action="store_true", help="Demonstrate hash functions")
    parser.add_argument("--keys", action="store_true", help="Demonstrate key generation")
    parser.add_argument("--hmac", action="store_true", help="Demonstrate HMAC")
    parser.add_argument("--all", action="store_true", help="Run all demonstrations")
    
    args = parser.parse_args()
    
    # If no arguments are provided, show all demonstrations
    if not (args.hash or args.keys or args.hmac or args.all):
        args.all = True
    
    print("===== Dirac Hashes - Quantum-Inspired Cryptography =====")
    print("\nDefault algorithm is now 'improved' (combines quantum-inspired techniques with cryptographic best practices)")
    
    if args.hash or args.all:
        demo_hash_functions()
    
    if args.keys or args.all:
        demo_key_generation()
    
    if args.hmac or args.all:
        demo_hmac()
    
    print("\n===== Demonstration Complete =====")


if __name__ == "__main__":
    main() 