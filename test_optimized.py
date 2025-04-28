#!/usr/bin/env python3
"""
Performance testing for SIMD-optimized hash functions.

This script compares the performance of our standard implementations against
the SIMD-optimized versions and verifies that they produce identical results.
"""

import time
import random
import statistics
from typing import Dict, Callable, List, Tuple

from src.quantum_hash.dirac import DiracHash
from src.quantum_hash.core.improved_hash import (
    improved_grover_hash, improved_shor_hash, improved_hybrid_hash
)

try:
    from src.quantum_hash.core.simd_optimized import (
        optimized_grover_hash, optimized_shor_hash, optimized_hybrid_hash
    )
    OPTIMIZED_AVAILABLE = True
except ImportError:
    OPTIMIZED_AVAILABLE = False


def generate_test_data(sizes: List[int], count: int = 5) -> Dict[int, List[bytes]]:
    """Generate random test data of various sizes."""
    result = {}
    for size in sizes:
        samples = []
        for _ in range(count):
            samples.append(random.getrandbits(size * 8).to_bytes(size, byteorder='big'))
        result[size] = samples
    return result


def test_correctness() -> bool:
    """
    Test that optimized and regular implementations produce identical results.
    """
    if not OPTIMIZED_AVAILABLE:
        print("Optimized implementations not available. Skipping correctness test.")
        return False
    
    print("\n===== CORRECTNESS TESTS =====")
    
    test_data = [
        b"",  # Empty
        b"a",  # Single byte
        b"abcdefghijklmnopqrstuvwxyz",  # Alpha
        b"1234567890" * 10,  # Numeric, repeated
        random.getrandbits(1024 * 8).to_bytes(1024, byteorder='big'),  # Random
    ]
    
    algorithms = [
        ('grover', improved_grover_hash, optimized_grover_hash),
        ('shor', improved_shor_hash, optimized_shor_hash),
        ('hybrid', improved_hybrid_hash, optimized_hybrid_hash),
    ]
    
    all_match = True
    
    for algo_name, standard_impl, optimized_impl in algorithms:
        print(f"\nTesting {algo_name} implementation:")
        
        for i, data in enumerate(test_data):
            # Standard implementation
            standard_result = standard_impl(data)
            
            # Optimized implementation
            optimized_result = optimized_impl(data)
            
            # Compare results
            match = standard_result == optimized_result
            all_match = all_match and match
            
            print(f"  Test {i+1}: {'MATCH' if match else 'MISMATCH'}")
            
            if not match:
                print(f"    Standard: {standard_result.hex()[:16]}...")
                print(f"    Optimized: {optimized_result.hex()[:16]}...")
    
    print(f"\nOverall result: {'ALL TESTS PASSED' if all_match else 'TESTS FAILED'}")
    return all_match


def benchmark_performance() -> None:
    """
    Benchmark the performance of standard vs. optimized implementations.
    """
    print("\n===== PERFORMANCE BENCHMARKS =====")
    
    # Data sizes to test (in bytes)
    sizes = [16, 64, 256, 1024, 4096, 16384]
    
    # Generate test data
    print("Generating test data...")
    test_data = generate_test_data(sizes)
    
    # Implementations to benchmark
    implementations = [
        ("Standard - Grover", lambda d: DiracHash.hash(d, algorithm='improved_grover', optimized=False)),
        ("Standard - Shor", lambda d: DiracHash.hash(d, algorithm='improved_shor', optimized=False)),
        ("Standard - Hybrid", lambda d: DiracHash.hash(d, algorithm='improved', optimized=False)),
    ]
    
    if OPTIMIZED_AVAILABLE:
        implementations.extend([
            ("Optimized - Grover", lambda d: DiracHash.hash(d, algorithm='improved_grover', optimized=True)),
            ("Optimized - Shor", lambda d: DiracHash.hash(d, algorithm='improved_shor', optimized=True)),
            ("Optimized - Hybrid", lambda d: DiracHash.hash(d, algorithm='improved', optimized=True)),
        ])
    
    # Number of iterations for each test
    iterations = 5
    
    # Store results
    results = {name: {} for name, _ in implementations}
    
    # Run benchmarks
    for size in sizes:
        print(f"\nBenchmarking with {size} byte inputs...")
        
        for name, func in implementations:
            times = []
            
            # Run multiple iterations
            for data in test_data[size]:
                start_time = time.time()
                _ = func(data)
                elapsed = time.time() - start_time
                times.append(elapsed)
            
            # Use median to minimize impact of outliers
            median_time = statistics.median(times)
            results[name][size] = median_time
            
            print(f"  {name}: {median_time:.6f} seconds")
    
    # Calculate speedup
    if OPTIMIZED_AVAILABLE:
        print("\n===== SPEEDUP FACTORS =====")
        for size in sizes:
            print(f"\nInput size: {size} bytes")
            for algo in ["Grover", "Shor", "Hybrid"]:
                std_time = results[f"Standard - {algo}"][size]
                opt_time = results[f"Optimized - {algo}"][size]
                speedup = std_time / opt_time if opt_time > 0 else float('inf')
                print(f"  {algo}: {speedup:.2f}x speedup")


if __name__ == "__main__":
    print("=== SIMD-Optimized Hash Function Tests ===\n")
    
    if not OPTIMIZED_AVAILABLE:
        print("Warning: SIMD-optimized implementations are not available.")
        print("Install Numba for better performance: pip install numba\n")
    
    # Test correctness
    if OPTIMIZED_AVAILABLE:
        test_correctness()
    
    # Benchmark performance
    benchmark_performance()
    
    print("\nTests completed.") 