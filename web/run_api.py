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
    
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up one level from web/
    sys.path.insert(0, project_root)
    
    # Add the web directory to the Python path
    web_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, web_dir)
    
    # Get the absolute path to the main.py file
    api_main_path = os.path.join(web_dir, "api", "main.py")
    print(f"Loading API from: {api_main_path}")
    
    # Run the server with absolute import path
    uvicorn.run(
        "web.api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 