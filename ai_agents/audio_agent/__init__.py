"""Audio Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade audio capabilities with
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
    AudioManager,
    AudioSystemStatus
)

# Core System
from .core.audio_engine import (
    AudioEngine,
    AudioJob,
    AudioResult
)

# Legacy compatibility (for smooth migration)
from .manager import AudioManager as AudioAgent

__all__ = [
    # Master Manager
    'AudioManager',
    'AudioSystemStatus',
    
    # Core System
    'AudioEngine',
    'AudioJob',
    'AudioResult',
    
    # Legacy compatibility
    'AudioAgent'
]
