"""
Video Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade video capabilities with
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
    VideoManager,
    VideoSystemStatus
)

# Core System
from .core.video_engine import (
    VideoEngine,
    VideoJob,
    VideoResult
)

# Legacy compatibility (for smooth migration)
from .manager import VideoManager as VideoAgent

__all__ = [
    # Master Manager
    'VideoManager',
    'VideoSystemStatus',
    
    # Core System
    'VideoEngine',
    'VideoJob',
    'VideoResult',
    
    # Legacy compatibility
    'VideoAgent'
]
