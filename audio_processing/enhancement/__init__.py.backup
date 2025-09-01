"""Audio Enhancement Module
========================

Professional audio enhancement system for content creators, musicians, and influencers.
This module provides comprehensive audio quality improvement capabilities including
noise reduction, spectral enhancement, dynamic range optimization, and real-time processing.

Key Features:
- Industrial-grade audio enhancement processing
- Real-time audio processing with ultra-low latency
- Comprehensive quality analysis and metrics
- Adaptive parameter configuration and presets
- Multi-pass and quality-guided processing pipelines
- Professional mastering and restoration tools

Components:
- AudioEnhancementProcessor: Core enhancement engine
- RealTimeEnhancer: Real-time processing system
- AudioQualityAnalyzer: Quality metrics and analysis
- EnhancementConfigManager: Configuration and presets
- AudioEnhancementPipeline: Orchestration system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will be prosecuted to the full extent of the law.
"""
from .processor import (
    AudioEnhancementProcessor,
    EnhancementParameters,
    EnhancementResult,
    EnhancementType,
    ContentType,
    SpectralEnhancer,
    NoiseReducer,
    DynamicRangeOptimizer
)

from .realtime import (
    RealTimeEnhancer,
    RealTimeConfig,
    ProcessingMode,
    LatencyMetrics,
    AudioBuffer
)

from .quality_analyzer import (
    AudioQualityAnalyzer,
    QualityMetrics,
    QualityLevel,
    ComparisonResult,
    MetricCategory,
    PsychoacousticAnalyzer
)

from .config_manager import (
    EnhancementConfigManager,
    EnhancementPreset,
    PresetCategory,
    AdaptiveConfig
)

from .pipeline import (
    AudioEnhancementPipeline,
    PipelineConfig,
    PipelineMode,
    ProcessingTask,
    PipelineResult,
    ProcessingPriority
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core processor
    "AudioEnhancementProcessor",
    "EnhancementParameters", 
    "EnhancementResult",
    "EnhancementType",
    "ContentType",
    "SpectralEnhancer",
    "NoiseReducer", 
    "DynamicRangeOptimizer",
    
    # Real-time processing
    "RealTimeEnhancer",
    "RealTimeConfig",
    "ProcessingMode",
    "LatencyMetrics",
    "AudioBuffer",
    
    # Quality analysis
    "AudioQualityAnalyzer",
    "QualityMetrics",
    "QualityLevel",
    "ComparisonResult",
    "MetricCategory",
    "PsychoacousticAnalyzer",
    
    # Configuration management
    "EnhancementConfigManager",
    "EnhancementPreset",
    "PresetCategory", 
    "AdaptiveConfig",
    
    # Pipeline orchestration
    "AudioEnhancementPipeline",
    "PipelineConfig",
    "PipelineMode",
    "ProcessingTask",
    "PipelineResult",
    "ProcessingPriority"
]


def create_enhancement_processor(config=None):
    """Create a new audio enhancement processor instance"""
    return AudioEnhancementProcessor(config)


def create_realtime_enhancer(buffer_size=512, sample_rate=44100, channels=2, mode=ProcessingMode.BALANCED):
    """Create a new real-time audio enhancer instance"""
    config = RealTimeConfig(
        buffer_size=buffer_size,
        sample_rate=sample_rate, 
        channels=channels,
        processing_mode=mode
    )
    return RealTimeEnhancer(config)


def create_quality_analyzer():
    """Create a new audio quality analyzer instance"""
    return AudioQualityAnalyzer()


def create_config_manager(config_dir=None):
    """Create a new enhancement configuration manager instance"""
    return EnhancementConfigManager(config_dir)


def create_enhancement_pipeline(config=None, config_dir=None):
    """Create a new audio enhancement pipeline instance"""
    return AudioEnhancementPipeline(config, config_dir)


# Default configuration presets
DEFAULT_MUSIC_PARAMETERS = EnhancementParameters(
    noise_reduction_strength=0.3,
    spectral_enhancement_gain=0.4,
    dynamic_range_target=0.8,
    stereo_width=1.2,
    harmonic_emphasis=0.4,
    vocal_clarity=0.2,
    mastering_loudness_lufs=-16.0,
    restoration_strength=0.2,
    preserve_original_character=True,
    adaptive_processing=True,
    multiband_processing=True,
    high_quality_mode=True
)

DEFAULT_SPEECH_PARAMETERS = EnhancementParameters(
    noise_reduction_strength=0.7,
    spectral_enhancement_gain=0.3,
    dynamic_range_target=0.9,
    stereo_width=1.0,
    harmonic_emphasis=0.2,
    vocal_clarity=0.8,
    mastering_loudness_lufs=-18.0,
    restoration_strength=0.5,
    preserve_original_character=True,
    adaptive_processing=True,
    multiband_processing=True,
    high_quality_mode=True
)

DEFAULT_STREAMING_PARAMETERS = EnhancementParameters(
    noise_reduction_strength=0.6,
    spectral_enhancement_gain=0.3,
    dynamic_range_target=0.85,
    stereo_width=1.1,
    harmonic_emphasis=0.3,
    vocal_clarity=0.6,
    mastering_loudness_lufs=-20.0,
    restoration_strength=0.3,
    preserve_original_character=True,
    adaptive_processing=True,
    multiband_processing=False,  # Optimized for real-time
    high_quality_mode=False
)
