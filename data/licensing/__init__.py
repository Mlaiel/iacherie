"""Data Licensing Module - IA Influencer Agent
==========================================

Advanced licensing data management for content monetization and rights protection.
Handles licensing agreements, royalty distribution, and compliance tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing and usage rights.

🎯 PROJECT TEAM SPECIALTIES:
- Lead AI Developer & Solution Architect: Advanced AI/ML systems and intelligent automation
- Backend Senior Engineer: Enterprise-grade backend architecture and microservices  
- ML Engineer: Machine learning models and predictive analytics
- Database Administrator: High-performance data management and optimization
- Security Engineer: Advanced cybersecurity and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Processing Specialist: Advanced audio processing and music industry integration
- DevOps Engineer: Infrastructure automation and deployment optimization
- AI Prompt Engineer: Natural language processing and conversational AI systems
"""

from .models import (
    LicenseAgreement,
    RoyaltyCalculation,
    LicenseUsageTracking,
    PaymentRecord,
    ComplianceReport,
    RightsOwnership,
    ContractTerms,
    RevenueDistribution
)

from .repository import LicensingRepository

from .calculator import RoyaltyCalculator, UsageTracker

from .compliance import ComplianceEngine

from .contract_generator import ContractGenerator

from .payment_processor import PaymentProcessor

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Models
    "LicenseAgreement",
    "RoyaltyCalculation", 
    "LicenseUsageTracking",
    "PaymentRecord",
    "ComplianceReport",
    "RightsOwnership",
    "ContractTerms",
    "RevenueDistribution",
    
    # Services
    "LicensingRepository",
    "RoyaltyCalculator",
    "ComplianceEngine", 
    "ContractGenerator",
    "UsageTracker",
    "PaymentProcessor"
]
