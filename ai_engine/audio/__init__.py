"""Audio Package - Complete Audio Processing and Management Infrastructure
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the proprietary intellectual property of Fahed Mlaiel.
Any unauthorized use, modification, distribution, or theft of this code 
without explicit written permission from the author is strictly prohibited
and will result in severe legal consequences under German and international law.

Email: mlaiel@live.de

This package provides comprehensive audio processing, analysis, protection,
monetization, collaboration, and distribution capabilities for the
IA Influencer Agent platform.
"""

import logging

# Import all modules for easy access
from .audio_manager import AudioManager, AudioProcessingStatus, ContentType, AudioUploadRequest, AudioProcessingResult
from .enhancement import AudioEnhancer, EnhancementSettings, EnhancementType, QualityLevel, EnhancementResult
from .fingerprinting import AudioFingerprinter, FingerprintType, AudioFingerprint, MatchQuality, FingerprintMatch
from .music_analysis import MusicAnalyzer, MusicGenre, MusicKey, MusicAnalysisResult
from ..recommendation.content_analyzer import AnalysisType  # Import depuis le bon module
from .signal_processing import AudioSignalProcessor, AudioData, AudioFormat, ProcessingType, ProcessingResult
from .content_protection import ContentProtector, ProtectionLevel, ProtectionMethod, InfringementType, ProtectionResult
from .rights_management import RightsManager, RightsLevel, LicenseType, UsageType, RoyaltyType, RightsResult
from .monetization import MonetizationEngine, RevenueModel, RevenueStream, PaymentStatus, MonetizationResult
from .collaboration import CollaborationMatcher, CollaborationType, SkillLevel, CollaborationStatus, CollaborationMatch
from .distribution import MultiPlatformDistributor, DistributionChannel, DistributionStatus, DistributionResult

logger = logging.getLogger(__name__)

# Package metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"

# Team Information
__team__ = {
    "project_lead": "Fahed Mlaiel",
    "email": "mlaiel@live.de",
    "specialties": [
        "Lead Dev IA",
        "Backend Senior Engineer", 
        "ML Engineer",
        "Database Administrator",
        "Security Engineer",
        "Microservices Architect",
        "Audio Processing Expert",
        "DevOps Engineer",
        "AI Prompt Engineer"
    ],
    "project": "IA Influencer Agent - Audio Processing & Protection Platform",
    "copyright_year": "2025"
}

# Export all classes for convenient imports
__all__ = [
    # Main orchestration
    'AudioManager',
    'AudioProcessingStatus',
    'ContentType', 
    'AudioUploadRequest',
    'AudioProcessingResult',
    
    # Audio enhancement
    'AudioEnhancer',
    'EnhancementSettings',
    'EnhancementType',
    'QualityLevel',
    'EnhancementResult',
    
    # Fingerprinting
    'AudioFingerprinter',
    'FingerprintType',
    'AudioFingerprint',
    'MatchQuality',
    'FingerprintMatch',
    
    # Music analysis
    'MusicAnalyzer',
    'MusicGenre',
    'MusicKey',
    'MusicAnalysisResult',
    'AnalysisType',  # Importé depuis recommendation.content_analyzer
    
    # Signal processing
    'AudioSignalProcessor',
    'AudioData',
    'AudioFormat',
    'ProcessingType',
    'ProcessingResult',
    
    # Content protection
    'ContentProtector',
    'ProtectionLevel',
    'ProtectionMethod',
    'InfringementType',
    'ProtectionResult',
    
    # Rights management
    'RightsManager',
    'RightsLevel',
    'LicenseType',
    'UsageType',
    'RoyaltyType',
    'RightsResult',
    
    # Monetization
    'MonetizationEngine',
    'RevenueModel',
    'RevenueStream',
    'PaymentStatus',
    'MonetizationResult',
    
    # Collaboration
    'CollaborationMatcher',
    'CollaborationType',
    'SkillLevel',
    'CollaborationStatus',
    'CollaborationMatch',
    
    # Distribution
    'MultiPlatformDistributor',
    'DistributionChannel',
    'DistributionStatus',
    'DistributionResult'
]

logger.info("Audio package v2.0.0 initialized with complete industrial-grade infrastructure")
