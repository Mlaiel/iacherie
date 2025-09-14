"""ML Model Orchestrator

Enterprise-grade machine learning model orchestration system for the IA Influencer Agent platform.
Coordinates dynamic ML model loading, inference scheduling, and performance optimization across
multiple AI processing workflows.

This module orchestrates ML models following the business logic:
User Upload → ML Model Selection → Inference Orchestration → Performance Optimization → Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution without explicit written permission from Fahed Mlaiel (mlaiel@live.de)
is strictly prohibited and may result in legal action.
"""

import logging
import asyncio
import threading
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import time

# Core imports
from ..core.base_event_handler import BaseEventHandler
from ..core.event_priority import EventPriority
from ..core.event_status import EventStatus

logger = logging.getLogger(__name__)

class MLModelType(Enum):
    """ML model type enumeration for orchestration"""
    
    TRANSFORMER = "transformer"
    NEURAL_NETWORK = "neural_network"
    DEEP_LEARNING = "deep_learning"
    COMPUTER_VISION = "computer_vision"
    NATURAL_LANGUAGE = "natural_language"
    AUDIO_PROCESSING = "audio_processing"
    RECOMMENDATION = "recommendation"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    REINFORCEMENT_LEARNING = "reinforcement_learning"

class ModelStatus(Enum):
    """Model status enumeration"""
    
    LOADING = "loading"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    UNLOADING = "unloading"
    MAINTENANCE = "maintenance"

class InferenceMode(Enum):
    """Inference execution mode"""
    
    SYNC = "synchronous"
    ASYNC = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"
    REAL_TIME = "real_time"

@dataclass
class ModelMetadata:
    """ML model metadata and configuration"""
    
    model_id: str
    model_type: MLModelType
    version: str
    framework: str  # pytorch, tensorflow, sklearn, etc.
    input_shape: Optional[tuple] = None
    output_shape: Optional[tuple] = None
    memory_requirements: int = 0  # MB
    gpu_required: bool = False
    batch_size: int = 1
    max_sequence_length: Optional[int] = None
    supported_formats: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    model_path: Optional[str] = None
    config_path: Optional[str] = None
    
    def estimate_inference_time(self, content_size: int) -> float:
        """Estimate inference time based on content size"""
        base_time = self.performance_metrics.get('base_inference_time', 0.1)
        size_factor = content_size / 1024.0  # Convert to KB
        return base_time * (1 + size_factor * 0.001)

@dataclass
class InferenceRequest:
    """ML model inference request"""
    
    request_id: str
    model_id: str
    content_data: Any
    content_type: str
    inference_mode: InferenceMode
    priority: EventPriority
    callback: Optional[Callable] = None
    timeout: float = 30.0
    preprocessing_params: Dict[str, Any] = field(default_factory=dict)
    postprocessing_params: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            'request_id': self.request_id,
            'model_id': self.model_id,
            'content_type': self.content_type,
            'inference_mode': self.inference_mode.value,
            'priority': self.priority.value,
            'timeout': self.timeout,
            'preprocessing_params': self.preprocessing_params,
            'postprocessing_params': self.postprocessing_params,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class InferenceResult:
    """ML model inference result"""
    
    request_id: str
    model_id: str
    success: bool
    predictions: Any
    confidence_scores: Optional[List[float]] = None
    processing_time: float = 0.0
    memory_usage: int = 0  # MB
    gpu_usage: float = 0.0  # %
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'request_id': self.request_id,
            'model_id': self.model_id,
            'success': self.success,
            'predictions': self.predictions,
            'confidence_scores': self.confidence_scores,
            'processing_time': self.processing_time,
            'memory_usage': self.memory_usage,
            'gpu_usage': self.gpu_usage,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }

class MLModelWrapper(ABC):
    """Abstract ML model wrapper for orchestration"""
    
    def __init__(self, metadata -> None: ModelMetadata) -> None:
        self.metadata = metadata
        self.status = ModelStatus.LOADING
        self.load_time = None
        self.inference_count = 0
        self.last_inference_time = None
        self.average_inference_time = 0.0
        self.error_count = 0
        
    @abstractmethod
    async def load_model(self) -> bool:
        """Load the ML model"""
        pass
    
    @abstractmethod
    async def unload_model(self) -> bool:
        """Unload the ML model"""
        pass
    
    @abstractmethod
    async def predict(self, input_data: Any, **kwargs) -> Any:
        """Run model inference"""
        pass
    
    @abstractmethod
    async def preprocess(self, raw_data: Any, **kwargs) -> Any:
        """Preprocess input data"""
        pass
    
    @abstractmethod
    async def postprocess(self, predictions: Any, **kwargs) -> Any:
        """Postprocess model predictions"""
        pass
    
    def update_performance_metrics(self, inference_time -> None: float) -> None:
        """Update model performance metrics"""
        self.inference_count += 1
        self.last_inference_time = inference_time
        
        if self.average_inference_time == 0.0:
            self.average_inference_time = inference_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.average_inference_time = (alpha * inference_time + 
                                         (1 - alpha) * self.average_inference_time)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get model performance statistics"""
        return {
            'inference_count': self.inference_count,
            'average_inference_time': self.average_inference_time,
            'last_inference_time': self.last_inference_time,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(self.inference_count, 1),
            'status': self.status.value,
            'load_time': self.load_time.isoformat() if self.load_time else None
        }

class ModelPool:
    """ML model pool for efficient resource management"""
    
    def __init__(self, max_models -> None: int = 10) -> None:
        self.max_models = max_models
        self.models: Dict[str, MLModelWrapper] = {}
        self.model_queue = queue.PriorityQueue()
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
    
    async def add_model(self, model: MLModelWrapper) -> bool:
        """Add model to pool"""
        async with asyncio.Lock():
            if len(self.models) >= self.max_models:
                # Remove least recently used model
                await self._evict_lru_model()
            
            try:
                success = await model.load_model()
                if success:
                    model.status = ModelStatus.READY
                    model.load_time = datetime.now()
                    self.models[model.metadata.model_id] = model
                    self.usage_stats[model.metadata.model_id] = {
                        'last_used': datetime.now(),
                        'usage_count': 0
                    }
                    logger.info(f"Model {model.metadata.model_id} loaded successfully")
                    return True
                else:
                    model.status = ModelStatus.ERROR
                    logger.error(f"Failed to load model {model.metadata.model_id}")
                    return False
            except Exception as e:
                model.status = ModelStatus.ERROR
                logger.error(f"Error loading model {model.metadata.model_id}: {str(e)}")
                return False
    
    async def get_model(self, model_id: str) -> Optional[MLModelWrapper]:
        """Get model from pool"""
        async with asyncio.Lock():
            model = self.models.get(model_id)
            if model and model.status == ModelStatus.READY:
                self.usage_stats[model_id]['last_used'] = datetime.now()
                self.usage_stats[model_id]['usage_count'] += 1
                return model
            return None
    
    async def remove_model(self, model_id: str) -> bool:
        """Remove model from pool"""
        async with asyncio.Lock():
            model = self.models.get(model_id)
            if model:
                try:
                    await model.unload_model()
                    del self.models[model_id]
                    del self.usage_stats[model_id]
                    logger.info(f"Model {model_id} removed from pool")
                    return True
                except Exception as e:
                    logger.error(f"Error removing model {model_id}: {str(e)}")
                    return False
            return False
    
    async def _evict_lru_model(self) -> None:
        """Evict least recently used model"""
        if not self.usage_stats:
            return
        
        # Find least recently used model
        lru_model_id = min(self.usage_stats.keys(), 
                          key=lambda x: self.usage_stats[x]['last_used'])
        
        await self.remove_model(lru_model_id)
        logger.info(f"Evicted LRU model: {lru_model_id}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get model pool statistics"""
        return {
            'total_models': len(self.models),
            'max_models': self.max_models,
            'model_statuses': {
                model_id: model.status.value 
                for model_id, model in self.models.items()
            },
            'usage_stats': self.usage_stats
        }

class MLModelOrchestrator(BaseEventHandler):
    """
    Enterprise ML Model Orchestrator
    
    Coordinates machine learning model loading, inference scheduling, and performance optimization
    across multiple AI processing workflows in the IA Influencer Agent platform.
    """
    
    def __init__(self, max_models -> None: int = 20, max_workers -> None: int = 10) -> None:
        super().__init__()
        self.model_pool = ModelPool(max_models)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.inference_queue = asyncio.Queue(maxsize=1000)
        self.model_registry: Dict[str, ModelMetadata] = {}
        self.performance_monitor = {}
        self.load_balancer = {}
        self.is_running = False
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0
        
        logger.info("ML Model Orchestrator initialized")
    
    async def start_orchestrator(self) -> None:
        """Start the ML model orchestrator"""
        self.is_running = True
        
        # Start background tasks
        asyncio.create_task(self._process_inference_queue())
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._optimize_model_allocation())
        
        logger.info("ML Model Orchestrator started")
    
    async def stop_orchestrator(self) -> None:
        """Stop the ML model orchestrator"""
        self.is_running = False
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Unload all models
        for model_id in list(self.model_pool.models.keys()):
            await self.model_pool.remove_model(model_id)
        
        logger.info("ML Model Orchestrator stopped")
    
    async def register_model(self, metadata: ModelMetadata) -> bool:
        """Register a new ML model"""
        try:
            self.model_registry[metadata.model_id] = metadata
            logger.info(f"Model {metadata.model_id} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register model {metadata.model_id}: {str(e)}")
            return False
    
    async def load_model(self, model_id: str, model_wrapper: MLModelWrapper) -> bool:
        """Load a model into the orchestrator"""
        try:
            if model_id not in self.model_registry:
                logger.error(f"Model {model_id} not registered")
                return False
            
            success = await self.model_pool.add_model(model_wrapper)
            if success:
                logger.info(f"Model {model_id} loaded and ready for inference")
            return success
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {str(e)}")
            return False
    
    async def submit_inference_request(self, request: InferenceRequest) -> str:
        """Submit an inference request to the orchestrator"""
        try:
            await self.inference_queue.put(request)
            self.total_requests += 1
            logger.debug(f"Inference request {request.request_id} queued")
            return request.request_id
        except Exception as e:
            logger.error(f"Failed to submit inference request: {str(e)}")
            self.failed_requests += 1
            raise
    
    async def _process_inference_queue(self) -> None:
        """Process inference requests from the queue"""
        while self.is_running:
            try:
                # Get request from queue
                request = await asyncio.wait_for(
                    self.inference_queue.get(), 
                    timeout=1.0
                )
                
                # Process request
                asyncio.create_task(self._execute_inference(request))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing inference queue: {str(e)}")
    
    async def _execute_inference(self, request: InferenceRequest) -> InferenceResult:
        """Execute a single inference request"""
        start_time = time.time()
        
        try:
            # Get model from pool
            model = await self.model_pool.get_model(request.model_id)
            if not model:
                error_msg = f"Model {request.model_id} not available"
                logger.error(error_msg)
                result = InferenceResult(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    success=False,
                    predictions=None,
                    error_message=error_msg
                )
                self.failed_requests += 1
                return result
            
            # Update model status
            model.status = ModelStatus.BUSY
            
            try:
                # Preprocess input data
                processed_input = await model.preprocess(
                    request.content_data, 
                    **request.preprocessing_params
                )
                
                # Run inference
                predictions = await model.predict(processed_input)
                
                # Postprocess predictions
                final_predictions = await model.postprocess(
                    predictions,
                    **request.postprocessing_params
                )
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Update model performance metrics
                model.update_performance_metrics(processing_time)
                
                # Create successful result
                result = InferenceResult(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    success=True,
                    predictions=final_predictions,
                    processing_time=processing_time
                )
                
                self.successful_requests += 1
                
                # Update orchestrator performance metrics
                self._update_performance_metrics(processing_time)
                
                logger.debug(f"Inference {request.request_id} completed successfully")
                
            finally:
                # Reset model status
                model.status = ModelStatus.READY
            
            # Execute callback if provided
            if request.callback:
                try:
                    await request.callback(result)
                except Exception as e:
                    logger.error(f"Error executing callback: {str(e)}")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Inference error: {str(e)}"
            logger.error(error_msg)
            
            result = InferenceResult(
                request_id=request.request_id,
                model_id=request.model_id,
                success=False,
                predictions=None,
                processing_time=processing_time,
                error_message=error_msg
            )
            
            self.failed_requests += 1
            return result
    
    def _update_performance_metrics(self, processing_time -> None: float) -> None:
        """Update orchestrator performance metrics"""
        if self.average_response_time == 0.0:
            self.average_response_time = processing_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.average_response_time = (alpha * processing_time + 
                                        (1 - alpha) * self.average_response_time)
    
    async def _monitor_performance(self) -> None:
        """Monitor orchestrator and model performance"""
        while self.is_running:
            try:
                # Log performance metrics
                stats = self.get_orchestrator_stats()
                logger.info(f"Orchestrator Stats: {json.dumps(stats, indent=2)}")
                
                # Check for performance issues
                if stats['success_rate'] < 0.95:
                    logger.warning(f"Low success rate: {stats['success_rate']:.2%}")
                
                if stats['average_response_time'] > 5.0:
                    logger.warning(f"High response time: {stats['average_response_time']:.2f}s")
                
                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {str(e)}")
                await asyncio.sleep(60)
    
    async def _optimize_model_allocation(self) -> None:
        """Optimize model allocation and resource usage"""
        while self.is_running:
            try:
                # Analyze model usage patterns
                pool_stats = self.model_pool.get_pool_stats()
                
                # Identify underused models
                current_time = datetime.now()
                for model_id, stats in pool_stats['usage_stats'].items():
                    last_used = stats['last_used']
                    time_since_use = (current_time - last_used).total_seconds()
                    
                    # Unload models not used in last hour
                    if time_since_use > 3600 and stats['usage_count'] < 10:
                        logger.info(f"Unloading underused model: {model_id}")
                        await self.model_pool.remove_model(model_id)
                
                # Sleep for optimization interval
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in model optimization: {str(e)}")
                await asyncio.sleep(300)
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator statistics"""
        success_rate = (self.successful_requests / max(self.total_requests, 1))
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'average_response_time': self.average_response_time,
            'queue_size': self.inference_queue.qsize(),
            'registered_models': len(self.model_registry),
            'loaded_models': len(self.model_pool.models),
            'model_pool_stats': self.model_pool.get_pool_stats(),
            'is_running': self.is_running
        }
    
    async def get_model_performance(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get performance statistics for a specific model"""
        model = await self.model_pool.get_model(model_id)
        if model:
            return model.get_performance_stats()
        return None
    
    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle orchestration events"""
        try:
            event_type = event_data.get('event_type')
            
            if event_type == 'inference_request':
                # Create inference request from event data
                request = InferenceRequest(
                    request_id=event_data.get('request_id'),
                    model_id=event_data.get('model_id'),
                    content_data=event_data.get('content_data'),
                    content_type=event_data.get('content_type'),
                    inference_mode=InferenceMode(event_data.get('inference_mode', 'async')),
                    priority=EventPriority(event_data.get('priority', 'medium'))
                )
                
                # Submit request
                request_id = await self.submit_inference_request(request)
                
                return {
                    'status': 'success',
                    'request_id': request_id,
                    'message': 'Inference request submitted successfully'
                }
            
            elif event_type == 'model_status':
                # Return model status information
                stats = self.get_orchestrator_stats()
                return {
                    'status': 'success',
                    'orchestrator_stats': stats
                }
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown event type: {event_type}'
                }
                
        except Exception as e:
            logger.error(f"Error handling orchestration event: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Export classes and functions
__all__ = [
    'MLModelType',
    'ModelStatus', 
    'InferenceMode',
    'ModelMetadata',
    'InferenceRequest',
    'InferenceResult',
    'MLModelWrapper',
    'ModelPool',
    'MLModelOrchestrator'
]