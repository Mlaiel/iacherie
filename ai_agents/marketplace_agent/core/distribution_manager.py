"""Distribution Manager - Multi-Platform Content Distribution System

Manages content distribution across multiple platforms and channels,
orchestrating delivery, optimization, and performance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from .marketplace_agent import MarketplaceConfig, ContentType, PriceModel


class DistributionPlatform(Enum):
    """Supported distribution platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"


class DistributionStatus(Enum):
    """Content distribution status."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class ContentOptimization(Enum):
    """Content optimization strategies."""
    AUTO_RESIZE = "auto_resize"
    QUALITY_ADAPTIVE = "quality_adaptive"
    PLATFORM_SPECIFIC = "platform_specific"
    MOBILE_OPTIMIZED = "mobile_optimized"
    BANDWIDTH_ADAPTIVE = "bandwidth_adaptive"


@dataclass
class PlatformConfig:
    """Platform-specific configuration."""
    platform: DistributionPlatform = DistributionPlatform.INSTAGRAM
    enabled: bool = True
    api_credentials: Dict[str, str] = field(default_factory=dict)
    content_formats: List[str] = field(default_factory=list)
    max_file_size_mb: int = 100
    supported_content_types: List[ContentType] = field(default_factory=list)
    posting_schedule: Dict[str, Any] = field(default_factory=dict)
    optimization_settings: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)


@dataclass
class DistributionJob:
    """Content distribution job."""
    id: str = ""
    content_id: str = ""
    creator_id: int = 0
    platforms: List[DistributionPlatform] = field(default_factory=list)
    status: DistributionStatus = DistributionStatus.PENDING
    scheduled_time: Optional[datetime] = None
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    platform_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    optimization_applied: List[ContentOptimization] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_details: Optional[str] = None
    retry_count: int = 0
    priority: int = 5  # 1-10, higher = more priority


@dataclass
class DistributionAnalytics:
    """Distribution performance analytics."""
    job_id: str = ""
    platform: DistributionPlatform = DistributionPlatform.INSTAGRAM
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    clicks: int = 0
    shares: int = 0
    comments: int = 0
    likes: int = 0
    views: int = 0
    conversion_rate: float = 0.0
    revenue_generated: float = 0.0
    cost_per_impression: float = 0.0
    roi: float = 0.0
    demographics: Dict[str, Any] = field(default_factory=dict)
    geographic_data: Dict[str, Any] = field(default_factory=dict)
    performance_score: float = 0.0
    collected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentVariant:
    """Platform-optimized content variant."""
    platform: DistributionPlatform = DistributionPlatform.INSTAGRAM
    file_path: str = ""
    format: str = ""
    resolution: str = ""
    file_size_mb: float = 0.0
    duration_seconds: Optional[int] = None
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    thumbnail_path: Optional[str] = None
    captions: Dict[str, str] = field(default_factory=dict)  # language: caption
    optimization_applied: List[ContentOptimization] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class DistributionManager:
    """
    Advanced multi-platform content distribution system.
    
    Manages automated content distribution across social media platforms,
    streaming services, and content networks with intelligent optimization,
    scheduling, and performance tracking.
    """
    def __init__(self, config: MarketplaceConfig):
        """
        Initialize distribution management system.
        
        Args:
            config: Marketplace configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize distribution components
        self.platform_configs = {}
        self.active_jobs = {}
        self.job_queue = []
        self.distribution_analytics = {}
        
        # Performance tracking
        self.distribution_metrics = {
            "total_distributions": 0,
            "successful_distributions": 0,
            "failed_distributions": 0,
            "average_processing_time": 0.0,
            "total_reach": 0,
            "total_engagement": 0.0
        }
        
        # Initialize platform configurations
        self._initialize_platform_configs()
        
        # Start background workers
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        self.logger.info("Distribution management system initialized")

    def _initialize_platform_configs(self) -> None:
        """Initialize platform-specific configurations."""
        try:
            # Instagram configuration
            self.platform_configs[DistributionPlatform.INSTAGRAM] = PlatformConfig(
                platform=DistributionPlatform.INSTAGRAM,
                content_formats=["jpg", "png", "mp4", "mov"],
                max_file_size_mb=100,
                supported_content_types=[ContentType.IMAGE, ContentType.VIDEO, ContentType.STORY],
                rate_limits={"posts_per_hour": 5, "api_calls_per_minute": 200}
            )
            
            # TikTok configuration
            self.platform_configs[DistributionPlatform.TIKTOK] = PlatformConfig(
                platform=DistributionPlatform.TIKTOK,
                content_formats=["mp4", "mov", "avi"],
                max_file_size_mb=287,
                supported_content_types=[ContentType.VIDEO, ContentType.AUDIO],
                rate_limits={"posts_per_day": 10, "api_calls_per_minute": 100}
            )
            
            # YouTube configuration
            self.platform_configs[DistributionPlatform.YOUTUBE] = PlatformConfig(
                platform=DistributionPlatform.YOUTUBE,
                content_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
                max_file_size_mb=12000,  # 12GB
                supported_content_types=[ContentType.VIDEO, ContentType.AUDIO],
                rate_limits={"uploads_per_day": 100, "api_calls_per_minute": 1000}
            )
            
            # Add more platform configurations as needed
            self.logger.info("Platform configurations initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize platform configs: {e}")
            raise

    async def create_distribution_job(
        self,
        content_id: str,
        creator_id: int,
        platforms: List[DistributionPlatform],
        scheduled_time: Optional[datetime] = None,
        priority: int = 5
    ) -> DistributionJob:
        """
        Create a new content distribution job.
        
        Args:
            content_id: Unique content identifier
            creator_id: Creator user ID
            platforms: Target distribution platforms
            scheduled_time: Optional scheduling time
            priority: Job priority (1-10)
            
        Returns:
            Created distribution job
        """
        try:
            job = DistributionJob(
                id=f"dist_{content_id}_{int(datetime.utcnow().timestamp())}",
                content_id=content_id,
                creator_id=creator_id,
                platforms=platforms,
                scheduled_time=scheduled_time,
                status=DistributionStatus.PENDING,
                priority=priority
            )
            
            # Validate platforms
            valid_platforms = []
            for platform in platforms:
                if platform in self.platform_configs and self.platform_configs[platform].enabled:
                    valid_platforms.append(platform)
                else:
                    self.logger.warning(f"Platform {platform.value} not configured or disabled")
            
            job.platforms = valid_platforms
            
            if not valid_platforms:
                job.status = DistributionStatus.FAILED
                job.error_details = "No valid platforms configured"
                return job
            
            # Add to job queue
            self.active_jobs[job.id] = job
            
            if scheduled_time and scheduled_time > datetime.utcnow():
                job.status = DistributionStatus.SCHEDULED
            else:
                self.job_queue.append(job)
                job.status = DistributionStatus.QUEUED
            
            self.logger.info(f"Distribution job created: {job.id} for platforms {[p.value for p in valid_platforms]}")
            
            return job

        except Exception as e:
            self.logger.error(f"Failed to create distribution job: {e}")
            raise

    async def process_distribution_queue(self) -> Dict[str, Any]:
        """
        Process pending distribution jobs in the queue.
        
        Returns:
            Processing summary
        """
        try:
            if not self.job_queue:
                return {"processed": 0, "message": "No jobs in queue"}
            
            processed_jobs = []
            failed_jobs = []
            
            # Sort by priority and creation time
            self.job_queue.sort(key=lambda x: (-x.priority, x.created_at))
            
            # Process jobs concurrently
            tasks = []
            for job in self.job_queue[:10]:  # Process up to 10 jobs at once
                if job.status == DistributionStatus.QUEUED:
                    task = asyncio.create_task(self._process_single_job(job))
                    tasks.append(task)
            
            # Wait for all tasks to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    job = self.job_queue[i]
                    if isinstance(result, Exception):
                        job.status = DistributionStatus.FAILED
                        job.error_details = str(result)
                        failed_jobs.append(job.id)
                    else:
                        processed_jobs.append(job.id)
            
            # Remove processed jobs from queue
            self.job_queue = [
                job for job in self.job_queue 
                if job.id not in processed_jobs and job.id not in failed_jobs
            ]
            
            return {
                "processed": len(processed_jobs),
                "failed": len(failed_jobs),
                "remaining_in_queue": len(self.job_queue),
                "processed_jobs": processed_jobs,
                "failed_jobs": failed_jobs
            }

        except Exception as e:
            self.logger.error(f"Queue processing failed: {e}")
            return {"error": str(e)}

    async def optimize_content_for_platforms(
        self,
        content_id: str,
        platforms: List[DistributionPlatform]
    ) -> Dict[DistributionPlatform, ContentVariant]:
        """
        Create optimized content variants for each target platform.
        
        Args:
            content_id: Content to optimize
            platforms: Target platforms
            
        Returns:
            Platform-specific content variants
        """
        try:
            content_variants = {}
            
            # Get original content metadata
            original_content = await self._get_content_metadata(content_id)
            
            for platform in platforms:
                if platform not in self.platform_configs:
                    continue
                
                platform_config = self.platform_configs[platform]
                
                # Create optimized variant
                variant = await self._create_platform_variant(
                    original_content,
                    platform,
                    platform_config
                )
                
                content_variants[platform] = variant
            
            self.logger.info(f"Content optimized for {len(content_variants)} platforms")
            return content_variants

        except Exception as e:
            self.logger.error(f"Content optimization failed: {e}")
            return {}

    async def get_distribution_analytics(
        self,
        job_id: Optional[str] = None,
        creator_id: Optional[int] = None,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """
        Retrieve comprehensive distribution analytics.
        
        Args:
            job_id: Specific job ID to analyze
            creator_id: Creator to analyze
            time_range: Time range for analysis
            
        Returns:
            Distribution analytics data
        """
        try:
            start_date, end_date = await self._parse_time_range(time_range)
            
            if job_id:
                # Single job analytics
                analytics = await self._get_job_analytics(job_id)
                return {"job_analytics": analytics}
            
            elif creator_id:
                # Creator-specific analytics
                creator_analytics = await self._get_creator_analytics(creator_id, start_date, end_date)
                return {"creator_analytics": creator_analytics}
            
            else:
                # Overall platform analytics
                platform_analytics = await self._get_platform_analytics(start_date, end_date)
                
                return {
                    "overall_metrics": {
                        "total_distributions": self.distribution_metrics["total_distributions"],
                        "success_rate": self._calculate_success_rate(),
                        "average_processing_time": self.distribution_metrics["average_processing_time"],
                        "total_reach": self.distribution_metrics["total_reach"],
                        "average_engagement_rate": self._calculate_average_engagement_rate()
                    },
                    "platform_breakdown": platform_analytics,
                    "performance_trends": await self._calculate_performance_trends(start_date, end_date)
                }

        except Exception as e:
            self.logger.error(f"Analytics retrieval failed: {e}")
            return {"error": str(e)}

    async def schedule_recurring_distribution(
        self,
        content_id: str,
        creator_id: int,
        platforms: List[DistributionPlatform],
        schedule_config: Dict[str, Any]
    ) -> str:
        """
        Schedule recurring content distribution.
        
        Args:
            content_id: Content to distribute
            creator_id: Creator user ID
            platforms: Target platforms
            schedule_config: Scheduling configuration
            
        Returns:
            Recurring schedule ID
        """
        try:
            schedule_id = f"recurring_{content_id}_{int(datetime.utcnow().timestamp())}"
            
            # Validate schedule configuration
            if not await self._validate_schedule_config(schedule_config):
                raise ValueError("Invalid schedule configuration")
            
            # Create recurring schedule
            recurring_schedule = {
                "id": schedule_id,
                "content_id": content_id,
                "creator_id": creator_id,
                "platforms": platforms,
                "config": schedule_config,
                "next_execution": await self._calculate_next_execution(schedule_config),
                "created_at": datetime.utcnow(),
                "active": True
            }
            
            # Store schedule (would persist to database)
            # self.recurring_schedules[schedule_id] = recurring_schedule
            
            self.logger.info(f"Recurring distribution scheduled: {schedule_id}")
            return schedule_id

        except Exception as e:
            self.logger.error(f"Recurring schedule creation failed: {e}")
            raise

    async def cancel_distribution_job(self, job_id: str) -> bool:
        """
        Cancel a distribution job.
        
        Args:
            job_id: Job to cancel
            
        Returns:
            Success status
        """
        try:
            if job_id not in self.active_jobs:
                return False
            
            job = self.active_jobs[job_id]
            
            if job.status in [DistributionStatus.COMPLETED, DistributionStatus.FAILED]:
                return False
            
            job.status = DistributionStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            
            # Remove from queue if present
            self.job_queue = [j for j in self.job_queue if j.id != job_id]
            
            self.logger.info(f"Distribution job cancelled: {job_id}")
            return True

        except Exception as e:
            self.logger.error(f"Job cancellation failed: {e}")
            return False

    async def get_job_status(self, job_id: str) -> Optional[DistributionJob]:
        """
        Get current status of a distribution job.
        
        Args:
            job_id: Job to check
            
        Returns:
            Job status information
        """
        try:
            if job_id in self.active_jobs:
                return self.active_jobs[job_id]
            return None

        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return None

    async def _process_single_job(self, job: DistributionJob) -> bool:
        """
        Process a single distribution job.
        
        Args:
            job: Job to process
            
        Returns:
            Success status
        """
        try:
            job.status = DistributionStatus.PROCESSING
            job.started_at = datetime.utcnow()
            
            # Optimize content for platforms
            content_variants = await self.optimize_content_for_platforms(
                job.content_id, 
                job.platforms
            )
            
            if not content_variants:
                raise Exception("Content optimization failed")
            
            # Distribute to each platform
            platform_results = {}
            
            for platform in job.platforms:
                try:
                    if platform in content_variants:
                        result = await self._distribute_to_platform(
                            platform,
                            content_variants[platform],
                            job
                        )
                        platform_results[platform.value] = result
                    else:
                        platform_results[platform.value] = {
                            "success": False,
                            "error": "Content variant not available"
                        }
                except Exception as platform_error:
                    platform_results[platform.value] = {
                        "success": False,
                        "error": str(platform_error)
                    }
            
            job.platform_results = platform_results
            
            # Check overall success
            successful_platforms = sum(
                1 for result in platform_results.values() 
                if result.get("success", False)
            )
            
            if successful_platforms > 0:
                job.status = DistributionStatus.PUBLISHED
                self.distribution_metrics["successful_distributions"] += 1
            else:
                job.status = DistributionStatus.FAILED
                job.error_details = "Failed to distribute to any platform"
                self.distribution_metrics["failed_distributions"] += 1
            
            job.completed_at = datetime.utcnow()
            self.distribution_metrics["total_distributions"] += 1
            
            # Update processing time metrics
            processing_time = (job.completed_at - job.started_at).total_seconds()
            await self._update_processing_time_metrics(processing_time)
            
            return successful_platforms > 0

        except Exception as e:
            job.status = DistributionStatus.FAILED
            job.error_details = str(e)
            job.completed_at = datetime.utcnow()
            self.distribution_metrics["failed_distributions"] += 1
            self.logger.error(f"Job processing failed: {e}")
            return False

    async def _distribute_to_platform(
        self,
        platform: DistributionPlatform,
        content_variant: ContentVariant,
        job: DistributionJob
    ) -> Dict[str, Any]:
        """
        Distribute content to a specific platform.
        
        Args:
            platform: Target platform
            content_variant: Optimized content variant
            job: Distribution job
            
        Returns:
            Distribution result
        """
        try:
            platform_config = self.platform_configs[platform]
            
            # Check rate limits
            if not await self._check_rate_limits(platform):
                return {
                    "success": False,
                    "error": "Rate limit exceeded",
                    "retry_after": 3600  # 1 hour
                }
            
            # Platform-specific distribution logic
            if platform == DistributionPlatform.INSTAGRAM:
                result = await self._distribute_to_instagram(content_variant, job)
            elif platform == DistributionPlatform.TIKTOK:
                result = await self._distribute_to_tiktok(content_variant, job)
            elif platform == DistributionPlatform.YOUTUBE:
                result = await self._distribute_to_youtube(content_variant, job)
            else:
                result = await self._distribute_generic(platform, content_variant, job)
            
            # Update rate limit tracking
            await self._update_rate_limits(platform)
            
            return result

        except Exception as e:
            self.logger.error(f"Platform distribution failed for {platform.value}: {e}")
            return {"success": False, "error": str(e)}

    async def _get_content_metadata(self, content_id: str) -> Dict[str, Any]:
        """Get metadata for content to be distributed."""
        # Mock implementation - would fetch from content database
        return {
            "id": content_id,
            "title": "Sample Content",
            "description": "Content description",
            "file_path": f"/content/{content_id}.mp4",
            "content_type": ContentType.VIDEO,
            "duration": 60,
            "resolution": "1920x1080",
            "file_size_mb": 25.5,
            "tags": ["sample", "content"],
            "created_at": datetime.utcnow()
        }

    async def _create_platform_variant(
        self,
        original_content: Dict[str, Any],
        platform: DistributionPlatform,
        platform_config: PlatformConfig
    ) -> ContentVariant:
        """Create optimized content variant for specific platform."""
        try:
            variant = ContentVariant(
                platform=platform,
                file_path=original_content["file_path"],
                format=original_content.get("format", "mp4"),
                resolution=original_content.get("resolution", "1920x1080"),
                file_size_mb=original_content.get("file_size_mb", 0.0),
                duration_seconds=original_content.get("duration"),
                title=original_content.get("title", ""),
                description=original_content.get("description", ""),
                tags=original_content.get("tags", [])
            )
            
            # Apply platform-specific optimizations
            if platform == DistributionPlatform.INSTAGRAM:
                # Instagram optimizations
                if variant.resolution == "1920x1080":
                    variant.resolution = "1080x1080"  # Square format preferred
                    variant.optimization_applied.append(ContentOptimization.AUTO_RESIZE)
                
                # Limit video length for Instagram
                if variant.duration_seconds and variant.duration_seconds > 60:
                    variant.duration_seconds = 60
                    variant.optimization_applied.append(ContentOptimization.PLATFORM_SPECIFIC)
            
            elif platform == DistributionPlatform.TIKTOK:
                # TikTok optimizations
                variant.resolution = "1080x1920"  # Vertical format
                variant.optimization_applied.append(ContentOptimization.MOBILE_OPTIMIZED)
                
                # TikTok preferred duration
                if variant.duration_seconds and variant.duration_seconds > 180:
                    variant.duration_seconds = 180
            
            elif platform == DistributionPlatform.YOUTUBE:
                # YouTube optimizations - keep high quality
                variant.optimization_applied.append(ContentOptimization.QUALITY_ADAPTIVE)
            
            return variant

        except Exception as e:
            self.logger.error(f"Variant creation failed: {e}")
            raise

    def _calculate_success_rate(self) -> float:
        """Calculate distribution success rate."""
        total = self.distribution_metrics["total_distributions"]
        if total == 0:
            return 0.0
        return self.distribution_metrics["successful_distributions"] / total
