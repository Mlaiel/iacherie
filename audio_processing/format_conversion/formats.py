"""Format Registry and Support System - Professional Audio Format Management

Advanced format detection, validation, and support management for audio format conversion.
Provides comprehensive format compatibility and optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import subprocess
import tempfile
import json

# Audio format detection libraries
import mutagen
import soundfile as sf
import librosa

from ..core.config import AudioConfig
from ..core.exceptions import UnsupportedFormatError, FormatError
from .models import FormatSpecification, QualityProfile
from .config import FormatConfig

logger = logging.getLogger(__name__)


class FormatCategory(Enum):
    """
Audio format categories"""

    LOSSLESS = "lossless"
    LOSSY = "lossy"
    UNCOMPRESSED = "uncompressed"
    PROFESSIONAL = "professional"
    STREAMING = "streaming"
    ARCHIVAL = "archival"


class CompressionType(Enum):
    """Audio compression types"""

    NONE = "none"
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    HYBRID = "hybrid"


@dataclass
class FormatCapabilities:
    """Format capability specification"""
    max_sample_rate: int
    max_bit_depth: int
    max_channels: int
    supports_metadata: bool
    supports_cover_art: bool
    supports_variable_bitrate: bool
    supports_gapless: bool
    streaming_friendly: bool
    professional_grade: bool
    
    # Advanced capabilities
    supports_multichannel: bool = False
    supports_high_resolution: bool = False
    supports_dsd: bool = False
    supports_spatial_audio: bool = False
    
    # Compression features
    compression_efficiency: float = 1.0  # Higher is better
    quality_scalability: float = 1.0     # Range of quality options
    
    # Platform support
    platform_support: Dict[str, bool] = field(default_factory=dict)


@dataclass
class FormatProfile:
    """
Complete format profile"""
    name: str
    extension: str
    mime_type: str
    category: FormatCategory
    compression_type: CompressionType
    capabilities: FormatCapabilities
    
    # Quality presets
    quality_presets: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Encoder/decoder information
    encoder_options: Dict[str, Any] = field(default_factory=dict)
    decoder_requirements: List[str] = field(default_factory=list)
    
    # Compatibility information
    compatibility_issues: List[str] = field(default_factory=list)
    recommended_use_cases: List[str] = field(default_factory=list)


class SupportedFormats:
    """
    Registry of Supported Audio Formats
    
    Comprehensive catalog of audio formats with detailed specifications,
    capabilities, and optimization parameters.
    """
    
    def __init__(self):
        """
Initialize supported formats registry"""
        self.formats = self._initialize_format_registry()
        self.format_aliases = self._initialize_aliases()
        self.conversion_matrix = self._initialize_conversion_matrix()
        
    def _initialize_format_registry(self) -> Dict[str, FormatProfile]:
        """
Initialize comprehensive format registry"""
        formats = {}
        
        # WAV - Uncompressed PCM
        formats['wav'] = FormatProfile(
            name="Waveform Audio File",
            extension="wav",
            mime_type="audio/wav",
            category=FormatCategory.UNCOMPRESSED,
            compression_type=CompressionType.NONE,
            capabilities=FormatCapabilities(
                max_sample_rate=192000,
                max_bit_depth=32,
                max_channels=32,
                supports_metadata=True,
                supports_cover_art=False,
                supports_variable_bitrate=False,
                supports_gapless=True,
                streaming_friendly=False,
                professional_grade=True,
                supports_multichannel=True,
                supports_high_resolution=True,
                platform_support={
                    'windows': True,
                    'macos': True,
                    'linux': True,
                    'ios': True,
                    'android': True,
                    'web': True
                }
            ),
            quality_presets={
                'cd': {'sample_rate': 44100, 'bit_depth': 16},
                'professional': {'sample_rate': 48000, 'bit_depth': 24},
                'high_resolution': {'sample_rate': 96000, 'bit_depth': 24},
                'archival': {'sample_rate': 192000, 'bit_depth': 32}
            },
            recommended_use_cases=['mastering', 'archival', 'professional_editing']
        )
        
        # FLAC - Free Lossless Audio Codec
        formats['flac'] = FormatProfile(
            name="Free Lossless Audio Codec",
            extension="flac",
            mime_type="audio/flac",
            category=FormatCategory.LOSSLESS,
            compression_type=CompressionType.LOSSLESS,
            capabilities=FormatCapabilities(
                max_sample_rate=655350,
                max_bit_depth=32,
                max_channels=8,
                supports_metadata=True,
                supports_cover_art=True,
                supports_variable_bitrate=False,
                supports_gapless=True,
                streaming_friendly=True,
                professional_grade=True,
                supports_multichannel=True,
                supports_high_resolution=True,
                compression_efficiency=0.6,
                platform_support={
                    'windows': True,
                    'macos': True,
                    'linux': True,
                    'ios': False,
                    'android': True,
                    'web': True
                }
            ),
            quality_presets={
                'fast': {'compression_level': 0},
                'standard': {'compression_level': 5},
                'best': {'compression_level': 8}
            },
            recommended_use_cases=['archival', 'high_quality_streaming', 'audiophile']
        )
        
        # MP3 - MPEG Audio Layer III
        formats['mp3'] = FormatProfile(
            name="MPEG Audio Layer III",
            extension="mp3",
            mime_type="audio/mpeg",
            category=FormatCategory.LOSSY,
            compression_type=CompressionType.LOSSY,
            capabilities=FormatCapabilities(
                max_sample_rate=48000,
                max_bit_depth=16,
                max_channels=2,
                supports_metadata=True,
                supports_cover_art=True,
                supports_variable_bitrate=True,
                supports_gapless=False,
                streaming_friendly=True,
                professional_grade=False,
                compression_efficiency=0.1,
                quality_scalability=0.8,
                platform_support={
                    'windows': True,
                    'macos': True,
                    'linux': True,
                    'ios': True,
                    'android': True,
                    'web': True
                }
            ),
            quality_presets={
                'low': {'bitrate': 128, 'mode': 'cbr'},
                'standard': {'bitrate': 192, 'mode': 'vbr', 'quality': 4},
                'high': {'bitrate': 256, 'mode': 'vbr', 'quality': 2},
                'extreme': {'bitrate': 320, 'mode': 'cbr'}
            },
            recommended_use_cases=['streaming', 'portable_devices', 'web_distribution']
        )
        
        # AAC - Advanced Audio Coding
        formats['aac'] = FormatProfile(
            name="Advanced Audio Coding",
            extension="aac",
            mime_type="audio/aac",
            category=FormatCategory.LOSSY,
            compression_type=CompressionType.LOSSY,
            capabilities=FormatCapabilities(
                max_sample_rate=96000,
                max_bit_depth=24,
                max_channels=48,
                supports_metadata=True,
                supports_cover_art=True,
                supports_variable_bitrate=True,
                supports_gapless=True,
                streaming_friendly=True,
                professional_grade=True,
                supports_multichannel=True,
                supports_spatial_audio=True,
                compression_efficiency=0.15,
                quality_scalability=0.9,
                platform_support={
                    'windows': True,
                    'macos': True,
                    'linux': True,
                    'ios': True,
                    'android': True,
                    'web': True
                }
            ),
            quality_presets={
                'he_aac': {'profile': 'he-aac', 'bitrate': 64},
                'lc': {'profile': 'lc', 'bitrate': 128},
                'high': {'profile': 'lc', 'bitrate': 256},
                'professional': {'profile': 'lc', 'bitrate': 320}
            },
            recommended_use_cases=['streaming', 'broadcast', 'mobile_apps', 'podcasts']
        )
        
        # OGG Vorbis - Open source lossy codec
        formats['ogg'] = FormatProfile(
            name="Ogg Vorbis",
            extension="ogg",
            mime_type="audio/ogg",
            category=FormatCategory.LOSSY,
            compression_type=CompressionType.LOSSY,
            capabilities=FormatCapabilities(
                max_sample_rate=192000,
                max_bit_depth=24,
                max_channels=255,
                supports_metadata=True,
                supports_cover_art=True,
                supports_variable_bitrate=True,
                supports_gapless=True,
                streaming_friendly=True,
                professional_grade=False,
                supports_multichannel=True,
                compression_efficiency=0.12,
                quality_scalability=1.0,
                platform_support={
                    'windows': False,
                    'macos': False,
                    'linux': True,
                    'ios': False,
                    'android': True,
                    'web': True
                }
            ),
            quality_presets={
                'low': {'quality': 2},
                'standard': {'quality': 5},
                'high': {'quality': 8},
                'extreme': {'quality': 10}
            },
            recommended_use_cases=['web_streaming', 'open_source_projects', 'gaming']
        )
        
        # M4A - MPEG-4 Audio
        formats['m4a'] = FormatProfile(
            name="MPEG-4 Audio",
            extension="m4a",
            mime_type="audio/mp4",
            category=FormatCategory.LOSSY,
            compression_type=CompressionType.LOSSY,
            capabilities=FormatCapabilities(
                max_sample_rate=96000,
                max_bit_depth=24,
                max_channels=48,
                supports_metadata=True,
                supports_cover_art=True,
                supports_variable_bitrate=True,
                supports_gapless=True,
                streaming_friendly=True,
                professional_grade=True,
                supports_multichannel=True,
                compression_efficiency=0.15,
                platform_support={
                    'windows': True,
                    'macos': True,
                    'linux': True,
                    'ios': True,
                    'android': True,
                    'web': True
                }
            ),
            recommended_use_cases=['itunes', 'apple_ecosystem', 'professional_distribution']
        )
        
        # AIFF - Audio Interchange File Format
        formats['aiff'] = FormatProfile(
            name="Audio Interchange File Format",
            extension="aiff",
            mime_type="audio/aiff",
            category=FormatCategory.UNCOMPRESSED,
            compression_type=CompressionType.NONE,
            capabilities=FormatCapabilities(
                max_sample_rate=192000,
                max_bit_depth=32,
                max_channels=32,
                supports_metadata=True,
                supports_cover_art=False,
                supports_variable_bitrate=False,
                supports_gapless=True,
                streaming_friendly=False,
                professional_grade=True,
                supports_multichannel=True,
                supports_high_resolution=True,
                platform_support={
                    'windows': False,
                    'macos': True,
                    'linux': True,
                    'ios': True,
                    'android': False,
                    'web': False
                }
            ),
            recommended_use_cases=['mac_professional', 'pro_tools', 'mastering']
        )
        
        return formats
    
    def _initialize_aliases(self) -> Dict[str, str]:
        """Initialize format aliases and alternative extensions"""
        return {
            'wave': 'wav',
            'oga': 'ogg',
            'mp4': 'm4a',
            'aif': 'aiff',
            'aifc': 'aiff'
        }
    
    def _initialize_conversion_matrix(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """
Initialize format conversion compatibility matrix"""
        matrix = {}
        
        # High-quality conversions (minimal loss)
        high_quality_pairs = [
            ('wav', 'flac'), ('flac', 'wav'),
            ('aiff', 'wav'), ('wav', 'aiff'),
            ('aiff', 'flac'), ('flac', 'aiff')
        ]
        
        for source, target in high_quality_pairs:
            matrix[(source, target)] = {
                'quality_loss': 0.0,
                'recommended': True,
                'processing_complexity': 'low',
                'special_considerations': []
            }
        
        # Good quality conversions (some loss acceptable)
        good_quality_pairs = [
            ('wav', 'aac'), ('flac', 'aac'),
            ('wav', 'm4a'), ('flac', 'm4a'),
            ('aiff', 'aac'), ('aiff', 'm4a')
        ]
        
        for source, target in good_quality_pairs:
            matrix[(source, target)] = {
                'quality_loss': 0.1,
                'recommended': True,
                'processing_complexity': 'medium',
                'special_considerations': ['bitrate_optimization']
            }
        
        # Standard conversions (acceptable loss)
        standard_pairs = [
            ('wav', 'mp3'), ('flac', 'mp3'),
            ('aiff', 'mp3'), ('wav', 'ogg'),
            ('flac', 'ogg'), ('aiff', 'ogg')
        ]
        
        for source, target in standard_pairs:
            matrix[(source, target)] = {
                'quality_loss': 0.2,
                'recommended': True,
                'processing_complexity': 'medium',
                'special_considerations': ['quality_preset_selection']
            }
        
        return matrix
    
    def get_format_profile(self, format_name: str) -> Optional[FormatProfile]:
        """
Get detailed format profile"""
        format_name = format_name.lower().lstrip('.')
        
        # Check aliases
        if format_name in self.format_aliases:
            format_name = self.format_aliases[format_name]
        
        return self.formats.get(format_name)
    
    def is_format_supported(self, format_name: str) -> bool:
        """
Check if format is supported"""
        return self.get_format_profile(format_name) is not None
    
    def get_supported_formats(self, category: Optional[FormatCategory] = None) -> List[str]:
        """
Get list of supported formats, optionally filtered by category"""
        if category is None:
            return list(self.formats.keys())
        
        return [name for name, profile in self.formats.items() 
                if profile.category == category]
    
    def get_conversion_info(self, source_format: str, target_format: str) -> Optional[Dict[str, Any]]:
        """
Get conversion information between two formats"""
        source = source_format.lower().lstrip('.')
        target = target_format.lower().lstrip('.')
        
        # Check aliases
        if source in self.format_aliases:
            source = self.format_aliases[source]
        if target in self.format_aliases:
            target = self.format_aliases[target]
        
        return self.conversion_matrix.get((source, target))
    
    def recommend_format(self, use_case: str, constraints: Optional[Dict[str, Any]] = None) -> List[str]:
        """
Recommend formats for specific use case"""
        constraints = constraints or {}
        
        use_case_recommendations = {
            'streaming': ['aac', 'mp3', 'ogg'],
            'archival': ['flac', 'wav', 'aiff'],
            'professional': ['wav', 'aiff', 'flac'],
            'broadcast': ['aac', 'mp3'],
            'mobile': ['aac', 'mp3'],
            'web': ['mp3', 'aac', 'ogg'],
            'podcast': ['mp3', 'aac'],
            'mastering': ['wav', 'aiff'],
            'distribution': ['flac', 'aac', 'mp3']
        }
        
        base_recommendations = use_case_recommendations.get(use_case.lower(), ['mp3'])
        
        # Apply constraints filtering
        filtered_recommendations = []
        
        for format_name in base_recommendations:
            profile = self.get_format_profile(format_name)
            if not profile:
                continue
            
            # Check file size constraint
            if constraints.get('max_file_size') and profile.compression_type == CompressionType.NONE:
                continue
            
            # Check platform support
            required_platforms = constraints.get('platforms', [])
            if required_platforms:
                if not all(profile.capabilities.platform_support.get(platform, False) 
                          for platform in required_platforms):
                    continue
            
            # Check quality requirements
            if constraints.get('require_lossless') and profile.compression_type == CompressionType.LOSSY:
                continue
            
            filtered_recommendations.append(format_name)
        
        return filtered_recommendations or base_recommendations


class FormatRegistry:
    """
    Professional Format Registry Manager
    
    Central registry for audio format management with advanced detection,
    validation, and compatibility checking capabilities.
    """
    
    def __init__(self, config: Optional[FormatConfig] = None):
        """
Initialize format registry"""
        self.config = config or FormatConfig()
        self.supported_formats = SupportedFormats()
        self.detection_cache: Dict[str, str] = {}
        self.validation_cache: Dict[str, bool] = {}
        
        # Initialize external tool detection
        self.external_tools = self._detect_external_tools()
        
    async def detect_format(self, file_path: Path) -> Optional[str]:
        """
        Detect audio format from file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Detected format name or None
        """
        file_str = str(file_path)
        
        # Check cache first
        if file_str in self.detection_cache:
            return self.detection_cache[file_str]
        
        detected_format = None
        
        try:
            # Method 1: Extension-based detection
            extension_format = self._detect_by_extension(file_path)
            
            # Method 2: Content-based detection using mutagen
            content_format = await self._detect_by_content(file_path)
            
            # Method 3: Magic number detection
            magic_format = await self._detect_by_magic_number(file_path)
            
            # Prioritize content detection over extension
            if content_format and self.supported_formats.is_format_supported(content_format):
                detected_format = content_format
            elif magic_format and self.supported_formats.is_format_supported(magic_format):
                detected_format = magic_format
            elif extension_format and self.supported_formats.is_format_supported(extension_format):
                detected_format = extension_format
            
            # Cache result
            if detected_format:
                self.detection_cache[file_str] = detected_format
            
            return detected_format
            
        except Exception as e:
            logger.warning(f"Format detection failed for {file_path}: {e}")
            return None
    
    async def validate_format_compatibility(self, 
                                          source_format: str, 
                                          target_format: str) -> Dict[str, Any]:
        """
        Validate format conversion compatibility
        
        Args:
            source_format: Source audio format
            target_format: Target audio format
            
        Returns:
            Compatibility analysis
        """
        compatibility = {
            'compatible': False,
            'quality_loss': 1.0,
            'recommended': False,
            'warnings': [],
            'requirements': [],
            'optimizations': []
        }
        
        try:
            # Get format profiles
            source_profile = self.supported_formats.get_format_profile(source_format)
            target_profile = self.supported_formats.get_format_profile(target_format)
            
            if not source_profile:
                compatibility['warnings'].append(f"Unsupported source format: {source_format}")
                return compatibility
            
            if not target_profile:
                compatibility['warnings'].append(f"Unsupported target format: {target_format}")
                return compatibility
            
            compatibility['compatible'] = True
            
            # Get conversion info
            conversion_info = self.supported_formats.get_conversion_info(source_format, target_format)
            
            if conversion_info:
                compatibility.update(conversion_info)
            else:
                # Calculate compatibility heuristically
                await self._calculate_heuristic_compatibility(
                    source_profile, target_profile, compatibility
                )
            
            # Add specific warnings and requirements
            await self._analyze_conversion_requirements(
                source_profile, target_profile, compatibility
            )
            
            return compatibility
            
        except Exception as e:
            logger.error(f"Compatibility validation failed: {e}")
            compatibility['warnings'].append(f"Validation error: {e}")
            return compatibility
    
    async def get_optimal_settings(self, 
                                 source_format: str, 
                                 target_format: str,
                                 quality_profile: Optional[QualityProfile] = None) -> Dict[str, Any]:
        """
        Get optimal conversion settings for format pair
        
        Args:
            source_format: Source audio format
            target_format: Target audio format
            quality_profile: Target quality profile
            
        Returns:
            Optimal conversion settings
        """
        settings = {
            'sample_rate': 44100,
            'bit_depth': 16,
            'bitrate': 192,
            'quality': 'standard',
            'special_processing': []
        }
        
        try:
            target_profile = self.supported_formats.get_format_profile(target_format)
            if not target_profile:
                return settings
            
            # Apply quality profile if specified
            if quality_profile:
                profile_settings = await self._get_quality_profile_settings(
                    target_profile, quality_profile
                )
                settings.update(profile_settings)
            
            # Apply format-specific optimizations
            format_optimizations = await self._get_format_optimizations(
                source_format, target_format
            )
            settings.update(format_optimizations)
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to get optimal settings: {e}")
            return settings
    
    def get_format_capabilities(self, format_name: str) -> Optional[FormatCapabilities]:
        """Get format capabilities"""
        profile = self.supported_formats.get_format_profile(format_name)
        return profile.capabilities if profile else None
    
    def is_lossless_format(self, format_name: str) -> bool:
        """
Check if format is lossless"""
        profile = self.supported_formats.get_format_profile(format_name)
        if not profile:
            return False
        
        return profile.compression_type in [CompressionType.NONE, CompressionType.LOSSLESS]
    
    def is_high_resolution_capable(self, format_name: str) -> bool:
        """
Check if format supports high resolution audio"""
        capabilities = self.get_format_capabilities(format_name)
        if not capabilities:
            return False
        
        return (capabilities.max_sample_rate >= 96000 and 
                capabilities.max_bit_depth >= 24 and
                capabilities.supports_high_resolution)
    
    def get_streaming_formats(self) -> List[str]:
        """
Get formats suitable for streaming"""
        return self.supported_formats.get_supported_formats(FormatCategory.STREAMING) + \
               [fmt for fmt, profile in self.supported_formats.formats.items() 
                if profile.capabilities.streaming_friendly]
    
    def get_professional_formats(self) -> List[str]:
        """
Get formats suitable for professional use"""
        return [fmt for fmt, profile in self.supported_formats.formats.items() 
                if profile.capabilities.professional_grade]
    
    # Private methods
    
    def _detect_by_extension(self, file_path: Path) -> Optional[str]:
        """
Detect format by file extension"""
        extension = file_path.suffix.lower().lstrip('.')
        
        # Check direct match
        if self.supported_formats.is_format_supported(extension):
            return extension
        
        # Check aliases
        if extension in self.supported_formats.format_aliases:
            return self.supported_formats.format_aliases[extension]
        
        return None
    
    async def _detect_by_content(self, file_path: Path) -> Optional[str]:
        """
Detect format by analyzing file content"""
        try:
            audio_file = mutagen.File(str(file_path))
            if not audio_file:
                return None
            
            # Map mutagen types to format names
            type_mapping = {
                'MP3': 'mp3',
                'FLAC': 'flac',
                'MP4': 'm4a',
                'OggVorbis': 'ogg',
                'WAVE': 'wav',
                'AIFF': 'aiff'
            }
            
            file_type = type(audio_file).__name__
            return type_mapping.get(file_type)
            
        except Exception:
            return None
    
    async def _detect_by_magic_number(self, file_path: Path) -> Optional[str]:
        """
Detect format by magic number (file signature)"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
            
            # Magic number signatures
            magic_signatures = {
                b'RIFF': 'wav',
                b'fLaC': 'flac',
                b'OggS': 'ogg',
                b'FORM': 'aiff',
                b'ID3': 'mp3',
                b'\xff\xfb': 'mp3',
                b'\xff\xf3': 'mp3',
                b'\xff\xf2': 'mp3'
            }
            
            for signature, format_name in magic_signatures.items():
                if header.startswith(signature):
                    return format_name
            
            return None
            
        except Exception:
            return None
    
    def _detect_external_tools(self) -> Dict[str, bool]:
        try:
            logger.info(f"Executing _detect_external_tools")
            
            # Implementation for _detect_external_tools
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_detect_external_tools completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_detect_external_tools failed: {e}")
            raise
    async def _calculate_heuristic_compatibility(self,
                                               source_profile: FormatProfile,
                                               target_profile: FormatProfile,
                                               compatibility: Dict[str, Any]):
        """
Calculate compatibility heuristically"""
        # Quality loss estimation
        if (source_profile.compression_type == CompressionType.NONE and 
            target_profile.compression_type == CompressionType.LOSSY):
            compatibility['quality_loss'] = 0.3
        elif (source_profile.compression_type == CompressionType.LOSSLESS and 
              target_profile.compression_type == CompressionType.LOSSY):
            compatibility['quality_loss'] = 0.2
        elif (source_profile.compression_type == CompressionType.LOSSY and 
              target_profile.compression_type == CompressionType.LOSSY):
            compatibility['quality_loss'] = 0.4
        else:
            compatibility['quality_loss'] = 0.0
        
        # Recommendation based on quality loss
        compatibility['recommended'] = compatibility['quality_loss'] < 0.25
    
    async def _analyze_conversion_requirements(self,
                                             source_profile: FormatProfile,
                                             target_profile: FormatProfile,
                                             compatibility: Dict[str, Any]):
        """
Analyze specific conversion requirements"""
        # Check sample rate compatibility
        if (hasattr(source_profile, 'max_sample_rate') and 
            target_profile.capabilities.max_sample_rate < source_profile.capabilities.max_sample_rate):
            compatibility['warnings'].append(
                f"Target format may not support high sample rates (max: {target_profile.capabilities.max_sample_rate})"
            )
        
        # Check bit depth compatibility
        if target_profile.capabilities.max_bit_depth < source_profile.capabilities.max_bit_depth:
            compatibility['warnings'].append(
                f"Target format has lower bit depth limit (max: {target_profile.capabilities.max_bit_depth})"
            )
        
        # Check multichannel support
        if (source_profile.capabilities.supports_multichannel and 
            not target_profile.capabilities.supports_multichannel):
            compatibility['warnings'].append("Target format may not support multichannel audio")
        
        # Check metadata support
        if (source_profile.capabilities.supports_metadata and 
            not target_profile.capabilities.supports_metadata):
            compatibility['warnings'].append("Metadata may be lost in conversion")
        
        # Requirements for specific formats
        if target_profile.decoder_requirements:
            compatibility['requirements'].extend(target_profile.decoder_requirements)
    
    async def _get_quality_profile_settings(self,
                                          target_profile: FormatProfile,
                                          quality_profile: QualityProfile) -> Dict[str, Any]:
        """Get settings based on quality profile"""
        settings = {}
        
        # Map quality profile to format presets
        if quality_profile.name.lower() in target_profile.quality_presets:
            preset = target_profile.quality_presets[quality_profile.name.lower()]
            settings.update(preset)
        
        return settings
    
    async def _get_format_optimizations(self,
                                      source_format: str,
                                      target_format: str) -> Dict[str, Any]:
        """
Get format-specific optimizations"""
        optimizations = {}
        
        # Source format specific optimizations
        if source_format == 'wav' and target_format in ['mp3', 'aac', 'ogg']:
            optimizations['pre_emphasis'] = False
            optimizations['normalize'] = True
        
        # Target format specific optimizations
        if target_format == 'mp3':
            optimizations.update({
                'joint_stereo': True,
                'reservoir': True,
                'quality_optimization': 'vbr'
            })
        elif target_format == 'aac':
            optimizations.update({
                'profile': 'lc',
                'bandwidth': 'auto',
                'tns': True
            })
        elif target_format == 'flac':
            optimizations.update({
                'compression_level': 5,
                'verify': True,
                'exhaustive_model_search': False
            })
        
        return optimizations


class FormatValidator:
    """
    Audio Format Validator
    
    Comprehensive validation system for audio format integrity,
    compliance, and quality assurance.
    """
    
    def __init__(self, registry: FormatRegistry):
        """
Initialize format validator"""
        self.registry = registry
        
    async def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate audio file integrity and compliance
        
        Args:
            file_path: Path to audio file to validate
            
        Returns:
            Validation report
        """
        validation_report = {
            'valid': False,
            'format': None,
            'errors': [],
            'warnings': [],
            'technical_info': {},
            'compliance_info': {}
        }
        
        try:
            # Detect format
            detected_format = await self.registry.detect_format(file_path)
            if not detected_format:
                validation_report['errors'].append("Could not detect audio format")
                return validation_report
            
            validation_report['format'] = detected_format
            
            # Validate file integrity
            integrity_check = await self._validate_file_integrity(file_path, detected_format)
            validation_report.update(integrity_check)
            
            # Extract and validate technical specifications
            tech_validation = await self._validate_technical_specs(file_path, detected_format)
            validation_report['technical_info'] = tech_validation
            
            # Check format compliance
            compliance_check = await self._validate_format_compliance(
                file_path, detected_format
            )
            validation_report['compliance_info'] = compliance_check
            
            # Overall validation status
            validation_report['valid'] = (
                len(validation_report['errors']) == 0 and
                integrity_check.get('readable', False)
            )
            
            return validation_report
            
        except Exception as e:
            validation_report['errors'].append(f"Validation failed: {e}")
            return validation_report
    
    async def _validate_file_integrity(self, 
                                     file_path: Path, 
                                     format_name: str) -> Dict[str, Any]:
        """Validate file integrity"""
        integrity = {
            'readable': False,
            'complete': False,
            'corrupted': False
        }
        
        try:
            # Try to read with multiple libraries
            read_attempts = [
                self._try_mutagen_read,
                self._try_soundfile_read,
                self._try_librosa_read
            ]
            
            successful_reads = 0
            for attempt in read_attempts:
                try:
                    result = await attempt(file_path)
                    if result:
                        successful_reads += 1
                except:
                    pass
            
            integrity['readable'] = successful_reads > 0
            integrity['complete'] = successful_reads >= 2
            integrity['corrupted'] = successful_reads == 0
            
            return integrity
            
        except Exception as e:
            logger.error(f"Integrity validation failed: {e}")
            return integrity
    
    async def _validate_technical_specs(self, 
                                       file_path: Path, 
                                       format_name: str) -> Dict[str, Any]:
        """Validate technical specifications"""
        try:
            # Load file info
            audio_file = mutagen.File(str(file_path))
            if not audio_file or not hasattr(audio_file, 'info'):
                return {}
            
            info = audio_file.info
            format_profile = self.registry.supported_formats.get_format_profile(format_name)
            
            specs = {
                'sample_rate': getattr(info, 'sample_rate', None),
                'bitrate': getattr(info, 'bitrate', None),
                'channels': getattr(info, 'channels', None),
                'duration': getattr(info, 'length', None),
                'bits_per_sample': getattr(info, 'bits_per_sample', None)
            }
            
            # Validate against format capabilities
            if format_profile:
                caps = format_profile.capabilities
                
                if specs['sample_rate'] and specs['sample_rate'] > caps.max_sample_rate:
                    specs['sample_rate_warning'] = f"Exceeds max sample rate: {caps.max_sample_rate}"
                
                if specs['channels'] and specs['channels'] > caps.max_channels:
                    specs['channels_warning'] = f"Exceeds max channels: {caps.max_channels}"
                
                if specs['bits_per_sample'] and specs['bits_per_sample'] > caps.max_bit_depth:
                    specs['bit_depth_warning'] = f"Exceeds max bit depth: {caps.max_bit_depth}"
            
            return specs
            
        except Exception as e:
            logger.error(f"Technical specs validation failed: {e}")
            return {}
    
    async def _validate_format_compliance(self, 
                                        file_path: Path, 
                                        format_name: str) -> Dict[str, Any]:
        """Validate format compliance"""
        compliance = {
            'standard_compliant': True,
            'profile_info': {},
            'compatibility_issues': []
        }
        
        try:
            format_profile = self.registry.supported_formats.get_format_profile(format_name)
            if format_profile and format_profile.compatibility_issues:
                compliance['compatibility_issues'] = format_profile.compatibility_issues
            
            return compliance
            
        except Exception as e:
            logger.error(f"Compliance validation failed: {e}")
            return compliance
    
    async def _try_mutagen_read(self, file_path: Path) -> bool:
        """Try reading with mutagen"""
        audio_file = mutagen.File(str(file_path))
        return audio_file is not None
    
    async def _try_soundfile_read(self, file_path: Path) -> bool:
        """
Try reading with soundfile"""
        info = sf.info(str(file_path))
        return info.frames > 0
    
    async def _try_librosa_read(self, file_path: Path) -> bool:
        """
Try reading with librosa"""
        y, sr = librosa.load(str(file_path), duration=1.0)  # Load 1 second
        return len(y) > 0


# Export main classes
__all__ = [
    'FormatRegistry',
    'FormatValidator',
    'SupportedFormats',
    'FormatProfile',
    'FormatCapabilities',
    'FormatCategory',
    'CompressionType'
]
