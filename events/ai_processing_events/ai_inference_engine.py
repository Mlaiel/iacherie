"""AI Inference Engine

Enterprise-grade AI inference engine for the IA Influencer Agent platform.
Provides high-performance, scalable inference capabilities for various AI models
including real-time, batch, and streaming inference with intelligent load balancing.

This module processes AI inference following the business logic:
Model Request → Resource Allocation → Inference Execution → Result Processing → Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de)
is strictly prohibited and may result in legal action.
"""

import logging
import asyncio
import threading
import time
import uuid
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import psutil
import gc

# Core imports
from ..core.base_event_handler import BaseEventHandler
from ..core.event_priority import EventPriority
from ..core.event_status import EventStatus

logger = logging.getLogger(__name__)

class InferenceType(Enum):
    """AI inference type enumeration"""
    
    REAL_TIME = "real_time"
    BATCH = "batch"
    STREAMING = "streaming"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"

class ModelFramework(Enum):
    """ML framework enumeration"""
    
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    TRANSFORMERS = "transformers"
    ONNX = "onnx"
    TENSORRT = "tensorrt"
    CUSTOM = "custom"

class InferenceStatus(Enum):
    """Inference execution status"""
    
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    RUNNING = "running"
    POSTPROCESSING = "postprocessing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class ResourceType(Enum):
    """Compute resource types"""
    
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    MEMORY = "memory"
    STORAGE = "storage"

@dataclass
class ModelSpec:
    """AI model specification"""
    
    model_id: str
    model_name: str
    framework: ModelFramework
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    resource_requirements: Dict[ResourceType, int]
    supported_batch_sizes: List[int] = field(default_factory=lambda: [1, 8, 16, 32])
    max_sequence_length: Optional[int] = None
    warm_up_time: float = 2.0  # seconds
    average_inference_time: float = 0.1  # seconds
    memory_footprint: int = 512  # MB
    model_path: Optional[str] = None
    config_file: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def estimate_memory_usage(self, batch_size: int) -> int:
        """Estimate memory usage for given batch size"""
        base_memory = self.memory_footprint
        batch_factor = batch_size / self.supported_batch_sizes[0] if self.supported_batch_sizes else batch_size
        return int(base_memory * (1 + batch_factor * 0.1))
    
    def estimate_inference_time(self, batch_size: int) -> float:
        """Estimate inference time for given batch size"""
        base_time = self.average_inference_time
        batch_factor = batch_size / self.supported_batch_sizes[0] if self.supported_batch_sizes else batch_size
        return base_time * (1 + batch_factor * 0.05)

@dataclass
class InferenceRequest:
    """AI inference request"""
    
    request_id: str
    model_id: str
    inference_type: InferenceType
    input_data: Any
    batch_size: int = 1
    priority: EventPriority = EventPriority.MEDIUM
    timeout: float = 30.0
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)
    postprocessing_config: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_priority_score(self) -> int:
        """Get numeric priority score for queue ordering"""
        priority_scores = {
            EventPriority.CRITICAL: 4,
            EventPriority.HIGH: 3,
            EventPriority.MEDIUM: 2,
            EventPriority.LOW: 1
        }
        return priority_scores.get(self.priority, 2)
    
    def is_expired(self) -> bool:
        """Check if request has expired"""
        return (datetime.now() - self.created_at).total_seconds() > self.timeout

@dataclass
class InferenceResult:
    """AI inference result"""
    
    request_id: str
    model_id: str
    status: InferenceStatus
    predictions: Any = None
    confidence_scores: Optional[List[float]] = None
    processing_time: float = 0.0
    queue_time: float = 0.0
    preprocessing_time: float = 0.0
    inference_time: float = 0.0
    postprocessing_time: float = 0.0
    memory_used: int = 0  # MB
    gpu_utilization: float = 0.0  # %
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'request_id': self.request_id,
            'model_id': self.model_id,
            'status': self.status.value,
            'predictions': self.predictions,
            'confidence_scores': self.confidence_scores,
            'processing_time': self.processing_time,
            'queue_time': self.queue_time,
            'preprocessing_time': self.preprocessing_time,
            'inference_time': self.inference_time,
            'postprocessing_time': self.postprocessing_time,
            'memory_used': self.memory_used,
            'gpu_utilization': self.gpu_utilization,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'completed_at': self.completed_at.isoformat()
        }

class ModelInstance(ABC):
    """Abstract AI model instance"""
    
    def __init__(self, spec -> None: ModelSpec) -> None:
        self.spec = spec
        self.model = None
        self.is_loaded = False
        self.load_time = None
        self.last_used = None
        self.inference_count = 0
        self.total_inference_time = 0.0
        self.error_count = 0
        self.lock = threading.RLock()
    
    @abstractmethod
    async def load(self) -> bool:
        """Load the model"""
        pass
    
    @abstractmethod
    async def unload(self) -> bool:
        """Unload the model"""
        pass
    
    @abstractmethod
    async def predict(self, input_data: Any, batch_size: int = 1) -> Any:
        """Run model inference"""
        pass
    
    @abstractmethod
    async def preprocess(self, raw_data: Any, config: Dict[str, Any]) -> Any:
        """Preprocess input data"""
        pass
    
    @abstractmethod
    async def postprocess(self, predictions: Any, config: Dict[str, Any]) -> Any:
        """Postprocess predictions"""
        pass
    
    async def warm_up(self) -> bool:
        """Warm up the model with dummy data"""
        try:
            if not self.is_loaded:
                return False
            
            # Create dummy input based on model spec
            dummy_input = self._create_dummy_input()
            if dummy_input is not None:
                await self.predict(dummy_input)
                logger.info(f"Model {self.spec.model_id} warmed up successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Model warm-up failed for {self.spec.model_id}: {str(e)}")
            return False
    
    def _create_dummy_input(self) -> Any:
        """Create dummy input for warm-up"""
        # This should be implemented based on model input schema
        # For now, return None to indicate no warm-up needed
        return None
    
    def update_performance_stats(self, inference_time -> None: float, success -> None: bool = True) -> None:
        """Update model performance statistics"""
        with self.lock:
            self.inference_count += 1
            self.total_inference_time += inference_time
            self.last_used = datetime.now()
            
            if not success:
                self.error_count += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get model performance statistics"""
        with self.lock:
            avg_inference_time = (self.total_inference_time / max(self.inference_count, 1))
            error_rate = self.error_count / max(self.inference_count, 1)
            
            return {
                'model_id': self.spec.model_id,
                'is_loaded': self.is_loaded,
                'load_time': self.load_time.isoformat() if self.load_time else None,
                'last_used': self.last_used.isoformat() if self.last_used else None,
                'inference_count': self.inference_count,
                'average_inference_time': avg_inference_time,
                'total_inference_time': self.total_inference_time,
                'error_count': self.error_count,
                'error_rate': error_rate
            }

class DummyModelInstance(ModelInstance):
    """Dummy model instance for testing and demonstration"""
    
    async def load(self) -> bool:
        """Load the dummy model"""
        try:
            await asyncio.sleep(self.spec.warm_up_time)  # Simulate loading time
            self.model = f"dummy_model_{self.spec.model_id}"
            self.is_loaded = True
            self.load_time = datetime.now()
            logger.info(f"Dummy model {self.spec.model_id} loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load dummy model {self.spec.model_id}: {str(e)}")
            return False
    
    async def unload(self) -> bool:
        """Unload the dummy model"""
        try:
            self.model = None
            self.is_loaded = False
            logger.info(f"Dummy model {self.spec.model_id} unloaded")
            return True
        except Exception as e:
            logger.error(f"Failed to unload dummy model {self.spec.model_id}: {str(e)}")
            return False
    
    async def predict(self, input_data: Any, batch_size: int = 1) -> Any:
        """Run dummy model inference"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        # Simulate inference time
        inference_time = self.spec.estimate_inference_time(batch_size)
        await asyncio.sleep(inference_time)
        
        # Generate dummy predictions
        if batch_size == 1:
            predictions = {
                'classification': np.random.rand(),
                'confidence': np.random.uniform(0.7, 0.95),
                'features': np.random.rand(10).tolist()
            }
        else:
            predictions = {
                'classifications': np.random.rand(batch_size).tolist(),
                'confidences': np.random.uniform(0.7, 0.95, batch_size).tolist(),
                'features': np.random.rand(batch_size, 10).tolist()
            }
        
        return predictions
    
    async def preprocess(self, raw_data: Any, config: Dict[str, Any]) -> Any:
        """Preprocess input data (dummy implementation)"""
        # Simulate preprocessing time
        await asyncio.sleep(0.01)
        
        return {
            'processed_data': raw_data,
            'preprocessing_applied': list(config.keys()) if config else []
        }
    
    async def postprocess(self, predictions: Any, config: Dict[str, Any]) -> Any:
        """Postprocess predictions (dummy implementation)"""
        # Simulate postprocessing time
        await asyncio.sleep(0.01)
        
        return {
            'final_predictions': predictions,
            'postprocessing_applied': list(config.keys()) if config else []
        }

class ResourceManager:
    """Manages compute resources for inference"""
    
    def __init__(self) -> None:
        self.available_resources: Dict[ResourceType, int] = {
            ResourceType.CPU: psutil.cpu_count(),
            ResourceType.GPU: 0,  # Will be detected if available
            ResourceType.MEMORY: int(psutil.virtual_memory().total / (1024 * 1024)),  # MB
            ResourceType.STORAGE: 1000000  # MB (dummy value)
        }
        
        self.allocated_resources: Dict[ResourceType, int] = {
            ResourceType.CPU: 0,
            ResourceType.GPU: 0,
            ResourceType.MEMORY: 0,
            ResourceType.STORAGE: 0
        }
        
        self.resource_lock = threading.RLock()
        
        # Try to detect GPU
        self._detect_gpu_resources()
    
    def _detect_gpu_resources(self) -> None:
        """Detect available GPU resources"""
        try:
            # Try to detect NVIDIA GPUs
            import pynvml
            pynvml.nvmlInit()
            gpu_count = pynvml.nvmlDeviceGetCount()
            self.available_resources[ResourceType.GPU] = gpu_count
            logger.info(f"Detected {gpu_count} GPU(s)")
        except:
            # GPU detection failed, assume no GPU
            logger.info("No GPU detected or NVIDIA-ML not available")
    
    def can_allocate(self, requirements: Dict[ResourceType, int]) -> bool:
        """Check if resources can be allocated"""
        with self.resource_lock:
            for resource_type, required in requirements.items():
                available = (self.available_resources.get(resource_type, 0) - 
                           self.allocated_resources.get(resource_type, 0))
                if available < required:
                    return False
            return True
    
    def allocate_resources(self, requirements: Dict[ResourceType, int]) -> bool:
        """Allocate resources"""
        with self.resource_lock:
            if not self.can_allocate(requirements):
                return False
            
            for resource_type, required in requirements.items():
                self.allocated_resources[resource_type] += required
            
            return True
    
    def deallocate_resources(self, requirements -> None: Dict[ResourceType, int]) -> None:
        """Deallocate resources"""
        with self.resource_lock:
            for resource_type, required in requirements.items():
                self.allocated_resources[resource_type] = max(
                    0, self.allocated_resources[resource_type] - required
                )
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Get current resource utilization"""
        with self.resource_lock:
            utilization = {}
            for resource_type in ResourceType:
                available = self.available_resources.get(resource_type, 0)
                allocated = self.allocated_resources.get(resource_type, 0)
                utilization[resource_type.value] = (allocated / max(available, 1)) * 100
            
            return utilization

class InferenceQueue:
    """Priority queue for inference requests"""
    
    def __init__(self, maxsize -> None: int = 10000) -> None:
        self.queue = queue.PriorityQueue(maxsize=maxsize)
        self.request_map: Dict[str, InferenceRequest] = {}
        self.lock = threading.RLock()
    
    async def put(self, request: InferenceRequest) -> bool:
        """Add request to queue"""
        try:
            # Priority queue uses tuple (priority, timestamp, request)
            # Lower priority number = higher priority
            priority_score = -request.get_priority_score()  # Negative for reverse ordering
            timestamp = time.time()
            
            with self.lock:
                self.queue.put((priority_score, timestamp, request.request_id))
                self.request_map[request.request_id] = request
            
            return True
        except queue.Full:
            logger.error("Inference queue is full")
            return False
        except Exception as e:
            logger.error(f"Failed to add request to queue: {str(e)}")
            return False
    
    async def get(self, timeout: float = 1.0) -> Optional[InferenceRequest]:
        """Get next request from queue"""
        try:
            priority, timestamp, request_id = self.queue.get(timeout=timeout)
            
            with self.lock:
                request = self.request_map.pop(request_id, None)
            
            return request
        except queue.Empty:
            return None
        except Exception as e:
            logger.error(f"Failed to get request from queue: {str(e)}")
            return None
    
    def remove(self, request_id: str) -> bool:
        """Remove request from queue"""
        with self.lock:
            if request_id in self.request_map:
                del self.request_map[request_id]
                return True
            return False
    
    def size(self) -> int:
        """Get queue size"""
        return self.queue.qsize()
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            total_requests = len(self.request_map)
            priority_counts = {}
            
            for request in self.request_map.values():
                priority = request.priority.value
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            return {
                'total_requests': total_requests,
                'priority_counts': priority_counts,
                'queue_size': self.queue.qsize()
            }

class AIInferenceEngine(BaseEventHandler):
    """
    Enterprise AI Inference Engine
    
    Provides high-performance, scalable inference capabilities for various AI models
    including real-time, batch, and streaming inference with intelligent load balancing
    for the IA Influencer Agent platform.
    """
    
    def __init__(self, 
                 max_workers -> None: int = 8,
                 max_queue_size -> None: int = 10000,
                 max_models -> None: int = 20) -> None:
        super().__init__()
        
        self.max_workers = max_workers
        self.max_models = max_models
        
        # Core components
        self.resource_manager = ResourceManager()
        self.inference_queue = InferenceQueue(maxsize=max_queue_size)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Model management
        self.model_specs: Dict[str, ModelSpec] = {}
        self.model_instances: Dict[str, ModelInstance] = {}
        self.model_load_order: List[str] = []  # LRU order
        
        # Performance tracking
        self.total_requests = 0
        self.completed_requests = 0
        self.failed_requests = 0
        self.average_queue_time = 0.0
        self.average_processing_time = 0.0
        
        # Runtime state
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []
        self.lock = threading.RLock()
        
        logger.info(f"AI Inference Engine initialized with {max_workers} workers")
    
    async def start_engine(self) -> None:
        """Start the inference engine"""
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            task = asyncio.create_task(self._worker_loop(f"worker_{i}"))
            self.worker_tasks.append(task)
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._cleanup_expired_requests())
        asyncio.create_task(self._optimize_model_allocation())
        
        logger.info("AI Inference Engine started")
    
    async def stop_engine(self) -> None:
        """Stop the inference engine"""
        self.is_running = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Unload all models
        for model_id in list(self.model_instances.keys()):
            await self.unload_model(model_id)
        
        logger.info("AI Inference Engine stopped")
    
    async def register_model(self, spec: ModelSpec) -> bool:
        """Register a new model specification"""
        try:
            with self.lock:
                self.model_specs[spec.model_id] = spec
            
            logger.info(f"Model {spec.model_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {spec.model_id}: {str(e)}")
            return False
    
    async def load_model(self, model_id: str) -> bool:
        """Load a model for inference"""
        try:
            spec = self.model_specs.get(model_id)
            if not spec:
                logger.error(f"Model {model_id} not registered")
                return False
            
            # Check if model is already loaded
            if model_id in self.model_instances:
                logger.info(f"Model {model_id} already loaded")
                return True
            
            # Check resource availability
            if not self.resource_manager.can_allocate(spec.resource_requirements):
                logger.warning(f"Insufficient resources to load model {model_id}")
                
                # Try to free up resources by unloading LRU models
                await self._free_resources_for_model(spec)
                
                if not self.resource_manager.can_allocate(spec.resource_requirements):
                    logger.error(f"Cannot allocate resources for model {model_id}")
                    return False
            
            # Create model instance (using dummy implementation for now)
            model_instance = DummyModelInstance(spec)
            
            # Load the model
            success = await model_instance.load()
            if success:
                # Allocate resources
                self.resource_manager.allocate_resources(spec.resource_requirements)
                
                # Store model instance
                with self.lock:
                    self.model_instances[model_id] = model_instance
                    self.model_load_order.append(model_id)
                
                # Warm up the model
                await model_instance.warm_up()
                
                logger.info(f"Model {model_id} loaded and ready for inference")
                return True
            else:
                logger.error(f"Failed to load model {model_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {str(e)}")
            return False
    
    async def unload_model(self, model_id: str) -> bool:
        """Unload a model"""
        try:
            with self.lock:
                model_instance = self.model_instances.get(model_id)
                if not model_instance:
                    logger.warning(f"Model {model_id} not loaded")
                    return False
                
                # Unload the model
                success = await model_instance.unload()
                if success:
                    # Deallocate resources
                    spec = model_instance.spec
                    self.resource_manager.deallocate_resources(spec.resource_requirements)
                    
                    # Remove from tracking
                    del self.model_instances[model_id]
                    if model_id in self.model_load_order:
                        self.model_load_order.remove(model_id)
                    
                    logger.info(f"Model {model_id} unloaded successfully")
                    return True
                else:
                    logger.error(f"Failed to unload model {model_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error unloading model {model_id}: {str(e)}")
            return False
    
    async def submit_inference_request(self, request: InferenceRequest) -> str:
        """Submit an inference request"""
        try:
            # Validate request
            if not self._validate_request(request):
                raise ValueError("Invalid inference request")
            
            # Check if model is loaded
            if request.model_id not in self.model_instances:
                # Try to load the model
                success = await self.load_model(request.model_id)
                if not success:
                    raise RuntimeError(f"Failed to load model {request.model_id}")
            
            # Add to queue
            success = await self.inference_queue.put(request)
            if success:
                self.total_requests += 1
                logger.debug(f"Inference request {request.request_id} queued")
                return request.request_id
            else:
                raise RuntimeError("Failed to queue inference request")
                
        except Exception as e:
            logger.error(f"Failed to submit inference request: {str(e)}")
            raise
    
    def _validate_request(self, request: InferenceRequest) -> bool:
        """Validate inference request"""
        try:
            # Check if model is registered
            if request.model_id not in self.model_specs:
                logger.error(f"Model {request.model_id} not registered")
                return False
            
            # Check input data
            if request.input_data is None:
                logger.error("Input data is required")
                return False
            
            # Check batch size
            spec = self.model_specs[request.model_id]
            if (spec.supported_batch_sizes and 
                request.batch_size not in spec.supported_batch_sizes):
                logger.warning(f"Unsupported batch size {request.batch_size} for model {request.model_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Request validation error: {str(e)}")
            return False
    
    async def _worker_loop(self, worker_id -> None: str) -> None:
        """Main worker loop for processing inference requests"""
        logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get next request from queue
                request = await self.inference_queue.get(timeout=1.0)
                if request is None:
                    continue
                
                # Check if request has expired
                if request.is_expired():
                    logger.warning(f"Request {request.request_id} expired")
                    continue
                
                # Process the request
                result = await self._process_inference_request(request)
                
                # Execute callback if provided
                if request.callback:
                    try:
                        await request.callback(result)
                    except Exception as e:
                        logger.error(f"Callback error for request {request.request_id}: {str(e)}")
                
                # Update statistics
                if result.status == InferenceStatus.COMPLETED:
                    self.completed_requests += 1
                else:
                    self.failed_requests += 1
                
                self._update_performance_metrics(result)
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                await asyncio.sleep(1.0)
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _process_inference_request(self, request: InferenceRequest) -> InferenceResult:
        """Process a single inference request"""
        start_time = time.time()
        queue_time = start_time - request.created_at.timestamp()
        
        result = InferenceResult(
            request_id=request.request_id,
            model_id=request.model_id,
            status=InferenceStatus.RUNNING,
            queue_time=queue_time
        )
        
        try:
            # Get model instance
            model_instance = self.model_instances.get(request.model_id)
            if not model_instance or not model_instance.is_loaded:
                result.status = InferenceStatus.FAILED
                result.error_message = f"Model {request.model_id} not available"
                return result
            
            # Update model usage order
            self._update_model_usage(request.model_id)
            
            # Preprocessing
            result.status = InferenceStatus.PREPROCESSING
            preprocess_start = time.time()
            
            processed_input = await model_instance.preprocess(
                request.input_data, 
                request.preprocessing_config
            )
            
            result.preprocessing_time = time.time() - preprocess_start
            
            # Inference
            result.status = InferenceStatus.RUNNING
            inference_start = time.time()
            
            predictions = await model_instance.predict(
                processed_input,
                request.batch_size
            )
            
            result.inference_time = time.time() - inference_start
            
            # Postprocessing
            result.status = InferenceStatus.POSTPROCESSING
            postprocess_start = time.time()
            
            final_predictions = await model_instance.postprocess(
                predictions,
                request.postprocessing_config
            )
            
            result.postprocessing_time = time.time() - postprocess_start
            
            # Complete result
            result.status = InferenceStatus.COMPLETED
            result.predictions = final_predictions
            result.processing_time = time.time() - start_time
            
            # Extract confidence scores if available
            if isinstance(final_predictions, dict):
                if 'confidence' in final_predictions:
                    result.confidence_scores = [final_predictions['confidence']]
                elif 'confidences' in final_predictions:
                    result.confidence_scores = final_predictions['confidences']
            
            # Update model performance stats
            model_instance.update_performance_stats(result.inference_time, success=True)
            
            logger.debug(f"Inference completed for request {request.request_id}")
            
        except Exception as e:
            result.status = InferenceStatus.FAILED
            result.error_message = str(e)
            result.processing_time = time.time() - start_time
            
            # Update model performance stats
            model_instance = self.model_instances.get(request.model_id)
            if model_instance:
                model_instance.update_performance_stats(result.processing_time, success=False)
            
            logger.error(f"Inference failed for request {request.request_id}: {str(e)}")
        
        return result
    
    def _update_model_usage(self, model_id -> None: str) -> None:
        """Update model usage order for LRU tracking"""
        with self.lock:
            if model_id in self.model_load_order:
                self.model_load_order.remove(model_id)
                self.model_load_order.append(model_id)
    
    def _update_performance_metrics(self, result -> None: InferenceResult) -> None:
        """Update engine performance metrics"""
        # Update average queue time
        if self.total_requests > 0:
            alpha = 0.1  # Exponential moving average factor
            self.average_queue_time = (alpha * result.queue_time + 
                                     (1 - alpha) * self.average_queue_time)
            
            self.average_processing_time = (alpha * result.processing_time + 
                                          (1 - alpha) * self.average_processing_time)
    
    async def _free_resources_for_model(self, spec -> None: ModelSpec) -> None:
        """Free resources by unloading LRU models"""
        with self.lock:
            models_to_unload = []
            
            # Find LRU models to unload
            for model_id in self.model_load_order:
                models_to_unload.append(model_id)
                
                # Check if we have enough resources after unloading these models
                freed_resources = {}
                for unload_id in models_to_unload:
                    model_spec = self.model_specs[unload_id]
                    for resource_type, amount in model_spec.resource_requirements.items():
                        freed_resources[resource_type] = freed_resources.get(resource_type, 0) + amount
                
                # Check if freed resources are sufficient
                sufficient = True
                for resource_type, required in spec.resource_requirements.items():
                    current_available = (self.resource_manager.available_resources.get(resource_type, 0) - 
                                       self.resource_manager.allocated_resources.get(resource_type, 0))
                    total_available = current_available + freed_resources.get(resource_type, 0)
                    
                    if total_available < required:
                        sufficient = False
                        break
                
                if sufficient:
                    break
        
        # Unload the identified models
        for model_id in models_to_unload:
            logger.info(f"Unloading LRU model {model_id} to free resources")
            await self.unload_model(model_id)
    
    async def _monitor_performance(self) -> None:
        """Monitor engine performance"""
        while self.is_running:
            try:
                # Log performance metrics
                stats = self.get_engine_stats()
                logger.info(f"Engine Stats: {json.dumps(stats, indent=2)}")
                
                # Check for performance issues
                if stats['success_rate'] < 0.95:
                    logger.warning(f"Low success rate: {stats['success_rate']:.2%}")
                
                if stats['average_queue_time'] > 5.0:
                    logger.warning(f"High queue time: {stats['average_queue_time']:.2f}s")
                
                # Memory cleanup
                if stats['queue_size'] == 0:
                    gc.collect()  # Force garbage collection when idle
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_requests(self) -> None:
        """Clean up expired requests from queue"""
        while self.is_running:
            try:
                # This is a simplified cleanup - in a real implementation,
                # we would need to iterate through the queue and remove expired items
                await asyncio.sleep(30)  # Clean up every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in request cleanup: {str(e)}")
                await asyncio.sleep(30)
    
    async def _optimize_model_allocation(self) -> None:
        """Optimize model allocation based on usage patterns"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Find unused models
                unused_threshold = timedelta(hours=1)
                for model_id, instance in list(self.model_instances.items()):
                    if (instance.last_used and 
                        current_time - instance.last_used > unused_threshold):
                        
                        logger.info(f"Unloading unused model: {model_id}")
                        await self.unload_model(model_id)
                
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in model optimization: {str(e)}")
                await asyncio.sleep(300)
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics"""
        success_rate = self.completed_requests / max(self.total_requests, 1)
        
        with self.lock:
            model_stats = {}
            for model_id, instance in self.model_instances.items():
                model_stats[model_id] = instance.get_performance_stats()
        
        return {
            'total_requests': self.total_requests,
            'completed_requests': self.completed_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'average_queue_time': self.average_queue_time,
            'average_processing_time': self.average_processing_time,
            'queue_size': self.inference_queue.size(),
            'loaded_models': len(self.model_instances),
            'registered_models': len(self.model_specs),
            'resource_utilization': self.resource_manager.get_resource_utilization(),
            'model_performance': model_stats,
            'is_running': self.is_running,
            'worker_count': len(self.worker_tasks)
        }
    
    async def get_model_performance(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get performance statistics for a specific model"""
        instance = self.model_instances.get(model_id)
        if instance:
            return instance.get_performance_stats()
        return None
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inference engine events"""
        try:
            event_type = event_data.get('event_type')
            
            if event_type == 'inference_request':
                # Create inference request from event data
                request = InferenceRequest(
                    request_id=event_data.get('request_id', str(uuid.uuid4())),
                    model_id=event_data.get('model_id'),
                    inference_type=InferenceType(event_data.get('inference_type', 'real_time')),
                    input_data=event_data.get('input_data'),
                    batch_size=event_data.get('batch_size', 1),
                    priority=EventPriority(event_data.get('priority', 'medium'))
                )
                
                # Submit request
                request_id = await self.submit_inference_request(request)
                
                return {
                    'status': 'success',
                    'request_id': request_id,
                    'message': 'Inference request submitted successfully'
                }
            
            elif event_type == 'load_model':
                model_id = event_data.get('model_id')
                success = await self.load_model(model_id)
                
                return {
                    'status': 'success' if success else 'error',
                    'message': f'Model {model_id} loaded' if success else f'Failed to load model {model_id}'
                }
            
            elif event_type == 'unload_model':
                model_id = event_data.get('model_id')
                success = await self.unload_model(model_id)
                
                return {
                    'status': 'success' if success else 'error',
                    'message': f'Model {model_id} unloaded' if success else f'Failed to unload model {model_id}'
                }
            
            elif event_type == 'get_stats':
                stats = self.get_engine_stats()
                return {
                    'status': 'success',
                    'engine_stats': stats
                }
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown event type: {event_type}'
                }
                
        except Exception as e:
            logger.error(f"Error handling inference engine event: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Export classes and functions
__all__ = [
    'InferenceType',
    'ModelFramework',
    'InferenceStatus',
    'ResourceType',
    'ModelSpec',
    'InferenceRequest',
    'InferenceResult',
    'ModelInstance',
    'DummyModelInstance',
    'ResourceManager',
    'InferenceQueue',
    'AIInferenceEngine'
]