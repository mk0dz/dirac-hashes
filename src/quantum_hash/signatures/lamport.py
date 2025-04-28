"""
Lamport Signature Scheme Implementation.

This module implements the Lamport one-time signature scheme, which is
considered secure against quantum computer attacks.
"""

import os
import secrets
import numpy as np
from typing import Dict, List, Tuple, Union

from src.quantum_hash.dirac import DiracHash


class LamportSignature:
    """
    Lamport one-time signature scheme implementation.
    
    This class provides methods for generating key pairs, signing messages,
    and verifying signatures using a quantum-resistant approach.
    """
    
    def __init__(self, hash_algorithm: str = 'improved'):
        """
        Initialize the Lamport signature scheme.
        
        Args:
            hash_algorithm: The hash algorithm to use ('improved', 'grover', 'shor', 'hybrid', 
                            'improved_grover', 'improved_shor')
        """
        self.hasher = DiracHash()
        self.hash_algorithm = hash_algorithm
        self.digest_size = 32  # 256 bits
    
    def generate_keypair(self) -> Tuple[Dict, Dict]:
        """
        Generate a Lamport key pair.
        
        Returns:
            A tuple containing (private_key, public_key)
        """
        private_key = {}
        public_key = {}
        
        # For each bit position of the message digest
        for i in range(self.digest_size * 8):
            # For each possible bit value (0 or 1)
            private_key[i] = {}
            public_key[i] = {}
            
            for bit in [0, 1]:
                # Generate a random value for the private key
                private_key[i][bit] = secrets.token_bytes(self.digest_size)
                # Compute the corresponding public key
                public_key[i][bit] = self.hasher.hash(
                    private_key[i][bit], 
                    algorithm=self.hash_algorithm
                )
        
        return private_key, public_key
    
    def sign(self, message: Union[str, bytes], private_key: Dict) -> List[bytes]:
        """
        Sign a message using the Lamport signature scheme.
        
        Args:
            message: The message to sign
            private_key: The private key to use for signing
            
        Returns:
            The signature as a list of bytes
        """
        # Convert string message to bytes if needed
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Hash the message using the same algorithm used for signing
        message_digest = self.hasher.hash(message, algorithm=self.hash_algorithm)
        
        # Create the signature
        signature = []
        
        # For each bit in the message digest
        for i in range(self.digest_size * 8):
            # Extract the bit at position i
            bit_position = i // 8
            bit_mask = 1 << (7 - (i % 8))
            bit_value = 1 if message_digest[bit_position] & bit_mask else 0
            
            # Add the corresponding private key value to the signature
            signature.append(private_key[i][bit_value])
        
        return signature
    
    def verify(self, message: Union[str, bytes], signature: List[bytes], public_key: Dict) -> bool:
        """
        Verify a Lamport signature.
        
        Args:
            message: The message that was signed
            signature: The signature to verify
            public_key: The public key to use for verification
            
        Returns:
            True if the signature is valid, False otherwise
        """
        # Convert string message to bytes if needed
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Hash the message using the same algorithm used for signing
        message_digest = self.hasher.hash(message, algorithm=self.hash_algorithm)
        
        # Verify the signature
        for i in range(self.digest_size * 8):
            # Extract the bit at position i from the message digest
            bit_position = i // 8
            bit_mask = 1 << (7 - (i % 8))
            bit_value = 1 if message_digest[bit_position] & bit_mask else 0
            
            # Hash the signature component using the same algorithm
            sig_hash = self.hasher.hash(signature[i], algorithm=self.hash_algorithm)
            
            # Convert both hashes to bytes for consistent comparison
            # This ensures compatibility with different hash implementations
            expected_hash = public_key[i][bit_value]
            
            # Compare with the public key component
            if sig_hash != expected_hash:
                return False
        
        return True 