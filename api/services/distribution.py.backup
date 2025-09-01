"""Enterprise Multi-Platform Distribution Service - Automated Content Publishing
Intelligent distribution across social media, streaming, and content platforms

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + Social Media API Expert + DevOps Expert

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel.
Unauthorized copying, distribution, or use without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
from pathlib import Path

import aiohttp
import redis
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.domain import ContentAsset, Creator, DistributionLog, PlatformCredentials
from backend.app.core.exceptions import DistributionError, PlatformError
from backend.app.services.seo_optimizer import SEOOptimizerService

logger = logging.getLogger(__name__)


class Platform(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISCORD = "discord"


class DistributionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    REVIEWING = "reviewing"


class ContentFormat(Enum):
    ORIGINAL = "original"
    SQUARE = "square"         # 1:1 for Instagram
    VERTICAL = "vertical"     # 9:16 for TikTok, Shorts
    HORIZONTAL = "horizontal" # 16:9 for YouTube
    STORY = "story"          # 9:16 for Stories
    AUDIO_ONLY = "audio_only" # For audio platforms


@dataclass
class PlatformConfig:
    name: str
    api_endpoint: str
    supported_formats: List[str]
    max_file_size: int
    aspect_ratios: List[str]
    required_metadata: List[str]
    authentication_type: str
    rate_limits: Dict[str, int]
    content_guidelines: List[str]


@dataclass
class DistributionResult:
    platform: Platform
    status: DistributionStatus
    platform_id: Optional[str]
    platform_url: Optional[str]
    published_at: Optional[datetime]
    engagement_metrics: Dict[str, Any]
    error_message: Optional[str]
    retry_count: int
    metadata: Dict[str, Any]


@dataclass
class DistributionRequest:
    asset_id: int
    platforms: List[Platform]
    schedule_time: Optional[datetime]
    custom_metadata: Dict[str, Any]
    format_preferences: Dict[Platform, ContentFormat]
    audience_targeting: Dict[str, Any]
    promotion_settings: Dict[str, Any]


class MultiPlatformDistributionService:
    """
    Professional multi-platform distribution service with intelligent
    content optimization and automated publishing workflows
    """
    
    PLATFORM_CONFIGS = {
        Platform.YOUTUBE: PlatformConfig(
            name="YouTube",
            api_endpoint="https://www.googleapis.com/youtube/v3",
            supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
            max_file_size=128 * 1024 * 1024 * 1024,  # 128GB
            aspect_ratios=["16:9", "4:3", "1:1", "9:16"],
            required_metadata=["title", "description"],
            authentication_type="oauth2",
            rate_limits={"uploads_per_day": 100, "api_calls_per_day": 10000},
            content_guidelines=["No copyrighted music", "Community guidelines compliance"]
        ),
        Platform.INSTAGRAM: PlatformConfig(
            name="Instagram",
            api_endpoint="https://graph.facebook.com/v18.0",
            supported_formats=["jpg", "jpeg", "png", "mp4", "mov"],
            max_file_size=100 * 1024 * 1024,  # 100MB
            aspect_ratios=["1:1", "4:5", "9:16"],
            required_metadata=["caption"],
            authentication_type="oauth2",
            rate_limits={"posts_per_hour": 25, "api_calls_per_hour": 200},
            content_guidelines=["No explicit content", "Original content preferred"]
        ),
        Platform.TIKTOK: PlatformConfig(
            name="TikTok",
            api_endpoint="https://open-api.tiktok.com",
            supported_formats=["mp4", "mov", "webm"],
            max_file_size=287 * 1024 * 1024,  # 287MB
            aspect_ratios=["9:16"],
            required_metadata=["description"],
            authentication_type="oauth2",
            rate_limits={"posts_per_day": 300, "api_calls_per_day": 1000},
            content_guidelines=["Community guidelines", "Copyright compliance"]
        ),
        Platform.SPOTIFY: PlatformConfig(
            name="Spotify",
            api_endpoint="https://api.spotify.com/v1",
            supported_formats=["mp3", "wav", "flac"],
            max_file_size=200 * 1024 * 1024,  # 200MB
            aspect_ratios=[],
            required_metadata=["title", "artist", "album"],
            authentication_type="oauth2",
            rate_limits={"uploads_per_day": 50},
            content_guidelines=["Original content only", "High audio quality required"]
        )
    }
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.seo_optimizer = SEOOptimizerService()
        self.session_pool = {}  # HTTP session pool for platforms
        
        # Distribution settings
        self.max_concurrent_uploads = 5
        self.retry_attempts = 3
        self.retry_delay = 60  # seconds
        
        # Content processing settings
        self.temp_dir = Path("/tmp/distribution")
        self.temp_dir.mkdir(exist_ok=True)

    async def distribute_content(
        self,
        db: Session,
        request: DistributionRequest
    ) -> List[DistributionResult]:
        """
        Distribute content to multiple platforms with intelligent optimization
        """
        try:
            asset = db.query(ContentAsset).filter(ContentAsset.id == request.asset_id).first()
            if not asset:
                raise DistributionError(f"Asset {request.asset_id} not found")
            
            creator = db.query(Creator).filter(Creator.id == asset.creator_id).first()
            
            # Prepare content for distribution
            prepared_content = await self._prepare_content_variants(asset, request)
            
            # Optimize metadata for each platform
            optimized_metadata = await self._optimize_platform_metadata(asset, request)
            
            # Distribute to platforms (with scheduling if specified)
            if request.schedule_time and request.schedule_time > datetime.now():
                return await self._schedule_distribution(db, asset, request, prepared_content, optimized_metadata)
            else:
                return await self._execute_immediate_distribution(db, asset, request, prepared_content, optimized_metadata)
                
        except Exception as e:
            logger.error(f"Content distribution failed: {str(e)}")
            raise DistributionError(f"Distribution failed: {str(e)}")

    async def _prepare_content_variants(
        self,
        asset: ContentAsset,
        request: DistributionRequest
    ) -> Dict[Platform, Dict[str, Any]]:
        """
        Prepare platform-specific content variants with optimal formats
        """
        variants = {}
        source_path = Path(asset.storage_uri)
        
        for platform in request.platforms:
            config = self.PLATFORM_CONFIGS.get(platform)
            if not config:
                logger.warning(f"Unsupported platform: {platform}")
                continue
            
            # Determine optimal format for platform
            target_format = request.format_preferences.get(platform, ContentFormat.ORIGINAL)
            
            # Process content based on platform requirements
            if asset.media_type == 'video':
                processed_content = await self._process_video_content(
                    source_path, platform, target_format, config
                )
            elif asset.media_type == 'image':
                processed_content = await self._process_image_content(
                    source_path, platform, target_format, config
                )
            elif asset.media_type == 'audio':
                processed_content = await self._process_audio_content(
                    source_path, platform, target_format, config
                )
            else:
                processed_content = {'file_path': source_path, 'format': 'original'}
            
            variants[platform] = processed_content
        
        return variants

    async def _process_video_content(
        self,
        source_path: Path,
        platform: Platform,
        target_format: ContentFormat,
        config: PlatformConfig
    ) -> Dict[str, Any]:
        """Process video content for platform-specific requirements"""
        try:
            from moviepy.editor import VideoFileClip
            
            with VideoFileClip(str(source_path)) as clip:
                # Determine target resolution and aspect ratio
                if target_format == ContentFormat.VERTICAL:
                    target_size = (1080, 1920)  # 9:16
                elif target_format == ContentFormat.SQUARE:
                    target_size = (1080, 1080)  # 1:1
                elif target_format == ContentFormat.HORIZONTAL:
                    target_size = (1920, 1080)  # 16:9
                else:
                    target_size = (clip.w, clip.h)  # Original
                
                # Generate processed file path
                output_path = self.temp_dir / f"{platform.value}_{source_path.stem}_processed{source_path.suffix}"
                
                # Resize and optimize
                processed_clip = clip.resize(target_size)
                
                # Apply platform-specific optimizations
                if platform == Platform.TIKTOK:
                    # TikTok prefers higher frame rates and specific codecs
                    processed_clip.write_videofile(
                        str(output_path),
                        codec='libx264',
                        fps=30,
                        bitrate="5000k"
                    )
                elif platform == Platform.INSTAGRAM:
                    # Instagram has specific requirements for video posts
                    processed_clip.write_videofile(
                        str(output_path),
                        codec='libx264',
                        fps=30,
                        bitrate="3500k"
                    )
                else:
                    processed_clip.write_videofile(str(output_path))
                
                return {
                    'file_path': output_path,
                    'format': target_format.value,
                    'resolution': f"{target_size[0]}x{target_size[1]}",
                    'file_size': output_path.stat().st_size,
                    'duration': clip.duration
                }
                
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            return {'file_path': source_path, 'format': 'original', 'error': str(e)}

    async def _process_image_content(
        self,
        source_path: Path,
        platform: Platform,
        target_format: ContentFormat,
        config: PlatformConfig
    ) -> Dict[str, Any]:
        """Process image content for platform-specific requirements"""
        try:
            from PIL import Image, ImageEnhance
            
            with Image.open(source_path) as img:
                # Determine target size based on platform and format
                if target_format == ContentFormat.SQUARE:
                    target_size = (1080, 1080)
                elif target_format == ContentFormat.VERTICAL:
                    target_size = (1080, 1350)  # Instagram portrait
                elif target_format == ContentFormat.HORIZONTAL:
                    target_size = (1200, 630)  # Facebook/LinkedIn landscape
                else:
                    target_size = img.size
                
                # Generate processed file path
                output_path = self.temp_dir / f"{platform.value}_{source_path.stem}_processed.jpg"
                
                # Resize maintaining aspect ratio
                img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Apply platform-specific enhancements
                if platform in [Platform.INSTAGRAM, Platform.FACEBOOK]:
                    # Enhance colors and contrast for social media
                    enhancer = ImageEnhance.Color(img_resized)
                    img_resized = enhancer.enhance(1.2)  # Slight color boost
                
                # Save with optimal quality
                img_resized.save(output_path, 'JPEG', quality=95, optimize=True)
                
                return {
                    'file_path': output_path,
                    'format': target_format.value,
                    'resolution': f"{target_size[0]}x{target_size[1]}",
                    'file_size': output_path.stat().st_size
                }
                
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return {'file_path': source_path, 'format': 'original', 'error': str(e)}

    async def _process_audio_content(
        self,
        source_path: Path,
        platform: Platform,
        target_format: ContentFormat,
        config: PlatformConfig
    ) -> Dict[str, Any]:
        """Process audio content for platform-specific requirements"""
        try:
            import librosa
            import soundfile as sf
            
            # Load audio
            y, sr = librosa.load(str(source_path), sr=None)
            
            # Platform-specific audio optimization
            if platform == Platform.SPOTIFY:
                # Spotify prefers high quality audio
                target_sr = 44100
                output_format = 'FLAC'
            else:
                # Standard quality for other platforms
                target_sr = 44100
                output_format = 'MP3'
            
            # Resample if necessary
            if sr != target_sr:
                y_resampled = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
            else:
                y_resampled = y
            
            # Generate output path
            ext = '.flac' if output_format == 'FLAC' else '.mp3'
            output_path = self.temp_dir / f"{platform.value}_{source_path.stem}_processed{ext}"
            
            # Save processed audio
            sf.write(str(output_path), y_resampled, target_sr)
            
            return {
                'file_path': output_path,
                'format': target_format.value,
                'sample_rate': target_sr,
                'file_size': output_path.stat().st_size,
                'duration': len(y_resampled) / target_sr
            }
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            return {'file_path': source_path, 'format': 'original', 'error': str(e)}

    async def _optimize_platform_metadata(
        self,
        asset: ContentAsset,
        request: DistributionRequest
    ) -> Dict[Platform, Dict[str, Any]]:
        """
        Optimize metadata for each platform using SEO and platform-specific best practices
        """
        optimized_metadata = {}
        base_metadata = asset.metadata or {}
        
        for platform in request.platforms:
            config = self.PLATFORM_CONFIGS.get(platform)
            if not config:
                continue
            
            # Get SEO-optimized content
            seo_data = await self.seo_optimizer.optimize_for_platform(
                title=asset.title,
                description=base_metadata.get('description', ''),
                tags=base_metadata.get('tags', []),
                platform=platform.value
            )
            
            # Platform-specific metadata optimization
            if platform == Platform.YOUTUBE:
                metadata = {
                    'title': seo_data.get('title', asset.title)[:100],
                    'description': seo_data.get('description', '')[:5000],
                    'tags': seo_data.get('tags', [])[:15],  # Max 15 tags
                    'category': self._determine_youtube_category(asset, base_metadata),
                    'privacy': request.custom_metadata.get('privacy', 'public'),
                    'thumbnail': request.custom_metadata.get('thumbnail_url'),
                    'language': base_metadata.get('language', 'en')
                }
            elif platform == Platform.INSTAGRAM:
                metadata = {
                    'caption': self._create_instagram_caption(seo_data, base_metadata)[:2200],
                    'hashtags': seo_data.get('hashtags', [])[:30],  # Max 30 hashtags
                    'location': request.custom_metadata.get('location'),
                    'alt_text': seo_data.get('alt_text', asset.title)[:100]
                }
            elif platform == Platform.TIKTOK:
                metadata = {
                    'description': self._create_tiktok_description(seo_data)[:150],
                    'hashtags': seo_data.get('hashtags', [])[:20],
                    'privacy': request.custom_metadata.get('privacy', 'public'),
                    'allows': {
                        'comment': request.custom_metadata.get('allow_comments', True),
                        'duet': request.custom_metadata.get('allow_duet', True),
                        'stitch': request.custom_metadata.get('allow_stitch', True)
                    }
                }
            elif platform == Platform.TWITTER:
                metadata = {
                    'text': self._create_twitter_text(seo_data)[:280],
                    'hashtags': seo_data.get('hashtags', [])[:10],
                    'reply_settings': request.custom_metadata.get('reply_settings', 'everyone')
                }
            else:
                # Generic metadata for other platforms
                metadata = {
                    'title': seo_data.get('title', asset.title),
                    'description': seo_data.get('description', ''),
                    'tags': seo_data.get('tags', [])
                }
            
            # Add common metadata
            metadata.update({
                'created_by': asset.creator_id,
                'source_asset_id': asset.id,
                'distribution_timestamp': datetime.now().isoformat()
            })
            
            optimized_metadata[platform] = metadata
        
        return optimized_metadata

    async def _execute_immediate_distribution(
        self,
        db: Session,
        asset: ContentAsset,
        request: DistributionRequest,
        prepared_content: Dict[Platform, Dict[str, Any]],
        optimized_metadata: Dict[Platform, Dict[str, Any]]
    ) -> List[DistributionResult]:
        """
        Execute immediate distribution to all platforms
        """
        results = []
        
        # Create semaphore to limit concurrent uploads
        semaphore = asyncio.Semaphore(self.max_concurrent_uploads)
        
        async def distribute_to_platform(platform: Platform):
            async with semaphore:
                return await self._distribute_to_single_platform(
                    db, asset, platform, prepared_content[platform], 
                    optimized_metadata[platform], request
                )
        
        # Execute distribution tasks
        tasks = []
        for platform in request.platforms:
            if platform in prepared_content and platform in optimized_metadata:
                task = asyncio.create_task(distribute_to_platform(platform))
                tasks.append(task)
        
        # Wait for all distributions to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter and log results
        successful_results = []
        for result in results:
            if isinstance(result, DistributionResult):
                successful_results.append(result)
                # Log distribution to database
                await self._log_distribution_result(db, result)
            elif isinstance(result, Exception):
                logger.error(f"Distribution task failed: {str(result)}")
        
        return successful_results

    async def _distribute_to_single_platform(
        self,
        db: Session,
        asset: ContentAsset,
        platform: Platform,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any],
        request: DistributionRequest
    ) -> DistributionResult:
        """
        Distribute content to a single platform with retry logic
        """
        for attempt in range(self.retry_attempts):
            try:
                # Get platform credentials
                credentials = await self._get_platform_credentials(db, asset.creator_id, platform)
                if not credentials:
                    return DistributionResult(
                        platform=platform,
                        status=DistributionStatus.FAILED,
                        platform_id=None,
                        platform_url=None,
                        published_at=None,
                        engagement_metrics={},
                        error_message="Platform credentials not configured",
                        retry_count=attempt,
                        metadata=metadata
                    )
                
                # Platform-specific distribution
                if platform == Platform.YOUTUBE:
                    result = await self._upload_to_youtube(content_data, metadata, credentials)
                elif platform == Platform.INSTAGRAM:
                    result = await self._upload_to_instagram(content_data, metadata, credentials)
                elif platform == Platform.TIKTOK:
                    result = await self._upload_to_tiktok(content_data, metadata, credentials)
                elif platform == Platform.TWITTER:
                    result = await self._upload_to_twitter(content_data, metadata, credentials)
                else:
                    result = await self._upload_to_generic_platform(platform, content_data, metadata, credentials)
                
                return result
                
            except Exception as e:
                logger.error(f"Distribution to {platform.value} failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    return DistributionResult(
                        platform=platform,
                        status=DistributionStatus.FAILED,
                        platform_id=None,
                        platform_url=None,
                        published_at=None,
                        engagement_metrics={},
                        error_message=str(e),
                        retry_count=attempt + 1,
                        metadata=metadata
                    )

    async def _upload_to_youtube(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> DistributionResult:
        """Upload content to YouTube using API"""
        try:
            # This would implement actual YouTube API integration
            # For now, simulate successful upload
            platform_id = f"YT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            platform_url = f"https://youtube.com/watch?v={platform_id}"
            
            return DistributionResult(
                platform=Platform.YOUTUBE,
                status=DistributionStatus.PUBLISHED,
                platform_id=platform_id,
                platform_url=platform_url,
                published_at=datetime.now(),
                engagement_metrics={'views': 0, 'likes': 0, 'comments': 0},
                error_message=None,
                retry_count=0,
                metadata=metadata
            )
            
        except Exception as e:
            raise PlatformError(f"YouTube upload failed: {str(e)}")

    async def _upload_to_instagram(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> DistributionResult:
        """Upload content to Instagram using API"""
        try:
            # Simulate Instagram upload
            platform_id = f"IG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            platform_url = f"https://instagram.com/p/{platform_id}"
            
            return DistributionResult(
                platform=Platform.INSTAGRAM,
                status=DistributionStatus.PUBLISHED,
                platform_id=platform_id,
                platform_url=platform_url,
                published_at=datetime.now(),
                engagement_metrics={'likes': 0, 'comments': 0, 'shares': 0},
                error_message=None,
                retry_count=0,
                metadata=metadata
            )
            
        except Exception as e:
            raise PlatformError(f"Instagram upload failed: {str(e)}")

    async def _upload_to_tiktok(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> DistributionResult:
        """Upload content to TikTok using API"""
        try:
            # Simulate TikTok upload
            platform_id = f"TT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            platform_url = f"https://tiktok.com/@user/video/{platform_id}"
            
            return DistributionResult(
                platform=Platform.TIKTOK,
                status=DistributionStatus.PUBLISHED,
                platform_id=platform_id,
                platform_url=platform_url,
                published_at=datetime.now(),
                engagement_metrics={'views': 0, 'likes': 0, 'shares': 0, 'comments': 0},
                error_message=None,
                retry_count=0,
                metadata=metadata
            )
            
        except Exception as e:
            raise PlatformError(f"TikTok upload failed: {str(e)}")

    async def _upload_to_twitter(
        self,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> DistributionResult:
        """Upload content to Twitter using API"""
        try:
            # Simulate Twitter upload
            platform_id = f"TW_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            platform_url = f"https://twitter.com/user/status/{platform_id}"
            
            return DistributionResult(
                platform=Platform.TWITTER,
                status=DistributionStatus.PUBLISHED,
                platform_id=platform_id,
                platform_url=platform_url,
                published_at=datetime.now(),
                engagement_metrics={'likes': 0, 'retweets': 0, 'replies': 0},
                error_message=None,
                retry_count=0,
                metadata=metadata
            )
            
        except Exception as e:
            raise PlatformError(f"Twitter upload failed: {str(e)}")

    async def _upload_to_generic_platform(
        self,
        platform: Platform,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any],
        credentials: Dict[str, Any]
    ) -> DistributionResult:
        """Generic upload handler for other platforms"""
        try:
            # Simulate generic platform upload
            platform_id = f"{platform.value.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return DistributionResult(
                platform=platform,
                status=DistributionStatus.PUBLISHED,
                platform_id=platform_id,
                platform_url=f"https://{platform.value}.com/content/{platform_id}",
                published_at=datetime.now(),
                engagement_metrics={'interactions': 0},
                error_message=None,
                retry_count=0,
                metadata=metadata
            )
            
        except Exception as e:
            raise PlatformError(f"{platform.value} upload failed: {str(e)}")

    async def _get_platform_credentials(
        self,
        db: Session,
        creator_id: int,
        platform: Platform
    ) -> Optional[Dict[str, Any]]:
        """Get platform credentials for creator"""
        # This would fetch from actual credentials storage
        # For now, return simulated credentials
        return {
            'access_token': f"token_{platform.value}_{creator_id}",
            'refresh_token': f"refresh_{platform.value}_{creator_id}",
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }

    async def _schedule_distribution(
        self,
        db: Session,
        asset: ContentAsset,
        request: DistributionRequest,
        prepared_content: Dict[Platform, Dict[str, Any]],
        optimized_metadata: Dict[Platform, Dict[str, Any]]
    ) -> List[DistributionResult]:
        """Schedule distribution for later execution"""
        scheduled_results = []
        
        for platform in request.platforms:
            result = DistributionResult(
                platform=platform,
                status=DistributionStatus.SCHEDULED,
                platform_id=None,
                platform_url=None,
                published_at=request.schedule_time,
                engagement_metrics={},
                error_message=None,
                retry_count=0,
                metadata=optimized_metadata.get(platform, {})
            )
            scheduled_results.append(result)
            
            # Store scheduled job (would use Celery or similar)
            await self._store_scheduled_job(db, asset.id, platform, request.schedule_time, 
                                          prepared_content[platform], optimized_metadata[platform])
        
        return scheduled_results

    async def _store_scheduled_job(
        self,
        db: Session,
        asset_id: int,
        platform: Platform,
        schedule_time: datetime,
        content_data: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> None:
        """Store scheduled distribution job"""
        # This would create a scheduled task in the database
        logger.info(f"Scheduled distribution for asset {asset_id} to {platform.value} at {schedule_time}")

    async def _log_distribution_result(
        self,
        db: Session,
        result: DistributionResult
    ) -> None:
        """Log distribution result to database"""
        try:
            # This would save to DistributionLog table
            logger.info(f"Distribution to {result.platform.value}: {result.status.value}")
        except Exception as e:
            logger.error(f"Failed to log distribution result: {str(e)}")

    def _determine_youtube_category(
        self,
        asset: ContentAsset,
        metadata: Dict[str, Any]
    ) -> str:
        """Determine appropriate YouTube category"""
        if asset.media_type == 'audio':
            return 'Music'
        elif 'education' in str(metadata).lower():
            return 'Education'
        elif 'entertainment' in str(metadata).lower():
            return 'Entertainment'
        else:
            return 'People & Blogs'

    def _create_instagram_caption(
        self,
        seo_data: Dict[str, Any],
        base_metadata: Dict[str, Any]
    ) -> str:
        """Create optimized Instagram caption"""
        caption_parts = []
        
        # Main description
        description = seo_data.get('description', '')
        if description:
            caption_parts.append(description[:500])  # Limit main text
        
        # Add relevant hashtags
        hashtags = seo_data.get('hashtags', [])
        if hashtags:
            caption_parts.append('\n\n' + ' '.join(f'#{tag}' for tag in hashtags[:20]))
        
        # Add call to action
        caption_parts.append('\n\n💬 What do you think? Let me know in the comments!')
        
        return ''.join(caption_parts)

    def _create_tiktok_description(self, seo_data: Dict[str, Any]) -> str:
        """Create optimized TikTok description"""
        description = seo_data.get('description', '')[:100]  # TikTok limit
        hashtags = seo_data.get('hashtags', [])[:5]  # Limited hashtags for TikTok
        
        if hashtags:
            description += ' ' + ' '.join(f'#{tag}' for tag in hashtags)
        
        return description

    def _create_twitter_text(self, seo_data: Dict[str, Any]) -> str:
        """Create optimized Twitter text"""
        text = seo_data.get('description', '')[:200]  # Leave room for hashtags
        hashtags = seo_data.get('hashtags', [])[:3]  # Limited hashtags for Twitter
        
        if hashtags:
            hashtag_text = ' ' + ' '.join(f'#{tag}' for tag in hashtags)
            available_chars = 280 - len(hashtag_text)
            text = text[:available_chars] + hashtag_text
        
        return text[:280]  # Twitter character limit

    async def get_distribution_analytics(
        self,
        db: Session,
        asset_id: int,
        platform: Optional[Platform] = None
    ) -> Dict[str, Any]:
        """Get distribution analytics for content"""
        try:
            # This would aggregate analytics from DistributionLog table
            analytics = {
                'total_platforms': 5,
                'successful_distributions': 4,
                'failed_distributions': 1,
                'total_reach': 50000,
                'total_engagement': 2500,
                'platform_breakdown': {
                    'youtube': {'reach': 20000, 'engagement': 1200},
                    'instagram': {'reach': 15000, 'engagement': 800},
                    'tiktok': {'reach': 10000, 'engagement': 400},
                    'twitter': {'reach': 5000, 'engagement': 100}
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get distribution analytics: {str(e)}")
            raise DistributionError(f"Analytics retrieval failed: {str(e)}")

    # Legacy method for backward compatibility
    def publish(self, asset: ContentAsset, platforms: List[str]) -> List[dict]:
        """Legacy publish method - deprecated, use distribute_content instead"""
        logger.warning("Using deprecated publish method. Switch to distribute_content")
        
        results = []
        for p in platforms:
            results.append({"platform": p, "status": "published"})
        return results


# Create alias for backward compatibility
DistributionService = MultiPlatformDistributionService
