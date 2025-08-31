"""Moderation Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade moderation capabilities with
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
    ModerationManager,
    ModerationSystemStatus
)

# Core System
from .core.moderation_engine import (
    ModerationEngine,
    ModerationJob,
    ModerationResult
)

# Legacy compatibility (for smooth migration)
from .manager import ModerationManager as ModerationAgent

__all__ = [
    # Master Manager
    'ModerationManager',
    'ModerationSystemStatus',
    
    # Core System
    'ModerationEngine',
    'ModerationJob',
    'ModerationResult',
    
    # Legacy compatibility
    'ModerationAgent'
]
