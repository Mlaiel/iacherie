"""IA Influencer Agent - Fingerprinting Performance Metrics Collector
Enterprise metrics for AI fingerprinting algorithms and content matching

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Fingerprinting algorithm performance tracking
- Content matching accuracy metrics
- Vector similarity computation analytics
- Real-time processing performance
- Multi-modal content analysis metrics
- AI model performance optimization
"""
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, Summary

from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager

logger = get_logger(__name__)


class FingerprintAlgorithm(Enum):
    """Supported fingerprinting algorithms"""
    CHROMAPRINT = "chromaprint"
    ESSENTIA = "essentia"
    CLIP_IMAGE = "clip_image"
    CLIP_TEXT = "clip_text"
    OPENCV_PERCEPTUAL = "opencv_perceptual"
    BERT_EMBEDDING = "bert_embedding"
    ROBERTA_EMBEDDING = "roberta_embedding"
    YOLO_DETECTION = "yolo_detection"
    SPECTRAL_HASH = "spectral_hash"
    MFCC_FEATURES = "mfcc_features"
    CUSTOM_NEURAL = "custom_neural"


class ContentType(Enum):
    """Content types for fingerprinting"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MUSIC = "music"
    SPEECH = "speech"
    PODCAST = "podcast"


class ProcessingStage(Enum):
    """Fingerprinting processing stages"""
    PREPROCESSING = "preprocessing"
    FEATURE_EXTRACTION = "feature_extraction"
    VECTORIZATION = "vectorization"
    SIMILARITY_SEARCH = "similarity_search"
    POST_PROCESSING = "post_processing"


class MatchQuality(Enum):
    """Quality of content matches"""
    EXACT = "exact"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FALSE_POSITIVE = "false_positive"


@dataclass
class FingerprintingJob:
    """Fingerprinting job details"""
    job_id: str
    content_id: str
    content_type: ContentType
    algorithm: FingerprintAlgorithm
    file_size_mb: float
    duration_seconds: Optional[float]
    start_time: datetime
    user_id: str


@dataclass
class MatchResult:
    """Content matching result"""
    match_id: str
    original_fingerprint_id: str
    candidate_fingerprint_id: str
    similarity_score: float
    algorithm_used: FingerprintAlgorithm
    match_quality: MatchQuality
    processing_time_ms: float
    detected_at: datetime


class FingerprintingPerformanceMetricsCollector:
    """
    Advanced metrics collector for fingerprinting performance
    
    Tracks:
    - Algorithm performance and accuracy
    - Processing times and throughput
    - Vector similarity computation metrics
    - Content matching effectiveness
    - Resource utilization optimization
    - Real-time performance analytics
    """
    
    def __init__(self, prometheus_manager=None):
        self.prometheus_manager = prometheus_manager
        self.redis_manager = RedisManager()
        self.logger = logger
        self._active_jobs: Dict[str, FingerprintingJob] = {}
        self._performance_cache: Dict[str, List[float]] = {}
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize comprehensive fingerprinting metrics"""
        
        if not self.prometheus_manager:
            self.logger.warning("No Prometheus manager provided, metrics disabled")
            return
        
        # Core Fingerprinting Metrics
        self.fingerprints_created_total = Counter(
            'ia_influencer_fingerprints_created_total',
            'Total fingerprints created by algorithm and content type',
            ['algorithm', 'content_type', 'success', 'user_id', 'tenant_id']
        )
        
        self.fingerprint_processing_duration = Histogram(
            'ia_influencer_fingerprint_processing_duration_seconds',
            'Time to create fingerprints by algorithm and content type',
            ['algorithm', 'content_type', 'stage'],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600]
        )
        
        self.fingerprint_file_size = Histogram(
            'ia_influencer_fingerprint_file_size_mb',
            'File size distribution for fingerprinting',
            ['content_type', 'algorithm'],
            buckets=[0.1, 1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500]
        )
        
        # Algorithm Performance Metrics
        self.algorithm_accuracy_score = Gauge(
            'ia_influencer_algorithm_accuracy_score',
            'Algorithm accuracy score (0-100)',
            ['algorithm', 'content_type', 'time_window']
        )
        
        self.algorithm_precision = Gauge(
            'ia_influencer_algorithm_precision',
            'Algorithm precision (true positives / all positives)',
            ['algorithm', 'content_type', 'time_window']
        )
        
        self.algorithm_recall = Gauge(
            'ia_influencer_algorithm_recall',
            'Algorithm recall (true positives / all actual positives)',
            ['algorithm', 'content_type', 'time_window']
        )
        
        self.algorithm_f1_score = Gauge(
            'ia_influencer_algorithm_f1_score',
            'Algorithm F1 score (harmonic mean of precision and recall)',
            ['algorithm', 'content_type', 'time_window']
        )
        
        # Similarity Search Metrics
        self.similarity_searches_total = Counter(
            'ia_influencer_similarity_searches_total',
            'Total similarity searches performed',
            ['algorithm', 'content_type', 'vector_dimension', 'success']
        )
        
        self.similarity_search_duration = Histogram(
            'ia_influencer_similarity_search_duration_seconds',
            'Time for similarity searches in vector space',
            ['algorithm', 'vector_dimension', 'index_size_range'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10, 30]
        )
        
        self.similarity_score_distribution = Histogram(
            'ia_influencer_similarity_score_distribution',
            'Distribution of similarity scores',
            ['algorithm', 'content_type', 'match_quality'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
        )
        
        # Content Matching Metrics
        self.content_matches_found_total = Counter(
            'ia_influencer_content_matches_found_total',
            'Total content matches found by quality and algorithm',
            ['algorithm', 'content_type', 'match_quality', 'user_id']
        )
        
        self.match_detection_latency = Histogram(
            'ia_influencer_match_detection_latency_ms',
            'Latency from fingerprint creation to match detection',
            ['algorithm', 'content_type'],
            buckets=[1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 30000]
        )
        
        self.false_positive_rate = Gauge(
            'ia_influencer_false_positive_rate_percent',
            'False positive rate by algorithm and content type',
            ['algorithm', 'content_type', 'time_window']
        )
        
        self.false_negative_rate = Gauge(
            'ia_influencer_false_negative_rate_percent',
            'False negative rate by algorithm and content type',
            ['algorithm', 'content_type', 'time_window']
        )
        
        # Vector Database Metrics
        self.vector_index_size = Gauge(
            'ia_influencer_vector_index_size',
            'Number of vectors in the index by content type',
            ['content_type', 'algorithm', 'index_name']
        )
        
        self.vector_insertion_duration = Histogram(
            'ia_influencer_vector_insertion_duration_seconds',
            'Time to insert vectors into the index',
            ['content_type', 'algorithm', 'batch_size_range'],
            buckets=[0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10, 30]
        )
        
        self.vector_memory_usage = Gauge(
            'ia_influencer_vector_memory_usage_mb',
            'Memory usage of vector indexes',
            ['content_type', 'algorithm', 'index_name']
        )
        
        # Resource Utilization Metrics
        self.fingerprinting_cpu_usage = Gauge(
            'ia_influencer_fingerprinting_cpu_usage_percent',
            'CPU usage during fingerprinting operations',
            ['algorithm', 'content_type', 'worker_id']
        )
        
        self.fingerprinting_memory_usage = Gauge(
            'ia_influencer_fingerprinting_memory_usage_mb',
            'Memory usage during fingerprinting operations',
            ['algorithm', 'content_type', 'worker_id']
        )
        
        self.gpu_utilization = Gauge(
            'ia_influencer_gpu_utilization_percent',
            'GPU utilization for AI fingerprinting algorithms',
            ['algorithm', 'gpu_id', 'model_name']
        )
        
        # Throughput Metrics
        self.fingerprinting_throughput = Gauge(
            'ia_influencer_fingerprinting_throughput_per_second',
            'Fingerprinting throughput (files per second)',
            ['algorithm', 'content_type', 'worker_count']
        )
        
        self.batch_processing_efficiency = Gauge(
            'ia_influencer_batch_processing_efficiency_percent',
            'Efficiency of batch processing operations',
            ['algorithm', 'batch_size_range', 'content_type']
        )
        
        # Quality Metrics
        self.fingerprint_uniqueness_score = Gauge(
            'ia_influencer_fingerprint_uniqueness_score',
            'Uniqueness score of generated fingerprints',
            ['algorithm', 'content_type', 'time_window']
        )
        
        self.fingerprint_stability_score = Gauge(
            'ia_influencer_fingerprint_stability_score',
            'Stability score (consistency across multiple extractions)',
            ['algorithm', 'content_type', 'time_window']
        )
        
        # Register all metrics
        self._register_metrics()
        
        self.logger.info("Fingerprinting performance metrics initialized")
    
    def _register_metrics(self) -> None:
        """Register all metrics with Prometheus manager"""
        
        metrics_to_register = [
            self.fingerprints_created_total,
            self.fingerprint_processing_duration,
            self.fingerprint_file_size,
            self.algorithm_accuracy_score,
            self.algorithm_precision,
            self.algorithm_recall,
            self.algorithm_f1_score,
            self.similarity_searches_total,
            self.similarity_search_duration,
            self.similarity_score_distribution,
            self.content_matches_found_total,
            self.match_detection_latency,
            self.false_positive_rate,
            self.false_negative_rate,
            self.vector_index_size,
            self.vector_insertion_duration,
            self.vector_memory_usage,
            self.fingerprinting_cpu_usage,
            self.fingerprinting_memory_usage,
            self.gpu_utilization,
            self.fingerprinting_throughput,
            self.batch_processing_efficiency,
            self.fingerprint_uniqueness_score,
            self.fingerprint_stability_score
        ]
        
        for metric in metrics_to_register:
            self.prometheus_manager.register_metric(metric)
    
    async def start_fingerprinting_job(
        self,
        job: FingerprintingJob,
        tenant_id: str = "default"
    ) -> None:
        """Start tracking a fingerprinting job"""
        
        self._active_jobs[job.job_id] = job
        
        # Record file size metrics
        self.fingerprint_file_size.labels(
            content_type=job.content_type.value,
            algorithm=job.algorithm.value
        ).observe(job.file_size_mb)
        
        # Store job in Redis
        await self.redis_manager.set(
            f"fingerprinting_job:{job.job_id}",
            job.__dict__,
            ttl=86400  # 24 hours
        )
        
        self.logger.info(
            f"Started fingerprinting job {job.job_id}: "
            f"{job.algorithm.value} on {job.content_type.value}"
        )
    
    async def record_processing_stage(
        self,
        job_id: str,
        stage: ProcessingStage,
        duration_seconds: float,
        success: bool = True
    ) -> None:
        """Record processing stage completion"""
        
        if job_id not in self._active_jobs:
            self.logger.warning(f"Job {job_id} not found in active jobs")
            return
        
        job = self._active_jobs[job_id]
        
        self.fingerprint_processing_duration.labels(
            algorithm=job.algorithm.value,
            content_type=job.content_type.value,
            stage=stage.value
        ).observe(duration_seconds)
        
        self.logger.debug(
            f"Job {job_id} completed stage {stage.value} in {duration_seconds:.3f}s"
        )
    
    async def complete_fingerprinting_job(
        self,
        job_id: str,
        success: bool,
        fingerprint_vector: Optional[np.ndarray] = None,
        total_duration_seconds: float = None,
        tenant_id: str = "default"
    ) -> None:
        """Complete a fingerprinting job"""
        
        if job_id not in self._active_jobs:
            self.logger.warning(f"Job {job_id} not found in active jobs")
            return
        
        job = self._active_jobs[job_id]
        end_time = datetime.utcnow()
        
        if total_duration_seconds is None:
            total_duration_seconds = (end_time - job.start_time).total_seconds()
        
        # Update core metrics
        self.fingerprints_created_total.labels(
            algorithm=job.algorithm.value,
            content_type=job.content_type.value,
            success=str(success).lower(),
            user_id=job.user_id,
            tenant_id=tenant_id
        ).inc()
        
        # Record processing duration if successful
        if success:
            self.fingerprint_processing_duration.labels(
                algorithm=job.algorithm.value,
                content_type=job.content_type.value,
                stage="total"
            ).observe(total_duration_seconds)
            
            # Calculate and store performance metrics
            await self._update_performance_cache(job, total_duration_seconds)
        
        # Clean up job
        del self._active_jobs[job_id]
        await self.redis_manager.delete(f"fingerprinting_job:{job_id}")
        
        # Store completed job
        await self.redis_manager.set(
            f"completed_fingerprinting_job:{job_id}",
            {
                **job.__dict__,
                "success": success,
                "total_duration_seconds": total_duration_seconds,
                "completed_at": end_time.isoformat()
            },
            ttl=604800  # 7 days
        )
        
        self.logger.info(
            f"Completed fingerprinting job {job_id}: "
            f"{'success' if success else 'failed'} in {total_duration_seconds:.3f}s"
        )
    
    async def record_similarity_search(
        self,
        algorithm: FingerprintAlgorithm,
        content_type: ContentType,
        vector_dimension: int,
        index_size: int,
        search_duration_seconds: float,
        results_count: int,
        success: bool = True
    ) -> None:
        """Record similarity search performance"""
        
        # Determine index size range for grouping
        if index_size < 1000:
            size_range = "small"
        elif index_size < 10000:
            size_range = "medium"
        elif index_size < 100000:
            size_range = "large"
        else:
            size_range = "xlarge"
        
        self.similarity_searches_total.labels(
            algorithm=algorithm.value,
            content_type=content_type.value,
            vector_dimension=str(vector_dimension),
            success=str(success).lower()
        ).inc()
        
        if success:
            self.similarity_search_duration.labels(
                algorithm=algorithm.value,
                vector_dimension=str(vector_dimension),
                index_size_range=size_range
            ).observe(search_duration_seconds)
        
        self.logger.debug(
            f"Similarity search: {algorithm.value} on {content_type.value}, "
            f"{results_count} results in {search_duration_seconds:.3f}s"
        )
    
    async def record_content_match(
        self,
        match: MatchResult,
        user_id: str
    ) -> None:
        """Record detected content match"""
        
        self.content_matches_found_total.labels(
            algorithm=match.algorithm_used.value,
            content_type="unknown",  # Could be extracted from fingerprint
            match_quality=match.match_quality.value,
            user_id=user_id
        ).inc()
        
        self.similarity_score_distribution.labels(
            algorithm=match.algorithm_used.value,
            content_type="unknown",
            match_quality=match.match_quality.value
        ).observe(match.similarity_score)
        
        self.match_detection_latency.labels(
            algorithm=match.algorithm_used.value,
            content_type="unknown"
        ).observe(match.processing_time_ms)
        
        # Store match for analysis
        await self.redis_manager.set(
            f"content_match:{match.match_id}",
            match.__dict__,
            ttl=2592000  # 30 days
        )
        
        self.logger.info(
            f"Content match recorded: {match.match_id} "
            f"(similarity: {match.similarity_score:.3f}, quality: {match.match_quality.value})"
        )
    
    async def update_algorithm_performance(
        self,
        algorithm: FingerprintAlgorithm,
        content_type: ContentType,
        accuracy: float,
        precision: float,
        recall: float,
        time_window: str = "1h"
    ) -> None:
        """Update algorithm performance metrics"""
        
        self.algorithm_accuracy_score.labels(
            algorithm=algorithm.value,
            content_type=content_type.value,
            time_window=time_window
        ).set(accuracy * 100)  # Convert to percentage
        
        self.algorithm_precision.labels(
            algorithm=algorithm.value,
            content_type=content_type.value,
            time_window=time_window
        ).set(precision)
        
        self.algorithm_recall.labels(
            algorithm=algorithm.value,
            content_type=content_type.value,
            time_window=time_window
        ).set(recall)
        
        # Calculate F1 score
        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
            self.algorithm_f1_score.labels(
                algorithm=algorithm.value,
                content_type=content_type.value,
                time_window=time_window
            ).set(f1_score)
        
        self.logger.info(
            f"Updated {algorithm.value} performance for {content_type.value}: "
            f"accuracy={accuracy:.3f}, precision={precision:.3f}, recall={recall:.3f}"
        )
    
    async def update_vector_index_metrics(
        self,
        content_type: ContentType,
        algorithm: FingerprintAlgorithm,
        index_name: str,
        size: int,
        memory_usage_mb: float
    ) -> None:
        """Update vector index metrics"""
        
        self.vector_index_size.labels(
            content_type=content_type.value,
            algorithm=algorithm.value,
            index_name=index_name
        ).set(size)
        
        self.vector_memory_usage.labels(
            content_type=content_type.value,
            algorithm=algorithm.value,
            index_name=index_name
        ).set(memory_usage_mb)
    
    async def update_resource_utilization(
        self,
        algorithm: FingerprintAlgorithm,
        content_type: ContentType,
        worker_id: str,
        cpu_percent: float,
        memory_mb: float,
        gpu_percent: Optional[float] = None,
        gpu_id: Optional[str] = None
    ) -> None:
        """Update resource utilization metrics"""
        
        self.fingerprinting_cpu_usage.labels(
            algorithm=algorithm.value,
            content_type=content_type.value,
            worker_id=worker_id
        ).set(cpu_percent)
        
        self.fingerprinting_memory_usage.labels(
            algorithm=algorithm.value,
            content_type=content_type.value,
            worker_id=worker_id
        ).set(memory_mb)
        
        if gpu_percent is not None and gpu_id is not None:
            self.gpu_utilization.labels(
                algorithm=algorithm.value,
                gpu_id=gpu_id,
                model_name=algorithm.value  # Could be more specific
            ).set(gpu_percent)
    
    async def update_throughput_metrics(
        self,
        algorithm: FingerprintAlgorithm,
        content_type: ContentType,
        throughput_per_second: float,
        worker_count: int
    ) -> None:
        """Update throughput metrics"""
        
        self.fingerprinting_throughput.labels(
            algorithm=algorithm.value,
            content_type=content_type.value,
            worker_count=str(worker_count)
        ).set(throughput_per_second)
    
    async def _update_performance_cache(
        self,
        job: FingerprintingJob,
        duration: float
    ) -> None:
        """Update performance cache for trend analysis"""
        
        cache_key = f"{job.algorithm.value}:{job.content_type.value}"
        
        if cache_key not in self._performance_cache:
            self._performance_cache[cache_key] = []
        
        self._performance_cache[cache_key].append(duration)
        
        # Keep only last 100 measurements
        if len(self._performance_cache[cache_key]) > 100:
            self._performance_cache[cache_key] = self._performance_cache[cache_key][-100:]
    
    async def get_performance_summary(
        self,
        algorithm: Optional[FingerprintAlgorithm] = None,
        content_type: Optional[ContentType] = None
    ) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_jobs": len(self._active_jobs),
            "algorithm_performance": {},
            "overall_statistics": {}
        }
        
        # Filter by criteria if provided
        jobs = list(self._active_jobs.values())
        if algorithm:
            jobs = [j for j in jobs if j.algorithm == algorithm]
        if content_type:
            jobs = [j for j in jobs if j.content_type == content_type]
        
        # Calculate statistics
        if jobs:
            summary["overall_statistics"] = {
                "total_active_jobs": len(jobs),
                "algorithms_in_use": len(set(j.algorithm for j in jobs)),
                "content_types_processing": len(set(j.content_type for j in jobs)),
                "users_active": len(set(j.user_id for j in jobs))
            }
        
        return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the fingerprinting metrics collector"""
        
        return {
            "status": "healthy",
            "active_jobs": len(self._active_jobs),
            "performance_cache_size": sum(len(v) for v in self._performance_cache.values()),
            "metrics_initialized": self.prometheus_manager is not None,
            "redis_connected": self.redis_manager is not None,
            "last_updated": datetime.utcnow().isoformat()
        }
