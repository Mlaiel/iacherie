"""Distribution Services Interface
Main entry point for Ainflue Platform distribution infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Platform(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"

class ContentType(Enum):
    VIDEO = "video"
    AUDIO = "audio" 
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

@dataclass
class DistributionJob:
    """Distribution job configuration"""
    content_id: str
    platforms: List[Platform]
    content_type: ContentType
    scheduled_time: Optional[datetime] = None
    format_requirements: Optional[Dict[Platform, Dict]] = None
    metadata: Optional[Dict] = None
    ab_test_variants: Optional[List[Dict]] = None

class DistributionOrchestrator:
    """Main orchestrator for content distribution across platforms"""
    
    def __init__(self):
        self.active_jobs: Dict[str, DistributionJob] = {}
        self.platform_connectors = {}
        self.scheduler = None
        self.format_adapter = None
        self.analytics_aggregator = None
    
    async def initialize(self):
        """Initialize all distribution services"""
        logger.info("Initializing Distribution Orchestrator...")
        
        # Initialize platform connectors
        await self._initialize_platform_connectors()
        
        # Initialize scheduler
        await self._initialize_scheduler()
        
        # Initialize format adapter
        await self._initialize_format_adapter()
        
        # Initialize analytics aggregator
        await self._initialize_analytics_aggregator()
        
        logger.info("Distribution Orchestrator initialized successfully")
    
    async def _initialize_platform_connectors(self):
        """Initialize connections to all supported platforms"""
        from .platform_connectors import (
            YoutubeConnector, InstagramConnector, TiktokConnector,
            SpotifyConnector, SoundcloudConnector, FacebookConnector,
            TwitterConnector, LinkedinConnector, PinterestConnector
        )
        
        self.platform_connectors = {
            Platform.YOUTUBE: YoutubeConnector(),
            Platform.INSTAGRAM: InstagramConnector(),
            Platform.TIKTOK: TiktokConnector(),
            Platform.SPOTIFY: SpotifyConnector(),
            Platform.SOUNDCLOUD: SoundcloudConnector(),
            Platform.FACEBOOK: FacebookConnector(),
            Platform.TWITTER: TwitterConnector(),
            Platform.LINKEDIN: LinkedinConnector(),
            Platform.PINTEREST: PinterestConnector(),
        }
        
        # Initialize each connector
        for platform, connector in self.platform_connectors.items():
            try:
                await connector.initialize()
                logger.info(f"✅ {platform.value} connector initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {platform.value}: {e}")
    
    async def _initialize_scheduler(self):
        """Initialize publication scheduler"""
        from .publication_scheduler import PublicationScheduler
        self.scheduler = PublicationScheduler()
        await self.scheduler.initialize()
        logger.info("✅ Publication scheduler initialized")
    
    async def _initialize_format_adapter(self):
        """Initialize format adapter"""
        from .format_adapter import FormatAdapter
        self.format_adapter = FormatAdapter()
        await self.format_adapter.initialize()
        logger.info("✅ Format adapter initialized")
    
    async def _initialize_analytics_aggregator(self):
        """Initialize analytics aggregator"""
        from .analytics_aggregator import AnalyticsAggregator
        self.analytics_aggregator = AnalyticsAggregator()
        await self.analytics_aggregator.initialize()
        logger.info("✅ Analytics aggregator initialized")
    
    async def submit_distribution_job(self, job: DistributionJob) -> str:
        """Submit a new distribution job"""
        job_id = f"dist_{job.content_id}_{int(datetime.now().timestamp())}"
        
        # Store job
        self.active_jobs[job_id] = job
        
        # Schedule or execute immediately
        if job.scheduled_time:
            await self.scheduler.schedule_job(job_id, job, job.scheduled_time)
            logger.info(f"📅 Job {job_id} scheduled for {job.scheduled_time}")
        else:
            await self._execute_distribution_job(job_id, job)
            logger.info(f"🚀 Job {job_id} executed immediately")
        
        return job_id
    
    async def _execute_distribution_job(self, job_id: str, job: DistributionJob):
        """Execute a distribution job"""
        logger.info(f"🎯 Executing distribution job {job_id}")
        
        try:
            # Adapt formats for each platform
            adapted_content = await self.format_adapter.adapt_for_platforms(
                job.content_id, job.platforms, job.content_type
            )
            
            # Distribute to each platform
            results = {}
            for platform in job.platforms:
                try:
                    connector = self.platform_connectors[platform]
                    platform_content = adapted_content[platform]
                    
                    result = await connector.publish_content(
                        platform_content, 
                        job.metadata or {}
                    )
                    
                    results[platform] = {"status": "success", "result": result}
                    logger.info(f"✅ Published to {platform.value}")
                    
                except Exception as e:
                    results[platform] = {"status": "error", "error": str(e)}
                    logger.error(f"❌ Failed to publish to {platform.value}: {e}")
            
            # Update analytics
            await self.analytics_aggregator.record_distribution(job_id, results)
            
            # Clean up job
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            logger.info(f"✅ Distribution job {job_id} completed")
            
        except Exception as e:
            logger.error(f"❌ Distribution job {job_id} failed: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a distribution job"""
        if job_id in self.active_jobs:
            return {"status": "pending", "job": self.active_jobs[job_id]}
        
        # Check with analytics for completed jobs
        return await self.analytics_aggregator.get_job_status(job_id)
    
    async def get_platform_analytics(self, platform: Platform, 
                                   start_date: datetime, 
                                   end_date: datetime) -> Dict:
        """Get analytics for a specific platform"""
        return await self.analytics_aggregator.get_platform_analytics(
            platform, start_date, end_date
        )
    
    async def get_cross_platform_analytics(self, 
                                         start_date: datetime,
                                         end_date: datetime) -> Dict:
        """Get aggregated cross-platform analytics"""
        return await self.analytics_aggregator.get_cross_platform_analytics(
            start_date, end_date
        )
    
    async def shutdown(self):
        """Gracefully shutdown all services"""
        logger.info("Shutting down Distribution Orchestrator...")
        
        # Shutdown all connectors
        for platform, connector in self.platform_connectors.items():
            try:
                await connector.shutdown()
                logger.info(f"✅ {platform.value} connector shutdown")
            except Exception as e:
                logger.error(f"❌ Error shutting down {platform.value}: {e}")
        
        # Shutdown other services
        if self.scheduler:
            await self.scheduler.shutdown()
        if self.format_adapter:
            await self.format_adapter.shutdown()
        if self.analytics_aggregator:
            await self.analytics_aggregator.shutdown()
        
        logger.info("✅ Distribution Orchestrator shutdown complete")

# Global orchestrator instance
distribution_orchestrator = DistributionOrchestrator()

async def initialize_distribution_services():
    """Initialize distribution services"""
    await distribution_orchestrator.initialize()

async def shutdown_distribution_services():
    """Shutdown distribution services"""
    await distribution_orchestrator.shutdown()

__all__ = [
    'Platform', 'ContentType', 'DistributionJob', 'DistributionOrchestrator',
    'distribution_orchestrator', 'initialize_distribution_services',
    'shutdown_distribution_services'
]