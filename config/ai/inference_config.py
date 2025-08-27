"""
Inference Configuration for IA-Influencer Agent Platform
========================================================

Professional AI Model Inference and Deployment configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass, field
import os


class InferenceBackend(str, Enum):
    """Supported inference backends."""
    
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    TRITON = "triton"
    TORCHSCRIPT = "torchscript"
    TFLITE = "tflite"


class BatchingStrategy(str, Enum):
    """Batching strategies for inference optimization."""
    
    DYNAMIC = "dynamic"
    STATIC = "static"
    ADAPTIVE = "adaptive"
    NO_BATCHING = "no_batching"


class CachingStrategy(str, Enum):
    """Caching strategies for inference results."""
    
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"
    HYBRID = "hybrid"
    NO_CACHE = "no_cache"


@dataclass
class InferenceEndpoint:
    """Configuration for inference endpoint."""
    
    name: str
    model_path: str
    backend: InferenceBackend
    device: str = "auto"
    max_batch_size: int = 32
    timeout_seconds: int = 30
    max_sequence_length: Optional[int] = None
    preprocessing_pipeline: List[str] = field(default_factory=list)
    postprocessing_pipeline: List[str] = field(default_factory=list)
    caching_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceOptimization:
    """Optimization settings for inference."""
    
    quantization_enabled: bool = False
    quantization_method: str = "dynamic"  # dynamic, static, qat
    pruning_enabled: bool = False
    pruning_sparsity: float = 0.1
    knowledge_distillation: bool = False
    model_compilation: bool = False
    tensor_parallelism: bool = False
    pipeline_parallelism: bool = False
    mixed_precision: bool = True
    graph_optimization: bool = True


class InferenceConfig(BaseSettings):
    """
    Professional Inference Configuration for IA-Influencer Agent Platform.
    
    Manages model inference, deployment, optimization, and serving configurations
    for production-ready AI model deployment.
    """
    
    # Core Inference Configuration
    INFERENCE_BACKEND: InferenceBackend = InferenceBackend.PYTORCH
    DEFAULT_DEVICE: str = "auto"
    MODEL_SERVING_HOST: str = "0.0.0.0"
    MODEL_SERVING_PORT: int = 8080
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    DEFAULT_BATCH_SIZE: int = 16
    MAX_BATCH_SIZE: int = 64
    BATCHING_STRATEGY: BatchingStrategy = BatchingStrategy.DYNAMIC
    BATCH_TIMEOUT_MS: int = 50
    
    # Memory and Resource Management
    MAX_MEMORY_USAGE_GB: float = 8.0
    MODEL_CACHE_SIZE: int = 5  # Number of models to keep in memory
    WORKER_PROCESSES: int = 2
    THREADS_PER_WORKER: int = 4
    
    # Caching Configuration
    CACHING_STRATEGY: CachingStrategy = CachingStrategy.REDIS
    CACHE_TTL_DEFAULT: int = 3600  # seconds
    CACHE_MAX_SIZE_MB: int = 1024
    CACHE_COMPRESSION: bool = True
    
    # Model Optimization
    QUANTIZATION_ENABLED: bool = False
    MIXED_PRECISION_ENABLED: bool = True
    MODEL_COMPILATION_ENABLED: bool = False
    GRAPH_OPTIMIZATION_ENABLED: bool = True
    
    # Monitoring and Logging
    METRICS_ENABLED: bool = True
    DETAILED_LOGGING: bool = True
    PERFORMANCE_PROFILING: bool = False
    HEALTH_CHECK_INTERVAL: int = 60  # seconds
    
    # Model-Specific Configurations
    NLP_INFERENCE_CONFIG: Dict[str, Any] = {
        "max_sequence_length": 512,
        "batch_size": 32,
        "truncation": True,
        "padding": True,
        "return_attention_mask": True,
        "return_token_type_ids": False,
    }
    
    VISION_INFERENCE_CONFIG: Dict[str, Any] = {
        "input_size": (224, 224),
        "batch_size": 64,
        "normalize": True,
        "center_crop": True,
        "resize_mode": "bilinear",
    }
    
    AUDIO_INFERENCE_CONFIG: Dict[str, Any] = {
        "sample_rate": 22050,
        "batch_size": 16,
        "n_fft": 2048,
        "hop_length": 512,
        "chunk_duration": 10.0,  # seconds
    }
    
    # API Configuration
    API_KEY_REQUIRED: bool = False
    RATE_LIMITING_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 1000
    CORS_ENABLED: bool = True
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Load Balancing
    LOAD_BALANCING_ENABLED: bool = False
    LOAD_BALANCER_STRATEGY: str = "round_robin"  # round_robin, least_connections, weighted
    
    class Config:
        env_prefix = "INFERENCE_"
        case_sensitive = False
        env_file = ".env"
    
    def get_inference_endpoint(self, model_name: str, task_type: str) -> InferenceEndpoint:
        """Get inference endpoint configuration for a specific model and task."""
        
        endpoint_configs = {
            "text_classification": InferenceEndpoint(
                name=f"{model_name}_text_classifier",
                model_path=f"/models/{model_name}",
                backend=self.INFERENCE_BACKEND,
                device=self.DEFAULT_DEVICE,
                max_batch_size=self.NLP_INFERENCE_CONFIG["batch_size"],
                timeout_seconds=self.REQUEST_TIMEOUT,
                max_sequence_length=self.NLP_INFERENCE_CONFIG["max_sequence_length"],
                preprocessing_pipeline=["tokenize", "truncate", "pad"],
                postprocessing_pipeline=["softmax", "argmax"],
                caching_enabled=True,
                cache_ttl=self.CACHE_TTL_DEFAULT,
                custom_config=self.NLP_INFERENCE_CONFIG
            ),
            
            "image_classification": InferenceEndpoint(
                name=f"{model_name}_image_classifier",
                model_path=f"/models/{model_name}",
                backend=self.INFERENCE_BACKEND,
                device=self.DEFAULT_DEVICE,
                max_batch_size=self.VISION_INFERENCE_CONFIG["batch_size"],
                timeout_seconds=self.REQUEST_TIMEOUT,
                preprocessing_pipeline=["resize", "normalize", "to_tensor"],
                postprocessing_pipeline=["softmax", "top_k"],
                caching_enabled=True,
                cache_ttl=self.CACHE_TTL_DEFAULT,
                custom_config=self.VISION_INFERENCE_CONFIG
            ),
            
            "audio_classification": InferenceEndpoint(
                name=f"{model_name}_audio_classifier",
                model_path=f"/models/{model_name}",
                backend=self.INFERENCE_BACKEND,
                device=self.DEFAULT_DEVICE,
                max_batch_size=self.AUDIO_INFERENCE_CONFIG["batch_size"],
                timeout_seconds=self.REQUEST_TIMEOUT * 2,  # Audio processing takes longer
                preprocessing_pipeline=["load_audio", "extract_features", "normalize"],
                postprocessing_pipeline=["softmax", "aggregate_predictions"],
                caching_enabled=True,
                cache_ttl=self.CACHE_TTL_DEFAULT,
                custom_config=self.AUDIO_INFERENCE_CONFIG
            ),
            
            "similarity_matching": InferenceEndpoint(
                name=f"{model_name}_similarity",
                model_path=f"/models/{model_name}",
                backend=self.INFERENCE_BACKEND,
                device=self.DEFAULT_DEVICE,
                max_batch_size=self.DEFAULT_BATCH_SIZE,
                timeout_seconds=self.REQUEST_TIMEOUT,
                preprocessing_pipeline=["preprocess_input"],
                postprocessing_pipeline=["normalize_embeddings", "compute_similarity"],
                caching_enabled=True,
                cache_ttl=self.CACHE_TTL_DEFAULT * 2,  # Cache embeddings longer
            ),
            
            "content_generation": InferenceEndpoint(
                name=f"{model_name}_generator",
                model_path=f"/models/{model_name}",
                backend=self.INFERENCE_BACKEND,
                device=self.DEFAULT_DEVICE,
                max_batch_size=4,  # Generation typically uses smaller batches
                timeout_seconds=self.REQUEST_TIMEOUT * 3,  # Generation takes longer
                preprocessing_pipeline=["tokenize", "create_prompt"],
                postprocessing_pipeline=["decode", "filter_output"],
                caching_enabled=False,  # Don't cache generated content
            ),
        }
        
        return endpoint_configs.get(task_type, self._get_default_endpoint(model_name, task_type))
    
    def _get_default_endpoint(self, model_name: str, task_type: str) -> InferenceEndpoint:
        """Get default inference endpoint configuration."""
        return InferenceEndpoint(
            name=f"{model_name}_default",
            model_path=f"/models/{model_name}",
            backend=self.INFERENCE_BACKEND,
            device=self.DEFAULT_DEVICE,
            max_batch_size=self.DEFAULT_BATCH_SIZE,
            timeout_seconds=self.REQUEST_TIMEOUT,
        )
    
    def get_optimization_config(self, model_type: str) -> InferenceOptimization:
        """Get optimization configuration for specific model type."""
        optimizations = {
            "lightweight": InferenceOptimization(
                quantization_enabled=True,
                quantization_method="dynamic",
                pruning_enabled=True,
                pruning_sparsity=0.2,
                model_compilation=True,
                mixed_precision=True,
                graph_optimization=True,
            ),
            
            "balanced": InferenceOptimization(
                quantization_enabled=self.QUANTIZATION_ENABLED,
                mixed_precision=self.MIXED_PRECISION_ENABLED,
                model_compilation=self.MODEL_COMPILATION_ENABLED,
                graph_optimization=self.GRAPH_OPTIMIZATION_ENABLED,
            ),
            
            "high_accuracy": InferenceOptimization(
                quantization_enabled=False,
                pruning_enabled=False,
                mixed_precision=False,
                model_compilation=False,
                graph_optimization=True,
            ),
        }
        
        return optimizations.get(model_type, optimizations["balanced"])
    
    def get_serving_config(self) -> Dict[str, Any]:
        """Get model serving configuration."""
        return {
            "server": {
                "host": self.MODEL_SERVING_HOST,
                "port": self.MODEL_SERVING_PORT,
                "workers": self.WORKER_PROCESSES,
                "threads_per_worker": self.THREADS_PER_WORKER,
            },
            "performance": {
                "max_concurrent_requests": self.MAX_CONCURRENT_REQUESTS,
                "request_timeout": self.REQUEST_TIMEOUT,
                "default_batch_size": self.DEFAULT_BATCH_SIZE,
                "max_batch_size": self.MAX_BATCH_SIZE,
                "batching_strategy": self.BATCHING_STRATEGY,
                "batch_timeout_ms": self.BATCH_TIMEOUT_MS,
            },
            "resources": {
                "max_memory_gb": self.MAX_MEMORY_USAGE_GB,
                "model_cache_size": self.MODEL_CACHE_SIZE,
                "device": self.DEFAULT_DEVICE,
            },
            "api": {
                "api_key_required": self.API_KEY_REQUIRED,
                "rate_limiting": self.RATE_LIMITING_ENABLED,
                "rate_limit_per_minute": self.RATE_LIMIT_PER_MINUTE,
                "cors_enabled": self.CORS_ENABLED,
                "allowed_origins": self.ALLOWED_ORIGINS,
            }
        }
    
    def get_caching_config(self) -> Dict[str, Any]:
        """Get caching configuration."""
        return {
            "strategy": self.CACHING_STRATEGY,
            "default_ttl": self.CACHE_TTL_DEFAULT,
            "max_size_mb": self.CACHE_MAX_SIZE_MB,
            "compression": self.CACHE_COMPRESSION,
            "backends": {
                "memory": {
                    "enabled": self.CACHING_STRATEGY in [CachingStrategy.MEMORY, CachingStrategy.HYBRID],
                    "max_size": self.CACHE_MAX_SIZE_MB // 2,
                },
                "redis": {
                    "enabled": self.CACHING_STRATEGY in [CachingStrategy.REDIS, CachingStrategy.HYBRID],
                    "host": "localhost",
                    "port": 6379,
                    "db": 1,
                },
                "disk": {
                    "enabled": self.CACHING_STRATEGY in [CachingStrategy.DISK, CachingStrategy.HYBRID],
                    "path": "/tmp/inference_cache",
                    "max_size": self.CACHE_MAX_SIZE_MB,
                }
            }
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring and observability configuration."""
        return {
            "metrics": {
                "enabled": self.METRICS_ENABLED,
                "detailed_logging": self.DETAILED_LOGGING,
                "performance_profiling": self.PERFORMANCE_PROFILING,
                "health_check_interval": self.HEALTH_CHECK_INTERVAL,
            },
            "prometheus": {
                "enabled": True,
                "port": 9090,
                "path": "/metrics",
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "file": "/logs/inference.log",
                "rotation": "daily",
            },
            "tracing": {
                "enabled": True,
                "service_name": "ia-influencer-inference",
                "sampling_rate": 0.1,
            }
        }
    
    def get_load_balancing_config(self) -> Dict[str, Any]:
        """Get load balancing configuration."""
        return {
            "enabled": self.LOAD_BALANCING_ENABLED,
            "strategy": self.LOAD_BALANCER_STRATEGY,
            "health_checks": {
                "enabled": True,
                "interval": 30,
                "timeout": 5,
                "healthy_threshold": 2,
                "unhealthy_threshold": 3,
            },
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 5,
                "reset_timeout": 60,
                "half_open_max_calls": 3,
            }
        }
    
    def get_batching_config(self) -> Dict[str, Any]:
        """Get request batching configuration."""
        return {
            "strategy": self.BATCHING_STRATEGY,
            "default_batch_size": self.DEFAULT_BATCH_SIZE,
            "max_batch_size": self.MAX_BATCH_SIZE,
            "batch_timeout_ms": self.BATCH_TIMEOUT_MS,
            "dynamic_batching": {
                "enabled": self.BATCHING_STRATEGY == BatchingStrategy.DYNAMIC,
                "preferred_batch_size": [16, 32, 64],
                "max_queue_delay_ms": 100,
            },
            "adaptive_batching": {
                "enabled": self.BATCHING_STRATEGY == BatchingStrategy.ADAPTIVE,
                "target_latency_ms": 50,
                "adaptation_rate": 0.1,
            }
        }
    
    def estimate_inference_latency(self, task_type: str, batch_size: int = 1) -> Dict[str, float]:
        """Estimate inference latency for different task types."""
        # Base latency estimates in milliseconds
        base_latencies = {
            "text_classification": 10,
            "image_classification": 15,
            "audio_classification": 50,
            "similarity_matching": 8,
            "content_generation": 200,
            "object_detection": 25,
            "speech_recognition": 100,
        }
        
        base_latency = base_latencies.get(task_type, 20)
        
        # Batch size scaling (sub-linear due to GPU parallelization)
        batch_factor = batch_size ** 0.7 if batch_size > 1 else 1
        
        # Device-specific multipliers
        device_multipliers = {
            "cpu": 3.0,
            "cuda": 1.0,
            "mps": 1.5,
        }
        
        device = self.DEFAULT_DEVICE.lower()
        device_multiplier = device_multipliers.get(device, 1.0)
        
        estimated_latency = base_latency * batch_factor * device_multiplier
        
        return {
            "inference_latency_ms": estimated_latency,
            "preprocessing_ms": estimated_latency * 0.2,
            "postprocessing_ms": estimated_latency * 0.1,
            "total_latency_ms": estimated_latency * 1.3,
        }


# Global inference configuration instance
inference_config = InferenceConfig()
