"""Support Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade support capabilities with
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
    SupportManager,
    SupportSystemStatus
)

# Core System
from .core.support_engine import (
    SupportEngine,
    SupportJob,
    SupportResult
)

# Legacy compatibility (for smooth migration)
from .manager import SupportManager as SupportAgent

__all__ = [
    # Master Manager
    'SupportManager',
    'SupportSystemStatus',
    
    # Core System
    'SupportEngine',
    'SupportJob',
    'SupportResult',
    
    # Legacy compatibility
    'SupportAgent'
]
