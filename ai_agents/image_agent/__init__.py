"""Image Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade image capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    ImageManager,
    ImageSystemStatus
)

# Core System
from .core.image_engine import (
    ImageEngine,
    ImageJob,
    ImageResult
)

# Legacy compatibility (for smooth migration)
from .manager import ImageManager as ImageAgent

__all__ = [
    # Master Manager
    'ImageManager',
    'ImageSystemStatus',
    
    # Core System
    'ImageEngine',
    'ImageJob',
    'ImageResult',
    
    # Legacy compatibility
    'ImageAgent'
]
