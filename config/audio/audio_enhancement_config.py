"""Audio Enhancement Configuration Module for IA-Influencer Agent Platform
=======================================================================

Professional audio enhancement and processing effects configuration.
Supports noise reduction, EQ, dynamics processing, spatial audio, and AI-based enhancements.

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


class EnhancementType(Enum):
    """
Audio enhancement types"""

    NOISE_REDUCTION = "noise_reduction"         # Noise suppression and reduction
    EQUALIZATION = "equalization"               # Frequency equalization
    DYNAMICS = "dynamics"                       # Compression, limiting, gating
    SPATIAL = "spatial"                         # Stereo widening, 3D audio
    HARMONIC = "harmonic"                       # Harmonic enhancement
    PSYCHOACOUSTIC = "psychoacoustic"           # Perceptual enhancements
    RESTORATION = "restoration"                 # Audio restoration
    MASTERING = "mastering"                     # Final mastering processing


class NoiseReductionAlgorithm(Enum):
    """Noise reduction algorithms"""

    SPECTRAL_SUBTRACTION = "spectral_subtraction"
    WIENER_FILTERING = "wiener_filtering"
    KALMAN_FILTERING = "kalman_filtering"
    ADAPTIVE_FILTERING = "adaptive_filtering"
    NEURAL_NETWORK = "neural_network"
    RNNOISE = "rnnoise"                        # RNNoise algorithm
    DEEP_NOISE_SUPPRESSION = "dns"             # Microsoft DNS
    META_DENOISER = "meta_denoiser"            # Meta's Denoiser


class EqualizerType(Enum):
    """Equalizer types"""

    PARAMETRIC = "parametric"                   # Parametric EQ
    GRAPHIC = "graphic"                         # Graphic EQ
    SHELVING = "shelving"                       # High/Low shelf filters
    LINEAR_PHASE = "linear_phase"               # Linear phase EQ
    MINIMUM_PHASE = "minimum_phase"             # Minimum phase EQ
    DYNAMIC = "dynamic"                         # Dynamic EQ
    MULTIBAND = "multiband"                     # Multiband EQ


class DynamicsProcessorType(Enum):
    """Dynamics processor types"""

    COMPRESSOR = "compressor"                   # Standard compressor
    LIMITER = "limiter"                         # Peak limiter
    EXPANDER = "expander"                       # Downward expander
    GATE = "gate"                              # Noise gate
    MULTIBAND_COMPRESSOR = "multiband_comp"    # Multiband compressor
    DYNAMIC_EQ = "dynamic_eq"                  # Dynamic equalizer
    DE_ESSER = "de_esser"                      # De-esser
    LEVELING_AMPLIFIER = "leveling_amp"        # Leveling amplifier


class SpatialAudioType(Enum):
    """Spatial audio processing types"""

    STEREO_WIDENING = "stereo_widening"        # Stereo field widening
    BINAURAL = "binaural"                      # Binaural processing
    SURROUND_UPMIX = "surround_upmix"         # Surround sound upmixing
    AMBISONICS = "ambisonics"                  # Ambisonics encoding
    HRTF_PROCESSING = "hrtf"                   # Head-related transfer function
    CROSSFEED = "crossfeed"                    # Headphone crossfeed
    ROOM_SIMULATION = "room_simulation"        # Virtual room acoustics


class ProcessingQuality(Enum):
    """Processing quality levels"""

    DRAFT = "draft"                            # Fast, low quality
    GOOD = "good"                              # Balanced quality/speed
    HIGH = "high"                              # High quality
    ULTRA = "ultra"                            # Ultra high quality
    BROADCAST = "broadcast"                    # Broadcast quality
    MASTERING = "mastering"                    # Mastering quality


@dataclass
class NoiseReductionConfig:
    """Noise reduction configuration"""
    enabled: bool = True
    algorithm: NoiseReductionAlgorithm = NoiseReductionAlgorithm.NEURAL_NETWORK
    strength: float = 0.7                      # 0.0 to 1.0
    preserve_speech: bool = True
    noise_floor_db: float = -60.0
    learning_rate: float = 0.01
    frame_size: int = 1024
    hop_size: int = 256
    frequency_smoothing: float = 0.8
    time_smoothing: float = 0.9
    voice_activity_detection: bool = True
    noise_profile_adaptation: bool = True


@dataclass
class EqualizerBand:
    """
Individual equalizer band configuration"""
    frequency: float                           # Center frequency in Hz
    gain_db: float                            # Gain in dB
    q_factor: float                           # Q factor (bandwidth)
    filter_type: str = "bell"                 # bell, highpass, lowpass, notch
    enabled: bool = True


@dataclass
class EqualizerConfig:
    """Equalizer configuration"""
    enabled: bool = True
    eq_type: EqualizerType = EqualizerType.PARAMETRIC
    bands: List[EqualizerBand] = field(default_factory=list)
    auto_gain_compensation: bool = True
    linear_phase: bool = False
    oversampling: int = 1
    quality: ProcessingQuality = ProcessingQuality.HIGH
    presets: Dict[str, List[EqualizerBand]] = field(default_factory=dict)


@dataclass
class DynamicsConfig:
    """
Dynamics processor configuration"""
    enabled: bool = True
    processor_type: DynamicsProcessorType = DynamicsProcessorType.COMPRESSOR
    threshold_db: float = -20.0
    ratio: float = 4.0
    attack_ms: float = 10.0
    release_ms: float = 100.0
    knee_db: float = 2.0
    makeup_gain_db: float = 0.0
    auto_makeup_gain: bool = True
    lookahead_ms: float = 0.0
    rms_window_ms: float = 10.0
    side_chain_enabled: bool = False
    side_chain_frequency: Optional[float] = None


@dataclass
class SpatialAudioConfig:
    """
Spatial audio processing configuration"""
    enabled: bool = False
    processing_type: SpatialAudioType = SpatialAudioType.STEREO_WIDENING
    width_factor: float = 1.5                 # 0.0 to 2.0
    depth_factor: float = 1.0                 # 0.0 to 2.0
    center_frequency: float = 250.0           # Frequency below which mono is preserved
    crossfeed_strength: float = 0.3           # For headphone listening
    room_size: float = 0.5                    # Virtual room size
    reverb_amount: float = 0.2                # Reverb amount
    hrtf_profile: str = "generic"             # HRTF profile name


@dataclass
class HarmonicEnhancementConfig:
    """Harmonic enhancement configuration"""
    enabled: bool = False
    enhancement_type: str = "tube_saturation"  # tube_saturation, tape_saturation, exciter
    drive: float = 0.3                        # 0.0 to 1.0
    harmonics_level: float = 0.2              # Amount of harmonics
    frequency_range: Tuple[float, float] = (1000.0, 8000.0)
    even_harmonics: float = 0.7               # Even harmonics emphasis
    odd_harmonics: float = 0.3                # Odd harmonics emphasis
    preserve_transients: bool = True


class AudioEnhancementConfig:
    """
    Comprehensive audio enhancement configuration manager
    
    Manages all aspects of audio enhancement including noise reduction,
    equalization, dynamics processing, spatial audio, and AI-based enhancements.
    """
    
    def __init__(self):
        """
Initialize audio enhancement configuration"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core enhancement components
        self.noise_reduction = NoiseReductionConfig()
        self.equalizer = EqualizerConfig()
        self.dynamics = DynamicsConfig()
        self.spatial_audio = SpatialAudioConfig()
        self.harmonic_enhancement = HarmonicEnhancementConfig()
        
        # Processing chain order
        self._processing_chain_order = [
            "noise_reduction",
            "restoration",
            "equalizer",
            "dynamics",
            "harmonic_enhancement",
            "spatial_audio",
            "mastering"
        ]
        
        # Enhancement presets
        self._enhancement_presets = self._initialize_enhancement_presets()
        
        # Platform-specific enhancement profiles
        self._platform_profiles = self._initialize_platform_profiles()
        
        # AI-based enhancement models
        self._ai_models = self._initialize_ai_models()
        
        # Real-time processing capabilities
        self._realtime_config = self._initialize_realtime_config()
        
        # Initialize EQ presets
        self._initialize_eq_presets()
        
        self.logger.info("AudioEnhancementConfig initialized successfully")
    
    def _initialize_enhancement_presets(self) -> Dict[str, Dict[str, Any]]:
        """Initialize enhancement presets"""
        return {
            "voice_clarity": {
                "name": "Voice Clarity",
                "description": "Optimized for speech and vocal clarity",
                "components": {
                    "noise_reduction": {
                        "enabled": True,
                        "algorithm": NoiseReductionAlgorithm.NEURAL_NETWORK.value,
                        "strength": 0.8,
                        "preserve_speech": True
                    },
                    "equalizer": {
                        "enabled": True,
                        "preset": "voice_clarity"
                    },
                    "dynamics": {
                        "enabled": True,
                        "processor_type": DynamicsProcessorType.COMPRESSOR.value,
                        "threshold_db": -18.0,
                        "ratio": 3.0,
                        "attack_ms": 5.0,
                        "release_ms": 50.0
                    }
                }
            },
            "music_enhancement": {
                "name": "Music Enhancement",
                "description": "Professional music enhancement preset",
                "components": {
                    "noise_reduction": {
                        "enabled": True,
                        "algorithm": NoiseReductionAlgorithm.SPECTRAL_SUBTRACTION.value,
                        "strength": 0.4
                    },
                    "equalizer": {
                        "enabled": True,
                        "preset": "music_enhancement"
                    },
                    "dynamics": {
                        "enabled": True,
                        "processor_type": DynamicsProcessorType.MULTIBAND_COMPRESSOR.value,
                        "threshold_db": -16.0,
                        "ratio": 2.5
                    },
                    "harmonic_enhancement": {
                        "enabled": True,
                        "enhancement_type": "tube_saturation",
                        "drive": 0.2
                    },
                    "spatial_audio": {
                        "enabled": True,
                        "processing_type": SpatialAudioType.STEREO_WIDENING.value,
                        "width_factor": 1.3
                    }
                }
            },
            "podcast_production": {
                "name": "Podcast Production",
                "description": "Optimized for podcast production",
                "components": {
                    "noise_reduction": {
                        "enabled": True,
                        "algorithm": NoiseReductionAlgorithm.RNNOISE.value,
                        "strength": 0.7
                    },
                    "equalizer": {
                        "enabled": True,
                        "preset": "podcast_voice"
                    },
                    "dynamics": {
                        "enabled": True,
                        "processor_type": DynamicsProcessorType.LEVELING_AMPLIFIER.value,
                        "threshold_db": -20.0,
                        "ratio": 10.0
                    }
                }
            },
            "gaming_audio": {
                "name": "Gaming Audio",
                "description": "Enhanced for gaming and real-time communication",
                "components": {
                    "noise_reduction": {
                        "enabled": True,
                        "algorithm": NoiseReductionAlgorithm.DEEP_NOISE_SUPPRESSION.value,
                        "strength": 0.9
                    },
                    "spatial_audio": {
                        "enabled": True,
                        "processing_type": SpatialAudioType.BINAURAL.value,
                        "width_factor": 1.8
                    },
                    "dynamics": {
                        "enabled": True,
                        "processor_type": DynamicsProcessorType.LIMITER.value,
                        "threshold_db": -6.0
                    }
                }
            },
            "live_streaming": {
                "name": "Live Streaming",
                "description": "Optimized for live streaming applications",
                "components": {
                    "noise_reduction": {
                        "enabled": True,
                        "algorithm": NoiseReductionAlgorithm.ADAPTIVE_FILTERING.value,
                        "strength": 0.6
                    },
                    "equalizer": {
                        "enabled": True,
                        "preset": "broadcast"
                    },
                    "dynamics": {
                        "enabled": True,
                        "processor_type": DynamicsProcessorType.COMPRESSOR.value,
                        "threshold_db": -12.0,
                        "ratio": 4.0,
                        "attack_ms": 3.0,
                        "release_ms": 25.0
                    }
                }
            },
            "audiophile": {
                "name": "Audiophile",
                "description": "Minimal processing for high-fidelity audio",
                "components": {
                    "noise_reduction": {
                        "enabled": False
                    },
                    "equalizer": {
                        "enabled": True,
                        "eq_type": EqualizerType.LINEAR_PHASE.value,
                        "preset": "transparent"
                    },
                    "dynamics": {
                        "enabled": False
                    },
                    "harmonic_enhancement": {
                        "enabled": True,
                        "enhancement_type": "tube_saturation",
                        "drive": 0.1
                    }
                }
            },
            "restoration": {
                "name": "Audio Restoration",
                "description": "Heavy processing for damaged audio restoration",
                "components": {
                    "noise_reduction": {
                        "enabled": True,
                        "algorithm": NoiseReductionAlgorithm.WIENER_FILTERING.value,
                        "strength": 0.9
                    },
                    "equalizer": {
                        "enabled": True,
                        "preset": "restoration"
                    },
                    "dynamics": {
                        "enabled": True,
                        "processor_type": DynamicsProcessorType.EXPANDER.value,
                        "threshold_db": -40.0,
                        "ratio": 2.0
                    },
                    "harmonic_enhancement": {
                        "enabled": True,
                        "enhancement_type": "exciter",
                        "drive": 0.4
                    }
                }
            }
        }
    
    def _initialize_platform_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific enhancement profiles"""
        return {
            "spotify": {
                "name": "Spotify Optimization",
                "loudness_target": -14.0,  # LUFS
                "peak_limit": -1.0,        # dBFS
                "dynamic_range_target": 8.0, # LU
                "enhancement_strength": 0.6,
                "spatial_processing": True
            },
            "apple_music": {
                "name": "Apple Music Optimization",
                "loudness_target": -16.0,  # LUFS
                "peak_limit": -1.0,        # dBFS
                "dynamic_range_target": 10.0, # LU
                "enhancement_strength": 0.5,
                "spatial_audio_support": True,
                "atmos_processing": True
            },
            "youtube": {
                "name": "YouTube Optimization",
                "loudness_target": -14.0,  # LUFS
                "peak_limit": -1.0,        # dBFS
                "voice_enhancement": True,
                "background_music_ducking": True,
                "dialogue_clarity": True
            },
            "tiktok": {
                "name": "TikTok Optimization",
                "loudness_target": -12.0,  # LUFS (louder for mobile)
                "peak_limit": -0.5,        # dBFS
                "bass_enhancement": True,
                "vocal_clarity": True,
                "mobile_optimization": True
            },
            "instagram": {
                "name": "Instagram Optimization",
                "loudness_target": -13.0,  # LUFS
                "peak_limit": -0.8,        # dBFS
                "story_optimization": True,
                "reel_optimization": True,
                "live_optimization": True
            },
            "twitch": {
                "name": "Twitch Streaming",
                "real_time_processing": True,
                "low_latency_mode": True,
                "voice_priority": True,
                "game_audio_separation": True,
                "chat_audio_integration": True
            },
            "discord": {
                "name": "Discord Voice",
                "real_time_processing": True,
                "ultra_low_latency": True,
                "voice_activity_detection": True,
                "echo_cancellation": True,
                "noise_suppression_aggressive": True
            },
            "podcast": {
                "name": "Podcast Production",
                "speech_optimization": True,
                "loudness_target": -19.0,  # LUFS for podcasts
                "consistency_processing": True,
                "chapter_processing": True,
                "intro_outro_processing": True
            }
        }
    
    def _initialize_ai_models(self) -> Dict[str, Dict[str, Any]]:
        """Initialize AI-based enhancement models"""
        return {
            "facebook_denoiser": {
                "name": "Meta Denoiser",
                "type": "noise_reduction",
                "model_path": "models/facebook_denoiser.pth",
                "input_format": "16khz_mono",
                "processing_time_ms": 50,
                "quality_score": 0.95,
                "use_cases": ["voice", "music", "general"]
            },
            "rnnoise": {
                "name": "RNNoise",
                "type": "noise_reduction",
                "model_path": "models/rnnoise.onnx",
                "input_format": "48khz_mono",
                "processing_time_ms": 20,
                "quality_score": 0.88,
                "use_cases": ["voice", "real_time"]
            },
            "neural_eq": {
                "name": "Neural EQ",
                "type": "equalization",
                "model_path": "models/neural_eq.onnx",
                "input_format": "44khz_stereo",
                "processing_time_ms": 100,
                "quality_score": 0.92,
                "use_cases": ["music", "mastering"]
            },
            "ai_mastering": {
                "name": "AI Mastering",
                "type": "mastering",
                "model_path": "models/ai_mastering.pth",
                "input_format": "48khz_stereo",
                "processing_time_ms": 200,
                "quality_score": 0.94,
                "use_cases": ["music", "podcast", "mastering"]
            },
            "speech_enhancement": {
                "name": "Speech Enhancement AI",
                "type": "speech_enhancement",
                "model_path": "models/speech_enhancement.onnx",
                "input_format": "16khz_mono",
                "processing_time_ms": 30,
                "quality_score": 0.91,
                "use_cases": ["voice", "podcast", "call"]
            },
            "music_separation": {
                "name": "Music Source Separation",
                "type": "source_separation",
                "model_path": "models/music_separation.pth",
                "input_format": "44khz_stereo",
                "processing_time_ms": 500,
                "quality_score": 0.89,
                "use_cases": ["music", "karaoke", "remix"]
            }
        }
    
    def _initialize_realtime_config(self) -> Dict[str, Any]:
        """Initialize real-time processing configuration"""
        return {
            "enabled": True,
            "max_latency_ms": 20,
            "buffer_size": 512,
            "sample_rate": 48000,
            "bit_depth": 32,
            "channels": 2,
            "processing_threads": 4,
            "gpu_acceleration": True,
            "cpu_priority": "high",
            "memory_limit_mb": 512,
            "quality_vs_speed_balance": 0.7,  # 0.0 = speed, 1.0 = quality
            "adaptive_processing": True,
            "load_monitoring": True
        }
    
    def _initialize_eq_presets(self):
        """Initialize equalizer presets"""
        self.equalizer.presets = {
            "voice_clarity": [
                EqualizerBand(frequency=80, gain_db=-6, q_factor=0.7, filter_type="highpass"),
                EqualizerBand(frequency=200, gain_db=-2, q_factor=1.0),
                EqualizerBand(frequency=1000, gain_db=2, q_factor=0.8),
                EqualizerBand(frequency=3000, gain_db=3, q_factor=0.9),
                EqualizerBand(frequency=5000, gain_db=2, q_factor=1.2),
                EqualizerBand(frequency=10000, gain_db=-1, q_factor=0.7)
            ],
            "music_enhancement": [
                EqualizerBand(frequency=60, gain_db=1, q_factor=0.7),
                EqualizerBand(frequency=200, gain_db=-1, q_factor=1.0),
                EqualizerBand(frequency=1000, gain_db=0, q_factor=0.8),
                EqualizerBand(frequency=4000, gain_db=1, q_factor=0.9),
                EqualizerBand(frequency=8000, gain_db=2, q_factor=1.0),
                EqualizerBand(frequency=16000, gain_db=1, q_factor=0.8)
            ],
            "podcast_voice": [
                EqualizerBand(frequency=100, gain_db=-4, q_factor=0.7, filter_type="highpass"),
                EqualizerBand(frequency=300, gain_db=-1, q_factor=1.0),
                EqualizerBand(frequency=1500, gain_db=2, q_factor=0.8),
                EqualizerBand(frequency=3000, gain_db=3, q_factor=1.0),
                EqualizerBand(frequency=6000, gain_db=1, q_factor=1.2),
                EqualizerBand(frequency=8000, gain_db=-1, q_factor=0.8, filter_type="lowpass")
            ],
            "broadcast": [
                EqualizerBand(frequency=80, gain_db=-3, q_factor=0.7, filter_type="highpass"),
                EqualizerBand(frequency=200, gain_db=-1, q_factor=1.0),
                EqualizerBand(frequency=1000, gain_db=1, q_factor=0.8),
                EqualizerBand(frequency=2500, gain_db=2, q_factor=0.9),
                EqualizerBand(frequency=5000, gain_db=1, q_factor=1.0),
                EqualizerBand(frequency=10000, gain_db=0, q_factor=0.8)
            ],
            "transparent": [
                EqualizerBand(frequency=20, gain_db=0, q_factor=0.7),
                EqualizerBand(frequency=200, gain_db=0, q_factor=1.0),
                EqualizerBand(frequency=1000, gain_db=0, q_factor=0.8),
                EqualizerBand(frequency=5000, gain_db=0, q_factor=1.0),
                EqualizerBand(frequency=20000, gain_db=0, q_factor=0.7)
            ],
            "restoration": [
                EqualizerBand(frequency=50, gain_db=-8, q_factor=1.0, filter_type="highpass"),
                EqualizerBand(frequency=2000, gain_db=3, q_factor=0.8),
                EqualizerBand(frequency=4000, gain_db=4, q_factor=1.0),
                EqualizerBand(frequency=8000, gain_db=3, q_factor=1.2),
                EqualizerBand(frequency=12000, gain_db=2, q_factor=0.9)
            ]
        }
    
    def get_enhancement_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get enhancement preset by name
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset configuration or None if not found
        """
        return self._enhancement_presets.get(preset_name)
    
    def get_platform_profile(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get platform-specific profile
        
        Args:
            platform: Platform name
            
        Returns:
            Platform profile or None if not found
        """
        return self._platform_profiles.get(platform.lower())
    
    def apply_enhancement_preset(self, preset_name: str) -> bool:
        """
        Apply enhancement preset to current configuration
        
        Args:
            preset_name: Name of the preset to apply
            
        Returns:
            Success status
        """
        try:
            preset = self.get_enhancement_preset(preset_name)
            if not preset:
                self.logger.error(f"Preset '{preset_name}' not found")
                return False
            
            components = preset.get("components", {})
            
            # Apply noise reduction settings
            if "noise_reduction" in components:
                nr_config = components["noise_reduction"]
                self.noise_reduction.enabled = nr_config.get("enabled", True)
                if "algorithm" in nr_config:
                    self.noise_reduction.algorithm = NoiseReductionAlgorithm(nr_config["algorithm"])
                self.noise_reduction.strength = nr_config.get("strength", 0.7)
                self.noise_reduction.preserve_speech = nr_config.get("preserve_speech", True)
            
            # Apply equalizer settings
            if "equalizer" in components:
                eq_config = components["equalizer"]
                self.equalizer.enabled = eq_config.get("enabled", True)
                if "preset" in eq_config:
                    eq_preset_name = eq_config["preset"]
                    if eq_preset_name in self.equalizer.presets:
                        self.equalizer.bands = self.equalizer.presets[eq_preset_name].copy()
                if "eq_type" in eq_config:
                    self.equalizer.eq_type = EqualizerType(eq_config["eq_type"])
            
            # Apply dynamics settings
            if "dynamics" in components:
                dyn_config = components["dynamics"]
                self.dynamics.enabled = dyn_config.get("enabled", True)
                if "processor_type" in dyn_config:
                    self.dynamics.processor_type = DynamicsProcessorType(dyn_config["processor_type"])
                self.dynamics.threshold_db = dyn_config.get("threshold_db", -20.0)
                self.dynamics.ratio = dyn_config.get("ratio", 4.0)
                self.dynamics.attack_ms = dyn_config.get("attack_ms", 10.0)
                self.dynamics.release_ms = dyn_config.get("release_ms", 100.0)
            
            # Apply spatial audio settings
            if "spatial_audio" in components:
                spatial_config = components["spatial_audio"]
                self.spatial_audio.enabled = spatial_config.get("enabled", False)
                if "processing_type" in spatial_config:
                    self.spatial_audio.processing_type = SpatialAudioType(spatial_config["processing_type"])
                self.spatial_audio.width_factor = spatial_config.get("width_factor", 1.5)
                self.spatial_audio.depth_factor = spatial_config.get("depth_factor", 1.0)
            
            # Apply harmonic enhancement settings
            if "harmonic_enhancement" in components:
                harm_config = components["harmonic_enhancement"]
                self.harmonic_enhancement.enabled = harm_config.get("enabled", False)
                self.harmonic_enhancement.enhancement_type = harm_config.get("enhancement_type", "tube_saturation")
                self.harmonic_enhancement.drive = harm_config.get("drive", 0.3)
            
            self.logger.info(f"Applied enhancement preset: {preset_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply preset '{preset_name}': {e}")
            return False
    
    def create_custom_preset(self, 
                           name: str,
                           description: str,
                           components: Dict[str, Any]) -> bool:
        """
        Create custom enhancement preset
        
        Args:
            name: Preset name
            description: Preset description
            components: Enhancement components configuration
            
        Returns:
            Success status
        """
        try:
            self._enhancement_presets[name] = {
                "name": name,
                "description": description,
                "components": components,
                "custom": True
            }
            
            self.logger.info(f"Created custom preset: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create custom preset: {e}")
            return False
    
    def optimize_for_platform(self, platform: str) -> bool:
        """
        Optimize enhancement settings for specific platform
        
        Args:
            platform: Target platform name
            
        Returns:
            Success status
        """
        try:
            profile = self.get_platform_profile(platform)
            if not profile:
                self.logger.warning(f"No profile found for platform: {platform}")
                return False
            
            # Apply platform-specific optimizations
            if "loudness_target" in profile:
                # Adjust dynamics processing for target loudness
                self.dynamics.enabled = True
                # Calculate threshold based on loudness target
                target_lufs = profile["loudness_target"]
                self.dynamics.threshold_db = max(-30.0, target_lufs + 6.0)
            
            if "enhancement_strength" in profile:
                # Adjust overall enhancement strength
                strength = profile["enhancement_strength"]
                self.noise_reduction.strength = min(1.0, self.noise_reduction.strength * strength)
                if self.harmonic_enhancement.enabled:
                    self.harmonic_enhancement.drive = min(1.0, self.harmonic_enhancement.drive * strength)
            
            if "spatial_processing" in profile and profile["spatial_processing"]:
                self.spatial_audio.enabled = True
                self.spatial_audio.processing_type = SpatialAudioType.STEREO_WIDENING
            
            if "voice_enhancement" in profile and profile["voice_enhancement"]:
                # Apply voice-optimized EQ preset
                if "voice_clarity" in self.equalizer.presets:
                    self.equalizer.bands = self.equalizer.presets["voice_clarity"].copy()
                    self.equalizer.enabled = True
            
            if "real_time_processing" in profile and profile["real_time_processing"]:
                # Optimize for real-time processing
                self._realtime_config["enabled"] = True
                self._realtime_config["max_latency_ms"] = 15
                self._realtime_config["quality_vs_speed_balance"] = 0.3
            
            self.logger.info(f"Optimized for platform: {platform}")
            return True
            
        except Exception as e:
            self.logger.error(f"Platform optimization failed: {e}")
            return False
    
    def get_ai_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get AI model configuration
        
        Args:
            model_name: Name of the AI model
            
        Returns:
            Model configuration or None if not found
        """
        return self._ai_models.get(model_name)
    
    def estimate_processing_latency(self, 
                                  enabled_components: List[str],
                                  sample_rate: int = 48000,
                                  buffer_size: int = 512,
                                  use_ai_models: bool = False) -> Dict[str, Any]:
        """
        Estimate processing latency for current configuration
        
        Args:
            enabled_components: List of enabled enhancement components
            sample_rate: Audio sample rate
            buffer_size: Processing buffer size
            use_ai_models: Whether AI models are being used
            
        Returns:
            Latency estimation breakdown
        """
        try:
            # Base latencies for different components (in milliseconds)
            component_latencies = {
                "noise_reduction": 5 if not use_ai_models else 30,
                "equalizer": 1,
                "dynamics": 2,
                "spatial_audio": 3,
                "harmonic_enhancement": 2,
                "restoration": 10,
                "mastering": 15
            }
            
            # AI model additional latencies
            ai_latencies = {
                "facebook_denoiser": 50,
                "rnnoise": 20,
                "neural_eq": 100,
                "ai_mastering": 200,
                "speech_enhancement": 30,
                "music_separation": 500
            }
            
            # Calculate buffer latency
            buffer_latency_ms = (buffer_size / sample_rate) * 1000
            
            # Calculate processing latency
            total_processing_latency = 0
            component_breakdown = {}
            
            for component in enabled_components:
                latency = component_latencies.get(component, 0)
                component_breakdown[component] = latency
                total_processing_latency += latency
            
            # Add AI model latencies if applicable
            ai_breakdown = {}
            if use_ai_models:
                for model_name, model_config in self._ai_models.items():
                    if any(component in enabled_components 
                          for component in [model_config["type"]]):
                        ai_latency = model_config["processing_time_ms"]
                        ai_breakdown[model_name] = ai_latency
                        total_processing_latency += ai_latency
            
            # Calculate total latency
            total_latency = buffer_latency_ms * 2 + total_processing_latency  # 2x buffer for I/O
            
            return {
                "total_latency_ms": total_latency,
                "buffer_latency_ms": buffer_latency_ms * 2,
                "processing_latency_ms": total_processing_latency,
                "component_breakdown": component_breakdown,
                "ai_model_breakdown": ai_breakdown,
                "real_time_capable": total_latency < 20,
                "low_latency_capable": total_latency < 50,
                "sample_rate": sample_rate,
                "buffer_size": buffer_size,
                "recommendation": self._get_latency_recommendation(total_latency)
            }
            
        except Exception as e:
            self.logger.error(f"Latency estimation failed: {e}")
            return {"error": str(e)}
    
    def _get_latency_recommendation(self, total_latency: float) -> str:
        """Get recommendation based on total latency"""
        if total_latency < 10:
            return "Excellent for real-time applications"
        elif total_latency < 20:
            return "Good for real-time applications"
        elif total_latency < 50:
            return "Suitable for most applications, not ideal for real-time"
        elif total_latency < 100:
            return "High latency - consider reducing processing complexity"
        else:
            return "Very high latency - significant optimization needed"
    
    def create_processing_chain(self, 
                              use_case: str,
                              quality_level: ProcessingQuality = ProcessingQuality.HIGH,
                              real_time: bool = False) -> Dict[str, Any]:
        """
        Create optimized processing chain for use case
        
        Args:
            use_case: Audio processing use case
            quality_level: Desired quality level
            real_time: Whether real-time processing is required
            
        Returns:
            Processing chain configuration
        """
        try:
            # Define processing chains for different use cases
            use_case_chains = {
                "voice_communication": ["noise_reduction", "equalizer", "dynamics"],
                "music_production": ["noise_reduction", "equalizer", "dynamics", "harmonic_enhancement", "spatial_audio"],
                "podcast_production": ["noise_reduction", "equalizer", "dynamics"],
                "live_streaming": ["noise_reduction", "equalizer", "dynamics"],
                "audio_restoration": ["noise_reduction", "restoration", "equalizer", "dynamics", "harmonic_enhancement"],
                "mastering": ["equalizer", "dynamics", "harmonic_enhancement", "spatial_audio", "mastering"],
                "gaming": ["noise_reduction", "spatial_audio", "dynamics"],
                "broadcasting": ["noise_reduction", "equalizer", "dynamics"]
            }
            
            # Get base chain for use case
            base_chain = use_case_chains.get(use_case.lower(), ["noise_reduction", "equalizer", "dynamics"])
            
            # Adjust chain based on quality level and real-time requirements
            if real_time and quality_level in [ProcessingQuality.DRAFT, ProcessingQuality.GOOD]:
                # Remove heavy processing for real-time
                base_chain = [comp for comp in base_chain if comp not in ["mastering", "restoration"]]
            elif quality_level in [ProcessingQuality.BROADCAST, ProcessingQuality.MASTERING]:
                # Add comprehensive processing for high quality
                if "mastering" not in base_chain:
                    base_chain.append("mastering")
                if use_case.lower() in ["music_production", "mastering"]:
                    if "spatial_audio" not in base_chain:
                        base_chain.append("spatial_audio")
            
            # Configure each component
            chain_config = {
                "use_case": use_case,
                "quality_level": quality_level.value,
                "real_time_processing": real_time,
                "processing_order": base_chain,
                "components": {}
            }
            
            # Configure individual components based on use case
            for component in base_chain:
                if component == "noise_reduction":
                    config = {
                        "enabled": True,
                        "algorithm": NoiseReductionAlgorithm.NEURAL_NETWORK.value if not real_time 
                                   else NoiseReductionAlgorithm.SPECTRAL_SUBTRACTION.value,
                        "strength": 0.7 if "voice" in use_case.lower() else 0.5
                    }
                elif component == "equalizer":
                    preset_map = {
                        "voice_communication": "voice_clarity",
                        "podcast_production": "podcast_voice",
                        "music_production": "music_enhancement",
                        "broadcasting": "broadcast"
                    }
                    config = {
                        "enabled": True,
                        "preset": preset_map.get(use_case.lower(), "transparent"),
                        "eq_type": EqualizerType.PARAMETRIC.value
                    }
                elif component == "dynamics":
                    if "voice" in use_case.lower() or "podcast" in use_case.lower():
                        config = {
                            "enabled": True,
                            "processor_type": DynamicsProcessorType.COMPRESSOR.value,
                            "threshold_db": -18.0,
                            "ratio": 3.0,
                            "attack_ms": 5.0,
                            "release_ms": 50.0
                        }
                    else:
                        config = {
                            "enabled": True,
                            "processor_type": DynamicsProcessorType.MULTIBAND_COMPRESSOR.value,
                            "threshold_db": -16.0,
                            "ratio": 2.5,
                            "attack_ms": 10.0,
                            "release_ms": 100.0
                        }
                elif component == "spatial_audio":
                    config = {
                        "enabled": True,
                        "processing_type": SpatialAudioType.STEREO_WIDENING.value,
                        "width_factor": 1.5 if "music" in use_case.lower() else 1.2
                    }
                elif component == "harmonic_enhancement":
                    config = {
                        "enabled": True,
                        "enhancement_type": "tube_saturation",
                        "drive": 0.3 if quality_level == ProcessingQuality.MASTERING else 0.2
                    }
                else:
                    config = {"enabled": True}
                
                chain_config["components"][component] = config
            
            # Add performance estimates
            latency_estimate = self.estimate_processing_latency(
                base_chain, use_ai_models=(quality_level == ProcessingQuality.MASTERING)
            )
            chain_config["performance"] = latency_estimate
            
            return chain_config
            
        except Exception as e:
            self.logger.error(f"Processing chain creation failed: {e}")
            return {"error": str(e)}
    
    def validate_enhancement_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate enhancement configuration
        
        Args:
            config: Enhancement configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        is_valid = True
        
        try:
            # Validate noise reduction
            if "noise_reduction" in config:
                nr_config = config["noise_reduction"]
                if "strength" in nr_config:
                    strength = nr_config["strength"]
                    if not (0.0 <= strength <= 1.0):
                        errors.append("Noise reduction strength must be between 0.0 and 1.0")
                        is_valid = False
            
            # Validate equalizer
            if "equalizer" in config:
                eq_config = config["equalizer"]
                if "bands" in eq_config:
                    for i, band in enumerate(eq_config["bands"]):
                        if "frequency" not in band or band["frequency"] <= 0:
                            errors.append(f"EQ band {i}: frequency must be positive")
                            is_valid = False
                        if "gain_db" not in band:
                            errors.append(f"EQ band {i}: gain_db is required")
                            is_valid = False
                        elif abs(band["gain_db"]) > 24:
                            errors.append(f"EQ band {i}: gain should be within ±24 dB")
                            is_valid = False
                        if "q_factor" in band and band["q_factor"] <= 0:
                            errors.append(f"EQ band {i}: Q factor must be positive")
                            is_valid = False
            
            # Validate dynamics
            if "dynamics" in config:
                dyn_config = config["dynamics"]
                if "threshold_db" in dyn_config and dyn_config["threshold_db"] > 0:
                    errors.append("Dynamics threshold should be negative")
                    is_valid = False
                if "ratio" in dyn_config:
                    ratio = dyn_config["ratio"]
                    if ratio < 1.0 or ratio > 100.0:
                        errors.append("Dynamics ratio should be between 1.0 and 100.0")
                        is_valid = False
                if "attack_ms" in dyn_config and dyn_config["attack_ms"] < 0:
                    errors.append("Attack time must be non-negative")
                    is_valid = False
                if "release_ms" in dyn_config and dyn_config["release_ms"] < 0:
                    errors.append("Release time must be non-negative")
                    is_valid = False
            
            # Validate spatial audio
            if "spatial_audio" in config:
                spatial_config = config["spatial_audio"]
                if "width_factor" in spatial_config:
                    width = spatial_config["width_factor"]
                    if not (0.0 <= width <= 2.0):
                        errors.append("Spatial width factor should be between 0.0 and 2.0")
                        is_valid = False
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            is_valid = False
        
        return is_valid, errors
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete enhancement configuration"""
        try:
            return {
                "noise_reduction": {
                    "enabled": self.noise_reduction.enabled,
                    "algorithm": self.noise_reduction.algorithm.value,
                    "strength": self.noise_reduction.strength,
                    "preserve_speech": self.noise_reduction.preserve_speech,
                    "noise_floor_db": self.noise_reduction.noise_floor_db,
                    "learning_rate": self.noise_reduction.learning_rate,
                    "frame_size": self.noise_reduction.frame_size,
                    "hop_size": self.noise_reduction.hop_size,
                    "frequency_smoothing": self.noise_reduction.frequency_smoothing,
                    "time_smoothing": self.noise_reduction.time_smoothing,
                    "voice_activity_detection": self.noise_reduction.voice_activity_detection,
                    "noise_profile_adaptation": self.noise_reduction.noise_profile_adaptation
                },
                "equalizer": {
                    "enabled": self.equalizer.enabled,
                    "eq_type": self.equalizer.eq_type.value,
                    "bands": [
                        {
                            "frequency": band.frequency,
                            "gain_db": band.gain_db,
                            "q_factor": band.q_factor,
                            "filter_type": band.filter_type,
                            "enabled": band.enabled
                        }
                        for band in self.equalizer.bands
                    ],
                    "auto_gain_compensation": self.equalizer.auto_gain_compensation,
                    "linear_phase": self.equalizer.linear_phase,
                    "oversampling": self.equalizer.oversampling,
                    "quality": self.equalizer.quality.value,
                    "available_presets": list(self.equalizer.presets.keys())
                },
                "dynamics": {
                    "enabled": self.dynamics.enabled,
                    "processor_type": self.dynamics.processor_type.value,
                    "threshold_db": self.dynamics.threshold_db,
                    "ratio": self.dynamics.ratio,
                    "attack_ms": self.dynamics.attack_ms,
                    "release_ms": self.dynamics.release_ms,
                    "knee_db": self.dynamics.knee_db,
                    "makeup_gain_db": self.dynamics.makeup_gain_db,
                    "auto_makeup_gain": self.dynamics.auto_makeup_gain,
                    "lookahead_ms": self.dynamics.lookahead_ms,
                    "rms_window_ms": self.dynamics.rms_window_ms,
                    "side_chain_enabled": self.dynamics.side_chain_enabled,
                    "side_chain_frequency": self.dynamics.side_chain_frequency
                },
                "spatial_audio": {
                    "enabled": self.spatial_audio.enabled,
                    "processing_type": self.spatial_audio.processing_type.value,
                    "width_factor": self.spatial_audio.width_factor,
                    "depth_factor": self.spatial_audio.depth_factor,
                    "center_frequency": self.spatial_audio.center_frequency,
                    "crossfeed_strength": self.spatial_audio.crossfeed_strength,
                    "room_size": self.spatial_audio.room_size,
                    "reverb_amount": self.spatial_audio.reverb_amount,
                    "hrtf_profile": self.spatial_audio.hrtf_profile
                },
                "harmonic_enhancement": {
                    "enabled": self.harmonic_enhancement.enabled,
                    "enhancement_type": self.harmonic_enhancement.enhancement_type,
                    "drive": self.harmonic_enhancement.drive,
                    "harmonics_level": self.harmonic_enhancement.harmonics_level,
                    "frequency_range": self.harmonic_enhancement.frequency_range,
                    "even_harmonics": self.harmonic_enhancement.even_harmonics,
                    "odd_harmonics": self.harmonic_enhancement.odd_harmonics,
                    "preserve_transients": self.harmonic_enhancement.preserve_transients
                },
                "processing_chain_order": self._processing_chain_order,
                "enhancement_presets": list(self._enhancement_presets.keys()),
                "platform_profiles": list(self._platform_profiles.keys()),
                "ai_models": list(self._ai_models.keys()),
                "realtime_config": self._realtime_config
            }
        except Exception as e:
            self.logger.error(f"Config export failed: {e}")
            return {}
