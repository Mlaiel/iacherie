"""AI Voice System - Backend Voice Generation Modules

Comprehensive voice generation system with:
- Voice bank with 1000+ voices
- Accent generation and synthesis
- Emotional voice modulation
- Age-specific voice synthesis
- Celebrity voice cloning
- Enterprise Voice Business Logic System

Enterprise Voice Business Logic Components:

Phase 1 - Core Intelligence & Business Logic:
- Creator Voice Content Intelligence Engine
- Voice Content Business Logic Orchestrator
- Creator Voice Performance Analytics
- Voice Content Monetization Engine

Phase 2 - Content Enhancement & Processing:
- Multi-Format Voice Content Processor
- Voice Content Enhancement Engine
- Voice Quality Optimization Engine
- Voice Transcription Processing Engine

Phase 3 - Voice Protection & Rights Management:
- Voice Content Protection Engine
- Voice Rights Management System
- Voice Fingerprinting Protection System
- Voice Piracy Detection Engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core voice generation modules
from .voice_bank import VoiceBank, VoiceBankManager
from .accent_generator import AccentGenerator
from .emotion_voice import EmotionVoiceGenerator
from .age_voice import AgeVoiceGenerator
from .celebrity_cloner import CelebrityVoiceCloner

# Enterprise Voice Business Logic modules - Phase 2: Content Enhancement & Processing
from .multi_format_voice_processor import (
    MultiFormatVoiceProcessor,
    ProcessingFormat,
    ProcessingQuality,
    EnhancementType,
    ProcessingPipeline,
    ProcessingSettings,
    ProcessingResult
)
from .voice_content_enhancer import (
    VoiceContentEnhancer,
    EnhancementMode,
    VoiceCharacteristic,
    EnhancementAlgorithm,
    EnhancementProfile,
    EnhancementResult
)
from .voice_quality_optimizer import (
    VoiceQualityOptimizer,
    QualityMetric,
    OptimizationTarget,
    OptimizationStrategy,
    QualityAnalysis,
    OptimizationSettings,
    OptimizationResult
)
from .voice_transcription_engine import (
    VoiceTranscriptionEngine,
    TranscriptionModel,
    TranscriptionQuality,
    SpeakerDetectionMode,
    OutputFormat,
    TranscriptionSettings,
    TranscriptionResult,
    WordSegment,
    SentenceSegment
)
from .creator_voice_intelligence import (
    CreatorVoiceIntelligenceEngine,
    CreatorType,
    VoiceContentType,
    VoiceAnalysisResult,
    CreatorVoiceProfile
)
from .voice_content_orchestrator import (
    VoiceContentOrchestrator,
    WorkflowStage,
    BusinessLogicTier,
    VoiceContentWorkflow
)
from .creator_voice_analytics import (
    CreatorVoiceAnalytics,
    AnalyticsMetric,
    PerformanceMetric,
    AnalyticsSnapshot,
    ContentPerformanceAnalysis
)
from .voice_monetization_engine import (
    VoiceContentMonetizationEngine,
    RevenueStream,
    MonetizationStrategy,
    RevenueOpportunity,
    PricingOptimization
)

# Enterprise Voice Business Logic modules - Phase 3: Voice Protection & Rights Management
from .voice_protection_engine import (
    VoiceProtectionEngine,
    ProtectionLevel,
    ProtectionStatus,
    ThreatType,
    VoiceFingerprint,
    ProtectionAlert,
    ProtectionConfiguration
)
from .voice_rights_manager import (
    VoiceRightsManager,
    RightsType,
    LicenseType,
    UsageScope,
    RightsStatus,
    VoiceRights,
    LicenseAgreement,
    UsageReport
)
from .voice_fingerprinting_system import (
    VoiceFingerprintingSystem,
    FingerprintType,
    FingerprintAlgorithm,
    MatchConfidence,
    VoiceFingerprint as VoiceFingerprintData,
    FingerprintMatch,
    FingerprintDatabase
)
from .voice_piracy_detector import (
    VoicePiracyDetector,
    PiracyType,
    DetectionMethod,
    SeverityLevel,
    DetectionStatus,
    PiracyDetection,
    MonitoringTarget,
    PiracyReport
)

__all__ = [
    # Core voice modules
    'VoiceBank',
    'VoiceBankManager',
    'AccentGenerator',
    'EmotionVoiceGenerator',
    'AgeVoiceGenerator',
    'CelebrityVoiceCloner',
    
    # Enterprise voice business logic - Phase 1: Intelligence & Core
    'CreatorVoiceIntelligenceEngine',
    'CreatorType',
    'VoiceContentType',
    'VoiceAnalysisResult',
    'CreatorVoiceProfile',
    'VoiceContentOrchestrator',
    'WorkflowStage',
    'BusinessLogicTier',
    'VoiceContentWorkflow',
    'CreatorVoiceAnalytics',
    'AnalyticsMetric',
    'PerformanceMetric',
    'AnalyticsSnapshot',
    'ContentPerformanceAnalysis',
    'VoiceContentMonetizationEngine',
    'RevenueStream',
    'MonetizationStrategy',
    'RevenueOpportunity',
    'PricingOptimization',
    
    # Enterprise voice business logic - Phase 2: Enhancement & Processing
    'MultiFormatVoiceProcessor',
    'ProcessingFormat',
    'ProcessingQuality',
    'EnhancementType',
    'ProcessingPipeline',
    'ProcessingSettings',
    'ProcessingResult',
    'VoiceContentEnhancer',
    'EnhancementMode',
    'VoiceCharacteristic',
    'EnhancementAlgorithm',
    'EnhancementProfile',
    'EnhancementResult',
    'VoiceQualityOptimizer',
    'QualityMetric',
    'OptimizationTarget',
    'OptimizationStrategy',
    'QualityAnalysis',
    'OptimizationSettings',
    'OptimizationResult',
    'VoiceTranscriptionEngine',
    'TranscriptionModel',
    'TranscriptionQuality',
    'SpeakerDetectionMode',
    'OutputFormat',
    'TranscriptionSettings',
    'TranscriptionResult',
    'WordSegment',
    'SentenceSegment',
    
    # Enterprise voice business logic - Phase 3: Protection & Rights Management
    'VoiceProtectionEngine',
    'ProtectionLevel',
    'ProtectionStatus',
    'ThreatType',
    'VoiceFingerprint',
    'ProtectionAlert',
    'ProtectionConfiguration',
    'VoiceRightsManager',
    'RightsType',
    'LicenseType',
    'UsageScope',
    'RightsStatus',
    'VoiceRights',
    'LicenseAgreement',
    'UsageReport',
    'VoiceFingerprintingSystem',
    'FingerprintType',
    'FingerprintAlgorithm',
    'MatchConfidence',
    'VoiceFingerprintData',
    'FingerprintMatch',
    'FingerprintDatabase',
    'VoicePiracyDetector',
    'PiracyType',
    'DetectionMethod',
    'SeverityLevel',
    'DetectionStatus',
    'PiracyDetection',
    'MonitoringTarget',
    'PiracyReport'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"