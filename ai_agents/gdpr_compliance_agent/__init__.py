"""GDPR Compliance Agent Module
Advanced Data Protection and Privacy Compliance System

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""
# Core compliance components
from .manager import GDPRComplianceManager
from .data_handler import DataPrivacyHandler
from .consent_manager import ConsentManager
from .data_processor import DataProcessor
from .anonymization_engine import AnonymizationEngine
from .audit_logger import ComplianceAuditLogger
from .rights_manager import DataRightsManager
from .breach_detector import BreachDetector
from .policy_engine import PolicyEngine
from .reporting_engine import ReportingEngine

__all__ = [
    "GDPRComplianceManager",
    "DataPrivacyHandler", 
    "ConsentManager",
    "DataProcessor",
    "AnonymizationEngine",
    "ComplianceAuditLogger",
    "DataRightsManager",
    "BreachDetector", 
    "PolicyEngine",
    "ReportingEngine"
]

from .manager import GDPRComplianceManager
from .data_handler import DataPrivacyHandler
from .consent_manager import ConsentManager
from .data_processor import DataProcessor
from .anonymization_engine import AnonymizationEngine
from .audit_logger import ComplianceAuditLogger
from .rights_manager import DataRightsManager
from .breach_detector import DataBreachDetector
from .policy_engine import PrivacyPolicyEngine
from .reporting_engine import ComplianceReportingEngine

__all__ = [
    'GDPRComplianceManager',
    'DataPrivacyHandler',
    'ConsentManager',
    'DataProcessor',
    'AnonymizationEngine',
    'ComplianceAuditLogger',
    'DataRightsManager',
    'DataBreachDetector',
    'PrivacyPolicyEngine',
    'ComplianceReportingEngine'
]

__version__ = '1.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
