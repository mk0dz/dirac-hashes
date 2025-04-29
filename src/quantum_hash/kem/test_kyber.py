"""
Unit tests for the Kyber Key Encapsulation Mechanism implementation.
"""

import unittest
import numpy as np

from quantum_hash.kem.kyber import Kyber


class TestKyberKEM(unittest.TestCase):
    """Test cases for the Kyber KEM implementation."""

    def setUp(self):
        """Set up test cases."""
        # Create instances with different security levels
        self.kyber512 = Kyber(security_level=1)
        self.kyber768 = Kyber(security_level=3)
        self.kyber1024 = Kyber(security_level=5)

    def test_polynomial_operations(self):
        """Test polynomial operations."""
        kyber = self.kyber768
        
        # Test polynomial addition
        a = np.array([1, 2, 3] + [0] * (kyber.n - 3), dtype=np.int16)
        b = np.array([4, 5, 6] + [0] * (kyber.n - 3), dtype=np.int16)
        c = kyber.poly_add(a, b)
        expected = np.array([5, 7, 9] + [0] * (kyber.n - 3), dtype=np.int16)
        np.testing.assert_array_equal(c[:3], expected[:3])
        
        # Test polynomial subtraction
        d = kyber.poly_sub(a, b)
        expected = np.array([kyber.q - 3, kyber.q - 3, kyber.q - 3] + [0] * (kyber.n - 3), dtype=np.int16)
        np.testing.assert_array_equal(d[:3], expected[:3])
        
        # Test polynomial multiplication (simplified test)
        a = np.array([1, 0, 0, 0] + [0] * (kyber.n - 4), dtype=np.int16)
        b = np.array([0, 1, 0, 0] + [0] * (kyber.n - 4), dtype=np.int16)
        c = kyber.poly_mul(a, b)
        expected = np.array([0, 1, 0, 0] + [0] * (kyber.n - 4), dtype=np.int16)
        np.testing.assert_array_equal(c[:4], expected[:4])

    def test_serialization(self):
        """Test polynomial serialization and deserialization."""
        kyber = self.kyber768
        
        # Create a test polynomial
        poly = np.array([1, 2, 3, 4, 5] + [0] * (kyber.n - 5), dtype=np.int16)
        
        # Test conversion to bytes and back
        poly_bytes = kyber.poly_to_bytes(poly)
        poly_restored = kyber.bytes_to_poly(poly_bytes)
        
        np.testing.assert_array_equal(poly, poly_restored)

    def test_key_generation(self):
        """Test key generation."""
        kyber = self.kyber768
        
        # Generate a key pair
        private_key, public_key = kyber.generate_keypair()
        
        # Check that keys have the expected structure
        self.assertIn('seed', private_key)
        self.assertIn('s', private_key)
        self.assertIn('public_key', private_key)
        
        self.assertIn('seed', public_key)
        self.assertIn('t', public_key)
        
        # Check dimensions
        self.assertEqual(len(private_key['s']), kyber.k)
        self.assertEqual(len(public_key['t']), kyber.k)
        
        for s_poly in private_key['s']:
            self.assertEqual(len(s_poly), kyber.n)
        
        for t_poly in public_key['t']:
            self.assertEqual(len(t_poly), kyber.n)

    def test_encapsulation(self):
        """Test key encapsulation and decapsulation."""
        kyber = self.kyber768
        
        # Generate a key pair
        private_key, public_key = kyber.generate_keypair()
        
        # Encapsulate a shared secret
        ciphertext, shared_secret_sender = kyber.encapsulate(public_key)
        
        # Decapsulate the shared secret
        shared_secret_receiver = kyber.decapsulate(ciphertext, private_key)
        
        # Check that both parties have the same shared secret
        self.assertEqual(shared_secret_sender, shared_secret_receiver)
    
    def test_all_security_levels(self):
        """Test all security levels."""
        for kyber in [self.kyber512, self.kyber768, self.kyber1024]:
            # Generate a key pair
            private_key, public_key = kyber.generate_keypair()
            
            # Encapsulate a shared secret
            ciphertext, shared_secret_sender = kyber.encapsulate(public_key)
            
            # Decapsulate the shared secret
            shared_secret_receiver = kyber.decapsulate(ciphertext, private_key)
            
            # Check that both parties have the same shared secret
            self.assertEqual(shared_secret_sender, shared_secret_receiver)
            
            # Check key sizes based on security level
            self.assertEqual(len(private_key['s']), kyber.k)
            self.assertEqual(len(public_key['t']), kyber.k)
            
            # Check shared secret size
            self.assertEqual(len(shared_secret_sender), kyber.shared_key_size)
    
    def test_blockchain_compatibility(self):
        """Test blockchain compatibility functions."""
        kyber = self.kyber768
        
        # Generate a key pair
        _, public_key = kyber.generate_keypair()
        
        # Get blockchain-compatible representation
        blockchain_key = kyber.get_blockchain_compatible_keys(public_key)
        
        # Ensure it's a byte string
        self.assertIsInstance(blockchain_key, bytes)


if __name__ == '__main__':
    unittest.main() 