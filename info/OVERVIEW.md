# Quantum-Inspired Post-Quantum Cryptography

This project implements a suite of quantum-inspired cryptographic primitives that are resistant to attacks by both classical and quantum computers. The goal is to provide practical cryptographic tools that can be used in blockchain applications, particularly for Solana, while maintaining security in a post-quantum world.

## Core Components

### Hash Functions

- **DiracHash**: A modular hashing framework that provides quantum-inspired hash algorithms
- **Improved Algorithms**: Enhanced versions with better avalanche effect, distribution, and collision resistance
- **HMAC Support**: Standard HMAC implementation for authentication using quantum-inspired hashes

### Post-Quantum Signature Schemes

- **Lamport Signatures**: One-time signatures with unconditional security
- **SPHINCS+**: Stateless hash-based signatures for general-purpose use
- **Dilithium**: Lattice-based signatures offering a balance of security and performance

### Key Encapsulation Mechanisms

- **Kyber**: Lattice-based key encapsulation for secure key exchange

## Optimizations

The project includes both standard and optimized implementations:

- **Fast Mode**: Reduced parameters and algorithmic optimizations for better performance
- **Security Parameters**: Configurable security levels (1-5) for different security/performance needs
- **Implementation Variants**: Different height/dimension parameters for hash-based and lattice-based schemes

## Performance Characteristics

| Algorithm Type | Key Size | Signature/Ciphertext Size | Security | Use Case |
|----------------|----------|---------------------------|----------|----------|
| Lamport        | ~16KB    | ~8KB                      | Very High| Critical operations |
| SPHINCS+       | ~64B     | ~8KB                      | High     | General signatures |
| Dilithium      | ~2.5KB   | ~2.5KB                    | High     | Frequent transactions |
| Kyber          | ~1.5KB   | ~1KB                      | High     | Key exchange |

## Demonstration & Benchmarking

- **demo.py**: Demonstrates the functionality of core hash algorithms
- **demo_post_quantum.py**: Showcases post-quantum signature and key exchange
- **benchmark_simple.py**: Compares hash function performance against SHA-256
- **benchmark_pqc.py**: Comprehensive benchmarking of post-quantum algorithms

## Blockchain Integration

The project is designed with Solana integration in mind:

- Serialization format compatible with Solana's account model
- Signature schemes that can replace Ed25519 in Solana transactions
- Key encapsulation for secure communication between wallets

## Project Status

This is a research and development project currently in Phase 1. See NEXT_STEPS.md for the detailed roadmap.

## Usage

```python
# Basic hash usage
from src.quantum_hash.dirac import DiracHash

hasher = DiracHash()
digest = hasher.hash(b"message", algorithm="improved")

# Post-quantum signatures
from src.quantum_hash.signatures.sphincs import SPHINCSSignature

# Fast version with reduced tree height
sphincs = SPHINCSSignature(hash_algorithm="improved", h=8, fast_mode=True)
private_key, public_key = sphincs.generate_keypair()
signature = sphincs.sign("message", private_key)
is_valid = sphincs.verify("message", signature, public_key)
```

## Requirements

- Python 3.7+
- NumPy
- Matplotlib (for benchmarking)
- Tabulate (for benchmarking)
- Cryptography (optional, for comparing with classical algorithms)

## Future Work

See NEXT_STEPS.md for upcoming features and phases of the project. 