"""
Content Format Configuration - Enterprise Configuration Management
Enterprise configuration for content format processing and validation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic import BaseSettings, validator, Field
except ImportError:
    # Fallback for environments without pydantic
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    
    def validator(field_name):
        def decorator(func):
            return func
        return decorator
    
    def Field(**kwargs):
        return kwargs.get('default_factory', kwargs.get('default'))()


class AudioFormat(str, Enum):
    """Professional audio format support"""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    AIFF = "aiff"
    APE = "ape"
    OPUS = "opus"


class VideoFormat(str, Enum):
    """Professional video format support"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WMV = "wmv"
    WEBM = "webm"
    FLV = "flv"
    M4V = "m4v"
    _3GP = "3gp"
    RM = "rm"


class ImageFormat(str, Enum):
    """Professional image format support"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    SVG = "svg"
    WEBP = "webp"
    GIF = "gif"
    TIFF = "tiff"
    BMP = "bmp"
    RAW = "raw"
    HEIC = "heic"


class TextFormat(str, Enum):
    """Text and document format support"""
    MARKDOWN = "markdown"
    HTML = "html"
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"
    RTF = "rtf"
    ODT = "odt"
    TEX = "tex"


class VoiceFormat(str, Enum):
    """Voice and speech format support"""
    VOICE_WAV = "voice_wav"
    VOICE_MP3 = "voice_mp3"
    VOICE_FLAC = "voice_flac"
    VOICE_SYNTHESIS = "voice_synthesis"
    SPEECH_TO_TEXT = "speech_to_text"
    VOICE_CLONE = "voice_clone"


class AvatarFormat(str, Enum):
    """Avatar and 3D model format support"""
    MODELS_3D = "3d_models"
    ANIMATIONS = "animations"
    VRCHAT = "vrchat"
    UNITY = "unity"
    FBX = "fbx"
    OBJ = "obj"
    GLTF = "gltf"
    BLEND = "blend"


class QualityLevel(str, Enum):
    """Content quality levels"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"
    ULTRA = "ultra"
    PROFESSIONAL = "professional"


class CompressionType(str, Enum):
    """Compression type support"""
    LOSSY = "lossy"
    LOSSLESS = "lossless"
    HYBRID = "hybrid"


@dataclass
class FormatSpecification:
    """Detailed format specification"""
    extensions: Set[str]
    mime_types: Set[str]
    max_size_mb: int
    quality_levels: Set[QualityLevel]
    compression_type: CompressionType
    professional_grade: bool
    ai_processable: bool
    copyright_detectable: bool


@dataclass
class ProcessingConfiguration:
    """Format processing configuration"""
    auto_conversion_enabled: bool
    quality_enhancement: bool
    compression_optimization: bool
    metadata_extraction: bool
    copyright_detection: bool
    ai_analysis: bool


class ContentFormatSettings(BaseSettings):
    """Content format configuration settings"""
    
    # Audio Format Specifications
    audio_formats: Dict[str, FormatSpecification] = Field(
        default_factory=lambda: {
            "mp3": FormatSpecification(
                extensions={"mp3"},
                mime_types={"audio/mpeg", "audio/mp3"},
                max_size_mb=500,
                quality_levels={QualityLevel.BASIC, QualityLevel.STANDARD, QualityLevel.HIGH},
                compression_type=CompressionType.LOSSY,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "wav": FormatSpecification(
                extensions={"wav"},
                mime_types={"audio/wav", "audio/wave"},
                max_size_mb=1000,
                quality_levels={QualityLevel.HIGH, QualityLevel.PREMIUM, QualityLevel.ULTRA},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "flac": FormatSpecification(
                extensions={"flac"},
                mime_types={"audio/flac"},
                max_size_mb=800,
                quality_levels={QualityLevel.HIGH, QualityLevel.PREMIUM, QualityLevel.PROFESSIONAL},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            )
        }
    )
    
    # Video Format Specifications
    video_formats: Dict[str, FormatSpecification] = Field(
        default_factory=lambda: {
            "mp4": FormatSpecification(
                extensions={"mp4"},
                mime_types={"video/mp4"},
                max_size_mb=2048,
                quality_levels={QualityLevel.STANDARD, QualityLevel.HIGH, QualityLevel.PREMIUM},
                compression_type=CompressionType.LOSSY,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "mov": FormatSpecification(
                extensions={"mov"},
                mime_types={"video/quicktime"},
                max_size_mb=3072,
                quality_levels={QualityLevel.HIGH, QualityLevel.PREMIUM, QualityLevel.PROFESSIONAL},
                compression_type=CompressionType.HYBRID,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "mkv": FormatSpecification(
                extensions={"mkv"},
                mime_types={"video/x-matroska"},
                max_size_mb=4096,
                quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA, QualityLevel.PROFESSIONAL},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            )
        }
    )
    
    # Image Format Specifications
    image_formats: Dict[str, FormatSpecification] = Field(
        default_factory=lambda: {
            "jpeg": FormatSpecification(
                extensions={"jpeg", "jpg"},
                mime_types={"image/jpeg"},
                max_size_mb=50,
                quality_levels={QualityLevel.BASIC, QualityLevel.STANDARD, QualityLevel.HIGH},
                compression_type=CompressionType.LOSSY,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "png": FormatSpecification(
                extensions={"png"},
                mime_types={"image/png"},
                max_size_mb=100,
                quality_levels={QualityLevel.HIGH, QualityLevel.PREMIUM},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "tiff": FormatSpecification(
                extensions={"tiff", "tif"},
                mime_types={"image/tiff"},
                max_size_mb=200,
                quality_levels={QualityLevel.PREMIUM, QualityLevel.ULTRA, QualityLevel.PROFESSIONAL},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            )
        }
    )
    
    # Text Format Specifications
    text_formats: Dict[str, FormatSpecification] = Field(
        default_factory=lambda: {
            "markdown": FormatSpecification(
                extensions={"md", "markdown"},
                mime_types={"text/markdown"},
                max_size_mb=10,
                quality_levels={QualityLevel.STANDARD, QualityLevel.HIGH},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "pdf": FormatSpecification(
                extensions={"pdf"},
                mime_types={"application/pdf"},
                max_size_mb=50,
                quality_levels={QualityLevel.HIGH, QualityLevel.PREMIUM},
                compression_type=CompressionType.HYBRID,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            )
        }
    )
    
    # Voice Format Specifications
    voice_formats: Dict[str, FormatSpecification] = Field(
        default_factory=lambda: {
            "voice_wav": FormatSpecification(
                extensions={"wav"},
                mime_types={"audio/wav"},
                max_size_mb=100,
                quality_levels={QualityLevel.HIGH, QualityLevel.PREMIUM},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "voice_synthesis": FormatSpecification(
                extensions={"wav", "mp3"},
                mime_types={"audio/wav", "audio/mpeg"},
                max_size_mb=50,
                quality_levels={QualityLevel.STANDARD, QualityLevel.HIGH},
                compression_type=CompressionType.HYBRID,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=False
            )
        }
    )
    
    # Avatar Format Specifications
    avatar_formats: Dict[str, FormatSpecification] = Field(
        default_factory=lambda: {
            "3d_models": FormatSpecification(
                extensions={"fbx", "obj", "gltf"},
                mime_types={"model/fbx", "model/obj", "model/gltf+json"},
                max_size_mb=200,
                quality_levels={QualityLevel.HIGH, QualityLevel.PREMIUM, QualityLevel.PROFESSIONAL},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            ),
            "animations": FormatSpecification(
                extensions={"fbx", "blend"},
                mime_types={"model/fbx", "application/x-blender"},
                max_size_mb=500,
                quality_levels={QualityLevel.PREMIUM, QualityLevel.ULTRA, QualityLevel.PROFESSIONAL},
                compression_type=CompressionType.LOSSLESS,
                professional_grade=True,
                ai_processable=True,
                copyright_detectable=True
            )
        }
    )
    
    # Processing Configuration
    processing_config: ProcessingConfiguration = Field(
        default_factory=lambda: ProcessingConfiguration(
            auto_conversion_enabled=True,
            quality_enhancement=True,
            compression_optimization=True,
            metadata_extraction=True,
            copyright_detection=True,
            ai_analysis=True
        )
    )
    
    # Quality Standards
    quality_standards: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "audio": {
                "min_bitrate": "128kbps",
                "preferred_bitrate": "320kbps",
                "max_bitrate": "1411kbps",
                "sample_rate": "44100Hz",
                "channels": "stereo"
            },
            "video": {
                "min_resolution": "720p",
                "preferred_resolution": "1080p", 
                "max_resolution": "4K",
                "min_framerate": "24fps",
                "preferred_framerate": "30fps",
                "max_framerate": "60fps"
            },
            "image": {
                "min_resolution": "1024x1024",
                "preferred_resolution": "2048x2048",
                "max_resolution": "8192x8192",
                "color_depth": "24bit",
                "dpi": "300"
            }
        }
    )
    
    # Validation Rules
    validation_rules: Dict[str, bool] = Field(
        default_factory=lambda: {
            "format_validation": True,
            "size_validation": True,
            "quality_validation": True,
            "metadata_validation": True,
            "copyright_validation": True,
            "security_scan": True,
            "virus_scan": True,
            "content_moderation": True
        }
    )
    
    # Performance Settings
    conversion_timeout_seconds: int = 600
    parallel_processing_enabled: bool = True
    max_parallel_conversions: int = 5
    cache_converted_files: bool = True
    auto_cleanup_enabled: bool = True
    cleanup_after_hours: int = 24
    
    class Config:
        env_prefix = "CONTENT_FORMAT_"
        case_sensitive = False
        extra = "allow"
    
    def get_format_specification(self, format_type: str, format_name: str) -> Optional[FormatSpecification]:
        """Get format specification by type and name"""
        format_configs = {
            "audio": self.audio_formats,
            "video": self.video_formats,
            "image": self.image_formats,
            "text": self.text_formats,
            "voice": self.voice_formats,
            "avatar": self.avatar_formats
        }
        
        if format_type not in format_configs:
            return None
            
        return format_configs[format_type].get(format_name)
    
    def is_format_supported(self, format_type: str, format_name: str) -> bool:
        """Check if a format is supported"""
        return self.get_format_specification(format_type, format_name) is not None
    
    def get_max_file_size(self, format_type: str, format_name: str) -> int:
        """Get maximum file size for a format"""
        spec = self.get_format_specification(format_type, format_name)
        return spec.max_size_mb if spec else 10
    
    def is_professional_grade(self, format_type: str, format_name: str) -> bool:
        """Check if format is professional grade"""
        spec = self.get_format_specification(format_type, format_name)
        return spec.professional_grade if spec else False
    
    def is_ai_processable(self, format_type: str, format_name: str) -> bool:
        """Check if format can be processed by AI"""
        spec = self.get_format_specification(format_type, format_name)
        return spec.ai_processable if spec else False
    
    def is_copyright_detectable(self, format_type: str, format_name: str) -> bool:
        """Check if format supports copyright detection"""
        spec = self.get_format_specification(format_type, format_name)
        return spec.copyright_detectable if spec else False
    
    def get_supported_extensions(self, format_type: str) -> Set[str]:
        """Get all supported extensions for a format type"""
        format_configs = {
            "audio": self.audio_formats,
            "video": self.video_formats,
            "image": self.image_formats,
            "text": self.text_formats,
            "voice": self.voice_formats,
            "avatar": self.avatar_formats
        }
        
        if format_type not in format_configs:
            return set()
        
        extensions = set()
        for spec in format_configs[format_type].values():
            extensions.update(spec.extensions)
        
        return extensions
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete configuration"""
        errors = []
        
        # Validate format specifications
        format_types = ["audio", "video", "image", "text", "voice", "avatar"]
        for format_type in format_types:
            format_configs = getattr(self, f"{format_type}_formats", {})
            if not format_configs:
                errors.append(f"No {format_type} formats configured")
        
        # Validate quality standards
        if not self.quality_standards:
            errors.append("Quality standards not configured")
        
        # Validate processing configuration
        if not self.processing_config:
            errors.append("Processing configuration not set")
        
        return errors


# Global content format settings instance
content_format_settings = ContentFormatSettings()

__all__ = [
    "ContentFormatSettings",
    "content_format_settings",
    "AudioFormat",
    "VideoFormat", 
    "ImageFormat",
    "TextFormat",
    "VoiceFormat",
    "AvatarFormat",
    "QualityLevel",
    "CompressionType",
    "FormatSpecification",
    "ProcessingConfiguration"
]