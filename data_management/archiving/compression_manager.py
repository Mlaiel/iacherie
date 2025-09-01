"""Archival Compression Management Module

Advanced compression management for archived content with support for multiple
compression algorithms, adaptive compression strategies, and performance optimization
for different content types (audio, video, image, text).

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import zlib
import lzma
import bz2
import gzip
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json

from .exceptions import CompressionError


logger = logging.getLogger(__name__)


class CompressionMethod(Enum):
    """
Supported compression methods"""

    GZIP = "gzip"
    ZLIB = "zlib"
    LZMA = "lzma"
    BZIP2 = "bzip2"
    ADAPTIVE = "adaptive"
    NONE = "none"


class CompressionLevel(Enum):
    """Compression level settings"""

    FAST = 1
    BALANCED = 6
    BEST = 9
    ADAPTIVE = -1


class ContentType(Enum):
    """
Content types for compression optimization"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    BINARY = "binary"
    MIXED = "mixed"


@dataclass
class CompressionMetrics:
    """Compression performance metrics"""
    method: CompressionMethod
    level: int
    
    # Size metrics
    original_size: int
    compressed_size: int
    compression_ratio: float
    space_saved_bytes: int
    space_saved_percentage: float
    
    # Performance metrics
    compression_time_ms: float
    decompression_time_ms: Optional[float] = None
    throughput_mbps: float = 0.0
    
    # Quality metrics
    integrity_hash: str = ""
    quality_score: float = 1.0
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Calculate derived metrics"""
        if self.original_size > 0:
            self.compression_ratio = self.compressed_size / self.original_size
            self.space_saved_bytes = self.original_size - self.compressed_size
            self.space_saved_percentage = (self.space_saved_bytes / self.original_size) * 100
        
        if self.compression_time_ms > 0:
            self.throughput_mbps = (self.original_size / (1024**2)) / (self.compression_time_ms / 1000)


@dataclass
class CompressionProfile:
    """
Compression profile for specific content types"""
    profile_id: str
    name: str
    content_type: ContentType
    
    # Method preferences
    primary_method: CompressionMethod
    fallback_methods: List[CompressionMethod] = field(default_factory=list)
    
    # Level configuration
    default_level: CompressionLevel = CompressionLevel.BALANCED
    quality_threshold: float = 0.95
    
    # Performance constraints
    max_compression_time_seconds: Optional[float] = None
    min_compression_ratio: float = 0.1
    
    # Adaptive settings
    adaptive_enabled: bool = True
    learning_enabled: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class CompressionAlgorithm(ABC):
    """
Abstract base for compression algorithms"""
    
    @abstractmethod
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        """
Compress data"""
        pass
    
    @abstractmethod
    async def decompress(self, data: bytes) -> bytes:
        """
Decompress data"""
        pass
    
    @abstractmethod
    def get_optimal_level(self, content_type: ContentType, size: int) -> int:
        """
Get optimal compression level for content"""
        pass


class GzipCompressionAlgorithm(CompressionAlgorithm):
    """
GZIP compression implementation"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        """
Compress using GZIP"""
        return gzip.compress(data, compresslevel=level)
    
    async def decompress(self, data: bytes) -> bytes:
        """
Decompress GZIP data"""
        return gzip.decompress(data)
    
    def get_optimal_level(self, content_type: ContentType, size: int) -> int:
        """
Get optimal GZIP level"""
        if content_type == ContentType.TEXT:
            return 9  # Best compression for text
        elif content_type in [ContentType.AUDIO, ContentType.VIDEO]:
            return 1  # Fast compression for media
        else:
            return 6  # Balanced for other types


class ZlibCompressionAlgorithm(CompressionAlgorithm):
    """
ZLIB compression implementation"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        """
Compress using ZLIB"""
        return zlib.compress(data, level=level)
    
    async def decompress(self, data: bytes) -> bytes:
        """
Decompress ZLIB data"""
        return zlib.decompress(data)
    
    def get_optimal_level(self, content_type: ContentType, size: int) -> int:
        """
Get optimal ZLIB level"""
        if size < 1024:  # Small files
            return 1
        elif size > 100 * 1024**2:  # Large files
            return 3
        else:
            return 6


class LzmaCompressionAlgorithm(CompressionAlgorithm):
    """
LZMA compression implementation"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        """
Compress using LZMA"""
        return lzma.compress(data, preset=level)
    
    async def decompress(self, data: bytes) -> bytes:
        """
Decompress LZMA data"""
        return lzma.decompress(data)
    
    def get_optimal_level(self, content_type: ContentType, size: int) -> int:
        """
Get optimal LZMA level"""
        if content_type == ContentType.TEXT:
            return 9  # Best compression for text
        else:
            return 6


class Bzip2CompressionAlgorithm(CompressionAlgorithm):
    """
BZIP2 compression implementation"""
    
    async def compress(self, data: bytes, level: int = 6) -> bytes:
        """
Compress using BZIP2"""
        return bz2.compress(data, compresslevel=level)
    
    async def decompress(self, data: bytes) -> bytes:
        """
Decompress BZIP2 data"""
        return bz2.decompress(data)
    
    def get_optimal_level(self, content_type: ContentType, size: int) -> int:
        """
Get optimal BZIP2 level"""
        return 9  # BZIP2 is best at highest level


class AdaptiveCompressionStrategy:
    """
Adaptive compression strategy selector"""
    
    def __init__(self):
        self.performance_history: Dict[str, List[CompressionMetrics]] = {}
        self.content_profiles: Dict[ContentType, CompressionProfile] = {}
        self._initialize_default_profiles()
    
    def _initialize_default_profiles(self):
        """
Initialize default compression profiles"""
        self.content_profiles = {
            ContentType.TEXT: CompressionProfile(
                profile_id="text_default",
                name="Text Optimized",
                content_type=ContentType.TEXT,
                primary_method=CompressionMethod.LZMA,
                fallback_methods=[CompressionMethod.GZIP, CompressionMethod.ZLIB]
            ),
            ContentType.AUDIO: CompressionProfile(
                profile_id="audio_default",
                name="Audio Optimized",
                content_type=ContentType.AUDIO,
                primary_method=CompressionMethod.GZIP,
                fallback_methods=[CompressionMethod.ZLIB]
            ),
            ContentType.VIDEO: CompressionProfile(
                profile_id="video_default",
                name="Video Optimized",
                content_type=ContentType.VIDEO,
                primary_method=CompressionMethod.ZLIB,
                fallback_methods=[CompressionMethod.GZIP]
            ),
            ContentType.IMAGE: CompressionProfile(
                profile_id="image_default",
                name="Image Optimized",
                content_type=ContentType.IMAGE,
                primary_method=CompressionMethod.GZIP,
                fallback_methods=[CompressionMethod.ZLIB, CompressionMethod.LZMA]
            ),
            ContentType.BINARY: CompressionProfile(
                profile_id="binary_default",
                name="Binary Optimized",
                content_type=ContentType.BINARY,
                primary_method=CompressionMethod.LZMA,
                fallback_methods=[CompressionMethod.BZIP2, CompressionMethod.GZIP]
            )
        }
    
    async def select_method(self, content_type: ContentType, data_size: int) -> Tuple[CompressionMethod, int]:
        """Select optimal compression method and level"""
        profile = self.content_profiles.get(content_type, self.content_profiles[ContentType.BINARY])
        
        # Check performance history for this content type
        if profile.adaptive_enabled and content_type.value in self.performance_history:
            return await self._select_adaptive_method(content_type, data_size)
        
        # Use default profile settings
        method = profile.primary_method
        level = self._get_level_value(profile.default_level)
        
        return method, level
    
    async def _select_adaptive_method(self, content_type: ContentType, data_size: int) -> Tuple[CompressionMethod, int]:
        """
Select method based on performance history"""
        history = self.performance_history[content_type.value]
        
        # Find best performing method for similar data sizes
        size_tolerance = 0.2  # 20% size tolerance
        min_size = data_size * (1 - size_tolerance)
        max_size = data_size * (1 + size_tolerance)
        
        relevant_metrics = [
            m for m in history
            if min_size <= m.original_size <= max_size
        ]
        
        if not relevant_metrics:
            # No relevant history, use default
            profile = self.content_profiles[content_type]
            return profile.primary_method, self._get_level_value(profile.default_level)
        
        # Score methods based on compression ratio and speed
        method_scores = {}
        for metric in relevant_metrics:
            score = (1 - metric.compression_ratio) * 0.7 + (metric.throughput_mbps / 100) * 0.3
            
            if metric.method not in method_scores:
                method_scores[metric.method] = []
            method_scores[metric.method].append(score)
        
        # Select method with highest average score
        best_method = None
        best_score = 0
        
        for method, scores in method_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_method = method
        
        # Find optimal level for best method
        method_metrics = [m for m in relevant_metrics if m.method == best_method]
        if method_metrics:
            # Use level with best compression ratio
            best_metric = max(method_metrics, key=lambda m: 1 - m.compression_ratio)
            return best_method, best_metric.level
        
        return best_method or CompressionMethod.GZIP, 6
    
    def _get_level_value(self, level: CompressionLevel) -> int:
        """
Convert compression level enum to integer"""
        if level == CompressionLevel.FAST:
            return 1
        elif level == CompressionLevel.BALANCED:
            return 6
        elif level == CompressionLevel.BEST:
            return 9
        else:  # ADAPTIVE
            return 6
    
    async def record_performance(self, metrics: CompressionMetrics):
        """
Record compression performance for future optimization"""
        content_key = "unknown"  # In real implementation, derive from context
        
        if content_key not in self.performance_history:
            self.performance_history[content_key] = []
        
        self.performance_history[content_key].append(metrics)
        
        # Keep only recent history (last 100 entries)
        if len(self.performance_history[content_key]) > 100:
            self.performance_history[content_key] = self.performance_history[content_key][-100:]


class ArchivalCompressionManager:
    """
    Advanced compression management for archival content.
    
    Provides intelligent compression with adaptive algorithm selection,
    performance optimization, and content-type specific strategies.
    """
    
    def __init__(self):
        self.algorithms = {
            CompressionMethod.GZIP: GzipCompressionAlgorithm(),
            CompressionMethod.ZLIB: ZlibCompressionAlgorithm(),
            CompressionMethod.LZMA: LzmaCompressionAlgorithm(),
            CompressionMethod.BZIP2: Bzip2CompressionAlgorithm()
        }
        
        self.adaptive_strategy = AdaptiveCompressionStrategy()
        self.compression_cache: Dict[str, bytes] = {}
        
        # Configuration
        self.cache_enabled = True
        self.max_cache_size = 100 * 1024**2  # 100MB
        self.current_cache_size = 0
        
        logger.info("Archival Compression Manager initialized")
    
    async def compress_content(
        self,
        data: bytes,
        content_type: ContentType = ContentType.BINARY,
        method: Optional[CompressionMethod] = None,
        level: Optional[int] = None
    ) -> Tuple[bytes, CompressionMetrics]:
        """
        Compress content with optimal settings.
        
        Args:
            data: Raw content data
            content_type: Type of content for optimization
            method: Specific compression method (optional)
            level: Compression level (optional)
            
        Returns:
            Tuple of compressed data and metrics
        """
        try:
            start_time = datetime.utcnow()
            
            # Generate cache key
            cache_key = self._generate_cache_key(data, content_type, method, level)
            
            # Check cache
            if self.cache_enabled and cache_key in self.compression_cache:
                logger.debug(f"Using cached compression for key: {cache_key[:16]}...")
                # Return cached result (simplified - in real implementation, return full metrics)
                return self.compression_cache[cache_key], CompressionMetrics(
                    method=method or CompressionMethod.GZIP,
                    level=level or 6,
                    original_size=len(data),
                    compressed_size=len(self.compression_cache[cache_key]),
                    compression_time_ms=0.1  # Cache hit is very fast
                )
            
            # Select optimal method and level
            if method is None or level is None:
                selected_method, selected_level = await self.adaptive_strategy.select_method(
                    content_type, len(data)
                )
                method = method or selected_method
                level = level or selected_level
            
            # Perform compression
            if method == CompressionMethod.NONE:
                compressed_data = data
            elif method == CompressionMethod.ADAPTIVE:
                compressed_data, method = await self._compress_adaptive(data, content_type, level)
            else:
                algorithm = self.algorithms.get(method)
                if not algorithm:
                    raise CompressionError(f"Unsupported compression method: {method}")
                
                compressed_data = await algorithm.compress(data, level)
            
            # Calculate metrics
            end_time = datetime.utcnow()
            compression_time = (end_time - start_time).total_seconds() * 1000
            
            metrics = CompressionMetrics(
                method=method,
                level=level,
                original_size=len(data),
                compressed_size=len(compressed_data),
                compression_time_ms=compression_time,
                integrity_hash=hashlib.sha256(data).hexdigest()
            )
            
            # Cache result if beneficial
            if self.cache_enabled and self._should_cache(metrics):
                await self._cache_result(cache_key, compressed_data)
            
            # Record performance for adaptive learning
            await self.adaptive_strategy.record_performance(metrics)
            
            logger.info(f"Compressed {len(data)} bytes to {len(compressed_data)} bytes "
                       f"({metrics.compression_ratio:.2%} ratio) using {method.value}")
            
            return compressed_data, metrics
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            raise CompressionError(f"Failed to compress content: {e}")
    
    async def decompress_content(
        self,
        compressed_data: bytes,
        method: CompressionMethod,
        verify_integrity: bool = True,
        expected_hash: Optional[str] = None
    ) -> Tuple[bytes, float]:
        """
        Decompress content and verify integrity.
        
        Args:
            compressed_data: Compressed content data
            method: Compression method used
            verify_integrity: Whether to verify data integrity
            expected_hash: Expected SHA256 hash for verification
            
        Returns:
            Tuple of decompressed data and decompression time
        """
        try:
            start_time = datetime.utcnow()
            
            # Decompress data
            if method == CompressionMethod.NONE:
                decompressed_data = compressed_data
            else:
                algorithm = self.algorithms.get(method)
                if not algorithm:
                    raise CompressionError(f"Unsupported compression method: {method}")
                
                decompressed_data = await algorithm.decompress(compressed_data)
            
            # Calculate decompression time
            end_time = datetime.utcnow()
            decompression_time = (end_time - start_time).total_seconds() * 1000
            
            # Verify integrity if requested
            if verify_integrity and expected_hash:
                actual_hash = hashlib.sha256(decompressed_data).hexdigest()
                if actual_hash != expected_hash:
                    raise CompressionError(f"Integrity check failed: {actual_hash} != {expected_hash}")
            
            logger.info(f"Decompressed {len(compressed_data)} bytes to {len(decompressed_data)} bytes "
                       f"in {decompression_time:.2f}ms using {method.value}")
            
            return decompressed_data, decompression_time
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            raise CompressionError(f"Failed to decompress content: {e}")
    
    async def analyze_compression_efficiency(
        self,
        data: bytes,
        content_type: ContentType = ContentType.BINARY
    ) -> Dict[CompressionMethod, CompressionMetrics]:
        """
        Analyze compression efficiency across all methods.
        
        Args:
            data: Content to analyze
            content_type: Type of content
            
        Returns:
            Dictionary mapping methods to their metrics
        """
        try:
            results = {}
            
            for method in CompressionMethod:
                if method in [CompressionMethod.ADAPTIVE, CompressionMethod.NONE]:
                    continue
                
                try:
                    # Test compression with method
                    compressed_data, metrics = await self.compress_content(
                        data, content_type, method, 6  # Use balanced level
                    )
                    results[method] = metrics
                    
                except Exception as e:
                    logger.warning(f"Failed to test {method.value}: {e}")
                    continue
            
            # Sort by compression ratio (best first)
            sorted_results = dict(sorted(
                results.items(),
                key=lambda x: x[1].compression_ratio
            ))
            
            logger.info(f"Analyzed compression for {len(data)} bytes across {len(results)} methods")
            return sorted_results
            
        except Exception as e:
            logger.error(f"Compression analysis failed: {e}")
            return {}
    
    async def optimize_compression_profile(
        self,
        content_type: ContentType,
        sample_data: List[bytes]
    ) -> CompressionProfile:
        """
        Optimize compression profile for a content type using sample data.
        
        Args:
            content_type: Content type to optimize
            sample_data: List of sample data for testing
            
        Returns:
            Optimized compression profile
        """
        try:
            method_performance = {}
            
            # Test each method on sample data
            for method in CompressionMethod:
                if method in [CompressionMethod.ADAPTIVE, CompressionMethod.NONE]:
                    continue
                
                method_metrics = []
                
                for sample in sample_data[:10]:  # Limit to 10 samples
                    try:
                        _, metrics = await self.compress_content(sample, content_type, method, 6)
                        method_metrics.append(metrics)
                    except Exception:
                        continue
                
                if method_metrics:
                    # Calculate average performance
                    avg_ratio = sum(m.compression_ratio for m in method_metrics) / len(method_metrics)
                    avg_speed = sum(m.throughput_mbps for m in method_metrics) / len(method_metrics)
                    
                    method_performance[method] = {
                        'compression_ratio': avg_ratio,
                        'throughput_mbps': avg_speed,
                        'score': (1 - avg_ratio) * 0.7 + (avg_speed / 100) * 0.3
                    }
            
            # Select best method
            if not method_performance:
                # Fallback to default
                return CompressionProfile(
                    profile_id=f"{content_type.value}_optimized",
                    name=f"{content_type.value.title()} Optimized",
                    content_type=content_type,
                    primary_method=CompressionMethod.GZIP
                )
            
            best_method = max(method_performance.keys(), key=lambda m: method_performance[m]['score'])
            
            # Create optimized profile
            profile = CompressionProfile(
                profile_id=f"{content_type.value}_optimized",
                name=f"{content_type.value.title()} Optimized",
                content_type=content_type,
                primary_method=best_method,
                fallback_methods=[
                    m for m, perf in sorted(
                        method_performance.items(),
                        key=lambda x: x[1]['score'],
                        reverse=True
                    )[1:4]  # Top 3 alternatives
                ]
            )
            
            logger.info(f"Optimized compression profile for {content_type.value}: "
                       f"primary={best_method.value}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Profile optimization failed: {e}")
            # Return default profile
            return CompressionProfile(
                profile_id=f"{content_type.value}_default",
                name=f"{content_type.value.title()} Default",
                content_type=content_type,
                primary_method=CompressionMethod.GZIP
            )
    
    async def get_compression_stats(self) -> Dict[str, Any]:
        """Get comprehensive compression statistics"""
        try:
            total_compressions = 0
            total_original_size = 0
            total_compressed_size = 0
            method_usage = {}
            
            # Aggregate statistics from performance history
            for content_type, history in self.adaptive_strategy.performance_history.items():
                for metrics in history:
                    total_compressions += 1
                    total_original_size += metrics.original_size
                    total_compressed_size += metrics.compressed_size
                    
                    method = metrics.method.value
                    if method not in method_usage:
                        method_usage[method] = 0
                    method_usage[method] += 1
            
            overall_ratio = total_compressed_size / total_original_size if total_original_size > 0 else 0
            space_saved = total_original_size - total_compressed_size
            
            return {
                "total_compressions": total_compressions,
                "total_original_size_bytes": total_original_size,
                "total_compressed_size_bytes": total_compressed_size,
                "overall_compression_ratio": overall_ratio,
                "space_saved_bytes": space_saved,
                "space_saved_percentage": (space_saved / total_original_size * 100) if total_original_size > 0 else 0,
                "method_usage": method_usage,
                "cache_size_bytes": self.current_cache_size,
                "cache_hit_rate": 0.0,  # Simplified
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get compression stats: {e}")
            return {}
    
    async def _compress_adaptive(
        self,
        data: bytes,
        content_type: ContentType,
        level: int
    ) -> Tuple[bytes, CompressionMethod]:
        """Compress using adaptive method selection"""
        # Test multiple methods and select the best one
        best_compressed = data
        best_method = CompressionMethod.NONE
        best_ratio = 1.0
        
        test_methods = [CompressionMethod.GZIP, CompressionMethod.ZLIB, CompressionMethod.LZMA]
        
        for method in test_methods:
            try:
                algorithm = self.algorithms[method]
                compressed = await algorithm.compress(data, level)
                ratio = len(compressed) / len(data)
                
                if ratio < best_ratio:
                    best_compressed = compressed
                    best_method = method
                    best_ratio = ratio
                    
            except Exception:
                continue
        
        return best_compressed, best_method
    
    def _generate_cache_key(
        self,
        data: bytes,
        content_type: ContentType,
        method: Optional[CompressionMethod],
        level: Optional[int]
    ) -> str:
        """
Generate cache key for compression result"""
        content_hash = hashlib.sha256(data).hexdigest()
        method_str = method.value if method else "auto"
        level_str = str(level) if level else "auto"
        
        return f"{content_hash}_{content_type.value}_{method_str}_{level_str}"
    
    def _should_cache(self, metrics: CompressionMetrics) -> bool:
        """Determine if compression result should be cached"""
        # Cache if good compression ratio and reasonable size
        return (
            metrics.compression_ratio < 0.8 and  # Good compression
            metrics.compressed_size < 10 * 1024**2 and  # Not too large (10MB)
            self.current_cache_size + metrics.compressed_size < self.max_cache_size
        )
    
    async def _cache_result(self, cache_key: str, compressed_data: bytes):
        """
Cache compression result"""
        if cache_key not in self.compression_cache:
            self.compression_cache[cache_key] = compressed_data
            self.current_cache_size += len(compressed_data)
            
            # Evict old entries if cache is full
            while self.current_cache_size > self.max_cache_size and self.compression_cache:
                # Remove oldest entry (simplified LRU)
                oldest_key = next(iter(self.compression_cache))
                old_data = self.compression_cache.pop(oldest_key)
                self.current_cache_size -= len(old_data)
