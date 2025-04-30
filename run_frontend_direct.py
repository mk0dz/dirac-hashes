#!/usr/bin/env python3
"""
Direct frontend server for the Dirac Hashes project.

This script starts a simple HTTP server to serve the frontend files.
"""

import os
import sys
import http.server
import socketserver
import socket
from pathlib import Path

# Default port
DEFAULT_PORT = 8080

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=DEFAULT_PORT, max_attempts=10):
    """Find an available port starting from start_port."""
    port = start_port
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

def main():
    # Determine the frontend directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, "web", "frontend")
    
    # Verify the frontend directory exists
    if not os.path.isdir(frontend_dir):
        print(f"Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)
    
    # Find an available port
    port = find_available_port()
    
    # Change to the frontend directory
    os.chdir(frontend_dir)
    
    # Set up the HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    
    # Create and start the server
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Frontend server started at http://localhost:{port}")
        print(f"Serving files from: {frontend_dir}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped by user")
            httpd.server_close()

if __name__ == "__main__":
    main() 