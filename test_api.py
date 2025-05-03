#!/usr/bin/env python3
"""
Test script for the Dirac Hashes API.

This script tests the signature and KEM API endpoints to ensure they're working correctly.
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"

def test_signature_api():
    """Test the signature API endpoints."""
    print("\n=== Testing Signature API ===")
    
    # Generate a keypair
    print("\nGenerating keypair...")
    keypair_url = f"{BASE_URL}/signatures/keypair"
    keypair_data = {
        "scheme": "lamport",
        "hash_algorithm": "grover",
        "security_level": 1
    }
    
    response = requests.post(keypair_url, json=keypair_data)
    if response.status_code != 200:
        print(f"Error generating keypair: {response.status_code}")
        print(f"Response: {response.text}")
        try:
            detail = response.json().get('detail', 'No detail provided')
            print(f"Detail: {detail}")
        except:
            print(f"Could not parse response as JSON: {response.text}")
        return False
    
    keypair = response.json()
    print(f"Generated keypair in {keypair['time_ms']:.2f}ms")
    
    # Sign a message
    print("\nSigning message...")
    sign_url = f"{BASE_URL}/signatures/sign"
    sign_data = {
        "message": "This is a test message to sign",
        "private_key": keypair["private_key"],
        "scheme": "lamport",
        "hash_algorithm": "grover"
    }
    
    response = requests.post(sign_url, json=sign_data)
    if response.status_code != 200:
        print(f"Error signing message: {response.text}")
        return False
    
    signature_result = response.json()
    print(f"Message signed in {signature_result['time_ms']:.2f}ms")
    
    # Verify the signature
    print("\nVerifying signature...")
    verify_url = f"{BASE_URL}/signatures/verify"
    verify_data = {
        "message": "This is a test message to sign",
        "signature": signature_result["signature"],
        "public_key": keypair["public_key"],
        "scheme": "lamport",
        "hash_algorithm": "grover"
    }
    
    response = requests.post(verify_url, json=verify_data)
    if response.status_code != 200:
        print(f"Error verifying signature: {response.text}")
        return False
    
    verify_result = response.json()
    print(f"Signature verified: {verify_result['valid']}")
    
    return True

def test_kem_api():
    """Test the KEM API endpoints."""
    print("\n=== Testing KEM API ===")
    
    # Generate a keypair
    print("\nGenerating keypair...")
    keypair_url = f"{BASE_URL}/kem/keypair"
    keypair_data = {
        "scheme": "kyber",
        "hash_algorithm": "grover",
        "security_level": 1
    }
    
    response = requests.post(keypair_url, json=keypair_data)
    if response.status_code != 200:
        print(f"Error generating keypair: {response.status_code}")
        print(f"Response: {response.text}")
        try:
            detail = response.json().get('detail', 'No detail provided')
            print(f"Detail: {detail}")
        except:
            print(f"Could not parse response as JSON: {response.text}")
        return False
    
    keypair = response.json()
    print(f"Generated keypair in {keypair['time_ms']:.2f}ms")
    
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
    print(f"Shared secret encapsulated in {encap_result['time_ms']:.2f}ms")
    
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
    print(f"Shared secret decapsulated in {decap_result['time_ms']:.2f}ms")
    
    # Verify that the shared secrets match
    if encap_result["shared_secret"] == decap_result["shared_secret"]:
        print("Shared secrets match! ✅")
        return True
    else:
        print("Error: Shared secrets do not match ❌")
        return False

def check_server():
    """Check if the server is running and return basic info."""
    try:
        response = requests.get(BASE_URL.split('/api')[0])
        if response.status_code != 200:
            print(f"API server is not responding correctly: {response.status_code}")
            return False
        
        info = response.json()
        print(f"Server is running: {info.get('name', 'Unknown')} v{info.get('version', 'Unknown')}")
        return True
    except requests.exceptions.ConnectionError:
        print("Cannot connect to API server. Make sure it's running.")
        return False

def main():
    """Run all tests."""
    print("Starting API tests - make sure the API server is running...")
    time.sleep(1)
    
    # Check if the API is running
    if not check_server():
        return
    
    # Run tests
    sig_result = test_signature_api()
    kem_result = test_kem_api()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Signature API: {'✅ PASSED' if sig_result else '❌ FAILED'}")
    print(f"KEM API: {'✅ PASSED' if kem_result else '❌ FAILED'}")
    
    if sig_result and kem_result:
        print("\nAll tests passed successfully! 🎉")
    else:
        print("\nSome tests failed. Please check the output for details.")

if __name__ == "__main__":
    main() 