"""
Queue Workers Manager - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/queue_workers.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Queue Workers Manager - Distributed Worker Orchestration
Responsibility: Worker lifecycle management and task execution for crawlers
Technologies: AsyncIO, Worker Pools, Load Balancing, Health Monitoring
================================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Worker initialization → Task assignment → Platform specialization → 
Load balancing → Health monitoring → Performance optimization → Scaling decisions
"""

from typing import Any, Dict, List, Optional, Set, Callable, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import time
import psutil
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

from .crawler_queue_manager import CrawlerTask, PlatformType, CrawlerPriority

logger = logging.getLogger(__name__)


class WorkerStatus(Enum):
    """Worker status states"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    OFFLINE = "offline"


class WorkerType(Enum):
    """Specialized worker types"""
    GENERAL_PURPOSE = "general_purpose"
    PLATFORM_SPECIALIZED = "platform_specialized"
    PROTECTION_MONITOR = "protection_monitor"
    BULK_PROCESSOR = "bulk_processor"
    ANALYTICS_CRAWLER = "analytics_crawler"
    VIOLATION_HANDLER = "violation_handler"


@dataclass
class WorkerMetrics:
    """Individual worker performance metrics"""
    worker_id: str
    worker_type: WorkerType
    platform_specialty: Optional[PlatformType] = None
    
    # Performance metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    
    # System metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    network_io_mb: float = 0.0
    
    # Operational metrics
    created_at: datetime = field(default_factory=datetime.now)
    last_task_at: Optional[datetime] = None
    last_health_check: datetime = field(default_factory=datetime.now)
    uptime_seconds: float = 0.0
    
    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_error: Optional[str] = None
    last_error_at: Optional[datetime] = None


@dataclass
class WorkerCapacity:
    """Worker capacity and resource limits"""
    max_concurrent_tasks: int = 5
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    max_requests_per_minute: int = 60
    priority_task_slots: int = 2  # Reserved for high priority tasks


@dataclass
class WorkerConfig:
    """Worker configuration"""
    worker_type: WorkerType = WorkerType.GENERAL_PURPOSE
    platform_specialty: Optional[PlatformType] = None
    capacity: WorkerCapacity = field(default_factory=WorkerCapacity)
    
    # Behavior settings
    auto_scaling_enabled: bool = True
    health_check_interval: int = 30  # seconds
    idle_timeout: int = 300  # seconds
    retry_failed_tasks: bool = True
    
    # Resource limits
    max_execution_time: int = 600  # 10 minutes
    memory_limit_mb: int = 1024
    
    # Integration settings
    enable_detailed_logging: bool = True
    send_metrics_to_monitoring: bool = True


class CrawlerWorker:
    """
    🤖 Advanced Crawler Worker - IA-Influencer-Agent
    
    Enterprise-grade crawler worker featuring:
    - Multi-platform crawling capabilities
    - Intelligent resource management
    - Real-time health monitoring
    - Adaptive performance optimization
    - Error recovery and retry logic
    - Platform-specific optimizations
    """
    
    def __init__(self, worker_id: str, config: WorkerConfig = None):
        self.worker_id = worker_id
        self.config = config or WorkerConfig()
        
        # Worker state
        self.status = WorkerStatus.INITIALIZING
        self.current_tasks: Dict[str, CrawlerTask] = {}
        self.task_history: deque = deque(maxlen=100)
        
        # Metrics and monitoring
        self.metrics = WorkerMetrics(
            worker_id=worker_id,
            worker_type=self.config.worker_type,
            platform_specialty=self.config.platform_specialty
        )
        
        # Task execution
        self._executor = ThreadPoolExecutor(max_workers=self.config.capacity.max_concurrent_tasks)
        self._task_semaphore = asyncio.Semaphore(self.config.capacity.max_concurrent_tasks)
        self._priority_semaphore = asyncio.Semaphore(self.config.capacity.priority_task_slots)
        
        # Health monitoring
        self._is_running = False
        self._last_activity = datetime.now()
        self._health_monitor_task: Optional[asyncio.Task] = None
        
        # Callbacks
        self._task_completion_callback: Optional[Callable] = None
        self._health_status_callback: Optional[Callable] = None
    
    async def initialize(self) -> bool:
        """Initialize worker"""



        try:
            self.status = WorkerStatus.INITIALIZING
            self._is_running = True
            
            # Start health monitoring
            self._health_monitor_task = asyncio.create_task(self._health_monitor())
            
            # Platform-specific initialization
            await self._initialize_platform_specific()
            
            self.status = WorkerStatus.IDLE
            self.metrics.created_at = datetime.now()
            
            logger.info(f" Worker {self.worker_id} initialized")
            return True
            
        except Exception as e:
            logger.error(f" Worker {self.worker_id} initialization failed: {e}")
            self.status = WorkerStatus.ERROR
            return False
    
    async def execute_task(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute crawler task"""



        try:
            # Check worker capacity
            if not await self._can_accept_task(task):
                raise Exception("Worker at capacity")
            
            # Acquire semaphore
            semaphore = (self._priority_semaphore 
                        if task.priority.value < 2 
                        else self._task_semaphore)
            
            async with semaphore:
                self.status = WorkerStatus.BUSY
                self.current_tasks[task.task_id] = task
                self._last_activity = datetime.now()
                
                start_time = time.time()
                
                try:
                    # Execute task based on type
                    result = await self._execute_task_by_platform(task)
                    
                    # Update success metrics
                    execution_time = time.time() - start_time
                    await self._update_success_metrics(task, execution_time)
                    
                    return result
                    
                except Exception as e:
                    # Update failure metrics
                    await self._update_failure_metrics(task, str(e))
                    raise
                    
                finally:
                    # Cleanup
                    self.current_tasks.pop(task.task_id, None)
                    self.task_history.append({
                        "task_id": task.task_id,
                        "platform": task.platform.value,
                        "completed_at": datetime.now(),
                        "execution_time": time.time() - start_time,
                        "success": task.task_id not in [t.get("task_id") for t in self.task_history if t.get("failed")]
                    })
                    
                    # Update status
                    self.status = WorkerStatus.IDLE if not self.current_tasks else WorkerStatus.BUSY
            
        except Exception as e:
            logger.error(f" Worker {self.worker_id} task execution failed: {e}")
            raise
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel currently executing task"""



        try:
            task = self.current_tasks.get(task_id)
            if not task:
                return False
            
            # Cancel task execution (implementation depends on crawler type)
            await self._cancel_task_execution(task_id)
            
            # Remove from current tasks
            self.current_tasks.pop(task_id, None)
            
            logger.info(f" Task {task_id} cancelled on worker {self.worker_id}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to cancel task {task_id}: {e}")
            return False
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get comprehensive worker status"""



        try:
            # Update system metrics
            await self._update_system_metrics()
            
            return {
                "worker_id": self.worker_id,
                "status": self.status.value,
                "worker_type": self.config.worker_type.value,
                "platform_specialty": self.config.platform_specialty.value if self.config.platform_specialty else None,
                "current_tasks": len(self.current_tasks),
                "max_concurrent_tasks": self.config.capacity.max_concurrent_tasks,
                "metrics": {
                    "tasks_completed": self.metrics.tasks_completed,
                    "tasks_failed": self.metrics.tasks_failed,
                    "success_rate": self.metrics.success_rate,
                    "average_execution_time": self.metrics.average_execution_time,
                    "cpu_usage_percent": self.metrics.cpu_usage_percent,
                    "memory_usage_mb": self.metrics.memory_usage_mb,
                    "uptime_seconds": (datetime.now() - self.metrics.created_at).total_seconds(),
                    "last_activity": self._last_activity.isoformat()
                },
                "capacity": {
                    "available_slots": self.config.capacity.max_concurrent_tasks - len(self.current_tasks),
                    "memory_available_mb": self.config.capacity.max_memory_mb - self.metrics.memory_usage_mb,
                    "cpu_available_percent": self.config.capacity.max_cpu_percent - self.metrics.cpu_usage_percent
                },
                "health": await self._get_health_status()
            }
            
        except Exception as e:
            logger.error(f" Failed to get worker status: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown worker"""



        try:
            self.status = WorkerStatus.SHUTTING_DOWN
            self._is_running = False
            
            # Cancel health monitor
            if self._health_monitor_task:
                self._health_monitor_task.cancel()
            
            # Wait for current tasks to complete or timeout
            timeout = 30  # seconds
            start_time = time.time()
            
            while self.current_tasks and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)
            
            # Force cancel remaining tasks
            for task_id in list(self.current_tasks.keys()):
                await self.cancel_task(task_id)
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            self.status = WorkerStatus.OFFLINE
            logger.info(f" Worker {self.worker_id} shutdown completed")
            
        except Exception as e:
            logger.error(f" Worker {self.worker_id} shutdown error: {e}")
    
    def set_completion_callback(self, callback: Callable):
        """Set task completion callback"""
        self._task_completion_callback = callback
    
    def set_health_callback(self, callback: Callable):
        """Set health status callback"""
        self._health_status_callback = callback
    
    async def _can_accept_task(self, task: CrawlerTask) -> bool:
        """Check if worker can accept new task"""
        # Check current capacity
        if len(self.current_tasks) >= self.config.capacity.max_concurrent_tasks:
            return False
        
        # Check resource availability
        if self.metrics.memory_usage_mb > self.config.capacity.max_memory_mb * 0.9:
            return False
        
        if self.metrics.cpu_usage_percent > self.config.capacity.max_cpu_percent:
            return False
        
        # Check platform compatibility
        if (self.config.platform_specialty and 
            task.platform != self.config.platform_specialty):
            return False
        
        # Check worker status
        if self.status not in [WorkerStatus.IDLE, WorkerStatus.BUSY]:
            return False
        
        return True
    
    async def _execute_task_by_platform(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute task based on platform type"""



        try:
            if task.platform == PlatformType.YOUTUBE:
                return await self._execute_youtube_crawl(task)
            elif task.platform == PlatformType.INSTAGRAM:
                return await self._execute_instagram_crawl(task)
            elif task.platform == PlatformType.TIKTOK:
                return await self._execute_tiktok_crawl(task)
            elif task.platform == PlatformType.TWITTER:
                return await self._execute_twitter_crawl(task)
            elif task.platform == PlatformType.SPOTIFY:
                return await self._execute_spotify_crawl(task)
            else:
                return await self._execute_generic_crawl(task)
                
        except Exception as e:
            logger.error(f"Platform-specific crawl failed: {e}")
            raise
    
    async def _execute_youtube_crawl(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute YouTube-specific crawling"""
        # Placeholder for YouTube crawling implementation
        await asyncio.sleep(2)  # Simulate crawling
        return {
            "platform": "youtube",
            "status": "completed",
            "content_discovered": [],
            "violations_detected": [],
            "metadata": {"worker_id": self.worker_id}
        }
    
    async def _execute_instagram_crawl(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute Instagram-specific crawling"""
        # Placeholder for Instagram crawling implementation
        await asyncio.sleep(2)  # Simulate crawling
        return {
            "platform": "instagram",
            "status": "completed",
            "content_discovered": [],
            "violations_detected": [],
            "metadata": {"worker_id": self.worker_id}
        }
    
    async def _execute_tiktok_crawl(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute TikTok-specific crawling"""
        # Placeholder for TikTok crawling implementation
        await asyncio.sleep(2)  # Simulate crawling
        return {
            "platform": "tiktok",
            "status": "completed",
            "content_discovered": [],
            "violations_detected": [],
            "metadata": {"worker_id": self.worker_id}
        }
    
    async def _execute_twitter_crawl(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute Twitter-specific crawling"""
        # Placeholder for Twitter crawling implementation
        await asyncio.sleep(2)  # Simulate crawling
        return {
            "platform": "twitter",
            "status": "completed",
            "content_discovered": [],
            "violations_detected": [],
            "metadata": {"worker_id": self.worker_id}
        }
    
    async def _execute_spotify_crawl(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute Spotify-specific crawling"""
        # Placeholder for Spotify crawling implementation
        await asyncio.sleep(2)  # Simulate crawling
        return {
            "platform": "spotify",
            "status": "completed",
            "content_discovered": [],
            "violations_detected": [],
            "metadata": {"worker_id": self.worker_id}
        }
    
    async def _execute_generic_crawl(self, task: CrawlerTask) -> Dict[str, Any]:
        """Execute generic web crawling"""
        # Placeholder for generic crawling implementation
        await asyncio.sleep(2)  # Simulate crawling
        return {
            "platform": "generic",
            "status": "completed",
            "content_discovered": [],
            "violations_detected": [],
            "metadata": {"worker_id": self.worker_id}
        }
    
    async def _initialize_platform_specific(self):
        """Initialize platform-specific configurations"""
        if self.config.platform_specialty:
            # Platform-specific initialization
            logger.info(f"Initializing {self.config.platform_specialty.value} specialist worker")
    
    async def _update_success_metrics(self, task: CrawlerTask, execution_time: float):
        """Update metrics after successful task completion"""
        self.metrics.tasks_completed += 1
        self.metrics.total_execution_time += execution_time
        self.metrics.average_execution_time = (
            self.metrics.total_execution_time / self.metrics.tasks_completed
        )
        self.metrics.success_rate = (
            self.metrics.tasks_completed / 
            (self.metrics.tasks_completed + self.metrics.tasks_failed)
        )
        self.metrics.last_task_at = datetime.now()
        
        # Callback notification
        if self._task_completion_callback:
            await self._task_completion_callback(self.worker_id, task, True)
    
    async def _update_failure_metrics(self, task: CrawlerTask, error: str):
        """Update metrics after task failure"""
        self.metrics.tasks_failed += 1
        self.metrics.error_counts[error] += 1
        self.metrics.last_error = error
        self.metrics.last_error_at = datetime.now()
        self.metrics.success_rate = (
            self.metrics.tasks_completed / 
            (self.metrics.tasks_completed + self.metrics.tasks_failed)
        )
        
        # Callback notification
        if self._task_completion_callback:
            await self._task_completion_callback(self.worker_id, task, False)
    
    async def _update_system_metrics(self):
        """Update system resource metrics"""



        try:
            # CPU usage
            self.metrics.cpu_usage_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            self.metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # Network I/O (approximation)
            net_io = psutil.net_io_counters()
            self.metrics.network_io_mb = (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024
            
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")
    
    async def _health_monitor(self):
        """Background health monitoring"""
        while self._is_running:
            try:
                await self._update_system_metrics()
                
                # Check health status
                health_status = await self._get_health_status()
                
                # Update worker status based on health
                if health_status["status"] == "unhealthy":
                    if self.status != WorkerStatus.ERROR:
                        self.status = WorkerStatus.OVERLOADED
                elif health_status["status"] == "healthy":
                    if self.status == WorkerStatus.OVERLOADED:
                        self.status = WorkerStatus.IDLE if not self.current_tasks else WorkerStatus.BUSY
                
                # Health callback
                if self._health_status_callback:
                    await self._health_status_callback(self.worker_id, health_status)
                
                self.metrics.last_health_check = datetime.now()
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""



        try:
            health_score = 100.0
            issues = []
            
            # Check CPU usage
            if self.metrics.cpu_usage_percent > self.config.capacity.max_cpu_percent:
                health_score -= 30
                issues.append(f"High CPU usage: {self.metrics.cpu_usage_percent:.1f}%")
            
            # Check memory usage
            if self.metrics.memory_usage_mb > self.config.capacity.max_memory_mb:
                health_score -= 30
                issues.append(f"High memory usage: {self.metrics.memory_usage_mb:.1f}MB")
            
            # Check error rate
            total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
            if total_tasks > 0:
                error_rate = self.metrics.tasks_failed / total_tasks
                if error_rate > 0.1:  # 10% error rate threshold
                    health_score -= 20
                    issues.append(f"High error rate: {error_rate:.1%}")
            
            # Check idle timeout
            if self.status == WorkerStatus.IDLE:
                idle_time = (datetime.now() - self._last_activity).total_seconds()
                if idle_time > self.config.idle_timeout:
                    health_score -= 10
                    issues.append(f"Worker idle for {idle_time:.0f}s")
            
            # Determine overall health
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "health_score": health_score,
                "issues": issues,
                "last_check": self.metrics.last_health_check.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health status check failed: {e}")
            return {
                "status": "error",
                "health_score": 0,
                "issues": [f"Health check failed: {e}"],
                "last_check": datetime.now().isoformat()
            }
    
    async def _cancel_task_execution(self, task_id: str):
        """Cancel specific task execution"""
        # Implementation would depend on the crawler type
        # For now, just a placeholder
        logger.info(f"Cancelling task execution: {task_id}")


class QueueWorkersManager:
    """
     Queue Workers Manager - IA-Influencer-Agent
    
    Enterprise worker pool management featuring:
    - Dynamic worker scaling
    - Platform-specialized workers
    - Load balancing and optimization
    - Health monitoring and recovery
    - Performance analytics
    - Resource management
    """
    
    def __init__(self, max_workers: int = 20):
        self.max_workers = max_workers
        
        # Worker management
        self.workers: Dict[str, CrawlerWorker] = {}
        self.worker_assignments: Dict[str, str] = {}  # task_id -> worker_id
        
        # Load balancing
        self.platform_workers: Dict[PlatformType, Set[str]] = defaultdict(set)
        self.general_workers: Set[str] = set()
        
        # Metrics and monitoring
        self.total_metrics = {
            "workers_created": 0,
            "workers_destroyed": 0,
            "tasks_distributed": 0,
            "load_balancing_decisions": 0
        }
        
        # Management tasks
        self._is_running = False
        self._management_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> bool:
        """Initialize workers manager"""



        try:
            self._is_running = True
            
            # Create initial worker pool
            await self._create_initial_workers()
            
            # Start management tasks
            self._management_tasks.extend([
                asyncio.create_task(self._worker_health_monitor()),
                asyncio.create_task(self._load_balancer()),
                asyncio.create_task(self._auto_scaler()),
                asyncio.create_task(self._performance_optimizer())
            ])
            
            logger.info(" Queue Workers Manager initialized")
            return True
            
        except Exception as e:
            logger.error(f" Workers manager initialization failed: {e}")
            return False
    
    async def assign_task_to_worker(self, task: CrawlerTask) -> Optional[str]:
        """Assign task to best available worker"""



        try:
            # Find best worker for task
            worker_id = await self._find_best_worker(task)
            
            if not worker_id:
                # Create specialized worker if needed
                worker_id = await self._create_worker_for_task(task)
            
            if worker_id:
                # Assign task
                worker = self.workers[worker_id]
                asyncio.create_task(worker.execute_task(task))
                self.worker_assignments[task.task_id] = worker_id
                self.total_metrics["tasks_distributed"] += 1
                
                logger.info(f" Task {task.task_id} assigned to worker {worker_id}")
                return worker_id
            
            return None
            
        except Exception as e:
            logger.error(f" Failed to assign task to worker: {e}")
            return None
    
    async def get_workers_status(self) -> Dict[str, Any]:
        """Get comprehensive workers status"""



        try:
            workers_status = {}
            
            for worker_id, worker in self.workers.items():
                workers_status[worker_id] = await worker.get_worker_status()
            
            # Aggregate metrics
            total_workers = len(self.workers)
            active_workers = sum(1 for w in self.workers.values() if w.status == WorkerStatus.BUSY)
            idle_workers = sum(1 for w in self.workers.values() if w.status == WorkerStatus.IDLE)
            error_workers = sum(1 for w in self.workers.values() if w.status == WorkerStatus.ERROR)
            
            return {
                "summary": {
                    "total_workers": total_workers,
                    "active_workers": active_workers,
                    "idle_workers": idle_workers,
                    "error_workers": error_workers,
                    "max_workers": self.max_workers
                },
                "platform_distribution": {
                    platform.value: len(workers) 
                    for platform, workers in self.platform_workers.items()
                },
                "general_workers": len(self.general_workers),
                "total_metrics": self.total_metrics,
                "workers": workers_status
            }
            
        except Exception as e:
            logger.error(f" Failed to get workers status: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown all workers"""



        try:
            self._is_running = False
            
            # Cancel management tasks
            for task in self._management_tasks:
                task.cancel()
            
            # Shutdown all workers
            shutdown_tasks = [worker.shutdown() for worker in self.workers.values()]
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            
            self.workers.clear()
            self.worker_assignments.clear()
            
            logger.info(" All workers shutdown completed")
            
        except Exception as e:
            logger.error(f" Workers shutdown error: {e}")
    
    async def _create_initial_workers(self):
        """Create initial worker pool"""
        # Create general purpose workers
        for i in range(5):  # Start with 5 general workers
            await self._create_worker(WorkerType.GENERAL_PURPOSE)
        
        # Create specialized workers for major platforms
        for platform in [PlatformType.YOUTUBE, PlatformType.INSTAGRAM, PlatformType.TIKTOK]:
            await self._create_worker(WorkerType.PLATFORM_SPECIALIZED, platform)
    
    async def _create_worker(
        self, 
        worker_type: WorkerType, 
        platform_specialty: Optional[PlatformType] = None
    ) -> Optional[str]:
        """Create new worker"""



        try:
            if len(self.workers) >= self.max_workers:
                return None
            
            worker_id = f"worker_{worker_type.value}_{uuid.uuid4().hex[:8]}"
            
            config = WorkerConfig(
                worker_type=worker_type,
                platform_specialty=platform_specialty
            )
            
            worker = CrawlerWorker(worker_id, config)
            
            # Set callbacks
            worker.set_completion_callback(self._on_task_completion)
            worker.set_health_callback(self._on_health_status_change)
            
            # Initialize worker
            if await worker.initialize():
                self.workers[worker_id] = worker
                
                # Track by type
                if platform_specialty:
                    self.platform_workers[platform_specialty].add(worker_id)
                else:
                    self.general_workers.add(worker_id)
                
                self.total_metrics["workers_created"] += 1
                logger.info(f" Created worker {worker_id}")
                return worker_id
            
            return None
            
        except Exception as e:
            logger.error(f" Failed to create worker: {e}")
            return None
    
    async def _find_best_worker(self, task: CrawlerTask) -> Optional[str]:
        """Find best available worker for task"""



        try:
            # Prefer platform-specialized workers
            if task.platform in self.platform_workers:
                for worker_id in self.platform_workers[task.platform]:
                    worker = self.workers.get(worker_id)
                    if worker and await worker._can_accept_task(task):
                        return worker_id
            
            # Fall back to general purpose workers
            for worker_id in self.general_workers:
                worker = self.workers.get(worker_id)
                if worker and await worker._can_accept_task(task):
                    return worker_id
            
            # Check all workers as last resort
            for worker_id, worker in self.workers.items():
                if await worker._can_accept_task(task):
                    return worker_id
            
            return None
            
        except Exception as e:
            logger.error(f" Failed to find best worker: {e}")
            return None
    
    async def _create_worker_for_task(self, task: CrawlerTask) -> Optional[str]:
        """Create specialized worker for specific task if needed"""
        if len(self.workers) >= self.max_workers:
            return None
        
        # Create platform-specialized worker if beneficial
        if task.platform not in self.platform_workers or len(self.platform_workers[task.platform]) == 0:
            return await self._create_worker(WorkerType.PLATFORM_SPECIALIZED, task.platform)
        
        # Create general worker
        return await self._create_worker(WorkerType.GENERAL_PURPOSE)
    
    async def _worker_health_monitor(self):
        """Monitor worker health and restart unhealthy workers"""
        while self._is_running:
            try:
                unhealthy_workers = []
                
                for worker_id, worker in self.workers.items():
                    health = await worker._get_health_status()
                    if health["status"] == "unhealthy":
                        unhealthy_workers.append(worker_id)
                
                # Restart unhealthy workers
                for worker_id in unhealthy_workers:
                    await self._restart_worker(worker_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Worker health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _load_balancer(self):
        """Background load balancing"""
        while self._is_running:
            try:
                # Implement load balancing logic
                await self._balance_worker_load()
                await asyncio.sleep(30)  # Balance every 30 seconds
                
            except Exception as e:
                logger.error(f"Load balancer error: {e}")
                await asyncio.sleep(30)
    
    async def _auto_scaler(self):
        """Automatic worker scaling based on demand"""
        while self._is_running:
            try:
                await self._scale_workers_based_on_demand()
                await asyncio.sleep(60)  # Scale check every minute
                
            except Exception as e:
                logger.error(f"Auto scaler error: {e}")
                await asyncio.sleep(60)
    
    async def _performance_optimizer(self):
        """Optimize worker performance"""
        while self._is_running:
            try:
                await self._optimize_worker_performance()
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance optimizer error: {e}")
                await asyncio.sleep(300)
    
    async def _restart_worker(self, worker_id: str):
        """Restart unhealthy worker"""



        try:
            worker = self.workers.get(worker_id)
            if not worker:
                return
            
            # Get worker config
            config = worker.config
            
            # Shutdown old worker
            await worker.shutdown()
            
            # Remove from tracking
            self.workers.pop(worker_id, None)
            for platform_workers in self.platform_workers.values():
                platform_workers.discard(worker_id)
            self.general_workers.discard(worker_id)
            
            # Create new worker
            await self._create_worker(config.worker_type, config.platform_specialty)
            
            logger.info(f" Restarted worker {worker_id}")
            
        except Exception as e:
            logger.error(f" Failed to restart worker {worker_id}: {e}")
    
    async def _balance_worker_load(self):
        """Balance load across workers"""
        # Implementation for load balancing
        pass
    
    async def _scale_workers_based_on_demand(self):
        """Scale workers based on current demand"""
        # Implementation for auto-scaling
        pass
    
    async def _optimize_worker_performance(self):
        """Optimize worker performance"""
        # Implementation for performance optimization
        pass
    
    async def _on_task_completion(self, worker_id: str, task: CrawlerTask, success: bool):
        """Callback for task completion"""
        # Cleanup assignment
        self.worker_assignments.pop(task.task_id, None)
        
        # Log completion
        status = "completed" if success else "failed"
        logger.info(f" Task {task.task_id} {status} on worker {worker_id}")
    
    async def _on_health_status_change(self, worker_id: str, health_status: Dict[str, Any]):
        """Callback for worker health status changes"""
        if health_status["status"] == "unhealthy":
            logger.warning(f" Worker {worker_id} health degraded: {health_status['issues']}")


# Factory function
def create_workers_manager(max_workers: int = 20) -> QueueWorkersManager:
    """Create and return configured workers manager"""



    return QueueWorkersManager(max_workers)
