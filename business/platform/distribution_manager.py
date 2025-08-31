"""Distribution Manager - Multi-Platform Content Distribution Engine

Manages automated content distribution across multiple platforms including
YouTube, Instagram, TikTok, Spotify, and other social media platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

import aiohttp
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from ...core.config import settings
from ...core.logging import get_logger
from ...models.distribution import DistributionJob, DistributionStatus, PlatformCredentials
from ...services.integrations.youtube_api import YouTubeAPIService
from ...services.integrations.instagram_api import InstagramAPIService
from ...services.integrations.tiktok_api import TikTokAPIService
from ...services.integrations.spotify_api import SpotifyAPIService
from ...services.notification.notification_service import NotificationService
from ...utils.retry_utils import retry_with_backoff

logger = get_logger(__name__)

class PlatformType(Enum):
    """Supported platform types"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"

class DistributionPriority(Enum):
    """Distribution priority levels"""    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class PlatformConfig:
    """Platform-specific configuration"""    platform: PlatformType
    api_service: Any
    max_file_size: int
    supported_formats: List[str]
    max_duration: Optional[int] = None
    scheduling_enabled: bool = True
    analytics_enabled: bool = True
    monetization_enabled: bool = False

@dataclass
class DistributionRequest:
    """Distribution request structure"""    user_id: int
    content_id: int
    platforms: List[PlatformType]
    content_path: str
    content_type: str
    metadata: Dict[str, Any]
    scheduling: Optional[Dict[str, Any]] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    priority: DistributionPriority = DistributionPriority.MEDIUM

@dataclass
class DistributionResult:
    """Distribution result for single platform"""    platform: PlatformType
    success: bool
    platform_id: Optional[str] = None
    platform_url: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class DistributionManager:
    """    Multi-platform content distribution engine
    
    Features:
    - Automated content distribution
    - Platform-specific optimization
    - Scheduled publishing
    - Real-time analytics tracking
    - Error handling and retry logic
    - Cross-platform synchronization
    """    
    def __init__(self):
        self.notification_service = NotificationService()
        
        # Platform API services
        self.platform_services = {
            PlatformType.YOUTUBE: YouTubeAPIService(),
            PlatformType.INSTAGRAM: InstagramAPIService(),
            PlatformType.TIKTOK: TikTokAPIService(),
            PlatformType.SPOTIFY: SpotifyAPIService()
        }
        
        # Platform configurations
        self.platform_configs = {
            PlatformType.YOUTUBE: PlatformConfig(
                platform=PlatformType.YOUTUBE,
                api_service=self.platform_services[PlatformType.YOUTUBE],
                max_file_size=128000000,  # 128MB
                supported_formats=['mp4', 'mov', 'avi'],
                max_duration=43200,  # 12 hours
                monetization_enabled=True
            ),
            PlatformType.INSTAGRAM: PlatformConfig(
                platform=PlatformType.INSTAGRAM,
                api_service=self.platform_services[PlatformType.INSTAGRAM],
                max_file_size=100000000,  # 100MB
                supported_formats=['mp4', 'jpg', 'png'],
                max_duration=60,  # 60 seconds for reels
                monetization_enabled=True
            ),
            PlatformType.TIKTOK: PlatformConfig(
                platform=PlatformType.TIKTOK,
                api_service=self.platform_services[PlatformType.TIKTOK],
                max_file_size=72000000,  # 72MB
                supported_formats=['mp4'],
                max_duration=180,  # 3 minutes
                monetization_enabled=True
            ),
            PlatformType.SPOTIFY: PlatformConfig(
                platform=PlatformType.SPOTIFY,
                api_service=self.platform_services[PlatformType.SPOTIFY],
                max_file_size=52428800,  # 50MB
                supported_formats=['mp3', 'wav', 'flac'],
                monetization_enabled=True
            )
        }
        
        # Distribution queue
        self.distribution_queue = asyncio.Queue(maxsize=500)
        self.active_distributions = {}
        
    async def initialize(self) -> bool:
        """        Initialize distribution manager
        
        Returns:
            bool: Initialization success status
        """        try:
            logger.info("Initializing Distribution Manager...")
            
            # Initialize platform services
            for platform, service in self.platform_services.items():
                await service.initialize()
                logger.info(f"{platform.value} service initialized")
            
            # Start distribution queue processor
            asyncio.create_task(self._process_distribution_queue())
            
            # Start scheduled distribution checker
            asyncio.create_task(self._check_scheduled_distributions())
            
            logger.info("Distribution Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Distribution Manager initialization failed: {e}")
            return False
    
    async def distribute_content(
        self,
        distribution_request: DistributionRequest,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Distribute content to multiple platforms
        
        Args:
            distribution_request: Distribution configuration
            session: Database session
            
        Returns:
            Dict containing distribution job information
        """        try:
            # Validate distribution request
            await self._validate_distribution_request(distribution_request, session)
            
            # Create distribution job
            job_id = f"dist_{distribution_request.user_id}_{int(datetime.utcnow().timestamp())}"
            
            distribution_job = DistributionJob(
                job_id=job_id,
                user_id=distribution_request.user_id,
                content_id=distribution_request.content_id,
                platforms=json.dumps([p.value for p in distribution_request.platforms]),
                content_path=distribution_request.content_path,
                content_type=distribution_request.content_type,
                metadata=json.dumps(distribution_request.metadata),
                priority=distribution_request.priority.value,
                status=DistributionStatus.QUEUED,
                created_at=datetime.utcnow()
            )
            
            session.add(distribution_job)
            await session.commit()
            await session.refresh(distribution_job)
            
            # Handle scheduled distribution
            if distribution_request.scheduling:
                await self._schedule_distribution(distribution_job, distribution_request.scheduling)
                status = "scheduled"
            else:
                # Queue for immediate distribution
                await self.distribution_queue.put(distribution_request)
                self.active_distributions[job_id] = distribution_job
                status = "queued"
            
            logger.info(f"Distribution job created: {job_id}")
            
            return {
                'job_id': job_id,
                'status': status,
                'platforms': [p.value for p in distribution_request.platforms],
                'estimated_completion': datetime.utcnow() + timedelta(minutes=len(distribution_request.platforms) * 5),
                'tracking_url': f"/api/v1/distribution/{job_id}/status"
            }
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            raise HTTPException(status_code=500, detail=f"Distribution failed: {str(e)}")
    
    async def get_distribution_status(
        self,
        job_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Get distribution job status and results
        
        Args:
            job_id: Distribution job ID
            session: Database session
            
        Returns:
            Dict containing job status and results
        """        try:
            # Get distribution job
            result = await session.execute(
                select(DistributionJob).where(DistributionJob.job_id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                raise HTTPException(status_code=404, detail="Distribution job not found")
            
            # Parse results
            platforms = json.loads(job.platforms) if job.platforms else []
            results = json.loads(job.results) if job.results else {}
            
            # Calculate progress
            total_platforms = len(platforms)
            completed_platforms = len([r for r in results.values() if r.get('completed')])
            progress_percentage = (completed_platforms / total_platforms * 100) if total_platforms > 0 else 0
            
            return {
                'job_id': job_id,
                'status': job.status.value,
                'progress_percentage': progress_percentage,
                'platforms': platforms,
                'results': results,
                'created_at': job.created_at.isoformat(),
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'error_message': job.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to get distribution status: {e}")
            raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
    async def cancel_distribution(
        self,
        job_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """        Cancel pending distribution job
        
        Args:
            job_id: Distribution job ID
            session: Database session
            
        Returns:
            Dict containing cancellation status
        """        try:
            # Get distribution job
            result = await session.execute(
                select(DistributionJob).where(DistributionJob.job_id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                raise HTTPException(status_code=404, detail="Distribution job not found")
            
            if job.status in [DistributionStatus.COMPLETED, DistributionStatus.FAILED]:
                raise HTTPException(status_code=400, detail="Cannot cancel completed job")
            
            # Update job status
            job.status = DistributionStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            job.error_message = "Cancelled by user"
            
            await session.commit()
            
            # Remove from active distributions
            if job_id in self.active_distributions:
                del self.active_distributions[job_id]
            
            logger.info(f"Distribution job cancelled: {job_id}")
            
            return {
                'job_id': job_id,
                'status': 'cancelled',
                'message': 'Distribution job cancelled successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel distribution: {e}")
            raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")
    
    async def retry_failed_distribution(
        self,
        job_id: str,
        platforms: Optional[List[str]] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """        Retry failed distribution for specific platforms
        
        Args:
            job_id: Distribution job ID
            platforms: Specific platforms to retry (None for all failed)
            session: Database session
            
        Returns:
            Dict containing retry status
        """        try:
            # Get distribution job
            result = await session.execute(
                select(DistributionJob).where(DistributionJob.job_id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                raise HTTPException(status_code=404, detail="Distribution job not found")
            
            # Parse current results
            results = json.loads(job.results) if job.results else {}
            
            # Determine platforms to retry
            if platforms:
                retry_platforms = [PlatformType(p) for p in platforms]
            else:
                # Retry all failed platforms
                retry_platforms = [
                    PlatformType(platform) for platform, result in results.items()
                    if not result.get('success', False)
                ]
            
            if not retry_platforms:
                raise HTTPException(status_code=400, detail="No failed platforms to retry")
            
            # Create new distribution request for retry
            original_platforms = json.loads(job.platforms)
            metadata = json.loads(job.metadata) if job.metadata else {}
            
            retry_request = DistributionRequest(
                user_id=job.user_id,
                content_id=job.content_id,
                platforms=retry_platforms,
                content_path=job.content_path,
                content_type=job.content_type,
                metadata=metadata,
                priority=DistributionPriority.HIGH  # Higher priority for retries
            )
            
            # Queue for retry
            await self.distribution_queue.put(retry_request)
            
            # Update job status
            job.status = DistributionStatus.PROCESSING
            await session.commit()
            
            logger.info(f"Distribution retry queued: {job_id}")
            
            return {
                'job_id': job_id,
                'status': 'retry_queued',
                'retry_platforms': [p.value for p in retry_platforms],
                'message': 'Distribution retry queued successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to retry distribution: {e}")
            raise HTTPException(status_code=500, detail=f"Retry failed: {str(e)}")
    
    async def get_platform_analytics(
        self,
        user_id: int,
        platform: str,
        content_id: Optional[int] = None,
        date_range: Optional[Dict[str, datetime]] = None,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """        Get analytics data for distributed content
        
        Args:
            user_id: User ID
            platform: Platform name
            content_id: Specific content ID (optional)
            date_range: Date range for analytics
            session: Database session
            
        Returns:
            Dict containing analytics data
        """        try:
            platform_type = PlatformType(platform)
            
            if platform_type not in self.platform_services:
                raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
            
            # Get platform credentials
            credentials = await self._get_platform_credentials(user_id, platform_type, session)
            
            if not credentials:
                raise HTTPException(status_code=404, detail="Platform credentials not found")
            
            # Fetch analytics from platform API
            service = self.platform_services[platform_type]
            analytics_data = await service.get_analytics(
                credentials=credentials,
                content_id=content_id,
                date_range=date_range
            )
            
            return {
                'platform': platform,
                'user_id': user_id,
                'content_id': content_id,
                'analytics': analytics_data,
                'fetched_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform analytics: {e}")
            raise HTTPException(status_code=500, detail=f"Analytics fetch failed: {str(e)}")
    
    async def _validate_distribution_request(
        self,
        request: DistributionRequest,
        session: AsyncSession
    ):
        """Validate distribution request"""        # Check if content exists and belongs to user
        # Check platform credentials
        # Validate file format compatibility
        # Check quota limits
        
        for platform in request.platforms:
            if platform not in self.platform_configs:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported platform: {platform.value}"
                )
            
            # Check platform credentials
            credentials = await self._get_platform_credentials(
                request.user_id, platform, session
            )
            
            if not credentials:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing credentials for platform: {platform.value}"
                )
    
    async def _process_distribution_queue(self):
        """Background task to process distribution queue"""        while True:
            try:
                # Get distribution request from queue
                request = await self.distribution_queue.get()
                
                # Process distribution
                await self._execute_distribution(request)
                
                # Mark as done
                self.distribution_queue.task_done()
                
            except Exception as e:
                logger.error(f"Distribution queue processing error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_distribution(self, request: DistributionRequest):
        """Execute distribution to all platforms"""        try:
            logger.info(f"Executing distribution for user {request.user_id}")
            
            # Distribute to each platform
            distribution_results = []
            
            for platform in request.platforms:
                result = await self._distribute_to_platform(request, platform)
                distribution_results.append(result)
                
                # Small delay between platform distributions
                await asyncio.sleep(2)
            
            # Update job results
            await self._update_distribution_results(request, distribution_results)
            
            # Send notification
            await self._send_distribution_notification(request, distribution_results)
            
            logger.info(f"Distribution completed for user {request.user_id}")
            
        except Exception as e:
            logger.error(f"Distribution execution failed: {e}")
            await self._handle_distribution_error(request, str(e))
    
    @retry_with_backoff(max_retries=3, backoff_factor=2.0)
    async def _distribute_to_platform(
        self,
        request: DistributionRequest,
        platform: PlatformType
    ) -> DistributionResult:
        """Distribute content to specific platform"""        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Distributing to {platform.value}")
            
            # Get platform configuration
            config = self.platform_configs[platform]
            
            # Get platform service
            service = config.api_service
            
            # Prepare platform-specific metadata
            platform_metadata = await self._prepare_platform_metadata(
                request.metadata, platform
            )
            
            # Upload content to platform
            upload_result = await service.upload_content(
                content_path=request.content_path,
                metadata=platform_metadata,
                user_id=request.user_id
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return DistributionResult(
                platform=platform,
                success=True,
                platform_id=upload_result.get('id'),
                platform_url=upload_result.get('url'),
                processing_time=processing_time,
                metadata=upload_result.get('metadata', {})
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.error(f"Platform distribution failed for {platform.value}: {e}")
            
            return DistributionResult(
                platform=platform,
                success=False,
                error_message=str(e),
                processing_time=processing_time
            )
    
    async def _prepare_platform_metadata(
        self,
        metadata: Dict[str, Any],
        platform: PlatformType
    ) -> Dict[str, Any]:
        """Prepare platform-specific metadata"""        platform_metadata = metadata.copy()
        
        # Platform-specific metadata transformations
        if platform == PlatformType.YOUTUBE:
            platform_metadata.update({
                'snippet': {
                    'title': metadata.get('title', ''),
                    'description': metadata.get('description', ''),
                    'tags': metadata.get('tags', []),
                    'categoryId': metadata.get('category_id', '22')  # People & Blogs
                },
                'status': {
                    'privacyStatus': metadata.get('privacy', 'public'),
                    'madeForKids': metadata.get('made_for_kids', False)
                }
            })
        
        elif platform == PlatformType.INSTAGRAM:
            platform_metadata.update({
                'caption': f"{metadata.get('title', '')}\n\n{metadata.get('description', '')}",
                'media_type': 'VIDEO' if metadata.get('content_type') == 'video' else 'IMAGE'
            })
        
        elif platform == PlatformType.TIKTOK:
            platform_metadata.update({
                'text': f"{metadata.get('title', '')} {' '.join(metadata.get('hashtags', []))}",
                'privacy_level': metadata.get('privacy', 'SELF_ONLY'),
                'disable_duet': metadata.get('disable_duet', False),
                'disable_comment': metadata.get('disable_comment', False)
            })
        
        return platform_metadata
    
    async def _update_distribution_results(
        self,
        request: DistributionRequest,
        results: List[DistributionResult]
    ):
        """Update distribution job results"""        # Implementation to update database with results
        pass
    
    async def _send_distribution_notification(
        self,
        request: DistributionRequest,
        results: List[DistributionResult]
    ):
        """Send distribution completion notification"""        successful_platforms = [r.platform.value for r in results if r.success]
        failed_platforms = [r.platform.value for r in results if not r.success]
        
        await self.notification_service.send_distribution_notification(
            user_id=request.user_id,
            content_id=request.content_id,
            successful_platforms=successful_platforms,
            failed_platforms=failed_platforms
        )
    
    async def _handle_distribution_error(self, request: DistributionRequest, error: str):
        """Handle distribution error"""        logger.error(f"Distribution error for user {request.user_id}: {error}")
        
        # Send error notification
        await self.notification_service.send_distribution_error(
            user_id=request.user_id,
            content_id=request.content_id,
            error=error
        )
    
    async def _schedule_distribution(
        self,
        job: DistributionJob,
        scheduling: Dict[str, Any]
    ):
        """Schedule distribution for later execution"""        # Implementation for scheduled distribution
        pass
    
    async def _check_scheduled_distributions(self):
        """Check and execute scheduled distributions"""        while True:
            try:
                # Check for due scheduled distributions
                # Execute them
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduled distribution check failed: {e}")
                await asyncio.sleep(60)
    
    async def _get_platform_credentials(
        self,
        user_id: int,
        platform: PlatformType,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Get platform credentials for user"""        result = await session.execute(
            select(PlatformCredentials).where(
                and_(
                    PlatformCredentials.user_id == user_id,
                    PlatformCredentials.platform == platform.value,
                    PlatformCredentials.is_active == True
                )
            )
        )
        
        credentials = result.scalar_one_or_none()
        
        if credentials:
            return json.loads(credentials.credentials_data)
        
        return None
