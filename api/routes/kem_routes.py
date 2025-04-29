"""
Routes for Key Encapsulation Mechanism (KEM) API endpoints.
"""

import time
import binascii
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import base64

from src.quantum_hash.kem.kyber import Kyber as KyberKEM

from api.models.kem_models import (
    KEMScheme,
    KEMKeyPairRequest,
    KEMKeyPairResponse,
    EncapsulateRequest,
    EncapsulateResponse,
    DecapsulateRequest,
    DecapsulateResponse,
)

router = APIRouter()


def get_kem_instance(scheme: KEMScheme, hash_algorithm: str, security_level: int = 1):
    """Get the appropriate KEM scheme instance."""
    try:
        if scheme == KEMScheme.KYBER:
            return KyberKEM(security_level=security_level, hash_algorithm=hash_algorithm)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported KEM scheme: {scheme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing KEM scheme: {str(e)}")


@router.post("/keypair", response_model=KEMKeyPairResponse)
async def generate_kem_keypair(request: KEMKeyPairRequest):
    """Generate a key pair for the specified KEM scheme."""
    try:
        # Get KEM instance
        kem = get_kem_instance(
            request.scheme, 
            request.hash_algorithm.value,
            request.security_level
        )
        
        # Generate key pair
        start_time = time.time()
        private_key, public_key = kem.generate_keypair()
        end_time = time.time()
        
        # Format keys for response
        private_key_formatted = ""
        public_key_formatted = ""
        
        if request.scheme == KEMScheme.KYBER:
            # Serialize the Kyber keys
            private_key_formatted = base64.b64encode(
                private_key['seed'] + b''.join(private_key['s'])
            ).decode('ascii')
            public_key_formatted = base64.b64encode(
                public_key['seed'] + b''.join(public_key['t'])
            ).decode('ascii')
        
        # Format response
        return KEMKeyPairResponse(
            private_key=private_key_formatted,
            public_key=public_key_formatted,
            scheme=request.scheme.value,
            hash_algorithm=request.hash_algorithm.value,
            security_level=request.security_level,
            time_ms=(end_time - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating KEM key pair: {str(e)}")


@router.post("/encapsulate", response_model=EncapsulateResponse)
async def encapsulate_key(request: EncapsulateRequest):
    """Encapsulate a shared secret using the specified KEM scheme."""
    try:
        # Get KEM instance
        kem = get_kem_instance(
            request.scheme, 
            request.hash_algorithm.value,
            request.security_level
        )
        
        # Parse public key
        public_key = None
        if request.scheme == KEMScheme.KYBER:
            # Parse the base64 encoded key
            key_bytes = base64.b64decode(request.public_key)
            seed = key_bytes[:32]
            t_bytes = key_bytes[32:]
            
            # In a typical KYBER implementation, 't' is an array of polynomial byte representations
            # The polynomial size depends on n = 256 and each coefficient is 2 bytes
            # So each polynomial is 512 bytes
            bytes_per_poly = 256 * 2  # 2 bytes per coefficient, 256 coefficients
            
            # Extract all available polynomials from t_bytes
            t = []
            num_polys = len(t_bytes) // bytes_per_poly
            for i in range(num_polys):
                start = i * bytes_per_poly
                end = start + bytes_per_poly
                if end <= len(t_bytes):
                    t.append(t_bytes[start:end])
            
            if not t:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid public key format: could not extract any polynomials from t_bytes (length {len(t_bytes)})"
                )
            
            public_key = {
                'seed': seed,
                't': t
            }
        
        # Encapsulate shared secret
        start_time = time.time()
        ciphertext, shared_secret = kem.encapsulate(public_key)
        end_time = time.time()
        
        # Format for response
        ciphertext_formatted = base64.b64encode(ciphertext).decode('ascii')
        shared_secret_formatted = shared_secret.hex()
        
        # Format response
        return EncapsulateResponse(
            ciphertext=ciphertext_formatted,
            shared_secret=shared_secret_formatted,
            scheme=request.scheme.value,
            ciphertext_size_bytes=len(ciphertext),
            time_ms=(end_time - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encapsulating shared secret: {str(e)}")


@router.post("/decapsulate", response_model=DecapsulateResponse)
async def decapsulate_key(request: DecapsulateRequest):
    """Decapsulate a shared secret using the specified KEM scheme."""
    try:
        # Get KEM instance
        kem = get_kem_instance(
            request.scheme, 
            request.hash_algorithm.value,
            request.security_level
        )
        
        # Parse private key and ciphertext
        private_key = None
        ciphertext = None
        
        if request.scheme == KEMScheme.KYBER:
            # Parse the base64 encoded key
            key_bytes = base64.b64decode(request.private_key)
            seed = key_bytes[:32]
            s_bytes = key_bytes[32:]
            
            # In a typical KYBER implementation, 's' is an array of polynomial byte representations
            # The polynomial size depends on n = 256 and each coefficient is 2 bytes
            # So each polynomial is 512 bytes
            bytes_per_poly = 256 * 2  # 2 bytes per coefficient, 256 coefficients
            
            # Extract all available polynomials from s_bytes
            s = []
            num_polys = len(s_bytes) // bytes_per_poly
            for i in range(num_polys):
                start = i * bytes_per_poly
                end = start + bytes_per_poly
                if end <= len(s_bytes):
                    s.append(s_bytes[start:end])
            
            if not s:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid private key format: could not extract any polynomials from s_bytes (length {len(s_bytes)})"
                )
            
            private_key = {
                'seed': seed,
                's': s
            }
            
            # Parse ciphertext
            ciphertext = base64.b64decode(request.ciphertext)
        
        # Decapsulate shared secret
        start_time = time.time()
        shared_secret = kem.decapsulate(ciphertext, private_key)
        end_time = time.time()
        
        # Format for response
        shared_secret_formatted = shared_secret.hex()
        
        # Format response
        return DecapsulateResponse(
            shared_secret=shared_secret_formatted,
            scheme=request.scheme.value,
            time_ms=(end_time - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error decapsulating shared secret: {str(e)}")


@router.get("/schemes", response_model=Dict[str, Any])
async def list_kem_schemes():
    """List all available KEM schemes with their details."""
    try:
        return {
            "kyber": {
                "name": "CRYSTALS-Kyber",
                "type": "lattice-based",
                "security": "post-quantum",
                "key_size": "~1KB private, ~1KB public",
                "ciphertext_size": "~1.5KB",
                "shared_secret_size": "32 bytes",
                "security_levels": {
                    "1": "Kyber-512 (equivalent to AES-128)",
                    "3": "Kyber-768 (equivalent to AES-192)",
                    "5": "Kyber-1024 (equivalent to AES-256)"
                },
                "notes": "NIST PQC standard, selected for key encapsulation"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing KEM schemes: {str(e)}") 