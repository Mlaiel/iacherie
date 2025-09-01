"""Crawler Manager Implementation
=============================

Professional crawler management system for coordinating multi-platform content monitoring.
Orchestrates all crawlers with advanced scheduling, monitoring, and result aggregation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use, 
reproduction, or distribution is strictly prohibited and may result in 
severe legal consequences.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import threading

from .platform_crawler import (
    PlatformCrawler, CrawlerConfig, CrawlerResult, 
    ContentMatch, ContentMatchType, CrawlerStatus
)
from .youtube_crawler import YouTubeCrawler
from .instagram_crawler import InstagramCrawler
from .tiktok_crawler import TikTokCrawler
from .generic_web_crawler import GenericWebCrawler
from ..fingerprinting.vector_matcher import VectorMatcher


class CrawlerPriority(Enum):
    """Crawler execution priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ScheduleType(Enum):
    """Crawler schedule types"""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    CONTINUOUS = "continuous"


@dataclass
class CrawlerTask:
    """Crawler task specification"""
    task_id: str
    crawler_type: str
    config: CrawlerConfig
    fingerprint_data: Dict[str, Any]
    priority: CrawlerPriority
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    callback_url: Optional[str] = None
    max_retries: int = 3
    retry_delay: int = 300  # seconds
    timeout: int = 3600  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    next_run: datetime = field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    retry_count: int = 0
    is_active: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class CrawlerMetrics:
    """Crawler performance metrics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    active_crawlers: int = 0
    total_matches_found: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    last_update: datetime = field(default_factory=datetime.utcnow)


class CrawlerManager:
    """
    Professional crawler management system for coordinating multi-platform monitoring.
    
    Features:
    - Multi-platform crawler orchestration
    - Advanced task scheduling and prioritization
    - Real-time monitoring and metrics
    - Automatic retry and error handling
    - Result aggregation and deduplication
    - Load balancing and resource management
    - Comprehensive logging and alerting
    - WebSocket notifications for real-time updates
    """
    
    def __init__(self, vector_matcher: VectorMatcher, max_concurrent_crawlers: int = 5):
        """
        Initialize crawler manager.
        
        Args:
            vector_matcher: Vector matching service
            max_concurrent_crawlers: Maximum number of concurrent crawlers
        """
        self.vector_matcher = vector_matcher
        self.max_concurrent_crawlers = max_concurrent_crawlers
        self.logger = logging.getLogger(__name__)
        
        # Task management
        self.tasks: Dict[str, CrawlerTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue = asyncio.PriorityQueue()
        self.task_lock = asyncio.Lock()
        
        # Crawler instances
        self.crawler_instances: Dict[str, PlatformCrawler] = {}
        self.crawler_configs: Dict[str, Dict[str, Any]] = {}
        
        # Metrics and monitoring
        self.metrics = CrawlerMetrics()
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            'task_started': [],
            'task_completed': [],
            'task_failed': [],
            'match_found': [],
            'crawler_error': []
        }
        
        # Manager state
        self.is_running = False
        self.scheduler_task = None
        self.monitor_task = None
        
        # Thread pool for blocking operations
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
    
    async def initialize(self):
        """Initialize the crawler manager"""
        try:
            self.logger.info("Initializing Crawler Manager")
            
            # Start scheduler and monitor tasks
            self.is_running = True
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            
            self.logger.info("Crawler Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Crawler Manager: {str(e)}")
            raise
    
    async def shutdown(self):
        """Shutdown the crawler manager gracefully"""
        try:
            self.logger.info("Shutting down Crawler Manager")
            
            self.is_running = False
            
            # Cancel running tasks
            for task_id, task in self.running_tasks.items():
                if not task.done():
                    task.cancel()
                    self.logger.info(f"Cancelled running task: {task_id}")
            
            # Cancel scheduler and monitor
            if self.scheduler_task:
                self.scheduler_task.cancel()
            if self.monitor_task:
                self.monitor_task.cancel()
            
            # Cleanup crawler instances
            for crawler in self.crawler_instances.values():
                if hasattr(crawler, 'close'):
                    await crawler.close()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            self.logger.info("Crawler Manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
    
    def register_crawler_config(self, crawler_type: str, config: Dict[str, Any]):
        """
        Register configuration for a crawler type.
        
        Args:
            crawler_type: Type of crawler (youtube, instagram, tiktok, web)
            config: Crawler configuration dictionary
        """
        self.crawler_configs[crawler_type] = config
        self.logger.info(f"Registered config for crawler type: {crawler_type}")
    
    async def create_crawler_task(self, 
                                crawler_type: str,
                                fingerprint_data: Dict[str, Any],
                                search_config: Dict[str, Any],
                                schedule_config: Dict[str, Any],
                                priority: CrawlerPriority = CrawlerPriority.NORMAL,
                                callback_url: Optional[str] = None,
                                tags: List[str] = None) -> str:
        """
        Create a new crawler task.
        
        Args:
            crawler_type: Type of crawler to use
            fingerprint_data: Fingerprint data to search for
            search_config: Search configuration
            schedule_config: Task scheduling configuration
            priority: Task priority level
            callback_url: Optional callback URL for notifications
            tags: Optional tags for task categorization
            
        Returns:
            Task ID
        """
        try:
            # Validate crawler type
            if crawler_type not in self.crawler_configs:
                raise ValueError(f"Unknown crawler type: {crawler_type}")
            
            # Generate task ID
            task_id = f"{crawler_type}_{uuid.uuid4().hex[:8]}"
            
            # Create crawler config
            base_config = self.crawler_configs[crawler_type]
            crawler_config = CrawlerConfig(
                platform_name=crawler_type,
                search_terms=search_config.get('search_terms', []),
                similarity_threshold=search_config.get('similarity_threshold', 0.8),
                max_results_per_search=search_config.get('max_results', 100),
                crawl_interval_minutes=search_config.get('interval_minutes', 60),
                respect_robots_txt=base_config.get('respect_robots_txt', True),
                rate_limit_delay=base_config.get('rate_limit_delay', 1.0),
                user_agent=base_config.get('user_agent', 'IA-Influencer-Agent/1.0'),
                timeout_seconds=base_config.get('timeout_seconds', 30),
                retry_attempts=base_config.get('retry_attempts', 3)
            )
            
            # Determine schedule type
            schedule_type = ScheduleType(schedule_config.get('type', 'once'))
            
            # Calculate next run time
            next_run = datetime.utcnow()
            if schedule_config.get('delay_seconds'):
                next_run += timedelta(seconds=schedule_config['delay_seconds'])
            
            # Create task
            task = CrawlerTask(
                task_id=task_id,
                crawler_type=crawler_type,
                config=crawler_config,
                fingerprint_data=fingerprint_data,
                priority=priority,
                schedule_type=schedule_type,
                schedule_config=schedule_config,
                callback_url=callback_url,
                max_retries=search_config.get('max_retries', 3),
                retry_delay=search_config.get('retry_delay', 300),
                timeout=search_config.get('timeout', 3600),
                next_run=next_run,
                tags=tags or []
            )
            
            # Store task
            async with self.task_lock:
                self.tasks[task_id] = task
                await self.task_queue.put((priority.value, task))
            
            self.metrics.total_tasks += 1
            
            # Trigger callbacks
            await self._trigger_event_callbacks('task_created', {
                'task_id': task_id,
                'crawler_type': crawler_type,
                'priority': priority.name,
                'next_run': next_run.isoformat()
            })
            
            self.logger.info(f"Created crawler task: {task_id} ({crawler_type})")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error creating crawler task: {str(e)}")
            raise
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a crawler task.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if task was cancelled, False if not found
        """
        try:
            async with self.task_lock:
                if task_id in self.tasks:
                    self.tasks[task_id].is_active = False
                    
                    # Cancel running task if exists
                    if task_id in self.running_tasks:
                        running_task = self.running_tasks[task_id]
                        if not running_task.done():
                            running_task.cancel()
                            del self.running_tasks[task_id]
                    
                    self.logger.info(f"Cancelled task: {task_id}")
                    return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling task {task_id}: {str(e)}")
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information or None if not found
        """
        try:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            is_running = task_id in self.running_tasks
            
            status = {
                'task_id': task_id,
                'crawler_type': task.crawler_type,
                'priority': task.priority.name,
                'schedule_type': task.schedule_type.value,
                'is_active': task.is_active,
                'is_running': is_running,
                'created_at': task.created_at.isoformat(),
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'retry_count': task.retry_count,
                'max_retries': task.max_retries,
                'tags': task.tags
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting task status for {task_id}: {str(e)}")
            return None
    
    async def get_all_tasks_status(self) -> List[Dict[str, Any]]:
        """Get status of all tasks"""
        try:
            all_status = []
            
            for task_id in self.tasks:
                status = await self.get_task_status(task_id)
                if status:
                    all_status.append(status)
            
            return all_status
            
        except Exception as e:
            self.logger.error(f"Error getting all tasks status: {str(e)}")
            return []
    
    async def search_across_platforms(self, 
                                    fingerprint_data: Dict[str, Any],
                                    platforms: List[str] = None,
                                    max_results_per_platform: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for content across multiple platforms simultaneously.
        
        Args:
            fingerprint_data: Fingerprint data to search for
            platforms: List of platforms to search (default: all configured)
            max_results_per_platform: Maximum results per platform
            
        Returns:
            Dictionary of results per platform
        """
        try:
            if platforms is None:
                platforms = list(self.crawler_configs.keys())
            
            # Create search tasks for each platform
            search_tasks = []
            for platform in platforms:
                if platform in self.crawler_configs:
                    task = asyncio.create_task(
                        self._search_single_platform(platform, fingerprint_data, max_results_per_platform)
                    )
                    search_tasks.append((platform, task))
            
            # Wait for all searches to complete
            results = {}
            for platform, task in search_tasks:
                try:
                    platform_results = await asyncio.wait_for(task, timeout=300)  # 5 minute timeout
                    results[platform] = platform_results
                except asyncio.TimeoutError:
                    self.logger.warning(f"Search timeout for platform: {platform}")
                    results[platform] = []
                except Exception as e:
                    self.logger.error(f"Search error for platform {platform}: {str(e)}")
                    results[platform] = []
            
            # Update metrics
            total_matches = sum(len(matches) for matches in results.values())
            self.metrics.total_matches_found += total_matches
            
            self.logger.info(f"Cross-platform search completed: {total_matches} total matches")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in cross-platform search: {str(e)}")
            return {}
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """
        Add event callback for notifications.
        
        Args:
            event_type: Type of event (task_started, task_completed, etc.)
            callback: Callback function
        """
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
            self.logger.info(f"Added callback for event: {event_type}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current crawler metrics"""
        active_crawlers = len(self.running_tasks)
        success_rate = 0.0
        
        if self.metrics.total_tasks > 0:
            success_rate = (self.metrics.completed_tasks / self.metrics.total_tasks) * 100
        
        return {
            'total_tasks': self.metrics.total_tasks,
            'completed_tasks': self.metrics.completed_tasks,
            'failed_tasks': self.metrics.failed_tasks,
            'active_crawlers': active_crawlers,
            'total_matches_found': self.metrics.total_matches_found,
            'average_execution_time': self.metrics.average_execution_time,
            'success_rate': success_rate,
            'last_update': self.metrics.last_update.isoformat(),
            'task_queue_size': self.task_queue.qsize(),
            'crawler_types_configured': list(self.crawler_configs.keys())
        }
    
    # Private methods
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        try:
            while self.is_running:
                try:
                    # Check for tasks ready to run
                    await self._process_pending_tasks()
                    
                    # Clean up completed tasks
                    await self._cleanup_completed_tasks()
                    
                    # Update metrics
                    await self._update_metrics()
                    
                    # Wait before next iteration
                    await asyncio.sleep(5.0)
                    
                except Exception as e:
                    self.logger.error(f"Error in scheduler loop: {str(e)}")
                    await asyncio.sleep(10.0)
                    
        except asyncio.CancelledError:
            self.logger.info("Scheduler loop cancelled")
        except Exception as e:
            self.logger.error(f"Fatal error in scheduler loop: {str(e)}")
    
    async def _monitor_loop(self):
        """Monitor loop for health checks and alerts"""
        try:
            while self.is_running:
                try:
                    # Check crawler health
                    await self._check_crawler_health()
                    
                    # Monitor resource usage
                    await self._monitor_resource_usage()
                    
                    # Check for stuck tasks
                    await self._check_stuck_tasks()
                    
                    # Wait before next check
                    await asyncio.sleep(30.0)
                    
                except Exception as e:
                    self.logger.error(f"Error in monitor loop: {str(e)}")
                    await asyncio.sleep(60.0)
                    
        except asyncio.CancelledError:
            self.logger.info("Monitor loop cancelled")
        except Exception as e:
            self.logger.error(f"Fatal error in monitor loop: {str(e)}")
    
    async def _process_pending_tasks(self):
        """Process tasks that are ready to run"""
        current_time = datetime.utcnow()
        
        # Limit concurrent crawlers
        if len(self.running_tasks) >= self.max_concurrent_crawlers:
            return
        
        # Get tasks ready to run
        ready_tasks = []
        async with self.task_lock:
            for task_id, task in self.tasks.items():
                if (task.is_active and 
                    task.next_run <= current_time and 
                    task_id not in self.running_tasks):
                    ready_tasks.append(task)
        
        # Sort by priority
        ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
        
        # Start tasks up to the limit
        slots_available = self.max_concurrent_crawlers - len(self.running_tasks)
        for task in ready_tasks[:slots_available]:
            await self._start_crawler_task(task)
    
    async def _start_crawler_task(self, task: CrawlerTask):
        """Start execution of a crawler task"""
        try:
            # Create and start async task
            async_task = asyncio.create_task(self._execute_crawler_task(task))
            self.running_tasks[task.task_id] = async_task
            
            # Update task state
            task.last_run = datetime.utcnow()
            
            # Calculate next run time for recurring tasks
            if task.schedule_type == ScheduleType.INTERVAL:
                interval_minutes = task.schedule_config.get('interval_minutes', 60)
                task.next_run = task.last_run + timedelta(minutes=interval_minutes)
            elif task.schedule_type == ScheduleType.ONCE:
                task.is_active = False
            
            # Trigger callbacks
            await self._trigger_event_callbacks('task_started', {
                'task_id': task.task_id,
                'crawler_type': task.crawler_type,
                'started_at': task.last_run.isoformat()
            })
            
            self.logger.info(f"Started crawler task: {task.task_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting task {task.task_id}: {str(e)}")
            await self._handle_task_error(task, str(e))
    
    async def _execute_crawler_task(self, task: CrawlerTask) -> CrawlerResult:
        """Execute a single crawler task"""
        start_time = datetime.utcnow()
        
        try:
            # Get or create crawler instance
            crawler = await self._get_crawler_instance(task.crawler_type, task.config)
            
            # Execute crawl
            result = await asyncio.wait_for(
                crawler.crawl_for_matches(task.fingerprint_data),
                timeout=task.timeout
            )
            
            # Process results
            await self._process_crawler_result(task, result)
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.completed_tasks += 1
            self._update_average_execution_time(execution_time)
            
            # Add to execution history
            self._add_to_execution_history(task, result, execution_time, 'completed')
            
            # Trigger callbacks
            await self._trigger_event_callbacks('task_completed', {
                'task_id': task.task_id,
                'crawler_type': task.crawler_type,
                'execution_time': execution_time,
                'matches_found': len(result.matches),
                'completed_at': datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Completed task {task.task_id}: {len(result.matches)} matches found")
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Task {task.task_id} timed out after {task.timeout} seconds")
            await self._handle_task_timeout(task)
            raise
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.task_id}: {str(e)}")
            await self._handle_task_error(task, str(e))
            raise
        
        finally:
            # Remove from running tasks
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
    
    async def _get_crawler_instance(self, crawler_type: str, config: CrawlerConfig) -> PlatformCrawler:
        """Get or create crawler instance"""
        if crawler_type not in self.crawler_instances:
            # Create new crawler instance
            crawler_config = self.crawler_configs[crawler_type]
            
            if crawler_type == 'youtube':
                api_key = crawler_config.get('api_key')
                crawler = YouTubeCrawler(config, self.vector_matcher, api_key)
            elif crawler_type == 'instagram':
                access_token = crawler_config.get('access_token')
                app_secret = crawler_config.get('app_secret')
                crawler = InstagramCrawler(config, self.vector_matcher, access_token, app_secret)
            elif crawler_type == 'tiktok':
                crawler = TikTokCrawler(config, self.vector_matcher)
            elif crawler_type == 'web':
                crawler = GenericWebCrawler(config, self.vector_matcher)
            else:
                raise ValueError(f"Unknown crawler type: {crawler_type}")
            
            self.crawler_instances[crawler_type] = crawler
        
        return self.crawler_instances[crawler_type]
    
    async def _search_single_platform(self, platform: str, fingerprint_data: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """Search single platform"""
        try:
            # Create temporary config
            base_config = self.crawler_configs[platform]
            config = CrawlerConfig(
                platform_name=platform,
                search_terms=fingerprint_data.get('search_terms', []),
                similarity_threshold=0.8,
                max_results_per_search=max_results,
                crawl_interval_minutes=60,
                respect_robots_txt=base_config.get('respect_robots_txt', True),
                rate_limit_delay=base_config.get('rate_limit_delay', 1.0),
                user_agent=base_config.get('user_agent', 'IA-Influencer-Agent/1.0'),
                timeout_seconds=base_config.get('timeout_seconds', 30),
                retry_attempts=base_config.get('retry_attempts', 3)
            )
            
            # Get crawler and search
            crawler = await self._get_crawler_instance(platform, config)
            search_terms = fingerprint_data.get('search_terms', [])
            results = await crawler.search_content(search_terms, max_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching platform {platform}: {str(e)}")
            return []
    
    async def _process_crawler_result(self, task: CrawlerTask, result: CrawlerResult):
        """Process crawler result and trigger notifications"""
        try:
            # Filter high-confidence matches
            high_confidence_matches = [
                match for match in result.matches 
                if match.similarity_score >= 0.9
            ]
            
            # Trigger match callbacks
            for match in high_confidence_matches:
                await self._trigger_event_callbacks('match_found', {
                    'task_id': task.task_id,
                    'platform': result.platform,
                    'match_url': match.url,
                    'similarity_score': match.similarity_score,
                    'match_type': match.match_type.value
                })
            
            # Send callback notification if configured
            if task.callback_url and result.matches:
                await self._send_callback_notification(task, result)
            
        except Exception as e:
            self.logger.error(f"Error processing crawler result: {str(e)}")
    
    async def _handle_task_error(self, task: CrawlerTask, error_message: str):
        """Handle task execution error"""
        task.retry_count += 1
        
        if task.retry_count < task.max_retries:
            # Schedule retry
            task.next_run = datetime.utcnow() + timedelta(seconds=task.retry_delay)
            self.logger.info(f"Scheduled retry for task {task.task_id} (attempt {task.retry_count + 1})")
        else:
            # Max retries reached, deactivate task
            task.is_active = False
            self.metrics.failed_tasks += 1
            self.logger.error(f"Task {task.task_id} failed permanently after {task.max_retries} retries")
        
        # Add to execution history
        self._add_to_execution_history(task, None, 0, 'failed', error_message)
        
        # Trigger error callbacks
        await self._trigger_event_callbacks('task_failed', {
            'task_id': task.task_id,
            'error_message': error_message,
            'retry_count': task.retry_count,
            'max_retries': task.max_retries
        })
    
    async def _handle_task_timeout(self, task: CrawlerTask):
        """Handle task timeout"""
        await self._handle_task_error(task, f"Task timed out after {task.timeout} seconds")
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed task references"""
        completed_task_ids = []
        
        for task_id, async_task in self.running_tasks.items():
            if async_task.done():
                completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            del self.running_tasks[task_id]
    
    async def _update_metrics(self):
        """Update crawler metrics"""
        self.metrics.active_crawlers = len(self.running_tasks)
        self.metrics.last_update = datetime.utcnow()
    
    async def _check_crawler_health(self):
        """Check health of crawler instances"""
        for crawler_type, crawler in self.crawler_instances.items():
            try:
                # Check if crawler is responsive
                stats = crawler.get_crawler_stats()
                if stats.get('status') == 'error':
                    self.logger.warning(f"Crawler {crawler_type} is in error state")
            except Exception as e:
                self.logger.error(f"Health check failed for crawler {crawler_type}: {str(e)}")
    
    async def _monitor_resource_usage(self):
        """Monitor system resource usage"""
        # This would implement resource monitoring
        # For now, just log current state
        self.logger.debug(f"Active crawlers: {len(self.running_tasks)}/{self.max_concurrent_crawlers}")
    
    async def _check_stuck_tasks(self):
        """Check for tasks that have been running too long"""
        current_time = datetime.utcnow()
        
        for task_id, async_task in self.running_tasks.items():
            task = self.tasks.get(task_id)
            if task and task.last_run:
                runtime = (current_time - task.last_run).total_seconds()
                if runtime > task.timeout * 1.5:  # 150% of timeout
                    self.logger.warning(f"Task {task_id} appears stuck (runtime: {runtime}s)")
                    async_task.cancel()
    
    async def _trigger_event_callbacks(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger event callbacks"""
        try:
            callbacks = self.event_callbacks.get(event_type, [])
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_data)
                    else:
                        # Run sync callback in thread pool
                        await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool, callback, event_data
                        )
                except Exception as e:
                    self.logger.error(f"Error in event callback for {event_type}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error triggering callbacks for {event_type}: {str(e)}")
    
    async def _send_callback_notification(self, task: CrawlerTask, result: CrawlerResult):
        """Send callback notification"""
        try:
            notification_data = {
                'task_id': task.task_id,
                'platform': result.platform,
                'crawl_id': result.crawl_id,
                'matches_found': len(result.matches),
                'high_similarity_matches': result.high_similarity_matches,
                'processing_time': result.processing_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(task.callback_url, json=notification_data) as response:
                    if response.status == 200:
                        self.logger.info(f"Callback notification sent for task {task.task_id}")
                    else:
                        self.logger.warning(f"Callback notification failed: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error sending callback notification: {str(e)}")
    
    def _update_average_execution_time(self, execution_time: float):
        """Update average execution time"""
        if self.metrics.completed_tasks <= 1:
            self.metrics.average_execution_time = execution_time
        else:
            # Running average
            self.metrics.average_execution_time = (
                (self.metrics.average_execution_time * (self.metrics.completed_tasks - 1) + execution_time) /
                self.metrics.completed_tasks
            )
    
    def _add_to_execution_history(self, task: CrawlerTask, result: Optional[CrawlerResult], 
                                execution_time: float, status: str, error_message: str = None):
        """Add execution to history"""
        history_entry = {
            'task_id': task.task_id,
            'crawler_type': task.crawler_type,
            'execution_time': execution_time,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'matches_found': len(result.matches) if result else 0,
            'error_message': error_message
        }
        
        self.execution_history.append(history_entry)
        
        # Limit history size
        if len(self.execution_history) > self.max_history_size:
            self.execution_history = self.execution_history[-self.max_history_size:]
