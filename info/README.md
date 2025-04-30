# Dirac Hashes - Quantum-Inspired Cryptography

Dirac Hashes is a Python library implementing quantum-inspired cryptographic hash functions for future-proof security.

## Overview

This project provides quantum-inspired hash functions based on principles from Grover's algorithm and Shor's algorithm. These hash functions offer an alternative approach to traditional cryptographic hash functions, drawing inspiration from quantum computing principles but implementable on classical computers.

The library includes:

- **Quantum-inspired hash algorithms**:
  - Grover-inspired hash (based on Grover's search algorithm principles)
  - Shor-inspired hash (based on Shor's period finding algorithm principles)
  - Hybrid hash (combining both approaches)
  - Improved implementations with enhanced security properties

- **Cryptographic utilities**:
  - HMAC implementation
  - Key generation and derivation
  - Performance optimizations

- **Post-Quantum Signatures**:
  - Lamport signature scheme (one-time signatures)
  - SPHINCS+ (stateless hash-based signatures)
  - Kyber (key encapsulation mechanism)
  - Dilithium (general-purpose signatures)

## Project Structure

- **src/**: Source code for the Dirac Hashes library
- **tests/**: Unit tests
- **info/**: Documentation and project information files
- **benchmark.py**: Comprehensive benchmarking tool with visualization capabilities
- **test_all.py**: Complete test suite for all components
- **demo.py**: Interactive demonstration of all features

## Recent Updates

- **Project Organization**: Reorganized project structure for clarity and maintainability
- **Consolidated Scripts**: Combined multiple testing, benchmarking, and demo scripts
- **Added Visualizations**: Enhanced benchmarking with graph generation capabilities for presentations
- **Improved Hash Functions**: Enhanced security properties for all hash algorithms
- **Lamport Signature Compatibility**: Fixed compatibility issues between Lamport signatures and all hash algorithms
- **Bugfixes**: See `info/BUGFIX_REPORT.md` for details on recent fixes

## Security Properties

Our improved hash functions demonstrate security properties comparable to industry-standard cryptographic hash functions:

- **Avalanche Effect**: ~50% bit change on average (ideal is 50%)
- **Uniform Distribution**: Low chi-square values
- **High Entropy**: Comparable to SHA-256
- **Collision Resistance**: No collisions detected in our tests
- **Length-Extension Attack Protection**: Built-in

## Installation

```bash
pip install dirac-hashes
```

Or install from source:

```bash
git clone https://github.com/yourusername/dirac-hashes.git
cd dirac-hashes
pip install -e .
```

## Usage

```python
from src.quantum_hash.dirac import DiracHash

# Generate a hash using the default (improved) algorithm
data = b"Hello, quantum world!"
digest = DiracHash.hash(data)
print(f"Hash: {DiracHash.format_key(digest)}")

# Generate a hash using a specific algorithm
digest = DiracHash.hash(data, algorithm='improved_grover')
print(f"Grover-inspired hash: {DiracHash.format_key(digest)}")

# Create an HMAC
key = DiracHash.generate_seed(16)
hmac_digest = DiracHash.hmac(key, data)
print(f"HMAC: {DiracHash.format_key(hmac_digest)}")

# Generate a keypair
private_key, public_key = DiracHash.generate_keypair()
print(f"Private key: {DiracHash.format_key(private_key)}")
print(f"Public key: {DiracHash.format_key(public_key)}")

# Derive a key for a specific purpose
derived_key = DiracHash.derive_key(private_key, "encryption")
print(f"Derived key: {DiracHash.format_key(derived_key)}")
```

### Using Lamport Signatures

```python
from src.quantum_hash.signatures.lamport import LamportSignature

# Create a Lamport signature instance with your preferred hash algorithm
lamport = LamportSignature(hash_algorithm='improved')  # Works with all algorithms now!

# Generate a keypair
private_key, public_key = lamport.generate_keypair()

# Sign a message
message = "Transfer 10 tokens to Alice"
signature = lamport.sign(message, private_key)

# Verify the signature
is_valid = lamport.verify(message, signature, public_key)
print(f"Signature valid: {is_valid}")
```

## Running Tests, Benchmarks, and Demos

The project provides three consolidated scripts for testing, benchmarking, and demonstrating features:

### Running Tests

```bash
python test_all.py
```

This will run comprehensive tests for all components of the library.

### Running Benchmarks

```bash
python benchmark.py
```

This will benchmark all hash functions and signature schemes and generate visualization graphs in the `benchmark_results/graphs` directory, ideal for presentations to VCs and funding providers.

### Interactive Demo

```bash
python demo.py
```

This will provide an interactive demonstration of all features. You can also run specific sections:

```bash
python demo.py --section hash     # Demonstrate hash functions
python demo.py --section keys     # Demonstrate key generation
python demo.py --section lamport  # Demonstrate Lamport signatures
python demo.py --section advanced # Demonstrate advanced signatures
```

## Benchmark Results

Our improved algorithms match industry-standard hash functions in security properties (avalanche effect, distribution, entropy) but are optimized for security rather than speed:

| Hash Function   | Avalanche Effect (%) | 256 bytes (MB/s) | 4096 bytes (MB/s) |
|-----------------|----------------------|------------------|-------------------|
| SHA-256         | 49.73                | 341.33           | 1365.33           |
| SHA3-256        | 49.75                | 256.00           | 431.16            |
| BLAKE2b         | 49.86                | 512.00           | 819.20            |
| Our Improved    | 49.35                | 0.04             | 0.04              |

For complete benchmark results, see `info/IMPROVEMENTS.md`.

## Roadmap

We are developing this library as part of a larger project to create a Quantum-Resistant Solana Wallet:

- **Phase 1 (Completed)**: Core cryptographic primitives (hash functions, HMAC, key derivation)
- **Phase 2 (In Progress)**: Post-quantum digital signatures (Lamport signatures)
- **Phase 3**: Solana blockchain integration
- **Phase 4**: User interface development
- **Phase 5**: Security enhancements
- **Phase 6**: Advanced features

For details on the next steps, see `info/NEXT_STEPS.md`.

## Enhancement Plan

We have a detailed plan for enhancing our hash functions before moving to Phase 2:

- Performance optimizations (SIMD, cache optimization)
- Enhanced quantum properties (superposition modeling, entanglement properties)
- Security enhancements (variable digest size, side-channel protection)
- Extended testing and validation
- Improved documentation

For details, see `info/ENHANCEMENT_PLAN.md`.

## License

MIT

## Citation

If you use this library in your research, please cite:

```
@software{dirac-hashes,
  author = {Your Name},
  title = {Dirac Hashes: Quantum-Inspired Cryptographic Hash Functions},
  year = {2025},
  url = {https://github.com/yourusername/dirac-hashes}
}
```
