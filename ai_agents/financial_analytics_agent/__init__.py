"""FinancialAnalytics Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade financial analytics and reporting capabilities with
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
    FinancialAnalyticsManager,
    FinancialAnalyticsSystemStatus
)

# Core System
from .core.financial_analytics_engine import (
    FinancialAnalyticsEngine,
    FinancialAnalyticsJob,
    FinancialAnalyticsResult
)

# Legacy compatibility (for smooth migration)
from .manager import FinancialAnalyticsManager as FinancialAnalyticsAgent

__all__ = [
    # Master Manager
    'FinancialAnalyticsManager',
    'FinancialAnalyticsSystemStatus',
    
    # Core System
    'FinancialAnalyticsEngine',
    'FinancialAnalyticsJob',
    'FinancialAnalyticsResult',
    
    # Legacy compatibility
    'FinancialAnalyticsAgent'
]