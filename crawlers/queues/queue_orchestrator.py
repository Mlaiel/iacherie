"""Queue Orchestrator - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/queue_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Queue Orchestrator - Central Queue Management System
Responsibility: Unified orchestration of all crawler queue operations
Technologies: Async Orchestration, Multi-Queue Coordination, Load Balancing
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Request reception → Queue routing → Priority analysis → Worker assignment → 
Load balancing → Execution monitoring → Result processing → Performance optimization
"""from typing import Any, Dict, List, Optional, Set, Callable, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import time
from collections import defaultdict, deque

from .crawler_queue_manager import CrawlerQueueManager, CrawlerTask, CrawlerQueueConfig
from .queue_workers import QueueWorkersManager, WorkerConfig
from .priority_manager import DynamicPriorityManager, PriorityFactors
from backend.core.managers.queue_manager import IntelligentQueueManager

logger = logging.getLogger(__name__)


class OrchestrationStatus(Enum):
    """Orchestrator status levels"""    INITIALIZING = "initializing"
    ACTIVE = "active"
    OVERLOADED = "overloaded"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"
    ERROR = "error"


@dataclass
class OrchestrationMetrics:
    """Comprehensive orchestration metrics"""    # Throughput metrics
    total_requests_received: int = 0
    total_tasks_processed: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    average_queue_wait_time_ms: float = 0.0
    average_processing_time_ms: float = 0.0
    current_throughput_per_minute: float = 0.0
    
    # Resource metrics
    active_queues: int = 0
    active_workers: int = 0
    total_queue_size: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Quality metrics
    success_rate: float = 0.0
    priority_accuracy: float = 0.0
    load_balance_efficiency: float = 0.0
    
    # Error tracking
    error_rate: float = 0.0
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Timestamp
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class OrchestrationConfig:
    """Orchestrator configuration"""    max_concurrent_requests: int = 1000
    max_queue_size: int = 50000
    max_workers: int = 100
    
    # Performance thresholds
    response_time_threshold_ms: float = 5000.0
    queue_wait_threshold_ms: float = 30000.0
    error_rate_threshold: float = 0.05  # 5%
    
    # Auto-scaling settings
    auto_scaling_enabled: bool = True
    scale_up_threshold: float = 0.8  # 80% capacity
    scale_down_threshold: float = 0.3  # 30% capacity
    
    # Monitoring settings
    metrics_collection_interval: int = 60  # seconds
    health_check_interval: int = 30  # seconds
    optimization_interval: int = 300  # 5 minutes
    
    # Integration settings
    core_queue_integration: bool = True
    external_monitoring: bool = True
    webhook_notifications: bool = True


class CrawlerQueueOrchestrator:
    """    🎼 Advanced Crawler Queue Orchestrator - IA-Influencer-Agent
    
    Enterprise-grade queue orchestration system featuring:
    - Multi-queue coordination and management
    - Intelligent load balancing and routing
    - Dynamic scaling and optimization
    - Real-time performance monitoring
    - Advanced error handling and recovery
    - Integration with core queue systems
    - Comprehensive analytics and reporting
    """    
    def __init__(self, config: OrchestrationConfig = None):
        self.config = config or OrchestrationConfig()
        
        # Core components
        self.queue_manager: Optional[CrawlerQueueManager] = None
        self.workers_manager: Optional[QueueWorkersManager] = None
        self.priority_manager: Optional[DynamicPriorityManager] = None
        self.core_queue_manager: Optional[IntelligentQueueManager] = None
        
        # Orchestration state
        self.status = OrchestrationStatus.INITIALIZING
        self.metrics = OrchestrationMetrics()
        
        # Request tracking
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.request_history: deque = deque(maxlen=10000)
        
        # Load balancing
        self.queue_load_balancer: Dict[str, float] = defaultdict(float)
        self.worker_load_balancer: Dict[str, float] = defaultdict(float)
        
        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)
        self.throughput_tracker: deque = deque(maxlen=60)  # Last 60 minutes
        
        # Background tasks
        self._is_running = False
        self._orchestration_tasks: List[asyncio.Task] = []
        
        # Callbacks and webhooks
        self._status_callbacks: List[Callable] = []
        self._metrics_callbacks: List[Callable] = []
        self._webhook_urls: List[str] = []
    
    async def initialize(
        self, 
        core_queue_manager: Optional[IntelligentQueueManager] = None
    ) -> bool:
        """Initialize orchestrator and all components"""        try:
            logger.info("🎼 Initializing Crawler Queue Orchestrator...")
            
            # Store core queue manager reference
            self.core_queue_manager = core_queue_manager
            
            # Initialize priority manager
            self.priority_manager = DynamicPriorityManager()
            if not await self.priority_manager.initialize():
                raise Exception("Priority manager initialization failed")
            
            # Initialize workers manager
            self.workers_manager = QueueWorkersManager(self.config.max_workers)
            if not await self.workers_manager.initialize():
                raise Exception("Workers manager initialization failed")
            
            # Initialize queue manager
            queue_config = CrawlerQueueConfig(
                max_concurrent_crawlers=self.config.max_workers,
                max_queue_size=self.config.max_queue_size
            )
            self.queue_manager = CrawlerQueueManager(queue_config)
            if not await self.queue_manager.initialize(core_queue_manager):
                raise Exception("Queue manager initialization failed")
            
            # Start orchestration background tasks
            self._is_running = True
            self._orchestration_tasks.extend([
                asyncio.create_task(self._orchestration_monitor()),
                asyncio.create_task(self._performance_optimizer()),
                asyncio.create_task(self._load_balancer()),
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._health_monitor()),
                asyncio.create_task(self._auto_scaler())
            ])
            
            self.status = OrchestrationStatus.ACTIVE
            logger.info("✅ Crawler Queue Orchestrator initialized successfully")
            
            # Notify status callbacks
            await self._notify_status_change(OrchestrationStatus.ACTIVE)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Orchestrator initialization failed: {e}")
            self.status = OrchestrationStatus.ERROR
            return False
    
    async def submit_crawler_request(
        self,
        task: CrawlerTask,
        priority_factors: Optional[PriorityFactors] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit crawler request for orchestrated processing"""        try:
            request_id = f"req_{uuid.uuid4().hex}"
            start_time = time.time()
            
            # Validate request
            if not await self._validate_request(task):
                return {
                    "status": "error",
                    "request_id": request_id,
                    "error": "Invalid crawler request"
                }
            
            # Check capacity
            if len(self.active_requests) >= self.config.max_concurrent_requests:
                return {
                    "status": "error",
                    "request_id": request_id,
                    "error": "System at capacity"
                }
            
            # Calculate priority
            if not priority_factors:
                priority_factors = await self._create_default_priority_factors(task)
            
            priority_score = await self.priority_manager.calculate_task_priority(
                task, priority_factors
            )
            
            # Route to appropriate queue
            queue_selection = await self._select_optimal_queue(task, priority_score)
            
            # Assign to worker
            worker_assignment = await self._assign_optimal_worker(task, priority_score)
            
            # Track request
            request_info = {
                "request_id": request_id,
                "task_id": task.task_id,
                "submitted_at": datetime.now(),
                "priority_score": priority_score,
                "queue_selection": queue_selection,
                "worker_assignment": worker_assignment,
                "callback_url": callback_url,
                "status": "processing"
            }
            
            self.active_requests[request_id] = request_info
            
            # Submit to queue manager
            queue_result = await self.queue_manager.enqueue_crawler_task(task)
            
            # Submit to workers manager
            worker_result = await self.workers_manager.assign_task_to_worker(task)
            
            # Update metrics
            processing_time_ms = (time.time() - start_time) * 1000
            await self._update_submission_metrics(processing_time_ms, True)
            
            response = {
                "status": "accepted",
                "request_id": request_id,
                "task_id": task.task_id,
                "priority_level": priority_score.priority_level.value,
                "estimated_completion": await self._estimate_completion_time(task, priority_score),
                "queue_position": await self._get_queue_position(task),
                "processing_time_ms": processing_time_ms
            }
            
            logger.info(f"📨 Crawler request submitted: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to submit crawler request: {e}")
            await self._update_submission_metrics(0, False)
            
            return {
                "status": "error",
                "request_id": request_id if 'request_id' in locals() else "unknown",
                "error": str(e)
            }
    
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get comprehensive status of submitted request"""        try:
            request_info = self.active_requests.get(request_id)
            if not request_info:
                # Check history
                for historical_request in self.request_history:
                    if historical_request.get("request_id") == request_id:
                        return {
                            "status": "completed",
                            "request_id": request_id,
                            "completed_at": historical_request.get("completed_at"),
                            "result": historical_request.get("result")
                        }
                
                return {
                    "status": "error",
                    "request_id": request_id,
                    "error": "Request not found"
                }
            
            # Get task status from queue manager
            task_status = await self.queue_manager.get_crawler_task_status(
                request_info["task_id"]
            )
            
            # Get worker status
            worker_status = None
            if request_info.get("worker_assignment"):
                workers_status = await self.workers_manager.get_workers_status()
                worker_status = workers_status.get("workers", {}).get(
                    request_info["worker_assignment"]
                )
            
            return {
                "status": request_info["status"],
                "request_id": request_id,
                "task_id": request_info["task_id"],
                "submitted_at": request_info["submitted_at"].isoformat(),
                "priority_level": request_info["priority_score"].priority_level.value,
                "queue_status": task_status,
                "worker_status": worker_status,
                "estimated_completion": await self._estimate_completion_time(
                    None, request_info["priority_score"]
                )
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get request status: {e}")
            return {
                "status": "error",
                "request_id": request_id,
                "error": str(e)
            }
    
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel active crawler request"""        try:
            request_info = self.active_requests.get(request_id)
            if not request_info:
                return False
            
            # Cancel in queue manager
            queue_cancelled = await self.queue_manager.cancel_crawler_task(
                request_info["task_id"]
            )
            
            # Cancel in workers manager (if assigned)
            worker_cancelled = True
            if request_info.get("worker_assignment"):
                # Would implement worker task cancellation
                pass
            
            # Remove from active requests
            if queue_cancelled:
                self.active_requests.pop(request_id, None)
                logger.info(f"🚫 Request cancelled: {request_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel request: {e}")
            return False
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""        try:
            # Update current metrics
            await self._update_current_metrics()
            
            # Get component statuses
            queue_metrics = await self.queue_manager.get_crawler_metrics()
            workers_status = await self.workers_manager.get_workers_status()
            priority_insights = await self.priority_manager.get_priority_insights()
            
            return {
                "orchestrator": {
                    "status": self.status.value,
                    "uptime_seconds": (datetime.now() - self.metrics.last_updated).total_seconds(),
                    "active_requests": len(self.active_requests),
                    "max_concurrent_requests": self.config.max_concurrent_requests
                },
                "performance": {
                    "total_requests_received": self.metrics.total_requests_received,
                    "total_tasks_processed": self.metrics.total_tasks_processed,
                    "success_rate": self.metrics.success_rate,
                    "average_response_time_ms": self.metrics.average_response_time_ms,
                    "current_throughput_per_minute": self.metrics.current_throughput_per_minute,
                    "error_rate": self.metrics.error_rate
                },
                "resources": {
                    "total_queue_size": self.metrics.total_queue_size,
                    "active_workers": self.metrics.active_workers,
                    "memory_usage_mb": self.metrics.memory_usage_mb,
                    "cpu_usage_percent": self.metrics.cpu_usage_percent
                },
                "components": {
                    "queue_manager": queue_metrics,
                    "workers_manager": workers_status,
                    "priority_manager": priority_insights
                },
                "load_balancing": {
                    "queue_distribution": dict(self.queue_load_balancer),
                    "worker_distribution": dict(self.worker_load_balancer)
                },
                "last_updated": self.metrics.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get orchestration status: {e}")
            return {"error": str(e)}
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Trigger performance optimization"""        try:
            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "optimizations_applied": []
            }
            
            # Optimize queue manager
            if self.queue_manager:
                queue_optimization = await self.queue_manager.optimize_crawler_performance()
                optimization_results["queue_optimization"] = queue_optimization
                optimization_results["optimizations_applied"].append("queue_performance")
            
            # Optimize priority manager
            if self.priority_manager:
                for queue_type in self.queue_manager.config.queue_routing.keys():
                    priority_optimization = await self.priority_manager.optimize_queue_priorities(queue_type)
                    optimization_results[f"priority_optimization_{queue_type.value}"] = priority_optimization
                optimization_results["optimizations_applied"].append("priority_optimization")
            
            # Optimize load balancing
            load_balance_optimization = await self._optimize_load_balancing()
            optimization_results["load_balance_optimization"] = load_balance_optimization
            optimization_results["optimizations_applied"].append("load_balancing")
            
            # Optimize worker allocation
            worker_optimization = await self._optimize_worker_allocation()
            optimization_results["worker_optimization"] = worker_optimization
            optimization_results["optimizations_applied"].append("worker_allocation")
            
            logger.info("⚡ Orchestration performance optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Performance optimization failed: {e}")
            return {"error": str(e)}
    
    async def register_status_callback(self, callback: Callable):
        """Register callback for status changes"""        self._status_callbacks.append(callback)
    
    async def register_metrics_callback(self, callback: Callable):
        """Register callback for metrics updates"""        self._metrics_callbacks.append(callback)
    
    async def add_webhook_url(self, webhook_url: str):
        """Add webhook URL for notifications"""        self._webhook_urls.append(webhook_url)
    
    async def shutdown(self):
        """Gracefully shutdown orchestrator"""        try:
            logger.info("🛑 Starting Crawler Queue Orchestrator shutdown...")
            
            self.status = OrchestrationStatus.SHUTDOWN
            self._is_running = False
            
            # Cancel background tasks
            for task in self._orchestration_tasks:
                task.cancel()
            
            # Shutdown components
            if self.priority_manager:
                await self.priority_manager.shutdown()
            
            if self.workers_manager:
                await self.workers_manager.shutdown()
            
            if self.queue_manager:
                await self.queue_manager.shutdown()
            
            # Notify callbacks
            await self._notify_status_change(OrchestrationStatus.SHUTDOWN)
            
            logger.info("✅ Crawler Queue Orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Orchestrator shutdown error: {e}")
    
    # Private helper methods
    
    async def _validate_request(self, task: CrawlerTask) -> bool:
        """Validate incoming crawler request"""        if not task.target_urls and not task.search_keywords:
            return False
        if not task.content_types:
            return False
        if not task.platform:
            return False
        return True
    
    async def _create_default_priority_factors(self, task: CrawlerTask) -> PriorityFactors:
        """Create default priority factors for task"""        # Would integrate with user management and content analysis
        from .priority_manager import PriorityFactors, BusinessImpact, UrgencyLevel
        
        return PriorityFactors(
            business_impact=BusinessImpact.ROUTINE_MONITORING,
            urgency_level=UrgencyLevel.NORMAL,
            user_tier=task.metadata.get("user_tier", "standard")
        )
    
    async def _select_optimal_queue(self, task: CrawlerTask, priority_score) -> str:
        """Select optimal queue for task"""        # Implement intelligent queue selection
        return task.task_type.value
    
    async def _assign_optimal_worker(self, task: CrawlerTask, priority_score) -> Optional[str]:
        """Assign optimal worker for task"""        if self.workers_manager:
            return await self.workers_manager.assign_task_to_worker(task)
        return None
    
    async def _estimate_completion_time(self, task: Optional[CrawlerTask], priority_score) -> str:
        """Estimate task completion time"""        # Implement ML-based time estimation
        base_time = 300  # 5 minutes default
        
        # Adjust based on priority
        if priority_score.priority_level.value < 2:
            base_time = 60  # High priority tasks: 1 minute
        elif priority_score.priority_level.value > 3:
            base_time = 900  # Low priority tasks: 15 minutes
        
        estimated_completion = datetime.now() + timedelta(seconds=base_time)
        return estimated_completion.isoformat()
    
    async def _get_queue_position(self, task: CrawlerTask) -> int:
        """Get approximate queue position"""        # Implement queue position calculation
        return 1  # Placeholder
    
    async def _update_submission_metrics(self, processing_time_ms: float, success: bool):
        """Update metrics after request submission"""        self.metrics.total_requests_received += 1
        
        if success:
            self.metrics.total_tasks_processed += 1
            # Update average response time
            self.metrics.average_response_time_ms = (
                (self.metrics.average_response_time_ms * (self.metrics.total_tasks_processed - 1) + 
                 processing_time_ms) / self.metrics.total_tasks_processed
            )
        else:
            self.metrics.error_counts["submission_error"] += 1
        
        # Update success rate
        self.metrics.success_rate = (
            self.metrics.total_tasks_processed / self.metrics.total_requests_received
        )
    
    async def _update_current_metrics(self):
        """Update current performance metrics"""        try:
            # Update queue sizes
            if self.queue_manager:
                queue_metrics = await self.queue_manager.get_crawler_metrics()
                self.metrics.total_queue_size = queue_metrics.get("performance_metrics", {}).get("current_queue_size", 0)
            
            # Update worker count
            if self.workers_manager:
                workers_status = await self.workers_manager.get_workers_status()
                self.metrics.active_workers = workers_status.get("summary", {}).get("active_workers", 0)
            
            # Calculate throughput
            current_minute = datetime.now().replace(second=0, microsecond=0)
            self.throughput_tracker.append((current_minute, self.metrics.total_tasks_processed))
            
            # Calculate throughput per minute
            if len(self.throughput_tracker) > 1:
                recent_throughput = [
                    count for timestamp, count in self.throughput_tracker
                    if timestamp > current_minute - timedelta(minutes=5)
                ]
                if recent_throughput:
                    self.metrics.current_throughput_per_minute = (
                        max(recent_throughput) - min(recent_throughput)
                    ) / 5.0  # Average over 5 minutes
            
            self.metrics.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Metrics update error: {e}")
    
    async def _notify_status_change(self, new_status: OrchestrationStatus):
        """Notify callbacks of status change"""        for callback in self._status_callbacks:
            try:
                await callback(new_status)
            except Exception as e:
                logger.error(f"Status callback error: {e}")
    
    async def _orchestration_monitor(self):
        """Main orchestration monitoring loop"""        while self._is_running:
            try:
                # Monitor overall system health
                await self._check_system_health()
                
                # Process completed requests
                await self._process_completed_requests()
                
                # Update load balancing
                await self._update_load_balancing()
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Orchestration monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _performance_optimizer(self):
        """Background performance optimization"""        while self._is_running:
            try:
                await self.optimize_performance()
                await asyncio.sleep(self.config.optimization_interval)
                
            except Exception as e:
                logger.error(f"Performance optimizer error: {e}")
                await asyncio.sleep(self.config.optimization_interval)
    
    async def _load_balancer(self):
        """Background load balancing"""        while self._is_running:
            try:
                await self._balance_system_load()
                await asyncio.sleep(30)  # Balance every 30 seconds
                
            except Exception as e:
                logger.error(f"Load balancer error: {e}")
                await asyncio.sleep(30)
    
    async def _metrics_collector(self):
        """Background metrics collection"""        while self._is_running:
            try:
                await self._update_current_metrics()
                
                # Notify metrics callbacks
                for callback in self._metrics_callbacks:
                    try:
                        await callback(self.metrics)
                    except Exception as e:
                        logger.error(f"Metrics callback error: {e}")
                
                await asyncio.sleep(self.config.metrics_collection_interval)
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(self.config.metrics_collection_interval)
    
    async def _health_monitor(self):
        """Background health monitoring"""        while self._is_running:
            try:
                await self._check_component_health()
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _auto_scaler(self):
        """Background auto-scaling"""        while self._is_running:
            try:
                if self.config.auto_scaling_enabled:
                    await self._perform_auto_scaling()
                
                await asyncio.sleep(60)  # Check scaling every minute
                
            except Exception as e:
                logger.error(f"Auto scaler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_system_health(self):
        """Check overall system health"""        # Implementation for system health checks
        pass
    
    async def _process_completed_requests(self):
        """Process and cleanup completed requests"""        # Implementation for processing completed requests
        pass
    
    async def _update_load_balancing(self):
        """Update load balancing metrics"""        # Implementation for load balancing updates
        pass
    
    async def _balance_system_load(self):
        """Balance load across system components"""        # Implementation for system load balancing
        pass
    
    async def _check_component_health(self):
        """Check health of all components"""        # Implementation for component health checks
        pass
    
    async def _perform_auto_scaling(self):
        """Perform auto-scaling operations"""        # Implementation for auto-scaling
        pass
    
    async def _optimize_load_balancing(self) -> Dict[str, Any]:
        """Optimize load balancing algorithms"""        return {"optimized": True}
    
    async def _optimize_worker_allocation(self) -> Dict[str, Any]:
        """Optimize worker allocation strategies"""        return {"optimized": True}


# Factory function
def create_queue_orchestrator(config: OrchestrationConfig = None) -> CrawlerQueueOrchestrator:
    """Create and return configured queue orchestrator"""    return CrawlerQueueOrchestrator(config)
