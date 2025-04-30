#!/usr/bin/env python3
"""
Test script for the Dirac Hashes API.

This script makes requests to the API to verify that it's working correctly.
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_hash_generate():
    """Test the hash generation endpoint."""
    print("\n=== Testing Hash Generation ===")
    data = {
        "message": "Hello, quantum world!",
        "algorithm": "improved",
        "encoding": "utf-8"
    }
    response = requests.post(f"{API_URL}/api/hash/generate", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_hash_compare():
    """Test the hash comparison endpoint."""
    print("\n=== Testing Hash Comparison ===")
    data = {
        "message": "Hello, quantum world!",
        "algorithms": ["improved", "grover", "shor"],
        "encoding": "utf-8"
    }
    response = requests.post(f"{API_URL}/api/hash/compare", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_signature_keypair():
    """Test the signature key pair generation endpoint."""
    print("\n=== Testing Signature Key Pair Generation ===")
    data = {
        "scheme": "dilithium",
        "hash_algorithm": "improved",
        "security_level": 2
    }
    response = requests.post(f"{API_URL}/api/signatures/keypair", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        # Truncate the keys for display
        result["public_key"] = result["public_key"][:50] + "..."
        result["private_key"] = result["private_key"][:50] + "..."
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Response: {response.text}")
    return response.status_code == 200

def test_kem_keypair():
    """Test the KEM key pair generation endpoint."""
    print("\n=== Testing KEM Key Pair Generation ===")
    data = {
        "scheme": "kyber",
        "hash_algorithm": "improved",
        "security_level": 1
    }
    response = requests.post(f"{API_URL}/api/kem/keypair", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        # Truncate the keys for display
        result["public_key"] = result["public_key"][:50] + "..."
        result["private_key"] = result["private_key"][:50] + "..."
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Response: {response.text}")
    return response.status_code == 200

def main():
    """Run all tests."""
    print("=== Dirac Hashes API Test Script ===")
    print(f"Testing API at {API_URL}")
    
    # Wait for the API to start
    time.sleep(1)
    
    # Run tests
    results = {
        "root": test_root(),
        "hash_generate": test_hash_generate(),
        "hash_compare": test_hash_compare(),
        "signature_keypair": test_signature_keypair(),
        "kem_keypair": test_kem_keypair()
    }
    
    # Print summary
    print("\n=== Test Summary ===")
    for test, result in results.items():
        print(f"{test}: {'✓ PASSED' if result else '✗ FAILED'}")
    
    # Return success if all tests passed
    return all(results.values())

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1) 