"""Brand Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade brand capabilities with
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
    BrandManager,
    BrandSystemStatus
)

# Core System
from .core.brand_engine import (
    BrandEngine,
    BrandJob,
    BrandResult
)

# Legacy compatibility (for smooth migration)
from .manager import BrandManager as BrandAgent

__all__ = [
    # Master Manager
    'BrandManager',
    'BrandSystemStatus',
    
    # Core System
    'BrandEngine',
    'BrandJob',
    'BrandResult',
    
    # Legacy compatibility
    'BrandAgent'
]
