"""Revenue Optimization Agent - AI-Powered Revenue Optimization

This module provides intelligent revenue optimization with AI-driven insights
and automated optimization strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .manager import RevenueOptimizationManager
from .core.optimization_engine import RevenueOptimizationEngine

# Legacy compatibility
RevenueOptimizationAgent = RevenueOptimizationManager

__all__ = [
    'RevenueOptimizationManager',
    'RevenueOptimizationEngine',
    'RevenueOptimizationAgent'
]