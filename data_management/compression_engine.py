"""Advanced Compression Engine
Enterprise-grade compression system with multiple algorithms and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
License: Proprietary - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, or use without explicit written permission from Fahed Mlaiel
is strictly prohibited and may result in legal action.
"""
import asyncio
import gzip
import bz2
import lzma
import zlib
import zstd
import lz4.frame
import blosc
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple, Protocol
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiofiles
from concurrent.futures import ThreadPoolExecutor

from ..core.exceptions import CompressionException, ValidationError
from ..core.metrics import MetricsCollector


class CompressionAlgorithm(Enum):
    """Supported compression algorithms"""    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZLIB = "zlib"
    ZSTD = "zstd"  # Fast compression
    LZ4 = "lz4"    # Ultra-fast compression
    BLOSC = "blosc"  # For scientific data
    AUTO = "auto"   # Automatic selection


class CompressionLevel(Enum):
    """Compression level presets"""    FASTEST = 1
    FAST = 3
    BALANCED = 6
    BEST = 9
    ULTRA = 22  # For ZSTD


class ContentType(Enum):
    """Content type for optimization"""    TEXT = "text"
    BINARY = "binary"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DATABASE = "database"
    LOG = "log"
    JSON = "json"
    XML = "xml"


@dataclass
class CompressionResult:
    """Results of compression operation"""    algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    data: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def space_saved(self) -> int:
        """Calculate space saved in bytes"""        return self.original_size - self.compressed_size
    
    @property
    def space_saved_percentage(self) -> float:
        """Calculate space saved percentage"""        if self.original_size == 0:
            return 0.0
        return (self.space_saved / self.original_size) * 100


@dataclass
class CompressionProfile:
    """Compression profile for specific use cases"""    name: str
    algorithm: CompressionAlgorithm
    level: CompressionLevel
    content_types: List[ContentType]
    min_size_threshold: int = 1024  # Don't compress files smaller than this
    max_size_threshold: Optional[int] = None
    priority_speed: bool = False
    priority_ratio: bool = False
    custom_params: Dict[str, Any] = field(default_factory=dict)


class CompressionEngine:
    """    Advanced compression engine with intelligent algorithm selection,
    multi-threading support, and performance optimization
    """    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        max_workers: int = 4
    ):
        self.config = config or self._get_default_config()
        self.metrics_collector = metrics_collector
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.compression_stats = {
            "total_operations": 0,
            "total_original_size": 0,
            "total_compressed_size": 0,
            "total_time": 0.0,
            "algorithm_usage": {},
            "average_ratio": 0.0
        }
        
        # Predefined compression profiles
        self.profiles = self._create_default_profiles()
        
        # Algorithm availability
        self.available_algorithms = self._check_algorithm_availability()
        
        self.logger.info("Advanced compression engine initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default compression configuration"""        return {
            "default_algorithm": CompressionAlgorithm.ZSTD,
            "default_level": CompressionLevel.BALANCED,
            "auto_select_threshold": 0.1,  # Minimum compression ratio improvement
            "benchmark_sample_size": 8192,  # Bytes for algorithm benchmarking
            "enable_parallel": True,
            "chunk_size": 1024 * 1024,  # 1MB chunks for large files
            "cache_algorithm_choices": True,
            "min_compression_threshold": 1024,  # Don't compress files smaller than 1KB
            "max_file_size": 100 * 1024 * 1024,  # 100MB max file size
        }
    
    def _check_algorithm_availability(self) -> Dict[CompressionAlgorithm, bool]:
        """Check which compression algorithms are available"""        availability = {}
        
        try:
            import gzip
            availability[CompressionAlgorithm.GZIP] = True
        except ImportError:
            availability[CompressionAlgorithm.GZIP] = False
        
        try:
            import bz2
            availability[CompressionAlgorithm.BZIP2] = True
        except ImportError:
            availability[CompressionAlgorithm.BZIP2] = False
        
        try:
            import lzma
            availability[CompressionAlgorithm.LZMA] = True
        except ImportError:
            availability[CompressionAlgorithm.LZMA] = False
        
        try:
            import zlib
            availability[CompressionAlgorithm.ZLIB] = True
        except ImportError:
            availability[CompressionAlgorithm.ZLIB] = False
        
        try:
            import zstd
            availability[CompressionAlgorithm.ZSTD] = True
        except ImportError:
            availability[CompressionAlgorithm.ZSTD] = False
        
        try:
            import lz4.frame
            availability[CompressionAlgorithm.LZ4] = True
        except ImportError:
            availability[CompressionAlgorithm.LZ4] = False
        
        try:
            import blosc
            availability[CompressionAlgorithm.BLOSC] = True
        except ImportError:
            availability[CompressionAlgorithm.BLOSC] = False
        
        return availability
    
    def _create_default_profiles(self) -> Dict[str, CompressionProfile]:
        """Create default compression profiles"""        return {
            "fast_text": CompressionProfile(
                name="fast_text",
                algorithm=CompressionAlgorithm.LZ4,
                level=CompressionLevel.FAST,
                content_types=[ContentType.TEXT, ContentType.JSON, ContentType.XML, ContentType.LOG],
                priority_speed=True
            ),
            "high_ratio_text": CompressionProfile(
                name="high_ratio_text",
                algorithm=CompressionAlgorithm.LZMA,
                level=CompressionLevel.BEST,
                content_types=[ContentType.TEXT, ContentType.JSON, ContentType.XML],
                priority_ratio=True
            ),
            "balanced_binary": CompressionProfile(
                name="balanced_binary",
                algorithm=CompressionAlgorithm.ZSTD,
                level=CompressionLevel.BALANCED,
                content_types=[ContentType.BINARY, ContentType.DATABASE],
                min_size_threshold=4096
            ),
            "media_optimized": CompressionProfile(
                name="media_optimized",
                algorithm=CompressionAlgorithm.ZSTD,
                level=CompressionLevel.FAST,
                content_types=[ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE],
                min_size_threshold=10240
            ),
            "scientific_data": CompressionProfile(
                name="scientific_data",
                algorithm=CompressionAlgorithm.BLOSC,
                level=CompressionLevel.BALANCED,
                content_types=[ContentType.BINARY, ContentType.DATABASE],
                custom_params={"shuffle": True, "typesize": 8}
            )
        }
    
    async def compress(
        self,
        data: bytes,
        algorithm: Optional[CompressionAlgorithm] = None,
        level: Optional[CompressionLevel] = None,
        content_type: Optional[ContentType] = None,
        profile: Optional[str] = None
    ) -> CompressionResult:
        """        Compress data using specified algorithm or auto-selection
        """        start_time = time.time()
        
        try:
            # Validate input
            if not isinstance(data, bytes):
                raise CompressionException("Input data must be bytes")
            
            if len(data) == 0:
                raise CompressionException("Cannot compress empty data")
            
            original_size = len(data)
            
            # Check size threshold
            if original_size < self.config["min_compression_threshold"]:
                return CompressionResult(
                    algorithm=CompressionAlgorithm.GZIP,  # Placeholder
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=1.0,
                    compression_time=0.0,
                    data=data,
                    metadata={"skipped": "below_threshold"}
                )
            
            # Determine compression parameters
            if profile and profile in self.profiles:
                profile_obj = self.profiles[profile]
                algorithm = algorithm or profile_obj.algorithm
                level = level or profile_obj.level
                content_type = content_type or profile_obj.content_types[0]
            
            if algorithm == CompressionAlgorithm.AUTO or algorithm is None:
                algorithm = await self._select_optimal_algorithm(data, content_type)
            
            level = level or self.config["default_level"]
            
            # Perform compression
            compressed_data = await self._compress_with_algorithm(data, algorithm, level)
            
            compression_time = time.time() - start_time
            compressed_size = len(compressed_data)
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Update statistics
            await self._update_statistics(algorithm, original_size, compressed_size, compression_time)
            
            result = CompressionResult(
                algorithm=algorithm,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                data=compressed_data,
                metadata={
                    "level": level.value,
                    "content_type": content_type.value if content_type else None,
                    "profile": profile
                }
            )
            
            if self.metrics_collector:
                await self.metrics_collector.record_metric(
                    "compression_operation",
                    1,
                    tags={
                        "algorithm": algorithm.value,
                        "level": str(level.value),
                        "content_type": content_type.value if content_type else "unknown"
                    }
                )
                
                await self.metrics_collector.record_metric(
                    "compression_ratio",
                    compression_ratio,
                    tags={"algorithm": algorithm.value}
                )
            
            self.logger.debug(
                f"Compressed {original_size} bytes to {compressed_size} bytes "
                f"using {algorithm.value} (ratio: {compression_ratio:.3f})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            raise CompressionException(f"Compression failed: {e}")
    
    async def decompress(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm,
        original_size: Optional[int] = None
    ) -> bytes:
        """        Decompress data using specified algorithm
        """        try:
            if not isinstance(data, bytes):
                raise CompressionException("Input data must be bytes")
            
            if len(data) == 0:
                raise CompressionException("Cannot decompress empty data")
            
            # Perform decompression
            decompressed_data = await self._decompress_with_algorithm(data, algorithm)
            
            # Validate decompressed size if provided
            if original_size is not None and len(decompressed_data) != original_size:
                raise CompressionException(
                    f"Decompressed size mismatch: expected {original_size}, got {len(decompressed_data)}"
                )
            
            self.logger.debug(
                f"Decompressed {len(data)} bytes to {len(decompressed_data)} bytes "
                f"using {algorithm.value}"
            )
            
            return decompressed_data
            
        except Exception as e:
            self.logger.error(f"Decompression failed: {e}")
            raise CompressionException(f"Decompression failed: {e}")
    
    async def _compress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm,
        level: CompressionLevel
    ) -> bytes:
        """Compress data with specific algorithm"""        if not self.available_algorithms.get(algorithm, False):
            raise CompressionException(f"Algorithm {algorithm.value} is not available")
        
        # Run compression in thread pool for CPU-intensive operations
        loop = asyncio.get_event_loop()
        
        if algorithm == CompressionAlgorithm.GZIP:
            return await loop.run_in_executor(
                self.executor,
                lambda: gzip.compress(data, compresslevel=level.value)
            )
        
        elif algorithm == CompressionAlgorithm.BZIP2:
            return await loop.run_in_executor(
                self.executor,
                lambda: bz2.compress(data, compresslevel=level.value)
            )
        
        elif algorithm == CompressionAlgorithm.LZMA:
            return await loop.run_in_executor(
                self.executor,
                lambda: lzma.compress(data, preset=level.value)
            )
        
        elif algorithm == CompressionAlgorithm.ZLIB:
            return await loop.run_in_executor(
                self.executor,
                lambda: zlib.compress(data, level.value)
            )
        
        elif algorithm == CompressionAlgorithm.ZSTD:
            return await loop.run_in_executor(
                self.executor,
                lambda: zstd.compress(data, level.value)
            )
        
        elif algorithm == CompressionAlgorithm.LZ4:
            return await loop.run_in_executor(
                self.executor,
                lambda: lz4.frame.compress(data, compression_level=level.value)
            )
        
        elif algorithm == CompressionAlgorithm.BLOSC:
            return await loop.run_in_executor(
                self.executor,
                lambda: blosc.compress(data, clevel=level.value, shuffle=blosc.SHUFFLE)
            )
        
        else:
            raise CompressionException(f"Unsupported algorithm: {algorithm.value}")
    
    async def _decompress_with_algorithm(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm
    ) -> bytes:
        """Decompress data with specific algorithm"""        if not self.available_algorithms.get(algorithm, False):
            raise CompressionException(f"Algorithm {algorithm.value} is not available")
        
        # Run decompression in thread pool for CPU-intensive operations
        loop = asyncio.get_event_loop()
        
        if algorithm == CompressionAlgorithm.GZIP:
            return await loop.run_in_executor(
                self.executor,
                lambda: gzip.decompress(data)
            )
        
        elif algorithm == CompressionAlgorithm.BZIP2:
            return await loop.run_in_executor(
                self.executor,
                lambda: bz2.decompress(data)
            )
        
        elif algorithm == CompressionAlgorithm.LZMA:
            return await loop.run_in_executor(
                self.executor,
                lambda: lzma.decompress(data)
            )
        
        elif algorithm == CompressionAlgorithm.ZLIB:
            return await loop.run_in_executor(
                self.executor,
                lambda: zlib.decompress(data)
            )
        
        elif algorithm == CompressionAlgorithm.ZSTD:
            return await loop.run_in_executor(
                self.executor,
                lambda: zstd.decompress(data)
            )
        
        elif algorithm == CompressionAlgorithm.LZ4:
            return await loop.run_in_executor(
                self.executor,
                lambda: lz4.frame.decompress(data)
            )
        
        elif algorithm == CompressionAlgorithm.BLOSC:
            return await loop.run_in_executor(
                self.executor,
                lambda: blosc.decompress(data)
            )
        
        else:
            raise CompressionException(f"Unsupported algorithm: {algorithm.value}")
    
    async def _select_optimal_algorithm(
        self,
        data: bytes,
        content_type: Optional[ContentType] = None
    ) -> CompressionAlgorithm:
        """        Automatically select the optimal compression algorithm
        """        try:
            # Use content type hints if available
            if content_type:
                if content_type in [ContentType.TEXT, ContentType.JSON, ContentType.XML, ContentType.LOG]:
                    # Text data compresses well with LZMA or ZSTD
                    return CompressionAlgorithm.ZSTD if self.available_algorithms[CompressionAlgorithm.ZSTD] else CompressionAlgorithm.GZIP
                
                elif content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE]:
                    # Media files are often already compressed, use fast algorithm
                    return CompressionAlgorithm.LZ4 if self.available_algorithms[CompressionAlgorithm.LZ4] else CompressionAlgorithm.GZIP
                
                elif content_type == ContentType.DATABASE:
                    # Database files benefit from good compression
                    return CompressionAlgorithm.ZSTD if self.available_algorithms[CompressionAlgorithm.ZSTD] else CompressionAlgorithm.GZIP
            
            # Benchmark different algorithms on a sample
            sample_size = min(len(data), self.config["benchmark_sample_size"])
            sample_data = data[:sample_size]
            
            best_algorithm = CompressionAlgorithm.GZIP
            best_score = 0.0
            
            # Test available algorithms
            algorithms_to_test = [
                CompressionAlgorithm.GZIP,
                CompressionAlgorithm.ZSTD,
                CompressionAlgorithm.LZ4,
                CompressionAlgorithm.LZMA
            ]
            
            for algorithm in algorithms_to_test:
                if not self.available_algorithms.get(algorithm, False):
                    continue
                
                try:
                    start_time = time.time()
                    compressed = await self._compress_with_algorithm(
                        sample_data,
                        algorithm,
                        CompressionLevel.FAST
                    )
                    compression_time = time.time() - start_time
                    
                    if len(compressed) > 0:
                        compression_ratio = len(sample_data) / len(compressed)
                        speed_score = 1.0 / (compression_time + 0.001)  # Avoid division by zero
                        
                        # Combined score: ratio weight 70%, speed weight 30%
                        score = 0.7 * compression_ratio + 0.3 * speed_score
                        
                        if score > best_score:
                            best_score = score
                            best_algorithm = algorithm
                
                except Exception as e:
                    self.logger.warning(f"Failed to benchmark {algorithm.value}: {e}")
                    continue
            
            return best_algorithm
            
        except Exception as e:
            self.logger.error(f"Failed to select optimal algorithm: {e}")
            return self.config["default_algorithm"]
    
    async def benchmark_algorithms(
        self,
        data: bytes,
        algorithms: Optional[List[CompressionAlgorithm]] = None
    ) -> Dict[CompressionAlgorithm, Dict[str, float]]:
        """        Benchmark compression algorithms on given data
        """        try:
            algorithms = algorithms or list(self.available_algorithms.keys())
            results = {}
            
            for algorithm in algorithms:
                if not self.available_algorithms.get(algorithm, False):
                    continue
                
                try:
                    # Test with balanced compression level
                    start_time = time.time()
                    compressed = await self._compress_with_algorithm(
                        data,
                        algorithm,
                        CompressionLevel.BALANCED
                    )
                    compression_time = time.time() - start_time
                    
                    # Test decompression
                    start_time = time.time()
                    await self._decompress_with_algorithm(compressed, algorithm)
                    decompression_time = time.time() - start_time
                    
                    compression_ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
                    
                    results[algorithm] = {
                        "compression_ratio": compression_ratio,
                        "compression_time": compression_time,
                        "decompression_time": decompression_time,
                        "total_time": compression_time + decompression_time,
                        "compressed_size": len(compressed),
                        "space_saved": len(data) - len(compressed)
                    }
                
                except Exception as e:
                    self.logger.warning(f"Benchmark failed for {algorithm.value}: {e}")
                    results[algorithm] = {"error": str(e)}
            
            return results
            
        except Exception as e:
            self.logger.error(f"Benchmarking failed: {e}")
            return {}
    
    async def compress_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        algorithm: Optional[CompressionAlgorithm] = None,
        level: Optional[CompressionLevel] = None,
        chunk_size: Optional[int] = None
    ) -> CompressionResult:
        """        Compress a file with chunked processing for large files
        """        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise CompressionException(f"Input file does not exist: {input_path}")
            
            output_path = Path(output_path) if output_path else input_path.with_suffix(input_path.suffix + '.compressed')
            chunk_size = chunk_size or self.config["chunk_size"]
            
            file_size = input_path.stat().st_size
            
            if file_size > self.config["max_file_size"]:
                raise CompressionException(f"File too large: {file_size} bytes (max: {self.config['max_file_size']})")
            
            # For small files, read entirely into memory
            if file_size <= chunk_size:
                async with aiofiles.open(input_path, 'rb') as f:
                    data = await f.read()
                
                result = await self.compress(data, algorithm, level)
                
                async with aiofiles.open(output_path, 'wb') as f:
                    await f.write(result.data)
                
                return result
            
            # For large files, use chunked compression
            return await self._compress_file_chunked(
                input_path,
                output_path,
                algorithm,
                level,
                chunk_size
            )
            
        except Exception as e:
            self.logger.error(f"File compression failed: {e}")
            raise CompressionException(f"File compression failed: {e}")
    
    async def _compress_file_chunked(
        self,
        input_path: Path,
        output_path: Path,
        algorithm: Optional[CompressionAlgorithm],
        level: Optional[CompressionLevel],
        chunk_size: int
    ) -> CompressionResult:
        """Compress large file in chunks"""        start_time = time.time()
        original_size = 0
        compressed_size = 0
        
        # Determine algorithm
        if algorithm == CompressionAlgorithm.AUTO or algorithm is None:
            # Read sample for algorithm selection
            async with aiofiles.open(input_path, 'rb') as f:
                sample = await f.read(self.config["benchmark_sample_size"])
                algorithm = await self._select_optimal_algorithm(sample)
        
        level = level or self.config["default_level"]
        
        try:
            async with aiofiles.open(input_path, 'rb') as input_file:
                async with aiofiles.open(output_path, 'wb') as output_file:
                    while True:
                        chunk = await input_file.read(chunk_size)
                        if not chunk:
                            break
                        
                        original_size += len(chunk)
                        
                        # Compress chunk
                        compressed_chunk = await self._compress_with_algorithm(chunk, algorithm, level)
                        compressed_size += len(compressed_chunk)
                        
                        # Write compressed chunk size and data
                        await output_file.write(len(compressed_chunk).to_bytes(4, 'big'))
                        await output_file.write(compressed_chunk)
            
            compression_time = time.time() - start_time
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            # Update statistics
            await self._update_statistics(algorithm, original_size, compressed_size, compression_time)
            
            return CompressionResult(
                algorithm=algorithm,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                data=b'',  # Data is in file
                metadata={
                    "level": level.value,
                    "chunked": True,
                    "chunk_size": chunk_size,
                    "output_file": str(output_path)
                }
            )
            
        except Exception as e:
            # Clean up partial file on error
            if output_path.exists():
                output_path.unlink()
            raise
    
    async def decompress_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        algorithm: CompressionAlgorithm = CompressionAlgorithm.AUTO,
        chunked: bool = False
    ) -> int:
        """        Decompress a file
        """        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise CompressionException(f"Input file does not exist: {input_path}")
            
            output_path = Path(output_path) if output_path else input_path.with_suffix('')
            
            if chunked:
                return await self._decompress_file_chunked(input_path, output_path, algorithm)
            
            # Simple file decompression
            async with aiofiles.open(input_path, 'rb') as f:
                compressed_data = await f.read()
            
            decompressed_data = await self.decompress(compressed_data, algorithm)
            
            async with aiofiles.open(output_path, 'wb') as f:
                await f.write(decompressed_data)
            
            return len(decompressed_data)
            
        except Exception as e:
            self.logger.error(f"File decompression failed: {e}")
            raise CompressionException(f"File decompression failed: {e}")
    
    async def _decompress_file_chunked(
        self,
        input_path: Path,
        output_path: Path,
        algorithm: CompressionAlgorithm
    ) -> int:
        """Decompress chunked file"""        total_size = 0
        
        try:
            async with aiofiles.open(input_path, 'rb') as input_file:
                async with aiofiles.open(output_path, 'wb') as output_file:
                    while True:
                        # Read chunk size
                        size_bytes = await input_file.read(4)
                        if len(size_bytes) < 4:
                            break
                        
                        chunk_size = int.from_bytes(size_bytes, 'big')
                        
                        # Read compressed chunk
                        compressed_chunk = await input_file.read(chunk_size)
                        if len(compressed_chunk) < chunk_size:
                            break
                        
                        # Decompress chunk
                        decompressed_chunk = await self._decompress_with_algorithm(
                            compressed_chunk,
                            algorithm
                        )
                        
                        total_size += len(decompressed_chunk)
                        await output_file.write(decompressed_chunk)
            
            return total_size
            
        except Exception as e:
            # Clean up partial file on error
            if output_path.exists():
                output_path.unlink()
            raise
    
    async def _update_statistics(
        self,
        algorithm: CompressionAlgorithm,
        original_size: int,
        compressed_size: int,
        compression_time: float
    ):
        """Update compression statistics"""        self.compression_stats["total_operations"] += 1
        self.compression_stats["total_original_size"] += original_size
        self.compression_stats["total_compressed_size"] += compressed_size
        self.compression_stats["total_time"] += compression_time
        
        if algorithm.value not in self.compression_stats["algorithm_usage"]:
            self.compression_stats["algorithm_usage"][algorithm.value] = 0
        self.compression_stats["algorithm_usage"][algorithm.value] += 1
        
        # Update average ratio
        if self.compression_stats["total_original_size"] > 0:
            self.compression_stats["average_ratio"] = (
                self.compression_stats["total_compressed_size"] / 
                self.compression_stats["total_original_size"]
            )
    
    def add_profile(self, profile: CompressionProfile):
        """Add a custom compression profile"""        self.profiles[profile.name] = profile
        self.logger.info(f"Added compression profile: {profile.name}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get compression engine statistics"""        return {
            "statistics": self.compression_stats.copy(),
            "available_algorithms": {
                alg.value: available for alg, available in self.available_algorithms.items()
            },
            "profiles": {
                name: {
                    "algorithm": profile.algorithm.value,
                    "level": profile.level.value,
                    "content_types": [ct.value for ct in profile.content_types]
                }
                for name, profile in self.profiles.items()
            },
            "configuration": self.config
        }
    
    async def close(self):
        """Close compression engine and cleanup resources"""        self.executor.shutdown(wait=True)
        self.logger.info("Compression engine closed")


# Global compression engine instance
_compression_engine: Optional[CompressionEngine] = None


async def get_compression_engine(
    config: Optional[Dict[str, Any]] = None,
    metrics_collector: Optional[MetricsCollector] = None,
    max_workers: int = 4
) -> CompressionEngine:
    """Get or create compression engine instance"""    global _compression_engine
    
    if _compression_engine is None:
        _compression_engine = CompressionEngine(
            config=config,
            metrics_collector=metrics_collector,
            max_workers=max_workers
        )
    
    return _compression_engine


# Utility functions for common compression tasks
async def compress_text(
    text: str,
    algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD
) -> CompressionResult:
    """Compress text data"""    engine = await get_compression_engine()
    return await engine.compress(
        text.encode('utf-8'),
        algorithm=algorithm,
        content_type=ContentType.TEXT
    )


async def compress_json(
    data: Dict[str, Any],
    algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD
) -> CompressionResult:
    """Compress JSON data"""    import json
    engine = await get_compression_engine()
    json_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
    return await engine.compress(
        json_bytes,
        algorithm=algorithm,
        content_type=ContentType.JSON
    )


async def compress_binary(
    data: bytes,
    algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD
) -> CompressionResult:
    """Compress binary data"""    engine = await get_compression_engine()
    return await engine.compress(
        data,
        algorithm=algorithm,
        content_type=ContentType.BINARY
    )
