"""Local AI Inference Engine
===========================

High-performance local AI inference engine supporting multiple
model types and optimization techniques for edge deployment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import json
import numpy as np
import pickle
import hashlib
import os
from pathlib import Path
import psutil
import GPUtil

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Supported AI model types."""
    TEXT_GENERATION = "text_generation"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    SPEECH_RECOGNITION = "speech_recognition"
    TEXT_TO_SPEECH = "text_to_speech"
    EMBEDDING = "embedding"
    RECOMMENDATION = "recommendation"
    STYLE_TRANSFER = "style_transfer"
    CONTENT_MODERATION = "content_moderation"


class InferenceBackend(str, Enum):
    """Inference backend options."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    COREML = "coreml"
    CPU = "cpu"
    CUSTOM = "custom"


class ModelFormat(str, Enum):
    """Model file formats."""
    PYTORCH_PT = "pytorch_pt"
    TENSORFLOW_PB = "tensorflow_pb"
    ONNX_MODEL = "onnx"
    TENSORRT_ENGINE = "tensorrt"
    PICKLE = "pickle"
    HUGGINGFACE = "huggingface"


class OptimizationLevel(str, Enum):
    """Model optimization levels."""
    NONE = "none"
    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    ULTRA = "ultra"


@dataclass
class ModelConfig:
    """Model configuration."""
    model_id: str
    model_type: ModelType
    model_format: ModelFormat
    backend: InferenceBackend
    model_path: str
    input_shape: Optional[Tuple[int, ...]]
    output_shape: Optional[Tuple[int, ...]]
    preprocessing: Optional[Dict[str, Any]]
    postprocessing: Optional[Dict[str, Any]]
    optimization_level: OptimizationLevel
    device: str  # cpu, cuda:0, etc.
    batch_size: int
    max_sequence_length: Optional[int]
    metadata: Dict[str, Any]


@dataclass
class InferenceRequest:
    """Inference request."""
    request_id: str
    model_id: str
    input_data: Any
    preprocessing_params: Optional[Dict[str, Any]]
    priority: int  # 1-10, higher is more urgent
    timeout_seconds: int
    callback_url: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class InferenceResult:
    """Inference result."""
    request_id: str
    model_id: str
    output_data: Any
    confidence_scores: Optional[List[float]]
    processing_time_ms: float
    queue_time_ms: float
    model_load_time_ms: float
    preprocessing_time_ms: float
    inference_time_ms: float
    postprocessing_time_ms: float
    memory_usage_mb: float
    gpu_utilization: Optional[float]
    status: str
    error_message: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    completed_at: datetime


@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics."""
    model_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_inference_time_ms: float
    average_queue_time_ms: float
    average_memory_usage_mb: float
    peak_memory_usage_mb: float
    throughput_requests_per_second: float
    last_used: datetime
    load_count: int
    error_rate: float
    uptime_seconds: float


class LocalInferenceEngine:
    """High-performance local AI inference engine."""
    
    def __init__(
        self,
        model_cache_dir -> None: str = "./models",
        max_models_in_memory -> None: int = 5,
        max_concurrent_requests -> None: int = 10,
        enable_gpu -> None: bool = True,
        optimization_enabled -> None: bool = True,
        metrics_enabled -> None: bool = True
    ) -> None:
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(exist_ok=True)
        
        self.max_models_in_memory = max_models_in_memory
        self.max_concurrent_requests = max_concurrent_requests
        self.enable_gpu = enable_gpu
        self.optimization_enabled = optimization_enabled
        self.metrics_enabled = metrics_enabled
        
        # Model management
        self.loaded_models: Dict[str, Any] = {}
        self.model_configs: Dict[str, ModelConfig] = {}
        self.model_last_used: Dict[str, datetime] = {}
        self.model_lock = threading.RLock()
        
        # Request management
        self.request_queue = asyncio.PriorityQueue()
        self.active_requests: Dict[str, InferenceRequest] = {}
        self.request_semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # Performance metrics
        self.performance_metrics: Dict[str, ModelPerformanceMetrics] = {}
        self.total_requests = 0
        self.total_inference_time = 0.0
        self.engine_start_time = datetime.now()
        
        # Worker management
        self.workers_running = False
        self.worker_tasks: List[asyncio.Task] = []
        
        # Hardware monitoring
        self.cpu_count = psutil.cpu_count()
        self.total_memory = psutil.virtual_memory().total
        self.gpu_available = self._check_gpu_availability()
        
        logger.info(f"Local inference engine initialized")
        logger.info(f"CPU cores: {self.cpu_count}, Memory: {self.total_memory // 1024**3}GB")
        if self.gpu_available:
            logger.info(f"GPU available: {self._get_gpu_info()}")
    
    async def start(self) -> None:
        """Start the inference engine."""
        self.workers_running = True
        
        # Start worker tasks
        for i in range(self.max_concurrent_requests):
            task = asyncio.create_task(self._inference_worker(f"worker_{i}"))
            self.worker_tasks.append(task)
        
        # Start monitoring task
        if self.metrics_enabled:
            monitor_task = asyncio.create_task(self._performance_monitor())
            self.worker_tasks.append(monitor_task)
        
        logger.info("Inference engine started")
    
    async def stop(self) -> None:
        """Stop the inference engine."""
        self.workers_running = False
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Unload all models
        with self.model_lock:
            self.loaded_models.clear()
            self.model_configs.clear()
        
        logger.info("Inference engine stopped")
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            return torch.cuda.is_available() and self.enable_gpu
        except ImportError:
            try:
                import tensorflow as tf
                return len(tf.config.list_physical_devices('GPU')) > 0 and self.enable_gpu
            except ImportError:
                return False
    
    def _get_gpu_info(self) -> str:
        """Get GPU information."""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return f"{gpu.name} ({gpu.memoryTotal}MB)"
        except:
            pass
        return "Unknown GPU"
    
    async def register_model(
        self,
        model_config: ModelConfig,
        preload: bool = False
    ) -> bool:
        """Register a model for inference."""
        try:
            # Validate model file exists
            if not os.path.exists(model_config.model_path):
                raise FileNotFoundError(f"Model file not found: {model_config.model_path}")
            
            # Store model configuration
            self.model_configs[model_config.model_id] = model_config
            
            # Initialize performance metrics
            self.performance_metrics[model_config.model_id] = ModelPerformanceMetrics(
                model_id=model_config.model_id,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_inference_time_ms=0.0,
                average_queue_time_ms=0.0,
                average_memory_usage_mb=0.0,
                peak_memory_usage_mb=0.0,
                throughput_requests_per_second=0.0,
                last_used=datetime.now(),
                load_count=0,
                error_rate=0.0,
                uptime_seconds=0.0
            )
            
            # Preload model if requested
            if preload:
                await self._load_model(model_config.model_id)
            
            logger.info(f"Model registered: {model_config.model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {model_config.model_id}: {e}")
            return False
    
    async def unregister_model(self, model_id: str) -> bool:
        """Unregister a model."""
        try:
            # Unload model from memory
            with self.model_lock:
                if model_id in self.loaded_models:
                    del self.loaded_models[model_id]
                
                if model_id in self.model_configs:
                    del self.model_configs[model_id]
                
                if model_id in self.model_last_used:
                    del self.model_last_used[model_id]
            
            logger.info(f"Model unregistered: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister model {model_id}: {e}")
            return False
    
    async def infer(
        self,
        model_id: str,
        input_data: Any,
        priority: int = 5,
        timeout_seconds: int = 30,
        preprocessing_params: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InferenceResult:
        """Perform inference on input data."""
        request_id = self._generate_request_id()
        
        request = InferenceRequest(
            request_id=request_id,
            model_id=model_id,
            input_data=input_data,
            preprocessing_params=preprocessing_params,
            priority=priority,
            timeout_seconds=timeout_seconds,
            callback_url=None,
            metadata=metadata or {},
            created_at=datetime.now()
        )
        
        # Queue request
        await self.request_queue.put((-priority, time.time(), request))
        self.active_requests[request_id] = request
        
        # Wait for result with timeout
        start_time = time.time()
        while request_id in self.active_requests:
            if time.time() - start_time > timeout_seconds:
                # Remove from active requests
                if request_id in self.active_requests:
                    del self.active_requests[request_id]
                
                return InferenceResult(
                    request_id=request_id,
                    model_id=model_id,
                    output_data=None,
                    confidence_scores=None,
                    processing_time_ms=0.0,
                    queue_time_ms=(time.time() - start_time) * 1000,
                    model_load_time_ms=0.0,
                    preprocessing_time_ms=0.0,
                    inference_time_ms=0.0,
                    postprocessing_time_ms=0.0,
                    memory_usage_mb=0.0,
                    gpu_utilization=None,
                    status="timeout",
                    error_message="Request timeout",
                    metadata=metadata or {},
                    created_at=request.created_at,
                    completed_at=datetime.now()
                )
            
            await asyncio.sleep(0.1)
        
        # This should not be reached if everything works correctly
        raise RuntimeError("Request processing failed unexpectedly")
    
    async def _inference_worker(self, worker_name -> None: str) -> None:
        """Worker task for processing inference requests."""
        logger.info(f"Inference worker {worker_name} started")
        
        while self.workers_running:
            try:
                # Get request from queue
                try:
                    priority, timestamp, request = await asyncio.wait_for(
                        self.request_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process request with semaphore
                async with self.request_semaphore:
                    result = await self._process_request(request)
                    
                    # Store result and remove from active requests
                    if request.request_id in self.active_requests:
                        # In a real implementation, you'd store the result
                        # and the client would retrieve it
                        del self.active_requests[request.request_id]
                
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1.0)
        
        logger.info(f"Inference worker {worker_name} stopped")
    
    async def _process_request(self, request: InferenceRequest) -> InferenceResult:
        """Process a single inference request."""
        start_time = time.time()
        queue_time = start_time - request.created_at.timestamp()
        
        try:
            # Load model if not in memory
            model_load_start = time.time()
            model = await self._load_model(request.model_id)
            model_load_time = (time.time() - model_load_start) * 1000
            
            # Preprocessing
            preprocessing_start = time.time()
            processed_input = await self._preprocess_input(
                request.model_id, 
                request.input_data, 
                request.preprocessing_params
            )
            preprocessing_time = (time.time() - preprocessing_start) * 1000
            
            # Inference
            inference_start = time.time()
            raw_output = await self._run_inference(request.model_id, processed_input)
            inference_time = (time.time() - inference_start) * 1000
            
            # Postprocessing
            postprocessing_start = time.time()
            final_output = await self._postprocess_output(request.model_id, raw_output)
            postprocessing_time = (time.time() - postprocessing_start) * 1000
            
            # Calculate metrics
            total_time = (time.time() - start_time) * 1000
            memory_usage = self._get_memory_usage()
            gpu_utilization = self._get_gpu_utilization()
            
            # Update performance metrics
            await self._update_performance_metrics(
                request.model_id,
                inference_time,
                queue_time * 1000,
                memory_usage,
                True
            )
            
            result = InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                output_data=final_output,
                confidence_scores=self._extract_confidence_scores(final_output),
                processing_time_ms=total_time,
                queue_time_ms=queue_time * 1000,
                model_load_time_ms=model_load_time,
                preprocessing_time_ms=preprocessing_time,
                inference_time_ms=inference_time,
                postprocessing_time_ms=postprocessing_time,
                memory_usage_mb=memory_usage,
                gpu_utilization=gpu_utilization,
                status="success",
                error_message=None,
                metadata=request.metadata,
                created_at=request.created_at,
                completed_at=datetime.now()
            )
            
            return result
            
        except Exception as e:
            # Update error metrics
            await self._update_performance_metrics(
                request.model_id,
                0.0,
                queue_time * 1000,
                0.0,
                False
            )
            
            error_result = InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                output_data=None,
                confidence_scores=None,
                processing_time_ms=(time.time() - start_time) * 1000,
                queue_time_ms=queue_time * 1000,
                model_load_time_ms=0.0,
                preprocessing_time_ms=0.0,
                inference_time_ms=0.0,
                postprocessing_time_ms=0.0,
                memory_usage_mb=0.0,
                gpu_utilization=None,
                status="error",
                error_message=str(e),
                metadata=request.metadata,
                created_at=request.created_at,
                completed_at=datetime.now()
            )
            
            logger.error(f"Inference failed for request {request.request_id}: {e}")
            return error_result
    
    async def _load_model(self, model_id: str) -> Any:
        """Load model into memory."""
        with self.model_lock:
            # Check if model is already loaded
            if model_id in self.loaded_models:
                self.model_last_used[model_id] = datetime.now()
                return self.loaded_models[model_id]
            
            # Check if we need to unload old models
            if len(self.loaded_models) >= self.max_models_in_memory:
                await self._evict_least_used_model()
            
            # Load model
            config = self.model_configs[model_id]
            model = await self._load_model_from_file(config)
            
            # Optimize model if enabled
            if self.optimization_enabled:
                model = await self._optimize_model(model, config)
            
            # Store model
            self.loaded_models[model_id] = model
            self.model_last_used[model_id] = datetime.now()
            
            # Update metrics
            if model_id in self.performance_metrics:
                self.performance_metrics[model_id].load_count += 1
            
            logger.info(f"Model loaded: {model_id}")
            return model
    
    async def _load_model_from_file(self, config: ModelConfig) -> Any:
        """Load model from file based on format."""
        if config.model_format == ModelFormat.PYTORCH_PT:
            return await self._load_pytorch_model(config)
        elif config.model_format == ModelFormat.TENSORFLOW_PB:
            return await self._load_tensorflow_model(config)
        elif config.model_format == ModelFormat.ONNX_MODEL:
            return await self._load_onnx_model(config)
        elif config.model_format == ModelFormat.PICKLE:
            return await self._load_pickle_model(config)
        elif config.model_format == ModelFormat.HUGGINGFACE:
            return await self._load_huggingface_model(config)
        else:
            raise ValueError(f"Unsupported model format: {config.model_format}")
    
    async def _load_pytorch_model(self, config: ModelConfig) -> Any:
        """Load PyTorch model."""
        try:
            import torch
            device = torch.device(config.device)
            model = torch.load(config.model_path, map_location=device)
            model.eval()
            return model
        except ImportError:
            raise RuntimeError("PyTorch not available")
    
    async def _load_tensorflow_model(self, config: ModelConfig) -> Any:
        """Load TensorFlow model."""
        try:
            import tensorflow as tf
            model = tf.saved_model.load(config.model_path)
            return model
        except ImportError:
            raise RuntimeError("TensorFlow not available")
    
    async def _load_onnx_model(self, config: ModelConfig) -> Any:
        """Load ONNX model."""
        try:
            import onnxruntime as ort
            
            providers = ['CPUExecutionProvider']
            if config.device.startswith('cuda') and self.gpu_available:
                providers.insert(0, 'CUDAExecutionProvider')
            
            session = ort.InferenceSession(config.model_path, providers=providers)
            return session
        except ImportError:
            raise RuntimeError("ONNX Runtime not available")
    
    async def _load_pickle_model(self, config: ModelConfig) -> Any:
        """Load pickled model."""
        with open(config.model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    
    async def _load_huggingface_model(self, config: ModelConfig) -> Any:
        """Load HuggingFace model."""
        try:
            from transformers import AutoModel, AutoTokenizer
            
            model = AutoModel.from_pretrained(config.model_path)
            tokenizer = AutoTokenizer.from_pretrained(config.model_path)
            
            return {"model": model, "tokenizer": tokenizer}
        except ImportError:
            raise RuntimeError("Transformers library not available")
    
    async def _optimize_model(self, model: Any, config: ModelConfig) -> Any:
        """Optimize model for inference."""
        if config.optimization_level == OptimizationLevel.NONE:
            return model
        
        # Model-specific optimizations would go here
        # For now, return model as-is
        return model
    
    async def _evict_least_used_model(self) -> None:
        """Evict the least recently used model."""
        if not self.loaded_models:
            return
        
        # Find least recently used model
        lru_model_id = min(
            self.model_last_used.keys(),
            key=lambda x: self.model_last_used[x]
        )
        
        # Remove from memory
        del self.loaded_models[lru_model_id]
        del self.model_last_used[lru_model_id]
        
        logger.info(f"Evicted model from memory: {lru_model_id}")
    
    async def _preprocess_input(
        self,
        model_id: str,
        input_data: Any,
        params: Optional[Dict[str, Any]]
    ) -> Any:
        """Preprocess input data."""
        config = self.model_configs[model_id]
        
        # Apply model-specific preprocessing
        if config.preprocessing:
            # Custom preprocessing logic would go here
            pass
        
        # Apply request-specific preprocessing
        if params:
            # Apply parameters
            pass
        
        return input_data
    
    async def _run_inference(self, model_id: str, input_data: Any) -> Any:
        """Run inference on preprocessed input."""
        model = self.loaded_models[model_id]
        config = self.model_configs[model_id]
        
        if config.backend == InferenceBackend.PYTORCH:
            return await self._run_pytorch_inference(model, input_data)
        elif config.backend == InferenceBackend.TENSORFLOW:
            return await self._run_tensorflow_inference(model, input_data)
        elif config.backend == InferenceBackend.ONNX:
            return await self._run_onnx_inference(model, input_data)
        else:
            # Generic inference
            if hasattr(model, 'predict'):
                return model.predict(input_data)
            elif hasattr(model, '__call__'):
                return model(input_data)
            else:
                raise RuntimeError(f"Don't know how to run inference with {config.backend}")
    
    async def _run_pytorch_inference(self, model: Any, input_data: Any) -> Any:
        """Run PyTorch inference."""
        try:
            import torch
            with torch.no_grad():
                if isinstance(input_data, np.ndarray):
                    input_tensor = torch.from_numpy(input_data)
                else:
                    input_tensor = torch.tensor(input_data)
                
                output = model(input_tensor)
                return output.cpu().numpy() if hasattr(output, 'cpu') else output
        except ImportError:
            raise RuntimeError("PyTorch not available")
    
    async def _run_tensorflow_inference(self, model: Any, input_data: Any) -> Any:
        """Run TensorFlow inference."""
        try:
            import tensorflow as tf
            if isinstance(input_data, np.ndarray):
                input_tensor = tf.constant(input_data)
            else:
                input_tensor = tf.constant(input_data)
            
            output = model(input_tensor)
            return output.numpy() if hasattr(output, 'numpy') else output
        except ImportError:
            raise RuntimeError("TensorFlow not available")
    
    async def _run_onnx_inference(self, session: Any, input_data: Any) -> Any:
        """Run ONNX inference."""
        try:
            input_name = session.get_inputs()[0].name
            output = session.run(None, {input_name: input_data})
            return output[0] if len(output) == 1 else output
        except Exception as e:
            raise RuntimeError(f"ONNX inference failed: {e}")
    
    async def _postprocess_output(self, model_id: str, raw_output: Any) -> Any:
        """Postprocess model output."""
        config = self.model_configs[model_id]
        
        # Apply model-specific postprocessing
        if config.postprocessing:
            # Custom postprocessing logic would go here
            pass
        
        return raw_output
    
    def _extract_confidence_scores(self, output: Any) -> Optional[List[float]]:
        """Extract confidence scores from output."""
        if isinstance(output, np.ndarray):
            if output.ndim == 1:
                return output.tolist()
            elif output.ndim == 2 and output.shape[0] == 1:
                return output[0].tolist()
        
        return None
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def _get_gpu_utilization(self) -> Optional[float]:
        """Get GPU utilization percentage."""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
        except:
            pass
        return None
    
    async def _update_performance_metrics(
        self,
        model_id -> None: str,
        inference_time -> None: float,
        queue_time -> None: float,
        memory_usage -> None: float,
        success -> None: bool
    ) -> None:
        """Update performance metrics for a model."""
        if model_id not in self.performance_metrics:
            return
        
        metrics = self.performance_metrics[model_id]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # Update averages
        total_requests = metrics.total_requests
        metrics.average_inference_time_ms = (
            (metrics.average_inference_time_ms * (total_requests - 1) + inference_time) / total_requests
        )
        metrics.average_queue_time_ms = (
            (metrics.average_queue_time_ms * (total_requests - 1) + queue_time) / total_requests
        )
        metrics.average_memory_usage_mb = (
            (metrics.average_memory_usage_mb * (total_requests - 1) + memory_usage) / total_requests
        )
        
        if memory_usage > metrics.peak_memory_usage_mb:
            metrics.peak_memory_usage_mb = memory_usage
        
        metrics.error_rate = metrics.failed_requests / total_requests
        metrics.last_used = datetime.now()
        
        # Calculate throughput (requests per second over last minute)
        uptime = (datetime.now() - self.engine_start_time).total_seconds()
        metrics.uptime_seconds = uptime
        
        if uptime > 0:
            metrics.throughput_requests_per_second = total_requests / uptime
    
    async def _performance_monitor(self) -> None:
        """Monitor performance and log metrics."""
        while self.workers_running:
            try:
                # Log system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                logger.info(
                    f"System metrics - CPU: {cpu_percent}%, "
                    f"Memory: {memory.percent}% ({memory.used // 1024**3}GB/{memory.total // 1024**3}GB)"
                )
                
                # Log model metrics
                for model_id, metrics in self.performance_metrics.items():
                    if metrics.total_requests > 0:
                        logger.info(
                            f"Model {model_id} - "
                            f"Requests: {metrics.total_requests}, "
                            f"Success rate: {(1 - metrics.error_rate) * 100:.1f}%, "
                            f"Avg inference: {metrics.average_inference_time_ms:.1f}ms, "
                            f"Throughput: {metrics.throughput_requests_per_second:.2f} req/s"
                        )
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return hashlib.md5(
            f"{time.time()}_{self.total_requests}".encode()
        ).hexdigest()[:16]
    
    def get_model_list(self) -> List[str]:
        """Get list of registered models."""
        return list(self.model_configs.keys())
    
    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models."""
        return list(self.loaded_models.keys())
    
    def get_model_metrics(self, model_id: str) -> Optional[ModelPerformanceMetrics]:
        """Get performance metrics for a specific model."""
        return self.performance_metrics.get(model_id)
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get overall engine status."""
        return {
            "status": "running" if self.workers_running else "stopped",
            "uptime_seconds": (datetime.now() - self.engine_start_time).total_seconds(),
            "total_models_registered": len(self.model_configs),
            "models_in_memory": len(self.loaded_models),
            "max_models_in_memory": self.max_models_in_memory,
            "active_requests": len(self.active_requests),
            "max_concurrent_requests": self.max_concurrent_requests,
            "total_requests_processed": self.total_requests,
            "gpu_available": self.gpu_available,
            "cpu_cores": self.cpu_count,
            "total_memory_gb": self.total_memory // 1024**3,
            "current_memory_usage_mb": self._get_memory_usage(),
            "current_gpu_utilization": self._get_gpu_utilization()
        }


# Utility functions
async def create_inference_engine(
    model_cache_dir: str = "./models",
    enable_gpu: bool = True,
    max_models: int = 5
) -> LocalInferenceEngine:
    """Create and start inference engine."""
    engine = LocalInferenceEngine(
        model_cache_dir=model_cache_dir,
        enable_gpu=enable_gpu,
        max_models_in_memory=max_models
    )
    await engine.start()
    return engine


async def quick_inference(
    engine: LocalInferenceEngine,
    model_id: str,
    input_data: Any,
    timeout: int = 30
) -> Any:
    """Quick inference utility."""
    result = await engine.infer(
        model_id=model_id,
        input_data=input_data,
        timeout_seconds=timeout
    )
    
    if result.status == "success":
        return result.output_data
    else:
        raise RuntimeError(f"Inference failed: {result.error_message}")


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        engine = await create_inference_engine()
        
        try:
            # Register a mock model
            config = ModelConfig(
                model_id="test_model",
                model_type=ModelType.TEXT_GENERATION,
                model_format=ModelFormat.PICKLE,
                backend=InferenceBackend.CPU,
                model_path="./test_model.pkl",
                input_shape=None,
                output_shape=None,
                preprocessing=None,
                postprocessing=None,
                optimization_level=OptimizationLevel.BASIC,
                device="cpu",
                batch_size=1,
                max_sequence_length=512,
                metadata={}
            )
            
            # For demonstration, create a dummy model file
            import pickle
            dummy_model = lambda x: f"Processed: {x}"
            with open("./test_model.pkl", "wb") as f:
                pickle.dump(dummy_model, f)
            
            success = await engine.register_model(config, preload=True)
            print(f"Model registered: {success}")
            
            # Perform inference
            result = await engine.infer(
                model_id="test_model",
                input_data="Hello World",
                priority=7
            )
            
            print(f"Inference result: {result.output_data}")
            print(f"Processing time: {result.processing_time_ms:.2f}ms")
            
            # Get engine status
            status = engine.get_engine_status()
            print(f"Engine status: {status}")
            
        finally:
            await engine.stop()
            # Clean up test file
            if os.path.exists("./test_model.pkl"):
                os.remove("./test_model.pkl")
    
    asyncio.run(main())