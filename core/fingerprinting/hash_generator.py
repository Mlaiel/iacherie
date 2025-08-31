"""IA Influencer Agent - Hash Generator
Advanced hash generation utilities for fingerprinting systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""
import hashlib
import hmac
import secrets
import time
import logging
import json
import base64
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class HashResult:
    """Result of hash generation operation"""
    algorithm: str
    hash_value: str
    salt: Optional[str]
    timestamp: float
    metadata: Dict[str, Any]


class HashGenerator:
    """
    Professional hash generator providing multiple hash algorithms
    for fingerprinting, verification, and cryptographic operations
    """
    
    def __init__(self, default_salt_length: int = 32):
        """
        Initialize hash generator
        
        Args:
            default_salt_length: Default length for generated salts
        """
        self.default_salt_length = default_salt_length
        self.supported_algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512,
            'sha3_256': hashlib.sha3_256,
            'sha3_512': hashlib.sha3_512,
            'blake2b': hashlib.blake2b,
            'blake2s': hashlib.blake2s
        }
        
        # Cache for performance optimization
        self.hash_cache = {}
        self.cache_max_size = 1000
        
        logger.info(f"HashGenerator initialized with {len(self.supported_algorithms)} algorithms")
    
    def generate_secure_hash(
        self, 
        data: Union[str, bytes, Dict, List],
        algorithm: str = 'sha256',
        use_salt: bool = True,
        custom_salt: Optional[str] = None
    ) -> HashResult:
        """
        Generate secure hash with optional salting
        
        Args:
            data: Data to hash (string, bytes, or JSON-serializable object)
            algorithm: Hash algorithm to use
            use_salt: Whether to use salt for additional security
            custom_salt: Custom salt to use (generates random if None)
        
        Returns:
            HashResult with hash value and metadata
        """
        try:
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Convert data to bytes
            data_bytes = self._prepare_data(data)
            
            # Generate or use salt
            salt = None
            if use_salt:
                if custom_salt:
                    salt = custom_salt
                else:
                    salt = self._generate_salt()
                
                # Prepend salt to data
                salted_data = salt.encode() + data_bytes
            else:
                salted_data = data_bytes
            
            # Generate hash
            hash_func = self.supported_algorithms[algorithm]
            hash_obj = hash_func(salted_data)
            hash_value = hash_obj.hexdigest()
            
            result = HashResult(
                algorithm=algorithm,
                hash_value=hash_value,
                salt=salt,
                timestamp=time.time(),
                metadata={
                    'data_length': len(data_bytes),
                    'salted': use_salt,
                    'salt_length': len(salt) if salt else 0
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating secure hash: {str(e)}")
            raise
    
    def generate_fingerprint_hash(
        self, 
        fingerprint_data: Dict[str, Any],
        include_metadata: bool = True
    ) -> str:
        """
        Generate hash specifically for fingerprint data
        
        Args:
            fingerprint_data: Fingerprint data dictionary
            include_metadata: Whether to include metadata in hash
        
        Returns:
            Generated hash string
        """
        try:
            # Extract relevant data for hashing
            hash_data = {}
            
            if 'methods' in fingerprint_data:
                methods = fingerprint_data['methods']
                
                # Extract primary hashes from each method
                for method, data in methods.items():
                    if 'error' not in data:
                        method_hash = self._extract_method_hash(method, data)
                        if method_hash:
                            hash_data[method] = method_hash
            
            # Include metadata if requested
            if include_metadata:
                metadata = {
                    'file_path': fingerprint_data.get('file_path', ''),
                    'file_size': fingerprint_data.get('file_size', 0),
                    'content_type': fingerprint_data.get('manager_info', {}).get('content_type', '')
                }
                hash_data['metadata'] = metadata
            
            # Sort keys for consistent hashing
            sorted_data = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
            
            # Generate SHA-256 hash
            hash_result = self.generate_secure_hash(
                sorted_data,
                algorithm='sha256',
                use_salt=False
            )
            
            return hash_result.hash_value
            
        except Exception as e:
            logger.error(f"Error generating fingerprint hash: {str(e)}")
            raise
    
    def _extract_method_hash(self, method: str, data: Dict[str, Any]) -> Optional[str]:
        """Extract primary hash from method data"""
        try:
            # Method-specific hash extraction
            hash_fields = {
                'chromaprint': 'hash',
                'spectral_hash': 'spectral_hash',
                'mfcc': 'mfcc_hash',
                'tempo_rhythm': 'rhythm_hash',
                'perceptual_hash': ['combined_hash', 'sequence_hash'],
                'histogram': 'histogram_hash',
                'optical_flow': 'motion_hash',
                'edge_detection': 'edge_hash',
                'sift_features': 'feature_hash',
                'texture_analysis': 'texture_hash'
            }
            
            field = hash_fields.get(method)
            
            if isinstance(field, list):
                # Try multiple field names
                for f in field:
                    if f in data:
                        return data[f]
            elif field and field in data:
                return data[field]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting method hash: {str(e)}")
            return None
    
    def generate_content_hash(
        self, 
        file_path: Union[str, Path],
        chunk_size: int = 65536,
        algorithm: str = 'sha256'
    ) -> HashResult:
        """
        Generate hash of file content
        
        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read
            algorithm: Hash algorithm to use
        
        Returns:
            HashResult with file content hash
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Initialize hash function
            hash_func = self.supported_algorithms[algorithm]()
            
            # Read file in chunks and update hash
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_func.update(chunk)
            
            hash_value = hash_func.hexdigest()
            
            result = HashResult(
                algorithm=algorithm,
                hash_value=hash_value,
                salt=None,
                timestamp=time.time(),
                metadata={
                    'file_path': str(file_path),
                    'file_size': file_path.stat().st_size,
                    'chunk_size': chunk_size
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating content hash: {str(e)}")
            raise
    
    def generate_hmac(
        self, 
        data: Union[str, bytes],
        key: Union[str, bytes],
        algorithm: str = 'sha256'
    ) -> str:
        """
        Generate HMAC (Hash-based Message Authentication Code)
        
        Args:
            data: Data to authenticate
            key: Secret key for HMAC
            algorithm: Hash algorithm to use
        
        Returns:
            HMAC hex digest
        """
        try:
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Convert to bytes if necessary
            if isinstance(data, str):
                data = data.encode('utf-8')
            if isinstance(key, str):
                key = key.encode('utf-8')
            
            # Generate HMAC
            hmac_obj = hmac.new(key, data, self.supported_algorithms[algorithm])
            return hmac_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating HMAC: {str(e)}")
            raise
    
    def generate_merkle_root(self, hashes: List[str]) -> str:
        """
        Generate Merkle tree root from list of hashes
        
        Args:
            hashes: List of hash strings
        
        Returns:
            Merkle root hash
        """
        try:
            if not hashes:
                raise ValueError("Hash list cannot be empty")
            
            # Make a copy to avoid modifying original
            current_hashes = hashes.copy()
            
            # Build Merkle tree bottom-up
            while len(current_hashes) > 1:
                next_level = []
                
                # Process pairs of hashes
                for i in range(0, len(current_hashes), 2):
                    left = current_hashes[i]
                    
                    # If odd number of hashes, duplicate the last one
                    if i + 1 < len(current_hashes):
                        right = current_hashes[i + 1]
                    else:
                        right = left
                    
                    # Combine and hash
                    combined = left + right
                    parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                    next_level.append(parent_hash)
                
                current_hashes = next_level
            
            return current_hashes[0]
            
        except Exception as e:
            logger.error(f"Error generating Merkle root: {str(e)}")
            raise
    
    def generate_rolling_hash(
        self, 
        data: Union[str, bytes],
        window_size: int = 64
    ) -> List[int]:
        """
        Generate rolling hash for similarity detection
        
        Args:
            data: Data to hash
            window_size: Size of rolling window
        
        Returns:
            List of rolling hash values
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if len(data) < window_size:
                return []
            
            rolling_hashes = []
            
            # Simple polynomial rolling hash
            base = 257
            mod = 10**9 + 7
            
            # Calculate initial hash
            current_hash = 0
            base_power = 1
            
            for i in range(window_size):
                current_hash = (current_hash + data[i] * base_power) % mod
                if i < window_size - 1:
                    base_power = (base_power * base) % mod
            
            rolling_hashes.append(current_hash)
            
            # Roll the hash
            for i in range(window_size, len(data)):
                # Remove leftmost character
                current_hash = (current_hash - data[i - window_size] * base_power) % mod
                # Add rightmost character
                current_hash = (current_hash * base + data[i]) % mod
                rolling_hashes.append(current_hash)
            
            return rolling_hashes
            
        except Exception as e:
            logger.error(f"Error generating rolling hash: {str(e)}")
            raise
    
    def generate_locality_sensitive_hash(
        self, 
        features: List[float],
        num_hashes: int = 10,
        hash_length: int = 32
    ) -> List[str]:
        """
        Generate Locality Sensitive Hash for approximate similarity
        
        Args:
            features: Feature vector
            num_hashes: Number of hash functions to use
            hash_length: Length of each hash
        
        Returns:
            List of LSH hash strings
        """
        try:
            if not features:
                raise ValueError("Features list cannot be empty")
            
            features_array = np.array(features)
            dimension = len(features_array)
            
            lsh_hashes = []
            
            for i in range(num_hashes):
                # Generate random projection vector
                np.random.seed(i + 1000)  # Deterministic but different for each hash
                projection = np.random.randn(dimension)
                
                # Project features onto random vector
                projection_value = np.dot(features_array, projection)
                
                # Generate binary hash
                binary_hash = '1' if projection_value >= 0 else '0'
                
                # Extend to desired length with additional projections
                hash_bits = [binary_hash]
                
                for j in range(1, hash_length):
                    np.random.seed(i * hash_length + j + 1000)
                    sub_projection = np.random.randn(dimension)
                    sub_value = np.dot(features_array, sub_projection)
                    hash_bits.append('1' if sub_value >= 0 else '0')
                
                lsh_hash = ''.join(hash_bits)
                lsh_hashes.append(lsh_hash)
            
            return lsh_hashes
            
        except Exception as e:
            logger.error(f"Error generating LSH: {str(e)}")
            raise
    
    def verify_hash(
        self, 
        data: Union[str, bytes, Dict, List],
        hash_result: HashResult
    ) -> bool:
        """
        Verify data against hash result
        
        Args:
            data: Original data
            hash_result: Hash result to verify against
        
        Returns:
            True if hash matches, False otherwise
        """
        try:
            # Generate new hash with same parameters
            new_result = self.generate_secure_hash(
                data,
                algorithm=hash_result.algorithm,
                use_salt=hash_result.salt is not None,
                custom_salt=hash_result.salt
            )
            
            return new_result.hash_value == hash_result.hash_value
            
        except Exception as e:
            logger.error(f"Error verifying hash: {str(e)}")
            return False
    
    def calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """
        Calculate similarity between two hash strings using Hamming distance
        
        Args:
            hash1: First hash string
            hash2: Second hash string
        
        Returns:
            Similarity score between 0 and 1
        """
        try:
            if len(hash1) != len(hash2):
                return 0.0
            
            if not hash1 or not hash2:
                return 0.0
            
            # Calculate Hamming distance
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            
            # Convert to similarity (1 - normalized distance)
            max_distance = len(hash1)
            similarity = 1.0 - (hamming_distance / max_distance)
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating hash similarity: {str(e)}")
            return 0.0
    
    def batch_generate_hashes(
        self, 
        data_list: List[Union[str, bytes, Dict, List]],
        algorithm: str = 'sha256',
        use_salt: bool = False
    ) -> List[HashResult]:
        """
        Generate hashes for multiple data items in batch
        
        Args:
            data_list: List of data items to hash
            algorithm: Hash algorithm to use
            use_salt: Whether to use salt
        
        Returns:
            List of hash results
        """
        try:
            results = []
            
            for data in data_list:
                try:
                    result = self.generate_secure_hash(
                        data,
                        algorithm=algorithm,
                        use_salt=use_salt
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error hashing item in batch: {str(e)}")
                    # Add placeholder result for failed item
                    results.append(HashResult(
                        algorithm=algorithm,
                        hash_value='',
                        salt=None,
                        timestamp=time.time(),
                        metadata={'error': str(e)}
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch hash generation: {str(e)}")
            raise
    
    def _prepare_data(self, data: Union[str, bytes, Dict, List]) -> bytes:
        """Convert various data types to bytes for hashing"""
        try:
            if isinstance(data, bytes):
                return data
            elif isinstance(data, str):
                return data.encode('utf-8')
            elif isinstance(data, (dict, list)):
                # Convert to JSON string then to bytes
                json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
                return json_str.encode('utf-8')
            else:
                # Convert to string then to bytes
                return str(data).encode('utf-8')
                
        except Exception as e:
            logger.error(f"Error preparing data for hashing: {str(e)}")
            raise
    
    def _generate_salt(self, length: Optional[int] = None) -> str:
        """Generate cryptographically secure random salt"""
        try:
            salt_length = length or self.default_salt_length
            salt_bytes = secrets.token_bytes(salt_length)
            return base64.b64encode(salt_bytes).decode('ascii')
            
        except Exception as e:
            logger.error(f"Error generating salt: {str(e)}")
            raise
    
    def export_hash_result(self, hash_result: HashResult, file_path: Union[str, Path]) -> bool:
        """
        Export hash result to JSON file
        
        Args:
            hash_result: Hash result to export
            file_path: Output file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                'algorithm': hash_result.algorithm,
                'hash_value': hash_result.hash_value,
                'salt': hash_result.salt,
                'timestamp': hash_result.timestamp,
                'metadata': hash_result.metadata,
                'exported_at': time.time()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported hash result to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting hash result: {str(e)}")
            return False
    
    def import_hash_result(self, file_path: Union[str, Path]) -> Optional[HashResult]:
        """
        Import hash result from JSON file
        
        Args:
            file_path: Input file path
        
        Returns:
            HashResult if successful, None otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            result = HashResult(
                algorithm=data['algorithm'],
                hash_value=data['hash_value'],
                salt=data.get('salt'),
                timestamp=data['timestamp'],
                metadata=data.get('metadata', {})
            )
            
            logger.info(f"Imported hash result from {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error importing hash result: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear the hash cache"""
        try:
            self.hash_cache.clear()
            logger.info("Hash cache cleared")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
    
    def get_generator_stats(self) -> Dict[str, Any]:
        """Get generator statistics and configuration"""
        try:
            return {
                'generator': 'HashGenerator',
                'version': '1.0.0',
                'supported_algorithms': list(self.supported_algorithms.keys()),
                'default_salt_length': self.default_salt_length,
                'cache_size': len(self.hash_cache),
                'cache_max_size': self.cache_max_size,
                'capabilities': {
                    'secure_hashing': True,
                    'salted_hashing': True,
                    'hmac_generation': True,
                    'merkle_trees': True,
                    'rolling_hash': True,
                    'locality_sensitive_hash': True,
                    'batch_processing': True,
                    'hash_verification': True,
                    'similarity_calculation': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting generator stats: {str(e)}")
            return {'error': str(e)}
