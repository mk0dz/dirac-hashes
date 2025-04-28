"""
Data models for hash function API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class HashAlgorithm(str, Enum):
    """Valid hash algorithms"""
    IMPROVED = "improved"
    GROVER = "grover"
    SHOR = "shor"
    HYBRID = "hybrid"
    IMPROVED_GROVER = "improved_grover"
    IMPROVED_SHOR = "improved_shor"


class HashRequest(BaseModel):
    """Request model for hash generation."""
    message: str = Field(..., description="Message to hash")
    algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.IMPROVED, 
        description="Hash algorithm to use"
    )
    encoding: str = Field(
        default="utf-8", 
        description="Message encoding (utf-8, hex, base64)"
    )


class HashResponse(BaseModel):
    """Response model for hash generation."""
    hash: str = Field(..., description="Generated hash in hex format")
    algorithm: str = Field(..., description="Algorithm used")
    message_preview: str = Field(..., description="Preview of the input message")
    digest_length: int = Field(..., description="Length of hash digest in bytes")
    time_ms: float = Field(..., description="Time taken to hash in milliseconds")


class HashComparisonRequest(BaseModel):
    """Request model for comparing multiple hash algorithms."""
    message: str = Field(..., description="Message to hash")
    algorithms: List[HashAlgorithm] = Field(
        default=[algo for algo in HashAlgorithm],
        description="List of algorithms to compare"
    )
    encoding: str = Field(
        default="utf-8", 
        description="Message encoding (utf-8, hex, base64)"
    )


class HashComparisonResponse(BaseModel):
    """Response model for hash comparison."""
    message_preview: str = Field(..., description="Preview of the input message")
    results: Dict[str, Any] = Field(..., description="Hash results for each algorithm") 