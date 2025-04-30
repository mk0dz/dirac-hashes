from quantum_hash.dirac import DiracHash
from quantum_hash.signatures.dilithium import DilithiumSignature

# Test basic hash functionality
print("Testing DiracHash...")
hash_obj = DiracHash()
result = hash_obj.hash("Test message")
print(f"Hash result: {result.hex()}")

# Test signature functionality
print("\nTesting Dilithium signature...")
dilithium = DilithiumSignature()
private_key, public_key = dilithium.generate_keypair()
message = b"Hello, quantum-resistant world!"
signature = dilithium.sign(message, private_key)
is_valid = dilithium.verify(message, signature, public_key)
print(f"Signature valid: {is_valid}")
print(f"Signature size: {len(signature)} bytes") 