"""AI Processing Intelligence - Advanced AI Performance Analytics Engine
========================================================================

Comprehensive AI processing analytics system providing deep insights into
ML/DL algorithm performance, resource optimization, processing efficiency,
and quality metrics for the Ainflue platform's AI infrastructure.

Monitors and optimizes AI processing pipelines, model performance, cost analysis,
scalability metrics, and processing quality across all AI operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import json
import hashlib
import time
import threading
from datetime import datetime, timedelta

# Configure logging first
logger = logging.getLogger(__name__)

# Optional dependency for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - system monitoring will use simulated data")
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import statistics
import math
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict, Counter, deque


class AIProcessingType(Enum):
    """Types of AI processing operations"""
    CONTENT_GENERATION = "content_generation"
    IMAGE_PROCESSING = "image_processing"
    AUDIO_PROCESSING = "audio_processing"
    VIDEO_PROCESSING = "video_processing"
    TEXT_ANALYSIS = "text_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_MODERATION = "content_moderation"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    VIRAL_PREDICTION = "viral_prediction"
    PERFORMANCE_PREDICTION = "performance_prediction"
    TREND_ANALYSIS = "trend_analysis"
    USER_BEHAVIOR_ANALYSIS = "user_behavior_analysis"


class ModelType(Enum):
    """AI/ML model types"""
    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    LSTM = "lstm"
    GAN = "gan"
    DIFFUSION = "diffusion"
    BERT = "bert"
    GPT = "gpt"
    RESNET = "resnet"
    YOLO = "yolo"
    WHISPER = "whisper"
    CLIP = "clip"
    CUSTOM_NEURAL = "custom_neural"
    ENSEMBLE = "ensemble"


class ProcessingStatus(Enum):
    """Processing status states"""
    QUEUED = "queued"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    OPTIMIZING = "optimizing"
    SCALING = "scaling"


class ResourceType(Enum):
    """Computing resource types"""
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    RAM = "ram"
    STORAGE = "storage"
    NETWORK = "network"
    CUSTOM_ACCELERATOR = "custom_accelerator"


class QualityMetric(Enum):
    """AI output quality metrics"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    BLEU_SCORE = "bleu_score"
    ROUGE_SCORE = "rouge_score"
    PERPLEXITY = "perplexity"
    INCEPTION_SCORE = "inception_score"
    FID_SCORE = "fid_score"
    SSIM = "ssim"
    PSNR = "psnr"
    USER_SATISFACTION = "user_satisfaction"


@dataclass
class ProcessingRequest:
    """AI processing request data structure"""
    request_id: str
    processing_type: AIProcessingType
    model_type: ModelType
    input_data_size: int  # in bytes
    priority: int = 5  # 1-10, 10 being highest
    timestamp: datetime = field(default_factory=datetime.now)
    estimated_processing_time: Optional[float] = None
    resource_requirements: Dict[ResourceType, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    content_id: Optional[str] = None


@dataclass
class ProcessingResult:
    """AI processing result data structure"""
    request_id: str
    status: ProcessingStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    processing_duration: Optional[float] = None
    output_data_size: Optional[int] = None
    resource_usage: Dict[ResourceType, float] = field(default_factory=dict)
    quality_scores: Dict[QualityMetric, float] = field(default_factory=dict)
    cost_breakdown: Dict[str, Decimal] = field(default_factory=dict)
    error_message: Optional[str] = None
    model_version: Optional[str] = None
    optimization_applied: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceMetrics:
    """System resource utilization metrics"""
    timestamp: datetime
    cpu_usage: float  # percentage
    ram_usage: float  # percentage
    storage_usage: float  # percentage
    gpu_usage: Dict[str, float] = field(default_factory=dict)  # device_id -> usage%
    network_io: Dict[str, float] = field(default_factory=dict)  # bytes/sec
    temperature: Dict[str, float] = field(default_factory=dict)  # device temps
    power_consumption: Dict[str, float] = field(default_factory=dict)  # watts


@dataclass
class ModelPerformanceMetrics:
    """Model-specific performance metrics"""
    model_type: ModelType
    model_version: str
    processing_type: AIProcessingType
    total_requests: int
    successful_requests: int
    average_processing_time: float
    average_quality_score: float
    average_cost_per_request: Decimal
    throughput_requests_per_hour: float
    resource_efficiency_score: float
    error_rate: float
    user_satisfaction_score: float
    optimization_impact: Dict[str, float] = field(default_factory=dict)


@dataclass
class ProcessingPipelineAnalysis:
    """Comprehensive processing pipeline analysis"""
    analysis_period: Tuple[datetime, datetime]
    total_requests_processed: int
    total_processing_time: float
    average_queue_time: float
    average_processing_time: float
    throughput_requests_per_hour: float
    success_rate: float
    error_rate: float
    
    # Resource utilization
    average_cpu_usage: float
    average_gpu_usage: float
    average_ram_usage: float
    peak_resource_usage: Dict[ResourceType, float]
    
    # Cost analysis
    total_processing_costs: Decimal
    cost_per_request: Decimal
    cost_breakdown_by_type: Dict[AIProcessingType, Decimal]
    
    # Quality metrics
    overall_quality_score: float
    quality_by_processing_type: Dict[AIProcessingType, float]
    quality_trends: Dict[str, List[float]]
    
    # Performance optimization
    optimization_opportunities: List[str]
    predicted_improvements: Dict[str, float]
    bottleneck_identification: List[str]
    scaling_recommendations: List[str]
    
    # Model performance comparison
    model_performance_ranking: List[Tuple[ModelType, float]]
    best_performing_models: Dict[AIProcessingType, ModelType]
    underperforming_models: List[Tuple[ModelType, str]]


class AIProcessingIntelligence:
    """
    Advanced AI Processing Intelligence Engine
    
    Provides comprehensive analytics for AI/ML processing operations,
    including performance monitoring, resource optimization, cost analysis,
    quality assessment, and predictive scaling recommendations.
    """
    
    def __init__(self, max_history_days -> None: int = 30) -> None:
        """Initialize the AI Processing Intelligence Engine"""
        self.max_history_days = max_history_days
        self.processing_requests: Dict[str, ProcessingRequest] = {}
        self.processing_results: Dict[str, ProcessingResult] = {}
        self.resource_metrics_history: deque = deque(maxlen=10000)  # Last 10k measurements
        self.model_performance_cache: Dict[str, ModelPerformanceMetrics] = {}
        
        # Real-time monitoring
        self.current_queue: Dict[str, ProcessingRequest] = {}
        self.active_processing: Dict[str, ProcessingRequest] = {}
        self.resource_monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Performance thresholds
        self.performance_thresholds = self._initialize_performance_thresholds()
        
        # Cost models
        self.cost_models = self._initialize_cost_models()
        
        # Quality benchmarks
        self.quality_benchmarks = self._initialize_quality_benchmarks()
        
        # Optimization strategies
        self.optimization_strategies = self._initialize_optimization_strategies()
        
        logger.info("🤖 AI Processing Intelligence Engine initialized")
    
    def _initialize_performance_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize performance thresholds for different metrics"""
        return {
            "response_time": {
                "excellent": 50.0,  # < 50ms
                "good": 200.0,      # < 200ms
                "acceptable": 1000.0,  # < 1s
                "poor": 5000.0      # < 5s
            },
            "throughput": {
                "excellent": 1000.0,  # > 1000 req/hour
                "good": 500.0,        # > 500 req/hour
                "acceptable": 100.0,  # > 100 req/hour
                "poor": 50.0          # > 50 req/hour
            },
            "resource_usage": {
                "efficient": 70.0,   # < 70% usage
                "normal": 85.0,       # < 85% usage
                "high": 95.0,         # < 95% usage
                "critical": 100.0     # < 100% usage
            },
            "quality_score": {
                "excellent": 0.95,   # > 95%
                "good": 0.85,         # > 85%
                "acceptable": 0.75,  # > 75%
                "poor": 0.60          # > 60%
            }
        }
    
    def _initialize_cost_models(self) -> Dict[ResourceType, Dict[str, Decimal]]:
        """Initialize cost models for different resource types"""
        return {
            ResourceType.CPU: {
                "cost_per_hour": Decimal("0.05"),
                "cost_per_gb_hour": Decimal("0.02")
            },
            ResourceType.GPU: {
                "cost_per_hour": Decimal("0.50"),
                "cost_per_gb_hour": Decimal("0.10")
            },
            ResourceType.TPU: {
                "cost_per_hour": Decimal("1.00"),
                "cost_per_gb_hour": Decimal("0.20")
            },
            ResourceType.RAM: {
                "cost_per_gb_hour": Decimal("0.01")
            },
            ResourceType.STORAGE: {
                "cost_per_gb_hour": Decimal("0.001")
            },
            ResourceType.NETWORK: {
                "cost_per_gb": Decimal("0.05")
            }
        }
    
    def _initialize_quality_benchmarks(self) -> Dict[AIProcessingType, Dict[QualityMetric, float]]:
        """Initialize quality benchmarks for different processing types"""
        return {
            AIProcessingType.CONTENT_GENERATION: {
                QualityMetric.BLEU_SCORE: 0.85,
                QualityMetric.USER_SATISFACTION: 0.80,
                QualityMetric.PERPLEXITY: 20.0
            },
            AIProcessingType.IMAGE_PROCESSING: {
                QualityMetric.SSIM: 0.90,
                QualityMetric.PSNR: 30.0,
                QualityMetric.USER_SATISFACTION: 0.85
            },
            AIProcessingType.SENTIMENT_ANALYSIS: {
                QualityMetric.ACCURACY: 0.92,
                QualityMetric.F1_SCORE: 0.90,
                QualityMetric.PRECISION: 0.88
            },
            AIProcessingType.VIRAL_PREDICTION: {
                QualityMetric.ACCURACY: 0.85,
                QualityMetric.PRECISION: 0.80,
                QualityMetric.RECALL: 0.85
            }
        }
    
    def _initialize_optimization_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize optimization strategies and their configurations"""
        return {
            "model_quantization": {
                "description": "Reduce model precision to improve speed",
                "impact_latency": -0.30,  # 30% faster
                "impact_quality": -0.05,  # 5% quality loss
                "impact_resource": -0.40  # 40% less resource usage
            },
            "batch_processing": {
                "description": "Group requests for better throughput",
                "impact_latency": 0.20,   # 20% slower individual requests
                "impact_throughput": 2.0, # 2x throughput
                "impact_resource": -0.20  # 20% better resource utilization
            },
            "model_caching": {
                "description": "Cache model outputs for repeated requests",
                "impact_latency": -0.80,  # 80% faster for cached
                "impact_resource": -0.50, # 50% less resource usage
                "cache_hit_rate": 0.30    # 30% cache hit rate expected
            },
            "load_balancing": {
                "description": "Distribute load across multiple instances",
                "impact_latency": -0.15,  # 15% faster
                "impact_throughput": 1.5, # 1.5x throughput
                "impact_reliability": 0.25 # 25% better reliability
            },
            "auto_scaling": {
                "description": "Automatically scale resources based on demand",
                "impact_resource_efficiency": 0.30, # 30% better efficiency
                "impact_cost": -0.25,     # 25% cost reduction
                "impact_availability": 0.20 # 20% better availability
            }
        }
    
    async def submit_processing_request(self, request: ProcessingRequest) -> bool:
        """Submit a new AI processing request"""
        try:
            # Store request
            self.processing_requests[request.request_id] = request
            
            # Add to queue
            self.current_queue[request.request_id] = request
            
            # Estimate processing time if not provided
            if not request.estimated_processing_time:
                request.estimated_processing_time = await self._estimate_processing_time(request)
            
            logger.info(f"✅ Processing request {request.request_id} submitted to queue")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to submit processing request: {e}")
            return False
    
    async def start_processing(self, request_id: str) -> bool:
        """Start processing a queued request"""
        try:
            if request_id not in self.current_queue:
                logger.error(f"Request {request_id} not found in queue")
                return False
            
            request = self.current_queue.pop(request_id)
            self.active_processing[request_id] = request
            
            # Create initial result
            result = ProcessingResult(
                request_id=request_id,
                status=ProcessingStatus.PROCESSING,
                start_time=datetime.now()
            )
            
            self.processing_results[request_id] = result
            
            logger.info(f"🚀 Started processing request {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start processing request {request_id}: {e}")
            return False
    
    async def complete_processing(
        self, 
        request_id: str, 
        result_data: Dict[str, Any]
    ) -> bool:
        """Complete processing and record results"""
        try:
            if request_id not in self.processing_results:
                logger.error(f"Processing result for {request_id} not found")
                return False
            
            result = self.processing_results[request_id]
            
            # Update result with completion data
            result.status = ProcessingStatus.COMPLETED
            result.end_time = datetime.now()
            result.processing_duration = (result.end_time - result.start_time).total_seconds()
            
            # Update with provided result data
            if "output_data_size" in result_data:
                result.output_data_size = result_data["output_data_size"]
            
            if "resource_usage" in result_data:
                result.resource_usage.update(result_data["resource_usage"])
            
            if "quality_scores" in result_data:
                result.quality_scores.update(result_data["quality_scores"])
            
            if "cost_breakdown" in result_data:
                result.cost_breakdown.update(result_data["cost_breakdown"])
            
            # Remove from active processing
            if request_id in self.active_processing:
                del self.active_processing[request_id]
            
            # Update model performance cache
            await self._update_model_performance_cache(request_id)
            
            logger.info(f"✅ Completed processing request {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to complete processing request {request_id}: {e}")
            return False
    
    async def fail_processing(self, request_id: str, error_message: str) -> bool:
        """Mark processing as failed"""
        try:
            if request_id not in self.processing_results:
                logger.error(f"Processing result for {request_id} not found")
                return False
            
            result = self.processing_results[request_id]
            result.status = ProcessingStatus.FAILED
            result.end_time = datetime.now()
            result.error_message = error_message
            
            if result.start_time:
                result.processing_duration = (result.end_time - result.start_time).total_seconds()
            
            # Remove from active processing
            if request_id in self.active_processing:
                del self.active_processing[request_id]
            
            logger.warning(f"❌ Processing request {request_id} failed: {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to mark processing as failed for {request_id}: {e}")
            return False
    
    def start_resource_monitoring(self, interval_seconds -> None: int = 10) -> None:
        """Start real-time resource monitoring"""
        if self.resource_monitoring_active:
            logger.warning("Resource monitoring already active")
            return
        
        self.resource_monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._resource_monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info(f"🔍 Started resource monitoring (interval: {interval_seconds}s)")
    
    def stop_resource_monitoring(self) -> None:
        """Stop resource monitoring"""
        self.resource_monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("🛑 Stopped resource monitoring")
    
    def _resource_monitoring_loop(self, interval_seconds -> None: int) -> None:
        """Resource monitoring loop (runs in separate thread)"""
        while self.resource_monitoring_active:
            try:
                metrics = self._collect_resource_metrics()
                self.resource_metrics_history.append(metrics)
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(interval_seconds)
    
    def _collect_resource_metrics(self) -> ResourceMetrics:
        """Collect current system resource metrics"""
        try:
            if PSUTIL_AVAILABLE:
                # CPU metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                ram_usage = memory.percent
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                storage_usage = disk.percent
                
                # Network metrics
                network = psutil.net_io_counters()
                network_io = {
                    "bytes_sent_per_sec": network.bytes_sent,
                    "bytes_recv_per_sec": network.bytes_recv
                }
            else:
                # Simulated metrics when psutil is not available
                import random
                cpu_usage = random.uniform(20, 80)
                ram_usage = random.uniform(30, 70)
                storage_usage = random.uniform(10, 90)
                network_io = {
                    "bytes_sent_per_sec": random.uniform(1000, 10000),
                    "bytes_recv_per_sec": random.uniform(1000, 10000)
                }
            
            # GPU metrics (simulated - in production would use nvidia-ml-py)
            gpu_usage = {
                "gpu_0": min(100.0, cpu_usage * 1.2 + (hash(str(time.time())) % 20)),
                "gpu_1": min(100.0, cpu_usage * 0.8 + (hash(str(time.time() + 1)) % 15))
            }
            
            # Temperature metrics (simulated)
            temperature = {
                "cpu": 45 + (cpu_usage * 0.3),
                "gpu_0": 55 + (gpu_usage["gpu_0"] * 0.25),
                "gpu_1": 52 + (gpu_usage["gpu_1"] * 0.28)
            }
            
            # Power consumption (simulated)
            power_consumption = {
                "cpu": 65 + (cpu_usage * 0.5),
                "gpu_0": 150 + (gpu_usage["gpu_0"] * 2.0),
                "gpu_1": 140 + (gpu_usage["gpu_1"] * 1.8)
            }
            
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                gpu_usage=gpu_usage,
                ram_usage=ram_usage,
                storage_usage=storage_usage,
                network_io=network_io,
                temperature=temperature,
                power_consumption=power_consumption
            )
            
        except Exception as e:
            logger.error(f"Failed to collect resource metrics: {e}")
            return ResourceMetrics(timestamp=datetime.now(), cpu_usage=0.0, ram_usage=0.0, storage_usage=0.0)
    
    async def _estimate_processing_time(self, request: ProcessingRequest) -> float:
        """Estimate processing time for a request"""
        try:
            # Base processing time estimates by type and model
            base_times = {
                AIProcessingType.CONTENT_GENERATION: {
                    ModelType.GPT: 2.0,
                    ModelType.BERT: 1.5,
                    ModelType.TRANSFORMER: 2.5
                },
                AIProcessingType.IMAGE_PROCESSING: {
                    ModelType.CNN: 1.0,
                    ModelType.RESNET: 1.2,
                    ModelType.GAN: 3.0,
                    ModelType.DIFFUSION: 5.0
                },
                AIProcessingType.AUDIO_PROCESSING: {
                    ModelType.WHISPER: 2.0,
                    ModelType.RNN: 1.8,
                    ModelType.LSTM: 2.2
                },
                AIProcessingType.VIDEO_PROCESSING: {
                    ModelType.CNN: 5.0,
                    ModelType.YOLO: 3.0,
                    ModelType.CUSTOM_NEURAL: 4.0
                }
            }
            
            # Get base time
            base_time = base_times.get(request.processing_type, {}).get(
                request.model_type, 2.0
            )
            
            # Adjust for data size
            size_factor = math.log10(max(1, request.input_data_size / 1024))  # KB scaling
            
            # Adjust for current system load
            current_load = len(self.active_processing)
            load_factor = 1.0 + (current_load * 0.1)  # 10% increase per active job
            
            estimated_time = base_time * size_factor * load_factor
            
            return max(0.1, estimated_time)  # Minimum 0.1 seconds
            
        except Exception as e:
            logger.error(f"Failed to estimate processing time: {e}")
            return 2.0  # Default estimate
    
    async def _update_model_performance_cache(self, request_id -> None: str) -> None:
        """Update model performance metrics cache"""
        try:
            if request_id not in self.processing_requests or request_id not in self.processing_results:
                return
            
            request = self.processing_requests[request_id]
            result = self.processing_results[request_id]
            
            cache_key = f"{request.model_type.value}_{request.processing_type.value}"
            
            if cache_key not in self.model_performance_cache:
                self.model_performance_cache[cache_key] = ModelPerformanceMetrics(
                    model_type=request.model_type,
                    model_version="1.0",
                    processing_type=request.processing_type,
                    total_requests=0,
                    successful_requests=0,
                    average_processing_time=0.0,
                    average_quality_score=0.0,
                    average_cost_per_request=Decimal('0'),
                    throughput_requests_per_hour=0.0,
                    resource_efficiency_score=0.0,
                    error_rate=0.0,
                    user_satisfaction_score=0.0
                )
            
            metrics = self.model_performance_cache[cache_key]
            
            # Update metrics
            metrics.total_requests += 1
            
            if result.status == ProcessingStatus.COMPLETED:
                metrics.successful_requests += 1
                
                if result.processing_duration:
                    # Update average processing time
                    total_time = metrics.average_processing_time * (metrics.successful_requests - 1)
                    metrics.average_processing_time = (total_time + result.processing_duration) / metrics.successful_requests
                
                # Update quality score
                if result.quality_scores:
                    avg_quality = statistics.mean(result.quality_scores.values())
                    total_quality = metrics.average_quality_score * (metrics.successful_requests - 1)
                    metrics.average_quality_score = (total_quality + avg_quality) / metrics.successful_requests
                
                # Update cost
                if result.cost_breakdown:
                    total_cost = sum(result.cost_breakdown.values())
                    total_accumulated_cost = metrics.average_cost_per_request * (metrics.successful_requests - 1)
                    metrics.average_cost_per_request = (total_accumulated_cost + total_cost) / metrics.successful_requests
            
            # Update error rate
            metrics.error_rate = 1.0 - (metrics.successful_requests / metrics.total_requests)
            
            # Update throughput (requests per hour)
            if metrics.average_processing_time > 0:
                metrics.throughput_requests_per_hour = 3600.0 / metrics.average_processing_time
            
        except Exception as e:
            logger.error(f"Failed to update model performance cache: {e}")
    
    async def analyze_processing_pipeline(
        self, 
        analysis_period_hours: int = 24
    ) -> Optional[ProcessingPipelineAnalysis]:
        """
        Analyze processing pipeline performance over specified period
        
        Args:
            analysis_period_hours: Analysis period in hours (default: 24)
            
        Returns:
            ProcessingPipelineAnalysis with comprehensive insights
        """
        try:
            # Define analysis period
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=analysis_period_hours)
            
            # Filter data for analysis period
            period_requests = {
                req_id: req for req_id, req in self.processing_requests.items()
                if start_time <= req.timestamp <= end_time
            }
            
            period_results = {
                req_id: result for req_id, result in self.processing_results.items()
                if req_id in period_requests and result.start_time and start_time <= result.start_time <= end_time
            }
            
            if not period_requests:
                logger.warning("No processing requests found in specified period")
                return None
            
            # Calculate basic metrics
            total_requests = len(period_requests)
            completed_requests = sum(1 for result in period_results.values() 
                                   if result.status == ProcessingStatus.COMPLETED)
            failed_requests = sum(1 for result in period_results.values() 
                                if result.status == ProcessingStatus.FAILED)
            
            success_rate = completed_requests / total_requests if total_requests > 0 else 0.0
            error_rate = failed_requests / total_requests if total_requests > 0 else 0.0
            
            # Calculate timing metrics
            processing_times = [
                result.processing_duration for result in period_results.values()
                if result.processing_duration is not None
            ]
            
            total_processing_time = sum(processing_times) if processing_times else 0.0
            average_processing_time = statistics.mean(processing_times) if processing_times else 0.0
            
            # Calculate queue times (simulated - in production would track actual queue times)
            average_queue_time = average_processing_time * 0.2  # Estimate 20% of processing time
            
            # Calculate throughput
            period_duration_hours = analysis_period_hours
            throughput_requests_per_hour = total_requests / period_duration_hours if period_duration_hours > 0 else 0.0
            
            # Analyze resource utilization
            period_resource_metrics = [
                metrics for metrics in self.resource_metrics_history
                if start_time <= metrics.timestamp <= end_time
            ]
            
            if period_resource_metrics:
                average_cpu_usage = statistics.mean([m.cpu_usage for m in period_resource_metrics])
                average_gpu_usage = statistics.mean([
                    statistics.mean(m.gpu_usage.values()) for m in period_resource_metrics
                    if m.gpu_usage
                ])
                average_ram_usage = statistics.mean([m.ram_usage for m in period_resource_metrics])
                
                # Calculate peak usage
                peak_cpu = max([m.cpu_usage for m in period_resource_metrics])
                peak_gpu = max([
                    max(m.gpu_usage.values()) for m in period_resource_metrics
                    if m.gpu_usage
                ]) if period_resource_metrics else 0.0
                peak_ram = max([m.ram_usage for m in period_resource_metrics])
                
                peak_resource_usage = {
                    ResourceType.CPU: peak_cpu,
                    ResourceType.GPU: peak_gpu,
                    ResourceType.RAM: peak_ram
                }
            else:
                average_cpu_usage = 0.0
                average_gpu_usage = 0.0
                average_ram_usage = 0.0
                peak_resource_usage = {}
            
            # Calculate cost analysis
            total_costs = Decimal('0')
            cost_by_type = defaultdict(lambda: Decimal('0'))
            
            for result in period_results.values():
                if result.cost_breakdown:
                    request = period_requests.get(result.request_id)
                    if request:
                        result_cost = sum(result.cost_breakdown.values())
                        total_costs += result_cost
                        cost_by_type[request.processing_type] += result_cost
            
            cost_per_request = total_costs / total_requests if total_requests > 0 else Decimal('0')
            
            # Calculate quality metrics
            quality_scores = []
            quality_by_type = defaultdict(list)
            
            for req_id, result in period_results.items():
                if result.quality_scores:
                    avg_quality = statistics.mean(result.quality_scores.values())
                    quality_scores.append(avg_quality)
                    
                    request = period_requests.get(req_id)
                    if request:
                        quality_by_type[request.processing_type].append(avg_quality)
            
            overall_quality_score = statistics.mean(quality_scores) if quality_scores else 0.0
            
            quality_by_processing_type = {
                proc_type: statistics.mean(scores) if scores else 0.0
                for proc_type, scores in quality_by_type.items()
            }
            
            # Generate optimization recommendations
            optimization_opportunities = await self._identify_optimization_opportunities(
                period_requests, period_results, period_resource_metrics
            )
            
            predicted_improvements = await self._predict_optimization_improvements(
                optimization_opportunities
            )
            
            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks(
                period_requests, period_results, period_resource_metrics
            )
            
            # Generate scaling recommendations
            scaling_recommendations = await self._generate_scaling_recommendations(
                throughput_requests_per_hour, average_cpu_usage, average_gpu_usage, average_ram_usage
            )
            
            # Model performance ranking
            model_performance_ranking = await self._rank_model_performance(period_requests, period_results)
            
            best_performing_models = await self._identify_best_models_by_type(period_requests, period_results)
            
            underperforming_models = await self._identify_underperforming_models(period_requests, period_results)
            
            # Quality trends (simulated)
            quality_trends = {
                "accuracy": [0.85, 0.87, 0.86, 0.88, 0.89],
                "latency": [120.0, 115.0, 110.0, 105.0, 100.0],
                "cost_efficiency": [0.75, 0.77, 0.78, 0.80, 0.82]
            }
            
            return ProcessingPipelineAnalysis(
                analysis_period=(start_time, end_time),
                total_requests_processed=total_requests,
                total_processing_time=total_processing_time,
                average_queue_time=average_queue_time,
                average_processing_time=average_processing_time,
                throughput_requests_per_hour=throughput_requests_per_hour,
                success_rate=success_rate,
                error_rate=error_rate,
                average_cpu_usage=average_cpu_usage,
                average_gpu_usage=average_gpu_usage,
                average_ram_usage=average_ram_usage,
                peak_resource_usage=peak_resource_usage,
                total_processing_costs=total_costs,
                cost_per_request=cost_per_request,
                cost_breakdown_by_type=dict(cost_by_type),
                overall_quality_score=overall_quality_score,
                quality_by_processing_type=quality_by_processing_type,
                quality_trends=quality_trends,
                optimization_opportunities=optimization_opportunities,
                predicted_improvements=predicted_improvements,
                bottleneck_identification=bottlenecks,
                scaling_recommendations=scaling_recommendations,
                model_performance_ranking=model_performance_ranking,
                best_performing_models=best_performing_models,
                underperforming_models=underperforming_models
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze processing pipeline: {e}")
            return None
    
    async def _identify_optimization_opportunities(
        self,
        requests: Dict[str, ProcessingRequest],
        results: Dict[str, ProcessingResult],
        resource_metrics: List[ResourceMetrics]
    ) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []
        
        # Analyze processing times
        processing_times = [
            result.processing_duration for result in results.values()
            if result.processing_duration is not None
        ]
        
        if processing_times:
            avg_time = statistics.mean(processing_times)
            if avg_time > 5.0:  # More than 5 seconds average
                opportunities.append("High average processing time - consider model optimization")
            
            if max(processing_times) > 30.0:  # Some requests take more than 30 seconds
                opportunities.append("Long tail processing times - implement timeout mechanisms")
        
        # Analyze resource utilization
        if resource_metrics:
            avg_cpu = statistics.mean([m.cpu_usage for m in resource_metrics])
            avg_gpu = statistics.mean([
                statistics.mean(m.gpu_usage.values()) for m in resource_metrics
                if m.gpu_usage
            ])
            
            if avg_cpu < 50.0:
                opportunities.append("Low CPU utilization - consider increasing batch sizes")
            
            if avg_gpu < 60.0:
                opportunities.append("Low GPU utilization - optimize GPU memory usage")
            
            if avg_cpu > 90.0:
                opportunities.append("High CPU utilization - scale CPU resources")
            
            if avg_gpu > 90.0:
                opportunities.append("High GPU utilization - scale GPU resources")
        
        # Analyze error rates by processing type
        error_by_type = defaultdict(int)
        total_by_type = defaultdict(int)
        
        for req_id, result in results.items():
            request = requests.get(req_id)
            if request:
                total_by_type[request.processing_type] += 1
                if result.status == ProcessingStatus.FAILED:
                    error_by_type[request.processing_type] += 1
        
        for proc_type, error_count in error_by_type.items():
            total_count = total_by_type[proc_type]
            error_rate = error_count / total_count if total_count > 0 else 0.0
            
            if error_rate > 0.05:  # More than 5% error rate
                opportunities.append(f"High error rate for {proc_type.value} - investigate and fix")
        
        # Analyze cost efficiency
        costs = [
            sum(result.cost_breakdown.values()) for result in results.values()
            if result.cost_breakdown
        ]
        
        if costs and statistics.mean(costs) > 1.0:  # More than $1 per request on average
            opportunities.append("High processing costs - optimize resource allocation")
        
        return opportunities
    
    async def _predict_optimization_improvements(
        self, 
        opportunities: List[str]
    ) -> Dict[str, float]:
        """Predict improvements from implementing optimization opportunities"""
        improvements = {}
        
        for opportunity in opportunities:
            if "processing time" in opportunity.lower():
                improvements["latency_reduction"] = 0.25  # 25% improvement
            
            if "utilization" in opportunity.lower():
                improvements["resource_efficiency"] = 0.20  # 20% improvement
            
            if "error rate" in opportunity.lower():
                improvements["reliability"] = 0.30  # 30% improvement
            
            if "cost" in opportunity.lower():
                improvements["cost_reduction"] = 0.15  # 15% cost reduction
        
        return improvements
    
    async def _identify_bottlenecks(
        self,
        requests: Dict[str, ProcessingRequest],
        results: Dict[str, ProcessingResult],
        resource_metrics: List[ResourceMetrics]
    ) -> List[str]:
        """Identify system bottlenecks"""
        bottlenecks = []
        
        # Analyze queue buildup patterns
        if len(self.current_queue) > 10:
            bottlenecks.append("Request queue buildup - insufficient processing capacity")
        
        # Analyze resource constraints
        if resource_metrics:
            cpu_usage = [m.cpu_usage for m in resource_metrics]
            gpu_usage = [
                max(m.gpu_usage.values()) for m in resource_metrics
                if m.gpu_usage
            ]
            ram_usage = [m.ram_usage for m in resource_metrics]
            
            if statistics.mean(cpu_usage) > 85.0:
                bottlenecks.append("CPU bottleneck - high sustained CPU usage")
            
            if gpu_usage and statistics.mean(gpu_usage) > 85.0:
                bottlenecks.append("GPU bottleneck - high sustained GPU usage")
            
            if statistics.mean(ram_usage) > 85.0:
                bottlenecks.append("Memory bottleneck - high RAM usage")
        
        # Analyze processing time variance
        processing_times = [
            result.processing_duration for result in results.values()
            if result.processing_duration is not None
        ]
        
        if processing_times and len(processing_times) > 1:
            std_dev = statistics.stdev(processing_times)
            mean_time = statistics.mean(processing_times)
            
            if std_dev > mean_time * 0.5:  # High variance
                bottlenecks.append("High processing time variance - inconsistent performance")
        
        return bottlenecks
    
    async def _generate_scaling_recommendations(
        self,
        throughput: float,
        cpu_usage: float,
        gpu_usage: float,
        ram_usage: float
    ) -> List[str]:
        """Generate scaling recommendations based on metrics"""
        recommendations = []
        
        # Throughput-based recommendations
        if throughput < 100:  # Less than 100 requests per hour
            recommendations.append("Low throughput - consider horizontal scaling")
        elif throughput > 1000:  # More than 1000 requests per hour
            recommendations.append("High throughput - monitor for capacity limits")
        
        # Resource-based recommendations
        if cpu_usage > 80:
            recommendations.append("Scale CPU resources - add more CPU cores or instances")
        
        if gpu_usage > 80:
            recommendations.append("Scale GPU resources - add more GPU instances")
        
        if ram_usage > 80:
            recommendations.append("Scale memory resources - increase RAM allocation")
        
        # Efficiency recommendations
        if cpu_usage < 30 and gpu_usage < 30:
            recommendations.append("Over-provisioned resources - consider downsizing")
        
        # Load balancing recommendations
        if throughput > 500 and (cpu_usage > 70 or gpu_usage > 70):
            recommendations.append("Implement load balancing across multiple instances")
        
        return recommendations
    
    async def _rank_model_performance(
        self,
        requests: Dict[str, ProcessingRequest],
        results: Dict[str, ProcessingResult]
    ) -> List[Tuple[ModelType, float]]:
        """Rank models by performance score"""
        model_scores = defaultdict(list)
        
        for req_id, result in results.items():
            request = requests.get(req_id)
            if request and result.status == ProcessingStatus.COMPLETED:
                # Calculate performance score
                score = 0.0
                
                # Speed component (lower time = higher score)
                if result.processing_duration:
                    speed_score = max(0, 1.0 - (result.processing_duration / 10.0))  # Normalize to 10s max
                    score += speed_score * 0.3
                
                # Quality component
                if result.quality_scores:
                    quality_score = statistics.mean(result.quality_scores.values())
                    score += quality_score * 0.4
                
                # Cost efficiency component (lower cost = higher score)
                if result.cost_breakdown:
                    total_cost = sum(result.cost_breakdown.values())
                    cost_score = max(0, 1.0 - (float(total_cost) / 5.0))  # Normalize to $5 max
                    score += cost_score * 0.3
                
                model_scores[request.model_type].append(score)
        
        # Calculate average scores and rank
        model_averages = {
            model_type: statistics.mean(scores)
            for model_type, scores in model_scores.items()
            if scores
        }
        
        return sorted(model_averages.items(), key=lambda x: x[1], reverse=True)
    
    async def _identify_best_models_by_type(
        self,
        requests: Dict[str, ProcessingRequest],
        results: Dict[str, ProcessingResult]
    ) -> Dict[AIProcessingType, ModelType]:
        """Identify best performing model for each processing type"""
        type_model_performance = defaultdict(lambda: defaultdict(list))
        
        for req_id, result in results.items():
            request = requests.get(req_id)
            if request and result.status == ProcessingStatus.COMPLETED:
                # Calculate performance score (same as above)
                score = 0.0
                
                if result.processing_duration:
                    speed_score = max(0, 1.0 - (result.processing_duration / 10.0))
                    score += speed_score * 0.3
                
                if result.quality_scores:
                    quality_score = statistics.mean(result.quality_scores.values())
                    score += quality_score * 0.4
                
                if result.cost_breakdown:
                    total_cost = sum(result.cost_breakdown.values())
                    cost_score = max(0, 1.0 - (float(total_cost) / 5.0))
                    score += cost_score * 0.3
                
                type_model_performance[request.processing_type][request.model_type].append(score)
        
        best_models = {}
        for proc_type, model_scores in type_model_performance.items():
            if model_scores:
                # Calculate average scores for each model
                avg_scores = {
                    model: statistics.mean(scores)
                    for model, scores in model_scores.items()
                    if scores
                }
                
                if avg_scores:
                    best_model = max(avg_scores.items(), key=lambda x: x[1])[0]
                    best_models[proc_type] = best_model
        
        return best_models
    
    async def _identify_underperforming_models(
        self,
        requests: Dict[str, ProcessingRequest],
        results: Dict[str, ProcessingResult]
    ) -> List[Tuple[ModelType, str]]:
        """Identify underperforming models with reasons"""
        model_performance = defaultdict(lambda: {
            'total_requests': 0,
            'failed_requests': 0,
            'processing_times': [],
            'quality_scores': [],
            'costs': []
        })
        
        # Collect performance data
        for req_id, result in results.items():
            request = requests.get(req_id)
            if request:
                model_data = model_performance[request.model_type]
                model_data['total_requests'] += 1
                
                if result.status == ProcessingStatus.FAILED:
                    model_data['failed_requests'] += 1
                elif result.status == ProcessingStatus.COMPLETED:
                    if result.processing_duration:
                        model_data['processing_times'].append(result.processing_duration)
                    
                    if result.quality_scores:
                        model_data['quality_scores'].extend(result.quality_scores.values())
                    
                    if result.cost_breakdown:
                        model_data['costs'].append(sum(result.cost_breakdown.values()))
        
        underperforming = []
        
        for model_type, data in model_performance.items():
            reasons = []
            
            # Check error rate
            if data['total_requests'] > 0:
                error_rate = data['failed_requests'] / data['total_requests']
                if error_rate > 0.1:  # More than 10% error rate
                    reasons.append(f"High error rate: {error_rate:.1%}")
            
            # Check processing time
            if data['processing_times']:
                avg_time = statistics.mean(data['processing_times'])
                if avg_time > 10.0:  # More than 10 seconds average
                    reasons.append(f"Slow processing: {avg_time:.1f}s average")
            
            # Check quality
            if data['quality_scores']:
                avg_quality = statistics.mean(data['quality_scores'])
                if avg_quality < 0.7:  # Less than 70% quality
                    reasons.append(f"Low quality: {avg_quality:.1%}")
            
            # Check cost
            if data['costs']:
                avg_cost = statistics.mean(data['costs'])
                if avg_cost > 2.0:  # More than $2 per request
                    reasons.append(f"High cost: ${avg_cost:.2f}/request")
            
            if reasons:
                underperforming.append((model_type, "; ".join(reasons)))
        
        return underperforming
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time processing metrics"""
        try:
            current_time = datetime.now()
            
            # Queue metrics
            queue_size = len(self.current_queue)
            active_processing_count = len(self.active_processing)
            
            # Recent performance (last hour)
            recent_results = [
                result for result in self.processing_results.values()
                if result.start_time and (current_time - result.start_time).total_seconds() < 3600
            ]
            
            recent_success_rate = 0.0
            recent_avg_time = 0.0
            
            if recent_results:
                successful = sum(1 for r in recent_results if r.status == ProcessingStatus.COMPLETED)
                recent_success_rate = successful / len(recent_results)
                
                processing_times = [
                    r.processing_duration for r in recent_results
                    if r.processing_duration is not None
                ]
                
                if processing_times:
                    recent_avg_time = statistics.mean(processing_times)
            
            # Current resource metrics
            current_resources = {}
            if self.resource_metrics_history:
                latest_metrics = self.resource_metrics_history[-1]
                current_resources = {
                    "cpu_usage": latest_metrics.cpu_usage,
                    "gpu_usage": latest_metrics.gpu_usage,
                    "ram_usage": latest_metrics.ram_usage,
                    "timestamp": latest_metrics.timestamp.isoformat()
                }
            
            # Throughput estimate
            hourly_throughput = len(recent_results) if recent_results else 0
            
            return {
                "timestamp": current_time.isoformat(),
                "queue_metrics": {
                    "queued_requests": queue_size,
                    "active_processing": active_processing_count,
                    "estimated_queue_time": queue_size * recent_avg_time if recent_avg_time > 0 else 0
                },
                "performance_metrics": {
                    "success_rate": recent_success_rate,
                    "average_processing_time": recent_avg_time,
                    "hourly_throughput": hourly_throughput
                },
                "resource_metrics": current_resources,
                "system_health": {
                    "status": "healthy" if recent_success_rate > 0.95 else "degraded" if recent_success_rate > 0.8 else "critical",
                    "monitoring_active": self.resource_monitoring_active
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get real-time metrics: {e}")
            return {"error": str(e)}
    
    async def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get current optimization recommendations"""
        try:
            # Analyze recent performance
            analysis = await self.analyze_processing_pipeline(analysis_period_hours=24)
            
            if not analysis:
                return {"error": "Unable to generate recommendations - insufficient data"}
            
            recommendations = {
                "immediate_actions": [],
                "short_term_optimizations": [],
                "long_term_improvements": [],
                "cost_optimizations": [],
                "performance_improvements": []
            }
            
            # Immediate actions based on current state
            if analysis.error_rate > 0.05:
                recommendations["immediate_actions"].append(
                    f"Investigate high error rate: {analysis.error_rate:.1%}"
                )
            
            if analysis.average_cpu_usage > 90:
                recommendations["immediate_actions"].append(
                    "Critical: CPU usage is very high - scale immediately"
                )
            
            if analysis.average_gpu_usage > 90:
                recommendations["immediate_actions"].append(
                    "Critical: GPU usage is very high - add GPU capacity"
                )
            
            # Short-term optimizations
            if analysis.average_processing_time > 5.0:
                recommendations["short_term_optimizations"].append(
                    "Optimize processing pipeline - average time is high"
                )
            
            if analysis.throughput_requests_per_hour < 100:
                recommendations["short_term_optimizations"].append(
                    "Implement batch processing to improve throughput"
                )
            
            # Long-term improvements
            if analysis.overall_quality_score < 0.8:
                recommendations["long_term_improvements"].append(
                    "Invest in model quality improvements"
                )
            
            recommendations["long_term_improvements"].extend([
                "Implement advanced caching strategies",
                "Develop predictive scaling algorithms",
                "Integrate real-time optimization feedback loops"
            ])
            
            # Cost optimizations
            if analysis.cost_per_request > Decimal('1.0'):
                recommendations["cost_optimizations"].append(
                    "High cost per request - optimize resource allocation"
                )
            
            recommendations["cost_optimizations"].extend([
                "Implement spot instance usage for non-critical processing",
                "Optimize model quantization to reduce resource costs",
                "Implement intelligent request routing for cost efficiency"
            ])
            
            # Performance improvements
            recommendations["performance_improvements"].extend([
                "Implement model ensemble optimization",
                "Deploy edge computing for latency reduction",
                "Optimize data preprocessing pipelines",
                "Implement adaptive batch sizing"
            ])
            
            return {
                "analysis_timestamp": datetime.now().isoformat(),
                "recommendations": recommendations,
                "optimization_opportunities": analysis.optimization_opportunities,
                "predicted_improvements": analysis.predicted_improvements,
                "bottlenecks": analysis.bottleneck_identification,
                "scaling_recommendations": analysis.scaling_recommendations
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization recommendations: {e}")
            return {"error": str(e)}


# Module initialization
logger.info("🤖 AI Processing Intelligence Engine module loaded")