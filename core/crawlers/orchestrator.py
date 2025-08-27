"""
Advanced Crawling Orchestrator
=============================

Centralized orchestration system for managing multiple crawlers and
monitoring tasks. Provides intelligent scheduling, resource management,
and coordinated content surveillance across all platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor
import schedule

from .base import BaseCrawler, CrawlResult
from .youtube_api import YouTubeCrawler
from .tiktok_scraper import TikTokCrawler
from .instagram_api import InstagramCrawler
from .twitter_api import TwitterCrawler
from .universal_web import UniversalWebCrawler
from ..config import ContentType
from ..database.models import CrawlResult as DBCrawlResult
from ..utils.notification_manager import NotificationManager
from ..security.encryption import SecurityManager

logger = logging.getLogger(__name__)

class CrawlerType(Enum):
    """Supported crawler types."""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    UNIVERSAL_WEB = "universal_web"

class MonitoringMode(Enum):
    """Monitoring operation modes."""
    CONTINUOUS = "continuous"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"
    TRIGGERED = "triggered"

@dataclass
class CrawlingTask:
    """Definition of a crawling task."""
    
    task_id: str
    crawler_type: CrawlerType
    mode: MonitoringMode
    target: str  # URL, username, hashtag, etc.
    parameters: Dict[str, Any]
    schedule_pattern: Optional[str] = None  # Cron-like pattern
    priority: int = 1  # 1-10, higher is more important
    max_results: int = 100
    similarity_threshold: float = 0.85
    
    # Timing
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    # Status
    active: bool = True
    error_count: int = 0
    max_errors: int = 5
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()

@dataclass
class CrawlingJobResult:
    """Result of a crawling job execution."""
    
    job_id: str
    task_id: str
    crawler_type: CrawlerType
    start_time: datetime
    end_time: Optional[datetime]
    status: str  # success, error, partial
    results_count: int
    error_message: Optional[str]
    execution_time: float
    resource_usage: Dict[str, Any]
    
    # Results
    crawl_results: List[CrawlResult] = None
    violations_detected: int = 0
    alerts_sent: int = 0

class CrawlerOrchestrator:
    """Advanced orchestrator for managing multiple crawlers and monitoring tasks."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize crawler orchestrator."""
        self.config = config
        self.crawlers: Dict[CrawlerType, BaseCrawler] = {}
        self.tasks: Dict[str, CrawlingTask] = {}
        self.job_results: List[CrawlingJobResult] = []
        
        # Resource management
        self.max_concurrent_jobs = config.get('max_concurrent_jobs', 5)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_concurrent_jobs)
        
        # Components
        self.notification_manager = NotificationManager(config)
        self.security_manager = SecurityManager(config)
        
        # State tracking
        self.running_jobs: Set[str] = set()
        self.is_running = False
        
        # Initialize crawlers
        self._initialize_crawlers()
    
    def _initialize_crawlers(self):
        """Initialize all available crawlers."""
        try:
            # YouTube crawler
            if self.config.get('youtube_api_key'):
                self.crawlers[CrawlerType.YOUTUBE] = YouTubeCrawler(self.config)
                logger.info("YouTube crawler initialized")
            
            # TikTok crawler
            if self.config.get('tiktok_api_key'):
                self.crawlers[CrawlerType.TIKTOK] = TikTokCrawler(self.config)
                logger.info("TikTok crawler initialized")
            
            # Instagram crawler
            if self.config.get('instagram_app_id'):
                self.crawlers[CrawlerType.INSTAGRAM] = InstagramCrawler(self.config)
                logger.info("Instagram crawler initialized")
            
            # Twitter crawler
            if self.config.get('twitter_bearer_token'):
                self.crawlers[CrawlerType.TWITTER] = TwitterCrawler(self.config)
                logger.info("Twitter crawler initialized")
            
            # Universal web crawler (always available)
            self.crawlers[CrawlerType.UNIVERSAL_WEB] = UniversalWebCrawler(self.config)
            logger.info("Universal web crawler initialized")
            
        except Exception as e:
            logger.error(f"Crawler initialization error: {e}")
    
    def add_monitoring_task(self, task: CrawlingTask) -> str:
        """Add a new monitoring task."""
        try:
            task_id = task.task_id
            self.tasks[task_id] = task
            
            logger.info(f"Added monitoring task: {task_id} ({task.crawler_type.value})")
            return task_id
            
        except Exception as e:
            logger.error(f"Add task error: {e}")
            return ""
    
    def remove_monitoring_task(self, task_id: str) -> bool:
        """Remove a monitoring task."""
        try:
            if task_id in self.tasks:
                del self.tasks[task_id]
                logger.info(f"Removed monitoring task: {task_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Remove task error: {e}")
            return False
    
    def update_task_status(self, task_id: str, active: bool) -> bool:
        """Update task active status."""
        try:
            if task_id in self.tasks:
                self.tasks[task_id].active = active
                logger.info(f"Updated task {task_id} status: {active}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Update task status error: {e}")
            return False
    
    async def execute_task(self, task: CrawlingTask) -> CrawlingJobResult:
        """Execute a single crawling task."""
        job_id = f"{task.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            # Check if crawler is available
            crawler = self.crawlers.get(task.crawler_type)
            if not crawler:
                raise Exception(f"Crawler {task.crawler_type.value} not available")
            
            # Track running job
            self.running_jobs.add(job_id)
            
            logger.info(f"Executing crawling task: {job_id}")
            
            # Execute based on crawler type and parameters
            results = []
            
            if task.crawler_type == CrawlerType.YOUTUBE:
                results = await self._execute_youtube_task(crawler, task)
            elif task.crawler_type == CrawlerType.TIKTOK:
                results = await self._execute_tiktok_task(crawler, task)
            elif task.crawler_type == CrawlerType.INSTAGRAM:
                results = await self._execute_instagram_task(crawler, task)
            elif task.crawler_type == CrawlerType.TWITTER:
                results = await self._execute_twitter_task(crawler, task)
            elif task.crawler_type == CrawlerType.UNIVERSAL_WEB:
                results = await self._execute_web_task(crawler, task)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update task
            task.last_run = start_time
            task.error_count = 0
            
            # Create job result
            job_result = CrawlingJobResult(
                job_id=job_id,
                task_id=task.task_id,
                crawler_type=task.crawler_type,
                start_time=start_time,
                end_time=end_time,
                status='success',
                results_count=len(results),
                error_message=None,
                execution_time=execution_time,
                resource_usage={
                    'memory_mb': 0,  # Would implement actual monitoring
                    'cpu_percent': 0
                },
                crawl_results=results
            )
            
            # Process results for violations
            violations = await self._analyze_violations(results, task)
            job_result.violations_detected = len(violations)
            
            # Send alerts if violations found
            if violations:
                alerts_sent = await self._send_violation_alerts(violations, task)
                job_result.alerts_sent = alerts_sent
            
            self.job_results.append(job_result)
            logger.info(f"Task completed: {job_id} - {len(results)} results, {len(violations)} violations")
            
            return job_result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update task error count
            task.error_count += 1
            if task.error_count >= task.max_errors:
                task.active = False
                logger.warning(f"Task {task.task_id} disabled due to errors")
            
            # Create error result
            job_result = CrawlingJobResult(
                job_id=job_id,
                task_id=task.task_id,
                crawler_type=task.crawler_type,
                start_time=start_time,
                end_time=end_time,
                status='error',
                results_count=0,
                error_message=str(e),
                execution_time=execution_time,
                resource_usage={},
                crawl_results=[]
            )
            
            self.job_results.append(job_result)
            logger.error(f"Task failed: {job_id} - {str(e)}")
            
            return job_result
            
        finally:
            self.running_jobs.discard(job_id)
    
    async def _execute_youtube_task(self, crawler: YouTubeCrawler, task: CrawlingTask) -> List[CrawlResult]:
        """Execute YouTube-specific crawling task."""
        try:
            operation = task.parameters.get('operation', 'search')
            
            if operation == 'search':
                query = task.target
                return await crawler.search_similar_content(
                    query=query,
                    limit=task.max_results
                )
            elif operation == 'monitor_channel':
                channel_id = task.target
                return await crawler.monitor_channel(channel_id)
            elif operation == 'crawl_video':
                video_id = task.target
                result = await crawler.crawl_video(video_id)
                return [result] if result else []
            
            return []
            
        except Exception as e:
            logger.error(f"YouTube task execution error: {e}")
            return []
    
    async def _execute_tiktok_task(self, crawler: TikTokCrawler, task: CrawlingTask) -> List[CrawlResult]:
        """Execute TikTok-specific crawling task."""
        try:
            operation = task.parameters.get('operation', 'search')
            
            if operation == 'search':
                query = task.target
                return await crawler.search_similar_content(
                    query=query,
                    limit=task.max_results
                )
            elif operation == 'monitor_user':
                username = task.target
                return await crawler.monitor_user(username)
            elif operation == 'crawl_video':
                video_url = task.target
                result = await crawler.crawl_video(video_url)
                return [result] if result else []
            
            return []
            
        except Exception as e:
            logger.error(f"TikTok task execution error: {e}")
            return []
    
    async def _execute_instagram_task(self, crawler: InstagramCrawler, task: CrawlingTask) -> List[CrawlResult]:
        """Execute Instagram-specific crawling task."""
        try:
            operation = task.parameters.get('operation', 'search')
            
            if operation == 'search':
                query = task.target
                return await crawler.search_similar_content(
                    query=query,
                    limit=task.max_results
                )
            elif operation == 'monitor_user':
                username = task.target
                return await crawler.monitor_user(username)
            elif operation == 'crawl_post':
                post_url = task.target
                result = await crawler.crawl_post(post_url)
                return [result] if result else []
            
            return []
            
        except Exception as e:
            logger.error(f"Instagram task execution error: {e}")
            return []
    
    async def _execute_twitter_task(self, crawler: TwitterCrawler, task: CrawlingTask) -> List[CrawlResult]:
        """Execute Twitter-specific crawling task."""
        try:
            operation = task.parameters.get('operation', 'search')
            
            if operation == 'search':
                query = task.target
                return await crawler.search_similar_content(
                    query=query,
                    limit=task.max_results
                )
            elif operation == 'monitor_user':
                username = task.target
                return await crawler.monitor_user(username)
            elif operation == 'crawl_tweet':
                tweet_url = task.target
                result = await crawler.crawl_tweet(tweet_url)
                return [result] if result else []
            
            return []
            
        except Exception as e:
            logger.error(f"Twitter task execution error: {e}")
            return []
    
    async def _execute_web_task(self, crawler: UniversalWebCrawler, task: CrawlingTask) -> List[CrawlResult]:
        """Execute web crawling task."""
        try:
            operation = task.parameters.get('operation', 'crawl_url')
            
            if operation == 'crawl_url':
                url = task.target
                result = await crawler.crawl_url(url)
                return [result] if result else []
            elif operation == 'search_similarity':
                reference_content = task.parameters.get('reference_content', '')
                domains = task.parameters.get('domains', [])
                return await crawler.search_content_similarity(
                    reference_content=reference_content,
                    domains=domains,
                    similarity_threshold=task.similarity_threshold
                )
            
            return []
            
        except Exception as e:
            logger.error(f"Web task execution error: {e}")
            return []
    
    async def _analyze_violations(self, results: List[CrawlResult], task: CrawlingTask) -> List[CrawlResult]:
        """Analyze crawl results for potential violations."""
        try:
            violations = []
            
            for result in results:
                # Check similarity threshold
                similarity_score = result.metadata.get('similarity_score', 0)
                if similarity_score >= task.similarity_threshold:
                    violations.append(result)
                    continue
                
                # Check for known violation patterns
                if self._check_violation_patterns(result, task):
                    violations.append(result)
            
            return violations
            
        except Exception as e:
            logger.error(f"Violation analysis error: {e}")
            return []
    
    def _check_violation_patterns(self, result: CrawlResult, task: CrawlingTask) -> bool:
        """Check for known violation patterns in content."""
        try:
            # Check title/description for known patterns
            text_content = f"{result.title} {result.description}".lower()
            
            # Known violation indicators
            violation_patterns = [
                'unauthorized', 'pirated', 'free download', 'leaked',
                'bootleg', 'stolen', 'copyright', 'dmca'
            ]
            
            for pattern in violation_patterns:
                if pattern in text_content:
                    return True
            
            # Platform-specific checks
            if result.platform == 'youtube':
                return self._check_youtube_violations(result)
            elif result.platform == 'tiktok':
                return self._check_tiktok_violations(result)
            
            return False
            
        except Exception as e:
            logger.error(f"Pattern check error: {e}")
            return False
    
    def _check_youtube_violations(self, result: CrawlResult) -> bool:
        """Check YouTube-specific violation patterns."""
        try:
            metadata = result.metadata.get('platform_specific', {})
            
            # Check for copyright indicators
            if metadata.get('content_rating', {}).get('youtubeDrRating'):
                return True
            
            # Check for blocked content
            if metadata.get('privacy_status') != 'public':
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"YouTube violation check error: {e}")
            return False
    
    def _check_tiktok_violations(self, result: CrawlResult) -> bool:
        """Check TikTok-specific violation patterns."""
        try:
            # Check for suspicious engagement patterns
            engagement = result.metadata.get('engagement', {})
            view_count = result.view_count or 0
            like_count = engagement.get('like_count', 0)
            
            # Suspicious if high views but low engagement
            if view_count > 100000 and like_count < view_count * 0.01:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"TikTok violation check error: {e}")
            return False
    
    async def _send_violation_alerts(self, violations: List[CrawlResult], task: CrawlingTask) -> int:
        """Send alerts for detected violations."""
        try:
            alerts_sent = 0
            
            for violation in violations:
                alert_data = {
                    'task_id': task.task_id,
                    'platform': violation.platform,
                    'url': violation.url,
                    'title': violation.title,
                    'author': violation.author,
                    'similarity_score': violation.metadata.get('similarity_score', 0),
                    'detected_at': datetime.now().isoformat()
                }
                
                # Send notification
                await self.notification_manager.send_violation_alert(alert_data)
                alerts_sent += 1
            
            return alerts_sent
            
        except Exception as e:
            logger.error(f"Alert sending error: {e}")
            return 0
    
    async def run_scheduled_tasks(self):
        """Run scheduled monitoring tasks."""
        try:
            current_time = datetime.now()
            tasks_to_run = []
            
            for task in self.tasks.values():
                if not task.active:
                    continue
                
                should_run = False
                
                # Check if task should run based on mode
                if task.mode == MonitoringMode.CONTINUOUS:
                    # Run if not run recently
                    if not task.last_run or (current_time - task.last_run) > timedelta(minutes=30):
                        should_run = True
                elif task.mode == MonitoringMode.SCHEDULED:
                    # Check schedule pattern (simplified)
                    if task.next_run and current_time >= task.next_run:
                        should_run = True
                
                if should_run:
                    tasks_to_run.append(task)
            
            # Execute tasks with concurrency limit
            semaphore = asyncio.Semaphore(self.max_concurrent_jobs)
            
            async def run_task_with_semaphore(task):
                async with semaphore:
                    return await self.execute_task(task)
            
            if tasks_to_run:
                logger.info(f"Running {len(tasks_to_run)} scheduled tasks")
                await asyncio.gather(*[run_task_with_semaphore(task) for task in tasks_to_run])
            
        except Exception as e:
            logger.error(f"Scheduled tasks execution error: {e}")
    
    async def start_monitoring(self):
        """Start continuous monitoring."""
        self.is_running = True
        logger.info("Crawler orchestrator started")
        
        while self.is_running:
            try:
                await self.run_scheduled_tasks()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.is_running = False
        logger.info("Crawler orchestrator stopped")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        try:
            task = self.tasks.get(task_id)
            if not task:
                return None
            
            # Get recent job results
            recent_jobs = [
                job for job in self.job_results
                if job.task_id == task_id
            ][-10:]  # Last 10 jobs
            
            return {
                'task': asdict(task),
                'recent_jobs': [asdict(job) for job in recent_jobs],
                'is_running': task_id in [job.task_id for job in recent_jobs if job.end_time is None]
            }
            
        except Exception as e:
            logger.error(f"Get task status error: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            active_tasks = sum(1 for task in self.tasks.values() if task.active)
            total_tasks = len(self.tasks)
            running_jobs = len(self.running_jobs)
            
            # Calculate success rate
            recent_jobs = self.job_results[-100:]  # Last 100 jobs
            successful_jobs = sum(1 for job in recent_jobs if job.status == 'success')
            success_rate = successful_jobs / len(recent_jobs) if recent_jobs else 0
            
            return {
                'is_running': self.is_running,
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'running_jobs': running_jobs,
                'available_crawlers': list(self.crawlers.keys()),
                'success_rate': success_rate,
                'total_job_results': len(self.job_results),
                'last_activity': max(
                    (job.start_time for job in self.job_results),
                    default=None
                )
            }
            
        except Exception as e:
            logger.error(f"Get system status error: {e}")
            return {}
    
    async def cleanup(self):
        """Clean up resources."""
        try:
            self.stop_monitoring()
            
            # Cleanup crawlers
            for crawler in self.crawlers.values():
                if hasattr(crawler, 'cleanup'):
                    await crawler.cleanup()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("Crawler orchestrator cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
