#!/usr/bin/env python3
"""
Example usage of the Kyber Key Encapsulation Mechanism (KEM).

This script demonstrates how to use the Kyber implementation for key exchange
between two parties in a post-quantum secure manner.
"""

from quantum_hash.kem.kyber import Kyber


def main():
    """Demonstrate the Kyber KEM implementation."""
    print("Kyber Key Encapsulation Mechanism (KEM) Example")
    print("------------------------------------------------")
    
    # Security levels: 1 (Kyber-512), 3 (Kyber-768), 5 (Kyber-1024)
    security_level = 3
    print(f"Using security level {security_level} (Kyber-{512 * security_level // 2})")
    
    # Create a Kyber instance
    kyber = Kyber(security_level=security_level, hash_algorithm='improved')
    
    print("\n1. Generating key pair for Bob (recipient)...")
    private_key, public_key = kyber.generate_keypair()
    
    print("2. Alice (sender) encapsulates a shared secret using Bob's public key...")
    ciphertext, shared_secret_alice = kyber.encapsulate(public_key)
    
    print("3. Bob decapsulates the shared secret using his private key...")
    shared_secret_bob = kyber.decapsulate(ciphertext, private_key)
    
    # Verify that both parties have the same shared secret
    print("\nResults:")
    print(f"Alice's shared secret: {shared_secret_alice.hex()}")
    print(f"Bob's shared secret:   {shared_secret_bob.hex()}")
    
    if shared_secret_alice == shared_secret_bob:
        print("\n✅ Success! Both parties have established the same shared secret.")
    else:
        print("\n❌ Error: The shared secrets do not match.")
    
    # Show ciphertext size for reference
    print(f"\nCiphertext size: {len(ciphertext)} bytes")
    
    # Show the size of blockchain-compatible representation
    blockchain_public_key = kyber.get_blockchain_compatible_keys(public_key)
    print(f"Blockchain public key size: {len(blockchain_public_key)} bytes")


if __name__ == "__main__":
    main() 