#!/usr/bin/env python3
"""
Comprehensive test suite for the Dirac Hashes library.

This script runs all tests for the quantum-inspired hash functions and
post-quantum signature schemes implemented in the library.
"""

import unittest
import sys
import os
import time
from typing import Dict, List, Any

# Import components for testing
from src.quantum_hash.dirac import DiracHash
from src.quantum_hash.signatures.lamport import LamportSignature
from src.quantum_hash.signatures.sphincs import SPHINCSSignature
from src.quantum_hash.signatures.kyber import KyberKEM
from src.quantum_hash.signatures.dilithium import DilithiumSignature


def print_header(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


class DiracTestRunner:
    """Class to run all tests for the Dirac Hashes library."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.results = {
            "hash_tests": {},
            "lamport_tests": {},
            "sphincs_tests": {},
            "kyber_tests": {},
            "dilithium_tests": {},
        }
    
    def run_unittest_suite(self) -> bool:
        """Run the standard unittest test suite."""
        print_header("RUNNING UNITTEST TEST SUITE")
        
        # Create a test loader
        loader = unittest.TestLoader()
        
        # Load tests from the tests directory
        try:
            test_suite = loader.discover('tests')
            
            # Run the tests
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(test_suite)
            
            return result.wasSuccessful()
        except Exception as e:
            print(f"Error running unittest suite: {e}")
            return False
    
    def test_hash_functions(self) -> bool:
        """Test all hash functions."""
        print_header("TESTING HASH FUNCTIONS")
        
        test_data = b"This is a test message for hash function verification"
        algorithms = ['improved', 'grover', 'shor', 'hybrid', 
                      'improved_grover', 'improved_shor']
        
        success = True
        
        print(f"{'Algorithm':<15} {'Digest Length':<15} {'Time (s)':<10} {'Result':<10}")
        print("-" * 55)
        
        for algo in algorithms:
            try:
                start_time = time.time()
                digest = DiracHash.hash(test_data, algorithm=algo)
                elapsed = time.time() - start_time
                
                # Simple verification test
                verify1 = DiracHash.hash(test_data, algorithm=algo)
                verify2 = DiracHash.hash(test_data + b"X", algorithm=algo)
                
                # Check if hash function is deterministic and different inputs give different outputs
                is_valid = (digest == verify1) and (digest != verify2)
                
                self.results["hash_tests"][algo] = {
                    "digest_length": len(digest),
                    "time": elapsed,
                    "valid": is_valid
                }
                
                print(f"{algo:<15} {len(digest):<15} {elapsed:.6f}    {'✓' if is_valid else '✗'}")
                
                if not is_valid:
                    success = False
            except Exception as e:
                print(f"{algo:<15} Error: {str(e)}")
                self.results["hash_tests"][algo] = {
                    "error": str(e),
                    "valid": False
                }
                success = False
        
        return success
    
    def test_lamport_signatures(self) -> bool:
        """Test Lamport signatures with all hash algorithms."""
        print_header("TESTING LAMPORT SIGNATURES")
        
        algorithms = ['improved', 'grover', 'shor', 'hybrid', 
                      'improved_grover', 'improved_shor']
        test_message = "This is a test message for Lamport signature verification"
        
        print(f"{'Algorithm':<15} {'Key Gen (s)':<12} {'Signing (s)':<12} {'Verify (s)':<12} {'Result':<8}")
        print("-" * 65)
        
        success = True
        
        for algo in algorithms:
            try:
                # Initialize with the algorithm
                lamport = LamportSignature(hash_algorithm=algo)
                
                # Generate key pair
                start_time = time.time()
                private_key, public_key = lamport.generate_keypair()
                key_gen_time = time.time() - start_time
                
                # Sign
                start_time = time.time()
                signature = lamport.sign(test_message, private_key)
                signing_time = time.time() - start_time
                
                # Verify valid signature
                start_time = time.time()
                is_valid = lamport.verify(test_message, signature, public_key)
                verification_time = time.time() - start_time
                
                # Verify invalid signature (modified message)
                modified_message = test_message + " (modified)"
                is_invalid = not lamport.verify(modified_message, signature, public_key)
                
                # Both tests should pass
                test_passed = is_valid and is_invalid
                
                self.results["lamport_tests"][algo] = {
                    "key_gen_time": key_gen_time,
                    "signing_time": signing_time,
                    "verification_time": verification_time,
                    "valid": test_passed
                }
                
                print(f"{algo:<15} {key_gen_time:.4f}       {signing_time:.4f}       {verification_time:.4f}       {'✓' if test_passed else '✗'}")
                
                if not test_passed:
                    success = False
            except Exception as e:
                print(f"{algo:<15} Error: {str(e)}")
                self.results["lamport_tests"][algo] = {
                    "error": str(e),
                    "valid": False
                }
                success = False
        
        return success
    
    def test_advanced_signatures(self) -> bool:
        """Test SPHINCS+, Kyber and Dilithium with default settings."""
        print_header("TESTING ADVANCED POST-QUANTUM SCHEMES")
        
        test_message = "This is a test message for signature verification"
        success = True
        
        # Test SPHINCS+ (with reduced height for speed)
        print("\nTesting SPHINCS+ (stateless hash-based signatures):")
        try:
            sphincs = SPHINCSSignature(hash_algorithm='improved', h=8, fast_mode=True)
            
            start_time = time.time()
            private_key, public_key = sphincs.generate_keypair()
            key_gen_time = time.time() - start_time
            
            start_time = time.time()
            signature = sphincs.sign(test_message, private_key)
            sign_time = time.time() - start_time
            
            start_time = time.time()
            is_valid = sphincs.verify(test_message, signature, public_key)
            verify_time = time.time() - start_time
            
            self.results["sphincs_tests"]["default"] = {
                "key_gen_time": key_gen_time,
                "signing_time": sign_time,
                "verification_time": verify_time,
                "valid": is_valid
            }
            
            print(f"  Key Generation: {key_gen_time:.4f}s, Signing: {sign_time:.4f}s, Verification: {verify_time:.4f}s")
            print(f"  Verification Result: {'Valid ✓' if is_valid else 'Invalid ✗'}")
            
            if not is_valid:
                success = False
        except Exception as e:
            print(f"  Error: {str(e)}")
            self.results["sphincs_tests"]["default"] = {
                "error": str(e),
                "valid": False
            }
            success = False
        
        # Test Kyber KEM
        print("\nTesting CRYSTALS-Kyber (key encapsulation mechanism):")
        try:
            kyber = KyberKEM(security_level=1, hash_algorithm='improved')
            
            start_time = time.time()
            private_key, public_key = kyber.generate_keypair()
            key_gen_time = time.time() - start_time
            
            start_time = time.time()
            ciphertext, sender_shared_secret = kyber.encapsulate(public_key)
            encap_time = time.time() - start_time
            
            start_time = time.time()
            recipient_shared_secret = kyber.decapsulate(ciphertext, private_key)
            decap_time = time.time() - start_time
            
            secrets_match = sender_shared_secret == recipient_shared_secret
            
            self.results["kyber_tests"]["default"] = {
                "key_gen_time": key_gen_time,
                "encapsulation_time": encap_time,
                "decapsulation_time": decap_time,
                "valid": secrets_match
            }
            
            print(f"  Key Generation: {key_gen_time:.4f}s, Encapsulation: {encap_time:.4f}s, Decapsulation: {decap_time:.4f}s")
            print(f"  Shared Secrets Match: {'Yes ✓' if secrets_match else 'No ✗'}")
            
            if not secrets_match:
                success = False
        except Exception as e:
            print(f"  Error: {str(e)}")
            self.results["kyber_tests"]["default"] = {
                "error": str(e),
                "valid": False
            }
            success = False
        
        # Test Dilithium
        print("\nTesting CRYSTALS-Dilithium (general-purpose signatures):")
        try:
            dilithium = DilithiumSignature(security_level=2, hash_algorithm='improved', fast_mode=True)
            
            start_time = time.time()
            private_key, public_key = dilithium.generate_keypair()
            key_gen_time = time.time() - start_time
            
            start_time = time.time()
            signature = dilithium.sign(test_message, private_key)
            sign_time = time.time() - start_time
            
            start_time = time.time()
            is_valid = dilithium.verify(test_message, signature, public_key)
            verify_time = time.time() - start_time
            
            self.results["dilithium_tests"]["default"] = {
                "key_gen_time": key_gen_time,
                "signing_time": sign_time,
                "verification_time": verify_time,
                "valid": is_valid
            }
            
            print(f"  Key Generation: {key_gen_time:.4f}s, Signing: {sign_time:.4f}s, Verification: {verify_time:.4f}s")
            print(f"  Verification Result: {'Valid ✓' if is_valid else 'Invalid ✗'}")
            
            if not is_valid:
                success = False
        except Exception as e:
            print(f"  Error: {str(e)}")
            self.results["dilithium_tests"]["default"] = {
                "error": str(e),
                "valid": False
            }
            success = False
        
        return success
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print_header("DIRAC HASHES COMPREHENSIVE TEST SUITE")
        print("Running all tests for quantum-inspired hash functions and post-quantum signatures...\n")
        
        # Track overall success
        overall_success = True
        
        # Run unittest suite if available
        unittest_success = self.run_unittest_suite()
        overall_success = overall_success and unittest_success
        
        # Test hash functions
        hash_success = self.test_hash_functions()
        overall_success = overall_success and hash_success
        
        # Test Lamport signatures
        lamport_success = self.test_lamport_signatures()
        overall_success = overall_success and lamport_success
        
        # Test advanced signature schemes
        advanced_success = self.test_advanced_signatures()
        overall_success = overall_success and advanced_success
        
        # Print summary
        print_header("TEST SUMMARY")
        print(f"Hash Functions:        {'✓ PASSED' if hash_success else '✗ FAILED'}")
        print(f"Lamport Signatures:    {'✓ PASSED' if lamport_success else '✗ FAILED'}")
        print(f"Advanced PQ Schemes:   {'✓ PASSED' if advanced_success else '✗ FAILED'}")
        print(f"Unittest Suite:        {'✓ PASSED' if unittest_success else '✗ FAILED'}")
        print(f"\nOverall Test Result:   {'✓ PASSED' if overall_success else '✗ FAILED'}")
        
        return self.results


def main() -> None:
    """Run the test suite."""
    runner = DiracTestRunner()
    results = runner.run_all_tests()
    
    # Exit with appropriate status code
    if all(result.get("valid", False) for category in results for result in results[category].values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main() 