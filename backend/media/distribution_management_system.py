"""Distribution Management System - Enterprise Multi-Platform Distribution Engine
============================================================================

Consolidated distribution system providing comprehensive content distribution management,
platform-specific content adaptation, and intelligent delivery optimization.

Consolidates:
- Content distribution management and routing (content_distribution_manager.py)
- Platform-specific content adaptation system (platform_adapter_system.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary distribution system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or distribution logic appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# External service imports with graceful fallbacks
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
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not available - using fallback image handling")

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    logging.warning("OpenCV not available - using basic image processing")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("Librosa not available - using basic audio processing")

logger = logging.getLogger(__name__)


class DistributionPlatform(Enum):
    """Supported distribution platforms"""
    # Social Media
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    TWITCH = "twitch"
    # Professional
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    # Podcasting
    SPOTIFY = "spotify"
    APPLE_PODCASTS = "apple_podcasts"
    GOOGLE_PODCASTS = "google_podcasts"
    # Websites
    WORDPRESS = "wordpress"
    MEDIUM = "medium"
    # Cloud Storage
    DROPBOX = "dropbox"
    GOOGLE_DRIVE = "google_drive"
    AWS_S3 = "aws_s3"
    # Custom
    CUSTOM_API = "custom_api"
    WEBHOOK = "webhook"


class DistributionStatus(Enum):
    """Distribution status types"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    ADAPTING = "adapting"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"
    RETRY = "retry"


class ContentType(Enum):
    """Content types for distribution"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    PODCAST = "podcast"


class AdaptationType(Enum):
    """Content adaptation types"""
    RESIZE = "resize"
    CROP = "crop"
    COMPRESS = "compress"
    FORMAT_CONVERT = "format_convert"
    QUALITY_ADJUST = "quality_adjust"
    WATERMARK = "watermark"
    SUBTITLE = "subtitle"
    THUMBNAIL = "thumbnail"
    METADATA = "metadata"


@dataclass
class DistributionConfig:
    """Distribution system configuration"""
    max_concurrent_uploads: int = 10
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    auto_adapt_content: bool = True
    quality_preservation: bool = True
    watermark_enabled: bool = False
    auto_scheduling: bool = True
    analytics_enabled: bool = True
    backup_enabled: bool = True


@dataclass
class PlatformRequirements:
    """Platform-specific requirements"""
    platform: DistributionPlatform
    max_file_size: int  # bytes
    supported_formats: List[str]
    max_duration: Optional[int] = None  # seconds
    aspect_ratios: List[str] = field(default_factory=list)
    resolution_limits: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    text_limits: Dict[str, int] = field(default_factory=dict)
    api_rate_limits: Dict[str, int] = field(default_factory=dict)
    auth_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentAdaptation:
    """Content adaptation specification"""
    adaptation_id: str
    source_content_id: str
    target_platform: DistributionPlatform
    adaptations_needed: List[AdaptationType]
    target_format: str
    target_quality: str
    target_dimensions: Optional[Tuple[int, int]] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionTask:
    """Distribution task definition"""
    task_id: str
    content_id: str
    target_platforms: List[DistributionPlatform]
    scheduling: Optional[datetime] = None
    priority: int = 1  # 1-5 scale
    status: DistributionStatus = DistributionStatus.PENDING
    adaptations: List[ContentAdaptation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class DistributionResult:
    """Distribution result data"""
    task_id: str
    platform: DistributionPlatform
    status: DistributionStatus
    platform_content_id: Optional[str] = None
    platform_url: Optional[str] = None
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None
    adaptation_applied: List[AdaptationType] = field(default_factory=list)
    upload_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PlatformAdapter:
    """Adapts content for specific platform requirements"""
    
    def __init__(self, platform -> None: DistributionPlatform, requirements -> None: PlatformRequirements) -> None:
        self.platform = platform
        self.requirements = requirements
        self.adaptation_cache = {}
        
        logger.info(f"🔧 Platform Adapter initialized for {platform.value}")
    
    async def adapt_content(
        self, 
        content_path: str, 
        content_type: ContentType,
        target_specs: Optional[Dict[str, Any]] = None
    ) -> ContentAdaptation:
        """Adapt content for platform requirements"""
        try:
            adaptation_id = str(uuid.uuid4())
            adaptations_needed = []
            
            # Analyze content and determine needed adaptations
            content_info = await self._analyze_content(content_path, content_type)
            
            # Check file size requirements
            if content_info.get('file_size', 0) > self.requirements.max_file_size:
                adaptations_needed.append(AdaptationType.COMPRESS)
            
            # Check format requirements
            if content_info.get('format') not in self.requirements.supported_formats:
                adaptations_needed.append(AdaptationType.FORMAT_CONVERT)
            
            # Check resolution requirements
            if content_type in [ContentType.IMAGE, ContentType.VIDEO]:
                await self._check_resolution_requirements(content_info, adaptations_needed)
            
            # Check duration requirements
            if content_type in [ContentType.VIDEO, ContentType.AUDIO] and self.requirements.max_duration:
                if content_info.get('duration', 0) > self.requirements.max_duration:
                    adaptations_needed.append(AdaptationType.QUALITY_ADJUST)
            
            # Determine target format and quality
            target_format = self._determine_target_format(content_type)
            target_quality = target_specs.get('quality', 'high') if target_specs else 'high'
            
            adaptation = ContentAdaptation(
                adaptation_id=adaptation_id,
                source_content_id=content_info.get('content_id', str(uuid.uuid4())),
                target_platform=self.platform,
                adaptations_needed=adaptations_needed,
                target_format=target_format,
                target_quality=target_quality,
                target_dimensions=self._determine_target_dimensions(content_type, target_specs),
                custom_parameters=target_specs or {}
            )
            
            logger.info(f"Content adaptation planned for {self.platform.value}: {len(adaptations_needed)} adaptations needed")
            return adaptation
            
        except Exception as e:
            logger.error(f"Content adaptation planning failed for {self.platform.value}: {e}")
            raise
    
    async def apply_adaptations(
        self, 
        adaptation: ContentAdaptation, 
        source_path: str
    ) -> str:
        """Apply content adaptations and return adapted content path"""
        try:
            adapted_path = source_path
            
            for adaptation_type in adaptation.adaptations_needed:
                if adaptation_type == AdaptationType.RESIZE:
                    adapted_path = await self._resize_content(adapted_path, adaptation.target_dimensions)
                elif adaptation_type == AdaptationType.CROP:
                    adapted_path = await self._crop_content(adapted_path, adaptation.target_dimensions)
                elif adaptation_type == AdaptationType.COMPRESS:
                    adapted_path = await self._compress_content(adapted_path, adaptation.target_quality)
                elif adaptation_type == AdaptationType.FORMAT_CONVERT:
                    adapted_path = await self._convert_format(adapted_path, adaptation.target_format)
                elif adaptation_type == AdaptationType.QUALITY_ADJUST:
                    adapted_path = await self._adjust_quality(adapted_path, adaptation.target_quality)
                elif adaptation_type == AdaptationType.WATERMARK:
                    adapted_path = await self._add_watermark(adapted_path)
                elif adaptation_type == AdaptationType.THUMBNAIL:
                    adapted_path = await self._generate_thumbnail(adapted_path)
            
            logger.info(f"Applied {len(adaptation.adaptations_needed)} adaptations for {self.platform.value}")
            return adapted_path
            
        except Exception as e:
            logger.error(f"Content adaptation application failed: {e}")
            return source_path  # Return original if adaptation fails
    
    async def _analyze_content(self, content_path: str, content_type: ContentType) -> Dict[str, Any]:
        """Analyze content properties"""
        try:
            file_path = Path(content_path)
            file_size = file_path.stat().st_size if file_path.exists() else 0
            
            content_info = {
                'content_id': str(uuid.uuid4()),
                'file_size': file_size,
                'format': file_path.suffix.lower().lstrip('.'),
                'path': str(file_path)
            }
            
            if content_type == ContentType.IMAGE and HAS_PIL:
                try:
                    with Image.open(content_path) as img:
                        content_info.update({
                            'width': img.width,
                            'height': img.height,
                            'aspect_ratio': img.width / img.height,
                            'mode': img.mode
                        })
                except Exception:
                    pass
            
            elif content_type == ContentType.VIDEO and HAS_OPENCV:
                try:
                    cap = cv2.VideoCapture(content_path)
                    if cap.isOpened():
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        duration = frame_count / fps if fps > 0 else 0
                        
                        content_info.update({
                            'width': width,
                            'height': height,
                            'aspect_ratio': width / height if height > 0 else 1,
                            'fps': fps,
                            'duration': duration
                        })
                    cap.release()
                except Exception:
                    pass
            
            elif content_type == ContentType.AUDIO and HAS_LIBROSA:
                try:
                    y, sr = librosa.load(content_path)
                    duration = librosa.get_duration(y=y, sr=sr)
                    content_info.update({
                        'duration': duration,
                        'sample_rate': sr,
                        'channels': 1 if len(y.shape) == 1 else y.shape[0]
                    })
                except Exception:
                    pass
            
            return content_info
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {'content_id': str(uuid.uuid4()), 'file_size': 0, 'format': 'unknown'}
    
    async def _check_resolution_requirements(self, content_info -> None: Dict[str, Any], adaptations_needed -> None: List[AdaptationType]) -> None:
        """Check if content meets resolution requirements"""
        content_width = content_info.get('width', 0)
        content_height = content_info.get('height', 0)
        
        # Check against platform resolution limits
        for limit_type, (max_width, max_height) in self.requirements.resolution_limits.items():
            if content_width > max_width or content_height > max_height:
                adaptations_needed.append(AdaptationType.RESIZE)
                break
        
        # Check aspect ratio requirements
        if self.requirements.aspect_ratios and content_width > 0 and content_height > 0:
            content_ratio = content_width / content_height
            
            # Find closest supported aspect ratio
            supported_ratios = []
            for ratio_str in self.requirements.aspect_ratios:
                try:
                    if ':' in ratio_str:
                        w, h = map(float, ratio_str.split(':'))
                        supported_ratios.append(w / h)
                    else:
                        supported_ratios.append(float(ratio_str))
                except ValueError:
                    continue
            
            if supported_ratios:
                closest_ratio = min(supported_ratios, key=lambda x: abs(x - content_ratio))
                if abs(closest_ratio - content_ratio) > 0.1:  # 10% tolerance
                    adaptations_needed.append(AdaptationType.CROP)
    
    def _determine_target_format(self, content_type: ContentType) -> str:
        """Determine optimal target format for platform"""
        format_preferences = {
            ContentType.IMAGE: 'jpg',
            ContentType.VIDEO: 'mp4',
            ContentType.AUDIO: 'mp3',
            ContentType.DOCUMENT: 'pdf'
        }
        
        preferred_format = format_preferences.get(content_type, 'mp4')
        
        # Use platform's preferred format if available
        if self.requirements.supported_formats:
            if preferred_format in self.requirements.supported_formats:
                return preferred_format
            else:
                return self.requirements.supported_formats[0]
        
        return preferred_format
    
    def _determine_target_dimensions(self, content_type: ContentType, target_specs: Optional[Dict[str, Any]]) -> Optional[Tuple[int, int]]:
        """Determine target dimensions for content"""
        if target_specs and 'dimensions' in target_specs:
            return target_specs['dimensions']
        
        # Platform-specific optimal dimensions
        optimal_dimensions = {
            DistributionPlatform.INSTAGRAM: {
                ContentType.IMAGE: (1080, 1080),
                ContentType.VIDEO: (1080, 1080),
                ContentType.STORY: (1080, 1920),
                ContentType.REEL: (1080, 1920)
            },
            DistributionPlatform.YOUTUBE: {
                ContentType.VIDEO: (1920, 1080),
                ContentType.SHORT: (1080, 1920)
            },
            DistributionPlatform.TIKTOK: {
                ContentType.VIDEO: (1080, 1920)
            },
            DistributionPlatform.TWITTER: {
                ContentType.IMAGE: (1200, 675),
                ContentType.VIDEO: (1280, 720)
            }
        }
        
        return optimal_dimensions.get(self.platform, {}).get(content_type)
    
    async def _resize_content(self, content_path: str, target_dimensions: Optional[Tuple[int, int]]) -> str:
        """Resize content to target dimensions"""
        if not target_dimensions or not HAS_PIL:
            return content_path
        
        try:
            output_path = content_path.replace('.', '_resized.')
            
            with Image.open(content_path) as img:
                resized_img = img.resize(target_dimensions, Image.Resampling.LANCZOS)
                resized_img.save(output_path, optimize=True, quality=95)
            
            return output_path
        except Exception as e:
            logger.error(f"Content resize failed: {e}")
            return content_path
    
    async def _crop_content(self, content_path: str, target_dimensions: Optional[Tuple[int, int]]) -> str:
        """Crop content to target aspect ratio"""
        if not target_dimensions or not HAS_PIL:
            return content_path
        
        try:
            output_path = content_path.replace('.', '_cropped.')
            target_width, target_height = target_dimensions
            target_ratio = target_width / target_height
            
            with Image.open(content_path) as img:
                img_ratio = img.width / img.height
                
                if abs(img_ratio - target_ratio) > 0.01:  # Need to crop
                    if img_ratio > target_ratio:
                        # Image is wider, crop width
                        new_width = int(img.height * target_ratio)
                        left = (img.width - new_width) // 2
                        crop_box = (left, 0, left + new_width, img.height)
                    else:
                        # Image is taller, crop height
                        new_height = int(img.width / target_ratio)
                        top = (img.height - new_height) // 2
                        crop_box = (0, top, img.width, top + new_height)
                    
                    cropped_img = img.crop(crop_box)
                    cropped_img = cropped_img.resize(target_dimensions, Image.Resampling.LANCZOS)
                    cropped_img.save(output_path, optimize=True, quality=95)
                else:
                    # No cropping needed, just resize
                    resized_img = img.resize(target_dimensions, Image.Resampling.LANCZOS)
                    resized_img.save(output_path, optimize=True, quality=95)
            
            return output_path
        except Exception as e:
            logger.error(f"Content crop failed: {e}")
            return content_path
    
    async def _compress_content(self, content_path: str, target_quality: str) -> str:
        """Compress content to reduce file size"""
        try:
            output_path = content_path.replace('.', '_compressed.')
            
            quality_settings = {
                'low': 60,
                'medium': 75,
                'high': 85,
                'maximum': 95
            }
            
            quality = quality_settings.get(target_quality, 75)
            
            if HAS_PIL and content_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                with Image.open(content_path) as img:
                    img.save(output_path, optimize=True, quality=quality)
                return output_path
            
            return content_path
        except Exception as e:
            logger.error(f"Content compression failed: {e}")
            return content_path
    
    async def _convert_format(self, content_path: str, target_format: str) -> str:
        """Convert content to target format"""
        try:
            file_path = Path(content_path)
            output_path = str(file_path.with_suffix(f'.{target_format}'))
            
            if HAS_PIL and target_format in ['jpg', 'jpeg', 'png', 'webp']:
                with Image.open(content_path) as img:
                    if target_format in ['jpg', 'jpeg'] and img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img.save(output_path, format=target_format.upper())
                return output_path
            
            return content_path
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            return content_path
    
    async def _adjust_quality(self, content_path: str, target_quality: str) -> str:
        """Adjust content quality"""
        # For now, same as compression
        return await self._compress_content(content_path, target_quality)
    
    async def _add_watermark(self, content_path: str) -> str:
        """Add watermark to content"""
        try:
            output_path = content_path.replace('.', '_watermarked.')
            
            if HAS_PIL and content_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                with Image.open(content_path) as img:
                    # Simple text watermark (would use actual watermark image in production)
                    from PIL import ImageDraw, ImageFont
                    
                    draw = ImageDraw.Draw(img)
                    watermark_text = "© Ainflue"
                    
                    # Position watermark at bottom right
                    text_width = len(watermark_text) * 10  # Rough estimate
                    text_height = 20
                    x = img.width - text_width - 10
                    y = img.height - text_height - 10
                    
                    draw.text((x, y), watermark_text, fill=(255, 255, 255, 128))
                    img.save(output_path)
                
                return output_path
            
            return content_path
        except Exception as e:
            logger.error(f"Watermark addition failed: {e}")
            return content_path
    
    async def _generate_thumbnail(self, content_path: str) -> str:
        """Generate thumbnail for content"""
        try:
            output_path = content_path.replace('.', '_thumbnail.')
            
            if HAS_PIL:
                with Image.open(content_path) as img:
                    img.thumbnail((320, 240), Image.Resampling.LANCZOS)
                    img.save(output_path)
                return output_path
            
            return content_path
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return content_path


class DistributionManager:
    """Manages content distribution across multiple platforms"""
    
    def __init__(self, config -> None: DistributionConfig) -> None:
        self.config = config
        self.platform_adapters: Dict[DistributionPlatform, PlatformAdapter] = {}
        self.distribution_queue: List[DistributionTask] = []
        self.active_tasks: Dict[str, DistributionTask] = {}
        self.results_history: List[DistributionResult] = []
        
        # Initialize platform requirements
        self._initialize_platform_requirements()
        
        # Task executor
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_uploads)
        
        logger.info("📡 Distribution Manager initialized")
    
    def _initialize_platform_requirements(self) -> None:
        """Initialize platform-specific requirements"""
        platform_requirements = {
            DistributionPlatform.INSTAGRAM: PlatformRequirements(
                platform=DistributionPlatform.INSTAGRAM,
                max_file_size=100 * 1024 * 1024,  # 100MB
                supported_formats=['jpg', 'jpeg', 'png', 'mp4'],
                max_duration=60,
                aspect_ratios=['1:1', '4:5', '9:16'],
                resolution_limits={'max': (1080, 1920)},
                text_limits={'caption': 2200, 'bio': 150}
            ),
            DistributionPlatform.YOUTUBE: PlatformRequirements(
                platform=DistributionPlatform.YOUTUBE,
                max_file_size=256 * 1024 * 1024 * 1024,  # 256GB
                supported_formats=['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                max_duration=12 * 3600,  # 12 hours
                aspect_ratios=['16:9', '4:3'],
                resolution_limits={'4k': (3840, 2160), 'hd': (1920, 1080)},
                text_limits={'title': 100, 'description': 5000}
            ),
            DistributionPlatform.TIKTOK: PlatformRequirements(
                platform=DistributionPlatform.TIKTOK,
                max_file_size=4 * 1024 * 1024 * 1024,  # 4GB
                supported_formats=['mp4', 'mov'],
                max_duration=600,  # 10 minutes
                aspect_ratios=['9:16'],
                resolution_limits={'max': (1080, 1920)},
                text_limits={'caption': 300}
            ),
            DistributionPlatform.TWITTER: PlatformRequirements(
                platform=DistributionPlatform.TWITTER,
                max_file_size=512 * 1024 * 1024,  # 512MB
                supported_formats=['jpg', 'jpeg', 'png', 'gif', 'mp4'],
                max_duration=140,
                aspect_ratios=['16:9', '1:1'],
                resolution_limits={'max': (1920, 1080)},
                text_limits={'tweet': 280}
            )
        }
        
        # Initialize adapters for each platform
        for platform, requirements in platform_requirements.items():
            self.platform_adapters[platform] = PlatformAdapter(platform, requirements)
    
    async def create_distribution_task(
        self,
        content_id: str,
        content_path: str,
        content_type: ContentType,
        target_platforms: List[DistributionPlatform],
        scheduling: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: int = 1
    ) -> DistributionTask:
        """Create new distribution task"""
        try:
            task_id = str(uuid.uuid4())
            
            # Create content adaptations for each platform
            adaptations = []
            for platform in target_platforms:
                if platform in self.platform_adapters:
                    adapter = self.platform_adapters[platform]
                    adaptation = await adapter.adapt_content(content_path, content_type)
                    adaptations.append(adaptation)
            
            task = DistributionTask(
                task_id=task_id,
                content_id=content_id,
                target_platforms=target_platforms,
                scheduling=scheduling,
                priority=priority,
                adaptations=adaptations,
                metadata=metadata or {}
            )
            
            # Add to queue
            self.distribution_queue.append(task)
            self.distribution_queue.sort(key=lambda t: (-t.priority, t.created_at))
            
            logger.info(f"Distribution task created: {task_id} for {len(target_platforms)} platforms")
            return task
            
        except Exception as e:
            logger.error(f"Failed to create distribution task: {e}")
            raise
    
    async def execute_distribution_task(self, task: DistributionTask, content_path: str) -> List[DistributionResult]:
        """Execute distribution task across all target platforms"""
        try:
            task.status = DistributionStatus.PROCESSING
            task.started_at = datetime.now(timezone.utc)
            self.active_tasks[task.task_id] = task
            
            results = []
            
            # Execute distribution for each platform
            for platform in task.target_platforms:
                try:
                    result = await self._distribute_to_platform(task, content_path, platform)
                    results.append(result)
                except Exception as e:
                    error_result = DistributionResult(
                        task_id=task.task_id,
                        platform=platform,
                        status=DistributionStatus.FAILED,
                        error_details=str(e)
                    )
                    results.append(error_result)
            
            # Update task status
            if all(r.status == DistributionStatus.PUBLISHED for r in results):
                task.status = DistributionStatus.PUBLISHED
            elif any(r.status == DistributionStatus.PUBLISHED for r in results):
                task.status = DistributionStatus.PUBLISHED  # Partial success
            else:
                task.status = DistributionStatus.FAILED
            
            task.completed_at = datetime.now(timezone.utc)
            
            # Store results
            self.results_history.extend(results)
            
            # Clean up active task
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
            logger.info(f"Distribution task completed: {task.task_id} - {task.status.value}")
            return results
            
        except Exception as e:
            logger.error(f"Distribution task execution failed: {e}")
            task.status = DistributionStatus.FAILED
            task.error_message = str(e)
            return []
    
    async def _distribute_to_platform(
        self, 
        task: DistributionTask, 
        content_path: str, 
        platform: DistributionPlatform
    ) -> DistributionResult:
        """Distribute content to specific platform"""
        try:
            # Find relevant adaptation
            adaptation = None
            for adapt in task.adaptations:
                if adapt.target_platform == platform:
                    adaptation = adapt
                    break
            
            if not adaptation:
                raise ValueError(f"No adaptation found for platform {platform.value}")
            
            # Apply content adaptations
            adapter = self.platform_adapters[platform]
            adapted_content_path = await adapter.apply_adaptations(adaptation, content_path)
            
            # Simulate platform upload (would use actual APIs in production)
            upload_result = await self._upload_to_platform(platform, adapted_content_path, task.metadata)
            
            result = DistributionResult(
                task_id=task.task_id,
                platform=platform,
                status=DistributionStatus.PUBLISHED,
                platform_content_id=upload_result.get('content_id'),
                platform_url=upload_result.get('url'),
                adaptation_applied=adaptation.adaptations_needed,
                upload_metrics=upload_result.get('metrics', {}),
                analytics_data=upload_result.get('analytics', {})
            )
            
            logger.info(f"Successfully distributed to {platform.value}")
            return result
            
        except Exception as e:
            logger.error(f"Distribution to {platform.value} failed: {e}")
            return DistributionResult(
                task_id=task.task_id,
                platform=platform,
                status=DistributionStatus.FAILED,
                error_details=str(e)
            )
    
    async def _upload_to_platform(
        self, 
        platform: DistributionPlatform, 
        content_path: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload content to platform (simulated)"""
        # This would contain actual platform API calls in production
        
        # Simulate upload delay
        await asyncio.sleep(1)
        
        # Simulate successful upload
        upload_result = {
            'content_id': f"{platform.value}_{uuid.uuid4().hex[:8]}",
            'url': f"https://{platform.value}.com/content/{uuid.uuid4().hex[:8]}",
            'metrics': {
                'upload_time': 1.2,
                'file_size': Path(content_path).stat().st_size if Path(content_path).exists() else 0,
                'processing_time': 0.5
            },
            'analytics': {
                'estimated_reach': 1000,
                'predicted_engagement': 50
            }
        }
        
        return upload_result
    
    async def process_distribution_queue(self) -> List[DistributionResult]:
        """Process pending distribution tasks"""
        try:
            if not self.distribution_queue:
                return []
            
            # Get tasks ready for processing
            current_time = datetime.now(timezone.utc)
            ready_tasks = [
                task for task in self.distribution_queue
                if (task.scheduling is None or task.scheduling <= current_time) and
                task.status == DistributionStatus.PENDING
            ]
            
            if not ready_tasks:
                return []
            
            # Process tasks up to concurrency limit
            tasks_to_process = ready_tasks[:self.config.max_concurrent_uploads]
            all_results = []
            
            # Execute tasks in parallel
            tasks = []
            for task in tasks_to_process:
                # Remove from queue
                if task in self.distribution_queue:
                    self.distribution_queue.remove(task)
                
                # Note: In production, would need actual content path
                content_path = f"/tmp/content_{task.content_id}"
                tasks.append(self.execute_distribution_task(task, content_path))
            
            if tasks:
                results_batches = await asyncio.gather(*tasks, return_exceptions=True)
                for batch in results_batches:
                    if not isinstance(batch, Exception):
                        all_results.extend(batch)
            
            logger.info(f"Processed {len(tasks_to_process)} distribution tasks")
            return all_results
            
        except Exception as e:
            logger.error(f"Distribution queue processing failed: {e}")
            return []
    
    async def get_distribution_status(self, task_id: str) -> Dict[str, Any]:
        """Get distribution task status"""
        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                return {
                    'task_id': task_id,
                    'status': task.status.value,
                    'progress': 'in_progress',
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'target_platforms': [p.value for p in task.target_platforms]
                }
            
            # Check completed tasks
            task_results = [r for r in self.results_history if r.task_id == task_id]
            if task_results:
                return {
                    'task_id': task_id,
                    'status': 'completed',
                    'results': [
                        {
                            'platform': r.platform.value,
                            'status': r.status.value,
                            'platform_url': r.platform_url,
                            'error': r.error_details
                        }
                        for r in task_results
                    ],
                    'completed_at': max(r.timestamp for r in task_results).isoformat()
                }
            
            # Check pending tasks
            pending_task = next((t for t in self.distribution_queue if t.task_id == task_id), None)
            if pending_task:
                return {
                    'task_id': task_id,
                    'status': pending_task.status.value,
                    'scheduled_for': pending_task.scheduling.isoformat() if pending_task.scheduling else None,
                    'position_in_queue': self.distribution_queue.index(pending_task) + 1
                }
            
            return {'error': f'Task {task_id} not found'}
            
        except Exception as e:
            logger.error(f"Failed to get distribution status: {e}")
            return {'error': str(e)}
    
    async def get_analytics_summary(self, time_range: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Get distribution analytics summary"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - time_range
            
            # Filter results by time range
            recent_results = [
                r for r in self.results_history
                if start_time <= r.timestamp <= end_time
            ]
            
            if not recent_results:
                return {'error': 'No distribution data available for the specified time range'}
            
            # Calculate summary statistics
            total_distributions = len(recent_results)
            successful_distributions = len([r for r in recent_results if r.status == DistributionStatus.PUBLISHED])
            success_rate = successful_distributions / total_distributions if total_distributions > 0 else 0
            
            # Platform distribution
            platform_stats = {}
            for result in recent_results:
                platform = result.platform.value
                if platform not in platform_stats:
                    platform_stats[platform] = {'total': 0, 'successful': 0}
                platform_stats[platform]['total'] += 1
                if result.status == DistributionStatus.PUBLISHED:
                    platform_stats[platform]['successful'] += 1
            
            # Calculate platform success rates
            for platform, stats in platform_stats.items():
                stats['success_rate'] = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            
            return {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'summary': {
                    'total_distributions': total_distributions,
                    'successful_distributions': successful_distributions,
                    'success_rate': success_rate,
                    'platform_statistics': platform_stats
                },
                'performance': {
                    'avg_upload_time': 1.2,  # Would calculate from actual metrics
                    'avg_processing_time': 0.5,
                    'total_content_size': sum(r.upload_metrics.get('file_size', 0) for r in recent_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Analytics summary generation failed: {e}")
            return {'error': str(e)}


class DistributionManagementSystem:
    """Main distribution management system orchestrating all distribution components"""
    
    def __init__(self, config -> None: Optional[DistributionConfig] = None) -> None:
        """Initialize distribution management system"""
        self.config = config or DistributionConfig()
        self.distribution_manager = DistributionManager(self.config)
        
        # System-wide state
        self.content_registry: Dict[str, Dict[str, Any]] = {}
        
        logger.info("🚀 Distribution Management System initialized")
    
    async def distribute_content(
        self,
        content_id: str,
        content_path: str,
        content_type: ContentType,
        target_platforms: List[DistributionPlatform],
        distribution_config: Optional[Dict[str, Any]] = None
    ) -> DistributionTask:
        """Distribute content across multiple platforms"""
        try:
            # Register content
            self.content_registry[content_id] = {
                'path': content_path,
                'type': content_type.value,
                'registered_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract distribution parameters
            config = distribution_config or {}
            scheduling = config.get('schedule')
            if scheduling and isinstance(scheduling, str):
                scheduling = datetime.fromisoformat(scheduling)
            
            priority = config.get('priority', 1)
            metadata = config.get('metadata', {})
            
            # Create distribution task
            task = await self.distribution_manager.create_distribution_task(
                content_id=content_id,
                content_path=content_path,
                content_type=content_type,
                target_platforms=target_platforms,
                scheduling=scheduling,
                metadata=metadata,
                priority=priority
            )
            
            logger.info(f"Content distribution initiated: {content_id} -> {len(target_platforms)} platforms")
            return task
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            raise
    
    async def batch_distribute_content(
        self, 
        distribution_requests: List[Dict[str, Any]]
    ) -> List[DistributionTask]:
        """Batch distribute multiple content pieces"""
        try:
            tasks = []
            
            for request in distribution_requests:
                try:
                    task = await self.distribute_content(
                        content_id=request['content_id'],
                        content_path=request['content_path'],
                        content_type=ContentType(request['content_type']),
                        target_platforms=[DistributionPlatform(p) for p in request['platforms']],
                        distribution_config=request.get('config', {})
                    )
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Failed to create distribution task for {request.get('content_id')}: {e}")
            
            logger.info(f"Batch distribution created: {len(tasks)}/{len(distribution_requests)} tasks successful")
            return tasks
            
        except Exception as e:
            logger.error(f"Batch distribution failed: {e}")
            return []
    
    async def process_pending_distributions(self) -> List[DistributionResult]:
        """Process all pending distribution tasks"""
        return await self.distribution_manager.process_distribution_queue()
    
    async def get_content_distribution_status(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive distribution status for content"""
        try:
            content_info = self.content_registry.get(content_id, {})
            
            if not content_info:
                return {'error': f'Content {content_id} not found in registry'}
            
            # Find all tasks for this content
            all_tasks = (
                list(self.distribution_manager.active_tasks.values()) +
                self.distribution_manager.distribution_queue
            )
            
            content_tasks = [t for t in all_tasks if t.content_id == content_id]
            
            # Find all results for this content
            content_results = [r for r in self.distribution_manager.results_history if r.task_id in [t.task_id for t in content_tasks]]
            
            return {
                'content_id': content_id,
                'content_info': content_info,
                'total_tasks': len(content_tasks),
                'active_tasks': len([t for t in content_tasks if t.status == DistributionStatus.PROCESSING]),
                'pending_tasks': len([t for t in content_tasks if t.status == DistributionStatus.PENDING]),
                'completed_tasks': len(content_results),
                'platform_status': [
                    {
                        'platform': r.platform.value,
                        'status': r.status.value,
                        'url': r.platform_url,
                        'timestamp': r.timestamp.isoformat()
                    }
                    for r in content_results
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get content distribution status: {e}")
            return {'error': str(e)}


# Backward compatibility classes for existing imports
class ContentDistributionManager_Legacy:
    """Legacy wrapper for distribution manager"""
    def __init__(self, *args, **kwargs) -> None:
        config = DistributionConfig()
        self.manager = DistributionManager(config)


class PlatformAdapterSystem_Legacy:
    """Legacy wrapper for platform adapter system"""
    def __init__(self, *args, **kwargs) -> None:
        self.adapters = {}
        # Initialize with basic requirements
        for platform in DistributionPlatform:
            requirements = PlatformRequirements(
                platform=platform,
                max_file_size=100 * 1024 * 1024,
                supported_formats=['jpg', 'mp4']
            )
            self.adapters[platform] = PlatformAdapter(platform, requirements)


# Export all classes for consolidated import
__all__ = [
    'DistributionManagementSystem',
    'DistributionManager',
    'PlatformAdapter',
    'DistributionConfig',
    'PlatformRequirements',
    'ContentAdaptation',
    'DistributionTask',
    'DistributionResult',
    'DistributionPlatform',
    'DistributionStatus',
    'ContentType',
    'AdaptationType',
    # Legacy compatibility
    'ContentDistributionManager_Legacy',
    'PlatformAdapterSystem_Legacy'
]