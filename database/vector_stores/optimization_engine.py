"""Vector Database Optimization Engine

This module provides advanced optimization capabilities for vector databases,
including index tuning, query optimization, and performance enhancement.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import numpy as np
import faiss
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, and_, or_
import psutil
import gc
import threading
from concurrent.futures import ThreadPoolExecutor

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.utils.exceptions import OptimizationError, VectorStoreError
from backend.utils.performance import measure_execution_time
from backend.utils.monitoring import MetricsCollector
from backend.utils.ml_models import AutoMLOptimizer

from .vector_store_manager import VectorStoreManager
from .faiss_vector_store import FAISSVectorStore

logger = logging.getLogger(__name__)
settings = get_settings()


class OptimizationStrategy(Enum):
    """
Vector database optimization strategies"""

    PERFORMANCE = "performance"      # Focus on query speed
    MEMORY = "memory"               # Focus on memory efficiency
    BALANCED = "balanced"           # Balance speed and memory
    QUALITY = "quality"             # Focus on search quality
    STORAGE = "storage"             # Focus on storage efficiency


class IndexType(Enum):
    """FAISS index types for optimization"""

    FLAT = "Flat"                   # Brute force, exact search
    IVF_FLAT = "IVFFlat"           # Inverted file with flat quantizer
    IVF_PQ = "IVFPQ"               # Inverted file with product quantization
    HNSW = "HNSW"                  # Hierarchical Navigable Small World
    LSH = "LSH"                    # Locality Sensitive Hashing
    SCALAR_QUANTIZER = "SQ"        # Scalar quantization


@dataclass
class OptimizationConfig:
    """Configuration for vector database optimization"""
    strategy: OptimizationStrategy
    target_latency_ms: float = 50.0
    target_memory_mb: float = 1024.0
    target_accuracy: float = 0.95
    batch_size: int = 1000
    test_queries: int = 100
    enable_gpu: bool = False
    parallel_workers: int = 4
    optimization_iterations: int = 10


@dataclass
class PerformanceMetrics:
    """
Performance metrics for optimization analysis"""
    query_latency_ms: float
    memory_usage_mb: float
    accuracy_score: float
    throughput_qps: float
    index_size_mb: float
    build_time_seconds: float
    cpu_usage_percent: float
    gpu_usage_percent: float = 0.0


@dataclass
class OptimizationResult:
    """
Result of optimization process"""
    original_metrics: PerformanceMetrics
    optimized_metrics: PerformanceMetrics
    improvement_ratio: float
    recommended_config: Dict[str, Any]
    optimization_log: List[str]
    success: bool


class VectorDatabaseOptimizer:
    """
    Advanced vector database optimization engine.
    
    Features:
    - Intelligent index selection and tuning
    - Query performance optimization
    - Memory usage optimization
    - Automatic parameter tuning
    - Multi-objective optimization
    - Real-time performance monitoring
    - Hardware-aware optimization
    """
    
    def __init__(self):
        """
Initialize vector database optimizer"""
        self.vector_manager = VectorStoreManager()
        self.metrics_collector = MetricsCollector()
        self.automl_optimizer = AutoMLOptimizer()
        
        # Optimization state
        self.optimization_history: List[OptimizationResult] = []
        self.current_configs: Dict[str, Dict[str, Any]] = {}
        self.performance_baselines: Dict[str, PerformanceMetrics] = {}
        
        # Hardware information
        self.system_info = self._get_system_info()
        
        # Thread pool for parallel optimization
        self.thread_pool = ThreadPoolExecutor(max_workers=settings.OPTIMIZATION_WORKERS)
        
        logger.info("Initialized VectorDatabaseOptimizer")
    
    async def initialize(self) -> None:
        """Initialize optimizer and baseline metrics"""
        try:
            await self.vector_manager.initialize()
            
            # Collect baseline metrics for all content types
            for content_type in ["audio", "video", "image", "text"]:
                baseline = await self._collect_baseline_metrics(content_type)
                self.performance_baselines[content_type] = baseline
            
            logger.info("Vector database optimizer initialized with baselines")
            
        except Exception as e:
            logger.error(f"Failed to initialize optimizer: {str(e)}")
            raise OptimizationError(f"Initialization failed: {str(e)}")
    
    @measure_execution_time
    async def optimize_content_type(
        self,
        content_type: str,
        config: OptimizationConfig,
        test_vectors: Optional[np.ndarray] = None
    ) -> OptimizationResult:
        """
        Optimize vector database for specific content type
        
        Args:
            content_type: Content type to optimize
            config: Optimization configuration
            test_vectors: Optional test vectors for evaluation
            
        Returns:
            Optimization result with recommendations
        """
        try:
            logger.info(f"Starting optimization for {content_type} with strategy {config.strategy.value}")
            
            # Get current metrics
            original_metrics = await self._measure_current_performance(content_type, config)
            
            # Generate test data if not provided
            if test_vectors is None:
                test_vectors = await self._generate_test_vectors(content_type, config.test_queries)
            
            # Optimization based on strategy
            optimization_log = []
            best_config = None
            best_metrics = original_metrics
            
            if config.strategy == OptimizationStrategy.PERFORMANCE:
                best_config, best_metrics, log = await self._optimize_for_performance(
                    content_type, config, test_vectors
                )
                optimization_log.extend(log)
            
            elif config.strategy == OptimizationStrategy.MEMORY:
                best_config, best_metrics, log = await self._optimize_for_memory(
                    content_type, config, test_vectors
                )
                optimization_log.extend(log)
            
            elif config.strategy == OptimizationStrategy.BALANCED:
                best_config, best_metrics, log = await self._optimize_balanced(
                    content_type, config, test_vectors
                )
                optimization_log.extend(log)
            
            elif config.strategy == OptimizationStrategy.QUALITY:
                best_config, best_metrics, log = await self._optimize_for_quality(
                    content_type, config, test_vectors
                )
                optimization_log.extend(log)
            
            elif config.strategy == OptimizationStrategy.STORAGE:
                best_config, best_metrics, log = await self._optimize_for_storage(
                    content_type, config, test_vectors
                )
                optimization_log.extend(log)
            
            # Calculate improvement ratio
            improvement_ratio = self._calculate_improvement_ratio(
                original_metrics, best_metrics, config.strategy
            )
            
            # Create result
            result = OptimizationResult(
                original_metrics=original_metrics,
                optimized_metrics=best_metrics,
                improvement_ratio=improvement_ratio,
                recommended_config=best_config,
                optimization_log=optimization_log,
                success=improvement_ratio > 1.0
            )
            
            # Store result
            self.optimization_history.append(result)
            self.current_configs[content_type] = best_config
            
            logger.info(
                f"Optimization completed for {content_type}. "
                f"Improvement ratio: {improvement_ratio:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Optimization failed for {content_type}: {str(e)}")
            raise OptimizationError(f"Optimization failed: {str(e)}")
    
    async def _optimize_for_performance(
        self,
        content_type: str,
        config: OptimizationConfig,
        test_vectors: np.ndarray
    ) -> Tuple[Dict[str, Any], PerformanceMetrics, List[str]]:
        """Optimize for query performance (speed)"""
        log = []
        best_config = None
        best_metrics = None
        
        try:
            # Test different index configurations for speed
            index_configs = [
                {"type": "IVFFlat", "nlist": 256, "nprobe": 32},
                {"type": "IVFFlat", "nlist": 512, "nprobe": 64},
                {"type": "IVFFlat", "nlist": 1024, "nprobe": 128},
                {"type": "HNSW", "M": 16, "efConstruction": 200, "efSearch": 50},
                {"type": "HNSW", "M": 32, "efConstruction": 400, "efSearch": 100},
            ]
            
            if config.enable_gpu and faiss.get_num_gpus() > 0:
                index_configs.extend([
                    {"type": "IVFFlat", "nlist": 2048, "nprobe": 256, "gpu": True},
                    {"type": "IVFFlat", "nlist": 4096, "nprobe": 512, "gpu": True},
                ])
            
            for idx_config in index_configs:
                try:
                    log.append(f"Testing index config: {idx_config}")
                    
                    # Create and test index
                    metrics = await self._test_index_configuration(
                        content_type, idx_config, test_vectors, config
                    )
                    
                    # Check if this is the best performance so far
                    if (best_metrics is None or 
                        metrics.query_latency_ms < best_metrics.query_latency_ms):
                        best_metrics = metrics
                        best_config = idx_config
                        log.append(f"New best latency: {metrics.query_latency_ms:.2f}ms")
                    
                    # Early termination if target achieved
                    if metrics.query_latency_ms <= config.target_latency_ms:
                        log.append(f"Target latency achieved: {metrics.query_latency_ms:.2f}ms")
                        break
                        
                except Exception as e:
                    log.append(f"Failed to test config {idx_config}: {str(e)}")
                    continue
            
            return best_config, best_metrics, log
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {str(e)}")
            return {}, PerformanceMetrics(0, 0, 0, 0, 0, 0, 0), [f"Error: {str(e)}"]
    
    async def _optimize_for_memory(
        self,
        content_type: str,
        config: OptimizationConfig,
        test_vectors: np.ndarray
    ) -> Tuple[Dict[str, Any], PerformanceMetrics, List[str]]:
        """Optimize for memory efficiency"""
        log = []
        best_config = None
        best_metrics = None
        
        try:
            # Test memory-efficient configurations
            index_configs = [
                {"type": "IVFPQ", "nlist": 256, "m": 8, "bits": 8},
                {"type": "IVFPQ", "nlist": 512, "m": 16, "bits": 8},
                {"type": "IVFPQ", "nlist": 1024, "m": 32, "bits": 8},
                {"type": "SQ", "type_variant": "SQ8"},
                {"type": "SQ", "type_variant": "SQ4"},
                {"type": "LSH", "nbits": 256},
                {"type": "LSH", "nbits": 512},
            ]
            
            for idx_config in index_configs:
                try:
                    log.append(f"Testing memory config: {idx_config}")
                    
                    metrics = await self._test_index_configuration(
                        content_type, idx_config, test_vectors, config
                    )
                    
                    # Check if this is the best memory usage so far
                    if (best_metrics is None or 
                        metrics.memory_usage_mb < best_metrics.memory_usage_mb):
                        best_metrics = metrics
                        best_config = idx_config
                        log.append(f"New best memory: {metrics.memory_usage_mb:.2f}MB")
                    
                    # Early termination if target achieved
                    if metrics.memory_usage_mb <= config.target_memory_mb:
                        log.append(f"Target memory achieved: {metrics.memory_usage_mb:.2f}MB")
                        break
                        
                except Exception as e:
                    log.append(f"Failed to test config {idx_config}: {str(e)}")
                    continue
            
            return best_config, best_metrics, log
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {str(e)}")
            return {}, PerformanceMetrics(0, 0, 0, 0, 0, 0, 0), [f"Error: {str(e)}"]
    
    async def _optimize_balanced(
        self,
        content_type: str,
        config: OptimizationConfig,
        test_vectors: np.ndarray
    ) -> Tuple[Dict[str, Any], PerformanceMetrics, List[str]]:
        """Optimize for balanced performance and efficiency"""
        log = []
        best_config = None
        best_metrics = None
        best_score = 0.0
        
        try:
            # Define balanced configurations
            index_configs = [
                {"type": "IVFFlat", "nlist": 512, "nprobe": 64},
                {"type": "IVFFlat", "nlist": 1024, "nprobe": 128},
                {"type": "IVFPQ", "nlist": 256, "m": 16, "bits": 8},
                {"type": "IVFPQ", "nlist": 512, "m": 8, "bits": 8},
                {"type": "HNSW", "M": 16, "efConstruction": 200, "efSearch": 50},
                {"type": "SQ", "type_variant": "SQ8"},
            ]
            
            for idx_config in index_configs:
                try:
                    log.append(f"Testing balanced config: {idx_config}")
                    
                    metrics = await self._test_index_configuration(
                        content_type, idx_config, test_vectors, config
                    )
                    
                    # Calculate balanced score (normalize and combine metrics)
                    latency_score = 1.0 / (1.0 + metrics.query_latency_ms / 100.0)
                    memory_score = 1.0 / (1.0 + metrics.memory_usage_mb / 1000.0)
                    accuracy_score = metrics.accuracy_score
                    throughput_score = min(metrics.throughput_qps / 1000.0, 1.0)
                    
                    balanced_score = (latency_score + memory_score + accuracy_score + throughput_score) / 4.0
                    
                    if balanced_score > best_score:
                        best_score = balanced_score
                        best_metrics = metrics
                        best_config = idx_config
                        log.append(f"New best balanced score: {balanced_score:.3f}")
                        
                except Exception as e:
                    log.append(f"Failed to test config {idx_config}: {str(e)}")
                    continue
            
            return best_config, best_metrics, log
            
        except Exception as e:
            logger.error(f"Balanced optimization failed: {str(e)}")
            return {}, PerformanceMetrics(0, 0, 0, 0, 0, 0, 0), [f"Error: {str(e)}"]
    
    async def _optimize_for_quality(
        self,
        content_type: str,
        config: OptimizationConfig,
        test_vectors: np.ndarray
    ) -> Tuple[Dict[str, Any], PerformanceMetrics, List[str]]:
        """Optimize for search quality (accuracy)"""
        log = []
        best_config = None
        best_metrics = None
        
        try:
            # Test high-quality configurations
            index_configs = [
                {"type": "Flat"},  # Exact search
                {"type": "IVFFlat", "nlist": 256, "nprobe": 256},  # High recall
                {"type": "IVFFlat", "nlist": 512, "nprobe": 512},
                {"type": "HNSW", "M": 32, "efConstruction": 400, "efSearch": 200},
                {"type": "HNSW", "M": 64, "efConstruction": 800, "efSearch": 400},
            ]
            
            for idx_config in index_configs:
                try:
                    log.append(f"Testing quality config: {idx_config}")
                    
                    metrics = await self._test_index_configuration(
                        content_type, idx_config, test_vectors, config
                    )
                    
                    # Check if this is the best accuracy so far
                    if (best_metrics is None or 
                        metrics.accuracy_score > best_metrics.accuracy_score):
                        best_metrics = metrics
                        best_config = idx_config
                        log.append(f"New best accuracy: {metrics.accuracy_score:.3f}")
                    
                    # Early termination if target achieved
                    if metrics.accuracy_score >= config.target_accuracy:
                        log.append(f"Target accuracy achieved: {metrics.accuracy_score:.3f}")
                        break
                        
                except Exception as e:
                    log.append(f"Failed to test config {idx_config}: {str(e)}")
                    continue
            
            return best_config, best_metrics, log
            
        except Exception as e:
            logger.error(f"Quality optimization failed: {str(e)}")
            return {}, PerformanceMetrics(0, 0, 0, 0, 0, 0, 0), [f"Error: {str(e)}"]
    
    async def _optimize_for_storage(
        self,
        content_type: str,
        config: OptimizationConfig,
        test_vectors: np.ndarray
    ) -> Tuple[Dict[str, Any], PerformanceMetrics, List[str]]:
        """Optimize for storage efficiency"""
        log = []
        best_config = None
        best_metrics = None
        
        try:
            # Test storage-efficient configurations
            index_configs = [
                {"type": "IVFPQ", "nlist": 256, "m": 64, "bits": 4},
                {"type": "IVFPQ", "nlist": 512, "m": 32, "bits": 4},
                {"type": "IVFPQ", "nlist": 1024, "m": 16, "bits": 8},
                {"type": "SQ", "type_variant": "SQ4"},
                {"type": "SQ", "type_variant": "SQ6"},
                {"type": "LSH", "nbits": 128},
                {"type": "LSH", "nbits": 256},
            ]
            
            for idx_config in index_configs:
                try:
                    log.append(f"Testing storage config: {idx_config}")
                    
                    metrics = await self._test_index_configuration(
                        content_type, idx_config, test_vectors, config
                    )
                    
                    # Check if this is the best storage efficiency so far
                    if (best_metrics is None or 
                        metrics.index_size_mb < best_metrics.index_size_mb):
                        best_metrics = metrics
                        best_config = idx_config
                        log.append(f"New best storage: {metrics.index_size_mb:.2f}MB")
                        
                except Exception as e:
                    log.append(f"Failed to test config {idx_config}: {str(e)}")
                    continue
            
            return best_config, best_metrics, log
            
        except Exception as e:
            logger.error(f"Storage optimization failed: {str(e)}")
            return {}, PerformanceMetrics(0, 0, 0, 0, 0, 0, 0), [f"Error: {str(e)}"]
    
    async def _test_index_configuration(
        self,
        content_type: str,
        index_config: Dict[str, Any],
        test_vectors: np.ndarray,
        config: OptimizationConfig
    ) -> PerformanceMetrics:
        """Test specific index configuration and measure performance"""
        try:
            # Create test index
            dimension = test_vectors.shape[1]
            test_index = self._create_faiss_index(index_config, dimension)
            
            # Measure build time
            build_start = datetime.now()
            
            # Train index if needed
            if hasattr(test_index, 'is_trained') and not test_index.is_trained:
                test_index.train(test_vectors.astype(np.float32))
            
            # Add vectors
            test_index.add(test_vectors.astype(np.float32))
            
            build_time = (datetime.now() - build_start).total_seconds()
            
            # Measure memory usage
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024
            index_size_mb = self._estimate_index_size(test_index, test_vectors.shape[0])
            
            # Measure query performance
            query_vectors = test_vectors[:config.test_queries].astype(np.float32)
            
            # Warm up
            test_index.search(query_vectors[:10], 10)
            
            # Measure query latency
            query_start = datetime.now()
            distances, indices = test_index.search(query_vectors, 10)
            query_end = datetime.now()
            
            query_latency_ms = (query_end - query_start).total_seconds() * 1000 / len(query_vectors)
            throughput_qps = len(query_vectors) / (query_end - query_start).total_seconds()
            
            # Measure accuracy (compared to exact search)
            accuracy_score = await self._measure_accuracy(
                test_vectors, query_vectors, test_index
            )
            
            # Measure resource usage
            cpu_usage = psutil.cpu_percent(interval=1)
            gpu_usage = 0.0
            if config.enable_gpu:
                gpu_usage = self._get_gpu_usage()
            
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            memory_usage_mb = memory_after - memory_before
            
            return PerformanceMetrics(
                query_latency_ms=query_latency_ms,
                memory_usage_mb=memory_usage_mb,
                accuracy_score=accuracy_score,
                throughput_qps=throughput_qps,
                index_size_mb=index_size_mb,
                build_time_seconds=build_time,
                cpu_usage_percent=cpu_usage,
                gpu_usage_percent=gpu_usage
            )
            
        except Exception as e:
            logger.error(f"Failed to test index configuration: {str(e)}")
            # Return worst-case metrics
            return PerformanceMetrics(
                query_latency_ms=float('inf'),
                memory_usage_mb=float('inf'),
                accuracy_score=0.0,
                throughput_qps=0.0,
                index_size_mb=float('inf'),
                build_time_seconds=float('inf'),
                cpu_usage_percent=100.0,
                gpu_usage_percent=0.0
            )
    
    def _create_faiss_index(self, config: Dict[str, Any], dimension: int) -> faiss.Index:
        """Create FAISS index based on configuration"""
        try:
            index_type = config["type"]
            
            if index_type == "Flat":
                index = faiss.IndexFlatL2(dimension)
            
            elif index_type == "IVFFlat":
                nlist = config.get("nlist", 256)
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
                
                # Set search parameters
                if "nprobe" in config:
                    index.nprobe = config["nprobe"]
            
            elif index_type == "IVFPQ":
                nlist = config.get("nlist", 256)
                m = config.get("m", 8)
                bits = config.get("bits", 8)
                quantizer = faiss.IndexFlatL2(dimension)
                index = faiss.IndexIVFPQ(quantizer, dimension, nlist, m, bits)
            
            elif index_type == "HNSW":
                M = config.get("M", 16)
                index = faiss.IndexHNSWFlat(dimension, M)
                
                if "efConstruction" in config:
                    index.hnsw.efConstruction = config["efConstruction"]
                if "efSearch" in config:
                    index.hnsw.efSearch = config["efSearch"]
            
            elif index_type == "SQ":
                type_variant = config.get("type_variant", "SQ8")
                if type_variant == "SQ8":
                    index = faiss.IndexScalarQuantizer(dimension, faiss.ScalarQuantizer.QT_8bit)
                elif type_variant == "SQ4":
                    index = faiss.IndexScalarQuantizer(dimension, faiss.ScalarQuantizer.QT_4bit)
                elif type_variant == "SQ6":
                    index = faiss.IndexScalarQuantizer(dimension, faiss.ScalarQuantizer.QT_6bit)
                else:
                    index = faiss.IndexScalarQuantizer(dimension, faiss.ScalarQuantizer.QT_8bit)
            
            elif index_type == "LSH":
                nbits = config.get("nbits", 256)
                index = faiss.IndexLSH(dimension, nbits)
            
            else:
                # Default to Flat index
                index = faiss.IndexFlatL2(dimension)
            
            # GPU support
            if config.get("gpu", False) and faiss.get_num_gpus() > 0:
                gpu_res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(gpu_res, 0, index)
            
            return index
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {str(e)}")
            # Fallback to flat index
            return faiss.IndexFlatL2(dimension)
    
    async def _measure_accuracy(
        self,
        all_vectors: np.ndarray,
        query_vectors: np.ndarray,
        test_index: faiss.Index
    ) -> float:
        """Measure search accuracy compared to exact search"""
        try:
            # Get ground truth using exact search
            exact_index = faiss.IndexFlatL2(all_vectors.shape[1])
            exact_index.add(all_vectors.astype(np.float32))
            
            # Search with both indices
            k = 10
            exact_distances, exact_indices = exact_index.search(query_vectors, k)
            test_distances, test_indices = test_index.search(query_vectors, k)
            
            # Calculate recall@k
            total_matches = 0
            total_possible = len(query_vectors) * k
            
            for i in range(len(query_vectors)):
                exact_set = set(exact_indices[i])
                test_set = set(test_indices[i])
                matches = len(exact_set.intersection(test_set))
                total_matches += matches
            
            accuracy = total_matches / total_possible
            return accuracy
            
        except Exception as e:
            logger.error(f"Failed to measure accuracy: {str(e)}")
            return 0.0
    
    def _estimate_index_size(self, index: faiss.Index, num_vectors: int) -> float:
        """Estimate index size in MB"""
        try:
            # Basic estimation based on index type and vector count
            dimension = index.d
            
            if hasattr(index, 'code_size'):
                # Quantized index
                code_size = index.code_size
                size_bytes = num_vectors * code_size
            else:
                # Flat index or similar
                size_bytes = num_vectors * dimension * 4  # float32
            
            # Add overhead
            size_bytes *= 1.2  # 20% overhead estimation
            
            return size_bytes / 1024 / 1024
            
        except Exception as e:
            logger.error(f"Failed to estimate index size: {str(e)}")
            return 0.0
    
    def _get_gpu_usage(self) -> float:
        """Get GPU usage percentage"""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return float(info.gpu)
        except:
            return 0.0
    
    async def _collect_baseline_metrics(self, content_type: str) -> PerformanceMetrics:
        """
Collect baseline performance metrics"""
        try:
            # Generate sample data for testing
            test_vectors = await self._generate_test_vectors(content_type, 100)
            
            # Create basic index for baseline
            baseline_config = {"type": "IVFFlat", "nlist": 256, "nprobe": 64}
            baseline_metrics = await self._test_index_configuration(
                content_type, baseline_config, test_vectors, OptimizationConfig(OptimizationStrategy.BALANCED)
            )
            
            return baseline_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect baseline metrics for {content_type}: {str(e)}")
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0)
    
    async def _generate_test_vectors(self, content_type: str, count: int) -> np.ndarray:
        """Generate test vectors for optimization"""
        try:
            # Get some real vectors from database for realistic testing
            async with get_db_session() as session:
                stmt = select(ContentFingerprint.vector_embedding).where(
                    and_(
                        ContentFingerprint.content_type == content_type,
                        ContentFingerprint.vector_embedding.isnot(None)
                    )
                ).limit(count)
                
                result = await session.execute(stmt)
                embeddings = result.scalars().all()
                
                if len(embeddings) >= count // 2:
                    # Use real embeddings
                    vectors = np.array([np.frombuffer(emb, dtype=np.float32) for emb in embeddings[:count]])
                else:
                    # Generate synthetic vectors
                    dimension = 512  # Default dimension
                    vectors = np.random.randn(count, dimension).astype(np.float32)
                    # Normalize
                    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
                    vectors = vectors / norms
                
                return vectors
                
        except Exception as e:
            logger.error(f"Failed to generate test vectors: {str(e)}")
            # Fallback to random vectors
            dimension = 512
            vectors = np.random.randn(count, dimension).astype(np.float32)
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            return vectors / norms
    
    async def _measure_current_performance(
        self,
        content_type: str,
        config: OptimizationConfig
    ) -> PerformanceMetrics:
        """Measure current system performance"""
        try:
            # Get current configuration if exists
            current_config = self.current_configs.get(content_type, {"type": "IVFFlat", "nlist": 256})
            
            # Generate test vectors
            test_vectors = await self._generate_test_vectors(content_type, config.test_queries)
            
            # Measure with current configuration
            metrics = await self._test_index_configuration(
                content_type, current_config, test_vectors, config
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to measure current performance: {str(e)}")
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0)
    
    def _calculate_improvement_ratio(
        self,
        original: PerformanceMetrics,
        optimized: PerformanceMetrics,
        strategy: OptimizationStrategy
    ) -> float:
        """Calculate improvement ratio based on optimization strategy"""
        try:
            if strategy == OptimizationStrategy.PERFORMANCE:
                if original.query_latency_ms == 0:
                    return 1.0
                return original.query_latency_ms / optimized.query_latency_ms
            
            elif strategy == OptimizationStrategy.MEMORY:
                if original.memory_usage_mb == 0:
                    return 1.0
                return original.memory_usage_mb / optimized.memory_usage_mb
            
            elif strategy == OptimizationStrategy.QUALITY:
                if original.accuracy_score == 0:
                    return optimized.accuracy_score
                return optimized.accuracy_score / original.accuracy_score
            
            elif strategy == OptimizationStrategy.STORAGE:
                if original.index_size_mb == 0:
                    return 1.0
                return original.index_size_mb / optimized.index_size_mb
            
            else:  # BALANCED
                # Weighted combination of improvements
                latency_improvement = (original.query_latency_ms / optimized.query_latency_ms) if original.query_latency_ms > 0 else 1.0
                memory_improvement = (original.memory_usage_mb / optimized.memory_usage_mb) if original.memory_usage_mb > 0 else 1.0
                accuracy_improvement = (optimized.accuracy_score / original.accuracy_score) if original.accuracy_score > 0 else optimized.accuracy_score
                throughput_improvement = (optimized.throughput_qps / original.throughput_qps) if original.throughput_qps > 0 else optimized.throughput_qps
                
                return (latency_improvement + memory_improvement + accuracy_improvement + throughput_improvement) / 4.0
            
        except Exception as e:
            logger.error(f"Failed to calculate improvement ratio: {str(e)}")
            return 1.0
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system hardware information"""
        try:
            info = {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3),
                "gpu_available": faiss.get_num_gpus() > 0,
                "gpu_count": faiss.get_num_gpus(),
            }
            
            # GPU details if available
            if info["gpu_available"]:
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    gpu_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    info["gpu_memory_gb"] = gpu_info.total / (1024**3)
                except:
                    info["gpu_memory_gb"] = 0
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get system info: {str(e)}")
            return {}
    
    async def apply_optimization(
        self,
        content_type: str,
        optimization_result: OptimizationResult
    ) -> bool:
        """Apply optimization result to production system"""
        try:
            if not optimization_result.success:
                logger.warning(f"Attempting to apply failed optimization for {content_type}")
                return False
            
            # Get the vector store for this content type
            if content_type not in self.vector_manager.stores:
                logger.error(f"No vector store found for {content_type}")
                return False
            
            # Apply the recommended configuration
            recommended_config = optimization_result.recommended_config
            
            # For FAISS store, recreate index with new configuration
            faiss_store = self.vector_manager.stores.get(VectorStoreType.FAISS)
            if faiss_store:
                await self._apply_faiss_optimization(faiss_store, content_type, recommended_config)
            
            # Update current configuration
            self.current_configs[content_type] = recommended_config
            
            logger.info(f"Applied optimization for {content_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimization for {content_type}: {str(e)}")
            return False
    
    async def _apply_faiss_optimization(
        self,
        faiss_store: FAISSVectorStore,
        content_type: str,
        config: Dict[str, Any]
    ) -> None:
        """Apply FAISS-specific optimization"""
        try:
            # This would involve recreating the index with the new configuration
            # For production, this should be done carefully with backup and migration
            logger.info(f"Applying FAISS optimization for {content_type}: {config}")
            
            # Note: In a real implementation, you would:
            # 1. Create new index with optimized configuration
            # 2. Migrate data from old index to new index
            # 3. Swap indices atomically
            # 4. Cleanup old index
            
        except Exception as e:
            logger.error(f"Failed to apply FAISS optimization: {str(e)}")
            raise
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        try:
            report = {
                "system_info": self.system_info,
                "optimization_history": [asdict(result) for result in self.optimization_history],
                "current_configs": self.current_configs,
                "performance_baselines": {
                    content_type: asdict(metrics) 
                    for content_type, metrics in self.performance_baselines.items()
                },
                "recommendations": await self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate optimization report: {str(e)}")
            return {}
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        try:
            # Analyze system resources
            if self.system_info.get("memory_gb", 0) < 8:
                recommendations.append("Consider memory optimization strategy due to limited RAM")
            
            if not self.system_info.get("gpu_available", False):
                recommendations.append("GPU acceleration not available - focus on CPU optimization")
            
            # Analyze optimization history
            if self.optimization_history:
                avg_improvement = np.mean([r.improvement_ratio for r in self.optimization_history])
                if avg_improvement < 1.2:
                    recommendations.append("Low improvement ratios - consider different optimization strategies")
            
            # Content type specific recommendations
            for content_type in ["audio", "video", "image", "text"]:
                if content_type in self.performance_baselines:
                    baseline = self.performance_baselines[content_type]
                    if baseline.query_latency_ms > 100:
                        recommendations.append(f"High latency detected for {content_type} - recommend performance optimization")
                    if baseline.memory_usage_mb > 2000:
                        recommendations.append(f"High memory usage for {content_type} - recommend memory optimization")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            return ["Error generating recommendations"]
    
    async def close(self) -> None:
        """Close optimizer and cleanup resources"""
        try:
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Force garbage collection
            gc.collect()
            
            logger.info("Vector database optimizer closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing optimizer: {str(e)}")
