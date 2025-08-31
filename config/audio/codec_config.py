"""
Audio Codec Configuration Module for IA-Influencer Agent Platform
================================================================

Professional audio codec configuration and optimization for multi-platform distribution.
Supports all major audio formats and streaming platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
 STRICT COPYRIGHT WARNING 
This code and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class CodecType(Enum):
    """Audio codec types"""
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    HYBRID = "hybrid"


class CodecFamily(Enum):
    """Audio codec families"""
    PCM = "pcm"          # WAV, AIFF
    MPEG = "mpeg"        # MP3, AAC
    XIPH = "xiph"        # Vorbis, Opus, FLAC
    WINDOWS = "windows"   # WMA
    PROPRIETARY = "proprietary"  # Various


class BitrateMode(Enum):
    """Bitrate encoding modes"""
    CBR = "cbr"          # Constant bitrate
    VBR = "vbr"          # Variable bitrate
    ABR = "abr"          # Average bitrate
    CONSTRAINED_VBR = "constrained_vbr"


class QualityProfile(Enum):
    """Audio quality profiles"""
    ARCHIVAL = "archival"        # Highest quality, no compression
    MASTERING = "mastering"      # Studio mastering quality
    DISTRIBUTION = "distribution" # High quality distribution
    STREAMING = "streaming"       # Streaming optimized
    MOBILE = "mobile"            # Mobile optimized
    VOICE = "voice"              # Voice/speech optimized


@dataclass
class CodecCapabilities:
    """Codec technical capabilities"""
    max_sample_rate: int
    max_bit_depth: int
    max_channels: int
    supports_metadata: bool
    supports_chapters: bool
    supports_embedded_images: bool
    supports_variable_bitrate: bool
    streaming_friendly: bool
    hardware_acceleration: bool


@dataclass
class EncodingPreset:
    """Audio encoding preset configuration"""
    name: str
    bitrate_kbps: Optional[int] = None
    quality_level: Optional[float] = None  # 0.0-1.0 or codec-specific
    bitrate_mode: BitrateMode = BitrateMode.VBR
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    channels: Optional[int] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


class CodecConfig:
    """
    Comprehensive audio codec configuration manager
    
    Manages codec configurations, encoding presets, and optimization settings
    for all supported audio formats across different platforms.
    """
    
    def __init__(self):
        """Initialize codec configuration manager"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize codec registry
        self._codecs = self._initialize_codec_registry()
        
        # Initialize encoding presets
        self._presets = self._initialize_encoding_presets()
        
        # Platform-specific codec preferences
        self._platform_codecs = self._initialize_platform_codecs()
        
        # Quality profiles
        self._quality_profiles = self._initialize_quality_profiles()
        
        self.logger.info("CodecConfig initialized successfully")
    
    def _initialize_codec_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive codec registry"""



        return {
            "wav": {
                "name": "WAV",
                "type": CodecType.LOSSLESS,
                "family": CodecFamily.PCM,
                "extensions": [".wav"],
                "mime_types": ["audio/wav", "audio/wave"],
                "capabilities": CodecCapabilities(
                    max_sample_rate=192000,
                    max_bit_depth=32,
                    max_channels=8,
                    supports_metadata=True,
                    supports_chapters=False,
                    supports_embedded_images=False,
                    supports_variable_bitrate=False,
                    streaming_friendly=False,
                    hardware_acceleration=True
                ),
                "use_cases": ["studio", "mastering", "archival"],
                "pros": ["Lossless", "Universal support", "Simple format"],
                "cons": ["Large file size", "Not streaming friendly"]
            },
            "flac": {
                "name": "FLAC",
                "type": CodecType.LOSSLESS,
                "family": CodecFamily.XIPH,
                "extensions": [".flac"],
                "mime_types": ["audio/flac"],
                "capabilities": CodecCapabilities(
                    max_sample_rate=192000,
                    max_bit_depth=32,
                    max_channels=8,
                    supports_metadata=True,
                    supports_chapters=True,
                    supports_embedded_images=True,
                    supports_variable_bitrate=False,
                    streaming_friendly=True,
                    hardware_acceleration=False
                ),
                "use_cases": ["archival", "audiophile", "distribution"],
                "pros": ["Lossless", "Good compression", "Rich metadata"],
                "cons": ["CPU intensive", "Limited mobile support"]
            },
            "mp3": {
                "name": "MP3",
                "type": CodecType.LOSSY,
                "family": CodecFamily.MPEG,
                "extensions": [".mp3"],
                "mime_types": ["audio/mpeg", "audio/mp3"],
                "capabilities": CodecCapabilities(
                    max_sample_rate=48000,
                    max_bit_depth=16,
                    max_channels=2,
                    supports_metadata=True,
                    supports_chapters=False,
                    supports_embedded_images=True,
                    supports_variable_bitrate=True,
                    streaming_friendly=True,
                    hardware_acceleration=True
                ),
                "use_cases": ["distribution", "streaming", "mobile"],
                "pros": ["Universal support", "Good compression", "Mature format"],
                "cons": ["Lossy", "Patent issues", "Limited to stereo"]
            },
            "aac": {
                "name": "AAC",
                "type": CodecType.LOSSY,
                "family": CodecFamily.MPEG,
                "extensions": [".aac", ".m4a"],
                "mime_types": ["audio/aac", "audio/mp4"],
                "capabilities": CodecCapabilities(
                    max_sample_rate=96000,
                    max_bit_depth=24,
                    max_channels=8,
                    supports_metadata=True,
                    supports_chapters=True,
                    supports_embedded_images=True,
                    supports_variable_bitrate=True,
                    streaming_friendly=True,
                    hardware_acceleration=True
                ),
                "use_cases": ["streaming", "mobile", "broadcast"],
                "pros": ["Better than MP3", "Wide support", "Efficient"],
                "cons": ["Lossy", "Patent restrictions"]
            },
            "opus": {
                "name": "Opus",
                "type": CodecType.LOSSY,
                "family": CodecFamily.XIPH,
                "extensions": [".opus"],
                "mime_types": ["audio/opus"],
                "capabilities": CodecCapabilities(
                    max_sample_rate=48000,
                    max_bit_depth=16,
                    max_channels=8,
                    supports_metadata=True,
                    supports_chapters=False,
                    supports_embedded_images=False,
                    supports_variable_bitrate=True,
                    streaming_friendly=True,
                    hardware_acceleration=False
                ),
                "use_cases": ["streaming", "voice", "real-time"],
                "pros": ["Best efficiency", "Low latency", "Open source"],
                "cons": ["Limited support", "Newer format"]
            },
            "ogg": {
                "name": "Ogg Vorbis",
                "type": CodecType.LOSSY,
                "family": CodecFamily.XIPH,
                "extensions": [".ogg"],
                "mime_types": ["audio/ogg"],
                "capabilities": CodecCapabilities(
                    max_sample_rate=192000,
                    max_bit_depth=24,
                    max_channels=8,
                    supports_metadata=True,
                    supports_chapters=False,
                    supports_embedded_images=False,
                    supports_variable_bitrate=True,
                    streaming_friendly=True,
                    hardware_acceleration=False
                ),
                "use_cases": ["streaming", "gaming", "open source"],
                "pros": ["Open source", "Good quality", "No patents"],
                "cons": ["Limited mobile support", "CPU intensive"]
            }
        }
    
    def _initialize_encoding_presets(self) -> Dict[str, Dict[str, EncodingPreset]]:
        """Initialize encoding presets for each codec"""
        presets = {}
        
        # MP3 Presets
        presets["mp3"] = {
            "archival": EncodingPreset(
                name="Archival Quality",
                bitrate_kbps=320,
                bitrate_mode=BitrateMode.CBR,
                sample_rate=44100,
                bit_depth=16,
                channels=2
            ),
            "high": EncodingPreset(
                name="High Quality",
                quality_level=0.0,  # LAME V0
                bitrate_mode=BitrateMode.VBR,
                sample_rate=44100,
                bit_depth=16,
                channels=2
            ),
            "standard": EncodingPreset(
                name="Standard Quality",
                quality_level=2.0,  # LAME V2
                bitrate_mode=BitrateMode.VBR,
                sample_rate=44100,
                bit_depth=16,
                channels=2
            ),
            "mobile": EncodingPreset(
                name="Mobile Optimized",
                bitrate_kbps=128,
                bitrate_mode=BitrateMode.CBR,
                sample_rate=44100,
                bit_depth=16,
                channels=2
            ),
            "voice": EncodingPreset(
                name="Voice Optimized",
                bitrate_kbps=64,
                bitrate_mode=BitrateMode.CBR,
                sample_rate=22050,
                bit_depth=16,
                channels=1
            )
        }
        
        # AAC Presets
        presets["aac"] = {
            "archival": EncodingPreset(
                name="Archival Quality",
                bitrate_kbps=256,
                bitrate_mode=BitrateMode.CBR,
                sample_rate=48000,
                bit_depth=24,
                channels=2
            ),
            "high": EncodingPreset(
                name="High Quality",
                quality_level=0.9,
                bitrate_mode=BitrateMode.VBR,
                sample_rate=48000,
                bit_depth=16,
                channels=2
            ),
            "standard": EncodingPreset(
                name="Standard Quality",
                bitrate_kbps=128,
                bitrate_mode=BitrateMode.VBR,
                sample_rate=44100,
                bit_depth=16,
                channels=2
            ),
            "mobile": EncodingPreset(
                name="Mobile Optimized",
                bitrate_kbps=96,
                bitrate_mode=BitrateMode.CBR,
                sample_rate=44100,
                bit_depth=16,
                channels=2
            ),
            "voice": EncodingPreset(
                name="Voice Optimized",
                bitrate_kbps=48,
                bitrate_mode=BitrateMode.CBR,
                sample_rate=22050,
                bit_depth=16,
                channels=1
            )
        }
        
        # FLAC Presets
        presets["flac"] = {
            "archival": EncodingPreset(
                name="Archival Quality",
                quality_level=8.0,  # Maximum compression
                sample_rate=96000,
                bit_depth=24,
                channels=2
            ),
            "high": EncodingPreset(
                name="High Quality",
                quality_level=5.0,  # Balanced compression
                sample_rate=48000,
                bit_depth=24,
                channels=2
            ),
            "standard": EncodingPreset(
                name="Standard Quality",
                quality_level=3.0,  # Fast compression
                sample_rate=44100,
                bit_depth=16,
                channels=2
            )
        }
        
        # Opus Presets
        presets["opus"] = {
            "high": EncodingPreset(
                name="High Quality",
                bitrate_kbps=160,
                bitrate_mode=BitrateMode.VBR,
                sample_rate=48000,
                bit_depth=16,
                channels=2
            ),
            "standard": EncodingPreset(
                name="Standard Quality",
                bitrate_kbps=96,
                bitrate_mode=BitrateMode.VBR,
                sample_rate=48000,
                bit_depth=16,
                channels=2
            ),
            "voice": EncodingPreset(
                name="Voice Optimized",
                bitrate_kbps=32,
                bitrate_mode=BitrateMode.VBR,
                sample_rate=16000,
                bit_depth=16,
                channels=1,
                additional_params={"application": "voip"}
            )
        }
        
        return presets
    
    def _initialize_platform_codecs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific codec preferences"""



        return {
            "spotify": {
                "primary": "ogg",
                "fallback": "mp3",
                "quality": "high",
                "max_bitrate": 320,
                "requirements": {
                    "sample_rate": [44100],
                    "channels": [1, 2],
                    "formats": ["ogg", "mp3"]
                }
            },
            "apple_music": {
                "primary": "aac",
                "fallback": "mp3",
                "quality": "high",
                "max_bitrate": 256,
                "requirements": {
                    "sample_rate": [44100, 48000],
                    "channels": [1, 2],
                    "formats": ["aac", "m4a"]
                }
            },
            "youtube": {
                "primary": "aac",
                "fallback": "mp3",
                "quality": "standard",
                "max_bitrate": 128,
                "requirements": {
                    "sample_rate": [48000],
                    "channels": [1, 2],
                    "formats": ["aac", "mp3"]
                }
            },
            "instagram": {
                "primary": "aac",
                "fallback": "mp3",
                "quality": "mobile",
                "max_bitrate": 128,
                "requirements": {
                    "sample_rate": [44100],
                    "channels": [1, 2],
                    "formats": ["aac", "mp3"],
                    "max_duration": 60
                }
            },
            "tiktok": {
                "primary": "aac",
                "fallback": "mp3",
                "quality": "mobile",
                "max_bitrate": 128,
                "requirements": {
                    "sample_rate": [44100],
                    "channels": [2],
                    "formats": ["aac", "mp3"],
                    "max_duration": 180
                }
            },
            "soundcloud": {
                "primary": "mp3",
                "fallback": "aac",
                "quality": "high",
                "max_bitrate": 320,
                "requirements": {
                    "sample_rate": [44100, 48000],
                    "channels": [1, 2],
                    "formats": ["mp3", "aac"]
                }
            },
            "podcast": {
                "primary": "mp3",
                "fallback": "aac",
                "quality": "voice",
                "max_bitrate": 128,
                "requirements": {
                    "sample_rate": [44100, 22050],
                    "channels": [1, 2],
                    "formats": ["mp3", "aac"],
                    "mono_preferred": True
                }
            }
        }
    
    def _initialize_quality_profiles(self) -> Dict[QualityProfile, Dict[str, Any]]:
        """Initialize quality profiles with codec recommendations"""



        return {
            QualityProfile.ARCHIVAL: {
                "description": "Highest quality for archival storage",
                "recommended_codecs": ["flac", "wav"],
                "min_sample_rate": 48000,
                "min_bit_depth": 24,
                "target_quality": 1.0,
                "use_cases": ["mastering", "archival", "source material"]
            },
            QualityProfile.MASTERING: {
                "description": "Studio mastering quality",
                "recommended_codecs": ["flac", "wav"],
                "min_sample_rate": 44100,
                "min_bit_depth": 24,
                "target_quality": 0.95,
                "use_cases": ["studio work", "professional mixing"]
            },
            QualityProfile.DISTRIBUTION: {
                "description": "High quality distribution",
                "recommended_codecs": ["flac", "aac", "mp3"],
                "min_sample_rate": 44100,
                "min_bit_depth": 16,
                "target_quality": 0.90,
                "use_cases": ["digital sales", "premium streaming"]
            },
            QualityProfile.STREAMING: {
                "description": "Streaming optimized quality",
                "recommended_codecs": ["aac", "opus", "ogg"],
                "min_sample_rate": 44100,
                "min_bit_depth": 16,
                "target_quality": 0.80,
                "use_cases": ["streaming platforms", "online distribution"]
            },
            QualityProfile.MOBILE: {
                "description": "Mobile device optimized",
                "recommended_codecs": ["aac", "mp3"],
                "min_sample_rate": 44100,
                "min_bit_depth": 16,
                "target_quality": 0.70,
                "use_cases": ["mobile apps", "bandwidth limited"]
            },
            QualityProfile.VOICE: {
                "description": "Voice/speech optimized",
                "recommended_codecs": ["opus", "aac", "mp3"],
                "min_sample_rate": 16000,
                "min_bit_depth": 16,
                "target_quality": 0.60,
                "use_cases": ["podcasts", "voice calls", "audiobooks"]
            }
        }
    
    def get_codec_info(self, codec: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific codec
        
        Args:
            codec: Codec identifier
            
        Returns:
            Codec information dictionary or None if not found
        """



        return self._codecs.get(codec.lower())
    
    def get_supported_codecs(self) -> List[str]:
        """Get list of all supported codecs"""



        return list(self._codecs.keys())
    
    def get_lossless_codecs(self) -> List[str]:
        """Get list of lossless codecs"""



        return [
            codec for codec, info in self._codecs.items()
            if info["type"] == CodecType.LOSSLESS
        ]
    
    def get_streaming_codecs(self) -> List[str]:
        """Get list of streaming-friendly codecs"""



        return [
            codec for codec, info in self._codecs.items()
            if info["capabilities"].streaming_friendly
        ]
    
    def recommend_codec(self, 
                       platform: Optional[str] = None,
                       quality_profile: Optional[QualityProfile] = None,
                       use_case: Optional[str] = None,
                       file_size_priority: bool = False) -> Dict[str, Any]:
        """
        Recommend optimal codec based on requirements
        
        Args:
            platform: Target platform
            quality_profile: Desired quality profile
            use_case: Specific use case
            file_size_priority: Prioritize file size over quality
            
        Returns:
            Codec recommendation with rationale
        """



        try:
            recommendations = []
            
            # Platform-based recommendation
            if platform and platform.lower() in self._platform_codecs:
                platform_config = self._platform_codecs[platform.lower()]
                recommendations.append({
                    "codec": platform_config["primary"],
                    "reason": f"Primary codec for {platform}",
                    "priority": 10,
                    "preset": platform_config["quality"]
                })
                
                recommendations.append({
                    "codec": platform_config["fallback"],
                    "reason": f"Fallback codec for {platform}",
                    "priority": 8,
                    "preset": platform_config["quality"]
                })
            
            # Quality profile recommendation
            if quality_profile:
                profile_config = self._quality_profiles[quality_profile]
                for codec in profile_config["recommended_codecs"]:
                    recommendations.append({
                        "codec": codec,
                        "reason": f"Recommended for {quality_profile.value} quality",
                        "priority": 9,
                        "preset": "high" if quality_profile in [QualityProfile.ARCHIVAL, QualityProfile.MASTERING] else "standard"
                    })
            
            # Use case recommendation
            if use_case:
                use_case_map = {
                    "music": ["aac", "mp3", "flac"],
                    "voice": ["opus", "mp3", "aac"],
                    "podcast": ["mp3", "aac"],
                    "streaming": ["aac", "opus", "ogg"],
                    "archival": ["flac", "wav"],
                    "mobile": ["aac", "mp3"]
                }
                
                if use_case in use_case_map:
                    for codec in use_case_map[use_case]:
                        recommendations.append({
                            "codec": codec,
                            "reason": f"Optimized for {use_case}",
                            "priority": 7,
                            "preset": "standard"
                        })
            
            # File size priority adjustment
            if file_size_priority:
                efficiency_order = ["opus", "aac", "ogg", "mp3"]
                for i, codec in enumerate(efficiency_order):
                    recommendations.append({
                        "codec": codec,
                        "reason": "Optimized for file size",
                        "priority": 6 - i,
                        "preset": "mobile"
                    })
            
            # Default recommendations
            if not recommendations:
                recommendations = [
                    {"codec": "aac", "reason": "Universal compatibility", "priority": 5, "preset": "standard"},
                    {"codec": "mp3", "reason": "Widest compatibility", "priority": 4, "preset": "standard"}
                ]
            
            # Sort by priority and remove duplicates
            seen_codecs = set()
            unique_recommendations = []
            
            for rec in sorted(recommendations, key=lambda x: x["priority"], reverse=True):
                if rec["codec"] not in seen_codecs:
                    seen_codecs.add(rec["codec"])
                    unique_recommendations.append(rec)
            
            # Get the top recommendation
            top_recommendation = unique_recommendations[0]
            
            return {
                "recommended_codec": top_recommendation["codec"],
                "reason": top_recommendation["reason"],
                "preset": top_recommendation["preset"],
                "alternatives": unique_recommendations[1:3],  # Top 2 alternatives
                "codec_info": self.get_codec_info(top_recommendation["codec"])
            }
            
        except Exception as e:
            self.logger.error(f"Codec recommendation failed: {e}")
            return {
                "recommended_codec": "aac",
                "reason": "Fallback recommendation",
                "preset": "standard",
                "alternatives": [],
                "codec_info": self.get_codec_info("aac")
            }
    
    def get_encoding_preset(self, codec: str, preset_name: str) -> Optional[EncodingPreset]:
        """
        Get encoding preset for specific codec
        
        Args:
            codec: Codec identifier
            preset_name: Preset name
            
        Returns:
            Encoding preset or None if not found
        """
        codec_presets = self._presets.get(codec.lower())
        if codec_presets:
            return codec_presets.get(preset_name.lower())
        return None
    
    def get_available_presets(self, codec: str) -> List[str]:
        """
        Get list of available presets for a codec
        
        Args:
            codec: Codec identifier
            
        Returns:
            List of preset names
        """
        codec_presets = self._presets.get(codec.lower())
        if codec_presets:
            return list(codec_presets.keys())
        return []
    
    def validate_codec_parameters(self, 
                                 codec: str, 
                                 sample_rate: int,
                                 bit_depth: int,
                                 channels: int,
                                 bitrate: Optional[int] = None) -> Tuple[bool, List[str]]:
        """
        Validate codec parameters against capabilities
        
        Args:
            codec: Codec identifier
            sample_rate: Sample rate in Hz
            bit_depth: Bit depth
            channels: Number of channels
            bitrate: Bitrate in kbps (optional)
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        is_valid = True
        
        try:
            codec_info = self.get_codec_info(codec)
            if not codec_info:
                errors.append(f"Unsupported codec: {codec}")
                return False, errors
            
            capabilities = codec_info["capabilities"]
            
            # Validate sample rate
            if sample_rate > capabilities.max_sample_rate:
                errors.append(
                    f"Sample rate {sample_rate} exceeds maximum {capabilities.max_sample_rate} for {codec}"
                )
                is_valid = False
            
            # Validate bit depth
            if bit_depth > capabilities.max_bit_depth:
                errors.append(
                    f"Bit depth {bit_depth} exceeds maximum {capabilities.max_bit_depth} for {codec}"
                )
                is_valid = False
            
            # Validate channels
            if channels > capabilities.max_channels:
                errors.append(
                    f"Channel count {channels} exceeds maximum {capabilities.max_channels} for {codec}"
                )
                is_valid = False
            
            # Codec-specific validations
            if codec == "mp3" and sample_rate not in [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]:
                errors.append(f"Invalid sample rate {sample_rate} for MP3 (must be standard rate)")
                is_valid = False
            
            if codec == "aac" and bitrate and bitrate > 320:
                errors.append(f"Bitrate {bitrate} too high for AAC (maximum 320 kbps recommended)")
                is_valid = False
                
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            is_valid = False
        
        return is_valid, errors
    
    def get_platform_requirements(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get platform-specific codec requirements
        
        Args:
            platform: Platform identifier
            
        Returns:
            Platform requirements or None if not found
        """



        return self._platform_codecs.get(platform.lower())
    
    def estimate_file_size(self, 
                          codec: str,
                          duration_seconds: float,
                          bitrate_kbps: int,
                          is_vbr: bool = False) -> Dict[str, float]:
        """
        Estimate encoded file size
        
        Args:
            codec: Codec identifier
            duration_seconds: Audio duration in seconds
            bitrate_kbps: Bitrate in kbps
            is_vbr: Whether using variable bitrate
            
        Returns:
            Size estimates in different units
        """



        try:
            # Base calculation: bitrate * duration
            base_size_bits = bitrate_kbps * 1000 * duration_seconds
            base_size_bytes = base_size_bits / 8
            
            # Adjust for VBR (typically 10-20% smaller)
            if is_vbr:
                base_size_bytes *= 0.85
            
            # Codec-specific overhead
            overhead_factors = {
                "mp3": 1.05,    # ID3 tags, frame headers
                "aac": 1.03,    # Container overhead
                "flac": 1.02,   # Metadata
                "ogg": 1.04,    # Ogg container
                "opus": 1.01,   # Minimal overhead
                "wav": 1.001    # Minimal header
            }
            
            overhead_factor = overhead_factors.get(codec.lower(), 1.05)
            final_size_bytes = base_size_bytes * overhead_factor
            
            return {
                "bytes": round(final_size_bytes),
                "kilobytes": round(final_size_bytes / 1024, 2),
                "megabytes": round(final_size_bytes / (1024 * 1024), 2),
                "duration_seconds": duration_seconds,
                "bitrate_kbps": bitrate_kbps,
                "codec": codec
            }
            
        except Exception as e:
            self.logger.error(f"File size estimation failed: {e}")
            return {"bytes": 0, "error": str(e)}
    
    def get_quality_comparison(self) -> Dict[str, Dict[str, float]]:
        """
        Get quality comparison between codecs
        
        Returns:
            Quality metrics for each codec
        """



        return {
            "flac": {
                "quality_score": 1.0,
                "compression_ratio": 0.6,
                "compatibility": 0.7,
                "streaming_efficiency": 0.6
            },
            "wav": {
                "quality_score": 1.0,
                "compression_ratio": 1.0,
                "compatibility": 0.9,
                "streaming_efficiency": 0.3
            },
            "aac": {
                "quality_score": 0.85,
                "compression_ratio": 0.15,
                "compatibility": 0.95,
                "streaming_efficiency": 0.9
            },
            "mp3": {
                "quality_score": 0.75,
                "compression_ratio": 0.12,
                "compatibility": 1.0,
                "streaming_efficiency": 0.85
            },
            "opus": {
                "quality_score": 0.9,
                "compression_ratio": 0.08,
                "compatibility": 0.6,
                "streaming_efficiency": 1.0
            },
            "ogg": {
                "quality_score": 0.8,
                "compression_ratio": 0.12,
                "compatibility": 0.7,
                "streaming_efficiency": 0.8
            }
        }
    
    def create_custom_preset(self, 
                            codec: str,
                            preset_name: str,
                            **params) -> bool:
        """
        Create custom encoding preset
        
        Args:
            codec: Target codec
            preset_name: Name for the preset
            **params: Encoding parameters
            
        Returns:
            Success status
        """



        try:
            if codec.lower() not in self._presets:
                self._presets[codec.lower()] = {}
            
            preset = EncodingPreset(
                name=preset_name,
                **params
            )
            
            self._presets[codec.lower()][preset_name.lower()] = preset
            self.logger.info(f"Created custom preset '{preset_name}' for {codec}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create custom preset: {e}")
            return False
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export complete codec configuration"""



        try:
            return {
                "codecs": self._codecs,
                "presets": {
                    codec: {
                        name: {
                            "name": preset.name,
                            "bitrate_kbps": preset.bitrate_kbps,
                            "quality_level": preset.quality_level,
                            "bitrate_mode": preset.bitrate_mode.value,
                            "sample_rate": preset.sample_rate,
                            "bit_depth": preset.bit_depth,
                            "channels": preset.channels,
                            "additional_params": preset.additional_params
                        }
                        for name, preset in presets.items()
                    }
                    for codec, presets in self._presets.items()
                },
                "platform_codecs": self._platform_codecs,
                "quality_profiles": {
                    profile.value: config
                    for profile, config in self._quality_profiles.items()
                }
            }
        except Exception as e:
            self.logger.error(f"Configuration export failed: {e}")
            return {}
