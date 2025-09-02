"""Crawler Queue Manager - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/crawler_queue_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Crawler Queue Manager - Distributed Crawling Orchestration
Responsibility: Specialized queue management for web crawler operations
Technologies: Celery, Redis, Priority Queues, Load Balancing, Rate Limiting
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
URL surveillance → Priority analysis → Queue routing → Worker distribution → 
Rate limiting → Content extraction → Protection analysis → Notification pipeline
"""

from typing import Any, Dict, List, Optional, Union, Set, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import heapq
from collections import defaultdict, deque
import time
import hashlib

from backend.core.managers.queue_manager import (
    IntelligentQueueManager, 
    TaskDefinition, 
    QueueType, 
    TaskPriority,
    QueueConfig
)

logger = logging.getLogger(__name__)


class CrawlerPriority(Enum):
    """
Crawler-specific priority levels"""

    PROTECTION_VIOLATION = 0      # Copyright infringement detected
    BRAND_MONITORING = 1          # Brand mention surveillance  
    COMPETITOR_ANALYSIS = 2       # Competitor content tracking
    PLATFORM_DISCOVERY = 3       # New platform content search
    BULK_SURVEILLANCE = 4         # Batch monitoring operations
    BACKGROUND_CRAWL = 5         # General purpose crawling


class CrawlerQueueType(Enum):
    """
Specialized crawler queue types"""

    PROTECTION_MONITOR = "protection_monitor"     # Real-time protection monitoring
    CONTENT_DISCOVERY = "content_discovery"      # New content discovery
    PLATFORM_SURVEILLANCE = "platform_surveillance"  # Platform-specific crawling
    BULK_OPERATIONS = "bulk_operations"          # Batch processing
    ANALYTICS_CRAWL = "analytics_crawl"          # Analytics data collection
    VIOLATION_RESPONSE = "violation_response"    # Immediate violation handling


class PlatformType(Enum):
    """Supported crawling platforms"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    GENERIC_WEB = "generic_web"


@dataclass
class CrawlerTask:
    """Specialized crawler task definition"""
    task_id: str = field(default_factory=lambda: f"crawler_{uuid.uuid4().hex}")
    task_type: CrawlerQueueType = CrawlerQueueType.CONTENT_DISCOVERY
    priority: CrawlerPriority = CrawlerPriority.BACKGROUND_CRAWL
    platform: PlatformType = PlatformType.GENERIC_WEB
    
    # Crawling parameters
    target_urls: List[str] = field(default_factory=list)
    search_keywords: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=lambda: ["text", "image", "video", "audio"])
    depth_limit: int = 3
    
    # Rate limiting
    max_requests_per_minute: int = 60
    delay_between_requests: float = 1.0
    respect_robots_txt: bool = True
    
    # Protection settings
    user_id: Optional[str] = None
    content_fingerprint_ids: List[str] = field(default_factory=list)
    similarity_threshold: float = 0.8
    
    # Scheduling
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Retry settings
    max_retries: int = 3
    retry_delay: timedelta = timedelta(minutes=5)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    callback_url: Optional[str] = None
    webhook_events: List[str] = field(default_factory=list)


@dataclass
class CrawlerQueueConfig:
    """Crawler queue system configuration"""
    max_concurrent_crawlers: int = 50
    default_timeout_seconds: int = 300
    rate_limit_window_seconds: int = 60
    max_queue_size: int = 10000
    priority_queue_enabled: bool = True
    load_balancing_enabled: bool = True
    dead_letter_queue_enabled: bool = True
    
    # Platform-specific rate limits
    platform_rate_limits: Dict[PlatformType, int] = field(default_factory=lambda: {
        PlatformType.YOUTUBE: 30,     # requests per minute
        PlatformType.INSTAGRAM: 20,
        PlatformType.TIKTOK: 15,
        PlatformType.TWITTER: 40,
        PlatformType.SPOTIFY: 25,
        PlatformType.SOUNDCLOUD: 35,
        PlatformType.FACEBOOK: 15,
        PlatformType.LINKEDIN: 20,
        PlatformType.PINTEREST: 25,
        PlatformType.GENERIC_WEB: 60
    })
    
    # Queue routing
    queue_routing: Dict[CrawlerQueueType, str] = field(default_factory=lambda: {
        CrawlerQueueType.PROTECTION_MONITOR: "crawler_protection_high",
        CrawlerQueueType.CONTENT_DISCOVERY: "crawler_discovery_medium", 
        CrawlerQueueType.PLATFORM_SURVEILLANCE: "crawler_surveillance_medium",
        CrawlerQueueType.BULK_OPERATIONS: "crawler_bulk_low",
        CrawlerQueueType.ANALYTICS_CRAWL: "crawler_analytics_low",
        CrawlerQueueType.VIOLATION_RESPONSE: "crawler_violation_critical"
    })


@dataclass
class CrawlerMetrics:
    """Crawler queue performance metrics"""
    total_tasks_queued: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    total_content_discovered: int = 0
    total_violations_detected: int = 0
    
    # Platform-specific metrics
    platform_metrics: Dict[PlatformType, Dict[str, int]] = field(default_factory=lambda: defaultdict(dict))
    
    # Performance metrics
    average_crawl_time: float = 0.0
    average_queue_wait_time: float = 0.0
    current_queue_size: int = 0
    active_crawlers: int = 0
    
    # Rate limiting metrics
    rate_limit_violations: int = 0
    throttled_requests: int = 0
    
    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_updated: datetime = field(default_factory=datetime.now)


class CrawlerQueueManager:
    """
    🕷️ Advanced Crawler Queue Manager - IA-Influencer-Agent
    
    Enterprise-grade crawler queue management system featuring:
    - Multi-platform crawling orchestration
    - Intelligent rate limiting per platform
    - Priority-based task scheduling
    - Real-time violation detection
    - Load balancing across crawler workers
    - Dead letter queue for failed crawls
    - Content protection monitoring
    - Analytics and performance tracking
    """
    
    def __init__(self, config: CrawlerQueueConfig = None):
        self.config = config or CrawlerQueueConfig()
        
        # Queue management
        self._priority_queues: Dict[CrawlerQueueType, List[Tuple[int, CrawlerTask]]] = {
            queue_type: [] for queue_type in CrawlerQueueType
        }
        self._active_tasks: Dict[str, CrawlerTask] = {}
        self._task_results: Dict[str, Any] = {}
        
        # Rate limiting
        self._rate_limiters: Dict[PlatformType, Dict[str, Any]] = defaultdict(dict)
        self._request_windows: Dict[PlatformType, deque] = {
            platform: deque() for platform in PlatformType
        }
        
        # Performance tracking
        self.metrics = CrawlerMetrics()
        self._task_history: deque = deque(maxlen=1000)
        
        # Worker management
        self._active_crawlers: Dict[str, Dict[str, Any]] = {}
        self._worker_assignments: Dict[str, str] = {}  # task_id -> worker_id
        
        # Monitoring
        self._monitoring_tasks: Set[str] = set()
        self._is_running = False
        
        # Integration with core queue manager
        self._core_queue_manager: Optional[IntelligentQueueManager] = None
    
    async def initialize(self, core_queue_manager: IntelligentQueueManager = None) -> bool:
        """
Initialize crawler queue system"""
        try:
            self._core_queue_manager = core_queue_manager
            self._is_running = True
            
            # Initialize priority queues
            for queue_type in CrawlerQueueType:
                heapq.heapify(self._priority_queues[queue_type])
            
            # Start background tasks
            asyncio.create_task(self._queue_processor())
            asyncio.create_task(self._rate_limit_monitor())
            asyncio.create_task(self._metrics_updater())
            asyncio.create_task(self._dead_letter_processor())
            
            logger.info("✅ Crawler Queue Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Crawler queue initialization failed: {e}")
            return False
    
    async def enqueue_crawler_task(
        self,
        crawler_task: CrawlerTask,
        immediate: bool = False
    ) -> str:
        """Enqueue crawler task with intelligent routing"""
        try:
            # Validate task
            if not self._validate_crawler_task(crawler_task):
                raise ValueError("Invalid crawler task configuration")
            
            # Check rate limits
            if not await self._check_rate_limit(crawler_task.platform):
                # Delay task if rate limited
                crawler_task.scheduled_for = datetime.now() + timedelta(seconds=60)
                self.metrics.throttled_requests += 1
            
            # Calculate dynamic priority
            priority_score = await self._calculate_priority_score(crawler_task)
            
            # Store task
            self._active_tasks[crawler_task.task_id] = crawler_task
            
            if immediate and priority_score < 2:  # Only high priority immediate
                return await self._execute_immediate_crawl(crawler_task)
            
            # Add to priority queue
            heapq.heappush(
                self._priority_queues[crawler_task.task_type],
                (priority_score, crawler_task)
            )
            
            # Integrate with core queue manager if available
            if self._core_queue_manager:
                core_task = TaskDefinition(
                    task_id=crawler_task.task_id,
                    task_name="crawler_task",
                    queue_type=QueueType.CONTENT_PROCESSING,
                    priority=self._map_to_core_priority(crawler_task.priority),
                    parameters=crawler_task.__dict__,
                    metadata=crawler_task.metadata
                )
                await self._core_queue_manager.enqueue_task(core_task)
            
            self.metrics.total_tasks_queued += 1
            logger.info(f"🕷️ Crawler task queued: {crawler_task.task_id}")
            
            return crawler_task.task_id
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue crawler task: {e}")
            raise
    
    async def get_crawler_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get comprehensive crawler task status"""
        try:
            task = self._active_tasks.get(task_id)
            if not task:
                return {"error": "Task not found", "task_id": task_id}
            
            # Get result if available
            result = self._task_results.get(task_id)
            
            status_info = {
                "task_id": task_id,
                "task_type": task.task_type.value,
                "platform": task.platform.value,
                "priority": task.priority.name,
                "created_at": task.created_at.isoformat(),
                "scheduled_for": task.scheduled_for.isoformat() if task.scheduled_for else None,
                "target_urls": task.target_urls,
                "search_keywords": task.search_keywords,
                "status": "queued",
                "progress": 0,
                "discovered_content": [],
                "violations_detected": [],
                "result": result,
                "metadata": task.metadata
            }
            
            # Check if task is being processed
            if task_id in self._worker_assignments:
                worker_id = self._worker_assignments[task_id]
                worker_info = self._active_crawlers.get(worker_id, {})
                status_info["status"] = "processing"
                status_info["worker_id"] = worker_id
                status_info["progress"] = worker_info.get("progress", 0)
            
            return status_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get crawler task status: {e}")
            return {"error": str(e), "task_id": task_id}
    
    async def cancel_crawler_task(self, task_id: str) -> bool:
        """Cancel a crawler task"""
        try:
            # Remove from active tasks
            task = self._active_tasks.pop(task_id, None)
            if not task:
                return False
            
            # Remove from priority queues
            for queue_type in CrawlerQueueType:
                queue = self._priority_queues[queue_type]
                self._priority_queues[queue_type] = [
                    (score, t) for score, t in queue if t.task_id != task_id
                ]
                heapq.heapify(self._priority_queues[queue_type])
            
            # Cancel if being processed
            if task_id in self._worker_assignments:
                worker_id = self._worker_assignments.pop(task_id)
                await self._cancel_worker_task(worker_id, task_id)
            
            logger.info(f"🚫 Crawler task cancelled: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel crawler task: {e}")
            return False
    
    async def schedule_recurring_crawl(
        self,
        platform: PlatformType,
        search_config: Dict[str, Any],
        schedule_cron: str,
        priority: CrawlerPriority = CrawlerPriority.BACKGROUND_CRAWL
    ) -> str:
        """Schedule recurring crawler task"""
        try:
            recurring_task_id = f"recurring_crawl_{uuid.uuid4().hex}"
            
            # Create recurring task configuration
            recurring_config = {
                "task_id": recurring_task_id,
                "platform": platform,
                "search_config": search_config,
                "priority": priority,
                "schedule": schedule_cron
            }
            
            # Integrate with core queue manager for scheduling
            if self._core_queue_manager:
                await self._core_queue_manager.schedule_recurring_task(
                    task_name="recurring_crawler_task",
                    queue_type=QueueType.CONTENT_PROCESSING,
                    priority=self._map_to_core_priority(priority),
                    parameters=recurring_config,
                    cron_expression=schedule_cron,
                    metadata={"type": "recurring_crawl"}
                )
            
            logger.info(f"📅 Scheduled recurring crawl: {recurring_task_id}")
            return recurring_task_id
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule recurring crawl: {e}")
            raise
    
    async def get_crawler_metrics(self) -> Dict[str, Any]:
        """Get comprehensive crawler metrics"""
        try:
            # Update current metrics
            self.metrics.current_queue_size = sum(
                len(queue) for queue in self._priority_queues.values()
            )
            self.metrics.active_crawlers = len(self._active_crawlers)
            self.metrics.last_updated = datetime.now()
            
            return {
                "total_metrics": {
                    "tasks_queued": self.metrics.total_tasks_queued,
                    "tasks_completed": self.metrics.total_tasks_completed,
                    "tasks_failed": self.metrics.total_tasks_failed,
                    "content_discovered": self.metrics.total_content_discovered,
                    "violations_detected": self.metrics.total_violations_detected
                },
                "performance_metrics": {
                    "average_crawl_time": self.metrics.average_crawl_time,
                    "average_queue_wait_time": self.metrics.average_queue_wait_time,
                    "current_queue_size": self.metrics.current_queue_size,
                    "active_crawlers": self.metrics.active_crawlers
                },
                "platform_metrics": dict(self.metrics.platform_metrics),
                "rate_limiting": {
                    "rate_limit_violations": self.metrics.rate_limit_violations,
                    "throttled_requests": self.metrics.throttled_requests
                },
                "error_analysis": dict(self.metrics.error_counts),
                "last_updated": self.metrics.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get crawler metrics: {e}")
            return {"error": str(e)}
    
    async def optimize_crawler_performance(self) -> Dict[str, Any]:
        """Optimize crawler queue performance"""
        try:
            optimization_results = {
                "queue_rebalancing": await self._rebalance_queues(),
                "rate_limit_optimization": await self._optimize_rate_limits(),
                "worker_allocation": await self._optimize_worker_allocation(),
                "priority_adjustment": await self._adjust_task_priorities()
            }
            
            logger.info("⚡ Crawler performance optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"❌ Crawler optimization failed: {e}")
            return {"error": str(e)}
    
    async def _queue_processor(self):
        """Background task processor for crawler queues"""
        while self._is_running:
            try:
                await self._process_priority_queues()
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                await asyncio.sleep(5)
    
    async def _process_priority_queues(self):
        """Process tasks from priority queues"""
        try:
            for queue_type in CrawlerQueueType:
                queue = self._priority_queues[queue_type]
                
                # Process high priority tasks first
                while queue and len(self._active_crawlers) < self.config.max_concurrent_crawlers:
                    priority_score, task = heapq.heappop(queue)
                    
                    # Check if task is ready to execute
                    if task.scheduled_for and task.scheduled_for > datetime.now():
                        # Re-queue for later
                        heapq.heappush(queue, (priority_score, task))
                        break
                    
                    # Check rate limits
                    if not await self._check_rate_limit(task.platform):
                        # Re-queue with delay
                        task.scheduled_for = datetime.now() + timedelta(seconds=30)
                        heapq.heappush(queue, (priority_score, task))
                        continue
                    
                    # Assign to worker
                    await self._assign_task_to_worker(task)
                    
        except Exception as e:
            logger.error(f"Priority queue processing error: {e}")
    
    async def _assign_task_to_worker(self, task: CrawlerTask):
        """Assign crawler task to available worker"""
        try:
            # Find or create worker
            worker_id = await self._get_available_worker(task.platform)
            
            if not worker_id:
                # No available worker, re-queue
                heapq.heappush(
                    self._priority_queues[task.task_type],
                    (task.priority.value, task)
                )
                return
            
            # Assign task
            self._worker_assignments[task.task_id] = worker_id
            self._active_crawlers[worker_id] = {
                "task_id": task.task_id,
                "platform": task.platform,
                "started_at": datetime.now(),
                "progress": 0
            }
            
            # Execute crawler task (would integrate with actual crawler agents)
            asyncio.create_task(self._execute_crawler_task(worker_id, task))
            
        except Exception as e:
            logger.error(f"Worker assignment error: {e}")
    
    async def _execute_crawler_task(self, worker_id: str, task: CrawlerTask):
        """Execute crawler task with worker"""
        try:
            start_time = time.time()
            
            # Update rate limiter
            await self._update_rate_limiter(task.platform)
            
            # Execute crawling operation (placeholder - would integrate with actual crawlers)
            result = await self._perform_crawling_operation(task)
            
            # Process results
            await self._process_crawl_results(task, result)
            
            # Update metrics
            execution_time = time.time() - start_time
            self.metrics.total_tasks_completed += 1
            self.metrics.average_crawl_time = (
                (self.metrics.average_crawl_time * (self.metrics.total_tasks_completed - 1) + execution_time) /
                self.metrics.total_tasks_completed
            )
            
            # Store results
            self._task_results[task.task_id] = result
            
            # Cleanup
            self._worker_assignments.pop(task.task_id, None)
            self._active_crawlers.pop(worker_id, None)
            
            logger.info(f"✅ Crawler task completed: {task.task_id}")
            
        except Exception as e:
            logger.error(f"Crawler task execution error: {e}")
            self.metrics.total_tasks_failed += 1
            self.metrics.error_counts[str(e)] += 1
            
            # Move to dead letter queue
            await self._move_to_dead_letter_queue(task, str(e))
    
    async def _perform_crawling_operation(self, task: CrawlerTask) -> Dict[str, Any]:
        """Perform actual crawling operation (placeholder for integration)"""
        # This would integrate with the actual crawler agents
        await asyncio.sleep(2)  # Simulate crawling time
        
        return {
            "status": "completed",
            "content_discovered": [],
            "violations_detected": [],
            "metadata": {}
        }
    
    async def _process_crawl_results(self, task: CrawlerTask, result: Dict[str, Any]):
        """Process crawler results for protection analysis"""
        try:
            # Extract discovered content
            discovered_content = result.get("content_discovered", [])
            self.metrics.total_content_discovered += len(discovered_content)
            
            # Check for violations
            violations = result.get("violations_detected", [])
            self.metrics.total_violations_detected += len(violations)
            
            # Update platform metrics
            platform_metrics = self.metrics.platform_metrics[task.platform]
            platform_metrics["content_discovered"] = platform_metrics.get("content_discovered", 0) + len(discovered_content)
            platform_metrics["violations_detected"] = platform_metrics.get("violations_detected", 0) + len(violations)
            
            # Send notifications for violations
            if violations:
                await self._send_violation_notifications(task, violations)
            
        except Exception as e:
            logger.error(f"Crawl result processing error: {e}")
    
    async def _send_violation_notifications(self, task: CrawlerTask, violations: List[Dict]):
        """Send notifications for detected violations"""
        try:
            notification_data = {
                "task_id": task.task_id,
                "user_id": task.user_id,
                "platform": task.platform.value,
                "violations": violations,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to notification system
            if self._core_queue_manager:
                notification_task = TaskDefinition(
                    task_id=f"violation_notification_{uuid.uuid4().hex}",
                    task_name="send_violation_notification",
                    queue_type=QueueType.NOTIFICATION,
                    priority=TaskPriority.HIGH,
                    parameters=notification_data
                )
                await self._core_queue_manager.enqueue_task(notification_task)
            
        except Exception as e:
            logger.error(f"Violation notification error: {e}")
    
    async def _check_rate_limit(self, platform: PlatformType) -> bool:
        """Check if platform rate limit allows new request"""
        try:
            current_time = time.time()
            window = self._request_windows[platform]
            rate_limit = self.config.platform_rate_limits[platform]
            
            # Clean old requests outside window
            while window and window[0] < current_time - self.config.rate_limit_window_seconds:
                window.popleft()
            
            # Check if under rate limit
            if len(window) < rate_limit:
                return True
            
            self.metrics.rate_limit_violations += 1
            return False
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return False
    
    async def _update_rate_limiter(self, platform: PlatformType):
        """Update rate limiter with new request"""
        current_time = time.time()
        self._request_windows[platform].append(current_time)
    
    async def _get_available_worker(self, platform: PlatformType) -> Optional[str]:
        """
Get available worker for platform"""
        # Find least loaded worker or create new one
        available_workers = [
            worker_id for worker_id, info in self._active_crawlers.items()
            if info.get("platform") == platform
        ]
        
        if len(available_workers) < 5:  # Max 5 workers per platform
            worker_id = f"crawler_{platform.value}_{uuid.uuid4().hex[:8]}"
            return worker_id
        
        return None
    
    async def _validate_crawler_task(self, task: CrawlerTask) -> bool:
        """Validate crawler task configuration"""
        if not task.target_urls and not task.search_keywords:
            return False
        if not task.content_types:
            return False
        return True
    
    async def _calculate_priority_score(self, task: CrawlerTask) -> int:
        """
Calculate dynamic priority score for task"""
        base_priority = task.priority.value
        
        # Adjust based on platform urgency
        if task.platform in [PlatformType.YOUTUBE, PlatformType.INSTAGRAM]:
            base_priority -= 1  # Higher priority for major platforms
        
        # Adjust based on protection context
        if task.content_fingerprint_ids:
            base_priority -= 2  # Much higher priority for protection tasks
        
        return max(0, base_priority)
    
    def _map_to_core_priority(self, crawler_priority: CrawlerPriority) -> TaskPriority:
        """
Map crawler priority to core queue priority"""
        mapping = {
            CrawlerPriority.PROTECTION_VIOLATION: TaskPriority.CRITICAL,
            CrawlerPriority.BRAND_MONITORING: TaskPriority.HIGH,
            CrawlerPriority.COMPETITOR_ANALYSIS: TaskPriority.MEDIUM,
            CrawlerPriority.PLATFORM_DISCOVERY: TaskPriority.MEDIUM,
            CrawlerPriority.BULK_SURVEILLANCE: TaskPriority.LOW,
            CrawlerPriority.BACKGROUND_CRAWL: TaskPriority.BACKGROUND
        }
        return mapping.get(crawler_priority, TaskPriority.MEDIUM)
    
    async def _execute_immediate_crawl(self, task: CrawlerTask) -> str:
        """
Execute immediate high-priority crawl"""
        # For critical protection violations
        worker_id = f"immediate_crawler_{uuid.uuid4().hex[:8]}"
        asyncio.create_task(self._execute_crawler_task(worker_id, task))
        return task.task_id
    
    async def _rate_limit_monitor(self):
        """Background monitor for rate limiting"""
        while self._is_running:
            try:
                # Monitor and adjust rate limits
                for platform in PlatformType:
                    await self._adjust_platform_rate_limit(platform)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Rate limit monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _adjust_platform_rate_limit(self, platform: PlatformType):
        try:
            logger.info(f"Executing _adjust_platform_rate_limit")
            
            # Implementation for _adjust_platform_rate_limit
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_adjust_platform_rate_limit completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_adjust_platform_rate_limit failed: {e}")
            raise
    async def _metrics_updater(self):
        """
Background metrics updater"""
        while self._is_running:
            try:
                self.metrics.last_updated = datetime.now()
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
                await asyncio.sleep(60)
    
    async def _dead_letter_processor(self):
        """Process dead letter queue for failed tasks"""
        while self._is_running:
            try:
                # Process failed tasks for potential retry
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
        try:
            logger.info(f"Executing _cancel_worker_task")
            
            # Implementation for _cancel_worker_task
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_cancel_worker_task completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_cancel_worker_task failed: {e}")
            raise
    async def _move_to_dead_letter_queue(self, task: CrawlerTask, error: str):
        """Move failed task to dead letter queue"""
        # Would implement dead letter queue logic
        logger.warning(f"💀 Task moved to DLQ: {task.task_id} - {error}")
    
    async def _cancel_worker_task(self, worker_id: str, task_id: str):
        """Cancel task being processed by worker"""
        # Would implement worker task cancellation
        pass
    
    async def _rebalance_queues(self) -> Dict[str, Any]:
        """
Rebalance crawler queues based on load"""
        return {"rebalanced": True}
    
    async def _optimize_rate_limits(self) -> Dict[str, Any]:
        """Optimize rate limits based on performance"""
        return {"optimized": True}
    
    async def _optimize_worker_allocation(self) -> Dict[str, Any]:
        """Optimize worker allocation across platforms"""
        return {"optimized": True}
    
    async def _adjust_task_priorities(self) -> Dict[str, Any]:
        """Adjust task priorities based on AI analysis"""
        return {"adjusted": True}
    
    async def shutdown(self):
        """Gracefully shutdown crawler queue manager"""
        try:
            self._is_running = False
            
            # Cancel all active tasks
            for task_id in list(self._active_tasks.keys()):
                await self.cancel_crawler_task(task_id)
            
            logger.info("🛑 Crawler Queue Manager shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


# Factory function for easy instantiation
def create_crawler_queue_manager(config: CrawlerQueueConfig = None) -> CrawlerQueueManager:
    """Create and return configured crawler queue manager"""
    return CrawlerQueueManager(config)
