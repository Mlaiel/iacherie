"""
Audit Trail Agent - Industrial-Grade Compliance & Security Tracking System

Enterprise audit trail management for comprehensive tracking of all platform activities,
security events, compliance monitoring, and forensic analysis capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from .audit_trail_agent import AuditTrailAgent
from .security_monitor import SecurityAuditMonitor
from .compliance_tracker import ComplianceTracker
from .forensic_analyzer import ForensicAnalyzer
from .activity_logger import ActivityLogger
from .event_correlator import EventCorrelator

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "AuditTrailAgent",
    "SecurityAuditMonitor", 
    "ComplianceTracker",
    "ForensicAnalyzer",
    "ActivityLogger",
    "EventCorrelator"
]

# Enterprise Module Configuration
AUDIT_MODULE_CONFIG = {
    "version": __version__,
    "author": __author__,
    "contact": __email__,
    "capabilities": [
        "enterprise_audit_logging",
        "security_event_monitoring", 
        "compliance_tracking",
        "forensic_analysis",
        "activity_correlation",
        "real_time_alerting"
    ],
    "compliance_standards": [
        "SOX", "GDPR", "HIPAA", "PCI_DSS", "ISO27001"
    ]
}
