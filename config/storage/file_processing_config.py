"""File Processing Configuration for IA-Influencer Agent Platform
==============================================================

Professional file processing and transformation configuration for multi-format content.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ProcessingType(Enum):
    """
Types of file processing operations."""

    TRANSCODING = "transcoding"
    COMPRESSION = "compression"
    THUMBNAIL = "thumbnail"
    WATERMARKING = "watermarking"
    METADATA_EXTRACTION = "metadata_extraction"
    FINGERPRINTING = "fingerprinting"
    FORMAT_CONVERSION = "format_conversion"
    QUALITY_OPTIMIZATION = "quality_optimization"

@dataclass
class AudioProcessingConfig:
    """Audio file processing configuration."""
    
    # Supported input formats
    supported_input_formats: List[str] = None
    
    # Output formats and quality settings
    output_formats: Dict[str, Dict[str, Any]] = None
    
    # Processing settings
    normalize_audio: bool = True
    noise_reduction: bool = True
    auto_gain_control: bool = True
    
    # Quality settings
    default_bitrate: int = 320  # kbps
    default_sample_rate: int = 44100  # Hz
    default_channels: int = 2  # Stereo
    
    # Advanced processing
    enable_ai_enhancement: bool = True
    enable_spectral_analysis: bool = True
    enable_loudness_normalization: bool = True
    
    def __post_init__(self):
        if self.supported_input_formats is None:
            self.supported_input_formats = [
                'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a', 'aiff'
            ]
        
        if self.output_formats is None:
            self.output_formats = {
                'mp3': {
                    'codec': 'mp3',
                    'bitrate': '320k',
                    'sample_rate': 44100,
                    'channels': 2,
                    'quality': 'high'
                },
                'wav': {
                    'codec': 'pcm_s16le',
                    'sample_rate': 44100,
                    'channels': 2,
                    'quality': 'lossless'
                },
                'flac': {
                    'codec': 'flac',
                    'compression_level': 5,
                    'sample_rate': 44100,
                    'channels': 2,
                    'quality': 'lossless'
                },
                'aac': {
                    'codec': 'aac',
                    'bitrate': '256k',
                    'sample_rate': 44100,
                    'channels': 2,
                    'quality': 'high'
                }
            }

@dataclass
class VideoProcessingConfig:
    """
Video file processing configuration."""
    
    # Supported input formats
    supported_input_formats: List[str] = None
    
    # Output formats and quality settings
    output_formats: Dict[str, Dict[str, Any]] = None
    
    # Processing settings
    enable_hardware_acceleration: bool = True
    gpu_acceleration: bool = True
    multi_threading: bool = True
    thread_count: int = 4
    
    # Quality settings
    default_video_codec: str = 'h264'
    default_audio_codec: str = 'aac'
    default_container: str = 'mp4'
    
    # Thumbnail settings
    thumbnail_count: int = 5
    thumbnail_format: str = 'jpg'
    thumbnail_quality: int = 85
    thumbnail_sizes: List[Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.supported_input_formats is None:
            self.supported_input_formats = [
                'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 'm4v', '3gp'
            ]
        
        if self.output_formats is None:
            self.output_formats = {
                'mp4_hd': {
                    'container': 'mp4',
                    'video_codec': 'h264',
                    'audio_codec': 'aac',
                    'resolution': '1920x1080',
                    'video_bitrate': '5000k',
                    'audio_bitrate': '192k',
                    'fps': 30,
                    'quality': 'high'
                },
                'mp4_sd': {
                    'container': 'mp4',
                    'video_codec': 'h264',
                    'audio_codec': 'aac',
                    'resolution': '1280x720',
                    'video_bitrate': '2500k',
                    'audio_bitrate': '128k',
                    'fps': 30,
                    'quality': 'medium'
                },
                'webm': {
                    'container': 'webm',
                    'video_codec': 'vp9',
                    'audio_codec': 'vorbis',
                    'resolution': '1920x1080',
                    'video_bitrate': '4000k',
                    'audio_bitrate': '192k',
                    'quality': 'high'
                },
                'hls': {
                    'container': 'm3u8',
                    'video_codec': 'h264',
                    'audio_codec': 'aac',
                    'segment_duration': 6,
                    'playlist_type': 'vod',
                    'quality': 'adaptive'
                }
            }
        
        if self.thumbnail_sizes is None:
            self.thumbnail_sizes = [
                (160, 90),   # Small
                (320, 180),  # Medium
                (640, 360),  # Large
                (1280, 720)  # HD
            ]

@dataclass
class ImageProcessingConfig:
    """
Image file processing configuration."""
    
    # Supported input formats
    supported_input_formats: List[str] = None
    
    # Output formats and quality settings
    output_formats: Dict[str, Dict[str, Any]] = None
    
    # Processing settings
    auto_orientation: bool = True
    strip_metadata: bool = False  # Keep for fingerprinting
    color_space_conversion: bool = True
    
    # Quality settings
    default_quality: int = 85
    progressive_jpeg: bool = True
    optimize_png: bool = True
    
    # Resize settings
    max_dimensions: Tuple[int, int] = (4096, 4096)
    thumbnail_sizes: List[Tuple[int, int]] = None
    maintain_aspect_ratio: bool = True
    
    def __post_init__(self):
        if self.supported_input_formats is None:
            self.supported_input_formats = [
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'
            ]
        
        if self.output_formats is None:
            self.output_formats = {
                'webp': {
                    'format': 'webp',
                    'quality': 85,
                    'lossless': False,
                    'method': 6
                },
                'jpeg': {
                    'format': 'jpeg',
                    'quality': 85,
                    'progressive': True,
                    'optimize': True
                },
                'png': {
                    'format': 'png',
                    'optimize': True,
                    'compress_level': 6
                },
                'avif': {
                    'format': 'avif',
                    'quality': 80,
                    'speed': 6
                }
            }
        
        if self.thumbnail_sizes is None:
            self.thumbnail_sizes = [
                (150, 150),   # Square small
                (300, 300),   # Square medium
                (600, 400),   # Rectangle large
                (1200, 800)   # Rectangle extra large
            ]

@dataclass
class DocumentProcessingConfig:
    """
Document file processing configuration."""
    
    # Supported input formats
    supported_input_formats: List[str] = None
    
    # Output formats
    output_formats: List[str] = None
    
    # Text extraction settings
    enable_ocr: bool = True
    ocr_languages: List[str] = None
    extract_metadata: bool = True
    
    # PDF processing
    pdf_quality: int = 85
    pdf_compression: bool = True
    extract_images: bool = True
    
    # Security settings
    enable_watermarking: bool = True
    password_protection: bool = False
    
    def __post_init__(self):
        if self.supported_input_formats is None:
            self.supported_input_formats = [
                'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx'
            ]
        
        if self.output_formats is None:
            self.output_formats = ['pdf', 'txt', 'html', 'markdown']
        
        if self.ocr_languages is None:
            self.ocr_languages = ['en', 'de', 'fr', 'es', 'it']

@dataclass
class FileProcessingConfig:
    """
    Comprehensive file processing configuration for IA-Influencer Agent platform.
    Handles multi-format content processing with enterprise-grade optimization.
    """
    
    # Processing configurations by type
    audio_config: AudioProcessingConfig = None
    video_config: VideoProcessingConfig = None
    image_config: ImageProcessingConfig = None
    document_config: DocumentProcessingConfig = None
    
    # Global processing settings
    max_file_size_mb: int = 500
    processing_timeout_seconds: int = 300  # 5 minutes
    concurrent_processing_limit: int = 4
    
    # Queue settings
    use_async_processing: bool = True
    queue_backend: str = 'celery'  # celery, rq, redis
    priority_levels: Dict[str, int] = None
    
    # Storage settings for processed files
    temp_storage_path: str = '/tmp/ia-influencer/processing'
    output_storage_path: str = '/var/lib/ia-influencer/processed'
    cleanup_temp_files: bool = True
    temp_file_retention_hours: int = 24
    
    # Monitoring and logging
    enable_processing_metrics: bool = True
    log_processing_details: bool = True
    enable_progress_tracking: bool = True
    
    # Security settings
    scan_uploaded_files: bool = True
    virus_scanning: bool = True
    content_validation: bool = True
    
    # AI processing features
    enable_ai_fingerprinting: bool = True
    enable_content_analysis: bool = True
    enable_quality_enhancement: bool = True
    
    def __post_init__(self):
        """
Initialize processing configurations if not provided."""
        if self.audio_config is None:
            self.audio_config = AudioProcessingConfig()
        
        if self.video_config is None:
            self.video_config = VideoProcessingConfig()
        
        if self.image_config is None:
            self.image_config = ImageProcessingConfig()
        
        if self.document_config is None:
            self.document_config = DocumentProcessingConfig()
        
        if self.priority_levels is None:
            self.priority_levels = {
                'audio': 8,     # High priority
                'image': 6,     # Medium priority
                'document': 4,  # Low priority
                'video': 2      # Lowest priority (heavy processing)
            }
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
Get all supported input formats by content type."""
        return {
            'audio': self.audio_config.supported_input_formats,
            'video': self.video_config.supported_input_formats,
            'image': self.image_config.supported_input_formats,
            'document': self.document_config.supported_input_formats
        }
    
    def is_format_supported(self, content_type: str, file_extension: str) -> bool:
        """
Check if file format is supported for processing."""
        supported_formats = self.get_supported_formats()
        
        if content_type not in supported_formats:
            return False
        
        return file_extension.lower().lstrip('.') in supported_formats[content_type]
    
    def get_output_formats(self, content_type: str) -> List[str]:
        """
Get available output formats for content type."""
        if content_type == 'audio':
            return list(self.audio_config.output_formats.keys())
        elif content_type == 'video':
            return list(self.video_config.output_formats.keys())
        elif content_type == 'image':
            return list(self.image_config.output_formats.keys())
        elif content_type == 'document':
            return self.document_config.output_formats
        
        return []
    
    def get_processing_priority(self, content_type: str) -> int:
        """
Get processing priority for content type."""
        return self.priority_levels.get(content_type, 5)  # Default priority
    
    def get_max_processing_time(self, content_type: str, file_size_mb: float) -> int:
        """
Get estimated max processing time based on content type and file size."""
        base_time = self.processing_timeout_seconds
        
        # Adjust based on content type
        multipliers = {
            'audio': 1.0,
            'image': 0.5,
            'document': 0.3,
            'video': 3.0  # Video processing takes much longer
        }
        
        multiplier = multipliers.get(content_type, 1.0)
        
        # Adjust based on file size
        size_factor = max(1.0, file_size_mb / 50.0)  # Scale after 50MB
        
        return int(base_time * multiplier * size_factor)
    
    def validate_file_for_processing(self, content_type: str, file_path: str, 
                                   file_size_mb: float) -> Tuple[bool, str]:
        """
Validate file for processing."""
        # Check file size
        if file_size_mb > self.max_file_size_mb:
            return False, f"File size ({file_size_mb}MB) exceeds limit ({self.max_file_size_mb}MB)"
        
        # Check format support
        file_extension = os.path.splitext(file_path)[1]
        if not self.is_format_supported(content_type, file_extension):
            return False, f"Unsupported format: {file_extension} for {content_type}"
        
        # Check file existence
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        return True, "File is valid for processing"
    
    def get_processing_workflow(self, content_type: str, 
                              operations: List[ProcessingType]) -> Dict[str, Any]:
        """Get processing workflow configuration for specific operations."""
        workflow = {
            'content_type': content_type,
            'operations': [],
            'estimated_time': 0,
            'priority': self.get_processing_priority(content_type)
        }
        
        for operation in operations:
            step = {
                'operation': operation.value,
                'config': self._get_operation_config(content_type, operation)
            }
            workflow['operations'].append(step)
        
        # Estimate total processing time
        workflow['estimated_time'] = len(operations) * 30  # Base 30 seconds per operation
        
        return workflow
    
    def _get_operation_config(self, content_type: str, 
                            operation: ProcessingType) -> Dict[str, Any]:
        """
Get configuration for specific processing operation."""
        if content_type == 'audio':
            config = self.audio_config
        elif content_type == 'video':
            config = self.video_config
        elif content_type == 'image':
            config = self.image_config
        elif content_type == 'document':
            config = self.document_config
        else:
            return {}
        
        # Return operation-specific configuration
        operation_configs = {
            ProcessingType.TRANSCODING: getattr(config, 'output_formats', {}),
            ProcessingType.COMPRESSION: {'quality': getattr(config, 'default_quality', 85)},
            ProcessingType.THUMBNAIL: getattr(config, 'thumbnail_sizes', []),
            ProcessingType.WATERMARKING: {'enabled': True},
            ProcessingType.METADATA_EXTRACTION: {'enabled': True},
            ProcessingType.FINGERPRINTING: {'enabled': self.enable_ai_fingerprinting},
            ProcessingType.FORMAT_CONVERSION: getattr(config, 'output_formats', {}),
            ProcessingType.QUALITY_OPTIMIZATION: {'enabled': self.enable_quality_enhancement}
        }
        
        return operation_configs.get(operation, {})
    
    def export_configuration(self) -> Dict[str, Any]:
        """
Export processing configuration to JSON-serializable format."""
        return {
            'max_file_size_mb': self.max_file_size_mb,
            'processing_timeout_seconds': self.processing_timeout_seconds,
            'concurrent_processing_limit': self.concurrent_processing_limit,
            'use_async_processing': self.use_async_processing,
            'queue_backend': self.queue_backend,
            'enable_ai_fingerprinting': self.enable_ai_fingerprinting,
            'enable_content_analysis': self.enable_content_analysis,
            'enable_quality_enhancement': self.enable_quality_enhancement,
            'supported_formats': self.get_supported_formats(),
            'priority_levels': self.priority_levels
        }

# Global file processing configuration instance
file_processing_config = FileProcessingConfig()
