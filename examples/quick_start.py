#!/usr/bin/env python3
"""
Quick start example for the dirac-hashes package.

This demonstrates the core functionality of the dirac-hashes package in a concise way.
"""

from quantum_hash.dirac import DiracHash
from quantum_hash.signatures.dilithium import DilithiumSignature
from quantum_hash.kem.kyber import KyberKEM

# Hash a message using the default algorithm
message = "Hello, quantum world!"
hash_value = DiracHash.hash(message)
print(f"Message: {message}")
print(f"Hash: {hash_value.hex()}")

# Digital signature with Dilithium
print("\n=== Digital Signature ===")
# Generate a key pair
dilithium = DilithiumSignature(security_level=2)
private_key, public_key = dilithium.generate_keypair()

# Sign a message
signature = dilithium.sign(message.encode(), private_key)
print(f"Signature size: {len(signature)} bytes")

# Verify the signature
is_valid = dilithium.verify(message.encode(), signature, public_key)
print(f"Signature valid: {is_valid}")

# Key Encapsulation Mechanism (KEM)
print("\n=== Key Encapsulation Mechanism ===")
# Create a KEM instance
kyber = KyberKEM(security_level=3)

# Generate a key pair
kem_private_key, kem_public_key = kyber.generate_keypair()

# Alice encapsulates a shared secret using Bob's public key
shared_secret, ciphertext = kyber.encapsulate(kem_public_key)

# Bob decapsulates the shared secret using his private key
decapsulated_secret = kyber.decapsulate(ciphertext, kem_private_key)

# Verify that both parties have the same shared secret
print(f"Shared secrets match: {shared_secret == decapsulated_secret}")
print(f"Shared secret: {shared_secret.hex()[:20]}...") 