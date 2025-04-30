#!/usr/bin/env python3
"""
Dirac Hashes installation script.

This script installs the Dirac Hashes package and its dependencies.
"""
import os
import subprocess
import sys

def main():
    """Install Dirac Hashes."""
    print("Installing Dirac Hashes...")
    
    # Check if pip is available
    try:
        import pip
    except ImportError:
        print("Error: pip is not installed. Please install pip first.")
        sys.exit(1)
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Install the package
    try:
        print("Installing from source...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", current_dir])
        print("\nDirac Hashes installed successfully!")
        
        # Test the installation
        print("\nTesting installation...")
        test_cmd = "from quantum_hash.dirac import DiracHash; print(f'Successfully installed DiracHash version {DiracHash.__version__}')"
        subprocess.check_call([sys.executable, "-c", test_cmd])
        
        print("\nYou can now use Dirac Hashes in your Python code:")
        print("\nfrom quantum_hash.dirac import DiracHash")
        print("hash_value = DiracHash.hash('Hello, quantum world!')")
        print("print(hash_value.hex())")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: Installation failed with error code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main() 