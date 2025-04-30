"""
Routes for hash function API endpoints.
"""

import time
import binascii
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import base64

from src.quantum_hash.dirac import DiracHash
from api.models.hash_models import (
    HashRequest, 
    HashResponse, 
    HashComparisonRequest,
    HashComparisonResponse
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
    """Compare multiple hash algorithms on the same input message."""
    try:
        # Parse message
        message_bytes = parse_message(request.message, request.encoding)
        
        # Create a preview of the message
        message_preview = request.message
        if len(message_preview) > 50:
            message_preview = message_preview[:47] + "..."
        
        # Generate hashes for each algorithm using static method
        results = {}
        for algo in request.algorithms:
            start_time = time.time()
            digest = DiracHash.hash(message_bytes, algorithm=algo.value)
            end_time = time.time()
            
            results[algo.value] = {
                "hash": digest.hex(),
                "digest_length": len(digest),
                "time_ms": (end_time - start_time) * 1000
            }
        
        # Format response
        return HashComparisonResponse(
            message_preview=message_preview,
            results=results
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