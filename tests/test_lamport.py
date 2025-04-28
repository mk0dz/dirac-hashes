"""
Tests for the Lamport signature scheme implementation.
"""

import unittest
from src.quantum_hash.signatures.lamport import LamportSignature


class TestLamportSignature(unittest.TestCase):
    """Test cases for the Lamport signature scheme."""
    
    def setUp(self):
        """Set up the test environment."""
        self.lamport = LamportSignature()
        self.test_message = "This is a test message"
        self.private_key, self.public_key = self.lamport.generate_keypair()
    
    def test_generate_keypair(self):
        """Test key pair generation."""
        private_key, public_key = self.lamport.generate_keypair()
        
        # Verify the structure of the keys
        self.assertEqual(len(private_key), 256)  # 32 bytes * 8 bits = 256 bits
        self.assertEqual(len(public_key), 256)
        
        # Check a few sample key entries
        for i in range(0, 256, 32):  # Check every 32nd position
            self.assertIn(0, private_key[i])
            self.assertIn(1, private_key[i])
            self.assertIn(0, public_key[i])
            self.assertIn(1, public_key[i])
            
            # Verify the lengths of the key components
            self.assertEqual(len(private_key[i][0]), 32)
            self.assertEqual(len(private_key[i][1]), 32)
            self.assertEqual(len(public_key[i][0]), 32)
            self.assertEqual(len(public_key[i][1]), 32)
    
    def test_sign_and_verify(self):
        """Test signature generation and verification."""
        # Sign the message
        signature = self.lamport.sign(self.test_message, self.private_key)
        
        # Verify the signature
        self.assertTrue(self.lamport.verify(self.test_message, signature, self.public_key))
        
        # Modify the message and ensure verification fails
        modified_message = self.test_message + " modified"
        self.assertFalse(self.lamport.verify(modified_message, signature, self.public_key))
    
    def test_sign_bytes(self):
        """Test signing binary data."""
        binary_data = b"\x00\x01\x02\x03\x04\x05"
        signature = self.lamport.sign(binary_data, self.private_key)
        
        # Verify the signature
        self.assertTrue(self.lamport.verify(binary_data, signature, self.public_key))
        
        # Modify the data and ensure verification fails
        modified_data = b"\x00\x01\x02\x03\x04\x06"  # Changed last byte
        self.assertFalse(self.lamport.verify(modified_data, signature, self.public_key))
    
    def test_signature_tampering(self):
        """Test that tampering with the signature causes verification failure."""
        signature = self.lamport.sign(self.test_message, self.private_key)
        
        # Tamper with the signature by modifying one component
        tampered_signature = signature.copy()
        tampered_signature[0] = b"\x00" * 32  # Replace first component with zeros
        
        # Verify the tampered signature should fail
        self.assertFalse(self.lamport.verify(self.test_message, tampered_signature, self.public_key))
    
    def test_different_hash_algorithms(self):
        """Test signing and verification with different hash algorithms."""
        algorithms = ['improved', 'grover', 'shor', 'hybrid', 'improved_grover', 'improved_shor']
        
        for algorithm in algorithms:
            with self.subTest(algorithm=algorithm):
                lamport = LamportSignature(hash_algorithm=algorithm)
                private_key, public_key = lamport.generate_keypair()
                signature = lamport.sign(self.test_message, private_key)
                self.assertTrue(lamport.verify(self.test_message, signature, public_key))


if __name__ == "__main__":
    unittest.main() 