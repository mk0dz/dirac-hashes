"""
CRYSTALS-Kyber Key Encapsulation Mechanism Implementation.

This module implements a simplified version of the CRYSTALS-Kyber KEM scheme,
which is a lattice-based key encapsulation mechanism (KEM) standardized by NIST
as a post-quantum alternative to traditional key exchange schemes based on ECC.
"""

import os
import secrets
import numpy as np
from typing import Dict, List, Tuple, Union, Optional

from quantum_hash.dirac import DiracHash


class Kyber:
    """
    CRYSTALS-Kyber key encapsulation mechanism implementation.
    
    This class provides a simplified implementation of Kyber, which is a
    lattice-based key encapsulation mechanism resistant to quantum computer attacks.
    This serves as a post-quantum alternative to ECC for blockchain applications.
    """
    
    def __init__(self, security_level: int = 3, hash_algorithm: str = 'improved'):
        """
        Initialize the Kyber KEM.
        
        Args:
            security_level: Security level (1, 3, or 5, corresponding to 128, 192, or 256-bit security)
            hash_algorithm: The hash algorithm to use ('improved', 'grover', 'shor', 'hybrid')
        """
        self.hasher = DiracHash()
        self.hash_algorithm = hash_algorithm
        
        # Set parameters based on security level
        if security_level not in [1, 3, 5]:
            raise ValueError("Security level must be 1, 3, or 5")
        
        self.security_level = security_level
        
        # Kyber parameters
        if security_level == 1:
            self.k = 2  # K-512
            self.eta1 = 3
            self.eta2 = 2
        elif security_level == 3:
            self.k = 3  # K-768
            self.eta1 = 2
            self.eta2 = 2
        else:  # security_level == 5
            self.k = 4  # K-1024
            self.eta1 = 2
            self.eta2 = 2
        
        self.q = 3329  # Prime modulus
        self.n = 256   # Polynomial degree
        self.du = 10   # Compression parameter for ciphertext
        self.dv = 4    # Compression parameter for ciphertext
        
        # Derived parameters for our simplified implementation
        self.seed_size = 32
        self.shared_key_size = 32
    
    def sample_poly(self, seed: bytes, nonce: int = 0) -> np.ndarray:
        """
        Sample a polynomial using rejection sampling.
        
        Args:
            seed: Seed for the sampling
            nonce: Nonce value
            
        Returns:
            Sampled polynomial as numpy array
        """
        # Use the seed and nonce to generate a deterministic sample
        sample_seed = self.hasher.hash(seed + nonce.to_bytes(4, byteorder='little'), 
                                     algorithm=self.hash_algorithm)
        
        # Convert to numpy seed
        np_seed = int.from_bytes(sample_seed[:4], byteorder='little')
        np.random.seed(np_seed)
        
        # Sample coefficients with Gaussian distribution - simplified approximation
        # to the centered binomial distribution used in Kyber
        poly = np.random.normal(0, 1, self.n).round().astype(np.int16)
        
        # Reduce modulo q
        poly = np.mod(poly, self.q)
        
        return poly
    
    def poly_to_bytes(self, poly: np.ndarray) -> bytes:
        """
        Convert a polynomial to bytes.
        
        Args:
            poly: Polynomial as numpy array
            
        Returns:
            Polynomial encoded as bytes
        """
        # Simplified encoding - in a real implementation, this would use
        # compression with appropriate bit packing
        result = bytearray()
        for coeff in poly:
            # Encode each coefficient as 2 bytes (little-endian)
            result.extend(int(coeff).to_bytes(2, byteorder='little'))
        return bytes(result)
    
    def bytes_to_poly(self, data: bytes) -> np.ndarray:
        """
        Convert bytes to a polynomial.
        
        Args:
            data: Polynomial encoded as bytes
            
        Returns:
            Polynomial as numpy array
        """
        # Simplified decoding
        poly = np.zeros(self.n, dtype=np.int16)
        for i in range(min(self.n, len(data) // 2)):
            # Decode each 2-byte coefficient
            coeff = int.from_bytes(data[i*2:i*2+2], byteorder='little')
            poly[i] = coeff % self.q
        return poly
    
    def poly_mul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Multiply two polynomials in the ring Rq.
        
        Args:
            a: First polynomial
            b: Second polynomial
            
        Returns:
            Product polynomial
        """
        # This is a simplified multiplication that doesn't use NTT
        # In a real implementation, we would use Number Theoretic Transform (NTT)
        
        result = np.zeros(self.n, dtype=np.int64)  # Use int64 to prevent overflow
        
        # Schoolbook multiplication with reduction by X^n + 1
        for i in range(self.n):
            for j in range(self.n):
                idx = (i + j) % self.n
                sign = 1 if (i + j) < self.n else -1
                result[idx] += sign * int(a[i]) * int(b[j])
        
        # Reduce modulo q
        return np.mod(result, self.q).astype(np.int16)
    
    def poly_add(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Add two polynomials in the ring Rq.
        
        Args:
            a: First polynomial
            b: Second polynomial
            
        Returns:
            Sum polynomial
        """
        # Simply add coefficients and reduce modulo q
        return np.mod(a + b, self.q).astype(np.int16)
    
    def poly_sub(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Subtract two polynomials in the ring Rq.
        
        Args:
            a: First polynomial
            b: Second polynomial
            
        Returns:
            Difference polynomial
        """
        # Subtract coefficients and reduce modulo q
        return np.mod(a - b, self.q).astype(np.int16)
    
    def sample_binomial(self, seed: bytes, eta: int = None, nonce: int = 0) -> np.ndarray:
        """
        Sample a polynomial from a centered binomial distribution.
        
        Args:
            seed: Seed for the sampling
            eta: Parameter for the distribution (uses self.eta1 if None)
            nonce: Nonce value
            
        Returns:
            Sampled polynomial as numpy array
        """
        if eta is None:
            eta = self.eta1
        
        # Use the seed and nonce to generate a deterministic sample
        sample_seed = self.hasher.hash(seed + nonce.to_bytes(4, byteorder='little'), 
                                     algorithm=self.hash_algorithm)
        
        # Convert to numpy seed
        np_seed = int.from_bytes(sample_seed[:4], byteorder='little')
        np.random.seed(np_seed)
        
        # Sample coefficients with simplified binomial distribution
        # In a real implementation, we'd use a more optimized approach
        poly = np.zeros(self.n, dtype=np.int16)
        for i in range(self.n):
            a = sum(np.random.randint(0, 2) for _ in range(eta))
            b = sum(np.random.randint(0, 2) for _ in range(eta))
            poly[i] = a - b
        
        # Reduce modulo q
        return np.mod(poly, self.q)
    
    def generate_keypair(self) -> Tuple[Dict, Dict]:
        """
        Generate a Kyber key pair.
        
        Returns:
            A tuple containing (private_key, public_key)
        """
        # Generate random seed
        seed = secrets.token_bytes(self.seed_size)
        
        # Generate matrix A from seed
        A = []
        for i in range(self.k):
            row = []
            for j in range(self.k):
                nonce = i * self.k + j
                row.append(self.sample_poly(seed, nonce))
            A.append(row)
        
        # Sample secret vector s
        s = []
        for i in range(self.k):
            noise_seed = self.hasher.hash(seed + i.to_bytes(4, byteorder='little'), 
                                        algorithm=self.hash_algorithm)
            s_poly = self.sample_binomial(noise_seed, eta=self.eta1)
            s.append(s_poly)
        
        # Sample error vector e
        e = []
        for i in range(self.k):
            noise_seed = self.hasher.hash(seed + (i + self.k).to_bytes(4, byteorder='little'), 
                                        algorithm=self.hash_algorithm)
            e_poly = self.sample_binomial(noise_seed, eta=self.eta1)
            e.append(e_poly)
        
        # Compute public key t = A*s + e
        t = []
        for i in range(self.k):
            t_poly = e[i].copy()  # Start with error term
            for j in range(self.k):
                t_poly = self.poly_add(t_poly, self.poly_mul(A[i][j], s[j]))
            t.append(t_poly)
        
        # Create private and public key dictionaries with serialized polynomials
        private_key = {
            'seed': seed,
            's': [self.poly_to_bytes(poly) for poly in s]
        }
        
        public_key = {
            'seed': seed,
            't': [self.poly_to_bytes(poly) for poly in t]
        }
        
        return private_key, public_key
    
    def encapsulate(self, public_key: Dict) -> Tuple[bytes, bytes]:
        """
        Encapsulate a shared secret to the given public key.
        
        Args:
            public_key: The recipient's public key
            
        Returns:
            A tuple containing (ciphertext, shared_secret)
        """
        # Extract public key components
        seed = public_key['seed']
        t_bytes = public_key['t']
        t = [self.bytes_to_poly(poly_bytes) for poly_bytes in t_bytes]
        
        # Check if t has the expected length based on security level
        if len(t) < self.k:
            # Pad t with zeros if needed (for API compatibility)
            while len(t) < self.k:
                t.append(np.zeros(self.n, dtype=np.int16))
        elif len(t) > self.k:
            # Truncate t if too long
            t = t[:self.k]
        
        # Generate random message
        m = np.array([np.random.randint(0, 2) for _ in range(self.n)], dtype=np.int16)
        
        # Compute shared secret from message
        shared_secret = self.hasher.hash(self.poly_to_bytes(m), algorithm=self.hash_algorithm)[:self.shared_key_size]
        
        # Re-create the public matrix A
        A = []
        for i in range(self.k):
            row = []
            for j in range(self.k):
                nonce = i * self.k + j
                row.append(self.sample_poly(seed, nonce))
            A.append(row)
        
        # Sample r with binomial distribution
        r = []
        for i in range(self.k):
            r_seed = self.hasher.hash(shared_secret + i.to_bytes(4, byteorder='little'), 
                                    algorithm=self.hash_algorithm)
            r_poly = self.sample_binomial(r_seed, eta=self.eta1)
            r.append(r_poly)
        
        # Sample error vector e1
        e1 = []
        for i in range(self.k):
            e_seed = self.hasher.hash(shared_secret + (i + self.k).to_bytes(4, byteorder='little'), 
                                    algorithm=self.hash_algorithm)
            e1_poly = self.sample_binomial(e_seed, eta=self.eta2)
            e1.append(e1_poly)
        
        # Sample error e2
        e2_seed = self.hasher.hash(shared_secret + (2 * self.k).to_bytes(4, byteorder='little'), 
                                 algorithm=self.hash_algorithm)
        e2 = self.sample_binomial(e2_seed, eta=self.eta2)
        
        # Compute u = A^T * r + e1
        u = []
        for j in range(self.k):
            u_poly = e1[j].copy()
            for i in range(self.k):
                u_poly = self.poly_add(u_poly, self.poly_mul(A[i][j], r[i]))
            u.append(u_poly)
        
        # Compute v = t^T * r + e2 + ⌊q/2⌋ * m
        v = e2.copy()
        for i in range(self.k):
            v = self.poly_add(v, self.poly_mul(t[i], r[i]))
        
        # Add message encoding (q/2 * m)
        q_half = self.q // 2
        for i in range(self.n):
            v[i] = (v[i] + q_half * m[i]) % self.q
        
        # Encode u and v into ciphertext
        ciphertext = bytearray()
        for u_poly in u:
            ciphertext.extend(self.poly_to_bytes(u_poly))
        ciphertext.extend(self.poly_to_bytes(v))
        
        return bytes(ciphertext), shared_secret
    
    def decapsulate(self, ciphertext: bytes, private_key: Dict) -> bytes:
        """
        Decapsulate a shared secret from ciphertext using private key.
        
        Args:
            ciphertext: The encapsulated key
            private_key: The recipient's private key
            
        Returns:
            The shared secret
        """
        # Extract private key components
        seed = private_key['seed']
        s_bytes = private_key['s']
        s = [self.bytes_to_poly(poly_bytes) for poly_bytes in s_bytes]
        
        # Check if s has the expected length based on security level
        if len(s) < self.k:
            # Pad s with zeros if needed (for API compatibility)
            while len(s) < self.k:
                s.append(np.zeros(self.n, dtype=np.int16))
        elif len(s) > self.k:
            # Truncate s if too long
            s = s[:self.k]
        
        # Decode ciphertext to get u and v
        bytes_per_poly = self.n * 2  # 2 bytes per coefficient
        u = []
        for i in range(self.k):
            offset = i * bytes_per_poly
            u_bytes = ciphertext[offset:offset + bytes_per_poly]
            u_poly = self.bytes_to_poly(u_bytes)
            u.append(u_poly)
        
        v_bytes = ciphertext[self.k * bytes_per_poly:]
        v = self.bytes_to_poly(v_bytes)
        
        # Compute v - s^T * u
        mp = v.copy()
        for i in range(self.k):
            mp = self.poly_sub(mp, self.poly_mul(s[i], u[i]))
        
        # Decode message
        m = np.zeros(self.n, dtype=np.int16)
        q_half = self.q // 2
        q_quarter = self.q // 4
        for i in range(self.n):
            # Check if coefficient is closer to 0 or q/2
            if mp[i] > q_quarter and mp[i] < (self.q - q_quarter):
                m[i] = 1
        
        # Derive shared secret from message
        shared_secret = self.hasher.hash(self.poly_to_bytes(m), algorithm=self.hash_algorithm)[:self.shared_key_size]
        
        return shared_secret
        
    def get_blockchain_compatible_keys(self, public_key: Dict) -> bytes:
        """
        Convert the public key to a compact format suitable for blockchain storage.
        
        Args:
            public_key: The public key to convert
            
        Returns:
            Compact representation of the public key
        """
        # In a real blockchain application, we would compress this further
        result = bytearray(public_key['seed'])
        
        for t_poly in public_key['t']:
            # For blockchain storage, we could implement a more compact encoding
            result.extend(self.poly_to_bytes(t_poly))
            
        return bytes(result)

# Create an alias for backward compatibility with existing code
KyberKEM = Kyber 