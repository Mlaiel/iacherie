"""AI Protection Rights Module

This module provides comprehensive AI-powered content protection and rights management
functionality including watermarking, blockchain registry, copyright detection,
NFT generation, and digital rights management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from .watermark_engine import WatermarkEngine, WatermarkConfig, WatermarkType, ContentType
from .blockchain_registry import BlockchainRightsRegistry, RightsType
from .copyright_detector import CopyrightDetector, ViolationType
from .nft_generator import NFTGenerator, NFTStandard
from .rights_manager import DigitalRightsManager, ProtectionLevel
from .ai_protection_orchestrator import (
    AIProtectionOrchestrator, 
    ProtectionRequest, 
    ProtectionResult, 
    OrchestrationStrategy,
    ThreatLevel,
    create_ai_protection_orchestrator
)

__all__ = [
    'WatermarkEngine',
    'WatermarkConfig', 
    'WatermarkType',
    'ContentType',
    'BlockchainRightsRegistry',
    'RightsType',
    'CopyrightDetector',
    'ViolationType',
    'NFTGenerator',
    'NFTStandard',
    'DigitalRightsManager',
    'ProtectionLevel',
    'AIProtectionOrchestrator',
    'ProtectionRequest',
    'ProtectionResult',
    'OrchestrationStrategy',
    'ThreatLevel',
    'create_ai_protection_orchestrator'
]

__version__ = "1.0.0"