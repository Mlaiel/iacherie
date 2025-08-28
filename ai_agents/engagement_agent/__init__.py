"""
Engagement Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade engagement capabilities with
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
    EngagementManager,
    EngagementSystemStatus
)

# Core System
from .core.engagement_engine import (
    EngagementEngine,
    EngagementJob,
    EngagementResult
)

# Legacy compatibility (for smooth migration)
from .manager import EngagementManager as EngagementAgent

__all__ = [
    # Master Manager
    'EngagementManager',
    'EngagementSystemStatus',
    
    # Core System
    'EngagementEngine',
    'EngagementJob',
    'EngagementResult',
    
    # Legacy compatibility
    'EngagementAgent'
]
