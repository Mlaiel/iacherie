"""
Compliance Agent Module - Advanced Regulatory Compliance & Governance System

Comprehensive compliance monitoring, regulatory adherence, and governance automation.
Handles GDPR, DMCA, platform policies, and international regulations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .compliance_agent import ComplianceAgent, ComplianceAgentManager
from .regulatory_monitor import RegulatoryMonitor, PolicyTracker
from .gdpr_manager import GDPRManager, DataProtectionOfficer
from .policy_enforcer import PolicyEnforcer, ViolationDetector
from .audit_system import AuditSystem, ComplianceReporter

__all__ = [
    'ComplianceAgent',
    'ComplianceAgentManager', 
    'RegulatoryMonitor',
    'PolicyTracker',
    'GDPRManager',
    'DataProtectionOfficer',
    'PolicyEnforcer',
    'ViolationDetector',
    'AuditSystem',
    'ComplianceReporter'
]
