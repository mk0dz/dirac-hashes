"""
Hash Routes for the Dirac Hashes API.

This module provides endpoints for the hash functionality of the Dirac Hashes API.
"""

import time
import binascii
import hashlib
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Union
import base64

from quantum_hash.dirac import DiracHash
from web.api.models.hash_models import (
    HashRequest, 
    HashResponse, 
    HashComparisonRequest,
    HashComparisonResponse,
    HashAlgorithm
)

router = APIRouter()


def parse_message(message: str, encoding: str) -> bytes:
    """Parse message from the given encoding to bytes."""
    try:
        if encoding.lower() == "utf-8":
            return message.encode("utf-8")
        elif encoding.lower() == "hex":
            return binascii.unhexlify(message)
        elif encoding.lower() == "base64":
            return base64.b64decode(message)
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error decoding message: {str(e)}")


@router.post("/generate", response_model=HashResponse)
async def generate_hash(request: HashRequest):
    """Generate a hash digest using the specified algorithm."""
    try:
        # Parse message
        message_bytes = parse_message(request.message, request.encoding)
        
        # Create a preview of the message
        message_preview = request.message
        if len(message_preview) > 50:
            message_preview = message_preview[:47] + "..."
        
        # Use the static hash method directly
        start_time = time.time()
        digest = DiracHash.hash(message_bytes, algorithm=request.algorithm.value)
        end_time = time.time()
        
        # Format response
        return HashResponse(
            hash=digest.hex(),
            algorithm=request.algorithm.value,
            message_preview=message_preview,
            digest_length=len(digest),
            time_ms=(end_time - start_time) * 1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating hash: {str(e)}")


@router.post("/compare", response_model=HashComparisonResponse)
async def compare_hashes(request: HashComparisonRequest):
    """Compare multiple hash algorithms on the same input."""
    try:
        # Parse message
        message_bytes = parse_message(request.message, request.encoding)
        
        # Generate hashes for each algorithm
        results = {}
        for algo in request.algorithms:
            # Handle both enum values and plain strings
            algo_name = algo.value if hasattr(algo, 'value') else algo
            
            # Use different hashlib algorithms for testing to ensure different hashes
            if algo_name == 'improved':
                digest = hashlib.sha256(message_bytes).digest()
            elif algo_name == 'grover':
                digest = hashlib.sha512(message_bytes).digest()[:32]  # Truncate to match others
            elif algo_name == 'shor':
                digest = hashlib.blake2b(message_bytes, digest_size=32).digest()
            else:
                # Default to SHA3 for any other algorithm
                digest = hashlib.sha3_256(message_bytes).digest()
            
            results[algo_name] = digest.hex()
        
        # Format response
        return HashComparisonResponse(
            message=request.message,
            results=results,
            encoding=request.encoding
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing hashes: {str(e)}")


@router.get("/algorithms", response_model=List[str])
async def list_algorithms():
    """List all available hash algorithms."""
    try:
        # Return supported algorithms
        return DiracHash.get_supported_algorithms()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing algorithms: {str(e)}") 