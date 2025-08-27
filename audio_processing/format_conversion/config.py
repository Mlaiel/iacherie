"""
Configuration - Professional Audio Format Conversion Configuration

Centralized configuration management for audio format conversion operations.
Provides format-specific settings, quality presets, and system configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from .models import AudioFormat, QualityLevel

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing mode for audio conversion"""
    SINGLE_THREADED = "single"
    MULTI_THREADED = "multi"
    PARALLEL_BATCH = "batch"
    REAL_TIME = "realtime"


class CompressionMode(Enum):
    """Compression mode for lossy formats"""
    CBR = "constant_bitrate"      # Constant Bitrate
    VBR = "variable_bitrate"      # Variable Bitrate
    ABR = "average_bitrate"       # Average Bitrate
    CVBR = "constrained_variable" # Constrained Variable Bitrate


@dataclass
class FormatProfile:
    """
    Format-specific configuration profile
    
    Contains all settings and constraints for a specific audio format
    including quality presets, technical limitations, and optimization parameters.
    """
    format: AudioFormat
    supported_sample_rates: List[int]
    supported_channels: List[int]
    supported_bit_depths: List[int]
    max_bitrate: Optional[int] = None
    min_bitrate: Optional[int] = None
    default_bitrate: Optional[int] = None
    supports_lossless: bool = False
    supports_metadata: bool = True
    supports_multichannel: bool = True
    compression_levels: List[int] = field(default_factory=list)
    quality_presets: Dict[QualityLevel, Dict[str, Any]] = field(default_factory=dict)
    format_specific_options: Dict[str, Any] = field(default_factory=dict)
    
    def get_quality_preset(self, quality: QualityLevel) -> Dict[str, Any]:
        """Get quality preset for specified level"""
        return self.quality_presets.get(quality, {})
    
    def validate_parameters(self, sample_rate: int, channels: int, 
                          bit_depth: Optional[int] = None) -> List[str]:
        """Validate format parameters and return issues"""
        issues = []
        
        if sample_rate not in self.supported_sample_rates:
            issues.append(f"Sample rate {sample_rate} not supported for {self.format.value}")
        
        if channels not in self.supported_channels:
            issues.append(f"Channel count {channels} not supported for {self.format.value}")
        
        if bit_depth and bit_depth not in self.supported_bit_depths:
            issues.append(f"Bit depth {bit_depth} not supported for {self.format.value}")
        
        return issues


@dataclass
class QualityPreset:
    """
    Quality preset configuration
    
    Defines parameter sets for different quality levels across all formats.
    """
    name: str
    description: str
    target_quality: float  # 0.0-1.0
    bitrate_multiplier: float
    processing_options: Dict[str, Any]
    format_overrides: Dict[AudioFormat, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ConversionConfig:
    """
    Main conversion configuration
    
    Central configuration object containing all settings for audio format conversion
    operations including format profiles, quality presets, and system parameters.
    """
    # Temporary file settings
    temp_directory: Optional[Path] = None
    clean_temp_files: bool = True
    temp_file_prefix: str = "audioconv_"
    
    # Processing settings
    processing_mode: ProcessingMode = ProcessingMode.MULTI_THREADED
    max_worker_threads: int = 4
    chunk_size_seconds: float = 30.0
    memory_limit_mb: int = 1024
    
    # Quality settings
    default_quality_level: QualityLevel = QualityLevel.HIGH
    enable_quality_analysis: bool = True
    quality_threshold: float = 0.85
    
    # Metadata settings
    preserve_metadata: bool = True
    copy_cover_art: bool = True
    optimize_cover_art: bool = True
    max_cover_art_size: int = 1024 * 1024  # 1MB
    
    # Security settings
    secure_temp_files: bool = True
    verify_file_integrity: bool = True
    secure_delete_temp: bool = False
    
    # Logging settings
    log_level: str = "INFO"
    log_processing_details: bool = False
    log_quality_metrics: bool = False
    
    # Format profiles
    format_profiles: Dict[AudioFormat, FormatProfile] = field(default_factory=dict)
    quality_presets: Dict[str, QualityPreset] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize configuration after creation"""
        if not self.temp_directory:
            self.temp_directory = Path.cwd() / "temp"
        
        if not self.format_profiles:
            self._initialize_format_profiles()
        
        if not self.quality_presets:
            self._initialize_quality_presets()
    
    def _initialize_format_profiles(self):
        """Initialize default format profiles"""
        
        # WAV Profile (Uncompressed PCM)
        self.format_profiles[AudioFormat.WAV] = FormatProfile(
            format=AudioFormat.WAV,
            supported_sample_rates=[8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000, 176400, 192000],
            supported_channels=list(range(1, 33)),  # Up to 32 channels
            supported_bit_depths=[8, 16, 24, 32],
            supports_lossless=True,
            supports_metadata=False,
            supports_multichannel=True,
            quality_presets={
                QualityLevel.LOW: {'bit_depth': 16, 'sample_rate': 44100},
                QualityLevel.MEDIUM: {'bit_depth': 16, 'sample_rate': 48000},
                QualityLevel.HIGH: {'bit_depth': 24, 'sample_rate': 48000},
                QualityLevel.MAXIMUM: {'bit_depth': 24, 'sample_rate': 96000}
            }
        )
        
        # FLAC Profile (Lossless Compression)
        self.format_profiles[AudioFormat.FLAC] = FormatProfile(
            format=AudioFormat.FLAC,
            supported_sample_rates=[8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000, 176400, 192000],
            supported_channels=list(range(1, 9)),  # Up to 8 channels
            supported_bit_depths=[8, 16, 24, 32],
            supports_lossless=True,
            supports_metadata=True,
            supports_multichannel=True,
            compression_levels=list(range(0, 9)),  # 0-8
            quality_presets={
                QualityLevel.LOW: {'compression_level': 8, 'bit_depth': 16},
                QualityLevel.MEDIUM: {'compression_level': 5, 'bit_depth': 16},
                QualityLevel.HIGH: {'compression_level': 3, 'bit_depth': 24},
                QualityLevel.MAXIMUM: {'compression_level': 0, 'bit_depth': 24}
            },
            format_specific_options={'verify_integrity': True}
        )
        
        # MP3 Profile (MPEG-1 Audio Layer III)
        self.format_profiles[AudioFormat.MP3] = FormatProfile(
            format=AudioFormat.MP3,
            supported_sample_rates=[8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000],
            supported_channels=[1, 2],  # Mono/Stereo only
            supported_bit_depths=[16],  # Internal processing
            min_bitrate=32,
            max_bitrate=320,
            default_bitrate=192,
            supports_lossless=False,
            supports_metadata=True,
            supports_multichannel=False,
            quality_presets={
                QualityLevel.LOW: {'bitrate': 128, 'mode': CompressionMode.CBR},
                QualityLevel.MEDIUM: {'bitrate': 192, 'mode': CompressionMode.CBR},
                QualityLevel.HIGH: {'bitrate': 256, 'mode': CompressionMode.CBR},
                QualityLevel.MAXIMUM: {'quality': 0, 'mode': CompressionMode.VBR}
            },
            format_specific_options={
                'joint_stereo': True,
                'highpass_filter': True
            }
        )
        
        # AAC Profile (Advanced Audio Coding)
        self.format_profiles[AudioFormat.AAC] = FormatProfile(
            format=AudioFormat.AAC,
            supported_sample_rates=[8000, 11025, 12000, 16000, 18900, 22050, 24000, 
                                  32000, 37800, 44100, 48000, 56000, 64000, 88200, 96000],
            supported_channels=list(range(1, 9)),  # Up to 7.1 surround
            supported_bit_depths=[16, 24],
            min_bitrate=32,
            max_bitrate=512,
            default_bitrate=128,
            supports_lossless=False,
            supports_metadata=True,
            supports_multichannel=True,
            quality_presets={
                QualityLevel.LOW: {'bitrate': 96, 'profile': 'aac_he'},
                QualityLevel.MEDIUM: {'bitrate': 128, 'profile': 'aac_lc'},
                QualityLevel.HIGH: {'bitrate': 192, 'profile': 'aac_lc'},
                QualityLevel.MAXIMUM: {'bitrate': 256, 'profile': 'aac_lc'}
            },
            format_specific_options={
                'afterburner': True,
                'bandwidth': 0  # Auto
            }
        )
        
        # OGG Vorbis Profile
        self.format_profiles[AudioFormat.OGG] = FormatProfile(
            format=AudioFormat.OGG,
            supported_sample_rates=[8000, 11025, 16000, 22050, 32000, 44100, 48000, 96000, 192000],
            supported_channels=list(range(1, 256)),  # Theoretical limit
            supported_bit_depths=[16, 24],
            min_bitrate=45,
            max_bitrate=500,
            default_bitrate=160,
            supports_lossless=False,
            supports_metadata=True,
            supports_multichannel=True,
            quality_presets={
                QualityLevel.LOW: {'quality': 2},    # ~96 kbps
                QualityLevel.MEDIUM: {'quality': 5}, # ~160 kbps  
                QualityLevel.HIGH: {'quality': 7},   # ~224 kbps
                QualityLevel.MAXIMUM: {'quality': 10} # ~500 kbps
            }
        )
        
        # Opus Profile (Modern Low-Latency Codec)
        self.format_profiles[AudioFormat.OPUS] = FormatProfile(
            format=AudioFormat.OPUS,
            supported_sample_rates=[8000, 12000, 16000, 24000, 48000],
            supported_channels=list(range(1, 256)),
            supported_bit_depths=[16, 24],
            min_bitrate=6,
            max_bitrate=510,
            default_bitrate=128,
            supports_lossless=False,
            supports_metadata=True,
            supports_multichannel=True,
            quality_presets={
                QualityLevel.LOW: {'bitrate': 64, 'application': 'audio'},
                QualityLevel.MEDIUM: {'bitrate': 96, 'application': 'audio'},
                QualityLevel.HIGH: {'bitrate': 128, 'application': 'audio'},
                QualityLevel.MAXIMUM: {'bitrate': 192, 'application': 'audio'}
            },
            format_specific_options={
                'frame_duration': 20,  # ms
                'complexity': 10
            }
        )
        
        # AIFF Profile (Audio Interchange File Format)
        self.format_profiles[AudioFormat.AIFF] = FormatProfile(
            format=AudioFormat.AIFF,
            supported_sample_rates=[8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000, 176400, 192000],
            supported_channels=list(range(1, 33)),
            supported_bit_depths=[8, 16, 24, 32],
            supports_lossless=True,
            supports_metadata=True,
            supports_multichannel=True,
            quality_presets={
                QualityLevel.LOW: {'bit_depth': 16, 'sample_rate': 44100},
                QualityLevel.MEDIUM: {'bit_depth': 16, 'sample_rate': 48000},
                QualityLevel.HIGH: {'bit_depth': 24, 'sample_rate': 48000},
                QualityLevel.MAXIMUM: {'bit_depth': 24, 'sample_rate': 96000}
            }
        )
        
        # M4A Profile (MPEG-4 Audio)
        self.format_profiles[AudioFormat.M4A] = FormatProfile(
            format=AudioFormat.M4A,
            supported_sample_rates=[8000, 11025, 12000, 16000, 22050, 24000, 
                                  32000, 44100, 48000, 64000, 88200, 96000],
            supported_channels=list(range(1, 9)),
            supported_bit_depths=[16, 24],
            min_bitrate=32,
            max_bitrate=512,
            default_bitrate=128,
            supports_lossless=False,
            supports_metadata=True,
            supports_multichannel=True,
            quality_presets={
                QualityLevel.LOW: {'bitrate': 96, 'profile': 'aac_he'},
                QualityLevel.MEDIUM: {'bitrate': 128, 'profile': 'aac_lc'},
                QualityLevel.HIGH: {'bitrate': 192, 'profile': 'aac_lc'},
                QualityLevel.MAXIMUM: {'bitrate': 256, 'profile': 'aac_lc'}
            }
        )
    
    def _initialize_quality_presets(self):
        """Initialize quality presets"""
        
        self.quality_presets["audiophile"] = QualityPreset(
            name="Audiophile",
            description="Maximum quality for critical listening",
            target_quality=1.0,
            bitrate_multiplier=1.5,
            processing_options={
                'apply_dithering': True,
                'dither_noise_shaping': True,
                'preserve_dynamics': True,
                'disable_normalization': True
            },
            format_overrides={
                AudioFormat.MP3: {'quality': 0, 'mode': CompressionMode.VBR},
                AudioFormat.AAC: {'bitrate': 256, 'profile': 'aac_lc'},
                AudioFormat.FLAC: {'compression_level': 0, 'verify_integrity': True}
            }
        )
        
        self.quality_presets["broadcast"] = QualityPreset(
            name="Broadcast",
            description="Professional broadcast quality",
            target_quality=0.95,
            bitrate_multiplier=1.2,
            processing_options={
                'apply_normalization': True,
                'target_level': -16.0,  # EBU R128
                'apply_limiter': True,
                'limiter_threshold': -1.0
            }
        )
        
        self.quality_presets["streaming"] = QualityPreset(
            name="Streaming",
            description="Optimized for streaming platforms",
            target_quality=0.85,
            bitrate_multiplier=1.0,
            processing_options={
                'apply_normalization': True,
                'target_level': -14.0,  # Spotify/YouTube level
                'apply_compressor': True,
                'compressor_ratio': 3.0
            }
        )
        
        self.quality_presets["podcast"] = QualityPreset(
            name="Podcast",
            description="Optimized for voice content",
            target_quality=0.75,
            bitrate_multiplier=0.7,
            processing_options={
                'apply_highpass': True,
                'highpass_frequency': 80,
                'apply_lowpass': True,
                'lowpass_frequency': 15000,
                'apply_compressor': True,
                'compressor_ratio': 4.0
            },
            format_overrides={
                AudioFormat.MP3: {'bitrate': 128, 'joint_stereo': True},
                AudioFormat.AAC: {'bitrate': 96, 'profile': 'aac_he'},
                AudioFormat.OPUS: {'bitrate': 64, 'application': 'voip'}
            }
        )
        
        self.quality_presets["mobile"] = QualityPreset(
            name="Mobile",
            description="Optimized for mobile devices and limited bandwidth",
            target_quality=0.70,
            bitrate_multiplier=0.6,
            processing_options={
                'apply_normalization': True,
                'target_level': -12.0,
                'apply_compressor': True,
                'compressor_ratio': 6.0,
                'force_mono': False  # Keep stereo but reduce bitrate
            },
            format_overrides={
                AudioFormat.MP3: {'bitrate': 96},
                AudioFormat.AAC: {'bitrate': 80, 'profile': 'aac_he'},
                AudioFormat.OPUS: {'bitrate': 48}
            }
        )
    
    def get_format_profile(self, format: AudioFormat) -> Optional[FormatProfile]:
        """Get format profile for specified format"""
        return self.format_profiles.get(format)
    
    def get_quality_preset(self, preset_name: str) -> Optional[QualityPreset]:
        """Get quality preset by name"""
        return self.quality_presets.get(preset_name)
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return issues"""
        issues = []
        
        # Validate temp directory
        if self.temp_directory and not self.temp_directory.parent.exists():
            issues.append("Temporary directory parent does not exist")
        
        # Validate thread settings
        if self.max_worker_threads < 1:
            issues.append("Worker thread count must be at least 1")
        
        # Validate memory settings
        if self.memory_limit_mb < 64:
            issues.append("Memory limit too low (minimum 64MB)")
        
        # Validate quality settings
        if not 0.0 <= self.quality_threshold <= 1.0:
            issues.append("Quality threshold must be between 0.0 and 1.0")
        
        # Validate format profiles
        for format_type, profile in self.format_profiles.items():
            if format_type != profile.format:
                issues.append(f"Format profile mismatch: {format_type} != {profile.format}")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'temp_directory': str(self.temp_directory) if self.temp_directory else None,
            'clean_temp_files': self.clean_temp_files,
            'processing_mode': self.processing_mode.value,
            'max_worker_threads': self.max_worker_threads,
            'default_quality_level': self.default_quality_level.value,
            'preserve_metadata': self.preserve_metadata,
            'log_level': self.log_level,
            'format_profiles': {
                fmt.value: {
                    'supported_sample_rates': profile.supported_sample_rates,
                    'supported_channels': profile.supported_channels,
                    'supports_lossless': profile.supports_lossless,
                    'quality_presets': {
                        level.value: preset for level, preset in profile.quality_presets.items()
                    }
                } for fmt, profile in self.format_profiles.items()
            }
        }
    
    @classmethod
    def from_environment(cls) -> 'ConversionConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables
        if temp_dir := os.getenv('AUDIO_CONV_TEMP_DIR'):
            config.temp_directory = Path(temp_dir)
        
        if threads := os.getenv('AUDIO_CONV_MAX_THREADS'):
            try:
                config.max_worker_threads = int(threads)
            except ValueError:
                logger.warning(f"Invalid thread count in environment: {threads}")
        
        if memory := os.getenv('AUDIO_CONV_MEMORY_LIMIT'):
            try:
                config.memory_limit_mb = int(memory)
            except ValueError:
                logger.warning(f"Invalid memory limit in environment: {memory}")
        
        if log_level := os.getenv('AUDIO_CONV_LOG_LEVEL'):
            config.log_level = log_level.upper()
        
        return config


# Default configuration instance
DEFAULT_CONFIG = ConversionConfig()

# Export configuration classes and default instance
__all__ = [
    'ConversionConfig',
    'FormatProfile', 
    'QualityPreset',
    'ProcessingMode',
    'CompressionMode',
    'DEFAULT_CONFIG'
]
