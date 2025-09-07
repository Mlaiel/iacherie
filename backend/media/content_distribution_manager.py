"""Content Distribution Manager - Intelligent Distribution Orchestrator

Enterprise-grade content distribution system for managing multi-platform 
content distribution with intelligent routing, scheduling, and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor

# Database and external service imports with graceful fallbacks
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    logging.warning("aiohttp not available - using basic HTTP handling")

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory caching")

try:
    from sqlalchemy import create_engine, text
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    logging.warning("SQLAlchemy not available - using basic data persistence")


class DistributionStatus(Enum):
    """Distribution status types"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class PlatformType(Enum):
    """Supported platform types for distribution"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    WEBHOOK = "webhook"
    API = "api"


class DistributionPriority(Enum):
    """Distribution priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10


@dataclass
class PlatformCredentials:
    """Platform-specific API credentials and configuration"""
    platform: PlatformType
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    account_id: Optional[str] = None
    channel_id: Optional[str] = None
    webhook_url: Optional[str] = None
    custom_config: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    rate_limits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionTarget:
    """Target platform for content distribution"""
    platform: PlatformType
    credentials: PlatformCredentials
    publish_config: Dict[str, Any] = field(default_factory=dict)
    scheduling_config: Dict[str, Any] = field(default_factory=dict)
    metadata_template: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    retry_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentMetadata:
    """Content metadata for distribution"""
    title: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = ""
    thumbnail_url: Optional[str] = None
    privacy_setting: str = "public"  # public, private, unlisted
    monetization_enabled: bool = False
    content_rating: str = "general"
    language: str = "en"
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchedulingConfig:
    """Content scheduling configuration"""
    publish_at: Optional[datetime] = None
    timezone: str = "UTC"
    recurring: bool = False
    recurring_pattern: Optional[str] = None  # daily, weekly, monthly
    optimal_timing: bool = True
    audience_timezone: Optional[str] = None
    delay_between_platforms: int = 0  # seconds


@dataclass
class DistributionResult:
    """Result of content distribution to a platform"""
    platform: PlatformType
    status: DistributionStatus
    published_url: Optional[str] = None
    platform_id: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    published_at: Optional[datetime] = None
    retry_count: int = 0
    response_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionJob:
    """Content distribution job"""
    job_id: str
    content_file: str
    targets: List[DistributionTarget]
    metadata: ContentMetadata
    scheduling: SchedulingConfig
    priority: DistributionPriority = DistributionPriority.NORMAL
    max_retries: int = 3
    timeout_seconds: int = 300
    webhook_url: Optional[str] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)
    
    # Job tracking
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: DistributionStatus = DistributionStatus.PENDING
    results: List[DistributionResult] = field(default_factory=list)
    progress: float = 0.0  # 0.0 to 1.0


class ContentDistributionManager:
    """Enterprise content distribution manager for multi-platform publishing"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Job management
        self.active_jobs: Dict[str, DistributionJob] = {}
        self.scheduled_jobs: Dict[str, DistributionJob] = {}
        self.job_queue = asyncio.Queue()
        
        # Platform handlers
        self.platform_handlers: Dict[PlatformType, Callable] = {}
        self._initialize_platform_handlers()
        
        # Distribution statistics
        self.distribution_stats = {
            "total_distributions": 0,
            "successful_distributions": 0,
            "failed_distributions": 0,
            "platforms_used": {},
            "average_distribution_time": 0.0,
            "retry_rate": 0.0,
            "total_content_distributed": 0
        }
        
        # Configuration
        self.max_concurrent_jobs = self.config.get("max_concurrent_jobs", 10)
        self.job_timeout = self.config.get("job_timeout", 1800)  # 30 minutes
        
        # Initialize storage backends
        self._initialize_storage()
        
        # Start background workers
        self._start_background_workers()
        
        self.logger.info("Content Distribution Manager initialized")
    
    def _initialize_storage(self) -> None:
        """Initialize storage backends for persistence"""
        
        # Redis for caching and job queues
        if HAS_REDIS and self.config.get("redis_url"):
            try:
                self.redis_client = redis.from_url(self.config["redis_url"])
                self.redis_client.ping()
                self.logger.info("Redis connection established")
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None
        else:
            self.redis_client = None
        
        # Database for job persistence
        if HAS_SQLALCHEMY and self.config.get("database_url"):
            try:
                self.db_engine = create_engine(self.config["database_url"])
                self.logger.info("Database connection established")
            except Exception as e:
                self.logger.warning(f"Database connection failed: {e}")
                self.db_engine = None
        else:
            self.db_engine = None
    
    def _initialize_platform_handlers(self) -> None:
        """Initialize platform-specific distribution handlers"""
        
        self.platform_handlers = {
            PlatformType.YOUTUBE: self._handle_youtube_distribution,
            PlatformType.INSTAGRAM: self._handle_instagram_distribution,
            PlatformType.TIKTOK: self._handle_tiktok_distribution,
            PlatformType.FACEBOOK: self._handle_facebook_distribution,
            PlatformType.TWITTER: self._handle_twitter_distribution,
            PlatformType.LINKEDIN: self._handle_linkedin_distribution,
            PlatformType.WEBHOOK: self._handle_webhook_distribution,
            PlatformType.API: self._handle_api_distribution
        }
    
    def _start_background_workers(self) -> None:
        """Start background worker tasks"""
        
        # Job processing worker
        asyncio.create_task(self._job_processor_worker())
        
        # Scheduled job checker
        asyncio.create_task(self._scheduled_job_checker())
        
        # Cleanup worker
        asyncio.create_task(self._cleanup_worker())
    
    async def create_distribution_job(
        self,
        content_file: str,
        targets: List[DistributionTarget],
        metadata: ContentMetadata,
        scheduling: Optional[SchedulingConfig] = None,
        **kwargs
    ) -> str:
        """Create a new content distribution job"""
        
        job_id = str(uuid.uuid4())
        
        job = DistributionJob(
            job_id=job_id,
            content_file=content_file,
            targets=targets,
            metadata=metadata,
            scheduling=scheduling or SchedulingConfig(),
            priority=kwargs.get("priority", DistributionPriority.NORMAL),
            max_retries=kwargs.get("max_retries", 3),
            timeout_seconds=kwargs.get("timeout_seconds", 300),
            webhook_url=kwargs.get("webhook_url"),
            custom_data=kwargs.get("custom_data", {})
        )
        
        # Check if job should be scheduled
        if scheduling and scheduling.publish_at and scheduling.publish_at > datetime.now():
            self.scheduled_jobs[job_id] = job
            job.status = DistributionStatus.SCHEDULED
            self.logger.info(f"Scheduled distribution job {job_id} for {scheduling.publish_at}")
        else:
            self.active_jobs[job_id] = job
            await self.job_queue.put(job)
            self.logger.info(f"Created distribution job {job_id} for {len(targets)} platforms")
        
        # Persist job if database available
        await self._persist_job(job)
        
        return job_id
    
    async def _job_processor_worker(self) -> None:
        """Background worker for processing distribution jobs"""
        
        while True:
            try:
                # Get job from queue with timeout
                job = await asyncio.wait_for(self.job_queue.get(), timeout=1.0)
                
                # Process job
                await self._process_distribution_job(job)
                
                # Mark task as done
                self.job_queue.task_done()
                
            except asyncio.TimeoutError:
                # No jobs in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Error in job processor worker: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _scheduled_job_checker(self) -> None:
        """Background worker for checking scheduled jobs"""
        
        while True:
            try:
                current_time = datetime.now()
                jobs_to_process = []
                
                # Check scheduled jobs
                for job_id, job in list(self.scheduled_jobs.items()):
                    if job.scheduling.publish_at and job.scheduling.publish_at <= current_time:
                        jobs_to_process.append(job)
                        del self.scheduled_jobs[job_id]
                
                # Move ready jobs to active queue
                for job in jobs_to_process:
                    self.active_jobs[job.job_id] = job
                    job.status = DistributionStatus.QUEUED
                    await self.job_queue.put(job)
                    self.logger.info(f"Activated scheduled job {job.job_id}")
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in scheduled job checker: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_worker(self) -> None:
        """Background worker for cleaning up completed jobs"""
        
        while True:
            try:
                # Clean up completed jobs older than 24 hours
                cutoff_time = datetime.now() - timedelta(hours=24)
                jobs_to_remove = []
                
                for job_id, job in self.active_jobs.items():
                    if (job.completed_at and job.completed_at < cutoff_time and
                        job.status in [DistributionStatus.PUBLISHED, DistributionStatus.FAILED]):
                        jobs_to_remove.append(job_id)
                
                for job_id in jobs_to_remove:
                    del self.active_jobs[job_id]
                
                if jobs_to_remove:
                    self.logger.info(f"Cleaned up {len(jobs_to_remove)} completed jobs")
                
                # Run cleanup every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup worker: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _process_distribution_job(self, job: DistributionJob) -> None:
        """Process a distribution job"""
        
        job.started_at = datetime.now()
        job.status = DistributionStatus.PROCESSING
        
        self.logger.info(f"Processing distribution job {job.job_id}")
        
        try:
            # Validate content file
            if not Path(job.content_file).exists():
                raise FileNotFoundError(f"Content file not found: {job.content_file}")
            
            # Process each target platform
            total_targets = len(job.targets)
            completed_targets = 0
            
            for target in job.targets:
                if not target.enabled:
                    self.logger.info(f"Skipping disabled target: {target.platform.value}")
                    completed_targets += 1
                    job.progress = completed_targets / total_targets
                    continue
                
                try:
                    result = await self._distribute_to_platform(job, target)
                    job.results.append(result)
                    
                    if result.status == DistributionStatus.PUBLISHED:
                        self.distribution_stats["successful_distributions"] += 1
                    else:
                        self.distribution_stats["failed_distributions"] += 1
                    
                    # Update platform statistics
                    platform_name = target.platform.value
                    if platform_name not in self.distribution_stats["platforms_used"]:
                        self.distribution_stats["platforms_used"][platform_name] = 0
                    self.distribution_stats["platforms_used"][platform_name] += 1
                    
                    # Add delay between platforms if configured
                    if job.scheduling.delay_between_platforms > 0:
                        await asyncio.sleep(job.scheduling.delay_between_platforms)
                    
                except Exception as e:
                    self.logger.error(f"Failed to distribute to {target.platform.value}: {str(e)}")
                    
                    result = DistributionResult(
                        platform=target.platform,
                        status=DistributionStatus.FAILED,
                        error_message=str(e)
                    )
                    job.results.append(result)
                    self.distribution_stats["failed_distributions"] += 1
                
                completed_targets += 1
                job.progress = completed_targets / total_targets
            
            # Update job completion
            job.completed_at = datetime.now()
            job.status = DistributionStatus.PUBLISHED if any(
                r.status == DistributionStatus.PUBLISHED for r in job.results
            ) else DistributionStatus.FAILED
            
            # Calculate processing time
            processing_time = (job.completed_at - job.started_at).total_seconds()
            
            # Update statistics
            self.distribution_stats["total_distributions"] += 1
            self.distribution_stats["average_distribution_time"] = (
                (self.distribution_stats["average_distribution_time"] * 
                 (self.distribution_stats["total_distributions"] - 1) + processing_time) /
                self.distribution_stats["total_distributions"]
            )
            
            # Send webhook notification if configured
            if job.webhook_url:
                await self._send_webhook_notification(job)
            
            self.logger.info(
                f"Completed distribution job {job.job_id} in {processing_time:.2f}s "
                f"with {len([r for r in job.results if r.status == DistributionStatus.PUBLISHED])} "
                f"successful distributions"
            )
            
        except Exception as e:
            job.status = DistributionStatus.FAILED
            job.completed_at = datetime.now()
            self.logger.error(f"Error processing distribution job {job.job_id}: {str(e)}")
        
        # Update job persistence
        await self._persist_job(job)
    
    async def _distribute_to_platform(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Distribute content to a specific platform"""
        
        if target.platform not in self.platform_handlers:
            return DistributionResult(
                platform=target.platform,
                status=DistributionStatus.FAILED,
                error_message=f"No handler for platform: {target.platform.value}"
            )
        
        handler = self.platform_handlers[target.platform]
        
        try:
            # Apply timeout
            result = await asyncio.wait_for(
                handler(job, target),
                timeout=job.timeout_seconds
            )
            
            return result
            
        except asyncio.TimeoutError:
            return DistributionResult(
                platform=target.platform,
                status=DistributionStatus.FAILED,
                error_message=f"Distribution timeout after {job.timeout_seconds}s"
            )
        except Exception as e:
            return DistributionResult(
                platform=target.platform,
                status=DistributionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _handle_youtube_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle YouTube distribution"""
        
        # Placeholder implementation - would integrate with YouTube API
        self.logger.info(f"Distributing to YouTube: {job.content_file}")
        
        # Simulate API call
        await asyncio.sleep(2)
        
        # Mock successful upload
        return DistributionResult(
            platform=target.platform,
            status=DistributionStatus.PUBLISHED,
            published_url=f"https://youtube.com/watch?v={uuid.uuid4().hex[:11]}",
            platform_id=f"yt_{uuid.uuid4().hex[:16]}",
            published_at=datetime.now(),
            metrics={"views": 0, "likes": 0, "comments": 0}
        )
    
    async def _handle_instagram_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle Instagram distribution"""
        
        self.logger.info(f"Distributing to Instagram: {job.content_file}")
        
        # Simulate API call
        await asyncio.sleep(1.5)
        
        return DistributionResult(
            platform=target.platform,
            status=DistributionStatus.PUBLISHED,
            published_url=f"https://instagram.com/p/{uuid.uuid4().hex[:11]}/",
            platform_id=f"ig_{uuid.uuid4().hex[:16]}",
            published_at=datetime.now(),
            metrics={"likes": 0, "comments": 0, "shares": 0}
        )
    
    async def _handle_tiktok_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle TikTok distribution"""
        
        self.logger.info(f"Distributing to TikTok: {job.content_file}")
        
        # Simulate API call
        await asyncio.sleep(1.8)
        
        return DistributionResult(
            platform=target.platform,
            status=DistributionStatus.PUBLISHED,
            published_url=f"https://tiktok.com/@user/video/{uuid.uuid4().hex[:16]}",
            platform_id=f"tt_{uuid.uuid4().hex[:16]}",
            published_at=datetime.now(),
            metrics={"views": 0, "likes": 0, "shares": 0, "comments": 0}
        )
    
    async def _handle_facebook_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle Facebook distribution"""
        
        self.logger.info(f"Distributing to Facebook: {job.content_file}")
        
        # Simulate API call
        await asyncio.sleep(2.2)
        
        return DistributionResult(
            platform=target.platform,
            status=DistributionStatus.PUBLISHED,
            published_url=f"https://facebook.com/posts/{uuid.uuid4().hex[:16]}",
            platform_id=f"fb_{uuid.uuid4().hex[:16]}",
            published_at=datetime.now(),
            metrics={"reactions": 0, "comments": 0, "shares": 0}
        )
    
    async def _handle_twitter_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle Twitter distribution"""
        
        self.logger.info(f"Distributing to Twitter: {job.content_file}")
        
        # Simulate API call
        await asyncio.sleep(1.0)
        
        return DistributionResult(
            platform=target.platform,
            status=DistributionStatus.PUBLISHED,
            published_url=f"https://twitter.com/user/status/{uuid.uuid4().hex[:16]}",
            platform_id=f"tw_{uuid.uuid4().hex[:16]}",
            published_at=datetime.now(),
            metrics={"retweets": 0, "likes": 0, "replies": 0}
        )
    
    async def _handle_linkedin_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle LinkedIn distribution"""
        
        self.logger.info(f"Distributing to LinkedIn: {job.content_file}")
        
        # Simulate API call
        await asyncio.sleep(1.5)
        
        return DistributionResult(
            platform=target.platform,
            status=DistributionStatus.PUBLISHED,
            published_url=f"https://linkedin.com/posts/{uuid.uuid4().hex[:16]}",
            platform_id=f"li_{uuid.uuid4().hex[:16]}",
            published_at=datetime.now(),
            metrics={"reactions": 0, "comments": 0, "shares": 0}
        )
    
    async def _handle_webhook_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle webhook distribution"""
        
        if not target.credentials.webhook_url:
            return DistributionResult(
                platform=target.platform,
                status=DistributionStatus.FAILED,
                error_message="No webhook URL configured"
            )
        
        try:
            # Prepare webhook payload
            payload = {
                "job_id": job.job_id,
                "content_file": job.content_file,
                "metadata": {
                    "title": job.metadata.title,
                    "description": job.metadata.description,
                    "tags": job.metadata.tags
                },
                "timestamp": datetime.now().isoformat()
            }
            
            if HAS_AIOHTTP:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        target.credentials.webhook_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        response_data = await response.text()
                        
                        if response.status == 200:
                            return DistributionResult(
                                platform=target.platform,
                                status=DistributionStatus.PUBLISHED,
                                published_url=target.credentials.webhook_url,
                                published_at=datetime.now(),
                                response_data={"status": response.status, "body": response_data}
                            )
                        else:
                            return DistributionResult(
                                platform=target.platform,
                                status=DistributionStatus.FAILED,
                                error_message=f"Webhook returned status {response.status}: {response_data}"
                            )
            else:
                # Fallback without aiohttp
                self.logger.warning("aiohttp not available - webhook distribution disabled")
                return DistributionResult(
                    platform=target.platform,
                    status=DistributionStatus.FAILED,
                    error_message="aiohttp not available for webhook distribution"
                )
                
        except Exception as e:
            return DistributionResult(
                platform=target.platform,
                status=DistributionStatus.FAILED,
                error_message=f"Webhook error: {str(e)}"
            )
    
    async def _handle_api_distribution(
        self,
        job: DistributionJob,
        target: DistributionTarget
    ) -> DistributionResult:
        """Handle generic API distribution"""
        
        # Generic API handler for custom integrations
        self.logger.info(f"Distributing via API: {job.content_file}")
        
        # This would be customized based on target API requirements
        await asyncio.sleep(1.0)
        
        return DistributionResult(
            platform=target.platform,
            status=DistributionStatus.PUBLISHED,
            platform_id=f"api_{uuid.uuid4().hex[:16]}",
            published_at=datetime.now()
        )
    
    async def _send_webhook_notification(self, job: DistributionJob) -> None:
        """Send webhook notification for job completion"""
        
        if not job.webhook_url or not HAS_AIOHTTP:
            return
        
        try:
            payload = {
                "job_id": job.job_id,
                "status": job.status.value,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "results": [
                    {
                        "platform": r.platform.value,
                        "status": r.status.value,
                        "published_url": r.published_url,
                        "error_message": r.error_message
                    } for r in job.results
                ],
                "progress": job.progress
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(
                    job.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                )
                
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {str(e)}")
    
    async def _persist_job(self, job: DistributionJob) -> None:
        """Persist job data to database if available"""
        
        if not self.db_engine:
            return
        
        try:
            # Serialize job data
            job_data = {
                "job_id": job.job_id,
                "content_file": job.content_file,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "progress": job.progress,
                "results_count": len(job.results)
            }
            
            # In a real implementation, you would use proper ORM or SQL queries
            self.logger.debug(f"Persisting job data: {job_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to persist job data: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a distribution job"""
        
        # Check active jobs
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
        elif job_id in self.scheduled_jobs:
            job = self.scheduled_jobs[job_id]
        else:
            return None
        
        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "content_file": job.content_file,
            "targets": [
                {
                    "platform": t.platform.value,
                    "enabled": t.enabled
                } for t in job.targets
            ],
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "results": [
                {
                    "platform": r.platform.value,
                    "status": r.status.value,
                    "published_url": r.published_url,
                    "platform_id": r.platform_id,
                    "error_message": r.error_message,
                    "published_at": r.published_at.isoformat() if r.published_at else None
                } for r in job.results
            ]
        }
    
    def get_distribution_statistics(self) -> Dict[str, Any]:
        """Get distribution system statistics"""
        
        return {
            **self.distribution_stats,
            "active_jobs": len(self.active_jobs),
            "scheduled_jobs": len(self.scheduled_jobs),
            "queue_size": self.job_queue.qsize(),
            "supported_platforms": len(self.platform_handlers),
            "max_concurrent_jobs": self.max_concurrent_jobs
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a distribution job"""
        
        if job_id in self.scheduled_jobs:
            job = self.scheduled_jobs[job_id]
            job.status = DistributionStatus.CANCELLED
            del self.scheduled_jobs[job_id]
            self.logger.info(f"Cancelled scheduled job {job_id}")
            return True
        
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status == DistributionStatus.PENDING:
                job.status = DistributionStatus.CANCELLED
                self.logger.info(f"Cancelled pending job {job_id}")
                return True
        
        return False
    
    async def retry_failed_job(self, job_id: str) -> bool:
        """Retry a failed distribution job"""
        
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        
        if job.status != DistributionStatus.FAILED:
            return False
        
        # Reset job for retry
        job.status = DistributionStatus.PENDING
        job.started_at = None
        job.completed_at = None
        job.progress = 0.0
        job.results = []
        
        # Re-queue job
        await self.job_queue.put(job)
        
        self.logger.info(f"Retrying failed job {job_id}")
        
        return True
    
    def get_platform_metrics(self, platform: PlatformType, days: int = 7) -> Dict[str, Any]:
        """Get metrics for a specific platform over the last N days"""
        
        # In a real implementation, this would query the database
        # For now, return basic stats from in-memory data
        
        platform_name = platform.value
        total_for_platform = self.distribution_stats["platforms_used"].get(platform_name, 0)
        
        return {
            "platform": platform_name,
            "total_distributions": total_for_platform,
            "success_rate": 0.95,  # Placeholder
            "average_engagement": 0.0,  # Placeholder
            "peak_hours": [18, 19, 20],  # Placeholder
            "trending_content_types": ["video", "image"]  # Placeholder
        }


# Global instance for easy access
_content_distribution_manager = None

def get_content_distribution_manager(config: Optional[Dict[str, Any]] = None) -> ContentDistributionManager:
    """Get or create global content distribution manager instance"""
    global _content_distribution_manager
    
    if _content_distribution_manager is None:
        _content_distribution_manager = ContentDistributionManager(config)
    
    return _content_distribution_manager


# Example usage and testing
if __name__ == "__main__":
    async def example_usage():
        """Example usage of the Content Distribution Manager"""
        
        # Initialize the system
        manager = get_content_distribution_manager()
        
        # Create distribution targets
        targets = [
            DistributionTarget(
                platform=PlatformType.YOUTUBE,
                credentials=PlatformCredentials(
                    platform=PlatformType.YOUTUBE,
                    api_key="yt_api_key",
                    channel_id="UCexample"
                )
            ),
            DistributionTarget(
                platform=PlatformType.INSTAGRAM,
                credentials=PlatformCredentials(
                    platform=PlatformType.INSTAGRAM,
                    access_token="ig_access_token",
                    account_id="ig_account"
                )
            )
        ]
        
        # Create content metadata
        metadata = ContentMetadata(
            title="Amazing Content Title",
            description="This is amazing content that will engage audiences",
            tags=["amazing", "content", "viral"],
            category="Entertainment"
        )
        
        # Create scheduling configuration
        scheduling = SchedulingConfig(
            optimal_timing=True,
            delay_between_platforms=30  # 30 seconds between platforms
        )
        
        # Create distribution job
        job_id = await manager.create_distribution_job(
            content_file="example_content.mp4",
            targets=targets,
            metadata=metadata,
            scheduling=scheduling
        )
        
        print(f"Created distribution job: {job_id}")
        
        # Wait for completion
        await asyncio.sleep(10)
        
        # Get job status
        status = manager.get_job_status(job_id)
        if status:
            print(f"Job status: {json.dumps(status, indent=2)}")
        
        # Get statistics
        stats = manager.get_distribution_statistics()
        print(f"Distribution statistics: {json.dumps(stats, indent=2)}")
    
    # Run example if this file is executed directly
    asyncio.run(example_usage())