"""
Distribution Services Module - Ainflue Platform
===============================================

Enterprise-grade multi-platform content distribution system for creators.
Handles automated publishing, format adaptation, platform optimization,
and cross-platform analytics aggregation.

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 3.0.0
License: Proprietary - All rights reserved
"""

from typing import Dict, List, Optional, Any, Union
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported distribution platforms"""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    DISCORD = "discord"
    PINTEREST = "pinterest"
    REDDIT = "reddit"

class ContentFormat(Enum):
    """Content format types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVESTREAM = "livestream"

class DistributionStatus(Enum):
    """Distribution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    REJECTED = "rejected"

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform: PlatformType
    api_endpoint: str
    max_file_size: int  # in bytes
    supported_formats: List[ContentFormat]
    requires_approval: bool
    scheduling_enabled: bool
    analytics_available: bool
    
@dataclass
class ContentMetadata:
    """Content metadata for distribution"""
    title: str
    description: str
    tags: List[str]
    category: str
    language: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    
@dataclass
class DistributionJob:
    """Distribution job definition"""
    job_id: str
    creator_id: str
    content_url: str
    content_format: ContentFormat
    target_platforms: List[PlatformType]
    metadata: ContentMetadata
    publish_time: Optional[datetime] = None
    status: DistributionStatus = DistributionStatus.PENDING
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class DistributionOrchestrator:
    """
    Main orchestrator for content distribution across platforms.
    
    Coordinates platform connectors, publication scheduling, format adaptation,
    analytics aggregation, and cross-platform synchronization.
    """
    
    def __init__(self):
        self.platform_configs = self._initialize_platform_configs()
        self.services = self._initialize_services()
        self.active_jobs = {}
    
    def _initialize_platform_configs(self) -> Dict[PlatformType, PlatformConfig]:
        """Initialize platform-specific configurations"""
        return {
            PlatformType.YOUTUBE: PlatformConfig(
                platform=PlatformType.YOUTUBE,
                api_endpoint="https://www.googleapis.com/youtube/v3",
                max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
                supported_formats=[ContentFormat.VIDEO, ContentFormat.LIVESTREAM],
                requires_approval=True,
                scheduling_enabled=True,
                analytics_available=True
            ),
            PlatformType.SPOTIFY: PlatformConfig(
                platform=PlatformType.SPOTIFY,
                api_endpoint="https://api.spotify.com/v1",
                max_file_size=200 * 1024 * 1024,  # 200MB
                supported_formats=[ContentFormat.AUDIO],
                requires_approval=True,
                scheduling_enabled=False,
                analytics_available=True
            ),
            PlatformType.INSTAGRAM: PlatformConfig(
                platform=PlatformType.INSTAGRAM,
                api_endpoint="https://graph.instagram.com",
                max_file_size=100 * 1024 * 1024,  # 100MB
                supported_formats=[ContentFormat.IMAGE, ContentFormat.VIDEO],
                requires_approval=False,
                scheduling_enabled=True,
                analytics_available=True
            ),
            PlatformType.TIKTOK: PlatformConfig(
                platform=PlatformType.TIKTOK,
                api_endpoint="https://open-api.tiktok.com",
                max_file_size=100 * 1024 * 1024,  # 100MB
                supported_formats=[ContentFormat.VIDEO],
                requires_approval=False,
                scheduling_enabled=True,
                analytics_available=True
            ),
            # Add more platforms as needed
        }
    
    def _initialize_services(self) -> Dict[str, str]:
        """Initialize distribution microservices"""
        return {
            'platform_connectors': 'http://platform-connectors:8100',
            'publication_scheduler': 'http://publication-scheduler:8101',
            'format_adapter': 'http://format-adapter:8102',
            'analytics_aggregator': 'http://analytics-aggregator:8103',
            'hashtag_optimizer': 'http://hashtag-optimizer:8104',
            'ab_testing_engine': 'http://ab-testing-engine:8105',
            'distribution_intelligence': 'http://distribution-intelligence:8106',
            'revenue_distribution': 'http://revenue-distribution:8107',
            'content_security': 'http://content-security:8108',
            'automation_orchestrator': 'http://automation-orchestrator:8109',
            'cross_platform_sync': 'http://cross-platform-sync:8110'
        }
    
    async def create_distribution_job(
        self, 
        creator_id: str, 
        content_url: str, 
        content_format: ContentFormat,
        target_platforms: List[PlatformType],
        metadata: ContentMetadata,
        publish_time: Optional[datetime] = None
    ) -> DistributionJob:
        """Create a new distribution job"""
        
        job_id = f"dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{creator_id}"
        
        job = DistributionJob(
            job_id=job_id,
            creator_id=creator_id,
            content_url=content_url,
            content_format=content_format,
            target_platforms=target_platforms,
            metadata=metadata,
            publish_time=publish_time
        )
        
        # Validate platforms support the content format
        validated_platforms = []
        for platform in target_platforms:
            if platform in self.platform_configs:
                config = self.platform_configs[platform]
                if content_format in config.supported_formats:
                    validated_platforms.append(platform)
                else:
                    logger.warning(f"Platform {platform.value} doesn't support {content_format.value}")
        
        job.target_platforms = validated_platforms
        self.active_jobs[job_id] = job
        
        logger.info(f"Created distribution job {job_id} for creator {creator_id}")
        return job
    
    async def process_distribution_job(self, job_id: str) -> Dict[str, Any]:
        """Process a distribution job"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        job.status = DistributionStatus.PROCESSING
        
        try:
            # Step 1: Format adaptation for each platform
            adapted_content = await self._adapt_content_formats(job)
            
            # Step 2: Optimize metadata for each platform
            optimized_metadata = await self._optimize_metadata(job)
            
            # Step 3: Security and compliance checks
            security_passed = await self._security_checks(job)
            if not security_passed:
                job.status = DistributionStatus.REJECTED
                return {"status": "rejected", "reason": "Security checks failed"}
            
            # Step 4: Schedule or publish immediately
            if job.publish_time and job.publish_time > datetime.now():
                await self._schedule_publication(job, adapted_content, optimized_metadata)
                job.status = DistributionStatus.SCHEDULED
            else:
                results = await self._publish_to_platforms(job, adapted_content, optimized_metadata)
                job.status = DistributionStatus.PUBLISHED
                return results
            
            return {
                "job_id": job_id,
                "status": job.status.value,
                "platforms": [p.value for p in job.target_platforms],
                "message": "Distribution job processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing distribution job {job_id}: {e}")
            job.status = DistributionStatus.FAILED
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _adapt_content_formats(self, job: DistributionJob) -> Dict[PlatformType, str]:
        """Adapt content format for each target platform"""
        adapted_content = {}
        
        for platform in job.target_platforms:
            try:
                # Call format adapter service
                async with aiohttp.ClientSession() as session:
                    adaptation_request = {
                        "source_url": job.content_url,
                        "source_format": job.content_format.value,
                        "target_platform": platform.value,
                        "quality_preset": "high"
                    }
                    
                    async with session.post(
                        f"{self.services['format_adapter']}/adapt",
                        json=adaptation_request
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            adapted_content[platform] = result["adapted_url"]
                        else:
                            logger.error(f"Format adaptation failed for {platform.value}")
                            adapted_content[platform] = job.content_url  # fallback
                            
            except Exception as e:
                logger.error(f"Error adapting content for {platform.value}: {e}")
                adapted_content[platform] = job.content_url  # fallback
        
        return adapted_content
    
    async def _optimize_metadata(self, job: DistributionJob) -> Dict[PlatformType, ContentMetadata]:
        """Optimize metadata for each platform"""
        optimized_metadata = {}
        
        for platform in job.target_platforms:
            try:
                # Call hashtag optimizer service
                async with aiohttp.ClientSession() as session:
                    optimization_request = {
                        "base_metadata": {
                            "title": job.metadata.title,
                            "description": job.metadata.description,
                            "tags": job.metadata.tags,
                            "category": job.metadata.category
                        },
                        "target_platform": platform.value,
                        "content_format": job.content_format.value
                    }
                    
                    async with session.post(
                        f"{self.services['hashtag_optimizer']}/optimize",
                        json=optimization_request
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            optimized_metadata[platform] = ContentMetadata(
                                title=result["optimized_title"],
                                description=result["optimized_description"],
                                tags=result["optimized_tags"],
                                category=job.metadata.category,
                                language=job.metadata.language,
                                thumbnail_url=job.metadata.thumbnail_url,
                                duration=job.metadata.duration
                            )
                        else:
                            optimized_metadata[platform] = job.metadata  # fallback
                            
            except Exception as e:
                logger.error(f"Error optimizing metadata for {platform.value}: {e}")
                optimized_metadata[platform] = job.metadata  # fallback
        
        return optimized_metadata
    
    async def _security_checks(self, job: DistributionJob) -> bool:
        """Perform security and compliance checks"""
        try:
            async with aiohttp.ClientSession() as session:
                security_request = {
                    "content_url": job.content_url,
                    "creator_id": job.creator_id,
                    "content_metadata": {
                        "title": job.metadata.title,
                        "description": job.metadata.description,
                        "tags": job.metadata.tags
                    }
                }
                
                async with session.post(
                    f"{self.services['content_security']}/scan",
                    json=security_request
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["security_passed"]
                    else:
                        logger.error("Security check service unavailable")
                        return False
                        
        except Exception as e:
            logger.error(f"Error during security checks: {e}")
            return False
    
    async def _schedule_publication(
        self, 
        job: DistributionJob, 
        adapted_content: Dict[PlatformType, str],
        optimized_metadata: Dict[PlatformType, ContentMetadata]
    ):
        """Schedule content publication"""
        try:
            async with aiohttp.ClientSession() as session:
                schedule_request = {
                    "job_id": job.job_id,
                    "creator_id": job.creator_id,
                    "publish_time": job.publish_time.isoformat(),
                    "platforms": {
                        platform.value: {
                            "content_url": adapted_content[platform],
                            "metadata": {
                                "title": optimized_metadata[platform].title,
                                "description": optimized_metadata[platform].description,
                                "tags": optimized_metadata[platform].tags
                            }
                        }
                        for platform in job.target_platforms
                    }
                }
                
                async with session.post(
                    f"{self.services['publication_scheduler']}/schedule",
                    json=schedule_request
                ) as response:
                    if response.status == 200:
                        logger.info(f"Scheduled publication for job {job.job_id}")
                    else:
                        logger.error(f"Failed to schedule publication for job {job.job_id}")
                        
        except Exception as e:
            logger.error(f"Error scheduling publication: {e}")
    
    async def _publish_to_platforms(
        self, 
        job: DistributionJob,
        adapted_content: Dict[PlatformType, str],
        optimized_metadata: Dict[PlatformType, ContentMetadata]
    ) -> Dict[str, Any]:
        """Publish content to all target platforms"""
        results = {}
        
        for platform in job.target_platforms:
            try:
                async with aiohttp.ClientSession() as session:
                    publish_request = {
                        "platform": platform.value,
                        "content_url": adapted_content[platform],
                        "metadata": {
                            "title": optimized_metadata[platform].title,
                            "description": optimized_metadata[platform].description,
                            "tags": optimized_metadata[platform].tags,
                            "category": optimized_metadata[platform].category
                        },
                        "creator_credentials": f"creator_{job.creator_id}_creds"
                    }
                    
                    async with session.post(
                        f"{self.services['platform_connectors']}/publish",
                        json=publish_request
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            results[platform.value] = {
                                "status": "success",
                                "platform_id": result.get("platform_id"),
                                "url": result.get("public_url")
                            }
                        else:
                            results[platform.value] = {
                                "status": "failed",
                                "error": f"HTTP {response.status}"
                            }
                            
            except Exception as e:
                results[platform.value] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a distribution job"""
        if job_id not in self.active_jobs:
            return {"error": "Job not found"}
        
        job = self.active_jobs[job_id]
        return {
            "job_id": job_id,
            "status": job.status.value,
            "creator_id": job.creator_id,
            "target_platforms": [p.value for p in job.target_platforms],
            "created_at": job.created_at.isoformat(),
            "publish_time": job.publish_time.isoformat() if job.publish_time else None
        }
    
    async def get_analytics(self, creator_id: str, timeframe: str = "week") -> Dict[str, Any]:
        """Get aggregated analytics across platforms"""
        try:
            async with aiohttp.ClientSession() as session:
                analytics_request = {
                    "creator_id": creator_id,
                    "timeframe": timeframe,
                    "platforms": [p.value for p in PlatformType]
                }
                
                async with session.post(
                    f"{self.services['analytics_aggregator']}/aggregate",
                    json=analytics_request
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": "Analytics service unavailable"}
                        
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}

# Initialize the orchestrator
distribution_orchestrator = DistributionOrchestrator()

async def health_check() -> Dict[str, str]:
    """Health check endpoint for distribution services"""
    return {
        "status": "healthy",
        "module": "distribution",
        "version": "3.0.0",
        "services_count": len(distribution_orchestrator.services),
        "supported_platforms": len(distribution_orchestrator.platform_configs),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Example usage
    async def main():
        # Create a test distribution job
        metadata = ContentMetadata(
            title="Test Music Track",
            description="Amazing electronic music",
            tags=["electronic", "music", "test"],
            category="music",
            language="en"
        )
        
        job = await distribution_orchestrator.create_distribution_job(
            creator_id="test_creator_123",
            content_url="https://example.com/test-track.mp3",
            content_format=ContentFormat.AUDIO,
            target_platforms=[PlatformType.SPOTIFY, PlatformType.SOUNDCLOUD],
            metadata=metadata
        )
        
        print(f"Created distribution job: {job.job_id}")
        
        # Process the job
        result = await distribution_orchestrator.process_distribution_job(job.job_id)
        print(f"Processing result: {result}")
    
    asyncio.run(main())