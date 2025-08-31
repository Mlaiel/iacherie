"""Webhook Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade webhook capabilities with
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
    WebhookManager,
    WebhookSystemStatus
)

# Core System
from .core.webhook_engine import (
    WebhookEngine,
    WebhookJob,
    WebhookResult
)

# Legacy compatibility (for smooth migration)
from .manager import WebhookManager as WebhookAgent

__all__ = [
    # Master Manager
    'WebhookManager',
    'WebhookSystemStatus',
    
    # Core System
    'WebhookEngine',
    'WebhookJob',
    'WebhookResult',
    
    # Legacy compatibility
    'WebhookAgent'
]
