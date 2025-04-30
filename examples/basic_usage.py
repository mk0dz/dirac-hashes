#!/usr/bin/env python3
"""
Basic usage examples for the dirac-hashes package.

This script demonstrates how to use the main features of the package.
"""

from quantum_hash.dirac import DiracHash
from quantum_hash.signatures.dilithium import DilithiumSignature
from quantum_hash.signatures.sphincs import SPHINCSSignature
from quantum_hash.signatures.lamport import LamportSignature
from quantum_hash.kem.kyber import KyberKEM

def hash_examples():
    """Examples of using the hashing functionality."""
    print("\n=== HASH EXAMPLES ===")
    
    # Basic hashing
    message = "Hello, quantum world!"
    print(f"Message: {message}")
    
    # Try different algorithms
    for algorithm in DiracHash.get_supported_algorithms():
        hash_value = DiracHash.hash(message, algorithm=algorithm)
        print(f"{algorithm.ljust(15)}: {hash_value.hex()}")
    
    # Custom digest size
    hash_64 = DiracHash.hash(message, digest_size=64)
    print(f"64-byte digest : {hash_64.hex()}")
    
    # HMAC
    key = b"my-secret-key"
    hmac_value = DiracHash.hmac(key, message)
    print(f"HMAC           : {hmac_value.hex()}")

def key_examples():
    """Examples of key generation and derivation."""
    print("\n=== KEY EXAMPLES ===")
    
    # Generate a keypair
    private_key, public_key = DiracHash.generate_keypair(key_size=32)
    print(f"Private key: {private_key.hex()}")
    print(f"Public key : {public_key.hex()}")
    
    # Key formatting
    formatted_key = DiracHash.format_key(private_key, format_type="base64")
    print(f"Formatted key (base64): {formatted_key}")
    
    # Parse a formatted key
    parsed_key = DiracHash.parse_key(formatted_key, format_type="base64")
    print(f"Parsed key: {parsed_key.hex()}")
    
    # Key derivation
    master_key = DiracHash.generate_seed(32)
    derived_key1 = DiracHash.derive_key(master_key, "authentication")
    derived_key2 = DiracHash.derive_key(master_key, "encryption")
    print(f"Master key  : {master_key.hex()}")
    print(f"Derived key1: {derived_key1.hex()}")
    print(f"Derived key2: {derived_key2.hex()}")

def signature_examples():
    """Examples of digital signatures."""
    print("\n=== SIGNATURE EXAMPLES ===")
    
    message = b"Sign this message"
    
    # Dilithium signatures
    print("\nDilithium Signature:")
    dilithium = DilithiumSignature(security_level=2)
    priv_key, pub_key = dilithium.generate_keypair()
    signature = dilithium.sign(message, priv_key)
    is_valid = dilithium.verify(message, signature, pub_key)
    print(f"Signature size: {len(signature)} bytes")
    print(f"Verification result: {is_valid}")
    
    # SPHINCS+ signatures
    print("\nSPHINCS+ Signature:")
    sphincs = SPHINCSSignature(security_level=128)
    priv_key, pub_key = sphincs.generate_keypair()
    signature = sphincs.sign(message, priv_key)
    is_valid = sphincs.verify(message, signature, pub_key)
    print(f"Signature size: {len(signature)} bytes")
    print(f"Verification result: {is_valid}")
    
    # Lamport signatures
    print("\nLamport Signature:")
    lamport = LamportSignature()
    priv_key, pub_key = lamport.generate_keypair()
    signature = lamport.sign(message, priv_key)
    is_valid = lamport.verify(message, signature, pub_key)
    print(f"Signature size: {len(signature)} bytes")
    print(f"Verification result: {is_valid}")

def kem_examples():
    """Examples of Key Encapsulation Mechanism."""
    print("\n=== KEM EXAMPLES ===")
    
    # Initialize KEM with security level
    kyber = KyberKEM(security_level=3)
    
    # Generate keypair
    priv_key, pub_key = kyber.generate_keypair()
    
    # Alice encapsulates a shared secret using Bob's public key
    shared_secret, ciphertext = kyber.encapsulate(pub_key)
    print(f"Shared secret (Alice): {shared_secret.hex()}")
    print(f"Ciphertext size: {len(ciphertext)} bytes")
    
    # Bob decapsulates the shared secret using the ciphertext and his private key
    decapsulated_secret = kyber.decapsulate(ciphertext, priv_key)
    print(f"Shared secret (Bob): {decapsulated_secret.hex()}")
    
    # Verify both parties have the same shared secret
    if shared_secret == decapsulated_secret:
        print("✓ Key exchange successful - shared secrets match!")
    else:
        print("✗ Key exchange failed - shared secrets do not match!")

if __name__ == "__main__":
    print("Dirac Hashes - Post-Quantum Cryptography Examples")
    print("================================================")
    
    # Check if optimized implementations are available
    if DiracHash.optimized_available():
        print("✓ SIMD-optimized implementations are available")
    else:
        print("⚠ SIMD-optimized implementations are not available")
    
    # Run examples
    hash_examples()
    key_examples()
    signature_examples()
    kem_examples() 