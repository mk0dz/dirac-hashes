#!/usr/bin/env python3
"""
Serve the Dirac Hashes frontend.

This script starts a simple HTTP server to serve the frontend files.
"""

import http.server
import socketserver
import os
import sys
import webbrowser
import socket
from urllib.parse import urlparse

# Configuration
PORT = 8082
DIRECTORY = "web/frontend"

# Check if port is available
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for serving from DIRECTORY."""
    
    def __init__(self, *args, **kwargs):
        # Make sure to use the directory relative to the current working directory
        directory_path = os.path.join(os.getcwd(), DIRECTORY)
        super().__init__(*args, directory=directory_path, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Run the server."""
    # Check if the API server is running
    try:
        import requests
        response = requests.get('http://localhost:8000/')
        if response.status_code != 200:
            print("Warning: API server doesn't seem to be responding correctly.")
            print("Make sure to start the API server with: python run_api.py")
    except:
        print("Warning: API server doesn't seem to be running.")
        print("Make sure to start the API server with: python run_api.py")
    
    # Check if port is in use
    if is_port_in_use(PORT):
        print(f"Error: Port {PORT} is already in use.")
        print(f"Try accessing the frontend at http://localhost:{PORT}")
        sys.exit(1)
    
    # Create server
    try:
        handler = Handler
        httpd = socketserver.TCPServer(("", PORT), handler)
        
        print(f"Serving frontend from '{DIRECTORY}' at http://localhost:{PORT}")
        
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}")
        
        # Start server
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
        sys.exit(0)
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print(f"Try accessing the frontend at http://localhost:{PORT}")
            sys.exit(1)
        else:
            raise

if __name__ == "__main__":
    # Make sure we're in the project root and the directory exists
    directory_path = os.path.join(os.getcwd(), DIRECTORY)
    if not os.path.isdir(directory_path):
        print(f"Error: '{DIRECTORY}' directory not found at '{directory_path}'.")
        print("Make sure you're running this script from the project root.")
        sys.exit(1)
        
    main() 