"""Database Content Protection Module

Ultra-advanced content protection database system providing comprehensive storage,
analytics, and management for AI-powered content protection platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + DBA + DevOps
Project: IA Influencer Agent + Content Protection Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️
==================================================================
This code and all associated intellectual property are the EXCLUSIVE property of Fahed Mlaiel.
ANY unauthorized use, copying, modification, distribution, or commercialization without 
explicit written permission is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries.
Legal violations will be prosecuted to the full extent of international law.
"""# Core protection modules
from .protection_storage import ProtectionStorageManager, ProtectionStorageError
from .alert_repository import ProtectionAlertRepository, ProtectionAlertRepositoryError
from .violation_tracker import ViolationTracker, ViolationTrackerError
from .protection_analytics import ProtectionAnalyticsEngine, ProtectionAnalyticsError
from .takedown_manager import TakedownManagerRepository, TakedownManagerError
from .evidence_storage import EvidenceStorageManager, EvidenceStorageError
from .protection_rules import ProtectionRulesRepository, ProtectionRulesError
from .whitelist_manager import WhitelistManagerRepository, WhitelistManagerError

# Advanced enterprise modules
from .compliance_reporter import ComplianceReporter, ComplianceReporterError, ComplianceFramework, ReportType
from .legal_documentation import LegalDocumentationGenerator, LegalDocumentationError, DocumentType, JurisdictionType, UrgencyLevel
from .platform_integrations import PlatformIntegrationsManager, PlatformIntegrationsError, PlatformType, IntegrationType, ActionType, ScanStatus
from .threat_intelligence import ThreatIntelligenceSystem, ThreatIntelligenceError, ThreatLevel, ThreatCategory, AttackVector, IndicatorType

# Master controller
from .index import ContentProtectionDatabase, ContentProtectionDatabaseError

__all__ = [
    # Master controller
    "ContentProtectionDatabase",
    "ContentProtectionDatabaseError",
    
    # Core protection modules
    "ProtectionStorageManager",
    "ProtectionAlertRepository",
    "ViolationTracker",
    "ProtectionAnalyticsEngine",
    "TakedownManagerRepository",
    "EvidenceStorageManager",
    "ProtectionRulesRepository",
    "WhitelistManagerRepository",
    
    # Advanced enterprise modules
    "ComplianceReporter",
    "LegalDocumentationGenerator",
    "PlatformIntegrationsManager",
    "ThreatIntelligenceSystem",
    
    # Core exceptions
    "ProtectionStorageError",
    "ProtectionAlertRepositoryError",
    "ViolationTrackerError",
    "ProtectionAnalyticsError",
    "TakedownManagerError",
    "EvidenceStorageError",
    "ProtectionRulesError",
    "WhitelistManagerError",
    
    # Advanced exceptions
    "ComplianceReporterError",
    "LegalDocumentationError",
    "PlatformIntegrationsError",
    "ThreatIntelligenceError",
    
    # Enums and types
    "ComplianceFramework",
    "ReportType",
    "DocumentType",
    "JurisdictionType",
    "UrgencyLevel",
    "PlatformType",
    "IntegrationType",
    "ActionType",
    "ScanStatus",
    "ThreatLevel",
    "ThreatCategory",
    "AttackVector",
    "IndicatorType"
]

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__team__ = "Lead AI Developer + ML Engineer + Security Architect + DBA + DevOps + Microservices Architect + Audio Engineer + Prompt Engineer"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "(c) 2025 Fahed Mlaiel"
