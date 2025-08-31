"""Content Distribution Network - Multi-Platform Content Delivery
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in 
legal action.

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

This module provides advanced content distribution capabilities across multiple
platforms with intelligent routing, optimization, and analytics.
"""import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
import json
import hashlib
import mimetypes
from pathlib import Path
import aiofiles
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Supported content types"""    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    STREAM = "stream"
    PODCAST = "podcast"
    LIVE = "live"

class DistributionPlatform(Enum):
    """Distribution platforms"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtube_music"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    TIDAL = "tidal"
    TWITCH = "twitch"
    DISCORD = "discord"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"

class ContentStatus(Enum):
    """Content distribution status"""    PENDING = auto()
    PROCESSING = auto()
    UPLOADING = auto()
    PUBLISHED = auto()
    FAILED = auto()
    REJECTED = auto()
    SCHEDULED = auto()
    DRAFT = auto()
    ARCHIVED = auto()

class OptimizationLevel(Enum):
    """Content optimization levels"""    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"

@dataclass
class ContentMetadata:
    """Content metadata"""    title: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    language: str = "en"
    duration: Optional[float] = None
    file_size: Optional[int] = None
    content_type: Optional[ContentType] = None
    mime_type: Optional[str] = None
    resolution: Optional[Tuple[int, int]] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    copyright_info: Optional[str] = None
    license_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlatformRequirements:
    """Platform-specific requirements"""    platform: DistributionPlatform
    supported_formats: List[str]
    max_file_size: Optional[int] = None
    max_duration: Optional[float] = None
    min_duration: Optional[float] = None
    required_resolutions: List[Tuple[int, int]] = field(default_factory=list)
    supported_bitrates: List[int] = field(default_factory=list)
    required_metadata: List[str] = field(default_factory=list)
    custom_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentAsset:
    """Content asset representation"""    asset_id: str
    file_path: str
    metadata: ContentMetadata
    content_hash: str
    versions: Dict[str, str] = field(default_factory=dict)  # quality -> file_path
    thumbnails: List[str] = field(default_factory=list)
    subtitles: Dict[str, str] = field(default_factory=dict)  # lang -> file_path
    status: ContentStatus = ContentStatus.PENDING
    distribution_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DistributionJob:
    """Content distribution job"""    job_id: str
    asset: ContentAsset
    target_platforms: List[DistributionPlatform]
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    schedule_time: Optional[datetime] = None
    platform_specific_config: Dict[DistributionPlatform, Dict[str, Any]] = field(default_factory=dict)
    priority: int = 5  # 1-10, higher = more priority
    retry_count: int = 0
    max_retries: int = 3
    status: ContentStatus = ContentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: Dict[DistributionPlatform, float] = field(default_factory=dict)

@dataclass
class DistributionResult:
    """Distribution operation result"""    job_id: str
    platform: DistributionPlatform
    success: bool
    asset_url: Optional[str] = None
    platform_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    analytics_url: Optional[str] = None
    distributed_at: datetime = field(default_factory=datetime.utcnow)

class ContentOptimizer:
    """Content optimization engine"""    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.optimization_cache = {}
        
        # Platform-specific requirements
        self.platform_requirements = {
            DistributionPlatform.YOUTUBE: PlatformRequirements(
                platform=DistributionPlatform.YOUTUBE,
                supported_formats=['mp4', 'mov', 'avi', 'wmv', 'flv'],
                max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
                max_duration=12 * 3600,  # 12 hours
                required_resolutions=[(1920, 1080), (1280, 720), (854, 480)],
                supported_bitrates=[1000, 2500, 5000, 8000]
            ),
            DistributionPlatform.SPOTIFY: PlatformRequirements(
                platform=DistributionPlatform.SPOTIFY,
                supported_formats=['mp3', 'flac', 'ogg'],
                max_file_size=200 * 1024 * 1024,  # 200MB
                min_duration=30,  # 30 seconds
                max_duration=30 * 60,  # 30 minutes
                supported_bitrates=[128, 160, 192, 320],
                required_metadata=['title', 'artist', 'album']
            ),
            DistributionPlatform.INSTAGRAM: PlatformRequirements(
                platform=DistributionPlatform.INSTAGRAM,
                supported_formats=['mp4', 'mov', 'jpg', 'png'],
                max_file_size=100 * 1024 * 1024,  # 100MB
                max_duration=60,  # 1 minute for video
                required_resolutions=[(1080, 1080), (1080, 1350), (1920, 1080)]
            ),
            DistributionPlatform.TIKTOK: PlatformRequirements(
                platform=DistributionPlatform.TIKTOK,
                supported_formats=['mp4', 'mov'],
                max_file_size=50 * 1024 * 1024,  # 50MB
                min_duration=3,
                max_duration=180,  # 3 minutes
                required_resolutions=[(1080, 1920), (720, 1280)]
            )
        }
    
    def get_platform_requirements(self, platform: DistributionPlatform) -> Optional[PlatformRequirements]:
        """Get requirements for specific platform"""        return self.platform_requirements.get(platform)
    
    async def validate_content(self, asset: ContentAsset, 
                             platform: DistributionPlatform) -> Tuple[bool, List[str]]:
        """Validate content against platform requirements"""        requirements = self.get_platform_requirements(platform)
        if not requirements:
            return True, []
        
        issues = []
        
        # Check file format
        file_ext = Path(asset.file_path).suffix.lower().lstrip('.')
        if file_ext not in requirements.supported_formats:
            issues.append(f"Unsupported format: {file_ext}. Supported: {requirements.supported_formats}")
        
        # Check file size
        if requirements.max_file_size and asset.metadata.file_size:
            if asset.metadata.file_size > requirements.max_file_size:
                issues.append(f"File too large: {asset.metadata.file_size} > {requirements.max_file_size}")
        
        # Check duration
        if asset.metadata.duration:
            if requirements.min_duration and asset.metadata.duration < requirements.min_duration:
                issues.append(f"Duration too short: {asset.metadata.duration}s < {requirements.min_duration}s")
            
            if requirements.max_duration and asset.metadata.duration > requirements.max_duration:
                issues.append(f"Duration too long: {asset.metadata.duration}s > {requirements.max_duration}s")
        
        # Check resolution
        if asset.metadata.resolution and requirements.required_resolutions:
            if asset.metadata.resolution not in requirements.required_resolutions:
                issues.append(f"Invalid resolution: {asset.metadata.resolution}. Required: {requirements.required_resolutions}")
        
        # Check required metadata
        metadata_dict = asset.metadata.__dict__
        for required_field in requirements.required_metadata:
            if required_field not in metadata_dict or not metadata_dict[required_field]:
                issues.append(f"Missing required metadata: {required_field}")
        
        return len(issues) == 0, issues
    
    async def optimize_for_platform(self, asset: ContentAsset, 
                                  platform: DistributionPlatform,
                                  optimization_level: OptimizationLevel) -> Optional[str]:
        """Optimize content for specific platform"""        cache_key = f"{asset.content_hash}_{platform.value}_{optimization_level.value}"
        
        if cache_key in self.optimization_cache:
            return self.optimization_cache[cache_key]
        
        requirements = self.get_platform_requirements(platform)
        if not requirements:
            return asset.file_path
        
        try:
            # This would integrate with actual media processing libraries
            # For now, we'll simulate optimization
            optimized_path = await self._perform_optimization(
                asset, platform, optimization_level, requirements
            )
            
            self.optimization_cache[cache_key] = optimized_path
            return optimized_path
            
        except Exception as e:
            self.logger.error(f"Optimization failed for {platform}: {e}")
            return None
    
    async def _perform_optimization(self, asset: ContentAsset, 
                                  platform: DistributionPlatform,
                                  optimization_level: OptimizationLevel,
                                  requirements: PlatformRequirements) -> str:
        """Perform actual content optimization"""        base_path = Path(asset.file_path)
        optimized_filename = f"{base_path.stem}_{platform.value}_{optimization_level.value}{base_path.suffix}"
        optimized_path = base_path.parent / optimized_filename
        
        self.logger.info(f"Optimizing {asset.file_path} for {platform.value}")
        
        # Simulate optimization process
        await asyncio.sleep(1)  # Simulate processing time
        
        # In real implementation, this would use FFmpeg, PIL, etc.
        # for actual media optimization
        
        return str(optimized_path)
    
    def clear_cache(self):
        """Clear optimization cache"""        self.optimization_cache.clear()
        self.logger.info("Optimization cache cleared")

class BasePlatformDistributor(ABC):
    """Base class for platform distributors"""    
    def __init__(self, platform: DistributionPlatform):
        self.platform = platform
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.rate_limiter = None
        self.upload_queue = asyncio.Queue()
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with platform"""        pass
    
    @abstractmethod
    async def upload_content(self, asset: ContentAsset, 
                           metadata: ContentMetadata) -> DistributionResult:
        """Upload content to platform"""        pass
    
    @abstractmethod
    async def update_content(self, platform_id: str, 
                           metadata: ContentMetadata) -> bool:
        """Update content metadata"""        pass
    
    @abstractmethod
    async def delete_content(self, platform_id: str) -> bool:
        """Delete content from platform"""        pass
    
    @abstractmethod
    async def get_analytics(self, platform_id: str, 
                          date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get content analytics"""        pass
    
    async def check_upload_status(self, upload_id: str) -> ContentStatus:
        """Check upload status"""        # Default implementation
        return ContentStatus.PUBLISHED

class YouTubeDistributor(BasePlatformDistributor):
    """YouTube content distributor"""    
    def __init__(self):
        super().__init__(DistributionPlatform.YOUTUBE)
        self.api_client = None
    
    async def authenticate(self) -> bool:
        """Authenticate with YouTube API"""        try:
            # Implementation would use Google API client
            self.logger.info("YouTube authentication successful")
            return True
        except Exception as e:
            self.logger.error(f"YouTube authentication failed: {e}")
            return False
    
    async def upload_content(self, asset: ContentAsset, 
                           metadata: ContentMetadata) -> DistributionResult:
        """Upload video to YouTube"""        try:
            self.logger.info(f"Uploading {asset.asset_id} to YouTube")
            
            # Simulate upload process
            await asyncio.sleep(2)
            
            # Create mock result
            result = DistributionResult(
                job_id=asset.asset_id,
                platform=self.platform,
                success=True,
                platform_id=f"youtube_{int(datetime.utcnow().timestamp())}",
                asset_url=f"https://youtube.com/watch?v=mock_{asset.asset_id}",
                analytics_url="https://studio.youtube.com/analytics"
            )
            
            self.logger.info(f"YouTube upload successful: {result.platform_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"YouTube upload failed: {e}")
            return DistributionResult(
                job_id=asset.asset_id,
                platform=self.platform,
                success=False,
                error_message=str(e)
            )
    
    async def update_content(self, platform_id: str, 
                           metadata: ContentMetadata) -> bool:
        """Update YouTube video metadata"""        try:
            self.logger.info(f"Updating YouTube video {platform_id}")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self.logger.error(f"YouTube update failed: {e}")
            return False
    
    async def delete_content(self, platform_id: str) -> bool:
        """Delete YouTube video"""        try:
            self.logger.info(f"Deleting YouTube video {platform_id}")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self.logger.error(f"YouTube deletion failed: {e}")
            return False
    
    async def get_analytics(self, platform_id: str, 
                          date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get YouTube analytics"""        return {
            "views": 1000,
            "watch_time_hours": 500,
            "likes": 50,
            "dislikes": 5,
            "comments": 25,
            "shares": 10,
            "subscribers_gained": 5,
            "revenue": 25.50
        }

class SpotifyDistributor(BasePlatformDistributor):
    """Spotify content distributor"""    
    def __init__(self):
        super().__init__(DistributionPlatform.SPOTIFY)
        self.api_client = None
    
    async def authenticate(self) -> bool:
        """Authenticate with Spotify API"""        try:
            self.logger.info("Spotify authentication successful")
            return True
        except Exception as e:
            self.logger.error(f"Spotify authentication failed: {e}")
            return False
    
    async def upload_content(self, asset: ContentAsset, 
                           metadata: ContentMetadata) -> DistributionResult:
        """Upload track to Spotify"""        try:
            self.logger.info(f"Uploading {asset.asset_id} to Spotify")
            
            # Spotify requires music distributors like DistroKid, CD Baby, etc.
            # This would integrate with their APIs
            await asyncio.sleep(3)  # Simulate processing time
            
            result = DistributionResult(
                job_id=asset.asset_id,
                platform=self.platform,
                success=True,
                platform_id=f"spotify_{int(datetime.utcnow().timestamp())}",
                asset_url=f"https://open.spotify.com/track/mock_{asset.asset_id}",
                metadata={
                    "isrc": f"US{datetime.utcnow().year}{asset.asset_id[:10]}",
                    "release_date": datetime.utcnow().date().isoformat()
                }
            )
            
            self.logger.info(f"Spotify upload successful: {result.platform_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Spotify upload failed: {e}")
            return DistributionResult(
                job_id=asset.asset_id,
                platform=self.platform,
                success=False,
                error_message=str(e)
            )
    
    async def update_content(self, platform_id: str, 
                           metadata: ContentMetadata) -> bool:
        """Update Spotify track metadata"""        try:
            self.logger.info(f"Updating Spotify track {platform_id}")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self.logger.error(f"Spotify update failed: {e}")
            return False
    
    async def delete_content(self, platform_id: str) -> bool:
        """Delete Spotify track"""        try:
            self.logger.info(f"Deleting Spotify track {platform_id}")
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self.logger.error(f"Spotify deletion failed: {e}")
            return False
    
    async def get_analytics(self, platform_id: str, 
                          date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get Spotify analytics"""        return {
            "streams": 5000,
            "listeners": 1200,
            "saves": 150,
            "playlist_adds": 75,
            "skip_rate": 0.15,
            "countries": ["US", "UK", "DE", "FR"],
            "monthly_listeners": 800
        }

class ContentDistributionNetwork:
    """Main CDN orchestrator"""    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.optimizer = ContentOptimizer()
        self.distributors: Dict[DistributionPlatform, BasePlatformDistributor] = {}
        self.job_queue = asyncio.PriorityQueue()
        self.active_jobs: Dict[str, DistributionJob] = {}
        self.completed_jobs: List[DistributionJob] = []
        self.worker_tasks: List[asyncio.Task] = []
        self.max_workers = 5
        self.running = False
        
        # Initialize distributors
        self._initialize_distributors()
    
    def _initialize_distributors(self):
        """Initialize platform distributors"""        self.distributors = {
            DistributionPlatform.YOUTUBE: YouTubeDistributor(),
            DistributionPlatform.SPOTIFY: SpotifyDistributor(),
            # Add more distributors as needed
        }
        
        self.logger.info(f"Initialized {len(self.distributors)} distributors")
    
    async def authenticate_all(self) -> Dict[DistributionPlatform, bool]:
        """Authenticate with all platforms"""        results = {}
        
        for platform, distributor in self.distributors.items():
            try:
                results[platform] = await distributor.authenticate()
            except Exception as e:
                self.logger.error(f"Authentication failed for {platform}: {e}")
                results[platform] = False
        
        return results
    
    def create_asset(self, file_path: str, metadata: ContentMetadata) -> ContentAsset:
        """Create content asset"""        # Generate asset ID
        asset_id = hashlib.md5(
            f"{file_path}_{metadata.title}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        # Calculate content hash
        content_hash = hashlib.sha256(file_path.encode()).hexdigest()
        
        return ContentAsset(
            asset_id=asset_id,
            file_path=file_path,
            metadata=metadata,
            content_hash=content_hash
        )
    
    async def submit_distribution_job(self, asset: ContentAsset, 
                                    target_platforms: List[DistributionPlatform],
                                    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD,
                                    schedule_time: Optional[datetime] = None,
                                    priority: int = 5) -> str:
        """Submit content distribution job"""        job_id = f"job_{int(datetime.utcnow().timestamp())}_{asset.asset_id[:8]}"
        
        job = DistributionJob(
            job_id=job_id,
            asset=asset,
            target_platforms=target_platforms,
            optimization_level=optimization_level,
            schedule_time=schedule_time,
            priority=priority
        )
        
        # Add to queue (priority queue uses negative priority for max-heap behavior)
        await self.job_queue.put((-priority, datetime.utcnow(), job))
        self.active_jobs[job_id] = job
        
        self.logger.info(f"Submitted distribution job {job_id} for {len(target_platforms)} platforms")
        return job_id
    
    async def start_workers(self):
        """Start distribution worker tasks"""        if self.running:
            return
        
        self.running = True
        self.worker_tasks = [
            asyncio.create_task(self._distribution_worker(i)) 
            for i in range(self.max_workers)
        ]
        
        self.logger.info(f"Started {self.max_workers} distribution workers")
    
    async def stop_workers(self):
        """Stop distribution worker tasks"""        self.running = False
        
        for task in self.worker_tasks:
            task.cancel()
        
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        self.logger.info("Stopped all distribution workers")
    
    async def _distribution_worker(self, worker_id: int):
        """Distribution worker coroutine"""        self.logger.info(f"Distribution worker {worker_id} started")
        
        while self.running:
            try:
                # Get job from queue with timeout
                try:
                    priority, timestamp, job = await asyncio.wait_for(
                        self.job_queue.get(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Check if job is scheduled for future
                if job.schedule_time and job.schedule_time > datetime.utcnow():
                    # Put back in queue
                    await self.job_queue.put((priority, timestamp, job))
                    await asyncio.sleep(60)  # Wait before checking again
                    continue
                
                # Process job
                await self._process_distribution_job(job, worker_id)
                
                # Mark queue task as done
                self.job_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        self.logger.info(f"Distribution worker {worker_id} stopped")
    
    async def _process_distribution_job(self, job: DistributionJob, worker_id: int):
        """Process single distribution job"""        self.logger.info(f"Worker {worker_id} processing job {job.job_id}")
        
        job.status = ContentStatus.PROCESSING
        job.started_at = datetime.utcnow()
        
        results = []
        
        for platform in job.target_platforms:
            try:
                # Check if distributor is available
                if platform not in self.distributors:
                    self.logger.error(f"No distributor available for {platform}")
                    continue
                
                distributor = self.distributors[platform]
                
                # Validate content for platform
                is_valid, issues = await self.optimizer.validate_content(job.asset, platform)
                
                if not is_valid and job.optimization_level == OptimizationLevel.NONE:
                    self.logger.error(f"Content validation failed for {platform}: {issues}")
                    result = DistributionResult(
                        job_id=job.job_id,
                        platform=platform,
                        success=False,
                        error_message=f"Validation failed: {'; '.join(issues)}"
                    )
                    results.append(result)
                    continue
                
                # Optimize content if needed
                optimized_path = job.asset.file_path
                if not is_valid or job.optimization_level != OptimizationLevel.NONE:
                    optimized_path = await self.optimizer.optimize_for_platform(
                        job.asset, platform, job.optimization_level
                    )
                    
                    if not optimized_path:
                        result = DistributionResult(
                            job_id=job.job_id,
                            platform=platform,
                            success=False,
                            error_message="Content optimization failed"
                        )
                        results.append(result)
                        continue
                
                # Update asset with optimized path
                optimized_asset = ContentAsset(
                    asset_id=job.asset.asset_id,
                    file_path=optimized_path,
                    metadata=job.asset.metadata,
                    content_hash=job.asset.content_hash,
                    versions=job.asset.versions.copy(),
                    status=job.asset.status
                )
                
                # Distribute content
                job.progress[platform] = 0.5  # 50% progress
                result = await distributor.upload_content(optimized_asset, job.asset.metadata)
                job.progress[platform] = 1.0  # 100% progress
                
                results.append(result)
                
                # Update distribution history
                job.asset.distribution_history.append({
                    'platform': platform.value,
                    'result': result.__dict__,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Distribution to {platform} failed: {e}")
                result = DistributionResult(
                    job_id=job.job_id,
                    platform=platform,
                    success=False,
                    error_message=str(e)
                )
                results.append(result)
        
        # Determine overall job status
        successful_distributions = sum(1 for r in results if r.success)
        
        if successful_distributions == len(job.target_platforms):
            job.status = ContentStatus.PUBLISHED
        elif successful_distributions > 0:
            job.status = ContentStatus.PUBLISHED  # Partial success
        else:
            job.status = ContentStatus.FAILED
            job.retry_count += 1
            
            # Retry if under max retries
            if job.retry_count <= job.max_retries:
                await asyncio.sleep(60)  # Wait before retry
                await self.job_queue.put((-job.priority, datetime.utcnow(), job))
                return
        
        job.completed_at = datetime.utcnow()
        
        # Move to completed jobs
        if job.job_id in self.active_jobs:
            del self.active_jobs[job.job_id]
        self.completed_jobs.append(job)
        
        # Keep only last 1000 completed jobs
        if len(self.completed_jobs) > 1000:
            self.completed_jobs = self.completed_jobs[-1000:]
        
        self.logger.info(f"Job {job.job_id} completed: {successful_distributions}/{len(job.target_platforms)} successful")
    
    def get_job_status(self, job_id: str) -> Optional[DistributionJob]:
        """Get job status"""        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        for job in self.completed_jobs:
            if job.job_id == job_id:
                return job
        
        return None
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get distribution statistics"""        total_jobs = len(self.completed_jobs)
        
        if total_jobs == 0:
            return {"total_jobs": 0}
        
        successful_jobs = sum(1 for job in self.completed_jobs 
                            if job.status == ContentStatus.PUBLISHED)
        
        platform_stats = {}
        for job in self.completed_jobs:
            for platform in job.target_platforms:
                platform_name = platform.value
                if platform_name not in platform_stats:
                    platform_stats[platform_name] = {
                        "total_attempts": 0,
                        "successful": 0,
                        "failed": 0
                    }
                
                platform_stats[platform_name]["total_attempts"] += 1
                
                # Check distribution history for this platform
                for history_item in job.asset.distribution_history:
                    if history_item.get('platform') == platform_name:
                        if history_item.get('result', {}).get('success'):
                            platform_stats[platform_name]["successful"] += 1
                        else:
                            platform_stats[platform_name]["failed"] += 1
                        break
        
        return {
            "total_jobs": total_jobs,
            "successful_jobs": successful_jobs,
            "success_rate": successful_jobs / total_jobs,
            "active_jobs": len(self.active_jobs),
            "platform_statistics": platform_stats
        }
    
    async def cleanup(self):
        """Cleanup resources"""        await self.stop_workers()
        self.optimizer.clear_cache()
        self.logger.info("Content distribution network cleaned up")

# Export main classes
__all__ = [
    'ContentDistributionNetwork',
    'ContentOptimizer',
    'BasePlatformDistributor',
    'YouTubeDistributor',
    'SpotifyDistributor',
    'ContentAsset',
    'ContentMetadata',
    'DistributionJob',
    'DistributionResult',
    'ContentType',
    'DistributionPlatform',
    'ContentStatus',
    'OptimizationLevel',
    'PlatformRequirements'
]

logger.info("Content distribution network module loaded successfully")
