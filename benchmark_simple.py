#!/usr/bin/env python3
"""
Simplified Hash Function Benchmarking and Security Analysis

This script benchmarks our quantum-inspired hash functions against SHA-256
and performs security analysis on the hash outputs without external dependencies.
"""

import hashlib
import time
import random
import binascii
import statistics
from collections import Counter
from typing import List, Dict, Callable, Any, Tuple

from src.quantum_hash.dirac import DiracHash


def generate_test_data(sizes: List[int]) -> Dict[int, bytes]:
    """Generate test data of various sizes."""
    result = {}
    for size in sizes:
        result[size] = random.getrandbits(size * 8).to_bytes(size, byteorder='big')
    return result


def benchmark_speed(hash_funcs: Dict[str, Callable], test_data: Dict[int, bytes], 
                   iterations: int = 5) -> Dict[str, Dict[int, float]]:
    """Benchmark the speed of different hash functions."""
    results = {name: {} for name in hash_funcs}
    
    for size, data in test_data.items():
        for name, func in hash_funcs.items():
            times = []
            for _ in range(iterations):
                start_time = time.time()
                _ = func(data)
                elapsed = time.time() - start_time
                times.append(elapsed)
            
            # Use median to minimize impact of outliers
            results[name][size] = statistics.median(times)
    
    return results


def calculate_avalanche_effect(hash_funcs: Dict[str, Callable], 
                              samples: int = 100, 
                              data_size: int = 32) -> Dict[str, float]:
    """Calculate the avalanche effect for different hash functions."""
    results = {}
    
    for name, func in hash_funcs.items():
        total_diff_bits = 0
        total_bits = 0
        
        for _ in range(samples):
            # Generate random data
            data1 = random.getrandbits(data_size * 8).to_bytes(data_size, byteorder='big')
            
            # Flip a random bit
            bit_pos = random.randint(0, data_size * 8 - 1)
            byte_pos = bit_pos // 8
            bit_in_byte = bit_pos % 8
            
            # Create a copy with one bit flipped
            data_bytes = bytearray(data1)
            data_bytes[byte_pos] ^= (1 << bit_in_byte)
            data2 = bytes(data_bytes)
            
            # Hash both data
            hash1 = func(data1)
            hash2 = func(data2)
            
            # Count bit differences
            xor_result = bytes(a ^ b for a, b in zip(hash1, hash2))
            diff_bits = bin(int.from_bytes(xor_result, byteorder='big')).count('1')
            
            total_diff_bits += diff_bits
            total_bits += len(hash1) * 8
        
        # Calculate average percentage of bits changed
        results[name] = (total_diff_bits / total_bits) * 100
    
    return results


def analyze_distribution(hash_funcs: Dict[str, Callable], 
                        samples: int = 100, 
                        data_size: int = 32) -> Dict[str, Dict[str, float]]:
    """Analyze the distribution of hash output values."""
    results = {}
    
    for name, func in hash_funcs.items():
        byte_counts = [Counter() for _ in range(32)]  # Assuming a 32-byte digest
        
        for _ in range(samples):
            # Generate random data
            data = random.getrandbits(data_size * 8).to_bytes(data_size, byteorder='big')
            
            # Hash the data
            hash_value = func(data)
            
            # Count occurrences of each byte value
            for i, byte in enumerate(hash_value):
                if i < 32:
                    byte_counts[i][byte] += 1
        
        # Calculate chi-square statistic for uniformity
        chi_square = 0
        expected = samples / 256  # Expect each byte value to occur with equal frequency
        
        for counter in byte_counts:
            for count in counter.values():
                chi_square += ((count - expected) ** 2) / expected
        
        # Calculate entropy metric (simple measure of byte distribution)
        entropy = 0
        for counter in byte_counts:
            # Count how many different values appeared at this position
            distinct_values = len(counter)
            # A simple entropy metric - ratio of distinct values to possible values (256)
            entropy += distinct_values / 256
        
        # Normalize entropy
        entropy = entropy / 32
        
        results[name] = {
            'chi_square': chi_square / 32,  # Average chi-square per byte position
            'entropy': entropy,
        }
    
    return results


def collision_test(hash_funcs: Dict[str, Callable], 
                  samples: int = 1000, 
                  reduced_bits: int = 24) -> Dict[str, float]:
    """
    Test for collisions using a reduced-bit output.
    
    This is not a full collision test (which would be infeasible), but gives
    an indication of collision behavior with truncated hashes.
    """
    results = {}
    
    for name, func in hash_funcs.items():
        seen = set()
        collisions = 0
        
        for i in range(samples):
            # Generate random data
            data = f"test_collision_{i}_{random.random()}".encode()
            
            # Hash and truncate to reduced_bits
            full_hash = func(data)
            truncated = int.from_bytes(full_hash, byteorder='big') & ((1 << reduced_bits) - 1)
            
            # Check if we've seen this truncated hash before
            if truncated in seen:
                collisions += 1
            else:
                seen.add(truncated)
        
        # Calculate collision rate
        results[name] = collisions / samples
    
    return results


def print_results(speed_results: Dict[str, Dict[int, float]], 
                 avalanche_results: Dict[str, float],
                 distribution_results: Dict[str, Dict[str, float]],
                 collision_results: Dict[str, float]) -> None:
    """Print the benchmark results in a formatted way."""
    print("\n===== HASH FUNCTION BENCHMARK RESULTS =====\n")
    
    # Print speed results
    print("SPEED BENCHMARK (seconds)")
    print("-" * 90)
    headers = ["Size (bytes)"] + list(speed_results.keys())
    print("{:<15} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}".format(*headers))
    print("-" * 90)
    
    for size in sorted(next(iter(speed_results.values())).keys()):
        row = [size]
        for name in speed_results.keys():
            row.append(f"{speed_results[name][size]:.6f}")
        print("{:<15} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}".format(*row))
    
    # Print avalanche effect results
    print("\nAVALANCHE EFFECT (% of bits changed)")
    print("-" * 90)
    for name, value in avalanche_results.items():
        print(f"{name:<15}: {value:.2f}% (ideal: 50%)")
    
    # Print distribution analysis results
    print("\nDISTRIBUTION ANALYSIS")
    print("-" * 90)
    for name, metrics in distribution_results.items():
        print(f"{name}:")
        print(f"    Chi-square: {metrics['chi_square']:.2f} (lower is better)")
        print(f"    Entropy:    {metrics['entropy']:.6f} (closer to 1.0 is better)")
    
    # Print collision test results
    print("\nCOLLISION TEST (reduced output bits)")
    print("-" * 90)
    for name, value in collision_results.items():
        print(f"{name:<15}: {value:.6f} collisions per sample")


def main():
    """Main function to run benchmarks."""
    # Define hash functions to benchmark
    hash_funcs = {
        'SHA-256': lambda data: hashlib.sha256(data).digest(),
        'Grover': lambda data: DiracHash.hash(data, algorithm='grover'),
        'Shor': lambda data: DiracHash.hash(data, algorithm='shor'),
        'Hybrid': lambda data: DiracHash.hash(data, algorithm='hybrid'),
        'Improved-G': lambda data: DiracHash.hash(data, algorithm='improved_grover'),
        'Improved-S': lambda data: DiracHash.hash(data, algorithm='improved_shor'),
        'Improved': lambda data: DiracHash.hash(data, algorithm='improved'),
    }
    
    # Data sizes for speed benchmark (in bytes)
    sizes = [16, 64, 256, 1024]
    
    # Generate test data
    print("Generating test data...")
    test_data = generate_test_data(sizes)
    
    # Benchmark speed
    print("Benchmarking hash function speed...")
    speed_results = benchmark_speed(hash_funcs, test_data)
    
    # Calculate avalanche effect
    print("Calculating avalanche effect...")
    avalanche_results = calculate_avalanche_effect(hash_funcs)
    
    # Analyze distribution
    print("Analyzing hash distribution...")
    distribution_results = analyze_distribution(hash_funcs)
    
    # Test for collisions
    print("Testing for collisions...")
    collision_results = collision_test(hash_funcs)
    
    # Print results
    print_results(speed_results, avalanche_results, distribution_results, collision_results)


if __name__ == "__main__":
    main() 