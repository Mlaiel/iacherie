"""
Content Distributor - Enterprise Multi-Platform Content Distribution Engine

This module provides intelligent content distribution across multiple platforms with
format adaptation, audience optimization, and automated scheduling.

🎯 Expert Roles Applied:
- Lead Dev IA: AI-driven content optimization and platform targeting
- Backend Senior: Robust distribution engine with fault tolerance
- ML Engineer: Machine learning for audience targeting and timing optimization
- DBA: Optimized content storage and distribution tracking
- Sécurité: Secure content delivery and rights management
- Microservices: Distributed content processing architecture
- Audio: Audio content processing and format optimization
- DevOps: Scalable distribution infrastructure and monitoring
- IA Prompt Engineer: AI-powered content enhancement and adaptation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorDatabase
import aiohttp
import hashlib
import mimetypes
from pathlib import Path
import ffmpeg
from PIL import Image
import io

from .platform_manager import PlatformType, ContentType, PlatformConfig, PlatformManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DistributionStatus(Enum):
    """Content distribution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    DISTRIBUTED = "distributed"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class OptimizationLevel(Enum):
    """Content optimization levels"""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    AI_ENHANCED = "ai_enhanced"


@dataclass
class ContentMetadata:
    """Enhanced content metadata for distribution"""
    content_id: str
    title: str
    description: str
    content_type: ContentType
    file_path: str
    file_size: int
    duration: Optional[float] = None
    dimensions: Optional[Tuple[int, int]] = None
    bitrate: Optional[int] = None
    format: Optional[str] = None
    thumbnail_path: Optional[str] = None
    tags: List[str] = None
    category: Optional[str] = None
    language: str = "en"
    age_rating: str = "general"
    monetization_enabled: bool = True
    
    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []


@dataclass
class PlatformAdaptation:
    """Platform-specific content adaptations"""
    platform_type: PlatformType
    adapted_title: str
    adapted_description: str
    adapted_tags: List[str]
    file_path: str
    thumbnail_path: Optional[str] = None
    custom_metadata: Dict[str, Any] = None
    posting_schedule: Optional[datetime] = None
    audience_targeting: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.custom_metadata is None:
            self.custom_metadata = {}
        if self.audience_targeting is None:
            self.audience_targeting = {}


@dataclass
class DistributionJob:
    """Content distribution job"""
    job_id: str
    user_id: str
    content_metadata: ContentMetadata
    target_platforms: List[PlatformType]
    adaptations: Dict[str, PlatformAdaptation]
    optimization_level: OptimizationLevel
    status: DistributionStatus
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    platform_results: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        if self.platform_results is None:
            self.platform_results = {}


class ContentDistributor:
    """
    Enterprise Content Distribution Engine
    
    Provides intelligent content distribution across multiple platforms with
    AI-powered optimization, format adaptation, and audience targeting.
    """
    
    def __init__(self, db -> None: AsyncIOMotorDatabase, platform_manager -> None: PlatformManager) -> None:
        """
        Initialize Content Distributor
        
        Args:
            db: MongoDB database connection
            platform_manager: Platform manager instance
        """
        self.db = db
        self.platform_manager = platform_manager
        
        # Collections
        self.jobs_collection = db.distribution_jobs
        self.adaptations_collection = db.content_adaptations
        self.results_collection = db.distribution_results
        self.templates_collection = db.content_templates
        
        # Processing queues
        self._pending_jobs: asyncio.Queue = asyncio.Queue()
        self._processing_jobs: Dict[str, DistributionJob] = {}
        
        # Worker tasks
        self._workers: List[asyncio.Task] = []
        self._is_running = False
        
        # Content processing capabilities
        self._supported_video_formats = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'}
        self._supported_audio_formats = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        self._supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        # AI optimization settings
        self._ai_optimization_enabled = True
        self._max_concurrent_jobs = 5
    
    async def initialize(self) -> None:
        """Initialize content distributor"""
        try:
            # Create indexes
            await self.jobs_collection.create_index([("user_id", 1), ("status", 1)])
            await self.jobs_collection.create_index([("created_at", -1)])
            await self.jobs_collection.create_index([("scheduled_at", 1)])
            
            await self.adaptations_collection.create_index([("content_id", 1), ("platform_type", 1)])
            await self.results_collection.create_index([("job_id", 1)])
            await self.templates_collection.create_index([("platform_type", 1), ("content_type", 1)])
            
            # Start worker tasks
            await self._start_workers()
            
            logger.info("Content Distributor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Content Distributor: {e}")
            raise
    
    async def distribute_content(self, user_id: str, content_metadata: ContentMetadata,
                               target_platforms: List[PlatformType],
                               optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED,
                               schedule_time: Optional[datetime] = None) -> str:
        """
        Distribute content to specified platforms
        
        Args:
            user_id: User identifier
            content_metadata: Content metadata
            target_platforms: List of target platforms
            optimization_level: Optimization level to apply
            schedule_time: Optional scheduled distribution time
            
        Returns:
            str: Distribution job ID
        """
        try:
            # Generate job ID
            job_id = hashlib.md5(f"{user_id}:{content_metadata.content_id}:{datetime.utcnow()}".encode()).hexdigest()
            
            # Validate content file exists
            if not Path(content_metadata.file_path).exists():
                raise ValueError(f"Content file not found: {content_metadata.file_path}")
            
            # Validate user has access to target platforms
            valid_platforms = await self._validate_user_platforms(user_id, target_platforms)
            if not valid_platforms:
                raise ValueError("No valid platforms available for distribution")
            
            # Create platform adaptations
            adaptations = await self._create_platform_adaptations(
                content_metadata, valid_platforms, optimization_level
            )
            
            # Create distribution job
            job = DistributionJob(
                job_id=job_id,
                user_id=user_id,
                content_metadata=content_metadata,
                target_platforms=valid_platforms,
                adaptations=adaptations,
                optimization_level=optimization_level,
                status=DistributionStatus.SCHEDULED if schedule_time else DistributionStatus.PENDING,
                created_at=datetime.utcnow(),
                scheduled_at=schedule_time
            )
            
            # Store job in database
            await self.jobs_collection.insert_one(asdict(job))
            
            # Add to processing queue if not scheduled
            if not schedule_time:
                await self._pending_jobs.put(job)
            
            logger.info(f"Content distribution job {job_id} created for user {user_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create distribution job: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get distribution job status
        
        Args:
            job_id: Job identifier
            
        Returns:
            Optional[Dict[str, Any]]: Job status information
        """
        try:
            # Check if job is currently processing
            if job_id in self._processing_jobs:
                job = self._processing_jobs[job_id]
                return {
                    "job_id": job_id,
                    "status": job.status.value,
                    "progress": job.progress,
                    "created_at": job.created_at,
                    "platform_results": job.platform_results
                }
            
            # Retrieve from database
            doc = await self.jobs_collection.find_one({"job_id": job_id})
            if not doc:
                return None
            
            return {
                "job_id": job_id,
                "status": doc["status"],
                "progress": doc.get("progress", 0.0),
                "created_at": doc["created_at"],
                "completed_at": doc.get("completed_at"),
                "error_message": doc.get("error_message"),
                "platform_results": doc.get("platform_results", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a distribution job
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: Success status
        """
        try:
            # Update job status in database
            result = await self.jobs_collection.update_one(
                {"job_id": job_id, "status": {"$in": ["pending", "scheduled", "processing"]}},
                {
                    "$set": {
                        "status": DistributionStatus.CANCELLED.value,
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            # Remove from processing if currently active
            if job_id in self._processing_jobs:
                self._processing_jobs[job_id].status = DistributionStatus.CANCELLED
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to cancel job: {e}")
            return False
    
    async def get_user_jobs(self, user_id: str, limit: int = 50, 
                          status_filter: Optional[DistributionStatus] = None) -> List[Dict[str, Any]]:
        """
        Get user's distribution jobs
        
        Args:
            user_id: User identifier
            limit: Maximum number of jobs to return
            status_filter: Optional status filter
            
        Returns:
            List[Dict[str, Any]]: List of user jobs
        """
        try:
            query = {"user_id": user_id}
            if status_filter:
                query["status"] = status_filter.value
            
            cursor = self.jobs_collection.find(query).sort("created_at", -1).limit(limit)
            jobs = await cursor.to_list(length=None)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get user jobs: {e}")
            return []
    
    async def _validate_user_platforms(self, user_id: str, platforms: List[PlatformType]) -> List[PlatformType]:
        """Validate user has access to specified platforms"""
        valid_platforms = []
        
        for platform in platforms:
            config = await self.platform_manager.get_platform(user_id, platform)
            if config and config.status.value == "active":
                valid_platforms.append(platform)
        
        return valid_platforms
    
    async def _create_platform_adaptations(self, content: ContentMetadata, 
                                         platforms: List[PlatformType],
                                         optimization_level: OptimizationLevel) -> Dict[str, PlatformAdaptation]:
        """Create platform-specific content adaptations"""
        adaptations = {}
        
        for platform in platforms:
            try:
                # Get platform-specific requirements
                platform_specs = await self._get_platform_specifications(platform)
                
                # Create adapted content
                adaptation = await self._adapt_content_for_platform(
                    content, platform, platform_specs, optimization_level
                )
                
                adaptations[platform.value] = adaptation
                
            except Exception as e:
                logger.error(f"Failed to create adaptation for {platform.value}: {e}")
        
        return adaptations
    
    async def _get_platform_specifications(self, platform: PlatformType) -> Dict[str, Any]:
        """Get platform-specific requirements and constraints"""
        
        platform_specs = {
            PlatformType.YOUTUBE: {
                "max_title_length": 100,
                "max_description_length": 5000,
                "max_tags": 15,
                "preferred_formats": ["mp4"],
                "max_file_size_mb": 128000,
                "max_duration_seconds": 43200,
                "aspect_ratios": ["16:9", "9:16", "1:1"],
                "min_resolution": (426, 240),
                "max_resolution": (7680, 4320)
            },
            PlatformType.INSTAGRAM: {
                "max_title_length": 30,
                "max_description_length": 2200,
                "max_tags": 30,
                "preferred_formats": ["mp4", "jpg", "png"],
                "max_file_size_mb": 100,
                "max_duration_seconds": 3600,
                "aspect_ratios": ["1:1", "4:5", "9:16"],
                "min_resolution": (600, 315),
                "max_resolution": (1936, 1936)
            },
            PlatformType.TIKTOK: {
                "max_title_length": 150,
                "max_description_length": 4000,
                "max_tags": 20,
                "preferred_formats": ["mp4"],
                "max_file_size_mb": 287,
                "max_duration_seconds": 600,
                "aspect_ratios": ["9:16"],
                "min_resolution": (540, 960),
                "max_resolution": (1080, 1920)
            },
            PlatformType.TWITTER: {
                "max_title_length": 280,
                "max_description_length": 280,
                "max_tags": 10,
                "preferred_formats": ["mp4", "gif", "jpg", "png"],
                "max_file_size_mb": 512,
                "max_duration_seconds": 140,
                "aspect_ratios": ["16:9", "1:1"],
                "min_resolution": (32, 32),
                "max_resolution": (8192, 8192)
            }
        }
        
        return platform_specs.get(platform, {})
    
    async def _adapt_content_for_platform(self, content: ContentMetadata, 
                                        platform: PlatformType,
                                        specs: Dict[str, Any],
                                        optimization_level: OptimizationLevel) -> PlatformAdaptation:
        """Adapt content for specific platform requirements"""
        
        # Adapt title
        adapted_title = content.title
        if specs.get("max_title_length"):
            adapted_title = content.title[:specs["max_title_length"]]
        
        # Adapt description
        adapted_description = content.description
        if specs.get("max_description_length"):
            adapted_description = content.description[:specs["max_description_length"]]
        
        # Adapt tags
        adapted_tags = content.tags.copy()
        if specs.get("max_tags"):
            adapted_tags = content.tags[:specs["max_tags"]]
        
        # Process content file if needed
        adapted_file_path = content.file_path
        if optimization_level != OptimizationLevel.NONE:
            adapted_file_path = await self._process_content_file(
                content, platform, specs, optimization_level
            )
        
        # AI enhancement if enabled
        if optimization_level == OptimizationLevel.AI_ENHANCED and self._ai_optimization_enabled:
            adapted_title, adapted_description, adapted_tags = await self._ai_enhance_content(
                adapted_title, adapted_description, adapted_tags, platform
            )
        
        return PlatformAdaptation(
            platform_type=platform,
            adapted_title=adapted_title,
            adapted_description=adapted_description,
            adapted_tags=adapted_tags,
            file_path=adapted_file_path,
            thumbnail_path=content.thumbnail_path
        )
    
    async def _process_content_file(self, content: ContentMetadata, 
                                  platform: PlatformType,
                                  specs: Dict[str, Any],
                                  optimization_level: OptimizationLevel) -> str:
        """Process content file for platform requirements"""
        
        file_path = Path(content.file_path)
        output_dir = file_path.parent / "adapted" / platform.value
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{file_path.stem}_{platform.value}{file_path.suffix}"
        
        try:
            if content.content_type == ContentType.VIDEO:
                return await self._process_video_file(content.file_path, str(output_path), specs)
            elif content.content_type == ContentType.AUDIO:
                return await self._process_audio_file(content.file_path, str(output_path), specs)
            elif content.content_type == ContentType.IMAGE:
                return await self._process_image_file(content.file_path, str(output_path), specs)
            else:
                # For other content types, return original path
                return content.file_path
                
        except Exception as e:
            logger.error(f"Failed to process content file: {e}")
            return content.file_path
    
    async def _process_video_file(self, input_path: str, output_path: str, specs: Dict[str, Any]) -> str:
        """Process video file for platform requirements"""
        
        try:
            # Get video info
            probe = ffmpeg.probe(input_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if not video_stream:
                return input_path
            
            # Determine target resolution and aspect ratio
            current_width = int(video_stream['width'])
            current_height = int(video_stream['height'])
            
            # Calculate target dimensions based on platform specs
            target_width, target_height = self._calculate_target_dimensions(
                current_width, current_height, specs
            )
            
            # Build ffmpeg command
            stream = ffmpeg.input(input_path)
            
            # Apply video filters
            if target_width != current_width or target_height != current_height:
                stream = ffmpeg.filter(stream, 'scale', target_width, target_height)
            
            # Set output parameters
            output_params = {
                'vcodec': 'libx264',
                'acodec': 'aac',
                'format': 'mp4'
            }
            
            # Apply quality settings based on platform
            if specs.get("max_file_size_mb"):
                # Calculate bitrate for target file size
                duration = float(video_stream.get('duration', 0))
                if duration > 0:
                    target_bitrate = (specs["max_file_size_mb"] * 8 * 1024) / duration * 0.8  # 80% of max
                    output_params['video_bitrate'] = f"{int(target_bitrate)}k"
            
            stream = ffmpeg.output(stream, output_path, **output_params)
            
            # Run ffmpeg
            await asyncio.create_subprocess_exec(*ffmpeg.compile(stream))
            
            return output_path
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return input_path
    
    async def _process_audio_file(self, input_path: str, output_path: str, specs: Dict[str, Any]) -> str:
        """Process audio file for platform requirements"""
        
        try:
            stream = ffmpeg.input(input_path)
            
            # Set output parameters
            output_params = {
                'acodec': 'aac',
                'format': 'mp4'  # Most platforms prefer mp4 container
            }
            
            # Apply bitrate limits if specified
            if specs.get("max_file_size_mb"):
                output_params['audio_bitrate'] = '128k'  # Standard quality
            
            stream = ffmpeg.output(stream, output_path, **output_params)
            await asyncio.create_subprocess_exec(*ffmpeg.compile(stream))
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return input_path
    
    async def _process_image_file(self, input_path: str, output_path: str, specs: Dict[str, Any]) -> str:
        """Process image file for platform requirements"""
        
        try:
            with Image.open(input_path) as img:
                # Calculate target dimensions
                current_width, current_height = img.size
                target_width, target_height = self._calculate_target_dimensions(
                    current_width, current_height, specs
                )
                
                # Resize if needed
                if target_width != current_width or target_height != current_height:
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Save with optimized quality
                save_params = {'optimize': True}
                
                if output_path.lower().endswith(('.jpg', '.jpeg')):
                    save_params['quality'] = 85
                    save_params['progressive'] = True
                
                img.save(output_path, **save_params)
                
            return output_path
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return input_path
    
    def _calculate_target_dimensions(self, width: int, height: int, specs: Dict[str, Any]) -> Tuple[int, int]:
        """Calculate target dimensions based on platform specifications"""
        
        target_width, target_height = width, height
        
        # Apply resolution constraints
        if specs.get("max_resolution"):
            max_w, max_h = specs["max_resolution"]
            if width > max_w or height > max_h:
                scale = min(max_w / width, max_h / height)
                target_width = int(width * scale)
                target_height = int(height * scale)
        
        if specs.get("min_resolution"):
            min_w, min_h = specs["min_resolution"]
            if target_width < min_w or target_height < min_h:
                scale = max(min_w / target_width, min_h / target_height)
                target_width = int(target_width * scale)
                target_height = int(target_height * scale)
        
        # Ensure even dimensions for video encoding
        target_width = target_width - (target_width % 2)
        target_height = target_height - (target_height % 2)
        
        return target_width, target_height
    
    async def _ai_enhance_content(self, title: str, description: str, tags: List[str], 
                                platform: PlatformType) -> Tuple[str, str, List[str]]:
        """AI-enhance content for platform optimization"""
        
        # This would integrate with actual AI services
        # For now, return basic enhancements
        
        # Platform-specific optimizations
        if platform == PlatformType.YOUTUBE:
            # Optimize for YouTube SEO
            if not title.endswith(" - YouTube"):
                title += " - YouTube"
            
            # Add trending hashtags
            if "#YouTube" not in tags:
                tags.append("#YouTube")
        
        elif platform == PlatformType.TIKTOK:
            # Optimize for TikTok trends
            if "#TikTok" not in tags:
                tags.append("#TikTok")
            if "#Viral" not in tags:
                tags.append("#Viral")
        
        elif platform == PlatformType.INSTAGRAM:
            # Optimize for Instagram engagement
            if "#Instagram" not in tags:
                tags.append("#Instagram")
            if "#Insta" not in tags:
                tags.append("#Insta")
        
        return title, description, tags
    
    async def _start_workers(self) -> None:
        """Start worker tasks for processing jobs"""
        
        if self._is_running:
            return
        
        self._is_running = True
        
        # Start worker tasks
        for i in range(self._max_concurrent_jobs):
            worker = asyncio.create_task(self._worker_task(f"worker_{i}"))
            self._workers.append(worker)
        
        # Start scheduler for scheduled jobs
        scheduler = asyncio.create_task(self._scheduler_task())
        self._workers.append(scheduler)
        
        logger.info(f"Started {len(self._workers)} worker tasks")
    
    async def _worker_task(self, worker_name: str) -> None:
        """Worker task for processing distribution jobs"""
        
        logger.info(f"Worker {worker_name} started")
        
        while self._is_running:
            try:
                # Get job from queue
                job = await asyncio.wait_for(self._pending_jobs.get(), timeout=1.0)
                
                # Process job
                await self._process_distribution_job(job, worker_name)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _scheduler_task(self) -> None:
        """Scheduler task for handling scheduled jobs"""
        
        while self._is_running:
            try:
                # Check for scheduled jobs that are ready
                now = datetime.utcnow()
                cursor = self.jobs_collection.find({
                    "status": DistributionStatus.SCHEDULED.value,
                    "scheduled_at": {"$lte": now}
                })
                
                async for doc in cursor:
                    # Convert to job object and add to queue
                    job = await self._doc_to_job(doc)
                    job.status = DistributionStatus.PENDING
                    
                    await self.jobs_collection.update_one(
                        {"job_id": job.job_id},
                        {"$set": {"status": DistributionStatus.PENDING.value}}
                    )
                    
                    await self._pending_jobs.put(job)
                
                # Sleep before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _process_distribution_job(self, job: DistributionJob, worker_name: str) -> None:
        """Process a distribution job"""
        
        logger.info(f"Worker {worker_name} processing job {job.job_id}")
        
        try:
            # Update job status
            job.status = DistributionStatus.PROCESSING
            self._processing_jobs[job.job_id] = job
            
            await self.jobs_collection.update_one(
                {"job_id": job.job_id},
                {"$set": {"status": DistributionStatus.PROCESSING.value}}
            )
            
            # Process each platform
            total_platforms = len(job.target_platforms)
            completed_platforms = 0
            
            for platform in job.target_platforms:
                try:
                    # Get platform adaptation
                    adaptation = job.adaptations.get(platform.value)
                    if not adaptation:
                        continue
                    
                    # Distribute to platform
                    result = await self._distribute_to_platform(
                        job.user_id, platform, adaptation
                    )
                    
                    job.platform_results[platform.value] = result
                    completed_platforms += 1
                    
                    # Update progress
                    job.progress = (completed_platforms / total_platforms) * 100
                    
                    await self.jobs_collection.update_one(
                        {"job_id": job.job_id},
                        {
                            "$set": {
                                "progress": job.progress,
                                f"platform_results.{platform.value}": result
                            }
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to distribute to {platform.value}: {e}")
                    job.platform_results[platform.value] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            # Determine final status
            successful_platforms = sum(1 for result in job.platform_results.values() 
                                     if result.get("status") == "success")
            
            if successful_platforms == 0:
                job.status = DistributionStatus.FAILED
            elif successful_platforms == total_platforms:
                job.status = DistributionStatus.DISTRIBUTED
            else:
                job.status = DistributionStatus.PARTIAL
            
            job.completed_at = datetime.utcnow()
            job.progress = 100.0
            
            # Update database
            await self.jobs_collection.update_one(
                {"job_id": job.job_id},
                {
                    "$set": {
                        "status": job.status.value,
                        "completed_at": job.completed_at,
                        "progress": job.progress,
                        "platform_results": job.platform_results
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Job processing failed: {e}")
            job.status = DistributionStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            await self.jobs_collection.update_one(
                {"job_id": job.job_id},
                {
                    "$set": {
                        "status": DistributionStatus.FAILED.value,
                        "error_message": str(e),
                        "completed_at": job.completed_at
                    }
                }
            )
        
        finally:
            # Remove from processing jobs
            if job.job_id in self._processing_jobs:
                del self._processing_jobs[job.job_id]
            
            logger.info(f"Worker {worker_name} completed job {job.job_id} with status {job.status.value}")
    
    async def _distribute_to_platform(self, user_id: str, platform: PlatformType, 
                                    adaptation: PlatformAdaptation) -> Dict[str, Any]:
        """Distribute content to specific platform"""
        
        # This would integrate with actual platform APIs
        # For now, simulate successful distribution
        
        try:
            # Simulate API call delay
            await asyncio.sleep(2)
            
            # Return success result
            return {
                "status": "success",
                "platform_id": f"{platform.value}_{hashlib.md5(adaptation.adapted_title.encode()).hexdigest()[:8]}",
                "url": f"https://{platform.value}.com/content/{adaptation.adapted_title.replace(' ', '_')}",
                "distributed_at": datetime.utcnow().isoformat(),
                "views": 0,
                "likes": 0,
                "shares": 0,
                "comments": 0
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "attempted_at": datetime.utcnow().isoformat()
            }
    
    async def _doc_to_job(self, doc: Dict[str, Any]) -> DistributionJob:
        """Convert database document to DistributionJob object"""
        
        # This is a simplified conversion - in production, use proper serialization
        content_data = doc["content_metadata"]
        content = ContentMetadata(**content_data)
        
        adaptations = {}
        for platform_key, adaptation_data in doc.get("adaptations", {}).items():
            adaptations[platform_key] = PlatformAdaptation(**adaptation_data)
        
        return DistributionJob(
            job_id=doc["job_id"],
            user_id=doc["user_id"],
            content_metadata=content,
            target_platforms=[PlatformType(p) for p in doc["target_platforms"]],
            adaptations=adaptations,
            optimization_level=OptimizationLevel(doc["optimization_level"]),
            status=DistributionStatus(doc["status"]),
            created_at=doc["created_at"],
            scheduled_at=doc.get("scheduled_at"),
            completed_at=doc.get("completed_at"),
            error_message=doc.get("error_message"),
            progress=doc.get("progress", 0.0),
            platform_results=doc.get("platform_results", {})
        )
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        self._is_running = False
        
        # Cancel all worker tasks
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        
        logger.info("Content Distributor cleanup completed")


async def create_content_distributor(db: AsyncIOMotorDatabase, 
                                   platform_manager: PlatformManager) -> ContentDistributor:
    """
    Factory function to create and initialize Content Distributor
    
    Args:
        db: MongoDB database connection
        platform_manager: Platform manager instance
        
    Returns:
        ContentDistributor: Initialized content distributor
    """
    distributor = ContentDistributor(db, platform_manager)
    await distributor.initialize()
    return distributor