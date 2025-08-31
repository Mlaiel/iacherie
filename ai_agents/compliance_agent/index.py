"""
Compliance Agent Index - Centralized Export System

Enterprise-grade compliance management module exports for the IA-Influencer-Agent platform.
Provides centralized access to all compliance management components and systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL WARNING:
This code and intellectual property belong exclusively to Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from typing import Dict, List, Any, Optional

# Core Compliance Management Components
from .compliance_agent import (
    ComplianceAgent,
    ComplianceAgentManager,
    ComplianceLevel,
    ComplianceStatus,
    RegulatoryFramework,
    ComplianceRule,
    ComplianceCheck,
    ComplianceReport,
    ViolationAlert
)

# Regulatory Monitoring System
from .regulatory_monitor import (
    RegulatoryMonitor,
    PolicyTracker,
    PolicyUpdateType,
    RegulatorySource,
    PolicyUpdate,
    RegulationDatabase
)

# GDPR Management System
from .gdpr_manager import (
    GDPRManager,
    DataProtectionOfficer,
    ConsentType,
    DataSubjectRequest,
    ConsentStatus,
    GDPRCompliance,
    DataProcessingAgreement
)

# Policy Enforcement System
from .policy_enforcer import (
    PolicyEnforcer,
    ViolationDetector,
    PolicyType,
    ViolationSeverity,
    EnforcementAction,
    PolicyRule,
    ViolationReport
)

# Audit System
from .audit_system import (
    AuditSystem,
    ComplianceReporter,
    AuditType,
    AuditEvent,
    ComplianceMetric,
    AuditReport,
    ComplianceScore
)

# Module Configuration
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"

# Export Collections
COMPLIANCE_COMPONENTS = [
    ComplianceAgent,
    ComplianceAgentManager,
    RegulatoryMonitor,
    PolicyTracker,
    GDPRManager,
    DataProtectionOfficer,
    PolicyEnforcer,
    ViolationDetector,
    AuditSystem,
    ComplianceReporter
]

COMPLIANCE_ENUMS = [
    ComplianceLevel,
    ComplianceStatus,
    RegulatoryFramework,
    PolicyUpdateType,
    ConsentType,
    PolicyType,
    ViolationSeverity,
    AuditType
]

COMPLIANCE_DATA_MODELS = [
    ComplianceRule,
    ComplianceCheck,
    ComplianceReport,
    ViolationAlert,
    PolicyUpdate,
    DataSubjectRequest,
    EnforcementAction,
    AuditEvent,
    ComplianceMetric
]

# Centralized Module Interface
class ComplianceModuleInterface:
    """
    Centralized interface for compliance module operations.
    Provides unified access to all compliance management capabilities.
    """
    
    def __init__(self):
        """Initialize compliance module interface"""
        self.components = {
            'agent': ComplianceAgent,
            'manager': ComplianceAgentManager,
            'regulatory_monitor': RegulatoryMonitor,
            'policy_tracker': PolicyTracker,
            'gdpr_manager': GDPRManager,
            'dpo': DataProtectionOfficer,
            'policy_enforcer': PolicyEnforcer,
            'violation_detector': ViolationDetector,
            'audit_system': AuditSystem,
            'reporter': ComplianceReporter
        }
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """Get compliance component by name"""



        return self.components.get(component_name)
    
    def list_components(self) -> List[str]:
        """List all available compliance components"""



        return list(self.components.keys())
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""



        return {
            'name': 'compliance_agent',
            'version': __version__,
            'author': __author__,
            'license': __license__,
            'components': len(self.components),
            'capabilities': [
                'regulatory_compliance',
                'gdpr_management',
                'policy_enforcement',
                'audit_trail',
                'violation_detection',
                'compliance_reporting'
            ]
        }

# Module instance
compliance_interface = ComplianceModuleInterface()

# All exports
__all__ = [
    # Core Components
    'ComplianceAgent',
    'ComplianceAgentManager',
    'RegulatoryMonitor', 
    'PolicyTracker',
    'GDPRManager',
    'DataProtectionOfficer',
    'PolicyEnforcer',
    'ViolationDetector',
    'AuditSystem',
    'ComplianceReporter',
    
    # Enums
    'ComplianceLevel',
    'ComplianceStatus',
    'RegulatoryFramework',
    'PolicyUpdateType',
    'ConsentType',
    'PolicyType',
    'ViolationSeverity',
    'AuditType',
    
    # Data Models
    'ComplianceRule',
    'ComplianceCheck', 
    'ComplianceReport',
    'ViolationAlert',
    'PolicyUpdate',
    'DataSubjectRequest',
    'EnforcementAction',
    'AuditEvent',
    'ComplianceMetric',
    
    # Collections
    'COMPLIANCE_COMPONENTS',
    'COMPLIANCE_ENUMS',
    'COMPLIANCE_DATA_MODELS',
    
    # Interface
    'ComplianceModuleInterface',
    'compliance_interface',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__'
]
