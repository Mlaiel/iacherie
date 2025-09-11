"""
Container Formats Management System
Enterprise-grade multimedia container format handling for Ainflue Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import mimetypes
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ContainerType(Enum):
    """Container format types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    MIXED = "mixed"


@dataclass
class ContainerFormat:
    """Container format specification"""
    name: str
    extension: str
    mime_type: str
    container_type: ContainerType
    supported_codecs: List[str]
    max_streams: int
    supports_chapters: bool
    supports_metadata: bool
    supports_subtitles: bool
    supports_attachments: bool
    quality_preserving: bool
    streaming_optimized: bool
    description: str


class ContainerFormatRegistry:
    """Enterprise container format registry and management system"""
    
    def __init__(self):
        self.formats: Dict[str, ContainerFormat] = {}
        self._initialize_formats()
    
    def _initialize_formats(self):
        """Initialize supported container formats"""
        
        # Video containers
        self.register_format(ContainerFormat(
            name="MP4",
            extension="mp4",
            mime_type="video/mp4",
            container_type=ContainerType.VIDEO,
            supported_codecs=["h264", "h265", "av1", "aac", "mp3"],
            max_streams=256,
            supports_chapters=True,
            supports_metadata=True,
            supports_subtitles=True,
            supports_attachments=True,
            quality_preserving=True,
            streaming_optimized=True,
            description="MPEG-4 Part 14 - Universal video container"
        ))
        
        self.register_format(ContainerFormat(
            name="WebM",
            extension="webm",
            mime_type="video/webm",
            container_type=ContainerType.VIDEO,
            supported_codecs=["vp8", "vp9", "av1", "opus", "vorbis"],
            max_streams=128,
            supports_chapters=True,
            supports_metadata=True,
            supports_subtitles=True,
            supports_attachments=False,
            quality_preserving=True,
            streaming_optimized=True,
            description="WebM - Open web video container"
        ))
        
        self.register_format(ContainerFormat(
            name="Matroska",
            extension="mkv",
            mime_type="video/x-matroska",
            container_type=ContainerType.VIDEO,
            supported_codecs=["h264", "h265", "av1", "vp9", "aac", "opus", "flac"],
            max_streams=65535,
            supports_chapters=True,
            supports_metadata=True,
            supports_subtitles=True,
            supports_attachments=True,
            quality_preserving=True,
            streaming_optimized=False,
            description="Matroska - Feature-rich open container"
        ))
        
        # Audio containers
        self.register_format(ContainerFormat(
            name="MP3",
            extension="mp3",
            mime_type="audio/mpeg",
            container_type=ContainerType.AUDIO,
            supported_codecs=["mp3"],
            max_streams=1,
            supports_chapters=False,
            supports_metadata=True,
            supports_subtitles=False,
            supports_attachments=True,
            quality_preserving=False,
            streaming_optimized=True,
            description="MPEG-1 Audio Layer III"
        ))
        
        self.register_format(ContainerFormat(
            name="FLAC",
            extension="flac",
            mime_type="audio/flac",
            container_type=ContainerType.AUDIO,
            supported_codecs=["flac"],
            max_streams=1,
            supports_chapters=True,
            supports_metadata=True,
            supports_subtitles=False,
            supports_attachments=True,
            quality_preserving=True,
            streaming_optimized=False,
            description="Free Lossless Audio Codec"
        ))
        
        self.register_format(ContainerFormat(
            name="Ogg",
            extension="ogg",
            mime_type="audio/ogg",
            container_type=ContainerType.AUDIO,
            supported_codecs=["vorbis", "opus", "flac"],
            max_streams=256,
            supports_chapters=True,
            supports_metadata=True,
            supports_subtitles=False,
            supports_attachments=False,
            quality_preserving=True,
            streaming_optimized=True,
            description="Ogg - Open multimedia container"
        ))
        
        # Image containers
        self.register_format(ContainerFormat(
            name="TIFF",
            extension="tiff",
            mime_type="image/tiff",
            container_type=ContainerType.IMAGE,
            supported_codecs=["uncompressed", "lzw", "jpeg"],
            max_streams=1,
            supports_chapters=False,
            supports_metadata=True,
            supports_subtitles=False,
            supports_attachments=False,
            quality_preserving=True,
            streaming_optimized=False,
            description="Tagged Image File Format"
        ))
        
        # Mixed media containers
        self.register_format(ContainerFormat(
            name="AVI",
            extension="avi",
            mime_type="video/x-msvideo",
            container_type=ContainerType.MIXED,
            supported_codecs=["h264", "xvid", "divx", "mp3", "pcm"],
            max_streams=100,
            supports_chapters=False,
            supports_metadata=True,
            supports_subtitles=False,
            supports_attachments=False,
            quality_preserving=True,
            streaming_optimized=False,
            description="Audio Video Interleave - Legacy container"
        ))
    
    def register_format(self, container_format: ContainerFormat):
        """Register a new container format"""
        self.formats[container_format.extension.lower()] = container_format
        logger.info(f"Registered container format: {container_format.name}")
    
    def get_format(self, extension: str) -> Optional[ContainerFormat]:
        """Get container format by extension"""
        return self.formats.get(extension.lower().lstrip('.'))
    
    def get_formats_by_type(self, container_type: ContainerType) -> List[ContainerFormat]:
        """Get all formats of a specific type"""
        return [fmt for fmt in self.formats.values() if fmt.container_type == container_type]
    
    def get_streaming_optimized_formats(self) -> List[ContainerFormat]:
        """Get formats optimized for streaming"""
        return [fmt for fmt in self.formats.values() if fmt.streaming_optimized]
    
    def get_lossless_formats(self) -> List[ContainerFormat]:
        """Get quality-preserving formats"""
        return [fmt for fmt in self.formats.values() if fmt.quality_preserving]
    
    def supports_codec(self, extension: str, codec: str) -> bool:
        """Check if container supports specific codec"""
        container = self.get_format(extension)
        return container and codec.lower() in [c.lower() for c in container.supported_codecs]
    
    def get_compatible_containers(self, codec: str) -> List[ContainerFormat]:
        """Get containers compatible with codec"""
        return [fmt for fmt in self.formats.values() 
                if codec.lower() in [c.lower() for c in fmt.supported_codecs]]
    
    def detect_container_from_file(self, file_path: str) -> Optional[ContainerFormat]:
        """Detect container format from file"""
        try:
            path = Path(file_path)
            extension = path.suffix.lower().lstrip('.')
            return self.get_format(extension)
        except Exception as e:
            logger.error(f"Error detecting container format: {e}")
            return None
    
    def get_format_recommendations(self, use_case: str) -> List[ContainerFormat]:
        """Get format recommendations for specific use cases"""
        recommendations = []
        
        if use_case.lower() == "web_streaming":
            recommendations = [fmt for fmt in self.formats.values() 
                             if fmt.streaming_optimized and fmt.container_type == ContainerType.VIDEO]
        elif use_case.lower() == "mobile_playback":
            recommendations = [self.get_format("mp4"), self.get_format("webm")]
        elif use_case.lower() == "archival":
            recommendations = [fmt for fmt in self.formats.values() if fmt.quality_preserving]
        elif use_case.lower() == "social_media":
            recommendations = [self.get_format("mp4"), self.get_format("webm")]
        elif use_case.lower() == "professional_editing":
            recommendations = [self.get_format("mkv"), self.get_format("mov")]
        
        return [fmt for fmt in recommendations if fmt is not None]
    
    def validate_container_compatibility(self, container_ext: str, codecs: List[str]) -> Dict[str, bool]:
        """Validate codec compatibility with container"""
        container = self.get_format(container_ext)
        if not container:
            return {codec: False for codec in codecs}
        
        return {
            codec: codec.lower() in [c.lower() for c in container.supported_codecs]
            for codec in codecs
        }
    
    def get_feature_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Get comprehensive feature matrix for all containers"""
        matrix = {}
        for ext, fmt in self.formats.items():
            matrix[ext] = {
                "chapters": fmt.supports_chapters,
                "metadata": fmt.supports_metadata,
                "subtitles": fmt.supports_subtitles,
                "attachments": fmt.supports_attachments,
                "streaming": fmt.streaming_optimized,
                "lossless": fmt.quality_preserving
            }
        return matrix


# Global registry instance
container_registry = ContainerFormatRegistry()


class ContainerAnalyzer:
    """Advanced container analysis and optimization"""
    
    def __init__(self):
        self.registry = container_registry
    
    def analyze_container_efficiency(self, container_ext: str, content_type: str) -> Dict[str, Any]:
        """Analyze container efficiency for content type"""
        container = self.registry.get_format(container_ext)
        if not container:
            return {"error": "Container format not supported"}
        
        efficiency_score = 0
        factors = []
        
        # Streaming optimization
        if container.streaming_optimized:
            efficiency_score += 25
            factors.append("Streaming optimized")
        
        # Quality preservation
        if container.quality_preserving:
            efficiency_score += 20
            factors.append("Quality preserving")
        
        # Feature support
        if container.supports_metadata:
            efficiency_score += 15
            factors.append("Metadata support")
        
        if container.supports_subtitles:
            efficiency_score += 10
            factors.append("Subtitle support")
        
        # Content type matching
        if content_type.startswith(container.container_type.value):
            efficiency_score += 20
            factors.append("Content type match")
        
        return {
            "container": container.name,
            "efficiency_score": min(efficiency_score, 100),
            "factors": factors,
            "recommendations": self._get_optimization_recommendations(container)
        }
    
    def _get_optimization_recommendations(self, container: ContainerFormat) -> List[str]:
        """Get optimization recommendations for container"""
        recommendations = []
        
        if not container.streaming_optimized:
            recommendations.append("Consider MP4 or WebM for better streaming")
        
        if not container.quality_preserving and container.container_type == ContainerType.AUDIO:
            recommendations.append("Use FLAC for lossless audio archiving")
        
        if container.max_streams < 10:
            recommendations.append("Limited multi-stream support")
        
        return recommendations
    
    def suggest_optimal_container(self, codecs: List[str], use_case: str) -> Optional[ContainerFormat]:
        """Suggest optimal container for codecs and use case"""
        compatible_containers = []
        
        # Find containers that support all codecs
        for container in self.registry.formats.values():
            if all(self.registry.supports_codec(container.extension, codec) for codec in codecs):
                compatible_containers.append(container)
        
        if not compatible_containers:
            return None
        
        # Score containers based on use case
        scored_containers = []
        for container in compatible_containers:
            score = 0
            
            if use_case == "streaming" and container.streaming_optimized:
                score += 50
            elif use_case == "archival" and container.quality_preserving:
                score += 50
            elif use_case == "editing" and container.supports_chapters:
                score += 50
            
            # General quality factors
            if container.supports_metadata:
                score += 10
            if container.supports_subtitles:
                score += 10
            
            scored_containers.append((container, score))
        
        # Return highest scored container
        best_container = max(scored_containers, key=lambda x: x[1])
        return best_container[0]


# Export main classes and functions
__all__ = [
    'ContainerType',
    'ContainerFormat', 
    'ContainerFormatRegistry',
    'ContainerAnalyzer',
    'container_registry'
]