#!/usr/bin/env python3
"""
Run the Dirac Hashes API server.

This script starts the FastAPI server for the Dirac Hashes API.
"""

import uvicorn
import sys
import os

if __name__ == "__main__":
    print("Starting Dirac Hashes API server...")
    
    # Add the project root to the Python path if needed
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the server
    uvicorn.run(
        "api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 