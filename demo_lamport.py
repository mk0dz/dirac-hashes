"""
Demo of the Lamport signature scheme.

This script demonstrates how to use the Lamport signature scheme
for signing and verifying messages with different hash algorithms.
"""

import time
from src.quantum_hash.signatures.lamport import LamportSignature


def demonstrate_lamport_signatures():
    """
    Demonstrate the Lamport signature scheme with different hash algorithms.
    """
    print("\n===== QUANTUM-RESISTANT LAMPORT SIGNATURES =====")
    print("A one-time signature scheme that is secure against quantum computer attacks.")
    print("This demonstration will show signing and verification with different hash algorithms.\n")
    
    # Message to sign
    message = "Transfer 10 Dirac tokens to Alice"
    print(f"Message to sign: '{message}'\n")
    
    # Test with different algorithms
    algorithms = ['improved', 'grover', 'shor', 'hybrid', 'improved_grover', 'improved_shor']
    
    for algorithm in algorithms:
        print(f"Using algorithm: {algorithm}")
        
        # Initialize Lamport signature with this algorithm
        lamport = LamportSignature(hash_algorithm=algorithm)
        
        # Generate key pair
        start_time = time.time()
        private_key, public_key = lamport.generate_keypair()
        key_gen_time = time.time() - start_time
        
        # Analyze the key sizes
        private_key_size = sum(len(private_key[i][bit]) for i in range(256) for bit in [0, 1])
        public_key_size = sum(len(public_key[i][bit]) for i in range(256) for bit in [0, 1])
        
        print(f"  Key generation time: {key_gen_time:.4f} seconds")
        print(f"  Private key size: {private_key_size} bytes")
        print(f"  Public key size: {public_key_size} bytes")
        
        # Sign the message
        start_time = time.time()
        signature = lamport.sign(message, private_key)
        signing_time = time.time() - start_time
        
        # Calculate signature size
        signature_size = sum(len(sig) for sig in signature)
        
        print(f"  Signing time: {signing_time:.4f} seconds")
        print(f"  Signature size: {signature_size} bytes")
        
        # Verify the signature
        start_time = time.time()
        result = lamport.verify(message, signature, public_key)
        verification_time = time.time() - start_time
        
        print(f"  Verification time: {verification_time:.4f} seconds")
        print(f"  Verification result: {'Success' if result else 'Failed'}")
        
        # Try with an altered message
        altered_message = "Transfer 100 Dirac tokens to Alice"  # Changed 10 to 100
        result = lamport.verify(altered_message, signature, public_key)
        print(f"  Verification with altered message: {'Failed (Expected)' if not result else 'Success (Unexpected!)'}")
        
        print()


if __name__ == "__main__":
    demonstrate_lamport_signatures() 