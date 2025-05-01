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

## API Usage Guide

Our API is live at `https://dirac-hashes.onrender.com`. Here are practical examples for using each feature:

### Hash Functions

#### Compare Multiple Hash Algorithms

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/hash/compare' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"message":"I am groot","algorithms":["improved","grover","shor"],"encoding":"utf-8"}' | python -m json.tool
```

Response:
```json
{
  "message": "I am groot",
  "results": {
    "improved": "a62a8045cd4cde9d7e38e9ce9ee95a58d97a31fc12c735959a6cd3aadfb07cde",
    "grover": "b73e4f7c84b12e7d1e38a9ca7ee15a46d87f41fc31c724958a5cd2badfb18cde",
    "shor": "c94f5e8d73c21f8e2f39b8db8ff25b35e98f52ed42d813847b6de1cadec29def"
  }
}
```

#### Generate a Single Hash

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/hash/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Quantum supremacy","algorithm":"improved","encoding":"utf-8"}' | python -m json.tool
```

### Digital Signatures

#### Generate a Signature Keypair

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/signatures/keypair' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"scheme":"dilithium","hash_algorithm":"improved","security_level":1}' | python -m json.tool
```

Save the returned `public_key` and `private_key` for the next steps.

#### Sign a Message

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/signatures/sign' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Sign this secure message",
    "private_key": "YOUR_PRIVATE_KEY_FROM_PREVIOUS_STEP",
    "scheme": "dilithium",
    "hash_algorithm": "improved"
  }' | python -m json.tool
```

Save the returned `signature` for verification.

#### Verify a Signature

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/signatures/verify' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Sign this secure message",
    "signature": "YOUR_SIGNATURE_FROM_PREVIOUS_STEP",
    "public_key": "YOUR_PUBLIC_KEY_FROM_KEYPAIR_STEP",
    "scheme": "dilithium",
    "hash_algorithm": "improved"
  }' | python -m json.tool
```

### Key Encapsulation Mechanism (KEM)

#### Generate a KEM Keypair

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/kem/keypair' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"scheme":"kyber","hash_algorithm":"improved","security_level":1}' | python -m json.tool
```

Save the returned `public_key` and `private_key` for the next steps.

#### Encapsulate a Shared Secret

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/kem/encapsulate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "public_key": "YOUR_PUBLIC_KEY_FROM_PREVIOUS_STEP",
    "scheme": "kyber",
    "hash_algorithm": "improved"
  }' | python -m json.tool
```

Save the returned `ciphertext` and `shared_secret` for the next step.

#### Decapsulate to Retrieve the Shared Secret

```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/kem/decapsulate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "private_key": "YOUR_PRIVATE_KEY_FROM_KEYPAIR_STEP",
    "ciphertext": "YOUR_CIPHERTEXT_FROM_PREVIOUS_STEP",
    "scheme": "kyber",
    "hash_algorithm": "improved"
  }' | python -m json.tool
```

### Real-World Example: End-to-End Secure Communication

This example demonstrates a complete workflow for secure communication:

1. **Generate KEM keypair for recipient:**
```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/kem/keypair' \
  -H 'Content-Type: application/json' \
  -d '{"scheme":"kyber","hash_algorithm":"improved","security_level":1}' > recipient_keys.json
```

2. **Sender encapsulates a shared secret using recipient's public key:**
```bash
recipient_public_key=$(cat recipient_keys.json | jq -r '.public_key')
curl -X POST 'https://dirac-hashes.onrender.com/api/kem/encapsulate' \
  -H 'Content-Type: application/json' \
  -d "{\"public_key\":\"$recipient_public_key\",\"scheme\":\"kyber\",\"hash_algorithm\":\"improved\"}" > encapsulation.json
```

3. **Sender signs the encrypted message with their own signature key:**
```bash
curl -X POST 'https://dirac-hashes.onrender.com/api/signatures/keypair' \
  -H 'Content-Type: application/json' \
  -d '{"scheme":"dilithium","hash_algorithm":"improved","security_level":1}' > sender_sig_keys.json

sender_private_key=$(cat sender_sig_keys.json | jq -r '.private_key')
shared_secret=$(cat encapsulation.json | jq -r '.shared_secret')
ciphertext=$(cat encapsulation.json | jq -r '.ciphertext')

# Create a message containing the encrypted data (in real system, you'd encrypt with the shared secret)
message="Encrypted data: $ciphertext"

curl -X POST 'https://dirac-hashes.onrender.com/api/signatures/sign' \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"$message\",\"private_key\":\"$sender_private_key\",\"scheme\":\"dilithium\",\"hash_algorithm\":\"improved\"}" > signed_message.json
```

4. **Recipient verifies sender's signature:**
```bash
sender_public_key=$(cat sender_sig_keys.json | jq -r '.public_key')
signature=$(cat signed_message.json | jq -r '.signature')

curl -X POST 'https://dirac-hashes.onrender.com/api/signatures/verify' \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"$message\",\"signature\":\"$signature\",\"public_key\":\"$sender_public_key\",\"scheme\":\"dilithium\",\"hash_algorithm\":\"improved\"}" > verification.json
```

5. **Recipient decapsulates the shared secret:**
```bash
recipient_private_key=$(cat recipient_keys.json | jq -r '.private_key')

curl -X POST 'https://dirac-hashes.onrender.com/api/kem/decapsulate' \
  -H 'Content-Type: application/json' \
  -d "{\"private_key\":\"$recipient_private_key\",\"ciphertext\":\"$ciphertext\",\"scheme\":\"kyber\",\"hash_algorithm\":\"improved\"}" > decapsulation.json
```

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
