"""🎵 Audio Infrastructure Module - Enterprise Implementation
========================================================

Module d'infrastructure audio enterprise avec traitement temps réel,
streaming optimization et codecs professionnels pour IA Chéries.

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

from .realtime_audio_processor import (
    RealtimeAudioProcessor,
    ProcessingMode,
    AudioEffect,
    LatencyTarget,
    AudioBuffer,
    ProcessingChain,
    LatencyMetrics,
    QualityMetrics,
    RealtimeProcessingResult,
    create_realtime_processor,
    create_processing_chain
)

from .audio_streaming_optimizer import (
    AudioStreamingOptimizer,
    StreamingProtocol,
    QualityLevel,
    NetworkConditions,
    StreamingResult,
    create_streaming_optimizer
)

from .audio_quality_analyzer import (
    AudioQualityAnalyzer,
    QualityStandard,
    QualityMetric,
    QualityAnalysisResult,
    create_quality_analyzer
)

from .audio_effects_processor import (
    AudioEffectsProcessor,
    EffectType,
    EffectQuality,
    ProcessingMode,
    EffectParameter,
    EffectConfiguration,
    EffectsChain,
    EffectResult,
    EQProcessor,
    DynamicsProcessor,
    ModulationEffects,
    ReverbProcessor,
    create_audio_effects_processor,
    create_preset_effects_chain
)

from .audio_transcription_engine import (
    AudioTranscriptionEngine,
    TranscriptionLanguage,
    TranscriptionModel,
    TranscriptionQuality,
    SpeakerDiarizationMode,
    OutputFormat,
    TranscriptionConfiguration,
    TranscriptionResult,
    TranscriptionSegment,
    SpeakerInfo,
    AudioPreprocessor,
    LanguageDetector,
    SpeakerDiarization,
    TranscriptionEngine,
    SubtitleGenerator,
    create_audio_transcription_engine,
    create_transcription_config
)

from .audio_fingerprinting_system import (
    AudioFingerprintingSystem,
    FingerprintAlgorithm,
    MatchQuality,
    ContentType,
    ProtectionLevel,
    AudioFingerprint,
    ContentMetadata,
    MatchResult,
    FingerprintingConfiguration,
    SpectralPeaksFingerprinter,
    MFCCHashFingerprinter,
    PerceptualHashFingerprinter,
    create_audio_fingerprinting_system,
    create_content_metadata
)

from .audio_normalization_engine import (
    AudioNormalizationEngine,
    BroadcastStandard,
    NormalizationType,
    QualityMode,
    ProcessingMode,
    LoudnessMetrics,
    NormalizationTarget,
    NormalizationConfiguration,
    NormalizationResult,
    LoudnessMeter,
    TruePeakLimiter,
    DynamicRangeProcessor,
    create_audio_normalization_engine,
    create_normalization_config
)

from .audio_codec_manager import (
    AudioCodecManager,
    AudioCodec,
    CompressionMode,
    EncodingSpeed,
    QualityMetric,
    CodecParameters,
    EncodingConfiguration,
    EncodingResult,
    AudioPreprocessor,
    QualityAnalyzer,
    FFmpegCodecManager,
    create_audio_codec_manager,
    create_encoding_config
)

from .audio_metadata_processor import (
    AudioMetadataProcessor,
    MetadataStandard,
    TagType,
    ImageType,
    AudioImage,
    AudioMetadata,
    MetadataProcessingConfig,
    MetadataExtractor,
    MetadataEnricher,
    create_audio_metadata_processor,
    create_metadata_config
)

from .audio_security_manager import (
    AudioSecurityManager,
    SecurityLevel,
    DRMPolicy,
    AccessLevel,
    ThreatType,
    SecurityCredentials,
    DRMConfiguration,
    SecurityEvent,
    AccessAuditLog,
    CryptographyManager,
    TokenManager,
    DRMManager,
    ThreatDetector,
    create_audio_security_manager,
    create_drm_config
)

from .audio_performance_monitor import (
    AudioPerformanceMonitor,
    MetricType,
    AlertSeverity,
    ResourceType,
    PerformanceMetric,
    PerformanceAlert,
    ResourceHealth,
    PerformanceReport,
    SystemMonitor,
    AudioMetricsCollector,
    AlertManager,
    PerformancePredictor,
    create_audio_performance_monitor
)

__version__ = "2.5.0"
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
    "create_audio_analytics_engine",
    
    # Realtime Processing
    "RealtimeAudioProcessor",
    "ProcessingMode",
    "AudioEffect",
    "LatencyTarget",
    "AudioBuffer",
    "ProcessingChain",
    "LatencyMetrics",
    "QualityMetrics",
    "RealtimeProcessingResult",
    "create_realtime_processor",
    "create_processing_chain",
    
    # Streaming Optimization
    "AudioStreamingOptimizer",
    "StreamingProtocol",
    "QualityLevel",
    "NetworkConditions",
    "StreamingResult",
    "create_streaming_optimizer",
    
    # Quality Analysis
    "AudioQualityAnalyzer",
    "QualityStandard",
    "QualityMetric",
    "QualityAnalysisResult",
    "create_quality_analyzer",
    
    # Audio Effects Processor
    "AudioEffectsProcessor",
    "EffectType",
    "EffectQuality",
    "EffectParameter",
    "EffectConfiguration",
    "EffectsChain",
    "EffectResult",
    "EQProcessor",
    "DynamicsProcessor",
    "ModulationEffects",
    "ReverbProcessor",
    "create_audio_effects_processor",
    "create_preset_effects_chain",
    
    # Audio Transcription Engine
    "AudioTranscriptionEngine",
    "TranscriptionLanguage",
    "TranscriptionModel",
    "TranscriptionQuality",
    "SpeakerDiarizationMode",
    "OutputFormat",
    "TranscriptionConfiguration",
    "TranscriptionResult",
    "TranscriptionSegment",
    "SpeakerInfo",
    "create_audio_transcription_engine",
    "create_transcription_config",
    
    # Audio Fingerprinting System
    "AudioFingerprintingSystem",
    "FingerprintAlgorithm",
    "MatchQuality",
    "ContentType",
    "ProtectionLevel",
    "AudioFingerprint",
    "ContentMetadata",
    "MatchResult",
    "FingerprintingConfiguration",
    "create_audio_fingerprinting_system",
    "create_content_metadata",
    
    # Audio Normalization Engine
    "AudioNormalizationEngine",
    "BroadcastStandard",
    "NormalizationType",
    "LoudnessMetrics",
    "NormalizationTarget",
    "NormalizationConfiguration",
    "NormalizationResult",
    "LoudnessMeter",
    "TruePeakLimiter",
    "DynamicRangeProcessor",
    "create_audio_normalization_engine",
    "create_normalization_config",
    
    # Audio Codec Manager
    "AudioCodecManager",
    "CompressionMode",
    "EncodingSpeed",
    "CodecParameters",
    "EncodingConfiguration",
    "EncodingResult",
    "FFmpegCodecManager",
    "create_audio_codec_manager",
    "create_encoding_config",
    
    # Audio Metadata Processor
    "AudioMetadataProcessor",
    "MetadataStandard",
    "TagType",
    "ImageType",
    "AudioImage",
    "AudioMetadata",
    "MetadataProcessingConfig",
    "MetadataExtractor",
    "MetadataEnricher",
    "create_audio_metadata_processor",
    "create_metadata_config",
    
    # Audio Security Manager
    "AudioSecurityManager",
    "SecurityLevel",
    "DRMPolicy",
    "AccessLevel",
    "ThreatType",
    "SecurityCredentials",
    "DRMConfiguration",
    "SecurityEvent",
    "AccessAuditLog",
    "CryptographyManager",
    "TokenManager",
    "DRMManager",
    "ThreatDetector",
    "create_audio_security_manager",
    "create_drm_config",
    
    # Audio Performance Monitor
    "AudioPerformanceMonitor",
    "AlertSeverity",
    "ResourceType",
    "PerformanceMetric",
    "PerformanceAlert",
    "ResourceHealth",
    "PerformanceReport",
    "SystemMonitor",
    "AudioMetricsCollector",
    "AlertManager",
    "PerformancePredictor",
    "create_audio_performance_monitor"
]