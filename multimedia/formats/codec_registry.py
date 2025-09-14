"""
Ainflue Platform - Multimedia Formats - Codec Registry System
Professional codec management and registry for multimedia processing

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CodecType(Enum):
    """Codec types"""
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    DATA = "data"


class CodecCategory(Enum):
    """Codec categories"""
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    UNCOMPRESSED = "uncompressed"
    HYBRID = "hybrid"


class CodecComplexity(Enum):
    """Encoding complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class CodecCapabilities:
    """Codec capabilities and features"""
    max_resolution: Optional[str] = None  # e.g., "4K", "8K"
    max_channels: Optional[int] = None
    max_sample_rate: Optional[int] = None
    supports_hdr: bool = False
    supports_transparency: bool = False
    supports_lossless: bool = False
    supports_variable_bitrate: bool = True
    supports_multi_pass: bool = False
    hardware_acceleration: List[str] = field(default_factory=list)
    color_spaces: List[str] = field(default_factory=list)
    chroma_subsampling: List[str] = field(default_factory=list)


@dataclass
class CodecProfile:
    """Codec profile information"""
    name: str = ""
    description: str = ""
    level: Optional[str] = None
    max_bitrate: Optional[int] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    recommended_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodecInfo:
    """Comprehensive codec information"""
    codec_id: str = ""
    name: str = ""
    description: str = ""
    codec_type: CodecType = CodecType.VIDEO
    category: CodecCategory = CodecCategory.LOSSY
    complexity: CodecComplexity = CodecComplexity.MEDIUM
    
    # Technical specifications
    fourcc_codes: List[str] = field(default_factory=list)
    mime_types: List[str] = field(default_factory=list)
    file_extensions: List[str] = field(default_factory=list)
    
    # Capabilities
    capabilities: CodecCapabilities = field(default_factory=CodecCapabilities)
    profiles: List[CodecProfile] = field(default_factory=list)
    
    # Compatibility
    supported_containers: List[str] = field(default_factory=list)
    compatibility_notes: str = ""
    
    # Performance
    encoding_speed: str = "medium"  # slow, medium, fast, very_fast
    compression_efficiency: str = "good"  # poor, fair, good, excellent
    quality_retention: str = "good"  # poor, fair, good, excellent
    
    # Licensing and support
    license_type: str = "open"  # open, proprietary, patent_encumbered
    patent_status: str = "clear"  # clear, encumbered, unknown
    vendor: str = ""
    standard_body: str = ""
    specification_url: str = ""
    
    # Usage recommendations
    recommended_for: List[str] = field(default_factory=list)
    not_recommended_for: List[str] = field(default_factory=list)


class CodecRegistry:
    """Professional codec registry and management system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize codec registry"""
        self.config = config or {}
        self.codecs: Dict[str, CodecInfo] = {}
        self.codec_aliases: Dict[str, str] = {}
        self.fourcc_mapping: Dict[str, str] = {}
        
        # Initialize with common codecs
        self._initialize_video_codecs()
        self._initialize_audio_codecs()
        self._initialize_subtitle_codecs()
    
    def _initialize_video_codecs(self) -> None:
        """Initialize video codec registry"""
        try:
            # H.264/AVC
            h264 = CodecInfo(
                codec_id="h264",
                name="H.264/AVC",
                description="Advanced Video Coding - industry standard video codec",
                codec_type=CodecType.VIDEO,
                category=CodecCategory.LOSSY,
                complexity=CodecComplexity.MEDIUM,
                fourcc_codes=["avc1", "h264", "x264"],
                mime_types=["video/h264", "video/avc"],
                file_extensions=[".h264", ".264"],
                capabilities=CodecCapabilities(
                    max_resolution="8K",
                    supports_hdr=False,
                    supports_variable_bitrate=True,
                    supports_multi_pass=True,
                    hardware_acceleration=["nvenc", "qsv", "videotoolbox", "vaapi"],
                    color_spaces=["bt709", "bt601"],
                    chroma_subsampling=["4:2:0", "4:2:2", "4:4:4"]
                ),
                profiles=[
                    CodecProfile("Baseline", "Basic profile for mobile devices", "3.0"),
                    CodecProfile("Main", "Standard profile for broadcasting", "4.0"),
                    CodecProfile("High", "High quality profile", "5.2"),
                    CodecProfile("High 10", "10-bit profile", "5.2"),
                    CodecProfile("High 422", "Professional 4:2:2 profile", "5.2")
                ],
                supported_containers=["mp4", "mkv", "mov", "avi", "ts"],
                encoding_speed="medium",
                compression_efficiency="good",
                quality_retention="good",
                license_type="patent_encumbered",
                patent_status="encumbered",
                vendor="ITU-T/ISO",
                standard_body="ITU-T VCEG, ISO/IEC MPEG",
                recommended_for=["streaming", "broadcasting", "mobile", "web"],
                not_recommended_for=["archival_lossless"]
            )
            self.register_codec(h264)
            
            # H.265/HEVC
            h265 = CodecInfo(
                codec_id="h265",
                name="H.265/HEVC",
                description="High Efficiency Video Coding - next generation video codec",
                codec_type=CodecType.VIDEO,
                category=CodecCategory.LOSSY,
                complexity=CodecComplexity.HIGH,
                fourcc_codes=["hvc1", "hev1", "h265"],
                mime_types=["video/h265", "video/hevc"],
                file_extensions=[".h265", ".265", ".hevc"],
                capabilities=CodecCapabilities(
                    max_resolution="8K",
                    supports_hdr=True,
                    supports_variable_bitrate=True,
                    supports_multi_pass=True,
                    hardware_acceleration=["nvenc", "qsv", "videotoolbox", "vaapi"],
                    color_spaces=["bt709", "bt2020", "p3"],
                    chroma_subsampling=["4:2:0", "4:2:2", "4:4:4"]
                ),
                profiles=[
                    CodecProfile("Main", "8-bit 4:2:0", "5.1"),
                    CodecProfile("Main 10", "10-bit 4:2:0", "5.1"),
                    CodecProfile("Main 422 10", "10-bit 4:2:2", "5.1"),
                    CodecProfile("Main 444", "4:4:4 profile", "5.1")
                ],
                supported_containers=["mp4", "mkv", "mov", "ts"],
                encoding_speed="slow",
                compression_efficiency="excellent",
                quality_retention="excellent",
                license_type="patent_encumbered",
                patent_status="encumbered",
                vendor="ITU-T/ISO",
                standard_body="ITU-T VCEG, ISO/IEC MPEG",
                recommended_for=["4k_streaming", "hdr_content", "mobile", "ott"],
                not_recommended_for=["real_time_low_latency"]
            )
            self.register_codec(h265)
            
            # VP9
            vp9 = CodecInfo(
                codec_id="vp9",
                name="VP9",
                description="Google's open-source video codec",
                codec_type=CodecType.VIDEO,
                category=CodecCategory.LOSSY,
                complexity=CodecComplexity.HIGH,
                fourcc_codes=["vp09", "vp9"],
                mime_types=["video/vp9"],
                file_extensions=[".vp9"],
                capabilities=CodecCapabilities(
                    max_resolution="8K",
                    supports_hdr=True,
                    supports_variable_bitrate=True,
                    supports_multi_pass=True,
                    hardware_acceleration=["vaapi", "nvenc"],
                    color_spaces=["bt709", "bt2020"],
                    chroma_subsampling=["4:2:0", "4:2:2", "4:4:4"]
                ),
                profiles=[
                    CodecProfile("Profile 0", "8-bit 4:2:0"),
                    CodecProfile("Profile 1", "8-bit 4:2:2/4:4:4"),
                    CodecProfile("Profile 2", "10/12-bit 4:2:0"),
                    CodecProfile("Profile 3", "10/12-bit 4:2:2/4:4:4")
                ],
                supported_containers=["webm", "mkv", "mp4"],
                encoding_speed="slow",
                compression_efficiency="excellent",
                quality_retention="excellent",
                license_type="open",
                patent_status="clear",
                vendor="Google",
                recommended_for=["web_streaming", "youtube", "open_source"],
                not_recommended_for=["legacy_devices"]
            )
            self.register_codec(vp9)
            
            # AV1
            av1 = CodecInfo(
                codec_id="av1",
                name="AV1",
                description="Alliance for Open Media next-generation codec",
                codec_type=CodecType.VIDEO,
                category=CodecCategory.LOSSY,
                complexity=CodecComplexity.VERY_HIGH,
                fourcc_codes=["av01"],
                mime_types=["video/av01"],
                file_extensions=[".av1"],
                capabilities=CodecCapabilities(
                    max_resolution="8K",
                    supports_hdr=True,
                    supports_variable_bitrate=True,
                    supports_multi_pass=True,
                    hardware_acceleration=["svt", "aom"],
                    color_spaces=["bt709", "bt2020"],
                    chroma_subsampling=["4:2:0", "4:2:2", "4:4:4"]
                ),
                profiles=[
                    CodecProfile("Main", "8-bit 4:2:0"),
                    CodecProfile("High", "8-bit 4:4:4"),
                    CodecProfile("Professional", "12-bit 4:2:2/4:4:4")
                ],
                supported_containers=["mp4", "webm", "mkv"],
                encoding_speed="very_slow",
                compression_efficiency="excellent",
                quality_retention="excellent",
                license_type="open",
                patent_status="clear",
                vendor="AOMedia",
                standard_body="Alliance for Open Media",
                recommended_for=["future_streaming", "archival", "ott_premium"],
                not_recommended_for=["real_time", "mobile_encode"]
            )
            self.register_codec(av1)
            
        except Exception as e:
            logger.error(f"Error initializing video codecs: {e}")
    
    def _initialize_audio_codecs(self) -> None:
        """Initialize audio codec registry"""
        try:
            # AAC
            aac = CodecInfo(
                codec_id="aac",
                name="Advanced Audio Coding",
                description="Standard audio codec for high-quality audio compression",
                codec_type=CodecType.AUDIO,
                category=CodecCategory.LOSSY,
                complexity=CodecComplexity.MEDIUM,
                fourcc_codes=["mp4a"],
                mime_types=["audio/aac", "audio/mp4"],
                file_extensions=[".aac", ".m4a"],
                capabilities=CodecCapabilities(
                    max_channels=48,
                    max_sample_rate=96000,
                    supports_variable_bitrate=True,
                    hardware_acceleration=["aac_at"]
                ),
                profiles=[
                    CodecProfile("LC", "Low Complexity", bitrate_range="64-320 kbps"),
                    CodecProfile("HE", "High Efficiency", bitrate_range="32-128 kbps"),
                    CodecProfile("HE v2", "High Efficiency v2", bitrate_range="16-64 kbps")
                ],
                supported_containers=["mp4", "mov", "3gp", "ts"],
                encoding_speed="fast",
                compression_efficiency="good",
                quality_retention="good",
                license_type="patent_encumbered",
                patent_status="encumbered",
                vendor="Dolby/Fraunhofer",
                recommended_for=["streaming", "mobile", "broadcasting"],
                not_recommended_for=["lossless_archival"]
            )
            self.register_codec(aac)
            
            # Opus
            opus = CodecInfo(
                codec_id="opus",
                name="Opus",
                description="Modern open-source audio codec",
                codec_type=CodecType.AUDIO,
                category=CodecCategory.LOSSY,
                complexity=CodecComplexity.MEDIUM,
                mime_types=["audio/opus"],
                file_extensions=[".opus"],
                capabilities=CodecCapabilities(
                    max_channels=255,
                    max_sample_rate=48000,
                    supports_variable_bitrate=True
                ),
                supported_containers=["webm", "ogg", "mkv"],
                encoding_speed="fast",
                compression_efficiency="excellent",
                quality_retention="excellent",
                license_type="open",
                patent_status="clear",
                vendor="Xiph.Org/IETF",
                recommended_for=["voip", "real_time", "web_audio"],
                not_recommended_for=["legacy_devices"]
            )
            self.register_codec(opus)
            
            # FLAC
            flac = CodecInfo(
                codec_id="flac",
                name="Free Lossless Audio Codec",
                description="Open-source lossless audio compression",
                codec_type=CodecType.AUDIO,
                category=CodecCategory.LOSSLESS,
                complexity=CodecComplexity.LOW,
                mime_types=["audio/flac"],
                file_extensions=[".flac"],
                capabilities=CodecCapabilities(
                    max_channels=8,
                    max_sample_rate=655350,
                    supports_lossless=True
                ),
                supported_containers=["flac", "ogg", "mkv"],
                encoding_speed="fast",
                compression_efficiency="good",
                quality_retention="perfect",
                license_type="open",
                patent_status="clear",
                vendor="Xiph.Org",
                recommended_for=["archival", "audiophile", "mastering"],
                not_recommended_for=["streaming", "mobile"]
            )
            self.register_codec(flac)
            
        except Exception as e:
            logger.error(f"Error initializing audio codecs: {e}")
    
    def _initialize_subtitle_codecs(self) -> None:
        """Initialize subtitle codec registry"""
        try:
            # SubRip
            srt = CodecInfo(
                codec_id="subrip",
                name="SubRip",
                description="Simple text-based subtitle format",
                codec_type=CodecType.SUBTITLE,
                category=CodecCategory.UNCOMPRESSED,
                complexity=CodecComplexity.LOW,
                mime_types=["text/srt"],
                file_extensions=[".srt"],
                supported_containers=["mp4", "mkv", "avi"],
                license_type="open",
                patent_status="clear",
                recommended_for=["simple_subtitles", "web", "compatibility"],
                not_recommended_for=["complex_formatting", "graphics"]
            )
            self.register_codec(srt)
            
            # ASS/SSA
            ass = CodecInfo(
                codec_id="ass",
                name="Advanced SubStation Alpha",
                description="Advanced subtitle format with styling",
                codec_type=CodecType.SUBTITLE,
                category=CodecCategory.UNCOMPRESSED,
                complexity=CodecComplexity.MEDIUM,
                mime_types=["text/ass"],
                file_extensions=[".ass", ".ssa"],
                supported_containers=["mkv"],
                license_type="open",
                patent_status="clear",
                recommended_for=["anime", "advanced_styling", "karaoke"],
                not_recommended_for=["simple_subtitles", "web"]
            )
            self.register_codec(ass)
            
        except Exception as e:
            logger.error(f"Error initializing subtitle codecs: {e}")
    
    def register_codec(self, codec_info: CodecInfo) -> bool:
        """Register a new codec in the registry"""
        try:
            self.codecs[codec_info.codec_id] = codec_info
            
            # Register FourCC mappings
            for fourcc in codec_info.fourcc_codes:
                self.fourcc_mapping[fourcc.lower()] = codec_info.codec_id
            
            logger.info(f"Registered codec: {codec_info.name} ({codec_info.codec_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering codec: {e}")
            return False
    
    def get_codec(self, codec_id: str) -> Optional[CodecInfo]:
        """Get codec information by ID"""
        try:
            # Check direct lookup
            if codec_id in self.codecs:
                return self.codecs[codec_id]
            
            # Check aliases
            if codec_id in self.codec_aliases:
                return self.codecs[self.codec_aliases[codec_id]]
            
            # Check FourCC mapping
            if codec_id.lower() in self.fourcc_mapping:
                actual_id = self.fourcc_mapping[codec_id.lower()]
                return self.codecs[actual_id]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting codec: {e}")
            return None
    
    def search_codecs(
        self,
        codec_type: Optional[CodecType] = None,
        category: Optional[CodecCategory] = None,
        container: Optional[str] = None,
        features: Optional[List[str]] = None
    ) -> List[CodecInfo]:
        """Search codecs by criteria"""
        try:
            results = []
            
            for codec in self.codecs.values():
                # Filter by type
                if codec_type and codec.codec_type != codec_type:
                    continue
                
                # Filter by category
                if category and codec.category != category:
                    continue
                
                # Filter by container support
                if container and container not in codec.supported_containers:
                    continue
                
                # Filter by features
                if features:
                    # Check for specific feature requirements
                    for feature in features:
                        if feature == "hdr" and not codec.capabilities.supports_hdr:
                            continue
                        elif feature == "lossless" and not codec.capabilities.supports_lossless:
                            continue
                        elif feature == "hardware_acceleration" and not codec.capabilities.hardware_acceleration:
                            continue
                
                results.append(codec)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching codecs: {e}")
            return []
    
    def get_recommended_codec(
        self,
        use_case: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[CodecInfo]:
        """Get recommended codec for specific use case"""
        try:
            constraints = constraints or {}
            
            # Define use case mappings
            use_case_preferences = {
                "web_streaming": {
                    "video": ["h264", "vp9", "h265"],
                    "audio": ["aac", "opus"]
                },
                "mobile": {
                    "video": ["h264", "h265"],
                    "audio": ["aac"]
                },
                "broadcasting": {
                    "video": ["h264", "h265"],
                    "audio": ["aac"]
                },
                "archival": {
                    "video": ["h265", "av1"],
                    "audio": ["flac"]
                },
                "real_time": {
                    "video": ["h264"],
                    "audio": ["opus", "aac"]
                }
            }
            
            if use_case not in use_case_preferences:
                return None
            
            preferences = use_case_preferences[use_case]
            codec_type = constraints.get("type", "video")
            
            if codec_type not in preferences:
                return None
            
            # Return first available codec from preferences
            for codec_id in preferences[codec_type]:
                codec = self.get_codec(codec_id)
                if codec:
                    return codec
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting recommended codec: {e}")
            return None
    
    def validate_codec_compatibility(
        self,
        video_codec: str,
        audio_codec: str,
        container: str
    ) -> Dict[str, Any]:
        """Validate codec compatibility with container"""
        try:
            result = {
                "compatible": True,
                "warnings": [],
                "errors": []
            }
            
            video_info = self.get_codec(video_codec)
            audio_info = self.get_codec(audio_codec)
            
            # Check video codec compatibility
            if video_info:
                if container not in video_info.supported_containers:
                    result["errors"].append(f"Video codec {video_codec} not supported in {container}")
                    result["compatible"] = False
            else:
                result["errors"].append(f"Unknown video codec: {video_codec}")
                result["compatible"] = False
            
            # Check audio codec compatibility
            if audio_info:
                if container not in audio_info.supported_containers:
                    result["errors"].append(f"Audio codec {audio_codec} not supported in {container}")
                    result["compatible"] = False
            else:
                result["errors"].append(f"Unknown audio codec: {audio_codec}")
                result["compatible"] = False
            
            # Add compatibility warnings
            if video_info and video_info.license_type == "patent_encumbered":
                result["warnings"].append(f"Video codec {video_codec} may require licensing")
            
            if audio_info and audio_info.license_type == "patent_encumbered":
                result["warnings"].append(f"Audio codec {audio_codec} may require licensing")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating codec compatibility: {e}")
            return {
                "compatible": False,
                "warnings": [],
                "errors": [str(e)]
            }
    
    def get_codec_alternatives(
        self,
        codec_id: str,
        criteria: Optional[List[str]] = None
    ) -> List[CodecInfo]:
        """Get alternative codecs with similar characteristics"""
        try:
            original_codec = self.get_codec(codec_id)
            if not original_codec:
                return []
            
            criteria = criteria or ["type", "category", "quality"]
            alternatives = []
            
            for codec in self.codecs.values():
                if codec.codec_id == codec_id:
                    continue
                
                score = 0
                
                # Type match (mandatory)
                if codec.codec_type == original_codec.codec_type:
                    score += 10
                else:
                    continue
                
                # Category match
                if "category" in criteria and codec.category == original_codec.category:
                    score += 5
                
                # Quality match
                if "quality" in criteria and codec.quality_retention == original_codec.quality_retention:
                    score += 3
                
                # License preference (open source preferred)
                if "license" in criteria and codec.license_type == "open":
                    score += 2
                
                # Container compatibility
                if "containers" in criteria:
                    common_containers = set(codec.supported_containers) & set(original_codec.supported_containers)
                    score += len(common_containers)
                
                if score > 10:  # Minimum threshold
                    alternatives.append((codec, score))
            
            # Sort by score and return codecs
            alternatives.sort(key=lambda x: x[1], reverse=True)
            return [codec for codec, _ in alternatives]
            
        except Exception as e:
            logger.error(f"Error getting codec alternatives: {e}")
            return []
    
    def export_registry(self, file_path: Union[str, Path]) -> bool:
        """Export codec registry to JSON file"""
        try:
            registry_data = {
                "codecs": {},
                "aliases": self.codec_aliases,
                "fourcc_mapping": self.fourcc_mapping
            }
            
            # Serialize codec data
            for codec_id, codec_info in self.codecs.items():
                registry_data["codecs"][codec_id] = {
                    "codec_id": codec_info.codec_id,
                    "name": codec_info.name,
                    "description": codec_info.description,
                    "codec_type": codec_info.codec_type.value,
                    "category": codec_info.category.value,
                    # Add other fields as needed
                }
            
            with open(file_path, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            logger.info(f"Codec registry exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting codec registry: {e}")
            return False


# Export main classes
__all__ = [
    'CodecRegistry',
    'CodecInfo',
    'CodecCapabilities',
    'CodecProfile',
    'CodecType',
    'CodecCategory',
    'CodecComplexity'
]