"""Content Formats Module - Professional Content Format Management System

Module avancé pour la gestion des formats de contenu multimédia et leurs
caractéristiques techniques dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Multimedia Expert, Format Specialist, Technical Architect
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import logging
import mimetypes
import magic
from enum import Enum

logger = logging.getLogger(__name__)

class MediaCategory(Enum):
    """Primary media categories"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    MULTIMEDIA = "multimedia"
    INTERACTIVE = "interactive"

class CompressionType(Enum):
    """Content compression types"""    NONE = "none"
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    ADAPTIVE = "adaptive"

class QualityTier(Enum):
    """Content quality tiers"""    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PROFESSIONAL = "professional"
    BROADCAST = "broadcast"
    STUDIO = "studio"

class UsageRights(Enum):
    """Content usage rights levels"""    PUBLIC_DOMAIN = "public_domain"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    EXCLUSIVE = "exclusive"
    RESTRICTED = "restricted"

@dataclass
class FormatSpecification:
    """Technical specifications for content formats"""    mime_type: str
    file_extensions: List[str]
    category: MediaCategory
    compression: CompressionType
    quality_tier: QualityTier
    
    # Technical characteristics
    supports_metadata: bool = True
    supports_transparency: bool = False
    supports_animation: bool = False
    supports_layers: bool = False
    supports_streaming: bool = False
    
    # Quality metrics
    max_resolution: Optional[Tuple[int, int]] = None
    max_bitrate: Optional[int] = None
    max_sample_rate: Optional[int] = None
    color_depth: Optional[int] = None
    
    # Processing capabilities
    web_compatible: bool = True
    mobile_optimized: bool = True
    seo_friendly: bool = True
    platform_support: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata support
    exif_support: bool = False
    iptc_support: bool = False
    xmp_support: bool = False
    id3_support: bool = False
    
    def __post_init__(self):
        """Initialize platform support if not provided"""        if not self.platform_support:
            self.platform_support = {
                'web': self.web_compatible,
                'mobile': self.mobile_optimized,
                'desktop': True,
                'streaming': self.supports_streaming
            }

class AudioFormat:
    """Audio format specifications and capabilities"""    
    MP3 = FormatSpecification(
        mime_type="audio/mpeg",
        file_extensions=[".mp3"],
        category=MediaCategory.AUDIO,
        compression=CompressionType.LOSSY,
        quality_tier=QualityTier.STANDARD,
        max_bitrate=320,
        max_sample_rate=48000,
        supports_streaming=True,
        web_compatible=True,
        mobile_optimized=True,
        id3_support=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'streaming': True,
            'spotify': True,
            'youtube': True,
            'soundcloud': True
        }
    )
    
    WAV = FormatSpecification(
        mime_type="audio/wav",
        file_extensions=[".wav"],
        category=MediaCategory.AUDIO,
        compression=CompressionType.NONE,
        quality_tier=QualityTier.PROFESSIONAL,
        max_bitrate=1411,  # CD quality
        max_sample_rate=192000,
        supports_streaming=False,
        web_compatible=True,
        mobile_optimized=False,
        platform_support={
            'web': True,
            'mobile': False,
            'desktop': True,
            'streaming': False,
            'professional': True
        }
    )
    
    FLAC = FormatSpecification(
        mime_type="audio/flac",
        file_extensions=[".flac"],
        category=MediaCategory.AUDIO,
        compression=CompressionType.LOSSLESS,
        quality_tier=QualityTier.STUDIO,
        max_sample_rate=192000,
        supports_streaming=True,
        web_compatible=True,
        mobile_optimized=False,
        platform_support={
            'web': True,
            'mobile': False,
            'desktop': True,
            'streaming': True,
            'audiophile': True,
            'tidal': True
        }
    )
    
    AAC = FormatSpecification(
        mime_type="audio/aac",
        file_extensions=[".aac", ".m4a"],
        category=MediaCategory.AUDIO,
        compression=CompressionType.LOSSY,
        quality_tier=QualityTier.HIGH,
        max_bitrate=512,
        max_sample_rate=96000,
        supports_streaming=True,
        web_compatible=True,
        mobile_optimized=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'streaming': True,
            'apple': True,
            'youtube': True
        }
    )
    
    OGG = FormatSpecification(
        mime_type="audio/ogg",
        file_extensions=[".ogg", ".oga"],
        category=MediaCategory.AUDIO,
        compression=CompressionType.LOSSY,
        quality_tier=QualityTier.HIGH,
        max_bitrate=500,
        max_sample_rate=48000,
        supports_streaming=True,
        web_compatible=True,
        mobile_optimized=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'streaming': True,
            'open_source': True
        }
    )

class VideoFormat:
    """Video format specifications and capabilities"""    
    MP4 = FormatSpecification(
        mime_type="video/mp4",
        file_extensions=[".mp4"],
        category=MediaCategory.VIDEO,
        compression=CompressionType.LOSSY,
        quality_tier=QualityTier.HIGH,
        max_resolution=(7680, 4320),  # 8K
        max_bitrate=100000,  # 100 Mbps
        supports_streaming=True,
        web_compatible=True,
        mobile_optimized=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'streaming': True,
            'youtube': True,
            'instagram': True,
            'tiktok': True,
            'facebook': True
        }
    )
    
    WEBM = FormatSpecification(
        mime_type="video/webm",
        file_extensions=[".webm"],
        category=MediaCategory.VIDEO,
        compression=CompressionType.LOSSY,
        quality_tier=QualityTier.HIGH,
        max_resolution=(7680, 4320),
        supports_streaming=True,
        web_compatible=True,
        mobile_optimized=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'streaming': True,
            'open_source': True
        }
    )
    
    MOV = FormatSpecification(
        mime_type="video/quicktime",
        file_extensions=[".mov"],
        category=MediaCategory.VIDEO,
        compression=CompressionType.LOSSY,
        quality_tier=QualityTier.PROFESSIONAL,
        max_resolution=(7680, 4320),
        supports_streaming=False,
        web_compatible=False,
        mobile_optimized=False,
        platform_support={
            'web': False,
            'mobile': False,
            'desktop': True,
            'professional': True,
            'apple': True
        }
    )
    
    AVI = FormatSpecification(
        mime_type="video/x-msvideo",
        file_extensions=[".avi"],
        category=MediaCategory.VIDEO,
        compression=CompressionType.ADAPTIVE,
        quality_tier=QualityTier.STANDARD,
        max_resolution=(1920, 1080),
        supports_streaming=False,
        web_compatible=False,
        mobile_optimized=False,
        platform_support={
            'web': False,
            'mobile': False,
            'desktop': True,
            'legacy': True
        }
    )

class ImageFormat:
    """Image format specifications and capabilities"""    
    JPEG = FormatSpecification(
        mime_type="image/jpeg",
        file_extensions=[".jpg", ".jpeg"],
        category=MediaCategory.IMAGE,
        compression=CompressionType.LOSSY,
        quality_tier=QualityTier.STANDARD,
        max_resolution=(65535, 65535),
        color_depth=24,
        supports_transparency=False,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=True,
        exif_support=True,
        iptc_support=True,
        xmp_support=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'social_media': True,
            'print': True
        }
    )
    
    PNG = FormatSpecification(
        mime_type="image/png",
        file_extensions=[".png"],
        category=MediaCategory.IMAGE,
        compression=CompressionType.LOSSLESS,
        quality_tier=QualityTier.HIGH,
        max_resolution=(2147483647, 2147483647),
        color_depth=48,
        supports_transparency=True,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'graphics': True,
            'transparency': True
        }
    )
    
    WEBP = FormatSpecification(
        mime_type="image/webp",
        file_extensions=[".webp"],
        category=MediaCategory.IMAGE,
        compression=CompressionType.ADAPTIVE,
        quality_tier=QualityTier.HIGH,
        max_resolution=(16383, 16383),
        color_depth=32,
        supports_transparency=True,
        supports_animation=True,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'modern_browsers': True,
            'google': True
        }
    )
    
    TIFF = FormatSpecification(
        mime_type="image/tiff",
        file_extensions=[".tiff", ".tif"],
        category=MediaCategory.IMAGE,
        compression=CompressionType.LOSSLESS,
        quality_tier=QualityTier.PROFESSIONAL,
        max_resolution=(4294967295, 4294967295),
        color_depth=64,
        supports_transparency=True,
        supports_layers=True,
        web_compatible=False,
        mobile_optimized=False,
        exif_support=True,
        iptc_support=True,
        xmp_support=True,
        platform_support={
            'web': False,
            'mobile': False,
            'desktop': True,
            'professional': True,
            'print': True,
            'archival': True
        }
    )
    
    GIF = FormatSpecification(
        mime_type="image/gif",
        file_extensions=[".gif"],
        category=MediaCategory.IMAGE,
        compression=CompressionType.LOSSLESS,
        quality_tier=QualityTier.STANDARD,
        max_resolution=(65535, 65535),
        color_depth=8,
        supports_transparency=True,
        supports_animation=True,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'social_media': True,
            'animation': True
        }
    )

class TextFormat:
    """Text format specifications and capabilities"""    
    PLAIN = FormatSpecification(
        mime_type="text/plain",
        file_extensions=[".txt"],
        category=MediaCategory.TEXT,
        compression=CompressionType.NONE,
        quality_tier=QualityTier.STANDARD,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'universal': True
        }
    )
    
    MARKDOWN = FormatSpecification(
        mime_type="text/markdown",
        file_extensions=[".md", ".markdown"],
        category=MediaCategory.TEXT,
        compression=CompressionType.NONE,
        quality_tier=QualityTier.HIGH,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'documentation': True,
            'cms': True
        }
    )
    
    HTML = FormatSpecification(
        mime_type="text/html",
        file_extensions=[".html", ".htm"],
        category=MediaCategory.TEXT,
        compression=CompressionType.NONE,
        quality_tier=QualityTier.HIGH,
        supports_metadata=True,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=True,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'browsers': True,
            'seo': True
        }
    )
    
    PDF = FormatSpecification(
        mime_type="application/pdf",
        file_extensions=[".pdf"],
        category=MediaCategory.DOCUMENT,
        compression=CompressionType.ADAPTIVE,
        quality_tier=QualityTier.PROFESSIONAL,
        supports_metadata=True,
        web_compatible=True,
        mobile_optimized=True,
        seo_friendly=False,
        platform_support={
            'web': True,
            'mobile': True,
            'desktop': True,
            'print': True,
            'professional': True,
            'archival': True
        }
    )

class FormatDetector:
    """Advanced format detection and validation"""    
    def __init__(self):
        self.magic_detector = magic.Magic(mime=True)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._format_registry = self._build_format_registry()
    
    def _build_format_registry(self) -> Dict[str, FormatSpecification]:
        """Build comprehensive format registry"""        registry = {}
        
        # Audio formats
        for attr_name in dir(AudioFormat):
            if not attr_name.startswith('_'):
                format_spec = getattr(AudioFormat, attr_name)
                if isinstance(format_spec, FormatSpecification):
                    registry[format_spec.mime_type] = format_spec
                    for ext in format_spec.file_extensions:
                        registry[ext.lower()] = format_spec
        
        # Video formats
        for attr_name in dir(VideoFormat):
            if not attr_name.startswith('_'):
                format_spec = getattr(VideoFormat, attr_name)
                if isinstance(format_spec, FormatSpecification):
                    registry[format_spec.mime_type] = format_spec
                    for ext in format_spec.file_extensions:
                        registry[ext.lower()] = format_spec
        
        # Image formats
        for attr_name in dir(ImageFormat):
            if not attr_name.startswith('_'):
                format_spec = getattr(ImageFormat, attr_name)
                if isinstance(format_spec, FormatSpecification):
                    registry[format_spec.mime_type] = format_spec
                    for ext in format_spec.file_extensions:
                        registry[ext.lower()] = format_spec
        
        # Text formats
        for attr_name in dir(TextFormat):
            if not attr_name.startswith('_'):
                format_spec = getattr(TextFormat, attr_name)
                if isinstance(format_spec, FormatSpecification):
                    registry[format_spec.mime_type] = format_spec
                    for ext in format_spec.file_extensions:
                        registry[ext.lower()] = format_spec
        
        return registry
    
    def detect_format(self, file_path: Path) -> Optional[FormatSpecification]:
        """Detect content format from file"""        try:
            # First try magic number detection
            mime_type = self.magic_detector.from_file(str(file_path))
            if mime_type in self._format_registry:
                return self._format_registry[mime_type]
            
            # Fallback to extension detection
            extension = file_path.suffix.lower()
            if extension in self._format_registry:
                return self._format_registry[extension]
            
            # Fallback to mimetypes library
            guessed_type, _ = mimetypes.guess_type(str(file_path))
            if guessed_type and guessed_type in self._format_registry:
                return self._format_registry[guessed_type]
            
            self.logger.warning(f"Unknown format for file: {file_path}")
            return None
            
        except Exception as e:
            self.logger.error(f"Format detection failed: {e}")
            return None
    
    def is_supported_format(self, file_path: Path) -> bool:
        """Check if format is supported"""        return self.detect_format(file_path) is not None
    
    def get_supported_extensions(self, category: MediaCategory = None) -> Set[str]:
        """Get all supported file extensions"""        extensions = set()
        
        for format_spec in self._format_registry.values():
            if isinstance(format_spec, FormatSpecification):
                if category is None or format_spec.category == category:
                    extensions.update(format_spec.file_extensions)
        
        return extensions
    
    def get_web_compatible_formats(self, category: MediaCategory = None) -> List[FormatSpecification]:
        """Get web-compatible formats"""        formats = []
        
        for format_spec in self._format_registry.values():
            if isinstance(format_spec, FormatSpecification):
                if format_spec.web_compatible:
                    if category is None or format_spec.category == category:
                        if format_spec not in formats:  # Avoid duplicates
                            formats.append(format_spec)
        
        return formats
    
    def get_platform_compatible_formats(self, platform: str, 
                                      category: MediaCategory = None) -> List[FormatSpecification]:
        """Get formats compatible with specific platform"""        formats = []
        
        for format_spec in self._format_registry.values():
            if isinstance(format_spec, FormatSpecification):
                if format_spec.platform_support.get(platform, False):
                    if category is None or format_spec.category == category:
                        if format_spec not in formats:  # Avoid duplicates
                            formats.append(format_spec)
        
        return formats

class FormatConverter:
    """Format conversion recommendations and capabilities"""    
    def __init__(self):
        self.detector = FormatDetector()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_conversion_recommendations(self, source_format: FormatSpecification,
                                     target_platform: str = None,
                                     quality_requirement: QualityTier = None) -> List[FormatSpecification]:
        """Get recommended conversion targets"""        recommendations = []
        
        # Filter by category
        candidate_formats = [
            fmt for fmt in self.detector._format_registry.values()
            if isinstance(fmt, FormatSpecification) and fmt.category == source_format.category
        ]
        
        # Filter by platform compatibility
        if target_platform:
            candidate_formats = [
                fmt for fmt in candidate_formats
                if fmt.platform_support.get(target_platform, False)
            ]
        
        # Filter by quality requirement
        if quality_requirement:
            quality_order = {
                QualityTier.DRAFT: 1,
                QualityTier.STANDARD: 2,
                QualityTier.HIGH: 3,
                QualityTier.PROFESSIONAL: 4,
                QualityTier.BROADCAST: 5,
                QualityTier.STUDIO: 6
            }
            
            required_level = quality_order.get(quality_requirement, 3)
            candidate_formats = [
                fmt for fmt in candidate_formats
                if quality_order.get(fmt.quality_tier, 3) >= required_level
            ]
        
        # Remove duplicates and sort by quality
        seen_mime_types = set()
        for fmt in sorted(candidate_formats, 
                         key=lambda x: (x.web_compatible, x.mobile_optimized, x.quality_tier.value),
                         reverse=True):
            if fmt.mime_type not in seen_mime_types:
                recommendations.append(fmt)
                seen_mime_types.add(fmt.mime_type)
        
        return recommendations
    
    def get_optimal_format_for_platform(self, source_format: FormatSpecification,
                                       platform: str) -> Optional[FormatSpecification]:
        """Get optimal format for specific platform"""        recommendations = self.get_conversion_recommendations(
            source_format, target_platform=platform
        )
        
        if not recommendations:
            return None
        
        # Return the best recommendation
        return recommendations[0]
    
    def estimate_file_size_change(self, source_format: FormatSpecification,
                                target_format: FormatSpecification,
                                source_size: int) -> Tuple[int, float]:
        """Estimate file size change after conversion"""        # Compression ratio estimates based on format characteristics
        compression_ratios = {
            CompressionType.NONE: 1.0,
            CompressionType.LOSSLESS: 0.5,
            CompressionType.LOSSY: 0.1,
            CompressionType.ADAPTIVE: 0.3
        }
        
        source_ratio = compression_ratios.get(source_format.compression, 0.5)
        target_ratio = compression_ratios.get(target_format.compression, 0.5)
        
        # Calculate size change factor
        size_factor = target_ratio / source_ratio
        
        # Adjust for quality differences
        quality_adjustments = {
            QualityTier.DRAFT: 0.5,
            QualityTier.STANDARD: 0.8,
            QualityTier.HIGH: 1.0,
            QualityTier.PROFESSIONAL: 1.5,
            QualityTier.BROADCAST: 2.0,
            QualityTier.STUDIO: 3.0
        }
        
        source_quality = quality_adjustments.get(source_format.quality_tier, 1.0)
        target_quality = quality_adjustments.get(target_format.quality_tier, 1.0)
        
        quality_factor = target_quality / source_quality
        
        final_factor = size_factor * quality_factor
        estimated_size = int(source_size * final_factor)
        
        return estimated_size, final_factor

# Export all classes and enums
__all__ = [
    'MediaCategory',
    'CompressionType',
    'QualityTier',
    'UsageRights',
    'FormatSpecification',
    'AudioFormat',
    'VideoFormat',
    'ImageFormat',
    'TextFormat',
    'FormatDetector',
    'FormatConverter'
]
