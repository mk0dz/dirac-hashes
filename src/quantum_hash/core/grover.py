"""
Grover's algorithm simulation for quantum-inspired hash functions.

This module provides a classical simulation of Grover's algorithm
that can be used as part of quantum-inspired hash functions.
"""

import numpy as np
import hashlib
from typing import Callable, List, Tuple

class GroverSimulator:
    """Classical simulation of Grover's algorithm for search problems."""
    
    def __init__(self, n_qubits: int, seed=None):
        """
        Initialize the Grover simulator.
        
        Args:
            n_qubits: Number of qubits in the system
            seed: Random seed for deterministic behavior
        """
        self.n_qubits = n_qubits
        self.n_states = 2 ** n_qubits
        
        # Set random seed if provided
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize quantum state to uniform superposition
        self.state = np.ones(self.n_states) / np.sqrt(self.n_states)
    
    def mark_target(self, target_states: List[int]) -> None:
        """
        Apply phase inversion to target states (oracle function).
        
        Args:
            target_states: List of states to mark with phase inversion
        """
        for state in target_states:
            if 0 <= state < self.n_states:
                self.state[state] *= -1
    
    def diffusion(self) -> None:
        """Apply the diffusion operator (Grover's diffusion)."""
        # Compute mean amplitude
        mean = np.mean(self.state)
        
        # Apply inversion about the mean
        self.state = 2 * mean - self.state
    
    def iterate(self, target_states: List[int], iterations: int = None) -> None:
        """
        Perform Grover iterations.
        
        Args:
            target_states: List of states to search for
            iterations: Number of iterations to perform. If None, uses optimal.
        """
        # Calculate optimal number of iterations if not provided
        if iterations is None:
            m = len(target_states)
            iterations = int(np.pi/4 * np.sqrt(self.n_states / m))
        
        for _ in range(iterations):
            self.mark_target(target_states)
            self.diffusion()
    
    def measure(self) -> int:
        """
        Measure the quantum state.
        
        Returns:
            The measured state index
        """
        probabilities = np.abs(self.state) ** 2
        probabilities /= np.sum(probabilities)  # Normalize
        
        # If using a seed, return the most probable state for deterministic behavior
        if self.seed is not None:
            return np.argmax(probabilities)
        else:
            # Sample from the probability distribution
            return np.random.choice(self.n_states, p=probabilities)
    
    def reset(self) -> None:
        """Reset the state to uniform superposition."""
        self.state = np.ones(self.n_states) / np.sqrt(self.n_states)


def grover_search(n_qubits: int, target_function: Callable[[int], bool], 
                  iterations: int = None, seed=None) -> int:
    """
    Perform Grover's search algorithm.
    
    Args:
        n_qubits: Number of qubits
        target_function: Function that returns True for target states
        iterations: Number of iterations (optional)
        seed: Random seed for deterministic behavior
    
    Returns:
        The measured state after applying Grover's algorithm
    """
    # Initialize the simulator
    simulator = GroverSimulator(n_qubits, seed=seed)
    
    # Find all states that satisfy the target function
    target_states = [i for i in range(simulator.n_states) if target_function(i)]
    
    # Perform Grover iterations
    simulator.iterate(target_states, iterations)
    
    # Measure and return the result
    return simulator.measure()
    
    
def grover_hash(data: bytes, digest_size: int = 32) -> bytes:
    """
    Generate a hash using Grover-inspired amplification.
    
    This function creates a hash by using principles from Grover's algorithm
    to amplify certain bit patterns based on the input data.
    
    Args:
        data: Input data to hash
        digest_size: Size of the output hash in bytes
    
    Returns:
        Hashed output as bytes
    """
    # Add algorithm-specific identifier by prepending a byte
    # only if it's not already tagged (to avoid double tagging from improved_grover_hash)
    if not data.startswith(b'grover:'):
        data = b'grover:' + data
        
    # Make algorithm deterministic for cryptographic use
    # Generate a seed based on the data
    if len(data) == 0:
        data = b"\x00"  # Handle empty data
    
    # Use SHA-256 to generate a deterministic seed from the input data
    seed_hash = hashlib.sha256(data).digest()
    seed_value = int.from_bytes(seed_hash[:4], byteorder='little')
    
    # Convert input to numeric array
    data_array = np.frombuffer(data, dtype=np.uint8)
    
    # Calculate necessary qubits (log2 of digest_size * 8 bits)
    n_qubits = max(4, int(np.log2(digest_size * 8)) + 2)
    
    # Initialize simulator with the seed
    simulator = GroverSimulator(n_qubits, seed=seed_value)
    
    # Use chunks of input data to influence the quantum state
    chunk_size = max(1, len(data_array) // 10)
    chunks = [data_array[i:i+chunk_size] for i in range(0, len(data_array), chunk_size)]
    
    # Apply a series of operations influenced by input data
    for chunk_idx, chunk in enumerate(chunks):
        # Use sum of chunk to determine target states
        chunk_sum = np.sum(chunk) % simulator.n_states
        target_states = [(chunk_sum + i + chunk_idx) % simulator.n_states for i in range(3)]
        
        # Apply a small number of Grover iterations
        simulator.iterate(target_states, iterations=2)
    
    # Generate output by repeated measurements
    result = bytearray()
    states_needed = digest_size * 8 // n_qubits + 1
    
    for i in range(states_needed):
        # Set different seed for each measurement based on the original seed
        np.random.seed(seed_value + i)
        state = simulator.measure()
        # Convert numpy int to Python int to ensure .to_bytes works
        state_int = int(state)
        # Calculate needed bytes for n_qubits
        bytes_needed = (n_qubits + 7) // 8
        result.extend(state_int.to_bytes(bytes_needed, byteorder='big'))
        simulator.reset()
    
    # Improve avalanche effect by XORing with seed hash
    for i in range(min(len(result), len(seed_hash))):
        result[i] ^= seed_hash[i]
    
    # Final mixing to ensure good distribution and collision resistance
    # Similar approach as improved algorithms
    mixed_result = bytearray(digest_size)
    for i in range(digest_size):
        idx1 = (i + 1) % digest_size
        idx2 = (i + 7) % digest_size
        if i < len(result):
            mixed_result[i] = result[i]
        if idx1 < len(result) and idx2 < len(result):
            mixed_result[i] = (mixed_result[i] + result[idx1] * result[idx2]) % 256
    
    # Truncate to desired digest size
    return bytes(mixed_result[:digest_size]) 