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
    AudioMetadataExtractor
)

# Advanced BPM and harmonic analysis
from .analysis.bpm_harmonic_analyzer import (
    BPMHarmonicAnalyzer,
    BPMAnalysisConfig,
    BPMResult,
    HarmonicResult,
    MusicalAnalysisResult,
    TempoAlgorithm,
    HarmonicModel,
    MusicalKey,
    TimeSignature,
    create_bpm_harmonic_analyzer,
    quick_bpm_detection,
    quick_key_detection
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

# Advanced AI mastering capabilities
from .effects.ai_mastering_engine import (
    AIMasteringEngine,
    MasteringConfig,
    MasteringResult,
    MasteringStyle,
    ProcessingChain,
    QualityTarget,
    AIGenreDetector,
    AIEqualizer,
    AILimiter,
    create_mastering_engine,
    quick_master_for_streaming,
    master_for_broadcast
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

# Advanced normalization capabilities
from .enhancement.normalization_engine import (
    ProfessionalNormalizationEngine,
    NormalizationConfig,
    NormalizationStandard,
    NormalizationResult,
    LoudnessMeter,
    TruePeakLimiter,
    create_normalization_engine,
    normalize_for_streaming,
    normalize_for_broadcast
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

# Advanced separation capabilities
from .separation.core import (
    AdvancedSeparationEngine,
    SeparationConfig,
    SeparationModel,
    SeparationQuality,
    SeparationResult,
    create_separation_engine
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
    # Advanced Separation Engine (NEW - Ultra-Professional)
    'AdvancedSeparationEngine',
    'SeparationConfig', 
    'SeparationModel',
    'SeparationQuality',
    'SeparationResult',
    'create_separation_engine',
    
    # Advanced Normalization Engine (NEW - Professional Standards)
    'ProfessionalNormalizationEngine',
    'NormalizationConfig',
    'NormalizationStandard', 
    'NormalizationResult',
    'LoudnessMeter',
    'TruePeakLimiter',
    'create_normalization_engine',
    'normalize_for_streaming',
    'normalize_for_broadcast',
    
    # Advanced BPM & Harmonic Analysis (NEW - Music Intelligence)
    'BPMHarmonicAnalyzer',
    'BPMAnalysisConfig',
    'BPMResult',
    'HarmonicResult', 
    'MusicalAnalysisResult',
    'TempoAlgorithm',
    'HarmonicModel',
    'MusicalKey',
    'TimeSignature',
    'create_bpm_harmonic_analyzer',
    'quick_bpm_detection',
    'quick_key_detection',
    
    # AI Mastering Engine (NEW - Professional Mastering)
    'AIMasteringEngine',
    'MasteringConfig',
    'MasteringResult',
    'MasteringStyle',
    'ProcessingChain', 
    'QualityTarget',
    'AIGenreDetector',
    'AIEqualizer',
    'AILimiter',
    'create_mastering_engine',
    'quick_master_for_streaming',
    'master_for_broadcast',
    
    # Analysis Engine
    'SpectralAnalyzer',
    'MelodyExtractor',
    'RhythmAnalyzer',
    'AudioQualityAssessment',
    'GenreClassifier',
    'InstrumentIdentifier',
    'VoiceActivityDetector',
    'AudioMetadataExtractor',
    
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