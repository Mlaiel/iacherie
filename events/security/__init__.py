"""Events Security Module

Advanced security utilities for the Ainflue events system.
Ultra-sophisticated threat detection, access control, and compliance management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core security modules (existing)
from .encryption import EncryptionManager
from .authentication import SecurityManager

# Advanced security modules (new)
from .threat_detection_engine import ThreatDetectionEngine, ThreatLevel, ThreatIndicator, ThreatAnalysisResult
from .access_control_manager import AccessControlManager, Permission, BusinessRole, AuthorizationResult, PermissionScope
from .audit_trail_collector import AuditTrailCollector, AuditRecord, ComplianceValidation, ForensicAnalysis, AuditLevel
from .compliance_validator import ComplianceValidator, ComplianceRegulation, ComplianceViolation, ComplianceValidationResult, ViolationSeverity
from .event_security_orchestrator import EventSecurityOrchestrator, SecurityContext, SecurityAssessment, SecurityDecision, SecurityLevel
from .intrusion_prevention_system import IntrusionPreventionSystem, IntrusionAttempt, PreventionResponse, IntrusionType, PreventionAction
from .security_analytics_dashboard import SecurityAnalyticsDashboard, SecurityMetric, DashboardWidget, SecurityAlert, DashboardData, MetricType, TimeRange
from .vulnerability_scanner import VulnerabilityScanner, Vulnerability, ScanResult, VulnerabilityReport, VulnerabilityType, VulnerabilitySeverity, ScanType
from .incident_response_handler import IncidentResponseHandler, SecurityIncident, IncidentReport, IncidentType, IncidentSeverity, IncidentStatus

__all__ = [
    # Core security
    'EncryptionManager', 
    'SecurityManager',
    
    # Threat detection
    'ThreatDetectionEngine', 
    'ThreatLevel', 
    'ThreatIndicator', 
    'ThreatAnalysisResult',
    
    # Access control
    'AccessControlManager', 
    'Permission', 
    'BusinessRole', 
    'AuthorizationResult', 
    'PermissionScope',
    
    # Audit and compliance
    'AuditTrailCollector', 
    'AuditRecord', 
    'ComplianceValidation', 
    'ForensicAnalysis', 
    'AuditLevel',
    
    # Compliance validation
    'ComplianceValidator',
    'ComplianceRegulation',
    'ComplianceViolation',
    'ComplianceValidationResult',
    'ViolationSeverity',
    
    # Security orchestration
    'EventSecurityOrchestrator',
    'SecurityContext',
    'SecurityAssessment',
    'SecurityDecision',
    'SecurityLevel',
    
    # Intrusion prevention
    'IntrusionPreventionSystem',
    'IntrusionAttempt',
    'PreventionResponse',
    'IntrusionType',
    'PreventionAction',
    
    # Security analytics
    'SecurityAnalyticsDashboard',
    'SecurityMetric',
    'DashboardWidget',
    'SecurityAlert',
    'DashboardData',
    'MetricType',
    'TimeRange',
    
    # Vulnerability scanning
    'VulnerabilityScanner',
    'Vulnerability',
    'ScanResult',
    'VulnerabilityReport',
    'VulnerabilityType',
    'VulnerabilitySeverity',
    'ScanType',
    
    # Incident response
    'IncidentResponseHandler',
    'SecurityIncident',
    'IncidentReport',
    'IncidentType',
    'IncidentSeverity',
    'IncidentStatus'
]