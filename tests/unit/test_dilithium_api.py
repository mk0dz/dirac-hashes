#!/usr/bin/env python3
"""
Simplified test script for the Dilithium signature API.
"""

import requests
import json
import base64
import binascii
import traceback
import pytest

# Base URL for API
BASE_URL = "http://localhost:8000/api"

def test_dilithium_directly():
    """Test Dilithium signature directly without the API"""
    from src.quantum_hash.signatures.dilithium import DilithiumSignature
    
    print("Testing Dilithium directly...")
    
    try:
        # Create signer
        signer = DilithiumSignature(security_level=1, hash_algorithm='improved')
        
        # Generate keypair
        private_key, public_key = signer.generate_keypair()
        
        # Print key details
        print("Private key contains:", list(private_key.keys()))
        print("Private key 's' length:", len(private_key['s']))
        print("Private key 's[0]' type:", type(private_key['s'][0]))
        
        # Print public key details
        print("Public key contains:", list(public_key.keys()))
        print("Public key 't' length:", len(public_key['t']))
        
        # Sign a message
        message = b"Test message for Dilithium"
        signature = signer.sign(message, private_key)
        
        # Print signature details
        print("Signature contains:", list(signature.keys()))
        
        # Verify signature
        is_valid = signer.verify(message, signature, public_key)
        print("Signature verification result:", is_valid)
        assert is_valid == True
        
    except Exception as e:
        print("Error during direct test:", str(e))
        traceback.print_exc()
        assert False, str(e)

def test_dilithium_api():
    """Test the Dilithium signature API endpoints"""
    print("\nTesting Dilithium API...")
    
    try:
        # 1. Generate keypair
        print("\n1. Generating keypair...")
        response = requests.post(
            f"{BASE_URL}/signatures/keypair",
            json={
                "scheme": "dilithium",
                "hash_algorithm": "improved",
                "security_level": 1
            }
        )
        
        # Check response
        if response.status_code != 200:
            print(f"Error generating keypair: {response.text}")
            assert False, f"API error: {response.text}"
        
        keypair = response.json()
        print("Keypair generated successfully")
        
        # Decode the private key for debugging
        private_key_bytes = base64.b64decode(keypair["private_key"])
        print("Private key length:", len(private_key_bytes))
        print("First 32 bytes (rho):", binascii.hexlify(private_key_bytes[:32]).decode())
        
        assert keypair["private_key"] is not None
        assert keypair["public_key"] is not None
        
        # Store keys in module-level variables for other tests
        global test_private_key, test_public_key
        test_private_key = keypair["private_key"]
        test_public_key = keypair["public_key"]
        
    except Exception as e:
        print("Error during API test:", str(e))
        traceback.print_exc()
        assert False, str(e)

@pytest.fixture
def keypair():
    """Fixture to provide a keypair for tests"""
    # Call the API to get a keypair
    response = requests.post(
        f"{BASE_URL}/signatures/keypair",
        json={
            "scheme": "dilithium",
            "hash_algorithm": "improved",
            "security_level": 1
        }
    )
    
    if response.status_code != 200:
        pytest.fail(f"Error generating keypair: {response.text}")
    
    keypair = response.json()
    return keypair["private_key"], keypair["public_key"]

@pytest.fixture
def test_message():
    """Fixture to provide a test message"""
    return "Test message for Dilithium API"

@pytest.fixture
def test_signature(keypair, test_message):
    """Fixture to provide a signature for tests"""
    private_key, _ = keypair
    
    try:
        # Sign a message
        response = requests.post(
            f"{BASE_URL}/signatures/sign",
            json={
                "scheme": "dilithium",
                "hash_algorithm": "improved",
                "message": test_message,
                "private_key": private_key
            }
        )
        
        # Check response
        if response.status_code != 200:
            pytest.fail(f"Error signing message: {response.text}")
            
        signature_data = response.json()
        return signature_data["signature"]
        
    except Exception as e:
        pytest.fail(f"Error during signing: {str(e)}")

def test_signing(keypair, test_message):
    """Test signing with the API"""
    private_key, _ = keypair
        
    try:
        # Sign a message
        print("\n2. Signing message...")
        
        response = requests.post(
            f"{BASE_URL}/signatures/sign",
            json={
                "scheme": "dilithium",
                "hash_algorithm": "improved",
                "message": test_message,
                "private_key": private_key
            }
        )
        
        # Check response
        if response.status_code != 200:
            print(f"Error signing message: {response.text}")
            assert False, f"API error: {response.text}"
            
        signature_data = response.json()
        print("Message signed successfully")
        print("Signature size:", signature_data["signature_size_bytes"], "bytes")
        
        assert signature_data["signature"] is not None
        assert signature_data["signature_size_bytes"] > 0
        
    except Exception as e:
        print("Error during signing test:", str(e))
        traceback.print_exc()
        assert False, str(e)

def test_verification(keypair, test_message, test_signature):
    """Test verification with the API"""
    _, public_key = keypair
        
    try:
        # Verify signature
        print("\n3. Verifying signature...")
        
        response = requests.post(
            f"{BASE_URL}/signatures/verify",
            json={
                "scheme": "dilithium",
                "hash_algorithm": "improved",
                "message": test_message,
                "signature": test_signature,
                "public_key": public_key
            }
        )
        
        # Check response
        if response.status_code != 200:
            print(f"Error verifying signature: {response.text}")
            assert False, f"API error: {response.text}"
            
        verify_data = response.json()
        print("Verification result:", verify_data["is_valid"])
        
        assert verify_data["is_valid"] == True
        
    except Exception as e:
        print("Error during verification test:", str(e))
        traceback.print_exc()
        assert False, str(e)

if __name__ == "__main__":
    print("Testing Dilithium signature functionality\n")
    
    # First test directly
    test_dilithium_directly()
    
    # Then test through API
    test_dilithium_api()
    
    # If keypair generation works, try signing
    if test_private_key and test_public_key:
        message = "Test message for Dilithium API"
        
        # Create a test signature
        response = requests.post(
            f"{BASE_URL}/signatures/sign",
            json={
                "scheme": "dilithium",
                "hash_algorithm": "improved",
                "message": message,
                "private_key": test_private_key
            }
        )
        
        if response.status_code == 200:
            signature_data = response.json()
            signature = signature_data["signature"]
            
            # If signing works, try verification
            if signature:
                test_verification({"private_key": test_private_key, "public_key": test_public_key}, message, signature) 