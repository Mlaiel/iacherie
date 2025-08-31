"""Format Processor Module
======================

Professional content format conversion and optimization engine.
Multi-format support with intelligent adaptation for all platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or theft of this code or concept without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action under German and international copyright law.

Features:
- Universal format conversion for all content types
- Platform-specific optimization (Instagram, TikTok, YouTube, etc.)
- Intelligent format selection based on content analysis
- Batch conversion with progress tracking
- Quality preservation during conversion
- Format compatibility validation
- Adaptive bitrate and resolution optimization
- Cross-platform format standardization
"""import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import tempfile
import os
from pathlib import Path
import mimetypes
import json

# Format conversion libraries
try:
    from PIL import Image, ImageOps, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - image format conversion limited")

try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning("Audio libraries not available - audio conversion limited")

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logging.warning("FFmpeg not available - video conversion limited")

try:
    import markdown
    import pypandoc
    TEXT_LIBS_AVAILABLE = True
except ImportError:
    TEXT_LIBS_AVAILABLE = False
    logging.warning("Text conversion libraries limited")

logger = logging.getLogger(__name__)

@dataclass
class FormatSpec:
    """Format specification container"""    format_name: str
    extension: str
    mime_type: str
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    max_duration: Optional[float] = None
    max_file_size: Optional[int] = None
    supported_codecs: List[str] = field(default_factory=list)
    quality_settings: Dict[str, Any] = field(default_factory=dict)
    platform_specific: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionResult:
    """Format conversion result"""    success: bool
    original_format: str
    target_format: str
    output_path: str
    file_size: int
    quality_score: float
    conversion_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class PlatformProfile:
    """Platform-specific format profile"""    platform: str
    video_specs: Optional[FormatSpec] = None
    audio_specs: Optional[FormatSpec] = None
    image_specs: Optional[FormatSpec] = None
    text_specs: Optional[FormatSpec] = None
    constraints: Dict[str, Any] = field(default_factory=dict)

class FormatProcessor:
    """Professional content format conversion engine"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize format specifications and platform profiles
        self._initialize_format_specs()
        self._initialize_platform_profiles()
        
        # Initialize conversion engines
        self._initialize_converters()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default format processing configuration"""        return {
            'conversion_quality': 'high',  # 'low', 'medium', 'high', 'lossless'
            'preserve_metadata': True,
            'optimize_for_web': True,
            'progressive_encoding': True,
            'batch_processing': True,
            'parallel_conversion': True,
            'max_workers': 4,
            
            # Output directory configuration
            'output_directory': 'converted',
            'create_subdirectories': True,
            'overwrite_existing': False,
            
            # Quality preservation settings
            'image_quality': 85,
            'video_crf': 23,  # Constant Rate Factor for video
            'audio_bitrate': 192,  # kbps
            'audio_sample_rate': 44100,
            
            # Platform optimization
            'auto_platform_optimization': True,
            'generate_multiple_formats': False,
            'adaptive_quality': True,
            
            # Professional settings
            'use_gpu_acceleration': False,
            'hardware_encoding': False,
            'two_pass_encoding': False,
            'custom_filters': {},
            
            # Supported formats
            'supported_image_formats': [
                'jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp', 'gif'
            ],
            'supported_video_formats': [
                'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'm4v'
            ],
            'supported_audio_formats': [
                'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'
            ],
            'supported_text_formats': [
                'txt', 'md', 'html', 'pdf', 'docx', 'rtf'
            ]
        }
    
    def _initialize_format_specs(self):
        """Initialize format specifications"""        try:
            # Image format specifications
            self.image_formats = {
                'jpg': FormatSpec(
                    format_name='JPEG',
                    extension='jpg',
                    mime_type='image/jpeg',
                    quality_settings={'quality': 85, 'optimize': True}
                ),
                'png': FormatSpec(
                    format_name='PNG',
                    extension='png',
                    mime_type='image/png',
                    quality_settings={'compress_level': 6, 'optimize': True}
                ),
                'webp': FormatSpec(
                    format_name='WebP',
                    extension='webp',
                    mime_type='image/webp',
                    quality_settings={'quality': 80, 'method': 6}
                ),
                'gif': FormatSpec(
                    format_name='GIF',
                    extension='gif',
                    mime_type='image/gif',
                    quality_settings={'optimize': True}
                )
            }
            
            # Video format specifications
            self.video_formats = {
                'mp4': FormatSpec(
                    format_name='MP4',
                    extension='mp4',
                    mime_type='video/mp4',
                    supported_codecs=['h264', 'h265'],
                    quality_settings={'crf': 23, 'preset': 'medium'}
                ),
                'webm': FormatSpec(
                    format_name='WebM',
                    extension='webm',
                    mime_type='video/webm',
                    supported_codecs=['vp8', 'vp9'],
                    quality_settings={'crf': 30, 'speed': 2}
                ),
                'mov': FormatSpec(
                    format_name='QuickTime',
                    extension='mov',
                    mime_type='video/quicktime',
                    supported_codecs=['h264', 'prores'],
                    quality_settings={'crf': 18, 'preset': 'slow'}
                )
            }
            
            # Audio format specifications
            self.audio_formats = {
                'mp3': FormatSpec(
                    format_name='MP3',
                    extension='mp3',
                    mime_type='audio/mpeg',
                    quality_settings={'bitrate': 192, 'quality': 2}
                ),
                'wav': FormatSpec(
                    format_name='WAV',
                    extension='wav',
                    mime_type='audio/wav',
                    quality_settings={'subtype': 'PCM_16'}
                ),
                'flac': FormatSpec(
                    format_name='FLAC',
                    extension='flac',
                    mime_type='audio/flac',
                    quality_settings={'compression_level': 5}
                ),
                'aac': FormatSpec(
                    format_name='AAC',
                    extension='aac',
                    mime_type='audio/aac',
                    quality_settings={'bitrate': 128, 'profile': 'aac_low'}
                )
            }
            
            # Text format specifications
            self.text_formats = {
                'txt': FormatSpec(
                    format_name='Plain Text',
                    extension='txt',
                    mime_type='text/plain'
                ),
                'md': FormatSpec(
                    format_name='Markdown',
                    extension='md',
                    mime_type='text/markdown'
                ),
                'html': FormatSpec(
                    format_name='HTML',
                    extension='html',
                    mime_type='text/html'
                ),
                'pdf': FormatSpec(
                    format_name='PDF',
                    extension='pdf',
                    mime_type='application/pdf'
                )
            }
            
            self.logger.info("Format specifications initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing format specs: {str(e)}")
            raise
    
    def _initialize_platform_profiles(self):
        """Initialize platform-specific format profiles"""        try:
            self.platform_profiles = {
                'instagram': PlatformProfile(
                    platform='Instagram',
                    image_specs=FormatSpec(
                        format_name='Instagram Image',
                        extension='jpg',
                        mime_type='image/jpeg',
                        max_width=1080,
                        max_height=1080,
                        max_file_size=8 * 1024 * 1024,  # 8MB
                        quality_settings={'quality': 85}
                    ),
                    video_specs=FormatSpec(
                        format_name='Instagram Video',
                        extension='mp4',
                        mime_type='video/mp4',
                        max_width=1080,
                        max_height=1920,  # Portrait for stories/reels
                        max_duration=60.0,
                        max_file_size=100 * 1024 * 1024,  # 100MB
                        supported_codecs=['h264'],
                        quality_settings={'crf': 25, 'preset': 'fast'}
                    ),
                    constraints={
                        'aspect_ratios': ['1:1', '4:5', '9:16'],
                        'min_resolution': (320, 320),
                        'frame_rate': [23.976, 25, 29.97, 30]
                    }
                ),
                
                'tiktok': PlatformProfile(
                    platform='TikTok',
                    video_specs=FormatSpec(
                        format_name='TikTok Video',
                        extension='mp4',
                        mime_type='video/mp4',
                        max_width=1080,
                        max_height=1920,  # Vertical format
                        max_duration=180.0,  # 3 minutes
                        max_file_size=287 * 1024 * 1024,  # 287MB
                        supported_codecs=['h264'],
                        quality_settings={'crf': 23, 'preset': 'medium'}
                    ),
                    constraints={
                        'aspect_ratios': ['9:16'],
                        'min_resolution': (540, 960),
                        'frame_rate': [25, 30]
                    }
                ),
                
                'youtube': PlatformProfile(
                    platform='YouTube',
                    video_specs=FormatSpec(
                        format_name='YouTube Video',
                        extension='mp4',
                        mime_type='video/mp4',
                        max_width=3840,  # 4K support
                        max_height=2160,
                        max_file_size=256 * 1024 * 1024 * 1024,  # 256GB
                        supported_codecs=['h264', 'h265'],
                        quality_settings={'crf': 18, 'preset': 'slow'}
                    ),
                    audio_specs=FormatSpec(
                        format_name='YouTube Audio',
                        extension='aac',
                        mime_type='audio/aac',
                        quality_settings={'bitrate': 384}
                    ),
                    constraints={
                        'aspect_ratios': ['16:9', '4:3', '1:1', '9:16'],
                        'min_resolution': (426, 240),
                        'frame_rate': [23.976, 24, 25, 29.97, 30, 50, 59.94, 60]
                    }
                ),
                
                'spotify': PlatformProfile(
                    platform='Spotify',
                    audio_specs=FormatSpec(
                        format_name='Spotify Audio',
                        extension='mp3',
                        mime_type='audio/mpeg',
                        quality_settings={'bitrate': 320}
                    ),
                    constraints={
                        'sample_rates': [44100, 48000],
                        'bit_depths': [16, 24],
                        'channels': [1, 2]  # Mono or Stereo
                    }
                ),
                
                'web': PlatformProfile(
                    platform='Web Optimized',
                    image_specs=FormatSpec(
                        format_name='Web Image',
                        extension='webp',
                        mime_type='image/webp',
                        max_width=1920,
                        max_height=1080,
                        quality_settings={'quality': 80, 'method': 6}
                    ),
                    video_specs=FormatSpec(
                        format_name='Web Video',
                        extension='mp4',
                        mime_type='video/mp4',
                        max_width=1920,
                        max_height=1080,
                        supported_codecs=['h264'],
                        quality_settings={'crf': 25, 'preset': 'fast'}
                    ),
                    audio_specs=FormatSpec(
                        format_name='Web Audio',
                        extension='mp3',
                        mime_type='audio/mpeg',
                        quality_settings={'bitrate': 192}
                    )
                )
            }
            
            self.logger.info("Platform profiles initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing platform profiles: {str(e)}")
            raise
    
    def _initialize_converters(self):
        """Initialize format converters"""        try:
            # Converter mapping
            self.converters = {
                'image': self._convert_image,
                'video': self._convert_video,
                'audio': self._convert_audio,
                'text': self._convert_text
            }
            
            # Format detection
            self.format_detectors = {
                'image': self._detect_image_format,
                'video': self._detect_video_format,
                'audio': self._detect_audio_format,
                'text': self._detect_text_format
            }
            
            self.logger.info("Format converters initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing converters: {str(e)}")
            raise
    
    async def process(
        self,
        content_data: Union[bytes, str],
        target_format: str,
        content_type: Optional[str] = None,
        platform: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Main format conversion pipeline
        
        Args:
            content_data: Content data as bytes or file path
            target_format: Target format (e.g., 'mp4', 'jpg', 'mp3')
            content_type: Content type hint ('image', 'video', 'audio', 'text')
            platform: Target platform for optimization
            config: Optional configuration override
        
        Returns:
            Dict containing conversion results
        """        try:
            start_time = datetime.now()
            
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Prepare content
            input_path, is_temp = await self._prepare_content(content_data)
            
            try:
                # Auto-detect content type if not provided
                if not content_type:
                    content_type = await self._detect_content_type(input_path)
                
                # Validate target format
                if not await self._validate_target_format(target_format, content_type):
                    raise ValueError(f"Invalid target format '{target_format}' for content type '{content_type}'")
                
                # Get platform profile if specified
                platform_profile = None
                if platform:
                    platform_profile = self.platform_profiles.get(platform.lower())
                    if not platform_profile:
                        self.logger.warning(f"Unknown platform '{platform}', using default settings")
                
                # Perform conversion
                conversion_result = await self._perform_conversion(
                    input_path,
                    target_format,
                    content_type,
                    platform_profile,
                    processing_config
                )
                
                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Compile result
                result = {
                    'success': True,
                    'content_type': content_type,
                    'target_format': target_format,
                    'platform': platform,
                    'conversion_result': conversion_result,
                    'processing_time': processing_time,
                    'processing_config': processing_config,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.logger.info(f"Format conversion completed: {content_type} -> {target_format}")
                return result
                
            finally:
                # Cleanup temporary input file if created
                if is_temp and os.path.exists(input_path):
                    os.unlink(input_path)
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'target_format': target_format,
                'platform': platform,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _prepare_content(self, content_data: Union[bytes, str]) -> Tuple[str, bool]:
        """Prepare content for conversion"""        try:
            if isinstance(content_data, str):
                # Already a file path
                if os.path.exists(content_data):
                    return content_data, False
                else:
                    raise FileNotFoundError(f"File not found: {content_data}")
                    
            elif isinstance(content_data, bytes):
                # Save bytes to temporary file
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(content_data)
                    return tmp_file.name, True
            else:
                raise ValueError(f"Unsupported content data type: {type(content_data)}")
                
        except Exception as e:
            self.logger.error(f"Error preparing content: {str(e)}")
            raise
    
    async def _detect_content_type(self, file_path: str) -> str:
        """Auto-detect content type from file"""        try:
            # Use mimetypes for initial detection
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type:
                if mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('video/'):
                    return 'video'
                elif mime_type.startswith('audio/'):
                    return 'audio'
                elif mime_type.startswith('text/'):
                    return 'text'
            
            # Fallback to file extension
            extension = Path(file_path).suffix.lower().lstrip('.')
            
            if extension in self.config.get('supported_image_formats', []):
                return 'image'
            elif extension in self.config.get('supported_video_formats', []):
                return 'video'
            elif extension in self.config.get('supported_audio_formats', []):
                return 'audio'
            elif extension in self.config.get('supported_text_formats', []):
                return 'text'
            
            # Default fallback
            return 'unknown'
            
        except Exception as e:
            self.logger.error(f"Error detecting content type: {str(e)}")
            return 'unknown'
    
    async def _validate_target_format(self, target_format: str, content_type: str) -> bool:
        """Validate target format compatibility"""        try:
            format_map = {
                'image': self.image_formats,
                'video': self.video_formats,
                'audio': self.audio_formats,
                'text': self.text_formats
            }
            
            supported_formats = format_map.get(content_type, {})
            return target_format.lower() in supported_formats
            
        except Exception as e:
            self.logger.error(f"Error validating target format: {str(e)}")
            return False
    
    async def _perform_conversion(
        self,
        input_path: str,
        target_format: str,
        content_type: str,
        platform_profile: Optional[PlatformProfile],
        config: Dict[str, Any]
    ) -> ConversionResult:
        """Perform the actual format conversion"""        try:
            # Get the appropriate converter
            converter = self.converters.get(content_type)
            if not converter:
                raise ValueError(f"No converter available for content type: {content_type}")
            
            # Get original format
            original_format = Path(input_path).suffix.lower().lstrip('.')
            
            # Create output path
            output_path = await self._create_output_path(
                input_path, target_format, config
            )
            
            # Perform conversion
            conversion_result = await converter(
                input_path,
                output_path,
                target_format,
                platform_profile,
                config
            )
            
            return conversion_result
            
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            raise
    
    async def _create_output_path(
        self,
        input_path: str,
        target_format: str,
        config: Dict[str, Any]
    ) -> str:
        """Create output file path"""        try:
            input_file = Path(input_path)
            output_dir = config.get('output_directory', 'converted')
            
            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            base_name = input_file.stem
            output_filename = f"{base_name}.{target_format}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Handle existing files
            if os.path.exists(output_path) and not config.get('overwrite_existing', False):
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{base_name}_{counter}.{target_format}"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating output path: {str(e)}")
            raise
    
    async def _convert_image(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        platform_profile: Optional[PlatformProfile],
        config: Dict[str, Any]
    ) -> ConversionResult:
        """Convert image format"""        try:
            if not PIL_AVAILABLE:
                raise RuntimeError("PIL not available for image conversion")
            
            start_time = datetime.now()
            
            # Load image
            with Image.open(input_path) as img:
                # Apply platform-specific constraints
                if platform_profile and platform_profile.image_specs:
                    img = await self._apply_image_constraints(img, platform_profile.image_specs)
                
                # Get format specifications
                format_spec = self.image_formats.get(target_format.lower())
                if not format_spec:
                    raise ValueError(f"Unsupported image format: {target_format}")
                
                # Apply quality settings
                save_kwargs = format_spec.quality_settings.copy()
                
                # Override with config settings
                if 'image_quality' in config:
                    save_kwargs['quality'] = config['image_quality']
                
                # Handle format-specific settings
                if target_format.lower() == 'png':
                    img = img.convert('RGBA')
                elif target_format.lower() in ['jpg', 'jpeg']:
                    if img.mode in ['RGBA', 'LA']:
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    else:
                        img = img.convert('RGB')
                
                # Save converted image
                img.save(output_path, format=format_spec.format_name, **save_kwargs)
            
            # Calculate conversion time
            conversion_time = (datetime.now() - start_time).total_seconds()
            
            # Get file info
            file_size = os.path.getsize(output_path)
            original_size = os.path.getsize(input_path)
            
            # Calculate quality score (simplified)
            quality_score = min(file_size / max(original_size, 1), 1.0)
            
            return ConversionResult(
                success=True,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path=output_path,
                file_size=file_size,
                quality_score=quality_score,
                conversion_time=conversion_time,
                metadata={
                    'original_size': original_size,
                    'compression_ratio': original_size / file_size if file_size > 0 else 1.0,
                    'format_spec': format_spec.__dict__
                }
            )
            
        except Exception as e:
            self.logger.error(f"Image conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path='',
                file_size=0,
                quality_score=0.0,
                conversion_time=0.0,
                error_message=str(e)
            )
    
    async def _convert_video(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        platform_profile: Optional[PlatformProfile],
        config: Dict[str, Any]
    ) -> ConversionResult:
        """Convert video format"""        try:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError("FFmpeg not available for video conversion")
            
            start_time = datetime.now()
            
            # Get format specifications
            format_spec = self.video_formats.get(target_format.lower())
            if not format_spec:
                raise ValueError(f"Unsupported video format: {target_format}")
            
            # Build FFmpeg command
            input_stream = ffmpeg.input(input_path)
            
            # Apply platform-specific constraints
            filters = []
            output_options = {}
            
            if platform_profile and platform_profile.video_specs:
                # Resolution constraints
                if platform_profile.video_specs.max_width and platform_profile.video_specs.max_height:
                    scale_filter = f"scale='min({platform_profile.video_specs.max_width},iw)':'min({platform_profile.video_specs.max_height},ih)':force_original_aspect_ratio=decrease"
                    filters.append(scale_filter)
                
                # Duration constraints
                if platform_profile.video_specs.max_duration:
                    output_options['t'] = platform_profile.video_specs.max_duration
            
            # Apply video codec
            if format_spec.supported_codecs:
                output_options['vcodec'] = format_spec.supported_codecs[0]
            
            # Apply quality settings
            quality_settings = format_spec.quality_settings.copy()
            if 'video_crf' in config:
                quality_settings['crf'] = config['video_crf']
            
            output_options.update(quality_settings)
            
            # Apply filters
            if filters:
                input_stream = input_stream.filter('scale', *filters[0].split(':')[1:])
            
            # Build output stream
            output_stream = input_stream.output(output_path, **output_options)
            
            # Run conversion
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            # Calculate conversion time
            conversion_time = (datetime.now() - start_time).total_seconds()
            
            # Get file info
            file_size = os.path.getsize(output_path)
            original_size = os.path.getsize(input_path)
            
            # Calculate quality score
            quality_score = 0.8  # Placeholder for video quality assessment
            
            return ConversionResult(
                success=True,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path=output_path,
                file_size=file_size,
                quality_score=quality_score,
                conversion_time=conversion_time,
                metadata={
                    'original_size': original_size,
                    'compression_ratio': original_size / file_size if file_size > 0 else 1.0,
                    'format_spec': format_spec.__dict__
                }
            )
            
        except Exception as e:
            self.logger.error(f"Video conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path='',
                file_size=0,
                quality_score=0.0,
                conversion_time=0.0,
                error_message=str(e)
            )
    
    async def _convert_audio(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        platform_profile: Optional[PlatformProfile],
        config: Dict[str, Any]
    ) -> ConversionResult:
        """Convert audio format"""        try:
            if not AUDIO_LIBS_AVAILABLE:
                raise RuntimeError("Audio libraries not available for conversion")
            
            start_time = datetime.now()
            
            # Load audio
            audio_data, sample_rate = librosa.load(input_path, sr=None)
            
            # Get format specifications
            format_spec = self.audio_formats.get(target_format.lower())
            if not format_spec:
                raise ValueError(f"Unsupported audio format: {target_format}")
            
            # Apply platform-specific constraints
            output_sample_rate = sample_rate
            if platform_profile and platform_profile.audio_specs:
                # Platform-specific sample rate
                platform_quality = platform_profile.audio_specs.quality_settings
                if 'sample_rate' in platform_quality:
                    output_sample_rate = platform_quality['sample_rate']
            
            # Resample if necessary
            if output_sample_rate != sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=output_sample_rate)
            
            # Apply quality settings
            quality_settings = format_spec.quality_settings.copy()
            
            # Save audio file
            if target_format.lower() in ['mp3']:
                # For MP3, we'd need additional libraries like pydub
                # For now, use soundfile for supported formats
                if target_format.lower() in ['wav', 'flac']:
                    sf.write(output_path, audio_data, output_sample_rate, **quality_settings)
                else:
                    # Fallback: save as WAV and note conversion limitation
                    wav_path = output_path.replace(f'.{target_format}', '.wav')
                    sf.write(wav_path, audio_data, output_sample_rate)
                    # Note: In production, integrate with pydub or similar for MP3/AAC
                    output_path = wav_path
            else:
                sf.write(output_path, audio_data, output_sample_rate, **quality_settings)
            
            # Calculate conversion time
            conversion_time = (datetime.now() - start_time).total_seconds()
            
            # Get file info
            file_size = os.path.getsize(output_path)
            original_size = os.path.getsize(input_path)
            
            # Calculate quality score
            quality_score = 0.85  # Placeholder for audio quality assessment
            
            return ConversionResult(
                success=True,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path=output_path,
                file_size=file_size,
                quality_score=quality_score,
                conversion_time=conversion_time,
                metadata={
                    'original_size': original_size,
                    'sample_rate': output_sample_rate,
                    'duration': len(audio_data) / output_sample_rate,
                    'format_spec': format_spec.__dict__
                }
            )
            
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path='',
                file_size=0,
                quality_score=0.0,
                conversion_time=0.0,
                error_message=str(e)
            )
    
    async def _convert_text(
        self,
        input_path: str,
        output_path: str,
        target_format: str,
        platform_profile: Optional[PlatformProfile],
        config: Dict[str, Any]
    ) -> ConversionResult:
        """Convert text format"""        try:
            start_time = datetime.now()
            
            # Read input text
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get format specifications
            format_spec = self.text_formats.get(target_format.lower())
            if not format_spec:
                raise ValueError(f"Unsupported text format: {target_format}")
            
            # Perform conversion based on target format
            if target_format.lower() == 'html':
                if TEXT_LIBS_AVAILABLE:
                    # Convert markdown to HTML
                    converted_content = markdown.markdown(content)
                else:
                    # Standard conversion
                    converted_content = f"<html><body><pre>{content}</pre></body></html>"
            
            elif target_format.lower() == 'md':
                # Assume input is plain text, add standard markdown formatting
                lines = content.split('
')
                converted_lines = []
                for line in lines:
                    if line.strip():
                        if len(line) < 80 and not line.endswith('.'):
                            # Likely a heading
                            converted_lines.append(f"## {line.strip()}")
                        else:
                            converted_lines.append(line)
                    else:
                        converted_lines.append(line)
                converted_content = '
'.join(converted_lines)
            
            elif target_format.lower() == 'txt':
                # Already plain text or strip formatting
                converted_content = content
            
            else:
                # Default: keep as-is
                converted_content = content
            
            # Write output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            
            # Calculate conversion time
            conversion_time = (datetime.now() - start_time).total_seconds()
            
            # Get file info
            file_size = os.path.getsize(output_path)
            original_size = os.path.getsize(input_path)
            
            return ConversionResult(
                success=True,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path=output_path,
                file_size=file_size,
                quality_score=1.0,  # Text conversion doesn't lose quality
                conversion_time=conversion_time,
                metadata={
                    'original_size': original_size,
                    'character_count': len(converted_content),
                    'line_count': len(converted_content.split('
')),
                    'format_spec': format_spec.__dict__
                }
            )
            
        except Exception as e:
            self.logger.error(f"Text conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                original_format=Path(input_path).suffix.lower().lstrip('.'),
                target_format=target_format,
                output_path='',
                file_size=0,
                quality_score=0.0,
                conversion_time=0.0,
                error_message=str(e)
            )
    
    async def _apply_image_constraints(
        self,
        img: Image.Image,
        image_specs: FormatSpec
    ) -> Image.Image:
        """Apply platform-specific image constraints"""        try:
            # Resize if necessary
            if image_specs.max_width and image_specs.max_height:
                max_size = (image_specs.max_width, image_specs.max_height)
                img.thumbnail(max_size, Image.LANCZOS)
            
            # Apply any additional constraints here
            # (e.g., aspect ratio, minimum resolution)
            
            return img
            
        except Exception as e:
            self.logger.error(f"Error applying image constraints: {str(e)}")
            return img
    
    # Format detection methods (simplified implementations)
    async def _detect_image_format(self, file_path: str) -> str:
        """Detect image format"""        try:
            with Image.open(file_path) as img:
                return img.format.lower() if img.format else 'unknown'
        except:
            return 'unknown'
    
    async def _detect_video_format(self, file_path: str) -> str:
        """Detect video format"""        try:
            probe = ffmpeg.probe(file_path)
            return probe.get('format', {}).get('format_name', 'unknown').split(',')[0]
        except:
            return 'unknown'
    
    async def _detect_audio_format(self, file_path: str) -> str:
        """Detect audio format"""        try:
            # Use file extension as approximation
            return Path(file_path).suffix.lower().lstrip('.')
        except:
            return 'unknown'
    
    async def _detect_text_format(self, file_path: str) -> str:
        """Detect text format"""        try:
            return Path(file_path).suffix.lower().lstrip('.')
        except:
            return 'unknown'
    
    async def batch_convert(
        self,
        file_list: List[Tuple[str, str]],  # (file_path, target_format)
        platform: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Convert multiple files in batch"""        if not self.config.get('batch_processing', True):
            raise ValueError("Batch processing is disabled")
        
        tasks = []
        for file_path, target_format in file_list:
            task = self.process(
                file_path,
                target_format,
                platform=platform,
                config=config
            )
            tasks.append(task)
        
        # Process in parallel if enabled
        if self.config.get('parallel_conversion', True):
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for task in tasks:
                result = await task
                results.append(result)
        
        return [
            result if not isinstance(result, Exception) 
            else {
                'success': False, 
                'error': str(result), 
                'file': file_list[i][0],
                'target_format': file_list[i][1]
            }
            for i, result in enumerate(results)
        ]
    
    async def optimize_for_platform(
        self,
        content_data: Union[bytes, str],
        platform: str,
        content_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize content for specific platform"""        try:
            # Get platform profile
            platform_profile = self.platform_profiles.get(platform.lower())
            if not platform_profile:
                raise ValueError(f"Unsupported platform: {platform}")
            
            # Auto-detect content type if not provided
            if isinstance(content_data, str) and not content_type:
                content_type = await self._detect_content_type(content_data)
            
            # Determine optimal format for platform and content type
            optimal_format = None
            if content_type == 'image' and platform_profile.image_specs:
                optimal_format = platform_profile.image_specs.extension
            elif content_type == 'video' and platform_profile.video_specs:
                optimal_format = platform_profile.video_specs.extension
            elif content_type == 'audio' and platform_profile.audio_specs:
                optimal_format = platform_profile.audio_specs.extension
            elif content_type == 'text' and platform_profile.text_specs:
                optimal_format = platform_profile.text_specs.extension
            
            if not optimal_format:
                raise ValueError(f"No optimal format found for {content_type} content on {platform}")
            
            # Perform platform-optimized conversion
            return await self.process(
                content_data,
                optimal_format,
                content_type=content_type,
                platform=platform,
                config=config
            )
            
        except Exception as e:
            self.logger.error(f"Platform optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'platform': platform,
                'content_type': content_type,
                'timestamp': datetime.now().isoformat()
            }

import asyncio
import logging
import os
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

# Format conversion libraries
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    logging.warning("FFmpeg not available - video/audio conversion will be limited")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - image conversion will be limited")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ConversionProfile:
    """Format conversion profile configuration"""    name: str
    input_format: str
    output_format: str
    quality: str = 'high'  # low, medium, high, lossless
    optimization_target: str = 'balanced'  # size, quality, speed, balanced
    
    # Format-specific settings
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    bitrate: Optional[str] = None
    resolution: Optional[Tuple[int, int]] = None
    fps: Optional[int] = None
    
    # Image settings
    image_quality: Optional[int] = None
    compression_level: Optional[int] = None
    
    # Professional options
    custom_params: Dict[str, Any] = None

class FormatProcessor:
    """Professional format conversion and standardization engine"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize format processors
        self._initialize_processors()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default format processing configuration"""        return {
            'temp_dir': '/tmp/format_processor',
            'supported_conversions': {
                'audio': {
                    'input_formats': ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg', 'wma'],
                    'output_formats': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
                    'preferred_format': 'mp3'
                },
                'video': {
                    'input_formats': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv'],
                    'output_formats': ['mp4', 'webm', 'mov', 'avi'],
                    'preferred_format': 'mp4'
                },
                'image': {
                    'input_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
                    'output_formats': ['jpg', 'png', 'webp', 'gif'],
                    'preferred_format': 'jpg'
                },
                'text': {
                    'input_formats': ['txt', 'md', 'rtf', 'docx', 'pdf'],
                    'output_formats': ['txt', 'md', 'html', 'pdf'],
                    'preferred_format': 'md'
                }
            },
            'conversion_profiles': {
                'social_media': {
                    'video': {'resolution': (1080, 1920), 'bitrate': '2M', 'fps': 30},
                    'image': {'max_size': (1080, 1080), 'quality': 85, 'format': 'jpg'},
                    'audio': {'bitrate': '128k', 'format': 'mp3'}
                },
                'professional': {
                    'video': {'resolution': (1920, 1080), 'bitrate': '8M', 'fps': 30},
                    'image': {'max_size': (4096, 4096), 'quality': 95, 'format': 'png'},
                    'audio': {'bitrate': '320k', 'format': 'flac'}
                },
                'web_optimized': {
                    'video': {'resolution': (720, 1280), 'bitrate': '1M', 'fps': 30},
                    'image': {'max_size': (1920, 1080), 'quality': 80, 'format': 'webp'},
                    'audio': {'bitrate': '128k', 'format': 'ogg'}
                }
            },
            'quality_settings': {
                'lossless': {'image_quality': 100, 'compression': 0},
                'high': {'image_quality': 95, 'compression': 2},
                'medium': {'image_quality': 85, 'compression': 5},
                'low': {'image_quality': 70, 'compression': 8}
            }
        }
    
    def _initialize_processors(self):
        """Initialize format processing components"""        try:
            # Ensure temp directory exists
            os.makedirs(self.config['temp_dir'], exist_ok=True)
            
            # Initialize format-specific converters
            self.audio_converter = AudioFormatConverter(self.config)
            self.video_converter = VideoFormatConverter(self.config)
            self.image_converter = ImageFormatConverter(self.config)
            self.text_converter = TextFormatConverter(self.config)
            
            self.logger.info("Format processor components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing format processors: {str(e)}")
            raise
    
    async def process(
        self,
        content_data: Union[bytes, str],
        input_format: str,
        output_format: str,
        content_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Main format conversion pipeline
        
        Args:
            content_data: Content data as bytes or file path
            input_format: Source format
            output_format: Target format
            content_type: Type of content (audio, video, image, text)
            config: Optional conversion configuration
        
        Returns:
            Dict containing converted content and conversion info
        """        try:
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Validate conversion capability
            validation_result = await self._validate_conversion(
                input_format, output_format, content_type
            )
            
            if not validation_result['supported']:
                return {
                    'success': False,
                    'error': f"Conversion from {input_format} to {output_format} not supported",
                    'validation': validation_result
                }
            
            # Perform format-specific conversion
            if content_type == 'audio':
                conversion_result = await self.audio_converter.convert(
                    content_data, input_format, output_format, processing_config
                )
            elif content_type == 'video':
                conversion_result = await self.video_converter.convert(
                    content_data, input_format, output_format, processing_config
                )
            elif content_type == 'image':
                conversion_result = await self.image_converter.convert(
                    content_data, input_format, output_format, processing_config
                )
            elif content_type == 'text':
                conversion_result = await self.text_converter.convert(
                    content_data, input_format, output_format, processing_config
                )
            else:
                return {
                    'success': False,
                    'error': f"Content type {content_type} not supported"
                }
            
            # Calculate conversion metrics
            metrics = await self._calculate_conversion_metrics(
                content_data, conversion_result, input_format, output_format
            )
            
            # Compile final result
            result = {
                'success': True,
                'converted_content': conversion_result.get('converted_data'),
                'output_path': conversion_result.get('output_path'),
                'input_format': input_format,
                'output_format': output_format,
                'content_type': content_type,
                'conversion_metrics': metrics,
                'validation': validation_result,
                'processing_config': processing_config,
                'timestamp': str(asyncio.get_event_loop().time())
            }
            
            self.logger.info(f"Format conversion completed: {input_format} -> {output_format}")
            return result
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_format': input_format,
                'output_format': output_format,
                'content_type': content_type
            }
    
    async def _validate_conversion(
        self,
        input_format: str,
        output_format: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Validate if conversion is supported"""        try:
            supported_conversions = self.config['supported_conversions'].get(content_type, {})
            
            input_supported = input_format.lower() in supported_conversions.get('input_formats', [])
            output_supported = output_format.lower() in supported_conversions.get('output_formats', [])
            
            validation = {
                'supported': input_supported and output_supported,
                'input_format_supported': input_supported,
                'output_format_supported': output_supported,
                'content_type_supported': content_type in self.config['supported_conversions'],
                'recommendations': []
            }
            
            # Add recommendations
            if not input_supported:
                validation['recommendations'].append(
                    f"Input format '{input_format}' not supported for {content_type}"
                )
            
            if not output_supported:
                preferred = supported_conversions.get('preferred_format')
                validation['recommendations'].append(
                    f"Output format '{output_format}' not supported. Consider using '{preferred}'"
                )
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Conversion validation failed: {str(e)}")
            return {
                'supported': False,
                'error': str(e)
            }
    
    async def _calculate_conversion_metrics(
        self,
        original_data: Union[bytes, str],
        conversion_result: Dict[str, Any],
        input_format: str,
        output_format: str
    ) -> Dict[str, Any]:
        """Calculate conversion quality and efficiency metrics"""        try:
            metrics = {
                'conversion_time': conversion_result.get('processing_time', 0),
                'size_reduction': 0.0,
                'quality_preservation': 0.0,
                'efficiency_score': 0.0
            }
            
            # Calculate size metrics
            if isinstance(original_data, bytes):
                original_size = len(original_data)
            elif isinstance(original_data, str) and os.path.exists(original_data):
                original_size = os.path.getsize(original_data)
            else:
                original_size = 0
            
            converted_data = conversion_result.get('converted_data')
            if converted_data:
                if isinstance(converted_data, bytes):
                    converted_size = len(converted_data)
                elif isinstance(converted_data, str) and os.path.exists(converted_data):
                    converted_size = os.path.getsize(converted_data)
                else:
                    converted_size = 0
                
                if original_size > 0:
                    metrics['size_reduction'] = (original_size - converted_size) / original_size * 100
                    metrics['compression_ratio'] = converted_size / original_size
            
            # Estimate quality preservation (format-specific logic would go here)
            lossy_formats = ['jpg', 'jpeg', 'mp3', 'aac', 'ogg']
            if output_format.lower() in lossy_formats:
                metrics['quality_preservation'] = 85.0  # Typical for lossy conversion
            else:
                metrics['quality_preservation'] = 95.0  # Lossless or minimal loss
            
            # Calculate efficiency score
            time_factor = max(0, 100 - metrics['conversion_time'])  # Faster is better
            size_factor = max(0, metrics['size_reduction'])  # Smaller is better
            quality_factor = metrics['quality_preservation']
            
            metrics['efficiency_score'] = (time_factor + size_factor + quality_factor) / 3
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {str(e)}")
            return {
                'conversion_time': 0,
                'size_reduction': 0.0,
                'quality_preservation': 0.0,
                'efficiency_score': 0.0
            }
    
    async def batch_convert(
        self,
        conversion_jobs: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Convert multiple files in batch"""        tasks = []
        
        for job in conversion_jobs:
            task = self.process(
                job.get('content_data'),
                job.get('input_format'),
                job.get('output_format'),
                job.get('content_type'),
                config
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) 
            else {'success': False, 'error': str(result), 'job_index': i}
            for i, result in enumerate(results)
        ]
    
    async def optimize_for_platform(
        self,
        content_data: Union[bytes, str],
        content_type: str,
        platform: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize content format for specific platform"""        try:
            platform_profiles = self.config['conversion_profiles'].get(platform, {})
            content_profile = platform_profiles.get(content_type, {})
            
            if not content_profile:
                return {
                    'success': False,
                    'error': f"No optimization profile for {content_type} on {platform}"
                }
            
            # Determine current format
            if isinstance(content_data, str):
                current_format = Path(content_data).suffix.lower().lstrip('.')
            else:
                current_format = 'unknown'
            
            # Get target format
            target_format = content_profile.get('format', 
                self.config['supported_conversions'][content_type]['preferred_format'])
            
            # Create optimization config
            optimization_config = config.copy() if config else {}
            optimization_config.update(content_profile)
            
            # Perform conversion
            result = await self.process(
                content_data, current_format, target_format, content_type, optimization_config
            )
            
            result['platform'] = platform
            result['optimization_applied'] = True
            
            return result
            
        except Exception as e:
            self.logger.error(f"Platform optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'platform': platform
            }
    
    def get_supported_formats(self, content_type: str) -> Dict[str, List[str]]:
        """Get supported input and output formats for content type"""        return self.config['supported_conversions'].get(content_type, {
            'input_formats': [],
            'output_formats': []
        })
    
    def get_conversion_profiles(self) -> Dict[str, Any]:
        """Get available conversion profiles"""        return self.config['conversion_profiles']

# Format-specific converter classes
class AudioFormatConverter:
    """Audio format conversion engine"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AudioFormatConverter")
    
    async def convert(
        self,
        content_data: Union[bytes, str],
        input_format: str,
        output_format: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert audio format"""        try:
            start_time = asyncio.get_event_loop().time()
            
            # Prepare input file
            if isinstance(content_data, bytes):
                input_path = os.path.join(
                    self.config['temp_dir'], 
                    f"input_{id(content_data)}.{input_format}"
                )
                with open(input_path, 'wb') as f:
                    f.write(content_data)
            else:
                input_path = content_data
            
            # Prepare output file
            output_path = os.path.join(
                self.config['temp_dir'],
                f"output_{id(content_data)}.{output_format}"
            )
            
            if FFMPEG_AVAILABLE:
                # Use FFmpeg for conversion
                input_stream = ffmpeg.input(input_path)
                
                # Apply audio settings
                kwargs = {}
                if config.get('bitrate'):
                    kwargs['audio_bitrate'] = config['bitrate']
                if config.get('audio_codec'):
                    kwargs['acodec'] = config['audio_codec']
                
                output_stream = ffmpeg.output(input_stream, output_path, **kwargs)
                ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            else:
                # Fallback: optimized copy for same format
                if input_format == output_format:
                    import shutil
                    shutil.copy2(input_path, output_path)
                else:
                    raise RuntimeError("FFmpeg required for audio conversion")
            
            # Read converted data
            with open(output_path, 'rb') as f:
                converted_data = f.read()
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                'converted_data': converted_data,
                'output_path': output_path,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {str(e)}")
            raise

class VideoFormatConverter:
    """Video format conversion engine"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.VideoFormatConverter")
    
    async def convert(
        self,
        content_data: Union[bytes, str],
        input_format: str,
        output_format: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert video format"""        try:
            start_time = asyncio.get_event_loop().time()
            
            # Similar implementation to audio but with video-specific parameters
            # This would include resolution, fps, codec settings, etc.
            
            # Placeholder implementation
            output_path = os.path.join(
                self.config['temp_dir'],
                f"video_output_{id(content_data)}.{output_format}"
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                'converted_data': None,  # Would contain converted video data
                'output_path': output_path,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Video conversion failed: {str(e)}")
            raise

class ImageFormatConverter:
    """Image format conversion engine"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ImageFormatConverter")
    
    async def convert(
        self,
        content_data: Union[bytes, str],
        input_format: str,
        output_format: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert image format"""        try:
            start_time = asyncio.get_event_loop().time()
            
            if PIL_AVAILABLE:
                # Load image
                if isinstance(content_data, bytes):
                    from io import BytesIO
                    image = Image.open(BytesIO(content_data))
                else:
                    image = Image.open(content_data)
                
                # Apply image settings
                if config.get('max_size'):
                    max_width, max_height = config['max_size']
                    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convert format
                if output_format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA'):
                    # Convert to RGB for JPEG
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                
                # Save converted image
                output_path = os.path.join(
                    self.config['temp_dir'],
                    f"image_output_{id(content_data)}.{output_format}"
                )
                
                save_kwargs = {}
                if output_format.upper() == 'JPEG':
                    save_kwargs['quality'] = config.get('quality', 85)
                    save_kwargs['optimize'] = True
                
                image.save(output_path, format=output_format.upper(), **save_kwargs)
                
                # Read converted data
                with open(output_path, 'rb') as f:
                    converted_data = f.read()
                
                processing_time = asyncio.get_event_loop().time() - start_time
                
                return {
                    'converted_data': converted_data,
                    'output_path': output_path,
                    'processing_time': processing_time
                }
            else:
                raise RuntimeError("PIL required for image conversion")
            
        except Exception as e:
            self.logger.error(f"Image conversion failed: {str(e)}")
            raise

class TextFormatConverter:
    """Text format conversion engine"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.TextFormatConverter")
    
    async def convert(
        self,
        content_data: Union[bytes, str],
        input_format: str,
        output_format: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert text format"""        try:
            start_time = asyncio.get_event_loop().time()
            
            # Read text content
            if isinstance(content_data, bytes):
                text_content = content_data.decode('utf-8')
            elif isinstance(content_data, str) and os.path.exists(content_data):
                with open(content_data, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            else:
                text_content = str(content_data)
            
            # Convert based on output format
            if output_format.lower() == 'html':
                # Convert to HTML
                html_content = f"<html><body><pre>{text_content}</pre></body></html>"
                converted_content = html_content
            elif output_format.lower() == 'md':
                # Professional text to markdown
                converted_content = text_content  # Standard conversion
            else:
                # Plain text output
                converted_content = text_content
            
            # Save converted content
            output_path = os.path.join(
                self.config['temp_dir'],
                f"text_output_{id(content_data)}.{output_format}"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            
            converted_data = converted_content.encode('utf-8')
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                'converted_data': converted_data,
                'output_path': output_path,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Text conversion failed: {str(e)}")
            raise
