# Dirac Hashes

[![Test](https://github.com/yourusername/dirac-hashes/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/dirac-hashes/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/dirac-hashes.svg)](https://badge.fury.io/py/dirac-hashes)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A next-generation cryptographic hash library built for speed, security, and quantum resistance.

## About

Dirac Hashes is a project aimed at developing and testing high-performance cryptographic hash functions that are resistant to quantum computing attacks. This repository contains a Python package implementing quantum-resistant hash functions, digital signature schemes, and key encapsulation mechanisms (KEM), plus tools for testing and comparing their performance.

## Features

- Quantum-resistant hash algorithms:
  - Improved (default, recommended)
  - Grover
  - Shor
  - Hybrid
  - Improved Grover
  - Improved Shor
- Post-quantum signature schemes:
  - Dilithium (NIST standard)
  - SPHINCS+
  - Lamport
- Key Encapsulation Mechanisms (KEM):
  - Kyber (NIST standard)
- Web-based testing interface with performance visualization
- Simple Python API for integration into other projects

## Installation

### Python Package

Install the package from PyPI:

```bash
pip install dirac-hashes
```

Or install from source:

```bash
git clone https://github.com/your-username/dirac-hashes.git
cd dirac-hashes
pip install -e .
```

### Development Setup

For development, install the dev dependencies:

```bash
pip install -r requirements-dev.txt
```

## Quick Start

```python
from quantum_hash.dirac import DiracHash
from quantum_hash.signatures.dilithium import DilithiumSignature

# Generate a hash
message = "Hello, quantum world!"
hash_value = DiracHash.hash(message)
print(f"Hash: {hash_value.hex()}")

# Generate a key pair
dilithium = DilithiumSignature()
private_key, public_key = dilithium.generate_keypair()

# Sign a message
signature = dilithium.sign(message.encode(), private_key)

# Verify the signature
is_valid = dilithium.verify(message.encode(), signature, public_key)
print(f"Signature valid: {is_valid}")
```

For more examples, see the [examples directory](examples/).

## Project Structure

```
dirac-hashes/
├── deployment/              # Docker and deployment files
├── docs/                    # Documentation files
├── examples/                # Example scripts
├── src/                     # Python package source
│   └── quantum_hash/        # Main package
│       ├── core/            # Core algorithms
│       ├── signatures/      # Signature schemes
│       ├── kem/             # Key encapsulation
│       └── utils/           # Utility functions
├── tests/                   # Test suite
├── tools/                   # Benchmark and demo tools
├── web/                     # Web interface and API
├── README.md                # This file
└── setup.py                 # Package setup
```

## Web Interface

To run the web interface locally:

1. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run the API server:
   ```bash
   python web/run_api.py
   ```

3. In another terminal, serve the frontend:
   ```bash
   python web/serve_frontend.py
   ```

4. Open `http://localhost:8000` in your browser

## Tools

### Benchmarking

Run performance benchmarks:

```bash
python tools/benchmark.py
```

### Demo

Run the interactive demo:

```bash
python tools/demo.py
```

## Docker Deployment

Docker files are provided in the `deployment` directory for containerized deployment:

```bash
docker build -t dirac-hashes -f deployment/Dockerfile .
docker run -p 8000:8000 -p 8080:8080 dirac-hashes
```

Or use Docker Compose:

```bash
docker-compose -f deployment/docker-compose.yml up
```

## Future Development

- Implementation of Dirac hash algorithms in Rust and WebAssembly
- Integration with Solana blockchain for high-performance verification
- Command-line tools for batch processing
- Integration tests for cryptographic properties

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 