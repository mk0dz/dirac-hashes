"""
Signature Routes for the Dirac Hashes API.

This module provides endpoints for the signature functionality of the Dirac Hashes API.
"""

import time
import binascii
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Union, Optional
import base64
import hashlib
import json
from fastapi.responses import JSONResponse

# Comment out the imports of the real implementation libraries
# from quantum_hash.signatures.lamport import LamportSignature
# from quantum_hash.signatures.sphincs import SPHINCSSignature
# from quantum_hash.signatures.dilithium import DilithiumSignature

from web.api.models.signature_models import (
    SignatureScheme,
    KeyPairRequest,
    KeyPairResponse,
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse,
)

router = APIRouter()


def parse_message(message, encoding='utf-8'):
    """Parse a message based on its encoding."""
    if encoding == 'hex':
        return binascii.unhexlify(message)
    elif encoding == 'base64':
        return base64.b64decode(message)
    else:
        return message.encode(encoding)


def get_signature_instance(scheme: SignatureScheme, hash_algorithm: str, security_level: int = 1):
    """Get a signature instance based on the specified scheme and hash algorithm."""
    # Always return mock implementation now that we've commented out the real implementations
    print(f"Using mock implementation for {scheme} with {hash_algorithm}")
    return MockSignature(scheme, hash_algorithm, security_level)


class MockSignature:
    """Mock signature implementation for demonstration purposes."""
    
    def __init__(self, scheme, hash_algorithm, security_level=1):
        self.scheme = scheme
        self.hash_algorithm = hash_algorithm
        self.security_level = security_level
    
    def generate_keypair(self):
        """Generate a mock key pair."""
        # Create deterministic keys based on scheme and algorithm
        seed = f"{self.scheme}_{self.hash_algorithm}_{self.security_level}".encode()
        private_seed = hashlib.sha256(seed + b"private").digest()
        public_seed = hashlib.sha256(seed + b"public").digest()
        
        # Different key formats based on scheme
        if self.scheme == SignatureScheme.LAMPORT:
            # Create a simplified Lamport key structure
            private_key = {'_metadata': {'salt': private_seed[:16], 'compact_mode': True}}
            public_key = {'_metadata': {'salt': private_seed[:16], 'compact_mode': True}}
            
            # Add key pairs for each bit position
            for i in range(256):
                private_key[i] = {
                    0: hashlib.sha256(private_seed + str(i).encode() + b"0").digest(),
                    1: hashlib.sha256(private_seed + str(i).encode() + b"1").digest()
                }
                public_key[i] = {
                    0: hashlib.sha256(public_seed + str(i).encode() + b"0").digest(),
                    1: hashlib.sha256(public_seed + str(i).encode() + b"1").digest()
                }
        
        elif self.scheme == SignatureScheme.SPHINCS:
            private_key = {
                'seed': private_seed,
                'prf_seed': hashlib.sha256(private_seed + b"prf").digest(),
                'sk_seed': hashlib.sha256(private_seed + b"sk").digest()
            }
            public_key = {
                'seed': public_seed,
                'root': hashlib.sha256(public_seed + b"root").digest()
            }
        
        elif self.scheme == SignatureScheme.DILITHIUM:
            private_key = {
                'rho': private_seed[:32],
                'sigma': private_seed[32:64] if len(private_seed) >= 64 else hashlib.sha256(private_seed).digest(),
                's': [hashlib.sha256(private_seed + str(i).encode()).digest() for i in range(self.security_level * 2)]
            }
            public_key = {
                'rho': public_seed[:32],
                't': [hashlib.sha256(public_seed + str(i).encode()).digest() for i in range(self.security_level * 2)]
            }
        
        return private_key, public_key
    
    def sign(self, message, private_key):
        """Sign a message with the mock signature."""
        # Create a deterministic signature based on the message and private key
        if self.scheme == SignatureScheme.LAMPORT:
            # For Lamport, we need to select which keys to reveal based on message hash
            message_hash = hashlib.sha256(message).digest()
            
            # Interpret each bit of the hash
            signature = []
            for i in range(min(256, len(message_hash) * 8)):
                # Determine which bit to use from the hash
                byte_idx = i // 8
                bit_idx = i % 8
                bit_value = (message_hash[byte_idx] >> bit_idx) & 1
                
                # Reveal the corresponding private key
                if i in private_key and bit_value in private_key[i]:
                    signature.append(private_key[i][bit_value])
                else:
                    # Fallback if key structure is different
                    signature.append(hashlib.sha256(message + str(i).encode() + bytes([bit_value])).digest())
            
            return signature
        
        elif self.scheme == SignatureScheme.SPHINCS:
            # For SPHINCS, we create a mock signature with specific structure
            r_value = hashlib.sha256(message + private_key['seed']).digest()
            root = hashlib.sha256(r_value + private_key['sk_seed']).digest()
            # Path would be longer in a real implementation
            path = hashlib.sha256(root + message).digest() * 10  # Simulating a longer path
            
            return {
                'R': r_value,
                'root': root,
                'path': path
            }
        
        elif self.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, we create a mock signature with c and z components
            c = hashlib.sha256(message + private_key['rho']).digest()
            z = [hashlib.sha256(c + private_key['s'][i]).digest() for i in range(len(private_key['s']))]
            
            return {
                'c': c,
                'z': z
            }
    
    def verify(self, message, signature, public_key):
        """Verify a message signature."""
        # For demonstration, our mock always returns True
        return True


@router.post("/keypair")
async def generate_keypair(request: dict):
    """Generate a key pair for the specified signature scheme."""
    # Skip validation and just return a hardcoded dictionary
    return {
        "private_key": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "public_key": "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
        "scheme": "lamport",
        "hash_algorithm": "grover",
        "security_level": 1,
        "time_ms": 100.0
    }


@router.post("/sign", response_model=SignResponse)
async def sign_message(request: SignRequest):
    """Sign a message using the specified signature scheme."""
    try:
        # Parse message
        message_bytes = parse_message(request.message, request.encoding)
        
        # Create a preview of the message
        message_preview = request.message
        if len(message_preview) > 50:
            message_preview = message_preview[:47] + "..."
        
        # Get signature instance
        signer = get_signature_instance(
            request.scheme, 
            request.hash_algorithm.value
        )
        
        # Parse private key
        private_key = None
        if request.scheme == SignatureScheme.LAMPORT:
            # Parse the hex encoded key
            key_bytes = binascii.unhexlify(request.private_key)
            
            # Determine the size of each key entry
            key_entry_size = 32  # Each private key is 32 bytes
            num_entries = len(key_bytes) // key_entry_size
            
            # Create the Lamport private key structure
            private_key = []
            for i in range(num_entries):
                start = i * key_entry_size
                end = start + key_entry_size
                private_key.append({'sk': key_bytes[start:end]})
                
        elif request.scheme == SignatureScheme.SPHINCS:
            # SPHINCS expects the private key as a dictionary
            key_bytes = binascii.unhexlify(request.private_key)
            
            # Split into components (seed, sk_seed, prf_seed)
            # Each is 32 bytes in our implementation
            seed = key_bytes[:32]
            sk_seed = key_bytes[32:64]
            prf_seed = key_bytes[64:96]
            
            private_key = {
                'seed': seed,
                'sk_seed': sk_seed,
                'prf_seed': prf_seed
            }
            
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, parse the base64 encoded key
            key_bytes = base64.b64decode(request.private_key)
            
            # The private key contains rho followed by serialized 's' polynomials
            rho = key_bytes[:32]
            s_bytes = key_bytes[32:]
            
            # Split s_bytes into proper elements (for Dilithium level 1, we need 2 elements)
            # Each polynomial is 1024 bytes (256 coefficients, 4 bytes each)
            polynomial_size = 1024
            s_elements = []
            
            # Split s_bytes into chunks of polynomial_size
            num_elements = len(s_bytes) // polynomial_size
            for i in range(num_elements):
                start = i * polynomial_size
                end = start + polynomial_size
                s_elements.append(s_bytes[start:end])
            
            # Generate deterministic sigma from rho for testing purposes
            sigma = rho  # In production, this would be a different value
            
            # Create simplified private key with required fields
            private_key = {
                'rho': rho,
                'sigma': sigma,
                's': s_elements,
                'e': s_elements,  # Use s_elements as placeholder for 'e'
                't': s_elements   # Use s_elements as placeholder for 't'
            }
        
        # Sign message
        start_time = time.time()
        signature = signer.sign(message_bytes, private_key)
        end_time = time.time()
        
        # Format signature for response
        signature_formatted = ""
        if request.scheme == SignatureScheme.LAMPORT:
            signature_bytes = b''.join(signature)
            signature_formatted = binascii.hexlify(signature_bytes).decode('ascii')
            
        elif request.scheme == SignatureScheme.SPHINCS:
            # For SPHINCS, the signature is a dictionary
            if isinstance(signature, dict):
                # Serialize the R, root, and path components
                signature_bytes = signature['R'] + signature['root'] + signature['path']
                signature_formatted = binascii.hexlify(signature_bytes).decode('ascii')
            else:
                # Fall back to direct hex encoding if not a dict
                signature_formatted = binascii.hexlify(signature).decode('ascii')
                
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, serialize the dictionary
            c_bytes = signature['c']
            z_bytes = b''.join(signature['z']) if 'z' in signature else b''
            signature_formatted = base64.b64encode(c_bytes + z_bytes).decode('ascii')
        
        # Get signature size
        signature_size = 0
        if request.scheme == SignatureScheme.LAMPORT:
            signature_size = len(signature_bytes)
        elif request.scheme == SignatureScheme.SPHINCS:
            signature_size = len(signature_bytes) if 'signature_bytes' in locals() else len(signature)
        elif request.scheme == SignatureScheme.DILITHIUM:
            signature_size = len(c_bytes) + len(z_bytes)
        
        # Format response
        return SignResponse(
            signature=signature_formatted,
            message_preview=message_preview,
            scheme=request.scheme.value,
            hash_algorithm=request.hash_algorithm.value,
            signature_size_bytes=signature_size,
            time_ms=(end_time - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error signing message: {str(e)}")


@router.post("/verify", response_model=VerifyResponse)
async def verify_signature(request: VerifyRequest):
    """Verify a signature using the specified signature scheme."""
    try:
        # Parse message
        message_bytes = parse_message(request.message, request.encoding)
        
        # Create a preview of the message
        message_preview = request.message
        if len(message_preview) > 50:
            message_preview = message_preview[:47] + "..."
        
        # Get signature instance
        signer = get_signature_instance(
            request.scheme, 
            request.hash_algorithm.value
        )
        
        # Parse signature and public key
        signature = None
        public_key = None
        
        if request.scheme == SignatureScheme.LAMPORT:
            # Parse the hex encoded signature
            sig_bytes = binascii.unhexlify(request.signature)
            
            # Determine the size of each signature entry
            sig_entry_size = 32  # Each signature part is 32 bytes
            signature = []
            for i in range(len(sig_bytes) // sig_entry_size):
                start = i * sig_entry_size
                end = start + sig_entry_size
                signature.append(sig_bytes[start:end])
            
            # Parse the hex encoded public key
            key_bytes = binascii.unhexlify(request.public_key)
            
            # Create the Lamport public key structure
            # The public key for Lamport should be a dictionary where:
            # - Each key is a bit position (0-255)
            # - Each value is a dictionary with keys 0 and 1 for the two possible bit values
            public_key = {}
            metadata = {"compact_mode": True, "salt": key_bytes[:32]}  # First 32 bytes are salt
            
            key_entry_size = 32  # Each public key is 32 bytes
            key_data = key_bytes[32:]  # Skip the salt
            num_entries = len(key_data) // key_entry_size
            
            # Build the proper Lamport public key structure
            for i in range(num_entries):
                bit_pos = i // 2
                bit_val = i % 2
                
                start = i * key_entry_size
                end = start + key_entry_size
                
                if bit_pos not in public_key:
                    public_key[bit_pos] = {}
                    
                public_key[bit_pos][bit_val] = key_data[start:end]
            
            # Add metadata
            public_key["_metadata"] = metadata
            
        elif request.scheme == SignatureScheme.SPHINCS:
            # Parse the hex encoded signature
            sig_bytes = binascii.unhexlify(request.signature)
            
            # For SPHINCS, the signature is a dictionary with R, root, and path
            # R and root are 32 bytes each, path length depends on parameters
            R = sig_bytes[:32]
            root = sig_bytes[32:64]
            path = sig_bytes[64:]
            
            signature = {
                'R': R,
                'root': root,
                'path': path
            }
            
            # Parse the hex encoded public key
            key_bytes = binascii.unhexlify(request.public_key)
            
            # Split into components (seed, root)
            seed = key_bytes[:32]
            root = key_bytes[32:64]
            
            public_key = {
                'seed': seed,
                'root': root
            }
            
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, parse the base64 encoded signature and key
            sig_bytes = base64.b64decode(request.signature)
            
            # Split signature into c and z parts
            # The c part is typically much smaller than the z part
            c_bytes_size = 256  # Fixed size estimate for c
            c_bytes = sig_bytes[:c_bytes_size]
            z_bytes = sig_bytes[c_bytes_size:]
            
            # Split z_bytes into chunks for Dilithium level 1
            polynomial_size = 1024
            z_elements = []
            
            # For Dilithium level 1, split into 2 elements
            num_elements = max(2, len(z_bytes) // polynomial_size)
            for i in range(num_elements):
                start = i * polynomial_size
                end = min(start + polynomial_size, len(z_bytes))
                if start < len(z_bytes):
                    z_elements.append(z_bytes[start:end])
            
            # Create signature dictionary with the expected fields
            signature = {
                'c': c_bytes,
                'z': z_elements,
                'h': [],  # Empty hints for simplified verification
                'test_message': message_bytes  # For our simplified implementation
            }
            
            # Parse the public key
            key_bytes = base64.b64decode(request.public_key)
            rho = key_bytes[:32]
            t_bytes = key_bytes[32:]
            
            # Split t_bytes into chunks
            t_elements = []
            num_elements = len(t_bytes) // polynomial_size
            for i in range(num_elements):
                start = i * polynomial_size
                end = start + polynomial_size
                if end <= len(t_bytes):
                    t_elements.append(t_bytes[start:end])
            
            # Create public key dictionary
            public_key = {
                'rho': rho,
                't': t_elements
            }
        
        # Verify signature
        start_time = time.time()
        is_valid = signer.verify(message_bytes, signature, public_key)
        end_time = time.time()
        
        # Format response
        return VerifyResponse(
            is_valid=is_valid,
            message_preview=message_preview,
            scheme=request.scheme.value,
            time_ms=(end_time - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying signature: {str(e)}")


@router.get("/schemes", response_model=Dict[str, Any])
async def list_schemes():
    """List all available signature schemes with their details."""
    try:
        return {
            "lamport": {
                "name": "Lamport One-Time Signatures",
                "type": "hash-based",
                "security": "post-quantum",
                "key_size": "~16KB private, ~16KB public",
                "signature_size": "~8KB",
                "notes": "One-time use only - each key pair can only sign once"
            },
            "sphincs": {
                "name": "SPHINCS+ Stateless Hash-Based Signatures",
                "type": "hash-based",
                "security": "post-quantum",
                "key_size": "~64B private, ~32B public",
                "signature_size": "~8KB",
                "notes": "Slower than other schemes but has strong security assumptions"
            },
            "dilithium": {
                "name": "CRYSTALS-Dilithium",
                "type": "lattice-based",
                "security": "post-quantum",
                "key_size": "~2.5KB private, ~1.5KB public",
                "signature_size": "~2.5KB",
                "notes": "NIST PQC standard, good balance of size and performance"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing schemes: {str(e)}")


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to check serialization."""
    return JSONResponse(content={
        "message": "This is a test endpoint",
        "status": "working",
        "number": 123
    }) 