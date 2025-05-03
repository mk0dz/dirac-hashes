#!/usr/bin/env python3
"""
Test script for working API endpoints (hash generation and KEM).
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"

def test_hash_api():
    """Test the hash generation API endpoints."""
    print("\n=== Testing Hash API ===")
    
    # Generate a hash
    print("\nGenerating hash...")
    hash_url = f"{BASE_URL}/hash/generate"
    hash_data = {
        "message": "Hello, hash world!",
        "algorithm": "grover",
        "encoding": "utf-8"
    }
    
    try:
        response = requests.post(hash_url, json=hash_data)
        if response.status_code == 200:
            result = response.json()
            print(f"Hash: {result['hash']}")
            print(f"Time: {result['time_ms']:.2f}ms")
            return True
        else:
            print(f"Error generating hash: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_full_kem_api():
    """Test the complete KEM workflow: keypair generation, encapsulation, and decapsulation."""
    print("\n=== Testing Complete KEM Workflow ===")
    
    # Generate keypair
    print("\nGenerating KEM keypair...")
    keypair_url = f"{BASE_URL}/kem/keypair"
    keypair_data = {
        "scheme": "kyber",
        "hash_algorithm": "grover",
        "security_level": 1
    }
    
    try:
        response = requests.post(keypair_url, json=keypair_data)
        if response.status_code != 200:
            print(f"Error generating KEM keypair: {response.text}")
            return False
        
        keypair = response.json()
        print(f"Generated KEM keypair in {keypair['time_ms']:.2f}ms")
        
        # Encapsulate a shared secret
        print("\nEncapsulating shared secret...")
        encap_url = f"{BASE_URL}/kem/encapsulate"
        encap_data = {
            "public_key": keypair["public_key"],
            "scheme": "kyber",
            "hash_algorithm": "grover",
            "security_level": 1
        }
        
        response = requests.post(encap_url, json=encap_data)
        if response.status_code != 200:
            print(f"Error encapsulating shared secret: {response.text}")
            return False
        
        encap_result = response.json()
        print(f"Encapsulated shared secret in {encap_result['time_ms']:.2f}ms")
        
        # Decapsulate the shared secret
        print("\nDecapsulating shared secret...")
        decap_url = f"{BASE_URL}/kem/decapsulate"
        decap_data = {
            "private_key": keypair["private_key"],
            "ciphertext": encap_result["ciphertext"],
            "scheme": "kyber",
            "hash_algorithm": "grover",
            "security_level": 1
        }
        
        response = requests.post(decap_url, json=decap_data)
        if response.status_code != 200:
            print(f"Error decapsulating shared secret: {response.text}")
            return False
        
        decap_result = response.json()
        print(f"Decapsulated shared secret in {decap_result['time_ms']:.2f}ms")
        
        # Verify that the shared secrets match
        if encap_result["shared_secret"] == decap_result["shared_secret"]:
            print("Shared secrets match! ✅")
            print(f"Secret: {decap_result['shared_secret'][:16]}...")
            return True
        else:
            print("Error: Shared secrets do not match ❌")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Starting API tests...")
    time.sleep(1)
    
    # Run tests
    hash_result = test_hash_api()
    kem_result = test_full_kem_api()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Hash API: {'✅ PASSED' if hash_result else '❌ FAILED'}")
    print(f"KEM API: {'✅ PASSED' if kem_result else '❌ FAILED'}")
    
    if hash_result and kem_result:
        print("\nAll tests passed successfully! 🎉")
        print("The hash and KEM endpoints are working correctly.")
        print("These endpoints can be safely used in the web frontend.")
    else:
        print("\nSome tests failed. Please check the output for details.")

if __name__ == "__main__":
    main() 