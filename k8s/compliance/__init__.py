"""IA Influencer Agent - Compliance Module
Comprehensive enterprise-grade compliance system for regulatory adherence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

This module provides complete compliance functionality including:
- GDPR, CCPA, DMCA, PCI DSS, SOX, ISO 27001 compliance
- Automated audit logging and reporting
- Policy enforcement and monitoring
- Risk assessment and mitigation
- KYC/AML verification systems
- Data retention and privacy controls
- Regulatory reporting automation
- External service integrations
"""

from .audit_logger import (
    AuditLogger,
    AuditCategory,
    AuditLevel,
    ComplianceFramework,
    AuditEvent,
    ComplianceReport
)

from .compliance_monitor import (
    ComplianceMonitor,
    ComplianceStatus,
    MonitoringScope,
    ViolationSeverity,
    ComplianceViolation,
    ComplianceMetrics
)

from .gdpr_compliance import (
    GDPRComplianceManager,
    ConsentType,
    ConsentStatus,
    DataSubjectRight,
    ProcessingPurpose,
    LegalBasis,
    ConsentRecord,
    DataSubjectRequest,
    PrivacyNotice
)

from .policy_enforcer import (
    PolicyEnforcer,
    PolicyType,
    PolicyStatus,
    EnforcementAction,
    PolicyRule,
    PolicyViolation,
    EnforcementResult
)

from .dmca_automation import (
    DMCAAutomation,
    InfringementType,
    NoticeStatus,
    InfringementEvidence,
    DMCANotice,
    TakedownRequest
)

from .kyc_verification import (
    KYCVerificationSystem,
    VerificationStatus,
    DocumentType,
    RiskRating,
    KYCDocument,
    VerificationResult,
    ComplianceWorkflow
)

from .data_retention import (
    DataRetentionManager,
    RetentionCategory,
    RetentionStatus,
    RetentionPolicy,
    RetentionSchedule,
    DataLifecycleEvent
)

from .privacy_controls import (
    PrivacyControlsManager,
    PrivacyPrincipal,
    PrivacyRisk,
    PrivacyImpactAssessment,
    DataMinimizationRule,
    AnonymizationConfig
)

from .regulatory_reporting import (
    RegulatoryReportingSystem,
    ReportType,
    ReportStatus,
    RegulatoryReport,
    ComplianceSubmission,
    ReportTemplate
)

from .risk_assessment import (
    RiskAssessmentEngine,
    RiskCategory,
    RiskLevel,
    RiskStatus,
    MitigationStrategy,
    RiskFactor,
    RiskScenario,
    ComprehensiveRiskAssessment,
    RiskMitigationPlan
)

from .integration_hub import (
    ComplianceIntegrationHub,
    IntegrationType,
    IntegrationStatus,
    ExternalServiceConfig,
    ComplianceWorkflow,
    ComplianceMetrics
)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "All rights reserved - Unauthorized use prohibited"

# Module metadata
__title__ = "IA Influencer Agent Compliance System"
__description__ = "Enterprise-grade compliance management system"
__license__ = "Proprietary"
__status__ = "Production"

# Supported compliance frameworks
SUPPORTED_FRAMEWORKS = [
    ComplianceFramework.GDPR,
    ComplianceFramework.CCPA,
    ComplianceFramework.DMCA,
    ComplianceFramework.PCI_DSS,
    ComplianceFramework.SOX,
    ComplianceFramework.ISO_27001,
    ComplianceFramework.PIPEDA,
    ComplianceFramework.LGPD
]

# Core system components
CORE_COMPONENTS = {
    "audit_logger": AuditLogger,
    "compliance_monitor": ComplianceMonitor,
    "gdpr_manager": GDPRComplianceManager,
    "policy_enforcer": PolicyEnforcer,
    "dmca_automation": DMCAAutomation,
    "kyc_system": KYCVerificationSystem,
    "data_retention": DataRetentionManager,
    "privacy_controls": PrivacyControlsManager,
    "regulatory_reporting": RegulatoryReportingSystem,
    "risk_assessment": RiskAssessmentEngine,
    "consent_manager": ConsentManager,
    "compliance_dashboard": ComplianceDashboard
}

# Export all public components
__all__ = [
    # Core classes
    "AuditLogger",
    "ComplianceMonitor", 
    "GDPRComplianceManager",
    "PolicyEnforcer",
    "DMCAAutomation",
    "KYCVerificationSystem",
    "DataRetentionManager",
    "PrivacyControlsManager",
    "RegulatoryReportingSystem",
    "RiskAssessmentEngine",
    "ComplianceIntegrationHub",
    
    # Enumerations
    "AuditCategory",
    "AuditLevel",
    "ComplianceFramework",
    "ComplianceStatus",
    "MonitoringScope",
    "ViolationSeverity",
    "ConsentType",
    "ConsentStatus",
    "DataSubjectRight",
    "ProcessingPurpose",
    "LegalBasis",
    "PolicyType",
    "PolicyStatus",
    "EnforcementAction",
    "InfringementType",
    "NoticeStatus",
    "VerificationStatus",
    "DocumentType",
    "RiskRating",
    "RetentionCategory",
    "RetentionStatus",
    "PrivacyPrincipal",
    "PrivacyRisk",
    "ReportType",
    "ReportStatus",
    "RiskCategory",
    "RiskLevel",
    "RiskStatus",
    "MitigationStrategy",
    "IntegrationType",
    "IntegrationStatus",
    
    # Data classes
    "AuditEvent",
    "ComplianceReport",
    "ComplianceViolation",
    "ComplianceMetrics",
    "ConsentRecord",
    "DataSubjectRequest",
    "PrivacyNotice",
    "PolicyRule",
    "PolicyViolation",
    "EnforcementResult",
    "InfringementEvidence",
    "DMCANotice",
    "TakedownRequest",
    "KYCDocument",
    "VerificationResult",
    "ComplianceWorkflow",
    "RetentionPolicy",
    "RetentionSchedule",
    "DataLifecycleEvent",
    "PrivacyImpactAssessment",
    "DataMinimizationRule",
    "AnonymizationConfig",
    "RegulatoryReport",
    "ComplianceSubmission",
    "ReportTemplate",
    "RiskFactor",
    "RiskScenario",
    "ComprehensiveRiskAssessment",
    "RiskMitigationPlan",
    "ExternalServiceConfig",
    
    # New modules
    "ConsentManager",
    "ConsentType",
    "ConsentStatus", 
    "ConsentMethod",
    "ProcessingPurpose",
    "ConsentDetails",
    "ConsentBundle",
    "PrivacyPreferences",
    "ComplianceDashboard",
    "DashboardView",
    "ReportFrequency",
    "AlertSeverity",
    "DashboardMetrics",
    "ComplianceAlert",
    "DashboardWidget",
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

from .consent_manager import (
    ConsentManager,
    ConsentType,
    ConsentStatus,
    ConsentMethod,
    ProcessingPurpose,
    ConsentDetails,
    ConsentBundle,
    PrivacyPreferences
)

from .compliance_dashboard import (
    ComplianceDashboard,
    DashboardView,
    ReportFrequency,
    AlertSeverity,
    DashboardMetrics,
    ComplianceAlert,
    DashboardWidget
)
