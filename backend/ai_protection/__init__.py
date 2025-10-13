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
from .multimedia_protection_engine import (
    MultimediaProtectionEngine,
    ProtectionProfile,
    MultimediaAnalysis,
    ProtectionAlgorithm,
    OptimizationTarget,
    create_multimedia_protection_engine,
    create_protection_profile
)
from .violation_monitoring_system import (
    ViolationMonitoringSystem,
    MonitoringTarget,
    ViolationDetection,
    MonitoringScope,
    ViolationSeverity,
    EscalationAction,
    create_violation_monitoring_system
)
from .legal_automation_engine import (
    LegalAutomationEngine,
    LegalCase,
    LegalDocument,
    DMCANotice,
    LegalActionType,
    LegalActionStatus,
    EnforcementStrategy,
    create_legal_automation_engine
)
from .global_protection_network import (
    GlobalProtectionNetwork,
    GlobalViolation,
    CountryCode,
    Region,
    ComplianceFramework,
    create_global_protection_network
)
from .protection_analytics_engine import (
    ProtectionAnalyticsEngine,
    AnalyticsMetric,
    ReportType,
    TimeRange,
    ROIAnalysis,
    PerformanceMetrics,
    create_protection_analytics_engine
)

__all__ = [
    # Core existing modules
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
    
    # AI Protection Orchestrator
    'AIProtectionOrchestrator',
    'ProtectionRequest',
    'ProtectionResult',
    'OrchestrationStrategy',
    'ThreatLevel',
    'create_ai_protection_orchestrator',
    
    # Multimedia Protection Engine
    'MultimediaProtectionEngine',
    'ProtectionProfile',
    'MultimediaAnalysis', 
    'ProtectionAlgorithm',
    'OptimizationTarget',
    'create_multimedia_protection_engine',
    'create_protection_profile',
    
    # Violation Monitoring System
    'ViolationMonitoringSystem',
    'MonitoringTarget',
    'ViolationDetection',
    'MonitoringScope',
    'ViolationSeverity',
    'EscalationAction',
    'create_violation_monitoring_system',
    
    # Legal Automation Engine
    'LegalAutomationEngine',
    'LegalCase',
    'LegalDocument', 
    'DMCANotice',
    'LegalActionType',
    'LegalActionStatus',
    'EnforcementStrategy',
    'create_legal_automation_engine',
    
    # Global Protection Network
    'GlobalProtectionNetwork',
    'GlobalViolation',
    'CountryCode',
    'Region',
    'ComplianceFramework',
    'create_global_protection_network',
    
    # Protection Analytics Engine
    'ProtectionAnalyticsEngine',
    'AnalyticsMetric',
    'ReportType',
    'TimeRange',
    'ROIAnalysis',
    'PerformanceMetrics',
    'create_protection_analytics_engine'
]

__version__ = "1.0.0"