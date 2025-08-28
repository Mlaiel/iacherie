"""
Legal Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade legal capabilities with
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
    LegalManager,
    LegalSystemStatus
)

# Core System
from .core.legal_engine import (
    LegalEngine,
    LegalJob,
    LegalResult
)

# Legacy compatibility (for smooth migration)
from .manager import LegalManager as LegalAgent

__all__ = [
    # Master Manager
    'LegalManager',
    'LegalSystemStatus',
    
    # Core System
    'LegalEngine',
    'LegalJob',
    'LegalResult',
    
    # Legacy compatibility
    'LegalAgent'
]
