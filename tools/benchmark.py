#!/usr/bin/env python3
"""
Benchmark script for Dirac Hashes library.

This script provides comprehensive benchmarking for quantum-inspired hash functions
and post-quantum signature schemes, including visualization capabilities
for presenting to VCs and funding providers.
"""

import time
import os
import numpy as np
import hashlib
from typing import Dict, List, Tuple, Any
import multiprocessing
from collections import defaultdict
import json

# Import visualization libraries if available
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import seaborn as sns
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    print("Warning: Visualization libraries not found. Installing required packages...")
    print("Run 'pip install matplotlib seaborn' for visualization support.")

# Import Dirac Hashes components
from src.quantum_hash.dirac import DiracHash
from src.quantum_hash.signatures.lamport import LamportSignature
from src.quantum_hash.signatures.sphincs import SPHINCSSignature
from src.quantum_hash.signatures.kyber import KyberKEM
from src.quantum_hash.signatures.dilithium import DilithiumSignature


class Benchmark:
    """Benchmark suite for quantum-inspired cryptographic primitives."""
    
    def __init__(self, output_dir="benchmark_results"):
        """Initialize benchmark suite."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Store results
        self.results = {
            "hash_speed": {},
            "hash_security": {},
            "signature_performance": {},
            "comparison": {}
        }
        
        # Define algorithms to test
        self.hash_algorithms = [
            'improved', 'grover', 'shor', 'hybrid', 
            'improved_grover', 'improved_shor'
        ]
        
        # Add standard hash functions for comparison
        self.standard_algorithms = ['SHA-256', 'SHA3-256', 'BLAKE2b']
        
        # Initialize result storage
        for algo in self.hash_algorithms + self.standard_algorithms:
            self.results["hash_speed"][algo] = {}
            self.results["hash_security"][algo] = {}
    
    def run_hash_speed_benchmark(self, sizes=[16, 64, 256, 1024, 4096], 
                                iterations=100, warmup=10) -> Dict[str, Any]:
        """
        Benchmark hash function speed across different input sizes.
        
        Args:
            sizes: List of input sizes to test (in bytes)
            iterations: Number of iterations for each test
            warmup: Number of warmup iterations
            
        Returns:
            Dictionary with benchmark results
        """
        print("\n=== Hash Function Speed Benchmark ===\n")
        print(f"Testing hash speed for {len(self.hash_algorithms + self.standard_algorithms)} algorithms")
        print(f"Input sizes: {sizes} bytes")
        print(f"Iterations: {iterations}\n")
        
        results = {}
        
        # Prepare header row for table
        headers = ["Algorithm"] + [f"{size} bytes (MB/s)" for size in sizes]
        print(" | ".join(headers))
        print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
        
        # Test Dirac Hash algorithms
        for algo in self.hash_algorithms:
            results[algo] = {}
            speeds = []
            
            for size in sizes:
                # Generate random test data
                data = os.urandom(size)
                
                # Warmup
                for _ in range(warmup):
                    _ = DiracHash.hash(data, algorithm=algo)
                
                # Timed benchmark
                start_time = time.time()
                for _ in range(iterations):
                    _ = DiracHash.hash(data, algorithm=algo)
                elapsed = time.time() - start_time
                
                # Calculate speed in MB/s
                mb_processed = (size * iterations) / (1024 * 1024)
                speed = mb_processed / elapsed
                
                results[algo][size] = speed
                speeds.append(f"{speed:.2f}")
            
            # Print results row
            print(f"{algo:<10} | {' | '.join(speeds)}")
        
        # Test standard hash algorithms
        for algo in self.standard_algorithms:
            results[algo] = {}
            speeds = []
            
            for size in sizes:
                # Generate random test data
                data = os.urandom(size)
                
                # Get hash function
                if algo == 'SHA-256':
                    hash_func = lambda x: hashlib.sha256(x).digest()
                elif algo == 'SHA3-256':
                    hash_func = lambda x: hashlib.sha3_256(x).digest()
                elif algo == 'BLAKE2b':
                    hash_func = lambda x: hashlib.blake2b(x).digest()
                
                # Warmup
                for _ in range(warmup):
                    _ = hash_func(data)
                
                # Timed benchmark
                start_time = time.time()
                for _ in range(iterations):
                    _ = hash_func(data)
                elapsed = time.time() - start_time
                
                # Calculate speed in MB/s
                mb_processed = (size * iterations) / (1024 * 1024)
                speed = mb_processed / elapsed
                
                results[algo][size] = speed
                speeds.append(f"{speed:.2f}")
            
            # Print results row
            print(f"{algo:<10} | {' | '.join(speeds)}")
        
        self.results["hash_speed"] = results
        return results
    
    def run_security_benchmark(self, iterations=100) -> Dict[str, Any]:
        """
        Benchmark hash function security properties.
        
        Args:
            iterations: Number of iterations for statistical tests
            
        Returns:
            Dictionary with security benchmark results
        """
        print("\n=== Hash Function Security Benchmark ===\n")
        
        results = {}
        
        # Test all algorithms
        for algo in self.hash_algorithms + self.standard_algorithms:
            results[algo] = {}
            
            # Get hash function
            if algo in self.hash_algorithms:
                hash_func = lambda x: DiracHash.hash(x, algorithm=algo)
            elif algo == 'SHA-256':
                hash_func = lambda x: hashlib.sha256(x).digest()
            elif algo == 'SHA3-256':
                hash_func = lambda x: hashlib.sha3_256(x).digest()
            elif algo == 'BLAKE2b':
                hash_func = lambda x: hashlib.blake2b(x).digest()
            
            # Test avalanche effect
            avalanche = self._test_avalanche_effect(hash_func, iterations)
            results[algo]['avalanche'] = avalanche
            
            # Test collision resistance
            collisions = self._test_collision_resistance(hash_func, iterations)
            results[algo]['collisions'] = collisions
            
            # Test distribution
            entropy, chi_square = self._test_distribution(hash_func, iterations)
            results[algo]['entropy'] = entropy
            results[algo]['chi_square'] = chi_square
            
            print(f"{algo:<10} | Avalanche: {avalanche:.2f}% | Entropy: {entropy:.4f} | Chi-square: {chi_square:.2f} | Collisions: {collisions}")
        
        self.results["hash_security"] = results
        return results
    
    def _test_avalanche_effect(self, hash_func, iterations=100) -> float:
        """
        Test the avalanche effect of a hash function.
        
        Args:
            hash_func: Hash function to test
            iterations: Number of iterations for the test
            
        Returns:
            Percentage of bits changed on average
        """
        total_bit_diff_percent = 0
        
        for _ in range(iterations):
            # Generate random data
            data = os.urandom(32)
            
            # Hash original data
            hash1 = hash_func(data)
            
            # Flip a random bit in the data
            bit_pos = np.random.randint(0, len(data) * 8)
            byte_pos = bit_pos // 8
            bit_in_byte = bit_pos % 8
            
            # Create a copy with a single bit flipped
            data_modified = bytearray(data)
            data_modified[byte_pos] ^= (1 << bit_in_byte)
            
            # Hash modified data
            hash2 = hash_func(bytes(data_modified))
            
            # Count differing bits
            bit_diff = 0
            for b1, b2 in zip(hash1, hash2):
                xor = b1 ^ b2
                bit_diff += bin(xor).count('1')
            
            # Calculate percentage of bits changed
            bit_diff_percent = (bit_diff / (len(hash1) * 8)) * 100
            total_bit_diff_percent += bit_diff_percent
        
        # Return average percentage
        return total_bit_diff_percent / iterations
    
    def _test_collision_resistance(self, hash_func, iterations=1000) -> int:
        """
        Test collision resistance of a hash function.
        
        Args:
            hash_func: Hash function to test
            iterations: Number of iterations for the test
            
        Returns:
            Number of collisions found
        """
        hashes = set()
        collisions = 0
        
        for _ in range(iterations):
            # Generate random data
            data = os.urandom(16)
            
            # Compute hash
            hash_value = hash_func(data)
            
            # Check for collision
            if hash_value in hashes:
                collisions += 1
            else:
                hashes.add(hash_value)
        
        return collisions
    
    def _test_distribution(self, hash_func, iterations=1000) -> Tuple[float, float]:
        """
        Test the distribution properties of a hash function.
        
        Args:
            hash_func: Hash function to test
            iterations: Number of iterations for the test
            
        Returns:
            Tuple of (entropy, chi_square_test_value)
        """
        # Generate hash values
        hash_values = []
        for _ in range(iterations):
            data = os.urandom(16)
            hash_value = hash_func(data)
            hash_values.append(hash_value)
        
        # Convert to numpy array for analysis
        hash_array = np.array([np.frombuffer(h, dtype=np.uint8) for h in hash_values])
        
        # Calculate entropy
        entropy = 0
        for byte_pos in range(hash_array.shape[1]):
            byte_values, counts = np.unique(hash_array[:, byte_pos], return_counts=True)
            probs = counts / len(hash_values)
            byte_entropy = -np.sum(probs * np.log2(probs))
            entropy += byte_entropy
        
        # Normalize entropy
        entropy /= hash_array.shape[1]
        
        # Calculate chi-square test (simplified, for byte distribution)
        chi_square = 0
        expected = iterations / 256  # Expected count for each byte value
        for byte_pos in range(min(4, hash_array.shape[1])):  # First 4 bytes only for speed
            observed, _ = np.histogram(hash_array[:, byte_pos], bins=256, range=(0, 256))
            chi_square += np.sum((observed - expected) ** 2 / expected)
        
        # Normalize chi-square
        chi_square /= min(4, hash_array.shape[1])
        
        return entropy, chi_square
    
    def run_signature_benchmark(self) -> Dict[str, Any]:
        """
        Benchmark signature schemes.
        
        Returns:
            Dictionary with signature benchmark results
        """
        print("\n=== Signature Scheme Benchmark ===\n")
        
        results = {}
        test_message = "This is a test message for benchmarking signature schemes"
        
        # Benchmark Lamport signatures with different hash algorithms
        print("Benchmarking Lamport signatures...")
        results['lamport'] = {}
        
        for algo in ['improved', 'grover', 'hybrid']:
            print(f"  Testing with {algo} algorithm...")
            lamport = LamportSignature(hash_algorithm=algo)
            
            # Measure key generation time
            start_time = time.time()
            private_key, public_key = lamport.generate_keypair()
            key_gen_time = time.time() - start_time
            
            # Measure signing time
            start_time = time.time()
            signature = lamport.sign(test_message, private_key)
            sign_time = time.time() - start_time
            
            # Measure verification time
            start_time = time.time()
            _ = lamport.verify(test_message, signature, public_key)
            verify_time = time.time() - start_time
            
            # Calculate sizes
            private_key_size = sum(len(private_key[i][bit]) for i in range(256) for bit in [0, 1])
            public_key_size = sum(len(public_key[i][bit]) for i in range(256) for bit in [0, 1])
            signature_size = sum(len(sig) for sig in signature)
            
            results['lamport'][algo] = {
                'key_gen_time': key_gen_time,
                'sign_time': sign_time,
                'verify_time': verify_time,
                'private_key_size': private_key_size,
                'public_key_size': public_key_size,
                'signature_size': signature_size
            }
            
            print(f"    Key Gen: {key_gen_time:.4f}s, Sign: {sign_time:.4f}s, Verify: {verify_time:.4f}s")
            print(f"    Private Key: {private_key_size/1024:.2f} KB, Public Key: {public_key_size/1024:.2f} KB, Signature: {signature_size/1024:.2f} KB")
        
        # Benchmark SPHINCS+
        print("\nBenchmarking SPHINCS+ signatures...")
        results['sphincs'] = {}
        
        sphincs = SPHINCSSignature(hash_algorithm='improved', h=8, fast_mode=True)
        
        # Measure key generation time
        start_time = time.time()
        private_key, public_key = sphincs.generate_keypair()
        key_gen_time = time.time() - start_time
        
        # Measure signing time
        start_time = time.time()
        signature = sphincs.sign(test_message, private_key)
        sign_time = time.time() - start_time
        
        # Measure verification time
        start_time = time.time()
        _ = sphincs.verify(test_message, signature, public_key)
        verify_time = time.time() - start_time
        
        # Calculate sizes
        private_key_size = len(private_key['sk_seed']) + len(private_key['pk_seed']) + len(private_key['pk_root'])
        public_key_size = len(public_key['pk_seed']) + len(public_key['pk_root'])
        signature_size = len(sphincs.get_blockchain_compatible_format(signature))
        
        results['sphincs']['default'] = {
            'key_gen_time': key_gen_time,
            'sign_time': sign_time,
            'verify_time': verify_time,
            'private_key_size': private_key_size,
            'public_key_size': public_key_size,
            'signature_size': signature_size
        }
        
        print(f"  Key Gen: {key_gen_time:.4f}s, Sign: {sign_time:.4f}s, Verify: {verify_time:.4f}s")
        print(f"  Private Key: {private_key_size} bytes, Public Key: {public_key_size} bytes, Signature: {signature_size} bytes")
        
        # Benchmark Dilithium
        print("\nBenchmarking Dilithium signatures...")
        results['dilithium'] = {}
        
        for level in [1, 2]:
            print(f"  Testing with security level {level}...")
            dilithium = DilithiumSignature(security_level=level, hash_algorithm='improved', fast_mode=True)
            
            # Measure key generation time
            start_time = time.time()
            private_key, public_key = dilithium.generate_keypair()
            key_gen_time = time.time() - start_time
            
            # Measure signing time
            start_time = time.time()
            signature = dilithium.sign(test_message, private_key)
            sign_time = time.time() - start_time
            
            # Measure verification time
            start_time = time.time()
            _ = dilithium.verify(test_message, signature, public_key)
            verify_time = time.time() - start_time
            
            # Calculate sizes
            private_key_size = len(private_key['rho']) + len(private_key['sigma']) + \
                               sum(len(s) for s in private_key['s']) + sum(len(e) for e in private_key['e'])
            public_key_size = len(public_key['rho']) + sum(len(t) for t in public_key['t'])
            signature_size = len(dilithium.get_blockchain_compatible_format(signature))
            
            results['dilithium'][f'level{level}'] = {
                'key_gen_time': key_gen_time,
                'sign_time': sign_time,
                'verify_time': verify_time,
                'private_key_size': private_key_size,
                'public_key_size': public_key_size,
                'signature_size': signature_size
            }
            
            print(f"    Key Gen: {key_gen_time:.4f}s, Sign: {sign_time:.4f}s, Verify: {verify_time:.4f}s")
            print(f"    Private Key: {private_key_size} bytes, Public Key: {public_key_size} bytes, Signature: {signature_size} bytes")
        
        # Benchmark Kyber KEM
        print("\nBenchmarking Kyber KEM...")
        results['kyber'] = {}
        
        for level in [1, 3]:
            print(f"  Testing with security level {level}...")
            kyber = KyberKEM(security_level=level, hash_algorithm='improved')
            
            # Measure key generation time
            start_time = time.time()
            private_key, public_key = kyber.generate_keypair()
            key_gen_time = time.time() - start_time
            
            # Measure encapsulation time
            start_time = time.time()
            ciphertext, shared_secret = kyber.encapsulate(public_key)
            encap_time = time.time() - start_time
            
            # Measure decapsulation time
            start_time = time.time()
            _ = kyber.decapsulate(ciphertext, private_key)
            decap_time = time.time() - start_time
            
            # Calculate sizes
            private_key_size = len(private_key['seed']) + sum(len(s) for s in private_key['s'])
            public_key_size = len(kyber.get_blockchain_compatible_keys(public_key))
            ciphertext_size = len(ciphertext)
            
            results['kyber'][f'level{level}'] = {
                'key_gen_time': key_gen_time,
                'encap_time': encap_time,
                'decap_time': decap_time,
                'private_key_size': private_key_size,
                'public_key_size': public_key_size,
                'ciphertext_size': ciphertext_size
            }
            
            print(f"    Key Gen: {key_gen_time:.4f}s, Encap: {encap_time:.4f}s, Decap: {decap_time:.4f}s")
            print(f"    Private Key: {private_key_size} bytes, Public Key: {public_key_size} bytes, Ciphertext: {ciphertext_size} bytes")
        
        self.results["signature_performance"] = results
        return results
    
    def create_visualizations(self):
        """Create visualizations from benchmark results."""
        if not HAS_VISUALIZATION:
            print("Visualization libraries not available. Skipping visualization creation.")
            return
        
        print("\n=== Creating Visualizations ===\n")
        os.makedirs(os.path.join(self.output_dir, "graphs"), exist_ok=True)
        
        # Set global plot style
        plt.style.use('ggplot')
        sns.set_style("whitegrid")
        
        # Create hash speed comparison chart
        self._create_hash_speed_chart()
        
        # Create avalanche effect chart
        self._create_avalanche_chart()
        
        # Create signature performance chart
        self._create_signature_performance_chart()
        
        # Create key/signature size comparison
        self._create_size_comparison_chart()
        
        print("Visualizations created successfully in:", os.path.join(self.output_dir, "graphs"))
    
    def _create_hash_speed_chart(self):
        """Create a chart comparing hash speeds."""
        if not self.results["hash_speed"]:
            print("No hash speed data available for visualization.")
            return
        
        data_sizes = sorted(next(iter(self.results["hash_speed"].values())).keys())
        algorithms = list(self.results["hash_speed"].keys())
        
        # Separate Dirac and standard algorithms
        dirac_algos = [a for a in algorithms if a in self.hash_algorithms]
        std_algos = [a for a in algorithms if a in self.standard_algorithms]
        
        # Create chart for medium-sized data (256 bytes)
        if 256 in data_sizes:
            plt.figure(figsize=(12, 6))
            
            # First plot: Standard algorithms
            speeds = [self.results["hash_speed"][algo][256] for algo in std_algos]
            plt.bar(std_algos, speeds, color='navy', alpha=0.7)
            
            # Second plot: Dirac algorithms (use different scale)
            ax2 = plt.twinx()
            dirac_speeds = [self.results["hash_speed"][algo][256] for algo in dirac_algos]
            ax2.bar([a + ' ' for a in dirac_algos], dirac_speeds, color='crimson', alpha=0.7)
            
            # Labels and title
            plt.title("Hash Speed Comparison (256 byte input)", fontsize=16)
            plt.xlabel("Hash Algorithm", fontsize=12)
            plt.ylabel("Speed (MB/s) - Standard Algorithms", fontsize=12)
            ax2.set_ylabel("Speed (MB/s) - Dirac Algorithms", fontsize=12)
            
            # Legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='navy', lw=4, label='Standard Algorithms'),
                Line2D([0], [0], color='crimson', lw=4, label='Dirac Algorithms')
            ]
            plt.legend(handles=legend_elements, loc='upper right')
            
            # Save the figure
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "graphs", "hash_speed_comparison.png"), dpi=300)
            plt.close()
            
        # Create chart for speed across different data sizes
        plt.figure(figsize=(14, 8))
        
        # Plot for standard algorithms
        for algo in std_algos:
            sizes = sorted(self.results["hash_speed"][algo].keys())
            speeds = [self.results["hash_speed"][algo][size] for size in sizes]
            plt.plot(sizes, speeds, marker='o', linewidth=2, label=algo)
        
        # Add log scales
        plt.xscale('log', base=2)
        plt.yscale('log', base=10)
        
        # Labels and title
        plt.title("Hash Speed vs. Input Size (Standard Algorithms)", fontsize=16)
        plt.xlabel("Input Size (bytes)", fontsize=12)
        plt.ylabel("Speed (MB/s)", fontsize=12)
        plt.legend()
        plt.grid(True, which="both", ls="-", alpha=0.2)
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "graphs", "hash_speed_by_size_standard.png"), dpi=300)
        plt.close()
        
        # Plot for Dirac algorithms
        plt.figure(figsize=(14, 8))
        for algo in dirac_algos:
            sizes = sorted(self.results["hash_speed"][algo].keys())
            speeds = [self.results["hash_speed"][algo][size] for size in sizes]
            plt.plot(sizes, speeds, marker='o', linewidth=2, label=algo)
        
        # Add log scales
        plt.xscale('log', base=2)
        plt.yscale('log', base=10)
        
        # Labels and title
        plt.title("Hash Speed vs. Input Size (Dirac Algorithms)", fontsize=16)
        plt.xlabel("Input Size (bytes)", fontsize=12)
        plt.ylabel("Speed (MB/s)", fontsize=12)
        plt.legend()
        plt.grid(True, which="both", ls="-", alpha=0.2)
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "graphs", "hash_speed_by_size_dirac.png"), dpi=300)
        plt.close()
    
    def _create_avalanche_chart(self):
        """Create a chart showing avalanche effect."""
        if not self.results["hash_security"]:
            print("No hash security data available for visualization.")
            return
        
        algorithms = list(self.results["hash_security"].keys())
        avalanche_values = [self.results["hash_security"][algo]["avalanche"] for algo in algorithms]
        
        # Create chart
        plt.figure(figsize=(12, 6))
        
        # Create bars
        bars = plt.bar(algorithms, avalanche_values, color='skyblue')
        
        # Add ideal line at 50%
        plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, label="Ideal (50%)")
        
        # Color bars based on how close they are to 50%
        for i, bar in enumerate(bars):
            # Calculate distance from ideal 50%
            distance = abs(avalanche_values[i] - 50)
            # Color gradient: green (close to 50%) to red (far from 50%)
            if distance < 5:
                bar.set_color('green')
            elif distance < 10:
                bar.set_color('yellowgreen')
            elif distance < 15:
                bar.set_color('gold')
            elif distance < 20:
                bar.set_color('orange')
            else:
                bar.set_color('red')
        
        # Labels and title
        plt.title("Avalanche Effect Comparison", fontsize=16)
        plt.xlabel("Hash Algorithm", fontsize=12)
        plt.ylabel("Bit Change Percentage (%)", fontsize=12)
        plt.ylim(0, 100)
        
        # Add value labels
        for i, v in enumerate(avalanche_values):
            plt.text(i, v + 2, f"{v:.1f}%", ha='center')
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "graphs", "avalanche_effect.png"), dpi=300)
        plt.close()
        
        # Create entropy chart
        entropy_values = [self.results["hash_security"][algo]["entropy"] for algo in algorithms]
        
        plt.figure(figsize=(12, 6))
        plt.bar(algorithms, entropy_values, color='teal')
        
        # Labels and title
        plt.title("Entropy Comparison", fontsize=16)
        plt.xlabel("Hash Algorithm", fontsize=12)
        plt.ylabel("Entropy (bits)", fontsize=12)
        
        # Add value labels
        for i, v in enumerate(entropy_values):
            plt.text(i, v + 0.1, f"{v:.2f}", ha='center')
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "graphs", "entropy_comparison.png"), dpi=300)
        plt.close()
    
    def _create_signature_performance_chart(self):
        """Create charts comparing signature schemes performance."""
        if not self.results["signature_performance"]:
            print("No signature performance data available for visualization.")
            return
        
        # Extract data
        schemes = []
        key_gen_times = []
        sign_times = []
        verify_times = []
        
        # Process Lamport results
        for algo, data in self.results["signature_performance"]["lamport"].items():
            schemes.append(f"Lamport-{algo}")
            key_gen_times.append(data["key_gen_time"])
            sign_times.append(data["sign_time"])
            verify_times.append(data["verify_time"])
        
        # Process SPHINCS+ results
        for variant, data in self.results["signature_performance"]["sphincs"].items():
            schemes.append(f"SPHINCS+-{variant}")
            key_gen_times.append(data["key_gen_time"])
            sign_times.append(data["sign_time"])
            verify_times.append(data["verify_time"])
        
        # Process Dilithium results
        for variant, data in self.results["signature_performance"]["dilithium"].items():
            schemes.append(f"Dilithium-{variant}")
            key_gen_times.append(data["key_gen_time"])
            sign_times.append(data["sign_time"])
            verify_times.append(data["verify_time"])
        
        # Create grouped bar chart
        plt.figure(figsize=(14, 8))
        
        # Set position of bars on X axis
        x = np.arange(len(schemes))
        width = 0.25
        
        # Create bars
        plt.bar(x - width, key_gen_times, width, label='Key Generation', color='royalblue')
        plt.bar(x, sign_times, width, label='Signing', color='forestgreen')
        plt.bar(x + width, verify_times, width, label='Verification', color='firebrick')
        
        # Add labels and title
        plt.title("Signature Scheme Performance Comparison", fontsize=16)
        plt.xlabel("Signature Scheme", fontsize=12)
        plt.ylabel("Time (seconds)", fontsize=12)
        plt.xticks(x, schemes, rotation=45, ha='right')
        plt.yscale('log')
        plt.legend()
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "graphs", "signature_performance.png"), dpi=300)
        plt.close()
    
    def _create_size_comparison_chart(self):
        """Create charts comparing key and signature sizes."""
        if not self.results["signature_performance"]:
            print("No signature size data available for visualization.")
            return
        
        # Extract data
        schemes = []
        private_key_sizes = []
        public_key_sizes = []
        signature_sizes = []
        
        # Process Lamport results
        for algo, data in self.results["signature_performance"]["lamport"].items():
            schemes.append(f"Lamport-{algo}")
            private_key_sizes.append(data["private_key_size"] / 1024)  # Convert to KB
            public_key_sizes.append(data["public_key_size"] / 1024)
            signature_sizes.append(data["signature_size"] / 1024)
        
        # Process SPHINCS+ results
        for variant, data in self.results["signature_performance"]["sphincs"].items():
            schemes.append(f"SPHINCS+-{variant}")
            private_key_sizes.append(data["private_key_size"] / 1024)
            public_key_sizes.append(data["public_key_size"] / 1024)
            signature_sizes.append(data["signature_size"] / 1024)
        
        # Process Dilithium results
        for variant, data in self.results["signature_performance"]["dilithium"].items():
            schemes.append(f"Dilithium-{variant}")
            private_key_sizes.append(data["private_key_size"] / 1024)
            public_key_sizes.append(data["public_key_size"] / 1024)
            signature_sizes.append(data["signature_size"] / 1024)
        
        # Process Kyber results for completeness
        kyber_schemes = []
        kyber_private_sizes = []
        kyber_public_sizes = []
        kyber_ciphertext_sizes = []
        
        for variant, data in self.results["signature_performance"]["kyber"].items():
            kyber_schemes.append(f"Kyber-{variant}")
            kyber_private_sizes.append(data["private_key_size"] / 1024)
            kyber_public_sizes.append(data["public_key_size"] / 1024)
            kyber_ciphertext_sizes.append(data["ciphertext_size"] / 1024)
        
        # Create grouped bar chart for signature schemes
        plt.figure(figsize=(14, 8))
        
        # Set position of bars on X axis
        x = np.arange(len(schemes))
        width = 0.25
        
        # Create bars
        plt.bar(x - width, private_key_sizes, width, label='Private Key', color='darkblue')
        plt.bar(x, public_key_sizes, width, label='Public Key', color='royalblue')
        plt.bar(x + width, signature_sizes, width, label='Signature', color='skyblue')
        
        # Add labels and title
        plt.title("Signature Scheme Size Comparison", fontsize=16)
        plt.xlabel("Signature Scheme", fontsize=12)
        plt.ylabel("Size (KB)", fontsize=12)
        plt.xticks(x, schemes, rotation=45, ha='right')
        plt.yscale('log')
        plt.legend()
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "graphs", "signature_size_comparison.png"), dpi=300)
        plt.close()
        
        # Create bar chart for Kyber
        if kyber_schemes:
            plt.figure(figsize=(10, 6))
            
            # Set position of bars on X axis
            x = np.arange(len(kyber_schemes))
            width = 0.25
            
            # Create bars
            plt.bar(x - width, kyber_private_sizes, width, label='Private Key', color='darkgreen')
            plt.bar(x, kyber_public_sizes, width, label='Public Key', color='limegreen')
            plt.bar(x + width, kyber_ciphertext_sizes, width, label='Ciphertext', color='lightgreen')
            
            # Add labels and title
            plt.title("Kyber KEM Size Comparison", fontsize=16)
            plt.xlabel("Kyber Variant", fontsize=12)
            plt.ylabel("Size (KB)", fontsize=12)
            plt.xticks(x, kyber_schemes)
            plt.legend()
            
            # Save the figure
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "graphs", "kyber_size_comparison.png"), dpi=300)
            plt.close()
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run all benchmarks and generate visualizations."""
        print("=" * 80)
        print(" DIRAC HASHES COMPREHENSIVE BENCHMARK")
        print("=" * 80)
        print("Starting benchmark suite...\n")
        
        # Run all benchmarks
        self.run_hash_speed_benchmark()
        self.run_security_benchmark()
        self.run_signature_benchmark()
        
        # Create visualizations
        self.create_visualizations()
        
        # Save results to JSON file
        with open(os.path.join(self.output_dir, "benchmark_results.json"), "w") as f:
            json.dump(self.results, f, indent=2)
        
        print("\nBenchmark complete! Results saved to:", self.output_dir)
        print("Generated visualizations can be found in:", os.path.join(self.output_dir, "graphs"))
        
        return self.results


def main():
    """Run the benchmark suite."""
    benchmark = Benchmark()
    benchmark.run_full_benchmark()


if __name__ == "__main__":
    main() 