"""Timeline Management Agent - Ultra-Advanced Enterprise System

This module provides optimal timeline planning and management with scheduling and milestone tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
# Master Manager
from .manager import (
    TimelineManagementManager,
    TimelineManagementSystemStatus
)

# Core System
from .core.timeline_management_engine import (
    TimelineManagementEngine,
    TimelineManagementJob,
    TimelineManagementResult
)

# Legacy compatibility (for smooth migration)
from .manager import TimelineManagementManager as TimelineManagementAgent

__all__ = [
    # Master Manager
    'TimelineManagementManager',
    'TimelineManagementSystemStatus',
    
    # Core System
    'TimelineManagementEngine',
    'TimelineManagementJob',
    'TimelineManagementResult',
    
    # Legacy compatibility
    'TimelineManagementAgent'
]