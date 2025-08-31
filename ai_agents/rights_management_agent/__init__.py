"""Rights Management Agent - Global Digital Rights Management System

Enterprise-grade digital rights management system with comprehensive ownership
tracking, licensing automation, royalty calculation, and global compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Features:
- Comprehensive ownership registration
- Multi-tier protection levels
- Territorial and usage rights control
- Automated royalty calculation
- License management and tracking
- Revenue optimization
"""

from .manager import RightsManagementManager

from .core.ownership_registry import OwnershipRegistry

from .core.license_manager import LicenseManager

from .core.royalty_calculator import RoyaltyCalculator

from .models.rights_models import (
    RightsRequest,
    RightsResult,
    OwnershipRecord,
    LicenseAgreement,
    RoyaltyPayment
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "RightsManagementManager",
    "OwnershipRegistry",
    "LicenseManager",
    "RoyaltyCalculator", 
    "RightsRequest",
    "RightsResult",
    "OwnershipRecord",
    "LicenseAgreement",
    "RoyaltyPayment"
]