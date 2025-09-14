"""
Inference Queue Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🚀 **Inference Queue Manager - Enterprise ML Request Orchestration**

**Author:** Fahed Mlaiel (mlaiel@live.de) - Backend Senior  
**Copyright:** © 2025 Fahed Mlaiel. All rights reserved.  
**Version:** 1.0.0  
**Created:** January 2025

**⚠️ WARNING:** This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly prohibited.

---

## 🎯 **ROLE: BACKEND SENIOR - INFRASTRUCTURE SCALABILITY MASTERY**

Enterprise-grade inference request queue management with intelligent scheduling,
priority handling, load balancing, and creator-specific optimization strategies.
"""

import asyncio
import uuid
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import heapq
from collections import defaultdict, deque
import logging

import redis.asyncio as redis
import aiohttp
from prometheus_client import Counter, Histogram, Gauge

# Monitoring metrics
inference_requests_total = Counter('inference_requests_total', 'Total inference requests', ['model_id', 'priority', 'creator_type'])
inference_duration = Histogram('inference_duration_seconds', 'Inference duration', ['model_id', 'creator_type'])
queue_size = Gauge('inference_queue_size', 'Current queue size', ['model_id', 'priority'])
active_workers = Gauge('inference_active_workers', 'Active workers', ['model_id'])

class RequestPriority(Enum):
    """Request priority levels"""
    CRITICAL = 1    # Real-time user interactions
    HIGH = 2        # Important creator workflows  
    NORMAL = 3      # Standard processing
    LOW = 4         # Batch/background tasks
    BULK = 5        # Large batch operations

class RequestStatus(Enum):
    """Request processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class CreatorType(Enum):
    """Creator specialization for request handling"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERIC = "generic"

@dataclass
class InferenceRequest:
    """Inference request specification"""
    request_id: str
    model_id: str
    data: Dict[str, Any]
    priority: RequestPriority
    creator_type: CreatorType
    creator_id: Optional[str] = None
    callback_url: Optional[str] = None
    timeout: int = 30  # seconds
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None
    expires_at: datetime = None
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.timeout * 2)
        if self.metadata is None:
            self.metadata = {}

@dataclass
class QueueStats:
    """Queue statistics"""
    total_requests: int
    queued_requests: int
    processing_requests: int
    completed_requests: int
    failed_requests: int
    average_wait_time: float
    average_processing_time: float
    throughput_per_second: float
    queue_size_by_priority: Dict[RequestPriority, int]
    active_workers: int

class InferenceQueueManager:
    """
    🚀 **Enterprise Inference Queue Manager**
    
    **Backend Senior Role:** High-performance request orchestration
    - Priority-based queue management with intelligent scheduling
    - Multi-model concurrent processing with resource optimization
    - Creator-specific SLA guarantees and optimization
    - Auto-scaling integration with load-based triggers
    - Circuit breaker pattern for resilience
    - Comprehensive monitoring and alerting
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Redis configuration for distributed queuing
        self.redis_url = config.get('redis_url', 'redis://localhost:6379/0')
        self.redis_client = None
        
        # Queue configuration
        self.max_queue_size = config.get('max_queue_size', 10000)
        self.default_timeout = config.get('default_timeout', 30)
        self.worker_pool_size = config.get('worker_pool_size', 10)
        
        # Priority queues (in-memory for fast access)
        self.priority_queues = {
            priority: deque() for priority in RequestPriority
        }
        
        # Request tracking
        self.active_requests: Dict[str, InferenceRequest] = {}
        self.processing_requests: Dict[str, InferenceRequest] = {}
        self.completed_requests: Dict[str, Dict[str, Any]] = {}
        
        # Worker management
        self.worker_tasks: List[asyncio.Task] = []
        self.worker_semaphore = asyncio.Semaphore(self.worker_pool_size)
        self.shutdown_event = asyncio.Event()
        
        # Creator-specific configurations
        self.creator_configs = {
            CreatorType.MUSICIAN: {
                'max_concurrent': 5,
                'timeout_multiplier': 2.0,  # Longer timeout for audio processing
                'priority_boost': 1,  # Boost priority by 1 level
                'sla_target_ms': 5000
            },
            CreatorType.PHOTOGRAPHER: {
                'max_concurrent': 3,
                'timeout_multiplier': 1.5,  # Image processing
                'priority_boost': 0,
                'sla_target_ms': 3000
            },
            CreatorType.BLOGGER: {
                'max_concurrent': 10,
                'timeout_multiplier': 0.5,  # Text processing is faster
                'priority_boost': 0,
                'sla_target_ms': 1000
            },
            CreatorType.INFLUENCER: {
                'max_concurrent': 8,
                'timeout_multiplier': 1.2,
                'priority_boost': 1,
                'sla_target_ms': 2000
            },
            CreatorType.COMEDIAN: {
                'max_concurrent': 6,
                'timeout_multiplier': 1.0,
                'priority_boost': 0,
                'sla_target_ms': 1500
            }
        }
        
        # Circuit breaker for model endpoints
        self.circuit_breakers = {}
        
        # Statistics
        self.stats = {
            'requests_processed': 0,
            'requests_failed': 0,
            'total_processing_time': 0,
            'start_time': time.time()
        }
    
    async def initialize(self) -> None:
        """Initialize the queue manager"""
        # Connect to Redis
        self.redis_client = redis.from_url(self.redis_url)
        await self.redis_client.ping()
        
        # Start background tasks
        await self._start_workers()
        await self._start_cleanup_task()
        await self._start_metrics_task()
        
        self.logger.info(f"InferenceQueueManager initialized with {self.worker_pool_size} workers")
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.shutdown_event.set()
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("InferenceQueueManager shutdown complete")
    
    async def submit_request(
        self, 
        model_id: str,
        data: Dict[str, Any],
        priority: RequestPriority = RequestPriority.NORMAL,
        creator_type: CreatorType = CreatorType.GENERIC,
        creator_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit inference request to queue
        
        **Backend Senior Expertise:**
        - Intelligent priority assignment based on creator type
        - Request validation and preprocessing
        - Queue overflow protection
        - SLA-based timeout calculation
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Apply creator-specific configurations
        creator_config = self.creator_configs.get(creator_type, {})
        
        # Adjust priority based on creator type
        adjusted_priority = priority
        priority_boost = creator_config.get('priority_boost', 0)
        if priority_boost > 0:
            new_priority_value = max(1, priority.value - priority_boost)
            adjusted_priority = RequestPriority(new_priority_value)
        
        # Calculate timeout with creator multiplier
        if timeout is None:
            timeout = self.default_timeout
        timeout_multiplier = creator_config.get('timeout_multiplier', 1.0)
        adjusted_timeout = int(timeout * timeout_multiplier)
        
        # Create request object
        request = InferenceRequest(
            request_id=request_id,
            model_id=model_id,
            data=data,
            priority=adjusted_priority,
            creator_type=creator_type,
            creator_id=creator_id,
            callback_url=callback_url,
            timeout=adjusted_timeout,
            metadata=metadata or {}
        )
        
        # Validate request
        await self._validate_request(request)
        
        # Check queue capacity
        current_queue_size = sum(len(q) for q in self.priority_queues.values())
        if current_queue_size >= self.max_queue_size:
            raise Exception("Queue is at maximum capacity")
        
        # Add to priority queue
        self.priority_queues[adjusted_priority].append(request)
        self.active_requests[request_id] = request
        
        # Store in Redis for persistence
        await self._persist_request(request)
        
        # Update metrics
        inference_requests_total.labels(
            model_id=model_id,
            priority=adjusted_priority.name,
            creator_type=creator_type.value
        ).inc()
        
        queue_size.labels(
            model_id=model_id,
            priority=adjusted_priority.name
        ).set(len(self.priority_queues[adjusted_priority]))
        
        self.logger.info(f"Request {request_id} submitted to queue with priority {adjusted_priority.name}")
        return request_id
    
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get request status and details"""
        # Check active requests
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            status = RequestStatus.QUEUED
            if request_id in self.processing_requests:
                status = RequestStatus.PROCESSING
            
            return {
                "request_id": request_id,
                "status": status.value,
                "created_at": request.created_at.isoformat(),
                "updated_at": request.updated_at.isoformat(),
                "priority": request.priority.name,
                "creator_type": request.creator_type.value,
                "model_id": request.model_id,
                "retry_count": request.retry_count,
                "estimated_wait_time": await self._estimate_wait_time(request)
            }
        
        # Check completed requests
        if request_id in self.completed_requests:
            return self.completed_requests[request_id]
        
        # Check Redis for historical data
        redis_data = await self.redis_client.get(f"request:{request_id}")
        if redis_data:
            return json.loads(redis_data)
        
        raise Exception(f"Request {request_id} not found")
    
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel a queued request"""
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            
            # Remove from priority queue
            try:
                self.priority_queues[request.priority].remove(request)
            except ValueError:
                pass  # Already removed or processing
            
            # Remove from tracking
            del self.active_requests[request_id]
            
            # Update status
            result = {
                "request_id": request_id,
                "status": RequestStatus.CANCELLED.value,
                "cancelled_at": datetime.utcnow().isoformat(),
                "message": "Request cancelled by user"
            }
            
            self.completed_requests[request_id] = result
            await self._persist_result(request_id, result)
            
            self.logger.info(f"Request {request_id} cancelled")
            return True
        
        return False
    
    async def get_queue_stats(self) -> QueueStats:
        """Get comprehensive queue statistics"""
        queue_size_by_priority = {
            priority: len(queue) for priority, queue in self.priority_queues.items()
        }
        
        total_requests = sum(queue_size_by_priority.values())
        processing_count = len(self.processing_requests)
        
        # Calculate averages
        current_time = time.time()
        uptime = current_time - self.stats['start_time']
        
        avg_processing_time = 0
        if self.stats['requests_processed'] > 0:
            avg_processing_time = self.stats['total_processing_time'] / self.stats['requests_processed']
        
        throughput = self.stats['requests_processed'] / uptime if uptime > 0 else 0
        
        return QueueStats(
            total_requests=len(self.active_requests) + len(self.completed_requests),
            queued_requests=total_requests,
            processing_requests=processing_count,
            completed_requests=len(self.completed_requests),
            failed_requests=self.stats['requests_failed'],
            average_wait_time=await self._calculate_average_wait_time(),
            average_processing_time=avg_processing_time,
            throughput_per_second=throughput,
            queue_size_by_priority=queue_size_by_priority,
            active_workers=len([task for task in self.worker_tasks if not task.done()])
        )
    
    async def _validate_request(self, request -> None: InferenceRequest) -> None:
        """Validate inference request"""
        # Basic validation
        if not request.model_id:
            raise ValueError("Model ID is required")
        
        if not request.data:
            raise ValueError("Request data is required")
        
        # Creator-specific validation
        creator_config = self.creator_configs.get(request.creator_type, {})
        
        # Check if we're at creator concurrency limit
        creator_processing = sum(
            1 for req in self.processing_requests.values()
            if req.creator_type == request.creator_type
        )
        
        max_concurrent = creator_config.get('max_concurrent', float('inf'))
        if creator_processing >= max_concurrent:
            raise Exception(f"Maximum concurrent requests exceeded for {request.creator_type.value}")
        
        # Model-specific validation
        if await self._is_circuit_breaker_open(request.model_id):
            raise Exception(f"Circuit breaker is open for model {request.model_id}")
    
    async def _persist_request(self, request -> None: InferenceRequest) -> None:
        """Persist request to Redis"""
        request_data = {
            "request_id": request.request_id,
            "model_id": request.model_id,
            "data": request.data,
            "priority": request.priority.name,
            "creator_type": request.creator_type.value,
            "creator_id": request.creator_id,
            "status": RequestStatus.QUEUED.value,
            "created_at": request.created_at.isoformat(),
            "timeout": request.timeout,
            "metadata": request.metadata
        }
        
        await self.redis_client.setex(
            f"request:{request.request_id}",
            timedelta(hours=24),  # Keep for 24 hours
            json.dumps(request_data)
        )
    
    async def _persist_result(self, request_id -> None: str, result -> None: Dict[str, Any]) -> None:
        """Persist result to Redis"""
        await self.redis_client.setex(
            f"result:{request_id}",
            timedelta(hours=24),
            json.dumps(result)
        )
    
    async def _start_workers(self) -> None:
        """Start worker tasks"""
        for i in range(self.worker_pool_size):
            task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.worker_tasks.append(task)
    
    async def _worker_loop(self, worker_id -> None: str) -> None:
        """
        Main worker loop for processing requests
        
        **Backend Senior Excellence:** Optimized worker processing
        """
        self.logger.info(f"Worker {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get next request with priority
                request = await self._get_next_request()
                
                if request is None:
                    await asyncio.sleep(0.1)  # No requests available
                    continue
                
                # Acquire semaphore
                async with self.worker_semaphore:
                    await self._process_request(request, worker_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying
        
        self.logger.info(f"Worker {worker_id} stopped")
    
    async def _get_next_request(self) -> Optional[InferenceRequest]:
        """Get next request based on priority"""
        # Check expired requests first
        await self._cleanup_expired_requests()
        
        # Get highest priority request
        for priority in RequestPriority:
            queue = self.priority_queues[priority]
            if queue:
                request = queue.popleft()
                
                # Check if request is still valid
                if request.request_id in self.active_requests:
                    return request
        
        return None
    
    async def _process_request(self, request -> None: InferenceRequest, worker_id -> None: str) -> None:
        """
        Process individual inference request
        
        **Backend Senior Mastery:** High-performance request processing
        """
        start_time = time.time()
        request_id = request.request_id
        
        try:
            # Move to processing
            self.processing_requests[request_id] = request
            request.updated_at = datetime.utcnow()
            
            self.logger.info(f"Worker {worker_id} processing request {request_id}")
            
            # Call model inference API
            result = await self._call_model_inference(request)
            
            # Success - update metrics and store result
            processing_time = time.time() - start_time
            
            self.stats['requests_processed'] += 1
            self.stats['total_processing_time'] += processing_time
            
            inference_duration.labels(
                model_id=request.model_id,
                creator_type=request.creator_type.value
            ).observe(processing_time)
            
            # Store successful result
            result_data = {
                "request_id": request_id,
                "status": RequestStatus.COMPLETED.value,
                "result": result,
                "processing_time": processing_time,
                "completed_at": datetime.utcnow().isoformat(),
                "worker_id": worker_id
            }
            
            self.completed_requests[request_id] = result_data
            await self._persist_result(request_id, result_data)
            
            # Send callback if configured
            if request.callback_url:
                await self._send_callback(request.callback_url, result_data)
            
            self.logger.info(f"Request {request_id} completed in {processing_time:.2f}s")
            
        except asyncio.TimeoutError:
            await self._handle_request_timeout(request, worker_id)
        except Exception as e:
            await self._handle_request_error(request, worker_id, e)
        finally:
            # Clean up
            self.processing_requests.pop(request_id, None)
            self.active_requests.pop(request_id, None)
            
            # Update queue size metrics
            queue_size.labels(
                model_id=request.model_id,
                priority=request.priority.name
            ).set(len(self.priority_queues[request.priority]))
    
    async def _call_model_inference(self, request: InferenceRequest) -> Dict[str, Any]:
        """Call the actual model inference API"""
        # Construct inference endpoint URL
        inference_url = f"{self.config.get('inference_base_url', 'http://localhost:8000')}/models/{request.model_id}/predict"
        
        # Prepare request payload
        payload = {
            "data": request.data,
            "options": {
                "request_id": request.request_id,
                "creator_type": request.creator_type.value,
                "priority": request.priority.name
            }
        }
        
        # Add creator-specific options
        creator_config = self.creator_configs.get(request.creator_type, {})
        if creator_config:
            payload["options"]["creator_config"] = creator_config
        
        timeout = aiohttp.ClientTimeout(total=request.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(inference_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    await self._record_circuit_breaker_success(request.model_id)
                    return result
                else:
                    error_msg = f"Model inference failed with status {response.status}"
                    await self._record_circuit_breaker_failure(request.model_id)
                    raise Exception(error_msg)
    
    async def _handle_request_timeout(self, request -> None: InferenceRequest, worker_id -> None: str) -> None:
        """Handle request timeout"""
        self.logger.warning(f"Request {request.request_id} timed out in worker {worker_id}")
        
        result_data = {
            "request_id": request.request_id,
            "status": RequestStatus.TIMEOUT.value,
            "error": f"Request timed out after {request.timeout} seconds",
            "failed_at": datetime.utcnow().isoformat(),
            "worker_id": worker_id
        }
        
        self.completed_requests[request.request_id] = result_data
        await self._persist_result(request.request_id, result_data)
        
        self.stats['requests_failed'] += 1
        await self._record_circuit_breaker_failure(request.model_id)
    
    async def _handle_request_error(self, request -> None: InferenceRequest, worker_id -> None: str, error -> None: Exception) -> None:
        """Handle request processing error with retry logic"""
        self.logger.error(f"Request {request.request_id} failed in worker {worker_id}: {error}")
        
        # Check if we should retry
        if request.retry_count < request.max_retries:
            request.retry_count += 1
            request.updated_at = datetime.utcnow()
            
            # Re-queue with exponential backoff
            await asyncio.sleep(2 ** request.retry_count)
            self.priority_queues[request.priority].append(request)
            
            self.logger.info(f"Request {request.request_id} queued for retry {request.retry_count}")
            return
        
        # Max retries reached - mark as failed
        result_data = {
            "request_id": request.request_id,
            "status": RequestStatus.FAILED.value,
            "error": str(error),
            "retry_count": request.retry_count,
            "failed_at": datetime.utcnow().isoformat(),
            "worker_id": worker_id
        }
        
        self.completed_requests[request.request_id] = result_data
        await self._persist_result(request.request_id, result_data)
        
        self.stats['requests_failed'] += 1
        await self._record_circuit_breaker_failure(request.model_id)
    
    async def _send_callback(self, callback_url -> None: str, result_data -> None: Dict[str, Any]) -> None:
        """Send result callback"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(callback_url, json=result_data) as response:
                    if response.status != 200:
                        self.logger.warning(f"Callback to {callback_url} failed with status {response.status}")
        except Exception as e:
            self.logger.error(f"Callback to {callback_url} failed: {e}")
    
    async def _cleanup_expired_requests(self) -> None:
        """Clean up expired requests"""
        current_time = datetime.utcnow()
        expired_requests = []
        
        for request_id, request in self.active_requests.items():
            if current_time > request.expires_at:
                expired_requests.append(request_id)
        
        for request_id in expired_requests:
            await self.cancel_request(request_id)
    
    async def _start_cleanup_task(self) -> None:
        """Start periodic cleanup task"""
        async def cleanup_loop() -> None:
            while not self.shutdown_event.is_set():
                await self._cleanup_expired_requests()
                await asyncio.sleep(60)  # Run every minute
        
        task = asyncio.create_task(cleanup_loop())
        self.worker_tasks.append(task)
    
    async def _start_metrics_task(self) -> None:
        """Start metrics collection task"""
        async def metrics_loop() -> None:
            while not self.shutdown_event.is_set():
                # Update active workers metric
                active_count = len([task for task in self.worker_tasks if not task.done()])
                active_workers.labels(model_id="all").set(active_count)
                
                await asyncio.sleep(10)  # Update every 10 seconds
        
        task = asyncio.create_task(metrics_loop())
        self.worker_tasks.append(task)
    
    async def _estimate_wait_time(self, request: InferenceRequest) -> float:
        """Estimate wait time for request"""
        # Count requests ahead in queue with same or higher priority
        requests_ahead = 0
        for priority in RequestPriority:
            if priority.value <= request.priority.value:
                requests_ahead += len(self.priority_queues[priority])
        
        # Estimate based on average processing time and active workers
        avg_processing_time = 1.0  # Default 1 second
        if self.stats['requests_processed'] > 0:
            avg_processing_time = self.stats['total_processing_time'] / self.stats['requests_processed']
        
        active_workers_count = len([task for task in self.worker_tasks if not task.done()])
        if active_workers_count == 0:
            active_workers_count = 1
        
        estimated_wait = (requests_ahead * avg_processing_time) / active_workers_count
        return max(0, estimated_wait)
    
    async def _calculate_average_wait_time(self) -> float:
        """Calculate average wait time across all requests"""
        # This would typically be calculated from historical data
        # For now, return a simple estimate
        total_queued = sum(len(q) for q in self.priority_queues.values())
        if total_queued == 0:
            return 0
        
        avg_processing_time = 1.0
        if self.stats['requests_processed'] > 0:
            avg_processing_time = self.stats['total_processing_time'] / self.stats['requests_processed']
        
        return total_queued * avg_processing_time / self.worker_pool_size
    
    # Circuit Breaker implementation
    async def _is_circuit_breaker_open(self, model_id: str) -> bool:
        """Check if circuit breaker is open for model"""
        breaker = self.circuit_breakers.get(model_id, {'failures': 0, 'last_failure': None, 'state': 'closed'})
        
        # If closed, allow requests
        if breaker['state'] == 'closed':
            return False
        
        # If open, check if we should try again (half-open)
        if breaker['state'] == 'open':
            if breaker['last_failure']:
                time_since_failure = time.time() - breaker['last_failure']
                if time_since_failure > 60:  # Try again after 1 minute
                    breaker['state'] = 'half-open'
                    self.circuit_breakers[model_id] = breaker
                    return False
            return True
        
        # Half-open state - allow limited requests
        return False
    
    async def _record_circuit_breaker_success(self, model_id -> None: str) -> None:
        """Record successful request for circuit breaker"""
        breaker = self.circuit_breakers.get(model_id, {'failures': 0, 'last_failure': None, 'state': 'closed'})
        breaker['failures'] = 0
        breaker['state'] = 'closed'
        self.circuit_breakers[model_id] = breaker
    
    async def _record_circuit_breaker_failure(self, model_id -> None: str) -> None:
        """Record failed request for circuit breaker"""
        breaker = self.circuit_breakers.get(model_id, {'failures': 0, 'last_failure': None, 'state': 'closed'})
        breaker['failures'] += 1
        breaker['last_failure'] = time.time()
        
        # Open circuit if too many failures
        if breaker['failures'] >= 5:
            breaker['state'] = 'open'
            self.logger.warning(f"Circuit breaker opened for model {model_id}")
        
        self.circuit_breakers[model_id] = breaker

# Usage example
async def main() -> None:
    """Example usage of InferenceQueueManager"""
    config = {
        'redis_url': 'redis://localhost:6379/0',
        'worker_pool_size': 5,
        'max_queue_size': 1000,
        'inference_base_url': 'http://localhost:8000'
    }
    
    queue_manager = InferenceQueueManager(config)
    await queue_manager.initialize()
    
    try:
        # Submit a request
        request_id = await queue_manager.submit_request(
            model_id="musician_audio_classifier",
            data={"audio_data": "base64_encoded_audio"},
            priority=RequestPriority.HIGH,
            creator_type=CreatorType.MUSICIAN,
            creator_id="musician_123"
        )
        
        print(f"Request submitted: {request_id}")
        
        # Check status
        status = await queue_manager.get_request_status(request_id)
        print(f"Request status: {status}")
        
        # Get queue stats
        stats = await queue_manager.get_queue_stats()
        print(f"Queue stats: {stats}")
        
        # Wait a bit for processing
        await asyncio.sleep(5)
        
    finally:
        await queue_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())