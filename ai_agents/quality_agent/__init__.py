"""Quality Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade quality capabilities with
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
    QualityManager,
    QualitySystemStatus
)

# Core System
from .core.quality_engine import (
    QualityEngine,
    QualityJob,
    QualityResult
)

# Legacy compatibility (for smooth migration)
from .manager import QualityManager as QualityAgent

__all__ = [
    # Master Manager
    'QualityManager',
    'QualitySystemStatus',
    
    # Core System
    'QualityEngine',
    'QualityJob',
    'QualityResult',
    
    # Legacy compatibility
    'QualityAgent'
]
