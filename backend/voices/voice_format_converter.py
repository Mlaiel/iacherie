"""Voice Format Conversion System

Enterprise voice format conversion system with support for multiple audio formats,
quality optimization, and intelligent format selection for different platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import io
import tempfile
import os

try:
    from voice_quality_optimizer import QualityMetric, OptimizationTarget
    from voice_metadata_generator import VoiceMetadata
except ImportError:
    from .voice_quality_optimizer import QualityMetric, OptimizationTarget
    from .voice_metadata_generator import VoiceMetadata

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    OPUS = "opus"
    WMA = "wma"
    AIFF = "aiff"
    AU = "au"


class ConversionQuality(Enum):
    """Conversion quality levels"""
    LOSSLESS = "lossless"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    COMPRESSED = "compressed"


class CompressionType(Enum):
    """Audio compression types"""
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    HYBRID = "hybrid"


class PlatformFormat(Enum):
    """Platform-specific format requirements"""
    PODCAST_PLATFORMS = "podcast_platforms"
    STREAMING_SERVICES = "streaming_services"
    SOCIAL_MEDIA = "social_media"
    AUDIOBOOK_PLATFORMS = "audiobook_platforms"
    BROADCAST_RADIO = "broadcast_radio"
    MOBILE_APPS = "mobile_apps"
    WEB_PLAYERS = "web_players"
    VOICE_ASSISTANTS = "voice_assistants"


@dataclass
class ConversionSettings:
    """Voice conversion settings"""
    target_format: AudioFormat
    quality: ConversionQuality = ConversionQuality.HIGH
    sample_rate: Optional[int] = None
    bit_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    channels: Optional[int] = None
    normalize_audio: bool = True
    remove_silence: bool = False
    apply_eq: bool = False
    compression_level: float = 0.5
    preserve_metadata: bool = True
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormatCapabilities:
    """Audio format capabilities"""
    format: AudioFormat
    compression_type: CompressionType
    max_sample_rate: int
    max_bit_depth: int
    max_channels: int
    supports_metadata: bool
    file_size_efficiency: float  # 0-1 scale
    quality_retention: float  # 0-1 scale
    platform_compatibility: List[PlatformFormat]
    streaming_friendly: bool


@dataclass
class ConversionResult:
    """Voice format conversion result"""
    success: bool
    converted_audio: Optional[bytes] = None
    output_format: Optional[AudioFormat] = None
    output_metadata: Optional[VoiceMetadata] = None
    conversion_time: float = 0.0
    file_size_reduction: float = 0.0
    quality_loss: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    conversion_stats: Dict[str, Any] = field(default_factory=dict)


class VoiceFormatConverter:
    """Voice format conversion engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize voice format converter"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize format capabilities
        self.format_capabilities = self._init_format_capabilities()
        
        # Platform format requirements
        self.platform_requirements = self._init_platform_requirements()
        
        # Quality settings for different formats
        self.quality_presets = self._init_quality_presets()
        
        self.logger.info("Voice format converter initialized")
    
    def _init_format_capabilities(self) -> Dict[AudioFormat, FormatCapabilities]:
        """Initialize audio format capabilities"""
        return {
            AudioFormat.WAV: FormatCapabilities(
                format=AudioFormat.WAV,
                compression_type=CompressionType.LOSSLESS,
                max_sample_rate=192000,
                max_bit_depth=32,
                max_channels=8,
                supports_metadata=True,
                file_size_efficiency=0.1,
                quality_retention=1.0,
                platform_compatibility=[
                    PlatformFormat.PODCAST_PLATFORMS,
                    PlatformFormat.AUDIOBOOK_PLATFORMS,
                    PlatformFormat.BROADCAST_RADIO
                ],
                streaming_friendly=False
            ),
            AudioFormat.MP3: FormatCapabilities(
                format=AudioFormat.MP3,
                compression_type=CompressionType.LOSSY,
                max_sample_rate=48000,
                max_bit_depth=16,
                max_channels=2,
                supports_metadata=True,
                file_size_efficiency=0.9,
                quality_retention=0.85,
                platform_compatibility=[
                    PlatformFormat.PODCAST_PLATFORMS,
                    PlatformFormat.STREAMING_SERVICES,
                    PlatformFormat.SOCIAL_MEDIA,
                    PlatformFormat.MOBILE_APPS,
                    PlatformFormat.WEB_PLAYERS
                ],
                streaming_friendly=True
            ),
            AudioFormat.FLAC: FormatCapabilities(
                format=AudioFormat.FLAC,
                compression_type=CompressionType.LOSSLESS,
                max_sample_rate=655350,
                max_bit_depth=32,
                max_channels=8,
                supports_metadata=True,
                file_size_efficiency=0.6,
                quality_retention=1.0,
                platform_compatibility=[
                    PlatformFormat.STREAMING_SERVICES,
                    PlatformFormat.AUDIOBOOK_PLATFORMS
                ],
                streaming_friendly=False
            ),
            AudioFormat.AAC: FormatCapabilities(
                format=AudioFormat.AAC,
                compression_type=CompressionType.LOSSY,
                max_sample_rate=96000,
                max_bit_depth=32,
                max_channels=48,
                supports_metadata=True,
                file_size_efficiency=0.95,
                quality_retention=0.9,
                platform_compatibility=[
                    PlatformFormat.PODCAST_PLATFORMS,
                    PlatformFormat.STREAMING_SERVICES,
                    PlatformFormat.MOBILE_APPS,
                    PlatformFormat.VOICE_ASSISTANTS
                ],
                streaming_friendly=True
            ),
            AudioFormat.OPUS: FormatCapabilities(
                format=AudioFormat.OPUS,
                compression_type=CompressionType.LOSSY,
                max_sample_rate=48000,
                max_bit_depth=16,
                max_channels=255,
                supports_metadata=True,
                file_size_efficiency=0.98,
                quality_retention=0.92,
                platform_compatibility=[
                    PlatformFormat.WEB_PLAYERS,
                    PlatformFormat.VOICE_ASSISTANTS,
                    PlatformFormat.MOBILE_APPS
                ],
                streaming_friendly=True
            ),
            AudioFormat.OGG: FormatCapabilities(
                format=AudioFormat.OGG,
                compression_type=CompressionType.LOSSY,
                max_sample_rate=192000,
                max_bit_depth=32,
                max_channels=255,
                supports_metadata=True,
                file_size_efficiency=0.9,
                quality_retention=0.88,
                platform_compatibility=[
                    PlatformFormat.WEB_PLAYERS,
                    PlatformFormat.STREAMING_SERVICES
                ],
                streaming_friendly=True
            )
        }
    
    def _init_platform_requirements(self) -> Dict[PlatformFormat, Dict[str, Any]]:
        """Initialize platform-specific format requirements"""
        return {
            PlatformFormat.PODCAST_PLATFORMS: {
                "preferred_formats": [AudioFormat.MP3, AudioFormat.AAC],
                "max_file_size": 200 * 1024 * 1024,  # 200 MB
                "recommended_bitrate": 128,  # kbps
                "sample_rate": 44100,
                "channels": 2
            },
            PlatformFormat.STREAMING_SERVICES: {
                "preferred_formats": [AudioFormat.FLAC, AudioFormat.AAC, AudioFormat.MP3],
                "max_file_size": 1024 * 1024 * 1024,  # 1 GB
                "recommended_bitrate": 320,  # kbps
                "sample_rate": 44100,
                "channels": 2
            },
            PlatformFormat.SOCIAL_MEDIA: {
                "preferred_formats": [AudioFormat.MP3, AudioFormat.AAC],
                "max_file_size": 25 * 1024 * 1024,  # 25 MB
                "recommended_bitrate": 128,  # kbps
                "sample_rate": 44100,
                "channels": 2
            },
            PlatformFormat.AUDIOBOOK_PLATFORMS: {
                "preferred_formats": [AudioFormat.MP3, AudioFormat.M4A],
                "max_file_size": 500 * 1024 * 1024,  # 500 MB
                "recommended_bitrate": 64,  # kbps for speech
                "sample_rate": 22050,
                "channels": 1
            },
            PlatformFormat.VOICE_ASSISTANTS: {
                "preferred_formats": [AudioFormat.OPUS, AudioFormat.AAC],
                "max_file_size": 10 * 1024 * 1024,  # 10 MB
                "recommended_bitrate": 64,  # kbps
                "sample_rate": 16000,
                "channels": 1
            }
        }
    
    def _init_quality_presets(self) -> Dict[ConversionQuality, Dict[str, Any]]:
        """Initialize quality presets for conversion"""
        return {
            ConversionQuality.LOSSLESS: {
                "sample_rate": 48000,
                "bit_depth": 24,
                "channels": 2,
                "compression_level": 0.0,
                "normalize": False,
                "filter_settings": "none"
            },
            ConversionQuality.HIGH: {
                "sample_rate": 44100,
                "bit_depth": 16,
                "channels": 2,
                "compression_level": 0.3,
                "normalize": True,
                "filter_settings": "light"
            },
            ConversionQuality.MEDIUM: {
                "sample_rate": 44100,
                "bit_depth": 16,
                "channels": 2,
                "compression_level": 0.5,
                "normalize": True,
                "filter_settings": "moderate"
            },
            ConversionQuality.LOW: {
                "sample_rate": 22050,
                "bit_depth": 16,
                "channels": 1,
                "compression_level": 0.7,
                "normalize": True,
                "filter_settings": "aggressive"
            },
            ConversionQuality.COMPRESSED: {
                "sample_rate": 16000,
                "bit_depth": 16,
                "channels": 1,
                "compression_level": 0.9,
                "normalize": True,
                "filter_settings": "maximum"
            }
        }
    
    async def convert_format(
        self,
        voice_content: bytes,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: Optional[ConversionSettings] = None
    ) -> ConversionResult:
        """Convert voice content to target format"""
        start_time = datetime.now()
        
        try:
            # Use provided settings or create default
            if settings is None:
                settings = ConversionSettings(target_format=target_format)
            
            # Validate conversion feasibility
            validation_result = self._validate_conversion(source_format, target_format, settings)
            if not validation_result["valid"]:
                return ConversionResult(
                    success=False,
                    error_message=validation_result["error"]
                )
            
            # Get source audio properties
            source_metadata = await self._analyze_source_audio(voice_content, source_format)
            
            # Apply quality settings
            final_settings = self._apply_quality_settings(settings, source_metadata)
            
            # Perform conversion
            converted_audio = await self._perform_conversion(
                voice_content, source_format, target_format, final_settings
            )
            
            # Generate output metadata
            output_metadata = await self._generate_output_metadata(
                converted_audio, target_format, final_settings, source_metadata
            )
            
            # Calculate conversion metrics
            conversion_time = (datetime.now() - start_time).total_seconds()
            file_size_reduction = self._calculate_size_reduction(voice_content, converted_audio)
            quality_loss = self._estimate_quality_loss(source_format, target_format, final_settings)
            
            # Generate warnings if any
            warnings = self._generate_warnings(source_format, target_format, final_settings)
            
            return ConversionResult(
                success=True,
                converted_audio=converted_audio,
                output_format=target_format,
                output_metadata=output_metadata,
                conversion_time=conversion_time,
                file_size_reduction=file_size_reduction,
                quality_loss=quality_loss,
                warnings=warnings,
                conversion_stats={
                    "source_size": len(voice_content),
                    "output_size": len(converted_audio),
                    "compression_ratio": len(converted_audio) / len(voice_content),
                    "processing_time": conversion_time
                }
            )
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {str(e)}")
            conversion_time = (datetime.now() - start_time).total_seconds()
            
            return ConversionResult(
                success=False,
                error_message=str(e),
                conversion_time=conversion_time
            )
    
    def _validate_conversion(
        self,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: ConversionSettings
    ) -> Dict[str, Any]:
        """Validate conversion parameters"""
        try:
            # Check if target format is supported
            if target_format not in self.format_capabilities:
                return {
                    "valid": False,
                    "error": f"Unsupported target format: {target_format.value}"
                }
            
            # Check format capabilities
            target_caps = self.format_capabilities[target_format]
            
            # Validate sample rate
            if settings.sample_rate and settings.sample_rate > target_caps.max_sample_rate:
                return {
                    "valid": False,
                    "error": f"Sample rate {settings.sample_rate} exceeds maximum for {target_format.value}"
                }
            
            # Validate bit depth
            if settings.bit_depth and settings.bit_depth > target_caps.max_bit_depth:
                return {
                    "valid": False,
                    "error": f"Bit depth {settings.bit_depth} exceeds maximum for {target_format.value}"
                }
            
            # Validate channels
            if settings.channels and settings.channels > target_caps.max_channels:
                return {
                    "valid": False,
                    "error": f"Channel count {settings.channels} exceeds maximum for {target_format.value}"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    async def _analyze_source_audio(
        self,
        voice_content: bytes,
        source_format: AudioFormat
    ) -> Dict[str, Any]:
        """Analyze source audio properties"""
        try:
            # Simulate audio analysis (in real implementation, use librosa/soundfile)
            metadata = {
                "duration": len(voice_content) / (44100 * 2),  # Simplified
                "sample_rate": 44100,
                "bit_depth": 16,
                "channels": 2,
                "file_size": len(voice_content),
                "format": source_format.value,
                "estimated_bitrate": (len(voice_content) * 8) / (len(voice_content) / (44100 * 2)) / 1000,
                "dynamic_range": 45.0,
                "peak_level": -3.2,
                "rms_level": -18.7
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Source audio analysis failed: {str(e)}")
            return {}
    
    def _apply_quality_settings(
        self,
        settings: ConversionSettings,
        source_metadata: Dict[str, Any]
    ) -> ConversionSettings:
        """Apply quality settings based on preset and source"""
        try:
            # Get quality preset
            preset = self.quality_presets.get(settings.quality, {})
            
            # Create new settings with applied presets
            final_settings = ConversionSettings(
                target_format=settings.target_format,
                quality=settings.quality
            )
            
            # Apply preset values if not explicitly set
            final_settings.sample_rate = settings.sample_rate or preset.get("sample_rate", source_metadata.get("sample_rate", 44100))
            final_settings.bit_depth = settings.bit_depth or preset.get("bit_depth", source_metadata.get("bit_depth", 16))
            final_settings.channels = settings.channels or preset.get("channels", source_metadata.get("channels", 2))
            final_settings.compression_level = preset.get("compression_level", settings.compression_level)
            final_settings.normalize_audio = settings.normalize_audio and preset.get("normalize", True)
            
            # Calculate appropriate bit rate for lossy formats
            if settings.target_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG]:
                if not settings.bit_rate:
                    if settings.quality == ConversionQuality.HIGH:
                        final_settings.bit_rate = 320
                    elif settings.quality == ConversionQuality.MEDIUM:
                        final_settings.bit_rate = 192
                    elif settings.quality == ConversionQuality.LOW:
                        final_settings.bit_rate = 128
                    else:
                        final_settings.bit_rate = 64
                else:
                    final_settings.bit_rate = settings.bit_rate
            
            # Copy other settings
            final_settings.remove_silence = settings.remove_silence
            final_settings.apply_eq = settings.apply_eq
            final_settings.preserve_metadata = settings.preserve_metadata
            final_settings.custom_parameters = settings.custom_parameters.copy()
            
            return final_settings
            
        except Exception as e:
            self.logger.error(f"Quality settings application failed: {str(e)}")
            return settings
    
    async def _perform_conversion(
        self,
        voice_content: bytes,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: ConversionSettings
    ) -> bytes:
        """Perform actual audio format conversion"""
        try:
            # This is a simplified simulation of audio conversion
            # In real implementation, use libraries like pydub, ffmpeg-python, or similar
            
            # Simulate conversion process
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Simulate format-specific conversion
            if target_format == AudioFormat.MP3:
                # Simulate MP3 compression
                compression_ratio = 0.1 if settings.quality == ConversionQuality.HIGH else 0.05
                output_size = int(len(voice_content) * compression_ratio)
            elif target_format == AudioFormat.FLAC:
                # Simulate FLAC lossless compression
                output_size = int(len(voice_content) * 0.6)
            elif target_format == AudioFormat.AAC:
                # Simulate AAC compression
                compression_ratio = 0.12 if settings.quality == ConversionQuality.HIGH else 0.08
                output_size = int(len(voice_content) * compression_ratio)
            elif target_format == AudioFormat.OPUS:
                # Simulate OPUS compression
                compression_ratio = 0.08 if settings.quality == ConversionQuality.HIGH else 0.05
                output_size = int(len(voice_content) * compression_ratio)
            else:
                # Default conversion
                output_size = len(voice_content)
            
            # Generate simulated converted audio data
            converted_audio = voice_content[:output_size] if output_size < len(voice_content) else voice_content
            
            # Apply audio processing if requested
            if settings.normalize_audio:
                # Simulate normalization
                pass
            
            if settings.remove_silence:
                # Simulate silence removal
                output_size = int(output_size * 0.95)
                converted_audio = converted_audio[:output_size]
            
            return converted_audio
            
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {str(e)}")
            raise
    
    async def _generate_output_metadata(
        self,
        converted_audio: bytes,
        target_format: AudioFormat,
        settings: ConversionSettings,
        source_metadata: Dict[str, Any]
    ) -> VoiceMetadata:
        """Generate metadata for converted audio"""
        try:
            metadata = VoiceMetadata(
                content_id=f"converted_{datetime.now().timestamp()}",
                creator_id="system",
                duration=len(converted_audio) / (settings.sample_rate * settings.channels * (settings.bit_depth // 8)),
                file_size=len(converted_audio),
                format=target_format.value,
                sample_rate=settings.sample_rate,
                bit_depth=settings.bit_depth,
                channels=settings.channels
            )
            
            # Add conversion metadata
            metadata.technical_metadata = {
                "converted_from": source_metadata.get("format", "unknown"),
                "conversion_quality": settings.quality.value,
                "conversion_timestamp": datetime.now().isoformat(),
                "bit_rate": settings.bit_rate,
                "compression_level": settings.compression_level,
                "audio_processing": {
                    "normalized": settings.normalize_audio,
                    "silence_removed": settings.remove_silence,
                    "eq_applied": settings.apply_eq
                }
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Output metadata generation failed: {str(e)}")
            # Return minimal metadata
            return VoiceMetadata(
                content_id="converted",
                creator_id="system",
                format=target_format.value
            )
    
    def _calculate_size_reduction(self, source_audio: bytes, converted_audio: bytes) -> float:
        """Calculate file size reduction percentage"""
        if len(source_audio) == 0:
            return 0.0
        
        reduction = (len(source_audio) - len(converted_audio)) / len(source_audio)
        return max(0.0, reduction)
    
    def _estimate_quality_loss(
        self,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: ConversionSettings
    ) -> float:
        """Estimate quality loss from conversion"""
        try:
            source_caps = self.format_capabilities.get(source_format)
            target_caps = self.format_capabilities.get(target_format)
            
            if not source_caps or not target_caps:
                return 0.5  # Unknown loss
            
            # Base quality loss from format change
            base_loss = 1.0 - target_caps.quality_retention
            
            # Additional loss from quality settings
            quality_multiplier = {
                ConversionQuality.LOSSLESS: 0.0,
                ConversionQuality.HIGH: 0.1,
                ConversionQuality.MEDIUM: 0.3,
                ConversionQuality.LOW: 0.5,
                ConversionQuality.COMPRESSED: 0.7
            }.get(settings.quality, 0.3)
            
            total_loss = base_loss + (quality_multiplier * 0.3)
            return min(1.0, total_loss)
            
        except Exception as e:
            self.logger.error(f"Quality loss estimation failed: {str(e)}")
            return 0.3  # Conservative estimate
    
    def _generate_warnings(
        self,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: ConversionSettings
    ) -> List[str]:
        """Generate conversion warnings"""
        warnings = []
        
        try:
            # Check for lossy to lossless conversion
            source_caps = self.format_capabilities.get(source_format)
            target_caps = self.format_capabilities.get(target_format)
            
            if (source_caps and target_caps and 
                source_caps.compression_type == CompressionType.LOSSY and
                target_caps.compression_type == CompressionType.LOSSLESS):
                warnings.append("Converting from lossy to lossless format will not improve quality")
            
            # Check for unnecessary high quality settings
            if (settings.quality == ConversionQuality.LOSSLESS and 
                target_format in [AudioFormat.MP3, AudioFormat.AAC]):
                warnings.append("Lossless quality setting not applicable for lossy format")
            
            # Check for extreme compression
            if settings.quality == ConversionQuality.COMPRESSED:
                warnings.append("High compression may result in significant quality loss")
            
            # Check for sample rate downsampling
            if settings.sample_rate and settings.sample_rate < 44100:
                warnings.append("Low sample rate may affect audio quality")
            
        except Exception as e:
            self.logger.error(f"Warning generation failed: {str(e)}")
        
        return warnings
    
    async def convert_for_platform(
        self,
        voice_content: bytes,
        source_format: AudioFormat,
        platform: PlatformFormat,
        optimization_level: ConversionQuality = ConversionQuality.HIGH
    ) -> ConversionResult:
        """Convert audio optimized for specific platform"""
        try:
            # Get platform requirements
            platform_req = self.platform_requirements.get(platform)
            if not platform_req:
                return ConversionResult(
                    success=False,
                    error_message=f"Unknown platform: {platform.value}"
                )
            
            # Select best format for platform
            preferred_formats = platform_req["preferred_formats"]
            target_format = preferred_formats[0]  # Use first preferred format
            
            # Create platform-optimized settings
            settings = ConversionSettings(
                target_format=target_format,
                quality=optimization_level,
                sample_rate=platform_req["sample_rate"],
                bit_rate=platform_req["recommended_bitrate"],
                channels=platform_req["channels"]
            )
            
            # Perform conversion
            result = await self.convert_format(voice_content, source_format, target_format, settings)
            
            # Validate file size constraints
            if result.success and result.converted_audio:
                max_size = platform_req["max_file_size"]
                if len(result.converted_audio) > max_size:
                    result.warnings.append(f"Output file size exceeds platform limit of {max_size} bytes")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Platform conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    def get_optimal_format(
        self,
        use_case: str,
        file_size_priority: bool = False,
        quality_priority: bool = True
    ) -> AudioFormat:
        """Get optimal format for specific use case"""
        try:
            if use_case.lower() == "streaming":
                return AudioFormat.AAC if quality_priority else AudioFormat.MP3
            elif use_case.lower() == "archival":
                return AudioFormat.FLAC
            elif use_case.lower() == "podcast":
                return AudioFormat.MP3
            elif use_case.lower() == "voice_assistant":
                return AudioFormat.OPUS
            elif use_case.lower() == "social_media":
                return AudioFormat.AAC if quality_priority else AudioFormat.MP3
            elif use_case.lower() == "audiobook":
                return AudioFormat.MP3
            else:
                # Default recommendation
                if file_size_priority:
                    return AudioFormat.OPUS
                elif quality_priority:
                    return AudioFormat.FLAC
                else:
                    return AudioFormat.MP3
                    
        except Exception as e:
            self.logger.error(f"Optimal format selection failed: {str(e)}")
            return AudioFormat.MP3  # Safe default
    
    async def batch_convert(
        self,
        conversion_jobs: List[Tuple[bytes, AudioFormat, AudioFormat, Optional[ConversionSettings]]]
    ) -> List[ConversionResult]:
        """Perform batch conversion of multiple audio files"""
        results = []
        
        for voice_content, source_format, target_format, settings in conversion_jobs:
            try:
                result = await self.convert_format(voice_content, source_format, target_format, settings)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch conversion item failed: {str(e)}")
                results.append(ConversionResult(
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def get_format_info(self, format: AudioFormat) -> Optional[FormatCapabilities]:
        """Get information about specific audio format"""
        return self.format_capabilities.get(format)
    
    def get_platform_requirements(self, platform: PlatformFormat) -> Optional[Dict[str, Any]]:
        """Get requirements for specific platform"""
        return self.platform_requirements.get(platform)


# Export classes and enums
__all__ = [
    'VoiceFormatConverter',
    'AudioFormat',
    'ConversionQuality',
    'CompressionType',
    'PlatformFormat',
    'ConversionSettings',
    'FormatCapabilities',
    'ConversionResult'
]