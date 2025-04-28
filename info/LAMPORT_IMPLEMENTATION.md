# Lamport Signature Implementation

## Overview

The Lamport signature scheme is a post-quantum digital signature algorithm that provides security against attacks by quantum computers. It uses a one-time signature approach where each private/public key pair should only be used once to maintain security.

## Implementation Details

Our implementation of the Lamport signature scheme includes:

1. **Key Generation**: Creates 512 random values (256 bit positions × 2 possible bit values) for the private key, and their corresponding hash values for the public key.

2. **Signing**: Hashes the message and selects one of the two private key values for each bit position based on the corresponding bit in the message digest.

3. **Verification**: Hashes the message, then hashes each component of the signature and compares to the corresponding public key value.

## Integration with Quantum-Inspired Hash Functions

The implementation supports multiple hash algorithms:

- `improved` (default): Our best quantum-inspired hybrid hash
- `grover`: Grover-inspired hash algorithm
- `shor`: Shor-inspired hash algorithm
- `hybrid`: Combination of Grover and Shor algorithms
- `improved_grover`: Enhanced Grover-inspired hash
- `improved_shor`: Enhanced Shor-inspired hash

## Recent Fixes

Several issues were identified and fixed in the Lamport signature implementation:

1. **Hash Algorithm Consistency**: Ensured that the same hash algorithm is used consistently between key generation, signing, and verification.

2. **Hash Function Determinism**: Fixed the `grover_hash` function to be deterministic, as its use of random sampling during the quantum simulation phase was causing verification failures. This was addressed by:
   - Using a seed derived from the input data for the random number generator
   - Choosing deterministic measurement outcomes when a seed is provided
   - Adding additional mixing and diffusion steps to improve avalanche effect

3. **Improved Avalanche Effect**: Enhanced the `grover_hash` function to ensure better diffusion and avalanche properties, resulting in a higher probability that changes in the input result in changes to at least half the bits in the output.

4. **Type Handling**: Fixed issues related to handling of numpy integer types to ensure compatibility with Python's built-in functions.

## Performance Characteristics

The Lamport signature scheme has the following performance characteristics:

| Algorithm | Key Generation | Signing | Verification |
|-----------|---------------|---------|-------------|
| improved | ~0.56s | ~0.001s | ~0.27s |
| grover | ~0.32s | ~0.001s | ~0.16s |
| shor | ~0.01s | ~0.0001s | ~0.006s |
| hybrid | ~0.33s | ~0.001s | ~0.17s |
| improved_grover | ~0.62s | ~0.001s | ~0.30s |
| improved_shor | ~0.31s | ~0.001s | ~0.16s |

## Security Properties

1. **Quantum Resistance**: The security of the scheme relies on the one-way property of hash functions, which is believed to be resistant to quantum attacks.

2. **One-Time Usage**: Each key pair should only be used once to prevent attackers from learning parts of the private key.

3. **Large Keys**: The scheme requires large key and signature sizes (~16KB for keys, ~8KB for signatures with 256-bit security).

4. **No Trapdoor**: Unlike RSA or ECC, Lamport signatures do not rely on mathematical trapdoor functions that could be vulnerable to quantum algorithms.

## Limitations and Future Improvements

1. **Key Size**: The large key and signature sizes can be a limitation in constrained environments.

2. **One-Time Use**: Managing key usage to ensure each key is used only once adds complexity.

3. **Stateful**: Requires tracking which keys have been used, making it more complex than stateless signature schemes.

4. **Future Improvements**: Considering implementations of stateless hash-based signature schemes like SPHINCS+ that build on Lamport signatures but don't require tracking key usage.

## Demo Usage

A demonstration script `demo_lamport.py` showcases the Lamport signature scheme with different hash algorithms, providing performance metrics and security analysis. 