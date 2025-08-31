"""Revenue Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade revenue capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    RevenueManager,
    RevenueSystemStatus
)

# Core System
from .core.revenue_engine import (
    RevenueEngine,
    RevenueJob,
    RevenueResult
)

# Legacy compatibility (for smooth migration)
from .manager import RevenueManager as RevenueAgent

__all__ = [
    # Master Manager
    'RevenueManager',
    'RevenueSystemStatus',
    
    # Core System
    'RevenueEngine',
    'RevenueJob',
    'RevenueResult',
    
    # Legacy compatibility
    'RevenueAgent'
]
