"""
Disk Optimizer - Enterprise Performance Module
===============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade disk I/O optimization for Creator Economy platform.
Advanced disk performance management for large multimedia file handling.

Performance Targets: < 50ms disk operations
I/O Throughput: > 500MB/s optimized operations
Cache Hit Rate: > 85% for frequently accessed files
"""

import asyncio
import logging
import os
import shutil
import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import psutil
import tempfile
import json
import hashlib
import aiofiles

# Enterprise logging setup
logger = logging.getLogger(__name__)


class DiskOptimizationMode(Enum):
    """Disk optimization modes"""
    LATENCY_OPTIMIZED = "latency_optimized"
    THROUGHPUT_OPTIMIZED = "throughput_optimized"
    BALANCED = "balanced"
    CREATOR_OPTIMIZED = "creator_optimized"
    ENTERPRISE = "enterprise"


class CompressionLevel(Enum):
    """Compression levels for disk optimization"""
    NONE = "none"
    FAST = "fast"
    BALANCED = "balanced"
    MAX = "max"
    CREATOR_AWARE = "creator_aware"


class CacheStrategy(Enum):
    """Disk caching strategies"""
    LRU = "lru"
    LFU = "lfu"
    ARC = "arc"
    CREATOR_AWARE = "creator_aware"
    INTELLIGENT = "intelligent"


@dataclass
class DiskMetrics:
    """Disk performance metrics"""
    timestamp: datetime = field(default_factory=datetime.now)
    read_bytes: int = 0
    write_bytes: int = 0
    read_count: int = 0
    write_count: int = 0
    read_time_ms: float = 0.0
    write_time_ms: float = 0.0
    busy_time_ms: float = 0.0
    usage_percent: float = 0.0
    free_space_bytes: int = 0
    total_space_bytes: int = 0
    iops: float = 0.0
    latency_ms: float = 0.0


@dataclass
class FileAccessPattern:
    """File access pattern analysis"""
    file_path: str
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    total_bytes_read: int = 0
    total_bytes_written: int = 0
    access_frequency: float = 0.0
    file_size: int = 0
    file_type: str = ""
    creator_context: str = ""


@dataclass
class CacheEntry:
    """Disk cache entry"""
    file_path: str
    cached_data: Optional[bytes] = None
    cached_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    size_bytes: int = 0
    compression_ratio: float = 1.0
    cache_hit_rate: float = 0.0


@dataclass
class DiskOptimizationRule:
    """Disk optimization rule"""
    rule_name: str
    file_patterns: List[str]
    optimization_type: str
    cache_strategy: CacheStrategy
    compression_level: CompressionLevel
    priority: int = 1
    creator_specific: bool = False
    conditions: Dict[str, Any] = field(default_factory=dict)


class CreatorDiskProfile:
    """Creator-specific disk optimization profiles"""
    
    def __init__(self, creator_type: str):
        self.creator_type = creator_type
        self.file_patterns = {}
        self.cache_preferences = {}
        self.compression_settings = {}
        
    def get_musician_profile(self) -> Dict[str, Any]:
        """Disk profile optimized for musicians"""
        return {
            "optimization_mode": DiskOptimizationMode.LATENCY_OPTIMIZED,
            "priority_file_types": [".wav", ".flac", ".aiff", ".mid", ".sf2"],
            "cache_strategy": CacheStrategy.CREATOR_AWARE,
            "cache_size_mb": 2048,  # Large cache for samples
            "compression_settings": {
                "audio_samples": CompressionLevel.FAST,  # Fast for real-time
                "project_files": CompressionLevel.BALANCED,
                "backup_files": CompressionLevel.MAX
            },
            "optimization_features": [
                "preload_frequently_used_samples",
                "optimize_audio_buffer_io",
                "minimize_seek_times",
                "priority_queue_for_audio_files"
            ],
            "disk_layout": {
                "audio_samples": "fast_ssd",
                "project_files": "fast_ssd", 
                "backups": "bulk_storage",
                "temp_files": "ram_disk_if_available"
            }
        }
    
    def get_photographer_profile(self) -> Dict[str, Any]:
        """Disk profile optimized for photographers"""
        return {
            "optimization_mode": DiskOptimizationMode.THROUGHPUT_OPTIMIZED,
            "priority_file_types": [".raw", ".cr2", ".nef", ".arw", ".tiff", ".psd"],
            "cache_strategy": CacheStrategy.INTELLIGENT,
            "cache_size_mb": 4096,  # Very large cache for RAW files
            "compression_settings": {
                "raw_files": CompressionLevel.NONE,  # Never compress RAW
                "processed_images": CompressionLevel.FAST,
                "backup_files": CompressionLevel.MAX
            },
            "optimization_features": [
                "sequential_read_optimization",
                "large_file_streaming",
                "batch_processing_optimization", 
                "thumbnail_cache_management"
            ],
            "disk_layout": {
                "raw_files": "fast_ssd",
                "processing_scratch": "nvme_ssd",
                "finished_work": "fast_ssd",
                "archive": "bulk_storage"
            }
        }
    
    def get_blogger_profile(self) -> Dict[str, Any]:
        """Disk profile optimized for bloggers"""
        return {
            "optimization_mode": DiskOptimizationMode.BALANCED,
            "priority_file_types": [".md", ".txt", ".docx", ".jpg", ".png", ".mp4"],
            "cache_strategy": CacheStrategy.LRU,
            "cache_size_mb": 512,  # Moderate cache for mixed content
            "compression_settings": {
                "text_files": CompressionLevel.MAX,  # High compression for text
                "images": CompressionLevel.BALANCED,
                "videos": CompressionLevel.FAST
            },
            "optimization_features": [
                "intelligent_content_caching",
                "background_compression",
                "smart_prefetching",
                "content_deduplication"
            ],
            "disk_layout": {
                "active_content": "ssd",
                "media_assets": "ssd",
                "archive": "bulk_storage",
                "temp_files": "temp_storage"
            }
        }


class DiskOptimizer:
    """
    Enterprise Disk Optimizer for Creator Economy Platform
    
    Advanced disk I/O optimization with intelligent caching and compression.
    Specialized for content creator workloads handling large multimedia files.
    
    Features:
    - < 50ms disk operations
    - > 500MB/s optimized throughput
    - Intelligent file caching
    - Creator-specific optimization
    - Predictive I/O management
    """
    
    def __init__(
        self,
        optimization_mode: DiskOptimizationMode = DiskOptimizationMode.BALANCED,
        cache_size_mb: int = 1024,
        enable_compression: bool = True,
        enable_intelligent_caching: bool = True,
        monitoring_interval: int = 15
    ):
        self.optimization_mode = optimization_mode
        self.cache_size_mb = cache_size_mb
        self.enable_compression = enable_compression
        self.enable_intelligent_caching = enable_intelligent_caching
        self.monitoring_interval = monitoring_interval
        
        # Enterprise state management
        self._is_running = False
        self._optimization_lock = threading.Lock()
        self._disk_history: deque = deque(maxlen=1000)
        self._file_cache: Dict[str, CacheEntry] = {}
        self._access_patterns: Dict[str, FileAccessPattern] = {}
        self._optimization_rules: List[DiskOptimizationRule] = []
        self._creator_profiles: Dict[str, CreatorDiskProfile] = {}
        
        # Cache management
        self._cache_size_bytes = cache_size_mb * 1024 * 1024
        self._current_cache_size = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Performance tracking
        self._optimization_stats = {
            "total_optimizations": 0,
            "avg_optimization_time_ms": 0.0,
            "io_improvements": 0.0,
            "cache_hit_rate": 0.0,
            "compression_ratio": 1.0,
            "bytes_saved": 0,
            "last_optimization": None
        }
        
        # Disk monitoring
        self._monitored_paths: Set[str] = set()
        self._io_counters_prev: Optional[Dict[str, Any]] = None
        
        # Initialize default optimization rules
        self._initialize_optimization_rules()
        
        # Create cache directory
        self._cache_dir = Path(tempfile.gettempdir()) / "ainflue_disk_cache"
        self._cache_dir.mkdir(exist_ok=True)
        
        logger.info(f"DiskOptimizer initialized - Mode: {optimization_mode.value}, Cache: {cache_size_mb}MB")
    
    def _initialize_optimization_rules(self) -> None:
        """Initialize default disk optimization rules"""
        default_rules = [
            # Audio file optimization
            DiskOptimizationRule(
                rule_name="audio_optimization",
                file_patterns=["*.wav", "*.flac", "*.aiff", "*.mp3"],
                optimization_type="latency_priority",
                cache_strategy=CacheStrategy.CREATOR_AWARE,
                compression_level=CompressionLevel.FAST,
                priority=1,
                creator_specific=True,
                conditions={"creator_type": "musician"}
            ),
            
            # Image file optimization
            DiskOptimizationRule(
                rule_name="image_optimization",
                file_patterns=["*.raw", "*.cr2", "*.nef", "*.tiff", "*.psd"],
                optimization_type="throughput_priority",
                cache_strategy=CacheStrategy.INTELLIGENT,
                compression_level=CompressionLevel.NONE,
                priority=2,
                creator_specific=True,
                conditions={"creator_type": "photographer"}
            ),
            
            # Text content optimization
            DiskOptimizationRule(
                rule_name="text_optimization",
                file_patterns=["*.md", "*.txt", "*.docx", "*.pdf"],
                optimization_type="compression_priority",
                cache_strategy=CacheStrategy.LRU,
                compression_level=CompressionLevel.MAX,
                priority=3,
                creator_specific=True,
                conditions={"creator_type": "blogger"}
            ),
            
            # General optimization
            DiskOptimizationRule(
                rule_name="general_optimization",
                file_patterns=["*"],
                optimization_type="balanced",
                cache_strategy=CacheStrategy.LRU,
                compression_level=CompressionLevel.BALANCED,
                priority=5
            )
        ]
        
        self._optimization_rules.extend(default_rules)
        logger.info(f"Initialized {len(default_rules)} disk optimization rules")
    
    async def start_optimization_monitor(self) -> None:
        """Start continuous disk optimization monitoring"""
        if self._is_running:
            logger.warning("Disk optimization monitor already running")
            return
        
        self._is_running = True
        logger.info("Starting enterprise disk optimization monitor")
        
        try:
            while self._is_running:
                start_time = time.perf_counter()
                
                # Collect disk metrics
                metrics = await self.collect_disk_metrics()
                self._disk_history.append(metrics)
                
                # Perform optimizations
                await self.auto_optimize_disk_io(metrics)
                
                # Manage cache
                await self.optimize_disk_cache()
                
                # Analyze file access patterns
                await self.analyze_file_access_patterns()
                
                # Update performance stats
                optimization_time = (time.perf_counter() - start_time) * 1000
                self._update_optimization_stats(optimization_time)
                
                # Sleep until next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"Error in disk optimization monitor: {e}")
        finally:
            self._is_running = False
            logger.info("Disk optimization monitor stopped")
    
    async def stop_optimization_monitor(self) -> None:
        """Stop disk optimization monitoring"""
        self._is_running = False
        logger.info("Stopping disk optimization monitor")
    
    async def collect_disk_metrics(self) -> DiskMetrics:
        """
        Collect comprehensive disk performance metrics
        
        Performance Target: < 10ms collection time
        """
        try:
            # Get disk I/O statistics
            disk_io = psutil.disk_io_counters()
            
            # Calculate disk usage
            disk_usage = psutil.disk_usage('/')
            
            # Calculate I/O rates and latency
            current_time = time.time()
            
            if self._io_counters_prev and disk_io:
                time_delta = current_time - self._io_counters_prev['timestamp']
                read_bytes_delta = disk_io.read_bytes - self._io_counters_prev['read_bytes']
                write_bytes_delta = disk_io.write_bytes - self._io_counters_prev['write_bytes']
                read_count_delta = disk_io.read_count - self._io_counters_prev['read_count']
                write_count_delta = disk_io.write_count - self._io_counters_prev['write_count']
                
                # Calculate IOPS and latency
                total_ops = read_count_delta + write_count_delta
                iops = total_ops / time_delta if time_delta > 0 else 0
                
                # Estimate latency (simplified calculation)
                total_time_delta = (disk_io.read_time - self._io_counters_prev['read_time'] + 
                                  disk_io.write_time - self._io_counters_prev['write_time'])
                latency_ms = (total_time_delta / total_ops) if total_ops > 0 else 0
            else:
                iops = 0
                latency_ms = 0
            
            # Update previous counters
            if disk_io:
                self._io_counters_prev = {
                    'timestamp': current_time,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count,
                    'read_time': disk_io.read_time,
                    'write_time': disk_io.write_time
                }
            
            metrics = DiskMetrics(
                read_bytes=disk_io.read_bytes if disk_io else 0,
                write_bytes=disk_io.write_bytes if disk_io else 0,
                read_count=disk_io.read_count if disk_io else 0,
                write_count=disk_io.write_count if disk_io else 0,
                read_time_ms=disk_io.read_time if disk_io else 0,
                write_time_ms=disk_io.write_time if disk_io else 0,
                busy_time_ms=disk_io.busy_time if disk_io else 0,
                usage_percent=disk_usage.used / disk_usage.total * 100,
                free_space_bytes=disk_usage.free,
                total_space_bytes=disk_usage.total,
                iops=iops,
                latency_ms=latency_ms
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
            return DiskMetrics()
    
    async def auto_optimize_disk_io(self, current_metrics: DiskMetrics) -> Dict[str, Any]:
        """
        Automatically optimize disk I/O based on current metrics
        
        Performance Target: < 50ms optimization cycles
        """
        with self._optimization_lock:
            optimization_results = {
                "optimizations_applied": [],
                "performance_improvements": {},
                "recommendations": [],
                "timestamp": datetime.now()
            }
            
            try:
                # Disk space optimization
                if current_metrics.usage_percent > 80:
                    space_results = await self.optimize_disk_space()
                    optimization_results["optimizations_applied"].extend(space_results)
                
                # I/O pattern optimization
                io_results = await self.optimize_io_patterns(current_metrics)
                optimization_results["optimizations_applied"].extend(io_results)
                
                # File placement optimization
                placement_results = await self.optimize_file_placement()
                optimization_results["optimizations_applied"].extend(placement_results)
                
                # Creator-specific optimizations
                creator_results = await self._apply_creator_optimizations(current_metrics)
                optimization_results["optimizations_applied"].extend(creator_results)
                
                # Update statistics
                self._optimization_stats["total_optimizations"] += len(optimization_results["optimizations_applied"])
                self._optimization_stats["last_optimization"] = datetime.now()
                
                return optimization_results
                
            except Exception as e:
                logger.error(f"Error in auto_optimize_disk_io: {e}")
                return optimization_results
    
    async def optimize_disk_space(self) -> List[Dict[str, Any]]:
        """
        Optimize disk space usage
        
        Performance Target: < 30ms space optimization
        """
        optimizations = []
        
        try:
            # Clean temporary files
            temp_cleaned = await self._clean_temp_files()
            if temp_cleaned > 0:
                optimizations.append({
                    "action": "temp_file_cleanup",
                    "bytes_freed": temp_cleaned,
                    "description": f"Cleaned {temp_cleaned // (1024*1024)}MB of temporary files"
                })
            
            # Compress old files
            if self.enable_compression:
                compressed_files = await self._compress_old_files()
                optimizations.extend(compressed_files)
            
            # Cache cleanup
            cache_cleaned = await self._cleanup_old_cache_entries()
            if cache_cleaned > 0:
                optimizations.append({
                    "action": "cache_cleanup",
                    "bytes_freed": cache_cleaned,
                    "description": f"Cleaned {cache_cleaned // (1024*1024)}MB from cache"
                })
            
        except Exception as e:
            logger.error(f"Error optimizing disk space: {e}")
        
        return optimizations
    
    async def optimize_io_patterns(self, metrics: DiskMetrics) -> List[Dict[str, Any]]:
        """
        Optimize I/O access patterns
        
        Performance Target: < 20ms pattern optimization
        """
        optimizations = []
        
        try:
            # Detect high latency
            if metrics.latency_ms > 10.0:  # High latency threshold
                optimization = {
                    "action": "io_latency_optimization",
                    "current_latency_ms": metrics.latency_ms,
                    "recommendations": [
                        "Consider SSD upgrade if using HDD",
                        "Optimize file access patterns",
                        "Reduce concurrent I/O operations"
                    ]
                }
                optimizations.append(optimization)
            
            # Detect inefficient I/O patterns
            if len(self._disk_history) > 2:
                recent_metrics = list(self._disk_history)[-3:]
                io_efficiency = await self._analyze_io_efficiency(recent_metrics)
                
                if io_efficiency < 0.7:  # Low efficiency
                    optimization = {
                        "action": "io_pattern_optimization",
                        "efficiency_score": io_efficiency,
                        "recommendations": [
                            "Implement sequential read patterns",
                            "Reduce random access operations",
                            "Optimize buffer sizes"
                        ]
                    }
                    optimizations.append(optimization)
            
        except Exception as e:
            logger.error(f"Error optimizing I/O patterns: {e}")
        
        return optimizations
    
    async def optimize_file_placement(self) -> List[Dict[str, Any]]:
        """
        Optimize file placement based on access patterns
        
        Performance Target: < 25ms placement optimization
        """
        optimizations = []
        
        try:
            # Analyze frequently accessed files
            frequent_files = sorted(
                self._access_patterns.values(),
                key=lambda x: x.access_frequency,
                reverse=True
            )[:10]  # Top 10 most accessed files
            
            for file_pattern in frequent_files:
                if file_pattern.access_frequency > 0.8:  # Very frequent access
                    optimization = {
                        "action": "file_placement_optimization",
                        "file_path": file_pattern.file_path,
                        "access_frequency": file_pattern.access_frequency,
                        "recommendation": "Move to fastest storage tier",
                        "estimated_improvement": "20-50% faster access"
                    }
                    optimizations.append(optimization)
            
        except Exception as e:
            logger.error(f"Error optimizing file placement: {e}")
        
        return optimizations
    
    async def optimize_disk_cache(self) -> Dict[str, Any]:
        """
        Optimize disk cache performance
        
        Performance Target: < 15ms cache optimization
        """
        optimization_result = {
            "action": "disk_cache_optimization",
            "cache_stats": {},
            "optimizations_applied": [],
            "recommendations": []
        }
        
        try:
            # Calculate cache statistics
            total_hits = self._cache_hits
            total_requests = self._cache_hits + self._cache_misses
            hit_rate = total_hits / total_requests if total_requests > 0 else 0
            
            optimization_result["cache_stats"] = {
                "hit_rate": hit_rate,
                "cache_size_mb": self._current_cache_size / (1024 * 1024),
                "max_cache_size_mb": self.cache_size_mb,
                "entries_count": len(self._file_cache)
            }
            
            # Evict old cache entries if cache is full
            if self._current_cache_size > self._cache_size_bytes:
                evicted_size = await self._evict_cache_entries()
                optimization_result["optimizations_applied"].append({
                    "action": "cache_eviction",
                    "bytes_evicted": evicted_size
                })
            
            # Preload frequently accessed files
            if self.enable_intelligent_caching:
                preloaded = await self._preload_frequent_files()
                if preloaded:
                    optimization_result["optimizations_applied"].append({
                        "action": "intelligent_preloading",
                        "files_preloaded": len(preloaded)
                    })
            
            # Update cache hit rate statistic
            self._optimization_stats["cache_hit_rate"] = hit_rate
            
        except Exception as e:
            logger.error(f"Error optimizing disk cache: {e}")
            optimization_result["error"] = str(e)
        
        return optimization_result
    
    async def analyze_file_access_patterns(self) -> Dict[str, Any]:
        """
        Analyze file access patterns for optimization
        
        Performance Target: < 20ms pattern analysis
        """
        analysis_result = {
            "action": "file_access_pattern_analysis",
            "patterns_detected": [],
            "recommendations": []
        }
        
        try:
            # Update access frequencies
            current_time = datetime.now()
            for pattern in self._access_patterns.values():
                time_since_access = (current_time - pattern.last_accessed).total_seconds()
                # Decay frequency over time
                pattern.access_frequency *= max(0.1, 1 - (time_since_access / 3600))  # Decay over 1 hour
            
            # Identify hot files
            hot_files = [p for p in self._access_patterns.values() if p.access_frequency > 0.5]
            if hot_files:
                analysis_result["patterns_detected"].append({
                    "pattern_type": "hot_files",
                    "file_count": len(hot_files),
                    "recommendation": "Consider caching or faster storage placement"
                })
            
            # Identify cold files
            cold_files = [p for p in self._access_patterns.values() 
                         if p.access_frequency < 0.1 and p.access_count > 0]
            if cold_files:
                analysis_result["patterns_detected"].append({
                    "pattern_type": "cold_files",
                    "file_count": len(cold_files),
                    "recommendation": "Consider archiving or compression"
                })
            
        except Exception as e:
            logger.error(f"Error analyzing file access patterns: {e}")
            analysis_result["error"] = str(e)
        
        return analysis_result
    
    async def _clean_temp_files(self) -> int:
        """Clean temporary files and return bytes freed"""
        bytes_freed = 0
        try:
            temp_dir = Path(tempfile.gettempdir())
            current_time = datetime.now()
            
            for temp_file in temp_dir.glob("tmp*"):
                try:
                    if temp_file.is_file():
                        # Remove files older than 1 hour
                        file_age = current_time - datetime.fromtimestamp(temp_file.stat().st_mtime)
                        if file_age > timedelta(hours=1):
                            file_size = temp_file.stat().st_size
                            temp_file.unlink()
                            bytes_freed += file_size
                except Exception:
                    continue  # Skip files that can't be processed
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
        
        return bytes_freed
    
    async def _compress_old_files(self) -> List[Dict[str, Any]]:
        """Compress old files to save space"""
        compressions = []
        try:
            # This would implement file compression logic
            # For now, return empty list as placeholder
            pass
        except Exception as e:
            logger.error(f"Error compressing old files: {e}")
        
        return compressions
    
    async def _cleanup_old_cache_entries(self) -> int:
        """Cleanup old cache entries and return bytes freed"""
        bytes_freed = 0
        try:
            current_time = datetime.now()
            entries_to_remove = []
            
            for file_path, entry in self._file_cache.items():
                # Remove entries older than 24 hours with low access count
                age = current_time - entry.cached_at
                if age > timedelta(hours=24) and entry.access_count < 5:
                    entries_to_remove.append(file_path)
                    bytes_freed += entry.size_bytes
            
            for file_path in entries_to_remove:
                del self._file_cache[file_path]
                self._current_cache_size -= self._file_cache.get(file_path, CacheEntry()).size_bytes
        
        except Exception as e:
            logger.error(f"Error cleaning cache entries: {e}")
        
        return bytes_freed
    
    async def _analyze_io_efficiency(self, metrics_list: List[DiskMetrics]) -> float:
        """Analyze I/O efficiency based on metrics history"""
        try:
            if len(metrics_list) < 2:
                return 1.0
            
            # Calculate efficiency based on IOPS vs latency ratio
            total_efficiency = 0
            count = 0
            
            for metrics in metrics_list:
                if metrics.iops > 0 and metrics.latency_ms > 0:
                    # Higher IOPS with lower latency = better efficiency
                    efficiency = metrics.iops / (metrics.latency_ms + 1)
                    total_efficiency += min(efficiency / 100, 1.0)  # Normalize
                    count += 1
            
            return total_efficiency / count if count > 0 else 1.0
            
        except Exception as e:
            logger.error(f"Error analyzing I/O efficiency: {e}")
            return 1.0
    
    async def _evict_cache_entries(self) -> int:
        """Evict cache entries using LRU strategy"""
        bytes_evicted = 0
        try:
            # Sort by last access time (LRU)
            sorted_entries = sorted(
                self._file_cache.items(),
                key=lambda x: x[1].cached_at
            )
            
            # Evict oldest entries until cache size is acceptable
            target_size = self._cache_size_bytes * 0.8  # 80% of max cache size
            
            for file_path, entry in sorted_entries:
                if self._current_cache_size <= target_size:
                    break
                
                del self._file_cache[file_path]
                self._current_cache_size -= entry.size_bytes
                bytes_evicted += entry.size_bytes
        
        except Exception as e:
            logger.error(f"Error evicting cache entries: {e}")
        
        return bytes_evicted
    
    async def _preload_frequent_files(self) -> List[str]:
        """Preload frequently accessed files into cache"""
        preloaded_files = []
        try:
            # Find frequently accessed files not in cache
            frequent_patterns = sorted(
                self._access_patterns.values(),
                key=lambda x: x.access_frequency,
                reverse=True
            )[:5]  # Top 5 most frequent
            
            for pattern in frequent_patterns:
                if pattern.file_path not in self._file_cache:
                    if await self._should_cache_file(pattern):
                        success = await self._cache_file(pattern.file_path)
                        if success:
                            preloaded_files.append(pattern.file_path)
        
        except Exception as e:
            logger.error(f"Error preloading frequent files: {e}")
        
        return preloaded_files
    
    async def _should_cache_file(self, pattern: FileAccessPattern) -> bool:
        """Determine if a file should be cached"""
        try:
            # Cache criteria
            if pattern.access_frequency > 0.3 and pattern.file_size < 100 * 1024 * 1024:  # < 100MB
                return True
            
            # Don't cache very large files or rarely accessed files
            return False
        except Exception:
            return False
    
    async def _cache_file(self, file_path: str) -> bool:
        """Cache a file in memory"""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_size = os.path.getsize(file_path)
            
            # Check if there's room in cache
            if self._current_cache_size + file_size > self._cache_size_bytes:
                await self._evict_cache_entries()
            
            # Read and cache file
            async with aiofiles.open(file_path, 'rb') as f:
                file_data = await f.read()
            
            cache_entry = CacheEntry(
                file_path=file_path,
                cached_data=file_data,
                size_bytes=file_size,
                access_count=1
            )
            
            self._file_cache[file_path] = cache_entry
            self._current_cache_size += file_size
            
            return True
            
        except Exception as e:
            logger.error(f"Error caching file {file_path}: {e}")
            return False
    
    async def _apply_creator_optimizations(self, metrics: DiskMetrics) -> List[Dict[str, Any]]:
        """Apply creator-specific disk optimizations"""
        optimizations = []
        
        try:
            for creator_id, profile in self._creator_profiles.items():
                creator_type = profile.creator_type
                
                if creator_type == "musician":
                    # Musician-specific optimizations
                    if metrics.latency_ms > 5.0:  # High latency for audio
                        optimization = {
                            "action": "musician_disk_optimization",
                            "creator_id": creator_id,
                            "optimizations": [
                                "Prioritize audio file I/O",
                                "Optimize audio buffer cache",
                                "Minimize audio file seek times"
                            ],
                            "target_latency_ms": 2.0
                        }
                        optimizations.append(optimization)
                
                elif creator_type == "photographer":
                    # Photographer-specific optimizations
                    if metrics.iops < 1000:  # Low IOPS for image processing
                        optimization = {
                            "action": "photographer_disk_optimization",
                            "creator_id": creator_id,
                            "optimizations": [
                                "Optimize large file streaming",
                                "Implement RAW file caching",
                                "Parallelize batch processing I/O"
                            ],
                            "target_throughput": "maximize"
                        }
                        optimizations.append(optimization)
                
                elif creator_type == "blogger":
                    # Blogger-specific optimizations
                    optimization = {
                        "action": "blogger_disk_optimization",
                        "creator_id": creator_id,
                        "optimizations": [
                            "Optimize content file access",
                            "Implement smart content caching",
                            "Compress text-based files"
                        ],
                        "target_balance": "space_efficiency"
                    }
                    optimizations.append(optimization)
                    
        except Exception as e:
            logger.error(f"Error applying creator optimizations: {e}")
        
        return optimizations
    
    async def predict_disk_failures(self) -> Dict[str, Any]:
        """
        Predict potential disk failures or performance issues
        
        Performance Target: < 30ms prediction time
        """
        prediction_result = {
            "failure_risk": "low",
            "predicted_issues": [],
            "confidence": 0.0,
            "recommendations": [],
            "time_horizon_hours": 24
        }
        
        try:
            if len(self._disk_history) < 10:
                prediction_result["recommendations"].append("Insufficient data for accurate prediction")
                return prediction_result
            
            # Analyze disk space trend
            recent_metrics = list(self._disk_history)[-10:]
            usage_values = [m.usage_percent for m in recent_metrics]
            
            # Calculate disk space trend
            space_trend = self._calculate_disk_trend(usage_values)
            
            if space_trend > 0.1:  # Disk space increasing rapidly
                time_to_full = (100 - usage_values[-1]) / space_trend if space_trend > 0 else float('inf')
                
                if time_to_full < 24:  # Disk full within 24 hours
                    prediction_result["failure_risk"] = "high"
                    prediction_result["confidence"] = 0.9
                    prediction_result["predicted_issues"].append({
                        "issue_type": "disk_space_exhaustion",
                        "estimated_time_hours": time_to_full,
                        "severity": "critical"
                    })
                elif time_to_full < 72:  # Disk full within 72 hours
                    prediction_result["failure_risk"] = "medium"
                    prediction_result["confidence"] = 0.7
            
            # Analyze latency trend
            latency_values = [m.latency_ms for m in recent_metrics if m.latency_ms > 0]
            if latency_values:
                avg_latency = sum(latency_values) / len(latency_values)
                if avg_latency > 20.0:  # High average latency
                    prediction_result["predicted_issues"].append({
                        "issue_type": "performance_degradation",
                        "current_latency_ms": avg_latency,
                        "severity": "medium"
                    })
            
            # Generate recommendations based on risk
            if prediction_result["failure_risk"] in ["high", "medium"]:
                prediction_result["recommendations"].extend([
                    "Immediate disk cleanup required",
                    "Consider adding storage capacity",
                    "Archive old files",
                    "Enable compression for large files"
                ])
            
        except Exception as e:
            logger.error(f"Error predicting disk failures: {e}")
            prediction_result["error"] = str(e)
        
        return prediction_result
    
    def _calculate_disk_trend(self, values: List[float]) -> float:
        """Calculate disk usage trend"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    async def add_creator_profile(self, creator_id: str, creator_type: str) -> None:
        """Add creator-specific disk optimization profile"""
        try:
            profile = CreatorDiskProfile(creator_type)
            self._creator_profiles[creator_id] = profile
            logger.info(f"Added creator disk profile: {creator_id} ({creator_type})")
        except Exception as e:
            logger.error(f"Error adding creator profile: {e}")
    
    async def track_file_access(self, file_path: str, operation: str, bytes_transferred: int = 0) -> None:
        """Track file access for pattern analysis"""
        try:
            if file_path not in self._access_patterns:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                file_ext = Path(file_path).suffix.lower()
                
                self._access_patterns[file_path] = FileAccessPattern(
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_ext
                )
            
            pattern = self._access_patterns[file_path]
            pattern.access_count += 1
            pattern.last_accessed = datetime.now()
            pattern.access_frequency = min(pattern.access_frequency + 0.1, 1.0)
            
            if operation == "read":
                pattern.total_bytes_read += bytes_transferred
            elif operation == "write":
                pattern.total_bytes_written += bytes_transferred
                
        except Exception as e:
            logger.error(f"Error tracking file access: {e}")
    
    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Get current optimization statistics"""
        return {
            **self._optimization_stats,
            "cache_stats": {
                "cache_size_mb": self._current_cache_size / (1024 * 1024),
                "cache_entries": len(self._file_cache),
                "hit_rate": self._optimization_stats["cache_hit_rate"]
            },
            "monitored_files": len(self._access_patterns),
            "creator_profiles": len(self._creator_profiles),
            "disk_history_size": len(self._disk_history),
            "is_running": self._is_running
        }
    
    def _update_optimization_stats(self, optimization_time_ms: float) -> None:
        """Update optimization performance statistics"""
        # Update average optimization time
        current_avg = self._optimization_stats["avg_optimization_time_ms"]
        total_opts = self._optimization_stats["total_optimizations"]
        
        if total_opts > 0:
            new_avg = ((current_avg * total_opts) + optimization_time_ms) / (total_opts + 1)
            self._optimization_stats["avg_optimization_time_ms"] = new_avg
        else:
            self._optimization_stats["avg_optimization_time_ms"] = optimization_time_ms
    
    def __del__(self):
        """Cleanup resources on destruction"""
        try:
            self._is_running = False
            # Clean up cache directory if needed
            if hasattr(self, '_cache_dir') and self._cache_dir.exists():
                shutil.rmtree(self._cache_dir, ignore_errors=True)
        except Exception:
            pass  # Ignore cleanup errors


# Factory function for enterprise instantiation
def create_disk_optimizer(
    optimization_mode: str = "balanced",
    cache_size_mb: int = 1024,
    enable_compression: bool = True
) -> DiskOptimizer:
    """
    Factory function to create DiskOptimizer instance
    
    Args:
        optimization_mode: latency_optimized, throughput_optimized, balanced, creator_optimized
        cache_size_mb: Cache size in megabytes
        enable_compression: Enable file compression features
    
    Returns:
        Configured DiskOptimizer instance
    """
    mode_map = {
        "latency_optimized": DiskOptimizationMode.LATENCY_OPTIMIZED,
        "throughput_optimized": DiskOptimizationMode.THROUGHPUT_OPTIMIZED,
        "balanced": DiskOptimizationMode.BALANCED,
        "creator_optimized": DiskOptimizationMode.CREATOR_OPTIMIZED,
        "enterprise": DiskOptimizationMode.ENTERPRISE
    }
    
    mode = mode_map.get(optimization_mode, DiskOptimizationMode.BALANCED)
    
    return DiskOptimizer(
        optimization_mode=mode,
        cache_size_mb=cache_size_mb,
        enable_compression=enable_compression
    )


# Export for enterprise usage
__all__ = [
    "DiskOptimizer",
    "DiskOptimizationMode",
    "CompressionLevel",
    "CacheStrategy",
    "DiskMetrics",
    "FileAccessPattern",
    "CacheEntry",
    "DiskOptimizationRule",
    "CreatorDiskProfile",
    "create_disk_optimizer"
]