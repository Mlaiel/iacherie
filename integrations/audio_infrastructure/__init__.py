"""🎵 Audio Infrastructure Module - Enterprise Implementation
========================================================

Module d'infrastructure audio enterprise avec traitement temps réel,
streaming optimization et codecs professionnels pour Ainflue.

Author: Fahed Mlaiel (mlaiel@live.de)
Date: 14 Septembre 2025
"""

from .enterprise_audio_infrastructure import (
    EnterpriseAudioInfrastructure,
    AudioConfiguration,
    AudioStream,
    AudioProcessingJob,
    AudioMetrics,
    AudioFormat,
    AudioQuality,
    ProcessingType,
    StreamingProtocol,
    initialize_audio_infrastructure
)

from .audio_watermarking_engine import (
    AudioWatermarkingEngine,
    WatermarkType,
    WatermarkStrength,
    WatermarkConfiguration,
    WatermarkPayload,
    AudioWatermarkResult,
    WatermarkDetectionResult,
    create_watermarking_engine
)

from .voice_processing_engine import (
    VoiceProcessingEngine,
    VoiceProcessingType,
    VoiceAnalysisType,
    VoiceQuality,
    EmotionType,
    VoiceConfiguration,
    VoiceBiometrics,
    EmotionAnalysis,
    VoiceQualityMetrics,
    VoiceProcessingResult,
    create_voice_processing_engine
)

from .music_generation_engine import (
    MusicGenerationEngine,
    MusicGenre,
    MusicMood,
    MusicalStructure,
    InstrumentType,
    CompositionComplexity,
    MusicGenerationConfig,
    MusicComposition,
    HarmonicProgression,
    MelodicPhrase,
    RhythmPattern,
    create_music_generation_engine,
    create_music_config
)

from .audio_format_converter import (
    AudioFormatConverter,
    AudioCodec,
    ConversionQuality,
    PlatformTarget,
    ConversionMode,
    AudioFormatSpec,
    ConversionConfig,
    ConversionResult,
    BatchConversionJob,
    PlatformSpecs,
    create_audio_format_converter,
    create_conversion_config
)

from .audio_analytics_engine import (
    AudioAnalyticsEngine,
    AnalysisType,
    AudioGenre as AnalyticsAudioGenre,
    AudioMood as AnalyticsAudioMood,
    MarketSegment,
    AudioFeatures,
    GenreClassification,
    MoodAnalysis,
    CommercialViability,
    PerformancePrediction,
    AudioAnalyticsResult,
    create_audio_analytics_engine
)

__version__ = "2.2.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core Infrastructure
    "EnterpriseAudioInfrastructure",
    "AudioConfiguration",
    "AudioStream",
    "AudioProcessingJob",
    "AudioMetrics",
    "AudioFormat",
    "AudioQuality",
    "ProcessingType",
    "StreamingProtocol",
    "initialize_audio_infrastructure",
    
    # Audio Watermarking
    "AudioWatermarkingEngine",
    "WatermarkType",
    "WatermarkStrength",
    "WatermarkConfiguration",
    "WatermarkPayload",
    "AudioWatermarkResult",
    "WatermarkDetectionResult",
    "create_watermarking_engine",
    
    # Voice Processing
    "VoiceProcessingEngine",
    "VoiceProcessingType",
    "VoiceAnalysisType",
    "VoiceQuality",
    "EmotionType",
    "VoiceConfiguration",
    "VoiceBiometrics",
    "EmotionAnalysis",
    "VoiceQualityMetrics",
    "VoiceProcessingResult",
    "create_voice_processing_engine",
    
    # Music Generation
    "MusicGenerationEngine",
    "MusicGenre",
    "MusicMood",
    "MusicalStructure",
    "InstrumentType",
    "CompositionComplexity",
    "MusicGenerationConfig",
    "MusicComposition",
    "HarmonicProgression",
    "MelodicPhrase",
    "RhythmPattern",
    "create_music_generation_engine",
    "create_music_config",
    
    # Audio Format Converter
    "AudioFormatConverter",
    "AudioCodec",
    "ConversionQuality",
    "PlatformTarget",
    "ConversionMode",
    "AudioFormatSpec",
    "ConversionConfig",
    "ConversionResult",
    "BatchConversionJob",
    "PlatformSpecs",
    "create_audio_format_converter",
    "create_conversion_config",
    
    # Audio Analytics
    "AudioAnalyticsEngine",
    "AnalysisType",
    "AnalyticsAudioGenre",
    "AnalyticsAudioMood",
    "MarketSegment",
    "AudioFeatures",
    "GenreClassification",
    "MoodAnalysis",
    "CommercialViability",
    "PerformancePrediction",
    "AudioAnalyticsResult",
    "create_audio_analytics_engine"
]