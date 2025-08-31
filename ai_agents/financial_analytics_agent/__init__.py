"""Financial Analytics Agent - Financial Analytics

This module provides comprehensive financial analytics and reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import FinancialAnalyticsManager
from .core.analytics_engine import FinancialAnalyticsEngine

FinancialAnalyticsAgent = FinancialAnalyticsManager

__all__ = ['FinancialAnalyticsManager', 'FinancialAnalyticsEngine', 'FinancialAnalyticsAgent']