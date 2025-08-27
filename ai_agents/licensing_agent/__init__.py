"""
Licensing Agent Module - Advanced Content Licensing & Rights Management System

Comprehensive digital rights management, licensing automation, and legal compliance system.
Handles copyright protection, licensing agreements, royalty distribution, and legal documentation.

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

from .licensing_agent import LicensingAgent, LicensingAgentManager
from .rights_manager import RightsManager, CopyrightProtector
from .license_generator import LicenseGenerator, ContractAutomator
from .royalty_calculator import RoyaltyCalculator, RevenueDistributor
from .compliance_checker import ComplianceChecker, LegalValidator

# Import factory and quick access functions
from .index import (
    LicensingAgentFactory,
    licensing_context,
    quick_license_generation,
    quick_rights_verification,
    quick_compliance_check
)

__all__ = [
    # Core agents
    'LicensingAgent',
    'LicensingAgentManager', 
    'RightsManager',
    'CopyrightProtector',
    'LicenseGenerator',
    'ContractAutomator',
    'RoyaltyCalculator',
    'RevenueDistributor',
    'ComplianceChecker',
    'LegalValidator',
    
    # Factory and utilities
    'LicensingAgentFactory',
    'licensing_context',
    'quick_license_generation',
    'quick_rights_verification',
    'quick_compliance_check'
]
