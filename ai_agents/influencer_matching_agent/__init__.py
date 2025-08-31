"""Influencer Matching Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade influencer matching capabilities with
AI-powered creator analysis and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

# Master Manager
from .manager import (
    InfluencerMatchingManager,
    InfluencerMatchingSystemStatus
)

# Core System
from .core.matching_engine import (
    MatchingEngine,
    MatchingJob,
    MatchingResult
)

# Legacy compatibility (for smooth migration)
from .manager import InfluencerMatchingManager as InfluencerMatchingAgent

__all__ = [
    # Master Manager
    'InfluencerMatchingManager',
    'InfluencerMatchingSystemStatus',
    
    # Core System
    'MatchingEngine',
    'MatchingJob',
    'MatchingResult',
    
    # Legacy compatibility
    'InfluencerMatchingAgent'
]