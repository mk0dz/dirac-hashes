"""
Dirac Hashes API

This module provides a FastAPI-based API for the Dirac Hashes library,
offering endpoints for hash generation, digital signatures, and key management.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create the FastAPI application
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

# Import routes
from api.routes import hash_routes, signature_routes, kem_routes

# Include routers
app.include_router(hash_routes.router, prefix="/api/hash", tags=["Hash Functions"])
app.include_router(signature_routes.router, prefix="/api/signatures", tags=["Digital Signatures"])
app.include_router(kem_routes.router, prefix="/api/kem", tags=["Key Encapsulation"])

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Dirac Hashes API",
        "version": "1.0.0",
        "description": "API for quantum-inspired cryptographic primitives",
        "endpoints": {
            "hash": "/api/hash - Quantum-inspired hash functions",
            "signatures": "/api/signatures - Post-quantum digital signatures",
            "kem": "/api/kem - Key encapsulation mechanisms",
        },
        "documentation": "/docs - Interactive API documentation",
    }

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 