#!/usr/bin/env python3
"""
Benchmark comparing quantum-inspired hash functions with standard cryptographic hash functions.

This script benchmarks our quantum-inspired hash functions against standard
cryptographic hash functions like SHA-256, SHA-3, BLAKE2, etc.
"""

import hashlib
import time
import random
import statistics
from collections import Counter
from typing import List, Dict, Callable, Any, Tuple
import platform
import os
import sys

from src.quantum_hash.dirac import DiracHash

# Check for optional dependencies
try:
    import blake3  # Install with: pip install blake3
    HAVE_BLAKE3 = True
except ImportError:
    HAVE_BLAKE3 = False


def generate_test_data(sizes: List[int], count: int = 5) -> Dict[int, List[bytes]]:
    """Generate random test data of various sizes."""
    result = {}
    for size in sizes:
        samples = []
        for _ in range(count):
            samples.append(random.getrandbits(size * 8).to_bytes(size, byteorder='big'))
        result[size] = samples
    return result


def benchmark_speed(hash_funcs: Dict[str, Callable], test_data: Dict[int, List[bytes]], 
                   iterations: int = 3) -> Dict[str, Dict[int, float]]:
    """Benchmark the speed of different hash functions."""
    results = {name: {} for name in hash_funcs}
    
    for size, data_samples in test_data.items():
        for name, func in hash_funcs.items():
            times = []
            
            for data in data_samples:
                # Run multiple iterations for more reliable results
                iteration_times = []
                for _ in range(iterations):
                    start_time = time.time()
                    _ = func(data)
                    elapsed = time.time() - start_time
                    iteration_times.append(elapsed)
                
                # Use median time from iterations
                times.append(statistics.median(iteration_times))
            
            # Use median across all samples
            results[name][size] = statistics.median(times)
    
    return results


def calculate_throughput(speed_results: Dict[str, Dict[int, float]], 
                        sizes: List[int]) -> Dict[str, Dict[int, float]]:
    """Calculate throughput in MB/s for each hash function and input size."""
    throughput = {name: {} for name in speed_results}
    
    for name, size_times in speed_results.items():
        for size in sizes:
            time_sec = size_times[size]
            if time_sec > 0:
                mb_per_sec = (size / (1024 * 1024)) / time_sec
                throughput[name][size] = mb_per_sec
            else:
                throughput[name][size] = float('inf')
    
    return throughput


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


def print_system_info():
    """Print system information."""
    print("System Information:")
    print(f"Python Version: {platform.python_version()}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Processor: {platform.processor()}")
    
    # Try to get CPU information on Linux
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        print(f"CPU: {line.split(':')[1].strip()}")
                        break
        except:
            pass
    
    print(f"BLAKE3 Available: {HAVE_BLAKE3}")
    print(f"Optimized Hash Functions Available: {DiracHash.optimized_available()}")
    print()


def print_speed_results(sizes: List[int], speed_results: Dict[str, Dict[int, float]], 
                       throughput_results: Dict[str, Dict[int, float]]):
    """Print the speed benchmark results in a formatted table."""
    # Get maximum function name length for formatting
    max_name_len = max(len(name) for name in speed_results.keys())
    
    # Print header
    header = f"{'Hash Function':{max_name_len}}"
    for size in sizes:
        header += f" | {size:7d} bytes (ms)"
    for size in sizes:
        header += f" | {size:7d} bytes (MB/s)"
    
    print("Speed Benchmark Results:")
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    
    # Print each row
    for name in sorted(speed_results.keys()):
        row = f"{name:{max_name_len}}"
        # Add time in milliseconds
        for size in sizes:
            row += f" | {speed_results[name][size] * 1000:15.2f}"
        # Add throughput in MB/s
        for size in sizes:
            row += f" | {throughput_results[name][size]:15.2f}"
        print(row)
    
    print("-" * len(header))
    print()


def print_avalanche_results(avalanche_results: Dict[str, float]):
    """Print the avalanche effect results in a formatted table."""
    # Get maximum function name length for formatting
    max_name_len = max(len(name) for name in avalanche_results.keys())
    
    # Sort by deviation from ideal (50%)
    sorted_results = sorted(
        avalanche_results.items(), 
        key=lambda x: abs(x[1] - 50.0)
    )
    
    print("Avalanche Effect Results (ideal is 50%):")
    print("-" * (max_name_len + 40))
    print(f"{'Hash Function':{max_name_len}} | {'Avalanche Effect (%)':20} | {'Deviation from Ideal':20}")
    print("-" * (max_name_len + 40))
    
    for name, value in sorted_results:
        deviation = abs(value - 50.0)
        print(f"{name:{max_name_len}} | {value:20.2f} | {deviation:20.2f}")
    
    print("-" * (max_name_len + 40))
    print()


def main():
    """Main function to run benchmarks."""
    print("===== Hash Function Comparison Benchmark =====\n")
    print_system_info()
    
    # Define standard cryptographic hash functions
    std_hash_funcs = {
        'SHA-256': lambda data: hashlib.sha256(data).digest(),
        'SHA-384': lambda data: hashlib.sha384(data).digest(),
        'SHA-512': lambda data: hashlib.sha512(data).digest(),
        'SHA3-256': lambda data: hashlib.sha3_256(data).digest(),
        'SHA3-512': lambda data: hashlib.sha3_512(data).digest(),
        'BLAKE2b': lambda data: hashlib.blake2b(data).digest(),
        'BLAKE2s': lambda data: hashlib.blake2s(data).digest(),
    }
    
    # Add BLAKE3 if available
    if HAVE_BLAKE3:
        std_hash_funcs['BLAKE3'] = lambda data: blake3.blake3(data).digest()
    
    # Define our quantum-inspired hash functions
    quantum_hash_funcs = {
        'Grover': lambda data: DiracHash.hash(data, algorithm='grover'),
        'Shor': lambda data: DiracHash.hash(data, algorithm='shor'),
        'Hybrid': lambda data: DiracHash.hash(data, algorithm='hybrid'),
        'Improved-Grover': lambda data: DiracHash.hash(data, algorithm='improved_grover'),
        'Improved-Shor': lambda data: DiracHash.hash(data, algorithm='improved_shor'),
        'Improved': lambda data: DiracHash.hash(data, algorithm='improved'),
    }
    
    # If optimized is available, add those as well
    if DiracHash.optimized_available():
        quantum_hash_funcs.update({
            'Opt-Grover': lambda data: DiracHash.hash(data, algorithm='improved_grover', optimized=True),
            'Opt-Shor': lambda data: DiracHash.hash(data, algorithm='improved_shor', optimized=True),
            'Opt-Hybrid': lambda data: DiracHash.hash(data, algorithm='improved', optimized=True),
        })
    
    # Combine all hash functions
    all_hash_funcs = {**std_hash_funcs, **quantum_hash_funcs}
    
    # Data sizes for speed benchmark (in bytes)
    sizes = [16, 64, 256, 1024, 4096, 16384]
    
    # Generate test data
    print("Generating test data...")
    test_data = generate_test_data(sizes)
    
    # Benchmark speed
    print("Benchmarking hash function speed...")
    speed_results = benchmark_speed(all_hash_funcs, test_data)
    
    # Calculate throughput
    throughput_results = calculate_throughput(speed_results, sizes)
    
    # Print speed benchmark results
    print_speed_results(sizes, speed_results, throughput_results)
    
    # Calculate avalanche effect
    print("Calculating avalanche effect...")
    avalanche_results = calculate_avalanche_effect(all_hash_funcs)
    
    # Print avalanche effect results
    print_avalanche_results(avalanche_results)
    
    print("Benchmark completed.")


if __name__ == "__main__":
    main() 