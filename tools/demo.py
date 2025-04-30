#!/usr/bin/env python3
"""
Dirac Hashes - Complete Demonstration Script.

This script provides an interactive demonstration of quantum-inspired 
hash functions and post-quantum signature schemes included in the 
Dirac Hashes library.
"""

import time
import binascii
import sys
import os
from typing import Dict, List, Tuple, Any
import argparse

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import Dirac Hashes components
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


def hex_preview(data: bytes, max_length: int = 32) -> str:
    """Return a shortened hex representation of binary data."""
    hex_str = binascii.hexlify(data).decode('utf-8')
    if len(hex_str) > max_length:
        return hex_str[:max_length] + "..."
    return hex_str


class DiracDemo:
    """Interactive demonstration for Dirac Hashes library."""
    
    def __init__(self):
        """Initialize the demo."""
        self.interactive = True
        self.current_section = None
    
    def wait_for_input(self, message: str = "Press Enter to continue...") -> None:
        """Wait for user input if in interactive mode."""
        if self.interactive:
            input(message)
    
    def demonstrate_hash_functions(self) -> None:
        """Demonstrate quantum-inspired hash functions."""
        self.current_section = "hash"
        print_header("QUANTUM-INSPIRED HASH FUNCTIONS")
        print("This demonstration showcases the quantum-inspired hash functions in Dirac Hashes.")
        
        # Define algorithms to demonstrate
        algorithms = [
            'improved', 'grover', 'shor', 'hybrid', 
            'improved_grover', 'improved_shor'
        ]
        
        print("\nAvailable Hash Algorithms:")
        for i, algo in enumerate(algorithms, 1):
            print(f"  {i}. {algo}")
        
        self.wait_for_input()
        
        # Get sample data
        print("\nEnter a message to hash (or press Enter for default):")
        if self.interactive:
            message = input("> ").strip() or "Hello, quantum world!"
        else:
            message = "Hello, quantum world!"
        
        print(f"\nHashing message: '{message}'")
        print("\nResults:")
        print(f"{'Algorithm':<15} {'Digest (hex)':<40} {'Length':<8} {'Time (ms)':<10}")
        print("-" * 75)
        
        # Hash with all algorithms
        for algo in algorithms:
            start_time = time.time()
            digest = DiracHash.hash(message, algorithm=algo)
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            print(f"{algo:<15} {hex_preview(digest):<40} {len(digest):<8} {elapsed:.2f}")
        
        self.wait_for_input()
        
        # Demonstrate avalanche effect
        print("\nDemonstrating Avalanche Effect:")
        print("The avalanche effect is a desirable property of cryptographic hash functions")
        print("where a small change in the input causes a significant change in the output.")
        
        self.wait_for_input()
        
        # Create two slightly different messages
        message1 = "Hello, quantum world!"
        message2 = "Hello, quantum World!"
        
        print(f"\nOriginal message:  '{message1}'")
        print(f"Modified message:  '{message2}'")
        print(f"Difference:        {' ' * 14}^")
        
        # Compare hashes
        for algo in ['improved', 'hybrid']:
            print(f"\nAlgorithm: {algo}")
            
            hash1 = DiracHash.hash(message1, algorithm=algo)
            hash2 = DiracHash.hash(message2, algorithm=algo)
            
            print(f"Hash of original:  {hex_preview(hash1)}")
            print(f"Hash of modified: {hex_preview(hash2)}")
            
            # Count differing bits
            bit_diff = 0
            for b1, b2 in zip(hash1, hash2):
                xor = b1 ^ b2
                bit_diff += bin(xor).count('1')
            
            bit_diff_percent = (bit_diff / (len(hash1) * 8)) * 100
            print(f"Bits changed: {bit_diff} out of {len(hash1) * 8} ({bit_diff_percent:.2f}%)")
        
        self.wait_for_input()
        
        # Demonstrate HMAC
        print("\nDemonstrating HMAC (Hash-based Message Authentication Code):")
        print("HMAC is used to verify both the integrity and authenticity of a message.")
        
        key = DiracHash.generate_seed(16)
        print(f"\nGenerated Key: {hex_preview(key)}")
        
        print("\nComputing HMAC for various algorithms:")
        for algo in ['improved', 'hybrid']:
            hmac_digest = DiracHash.hmac(key, message1, algorithm=algo)
            print(f"HMAC-{algo:<8}: {hex_preview(hmac_digest)}")
        
        self.wait_for_input()
    
    def demonstrate_keypair_generation(self) -> None:
        """Demonstrate quantum-inspired key generation."""
        self.current_section = "keys"
        print_header("QUANTUM-INSPIRED KEY GENERATION")
        print("This demonstration showcases the quantum-inspired key generation in Dirac Hashes.")
        
        print("\nGenerating a keypair using the default improved algorithm:")
        private_key, public_key = DiracHash.generate_keypair()
        
        print(f"Private Key: {DiracHash.format_key(private_key)}")
        print(f"Public Key:  {DiracHash.format_key(public_key)}")
        
        print("\nDerive a child key for a specific purpose:")
        derived_key = DiracHash.derive_key(private_key, purpose="encryption")
        print(f"Derived Key: {DiracHash.format_key(derived_key)}")
        
        self.wait_for_input()
        
        print("\nKey formatting options:")
        formats = ['hex', 'base64', 'base58']
        for fmt in formats:
            formatted = DiracHash.format_key(private_key, format_type=fmt)
            print(f"{fmt}:   {formatted}")
            
            # Verify parsing works
            parsed = DiracHash.parse_key(formatted, format_type=fmt)
            if parsed == private_key:
                print(f"       ✓ Successfully parsed back to original key")
            else:
                print(f"       ✗ Failed to parse correctly")
        
        self.wait_for_input()
    
    def demonstrate_lamport_signatures(self) -> None:
        """Demonstrate Lamport signatures."""
        self.current_section = "lamport"
        print_header("LAMPORT SIGNATURE SCHEME")
        print("This demonstration showcases the Lamport one-time signature scheme.")
        print("Lamport signatures are quantum-resistant but can only be used once per key pair.")
        
        # Choose an algorithm
        algorithms = ['improved', 'grover', 'shor', 'hybrid']
        
        print("\nAvailable hash algorithms for Lamport:")
        for i, algo in enumerate(algorithms, 1):
            print(f"  {i}. {algo}")
        
        self.wait_for_input()
        
        # Get message to sign
        print("\nEnter a message to sign (or press Enter for default):")
        if self.interactive:
            message = input("> ").strip() or "Transfer 10 DIRAC tokens to Alice (0x1234...5678)"
        else:
            message = "Transfer 10 DIRAC tokens to Alice (0x1234...5678)"
        
        print(f"\nMessage to sign: '{message}'")
        
        # Initialize Lamport with improved algorithm
        print("\nUsing 'improved' algorithm for demonstration:")
        lamport = LamportSignature(hash_algorithm='improved')
        
        # Generate key pair
        print("\nGenerating key pair (this may take a moment)...")
        start_time = time.time()
        private_key, public_key = lamport.generate_keypair()
        key_gen_time = time.time() - start_time
        print(f"Key generation completed in {key_gen_time:.4f} seconds")
        
        # Signing
        print("\nSigning message...")
        start_time = time.time()
        signature = lamport.sign(message, private_key)
        signing_time = time.time() - start_time
        print(f"Signing completed in {signing_time:.4f} seconds")
        
        # Verification
        print("\nVerifying signature...")
        start_time = time.time()
        is_valid = lamport.verify(message, signature, public_key)
        verification_time = time.time() - start_time
        print(f"Verification completed in {verification_time:.4f} seconds")
        print(f"Signature valid: {'✓' if is_valid else '✗'}")
        
        # Key sizes
        private_key_size = sum(len(private_key[i][bit]) for i in range(256) for bit in [0, 1])
        public_key_size = sum(len(public_key[i][bit]) for i in range(256) for bit in [0, 1])
        signature_size = sum(len(sig) for sig in signature)
        
        print(f"\nKey and Signature Sizes:")
        print(f"  • Private Key: {private_key_size / 1024:.2f} KB")
        print(f"  • Public Key:  {public_key_size / 1024:.2f} KB")
        print(f"  • Signature:   {signature_size / 1024:.2f} KB")
        
        # Demonstrate what happens with modified message
        self.wait_for_input()
        
        print("\nAttempting to verify with a modified message:")
        modified_message = message + " (modified)"
        print(f"Modified message: '{modified_message}'")
        
        start_time = time.time()
        is_valid_modified = lamport.verify(modified_message, signature, public_key)
        verification_time = time.time() - start_time
        print(f"Verification completed in {verification_time:.4f} seconds")
        print(f"Signature valid for modified message: {'✓' if is_valid_modified else '✗'}")
        
        if not is_valid_modified:
            print("As expected, the signature is not valid for the modified message.")
            print("This demonstrates the integrity protection provided by the signature.")
        
        self.wait_for_input()
        
        print("\nImportant Security Notes:")
        print("  1. Each Lamport key pair MUST only be used once!")
        print("  2. The private key is large and must be stored securely")
        print("  3. Signatures are also large, around 8KB per signature")
        print("  4. Ideal for high-value, infrequent transactions")
        
        self.wait_for_input()
    
    def demonstrate_advanced_signatures(self) -> None:
        """Demonstrate advanced post-quantum signature schemes."""
        self.current_section = "advanced"
        print_header("ADVANCED POST-QUANTUM SIGNATURE SCHEMES")
        print("This demonstration showcases additional post-quantum signature schemes:")
        print("  • SPHINCS+ (stateless hash-based signatures)")
        print("  • CRYSTALS-Dilithium (lattice-based signatures)")
        print("  • CRYSTALS-Kyber (key encapsulation mechanism)")
        
        # Get message to sign
        print("\nEnter a message to sign (or press Enter for default):")
        if self.interactive:
            message = input("> ").strip() or "Transfer 10 DIRAC tokens to Alice (0x1234...5678)"
        else:
            message = "Transfer 10 DIRAC tokens to Alice (0x1234...5678)"
        
        print(f"\nMessage: '{message}'")
        
        self.wait_for_input()
        
        # SPHINCS+ demonstration
        print_header("SPHINCS+ SIGNATURE SCHEME")
        print("SPHINCS+ is a stateless hash-based signature scheme.")
        print("Unlike Lamport signatures, SPHINCS+ keys can be reused safely.")
        
        sphincs = SPHINCSSignature(hash_algorithm='improved', h=8, fast_mode=True)
        print("\nUsing SPHINCS+ with optimized parameters (h=8, fast_mode=True) for demonstration")
        
        # Generate key pair
        print("\nGenerating key pair...")
        start_time = time.time()
        private_key, public_key = sphincs.generate_keypair()
        key_gen_time = time.time() - start_time
        print(f"Key generation completed in {key_gen_time:.4f} seconds")
        
        # Signing
        print("\nSigning message...")
        start_time = time.time()
        signature = sphincs.sign(message, private_key)
        sign_time = time.time() - start_time
        print(f"Signing completed in {sign_time:.4f} seconds")
        
        # Verification
        print("\nVerifying signature...")
        start_time = time.time()
        is_valid = sphincs.verify(message, signature, public_key)
        verify_time = time.time() - start_time
        print(f"Verification completed in {verify_time:.4f} seconds")
        print(f"Signature valid: {'✓' if is_valid else '✗'}")
        
        # Convert to blockchain-compatible format
        blockchain_sig = sphincs.get_blockchain_compatible_format(signature)
        
        # Sizes
        private_key_size = len(private_key['sk_seed']) + len(private_key['pk_seed']) + len(private_key['pk_root'])
        public_key_size = len(public_key['pk_seed']) + len(public_key['pk_root'])
        signature_size = len(blockchain_sig)
        
        print(f"\nKey and Signature Sizes:")
        print(f"  • Private Key: {private_key_size} bytes")
        print(f"  • Public Key:  {public_key_size} bytes")
        print(f"  • Signature:   {signature_size} bytes")
        
        print(f"\nBlockchain-compatible signature (excerpt): {hex_preview(blockchain_sig)}")
        
        self.wait_for_input()
        
        # Dilithium demonstration
        print_header("CRYSTALS-DILITHIUM SIGNATURE SCHEME")
        print("Dilithium is a lattice-based signature scheme, efficient for general-purpose use.")
        print("It provides a good balance of security, performance, and key/signature size.")
        
        dilithium = DilithiumSignature(security_level=2, hash_algorithm='improved', fast_mode=True)
        print("\nUsing Dilithium with security level 2 (equivalent to AES-128) and fast mode")
        
        # Generate key pair
        print("\nGenerating key pair...")
        start_time = time.time()
        private_key, public_key = dilithium.generate_keypair()
        key_gen_time = time.time() - start_time
        print(f"Key generation completed in {key_gen_time:.4f} seconds")
        
        # Signing
        print("\nSigning message...")
        start_time = time.time()
        signature = dilithium.sign(message, private_key)
        sign_time = time.time() - start_time
        print(f"Signing completed in {sign_time:.4f} seconds")
        
        # Verification
        print("\nVerifying signature...")
        start_time = time.time()
        is_valid = dilithium.verify(message, signature, public_key)
        verify_time = time.time() - start_time
        print(f"Verification completed in {verify_time:.4f} seconds")
        print(f"Signature valid: {'✓' if is_valid else '✗'}")
        
        # Sizes
        private_key_size = len(private_key['rho']) + len(private_key['sigma']) + \
                          sum(len(s) for s in private_key['s']) + sum(len(e) for e in private_key['e'])
        public_key_size = len(public_key['rho']) + sum(len(t) for t in public_key['t'])
        signature_size = len(dilithium.get_blockchain_compatible_format(signature))
        
        print(f"\nKey and Signature Sizes:")
        print(f"  • Private Key: {private_key_size} bytes")
        print(f"  • Public Key:  {public_key_size} bytes")
        print(f"  • Signature:   {signature_size} bytes")
        
        self.wait_for_input()
        
        # Kyber KEM demonstration
        print_header("CRYSTALS-KYBER KEY ENCAPSULATION MECHANISM")
        print("Kyber is a lattice-based key encapsulation mechanism (KEM).")
        print("It's used for secure key exchange and encryption rather than signatures.")
        
        kyber = KyberKEM(security_level=1, hash_algorithm='improved')
        print("\nUsing Kyber-512 (security level 1)")
        
        # Generate key pair
        print("\nGenerating key pair for recipient...")
        start_time = time.time()
        private_key, public_key = kyber.generate_keypair()
        key_gen_time = time.time() - start_time
        print(f"Key generation completed in {key_gen_time:.4f} seconds")
        
        # Encapsulation (sender)
        print("\nSender encapsulating a shared secret...")
        start_time = time.time()
        ciphertext, sender_shared_secret = kyber.encapsulate(public_key)
        encap_time = time.time() - start_time
        print(f"Encapsulation completed in {encap_time:.4f} seconds")
        
        # Decapsulation (recipient)
        print("\nRecipient decapsulating the shared secret...")
        start_time = time.time()
        recipient_shared_secret = kyber.decapsulate(ciphertext, private_key)
        decap_time = time.time() - start_time
        print(f"Decapsulation completed in {decap_time:.4f} seconds")
        
        # Check if shared secrets match
        secrets_match = sender_shared_secret == recipient_shared_secret
        print(f"\nShared secrets match: {'✓' if secrets_match else '✗'}")
        
        # Display shared secret
        print(f"Shared Secret: {hex_preview(sender_shared_secret)}")
        
        # Sizes
        private_key_size = len(private_key['seed']) + sum(len(s) for s in private_key['s'])
        public_key_size = len(kyber.get_blockchain_compatible_keys(public_key))
        ciphertext_size = len(ciphertext)
        
        print(f"\nKey and Ciphertext Sizes:")
        print(f"  • Private Key: {private_key_size} bytes")
        print(f"  • Public Key:  {public_key_size} bytes")
        print(f"  • Ciphertext:  {ciphertext_size} bytes")
        
        self.wait_for_input()
    
    def demonstrate_comparison(self) -> None:
        """Demonstrate algorithm comparison."""
        self.current_section = "comparison"
        print_header("ALGORITHM COMPARISON FOR BLOCKCHAIN INTEGRATION")
        
        # Performance comparison table
        data = [
            ["Algorithm", "Key Size (B)", "Sig Size (B)", "Security", "Use Case"],
            ["Ed25519", "32/64", "64", "Classical", "General-purpose signatures (current)"],
            ["Lamport", "~16K/16K", "~8K", "Post-Quantum", "One-time signatures for critical ops"],
            ["SPHINCS+", "~64/~32", "~8K", "Post-Quantum", "Stateless replacement for Ed25519"],
            ["Kyber", "~1K/~1.5K", "~1K (cipher)", "Post-Quantum", "Key exchange, wallet encryption"],
            ["Dilithium", "~2.5K/~1.5K", "~2.5K", "Post-Quantum", "General-purpose signatures"]
        ]
        
        # Print formatted table
        col_widths = [max(len(str(row[i])) for row in data) for i in range(len(data[0]))]
        
        # Print header
        header = data[0]
        print("\n  " + "  ".join(f"{header[i]:<{col_widths[i]}}" for i in range(len(header))))
        print("  " + "  ".join("-" * col_widths[i] for i in range(len(header))))
        
        # Print data rows
        for row in data[1:]:
            print("  " + "  ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row))))
        
        print("\nIntegration Strategy:")
        print("  1. Immediate: Use Lamport for high-value operations with existing architecture")
        print("  2. Short-term: Add Kyber for encrypted communications and wallet security")
        print("  3. Medium-term: Implement SPHINCS+ or Dilithium as main signature algorithms")
        print("  4. Long-term: Full hybrid cryptography model supporting both classical and PQ")
        
        print("\nRecommended Approach for Blockchain Integration:")
        print("  • Solana: Dilithium for transaction signing, Kyber for encryption")
        print("  • Ethereum: SPHINCS+ for smart contract signatures, Kyber for secure channels")
        print("  • Bitcoin: Lamport for high-value transactions with P2SH scripts")
        
        self.wait_for_input()
    
    def run_demo(self, section: str = None, interactive: bool = True) -> None:
        """Run the full demonstration or a specific section."""
        self.interactive = interactive
        
        if section:
            self.current_section = section
            if section == "hash":
                self.demonstrate_hash_functions()
            elif section == "keys":
                self.demonstrate_keypair_generation()
            elif section == "lamport":
                self.demonstrate_lamport_signatures()
            elif section == "advanced":
                self.demonstrate_advanced_signatures()
            elif section == "comparison":
                self.demonstrate_comparison()
            else:
                print(f"Unknown section: {section}")
                print("Available sections: hash, keys, lamport, advanced, comparison")
            return
        
        # Full demonstration
        print_header("DIRAC HASHES COMPLETE DEMONSTRATION")
        print("This script demonstrates the quantum-inspired cryptographic primitives")
        print("provided by the Dirac Hashes library.")
        
        self.wait_for_input()
        
        # Run each demonstration in sequence
        self.demonstrate_hash_functions()
        self.demonstrate_keypair_generation()
        self.demonstrate_lamport_signatures()
        self.demonstrate_advanced_signatures()
        self.demonstrate_comparison()
        
        print_header("DEMONSTRATION COMPLETE")
        print("Thank you for exploring the Dirac Hashes library!")
        print("For more information, see the documentation in the 'info' directory.")


def main():
    """Run the demonstration."""
    parser = argparse.ArgumentParser(description="Dirac Hashes Demonstration")
    parser.add_argument("--section", "-s", type=str, 
                       choices=["hash", "keys", "lamport", "advanced", "comparison"],
                       help="Run a specific section of the demo")
    parser.add_argument("--non-interactive", "-n", action="store_true",
                       help="Run in non-interactive mode (no prompts)")
    
    args = parser.parse_args()
    
    demo = DiracDemo()
    demo.run_demo(section=args.section, interactive=not args.non_interactive)


if __name__ == "__main__":
    main() 