#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache Compression Engine - Industrial-Grade Data Compression
===========================================================

Advanced compression system with multiple algorithms, adaptive selection,
and real-time performance optimization for cache efficiency.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Data input → Algorithm selection → Compression optimization → 
Space efficiency → Performance tracking → Adaptive learning
"""import asyncio
import logging
import gzip
import lz4.frame
import zstandard as zstd
import brotli
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import numpy as np

logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """Advanced compression algorithms for different use cases."""    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"
    ADAPTIVE = "adaptive"

class CompressionLevel(Enum):
    """Compression level priorities."""    FASTEST = 1
    FAST = 3
    BALANCED = 6
    BEST = 9
    MAXIMUM = 12

@dataclass
class CompressionStats:
    """Comprehensive compression statistics."""    algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_time_ms: float
    decompression_time_ms: float = 0.0
    
    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio."""        if self.original_size == 0:
            return 1.0
        return self.compressed_size / self.original_size
    
    @property
    def space_savings_percent(self) -> float:
        """Calculate space savings percentage."""        return (1 - self.compression_ratio) * 100
    
    @property
    def compression_speed_mbps(self) -> float:
        """Calculate compression speed in MB/s."""        if self.compression_time_ms == 0:
            return 0.0
        size_mb = self.original_size / (1024 * 1024)
        time_seconds = self.compression_time_ms / 1000
        return size_mb / time_seconds

class IndustrialCacheCompressor:
    """    🎯 Industrial-Grade Cache Compression Engine
    
    Advanced compression system featuring:
    - Multiple compression algorithms (gzip, LZ4, Zstandard, Brotli)
    - Adaptive algorithm selection based on data characteristics
    - Real-time performance monitoring and optimization
    - Content-aware compression strategies
    - Parallel compression for large datasets
    - Machine learning-driven algorithm recommendation
    """    
    def __init__(self):
        """Initialize industrial cache compressor."""        self.logger = logging.getLogger(f"{__name__}.IndustrialCacheCompressor")
        
        # Performance tracking
        self.algorithm_stats = defaultdict(list)
        self.content_type_preferences = defaultdict(str)
        self.size_thresholds = {
            CompressionAlgorithm.LZ4: 1024,      # 1KB
            CompressionAlgorithm.GZIP: 2048,     # 2KB
            CompressionAlgorithm.ZSTD: 4096,     # 4KB
            CompressionAlgorithm.BROTLI: 8192,   # 8KB
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Adaptive learning
        self._learning_enabled = True
        self._min_samples_for_learning = 100
        
        self.logger.info("🚀 Industrial Cache Compressor initialized")
    
    async def initialize(self) -> bool:
        """Initialize compression engine."""        try:
            # Test all compression algorithms
            test_data = b"test data for compression algorithms" * 100
            
            for algorithm in CompressionAlgorithm:
                if algorithm in [CompressionAlgorithm.NONE, CompressionAlgorithm.ADAPTIVE]:
                    continue
                
                try:
                    compressed = await self.compress(test_data, algorithm)
                    decompressed = await self.decompress(compressed, algorithm)
                    
                    if decompressed == test_data:
                        self.logger.debug(f"✅ {algorithm.value} compression verified")
                    else:
                        self.logger.warning(f"❌ {algorithm.value} compression failed verification")
                        
                except Exception as e:
                    self.logger.warning(f"❌ {algorithm.value} not available: {e}")
            
            self.logger.info("✅ Cache Compressor successfully initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Cache Compressor initialization failed: {e}")
            return False
    
    async def compress(
        self, 
        data: bytes, 
        algorithm: CompressionAlgorithm = CompressionAlgorithm.ADAPTIVE,
        level: CompressionLevel = CompressionLevel.BALANCED
    ) -> Tuple[bytes, CompressionStats]:
        """        Compress data using specified or adaptive algorithm.
        
        Args:
            data: Data to compress
            algorithm: Compression algorithm to use
            level: Compression level
            
        Returns:
            Tuple of (compressed_data, compression_stats)
        """        start_time = time.perf_counter()
        
        try:
            # Select optimal algorithm if adaptive
            if algorithm == CompressionAlgorithm.ADAPTIVE:
                algorithm = self._select_optimal_algorithm(data)
            
            # Skip compression for small data
            if len(data) < self.size_thresholds.get(algorithm, 1024):
                stats = CompressionStats(
                    algorithm=CompressionAlgorithm.NONE,
                    original_size=len(data),
                    compressed_size=len(data),
                    compression_time_ms=0.0
                )
                return data, stats
            
            # Perform compression
            compressed_data = await self._compress_with_algorithm(data, algorithm, level)
            compression_time = (time.perf_counter() - start_time) * 1000
            
            # Create statistics
            stats = CompressionStats(
                algorithm=algorithm,
                original_size=len(data),
                compressed_size=len(compressed_data),
                compression_time_ms=compression_time
            )
            
            # Update learning data
            if self._learning_enabled:
                with self._lock:
                    self.algorithm_stats[algorithm].append(stats)
                    
                    # Keep only recent samples
                    if len(self.algorithm_stats[algorithm]) > 1000:
                        self.algorithm_stats[algorithm] = self.algorithm_stats[algorithm][-500:]
            
            # Only return compressed data if it's actually smaller
            if len(compressed_data) < len(data) * 0.95:  # At least 5% savings
                return compressed_data, stats
            else:
                # Return original data if compression not beneficial
                stats.algorithm = CompressionAlgorithm.NONE
                stats.compressed_size = len(data)
                return data, stats
                
        except Exception as e:
            self.logger.error(f"❌ Compression failed with {algorithm.value}: {e}")
            # Return original data on compression failure
            stats = CompressionStats(
                algorithm=CompressionAlgorithm.NONE,
                original_size=len(data),
                compressed_size=len(data),
                compression_time_ms=(time.perf_counter() - start_time) * 1000
            )
            return data, stats
    
    async def decompress(
        self, 
        compressed_data: bytes, 
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """        Decompress data using specified algorithm.
        
        Args:
            compressed_data: Compressed data
            algorithm: Algorithm used for compression
            
        Returns:
            Decompressed data
        """        start_time = time.perf_counter()
        
        try:
            if algorithm == CompressionAlgorithm.NONE:
                return compressed_data
            
            decompressed_data = await self._decompress_with_algorithm(
                compressed_data, algorithm
            )
            
            decompression_time = (time.perf_counter() - start_time) * 1000
            
            # Update decompression stats if available
            if self._learning_enabled and algorithm in self.algorithm_stats:
                with self._lock:
                    recent_stats = self.algorithm_stats[algorithm]
                    if recent_stats:
                        recent_stats[-1].decompression_time_ms = decompression_time
            
            return decompressed_data
            
        except Exception as e:
            self.logger.error(f"❌ Decompression failed with {algorithm.value}: {e}")
            raise
    
    async def _compress_with_algorithm(
        self, 
        data: bytes, 
        algorithm: CompressionAlgorithm,
        level: CompressionLevel
    ) -> bytes:
        """Compress data with specific algorithm."""        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=level.value)
        
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.compress(data, compression_level=level.value)
        
        elif algorithm == CompressionAlgorithm.ZSTD:
            cctx = zstd.ZstdCompressor(level=level.value)
            return cctx.compress(data)
        
        elif algorithm == CompressionAlgorithm.BROTLI:
            return brotli.compress(data, quality=level.value)
        
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
    
    async def _decompress_with_algorithm(
        self, 
        compressed_data: bytes, 
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """Decompress data with specific algorithm."""        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(compressed_data)
        
        elif algorithm == CompressionAlgorithm.LZ4:
            return lz4.frame.decompress(compressed_data)
        
        elif algorithm == CompressionAlgorithm.ZSTD:
            dctx = zstd.ZstdDecompressor()
            return dctx.decompress(compressed_data)
        
        elif algorithm == CompressionAlgorithm.BROTLI:
            return brotli.decompress(compressed_data)
        
        else:
            raise ValueError(f"Unsupported decompression algorithm: {algorithm}")
    
    def _select_optimal_algorithm(self, data: bytes) -> CompressionAlgorithm:
        """        Select optimal compression algorithm based on data characteristics
        and historical performance.
        """        data_size = len(data)
        
        # Fast path for small data
        if data_size < 1024:
            return CompressionAlgorithm.LZ4
        
        # Analyze data characteristics
        data_entropy = self._calculate_entropy(data[:min(1024, len(data))])
        
        # High entropy data (already compressed/random) - use fast algorithm
        if data_entropy > 7.5:
            return CompressionAlgorithm.LZ4
        
        # Medium entropy - balanced approach
        elif data_entropy > 6.0:
            if data_size < 64 * 1024:  # 64KB
                return CompressionAlgorithm.ZSTD
            else:
                return CompressionAlgorithm.LZ4
        
        # Low entropy - use best compression
        else:
            if data_size < 1024 * 1024:  # 1MB
                return CompressionAlgorithm.ZSTD
            else:
                return CompressionAlgorithm.GZIP
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data sample."""        if not data:
            return 0.0
        
        # Count byte frequencies
        counts = defaultdict(int)
        for byte in data:
            counts[byte] += 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        
        for count in counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive compression performance statistics."""        with self._lock:
            stats = {}
            
            for algorithm, measurements in self.algorithm_stats.items():
                if not measurements:
                    continue
                
                compression_ratios = [m.compression_ratio for m in measurements]
                compression_times = [m.compression_time_ms for m in measurements]
                compression_speeds = [m.compression_speed_mbps for m in measurements]
                
                stats[algorithm.value] = {
                    'sample_count': len(measurements),
                    'avg_compression_ratio': np.mean(compression_ratios),
                    'avg_space_savings_percent': (1 - np.mean(compression_ratios)) * 100,
                    'avg_compression_time_ms': np.mean(compression_times),
                    'avg_compression_speed_mbps': np.mean(compression_speeds),
                    'p95_compression_time_ms': np.percentile(compression_times, 95),
                    'best_compression_ratio': min(compression_ratios),
                    'worst_compression_ratio': max(compression_ratios)
                }
            
            return stats
    
    def optimize_thresholds(self) -> Dict[str, int]:
        """Optimize size thresholds based on performance data."""        optimized_thresholds = {}
        
        with self._lock:
            for algorithm, measurements in self.algorithm_stats.items():
                if len(measurements) < self._min_samples_for_learning:
                    continue
                
                # Find optimal threshold where compression becomes beneficial
                beneficial_sizes = [
                    m.original_size for m in measurements 
                    if m.compression_ratio < 0.9  # At least 10% savings
                ]
                
                if beneficial_sizes:
                    # Use 25th percentile as threshold
                    threshold = int(np.percentile(beneficial_sizes, 25))
                    optimized_thresholds[algorithm.value] = threshold
                    self.size_thresholds[algorithm] = threshold
        
        return optimized_thresholds

# Aliases for compatibility
CacheCompressor = IndustrialCacheCompressor

class ContentCompressor(IndustrialCacheCompressor):
    """Content-aware compressor with specialized handling for different data types."""    
    def __init__(self):
        super().__init__()
        
        # Content-specific preferences
        self.content_preferences = {
            'text': CompressionAlgorithm.ZSTD,
            'json': CompressionAlgorithm.BROTLI,
            'binary': CompressionAlgorithm.LZ4,
            'image': CompressionAlgorithm.NONE,  # Usually already compressed
            'video': CompressionAlgorithm.NONE,  # Usually already compressed
            'audio': CompressionAlgorithm.NONE   # Usually already compressed
        }
    
    def detect_content_type(self, data: bytes) -> str:
        """Detect content type for optimization."""        if not data:
            return 'binary'
        
        # Simple heuristics for content detection
        try:
            # Try to decode as text
            text = data.decode('utf-8')
            
            # Check for JSON
            if text.strip().startswith(('{', '[')):
                return 'json'
            
            # General text
            return 'text'
            
        except UnicodeDecodeError:
            # Check for common binary signatures
            if data.startswith(b'\x89PNG'):
                return 'image'
            elif data.startswith((b'\xff\xd8\xff', b'GIF8')):
                return 'image'
            elif data.startswith(b'ID3'):
                return 'audio'
            else:
                return 'binary'

import asyncio
import logging
import gzip
import zlib
import lzma
import bz2
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple, BinaryIO
from dataclasses import dataclass
from enum import Enum
import json
import pickle
import base64

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
    brotli = None

try:
    import lz4.frame
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False
    lz4 = None

from ...core.config import get_settings
from ...core.utils import calculate_object_size

logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """Compression algorithm types."""    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    BROTLI = "brotli"
    LZ4 = "lz4"

class CompressionLevel(Enum):
    """Compression level settings."""    FASTEST = 1
    FAST = 3
    BALANCED = 6
    BEST = 9

@dataclass
class CompressionResult:
    """Compression operation result."""    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: CompressionAlgorithm
    level: int
    compression_time: float
    data: bytes

@dataclass
class CompressionSettings:
    """Compression configuration."""    algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP
    level: CompressionLevel = CompressionLevel.BALANCED
    threshold_bytes: int = 1024  # Minimum size to compress
    max_size_bytes: int = 104857600  # 100MB max
    auto_detect: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""        return {
            "algorithm": self.algorithm.value,
            "level": self.level.value,
            "threshold_bytes": self.threshold_bytes,
            "max_size_bytes": self.max_size_bytes,
            "auto_detect": self.auto_detect
        }

class CacheCompressor:
    """    Advanced cache compression engine.
    
    Features:
    - Multiple compression algorithms
    - Content-aware compression
    - Adaptive algorithm selection
    - Performance optimization
    - Compression ratio tracking
    """    
    def __init__(self, settings: Optional[CompressionSettings] = None):
        """Initialize cache compressor."""        self.settings = settings or CompressionSettings()
        self.logger = logging.getLogger(f"{__name__}.CacheCompressor")
        
        # Algorithm availability
        self.available_algorithms = {
            CompressionAlgorithm.GZIP: True,
            CompressionAlgorithm.ZLIB: True,
            CompressionAlgorithm.BZIP2: True,
            CompressionAlgorithm.LZMA: True,
            CompressionAlgorithm.BROTLI: HAS_BROTLI,
            CompressionAlgorithm.LZ4: HAS_LZ4
        }
        
        # Performance tracking
        self.compression_stats = {
            algorithm: {
                "operations": 0,
                "total_input_size": 0,
                "total_output_size": 0,
                "total_time": 0.0,
                "average_ratio": 0.0
            }
            for algorithm in CompressionAlgorithm
        }
        
        # Content type to algorithm mapping
        self.algorithm_by_content = {
            "text": CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
            "json": CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
            "binary": CompressionAlgorithm.LZ4 if HAS_LZ4 else CompressionAlgorithm.GZIP,
            "image": CompressionAlgorithm.NONE,  # Usually already compressed
            "audio": CompressionAlgorithm.NONE,  # Usually already compressed
            "video": CompressionAlgorithm.NONE   # Usually already compressed
        }
        
        self.logger.info(f"Cache compressor initialized with {self.settings.algorithm.value}")
    
    def _detect_content_type(self, data: Any) -> str:
        """Detect content type for compression optimization."""        if isinstance(data, str):
            try:
                json.loads(data)
                return "json"
            except (json.JSONDecodeError, ValueError):
                return "text"
        elif isinstance(data, dict):
            return "json"
        elif isinstance(data, bytes):
            # Simple binary detection
            if b'\x00' in data[:100]:  # Null bytes suggest binary
                return "binary"
            try:
                data.decode('utf-8')
                return "text"
            except UnicodeDecodeError:
                return "binary"
        else:
            return "binary"
    
    def _select_algorithm(self, data: Any, content_type: str) -> CompressionAlgorithm:
        """Select optimal compression algorithm."""        if self.settings.auto_detect:
            # Use content-aware selection
            algorithm = self.algorithm_by_content.get(content_type, self.settings.algorithm)
            
            # Fallback if algorithm not available
            if not self.available_algorithms.get(algorithm, False):
                algorithm = CompressionAlgorithm.GZIP
                
            return algorithm
        else:
            return self.settings.algorithm
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data to bytes."""        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode('utf-8')
        elif isinstance(data, (dict, list)):
            return json.dumps(data, separators=(',', ':')).encode('utf-8')
        else:
            return pickle.dumps(data)
    
    def _compress_with_algorithm(self, data: bytes, 
                               algorithm: CompressionAlgorithm,
                               level: int) -> bytes:
        """Compress data with specific algorithm."""        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data, compresslevel=level)
            
        elif algorithm == CompressionAlgorithm.ZLIB:
            return zlib.compress(data, level=level)
            
        elif algorithm == CompressionAlgorithm.BZIP2:
            return bz2.compress(data, compresslevel=level)
            
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.compress(data, preset=level)
            
        elif algorithm == CompressionAlgorithm.BROTLI and HAS_BROTLI:
            return brotli.compress(data, quality=level)
            
        elif algorithm == CompressionAlgorithm.LZ4 and HAS_LZ4:
            return lz4.frame.compress(data, compression_level=level)
            
        else:
            # No compression or algorithm not available
            return data
    
    def _decompress_with_algorithm(self, data: bytes,
                                 algorithm: CompressionAlgorithm) -> bytes:
        """Decompress data with specific algorithm."""        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(data)
            
        elif algorithm == CompressionAlgorithm.ZLIB:
            return zlib.decompress(data)
            
        elif algorithm == CompressionAlgorithm.BZIP2:
            return bz2.decompress(data)
            
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.decompress(data)
            
        elif algorithm == CompressionAlgorithm.BROTLI and HAS_BROTLI:
            return brotli.decompress(data)
            
        elif algorithm == CompressionAlgorithm.LZ4 and HAS_LZ4:
            return lz4.frame.decompress(data)
            
        else:
            # No compression
            return data
    
    async def compress(self, data: Any, 
                      algorithm: Optional[CompressionAlgorithm] = None,
                      level: Optional[CompressionLevel] = None) -> CompressionResult:
        """        Compress data for cache storage.
        
        Args:
            data: Data to compress
            algorithm: Compression algorithm override
            level: Compression level override
            
        Returns:
            Compression result with metadata
        """        start_time = datetime.now()
        
        try:
            # Serialize data
            serialized_data = self._serialize_data(data)
            original_size = len(serialized_data)
            
            # Check size threshold
            if original_size < self.settings.threshold_bytes:
                return CompressionResult(
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=1.0,
                    algorithm=CompressionAlgorithm.NONE,
                    level=0,
                    compression_time=0.0,
                    data=serialized_data
                )
            
            # Check maximum size
            if original_size > self.settings.max_size_bytes:
                raise ValueError(f"Data too large: {original_size} bytes")
            
            # Select algorithm
            content_type = self._detect_content_type(data)
            selected_algorithm = algorithm or self._select_algorithm(data, content_type)
            selected_level = (level or self.settings.level).value
            
            # Compress data
            if selected_algorithm == CompressionAlgorithm.NONE:
                compressed_data = serialized_data
            else:
                compressed_data = self._compress_with_algorithm(
                    serialized_data, selected_algorithm, selected_level
                )
            
            compressed_size = len(compressed_data)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            compression_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            stats = self.compression_stats[selected_algorithm]
            stats["operations"] += 1
            stats["total_input_size"] += original_size
            stats["total_output_size"] += compressed_size
            stats["total_time"] += compression_time
            stats["average_ratio"] = stats["total_output_size"] / stats["total_input_size"]
            
            # Create result with metadata header
            metadata = {
                "algorithm": selected_algorithm.value,
                "original_size": original_size,
                "content_type": content_type
            }
            
            # Prepend metadata to compressed data
            metadata_bytes = json.dumps(metadata).encode('utf-8')
            metadata_length = len(metadata_bytes).to_bytes(4, 'big')
            final_data = metadata_length + metadata_bytes + compressed_data
            
            result = CompressionResult(
                original_size=original_size,
                compressed_size=len(final_data),
                compression_ratio=len(final_data) / original_size,
                algorithm=selected_algorithm,
                level=selected_level,
                compression_time=compression_time,
                data=final_data
            )
            
            self.logger.debug(
                f"Compressed {original_size} -> {compressed_size} bytes "
                f"({compression_ratio:.2%}) with {selected_algorithm.value}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Compression error: {e}")
            # Return uncompressed data on error
            serialized_data = self._serialize_data(data)
            return CompressionResult(
                original_size=len(serialized_data),
                compressed_size=len(serialized_data),
                compression_ratio=1.0,
                algorithm=CompressionAlgorithm.NONE,
                level=0,
                compression_time=0.0,
                data=serialized_data
            )
    
    async def decompress(self, compressed_data: bytes) -> Any:
        """        Decompress cached data.
        
        Args:
            compressed_data: Compressed data with metadata
            
        Returns:
            Original decompressed data
        """        try:
            # Check if data has metadata header
            if len(compressed_data) < 4:
                # No metadata, assume uncompressed
                return self._deserialize_data(compressed_data)
            
            # Read metadata length
            metadata_length = int.from_bytes(compressed_data[:4], 'big')
            
            if metadata_length > len(compressed_data) - 4:
                # Invalid metadata, assume uncompressed
                return self._deserialize_data(compressed_data)
            
            # Extract metadata
            metadata_bytes = compressed_data[4:4+metadata_length]
            payload = compressed_data[4+metadata_length:]
            
            try:
                metadata = json.loads(metadata_bytes.decode('utf-8'))
                algorithm = CompressionAlgorithm(metadata["algorithm"])
            except (json.JSONDecodeError, KeyError, ValueError):
                # Invalid metadata, assume uncompressed
                return self._deserialize_data(compressed_data)
            
            # Decompress payload
            if algorithm == CompressionAlgorithm.NONE:
                decompressed_data = payload
            else:
                decompressed_data = self._decompress_with_algorithm(payload, algorithm)
            
            # Deserialize
            return self._deserialize_data(decompressed_data)
            
        except Exception as e:
            self.logger.error(f"Decompression error: {e}")
            # Try to return as-is if decompression fails
            try:
                return self._deserialize_data(compressed_data)
            except Exception:
                return compressed_data
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize bytes to original data type."""        try:
            # Try JSON first
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            
            # Try string
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                pass
            
            # Try pickle
            try:
                return pickle.loads(data)
            except (pickle.PickleError, EOFError):
                pass
            
            # Return as bytes
            return data
            
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            return data
    
    async def benchmark_algorithms(self, test_data: Any) -> Dict[str, CompressionResult]:
        """Benchmark compression algorithms on test data."""        results = {}
        
        for algorithm in CompressionAlgorithm:
            if algorithm == CompressionAlgorithm.NONE:
                continue
                
            if not self.available_algorithms.get(algorithm, False):
                continue
            
            try:
                result = await self.compress(test_data, algorithm)
                results[algorithm.value] = result
            except Exception as e:
                self.logger.warning(f"Benchmark failed for {algorithm.value}: {e}")
        
        return results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""        total_operations = sum(stats["operations"] for stats in self.compression_stats.values())
        total_input = sum(stats["total_input_size"] for stats in self.compression_stats.values())
        total_output = sum(stats["total_output_size"] for stats in self.compression_stats.values())
        
        return {
            "total_operations": total_operations,
            "total_input_bytes": total_input,
            "total_output_bytes": total_output,
            "overall_compression_ratio": total_output / total_input if total_input > 0 else 1.0,
            "space_saved_bytes": total_input - total_output,
            "space_saved_percentage": ((total_input - total_output) / total_input * 100) if total_input > 0 else 0,
            "algorithm_stats": {
                algo.value: stats for algo, stats in self.compression_stats.items()
                if stats["operations"] > 0
            }
        }

class ContentCompressor(CacheCompressor):
    """    Content-aware compressor for media and specialized content.
    
    Enhanced with content-specific optimization strategies.
    """    
    def __init__(self, settings: Optional[CompressionSettings] = None):
        """Initialize content compressor."""        super().__init__(settings)
        self.logger = logging.getLogger(f"{__name__}.ContentCompressor")
        
        # Content-specific settings
        self.content_settings = {
            "text": CompressionSettings(
                algorithm=CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
                level=CompressionLevel.BEST,
                threshold_bytes=100
            ),
            "json": CompressionSettings(
                algorithm=CompressionAlgorithm.BROTLI if HAS_BROTLI else CompressionAlgorithm.GZIP,
                level=CompressionLevel.BEST,
                threshold_bytes=200
            ),
            "binary": CompressionSettings(
                algorithm=CompressionAlgorithm.LZ4 if HAS_LZ4 else CompressionAlgorithm.GZIP,
                level=CompressionLevel.FAST,
                threshold_bytes=1024
            )
        }
    
    async def compress_content(self, data: Any, content_type: str) -> CompressionResult:
        """Compress with content-specific settings."""        settings = self.content_settings.get(content_type, self.settings)
        
        # Temporarily override settings
        original_settings = self.settings
        self.settings = settings
        
        try:
            result = await self.compress(data)
            return result
        finally:
            self.settings = original_settings
