"""
Audio Module Index - Quick Access to All Audio Processing Components
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, modification, distribution, or theft of this code 
without explicit written permission from the author is strictly prohibited
and will result in severe legal consequences under German and international law.

Email: mlaiel@live.de

This index provides convenient access to all audio processing components
and serves as the main entry point for the audio module.
"""

# Main orchestration and management
from .audio_manager import (
    AudioManager,
    AudioProcessingStatus,
    ContentType,
    AudioUploadRequest,
    AudioProcessingResult
)

# Core audio processing capabilities
from .enhancement import (
    AudioEnhancer,
    EnhancementSettings,
    EnhancementType,
    QualityLevel,
    EnhancementResult
)

from .fingerprinting import (
    AudioFingerprinter,
    FingerprintType,
    AudioFingerprint,
    MatchQuality,
    FingerprintResult,
    FingerprintMatch
)

from .music_analysis import (
    MusicAnalyzer,
    MusicGenre,
    MusicKey,
    MusicAnalysisResult,
    AnalysisType,
    MusicFeatures
)

from .signal_processing import (
    AudioSignalProcessor,
    AudioData,
    AudioFormat,
    ProcessingType,
    ProcessingResult
)

# Protection and rights management
from .content_protection import (
    ContentProtector,
    ProtectionLevel,
    ProtectionMethod,
    InfringementType,
    EnforcementAction,
    ProtectionSettings,
    ProtectionResult,
    InfringementDetection,
    EnforcementResult
)

from .rights_management import (
    RightsManager,
    RightsLevel,
    LicenseType,
    UsageType,
    RoyaltyType,
    RightsStatus,
    RightsHolder,
    LicenseTerms,
    RightsRegistration,
    RoyaltyPayment,
    UsageReport,
    RightsResult
)

# Monetization and revenue
from .monetization import (
    MonetizationEngine,
    RevenueModel,
    RevenueStream,
    PaymentStatus,
    PaymentMethod,
    RevenueSource,
    RevenueMetrics,
    MonetizationStrategy,
    PaymentRecord,
    MonetizationResult
)

# Collaboration and networking
from .collaboration import (
    CollaborationMatcher,
    CollaborationType,
    SkillLevel,
    CollaborationStatus,
    MatchQuality as CollabMatchQuality,
    ArtistProfile,
    MatchingCriteria,
    CollaborationMatch,
    CollaborationProject,
    CollaborationInvite
)

# Distribution and publishing
from .distribution import (
    MultiPlatformDistributor,
    DistributionChannel,
    DistributionStatus,
    ContentFormat,
    ReleaseType,
    PlatformCredentials,
    DistributionMetadata,
    DistributionSettings,
    DistributionResult,
    CrossPlatformAnalytics
)

# Quick access factory functions
def create_audio_processor(config=None):
    """Create a complete audio processing system"""
    return AudioManager(config)

def create_content_protector(config=None):
    """Create a content protection system"""
    return ContentProtector(config)

def create_monetization_engine(config=None):
    """Create a monetization engine"""
    return MonetizationEngine(config)

def create_collaboration_matcher(config=None):
    """Create a collaboration matching system"""
    return CollaborationMatcher(config)

def create_multi_platform_distributor(config=None):
    """Create a multi-platform distribution system"""
    return MultiPlatformDistributor(config)

# Complete system factory
def create_complete_audio_system(config=None):
    """
    Create a complete audio processing system with all components
    
    Returns:
        dict: Dictionary containing all system components
    """
    return {
        'audio_manager': AudioManager(config),
        'enhancer': AudioEnhancer(),
        'fingerprinter': AudioFingerprinter(),
        'music_analyzer': MusicAnalyzer(),
        'signal_processor': AudioSignalProcessor(),
        'content_protector': ContentProtector(config),
        'rights_manager': RightsManager(config),
        'monetization_engine': MonetizationEngine(config),
        'collaboration_matcher': CollaborationMatcher(config),
        'distributor': MultiPlatformDistributor(config)
    }

# System information
SYSTEM_INFO = {
    'name': 'IA Influencer Agent - Audio Processing System',
    'version': '2.0.0',
    'author': 'Fahed Mlaiel',
    'email': 'mlaiel@live.de',
    'components': [
        'AudioManager - Complete audio processing orchestration',
        'AudioEnhancer - Professional audio enhancement',
        'AudioFingerprinter - Advanced audio fingerprinting',
        'MusicAnalyzer - Intelligent music analysis',
        'AudioSignalProcessor - Digital signal processing',
        'ContentProtector - AI-powered content protection',
        'RightsManager - Digital rights management',
        'MonetizationEngine - Revenue generation and optimization',
        'CollaborationMatcher - AI-driven artist collaboration',
        'MultiPlatformDistributor - Automated content distribution'
    ],
    'capabilities': [
        'Multi-format audio processing (WAV, MP3, FLAC, AAC)',
        'Real-time audio analysis and enhancement',
        'Advanced copyright protection and enforcement',
        'Blockchain-based rights registration',
        'AI-powered collaboration matching',
        'Multi-platform content distribution',
        'Automated monetization and royalty management',
        'Cross-platform analytics and reporting'
    ]
}

def get_system_info():
    """Get information about the audio processing system"""
    return SYSTEM_INFO

def print_system_info():
    """Print system information"""
    info = get_system_info()
    print(f"\n🎵 {info['name']} v{info['version']}")
    print(f"👨‍💻 Author: {info['author']} ({info['email']})")
    print("\n🔧 Components:")
    for component in info['components']:
        print(f"  • {component}")
    print("\n🚀 Capabilities:")
    for capability in info['capabilities']:
        print(f"  • {capability}")
    print("\n© 2025 Fahed Mlaiel. All rights reserved.")

# Export all for easy imports
__all__ = [
    # Main components
    'AudioManager', 'AudioEnhancer', 'AudioFingerprinter', 'MusicAnalyzer', 
    'AudioSignalProcessor', 'ContentProtector', 'RightsManager', 'MonetizationEngine',
    'CollaborationMatcher', 'MultiPlatformDistributor',
    
    # Data types and enums
    'AudioProcessingStatus', 'ContentType', 'EnhancementType', 'QualityLevel',
    'FingerprintType', 'MatchQuality', 'MusicGenre', 'MusicKey', 'AnalysisType',
    'AudioFormat', 'ProcessingType', 'ProtectionLevel', 'ProtectionMethod',
    'InfringementType', 'EnforcementAction', 'RightsLevel', 'LicenseType',
    'UsageType', 'RoyaltyType', 'RightsStatus', 'RevenueModel', 'RevenueStream',
    'PaymentStatus', 'PaymentMethod', 'CollaborationType', 'SkillLevel',
    'CollaborationStatus', 'DistributionChannel', 'DistributionStatus',
    'ContentFormat', 'ReleaseType',
    
    # Data classes
    'AudioUploadRequest', 'AudioProcessingResult', 'EnhancementSettings',
    'EnhancementResult', 'AudioFingerprint', 'FingerprintResult', 'FingerprintMatch',
    'MusicAnalysisResult', 'MusicFeatures', 'AudioData', 'ProcessingResult',
    'ProtectionSettings', 'ProtectionResult', 'InfringementDetection',
    'EnforcementResult', 'RightsHolder', 'LicenseTerms', 'RightsRegistration',
    'RoyaltyPayment', 'UsageReport', 'RightsResult', 'RevenueSource',
    'RevenueMetrics', 'MonetizationStrategy', 'PaymentRecord', 'MonetizationResult',
    'ArtistProfile', 'MatchingCriteria', 'CollaborationMatch', 'CollaborationProject',
    'CollaborationInvite', 'PlatformCredentials', 'DistributionMetadata',
    'DistributionSettings', 'DistributionResult', 'CrossPlatformAnalytics',
    
    # Factory functions
    'create_audio_processor', 'create_content_protector', 'create_monetization_engine',
    'create_collaboration_matcher', 'create_multi_platform_distributor',
    'create_complete_audio_system',
    
    # Utility functions
    'get_system_info', 'print_system_info',
    'SYSTEM_INFO'
]
