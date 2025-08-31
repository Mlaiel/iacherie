"""PredictiveAnalytics Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade predictive_analytics capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""# Master Manager
from .manager import (
    PredictiveAnalyticsManager,
    PredictiveAnalyticsSystemStatus
)

# Core System
from .core.predictive_analytics_engine import (
    PredictiveAnalyticsEngine,
    PredictiveAnalyticsJob,
    PredictiveAnalyticsResult
)

# Legacy compatibility (for smooth migration)
from .manager import PredictiveAnalyticsManager as PredictiveAnalyticsAgent

__all__ = [
    # Master Manager
    'PredictiveAnalyticsManager',
    'PredictiveAnalyticsSystemStatus',
    
    # Core System
    'PredictiveAnalyticsEngine',
    'PredictiveAnalyticsJob',
    'PredictiveAnalyticsResult',
    
    # Legacy compatibility
    'PredictiveAnalyticsAgent'
]
