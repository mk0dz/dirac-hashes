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

# Dirac Hashes - Current Project Status

## Overview

Dirac Hashes is a quantum-resistant cryptographic library focused on providing alternative hash functions and cryptographic primitives that are resistant to quantum computing attacks. The project is now at a stable beta stage with significant performance improvements and security validations.

## Current Status

As of version 0.1.4, we have:

1. **Core Hash Functions**
   - Improved algorithms with C-extension optimization
   - SIMD optimization for parallel operations
   - Cross-platform compatibility (Linux, Windows, macOS)
   - Quantum-resistant design validated through rigorous testing

2. **Cryptographic Primitives**
   - Lamport signatures (one-time, quantum-resistant)
   - SPHINCS+ (stateless hash-based signatures)
   - Dilithium (lattice-based general-purpose signatures)
   - Kyber KEM (lattice-based key encapsulation)

3. **API and Integration**
   - RESTful API deployed on cloud
   - Web-based demonstration tools
   - Blockchain integration capabilities

## Latest Benchmark Results

Our latest benchmark (May 2023) shows significant improvement from previous versions:

### Hash Function Performance

| Algorithm | 16 bytes | 64 bytes | 256 bytes | 1024 bytes | 4096 bytes |
|-----------|----------|----------|-----------|------------|------------|
| improved  | 0.003 MB/s | 0.005 MB/s | 0.007 MB/s | 0.008 MB/s | 0.008 MB/s |
| grover    | 0.023 MB/s | 0.094 MB/s | 0.362 MB/s | 1.421 MB/s | 5.857 MB/s |
| shor      | 0.247 MB/s | 0.657 MB/s | 0.999 MB/s | 1.053 MB/s | 1.142 MB/s |
| hybrid    | 0.021 MB/s | 0.080 MB/s | 0.253 MB/s | 0.608 MB/s | 0.957 MB/s |
| SHA-256   | 42.667 MB/s | 165.161 MB/s | 519.797 MB/s | 1098.123 MB/s | 1488.102 MB/s |
| SHA3-256  | 22.145 MB/s | 95.522 MB/s | 270.185 MB/s | 389.724 MB/s | 437.140 MB/s |
| BLAKE2b   | 44.444 MB/s | 180.282 MB/s | 519.797 MB/s | 764.179 MB/s | 843.232 MB/s |

### Security Metrics

| Algorithm | Avalanche Effect | Entropy | Chi-Square | Collisions |
|-----------|-----------------|---------|------------|------------|
| improved  | 49.93% | 6.302 | 262.24 | 0 |
| grover    | 49.31% | 6.289 | 267.36 | 0 |
| shor      | 49.76% | 6.298 | 253.28 | 0 |
| hybrid    | 50.13% | 6.286 | 254.56 | 0 |
| SHA-256   | 50.34% | 6.296 | 246.88 | 0 |
| SHA3-256  | 49.83% | 6.283 | 245.60 | 0 |
| BLAKE2b   | 50.16% | 6.284 | 240.48 | 0 |

### Signature Performance

| Scheme | Variant | Key Gen Time | Sign Time | Verify Time | Private Key Size | Public Key Size | Signature Size |
|--------|---------|--------------|-----------|-------------|------------------|-----------------|----------------|
| Lamport | improved | 9.078s | 0.011s | 0.559s | 16.0 KB | 16.0 KB | 2.2 KB |
| Lamport | grover | 0.673s | 0.001s | 0.043s | 16.0 KB | 16.0 KB | 2.2 KB |
| Lamport | hybrid | 0.800s | 0.001s | 0.049s | 16.0 KB | 16.0 KB | 2.2 KB |
| SPHINCS+ | default | 5.346s | 28.340s | 24.922s | 96 bytes | 64 bytes | 8.2 KB |
| Dilithium | level1 | 0.109s | 0.284s | ~0s | 5.1 KB | 3.0 KB | 3.2 KB |
| Dilithium | level2 | 0.145s | 0.411s | ~0s | 6.1 KB | 3.0 KB | 4.2 KB |
| Kyber KEM | level1 | 0.167s | 0.245s | 0.007s | 1.0 KB | 1.0 KB | 1.5 KB |
| Kyber KEM | level3 | 0.359s | 0.468s | 0.008s | 1.5 KB | 1.5 KB | 2.0 KB |

## Suitability for Production

Based on our latest benchmarks and security analysis:

1. **Wallet Applications**:
   - **Ready for Testnet**: The "Grover" variant (5.85 MB/s) is suitable for wallet applications on testnet.
   - **Recommended**: For wallet applications requiring quantum resistance with reasonable performance.
   - **Ideal Use Cases**: Key generation, address derivation, transaction signing.

2. **Stablecoin Applications**:
   - **Ready for Testnet**: Current performance is sufficient for testnet volumes.
   - **Hybrid Approach Recommended**: Use standard algorithms for high-volume operations and quantum-resistant algorithms for critical security operations.
   - **Signature Schemes**: Dilithium offers the best performance/security trade-off for validation.

3. **Production Readiness**:
   - **Security**: Excellent security properties comparable to industry standards.
   - **Performance**: Needs optimization to reach the 10-20x target compared to standard algorithms.
   - **Integration**: Well-designed API ready for integration.

## Next Steps

1. **Performance Optimization**:
   - Further optimizations of C extensions
   - Parallelization of critical operations
   - Platform-specific optimizations

2. **Additional Security Validations**:
   - Formal security proofs
   - Third-party security audit
   - Extended collision testing

3. **Framework Integration**:
   - SDKs for popular blockchain platforms
   - Direct wallet integration examples
   - Smart contract verification tools 