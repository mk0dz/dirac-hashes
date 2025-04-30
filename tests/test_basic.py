#!/usr/bin/env python3
"""
Basic tests for the core package functionality.
These tests have no external dependencies and should run reliably in CI environments.
"""

import unittest

from quantum_hash.dirac import DiracHash
from quantum_hash.signatures.dilithium import DilithiumSignature


class TestCorePackage(unittest.TestCase):
    """Test the core package functionality."""

    def test_dirac_hash(self):
        """Test basic hash functionality."""
        test_data = b"This is a test message"
        
        # Test default algorithm
        hash_value = DiracHash.hash(test_data)
        self.assertEqual(len(hash_value), 32)
        
        # Test deterministic output
        hash_value2 = DiracHash.hash(test_data)
        self.assertEqual(hash_value, hash_value2)
        
        # Test different input produces different output
        hash_value3 = DiracHash.hash(b"Different message")
        self.assertNotEqual(hash_value, hash_value3)
    
    def test_hmac(self):
        """Test HMAC functionality."""
        key = b"test-key"
        data = b"test-data"
        
        hmac_value = DiracHash.hmac(key, data)
        self.assertEqual(len(hmac_value), 32)
        
        # Test deterministic output
        hmac_value2 = DiracHash.hmac(key, data)
        self.assertEqual(hmac_value, hmac_value2)
        
        # Test different key produces different output
        hmac_value3 = DiracHash.hmac(b"different-key", data)
        self.assertNotEqual(hmac_value, hmac_value3)
    
    def test_dilithium_basic(self):
        """Test basic Dilithium functionality."""
        # Use fast_mode and security_level=1 for faster tests
        dilithium = DilithiumSignature(security_level=1, fast_mode=True)
        
        # Generate keypair
        private_key, public_key = dilithium.generate_keypair()
        
        # Check key structure
        self.assertIn('rho', private_key)
        self.assertIn('sigma', private_key)
        self.assertIn('s', private_key)
        self.assertIn('rho', public_key)
        self.assertIn('t', public_key)
        
        # Sign a message
        message = b"Test message"
        signature = dilithium.sign(message, private_key)
        
        # Verify valid signature
        is_valid = dilithium.verify(message, signature, public_key)
        self.assertTrue(is_valid)
        
        # Verify invalid signature (modified message)
        is_invalid = dilithium.verify(b"Modified message", signature, public_key)
        self.assertFalse(is_invalid)


if __name__ == '__main__':
    unittest.main() 