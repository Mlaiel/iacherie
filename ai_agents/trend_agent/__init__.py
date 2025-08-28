"""
Trend Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade trend capabilities with
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
    TrendManager,
    TrendSystemStatus
)

# Core System
from .core.trend_engine import (
    TrendEngine,
    TrendJob,
    TrendResult
)

# Legacy compatibility (for smooth migration)
from .manager import TrendManager as TrendAgent

__all__ = [
    # Master Manager
    'TrendManager',
    'TrendSystemStatus',
    
    # Core System
    'TrendEngine',
    'TrendJob',
    'TrendResult',
    
    # Legacy compatibility
    'TrendAgent'
]
