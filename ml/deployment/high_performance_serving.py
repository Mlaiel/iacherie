"""
High-Performance Model Serving with Auto-Scaling
Implements optimized model serving infrastructure with auto-scaling capabilities
"""

import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
from abc import ABC, abstractmethod
import psutil
import gc

logger = logging.getLogger(__name__)


class ServeMode(Enum):
    """Model serving modes"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"


class ScalingStrategy(Enum):
    """Auto-scaling strategies"""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    LATENCY_BASED = "latency_based"
    THROUGHPUT_BASED = "throughput_based"
    HYBRID = "hybrid"


@dataclass
class PredictionRequest:
    """Prediction request structure"""
    request_id: str
    input_data: Union[Dict, List, np.ndarray, pd.DataFrame]
    model_name: str
    model_version: Optional[str] = None
    preprocessing_config: Optional[Dict] = None
    postprocessing_config: Optional[Dict] = None
    timeout_seconds: float = 30.0
    priority: int = 0  # Higher values = higher priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PredictionResponse:
    """Prediction response structure"""
    request_id: str
    predictions: Union[List, np.ndarray, Dict]
    model_name: str
    model_version: str
    confidence_scores: Optional[Union[List, np.ndarray]] = None
    processing_time_ms: float = 0.0
    preprocessing_time_ms: float = 0.0
    inference_time_ms: float = 0.0
    postprocessing_time_ms: float = 0.0
    status: str = "success"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)


@dataclass
class ServingMetrics:
    """Serving performance metrics"""
    requests_per_second: float = 0.0
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    queue_size: int = 0
    active_workers: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class ModelWrapper:
    """Wrapper for ML models with optimization features"""
    
    def __init__(
        self,
        model: Any,
        model_name: str,
        model_version: str,
        preprocessing_func: Optional[Callable] = None,
        postprocessing_func: Optional[Callable] = None
    ):
        self.model = model
        self.model_name = model_name
        self.model_version = model_version
        self.preprocessing_func = preprocessing_func
        self.postprocessing_func = postprocessing_func
        self.prediction_count = 0
        self.total_inference_time = 0.0
        self.last_accessed = datetime.now()
        
        # Model optimization flags
        self.is_optimized = False
        self.optimization_metadata = {}
    
    def preprocess(self, input_data: Any) -> Any:
        """Preprocess input data"""
        if self.preprocessing_func:
            return self.preprocessing_func(input_data)
        return input_data
    
    def predict(self, preprocessed_data: Any) -> Any:
        """Make prediction"""
        start_time = time.time()
        
        try:
            if hasattr(self.model, 'predict_proba'):
                predictions = self.model.predict_proba(preprocessed_data)
            else:
                predictions = self.model.predict(preprocessed_data)
            
            inference_time = (time.time() - start_time) * 1000
            self.total_inference_time += inference_time
            self.prediction_count += 1
            self.last_accessed = datetime.now()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction error for {self.model_name}: {str(e)}")
            raise
    
    def postprocess(self, predictions: Any) -> Any:
        """Postprocess predictions"""
        if self.postprocessing_func:
            return self.postprocessing_func(predictions)
        return predictions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model usage statistics"""
        avg_inference_time = (
            self.total_inference_time / self.prediction_count
            if self.prediction_count > 0 else 0.0
        )
        
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "prediction_count": self.prediction_count,
            "average_inference_time_ms": avg_inference_time,
            "total_inference_time_ms": self.total_inference_time,
            "last_accessed": self.last_accessed.isoformat(),
            "is_optimized": self.is_optimized,
            "optimization_metadata": self.optimization_metadata
        }
    
    def optimize_for_inference(self):
        """Optimize model for inference"""
        try:
            # This would implement model-specific optimizations
            # For example: ONNX conversion, TensorRT optimization, etc.
            
            logger.info(f"Optimizing model {self.model_name} for inference")
            
            # Placeholder for actual optimization logic
            self.is_optimized = True
            self.optimization_metadata = {
                "optimized_at": datetime.now().isoformat(),
                "optimization_type": "placeholder"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing model {self.model_name}: {str(e)}")


class PredictionWorker:
    """Worker for processing prediction requests"""
    
    def __init__(self, worker_id: str, model_wrapper: ModelWrapper):
        self.worker_id = worker_id
        self.model_wrapper = model_wrapper
        self.is_busy = False
        self.current_request: Optional[PredictionRequest] = None
        self.processed_requests = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        self.created_at = datetime.now()
    
    async def process_request(self, request: PredictionRequest) -> PredictionResponse:
        """Process a prediction request"""
        self.is_busy = True
        self.current_request = request
        start_time = time.time()
        
        try:
            # Preprocessing
            preprocess_start = time.time()
            preprocessed_data = self.model_wrapper.preprocess(request.input_data)
            preprocessing_time = (time.time() - preprocess_start) * 1000
            
            # Inference
            inference_start = time.time()
            predictions = self.model_wrapper.predict(preprocessed_data)
            inference_time = (time.time() - inference_start) * 1000
            
            # Postprocessing
            postprocess_start = time.time()
            final_predictions = self.model_wrapper.postprocess(predictions)
            postprocessing_time = (time.time() - postprocess_start) * 1000
            
            total_time = (time.time() - start_time) * 1000
            
            # Extract confidence scores if available
            confidence_scores = None
            if hasattr(predictions, 'shape') and len(predictions.shape) > 1:
                if predictions.shape[1] > 1:  # Multi-class probabilities
                    confidence_scores = np.max(predictions, axis=1).tolist()
            
            response = PredictionResponse(
                request_id=request.request_id,
                predictions=final_predictions.tolist() if hasattr(final_predictions, 'tolist') else final_predictions,
                model_name=self.model_wrapper.model_name,
                model_version=self.model_wrapper.model_version,
                confidence_scores=confidence_scores,
                processing_time_ms=total_time,
                preprocessing_time_ms=preprocessing_time,
                inference_time_ms=inference_time,
                postprocessing_time_ms=postprocessing_time
            )
            
            self.processed_requests += 1
            self.total_processing_time += total_time
            
            return response
            
        except Exception as e:
            self.error_count += 1
            error_response = PredictionResponse(
                request_id=request.request_id,
                predictions=[],
                model_name=self.model_wrapper.model_name,
                model_version=self.model_wrapper.model_version,
                processing_time_ms=(time.time() - start_time) * 1000,
                status="error",
                error_message=str(e)
            )
            
            logger.error(f"Worker {self.worker_id} error processing request {request.request_id}: {str(e)}")
            return error_response
            
        finally:
            self.is_busy = False
            self.current_request = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        avg_processing_time = (
            self.total_processing_time / self.processed_requests
            if self.processed_requests > 0 else 0.0
        )
        
        error_rate = (
            self.error_count / (self.processed_requests + self.error_count)
            if (self.processed_requests + self.error_count) > 0 else 0.0
        )
        
        return {
            "worker_id": self.worker_id,
            "is_busy": self.is_busy,
            "processed_requests": self.processed_requests,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "average_processing_time_ms": avg_processing_time,
            "total_processing_time_ms": self.total_processing_time,
            "uptime_seconds": (datetime.now() - self.created_at).total_seconds(),
            "current_request_id": self.current_request.request_id if self.current_request else None
        }


class AutoScaler:
    """Auto-scaling logic for model serving"""
    
    def __init__(
        self,
        min_workers: int = 1,
        max_workers: int = 10,
        target_cpu_utilization: float = 70.0,
        target_latency_ms: float = 100.0,
        scale_up_threshold: float = 80.0,
        scale_down_threshold: float = 40.0,
        scaling_strategy: ScalingStrategy = ScalingStrategy.HYBRID
    ):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.target_cpu_utilization = target_cpu_utilization
        self.target_latency_ms = target_latency_ms
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.scaling_strategy = scaling_strategy
        self.last_scaling_action = datetime.now()
        self.scaling_cooldown = timedelta(minutes=2)  # Prevent rapid scaling
        
    def should_scale(self, current_workers: int, metrics: ServingMetrics) -> Tuple[bool, int]:
        """Determine if scaling is needed and return desired worker count"""
        
        # Check cooldown period
        if datetime.now() - self.last_scaling_action < self.scaling_cooldown:
            return False, current_workers
        
        desired_workers = current_workers
        scale_needed = False
        
        if self.scaling_strategy == ScalingStrategy.CPU_BASED:
            if metrics.cpu_usage > self.scale_up_threshold and current_workers < self.max_workers:
                desired_workers = min(current_workers + 1, self.max_workers)
                scale_needed = True
            elif metrics.cpu_usage < self.scale_down_threshold and current_workers > self.min_workers:
                desired_workers = max(current_workers - 1, self.min_workers)
                scale_needed = True
                
        elif self.scaling_strategy == ScalingStrategy.LATENCY_BASED:
            if metrics.average_latency_ms > self.target_latency_ms * 1.5 and current_workers < self.max_workers:
                desired_workers = min(current_workers + 1, self.max_workers)
                scale_needed = True
            elif metrics.average_latency_ms < self.target_latency_ms * 0.5 and current_workers > self.min_workers:
                desired_workers = max(current_workers - 1, self.min_workers)
                scale_needed = True
                
        elif self.scaling_strategy == ScalingStrategy.THROUGHPUT_BASED:
            # Scale based on queue size and request rate
            if metrics.queue_size > current_workers * 5 and current_workers < self.max_workers:
                desired_workers = min(current_workers + 1, self.max_workers)
                scale_needed = True
            elif metrics.queue_size < current_workers and current_workers > self.min_workers:
                desired_workers = max(current_workers - 1, self.min_workers)
                scale_needed = True
                
        elif self.scaling_strategy == ScalingStrategy.HYBRID:
            # Combine multiple factors
            scale_factors = []
            
            # CPU factor
            if metrics.cpu_usage > self.scale_up_threshold:
                scale_factors.append(1)  # Scale up
            elif metrics.cpu_usage < self.scale_down_threshold:
                scale_factors.append(-1)  # Scale down
            else:
                scale_factors.append(0)  # No change
            
            # Latency factor
            if metrics.average_latency_ms > self.target_latency_ms * 1.5:
                scale_factors.append(1)
            elif metrics.average_latency_ms < self.target_latency_ms * 0.5:
                scale_factors.append(-1)
            else:
                scale_factors.append(0)
            
            # Queue factor
            if metrics.queue_size > current_workers * 3:
                scale_factors.append(1)
            elif metrics.queue_size == 0 and current_workers > self.min_workers:
                scale_factors.append(-1)
            else:
                scale_factors.append(0)
            
            # Make decision based on majority
            scale_decision = sum(scale_factors)
            if scale_decision >= 2 and current_workers < self.max_workers:
                desired_workers = min(current_workers + 1, self.max_workers)
                scale_needed = True
            elif scale_decision <= -2 and current_workers > self.min_workers:
                desired_workers = max(current_workers - 1, self.min_workers)
                scale_needed = True
        
        if scale_needed:
            self.last_scaling_action = datetime.now()
            logger.info(f"Auto-scaling: {current_workers} -> {desired_workers} workers")
        
        return scale_needed, desired_workers


class HighPerformanceModelServer:
    """High-performance model serving system with auto-scaling"""
    
    def __init__(
        self,
        serve_mode: ServeMode = ServeMode.ASYNCHRONOUS,
        auto_scaler: Optional[AutoScaler] = None,
        batch_size: int = 32,
        batch_timeout_ms: float = 100.0,
        enable_model_optimization: bool = True
    ):
        self.serve_mode = serve_mode
        self.auto_scaler = auto_scaler or AutoScaler()
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self.enable_model_optimization = enable_model_optimization
        
        # Model management
        self.models: Dict[str, ModelWrapper] = {}
        self.workers: Dict[str, PredictionWorker] = {}
        
        # Request handling
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.batch_queue: List[PredictionRequest] = []
        self.batch_timer = None
        
        # Metrics and monitoring
        self.metrics_history: List[ServingMetrics] = []
        self.request_times: List[float] = []
        self.error_count = 0
        self.total_requests = 0
        
        # Server state
        self.is_running = False
        self.server_start_time = None
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.auto_scaler.max_workers)
        
    def register_model(
        self,
        model: Any,
        model_name: str,
        model_version: str,
        preprocessing_func: Optional[Callable] = None,
        postprocessing_func: Optional[Callable] = None
    ) -> bool:
        """Register a model for serving"""
        try:
            model_wrapper = ModelWrapper(
                model, model_name, model_version,
                preprocessing_func, postprocessing_func
            )
            
            if self.enable_model_optimization:
                model_wrapper.optimize_for_inference()
            
            model_key = f"{model_name}:{model_version}"
            self.models[model_key] = model_wrapper
            
            logger.info(f"Registered model {model_name} v{model_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering model {model_name}: {str(e)}")
            return False
    
    def unregister_model(self, model_name: str, model_version: str) -> bool:
        """Unregister a model"""
        model_key = f"{model_name}:{model_version}"
        if model_key in self.models:
            del self.models[model_key]
            logger.info(f"Unregistered model {model_name} v{model_version}")
            return True
        return False
    
    async def start_server(self):
        """Start the model serving server"""
        if self.is_running:
            logger.warning("Server is already running")
            return
        
        self.is_running = True
        self.server_start_time = datetime.now()
        
        # Initialize workers
        await self._scale_workers(self.auto_scaler.min_workers)
        
        # Start request processing loop
        processing_task = asyncio.create_task(self._request_processing_loop())
        
        # Start metrics collection
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        
        # Start auto-scaling
        scaling_task = asyncio.create_task(self._auto_scaling_loop())
        
        logger.info("High-performance model server started")
        
        try:
            await asyncio.gather(processing_task, metrics_task, scaling_task)
        except asyncio.CancelledError:
            logger.info("Server tasks cancelled")
    
    async def stop_server(self):
        try:
            logger.info(f"Executing stop_server")
            
            # Implementation for stop_server
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"stop_server completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"stop_server failed: {e}")
            raise
    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Make a prediction"""
        if not self.is_running:
            return PredictionResponse(
                request_id=request.request_id,
                predictions=[],
                model_name=request.model_name,
                model_version="unknown",
                status="error",
                error_message="Server is not running"
            )
        
        self.total_requests += 1
        
        if self.serve_mode == ServeMode.BATCH:
            return await self._handle_batch_request(request)
        else:
            return await self._handle_single_request(request)
    
    async def _handle_single_request(self, request: PredictionRequest) -> PredictionResponse:
        """Handle a single prediction request"""
        # Find available worker
        available_worker = None
        for worker in self.workers.values():
            if not worker.is_busy:
                available_worker = worker
                break
        
        if not available_worker:
            # All workers busy, queue the request
            await self.request_queue.put(request)
            
            # Wait for processing (with timeout)
            start_wait = time.time()
            while (time.time() - start_wait) < request.timeout_seconds:
                if not await self.request_queue.empty():
                    await asyncio.sleep(0.01)
                else:
                    break
            
            # Try to find a worker again
            for worker in self.workers.values():
                if not worker.is_busy:
                    available_worker = worker
                    break
        
        if available_worker:
            return await available_worker.process_request(request)
        else:
            self.error_count += 1
            return PredictionResponse(
                request_id=request.request_id,
                predictions=[],
                model_name=request.model_name,
                model_version="unknown",
                status="error",
                error_message="No available workers (timeout)"
            )
    
    async def _handle_batch_request(self, request: PredictionRequest) -> PredictionResponse:
        """Handle batched prediction requests"""
        self.batch_queue.append(request)
        
        # Process batch if conditions are met
        if (len(self.batch_queue) >= self.batch_size or 
            self._should_process_batch()):
            return await self._process_batch()
        
        # Wait for batch to be processed
        start_wait = time.time()
        while request in self.batch_queue and (time.time() - start_wait) < request.timeout_seconds:
            await asyncio.sleep(0.01)
        
        # This is a simplified implementation
        # In reality, you'd need a more sophisticated batch coordination system
        return PredictionResponse(
            request_id=request.request_id,
            predictions=[],
            model_name=request.model_name,
            model_version="unknown",
            status="error",
            error_message="Batch processing timeout"
        )
    
    def _should_process_batch(self) -> bool:
        """Determine if batch should be processed based on timeout"""
        if not self.batch_queue:
            return False
        
        oldest_request = min(self.batch_queue, key=lambda r: r.created_at)
        age_ms = (datetime.now() - oldest_request.created_at).total_seconds() * 1000
        
        return age_ms >= self.batch_timeout_ms
    
    async def _process_batch(self) -> PredictionResponse:
        """Process a batch of requests"""
        if not self.batch_queue:
            return None
        
        batch = self.batch_queue[:self.batch_size]
        self.batch_queue = self.batch_queue[self.batch_size:]
        
        # Simplified batch processing
        # In reality, you'd combine inputs and process them together
        results = []
        for request in batch:
            result = await self._handle_single_request(request)
            results.append(result)
        
        return results[0] if results else None
    
    async def _request_processing_loop(self):
        """Main request processing loop"""
        while self.is_running:
            try:
                # Process queued requests
                while not self.request_queue.empty():
                    request = await self.request_queue.get()
                    
                    # Find available worker
                    available_worker = None
                    for worker in self.workers.values():
                        if not worker.is_busy:
                            available_worker = worker
                            break
                    
                    if available_worker:
                        # Process request asynchronously
                        asyncio.create_task(available_worker.process_request(request))
                
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in request processing loop: {str(e)}")
                await asyncio.sleep(1)
    
    async def _metrics_collection_loop(self):
        """Collect and store performance metrics"""
        while self.is_running:
            try:
                metrics = self._calculate_current_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics (last hour)
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                await asyncio.sleep(10)  # Collect metrics every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {str(e)}")
                await asyncio.sleep(10)
    
    async def _auto_scaling_loop(self):
        """Auto-scaling loop"""
        while self.is_running:
            try:
                if self.metrics_history:
                    current_metrics = self.metrics_history[-1]
                    current_worker_count = len(self.workers)
                    
                    should_scale, desired_workers = self.auto_scaler.should_scale(
                        current_worker_count, current_metrics
                    )
                    
                    if should_scale:
                        await self._scale_workers(desired_workers)
                
                await asyncio.sleep(30)  # Check scaling every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in auto-scaling loop: {str(e)}")
                await asyncio.sleep(30)
    
    def _calculate_current_metrics(self) -> ServingMetrics:
        """Calculate current serving metrics"""
        # Recent request times (last 5 minutes)
        cutoff_time = time.time() - 300
        recent_times = [t for t in self.request_times if t > cutoff_time]
        
        # Calculate RPS
        rps = len(recent_times) / 300 if recent_times else 0.0
        
        # Calculate latency metrics
        recent_latencies = []
        for worker in self.workers.values():
            if worker.processed_requests > 0:
                avg_latency = worker.total_processing_time / worker.processed_requests
                recent_latencies.append(avg_latency)
        
        avg_latency = np.mean(recent_latencies) if recent_latencies else 0.0
        p95_latency = np.percentile(recent_latencies, 95) if recent_latencies else 0.0
        p99_latency = np.percentile(recent_latencies, 99) if recent_latencies else 0.0
        
        # Calculate error rate
        total_errors = sum(worker.error_count for worker in self.workers.values())
        total_processed = sum(worker.processed_requests for worker in self.workers.values())
        error_rate = total_errors / max(total_processed + total_errors, 1)
        
        # System metrics
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_usage_mb = memory_info.used / (1024 * 1024)
        
        # Queue metrics
        queue_size = self.request_queue.qsize()
        active_workers = sum(1 for worker in self.workers.values() if worker.is_busy)
        
        return ServingMetrics(
            requests_per_second=rps,
            average_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            memory_usage_mb=memory_usage_mb,
            queue_size=queue_size,
            active_workers=active_workers
        )
    
    async def _scale_workers(self, desired_count: int):
        """Scale workers to desired count"""
        current_count = len(self.workers)
        
        if desired_count > current_count:
            # Scale up
            for i in range(desired_count - current_count):
                await self._add_worker()
        elif desired_count < current_count:
            # Scale down
            for i in range(current_count - desired_count):
                await self._remove_worker()
    
    async def _add_worker(self):
        """Add a new worker"""
        if not self.models:
            logger.warning("No models registered, cannot add worker")
            return
        
        # Use the first available model (in a real system, you'd have more sophisticated logic)
        model_wrapper = list(self.models.values())[0]
        
        worker_id = f"worker_{len(self.workers)}_{int(time.time())}"
        worker = PredictionWorker(worker_id, model_wrapper)
        
        self.workers[worker_id] = worker
        logger.info(f"Added worker {worker_id}")
    
    async def _remove_worker(self):
        """Remove a worker"""
        if not self.workers:
            return
        
        # Remove the least busy worker
        worker_to_remove = None
        for worker in self.workers.values():
            if not worker.is_busy:
                worker_to_remove = worker
                break
        
        if worker_to_remove:
            del self.workers[worker_to_remove.worker_id]
            logger.info(f"Removed worker {worker_to_remove.worker_id}")
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get comprehensive server statistics"""
        uptime = (datetime.now() - self.server_start_time).total_seconds() if self.server_start_time else 0
        
        # Worker stats
        worker_stats = [worker.get_stats() for worker in self.workers.values()]
        
        # Model stats
        model_stats = {key: model.get_stats() for key, model in self.models.items()}
        
        # Recent metrics
        recent_metrics = self.metrics_history[-10:] if self.metrics_history else []
        
        return {
            "server_info": {
                "is_running": self.is_running,
                "uptime_seconds": uptime,
                "serve_mode": self.serve_mode.value,
                "total_requests": self.total_requests,
                "total_errors": self.error_count
            },
            "workers": {
                "count": len(self.workers),
                "active": sum(1 for w in self.workers.values() if w.is_busy),
                "stats": worker_stats
            },
            "models": {
                "count": len(self.models),
                "stats": model_stats
            },
            "auto_scaler": {
                "min_workers": self.auto_scaler.min_workers,
                "max_workers": self.auto_scaler.max_workers,
                "strategy": self.auto_scaler.scaling_strategy.value
            },
            "recent_metrics": [m.__dict__ for m in recent_metrics],
            "queue_size": self.request_queue.qsize()
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
        
        # Force garbage collection
        gc.collect()