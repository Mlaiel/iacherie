"""Seo Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade seo capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    SeoManager,
    SeoSystemStatus
)

# Core System
from .core.seo_engine import (
    SeoEngine,
    SeoJob,
    SeoResult
)

# Legacy compatibility (for smooth migration)
from .manager import SeoManager as SeoAgent
from .manager import SeoManager as SEOAgent  # Additional alias for compatibility

__all__ = [
    # Master Manager
    'SeoManager',
    'SeoSystemStatus',
    
    # Core System
    'SeoEngine',
    'SeoJob',
    'SeoResult',
    
    # Legacy compatibility
    'SeoAgent',
    'SEOAgent'  # Additional alias
]
