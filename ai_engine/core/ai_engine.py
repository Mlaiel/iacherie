"""AI Engine Management Module

Enterprise-grade AI engine orchestration and lifecycle management for industrial content platform.
Supports advanced AI workload management for multi-format content creators.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""
import asyncio
import threading
import time
import gc
from typing import Dict, Any, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager, contextmanager
import logging
import json
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import weakref

# AI and ML imports
try:
    import torch
    import torch.nn as nn
    from transformers import AutoModel, AutoTokenizer, pipeline
    import numpy as np
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

from .exceptions import ModelConnectionError, ConfigurationError, OptimizationError
from .metrics import metrics_collector
from .performance import performance_monitor

logger = logging.getLogger(__name__)


class AIModelType(Enum):
    """Supported AI model types"""    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    DIFFUSION = "diffusion"
    GAN = "gan"
    AUDIO_CLASSIFIER = "audio_classifier"
    IMAGE_CLASSIFIER = "image_classifier"
    TEXT_CLASSIFIER = "text_classifier"
    CONTENT_GENERATOR = "content_generator"
    PROTECTION_DETECTOR = "protection_detector"
    QUALITY_ASSESSOR = "quality_assessor"
    SEO_OPTIMIZER = "seo_optimizer"
    COLLABORATION_MATCHER = "collaboration_matcher"


class ModelStatus(Enum):
    """AI model status states"""    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    UNLOADING = "unloading"


class DeviceType(Enum):
    """Device types for model execution"""    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Metal
    AUTO = "auto"


@dataclass
class ModelConfig:
    """Configuration for AI model"""    name: str
    model_type: AIModelType
    model_path: str
    device: DeviceType = DeviceType.AUTO
    batch_size: int = 1
    max_length: int = 512
    precision: str = "float32"
    cache_size: int = 1000
    timeout_seconds: int = 30
    memory_limit_gb: Optional[float] = None
    auto_unload_after_seconds: int = 300
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)
    postprocessing_config: Dict[str, Any] = field(default_factory=dict)
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            "name": self.name,
            "model_type": self.model_type.value,
            "model_path": self.model_path,
            "device": self.device.value,
            "batch_size": self.batch_size,
            "max_length": self.max_length,
            "precision": self.precision,
            "cache_size": self.cache_size,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_gb": self.memory_limit_gb,
            "auto_unload_after_seconds": self.auto_unload_after_seconds,
            "preprocessing_config": self.preprocessing_config,
            "postprocessing_config": self.postprocessing_config,
            "custom_config": self.custom_config
        }


@dataclass
class ModelMetrics:
    """Metrics for AI model performance"""    model_name: str
    load_time: float = 0.0
    inference_count: int = 0
    total_inference_time: float = 0.0
    average_inference_time: float = 0.0
    peak_memory_usage: float = 0.0
    error_count: int = 0
    last_used: datetime = field(default_factory=datetime.utcnow)
    cache_hits: int = 0
    cache_misses: int = 0
    
    def update_inference_stats(self, inference_time: float):
        """Update inference statistics"""        self.inference_count += 1
        self.total_inference_time += inference_time
        self.average_inference_time = self.total_inference_time / self.inference_count
        self.last_used = datetime.utcnow()
        
    def update_cache_stats(self, hit: bool):
        """Update cache statistics"""        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class ModelCache:
    """Advanced caching system for AI model results"""    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
    def _generate_key(self, input_data: Any, model_config: Dict[str, Any]) -> str:
        """Generate cache key for input and configuration"""        # Create deterministic hash from input and config
        content = json.dumps({
            "input": str(input_data),
            "config": model_config
        }, sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()
        
    def get(self, input_data: Any, model_config: Dict[str, Any]) -> Optional[Any]:
        """Get cached result"""        key = self._generate_key(input_data, model_config)
        
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check TTL
                if datetime.utcnow() - entry["timestamp"] < timedelta(seconds=self.ttl_seconds):
                    entry["access_count"] += 1
                    entry["last_access"] = datetime.utcnow()
                    return entry["result"]
                else:
                    # Expired
                    del self.cache[key]
                    
        return None
        
    def put(self, input_data: Any, model_config: Dict[str, Any], result: Any):
        """Cache result"""        key = self._generate_key(input_data, model_config)
        
        with self._lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]["last_access"]
                )
                del self.cache[oldest_key]
                
            self.cache[key] = {
                "result": result,
                "timestamp": datetime.utcnow(),
                "last_access": datetime.utcnow(),
                "access_count": 1
            }
            
    def clear(self):
        """Clear all cached entries"""        with self._lock:
            self.cache.clear()
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""        with self._lock:
            total_access = sum(entry["access_count"] for entry in self.cache.values())
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "total_accesses": total_access,
                "memory_usage_estimate": len(str(self.cache)) * 8  # Rough estimate
            }


class AIModel:
    """Wrapper for AI model with advanced lifecycle management"""    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.status = ModelStatus.UNLOADED
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = None
        self.metrics = ModelMetrics(config.name)
        self.cache = ModelCache(config.cache_size)
        self._lock = threading.RLock()
        self._last_activity = datetime.utcnow()
        
        logger.info(f"AI model '{config.name}' initialized with config: {config.model_type.value}")
        
    def load(self) -> bool:
        """Load the AI model"""        if self.status in [ModelStatus.LOADED, ModelStatus.READY, ModelStatus.LOADING]:
            return True
            
        with self._lock:
            if self.status != ModelStatus.UNLOADED:
                return self.status == ModelStatus.READY
                
            self.status = ModelStatus.LOADING
            load_start = time.perf_counter()
            
            try:
                # Determine device
                self.device = self._determine_device()
                logger.info(f"Loading model '{self.config.name}' on device: {self.device}")
                
                # Load model based on type
                if self.config.model_type == AIModelType.TRANSFORMER:
                    self._load_transformer_model()
                elif self.config.model_type == AIModelType.CNN:
                    self._load_cnn_model()
                elif self.config.model_type == AIModelType.AUDIO_CLASSIFIER:
                    self._load_audio_model()
                elif self.config.model_type == AIModelType.IMAGE_CLASSIFIER:
                    self._load_image_model()
                else:
                    self._load_generic_model()
                    
                # Model loaded successfully
                load_time = time.perf_counter() - load_start
                self.metrics.load_time = load_time
                self.status = ModelStatus.READY
                self._last_activity = datetime.utcnow()
                
                logger.info(f"Model '{self.config.name}' loaded successfully in {load_time:.2f}s")
                
                # Record metrics
                metrics_collector.record_timer("ai.model.load_time", load_time, {
                    "model_name": self.config.name,
                    "model_type": self.config.model_type.value
                })
                
                return True
                
            except Exception as e:
                self.status = ModelStatus.ERROR
                logger.error(f"Failed to load model '{self.config.name}': {e}")
                raise ModelConnectionError(
                    f"Failed to load model '{self.config.name}': {str(e)}",
                    model_name=self.config.name,
                    model_version="unknown"
                )
                
    def _determine_device(self) -> str:
        """Determine the best device for model execution"""        if self.config.device == DeviceType.AUTO:
            if PYTORCH_AVAILABLE and torch.cuda.is_available():
                return "cuda"
            elif PYTORCH_AVAILABLE and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        else:
            return self.config.device.value
            
    def _load_transformer_model(self):
        """Load transformer model"""        if not PYTORCH_AVAILABLE:
            raise ConfigurationError("PyTorch not available for transformer model")
            
        from transformers import AutoModel, AutoTokenizer
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path)
        self.model = AutoModel.from_pretrained(self.config.model_path)
        
        if self.device != "cpu":
            self.model = self.model.to(self.device)
            
        self.model.eval()  # Set to evaluation mode
        
    def _load_cnn_model(self):
        """Load CNN model"""        if not PYTORCH_AVAILABLE:
            raise ConfigurationError("PyTorch not available for CNN model")
            
        # Load custom CNN model
        model_path = Path(self.config.model_path)
        if model_path.suffix == '.pth':
            self.model = torch.load(model_path, map_location=self.device)
        else:
            raise ConfigurationError(f"Unsupported CNN model format: {model_path.suffix}")
            
    def _load_audio_model(self):
        """Load audio processing model"""        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "audio-classification",
                model=self.config.model_path,
                device=0 if self.device == "cuda" else -1
            )
        except Exception as e:
            raise ModelConnectionError(f"Failed to load audio model: {e}")
            
    def _load_image_model(self):
        """Load image processing model"""        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "image-classification",
                model=self.config.model_path,
                device=0 if self.device == "cuda" else -1
            )
        except Exception as e:
            raise ModelConnectionError(f"Failed to load image model: {e}")
            
    def _load_generic_model(self):
        """Load generic model"""        # Implement generic model loading logic
        logger.warning(f"Generic model loading for type {self.config.model_type.value}")
        
    def unload(self):
        """Unload the AI model to free memory"""        with self._lock:
            if self.status == ModelStatus.UNLOADED:
                return
                
            self.status = ModelStatus.UNLOADING
            
            try:
                # Clear model references
                self.model = None
                self.tokenizer = None
                self.pipeline = None
                
                # Clear cache
                self.cache.clear()
                
                # Force garbage collection
                gc.collect()
                
                if PYTORCH_AVAILABLE and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                self.status = ModelStatus.UNLOADED
                logger.info(f"Model '{self.config.name}' unloaded successfully")
                
            except Exception as e:
                logger.error(f"Error unloading model '{self.config.name}': {e}")
                self.status = ModelStatus.ERROR
                
    def predict(self, input_data: Any, use_cache: bool = True, **kwargs) -> Any:
        """Make prediction with the model"""        if self.status != ModelStatus.READY:
            if not self.load():
                raise ModelConnectionError(f"Model '{self.config.name}' is not ready")
                
        # Check cache first
        if use_cache:
            cached_result = self.cache.get(input_data, self.config.to_dict())
            if cached_result is not None:
                self.metrics.update_cache_stats(True)
                self._last_activity = datetime.utcnow()
                return cached_result
            else:
                self.metrics.update_cache_stats(False)
                
        with self._lock:
            self.status = ModelStatus.BUSY
            inference_start = time.perf_counter()
            
            try:
                # Perform inference based on model type
                if self.pipeline:
                    result = self._predict_with_pipeline(input_data, **kwargs)
                elif self.model and self.tokenizer:
                    result = self._predict_with_transformer(input_data, **kwargs)
                elif self.model:
                    result = self._predict_with_model(input_data, **kwargs)
                else:
                    raise ModelConnectionError("No valid model interface available")
                    
                inference_time = time.perf_counter() - inference_start
                
                # Update metrics
                self.metrics.update_inference_stats(inference_time)
                self._last_activity = datetime.utcnow()
                
                # Cache result
                if use_cache:
                    self.cache.put(input_data, self.config.to_dict(), result)
                    
                # Record metrics
                metrics_collector.record_timer("ai.model.inference_time", inference_time, {
                    "model_name": self.config.name,
                    "model_type": self.config.model_type.value
                })
                
                self.status = ModelStatus.READY
                return result
                
            except Exception as e:
                self.status = ModelStatus.READY  # Return to ready state
                self.metrics.error_count += 1
                logger.error(f"Inference failed for model '{self.config.name}': {e}")
                raise
                
    def _predict_with_pipeline(self, input_data: Any, **kwargs) -> Any:
        """Predict using Hugging Face pipeline"""        return self.pipeline(input_data, **kwargs)
        
    def _predict_with_transformer(self, input_data: str, **kwargs) -> Any:
        """Predict using transformer model"""        # Tokenize input
        inputs = self.tokenizer(
            input_data,
            return_tensors="pt",
            max_length=self.config.max_length,
            truncation=True,
            padding=True
        )
        
        if self.device != "cpu":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
        # Forward pass
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        return outputs
        
    def _predict_with_model(self, input_data: Any, **kwargs) -> Any:
        """Predict using generic model"""        # Implement generic prediction logic
        if hasattr(self.model, 'predict'):
            return self.model.predict(input_data)
        elif hasattr(self.model, '__call__'):
            return self.model(input_data)
        else:
            raise ModelConnectionError("Model does not have predict method")
            
    @property
    def is_idle(self) -> bool:
        """Check if model has been idle for auto-unload threshold"""        idle_time = (datetime.utcnow() - self._last_activity).total_seconds()
        return idle_time > self.config.auto_unload_after_seconds
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics"""        return {
            "model_name": self.config.name,
            "model_type": self.config.model_type.value,
            "status": self.status.value,
            "device": self.device,
            "load_time": self.metrics.load_time,
            "inference_count": self.metrics.inference_count,
            "average_inference_time": self.metrics.average_inference_time,
            "error_count": self.metrics.error_count,
            "cache_hit_rate": self.metrics.cache_hit_rate,
            "last_used": self.metrics.last_used.isoformat(),
            "cache_stats": self.cache.get_stats()
        }


class AIEngineManager:
    """    Enterprise-grade AI engine orchestration and lifecycle management
    
    Features:
    - Dynamic model loading/unloading
    - Automatic resource optimization
    - Load balancing and scaling
    - Performance monitoring
    - Error recovery and failover
    - Memory management and caching
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.models: Dict[str, AIModel] = {}
        self.model_pool = ThreadPoolExecutor(max_workers=4)
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        
        # Configuration
        self.auto_cleanup_interval = self.config.get("auto_cleanup_interval", 300)  # 5 minutes
        self.max_concurrent_models = self.config.get("max_concurrent_models", 5)
        self.memory_threshold_gb = self.config.get("memory_threshold_gb", 8.0)
        
        # Start background cleanup
        self._start_cleanup_thread()
        
        logger.info("AI Engine Manager initialized with advanced orchestration capabilities")
        
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""        if self._cleanup_thread is None:
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True
            )
            self._cleanup_thread.start()
            
    def _cleanup_loop(self):
        """Background cleanup loop for idle models"""        while not self._stop_cleanup.wait(self.auto_cleanup_interval):
            try:
                self._cleanup_idle_models()
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                
    def _cleanup_idle_models(self):
        """Unload idle models to free resources"""        with self._lock:
            idle_models = [
                name for name, model in self.models.items()
                if model.is_idle and model.status == ModelStatus.READY
            ]
            
            for model_name in idle_models:
                try:
                    self.models[model_name].unload()
                    logger.info(f"Auto-unloaded idle model: {model_name}")
                except Exception as e:
                    logger.error(f"Error auto-unloading model {model_name}: {e}")
                    
    def register_model(self, config: ModelConfig) -> bool:
        """Register a new AI model"""        with self._lock:
            if config.name in self.models:
                logger.warning(f"Model '{config.name}' already registered")
                return False
                
            model = AIModel(config)
            self.models[config.name] = model
            
            logger.info(f"Model '{config.name}' registered successfully")
            return True
            
    def unregister_model(self, model_name: str) -> bool:
        """Unregister and cleanup AI model"""        with self._lock:
            if model_name not in self.models:
                logger.warning(f"Model '{model_name}' not found")
                return False
                
            model = self.models[model_name]
            model.unload()
            del self.models[model_name]
            
            logger.info(f"Model '{model_name}' unregistered successfully")
            return True
            
    def load_model(self, model_name: str) -> bool:
        """Load a specific model"""        if model_name not in self.models:
            raise ModelConnectionError(f"Model '{model_name}' not registered")
            
        return self.models[model_name].load()
        
    def unload_model(self, model_name: str) -> bool:
        """Unload a specific model"""        if model_name not in self.models:
            logger.warning(f"Model '{model_name}' not found")
            return False
            
        self.models[model_name].unload()
        return True
        
    def predict(
        self,
        model_name: str,
        input_data: Any,
        use_cache: bool = True,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """Make prediction with specified model"""        if model_name not in self.models:
            raise ModelConnectionError(f"Model '{model_name}' not registered")
            
        model = self.models[model_name]
        
        # Use timeout if specified
        if timeout:
            future = self.model_pool.submit(model.predict, input_data, use_cache, **kwargs)
            try:
                return future.result(timeout=timeout)
            except TimeoutError:
                raise ModelConnectionError(f"Prediction timeout for model '{model_name}'")
        else:
            return model.predict(input_data, use_cache, **kwargs)
            
    async def async_predict(
        self,
        model_name: str,
        input_data: Any,
        use_cache: bool = True,
        **kwargs
    ) -> Any:
        """Asynchronous prediction"""        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.model_pool,
            self.predict,
            model_name,
            input_data,
            use_cache,
            kwargs
        )
        
    def batch_predict(
        self,
        model_name: str,
        input_batch: List[Any],
        use_cache: bool = True,
        max_workers: Optional[int] = None
    ) -> List[Any]:
        """Batch prediction with parallel processing"""        if model_name not in self.models:
            raise ModelConnectionError(f"Model '{model_name}' not registered")
            
        max_workers = max_workers or min(len(input_batch), 4)
        results = [None] * len(input_batch)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self.predict, model_name, input_data, use_cache): i
                for i, input_data in enumerate(input_batch)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Batch prediction failed for item {index}: {e}")
                    results[index] = None
                    
        return results
        
    def get_model_status(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed model status and metrics"""        if model_name not in self.models:
            return None
            
        return self.models[model_name].get_metrics()
        
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""        with self._lock:
            model_statuses = {}
            total_inference_count = 0
            total_error_count = 0
            
            for name, model in self.models.items():
                status = model.get_metrics()
                model_statuses[name] = status
                total_inference_count += status["inference_count"]
                total_error_count += status["error_count"]
                
            loaded_models = sum(
                1 for model in self.models.values()
                if model.status in [ModelStatus.LOADED, ModelStatus.READY]
            )
            
            return {
                "total_models": len(self.models),
                "loaded_models": loaded_models,
                "total_inferences": total_inference_count,
                "total_errors": total_error_count,
                "error_rate": total_error_count / max(total_inference_count, 1) * 100,
                "model_statuses": model_statuses,
                "system_info": {
                    "pytorch_available": PYTORCH_AVAILABLE,
                    "tensorflow_available": TENSORFLOW_AVAILABLE,
                    "cuda_available": PYTORCH_AVAILABLE and torch.cuda.is_available() if PYTORCH_AVAILABLE else False
                }
            }
            
    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage by unloading least used models"""        with self._lock:
            optimization_results = {
                "models_unloaded": [],
                "memory_freed_estimate": 0,
                "optimization_time": 0
            }
            
            start_time = time.perf_counter()
            
            # Sort models by last usage
            sorted_models = sorted(
                self.models.items(),
                key=lambda x: x[1].metrics.last_used
            )
            
            # Unload least recently used models
            for name, model in sorted_models:
                if model.status == ModelStatus.READY and len(optimization_results["models_unloaded"]) < 3:
                    model.unload()
                    optimization_results["models_unloaded"].append(name)
                    optimization_results["memory_freed_estimate"] += 1000  # Rough estimate in MB
                    
            # Force garbage collection
            gc.collect()
            if PYTORCH_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            optimization_results["optimization_time"] = time.perf_counter() - start_time
            
            logger.info(f"Memory optimization completed: {optimization_results}")
            return optimization_results
            
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of AI engine"""        health_status = {
            "status": "healthy",
            "issues": [],
            "recommendations": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Check model availability
            if not self.models:
                health_status["issues"].append("No models registered")
                health_status["status"] = "warning"
                
            # Check for error models
            error_models = [
                name for name, model in self.models.items()
                if model.status == ModelStatus.ERROR
            ]
            if error_models:
                health_status["issues"].append(f"Models in error state: {error_models}")
                health_status["status"] = "degraded"
                
            # Check inference performance
            engine_status = self.get_engine_status()
            if engine_status["error_rate"] > 10:
                health_status["issues"].append(f"High error rate: {engine_status['error_rate']:.1f}%")
                health_status["status"] = "degraded"
                
            # Memory recommendations
            if engine_status["loaded_models"] > self.max_concurrent_models:
                health_status["recommendations"].append("Consider unloading some models to free memory")
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["issues"].append(f"Health check failed: {str(e)}")
            
        return health_status
        
    def shutdown(self):
        """Graceful shutdown of AI engine"""        logger.info("Shutting down AI Engine Manager...")
        
        # Stop cleanup thread
        self._stop_cleanup.set()
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
            
        # Unload all models
        with self._lock:
            for model in self.models.values():
                try:
                    model.unload()
                except Exception as e:
                    logger.error(f"Error unloading model during shutdown: {e}")
                    
        # Shutdown thread pool
        self.model_pool.shutdown(wait=True)
        
        logger.info("AI Engine Manager shutdown completed")


# Global AI engine manager instance
ai_engine = AIEngineManager()


@contextmanager
def ai_model_context(model_name: str, auto_unload: bool = False):
    """Context manager for AI model usage"""    try:
        # Ensure model is loaded
        ai_engine.load_model(model_name)
        yield ai_engine.models[model_name]
    finally:
        if auto_unload:
            ai_engine.unload_model(model_name)


def ai_inference_decorator(
    model_name: str,
    input_key: str = "content",
    cache_results: bool = True,
    timeout: Optional[float] = None
):
    """    Decorator for automatic AI inference
    
    Args:
        model_name: Name of the AI model to use
        input_key: Key in kwargs to use as model input
        cache_results: Whether to cache inference results
        timeout: Inference timeout in seconds
    """    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract input data
            input_data = kwargs.get(input_key)
            if input_data is None:
                raise ValueError(f"Required input key '{input_key}' not found in kwargs")
                
            # Perform inference
            result = ai_engine.predict(
                model_name,
                input_data,
                use_cache=cache_results,
                timeout=timeout
            )
            
            # Add inference result to kwargs
            kwargs[f"{model_name}_result"] = result
            
            # Call original function
            return func(*args, **kwargs)
            
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract input data
            input_data = kwargs.get(input_key)
            if input_data is None:
                raise ValueError(f"Required input key '{input_key}' not found in kwargs")
                
            # Perform async inference
            result = await ai_engine.async_predict(
                model_name,
                input_data,
                use_cache=cache_results
            )
            
            # Add inference result to kwargs
            kwargs[f"{model_name}_result"] = result
            
            # Call original function
            return await func(*args, **kwargs)
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator
