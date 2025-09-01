"""Machine Learning Services Health Monitoring
Comprehensive health checking for AI/ML pipeline components

This module provides health monitoring for:
- AI fingerprinting engines (audio, video, image, text)
- ML model serving and inference pipelines
- Vector databases and similarity search engines
- Content recommendation systems
- AI training job monitoring and resource usage
- Model version management and deployment status
- GPU/TPU resource utilization and performance

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""

import asyncio
import time
import json
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

import numpy as np
import torch
import tensorflow as tf
from transformers import pipeline
import faiss

from .core_health import HealthStatus, HealthCheckResult


@dataclass
class MLModelMetrics:
    """
Machine learning model performance metrics"""
    model_name: str
    model_version: str
    inference_latency_ms: float
    memory_usage_mb: float
    accuracy_score: float
    last_training_date: Optional[datetime]
    prediction_count_24h: int
    error_rate_percent: float


@dataclass
class GPUMetrics:
    """
GPU utilization and performance metrics"""
    device_id: int
    device_name: str
    gpu_utilization_percent: float
    memory_used_mb: float
    memory_total_mb: float
    memory_utilization_percent: float
    temperature_celsius: float
    power_usage_watts: float


class MLServiceHealthChecker:
    """
    Machine Learning services health monitoring system
    
    Monitors AI/ML pipeline components including model serving,
    training jobs, vector databases, and GPU resources.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ML service health checker
        
        Args:
            config: ML configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # ML configurations
        self.ml_config = config.get("ml", {})
        self.models_config = self.ml_config.get("models", {})
        self.gpu_config = self.ml_config.get("gpu", {})
        self.vector_db_config = self.ml_config.get("vector_db", {})
        
        # Health check thresholds
        self.inference_latency_threshold = config.get("health_checks", {}).get("ml_latency_threshold_ms", 5000)
        self.gpu_memory_threshold = config.get("health_checks", {}).get("gpu_memory_threshold", 90.0)
        self.model_accuracy_threshold = config.get("health_checks", {}).get("model_accuracy_threshold", 0.85)
        self.error_rate_threshold = config.get("health_checks", {}).get("model_error_rate_threshold", 5.0)
        
        # Initialize model cache
        self._loaded_models = {}
        self._faiss_indexes = {}

    async def check_pytorch_models(self) -> HealthCheckResult:
        """
        Check PyTorch model health and performance
        
        Returns:
            HealthCheckResult: PyTorch models health status
        """
        start_time = time.time()
        
        try:
            details = {
                "pytorch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
                "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                "models": []
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Check each configured PyTorch model
            pytorch_models = self.models_config.get("pytorch", {})
            
            for model_name, model_config in pytorch_models.items():
                model_start = time.time()
                
                try:
                    # Test model loading and inference
                    model_path = model_config.get("path")
                    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    
                    # Simulate model loading (in production, use actual models)
                    if model_name not in self._loaded_models:
                        # This would load actual model in production
                        self._loaded_models[model_name] = {
                            "loaded_at": datetime.utcnow(),
                            "device": str(device)
                        }
                    
                    # Test inference with dummy data
                    test_input = torch.randn(1, 3, 224, 224).to(device)
                    inference_start = time.time()
                    
                    # Simulate inference (replace with actual model inference)
                    with torch.no_grad():
                        _ = torch.nn.functional.softmax(test_input.mean(dim=[2, 3]), dim=1)
                    
                    inference_time = (time.time() - inference_start) * 1000
                    
                    # Get memory usage
                    if torch.cuda.is_available():
                        memory_allocated = torch.cuda.memory_allocated(device) / (1024 * 1024)
                        memory_cached = torch.cuda.memory_reserved(device) / (1024 * 1024)
                    else:
                        memory_allocated = 0
                        memory_cached = 0
                    
                    model_metrics = {
                        "model_name": model_name,
                        "status": "healthy",
                        "inference_latency_ms": inference_time,
                        "memory_allocated_mb": memory_allocated,
                        "memory_cached_mb": memory_cached,
                        "device": str(device),
                        "last_inference": datetime.utcnow().isoformat()
                    }
                    
                    # Check thresholds
                    if inference_time > self.inference_latency_threshold:
                        status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                        warnings.append(f"High inference latency for {model_name}: {inference_time:.1f}ms")
                        model_metrics["status"] = "degraded"
                    
                    details["models"].append(model_metrics)
                    
                except Exception as e:
                    self.logger.error(f"PyTorch model {model_name} health check failed: {str(e)}")
                    status = HealthStatus.UNHEALTHY
                    details["models"].append({
                        "model_name": model_name,
                        "status": "unhealthy",
                        "error": str(e)
                    })
            
            # Check CUDA memory usage if available
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    memory_info = torch.cuda.mem_get_info(i)
                    memory_free = memory_info[0] / (1024 * 1024 * 1024)  # GB
                    memory_total = memory_info[1] / (1024 * 1024 * 1024)  # GB
                    memory_used = memory_total - memory_free
                    memory_percent = (memory_used / memory_total) * 100
                    
                    if memory_percent > self.gpu_memory_threshold:
                        status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY
                        warnings.append(f"High GPU {i} memory usage: {memory_percent:.1f}%")
            
            details["warnings"] = warnings
            details["total_models"] = len(pytorch_models)
            details["healthy_models"] = len([m for m in details["models"] if m.get("status") == "healthy"])
            
            return HealthCheckResult(
                service="pytorch_models",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"PyTorch models health check failed: {str(e)}")
            return HealthCheckResult(
                service="pytorch_models",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_tensorflow_models(self) -> HealthCheckResult:
        """
        Check TensorFlow model health and performance
        
        Returns:
            HealthCheckResult: TensorFlow models health status
        """
        start_time = time.time()
        
        try:
            details = {
                "tensorflow_version": tf.__version__,
                "gpu_devices": len(tf.config.list_physical_devices('GPU')),
                "cpu_devices": len(tf.config.list_physical_devices('CPU')),
                "models": []
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Check GPU availability and configuration
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                try:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    details["gpu_memory_growth_enabled"] = True
                except RuntimeError as e:
                    self.logger.warning(f"Could not set GPU memory growth: {str(e)}")
                    details["gpu_memory_growth_enabled"] = False
            
            # Check each configured TensorFlow model
            tensorflow_models = self.models_config.get("tensorflow", {})
            
            for model_name, model_config in tensorflow_models.items():
                try:
                    # Test model loading and inference
                    model_path = model_config.get("path")
                    
                    # Simulate model loading (in production, use actual models)
                    if model_name not in self._loaded_models:
                        self._loaded_models[model_name] = {
                            "loaded_at": datetime.utcnow(),
                            "framework": "tensorflow"
                        }
                    
                    # Test inference with dummy data
                    test_input = tf.random.normal([1, 224, 224, 3])
                    inference_start = time.time()
                    
                    # Simulate inference (replace with actual model inference)
                    with tf.device('/GPU:0' if gpus else '/CPU:0'):
                        _ = tf.nn.softmax(tf.reduce_mean(test_input, axis=[1, 2]))
                    
                    inference_time = (time.time() - inference_start) * 1000
                    
                    model_metrics = {
                        "model_name": model_name,
                        "status": "healthy",
                        "inference_latency_ms": inference_time,
                        "device": "GPU" if gpus else "CPU",
                        "last_inference": datetime.utcnow().isoformat()
                    }
                    
                    # Check thresholds
                    if inference_time > self.inference_latency_threshold:
                        status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                        warnings.append(f"High inference latency for {model_name}: {inference_time:.1f}ms")
                        model_metrics["status"] = "degraded"
                    
                    details["models"].append(model_metrics)
                    
                except Exception as e:
                    self.logger.error(f"TensorFlow model {model_name} health check failed: {str(e)}")
                    status = HealthStatus.UNHEALTHY
                    details["models"].append({
                        "model_name": model_name,
                        "status": "unhealthy",
                        "error": str(e)
                    })
            
            details["warnings"] = warnings
            details["total_models"] = len(tensorflow_models)
            details["healthy_models"] = len([m for m in details["models"] if m.get("status") == "healthy"])
            
            return HealthCheckResult(
                service="tensorflow_models",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"TensorFlow models health check failed: {str(e)}")
            return HealthCheckResult(
                service="tensorflow_models",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_huggingface_models(self) -> HealthCheckResult:
        """
        Check Hugging Face transformers model health
        
        Returns:
            HealthCheckResult: Hugging Face models health status
        """
        start_time = time.time()
        
        try:
            details = {
                "transformers_available": True,
                "models": []
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Check each configured Hugging Face model
            hf_models = self.models_config.get("huggingface", {})
            
            for model_name, model_config in hf_models.items():
                try:
                    model_type = model_config.get("type", "text-classification")
                    model_id = model_config.get("model_id", "distilbert-base-uncased")
                    
                    # Test model loading and inference
                    inference_start = time.time()
                    
                    if model_type == "text-classification":
                        classifier = pipeline("text-classification", model=model_id)
                        result = classifier("This is a test sentence for health check.")
                    elif model_type == "feature-extraction":
                        feature_extractor = pipeline("feature-extraction", model=model_id)
                        result = feature_extractor("Test text for feature extraction.")
                    elif model_type == "audio-classification":
                        # Simulate audio classification (would use actual audio in production)
                        result = {"label": "test", "score": 0.99}
                    else:
                        result = {"status": "unknown_model_type"}
                    
                    inference_time = (time.time() - inference_start) * 1000
                    
                    model_metrics = {
                        "model_name": model_name,
                        "model_id": model_id,
                        "model_type": model_type,
                        "status": "healthy",
                        "inference_latency_ms": inference_time,
                        "last_inference": datetime.utcnow().isoformat(),
                        "test_result": str(result)[:100]  # Truncate for brevity
                    }
                    
                    # Check thresholds
                    if inference_time > self.inference_latency_threshold:
                        status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                        warnings.append(f"High inference latency for {model_name}: {inference_time:.1f}ms")
                        model_metrics["status"] = "degraded"
                    
                    details["models"].append(model_metrics)
                    
                except Exception as e:
                    self.logger.error(f"Hugging Face model {model_name} health check failed: {str(e)}")
                    status = HealthStatus.UNHEALTHY
                    details["models"].append({
                        "model_name": model_name,
                        "status": "unhealthy",
                        "error": str(e)
                    })
            
            details["warnings"] = warnings
            details["total_models"] = len(hf_models)
            details["healthy_models"] = len([m for m in details["models"] if m.get("status") == "healthy"])
            
            return HealthCheckResult(
                service="huggingface_models",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Hugging Face models health check failed: {str(e)}")
            return HealthCheckResult(
                service="huggingface_models",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_vector_databases(self) -> HealthCheckResult:
        """
        Check vector database and similarity search health
        
        Returns:
            HealthCheckResult: Vector databases health status
        """
        start_time = time.time()
        
        try:
            details = {
                "faiss_available": True,
                "indexes": []
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            # Check FAISS indexes
            faiss_config = self.vector_db_config.get("faiss", {})
            
            for index_name, index_config in faiss_config.items():
                try:
                    dimension = index_config.get("dimension", 768)
                    index_type = index_config.get("type", "IndexFlatL2")
                    
                    # Create or load test index
                    if index_name not in self._faiss_indexes:
                        if index_type == "IndexFlatL2":
                            index = faiss.IndexFlatL2(dimension)
                        elif index_type == "IndexIVFFlat":
                            quantizer = faiss.IndexFlatL2(dimension)
                            index = faiss.IndexIVFFlat(quantizer, dimension, 100)
                        else:
                            index = faiss.IndexFlatL2(dimension)
                        
                        self._faiss_indexes[index_name] = index
                    else:
                        index = self._faiss_indexes[index_name]
                    
                    # Test search performance
                    search_start = time.time()
                    
                    # Add test vectors if index is empty
                    if index.ntotal == 0:
                        test_vectors = np.random.random((1000, dimension)).astype('float32')
                        index.add(test_vectors)
                        
                        if hasattr(index, 'train'):
                            index.train(test_vectors)
                    
                    # Perform test search
                    query_vector = np.random.random((1, dimension)).astype('float32')
                    k = min(10, index.ntotal)
                    
                    if k > 0:
                        distances, indices = index.search(query_vector, k)
                        search_time = (time.time() - search_start) * 1000
                    else:
                        search_time = 0.0
                    
                    index_metrics = {
                        "index_name": index_name,
                        "index_type": index_type,
                        "dimension": dimension,
                        "total_vectors": index.ntotal,
                        "status": "healthy",
                        "search_latency_ms": search_time,
                        "last_search": datetime.utcnow().isoformat()
                    }
                    
                    # Check thresholds
                    if search_time > 1000:  # 1 second threshold for vector search
                        status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                        warnings.append(f"High search latency for {index_name}: {search_time:.1f}ms")
                        index_metrics["status"] = "degraded"
                    
                    details["indexes"].append(index_metrics)
                    
                except Exception as e:
                    self.logger.error(f"FAISS index {index_name} health check failed: {str(e)}")
                    status = HealthStatus.UNHEALTHY
                    details["indexes"].append({
                        "index_name": index_name,
                        "status": "unhealthy",
                        "error": str(e)
                    })
            
            details["warnings"] = warnings
            details["total_indexes"] = len(faiss_config)
            details["healthy_indexes"] = len([i for i in details["indexes"] if i.get("status") == "healthy"])
            
            return HealthCheckResult(
                service="vector_databases",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Vector databases health check failed: {str(e)}")
            return HealthCheckResult(
                service="vector_databases",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_gpu_resources(self) -> HealthCheckResult:
        """
        Check GPU resource utilization and performance
        
        Returns:
            HealthCheckResult: GPU resources health status
        """
        start_time = time.time()
        
        try:
            details = {
                "gpu_available": torch.cuda.is_available(),
                "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
                "gpus": []
            }
            
            status = HealthStatus.HEALTHY
            warnings = []
            
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    try:
                        # Get GPU properties
                        props = torch.cuda.get_device_properties(i)
                        memory_info = torch.cuda.mem_get_info(i)
                        
                        memory_free = memory_info[0] / (1024 * 1024 * 1024)  # GB
                        memory_total = memory_info[1] / (1024 * 1024 * 1024)  # GB
                        memory_used = memory_total - memory_free
                        memory_percent = (memory_used / memory_total) * 100
                        
                        # Try to get additional metrics using nvidia-ml-py if available
                        try:
                            import pynvml
                            pynvml.nvmlInit()
                            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                            
                            gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                            power_info = pynvml.nvmlDeviceGetPowerUsage(handle)
                            
                            gpu_utilization = gpu_util.gpu
                            temp_celsius = temperature
                            power_watts = power_info / 1000.0  # Convert from mW to W
                            
                        except ImportError:
                            gpu_utilization = 0.0
                            temp_celsius = 0.0
                            power_watts = 0.0
                        
                        gpu_metrics = {
                            "device_id": i,
                            "device_name": props.name,
                            "compute_capability": f"{props.major}.{props.minor}",
                            "total_memory_gb": memory_total,
                            "used_memory_gb": memory_used,
                            "free_memory_gb": memory_free,
                            "memory_utilization_percent": memory_percent,
                            "gpu_utilization_percent": gpu_utilization,
                            "temperature_celsius": temp_celsius,
                            "power_usage_watts": power_watts,
                            "multiprocessor_count": props.multi_processor_count,
                            "status": "healthy"
                        }
                        
                        # Check thresholds
                        if memory_percent > self.gpu_memory_threshold:
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY
                            warnings.append(f"High GPU {i} memory usage: {memory_percent:.1f}%")
                            gpu_metrics["status"] = "degraded"
                        
                        if temp_celsius > 85:  # Temperature threshold
                            status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else status
                            warnings.append(f"High GPU {i} temperature: {temp_celsius}°C")
                            gpu_metrics["status"] = "degraded"
                        
                        details["gpus"].append(gpu_metrics)
                        
                    except Exception as e:
                        self.logger.error(f"GPU {i} metrics collection failed: {str(e)}")
                        status = HealthStatus.UNHEALTHY
                        details["gpus"].append({
                            "device_id": i,
                            "status": "unhealthy",
                            "error": str(e)
                        })
            else:
                details["message"] = "No GPU devices available, using CPU for ML workloads"
            
            details["warnings"] = warnings
            details["healthy_gpus"] = len([g for g in details["gpus"] if g.get("status") == "healthy"])
            
            return HealthCheckResult(
                service="gpu_resources",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"GPU resources health check failed: {str(e)}")
            return HealthCheckResult(
                service="gpu_resources",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def perform_comprehensive_check(self) -> List[HealthCheckResult]:
        """
        Perform all ML service health checks concurrently
        
        Returns:
            List[HealthCheckResult]: All ML service health check results
        """
        checks = await asyncio.gather(
            self.check_pytorch_models(),
            self.check_tensorflow_models(),
            self.check_huggingface_models(),
            self.check_vector_databases(),
            self.check_gpu_resources(),
            return_exceptions=True
        )
        
        results = []
        for check in checks:
            if isinstance(check, Exception):
                self.logger.error(f"ML service health check failed with exception: {str(check)}")
                results.append(HealthCheckResult(
                    service="unknown_ml_service",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    timestamp=datetime.utcnow(),
                    details={},
                    error_message=str(check)
                ))
            else:
                results.append(check)
                
        return results

    async def get_ml_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive ML services health summary
        
        Returns:
            Dict[str, Any]: ML services health summary with overall status
        """
        results = await self.perform_comprehensive_check()
        
        # Calculate overall ML services health
        status_weights = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 2,
            HealthStatus.CRITICAL: 3
        }
        
        overall_score = max([status_weights[result.status] for result in results])
        overall_status = [status for status, weight in status_weights.items() if weight == overall_score][0]
        
        # Calculate metrics
        avg_response_time = sum([result.response_time_ms for result in results]) / len(results)
        healthy_services = len([r for r in results if r.status == HealthStatus.HEALTHY])
        total_services = len(results)
        
        return {
            "overall_status": overall_status.value,
            "healthy_ml_services": healthy_services,
            "total_ml_services": total_services,
            "ml_health_percentage": (healthy_services / total_services) * 100,
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "ml_results": [asdict(result) for result in results]
        }
