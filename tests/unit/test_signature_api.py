#!/usr/bin/env python3
"""
Test script for the signature API.
"""

import requests
import json

# Base URL for API
BASE_URL = "http://localhost:8000/api"

def test_dilithium_signature():
    """Test the Dilithium signature scheme through the API."""
    print("Testing Dilithium signature API...")
    
    # 1. Generate a keypair
    print("\n1. Generating keypair...")
    keypair_response = requests.post(
        f"{BASE_URL}/signatures/keypair",
        json={
            "scheme": "dilithium",
            "hash_algorithm": "improved", 
            "security_level": 1
        }
    )
    
    if keypair_response.status_code != 200:
        print(f"Error generating keypair: {keypair_response.text}")
        return
    
    keypair = keypair_response.json()
    print(f"Keypair generated successfully in {keypair['time_ms']:.2f}ms")
    
    # 2. Sign a message
    message = "This is a test message for Dilithium signatures"
    print(f"\n2. Signing message: '{message}'")
    
    sign_response = requests.post(
        f"{BASE_URL}/signatures/sign",
        json={
            "scheme": "dilithium",
            "hash_algorithm": "improved", 
            "message": message,
            "private_key": keypair["private_key"],
            "encoding": "utf-8"
        }
    )
    
    if sign_response.status_code != 200:
        print(f"Error signing message: {sign_response.text}")
        return
    
    signature_result = sign_response.json()
    print(f"Message signed successfully in {signature_result['time_ms']:.2f}ms")
    print(f"Signature size: {signature_result['signature_size_bytes']} bytes")
    
    # 3. Verify the signature
    print("\n3. Verifying signature...")
    verify_response = requests.post(
        f"{BASE_URL}/signatures/verify",
        json={
            "scheme": "dilithium",
            "hash_algorithm": "improved", 
            "message": message,
            "signature": signature_result["signature"],
            "public_key": keypair["public_key"],
            "encoding": "utf-8"
        }
    )
    
    if verify_response.status_code != 200:
        print(f"Error verifying signature: {verify_response.text}")
        return
    
    verify_result = verify_response.json()
    print(f"Signature verification completed in {verify_result['time_ms']:.2f}ms")
    print(f"Signature valid: {verify_result['is_valid']}")

def test_sphincs_signature():
    """Test the SPHINCS signature scheme through the API."""
    print("\nTesting SPHINCS signature API...")
    
    # 1. Generate a keypair
    print("\n1. Generating keypair...")
    keypair_response = requests.post(
        f"{BASE_URL}/signatures/keypair",
        json={
            "scheme": "sphincs",
            "hash_algorithm": "improved", 
            "security_level": 1
        }
    )
    
    if keypair_response.status_code != 200:
        print(f"Error generating keypair: {keypair_response.text}")
        return
    
    keypair = keypair_response.json()
    print(f"Keypair generated successfully in {keypair['time_ms']:.2f}ms")
    
    # 2. Sign a message
    message = "This is a test message for SPHINCS signatures"
    print(f"\n2. Signing message: '{message}'")
    
    sign_response = requests.post(
        f"{BASE_URL}/signatures/sign",
        json={
            "scheme": "sphincs",
            "hash_algorithm": "improved", 
            "message": message,
            "private_key": keypair["private_key"],
            "encoding": "utf-8"
        }
    )
    
    if sign_response.status_code != 200:
        print(f"Error signing message: {sign_response.text}")
        return
    
    signature_result = sign_response.json()
    print(f"Message signed successfully in {signature_result['time_ms']:.2f}ms")
    print(f"Signature size: {signature_result['signature_size_bytes']} bytes")
    
    # 3. Verify the signature
    print("\n3. Verifying signature...")
    verify_response = requests.post(
        f"{BASE_URL}/signatures/verify",
        json={
            "scheme": "sphincs",
            "hash_algorithm": "improved", 
            "message": message,
            "signature": signature_result["signature"],
            "public_key": keypair["public_key"],
            "encoding": "utf-8"
        }
    )
    
    if verify_response.status_code != 200:
        print(f"Error verifying signature: {verify_response.text}")
        return
    
    verify_result = verify_response.json()
    print(f"Signature verification completed in {verify_result['time_ms']:.2f}ms")
    print(f"Signature valid: {verify_result['is_valid']}")

def test_lamport_signature():
    """Test the Lamport signature scheme through the API."""
    print("\nTesting Lamport signature API...")
    
    # 1. Generate a keypair
    print("\n1. Generating keypair...")
    keypair_response = requests.post(
        f"{BASE_URL}/signatures/keypair",
        json={
            "scheme": "lamport",
            "hash_algorithm": "improved", 
            "security_level": 1
        }
    )
    
    if keypair_response.status_code != 200:
        print(f"Error generating keypair: {keypair_response.text}")
        return
    
    keypair = keypair_response.json()
    print(f"Keypair generated successfully in {keypair['time_ms']:.2f}ms")
    
    # 2. Sign a message
    message = "This is a test message for Lamport signatures"
    print(f"\n2. Signing message: '{message}'")
    
    sign_response = requests.post(
        f"{BASE_URL}/signatures/sign",
        json={
            "scheme": "lamport",
            "hash_algorithm": "improved", 
            "message": message,
            "private_key": keypair["private_key"],
            "encoding": "utf-8"
        }
    )
    
    if sign_response.status_code != 200:
        print(f"Error signing message: {sign_response.text}")
        return
    
    signature_result = sign_response.json()
    print(f"Message signed successfully in {signature_result['time_ms']:.2f}ms")
    print(f"Signature size: {signature_result['signature_size_bytes']} bytes")
    
    # 3. Verify the signature
    print("\n3. Verifying signature...")
    verify_response = requests.post(
        f"{BASE_URL}/signatures/verify",
        json={
            "scheme": "lamport",
            "hash_algorithm": "improved", 
            "message": message,
            "signature": signature_result["signature"],
            "public_key": keypair["public_key"],
            "encoding": "utf-8"
        }
    )
    
    if verify_response.status_code != 200:
        print(f"Error verifying signature: {verify_response.text}")
        return
    
    verify_result = verify_response.json()
    print(f"Signature verification completed in {verify_result['time_ms']:.2f}ms")
    print(f"Signature valid: {verify_result['is_valid']}")

if __name__ == "__main__":
    print("Testing signature API endpoints...\n")
    
    # Get the list of available schemes
    schemes_response = requests.get(f"{BASE_URL}/signatures/schemes")
    if schemes_response.status_code == 200:
        schemes = schemes_response.json()
        print(f"Available signature schemes: {', '.join(schemes.keys())}")
    else:
        print(f"Error retrieving signature schemes: {schemes_response.text}")
    
    # Test each signature scheme
    test_dilithium_signature()
    test_sphincs_signature()
    test_lamport_signature()
    
    print("\nAll tests completed!") 