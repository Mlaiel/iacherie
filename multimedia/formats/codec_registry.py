"""
Codec Registry Management System
Enterprise-grade codec discovery, validation and management for Ainflue Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import subprocess
import sys
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class CodecType(Enum):
    """Codec types"""
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    DATA = "data"


class CodecLicense(Enum):
    """Codec licensing types"""
    OPEN_SOURCE = "open_source"
    PROPRIETARY = "proprietary"
    ROYALTY_FREE = "royalty_free"
    LICENSED = "licensed"


@dataclass
class CodecInfo:
    """Comprehensive codec information"""
    name: str
    codec_id: str
    codec_type: CodecType
    description: str
    license_type: CodecLicense
    extensions: List[str]
    mime_types: List[str]
    quality_range: Tuple[int, int]  # 1-10 scale
    compression_efficiency: int  # 1-10 scale
    encoding_speed: int  # 1-10 scale (1=slow, 10=fast)
    hardware_support: bool
    streaming_optimized: bool
    lossless_capable: bool
    supported_resolutions: List[str] = field(default_factory=list)
    supported_framerates: List[int] = field(default_factory=list)
    supported_bitrates: Tuple[int, int] = field(default=(0, 0))  # min, max kbps
    platform_support: List[str] = field(default_factory=list)
    encoder_libraries: List[str] = field(default_factory=list)
    decoder_libraries: List[str] = field(default_factory=list)


class CodecRegistry:
    """Enterprise codec registry and management system"""
    
    def __init__(self):
        self.codecs: Dict[str, CodecInfo] = {}
        self.codec_aliases: Dict[str, str] = {}
        self.system_codecs: Dict[str, bool] = {}
        self._initialize_codecs()
        self._detect_system_codecs()
    
    def _initialize_codecs(self):
        """Initialize comprehensive codec database"""
        
        # Video Codecs
        self.register_codec(CodecInfo(
            name="H.264/AVC",
            codec_id="h264",
            codec_type=CodecType.VIDEO,
            description="Advanced Video Coding - Industry standard",
            license_type=CodecLicense.LICENSED,
            extensions=["mp4", "mkv", "avi", "mov"],
            mime_types=["video/mp4", "video/h264"],
            quality_range=(6, 9),
            compression_efficiency=8,
            encoding_speed=7,
            hardware_support=True,
            streaming_optimized=True,
            lossless_capable=True,
            supported_resolutions=["480p", "720p", "1080p", "4K", "8K"],
            supported_framerates=[23, 24, 25, 30, 50, 60, 120],
            supported_bitrates=(100, 100000),
            platform_support=["web", "mobile", "desktop", "tv"],
            encoder_libraries=["x264", "openh264", "nvenc", "quicksync"],
            decoder_libraries=["ffmpeg", "gstreamer", "directshow"]
        ))
        
        self.register_codec(CodecInfo(
            name="H.265/HEVC",
            codec_id="h265",
            codec_type=CodecType.VIDEO,
            description="High Efficiency Video Coding - Next-gen standard",
            license_type=CodecLicense.LICENSED,
            extensions=["mp4", "mkv", "mov"],
            mime_types=["video/mp4", "video/hevc"],
            quality_range=(7, 10),
            compression_efficiency=9,
            encoding_speed=5,
            hardware_support=True,
            streaming_optimized=True,
            lossless_capable=True,
            supported_resolutions=["720p", "1080p", "4K", "8K"],
            supported_framerates=[24, 25, 30, 50, 60, 120],
            supported_bitrates=(50, 80000),
            platform_support=["web", "mobile", "desktop", "tv"],
            encoder_libraries=["x265", "nvenc", "quicksync"],
            decoder_libraries=["ffmpeg", "gstreamer"]
        ))
        
        self.register_codec(CodecInfo(
            name="AV1",
            codec_id="av1",
            codec_type=CodecType.VIDEO,
            description="AOMedia Video 1 - Royalty-free future standard",
            license_type=CodecLicense.ROYALTY_FREE,
            extensions=["mp4", "webm", "mkv"],
            mime_types=["video/mp4", "video/webm"],
            quality_range=(8, 10),
            compression_efficiency=10,
            encoding_speed=3,
            hardware_support=True,
            streaming_optimized=True,
            lossless_capable=True,
            supported_resolutions=["1080p", "4K", "8K"],
            supported_framerates=[24, 25, 30, 50, 60, 120],
            supported_bitrates=(30, 50000),
            platform_support=["web", "mobile", "desktop"],
            encoder_libraries=["libaom", "svt-av1", "rav1e"],
            decoder_libraries=["dav1d", "libaom", "ffmpeg"]
        ))
        
        self.register_codec(CodecInfo(
            name="VP9",
            codec_id="vp9",
            codec_type=CodecType.VIDEO,
            description="VP9 - Google's open video codec",
            license_type=CodecLicense.ROYALTY_FREE,
            extensions=["webm", "mkv"],
            mime_types=["video/webm"],
            quality_range=(7, 9),
            compression_efficiency=8,
            encoding_speed=4,
            hardware_support=True,
            streaming_optimized=True,
            lossless_capable=True,
            supported_resolutions=["720p", "1080p", "4K", "8K"],
            supported_framerates=[24, 25, 30, 50, 60],
            supported_bitrates=(50, 40000),
            platform_support=["web", "mobile", "desktop"],
            encoder_libraries=["libvpx"],
            decoder_libraries=["libvpx", "ffmpeg"]
        ))
        
        # Audio Codecs
        self.register_codec(CodecInfo(
            name="AAC",
            codec_id="aac",
            codec_type=CodecType.AUDIO,
            description="Advanced Audio Coding - Universal audio standard",
            license_type=CodecLicense.LICENSED,
            extensions=["mp4", "aac", "m4a"],
            mime_types=["audio/aac", "audio/mp4"],
            quality_range=(6, 9),
            compression_efficiency=8,
            encoding_speed=8,
            hardware_support=True,
            streaming_optimized=True,
            lossless_capable=False,
            supported_bitrates=(32, 320),
            platform_support=["web", "mobile", "desktop", "tv"],
            encoder_libraries=["fdk-aac", "aac"],
            decoder_libraries=["ffmpeg", "gstreamer"]
        ))
        
        self.register_codec(CodecInfo(
            name="Opus",
            codec_id="opus",
            codec_type=CodecType.AUDIO,
            description="Opus - High-quality open audio codec",
            license_type=CodecLicense.ROYALTY_FREE,
            extensions=["opus", "webm", "ogg"],
            mime_types=["audio/opus", "audio/webm"],
            quality_range=(8, 10),
            compression_efficiency=9,
            encoding_speed=9,
            hardware_support=False,
            streaming_optimized=True,
            lossless_capable=False,
            supported_bitrates=(6, 510),
            platform_support=["web", "mobile", "desktop"],
            encoder_libraries=["libopus"],
            decoder_libraries=["libopus", "ffmpeg"]
        ))
        
        self.register_codec(CodecInfo(
            name="FLAC",
            codec_id="flac",
            codec_type=CodecType.AUDIO,
            description="Free Lossless Audio Codec",
            license_type=CodecLicense.OPEN_SOURCE,
            extensions=["flac"],
            mime_types=["audio/flac"],
            quality_range=(10, 10),
            compression_efficiency=6,
            encoding_speed=7,
            hardware_support=False,
            streaming_optimized=False,
            lossless_capable=True,
            supported_bitrates=(400, 1411),
            platform_support=["web", "desktop"],
            encoder_libraries=["libflac"],
            decoder_libraries=["libflac", "ffmpeg"]
        ))
        
        # Setup aliases
        self.codec_aliases.update({
            "avc": "h264",
            "x264": "h264",
            "hevc": "h265",
            "x265": "h265",
            "vp8": "vp8",
            "libvpx": "vp9",
            "mp3": "mp3",
            "vorbis": "vorbis"
        })
    
    def register_codec(self, codec_info: CodecInfo):
        """Register a new codec"""
        self.codecs[codec_info.codec_id.lower()] = codec_info
        logger.info(f"Registered codec: {codec_info.name} ({codec_info.codec_id})")
    
    def get_codec(self, codec_id: str) -> Optional[CodecInfo]:
        """Get codec by ID, including aliases"""
        codec_id = codec_id.lower()
        
        # Try direct lookup
        if codec_id in self.codecs:
            return self.codecs[codec_id]
        
        # Try alias lookup
        if codec_id in self.codec_aliases:
            return self.codecs[self.codec_aliases[codec_id]]
        
        return None
    
    def get_codecs_by_type(self, codec_type: CodecType) -> List[CodecInfo]:
        """Get all codecs of specific type"""
        return [codec for codec in self.codecs.values() if codec.codec_type == codec_type]
    
    def get_open_source_codecs(self) -> List[CodecInfo]:
        """Get open source and royalty-free codecs"""
        return [codec for codec in self.codecs.values() 
                if codec.license_type in [CodecLicense.OPEN_SOURCE, CodecLicense.ROYALTY_FREE]]
    
    def get_hardware_accelerated_codecs(self) -> List[CodecInfo]:
        """Get codecs with hardware acceleration support"""
        return [codec for codec in self.codecs.values() if codec.hardware_support]
    
    def get_streaming_optimized_codecs(self) -> List[CodecInfo]:
        """Get streaming-optimized codecs"""
        return [codec for codec in self.codecs.values() if codec.streaming_optimized]
    
    def get_lossless_codecs(self) -> List[CodecInfo]:
        """Get lossless-capable codecs"""
        return [codec for codec in self.codecs.values() if codec.lossless_capable]
    
    def find_best_codec(self, 
                       codec_type: CodecType,
                       priority: str = "quality",
                       platform: str = None,
                       license_pref: CodecLicense = None) -> Optional[CodecInfo]:
        """Find best codec based on criteria"""
        
        candidates = self.get_codecs_by_type(codec_type)
        
        # Filter by platform if specified
        if platform:
            candidates = [c for c in candidates if platform in c.platform_support]
        
        # Filter by license preference
        if license_pref:
            candidates = [c for c in candidates if c.license_type == license_pref]
        
        if not candidates:
            return None
        
        # Score based on priority
        def score_codec(codec: CodecInfo) -> float:
            score = 0.0
            
            if priority == "quality":
                score += codec.quality_range[1] * 0.4
                score += codec.compression_efficiency * 0.3
                score += (10 if codec.lossless_capable else 0) * 0.3
            elif priority == "speed":
                score += codec.encoding_speed * 0.5
                score += (10 if codec.hardware_support else 0) * 0.3
                score += codec.compression_efficiency * 0.2
            elif priority == "compatibility":
                score += len(codec.platform_support) * 2
                score += len(codec.extensions) * 1
                score += (10 if codec.hardware_support else 0) * 0.2
            elif priority == "streaming":
                score += (10 if codec.streaming_optimized else 0) * 0.4
                score += codec.encoding_speed * 0.3
                score += codec.compression_efficiency * 0.3
            
            return score
        
        best_codec = max(candidates, key=score_codec)
        return best_codec
    
    def _detect_system_codecs(self):
        """Detect available codecs on the system"""
        try:
            # Try to detect FFmpeg codecs
            result = subprocess.run(
                ["ffmpeg", "-codecs"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                self._parse_ffmpeg_codecs(result.stdout)
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Could not detect system codecs - FFmpeg not available")
        
        # Mark known system codecs
        for codec_id in self.codecs.keys():
            self.system_codecs[codec_id] = codec_id in self.system_codecs or self._test_codec_availability(codec_id)
    
    def _parse_ffmpeg_codecs(self, output: str):
        """Parse FFmpeg codec output"""
        lines = output.split('\n')
        for line in lines:
            if line.startswith(' '):
                parts = line.strip().split()
                if len(parts) >= 2:
                    codec_id = parts[1].lower()
                    if codec_id in self.codecs:
                        self.system_codecs[codec_id] = True
    
    def _test_codec_availability(self, codec_id: str) -> bool:
        """Test if codec is available for encoding/decoding"""
        try:
            # Simple test - try to get codec info
            result = subprocess.run(
                ["ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=1:size=32x32:rate=1", 
                 "-c:v", codec_id, "-f", "null", "-"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def is_codec_available(self, codec_id: str) -> bool:
        """Check if codec is available on system"""
        codec_id = codec_id.lower()
        if codec_id in self.codec_aliases:
            codec_id = self.codec_aliases[codec_id]
        return self.system_codecs.get(codec_id, False)
    
    def get_available_codecs(self) -> List[CodecInfo]:
        """Get codecs available on current system"""
        return [codec for codec_id, codec in self.codecs.items() 
                if self.system_codecs.get(codec_id, False)]
    
    def get_codec_recommendations(self, use_case: str, platform: str = None) -> List[CodecInfo]:
        """Get codec recommendations for specific use cases"""
        recommendations = []
        
        if use_case.lower() == "web_streaming":
            # Prioritize web-compatible streaming codecs
            video_codec = self.find_best_codec(CodecType.VIDEO, "streaming", "web")
            audio_codec = self.find_best_codec(CodecType.AUDIO, "streaming", "web")
            if video_codec:
                recommendations.append(video_codec)
            if audio_codec:
                recommendations.append(audio_codec)
        
        elif use_case.lower() == "mobile_app":
            # Prioritize hardware-accelerated codecs
            recommendations.extend(
                [c for c in self.get_hardware_accelerated_codecs() 
                 if "mobile" in c.platform_support]
            )
        
        elif use_case.lower() == "archival":
            # Prioritize lossless codecs
            recommendations.extend(self.get_lossless_codecs())
        
        elif use_case.lower() == "social_media":
            # H.264 for compatibility, AAC for audio
            h264 = self.get_codec("h264")
            aac = self.get_codec("aac")
            if h264:
                recommendations.append(h264)
            if aac:
                recommendations.append(aac)
        
        return recommendations
    
    def validate_codec_compatibility(self, codec_pairs: List[Tuple[str, str]]) -> Dict[str, bool]:
        """Validate codec combinations for compatibility"""
        results = {}
        
        for video_codec, audio_codec in codec_pairs:
            video_info = self.get_codec(video_codec)
            audio_info = self.get_codec(audio_codec)
            
            key = f"{video_codec}+{audio_codec}"
            
            if not video_info or not audio_info:
                results[key] = False
                continue
            
            # Check if they share common container formats
            common_containers = set(video_info.extensions) & set(audio_info.extensions)
            results[key] = len(common_containers) > 0
        
        return results
    
    def export_codec_database(self) -> Dict[str, Any]:
        """Export complete codec database"""
        return {
            "codecs": {
                codec_id: {
                    "name": codec.name,
                    "type": codec.codec_type.value,
                    "description": codec.description,
                    "license": codec.license_type.value,
                    "quality_range": codec.quality_range,
                    "compression_efficiency": codec.compression_efficiency,
                    "encoding_speed": codec.encoding_speed,
                    "hardware_support": codec.hardware_support,
                    "streaming_optimized": codec.streaming_optimized,
                    "lossless_capable": codec.lossless_capable,
                    "platform_support": codec.platform_support,
                    "available": self.system_codecs.get(codec_id, False)
                }
                for codec_id, codec in self.codecs.items()
            },
            "aliases": self.codec_aliases,
            "system_availability": self.system_codecs
        }


# Global registry instance
codec_registry = CodecRegistry()


class CodecMatcher:
    """Advanced codec matching and recommendation engine"""
    
    def __init__(self):
        self.registry = codec_registry
    
    def match_optimal_codecs(self, 
                           requirements: Dict[str, Any]) -> Dict[str, CodecInfo]:
        """Match optimal codecs based on requirements"""
        
        matched_codecs = {}
        
        # Extract requirements
        target_quality = requirements.get("quality", 8)
        max_encoding_time = requirements.get("max_encoding_time", 5)
        target_platforms = requirements.get("platforms", ["web"])
        license_requirement = requirements.get("license", None)
        file_size_priority = requirements.get("file_size_priority", 5)
        
        # Find video codec
        video_candidates = self.registry.get_codecs_by_type(CodecType.VIDEO)
        video_candidates = [c for c in video_candidates 
                          if any(platform in c.platform_support for platform in target_platforms)]
        
        if license_requirement:
            license_enum = CodecLicense(license_requirement)
            video_candidates = [c for c in video_candidates if c.license_type == license_enum]
        
        if video_candidates:
            def score_video_codec(codec: CodecInfo) -> float:
                score = 0.0
                
                # Quality factor
                quality_match = min(codec.quality_range[1], target_quality) / target_quality
                score += quality_match * 30
                
                # Encoding speed factor
                if codec.encoding_speed >= max_encoding_time:
                    score += 25
                
                # Compression efficiency factor
                score += codec.compression_efficiency * file_size_priority / 10 * 20
                
                # Hardware acceleration bonus
                if codec.hardware_support:
                    score += 15
                
                # Streaming optimization bonus
                if codec.streaming_optimized:
                    score += 10
                
                return score
            
            best_video_codec = max(video_candidates, key=score_video_codec)
            matched_codecs["video"] = best_video_codec
        
        # Find audio codec
        audio_candidates = self.registry.get_codecs_by_type(CodecType.AUDIO)
        audio_candidates = [c for c in audio_candidates 
                          if any(platform in c.platform_support for platform in target_platforms)]
        
        if license_requirement:
            license_enum = CodecLicense(license_requirement)
            audio_candidates = [c for c in audio_candidates if c.license_type == license_enum]
        
        if audio_candidates:
            def score_audio_codec(codec: CodecInfo) -> float:
                score = 0.0
                
                # Quality factor
                quality_match = min(codec.quality_range[1], target_quality) / target_quality
                score += quality_match * 40
                
                # Compression efficiency
                score += codec.compression_efficiency * 30 / 10
                
                # Encoding speed
                score += codec.encoding_speed * 20 / 10
                
                # Streaming optimization
                if codec.streaming_optimized:
                    score += 10
                
                return score
            
            best_audio_codec = max(audio_candidates, key=score_audio_codec)
            matched_codecs["audio"] = best_audio_codec
        
        return matched_codecs


# Export main classes and functions
__all__ = [
    'CodecType',
    'CodecLicense',
    'CodecInfo',
    'CodecRegistry',
    'CodecMatcher',
    'codec_registry'
]