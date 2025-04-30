"""
Basic tests for the quantum_hash package.
"""

import unittest

from quantum_hash.dirac import DiracHash


class TestDiracHash(unittest.TestCase):
    """Test case for DiracHash class."""
    
    def test_basic_hash(self):
        """Test basic hash functionality."""
        data = b"test data"
        hash_value = DiracHash.hash(data)
        
        # Check that hash is not empty
        self.assertTrue(hash_value)
        # Check that hash has correct length
        self.assertEqual(len(hash_value), 32)
        
    def test_string_input(self):
        """Test string input is handled correctly."""
        str_data = "test string"
        hash_value = DiracHash.hash(str_data)
        
        # Check that hash is not empty
        self.assertTrue(hash_value)
        # Check that hash has correct length
        self.assertEqual(len(hash_value), 32)
        
    def test_different_algorithms(self):
        """Test different hash algorithms."""
        data = b"test data"
        
        # Try each algorithm
        algorithms = ['improved', 'grover', 'shor', 'hybrid', 
                      'improved_grover', 'improved_shor']
        
        for algorithm in algorithms:
            hash_value = DiracHash.hash(data, algorithm=algorithm)
            
            # Check that hash is not empty
            self.assertTrue(hash_value)
            # Check that hash has correct length
            self.assertEqual(len(hash_value), 32)
            
    def test_custom_digest_size(self):
        """Test custom digest size."""
        data = b"test data"
        
        # Try different digest sizes
        for size in [16, 32, 64]:
            hash_value = DiracHash.hash(data, digest_size=size)
            
            # Check that hash is not empty
            self.assertTrue(hash_value)
            # Check that hash has correct length
            self.assertEqual(len(hash_value), size)


if __name__ == '__main__':
    unittest.main() 