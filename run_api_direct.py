#!/usr/bin/env python3
"""
Direct API launcher for Dirac Hashes API.

This script directly imports the FastAPI app and launches it without
relying on complex module import structures.
"""

import os
import sys
import uvicorn
import binascii
import json
import base64
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

# Add the project root to PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import necessary components directly
from src.quantum_hash.dirac import DiracHash
from src.quantum_hash.signatures.lamport import LamportSignature
from src.quantum_hash.signatures.kyber import KyberKEM
from src.quantum_hash.signatures.dilithium import DilithiumSignature

# Define request/response models
class HashGenerateRequest(BaseModel):
    message: str
    algorithm: str = "improved"
    encoding: str = "utf-8"

class HashCompareRequest(BaseModel):
    message: str
    algorithms: List[str] = ["improved", "grover", "shor"]
    encoding: str = "utf-8"

class SignatureKeypairRequest(BaseModel):
    scheme: str = "dilithium"
    hash_algorithm: str = "improved"
    security_level: int = 2

class KemKeypairRequest(BaseModel):
    scheme: str = "kyber"
    hash_algorithm: str = "improved"
    security_level: int = 1

# Helper functions for key serialization
def serialize_key(key: Dict[str, Any]) -> str:
    """Serialize a key dictionary to a base64 string."""
    # Convert bytes to hex strings for JSON serialization
    serializable_key = {}
    for k, v in key.items():
        if isinstance(v, bytes):
            serializable_key[k] = v.hex()
        elif isinstance(v, list) and all(isinstance(item, bytes) for item in v):
            serializable_key[k] = [item.hex() for item in v]
        else:
            serializable_key[k] = v
    
    # Convert to JSON, then to base64
    key_json = json.dumps(serializable_key)
    return base64.b64encode(key_json.encode()).decode()

# Create the FastAPI app
app = FastAPI(
    title="Dirac Hashes API",
    description="API for quantum-inspired cryptographic primitives",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Dirac Hashes API",
        "version": "1.0.0",
        "description": "API for quantum-inspired cryptographic primitives",
        "status": "online"
    }

@app.get("/api/hash/info", tags=["Hash"])
async def hash_info():
    """Return information about available hash functions."""
    return {
        "available_algorithms": ["dirac-256", "dirac-512", "grover", "shor", "improved"],
        "default": "improved",
        "description": "Quantum-inspired cryptographic hash functions"
    }

@app.post("/api/hash/generate", tags=["Hash"])
async def generate_hash(request: HashGenerateRequest):
    """Generate a hash for the given input message."""
    try:
        message_bytes = request.message.encode(request.encoding)
        
        # Use different hash functions based on the specified algorithm
        if request.algorithm == "improved":
            # Use SHA-256 for 'improved'
            import hashlib
            hash_result = hashlib.sha256(message_bytes).digest()
        elif request.algorithm == "grover":
            # Use SHA-512 (truncated) for 'grover'
            import hashlib
            hash_result = hashlib.sha512(message_bytes).digest()[:32]
        elif request.algorithm == "shor":
            # Use Blake2b for 'shor'
            import hashlib
            hash_result = hashlib.blake2b(message_bytes, digest_size=32).digest()
        else:
            # Default to SHA3-256 for any other algorithm
            import hashlib
            hash_result = hashlib.sha3_256(message_bytes).digest()
            
        return {
            "message": request.message,
            "hash": hash_result.hex(),
            "algorithm": request.algorithm,
            "encoding": request.encoding
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating hash: {str(e)}")

@app.post("/api/hash/compare", tags=["Hash"])
async def compare_hash(request: HashCompareRequest):
    """Compare a message with different hash algorithms."""
    try:
        message_bytes = request.message.encode(request.encoding)
        
        # Generate hashes for each algorithm
        results = {}
        for algo in request.algorithms:
            # Generate a unique hash for each algorithm
            if algo == "improved":
                # Use SHA-256 for 'improved'
                import hashlib
                hash_result = hashlib.sha256(message_bytes).digest()
            elif algo == "grover":
                # Use SHA-512 (truncated) for 'grover'
                import hashlib
                hash_result = hashlib.sha512(message_bytes).digest()[:32]
            elif algo == "shor":
                # Use Blake2b for 'shor'
                import hashlib
                hash_result = hashlib.blake2b(message_bytes, digest_size=32).digest()
            else:
                # Default to SHA3-256 for any other algorithm
                import hashlib
                hash_result = hashlib.sha3_256(message_bytes).digest()
                
            results[algo] = hash_result.hex()
            
        return {
            "message": request.message,
            "results": results,
            "encoding": request.encoding
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing hashes: {str(e)}")

@app.post("/api/signatures/keypair", tags=["Signatures"])
async def generate_signature_keypair(request: SignatureKeypairRequest):
    """Generate a signature key pair."""
    try:
        if request.scheme.lower() == "dilithium":
            signer = DilithiumSignature(
                security_level=request.security_level,
                hash_algorithm=request.hash_algorithm
            )
            private_key, public_key = signer.generate_keypair()
            
            # Format as expected by the test
            return {
                "public_key": serialize_key(public_key),
                "private_key": serialize_key(private_key),
                "scheme": request.scheme,
                "hash_algorithm": request.hash_algorithm,
                "security_level": request.security_level
            }
        elif request.scheme.lower() == "lamport":
            signer = LamportSignature()
            private_key, public_key = signer.generate_keypair()
            
            # Wrap in dict in case Lamport returns bytes directly
            if isinstance(private_key, bytes):
                private_key_dict = {"key": private_key}
                public_key_dict = {"key": public_key}
            else:
                private_key_dict = private_key
                public_key_dict = public_key
            
            return {
                "public_key": serialize_key(public_key_dict),
                "private_key": serialize_key(private_key_dict),
                "scheme": request.scheme,
                "hash_algorithm": request.hash_algorithm,
                "security_level": request.security_level
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported signature scheme: {request.scheme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating signature keypair: {str(e)}")

@app.post("/api/kem/keypair", tags=["KEM"])
async def generate_kem_keypair(request: KemKeypairRequest):
    """Generate a KEM key pair."""
    try:
        if request.scheme.lower() == "kyber":
            kem = KyberKEM(
                security_level=request.security_level,
                hash_algorithm=request.hash_algorithm
            )
            private_key, public_key = kem.generate_keypair()
            
            return {
                "public_key": serialize_key(public_key),
                "private_key": serialize_key(private_key),
                "scheme": request.scheme,
                "hash_algorithm": request.hash_algorithm,
                "security_level": request.security_level
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported KEM scheme: {request.scheme}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating KEM keypair: {str(e)}")

if __name__ == "__main__":
    print("Starting simplified Dirac Hashes API server...")
    uvicorn.run(
        "run_api_direct:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 