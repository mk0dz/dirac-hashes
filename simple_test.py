#!/usr/bin/env python3
"""
Simple test script for the Dirac Hashes API test endpoint.
"""

import requests
import json

# Test the simple test endpoint
print("Testing /api/signatures/test endpoint...")
url = "http://localhost:8000/api/signatures/test"

try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Response:")
        print(response.json())
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {str(e)}") 