#!/usr/bin/env python3
"""
Debug script for the KEM implementation.
"""

import sys
import base64
import json
import traceback
from src.quantum_hash.kem.kyber import Kyber
from src.quantum_hash.signatures.kyber import KyberKEM as SignatureKyberKEM

def test_our_implementation():
    """Test our KEM implementation directly."""
    print("Testing our Kyber implementation")
    
    # Generate a key pair
    kyber = Kyber(security_level=1, hash_algorithm='improved')
    private_key, public_key = kyber.generate_keypair()
    
    print("Key pair generated:")
    print("- Public key structure:", public_key.keys())
    print("- Number of t elements:", len(public_key['t']))
    print("- Length of first t element (bytes):", len(public_key['t'][0]))
    
    # Encapsulate
    try:
        ciphertext, shared_secret_sender = kyber.encapsulate(public_key)
        print("\nEncapsulation successful:")
        print("- Ciphertext length:", len(ciphertext))
        print("- Shared secret:", shared_secret_sender.hex())
        
        # Decapsulate
        shared_secret_receiver = kyber.decapsulate(ciphertext, private_key)
        print("\nDecapsulation successful:")
        print("- Shared secret:", shared_secret_receiver.hex())
        
        # Check if shared secrets match
        print("\nShared secrets match:", shared_secret_sender == shared_secret_receiver)
    except Exception as e:
        print("\nError during encapsulation/decapsulation:", str(e))
        import traceback
        traceback.print_exc()

def test_old_implementation():
    """Test the KyberKEM from the signatures module."""
    print("\n\nTesting the original KyberKEM implementation")
    
    # Generate a key pair
    kyber = SignatureKyberKEM(security_level=1, hash_algorithm='improved')
    private_key, public_key = kyber.generate_keypair()
    
    print("Key pair generated:")
    print("- Public key structure:", public_key.keys())
    print("- Number of t elements:", len(public_key['t']))
    print("- Length of first t element (bytes):", len(public_key['t'][0]))
    
    # Encapsulate
    try:
        ciphertext, shared_secret_sender = kyber.encapsulate(public_key)
        print("\nEncapsulation successful:")
        print("- Ciphertext length:", len(ciphertext))
        print("- Shared secret:", shared_secret_sender.hex())
        
        # Decapsulate
        shared_secret_receiver = kyber.decapsulate(ciphertext, private_key)
        print("\nDecapsulation successful:")
        print("- Shared secret:", shared_secret_receiver.hex())
        
        # Check if shared secrets match
        print("\nShared secrets match:", shared_secret_sender == shared_secret_receiver)
    except Exception as e:
        print("\nError during encapsulation/decapsulation:", str(e))
        import traceback
        traceback.print_exc()

def test_api_simulation():
    """Simulate the API's processing of the keys."""
    print("\n\nSimulating API key processing")
    
    # Generate a key pair using our implementation
    kyber = Kyber(security_level=1, hash_algorithm='improved')
    private_key, public_key = kyber.generate_keypair()
    
    # Serialize the keys as in the API
    serialized_public_key = base64.b64encode(
        public_key['seed'] + b''.join(public_key['t'])
    ).decode('ascii')
    
    serialized_private_key = base64.b64encode(
        private_key['seed'] + b''.join(private_key['s'])
    ).decode('ascii')
    
    print("Keys serialized")
    print(f"Public key length (base64): {len(serialized_public_key)}")
    print(f"Private key length (base64): {len(serialized_private_key)}")
    
    # Deserialize the public key as in the API
    key_bytes = base64.b64decode(serialized_public_key)
    seed = key_bytes[:32]
    t_bytes = key_bytes[32:]
    
    print(f"Public key seed length: {len(seed)}")
    print(f"Public key t_bytes length: {len(t_bytes)}")
    
    # Parse t_bytes as in the API
    bytes_per_poly = 256 * 2  # 2 bytes per coefficient, 256 coefficients
    print(f"Expected bytes per polynomial: {bytes_per_poly}")
    
    # Create t list with proper length polynomials
    t = []
    num_polys = len(t_bytes) // bytes_per_poly
    print(f"Number of polynomials in t_bytes: {num_polys}")
    
    for i in range(num_polys):
        start = i * bytes_per_poly
        end = start + bytes_per_poly
        if start < len(t_bytes) and end <= len(t_bytes):
            t.append(t_bytes[start:end])
            print(f"Extracted polynomial {i+1}, length: {len(t_bytes[start:end])}")
        else:
            print(f"Error: t_bytes has length {len(t_bytes)}, "
                 f"but we expected at least {end} bytes for {i+1} polynomials")
    
    if not t:
        print("No polynomials could be extracted!")
        return
    
    deserialized_public_key = {
        'seed': seed,
        't': t
    }
    
    print("Public key deserialized")
    print(f"Number of polynomials in deserialized public key: {len(deserialized_public_key['t'])}")
    
    # Try to encapsulate with the deserialized public key
    try:
        ciphertext, shared_secret = kyber.encapsulate(deserialized_public_key)
        print("\nEncapsulation successful:")
        print("- Ciphertext length:", len(ciphertext))
        print("- Shared secret:", shared_secret.hex())
        
        # Now try to deserialize the private key
        key_bytes = base64.b64decode(serialized_private_key)
        seed = key_bytes[:32]
        s_bytes = key_bytes[32:]
        
        print(f"Private key seed length: {len(seed)}")
        print(f"Private key s_bytes length: {len(s_bytes)}")
        
        # Parse s_bytes
        s = []
        num_polys = len(s_bytes) // bytes_per_poly
        print(f"Number of polynomials in s_bytes: {num_polys}")
        
        for i in range(num_polys):
            start = i * bytes_per_poly
            end = start + bytes_per_poly
            if start < len(s_bytes) and end <= len(s_bytes):
                s.append(s_bytes[start:end])
                print(f"Extracted polynomial {i+1}, length: {len(s_bytes[start:end])}")
            else:
                print(f"Error: s_bytes has length {len(s_bytes)}, "
                     f"but we expected at least {end} bytes for {i+1} polynomials")
        
        if not s:
            print("No polynomials could be extracted from private key!")
            return
        
        deserialized_private_key = {
            'seed': seed,
            's': s
        }
        
        # Try to decapsulate
        shared_secret_decap = kyber.decapsulate(ciphertext, deserialized_private_key)
        print("\nDecapsulation successful:")
        print("- Shared secret:", shared_secret_decap.hex())
        print("\nShared secrets match:", shared_secret == shared_secret_decap)
        
    except Exception as e:
        print("\nError during encapsulation/decapsulation:", str(e))
        traceback.print_exc()

def test_direct_api_route_simulation():
    """Directly simulate the API route logic without the actual API."""
    print("\n\nDirect API route simulation")
    
    # Generate key pair
    kyber = Kyber(security_level=1, hash_algorithm='improved')
    private_key, public_key = kyber.generate_keypair()
    
    print("Key pair generated:")
    print("- Private key:", {k: f"<{len(v)} bytes>" if isinstance(v, bytes) else f"<{len(v)} items>" for k, v in private_key.items() if k != 'public_key'})
    print("- Public key:", {k: f"<{len(v)} bytes>" if isinstance(v, bytes) else f"<{len(v)} items>" for k, v in public_key.items()})
    
    # Simulate keypair route logic
    private_key_formatted = base64.b64encode(
        private_key['seed'] + b''.join(private_key['s'])
    ).decode('ascii')
    
    public_key_formatted = base64.b64encode(
        public_key['seed'] + b''.join(public_key['t'])
    ).decode('ascii')
    
    print("\nFormatted keys:")
    print("- Private key (base64):", f"<{len(private_key_formatted)} chars>")
    print("- Public key (base64):", f"<{len(public_key_formatted)} chars>")
    
    # Simulate encapsulate route logic
    try:
        # Parse formatted public key
        key_bytes = base64.b64decode(public_key_formatted)
        seed = key_bytes[:32]
        t_bytes = key_bytes[32:]
        
        print("\nParsing public key:")
        print("- Seed length:", len(seed))
        print("- t_bytes length:", len(t_bytes))
        
        # Parse t_bytes
        bytes_per_poly = 256 * 2  # 2 bytes per coefficient, 256 coefficients
        print("- Bytes per polynomial:", bytes_per_poly)
        
        t = []
        num_polys = len(t_bytes) // bytes_per_poly
        print("- Number of polynomials:", num_polys)
        
        for i in range(num_polys):
            start = i * bytes_per_poly
            end = start + bytes_per_poly
            if end <= len(t_bytes):
                t.append(t_bytes[start:end])
                print(f"  - Extracted polynomial {i+1}, length: {len(t_bytes[start:end])}")
        
        parsed_public_key = {
            'seed': seed,
            't': t
        }
        
        print("Parsed public key structure:", parsed_public_key.keys())
        
        # Encapsulate
        ciphertext, shared_secret = kyber.encapsulate(parsed_public_key)
        print("\nEncapsulation successful:")
        print("- Ciphertext length:", len(ciphertext))
        print("- Shared secret:", shared_secret.hex())
        
        # Format for response
        ciphertext_formatted = base64.b64encode(ciphertext).decode('ascii')
        
        # Simulate decapsulate route logic
        # Parse private key
        key_bytes = base64.b64decode(private_key_formatted)
        seed = key_bytes[:32]
        s_bytes = key_bytes[32:]
        
        print("\nParsing private key:")
        print("- Seed length:", len(seed))
        print("- s_bytes length:", len(s_bytes))
        
        # Parse s_bytes
        s = []
        num_polys = len(s_bytes) // bytes_per_poly
        print("- Number of polynomials:", num_polys)
        
        for i in range(num_polys):
            start = i * bytes_per_poly
            end = start + bytes_per_poly
            if end <= len(s_bytes):
                s.append(s_bytes[start:end])
                print(f"  - Extracted polynomial {i+1}, length: {len(s_bytes[start:end])}")
        
        parsed_private_key = {
            'seed': seed,
            's': s
        }
        
        print("Parsed private key structure:", parsed_private_key.keys())
        
        # Decapsulate
        decapsulated_secret = kyber.decapsulate(ciphertext, parsed_private_key)
        print("\nDecapsulation successful:")
        print("- Shared secret:", decapsulated_secret.hex())
        
        print("\nShared secrets match:", shared_secret == decapsulated_secret)
        
    except Exception as e:
        print("\nError:", str(e))
        traceback.print_exc()

if __name__ == "__main__":
    test_our_implementation()
    test_old_implementation()
    test_api_simulation()
    test_direct_api_route_simulation() 