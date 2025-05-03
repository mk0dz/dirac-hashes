"""
Dirac Hashes API

This module provides a FastAPI-based API for the Dirac Hashes library,
offering endpoints for hash generation, digital signatures, and key management.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add the project root to path to make imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(web_dir)
sys.path.insert(0, project_root)

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
from web.api.routes import hash_routes, signature_routes, kem_routes

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
    uvicorn.run("web.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug") 