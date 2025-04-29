#!/usr/bin/env python3
"""
Debug script for the signature implementations.
"""

from src.quantum_hash.signatures.dilithium import DilithiumSignature
from src.quantum_hash.signatures.sphincs import SPHINCSSignature
from src.quantum_hash.signatures.lamport import LamportSignature

def test_dilithium_direct():
    """Test the Dilithium signature scheme directly."""
    print("Testing Dilithium signature scheme directly...")
    
    # Initialize the signer
    signer = DilithiumSignature(security_level=1, hash_algorithm='improved')
    
    # Generate a keypair
    private_key, public_key = signer.generate_keypair()
    
    # Print key components
    print("Private key has components:", list(private_key.keys()))
    print("Private key 's' has type:", type(private_key['s'][0]), "and length:", len(private_key['s']))
    
    # Sign a message
    message = b"This is a test message for Dilithium signatures"
    
    try:
        signature = signer.sign(message, private_key)
        print("Signature successful, components:", list(signature.keys()))
        
        # Verify the signature
        is_valid = signer.verify(message, signature, public_key)
        print("Signature verification result:", is_valid)
    except Exception as e:
        print("Error during signing/verification:", str(e))
        import traceback
        traceback.print_exc()

def test_sphincs_direct():
    """Test the SPHINCS signature scheme directly."""
    print("\nTesting SPHINCS signature scheme directly...")
    
    # Initialize the signer
    signer = SPHINCSSignature(hash_algorithm='improved', h=8, fast_mode=True)
    
    try:
        # Generate a keypair
        private_key, public_key = signer.generate_keypair()
        
        # Print key details
        print("Private key type:", type(private_key))
        print("Private key length:", len(private_key))
        print("Public key type:", type(public_key))
        print("Public key length:", len(public_key))
        
        # Sign a message
        message = b"This is a test message for SPHINCS signatures"
        signature = signer.sign(message, private_key)
        
        # Print signature details
        print("Signature type:", type(signature))
        print("Signature length:", len(signature))
        
        # Verify the signature
        is_valid = signer.verify(message, signature, public_key)
        print("Signature verification result:", is_valid)
    except Exception as e:
        print("Error during SPHINCS testing:", str(e))
        import traceback
        traceback.print_exc()

def test_lamport_direct():
    """Test the Lamport signature scheme directly."""
    print("\nTesting Lamport signature scheme directly...")
    
    # Initialize the signer
    signer = LamportSignature(hash_algorithm='improved')
    
    try:
        # Generate a keypair
        private_key, public_key = signer.generate_keypair()
        
        # Print key details
        print("Private key type:", type(private_key))
        print("Private key length:", len(private_key))
        print("Private key[0] type:", type(private_key[0]))
        print("Public key type:", type(public_key))
        print("Public key length:", len(public_key))
        
        # Sign a message
        message = b"This is a test message for Lamport signatures"
        signature = signer.sign(message, private_key)
        
        # Print signature details
        print("Signature type:", type(signature))
        print("Signature length:", len(signature))
        
        # Verify the signature
        is_valid = signer.verify(message, signature, public_key)
        print("Signature verification result:", is_valid)
    except Exception as e:
        print("Error during Lamport testing:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing signature implementations directly...\n")
    
    test_dilithium_direct()
    test_sphincs_direct()
    test_lamport_direct() 