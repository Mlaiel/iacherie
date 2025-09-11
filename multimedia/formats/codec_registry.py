"""
Codec Registry Module for Ainflue Platform
Enterprise-grade codec management and registry system

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CodecType(Enum):
    """Codec type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    SUBTITLE = "subtitle"
    CONTAINER = "container"


class CompressionType(Enum):
    """Compression type enumeration"""
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    HYBRID = "hybrid"


@dataclass
class CodecCapability:
    """Codec capability definition"""
    name: str
    supported_operations: Set[str]
    quality_range: Tuple[int, int]
    max_resolution: Optional[str] = None
    max_bitrate: Optional[int] = None
    hardware_acceleration: bool = False


@dataclass
class CodecInfo:
    """Comprehensive codec information"""
    codec_id: str
    name: str
    codec_type: CodecType
    compression_type: CompressionType
    mime_types: List[str]
    file_extensions: List[str]
    description: str
    version: str
    vendor: str
    capabilities: CodecCapability
    license_type: str
    platform_support: Dict[str, bool]
    performance_metrics: Dict[str, float]
    created_at: str
    updated_at: str


class CodecRegistry:
    """
    Enterprise codec registry system for multimedia processing
    Manages all supported codecs with performance tracking
    """
    
    def __init__(self):
        self.codecs: Dict[str, CodecInfo] = {}
        self.codec_aliases: Dict[str, str] = {}
        self.type_mappings: Dict[CodecType, List[str]] = {
            CodecType.AUDIO: [],
            CodecType.VIDEO: [],
            CodecType.IMAGE: [],
            CodecType.SUBTITLE: [],
            CodecType.CONTAINER: []
        }
        self._initialize_default_codecs()
    
    def _initialize_default_codecs(self):
        """Initialize registry with default supported codecs"""
        
        # Audio Codecs
        self._register_audio_codecs()
        
        # Video Codecs  
        self._register_video_codecs()
        
        # Image Codecs
        self._register_image_codecs()
        
        # Container Codecs
        self._register_container_codecs()
        
        # Subtitle Codecs
        self._register_subtitle_codecs()
    
    def _register_audio_codecs(self):
        """Register audio codecs"""
        
        # AAC Codec
        aac_codec = CodecInfo(
            codec_id="aac",
            name="Advanced Audio Coding",
            codec_type=CodecType.AUDIO,
            compression_type=CompressionType.LOSSY,
            mime_types=["audio/aac", "audio/mp4"],
            file_extensions=[".aac", ".m4a"],
            description="High-quality lossy audio codec",
            version="LC/HE-AAC v2",
            vendor="ISO/IEC",
            capabilities=CodecCapability(
                name="AAC Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(64, 512),
                hardware_acceleration=True
            ),
            license_type="Patent-encumbered",
            platform_support={
                "windows": True,
                "macos": True, 
                "linux": True,
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 50.0,
                "decode_speed": 100.0,
                "quality_score": 0.92
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(aac_codec)
        
        # MP3 Codec
        mp3_codec = CodecInfo(
            codec_id="mp3",
            name="MPEG-1 Audio Layer III",
            codec_type=CodecType.AUDIO,
            compression_type=CompressionType.LOSSY,
            mime_types=["audio/mpeg", "audio/mp3"],
            file_extensions=[".mp3"],
            description="Legacy widespread audio codec",
            version="MPEG-1 Layer 3",
            vendor="ISO/IEC",
            capabilities=CodecCapability(
                name="MP3 Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(32, 320),
                hardware_acceleration=False
            ),
            license_type="Patent-expired",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True, 
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 75.0,
                "decode_speed": 150.0,
                "quality_score": 0.78
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(mp3_codec)
        
        # FLAC Codec
        flac_codec = CodecInfo(
            codec_id="flac",
            name="Free Lossless Audio Codec",
            codec_type=CodecType.AUDIO,
            compression_type=CompressionType.LOSSLESS,
            mime_types=["audio/flac"],
            file_extensions=[".flac"],
            description="Open-source lossless audio codec",
            version="1.4.3",
            vendor="Xiph.Org Foundation",
            capabilities=CodecCapability(
                name="FLAC Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(0, 8),
                hardware_acceleration=False
            ),
            license_type="Open Source (BSD)",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 25.0,
                "decode_speed": 80.0,
                "quality_score": 1.0
            },
            created_at="2025-09-11T19:18:00Z", 
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(flac_codec)
    
    def _register_video_codecs(self):
        """Register video codecs"""
        
        # H.264/AVC Codec
        h264_codec = CodecInfo(
            codec_id="h264",
            name="H.264/MPEG-4 AVC",
            codec_type=CodecType.VIDEO,
            compression_type=CompressionType.LOSSY,
            mime_types=["video/mp4", "video/h264"],
            file_extensions=[".mp4", ".m4v"],
            description="Widely supported video codec",
            version="ITU-T H.264",
            vendor="ITU-T/ISO",
            capabilities=CodecCapability(
                name="H.264 Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(1, 51),
                max_resolution="8K",
                max_bitrate=100000000,
                hardware_acceleration=True
            ),
            license_type="Patent-encumbered",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 30.0,
                "decode_speed": 120.0,
                "quality_score": 0.85
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(h264_codec)
        
        # H.265/HEVC Codec
        h265_codec = CodecInfo(
            codec_id="h265",
            name="H.265/HEVC",
            codec_type=CodecType.VIDEO,
            compression_type=CompressionType.LOSSY,
            mime_types=["video/mp4", "video/hevc"],
            file_extensions=[".mp4", ".hevc"],
            description="Next-generation video codec",
            version="ITU-T H.265",
            vendor="ITU-T/ISO",
            capabilities=CodecCapability(
                name="H.265 Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(1, 51),
                max_resolution="8K",
                max_bitrate=200000000,
                hardware_acceleration=True
            ),
            license_type="Patent-encumbered",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 15.0,
                "decode_speed": 60.0,
                "quality_score": 0.92
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(h265_codec)
        
        # AV1 Codec
        av1_codec = CodecInfo(
            codec_id="av1",
            name="AOMedia Video 1",
            codec_type=CodecType.VIDEO,
            compression_type=CompressionType.LOSSY,
            mime_types=["video/mp4", "video/webm"],
            file_extensions=[".mp4", ".webm"],
            description="Royalty-free next-gen video codec",
            version="AV1 v1.0",
            vendor="Alliance for Open Media",
            capabilities=CodecCapability(
                name="AV1 Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(1, 63),
                max_resolution="8K",
                max_bitrate=300000000,
                hardware_acceleration=True
            ),
            license_type="Open Source (BSD)",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": True
            },
            performance_metrics={
                "encode_speed": 5.0,
                "decode_speed": 40.0,
                "quality_score": 0.95
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(av1_codec)
    
    def _register_image_codecs(self):
        """Register image codecs"""
        
        # WebP Codec
        webp_codec = CodecInfo(
            codec_id="webp",
            name="WebP",
            codec_type=CodecType.IMAGE,
            compression_type=CompressionType.HYBRID,
            mime_types=["image/webp"],
            file_extensions=[".webp"],
            description="Modern web image format",
            version="WebP 1.3",
            vendor="Google",
            capabilities=CodecCapability(
                name="WebP Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(0, 100),
                hardware_acceleration=False
            ),
            license_type="Open Source (BSD)",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 45.0,
                "decode_speed": 90.0,
                "quality_score": 0.88
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(webp_codec)
        
        # AVIF Codec
        avif_codec = CodecInfo(
            codec_id="avif",
            name="AV1 Image File Format",
            codec_type=CodecType.IMAGE,
            compression_type=CompressionType.LOSSY,
            mime_types=["image/avif"],
            file_extensions=[".avif"],
            description="Next-generation image format",
            version="AVIF 1.0",
            vendor="Alliance for Open Media",
            capabilities=CodecCapability(
                name="AVIF Encoding/Decoding",
                supported_operations={"encode", "decode", "transcode"},
                quality_range=(0, 63),
                hardware_acceleration=False
            ),
            license_type="Open Source (BSD)",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": True
            },
            performance_metrics={
                "encode_speed": 20.0,
                "decode_speed": 50.0,
                "quality_score": 0.92
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(avif_codec)
    
    def _register_container_codecs(self):
        """Register container format codecs"""
        
        # MP4 Container
        mp4_container = CodecInfo(
            codec_id="mp4",
            name="MPEG-4 Part 14",
            codec_type=CodecType.CONTAINER,
            compression_type=CompressionType.HYBRID,
            mime_types=["video/mp4", "audio/mp4"],
            file_extensions=[".mp4", ".m4v", ".m4a"],
            description="Universal multimedia container",
            version="ISO/IEC 14496-14",
            vendor="ISO/IEC",
            capabilities=CodecCapability(
                name="MP4 Container",
                supported_operations={"mux", "demux", "transcode"},
                quality_range=(0, 100),
                hardware_acceleration=True
            ),
            license_type="ISO Standard",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 80.0,
                "decode_speed": 150.0,
                "quality_score": 0.90
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(mp4_container)
    
    def _register_subtitle_codecs(self):
        """Register subtitle codecs"""
        
        # SRT Subtitle
        srt_codec = CodecInfo(
            codec_id="srt",
            name="SubRip Text",
            codec_type=CodecType.SUBTITLE,
            compression_type=CompressionType.LOSSLESS,
            mime_types=["text/srt", "application/x-subrip"],
            file_extensions=[".srt"],
            description="Simple subtitle text format",
            version="SRT 1.0",
            vendor="SubRip",
            capabilities=CodecCapability(
                name="SRT Subtitle",
                supported_operations={"encode", "decode", "parse"},
                quality_range=(0, 100),
                hardware_acceleration=False
            ),
            license_type="Open Standard",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True
            },
            performance_metrics={
                "encode_speed": 1000.0,
                "decode_speed": 2000.0,
                "quality_score": 1.0
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_codec(srt_codec)
    
    def register_codec(self, codec_info: CodecInfo):
        """Register a new codec in the registry"""
        self.codecs[codec_info.codec_id] = codec_info
        self.type_mappings[codec_info.codec_type].append(codec_info.codec_id)
        
        # Add aliases for common variations
        if codec_info.codec_id == "h264":
            self.codec_aliases["avc"] = "h264"
            self.codec_aliases["x264"] = "h264"
        elif codec_info.codec_id == "h265":
            self.codec_aliases["hevc"] = "h265"
            self.codec_aliases["x265"] = "h265"
        
        logger.info(f"Registered codec: {codec_info.name} ({codec_info.codec_id})")
    
    def get_codec(self, codec_id: str) -> Optional[CodecInfo]:
        """Get codec information by ID or alias"""
        # Check direct ID first
        if codec_id in self.codecs:
            return self.codecs[codec_id]
        
        # Check aliases
        if codec_id in self.codec_aliases:
            return self.codecs[self.codec_aliases[codec_id]]
        
        return None
    
    def get_codecs_by_type(self, codec_type: CodecType) -> List[CodecInfo]:
        """Get all codecs of a specific type"""
        codec_ids = self.type_mappings.get(codec_type, [])
        return [self.codecs[codec_id] for codec_id in codec_ids]
    
    def get_codecs_by_mime_type(self, mime_type: str) -> List[CodecInfo]:
        """Get codecs supporting specific MIME type"""
        matching_codecs = []
        for codec in self.codecs.values():
            if mime_type in codec.mime_types:
                matching_codecs.append(codec)
        return matching_codecs
    
    def get_codecs_by_extension(self, extension: str) -> List[CodecInfo]:
        """Get codecs supporting specific file extension"""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        matching_codecs = []
        for codec in self.codecs.values():
            if extension.lower() in [ext.lower() for ext in codec.file_extensions]:
                matching_codecs.append(codec)
        return matching_codecs
    
    def is_codec_supported(self, codec_id: str, operation: str = None) -> bool:
        """Check if codec is supported with optional operation"""
        codec = self.get_codec(codec_id)
        if not codec:
            return False
        
        if operation:
            return operation in codec.capabilities.supported_operations
        
        return True
    
    def get_best_codec_for_purpose(
        self, 
        codec_type: CodecType, 
        criteria: str = "quality"
    ) -> Optional[CodecInfo]:
        """Get best codec for specific purpose"""
        codecs = self.get_codecs_by_type(codec_type)
        
        if not codecs:
            return None
        
        if criteria == "quality":
            return max(codecs, key=lambda c: c.performance_metrics.get("quality_score", 0))
        elif criteria == "speed":
            return max(codecs, key=lambda c: c.performance_metrics.get("encode_speed", 0))
        elif criteria == "compatibility":
            return max(codecs, key=lambda c: sum(c.platform_support.values()))
        
        return codecs[0]
    
    def get_codec_compatibility_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Get compatibility matrix for all codecs"""
        matrix = {}
        platforms = ["windows", "macos", "linux", "ios", "android"]
        
        for codec_id, codec in self.codecs.items():
            matrix[codec_id] = {}
            for platform in platforms:
                matrix[codec_id][platform] = codec.platform_support.get(platform, False)
        
        return matrix
    
    def export_registry(self, file_path: Path) -> bool:
        """Export codec registry to JSON file"""
        try:
            registry_data = {
                "codecs": {
                    codec_id: {
                        "codec_id": codec.codec_id,
                        "name": codec.name,
                        "codec_type": codec.codec_type.value,
                        "compression_type": codec.compression_type.value,
                        "mime_types": codec.mime_types,
                        "file_extensions": codec.file_extensions,
                        "description": codec.description,
                        "version": codec.version,
                        "vendor": codec.vendor,
                        "license_type": codec.license_type,
                        "platform_support": codec.platform_support,
                        "performance_metrics": codec.performance_metrics,
                        "created_at": codec.created_at,
                        "updated_at": codec.updated_at
                    }
                    for codec_id, codec in self.codecs.items()
                },
                "aliases": self.codec_aliases,
                "export_timestamp": "2025-09-11T19:18:00Z"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Codec registry exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export codec registry: {e}")
            return False
    
    def get_registry_stats(self) -> Dict[str, Union[int, Dict[str, int]]]:
        """Get registry statistics"""
        stats = {
            "total_codecs": len(self.codecs),
            "total_aliases": len(self.codec_aliases),
            "by_type": {},
            "by_license": {},
            "by_compression": {}
        }
        
        # Count by type
        for codec_type in CodecType:
            stats["by_type"][codec_type.value] = len(self.type_mappings[codec_type])
        
        # Count by license and compression type
        for codec in self.codecs.values():
            license_type = codec.license_type
            compression_type = codec.compression_type.value
            
            stats["by_license"][license_type] = stats["by_license"].get(license_type, 0) + 1
            stats["by_compression"][compression_type] = stats["by_compression"].get(compression_type, 0) + 1
        
        return stats


# Global codec registry instance
codec_registry = CodecRegistry()


async def get_codec_registry() -> CodecRegistry:
    """Get the global codec registry instance"""
    return codec_registry


def register_custom_codec(codec_info: CodecInfo) -> bool:
    """Register a custom codec"""
    try:
        codec_registry.register_codec(codec_info)
        return True
    except Exception as e:
        logger.error(f"Failed to register custom codec: {e}")
        return False


if __name__ == "__main__":
    # Test codec registry
    registry = CodecRegistry()
    
    print("Codec Registry Statistics:")
    stats = registry.get_registry_stats()
    print(json.dumps(stats, indent=2))
    
    print("\nH.264 Codec Info:")
    h264 = registry.get_codec("h264")
    if h264:
        print(f"Name: {h264.name}")
        print(f"Type: {h264.codec_type.value}")
        print(f"Quality Score: {h264.performance_metrics['quality_score']}")
    
    print("\nBest Video Codec for Quality:")
    best_video = registry.get_best_codec_for_purpose(CodecType.VIDEO, "quality")
    if best_video:
        print(f"Best: {best_video.name} (Score: {best_video.performance_metrics['quality_score']})")