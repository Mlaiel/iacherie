"""
Monetization Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade monetization capabilities with
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
    MonetizationManager,
    MonetizationSystemStatus
)

# Core System
from .core.monetization_engine import (
    MonetizationEngine,
    MonetizationJob,
    MonetizationResult
)

# Legacy compatibility (for smooth migration)
from .manager import MonetizationManager as MonetizationAgent

__all__ = [
    # Master Manager
    'MonetizationManager',
    'MonetizationSystemStatus',
    
    # Core System
    'MonetizationEngine',
    'MonetizationJob',
    'MonetizationResult',
    
    # Legacy compatibility
    'MonetizationAgent'
]
