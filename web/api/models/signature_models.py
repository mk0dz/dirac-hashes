"""
Data models for signature API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from web.api.models.hash_models import HashAlgorithm


class SignatureScheme(str, Enum):
    """Valid signature schemes"""
    LAMPORT = "lamport"
    SPHINCS = "sphincs"
    DILITHIUM = "dilithium"


class KeyPairRequest(BaseModel):
    """Request model for key pair generation."""
    scheme: SignatureScheme = Field(
        ..., 
        description="Signature scheme to use"
    )
    hash_algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.IMPROVED, 
        description="Hash algorithm to use"
    )
    security_level: int = Field(
        default=2, 
        description="Security level (1-5, higher is more secure but slower)",
        ge=1, 
        le=5
    )
    
    
class KeyPairResponse(BaseModel):
    """Response model for key pair generation."""
    public_key: str = Field(..., description="Public key in hex format")
    private_key: str = Field(..., description="Private key in hex format")
    scheme: str = Field(..., description="Signature scheme used")
    hash_algorithm: str = Field(..., description="Hash algorithm used")
    security_level: int = Field(..., description="Security level used")
    time_ms: float = Field(..., description="Time taken to generate in milliseconds")


class SignRequest(BaseModel):
    """Request model for message signing."""
    message: str = Field(..., description="Message to sign")
    private_key: str = Field(..., description="Private key in hex format")
    scheme: SignatureScheme = Field(
        ..., 
        description="Signature scheme to use"
    )
    hash_algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.IMPROVED, 
        description="Hash algorithm to use"
    )
    encoding: str = Field(
        default="utf-8", 
        description="Message encoding (utf-8, hex, base64)"
    )


class SignResponse(BaseModel):
    """Response model for message signing."""
    signature: str = Field(..., description="Signature in hex format")
    message_preview: str = Field(..., description="Preview of the input message")
    scheme: str = Field(..., description="Signature scheme used")
    hash_algorithm: str = Field(..., description="Hash algorithm used")
    signature_size_bytes: int = Field(..., description="Size of signature in bytes")
    time_ms: float = Field(..., description="Time taken to sign in milliseconds")


class VerifyRequest(BaseModel):
    """Request model for signature verification."""
    message: str = Field(..., description="Original message")
    signature: str = Field(..., description="Signature in hex format")
    public_key: str = Field(..., description="Public key in hex format")
    scheme: SignatureScheme = Field(
        ..., 
        description="Signature scheme to use"
    )
    hash_algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.IMPROVED, 
        description="Hash algorithm to use"
    )
    encoding: str = Field(
        default="utf-8", 
        description="Message encoding (utf-8, hex, base64)"
    )


class VerifyResponse(BaseModel):
    """Response model for signature verification."""
    is_valid: bool = Field(..., description="Whether the signature is valid")
    message_preview: str = Field(..., description="Preview of the input message")
    scheme: str = Field(..., description="Signature scheme used")
    time_ms: float = Field(..., description="Time taken to verify in milliseconds") 