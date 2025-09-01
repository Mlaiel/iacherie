"""Crawler Worker Engine - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/crawler_worker.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Crawler Worker - Background Processing Engine
Responsibility: Asynchronous crawler task execution with intelligent load balancing
Technologies: Celery, Redis, AsyncIO, Priority Queues, Resource Management
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Request crawler → Worker pool → Load balancing → 
Platform extraction → Content protection → Result processing → Notification
"""
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
from contextlib import asynccontextmanager
from collections import defaultdict, deque
import heapq
import resource
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..engines.crawler_engine import CrawlerEngine
from ..platforms.platform_detector import PlatformDetector
from ..extractors.content_extractor import ContentExtractor
from ..filters.content_filter import ContentFilter
from ..validators.data_validator import DataValidator
from ..storage.result_storage import ResultStorage
from ...core.managers.queue_manager import ProductionQueueManager, TaskDefinition, TaskPriority, QueueType
from ...security.input_validator import InputValidator
from ...monitoring.performance_monitor import PerformanceMonitor
from ...ai.content_protection.fingerprint_engine import FingerprintEngine

logger = logging.getLogger(__name__)


class WorkerStatus(Enum):
    """Crawler worker status states"""
    IDLE = "idle"
    RUNNING = "running"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class WorkerType(Enum):
    """Types of crawler workers"""
    GENERIC = "generic"
    SOCIAL_MEDIA = "social_media"
    CONTENT_PLATFORM = "content_platform"
    NEWS_MEDIA = "news_media"
    ECOMMERCE = "ecommerce"
    SURVEILLANCE = "surveillance"
    FINGERPRINT = "fingerprint"


class TaskResult(Enum):
    """Task execution results"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RETRY = "retry"
    CANCELLED = "cancelled"


@dataclass
class WorkerConfig:
    """Worker configuration settings"""
    worker_id: str
    worker_type: WorkerType
    max_concurrent_tasks: int = 5
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    timeout_seconds: int = 300
    retry_attempts: int = 3
    backoff_factor: float = 2.0
    health_check_interval: int = 30
    supported_platforms: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    proxy_settings: Optional[Dict[str, Any]] = None


@dataclass
class WorkerMetrics:
    """Worker performance metrics"""
    worker_id: str
    total_tasks_processed: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_task_duration: float = 0.0
    current_memory_usage: float = 0.0
    current_cpu_usage: float = 0.0
    last_activity: Optional[datetime] = None
    uptime_hours: float = 0.0
    error_rate: float = 0.0
    throughput_per_hour: float = 0.0


@dataclass
class CrawlerTask:
    """Crawler task definition"""
    task_id: str
    task_type: str
    target_url: str
    platform: str
    content_types: List[str]
    extraction_rules: Dict[str, Any]
    priority: TaskPriority
    user_id: str
    tenant_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout: int = 300
    retry_count: int = 0
    max_retries: int = 3
    callback_url: Optional[str] = None
    webhook_data: Optional[Dict[str, Any]] = None


@dataclass
class TaskExecution:
    """Task execution context"""
    task: CrawlerTask
    worker_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[TaskResult] = None
    extracted_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class CrawlerWorker:
    """
    High-performance asynchronous crawler worker for content extraction
    
    Features:
    - Intelligent task prioritization
    - Resource monitoring and management
    - Platform-specific optimization
    - Content fingerprinting integration
    - Real-time performance metrics
    """
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.worker_id = config.worker_id
        self.status = WorkerStatus.IDLE
        self.metrics = WorkerMetrics(worker_id=self.worker_id)
        
        # Core components
        self.crawler_engine = CrawlerEngine()
        self.platform_detector = PlatformDetector()
        self.content_extractor = ContentExtractor()
        self.content_filter = ContentFilter()
        self.data_validator = DataValidator()
        self.result_storage = ResultStorage()
        self.input_validator = InputValidator()
        self.performance_monitor = PerformanceMonitor()
        self.fingerprint_engine = FingerprintEngine()
        
        # Task management
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, TaskExecution] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        self.failed_tasks: deque = deque(maxlen=500)
        
        # Resource management
        self.max_concurrent_tasks = config.max_concurrent_tasks
        self.running_tasks: Set[str] = set()
        self.task_semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.shutdown_event = asyncio.Event()
        self.startup_time = datetime.utcnow()
        
        # Thread pool for CPU-intensive tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix=f"CrawlerWorker-{self.worker_id}")

    async def start(self) -> bool:
        """Start the crawler worker"""
        try:
            logger.info(f"🚀 Starting crawler worker: {self.worker_id}")
            
            # Initialize components
            await self._initialize_components()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.status = WorkerStatus.IDLE
            self.metrics.last_activity = datetime.utcnow()
            
            logger.info(f"✅ Crawler worker {self.worker_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start crawler worker {self.worker_id}: {e}")
            self.status = WorkerStatus.ERROR
            return False

    async def stop(self) -> None:
        """Gracefully stop the crawler worker"""
        try:
            logger.info(f"🛑 Stopping crawler worker: {self.worker_id}")
            
            self.status = WorkerStatus.SHUTDOWN
            self.shutdown_event.set()
            
            # Wait for active tasks to complete (with timeout)
            if self.active_tasks:
                logger.info(f"⏳ Waiting for {len(self.active_tasks)} active tasks to complete...")
                await asyncio.wait_for(
                    self._wait_for_active_tasks(),
                    timeout=60.0
                )
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True, timeout=30.0)
            
            logger.info(f"✅ Crawler worker {self.worker_id} stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping crawler worker {self.worker_id}: {e}")

    async def submit_task(self, task: CrawlerTask) -> bool:
        """Submit a crawler task for execution"""
        try:
            # Validate task
            if not await self._validate_task(task):
                logger.warning(f"❌ Invalid task rejected: {task.task_id}")
                return False
            
            # Check worker capacity
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                logger.warning(f"⚠️ Worker {self.worker_id} at capacity, task queued: {task.task_id}")
            
            # Add to queue
            await self.task_queue.put(task)
            logger.info(f"📝 Task submitted to worker {self.worker_id}: {task.task_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to submit task {task.task_id}: {e}")
            return False

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive worker status"""
        return {
            "worker_id": self.worker_id,
            "status": self.status.value,
            "worker_type": self.config.worker_type.value,
            "active_tasks": len(self.active_tasks),
            "queued_tasks": self.task_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "max_concurrent": self.max_concurrent_tasks,
            "metrics": {
                "total_processed": self.metrics.total_tasks_processed,
                "successful": self.metrics.successful_tasks,
                "failed": self.metrics.failed_tasks,
                "error_rate": self.metrics.error_rate,
                "avg_duration": self.metrics.average_task_duration,
                "throughput_per_hour": self.metrics.throughput_per_hour,
                "memory_usage_mb": self.metrics.current_memory_usage,
                "cpu_usage_percent": self.metrics.current_cpu_usage,
                "uptime_hours": self.metrics.uptime_hours,
                "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
            },
            "config": {
                "supported_platforms": self.config.supported_platforms,
                "timeout_seconds": self.config.timeout_seconds,
                "max_retries": self.config.retry_attempts
            }
        }

    async def _initialize_components(self) -> None:
        """Initialize worker components"""
        try:
            # Initialize crawler engine
            await self.crawler_engine.initialize()
            
            # Initialize content extractor
            await self.content_extractor.initialize()
            
            # Initialize fingerprint engine
            await self.fingerprint_engine.initialize()
            
            # Initialize result storage
            await self.result_storage.initialize()
            
            logger.info(f"✅ Worker {self.worker_id} components initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize worker components: {e}")
            raise

    async def _start_background_tasks(self) -> None:
        """Start background worker tasks"""
        try:
            # Task processor
            task_processor = asyncio.create_task(self._task_processor())
            self.background_tasks.add(task_processor)
            
            # Resource monitor
            resource_monitor = asyncio.create_task(self._resource_monitor())
            self.background_tasks.add(resource_monitor)
            
            # Health checker
            health_checker = asyncio.create_task(self._health_checker())
            self.background_tasks.add(health_checker)
            
            # Metrics updater
            metrics_updater = asyncio.create_task(self._metrics_updater())
            self.background_tasks.add(metrics_updater)
            
            logger.info(f"✅ Background tasks started for worker {self.worker_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            raise

    async def _task_processor(self) -> None:
        """Main task processing loop"""
        while not self.shutdown_event.is_set():
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # Process task asynchronously
                asyncio.create_task(self._execute_task(task))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Task processor error: {e}")
                await asyncio.sleep(5)

    async def _execute_task(self, task: CrawlerTask) -> None:
        """Execute a crawler task"""
        execution = TaskExecution(
            task=task,
            worker_id=self.worker_id,
            start_time=datetime.utcnow()
        )
        
        async with self.task_semaphore:
            try:
                # Add to active tasks
                self.active_tasks[task.task_id] = execution
                self.running_tasks.add(task.task_id)
                self.status = WorkerStatus.RUNNING
                
                logger.info(f"🚀 Executing task {task.task_id} on worker {self.worker_id}")
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._perform_crawling(task),
                    timeout=task.timeout
                )
                
                # Process successful result
                execution.result = TaskResult.SUCCESS
                execution.extracted_data = result
                execution.end_time = datetime.utcnow()
                
                # Store result
                await self._store_result(execution)
                
                # Update metrics
                self.metrics.successful_tasks += 1
                
                logger.info(f"✅ Task {task.task_id} completed successfully")
                
            except asyncio.TimeoutError:
                execution.result = TaskResult.TIMEOUT
                execution.error_message = f"Task timed out after {task.timeout}s"
                execution.end_time = datetime.utcnow()
                
                logger.warning(f"⏰ Task {task.task_id} timed out")
                
                # Retry if possible
                if task.retry_count < task.max_retries:
                    await self._retry_task(task)
                else:
                    self.metrics.failed_tasks += 1
                    await self._handle_failed_task(execution)
                
            except Exception as e:
                execution.result = TaskResult.FAILED
                execution.error_message = str(e)
                execution.end_time = datetime.utcnow()
                
                logger.error(f"❌ Task {task.task_id} failed: {e}")
                
                # Retry if possible
                if task.retry_count < task.max_retries:
                    await self._retry_task(task)
                else:
                    self.metrics.failed_tasks += 1
                    await self._handle_failed_task(execution)
                
            finally:
                # Clean up
                self.running_tasks.discard(task.task_id)
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
                
                # Update status
                if not self.running_tasks:
                    self.status = WorkerStatus.IDLE
                
                # Update total tasks
                self.metrics.total_tasks_processed += 1
                self.metrics.last_activity = datetime.utcnow()

    async def _perform_crawling(self, task: CrawlerTask) -> Dict[str, Any]:
        """Perform the actual crawling operation"""
        try:
            # Detect platform
            platform_info = await self.platform_detector.detect_platform(task.target_url)
            
            # Configure crawler for platform
            crawler_config = await self._configure_crawler_for_platform(
                platform_info, task
            )
            
            # Extract content
            raw_content = await self.crawler_engine.crawl_url(
                task.target_url, 
                crawler_config
            )
            
            # Extract structured data
            extracted_data = await self.content_extractor.extract_content(
                raw_content, 
                task.content_types, 
                task.extraction_rules
            )
            
            # Filter content
            filtered_data = await self.content_filter.filter_content(
                extracted_data, 
                task.metadata.get('filter_rules', {})
            )
            
            # Validate data
            validated_data = await self.data_validator.validate_data(
                filtered_data
            )
            
            # Generate fingerprints for content protection
            if task.metadata.get('generate_fingerprints', False):
                fingerprints = await self._generate_content_fingerprints(validated_data)
                validated_data['fingerprints'] = fingerprints
            
            # Prepare result
            result = {
                'task_id': task.task_id,
                'url': task.target_url,
                'platform': platform_info,
                'content_types': task.content_types,
                'extracted_data': validated_data,
                'extraction_metadata': {
                    'extraction_time': datetime.utcnow().isoformat(),
                    'worker_id': self.worker_id,
                    'content_size': len(str(validated_data)),
                    'processing_duration': time.time() - task.created_at.timestamp()
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Crawling operation failed for {task.target_url}: {e}")
            raise

    async def _generate_content_fingerprints(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fingerprints for extracted content"""
        try:
            fingerprints = {}
            
            # Generate fingerprints for different content types
            for content_type, content in content_data.items():
                if content_type == 'text' and content:
                    fingerprints['text'] = await self.fingerprint_engine.generate_text_fingerprint(content)
                elif content_type == 'images' and content:
                    fingerprints['images'] = []
                    for image_url in content[:5]:  # Limit to first 5 images
                        fp = await self.fingerprint_engine.generate_image_fingerprint(image_url)
                        fingerprints['images'].append(fp)
                elif content_type == 'videos' and content:
                    fingerprints['videos'] = []
                    for video_url in content[:3]:  # Limit to first 3 videos
                        fp = await self.fingerprint_engine.generate_video_fingerprint(video_url)
                        fingerprints['videos'].append(fp)
                elif content_type == 'audio' and content:
                    fingerprints['audio'] = []
                    for audio_url in content[:3]:  # Limit to first 3 audio files
                        fp = await self.fingerprint_engine.generate_audio_fingerprint(audio_url)
                        fingerprints['audio'].append(fp)
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"❌ Fingerprint generation failed: {e}")
            return {}

    async def _configure_crawler_for_platform(self, platform_info: Dict[str, Any], task: CrawlerTask) -> Dict[str, Any]:
        """Configure crawler settings for specific platform"""
        try:
            config = {
                'user_agent': 'IA-Influencer-Agent/1.0',
                'timeout': task.timeout,
                'headers': self.config.custom_headers.copy(),
                'proxy': self.config.proxy_settings,
                'respect_robots_txt': True,
                'max_redirects': 5
            }
            
            platform = platform_info.get('platform', 'unknown')
            
            # Platform-specific configurations
            if platform == 'youtube':
                config.update({
                    'wait_for_video': True,
                    'extract_comments': task.metadata.get('extract_comments', False),
                    'extract_metadata': True
                })
            elif platform == 'instagram':
                config.update({
                    'extract_stories': task.metadata.get('extract_stories', False),
                    'extract_highlights': task.metadata.get('extract_highlights', False)
                })
            elif platform == 'tiktok':
                config.update({
                    'extract_sounds': task.metadata.get('extract_sounds', True),
                    'extract_effects': task.metadata.get('extract_effects', False)
                })
            elif platform == 'twitter':
                config.update({
                    'extract_replies': task.metadata.get('extract_replies', False),
                    'extract_media': True
                })
            elif platform == 'spotify':
                config.update({
                    'extract_playlists': task.metadata.get('extract_playlists', True),
                    'extract_artist_info': True
                })
            
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to configure crawler for platform: {e}")
            return {}

    async def _store_result(self, execution: TaskExecution) -> None:
        """Store task execution result"""
        try:
            await self.result_storage.store_result({
                'task_id': execution.task.task_id,
                'worker_id': execution.worker_id,
                'result': execution.result.value,
                'start_time': execution.start_time.isoformat(),
                'end_time': execution.end_time.isoformat() if execution.end_time else None,
                'duration_seconds': (execution.end_time - execution.start_time).total_seconds() if execution.end_time else None,
                'extracted_data': execution.extracted_data,
                'error_message': execution.error_message,
                'task_metadata': execution.task.metadata
            })
            
            # Add to completed tasks
            self.completed_tasks.append(execution)
            
        except Exception as e:
            logger.error(f"❌ Failed to store result for task {execution.task.task_id}: {e}")

    async def _retry_task(self, task: CrawlerTask) -> None:
        """Retry a failed task"""
        try:
            task.retry_count += 1
            
            # Calculate backoff delay
            delay = self.config.backoff_factor ** task.retry_count
            
            logger.info(f"🔄 Retrying task {task.task_id} (attempt {task.retry_count + 1}) in {delay}s")
            
            # Schedule retry
            asyncio.create_task(self._delayed_retry(task, delay))
            
        except Exception as e:
            logger.error(f"❌ Failed to schedule retry for task {task.task_id}: {e}")

    async def _delayed_retry(self, task: CrawlerTask, delay: float) -> None:
        """Execute delayed task retry"""
        await asyncio.sleep(delay)
        await self.task_queue.put(task)

    async def _handle_failed_task(self, execution: TaskExecution) -> None:
        """Handle permanently failed task"""
        try:
            # Store failed task
            self.failed_tasks.append(execution)
            
            # Send failure notification
            if execution.task.callback_url:
                await self._send_failure_notification(execution)
            
            logger.error(f"❌ Task {execution.task.task_id} permanently failed after {execution.task.retry_count} retries")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle failed task {execution.task.task_id}: {e}")

    async def _send_failure_notification(self, execution: TaskExecution) -> None:
        """Send failure notification to callback URL"""
        try:
            notification_data = {
                'task_id': execution.task.task_id,
                'status': 'failed',
                'error_message': execution.error_message,
                'retry_count': execution.task.retry_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Implementation would include HTTP callback
            logger.info(f"📢 Failure notification prepared for task {execution.task.task_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send failure notification: {e}")

    async def _validate_task(self, task: CrawlerTask) -> bool:
        """Validate task before execution"""
        try:
            # Basic validation
            if not task.task_id or not task.target_url:
                return False
            
            # URL validation
            if not self.input_validator.is_valid_url(task.target_url):
                return False
            
            # Platform support check
            if self.config.supported_platforms:
                platform_info = await self.platform_detector.detect_platform(task.target_url)
                if platform_info.get('platform') not in self.config.supported_platforms:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Task validation failed: {e}")
            return False

    async def _resource_monitor(self) -> None:
        """Monitor worker resource usage"""
        while not self.shutdown_event.is_set():
            try:
                # Get current process
                process = psutil.Process()
                
                # Update resource metrics
                self.metrics.current_memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                self.metrics.current_cpu_usage = process.cpu_percent()
                
                # Check resource limits
                if self.metrics.current_memory_usage > self.config.max_memory_mb:
                    logger.warning(f"⚠️ Worker {self.worker_id} memory usage high: {self.metrics.current_memory_usage:.1f}MB")
                    self.status = WorkerStatus.OVERLOADED
                elif self.metrics.current_cpu_usage > self.config.max_cpu_percent:
                    logger.warning(f"⚠️ Worker {self.worker_id} CPU usage high: {self.metrics.current_cpu_usage:.1f}%")
                    self.status = WorkerStatus.OVERLOADED
                elif self.status == WorkerStatus.OVERLOADED and len(self.running_tasks) == 0:
                    self.status = WorkerStatus.IDLE
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Resource monitor error: {e}")
                await asyncio.sleep(30)

    async def _health_checker(self) -> None:
        """Periodic health checks"""
        while not self.shutdown_event.is_set():
            try:
                # Check component health
                components_healthy = await self._check_component_health()
                
                if not components_healthy:
                    self.status = WorkerStatus.ERROR
                    logger.error(f"❌ Worker {self.worker_id} health check failed")
                elif self.status == WorkerStatus.ERROR and len(self.running_tasks) == 0:
                    self.status = WorkerStatus.IDLE
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Health checker error: {e}")
                await asyncio.sleep(60)

    async def _check_component_health(self) -> bool:
        """Check health of worker components"""
        try:
            # Check crawler engine
            if not await self.crawler_engine.health_check():
                return False
            
            # Check content extractor
            if not await self.content_extractor.health_check():
                return False
            
            # Check result storage
            if not await self.result_storage.health_check():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Component health check failed: {e}")
            return False

    async def _metrics_updater(self) -> None:
        """Update worker metrics"""
        while not self.shutdown_event.is_set():
            try:
                # Calculate uptime
                uptime = datetime.utcnow() - self.startup_time
                self.metrics.uptime_hours = uptime.total_seconds() / 3600
                
                # Calculate error rate
                total_tasks = self.metrics.total_tasks_processed
                if total_tasks > 0:
                    self.metrics.error_rate = (self.metrics.failed_tasks / total_tasks) * 100
                
                # Calculate throughput
                if self.metrics.uptime_hours > 0:
                    self.metrics.throughput_per_hour = total_tasks / self.metrics.uptime_hours
                
                # Calculate average task duration
                if self.completed_tasks:
                    durations = []
                    for execution in list(self.completed_tasks):
                        if execution.end_time:
                            duration = (execution.end_time - execution.start_time).total_seconds()
                            durations.append(duration)
                    
                    if durations:
                        self.metrics.average_task_duration = sum(durations) / len(durations)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"❌ Metrics updater error: {e}")
                await asyncio.sleep(120)

    async def _wait_for_active_tasks(self) -> None:
        """Wait for all active tasks to complete"""
        while self.active_tasks:
            await asyncio.sleep(1)

    def __del__(self):
        """Cleanup on deletion"""
        try:
            if hasattr(self, 'thread_pool') and self.thread_pool:
                self.thread_pool.shutdown(wait=False)
        except Exception:
            pass
