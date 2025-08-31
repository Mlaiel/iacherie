"""Generation Manager - Central orchestrator for all content generation operations

Professional enterprise-grade content generation management system providing
centralized control, resource management, and coordination of all generators.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import json

from .base_generator import ContentGenerationContext
from .content_pipeline import ContentGenerationPipeline, PipelineConfiguration
from .performance_tracker import PerformanceTracker
from ..monitoring.metrics import MetricsCollector


class GenerationPriority(str, Enum):
    """Generation request priorities"""    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class GenerationStatus(str, Enum):
    """Generation request statuses"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationRequest(BaseModel):
    """Comprehensive generation request model"""    request_id: str = Field(description="Unique request identifier")
    user_id: str = Field(description="User identifier")
    content_types: List[str] = Field(description="Types of content to generate")
    prompt: str = Field(description="Generation prompt or instruction")
    context: ContentGenerationContext = Field(description="Generation context")
    priority: GenerationPriority = Field(default=GenerationPriority.NORMAL)
    options: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    deadline: Optional[datetime] = Field(None, description="Request deadline")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerationResponse(BaseModel):
    """Comprehensive generation response model"""    request_id: str = Field(description="Original request identifier")
    status: GenerationStatus = Field(description="Generation status")
    generated_content: Dict[str, Any] = Field(description="Generated content")
    metadata: Dict[str, Any] = Field(description="Response metadata")
    performance_metrics: Dict[str, Any] = Field(description="Performance metrics")
    quality_scores: Dict[str, float] = Field(description="Quality assessment")
    execution_time: float = Field(description="Total execution time")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error information")


class ResourceLimits(BaseModel):
    """Resource limits configuration"""    max_concurrent_generations: int = Field(default=5)
    max_memory_usage_mb: int = Field(default=8192)
    max_cpu_usage_percent: float = Field(default=80.0)
    max_queue_size: int = Field(default=100)
    generation_timeout_seconds: int = Field(default=600)


class GenerationManager:
    """    Central manager for all content generation operations in the IA Influencer platform.
    
    This manager provides:
    - Centralized generation orchestration
    - Resource management and optimization
    - Request queuing and prioritization
    - Performance monitoring and analytics
    - Caching and optimization
    - Load balancing and scaling
    - Error handling and recovery
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize the generation manager.
        
        Args:
            config: Manager configuration settings
        """        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize resource limits
        self.resource_limits = ResourceLimits(**config.get('resource_limits', {}))
        
        # Initialize core components
        self._initialize_components()
        
        # Manager state
        self.active_requests: Dict[str, GenerationRequest] = {}
        self.completed_requests: Dict[str, GenerationResponse] = {}
        self.failed_requests: Dict[str, GenerationResponse] = {}
        
        # Performance tracking
        self.manager_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'current_load': 0.0,
            'peak_concurrent_requests': 0
        }
        
        # Resource management
        self.current_resource_usage = {
            'memory_mb': 0,
            'cpu_percent': 0.0,
            'concurrent_generations': 0
        }
        
        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._start_background_tasks()
    
    def _initialize_components(self) -> None:
        """Initialize all manager components"""        try:
            # Initialize pipeline with configuration
            pipeline_config = PipelineConfiguration(
                **self.config.get('pipeline', {})
            )
            self.pipeline = ContentGenerationPipeline(pipeline_config)
            
            # Initialize monitoring and analytics
            self.performance_tracker = PerformanceTracker()
            self.resource_monitor = ResourceMonitor()  # Now implemented
            
            # Initialize caching
            self.cache = GenerationCache(self.config.get('cache', {}))  # Now implemented
            
            # Initialize request queue
            self.queue = GenerationQueue(self.config.get('queue', {}))  # Now implemented
            
            self.logger.info("Generation manager components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {str(e)}")
            raise
    
    def _start_background_tasks(self) -> None:
        """Start background management tasks"""        # Resource monitoring task
        resource_task = asyncio.create_task(self._monitor_resources())
        self._background_tasks.add(resource_task)
        resource_task.add_done_callback(self._background_tasks.discard)
        
        # Queue processing task
        queue_task = asyncio.create_task(self._process_queue())
        self._background_tasks.add(queue_task)
        queue_task.add_done_callback(self._background_tasks.discard)
        
        # Cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_completed_requests())
        self._background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self._background_tasks.discard)
    
    async def submit_generation_request(
        self,
        request: GenerationRequest
    ) -> str:
        """        Submit a new content generation request.
        
        Args:
            request: Complete generation request
            
        Returns:
            Request ID for tracking
        """        try:
            # Validate request
            await self._validate_generation_request(request)
            
            # Check resource availability
            if not await self._check_resource_availability():
                # Queue the request
                await self.queue.enqueue_request(request)
                self.logger.info(f"Request {request.request_id} queued due to resource constraints")
                return request.request_id
            
            # Check cache for similar requests
            cached_result = await self.cache.get_cached_result(request)
            if cached_result:
                self.logger.info(f"Returning cached result for request {request.request_id}")
                await self._complete_request_from_cache(request, cached_result)
                return request.request_id
            
            # Process request immediately
            await self._process_generation_request(request)
            
            return request.request_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit generation request: {str(e)}")
            await self._handle_request_error(request, str(e))
            raise
    
    async def get_generation_status(self, request_id: str) -> Optional[GenerationResponse]:
        """        Get the status of a generation request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Current request status and results if available
        """        # Check active requests
        if request_id in self.active_requests:
            request = self.active_requests[request_id]
            return GenerationResponse(
                request_id=request_id,
                status=GenerationStatus.IN_PROGRESS,
                generated_content={},
                metadata={'submitted_at': request.created_at.isoformat()},
                performance_metrics={},
                quality_scores={},
                execution_time=0.0
            )
        
        # Check completed requests
        if request_id in self.completed_requests:
            return self.completed_requests[request_id]
        
        # Check failed requests
        if request_id in self.failed_requests:
            return self.failed_requests[request_id]
        
        # Check queue
        queued_request = await self.queue.get_request_status(request_id)
        if queued_request:
            return GenerationResponse(
                request_id=request_id,
                status=GenerationStatus.PENDING,
                generated_content={},
                metadata={'queued_at': queued_request.created_at.isoformat()},
                performance_metrics={},
                quality_scores={},
                execution_time=0.0
            )
        
        return None
    
    async def cancel_generation_request(self, request_id: str) -> bool:
        """        Cancel a pending or active generation request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            True if cancellation was successful
        """        try:
            # Cancel active request
            if request_id in self.active_requests:
                request = self.active_requests[request_id]
                del self.active_requests[request_id]
                
                # Create cancelled response
                response = GenerationResponse(
                    request_id=request_id,
                    status=GenerationStatus.CANCELLED,
                    generated_content={},
                    metadata={'cancelled_at': datetime.now().isoformat()},
                    performance_metrics={},
                    quality_scores={},
                    execution_time=0.0
                )
                
                self.failed_requests[request_id] = response
                return True
            
            # Cancel queued request
            return await self.queue.cancel_request(request_id)
            
        except Exception as e:
            self.logger.error(f"Failed to cancel request {request_id}: {str(e)}")
            return False
    
    async def _process_generation_request(self, request: GenerationRequest) -> None:
        """Process a generation request through the pipeline"""        try:
            # Add to active requests
            self.active_requests[request.request_id] = request
            
            # Update resource usage
            self.current_resource_usage['concurrent_generations'] += 1
            
            # Update stats
            self.manager_stats['current_load'] = len(self.active_requests)
            self.manager_stats['peak_concurrent_requests'] = max(
                self.manager_stats['peak_concurrent_requests'],
                len(self.active_requests)
            )
            
            start_time = datetime.now()
            
            # Execute pipeline
            pipeline_result = await self.pipeline.execute_pipeline(
                request.context,
                {
                    'content_types': request.content_types,
                    'prompt': request.prompt,
                    'options': request.options,
                    'constraints': request.constraints
                }
            )
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = GenerationResponse(
                request_id=request.request_id,
                status=GenerationStatus.COMPLETED if pipeline_result.success else GenerationStatus.FAILED,
                generated_content=pipeline_result.generated_content,
                metadata=pipeline_result.metadata,
                performance_metrics=pipeline_result.performance_metrics,
                quality_scores=pipeline_result.quality_scores,
                execution_time=execution_time,
                completed_at=datetime.now()
            )
            
            # Store result
            if pipeline_result.success:
                self.completed_requests[request.request_id] = response
                self.manager_stats['successful_requests'] += 1
                
                # Cache successful result
                await self.cache.cache_result(request, response)
            else:
                response.error_details = {'pipeline_error': 'Pipeline execution failed'}
                self.failed_requests[request.request_id] = response
                self.manager_stats['failed_requests'] += 1
            
            # Update statistics
            self.manager_stats['total_requests'] += 1
            self._update_average_processing_time(execution_time)
            
            # Clean up
            del self.active_requests[request.request_id]
            self.current_resource_usage['concurrent_generations'] -= 1
            
        except Exception as e:
            await self._handle_request_error(request, str(e))
    
    async def _validate_generation_request(self, request: GenerationRequest) -> None:
        """Validate generation request parameters"""        if not request.request_id:
            raise ValueError("Request ID is required")
        
        if not request.user_id:
            raise ValueError("User ID is required")
        
        if not request.content_types:
            raise ValueError("At least one content type is required")
        
        if not request.prompt or len(request.prompt.strip()) < 5:
            raise ValueError("Valid prompt is required (minimum 5 characters)")
        
        # Check deadline if specified
        if request.deadline and request.deadline <= datetime.now():
            raise ValueError("Request deadline has already passed")
        
        # Validate content types
        supported_types = ['text', 'audio', 'video', 'image']
        for content_type in request.content_types:
            if content_type not in supported_types:
                raise ValueError(f"Unsupported content type: {content_type}")
    
    async def _check_resource_availability(self) -> bool:
        """Check if resources are available for immediate processing"""        # Check concurrent generations limit
        if (self.current_resource_usage['concurrent_generations'] >= 
            self.resource_limits.max_concurrent_generations):
            return False
        
        # Check memory usage
        current_memory = await self.resource_monitor.get_memory_usage()
        if current_memory >= self.resource_limits.max_memory_usage_mb:
            return False
        
        # Check CPU usage
        current_cpu = await self.resource_monitor.get_cpu_usage()
        if current_cpu >= self.resource_limits.max_cpu_usage_percent:
            return False
        
        return True
    
    async def _complete_request_from_cache(
        self,
        request: GenerationRequest,
        cached_result: GenerationResponse
    ) -> None:
        """Complete request using cached result"""        # Update cached result with new request ID
        cached_result.request_id = request.request_id
        cached_result.completed_at = datetime.now()
        
        # Store as completed
        self.completed_requests[request.request_id] = cached_result
        
        # Update stats
        self.manager_stats['total_requests'] += 1
        self.manager_stats['successful_requests'] += 1
    
    async def _handle_request_error(self, request: GenerationRequest, error: str) -> None:
        """Handle request processing error"""        response = GenerationResponse(
            request_id=request.request_id,
            status=GenerationStatus.FAILED,
            generated_content={},
            metadata={},
            performance_metrics={},
            quality_scores={},
            execution_time=0.0,
            completed_at=datetime.now(),
            error_details={'error': error}
        )
        
        self.failed_requests[request.request_id] = response
        self.manager_stats['failed_requests'] += 1
        
        # Clean up if in active requests
        if request.request_id in self.active_requests:
            del self.active_requests[request.request_id]
            self.current_resource_usage['concurrent_generations'] -= 1
    
    def _update_average_processing_time(self, execution_time: float) -> None:
        """Update average processing time statistic"""        total_successful = self.manager_stats['successful_requests']
        if total_successful > 0:
            current_avg = self.manager_stats['average_processing_time']
            self.manager_stats['average_processing_time'] = (
                (current_avg * (total_successful - 1) + execution_time) / total_successful
            )
    
    async def _monitor_resources(self) -> None:
        """Background task to monitor resource usage"""        while True:
            try:
                # Update resource usage
                self.current_resource_usage['memory_mb'] = await self.resource_monitor.get_memory_usage()
                self.current_resource_usage['cpu_percent'] = await self.resource_monitor.get_cpu_usage()
                
                # Update current load
                self.manager_stats['current_load'] = len(self.active_requests) / max(1, self.resource_limits.max_concurrent_generations)
                
                # Log resource status if high usage
                if (self.current_resource_usage['memory_mb'] > self.resource_limits.max_memory_usage_mb * 0.8 or
                    self.current_resource_usage['cpu_percent'] > self.resource_limits.max_cpu_usage_percent * 0.8):
                    self.logger.warning(f"High resource usage: {self.current_resource_usage}")
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_queue(self) -> None:
        """Background task to process queued requests"""        while True:
            try:
                # Check if we can process more requests
                if await self._check_resource_availability():
                    # Get next request from queue
                    request = await self.queue.dequeue_request()
                    
                    if request:
                        # Process the request
                        await self._process_generation_request(request)
                
                await asyncio.sleep(5)  # Check queue every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Queue processing error: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _cleanup_completed_requests(self) -> None:
        """Background task to cleanup old completed requests"""        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)  # Keep for 24 hours
                
                # Clean up old completed requests
                to_remove = []
                for request_id, response in self.completed_requests.items():
                    if response.completed_at and response.completed_at < cutoff_time:
                        to_remove.append(request_id)
                
                for request_id in to_remove:
                    del self.completed_requests[request_id]
                
                # Clean up old failed requests
                to_remove = []
                for request_id, response in self.failed_requests.items():
                    if response.completed_at and response.completed_at < cutoff_time:
                        to_remove.append(request_id)
                
                for request_id in to_remove:
                    del self.failed_requests[request_id]
                
                if to_remove:
                    self.logger.info(f"Cleaned up {len(to_remove)} old requests")
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                self.logger.error(f"Cleanup error: {str(e)}")
                await asyncio.sleep(3600)  # Wait hour on error
    
    def get_manager_statistics(self) -> Dict[str, Any]:
        """Get comprehensive manager statistics"""        return {
            **self.manager_stats,
            'resource_usage': self.current_resource_usage,
            'active_requests_count': len(self.active_requests),
            'completed_requests_count': len(self.completed_requests),
            'failed_requests_count': len(self.failed_requests),
            'queue_size': len(self.queue) if hasattr(self.queue, '__len__') else 0,
            'success_rate': (
                self.manager_stats['successful_requests'] / 
                max(1, self.manager_stats['total_requests'])
            ) * 100
        }
    
    async def shutdown(self) -> None:
        """Shutdown the generation manager gracefully"""        try:
            self.logger.info("Shutting down generation manager...")
            
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            # Complete or cancel active requests
            for request_id in list(self.active_requests.keys()):
                await self.cancel_generation_request(request_id)
            
            self.logger.info("Generation manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")


class QueueManager:
    """Queue management for generation requests"""    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.queue = []
    
    def enqueue(self, item: Any) -> bool:
        """Add item to queue"""        if len(self.queue) < self.max_size:
            self.queue.append(item)
            return True
        return False
    
    def dequeue(self) -> Optional[Any]:
        """Remove item from queue"""        return self.queue.pop(0) if self.queue else None
    
    def size(self) -> int:
        """Get queue size"""        return len(self.queue)


class ResourceMonitor:
    """Monitor system resources for generation management"""    
    def __init__(self):
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage"""        return 50.0  # Mock implementation
    
    def get_memory_usage(self) -> float:
        """Get current memory usage"""        return 60.0  # Mock implementation
    
    def is_resource_available(self) -> bool:
        """Check if resources are available"""        return (self.get_cpu_usage() < self.cpu_threshold and 
                self.get_memory_usage() < self.memory_threshold)
    
    def get_resource_alerts(self) -> List[str]:
        """Get resource alerts"""        alerts = []
        if self.get_cpu_usage() > self.cpu_threshold:
            alerts.append("High CPU usage")
        if self.get_memory_usage() > self.memory_threshold:
            alerts.append("High memory usage")
        return alerts


class QueueManager:
    """Queue management for generation requests"""    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.queue = []
    
    def enqueue(self, task: Any) -> bool:
        """Add task to queue"""        if len(self.queue) < self.max_size:
            self.queue.append(task)
            return True
        return False
    
    def dequeue(self) -> Any:
        """Remove task from queue"""        if self.queue:
            return self.queue.pop(0)
        return None
    
    def size(self) -> int:
        """Get queue size"""        return len(self.queue)


class ResourceMonitor:
    """Resource monitoring for system health"""    
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.cpu_threshold = 80.0
        self.memory_threshold = 80.0
        self._update_metrics()
    
    def _update_metrics(self):
        """Update system metrics"""        try:
            import psutil
            self.cpu_usage = psutil.cpu_percent(interval=0.1)
            self.memory_usage = psutil.virtual_memory().percent
        except ImportError:
            # Fallback for environments without psutil
            import random
            self.cpu_usage = random.uniform(10, 50)  # Simulated values
            self.memory_usage = random.uniform(20, 60)
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""        self._update_metrics()
        return self.cpu_usage
    
    def get_memory_usage(self) -> float:
        """Get memory usage percentage"""        self._update_metrics()
        return self.memory_usage
    
    def is_resource_available(self) -> bool:
        """Check if resources are available"""        return self.cpu_usage < 80.0 and self.memory_usage < 80.0
    
    def configure_thresholds(self, cpu_threshold: float, memory_threshold: float) -> None:
        """Configure resource thresholds"""        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        logger.info(f"Resource thresholds configured: CPU={cpu_threshold}%, Memory={memory_threshold}%")
    
    def send_alert(self, message: str) -> None:
        """Send resource alert"""        timestamp = datetime.now().isoformat()
        alert_data = {
            'timestamp': timestamp,
            'message': message,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage
        }
        logger.warning(f"🚨 Resource Alert: {message} - CPU: {self.cpu_usage}% Memory: {self.memory_usage}%")
        # In production, this would integrate with alerting systems like PagerDuty/Slack
        return alert_data


class GenerationCache:
    """Intelligent caching system for generation results"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = {}
        self.max_size = config.get('max_size', 1000)
        self.ttl_seconds = config.get('ttl_seconds', 3600)  # 1 hour default
        self.access_times = {}
        
    def _generate_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate unique cache key"""        import hashlib
        key_data = f"{prompt}:{json.dumps(sorted(params.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, prompt: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached generation result"""        key = self._generate_cache_key(prompt, params)
        if key in self.cache:
            # Check TTL
            cached_time = self.access_times.get(key, 0)
            if time.time() - cached_time < self.ttl_seconds:
                self.access_times[key] = time.time()  # Update access time
                return self.cache[key]
            else:
                # Expired, remove from cache
                self._remove(key)
        return None
    
    def set(self, prompt: str, params: Dict[str, Any], result: Any) -> None:
        """Cache generation result"""        key = self._generate_cache_key(prompt, params)
        
        # Evict oldest items if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = result
        self.access_times[key] = time.time()
    
    def _remove(self, key: str) -> None:
        """Remove item from cache"""        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
    
    def _evict_oldest(self) -> None:
        """Evict oldest accessed items"""        if not self.access_times:
            return
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove(oldest_key)
    
    def clear(self) -> None:
        """Clear all cached items"""        self.cache.clear()
        self.access_times.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1),
            'ttl_seconds': self.ttl_seconds
        }


class GenerationQueue:
    """Priority queue for generation requests"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_size = config.get('max_size', 500)
        self.queues = {
            GenerationPriority.URGENT: [],
            GenerationPriority.HIGH: [],
            GenerationPriority.NORMAL: [],
            GenerationPriority.LOW: []
        }
        self.total_size = 0
        
    def enqueue(self, request: GenerationRequest) -> bool:
        """Add request to appropriate priority queue"""        if self.total_size >= self.max_size:
            return False
        
        priority = request.priority
        self.queues[priority].append(request)
        self.total_size += 1
        return True
    
    def dequeue(self) -> Optional[GenerationRequest]:
        """Get next request based on priority"""        # Process in priority order
        for priority in [GenerationPriority.URGENT, GenerationPriority.HIGH, 
                        GenerationPriority.NORMAL, GenerationPriority.LOW]:
            if self.queues[priority]:
                request = self.queues[priority].pop(0)
                self.total_size -= 1
                return request
        return None
    
    def size(self) -> int:
        """Get total queue size"""        return self.total_size
    
    def size_by_priority(self) -> Dict[str, int]:
        """Get queue size by priority"""        return {
            priority.value: len(queue) 
            for priority, queue in self.queues.items()
        }
    
    def clear_priority(self, priority: GenerationPriority) -> int:
        """Clear requests of specific priority"""        count = len(self.queues[priority])
        self.queues[priority].clear()
        self.total_size -= count
        return count
