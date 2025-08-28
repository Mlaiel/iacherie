"""
Notification Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade notification capabilities with
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
    NotificationManager,
    NotificationSystemStatus
)

# Core System
from .core.notification_engine import (
    NotificationEngine,
    NotificationJob,
    NotificationResult
)

# Legacy compatibility (for smooth migration)
from .manager import NotificationManager as NotificationAgent

__all__ = [
    # Master Manager
    'NotificationManager',
    'NotificationSystemStatus',
    
    # Core System
    'NotificationEngine',
    'NotificationJob',
    'NotificationResult',
    
    # Legacy compatibility
    'NotificationAgent'
]
