"""Format Converter

Universal multi-format conversion engine supporting audio, video, and image formats
with platform-specific optimizations and intelligent format selection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import tempfile
import os

from .audio_processor import AudioProcessor, AudioFormat
from .video_processor import VideoProcessor, VideoFormat
from .image_optimizer import ImageOptimizer, ImageFormat

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """Media types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"


class Platform(Enum):
    """Target platforms"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    WEB = "web"
    MOBILE = "mobile"


@dataclass
class ConversionConfig:
    """Format conversion configuration"""
    target_format: str
    quality: str = "high"
    optimize_for_platform: Optional[Platform] = None
    max_file_size: Optional[int] = None
    custom_params: Optional[Dict[str, Any]] = None


@dataclass
class ConversionResult:
    """Format conversion result"""
    success: bool
    converted_data: Optional[bytes]
    source_format: str
    target_format: str
    media_type: MediaType
    processing_time: float
    file_size_reduction: float
    platform_optimized: bool
    conversion_details: Dict[str, Any]
    error: Optional[str] = None


class FormatConverter:
    """Universal multi-format conversion engine"""
    
    def __init__(self):
        """Initialize format converter"""
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.image_optimizer = ImageOptimizer()
        
        # Platform-specific configurations
        self._platform_configs = self._initialize_platform_configs()
        
        # Format detection mappings
        self._format_mappings = {
            # Audio formats
            'mp3': MediaType.AUDIO,
            'wav': MediaType.AUDIO,
            'flac': MediaType.AUDIO,
            'aac': MediaType.AUDIO,
            'ogg': MediaType.AUDIO,
            'm4a': MediaType.AUDIO,
            
            # Video formats
            'mp4': MediaType.VIDEO,
            'avi': MediaType.VIDEO,
            'mov': MediaType.VIDEO,
            'mkv': MediaType.VIDEO,
            'webm': MediaType.VIDEO,
            'flv': MediaType.VIDEO,
            
            # Image formats
            'jpg': MediaType.IMAGE,
            'jpeg': MediaType.IMAGE,
            'png': MediaType.IMAGE,
            'webp': MediaType.IMAGE,
            'tiff': MediaType.IMAGE,
            'bmp': MediaType.IMAGE,
            'heic': MediaType.IMAGE
        }
    
    async def convert_media(self,
                          media_data: Union[bytes, BinaryIO],
                          source_format: str,
                          target_format: str,
                          config: Optional[ConversionConfig] = None) -> ConversionResult:
        """
        Convert media from one format to another
        
        Args:
            media_data: Input media data
            source_format: Source format (e.g., 'mp4', 'jpg')
            target_format: Target format (e.g., 'webm', 'png')
            config: Conversion configuration
            
        Returns:
            Conversion result
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            if config is None:
                config = ConversionConfig(target_format=target_format)
            
            # Detect media type
            source_media_type = self._detect_media_type(source_format)
            target_media_type = self._detect_media_type(target_format)
            
            if source_media_type != target_media_type:
                raise ValueError(f"Cannot convert between different media types: {source_media_type} to {target_media_type}")
            
            # Get input data
            if isinstance(media_data, bytes):
                input_bytes = media_data
            else:
                input_bytes = media_data.read()
                media_data.seek(0)
            
            # Apply platform optimization if specified
            if config.optimize_for_platform:
                config = self._apply_platform_optimization(config, source_media_type)
            
            # Perform conversion based on media type
            if source_media_type == MediaType.AUDIO:
                result = await self._convert_audio(input_bytes, source_format, target_format, config)
            elif source_media_type == MediaType.VIDEO:
                result = await self._convert_video(input_bytes, source_format, target_format, config)
            elif source_media_type == MediaType.IMAGE:
                result = await self._convert_image(input_bytes, source_format, target_format, config)
            else:
                raise ValueError(f"Unsupported media type: {source_media_type}")
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate file size reduction
            if result['success'] and result['converted_data']:
                original_size = len(input_bytes)
                converted_size = len(result['converted_data'])
                size_reduction = ((original_size - converted_size) / original_size) * 100
            else:
                size_reduction = 0
            
            return ConversionResult(
                success=result['success'],
                converted_data=result.get('converted_data'),
                source_format=source_format,
                target_format=target_format,
                media_type=source_media_type,
                processing_time=processing_time,
                file_size_reduction=size_reduction,
                platform_optimized=config.optimize_for_platform is not None,
                conversion_details=result.get('details', {}),
                error=result.get('error')
            )
            
        except Exception as e:
            logger.error(f"Media conversion failed: {e}")
            return ConversionResult(
                success=False,
                converted_data=None,
                source_format=source_format,
                target_format=target_format,
                media_type=MediaType.AUDIO,  # Default
                processing_time=0,
                file_size_reduction=0,
                platform_optimized=False,
                conversion_details={},
                error=str(e)
            )
    
    async def auto_convert_for_platform(self,
                                      media_data: Union[bytes, BinaryIO],
                                      source_format: str,
                                      platform: Platform) -> ConversionResult:
        """
        Automatically convert media optimized for specific platform
        
        Args:
            media_data: Input media data
            source_format: Source format
            platform: Target platform
            
        Returns:
            Platform-optimized conversion result
        """
        try:
            media_type = self._detect_media_type(source_format)
            
            # Get platform-specific target format
            platform_config = self._platform_configs.get(platform, {})
            media_config = platform_config.get(media_type.value, {})
            
            if not media_config:
                raise ValueError(f"No configuration available for {media_type.value} on {platform.value}")
            
            target_format = media_config['format']
            
            # Create conversion config
            config = ConversionConfig(
                target_format=target_format,
                quality=media_config.get('quality', 'high'),
                optimize_for_platform=platform,
                max_file_size=media_config.get('max_file_size'),
                custom_params=media_config.get('params', {})
            )
            
            return await self.convert_media(media_data, source_format, target_format, config)
            
        except Exception as e:
            logger.error(f"Platform conversion failed: {e}")
            return ConversionResult(
                success=False,
                converted_data=None,
                source_format=source_format,
                target_format="",
                media_type=MediaType.AUDIO,
                processing_time=0,
                file_size_reduction=0,
                platform_optimized=True,
                conversion_details={},
                error=str(e)
            )
    
    async def batch_convert(self,
                          media_files: List[Dict[str, Any]],
                          target_format: str,
                          config: Optional[ConversionConfig] = None) -> List[ConversionResult]:
        """
        Convert multiple media files in batch
        
        Args:
            media_files: List of media files with metadata
            target_format: Target format for all files
            config: Conversion configuration
            
        Returns:
            List of conversion results
        """
        tasks = []
        
        for media_file in media_files:
            task = self.convert_media(
                media_file['data'],
                media_file['source_format'],
                target_format,
                config
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = ConversionResult(
                    success=False,
                    converted_data=None,
                    source_format=media_files[i].get('source_format', ''),
                    target_format=target_format,
                    media_type=MediaType.AUDIO,
                    processing_time=0,
                    file_size_reduction=0,
                    platform_optimized=False,
                    conversion_details={},
                    error=str(result)
                )
        
        return results
    
    async def _convert_audio(self,
                           audio_data: bytes,
                           source_format: str,
                           target_format: str,
                           config: ConversionConfig) -> Dict[str, Any]:
        """Convert audio format"""
        try:
            # Map target format to AudioFormat enum
            audio_format_map = {
                'mp3': AudioFormat.MP3,
                'wav': AudioFormat.WAV,
                'flac': AudioFormat.FLAC,
                'aac': AudioFormat.AAC,
                'ogg': AudioFormat.OGG,
                'm4a': AudioFormat.M4A
            }
            
            target_audio_format = audio_format_map.get(target_format.lower())
            if not target_audio_format:
                raise ValueError(f"Unsupported audio format: {target_format}")
            
            # Use audio processor for conversion
            from .audio_processor import ProcessingMode, QualityLevel
            
            quality_map = {
                'draft': QualityLevel.DRAFT,
                'standard': QualityLevel.STANDARD,
                'high': QualityLevel.HIGH,
                'studio': QualityLevel.STUDIO,
                'lossless': QualityLevel.LOSSLESS
            }
            
            quality_level = quality_map.get(config.quality, QualityLevel.HIGH)
            
            result = await self.audio_processor.process_audio(
                audio_data,
                ProcessingMode.ENHANCE,
                target_audio_format,
                quality_level,
                config.custom_params
            )
            
            return {
                'success': result.success,
                'converted_data': result.processed_audio,
                'details': {
                    'processing_time': result.processing_time,
                    'enhancements': result.enhancement_applied,
                    'quality_metrics': result.quality_metrics.__dict__
                },
                'error': result.error
            }
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _convert_video(self,
                           video_data: bytes,
                           source_format: str,
                           target_format: str,
                           config: ConversionConfig) -> Dict[str, Any]:
        """Convert video format"""
        try:
            # Map target format to VideoFormat enum
            video_format_map = {
                'mp4': VideoFormat.MP4,
                'avi': VideoFormat.AVI,
                'mov': VideoFormat.MOV,
                'mkv': VideoFormat.MKV,
                'webm': VideoFormat.WEBM,
                'flv': VideoFormat.FLV
            }
            
            target_video_format = video_format_map.get(target_format.lower())
            if not target_video_format:
                raise ValueError(f"Unsupported video format: {target_format}")
            
            # Use video processor for conversion
            from .video_processor import ProcessingMode
            
            result = await self.video_processor.process_video(
                video_data,
                ProcessingMode.COMPRESS,
                target_video_format,
                custom_params=config.custom_params
            )
            
            return {
                'success': result.success,
                'converted_data': result.processed_video,
                'details': {
                    'processing_time': result.processing_time,
                    'enhancements': result.enhancement_applied,
                    'quality_metrics': result.quality_metrics.__dict__,
                    'frames_processed': result.frames_processed
                },
                'error': result.error
            }
            
        except Exception as e:
            logger.error(f"Video conversion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _convert_image(self,
                           image_data: bytes,
                           source_format: str,
                           target_format: str,
                           config: ConversionConfig) -> Dict[str, Any]:
        """Convert image format"""
        try:
            # Map target format to ImageFormat enum
            image_format_map = {
                'jpg': ImageFormat.JPEG,
                'jpeg': ImageFormat.JPEG,
                'png': ImageFormat.PNG,
                'webp': ImageFormat.WEBP,
                'tiff': ImageFormat.TIFF,
                'bmp': ImageFormat.BMP,
                'heic': ImageFormat.HEIC
            }
            
            target_image_format = image_format_map.get(target_format.lower())
            if not target_image_format:
                raise ValueError(f"Unsupported image format: {target_format}")
            
            # Use image optimizer for conversion
            from .image_optimizer import OptimizationMode
            
            # Determine optimization mode based on platform
            if config.optimize_for_platform:
                if config.optimize_for_platform in [Platform.WEB, Platform.MOBILE]:
                    opt_mode = OptimizationMode.WEB
                else:
                    opt_mode = OptimizationMode.BALANCED
            else:
                opt_mode = OptimizationMode.QUALITY
            
            result = await self.image_optimizer.optimize_image(
                image_data,
                opt_mode,
                target_image_format,
                config.max_file_size,
                config.custom_params
            )
            
            return {
                'success': result.success,
                'converted_data': result.optimized_image,
                'details': {
                    'processing_time': result.processing_time,
                    'optimizations': result.optimization_applied,
                    'quality_metrics': result.quality_metrics.__dict__
                },
                'error': result.error
            }
            
        except Exception as e:
            logger.error(f"Image conversion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_media_type(self, format_str: str) -> MediaType:
        """Detect media type from format string"""
        format_lower = format_str.lower().strip('.')
        
        media_type = self._format_mappings.get(format_lower)
        if not media_type:
            raise ValueError(f"Unknown format: {format_str}")
        
        return media_type
    
    def _apply_platform_optimization(self,
                                   config: ConversionConfig,
                                   media_type: MediaType) -> ConversionConfig:
        """Apply platform-specific optimizations to config"""
        platform_config = self._platform_configs.get(config.optimize_for_platform, {})
        media_config = platform_config.get(media_type.value, {})
        
        if media_config:
            # Update config with platform-specific settings
            if 'quality' in media_config:
                config.quality = media_config['quality']
            
            if 'max_file_size' in media_config:
                config.max_file_size = media_config['max_file_size']
            
            if 'params' in media_config:
                if config.custom_params:
                    config.custom_params.update(media_config['params'])
                else:
                    config.custom_params = media_config['params'].copy()
        
        return config
    
    def _initialize_platform_configs(self) -> Dict[Platform, Dict[str, Any]]:
        """Initialize platform-specific configurations"""
        return {
            Platform.YOUTUBE: {
                'video': {
                    'format': 'mp4',
                    'quality': 'high',
                    'max_file_size': 128 * 1024 * 1024 * 1024,  # 128 GB
                    'params': {
                        'bitrate': '8M',
                        'fps': 30,
                        'codec': 'h264'
                    }
                },
                'audio': {
                    'format': 'mp3',
                    'quality': 'high',
                    'max_file_size': 512 * 1024 * 1024,  # 512 MB
                    'params': {
                        'bitrate': '320k'
                    }
                },
                'image': {
                    'format': 'jpg',
                    'quality': 'high',
                    'max_file_size': 2 * 1024 * 1024,  # 2 MB
                    'params': {
                        'max_width': 1280
                    }
                }
            },
            Platform.INSTAGRAM: {
                'video': {
                    'format': 'mp4',
                    'quality': 'high',
                    'max_file_size': 4 * 1024 * 1024 * 1024,  # 4 GB
                    'params': {
                        'bitrate': '3.5M',
                        'fps': 30
                    }
                },
                'audio': {
                    'format': 'mp3',
                    'quality': 'standard',
                    'max_file_size': 100 * 1024 * 1024,  # 100 MB
                    'params': {
                        'bitrate': '192k'
                    }
                },
                'image': {
                    'format': 'jpg',
                    'quality': 'high',
                    'max_file_size': 8 * 1024 * 1024,  # 8 MB
                    'params': {
                        'max_width': 1080
                    }
                }
            },
            Platform.TIKTOK: {
                'video': {
                    'format': 'mp4',
                    'quality': 'standard',
                    'max_file_size': 287 * 1024 * 1024,  # 287 MB
                    'params': {
                        'bitrate': '2M',
                        'fps': 30
                    }
                }
            },
            Platform.WEB: {
                'video': {
                    'format': 'webm',
                    'quality': 'balanced',
                    'params': {
                        'bitrate': '1.5M'
                    }
                },
                'audio': {
                    'format': 'ogg',
                    'quality': 'standard',
                    'params': {
                        'bitrate': '128k'
                    }
                },
                'image': {
                    'format': 'webp',
                    'quality': 'balanced',
                    'params': {
                        'max_width': 1920,
                        'quality': 80
                    }
                }
            }
        }
    
    def get_supported_formats(self, media_type: MediaType) -> List[str]:
        """Get list of supported formats for media type"""
        formats = []
        
        for format_ext, format_media_type in self._format_mappings.items():
            if format_media_type == media_type:
                formats.append(format_ext)
        
        return sorted(formats)
    
    def get_platform_recommendations(self, platform: Platform) -> Dict[str, Any]:
        """Get format recommendations for a platform"""
        return self._platform_configs.get(platform, {})
    
    def estimate_conversion_time(self,
                               file_size: int,
                               source_format: str,
                               target_format: str) -> float:
        """Estimate conversion time in seconds"""
        # Simple estimation based on file size and complexity
        media_type = self._detect_media_type(source_format)
        
        # Base processing time per MB
        time_per_mb = {
            MediaType.AUDIO: 0.1,  # 0.1 seconds per MB
            MediaType.VIDEO: 2.0,  # 2 seconds per MB
            MediaType.IMAGE: 0.05  # 0.05 seconds per MB
        }
        
        file_size_mb = file_size / (1024 * 1024)
        base_time = file_size_mb * time_per_mb.get(media_type, 1.0)
        
        # Complexity multiplier for certain conversions
        complexity_multiplier = 1.0
        
        if media_type == MediaType.VIDEO:
            if target_format in ['webm', 'av1']:
                complexity_multiplier = 2.0  # More complex encoding
        
        return base_time * complexity_multiplier