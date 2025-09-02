"""Crawler Coordination and Management System
==========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
Unauthorized use, copying or distribution prohibited.

Master coordinator for managing multiple web crawlers simultaneously.
Handles task distribution, resource allocation, monitoring, and error recovery
across all supported platforms for optimal content surveillance.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import redis
import json
from sqlalchemy.orm import Session

from .config import CrawlerConfig, CrawlerType, PlatformConfig
from .platforms import (
    YouTubeCrawler, TikTokCrawler, InstagramCrawler, 
    TwitterCrawler, GenericWebCrawler
)
from .detection import ViolationDetector
from .evidence import EvidenceCollector
from .scheduler import CrawlingScheduler

logger = logging.getLogger(__name__)

@dataclass
class CrawlerTask:
    """
Represents a crawling task with metadata."""
    
    task_id: str
    platform: CrawlerType
    target_urls: List[str]
    content_fingerprints: List[str]
    priority: int = 1  # 1=highest, 5=lowest
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed, cancelled
    error_message: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)

@dataclass  
class CrawlerStats:
    """Statistics for crawler performance monitoring."""
    
    platform: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    violations_detected: int = 0
    evidence_collected: int = 0
    avg_response_time: float = 0.0
    last_activity: Optional[datetime] = None
    error_rate: float = 0.0

class CrawlerCoordinator:
    """
    Master coordinator for multi-platform web crawling operations.
    
    Manages crawler lifecycle, task scheduling, resource allocation,
    and violation detection across all supported platforms.
    """
    
    def __init__(
        self,
        config: CrawlerConfig,
        database_session: Session,
        redis_client: redis.Redis,
        violation_detector: ViolationDetector,
        evidence_collector: EvidenceCollector
    ):
        self.config = config
        self.db_session = database_session
        self.redis_client = redis_client
        self.violation_detector = violation_detector
        self.evidence_collector = evidence_collector
        
        # Initialize crawlers
        self.crawlers: Dict[CrawlerType, Any] = {}
        self._initialize_crawlers()
        
        # Task management
        self.task_queue: List[CrawlerTask] = []
        self.running_tasks: Dict[str, CrawlerTask] = {}
        self.completed_tasks: Dict[str, CrawlerTask] = {}
        
        # Performance monitoring
        self.crawler_stats: Dict[str, CrawlerStats] = {}
        self._initialize_stats()
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(
            max_workers=config.concurrent_crawlers,
            thread_name_prefix="crawler_worker"
        )
        
        # Scheduler for automated crawling
        self.scheduler = CrawlingScheduler(self)
        
        # Status tracking
        self.is_running = False
        self.start_time: Optional[datetime] = None
        
        logger.info("CrawlerCoordinator initialized with %d platforms", len(self.crawlers))
    
    def _initialize_crawlers(self):
        """Initialize platform-specific crawlers."""
        
        for platform_type in CrawlerType:
            platform_config = self.config.get_platform_config(platform_type)
            
            if not platform_config or not platform_config.enabled:
                logger.info("Skipping disabled platform: %s", platform_type.value)
                continue
            
            try:
                if platform_type == CrawlerType.YOUTUBE:
                    crawler = YouTubeCrawler(platform_config, self.db_session)
                elif platform_type == CrawlerType.TIKTOK:
                    crawler = TikTokCrawler(platform_config, self.db_session)
                elif platform_type == CrawlerType.INSTAGRAM:
                    crawler = InstagramCrawler(platform_config, self.db_session)
                elif platform_type == CrawlerType.TWITTER:
                    crawler = TwitterCrawler(platform_config, self.db_session)
                elif platform_type == CrawlerType.GENERIC_WEB:
                    crawler = GenericWebCrawler(platform_config, self.db_session)
                else:
                    logger.warning("Unknown platform type: %s", platform_type)
                    continue
                
                self.crawlers[platform_type] = crawler
                logger.info("Initialized crawler for platform: %s", platform_type.value)
                
            except Exception as e:
                logger.error("Failed to initialize crawler for %s: %s", platform_type.value, str(e))
    
    def _initialize_stats(self):
        """Initialize performance statistics for all platforms."""
        for platform_type in self.crawlers:
            self.crawler_stats[platform_type.value] = CrawlerStats(
                platform=platform_type.value
            )
    
    async def start(self):
        """
Start the crawler coordinator and all managed crawlers."""
        if self.is_running:
            logger.warning("Coordinator is already running")
            return
        
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        logger.info("Starting CrawlerCoordinator with %d crawlers", len(self.crawlers))
        
        try:
            # Start scheduler for automated tasks
            await self.scheduler.start()
            
            # Start main coordination loop
            await self._coordination_loop()
            
        except Exception as e:
            logger.error("Error in crawler coordinator: %s", str(e))
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the crawler coordinator and cleanup resources."""
        if not self.is_running:
            return
        
        logger.info("Stopping CrawlerCoordinator...")
        
        self.is_running = False
        
        # Stop scheduler
        await self.scheduler.stop()
        
        # Cancel running tasks
        for task_id in list(self.running_tasks.keys()):
            await self.cancel_task(task_id)
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        # Close crawler connections
        for crawler in self.crawlers.values():
            if hasattr(crawler, 'close'):
                await crawler.close()
        
        logger.info("CrawlerCoordinator stopped")
    
    async def _coordination_loop(self):
        """Main coordination loop for task processing."""
        
        while self.is_running:
            try:
                # Process pending tasks
                await self._process_task_queue()
                
                # Monitor running tasks
                await self._monitor_running_tasks()
                
                # Update statistics
                await self._update_statistics()
                
                # Cleanup completed tasks
                await self._cleanup_old_tasks()
                
                # Health check on crawlers
                await self._health_check_crawlers()
                
                # Wait before next iteration
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error("Error in coordination loop: %s", str(e))
                await asyncio.sleep(10)
    
    async def submit_crawling_task(
        self,
        platform: CrawlerType,
        target_urls: List[str],
        content_fingerprints: List[str],
        priority: int = 3,
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """
        Submit a new crawling task for processing.
        
        Args:
            platform: Target platform to crawl
            target_urls: List of URLs to monitor
            content_fingerprints: Fingerprints to match against
            priority: Task priority (1=highest, 5=lowest)
            scheduled_at: Optional scheduled execution time
            
        Returns:
            Task ID for tracking
        """
        
        if platform not in self.crawlers:
            raise ValueError(f"Platform {platform.value} is not supported or enabled")
        
        task_id = f"{platform.value}_{datetime.utcnow().isoformat()}_{len(self.task_queue)}"
        
        task = CrawlerTask(
            task_id=task_id,
            platform=platform,
            target_urls=target_urls,
            content_fingerprints=content_fingerprints,
            priority=priority,
            scheduled_at=scheduled_at
        )
        
        # Add to queue (sorted by priority)
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: (t.priority, t.created_at))
        
        # Store in Redis for persistence
        await self._store_task_state(task)
        
        logger.info("Submitted crawling task %s for platform %s", task_id, platform.value)
        
        return task_id
    
    async def _process_task_queue(self):
        """Process pending tasks from the queue."""
        
        if not self.task_queue:
            return
        
        # Check available capacity
        available_slots = self.config.concurrent_crawlers - len(self.running_tasks)
        if available_slots <= 0:
            return
        
        # Process tasks up to available capacity
        tasks_to_process = []
        for task in self.task_queue[:available_slots]:
            # Check if task should be executed now
            if task.scheduled_at and task.scheduled_at > datetime.utcnow():
                continue
            tasks_to_process.append(task)
        
        for task in tasks_to_process:
            await self._execute_task(task)
            self.task_queue.remove(task)
    
    async def _execute_task(self, task: CrawlerTask):
        """
Execute a crawling task asynchronously."""
        
        task.status = "running"
        task.started_at = datetime.utcnow()
        self.running_tasks[task.task_id] = task
        
        logger.info("Executing task %s on platform %s", task.task_id, task.platform.value)
        
        try:
            # Get appropriate crawler
            crawler = self.crawlers[task.platform]
            
            # Submit to thread pool
            future = self.executor.submit(
                self._run_crawler_task,
                crawler,
                task
            )
            
            # Store future reference for monitoring
            task.results['future'] = future
            
            await self._store_task_state(task)
            
        except Exception as e:
            logger.error("Failed to execute task %s: %s", task.task_id, str(e))
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            # Move to completed tasks
            del self.running_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
    
    def _run_crawler_task(self, crawler, task: CrawlerTask) -> Dict[str, Any]:
        """Run crawler task in thread pool (synchronous)."""
        
        try:
            # Execute crawling
            crawler_results = crawler.crawl_urls(
                urls=task.target_urls,
                fingerprints=task.content_fingerprints
            )
            
            # Process results for violations
            violations = []
            for result in crawler_results:
                if self.violation_detector.check_violation(result, task.content_fingerprints):
                    violation = self.violation_detector.create_violation_record(result)
                    violations.append(violation)
                    
                    # Collect evidence
                    evidence = self.evidence_collector.collect_evidence(result)
                    violation['evidence'] = evidence
            
            return {
                'crawler_results': crawler_results,
                'violations': violations,
                'total_checked': len(crawler_results),
                'violations_found': len(violations)
            }
            
        except Exception as e:
            logger.error("Error in crawler task execution: %s", str(e))
            raise
    
    async def _monitor_running_tasks(self):
        """Monitor running tasks and handle completion."""
        
        completed_task_ids = []
        
        for task_id, task in self.running_tasks.items():
            future = task.results.get('future')
            if not future:
                continue
            
            if future.done():
                try:
                    # Get results
                    results = future.result()
                    task.results.update(results)
                    task.status = "completed"
                    task.completed_at = datetime.utcnow()
                    
                    logger.info(
                        "Task %s completed: %d violations found", 
                        task_id, 
                        results.get('violations_found', 0)
                    )
                    
                    # Handle violations
                    if results.get('violations'):
                        await self._handle_violations(task, results['violations'])
                    
                except Exception as e:
                    logger.error("Task %s failed: %s", task_id, str(e))
                    task.status = "failed"
                    task.error_message = str(e)
                    task.completed_at = datetime.utcnow()
                
                completed_task_ids.append(task_id)
        
        # Move completed tasks
        for task_id in completed_task_ids:
            task = self.running_tasks.pop(task_id)
            self.completed_tasks[task_id] = task
            await self._store_task_state(task)
    
    async def _handle_violations(self, task: CrawlerTask, violations: List[Dict[str, Any]]):
        """Handle detected violations with notifications and actions."""
        
        for violation in violations:
            try:
                # Store violation in database
                await self._store_violation(violation)
                
                # Send notifications
                await self._send_violation_notification(violation)
                
                # Update statistics
                stats = self.crawler_stats[task.platform.value]
                stats.violations_detected += 1
                
                logger.warning(
                    "Violation detected on %s: %s", 
                    task.platform.value,
                    violation.get('url', 'unknown')
                )
                
            except Exception as e:
                logger.error("Error handling violation: %s", str(e))
    
    async def _update_statistics(self):
        """Update performance statistics for all crawlers."""
        
        for platform, stats in self.crawler_stats.items():
            # Count completed tasks
            completed_for_platform = [
                task for task in self.completed_tasks.values()
                if task.platform.value == platform and task.completed_at
            ]
            
            if completed_for_platform:
                stats.completed_tasks = len([t for t in completed_for_platform if t.status == "completed"])
                stats.failed_tasks = len([t for t in completed_for_platform if t.status == "failed"])
                stats.total_tasks = len(completed_for_platform)
                
                if stats.total_tasks > 0:
                    stats.error_rate = stats.failed_tasks / stats.total_tasks
                
                # Calculate average response time
                completed_tasks = [t for t in completed_for_platform if t.status == "completed"]
                if completed_tasks:
                    response_times = [
                        (t.completed_at - t.started_at).total_seconds()
                        for t in completed_tasks
                        if t.started_at and t.completed_at
                    ]
                    if response_times:
                        stats.avg_response_time = sum(response_times) / len(response_times)
                
                stats.last_activity = max(t.completed_at for t in completed_for_platform)
        
        # Store statistics in Redis
        await self._store_statistics()
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or pending task."""
        
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            future = task.results.get('future')
            
            if future and not future.done():
                future.cancel()
            
            task.status = "cancelled"
            task.completed_at = datetime.utcnow()
            
            # Move to completed
            del self.running_tasks[task_id]
            self.completed_tasks[task_id] = task
            
            await self._store_task_state(task)
            
            logger.info("Cancelled running task: %s", task_id)
            return True
        
        # Check pending tasks
        for i, task in enumerate(self.task_queue):
            if task.task_id == task_id:
                task.status = "cancelled"
                task.completed_at = datetime.utcnow()
                
                self.task_queue.pop(i)
                self.completed_tasks[task_id] = task
                
                await self._store_task_state(task)
                
                logger.info("Cancelled pending task: %s", task_id)
                return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status information for a specific task."""
        
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return self._task_to_dict(task)
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return self._task_to_dict(task)
        
        # Check pending tasks
        for task in self.task_queue:
            if task.task_id == task_id:
                return self._task_to_dict(task)
        
        return None
    
    def get_platform_statistics(self) -> Dict[str, CrawlerStats]:
        """
Get performance statistics for all platforms."""
        return self.crawler_stats.copy()
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """
Get overall coordinator status and statistics."""
        
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0,
            'active_crawlers': len(self.crawlers),
            'pending_tasks': len(self.task_queue),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'total_violations_detected': sum(stats.violations_detected for stats in self.crawler_stats.values()),
            'platform_stats': {name: self._stats_to_dict(stats) for name, stats in self.crawler_stats.items()}
        }
    
    # Private helper methods
    
    def _task_to_dict(self, task: CrawlerTask) -> Dict[str, Any]:
        """
Convert task object to dictionary."""
        return {
            'task_id': task.task_id,
            'platform': task.platform.value,
            'target_urls': task.target_urls,
            'priority': task.priority,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_message': task.error_message,
            'results_summary': {
                k: v for k, v in task.results.items() 
                if k != 'future'  # Exclude non-serializable future object
            }
        }
    
    def _stats_to_dict(self, stats: CrawlerStats) -> Dict[str, Any]:
        """
Convert stats object to dictionary."""
        return {
            'platform': stats.platform,
            'total_tasks': stats.total_tasks,
            'completed_tasks': stats.completed_tasks,
            'failed_tasks': stats.failed_tasks,
            'violations_detected': stats.violations_detected,
            'evidence_collected': stats.evidence_collected,
            'avg_response_time': stats.avg_response_time,
            'error_rate': stats.error_rate,
            'last_activity': stats.last_activity.isoformat() if stats.last_activity else None
        }
    
    async def _store_task_state(self, task: CrawlerTask):
        """
Store task state in Redis for persistence."""
        try:
            task_data = self._task_to_dict(task)
            self.redis_client.setex(
                f"crawler_task:{task.task_id}",
                86400,  # 24 hours
                json.dumps(task_data)
            )
        except Exception as e:
            logger.error("Failed to store task state: %s", str(e))
    
    async def _store_statistics(self):
        """Store statistics in Redis."""
        try:
            stats_data = {
                name: self._stats_to_dict(stats)
                for name, stats in self.crawler_stats.items()
            }
            self.redis_client.setex(
                "crawler_statistics",
                300,  # 5 minutes
                json.dumps(stats_data)
            )
        except Exception as e:
            logger.error("Failed to store statistics: %s", str(e))
    
    async def _store_violation(self, violation: Dict[str, Any]):
        try:
            logger.info(f"Executing _store_violation")
            
            # Implementation for _store_violation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_store_violation completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing _send_violation_notification")
            
            # Implementation for _send_violation_notification
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_send_violation_notification completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_send_violation_notification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"_store_violation failed: {e}")
            raise
    async def _send_violation_notification(self, violation: Dict[str, Any]):
        """
Send violation notification via configured channels."""
        # Implementation for webhook/email notifications
        pass
    
    async def _cleanup_old_tasks(self):
        """
Clean up old completed tasks to prevent memory leaks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        old_task_ids = [
            task_id for task_id, task in self.completed_tasks.items()
            if task.completed_at and task.completed_at < cutoff_time
        ]
        
        for task_id in old_task_ids:
            del self.completed_tasks[task_id]
        
        if old_task_ids:
            logger.info("Cleaned up %d old tasks", len(old_task_ids))
    
    async def _health_check_crawlers(self):
        """Perform health checks on all crawlers."""
        for platform_type, crawler in self.crawlers.items():
            try:
                if hasattr(crawler, 'health_check'):
                    is_healthy = await crawler.health_check()
                    if not is_healthy:
                        logger.warning("Health check failed for %s crawler", platform_type.value)
            except Exception as e:
                logger.error("Health check error for %s: %s", platform_type.value, str(e))
