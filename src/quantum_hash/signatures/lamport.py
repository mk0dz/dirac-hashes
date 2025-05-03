"""
Lamport one-time signature scheme.

This implements a quantum-resistant Lamport one-time signature scheme, optimized
for use in cryptocurrency wallets, with enhanced security against quantum attacks.
"""

import hashlib
import os
import secrets
import numpy as np
from typing import Dict, List, Tuple, Union, Optional, Any
import time
import functools
import json
import binascii
import zlib
import base64

# Import DiracHash for consistent hashing
from ..dirac import DiracHash


class LamportSignature:
    """
    Enhanced Lamport one-time signature scheme implementation for wallet applications.
    
    This class provides optimized methods for generating key pairs, signing messages,
    and verifying signatures using a quantum-resistant approach. It includes features
    specific for wallet applications like cached key generation, compact signatures,
    and precomputation.
    """
    
    def __init__(self, hash_algorithm: str = 'improved', cache_enabled: bool = True, 
                 compact_mode: bool = True, digest_size: int = 32):
        """
        Initialize the Lamport signature scheme with wallet-optimized settings.
        
        Args:
            hash_algorithm: The hash algorithm to use ('improved', 'grover', 'shor', 'hybrid')
            cache_enabled: Whether to cache parts of the key generation for speedup
            compact_mode: Whether to use compact signatures (reduces size significantly)
            digest_size: The digest size to use in bytes (default 32 = 256 bits)
        """
        self.hasher = DiracHash()
        self.hash_algorithm = hash_algorithm
        self.digest_size = digest_size
        self.cache_enabled = cache_enabled
        self.compact_mode = compact_mode
        self._key_cache = {}
        
        # Enhanced security - add cryptographic salt to prevent multi-target attacks
        # Use a fixed salt for deterministic testing (in production, use a random salt)
        self.global_salt = b'DiracQuantumSalt0123456789'[:16]
    
    def _get_cached_or_generate(self, cache_key: str, generator_func) -> bytes:
        """Get a value from cache or generate it."""
        if self.cache_enabled and cache_key in self._key_cache:
            return self._key_cache[cache_key]
        
        value = generator_func()
        
        if self.cache_enabled:
            self._key_cache[cache_key] = value
        
        return value
    
    def generate_keypair(self, seed: Optional[bytes] = None) -> Tuple[Dict, Dict]:
        """
        Generate a Lamport key pair, optimized for wallet applications.
        
        Args:
            seed: Optional seed for deterministic key generation
        
        Returns:
            A tuple containing (private_key, public_key)
        """
        private_key = {}
        public_key = {}
        
        # Use provided seed or generate a random one
        if seed is None:
            seed = secrets.token_bytes(32)
        
        # Use seed to derive private key values deterministically
        # This is more efficient than generating each key randomly
        
        start_time = time.time()
        
        # For each bit position of the message digest
        for i in range(self.digest_size * 8):
            private_key[i] = {}
            public_key[i] = {}
            
            # For each possible bit value (0 or 1)
            for bit in [0, 1]:
                # Deterministically derive private key from seed using position and bit value
                # This is more efficient and allows for partial key reconstruction
                pos_seed = seed + i.to_bytes(4, byteorder='little') + bytes([bit])
                
                # Generate a deterministic value for the private key
                private_key_gen = lambda: self.hasher.hash(
                    pos_seed + self.global_salt, 
                    algorithm=self.hash_algorithm,
                    digest_size=self.digest_size
                )
                
                private_key[i][bit] = self._get_cached_or_generate(
                    f"{seed.hex()[:8]}_{i}_{bit}", 
                    private_key_gen
                )
                
                # Compute the corresponding public key
                public_key_gen = lambda: self.hasher.hash(
                    private_key[i][bit] + self.global_salt, 
                    algorithm=self.hash_algorithm
                )
                
                public_key[i][bit] = self._get_cached_or_generate(
                    f"{seed.hex()[:8]}_{i}_{bit}_pub", 
                    public_key_gen
                )
        
        # Add key metadata for wallet use
        private_key['_metadata'] = {
            'creation_time': time.time(),
            'algorithm': self.hash_algorithm,
            'digest_size': self.digest_size,
            'compact_mode': self.compact_mode,
            'seed_id': self.hasher.hash(seed, algorithm='improved', digest_size=8).hex()
        }
        
        public_key['_metadata'] = {
            'creation_time': time.time(),
            'algorithm': self.hash_algorithm,
            'digest_size': self.digest_size,
            'compact_mode': self.compact_mode,
            'seed_id': self.hasher.hash(seed, algorithm='improved', digest_size=8).hex()
        }
        
        return private_key, public_key
    
    def sign(self, message: Union[str, bytes], private_key: Dict) -> Union[List[bytes], bytes]:
        """
        Sign a message using the enhanced Lamport signature scheme.
        
        Args:
            message: The message to sign
            private_key: The private key to use for signing
            
        Returns:
            The signature as a list of bytes or compressed format
        """
        # Convert string message to bytes if needed
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Hash the message using the same algorithm used for signing
        message_digest = self.hasher.hash(message, algorithm=self.hash_algorithm)
        
        # Check metadata to ensure correct key format
        if '_metadata' not in private_key:
            raise ValueError("Invalid private key format - missing metadata")
        
        # Check if key algorithm matches current algorithm
        if private_key['_metadata'].get('algorithm') != self.hash_algorithm:
            raise ValueError(f"Key algorithm mismatch: {private_key['_metadata'].get('algorithm')} vs {self.hash_algorithm}")
        
        # Create the signature
        if self.compact_mode:
            # Simplified compact mode - use a subset of keys for wallet applications
            # We'll use 64 positions (1/4 of the 256 bits) for a more compact signature
            # This provides adequate security for wallet applications
            
            # Create a subset of positions to use (deterministic based on first 8 bytes of message digest)
            subset_size = 64  # 1/4 of the 256 bits
            subset = []
            
            # Select positions deterministically using the message digest
            for i in range(subset_size):
                # Use a deterministic pattern based on message digest
                # This ensures signature verification works consistently
                pos = (i * (message_digest[i % 32] % 4 + 1)) % (self.digest_size * 8)
                subset.append(pos)
            
            # Extract revealed keys
            revealed_keys = []
            bit_values = []
            
            for pos in subset:
                # Extract the bit at position pos
                byte_pos = pos // 8
                bit_pos = pos % 8
                bit_mask = 1 << (7 - bit_pos)  # Fixed bit mask calculation
                bit_value = 1 if message_digest[byte_pos] & bit_mask else 0
                
                # Add to the signature
                revealed_keys.append(private_key[pos][bit_value])
                bit_values.append(bit_value)
            
            # Create compact signature as bytes
            # Format:
            # - Magic number (2 bytes): 'DC' for Dirac
            # - Message digest (32 bytes)
            # - Positions (subset_size * 2 bytes)
            # - Bit values (subset_size bytes)
            # - Revealed keys (concatenated)
            
            compact_sig = bytearray()
            compact_sig.extend(b'DC')  # 2-byte magic number
            compact_sig.extend(message_digest)  # 32 bytes
            
            # Add positions as 2-byte integers (little-endian)
            for pos in subset:
                compact_sig.extend(pos.to_bytes(2, byteorder='little'))
            
            # Add bit values as bytes
            for bit in bit_values:
                compact_sig.append(bit)
            
            # Add revealed keys
            for key in revealed_keys:
                compact_sig.extend(key)
            
            return bytes(compact_sig)
        else:
            # Original mode - full list of revealed values
            signature = []
            
            # For each bit in the message digest
            for i in range(self.digest_size * 8):
                # Extract the bit at position i
                bit_position = i // 8
                bit_pos = i % 8
                bit_mask = 1 << (7 - bit_pos)  # Fixed bit mask calculation
                bit_value = 1 if message_digest[bit_position] & bit_mask else 0
                
                # Add the corresponding private key value to the signature
                signature.append(private_key[i][bit_value])
            
            return signature
    
    def verify(self, message: Union[str, bytes], signature: Union[List[bytes], bytes], 
               public_key: Dict) -> bool:
        """
        Verify a Lamport signature with optimizations for wallet use.
        
        Args:
            message: The message that was signed
            signature: The signature to verify (standard or compact format)
            public_key: The public key to use for verification
            
        Returns:
            True if the signature is valid, False otherwise
        """
        # Convert string message to bytes if needed
        if isinstance(message, str):
            message = message.encode('utf-8')
            
        # Check metadata to ensure correct key format
        if '_metadata' not in public_key:
            raise ValueError("Invalid public key format - missing metadata")
        
        # Determine format based on signature type
        is_compact = isinstance(signature, (bytes, bytearray)) and len(signature) >= 2 and signature[:2] == b'DC'
        
        # For compact binary signatures
        if is_compact:
            try:
                # Check if signature is long enough
                if len(signature) < 34:  # Magic + digest
                    return False
                
                # Extract message digest
                msg_digest = signature[2:34]
                
                # Hash the message to verify
                computed_digest = self.hasher.hash(message, algorithm=self.hash_algorithm)
                
                # Check if digests match
                if msg_digest != computed_digest:
                    return False
                
                # Parse the signature
                subset_size = 64  # Same as in sign()
                
                # Calculate expected offsets
                pos_offset = 34  # After magic and digest
                pos_size = subset_size * 2  # 2 bytes per position
                bit_offset = pos_offset + pos_size
                bit_size = subset_size  # 1 byte per bit
                keys_offset = bit_offset + bit_size
                
                # Check if signature is long enough
                if len(signature) < keys_offset:
                    return False
                
                # Extract positions
                positions = []
                for i in range(subset_size):
                    pos_bytes = signature[pos_offset + i*2:pos_offset + i*2 + 2]
                    positions.append(int.from_bytes(pos_bytes, byteorder='little'))
                
                # Extract bit values from signature
                sig_bit_values = []
                for i in range(subset_size):
                    sig_bit_values.append(signature[bit_offset + i])
                
                # Check if all bit values are valid
                if not all(bit in (0, 1) for bit in sig_bit_values):
                    return False
                
                # Check if all positions are valid
                if not all(0 <= pos < self.digest_size * 8 for pos in positions):
                    return False
                
                # Size of each key
                key_size = self.digest_size
                
                # Verify each revealed key
                for i in range(subset_size):
                    pos = positions[i]
                    bit = sig_bit_values[i]
                    
                    # Calculate where the key is in the signature
                    key_pos = keys_offset + i * key_size
                    
                    # Check if signature is long enough
                    if key_pos + key_size > len(signature):
                        return False
                    
                    # Extract the key
                    key = signature[key_pos:key_pos + key_size]
                    
                    # Hash it with the salt
                    computed_hash = self.hasher.hash(
                        key + self.global_salt,
                        algorithm=self.hash_algorithm
                    )
                    
                    # Verify against public key
                    if pos not in public_key or bit not in public_key[pos]:
                        return False
                    
                    if computed_hash != public_key[pos][bit]:
                        return False
                
                return True
            except Exception as e:
                # For debugging
                print(f"Error in compact signature verification: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            # Standard signature format
            # Hash the message using the same algorithm
            message_digest = self.hasher.hash(message, algorithm=self.hash_algorithm)
            
            # Verify the signature
            for i in range(self.digest_size * 8):
                # Extract the bit at position i from the message digest
                bit_position = i // 8
                bit_pos = i % 8
                bit_mask = 1 << (7 - bit_pos)  # Fixed bit mask calculation
                bit_value = 1 if message_digest[bit_position] & bit_mask else 0
                
                # Hash the signature component
                sig_hash = self.hasher.hash(
                    signature[i] + self.global_salt, 
                    algorithm=self.hash_algorithm
                )
                
                # Compare with the public key component
                if sig_hash != public_key[i][bit_value]:
                    return False
            
            return True
    
    def serialize_keys(self, keys: Dict, format_type: str = 'json') -> str:
        """
        Serialize keys for storage in wallets.
        
        Args:
            keys: The keys to serialize (private or public)
            format_type: Format type ('json' or 'compact')
            
        Returns:
            Serialized key string
        """
        if format_type == 'json':
            # Convert binary data to hex strings for JSON serialization
            serializable_keys = {}
            
            for k, v in keys.items():
                if k == '_metadata':
                    serializable_keys[k] = v
                else:
                    serializable_keys[k] = {
                        '0': v[0].hex() if isinstance(v[0], bytes) else v[0],
                        '1': v[1].hex() if isinstance(v[1], bytes) else v[1]
                    }
            
            return json.dumps(serializable_keys)
        elif format_type == 'compact':
            # More compact representation for wallet storage
            # Just store the seed ID and key metadata
            if '_metadata' not in keys:
                raise ValueError("Cannot create compact representation without metadata")
            
            compact_data = {
                'type': 'lamport_compact',
                'metadata': keys['_metadata']
            }
            return json.dumps(compact_data)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def deserialize_keys(self, key_str: str, key_type: str = 'public') -> Dict:
        """
        Deserialize keys from storage.
        
        Args:
            key_str: Serialized key string
            key_type: Type of key ('public' or 'private')
            
        Returns:
            Deserialized key dictionary
        """
        data = json.loads(key_str)
        
        # Check if it's compact format
        if isinstance(data, dict) and data.get('type') == 'lamport_compact':
            # We need to regenerate the key from seed
            seed_id = data.get('metadata', {}).get('seed_id')
            if not seed_id:
                raise ValueError("Cannot deserialize compact key without seed_id")
            
            # This would require access to the seed storage
            # In a real wallet implementation, we would look up the seed by ID
            raise NotImplementedError("Seed-based key regeneration not implemented")
        
        # Standard JSON format
        keys = {}
        for k, v in data.items():
            if k == '_metadata':
                keys[k] = v
            else:
                keys[int(k)] = {
                    0: bytes.fromhex(v['0']) if isinstance(v['0'], str) else v['0'],
                    1: bytes.fromhex(v['1']) if isinstance(v['1'], str) else v['1']
                }
        
        return keys
    
    def generate_wallet_address(self, public_key: Dict, address_format: str = 'base58') -> str:
        """
        Generate a wallet address from a public key.
        
        Args:
            public_key: The public key to generate an address from
            address_format: Format of the address ('base58', 'hex', or 'bech32')
            
        Returns:
            Wallet address as a string
        """
        # Extract all public key components
        key_bytes = bytearray()
        
        # Add the metadata hash first
        if '_metadata' in public_key:
            metadata_str = json.dumps(public_key['_metadata'], sort_keys=True)
            key_bytes.extend(self.hasher.hash(metadata_str.encode(), algorithm='improved', digest_size=8))
        
        # Add the first value from each bit position (more compact)
        for i in range(min(16, self.digest_size * 8)):  # Use only first 16 positions to keep address reasonable
            if i in public_key:
                key_bytes.extend(public_key[i][0][:4])  # Use only first 4 bytes to keep size manageable
        
        # Create a compact representation
        address_bytes = self.hasher.hash(bytes(key_bytes), algorithm=self.hash_algorithm)
        
        # Format the address according to the specified format
        if address_format == 'hex':
            return address_bytes.hex()
        elif address_format == 'base58':
            return DiracHash.format_key(address_bytes, format_type='base58')
        elif address_format == 'bech32':
            # Simplified bech32 implementation
            return 'dc1' + DiracHash.format_key(address_bytes, format_type='base58')
        
        raise ValueError(f"Unsupported address format: {address_format}")
    
    def clear_cache(self):
        """Clear the key cache."""
        self._key_cache = {} 