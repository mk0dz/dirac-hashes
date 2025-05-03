#!/usr/bin/env python3
"""
Simple test script for the Dirac Hashes API.
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_hash_generate():
    """Test the basic hash generation endpoint."""
    print("\n=== Testing Hash Generation ===")
    url = f"{BASE_URL}/api/hash/generate"
    data = {
        "message": "Hello, world!",
        "algorithm": "grover",
        "encoding": "utf-8"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Hash generated.")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_signature_keypair():
    """Test the signature keypair generation endpoint."""
    print("\n=== Testing Signature Keypair Generation ===")
    url = f"{BASE_URL}/api/signatures/keypair"
    data = {
        "scheme": "lamport",
        "hash_algorithm": "grover",
        "security_level": 1
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Keypair generated.")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_kem_keypair():
    """Test the KEM keypair generation endpoint."""
    print("\n=== Testing KEM Keypair Generation ===")
    url = f"{BASE_URL}/api/kem/keypair"
    data = {
        "scheme": "kyber",
        "hash_algorithm": "grover",
        "security_level": 1
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! KEM keypair generated.")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("Starting simple API tests...")
    time.sleep(1)
    
    # Check if the API is running
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print(f"API server is not responding: {response.status_code}")
            return
        print("API server is running.")
    except requests.exceptions.ConnectionError:
        print("Cannot connect to API server. Make sure it's running.")
        return
    
    # Run tests
    hash_result = test_hash_generate()
    sig_result = test_signature_keypair()
    kem_result = test_kem_keypair()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Hash Generation: {'✅ PASSED' if hash_result else '❌ FAILED'}")
    print(f"Signature Keypair: {'✅ PASSED' if sig_result else '❌ FAILED'}")
    print(f"KEM Keypair: {'✅ PASSED' if kem_result else '❌ FAILED'}")

if __name__ == "__main__":
    main() 