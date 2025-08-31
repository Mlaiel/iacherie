"""Merchandise Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade merchandise and product monetization capabilities with
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
    MerchandiseManager,
    MerchandiseSystemStatus
)

# Core System
from .core.merchandise_engine import (
    MerchandiseEngine,
    MerchandiseJob,
    MerchandiseResult
)

# Legacy compatibility (for smooth migration)
from .manager import MerchandiseManager as MerchandiseAgent

__all__ = [
    # Master Manager
    'MerchandiseManager',
    'MerchandiseSystemStatus',
    
    # Core System
    'MerchandiseEngine',
    'MerchandiseJob',
    'MerchandiseResult',
    
    # Legacy compatibility
    'MerchandiseAgent'
]