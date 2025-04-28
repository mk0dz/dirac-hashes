"""
Basic tests for quantum hash functionality.
"""

import unittest
import binascii
from src.quantum_hash.dirac import DiracHash

class TestDiracHash(unittest.TestCase):
    """Test cases for DiracHash."""
    
    def test_hash_grover(self):
        """Test Grover-inspired hash function."""
        data = b"Hello, quantum world!"
        digest = DiracHash.hash(data, algorithm='grover')
        self.assertEqual(len(digest), 32)  # Default digest size
        
        # Test with string input
        digest2 = DiracHash.hash("Hello, quantum world!", algorithm='grover')
        self.assertEqual(digest, digest2)
        
        # Hash should be deterministic
        digest3 = DiracHash.hash(data, algorithm='grover')
        self.assertEqual(digest, digest3)
    
    def test_hash_shor(self):
        """Test Shor-inspired hash function."""
        data = b"Hello, quantum world!"
        digest = DiracHash.hash(data, algorithm='shor')
        self.assertEqual(len(digest), 32)  # Default digest size
        
        # Hash should be deterministic
        digest2 = DiracHash.hash(data, algorithm='shor')
        self.assertEqual(digest, digest2)
    
    def test_hash_hybrid(self):
        """Test hybrid hash function."""
        data = b"Hello, quantum world!"
        digest = DiracHash.hash(data, algorithm='hybrid')
        self.assertEqual(len(digest), 32)  # Default digest size
        
        # Hybrid hash should differ from individual hashes
        digest_grover = DiracHash.hash(data, algorithm='grover')
        digest_shor = DiracHash.hash(data, algorithm='shor')
        self.assertNotEqual(digest, digest_grover)
        self.assertNotEqual(digest, digest_shor)
    
    def test_hmac(self):
        """Test HMAC functionality."""
        key = b"quantum-key"
        data = b"Hello, quantum world!"
        
        hmac = DiracHash.hmac(key, data)
        self.assertEqual(len(hmac), 32)
        
        # HMAC should be deterministic
        hmac2 = DiracHash.hmac(key, data)
        self.assertEqual(hmac, hmac2)
        
        # Different key should produce different HMAC
        hmac3 = DiracHash.hmac(b"different-key", data)
        self.assertNotEqual(hmac, hmac3)
    
    def test_key_generation(self):
        """Test key generation functionality."""
        # Generate seed
        seed = DiracHash.generate_seed()
        self.assertEqual(len(seed), 32)
        
        # Generate keypair
        private_key, public_key = DiracHash.generate_keypair()
        self.assertEqual(len(private_key), 32)
        self.assertEqual(len(public_key), 32)
        self.assertNotEqual(private_key, public_key)
        
        # Test key formatting
        hex_key = DiracHash.format_key(private_key)
        self.assertEqual(len(hex_key), 64)  # 32 bytes = 64 hex chars
        
        base64_key = DiracHash.format_key(private_key, format_type='base64')
        self.assertTrue(isinstance(base64_key, str))
        
        # Test key parsing
        parsed_key = DiracHash.parse_key(hex_key)
        self.assertEqual(parsed_key, private_key)
    
    def test_derive_key(self):
        """Test key derivation functionality."""
        master_key = DiracHash.generate_seed()
        
        # Derive subkeys
        subkey1 = DiracHash.derive_key(master_key, "purpose1")
        subkey2 = DiracHash.derive_key(master_key, "purpose2")
        
        self.assertEqual(len(subkey1), 32)
        self.assertEqual(len(subkey2), 32)
        self.assertNotEqual(subkey1, subkey2)
        
        # Derivation should be deterministic
        subkey1_again = DiracHash.derive_key(master_key, "purpose1")
        self.assertEqual(subkey1, subkey1_again)
    
    def test_avalanche_effect(self):
        """Test that small input changes cause large output changes."""
        data1 = b"Hello, quantum world!"
        data2 = b"Hello, quantum world."  # One character difference
        
        hash1 = DiracHash.hash(data1, algorithm='hybrid')
        hash2 = DiracHash.hash(data2, algorithm='hybrid')
        
        # Count bit differences
        xor_result = bytes(a ^ b for a, b in zip(hash1, hash2))
        diff_bits = bin(int.from_bytes(xor_result, byteorder='big')).count('1')
        
        # With good avalanche effect, around 50% of bits should differ
        # We'll accept 30% as a minimum for this test
        min_expected_diff = len(hash1) * 8 * 0.3
        self.assertGreater(diff_bits, min_expected_diff)
        
        print(f"Avalanche effect: {diff_bits/(len(hash1)*8)*100:.2f}% of bits differ")


if __name__ == "__main__":
    unittest.main() 