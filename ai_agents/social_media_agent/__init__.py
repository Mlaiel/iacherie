"""SocialMedia Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade social_media capabilities with
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
    SocialMediaManager,
    SocialMediaSystemStatus
)

# Core System
from .core.social_media_engine import (
    SocialMediaEngine,
    SocialMediaJob,
    SocialMediaResult
)

# Legacy compatibility (for smooth migration)
from .manager import SocialMediaManager as SocialMediaAgent

__all__ = [
    # Master Manager
    'SocialMediaManager',
    'SocialMediaSystemStatus',
    
    # Core System
    'SocialMediaEngine',
    'SocialMediaJob',
    'SocialMediaResult',
    
    # Legacy compatibility
    'SocialMediaAgent'
]
