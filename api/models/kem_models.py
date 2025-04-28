"""
Data models for Key Encapsulation Mechanism (KEM) API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from api.models.hash_models import HashAlgorithm


class KEMScheme(str, Enum):
    """Valid KEM schemes"""
    KYBER = "kyber"


class KEMKeyPairRequest(BaseModel):
    """Request model for KEM key pair generation."""
    scheme: KEMScheme = Field(
        default=KEMScheme.KYBER,
        description="KEM scheme to use"
    )
    hash_algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.IMPROVED, 
        description="Hash algorithm to use"
    )
    security_level: int = Field(
        default=1,
        description="Security level (1, 3, or 5 for Kyber-512, Kyber-768, Kyber-1024)",
        ge=1,
        le=5
    )


class KEMKeyPairResponse(BaseModel):
    """Response model for KEM key pair generation."""
    public_key: str = Field(..., description="Public key in hex format")
    private_key: str = Field(..., description="Private key in hex format")
    scheme: str = Field(..., description="KEM scheme used")
    hash_algorithm: str = Field(..., description="Hash algorithm used")
    security_level: int = Field(..., description="Security level used")
    time_ms: float = Field(..., description="Time taken to generate in milliseconds")


class EncapsulateRequest(BaseModel):
    """Request model for key encapsulation."""
    public_key: str = Field(..., description="Public key in hex format")
    scheme: KEMScheme = Field(
        default=KEMScheme.KYBER,
        description="KEM scheme to use"
    )
    hash_algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.IMPROVED, 
        description="Hash algorithm to use"
    )
    security_level: int = Field(
        default=1,
        description="Security level (1, 3, or 5 for Kyber-512, Kyber-768, Kyber-1024)",
        ge=1,
        le=5
    )


class EncapsulateResponse(BaseModel):
    """Response model for key encapsulation."""
    ciphertext: str = Field(..., description="Ciphertext in hex format")
    shared_secret: str = Field(..., description="Shared secret in hex format")
    scheme: str = Field(..., description="KEM scheme used")
    ciphertext_size_bytes: int = Field(..., description="Size of ciphertext in bytes")
    time_ms: float = Field(..., description="Time taken to encapsulate in milliseconds")


class DecapsulateRequest(BaseModel):
    """Request model for key decapsulation."""
    ciphertext: str = Field(..., description="Ciphertext in hex format")
    private_key: str = Field(..., description="Private key in hex format")
    scheme: KEMScheme = Field(
        default=KEMScheme.KYBER,
        description="KEM scheme to use"
    )
    hash_algorithm: HashAlgorithm = Field(
        default=HashAlgorithm.IMPROVED, 
        description="Hash algorithm to use"
    )
    security_level: int = Field(
        default=1,
        description="Security level (1, 3, or 5 for Kyber-512, Kyber-768, Kyber-1024)",
        ge=1,
        le=5
    )


class DecapsulateResponse(BaseModel):
    """Response model for key decapsulation."""
    shared_secret: str = Field(..., description="Shared secret in hex format")
    scheme: str = Field(..., description="KEM scheme used")
    time_ms: float = Field(..., description="Time taken to decapsulate in milliseconds") 