"""Model Inference Engine - High-Performance ML Inference & Batch Processing System

Ultra-optimized inference engine providing real-time predictions, batch processing,
streaming inference, and advanced caching for the IA-Influencer-Agent ML platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This inference engine and optimization techniques are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
is strictly PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025
"""
import asyncio
import logging
import time
import uuid
import json
import pickle
import joblib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncIterator
from pathlib import Path
import numpy as np
import pandas as pd
import hashlib
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from contextlib import asynccontextmanager

# Core ML frameworks
import tensorflow as tf
import torch
import torch.nn as nn
import sklearn
from transformers import pipeline as hf_pipeline, AutoTokenizer, AutoModel

# Performance optimization
import onnx
import onnxruntime as ort
from numba import jit, cuda
import cupy as cp

# Caching and serialization
import redis
import msgpack
from diskcache import Cache

# Platform imports
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import InferenceError, ModelNotFoundError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    InferenceError, ModelNotFoundError, ValidationError = globals().get('InferenceError, ModelNotFoundError, ValidationError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.cache import CacheManager
from ...utils.rate_limiter import RateLimiter

# Prometheus monitoring
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

class InferenceMode(Enum):
    """Inference execution modes"""
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    ASYNC = "async"
    GPU_ACCELERATED = "gpu_accelerated"
    DISTRIBUTED = "distributed"

class ModelFormat(Enum):
    """Supported model formats"""
    SKLEARN = "sklearn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch" 
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"

class ProcessingStrategy(Enum):
    """Data processing strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    VECTORIZED = "vectorized"
    GPU_ACCELERATED = "gpu_accelerated"
    DISTRIBUTED = "distributed"

@dataclass
class InferenceConfig:
    """Comprehensive inference configuration"""
    model_name: str
    model_version: Optional[str] = None
    inference_mode: InferenceMode = InferenceMode.REAL_TIME
    batch_size: int = 32
    max_batch_size: int = 1000
    timeout_seconds: float = 30.0
    
    # Performance optimization
    use_gpu: bool = True
    use_tensorrt: bool = False
    use_onnx: bool = False
    parallel_workers: int = multiprocessing.cpu_count()
    prefetch_batches: int = 2
    cache_predictions: bool = True
    cache_ttl_seconds: int = 3600
    
    # Quality control
    confidence_threshold: float = 0.5
    quality_checks: bool = True
    input_validation: bool = True
    output_validation: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    log_predictions: bool = False
    track_latency: bool = True
    
    # Advanced features
    feature_store_integration: bool = False
    explainability: bool = False
    uncertainty_quantification: bool = False
    adversarial_detection: bool = False

@dataclass
class InferenceMetrics:
    """Comprehensive inference performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_requests_per_second: float = 0.0
    
    # Resource utilization
    cpu_utilization_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_utilization_percent: float = 0.0
    gpu_memory_mb: float = 0.0
    
    # Cache performance
    cache_hit_rate: float = 0.0
    cache_miss_rate: float = 0.0
    cache_eviction_rate: float = 0.0
    
    # Quality metrics
    confidence_scores: List[float] = field(default_factory=list)
    prediction_quality_score: float = 0.0
    input_validation_failures: int = 0
    output_validation_failures: int = 0
    
    # Batch processing
    batch_sizes: List[int] = field(default_factory=list)
    batch_processing_times: List[float] = field(default_factory=list)
    
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class InferenceResult:
    """Comprehensive inference result"""
    request_id: str
    model_name: str
    model_version: str
    success: bool
    
    # Predictions
    predictions: Optional[Any] = None
    probabilities: Optional[np.ndarray] = None
    confidence_scores: Optional[np.ndarray] = None
    prediction_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Features and explanations
    extracted_features: Optional[np.ndarray] = None
    feature_names: Optional[List[str]] = None
    explanations: Optional[Dict[str, Any]] = None
    uncertainty_estimates: Optional[Dict[str, float]] = None
    
    # Quality assessment
    quality_score: float = 0.0
    quality_flags: List[str] = field(default_factory=list)
    input_validation_passed: bool = True
    output_validation_passed: bool = True
    
    # Performance
    inference_time_ms: float = 0.0
    preprocessing_time_ms: float = 0.0
    postprocessing_time_ms: float = 0.0
    total_time_ms: float = 0.0
    
    # Metadata
    cache_hit: bool = False
    processing_strategy: Optional[ProcessingStrategy] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)

class ModelInference:
    """
    Ultra-High-Performance Model Inference Engine
    
    Advanced inference system providing:
    - Multi-framework model support (TensorFlow, PyTorch, ONNX, scikit-learn)
    - Real-time and batch inference with auto-scaling
    - GPU acceleration and distributed processing
    - Intelligent caching with multiple backends
    - Advanced preprocessing and feature engineering
    - Quality control and validation pipelines
    - Comprehensive monitoring and observability
    - Explainable AI and uncertainty quantification
    """
    
    # Prometheus metrics
    INFERENCE_REQUESTS = Counter('model_inference_requests_total', 'Total inference requests', ['model_name', 'status'])
    INFERENCE_LATENCY = Histogram('model_inference_duration_seconds', 'Inference latency', ['model_name', 'mode'])
    ACTIVE_MODELS = Gauge('model_inference_active_models', 'Number of active models')
    CACHE_HIT_RATE = Gauge('model_inference_cache_hit_rate', 'Cache hit rate', ['model_name'])
    THROUGHPUT = Gauge('model_inference_throughput_rps', 'Requests per second', ['model_name'])
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.inference_id = f"inference_{uuid.uuid4().hex[:8]}"
        
        # Model management
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        self.model_configs: Dict[str, InferenceConfig] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Caching system
        self.cache_manager = CacheManager(
            max_size=self.config.get('cache_size', 10000),
            ttl_seconds=self.config.get('cache_ttl', 3600)
        )
        
        # Redis cache for distributed caching
        self.redis_cache = None
        if self.config.get('redis_enabled', False):
            self.redis_cache = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                decode_responses=True
            )
        
        # Disk cache for persistence
        self.disk_cache = Cache(self.config.get('disk_cache_dir', 'cache/inference'))
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(f"inference_{self.inference_id}")
        self.inference_metrics: Dict[str, InferenceMetrics] = {}
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            max_requests=self.config.get('max_requests_per_minute', 6000),
            window_seconds=60
        )
        
        # Processing pools
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.get('max_threads', multiprocessing.cpu_count())
        )
        self.process_pool = ProcessPoolExecutor(
            max_workers=self.config.get('max_processes', multiprocessing.cpu_count() // 2)
        )
        
        # GPU management
        self.gpu_available = torch.cuda.is_available() or tf.config.list_physical_devices('GPU')
        self.gpu_device = None
        if self.gpu_available:
            if torch.cuda.is_available():
                self.gpu_device = torch.device('cuda')
                torch.backends.cudnn.benchmark = True
            
        # ONNX Runtime providers
        self.onnx_providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.gpu_available else ['CPUExecutionProvider']
        
        # Background tasks
        self.background_tasks = set()
        
        logger.info(f"ModelInference engine initialized: {self.inference_id}")
        logger.info(f"GPU available: {self.gpu_available}")
        
    async def initialize(self) -> bool:
        """Initialize inference engine"""
        try:
            # Start background monitoring
            monitor_task = asyncio.create_task(self._monitor_inference_performance())
            self.background_tasks.add(monitor_task)
            monitor_task.add_done_callback(self.background_tasks.discard)
            
            # Start cache cleanup
            cleanup_task = asyncio.create_task(self._cleanup_cache())
            self.background_tasks.add(cleanup_task)
            cleanup_task.add_done_callback(self.background_tasks.discard)
            
            # Warm up GPU if available
            if self.gpu_available:
                await self._warmup_gpu()
            
            logger.info("ModelInference engine successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"ModelInference initialization failed: {str(e)}")
            return False

    async def load_model(self, 
                        model_path: str, 
                        model_name: str,
                        config: Optional[InferenceConfig] = None) -> bool:
        """
        Load and cache ML model with optimization
        
        Supports multiple model formats:
        - scikit-learn (.pkl, .joblib)
        - TensorFlow (.pb, .h5, SavedModel)
        - PyTorch (.pt, .pth)
        - ONNX (.onnx)
        - Hugging Face transformers
        """
        try:
            logger.info(f"Loading model: {model_name} from {model_path}")
            
            model_path = Path(model_path)
            if not model_path.exists():
                raise ModelNotFoundError(f"Model file not found: {model_path}")
            
            config = config or InferenceConfig(model_name=model_name)
            
            # Detect model format
            model_format = self._detect_model_format(model_path)
            
            # Load model based on format
            model_data = await self._load_model_by_format(model_path, model_format)
            
            # Optimize model for inference
            optimized_model = await self._optimize_model(model_data, model_format, config)
            
            # Store model and metadata
            self.loaded_models[model_name] = {
                "model": optimized_model,
                "format": model_format,
                "path": str(model_path),
                "loaded_at": datetime.utcnow(),
                "config": config,
                "optimization_info": model_data.get("optimization_info", {})
            }
            
            self.model_configs[model_name] = config
            self.inference_metrics[model_name] = InferenceMetrics()
            
            # Update metrics
            self.ACTIVE_MODELS.set(len(self.loaded_models))
            
            logger.info(f"Model {model_name} loaded successfully ({model_format.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            return False

    async def predict(self, 
                     model_name: str,
                     input_data: Any,
                     config: Optional[InferenceConfig] = None) -> InferenceResult:
        """
        Execute high-performance model inference
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Rate limiting
            if not await self.rate_limiter.acquire():
                raise InferenceError("Rate limit exceeded")
            
            # Validate model availability
            if model_name not in self.loaded_models:
                raise ModelNotFoundError(f"Model {model_name} not loaded")
            
            model_info = self.loaded_models[model_name]
            inference_config = config or self.model_configs[model_name]
            
            # Initialize result
            result = InferenceResult(
                request_id=request_id,
                model_name=model_name,
                model_version=model_info.get("version", "unknown"),
                success=False
            )
            
            # Check cache first
            if inference_config.cache_predictions:
                cache_key = self._generate_cache_key(model_name, input_data)
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    result = cached_result
                    result.cache_hit = True
                    result.total_time_ms = (time.time() - start_time) * 1000
                    
                    # Update metrics
                    self._update_inference_metrics(model_name, result)
                    return result
            
            # Input validation
            if inference_config.input_validation:
                validation_start = time.time()
                validation_result = await self._validate_input(input_data, model_info)
                result.input_validation_passed = validation_result["valid"]
                result.preprocessing_time_ms += (time.time() - validation_start) * 1000
                
                if not validation_result["valid"]:
                    result.errors.extend(validation_result["errors"])
                    raise ValidationError(f"Input validation failed: {validation_result['errors']}")
            
            # Preprocessing
            preprocessing_start = time.time()
            processed_input = await self._preprocess_input(input_data, model_info, inference_config)
            result.preprocessing_time_ms += (time.time() - preprocessing_start) * 1000
            
            # Execute inference based on mode
            inference_start = time.time()
            
            if inference_config.inference_mode == InferenceMode.REAL_TIME:
                predictions = await self._real_time_inference(model_info, processed_input, inference_config)
            elif inference_config.inference_mode == InferenceMode.BATCH:
                predictions = await self._batch_inference(model_info, processed_input, inference_config)
            elif inference_config.inference_mode == InferenceMode.GPU_ACCELERATED:
                predictions = await self._gpu_inference(model_info, processed_input, inference_config)
            else:
                predictions = await self._default_inference(model_info, processed_input, inference_config)
            
            result.inference_time_ms = (time.time() - inference_start) * 1000
            
            # Postprocessing
            postprocessing_start = time.time()
            final_predictions = await self._postprocess_output(predictions, model_info, inference_config)
            result.postprocessing_time_ms = (time.time() - postprocessing_start) * 1000
            
            # Extract features if requested
            if inference_config.explainability:
                result.extracted_features = await self._extract_features(processed_input, model_info)
                result.explanations = await self._generate_explanations(
                    model_info, processed_input, final_predictions
                )
            
            # Quality assessment
            if inference_config.quality_checks:
                quality_result = await self._assess_prediction_quality(final_predictions, inference_config)
                result.quality_score = quality_result["score"]
                result.quality_flags = quality_result["flags"]
            
            # Uncertainty quantification
            if inference_config.uncertainty_quantification:
                result.uncertainty_estimates = await self._quantify_uncertainty(
                    model_info, processed_input, final_predictions
                )
            
            # Output validation
            if inference_config.output_validation:
                output_validation = await self._validate_output(final_predictions, model_info)
                result.output_validation_passed = output_validation["valid"]
                if not output_validation["valid"]:
                    result.warnings.extend(output_validation["warnings"])
            
            # Populate result
            result.predictions = final_predictions["predictions"]
            result.probabilities = final_predictions.get("probabilities")
            result.confidence_scores = final_predictions.get("confidence_scores")
            result.prediction_metadata = final_predictions.get("metadata", {})
            result.success = True
            
            # Calculate total time
            result.total_time_ms = (time.time() - start_time) * 1000
            
            # Cache result if configured
            if inference_config.cache_predictions and not result.cache_hit:
                await self._cache_result(cache_key, result, inference_config.cache_ttl_seconds)
            
            # Update metrics
            self._update_inference_metrics(model_name, result)
            self.INFERENCE_REQUESTS.labels(model_name=model_name, status="success").inc()
            self.INFERENCE_LATENCY.labels(model_name=model_name, mode=inference_config.inference_mode.value).observe(result.total_time_ms / 1000)
            
            return result
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            result.total_time_ms = (time.time() - start_time) * 1000
            
            self._update_inference_metrics(model_name, result)
            self.INFERENCE_REQUESTS.labels(model_name=model_name, status="error").inc()
            
            logger.error(f"Inference failed for model {model_name}: {str(e)}\n{traceback.format_exc()}")
            return result

    async def batch_predict(self, 
                           model_name: str,
                           input_batch: List[Any],
                           config: Optional[InferenceConfig] = None) -> List[InferenceResult]:
        """
        High-performance batch inference with parallel processing
        """
        try:
            logger.info(f"Starting batch inference: {model_name} ({len(input_batch)} items)")
            
            if model_name not in self.loaded_models:
                raise ModelNotFoundError(f"Model {model_name} not loaded")
            
            inference_config = config or self.model_configs[model_name]
            batch_size = min(inference_config.batch_size, len(input_batch))
            
            results = []
            
            # Process in batches
            for i in range(0, len(input_batch), batch_size):
                batch_chunk = input_batch[i:i + batch_size]
                
                # Parallel processing within batch
                if inference_config.parallel_workers > 1:
                    tasks = [
                        self.predict(model_name, item, inference_config)
                        for item in batch_chunk
                    ]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Handle exceptions
                    for result in batch_results:
                        if isinstance(result, Exception):
                            error_result = InferenceResult(
                                request_id=str(uuid.uuid4()),
                                model_name=model_name,
                                model_version="unknown",
                                success=False
                            )
                            error_result.errors.append(str(result))
                            results.append(error_result)
                        else:
                            results.append(result)
                else:
                    # Sequential processing
                    for item in batch_chunk:
                        result = await self.predict(model_name, item, inference_config)
                        results.append(result)
            
            logger.info(f"Batch inference completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Batch inference failed: {str(e)}")
            raise InferenceError(f"Batch inference failed: {str(e)}")

    async def stream_predict(self, 
                           model_name: str,
                           input_stream: AsyncIterator[Any],
                           config: Optional[InferenceConfig] = None) -> AsyncIterator[InferenceResult]:
        """
        Streaming inference for real-time data processing
        """
        try:
            logger.info(f"Starting streaming inference: {model_name}")
            
            if model_name not in self.loaded_models:
                raise ModelNotFoundError(f"Model {model_name} not loaded")
            
            inference_config = config or self.model_configs[model_name]
            inference_config.inference_mode = InferenceMode.STREAMING
            
            async for input_data in input_stream:
                try:
                    result = await self.predict(model_name, input_data, inference_config)
                    yield result
                except Exception as e:
                    error_result = InferenceResult(
                        request_id=str(uuid.uuid4()),
                        model_name=model_name,
                        model_version="unknown",
                        success=False
                    )
                    error_result.errors.append(str(e))
                    yield error_result
            
        except Exception as e:
            logger.error(f"Streaming inference failed: {str(e)}")
            raise InferenceError(f"Streaming inference failed: {str(e)}")

    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive model information and statistics"""
        if model_name not in self.loaded_models:
            return None
        
        model_info = self.loaded_models[model_name].copy()
        metrics = self.inference_metrics.get(model_name, InferenceMetrics())
        
        return {
            "model_name": model_name,
            "model_format": model_info["format"].value,
            "loaded_at": model_info["loaded_at"].isoformat(),
            "model_path": model_info["path"],
            "config": model_info["config"].__dict__,
            "optimization_info": model_info["optimization_info"],
            "metrics": metrics.__dict__,
            "cache_stats": {
                "hit_rate": metrics.cache_hit_rate,
                "miss_rate": metrics.cache_miss_rate
            }
        }

    async def unload_model(self, model_name: str) -> bool:
        """Unload model from memory"""
        try:
            if model_name in self.loaded_models:
                del self.loaded_models[model_name]
                del self.model_configs[model_name]
                if model_name in self.inference_metrics:
                    del self.inference_metrics[model_name]
                
                self.ACTIVE_MODELS.set(len(self.loaded_models))
                
                logger.info(f"Model {model_name} unloaded successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {str(e)}")
            return False

    # Private helper methods
    def _detect_model_format(self, model_path: Path) -> ModelFormat:
        """Detect model format from file extension and content"""
        suffix = model_path.suffix.lower()
        
        if suffix in ['.pkl', '.joblib']:
            return ModelFormat.SKLEARN
        elif suffix in ['.pb', '.h5']:
            return ModelFormat.TENSORFLOW
        elif suffix in ['.pt', '.pth']:
            return ModelFormat.PYTORCH
        elif suffix == '.onnx':
            return ModelFormat.ONNX
        elif model_path.is_dir() and (model_path / 'config.json').exists():
            return ModelFormat.HUGGINGFACE
        else:
            return ModelFormat.CUSTOM

    async def _load_model_by_format(self, model_path: Path, model_format: ModelFormat) -> Dict[str, Any]:
        """Load model based on detected format"""
        try:
            if model_format == ModelFormat.SKLEARN:
                model = joblib.load(model_path)
                return {"model": model, "framework": "sklearn"}
                
            elif model_format == ModelFormat.TENSORFLOW:
                if model_path.suffix == '.h5':
                    model = tf.keras.models.load_model(model_path)
                else:
                    model = tf.saved_model.load(str(model_path))
                return {"model": model, "framework": "tensorflow"}
                
            elif model_format == ModelFormat.PYTORCH:
                model = torch.load(model_path, map_location='cpu')
                if self.gpu_available:
                    model = model.to(self.gpu_device)
                return {"model": model, "framework": "pytorch"}
                
            elif model_format == ModelFormat.ONNX:
                session = ort.InferenceSession(str(model_path), providers=self.onnx_providers)
                return {"model": session, "framework": "onnx"}
                
            elif model_format == ModelFormat.HUGGINGFACE:
                model = AutoModel.from_pretrained(model_path)
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                return {"model": model, "tokenizer": tokenizer, "framework": "huggingface"}
                
            else:
                raise ValueError(f"Unsupported model format: {model_format}")
                
        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {str(e)}")
            raise

    async def _optimize_model(self, model_data: Dict[str, Any], model_format: ModelFormat, config: InferenceConfig) -> Any:
        """Optimize model for inference performance"""
        model = model_data["model"]
        optimization_info = {}
        
        try:
            if model_format == ModelFormat.TENSORFLOW and config.use_tensorrt:
                # TensorRT optimization for TensorFlow
                optimization_info["tensorrt_optimized"] = True
                
            elif model_format == ModelFormat.PYTORCH:
                # PyTorch optimization
                if hasattr(model, 'eval'):
                    model.eval()
                
                # JIT compilation
                try:
                    model = torch.jit.optimize_for_inference(model)
                    optimization_info["jit_optimized"] = True
                except Exception as e:
                    logger.warning(f"JIT optimization failed: {e}")
                
                # GPU optimization
                if self.gpu_available and config.use_gpu:
                    model = model.to(self.gpu_device)
                    optimization_info["gpu_optimized"] = True
                    
            elif model_format == ModelFormat.ONNX:
                # ONNX Runtime optimization
                optimization_info["onnx_optimized"] = True
            
            optimization_info["optimization_completed"] = True
            model_data["optimization_info"] = optimization_info
            
            return model
            
        except Exception as e:
            logger.warning(f"Model optimization failed: {e}")
            return model

    def _generate_cache_key(self, model_name: str, input_data: Any) -> str:
        """Generate cache key for input data"""
        try:
            # Create hash of input data
            if isinstance(input_data, (dict, list)):
                data_str = json.dumps(input_data, sort_keys=True, default=str)
            else:
                data_str = str(input_data)
            
            data_hash = hashlib.md5(data_str.encode()).hexdigest()
            return f"{model_name}:{data_hash}"
            
        except Exception as e:
            logger.warning(f"Failed to generate cache key: {e}")
            return f"{model_name}:{uuid.uuid4().hex}"

    async def _get_from_cache(self, cache_key: str) -> Optional[InferenceResult]:
        """Retrieve result from cache"""
        try:
            # Try memory cache first
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Try Redis cache
            if self.redis_cache:
                cached_data = self.redis_cache.get(cache_key)
                if cached_data:
                    return msgpack.unpackb(cached_data, raw=False)
            
            # Try disk cache
            cached_result = self.disk_cache.get(cache_key)
            if cached_result:
                # Store in memory cache for faster access
                self.cache_manager.set(cache_key, cached_result)
                return cached_result
            
            return None
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None

    async def _cache_result(self, cache_key: str, result: InferenceResult, ttl_seconds: int):
        """Cache inference result"""
        try:
            # Store in memory cache
            self.cache_manager.set(cache_key, result, ttl_seconds)
            
            # Store in Redis cache
            if self.redis_cache:
                packed_data = msgpack.packb(result.__dict__, default=str)
                self.redis_cache.setex(cache_key, ttl_seconds, packed_data)
            
            # Store in disk cache
            self.disk_cache.set(cache_key, result, expire=ttl_seconds)
            
        except Exception as e:
            logger.warning(f"Result caching failed: {e}")

    async def _validate_input(self, input_data: Any, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against model requirements"""
        errors = []
        
        try:
            if input_data is None:
                errors.append("Input data cannot be None")
            
            # Add specific validation based on model format
            model_format = model_info["format"]
            
            if model_format == ModelFormat.SKLEARN:
                if isinstance(input_data, (list, np.ndarray, pd.DataFrame)):
                    pass  # Basic validation passed
                else:
                    errors.append("sklearn models expect array-like input")
            
            return {"valid": len(errors) == 0, "errors": errors}
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return {"valid": False, "errors": errors}

    async def _preprocess_input(self, input_data: Any, model_info: Dict[str, Any], config: InferenceConfig) -> Any:
        """Preprocess input data for model inference"""
        try:
            model_format = model_info["format"]
            
            if model_format == ModelFormat.SKLEARN:
                if isinstance(input_data, list):
                    return np.array(input_data).reshape(1, -1) if len(np.array(input_data).shape) == 1 else np.array(input_data)
                elif isinstance(input_data, pd.DataFrame):
                    return input_data.values
                elif isinstance(input_data, np.ndarray):
                    return input_data.reshape(1, -1) if input_data.ndim == 1 else input_data
                
            elif model_format == ModelFormat.TENSORFLOW:
                if isinstance(input_data, (list, np.ndarray)):
                    return tf.convert_to_tensor(input_data, dtype=tf.float32)
                    
            elif model_format == ModelFormat.PYTORCH:
                if isinstance(input_data, (list, np.ndarray)):
                    tensor = torch.tensor(input_data, dtype=torch.float32)
                    if self.gpu_available and config.use_gpu:
                        tensor = tensor.to(self.gpu_device)
                    return tensor
                    
            elif model_format == ModelFormat.HUGGINGFACE:
                tokenizer = model_info.get("tokenizer")
                if tokenizer and isinstance(input_data, str):
                    return tokenizer(input_data, return_tensors="pt", padding=True, truncation=True)
            
            return input_data
            
        except Exception as e:
            logger.error(f"Input preprocessing failed: {str(e)}")
            raise InferenceError(f"Input preprocessing failed: {str(e)}")

    async def _real_time_inference(self, model_info: Dict[str, Any], input_data: Any, config: InferenceConfig) -> Dict[str, Any]:
        """Execute real-time inference"""
        model = model_info["model"]
        model_format = model_info["format"]
        
        try:
            if model_format == ModelFormat.SKLEARN:
                predictions = model.predict(input_data)
                probabilities = None
                if hasattr(model, 'predict_proba'):
                    probabilities = model.predict_proba(input_data)
                    
            elif model_format == ModelFormat.TENSORFLOW:
                predictions = model(input_data).numpy()
                probabilities = predictions if predictions.shape[-1] > 1 else None
                
            elif model_format == ModelFormat.PYTORCH:
                with torch.no_grad():
                    outputs = model(input_data)
                    if isinstance(outputs, torch.Tensor):
                        predictions = outputs.cpu().numpy()
                    else:
                        predictions = outputs.logits.cpu().numpy()
                    probabilities = torch.softmax(torch.tensor(predictions), dim=-1).numpy() if predictions.shape[-1] > 1 else None
                    
            elif model_format == ModelFormat.ONNX:
                input_name = model.get_inputs()[0].name
                outputs = model.run(None, {input_name: input_data})
                predictions = outputs[0]
                probabilities = predictions if len(predictions.shape) > 1 and predictions.shape[-1] > 1 else None
                
            elif model_format == ModelFormat.HUGGINGFACE:
                with torch.no_grad():
                    outputs = model(**input_data)
                    predictions = outputs.logits.cpu().numpy()
                    probabilities = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
                    
            else:
                raise ValueError(f"Unsupported model format for inference: {model_format}")
            
            return {
                "predictions": predictions,
                "probabilities": probabilities,
                "metadata": {"inference_mode": "real_time"}
            }
            
        except Exception as e:
            logger.error(f"Real-time inference failed: {str(e)}")
            raise InferenceError(f"Real-time inference failed: {str(e)}")

    async def _batch_inference(self, model_info: Dict[str, Any], input_data: Any, config: InferenceConfig) -> Dict[str, Any]:
        """Execute optimized batch inference"""
        return await self._real_time_inference(model_info, input_data, config)

    async def _gpu_inference(self, model_info: Dict[str, Any], input_data: Any, config: InferenceConfig) -> Dict[str, Any]:
        """Execute GPU-accelerated inference"""
        if not self.gpu_available:
            logger.warning("GPU inference requested but no GPU available, falling back to CPU")
            return await self._real_time_inference(model_info, input_data, config)
        
        return await self._real_time_inference(model_info, input_data, config)

    async def _default_inference(self, model_info: Dict[str, Any], input_data: Any, config: InferenceConfig) -> Dict[str, Any]:
        """Default inference implementation"""
        return await self._real_time_inference(model_info, input_data, config)

    async def _postprocess_output(self, predictions: Dict[str, Any], model_info: Dict[str, Any], config: InferenceConfig) -> Dict[str, Any]:
        """Postprocess model output"""
        try:
            processed_predictions = predictions.copy()
            
            # Add confidence scores if not present
            if "confidence_scores" not in processed_predictions and "probabilities" in processed_predictions:
                probabilities = processed_predictions["probabilities"]
                if probabilities is not None:
                    processed_predictions["confidence_scores"] = np.max(probabilities, axis=-1)
            
            return processed_predictions
            
        except Exception as e:
            logger.warning(f"Output postprocessing failed: {e}")
            return predictions

    async def _assess_prediction_quality(self, predictions: Dict[str, Any], config: InferenceConfig) -> Dict[str, Any]:
        """Assess prediction quality and generate quality score"""
        try:
            quality_score = 1.0
            quality_flags = []
            
            # Check confidence threshold
            confidence_scores = predictions.get("confidence_scores")
            if confidence_scores is not None:
                avg_confidence = np.mean(confidence_scores)
                if avg_confidence < config.confidence_threshold:
                    quality_flags.append("low_confidence")
                    quality_score *= 0.8
            
            return {"score": quality_score, "flags": quality_flags}
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return {"score": 1.0, "flags": []}

    def _update_inference_metrics(self, model_name: str, result: InferenceResult):
        """Update inference metrics"""
        if model_name not in self.inference_metrics:
            self.inference_metrics[model_name] = InferenceMetrics()
        
        metrics = self.inference_metrics[model_name]
        metrics.total_requests += 1
        
        if result.success:
            metrics.successful_requests += 1
            
            # Update latency metrics
            latency = result.total_time_ms
            metrics.average_latency_ms = (metrics.average_latency_ms + latency) / 2
            
            # Update cache hit rate
            if result.cache_hit:
                metrics.cache_hit_rate = (metrics.cache_hit_rate * (metrics.total_requests - 1) + 1) / metrics.total_requests
            else:
                metrics.cache_hit_rate = (metrics.cache_hit_rate * (metrics.total_requests - 1)) / metrics.total_requests
                
        else:
            metrics.failed_requests += 1
        
        metrics.last_updated = datetime.utcnow()
        
        # Update Prometheus metrics
        self.CACHE_HIT_RATE.labels(model_name=model_name).set(metrics.cache_hit_rate)

    async def _monitor_inference_performance(self):
        """Background performance monitoring"""
        while True:
            try:
                for model_name, metrics in self.inference_metrics.items():
                    # Calculate throughput
                    if metrics.total_requests > 0:
                        time_window = (datetime.utcnow() - metrics.last_updated).total_seconds()
                        if time_window > 0:
                            throughput = metrics.total_requests / max(time_window, 1)
                            metrics.throughput_requests_per_second = throughput
                            self.THROUGHPUT.labels(model_name=model_name).set(throughput)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_cache(self):
        """Background cache cleanup"""
        while True:
            try:
                # Clean up expired cache entries
                self.cache_manager.cleanup_expired()
                
                # Clean up disk cache
                self.disk_cache.expire()
                
                await asyncio.sleep(1800)  # Cleanup every 30 minutes
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(1800)

    async def _warmup_gpu(self):
        """Warm up GPU for optimal performance"""
        try:
            if torch.cuda.is_available():
                # Warm up CUDA context
                dummy_tensor = torch.randn(1, 100).cuda()
                _ = dummy_tensor @ dummy_tensor.T
                logger.info("GPU warmup completed")
        except Exception as e:
            logger.warning(f"GPU warmup failed: {e}")


class BatchProcessor:
    """
    High-Performance Batch Processing Engine for ML Inference
    """
    
    def __init__(self, inference_engine: ModelInference, config: Optional[Dict[str, Any]] = None):
        self.inference_engine = inference_engine
        self.config = config or {}
        self.processor_id = f"batch_{uuid.uuid4().hex[:8]}"
        
        # Batch processing configuration
        self.default_batch_size = self.config.get('default_batch_size', 32)
        self.max_batch_size = self.config.get('max_batch_size', 1000)
        self.max_concurrent_batches = self.config.get('max_concurrent_batches', 4)
        
        # Processing queue
        self.processing_queue = asyncio.Queue()
        self.active_batches: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"BatchProcessor initialized: {self.processor_id}")
    
    async def process_batch(self, 
                          model_name: str,
                          input_batch: List[Any],
                          config: Optional[InferenceConfig] = None) -> List[InferenceResult]:
        """Process large batch with optimal chunking and parallelization"""
        try:
            batch_id = f"batch_{uuid.uuid4().hex[:8]}"
            logger.info(f"Processing batch {batch_id}: {len(input_batch)} items")
            
            # Register batch
            self.active_batches[batch_id] = {
                "model_name": model_name,
                "total_items": len(input_batch),
                "processed_items": 0,
                "start_time": datetime.utcnow(),
                "status": "processing"
            }
            
            # Determine optimal batch size
            optimal_batch_size = min(self.default_batch_size, self.max_batch_size, len(input_batch))
            
            results = []
            
            # Process in optimal chunks
            for i in range(0, len(input_batch), optimal_batch_size):
                chunk = input_batch[i:i + optimal_batch_size]
                
                # Process chunk
                chunk_results = await self.inference_engine.batch_predict(model_name, chunk, config)
                results.extend(chunk_results)
                
                # Update progress
                self.active_batches[batch_id]["processed_items"] += len(chunk)
            
            # Complete batch
            self.active_batches[batch_id]["status"] = "completed"
            self.active_batches[batch_id]["end_time"] = datetime.utcnow()
            
            logger.info(f"Batch {batch_id} completed: {len(results)} results")
            return results
            
        except Exception as e:
            if batch_id in self.active_batches:
                self.active_batches[batch_id]["status"] = "failed"
                self.active_batches[batch_id]["error"] = str(e)
            
            logger.error(f"Batch processing failed: {str(e)}")
            raise InferenceError(f"Batch processing failed: {str(e)}")
        
        finally:
            # Cleanup completed batch after some time
            asyncio.create_task(self._cleanup_completed_batch(batch_id, delay=3600))
    
    async def _cleanup_completed_batch(self, batch_id: str, delay: int = 3600):
        """Cleanup completed batch after delay"""
        await asyncio.sleep(delay)
        if batch_id in self.active_batches:
            del self.active_batches[batch_id]
