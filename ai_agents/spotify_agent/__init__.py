"""
Spotify Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade spotify capabilities with
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
    SpotifyManager,
    SpotifySystemStatus
)

# Core System
from .core.spotify_engine import (
    SpotifyEngine,
    SpotifyJob,
    SpotifyResult
)

# Legacy compatibility (for smooth migration)
from .manager import SpotifyManager as SpotifyAgent

__all__ = [
    # Master Manager
    'SpotifyManager',
    'SpotifySystemStatus',
    
    # Core System
    'SpotifyEngine',
    'SpotifyJob',
    'SpotifyResult',
    
    # Legacy compatibility
    'SpotifyAgent'
]
