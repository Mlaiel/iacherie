"""Edge Security Module
====================

Security infrastructure for edge computing nodes,
providing firewall, intrusion detection, DDoS protection, and threat intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Edge firewall
from .edge_firewall import (
    EdgeFirewall,
    FirewallRule,
    RuleAction,
    ProtocolType,
    create_edge_firewall
)

# Intrusion detection
from .intrusion_detection import (
    IntrusionDetectionSystem,
    ThreatLevel,
    AttackSignature,
    create_intrusion_detection
)

# DDoS protection
from .ddos_protection import (
    DDoSProtection,
    AttackType,
    MitigationStrategy,
    create_ddos_protection
)

# Threat intelligence
from .threat_intelligence import (
    ThreatIntelligence,
    ThreatIndicator,
    ThreatSource,
    create_threat_intelligence
)

# Secure tunneling
from .secure_tunneling import (
    SecureTunnel,
    TunnelProtocol,
    EncryptionMethod,
    create_secure_tunnel
)

# Key management
from .key_management import (
    KeyManager,
    KeyType,
    KeyRotationPolicy,
    create_key_manager
)

# Compliance checker
from .compliance_checker import (
    ComplianceChecker,
    ComplianceFramework,
    ComplianceResult,
    create_compliance_checker
)

__all__ = [
    # Edge firewall
    "EdgeFirewall",
    "FirewallRule",
    "RuleAction",
    "ProtocolType",
    "create_edge_firewall",
    
    # Intrusion detection
    "IntrusionDetectionSystem",
    "ThreatLevel",
    "AttackSignature",
    "create_intrusion_detection",
    
    # DDoS protection
    "DDoSProtection",
    "AttackType",
    "MitigationStrategy",
    "create_ddos_protection",
    
    # Threat intelligence
    "ThreatIntelligence",
    "ThreatIndicator",
    "ThreatSource",
    "create_threat_intelligence",
    
    # Secure tunneling
    "SecureTunnel",
    "TunnelProtocol",
    "EncryptionMethod",
    "create_secure_tunnel",
    
    # Key management
    "KeyManager",
    "KeyType",
    "KeyRotationPolicy",
    "create_key_manager",
    
    # Compliance checking
    "ComplianceChecker",
    "ComplianceFramework",
    "ComplianceResult",
    "create_compliance_checker"
]