"""
Licensing Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade licensing capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

# Master Manager
from .manager import (
    LicensingManager,
    LicensingSystemStatus
)

# Core System
from .core.licensing_engine import (
    LicensingEngine,
    LicensingJob,
    LicensingResult
)

# Legacy compatibility (for smooth migration)
from .manager import LicensingManager as LicensingAgent

__all__ = [
    # Master Manager
    'LicensingManager',
    'LicensingSystemStatus',
    
    # Core System
    'LicensingEngine',
    'LicensingJob',
    'LicensingResult',
    
    # Legacy compatibility
    'LicensingAgent'
]
