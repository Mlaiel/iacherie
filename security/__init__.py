"""
Security Module - Comprehensive security audit, monitoring, and compliance system
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import main security components for easy access
try:
    from .audit_trail import (
        SecurityAuditTrail,
        AuditTrailLevel,
        SecurityAuditEvent,
        security_audit_trail,
        log_security_audit,
        log_authentication_event,
        log_data_access_event
    )
except ImportError:
    pass

try:
    from .monitoring import (
        SecurityMonitoringDashboard,
        IncidentSeverity,
        IncidentStatus,
        SecurityIncident,
        security_dashboard,
        get_security_status,
        create_security_incident
    )
except ImportError:
    pass

try:
    from .policies import (
        SecurityPolicyManager,
        PolicyType,
        PolicyStatus,
        SecurityPolicy,
        IncidentResponseProcedures,
        security_policy_manager,
        get_security_policies,
        get_policy_compliance_report,
        execute_incident_response_procedure
    )
except ImportError:
    pass

try:
    from .vulnerability_scanner import (
        SecurityScanner,
        VulnerabilitySeverity,
        Vulnerability,
        SecurityScanResult,
        security_scanner
    )
except ImportError:
    pass

__all__ = [
    # Audit Trail
    'SecurityAuditTrail',
    'AuditTrailLevel', 
    'SecurityAuditEvent',
    'security_audit_trail',
    'log_security_audit',
    'log_authentication_event',
    'log_data_access_event',
    
    # Monitoring
    'SecurityMonitoringDashboard',
    'IncidentSeverity',
    'IncidentStatus',
    'SecurityIncident',
    'security_dashboard',
    'get_security_status',
    'create_security_incident',
    
    # Policies
    'SecurityPolicyManager',
    'PolicyType',
    'PolicyStatus',
    'SecurityPolicy',
    'IncidentResponseProcedures',
    'security_policy_manager',
    'get_security_policies',
    'get_policy_compliance_report',
    'execute_incident_response_procedure',
    
    # Vulnerability Scanner
    'SecurityScanner',
    'VulnerabilitySeverity',
    'Vulnerability',
    'SecurityScanResult',
    'security_scanner'
]