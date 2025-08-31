"""Recommendation Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade recommendation capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    RecommendationManager,
    RecommendationSystemStatus
)

# Core System
from .core.recommendation_engine import (
    RecommendationEngine,
    RecommendationJob,
    RecommendationResult
)

# Legacy compatibility (for smooth migration)
from .manager import RecommendationManager as RecommendationAgent

__all__ = [
    # Master Manager
    'RecommendationManager',
    'RecommendationSystemStatus',
    
    # Core System
    'RecommendationEngine',
    'RecommendationJob',
    'RecommendationResult',
    
    # Legacy compatibility
    'RecommendationAgent'
]
