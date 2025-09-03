"""🎵 Audio Processing Engine - Professional Audio Intelligence System

This module provides comprehensive audio processing, protection, and intelligence
capabilities for the IA Influencer Agent platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

Expert Development Team:
- Lead Dev IA: Advanced AI algorithms and intelligent processing
- Backend Senior: Robust architecture and scalable systems  
- ML Engineer: Machine learning models and audio intelligence
- DBA: Optimized data storage and retrieval systems
- Security Specialist: Content protection and fingerprinting
- Microservices Architect: Distributed audio processing
- Audio Engineer: Professional audio processing and effects
- DevOps Engineer: Containerization and production deployment
- IA Prompt Engineer: Natural language audio interfaces

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de
"""

from .analysis import (
    SpectralAnalyzer,
    MelodyExtractor,
    RhythmAnalyzer,
    AudioQualityAssessment,
    GenreClassifier,
    InstrumentIdentifier,
    VoiceActivityDetector,
    AudioMetadataExtractor,
    ProfessionalAudioVisualizer,
    WaveformConfig,
    SpectrogramConfig,
    WaveformStyle,
    SpectrogramMode,
    ColorScheme,
    VisualizationResult
)

from .effects import (
    EqualizerProcessor,
    CompressorProcessor,
    ReverbProcessor,
    ChorusProcessor,
    DistortionProcessor,
    NoiseReductionProcessor,
    PitchShifter,
    TimeStretcher,
    AudioMixer,
    MasteringProcessor
)

from .enhancement import (
    AudioUpsampler,
    NoiseSuppressionEngine,
    DynamicRangeProcessor,
    StereoWidener,
    BassEnhancer,
    VocalEnhancer,
    AudioRestorer,
    QualityEnhancer
)

from .fingerprinting import (
    AudioFingerprinter,
    ContentMatcher,
    CopyrightDetector,
    FingerprintDatabase,
    SimilarityEngine,
    DuplicateDetector
)

from .format_conversion import (
    AudioConverter,
    CodecManager,
    BitrateOptimizer,
    FormatValidator,
    MetadataPreserver,
    BatchConverter
)

from .quality_control import (
    AudioValidator,
    QualityMetrics,
    ComplianceChecker,
    MasteringStandards,
    DistortionAnalyzer,
    DynamicRangeAnalyzer
)

from .separation import (
    VocalSeparator,
    InstrumentSeparator,
    SourceSeparationEngine,
    StemExtractor,
    BackgroundRemover,
    HarmonyExtractor
)

from .synthesis import (
    AudioSynthesisHub,
    NeuralVocoderManager,
    CompositionEngine,
    TextToSpeechEngine,
    RealtimeSynthesisEngine,
    SpatialAudioSynthesis,
    SynthesisModelManager,
    SynthesisPipelineManager,
    get_synthesis_hub,
    synthesize_audio,
    SynthesisCapability
)

# Import central hub from index
from .index import (
    AudioEngineHub,
    get_audio_hub,
    AudioRequest,
    AudioResponse,
    AudioCapability,
    AudioProcessingMode,
    process_audio,
    list_audio_capabilities,
    get_audio_hub_health,
    get_audio_hub_stats
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Export main classes and hub functionality
__all__ = [
    # Central Hub (NEW - Main Entry Point)
    'AudioEngineHub',
    'get_audio_hub',
    'AudioRequest', 
    'AudioResponse',
    'AudioCapability',
    'AudioProcessingMode',
    'process_audio',
    'list_audio_capabilities', 
    'get_audio_hub_health',
    'get_audio_hub_stats',
    
    # Analysis Engine
    'SpectralAnalyzer',
    'MelodyExtractor',
    'RhythmAnalyzer',
    'AudioQualityAssessment',
    'GenreClassifier',
    'InstrumentIdentifier',
    'VoiceActivityDetector',
    'AudioMetadataExtractor',
    
    # Professional Visualization Engine (NEW)
    'ProfessionalAudioVisualizer',
    'WaveformConfig',
    'SpectrogramConfig',
    'WaveformStyle',
    'SpectrogramMode',
    'ColorScheme',
    'VisualizationResult',
    
    # Synthesis Engine (Enhanced)
    'AudioSynthesisHub',
    'NeuralVocoderManager',
    'CompositionEngine', 
    'TextToSpeechEngine',
    'RealtimeSynthesisEngine',
    'SpatialAudioSynthesis',
    'SynthesisModelManager',
    'SynthesisPipelineManager',
    'get_synthesis_hub',
    'synthesize_audio',
    'SynthesisCapability',
    
    # Enhancement Engine
    'SpatialEnhancer',
    'NoiseRemover',
    'AudioUpsampler',
    'DynamicRangeProcessor',
    'StereoWidener',
    'HarmonicEnhancer',
    
    # Effects Engine
    'EqualizerProcessor',
    'CompressorProcessor', 
    'ReverbProcessor',
    'ChorusProcessor',
    'DistortionProcessor',
    'NoiseReductionProcessor',
    'PitchShifter',
    'TimeStretcher',
    'FilterBank',
    'ModulationProcessor',
    
    # Quality Control Engine
    'QualityAnalyzer',
    'LoudnessAnalyzer', 
    'PeakLimiter',
    'DynamicRangeAnalyzer',
    'SpectrumAnalyzer',
    'PhaseAnalyzer',
    
    # Fingerprinting & Protection Engine
    'AudioFingerprinter',
    'ContentMatcher',
    'CopyrightDetector', 
    'WatermarkEmbedder',
    'IntegrityValidator',
    'UsageTracker',
    
    # Separation Engine
    'VocalSeparator',
    'InstrumentSeparator',
    'StemExtractor',
    'SourceSeparator', 
    'MelodySeparator',
    'PercussionSeparator',
    
    # Format Conversion Engine  
    'AudioConverter',
    'CodecManager',
    'MetadataProcessor',
    'BitrateOptimizer',
    'FormatValidator',
    'CompressionEngine'
]