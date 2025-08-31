"""Caching Agent Utilities

Utility functions and helper classes for the caching agent system,
providing common functionality and tools for cache operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

ATTENTION: Ce code fait partie de la propriété intellectuelle de Fahed Mlaiel.
Toute reproduction, distribution, ou utilisation non autorisée est strictement interdite.
Contact: mlaiel@live.de
"""
import asyncio
import hashlib
import json
import time
import zlib
import gzip
import lz4.frame
import zstandard as zstd
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

from .exceptions import CacheSerializationError, CacheCompressionError


@dataclass
class CacheKey:
    """Structured cache key with metadata."""    
    namespace: str
    identifier: str
    version: Optional[str] = None
    tenant_id: Optional[str] = None
    content_type: Optional[str] = None
    
    def __post_init__(self):
        """Validate key components."""        if not self.namespace:
            raise ValueError("Namespace cannot be empty")
        if not self.identifier:
            raise ValueError("Identifier cannot be empty")
    
    def to_string(self) -> str:
        """Convert cache key to string representation."""        parts = [self.namespace, self.identifier]
        
        if self.tenant_id:
            parts.append(f"tenant:{self.tenant_id}")
        if self.version:
            parts.append(f"v:{self.version}")
        if self.content_type:
            parts.append(f"type:{self.content_type}")
            
        return ":".join(parts)
    
    def to_hash(self) -> str:
        """Convert cache key to hash for consistent key generation."""        return hashlib.sha256(self.to_string().encode('utf-8')).hexdigest()[:16]
    
    @classmethod
    def from_string(cls, key_string: str) -> 'CacheKey':
        """Parse cache key from string representation."""        parts = key_string.split(':')
        if len(parts) < 2:
            raise ValueError("Invalid key string format")
        
        namespace = parts[0]
        identifier = parts[1]
        
        # Parse optional components
        tenant_id = None
        version = None
        content_type = None
        
        for part in parts[2:]:
            if part.startswith('tenant:'):
                tenant_id = part[7:]
            elif part.startswith('v:'):
                version = part[2:]
            elif part.startswith('type:'):
                content_type = part[5:]
        
        return cls(
            namespace=namespace,
            identifier=identifier,
            version=version,
            tenant_id=tenant_id,
            content_type=content_type
        )


class SerializationManager:
    """Handles serialization and deserialization of cache data."""    
    SUPPORTED_FORMATS = {
        'json': {'serialize': json.dumps, 'deserialize': json.loads},
        'pickle': None,  # Implemented separately for security
        'msgpack': None  # Can be added if needed
    }
    
    @staticmethod
    def serialize(data: Any, format_type: str = 'json') -> bytes:
        """        Serialize data to bytes.
        
        Args:
            data: Data to serialize
            format_type: Serialization format
            
        Returns:
            Serialized data as bytes
        """        try:
            if format_type == 'json':
                json_str = json.dumps(data, default=str, ensure_ascii=False)
                return json_str.encode('utf-8')
            elif format_type == 'pickle':
                import pickle
                return pickle.dumps(data)
            else:
                raise CacheSerializationError(
                    f"Unsupported serialization format: {format_type}",
                    serialization_format=format_type
                )
        except Exception as e:
            raise CacheSerializationError(
                f"Serialization failed: {str(e)}",
                data_type=type(data).__name__,
                serialization_format=format_type
            ) from e
    
    @staticmethod
    def deserialize(data: bytes, format_type: str = 'json') -> Any:
        """        Deserialize data from bytes.
        
        Args:
            data: Serialized data
            format_type: Serialization format
            
        Returns:
            Deserialized data
        """        try:
            if format_type == 'json':
                json_str = data.decode('utf-8')
                return json.loads(json_str)
            elif format_type == 'pickle':
                import pickle
                return pickle.loads(data)
            else:
                raise CacheSerializationError(
                    f"Unsupported deserialization format: {format_type}",
                    serialization_format=format_type
                )
        except Exception as e:
            raise CacheSerializationError(
                f"Deserialization failed: {str(e)}",
                serialization_format=format_type
            ) from e


class CompressionManager:
    """Handles compression and decompression of cache data."""    
    @staticmethod
    def compress(data: bytes, compression_type: str = 'gzip') -> bytes:
        """        Compress data using specified algorithm.
        
        Args:
            data: Data to compress
            compression_type: Compression algorithm
            
        Returns:
            Compressed data
        """        try:
            if compression_type == 'gzip':
                return gzip.compress(data)
            elif compression_type == 'zlib':
                return zlib.compress(data)
            elif compression_type == 'lz4':
                return lz4.frame.compress(data)
            elif compression_type == 'zstd':
                cctx = zstd.ZstdCompressor()
                return cctx.compress(data)
            elif compression_type == 'none':
                return data
            else:
                raise CacheCompressionError(
                    f"Unsupported compression type: {compression_type}",
                    compression_type=compression_type
                )
        except Exception as e:
            raise CacheCompressionError(
                f"Compression failed: {str(e)}",
                compression_type=compression_type,
                operation="compress"
            ) from e
    
    @staticmethod
    def decompress(data: bytes, compression_type: str = 'gzip') -> bytes:
        """        Decompress data using specified algorithm.
        
        Args:
            data: Compressed data
            compression_type: Compression algorithm
            
        Returns:
            Decompressed data
        """        try:
            if compression_type == 'gzip':
                return gzip.decompress(data)
            elif compression_type == 'zlib':
                return zlib.decompress(data)
            elif compression_type == 'lz4':
                return lz4.frame.decompress(data)
            elif compression_type == 'zstd':
                dctx = zstd.ZstdDecompressor()
                return dctx.decompress(data)
            elif compression_type == 'none':
                return data
            else:
                raise CacheCompressionError(
                    f"Unsupported compression type: {compression_type}",
                    compression_type=compression_type
                )
        except Exception as e:
            raise CacheCompressionError(
                f"Decompression failed: {str(e)}",
                compression_type=compression_type,
                operation="decompress"
            ) from e
    
    @staticmethod
    def get_compression_ratio(original_size: int, compressed_size: int) -> float:
        """Calculate compression ratio."""        if original_size == 0:
            return 0.0
        return (original_size - compressed_size) / original_size


class TimingUtilities:
    """Utilities for time-based operations."""    
    @staticmethod
    def get_current_timestamp() -> float:
        """Get current timestamp in seconds."""        return time.time()
    
    @staticmethod
    def get_ttl_expiry(ttl_seconds: int) -> float:
        """Get expiry timestamp from TTL."""        return time.time() + ttl_seconds
    
    @staticmethod
    def is_expired(expiry_timestamp: float) -> bool:
        """Check if timestamp is expired."""        return time.time() > expiry_timestamp
    
    @staticmethod
    def get_remaining_ttl(expiry_timestamp: float) -> int:
        """Get remaining TTL in seconds."""        remaining = expiry_timestamp - time.time()
        return max(0, int(remaining))
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format."""        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"


class SizeUtilities:
    """Utilities for size calculations and formatting."""    
    @staticmethod
    def format_bytes(size_bytes: int) -> str:
        """Format byte size in human-readable format."""        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f}{size_names[i]}"
    
    @staticmethod
    def parse_size_string(size_string: str) -> int:
        """Parse size string to bytes."""        size_string = size_string.upper().strip()
        
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024,
            'TB': 1024 * 1024 * 1024 * 1024
        }
        
        for suffix, multiplier in multipliers.items():
            if size_string.endswith(suffix):
                number_part = size_string[:-len(suffix)].strip()
                try:
                    return int(float(number_part) * multiplier)
                except ValueError:
                    raise ValueError(f"Invalid size string: {size_string}")
        
        # Assume bytes if no suffix
        try:
            return int(size_string)
        except ValueError:
            raise ValueError(f"Invalid size string: {size_string}")


class HashUtilities:
    """Utilities for hashing operations."""    
    @staticmethod
    def hash_data(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """        Hash data using specified algorithm.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of hash
        """        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def consistent_hash(key: str, num_slots: int) -> int:
        """        Generate consistent hash for key distribution.
        
        Args:
            key: Key to hash
            num_slots: Number of hash slots
            
        Returns:
            Hash slot number
        """        hash_value = hashlib.sha256(key.encode('utf-8')).hexdigest()
        return int(hash_value, 16) % num_slots


class ValidationUtilities:
    """Utilities for data validation."""    
    @staticmethod
    def validate_key(key: str) -> bool:
        """Validate cache key format."""        if not key or not isinstance(key, str):
            return False
        
        # Basic validation - can be extended
        if len(key) > 512:  # Max key length
            return False
        
        # Check for invalid characters
        invalid_chars = ['\n', '\r', '\t', '\x00']
        for char in invalid_chars:
            if char in key:
                return False
        
        return True
    
    @staticmethod
    def validate_ttl(ttl: int) -> bool:
        """Validate TTL value."""        return isinstance(ttl, int) and ttl >= 0
    
    @staticmethod
    def validate_size(size: int, max_size: int) -> bool:
        """Validate data size."""        return isinstance(size, int) and 0 <= size <= max_size


class AsyncUtilities:
    """Utilities for async operations."""    
    @staticmethod
    async def run_with_timeout(coroutine, timeout_seconds: float):
        """Run coroutine with timeout."""        try:
            return await asyncio.wait_for(coroutine, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Operation timed out after {timeout_seconds}s")
    
    @staticmethod
    async def batch_execute(coroutines: List, batch_size: int = 10):
        """Execute coroutines in batches."""        results = []
        
        for i in range(0, len(coroutines), batch_size):
            batch = coroutines[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        
        return results


class ThreadUtilities:
    """Utilities for thread operations."""    
    _thread_pool = ThreadPoolExecutor(max_workers=4)
    _lock = threading.RLock()
    
    @classmethod
    def run_in_thread(cls, func, *args, **kwargs):
        """Run function in thread pool."""        return cls._thread_pool.submit(func, *args, **kwargs)
    
    @classmethod
    def get_thread_safe_counter(cls):
        """Get thread-safe counter."""        return ThreadSafeCounter()


class ThreadSafeCounter:
    """Thread-safe counter implementation."""    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.RLock()
    
    def increment(self, amount: int = 1) -> int:
        """Increment counter and return new value."""        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """Decrement counter and return new value."""        with self._lock:
            self._value -= amount
            return self._value
    
    def get_value(self) -> int:
        """Get current counter value."""        with self._lock:
            return self._value
    
    def reset(self, value: int = 0) -> int:
        """Reset counter to specified value."""        with self._lock:
            old_value = self._value
            self._value = value
            return old_value


class PerformanceTimer:
    """Context manager for performance timing."""    
    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
    
    def get_duration_ms(self) -> float:
        """Get duration in milliseconds."""        return self.duration * 1000 if self.duration else 0
    
    def get_duration_seconds(self) -> float:
        """Get duration in seconds."""        return self.duration if self.duration else 0


class ConfigurationValidator:
    """Validates cache configuration parameters."""    
    @staticmethod
    def validate_cache_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """        Validate cache configuration.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """        errors = []
        
        # Required fields
        required_fields = ['max_memory_size', 'max_entries', 'default_ttl']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric fields
        numeric_fields = {
            'max_memory_size': (1024, 10 * 1024 * 1024 * 1024),  # 1KB to 10GB
            'max_entries': (1, 10000000),  # 1 to 10M entries
            'default_ttl': (1, 86400 * 365),  # 1 second to 1 year
            'compression_threshold': (0, 1024 * 1024)  # 0 to 1MB
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in config:
                value = config[field]
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    errors.append(f"Invalid {field}: must be between {min_val} and {max_val}")
        
        # Validate boolean fields
        boolean_fields = ['enable_encryption', 'enable_analytics', 'enable_distributed_coordination']
        for field in boolean_fields:
            if field in config and not isinstance(config[field], bool):
                errors.append(f"Invalid {field}: must be boolean")
        
        return len(errors) == 0, errors


# Global utility instances for easy access
serialization_manager = SerializationManager()
compression_manager = CompressionManager()
timing_utils = TimingUtilities()
size_utils = SizeUtilities()
hash_utils = HashUtilities()
validation_utils = ValidationUtilities()
async_utils = AsyncUtilities()
thread_utils = ThreadUtilities()
config_validator = ConfigurationValidator()
