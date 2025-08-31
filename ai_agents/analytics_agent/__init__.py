"""Analytics Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade analytics capabilities with
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
    AnalyticsManager,
    AnalyticsSystemStatus
)

# Core System
from .core.analytics_engine import (
    AnalyticsEngine,
    AnalyticsJob,
    AnalyticsResult
)

# Legacy compatibility (for smooth migration)
from .manager import AnalyticsManager as AnalyticsAgent

__all__ = [
    # Master Manager
    'AnalyticsManager',
    'AnalyticsSystemStatus',
    
    # Core System
    'AnalyticsEngine',
    'AnalyticsJob',
    'AnalyticsResult',
    
    # Legacy compatibility
    'AnalyticsAgent'
]
