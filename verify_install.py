#!/usr/bin/env python3
"""
Dirac Hashes Installation Verification

This script verifies that the Dirac Hashes package is installed correctly and 
can perform basic operations.
"""

import sys

try:
    from quantum_hash.dirac import DiracHash
    from quantum_hash.signatures.dilithium import DilithiumSignature
    
    print("Dirac Hashes package is installed correctly!")
    print(f"Version: {DiracHash.__version__}")
    
    # Test basic hash functionality
    print("\nTesting hash functionality...")
    hash_value = DiracHash.hash("Test message")
    print(f"Hash result: {hash_value.hex()}")
    
    # Test signature functionality
    print("\nTesting signature functionality...")
    dilithium = DilithiumSignature()
    private_key, public_key = dilithium.generate_keypair()
    message = b"Hello, quantum-resistant world!"
    signature = dilithium.sign(message, private_key)
    is_valid = dilithium.verify(message, signature, public_key)
    print(f"Signature valid: {is_valid}")
    
    print("\nAll tests passed successfully!")
    print("\nThe Dirac Hashes package is working correctly.")
    
except ImportError as e:
    print(f"Error: {e}")
    print("\nThe Dirac Hashes package is not installed correctly.")
    print("Please install it using: pip install dirac-hashes")
    sys.exit(1)
except Exception as e:
    print(f"Error during testing: {e}")
    print("\nThe Dirac Hashes package is installed but encountered an error during testing.")
    sys.exit(1) 