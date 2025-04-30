"""
Routes for digital signature API endpoints.
"""

import time
import binascii
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import base64

from src.quantum_hash.signatures.lamport import LamportSignature
from src.quantum_hash.signatures.sphincs import SPHINCSSignature
from src.quantum_hash.signatures.dilithium import DilithiumSignature

from api.models.signature_models import (
    SignatureScheme,
    KeyPairRequest,
    KeyPairResponse,
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse,
)
from api.routes.hash_routes import parse_message

router = APIRouter()


def get_signature_instance(scheme: SignatureScheme, hash_algorithm: str, security_level: int = 1):
    """Get the appropriate signature scheme instance."""
    try:
        if scheme == SignatureScheme.LAMPORT:
            return LamportSignature(hash_algorithm=hash_algorithm)
        elif scheme == SignatureScheme.SPHINCS:
            # Use reduced height for better performance
            return SPHINCSSignature(hash_algorithm=hash_algorithm, h=8, fast_mode=True)
        elif scheme == SignatureScheme.DILITHIUM:
            return DilithiumSignature(security_level=security_level, hash_algorithm=hash_algorithm)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported signature scheme: {scheme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing signature scheme: {str(e)}")


@router.post("/keypair", response_model=KeyPairResponse)
async def generate_keypair(request: KeyPairRequest):
    """Generate a key pair for the specified signature scheme."""
    try:
        # Get signature instance
        signer = get_signature_instance(
            request.scheme, 
            request.hash_algorithm.value,
            request.security_level
        )
        
        # Generate key pair
        start_time = time.time()
        private_key, public_key = signer.generate_keypair()
        end_time = time.time()
        
        # Format keys for response
        private_key_formatted = ""
        public_key_formatted = ""
        
        if request.scheme == SignatureScheme.LAMPORT:
            # For Lamport, serialize the dictionary structure
            private_key_bytes = []
            public_key_bytes = []
            
            # Each key entry is a dictionary with sk/pk
            for i in range(len(private_key)):
                private_key_bytes.append(private_key[i]['sk'])
                public_key_bytes.append(public_key[i]['pk'])
            
            private_key_formatted = binascii.hexlify(
                b''.join(private_key_bytes)
            ).decode('ascii')
            public_key_formatted = binascii.hexlify(
                b''.join(public_key_bytes)
            ).decode('ascii')
        elif request.scheme == SignatureScheme.SPHINCS:
            # SPHINCS returns a dictionary structure
            # Serialize seed, sk_seed, and prf_seed for private key
            private_key_bytes = private_key['seed'] + private_key['sk_seed'] + private_key['prf_seed']
            # Serialize seed and root for public key
            public_key_bytes = public_key['seed'] + public_key['root']
            
            private_key_formatted = binascii.hexlify(private_key_bytes).decode('ascii')
            public_key_formatted = binascii.hexlify(public_key_bytes).decode('ascii')
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, we need to serialize the dictionary
            private_key_formatted = base64.b64encode(
                private_key['rho'] + b''.join(private_key['s'])
            ).decode('ascii')
            public_key_formatted = base64.b64encode(
                public_key['rho'] + b''.join(public_key['t'])
            ).decode('ascii')
        
        # Format response
        return KeyPairResponse(
            private_key=private_key_formatted,
            public_key=public_key_formatted,
            scheme=request.scheme.value,
            hash_algorithm=request.hash_algorithm.value,
            security_level=request.security_level,
            time_ms=(end_time - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating key pair: {str(e)}")


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
            key_entry_size = 32  # Each public key is 32 bytes
            public_key = []
            for i in range(len(key_bytes) // key_entry_size):
                start = i * key_entry_size
                end = start + key_entry_size
                public_key.append({'pk': key_bytes[start:end]})
                
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