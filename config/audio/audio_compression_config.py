"""Audio Compression Configuration Module for IA-Influencer Agent Platform
======================================================================

Professional audio compression and dynamics processing configuration.
Supports professional compressor, limiter, expander, and multiband dynamics processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
⚠️ STRICT COPYRIGHT WARNING ⚠️
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
import math

logger = logging.getLogger(__name__)


class CompressorType(Enum):
    """Types of audio compressors"""    VCA = "vca"                                # Voltage Controlled Amplifier
    FET = "fet"                                # Field Effect Transistor
    OPTICAL = "optical"                        # Optical/Opto compressor
    VARIABLE_MU = "variable_mu"                # Variable-mu tube compressor
    DIGITAL = "digital"                        # Digital compressor
    MULTIBAND = "multiband"                    # Multiband compressor
    BRICK_WALL = "brick_wall"                  # Brick wall limiter
    SOFT_KNEE = "soft_knee"                    # Soft knee compressor


class CompressorKneeType(Enum):
    """Compressor knee characteristics"""    HARD = "hard"                              # Hard knee
    SOFT = "soft"                              # Soft knee
    ADAPTIVE = "adaptive"                      # Adaptive knee
    ROUNDED = "rounded"                        # Rounded knee


class DetectionMode(Enum):
    """Signal detection modes"""    PEAK = "peak"                              # Peak detection
    RMS = "rms"                                # RMS detection
    PROGRAM = "program"                        # Program dependent
    TRUE_PEAK = "true_peak"                    # True peak detection
    CREST_FACTOR = "crest_factor"              # Crest factor based


class SideChainSource(Enum):
    """Side-chain signal sources"""    INTERNAL = "internal"                      # Internal signal
    EXTERNAL = "external"                      # External sidechain input
    MID = "mid"                               # Mid channel for M/S processing
    SIDE = "side"                             # Side channel for M/S processing
    FREQUENCY_WEIGHTED = "frequency_weighted"  # Frequency weighted internal


class CompressionStyle(Enum):
    """Compression style characteristics"""    TRANSPARENT = "transparent"                # Transparent/clean compression
    VINTAGE = "vintage"                        # Vintage hardware emulation
    AGGRESSIVE = "aggressive"                  # Aggressive/pumping style
    MUSICAL = "musical"                        # Musical/smooth style
    BROADCAST = "broadcast"                    # Broadcast standard compression
    MASTERING = "mastering"                    # Mastering-grade compression


class LimiterType(Enum):
    """Types of audio limiters"""    PEAK_LIMITER = "peak_limiter"              # Peak limiting
    TRUE_PEAK_LIMITER = "true_peak_limiter"    # True peak limiting
    LOUDNESS_LIMITER = "loudness_limiter"      # Loudness-based limiting
    MULTIBAND_LIMITER = "multiband_limiter"    # Multiband limiting
    SOFT_CLIPPER = "soft_clipper"              # Soft clipping limiter
    HARD_CLIPPER = "hard_clipper"              # Hard clipping limiter


@dataclass
class CompressorBand:
    """Individual compressor band configuration for multiband processing"""    name: str
    frequency_range: Tuple[float, float]       # (low_freq, high_freq) in Hz
    threshold_db: float = -20.0
    ratio: float = 4.0
    attack_ms: float = 10.0
    release_ms: float = 100.0
    knee_db: float = 2.0
    makeup_gain_db: float = 0.0
    enabled: bool = True
    solo: bool = False
    bypass: bool = False


@dataclass
class CompressorConfig:
    """Main compressor configuration"""    enabled: bool = True
    compressor_type: CompressorType = CompressorType.DIGITAL
    compression_style: CompressionStyle = CompressionStyle.TRANSPARENT
    
    # Core parameters
    threshold_db: float = -20.0
    ratio: float = 4.0
    attack_ms: float = 10.0
    release_ms: float = 100.0
    knee_db: float = 2.0
    knee_type: CompressorKneeType = CompressorKneeType.SOFT
    
    # Gain control
    makeup_gain_db: float = 0.0
    auto_makeup_gain: bool = True
    input_gain_db: float = 0.0
    output_gain_db: float = 0.0
    
    # Detection and processing
    detection_mode: DetectionMode = DetectionMode.RMS
    rms_window_ms: float = 10.0
    lookahead_ms: float = 0.0
    
    # Side-chain
    side_chain_enabled: bool = False
    side_chain_source: SideChainSource = SideChainSource.INTERNAL
    side_chain_filter_enabled: bool = False
    side_chain_hpf_frequency: float = 80.0
    side_chain_lpf_frequency: float = 8000.0
    
    # Advanced features
    saturation_enabled: bool = False
    saturation_amount: float = 0.1
    oversampling: int = 1
    dry_wet_mix: float = 1.0                   # 0.0 = dry, 1.0 = wet
    
    # Multiband specific
    crossover_frequencies: List[float] = field(default_factory=lambda: [200.0, 2000.0])
    bands: List[CompressorBand] = field(default_factory=list)


@dataclass
class LimiterConfig:
    """Audio limiter configuration"""    enabled: bool = True
    limiter_type: LimiterType = LimiterType.PEAK_LIMITER
    
    # Core parameters
    ceiling_db: float = -0.3
    release_ms: float = 50.0
    lookahead_ms: float = 5.0
    
    # Advanced parameters
    isr_enabled: bool = True                   # Intersample Reduction
    oversampling: int = 4
    linking: float = 1.0                       # Channel linking 0-1
    
    # Soft clipping
    soft_clip_enabled: bool = False
    soft_clip_threshold_db: float = -1.0
    soft_clip_ratio: float = 10.0
    
    # True peak limiting
    true_peak_detection: bool = True
    true_peak_ceiling_db: float = -1.0
    
    # Loudness limiting
    lufs_target: float = -23.0
    lra_max: float = 7.0                       # Loudness Range
    true_peak_max_db: float = -1.0


@dataclass
class GateConfig:
    """Noise gate/expander configuration"""    enabled: bool = False
    
    # Core parameters
    threshold_db: float = -40.0
    ratio: float = 10.0                        # Expansion ratio
    attack_ms: float = 1.0
    hold_ms: float = 10.0
    release_ms: float = 100.0
    
    # Gate specific
    range_db: float = -60.0                    # Maximum reduction
    hysteresis_db: float = 3.0                 # Threshold hysteresis
    
    # Detection
    detection_mode: DetectionMode = DetectionMode.PEAK
    lookahead_ms: float = 0.0
    
    # Side-chain
    side_chain_enabled: bool = False
    side_chain_source: SideChainSource = SideChainSource.INTERNAL


@dataclass
class DeEsserConfig:
    """De-esser configuration"""    enabled: bool = False
    
    # Core parameters
    threshold_db: float = -15.0
    ratio: float = 5.0
    frequency_center: float = 6000.0
    frequency_bandwidth: float = 2000.0
    
    # Processing
    attack_ms: float = 1.0
    release_ms: float = 10.0
    lookahead_ms: float = 2.0
    
    # Advanced
    split_band: bool = True                    # Split band vs. wide band
    monitor_frequency: bool = False            # Monitor the de-ess frequency


class AudioCompressionConfig:
    """    Comprehensive audio compression configuration manager
    
    Manages all aspects of audio dynamics processing including compression,
    limiting, gating, de-essing, and multiband dynamics processing.
    """    
    def __init__(self):
        """Initialize audio compression configuration"""        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core processors
        self.compressor = CompressorConfig()
        self.limiter = LimiterConfig()
        self.gate = GateConfig()
        self.de_esser = DeEsserConfig()
        
        # Processing chain configuration
        self._processing_chain_order = [
            "gate",
            "compressor", 
            "de_esser",
            "limiter"
        ]
        
        # Compression presets
        self._compression_presets = self._initialize_compression_presets()
        
        # Hardware emulations
        self._hardware_emulations = self._initialize_hardware_emulations()
        
        # Platform-specific compression profiles
        self._platform_profiles = self._initialize_platform_profiles()
        
        # Broadcast standards compliance
        self._broadcast_standards = self._initialize_broadcast_standards()
        
        # Real-time processing optimizations
        self._realtime_optimizations = self._initialize_realtime_optimizations()
        
        # Initialize multiband compressor bands
        self._initialize_multiband_setup()
        
        self.logger.info("AudioCompressionConfig initialized successfully")
    
    def _initialize_compression_presets(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compression presets"""        return {
            "vocal_compression": {
                "name": "Vocal Compression",
                "description": "Optimized for vocal recording and processing",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.OPTICAL.value,
                    "compression_style": CompressionStyle.MUSICAL.value,
                    "threshold_db": -18.0,
                    "ratio": 3.0,
                    "attack_ms": 8.0,
                    "release_ms": 80.0,
                    "knee_db": 3.0,
                    "auto_makeup_gain": True,
                    "detection_mode": DetectionMode.RMS.value,
                    "rms_window_ms": 15.0
                },
                "de_esser": {
                    "enabled": True,
                    "threshold_db": -12.0,
                    "frequency_center": 6500.0,
                    "frequency_bandwidth": 1500.0
                },
                "gate": {
                    "enabled": True,
                    "threshold_db": -45.0,
                    "ratio": 8.0,
                    "release_ms": 150.0
                }
            },
            "drum_compression": {
                "name": "Drum Compression",
                "description": "Aggressive compression for drums",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.FET.value,
                    "compression_style": CompressionStyle.AGGRESSIVE.value,
                    "threshold_db": -12.0,
                    "ratio": 6.0,
                    "attack_ms": 0.5,
                    "release_ms": 30.0,
                    "knee_db": 1.0,
                    "knee_type": CompressorKneeType.HARD.value,
                    "saturation_enabled": True,
                    "saturation_amount": 0.2
                },
                "gate": {
                    "enabled": True,
                    "threshold_db": -35.0,
                    "ratio": 15.0,
                    "attack_ms": 0.1,
                    "release_ms": 50.0,
                    "range_db": -40.0
                }
            },
            "bass_compression": {
                "name": "Bass Compression",
                "description": "Compression optimized for bass instruments",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.VCA.value,
                    "compression_style": CompressionStyle.MUSICAL.value,
                    "threshold_db": -15.0,
                    "ratio": 4.5,
                    "attack_ms": 15.0,
                    "release_ms": 120.0,
                    "knee_db": 4.0,
                    "side_chain_enabled": True,
                    "side_chain_hpf_frequency": 60.0
                }
            },
            "mix_bus_compression": {
                "name": "Mix Bus Compression",
                "description": "Gentle compression for mix bus processing",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.VARIABLE_MU.value,
                    "compression_style": CompressionStyle.VINTAGE.value,
                    "threshold_db": -6.0,
                    "ratio": 2.5,
                    "attack_ms": 30.0,
                    "release_ms": 300.0,
                    "knee_db": 5.0,
                    "detection_mode": DetectionMode.PROGRAM.value,
                    "saturation_enabled": True,
                    "saturation_amount": 0.1
                }
            },
            "mastering_compression": {
                "name": "Mastering Compression",
                "description": "Transparent compression for mastering",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.MULTIBAND.value,
                    "compression_style": CompressionStyle.MASTERING.value,
                    "threshold_db": -8.0,
                    "ratio": 2.0,
                    "attack_ms": 50.0,
                    "release_ms": 500.0,
                    "knee_db": 6.0,
                    "oversampling": 4,
                    "lookahead_ms": 10.0
                },
                "limiter": {
                    "enabled": True,
                    "limiter_type": LimiterType.TRUE_PEAK_LIMITER.value,
                    "ceiling_db": -0.3,
                    "release_ms": 100.0,
                    "lookahead_ms": 10.0,
                    "oversampling": 8,
                    "true_peak_detection": True
                }
            },
            "broadcast_compression": {
                "name": "Broadcast Compression",
                "description": "Broadcast standard compression and limiting",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.MULTIBAND.value,
                    "compression_style": CompressionStyle.BROADCAST.value,
                    "threshold_db": -20.0,
                    "ratio": 5.0,
                    "attack_ms": 5.0,
                    "release_ms": 50.0
                },
                "limiter": {
                    "enabled": True,
                    "limiter_type": LimiterType.LOUDNESS_LIMITER.value,
                    "lufs_target": -23.0,
                    "lra_max": 7.0,
                    "true_peak_max_db": -1.0
                }
            },
            "podcast_compression": {
                "name": "Podcast Compression",
                "description": "Optimized for podcast production",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.OPTICAL.value,
                    "compression_style": CompressionStyle.BROADCAST.value,
                    "threshold_db": -20.0,
                    "ratio": 10.0,  # Heavy compression for consistency
                    "attack_ms": 10.0,
                    "release_ms": 200.0,
                    "auto_makeup_gain": True
                },
                "gate": {
                    "enabled": True,
                    "threshold_db": -50.0,
                    "ratio": 6.0,
                    "release_ms": 300.0
                },
                "de_esser": {
                    "enabled": True,
                    "threshold_db": -10.0,
                    "frequency_center": 7000.0
                },
                "limiter": {
                    "enabled": True,
                    "ceiling_db": -3.0,
                    "release_ms": 100.0
                }
            },
            "live_streaming": {
                "name": "Live Streaming",
                "description": "Real-time compression for live streaming",
                "compressor": {
                    "enabled": True,
                    "compressor_type": CompressorType.DIGITAL.value,
                    "compression_style": CompressionStyle.BROADCAST.value,
                    "threshold_db": -16.0,
                    "ratio": 6.0,
                    "attack_ms": 3.0,
                    "release_ms": 40.0,
                    "lookahead_ms": 0.0  # No lookahead for real-time
                },
                "gate": {
                    "enabled": True,
                    "threshold_db": -40.0,
                    "attack_ms": 0.5,
                    "release_ms": 100.0
                },
                "limiter": {
                    "enabled": True,
                    "ceiling_db": -1.0,
                    "release_ms": 25.0,
                    "lookahead_ms": 2.0
                }
            }
        }
    
    def _initialize_hardware_emulations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize hardware emulation models"""        return {
            "la2a_optical": {
                "name": "LA-2A Optical Leveling Amplifier",
                "type": "optical",
                "characteristics": {
                    "attack_ms": [10, 20],  # Variable range
                    "release_ms": [60, 5000],  # Auto release
                    "ratio": "program_dependent",
                    "frequency_response": "vintage_warmth",
                    "harmonic_distortion": 0.5
                },
                "use_cases": ["vocals", "bass", "mix_bus"]
            },
            "1176_fet": {
                "name": "1176 FET Compressor",
                "type": "fet",
                "characteristics": {
                    "attack_ms": [0.02, 0.8],
                    "release_ms": [5, 1100],
                    "ratio_options": [4, 8, 12, 20],
                    "all_buttons_mode": True,  # Famous "all buttons in" mode
                    "frequency_response": "bright",
                    "harmonic_distortion": 0.8
                },
                "use_cases": ["drums", "vocals", "guitar"]
            },
            "fairchild_670": {
                "name": "Fairchild 670 Variable-Mu",
                "type": "variable_mu",
                "characteristics": {
                    "attack_ms": [0.2, 25],
                    "release_ms": [300, 25000],
                    "ratio": "program_dependent",
                    "mid_side_processing": True,
                    "tube_saturation": True,
                    "frequency_response": "vintage_smooth"
                },
                "use_cases": ["mix_bus", "mastering", "program_material"]
            },
            "distressor": {
                "name": "Distressor",
                "type": "digital_vintage",
                "characteristics": {
                    "ratios": [1, 2, 3, 4, 6, 8, 10, "nuke"],
                    "attack_options": 10,  # 10 positions
                    "release_options": 10,  # 10 positions
                    "distortion_modes": ["dist1", "dist2", "dist3"],
                    "frequency_response": "modern"
                },
                "use_cases": ["drums", "mix_bus", "creative_processing"]
            },
            "ssl_bus_comp": {
                "name": "SSL Bus Compressor",
                "type": "vca",
                "characteristics": {
                    "attack_ms": [0.1, 30],
                    "release_ms": [0.1, 4000],
                    "ratio_options": [2, 4, 10],
                    "frequency_response": "clean_modern",
                    "mix_bus_optimized": True
                },
                "use_cases": ["mix_bus", "drum_bus", "master_bus"]
            }
        }
    
    def _initialize_platform_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific compression profiles"""        return {
            "spotify": {
                "name": "Spotify Optimization",
                "loudness_target": -14.0,  # LUFS
                "true_peak_limit": -1.0,   # dBFS
                "compression_characteristics": {
                    "preserve_dynamics": True,
                    "max_ratio": 4.0,
                    "gentle_limiting": True
                },
                "quality_priorities": ["dynamic_range", "tonal_balance"]
            },
            "apple_music": {
                "name": "Apple Music Optimization",
                "loudness_target": -16.0,  # LUFS
                "true_peak_limit": -1.0,   # dBFS
                "compression_characteristics": {
                    "preserve_dynamics": True,
                    "spatial_audio_compatible": True,
                    "atmos_optimized": True
                },
                "quality_priorities": ["dynamic_range", "spatial_imaging"]
            },
            "youtube": {
                "name": "YouTube Optimization",
                "loudness_target": -14.0,  # LUFS
                "true_peak_limit": -1.0,   # dBFS
                "compression_characteristics": {
                    "dialogue_clarity": True,
                    "background_ducking": True,
                    "mobile_optimized": True
                },
                "quality_priorities": ["speech_intelligibility", "loudness_consistency"]
            },
            "tiktok": {
                "name": "TikTok Optimization",
                "loudness_target": -12.0,  # LUFS (louder)
                "true_peak_limit": -0.5,   # dBFS
                "compression_characteristics": {
                    "punch_emphasis": True,
                    "mobile_speakers": True,
                    "short_form_optimized": True
                },
                "quality_priorities": ["impact", "mobile_playback"]
            },
            "twitch": {
                "name": "Twitch Streaming",
                "real_time_constraints": True,
                "max_latency_ms": 20,
                "compression_characteristics": {
                    "voice_priority": True,
                    "game_audio_balance": True,
                    "consistent_levels": True
                },
                "quality_priorities": ["real_time_performance", "voice_clarity"]
            },
            "discord": {
                "name": "Discord Voice",
                "real_time_constraints": True,
                "max_latency_ms": 10,
                "compression_characteristics": {
                    "ultra_low_latency": True,
                    "voice_optimized": True,
                    "bandwidth_efficient": True
                },
                "quality_priorities": ["latency", "speech_clarity"]
            }
        }
    
    def _initialize_broadcast_standards(self) -> Dict[str, Dict[str, Any]]:
        """Initialize broadcast standards compliance"""        return {
            "ebu_r128": {
                "name": "EBU R128",
                "region": "Europe",
                "loudness_target": -23.0,  # LUFS
                "loudness_range_max": 20.0,  # LU
                "true_peak_max": -1.0,      # dBFS
                "measurement_window": "momentary_400ms"
            },
            "atsc_a85": {
                "name": "ATSC A/85",
                "region": "North America",
                "loudness_target": -24.0,  # LKFS
                "dialogue_intelligence": "primary",
                "commercial_loudness": -24.0,
                "true_peak_max": -2.0
            },
            "arib_tr_b32": {
                "name": "ARIB TR-B32",
                "region": "Japan",
                "loudness_target": -24.0,  # LKFS
                "dynamic_range_control": True,
                "multichannel_support": True
            },
            "itut_bs1770": {
                "name": "ITU-R BS.1770-4",
                "region": "International",
                "loudness_target": -23.0,  # LUFS
                "gating_method": "relative_absolute",
                "multichannel_weighting": True
            },
            "netflix": {
                "name": "Netflix Delivery Spec",
                "loudness_target": -27.0,  # LUFS (dialogue)
                "true_peak_max": -2.0,     # dBFS
                "dynamic_range_min": 3.0,   # LU
                "dialogue_gating": True
            }
        }
    
    def _initialize_realtime_optimizations(self) -> Dict[str, Any]:
        """Initialize real-time processing optimizations"""        return {
            "latency_optimized": {
                "lookahead_ms": 0.0,
                "oversampling": 1,
                "buffer_size": 64,
                "quality_vs_speed": 0.2  # Favor speed
            },
            "balanced": {
                "lookahead_ms": 2.0,
                "oversampling": 2,
                "buffer_size": 128,
                "quality_vs_speed": 0.5  # Balanced
            },
            "quality_optimized": {
                "lookahead_ms": 10.0,
                "oversampling": 4,
                "buffer_size": 512,
                "quality_vs_speed": 0.9  # Favor quality
            },
            "streaming": {
                "lookahead_ms": 1.0,
                "oversampling": 2,
                "buffer_size": 256,
                "adaptive_processing": True,
                "cpu_monitoring": True
            }
        }
    
    def _initialize_multiband_setup(self):
        """Initialize default multiband compressor setup"""        if not self.compressor.bands:
            self.compressor.bands = [
                CompressorBand(
                    name="Low Band",
                    frequency_range=(20.0, 200.0),
                    threshold_db=-15.0,
                    ratio=3.0,
                    attack_ms=20.0,
                    release_ms=200.0
                ),
                CompressorBand(
                    name="Mid Band",
                    frequency_range=(200.0, 2000.0),
                    threshold_db=-18.0,
                    ratio=4.0,
                    attack_ms=10.0,
                    release_ms=100.0
                ),
                CompressorBand(
                    name="High Band",
                    frequency_range=(2000.0, 20000.0),
                    threshold_db=-12.0,
                    ratio=2.5,
                    attack_ms=5.0,
                    release_ms=50.0
                )
            ]
            
            self.compressor.crossover_frequencies = [200.0, 2000.0]
    
    def get_compression_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """        Get compression preset by name
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset configuration or None if not found
        """        return self._compression_presets.get(preset_name)
    
    def apply_compression_preset(self, preset_name: str) -> bool:
        """        Apply compression preset to current configuration
        
        Args:
            preset_name: Name of the preset to apply
            
        Returns:
            Success status
        """        try:
            preset = self.get_compression_preset(preset_name)
            if not preset:
                self.logger.error(f"Preset '{preset_name}' not found")
                return False
            
            # Apply compressor settings
            if "compressor" in preset:
                comp_config = preset["compressor"]
                self.compressor.enabled = comp_config.get("enabled", True)
                
                if "compressor_type" in comp_config:
                    self.compressor.compressor_type = CompressorType(comp_config["compressor_type"])
                if "compression_style" in comp_config:
                    self.compressor.compression_style = CompressionStyle(comp_config["compression_style"])
                
                # Core parameters
                self.compressor.threshold_db = comp_config.get("threshold_db", -20.0)
                self.compressor.ratio = comp_config.get("ratio", 4.0)
                self.compressor.attack_ms = comp_config.get("attack_ms", 10.0)
                self.compressor.release_ms = comp_config.get("release_ms", 100.0)
                self.compressor.knee_db = comp_config.get("knee_db", 2.0)
                
                if "knee_type" in comp_config:
                    self.compressor.knee_type = CompressorKneeType(comp_config["knee_type"])
                if "detection_mode" in comp_config:
                    self.compressor.detection_mode = DetectionMode(comp_config["detection_mode"])
                
                # Advanced settings
                self.compressor.auto_makeup_gain = comp_config.get("auto_makeup_gain", True)
                self.compressor.rms_window_ms = comp_config.get("rms_window_ms", 10.0)
                self.compressor.lookahead_ms = comp_config.get("lookahead_ms", 0.0)
                self.compressor.saturation_enabled = comp_config.get("saturation_enabled", False)
                self.compressor.saturation_amount = comp_config.get("saturation_amount", 0.1)
                self.compressor.oversampling = comp_config.get("oversampling", 1)
                
                # Side-chain settings
                self.compressor.side_chain_enabled = comp_config.get("side_chain_enabled", False)
                if self.compressor.side_chain_enabled:
                    self.compressor.side_chain_hpf_frequency = comp_config.get("side_chain_hpf_frequency", 80.0)
            
            # Apply limiter settings
            if "limiter" in preset:
                lim_config = preset["limiter"]
                self.limiter.enabled = lim_config.get("enabled", False)
                
                if "limiter_type" in lim_config:
                    self.limiter.limiter_type = LimiterType(lim_config["limiter_type"])
                
                self.limiter.ceiling_db = lim_config.get("ceiling_db", -0.3)
                self.limiter.release_ms = lim_config.get("release_ms", 50.0)
                self.limiter.lookahead_ms = lim_config.get("lookahead_ms", 5.0)
                self.limiter.oversampling = lim_config.get("oversampling", 4)
                self.limiter.true_peak_detection = lim_config.get("true_peak_detection", True)
                
                # Loudness limiting
                self.limiter.lufs_target = lim_config.get("lufs_target", -23.0)
                self.limiter.lra_max = lim_config.get("lra_max", 7.0)
                self.limiter.true_peak_max_db = lim_config.get("true_peak_max_db", -1.0)
            
            # Apply gate settings
            if "gate" in preset:
                gate_config = preset["gate"]
                self.gate.enabled = gate_config.get("enabled", False)
                self.gate.threshold_db = gate_config.get("threshold_db", -40.0)
                self.gate.ratio = gate_config.get("ratio", 10.0)
                self.gate.attack_ms = gate_config.get("attack_ms", 1.0)
                self.gate.release_ms = gate_config.get("release_ms", 100.0)
                self.gate.range_db = gate_config.get("range_db", -60.0)
            
            # Apply de-esser settings
            if "de_esser" in preset:
                de_ess_config = preset["de_esser"]
                self.de_esser.enabled = de_ess_config.get("enabled", False)
                self.de_esser.threshold_db = de_ess_config.get("threshold_db", -15.0)
                self.de_esser.frequency_center = de_ess_config.get("frequency_center", 6000.0)
                self.de_esser.frequency_bandwidth = de_ess_config.get("frequency_bandwidth", 2000.0)
            
            self.logger.info(f"Applied compression preset: {preset_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply preset '{preset_name}': {e}")
            return False
    
    def optimize_for_platform(self, platform: str) -> bool:
        """        Optimize compression settings for specific platform
        
        Args:
            platform: Target platform name
            
        Returns:
            Success status
        """        try:
            profile = self._platform_profiles.get(platform.lower())
            if not profile:
                self.logger.warning(f"No profile found for platform: {platform}")
                return False
            
            # Apply loudness targeting
            if "loudness_target" in profile:
                target_lufs = profile["loudness_target"]
                
                # Adjust limiter for loudness target
                self.limiter.enabled = True
                self.limiter.limiter_type = LimiterType.LOUDNESS_LIMITER
                self.limiter.lufs_target = target_lufs
                
                # Adjust compressor threshold relative to target
                self.compressor.threshold_db = target_lufs + 8.0
            
            if "true_peak_limit" in profile:
                self.limiter.ceiling_db = profile["true_peak_limit"]
                self.limiter.true_peak_ceiling_db = profile["true_peak_limit"]
            
            # Apply compression characteristics
            characteristics = profile.get("compression_characteristics", {})
            
            if characteristics.get("preserve_dynamics"):
                # Use gentler compression
                self.compressor.ratio = min(self.compressor.ratio, 3.0)
                self.compressor.knee_db = max(self.compressor.knee_db, 4.0)
                self.compressor.compression_style = CompressionStyle.TRANSPARENT
            
            if characteristics.get("dialogue_clarity"):
                # Optimize for speech
                self.compressor.side_chain_enabled = True
                self.compressor.side_chain_hpf_frequency = 200.0
                self.de_esser.enabled = True
            
            if characteristics.get("mobile_optimized"):
                # Optimize for mobile playback
                self.compressor.ratio = max(self.compressor.ratio, 4.0)
                self.limiter.ceiling_db = max(self.limiter.ceiling_db, -1.0)
            
            if characteristics.get("real_time_constraints"):
                # Apply real-time optimizations
                self.compressor.lookahead_ms = 0.0
                self.compressor.oversampling = 1
                self.limiter.lookahead_ms = min(self.limiter.lookahead_ms, 2.0)
                self.limiter.oversampling = 1
            
            self.logger.info(f"Optimized compression for platform: {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Platform optimization failed: {e}")
            return False
    
    def apply_hardware_emulation(self, emulation_name: str) -> bool:
        """        Apply hardware emulation characteristics
        
        Args:
            emulation_name: Name of hardware emulation
            
        Returns:
            Success status
        """        try:
            emulation = self._hardware_emulations.get(emulation_name)
            if not emulation:
                self.logger.error(f"Hardware emulation '{emulation_name}' not found")
                return False
            
            characteristics = emulation["characteristics"]
            
            # Apply attack/release characteristics
            if "attack_ms" in characteristics:
                attack_range = characteristics["attack_ms"]
                if isinstance(attack_range, list):
                    self.compressor.attack_ms = attack_range[0]  # Use fast attack
                else:
                    self.compressor.attack_ms = attack_range
            
            if "release_ms" in characteristics:
                release_range = characteristics["release_ms"]
                if isinstance(release_range, list):
                    self.compressor.release_ms = release_range[1]  # Use slow release
                else:
                    self.compressor.release_ms = release_range
            
            # Apply ratio characteristics
            if "ratio_options" in characteristics:
                ratios = characteristics["ratio_options"]
                if isinstance(ratios, list):
                    self.compressor.ratio = ratios[1]  # Use moderate ratio
                else:
                    self.compressor.ratio = ratios
            
            # Apply type-specific characteristics
            emulation_type = emulation["type"]
            if emulation_type == "optical":
                self.compressor.compressor_type = CompressorType.OPTICAL
                self.compressor.compression_style = CompressionStyle.MUSICAL
                self.compressor.knee_type = CompressorKneeType.SOFT
            elif emulation_type == "fet":
                self.compressor.compressor_type = CompressorType.FET
                self.compressor.compression_style = CompressionStyle.AGGRESSIVE
                self.compressor.knee_type = CompressorKneeType.HARD
            elif emulation_type == "variable_mu":
                self.compressor.compressor_type = CompressorType.VARIABLE_MU
                self.compressor.compression_style = CompressionStyle.VINTAGE
                self.compressor.knee_type = CompressorKneeType.SOFT
            elif emulation_type == "vca":
                self.compressor.compressor_type = CompressorType.VCA
                self.compressor.compression_style = CompressionStyle.TRANSPARENT
            
            # Apply harmonic characteristics
            if "harmonic_distortion" in characteristics:
                self.compressor.saturation_enabled = True
                self.compressor.saturation_amount = characteristics["harmonic_distortion"]
            
            # Special modes
            if "all_buttons_mode" in characteristics and characteristics["all_buttons_mode"]:
                # 1176 "all buttons in" mode
                self.compressor.ratio = 12.0
                self.compressor.attack_ms = 0.05
                self.compressor.compression_style = CompressionStyle.AGGRESSIVE
            
            self.logger.info(f"Applied hardware emulation: {emulation_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Hardware emulation failed: {e}")
            return False
    
    def calculate_compression_parameters(self, 
                                       input_level_db: float,
                                       target_level_db: float,
                                       dynamic_range_db: float) -> Dict[str, float]:
        """        Calculate optimal compression parameters for target levels
        
        Args:
            input_level_db: Average input level in dB
            target_level_db: Desired output level in dB
            dynamic_range_db: Desired dynamic range in dB
            
        Returns:
            Calculated compression parameters
        """        try:
            # Calculate required gain reduction
            gain_reduction_db = input_level_db - target_level_db
            
            # Calculate threshold (typically 6-10 dB above target)
            threshold_db = target_level_db + 8.0
            
            # Calculate ratio based on dynamic range requirements
            if dynamic_range_db < 6.0:
                ratio = 8.0  # Heavy compression
            elif dynamic_range_db < 12.0:
                ratio = 4.0  # Moderate compression
            else:
                ratio = 2.5  # Light compression
            
            # Calculate makeup gain
            makeup_gain_db = gain_reduction_db * (1.0 - 1.0/ratio)
            
            # Adjust attack/release based on ratio
            if ratio >= 6.0:
                attack_ms = 5.0   # Fast for heavy compression
                release_ms = 50.0
            elif ratio >= 4.0:
                attack_ms = 10.0  # Medium
                release_ms = 100.0
            else:
                attack_ms = 20.0  # Slow for light compression
                release_ms = 200.0
            
            # Calculate knee width based on material
            knee_db = min(6.0, max(1.0, dynamic_range_db / 4.0))
            
            return {
                "threshold_db": threshold_db,
                "ratio": ratio,
                "attack_ms": attack_ms,
                "release_ms": release_ms,
                "knee_db": knee_db,
                "makeup_gain_db": makeup_gain_db,
                "expected_gain_reduction_db": gain_reduction_db
            }
            
        except Exception as e:
            self.logger.error(f"Parameter calculation failed: {e}")
            return {}
    
    def estimate_processing_latency(self, 
                                  real_time: bool = False,
                                  quality_level: str = "balanced") -> Dict[str, Any]:
        """        Estimate processing latency for current configuration
        
        Args:
            real_time: Whether real-time processing is required
            quality_level: Processing quality level
            
        Returns:
            Latency estimation breakdown
        """        try:
            # Get optimization settings
            optimization = self._realtime_optimizations.get(quality_level, 
                                                          self._realtime_optimizations["balanced"])
            
            # Base latencies (milliseconds)
            component_latencies = {
                "gate": 0.5,
                "compressor": 2.0 + optimization["lookahead_ms"],
                "de_esser": 1.0,
                "limiter": 1.0 + optimization["lookahead_ms"]
            }
            
            # Oversampling adds latency
            oversampling_latency = 0.5 * math.log2(optimization["oversampling"])
            
            # Calculate total latency
            total_latency = 0.0
            active_components = []
            
            if self.gate.enabled:
                total_latency += component_latencies["gate"]
                active_components.append("gate")
            
            if self.compressor.enabled:
                comp_latency = component_latencies["compressor"]
                if self.compressor.compressor_type == CompressorType.MULTIBAND:
                    comp_latency *= 1.5  # Additional latency for multiband
                total_latency += comp_latency
                active_components.append("compressor")
            
            if self.de_esser.enabled:
                total_latency += component_latencies["de_esser"]
                active_components.append("de_esser")
            
            if self.limiter.enabled:
                lim_latency = component_latencies["limiter"]
                total_latency += lim_latency
                active_components.append("limiter")
            
            # Add oversampling latency
            total_latency += oversampling_latency
            
            # Buffer latency
            buffer_latency = (optimization["buffer_size"] / 48000.0) * 1000.0 * 2  # I/O buffers
            
            total_system_latency = total_latency + buffer_latency
            
            return {
                "processing_latency_ms": total_latency,
                "buffer_latency_ms": buffer_latency,
                "total_latency_ms": total_system_latency,
                "active_components": active_components,
                "oversampling_factor": optimization["oversampling"],
                "buffer_size": optimization["buffer_size"],
                "real_time_capable": total_system_latency < 20.0,
                "broadcast_capable": total_system_latency < 50.0,
                "quality_level": quality_level,
                "optimization_applied": optimization
            }
            
        except Exception as e:
            self.logger.error(f"Latency estimation failed: {e}")
            return {"error": str(e)}
    
    def validate_compression_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """        Validate compression configuration
        
        Args:
            config: Compression configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """        errors = []
        is_valid = True
        
        try:
            # Validate compressor settings
            if "compressor" in config and config["compressor"].get("enabled", False):
                comp_config = config["compressor"]
                
                # Validate ratio
                ratio = comp_config.get("ratio", 1.0)
                if ratio < 1.0 or ratio > 100.0:
                    errors.append("Compressor ratio must be between 1.0 and 100.0")
                    is_valid = False
                
                # Validate threshold
                threshold = comp_config.get("threshold_db", 0.0)
                if threshold > 0.0:
                    errors.append("Compressor threshold should be negative or zero")
                    is_valid = False
                
                # Validate attack/release times
                attack = comp_config.get("attack_ms", 0.0)
                if attack < 0.0 or attack > 1000.0:
                    errors.append("Attack time should be between 0 and 1000 ms")
                    is_valid = False
                
                release = comp_config.get("release_ms", 0.0)
                if release < 0.0 or release > 10000.0:
                    errors.append("Release time should be between 0 and 10000 ms")
                    is_valid = False
                
                # Validate knee
                knee = comp_config.get("knee_db", 0.0)
                if knee < 0.0 or knee > 20.0:
                    errors.append("Knee width should be between 0 and 20 dB")
                    is_valid = False
            
            # Validate limiter settings
            if "limiter" in config and config["limiter"].get("enabled", False):
                lim_config = config["limiter"]
                
                ceiling = lim_config.get("ceiling_db", 0.0)
                if ceiling > 0.0:
                    errors.append("Limiter ceiling should be negative or zero")
                    is_valid = False
                
                release = lim_config.get("release_ms", 0.0)
                if release < 1.0 or release > 1000.0:
                    errors.append("Limiter release should be between 1 and 1000 ms")
                    is_valid = False
            
            # Validate gate settings
            if "gate" in config and config["gate"].get("enabled", False):
                gate_config = config["gate"]
                
                threshold = gate_config.get("threshold_db", 0.0)
                if threshold > 0.0:
                    errors.append("Gate threshold should be negative or zero")
                    is_valid = False
                
                range_db = gate_config.get("range_db", -60.0)
                if range_db > threshold:
                    errors.append("Gate range should be lower than threshold")
                    is_valid = False
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            is_valid = False
        
        return is_valid, errors
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete compression configuration"""        try:
            return {
                "compressor": {
                    "enabled": self.compressor.enabled,
                    "compressor_type": self.compressor.compressor_type.value,
                    "compression_style": self.compressor.compression_style.value,
                    "threshold_db": self.compressor.threshold_db,
                    "ratio": self.compressor.ratio,
                    "attack_ms": self.compressor.attack_ms,
                    "release_ms": self.compressor.release_ms,
                    "knee_db": self.compressor.knee_db,
                    "knee_type": self.compressor.knee_type.value,
                    "makeup_gain_db": self.compressor.makeup_gain_db,
                    "auto_makeup_gain": self.compressor.auto_makeup_gain,
                    "input_gain_db": self.compressor.input_gain_db,
                    "output_gain_db": self.compressor.output_gain_db,
                    "detection_mode": self.compressor.detection_mode.value,
                    "rms_window_ms": self.compressor.rms_window_ms,
                    "lookahead_ms": self.compressor.lookahead_ms,
                    "side_chain_enabled": self.compressor.side_chain_enabled,
                    "side_chain_source": self.compressor.side_chain_source.value,
                    "side_chain_filter_enabled": self.compressor.side_chain_filter_enabled,
                    "side_chain_hpf_frequency": self.compressor.side_chain_hpf_frequency,
                    "side_chain_lpf_frequency": self.compressor.side_chain_lpf_frequency,
                    "saturation_enabled": self.compressor.saturation_enabled,
                    "saturation_amount": self.compressor.saturation_amount,
                    "oversampling": self.compressor.oversampling,
                    "dry_wet_mix": self.compressor.dry_wet_mix,
                    "crossover_frequencies": self.compressor.crossover_frequencies,
                    "bands": [
                        {
                            "name": band.name,
                            "frequency_range": band.frequency_range,
                            "threshold_db": band.threshold_db,
                            "ratio": band.ratio,
                            "attack_ms": band.attack_ms,
                            "release_ms": band.release_ms,
                            "knee_db": band.knee_db,
                            "makeup_gain_db": band.makeup_gain_db,
                            "enabled": band.enabled,
                            "solo": band.solo,
                            "bypass": band.bypass
                        }
                        for band in self.compressor.bands
                    ]
                },
                "limiter": {
                    "enabled": self.limiter.enabled,
                    "limiter_type": self.limiter.limiter_type.value,
                    "ceiling_db": self.limiter.ceiling_db,
                    "release_ms": self.limiter.release_ms,
                    "lookahead_ms": self.limiter.lookahead_ms,
                    "isr_enabled": self.limiter.isr_enabled,
                    "oversampling": self.limiter.oversampling,
                    "linking": self.limiter.linking,
                    "soft_clip_enabled": self.limiter.soft_clip_enabled,
                    "soft_clip_threshold_db": self.limiter.soft_clip_threshold_db,
                    "soft_clip_ratio": self.limiter.soft_clip_ratio,
                    "true_peak_detection": self.limiter.true_peak_detection,
                    "true_peak_ceiling_db": self.limiter.true_peak_ceiling_db,
                    "lufs_target": self.limiter.lufs_target,
                    "lra_max": self.limiter.lra_max,
                    "true_peak_max_db": self.limiter.true_peak_max_db
                },
                "gate": {
                    "enabled": self.gate.enabled,
                    "threshold_db": self.gate.threshold_db,
                    "ratio": self.gate.ratio,
                    "attack_ms": self.gate.attack_ms,
                    "hold_ms": self.gate.hold_ms,
                    "release_ms": self.gate.release_ms,
                    "range_db": self.gate.range_db,
                    "hysteresis_db": self.gate.hysteresis_db,
                    "detection_mode": self.gate.detection_mode.value,
                    "lookahead_ms": self.gate.lookahead_ms,
                    "side_chain_enabled": self.gate.side_chain_enabled,
                    "side_chain_source": self.gate.side_chain_source.value
                },
                "de_esser": {
                    "enabled": self.de_esser.enabled,
                    "threshold_db": self.de_esser.threshold_db,
                    "ratio": self.de_esser.ratio,
                    "frequency_center": self.de_esser.frequency_center,
                    "frequency_bandwidth": self.de_esser.frequency_bandwidth,
                    "attack_ms": self.de_esser.attack_ms,
                    "release_ms": self.de_esser.release_ms,
                    "lookahead_ms": self.de_esser.lookahead_ms,
                    "split_band": self.de_esser.split_band,
                    "monitor_frequency": self.de_esser.monitor_frequency
                },
                "processing_chain_order": self._processing_chain_order,
                "available_presets": list(self._compression_presets.keys()),
                "hardware_emulations": list(self._hardware_emulations.keys()),
                "platform_profiles": list(self._platform_profiles.keys()),
                "broadcast_standards": list(self._broadcast_standards.keys()),
                "realtime_optimizations": self._realtime_optimizations
            }
        except Exception as e:
            self.logger.error(f"Config export failed: {e}")
            return {}
