"""Multimedia Orchestrator - Enterprise Content Processing Coordinator

Central orchestration system for managing complex multimedia workflows.
Coordinates multiple processing engines and ensures optimal resource utilization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid
import time

from ..events.dispatcher import EventDispatcher
from ..monitoring.metrics import MetricsCollector
from .registry import MultimediaRegistry
from .pipeline import MultimediaPipeline
from .scheduler import MultimediaScheduler
from .cache import MultimediaCache
from .validator import MultimediaValidator

logger = logging.getLogger(__name__)


class ProcessingPriority(Enum):
    """Processing priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessingRequest:
    """Multimedia processing request"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    content_type: str = ""
    content_source: Union[str, bytes] = ""
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_options: Dict[str, Any] = field(default_factory=dict)
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    deadline: Optional[datetime] = None
    callback_url: Optional[str] = None
    webhook_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    progress: float = 0.0
    error_details: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowDefinition:
    """Multimedia workflow definition"""
    workflow_id: str
    name: str
    description: str
    pipeline_steps: List[Dict[str, Any]]
    input_validation: Dict[str, Any]
    output_format: Dict[str, Any]
    timeout_seconds: int = 3600
    retry_config: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    parallel_execution: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    enabled: bool = True


class MultimediaOrchestrator:
    """Enterprise multimedia processing orchestrator"""
    
    def __init__(
        self, 
        config: Dict[str, Any],
        event_dispatcher: Optional[EventDispatcher] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.config = config
        self.event_dispatcher = event_dispatcher or EventDispatcher()
        self.metrics = metrics_collector or MetricsCollector()
        
        # Core components
        self.registry = MultimediaRegistry(config.get("registry", {}))
        self.pipeline = MultimediaPipeline(config.get("pipeline", {}))
        self.scheduler = MultimediaScheduler(config.get("scheduler", {}))
        self.cache = MultimediaCache(config.get("cache", {}))
        self.validator = MultimediaValidator(config.get("validator", {}))
        
        # Processing state
        self.active_requests: Dict[str, ProcessingRequest] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.processing_queues: Dict[ProcessingPriority, asyncio.Queue] = {}
        self.worker_pools: Dict[str, List[asyncio.Task]] = {}
        
        # Configuration
        self.max_concurrent_requests = config.get("max_concurrent", 50)
        self.max_workers_per_type = config.get("max_workers_per_type", 10)
        self.health_check_interval = config.get("health_check_interval", 30)
        self.cleanup_interval = config.get("cleanup_interval", 300)
        
        # Monitoring
        self.performance_metrics = {
            "requests_processed": 0,
            "requests_failed": 0,
            "average_processing_time": 0.0,
            "active_workflows": 0,
            "queue_sizes": {},
            "worker_utilization": {}
        }
        
        self._initialize_queues()
        self._setup_event_handlers()
        
    async def initialize(self):
        """Initialize orchestrator components"""
        try:
            # Initialize core components
            await self.registry.initialize()
            await self.pipeline.initialize()
            await self.scheduler.initialize()
            await self.cache.initialize()
            await self.validator.initialize()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Load workflow definitions
            await self._load_workflow_definitions()
            
            logger.info("Multimedia orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            raise
            
    def _initialize_queues(self):
        """Initialize processing queues for different priorities"""
        for priority in ProcessingPriority:
            self.processing_queues[priority] = asyncio.Queue(
                maxsize=self.config.get(f"queue_size_{priority.value}", 1000)
            )
            
    def _setup_event_handlers(self):
        """Setup event handlers for workflow lifecycle"""
        self.event_dispatcher.subscribe("request_created", self._handle_request_created)
        self.event_dispatcher.subscribe("request_started", self._handle_request_started)
        self.event_dispatcher.subscribe("request_progress", self._handle_request_progress)
        self.event_dispatcher.subscribe("request_completed", self._handle_request_completed)
        self.event_dispatcher.subscribe("request_failed", self._handle_request_failed)
        
    async def submit_request(
        self, 
        request: ProcessingRequest,
        workflow_id: Optional[str] = None
    ) -> str:
        """Submit multimedia processing request"""
        try:
            # Validate request
            validation_result = await self.validator.validate_request(request)
            if not validation_result.is_valid:
                raise ValueError(f"Invalid request: {validation_result.errors}")
                
            # Determine workflow
            if workflow_id:
                workflow = self.workflow_definitions.get(workflow_id)
                if not workflow or not workflow.enabled:
                    raise ValueError(f"Workflow not found or disabled: {workflow_id}")
            else:
                workflow = await self._select_optimal_workflow(request)
                
            # Enqueue request
            request.status = WorkflowStatus.PENDING
            self.active_requests[request.request_id] = request
            
            await self.processing_queues[request.priority].put({
                "request": request,
                "workflow": workflow
            })
            
            # Fire event
            await self.event_dispatcher.emit("request_created", {
                "request_id": request.request_id,
                "user_id": request.user_id,
                "content_type": request.content_type,
                "priority": request.priority.value,
                "workflow_id": workflow.workflow_id if workflow else None
            })
            
            # Update metrics
            self.performance_metrics["active_workflows"] += 1
            self._update_queue_metrics()
            
            logger.info(f"Request submitted: {request.request_id}")
            return request.request_id
            
        except Exception as e:
            logger.error(f"Failed to submit request: {e}")
            raise
            
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get processing request status"""
        request = self.active_requests.get(request_id)
        if not request:
            # Check cache for completed requests
            cached_result = await self.cache.get_request_result(request_id)
            if cached_result:
                return cached_result
            raise ValueError(f"Request not found: {request_id}")
            
        return {
            "request_id": request.request_id,
            "status": request.status.value,
            "progress": request.progress,
            "created_at": request.created_at.isoformat(),
            "started_at": request.started_at.isoformat() if request.started_at else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "error_details": request.error_details,
            "result": request.result
        }
        
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel processing request"""
        try:
            request = self.active_requests.get(request_id)
            if not request:
                return False
                
            if request.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                return False
                
            request.status = WorkflowStatus.CANCELLED
            request.completed_at = datetime.now(timezone.utc)
            
            # Fire event
            await self.event_dispatcher.emit("request_cancelled", {
                "request_id": request_id,
                "user_id": request.user_id
            })
            
            logger.info(f"Request cancelled: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel request: {e}")
            return False
            
    async def pause_request(self, request_id: str) -> bool:
        """Pause processing request"""
        try:
            request = self.active_requests.get(request_id)
            if not request or request.status != WorkflowStatus.RUNNING:
                return False
                
            request.status = WorkflowStatus.PAUSED
            
            # Fire event
            await self.event_dispatcher.emit("request_paused", {
                "request_id": request_id,
                "user_id": request.user_id
            })
            
            logger.info(f"Request paused: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause request: {e}")
            return False
            
    async def resume_request(self, request_id: str) -> bool:
        """Resume paused processing request"""
        try:
            request = self.active_requests.get(request_id)
            if not request or request.status != WorkflowStatus.PAUSED:
                return False
                
            request.status = WorkflowStatus.RUNNING
            
            # Fire event
            await self.event_dispatcher.emit("request_resumed", {
                "request_id": request_id,
                "user_id": request.user_id
            })
            
            logger.info(f"Request resumed: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume request: {e}")
            return False
            
    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register new workflow definition"""
        try:
            # Validate workflow
            validation_result = await self._validate_workflow(workflow)
            if not validation_result:
                return False
                
            self.workflow_definitions[workflow.workflow_id] = workflow
            
            # Cache workflow
            await self.cache.cache_workflow(workflow)
            
            logger.info(f"Workflow registered: {workflow.workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register workflow: {e}")
            return False
            
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics"""
        return {
            **self.performance_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_requests": len(self.active_requests),
            "queue_sizes": {
                priority.value: queue.qsize() 
                for priority, queue in self.processing_queues.items()
            },
            "component_health": await self._get_component_health()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "components": {
                    "registry": await self.registry.health_check(),
                    "pipeline": await self.pipeline.health_check(),
                    "scheduler": await self.scheduler.health_check(),
                    "cache": await self.cache.health_check(),
                    "validator": await self.validator.health_check()
                },
                "metrics": await self.get_performance_metrics()
            }
            
            # Check component health
            unhealthy_components = [
                name for name, status in health_status["components"].items()
                if status.get("status") != "healthy"
            ]
            
            if unhealthy_components:
                health_status["status"] = "degraded"
                health_status["unhealthy_components"] = unhealthy_components
                
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    async def shutdown(self):
        """Graceful shutdown of orchestrator"""
        try:
            logger.info("Shutting down multimedia orchestrator...")
            
            # Cancel all background tasks
            for pool_name, tasks in self.worker_pools.items():
                for task in tasks:
                    if not task.done():
                        task.cancel()
                        
            # Wait for active requests to complete (with timeout)
            await self._wait_for_active_requests(timeout=60)
            
            # Shutdown components
            await self.scheduler.shutdown()
            await self.cache.shutdown()
            
            logger.info("Multimedia orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            
    # Private methods
    
    async def _start_background_tasks(self):
        """Start background worker tasks"""
        # Start worker pools for each priority level
        for priority in ProcessingPriority:
            workers = []
            worker_count = self.max_workers_per_type
            
            for i in range(worker_count):
                worker = asyncio.create_task(
                    self._process_queue_worker(priority)
                )
                workers.append(worker)
                
            self.worker_pools[f"queue_{priority.value}"] = workers
            
        # Start monitoring tasks
        self.worker_pools["health_monitor"] = [
            asyncio.create_task(self._health_monitor_worker())
        ]
        
        self.worker_pools["cleanup"] = [
            asyncio.create_task(self._cleanup_worker())
        ]
        
    async def _process_queue_worker(self, priority: ProcessingPriority):
        """Worker for processing requests from priority queue"""
        queue = self.processing_queues[priority]
        
        while True:
            try:
                # Get next request from queue
                item = await queue.get()
                request = item["request"]
                workflow = item["workflow"]
                
                # Process request
                await self._process_request(request, workflow)
                
                # Mark task as done
                queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error for priority {priority.value}: {e}")
                await asyncio.sleep(1)
                
    async def _process_request(self, request: ProcessingRequest, workflow: WorkflowDefinition):
        """Process individual multimedia request"""
        try:
            # Update request status
            request.status = WorkflowStatus.RUNNING
            request.started_at = datetime.now(timezone.utc)
            
            # Fire event
            await self.event_dispatcher.emit("request_started", {
                "request_id": request.request_id,
                "user_id": request.user_id,
                "workflow_id": workflow.workflow_id
            })
            
            # Execute workflow pipeline
            result = await self.pipeline.execute_workflow(request, workflow)
            
            # Update request with result
            request.status = WorkflowStatus.COMPLETED
            request.completed_at = datetime.now(timezone.utc)
            request.progress = 100.0
            request.result = result
            
            # Cache result
            await self.cache.cache_request_result(request.request_id, result)
            
            # Fire completion event
            await self.event_dispatcher.emit("request_completed", {
                "request_id": request.request_id,
                "user_id": request.user_id,
                "result": result
            })
            
            # Update metrics
            self.performance_metrics["requests_processed"] += 1
            self._update_processing_time_metric(request)
            
            logger.info(f"Request completed successfully: {request.request_id}")
            
        except Exception as e:
            # Handle processing failure
            request.status = WorkflowStatus.FAILED
            request.completed_at = datetime.now(timezone.utc)
            request.error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Fire failure event
            await self.event_dispatcher.emit("request_failed", {
                "request_id": request.request_id,
                "user_id": request.user_id,
                "error": str(e)
            })
            
            # Update metrics
            self.performance_metrics["requests_failed"] += 1
            
            logger.error(f"Request failed: {request.request_id} - {e}")
            
        finally:
            # Update metrics
            self.performance_metrics["active_workflows"] -= 1
            
    async def _select_optimal_workflow(self, request: ProcessingRequest) -> WorkflowDefinition:
        """Select optimal workflow for processing request"""
        # This is a simplified implementation
        # In production, this would use AI/ML for optimal workflow selection
        
        content_type = request.content_type.lower()
        
        # Default workflow mapping
        workflow_mapping = {
            "audio": "audio_processing_workflow",
            "video": "video_processing_workflow", 
            "image": "image_processing_workflow",
            "text": "text_processing_workflow",
            "mixed": "mixed_media_workflow"
        }
        
        workflow_id = workflow_mapping.get(content_type, "default_workflow")
        workflow = self.workflow_definitions.get(workflow_id)
        
        if not workflow:
            # Create default workflow
            workflow = WorkflowDefinition(
                workflow_id="default_workflow",
                name="Default Processing Workflow",
                description="Default multimedia processing workflow",
                pipeline_steps=[
                    {"step": "validate", "processor": "validator"},
                    {"step": "analyze", "processor": "analyzer"},
                    {"step": "process", "processor": "converter"},
                    {"step": "enhance", "processor": "enhancer"},
                    {"step": "finalize", "processor": "optimizer"}
                ],
                input_validation={},
                output_format={}
            )
            
        return workflow
        
    async def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Validate workflow definition"""
        try:
            # Basic validation
            if not workflow.workflow_id or not workflow.name:
                return False
                
            if not workflow.pipeline_steps:
                return False
                
            # Validate pipeline steps
            for step in workflow.pipeline_steps:
                if "step" not in step or "processor" not in step:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Workflow validation error: {e}")
            return False
            
    async def _health_monitor_worker(self):
        """Background health monitoring worker"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Perform health checks
                health_status = await self.health_check()
                
                # Log health status
                if health_status["status"] != "healthy":
                    logger.warning(f"Health check warning: {health_status}")
                    
                # Update metrics
                await self.metrics.record_health_check(health_status)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                
    async def _cleanup_worker(self):
        """Background cleanup worker"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Cleanup completed requests
                await self._cleanup_completed_requests()
                
                # Cleanup cache
                await self.cache.cleanup_expired()
                
                # Update metrics
                self._update_queue_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")
                
    async def _cleanup_completed_requests(self):
        """Cleanup completed requests from memory"""
        current_time = datetime.now(timezone.utc)
        retention_period = self.config.get("completed_request_retention", 3600)  # 1 hour
        
        requests_to_remove = []
        
        for request_id, request in self.active_requests.items():
            if request.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                if request.completed_at:
                    elapsed = (current_time - request.completed_at).total_seconds()
                    if elapsed > retention_period:
                        requests_to_remove.append(request_id)
                        
        for request_id in requests_to_remove:
            del self.active_requests[request_id]
            
        if requests_to_remove:
            logger.info(f"Cleaned up {len(requests_to_remove)} completed requests")
            
    def _update_queue_metrics(self):
        """Update queue size metrics"""
        self.performance_metrics["queue_sizes"] = {
            priority.value: queue.qsize()
            for priority, queue in self.processing_queues.items()
        }
        
    def _update_processing_time_metric(self, request: ProcessingRequest):
        """Update average processing time metric"""
        if request.started_at and request.completed_at:
            processing_time = (request.completed_at - request.started_at).total_seconds()
            current_avg = self.performance_metrics["average_processing_time"]
            total_processed = self.performance_metrics["requests_processed"]
            
            # Calculate new average
            new_avg = ((current_avg * (total_processed - 1)) + processing_time) / total_processed
            self.performance_metrics["average_processing_time"] = new_avg
            
    async def _get_component_health(self) -> Dict[str, str]:
        """Get health status of all components"""
        try:
            components = {
                "registry": await self.registry.health_check(),
                "pipeline": await self.pipeline.health_check(),
                "scheduler": await self.scheduler.health_check(),
                "cache": await self.cache.health_check(),
                "validator": await self.validator.health_check()
            }
            
            return {
                name: status.get("status", "unknown")
                for name, status in components.items()
            }
            
        except Exception as e:
            logger.error(f"Error getting component health: {e}")
            return {}
            
    async def _wait_for_active_requests(self, timeout: int = 60):
        """Wait for active requests to complete"""
        start_time = time.time()
        
        while self.active_requests and (time.time() - start_time) < timeout:
            active_count = len([
                r for r in self.active_requests.values()
                if r.status == WorkflowStatus.RUNNING
            ])
            
            if active_count == 0:
                break
                
            await asyncio.sleep(1)
            
        remaining_active = len([
            r for r in self.active_requests.values()
            if r.status == WorkflowStatus.RUNNING
        ])
        
        if remaining_active > 0:
            logger.warning(f"{remaining_active} requests still active after timeout")
            
    async def _load_workflow_definitions(self):
        """Load workflow definitions from configuration"""
        # This would typically load from database or configuration files
        # For now, we'll create some default workflows
        
        default_workflows = [
            WorkflowDefinition(
                workflow_id="audio_processing_workflow",
                name="Audio Processing Workflow",
                description="Complete audio processing pipeline",
                pipeline_steps=[
                    {"step": "validate", "processor": "validator"},
                    {"step": "analyze", "processor": "analyzer"},
                    {"step": "enhance", "processor": "enhancer"},
                    {"step": "compress", "processor": "compressor"},
                    {"step": "fingerprint", "processor": "fingerprint"},
                    {"step": "metadata", "processor": "metadata"}
                ],
                input_validation={"allowed_formats": ["mp3", "wav", "flac", "aac"]},
                output_format={"format": "mp3", "quality": "high"}
            ),
            WorkflowDefinition(
                workflow_id="video_processing_workflow",
                name="Video Processing Workflow", 
                description="Complete video processing pipeline",
                pipeline_steps=[
                    {"step": "validate", "processor": "validator"},
                    {"step": "analyze", "processor": "analyzer"},
                    {"step": "transcode", "processor": "transcoder"},
                    {"step": "enhance", "processor": "enhancer"},
                    {"step": "thumbnails", "processor": "thumbnails"},
                    {"step": "fingerprint", "processor": "fingerprint"}
                ],
                input_validation={"allowed_formats": ["mp4", "avi", "mov", "mkv"]},
                output_format={"format": "mp4", "resolution": "1080p"}
            ),
            WorkflowDefinition(
                workflow_id="image_processing_workflow",
                name="Image Processing Workflow",
                description="Complete image processing pipeline", 
                pipeline_steps=[
                    {"step": "validate", "processor": "validator"},
                    {"step": "analyze", "processor": "analyzer"},
                    {"step": "enhance", "processor": "enhancer"},
                    {"step": "optimize", "processor": "optimizer"},
                    {"step": "watermark", "processor": "watermark"},
                    {"step": "fingerprint", "processor": "fingerprint"}
                ],
                input_validation={"allowed_formats": ["jpg", "png", "gif", "webp"]},
                output_format={"format": "jpg", "quality": 85}
            )
        ]
        
        for workflow in default_workflows:
            self.workflow_definitions[workflow.workflow_id] = workflow
            
    # Event handlers
    
    async def _handle_request_created(self, event_data: Dict[str, Any]):
        """Handle request created event"""
        logger.info(f"Request created: {event_data['request_id']}")
        
    async def _handle_request_started(self, event_data: Dict[str, Any]):
        """Handle request started event"""
        logger.info(f"Request started: {event_data['request_id']}")
        
    async def _handle_request_progress(self, event_data: Dict[str, Any]):
        """Handle request progress event"""
        request_id = event_data.get("request_id")
        progress = event_data.get("progress", 0)
        
        if request_id in self.active_requests:
            self.active_requests[request_id].progress = progress
            
    async def _handle_request_completed(self, event_data: Dict[str, Any]):
        """Handle request completed event"""
        logger.info(f"Request completed: {event_data['request_id']}")
        
    async def _handle_request_failed(self, event_data: Dict[str, Any]):
        """Handle request failed event"""
        logger.error(f"Request failed: {event_data['request_id']} - {event_data.get('error')}")
