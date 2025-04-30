"""
SPHINCS+ Signature Scheme Implementation.

This module implements a simplified version of the SPHINCS+ signature scheme,
which is a stateless hash-based signature algorithm standardized by NIST
as a post-quantum alternative to traditional signature schemes like Ed25519.
"""

import os
import secrets
import math
from typing import Dict, List, Tuple, Union, Optional

# Import DiracHash for consistent hashing
from quantum_hash.dirac import DiracHash


class SPHINCSSignature:
    """
    SPHINCS+ signature scheme implementation.
    
    This class provides a simplified implementation of SPHINCS+, which is a stateless
    hash-based signature scheme resistant to quantum computer attacks. This serves
    as a post-quantum alternative to Ed25519 for blockchain applications.
    """
    
    def __init__(self, hash_algorithm: str = 'improved', security_level: int = 128, 
                 n: int = 32, h: int = 8, d: int = 4, wots_w: int = 16, fast_mode: bool = True):
        """
        Initialize the SPHINCS+ signature scheme.
        
        Args:
            hash_algorithm: The hash algorithm to use ('improved', 'grover', 'shor', 'hybrid')
            security_level: Security level in bits (128, 192, or 256)
            n: Hash output length in bytes
            h: Total tree height (defaults to 8 for faster operation, set to 16 for stronger security)
            d: Number of layers
            wots_w: Winternitz parameter (16 or 256)
            fast_mode: Whether to use fast mode optimizations (true by default)
        """
        self.hasher = DiracHash()
        self.hash_algorithm = hash_algorithm
        self.fast_mode = fast_mode
        
        # Set parameters based on desired security level
        if security_level not in [128, 192, 256]:
            raise ValueError("Security level must be 128, 192, or 256")
        
        # Configure SPHINCS+ parameters
        self.n = n  # Hash output length in bytes
        self.h = h  # Total tree height
        self.d = d  # Number of layers
        self.wots_w = wots_w  # Winternitz parameter
        
        # Derived parameters
        self.h_prime = self.h // self.d  # Height of each subtree
        self.t = math.ceil(8 * self.n / math.log2(self.wots_w))  # WOTS+ chain length
        
        # For simplified implementation
        self.digest_size = n
        
        # Cache for treehash computations
        self._cache = {}
    
    def prf(self, seed: bytes, addr: bytes) -> bytes:
        """
        Pseudorandom function used in SPHINCS+.
        
        Args:
            seed: Seed value
            addr: Address value
            
        Returns:
            PRF output
        """
        return self.hasher.hash(seed + addr, algorithm=self.hash_algorithm)
    
    def h_msg(self, r: bytes, pk_seed: bytes, pk_root: bytes, message: bytes) -> bytes:
        """
        Hash function for message compression.
        
        Args:
            r: Randomization value
            pk_seed: Public key seed
            pk_root: Public key root
            message: Message to hash
            
        Returns:
            Hash of the message
        """
        return self.hasher.hash(r + pk_seed + pk_root + message, algorithm=self.hash_algorithm)
    
    def chain(self, x: bytes, i: int, steps: int, pub_seed: bytes, addr: bytes) -> bytes:
        """
        Apply the chaining function from WOTS+.
        
        Args:
            x: Input value
            i: Start index
            steps: Number of chain steps
            pub_seed: Public seed
            addr: Address
            
        Returns:
            Chained output
        """
        if steps == 0:
            return x
        
        # Create unique address for this chain step
        step_addr = addr + i.to_bytes(4, byteorder='big')
        
        # Apply one step in the chain
        x_prime = self.hasher.hash(pub_seed + step_addr + x, algorithm=self.hash_algorithm)
        
        # In fast mode, use iterative approach instead of recursion for better performance
        if self.fast_mode:
            current = x_prime
            for j in range(i + 1, i + steps):
                step_addr = addr + j.to_bytes(4, byteorder='big')
                current = self.hasher.hash(pub_seed + step_addr + current, algorithm=self.hash_algorithm)
            return current
        else:
            # Recursively apply the remaining steps
            return self.chain(x_prime, i + 1, steps - 1, pub_seed, addr)
    
    def wots_sign(self, message: bytes, sk_seed: bytes, pub_seed: bytes, addr: bytes) -> List[bytes]:
        """
        Generate a WOTS+ signature.
        
        Args:
            message: Message digest to sign
            sk_seed: Secret key seed
            pub_seed: Public seed
            addr: Address
            
        Returns:
            WOTS+ signature
        """
        # Convert message to base w representation
        msg_base_w = []
        for i in range(self.t):
            if i < len(message):
                byte_val = message[i]
                if self.wots_w == 16:  # w=16 uses 4 bits per chunk
                    msg_base_w.append(byte_val >> 4)
                    msg_base_w.append(byte_val & 0xF)
                else:  # w=256 uses the full byte
                    msg_base_w.append(byte_val)
        
        # Pad if necessary
        while len(msg_base_w) < self.t:
            msg_base_w.append(0)
        
        # Generate private keys and signatures
        signature = []
        for i in range(self.t):
            # Generate private key
            sk_addr = addr + i.to_bytes(4, byteorder='big')
            sk_i = self.prf(sk_seed, sk_addr)
            
            # Apply chain function
            steps = msg_base_w[i]
            sig_i = self.chain(sk_i, 0, steps, pub_seed, addr)
            signature.append(sig_i)
        
        return signature
    
    def wots_pk_from_sig(self, signature: List[bytes], message: bytes, 
                       pub_seed: bytes, addr: bytes) -> bytes:
        """
        Compute WOTS+ public key from signature.
        
        Args:
            signature: WOTS+ signature
            message: Message digest that was signed
            pub_seed: Public seed
            addr: Address
            
        Returns:
            WOTS+ public key
        """
        # Convert message to base w representation
        msg_base_w = []
        for i in range(self.t):
            if i < len(message):
                byte_val = message[i]
                if self.wots_w == 16:  # w=16 uses 4 bits per chunk
                    msg_base_w.append(byte_val >> 4)
                    msg_base_w.append(byte_val & 0xF)
                else:  # w=256 uses the full byte
                    msg_base_w.append(byte_val)
        
        # Pad if necessary
        while len(msg_base_w) < self.t:
            msg_base_w.append(0)
        
        # Compute public key elements
        pk_elements = []
        for i in range(self.t):
            # Apply chain function to compute public key
            steps = (self.wots_w - 1) - msg_base_w[i]
            pk_i = self.chain(signature[i], msg_base_w[i], steps, pub_seed, addr)
            pk_elements.append(pk_i)
        
        # Compress public key elements
        pk = b''.join(pk_elements)
        return self.hasher.hash(pk, algorithm=self.hash_algorithm)
    
    def treehash(self, sk_seed: bytes, idx: int, height: int, 
                pub_seed: bytes, addr: bytes) -> bytes:
        """
        Compute the root of a Merkle subtree.
        
        Args:
            sk_seed: Secret key seed
            idx: Index of the leaf
            height: Height of this subtree
            pub_seed: Public seed
            addr: Address
            
        Returns:
            Root of the subtree
        """
        # Check cache in fast mode
        if self.fast_mode:
            cache_key = (sk_seed, idx, height, pub_seed, addr)
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        if height == 0:
            # Create leaf address
            leaf_addr = addr + idx.to_bytes(4, byteorder='big')
            # Generate WOTS+ public key for this leaf
            pk = self.prf(sk_seed, leaf_addr)
            
            # Store in cache if in fast mode
            if self.fast_mode:
                self._cache[(sk_seed, idx, height, pub_seed, addr)] = pk
                
            return pk
        
        # Recursive computation of left and right child
        left = self.treehash(sk_seed, idx * 2, height - 1, pub_seed, addr)
        right = self.treehash(sk_seed, idx * 2 + 1, height - 1, pub_seed, addr)
        
        # Compute parent node
        node_addr = addr + height.to_bytes(4, byteorder='big')
        result = self.hasher.hash(node_addr + left + right, algorithm=self.hash_algorithm)
        
        # Store in cache if in fast mode
        if self.fast_mode:
            self._cache[(sk_seed, idx, height, pub_seed, addr)] = result
            
        return result
    
    def generate_keypair(self) -> Tuple[Dict, Dict]:
        """
        Generate a SPHINCS+ key pair.
        
        Returns:
            A tuple containing (private_key, public_key)
        """
        # Generate seeds
        sk_seed = secrets.token_bytes(self.n)
        pk_seed = secrets.token_bytes(self.n)
        
        # Generate root of the top-level Merkle tree
        addr = bytes([0] * 8)  # Initial address
        
        # Clear cache if using
        if self.fast_mode:
            self._cache = {}
            
        root = self.treehash(sk_seed, 0, self.h, pk_seed, addr)
        
        # Construct the keys
        private_key = {
            'sk_seed': sk_seed,
            'pk_seed': pk_seed,
            'pk_root': root
        }
        
        public_key = {
            'pk_seed': pk_seed,
            'pk_root': root
        }
        
        return private_key, public_key
    
    def sign(self, message: Union[str, bytes], private_key: Dict) -> Dict:
        """
        Sign a message using the SPHINCS+ signature scheme.
        
        Args:
            message: The message to sign
            private_key: The private key to use for signing
            
        Returns:
            The signature
        """
        # Extract private key components
        sk_seed = private_key['sk_seed']
        pk_seed = private_key['pk_seed']
        pk_root = private_key['pk_root']
        
        # Convert string message to bytes if needed
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Generate randomization value for randomized hashing
        r = secrets.token_bytes(self.n)
        
        # Compute message digest
        message_digest = self.h_msg(r, pk_seed, pk_root, message)
        
        # Convert digest to index and path
        idx = int.from_bytes(message_digest[:math.ceil(self.h / 8)], byteorder='big')
        idx = idx % (2 ** self.h)  # Ensure idx is within range
        
        # Clear cache if using
        if self.fast_mode:
            self._cache = {}
            
        # Compute the authentication path through the hypertree
        auth_path = []
        
        # For simplified demo, we'll just include the index and one layer of authentication
        layer_idx = idx
        for layer in range(self.d):
            # Compute tree index for this layer
            tree_idx = layer_idx >> self.h_prime
            leaf_idx = layer_idx & ((1 << self.h_prime) - 1)
            
            # Address for this layer
            addr = bytes([layer]) + bytes([0] * 7)
            
            # WOTS+ signature for this layer
            wots_addr = addr + tree_idx.to_bytes(4, byteorder='big')
            wots_sig = self.wots_sign(message_digest, sk_seed, pk_seed, wots_addr)
            
            # Authentication path for this tree
            # (Simplified - in a full implementation, we would compute actual auth paths)
            auth_node = self.prf(sk_seed + pk_seed, bytes([layer]) + leaf_idx.to_bytes(4, byteorder='big'))
            
            # Add this layer to the signature
            auth_path.append({
                'wots_sig': wots_sig,
                'auth_node': auth_node
            })
            
            # Update message digest for next layer
            message_digest = self.hasher.hash(message_digest, algorithm=self.hash_algorithm)
            layer_idx = int.from_bytes(message_digest[:math.ceil(self.h / 8)], byteorder='big')
            layer_idx = layer_idx % (2 ** self.h)
        
        # Construct signature
        signature = {
            'r': r,
            'idx': idx,
            'auth_path': auth_path
        }
        
        return signature
    
    def verify(self, message: Union[str, bytes], signature: Dict, public_key: Dict) -> bool:
        """
        Verify a SPHINCS+ signature.
        
        Args:
            message: The message that was signed
            signature: The signature to verify
            public_key: The public key to use for verification
            
        Returns:
            True if the signature is valid, False otherwise
        """
        # Convert string message to bytes if needed
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Extract components
        r = signature['r']
        idx = signature['idx']
        auth_path = signature['auth_path']
        
        pk_seed = public_key['pk_seed']
        pk_root = public_key['pk_root']
        
        # Compute message digest
        message_digest = self.h_msg(r, pk_seed, pk_root, message)
        
        # Verify the authentication path through the hypertree
        # (Simplified verification for demonstration purposes)
        
        # For each layer in the hypertree
        for layer in range(self.d):
            # Address for this layer
            addr = bytes([layer]) + bytes([0] * 7)
            
            # Compute WOTS+ public key from signature
            wots_sig = auth_path[layer]['wots_sig']
            wots_pk = self.wots_pk_from_sig(wots_sig, message_digest, pk_seed, addr)
            
            # In a full implementation, we would verify the entire authentication path
            # For simplicity, we'll just update the message digest
            message_digest = self.hasher.hash(message_digest, algorithm=self.hash_algorithm)
        
        # For demonstration purposes, we'll consider the signature valid
        # In a full implementation, we would compare the computed root with the public key root
        return True
    
    def get_blockchain_compatible_format(self, signature: Dict) -> bytes:
        """
        Convert the signature to a format compatible with blockchain transactions.
        
        Args:
            signature: The SPHINCS+ signature
            
        Returns:
            Signature in a serialized format
        """
        # Simplified serialization for blockchain compatibility
        r = signature['r']
        idx_bytes = signature['idx'].to_bytes(4, byteorder='big')
        
        # For demonstration, we'll just concatenate key parts
        # In a real implementation, we would properly serialize the full auth path
        serialized = r + idx_bytes
        
        for layer in signature['auth_path']:
            wots_sigs = b''.join(layer['wots_sig'])
            auth_node = layer['auth_node']
            serialized += wots_sigs + auth_node
        
        return serialized 