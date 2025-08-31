"""Deployment Security Module for IA Influencer Agent Platform

This module provides comprehensive security management for deployment environments,
including certificate management, encrypted configurations, secure communication,
compliance monitoring, threat detection, network security, incident response,
and threat intelligence for the multi-content protection platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Company: IA Influencer Agent Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and
will result in legal action.
"""# Certificate Management
from .certificate_manager import CertificateManager, TLSConfigGenerator

# Configuration Security
from .encrypted_config import (
    EncryptedConfigManager,
    SecretVaultIntegration,
    ConfigEncryption
)

# Secure Communication
from .secure_communication import (
    SecureChannelManager,
    MessageEncryption,
    ProtocolValidator
)

# Compliance & Monitoring
from .compliance_monitor import (
    ComplianceChecker,
    SecurityAuditLogger,
    PolicyEnforcer
)

# Access Control
from .access_control import (
    DeploymentAccessControl,
    PermissionManager,
    RoleBasedSecurity
)

# Vulnerability Management
from .vulnerability_scanner import (
    ContainerScanner,
    DependencyChecker,
    SecurityAssessment
)

# Advanced Threat Detection
from .threat_detection import (
    DeploymentThreatDetection,
    ThreatDetector,
    AnomalyDetector,
    BehaviorAnalyzer,
    IncidentResponse,
    ThreatIndicator as ThreatDetectionIndicator,
    SecurityEvent,
    ThreatLevel,
    ThreatType as DetectionThreatType
)

# Network Security Monitoring
from .network_security import (
    NetworkSecurityMonitor,
    PortScanner,
    TrafficAnalyzer,
    IntrusionDetector,
    NetworkAlert,
    NetworkConnection,
    NetworkPacket,
    NetworkThreatType,
    AlertSeverity
)

# Incident Response & Forensics
from .incident_response import (
    SecurityIncidentManager,
    EvidenceCollector,
    IncidentResponseOrchestrator,
    ForensicsAnalyzer,
    SecurityIncident,
    DigitalEvidence,
    ForensicsTask,
    IncidentSeverity,
    IncidentStatus,
    IncidentCategory,
    EvidenceType,
    ResponseAction
)

# Threat Intelligence
from .threat_intelligence import (
    ThreatIntelligenceEngine,
    ThreatIntelligenceDatabase,
    ThreatIntelligenceCollector,
    ThreatIndicator as IntelThreatIndicator,
    ThreatCampaign,
    ThreatActor,
    IndicatorType,
    ThreatType as IntelThreatType,
    ConfidenceLevel,
    ThreatIntelligenceSource
)

__all__ = [
    # Certificate Management
    'CertificateManager',
    'TLSConfigGenerator',
    
    # Configuration Security
    'EncryptedConfigManager',
    'SecretVaultIntegration',
    'ConfigEncryption',
    
    # Secure Communication
    'SecureChannelManager',
    'MessageEncryption',
    'ProtocolValidator',
    
    # Compliance & Monitoring
    'ComplianceChecker',
    'SecurityAuditLogger',
    'PolicyEnforcer',
    
    # Access Control
    'DeploymentAccessControl',
    'PermissionManager',
    'RoleBasedSecurity',
    
    # Vulnerability Management
    'ContainerScanner',
    'DependencyChecker',
    'SecurityAssessment',
    
    # Advanced Threat Detection
    'DeploymentThreatDetection',
    'ThreatDetector',
    'AnomalyDetector',
    'BehaviorAnalyzer',
    'IncidentResponse',
    'ThreatDetectionIndicator',
    'SecurityEvent',
    'ThreatLevel',
    'DetectionThreatType',
    
    # Network Security Monitoring
    'NetworkSecurityMonitor',
    'PortScanner',
    'TrafficAnalyzer',
    'IntrusionDetector',
    'NetworkAlert',
    'NetworkConnection',
    'NetworkPacket',
    'NetworkThreatType',
    'AlertSeverity',
    
    # Incident Response & Forensics
    'SecurityIncidentManager',
    'EvidenceCollector',
    'IncidentResponseOrchestrator',
    'ForensicsAnalyzer',
    'SecurityIncident',
    'DigitalEvidence',
    'ForensicsTask',
    'IncidentSeverity',
    'IncidentStatus',
    'IncidentCategory',
    'EvidenceType',
    'ResponseAction',
    
    # Threat Intelligence
    'ThreatIntelligenceEngine',
    'ThreatIntelligenceDatabase',
    'ThreatIntelligenceCollector',
    'IntelThreatIndicator',
    'ThreatCampaign',
    'ThreatActor',
    'IndicatorType',
    'IntelThreatType',
    'ConfidenceLevel',
    'ThreatIntelligenceSource'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced Deployment Security Suite for IA Influencer Agent Platform"
