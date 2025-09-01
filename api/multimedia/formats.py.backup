"""Multimedia Format Definitions and Specifications
Comprehensive format support for multimedia content processing

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer, Backend Senior Engineer, ML Engineer, 
              Database Administrator, Security Expert, Microservices Architect,
              Multimedia Processing Specialist, DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.
"""
from typing import Dict, List, Set, Optional, Union
from enum import Enum, IntEnum
from dataclasses import dataclass
import mimetypes


class ContentFormat(Enum):
    """Supported content format categories"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    TEXT = "text"
    MULTIMODAL = "multimodal"


class AudioFormat(Enum):
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
    AC3 = "ac3"
    DTS = "dts"


class VideoFormat(Enum):
    """Professional video format support"""
    MP4 = "mp4"
    AVI = "avi"
    MKV = "mkv"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"
    M4V = "m4v"
    MPG = "mpg"
    MPEG = "mpeg"
    TS = "ts"
    M2TS = "m2ts"
    F4V = "f4v"
    ASF = "asf"
    RM = "rm"
    RMVB = "rmvb"


class ImageFormat(Enum):
    """Professional image format support"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    TIF = "tif"
    WEBP = "webp"
    SVG = "svg"
    ICO = "ico"
    PSD = "psd"
    AI = "ai"
    EPS = "eps"
    PDF = "pdf"
    HEIC = "heic"
    HEIF = "heif"
    RAW = "raw"
    CR2 = "cr2"
    NEF = "nef"
    ARW = "arw"


class QualityLevel(IntEnum):
    """Content quality levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    ULTRA = 4
    STUDIO = 5


class CompressionType(Enum):
    """Compression algorithms"""
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    HYBRID = "hybrid"


@dataclass
class FormatSpecification:
    """Format specification details"""
    name: str
    extensions: Set[str]
    mime_types: Set[str]
    max_file_size: Optional[int] = None
    supports_metadata: bool = True
    supports_compression: bool = True
    compression_type: CompressionType = CompressionType.LOSSY
    quality_levels: Set[QualityLevel] = None
    streaming_support: bool = False
    professional_grade: bool = False


@dataclass
class AudioSpecification(FormatSpecification):
    """Audio format specifications"""
    max_sample_rate: Optional[int] = None
    max_bit_depth: Optional[int] = None
    max_channels: Optional[int] = None
    supports_drm: bool = False
    supports_chapters: bool = False
    supports_lyrics: bool = False


@dataclass
class VideoSpecification(FormatSpecification):
    """Video format specifications"""
    max_resolution: Optional[tuple] = None
    max_fps: Optional[int] = None
    supports_hdr: bool = False
    supports_dolby: bool = False
    supports_subtitles: bool = False
    supports_chapters: bool = False
    supports_multiple_audio: bool = False


@dataclass
class ImageSpecification(FormatSpecification):
    """Image format specifications"""
    max_resolution: Optional[tuple] = None
    supports_transparency: bool = False
    supports_animation: bool = False
    supports_layers: bool = False
    color_depth: Optional[int] = None
    supports_icc_profile: bool = False


class SupportedFormats:
    """Comprehensive format support definitions"""
    
    AUDIO_FORMATS = {
        AudioFormat.MP3: AudioSpecification(
            name="MPEG Audio Layer III",
            extensions={"mp3"},
            mime_types={"audio/mpeg", "audio/mp3"},
            max_sample_rate=48000,
            max_bit_depth=16,
            max_channels=2,
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.LOW, QualityLevel.MEDIUM, QualityLevel.HIGH},
            streaming_support=True,
            professional_grade=True,
            supports_lyrics=True
        ),
        AudioFormat.WAV: AudioSpecification(
            name="Waveform Audio File",
            extensions={"wav"},
            mime_types={"audio/wav", "audio/wave"},
            max_sample_rate=192000,
            max_bit_depth=32,
            max_channels=8,
            compression_type=CompressionType.LOSSLESS,
            quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA, QualityLevel.STUDIO},
            professional_grade=True
        ),
        AudioFormat.FLAC: AudioSpecification(
            name="Free Lossless Audio Codec",
            extensions={"flac"},
            mime_types={"audio/flac"},
            max_sample_rate=655350,
            max_bit_depth=32,
            max_channels=8,
            compression_type=CompressionType.LOSSLESS,
            quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA, QualityLevel.STUDIO},
            professional_grade=True,
            supports_chapters=True
        ),
        AudioFormat.AAC: AudioSpecification(
            name="Advanced Audio Coding",
            extensions={"aac", "m4a"},
            mime_types={"audio/aac", "audio/mp4"},
            max_sample_rate=96000,
            max_bit_depth=16,
            max_channels=48,
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.MEDIUM, QualityLevel.HIGH, QualityLevel.ULTRA},
            streaming_support=True,
            professional_grade=True,
            supports_drm=True
        ),
        AudioFormat.OGG: AudioSpecification(
            name="Ogg Vorbis",
            extensions={"ogg"},
            mime_types={"audio/ogg"},
            max_sample_rate=192000,
            max_bit_depth=32,
            max_channels=255,
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.MEDIUM, QualityLevel.HIGH},
            streaming_support=True
        )
    }
    
    VIDEO_FORMATS = {
        VideoFormat.MP4: VideoSpecification(
            name="MPEG-4 Part 14",
            extensions={"mp4", "m4v"},
            mime_types={"video/mp4"},
            max_resolution=(7680, 4320),  # 8K
            max_fps=120,
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.LOW, QualityLevel.MEDIUM, QualityLevel.HIGH, QualityLevel.ULTRA},
            streaming_support=True,
            professional_grade=True,
            supports_hdr=True,
            supports_dolby=True,
            supports_subtitles=True,
            supports_chapters=True,
            supports_multiple_audio=True
        ),
        VideoFormat.MKV: VideoSpecification(
            name="Matroska Video",
            extensions={"mkv"},
            mime_types={"video/x-matroska"},
            max_resolution=(7680, 4320),
            max_fps=120,
            compression_type=CompressionType.HYBRID,
            quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA, QualityLevel.STUDIO},
            professional_grade=True,
            supports_hdr=True,
            supports_dolby=True,
            supports_subtitles=True,
            supports_chapters=True,
            supports_multiple_audio=True
        ),
        VideoFormat.AVI: VideoSpecification(
            name="Audio Video Interleave",
            extensions={"avi"},
            mime_types={"video/x-msvideo"},
            max_resolution=(1920, 1080),
            max_fps=60,
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.MEDIUM, QualityLevel.HIGH}
        ),
        VideoFormat.MOV: VideoSpecification(
            name="QuickTime Movie",
            extensions={"mov"},
            mime_types={"video/quicktime"},
            max_resolution=(7680, 4320),
            max_fps=120,
            compression_type=CompressionType.HYBRID,
            quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA, QualityLevel.STUDIO},
            professional_grade=True,
            supports_hdr=True,
            supports_chapters=True,
            supports_multiple_audio=True
        ),
        VideoFormat.WEBM: VideoSpecification(
            name="WebM Video",
            extensions={"webm"},
            mime_types={"video/webm"},
            max_resolution=(3840, 2160),  # 4K
            max_fps=60,
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.MEDIUM, QualityLevel.HIGH},
            streaming_support=True
        )
    }
    
    IMAGE_FORMATS = {
        ImageFormat.JPEG: ImageSpecification(
            name="Joint Photographic Experts Group",
            extensions={"jpg", "jpeg"},
            mime_types={"image/jpeg"},
            max_resolution=(65535, 65535),
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.LOW, QualityLevel.MEDIUM, QualityLevel.HIGH},
            color_depth=24,
            supports_icc_profile=True,
            professional_grade=True
        ),
        ImageFormat.PNG: ImageSpecification(
            name="Portable Network Graphics",
            extensions={"png"},
            mime_types={"image/png"},
            max_resolution=(2147483647, 2147483647),
            compression_type=CompressionType.LOSSLESS,
            quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA},
            supports_transparency=True,
            color_depth=48,
            supports_icc_profile=True,
            professional_grade=True
        ),
        ImageFormat.GIF: ImageSpecification(
            name="Graphics Interchange Format",
            extensions={"gif"},
            mime_types={"image/gif"},
            max_resolution=(65535, 65535),
            compression_type=CompressionType.LOSSLESS,
            supports_transparency=True,
            supports_animation=True,
            color_depth=8
        ),
        ImageFormat.TIFF: ImageSpecification(
            name="Tagged Image File Format",
            extensions={"tiff", "tif"},
            mime_types={"image/tiff"},
            max_resolution=(4294967295, 4294967295),
            compression_type=CompressionType.LOSSLESS,
            quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA, QualityLevel.STUDIO},
            supports_layers=True,
            color_depth=64,
            supports_icc_profile=True,
            professional_grade=True
        ),
        ImageFormat.WEBP: ImageSpecification(
            name="WebP Image Format",
            extensions={"webp"},
            mime_types={"image/webp"},
            max_resolution=(16383, 16383),
            compression_type=CompressionType.HYBRID,
            quality_levels={QualityLevel.MEDIUM, QualityLevel.HIGH},
            supports_transparency=True,
            supports_animation=True,
            color_depth=24
        ),
        ImageFormat.HEIC: ImageSpecification(
            name="High Efficiency Image Container",
            extensions={"heic", "heif"},
            mime_types={"image/heic", "image/heif"},
            max_resolution=(8192, 8192),
            compression_type=CompressionType.LOSSY,
            quality_levels={QualityLevel.HIGH, QualityLevel.ULTRA},
            color_depth=30,
            supports_icc_profile=True,
            professional_grade=True
        )
    }
    
    @classmethod
    def get_format_by_extension(cls, extension: str) -> Optional[Union[AudioFormat, VideoFormat, ImageFormat]]:
        """Get format enum by file extension"""
        extension = extension.lower().lstrip('.')
        
        for format_enum, spec in cls.AUDIO_FORMATS.items():
            if extension in spec.extensions:
                return format_enum
                
        for format_enum, spec in cls.VIDEO_FORMATS.items():
            if extension in spec.extensions:
                return format_enum
                
        for format_enum, spec in cls.IMAGE_FORMATS.items():
            if extension in spec.extensions:
                return format_enum
                
        return None
    
    @classmethod
    def get_format_by_mime_type(cls, mime_type: str) -> Optional[Union[AudioFormat, VideoFormat, ImageFormat]]:
        """Get format enum by MIME type"""
        mime_type = mime_type.lower()
        
        for format_enum, spec in cls.AUDIO_FORMATS.items():
            if mime_type in spec.mime_types:
                return format_enum
                
        for format_enum, spec in cls.VIDEO_FORMATS.items():
            if mime_type in spec.mime_types:
                return format_enum
                
        for format_enum, spec in cls.IMAGE_FORMATS.items():
            if mime_type in spec.mime_types:
                return format_enum
                
        return None
    
    @classmethod
    def is_audio_format(cls, format_or_extension: Union[str, AudioFormat]) -> bool:
        """Check if format is audio"""
        if isinstance(format_or_extension, AudioFormat):
            return True
        return cls.get_format_by_extension(format_or_extension) in cls.AUDIO_FORMATS
    
    @classmethod
    def is_video_format(cls, format_or_extension: Union[str, VideoFormat]) -> bool:
        """Check if format is video"""
        if isinstance(format_or_extension, VideoFormat):
            return True
        return cls.get_format_by_extension(format_or_extension) in cls.VIDEO_FORMATS
    
    @classmethod
    def is_image_format(cls, format_or_extension: Union[str, ImageFormat]) -> bool:
        """Check if format is image"""
        if isinstance(format_or_extension, ImageFormat):
            return True
        return cls.get_format_by_extension(format_or_extension) in cls.IMAGE_FORMATS
    
    @classmethod
    def get_supported_extensions(cls) -> Set[str]:
        """Get all supported file extensions"""
        extensions = set()
        
        for spec in cls.AUDIO_FORMATS.values():
            extensions.update(spec.extensions)
        for spec in cls.VIDEO_FORMATS.values():
            extensions.update(spec.extensions)
        for spec in cls.IMAGE_FORMATS.values():
            extensions.update(spec.extensions)
            
        return extensions
    
    @classmethod
    def get_mime_types(cls) -> Set[str]:
        """Get all supported MIME types"""
        mime_types = set()
        
        for spec in cls.AUDIO_FORMATS.values():
            mime_types.update(spec.mime_types)
        for spec in cls.VIDEO_FORMATS.values():
            mime_types.update(spec.mime_types)
        for spec in cls.IMAGE_FORMATS.values():
            mime_types.update(spec.mime_types)
            
        return mime_types
    
    @classmethod
    def get_professional_formats(cls) -> Dict[ContentFormat, List]:
        """Get professional-grade formats by category"""
        return {
            ContentFormat.AUDIO: [
                fmt for fmt, spec in cls.AUDIO_FORMATS.items() 
                if spec.professional_grade
            ],
            ContentFormat.VIDEO: [
                fmt for fmt, spec in cls.VIDEO_FORMATS.items() 
                if spec.professional_grade
            ],
            ContentFormat.IMAGE: [
                fmt for fmt, spec in cls.IMAGE_FORMATS.items() 
                if spec.professional_grade
            ]
        }
