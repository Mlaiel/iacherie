"""
Ml Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade ml capabilities with
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
    MlManager,
    MlSystemStatus
)

# Core System
from .core.ml_engine import (
    MlEngine,
    MlJob,
    MlResult
)

# Legacy compatibility (for smooth migration)
from .manager import MlManager as MlAgent

__all__ = [
    # Master Manager
    'MlManager',
    'MlSystemStatus',
    
    # Core System
    'MlEngine',
    'MlJob',
    'MlResult',
    
    # Legacy compatibility
    'MlAgent'
]
