"""Content Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade content capabilities with
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
    ContentManager,
    ContentSystemStatus
)

# Core System
from .core.content_engine import (
    ContentEngine,
    ContentJob,
    ContentResult
)

# Legacy compatibility (for smooth migration)
from .manager import ContentManager as ContentAgent

__all__ = [
    # Master Manager
    'ContentManager',
    'ContentSystemStatus',
    
    # Core System
    'ContentEngine',
    'ContentJob',
    'ContentResult',
    
    # Legacy compatibility
    'ContentAgent'
]
