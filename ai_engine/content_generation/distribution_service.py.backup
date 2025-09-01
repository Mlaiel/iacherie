"""Distribution Service - Content distribution and publishing service

Professional service for distributing and publishing content across
multiple platforms with advanced scheduling and optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
from concurrent.futures import ThreadPoolExecutor
import schedule

from .content_models import (
    Platform, ContentType, ContentFormat,
    PerformanceMetrics, ContentError
)


class PublishingStatus(str, Enum):
    """Publishing status enumeration"""
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRAFT = "draft"


@dataclass
class PlatformConfig:
    """Platform configuration for publishing"""
    platform: Platform
    api_endpoint: str
    auth_type: str
    credentials: Dict[str, Any]
    rate_limits: Dict[str, int]
    content_limits: Dict[str, Any]
    optimal_times: List[str]
    supported_formats: List[ContentFormat]


@dataclass
class PublishingTask:
    """Publishing task definition"""
    task_id: str
    content_id: str
    platform: Platform
    content: str
    scheduled_time: datetime
    status: PublishingStatus
    metadata: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class DistributionService:
    """
    Professional content distribution service for multi-platform publishing
    
    Features:
    - Multi-platform publishing with API integrations
    - Advanced scheduling with optimal timing
    - Cross-platform optimization and formatting
    - Real-time monitoring and analytics
    - Automated retry and error handling
    - Batch publishing capabilities
    - Performance tracking and optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Platform configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Publishing queue and tracking
        self.publishing_queue: List[PublishingTask] = []
        self.active_tasks: Dict[str, PublishingTask] = {}
        self.completed_tasks: Dict[str, PublishingTask] = {}
        
        # Performance tracking
        self.metrics_cache: Dict[str, PerformanceMetrics] = {}
        
        # Scheduling
        self.scheduler_running = False
        
        self.logger.info("DistributionService initialized successfully")
    
    def _initialize_platform_configs(self) -> Dict[Platform, PlatformConfig]:
        """Initialize platform configurations"""
        configs = {}
        
        # Instagram configuration
        configs[Platform.INSTAGRAM] = PlatformConfig(
            platform=Platform.INSTAGRAM,
            api_endpoint="https://graph.instagram.com/v18.0",
            auth_type="oauth2",
            credentials={},
            rate_limits={"posts_per_hour": 25, "requests_per_hour": 200},
            content_limits={
                "max_caption_length": 2200,
                "max_hashtags": 30,
                "image_formats": ["jpg", "png"],
                "video_formats": ["mp4", "mov"]
            },
            optimal_times=["09:00", "12:00", "15:00", "18:00", "21:00"],
            supported_formats=[ContentFormat.TEXT, ContentFormat.HTML]
        )
        
        # Twitter configuration
        configs[Platform.TWITTER] = PlatformConfig(
            platform=Platform.TWITTER,
            api_endpoint="https://api.twitter.com/2",
            auth_type="oauth2",
            credentials={},
            rate_limits={"tweets_per_hour": 300, "requests_per_hour": 500},
            content_limits={
                "max_tweet_length": 280,
                "max_thread_tweets": 25,
                "image_formats": ["jpg", "png", "gif", "webp"],
                "video_formats": ["mp4", "mov"]
            },
            optimal_times=["08:00", "12:00", "17:00", "19:00"],
            supported_formats=[ContentFormat.TEXT, ContentFormat.MARKDOWN]
        )
        
        # LinkedIn configuration
        configs[Platform.LINKEDIN] = PlatformConfig(
            platform=Platform.LINKEDIN,
            api_endpoint="https://api.linkedin.com/v2",
            auth_type="oauth2",
            credentials={},
            rate_limits={"posts_per_hour": 20, "requests_per_hour": 100},
            content_limits={
                "max_post_length": 3000,
                "max_hashtags": 20,
                "image_formats": ["jpg", "png"],
                "video_formats": ["mp4", "mov"]
            },
            optimal_times=["07:00", "08:00", "12:00", "17:00", "18:00"],
            supported_formats=[ContentFormat.TEXT, ContentFormat.HTML]
        )
        
        # TikTok configuration
        configs[Platform.TIKTOK] = PlatformConfig(
            platform=Platform.TIKTOK,
            api_endpoint="https://open-api.tiktok.com/platform/v1",
            auth_type="oauth2",
            credentials={},
            rate_limits={"posts_per_hour": 10, "requests_per_hour": 50},
            content_limits={
                "max_caption_length": 150,
                "max_hashtags": 20,
                "video_formats": ["mp4", "mov"],
                "min_duration": 15,
                "max_duration": 180
            },
            optimal_times=["18:00", "19:00", "20:00", "21:00"],
            supported_formats=[ContentFormat.TEXT]
        )
        
        # YouTube configuration
        configs[Platform.YOUTUBE] = PlatformConfig(
            platform=Platform.YOUTUBE,
            api_endpoint="https://www.googleapis.com/youtube/v3",
            auth_type="oauth2",
            credentials={},
            rate_limits={"uploads_per_day": 6, "requests_per_hour": 100},
            content_limits={
                "max_title_length": 100,
                "max_description_length": 5000,
                "max_tags": 500,
                "video_formats": ["mp4", "mov", "avi", "wmv", "flv", "webm"]
            },
            optimal_times=["14:00", "15:00", "16:00", "20:00", "21:00"],
            supported_formats=[ContentFormat.TEXT, ContentFormat.HTML]
        )
        
        return configs
    
    async def schedule_publication(
        self,
        content_id: str,
        content: str,
        platforms: List[Platform],
        scheduled_time: Optional[datetime] = None,
        auto_optimize: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Schedule content publication across multiple platforms
        
        Args:
            content_id: Unique content identifier
            content: Content to publish
            platforms: Target platforms
            scheduled_time: When to publish (None for immediate)
            auto_optimize: Apply platform-specific optimizations
            metadata: Additional publication metadata
            
        Returns:
            Dictionary of platform -> task_id mappings
        """
        try:
            task_ids = {}
            
            if scheduled_time is None:
                scheduled_time = datetime.now()
            
            if metadata is None:
                metadata = {}
            
            for platform in platforms:
                # Optimize content for platform
                if auto_optimize:
                    optimized_content = await self._optimize_for_platform(content, platform)
                else:
                    optimized_content = content
                
                # Validate content for platform
                validation_result = await self._validate_content_for_platform(
                    optimized_content, platform
                )
                
                if not validation_result["valid"]:
                    self.logger.warning(
                        f"Content validation failed for {platform}: {validation_result['errors']}"
                    )
                    continue
                
                # Create publishing task
                task_id = f"{content_id}_{platform}_{int(scheduled_time.timestamp())}"
                
                # Adjust timing for platform optimal times
                optimal_time = self._get_optimal_publishing_time(platform, scheduled_time)
                
                task = PublishingTask(
                    task_id=task_id,
                    content_id=content_id,
                    platform=platform,
                    content=optimized_content,
                    scheduled_time=optimal_time,
                    status=PublishingStatus.SCHEDULED,
                    metadata={**metadata, "validation": validation_result}
                )
                
                # Add to queue
                self.publishing_queue.append(task)
                task_ids[platform.value] = task_id
                
                self.logger.info(f"Scheduled publication: {task_id} for {platform} at {optimal_time}")
            
            # Start scheduler if not running
            if not self.scheduler_running:
                asyncio.create_task(self._run_scheduler())
            
            return task_ids
            
        except Exception as e:
            self.logger.error(f"Error scheduling publication: {str(e)}")
            raise
    
    async def publish_immediately(
        self,
        content_id: str,
        content: str,
        platforms: List[Platform],
        auto_optimize: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Publish content immediately across platforms
        
        Args:
            content_id: Unique content identifier
            content: Content to publish
            platforms: Target platforms
            auto_optimize: Apply platform-specific optimizations
            metadata: Additional publication metadata
            
        Returns:
            Dictionary of platform -> publication result
        """
        try:
            results = {}
            
            # Create immediate publishing tasks
            tasks = []
            for platform in platforms:
                task = asyncio.create_task(
                    self._publish_to_platform(content_id, content, platform, auto_optimize, metadata)
                )
                tasks.append((platform, task))
            
            # Execute all publishing tasks concurrently
            for platform, task in tasks:
                try:
                    result = await task
                    results[platform.value] = result
                except Exception as e:
                    results[platform.value] = {
                        "success": False,
                        "error": str(e),
                        "platform": platform.value
                    }
                    self.logger.error(f"Failed to publish to {platform}: {str(e)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in immediate publication: {str(e)}")
            raise
    
    async def _publish_to_platform(
        self,
        content_id: str,
        content: str,
        platform: Platform,
        auto_optimize: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Publish content to a specific platform"""
        try:
            # Optimize content for platform
            if auto_optimize:
                optimized_content = await self._optimize_for_platform(content, platform)
            else:
                optimized_content = content
            
            # Validate content
            validation_result = await self._validate_content_for_platform(optimized_content, platform)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Validation failed: {validation_result['errors']}",
                    "platform": platform.value
                }
            
            # Get platform config
            config = self.platform_configs.get(platform)
            if not config:
                return {
                    "success": False,
                    "error": f"Platform {platform} not configured",
                    "platform": platform.value
                }
            
            # Publish using platform API
            publication_result = await self._call_platform_api(
                platform, optimized_content, metadata or {}
            )
            
            if publication_result["success"]:
                # Track successful publication
                await self._track_publication(content_id, platform, publication_result)
                
                return {
                    "success": True,
                    "platform": platform.value,
                    "post_id": publication_result.get("post_id"),
                    "url": publication_result.get("url"),
                    "published_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": publication_result.get("error", "Unknown error"),
                    "platform": platform.value
                }
                
        except Exception as e:
            self.logger.error(f"Error publishing to {platform}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform.value
            }
    
    async def _optimize_for_platform(self, content: str, platform: Platform) -> str:
        """Optimize content for specific platform"""
        config = self.platform_configs.get(platform)
        if not config:
            return content
        
        optimized_content = content
        
        # Platform-specific optimizations
        if platform == Platform.TWITTER:
            # Twitter optimizations
            max_length = config.content_limits["max_tweet_length"]
            if len(optimized_content) > max_length:
                # Create thread or truncate
                optimized_content = optimized_content[:max_length-3] + "..."
        
        elif platform == Platform.INSTAGRAM:
            # Instagram optimizations
            max_length = config.content_limits["max_caption_length"]
            if len(optimized_content) > max_length:
                optimized_content = optimized_content[:max_length-3] + "..."
            
            # Add Instagram-specific formatting
            optimized_content = self._add_instagram_formatting(optimized_content)
        
        elif platform == Platform.LINKEDIN:
            # LinkedIn optimizations
            max_length = config.content_limits["max_post_length"]
            if len(optimized_content) > max_length:
                optimized_content = optimized_content[:max_length-3] + "..."
            
            # Add professional formatting
            optimized_content = self._add_linkedin_formatting(optimized_content)
        
        elif platform == Platform.TIKTOK:
            # TikTok optimizations
            max_length = config.content_limits["max_caption_length"]
            if len(optimized_content) > max_length:
                optimized_content = optimized_content[:max_length-3] + "..."
        
        return optimized_content
    
    def _add_instagram_formatting(self, content: str) -> str:
        """Add Instagram-specific formatting"""
        # Add line breaks for better readability
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                formatted_paragraphs.append(paragraph.strip())
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _add_linkedin_formatting(self, content: str) -> str:
        """Add LinkedIn-specific formatting"""
        # Professional formatting with proper spacing
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                formatted_lines.append(line.strip())
            else:
                formatted_lines.append('')
        
        return '\n'.join(formatted_lines)
    
    async def _validate_content_for_platform(
        self, content: str, platform: Platform
    ) -> Dict[str, Any]:
        """Validate content for platform requirements"""
        config = self.platform_configs.get(platform)
        if not config:
            return {"valid": False, "errors": [f"Platform {platform} not configured"]}
        
        errors = []
        warnings = []
        
        # Check content length
        limits = config.content_limits
        
        if platform == Platform.TWITTER:
            if len(content) > limits["max_tweet_length"]:
                errors.append(f"Content exceeds Twitter limit of {limits['max_tweet_length']} characters")
        
        elif platform == Platform.INSTAGRAM:
            if len(content) > limits["max_caption_length"]:
                errors.append(f"Content exceeds Instagram limit of {limits['max_caption_length']} characters")
        
        elif platform == Platform.LINKEDIN:
            if len(content) > limits["max_post_length"]:
                errors.append(f"Content exceeds LinkedIn limit of {limits['max_post_length']} characters")
        
        elif platform == Platform.TIKTOK:
            if len(content) > limits["max_caption_length"]:
                errors.append(f"Content exceeds TikTok limit of {limits['max_caption_length']} characters")
        
        # Check hashtag count
        hashtag_count = content.count('#')
        max_hashtags = limits.get("max_hashtags", 30)
        
        if hashtag_count > max_hashtags:
            errors.append(f"Too many hashtags: {hashtag_count} (max: {max_hashtags})")
        
        # Content quality checks
        if len(content.strip()) == 0:
            errors.append("Content is empty")
        
        if len(content.strip()) < 10:
            warnings.append("Content is very short")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "character_count": len(content),
            "hashtag_count": hashtag_count
        }
    
    def _get_optimal_publishing_time(
        self, platform: Platform, requested_time: datetime
    ) -> datetime:
        """Get optimal publishing time for platform"""
        config = self.platform_configs.get(platform)
        if not config or not config.optimal_times:
            return requested_time
        
        # If requesting immediate publication, use next optimal time
        now = datetime.now()
        if requested_time <= now + timedelta(minutes=5):
            # Find next optimal time today
            for time_str in config.optimal_times:
                hour, minute = map(int, time_str.split(':'))
                optimal_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                if optimal_time > now:
                    return optimal_time
            
            # Use first optimal time tomorrow
            tomorrow = now + timedelta(days=1)
            hour, minute = map(int, config.optimal_times[0].split(':'))
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return requested_time
    
    async def _call_platform_api(
        self, platform: Platform, content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call platform API to publish content"""
        # This is a mock implementation
        # In production, implement actual API calls for each platform
        
        config = self.platform_configs.get(platform)
        if not config:
            return {"success": False, "error": "Platform not configured"}
        
        try:
            # Simulate API call delay
            await asyncio.sleep(1)
            
            # Mock successful publication
            post_id = f"{platform.value}_{int(datetime.now().timestamp())}"
            url = f"https://{platform.value}.com/post/{post_id}"
            
            return {
                "success": True,
                "post_id": post_id,
                "url": url,
                "platform": platform.value,
                "published_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _track_publication(
        self, content_id: str, platform: Platform, result: Dict[str, Any]
    ) -> None:
        """Track successful publication for analytics"""
        try:
            # Store publication metrics
            metrics = PerformanceMetrics(
                content_id=content_id,
                platform=platform,
                content_type=ContentType.SOCIAL_POST,  # Default, should be passed in
                created_at=datetime.now()
            )
            
            self.metrics_cache[f"{content_id}_{platform.value}"] = metrics
            
            self.logger.info(f"Tracked publication: {content_id} on {platform}")
            
        except Exception as e:
            self.logger.error(f"Error tracking publication: {str(e)}")
    
    async def _run_scheduler(self) -> None:
        """Run the publication scheduler"""
        self.scheduler_running = True
        
        try:
            while self.scheduler_running:
                current_time = datetime.now()
                
                # Process scheduled tasks
                due_tasks = [
                    task for task in self.publishing_queue
                    if task.scheduled_time <= current_time and task.status == PublishingStatus.SCHEDULED
                ]
                
                for task in due_tasks:
                    # Move to active tasks
                    self.publishing_queue.remove(task)
                    self.active_tasks[task.task_id] = task
                    task.status = PublishingStatus.PUBLISHING
                    
                    # Execute publication
                    asyncio.create_task(self._execute_scheduled_task(task))
                
                # Sleep for 30 seconds before next check
                await asyncio.sleep(30)
                
        except Exception as e:
            self.logger.error(f"Error in scheduler: {str(e)}")
        finally:
            self.scheduler_running = False
    
    async def _execute_scheduled_task(self, task: PublishingTask) -> None:
        """Execute a scheduled publishing task"""
        try:
            result = await self._publish_to_platform(
                task.content_id,
                task.content,
                task.platform,
                auto_optimize=True,
                metadata=task.metadata
            )
            
            if result["success"]:
                task.status = PublishingStatus.PUBLISHED
                task.published_at = datetime.now()
                self.logger.info(f"Successfully published task: {task.task_id}")
            else:
                task.status = PublishingStatus.FAILED
                task.error_message = result.get("error", "Unknown error")
                
                # Retry logic
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = PublishingStatus.SCHEDULED
                    task.scheduled_time = datetime.now() + timedelta(minutes=5 * task.retry_count)
                    self.publishing_queue.append(task)
                    self.logger.info(f"Scheduled retry for task: {task.task_id}")
                else:
                    self.logger.error(f"Task failed after max retries: {task.task_id}")
            
            # Move to completed tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
            
        except Exception as e:
            task.status = PublishingStatus.FAILED
            task.error_message = str(e)
            self.logger.error(f"Error executing task {task.task_id}: {str(e)}")
    
    async def get_publication_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a publication task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
        # Check completed tasks
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
        # Check scheduled tasks
        else:
            task = None
            for scheduled_task in self.publishing_queue:
                if scheduled_task.task_id == task_id:
                    task = scheduled_task
                    break
        
        if not task:
            return {"error": "Task not found"}
        
        return {
            "task_id": task.task_id,
            "content_id": task.content_id,
            "platform": task.platform.value,
            "status": task.status.value,
            "scheduled_time": task.scheduled_time.isoformat(),
            "published_at": task.published_at.isoformat() if task.published_at else None,
            "retry_count": task.retry_count,
            "error_message": task.error_message
        }
    
    async def cancel_publication(self, task_id: str) -> bool:
        """Cancel a scheduled publication"""
        # Find and remove from queue
        for task in self.publishing_queue:
            if task.task_id == task_id:
                task.status = PublishingStatus.CANCELLED
                self.publishing_queue.remove(task)
                self.completed_tasks[task_id] = task
                self.logger.info(f"Cancelled task: {task_id}")
                return True
        
        return False
    
    async def get_platform_analytics(self, platform: Platform) -> Dict[str, Any]:
        """Get analytics for a specific platform"""
        platform_metrics = [
            metrics for metrics in self.metrics_cache.values()
            if metrics.platform == platform
        ]
        
        if not platform_metrics:
            return {"platform": platform.value, "total_posts": 0}
        
        total_posts = len(platform_metrics)
        total_engagement = sum(
            metrics.likes + metrics.shares + metrics.comments
            for metrics in platform_metrics
        )
        
        return {
            "platform": platform.value,
            "total_posts": total_posts,
            "total_engagement": total_engagement,
            "average_engagement": total_engagement / total_posts if total_posts > 0 else 0,
            "last_updated": datetime.now().isoformat()
        }
    
    async def batch_publish(
        self,
        content_items: List[Dict[str, Any]],
        platforms: List[Platform],
        auto_schedule: bool = True
    ) -> Dict[str, Any]:
        """Publish multiple content items across platforms"""
        try:
            batch_id = f"batch_{int(datetime.now().timestamp())}"
            results = {"batch_id": batch_id, "results": []}
            
            for item in content_items:
                content_id = item["content_id"]
                content = item["content"]
                metadata = item.get("metadata", {})
                
                if auto_schedule:
                    # Schedule with optimal timing
                    task_ids = await self.schedule_publication(
                        content_id, content, platforms, metadata=metadata
                    )
                    results["results"].append({
                        "content_id": content_id,
                        "task_ids": task_ids,
                        "status": "scheduled"
                    })
                else:
                    # Publish immediately
                    publish_results = await self.publish_immediately(
                        content_id, content, platforms, metadata=metadata
                    )
                    results["results"].append({
                        "content_id": content_id,
                        "publish_results": publish_results,
                        "status": "published"
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in batch publish: {str(e)}")
            raise
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            "scheduled_tasks": len(self.publishing_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "scheduler_running": self.scheduler_running,
            "queue_items": [
                {
                    "task_id": task.task_id,
                    "platform": task.platform.value,
                    "scheduled_time": task.scheduled_time.isoformat(),
                    "status": task.status.value
                }
                for task in self.publishing_queue
            ]
        }
