"""
🎯 AI Inference Microservice
Real-time AI inference and prediction service with model management, scaling, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
import logging
import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import concurrent.futures
from pydantic import BaseModel, Field
import base64
import io

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """AI model types"""
    TEXT_CLASSIFICATION = "text_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTENT_GENERATION = "content_generation"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    AUDIO_ANALYSIS = "audio_analysis"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    LANGUAGE_TRANSLATION = "language_translation"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    FACE_DETECTION = "face_detection"
    STYLE_TRANSFER = "style_transfer"
    CONTENT_MODERATION = "content_moderation"


class ModelStatus(str, Enum):
    """Model status"""
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    UPDATING = "updating"
    DISABLED = "disabled"


class InferenceStatus(str, Enum):
    """Inference request status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ModelFramework(str, Enum):
    """Supported ML frameworks"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    HUGGINGFACE = "huggingface"
    ONNX = "onnx"
    CUSTOM = "custom"


@dataclass
class ModelMetadata:
    """AI model metadata"""
    id: str
    name: str
    version: str
    type: ModelType
    framework: ModelFramework
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    model_path: str = ""
    config_path: str = ""
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)
    postprocessing_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'type': self.type.value,
            'framework': self.framework.value,
            'description': self.description,
            'input_schema': self.input_schema,
            'output_schema': self.output_schema,
            'model_path': self.model_path,
            'config_path': self.config_path,
            'preprocessing_config': self.preprocessing_config,
            'postprocessing_config': self.postprocessing_config,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    throughput: float = 0.0  # requests per second
    memory_usage: float = 0.0  # MB
    cpu_usage: float = 0.0  # percentage
    gpu_usage: float = 0.0  # percentage
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / max(self.total_requests, 1),
            'average_latency': self.average_latency,
            'p95_latency': self.p95_latency,
            'p99_latency': self.p99_latency,
            'throughput': self.throughput,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'gpu_usage': self.gpu_usage,
            'last_updated': self.last_updated.isoformat()
        }


@dataclass
class InferenceRequest:
    """AI inference request"""
    id: str
    model_id: str
    input_data: Dict[str, Any]
    parameters: Dict[str, Any] = field(default_factory=dict)
    callback_url: Optional[str] = None
    priority: int = 5  # 1-10, higher is more priority
    timeout: int = 30  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: InferenceStatus = InferenceStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def get_latency(self) -> Optional[float]:
        """Get request latency in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
        
    def is_expired(self) -> bool:
        """Check if request is expired"""
        if not self.started_at:
            return False
        return (datetime.utcnow() - self.started_at).total_seconds() > self.timeout
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'model_id': self.model_id,
            'input_data': self.input_data,
            'parameters': self.parameters,
            'callback_url': self.callback_url,
            'priority': self.priority,
            'timeout': self.timeout,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'latency': self.get_latency()
        }


class ModelInterface(ABC):
    """Abstract model interface"""
    
    @abstractmethod
    async def load(self, metadata: ModelMetadata) -> bool:
        """Load model"""
        pass
        
    @abstractmethod
    async def predict(self, input_data: Dict[str, Any], 
                     parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make prediction"""
        pass
        
    @abstractmethod
    async def unload(self) -> bool:
        """Unload model"""
        pass
        
    @abstractmethod
    def get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        pass


class HuggingFaceModel(ModelInterface):
    """Hugging Face model implementation"""
    
    def __init__(self) -> None:
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.metadata = None
        
    async def load(self, metadata: ModelMetadata) -> bool:
        """Load Hugging Face model"""
        try:
            # This would require transformers library
            logger.info(f"Loading Hugging Face model: {metadata.name}")
            
            # Simulate model loading
            await asyncio.sleep(1)  # Simulate loading time
            
            self.metadata = metadata
            logger.info(f"Loaded Hugging Face model: {metadata.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Hugging Face model: {str(e)}")
            return False
            
    async def predict(self, input_data: Dict[str, Any], 
                     parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make prediction with Hugging Face model"""
        try:
            if not self.metadata:
                raise Exception("Model not loaded")
                
            # Simulate prediction based on model type
            if self.metadata.type == ModelType.TEXT_CLASSIFICATION:
                text = input_data.get('text', '')
                return {
                    'labels': ['positive', 'negative'],
                    'scores': [0.7, 0.3],
                    'predicted_label': 'positive'
                }
            elif self.metadata.type == ModelType.SENTIMENT_ANALYSIS:
                text = input_data.get('text', '')
                return {
                    'sentiment': 'positive',
                    'confidence': 0.85,
                    'scores': {'positive': 0.85, 'negative': 0.15}
                }
            elif self.metadata.type == ModelType.CONTENT_GENERATION:
                prompt = input_data.get('prompt', '')
                max_length = parameters.get('max_length', 100) if parameters else 100
                return {
                    'generated_text': f"Generated content based on: {prompt}",
                    'length': max_length
                }
            else:
                return {'result': 'prediction_result', 'confidence': 0.9}
                
        except Exception as e:
            logger.error(f"Error in Hugging Face prediction: {str(e)}")
            raise
            
    async def unload(self) -> bool:
        """Unload Hugging Face model"""
        try:
            self.model = None
            self.tokenizer = None
            self.pipeline = None
            self.metadata = None
            return True
        except Exception as e:
            logger.error(f"Error unloading Hugging Face model: {str(e)}")
            return False
            
    def get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        # Simulate memory usage calculation
        return 512.0 if self.metadata else 0.0


class CustomModel(ModelInterface):
    """Custom model implementation"""
    
    def __init__(self) -> None:
        self.model = None
        self.metadata = None
        
    async def load(self, metadata: ModelMetadata) -> bool:
        """Load custom model"""
        try:
            logger.info(f"Loading custom model: {metadata.name}")
            
            # Simulate model loading
            await asyncio.sleep(0.5)
            
            self.metadata = metadata
            logger.info(f"Loaded custom model: {metadata.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading custom model: {str(e)}")
            return False
            
    async def predict(self, input_data: Dict[str, Any], 
                     parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make prediction with custom model"""
        try:
            if not self.metadata:
                raise Exception("Model not loaded")
                
            # Simulate custom prediction logic
            if self.metadata.type == ModelType.IMAGE_CLASSIFICATION:
                return {
                    'labels': ['cat', 'dog', 'bird'],
                    'scores': [0.6, 0.3, 0.1],
                    'predicted_label': 'cat'
                }
            elif self.metadata.type == ModelType.AUDIO_ANALYSIS:
                return {
                    'emotion': 'happy',
                    'energy': 0.8,
                    'tempo': 120,
                    'key': 'C major'
                }
            else:
                return {'result': 'custom_prediction', 'confidence': 0.88}
                
        except Exception as e:
            logger.error(f"Error in custom prediction: {str(e)}")
            raise
            
    async def unload(self) -> bool:
        """Unload custom model"""
        try:
            self.model = None
            self.metadata = None
            return True
        except Exception as e:
            logger.error(f"Error unloading custom model: {str(e)}")
            return False
            
    def get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        return 256.0 if self.metadata else 0.0


class ModelManager:
    """Manages AI models and their lifecycle"""
    
    def __init__(self, max_models -> None: int = 10) -> None:
        self.max_models = max_models
        self.models: Dict[str, ModelInterface] = {}
        self.metadata: Dict[str, ModelMetadata] = {}
        self.status: Dict[str, ModelStatus] = {}
        self.metrics: Dict[str, ModelPerformanceMetrics] = {}
        self.latency_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.RLock()
        
    async def load_model(self, metadata: ModelMetadata) -> bool:
        """Load a model"""
        try:
            with self._lock:
                # Check if model is already loaded
                if metadata.id in self.models:
                    logger.info(f"Model {metadata.id} already loaded")
                    return True
                    
                # Check capacity
                if len(self.models) >= self.max_models:
                    # Unload least used model
                    await self._unload_least_used_model()
                    
                # Set status to loading
                self.status[metadata.id] = ModelStatus.LOADING
                
            # Create model instance based on framework
            model = self._create_model_instance(metadata.framework)
            
            # Load the model
            success = await model.load(metadata)
            
            with self._lock:
                if success:
                    self.models[metadata.id] = model
                    self.metadata[metadata.id] = metadata
                    self.status[metadata.id] = ModelStatus.READY
                    self.metrics[metadata.id] = ModelPerformanceMetrics()
                    logger.info(f"Successfully loaded model: {metadata.id}")
                else:
                    self.status[metadata.id] = ModelStatus.ERROR
                    logger.error(f"Failed to load model: {metadata.id}")
                    
            return success
            
        except Exception as e:
            logger.error(f"Error loading model {metadata.id}: {str(e)}")
            with self._lock:
                self.status[metadata.id] = ModelStatus.ERROR
            return False
            
    async def unload_model(self, model_id: str) -> bool:
        """Unload a model"""
        try:
            with self._lock:
                if model_id not in self.models:
                    return False
                    
                model = self.models[model_id]
                
            success = await model.unload()
            
            with self._lock:
                if success:
                    del self.models[model_id]
                    del self.metadata[model_id]
                    del self.status[model_id]
                    del self.metrics[model_id]
                    if model_id in self.latency_history:
                        del self.latency_history[model_id]
                    logger.info(f"Successfully unloaded model: {model_id}")
                    
            return success
            
        except Exception as e:
            logger.error(f"Error unloading model {model_id}: {str(e)}")
            return False
            
    async def predict(self, model_id: str, input_data: Dict[str, Any], 
                     parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make prediction with a model"""
        start_time = time.time()
        
        try:
            with self._lock:
                if model_id not in self.models or self.status[model_id] != ModelStatus.READY:
                    raise Exception(f"Model {model_id} not ready")
                    
                model = self.models[model_id]
                metrics = self.metrics[model_id]
                
            # Make prediction
            result = await model.predict(input_data, parameters)
            
            # Update metrics
            latency = time.time() - start_time
            with self._lock:
                metrics.total_requests += 1
                metrics.successful_requests += 1
                metrics.average_latency = (
                    (metrics.average_latency * (metrics.total_requests - 1) + latency) / 
                    metrics.total_requests
                )
                self.latency_history[model_id].append(latency)
                self._update_percentiles(model_id)
                metrics.last_updated = datetime.utcnow()
                
            return result
            
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"Error in prediction for model {model_id}: {str(e)}")
            
            with self._lock:
                if model_id in self.metrics:
                    self.metrics[model_id].total_requests += 1
                    self.metrics[model_id].failed_requests += 1
                    
            raise
            
    def _create_model_instance(self, framework: ModelFramework) -> ModelInterface:
        """Create model instance based on framework"""
        if framework == ModelFramework.HUGGINGFACE:
            return HuggingFaceModel()
        elif framework == ModelFramework.CUSTOM:
            return CustomModel()
        else:
            # Default to custom for unsupported frameworks
            return CustomModel()
            
    async def _unload_least_used_model(self) -> None:
        """Unload the least used model"""
        if not self.models:
            return
            
        # Find model with lowest request count
        least_used_id = min(
            self.metrics.keys(),
            key=lambda mid: self.metrics[mid].total_requests
        )
        
        await self.unload_model(least_used_id)
        
    def _update_percentiles(self, model_id -> None: str) -> None:
        """Update latency percentiles"""
        if model_id not in self.latency_history:
            return
            
        latencies = sorted(self.latency_history[model_id])
        if not latencies:
            return
            
        metrics = self.metrics[model_id]
        n = len(latencies)
        
        if n >= 20:  # Only calculate percentiles with sufficient data
            metrics.p95_latency = latencies[int(0.95 * n)]
            metrics.p99_latency = latencies[int(0.99 * n)]
            
    def get_model_status(self, model_id: str) -> Optional[ModelStatus]:
        """Get model status"""
        return self.status.get(model_id)
        
    def get_model_metrics(self, model_id: str) -> Optional[ModelPerformanceMetrics]:
        """Get model metrics"""
        return self.metrics.get(model_id)
        
    def list_models(self) -> List[Dict[str, Any]]:
        """List all loaded models"""
        result = []
        with self._lock:
            for model_id in self.models:
                model_info = {
                    'id': model_id,
                    'metadata': self.metadata[model_id].to_dict(),
                    'status': self.status[model_id].value,
                    'metrics': self.metrics[model_id].to_dict(),
                    'memory_usage': self.models[model_id].get_memory_usage()
                }
                result.append(model_info)
        return result


class RequestQueue:
    """Priority queue for inference requests"""
    
    def __init__(self, maxsize -> None: int = 1000) -> None:
        self.maxsize = maxsize
        self.requests: Dict[str, InferenceRequest] = {}
        self.priority_queue: List[str] = []  # request_ids sorted by priority
        self._lock = threading.RLock()
        
    def add_request(self, request: InferenceRequest) -> bool:
        """Add request to queue"""
        with self._lock:
            if len(self.requests) >= self.maxsize:
                return False
                
            self.requests[request.id] = request
            
            # Insert in priority order (higher priority first)
            inserted = False
            for i, req_id in enumerate(self.priority_queue):
                if request.priority > self.requests[req_id].priority:
                    self.priority_queue.insert(i, request.id)
                    inserted = True
                    break
                    
            if not inserted:
                self.priority_queue.append(request.id)
                
            return True
            
    def get_next_request(self) -> Optional[InferenceRequest]:
        """Get next request from queue"""
        with self._lock:
            if not self.priority_queue:
                return None
                
            request_id = self.priority_queue.pop(0)
            request = self.requests.pop(request_id)
            return request
            
    def remove_request(self, request_id: str) -> Optional[InferenceRequest]:
        """Remove specific request from queue"""
        with self._lock:
            if request_id not in self.requests:
                return None
                
            request = self.requests.pop(request_id)
            if request_id in self.priority_queue:
                self.priority_queue.remove(request_id)
                
            return request
            
    def get_queue_size(self) -> int:
        """Get queue size"""
        return len(self.requests)


class AIInferenceService:
    """Real-time AI Inference and Prediction Service"""
    
    def __init__(self, name -> None: str = "ai_inference_service") -> None:
        self.name = name
        self.model_manager = ModelManager()
        self.request_queue = RequestQueue()
        self.active_requests: Dict[str, InferenceRequest] = {}
        self.completed_requests: Dict[str, InferenceRequest] = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.running = False
        self.worker_tasks = []
        self.cleanup_task = None
        self.stats = {
            'total_requests': 0,
            'completed_requests': 0,
            'failed_requests': 0,
            'average_queue_time': 0.0,
            'models_loaded': 0
        }
        
    async def start(self) -> None:
        """Start AI inference service"""
        self.running = True
        
        # Start worker tasks
        for i in range(4):  # 4 workers
            task = asyncio.create_task(self._worker(f"worker_{i}"))
            self.worker_tasks.append(task)
            
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_completed_requests())
        
        logger.info(f"Started AI inference service: {self.name}")
        
    async def stop(self) -> None:
        """Stop AI inference service"""
        self.running = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
                
        logger.info(f"Stopped AI inference service: {self.name}")
        
    async def load_model(self, metadata: ModelMetadata) -> bool:
        """Load AI model"""
        success = await self.model_manager.load_model(metadata)
        if success:
            self.stats['models_loaded'] += 1
        return success
        
    async def unload_model(self, model_id: str) -> bool:
        """Unload AI model"""
        success = await self.model_manager.unload_model(model_id)
        if success:
            self.stats['models_loaded'] -= 1
        return success
        
    async def submit_inference(self, model_id: str, input_data: Dict[str, Any],
                             parameters: Dict[str, Any] = None,
                             priority: int = 5, timeout: int = 30,
                             callback_url: str = None) -> str:
        """Submit inference request"""
        try:
            # Check if model exists and is ready
            status = self.model_manager.get_model_status(model_id)
            if status != ModelStatus.READY:
                raise Exception(f"Model {model_id} not ready (status: {status})")
                
            # Create request
            request = InferenceRequest(
                id=str(uuid.uuid4()),
                model_id=model_id,
                input_data=input_data,
                parameters=parameters or {},
                priority=priority,
                timeout=timeout,
                callback_url=callback_url
            )
            
            # Add to queue
            if not self.request_queue.add_request(request):
                raise Exception("Request queue is full")
                
            self.stats['total_requests'] += 1
            
            logger.info(f"Submitted inference request: {request.id}")
            return request.id
            
        except Exception as e:
            logger.error(f"Error submitting inference request: {str(e)}")
            raise
            
    async def get_inference_result(self, request_id: str) -> Optional[InferenceRequest]:
        """Get inference result"""
        # Check active requests
        if request_id in self.active_requests:
            return self.active_requests[request_id]
            
        # Check completed requests
        if request_id in self.completed_requests:
            return self.completed_requests[request_id]
            
        return None
        
    async def cancel_inference(self, request_id: str) -> bool:
        """Cancel inference request"""
        try:
            # Remove from queue if still pending
            request = self.request_queue.remove_request(request_id)
            if request:
                request.status = InferenceStatus.FAILED
                request.error = "Cancelled by user"
                self.completed_requests[request_id] = request
                return True
                
            # Check if currently processing
            if request_id in self.active_requests:
                request = self.active_requests[request_id]
                request.status = InferenceStatus.FAILED
                request.error = "Cancelled by user"
                # Note: Cannot stop already running inference
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling inference request: {str(e)}")
            return False
            
    async def _worker(self, worker_name -> None: str) -> None:
        """Worker to process inference requests"""
        logger.info(f"Started inference worker: {worker_name}")
        
        while self.running:
            try:
                # Get next request
                request = self.request_queue.get_next_request()
                if not request:
                    await asyncio.sleep(0.1)
                    continue
                    
                # Check if request expired
                if request.is_expired():
                    request.status = InferenceStatus.TIMEOUT
                    request.error = "Request expired in queue"
                    self.completed_requests[request.id] = request
                    self.stats['failed_requests'] += 1
                    continue
                    
                # Process request
                request.status = InferenceStatus.PROCESSING
                request.started_at = datetime.utcnow()
                self.active_requests[request.id] = request
                
                logger.debug(f"{worker_name} processing request: {request.id}")
                
                try:
                    # Make prediction
                    result = await self.model_manager.predict(
                        request.model_id,
                        request.input_data,
                        request.parameters
                    )
                    
                    # Update request
                    request.status = InferenceStatus.COMPLETED
                    request.result = result
                    request.completed_at = datetime.utcnow()
                    
                    self.stats['completed_requests'] += 1
                    
                except Exception as e:
                    request.status = InferenceStatus.FAILED
                    request.error = str(e)
                    request.completed_at = datetime.utcnow()
                    
                    self.stats['failed_requests'] += 1
                    logger.error(f"Inference failed for request {request.id}: {str(e)}")
                    
                # Move to completed
                self.active_requests.pop(request.id, None)
                self.completed_requests[request.id] = request
                
                # Send callback if specified
                if request.callback_url:
                    asyncio.create_task(self._send_callback(request))
                    
            except Exception as e:
                logger.error(f"Error in worker {worker_name}: {str(e)}")
                await asyncio.sleep(1)
                
        logger.info(f"Stopped inference worker: {worker_name}")
        
    async def _send_callback(self, request -> None: InferenceRequest) -> None:
        """Send callback notification"""
        try:
            import aiohttp
            
            payload = {
                'request_id': request.id,
                'status': request.status.value,
                'result': request.result,
                'error': request.error,
                'latency': request.get_latency()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(request.callback_url, json=payload) as response:
                    if response.status == 200:
                        logger.debug(f"Callback sent for request {request.id}")
                    else:
                        logger.warning(f"Callback failed for request {request.id}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending callback for request {request.id}: {str(e)}")
            
    async def _cleanup_completed_requests(self) -> None:
        """Cleanup old completed requests"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                expired_requests = [
                    req_id for req_id, request in self.completed_requests.items()
                    if request.completed_at and request.completed_at < cutoff_time
                ]
                
                for req_id in expired_requests:
                    del self.completed_requests[req_id]
                    
                if expired_requests:
                    logger.info(f"Cleaned up {len(expired_requests)} old requests")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "stats": self.stats,
            "queue_size": self.request_queue.get_queue_size(),
            "active_requests": len(self.active_requests),
            "completed_requests": len(self.completed_requests),
            "loaded_models": len(self.model_manager.models),
            "models": self.model_manager.list_models(),
            "timestamp": datetime.utcnow().isoformat()
        }


def create_ai_inference_service(config: Dict[str, Any] = None) -> AIInferenceService:
    """Factory function to create AI Inference service"""
    config = config or {}
    service_name = config.get('name', 'ai_inference_service')
    
    service = AIInferenceService(service_name)
    
    # Configure model manager
    if 'max_models' in config:
        service.model_manager.max_models = config['max_models']
        
    # Configure request queue
    if 'queue_size' in config:
        service.request_queue.maxsize = config['queue_size']
        
    # Configure workers
    if 'worker_count' in config:
        # This would need to be implemented in the service
        pass
        
    return service


__all__ = [
    'AIInferenceService', 'ModelMetadata', 'ModelPerformanceMetrics', 'InferenceRequest',
    'ModelType', 'ModelStatus', 'InferenceStatus', 'ModelFramework',
    'ModelInterface', 'HuggingFaceModel', 'CustomModel', 'ModelManager',
    'create_ai_inference_service'
]