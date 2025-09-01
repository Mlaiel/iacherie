"""Cache Compression Configuration for IA-Influencer Agent Platform
=================================================================

Advanced compression strategies for cache data to optimize memory usage
and network bandwidth in distributed caching environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import zlib
import gzip
import bz2
import lzma
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, validator


class CompressionAlgorithm(str, Enum):
    """
Supported compression algorithms"""

    GZIP = "gzip"
    ZLIB = "zlib"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    LZ4 = "lz4"
    ZSTD = "zstd"
    SNAPPY = "snappy"
    NONE = "none"


class CompressionLevel(int, Enum):
    """Compression levels (1-9, where 9 is highest compression)"""

    FASTEST = 1
    FAST = 3
    DEFAULT = 6
    BEST = 9


class ContentType(str, Enum):
    """
Content types for compression optimization"""

    JSON = "json"
    XML = "xml"
    TEXT = "text"
    BINARY = "binary"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    HTML = "html"
    CSS = "css"
    JAVASCRIPT = "javascript"
    PDF = "pdf"
    UNKNOWN = "unknown"


@dataclass
class CompressionProfile:
    """Compression profile for specific content types"""
    name: str
    algorithm: CompressionAlgorithm
    level: CompressionLevel
    min_size_bytes: int = 1024
    max_size_bytes: int = 10 * 1024 * 1024  # 10MB
    content_types: List[ContentType] = field(default_factory=list)
    key_patterns: List[str] = field(default_factory=list)
    enabled: bool = True
    
    # Performance settings
    max_compression_time_ms: int = 5000
    parallel_compression: bool = False
    chunk_size: int = 64 * 1024  # 64KB chunks
    
    # Quality settings
    min_compression_ratio: float = 0.1  # At least 10% reduction
    target_compression_ratio: float = 0.3  # Target 30% reduction
    
    def should_compress(self, data_size: int, content_type: ContentType = None, 
                       key: str = None) -> bool:
        """
Check if data should be compressed with this profile"""
        if not self.enabled:
            return False
        
        # Size check
        if not (self.min_size_bytes <= data_size <= self.max_size_bytes):
            return False
        
        # Content type check
        if content_type and self.content_types and content_type not in self.content_types:
            return False
        
        # Key pattern check
        if key and self.key_patterns:
            if not any(pattern in key for pattern in self.key_patterns):
                return False
        
        return True


@dataclass
class CompressionMetrics:
    """
Compression performance metrics"""
    total_compressions: int = 0
    total_decompressions: int = 0
    bytes_before_compression: int = 0
    bytes_after_compression: int = 0
    total_compression_time: float = 0.0
    total_decompression_time: float = 0.0
    compression_failures: int = 0
    decompression_failures: int = 0
    
    @property
    def compression_ratio(self) -> float:
        """
Average compression ratio"""
        if self.bytes_before_compression == 0:
            return 0.0
        return self.bytes_after_compression / self.bytes_before_compression
    
    @property
    def space_saved_bytes(self) -> int:
        """
Total bytes saved through compression"""
        return self.bytes_before_compression - self.bytes_after_compression
    
    @property
    def space_saved_percentage(self) -> float:
        """
Percentage of space saved"""
        if self.bytes_before_compression == 0:
            return 0.0
        return (1.0 - self.compression_ratio) * 100.0
    
    @property
    def avg_compression_time(self) -> float:
        """
Average compression time per operation"""
        if self.total_compressions == 0:
            return 0.0
        return self.total_compression_time / self.total_compressions
    
    @property
    def avg_decompression_time(self) -> float:
        """
Average decompression time per operation"""
        if self.total_decompressions == 0:
            return 0.0
        return self.total_decompression_time / self.total_decompressions


class CacheCompressionConfig(BaseModel):
    """
    Comprehensive cache compression configuration
    """
    
    # General settings
    enabled: bool = True
    default_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB
    default_level: CompressionLevel = CompressionLevel.DEFAULT
    
    # Compression profiles
    profiles: List[CompressionProfile] = field(default_factory=list)
    
    # Threshold settings
    global_min_size: int = 512  # Don't compress smaller data
    global_max_size: int = 50 * 1024 * 1024  # 50MB limit
    compression_threshold: float = 0.1  # Must achieve 10% compression
    
    # Performance settings
    async_compression: bool = True
    compression_workers: int = 4
    worker_queue_size: int = 1000
    compression_timeout: int = 30  # seconds
    
    # Content detection
    auto_detect_content_type: bool = True
    content_type_header: str = "content-type"
    fallback_content_type: ContentType = ContentType.UNKNOWN
    
    # Caching of compressed data
    cache_compressed_data: bool = True
    compressed_cache_ttl: int = 3600  # 1 hour
    store_compression_metadata: bool = True
    
    # Multi-tenant support
    tenant_specific_profiles: bool = False
    tenant_compression_quotas: Dict[str, int] = field(default_factory=dict)  # bytes per tenant
    
    # Monitoring and metrics
    enable_metrics: bool = True
    metrics_collection_interval: int = 300  # 5 minutes
    log_compression_stats: bool = True
    
    # Error handling
    compression_failure_fallback: str = "store_uncompressed"  # store_uncompressed, skip, error
    max_consecutive_failures: int = 5
    failure_circuit_breaker: bool = True
    circuit_breaker_timeout: int = 300  # 5 minutes
    
    # Adaptive compression
    adaptive_compression: bool = True
    performance_monitoring_window: int = 3600  # 1 hour
    auto_adjust_levels: bool = True
    performance_target_ms: int = 100  # Target compression time
    
    class Config:
        use_enum_values = True
        validate_assignment = True
    
    @validator('global_min_size')
    def validate_min_size(cls, v):
        if v < 0:
            raise ValueError("Minimum size cannot be negative")
        return v
    
    @validator('compression_threshold')
    def validate_compression_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Compression threshold must be between 0 and 1")
        return v
    
    @validator('compression_workers')
    def validate_workers(cls, v):
        if v <= 0:
            raise ValueError("Number of workers must be positive")
        return v
    
    def add_profile(self, profile: CompressionProfile):
        """Add compression profile"""
        if any(p.name == profile.name for p in self.profiles):
            raise ValueError(f"Profile with name '{profile.name}' already exists")
        
        self.profiles.append(profile)
    
    def remove_profile(self, profile_name: str) -> bool:
        """Remove compression profile"""
        for i, profile in enumerate(self.profiles):
            if profile.name == profile_name:
                del self.profiles[i]
                return True
        return False
    
    def get_profile_for_data(self, data_size: int, content_type: ContentType = None, 
                           key: str = None, tenant_id: str = None) -> Optional[CompressionProfile]:
        """
Get best compression profile for given data"""
        if not self.enabled:
            return None
        
        # Check global size limits
        if not (self.global_min_size <= data_size <= self.global_max_size):
            return None
        
        # Check tenant quota
        if tenant_id and tenant_id in self.tenant_compression_quotas:
            quota = self.tenant_compression_quotas[tenant_id]
            if data_size > quota:
                return None
        
        # Find matching profiles
        matching_profiles = []
        for profile in self.profiles:
            if profile.should_compress(data_size, content_type, key):
                matching_profiles.append(profile)
        
        if not matching_profiles:
            # Use default profile if no specific match
            return CompressionProfile(
                name="default",
                algorithm=self.default_algorithm,
                level=self.default_level,
                min_size_bytes=self.global_min_size,
                max_size_bytes=self.global_max_size
            )
        
        # Return first matching profile (profiles should be ordered by priority)
        return matching_profiles[0]
    
    def detect_content_type(self, data: bytes, key: str = None) -> ContentType:
        """Detect content type from data or key"""
        if not self.auto_detect_content_type:
            return self.fallback_content_type
        
        # Try to detect from key extension
        if key:
            key_lower = key.lower()
            if key_lower.endswith(('.json', '.js')):
                return ContentType.JSON
            elif key_lower.endswith(('.xml', '.html', '.htm')):
                return ContentType.XML if '.xml' in key_lower else ContentType.HTML
            elif key_lower.endswith(('.txt', '.log')):
                return ContentType.TEXT
            elif key_lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                return ContentType.IMAGE
            elif key_lower.endswith(('.mp3', '.wav', '.flac', '.ogg')):
                return ContentType.AUDIO
            elif key_lower.endswith(('.mp4', '.avi', '.mkv', '.mov')):
                return ContentType.VIDEO
            elif key_lower.endswith('.pdf'):
                return ContentType.PDF
            elif key_lower.endswith('.css'):
                return ContentType.CSS
            elif key_lower.endswith('.js'):
                return ContentType.JAVASCRIPT
        
        # Try to detect from data content
        if data:
            # Check for JSON
            if data.strip().startswith(b'{') or data.strip().startswith(b'['):
                return ContentType.JSON
            
            # Check for XML/HTML
            if data.strip().startswith(b'<'):
                if b'<html' in data[:1024].lower():
                    return ContentType.HTML
                else:
                    return ContentType.XML
            
            # Check for text (printable ASCII)
            try:
                data.decode('utf-8')
                return ContentType.TEXT
            except UnicodeDecodeError:
                pass
            
            # Check for common binary signatures
            if data.startswith(b'\x89PNG'):
                return ContentType.IMAGE
            elif data.startswith(b'\xff\xfb') or data.startswith(b'ID3'):
                return ContentType.AUDIO
            elif data.startswith(b'%PDF'):
                return ContentType.PDF
        
        return self.fallback_content_type
    
    def should_use_async_compression(self, data_size: int, algorithm: CompressionAlgorithm) -> bool:
        """
Determine if async compression should be used"""
        if not self.async_compression:
            return False
        
        # Use async for larger data or slower algorithms
        large_data_threshold = 10 * 1024  # 10KB
        slow_algorithms = [CompressionAlgorithm.BZIP2, CompressionAlgorithm.LZMA]
        
        return data_size >= large_data_threshold or algorithm in slow_algorithms
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """
Get configuration summary"""
        return {
            "enabled": self.enabled,
            "default_algorithm": self.default_algorithm,
            "total_profiles": len(self.profiles),
            "active_profiles": len([p for p in self.profiles if p.enabled]),
            "global_min_size": self.global_min_size,
            "global_max_size": self.global_max_size,
            "async_compression": self.async_compression,
            "compression_workers": self.compression_workers,
            "adaptive_compression": self.adaptive_compression,
            "metrics_enabled": self.enable_metrics
        }


class CompressionEngine:
    """
    Cache compression engine with async support
    """
    
    def __init__(self, config: CacheCompressionConfig):
        self.config = config
        self.metrics = CompressionMetrics()
        self.executor = None
        self.compression_cache: Dict[str, tuple] = {}  # Cache compressed data
        self.circuit_breaker_state = "closed"
        self.consecutive_failures = 0
        self.last_failure_time = 0
        
        if config.async_compression:
            self.executor = ThreadPoolExecutor(max_workers=config.compression_workers)
    
    def __del__(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=False)
    
    async def compress(self, data: Union[str, bytes], key: str = None, 
                     tenant_id: str = None, force_sync: bool = False) -> tuple:
        """
        Compress data with optimal algorithm
        Returns: (compressed_data, compression_metadata)
        """
        if not self.config.enabled or not data:
            return data, None
        
        # Check circuit breaker
        if not self._check_circuit_breaker():
            return data, None
        
        # Convert to bytes if string
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        data_size = len(data)
        
        # Detect content type
        content_type = self.config.detect_content_type(data, key)
        
        # Get compression profile
        profile = self.config.get_profile_for_data(data_size, content_type, key, tenant_id)
        if not profile:
            return data, None
        
        # Check compression cache
        cache_key = self._generate_cache_key(data, profile)
        if self.config.cache_compressed_data and cache_key in self.compression_cache:
            cached_data, metadata = self.compression_cache[cache_key]
            return cached_data, metadata
        
        start_time = time.time()
        
        try:
            # Determine compression method
            use_async = (self.config.should_use_async_compression(data_size, profile.algorithm) 
                        and not force_sync and self.executor)
            
            if use_async:
                compressed_data = await self._compress_async(data, profile)
            else:
                compressed_data = self._compress_sync(data, profile)
            
            compression_time = time.time() - start_time
            
            # Check compression effectiveness
            compression_ratio = len(compressed_data) / len(data)
            
            if compression_ratio > (1.0 - profile.min_compression_ratio):
                # Compression not effective enough
                self.metrics.compression_failures += 1
                return data, None
            
            # Create metadata
            metadata = {
                "algorithm": profile.algorithm,
                "level": profile.level,
                "original_size": len(data),
                "compressed_size": len(compressed_data),
                "compression_ratio": compression_ratio,
                "compression_time": compression_time,
                "content_type": content_type,
                "profile": profile.name
            }
            
            # Update metrics
            self._update_compression_metrics(len(data), len(compressed_data), compression_time, True)
            
            # Cache compressed data
            if self.config.cache_compressed_data:
                self.compression_cache[cache_key] = (compressed_data, metadata)
            
            # Reset circuit breaker on success
            self.consecutive_failures = 0
            
            return compressed_data, metadata
            
        except Exception as e:
            compression_time = time.time() - start_time
            self._update_compression_metrics(len(data), 0, compression_time, False)
            self._handle_compression_failure()
            
            # Fallback behavior
            if self.config.compression_failure_fallback == "store_uncompressed":
                return data, None
            elif self.config.compression_failure_fallback == "skip":
                return None, None
            else:  # "error"
                raise e
    
    async def decompress(self, compressed_data: bytes, metadata: Dict[str, Any]) -> bytes:
        """
        Decompress data using stored metadata
        """
        if not metadata or not compressed_data:
            return compressed_data
        
        algorithm = CompressionAlgorithm(metadata.get("algorithm", CompressionAlgorithm.ZLIB))
        start_time = time.time()
        
        try:
            # Determine decompression method
            use_async = len(compressed_data) > 10 * 1024 and self.executor  # 10KB threshold
            
            if use_async:
                decompressed_data = await self._decompress_async(compressed_data, algorithm)
            else:
                decompressed_data = self._decompress_sync(compressed_data, algorithm)
            
            decompression_time = time.time() - start_time
            
            # Update metrics
            self.metrics.total_decompressions += 1
            self.metrics.total_decompression_time += decompression_time
            
            return decompressed_data
            
        except Exception as e:
            decompression_time = time.time() - start_time
            self.metrics.decompression_failures += 1
            self.metrics.total_decompression_time += decompression_time
            raise e
    
    async def _compress_async(self, data: bytes, profile: CompressionProfile) -> bytes:
        """Asynchronous compression"""
        loop = asyncio.get_event_loop()
        
        # For large data, use chunked compression
        if len(data) > profile.chunk_size and profile.parallel_compression:
            return await self._compress_chunked(data, profile)
        else:
            return await loop.run_in_executor(
                self.executor, self._compress_sync, data, profile
            )
    
    def _compress_sync(self, data: bytes, profile: CompressionProfile) -> bytes:
        """
Synchronous compression"""
        algorithm = profile.algorithm
        level = profile.level.value
        
        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=level)
        elif algorithm == CompressionAlgorithm.ZLIB:
            return zlib.compress(data, level=level)
        elif algorithm == CompressionAlgorithm.BZIP2:
            return bz2.compress(data, compresslevel=level)
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.compress(data, preset=level)
        elif algorithm == CompressionAlgorithm.LZ4:
            try:
                import lz4.frame
                return lz4.frame.compress(data, compression_level=level)
            except ImportError:
                # Fallback to zlib
                return zlib.compress(data, level=level)
        elif algorithm == CompressionAlgorithm.ZSTD:
            try:
                import zstd
                return zstd.compress(data, level=level)
            except ImportError:
                # Fallback to zlib
                return zlib.compress(data, level=level)
        elif algorithm == CompressionAlgorithm.SNAPPY:
            try:
                import snappy
                return snappy.compress(data)
            except ImportError:
                # Fallback to zlib
                return zlib.compress(data, level=level)
        else:
            # Default to zlib
            return zlib.compress(data, level=level)
    
    async def _compress_chunked(self, data: bytes, profile: CompressionProfile) -> bytes:
        """
Compress data in parallel chunks"""
        chunk_size = profile.chunk_size
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        # Compress chunks in parallel
        tasks = []
        for chunk in chunks:
            task = asyncio.get_event_loop().run_in_executor(
                self.executor, self._compress_sync, chunk, profile
            )
            tasks.append(task)
        
        compressed_chunks = await asyncio.gather(*tasks)
        
        # Combine compressed chunks with metadata
        result = b""
        for chunk in compressed_chunks:
            # Add chunk length prefix
            result += len(chunk).to_bytes(4, 'big') + chunk
        
        return result
    
    async def _decompress_async(self, compressed_data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """Asynchronous decompression"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._decompress_sync, compressed_data, algorithm
        )
    
    def _decompress_sync(self, compressed_data: bytes, algorithm: CompressionAlgorithm) -> bytes:
        """
Synchronous decompression"""
        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.ZLIB:
            return zlib.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.BZIP2:
            return bz2.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.LZ4:
            try:
                import lz4.frame
                return lz4.frame.decompress(compressed_data)
            except ImportError:
                return zlib.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.ZSTD:
            try:
                import zstd
                return zstd.decompress(compressed_data)
            except ImportError:
                return zlib.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.SNAPPY:
            try:
                import snappy
                return snappy.decompress(compressed_data)
            except ImportError:
                return zlib.decompress(compressed_data)
        else:
            return zlib.decompress(compressed_data)
    
    def _generate_cache_key(self, data: bytes, profile: CompressionProfile) -> str:
        """
Generate cache key for compressed data"""
        import hashlib
        data_hash = hashlib.md5(data).hexdigest()
        return f"{profile.name}:{profile.algorithm}:{profile.level}:{data_hash}"
    
    def _update_compression_metrics(self, original_size: int, compressed_size: int, 
                                  compression_time: float, success: bool):
        """Update compression metrics"""
        if success:
            self.metrics.total_compressions += 1
            self.metrics.bytes_before_compression += original_size
            self.metrics.bytes_after_compression += compressed_size
        else:
            self.metrics.compression_failures += 1
        
        self.metrics.total_compression_time += compression_time
    
    def _handle_compression_failure(self):
        """
Handle compression failure for circuit breaker"""
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        
        if (self.config.failure_circuit_breaker and 
            self.consecutive_failures >= self.config.max_consecutive_failures):
            self.circuit_breaker_state = "open"
    
    def _check_circuit_breaker(self) -> bool:
        """Check circuit breaker state"""
        if not self.config.failure_circuit_breaker:
            return True
        
        if self.circuit_breaker_state == "closed":
            return True
        elif self.circuit_breaker_state == "open":
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.config.circuit_breaker_timeout:
                self.circuit_breaker_state = "half_open"
                return True
            return False
        else:  # half_open
            return True
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get compression metrics summary"""
        return {
            "total_compressions": self.metrics.total_compressions,
            "total_decompressions": self.metrics.total_decompressions,
            "compression_ratio": self.metrics.compression_ratio,
            "space_saved_bytes": self.metrics.space_saved_bytes,
            "space_saved_percentage": self.metrics.space_saved_percentage,
            "avg_compression_time": self.metrics.avg_compression_time,
            "avg_decompression_time": self.metrics.avg_decompression_time,
            "compression_failures": self.metrics.compression_failures,
            "decompression_failures": self.metrics.decompression_failures,
            "circuit_breaker_state": self.circuit_breaker_state,
            "cache_entries": len(self.compression_cache)
        }


# Predefined compression profiles for common use cases
TEXT_PROFILE = CompressionProfile(
    name="text_optimized",
    algorithm=CompressionAlgorithm.ZLIB,
    level=CompressionLevel.BEST,
    content_types=[ContentType.TEXT, ContentType.JSON, ContentType.XML, ContentType.HTML],
    min_compression_ratio=0.3,
    target_compression_ratio=0.5
)

BINARY_PROFILE = CompressionProfile(
    name="binary_optimized",
    algorithm=CompressionAlgorithm.LZ4,
    level=CompressionLevel.FAST,
    content_types=[ContentType.BINARY],
    min_compression_ratio=0.1,
    parallel_compression=True
)

LARGE_DATA_PROFILE = CompressionProfile(
    name="large_data",
    algorithm=CompressionAlgorithm.ZSTD,
    level=CompressionLevel.DEFAULT,
    min_size_bytes=100 * 1024,  # 100KB
    parallel_compression=True,
    chunk_size=128 * 1024  # 128KB chunks
)

FAST_PROFILE = CompressionProfile(
    name="fast_compression",
    algorithm=CompressionAlgorithm.SNAPPY,
    level=CompressionLevel.FASTEST,
    max_compression_time_ms=1000,
    min_compression_ratio=0.05
)

# Default configurations
DEFAULT_CONFIG = CacheCompressionConfig(
    profiles=[TEXT_PROFILE, BINARY_PROFILE, FAST_PROFILE]
)

PRODUCTION_CONFIG = CacheCompressionConfig(
    enabled=True,
    profiles=[TEXT_PROFILE, BINARY_PROFILE, LARGE_DATA_PROFILE, FAST_PROFILE],
    async_compression=True,
    compression_workers=8,
    adaptive_compression=True,
    cache_compressed_data=True,
    enable_metrics=True,
    failure_circuit_breaker=True
)

DEVELOPMENT_CONFIG = CacheCompressionConfig(
    enabled=True,
    profiles=[TEXT_PROFILE, FAST_PROFILE],
    async_compression=False,
    compression_workers=2,
    enable_metrics=True,
    log_compression_stats=True
)
