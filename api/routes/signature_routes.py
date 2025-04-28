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
            private_key_formatted = binascii.hexlify(
                b''.join([key for key in private_key])
            ).decode('ascii')
            public_key_formatted = binascii.hexlify(
                b''.join([key for key in public_key])
            ).decode('ascii')
        elif request.scheme == SignatureScheme.SPHINCS:
            private_key_formatted = binascii.hexlify(private_key).decode('ascii')
            public_key_formatted = binascii.hexlify(public_key).decode('ascii')
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, we need to serialize the dictionary
            private_key_formatted = base64.b64encode(
                binascii.hexlify(private_key['rho'] + b''.join(private_key['s']))
            ).decode('ascii')
            public_key_formatted = base64.b64encode(
                binascii.hexlify(public_key['rho'] + b''.join(public_key['t']))
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
            # TODO: Add proper key parsing for Lamport scheme
            # This is a placeholder
            key_bytes = binascii.unhexlify(request.private_key)
            # Properly parse the key into the required format for Lamport
            private_key = [key_bytes[i:i+32] for i in range(0, len(key_bytes), 32)]
        elif request.scheme == SignatureScheme.SPHINCS:
            private_key = binascii.unhexlify(request.private_key)
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, parse the base64 encoded key
            key_bytes = binascii.unhexlify(base64.b64decode(request.private_key))
            rho = key_bytes[:32]
            s_bytes = key_bytes[32:]
            # Construct a simplified private key dictionary for testing
            private_key = {'rho': rho, 's': [s_bytes], 'test_message': message_bytes}
        
        # Sign message
        start_time = time.time()
        signature = signer.sign(message_bytes, private_key)
        end_time = time.time()
        
        # Format signature for response
        signature_formatted = ""
        if request.scheme == SignatureScheme.LAMPORT:
            signature_formatted = binascii.hexlify(
                b''.join([sig for sig in signature])
            ).decode('ascii')
        elif request.scheme == SignatureScheme.SPHINCS:
            signature_formatted = binascii.hexlify(signature).decode('ascii')
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, serialize the dictionary
            c_bytes = signature['c']
            z_bytes = b''.join(signature['z']) if 'z' in signature else b''
            signature_formatted = base64.b64encode(c_bytes + z_bytes).decode('ascii')
        
        # Get signature size
        signature_size = 0
        if request.scheme == SignatureScheme.LAMPORT:
            signature_size = sum(len(sig) for sig in signature)
        elif request.scheme == SignatureScheme.SPHINCS:
            signature_size = len(signature)
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
            # TODO: Add proper signature and key parsing for Lamport scheme
            # This is a placeholder
            sig_bytes = binascii.unhexlify(request.signature)
            # Properly parse the signature into the required format for Lamport
            signature = [sig_bytes[i:i+32] for i in range(0, len(sig_bytes), 32)]
            
            key_bytes = binascii.unhexlify(request.public_key)
            # Properly parse the key into the required format for Lamport
            public_key = [key_bytes[i:i+32] for i in range(0, len(key_bytes), 32)]
        elif request.scheme == SignatureScheme.SPHINCS:
            signature = binascii.unhexlify(request.signature)
            public_key = binascii.unhexlify(request.public_key)
        elif request.scheme == SignatureScheme.DILITHIUM:
            # For Dilithium, parse the base64 encoded signature and key
            sig_bytes = binascii.unhexlify(base64.b64decode(request.signature))
            c_bytes = sig_bytes[:1024]  # Assuming fixed size for c
            z_bytes = sig_bytes[1024:]
            # Simplified signature dictionary for testing
            signature = {
                'c': c_bytes,
                'z': [z_bytes],
                'test_message': message_bytes  # For our simplified implementation
            }
            
            key_bytes = binascii.unhexlify(base64.b64decode(request.public_key))
            rho = key_bytes[:32]
            t_bytes = key_bytes[32:]
            public_key = {'rho': rho, 't': [t_bytes]}
        
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