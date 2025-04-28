# Dirac Hashes API

This API provides access to the quantum-inspired cryptographic primitives implemented in the Dirac Hashes library.

## Features

- **Quantum-inspired hash functions**: Various hash algorithms with different resistance levels against quantum attacks
- **Post-quantum signature schemes**: Lamport, SPHINCS+, and Dilithium signature schemes
- **Key encapsulation mechanisms**: Kyber KEM for secure key exchange

## API Endpoints

### Hash Functions

- `POST /api/hash/generate`: Generate a hash digest using the specified algorithm
- `POST /api/hash/compare`: Compare multiple hash algorithms on the same input
- `GET /api/hash/algorithms`: List all available hash algorithms

### Digital Signatures

- `POST /api/signatures/keypair`: Generate a key pair for the specified signature scheme
- `POST /api/signatures/sign`: Sign a message using the specified signature scheme
- `POST /api/signatures/verify`: Verify a signature using the specified signature scheme
- `GET /api/signatures/schemes`: List all available signature schemes

### Key Encapsulation

- `POST /api/kem/keypair`: Generate a key pair for the specified KEM scheme
- `POST /api/kem/encapsulate`: Encapsulate a shared secret using the specified KEM scheme
- `POST /api/kem/decapsulate`: Decapsulate a shared secret using the specified KEM scheme
- `GET /api/kem/schemes`: List all available KEM schemes

## Interactive Documentation

When the API is running, you can access the interactive documentation at:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python run_api.py
```

The API will be available at http://localhost:8000

## Example Requests

### Generate a Hash

```bash
curl -X POST "http://localhost:8000/api/hash/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, quantum world!",
    "algorithm": "improved",
    "encoding": "utf-8"
  }'
```

### Generate a Key Pair

```bash
curl -X POST "http://localhost:8000/api/signatures/keypair" \
  -H "Content-Type: application/json" \
  -d '{
    "scheme": "dilithium",
    "hash_algorithm": "improved",
    "security_level": 2
  }'
```

### Sign a Message

```bash
curl -X POST "http://localhost:8000/api/signatures/sign" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Message to sign",
    "private_key": "YOUR_PRIVATE_KEY",
    "scheme": "dilithium",
    "hash_algorithm": "improved",
    "encoding": "utf-8"
  }'
```

## Integration with Frontend

This API is designed to be used with the Dirac Hashes Frontend Portal, which provides a user-friendly interface for interacting with these cryptographic primitives. 