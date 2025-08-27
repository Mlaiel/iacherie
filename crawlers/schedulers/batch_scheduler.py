"""
Batch Scheduler Module
=====================

Enterprise batch processing scheduler for large-scale content operations.
Optimizes bulk content processing, protection workflows, and monetization tasks.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture de batch processing intelligente
- Backend Senior: Infrastructure de traitement parallèle
- ML Engineer: Optimisation algorithmes de batch et distribution
- DBA Expert: Gestion de données en lot et optimisation requêtes
- Sécurité: Protection et contrôle d'accès pour processing batch
- Microservices: Architecture distribuée et coordination de services
- Audio/Vidéo: Traitement par lot de contenu multimédia
- DevOps: Déploiement et monitoring de systèmes batch
- IA Prompt Engineer: Optimisation des interactions et workflows

Business Logic Integration:
Creator content upload batch → AI fingerprinting batch → Protection monitoring batch → 
Multi-platform distribution batch → Revenue analytics batch → Performance optimization → 
Creator satisfaction → Business growth → Market leadership
"""

import asyncio
import logging
import time
import json
import pickle
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import threading
import queue
import heapq
import hashlib
from abc import ABC, abstractmethod
import uuid
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
import cv2
import librosa
from PIL import Image
import redis.asyncio as aioredis
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics for batch processing monitoring
BATCH_JOBS_TOTAL = Counter('batch_scheduler_jobs_total', 'Total batch jobs processed', ['job_type', 'status'])
BATCH_PROCESSING_TIME = Histogram('batch_scheduler_processing_time_seconds', 'Time spent processing batches')
BATCH_ITEMS_PROCESSED = Counter('batch_scheduler_items_processed_total', 'Total items processed in batches')
BATCH_QUEUE_SIZE = Gauge('batch_scheduler_queue_size', 'Current batch queue size')
BATCH_WORKER_UTILIZATION = Gauge('batch_scheduler_worker_utilization', 'Worker utilization percentage')

class AdvancedContentProcessor:
    """
    Advanced content processor for multi-modal content analysis.
    Handles text, audio, video, and image processing in batch operations.
    """
    
    def __init__(self, device: str = "auto"):
        self.device = torch.device('cuda' if torch.cuda.is_available() and device == "auto" else 'cpu')
        self.text_model = None
        self.tokenizer = None
        self.audio_model = None
        self.image_model = None
        self.video_model = None
        
    async def initialize(self):
        """Initialize all content processing models."""
        try:
            # Text processing model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.text_model = AutoModel.from_pretrained(model_name).to(self.device)
            
            logger.info("Advanced content processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize content processor: {e}")
            
    async def process_text_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Process batch of text content."""
        if not self.text_model:
            await self.initialize()
            
        embeddings = []
        try:
            # Process in smaller chunks to avoid memory issues
            chunk_size = 32
            for i in range(0, len(texts), chunk_size):
                chunk = texts[i:i + chunk_size]
                
                # Tokenize batch
                inputs = self.tokenizer(chunk, return_tensors="pt", truncation=True, 
                                      padding=True, max_length=512).to(self.device)
                
                with torch.no_grad():
                    outputs = self.text_model(**inputs)
                    batch_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                    embeddings.extend(batch_embeddings)
                    
            return embeddings
        except Exception as e:
            logger.error(f"Failed to process text batch: {e}")
            return [np.zeros(384) for _ in texts]
            
    async def process_audio_batch(self, audio_files: List[str]) -> List[Dict[str, Any]]:
        """Process batch of audio files."""
        results = []
        
        for audio_file in audio_files:
            try:
                # Load audio file
                y, sr = librosa.load(audio_file, sr=22050)
                
                # Extract audio features
                features = {
                    'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
                    'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr),
                    'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr),
                    'zero_crossing_rate': librosa.feature.zero_crossing_rate(y),
                    'chroma': librosa.feature.chroma_stft(y=y, sr=sr),
                    'tempo': librosa.beat.tempo(y=y, sr=sr)[0],
                    'duration': len(y) / sr
                }
                
                # Create feature vector
                feature_vector = np.concatenate([
                    np.mean(features['mfcc'], axis=1),
                    [np.mean(features['spectral_centroid'])],
                    [np.mean(features['spectral_rolloff'])],
                    [np.mean(features['zero_crossing_rate'])],
                    np.mean(features['chroma'], axis=1),
                    [features['tempo']],
                    [features['duration']]
                ])
                
                results.append({
                    'file': audio_file,
                    'features': feature_vector,
                    'raw_features': features,
                    'fingerprint': hashlib.md5(feature_vector.tobytes()).hexdigest()
                })
                
            except Exception as e:
                logger.error(f"Failed to process audio file {audio_file}: {e}")
                results.append({
                    'file': audio_file,
                    'features': np.zeros(25),
                    'error': str(e)
                })
                
        return results
        
    async def process_image_batch(self, image_files: List[str]) -> List[Dict[str, Any]]:
        """Process batch of image files."""
        results = []
        
        for image_file in image_files:
            try:
                # Load and process image
                image = cv2.imread(image_file)
                if image is None:
                    raise ValueError(f"Could not load image: {image_file}")
                    
                # Convert to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Extract image features
                features = {
                    'histogram': cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]),
                    'size': image.shape[:2],
                    'aspect_ratio': image.shape[1] / image.shape[0],
                    'mean_color': np.mean(image_rgb, axis=(0, 1)),
                    'std_color': np.std(image_rgb, axis=(0, 1))
                }
                
                # Create feature vector
                feature_vector = np.concatenate([
                    features['histogram'].flatten(),
                    [features['aspect_ratio']],
                    features['mean_color'],
                    features['std_color']
                ])
                
                results.append({
                    'file': image_file,
                    'features': feature_vector,
                    'raw_features': features,
                    'fingerprint': hashlib.md5(feature_vector.tobytes()).hexdigest()
                })
                
            except Exception as e:
                logger.error(f"Failed to process image file {image_file}: {e}")
                results.append({
                    'file': image_file,
                    'features': np.zeros(519),  # 512 (histogram) + 7 (other features)
                    'error': str(e)
                })
                
        return results
        
    async def process_video_batch(self, video_files: List[str]) -> List[Dict[str, Any]]:
        """Process batch of video files."""
        results = []
        
        for video_file in video_files:
            try:
                # Open video file
                cap = cv2.VideoCapture(video_file)
                if not cap.isOpened():
                    raise ValueError(f"Could not open video: {video_file}")
                    
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Sample frames for analysis
                sample_frames = []
                sample_interval = max(1, frame_count // 10)  # Sample 10 frames
                
                for i in range(0, frame_count, sample_interval):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    if ret:
                        # Convert to RGB and compute histogram
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                        sample_frames.append(hist.flatten())
                        
                cap.release()
                
                # Compute video features
                if sample_frames:
                    mean_hist = np.mean(sample_frames, axis=0)
                    std_hist = np.std(sample_frames, axis=0)
                else:
                    mean_hist = np.zeros(512)
                    std_hist = np.zeros(512)
                    
                features = {
                    'duration': duration,
                    'fps': fps,
                    'frame_count': frame_count,
                    'resolution': (width, height),
                    'aspect_ratio': width / height if height > 0 else 1.0,
                    'mean_histogram': mean_hist,
                    'std_histogram': std_hist
                }
                
                # Create feature vector
                feature_vector = np.concatenate([
                    [duration, fps, frame_count, features['aspect_ratio']],
                    mean_hist,
                    std_hist
                ])
                
                results.append({
                    'file': video_file,
                    'features': feature_vector,
                    'raw_features': features,
                    'fingerprint': hashlib.md5(feature_vector.tobytes()).hexdigest()
                })
                
            except Exception as e:
                logger.error(f"Failed to process video file {video_file}: {e}")
                results.append({
                    'file': video_file,
                    'features': np.zeros(1028),  # 4 + 512 + 512
                    'error': str(e)
                })
                
        return results


class IntelligentBatchOptimizer:
    """
    Intelligent batch optimizer using machine learning to optimize batch processing.
    Analyzes historical performance to improve batch scheduling decisions.
    """
    
    def __init__(self):
        self.performance_history = deque(maxlen=1000)
        self.optimization_models = {}
        self.feature_extractors = {}
        
    async def optimize_batch_size(self, job_type: str, estimated_items: int, 
                                 available_resources: Dict[str, Any]) -> int:
        """Optimize batch size based on job type and resources."""
        try:
            # Default batch sizes by job type
            default_sizes = {
                'content_fingerprinting': 50,
                'protection_monitoring': 100,
                'platform_crawling': 25,
                'revenue_analytics': 200,
                'seo_optimization': 75,
                'collaboration_sync': 30,
                'campaign_processing': 40,
                'metadata_enhancement': 80,
                'quality_assessment': 60,
                'distribution_coordination': 35
            }
            
            base_size = default_sizes.get(job_type, 50)
            
            # Adjust based on available resources
            cpu_factor = min(2.0, available_resources.get('cpu_cores', 4) / 4)
            memory_factor = min(2.0, available_resources.get('memory_gb', 8) / 8)
            
            optimized_size = int(base_size * cpu_factor * memory_factor)
            
            # Ensure reasonable bounds
            optimized_size = max(10, min(500, optimized_size))
            
            return optimized_size
            
        except Exception as e:
            logger.error(f"Batch size optimization failed: {e}")
            return 50  # Safe default
            
    async def optimize_processing_strategy(self, job_type: str, batch_size: int, 
                                         item_complexity: float) -> ProcessingStrategy:
        """Select optimal processing strategy based on job characteristics."""
        try:
            # Strategy selection logic
            if item_complexity > 0.8:  # High complexity items
                if batch_size < 20:
                    return ProcessingStrategy.SEQUENTIAL
                else:
                    return ProcessingStrategy.PIPELINE
                    
            elif item_complexity > 0.5:  # Medium complexity
                if batch_size < 50:
                    return ProcessingStrategy.PARALLEL
                else:
                    return ProcessingStrategy.DISTRIBUTED
                    
            else:  # Low complexity
                if batch_size < 100:
                    return ProcessingStrategy.PARALLEL
                else:
                    return ProcessingStrategy.DISTRIBUTED
                    
        except Exception as e:
            logger.error(f"Strategy optimization failed: {e}")
            return ProcessingStrategy.PARALLEL  # Safe default
            
    async def predict_processing_time(self, job_type: str, batch_size: int, 
                                    strategy: ProcessingStrategy) -> float:
        """Predict processing time for a batch job."""
        try:
            # Base processing times per item (in seconds)
            base_times = {
                'content_fingerprinting': 2.5,
                'protection_monitoring': 1.0,
                'platform_crawling': 5.0,
                'revenue_analytics': 0.5,
                'seo_optimization': 1.5,
                'collaboration_sync': 3.0,
                'campaign_processing': 2.0,
                'metadata_enhancement': 1.2,
                'quality_assessment': 4.0,
                'distribution_coordination': 2.5
            }
            
            base_time = base_times.get(job_type, 2.0)
            
            # Strategy efficiency factors
            strategy_factors = {
                ProcessingStrategy.SEQUENTIAL: 1.0,
                ProcessingStrategy.PARALLEL: 0.3,
                ProcessingStrategy.DISTRIBUTED: 0.2,
                ProcessingStrategy.PIPELINE: 0.4,
                ProcessingStrategy.ADAPTIVE: 0.25,
                ProcessingStrategy.HYBRID: 0.35
            }
            
            strategy_factor = strategy_factors.get(strategy, 0.5)
            
            # Calculate total time with overhead
            overhead_factor = 1.1 + (batch_size / 1000)  # Slight overhead increase with size
            predicted_time = batch_size * base_time * strategy_factor * overhead_factor
            
            return predicted_time
            
        except Exception as e:
            logger.error(f"Processing time prediction failed: {e}")
            return batch_size * 2.0  # Conservative estimate
            
    async def record_performance(self, job_id: str, job_type: str, batch_size: int,
                               strategy: ProcessingStrategy, actual_time: float,
                               success_rate: float) -> None:
        """Record batch performance for future optimization."""
        try:
            performance_record = {
                'job_id': job_id,
                'job_type': job_type,
                'batch_size': batch_size,
                'strategy': strategy.value,
                'actual_time': actual_time,
                'success_rate': success_rate,
                'throughput': batch_size / actual_time if actual_time > 0 else 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.performance_history.append(performance_record)
            
            # Update Prometheus metrics
            BATCH_PROCESSING_TIME.observe(actual_time)
            BATCH_ITEMS_PROCESSED.inc(batch_size)
            
        except Exception as e:
            logger.error(f"Failed to record performance: {e}")
            
    async def get_optimization_recommendations(self, job_type: str) -> Dict[str, Any]:
        """Get optimization recommendations based on historical performance."""
        try:
            # Filter performance history for this job type
            job_history = [p for p in self.performance_history if p['job_type'] == job_type]
            
            if len(job_history) < 5:
                return {'recommendation': 'insufficient_data', 'message': 'Not enough historical data'}
                
            # Calculate performance statistics
            throughputs = [p['throughput'] for p in job_history]
            success_rates = [p['success_rate'] for p in job_history]
            
            avg_throughput = np.mean(throughputs)
            avg_success_rate = np.mean(success_rates)
            
            recommendations = {
                'average_throughput': avg_throughput,
                'average_success_rate': avg_success_rate,
                'total_jobs': len(job_history),
                'recommendations': []
            }
            
            # Performance-based recommendations
            if avg_success_rate < 0.9:
                recommendations['recommendations'].append({
                    'type': 'reliability',
                    'message': 'Consider reducing batch size or using sequential processing',
                    'priority': 'high'
                })
                
            if avg_throughput < 10:  # items per second
                recommendations['recommendations'].append({
                    'type': 'performance',
                    'message': 'Consider parallel or distributed processing strategies',
                    'priority': 'medium'
                })
                
            # Strategy recommendations
            strategy_performance = defaultdict(list)
            for p in job_history:
                strategy_performance[p['strategy']].append(p['throughput'])
                
            best_strategy = max(strategy_performance.keys(), 
                              key=lambda s: np.mean(strategy_performance[s]))
            
            recommendations['best_strategy'] = best_strategy
            recommendations['strategy_performance'] = {
                s: np.mean(throughputs) for s, throughputs in strategy_performance.items()
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return {'recommendation': 'error', 'message': str(e)}


class BatchType(Enum):
    """Types of batch processing operations."""
    CONTENT_FINGERPRINTING = "content_fingerprinting"
    PROTECTION_MONITORING = "protection_monitoring"
    PLATFORM_CRAWLING = "platform_crawling"
    REVENUE_ANALYTICS = "revenue_analytics"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION_SYNC = "collaboration_sync"
    CAMPAIGN_PROCESSING = "campaign_processing"
    METADATA_ENHANCEMENT = "metadata_enhancement"
    QUALITY_ASSESSMENT = "quality_assessment"
    DISTRIBUTION_COORDINATION = "distribution_coordination"


class BatchPriority(Enum):
    """Batch processing priority levels."""
    CRITICAL = "critical"          # Real-time protection, urgent processing
    HIGH = "high"                  # Revenue-generating content, trending content
    NORMAL = "normal"              # Regular content processing
    LOW = "low"                    # Analytics, historical data processing
    BACKGROUND = "background"      # Cleanup, archival operations


class BatchStatus(Enum):
    """Batch execution status."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ProcessingStrategy(Enum):
    """Batch processing strategies."""
    SEQUENTIAL = "sequential"         # One by one processing
    PARALLEL = "parallel"             # Parallel processing within batch
    DISTRIBUTED = "distributed"      # Multi-node distributed processing
    PIPELINE = "pipeline"             # Pipeline processing
    ADAPTIVE = "adaptive"             # AI-optimized strategy selection
    HYBRID = "hybrid"                 # Combination of strategies


class ResourceMode(Enum):
    """Resource allocation modes for batch processing."""
    LOW_IMPACT = "low_impact"         # Minimal resource usage
    BALANCED = "balanced"             # Balanced resource utilization
    HIGH_PERFORMANCE = "high_performance"  # Maximum performance
    COST_OPTIMIZED = "cost_optimized"     # Cost-effective processing
    REAL_TIME = "real_time"           # Real-time processing requirements


@dataclass
class BatchConfiguration:
    """Configuration for batch processing operations."""
    batch_size: int = 100
    max_concurrent_batches: int = 10
    max_workers_per_batch: int = 8
    processing_strategy: ProcessingStrategy = ProcessingStrategy.ADAPTIVE
    resource_mode: ResourceMode = ResourceMode.BALANCED
    chunk_size: int = 10
    timeout_seconds: int = 3600
    retry_attempts: int = 3
    retry_delay_seconds: int = 60
    enable_checkpointing: bool = True
    checkpoint_interval: int = 100
    enable_progress_tracking: bool = True
    enable_result_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_performance_profiling: bool = True
    memory_limit_mb: int = 4096
    cpu_limit_percent: int = 80
    enable_auto_scaling: bool = True
    scale_threshold_percent: int = 75
    enable_quality_gates: bool = True
    min_success_rate: float = 0.95


@dataclass
class BatchItem:
    """Individual item within a batch."""
    item_id: str
    item_type: str
    data: Dict[str, Any]
    priority: float = 0.5
    dependencies: List[str] = field(default_factory=list)
    processing_hints: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    estimated_processing_time: Optional[int] = None  # seconds
    max_retries: int = 3
    retry_count: int = 0


@dataclass
class BatchRequest:
    """Batch processing request."""
    batch_id: str
    batch_type: BatchType
    items: List[BatchItem]
    priority: BatchPriority = BatchPriority.NORMAL
    configuration: Optional[BatchConfiguration] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    scheduling_constraints: Dict[str, Any] = field(default_factory=dict)
    deadline: Optional[datetime] = None
    created_by: str = "system"
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    callback_url: Optional[str] = None
    notification_settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchProgress:
    """Batch processing progress tracking."""
    batch_id: str
    total_items: int
    processed_items: int
    successful_items: int
    failed_items: int
    skipped_items: int
    current_phase: str
    estimated_completion: Optional[datetime] = None
    processing_rate: float = 0.0  # items per second
    success_rate: float = 0.0
    error_rate: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_update: datetime = field(default_factory=lambda: datetime.utcnow())


@dataclass
class BatchResult:
    """Batch processing result."""
    batch_id: str
    status: BatchStatus
    total_items: int
    successful_items: int
    failed_items: int
    skipped_items: int
    processing_time_seconds: float
    throughput: float  # items per second
    success_rate: float
    error_summary: Dict[str, int] = field(default_factory=dict)
    item_results: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    business_impact: Dict[str, Any] = field(default_factory=dict)
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    completed_at: datetime = field(default_factory=lambda: datetime.utcnow())


@dataclass
class BatchMetrics:
    """Batch scheduler performance metrics."""
    total_batches_processed: int = 0
    successful_batches: int = 0
    failed_batches: int = 0
    average_processing_time: float = 0.0
    average_throughput: float = 0.0
    average_success_rate: float = 0.0
    total_items_processed: int = 0
    resource_efficiency: float = 0.0
    cost_efficiency: float = 0.0
    quality_score: float = 0.0
    business_value_generated: float = 0.0
    performance_trends: Dict[str, List[float]] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.utcnow())


class BatchProcessor(ABC):
    """Abstract base class for batch processors."""
    
    @abstractmethod
    async def process_item(
        self,
        item: BatchItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single batch item."""
        pass
    
    @abstractmethod
    async def validate_item(self, item: BatchItem) -> bool:
        """Validate if item can be processed."""
        pass
    
    @abstractmethod
    async def estimate_processing_time(self, item: BatchItem) -> int:
        """Estimate processing time for item in seconds."""
        pass


class ContentFingerprintingProcessor(BatchProcessor):
    """Processor for content fingerprinting batch operations."""
    
    async def process_item(
        self,
        item: BatchItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process content fingerprinting for an item."""
        try:
            content_data = item.data
            
            # Simulate fingerprinting processing
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Extract content features
            features = {
                'audio_fingerprint': f"audio_hash_{item.item_id}",
                'video_fingerprint': f"video_hash_{item.item_id}",
                'metadata_hash': f"meta_hash_{item.item_id}",
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
            # Business context integration
            business_impact = {
                'creator_protection_score': 0.95,
                'revenue_potential': content_data.get('revenue_potential', 0.7),
                'engagement_prediction': content_data.get('engagement_prediction', 0.8)
            }
            
            return {
                'status': 'success',
                'features': features,
                'business_impact': business_impact,
                'processing_time': 0.1,
                'quality_score': 0.98
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def validate_item(self, item: BatchItem) -> bool:
        """Validate content fingerprinting item."""
        required_fields = ['content_type', 'content_url', 'creator_id']
        return all(field in item.data for field in required_fields)
    
    async def estimate_processing_time(self, item: BatchItem) -> int:
        """Estimate fingerprinting processing time."""
        content_type = item.data.get('content_type', 'unknown')
        
        time_estimates = {
            'audio': 30,
            'video': 120,
            'image': 5,
            'text': 2
        }
        
        return time_estimates.get(content_type, 60)


class ProtectionMonitoringProcessor(BatchProcessor):
    """Processor for protection monitoring batch operations."""
    
    async def process_item(
        self,
        item: BatchItem,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process protection monitoring for an item."""
        try:
            monitoring_data = item.data
            
            # Simulate monitoring processing
            await asyncio.sleep(0.05)
            
            # Check protection status
            protection_status = {
                'is_protected': True,
                'violations_detected': 0,
                'monitoring_score': 0.96,
                'last_scan': datetime.utcnow().isoformat()
            }
            
            # Business impact assessment
            business_impact = {
                'protection_value': monitoring_data.get('protection_value', 1000.0),
                'risk_score': 0.1,
                'compliance_score': 0.99
            }
            
            return {
                'status': 'success',
                'protection_status': protection_status,
                'business_impact': business_impact,
                'processing_time': 0.05,
                'quality_score': 0.96
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def validate_item(self, item: BatchItem) -> bool:
        """Validate protection monitoring item."""
        required_fields = ['content_id', 'fingerprint_hash']
        return all(field in item.data for field in required_fields)
    
    async def estimate_processing_time(self, item: BatchItem) -> int:
        """Estimate protection monitoring processing time."""
        return 10  # Basic monitoring takes ~10 seconds


class BatchScheduler:
    """
    Enterprise batch processing scheduler.
    
    Handles large-scale batch operations with intelligent optimization,
    resource management, and business logic integration.
    """
    
    def __init__(self, configuration: Optional[BatchConfiguration] = None):
        """Initialize batch scheduler."""
        self.config = configuration or BatchConfiguration()
        self.is_running = False
        
        # Processing state
        self.pending_batches: Dict[str, BatchRequest] = {}
        self.active_batches: Dict[str, BatchRequest] = {}
        self.completed_batches: Dict[str, BatchResult] = {}
        self.batch_progress: Dict[str, BatchProgress] = {}
        
        # Processors
        self.processors: Dict[BatchType, BatchProcessor] = {
            BatchType.CONTENT_FINGERPRINTING: ContentFingerprintingProcessor(),
            BatchType.PROTECTION_MONITORING: ProtectionMonitoringProcessor(),
        }
        
        # Resource management
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_workers_per_batch)
        self.process_pool = ProcessPoolExecutor(max_workers=mp.cpu_count())
        
        # Performance tracking
        self.metrics = BatchMetrics()
        self.performance_history: deque = deque(maxlen=1000)
        
        # Synchronization
        self.batch_lock = asyncio.Lock()
        self.metrics_lock = asyncio.Lock()
        
        # Background tasks
        self.processing_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        logger.info("Batch scheduler initialized successfully")
    
    async def initialize(self) -> None:
        """Initialize the batch scheduler."""
        try:
            self.is_running = True
            
            # Start background tasks
            self.processing_task = asyncio.create_task(self._processing_loop())
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.metrics_task = asyncio.create_task(self._metrics_loop())
            
            logger.info("Batch scheduler initialized and running")
            
        except Exception as e:
            logger.error(f"Batch scheduler initialization failed: {e}")
            raise
    
    async def submit_batch(self, batch_request: BatchRequest) -> str:
        """
        Submit a batch for processing.
        
        Args:
            batch_request: Batch processing request
            
        Returns:
            Batch ID for tracking
        """
        try:
            async with self.batch_lock:
                # Validate batch request
                if not await self._validate_batch_request(batch_request):
                    raise ValueError("Invalid batch request")
                
                # Initialize batch configuration if not provided
                if not batch_request.configuration:
                    batch_request.configuration = self.config
                
                # Optimize batch configuration
                await self._optimize_batch_configuration(batch_request)
                
                # Add to pending queue
                self.pending_batches[batch_request.batch_id] = batch_request
                
                # Initialize progress tracking
                self.batch_progress[batch_request.batch_id] = BatchProgress(
                    batch_id=batch_request.batch_id,
                    total_items=len(batch_request.items),
                    processed_items=0,
                    successful_items=0,
                    failed_items=0,
                    skipped_items=0,
                    current_phase="queued"
                )
                
                logger.info(f"Batch {batch_request.batch_id} submitted for processing")
                return batch_request.batch_id
                
        except Exception as e:
            logger.error(f"Failed to submit batch {batch_request.batch_id}: {e}")
            raise
    
    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a batch."""
        try:
            # Check in different states
            if batch_id in self.pending_batches:
                status = "pending"
                batch_data = self.pending_batches[batch_id]
            elif batch_id in self.active_batches:
                status = "active"
                batch_data = self.active_batches[batch_id]
            elif batch_id in self.completed_batches:
                status = "completed"
                result = self.completed_batches[batch_id]
                return {
                    'batch_id': batch_id,
                    'status': status,
                    'result': asdict(result),
                    'progress': asdict(self.batch_progress.get(batch_id, BatchProgress(batch_id, 0, 0, 0, 0, 0, "completed")))
                }
            else:
                return None
            
            progress = self.batch_progress.get(batch_id)
            
            return {
                'batch_id': batch_id,
                'status': status,
                'batch_type': batch_data.batch_type.value,
                'priority': batch_data.priority.value,
                'total_items': len(batch_data.items),
                'progress': asdict(progress) if progress else None,
                'created_at': batch_data.created_at.isoformat(),
                'estimated_completion': progress.estimated_completion.isoformat() if progress and progress.estimated_completion else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get batch status for {batch_id}: {e}")
            return None
    
    async def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a pending or active batch."""
        try:
            async with self.batch_lock:
                # Remove from pending
                if batch_id in self.pending_batches:
                    del self.pending_batches[batch_id]
                    
                    # Update progress
                    if batch_id in self.batch_progress:
                        self.batch_progress[batch_id].current_phase = "cancelled"
                    
                    logger.info(f"Cancelled pending batch {batch_id}")
                    return True
                
                # Mark active batch for cancellation
                if batch_id in self.active_batches:
                    batch_request = self.active_batches[batch_id]
                    
                    # Create cancellation result
                    result = BatchResult(
                        batch_id=batch_id,
                        status=BatchStatus.CANCELLED,
                        total_items=len(batch_request.items),
                        successful_items=0,
                        failed_items=0,
                        skipped_items=len(batch_request.items),
                        processing_time_seconds=0.0,
                        throughput=0.0,
                        success_rate=0.0
                    )
                    
                    # Move to completed
                    self.completed_batches[batch_id] = result
                    del self.active_batches[batch_id]
                    
                    # Update progress
                    if batch_id in self.batch_progress:
                        self.batch_progress[batch_id].current_phase = "cancelled"
                    
                    logger.info(f"Cancelled active batch {batch_id}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to cancel batch {batch_id}: {e}")
            return False
    
    async def get_metrics(self) -> BatchMetrics:
        """Get batch scheduler performance metrics."""
        async with self.metrics_lock:
            return self.metrics
    
    async def _processing_loop(self) -> None:
        """Main batch processing loop."""
        while self.is_running:
            try:
                # Check if we can process more batches
                if len(self.active_batches) >= self.config.max_concurrent_batches:
                    await asyncio.sleep(1)
                    continue
                
                # Get next batch to process
                batch_to_process = await self._get_next_batch()
                
                if batch_to_process:
                    # Move to active
                    async with self.batch_lock:
                        self.active_batches[batch_to_process.batch_id] = batch_to_process
                        del self.pending_batches[batch_to_process.batch_id]
                    
                    # Start processing
                    asyncio.create_task(self._process_batch(batch_to_process))
                else:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(5)
    
    async def _process_batch(self, batch_request: BatchRequest) -> None:
        """Process a single batch."""
        batch_id = batch_request.batch_id
        start_time = time.time()
        
        try:
            logger.info(f"Starting batch processing: {batch_id}")
            
            # Update progress
            progress = self.batch_progress[batch_id]
            progress.current_phase = "processing"
            progress.last_update = datetime.utcnow()
            
            # Get processor
            processor = self.processors.get(batch_request.batch_type)
            if not processor:
                raise ValueError(f"No processor found for batch type: {batch_request.batch_type.value}")
            
            # Process items based on strategy
            result = await self._execute_processing_strategy(batch_request, processor)
            
            # Calculate final metrics
            processing_time = time.time() - start_time
            result.processing_time_seconds = processing_time
            result.throughput = result.total_items / processing_time if processing_time > 0 else 0
            result.success_rate = result.successful_items / result.total_items if result.total_items > 0 else 0
            
            # Update business impact
            await self._calculate_business_impact(result, batch_request)
            
            # Move to completed
            async with self.batch_lock:
                self.completed_batches[batch_id] = result
                del self.active_batches[batch_id]
            
            # Update metrics
            await self._update_batch_metrics(result)
            
            logger.info(f"Batch processing completed: {batch_id} ({result.success_rate:.2%} success rate)")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {batch_id} - {e}")
            
            # Create failure result
            failure_result = BatchResult(
                batch_id=batch_id,
                status=BatchStatus.FAILED,
                total_items=len(batch_request.items),
                successful_items=0,
                failed_items=len(batch_request.items),
                skipped_items=0,
                processing_time_seconds=time.time() - start_time,
                throughput=0.0,
                success_rate=0.0,
                errors=[{
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'timestamp': datetime.utcnow().isoformat()
                }]
            )
            
            async with self.batch_lock:
                self.completed_batches[batch_id] = failure_result
                if batch_id in self.active_batches:
                    del self.active_batches[batch_id]
    
    async def _execute_processing_strategy(
        self,
        batch_request: BatchRequest,
        processor: BatchProcessor
    ) -> BatchResult:
        """Execute batch processing based on configured strategy."""
        config = batch_request.configuration
        strategy = config.processing_strategy
        
        if strategy == ProcessingStrategy.SEQUENTIAL:
            return await self._process_sequential(batch_request, processor)
        elif strategy == ProcessingStrategy.PARALLEL:
            return await self._process_parallel(batch_request, processor)
        elif strategy == ProcessingStrategy.PIPELINE:
            return await self._process_pipeline(batch_request, processor)
        elif strategy == ProcessingStrategy.ADAPTIVE:
            return await self._process_adaptive(batch_request, processor)
        else:
            # Default to parallel
            return await self._process_parallel(batch_request, processor)
    
    async def _process_parallel(
        self,
        batch_request: BatchRequest,
        processor: BatchProcessor
    ) -> BatchResult:
        """Process batch items in parallel."""
        batch_id = batch_request.batch_id
        items = batch_request.items
        config = batch_request.configuration
        
        # Initialize result
        result = BatchResult(
            batch_id=batch_id,
            status=BatchStatus.RUNNING,
            total_items=len(items),
            successful_items=0,
            failed_items=0,
            skipped_items=0,
            processing_time_seconds=0.0,
            throughput=0.0,
            success_rate=0.0
        )
        
        # Process in chunks
        chunk_size = config.chunk_size
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
        
        for chunk_idx, chunk in enumerate(chunks):
            try:
                # Create semaphore for concurrent control
                semaphore = asyncio.Semaphore(config.max_workers_per_batch)
                
                # Process chunk items concurrently
                tasks = []
                for item in chunk:
                    task = asyncio.create_task(
                        self._process_item_with_semaphore(
                            item, processor, semaphore, batch_request.business_context
                        )
                    )
                    tasks.append(task)
                
                # Wait for chunk completion
                chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for item, item_result in zip(chunk, chunk_results):
                    if isinstance(item_result, Exception):
                        result.failed_items += 1
                        result.errors.append({
                            'item_id': item.item_id,
                            'error': str(item_result),
                            'error_type': type(item_result).__name__,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    elif isinstance(item_result, dict) and item_result.get('status') == 'success':
                        result.successful_items += 1
                        result.item_results.append({
                            'item_id': item.item_id,
                            'result': item_result
                        })
                    else:
                        result.failed_items += 1
                        result.errors.append({
                            'item_id': item.item_id,
                            'error': item_result.get('error', 'Unknown error'),
                            'error_type': item_result.get('error_type', 'ProcessingError'),
                            'timestamp': datetime.utcnow().isoformat()
                        })
                
                # Update progress
                progress = self.batch_progress[batch_id]
                progress.processed_items = result.successful_items + result.failed_items
                progress.successful_items = result.successful_items
                progress.failed_items = result.failed_items
                progress.success_rate = progress.successful_items / progress.processed_items if progress.processed_items > 0 else 0
                progress.last_update = datetime.utcnow()
                
                # Estimate completion
                if progress.processed_items > 0:
                    processing_rate = progress.processed_items / (time.time() - batch_request.created_at.timestamp())
                    remaining_items = progress.total_items - progress.processed_items
                    estimated_remaining_time = remaining_items / processing_rate if processing_rate > 0 else 0
                    progress.estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_remaining_time)
                    progress.processing_rate = processing_rate
                
                # Checkpoint if enabled
                if config.enable_checkpointing and (chunk_idx + 1) % config.checkpoint_interval == 0:
                    checkpoint = {
                        'chunk_index': chunk_idx + 1,
                        'processed_items': progress.processed_items,
                        'successful_items': progress.successful_items,
                        'failed_items': progress.failed_items,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    result.checkpoints.append(checkpoint)
                
            except Exception as e:
                logger.error(f"Chunk processing failed for batch {batch_id}, chunk {chunk_idx}: {e}")
                result.failed_items += len(chunk)
        
        # Finalize result
        result.status = BatchStatus.COMPLETED if result.failed_items == 0 else BatchStatus.COMPLETED
        
        return result
    
    async def _process_sequential(
        self,
        batch_request: BatchRequest,
        processor: BatchProcessor
    ) -> BatchResult:
        """Process batch items sequentially."""
        # Implementation for sequential processing
        # Similar to parallel but without concurrency
        batch_id = batch_request.batch_id
        items = batch_request.items
        
        result = BatchResult(
            batch_id=batch_id,
            status=BatchStatus.RUNNING,
            total_items=len(items),
            successful_items=0,
            failed_items=0,
            skipped_items=0,
            processing_time_seconds=0.0,
            throughput=0.0,
            success_rate=0.0
        )
        
        for item in items:
            try:
                item_result = await processor.process_item(item, batch_request.business_context)
                
                if item_result.get('status') == 'success':
                    result.successful_items += 1
                    result.item_results.append({
                        'item_id': item.item_id,
                        'result': item_result
                    })
                else:
                    result.failed_items += 1
                
            except Exception as e:
                result.failed_items += 1
                result.errors.append({
                    'item_id': item.item_id,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        result.status = BatchStatus.COMPLETED
        return result
    
    async def _process_pipeline(
        self,
        batch_request: BatchRequest,
        processor: BatchProcessor
    ) -> BatchResult:
        """Process batch items using pipeline strategy."""
        # Implementation for pipeline processing
        # This would involve multiple stages of processing
        return await self._process_parallel(batch_request, processor)
    
    async def _process_adaptive(
        self,
        batch_request: BatchRequest,
        processor: BatchProcessor
    ) -> BatchResult:
        """Process batch items using adaptive strategy selection."""
        # Analyze batch characteristics and choose optimal strategy
        items = batch_request.items
        config = batch_request.configuration
        
        # Simple heuristic for strategy selection
        if len(items) < 10:
            config.processing_strategy = ProcessingStrategy.SEQUENTIAL
        elif config.resource_mode == ResourceMode.HIGH_PERFORMANCE:
            config.processing_strategy = ProcessingStrategy.PARALLEL
        else:
            config.processing_strategy = ProcessingStrategy.PARALLEL
        
        return await self._execute_processing_strategy(batch_request, processor)
    
    async def _process_item_with_semaphore(
        self,
        item: BatchItem,
        processor: BatchProcessor,
        semaphore: asyncio.Semaphore,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single item with semaphore control."""
        async with semaphore:
            try:
                # Validate item
                if not await processor.validate_item(item):
                    return {
                        'status': 'error',
                        'error': 'Item validation failed',
                        'error_type': 'ValidationError'
                    }
                
                # Process item
                result = await processor.process_item(item, context)
                return result
                
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'error_type': type(e).__name__
                }
    
    async def _get_next_batch(self) -> Optional[BatchRequest]:
        """Get the next batch to process based on priority."""
        if not self.pending_batches:
            return None
        
        # Sort by priority and creation time
        sorted_batches = sorted(
            self.pending_batches.values(),
            key=lambda b: (self._get_priority_weight(b.priority), b.created_at)
        )
        
        return sorted_batches[0] if sorted_batches else None
    
    def _get_priority_weight(self, priority: BatchPriority) -> int:
        """Get numerical weight for priority sorting."""
        weights = {
            BatchPriority.CRITICAL: 0,
            BatchPriority.HIGH: 1,
            BatchPriority.NORMAL: 2,
            BatchPriority.LOW: 3,
            BatchPriority.BACKGROUND: 4
        }
        return weights.get(priority, 2)
    
    async def _validate_batch_request(self, batch_request: BatchRequest) -> bool:
        """Validate batch request."""
        if not batch_request.batch_id:
            return False
        
        if not batch_request.items:
            return False
        
        if batch_request.batch_type not in self.processors:
            return False
        
        return True
    
    async def _optimize_batch_configuration(self, batch_request: BatchRequest) -> None:
        """Optimize batch configuration based on batch characteristics."""
        config = batch_request.configuration
        items = batch_request.items
        
        # Adjust batch size based on item count
        if len(items) > 1000:
            config.batch_size = min(config.batch_size, 50)
            config.chunk_size = min(config.chunk_size, 10)
        
        # Adjust workers based on resource mode
        if config.resource_mode == ResourceMode.HIGH_PERFORMANCE:
            config.max_workers_per_batch = min(config.max_workers_per_batch * 2, 16)
        elif config.resource_mode == ResourceMode.LOW_IMPACT:
            config.max_workers_per_batch = max(config.max_workers_per_batch // 2, 2)
    
    async def _calculate_business_impact(
        self,
        result: BatchResult,
        batch_request: BatchRequest
    ) -> None:
        """Calculate business impact of batch processing."""
        batch_type = batch_request.batch_type
        
        # Calculate different business impacts based on batch type
        if batch_type == BatchType.CONTENT_FINGERPRINTING:
            # Protection value calculation
            protection_value = result.successful_items * 1000.0  # $1000 per protected content
            result.business_impact['protection_value'] = protection_value
            result.business_impact['creator_satisfaction_score'] = result.success_rate
            
        elif batch_type == BatchType.PROTECTION_MONITORING:
            # Risk mitigation value
            risk_mitigation = result.successful_items * 500.0  # $500 per monitored content
            result.business_impact['risk_mitigation_value'] = risk_mitigation
            result.business_impact['compliance_score'] = result.success_rate
        
        # General business metrics
        result.business_impact['efficiency_score'] = result.throughput / 100.0  # Normalize to 0-1
        result.business_impact['quality_score'] = result.success_rate
        result.business_impact['cost_efficiency'] = result.throughput * result.success_rate
    
    async def _update_batch_metrics(self, result: BatchResult) -> None:
        """Update overall batch scheduler metrics."""
        async with self.metrics_lock:
            self.metrics.total_batches_processed += 1
            
            if result.status == BatchStatus.COMPLETED:
                self.metrics.successful_batches += 1
            else:
                self.metrics.failed_batches += 1
            
            self.metrics.total_items_processed += result.total_items
            
            # Update averages
            total_batches = self.metrics.total_batches_processed
            
            # Processing time average
            new_avg_time = (
                (self.metrics.average_processing_time * (total_batches - 1) + result.processing_time_seconds) /
                total_batches
            )
            self.metrics.average_processing_time = new_avg_time
            
            # Throughput average
            new_avg_throughput = (
                (self.metrics.average_throughput * (total_batches - 1) + result.throughput) /
                total_batches
            )
            self.metrics.average_throughput = new_avg_throughput
            
            # Success rate average
            new_avg_success = (
                (self.metrics.average_success_rate * (total_batches - 1) + result.success_rate) /
                total_batches
            )
            self.metrics.average_success_rate = new_avg_success
            
            # Business value
            business_value = sum(result.business_impact.values()) if result.business_impact else 0
            new_business_value = (
                (self.metrics.business_value_generated * (total_batches - 1) + business_value) /
                total_batches
            )
            self.metrics.business_value_generated = new_business_value
            
            self.metrics.last_updated = datetime.utcnow()
    
    async def _monitoring_loop(self) -> None:
        """Monitoring loop for batch processing."""
        while self.is_running:
            try:
                # Monitor resource usage
                await self._monitor_resource_usage()
                
                # Check for stuck batches
                await self._check_stuck_batches()
                
                # Auto-scale if needed
                if self.config.enable_auto_scaling:
                    await self._auto_scale_resources()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_loop(self) -> None:
        """Metrics collection loop."""
        while self.is_running:
            try:
                # Collect current state metrics
                current_metrics = {
                    'timestamp': datetime.utcnow(),
                    'pending_batches': len(self.pending_batches),
                    'active_batches': len(self.active_batches),
                    'completed_batches': len(self.completed_batches),
                    'total_metrics': asdict(self.metrics)
                }
                
                self.performance_history.append(current_metrics)
                
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                logger.error(f"Metrics loop error: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_resource_usage(self) -> None:
        """Monitor system resource usage."""
        try:
            # Monitor CPU and memory usage
            # This would integrate with system monitoring tools
            pass
        except Exception as e:
            logger.error(f"Resource monitoring error: {e}")
    
    async def _check_stuck_batches(self) -> None:
        """Check for batches that might be stuck."""
        try:
            current_time = datetime.utcnow()
            timeout_threshold = timedelta(seconds=self.config.timeout_seconds)
            
            stuck_batches = []
            for batch_id, batch_request in self.active_batches.items():
                if current_time - batch_request.created_at > timeout_threshold:
                    stuck_batches.append(batch_id)
            
            # Handle stuck batches
            for batch_id in stuck_batches:
                logger.warning(f"Detected stuck batch: {batch_id}")
                await self.cancel_batch(batch_id)
                
        except Exception as e:
            logger.error(f"Stuck batch check error: {e}")
    
    async def _auto_scale_resources(self) -> None:
        """Auto-scale resources based on load."""
        try:
            # Calculate current load
            total_pending = len(self.pending_batches)
            total_active = len(self.active_batches)
            current_load = (total_active / self.config.max_concurrent_batches) * 100
            
            # Scale up if load is high
            if current_load > self.config.scale_threshold_percent and total_pending > 0:
                # Increase concurrent batch limit temporarily
                new_limit = min(self.config.max_concurrent_batches + 2, 20)
                self.config.max_concurrent_batches = new_limit
                logger.info(f"Scaled up concurrent batch limit to {new_limit}")
            
            # Scale down if load is low
            elif current_load < 30 and self.config.max_concurrent_batches > 10:
                new_limit = max(self.config.max_concurrent_batches - 1, 10)
                self.config.max_concurrent_batches = new_limit
                logger.info(f"Scaled down concurrent batch limit to {new_limit}")
                
        except Exception as e:
            logger.error(f"Auto-scaling error: {e}")
    
    async def health_check(self) -> bool:
        """Check scheduler health."""
        try:
            return (
                self.is_running and
                self.processing_task and not self.processing_task.done() and
                self.monitoring_task and not self.monitoring_task.done()
            )
        except Exception:
            return False
    
    async def stop(self) -> None:
        """Stop the batch scheduler."""
        logger.info("Stopping batch scheduler...")
        
        self.is_running = False
        
        # Cancel background tasks
        for task in [self.processing_task, self.monitoring_task, self.metrics_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Shutdown executors
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        logger.info("Batch scheduler stopped")


# Export main classes
__all__ = [
    'BatchScheduler',
    'BatchRequest',
    'BatchItem',
    'BatchResult',
    'BatchProgress',
    'BatchConfiguration',
    'BatchMetrics',
    'BatchProcessor',
    'ContentFingerprintingProcessor',
    'ProtectionMonitoringProcessor',
    'BatchType',
    'BatchPriority',
    'BatchStatus',
    'ProcessingStrategy',
    'ResourceMode'
]
