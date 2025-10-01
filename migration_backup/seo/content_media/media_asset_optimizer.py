"""Media Asset Optimizer
Advanced media asset optimization system for multi-platform content delivery.

Features:
- Image compression/optimization
- Video encoding optimization
- Audio quality enhancement
- Thumbnail generation/optimization
- Cover art optimization
- Social media asset creation
- Multi-format asset generation
- Asset metadata synchronization

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Expertise: Lead Dev IA + Media Engineer + Optimization Expert + DevOps Specialist
"""

import asyncio
import logging
import os
import hashlib
import base64
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import tempfile
import shutil

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
    import cv2
    import numpy as np
    import ffmpeg
    import librosa
    import soundfile as sf
    from pydub import AudioSegment
    from pydub.effects import compress_dynamic_range, normalize
    import mutagen
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4
    from mutagen.flac import FLAC
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
    import webp
    from wand.image import Image as WandImage
    from colorthief import ColorThief
    import tinify  # TinyPNG API
    import io
    import subprocess
    from concurrent.futures import ThreadPoolExecutor
    import asyncio
except ImportError as e:
    logging.warning(f"Optional media optimization dependencies not available: {e}")

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """Media types for optimization."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    THUMBNAIL = "thumbnail"
    COVER_ART = "cover_art"
    LOGO = "logo"
    BANNER = "banner"
    AVATAR = "avatar"


class OptimizationProfile(Enum):
    """Optimization profiles for different use cases."""
    WEB = "web"
    MOBILE = "mobile"
    PRINT = "print"
    SOCIAL_MEDIA = "social_media"
    STREAMING = "streaming"
    ARCHIVE = "archive"
    EMAIL = "email"
    PRESENTATION = "presentation"


class Platform(Enum):
    """Platforms with specific requirements."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    WEBSITE = "website"


class CompressionLevel(Enum):
    """Compression levels."""
    LOSSLESS = "lossless"
    HIGH_QUALITY = "high_quality"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


@dataclass
class MediaAsset:
    """Media asset information."""
    asset_id: str
    file_path: str
    media_type: MediaType
    original_format: str
    file_size: int
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    color_space: Optional[str] = None
    bit_depth: Optional[int] = None
    sample_rate: Optional[int] = None
    bitrate: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    creation_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None


@dataclass
class OptimizationSettings:
    """Optimization settings for media assets."""
    profile: OptimizationProfile
    target_platforms: List[Platform]
    compression_level: CompressionLevel
    max_file_size: Optional[int] = None
    target_dimensions: Optional[Tuple[int, int]] = None
    quality_threshold: float = 0.8
    preserve_metadata: bool = True
    watermark_enabled: bool = False
    watermark_settings: Dict[str, Any] = field(default_factory=dict)
    format_preferences: List[str] = field(default_factory=list)
    color_profile: Optional[str] = None
    enable_progressive: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizedAsset:
    """Optimized media asset result."""
    original_asset: MediaAsset
    optimized_path: str
    optimization_settings: OptimizationSettings
    file_size_reduction: float
    quality_score: float
    compression_ratio: float
    processing_time: float
    format_conversions: List[str]
    metadata_preserved: bool
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    platform_variants: Dict[Platform, str] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchOptimizationResult:
    """Result of batch optimization operation."""
    total_assets: int
    successful_optimizations: int
    failed_optimizations: int
    total_size_reduction: float
    average_quality_score: float
    processing_time: float
    optimized_assets: List[OptimizedAsset]
    errors: List[str] = field(default_factory=list)
    summary_statistics: Dict[str, Any] = field(default_factory=dict)


class MediaAssetOptimizer:
    """Advanced media asset optimization system for multi-platform content delivery.
    
    Provides comprehensive media optimization including compression, format conversion,
    quality enhancement, and platform-specific optimizations.
    """
    
    def __init__(self, 
                 temp_directory: Optional[str] = None,
                 enable_gpu_acceleration: bool = True,
                 enable_cloud_optimization: bool = False,
                 tinify_api_key: Optional[str] = None):
        """Initialize Media Asset Optimizer.
        
        Args:
            temp_directory: Temporary directory for processing
            enable_gpu_acceleration: Enable GPU acceleration for processing
            enable_cloud_optimization: Enable cloud-based optimization services
            tinify_api_key: TinyPNG API key for advanced compression
        """
        self.temp_directory = temp_directory or tempfile.gettempdir()
        self.enable_gpu_acceleration = enable_gpu_acceleration
        self.enable_cloud_optimization = enable_cloud_optimization
        self.tinify_api_key = tinify_api_key
        
        if tinify_api_key:
            try:
                tinify.key = tinify_api_key
                logger.info("TinyPNG API initialized successfully")
            except Exception as e:
                logger.warning(f"TinyPNG API initialization failed: {e}")
        
        # Platform-specific requirements
        self.platform_requirements = {
            Platform.INSTAGRAM: {
                "image": {"max_size": 8 * 1024 * 1024, "formats": ["jpg", "png"], "dimensions": [(1080, 1080), (1080, 1350)]},
                "video": {"max_size": 100 * 1024 * 1024, "formats": ["mp4"], "max_duration": 60}
            },
            Platform.TIKTOK: {
                "video": {"max_size": 4 * 1024 * 1024 * 1024, "formats": ["mp4"], "dimensions": [(1080, 1920)]}
            },
            Platform.YOUTUBE: {
                "video": {"max_size": 128 * 1024 * 1024 * 1024, "formats": ["mp4", "mov", "avi"], "max_duration": None},
                "thumbnail": {"max_size": 2 * 1024 * 1024, "formats": ["jpg", "png"], "dimensions": [(1280, 720)]}
            },
            Platform.SPOTIFY: {
                "audio": {"max_size": 100 * 1024 * 1024, "formats": ["mp3", "flac"], "sample_rate": 44100},
                "cover_art": {"max_size": 10 * 1024 * 1024, "formats": ["jpg"], "dimensions": [(640, 640)]}
            }
        }
        
        # Optimization presets
        self.optimization_presets = {
            OptimizationProfile.WEB: {
                "image": {"quality": 85, "progressive": True, "strip_metadata": False},
                "video": {"crf": 23, "preset": "medium", "profile": "main"},
                "audio": {"bitrate": 128, "sample_rate": 44100}
            },
            OptimizationProfile.MOBILE: {
                "image": {"quality": 80, "progressive": True, "strip_metadata": True},
                "video": {"crf": 25, "preset": "fast", "profile": "baseline"},
                "audio": {"bitrate": 96, "sample_rate": 44100}
            },
            OptimizationProfile.SOCIAL_MEDIA: {
                "image": {"quality": 90, "progressive": True, "strip_metadata": False},
                "video": {"crf": 20, "preset": "medium", "profile": "high"},
                "audio": {"bitrate": 160, "sample_rate": 44100}
            },
            OptimizationProfile.STREAMING: {
                "video": {"crf": 18, "preset": "slow", "profile": "high"},
                "audio": {"bitrate": 320, "sample_rate": 48000}
            }
        }
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("Media Asset Optimizer initialized successfully")
    
    async def optimize_single_asset(self,
                                  asset: MediaAsset,
                                  settings: OptimizationSettings) -> OptimizedAsset:
        """Optimize a single media asset.
        
        Args:
            asset: Media asset to optimize
            settings: Optimization settings
            
        Returns:
            OptimizedAsset with optimization results
        """
        try:
            start_time = datetime.now()
            logger.info(f"Optimizing asset {asset.asset_id} ({asset.media_type.value})")
            
            # Create temporary working directory
            work_dir = os.path.join(self.temp_directory, f"optimize_{asset.asset_id}")
            os.makedirs(work_dir, exist_ok=True)
            
            try:
                # Optimize based on media type
                if asset.media_type == MediaType.IMAGE:
                    optimized_path = await self._optimize_image(asset, settings, work_dir)
                elif asset.media_type == MediaType.VIDEO:
                    optimized_path = await self._optimize_video(asset, settings, work_dir)
                elif asset.media_type == MediaType.AUDIO:
                    optimized_path = await self._optimize_audio(asset, settings, work_dir)
                elif asset.media_type in [MediaType.THUMBNAIL, MediaType.COVER_ART]:
                    optimized_path = await self._optimize_thumbnail(asset, settings, work_dir)
                else:
                    raise ValueError(f"Unsupported media type: {asset.media_type}")
                
                # Calculate optimization metrics
                original_size = os.path.getsize(asset.file_path)
                optimized_size = os.path.getsize(optimized_path)
                size_reduction = ((original_size - optimized_size) / original_size) * 100
                compression_ratio = original_size / optimized_size
                
                # Calculate quality score
                quality_score = await self._calculate_quality_score(
                    asset.file_path, optimized_path, asset.media_type
                )
                
                # Generate platform variants
                platform_variants = await self._generate_platform_variants(
                    optimized_path, asset, settings
                )
                
                # Generate recommendations
                recommendations = self._generate_optimization_recommendations(
                    asset, settings, size_reduction, quality_score
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                result = OptimizedAsset(
                    original_asset=asset,
                    optimized_path=optimized_path,
                    optimization_settings=settings,
                    file_size_reduction=size_reduction,
                    quality_score=quality_score,
                    compression_ratio=compression_ratio,
                    processing_time=processing_time,
                    format_conversions=[],
                    metadata_preserved=settings.preserve_metadata,
                    recommendations=recommendations,
                    platform_variants=platform_variants,
                    performance_metrics={
                        "original_size": original_size,
                        "optimized_size": optimized_size,
                        "compression_efficiency": size_reduction / processing_time
                    }
                )
                
                logger.info(f"Asset {asset.asset_id} optimized successfully")
                return result
                
            finally:
                # Cleanup temporary files (optional - keep for debugging)
                # shutil.rmtree(work_dir, ignore_errors=True)
                pass
                
        except Exception as e:
            logger.error(f"Error optimizing asset {asset.asset_id}: {e}")
            raise
    
    async def optimize_batch(self,
                           assets: List[MediaAsset],
                           settings: OptimizationSettings,
                           max_concurrent: int = 4) -> BatchOptimizationResult:
        """Optimize multiple assets in batch.
        
        Args:
            assets: List of media assets to optimize
            settings: Optimization settings
            max_concurrent: Maximum concurrent optimizations
            
        Returns:
            BatchOptimizationResult with batch optimization results
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting batch optimization of {len(assets)} assets")
            
            optimized_assets = []
            errors = []
            
            # Process assets in batches
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def optimize_with_semaphore(asset):
                async with semaphore:
                    try:
                        return await self.optimize_single_asset(asset, settings)
                    except Exception as e:
                        errors.append(f"Asset {asset.asset_id}: {str(e)}")
                        return None
            
            # Run optimizations concurrently
            results = await asyncio.gather(
                *[optimize_with_semaphore(asset) for asset in assets],
                return_exceptions=True
            )
            
            # Collect successful results
            for result in results:
                if isinstance(result, OptimizedAsset):
                    optimized_assets.append(result)
                elif isinstance(result, Exception):
                    errors.append(str(result))
            
            # Calculate summary statistics
            total_size_reduction = 0
            total_quality = 0
            
            if optimized_assets:
                total_size_reduction = sum(asset.file_size_reduction for asset in optimized_assets)
                total_quality = sum(asset.quality_score for asset in optimized_assets)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = BatchOptimizationResult(
                total_assets=len(assets),
                successful_optimizations=len(optimized_assets),
                failed_optimizations=len(errors),
                total_size_reduction=total_size_reduction,
                average_quality_score=total_quality / len(optimized_assets) if optimized_assets else 0,
                processing_time=processing_time,
                optimized_assets=optimized_assets,
                errors=errors,
                summary_statistics={
                    "success_rate": len(optimized_assets) / len(assets) * 100,
                    "average_processing_time": processing_time / len(assets),
                    "total_size_saved": sum(
                        asset.original_asset.file_size * (asset.file_size_reduction / 100)
                        for asset in optimized_assets
                    )
                }
            )
            
            logger.info(f"Batch optimization completed: {len(optimized_assets)}/{len(assets)} successful")
            return result
            
        except Exception as e:
            logger.error(f"Error in batch optimization: {e}")
            raise
    
    async def create_platform_variants(self,
                                     asset: MediaAsset,
                                     target_platforms: List[Platform]) -> Dict[Platform, OptimizedAsset]:
        """Create optimized variants for specific platforms.
        
        Args:
            asset: Source media asset
            target_platforms: List of target platforms
            
        Returns:
            Dictionary mapping platforms to optimized assets
        """
        try:
            variants = {}
            
            for platform in target_platforms:
                # Get platform-specific requirements
                platform_reqs = self.platform_requirements.get(platform, {})
                media_reqs = platform_reqs.get(asset.media_type.value, {})
                
                if not media_reqs:
                    logger.warning(f"No requirements defined for {asset.media_type.value} on {platform.value}")
                    continue
                
                # Create platform-specific optimization settings
                platform_settings = OptimizationSettings(
                    profile=OptimizationProfile.SOCIAL_MEDIA,
                    target_platforms=[platform],
                    compression_level=CompressionLevel.BALANCED,
                    max_file_size=media_reqs.get("max_size"),
                    target_dimensions=media_reqs.get("dimensions", [None])[0],
                    format_preferences=media_reqs.get("formats", [])
                )
                
                # Optimize for platform
                optimized = await self.optimize_single_asset(asset, platform_settings)
                variants[platform] = optimized
            
            return variants
            
        except Exception as e:
            logger.error(f"Error creating platform variants: {e}")
            return {}
    
    # Private optimization methods
    
    async def _optimize_image(self,
                            asset: MediaAsset,
                            settings: OptimizationSettings,
                            work_dir: str) -> str:
        """Optimize image asset."""
        try:
            # Load image
            with Image.open(asset.file_path) as img:
                # Convert to RGB if necessary
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')
                
                # Resize if target dimensions specified
                if settings.target_dimensions:
                    target_width, target_height = settings.target_dimensions
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Apply enhancement based on settings
                if settings.profile == OptimizationProfile.WEB:
                    # Web optimization: balance quality and size
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.1)
                
                elif settings.profile == OptimizationProfile.MOBILE:
                    # Mobile optimization: smaller size, acceptable quality
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.05)
                
                # Apply watermark if enabled
                if settings.watermark_enabled:
                    img = self._apply_watermark(img, settings.watermark_settings)
                
                # Determine output format
                output_format = self._determine_output_format(
                    asset.original_format, settings.format_preferences, "image"
                )
                
                # Set compression parameters
                compression_params = self._get_compression_parameters(
                    settings.compression_level, output_format, "image"
                )
                
                # Save optimized image
                output_filename = f"optimized_{asset.asset_id}.{output_format}"
                output_path = os.path.join(work_dir, output_filename)
                
                img.save(output_path, format=output_format.upper(), **compression_params)
                
                # Advanced compression with TinyPNG if available
                if self.enable_cloud_optimization and self.tinify_api_key and output_format in ['jpg', 'png']:
                    output_path = await self._apply_tinify_compression(output_path)
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            raise
    
    async def _optimize_video(self,
                            asset: MediaAsset,
                            settings: OptimizationSettings,
                            work_dir: str) -> str:
        """Optimize video asset."""
        try:
            # Determine output format
            output_format = self._determine_output_format(
                asset.original_format, settings.format_preferences, "video"
            )
            
            # Get video optimization parameters
            video_params = self._get_video_optimization_parameters(settings)
            
            # Build FFmpeg command
            output_filename = f"optimized_{asset.asset_id}.{output_format}"
            output_path = os.path.join(work_dir, output_filename)
            
            # FFmpeg optimization
            input_stream = ffmpeg.input(asset.file_path)
            
            # Apply video filters
            video_stream = input_stream.video
            
            # Resize if target dimensions specified
            if settings.target_dimensions:
                width, height = settings.target_dimensions
                video_stream = video_stream.filter('scale', width, height)
            
            # Apply platform-specific optimizations
            if Platform.TIKTOK in settings.target_platforms:
                # TikTok optimization: vertical format, high engagement
                video_stream = video_stream.filter('scale', 1080, 1920)
            elif Platform.YOUTUBE in settings.target_platforms:
                # YouTube optimization: high quality, various formats
                video_params['crf'] = 18
            
            # Output with optimization parameters
            output_stream = ffmpeg.output(
                video_stream,
                input_stream.audio,
                output_path,
                **video_params
            )
            
            # Run FFmpeg
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error optimizing video: {e}")
            raise
    
    async def _optimize_audio(self,
                            asset: MediaAsset,
                            settings: OptimizationSettings,
                            work_dir: str) -> str:
        """Optimize audio asset."""
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(asset.file_path, sr=None)
            
            # Apply audio processing based on settings
            if settings.profile == OptimizationProfile.STREAMING:
                # High-quality streaming: minimal processing
                target_sample_rate = 48000
                target_bitrate = 320
            elif settings.profile == OptimizationProfile.MOBILE:
                # Mobile optimization: lower bitrate
                target_sample_rate = 44100
                target_bitrate = 128
            else:
                # Default web optimization
                target_sample_rate = 44100
                target_bitrate = 192
            
            # Resample if necessary
            if sample_rate != target_sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=target_sample_rate)
                sample_rate = target_sample_rate
            
            # Apply audio enhancements
            if settings.compression_level != CompressionLevel.LOSSLESS:
                # Normalize audio
                audio_data = librosa.util.normalize(audio_data)
                
                # Apply dynamic range compression
                # (Simplified - would use more sophisticated processing)
                audio_data = np.tanh(audio_data * 0.7)
            
            # Determine output format
            output_format = self._determine_output_format(
                asset.original_format, settings.format_preferences, "audio"
            )
            
            # Save optimized audio
            output_filename = f"optimized_{asset.asset_id}.{output_format}"
            output_path = os.path.join(work_dir, output_filename)
            
            if output_format == 'mp3':
                # Convert to MP3 using pydub
                audio_segment = AudioSegment(
                    audio_data.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,  # 16-bit
                    channels=1 if len(audio_data.shape) == 1 else audio_data.shape[1]
                )
                audio_segment.export(output_path, format="mp3", bitrate=f"{target_bitrate}k")
            else:
                # Save as high-quality format
                sf.write(output_path, audio_data, sample_rate, format=output_format.upper())
            
            # Preserve metadata if requested
            if settings.preserve_metadata:
                await self._preserve_audio_metadata(asset.file_path, output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error optimizing audio: {e}")
            raise
    
    async def _optimize_thumbnail(self,
                                asset: MediaAsset,
                                settings: OptimizationSettings,
                                work_dir: str) -> str:
        """Optimize thumbnail/cover art."""
        try:
            with Image.open(asset.file_path) as img:
                # Ensure square aspect ratio for cover art
                if asset.media_type == MediaType.COVER_ART:
                    # Make square
                    size = min(img.size)
                    img = img.crop((
                        (img.width - size) // 2,
                        (img.height - size) // 2,
                        (img.width + size) // 2,
                        (img.height + size) // 2
                    ))
                
                # Resize to target dimensions
                if settings.target_dimensions:
                    img = img.resize(settings.target_dimensions, Image.Resampling.LANCZOS)
                else:
                    # Default thumbnail size
                    default_size = (640, 640) if asset.media_type == MediaType.COVER_ART else (1280, 720)
                    img = img.resize(default_size, Image.Resampling.LANCZOS)
                
                # Enhance for thumbnail display
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.1)
                
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.05)
                
                # Save optimized thumbnail
                output_format = "jpg"  # Thumbnails typically use JPEG
                output_filename = f"optimized_{asset.asset_id}.{output_format}"
                output_path = os.path.join(work_dir, output_filename)
                
                img.save(output_path, format="JPEG", quality=90, optimize=True)
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error optimizing thumbnail: {e}")
            raise
    
    # Helper methods
    
    def _determine_output_format(self,
                               original_format: str,
                               format_preferences: List[str],
                               media_type: str) -> str:
        """Determine optimal output format."""
        if format_preferences:
            return format_preferences[0]
        
        # Default format recommendations
        format_defaults = {
            "image": "jpg",
            "video": "mp4", 
            "audio": "mp3"
        }
        
        return format_defaults.get(media_type, original_format.lower())
    
    def _get_compression_parameters(self,
                                  compression_level: CompressionLevel,
                                  output_format: str,
                                  media_type: str) -> Dict[str, Any]:
        """Get compression parameters for format."""
        params = {}
        
        if media_type == "image":
            quality_map = {
                CompressionLevel.LOSSLESS: 100,
                CompressionLevel.HIGH_QUALITY: 95,
                CompressionLevel.BALANCED: 85,
                CompressionLevel.AGGRESSIVE: 75,
                CompressionLevel.MAXIMUM: 60
            }
            
            if output_format.lower() in ['jpg', 'jpeg']:
                params['quality'] = quality_map[compression_level]
                params['optimize'] = True
                params['progressive'] = True
            elif output_format.lower() == 'png':
                params['optimize'] = True
                if compression_level in [CompressionLevel.AGGRESSIVE, CompressionLevel.MAXIMUM]:
                    params['compress_level'] = 9
        
        return params
    
    def _get_video_optimization_parameters(self, settings: OptimizationSettings) -> Dict[str, Any]:
        """Get video optimization parameters."""
        preset_params = self.optimization_presets.get(settings.profile, {}).get("video", {})
        
        # Default video parameters
        params = {
            'vcodec': 'libx264',
            'acodec': 'aac',
            'crf': preset_params.get('crf', 23),
            'preset': preset_params.get('preset', 'medium'),
            'profile:v': preset_params.get('profile', 'main'),
            'movflags': 'faststart'  # Web optimization
        }
        
        # GPU acceleration if enabled
        if self.enable_gpu_acceleration:
            params['vcodec'] = 'h264_nvenc'  # NVIDIA GPU encoding
        
        return params
    
    def _apply_watermark(self, img: Image.Image, watermark_settings: Dict[str, Any]) -> Image.Image:
        """Apply watermark to image."""
        try:
            # Simple text watermark implementation
            watermark_text = watermark_settings.get('text', '© IA Chéries')
            opacity = watermark_settings.get('opacity', 0.5)
            position = watermark_settings.get('position', 'bottom-right')
            
            # Create watermark
            watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # Use default font (would use custom font in production)
            try:
                font_size = min(img.size) // 30
                font = ImageFont.load_default()
            except:
                font = None
            
            # Calculate position
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            if position == 'bottom-right':
                x = img.width - text_width - 20
                y = img.height - text_height - 20
            elif position == 'bottom-left':
                x = 20
                y = img.height - text_height - 20
            else:  # center
                x = (img.width - text_width) // 2
                y = (img.height - text_height) // 2
            
            # Draw watermark
            color = (*watermark_settings.get('color', (255, 255, 255)), int(255 * opacity))
            draw.text((x, y), watermark_text, font=font, fill=color)
            
            # Composite watermark onto image
            img = Image.alpha_composite(img.convert('RGBA'), watermark)
            return img.convert('RGB')
            
        except Exception as e:
            logger.warning(f"Failed to apply watermark: {e}")
            return img
    
    async def _apply_tinify_compression(self, image_path: str) -> str:
        """Apply TinyPNG compression."""
        try:
            source = tinify.from_file(image_path)
            source.to_file(image_path)  # Overwrite with compressed version
            return image_path
        except Exception as e:
            logger.warning(f"TinyPNG compression failed: {e}")
            return image_path
    
    async def _calculate_quality_score(self,
                                     original_path: str,
                                     optimized_path: str,
                                     media_type: MediaType) -> float:
        """Calculate quality score comparing original and optimized assets."""
        try:
            if media_type == MediaType.IMAGE:
                return await self._calculate_image_quality_score(original_path, optimized_path)
            elif media_type == MediaType.VIDEO:
                return await self._calculate_video_quality_score(original_path, optimized_path)
            elif media_type == MediaType.AUDIO:
                return await self._calculate_audio_quality_score(original_path, optimized_path)
            else:
                return 0.8  # Default quality score
                
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {e}")
            return 0.75  # Default fallback
    
    async def _calculate_image_quality_score(self, original_path: str, optimized_path: str) -> float:
        """Calculate image quality score using SSIM or similar metrics."""
        try:
            # Load images
            original = cv2.imread(original_path)
            optimized = cv2.imread(optimized_path)
            
            if original is None or optimized is None:
                return 0.75
            
            # Resize to same dimensions if different
            if original.shape != optimized.shape:
                optimized = cv2.resize(optimized, (original.shape[1], original.shape[0]))
            
            # Calculate SSIM (simplified version)
            # In production, would use scikit-image's structural_similarity
            original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            optimized_gray = cv2.cvtColor(optimized, cv2.COLOR_BGR2GRAY)
            
            # Simple correlation coefficient as quality metric
            correlation = cv2.matchTemplate(original_gray, optimized_gray, cv2.TM_CCOEFF_NORMED)[0][0]
            
            return max(0.0, min(1.0, correlation))
            
        except Exception as e:
            logger.warning(f"Image quality calculation failed: {e}")
            return 0.75
    
    async def _generate_platform_variants(self,
                                        optimized_path: str,
                                        original_asset: MediaAsset,
                                        settings: OptimizationSettings) -> Dict[Platform, str]:
        """Generate platform-specific variants."""
        variants = {}
        
        for platform in settings.target_platforms:
            try:
                # Create platform-specific version
                platform_settings = OptimizationSettings(
                    profile=OptimizationProfile.SOCIAL_MEDIA,
                    target_platforms=[platform],
                    compression_level=settings.compression_level
                )
                
                # For now, return the same optimized path
                # In production, would create platform-specific variants
                variants[platform] = optimized_path
                
            except Exception as e:
                logger.warning(f"Failed to create variant for {platform.value}: {e}")
        
        return variants
    
    def _generate_optimization_recommendations(self,
                                             asset: MediaAsset,
                                             settings: OptimizationSettings,
                                             size_reduction: float,
                                             quality_score: float) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if size_reduction < 10:
            recommendations.append("Consider more aggressive compression for better size reduction")
        
        if quality_score < 0.7:
            recommendations.append("Quality loss detected - consider adjusting compression settings")
        
        if asset.file_size > 10 * 1024 * 1024:  # 10MB
            recommendations.append("Large file size - consider additional compression or format conversion")
        
        if not settings.format_preferences:
            recommendations.append("Specify format preferences for better optimization results")
        
        return recommendations
    
    # Additional helper methods would be implemented here...
    
    async def _preserve_audio_metadata(self, original_path: str, optimized_path: str) -> None:
        """Preserve audio metadata in optimized file."""
        try:
            # Copy metadata from original to optimized file
            original_file = mutagen.File(original_path)
            optimized_file = mutagen.File(optimized_path)
            
            if original_file and optimized_file:
                # Copy tags
                if hasattr(original_file, 'tags') and original_file.tags:
                    for key, value in original_file.tags.items():
                        if hasattr(optimized_file, 'tags'):
                            optimized_file.tags[key] = value
                
                optimized_file.save()
                
        except Exception as e:
            logger.warning(f"Failed to preserve audio metadata: {e}")
    
    async def _calculate_video_quality_score(self, original_path: str, optimized_path: str) -> float:
        """Calculate video quality score."""
        # Simplified implementation - would use VMAF or similar in production
        return 0.85
    
    async def _calculate_audio_quality_score(self, original_path: str, optimized_path: str) -> float:
        """Calculate audio quality score."""
        # Simplified implementation - would use PESQ or similar in production
        return 0.80