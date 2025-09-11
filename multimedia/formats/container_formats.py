"""
Container Formats Module for Ainflue Platform
Enterprise-grade multimedia container format handling

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Optional, Union, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class ContainerType(Enum):
    """Container format types"""
    VIDEO = "video"
    AUDIO = "audio"
    MIXED = "mixed"
    ARCHIVE = "archive"
    STREAMING = "streaming"


class StreamingCapability(Enum):
    """Streaming capabilities"""
    PROGRESSIVE = "progressive"
    ADAPTIVE = "adaptive"
    REALTIME = "realtime"
    OFFLINE = "offline"


@dataclass
class StreamInfo:
    """Stream information within container"""
    stream_id: int
    codec: str
    type: str  # video, audio, subtitle, data
    language: Optional[str] = None
    bitrate: Optional[int] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContainerMetadata:
    """Container metadata information"""
    title: Optional[str] = None
    description: Optional[str] = None
    creation_time: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    file_size: Optional[int] = None
    format_tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ContainerCapabilities:
    """Container format capabilities"""
    max_video_streams: int
    max_audio_streams: int
    max_subtitle_streams: int
    supports_metadata: bool
    supports_chapters: bool
    supports_attachments: bool
    streaming_capabilities: Set[StreamingCapability]
    supported_codecs: Dict[str, List[str]]


@dataclass
class ContainerFormat:
    """Container format definition"""
    format_id: str
    name: str
    description: str
    container_type: ContainerType
    mime_types: List[str]
    file_extensions: List[str]
    magic_bytes: Optional[bytes] = None
    capabilities: Optional[ContainerCapabilities] = None
    vendor: str = ""
    version: str = ""
    specification_url: str = ""
    license_type: str = ""
    platform_support: Dict[str, bool] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class ContainerRegistry:
    """
    Enterprise container format registry and management system
    Handles multimedia container formats for Ainflue platform
    """
    
    def __init__(self):
        self.containers: Dict[str, ContainerFormat] = {}
        self.mime_mappings: Dict[str, str] = {}
        self.extension_mappings: Dict[str, str] = {}
        self._initialize_default_containers()
    
    def _initialize_default_containers(self):
        """Initialize registry with default container formats"""
        
        # MP4 Container
        mp4_capabilities = ContainerCapabilities(
            max_video_streams=32,
            max_audio_streams=32,
            max_subtitle_streams=32,
            supports_metadata=True,
            supports_chapters=True,
            supports_attachments=True,
            streaming_capabilities={
                StreamingCapability.PROGRESSIVE,
                StreamingCapability.ADAPTIVE,
                StreamingCapability.OFFLINE
            },
            supported_codecs={
                "video": ["h264", "h265", "av1", "vp9"],
                "audio": ["aac", "mp3", "opus", "ac3"],
                "subtitle": ["tx3g", "wvtt"]
            }
        )
        
        mp4_container = ContainerFormat(
            format_id="mp4",
            name="MPEG-4 Part 14",
            description="Universal multimedia container format",
            container_type=ContainerType.MIXED,
            mime_types=["video/mp4", "audio/mp4"],
            file_extensions=[".mp4", ".m4v", ".m4a"],
            magic_bytes=b'\x00\x00\x00\x20ftypmp4',
            capabilities=mp4_capabilities,
            vendor="ISO/IEC",
            version="ISO/IEC 14496-14",
            specification_url="https://www.iso.org/standard/61988.html",
            license_type="ISO Standard",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True,
                "web": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(mp4_container)
        
        # WebM Container
        webm_capabilities = ContainerCapabilities(
            max_video_streams=16,
            max_audio_streams=16,
            max_subtitle_streams=16,
            supports_metadata=True,
            supports_chapters=True,
            supports_attachments=False,
            streaming_capabilities={
                StreamingCapability.PROGRESSIVE,
                StreamingCapability.ADAPTIVE,
                StreamingCapability.REALTIME
            },
            supported_codecs={
                "video": ["vp8", "vp9", "av1"],
                "audio": ["vorbis", "opus"],
                "subtitle": ["webvtt"]
            }
        )
        
        webm_container = ContainerFormat(
            format_id="webm",
            name="WebM",
            description="Open web media container",
            container_type=ContainerType.MIXED,
            mime_types=["video/webm", "audio/webm"],
            file_extensions=[".webm"],
            magic_bytes=b'\x1a\x45\xdf\xa3',
            capabilities=webm_capabilities,
            vendor="Google",
            version="WebM 1.0",
            specification_url="https://www.webmproject.org/docs/container/",
            license_type="Open Source (BSD)",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": True,
                "web": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(webm_container)
        
        # MOV Container (QuickTime)
        mov_capabilities = ContainerCapabilities(
            max_video_streams=32,
            max_audio_streams=32,
            max_subtitle_streams=32,
            supports_metadata=True,
            supports_chapters=True,
            supports_attachments=True,
            streaming_capabilities={
                StreamingCapability.PROGRESSIVE,
                StreamingCapability.OFFLINE
            },
            supported_codecs={
                "video": ["h264", "h265", "prores", "dnxhd"],
                "audio": ["aac", "pcm", "alac"],
                "subtitle": ["tx3g", "c608"]
            }
        )
        
        mov_container = ContainerFormat(
            format_id="mov",
            name="QuickTime File Format",
            description="Apple's multimedia container",
            container_type=ContainerType.MIXED,
            mime_types=["video/quicktime"],
            file_extensions=[".mov", ".qt"],
            magic_bytes=b'\x00\x00\x00\x14ftypqt',
            capabilities=mov_capabilities,
            vendor="Apple",
            version="QuickTime 7",
            specification_url="https://developer.apple.com/documentation/quicktime",
            license_type="Proprietary",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": False,
                "web": False
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(mov_container)
        
        # AVI Container
        avi_capabilities = ContainerCapabilities(
            max_video_streams=99,
            max_audio_streams=99,
            max_subtitle_streams=0,
            supports_metadata=True,
            supports_chapters=False,
            supports_attachments=False,
            streaming_capabilities={
                StreamingCapability.PROGRESSIVE,
                StreamingCapability.OFFLINE
            },
            supported_codecs={
                "video": ["h264", "xvid", "divx", "mjpeg"],
                "audio": ["mp3", "pcm", "ac3"],
                "subtitle": []
            }
        )
        
        avi_container = ContainerFormat(
            format_id="avi",
            name="Audio Video Interleave",
            description="Legacy Microsoft container",
            container_type=ContainerType.MIXED,
            mime_types=["video/x-msvideo"],
            file_extensions=[".avi"],
            magic_bytes=b'RIFF',
            capabilities=avi_capabilities,
            vendor="Microsoft",
            version="AVI 1.0",
            specification_url="https://docs.microsoft.com/en-us/windows/win32/directshow/avi-riff-file-reference",
            license_type="Proprietary",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": True,
                "web": False
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(avi_container)
        
        # MKV Container (Matroska)
        mkv_capabilities = ContainerCapabilities(
            max_video_streams=65535,
            max_audio_streams=65535,
            max_subtitle_streams=65535,
            supports_metadata=True,
            supports_chapters=True,
            supports_attachments=True,
            streaming_capabilities={
                StreamingCapability.PROGRESSIVE,
                StreamingCapability.ADAPTIVE,
                StreamingCapability.OFFLINE
            },
            supported_codecs={
                "video": ["h264", "h265", "av1", "vp9", "prores"],
                "audio": ["aac", "mp3", "flac", "opus", "dts"],
                "subtitle": ["srt", "ass", "vobsub", "pgs"]
            }
        )
        
        mkv_container = ContainerFormat(
            format_id="mkv",
            name="Matroska Video",
            description="Open standard container format",
            container_type=ContainerType.MIXED,
            mime_types=["video/x-matroska"],
            file_extensions=[".mkv", ".mka", ".mks"],
            magic_bytes=b'\x1a\x45\xdf\xa3',
            capabilities=mkv_capabilities,
            vendor="Matroska",
            version="Matroska v4",
            specification_url="https://www.matroska.org/technical/specs/index.html",
            license_type="Open Source",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": True,
                "web": False
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(mkv_container)
        
        # FLV Container (Flash Video)
        flv_capabilities = ContainerCapabilities(
            max_video_streams=1,
            max_audio_streams=1,
            max_subtitle_streams=0,
            supports_metadata=True,
            supports_chapters=False,
            supports_attachments=False,
            streaming_capabilities={
                StreamingCapability.PROGRESSIVE,
                StreamingCapability.REALTIME
            },
            supported_codecs={
                "video": ["h264", "vp6", "sorenson"],
                "audio": ["aac", "mp3", "nellymoser"],
                "subtitle": []
            }
        )
        
        flv_container = ContainerFormat(
            format_id="flv",
            name="Flash Video",
            description="Adobe Flash video container",
            container_type=ContainerType.VIDEO,
            mime_types=["video/x-flv"],
            file_extensions=[".flv"],
            magic_bytes=b'FLV\x01',
            capabilities=flv_capabilities,
            vendor="Adobe",
            version="FLV 1.1",
            specification_url="https://www.adobe.com/devnet/f4v.html",
            license_type="Proprietary",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": False,
                "android": False,
                "web": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(flv_container)
        
        # HLS Container (HTTP Live Streaming)
        hls_capabilities = ContainerCapabilities(
            max_video_streams=16,
            max_audio_streams=16,
            max_subtitle_streams=16,
            supports_metadata=True,
            supports_chapters=False,
            supports_attachments=False,
            streaming_capabilities={
                StreamingCapability.ADAPTIVE,
                StreamingCapability.REALTIME
            },
            supported_codecs={
                "video": ["h264", "h265"],
                "audio": ["aac", "mp3"],
                "subtitle": ["webvtt", "tx3g"]
            }
        )
        
        hls_container = ContainerFormat(
            format_id="hls",
            name="HTTP Live Streaming",
            description="Apple adaptive streaming format",
            container_type=ContainerType.STREAMING,
            mime_types=["application/vnd.apple.mpegurl"],
            file_extensions=[".m3u8", ".m3u"],
            magic_bytes=b'#EXTM3U',
            capabilities=hls_capabilities,
            vendor="Apple",
            version="HLS RFC 8216",
            specification_url="https://tools.ietf.org/html/rfc8216",
            license_type="Open Standard",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True,
                "web": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(hls_container)
        
        # DASH Container (Dynamic Adaptive Streaming)
        dash_capabilities = ContainerCapabilities(
            max_video_streams=32,
            max_audio_streams=32,
            max_subtitle_streams=32,
            supports_metadata=True,
            supports_chapters=False,
            supports_attachments=False,
            streaming_capabilities={
                StreamingCapability.ADAPTIVE,
                StreamingCapability.REALTIME
            },
            supported_codecs={
                "video": ["h264", "h265", "av1", "vp9"],
                "audio": ["aac", "opus", "ac3"],
                "subtitle": ["webvtt", "ttml"]
            }
        )
        
        dash_container = ContainerFormat(
            format_id="dash",
            name="Dynamic Adaptive Streaming over HTTP",
            description="MPEG-DASH adaptive streaming",
            container_type=ContainerType.STREAMING,
            mime_types=["application/dash+xml"],
            file_extensions=[".mpd"],
            magic_bytes=b'<?xml',
            capabilities=dash_capabilities,
            vendor="MPEG",
            version="MPEG-DASH ISO/IEC 23009-1",
            specification_url="https://www.iso.org/standard/65274.html",
            license_type="ISO Standard",
            platform_support={
                "windows": True,
                "macos": True,
                "linux": True,
                "ios": True,
                "android": True,
                "web": True
            },
            created_at="2025-09-11T19:18:00Z",
            updated_at="2025-09-11T19:18:00Z"
        )
        self.register_container(dash_container)
    
    def register_container(self, container: ContainerFormat):
        """Register a container format"""
        self.containers[container.format_id] = container
        
        # Update MIME type mappings
        for mime_type in container.mime_types:
            self.mime_mappings[mime_type] = container.format_id
        
        # Update extension mappings
        for extension in container.file_extensions:
            self.extension_mappings[extension.lower()] = container.format_id
        
        logger.info(f"Registered container format: {container.name} ({container.format_id})")
    
    def get_container(self, format_id: str) -> Optional[ContainerFormat]:
        """Get container format by ID"""
        return self.containers.get(format_id)
    
    def get_container_by_mime_type(self, mime_type: str) -> Optional[ContainerFormat]:
        """Get container format by MIME type"""
        format_id = self.mime_mappings.get(mime_type)
        return self.containers.get(format_id) if format_id else None
    
    def get_container_by_extension(self, extension: str) -> Optional[ContainerFormat]:
        """Get container format by file extension"""
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        format_id = self.extension_mappings.get(extension.lower())
        return self.containers.get(format_id) if format_id else None
    
    def get_containers_by_type(self, container_type: ContainerType) -> List[ContainerFormat]:
        """Get all containers of specific type"""
        return [
            container for container in self.containers.values()
            if container.container_type == container_type
        ]
    
    def detect_container_format(self, file_path: Path) -> Optional[ContainerFormat]:
        """Detect container format from file"""
        # Try by extension first
        extension = file_path.suffix.lower()
        container = self.get_container_by_extension(extension)
        if container:
            return container
        
        # Try by MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            container = self.get_container_by_mime_type(mime_type)
            if container:
                return container
        
        # Try by magic bytes
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)
                for container in self.containers.values():
                    if container.magic_bytes and header.startswith(container.magic_bytes):
                        return container
        except Exception as e:
            logger.warning(f"Could not read file header: {e}")
        
        return None
    
    def is_codec_supported(self, container_id: str, codec: str, stream_type: str) -> bool:
        """Check if codec is supported in container"""
        container = self.get_container(container_id)
        if not container or not container.capabilities:
            return False
        
        supported_codecs = container.capabilities.supported_codecs.get(stream_type, [])
        return codec in supported_codecs
    
    def get_supported_codecs(self, container_id: str) -> Dict[str, List[str]]:
        """Get all supported codecs for container"""
        container = self.get_container(container_id)
        if not container or not container.capabilities:
            return {}
        
        return container.capabilities.supported_codecs.copy()
    
    def get_streaming_containers(self) -> List[ContainerFormat]:
        """Get containers that support streaming"""
        streaming_containers = []
        for container in self.containers.values():
            if (container.capabilities and 
                container.capabilities.streaming_capabilities and
                any(cap in {StreamingCapability.ADAPTIVE, StreamingCapability.REALTIME}
                    for cap in container.capabilities.streaming_capabilities)):
                streaming_containers.append(container)
        
        return streaming_containers
    
    def get_web_compatible_containers(self) -> List[ContainerFormat]:
        """Get containers compatible with web browsers"""
        web_containers = []
        for container in self.containers.values():
            if container.platform_support.get("web", False):
                web_containers.append(container)
        
        return web_containers
    
    def get_mobile_compatible_containers(self) -> List[ContainerFormat]:
        """Get containers compatible with mobile devices"""
        mobile_containers = []
        for container in self.containers.values():
            ios_support = container.platform_support.get("ios", False)
            android_support = container.platform_support.get("android", False)
            if ios_support or android_support:
                mobile_containers.append(container)
        
        return mobile_containers
    
    def find_best_container(
        self, 
        codecs: Dict[str, str],
        target_platform: str = "web",
        streaming: bool = False
    ) -> Optional[ContainerFormat]:
        """Find best container for given codecs and requirements"""
        candidates = []
        
        for container in self.containers.values():
            # Check platform support
            if not container.platform_support.get(target_platform, False):
                continue
            
            # Check streaming requirement
            if streaming and container.capabilities:
                has_streaming = any(
                    cap in {StreamingCapability.ADAPTIVE, StreamingCapability.REALTIME}
                    for cap in container.capabilities.streaming_capabilities
                )
                if not has_streaming:
                    continue
            
            # Check codec support
            if container.capabilities:
                all_supported = True
                for stream_type, codec in codecs.items():
                    if not self.is_codec_supported(container.format_id, codec, stream_type):
                        all_supported = False
                        break
                
                if all_supported:
                    candidates.append(container)
        
        if not candidates:
            return None
        
        # Prefer more modern containers
        modern_priority = {
            "mp4": 10,
            "webm": 9,
            "mkv": 8,
            "hls": 7,
            "dash": 7,
            "mov": 6,
            "avi": 3,
            "flv": 2
        }
        
        return max(candidates, key=lambda c: modern_priority.get(c.format_id, 1))
    
    def get_container_comparison(self, container_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare multiple containers"""
        comparison = {}
        
        for container_id in container_ids:
            container = self.get_container(container_id)
            if not container:
                continue
            
            comparison[container_id] = {
                "name": container.name,
                "type": container.container_type.value,
                "mime_types": container.mime_types,
                "extensions": container.file_extensions,
                "vendor": container.vendor,
                "license": container.license_type,
                "platform_support": container.platform_support,
                "streaming_support": bool(
                    container.capabilities and
                    container.capabilities.streaming_capabilities
                ),
                "metadata_support": bool(
                    container.capabilities and
                    container.capabilities.supports_metadata
                ),
                "supported_codecs": (
                    container.capabilities.supported_codecs
                    if container.capabilities else {}
                )
            }
        
        return comparison
    
    def export_registry(self, file_path: Path) -> bool:
        """Export container registry to JSON"""
        try:
            registry_data = {
                "containers": {},
                "mime_mappings": self.mime_mappings,
                "extension_mappings": self.extension_mappings,
                "export_timestamp": "2025-09-11T19:18:00Z"
            }
            
            for container_id, container in self.containers.items():
                container_data = {
                    "format_id": container.format_id,
                    "name": container.name,
                    "description": container.description,
                    "container_type": container.container_type.value,
                    "mime_types": container.mime_types,
                    "file_extensions": container.file_extensions,
                    "vendor": container.vendor,
                    "version": container.version,
                    "specification_url": container.specification_url,
                    "license_type": container.license_type,
                    "platform_support": container.platform_support,
                    "created_at": container.created_at,
                    "updated_at": container.updated_at
                }
                
                if container.capabilities:
                    container_data["capabilities"] = {
                        "max_video_streams": container.capabilities.max_video_streams,
                        "max_audio_streams": container.capabilities.max_audio_streams,
                        "max_subtitle_streams": container.capabilities.max_subtitle_streams,
                        "supports_metadata": container.capabilities.supports_metadata,
                        "supports_chapters": container.capabilities.supports_chapters,
                        "supports_attachments": container.capabilities.supports_attachments,
                        "streaming_capabilities": [
                            cap.value for cap in container.capabilities.streaming_capabilities
                        ],
                        "supported_codecs": container.capabilities.supported_codecs
                    }
                
                registry_data["containers"][container_id] = container_data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Container registry exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export container registry: {e}")
            return False
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        stats = {
            "total_containers": len(self.containers),
            "by_type": {},
            "by_license": {},
            "platform_coverage": {},
            "streaming_support": 0,
            "web_compatible": 0,
            "mobile_compatible": 0
        }
        
        platforms = ["windows", "macos", "linux", "ios", "android", "web"]
        for platform in platforms:
            stats["platform_coverage"][platform] = 0
        
        for container in self.containers.values():
            # Count by type
            container_type = container.container_type.value
            stats["by_type"][container_type] = stats["by_type"].get(container_type, 0) + 1
            
            # Count by license
            license_type = container.license_type
            stats["by_license"][license_type] = stats["by_license"].get(license_type, 0) + 1
            
            # Platform coverage
            for platform in platforms:
                if container.platform_support.get(platform, False):
                    stats["platform_coverage"][platform] += 1
            
            # Special capabilities
            if container.capabilities:
                if container.capabilities.streaming_capabilities:
                    stats["streaming_support"] += 1
            
            if container.platform_support.get("web", False):
                stats["web_compatible"] += 1
            
            if (container.platform_support.get("ios", False) or 
                container.platform_support.get("android", False)):
                stats["mobile_compatible"] += 1
        
        return stats


# Global container registry instance
container_registry = ContainerRegistry()


async def get_container_registry() -> ContainerRegistry:
    """Get the global container registry instance"""
    return container_registry


if __name__ == "__main__":
    # Test container registry
    registry = ContainerRegistry()
    
    print("Container Registry Statistics:")
    stats = registry.get_registry_stats()
    print(json.dumps(stats, indent=2))
    
    print("\nWeb Compatible Containers:")
    web_containers = registry.get_web_compatible_containers()
    for container in web_containers:
        print(f"- {container.name} ({container.format_id})")
    
    print("\nBest container for H.264 video + AAC audio (web):")
    best_container = registry.find_best_container(
        codecs={"video": "h264", "audio": "aac"},
        target_platform="web"
    )
    if best_container:
        print(f"Best: {best_container.name} ({best_container.format_id})")