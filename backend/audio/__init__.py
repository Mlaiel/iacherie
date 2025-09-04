"""🎵 Backend Audio Processing Module - Streamlined Audio Intelligence System

Consolidated audio processing module for the IA Influencer Agent platform,
providing comprehensive audio processing capabilities in a clean, maintainable structure.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de
"""

# Core audio processing
from .processing import (
    AudioProcessor,
    SourceSeparator, 
    VocalSeparator,
    InstrumentSeparator,
    StemExtractor,
    BackgroundRemover
)

# Audio analysis and features
from .analysis import (
    SpectralAnalyzer,
    MelodyExtractor,
    RhythmAnalyzer,
    AudioQualityAssessment,
    GenreClassifier,
    InstrumentIdentifier,
    VoiceActivityDetector,
    AudioMetadataExtractor,
    HarmonicAnalyzer,
    TempoDetector,
    KeyDetector,
    MoodAnalyzer
)

# Audio enhancement algorithms
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

# Speech recognition
from .recognition import (
    SpeechRecognizer,
    LanguageDetector,
    SpeakerIdentifier,
    KeywordSpotter,
    VoiceActivityDetector,
    SpeechToText,
    RealTimeRecognizer
)

# Text-to-speech synthesis  
from .synthesis import (
    TextToSpeechEngine,
    NeuralVocoderManager,
    CompositionEngine,
    RealtimeSynthesisEngine,
    SpatialAudioSynthesis,
    SynthesisModelManager,
    SynthesisPipelineManager
)

# Audio fingerprinting
from .fingerprinting import (
    AudioFingerprinter,
    ContentMatcher,
    CopyrightDetector,
    FingerprintDatabase,
    SimilarityEngine,
    DuplicateDetector,
    PerceptualHashGenerator,
    FingerprintMatchingEngine
)

# Audio compression/codecs
from .compression import (
    AudioCompressor,
    CodecManager,
    BitrateOptimizer,
    LosslessCompressor,
    StreamingCompressor,
    AdaptiveBitrate,
    QualityPreserver
)

# Real-time audio streaming
from .streaming import (
    StreamingProcessor,
    RealTimeAnalyzer,
    StreamingEncoder,
    AdaptiveStreaming,
    LatencyOptimizer,
    BufferManager,
    NetworkAdapter
)

# Audio effects and filters
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

# Format conversion utilities
from .conversion import (
    AudioConverter,
    FormatValidator,
    MetadataPreserver,
    BatchConverter,
    QualityMaintainer,
    FormatDetector,
    TranscodingEngine
)

# Audio processing monitoring
from .monitoring import (
    AudioValidator,
    QualityMetrics,
    ComplianceChecker,
    MasteringStandards,
    DistortionAnalyzer,
    DynamicRangeAnalyzer,
    PerformanceMonitor,
    ProcessingStats
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Export all main classes
__all__ = [
    # Core Processing
    'AudioProcessor',
    'SourceSeparator', 
    'VocalSeparator',
    'InstrumentSeparator',
    'StemExtractor',
    'BackgroundRemover',
    
    # Analysis
    'SpectralAnalyzer',
    'MelodyExtractor',
    'RhythmAnalyzer',
    'AudioQualityAssessment',
    'GenreClassifier',
    'InstrumentIdentifier',
    'VoiceActivityDetector',
    'AudioMetadataExtractor',
    'HarmonicAnalyzer',
    'TempoDetector',
    'KeyDetector',
    'MoodAnalyzer',
    
    # Enhancement
    'AudioUpsampler',
    'NoiseSuppressionEngine',
    'DynamicRangeProcessor',
    'StereoWidener',
    'BassEnhancer',
    'VocalEnhancer',
    'AudioRestorer',
    'QualityEnhancer',
    
    # Recognition
    'SpeechRecognizer',
    'LanguageDetector',
    'SpeakerIdentifier',
    'KeywordSpotter',
    'SpeechToText',
    'RealTimeRecognizer',
    
    # Synthesis
    'TextToSpeechEngine',
    'NeuralVocoderManager',
    'CompositionEngine',
    'RealtimeSynthesisEngine',
    'SpatialAudioSynthesis',
    'SynthesisModelManager',
    'SynthesisPipelineManager',
    
    # Fingerprinting
    'AudioFingerprinter',
    'ContentMatcher',
    'CopyrightDetector',
    'FingerprintDatabase',
    'SimilarityEngine',
    'DuplicateDetector',
    'PerceptualHashGenerator',
    'FingerprintMatchingEngine',
    
    # Compression
    'AudioCompressor',
    'CodecManager',
    'BitrateOptimizer',
    'LosslessCompressor',
    'StreamingCompressor',
    'AdaptiveBitrate',
    'QualityPreserver',
    
    # Streaming
    'StreamingProcessor',
    'RealTimeAnalyzer',
    'StreamingEncoder',
    'AdaptiveStreaming',
    'LatencyOptimizer',
    'BufferManager',
    'NetworkAdapter',
    
    # Effects
    'EqualizerProcessor',
    'CompressorProcessor',
    'ReverbProcessor',
    'ChorusProcessor',
    'DistortionProcessor',
    'NoiseReductionProcessor',
    'PitchShifter',
    'TimeStretcher',
    'AudioMixer',
    'MasteringProcessor',
    
    # Conversion
    'AudioConverter',
    'FormatValidator',
    'MetadataPreserver',
    'BatchConverter',
    'QualityMaintainer',
    'FormatDetector',
    'TranscodingEngine',
    
    # Monitoring
    'AudioValidator',
    'QualityMetrics',
    'ComplianceChecker',
    'MasteringStandards',
    'DistortionAnalyzer',
    'DynamicRangeAnalyzer',
    'PerformanceMonitor',
    'ProcessingStats'
]