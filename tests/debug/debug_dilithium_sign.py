#!/usr/bin/env python3
"""
Debug the Dilithium sign method step by step.
"""

import base64
import binascii
import traceback
import requests

from src.quantum_hash.signatures.dilithium import DilithiumSignature

def manual_sign_test():
    """Test the Dilithium sign method manually with the same input as the API"""
    # First get a keypair from the API
    response = requests.post(
        "http://localhost:8000/api/signatures/keypair",
        json={
            "scheme": "dilithium",
            "hash_algorithm": "improved",
            "security_level": 1
        }
    )
    
    if response.status_code != 200:
        print(f"Error generating keypair: {response.text}")
        return
    
    keypair = response.json()
    api_private_key = keypair["private_key"]
    
    # Decode the private key
    private_key_bytes = base64.b64decode(api_private_key)
    print(f"Private key from API length: {len(private_key_bytes)} bytes")
    
    # Extract components 
    rho = private_key_bytes[:32]
    s_bytes = private_key_bytes[32:]
    print(f"  - rho length: {len(rho)} bytes")
    print(f"  - s_bytes length: {len(s_bytes)} bytes")
    
    # Create the private key dictionary manually
    print("\nCreating private key dictionary manually...")
    sigma = rho  # Using rho as sigma for simplicity
    
    # Try different approaches to parsing s_bytes
    # Original, directly using s_bytes
    private_key1 = {
        'rho': rho,
        'sigma': sigma,
        's': [s_bytes],
        'e': [s_bytes],
        't': [s_bytes]
    }
    
    # Manual decoding attempting to split into individual elements
    size_per_element = len(s_bytes) // 2  # Guess for test
    s_elements = []
    for i in range(2):  # Split into 2 elements
        start = i * size_per_element
        end = start + size_per_element
        s_elements.append(s_bytes[start:end])
    
    private_key2 = {
        'rho': rho,
        'sigma': sigma,
        's': s_elements,
        'e': s_elements,
        't': s_elements
    }
    
    # Test both approaches
    print("\nTrying method 1 (single element)...")
    try_sign_with_key(private_key1)
    
    print("\nTrying method 2 (split elements)...")
    try_sign_with_key(private_key2)
    
    # Generate a clean keypair and try that
    print("\nTrying a fresh keypair...")
    try_sign_with_fresh_keypair()

def try_sign_with_key(private_key):
    """Try signing with the given private key"""
    try:
        # Create signer
        signer = DilithiumSignature(security_level=1, hash_algorithm='improved')
        
        # Print key details
        print(f"Private key 's' has {len(private_key['s'])} elements")
        print(f"First element type: {type(private_key['s'][0])}, length: {len(private_key['s'][0])}")
        
        # Sign a message
        message = b"Test message for Dilithium"
        print("Signing message...")
        signature = signer.sign(message, private_key)
        
        print("Signing successful!")
    except Exception as e:
        print(f"Error during signing: {str(e)}")
        traceback.print_exc()

def try_sign_with_fresh_keypair():
    """Generate a fresh keypair and try signing"""
    try:
        # Create signer
        signer = DilithiumSignature(security_level=1, hash_algorithm='improved')
        
        # Generate keypair
        private_key, public_key = signer.generate_keypair()
        
        # Print key details
        print(f"Fresh private key 's' has {len(private_key['s'])} elements")
        for i, s_elem in enumerate(private_key['s']):
            print(f"  - Element {i} type: {type(s_elem)}, length: {len(s_elem)}")
        
        # Sign a message
        message = b"Test message for Dilithium"
        print("Signing message...")
        signature = signer.sign(message, private_key)
        
        print("Signing successful!")
        print("Signature contains:", list(signature.keys()))
        
        # Verify signature
        is_valid = signer.verify(message, signature, public_key)
        print("Signature verification result:", is_valid)
    except Exception as e:
        print(f"Error during signing: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Debugging Dilithium signing process\n")
    manual_sign_test() 