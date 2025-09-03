"""Cross-Posting Automation - Auto cross-posting
==============================================

Automated cross-posting system for simultaneous content distribution
across multiple platforms with platform-specific optimizations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from enum import Enum
import copy

logger = logging.getLogger(__name__)


class CrossPostingStrategy(str, Enum):
    """Cross-posting strategies."""
    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    STAGGERED = "staggered"
    OPTIMAL_TIMING = "optimal_timing"


class PostingStatus(str, Enum):
    """Cross-posting status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


@dataclass
class PlatformContent:
    """Platform-specific content configuration."""
    platform: str
    title: str
    content: str
    media_urls: List[str]
    hashtags: List[str]
    platform_specific_settings: Dict[str, Any]
    scheduled_time: Optional[datetime] = None


@dataclass
class CrossPostingJob:
    """Cross-posting job data structure."""
    job_id: str
    content_id: str
    original_content: Dict[str, Any]
    platform_contents: Dict[str, PlatformContent]
    strategy: CrossPostingStrategy
    status: PostingStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    results: Dict[str, Dict[str, Any]]
    errors: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class CrossPostingResult:
    """Result of cross-posting operation."""
    job_id: str
    total_platforms: int
    successful_platforms: List[str]
    failed_platforms: List[str]
    partial_platforms: List[str]
    execution_time_seconds: float
    platform_results: Dict[str, Any]


class CrossPostingEngine:
    """Advanced cross-posting automation engine."""
    
    def __init__(self):
        """Initialize cross-posting engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.active_jobs: Dict[str, CrossPostingJob] = {}
        self.completed_jobs: Dict[str, CrossPostingJob] = {}
        
        # Platform-specific configurations
        self.platform_configs = self._initialize_platform_configs()
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific configurations."""
        return {
            "youtube": {
                "max_title_length": 100,
                "max_description_length": 5000,
                "hashtag_prefix": "",
                "optimal_timing_offset": timedelta(hours=0),
                "content_type": "video"
            },
            "instagram": {
                "max_title_length": 2200,
                "max_description_length": 2200,
                "hashtag_prefix": "#",
                "optimal_timing_offset": timedelta(minutes=5),
                "content_type": "image_video"
            },
            "tiktok": {
                "max_title_length": 150,
                "max_description_length": 2200,
                "hashtag_prefix": "#",
                "optimal_timing_offset": timedelta(minutes=10),
                "content_type": "video"
            },
            "spotify": {
                "max_title_length": 100,
                "max_description_length": 1000,
                "hashtag_prefix": "",
                "optimal_timing_offset": timedelta(minutes=15),
                "content_type": "audio"
            },
            "soundcloud": {
                "max_title_length": 100,
                "max_description_length": 2000,
                "hashtag_prefix": "#",
                "optimal_timing_offset": timedelta(minutes=20),
                "content_type": "audio"
            }
        }
    
    async def create_cross_posting_job(
        self,
        content_id: str,
        platforms: List[str],
        content_data: Dict[str, Any],
        strategy: CrossPostingStrategy = CrossPostingStrategy.OPTIMAL_TIMING,
        base_scheduled_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CrossPostingJob:
        """Create a new cross-posting job.
        
        Args:
            content_id: Unique content identifier
            platforms: List of target platforms
            content_data: Base content data
            strategy: Cross-posting strategy
            base_scheduled_time: Base time for scheduling
            metadata: Additional metadata
            
        Returns:
            CrossPostingJob object
        """
        try:
            job_id = f"crosspost_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate platform-specific content
            platform_contents = {}
            for platform in platforms:
                platform_content = await self._adapt_content_for_platform(
                    platform, content_data, base_scheduled_time, strategy
                )
                platform_contents[platform] = platform_content
            
            job = CrossPostingJob(
                job_id=job_id,
                content_id=content_id,
                original_content=content_data,
                platform_contents=platform_contents,
                strategy=strategy,
                status=PostingStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                started_at=None,
                completed_at=None,
                results={},
                errors={},
                metadata=metadata or {}
            )
            
            self.active_jobs[job_id] = job
            
            self.logger.info(f"Cross-posting job created: {job_id} for platforms: {platforms}")
            return job
            
        except Exception as e:
            self.logger.error(f"Failed to create cross-posting job: {str(e)}")
            raise
    
    async def _adapt_content_for_platform(
        self,
        platform: str,
        content_data: Dict[str, Any],
        base_time: Optional[datetime],
        strategy: CrossPostingStrategy
    ) -> PlatformContent:
        """Adapt content for specific platform requirements.
        
        Args:
            platform: Target platform
            content_data: Original content data
            base_time: Base scheduling time
            strategy: Cross-posting strategy
            
        Returns:
            PlatformContent adapted for the platform
        """
        config = self.platform_configs.get(platform, {})
        
        # Adapt title
        title = content_data.get("title", "")
        max_title_length = config.get("max_title_length", 100)
        if len(title) > max_title_length:
            title = title[:max_title_length-3] + "..."
        
        # Adapt content/description
        content = content_data.get("description", content_data.get("content", ""))
        max_content_length = config.get("max_description_length", 1000)
        if len(content) > max_content_length:
            content = content[:max_content_length-3] + "..."
        
        # Adapt hashtags
        hashtags = content_data.get("hashtags", [])
        hashtag_prefix = config.get("hashtag_prefix", "#")
        if hashtag_prefix and not hashtags[0].startswith(hashtag_prefix) if hashtags else False:
            hashtags = [f"{hashtag_prefix}{tag}" if not tag.startswith(hashtag_prefix) else tag for tag in hashtags]
        
        # Calculate scheduled time based on strategy
        scheduled_time = None
        if base_time:
            offset = config.get("optimal_timing_offset", timedelta(0))
            if strategy == CrossPostingStrategy.SIMULTANEOUS:
                scheduled_time = base_time
            elif strategy == CrossPostingStrategy.STAGGERED:
                scheduled_time = base_time + offset
            elif strategy == CrossPostingStrategy.OPTIMAL_TIMING:
                # Use platform-specific optimal timing
                scheduled_time = await self._calculate_optimal_time(platform, base_time)
            else:
                scheduled_time = base_time
        
        # Platform-specific settings
        platform_settings = {
            "content_type": config.get("content_type", "general"),
            "privacy_level": content_data.get("privacy", "public"),
            "allow_comments": content_data.get("allow_comments", True),
            "monetization": content_data.get("monetization", False)
        }
        
        # Add platform-specific tweaks
        if platform.lower() == "youtube":
            platform_settings.update({
                "category_id": content_data.get("category_id", "22"),
                "language": content_data.get("language", "en")
            })
        elif platform.lower() == "instagram":
            platform_settings.update({
                "location_id": content_data.get("location_id"),
                "alt_text": content_data.get("alt_text")
            })
        elif platform.lower() == "tiktok":
            platform_settings.update({
                "allow_duet": content_data.get("allow_duet", True),
                "allow_stitch": content_data.get("allow_stitch", True)
            })
        
        return PlatformContent(
            platform=platform,
            title=title,
            content=content,
            media_urls=content_data.get("media_urls", []),
            hashtags=hashtags,
            platform_specific_settings=platform_settings,
            scheduled_time=scheduled_time
        )
    
    async def _calculate_optimal_time(
        self,
        platform: str,
        base_time: datetime
    ) -> datetime:
        """Calculate optimal posting time for platform.
        
        Args:
            platform: Target platform
            base_time: Base time reference
            
        Returns:
            Optimal posting time
        """
        # Simulate optimal time calculation
        await asyncio.sleep(0.01)
        
        # Platform-specific optimal hour adjustments
        optimal_adjustments = {
            "youtube": timedelta(hours=2),    # 2 hours after base
            "instagram": timedelta(hours=1),  # 1 hour after base
            "tiktok": timedelta(minutes=30),  # 30 minutes after base
            "spotify": timedelta(hours=3),    # 3 hours after base
            "soundcloud": timedelta(hours=4)  # 4 hours after base
        }
        
        adjustment = optimal_adjustments.get(platform.lower(), timedelta(0))
        return base_time + adjustment
    
    async def execute_cross_posting_job(self, job_id: str) -> CrossPostingResult:
        """Execute a cross-posting job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            CrossPostingResult with execution details
        """
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        start_time = datetime.now(timezone.utc)
        
        try:
            job.status = PostingStatus.IN_PROGRESS
            job.started_at = start_time
            
            self.logger.info(f"Starting cross-posting job: {job_id}")
            
            successful_platforms = []
            failed_platforms = []
            partial_platforms = []
            
            # Execute based on strategy
            if job.strategy == CrossPostingStrategy.SIMULTANEOUS:
                results = await self._execute_simultaneous_posting(job)
            elif job.strategy == CrossPostingStrategy.SEQUENTIAL:
                results = await self._execute_sequential_posting(job)
            elif job.strategy == CrossPostingStrategy.STAGGERED:
                results = await self._execute_staggered_posting(job)
            else:  # OPTIMAL_TIMING
                results = await self._execute_optimal_timing_posting(job)
            
            # Process results
            for platform, result in results.items():
                if result.get("success", False):
                    successful_platforms.append(platform)
                elif result.get("partial", False):
                    partial_platforms.append(platform)
                else:
                    failed_platforms.append(platform)
                    job.errors[platform] = result.get("error", "Unknown error")
            
            # Update job status
            if failed_platforms and not successful_platforms:
                job.status = PostingStatus.FAILED
            elif failed_platforms or partial_platforms:
                job.status = PostingStatus.PARTIAL_SUCCESS
            else:
                job.status = PostingStatus.COMPLETED
            
            job.completed_at = datetime.now(timezone.utc)
            job.results = results
            
            # Move to completed jobs
            self.completed_jobs[job_id] = job
            del self.active_jobs[job_id]
            
            execution_time = (job.completed_at - start_time).total_seconds()
            
            result = CrossPostingResult(
                job_id=job_id,
                total_platforms=len(job.platform_contents),
                successful_platforms=successful_platforms,
                failed_platforms=failed_platforms,
                partial_platforms=partial_platforms,
                execution_time_seconds=execution_time,
                platform_results=results
            )
            
            self.logger.info(f"Cross-posting job completed: {job_id} - "
                           f"Success: {len(successful_platforms)}, "
                           f"Failed: {len(failed_platforms)}")
            
            return result
            
        except Exception as e:
            job.status = PostingStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.errors["system"] = str(e)
            
            self.logger.error(f"Cross-posting job failed: {job_id} - {str(e)}")
            raise
    
    async def _execute_simultaneous_posting(self, job: CrossPostingJob) -> Dict[str, Any]:
        """Execute simultaneous posting to all platforms."""
        tasks = []
        
        for platform, content in job.platform_contents.items():
            task = self._post_to_platform(platform, content)
            tasks.append((platform, task))
        
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in tasks], 
            return_exceptions=True
        )
        
        for (platform, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                results[platform] = {"success": False, "error": str(result)}
            else:
                results[platform] = result
        
        return results
    
    async def _execute_sequential_posting(self, job: CrossPostingJob) -> Dict[str, Any]:
        """Execute sequential posting to platforms."""
        results = {}
        
        for platform, content in job.platform_contents.items():
            try:
                result = await self._post_to_platform(platform, content)
                results[platform] = result
                
                # Add delay between posts
                await asyncio.sleep(1)
                
            except Exception as e:
                results[platform] = {"success": False, "error": str(e)}
        
        return results
    
    async def _execute_staggered_posting(self, job: CrossPostingJob) -> Dict[str, Any]:
        """Execute staggered posting with time delays."""
        results = {}
        delay_increment = 30  # 30 seconds between each platform
        
        for i, (platform, content) in enumerate(job.platform_contents.items()):
            if i > 0:
                await asyncio.sleep(delay_increment)
            
            try:
                result = await self._post_to_platform(platform, content)
                results[platform] = result
                
            except Exception as e:
                results[platform] = {"success": False, "error": str(e)}
        
        return results
    
    async def _execute_optimal_timing_posting(self, job: CrossPostingJob) -> Dict[str, Any]:
        """Execute posting at platform-optimal times."""
        # For now, simulate immediate posting with optimal content
        # In real implementation, this would schedule posts for optimal times
        return await self._execute_simultaneous_posting(job)
    
    async def _post_to_platform(self, platform: str, content: PlatformContent) -> Dict[str, Any]:
        """Post content to a specific platform.
        
        Args:
            platform: Target platform
            content: Platform-specific content
            
        Returns:
            Posting result dictionary
        """
        try:
            # Simulate posting process
            await asyncio.sleep(0.2)
            
            post_id = f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "success": True,
                "platform": platform,
                "post_id": post_id,
                "url": f"https://{platform}.com/post/{post_id}",
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "title": content.title,
                "content_length": len(content.content),
                "media_count": len(content.media_urls),
                "hashtags_count": len(content.hashtags)
            }
            
        except Exception as e:
            return {
                "success": False,
                "platform": platform,
                "error": str(e),
                "attempted_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a cross-posting job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        job = None
        
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
        elif job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
        
        if not job:
            return {"error": "Job not found"}
        
        return {
            "job_id": job.job_id,
            "content_id": job.content_id,
            "status": job.status.value,
            "platforms": list(job.platform_contents.keys()),
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "strategy": job.strategy.value,
            "results_count": len(job.results),
            "errors_count": len(job.errors)
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel an active cross-posting job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if successful
        """
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = PostingStatus.FAILED
            job.errors["system"] = "Job cancelled by user"
            job.completed_at = datetime.now(timezone.utc)
            
            # Move to completed jobs
            self.completed_jobs[job_id] = job
            del self.active_jobs[job_id]
            
            self.logger.info(f"Cross-posting job cancelled: {job_id}")
            return True
        
        return False


# Global cross-posting engine instance
_cross_posting_engine: Optional[CrossPostingEngine] = None


def get_cross_posting_engine() -> CrossPostingEngine:
    """Get global cross-posting engine instance."""
    global _cross_posting_engine
    
    if _cross_posting_engine is None:
        _cross_posting_engine = CrossPostingEngine()
    
    return _cross_posting_engine


# Convenience functions
async def create_cross_post(
    content_id: str,
    platforms: List[str],
    content_data: Dict[str, Any],
    strategy: CrossPostingStrategy = CrossPostingStrategy.OPTIMAL_TIMING
) -> CrossPostingJob:
    """Convenience function to create cross-posting job."""
    engine = get_cross_posting_engine()
    return await engine.create_cross_posting_job(
        content_id=content_id,
        platforms=platforms,
        content_data=content_data,
        strategy=strategy
    )


async def execute_cross_post(job_id: str) -> CrossPostingResult:
    """Convenience function to execute cross-posting job."""
    engine = get_cross_posting_engine()
    return await engine.execute_cross_posting_job(job_id)